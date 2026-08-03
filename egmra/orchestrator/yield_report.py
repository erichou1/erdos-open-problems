"""Cost / mathematical-yield telemetry over persisted runs (report R13).

The optimization target is *admissible evidence per unit of model cost*, not
branch or claim counts. This module turns the persisted artifacts that already
exist — signed event logs (`egmra_runs/*.jsonl`) and outcome ledgers
(`egmra_outcomes/*.jsonl`) — into one versioned yield report, replacing the ad
hoc shell census in the effectiveness report §3.2.4.

Read-only and fail-open: malformed lines are counted, never raised; the report
is diagnostics for allocation decisions, never a truth or release input.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

# Event actions that represent genuinely admissible progress artifacts.
_EVIDENCE_ACTIONS = ("EVIDENCE_ATTACHED", "CLAIM_PROMOTED")
_EXCHANGE_ACTION = "MODEL_EXCHANGE_RECORDED"
_PROGRESS_STATES = frozenset({
    "PARTIAL_PROGRESS", "CONDITIONAL_RESULT", "COMPUTATIONAL_EVIDENCE",
    "CANDIDATE_PROOF", "CANDIDATE_DISPROOF", "FORMALLY_VERIFIED_CANDIDATE",
    "EXTERNALLY_VALIDATED_SOLUTION", "EXTERNALLY_VALIDATED_DISPROOF",
})


def _iter_jsonl(path: Path):
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    yield None
    except OSError:
        return


def build_yield_report(runs_dir: Path,
                       outcome_paths: tuple[Path, ...] = ()) -> dict[str, Any]:
    """Aggregate event logs + outcome ledgers into the R13 yield metrics."""
    actions: Counter[str] = Counter()
    depth: Counter[int] = Counter()
    malformed = 0
    run_files = 0
    runs_with_evidence = 0
    runs_dir = Path(runs_dir)
    for path in sorted(runs_dir.glob("*.jsonl")):
        if path.is_symlink():
            continue
        run_files += 1
        events = 0
        run_actions: Counter[str] = Counter()
        for record in _iter_jsonl(path):
            if record is None or not isinstance(record, dict):
                malformed += 1
                continue
            events += 1
            action = str(record.get("action", ""))
            if action:
                run_actions[action] += 1
        actions.update(run_actions)
        depth[events] += 1
        if any(run_actions.get(a) for a in _EVIDENCE_ACTIONS):
            runs_with_evidence += 1

    outcomes: Counter[str] = Counter()
    salvaged_claims = 0
    for outcome_path in outcome_paths:
        for record in _iter_jsonl(Path(outcome_path)):
            if record is None or not isinstance(record, dict):
                malformed += 1
                continue
            outcomes[str(record.get("public_state", ""))] += 1
            salvage = record.get("salvage") or {}
            salvaged_claims += len(salvage.get("supported") or ())

    branches = actions.get("BRANCH_OPENED", 0)
    claims = actions.get("CLAIM_PROPOSED", 0)
    evidence = sum(actions.get(a, 0) for a in _EVIDENCE_ACTIONS)
    exchanges = actions.get(_EXCHANGE_ACTION, 0)
    progress_outcomes = sum(
        count for state, count in outcomes.items() if state in _PROGRESS_STATES)

    def _per_100(numerator: int, denominator: int) -> float | None:
        return round(100.0 * numerator / denominator, 3) if denominator else None

    return {
        "schema_version": SCHEMA_VERSION,
        "runs": {
            "files": run_files,
            "depth_distribution": {str(k): v for k, v in sorted(depth.items())},
            "two_event_runs": depth.get(2, 0),
            "runs_with_admissible_evidence": runs_with_evidence,
        },
        "events_by_action": dict(actions.most_common()),
        "outcomes_by_state": dict(outcomes.most_common()),
        "malformed_lines": malformed,
        "yield": {
            # The ratios that matter (never optimize raw branch/claim counts):
            "evidence_per_100_branches": _per_100(evidence, branches),
            "evidence_per_100_claims": _per_100(evidence, claims),
            "evidence_per_100_model_exchanges": _per_100(evidence, exchanges),
            "claims_per_100_model_exchanges": _per_100(claims, exchanges),
            "progress_outcomes": progress_outcomes,
            "salvaged_supported_claims": salvaged_claims,
        },
        "note": (
            "diagnostics for search-allocation decisions only — never a truth, "
            "release, or calibration authority; branch/claim counts are "
            "denominators, not targets"
        ),
    }
