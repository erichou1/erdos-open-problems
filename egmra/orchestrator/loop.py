"""The main EGMRA research loop (spec §5.2, §7.9).

``research()`` implements the seventeen-step end-to-end flow: freeze the source,
build the Statement IR and interpretation lattice, run integrity probes, audit
status, run a short blind cold pass, build a frozen solver packet, score the
problem, create the epistemic graph and AND/OR blueprint, attack dynamic leaves
with a posterior controller, admit/reject claims through the evidence router,
compile a proof from admitted claims, run an independent referee, apply the five
release gates, and distill only authenticated learning.

Two-pass protocol (spec §4.3 item 4): the blind cold pass always precedes the
frozen literature packet, which precedes deep proof work. The ``phases`` list
records this order so it is auditable.
"""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from pathlib import Path
import inspect
import json
import re
import sys
import threading
from typing import Any, Callable, Protocol
from urllib.parse import urlparse

from egmra.agents import AuthorityTokenIssuer
from egmra.agents.browser_runner import BrowserRunnerError
from egmra.agents.runner import DeterministicRunner, ModelRunner
from egmra.compute.artifact import ReplayReport, validator_classification
from egmra.compute.service import ComputeService
from egmra.compute.sandbox import RestrictedPythonExecutor
from egmra.compute.spec import ExperimentSpec
from egmra.control.leases import LeaseError, LeaseManager
from egmra.corpus.status import StatusClaim, reconcile_status
from egmra.intake.contract import ProblemContract, build_problem_contract
from egmra.intake.review import interpretation_review_hash, verify_intent_certificate
from egmra.learning import LongTermMemory
from egmra.lean import LeanService, verify_formal_correspondence_certificate
from egmra.lean.warm import dev_obligation_source
from egmra.oeis import OEISClient, OEISUnavailable
from egmra.orchestrator.checkpoint import CheckpointError, take_checkpoint
from egmra.policy import PolicyEnforcer
from egmra.provenance.hashing import canonical_json, content_id, is_sha256, sha256_hex
from egmra.release.certificate import ReleaseCertificate
from egmra.release.compiler import CompiledProof, assemble_from_admitted_graph
from egmra.release.expert_review import ExpertReviewCertificate, expert_reviewed_for_run
from egmra.release.gates import FiveGateResult, run_five_gates
from egmra.release.policy import PromotionDecision, PromotionPolicy
from egmra.retrieval.packet import LiteratureQuery, SourcePacket
from egmra.retrieval.records import TheoremRecord
from egmra.retrieval.service import RetrievalService
from egmra.search.blueprint import AndOrBlueprint, Node
from egmra.search.controller import ActionComponents, BranchPosterior, Controller
from egmra.search.mechanism import MechanismFingerprint, QualityDiversityArchive
from egmra.search.programs import ResearchProgram, instantiate_programs
from egmra.search.verified_debt import (
    DebtPolicy,
    Obligation,
    delta_verified_debt,
    verified_debt,
)
from egmra.selection.features import ProblemFeatures
from egmra.selection.posterior import CompetingRiskPosterior
from egmra.selection.acquisition import ProblemSelector
from egmra.truth.entities import (
    Branch,
    Evidence,
    EvidenceKind,
    FormalCorrespondenceCertificate,
    IntentCertificate,
    Problem,
    Verdict,
)
from egmra.truth.blackboard import Blackboard, BlackboardError, ReadSlice
from egmra.truth.events import EventLog
from egmra.truth.graph import EpistemicGraph
from egmra.truth.router import EvidenceRouter
from egmra.truth.validators import attest_evidence
from egmra.verification.attacks import AttackResult, REQUIRED_ATTACKS
from egmra.verification.informal_review import (
    build_informal_review_evidence,
    run_hostile_reviews,
)
from egmra.verification.referee import AdversarialReferee, DiversityProfile, RefereeResult


# Branch leases are heartbeated while a (possibly slow) worker reasons, so that
# legitimately long browser/model generation is never rejected as a stale lease.
_BRANCH_LEASE_GRACE_SECONDS = 60.0
_MAX_LITERATURE_IMPORTS = 8
_RESEARCH_LOOP_CLOSURE = "egmra-research-loop-v1"
_BRANCH_LEASE_HEARTBEAT_SECONDS = 20.0


