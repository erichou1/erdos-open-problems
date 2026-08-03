"""Adversarial validation and hard-constraint tests for problem selection."""

from __future__ import annotations

import math

import pytest

from egmra.selection import (
    AcquisitionWeights,
    CompetingRiskPosterior,
    ProblemFeatures,
    ProblemSelector,
    acquisition_score,
)


@pytest.mark.parametrize(
    "features",
    [
        ProblemFeatures("p", source_access_authorized=False),
        ProblemFeatures("p", license_compatible=False),
        ProblemFeatures("p", statement_well_formed=False),
        ProblemFeatures("p", false_promotion_risk_acceptable=False),
        ProblemFeatures("p", provable_duplicate=True),
    ],
)
def test_all_specified_hard_constraints_are_enforced(features: ProblemFeatures) -> None:
    ok, reason = ProblemSelector().hard_constraints_ok(features)
    assert not ok and reason


@pytest.mark.parametrize(
    "kwargs",
    [
        {"expected_cost": 0},
        {"mathlib_coverage": 1.1},
        {"reuse_probability": -0.1},
        {"formal_clarity": math.nan},
        {"prior_attempts": -1},
    ],
)
def test_invalid_feature_ranges_fail_closed(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        ProblemFeatures("p", **kwargs)


def test_malformed_posterior_and_observations_fail_closed() -> None:
    with pytest.raises(ValueError):
        CompetingRiskPosterior(alpha={"novel_full": 1.0})
    posterior = CompetingRiskPosterior()
    with pytest.raises(ValueError):
        posterior.observe("novel_full", censored="yes")
    with pytest.raises(ValueError):
        posterior.expected_value({"novel_full": math.nan})


def test_selector_rejects_duplicate_ids_and_invalid_k() -> None:
    selector = ProblemSelector()
    duplicate = [
        (ProblemFeatures("p"), CompetingRiskPosterior()),
        (ProblemFeatures("p"), CompetingRiskPosterior()),
    ]
    with pytest.raises(ValueError, match="duplicate"):
        selector.select(duplicate, k=1)
    with pytest.raises(ValueError):
        selector.select([], k=0)


def test_acquisition_weights_and_inputs_are_numerically_validated() -> None:
    with pytest.raises(ValueError):
        AcquisitionWeights(cost_exponent=1.1)
    with pytest.raises(ValueError):
        acquisition_score(
            ProblemFeatures("p"), CompetingRiskPosterior(), expected_information_gain=-1
        )

