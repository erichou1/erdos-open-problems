"""Outcome-ledger calibration report (R11, EGMRA-native).

The outcome ledger accumulates honest per-run telemetry; this module reads it
back into an aggregate report so triage can be recalibrated from observed
outcomes instead of static heuristics.

Honesty invariants: the report only COUNTS what the ledger records — it never
reinterprets a state, never scores "how close" a failed run was, and carries
an explicit note that these are frequencies, not posteriors.  Malformed lines
are counted and surfaced, never silently dropped.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_calibration_report(ledger_paths: list[Path | str]) -> dict[str, Any]:
    """Aggregate one or more outcome ledgers into a calibration report."""
    by_state: dict[str, int] = {}
    by_problem: dict[str, dict[str, Any]] = {}
    truth_distribution: dict[str, int] = {}
    salvage_supported = 0
    released: list[str] = []
    total = 0
    malformed = 0
    for raw_path in ledger_paths:
        path = Path(raw_path)
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"outcome ledger must be a regular file: {path}")
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                problem_id = str(record["problem_id"])
                state = str(record["public_state"])
            except (json.JSONDecodeError, KeyError, TypeError):
                malformed += 1
                continue
            total += 1
            by_state[state] = by_state.get(state, 0) + 1
            entry = by_problem.setdefault(problem_id, {
                "attempts": 0, "states": {}, "last_state": "",
                "last_recorded_at": "", "salvaged_supported_claims": 0,
            })
            entry["attempts"] += 1
            entry["states"][state] = entry["states"].get(state, 0) + 1
            recorded_at = str(record.get("recorded_at", ""))
            if recorded_at >= entry["last_recorded_at"]:
                entry["last_recorded_at"] = recorded_at
                entry["last_state"] = state
            profile = record.get("gate_profile")
            if isinstance(profile, dict) and profile.get("truth"):
                truth = str(profile["truth"])
                truth_distribution[truth] = truth_distribution.get(truth, 0) + 1
            salvage = record.get("salvage")
            if isinstance(salvage, dict):
                supported = salvage.get("supported")
                if isinstance(supported, list):
                    count = len(supported)
                    salvage_supported += count
                    entry["salvaged_supported_claims"] += count
            if record.get("released"):
                released.append(problem_id)
    return {
        "schema_version": 1,
        "generated_at": _utc_now(),
        "total_runs": total,
        "malformed_lines": malformed,
        "by_state": dict(sorted(by_state.items())),
        "by_problem": dict(sorted(by_problem.items())),
        "gate_truth_distribution": dict(sorted(truth_distribution.items())),
        "salvaged_supported_claims": salvage_supported,
        "released_problem_ids": sorted(set(released)),
        "note": (
            "observed outcome frequencies from the EGMRA outcome ledger; "
            "counts, not posteriors — no claim about how close a failed run "
            "came, and never a release authority"
        ),
    }
