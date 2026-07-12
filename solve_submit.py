#!/usr/bin/env python3
"""
solve_submit.py — SUBMIT prompts to ChatGPT (no waiting for answers).

For each Erdős problem it:
  1. opens a new chat inside the configured ChatGPT project,
  2. submits the offline candidate-research prompt,
  3. records the conversation URL in .chatgpt_chat_map.json.

It does not collect the final answer. Use solve_rename.py for collection.

Usage:
  python solve_submit.py --login
  python solve_submit.py --limit 100
  python solve_submit.py --limit 100 --delay 20
  python solve_submit.py --problem 137
"""

import argparse
import sys
import time
from pathlib import Path

import erdos_common as C
from erdos_ingest import ProvenanceError
from erdos_common import sync_playwright
from legacy_candidate_collection import (
    AdaptiveCooldown,
    CandidateSource,
    build_bound_prompt,
    build_collection_contract,
    chat_metadata,
    clamp_cooldown,
    load_canonical_candidate_sources,
    reusable_chat_entry,
)


DEFAULT_TRIAGE_DIR = Path(__file__).resolve().parent / "triage"


def prepare_submission(
    source: CandidateSource, category: str
) -> tuple[dict[str, object], str]:
    """Build one source-bound, explicitly unverified ChatGPT submission."""
    contract = build_collection_contract(
        source,
        provider="chatgpt",
        category=category,
        prompt_template=C.PROMPT_TEMPLATE,
    )
    prompt = build_bound_prompt(
        C.PROMPT_TEMPLATE, source=source, contract=contract
    )
    return contract, prompt


