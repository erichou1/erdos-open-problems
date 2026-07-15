"""Continuous outcome-driven reranking of the campaign queue (R11 closing).

The searcher's ranking is a static snapshot: campaigns drained it in frozen
order no matter what the live outcomes showed.  This module closes the loop —
observed outcomes (the calibration data) mechanically adjust the *pending*
order while a campaign runs, so budget flows toward problems showing genuine
progress and away from dead ends.

Honesty invariants:

* the adjustment is a **search-order preference only** — it never touches
  truth, evidence, gates, or release, and it never *removes* a problem
  (exclusion stays the searcher's job);
* rules are mechanical and recorded per problem (every move carries its
  reason), the function is pure and deterministic, and the searcher's prior
  order is the tie-break — no hidden scoring;
* demotions react to *observed* dead-ends (repeated interpretation blocks,
  repeated failures); promotions react to *observed* progress (salvaged
  supported claims, computational evidence, complete assembly).  A problem
  with no outcomes keeps exactly its searcher rank.
"""

from __future__ import annotations

from typing import Any

# Observed states that indicate the problem cannot progress without a human
# artifact or upstream fix — repeated occurrences push it to the back.
_DEAD_END_STATES = {"BLOCKED_BY_INTERPRETATION", "MALFORMED_STATEMENT"}
# Observed states that indicate genuine forward motion.
_PROGRESS_STATES = {
    "COMPUTATIONAL_EVIDENCE", "CANDIDATE_SOLUTION", "CANDIDATE_DISPROOF",
    "VERIFIED_CANDIDATE", "FORMALLY_VERIFIED_CANDIDATE",
}


def _score(problem_id: str, outcomes: dict[str, list[dict]]) -> tuple[int, list[str]]:
    """Mechanical adjustment score (positive = promote) with recorded reasons."""
    rows = outcomes.get(problem_id, [])
    if not rows:
        return 0, []
    score = 0
    reasons: list[str] = []
    states = [str(r.get("public_state", "")) for r in rows]
    dead_ends = sum(1 for s in states if s in _DEAD_END_STATES)
    if dead_ends >= 2:
        score -= 2
        reasons.append(f"repeated_dead_end:{dead_ends}x_interpretation_blocked")
    failures = sum(
        1 for r in rows
        if str(r.get("public_state", "")) not in _PROGRESS_STATES
        and not r.get("released")
    )
    if failures >= 3:
        score -= 1
        reasons.append(f"no_progress_in_{failures}_attempts")
    progressed = [s for s in states if s in _PROGRESS_STATES]
    if progressed:
        score += 2
        reasons.append(f"observed_progress:{progressed[-1]}")
    salvaged = sum(
        len((r.get("salvage") or {}).get("supported", [])) for r in rows
    )
    if salvaged:
        score += 1
        reasons.append(f"salvaged_supported_claims:{salvaged}")
    if any(r.get("candidate_assembly_complete") for r in rows):
        score += 1
        reasons.append("candidate_assembly_complete_observed")
    return score, reasons


def rerank_pending(
    base_order: list[str], outcome_rows: list[dict[str, Any]],
) -> tuple[list[str], dict[str, list[str]]]:
    """Adjust a pending queue by observed outcomes; stable on the searcher prior.

    Returns ``(new_order, reasons_by_problem)``.  Sorting is by descending
    adjustment score with the ORIGINAL searcher rank as tie-break, so problems
    without outcomes keep their exact relative order.  Pure and deterministic.
    """
    outcomes: dict[str, list[dict]] = {}
    for row in outcome_rows:
        if isinstance(row, dict) and row.get("problem_id"):
            outcomes.setdefault(str(row["problem_id"]), []).append(row)
    scored: list[tuple[int, int, str]] = []
    reasons_by_problem: dict[str, list[str]] = {}
    for rank, problem_id in enumerate(base_order):
        score, reasons = _score(problem_id, outcomes)
        if reasons:
            reasons_by_problem[problem_id] = reasons
        scored.append((-score, rank, problem_id))
    scored.sort()
    return [problem_id for _, _, problem_id in scored], reasons_by_problem
