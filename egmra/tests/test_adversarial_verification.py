"""Adversarial tier, referee, and disagreement tests."""

from __future__ import annotations

import pytest

from egmra.truth import EvidenceProfile, FormalVerification
from egmra.verification import (
    REQUIRED_ATTACKS,
    AdversarialReferee,
    AttackResult,
    DiversityProfile,
    ReviewVerdict,
    aggregate,
    truth_level,
)


def _diversity(*, independent: bool = True) -> DiversityProfile:
    if independent:
        return DiversityProfile(("generator-a",), ("checker-b",), ("env-a", "env-b"))
    return DiversityProfile(("same",), ("same",), ("env-a",))


def test_caller_hardened_boolean_cannot_promote_kernel_result_to_t5() -> None:
    profile = EvidenceProfile(formal_verification=FormalVerification.KERNEL_CHECKED)
    assert truth_level(profile, hardened=True) == "T4"


def test_unknown_or_correlated_reviews_cannot_return_promote_ok() -> None:
    unknown = aggregate([
        ReviewVerdict("a", "fam-a", "pass"),
        ReviewVerdict("b", "fam-b", "unknown"),
    ])
    assert unknown.decision != "promote_ok"
    correlated = aggregate([
        ReviewVerdict("a", "same", "pass"),
        ReviewVerdict("b", "same", "pass"),
    ])
    assert correlated.decision != "promote_ok"


def test_duplicate_reviewer_and_invalid_verdict_fail_closed() -> None:
    with pytest.raises(ValueError):
        aggregate([
            ReviewVerdict("a", "fam", "pass"),
            ReviewVerdict("a", "fam", "pass"),
        ])
    with pytest.raises(ValueError):
        ReviewVerdict("a", "fam", "looks_good")


def test_attack_results_cannot_contradict_their_own_verdict() -> None:
    with pytest.raises(ValueError):
        AttackResult("circularity", passed=True, defect="cycle found")
    with pytest.raises(ValueError):
        AttackResult("circularity", passed=False, defect="")


def test_referee_blocks_residual_uncertainty_and_nonindependence() -> None:
    referee = AdversarialReferee(referee_id="r", diversity=_diversity(independent=False))
    for attack in REQUIRED_ATTACKS:
        referee.run_attack(AttackResult(attack, passed=True))
    result = referee.finalize(residual=("semantic correspondence unresolved",))
    assert result.blocks_release


def test_referee_report_is_frozen_and_attacks_cannot_be_duplicated() -> None:
    referee = AdversarialReferee(referee_id="r", diversity=_diversity())
    referee.run_attack(AttackResult("target_diff", passed=True))
    with pytest.raises(ValueError, match="duplicate"):
        referee.run_attack(AttackResult("target_diff", passed=True))
    result = referee.finalize(residual=("incomplete",))
    with pytest.raises(RuntimeError, match="finalized"):
        referee.run_attack(AttackResult("circularity", passed=True))
    assert result.attack_report.results == (AttackResult("target_diff", passed=True),)

