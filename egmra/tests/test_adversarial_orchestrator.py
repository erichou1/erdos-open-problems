"""Independent production-path tests for orchestration fail-closed behavior."""

from __future__ import annotations

import base64
import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from egmra.agents.runner import DeterministicRunner
from egmra.compute.spec import ExperimentSpec
from egmra.control.leases import LeaseManager
from egmra.corpus.status import StatusClaim
from egmra.intake import build_problem_contract
from egmra.intake.review import interpretation_review_hash, sign_intent_certificate
from egmra.learning import LongTermMemory
from egmra.lean import (
    AttestedKernelRunner,
    LeanService,
    sign_formal_correspondence_certificate,
)
from egmra.oeis import OEISClient
from egmra.orchestrator import DeterministicWorker, WorkerOutput, research
from egmra.policy import PolicyEnforcer, sign_policy
from egmra.provenance.hashing import content_id, sha256_bytes, sha256_hex
from egmra.retrieval.records import TheoremRecord
from egmra.release.certificate import ReleaseSecurityError
from egmra.verification.attacks import AttackResult, REQUIRED_ATTACKS
from egmra.truth.events import EventLog
from egmra.truth.graph import EpistemicGraph
from egmra.truth.entities import (
    EvidenceKind,
    FormalCorrespondenceCertificate,
    IntentCertificate,
    Verdict,
)


POLICY_ENV = {"EGMRA_POLICY_KEY": "orchestrator-test-policy-key-32-bytes"}


def _enforcer(*, promotion: bool = False) -> PolicyEnforcer:
    policy = sign_policy(
        {
            "claim_graph": True,
            "literature_retrieval": True,
            "computation_service": True,
            "promotion": promotion,
            "formal_promotion": False,
        },
        env=POLICY_ENV,
    )
    return PolicyEnforcer(policy, verification_env=POLICY_ENV)


def _corpus() -> list[TheoremRecord]:
    return [
        TheoremRecord(
            theorem_id="source-1",
            canonical_statement="squares are nonnegative",
            conclusion="n squared is nonnegative",
            source_uri="local://fixture",
            source_version="1",
            source_content_hash="fixture-hash",
            verbatim_theorem_and_hypothesis_extract="For every natural n, n^2 >= 0.",
        )
    ]


def _current_status(problem_id: str) -> list[StatusClaim]:
    return [StatusClaim(
        problem_id=problem_id, status="open", source="local://fixture-status",
        review_date="2026-07-13", source_independence="test-fixture",
    )]


def _intent_review(
    problem_id: str, source: bytes, *, source_id: str = "fixture", predicate,
) -> IntentCertificate:
    contract = build_problem_contract(
        problem_id=problem_id, source_bytes=source, source_id=source_id,
        predicate=predicate,
    )
    interp = contract.lattice.nodes[0]
    return sign_intent_certificate(IntentCertificate(
        certificate_id=f"intent-{problem_id}",
        source_bytes_hash=contract.source_bytes_hash,
        interpretation_hash=interpretation_review_hash(interp),
        informal_claim_hash=sha256_hex(interp.conclusion),
        methods=[
            "independent_parse", "examples", "anti_examples",
            "paraphrase", "local_mutation",
        ],
        reviewer_ids=["semantic-reviewer"],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "semantic-reviewer",
            "independent_from": ["governor", "intake_retrieval"],
            "conflicts": [],
        }],
        verdict=Verdict.APPROVED,
    ))


@dataclass
class RecordingWorker:
    cold_budgets: list[float] = field(default_factory=list)
    branch_budgets: list[float] = field(default_factory=list)
    packet_queries: list[str] = field(default_factory=list)
    slice_packet_hashes: list[str] = field(default_factory=list)
    fencing_tokens: list[int] = field(default_factory=list)
    branch_ids: list[str] = field(default_factory=list)

    def cold_pass(self, contract, *, budget: float) -> WorkerOutput:
        self.cold_budgets.append(budget)
        return WorkerOutput(
            falsifiers=["try n=0"],
            search_queries=["cold-pass-square-invariant"],
            bottleneck="finite verification",
        )

    def work_branch(
        self, contract, packet, *, branch_id: str, budget: float, fencing_token: int,
        branch_slice,
    ) -> WorkerOutput:
        self.branch_budgets.append(budget)
        self.fencing_tokens.append(fencing_token)
        self.branch_ids.append(branch_id)
        self.slice_packet_hashes.append(branch_slice.packet_hash)
        with pytest.raises(TypeError):
            branch_slice.packet["forged"] = True
        self.packet_queries.extend(event.query_text for event in packet.query_log)
        return WorkerOutput()


