#!/usr/bin/env python3
"""Run the verified pipeline over a range of problem numbers, one browser session."""

import argparse
import traceback
from pathlib import Path

import erdos_common as C
from proof_pipeline import ProofPipeline
from run_verified_pipeline import ChatGPTBrowserRunner
from outcome_ledger import record_outcome
from run_status import has_verified_result
from erdos_searcher import (
    canonical_problem_run_inputs,
    find_latest_canonical_snapshot,
    load_canonical_corpus,
    normalized_budget_config,
)


def rate_limit_defaults() -> dict[str, float]:
    return {
        "backoff_s": 15.0,
        "max_backoff_s": 120.0,
        "request_spacing_s": 12.0,
    }


def already_verified(
    artifact_root: Path, problem_number: int, *,
    expected_run_contract_id: str | None = None,
) -> bool:
    return has_verified_result(
        artifact_root, problem_number,
        expected_run_contract_id=expected_run_contract_id,
    )


def main() -> None:
    limiter_defaults = rate_limit_defaults()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--category", default="open")
    parser.add_argument("--artifacts", type=Path, default=Path("proof_runs"))
    parser.add_argument("--triage", type=Path, default=Path("triage"))
    parser.add_argument("--stage-timeout", type=float, default=1800)
    parser.add_argument("--backoff", type=float,
                        default=limiter_defaults["backoff_s"])
    parser.add_argument("--max-backoff", type=float,
                        default=limiter_defaults["max_backoff_s"])
    parser.add_argument("--request-spacing", type=float,
                        default=limiter_defaults["request_spacing_s"])
    parser.add_argument("--max-revisions", type=int, default=2)
    parser.add_argument("--max-attempts", type=int, default=8)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--shard-index", type=int, default=0,
                        help="This worker's index (0-based) when splitting the range")
    parser.add_argument("--shard-count", type=int, default=1,
                        help="Total number of workers splitting the range")
    parser.add_argument(
        "--force-legacy", action="store_true",
        help="Run the RETIRED legacy range anyway. The supported path is "
             "`egmra campaign --triage <triage-dir>` (verified EGMRA pipeline).",
    )
    args = parser.parse_args()
    if not args.force_legacy:
        parser.error(
            "run_verified_range.py is RETIRED: it drives the legacy ProofPipeline "
            "over a range, which can never emit a ReleaseCertificate. Use the "
            "single verified pipeline instead:\n"
            "  egmra campaign --triage <triage-dir> --provider browser "
            "--policy <signed-policy>\n"
            "Pass --force-legacy only to run the retired path deliberately."
        )
    if "unrecorded" in args.model_id.lower() or not args.model_id.strip():
        parser.error("--model-id must be the exact recorded UI model identity")
    triage_dir = args.triage if args.triage.is_absolute() else C.REPO_DIR / args.triage
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

    problem_dir = C.REPO_DIR / args.category / "individual"
    numbers = sorted(
        int(f.stem.split("_")[1])
        for f in problem_dir.glob("problem_*.tex")
        if args.start <= int(f.stem.split("_")[1]) <= args.end
    )
    numbers = numbers[args.shard_index::args.shard_count]
    exact_inputs = {}
    for number in numbers:
        try:
            exact_inputs[number] = canonical_problem_run_inputs(
                C.REPO_DIR,
                triage_dir,
                number,
                model_portfolio=args.model_id,
                budget_config=budget_config,
                canonical_snapshot=canonical_snapshot,
                canonical_sources=canonical_sources,
            )
        except Exception as exc:
            print(f"problem {number}: exact context unavailable ({exc})", flush=True)
    todo = [
        number for number, run_inputs in exact_inputs.items()
        if not already_verified(
            args.artifacts,
            number,
            expected_run_contract_id=run_inputs["run_contract_id"],
        )
    ]
    unavailable = len(numbers) - len(exact_inputs)
    verified = len(exact_inputs) - len(todo)
    print(f"shard {args.shard_index}/{args.shard_count} of range {args.start}-{args.end}: "
          f"{len(numbers)} problems, {verified} exact-context verified, "
          f"{unavailable} unavailable, {len(todo)} to run", flush=True)

    C.PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with C.sync_playwright() as playwright:
        browser = C.launch_browser(playwright, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()
        C.ensure_logged_in(page)
        runner = ChatGPTBrowserRunner(
            browser, page, timeout_s=budget_config["stage_timeout_s"],
            backoff_s=budget_config["initial_backoff_s"],
            max_backoff_s=budget_config["max_backoff_s"],
            request_spacing_s=budget_config["request_spacing_s"],
            max_attempts=budget_config["max_attempts"],
        )

        for problem_number in todo:
            run_inputs = exact_inputs[problem_number]
            statement = run_inputs["statement"]
            pipeline = ProofPipeline(
                runner,
                args.artifacts,
                max_revisions=args.max_revisions,
                pipeline_version=run_inputs["pipeline_version"],
                model_portfolio=args.model_id,
                execution_config=run_inputs["execution_config"],
                source_snapshot_id=run_inputs["source_snapshot_id"],
                source_snapshot_sha256=run_inputs["source_snapshot_sha256"],
                toolset=run_inputs["toolset"],
                dependencies=run_inputs["dependencies"],
                runtime=run_inputs["runtime"],
            )
            print(f"\n=== problem {problem_number} ===", flush=True)
            try:
                result = pipeline.solve(
                    problem_number, statement,
                    research_directive=run_inputs["research_directive"],
                )
                record_outcome(
                    triage_dir, problem_number,
                    result.artifact_dir / "manifest.json",
                )
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
