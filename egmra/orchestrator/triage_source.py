"""Triage-ranked problem source for the EGMRA continuous drainer (single-pipeline).

The legacy ``run_continuous.py`` pulled the next highest-ranked unclaimed problem
from the searcher rankings and drove the *legacy* ``ProofPipeline``.  This module
lets ``egmra campaign`` drain the same triage rankings through the **EGMRA**
research loop instead, so one pipeline covers both the deep reasoning and the
verified release.

It only *reads* the rankings the searcher already produced
(``triage/rankings/<lane>.json`` or ``current.json``); it never re-ranks and
never fabricates a probability.  Selection is honest metadata:

* ``attempt_exclusions`` recorded by the searcher are skipped;
* the allocation queue is used only when ``allocation_status == "ready"`` (the
  searcher withholds it until it has a complete exact-recorded context);
* ordering is the ranking's own order (allocation rank / lane rank), truncated
  to ``limit``.
"""

from __future__ import annotations

import json
from pathlib import Path

# Ranking files whose entries carry an ordered ``problem_number``.  ``current``
# maps to the interleaved allocation queue (exploitation + protected
# exploration); the others are the searcher's single-objective lanes, including
# the T2-closable finite-computation lane (see ``build_t2_lane.py``).
_ALLOCATION_LANE = "current"
_MAX_RANKING_BYTES = 64_000_000
_RANKING_LANES = (
    "current",
    "highest_probability_verified_novel_solution",
    "highest_probability_verified_partial_progress",
    "highest_probability_lean_verification",
    "best_finite_computation_targets",
    "tractable_frontier",
    "highest_expected_corpus_wide_unlock",
    "highest_mathematical_value_targets",
    "highest_reusable_formal_infrastructure_value",
    "t2_closable",
)


class TriageSourceError(RuntimeError):
    """The triage rankings are missing, malformed, or not ready to drain."""


def available_lanes() -> tuple[str, ...]:
    return _RANKING_LANES


def _read_json(path: Path) -> object:
    if path.is_symlink() or not path.is_file():
        raise TriageSourceError(f"triage ranking is not a regular file: {path}")
    if path.stat().st_size > _MAX_RANKING_BYTES:
        raise TriageSourceError(f"triage ranking is implausibly large: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise TriageSourceError(f"cannot read triage ranking {path}: {exc}") from exc


def _entries_for_lane(document: object, lane: str) -> list[dict]:
    """Return the ordered ranking rows for ``lane`` from a rankings document."""
    if lane == "t2_closable":
        if not isinstance(document, dict) or not isinstance(document.get("problems"), list):
            raise TriageSourceError("t2_closable ranking has no 'problems' list")
        return [row for row in document["problems"] if isinstance(row, dict)]
    if not isinstance(document, dict):
        raise TriageSourceError("ranking document is not a JSON object")
    if lane == _ALLOCATION_LANE:
        if document.get("allocation_status") != "ready":
            raise TriageSourceError(
                "allocation queue is not ready "
                f"({document.get('allocation_status')!r}); the searcher withholds "
                "it until a complete exact-recorded context exists"
            )
        rows = document.get("allocation_queue")
    else:
        rows = document.get(lane)
    if not isinstance(rows, list):
        raise TriageSourceError(f"ranking lane {lane!r} is missing or not a list")
    return [row for row in rows if isinstance(row, dict)]


def _problem_number(row: dict) -> int | None:
    value = row.get("problem_number")
    if value is None and isinstance(row.get("problem"), int):
        value = row["problem"]
    if value is None and isinstance(row.get("problem_id"), str):
        _, _, tail = row["problem_id"].partition("-")
        value = tail
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 1 else None


def triage_ranked_problem_ids(
    triage_dir: Path, *, lane: str = _ALLOCATION_LANE, limit: int | None = None,
) -> list[str]:
    """Ordered ``erdos-<n>`` ids from a triage ranking lane, exclusions removed.

    ``limit`` caps the number returned (``None`` = all).  The order is the
    ranking's own order; duplicates and searcher ``attempt_exclusions`` are
    dropped.  Raises :class:`TriageSourceError` if the lane is unknown, missing,
    malformed, or (for the allocation queue) not yet ready.
    """
    if lane not in _RANKING_LANES:
        raise TriageSourceError(
            f"unknown triage lane {lane!r}; choose one of {', '.join(_RANKING_LANES)}"
        )
    triage_dir = Path(triage_dir)
    rankings_dir = triage_dir / "rankings" if (triage_dir / "rankings").is_dir() else triage_dir
    document = _read_json(rankings_dir / f"{lane}.json")

    exclusions: set[int] = set()
    if lane != "t2_closable":
        # The allocation-context rankings record the searcher's exclusions; reuse
        # them so a problem the searcher retired is never drained.
        current = document if lane == _ALLOCATION_LANE else _read_json(
            rankings_dir / f"{_ALLOCATION_LANE}.json") if (
                rankings_dir / f"{_ALLOCATION_LANE}.json").is_file() else {}
        if isinstance(current, dict):
            exclusions = {
                int(n) for n in current.get("attempt_exclusions", [])
                if isinstance(n, int)
            }

    ordered: list[str] = []
    seen: set[int] = set()
    for row in _entries_for_lane(document, lane):
        number = _problem_number(row)
        if number is None or number in seen or number in exclusions:
            continue
        seen.add(number)
        ordered.append(f"erdos-{number}")
        if limit is not None and len(ordered) >= limit:
            break
    if not ordered:
        raise TriageSourceError(
            f"triage lane {lane!r} yielded no drainable problems"
        )
    return ordered


def solvability_order(triage_dir: Path, problem_ids: list[str]) -> list[str]:
    """Order an EXISTING campaign set by formal/exact-computation fit.

    Matches ``erdos_searcher.tractable_frontier_ranking`` exactly:
    0.5 Lean prior + 0.4 finite-computation prior + 0.15 Lean-route flag +
    0.05 statement clarity. This is a weak-prior search preference, never a
    solution probability or truth signal. Missing/malformed cards sort last
    in their original order rather than dropping a problem.
    """
    root = Path(triage_dir)
    cards = root / "normalized" / "problem_cards"
    original = {problem_id: index for index, problem_id in enumerate(problem_ids)}

    def score(problem_id: str) -> float:
        number = _problem_number({"problem_id": problem_id})
        if number is None:
            return -1.0
        try:
            card = _read_json(cards / f"{number}.json")
            if not isinstance(card, dict):
                return -1.0
            posterior = card["posterior"]
            lean = float(posterior["p_lean_verified_exact_target"]["probability"])
            compute = float(
                posterior["p_finite_computational_resolution"]["probability"])
            lean_route = bool(
                card["probe_summary"]["formal"]["lean_route_available"])
            clear = card["statement"]["ambiguity_status"] == "clear"
            return 0.5 * lean + 0.4 * compute + 0.15 * lean_route + 0.05 * clear
        except (KeyError, TypeError, ValueError, TriageSourceError):
            return -1.0

    return sorted(problem_ids, key=lambda pid: (-score(pid), original[pid]))
