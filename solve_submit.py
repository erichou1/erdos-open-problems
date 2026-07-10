#!/usr/bin/env python3
"""
solve_submit.py — SUBMIT prompts to ChatGPT (no waiting for answers).

For each Erdős problem it:
  1. opens a new chat inside the configured ChatGPT project,
  2. submits a literature-aware mathematical research prompt,
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

import erdos_common as C
from erdos_common import sync_playwright


def main() -> None:
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
    args = ap.parse_args()

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

        # Build the problem list.
        if args.problem is not None:
            tex = (
                C.REPO_DIR
                / args.category
                / "individual"
                / f"problem_{args.problem}.tex"
            )

            if not tex.exists():
                sys.exit(f"File not found: {tex}")

            files = [tex]
        else:
            files = C.get_problem_files(args.category)

            if args.reverse:
                files = list(reversed(files))

            files = files[args.start:]

            if args.limit is not None:
                files = files[:args.limit]

        C.ensure_logged_in(page)

        chat_map = C.load_chat_map()
        cat_map = chat_map.setdefault(args.category, {})

        # Exclude already submitted problems.
        pending = []

        for tex in files:
            num = C.problem_number(tex)
            key = str(num)
            existing = cat_map.get(key, {})

            if "/c/" in existing.get("url", ""):
                print(f"#{num}: already submitted, skipping.")
                continue

            pending.append(tex)

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

        def submit_one(tab, tex):
            """
            Submit one problem.

            Returns:
                tuple[int, str | None]: problem number and conversation URL.
            """
            num = C.problem_number(tex)
            statement = C.extract_problem_statement(tex)

            # The canonical problem page provides the surrounding remarks,
            # references, definitions, and literature context.
            canonical_url = f"https://www.erdosproblems.com/{num}"

            prompt = C.PROMPT_TEMPLATE.format(
                problem_number=num,
                problem_url=canonical_url,
                problem=statement,
            )

            try:
                try:
                    _ = tab.url
                except Exception:
                    tab = browser.new_page()

                C.start_new_chat(tab)

                if C.detect_rate_limit(tab):
                    print(
                        f"  #{num}: RATE LIMITED, "
                        f"backing off {args.backoff}s..."
                    )
                    time.sleep(args.backoff)

                C.send_prompt(tab, prompt)
                url = C.wait_for_conversation_url(
                    tab,
                    timeout_s=45,
                )

                if "/c/" not in url and C.detect_rate_limit(tab):
                    print(
                        f"  #{num}: RATE LIMITED after send, "
                        f"backing off {args.backoff}s..."
                    )
                    time.sleep(args.backoff)

                return num, url

            except Exception as exc:
                print(f"  ERROR submitting #{num}: {exc}")
                return num, None

        def valid_url(url) -> bool:
            return bool(url and "/c/" in url)

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

            for tab, tex in zip(tabs, chunk):
                num, url = submit_one(tab, tex)
                results.append((num, url))
                round_tabs.append(tab)

                # Avoid starting all requests at exactly the same moment.
                time.sleep(2)

            for num, url in results:
                if valid_url(url):
                    cat_map[str(num)] = {
                        "url": url,
                        "problem": num,
                    }
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