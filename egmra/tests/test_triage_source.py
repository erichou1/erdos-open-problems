"""Triage-ranked problem source for the EGMRA continuous drainer (single pipeline).

These pin the behavior that lets ``egmra campaign --triage`` replace the legacy
``run_continuous.py``: read the searcher's own rankings, drain in ranked order,
skip exclusions, and fail closed when a lane is unknown/malformed/not-ready.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from egmra.orchestrator.triage_source import (
    TriageSourceError,
    _read_json,
    available_lanes,
    solvability_order,
    triage_ranked_problem_ids,
)


def _write(rankings_dir: Path, lane: str, document: dict) -> None:
    rankings_dir.mkdir(parents=True, exist_ok=True)
    (rankings_dir / f"{lane}.json").write_text(json.dumps(document), encoding="utf-8")


def _alloc(entries, *, status="ready", exclusions=()):
    return {
        "allocation_status": status,
        "allocation_queue": entries,
        "attempt_exclusions": list(exclusions),
    }


def test_allocation_queue_drained_in_rank_order(tmp_path):
    rankings = tmp_path / "rankings"
    _write(rankings, "current", _alloc([
        {"problem_number": 312, "allocation_rank": 1},
        {"problem_number": 1104, "allocation_rank": 2},
        {"problem_number": 153, "allocation_rank": 3},
    ]))
    ids = triage_ranked_problem_ids(tmp_path, lane="current")
    assert ids == ["erdos-312", "erdos-1104", "erdos-153"]


def test_limit_caps_and_preserves_order(tmp_path):
    rankings = tmp_path / "rankings"
    _write(rankings, "current", _alloc([
        {"problem_number": n} for n in (5, 6, 7, 8)
    ]))
    assert triage_ranked_problem_ids(tmp_path, lane="current", limit=2) == [
        "erdos-5", "erdos-6"]


def test_exclusions_and_duplicates_are_skipped(tmp_path):
    rankings = tmp_path / "rankings"
    _write(rankings, "current", _alloc(
        [{"problem_number": n} for n in (5, 6, 6, 7)], exclusions=[6]))
    assert triage_ranked_problem_ids(tmp_path, lane="current") == [
        "erdos-5", "erdos-7"]


def test_allocation_not_ready_is_refused(tmp_path):
    rankings = tmp_path / "rankings"
    _write(rankings, "current", _alloc([{"problem_number": 5}], status="withheld"))
    with pytest.raises(TriageSourceError):
        triage_ranked_problem_ids(tmp_path, lane="current")


def test_single_objective_lane_uses_its_own_list_and_current_exclusions(tmp_path):
    rankings = tmp_path / "rankings"
    _write(rankings, "current", _alloc([{"problem_number": 5}], exclusions=[9]))
    _write(rankings, "tractable_frontier", {
        "tractable_frontier": [
            {"problem_number": 8}, {"problem_number": 9}, {"problem_number": 10}]})
    # 9 is excluded via the allocation-context exclusions even on another lane.
    assert triage_ranked_problem_ids(tmp_path, lane="tractable_frontier") == [
        "erdos-8", "erdos-10"]


def test_t2_lane_reads_problems_list(tmp_path):
    rankings = tmp_path / "rankings"
    _write(rankings, "t2_closable", {
        "problems": [
            {"problem": 742, "state": "decidable"},
            {"problem": 7, "state": "verifiable"},
        ]})
    assert triage_ranked_problem_ids(tmp_path, lane="t2_closable") == [
        "erdos-742", "erdos-7"]


def test_unknown_lane_rejected(tmp_path):
    with pytest.raises(TriageSourceError):
        triage_ranked_problem_ids(tmp_path, lane="not_a_lane")


def test_missing_ranking_file_rejected(tmp_path):
    (tmp_path / "rankings").mkdir()
    with pytest.raises(TriageSourceError):
        triage_ranked_problem_ids(tmp_path, lane="current")


def test_empty_lane_rejected(tmp_path):
    rankings = tmp_path / "rankings"
    _write(rankings, "current", _alloc([]))
    with pytest.raises(TriageSourceError):
        triage_ranked_problem_ids(tmp_path, lane="current")


def test_symlink_ranking_refused(tmp_path):
    rankings = tmp_path / "rankings"
    rankings.mkdir()
    real = tmp_path / "real.json"
    real.write_text(json.dumps(_alloc([{"problem_number": 5}])), encoding="utf-8")
    (rankings / "current.json").symlink_to(real)
    with pytest.raises(TriageSourceError):
        triage_ranked_problem_ids(tmp_path, lane="current")


class _SizedRankingPath:
    def __init__(self, size: int) -> None:
        self.size = size

    def is_symlink(self) -> bool:
        return False

    def is_file(self) -> bool:
        return True

    def stat(self):
        return type("Stat", (), {"st_size": self.size})()

    def read_text(self, *, encoding: str) -> str:
        return json.dumps(_alloc([{"problem_number": 5}]))

    def __str__(self) -> str:
        return "sized-ranking.json"


def test_reader_accepts_current_auditable_ranking_size():
    document = _read_json(_SizedRankingPath(44_000_000))
    assert document["allocation_status"] == "ready"


def test_reader_still_rejects_excessive_ranking_size():
    with pytest.raises(TriageSourceError, match="implausibly large"):
        _read_json(_SizedRankingPath(65_000_000))


def test_available_lanes_includes_t2_and_current():
    lanes = available_lanes()
    assert "current" in lanes and "t2_closable" in lanes


def _card(root: Path, number: int, *, lean: float, compute: float,
          route: bool, clear: bool) -> None:
    directory = root / "normalized" / "problem_cards"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{number}.json").write_text(json.dumps({
        "posterior": {
            "p_lean_verified_exact_target": {"probability": lean},
            "p_finite_computational_resolution": {"probability": compute},
        },
        "probe_summary": {"formal": {"lean_route_available": route}},
        "statement": {"ambiguity_status": "clear" if clear else "ambiguous"},
    }), encoding="utf-8")


def test_solvability_order_matches_tractable_frontier_formula(tmp_path):
    _card(tmp_path, 1, lean=.1, compute=.1, route=False, clear=True)
    _card(tmp_path, 2, lean=.7, compute=.2, route=True, clear=True)
    _card(tmp_path, 3, lean=.2, compute=.8, route=False, clear=True)
    # score: #2=.63, #3=.47, #1=.14
    assert solvability_order(
        tmp_path, ["erdos-1", "erdos-2", "erdos-3"]
    ) == ["erdos-2", "erdos-3", "erdos-1"]


def test_solvability_order_keeps_missing_cards_last_and_stable(tmp_path):
    _card(tmp_path, 2, lean=.2, compute=.2, route=False, clear=True)
    assert solvability_order(
        tmp_path, ["erdos-9", "erdos-2", "erdos-8"]
    ) == ["erdos-2", "erdos-9", "erdos-8"]
