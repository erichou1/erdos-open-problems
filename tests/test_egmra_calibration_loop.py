"""The closed calibration loop: EGMRA outcomes → searcher posteriors → ranking.

The adjustment is deliberately WEAK and CAPPED (observed pipeline telemetry,
never verified outcomes: a verified ledger record moves a posterior by 3.0;
an entire EGMRA history is capped below that), every application is recorded
in the posterior with its reasons, and the report loader fails closed on
malformed or symlinked input.  The `egmra refresh-ranking` command and the
campaign's `--refresh-ranking-after` hook drive the rebuild end-to-end.
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import egmra.cli as cli_module
from erdos_searcher import estimate_posteriors, load_egmra_calibration
from tests.test_searcher_safety import base_card


# ---------------------------------------------------------------------------
# posterior adjustment semantics


def test_no_calibration_leaves_posteriors_identical():
    card = base_card()
    baseline = estimate_posteriors(card)
    unadjusted = estimate_posteriors(card, egmra_calibration=None)
    assert baseline["p_verified_partial_progress"] == \
        unadjusted["p_verified_partial_progress"]
    assert unadjusted["calibration_status"] == "uncalibrated_weak_prior_mvp"
    assert unadjusted["egmra_calibration"] is None


def test_repeated_interpretation_blocks_raise_failure_posterior():
    card = base_card()
    baseline = estimate_posteriors(card)
    adjusted = estimate_posteriors(card, egmra_calibration={
        "attempts": 3, "states": {"BLOCKED_BY_INTERPRETATION": 3},
        "salvaged_supported_claims": 0,
    })
    key = "p_statement_or_interpretation_failure"
    assert adjusted[key]["probability"] > baseline[key]["probability"]
    assert adjusted["calibration_status"] == "egmra_outcome_adjusted"
    note = adjusted["egmra_calibration"]
    assert note["applied"] and "interpretation_failure_evidence" in note["adjustments"]
    assert "never a verified outcome" in note["note"]


def test_observed_progress_raises_partial_progress_posterior():
    card = base_card()
    baseline = estimate_posteriors(card)
    adjusted = estimate_posteriors(card, egmra_calibration={
        "attempts": 2, "states": {"COMPUTATIONAL_EVIDENCE": 2},
        "salvaged_supported_claims": 3,
    })
    key = "p_verified_partial_progress"
    assert adjusted[key]["probability"] > baseline[key]["probability"]
    reasons = adjusted["egmra_calibration"]["adjustments"]
    assert "observed_progress_evidence" in reasons
    assert "salvaged_claims_evidence" in reasons


def test_adjustment_is_capped_below_a_verified_outcome():
    """1000 observed attempts must move the posterior less than ONE verified record."""
    card = base_card()
    flooded = estimate_posteriors(card, egmra_calibration={
        "attempts": 1000, "states": {"COMPUTATIONAL_EVIDENCE": 1000},
        "salvaged_supported_claims": 1000,
    })
    verified = estimate_posteriors(
        deepcopy(card), [{"status": "verified_partial_progress"}])
    key = "p_verified_partial_progress"
    assert flooded[key]["probability"] <= verified[key]["probability"]
    caps = flooded["egmra_calibration"]["adjustments"]
    assert caps["observed_progress_evidence"] <= 2.0
    assert caps["salvaged_claims_evidence"] <= 1.0


def test_single_block_or_bare_attempts_apply_nothing():
    card = base_card()
    unmoved = estimate_posteriors(card, egmra_calibration={
        "attempts": 1, "states": {"BLOCKED_BY_INTERPRETATION": 1},
        "salvaged_supported_claims": 0,
    })
    assert unmoved["calibration_status"] == "uncalibrated_weak_prior_mvp"
    assert not unmoved["egmra_calibration"]["applied"]


# ---------------------------------------------------------------------------
# report loader (fail-closed)


def test_load_egmra_calibration_paths(tmp_path):
    assert load_egmra_calibration(None) == ({}, {"enabled": False})

    report = tmp_path / "calibration.json"
    report.write_text(json.dumps({
        "generated_at": "2026-07-14T00:00:00Z", "total_runs": 3,
        "by_problem": {"erdos-312": {
            "attempts": 2, "states": {"BLOCKED_BY_INTERPRETATION": 2},
            "salvaged_supported_claims": 1}},
    }))
    by_problem, provenance = load_egmra_calibration(report)
    assert by_problem["erdos-312"]["attempts"] == 2
    assert provenance["enabled"] and len(provenance["report_sha256"]) == 64

    malformed = tmp_path / "bad.json"
    malformed.write_text("{\"by_problem\": []}")
    with pytest.raises(RuntimeError):
        load_egmra_calibration(malformed)

    link = tmp_path / "link.json"
    link.symlink_to(report)
    with pytest.raises(RuntimeError):
        load_egmra_calibration(link)


# ---------------------------------------------------------------------------
# refresh plumbing (CLI command + campaign hook), via the searcher seam


def _seed_ledger(path: Path) -> None:
    path.write_text(json.dumps({
        "problem_id": "erdos-312", "public_state": "BLOCKED_BY_INTERPRETATION",
        "recorded_at": "2026-07-14T01:00:00Z", "released": False,
    }) + "\n")


def test_refresh_ranking_command_writes_report_and_rebuilds(tmp_path, capsys,
                                                            monkeypatch):
    ledger = tmp_path / "outcomes.jsonl"
    _seed_ledger(ledger)
    seen: dict = {}

    def fake_build(searcher_root, output_root, *, snapshot_date, top_k,
                   calibration_path):
        seen.update(root=searcher_root, output=output_root,
                    calibration=Path(calibration_path))
        return {"eligible_problems": 591, "snapshot_id": "snap-1",
                "egmra_calibration": {"enabled": True},
                "ranking_pipeline": {
                    "policy_version": "egmra-ranking-pipeline-v1",
                    "content_sha256": "a" * 64,
                    "selected_count": 25,
                    "stages": [
                        {"stage": "validate", "status": "passed"},
                        {"stage": "allocate", "status": "passed"},
                    ],
                }}

    monkeypatch.setattr(cli_module, "_build_searcher_for_refresh", fake_build)
    rc = cli_module.main(["refresh-ranking", "--outcomes", str(ledger),
                          "--searcher-root", str(tmp_path),
                          "--searcher-output", str(tmp_path / "triage")])
    assert rc == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["eligible_problems"] == 591
    assert summary["ranking_pipeline"] == {
        "policy_version": "egmra-ranking-pipeline-v1",
        "content_sha256": "a" * 64,
        "selected_count": 25,
        "stages": [
            {"stage": "validate", "status": "passed"},
            {"stage": "allocate", "status": "passed"},
        ],
    }
    # the derived calibration report was written where the searcher reads it
    report = json.loads(seen["calibration"].read_text())
    assert report["by_problem"]["erdos-312"]["attempts"] == 1
    assert seen["calibration"].parent.name == "labels"


def test_build_searcher_refresh_inherits_exact_current_allocation_contract(
        tmp_path, monkeypatch):
    from egmra.ranking_queue import write_queue_projection

    output = tmp_path / "triage"
    rankings = output / "rankings"
    context_id = "c" * 64
    ranking_hash = "d" * 64
    complete_ranking = {
        "allocation_status": "ready",
        "allocation_context_id": context_id,
        "ranking_content_sha256": ranking_hash,
        "source_snapshot_id": "snapshot-1",
        "source_snapshot_sha256": "e" * 64,
        "prize_policy_version": "p1",
        "literature_policy_version": "l1",
        "literature_model_version": "m1",
        "literature_coverage": {},
        "corpus_integrity": {"status": "complete"},
        "attempt_exclusions": [],
        "allocation_queue": [{
            "problem_id": "erdos-1", "problem_number": 1,
            "allocation_rank": 1, "allocation_lane": "exploitation",
            "prize": "no", "prize_status": "unpaid",
            "selection_priority_tier": 0,
            "literature_coverage_status": "partial",
            "base_acquisition_score": 0.1, "literature_adjustment": 0.0,
            "selection_score": 0.1, "reason_selected": "test",
        }],
    }
    write_queue_projection(rankings / "current_queue.json", complete_ranking)
    immutable = rankings / "contexts" / context_id / f"{ranking_hash}.json"
    immutable.parent.mkdir(parents=True)
    immutable.write_text(json.dumps({
        "allocation_context_id": context_id,
        "ranking_content_sha256": ranking_hash,
        "model_portfolio": "chatgpt-5.6",
        "budget": "verified_pipeline_v2:test",
        "allocation_context": {
            "model_portfolio": "chatgpt-5.6",
            "budget": "verified_pipeline_v2:test",
            "budget_config": {"prover_calls": 1, "verifier_calls": 1,
                              "literature_calls": 1, "max_iterations": 1},
        },
    }))
    captured = {}

    def fake_searcher(root, output_root, **kwargs):
        captured.update(kwargs)
        return {"ok": True}

    import erdos_searcher
    monkeypatch.setattr(erdos_searcher, "build_searcher", fake_searcher)
    result = cli_module._build_searcher_for_refresh(
        tmp_path, output, snapshot_date="2026-07-17", top_k=25,
        calibration_path=tmp_path / "calibration.json")
    assert result == {"ok": True}
    assert captured["model_portfolio"] == "chatgpt-5.6"
    assert captured["budget"] == "verified_pipeline_v2:test"
    assert captured["budget_config"]["max_iterations"] == 1


def test_build_searcher_refresh_rejects_misbound_immutable_contract(
        tmp_path):
    from egmra.ranking_queue import write_queue_projection

    output = tmp_path / "triage"
    rankings = output / "rankings"
    context_id, ranking_hash = "c" * 64, "d" * 64
    write_queue_projection(rankings / "current_queue.json", {
        "allocation_status": "ready", "allocation_context_id": context_id,
        "ranking_content_sha256": ranking_hash,
        "source_snapshot_id": "s", "source_snapshot_sha256": "e" * 64,
        "prize_policy_version": "p", "literature_policy_version": "l",
        "literature_model_version": "m", "literature_coverage": {},
        "corpus_integrity": {"status": "complete"}, "attempt_exclusions": [],
        "allocation_queue": [{
            "problem_id": "erdos-1", "problem_number": 1,
            "allocation_rank": 1, "allocation_lane": "exploitation",
            "prize": "no", "prize_status": "unpaid",
            "selection_priority_tier": 0,
            "literature_coverage_status": "partial",
            "base_acquisition_score": 0.1, "literature_adjustment": 0.0,
            "selection_score": 0.1, "reason_selected": "test",
        }],
    })
    immutable = rankings / "contexts" / context_id / f"{ranking_hash}.json"
    immutable.parent.mkdir(parents=True)
    immutable.write_text(json.dumps({
        "allocation_context_id": "wrong", "ranking_content_sha256": ranking_hash,
        "model_portfolio": "chatgpt-5.6", "budget": "b",
        "allocation_context": {
            "model_portfolio": "chatgpt-5.6", "budget": "b", "budget_config": {},
        },
    }))
    with pytest.raises(RuntimeError, match="binding mismatch"):
        cli_module._build_searcher_for_refresh(
            tmp_path, output, snapshot_date="2026-07-17", top_k=25,
            calibration_path=tmp_path / "calibration.json")


def test_campaign_refresh_ranking_after_runs_the_full_loop(tmp_path, capsys,
                                                           monkeypatch):
    from egmra.tests.conftest import TEST_KEYS
    from egmra.tests.test_cli import _signed_policy_file, _write_triage

    # This file lives outside egmra/tests, so the autouse key fixture does not
    # apply; provide the process-local test keys explicitly (never rely on the
    # invoking shell having sourced real keys).
    for name, value in TEST_KEYS.items():
        monkeypatch.setenv(name, value)

    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)
    triage = _write_triage(tmp_path)
    ledger = tmp_path / "outcomes.jsonl"

    def fake_build(searcher_root, output_root, *, snapshot_date, top_k,
                   calibration_path):
        return {"eligible_problems": 2, "snapshot_id": "snap-2",
                "egmra_calibration": {"enabled": True,
                                      "report": str(calibration_path)}}

    monkeypatch.setattr(cli_module, "_build_searcher_for_refresh", fake_build)
    rc = cli_module.main(["--config", str(cfg), "campaign",
                          "--triage", str(triage), "--triage-lane", "current",
                          "--provider", "deterministic", "--policy", str(policy),
                          "--retrieval", "none", "--oeis", "offline",
                          "--refresh-ranking-after",
                          "--state", str(tmp_path / "camp.json"),
                          "--outcome-ledger", str(ledger)])
    assert rc == 0
    status = json.loads(capsys.readouterr().out)
    refresh = status["ranking_refresh"]
    assert refresh["snapshot_id"] == "snap-2"
    # the report fed to the searcher was derived from THIS campaign's ledger
    report = json.loads(Path(refresh["calibration_report"]).read_text())
    assert set(report["by_problem"]) == {"erdos-312", "erdos-1104"}
