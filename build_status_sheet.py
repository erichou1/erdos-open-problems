#!/usr/bin/env python3
"""Build the data feed for the Erdős × ChatGPT status website.

The website (index.html) is a static single-page app that loads everything at
runtime from ``data.json``. This script (re)generates that feed by scanning the
committed solution copies in ``outputs/chatgpt/open/`` — the filenames already
encode each problem's number, verdict and completeness score, e.g.

    outputs/chatgpt/open/Erdős #117 [solved] 82%.md

so no parsing of file *contents* is required. A GitHub Action re-runs this on
every push that touches ``outputs/``, keeping the site in sync automatically.

Outputs written next to this script:
  * data.json    — the feed the website renders from (problems + totals)
  * status.csv   — the same data as a plain spreadsheet

This script is intentionally self-contained (Python standard library only) and
does NOT import the solving pipeline, so CI can run it with no dependencies.
``status_state.json`` (the Fable/Cooked marks) is owned by the website and is
left untouched here.
"""

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

BASE_DIR = Path(__file__).resolve().parent
CATEGORY = "open"
OUTPUTS_DIR = BASE_DIR / "outputs" / "chatgpt" / CATEGORY
PROBLEMS_DIR = BASE_DIR / CATEGORY / "individual"

DATA_OUT = BASE_DIR / "data.json"
CSV_OUT = BASE_DIR / "status.csv"

# Repo the solution links point at, and the branch they live on.
REPO = "erichou1/erdos-open-problems"
BRANCH = "main"
BLOB_BASE = f"https://github.com/{REPO}/blob/{BRANCH}/"

GREEN_THRESHOLD = 60  # completeness >= this counts as a strong result

# "Erdős #117 [solved] 82%.md"  ->  (117, "solved", "82")
FNAME_RE = re.compile(r"Erdős\s+#(\d+)\s+\[([^\]]+)\]\s+(\d+|\?)\s*%", re.UNICODE)


def all_problem_numbers() -> list:
    """Every open Erdős problem number (one problem_N.tex per problem)."""
    nums = []
    if PROBLEMS_DIR.is_dir():
        for f in PROBLEMS_DIR.glob("problem_*.tex"):
            m = re.search(r"(\d+)", f.stem)
            if m:
                nums.append(int(m.group(1)))
    return sorted(set(nums))


def scan_outputs() -> dict:
    """Map problem number -> best record parsed from the output filenames.

    A problem can have more than one committed copy (e.g. an old "?%" file next
    to a scored one). Keep the most informative: a numeric completeness beats
    "?", a higher score beats a lower one, and "solved" beats "unsolved".
    """
    best = {}
    if not OUTPUTS_DIR.is_dir():
        return best
    for f in sorted(OUTPUTS_DIR.glob("*.md")):
        m = FNAME_RE.search(f.name)
        if not m:
            continue
        num = int(m.group(1))
        status = m.group(2).strip().lower()
        comp = m.group(3)
        comp_val = int(comp) if comp.isdigit() else -1
        rel = f"outputs/chatgpt/{CATEGORY}/{f.name}"
        rec = {
            "n": num,
            "run": True,
            "status": "solved" if status == "solved" else "unsolved",
            "completeness": comp_val if comp_val >= 0 else None,
            "path": rel,
            "blob": BLOB_BASE + quote(rel),
        }
        prev = best.get(num)
        if prev is None:
            best[num] = rec
            continue
        # Prefer the better-scored / solved record.
        prev_score = prev["completeness"] if prev["completeness"] is not None else -1
        new_score = rec["completeness"] if rec["completeness"] is not None else -1
        better = (new_score, rec["status"] == "solved") > (
            prev_score, prev["status"] == "solved")
        if better:
            best[num] = rec
    return best


def build():
    records = scan_outputs()

    # Include every open problem, not just the ones that have been run, so the
    # site can show what is still pending. Problems with no output file get a
    # lightweight "not run" record.
    numbers = all_problem_numbers()
    if not numbers:
        numbers = sorted(records)
    else:
        numbers = sorted(set(numbers) | set(records))

    problems = []
    for n in numbers:
        rec = records.get(n)
        if rec:
            problems.append(rec)
        else:
            problems.append({
                "n": n, "run": False, "status": None,
                "completeness": None, "path": None, "blob": None,
            })

    total = len(numbers)
    run_recs = [r for r in problems if r["run"]]
    run = len(run_recs)
    solved = sum(1 for r in run_recs if r["status"] == "solved")
    scored = [r["completeness"] for r in run_recs if r["completeness"] is not None]
    green = sum(1 for c in scored if c >= GREEN_THRESHOLD)
    avg = round(sum(scored) / len(scored), 1) if scored else 0

    feed = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": REPO,
        "branch": BRANCH,
        "category": CATEGORY,
        "green_threshold": GREEN_THRESHOLD,
        "totals": {
            "total": total,
            "run": run,
            "pending": total - run,
            "solved": solved,
            "green": green,
            "avg_completeness": avg,
        },
        "problems": problems,
    }
    DATA_OUT.write_text(
        json.dumps(feed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with CSV_OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["problem", "run", "status", "completeness", "link"])
        for r in problems:
            comp = "" if r["completeness"] is None else r["completeness"]
            w.writerow([r["n"], "yes" if r["run"] else "no",
                        r["status"] or "", comp, r["blob"] or ""])

    print(f"wrote {DATA_OUT.name} and {CSV_OUT.name} "
          f"({run}/{total} run, {total - run} pending, {solved} solved, "
          f"{green} >= {GREEN_THRESHOLD}%)")


if __name__ == "__main__":
    build()
