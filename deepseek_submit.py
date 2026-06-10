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

import deepseek_common as D
from deepseek_common import sync_playwright


def main():
    ap = argparse.ArgumentParser(description="Submit Erdős problems to DeepSeek")
    ap.add_argument("--login",    action="store_true", help="Open browser to log in, then exit")
    ap.add_argument("--category", default="open",      help="open / verifiable / falsifiable")
    ap.add_argument("--start",    type=int, default=0, help="Start index in the problem list")
    ap.add_argument("--limit",    type=int, default=None, help="Max number of problems to submit")
    ap.add_argument("--problem",  type=int, default=None, help="Submit a single problem by Erdős number")
    ap.add_argument("--batch",    type=int, default=1, help="Tabs to submit in parallel (default 1; DeepSeek allows only one message at a time)")
    ap.add_argument("--reverse",  action="store_true", help="Process problems from the end (highest number) backwards")
    ap.add_argument("--delay",    type=float, default=15.0, help="Seconds between submission rounds (default 15)")
    ap.add_argument("--backoff",  type=float, default=120.0, help="Seconds to wait when rate-limited (default 120)")
    ap.add_argument("--headless", action="store_true", help="Run without a visible window")
    args = ap.parse_args()

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
            tex = D.REPO_DIR / args.category / "individual" / f"problem_{args.problem}.tex"
            if not tex.exists():
                sys.exit(f"File not found: {tex}")
            files = [tex]
        else:
            files = D.get_problem_files(args.category)
            if args.reverse:
                files = list(reversed(files))
            files = files[args.start:]
            if args.limit is not None:
                files = files[:args.limit]

        D.ensure_logged_in(page)

        chat_map = D.load_chat_map()
        cat_map = chat_map.setdefault(args.category, {})

        # Filter out already-submitted problems up front
        pending = []
        for tex in files:
            num = D.problem_number(tex)
            key = str(num)
            if key in cat_map and ("/chat/s/" in cat_map[key].get("url", "")
                                   or "/a/chat/" in cat_map[key].get("url", "")):
                print(f"#{num}: already submitted, skipping.")
                continue
            pending.append(tex)

        total = len(pending)
        batch = max(1, args.batch)
        print(f"\n[DeepSeek] Category: {args.category}  |  Submitting {total} problems  |  {batch} tab(s) in parallel\n")

        n_tabs = max(1, min(batch, total)) if total else 1
        tabs = [page] + [browser.new_page() for _ in range(n_tabs - 1)]

        def submit_one(tab, tex):
            num = D.problem_number(tex)
            statement = D.extract_problem_statement(tex)
            prompt = D.PROMPT_TEMPLATE.format(problem=statement)
            try:
                try:
                    _ = tab.url
                except Exception:
                    tab = browser.new_page()
                D.start_new_chat(tab)
                if D.detect_rate_limit(tab):
                    print(f"  #{num}: RATE LIMITED, backing off {args.backoff}s...")
                    time.sleep(args.backoff)
                D.send_prompt(tab, prompt)
                url = D.wait_for_conversation_url(tab, timeout_s=30)
                if D.detect_rate_limit(tab):
                    print(f"  #{num}: RATE LIMITED after send, backing off {args.backoff}s...")
                    time.sleep(args.backoff)
                return num, url
            except Exception as e:
                print(f"  ERROR submitting #{num}: {e}")
                return num, None

        def valid_url(u):
            return u and ("/chat/s/" in u or "/a/chat/" in u)

        submitted = 0
        for round_start in range(0, total, n_tabs):
            chunk = pending[round_start:round_start + n_tabs]
            print(f"-- Round {round_start // n_tabs + 1}: submitting {len(chunk)} problem(s) --")

            results = []
            for tab, tex in zip(tabs, chunk):
                num, url = submit_one(tab, tex)
                results.append((num, url))
                time.sleep(2)

            for num, url in results:
                if valid_url(url):
                    cat_map[str(num)] = {"url": url, "problem": num}
                    submitted += 1
                    print(f"  #{num}: submitted → {url}")
                else:
                    print(f"  #{num}: no URL captured (will retry on next run)")
            D.save_chat_map(chat_map)

            if round_start + n_tabs < total:
                time.sleep(args.delay)

        print(f"\nDone. {submitted} new submissions. Map saved to {D.DS_CHAT_MAP_FILE}")
        print("Now run:  python3 deepseek_rename.py")
        browser.close()


if __name__ == "__main__":
    main()