def test_runner_cold_pass_and_budget_are_consumed_by_production_flow(tmp_path):
    worker = RecordingWorker()
    runner = DeterministicRunner()
    source = b"Prove that for all natural numbers n, n squared is at least 0."
    event_path = tmp_path / "events.jsonl"

    result = research(
        problem_id="budgeted", source_bytes=source,
        source_id="fixture", budget=20.0, enforcer=_enforcer(), worker=worker,
        goal_claim_id="goal", events_path=event_path,
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("budgeted"), runner=runner, max_iterations=2,
    )

    assert worker.cold_budgets == [pytest.approx(1.0)]
    assert sum(worker.branch_budgets) <= 19.0
    assert "cold-pass-square-invariant" in " ".join(worker.packet_queries)
    stages = {call["stage"] for call in runner.calls}
    assert "cold_pass" in stages          # legacy identity probe (no worker identity)
    # R1: the ignored branch-selection model call was removed outright —
    # selection is the numeric controller's decision.
    assert "branch_selection" not in stages
    assert worker.fencing_tokens and all(token > 0 for token in worker.fencing_tokens)
    assert worker.branch_ids[0] == "direct_structural"
    fingerprints = [
        branch.mechanism_fingerprint["fingerprint_hash"]
        for branch in result.graph.branches.values()
    ]
    assert len(fingerprints) == len(set(fingerprints)) == len(result.programs)
    assert {"AND", "OR", "GOAL", "LEAF"}.issubset({
        node.node_type for node in result.blueprint.nodes.values()
    })
    assert len(result.verified_debt["policy_hash"]) == 64
    assert result.verified_debt["final"] <= result.verified_debt["initial"]
    replayed = EpistemicGraph(EventLog(event_path, run_id="budgeted"))
    frozen_source = replayed.problems["budgeted"].source_versions[0]
    assert base64.b64decode(frozen_source["bytes_b64"]) == source
    assert replayed.problems["budgeted"].status_claims[0]["source"] == "local://fixture-status"
    assert worker.slice_packet_hashes == [content_id(result.packet.to_dict())] * len(
        worker.branch_budgets
    )
    assert result.budget.spent <= result.budget.total


@dataclass
class CyclicProposalWorker:
    def cold_pass(self, contract, *, budget: float) -> WorkerOutput:
        return WorkerOutput(bottleneck="dependency validation")

    def work_branch(self, contract, packet, *, branch_id: str, budget: float,
                    fencing_token: int, branch_slice) -> WorkerOutput:
        return WorkerOutput(claim_proposals=[
            {"claim_id": "goal", "canonical_formula": contract.primary_ir.conclusion,
             "informal_text": contract.primary_ir.conclusion, "dependencies": []},
            {"claim_id": "lemma-a", "canonical_formula": "A", "informal_text": "A",
             "dependencies": ["lemma-b"]},
            {"claim_id": "lemma-b", "canonical_formula": "B", "informal_text": "B",
             "dependencies": ["lemma-a"]},
        ])


def test_circular_claim_proposal_batch_is_rejected_without_crashing_run(tmp_path):
    source = b"Prove that for all natural numbers n, n squared is at least 0."
    result = research(
        problem_id="cyclic-proposals", source_bytes=source, source_id="fixture",
        budget=20.0, enforcer=_enforcer(), worker=CyclicProposalWorker(),
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("cyclic-proposals"), max_iterations=1,
    )

    assert "goal" in result.graph.claims
    assert "lemma-a" not in result.graph.claims
    assert "lemma-b" not in result.graph.claims
    assert any(failure.startswith("claim_dependency_cycle_or_unknown:")
               for failure in result.failures)
    assert result.certificate is None


@dataclass
class CrashingWorker:
    def cold_pass(self, contract, *, budget: float) -> WorkerOutput:
        return WorkerOutput(bottleneck="crash recovery")

    def work_branch(self, contract, packet, *, branch_id: str, budget: float,
                    fencing_token: int, branch_slice) -> WorkerOutput:
        raise RuntimeError("simulated worker process died")


