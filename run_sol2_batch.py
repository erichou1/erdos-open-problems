#!/usr/bin/env python3
"""Sequentially run the verified pipeline over a problem range into an artifacts dir.

Only one Chromium may use the shared profile at a time, so problems are run
strictly one at a time. Progress is tracked with marker files under
<artifacts>/.done/, so the batch is resumable: already-finished problems are
skipped, and a failed problem is left unmarked for a later retry.

Optionally waits for an already-running pipeline process to exit first (so it can
be launched while a manual validation run is still finishing).

Usage:
  .venv/bin/python -u run_sol2_batch.py --min 601 --max 899 [--wait-pid 50029]
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

import erdos_common as C
from erdos_searcher import (
    canonical_problem_run_inputs,
    find_latest_canonical_snapshot,
    load_canonical_corpus,
    normalized_budget_config,
)
from run_status import has_verified_result, problem_disposition


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def should_skip_problem(
    artifacts: Path, problem_number: int, marker: Path, *,
    expected_run_contract_id: str | None = None,
) -> bool:
    """A legacy marker is advisory; only a verified manifest makes it skippable."""
    return marker.exists() and has_verified_result(
        artifacts, problem_number,
        expected_run_contract_id=expected_run_contract_id,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--category", default="open")
    ap.add_argument("--min", type=int, default=None)
    ap.add_argument("--max", type=int, default=None)
    ap.add_argument("--problems", default="",
                    help="Explicit comma/space-separated problem numbers, in "
                         "priority order; overrides --min/--max")
    ap.add_argument("--artifacts", default="proof_runs_sol2")
    ap.add_argument("--triage", default="triage")
    ap.add_argument("--max-revisions", type=int, default=2)
    ap.add_argument("--max-attempts", type=int, default=8)
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--stage-timeout", type=float, default=1800)
    ap.add_argument("--backoff", type=float, default=15.0,
                    help="Initial seconds to wait after a rate-limit alert")
    ap.add_argument("--max-backoff", type=float, default=120.0,
                    help="Maximum adaptive rate-limit backoff in seconds")
    ap.add_argument("--request-spacing", type=float, default=12.0,
                    help="Minimum seconds between any two worker requests")
    ap.add_argument("--headless", action="store_true",
                    help="Run the browser without a visible window")
    ap.add_argument("--wait-pid", type=int, default=0,
                    help="Wait for this pid to exit before starting")
    ap.add_argument(
        "--force-legacy", action="store_true",
        help="Run the RETIRED legacy batch anyway. The supported production path "
             "is `egmra campaign --triage <triage-dir>` (verified EGMRA pipeline).",
    )
    args = ap.parse_args()
    if not args.force_legacy:
        ap.error(
            "run_sol2_batch.py is RETIRED: it batch-drives the legacy "
            "run_verified_pipeline/ProofPipeline, which can never emit a "
            "ReleaseCertificate. Use the single verified pipeline instead:\n"
            "  egmra campaign --triage <triage-dir> --workers N --provider browser "
            "--policy <signed-policy> --outcome-ledger <path>\n"
            "Pass --force-legacy only to run the retired batch deliberately."
        )
    if "unrecorded" in args.model_id.lower() or not args.model_id.strip():
        ap.error("--model-id must be the exact recorded UI model identity")

    artifacts = Path(args.artifacts)
    triage_dir = Path(args.triage)
    if not triage_dir.is_absolute():
        triage_dir = C.REPO_DIR / triage_dir
    budget_config = normalized_budget_config(
        max_revisions=args.max_revisions,
        stage_timeout_s=args.stage_timeout,
        initial_backoff_s=args.backoff,
        max_backoff_s=args.max_backoff,
        request_spacing_s=args.request_spacing,
        max_attempts=args.max_attempts,
        browser_headless=args.headless,
    )
    canonical_snapshot = find_latest_canonical_snapshot(triage_dir)
    canonical_sources = load_canonical_corpus(canonical_snapshot)
    done_dir = artifacts / ".done"
    done_dir.mkdir(parents=True, exist_ok=True)

    if args.wait_pid and pid_alive(args.wait_pid):
        print(f"[batch] waiting for pid {args.wait_pid} to finish...", flush=True)
        while pid_alive(args.wait_pid):
            time.sleep(30)
        print("[batch] prior run finished; starting.", flush=True)

    files = C.get_problem_files(args.category)
    available = {C.problem_number(f) for f in files}
    if args.problems.strip():
        requested = [int(tok) for tok in args.problems.replace(",", " ").split()]
        nums = [n for n in requested if n in available]
        missing = [n for n in requested if n not in available]
        if missing:
            print(f"[batch] skipping {len(missing)} unknown problems: {missing}",
                  flush=True)
        print(f"[batch] {len(nums)} explicit problems queued", flush=True)
    elif args.min is not None and args.max is not None:
        nums = [n for n in sorted(available) if args.min <= n <= args.max]
        print(f"[batch] {len(nums)} problems in [{args.min},{args.max}]", flush=True)
    else:
        ap.error("provide --problems or both --min and --max")

    for num in nums:
        try:
            run_inputs = canonical_problem_run_inputs(
                C.REPO_DIR,
                triage_dir,
                num,
                model_portfolio=args.model_id,
                budget_config=budget_config,
                canonical_snapshot=canonical_snapshot,
                canonical_sources=canonical_sources,
            )
        except Exception as exc:
            print(f"[batch] #{num}: exact context unavailable ({exc}); not started.",
                  flush=True)
            continue
        expected_run_contract_id = run_inputs["run_contract_id"]
        marker = done_dir / f"problem_{num}"
        if should_skip_problem(
            artifacts, num, marker,
            expected_run_contract_id=expected_run_contract_id,
        ):
            print(f"[batch] #{num}: verified result already present, skipping.", flush=True)
            continue
        if marker.exists():
            print(f"[batch] #{num}: ignoring stale non-verified done marker.", flush=True)

        print(f"[batch] === #{num}: starting verified run ===", flush=True)
        cmd = [
            sys.executable, "-u", "run_verified_pipeline.py",
            "--problem", str(num),
            "--category", args.category,
            "--artifacts", args.artifacts,
            "--triage", args.triage,
            "--max-revisions", str(args.max_revisions),
            "--max-attempts", str(args.max_attempts),
            "--stage-timeout", str(args.stage_timeout),
            "--backoff", str(args.backoff),
            "--max-backoff", str(args.max_backoff),
            "--request-spacing", str(args.request_spacing),
            "--model-id", args.model_id,
            "--force-legacy",
        ]
        if args.headless:
            cmd.append("--headless")
        returncode = subprocess.run(cmd).returncode

        if returncode == 0 and has_verified_result(
            artifacts, num,
            expected_run_contract_id=expected_run_contract_id,
        ):
            marker.write_text("verified\n", encoding="utf-8")
            print(f"[batch] #{num}: verified; completion marker written.", flush=True)
        elif returncode == 0:
            disposition = problem_disposition(artifacts, num)
            print(f"[batch] #{num}: run finished as "
                  f"{disposition['outcome_class']}; left eligible for future policy.",
                  flush=True)
        else:
            print(f"[batch] #{num}: FAILED (exit {returncode}); "
                  "left unmarked for retry.", flush=True)
            time.sleep(30)  # brief cooldown after a failure

    print("[batch] complete.", flush=True)


if __name__ == "__main__":
    main()
