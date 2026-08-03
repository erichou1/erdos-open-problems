"""EGMRA-native outcome ledger for the continuous drainer (audit R11, native scope).

Pins that the ledger records honest, decoupled telemetry (public state + gate
profile + run id), reads back append-only, and never claims release authority
beyond a present certificate.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

from egmra.orchestrator.outcome_ledger import (
    EgmraOutcomeLedger,
    build_outcome_record,
)


class _Gates:
    def profile(self):
        return {"truth": "T2", "intent": "I2", "formal_correspondence": "N/A",
                "novelty": "known", "significance": "S1", "reproducibility": "R2"}


def _result(*, outcome, certificate=None, complete=True, gates=None, events=5):
    return SimpleNamespace(
        outcome=outcome,
        acquired=True,
        certificate=certificate,
        compiled_proof=SimpleNamespace(complete=complete),
        gates=gates,
        graph=SimpleNamespace(log=list(range(events))),
    )


def test_build_record_captures_honest_fields():
    record = build_outcome_record(
        problem_id="erdos-336",
        result=_result(outcome="verified_finite_or_conditional_result",
                       certificate=object(), gates=_Gates(), events=10),
        run_id="run-abc", state="COMPUTATIONAL_EVIDENCE")
    assert record["problem_id"] == "erdos-336"
    assert record["public_state"] == "COMPUTATIONAL_EVIDENCE"
    assert record["released"] is True
    assert record["gate_profile"]["truth"] == "T2"
    assert record["event_count"] == 10
    assert record["schema_version"] == 1


def test_no_certificate_means_not_released():
    record = build_outcome_record(
        problem_id="erdos-312",
        result=_result(outcome="honest_triage_report", certificate=None,
                       gates=None, complete=False),
        run_id="run-xyz", state="BLOCKED_BY_INTERPRETATION")
    assert record["released"] is False
    assert record["gate_profile"] is None
    assert record["candidate_assembly_complete"] is False


def test_ledger_append_and_readback(tmp_path):
    ledger = EgmraOutcomeLedger(tmp_path / "out.jsonl")
    ledger.record(build_outcome_record(
        problem_id="erdos-1", result=_result(outcome="no_result"),
        run_id="r1", state="OPEN_NO_PROGRESS"))
    ledger.record(build_outcome_record(
        problem_id="erdos-2", result=_result(outcome="honest_triage_report"),
        run_id="r2", state="CANDIDATE_DISPROOF"))
    records = ledger.records()
    assert [r["problem_id"] for r in records] == ["erdos-1", "erdos-2"]
    # Each line is independently valid JSON (append-only, one record per line).
    lines = (tmp_path / "out.jsonl").read_text().splitlines()
    assert len(lines) == 2 and all(json.loads(line) for line in lines)


def test_latest_by_problem_keeps_most_recent(tmp_path):
    ledger = EgmraOutcomeLedger(tmp_path / "out.jsonl")
    ledger.record(build_outcome_record(
        problem_id="erdos-1", result=_result(outcome="no_result"),
        run_id="r1", state="OPEN_NO_PROGRESS"))
    ledger.record(build_outcome_record(
        problem_id="erdos-1", result=_result(outcome="honest_triage_report"),
        run_id="r2", state="COMPUTATIONAL_EVIDENCE"))
    latest = ledger.latest_by_problem()
    assert set(latest) == {"erdos-1"}
    assert latest["erdos-1"]["run_id"] == "r2"
    assert latest["erdos-1"]["public_state"] == "COMPUTATIONAL_EVIDENCE"


def test_malformed_lines_are_skipped(tmp_path):
    path = tmp_path / "out.jsonl"
    path.write_text('{"problem_id": "erdos-1", "public_state": "X"}\n'
                    "not json\n"
                    "\n"
                    '{"problem_id": "erdos-2", "public_state": "Y"}\n',
                    encoding="utf-8")
    ledger = EgmraOutcomeLedger(path)
    assert [r["problem_id"] for r in ledger.records()] == ["erdos-1", "erdos-2"]


def test_missing_ledger_reads_empty(tmp_path):
    assert EgmraOutcomeLedger(tmp_path / "nope.jsonl").records() == []
