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
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from egmra.corpus.sources import from_erdos_number
from egmra.orchestrator.campaign import PostgresCampaignStore
from egmra.ranking_queue import QUEUE_FILENAME, load_queue_projection


SITE_ROOT = ROOT / "status_site"
CAMPAIGN = os.environ.get("EGMRA_STATUS_CAMPAIGN", "shared-current-v1")
GITHUB_BRANCH = "audit/egmra-independent-remediation-20260713"
GITHUB_ROOT = "https://github.com/erichou1/erdos-open-problems"


def _solvability_record(number: int) -> dict[str, Any]:
    """Transparent tractability index from the searcher's existing formula.

    This is deliberately NOT called a solution probability. The card values
    are uncalibrated weak priors; the index only ranks which problems best fit
    the current formal/exact-computation pipeline.
    """
    path = ROOT / "triage" / "normalized" / "problem_cards" / f"{number}.json"
    try:
        card = json.loads(path.read_text(encoding="utf-8"))
        posterior = card["posterior"]
        lean = float(posterior["p_lean_verified_exact_target"]["probability"])
        compute = float(
            posterior["p_finite_computational_resolution"]["probability"])
        partial = float(posterior["p_verified_partial_progress"]["probability"])
        novel = float(posterior["p_verified_novel_resolution"]["probability"])
        lean_route = bool(card["probe_summary"]["formal"]["lean_route_available"])
        clear = card["statement"]["ambiguity_status"] == "clear"
        score = 0.5 * lean + 0.4 * compute + 0.15 * lean_route + 0.05 * clear
        signals = list(card.get("strongest_positive_signals", ()))[:4]
        if not signals:
            signals = list(card.get("probe_summary", {}).get("positive_signals", ()))[:4]
        return {
            "available": True,
            "score": round(score, 6),
            # The formula's theoretical maximum is 1.10. This 0-100 index is
            # only a readable normalization of the formula, not probability.
            "index": round(100 * score / 1.10),
            "lean_route_estimate": round(100 * lean),
            "finite_computation_estimate": round(100 * compute),
            "verified_partial_progress_prior": round(100 * partial),
            "verified_novel_resolution_prior": round(100 * novel, 1),
            "lean_route_available": lean_route,
            "statement_clear": clear,
            "calibration": str(posterior.get("calibration_status", "weak prior")),
            "positive_signals": signals,
        }
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return {"available": False, "score": 0.0, "index": 0}


def _progress_record(*, status: str, runs: list[dict[str, Any]],
                     linked_aristotle: int) -> dict[str, Any]:
    """Highest observable research milestone; never mathematical proximity."""
    actions = collections.Counter()
    for run in runs:
        actions.update(run.get("actions") or {})
    released = any(bool(run.get("released")) for run in runs)
    states = {str(run.get("state", "")) for run in runs}
    milestones = [
        (5, "Queued", True, "The problem is in the campaign."),
        (15, "Worker assigned", status == "leased",
         "A worker is currently spending time on it."),
        (20, "Meaning recorded", actions["INTERPRETATION_ADDED"] > 0,
         "The pipeline recorded a precise reading of the statement."),
        (30, "Meaning approved", actions["INTENT_CERTIFICATE_ISSUED"] > 0,
         "The intended interpretation passed its review."),
        (40, "Approaches explored", actions["BRANCH_OPENED"] > 0,
         "At least one proof or counterexample approach was attempted."),
        (50, "Candidate statement found", actions["CLAIM_PROPOSED"] > 0,
         "The run produced a concrete lemma or intermediate claim."),
        (65, "Checked evidence found",
         actions["EVIDENCE_ATTACHED"] > 0 or actions["CLAIM_PROMOTED"] > 0,
         "Independent checking accepted evidence for a claim."),
        (75, "Formal proof draft linked", linked_aristotle > 0,
         "An Aristotle Lean draft is reliably associated with this problem."),
        (88, "Informal and Lean statements matched",
         actions["FORMAL_CORRESPONDENCE_ISSUED"] > 0,
         "A review confirmed that the Lean statement matches the problem."),
        (95, "Formally checked candidate",
         "FORMALLY_VERIFIED_CANDIDATE" in states,
         "A candidate passed the independent formal checker."),
        (100, "Released result", released,
         "All release gates passed."),
    ]
    achieved = [item for item in milestones if item[2]]
    percent, stage, _, explanation = max(achieved, key=lambda item: item[0])
    return {
        "percent": percent,
        "stage": stage,
        "explanation": explanation,
        "disclaimer": (
            "Research milestone, not the probability of solving the problem "
            "and not mathematical distance to a proof."
        ),
        "milestones": [
            {"percent": value, "label": label, "achieved": condition}
            for value, label, condition, _ in milestones
        ],
    }