def test_worker_crash_is_recorded_and_other_branches_remain_schedulable(tmp_path):
    result = research(
        problem_id="worker-crash",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(), worker=CrashingWorker(),
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("worker-crash"), max_iterations=3,
    )

    crashes = [failure for failure in result.failures if failure.startswith("worker_crashed:")]
    assert len(crashes) >= 2
    assert any("direct_structural" in failure for failure in crashes)
    assert result.certificate is None
    assert result.outcome in {"no_result", "honest_triage_report"}


@dataclass
class MalformedArtifactWorker:
    def cold_pass(self, contract, *, budget: float) -> WorkerOutput:
        return WorkerOutput(bottleneck="artifact validation")

    def work_branch(self, contract, packet, *, branch_id: str, budget: float,
                    fencing_token: int, branch_slice) -> WorkerOutput:
        return WorkerOutput(
            claim_proposals=[{
                "claim_id": "goal", "canonical_formula": contract.primary_ir.conclusion,
                "informal_text": contract.primary_ir.conclusion, "dependencies": [],
            }],
            evidence=[{"kind": "exact_computation"}, "not-an-object"],
            formal_candidates=[{"claim_id": "goal"}, "not-an-object"],
        )


def test_malformed_evidence_and_formal_artifacts_are_quarantined(tmp_path):
    result = research(
        problem_id="malformed-artifacts",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(),
        worker=MalformedArtifactWorker(), goal_claim_id="goal",
        events_path=tmp_path / "events.jsonl", retrieval_corpus=_corpus(),
        probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("malformed-artifacts"), max_iterations=1,
    )

    assert not result.graph.evidence
    assert result.certificate is None
    assert any(f.startswith("evidence_proposal_malformed:") for f in result.failures)
    assert any(f.startswith("formal_candidate_malformed:") for f in result.failures)


def test_non_positive_budget_is_rejected_before_worker_execution(tmp_path):
    worker = RecordingWorker()

    with pytest.raises(ValueError, match="budget must be positive"):
        research(
            problem_id="zero", source_bytes=b"Prove True.", source_id="fixture",
            budget=0.0, enforcer=_enforcer(), worker=worker, goal_claim_id="goal",
            events_path=tmp_path / "events.jsonl", retrieval_corpus=_corpus(),
        )

    assert worker.cold_budgets == []
    assert worker.branch_budgets == []


def test_malformed_empty_statement_is_not_acquired_or_sent_to_deep_work(tmp_path):
    worker = RecordingWorker()

    result = research(
        problem_id="empty", source_bytes=b"", source_id="fixture", budget=20.0,
        enforcer=_enforcer(), worker=worker, goal_claim_id="goal",
        events_path=tmp_path / "events.jsonl", retrieval_corpus=_corpus(),
    )

    assert not result.acquired
    assert worker.branch_budgets == []
    assert result.certificate is None
    assert result.outcome == "honest_triage_report"


@dataclass
class ExpiringWorker:
    """Return forged success only after deliberately losing the branch lease."""

    lease_manager: LeaseManager
    clock: list[float]

    def cold_pass(self, contract, *, budget: float) -> WorkerOutput:
        return WorkerOutput(bottleneck="force a stale-worker race")

    def work_branch(
        self, contract, packet, *, branch_id: str, budget: float, fencing_token: int,
        branch_slice,
    ) -> WorkerOutput:
        self.clock[0] += 61.0
        replacement = self.lease_manager.transfer_if_expired(
            branch_id=branch_id,
            new_holder="replacement:worker",
            run_contract_id=contract.contract_hash(),
        )
        assert replacement is not None
        assert replacement.fencing_token > fencing_token
        return WorkerOutput(
            claim_proposals=[{
                "claim_id": "goal",
                "canonical_formula": "forged stale result",
                "informal_text": "forged stale result",
                "dependencies": [],
                "scope": "finite_domain",
            }],
            evidence=[{
                "evidence_id": "stale-forgery",
                "claim_ids": ["goal"],
                "kind": "exact_computation",
                "replay_result": "pass",
                "findings": {
                    "classification": "exhaustive_finite_subcase",
                    "exact_arithmetic": True,
                    "coverage_statement": True,
                    "predicate_result": True,
                },
                "environment_hash": "forged",
            }],
        )


