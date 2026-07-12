#!/usr/bin/env python3
"""Continuously solve open problems in searcher-ranked order with one browser.

Unlike run_sol2_batch (a fixed list), this worker pulls the next highest-ranked,
unclaimed, unverified problem from the shared queue, so N of these processes
(one per ChatGPT profile) drain the whole ranked corpus and refill themselves as
problems complete. It also re-ranks periodically under a lock (only one worker
rebuilds), and records each durable outcome so the searcher — which now folds
recorded outcomes back into its priors — adapts the queue over time.

Usage (one per profile):
  CHATGPT_PROFILE_DIR=/abs/.chatgpt_profile_2 \\
    .venv/bin/python -u run_continuous.py --worker-id w2
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import erdos_common as C
from proof_pipeline import ProofPipeline
from run_verified_pipeline import ChatGPTBrowserRunner, publish_verified_result
from outcome_ledger import record_outcome
from problem_queue import (
    allocation_record,
    claim_next,
    load_allocation_plan,
    release_unverified_claims,
)
from erdos_searcher import (
    build_searcher,
    canonical_problem_run_inputs,
    find_latest_canonical_snapshot,
    load_canonical_corpus,
    normalized_budget_config,
    pipeline_fingerprint,
    research_budget_id,
    toolset_version,
)
from feature_flags import require_feature

VERIFIED_GATES = {"verified_proved", "verified_disproved"}


def maybe_rerank(triage_dir: Path, root: Path, interval_s: float, top_k: int,
                 model_portfolio: str, budget: str,
                 budget_config: dict, *, source_snapshot_id: str,
                 source_snapshot_sha256: str,
                 canonical_open_source_records: int) -> dict | None:
    """Return a fresh exact-context ranking; rebuild under a cross-worker lock."""
    now = time.time()
    expected = {
        "pipeline_version": pipeline_fingerprint(root),
        "model_portfolio": model_portfolio,
        "budget": budget,
        "budget_config": budget_config,
        "toolset_version": toolset_version(root),
        "source_snapshot_id": source_snapshot_id,
        "source_snapshot_sha256": source_snapshot_sha256,
        "canonical_open_source_records": canonical_open_source_records,
        "allocation_top_k": int(top_k),
    }
    contexts = triage_dir / "rankings" / "contexts"
    candidates: list[tuple[float, dict]] = []
    for path in contexts.glob("*/*.json"):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            age = now - path.stat().st_mtime
        except (OSError, json.JSONDecodeError):
            continue
        if (
            isinstance(value, dict)
            and value.get("allocation_status") == "ready"
            and all(value.get(key) == expected_value for key, expected_value in expected.items())
            and (interval_s <= 0 or age < interval_s)
        ):
            candidates.append((path.stat().st_mtime, value))
    if candidates:
        return max(candidates, key=lambda item: item[0])[1]
    lock = triage_dir / ".rerank.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        try:  # steal only a clearly stale lock left by a dead worker
            if now - lock.stat().st_mtime > max(interval_s, 300):
                lock.unlink()
        except OSError:
            pass
        return None
    try:
        os.write(fd, str(now).encode())
        rankings = build_searcher(
            root, triage_dir,
            snapshot_date=datetime.now(timezone.utc).date().isoformat(),
            top_k=top_k, model_portfolio=model_portfolio, budget=budget,
            budget_config=budget_config,
        )
        if rankings.get("allocation_status") != "ready":
            raise RuntimeError(rankings.get("allocation_status", "ranking withheld"))
        print("[continuous] re-ranked searcher queue", flush=True)
        return rankings
    except Exception as exc:  # a bad re-rank must not kill the solver loop
        print(f"[continuous] rerank failed: {exc}", flush=True)
        return None
    finally:
        os.close(fd)
        try:
            lock.unlink()
        except OSError:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--category", default="open")
    parser.add_argument("--artifacts", type=Path, default=Path("proof_runs_sol2"))
    parser.add_argument("--triage", type=Path, default=Path("triage"))
    parser.add_argument("--worker-id",
                        default=os.environ.get("CHATGPT_PROFILE_DIR", "w0"))
    parser.add_argument("--stage-timeout", type=float, default=1800)
    parser.add_argument("--backoff", type=float, default=15.0)
    parser.add_argument("--max-backoff", type=float, default=120.0)
    parser.add_argument("--request-spacing", type=float, default=12.0)
    parser.add_argument("--max-revisions", type=int, default=2)
    parser.add_argument("--max-attempts", type=int, default=8)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--max-problems", type=int, default=0, help="0 = unlimited")
    parser.add_argument("--rerank-interval", type=float, default=1800.0,
                        help="Seconds between searcher re-ranks; 0 disables")
    parser.add_argument("--rerank-top-k", type=int, default=600)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument(
        "--new-campaign", action="store_true",
        help="Release all unverified claims before starting. Use only when no "
             "other continuous workers are active.",
    )
    parser.add_argument(
        "--enable-experimental", action="store_true",
        help="Explicitly override the disabled continuous_scheduler release flag",
    )
    args = parser.parse_args()
    if "unrecorded" in args.model_id.lower() or not args.model_id.strip():
        parser.error("--model-id must be the exact recorded UI model identity")

    require_feature("continuous_scheduler", override=args.enable_experimental)

    root = C.REPO_DIR
    triage_dir = args.triage if args.triage.is_absolute() else root / args.triage
    artifacts = args.artifacts if args.artifacts.is_absolute() else root / args.artifacts
    budget_config = normalized_budget_config(
        max_revisions=args.max_revisions,
        stage_timeout_s=args.stage_timeout,
        initial_backoff_s=args.backoff,
        max_backoff_s=args.max_backoff,
        request_spacing_s=args.request_spacing,
        max_attempts=args.max_attempts,
        browser_headless=args.headless,
    )
    budget = research_budget_id(**budget_config)
    canonical_snapshot = find_latest_canonical_snapshot(triage_dir)
    canonical_sources = load_canonical_corpus(canonical_snapshot)
    canonical_snapshot_sha256 = hashlib.sha256(
        (canonical_snapshot / "manifest.json").read_bytes()
    ).hexdigest()

    if args.new_campaign:
        released = release_unverified_claims(artifacts)
        print(f"[continuous] new campaign released {released} unverified claims",
              flush=True)

    C.PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    solved = 0
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

        while True:
            ranking = maybe_rerank(
                triage_dir, root, args.rerank_interval, args.rerank_top_k,
                args.model_id, budget, budget_config,
                source_snapshot_id=canonical_snapshot.name,
                source_snapshot_sha256=canonical_snapshot_sha256,
                canonical_open_source_records=len(canonical_sources),
            )
            if ranking is None:
                print("[continuous] exact-context ranking is being prepared; retrying.",
                      flush=True)
                time.sleep(max(1.0, min(
                    30.0, budget_config["request_spacing_s"]
                )))
                continue
            allocation_context_id = ranking["allocation_context_id"]
            plan = load_allocation_plan(
                triage_dir,
                expected_allocation_context_id=allocation_context_id,
                expected_ranking_content_sha256=ranking["ranking_content_sha256"],
            )
            if not plan.records:
                print("[continuous] no ranked problems available; stopping.", flush=True)
                break
            number = claim_next(
                artifacts, plan, args.worker_id,
            )
            if number is None:
                print("[continuous] all ranked problems verified or claimed; stopping.",
                      flush=True)
                break

            run_inputs = canonical_problem_run_inputs(
                root,
                triage_dir,
                number,
                model_portfolio=args.model_id,
                budget_config=budget_config,
                canonical_snapshot=canonical_snapshot,
                canonical_sources=canonical_sources,
            )
            queued_record = allocation_record(
                plan, number,
            )
            if queued_record["run_contract_id"] != run_inputs["run_contract_id"]:
                raise RuntimeError(
                    f"problem {number} source/run contract changed after ranking"
                )
            statement = run_inputs["statement"]
            pipeline = ProofPipeline(
                runner,
                artifacts,
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
            print(f"\n[continuous] === #{number}: starting (worker {args.worker_id}) ===",
                  flush=True)
            result = None
            try:
                result = pipeline.solve(
                    number, statement,
                    research_directive=run_inputs["research_directive"],
                )
                print(f"[continuous] #{number}: candidate={result.candidate_outcome} "
                      f"gate={result.gate.status}", flush=True)
                if result.gate.status in VERIFIED_GATES:
                    try:
                        published = publish_verified_result(result, args.category, root)
                        print(f"[continuous] #{number}: published {published}", flush=True)
                    except Exception as exc:
                        print(f"[continuous] #{number}: publish failed: {exc}", flush=True)
            except Exception as exc:
                print(f"[continuous] #{number}: FAILED ({exc})", flush=True)
                traceback.print_exc()

            if result is not None:
                try:
                    record_outcome(
                        triage_dir,
                        number,
                        result.artifact_dir / "manifest.json",
                    )
                except Exception as exc:
                    print(f"[continuous] #{number}: outcome record failed: {exc}", flush=True)

            solved += 1
            if args.max_problems and solved >= args.max_problems:
                print(f"[continuous] reached --max-problems={args.max_problems}; stopping.",
                      flush=True)
                break

        browser.close()
    print(f"[continuous] worker {args.worker_id} done; attempted {solved} problems.",
          flush=True)


if __name__ == "__main__":
    main()
