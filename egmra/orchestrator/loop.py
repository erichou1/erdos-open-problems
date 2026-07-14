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
from dataclasses import dataclass, field, replace
from pathlib import Path
import sys
from typing import Any, Callable, Protocol

from egmra.agents import AuthorityTokenIssuer
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
from egmra.oeis import OEISClient, OEISUnavailable
from egmra.policy import PolicyEnforcer
from egmra.provenance.hashing import canonical_json, content_id, is_sha256, sha256_hex
from egmra.release.certificate import ReleaseCertificate
from egmra.release.compiler import CompiledProof, assemble_from_admitted_graph
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
from egmra.truth.blackboard import Blackboard, ReadSlice
from egmra.truth.events import EventLog
from egmra.truth.graph import EpistemicGraph
from egmra.truth.router import EvidenceRouter
from egmra.truth.validators import attest_evidence
from egmra.verification.attacks import AttackResult, REQUIRED_ATTACKS
from egmra.verification.referee import AdversarialReferee, DiversityProfile, RefereeResult

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

        replay_ok = bool(replay_reports) and all(
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
                replay_ok,
                "no matching computation replay report reached the referee",
            ),
            "formal_audit": (
                informal_only,
                "formal result has no local kernel/formal audit artifact",
            ),
            "proof_reconstruction": (
                bool(compiled and compiled.complete and replay_ok),
                "candidate could not be reconstructed from admitted claims and replay",
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
        failures.append(f"computation job {job} failed")
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
            # Candidate assembly is not a released proof.  The public boolean is
            # true only when a release certificate exists for that candidate.
            "proof_complete": bool(
                self.certificate and self.compiled_proof and self.compiled_proof.complete
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
# target directly, the experimentalist drives finite computation, and the
# formalizer works library/lemma-first. The role shapes the model prompt and is
# recorded in each branch's mechanism fingerprint, so allocation is role-aware.
WORKER_ROLE_BY_FAMILY = {
    "direct_structural": "prover",
    "computational_finite_reduction": "experimentalist",
    "formal_library_first": "formalizer",
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
    seen_exchanges: set[tuple] = set()
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
    if intent_review is None:
        failures.append("intent_review_unavailable")
    elif (
        not release_blocked
        and intent_review.verdict is Verdict.APPROVED
        and intent_review.source_bytes_hash == contract.source_bytes_hash
        and intent_review.interpretation_hash == expected_interpretation_hash
        and intent_review.informal_claim_hash == expected_claim_hash
        and review_methods.issubset(set(intent_review.methods))
        and verify_intent_certificate(intent_review)
    ):
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
    runner_cold = runner.run(
        f"Blindly list falsifiers and retrieval queries for: {interp.conclusion}",
        stage="cold_pass",
    )
    runner_responses.append({
        "stage": "cold_pass", "text": runner_cold.text,
        "runner_id": runner.runner_id, "prompt_hash": runner_cold.prompt_hash,
        "model_attested": runner_cold.model.attested,
    })
    cold_output = worker.cold_pass(contract, budget=cold_budget)
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

    # 7. frozen solver packet (literature) — mandatory before deep proof work
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
            runner_cold.text,
        ])),
    ))
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
        max_programs=max(1, min(max_iterations, 3)) if max_iterations else 1,
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
        runner_branch = runner.run(
            "Select among branch mechanisms: " + ", ".join(bid for bid, _ in candidates),
            stage="branch_selection",
        )
        runner_responses.append({
            "stage": "branch_selection", "text": runner_branch.text,
            "runner_id": runner.runner_id, "prompt_hash": runner_branch.prompt_hash,
            "model_attested": runner_branch.model.attested,
        })
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
            run_contract_id=contract.contract_hash(), grace_seconds=60.0,
        )
        worker_token = authority_issuer.issue(
            authority_name="program_worker",
            subject=f"worker:{branch_id}",
            resources=(f"branch:{branch_id}", f"packet:{board_packet_hash}"),
            lineage=runner_cold.model.label,
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
        finally:
            try:
                leases.release(
                    branch_id, lease.holder, fencing_token=lease.fencing_token,
                )
            except LeaseError:
                # A replacement worker now owns the branch.  Its lease is not
                # ours to release, and the stale output above has been dropped.
                pass
        replay_reports.extend(output.replay_reports)
        failures.extend(output.failures)
        memory.problem_local.admit({
            "problem_id": problem_id,
            "stage": "branch",
            "branch_id": branch_id,
            "role": branch_role,
            "failures": list(output.failures),
            "falsifiers": list(output.falsifiers),
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
        for prop in output.claim_proposals:
            accepted = blackboard.write_proposal({
                **prop, "kind": "claim_proposal", "branch_id": branch_id,
            }, token=worker_token)
            if accepted["claim_id"] not in graph.claims:
                # The locked target text, not worker-selected prose, is the
                # canonical goal formula.  Workers may propose subsidiary
                # claims, but cannot silently substitute the research target.
                canonical_formula = (
                    interp.conclusion
                    if accepted["claim_id"] == goal_claim_id
                    else accepted["canonical_formula"]
                )
                graph.propose_claim(
                    claim_id=accepted["claim_id"], interpretation_id=interp.interpretation_id,
                    canonical_formula=canonical_formula,
                    informal_text=(interp.conclusion if accepted["claim_id"] == goal_claim_id
                                   else accepted.get("informal_text", "")),
                    dependencies=accepted.get("dependencies", []),
                    scope=accepted.get("scope", "general"), actor=ACTOR)
                if accepted["claim_id"] == goal_claim_id and intent_cert is not None:
                    graph.bind_intent_certificate(
                        goal_claim_id, intent_cert.certificate_id, actor=ACTOR,
                    )
        for ev in output.evidence:
            accepted = blackboard.write_proposal({
                **ev, "evidence_kind": ev.get("kind", ""),
                "kind": "evidence_proposal", "branch_id": branch_id,
            }, token=worker_token)
            if accepted["evidence_id"] in graph.evidence:
                continue
            evidence = _authenticate_computation_proposal(
                accepted, graph=graph, compute_service=trusted_compute_service,
                replay_reports=output.replay_reports, intent_cert=intent_cert,
            )
            if evidence is None:
                failures.append(f"untrusted_evidence_proposal:{accepted['evidence_id']}")
                continue
            enforcer.require("computation_service", entry_point="orchestrator.compute")
            router.admit(evidence, actor=ACTOR)
        for candidate in output.formal_candidates:
            formal_token = authority_issuer.issue(
                authority_name="formalization_authority",
                subject=f"formalizer:{branch_id}",
                resources=(f"branch:{branch_id}", f"packet:{board_packet_hash}"),
                lineage="lean-service",
            )
            accepted = blackboard.write_proposal({
                **candidate, "kind": "formal_artifact", "branch_id": branch_id,
            }, token=formal_token)
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
            environment = lean_service.create_environment(
                lean_version=accepted["lean_version"],
                mathlib_commit=accepted["mathlib_commit"],
                project_hash=accepted["project_hash"],
                trust_policy=accepted.get("trust_policy", "classical-whitelist"),
                imports=tuple(accepted.get("imports", ())),
                options=dict(accepted.get("options", {})),
            )
            formal_certificate = lean_service.verify_declaration(
                environment=environment,
                source=accepted["source"],
                declaration_name=accepted["declaration_name"],
                expected_type_hash=accepted["expected_type_hash"],
                immutable_target_module_hash=accepted["immutable_target_module_hash"],
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
            formal_reports.append({
                "branch_id": branch_id,
                "claim_id": accepted["claim_id"],
                **formal_certificate.to_dict(),
            })
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
            branch_id, success=supported, debt_reduction=debt_reduction,
        )
        leaf = blueprint.nodes.get(f"leaf:{branch_id}")
        if leaf is not None:
            leaf.closed = supported
        if branch_id == "direct_structural":
            blueprint.direct_attempted = True
        if supported:
            break

    # Durable, content-addressed model-exchange artifacts + signed events (4.10).
    if artifact_store is not None:
        _record_model_exchanges(log, artifact_store, problem_id,
                                runners=(runner, getattr(worker, "runner", None)))
        phases.append("record_exchanges")

    # 15. compile from admitted graph
    compiled = None
    if goal_claim_id in graph.claims:
        compiled = assemble_from_admitted_graph(graph, goal_claim_id)
    phases.append("assemble")

    # 16. Independent referee + five gates.  The evaluator returns observed
    # attack results; the orchestrator never manufactures all-pass outcomes.
    referee = AdversarialReferee(
        referee_id="referee-1",
        diversity=DiversityProfile(
            (runner_cold.model.label,),
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
                "runner_attested": runner_cold.model.attested,
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
