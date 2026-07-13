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
from aristotle_verifier import verify_run

AWAITING = "awaiting_external_evidence"


def _run_dirs(artifacts: Path):
    for problem_dir in sorted(Path(artifacts).glob("problem_*")):
        if not problem_dir.is_dir():
            continue
        for run_dir in sorted(p for p in problem_dir.iterdir() if p.is_dir()):
            yield run_dir


def find_awaiting_runs(artifacts: Path) -> list[Path]:
    """Runs whose gate is awaiting external evidence and not already verified."""
    awaiting: list[Path] = []
    for run_dir in _run_dirs(Path(artifacts)):
        try:
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        gate_status = str(manifest.get("gate", {}).get("status", ""))
        problem = manifest.get("problem_number")
        if (gate_status == AWAITING and isinstance(problem, int)
                and not has_verified_result(Path(artifacts), problem)):
            awaiting.append(run_dir)
    return awaiting


def verify_awaiting(
    artifacts: Path, *, triage_dir: Path | None = None, category: str = "open",
    require_kernel: bool = False, publish: bool = False, limit: int = 0,
    verify=verify_run, client=None,
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
    args = parser.parse_args()
    results = verify_awaiting(
        args.artifacts, triage_dir=args.triage, category=args.category,
        require_kernel=args.require_kernel, publish=args.publish, limit=args.limit,
    )
    promoted = sum(1 for _, status in results if status.startswith("verified_"))
    print(f"[verify] done: {len(results)} runs, {promoted} promoted.", flush=True)


if __name__ == "__main__":
    main()
