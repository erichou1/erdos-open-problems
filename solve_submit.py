#!/usr/bin/env python3
"""
solve_submit.py — SUBMIT prompts to ChatGPT (no waiting for answers).

For each Erdős problem it:
  1. opens a new chat inside the project,
  2. submits the solving prompt,
  3. records the conversation URL in .chatgpt_chat_map.json.

It does NOT wait for the full answer (that's what solve_rename.py is for),
which keeps it fast and lets ChatGPT work on many chats at once.

Rate-limit handling: a delay between submissions, plus automatic back-off when
ChatGPT shows a rate-limit message.

Usage:
  python3 solve_submit.py --login            # one-time login
  python3 solve_submit.py --limit 100        # submit first 100 open problems
  python3 solve_submit.py --limit 100 --delay 20
  python3 solve_submit.py --problem 137      # single problem
"""

import argparse
import sys
import time

import erdos_common as C
from erdos_common import sync_playwright


def main():
    ap = argparse.ArgumentParser(description="Submit Erdős problems to ChatGPT")
    ap.add_argument("--login",    action="store_true", help="Open browser to log in, then exit")
    ap.add_argument("--category", default="open",      help="open / verifiable / falsifiable")
    ap.add_argument("--start",    type=int, default=0, help="Start index in the problem list")
    ap.add_argument("--limit",    type=int, default=None, help="Max number of problems to submit")
    ap.add_argument("--problem",  type=int, default=None, help="Submit a single problem by Erdős number")
    ap.add_argument("--batch",    type=int, default=5, help="Number of tabs to submit in parallel (default 5)")
    ap.add_argument("--reverse",  action="store_true", help="Process problems from the end (highest number) backwards")
    ap.add_argument("--delay",    type=float, default=120.0, help="Seconds to wait between submission rounds, after the round finishes thinking (default 120)")
    ap.add_argument("--backoff",  type=float, default=120.0, help="Seconds to wait when rate-limited (default 120)")
    ap.add_argument("--think-timeout", type=float, default=1200.0, help="Max seconds to wait for a round to finish thinking (default 1200)")
    ap.add_argument("--headless", action="store_true", help="Run without a visible window")
    args = ap.parse_args()

    C.PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = C.launch_browser(pw, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()

        if args.login:
            print("Opening ChatGPT for login. Log in, then return here.")
            page.goto(C.CHATGPT_URL, wait_until="domcontentloaded")
            input("Press Enter after you have logged in and the chat page is visible...")
            browser.close()
            print("Login saved.")
            return

        # Build problem list
        if args.problem is not None:
            tex = C.REPO_DIR / args.category / "individual" / f"problem_{args.problem}.tex"
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

        # Filter out already-submitted problems up front
        pending = []
        for tex in files:
            num = C.problem_number(tex)
            key = str(num)
            if key in cat_map and "/c/" in cat_map[key].get("url", ""):
                print(f"#{num}: already submitted, skipping.")
                continue
            pending.append(tex)

        total = len(pending)
        batch = max(1, args.batch)
        print(f"\nCategory: {args.category}  |  Submitting {total} problems  |  {batch} tab(s) in parallel\n")

        # Create the tab pool
        n_tabs = max(1, min(batch, total)) if total else 1
        tabs = [page] + [browser.new_page() for _ in range(n_tabs - 1)]

        def submit_one(tab, tex):
            """Submit one problem in the given tab; return (num, url) or (num, None)."""
            num = C.problem_number(tex)
            statement = C.extract_problem_statement(tex)
            prompt = C.PROMPT_TEMPLATE.format(problem=statement)
            try:
                try:
                    _ = tab.url
                except Exception:
                    tab = browser.new_page()
                C.start_new_chat(tab)
                if C.detect_rate_limit(tab):
                    print(f"  #{num}: RATE LIMITED, backing off {args.backoff}s...")
                    time.sleep(args.backoff)
                C.send_prompt(tab, prompt)
                url = C.wait_for_conversation_url(tab, timeout_s=45)
                # Only treat as rate-limited if the message clearly did NOT go
                # through (no conversation URL was created).
                if "/c/" not in url and C.detect_rate_limit(tab):
                    print(f"  #{num}: RATE LIMITED after send, backing off {args.backoff}s...")
                    time.sleep(args.backoff)
                return num, url
            except Exception as e:
                print(f"  ERROR submitting #{num}: {e}")
                return num, None

        def valid_url(u):
            return u and "/c/" in u

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
                        if C.is_generating(tab):
                            still.append(tab)
                    except Exception:
                        pass
                if not still:
                    print("  round finished thinking.")
                    return
                time.sleep(10)
            print("  WARNING: think-timeout reached; moving on.")

        submitted = 0
        # Process in rounds of n_tabs problems at a time
        for round_start in range(0, total, n_tabs):
            chunk = pending[round_start:round_start + n_tabs]
            print(f"-- Round {round_start // n_tabs + 1}: submitting {len(chunk)} problem(s) --")

            # Stagger the start of each tab slightly to avoid a thundering herd
            results = []
            round_tabs = []
            for tab, tex in zip(tabs, chunk):
                num, url = submit_one(tab, tex)
                results.append((num, url))
                round_tabs.append(tab)
                time.sleep(2)  # small stagger between tabs in the same round

            # Record results
            for num, url in results:
                if valid_url(url):
                    cat_map[str(num)] = {"url": url, "problem": num}
                    submitted += 1
                    print(f"  #{num}: submitted → {url}")
                else:
                    print(f"  #{num}: no URL captured (will retry on next run)")
            C.save_chat_map(chat_map)

            # Wait for this whole round to finish thinking before continuing.
            wait_round_finished(round_tabs)

            # Delay before the next round
            if round_start + n_tabs < total:
                print(f"  waiting {args.delay:.0f}s before next round...")
                time.sleep(args.delay)

        print(f"\nDone. {submitted} new submissions. Map saved to {C.CHAT_MAP_FILE}")
        print("Now run:  python3 solve_rename.py")
        browser.close()


if __name__ == "__main__":
    main()
