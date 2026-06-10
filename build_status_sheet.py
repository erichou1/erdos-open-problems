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


def total_open_problems() -> int:
    """Count of open Erdős problems (one .tex per problem), for the headline %."""
    if PROBLEMS_DIR.is_dir():
        n = sum(1 for _ in PROBLEMS_DIR.glob("problem_*.tex"))
        if n:
            return n
    return 0


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
    problems = sorted(records.values(), key=lambda r: r["n"])

    total = total_open_problems() or len(problems)
    run = len(problems)
    solved = sum(1 for r in problems if r["status"] == "solved")
    scored = [r["completeness"] for r in problems if r["completeness"] is not None]
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
            w.writerow([r["n"], "yes", r["status"], comp, r["blob"]])

    print(f"wrote {DATA_OUT.name} and {CSV_OUT.name} "
          f"({run}/{total} run, {solved} solved, {green} >= {GREEN_THRESHOLD}%)")


if __name__ == "__main__":
    build()
