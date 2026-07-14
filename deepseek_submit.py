#!/usr/bin/env python3
"""
deepseek_submit.py — SUBMIT prompts to DeepSeek (no waiting for answers).

For each Erdős problem it opens a new chat, submits the solving prompt, and
records the conversation URL in .deepseek_chat_map.json.

Usage:
  python3 deepseek_submit.py --login            # one-time login
  python3 deepseek_submit.py --limit 100        # submit first 100 open problems
  python3 deepseek_submit.py --limit 100 --delay 20
  python3 deepseek_submit.py --problem 137      # single problem
"""

import argparse
import sys
import time
from pathlib import Path

import deepseek_common as D
from deepseek_common import sync_playwright
from erdos_ingest import ProvenanceError
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


def valid_conversation_url(url: str) -> bool:
    return bool(url and ("/chat/s/" in url or "/a/chat/" in url))


def prepare_submission(
    source: CandidateSource, category: str
) -> tuple[dict[str, object], str]:
    """Build one source-bound, explicitly unverified DeepSeek submission."""
    contract = build_collection_contract(
        source,
        provider="deepseek",
        category=category,
        prompt_template=D.PROMPT_TEMPLATE,
    )
    prompt = build_bound_prompt(
        D.PROMPT_TEMPLATE, source=source, contract=contract
    )
    return contract, prompt