def _card_statement(root: Path, number: int) -> str:
    path = root / "triage" / "normalized" / "problem_cards" / f"{number}.json"
    try:
        card = json.loads(path.read_text(encoding="utf-8"))
        statement = card["statement"]["normalized"]
        if isinstance(statement, str) and statement.strip():
            return statement.strip()
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        pass
    try:
        return from_erdos_number(number).display_statement
    except Exception:
        return "Statement unavailable in this snapshot."


def build_public_ranking(
    queue: dict,
    problems: list[dict[str, Any]],
    root: Path = ROOT,
) -> list[dict[str, Any]]:
    """Join public campaign progress onto the shared allocation projection."""
    by_number = {
        int(problem["number"]): problem
        for problem in problems
        if isinstance(problem.get("number"), int)
    }
    queued_progress = _progress_record(
        status="pending", runs=[], linked_aristotle=0
    )
    public: list[dict[str, Any]] = []
    for row in queue["allocation_queue"]:
        number = int(row["problem_number"])
        campaign = by_number.get(number, {})
        public.append({
            "problem_id": row["problem_id"],
            "number": number,
            "allocation_rank": row["allocation_rank"],
            "statement": campaign.get("statement") or _card_statement(root, number),
            "status": campaign.get("status", "pending"),
            "worker": campaign.get("worker"),
            "progress": campaign.get("progress") or dict(queued_progress),
            "prize": row["prize"],
            "prize_status": row["prize_status"],
            "literature_coverage_status": row["literature_coverage_status"],
            "base_acquisition_score": row["base_acquisition_score"],
            "literature_adjustment": row["literature_adjustment"],
            "selection_score": row["selection_score"],
            "reason_selected": row["reason_selected"],
        })
    return public


