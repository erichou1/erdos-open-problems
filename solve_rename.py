#!/usr/bin/env python3
"""
solve_rename.py — COLLECT answers and RENAME chats.

Reads .chatgpt_chat_map.json (written by solve_submit.py). For each recorded
chat it:
  1. navigates directly to the conversation URL,
  2. waits if ChatGPT is still generating,
  3. saves the answer to erdos_problems/solutions/<category>/solution_<N>.md,
  4. renames the chat to  "Erdős #N [solved|unsolved] C%".

Safe to run repeatedly: chats still generating are left for the next run,
already-renamed/saved chats are skipped.

Usage:
  python3 solve_rename.py                 # process all categories in the map
  python3 solve_rename.py --category open
  python3 solve_rename.py --watch         # keep polling every 60s until all done
  python3 solve_rename.py --no-rename     # only save answers, skip renaming
"""

import argparse
import time

import erdos_common as C
from erdos_common import sync_playwright


def process_once(page, category, do_rename=True, gen_wait_s=20) -> tuple[int, int]:
    """
    Returns (completed_this_pass, still_pending).
    """
    chat_map = C.load_chat_map()
    cat_map = chat_map.get(category, {})
    if not cat_map:
        return 0, 0

    solutions_dir = C.REPO_DIR / "solutions" / category
    solutions_dir.mkdir(parents=True, exist_ok=True)

    completed = 0
    pending = 0

    for key, info in sorted(cat_map.items(), key=lambda kv: int(kv[0])):
        num = info.get("problem", int(key))
        url = info.get("url", "")
        out_file = solutions_dir / f"solution_{num}.md"

        # Skip if already saved as a real (non-error) solution
        if out_file.exists():
            txt = out_file.read_text(encoding="utf-8", errors="ignore")
            if "\nERROR:" not in txt[:200]:
                # Make sure the named output copy exists (restores progress even
                # if outputs/ was deleted or a previous run was interrupted).
                C.restore_output_from_solution("chatgpt", category, num, txt)
                continue

        if "/c/" not in url:
            print(f"#{num}: no valid chat URL recorded, skipping.")
            continue

        try:
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(2)

            # If still generating, give it a short grace period, else leave for later
            if C.is_generating(page):
                waited = 0
                while C.is_generating(page) and waited < gen_wait_s:
                    time.sleep(3)
                    waited += 3
                if C.is_generating(page):
                    print(f"#{num}: still generating, will retry next pass.")
                    pending += 1
                    continue

            time.sleep(2)  # let final tokens settle
            response = C.extract_response(page)

            # Guard: never save an empty/placeholder/truncated response. Leave it
            # pending so a later pass (or rerun) can collect the real answer.
            if (not response
                    or "[could not extract response]" in response.lower()
                    or len(response.strip()) < 200):
                print(f"#{num}: response not ready/empty, will retry next pass.")
                pending += 1
                continue

            solved = C.is_solved(response)
            confidence = C.extract_confidence(response)
            status_tag = "[solved]" if solved else "[unsolved]"
            title = C.output_title(num, status_tag, confidence)

            body = (
                f"# Erdős Problem #{num} {status_tag} {confidence}%\n\n"
                f"---\n\n## ChatGPT Response\n\n{response}\n"
            )
            out_file.write_text(body, encoding="utf-8")
            # Human-named copy in outputs/chatgpt/<category>/.
            C.save_output("chatgpt", category, num, title, body)

            renamed = ""
            if do_rename:
                ok = C.rename_chat(page, title)
                renamed = " (renamed)" if ok else " (rename failed)"

            completed += 1
            print(f"#{num}: {status_tag} {confidence}% saved{renamed}")

        except Exception as e:
            print(f"#{num}: ERROR {e}")
            pending += 1

    return completed, pending


def main():
    ap = argparse.ArgumentParser(description="Collect answers and rename Erdős chats")
    ap.add_argument("--category", default=None, help="Limit to one category (default: all in map)")
    ap.add_argument("--watch", action="store_true", help="Keep polling every --interval until all done")
    ap.add_argument("--interval", type=float, default=60.0, help="Seconds between watch passes (default 60)")
    ap.add_argument("--no-rename", action="store_true", help="Save answers but do not rename chats")
    ap.add_argument("--headless", action="store_true", help="Run without a visible window")
    args = ap.parse_args()

    chat_map = C.load_chat_map()
    if not chat_map:
        raise SystemExit(f"No chat map found at {C.CHAT_MAP_FILE}. Run solve_submit.py first.")

    categories = [args.category] if args.category else list(chat_map.keys())

    with sync_playwright() as pw:
        browser = C.launch_browser(pw, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()
        C.ensure_logged_in(page)

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
                browser = C.launch_browser(pw, headless=args.headless)
                page = browser.pages[0] if browser.pages else browser.new_page()
                C.ensure_logged_in(page)

            total_completed = 0
            total_pending = 0
            for cat in categories:
                print(f"\n=== Category: {cat} ===")
                done, pend = process_once(page, cat, do_rename=not args.no_rename)
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
