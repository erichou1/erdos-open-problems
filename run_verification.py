#!/usr/bin/env python3
"""Automated formal-verification pass: submit awaiting runs to Aristotle.

This is deliberately decoupled from the browser proof-search workers: Aristotle
submits block for a long time, so running verification in the same loop would
stall proof generation. This scanner finds runs whose deterministic gate is
`awaiting_external_evidence` (reviews passed, only external evidence missing) and,
for each, runs the Aristotle verifier + local Lean kernel check and re-applies
the gate.

Usage:
  .venv/bin/python run_verification.py --artifacts proof_runs_sol2 \\
      --require-kernel --publish
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_status import has_verified_result
from run_status import _read_bounded_regular
from aristotle_verifier import verify_run
from egmra.policy import PolicyEnforcer, load_policy

AWAITING = "awaiting_external_evidence"


def _run_dirs(artifacts: Path):
    root = Path(artifacts)
    if root.is_symlink() or not root.is_dir():
        return
    for problem_dir in sorted(root.glob("problem_*")):
        if problem_dir.is_symlink() or not problem_dir.is_dir():
            continue
        for run_dir in sorted(
            p for p in problem_dir.iterdir()
            if not p.is_symlink() and p.is_dir()
        ):
            yield run_dir


def find_awaiting_runs(artifacts: Path) -> list[Path]:
    """Runs whose gate is awaiting external evidence and not already verified."""
    awaiting: list[Path] = []
    for run_dir in _run_dirs(Path(artifacts)):
        try:
            manifest = json.loads(_read_bounded_regular(
                run_dir / "manifest.json", max_bytes=4_000_000,
            ).decode("utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            continue
        gate_status = str(manifest.get("gate", {}).get("status", ""))
        problem = manifest.get("problem_number")
        if (gate_status == AWAITING and isinstance(problem, int)
                and run_dir.parent.name == f"problem_{problem}"
                and not has_verified_result(Path(artifacts), problem)):
            awaiting.append(run_dir)
    return awaiting


def verify_awaiting(
    artifacts: Path, *, triage_dir: Path | None = None, category: str = "open",
    require_kernel: bool = False, publish: bool = False, limit: int = 0,
    verify=verify_run, client=None, enforcer=None,
) -> list[tuple[Path, str]]:
    """Run the verifier on each awaiting run; ``verify`` is injectable for tests."""
    artifacts = Path(artifacts)
    runs = find_awaiting_runs(artifacts)
    if limit:
        runs = runs[:limit]
    results: list[tuple[Path, str]] = []
    for run_dir in runs:
        try:
            result, _evidence, promoted = verify(
                run_dir, client=client, promote_result=True, publish=publish,
                triage_dir=triage_dir, category=category, require_kernel=require_kernel,
                enforcer=enforcer,
            )
            status = promoted.gate.status if promoted is not None else "no_promote"
            print(f"[verify] {run_dir.parent.name}/{run_dir.name}: "
                  f"aristotle_verified={result.verified} "
                  f"method={result.verification_method} gate={status}", flush=True)
            results.append((run_dir, status))
        except Exception as exc:  # one bad run must not stop the pass
            print(f"[verify] {run_dir}: FAILED ({exc})", flush=True)
            results.append((run_dir, f"error: {exc}"))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, default=Path("proof_runs_sol2"))
    parser.add_argument("--triage", type=Path, default=Path("triage"))
    parser.add_argument("--category", default="open")
    parser.add_argument("--require-kernel", action="store_true",
                        help="only promote proofs re-checked by the local Lean kernel")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="0 = all awaiting runs")
    parser.add_argument(
        "--policy", type=Path, required=True,
        help="signed policy enabling external prover routing and evidence generation",
    )
    args = parser.parse_args()
    enforcer = PolicyEnforcer(load_policy(args.policy))
    results = verify_awaiting(
        args.artifacts, triage_dir=args.triage, category=args.category,
        require_kernel=args.require_kernel, publish=args.publish, limit=args.limit,
        enforcer=enforcer,
    )
    promoted = sum(1 for _, status in results if status.startswith("verified_"))
    print(f"[verify] done: {len(results)} runs, {promoted} promoted.", flush=True)


if __name__ == "__main__":
    main()
