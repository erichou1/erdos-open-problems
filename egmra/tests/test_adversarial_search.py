"""Independent numerical, budget, graph, and failure tests for the search plane."""

from __future__ import annotations

import math

import pytest

from egmra.search import (
    ActionComponents,
    AndOrBlueprint,
    BranchPosterior,
    Controller,
    DebtPolicy,
    MechanismFingerprint,
    Node,
    Obligation,
    QualityDiversityArchive,
    UtilityWeights,
    branch_action_utility,
    credit_for_action,
    verified_debt,
)
from egmra.search.blueprint import BlueprintError


def _fingerprint(*, falsifier: str) -> MechanismFingerprint:
    return MechanismFingerprint(
        target_interpretation="i",
        reformulation="R",
        method_family="direct_structural",
        central_proposed_lemma="L",
        expected_falsifiers=(falsifier,),
    )


def test_additive_utility_matches_independent_arithmetic() -> None:
    components = ActionComponents(
        expected_outcome_value=3.0,
        info_gain=2.0,
        unlock=4.0,
        reuse=6.0,
        diversity=8.0,
        falsification_value=10.0,
        expected_cost=5.0,
        duplicate=7.0,
        semantic_risk=9.0,
    )
    weights = UtilityWeights(
        info_gain=0.5, unlock=0.25, reuse=0.2, diversity=0.1,
        falsification=0.3, duplicate=0.4, semantic_risk=0.6,
    )
    expected = 3 + .5 * 2 + .25 * 4 + .2 * 6 + .1 * 8 + .3 * 10 - 5 - .4 * 7 - .6 * 9
    assert branch_action_utility(components, weights) == round(expected, 6)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_nonfinite_utility_inputs_fail_closed(value: float) -> None:
    with pytest.raises(ValueError):
        ActionComponents(expected_outcome_value=value)
    with pytest.raises(ValueError):
        UtilityWeights(info_gain=value)


def test_controller_tracks_real_branch_spend_and_never_exceeds_global_budget() -> None:
    controller = Controller(global_budget=10, max_branch_fraction=.4)
    controller.register(BranchPosterior("b"))
    assert controller.allocate("b", 3, verified_debt_reduction=0, info_gain=0)
    assert not controller.allocate("b", 2, verified_debt_reduction=0, info_gain=0)
    assert controller.allocate("b", 2, verified_debt_reduction=1, info_gain=0)
    assert controller.branch_spend["b"] == 5
    assert controller.allocate("b", 5, verified_debt_reduction=1, info_gain=0)
    assert not controller.allocate("b", .01, verified_debt_reduction=10, info_gain=10)
    assert controller.spent == 10


def test_negative_or_unknown_allocations_and_duplicate_registration_are_rejected() -> None:
    controller = Controller(global_budget=10)
    controller.register(BranchPosterior("b"))
    with pytest.raises(ValueError):
        controller.allocate("b", -1, verified_debt_reduction=0, info_gain=0)
    with pytest.raises(KeyError):
        controller.allocate("missing", 1, verified_debt_reduction=0, info_gain=0)
    with pytest.raises(ValueError, match="duplicate"):
        controller.register(BranchPosterior("b"))


def test_rate_limit_update_is_censored_and_does_not_change_math_posterior() -> None:
    controller = Controller(global_budget=10)
    posterior = BranchPosterior("b", alpha=2, beta=3)
    controller.register(posterior)
    controller.update_posterior("b", success=False, censored_reason="rate_limit")
    assert (posterior.alpha, posterior.beta) == (2, 3)
    assert controller.governor_events[-1]["classification"] == "censored_operational_event"


def test_protected_exploration_lane_prefers_protected_candidate() -> None:
    controller = Controller(global_budget=10, protected_fraction=.25, seed=4)
    for index in range(5):
        controller.register(
            BranchPosterior(f"b{index}", attempts=100 if index == 4 else index,
                            protected=index == 4)
        )
    candidates = [
        (f"b{index}", ActionComponents(expected_outcome_value=10 - index))
        for index in range(5)
    ]
    assert "b4" in controller.select_posterior_actions(candidates, k=4)


def test_mechanism_fingerprint_commits_expected_falsifiers_and_quality_is_finite() -> None:
    assert _fingerprint(falsifier="small case").fingerprint_hash() != _fingerprint(
        falsifier="large countermodel"
    ).fingerprint_hash()
    archive = QualityDiversityArchive()
    with pytest.raises(ValueError):
        archive.consider(_fingerprint(falsifier="x"), quality=math.nan, branch_id="b")


def test_verified_debt_rejects_negative_gaming_and_disappearing_obligations() -> None:
    with pytest.raises(ValueError):
        verified_debt([Obligation("o", False, risk=-1, cost=1)], DebtPolicy())
    before = [Obligation("target", False, risk=1, cost=1)]
    with pytest.raises(ValueError, match="disappeared"):
        credit_for_action(before, [], DebtPolicy())


def test_blueprint_cycle_is_rejected_instead_of_recursing_forever() -> None:
    blueprint = AndOrBlueprint(goal_id="goal")
    blueprint.add_node(Node("leaf", "L", "LEAF"))
    blueprint.add_node(Node("goal", "G", "AND", children=["leaf"]))
    blueprint.nodes["leaf"].node_type = "AND"
    blueprint.nodes["leaf"].children = ["goal"]
    with pytest.raises(BlueprintError, match="cycle"):
        blueprint.is_closed()