def test_stale_fencing_token_rejects_worker_output_before_evidence_admission(tmp_path):
    clock = [100.0]
    leases = LeaseManager(now_fn=lambda: clock[0])
    worker = ExpiringWorker(lease_manager=leases, clock=clock)

    result = research(
        problem_id="stale-worker",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(), worker=worker,
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("stale-worker"), lease_manager=leases,
        max_iterations=1,
    )

    assert "goal" not in result.graph.claims
    assert "stale-forgery" not in result.graph.evidence
    assert result.certificate is None
    assert any(failure.startswith("stale_worker_rejected:") for failure in result.failures)


@dataclass
class ForgingWorker:
    def cold_pass(self, contract, *, budget: float) -> WorkerOutput:
        return WorkerOutput(bottleneck="forge evidence")

    def work_branch(
        self, contract, packet, *, branch_id: str, budget: float, fencing_token: int,
        branch_slice,
    ) -> WorkerOutput:
        digest = "a" * 64
        return WorkerOutput(
            claim_proposals=[{
                "claim_id": "goal", "canonical_formula": "attacker-chosen claim",
                "informal_text": "attacker-chosen claim", "dependencies": [],
                "scope": "finite_domain",
            }],
            evidence=[{
                "evidence_id": "forged-evidence", "claim_ids": ["goal"],
                "kind": "exact_computation", "replay_result": "pass",
                "assertion_scope": "everything", "artifact_hashes": [digest],
                "environment_hash": digest, "replay_command": "pretend replay",
                "verifier_identities": [{"id": "attacker", "attested": True}],
                "findings": {
                    "classification": "exhaustive_finite", "exact_arithmetic": True,
                    "coverage_statement": True, "result_verified": True,
                },
            }],
        )


def test_untrusted_worker_cannot_forge_computation_evidence(tmp_path):
    result = research(
        problem_id="forged-worker",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(), worker=ForgingWorker(),
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("forged-worker"), max_iterations=1,
    )

    assert "forged-evidence" not in result.graph.evidence
    assert result.graph.claims["goal"].truth_status.value == "UNKNOWN"
    assert any(failure.startswith("untrusted_evidence_proposal:") for failure in result.failures)


def test_computation_without_locked_claim_binding_is_quarantined(tmp_path):
    worker = DeterministicWorker(
        goal_claim_id="goal", goal_formula="unbound candidate", goal_scope="finite_domain",
        experiment_code=TRUE_EXPERIMENT,
        experiment_spec=ExperimentSpec(
            purpose="missing claim binding", inputs={"n": 4}, arithmetic_mode="exact",
            coverage="exhaustive 0..n",
        ),
    )

    result = research(
        problem_id="unbound-computation",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(), worker=worker,
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("unbound-computation"), max_iterations=1,
    )

    assert result.graph.claims["goal"].truth_status.value == "UNKNOWN"
    assert not result.graph.evidence
    assert any("claim binding" in failure for failure in result.failures)


@dataclass
class SequenceWorker(RecordingWorker):
    def work_branch(
        self, contract, packet, *, branch_id: str, budget: float, fencing_token: int,
        branch_slice,
    ) -> WorkerOutput:
        super().work_branch(
            contract, packet, branch_id=branch_id, budget=budget,
            fencing_token=fencing_token, branch_slice=branch_slice,
        )
        return WorkerOutput(generated_sequences=[[1, 1, 2, 3, 5, 8]])


def test_generated_sequence_reaches_read_only_oeis_without_becoming_truth(tmp_path):
    requested: list[str] = []

    def fetch(url: str) -> str:
        requested.append(url)
        return '{"results":[{"number":45,"data":"1,1,2,3,5,8"}]}'

    result = research(
        problem_id="oeis-routing",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(), worker=SequenceWorker(),
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("oeis-routing"), max_iterations=1,
        oeis_client=OEISClient(fetcher=fetch, offline=False, min_interval_s=0),
    )

    assert requested and "q=1%2C1%2C2%2C3%2C5%2C8" in requested[0]
    assert result.oeis_results[0]["entry_count"] == 1
    assert not result.graph.evidence


def test_cold_and_branch_learning_is_quarantined_problem_local(tmp_path):
    memory = LongTermMemory()

    result = research(
        problem_id="memory-routing",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(), worker=RecordingWorker(),
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("memory-routing"), max_iterations=1,
        memory=memory,
    )

    assert result.memory is memory
    assert memory.problem_local.records
    assert not memory.verified_semantic.records


