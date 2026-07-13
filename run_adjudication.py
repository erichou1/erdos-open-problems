#!/usr/bin/env python3
"""Decoupled distinct-model adjudication pass (DeepSeek).

DeepSeek allows only one in-flight message and one browser profile, so the
distinct adjudicator cannot run inside every parallel ChatGPT worker. This pass
runs as a SINGLE process: it scans the shared artifact tree for runs the ChatGPT
fleet left at ``awaiting_external_evidence`` (reviews passed inline, only trusted
evidence missing) and, one at a time, re-adjudicates each candidate with a
genuinely different model.

The distinct verdict replaces the same-model adjudicator in the gate, so a
correlated blind spot in the ChatGPT self-review is caught *before* expensive
Aristotle verification is spent on it:

  * DeepSeek agrees  -> gate stays ``awaiting_external_evidence`` (proceed to
    formal verification).
  * DeepSeek dissents -> gate becomes ``candidate_rejected`` (do not spend
    Aristotle; the run is flagged for attention).
  * malformed DeepSeek output -> advisory only; the gate is left untouched.

A kernel-verified formal proof always overrides this signal, so a false dissent
only defers, never permanently blocks, a genuine proof.

Usage (single process, honours DeepSeek's one-at-a-time limit):
  .venv/bin/python run_adjudication.py --artifacts proof_runs_sol2
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from research_state import StatementLock, statement_lock_text
from solver_prompts import ADJUDICATOR_PROMPT_TEMPLATE, OFFLINE_POLICY
from proof_pipeline import REVIEW_MANDATES, _failed_review, _json_object, _review
from verification import (
    GateDecision,
    VerificationEvidence,
    candidate_contract,
    evaluate_gate,
)
from promote_verified_run import load_reviews
from erdos_searcher import write_json
from run_status import has_verified_result

AWAITING = "awaiting_external_evidence"
ADJ_FILE = "deepseek_adjudication.json"
ADJ_STAGE = "deepseek_adjudication"
ONLY_EVIDENCE_MISSING = ("no trusted external or mechanical verification evidence",)


def _run_dirs(artifacts: Path):
    for problem_dir in sorted(Path(artifacts).glob("problem_*")):
        if not problem_dir.is_dir():
            continue
        for run_dir in sorted(p for p in problem_dir.iterdir() if p.is_dir()):
            yield run_dir


def find_adjudicatable_runs(artifacts: Path) -> list[Path]:
    """Awaiting runs not yet distinct-adjudicated and not already verified."""
    out: list[Path] = []
    artifacts = Path(artifacts)
    for run_dir in _run_dirs(artifacts):
        if (run_dir / ADJ_FILE).exists():
            continue
        try:
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        gate_status = str(manifest.get("gate", {}).get("status", ""))
        problem = manifest.get("problem_number")
        if (gate_status == AWAITING and isinstance(problem, int)
                and not has_verified_result(artifacts, problem)):
            out.append(run_dir)
    return out


# ── prompt reconstruction from persisted artifacts ───────────────────────────

def _latest_attempt_dir(run_dir: Path) -> Path | None:
    attempts = [d for d in run_dir.glob("attempt_*") if d.is_dir()]
    if not attempts:
        return None
    return max(attempts, key=lambda d: int(d.name.rsplit("_", 1)[-1]))


def _graph_text(run_dir: Path) -> str:
    revisions = sorted(
        run_dir.glob("subgoal_graph_revision_*.json"),
        key=lambda p: int(p.stem.rsplit("_", 1)[-1]),
    )
    source = revisions[-1] if revisions else (run_dir / "subgoal_graph.json")
    try:
        return source.read_text(encoding="utf-8")
    except OSError:
        return "{}"


def _raw_reviews(attempt_dir: Path | None) -> str:
    if attempt_dir is None:
        return ""
    parts = []
    for role in REVIEW_MANDATES:  # deterministic order matches the inline pass
        review_file = attempt_dir / f"review_{role}.json"
        if review_file.is_file():
            parts.append(review_file.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def _statement_lock_text(run_dir: Path) -> str:
    data = json.loads((run_dir / "statement_lock.json").read_text(encoding="utf-8"))
    lock = StatementLock(
        original_statement=str(data["original_statement"]),
        sha256=str(data["sha256"]),
        acceptance_criteria=tuple(data.get("acceptance_criteria", ())),
    )
    return statement_lock_text(lock)


def build_adjudicator_prompt(run_dir: Path) -> str:
    """Rebuild the exact adjudicator prompt the inline stage would have used."""
    candidate = (run_dir / "candidate.md").read_text(encoding="utf-8")
    return ADJUDICATOR_PROMPT_TEMPLATE.format(
        offline=OFFLINE_POLICY,
        statement_lock=_statement_lock_text(run_dir),
        subgoal_graph=_graph_text(run_dir),
        candidate=candidate,
        reviews=_raw_reviews(_latest_attempt_dir(run_dir)),
    )


# ── one run ──────────────────────────────────────────────────────────────────

def _evidence_from_manifest(manifest: dict) -> tuple[VerificationEvidence, ...]:
    return tuple(
        VerificationEvidence(**item)
        for item in manifest.get("verification_evidence", [])
    )


def adjudicate_run(run_dir: Path, runner, *, apply_gate: bool = True) -> dict:
    """Re-adjudicate one run with ``runner`` (a distinct model) and record it."""
    run_dir = Path(run_dir)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    prompt = build_adjudicator_prompt(run_dir)
    raw = runner.run(prompt, stage=ADJ_STAGE, isolated=True)
    context_id = runner.context_id(ADJ_STAGE)

    malformed = False
    try:
        review = _review(
            _json_object(raw), reviewer_id="adjudicator-deepseek",
            expected_role="adjudicator", context_id=context_id,
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        review = _failed_review(
            reviewer_id="adjudicator-deepseek", expected_role="adjudicator",
            context_id=context_id, error=error,
        )
        malformed = True

    agrees = (
        not malformed
        and review.verdict.lower() == "pass"
        and not review.open_gaps
        and not review.unchecked_imports
        and not review.material_errors
    )

    gate_before = str(manifest.get("gate", {}).get("status", ""))
    gate_after = gate_before
    # A malformed distinct verdict is advisory only: never let DeepSeek's own
    # formatting failure reject an otherwise-passing candidate.
    if apply_gate and not malformed:
        swapped = [
            record for record in manifest["reviews"]
            if record.get("reviewer_role") != "adjudicator"
        ]
        swapped.append(asdict(review))
        candidate = (run_dir / "candidate.md").read_text(encoding="utf-8")
        decision = evaluate_gate(
            manifest["candidate_outcome"],
            load_reviews(swapped),
            expected_statement_sha256=manifest["statement_sha256"],
            candidate_contract=candidate_contract(candidate),
            verification_evidence=_evidence_from_manifest(manifest),
            expected_candidate_sha256=hashlib.sha256(
                candidate.encode("utf-8")
            ).hexdigest(),
        )
        # Mirror ProofPipeline.solve: "reviews pass, only evidence missing" is
        # the awaiting state, not a rejection.
        if decision.reasons == ONLY_EVIDENCE_MISSING:
            decision = GateDecision(AWAITING, decision.reasons)
        manifest["reviews"] = swapped
        manifest["gate"] = asdict(decision)
        manifest["adjudicator_distinct_model"] = True
        gate_after = decision.status

    record = {
        "model": "deepseek",
        "reviewer_role": "adjudicator",
        "agrees": agrees,
        "malformed": malformed,
        "verdict": review.verdict,
        "outcome": review.adjudicated_outcome,
        "context_id": context_id,
        "open_gaps": list(review.open_gaps),
        "unchecked_imports": list(review.unchecked_imports),
        "material_errors": list(review.material_errors),
        "gate_before": gate_before,
        "gate_after": gate_after,
        "adjudicated_at": datetime.now(timezone.utc).isoformat(),
        "raw": raw,
    }
    manifest["distinct_adjudicator"] = {
        "model": "deepseek",
        "agrees": agrees,
        "malformed": malformed,
        "verdict": review.verdict,
        "context_id": context_id,
        "gate_before": gate_before,
        "gate_after": gate_after,
        "adjudicated_at": record["adjudicated_at"],
    }
    write_json(manifest_path, manifest)
    write_json(run_dir / ADJ_FILE, record)
    return record


def adjudicate_awaiting(
    artifacts: Path, runner, *, limit: int = 0, apply_gate: bool = True,
) -> list[tuple[Path, dict | str]]:
    """Serially re-adjudicate every awaiting run (honours one-at-a-time)."""
    runs = find_adjudicatable_runs(Path(artifacts))
    if limit:
        runs = runs[:limit]
    results: list[tuple[Path, dict | str]] = []
    for run_dir in runs:
        try:
            record = adjudicate_run(run_dir, runner, apply_gate=apply_gate)
            print(f"[adjudicate] {run_dir.parent.name}/{run_dir.name}: "
                  f"deepseek agrees={record['agrees']} "
                  f"malformed={record['malformed']} gate={record['gate_after']}",
                  flush=True)
            results.append((run_dir, record))
        except Exception as exc:  # one bad run must not stop the pass
            print(f"[adjudicate] {run_dir}: FAILED ({exc})", flush=True)
            results.append((run_dir, f"error: {exc}"))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, default=Path("proof_runs_sol2"))
    parser.add_argument("--limit", type=int, default=0, help="0 = all awaiting runs")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--stage-timeout", type=float, default=1800)
    parser.add_argument("--backoff", type=float, default=15.0)
    parser.add_argument("--max-backoff", type=float, default=120.0)
    parser.add_argument("--request-spacing", type=float, default=12.0)
    parser.add_argument("--max-attempts", type=int, default=8)
    parser.add_argument(
        "--advisory-only", action="store_true",
        help="record the distinct verdict without changing the gate",
    )
    args = parser.parse_args()

    pending = find_adjudicatable_runs(args.artifacts)
    if not pending:
        print("[adjudicate] no awaiting runs to adjudicate.", flush=True)
        return

    # Imported here so the module is unit-testable without Playwright/DeepSeek.
    import deepseek_common as DS
    from deepseek_runner import DeepSeekBrowserRunner

    with DS.sync_playwright() as playwright:
        browser = DS.launch_browser(playwright, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()
        DS.ensure_logged_in(page)
        runner = DeepSeekBrowserRunner(
            browser, page, timeout_s=args.stage_timeout,
            backoff_s=args.backoff, max_backoff_s=args.max_backoff,
            request_spacing_s=args.request_spacing, max_attempts=args.max_attempts,
        )
        results = adjudicate_awaiting(
            args.artifacts, runner, limit=args.limit,
            apply_gate=not args.advisory_only,
        )

    agreed = sum(1 for _, r in results if isinstance(r, dict) and r["agrees"])
    dissented = sum(
        1 for _, r in results
        if isinstance(r, dict) and not r["agrees"] and not r["malformed"]
    )
    print(f"[adjudicate] done: {len(results)} runs, {agreed} agreed, "
          f"{dissented} dissented.", flush=True)


if __name__ == "__main__":
    main()
