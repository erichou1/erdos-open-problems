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


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--category", default="open")
    ap.add_argument("--min", type=int, required=True)
    ap.add_argument("--max", type=int, required=True)
    ap.add_argument("--artifacts", default="proof_runs_sol2")
    ap.add_argument("--max-revisions", type=int, default=2)
    ap.add_argument("--stage-timeout", type=float, default=1800)
    ap.add_argument("--backoff", type=float, default=180.0,
                    help="Initial seconds to wait after a rate-limit alert")
    ap.add_argument("--max-backoff", type=float, default=1800.0,
                    help="Maximum adaptive rate-limit backoff in seconds")
    ap.add_argument("--headless", action="store_true",
                    help="Run the browser without a visible window")
    ap.add_argument("--wait-pid", type=int, default=0,
                    help="Wait for this pid to exit before starting")
    args = ap.parse_args()

    artifacts = Path(args.artifacts)
    done_dir = artifacts / ".done"
    done_dir.mkdir(parents=True, exist_ok=True)

    if args.wait_pid and pid_alive(args.wait_pid):
        print(f"[batch] waiting for pid {args.wait_pid} to finish...", flush=True)
        while pid_alive(args.wait_pid):
            time.sleep(30)
        print("[batch] prior run finished; starting.", flush=True)

    files = C.get_problem_files(args.category)
    nums = [
        C.problem_number(f)
        for f in files
        if args.min <= C.problem_number(f) <= args.max
    ]
    print(f"[batch] {len(nums)} problems in [{args.min},{args.max}]", flush=True)

    for num in nums:
        marker = done_dir / f"problem_{num}"
        if marker.exists():
            print(f"[batch] #{num}: already done, skipping.", flush=True)
            continue

        print(f"[batch] === #{num}: starting verified run ===", flush=True)
        cmd = [
            sys.executable, "-u", "run_verified_pipeline.py",
            "--problem", str(num),
            "--category", args.category,
            "--artifacts", args.artifacts,
            "--max-revisions", str(args.max_revisions),
            "--stage-timeout", str(args.stage_timeout),
            "--backoff", str(args.backoff),
            "--max-backoff", str(args.max_backoff),
        ]
        if args.headless:
            cmd.append("--headless")
        returncode = subprocess.run(cmd).returncode

        if returncode == 0:
            marker.write_text("ok\n", encoding="utf-8")
            print(f"[batch] #{num}: done.", flush=True)
        else:
            print(f"[batch] #{num}: FAILED (exit {returncode}); "
                  "left unmarked for retry.", flush=True)
            time.sleep(30)  # brief cooldown after a failure

    print("[batch] complete.", flush=True)


if __name__ == "__main__":
    main()