@dataclass
class FormalCandidateWorker(RecordingWorker):
    def work_branch(
        self, contract, packet, *, branch_id: str, budget: float, fencing_token: int,
        branch_slice,
    ) -> WorkerOutput:
        super().work_branch(
            contract, packet, branch_id=branch_id, budget=budget,
            fencing_token=fencing_token, branch_slice=branch_slice,
        )
        return WorkerOutput(
            claim_proposals=[{
                "claim_id": "goal", "canonical_formula": "True",
                "informal_text": "True", "dependencies": [], "scope": "general",
            }],
            formal_candidates=[{
                "claim_id": "goal",
                "source": "theorem candidate : True := trivial",
                "declaration_name": "candidate",
                "expected_type_hash": sha256_hex("True"),
                "immutable_target_module_hash": sha256_hex("locked target module"),
                "lean_version": "4.9.0",
                "mathlib_commit": "pinned-test-commit",
                "project_hash": sha256_hex("test project"),
            }],
        )


def test_formal_candidate_reaches_lean_but_static_or_mock_result_cannot_promote(tmp_path):
    result = research(
        problem_id="formal-routing",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(),
        worker=FormalCandidateWorker(), goal_claim_id="goal",
        events_path=tmp_path / "events.jsonl", retrieval_corpus=_corpus(),
        probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("formal-routing"), max_iterations=1,
        lean_service=LeanService(kernel_runner=lambda **_kwargs: "COMPLETE"),
        informal_only=False,
    )

    assert result.formal_reports
    assert result.formal_reports[0]["passed"] is False
    assert result.graph.claims["goal"].truth_status.value == "UNKNOWN"
    assert result.certificate is None
    assert any("formal_verification_failed" in failure for failure in result.failures)


class FailingLeanService:
    def create_environment(self, **_kwargs):
        raise RuntimeError("simulated unavailable Lean worker")


def test_formal_verifier_failure_is_recorded_without_aborting_research(tmp_path):
    result = research(
        problem_id="formal-service-failure",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(),
        worker=FormalCandidateWorker(), goal_claim_id="goal",
        events_path=tmp_path / "events.jsonl", retrieval_corpus=_corpus(),
        probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("formal-service-failure"), max_iterations=1,
        lean_service=FailingLeanService(), informal_only=False,
    )

    assert result.certificate is None
    assert not result.formal_reports
    assert any(f.startswith("formal_verification_error:") for f in result.failures)


def test_authenticated_formal_envelope_is_carried_into_truth_evidence(
    tmp_path, monkeypatch,
):
    executable = Path("/usr/bin/true")
    runner = AttestedKernelRunner(
        command=(str(executable),), checker_id="lean4checker",
        checker_version="pinned", checker_binary_hash=sha256_bytes(executable.read_bytes()),
        checker_trust_base="lean-kernel", env=dict(os.environ),
    )

    def complete_checker(command, **kwargs):
        request = json.loads(kwargs["input"])
        return subprocess.CompletedProcess(
            command, 0, stdout=json.dumps({
                "kernel_verified": True,
                "candidate_type_hash": request["expected_type_hash"],
                "candidate_declaration_hash": sha256_hex("declaration"),
                "proof_term_hash": sha256_hex("proof-term"),
                "source_tree_hash": sha256_hex("tree"),
                "imports_hash": sha256_hex("imports"),
                "transitive_axioms": [], "placeholder_findings": [],
                "unsafe_findings": [], "imports_audited": True,
                "axiom_closure_verified": True, "immutable_target_isolated": True,
                "clean_replay": True, "network_disabled": True,
            }), stderr="",
        )

    monkeypatch.setattr("egmra.lean.service.subprocess.run", complete_checker)
    source = b"Prove that for all natural numbers n, n squared is at least 0."
    intent = _intent_review(
        "formal-envelope", source, predicate=lambda n: n * n >= 0,
    )
    correspondence = sign_formal_correspondence_certificate(
        FormalCorrespondenceCertificate(
            certificate_id="formal-correspondence-goal",
            intent_certificate_id=intent.certificate_id,
            informal_claim_hash=intent.informal_claim_hash,
            lean_declaration_name="candidate",
            elaborated_type_hash=sha256_hex("True"),
            notation_and_definition_map_hash=sha256_hex("notation-map"),
            methods=[
                "backtranslation", "examples", "anti_examples",
                "paraphrase", "local_mutation",
            ],
            reviewer_ids=["formal-correspondence-reviewer"],
            reviewer_independence_and_conflicts=[{
                "reviewer_id": "formal-correspondence-reviewer",
                "independent_from": ["formalization_authority", "governor"],
                "conflicts": [],
            }],
            verdict=Verdict.APPROVED,
        )
    )

    result = research(
        problem_id="formal-envelope", source_bytes=source, source_id="fixture",
        budget=20.0, enforcer=_enforcer(), worker=FormalCandidateWorker(),
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("formal-envelope"), max_iterations=1,
        lean_service=LeanService(kernel_runner=runner), informal_only=False,
        intent_review=intent,
        formal_correspondence_reviews={"goal": correspondence},
    )

    formal_evidence = [
        evidence for evidence in result.graph.evidence.values()
        if evidence.kind is EvidenceKind.LEAN_PROOF
    ]
    assert len(formal_evidence) == 1
    evidence = formal_evidence[0]
    assert evidence.generator_identity["formal_certificate"]["passed"] is True
    assert evidence.generator_identity["source_hash"] in evidence.artifact_hashes
    assert evidence.formal_correspondence_certificate_id == correspondence.certificate_id
    assert result.graph.claims["goal"].truth_status.value == "SUPPORTED"


