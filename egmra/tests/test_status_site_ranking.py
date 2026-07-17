"""Public ranking projection must match the shared worker allocation."""

from __future__ import annotations

import json
from pathlib import Path

from egmra.ranking_queue import build_queue_projection
from status_site.build_data import build_public_ranking


ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "status_site"


def _queue() -> dict:
    rows = []
    for rank, number in enumerate((8, 3, 5), start=1):
        status = "paid" if number == 5 else "unpaid"
        rows.append({
            "problem_id": f"erdos-{number}",
            "problem_number": number,
            "allocation_rank": rank,
            "allocation_lane": "exploitation",
            "prize": "$100" if status == "paid" else "no",
            "prize_status": status,
            "selection_priority_tier": int(status == "paid"),
            "literature_coverage_status": "partial",
            "base_acquisition_score": 0.1 - rank / 100,
            "literature_adjustment": 0.02,
            "selection_score": 0.12 - rank / 100,
            "reason_selected": "test allocation",
        })
    return build_queue_projection({
        "allocation_status": "ready",
        "allocation_context_id": "a" * 64,
        "ranking_content_sha256": "b" * 64,
        "source_snapshot_id": "source-1",
        "source_snapshot_sha256": "c" * 64,
        "prize_policy_version": "prize-tier-v1",
        "literature_policy_version": "literature-ranking-v1",
        "literature_model_version": "literature-opportunity-v1",
        "literature_coverage": {},
        "corpus_integrity": {"status": "complete"},
        "attempt_exclusions": [],
        "allocation_queue": rows,
    })


def test_public_ranking_follows_queue_and_joins_campaign_progress(tmp_path):
    cards = tmp_path / "triage" / "normalized" / "problem_cards"
    cards.mkdir(parents=True)
    (cards / "3.json").write_text(json.dumps({
        "statement": {"normalized": "Fallback statement for three."}
    }))
    campaign = [{
        "problem_id": "erdos-8",
        "number": 8,
        "statement": "Campaign statement for eight.",
        "status": "leased",
        "worker": "w0",
        "progress": {"percent": 40, "stage": "Approaches explored"},
    }, {
        "problem_id": "erdos-99",
        "number": 99,
        "statement": "Stale campaign-only problem.",
        "status": "pending",
        "worker": None,
        "progress": {"percent": 5, "stage": "Queued"},
    }]

    ranking = build_public_ranking(_queue(), campaign, root=tmp_path)

    assert [row["number"] for row in ranking] == [8, 3, 5]
    assert ranking[0]["progress"] == campaign[0]["progress"]
    assert ranking[0]["worker"] == "w0"
    assert ranking[1]["statement"] == "Fallback statement for three."
    assert ranking[1]["progress"]["stage"] == "Queued"
    assert ranking[2]["prize_status"] == "paid"
    assert all(row["number"] != 99 for row in ranking)


def test_ranking_page_names_shared_policy_and_renders_projection_fields():
    html = (SITE / "ranking.html").read_text(encoding="utf-8")
    javascript = (SITE / "ranking.js").read_text(encoding="utf-8")

    assert "eligible unpaid problems" in html
    assert "Literature adjustment" in html
    for field in (
        "allocation_rank",
        "prize_status",
        "literature_coverage_status",
        "base_acquisition_score",
        "literature_adjustment",
        "selection_score",
    ):
        assert field in javascript
