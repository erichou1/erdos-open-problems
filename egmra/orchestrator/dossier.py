"""Per-problem research dossier: durable learning across campaign processes.

agentic-erdos's core operational discipline is that every problem is a durable
object revisited over months — each visit starts from everything already
learned. EGMRA's in-process ``LongTermMemory`` gives campaigns that within one
process; this module persists the SEARCH-relevant slice (approach-family
outcomes, failed approaches, terminal states) to a small JSON file under the
problem's checkpoint directory, so the next campaign process — or a fresh
pass@k attempt with a salted exchange cache — seeds its controller posteriors,
family registry, and failed-approach memory instead of re-deriving them.

Trust boundary: a dossier is search guidance only. It never carries evidence,
claims, or verdicts; a corrupted or hostile dossier can bias prompts and
allocation, never truth. Loading fails OPEN to empty (symlink, oversize,
malformed → {}), and writes are atomic with mode 0600.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

_SCHEMA_VERSION = 1
_MAX_BYTES = 1_000_000
_MAX_FAMILY_OUTCOMES = 48
_MAX_FAILED_APPROACHES = 24
_MAX_STATES = 24


def load_dossier(path: Path | None) -> dict[str, Any]:
    """Read a dossier, failing OPEN to {} on any degenerate state."""
    if path is None:
        return {}
    path = Path(path)
    try:
        if path.is_symlink() or not path.is_file():
            return {}
        if path.stat().st_size > _MAX_BYTES:
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("schema_version") != _SCHEMA_VERSION:
            return {}
        return data
    except (OSError, ValueError, json.JSONDecodeError):
        return {}


def seed_from_dossier(dossier: dict[str, Any], *, memory: Any, worker: Any,
                      problem_id: str) -> int:
    """Replay a dossier into the in-process memory + worker (idempotent).

    Family outcomes are admitted as ``branch_family_outcome`` records flagged
    ``from_dossier`` — the existing controller seeding and family-registry
    rendering pick them up with zero extra plumbing.  Seeding is skipped when
    the process already holds dossier records for this problem (a campaign
    retry within one process must not double-count attempts).
    """
    if not dossier or dossier.get("problem_id") != problem_id:
        return 0
    for record in getattr(memory.procedural, "records", ()):
        if isinstance(record, dict) and record.get("from_dossier") \
                and record.get("problem_id") == problem_id:
            return 0
    seeded = 0
    for outcome in list(dossier.get("family_outcomes", ()))[:_MAX_FAMILY_OUTCOMES]:
        if not isinstance(outcome, dict):
            continue
        family = str(outcome.get("branch_family", "")).strip()
        if not family:
            continue
        memory.procedural.admit({
            "kind": "branch_family_outcome",
            "problem_id": problem_id,
            "branch_family": family,
            "supported": bool(outcome.get("supported")),
            "cross_problem_usable": True,
            "from_dossier": True,
        })
        seeded += 1
    failed = getattr(worker, "failed_approach_memory", None)
    if failed is not None:
        for entry in list(dossier.get("failed_approaches", ()))[:_MAX_FAILED_APPROACHES]:
            text = str(entry).strip()[:200]
            if text and text not in failed:
                failed.append(text)
        del failed[:-_MAX_FAILED_APPROACHES]
    return seeded


def harvest_for_dossier(memory: Any, worker: Any, problem_id: str) -> dict[str, Any]:
    """Extract THIS process's genuine learning for the problem.

    Dossier-seeded records are excluded so repeated harvest→seed cycles never
    inflate attempt counts.
    """
    outcomes: list[dict[str, Any]] = []
    for record in getattr(memory.procedural, "records", ()):
        if not isinstance(record, dict) \
                or record.get("kind") != "branch_family_outcome" \
                or record.get("problem_id") != problem_id \
                or record.get("from_dossier"):
            continue
        family = str(record.get("branch_family", "")).strip()
        if family:
            outcomes.append({"branch_family": family,
                             "supported": bool(record.get("supported"))})
    return {
        "family_outcomes": outcomes,
        "failed_approaches": [
            str(item)[:200]
            for item in getattr(worker, "failed_approach_memory", ())],
    }


def update_dossier(path: Path, *, problem_id: str, public_state: str,
                   harvest: dict[str, Any]) -> dict[str, Any]:
    """Merge new learning into the stored dossier and write it atomically.

    Persistence is an ops aid: an OSError is swallowed by the CALLER (fail
    open), and this function never raises on merge content.
    """
    path = Path(path)
    stored = load_dossier(path)
    if stored.get("problem_id") != problem_id:
        stored = {}
    family_outcomes = list(stored.get("family_outcomes", ()))
    family_outcomes.extend(harvest.get("family_outcomes", ()))
    failed = list(dict.fromkeys([
        *stored.get("failed_approaches", ()),
        *harvest.get("failed_approaches", ()),
    ]))
    states = list(stored.get("terminal_states", ()))
    if public_state:
        states.append(public_state)
    dossier = {
        "schema_version": _SCHEMA_VERSION,
        "problem_id": problem_id,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "attempts": int(stored.get("attempts", 0)) + 1,
        "family_outcomes": family_outcomes[-_MAX_FAMILY_OUTCOMES:],
        "failed_approaches": failed[-_MAX_FAILED_APPROACHES:],
        "terminal_states": states[-_MAX_STATES:],
    }
    payload = json.dumps(dossier, ensure_ascii=False)
    if len(payload.encode("utf-8")) > _MAX_BYTES:
        return dossier          # never write an oversize file; keep the old one
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    return dossier
