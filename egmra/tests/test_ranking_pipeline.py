"""Five-stage ranking-pipeline invariants."""

from __future__ import annotations

import copy

import pytest

from egmra.ranking_pipeline import (
    LANE_PATTERN,
    RankingPipelineError,
    build_ranking_plan,
)
from tests.test_searcher_safety import base_card


def _card(
    number: int, *, prize_status: str = "unpaid", domain: str = "graph_theory",
    routes: tuple[str, ...] = ("natural_language_research",),
    resolution: float = 0.2, partial: float = 0.2, lean: float = 0.1,
    finite: float = 0.1, value: float = 0.3, unlock: float = 0.1,
    known: float = 0.05, interpretation: float = 0.05,
    attempts: int = 0,
) -> dict:
    card = copy.deepcopy(base_card())
    card["problem_id"] = f"erdos-{number}"
    card["problem_number"] = number
    card["metadata"]["prize_status"] = prize_status
    card["metadata"]["prize"] = "no" if prize_status == "unpaid" else "$500"
    card["problem_type"]["primary_domain"] = domain
    card["routes"] = list(routes)
    card["cost"]["relative_compute_units"] = 1.0
    card["probe_summary"]["early_research"]["attempts"] = attempts
    card["posterior"] = {}
    values = {
        "p_verified_novel_resolution": resolution,
        "p_verified_partial_progress": partial,
        "p_lean_verified_exact_target": lean,
        "p_finite_computational_resolution": finite,
        "p_high_mathematical_value": value,
        "p_expected_corpus_wide_unlock": unlock,
        "p_correct_but_already_known": known,
        "p_statement_or_interpretation_failure": interpretation,
    }
    for key, probability in values.items():
        card["posterior"][key] = {
            "probability": probability,
            "credible_interval_approx": [max(0.0, probability - 0.1),
                                         min(1.0, probability + 0.1)],
            "alpha": 1.0, "beta": 1.0,
        }
    card["probe_summary"]["literature_ranking"] = {
        "coverage_status": "partial",
        "features": {"foothold": 0.2, "reuse": 0.1,
                     "machinery_risk": 0.0, "status_risk": 0.0},
    }
    return card


def test_pipeline_is_deterministic_and_hash_bound():
    cards = [_card(i, resolution=0.1 + i / 100) for i in range(1, 9)]
    first = build_ranking_plan(cards, limit=8, allocation_ready=True)
    second = build_ranking_plan(copy.deepcopy(cards), limit=8, allocation_ready=True)
    assert first == second
    assert len(first.audit["content_sha256"]) == 64
    assert [stage["stage"] for stage in first.audit["stages"]] == [
        "validate", "score", "route", "allocate", "audit"]
    assert first.audit["purpose"].startswith("search-order")
    stability = first.audit["stability_vs_input_order"]
    assert stability["compared"] == 8
    assert 0.0 <= stability["top_k_overlap"] <= 1.0
    assert 0.0 <= stability["mean_normalized_rank_displacement"] <= 1.0


def test_explicit_prior_order_is_tie_break_and_stability_baseline():
    cards = [_card(1), _card(2), _card(3)]
    prior = ["erdos-3", "erdos-2", "erdos-1"]
    plan = build_ranking_plan(
        cards, limit=3, allocation_ready=True, prior_order=prior)
    scorecards = {row["problem_id"]: row for row in plan.audit["scorecards"]}
    assert scorecards["erdos-3"]["prior_rank"] == 0
    assert scorecards["erdos-1"]["prior_rank"] == 2
    assert plan.audit["stability_vs_input_order"]["compared"] == 3


def test_prior_order_fails_closed_on_duplicates_or_unknown_ids():
    cards = [_card(1), _card(2)]
    with pytest.raises(RankingPipelineError, match="duplicates"):
        build_ranking_plan(
            cards, limit=2, allocation_ready=True,
            prior_order=["erdos-1", "erdos-1"])
    with pytest.raises(RankingPipelineError, match="unknown problems"):
        build_ranking_plan(
            cards, limit=2, allocation_ready=True,
            prior_order=["erdos-1", "erdos-999"])


