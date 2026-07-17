"""Evidence-gated, multi-stage ranking pipeline for research allocation.

The legacy searcher already builds strong, source-bound problem cards and many
useful descriptive ranking lanes.  What it lacked was a first-class allocation
pipeline: one posterior/cost formula plus a fixed exploitation/exploration splice
made the final queue important but comparatively under-audited.

This module turns allocation into a pure five-stage pipeline:

1. validate every card needed for allocation (fail closed; never silently drop);
2. build a transparent multi-objective scorecard (indices, not truth/probability);
3. route each problem to the capability lane where the current stack has leverage;
4. allocate deterministically with protected exploration plus domain/lane diversity;
5. emit a complete audit artifact with a canonical content hash.

The output is SEARCH GUIDANCE ONLY.  It never changes evidence, truth, gates,
release, or the underlying posteriors.  Prize policy remains an outer hard tier:
every unpaid target precedes every paid target regardless of numeric score.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable

RANKING_PIPELINE_SCHEMA_VERSION = 1
RANKING_PIPELINE_POLICY_VERSION = "egmra-ranking-pipeline-v1"

# Ten-slot repeating allocation schedule.  It reserves 20% for uncertainty-led
# exploration and prevents one capability (usually generic NL proof search) from
# monopolizing all spend. Missing lanes backfill from the best remaining card.
LANE_PATTERN: tuple[str, ...] = (
    "direct_resolution",
    "formal_verification",
    "finite_exact",
    "direct_resolution",
    "protected_exploration",
    "literature_novelty",
    "infrastructure",
    "direct_resolution",
    "statement_repair",
    "protected_exploration",
)

SCORE_WEIGHTS = {
    "resolution": 0.30,
    "partial_progress": 0.20,
    "verification": 0.15,
    "mathematical_value": 0.15,
    "corpus_unlock": 0.10,
    "literature_foothold": 0.10,
    "already_known_risk": 0.15,
    "interpretation_risk": 0.10,
    "machinery_risk": 0.05,
}


class RankingPipelineError(ValueError):
    """A card cannot safely participate in allocation."""


@dataclass(frozen=True)
class RankingPlan:
    """Pure pipeline result consumed by the searcher's record renderer."""

    order: tuple[str, ...]
    decisions: tuple[dict[str, Any], ...]
    audit: dict[str, Any]


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _finite(value: Any, *, label: str, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RankingPipelineError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise RankingPipelineError(f"{label} must be finite")
    if minimum is not None and result < minimum:
        raise RankingPipelineError(f"{label} must be >= {minimum}")
    return result


def _posterior(card: dict[str, Any], key: str) -> tuple[float, float]:
    try:
        summary = card["posterior"][key]
        probability = _finite(
            summary["probability"], label=f"{card.get('problem_id')}.{key}.probability")
        interval = summary["credible_interval_approx"]
        low = _finite(interval[0], label=f"{card.get('problem_id')}.{key}.low")
        high = _finite(interval[1], label=f"{card.get('problem_id')}.{key}.high")
    except (KeyError, IndexError, TypeError) as exc:
        raise RankingPipelineError(
            f"{card.get('problem_id', '?')} lacks posterior {key}"
        ) from exc
    if not (0.0 <= probability <= 1.0 and 0.0 <= low <= high <= 1.0):
        raise RankingPipelineError(
            f"{card.get('problem_id', '?')}.{key} is outside [0,1]"
        )
    return probability, high - low


def _feature(card: dict[str, Any], key: str) -> float:
    try:
        value = card["probe_summary"]["literature_ranking"]["features"].get(key, 0.0)
    except (KeyError, TypeError, AttributeError):
        value = 0.0
    return min(1.0, max(0.0, _finite(
        value, label=f"{card.get('problem_id')}.literature.{key}")))


def _validate_cards(
    cards: Iterable[dict[str, Any]], *, allow_unknown_prize: bool = False,
) -> list[dict[str, Any]]:
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    required_posteriors = (
        "p_verified_novel_resolution",
        "p_verified_partial_progress",
        "p_lean_verified_exact_target",
        "p_finite_computational_resolution",
        "p_high_mathematical_value",
        "p_expected_corpus_wide_unlock",
        "p_correct_but_already_known",
        "p_statement_or_interpretation_failure",
    )
    for position, card in enumerate(cards):
        if not isinstance(card, dict):
            raise RankingPipelineError(f"card {position} is not an object")
        problem_id = str(card.get("problem_id", "")).strip()
        number = card.get("problem_number")
        if not problem_id or isinstance(number, bool) or not isinstance(number, int) \
                or number < 1:
            raise RankingPipelineError(f"card {position} has invalid problem identity")
        if problem_id in seen:
            raise RankingPipelineError(f"duplicate ranking card {problem_id}")
        seen.add(problem_id)
        prize_status = card.get("metadata", {}).get("prize_status")
        allowed_prize_statuses = (
            {"unpaid", "paid", "unknown"}
            if allow_unknown_prize else {"unpaid", "paid"}
        )
        if prize_status not in allowed_prize_statuses:
            raise RankingPipelineError(f"{problem_id} has unknown prize status")
        domain = str(card.get("problem_type", {}).get("primary_domain", "")).strip()
        if not domain:
            raise RankingPipelineError(f"{problem_id} has no primary domain")
        routes = card.get("routes")
        if not isinstance(routes, list) or not routes or not all(
                isinstance(route, str) and route.strip() for route in routes):
            raise RankingPipelineError(f"{problem_id} has no usable research route")
        _finite(
            card.get("cost", {}).get("relative_compute_units"),
            label=f"{problem_id}.relative_compute_units", minimum=1e-9)
        for key in required_posteriors:
            _posterior(card, key)
        validated.append(card)
    return validated


def _scorecard(card: dict[str, Any], prior_rank: int) -> dict[str, Any]:
    problem_id = str(card["problem_id"])
    resolution, uncertainty = _posterior(card, "p_verified_novel_resolution")
    partial, _ = _posterior(card, "p_verified_partial_progress")
    lean, _ = _posterior(card, "p_lean_verified_exact_target")
    finite, _ = _posterior(card, "p_finite_computational_resolution")
    value, _ = _posterior(card, "p_high_mathematical_value")
    unlock, _ = _posterior(card, "p_expected_corpus_wide_unlock")
    known_risk, _ = _posterior(card, "p_correct_but_already_known")
    interpretation_risk, _ = _posterior(
        card, "p_statement_or_interpretation_failure")
    foothold = _feature(card, "foothold")
    reuse = _feature(card, "reuse")
    machinery_risk = _feature(card, "machinery_risk")
    cost = _finite(
        card["cost"]["relative_compute_units"],
        label=f"{problem_id}.relative_compute_units", minimum=1e-9)
    attempts = int(card.get("probe_summary", {}).get(
        "early_research", {}).get("attempts", 0) or 0)
    if attempts < 0:
        raise RankingPipelineError(f"{problem_id}.attempts cannot be negative")
    verification = max(lean, finite)
    numerator = (
        SCORE_WEIGHTS["resolution"] * resolution
        + SCORE_WEIGHTS["partial_progress"] * partial
        + SCORE_WEIGHTS["verification"] * verification
        + SCORE_WEIGHTS["mathematical_value"] * value
        + SCORE_WEIGHTS["corpus_unlock"] * unlock
        + SCORE_WEIGHTS["literature_foothold"] * foothold
        - SCORE_WEIGHTS["already_known_risk"] * known_risk
        - SCORE_WEIGHTS["interpretation_risk"] * interpretation_risk
        - SCORE_WEIGHTS["machinery_risk"] * machinery_risk
    )
    exploitation = numerator / cost
    exploration = uncertainty * max(value, 0.05) / cost / math.sqrt(1 + attempts)
    lane_scores = {
        "direct_resolution": exploitation,
        "formal_verification": (0.70 * lean + 0.20 * partial + 0.10 * reuse) / cost,
        "finite_exact": (0.75 * finite + 0.15 * partial + 0.10 * uncertainty) / cost,
        "literature_novelty": (0.55 * known_risk + 0.30 * foothold
                               + 0.15 * uncertainty) / cost,
        "infrastructure": (0.65 * unlock + 0.25 * reuse + 0.10 * value) / cost,
        "statement_repair": (0.75 * interpretation_risk
                             + 0.25 * uncertainty) / cost,
        "protected_exploration": exploration,
    }
    routes = set(card["routes"])
    # Route compatibility is a measured capability gate, not a truth signal.
    compatible = {
        "direct_resolution": "natural_language_research" in routes,
        "formal_verification": "formal_search" in routes,
        "finite_exact": bool(routes & {"exact_computation", "counterexample_search",
                                         "exact_construction_search"}),
        "literature_novelty": "literature_search" in routes,
        "infrastructure": "shared_infrastructure_search" in routes,
        "statement_repair": bool(routes & {"statement_audit", "human_clarification"}),
        "protected_exploration": True,
    }
    viable = {
        lane: score for lane, score in lane_scores.items()
        if compatible[lane] and lane != "protected_exploration"
    }
    primary_lane = max(
        viable or {"protected_exploration": exploration},
        key=lambda lane: (viable.get(lane, exploration), lane),
    )
    return {
        "problem_id": problem_id,
        "problem_number": int(card["problem_number"]),
        "prior_rank": prior_rank,
        "prize_status": card["metadata"]["prize_status"],
        "domain": str(card["problem_type"]["primary_domain"]),
        "routes": sorted(routes),
        "cost": round(cost, 6),
        "attempts": attempts,
        "metrics": {
            "resolution": round(resolution, 6),
            "partial_progress": round(partial, 6),
            "lean": round(lean, 6),
            "finite_exact": round(finite, 6),
            "mathematical_value": round(value, 6),
            "corpus_unlock": round(unlock, 6),
            "already_known_risk": round(known_risk, 6),
            "interpretation_risk": round(interpretation_risk, 6),
            "uncertainty": round(uncertainty, 6),
            "literature_foothold": round(foothold, 6),
            "literature_reuse": round(reuse, 6),
            "machinery_risk": round(machinery_risk, 6),
        },
        "indices": {
            "exploitation": round(exploitation, 9),
            "exploration": round(exploration, 9),
            **{lane: round(score, 9) for lane, score in lane_scores.items()},
        },
        "compatible_lanes": sorted(lane for lane, ok in compatible.items() if ok),
        "primary_lane": primary_lane,
    }


def _allocate_tier(
    scorecards: list[dict[str, Any]], *, limit: int,
    start_rank: int,
) -> list[dict[str, Any]]:
    remaining = {row["problem_id"]: row for row in scorecards}
    selected: list[dict[str, Any]] = []
    domain_counts: Counter[str] = Counter()
    lane_counts: Counter[str] = Counter()
    slot = 0
    while remaining and len(selected) < limit:
        requested_lane = LANE_PATTERN[slot % len(LANE_PATTERN)]
        slot += 1
        candidates = [
            row for row in remaining.values()
            if requested_lane == "protected_exploration"
            or requested_lane in row["compatible_lanes"]
        ]
        backfilled = False
        if not candidates:
            candidates = list(remaining.values())
            backfilled = True
        score_key = (
            "exploration" if requested_lane == "protected_exploration"
            else requested_lane
        )

        def priority(row: dict[str, Any]) -> tuple[float, int, int]:
            raw = float(row["indices"].get(
                score_key, row["indices"]["exploitation"]))
            diversity_penalty = (
                1.0 + 0.12 * domain_counts[row["domain"]]
                + 0.08 * lane_counts[row["primary_lane"]]
            )
            return (-raw / diversity_penalty, row["prior_rank"], row["problem_number"])

        chosen = min(candidates, key=priority)
        remaining.pop(chosen["problem_id"])
        actual_lane = (
            "protected_exploration"
            if requested_lane == "protected_exploration"
            else chosen["primary_lane"] if backfilled else requested_lane
        )
        domain_counts[chosen["domain"]] += 1
        lane_counts[actual_lane] += 1
        selected.append({
            "allocation_rank": start_rank + len(selected),
            "problem_id": chosen["problem_id"],
            "problem_number": chosen["problem_number"],
            "requested_lane": requested_lane,
            "assigned_lane": actual_lane,
            "allocation_lane": (
                "protected_exploration"
                if actual_lane == "protected_exploration" else "exploitation"
            ),
            "backfilled": backfilled,
            "domain": chosen["domain"],
            "primary_lane": chosen["primary_lane"],
            "priority_index": chosen["indices"].get(
                score_key, chosen["indices"]["exploitation"]),
            "reason": (
                f"ranking pipeline lane={actual_lane}; requested={requested_lane}; "
                f"domain_count_before={domain_counts[chosen['domain']] - 1}; "
                f"prior_rank={chosen['prior_rank']}"
            ),
        })
    return selected


def _stability_metrics(
    prior_order: list[str], allocation_order: list[str], *, top_k: int = 25,
) -> dict[str, Any]:
    """Transparent queue-drift metrics against the input/searcher prior.

    This is an audit signal, never a gate.  Large movement may be intentional
    (new evidence or policy) but should be visible rather than hidden inside a
    new score formula.
    """
    if not prior_order or not allocation_order:
        return {
            "compared": 0,
            "top_k": min(top_k, len(prior_order), len(allocation_order)),
            "top_k_overlap": 0.0,
            "mean_normalized_rank_displacement": 0.0,
        }
    compared_ids = [pid for pid in allocation_order if pid in set(prior_order)]
    prior_rank = {pid: index for index, pid in enumerate(prior_order)}
    new_rank = {pid: index for index, pid in enumerate(allocation_order)}
    denominator = max(1, len(prior_order) - 1)
    displacement = sum(
        abs(prior_rank[pid] - new_rank[pid]) / denominator
        for pid in compared_ids
    ) / max(1, len(compared_ids))
    effective_k = min(top_k, len(prior_order), len(allocation_order))
    overlap = len(
        set(prior_order[:effective_k]) & set(allocation_order[:effective_k])
    ) / max(1, effective_k)
    return {
        "compared": len(compared_ids),
        "top_k": effective_k,
        "top_k_overlap": round(overlap, 6),
        "mean_normalized_rank_displacement": round(displacement, 6),
    }


def build_ranking_plan(
    cards: Iterable[dict[str, Any]], *, limit: int, allocation_ready: bool,
    prior_order: Iterable[str] | None = None,
) -> RankingPlan:
    """Run all ranking stages and return allocation decisions + audit artifact."""
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
        raise RankingPipelineError("ranking limit must be a nonnegative integer")
    # Unknown prize metadata is itself a hard allocation blocker in the
    # searcher.  When allocation is already withheld, still score/audit every
    # card so operators can see what is blocked; never permit those cards into
    # an actual queue.
    validated = _validate_cards(
        cards, allow_unknown_prize=not allocation_ready)
    card_ids = [str(card["problem_id"]) for card in validated]
    if prior_order is None:
        normalized_prior = list(card_ids)
    else:
        requested_prior = [str(problem_id) for problem_id in prior_order]
        if len(requested_prior) != len(set(requested_prior)):
            raise RankingPipelineError("prior allocation order contains duplicates")
        unknown = set(requested_prior) - set(card_ids)
        if unknown:
            raise RankingPipelineError(
                f"prior allocation order contains unknown problems: {sorted(unknown)}")
        normalized_prior = requested_prior + [
            problem_id for problem_id in card_ids
            if problem_id not in set(requested_prior)
        ]
    prior_ranks = {
        problem_id: rank for rank, problem_id in enumerate(normalized_prior)
    }
    scorecards = [
        _scorecard(card, prior_rank=prior_ranks[str(card["problem_id"])])
        for card in validated
    ]
    decisions: list[dict[str, Any]] = []
    if allocation_ready and limit:
        for prize_status in ("unpaid", "paid"):
            tier = [row for row in scorecards if row["prize_status"] == prize_status]
            remaining_limit = limit - len(decisions)
            if remaining_limit <= 0:
                break
            decisions.extend(_allocate_tier(
                tier, limit=min(remaining_limit, len(tier)),
                start_rank=len(decisions) + 1,
            ))
    stage_records = [
        {"stage": "validate", "status": "passed", "input_cards": len(validated),
         "rejected_cards": 0},
        {"stage": "score", "status": "passed", "scorecards": len(scorecards),
         "weights": dict(SCORE_WEIGHTS)},
        {"stage": "route", "status": "passed", "lane_counts": dict(sorted(
            Counter(row["primary_lane"] for row in scorecards).items()))},
        {"stage": "allocate", "status": "passed" if allocation_ready else "withheld",
         "selected": len(decisions), "requested_limit": limit,
         "lane_pattern": list(LANE_PATTERN)},
        {"stage": "audit", "status": "passed", "deterministic": True,
         "truth_authority": False},
    ]
    audit = {
        "schema_version": RANKING_PIPELINE_SCHEMA_VERSION,
        "policy_version": RANKING_PIPELINE_POLICY_VERSION,
        "purpose": "search-order allocation only; never truth or release authority",
        "allocation_ready": bool(allocation_ready),
        "input_count": len(validated),
        "selected_count": len(decisions),
        "stages": stage_records,
        "scorecards": scorecards,
        "allocation_decisions": decisions,
        "stability_vs_input_order": _stability_metrics(
            normalized_prior,
            [str(row["problem_id"]) for row in decisions],
        ),
    }
    audit["content_sha256"] = _digest(audit)
    return RankingPlan(
        order=tuple(row["problem_id"] for row in decisions),
        decisions=tuple(decisions),
        audit=audit,
    )
