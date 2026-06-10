#!/usr/bin/env python3
"""
deepseek_rename.py — COLLECT answers from DeepSeek chats.

Reads .deepseek_chat_map.json (written by deepseek_submit.py). For each chat it
navigates to the conversation, waits if still generating, and saves the answer
to erdos_problems/solutions_deepseek/<category>/solution_<N>.md plus a
human-named copy to outputs/deepseek/<category>/<title>.md.

Chats are NOT renamed: when DeepSeek shows a "too many requests" page the
sidebar disappears and renaming is impossible, so the verdict + completeness is
recorded only in the saved output filename.

Usage:
  python3 deepseek_rename.py                 # process all categories in the map
  python3 deepseek_rename.py --category open
  python3 deepseek_rename.py --watch         # keep polling until all done
"""

import argparse
import time

import deepseek_common as D
from deepseek_common import sync_playwright

SOLUTIONS_ROOT = D.REPO_DIR / "solutions_deepseek"


def process_once(page, category, gen_wait_s=20):
    chat_map = D.load_chat_map()
    cat_map = chat_map.get(category, {})
    if not cat_map:
        return 0, 0

    solutions_dir = SOLUTIONS_ROOT / category
    solutions_dir.mkdir(parents=True, exist_ok=True)

    completed = 0
    pending = 0

    for key, info in sorted(cat_map.items(), key=lambda kv: int(kv[0])):
        num = info.get("problem", int(key))
        url = info.get("url", "")
        out_file = solutions_dir / f"solution_{num}.md"

        if out_file.exists():
            txt = out_file.read_text(encoding="utf-8", errors="ignore")
            if "\nERROR:" not in txt[:200]:
                # Ensure the named output copy exists (restores progress even if
                # outputs/ was deleted or a previous run was interrupted).
                D.restore_output_from_solution("deepseek", category, num, txt)
                continue

        if "/chat/s/" not in url and "/a/chat/" not in url:
            print(f"#{num}: no valid chat URL recorded, skipping.")
            continue

        try:
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(3)

            # If the deep link is dead, DeepSeek redirects to the root/new-chat
            # page (no conversation loads). Skip and retry on a later pass.
            cur = page.url.rstrip("/")
            if "/chat/s/" not in cur and "/a/chat/" not in cur:
                print(f"#{num}: chat URL did not load (redirected to {page.url}), will retry.")
                pending += 1
                continue

            if D.is_generating(page):
                waited = 0
                while D.is_generating(page) and waited < gen_wait_s:
                    time.sleep(3)
                    waited += 3
                if D.is_generating(page):
                    print(f"#{num}: still generating, will retry next pass.")
                    pending += 1
                    continue

            # DeepSeek truncates long answers and shows a "Continue" button.
            # Click through any continuations before extracting.
            cont = D.click_continue_if_needed(page)
            if cont:
                print(f"#{num}: clicked Continue {cont}x")

            time.sleep(2)
            response = D.extract_response(page)

            # Guard: never save an empty/placeholder/truncated response.
            if (not response
                    or "[could not extract response]" in response.lower()
                    or len(response.strip()) < 200):
                print(f"#{num}: response not ready/empty, will retry next pass.")
                pending += 1
                continue

            solved = D.is_solved(response)
            completeness = D.extract_completeness(response)
            status_tag = "[solved]" if solved else "[unsolved]"
            title = D.output_title(num, status_tag, completeness)

            body = (
                f"# Erdős Problem #{num} {status_tag} {completeness}% (DeepSeek)\n\n"
                f"---\n\n## DeepSeek Response\n\n{response}\n"
            )
            out_file.write_text(body, encoding="utf-8")
            # Human-named copy in outputs/deepseek/<category>/.
            D.save_output("deepseek", category, num, title, body)

            completed += 1
            print(f"#{num}: {status_tag} {completeness}% saved")

        except Exception as e:
            print(f"#{num}: ERROR {e}")
            pending += 1

    return completed, pending


def main():
    ap = argparse.ArgumentParser(description="Collect answers from DeepSeek chats")
    ap.add_argument("--category", default=None, help="Limit to one category (default: all in map)")
    ap.add_argument("--watch", action="store_true", help="Keep polling every --interval until all done")
    ap.add_argument("--interval", type=float, default=60.0, help="Seconds between watch passes (default 60)")
    ap.add_argument("--headless", action="store_true", help="Run without a visible window")
    args = ap.parse_args()

    chat_map = D.load_chat_map()
    if not chat_map:
        raise SystemExit(f"No chat map found at {D.DS_CHAT_MAP_FILE}. Run deepseek_submit.py first.")

    categories = [args.category] if args.category else list(chat_map.keys())

    with sync_playwright() as pw:
        browser = D.launch_browser(pw, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()
        D.ensure_logged_in(page)

        def _healthy(pg) -> bool:
            try:
                _ = pg.url
                return True
            except Exception:
                return False

        while True:
            # Recover if the page/browser was closed (e.g. user closed window).
            if not _healthy(page):
                print("  (page closed — reopening browser)")
                try:
                    browser.close()
                except Exception:
                    pass
                browser = D.launch_browser(pw, headless=args.headless)
                page = browser.pages[0] if browser.pages else browser.new_page()
                D.ensure_logged_in(page)

            total_completed = 0
            total_pending = 0
            for cat in categories:
                print(f"\n=== [DeepSeek] Category: {cat} ===")
                done, pend = process_once(page, cat)
                total_completed += done
                total_pending += pend

            print(f"\nPass complete: {total_completed} saved this pass, {total_pending} still pending.")

            if not args.watch or total_pending == 0:
                break
            print(f"Waiting {args.interval}s before next pass...")
            time.sleep(args.interval)

        print("\nAll done.")
        browser.close()


if __name__ == "__main__":
    main()