def test_every_unpaid_problem_precedes_paid_regardless_of_score():
    cards = [
        _card(1, prize_status="unpaid", resolution=0.01),
        _card(2, prize_status="unpaid", resolution=0.02),
        _card(3, prize_status="paid", resolution=0.99),
    ]
    plan = build_ranking_plan(cards, limit=3, allocation_ready=True)
    by_id = {card["problem_id"]: card for card in cards}
    statuses = [by_id[pid]["metadata"]["prize_status"] for pid in plan.order]
    assert statuses == ["unpaid", "unpaid", "paid"]


def test_pipeline_routes_to_capability_lanes_and_protects_exploration():
    cards = [
        _card(1, routes=("formal_search", "natural_language_research"), lean=0.95),
        _card(2, routes=("exact_computation",), finite=0.95),
        _card(3, routes=("literature_search",), known=0.8),
        _card(4, routes=("shared_infrastructure_search",), unlock=0.9),
        _card(5, routes=("statement_audit", "human_clarification"),
              interpretation=0.9),
        _card(6), _card(7), _card(8), _card(9), _card(10),
    ]
    plan = build_ranking_plan(cards, limit=10, allocation_ready=True)
    scorecards = {row["problem_id"]: row for row in plan.audit["scorecards"]}
    assert scorecards["erdos-1"]["primary_lane"] == "formal_verification"
    assert scorecards["erdos-2"]["primary_lane"] == "finite_exact"
    assert scorecards["erdos-3"]["primary_lane"] == "literature_novelty"
    assert scorecards["erdos-4"]["primary_lane"] == "infrastructure"
    assert scorecards["erdos-5"]["primary_lane"] == "statement_repair"
    assert sum(d["allocation_lane"] == "protected_exploration"
               for d in plan.decisions) == LANE_PATTERN.count("protected_exploration")


def test_diversity_penalty_prevents_one_domain_from_monopolizing_top_slots():
    cards = [
        _card(1, domain="graph", resolution=0.8),
        _card(2, domain="graph", resolution=0.79),
        _card(3, domain="number_theory", resolution=0.78),
        _card(4, domain="geometry", resolution=0.77),
    ]
    plan = build_ranking_plan(cards, limit=4, allocation_ready=True)
    first_three_domains = [d["domain"] for d in plan.decisions[:3]]
    assert len(set(first_three_domains)) >= 2


def test_withheld_allocation_still_emits_scored_audit():
    cards = [_card(1), _card(2)]
    plan = build_ranking_plan(cards, limit=2, allocation_ready=False)
    assert plan.order == () and plan.decisions == ()
    assert plan.audit["selected_count"] == 0
    assert plan.audit["stages"][3]["status"] == "withheld"
    assert len(plan.audit["scorecards"]) == 2


def test_unknown_prize_is_audited_when_withheld_but_never_allocated():
    card = _card(1)
    card["metadata"]["prize_status"] = "unknown"
    withheld = build_ranking_plan([card], limit=1, allocation_ready=False)
    assert withheld.order == ()
    assert withheld.audit["scorecards"][0]["prize_status"] == "unknown"
    with pytest.raises(RankingPipelineError):
        build_ranking_plan([card], limit=1, allocation_ready=True)


@pytest.mark.parametrize("mutate", [
    lambda card: card.update(problem_id=""),
    lambda card: card["routes"].clear(),
    lambda card: card["metadata"].update(prize_status="unknown"),
    lambda card: card["cost"].update(relative_compute_units=float("nan")),
    lambda card: card["posterior"].pop("p_verified_novel_resolution"),
])
def test_malformed_card_fails_closed(mutate):
    card = _card(1)
    mutate(card)
    with pytest.raises(RankingPipelineError):
        build_ranking_plan([card], limit=1, allocation_ready=True)
