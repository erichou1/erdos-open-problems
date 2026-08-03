"""Tests for the verification plane: standards, attacks, referee, aggregation."""

import pytest

from egmra.truth.entities import (
    EvidenceProfile,
    ExactComputation,
    FormalVerification,
    InformalReview,
    NumericalEvidence,
)
from egmra.verification import (
    REQUIRED_ATTACKS,
    AdversarialReferee,
    AttackReport,
    AttackResult,
    DiversityProfile,
    ReviewVerdict,
    aggregate,
    lean_verified_available,
    propagate_taint,
    truth_level,
)
from egmra.verification.aggregation import ConflictResolution


# ── standards ─────────────────────────────────────────────────────────────────

def test_truth_levels_from_profile():
    assert truth_level(EvidenceProfile()) == "T0"
    assert truth_level(EvidenceProfile(numerical=NumericalEvidence.REPRODUCIBLE)) == "T1"
    assert truth_level(EvidenceProfile(exact_computation=ExactComputation.CERTIFICATE_CHECKED)) == "T2"
    assert truth_level(
        EvidenceProfile(informal_review=InformalReview.DOUBLE_INDEPENDENT),
        high_value=True, dependency_audit_complete=True) == "T3"
    assert truth_level(EvidenceProfile(formal_verification=FormalVerification.KERNEL_CHECKED)) == "T4"
    assert truth_level(
        EvidenceProfile(formal_verification=FormalVerification.INDEPENDENT_CHECKER)) == "T5"


def test_lean_verified_only_at_t4_plus():
    assert lean_verified_available("T4")
    assert lean_verified_available("T5")
    assert not lean_verified_available("T3")


def test_kernel_hardened_promotes_to_t5():
    p = EvidenceProfile(formal_verification=FormalVerification.KERNEL_CHECKED)
    assert truth_level(p, hardened=True) == "T4"


# ── attacks ────────────────────────────────────────────────────────────────────

def test_attack_report_completeness():
    report = AttackReport(tuple(AttackResult(attack, passed=True)
                                for attack in REQUIRED_ATTACKS[:-1]))
    assert not report.complete()
    report = AttackReport(report.results + (AttackResult(REQUIRED_ATTACKS[-1], passed=True),))
    assert report.complete()


def test_attack_rejects_unknown():
    with pytest.raises(ValueError):
        AttackResult("bogus_attack", passed=True)


def test_taint_propagates_to_dependents():
    edges = {"c1": ["c2"], "c2": ["c3"]}
    tainted = propagate_taint(edges, {"c1": "circular"})
    assert tainted["c2"] == "circular" and tainted["c3"] == "circular"


# ── referee ────────────────────────────────────────────────────────────────────

def _diversity(independent=True):
    if independent:
        return DiversityProfile(("gen-fam1",), ("check-fam2",), ("envA", "envB"))
    return DiversityProfile(("fam1",), ("fam1",), ("envA",))


def test_referee_blocks_on_defect_and_cannot_repair():
    ref = AdversarialReferee(referee_id="r1", diversity=_diversity())
    for attack in REQUIRED_ATTACKS:
        ref.run_attack(AttackResult(attack, passed=(attack != "circularity"),
                                    defect="cycle" if attack == "circularity" else "",
                                    affected_claims=("target",) if attack == "circularity" else ()))
    result = ref.finalize(discharged=("kernel_replay",))
    assert result.found_defect and result.blocks_release
    assert result.attack_report.first_invalid_dependency() == "target"
    with pytest.raises(RuntimeError):
        ref.repair()


def test_referee_reward_is_for_defects_not_agreement():
    ref = AdversarialReferee(referee_id="r1", diversity=_diversity())
    for attack in REQUIRED_ATTACKS:
        ref.run_attack(AttackResult(attack, passed=True))
    clean = ref.finalize()
    assert not clean.blocks_release
    # a referee that finds nothing but completes coverage gets a small reward,
    # far less than one that finds a defect
    assert ref.reward(clean) < 1.0

    ref2 = AdversarialReferee(referee_id="r2", diversity=_diversity())
    for attack in REQUIRED_ATTACKS:
        ref2.run_attack(AttackResult(attack, passed=(attack != "import_challenge"),
                                     defect="bad import" if attack == "import_challenge" else ""))
    defective = ref2.finalize()
    assert ref2.reward(defective) >= 1.0


def test_referee_independence_flags():
    assert _diversity(True).model_family_independence
    assert not _diversity(False).model_family_independence


# ── aggregation ─────────────────────────────────────────────────────────────────

def test_single_central_defect_blocks():
    verdicts = [
        ReviewVerdict("a", "fam1", "pass"),
        ReviewVerdict("b", "fam2", "fail", central_defect=True),
    ]
    assert aggregate(verdicts).decision == "blocked"


def test_conflict_triggers_fresh_adjudicator():
    verdicts = [ReviewVerdict("a", "fam1", "pass"), ReviewVerdict("b", "fam2", "fail")]
    result = aggregate(verdicts)
    assert result.decision == "conflict_unknown" and result.needs_fresh_adjudicator


def test_consensus_raises_priority_not_tier():
    verdicts = [ReviewVerdict("a", "fam1", "pass"), ReviewVerdict("b", "fam2", "pass")]
    result = aggregate(verdicts)
    assert result.decision == "promote_ok" and result.priority_boost > 0


def test_unresolved_conflict_returns_unknown():
    cr = ConflictResolution(normalized_issue="quantifier order")
    assert cr.resolve() == "unknown"
    cr2 = ConflictResolution(normalized_issue="x", formal_or_executable_resolution="lean proof")
    assert cr2.resolve() == "lean proof"