def ranking_method_record(queue: dict, ranking_pipeline: dict) -> dict:
    """Public, credential-free description of the active allocation policy."""
    pipeline_decisions = ranking_pipeline.get("allocation_decisions") or []
    lane_counts = dict(sorted(collections.Counter(
        str(row.get("assigned_lane", "unknown"))
        for row in pipeline_decisions if isinstance(row, dict)
    ).items()))
    return {
        "name": "Evidence-gated five-stage research allocation",
        "formula": (
            "validate → multi-objective scorecard → capability routing → "
            "domain/lane-diverse allocation with 20% protected exploration → audit"
        ),
        "warning": (
            "Transparent search-order indices, not solution probabilities. "
            "Every eligible unpaid problem precedes paid targets."
        ),
        "ranking_pipeline_policy_version": ranking_pipeline.get("policy_version"),
        "ranking_pipeline_content_sha256": ranking_pipeline.get("content_sha256"),
        "ranking_pipeline_stages": [
            {"stage": row.get("stage"), "status": row.get("status")}
            for row in (ranking_pipeline.get("stages") or [])
            if isinstance(row, dict)
        ],
        "ranking_pipeline_lane_counts": lane_counts,
        "ranking_pipeline_stability": ranking_pipeline.get(
            "stability_vs_input_order"),
        "projection_policy_version": queue["projection_policy_version"],
        "projection_content_sha256": queue["projection_content_sha256"],
        "ranking_content_sha256": queue["ranking_content_sha256"],
    }


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
    # One atomic HMAC-verified read for BOTH assignments and machines. Reading
    # assignments from the SQL view and machines from a later store read can
    # straddle a complete→next-lease transition and briefly make one slot look
    # assigned to two problems. One body gives a coherent point-in-time view.
    campaign_store = PostgresCampaignStore(dsn, name=CAMPAIGN)
    try:
        campaign_body = campaign_store.read() or {}
    finally:
        campaign_store.close()
    assignments = {}
    for problem_id, raw in dict(campaign_body.get("assignments") or {}).items():
        record = dict(raw)
        lease_value = float(record.get("lease_expires_at", 0.0) or 0.0)
        assignments[str(problem_id)] = {
            **record,
            "problem_id": str(problem_id),
            "worker": record.get("worker_id") or None,
            "lease_expires_at": (
                datetime.fromtimestamp(lease_value, timezone.utc)
                if lease_value else None),
            "updated_at": None,
            "campaign": campaign_body.get("campaign_id", CAMPAIGN),
        }
    machine_records = dict(campaign_body.get("machines") or {})

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
            "solvability": _solvability_record(number) if number else {
                "available": False, "score": 0.0, "index": 0},
            "erdos_page": f"https://www.erdosproblems.com/{number}" if number else None,
        })

    solvability_ranked = sorted(
        problems,
        key=lambda problem: (
            -float(problem["solvability"].get("score", 0.0)),
            problem["number"],
        ),
    )
    for rank, problem in enumerate(solvability_ranked, start=1):
        problem["solvability"]["rank"] = rank
        problem["progress"] = _progress_record(
            status=str(problem["status"]),
            runs=problem["runs"],
            linked_aristotle=len(problem["aristotle"]),
        )

    statuses = collections.Counter(str(problem["status"]) for problem in problems)
    states = collections.Counter(str(problem["latest_state"]) for problem in problems
                                 if problem.get("latest_state"))
    workers = [{"worker": problem["worker"], "problem_id": problem["problem_id"],
                "number": problem["number"], "status": problem["status"]}
               for problem in problems
               if problem["status"] == "leased" and problem.get("worker")]
    now_ts = datetime.now(timezone.utc).timestamp()
    machines: list[dict[str, Any]] = []
    for machine_id, record in sorted(machine_records.items()):
        heartbeat_at = float(record.get("heartbeat_at", 0.0) or 0.0)
        stopped_at = float(record.get("stopped_at", 0.0) or 0.0)
        age = max(0.0, now_ts - heartbeat_at) if heartbeat_at else None
        if stopped_at:
            activity = "stopped"
        elif age is not None and age <= 120.0:
            activity = "active"
        else:
            activity = "stale"
        worker_ids = [str(value) for value in record.get("worker_ids", ())]
        current_problems = [
            problem["problem_id"] for problem in problems
            if problem["status"] == "leased"
            and problem.get("worker") in worker_ids
        ]
        machines.append({
            "machine_id": machine_id,
            "hostname": record.get("hostname") or machine_id,
            "activity": activity,
            "heartbeat_age_seconds": round(age) if age is not None else None,
            "heartbeat_at": datetime.fromtimestamp(
                heartbeat_at, timezone.utc).isoformat() if heartbeat_at else None,
            "started_at": datetime.fromtimestamp(
                float(record.get("started_at", 0.0)), timezone.utc).isoformat()
                if record.get("started_at") else None,
            "process_id": record.get("process_id"),
            "branch": record.get("branch"),
            "code_commit": record.get("code_commit"),
            "latest_commit": record.get("latest_commit"),
            "version_status": record.get("version_status", "unknown"),
            "worker_slots": len(worker_ids),
            "worker_ids": worker_ids,
            "current_problems": current_problems,
        })
    active_worker_ids = {
        worker_id
        for machine in machines if machine["activity"] == "active"
        for worker_id in machine["worker_ids"]
    }
    for problem in problems:
        if problem["status"] == "leased":
            problem["worker_liveness"] = (
                "active" if problem.get("worker") in active_worker_ids
                else "stale"
            )
        else:
            problem["worker_liveness"] = "not_applicable"
    for worker in workers:
        worker["active"] = worker.get("worker") in active_worker_ids
    linked_artifacts = sum(bool(artifact["problem_numbers"]) for artifact in artifacts)
    recorded_chatgpt_links = sum(
        len(run.get("chatgpt", ()))
        for problem in problems for run in problem["runs"]
    )
    queue = load_queue_projection(
        ROOT / "triage" / "rankings" / QUEUE_FILENAME
    )
    ranking_pipeline: dict[str, Any] = {}
    pipeline_path = ROOT / "triage" / "rankings" / "ranking_pipeline.json"
    try:
        candidate = json.loads(pipeline_path.read_text(encoding="utf-8"))
        if isinstance(candidate, dict) and candidate.get("content_sha256"):
            ranking_pipeline = candidate
    except (OSError, json.JSONDecodeError):
        pass
    public_ranking = build_public_ranking(queue, problems)
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
            "computers_active": sum(
                machine["activity"] == "active" for machine in machines),
            "computers_known": len(machines),
        },
        "machines": machines,
        "workers": workers,
        "problems": problems,
        "aristotle_artifacts": artifacts,
        "ranking": public_ranking,
        "ranking_method": ranking_method_record(queue, ranking_pipeline),
        "source": {
            "repository": GITHUB_ROOT,
            "branch": GITHUB_BRANCH,
            "snapshot_note": "Static public snapshot; credentials and raw model text are excluded.",
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=SITE_ROOT / "data.json",
        help="snapshot path (default: status_site/data.json)",
    )
    args = parser.parse_args()
    SITE_ROOT.mkdir(parents=True, exist_ok=True)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = build()
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
                      encoding="utf-8")
    try:
        display_path = output.relative_to(ROOT)
    except ValueError:
        display_path = output
    print(f"wrote {display_path}")
    print(json.dumps(payload["summary"], indent=2))
