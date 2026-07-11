#!/usr/bin/env python3
"""Run the verified pipeline over a range of problem numbers, one browser session."""

import argparse
import traceback
from pathlib import Path

import erdos_common as C
from proof_pipeline import ProofPipeline
from run_verified_pipeline import ChatGPTBrowserRunner


def already_verified(artifact_root: Path, problem_number: int) -> bool:
    prob_dir = artifact_root / f"problem_{problem_number}"
    if not prob_dir.exists():
        return False
    return any((d / "manifest.json").exists() for d in prob_dir.glob("*") if d.is_dir())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--category", default="open")
    parser.add_argument("--artifacts", type=Path, default=Path("proof_runs"))
    parser.add_argument("--stage-timeout", type=float, default=1800)
    parser.add_argument("--backoff", type=float, default=180.0)
    parser.add_argument("--max-revisions", type=int, default=2)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--shard-index", type=int, default=0,
                        help="This worker's index (0-based) when splitting the range")
    parser.add_argument("--shard-count", type=int, default=1,
                        help="Total number of workers splitting the range")
    args = parser.parse_args()

    problem_dir = C.REPO_DIR / args.category / "individual"
    numbers = sorted(
        int(f.stem.split("_")[1])
        for f in problem_dir.glob("problem_*.tex")
        if args.start <= int(f.stem.split("_")[1]) <= args.end
    )
    numbers = numbers[args.shard_index::args.shard_count]
    todo = [n for n in numbers if not already_verified(args.artifacts, n)]
    print(f"shard {args.shard_index}/{args.shard_count} of range {args.start}-{args.end}: "
          f"{len(numbers)} problems, {len(numbers) - len(todo)} already verified, "
          f"{len(todo)} to run", flush=True)

    C.PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with C.sync_playwright() as playwright:
        browser = C.launch_browser(playwright, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()
        C.ensure_logged_in(page)
        runner = ChatGPTBrowserRunner(
            browser, page, timeout_s=args.stage_timeout, backoff_s=args.backoff,
        )
        pipeline = ProofPipeline(runner, args.artifacts, max_revisions=args.max_revisions)

        for problem_number in todo:
            problem_file = problem_dir / f"problem_{problem_number}.tex"
            statement = C.extract_problem_statement(problem_file)
            print(f"\n=== problem {problem_number} ===", flush=True)
            try:
                result = pipeline.solve(problem_number, statement)
                print(f"problem {problem_number}: candidate={result.candidate_outcome} "
                      f"gate={result.gate.status}", flush=True)
            except Exception as exc:
                print(f"problem {problem_number}: FAILED ({exc})", flush=True)
                traceback.print_exc()
                continue

        browser.close()

    print("\nrange run complete.")


if __name__ == "__main__":
    main()
