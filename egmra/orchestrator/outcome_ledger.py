"""EGMRA-native outcome ledger for the continuous drainer (single-pipeline).

The legacy searcher ledger (``triage/labels/outcomes.jsonl``) is bound to the
legacy run-contract schema, so the EGMRA loop cannot write it without
fabricating a contract.  This module records EGMRA outcomes in a separate,
append-only JSONL keyed by problem — an honest telemetry trail for the drainer,
never a truth or release authority.

Each record captures only what the EGMRA result already establishes: the
classified public state, the five-gate profile, the run id / event-log head,
and a UTC timestamp.  It carries no probabilities and no promotion authority; it
exists so a continuous campaign has a durable, inspectable outcome history
(audit recommendation R11, EGMRA-native scope).
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def build_outcome_record(
    *, problem_id: str, result: Any, run_id: str, state: str,
    recorded_at: str | None = None,
) -> dict:
    """Shape one honest outcome record from an EGMRA ``ResearchResult``."""
    gates = getattr(result, "gates", None)
    certificate = getattr(result, "certificate", None)
    compiled = getattr(result, "compiled_proof", None)
    graph = getattr(result, "graph", None)
    return {
        "schema_version": SCHEMA_VERSION,
        "problem_id": problem_id,
        "run_id": run_id,
        "recorded_at": recorded_at or _utc_now(),
        "public_state": state,
        "outcome": getattr(result, "outcome", ""),
        "acquired": bool(getattr(result, "acquired", False)),
        # A released certificate is the only signal that a gate profile is
        # authoritative; record it plainly, never inferring more.
        "released": certificate is not None,
        "candidate_assembly_complete": bool(
            compiled is not None and getattr(compiled, "complete", False)
        ),
        "gate_profile": gates.profile() if gates is not None else None,
        "event_count": len(graph.log) if graph is not None else 0,
    }


class EgmraOutcomeLedger:
    """Append-only, per-line JSON outcome log with an advisory file lock."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def record(self, record: dict) -> dict:
        """Append one record atomically; returns the record written."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
        # O_APPEND writes are atomic for a single line below PIPE_BUF on POSIX;
        # an advisory lock additionally serializes concurrent drainer workers.
        fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            try:
                import fcntl

                fcntl.flock(fd, fcntl.LOCK_EX)
            except (ImportError, OSError):
                pass  # advisory only; append remains atomic for one short line
            os.write(fd, line.encode("utf-8"))
        finally:
            os.close(fd)
        return record

    def records(self) -> list[dict]:
        """All well-formed records, oldest first (malformed lines skipped)."""
        if not self.path.is_file():
            return []
        out: list[dict] = []
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                value = json.loads(raw)
            except ValueError:
                continue
            if isinstance(value, dict):
                out.append(value)
        return out

    def latest_by_problem(self) -> dict[str, dict]:
        """The most recently recorded outcome per problem id."""
        latest: dict[str, dict] = {}
        for record in self.records():
            pid = record.get("problem_id")
            if isinstance(pid, str):
                latest[pid] = record
        return latest