def main(argv=None, *, problem_file_provider=None) -> None:
    ap = argparse.ArgumentParser(
        description="Submit Erdős problems to ChatGPT"
    )
    ap.add_argument(
        "--login",
        action="store_true",
        help="Open browser to log in, then exit",
    )
    ap.add_argument(
        "--category",
        default="open",
        help="open / verifiable / falsifiable",
    )
    ap.add_argument(
        "--start",
        type=int,
        default=0,
        help="Start index in the problem list",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of problems to submit",
    )
    ap.add_argument(
        "--problem",
        type=int,
        default=None,
        help="Submit one problem by Erdős number",
    )
    ap.add_argument(
        "--batch",
        type=int,
        default=5,
        help="Number of tabs to submit in parallel",
    )
    ap.add_argument(
        "--reverse",
        action="store_true",
        help="Process problems from highest number backwards",
    )
    ap.add_argument(
        "--delay",
        type=float,
        default=120.0,
        help="Seconds between submission rounds",
    )
    ap.add_argument(
        "--backoff",
        type=float,
        default=120.0,
        help="Seconds to wait when rate-limited",
    )
    ap.add_argument(
        "--think-timeout",
        type=float,
        default=1200.0,
        help="Maximum seconds to wait for a round to finish",
    )
    ap.add_argument(
        "--headless",
        action="store_true",
        help="Run without a visible browser window",
    )
    ap.add_argument(
        "--triage",
        type=Path,
        default=DEFAULT_TRIAGE_DIR,
        help="Triage root containing a complete canonical ingestion snapshot",
    )
    args = ap.parse_args(argv)
    args.backoff = clamp_cooldown(args.backoff)
    args.delay = clamp_cooldown(args.delay)
    adaptive_cooldown = AdaptiveCooldown(args.backoff)

    canonical_sources = None
    if not args.login:
        try:
            canonical_sources = load_canonical_candidate_sources(args.triage)
        except ProvenanceError as exc:
            sys.exit(
                "Refusing to submit without a complete canonical source "
                f"snapshot: {exc}"
            )

    C.PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = C.launch_browser(pw, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()

        if args.login:
            print("Opening ChatGPT for login. Log in, then return here.")
            page.goto(C.CHATGPT_URL, wait_until="domcontentloaded")
            input(
                "Press Enter after you have logged in and "
                "the chat page is visible..."
            )
            browser.close()
            print("Login saved.")
            return

        # Local paths select problem numbers only. Statements always come from
        # the fully validated immutable canonical snapshot loaded above.
        if args.problem is not None:
            numbers = [args.problem]
            if args.problem not in canonical_sources:
                sys.exit(
                    f"Problem #{args.problem} is not present in the complete "
                    "canonical source-open snapshot"
                )
        else:
            provider = problem_file_provider or C.get_problem_files
            files = provider(args.category)

            if args.reverse:
                files = list(reversed(files))

            files = files[args.start:]

            if args.limit is not None:
                files = files[:args.limit]

            numbers = [C.problem_number(path) for path in files]
            unavailable = [
                number for number in numbers if number not in canonical_sources
            ]
            for number in unavailable:
                print(
                    f"#{number}: not in the canonical source-open snapshot; "
                    "not submitting."
                )
            numbers = [
                number for number in numbers if number in canonical_sources
            ]

        C.ensure_logged_in(page)

        chat_map = C.load_chat_map()
        cat_map = chat_map.setdefault(args.category, {})

        # Exclude already submitted problems.
        pending = []

        for num in numbers:
            key = str(num)
            existing = cat_map.get(key, {})
            source = canonical_sources[num]
            contract, prompt = prepare_submission(source, args.category)

            if reusable_chat_entry(
                existing,
                contract,
                valid_url=lambda value: C.is_conversation_url(value),
            ):
                print(f"#{num}: current source-bound chat exists, skipping.")
                continue

            existing_url = (
                existing.get("url", "") if isinstance(existing, dict) else ""
            )
            if C.is_conversation_url(existing_url):
                print(f"#{num}: stale or unbound chat metadata; resubmitting.")
            pending.append((source, contract, prompt))

        total = len(pending)
        batch = max(1, args.batch)

        print(
            f"\nCategory: {args.category}"
            f"  |  Submitting {total} problems"
            f"  |  {batch} tab(s) in parallel\n"
        )

        n_tabs = max(1, min(batch, total)) if total else 1
        tabs = [page] + [
            browser.new_page()
            for _ in range(n_tabs - 1)
        ]

        def submit_one(tab, submission):
            """
            Submit one problem.

            Returns:
                tuple[int, str | None]: problem number and conversation URL.
            """
            source, contract, prompt = submission
            num = source.problem_number

            while True:
                try:
                    try:
                        _ = tab.url
                    except Exception:
                        tab = browser.new_page()

                    C.start_new_chat(tab)

                    if C.detect_rate_limit(tab):
                        wait_s = adaptive_cooldown.record_rate_limit()
                        C.dismiss_rate_limit_modal(tab)
                        print(
                            f"  #{num}: RATE LIMITED; adaptive wait "
                            f"{wait_s:.0f}s (streak {adaptive_cooldown.streak})..."
                        )
                        time.sleep(wait_s)
                        continue

                    start_url = C.current_url(tab)
                    C.send_prompt(tab, prompt)
                    url = C.wait_for_conversation_url(
                        tab,
                        timeout_s=45,
                        start_url=start_url,
                    )

                    if not valid_url(url, start_url) and C.detect_rate_limit(tab):
                        wait_s = adaptive_cooldown.record_rate_limit()
                        C.dismiss_rate_limit_modal(tab)
                        print(
                            f"  #{num}: RATE LIMITED after send; adaptive wait "
                            f"{wait_s:.0f}s (streak {adaptive_cooldown.streak})..."
                        )
                        time.sleep(wait_s)
                        continue
                    if valid_url(url, start_url):
                        adaptive_cooldown.record_success()
                    return num, url, start_url, contract

                except Exception as exc:
                    try:
                        limited = C.detect_rate_limit(tab)
                    except Exception:
                        limited = False
                    if limited:
                        wait_s = adaptive_cooldown.record_rate_limit()
                        print(
                            f"  #{num}: RATE LIMITED during browser error; adaptive "
                            f"wait {wait_s:.0f}s (streak {adaptive_cooldown.streak})..."
                        )
                        time.sleep(wait_s)
                        continue
                    print(f"  ERROR submitting #{num}: {exc}")
                    return num, None, "", contract

        def valid_url(url, start_url="") -> bool:
            return C.is_conversation_url(url, start_url)

        def wait_round_finished(round_tabs) -> None:
            """
            Wait until every tab in the current round stops generating,
            or until the configured timeout is reached.
            """
            print(
                f"  waiting for {len(round_tabs)} "
                "chat(s) to finish thinking..."
            )

            deadline = time.time() + args.think_timeout
            time.sleep(5)

            while time.time() < deadline:
                still_generating = []

                for tab in round_tabs:
                    try:
                        if C.is_generating(tab):
                            still_generating.append(tab)
                    except Exception:
                        pass

                if not still_generating:
                    print("  round finished thinking.")
                    return

                time.sleep(10)

            print(
                "  WARNING: think-timeout reached; "
                "moving to the next round."
            )

        submitted = 0

        for round_start in range(0, total, n_tabs):
            chunk = pending[
                round_start:round_start + n_tabs
            ]

            round_number = round_start // n_tabs + 1

            print(
                f"-- Round {round_number}: "
                f"submitting {len(chunk)} problem(s) --"
            )

            results = []
            round_tabs = []

            for tab, submission in zip(tabs, chunk):
                num, url, start_url, contract = submit_one(tab, submission)
                results.append((num, url, start_url, contract))
                round_tabs.append(tab)

                # Avoid starting all requests at exactly the same moment.
                time.sleep(2)

            for num, url, start_url, contract in results:
                if valid_url(url, start_url):
                    cat_map[str(num)] = chat_metadata(contract, url)
                    submitted += 1
                    print(f"  #{num}: submitted -> {url}")
                else:
                    print(
                        f"  #{num}: no URL captured "
                        "(will retry on next run)"
                    )

            # Save after every round so an interruption loses at most
            # one incomplete round.
            C.save_chat_map(chat_map)

            wait_round_finished(round_tabs)

            if round_start + n_tabs < total:
                print(
                    f"  waiting {args.delay:.0f}s "
                    "before the next round..."
                )
                time.sleep(args.delay)

        print(
            f"\nDone. {submitted} new submissions. "
            f"Map saved to {C.CHAT_MAP_FILE}"
        )
        print("Now run: python solve_rename.py")

        browser.close()


if __name__ == "__main__":
    main()
