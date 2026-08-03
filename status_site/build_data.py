"""Build the public EGMRA status snapshot without publishing credentials.

Usage (from the repository root):

    source egmra.keys.sh
    .venv/bin/python status_site/build_data.py

The output is a static JSON snapshot.  It reads Neon for current assignments,
then joins local outcome ledgers, append-only event logs, exchange-cache
metadata, and quarantined Aristotle artifacts.  It never emits prompts,
responses, credentials, signatures, or full local paths.
"""

from __future__ import annotations

import collections
import glob
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg

from egmra.corpus.sources import from_erdos_number


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "status_site"
CAMPAIGN = os.environ.get("EGMRA_STATUS_CAMPAIGN", "shared-current-v1")
GITHUB_BRANCH = "audit/egmra-independent-remediation-20260713"
GITHUB_ROOT = "https://github.com/erichou1/erdos-open-problems"


def _json_lines(path: Path):
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                yield row
    except OSError:
        return


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _problem_number(problem_id: str) -> int | None:
    match = re.fullmatch(r"erdos-(\d+)", str(problem_id))
    return int(match.group(1)) if match else None


def _event_summary(path: Path) -> dict[str, Any] | None:
    events = list(_json_lines(path))
    if not events:
        return None
    run_id = str(events[0].get("run_id") or path.stem)
    problem_id = next((str(item) for event in events
                       for item in event.get("object_ids", ())
                       if str(item).startswith("erdos-")), "")
    if not problem_id:
        match = re.search(r"(erdos-\d+)", run_id)
        problem_id = match.group(1) if match else ""
    if not problem_id:
        return None
    actions = collections.Counter(str(e.get("action", "UNKNOWN")) for e in events)
    families: list[str] = []
    chatgpt: list[dict[str, str]] = []
    timeline: list[dict[str, Any]] = []
    for index, event in enumerate(events, start=1):
        payload = event.get("payload") or {}
        conversation_url = payload.get("conversation_url")
        safe_url = (
            conversation_url
            if isinstance(conversation_url, str)
            and conversation_url.startswith("https://chatgpt.com/")
            else None
        )
        timeline.append({
            "sequence": event.get("sequence", index),
            "action": str(event.get("action", "UNKNOWN")),
            "timestamp": event.get("timestamp"),
            "description": str(
                event.get("human_readable_reason")
                or event.get("reason_code") or ""
            )[:240],
            "stage": str(payload.get("stage", ""))[:120] or None,
            "conversation_url": safe_url,
        })
        if event.get("action") == "BRANCH_OPENED":
            for object_id in event.get("object_ids", ()):
                value = str(object_id)
                if value and not value.startswith("erdos-") and value not in families:
                    families.append(value)
        if event.get("action") == "MODEL_EXCHANGE_RECORDED":
            if safe_url:
                chatgpt.append({
                    "stage": str(payload.get("stage", "exchange")),
                    "url": safe_url,
                })
    return {
        "run_id": run_id,
        "problem_id": problem_id,
        "started_at": events[0].get("timestamp"),
        "updated_at": events[-1].get("timestamp"),
        "event_count": len(events),
        "families": families,
        "claims_proposed": actions["CLAIM_PROPOSED"],
        "evidence_attached": actions["EVIDENCE_ATTACHED"],
        "claims_promoted": actions["CLAIM_PROMOTED"],
        "packet_reentries": actions["PACKET_REENTRY"],
        "formal_correspondences": actions["FORMAL_CORRESPONDENCE_ISSUED"],
        "chatgpt": chatgpt,
        "events": timeline,
        "actions": dict(sorted(actions.items())),
    }