FALSE_EXPERIMENT = """
def experiment(inputs):
    return {"result": False, "coverage": "exhaustive 0..n"}
"""


def test_false_computation_cannot_support_or_release_a_claim(tmp_path):
    worker = DeterministicWorker(
        goal_claim_id="goal",
        goal_formula="the deliberately false candidate",
        goal_scope="finite_domain",
        experiment_code=FALSE_EXPERIMENT,
        experiment_spec=ExperimentSpec(
            purpose="negative regression", inputs={"n": 4}, arithmetic_mode="exact",
            coverage="exhaustive 0..n", claim_ids=("goal",),
        ),
    )

    result = research(
        problem_id="false-output",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(), worker=worker,
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("false-output"),
    )

    assert result.graph.claims["goal"].truth_status.value != "SUPPORTED"
    assert result.certificate is None
    assert result.outcome in {"honest_no_result", "no_result"}


TRUE_EXPERIMENT = """
def experiment(inputs):
    n = inputs["n"]
    return {"result": all(k * k >= 0 for k in range(n + 1)),
            "coverage": "exhaustive 0..n"}
"""


def test_research_cannot_self_issue_semantic_intent_approval(tmp_path):
    worker = DeterministicWorker(
        goal_claim_id="goal", goal_formula="all checked squares are nonnegative",
        goal_scope="finite_domain", experiment_code=TRUE_EXPERIMENT,
        experiment_spec=ExperimentSpec(
            purpose="intent separation", inputs={"n": 8}, arithmetic_mode="exact",
            coverage="exhaustive 0..n", claim_ids=("goal",),
        ),
    )

    result = research(
        problem_id="no-intent-review",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(promotion=True), worker=worker,
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("no-intent-review"),
    )

    assert result.graph.claims["goal"].truth_status.value == "UNKNOWN"
    assert result.graph.intent_certificates == {}
    assert "intent_review_unavailable" in result.failures
    assert result.gates is None
    assert result.certificate is None


def test_computation_replay_report_reaches_reproducibility_gate(tmp_path):
    worker = DeterministicWorker(
        goal_claim_id="goal", goal_formula="all checked squares are nonnegative",
        goal_scope="finite_domain", experiment_code=TRUE_EXPERIMENT,
        experiment_spec=ExperimentSpec(
            purpose="positive regression", inputs={"n": 8}, arithmetic_mode="exact",
            coverage="exhaustive 0..n", claim_ids=("goal",),
        ),
    )

    result = research(
        problem_id="replay",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(), worker=worker,
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("replay"),
        intent_review=_intent_review(
            "replay",
            b"Prove that for all natural numbers n, n squared is at least 0.",
            predicate=lambda n: n * n >= 0,
        ),
    )

    assert result.replay_reports
    assert all(report.replayed and report.output_hash_matches for report in result.replay_reports)
    assert result.gates is not None
    assert result.gates.reproducibility != "R0"


