from __future__ import annotations

import copy
import json

import pytest

from egmra.ranking_queue import (
    QueueProjectionError,
    build_queue_projection,
    load_queue_projection,
    validate_queue_projection,
    write_queue_projection,
)


def _row(number: int, rank: int, prize_status: str) -> dict:
    return {
        "problem_id": f"erdos-{number}",
        "problem_number": number,
        "allocation_rank": rank,
        "allocation_lane": "exploitation",
        "prize": "no" if prize_status == "unpaid" else "$100",
        "prize_status": prize_status,
        "selection_priority_tier": 0 if prize_status == "unpaid" else 1,
        "literature_coverage_status": "partial",
        "base_acquisition_score": 0.1,
        "literature_adjustment": 0.02,
        "selection_score": 0.12,
        "reason_selected": "test ranking",
    }


def _ranking() -> dict:
    return {
        "allocation_status": "ready",
        "allocation_context_id": "a" * 64,
        "ranking_content_sha256": "b" * 64,
        "source_snapshot_id": "source-1",
        "source_snapshot_sha256": "c" * 64,
        "prize_policy_version": "prize-tier-v1",
        "literature_policy_version": "literature-ranking-v1",
        "literature_model_version": "literature-opportunity-v1",
        "literature_coverage": {
            "status_counts": {"local_only": 3},
            "cache_reused_artifacts": 0,
            "live_requests": 0,
            "source_failure_count": 0,
        },
        "corpus_integrity": {
            "status": "complete",
            "canonical_open_source_records": 3,
        },
        "attempt_exclusions": [9],
        "allocation_queue": [
            _row(8, 1, "unpaid"),
            _row(3, 2, "unpaid"),
            _row(5, 3, "paid"),
        ],
    }


def test_projection_round_trip_is_hash_bound(tmp_path):
    projection = build_queue_projection(_ranking())
    path = tmp_path / "current_queue.json"
    path.write_text(json.dumps(projection), encoding="utf-8")

    assert load_queue_projection(path) == projection

    projection["allocation_queue"][0]["selection_score"] = 0.99
    with pytest.raises(QueueProjectionError, match="content hash"):
        validate_queue_projection(projection)


def test_projection_is_deterministic_and_contains_only_public_row_fields():
    first = build_queue_projection(_ranking())
    second = build_queue_projection(copy.deepcopy(_ranking()))

    assert first == second
    assert set(first["allocation_queue"][0]) == {
        "problem_id", "problem_number", "allocation_rank", "allocation_lane",
        "prize", "prize_status", "selection_priority_tier",
        "literature_coverage_status", "base_acquisition_score",
        "literature_adjustment", "selection_score", "reason_selected",
    }


def test_projection_rejects_paid_before_unpaid():
    ranking = _ranking()
    ranking["allocation_queue"] = [
        _row(5, 1, "paid"),
        _row(8, 2, "unpaid"),
    ]

    with pytest.raises(QueueProjectionError, match="unpaid"):
        build_queue_projection(ranking)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda rows: rows[1].update(allocation_rank=7), "contiguous"),
        (lambda rows: rows[1].update(problem_number=8, problem_id="erdos-8"),
         "duplicate"),
        (lambda rows: rows[1].update(prize_status="unknown"), "prize status"),
        (lambda rows: rows[1].update(problem_number=0, problem_id="erdos-0"),
         "positive integer"),
    ],
)
def test_projection_rejects_invalid_rows(mutation, message):
    ranking = _ranking()
    mutation(ranking["allocation_queue"])

    with pytest.raises(QueueProjectionError, match=message):
        build_queue_projection(ranking)


def test_projection_requires_ready_complete_context():
    ranking = _ranking()
    ranking["allocation_status"] = "withheld"
    with pytest.raises(QueueProjectionError, match="not ready"):
        build_queue_projection(ranking)

    ranking = _ranking()
    ranking["corpus_integrity"]["status"] = "degraded"
    with pytest.raises(QueueProjectionError, match="corpus integrity"):
        build_queue_projection(ranking)


def test_projection_writer_is_atomic_and_validated(tmp_path):
    path = tmp_path / "rankings" / "current_queue.json"
    projection = write_queue_projection(path, _ranking())

    assert load_queue_projection(path) == projection
    assert not path.with_suffix(".json.tmp").exists()


def test_projection_loader_rejects_symlink(tmp_path):
    real = tmp_path / "real.json"
    real.write_text(json.dumps(build_queue_projection(_ranking())))
    link = tmp_path / "current_queue.json"
    link.symlink_to(real)

    with pytest.raises(QueueProjectionError, match="regular file"):
        load_queue_projection(link)
