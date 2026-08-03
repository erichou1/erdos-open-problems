"""Continuous outcome-driven reranking (search preference only, never truth).

The rerank is pure and deterministic; problems with no outcomes keep their
exact searcher rank (stable tie-break); dead-ends demote and observed
progress promotes, each move carrying its recorded reason; a reorder is a
strict permutation — nothing is ever added or dropped.
"""

from __future__ import annotations

import json

from egmra.orchestrator.campaign import Campaign, CampaignError
from egmra.orchestrator.rerank import rerank_pending

import pytest

BASE = ["erdos-1", "erdos-2", "erdos-3", "erdos-4"]


def _row(problem_id, state, **extra):
    return {"problem_id": problem_id, "public_state": state, **extra}


def test_no_outcomes_keeps_searcher_order_exactly():
    order, reasons = rerank_pending(BASE, [])
    assert order == BASE and reasons == {}


def test_repeated_dead_end_demotes_with_recorded_reason():
    rows = [_row("erdos-1", "BLOCKED_BY_INTERPRETATION"),
            _row("erdos-1", "BLOCKED_BY_INTERPRETATION")]
    order, reasons = rerank_pending(BASE, rows)
    assert order == ["erdos-2", "erdos-3", "erdos-4", "erdos-1"]
    assert any(r.startswith("repeated_dead_end") for r in reasons["erdos-1"])


def test_single_dead_end_is_not_enough_to_demote():
    order, _ = rerank_pending(BASE, [_row("erdos-1", "BLOCKED_BY_INTERPRETATION")])
    assert order == BASE                     # one bad attempt is not a verdict


def test_observed_progress_promotes():
    rows = [_row("erdos-3", "COMPUTATIONAL_EVIDENCE",
                 candidate_assembly_complete=True)]
    order, reasons = rerank_pending(BASE, rows)
    assert order[0] == "erdos-3"
    assert any(r.startswith("observed_progress") for r in reasons["erdos-3"])
    # untouched problems keep their relative searcher order
    assert [p for p in order if p != "erdos-3"] == ["erdos-1", "erdos-2", "erdos-4"]


def test_salvaged_claims_count_as_progress_signal():
    rows = [_row("erdos-4", "OPEN_NO_PROGRESS",
                 salvage={"supported": [{"claim_id": "lem1"}], "refuted": []})]
    order, reasons = rerank_pending(BASE, rows)
    assert order.index("erdos-4") < BASE.index("erdos-4")
    assert any(r.startswith("salvaged_supported_claims") for r in reasons["erdos-4"])


def test_rerank_is_deterministic_and_a_permutation():
    rows = [_row("erdos-1", "BLOCKED_BY_INTERPRETATION")] * 2 + \
           [_row("erdos-4", "COMPUTATIONAL_EVIDENCE")]
    first, _ = rerank_pending(BASE, rows)
    second, _ = rerank_pending(BASE, rows)
    assert first == second
    assert sorted(first) == sorted(BASE)     # never adds or drops a problem


# ---------------------------------------------------------------------------
# Campaign.reorder_pending


def _campaign(tmp_path):
    campaign = Campaign(tmp_path / "state.json", worker_ids=("w0",))
    campaign.initialize("rerank-test", list(BASE))
    return campaign


def test_reorder_changes_which_problem_leases_next(tmp_path):
    campaign = _campaign(tmp_path)
    assert campaign.reorder_pending(["erdos-3", "erdos-1", "erdos-2", "erdos-4"])
    leased = campaign.lease("w0", now=0.0)
    assert leased.problem_id == "erdos-3"


def test_reorder_rejects_anything_but_a_permutation(tmp_path):
    campaign = _campaign(tmp_path)
    with pytest.raises(CampaignError):
        campaign.reorder_pending(["erdos-1", "erdos-2", "erdos-3"])          # dropped
    with pytest.raises(CampaignError):
        campaign.reorder_pending(BASE + ["erdos-99"])                        # added
    with pytest.raises(CampaignError):
        campaign.reorder_pending(["erdos-1", "erdos-1", "erdos-2", "erdos-3"])  # dup


def test_reorder_same_order_is_a_recorded_noop(tmp_path):
    campaign = _campaign(tmp_path)
    assert campaign.reorder_pending(list(BASE)) is False


def test_reorder_never_disturbs_a_live_lease(tmp_path):
    campaign = _campaign(tmp_path)
    leased = campaign.lease("w0", now=0.0)
    assert leased.problem_id == "erdos-1"
    campaign.reorder_pending(["erdos-4", "erdos-3", "erdos-2", "erdos-1"])
    # the in-flight lease completes under its original fencing token
    assert campaign.complete("erdos-1", "w0", leased.fencing_token,
                             result_state="OPEN_NO_PROGRESS")
    # and the next lease follows the NEW order
    assert campaign.lease("w0", now=0.0).problem_id == "erdos-4"


def test_reordered_state_is_still_signed_and_loadable(tmp_path):
    campaign = _campaign(tmp_path)
    campaign.reorder_pending(["erdos-2", "erdos-1", "erdos-3", "erdos-4"])
    # a fresh Campaign over the same state verifies the signature on read
    reopened = Campaign(tmp_path / "state.json", worker_ids=("w0",))
    assert reopened.lease("w0", now=0.0).problem_id == "erdos-2"
    raw = json.loads((tmp_path / "state.json").read_text())
    assert raw["order"][0] == "erdos-2" and raw.get("signature")