def test_promoted_scoped_result_has_current_verifiable_release_certificate(tmp_path):
    worker = DeterministicWorker(
        goal_claim_id="goal", goal_formula="all checked squares are nonnegative",
        goal_scope="finite_domain", experiment_code=TRUE_EXPERIMENT,
        experiment_spec=ExperimentSpec(
            purpose="promoted scoped regression", inputs={"n": 8},
            arithmetic_mode="exact", coverage="exhaustive 0..n",
            claim_ids=("goal",),
        ),
    )

    result = research(
        problem_id="promoted-replay",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(promotion=True), worker=worker,
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("promoted-replay"),
        intent_review=_intent_review(
            "promoted-replay",
            b"Prove that for all natural numbers n, n squared is at least 0.",
            predicate=lambda n: n * n >= 0,
        ),
    )

    assert result.certificate is not None
    assert result.certificate.verify(event_log=result.graph.log)
    assert result.verified_debt["final"] == 0
    assert len(result.memory.verified_semantic.records) == 1
    assert result.memory.verified_semantic.records[0]["authenticated"] is True
    assert result.outcome == "verified_finite_or_conditional_result"
    # A promoted T2 finite/scoped result is reproducible evidence, not a proof
    # of the universal informal theorem.
    assert result.render()["proof_complete"] is False

    branch_id = next(iter(result.graph.branches))
    result.graph.set_branch_status(
        branch_id, "paused", reason="post-release state changed",
        actor={"type": "agent", "id": "test-auditor"},
    )
    assert not result.certificate.verify(event_log=result.graph.log)
    with pytest.raises(ReleaseSecurityError):
        result.render()


def test_unresolved_interpretation_blocks_certificate_even_with_support(tmp_path):
    worker = DeterministicWorker(
        goal_claim_id="goal", goal_formula="ambiguous target", goal_scope="finite_domain",
        experiment_code=TRUE_EXPERIMENT,
        experiment_spec=ExperimentSpec(
            purpose="blocked target", inputs={"n": 8}, arithmetic_mode="exact",
            coverage="exhaustive 0..n", claim_ids=("goal",),
        ),
    )

    result = research(
        problem_id="ambiguous-supported",
        source_bytes=(b"Prove that for all natural numbers n, n squared is at least 0, "
                      b"where equality holds at zero."),
        source_id="fixture", budget=20.0, enforcer=_enforcer(), worker=worker,
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("ambiguous-supported"),
    )

    assert result.contract.release_blocked
    assert result.certificate is None
    assert result.gates is None
    assert result.outcome == "honest_triage_report"
    assert result.render()["proof_complete"] is False


@dataclass
class RejectingAttackEvaluator:
    calls: int = 0

    def evaluate(self, **context) -> list[AttackResult]:
        self.calls += 1
        return [
            AttackResult(
                attack,
                passed=attack != "dependency_trace",
                defect="independently reproduced dependency defect"
                if attack == "dependency_trace" else "",
            )
            for attack in REQUIRED_ATTACKS
        ]


def test_independent_referee_defect_blocks_release(tmp_path):
    evaluator = RejectingAttackEvaluator()
    worker = DeterministicWorker(
        goal_claim_id="goal", goal_formula="all checked squares are nonnegative",
        goal_scope="finite_domain", experiment_code=TRUE_EXPERIMENT,
        experiment_spec=ExperimentSpec(
            purpose="referee regression", inputs={"n": 8}, arithmetic_mode="exact",
            coverage="exhaustive 0..n", claim_ids=("goal",),
        ),
    )

    result = research(
        problem_id="referee-defect",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(), worker=worker,
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("referee-defect"), attack_evaluator=evaluator,
        intent_review=_intent_review(
            "referee-defect",
            b"Prove that for all natural numbers n, n squared is at least 0.",
            predicate=lambda n: n * n >= 0,
        ),
    )

    assert evaluator.calls == 1
    assert result.referee_result is not None
    assert result.referee_result.blocks_release
    assert result.certificate is None
    assert result.outcome == "blocked_by_referee"


@dataclass
class IncompleteAttackEvaluator:
    def evaluate(self, **context) -> list[AttackResult]:
        return [AttackResult("target_diff", passed=True)]


def test_missing_referee_attacks_fail_closed(tmp_path):
    result = research(
        problem_id="missing-attacks",
        source_bytes=b"Prove that for all natural numbers n, n squared is at least 0.",
        source_id="fixture", budget=20.0, enforcer=_enforcer(),
        worker=DeterministicWorker(goal_claim_id="goal", goal_formula="candidate"),
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("missing-attacks"),
        attack_evaluator=IncompleteAttackEvaluator(),
    )

    assert result.referee_result is not None
    assert result.referee_result.blocks_release
    assert result.certificate is None