@contextmanager
def _lease_heartbeat(leases, lease, *, interval: float = _BRANCH_LEASE_HEARTBEAT_SECONDS):
    """Keep a branch lease alive while its worker runs.

    Modern browser reasoning routinely exceeds the lease grace window, and the
    fence is only checked *after* the worker returns; without a heartbeat, valid
    work is discarded as ``stale_worker_rejected: lease has expired``. A daemon
    thread renews the lease every ``interval`` seconds (strictly less than the
    grace window) so long-but-live reasoning is preserved. If the lease is
    legitimately superseded (a replacement worker bumped the fencing token), the
    renewal fails closed and the subsequent fence check still rejects this
    worker's entire output batch — liveness is extended, safety is not weakened.
    """
    stop = threading.Event()

    def _beat() -> None:
        while not stop.wait(interval):
            try:
                leases.renew(lease.branch_id, lease.holder,
                             fencing_token=lease.fencing_token)
            except LeaseError:
                return  # superseded/expired; assert_current will reject the batch

    thread = threading.Thread(
        target=_beat, name=f"lease-heartbeat:{lease.branch_id}", daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(timeout=interval)

ACTOR = {"type": "agent", "id": "governor", "model": "local", "version": "1"}


def _default_independent_replay_executor():
    """Use a measured second Python toolchain when one exists locally."""
    current = Path(sys.executable).resolve()
    for candidate in (Path("/usr/bin/python3"), Path("/opt/homebrew/bin/python3")):
        try:
            if candidate.exists() and candidate.resolve() != current:
                return RestrictedPythonExecutor(python_executable=candidate)
        except (OSError, ValueError):
            continue
    return None


@dataclass
class WorkerOutput:
    claim_proposals: list[dict] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    falsifiers: list[str] = field(default_factory=list)
    search_queries: list[str] = field(default_factory=list)
    replay_reports: list[ReplayReport] = field(default_factory=list)
    generated_sequences: list[list[int]] = field(default_factory=list)
    formal_candidates: list[dict] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    bottleneck: str = ""
    proof_steps: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    formalization_requests: list[str] = field(default_factory=list)
    literature_imports: list[dict] = field(default_factory=list)
    # Unclosed subgoals the branch left behind — fed forward so LATER branches
    # attack the specific remaining gaps instead of restarting from the goal
    # (report R3 phase 1: the gap generates the next work).
    open_subgoals: list[str] = field(default_factory=list)


class Worker(Protocol):
    def cold_pass(self, contract: ProblemContract, *, budget: float) -> WorkerOutput: ...
    def work_branch(
        self, contract: ProblemContract, packet: SourcePacket, *, branch_id: str, budget: float,
        fencing_token: int, branch_slice: ReadSlice | None = None,
    ) -> WorkerOutput: ...


class AttackEvaluator(Protocol):
    """Independent verifier boundary consumed by the orchestrator."""

    def evaluate(self, **context) -> list[AttackResult]: ...


@dataclass(frozen=True)
class MechanicalAttackEvaluator:
    """Run only attacks that the local M1 slice can substantiate mechanically.

    Missing executable/formal evidence produces a failed obligation.  This is
    intentionally pessimistic: an unavailable attack is never synthesized as a
    successful referee verdict.

    Discharge routes for the two computation-flavoured attacks
    (``independent_computation`` and ``proof_reconstruction``):

    * finite route — every recorded finite-computation replay matched in an
      independent environment; and
    * formal route — only for a formal run (``informal_only=False``) with **no**
      finite experiments: an admitted, kernel-replayed Lean/ATP proof bound to
      an approved formal-correspondence certificate and an attested verifier.
      The pinned kernel replay *is* the independent mechanical computation for
      a purely formal result; requiring a side finite experiment for such runs
      made the attacks unsatisfiable for honest general theorems.

    Fail-closed properties preserved: an informal-only run has no formal route;
    a run whose finite replays exist but do not all match never falls back to
    the formal route; a formal run without admitted kernel evidence fails both
    attacks exactly as before.
    """

    def evaluate(self, **context) -> list[AttackResult]:
        contract: ProblemContract = context["contract"]
        graph: EpistemicGraph = context["graph"]
        compiled: CompiledProof | None = context["compiled"]
        packet: SourcePacket = context["packet"]
        replay_reports: list[ReplayReport] = context["replay_reports"]
        novelty_verdict: str = context["novelty_verdict"]
        informal_only: bool = context["informal_only"]
        intent_cert: IntentCertificate | None = context["intent_cert"]

        finite_replays_present = bool(replay_reports)
        replay_ok = finite_replays_present and all(
            report.replayed and report.output_hash_matches and report.independent_environment
            for report in replay_reports
        )
        executable_countermodel = next(
            (probe for probe in contract.probes if probe.name == "counterexample_search"),
            None,
        )
        source_used = any(
            evidence.kind == EvidenceKind.SOURCE_IMPORT for evidence in graph.evidence.values()
        )
        source_provenance_ok = (not source_used) or all(
            record.source_uri and record.source_version and record.source_content_hash
            and record.verbatim_theorem_and_hypothesis_extract
            for record in packet.theorem_records
        )
        # A formal result is audited against an actual kernel/formal artifact: a
        # valid Lean/ATP proof evidence bound to a formal-correspondence certificate
        # (only admitted after independent correspondence review). ``informal_only``
        # runs carry no formal obligation, so the audit passes vacuously there.
        formal_artifact_ok = any(
            evidence.valid
            and evidence.kind in {EvidenceKind.LEAN_PROOF, EvidenceKind.ATP_PROOF}
            and bool(evidence.formal_correspondence_certificate_id)
            for evidence in graph.evidence.values()
        )
        # The formal discharge route additionally requires a passed kernel replay
        # and at least one attested verifier identity on the admitted evidence.
        formal_kernel_replay_ok = any(
            evidence.valid
            and evidence.kind in {EvidenceKind.LEAN_PROOF, EvidenceKind.ATP_PROOF}
            and bool(evidence.formal_correspondence_certificate_id)
            and evidence.replay_result == "pass"
            and any(
                bool(identity.get("attested"))
                for identity in evidence.verifier_identities
                if isinstance(identity, dict)
            )
            for evidence in graph.evidence.values()
        )
        formal_discharge = (
            not informal_only
            and formal_kernel_replay_ok
            and not finite_replays_present
        )
        # A hostile informal review with an independent reconstruction artifact
        # IS the §11.2 proof-reconstruction attack executed (a referee wrote a
        # skeleton without copying the argument); it discharges that one attack
        # only — never the computation replay obligation.
        hostile_reconstruction_ok = any(
            evidence.valid
            and evidence.kind == EvidenceKind.INFORMAL_REVIEW
            and bool(evidence.artifact_hashes)
            for evidence in graph.evidence.values()
        )
        # ``independent_computation`` is vacuously satisfied only when NOTHING
        # computational exists to replay: no finite replays ran and no
        # numerical/exact/SAT evidence was admitted.  A bad replay still fails;
        # used computations still require matching independent replays.
        computational_evidence_present = finite_replays_present or any(
            evidence.kind in {
                EvidenceKind.NUMERICAL, EvidenceKind.EXACT_COMPUTATION,
                EvidenceKind.SAT_CERTIFICATE,
            }
            for evidence in graph.evidence.values()
        )
        checks = {
            "target_diff": (
                bool(intent_cert) and not contract.release_blocked,
                "target intent is unresolved or an intake probe blocks correspondence",
            ),
            "quantifier_domain_audit": (
                all(b.domain != "unspecified" for b in contract.primary_ir.binders),
                "at least one quantified binder has no preserved domain",
            ),
            "dependency_trace": (
                bool(compiled and compiled.complete),
                "admitted dependency trace does not close the goal",
            ),
            "circularity": (
                bool(compiled),
                "no successfully cycle-checked compiled dependency cone",
            ),
            "import_challenge": (
                source_provenance_ok,
                "a used import lacks complete source provenance",
            ),
            "countermodel_search": (
                bool(executable_countermodel
                     and executable_countermodel.artifacts.get("executable")
                     and executable_countermodel.passed),
                "no passing executable countermodel search for the selected interpretation",
            ),
            "independent_computation": (
                replay_ok or formal_discharge or not computational_evidence_present,
                "a computational result was used without a matching independent "
                "replay and no kernel-replayed formal proof can discharge it",
            ),
            "formal_audit": (
                informal_only or formal_artifact_ok,
                "formal result has no local kernel/formal audit artifact",
            ),
            "proof_reconstruction": (
                bool(compiled and compiled.complete
                     and (replay_ok or formal_discharge or hostile_reconstruction_ok)),
                "candidate could not be independently reconstructed (no matching "
                "replay, kernel proof, or hostile-review reconstruction)",
            ),
            "novelty_significance_firewall": (
                novelty_verdict in {"N0", "N1", "known"},
                "novelty level requires an independent expert audit not present locally",
            ),
        }
        return [
            AttackResult(attack, passed=checks[attack][0],
                         defect="" if checks[attack][0] else checks[attack][1])
            for attack in REQUIRED_ATTACKS
        ]


@dataclass
class BudgetLedger:
    """Auditable hard budget for one research run.

    Amounts are committed before a stage is invoked.  A stage can receive no more
    than its recorded allocation, and an allocation that would exceed the global
    budget fails rather than silently borrowing from a later stage.
    """

    total: float
    spent: float = 0.0
    allocations: list[dict] = field(default_factory=list)

    @property
    def remaining(self) -> float:
        return max(0.0, self.total - self.spent)

    def allocate(self, stage: str, amount: float, *, branch_id: str = "") -> bool:
        if amount < 0:
            raise ValueError("budget allocation cannot be negative")
        if amount > self.remaining + 1e-12:
            return False
        self.spent += amount
        self.allocations.append(
            {"stage": stage, "branch_id": branch_id, "amount": amount,
             "spent_after": self.spent, "remaining_after": self.remaining}
        )
        return True


def _execute_finite_experiment(
    compute_service: "ComputeService", replay_sandbox: object | None,
    spec: ExperimentSpec, code: str, claim_id: str,
) -> tuple[list[dict], list[ReplayReport], list[str]]:
    """Run one finite experiment in the sandbox and shape trusted evidence.

    Shared by the fixture worker and the model-backed worker (task 4.5). Emits
    ``exact_computation`` evidence only when the sandboxed predicate returns
    literal True, an independent replay matches, and the claim is bound to the
    spec — so a model-proposed experiment can reach at most COMPUTATIONAL_EVIDENCE
    (a finite result), never a general proof. The RestrictedPython/container
    sandbox contains untrusted, model-authored code.
    """
    evidence: list[dict] = []
    replays: list[ReplayReport] = []
    failures: list[str] = []
    job = compute_service.submit_experiment(
        spec, code, claimed_classification="exhaustive_finite_subcase")
    if compute_service.poll(job) != "done":
        # ``artifact`` is deliberately the public fail-closed boundary for a
        # failed job and includes the executor's bounded diagnostic.  Preserve
        # that detail in the run result: otherwise a generated syntax error,
        # timeout, policy rejection, and infrastructure failure are all
        # indistinguishable and cannot be repaired or audited.
        try:
            compute_service.artifact(job)
        except RuntimeError as exc:
            failures.append(f"computation job {job} failed: {exc}")
        else:  # defensive: a non-done job must never expose an artifact
            failures.append(f"computation job {job} failed without diagnostic")
        return evidence, replays, failures
    artifact = compute_service.artifact(job)
    replay = compute_service.replay(artifact.artifact_id, sandbox=replay_sandbox)
    replays.append(replay)
    output_result = artifact.output.get("result") if isinstance(artifact.output, Mapping) else None
    claim_bound = claim_id in spec.claim_ids
    if output_result is True and replay.replayed and replay.output_hash_matches \
            and replay.independent_environment and claim_bound:
        classification = validator_classification(artifact.effective_classification())
        evidence.append({
            "evidence_id": f"ev_{claim_id}",
            "claim_ids": [claim_id],
            "kind": "exact_computation",
            "artifact_id": artifact.artifact_id,
            "artifact_hash": artifact.content_id(),
            "replay_result": "pass",
            "findings": {
                "classification": classification,
                "exact_arithmetic": spec.arithmetic_mode == "exact",
                "coverage_statement": bool(artifact.coverage),
                "result_verified": True,
            },
            "environment_hash": artifact.environment_hash,
        })
    elif output_result is False:
        failures.append("experiment predicate returned false")
    elif not claim_bound:
        failures.append("experiment lacks locked claim binding")
    elif replay.replayed and replay.output_hash_matches and not replay.independent_environment:
        failures.append("independent replay environment unavailable")
    else:
        failures.append("experiment result missing or replay failed")
    return evidence, replays, failures


@dataclass
class DeterministicWorker:
    """A credential-free worker that produces genuine evidence for a fixture.

    When given an executable ``experiment_code`` + ``experiment_spec``, it runs the
    sandboxed compute service and emits real ``exact_computation`` evidence, so the
    end-to-end slice exercises compute -> artifact -> replay -> router -> SUPPORTED.
    """

    goal_claim_id: str
    goal_formula: str
    goal_scope: str = "general"
    experiment_code: str = ""
    experiment_spec: ExperimentSpec | None = None
    compute_service: ComputeService = field(default_factory=ComputeService)
    replay_sandbox: object | None = field(default_factory=_default_independent_replay_executor)

    def cold_pass(self, contract: ProblemContract, *, budget: float) -> WorkerOutput:
        # A blind scratch pass: hypotheses only, never a publication claim.
        return WorkerOutput(falsifiers=["check smallest cases first"],
                            search_queries=["smallest cases boundary counterexample"],
                            bottleneck="no literature yet (blind pass)")

    def work_branch(
        self, contract: ProblemContract, packet: SourcePacket, *, branch_id: str, budget: float,
        fencing_token: int, branch_slice: ReadSlice | None = None,
    ) -> WorkerOutput:
        proposals = [{
            "claim_id": self.goal_claim_id,
            "canonical_formula": self.goal_formula,
            "informal_text": self.goal_formula,
            "scope": self.goal_scope,
            "dependencies": [],
        }]
        evidence: list[dict] = []
        replay_reports: list[ReplayReport] = []
        failures: list[str] = []
        if self.experiment_code and self.experiment_spec is not None:
            evidence, replay_reports, failures = _execute_finite_experiment(
                self.compute_service, self.replay_sandbox, self.experiment_spec,
                self.experiment_code, self.goal_claim_id)
        return WorkerOutput(
            claim_proposals=proposals, evidence=evidence, replay_reports=replay_reports,
            failures=failures, bottleneck="close the goal claim",
        )


@dataclass
class ResearchResult:
    problem_id: str
    contract: ProblemContract
    graph: EpistemicGraph
    phases: list[str]
    compiled_proof: CompiledProof | None
    gates: FiveGateResult | None
    certificate: ReleaseCertificate | None
    promotion: PromotionDecision | None
    outcome: str
    acquired: bool
    budget: BudgetLedger
    cold_output: WorkerOutput = field(default_factory=WorkerOutput)
    packet: SourcePacket | None = None
    programs: tuple[ResearchProgram, ...] = ()
    blueprint: AndOrBlueprint | None = None
    replay_reports: tuple[ReplayReport, ...] = ()
    runner_responses: tuple[dict, ...] = ()
    failures: tuple[str, ...] = ()
    referee_result: RefereeResult | None = None
    oeis_results: tuple[dict, ...] = ()
    formal_reports: tuple[dict, ...] = ()
    memory: LongTermMemory | None = None
    verified_debt: dict = field(default_factory=dict)

    def render(self) -> dict:
        return {
            "problem_id": self.problem_id,
            "phases": list(self.phases),
            "outcome": self.outcome,
            "acquired": self.acquired,
            "budget": {
                "total": self.budget.total,
                "spent": self.budget.spent,
                "remaining": self.budget.remaining,
            },
            "gate_profile": self.gates.profile() if self.gates else None,
            # Candidate assembly and even a promoted scoped T2 result are not a
            # proof of the original theorem.  The public boolean is reserved for
            # a rigorous informal result (T3) or a hardened formal result whose
            # intended-statement correspondence is approved (T5/F2).
            "proof_complete": bool(
                self.certificate
                and self.compiled_proof
                and self.compiled_proof.complete
                and self.gates
                and (
                    (self.gates.truth == "T3"
                     and self.gates.formal_correspondence == "N/A")
                    or (self.gates.truth == "T5"
                        and self.gates.formal_correspondence == "F2")
                )
            ),
            "candidate_assembly_complete": bool(
                self.compiled_proof and self.compiled_proof.complete
            ),
            "event_count": len(self.graph.log),
            "release": (
                self.certificate.render(event_log=self.graph.log)
                if self.certificate else None
            ),
            "failures": list(self.failures),
            "oeis_queries": len(self.oeis_results),
            "formal_checks": len(self.formal_reports),
            "memory_records": (
                sum(len(store.records) for store in self.memory.stores().values())
                if self.memory else 0
            ),
            "verified_debt": dict(self.verified_debt),
        }


# Distinct worker roles per mechanism branch (task 4.11): the prover attacks the
# target directly, the experimentalist drives finite computation, the formalizer
# works library/lemma-first, and the skeptic assumes the stated form is wrong
# and hunts the obstruction (refutation-first — the ErdosBench audit found
# decisive progress is often a refutation of the proposed form, not a proof).
WORKER_ROLE_BY_FAMILY = {
    "direct_structural": "prover",
    "computational_finite_reduction": "experimentalist",
    "formal_library_first": "formalizer",
    "counterexample_model_construction": "skeptic",
    "contradiction_minimal_counterexample": "skeptic",
}


def _branch_role(family: str, worker: "Worker") -> str:
    return WORKER_ROLE_BY_FAMILY.get(family, getattr(worker, "role", "prover"))


def _record_model_exchanges(log, artifact_store, problem_id: str, *, runners) -> int:
    """Persist browser/model exchange provenance durably + sign an event (task 4.10).

    Each exchange's provenance record (never the raw response text) is written to
    the content-addressed object store, and a signed ``MODEL_EXCHANGE_RECORDED``
    event references the artifact hash — so the informal reasoning that produced
    claims is tamper-evident and auditable. Idempotent across shared runners.
    """
    seen_runners: set[int] = set()
    # Idempotent across repeated calls, not merely within this invocation.
    # This lets the research loop seal exchanges after EACH completed branch
    # (so a later crash cannot lose the ChatGPT links) and call once more at
    # run end without duplicating events.
    seen_exchanges: set[tuple] = set()
    for event in list(getattr(log, "events", ()) or ()):
        if getattr(event, "action", "") != "MODEL_EXCHANGE_RECORDED":
            continue
        payload = getattr(event, "payload", {}) or {}
        seen_exchanges.add((
            payload.get("stage", ""), payload.get("prompt_hash", ""),
            payload.get("response_hash", ""),
        ))
    recorded = 0
    for runner in runners:
        if runner is None or id(runner) in seen_runners:
            continue
        seen_runners.add(id(runner))
        for transcript in list(getattr(runner, "records", []) or []):
            record = transcript.to_dict() if hasattr(transcript, "to_dict") else dict(transcript)
            key = (record.get("stage", ""), record.get("prompt_hash", ""),
                   record.get("response_hash", ""))
            if key in seen_exchanges:
                continue
            seen_exchanges.add(key)
            artifact_hash = artifact_store.put(canonical_json(record).encode("utf-8"))
            log.append(
                action="MODEL_EXCHANGE_RECORDED", actor=ACTOR, object_ids=[problem_id],
                output_hashes=[artifact_hash], reason_code="model_exchange",
                human_readable_reason=f"model exchange at stage {record.get('stage', '')}",
                payload={key: record.get(key) for key in (
                    "stage", "prompt_hash", "response_hash", "conversation_url",
                    "model_label", "account_class", "attested", "created_at")},
            )
            recorded += 1
    return recorded


def _source_identity(uri: str) -> str:
    """Canonical mathematical-source identity for corroboration (report R9).

    arXiv id and DOI dominate the host: two mirrors of one paper are ONE
    source. Falls back to the host only when no canonical identity exists.
    """
    text = uri.strip().lower()
    arxiv = re.search(r"arxiv\.org/(?:abs|pdf)/([a-z0-9.\-/]+?)(?:\.pdf)?(?:v\d+)?$", text)
    if arxiv:
        return f"arxiv:{arxiv.group(1)}"
    doi = re.search(r"doi\.org/(\S+)", text)
    if doi:
        return f"doi:{doi.group(1)}"
    return f"host:{urlparse(uri).netloc or uri}"


def _admit_literature_imports(
    imports: list[dict], *, packet: SourcePacket, graph: EpistemicGraph,
    router: EvidenceRouter, branch_id: str, failures: list[str],
) -> int:
    """Admit model-cited frozen-packet records as ``source_import`` evidence.

    The model only SELECTS records; every provenance field (verbatim extract,
    source URI/version, content hash) comes from the frozen retrieval packet.
    A citation is rejected unless the record exists in the packet, the claim
    exists in the graph, and the claim's formula genuinely overlaps the record
    text (a mechanical non-sequitur gate, not a truth assertion).  One passing
    record yields ``AUDITED_SOURCE`` \u2014 provenance only, never support; \u22652
    passing records from distinct mathematical source identities (arXiv id /
    DOI, host only as fallback) yield
    ``INDEPENDENTLY_CORROBORATED`` for that claim.  Fail-closed and capped.
    """
    records = {
        record.theorem_id: record
        for record in getattr(packet, "theorem_records", ())
    }
    cited: dict[str, list[Any]] = {}
    seen: set[tuple[str, str]] = set()
    for item in imports[:_MAX_LITERATURE_IMPORTS]:
        if not isinstance(item, dict):
            failures.append(f"literature_import_malformed:{branch_id}")
            continue
        claim_id = str(item.get("claim_id") or "").strip()
        theorem_id = str(item.get("theorem_id") or "").strip()
        if not claim_id or not theorem_id or (claim_id, theorem_id) in seen:
            continue
        seen.add((claim_id, theorem_id))
        record = records.get(theorem_id)
        if record is None:
            failures.append(
                f"literature_import_unknown_record:{branch_id}:{theorem_id}")
            continue
        claim = graph.claims.get(claim_id)
        if claim is None:
            failures.append(
                f"literature_import_unknown_claim:{branch_id}:{claim_id}")
            continue
        if not _import_applicable(claim.canonical_formula, record):
            failures.append(
                f"literature_import_inapplicable:{branch_id}:{claim_id}:{theorem_id}")
            continue
        cited.setdefault(claim_id, []).append(record)
    admitted = 0
    for claim_id, claim_records in cited.items():
        # Corroboration must identify independent mathematical SOURCES, not web
        # hosts (report R9): two mirrors of the same arXiv paper are one
        # source. Canonical paper identity (arXiv id / DOI) dominates; the
        # host is only the fallback when no canonical identity exists.
        identities = {
            _source_identity(str(record.source_uri or ""))
            for record in claim_records
        }
        corroborated = len(claim_records) >= 2 and len(identities) >= 2
        claim = graph.claims[claim_id]
        for record in claim_records:
            evidence = Evidence(
                evidence_id="import_" + content_id({
                    "claim": claim.canonical_hash, "theorem": record.theorem_id,
                    "content": record.source_content_hash,
                })[:20],
                claim_ids=[claim_id],
                kind=EvidenceKind.SOURCE_IMPORT,
                assertion_scope=claim.scope,
                claim_bindings={claim_id: claim.canonical_hash},
                artifact_hashes=[sha256_hex(
                    record.verbatim_theorem_and_hypothesis_extract or "")],
                generator_identity={
                    "id": "frozen-packet-literature-import-v1",
                    "findings": {
                        "theorem_id": record.theorem_id,
                        "verbatim_extract":
                            record.verbatim_theorem_and_hypothesis_extract,
                        "source_uri": record.source_uri,
                        "source_version": record.source_version,
                        "source_content_hash": record.source_content_hash,
                        "applicability_check_passed": True,
                        "independently_corroborated": corroborated,
                        "distinct_source_identities": sorted(identities),
                    },
                },
                verifier_identities=[{
                    "id": "mechanical-applicability-check-v1", "attested": False,
                }],
                environment_hash="",
                replay_command="",
                replay_result="not_applicable",
                trust_assumptions=[
                    "imported statement trusted to its published source; "
                    "applicability gate is a mechanical token-overlap check, "
                    "not a proof of applicability",
                ],
            )
            if evidence.evidence_id in graph.evidence:
                continue
            router.admit(attest_evidence(evidence), actor=ACTOR)
            admitted += 1
    return admitted


def _import_applicable(claim_formula: str, record: Any) -> bool:
    """Mechanical non-sequitur gate: the claim must share substantial content
    words with the record's statement/conclusion/extract."""
    def tokens(text: str) -> set[str]:
        return {
            token for token in re.findall(r"[a-z0-9]+", str(text).lower())
            if len(token) >= 3
        }

    claim_tokens = tokens(claim_formula)
    if not claim_tokens:
        return False
    record_tokens = tokens(" ".join((
        str(getattr(record, "canonical_statement", "") or ""),
        str(getattr(record, "conclusion", "") or ""),
        str(getattr(record, "verbatim_theorem_and_hypothesis_extract", "") or ""),
    )))
    if not record_tokens:
        return False
    overlap = len(claim_tokens & record_tokens) / len(claim_tokens)
    return overlap >= 0.5


def _seed_controller_from_memory(controller: Controller, memory: LongTermMemory,
                                 programs: list[ResearchProgram]) -> None:
    """Replay bounded cross-problem branch-family outcomes as posterior updates."""
    families = {program.family for program in programs}
    replayed = 0
    for record in reversed(memory.procedural.records):
        if replayed >= 24:
            break
        if not isinstance(record, dict) \
                or record.get("kind") != "branch_family_outcome":
            continue
        family = record.get("branch_family")
        if family not in families:
            continue
        try:
            controller.update_posterior(
                family, success=bool(record.get("supported")),
                debt_reduction=0.0,
            )
        except (KeyError, ValueError):
            continue
        replayed += 1


def _derive_problem_traps(contract) -> list[str]:
    """Mechanical, problem-specific adversarial checklist for worker prompts.

    The CDC prompt hand-encoded the traps of its problem (parallel edges,
    bridges introduced by reductions, ...). We derive the analogue from what
    intake already computed: the interpretation lattice's ambiguity nodes and
    every failed integrity probe. Read-only prompt guidance — it never changes
    what the referee attacks or what the gates require.
    """
    traps: list[str] = []
    seen: set[str] = set()
    ambiguities = list(getattr(getattr(contract, "reconciliation", None),
                               "ambiguity_nodes", ()) or ())
    for node in ambiguities[:8]:
        text = str(node).strip()
        if text and text not in seen:
            seen.add(text)
            traps.append(f"ambiguous reading — check your claims under BOTH "
                         f"resolutions of: {text[:160]}")
    for probe in list(getattr(contract, "probes", ()) or ()):
        if getattr(probe, "passed", True):
            continue
        name = str(getattr(probe, "name", "")).strip()
        detail = str(getattr(probe, "detail", "") or
                     getattr(probe, "reason", "")).strip()
        text = f"integrity probe '{name}' failed" + (f": {detail[:140]}" if detail else "")
        if name and text not in seen:
            seen.add(text)
            traps.append(text + " — verify boundary/small/degenerate cases "
                         "explicitly before relying on them")
    return traps[:12]


def _family_history_lines(memory: LongTermMemory, problem_id: str) -> list[str]:
    """Render this problem's prior branch-family outcomes for the worker prompt.

    The controller already replays these records as posterior updates (search
    allocation); this surfaces the SAME registry to the model — the CDC-prompt
    rule that a blocked route is only reopened with a materially new mechanism
    needs the model to know which routes are blocked. Guidance only.
    """
    outcomes: dict[str, list[bool]] = {}
    for record in memory.procedural.records:
        if not isinstance(record, dict) \
                or record.get("kind") != "branch_family_outcome" \
                or record.get("problem_id") != problem_id:
            continue
        family = str(record.get("branch_family", "")).strip()
        if family:
            outcomes.setdefault(family, []).append(bool(record.get("supported")))
    lines = []
    for family, results in sorted(outcomes.items()):
        attempts = len(results)
        if any(results):
            lines.append(f"{family}: produced supported claims "
                         f"({attempts} attempt{'s' if attempts != 1 else ''})")
        else:
            lines.append(f"{family}: BLOCKED — {attempts} "
                         f"attempt{'s' if attempts != 1 else ''}, no supported "
                         "claims; reopen only with a materially new mechanism")
    return lines[:12]


def _supports_repair(formalizer: Any) -> bool:
    """True when the formalizer's ``formalize`` accepts repair feedback.

    Third-party :class:`Formalizer` implementations predating the repair
    protocol simply never repair — fail-closed, not an error.
    """
    try:
        parameters = inspect.signature(formalizer.formalize).parameters
    except (TypeError, ValueError):
        return False
    return "kernel_feedback" in parameters


def _write_branch_checkpoint(
    checkpoint_dir: Path | str, *, problem_id: str, branch_id: str,
    log: EventLog, contract: ProblemContract, interp: Any,
    graph: EpistemicGraph, budget_ledger: "BudgetLedger", failures: list[str],
    attempted: set[str] | None = None,
) -> Path | None:
    """Seal and persist one signed within-problem checkpoint (ops aid).

    The checkpoint commits to the exact event-log prefix (merkle root), the
    graph view hash, the attempted-branch set, and the remaining budget;
    ``resume()`` can later verify it against a stored event log.  Any failure
    here is recorded as an operational failure string — never a mathematical
    verdict.
    """
    try:
        checkpoint = take_checkpoint(
            log=log,
            problem_contract_hash=contract.source_bytes_hash,
            interpretation_hashes=(interpretation_review_hash(interp),),
            graph_view_hash=graph.view_hash(),
            controller_posteriors={
                "attempted_branches": sorted(attempted or ()),
            },
            budgets={"remaining": float(budget_ledger.remaining),
                     "total": float(budget_ledger.total)},
            seeds={},
            active_leases=(),
            behavior_closure_fingerprint=sha256_hex(_RESEARCH_LOOP_CLOSURE),
        )
        directory = Path(checkpoint_dir) / problem_id
        directory.mkdir(parents=True, exist_ok=True)
        record = {
            **checkpoint._content_record(),
            "sealed_hash": checkpoint.checkpoint_hash(),
            "signature": checkpoint._signature,
            "branch_id": branch_id,
        }
        path = directory / f"checkpoint_{checkpoint.last_sequence:06d}.json"
        tmp_path = path.with_suffix(".tmp")
        tmp_path.write_text(canonical_json(record), encoding="utf-8")
        tmp_path.replace(path)
        return path
    except (CheckpointError, OSError, TypeError, ValueError) as exc:
        failures.append(
            f"checkpoint_write_failed:{branch_id}:{type(exc).__name__}")
        return None


def _load_resume_checkpoint(
    resume_from: Path | str, *, problem_id: str, contract: ProblemContract,
    log: EventLog, failures: list[str],
) -> tuple[list[str], float, bool] | None:
    """Load and verify the latest checkpoint; fail closed to a fresh start.

    Returns ``(attempted_branches, prior_spend, chain_verified)``.  The
    signature and the problem-contract binding are always required.  The full
    event-chain prefix additionally verifies when the current run continues
    the SAME event log (same run id); a fresh log yields an honest warm start
    (branch skip + budget carry) without claiming chain continuity.
    """
    from egmra.orchestrator.checkpoint import Checkpoint, resume as verify_resume

    directory = Path(resume_from) / problem_id
    try:
        candidates = sorted(directory.glob("checkpoint_*.json"))
    except OSError:
        candidates = []
    if not candidates:
        return None
    path = candidates[-1]
    try:
        if path.is_symlink():
            raise ValueError("checkpoint file is a symlink")
        record = json.loads(path.read_text(encoding="utf-8"))
        checkpoint = Checkpoint(
            run_id=record["run_id"], last_sequence=record["last_sequence"],
            last_event_id=record["last_event_id"],
            merkle_root=record["merkle_root"],
            problem_contract_hash=record["problem_contract_hash"],
            interpretation_hashes=tuple(record["interpretation_hashes"]),
            graph_view_hash=record["graph_view_hash"],
            controller_posteriors=record["controller_posteriors"],
            budgets=record["budgets"], seeds=record["seeds"],
            active_leases=tuple(record["active_leases"]),
            behavior_closure_fingerprint=record["behavior_closure_fingerprint"],
            stage_caches=record["stage_caches"],
            rate_limit_state=record["rate_limit_state"],
            in_flight_calls=tuple(record["in_flight_calls"]),
            _sealed_hash=record["sealed_hash"], _signature=record["signature"],
        )
    except (OSError, KeyError, TypeError, ValueError, CheckpointError) as exc:
        failures.append(f"resume_rejected:malformed:{type(exc).__name__}")
        return None
    if not checkpoint.verify_checkpoint_hash():
        failures.append("resume_rejected:signature")
        return None
    if checkpoint.problem_contract_hash != contract.source_bytes_hash:
        failures.append("resume_rejected:contract_mismatch")
        return None
    chain_verified = False
    if checkpoint.run_id == log.run_id:
        try:
            chain_verified = verify_resume(
                checkpoint, log=log,
                current_closure_fingerprint=sha256_hex(_RESEARCH_LOOP_CLOSURE),
            ).ok
        except (CheckpointError, TypeError, ValueError):
            chain_verified = False
    branches = [
        str(branch) for branch in
        checkpoint.controller_posteriors.get("attempted_branches", ())
    ]
    budgets = checkpoint.budgets
    prior_spend = max(
        0.0, float(budgets.get("total", 0.0)) - float(budgets.get("remaining", 0.0)))
    return branches, prior_spend, chain_verified


def _proposed_dependency_cone(graph: EpistemicGraph, goal_claim_id: str) -> list[str]:
    """The goal's transitive dependency cone in dependency order (deps first).

    Includes *proposed* claims regardless of truth status — this is the ledger
    a hostile reviewer must attack, not the already-admitted subset.  Cycles
    and unknown dependencies are skipped defensively (admission already rejects
    them), never followed.
    """
    ordered: list[str] = []
    visiting: set[str] = set()
    done: set[str] = set()

    def visit(cid: str) -> None:
        if cid in done or cid in visiting:
            return
        claim = graph.claims.get(cid)
        if claim is None:
            return
        visiting.add(cid)
        for dep in claim.dependencies:
            visit(dep)
        visiting.discard(cid)
        done.add(cid)
        ordered.append(cid)

    visit(goal_claim_id)
    return ordered


def research(
    *,
    problem_id: str,
    source_bytes: bytes,
    source_id: str,
    budget: float,
    enforcer: PolicyEnforcer,
    worker: Worker,
    goal_claim_id: str,
    events_path: Path | str,
    event_log: Any = None,
    retrieval_corpus: list[TheoremRecord] | None = None,
    status_claims: list[StatusClaim] | None = None,
    probe_predicate: Callable[[int], bool] | None = None,
    novelty_verdict: str = "N1",
    informal_only: bool = True,
    runner: ModelRunner | None = None,
    attack_evaluator: AttackEvaluator | None = None,
    lease_manager: LeaseManager | None = None,
    oeis_client: OEISClient | None = None,
    lean_service: LeanService | None = None,
    trusted_compute_service: ComputeService | None = None,
    memory: LongTermMemory | None = None,
    artifact_store: Any = None,
    intent_review: IntentCertificate | None = None,
    formal_correspondence_reviews: Mapping[
        str, FormalCorrespondenceCertificate
    ] | None = None,
    informal_reviewers: list[tuple[str, ModelRunner]] | None = None,
    lean_repair_rounds: int = 0,
    dev_lean_service: Any | None = None,
    checkpoint_dir: Path | str | None = None,
    resume_from: Path | str | None = None,
    expert_review: ExpertReviewCertificate | None = None,
    explore_blocked: bool = False,
    max_iterations: int = 4,
) -> ResearchResult:
    """Run the full research loop for one problem."""
    if budget <= 0:
        raise ValueError("budget must be positive")
    if max_iterations < 0:
        raise ValueError("max_iterations cannot be negative")
    runner = runner or DeterministicRunner()
    attack_evaluator = attack_evaluator or MechanicalAttackEvaluator()
    phases: list[str] = []
    budget_ledger = BudgetLedger(float(budget))
    runner_responses: list[dict] = []
    replay_reports: list[ReplayReport] = []
    failures: list[str] = []
    oeis_results: list[dict] = []
    formal_reports: list[dict] = []
    collected_proof_steps: list[str] = []
    release_correspondence_cert: FormalCorrespondenceCertificate | None = None
    memory = memory or LongTermMemory()

    # 1-4. freeze source, build IR + lattice, run probes, audit status
    enforcer.require("claim_graph", entry_point="orchestrator.freeze")
    contract = build_problem_contract(
        problem_id=problem_id, source_bytes=source_bytes, source_id=source_id,
        predicate=probe_predicate,
    )
    phases.append("freeze_and_parse")
    status = reconcile_status(problem_id, status_claims or [])
    phases.append("status_audit")

    # Ambiguous/false/uncertain -> honest triage; exploration allowed but no release.
    release_blocked = contract.release_blocked or status.blocks_proof_campaign
    interp = contract.lattice.nodes[0]
    intent_cert = None
    review_methods = {
        "independent_parse", "examples", "anti_examples",
        "paraphrase", "local_mutation",
    }
    expected_interpretation_hash = interpretation_review_hash(interp)
    expected_claim_hash = sha256_hex(interp.conclusion)
    intent_review_valid = (
        intent_review is not None
        and intent_review.verdict is Verdict.APPROVED
        and intent_review.source_bytes_hash == contract.source_bytes_hash
        and intent_review.interpretation_hash == expected_interpretation_hash
        and intent_review.informal_claim_hash == expected_claim_hash
        and review_methods.issubset(set(intent_review.methods))
        and verify_intent_certificate(intent_review)
    )
    # An authenticated intent review that binds THIS exact source and THIS
    # exact interpretation IS the human resolution of parser ambiguity — that
    # is what the review's independent_parse/paraphrase methods certify.  It
    # lifts only lattice ambiguity (the reviewer chose the reading); a failed
    # intake probe, a malformed statement, or a status conflict is a fact
    # about the problem no signature can lift.
    if intent_review_valid and contract.lattice.release_blocked \
            and not status.blocks_proof_campaign:
        for ambiguity in list(contract.lattice.open_ambiguities):
            contract.lattice.resolve_ambiguity(ambiguity)
        contract.lattice.approve(interp.interpretation_id)
        phases.append("interpretation_resolved_by_intent_review")
        if not contract.release_blocked:
            release_blocked = False
    if intent_review is None:
        failures.append("intent_review_unavailable")
    elif intent_review_valid and not contract.lattice.release_blocked \
            and not status.blocks_proof_campaign:
        # The reading is settled (clean parse, or resolved by this very
        # certificate) and the status is clean: the intent binds and I2 is
        # earned.  Failed intake probes (e.g. no executable countermodel)
        # still block RELEASE via ``release_blocked`` — they are a fact about
        # falsifiability, not about the reviewer's reading.
        contract.lattice.approve(interp.interpretation_id)
        intent_cert = intent_review
    else:
        failures.append("intent_review_rejected")
    log = event_log if event_log is not None else EventLog(Path(events_path), run_id=problem_id)
    graph = EpistemicGraph(log)
    graph.add_problem(Problem(
        problem_id=problem_id,
        source_versions=[{
            "source_id": contract.source_id,
            "content_hash": contract.source_bytes_hash,
            "bytes_b64": contract.source_bytes_b64,
        }],
        original_bytes_hash=contract.source_bytes_hash,
        statement_ir_hash=contract.statement_ir_hash,
        status_claims=[claim.to_dict() for claim in status.claims],
    ), actor=ACTOR)
    graph.add_interpretation(interp, actor=ACTOR)
    if intent_cert is not None:
        graph.issue_intent_certificate(intent_cert, actor={
            "type": "authority",
            "id": intent_cert.reviewer_ids[0],
            "model": "authenticated-intent-review",
            "version": intent_cert.reviewer_key_id,
        })

    # 6. short cold pass (blind), BEFORE any literature packet.  The default is
    # the lower bound of the specified 5-10% range; it is a real hard allocation.
    cold_budget = 0.05 * budget_ledger.total
    if not budget_ledger.allocate("cold_pass", cold_budget):  # defensive: exact by construction
        raise RuntimeError("unable to reserve cold-pass budget")
    # ONE structured cold pass (report R1): the worker's parsed pass is the
    # single source of falsifiers/queries/bottleneck. The previous extra raw
    # runner call duplicated this generation and fed only free text into the
    # packet. Lineage/attestation now bind to the worker's own generation;
    # legacy workers that do not expose their model identity keep the original
    # probe call so those fields never silently change meaning.
    cold_output = worker.cold_pass(contract, budget=cold_budget)
    cold_identity = getattr(worker, "last_model_identity", None)
    if cold_identity is None:
        runner_cold = runner.run(
            "MODEL IDENTITY / TRANSPORT PROBE ONLY. Do not reason about the "
            "mathematical target, propose claims, list falsifiers, or suggest "
            "retrieval queries. This response is discarded and has no "
            "decision or evidentiary authority. Return exactly the ASCII token "
            "EGMRA_IDENTITY_PROBE_OK and nothing else.",
            stage="cold_pass",
        )
        cold_identity = runner_cold.model
        runner_responses.append({
            "stage": "cold_pass", "text": runner_cold.text,
            "runner_id": runner.runner_id, "prompt_hash": runner_cold.prompt_hash,
            "model_attested": cold_identity.attested,
            "decision_used": False,   # legacy identity probe only
        })
    else:
        parsed_meta = (getattr(worker, "parsed_responses", None) or [{}])[-1]
        runner_responses.append({
            "stage": "cold_pass",
            "runner_id": runner.runner_id,
            "prompt_hash": str(parsed_meta.get("prompt_hash", "")),
            "model_attested": bool(getattr(cold_identity, "attested", False)),
            "decision_used": True,    # this generation's output drives the packet
        })
    memory.problem_local.admit({
        "problem_id": problem_id,
        "stage": "cold_pass",
        "source_bytes_hash": contract.source_bytes_hash,
        "falsifiers": list(cold_output.falsifiers),
        "search_queries": list(cold_output.search_queries),
        "bottleneck": cold_output.bottleneck,
        "cross_problem_usable": False,
    })
    phases.append("cold_pass")

    # 7. frozen solver packet (literature) — mandatory before deep proof work.
    # The cold pass's individual search queries run as their OWN targeted
    # searches (a mashed query dilutes every term); the union freezes into the
    # one auditable packet, so continuation rounds can refocus over it.
    enforcer.require("literature_retrieval", entry_point="orchestrator.packet")
    svc = RetrievalService(retrieval_corpus or [])
    packet = svc.build_packet(LiteratureQuery(
        problem_contract_hash=contract.contract_hash(),
        interpretation_id=interp.interpretation_id,
        exact_statements=(interp.conclusion,),
        objects=tuple(interp.conclusion.split()[:6]),
        techniques=tuple(dict.fromkeys([
            *cold_output.search_queries,
            *cold_output.falsifiers,
        ])),
    ), limit=8, extra_queries=tuple(cold_output.search_queries[:8]))
    phases.append("freeze_solver_packet")

    # 8. score/acquire.  Selection is a real production call, not an unconditional
    # label.  A blocked target may still be explored, but an empty/malformed target
    # and a run with no deep-search budget are not acquired.
    domain = _domain_for_contract(contract)
    features = ProblemFeatures(
        problem_id=problem_id,
        open_state_source_count=len(status_claims or []),
        last_status_review="current" if status_claims else "",
        database_conflicts=int(status.blocks_proof_campaign),
        ambiguity_count=len(contract.lattice.open_ambiguities),
        formal_clarity=max(0.0, 1.0 - contract.target_fidelity_risk),
        number_of_parts=1 if interp.conclusion.strip() else 0,
        parameter_regimes=1 if contract.primary_ir.parameter_regime else 0,
        theorem_density=float(len(packet.theorem_records)),
        finite_reductions=int(probe_predicate is not None),
        falsifiability=1.0 if probe_predicate is not None else 0.0,
        certificate_available=probe_predicate is not None,
        domain=domain,
        expected_cost=max(1.0, budget_ledger.total - cold_budget),
    )
    selector = ProblemSelector(seed=0)
    selected = selector.select([(features, CompetingRiskPosterior())], k=1)
    acquired = problem_id in selected and budget_ledger.remaining > 0
    # Interpretation ambiguity is the dominant live funnel drop: the selector
    # honestly declines targets whose reading is disputed, so blocked problems
    # end with zero branch work. ``explore_blocked`` overrides ACQUISITION
    # only — lemmas, falsifiers, and experiments still accumulate under the
    # primary interpretation while release stays blocked (a blocked
    # interpretation can never certify), and the override is recorded.
    if explore_blocked and release_blocked and not acquired \
            and budget_ledger.remaining > 0 and interp.conclusion.strip():
        acquired = True
        failures.append("acquisition_overridden_for_blocked_exploration")
        phases.append("explore_blocked_override")
    phases.append("score_and_acquire")

    # 9-10. Instantiate mechanism-distinct programs and a direct-first AND/OR
    # blueprint. These are the actual objects consumed by branch selection below.
    action_budget = (
        budget_ledger.remaining / max(1, max_iterations) if max_iterations else 0.0
    )
    programs = instantiate_programs(
        domain,
        bottleneck=cold_output.bottleneck,
        budget_each=action_budget,
        # CDC/Kerger long-horizon search: the old hard cap of three meant
        # max_iterations > 3 could never run more than three method families.
        # The caller's bounded max_iterations is already the spend/termination
        # control; domain compatibility and quality-diversity dedupe remain.
        max_programs=max(1, min(max_iterations, 8)) if max_iterations else 1,
        # Stratified wave signals (report R2): a community Lean target steers
        # the tool stratum toward formal_library_first; an executable predicate
        # toward computational_finite_reduction.
        has_formal_target=bool(getattr(worker, "formal_target", "")),
        has_predicate=probe_predicate is not None,
    ) if acquired else []
    diversity_archive = QualityDiversityArchive()
    program_fingerprints: dict[str, MechanismFingerprint] = {}
    distinct_programs: list[ResearchProgram] = []
    for program in programs:
        fingerprint = _program_fingerprint(
            program, interpretation_id=interp.interpretation_id,
            conclusion=interp.conclusion, bottleneck=cold_output.bottleneck,
            packet=packet,
        )
        if diversity_archive.consider(
            fingerprint, quality=features.formal_clarity, branch_id=program.family,
        ):
            distinct_programs.append(program)
            program_fingerprints[program.family] = fingerprint
    programs = distinct_programs
    # Problem-specific adversarial checklist + approach-family registry, both
    # rendered read-only into worker prompts (search guidance, never truth):
    # traps come from the lattice's ambiguity nodes and failed probes; the
    # family registry surfaces prior blocked routes so they are only reopened
    # with a materially new mechanism (CDC-prompt discipline).
    if hasattr(worker, "problem_traps"):
        traps = _derive_problem_traps(contract)
        if traps:
            worker.problem_traps[:] = traps
    if hasattr(worker, "family_history"):
        history = _family_history_lines(memory, problem_id)
        if history:
            worker.family_history[:] = history
    debt_policy = DebtPolicy()
    debt_obligations = {
        program.family: Obligation(
            obligation_id=f"leaf:{program.family}", closed=False,
            risk=contract.target_fidelity_risk,
            cost=action_budget,
            kind="goal" if program.family == "direct_structural" else "helper",
        )
        for program in programs
    }
    initial_debt = verified_debt(list(debt_obligations.values()), debt_policy)
    blueprint = _build_blueprint(goal_claim_id, interp.conclusion, programs)
    for program in programs:
        fingerprint = program_fingerprints[program.family]
        graph.add_branch(Branch(
            branch_id=program.family,
            goal_claim_ids=[goal_claim_id],
            interpretation_id=interp.interpretation_id,
            mechanism_fingerprint={
                "target_interpretation": interp.interpretation_id,
                "reformulation": interp.conclusion,
                "method_family": program.family,
                "central_proposed_lemma": cold_output.bottleneck,
                "objects_invariants": [],
                "external_theorems": [],
                "computational_signature": (
                    "finite exact computation"
                    if program.family == "computational_finite_reduction" else ""
                ),
                "expected_falsifiers": [program.falsifier],
                "formalization_route": (
                    "local Lean" if program.family == "formal_library_first" else ""
                ),
                "worker_role": _branch_role(program.family, worker),
                "fingerprint_hash": fingerprint.fingerprint_hash(),
                "quality_diversity_bin": list(fingerprint.quality_diversity_bin()),
            },
        ), actor=ACTOR)
    phases.extend(["generate_programs", "build_blueprint"])

    # 11-14. Dynamic leased branch execution with posterior allocation and typed
    # evidence admission. Every action is charged before invocation.
    router = EvidenceRouter(graph)
    controller = Controller(global_budget=budget_ledger.remaining, seed=0)
    for program in programs:
        controller.register(BranchPosterior(program.family))
    # R12-lite cross-problem priors: earlier runs sharing this LongTermMemory
    # (a campaign) recorded per-family outcomes into procedural memory; replay
    # them (bounded) so families that actually produce supported claims start
    # ahead. Never a truth signal — only search-order preference.
    _seed_controller_from_memory(controller, memory, programs)
    leases = lease_manager or LeaseManager()
    authority_issuer = AuthorityTokenIssuer()
    blackboard = Blackboard(graph, authority_guard=authority_issuer)
    packet_payload = packet.to_dict()
    board_packet_hash = content_id(packet_payload)
    if trusted_compute_service is None:
        # The orchestrator re-authenticates evidence against the SAME compute
        # service the worker executed on, so a worker that owns a sandboxed
        # service (fixture or model-backed) makes finite computation reachable.
        trusted_compute_service = getattr(worker, "compute_service", None)
    phases.append("deep_branches")
    attempted: set[str] = set()
    # R3 phase 1: unclosed subgoals carried across branches (bounded, dedup) so
    # each later family attacks the specific remaining gaps.
    carried_subgoals: list[str] = []
    # R9: bounded auditable packet re-entry state (queries already retried and
    # how many chained packet versions were created for this problem).
    reentry_seen_queries: set[str] = {e.query_text for e in packet.query_log}
    reentry_count = 0
    # Consume a durable within-problem checkpoint: a verified prior snapshot
    # seeds the attempted-branch set (no branch is re-bought) and re-books the
    # budget already spent.  Verification fails closed — a bad checkpoint is
    # recorded and the run simply starts fresh.
    if resume_from is not None:
        resumed = _load_resume_checkpoint(
            resume_from, problem_id=problem_id, contract=contract, log=log,
            failures=failures,
        )
        if resumed is not None:
            resumed_branches, prior_spend, chain_verified = resumed
            if chain_verified:
                # A verified continuation of THIS run's own event chain: skip
                # already-bought branches and re-book the budget they spent.
                attempted.update(resumed_branches)
                if prior_spend > 0:
                    budget_ledger.allocate(
                        "resumed_prior_spend",
                        min(budget_ledger.remaining, prior_spend))
                phases.append("resume_verified")
            else:
                # A NEW attempt is a fresh independent sample.  Prior learning
                # arrives through the dossier and the exchange cache (replays
                # are free); seeding prior branch families or re-booking prior
                # spend here silently turned every later attempt into a
                # zero-work no-op that burned the mathematical budget.
                phases.append("resume_fresh_attempt")
    for _ in range(max_iterations):
        if not acquired or not programs or not controller.has_budget():
            break
        candidates = [
            (
                program.family,
                ActionComponents(
                    expected_outcome_value=features.formal_clarity,
                        info_gain=0.5,
                        unlock=(
                            1.0 / (1.0 + initial_debt.debt)
                            if initial_debt.debt else 0.0
                        ),
                    diversity=1.0 if program.family not in attempted else 0.0,
                    falsification_value=features.falsifiability,
                    expected_cost=action_budget,
                    semantic_risk=contract.target_fidelity_risk,
                ),
            )
            for program in programs
            if program.family not in attempted
        ]
        if not candidates:
            break
        # Branch selection is the numeric controller's decision (direct-first on
        # the opening wave, posterior selection afterwards). The former model
        # call here was recorded and then IGNORED — pure cost on the serialized
        # provider budget (report R1) — so it was removed outright.
        direct_first = next(
            (branch for branch, _ in candidates if branch == "direct_structural"),
            None,
        ) if not attempted else None
        chosen = (
            [direct_first] if direct_first is not None
            else controller.select_posterior_actions(candidates, k=1)
        )
        if not chosen:
            break
        branch_id = chosen[0]
        if not budget_ledger.allocate("branch", action_budget, branch_id=branch_id):
            failures.append("budget_exhausted")
            break
        if not controller.allocate(
            branch_id, action_budget, verified_debt_reduction=0.0, info_gain=0.5,
        ):
            failures.append(f"controller_rejected:{branch_id}")
            break
        attempted.add(branch_id)
        lease = leases.acquire(
            branch_id=branch_id, holder="local:orchestrator", stage="deep_branch",
            run_contract_id=contract.contract_hash(),
            grace_seconds=_BRANCH_LEASE_GRACE_SECONDS,
        )
        worker_token = authority_issuer.issue(
            authority_name="program_worker",
            subject=f"worker:{branch_id}",
            resources=(f"branch:{branch_id}", f"packet:{board_packet_hash}"),
            lineage=cold_identity.label,
        )
        branch_slice = blackboard.read_slice(
            branch_id=branch_id, packet_hash=board_packet_hash,
            packet=packet_payload, token=worker_token,
        )
        # A distinct role per mechanism branch: prover / experimentalist /
        # formalizer reason from different prompts (task 4.11). The base worker is
        # reused when it does not support role specialization.
        branch_role = _branch_role(branch_id, worker)
        branch_worker = worker.for_role(branch_role) if hasattr(worker, "for_role") else worker
        try:
            with _lease_heartbeat(leases, lease):
                output = branch_worker.work_branch(
                    contract, packet, branch_id=branch_id, budget=action_budget,
                    fencing_token=lease.fencing_token, branch_slice=branch_slice,
                )
            # The fence is checked after the worker finishes and immediately
            # before any proposal, evidence, or replay report is consumed.
            # Losing the lease therefore invalidates the entire returned batch.
            leases.assert_current(branch_id, lease.holder, lease.fencing_token)
        except LeaseError as exc:
            failures.append(f"stale_worker_rejected:{branch_id}:{exc}")
            controller.update_posterior(branch_id, success=False, debt_reduction=0.0)
            continue
        except BrowserRunnerError:
            # Provider throttling/unusable browser output is handled by the
            # caller's durable retain/resume policy, never converted into a
            # mathematical branch failure.
            raise
        except Exception as exc:  # noqa: BLE001 - isolate one failed worker branch
            failures.append(
                f"worker_crashed:{branch_id}:{type(exc).__name__}:{exc}"
            )
            controller.update_posterior(branch_id, success=False, debt_reduction=0.0)
            continue
        finally:
            try:
                leases.release(
                    branch_id, lease.holder, fencing_token=lease.fencing_token,
                )
            except LeaseError:
                # A replacement worker now owns the branch.  Its lease is not
                # ours to release, and the stale output above has been dropped.
                pass
        # LIVE-CAMPAIGN FIX: the pre-branch token above expires after 300s,
        # but a browser branch legitimately reasons for HOURS — write-phase
        # authority must be issued AFTER the worker returns, once the lease
        # fence has validated the batch. Elapsed-time staleness is the
        # LEASE's job (heartbeat + fence); the token scopes authority, so a
        # fresh short-lived token here keeps both properties honest instead
        # of failing every long branch with 'authority token has expired'.
        worker_token = authority_issuer.issue(
            authority_name="program_worker",
            subject=f"worker:{branch_id}",
            resources=(f"branch:{branch_id}", f"packet:{board_packet_hash}"),
            lineage=cold_identity.label,
        )
        replay_reports.extend(output.replay_reports)
        failures.extend(output.failures)
        collected_proof_steps.extend(
            step for step in output.proof_steps
            if step not in collected_proof_steps
        )
        memory.problem_local.admit({
            "problem_id": problem_id,
            "stage": "branch",
            "branch_id": branch_id,
            "role": branch_role,
            "failures": list(output.failures),
            "falsifiers": list(output.falsifiers),
            "proof_steps": list(output.proof_steps),
            "assumptions": list(output.assumptions),
            "formalization_requests": list(output.formalization_requests),
            "sequence_hashes": [content_id(sequence) for sequence in output.generated_sequences],
            "cross_problem_usable": False,
        })
        for sequence in output.generated_sequences:
            blackboard.write_proposal({
                "kind": "next_experiment", "branch_id": branch_id,
                "tool": "oeis_read_only", "sequence": list(sequence),
            }, token=worker_token)
            if oeis_client is None:
                failures.append(f"oeis_unavailable:{branch_id}:not_configured")
                continue
            try:
                response = oeis_client.query_terms(list(sequence))
            except (OEISUnavailable, OSError, ValueError) as exc:
                failures.append(f"oeis_unavailable:{branch_id}:{exc}")
                continue
            oeis_results.append({
                "branch_id": branch_id,
                "sequence_hash": content_id(sequence),
                "query": response.query,
                "content_hash": response.content_hash,
                "retrieved_at": response.retrieved_at,
                "from_cache": response.from_cache,
                "entry_count": len(response.entries()),
            })
        # Validate the whole proposal batch before materializing dependencies.
        # Model output is not guaranteed to be topologically ordered; unknown or
        # circular dependencies are rejected as branch failures rather than
        # crashing the research run or entering a cyclic proof graph.
        pending_claims: dict[str, dict[str, Any]] = {}
        for prop in output.claim_proposals:
            try:
                accepted = blackboard.write_proposal({
                    **prop, "kind": "claim_proposal", "branch_id": branch_id,
                }, token=worker_token)
                claim_id = accepted.get("claim_id")
                formula = accepted.get("canonical_formula")
                dependencies = accepted.get("dependencies", [])
                if not isinstance(claim_id, str) or not claim_id.strip() \
                        or not isinstance(formula, str) or not formula.strip() \
                        or not isinstance(dependencies, list) \
                        or any(not isinstance(dep, str) or not dep.strip()
                               for dep in dependencies):
                    raise BlackboardError("claim proposal has an invalid claim/formula/dependency")
            except (BlackboardError, KeyError, TypeError, ValueError) as exc:
                failures.append(f"claim_proposal_malformed:{branch_id}:{exc}")
                continue
            if claim_id in graph.claims:
                continue
            if claim_id in pending_claims:
                failures.append(f"duplicate_claim_proposal:{branch_id}:{claim_id}")
                continue
            pending_claims[claim_id] = accepted

        while pending_claims:
            progressed = False
            for claim_id, accepted in list(pending_claims.items()):
                dependencies = accepted.get("dependencies", [])
                unresolved_external = [
                    dep for dep in dependencies
                    if dep not in graph.claims and dep not in pending_claims
                ]
                if unresolved_external:
                    failures.append(
                        f"claim_dependency_cycle_or_unknown:{branch_id}:{claim_id}:"
                        + ",".join(unresolved_external)
                    )
                    del pending_claims[claim_id]
                    progressed = True
                    continue
                if any(dep not in graph.claims for dep in dependencies):
                    continue
                # The locked target text, not worker-selected prose, is the
                # canonical goal formula. Workers may propose subsidiary claims,
                # but cannot silently substitute the research target.
                canonical_formula = (
                    interp.conclusion if claim_id == goal_claim_id
                    else accepted["canonical_formula"]
                )
                graph.propose_claim(
                    claim_id=claim_id, interpretation_id=interp.interpretation_id,
                    canonical_formula=canonical_formula,
                    informal_text=(interp.conclusion if claim_id == goal_claim_id
                                   else accepted.get("informal_text", "")),
                    dependencies=dependencies,
                    scope=accepted.get("scope", "general"), actor=ACTOR)
                if claim_id == goal_claim_id and intent_cert is not None:
                    graph.bind_intent_certificate(
                        goal_claim_id, intent_cert.certificate_id, actor=ACTOR,
                    )
                del pending_claims[claim_id]
                progressed = True
            if not progressed:
                for claim_id, accepted in pending_claims.items():
                    failures.append(
                        f"claim_dependency_cycle_or_unknown:{branch_id}:{claim_id}:"
                        + ",".join(accepted.get("dependencies", []))
                    )
                break
        for ev in output.evidence:
            try:
                if not isinstance(ev, dict):
                    raise TypeError("evidence proposal must be an object")
                accepted = blackboard.write_proposal({
                    **ev, "evidence_kind": ev.get("kind", ""),
                    "kind": "evidence_proposal", "branch_id": branch_id,
                }, token=worker_token)
                evidence_id = accepted.get("evidence_id")
                if not isinstance(evidence_id, str) or not evidence_id.strip():
                    raise BlackboardError("evidence proposal has no evidence_id")
                if evidence_id in graph.evidence:
                    continue
                evidence = _authenticate_computation_proposal(
                    accepted, graph=graph, compute_service=trusted_compute_service,
                    replay_reports=output.replay_reports, intent_cert=intent_cert,
                )
            except (BlackboardError, KeyError, TypeError, ValueError) as exc:
                failures.append(f"evidence_proposal_malformed:{branch_id}:{exc}")
                continue
            if evidence is None:
                failures.append(f"untrusted_evidence_proposal:{evidence_id}")
                continue
            enforcer.require("computation_service", entry_point="orchestrator.compute")
            router.admit(evidence, actor=ACTOR)
        # Audited literature→lemma imports: the model may CITE a frozen-packet
        # record as support for a claim, but never authors provenance — every
        # field of the evidence comes from the packet record itself, and the
        # citation is rejected unless the claim's formula genuinely overlaps
        # the record text.  A single audited import records provenance only
        # (ExternalImport.AUDITED_SOURCE never supports); corroboration — and
        # hence support — requires ≥2 passing records from distinct hosts.
        _admit_literature_imports(
            output.literature_imports, packet=packet, graph=graph,
            router=router, branch_id=branch_id, failures=failures,
        )
        for candidate in output.formal_candidates:
            formal_token = authority_issuer.issue(
                authority_name="formalization_authority",
                subject=f"formalizer:{branch_id}",
                resources=(f"branch:{branch_id}", f"packet:{board_packet_hash}"),
                lineage="lean-service",
            )
            try:
                if not isinstance(candidate, dict):
                    raise TypeError("formal candidate must be an object")
                accepted = blackboard.write_proposal({
                    **candidate, "kind": "formal_artifact", "branch_id": branch_id,
                }, token=formal_token)
            except (BlackboardError, KeyError, TypeError, ValueError) as exc:
                failures.append(f"formal_candidate_malformed:{branch_id}:{exc}")
                continue
            required_strings = (
                "claim_id", "source", "declaration_name", "lean_version",
                "mathlib_commit", "project_hash", "expected_type_hash",
                "immutable_target_module_hash",
            )
            if any(not isinstance(accepted.get(name), str) or not accepted[name].strip()
                   for name in required_strings) \
                    or not is_sha256(accepted["project_hash"]) \
                    or not is_sha256(accepted["expected_type_hash"]) \
                    or not is_sha256(accepted["immutable_target_module_hash"]):
                failures.append(f"formal_candidate_malformed:{branch_id}")
                continue
            if accepted["claim_id"] not in graph.claims:
                failures.append(f"formal_candidate_unknown_claim:{accepted['claim_id']}")
                continue
            if lean_service is None:
                failures.append(f"formal_verification_unavailable:{branch_id}")
                continue
            try:
                environment = lean_service.create_environment(
                    lean_version=accepted["lean_version"],
                    mathlib_commit=accepted["mathlib_commit"],
                    project_hash=accepted["project_hash"],
                    trust_policy=accepted.get("trust_policy", "classical-whitelist"),
                    imports=tuple(accepted.get("imports", ())),
                    options=dict(accepted.get("options", {})),
                )
            except Exception as exc:  # noqa: BLE001 - external verifier isolation
                failures.append(
                    f"formal_verification_error:{branch_id}:"
                    f"{type(exc).__name__}:{exc}"
                )
                continue
            # A checker EXCEPTION (lake crash, OOM, timeout) is
            # infrastructure, not a mathematical verdict — conflating the two
            # is a false-rejection channel. Retry ONCE; only a repeated
            # failure is recorded (as before). A genuine kernel REJECTION
            # (passed=False) never raises and is never retried here.
            formal_certificate = None
            for verification_attempt in (1, 2):
                try:
                    formal_certificate = lean_service.verify_declaration(
                        environment=environment,
                        source=accepted["source"],
                        declaration_name=accepted["declaration_name"],
                        expected_type_hash=accepted["expected_type_hash"],
                        immutable_target_module_hash=accepted["immutable_target_module_hash"],
                        expected_type_source=accepted.get("expected_type_source", ""),
                        claim_bindings={
                            accepted["claim_id"]: graph.claims[
                                accepted["claim_id"]
                            ].canonical_hash,
                        },
                        artifact_hashes=(
                            accepted["project_hash"],
                            accepted["immutable_target_module_hash"],
                        ),
                    )
                    break
                except Exception as exc:  # noqa: BLE001 - external verifier isolation
                    if verification_attempt == 1:
                        failures.append(
                            f"formal_verification_infra_retry:{branch_id}:"
                            f"{type(exc).__name__}")
                        continue
                    failures.append(
                        f"formal_verification_error:{branch_id}:"
                        f"{type(exc).__name__}:{exc}"
                    )
            if formal_certificate is None:
                continue
            formal_reports.append({
                "branch_id": branch_id,
                "claim_id": accepted["claim_id"],
                **formal_certificate.to_dict(),
            })
            # Autonomous bounded Lean repair: a kernel-REJECTED candidate goes
            # back to the configured formalizer together with the pinned
            # checker's diagnostics; the obligation (declaration name +
            # expected type + hashes) never changes, and every repaired source
            # is re-checked by the same pinned kernel.  Exhausted repairs leave
            # the candidate rejected exactly as before \u2014 never masked.
            # KERNEL-CHECKED EQUIVALENCE BRIDGE: a vendor sometimes proves
            # the right mathematics in a differently-CAST form (ℕ vs ℤ
            # coercions, simp-normal shape). The definitional obligation then
            # fails even though a one-line bridge closes it. Before spending
            # vendor repair rounds, try ONE local bridge declaration —
            # `first | exact | exact_mod_cast | simpa` — dev-prechecked on
            # the warm REPL, then verified by the SAME sealed kernel against
            # the SAME pinned expected_type_hash. No trust change: the bridge
            # is just more Lean source through the unchanged checker; a
            # failed bridge changes nothing.
            if not formal_certificate.passed and dev_lean_service is not None \
                    and accepted.get("expected_type_source", "").strip():
                bridge_name = f"{accepted['declaration_name']}_egmra_bridge"
                bridge_source = (
                    accepted["source"].rstrip() + "\n\n"
                    f"theorem {bridge_name} : "
                    f"{accepted['expected_type_source'].strip()} := by\n"
                    "  first\n"
                    f"  | exact {accepted['declaration_name']}\n"
                    f"  | exact_mod_cast {accepted['declaration_name']}\n"
                    f"  | simpa using {accepted['declaration_name']}\n")
                bridge_ok = False
                try:
                    bridge_dev = dev_lean_service.check(dev_obligation_source(
                        bridge_source, declaration_name=bridge_name,
                        expected_type_source=accepted["expected_type_source"]))
                    bridge_ok = bool(bridge_dev.ok and not bridge_dev.sorries)
                except Exception:  # noqa: BLE001 - dev isolation, fail open
                    bridge_ok = False
                if bridge_ok:
                    try:
                        bridge_certificate = lean_service.verify_declaration(
                            environment=environment,
                            source=bridge_source,
                            declaration_name=bridge_name,
                            expected_type_hash=accepted["expected_type_hash"],
                            immutable_target_module_hash=accepted[
                                "immutable_target_module_hash"],
                            expected_type_source=accepted.get(
                                "expected_type_source", ""),
                            claim_bindings={
                                accepted["claim_id"]: graph.claims[
                                    accepted["claim_id"]
                                ].canonical_hash,
                            },
                            artifact_hashes=(
                                accepted["project_hash"],
                                accepted["immutable_target_module_hash"],
                            ),
                        )
                    except Exception as exc:  # noqa: BLE001 - verifier isolation
                        failures.append(
                            f"formal_bridge_error:{branch_id}:"
                            f"{type(exc).__name__}")
                    else:
                        formal_reports.append({
                            "branch_id": branch_id,
                            "claim_id": accepted["claim_id"],
                            "equivalence_bridge": True,
                            **bridge_certificate.to_dict(),
                        })
                        if bridge_certificate.passed:
                            failures.append(
                                f"formal_bridge_applied:{branch_id}:"
                                f"{bridge_name}")
                            formal_certificate = bridge_certificate
                            accepted = {**accepted, "source": bridge_source,
                                        "declaration_name": bridge_name}
            formalizer = getattr(worker, "formalizer", None)
            if not formal_certificate.passed and formalizer is not None \
                    and lean_repair_rounds > 0 and _supports_repair(formalizer):
                current_source = accepted["source"]
                dev_feedback: str | None = None
                for repair_round in range(1, int(lean_repair_rounds) + 1):
                    if dev_feedback is not None:
                        feedback = dev_feedback
                    else:
                        feedback = "; ".join((
                            *formal_certificate.placeholder_findings,
                            *formal_certificate.unsafe_findings,
                        ))[:1200]
                    try:
                        repaired = formalizer.formalize(
                            declaration_name=accepted["declaration_name"],
                            expected_type=accepted.get(
                                "expected_type_source", ""),
                            informal_statement=interp.conclusion,
                            previous_source=current_source,
                            kernel_feedback=feedback,
                        )
                    except Exception as exc:  # noqa: BLE001 - vendor outage isolation
                        failures.append(
                            f"formal_repair_error:{branch_id}:"
                            f"{type(exc).__name__}")
                        break
                    repaired = (repaired or "").strip()
                    if not repaired or repaired == current_source:
                        failures.append(
                            f"formal_repair_unavailable:{branch_id}:"
                            f"round{repair_round}")
                        break
                    current_source = repaired
                    # R5: warm DEVELOPMENT pre-check — a repaired candidate
                    # that does not even development-compile never spends a
                    # sealed cold kernel run; its diagnostics feed the next
                    # repair round instead. Development verdicts are search
                    # guidance only; any dev failure falls OPEN to the sealed
                    # check exactly as before.
                    if dev_lean_service is not None:
                        try:
                            dev_result = dev_lean_service.check(
                                dev_obligation_source(
                                    repaired,
                                    declaration_name=accepted[
                                        "declaration_name"],
                                    expected_type_source=accepted.get(
                                        "expected_type_source", ""),
                                ))
                        except Exception:  # noqa: BLE001 - dev isolation
                            dev_result = None
                        if dev_result is not None and (
                                not dev_result.ok or dev_result.sorries):
                            failures.append(
                                f"formal_dev_precheck_failed:{branch_id}:"
                                f"round{repair_round}")
                            dev_feedback = "; ".join(
                                dev_result.messages)[:1200] or \
                                "development compile failed"
                            if dev_result.sorries:
                                dev_feedback = (
                                    "sorry placeholders are forbidden; "
                                    + dev_feedback)[:1200]
                            continue
                    dev_feedback = None
                    try:
                        formal_certificate = lean_service.verify_declaration(
                            environment=environment,
                            source=repaired,
                            declaration_name=accepted["declaration_name"],
                            expected_type_hash=accepted["expected_type_hash"],
                            immutable_target_module_hash=accepted[
                                "immutable_target_module_hash"],
                            expected_type_source=accepted.get(
                                "expected_type_source", ""),
                            claim_bindings={
                                accepted["claim_id"]: graph.claims[
                                    accepted["claim_id"]
                                ].canonical_hash,
                            },
                            artifact_hashes=(
                                accepted["project_hash"],
                                accepted["immutable_target_module_hash"],
                            ),
                        )
                    except Exception as exc:  # noqa: BLE001 - verifier isolation
                        failures.append(
                            f"formal_verification_error:{branch_id}:"
                            f"{type(exc).__name__}:{exc}")
                        break
                    formal_reports.append({
                        "branch_id": branch_id,
                        "claim_id": accepted["claim_id"],
                        "repair_round": repair_round,
                        **formal_certificate.to_dict(),
                    })
                    # FALSE-REJECTION SENTINEL: the warm development REPL
                    # accepted this exact obligation but the sealed checker
                    # rejected it. That signature usually means an
                    # environment/toolchain mismatch or an over-strict sealed
                    # gate — an operator should look at it, because the math
                    # may be correct. Telemetry only; the sealed verdict
                    # stands untouched.
                    if not formal_certificate.passed \
                            and dev_lean_service is not None \
                            and dev_feedback is None:
                        failures.append(
                            f"checker_discrepancy:{branch_id}:"
                            f"round{repair_round}:dev_accepted_sealed_rejected")
                    if formal_certificate.passed:
                        accepted = {**accepted, "source": repaired}
                        break
            if formal_certificate.passed:
                correspondence = (formal_correspondence_reviews or {}).get(
                    accepted["claim_id"]
                )
                claim = graph.claims[accepted["claim_id"]]
                correspondence_valid = bool(
                    intent_cert is not None
                    and correspondence is not None
                    and correspondence.verdict is Verdict.APPROVED
                    and bool(correspondence.reviewer_ids)
                    and verify_formal_correspondence_certificate(correspondence)
                    and correspondence.intent_certificate_id
                    == intent_cert.certificate_id
                    and correspondence.informal_claim_hash == claim.canonical_hash
                    and correspondence.lean_declaration_name
                    == accepted["declaration_name"]
                    and correspondence.elaborated_type_hash
                    == accepted["expected_type_hash"]
                )
                if not correspondence_valid or correspondence is None or intent_cert is None:
                    failures.append(f"formal_correspondence_required:{branch_id}")
                    continue
                if correspondence.certificate_id not in graph.correspondence_certificates:
                    graph.issue_correspondence_certificate(correspondence, actor={
                        "type": "authority",
                        "id": correspondence.reviewer_ids[0],
                        "model": "authenticated-formal-correspondence-review",
                        "version": correspondence.reviewer_key_id,
                    })
                certificate_envelope = formal_certificate.to_dict()
                evidence = Evidence(
                    evidence_id="formal_" + formal_certificate.certificate_digest[:20],
                    claim_ids=[claim.claim_id],
                    kind=EvidenceKind.LEAN_PROOF,
                    assertion_scope=claim.scope,
                    claim_bindings={claim.claim_id: claim.canonical_hash},
                    artifact_hashes=list(dict.fromkeys((
                        formal_certificate.certificate_digest,
                        *formal_certificate.artifact_hashes,
                    ))),
                    generator_identity={
                        "id": formal_certificate.checker_id,
                        "formal_certificate": certificate_envelope,
                        "source_hash": formal_certificate.source_hash,
                    },
                    verifier_identities=[{
                        "id": formal_certificate.independent_checker_id
                        or formal_certificate.checker_id,
                        "attested": True,
                    }],
                    diversity_profile={
                        "kernel_checker": formal_certificate.checker_id,
                        "independent_checker": formal_certificate.independent_checker_id,
                    },
                    environment_hash=formal_certificate.environment_id,
                    replay_command=(
                        "LeanService.verify_declaration:"
                        + accepted["declaration_name"]
                    ),
                    replay_result="pass",
                    intent_certificate_id=intent_cert.certificate_id,
                    formal_correspondence_certificate_id=correspondence.certificate_id,
                    trust_assumptions=[
                        "pinned Lean environment and isolated checker key",
                    ],
                )
                if evidence.evidence_id not in graph.evidence:
                    router.admit(attest_evidence(evidence), actor=ACTOR)
                if claim.claim_id == goal_claim_id:
                    release_correspondence_cert = correspondence
            else:
                failures.append(f"formal_verification_failed:{branch_id}")
        supported = bool(
            graph.claims.get(goal_claim_id)
            and graph.claims[goal_claim_id].truth_status.value == "SUPPORTED"
        )
        # Obligation-level credit (report R3): a branch that produced a
        # verified CHILD claim made real search progress even when the goal
        # itself stays open. The controller and the family registry learn from
        # that, not only from terminal goal support. Truth is untouched — this
        # only shapes future allocation.
        supported_children = [
            proposal["claim_id"]
            for proposal in output.claim_proposals
            if proposal["claim_id"] != goal_claim_id
            and proposal["claim_id"] in graph.claims
            and graph.claims[proposal["claim_id"]].truth_status.value == "SUPPORTED"
        ]
        search_success = supported or bool(supported_children)
        before_obligations = list(debt_obligations.values())
        if supported:
            # Closing one sufficient OR route discharges the target; alternative
            # routes become explicitly closed-as-unneeded rather than silently
            # disappearing from the frozen debt inventory.
            debt_obligations = {
                key: replace(obligation, closed=True)
                for key, obligation in debt_obligations.items()
            }
        else:
            debt_obligations[branch_id] = replace(
                debt_obligations[branch_id], closed=False,
            )
        debt_reduction = delta_verified_debt(
            before_obligations, list(debt_obligations.values()), debt_policy,
        )
        controller.update_posterior(
            branch_id, success=search_success, debt_reduction=debt_reduction,
        )
        memory.procedural.admit({
            "kind": "branch_family_outcome",
            "problem_id": problem_id,
            "branch_family": branch_id,
            "supported": bool(search_success),
            "supported_children": list(supported_children),
            "cross_problem_usable": True,
        })
        # R3 phase 1: feed this branch's unclosed subgoals forward so the NEXT
        # family attacks the specific remaining gaps (search guidance only).
        for subgoal in output.open_subgoals:
            text = str(subgoal).strip()[:300]
            if text and text not in carried_subgoals:
                carried_subgoals.append(text)
        del carried_subgoals[:-8]
        if hasattr(worker, "carried_subgoals"):
            worker.carried_subgoals[:] = carried_subgoals
        # R9: auditable retrieval RE-ENTRY — a branch's own queries may name a
        # subgoal the frozen packet never covered. Re-query the LOCAL corpus
        # index and extend the packet as a new chained VERSION (never mutated;
        # parent hash + trigger + queries recorded in a signed event). The
        # blackboard keeps the original packet identity (authority slices bind
        # the frozen v1); imports audit against the current version.
        new_queries = [
            q.strip() for q in output.search_queries
            if q.strip() and q.strip() not in reentry_seen_queries
        ][:4]
        if new_queries and getattr(svc, "corpus", None) and reentry_count < 2:
            reentry_seen_queries.update(new_queries)
            fresh_records = []
            known_ids = {r.theorem_id for r in packet.theorem_records}
            for query in new_queries:
                for record, _score in svc.index.search(query, limit=2):
                    if record.theorem_id not in known_ids:
                        known_ids.add(record.theorem_id)
                        fresh_records.append(record)
            if fresh_records:
                reentry_count += 1
                parent_hash = packet.packet_hash()
                packet = packet.reentry(
                    new_records=fresh_records,
                    reason=f"branch {branch_id} queries: " + "; ".join(new_queries)[:300],
                    new_packet_id=f"{packet.packet_id}-r{reentry_count}",
                )
                log.append(
                    action="PACKET_REENTRY", actor=ACTOR, object_ids=[problem_id],
                    reason_code="retrieval_reentry",
                    human_readable_reason=(
                        f"packet re-entry after {branch_id}: "
                        f"{len(fresh_records)} new records"),
                    payload={
                        "parent_packet_hash": parent_hash,
                        "new_packet_hash": packet.packet_hash(),
                        "queries": new_queries,
                        "added_theorem_ids": [r.theorem_id for r in fresh_records],
                    },
                )
        leaf = blueprint.nodes.get(f"leaf:{branch_id}")
        if leaf is not None:
            leaf.closed = supported
        if branch_id == "direct_structural":
            blueprint.direct_attempted = True
        # Persist browser/model exchange provenance as soon as this branch is
        # complete. In particular, the exact ChatGPT conversation URL now
        # survives a crash in a later branch. _record_model_exchanges is
        # idempotent against events already in the log.
        if artifact_store is not None:
            _record_model_exchanges(
                log, artifact_store, problem_id,
                runners=(runner, getattr(worker, "runner", None),
                         getattr(branch_worker, "runner", None)),
            )
            if "record_exchanges" not in phases:
                phases.append("record_exchanges")
        # Durable within-problem checkpoint: after each completed branch, seal
        # a signed snapshot of the event-log prefix + graph view so a crashed
        # long run leaves verifiable state behind.  Checkpointing is an ops
        # aid: a write failure is recorded and never becomes a math verdict.
        if checkpoint_dir is not None:
            _write_branch_checkpoint(
                checkpoint_dir, problem_id=problem_id, branch_id=branch_id,
                log=log, contract=contract, interp=interp, graph=graph,
                budget_ledger=budget_ledger, failures=failures,
                attempted=attempted,
            )
            if "checkpoint" not in phases:
                phases.append("checkpoint")
        if supported:
            break

    # Durable, content-addressed model-exchange artifacts + signed events (4.10).
    if artifact_store is not None:
        _record_model_exchanges(log, artifact_store, problem_id,
                                runners=(runner, getattr(worker, "runner", None)))
        if "record_exchanges" not in phases:
            phases.append("record_exchanges")

    # 15a. Hostile natural-language review of the PROPOSED dependency cone
    # (the T3 informal-evidence producer). Runs before assembly because the
    # compiler admits only SUPPORTED claims; the review is what can support
    # them. Fail-closed: no reviewers, no passing reviews, or no covered
    # claims -> no evidence; unattested reviewer lineages collapse so
    # DOUBLE_INDEPENDENT requires genuinely attested distinct families.
    review_evidence = None
    if informal_reviewers and goal_claim_id in graph.claims:
        cone_order = _proposed_dependency_cone(graph, goal_claim_id)
        ledger_rows = [
            {
                "claim_id": cid,
                "dependencies": list(graph.claims[cid].dependencies),
                "canonical_formula": graph.claims[cid].canonical_formula,
            }
            for cid in cone_order
        ]
        reports, review_failures = run_hostile_reviews(
            informal_reviewers, statement=interp.conclusion,
            ledger=ledger_rows, proof_steps=collected_proof_steps,
        )
        failures.extend(review_failures)
        for report in reports:
            memory.problem_local.admit({
                "problem_id": problem_id,
                "stage": "hostile_review",
                "reviewer_id": report.reviewer_id,
                "verdict": report.verdict,
                "material_errors": list(report.material_errors),
                "open_gaps": list(report.open_gaps),
                "cross_problem_usable": False,
            })
            if not report.passing:
                for objection in (*report.material_errors, *report.open_gaps):
                    failures.append(
                        f"hostile_review_objection:{report.reviewer_id}:"
                        f"{objection[:160]}")
        review_evidence = build_informal_review_evidence(
            reports=reports,
            claim_hashes={
                cid: graph.claims[cid].canonical_hash for cid in cone_order
            },
            dependency_order=cone_order,
            intent_certificate_id=(
                intent_cert.certificate_id if intent_cert is not None else None
            ),
        )
        if review_evidence is not None:
            router.admit(attest_evidence(review_evidence), actor=ACTOR)
        phases.append("hostile_review")

    # 15. compile from admitted graph
    compiled = None
    if goal_claim_id in graph.claims:
        compiled = assemble_from_admitted_graph(graph, goal_claim_id)
    phases.append("assemble")
    # A complete dependency audit (the T3 gate input) is mechanical here: the
    # assembled cone closed AND every used claim carries the hostile-review
    # evidence. Never caller-asserted.
    dependency_audit_complete = bool(
        compiled is not None and compiled.complete
        and review_evidence is not None
        and set(compiled.used_claim_ids) <= set(review_evidence.claim_ids)
    )

    # 16. Independent referee + five gates.  The evaluator returns observed
    # attack results; the orchestrator never manufactures all-pass outcomes.
    referee = AdversarialReferee(
        referee_id="referee-1",
        diversity=DiversityProfile(
            (cold_identity.label,),
            ("mechanical-checks-v1",),
            tuple(dict.fromkeys(
                environment
                for report in replay_reports
                for environment in (
                    report.original_environment_hash, report.environment_hash,
                )
                if environment
            )),
        ))
    attack_results = attack_evaluator.evaluate(
        contract=contract, graph=graph, compiled=compiled, packet=packet,
        replay_reports=replay_reports, novelty_verdict=novelty_verdict,
        informal_only=informal_only, intent_cert=intent_cert,
    )
    for attack_result in attack_results:
        referee.run_attack(attack_result)
    discharged = tuple(result.attack for result in attack_results if result.passed)
    residual = tuple(result.attack for result in attack_results if not result.passed)
    referee_result = referee.finalize(discharged=discharged, residual=residual)
    phases.append("referee")

    goal = graph.claims.get(goal_claim_id)
    profile = goal.evidence_profile if goal else None
    gates = None
    certificate = None
    promotion = None
    goal_supported = bool(goal and goal.truth_status.value == "SUPPORTED")
    release_eligible = (
        acquired
        and not release_blocked
        and intent_cert is not None
        and goal_supported
        and bool(compiled and compiled.complete)
        and not referee_result.blocks_release
    )
    if profile is not None and release_eligible and goal is not None \
            and compiled is not None and intent_cert is not None:
        interpretation_hash = interpretation_review_hash(interp)
        informal_claim_hash = sha256_hex(interp.conclusion)
        truth_snapshot = graph.snapshot_claim(goal_claim_id)
        gates = run_five_gates(
            truth_snapshot=truth_snapshot, event_log=log,
            intent_cert=intent_cert,
            correspondence_cert=release_correspondence_cert,
            novelty_verdict=novelty_verdict, informal_only=informal_only,
            responsive=bool(compiled and compiled.complete),
            non_vacuous=_non_vacuous_supported_result(goal),
            expert_reviewed=expert_reviewed_for_run(
                expert_review,
                source_bytes_hash=contract.source_bytes_hash,
                informal_claim_hash=informal_claim_hash,
            ),
            dependency_audit_complete=dependency_audit_complete,
            replay_reports=replay_reports,
            source_bytes_hash=contract.source_bytes_hash,
            interpretation_hash=interpretation_hash,
            informal_claim_hash=informal_claim_hash,
            elaborated_type_hash=(
                release_correspondence_cert.elaborated_type_hash
                if release_correspondence_cert is not None else ""
            ),
        )
        learning_admitted = memory.promote_verified_fact(
            {
                "problem_id": problem_id,
                "claim_id": goal_claim_id,
                "theorem_hash": goal.canonical_hash,
                "scope": goal.scope,
                "kernel_or_certificate_replay": [
                    report.artifact_id for report in replay_reports
                ],
                "dependency_audit": list(referee_result.discharged_obligations),
            },
            truth_snapshot=truth_snapshot, event_log=log, gates=gates,
        )
        if not learning_admitted:
            failures.append("verified_learning_rejected")
        draft = ReleaseCertificate(
            problem_contract_hash=contract.contract_hash(),
            active_interpretation_id=interp.interpretation_id,
            active_interpretation_hash=interpretation_hash,
            result_claim_id=goal_claim_id,
            result_claim_hash=goal.canonical_hash,
            gates=gates,
            proof_bundle_hash=content_id(compiled.to_dict()),
            truth_certificate_ids=tuple(goal.evidence_ids),
            trust_policy_hash=enforcer.policy.policy_hash,
            intent_certificate_id=intent_cert.certificate_id,
            novelty_search_packet_hash=packet.packet_hash(),
            reproducibility_environments=tuple(
                dict.fromkeys(
                    environment
                    for report in replay_reports
                    for environment in (
                        report.original_environment_hash, report.environment_hash,
                    )
                    if environment
                )
            ),
            autonomy={
                "runner_id": runner.runner_id,
                "runner_attested": cold_identity.attested,
                "intervention_counts": {
                    "pre_run": 0, "in_run": 0, "post_run": 0,
                },
                "phase_boundaries": list(phases),
                "model_tool_trace_hash": content_id(runner_responses),
            },
            unresolved_risks=tuple(contract.unresolved_decisions),
        )
        release_kind = _release_kind(gates, informal_only=informal_only)
        promotion = PromotionPolicy().authorize(
            gates, subject_hash=draft.subject_hash, enforcer=enforcer,
            informal_only=informal_only, release_kind=release_kind,
            event_log=log,
        )
        if promotion.promoted:
            certificate = draft.sign(authorization=promotion, event_log=log)

    phases.append("release")

    # Recheck the release boundary immediately before returning.  Gate and
    # certificate signatures are bound to the exact current event-log head; a
    # concurrent append or truth-state change invalidates the would-be release.
    if certificate is not None and (
        graph.claims.get(goal_claim_id) is None
        or graph.claims[goal_claim_id].truth_status.value != "SUPPORTED"
        or gates is None
        or not gates.verify_attestation(event_log=log)
        or not certificate.verify(event_log=log)
    ):
        failures.append("release_invalidated_before_return")
        certificate = None

    outcome = _outcome_label(
        release_blocked=release_blocked, acquired=acquired,
        goal_supported=goal_supported,
        referee_blocks=referee_result.blocks_release, gates=gates,
        promotion=promotion, certificate=certificate,
    )
    final_debt = verified_debt(list(debt_obligations.values()), debt_policy)
    return ResearchResult(
        problem_id=problem_id, contract=contract, graph=graph, phases=phases,
        compiled_proof=compiled, gates=gates, certificate=certificate,
        promotion=promotion, outcome=outcome, acquired=acquired,
        budget=budget_ledger, cold_output=cold_output, packet=packet,
        programs=tuple(programs), blueprint=blueprint,
        replay_reports=tuple(replay_reports), runner_responses=tuple(runner_responses),
        failures=tuple(failures),
        referee_result=referee_result,
        oeis_results=tuple(oeis_results), formal_reports=tuple(formal_reports),
        memory=memory,
        verified_debt={
            "policy_hash": debt_policy.policy_hash(),
            "initial": initial_debt.debt,
            "final": final_debt.debt,
            "open_obligations": final_debt.open_obligations,
        },
    )


def _domain_for_contract(contract: ProblemContract) -> str:
    regime = contract.primary_ir.parameter_regime
    if "natural" in regime or any(b.domain in {"ℕ", "ℤ", "integer", "integers"}
                                   for b in contract.primary_ir.binders):
        return "number_theory"
    return "unknown"


def _authenticate_computation_proposal(
    proposal: dict, *, graph: EpistemicGraph,
    compute_service: ComputeService | None,
    replay_reports: list[ReplayReport],
    intent_cert: IntentCertificate | None,
) -> Evidence | None:
    """Reconstruct trusted evidence from service-owned state, never worker claims.

    A program worker is permitted to *propose* evidence, but cannot authenticate
    it.  The local M1 path accepts only an artifact found in the orchestrator's
    trusted compute service, bound by its immutable ExperimentSpec to the exact
    graph claim, with a measured independent replay matching the stored output.
    """
    if compute_service is None or proposal.get("evidence_kind") != "exact_computation":
        return None
    artifact_id = proposal.get("artifact_id")
    if not isinstance(artifact_id, str):
        return None
    artifact = compute_service.artifacts.get(artifact_id)
    if artifact is None or proposal.get("artifact_hash") != artifact.content_id():
        return None
    claim_ids = proposal.get("claim_ids")
    if not isinstance(claim_ids, list) or not claim_ids \
            or any(claim_id not in graph.claims for claim_id in claim_ids):
        return None
    job = next(
        (
            candidate for candidate in compute_service.jobs.values()
            if candidate.artifact is not None
            and candidate.artifact.artifact_id == artifact.artifact_id
        ),
        None,
    )
    if job is None or not set(claim_ids).issubset(set(job.spec.claim_ids)):
        return None
    if artifact.effective_classification() not in {
        "exhaustive_finite_subcase", "finite_reduction_proof",
        "certificate_checked_lemma",
    } or not isinstance(artifact.output, Mapping) or artifact.output.get("result") is not True:
        return None
    replay = next(
        (
            report for report in replay_reports
            if report.artifact_id == artifact.artifact_id
            and report.replayed
            and report.output_hash_matches
            and report.original_hash == artifact.output_hash
            and report.replay_hash == artifact.output_hash
            and report.original_environment_hash == artifact.environment_hash
            and report.independent_environment
        ),
        None,
    )
    if replay is None:
        return None
    if intent_cert is None or intent_cert.verdict is not Verdict.APPROVED \
            or any(intent_cert.informal_claim_hash != graph.claims[claim_id].canonical_hash
                   for claim_id in claim_ids):
        return None
    classification = validator_classification(artifact.effective_classification())
    evidence = Evidence(
        evidence_id=str(proposal.get("evidence_id", "")),
        claim_ids=list(claim_ids),
        kind=EvidenceKind.EXACT_COMPUTATION,
        assertion_scope=artifact.coverage,
        claim_bindings={claim_id: graph.claims[claim_id].canonical_hash for claim_id in claim_ids},
        artifact_hashes=[artifact.content_id(), artifact.output_hash],
        generator_identity={
            "id": "egmra-compute-service",
            "artifact_id": artifact.artifact_id,
            "spec_hash": artifact.spec_hash,
            "code_hash": artifact.code_hash,
            "findings": {
                "classification": classification,
                "exact_arithmetic": artifact.arithmetic_mode == "exact",
                "coverage_statement": bool(artifact.coverage),
                "result_verified": True,
            },
        },
        verifier_identities=[{
            "id": f"independent-replay:{replay.environment_hash}",
            "attested": True,
        }],
        diversity_profile={
            "original_environment": replay.original_environment_hash,
            "replay_environment": replay.environment_hash,
        },
        environment_hash=replay.environment_hash,
        replay_command=f"ComputeService.replay:{artifact.artifact_id}",
        replay_result="pass",
        intent_certificate_id=intent_cert.certificate_id,
        trust_assumptions=["local M1 compute service and evidence HMAC key isolation"],
    )
    return attest_evidence(evidence)


def _program_fingerprint(
    program: ResearchProgram, *, interpretation_id: str, conclusion: str,
    bottleneck: str, packet: SourcePacket,
) -> MechanismFingerprint:
    return MechanismFingerprint(
        target_interpretation=interpretation_id,
        reformulation=conclusion,
        method_family=program.family,
        central_proposed_lemma=bottleneck or f"advance {program.family}",
        external_theorems=(
            tuple(record.theorem_id for record in packet.theorem_records)
            if program.family == "literature_derived_transfer" else ()
        ),
        computational_signature=(
            "finite exact computation"
            if program.family == "computational_finite_reduction" else ""
        ),
        expected_falsifiers=(program.falsifier,),
        formalization_route=(
            "local Lean" if program.family == "formal_library_first" else ""
        ),
    )


def _build_blueprint(
    goal_claim_id: str, goal_text: str, programs: list[ResearchProgram],
) -> AndOrBlueprint:
    blueprint = AndOrBlueprint(goal_id=goal_claim_id, direct_attempted=False)
    leaves: list[str] = []
    for program in programs:
        leaf_id = f"leaf:{program.family}"
        blueprint.add_node(Node(
            leaf_id, claim=f"{program.family}: {goal_text}", node_type="LEAF",
            semantic_risk=0.0,
        ))
        leaves.append(leaf_id)
    route_id = "routes:" + content_id({"goal": goal_claim_id, "leaves": leaves})[:12]
    blueprint.add_node(Node(route_id, claim="alternative sufficient routes",
                            node_type="OR"))
    for leaf_id in leaves:
        blueprint.add_sufficient_lemma_set([leaf_id], or_parent=route_id)
    blueprint.add_node(Node(goal_claim_id, claim=goal_text, node_type="GOAL",
                            children=[route_id]))
    return blueprint


def _non_vacuous_supported_result(goal) -> bool:
    if goal is None or goal.truth_status.value != "SUPPORTED":
        return False
    profile = goal.evidence_profile
    return any(
        str(value) not in {"NONE", "None", ""}
        for value in (
            profile.exact_computation,
            profile.informal_review,
            profile.formal_verification,
        )
    )


def _release_kind(gates: FiveGateResult, *, informal_only: bool) -> str:
    if gates.truth in {"T1", "T2"}:
        return "scoped_result"
    if gates.truth == "T4":
        return "encoded_theorem"
    return "resolution"


def _outcome_label(
    *, release_blocked: bool, acquired: bool, goal_supported: bool,
    referee_blocks: bool, gates,
    promotion: PromotionDecision | None, certificate: ReleaseCertificate | None,
) -> str:
    if release_blocked or not acquired:
        return "honest_triage_report"
    if not goal_supported:
        return "no_result"
    if referee_blocks:
        return "blocked_by_referee"
    if gates is None:
        return "no_result"
    if certificate is None or promotion is None or not promotion.promoted:
        return "release_blocked_by_policy"
    return gates.summary_label()