def main(argv=None):
    ap = argparse.ArgumentParser(description="Submit Erdős problems to DeepSeek")
    ap.add_argument("--login",    action="store_true", help="Open browser to log in, then exit")
    ap.add_argument("--category", default="open",      help="open / verifiable / falsifiable")
    ap.add_argument("--start",    type=int, default=0, help="Start index in the problem list")
    ap.add_argument("--limit",    type=int, default=None, help="Max number of problems to submit")
    ap.add_argument("--problem",  type=int, default=None, help="Submit a single problem by Erdős number")
    ap.add_argument("--batch",    type=int, default=1, help="Tabs to submit in parallel (default 1; DeepSeek allows only one message at a time)")
    ap.add_argument("--reverse",  action="store_true", help="Process problems from the end (highest number) backwards")
    ap.add_argument("--delay",    type=float, default=120.0, help="Seconds between submission rounds, after the round finishes thinking (default 120)")
    ap.add_argument("--backoff",  type=float, default=120.0, help="Seconds to wait when rate-limited (default 120)")
    ap.add_argument("--think-timeout", type=float, default=1200.0, help="Max seconds to wait for a round to finish thinking (default 1200)")
    ap.add_argument("--headless", action="store_true", help="Run without a visible window")
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

    canonical_sources: dict[int, CandidateSource] = {}
    if not args.login:
        try:
            canonical_sources = load_canonical_candidate_sources(args.triage)
        except ProvenanceError as exc:
            sys.exit(
                "Refusing to submit without a complete canonical source "
                f"snapshot: {exc}"
            )

    D.DS_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = D.launch_browser(pw, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()

        if args.login:
            print("Opening DeepSeek for login. Log in, then return here.")
            page.goto(D.DEEPSEEK_URL, wait_until="domcontentloaded")
            input("Press Enter after you have logged in and the chat page is visible...")
            browser.close()
            print("Login saved.")
            return

        if args.problem is not None:
            numbers = [args.problem]
            if args.problem not in canonical_sources:
                sys.exit(
                    f"Problem #{args.problem} is not present in the complete "
                    "canonical source-open snapshot"
                )
        else:
            files = D.get_problem_files(args.category)
            if args.reverse:
                files = list(reversed(files))
            files = files[args.start:]
            if args.limit is not None:
                files = files[:args.limit]
            numbers = [D.problem_number(path) for path in files]
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

        D.ensure_logged_in(page)

        chat_map = D.load_chat_map()
        cat_map = chat_map.setdefault(args.category, {})

        # Filter out already-submitted problems up front
        pending = []
        for num in numbers:
            key = str(num)
            existing = cat_map.get(key, {})
            source = canonical_sources[num]
            contract, prompt = prepare_submission(source, args.category)
            if reusable_chat_entry(
                existing, contract, valid_url=valid_conversation_url
            ):
                print(f"#{num}: current source-bound chat exists, skipping.")
                continue
            existing_url = existing.get("url", "") if isinstance(existing, dict) else ""
            if valid_conversation_url(existing_url):
                print(f"#{num}: stale or unbound chat metadata; resubmitting.")
            pending.append((source, contract, prompt))

        total = len(pending)
        batch = max(1, args.batch)
        print(f"\n[DeepSeek] Category: {args.category}  |  Submitting {total} problems  |  {batch} tab(s) in parallel\n")

        n_tabs = max(1, min(batch, total)) if total else 1
        tabs = [page] + [browser.new_page() for _ in range(n_tabs - 1)]

        def submit_one(tab, submission):
            source, contract, prompt = submission
            num = source.problem_number
            while True:
                try:
                    try:
                        _ = tab.url
                    except Exception:
                        tab = browser.new_page()
                    D.start_new_chat(tab)
                    if D.detect_rate_limit(tab):
                        wait_s = adaptive_cooldown.record_rate_limit()
                        print(
                            f"  #{num}: RATE LIMITED; adaptive wait {wait_s:.0f}s "
                            f"(streak {adaptive_cooldown.streak})..."
                        )
                        time.sleep(wait_s)
                        continue
                    D.send_prompt(tab, prompt)
                    url = D.wait_for_conversation_url(tab, timeout_s=30)
                    if not valid_conversation_url(url) and D.detect_rate_limit(tab):
                        wait_s = adaptive_cooldown.record_rate_limit()
                        print(
                            f"  #{num}: RATE LIMITED after send; adaptive wait "
                            f"{wait_s:.0f}s (streak {adaptive_cooldown.streak})..."
                        )
                        time.sleep(wait_s)
                        continue
                    if valid_conversation_url(url):
                        adaptive_cooldown.record_success()
                    return num, url, contract
                except Exception as error:
                    try:
                        limited = D.detect_rate_limit(tab)
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
                    print(f"  ERROR submitting #{num}: {error}")
                    return num, None, contract

        def valid_url(u):
            return valid_conversation_url(u)

        def wait_round_finished(round_tabs):
            """Block until every tab in this round stops generating (or timeout)."""
            print(f"  waiting for {len(round_tabs)} chat(s) to finish thinking...")
            deadline = time.time() + args.think_timeout
            # Give generation a moment to actually start before polling.
            time.sleep(5)
            while time.time() < deadline:
                still = []
                for tab in round_tabs:
                    try:
                        if D.is_generating(tab):
                            still.append(tab)
                    except Exception:
                        pass
                if not still:
                    print("  round finished thinking.")
                    return
                time.sleep(10)
            print("  WARNING: think-timeout reached; moving on.")

        submitted = 0
        for round_start in range(0, total, n_tabs):
            chunk = pending[round_start:round_start + n_tabs]
            print(f"-- Round {round_start // n_tabs + 1}: submitting {len(chunk)} problem(s) --")

            results = []
            round_tabs = []
            for tab, submission in zip(tabs, chunk):
                num, url, contract = submit_one(tab, submission)
                results.append((num, url, contract))
                round_tabs.append(tab)
                time.sleep(2)

            for num, url, contract in results:
                if valid_url(url):
                    cat_map[str(num)] = chat_metadata(contract, url)
                    submitted += 1
                    print(f"  #{num}: submitted → {url}")
                else:
                    print(f"  #{num}: no URL captured (will retry on next run)")
            D.save_chat_map(chat_map)

            # Wait for this round to finish thinking before continuing.
            wait_round_finished(round_tabs)

            if round_start + n_tabs < total:
                print(f"  waiting {args.delay:.0f}s before next round...")
                time.sleep(args.delay)

        print(f"\nDone. {submitted} new submissions. Map saved to {D.DS_CHAT_MAP_FILE}")
        print("Now run:  python3 deepseek_rename.py")
        browser.close()


if __name__ == "__main__":
    main()
