"""Referee attack semantics (R4): kernel-replay discharge for formal-only runs.

`MechanicalAttackEvaluator` must let a *formal* run (``informal_only=False``)
with no finite experiments discharge ``independent_computation`` and
``proof_reconstruction`` through an admitted, kernel-replayed Lean proof bound
to a correspondence certificate — while every informal or failed-replay path
stays fail-closed exactly as before.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from egmra.intake.contract import build_problem_contract
from egmra.orchestrator.loop import MechanicalAttackEvaluator
from egmra.truth.entities import EvidenceKind

STATEMENT = b"Prove that for all natural numbers n, n squared is at least 0."


@pytest.fixture(scope="module")
def contract():
    return build_problem_contract(
        problem_id="attack-semantics-problem",
        source_bytes=STATEMENT,
        source_id="test:attack-semantics",
        predicate=lambda n: n * n >= 0,
    )


def _formal_evidence(
    *,
    valid: bool = True,
    kind=EvidenceKind.LEAN_PROOF,
    correspondence_id: str = "fcc_test",
    replay_result: str = "pass",
    attested: bool = True,
):
    return SimpleNamespace(
        valid=valid,
        kind=kind,
        formal_correspondence_certificate_id=correspondence_id,
        replay_result=replay_result,
        verifier_identities=[{"id": "pinned-kernel", "attested": attested}],
    )


def _finite_replay(*, matches: bool = True, independent: bool = True):
    return SimpleNamespace(
        replayed=True,
        output_hash_matches=matches,
        independent_environment=independent,
    )


def _evaluate(contract, *, evidence=(), replays=(), informal_only, compiled_complete=True):
    graph = SimpleNamespace(
        evidence={f"ev_{i}": item for i, item in enumerate(evidence)}
    )
    compiled = SimpleNamespace(complete=compiled_complete)
    packet = SimpleNamespace(theorem_records=[])
    results = MechanicalAttackEvaluator().evaluate(
        contract=contract,
        graph=graph,
        compiled=compiled,
        packet=packet,
        replay_reports=list(replays),
        novelty_verdict="N1",
        informal_only=informal_only,
        intent_cert=object(),
    )
    return {result.attack: result for result in results}


def test_formal_run_with_kernel_replay_discharges_computation_attacks(contract):
    """A purely formal run with admitted kernel evidence passes both attacks."""
    outcome = _evaluate(
        contract, evidence=[_formal_evidence()], replays=[], informal_only=False,
    )
    assert outcome["independent_computation"].passed
    assert outcome["proof_reconstruction"].passed
    assert outcome["formal_audit"].passed


def test_informal_only_run_without_replays_still_fails(contract):
    """The formal route never applies to an informal-only run (fail-closed).

    ``independent_computation`` passes vacuously (no computational evidence
    exists to replay), but ``proof_reconstruction`` still fails: nothing
    independently re-derived the argument.
    """
    outcome = _evaluate(
        contract, evidence=[_formal_evidence()], replays=[], informal_only=True,
    )
    assert outcome["independent_computation"].passed  # vacuous: nothing to replay
    assert not outcome["proof_reconstruction"].passed
    assert outcome["proof_reconstruction"].defect


def test_formal_run_without_formal_evidence_fails(contract):
    """informal_only=False alone cannot discharge reconstruction/audit."""
    outcome = _evaluate(contract, evidence=[], replays=[], informal_only=False)
    assert not outcome["proof_reconstruction"].passed
    assert not outcome["formal_audit"].passed


@pytest.mark.parametrize("mutation", [
    {"replay_result": "pending"},
    {"replay_result": "fail"},
    {"attested": False},
    {"correspondence_id": ""},
    {"valid": False},
])
def test_weak_formal_evidence_cannot_discharge_reconstruction(contract, mutation):
    """Every required property of the formal route is load-bearing."""
    outcome = _evaluate(
        contract, evidence=[_formal_evidence(**mutation)], replays=[],
        informal_only=False,
    )
    assert not outcome["proof_reconstruction"].passed


def test_unreplayed_exact_computation_evidence_fails_the_attack(contract):
    """Admitted computational evidence with no replay reports is a defect."""
    outcome = _evaluate(
        contract,
        evidence=[_formal_evidence(kind=EvidenceKind.EXACT_COMPUTATION)],
        replays=[], informal_only=True,
    )
    assert not outcome["independent_computation"].passed
    assert outcome["independent_computation"].defect


def test_failed_finite_replays_are_not_masked_by_formal_route(contract):
    """A bad finite replay is a defect; the formal route must not hide it."""
    outcome = _evaluate(
        contract,
        evidence=[_formal_evidence()],
        replays=[_finite_replay(matches=False)],
        informal_only=False,
    )
    assert not outcome["independent_computation"].passed
    assert not outcome["proof_reconstruction"].passed


def test_good_finite_replays_still_discharge_for_informal_runs(contract):
    """The pre-existing finite route is unchanged."""
    outcome = _evaluate(
        contract, evidence=[], replays=[_finite_replay()], informal_only=True,
    )
    assert outcome["independent_computation"].passed
    assert outcome["proof_reconstruction"].passed


def test_incomplete_compilation_blocks_reconstruction_even_with_kernel(contract):
    """proof_reconstruction still requires a complete admitted dependency cone."""
    outcome = _evaluate(
        contract, evidence=[_formal_evidence()], replays=[], informal_only=False,
        compiled_complete=False,
    )
    assert outcome["independent_computation"].passed
    assert not outcome["proof_reconstruction"].passed


def _review_evidence(*, valid=True, artifacts=("a" * 64,)):
    return SimpleNamespace(
        valid=valid,
        kind=EvidenceKind.INFORMAL_REVIEW,
        formal_correspondence_certificate_id="",
        replay_result="not_applicable",
        verifier_identities=[{"id": "rev", "attested": False}],
        artifact_hashes=list(artifacts),
    )


def test_hostile_reconstruction_discharges_proof_reconstruction_only(contract):
    """A hostile-review reconstruction is the §11.2 attack-9 artifact."""
    outcome = _evaluate(
        contract, evidence=[_review_evidence()], replays=[], informal_only=True,
    )
    assert outcome["proof_reconstruction"].passed
    # It never discharges the formal audit for a formal run.
    formal = _evaluate(
        contract, evidence=[_review_evidence()], replays=[], informal_only=False,
    )
    assert not formal["formal_audit"].passed


def test_invalid_or_artifactless_review_does_not_discharge(contract):
    for evidence in (_review_evidence(valid=False), _review_evidence(artifacts=())):
        outcome = _evaluate(
            contract, evidence=[evidence], replays=[], informal_only=True,
        )
        assert not outcome["proof_reconstruction"].passed