def _exchange_summary(problem_id: str) -> list[dict[str, Any]]:
    directory = ROOT / "egmra_campaigns" / "ckpts-shared" / problem_id / "exchanges"
    rows: list[dict[str, Any]] = []
    if not directory.is_dir():
        return rows
    for path in sorted(directory.glob("*.json"), key=lambda item: item.stat().st_mtime,
                       reverse=True)[:80]:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        model = record.get("model") if isinstance(record.get("model"), dict) else {}
        url = record.get("conversation_url")
        rows.append({
            "stage": str(record.get("stage", "exchange")),
            "model": str(model.get("model", "ChatGPT browser")),
            "provider": str(model.get("provider", "openai")),
            "prompt_hash": str(record.get("prompt_hash", ""))[:16],
            "response_hash": str(record.get("response_hash", ""))[:16],
            "conversation_url": (
                url if isinstance(url, str) and url.startswith("https://chatgpt.com/")
                else None
            ),
        })
    return rows


def _aristotle_artifacts() -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    artifacts: list[dict[str, Any]] = []
    by_problem: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    pattern = ROOT / "egmra_quarantine" / "formalize_campaign"
    for path_string in glob.glob(str(pattern / "**" / "AristotleProject.lean"), recursive=True):
        path = Path(path_string)
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
            relative = path.relative_to(ROOT).as_posix()
        except OSError:
            continue
        parts = relative.split("/")
        worker = next((part for part in parts if re.fullmatch(r"w\d+", part)), "")
        session = next((part for part in parts
                        if re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", part)), "")
        declarations = re.findall(
            r"^\s*(?:theorem|lemma|def)\s+([A-Za-z_][A-Za-z0-9_']*)",
            source, flags=re.MULTILINE,
        )[:12]
        numbers = {int(number) for number in re.findall(r"erdos[_-]?(\d+)", source, re.I)}
        linked_by = "Lean declaration names problem" if numbers else None
        if session:
            session_dir = next(
                (parent for parent in path.parents if parent.name == session),
                None,
            )
            sidecar = session_dir / "egmra-artifact-link.json" if session_dir else None
            if sidecar is not None and sidecar.is_file() and not sidecar.is_symlink():
                try:
                    link = json.loads(sidecar.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    link = {}
                linked_problem = str(link.get("problem_id", ""))
                linked_number = _problem_number(linked_problem)
                if linked_number is not None:
                    numbers.add(linked_number)
                    linked_by = "EGMRA submission metadata"
        numbers = sorted(numbers)
        row = {
            "artifact_id": session or path.parent.name,
            "worker": worker or None,
            "session": session or None,
            "bytes": path.stat().st_size,
            "declarations": declarations,
            "problem_numbers": numbers,
            "linked_by": linked_by,
            "status": "proof draft — not yet verified",
            "source_preview": source[:5000],
        }
        artifacts.append(row)
        for number in numbers:
            by_problem[f"erdos-{number}"].append(row)
    artifacts.sort(key=lambda row: (row["worker"] or "", row["artifact_id"]))
    return artifacts, by_problem


def _outcomes() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in (ROOT / "egmra_outcomes").glob("*.jsonl"):
        machine = path.stem
        for row in _json_lines(path):
            run_id = str(row.get("run_id", ""))
            if run_id:
                rows[run_id] = {**row, "machine": machine}
    return rows


def build() -> dict[str, Any]:
    dsn = os.environ.get("EGMRA_POSTGRES_DSN")
    if not dsn:
        raise RuntimeError("EGMRA_POSTGRES_DSN is required (source egmra.keys.sh)")
    columns = (
        "problem_id", "status", "attempts", "worker", "result_state",
        "lease_expires_at", "updated_at", "campaign",
    )
    with psycopg.connect(dsn) as connection:
        result = connection.execute(
            "SELECT problem_id, status, attempts, worker, result_state, "
            "lease_expires_at, updated_at, campaign "
            "FROM problem_status WHERE campaign=%s",
            (CAMPAIGN,),
        ).fetchall()
    assignments = {
        str(dict(zip(columns, row))["problem_id"]): dict(zip(columns, row))
        for row in result
    }

    outcomes = _outcomes()
    run_summaries: dict[str, dict[str, Any]] = {}
    for path in (ROOT / "egmra_runs").glob("*.jsonl"):
        summary = _event_summary(path)
        if summary:
            run_summaries[summary["run_id"]] = summary
    for run_id, outcome in outcomes.items():
        summary = run_summaries.setdefault(run_id, {
            "run_id": run_id,
            "problem_id": str(outcome.get("problem_id", "")),
            "started_at": None,
            "updated_at": outcome.get("recorded_at"),
            "event_count": int(outcome.get("event_count", 0)),
            "families": [], "claims_proposed": 0, "evidence_attached": 0,
            "claims_promoted": 0, "packet_reentries": 0,
            "formal_correspondences": 0, "chatgpt": [], "actions": {},
            "events": [],
        })
        summary.update({
            "machine": outcome.get("machine"),
            "state": outcome.get("public_state"),
            "outcome": outcome.get("outcome"),
            "released": bool(outcome.get("released")),
            "recorded_at": outcome.get("recorded_at"),
            "salvage": outcome.get("salvage") or {},
        })

    artifacts, artifacts_by_problem = _aristotle_artifacts()
    problem_ids = sorted(assignments, key=lambda pid: _problem_number(pid) or 10**9)
    problems: list[dict[str, Any]] = []
    for problem_id in problem_ids:
        assignment = assignments[problem_id]
        number = _problem_number(problem_id)
        try:
            statement = from_erdos_number(number).display_statement if number else ""
        except Exception:
            statement = "Statement unavailable in this snapshot."
        runs = [row for row in run_summaries.values() if row["problem_id"] == problem_id]
        runs.sort(key=lambda row: str(row.get("updated_at") or row.get("recorded_at") or ""),
                  reverse=True)
        exchanges = _exchange_summary(problem_id)
        latest_state = next((str(run.get("state")) for run in runs if run.get("state")), None)
        problems.append({
            "problem_id": problem_id,
            "number": number,
            "statement": statement,
            "status": assignment.get("status"),
            "attempts": int(assignment.get("attempts") or 0),
            "worker": assignment.get("worker") or None,
            "result_state": assignment.get("result_state") or None,
            "lease_expires_at": _iso(assignment.get("lease_expires_at")),
            "updated_at": _iso(assignment.get("updated_at")),
            "latest_state": latest_state,
            "run_count": len(runs),
            "chatgpt_run_count": len(exchanges),
            "runs": runs,
            "exchanges": exchanges,
            "aristotle": artifacts_by_problem.get(problem_id, []),
            "erdos_page": f"https://www.erdosproblems.com/{number}" if number else None,
        })

    statuses = collections.Counter(str(problem["status"]) for problem in problems)
    states = collections.Counter(str(problem["latest_state"]) for problem in problems
                                 if problem.get("latest_state"))
    workers = [{"worker": problem["worker"], "problem_id": problem["problem_id"],
                "number": problem["number"], "status": problem["status"]}
               for problem in problems if problem.get("worker")]
    linked_artifacts = sum(bool(artifact["problem_numbers"]) for artifact in artifacts)
    recorded_chatgpt_links = sum(
        len(run.get("chatgpt", ()))
        for problem in problems for run in problem["runs"]
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "campaign": CAMPAIGN,
        "summary": {
            "total": len(problems),
            "by_status": dict(sorted(statuses.items())),
            "by_latest_state": dict(sorted(states.items())),
            "total_runs": sum(problem["run_count"] for problem in problems),
            "problems_with_chatgpt_exchanges": sum(
                bool(problem["exchanges"]) for problem in problems),
            "chatgpt_links_recorded": recorded_chatgpt_links,
            "aristotle_artifacts": len(artifacts),
            "aristotle_linked": linked_artifacts,
            "aristotle_unlinked": len(artifacts) - linked_artifacts,
        },
        "workers": workers,
        "problems": problems,
        "aristotle_artifacts": artifacts,
        "source": {
            "repository": GITHUB_ROOT,
            "branch": GITHUB_BRANCH,
            "snapshot_note": "Static public snapshot; credentials and raw model text are excluded.",
        },
    }


if __name__ == "__main__":
    SITE_ROOT.mkdir(parents=True, exist_ok=True)
    output = SITE_ROOT / "data.json"
    payload = build()
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
                      encoding="utf-8")
    print(f"wrote {output.relative_to(ROOT)}")
    print(json.dumps(payload["summary"], indent=2))