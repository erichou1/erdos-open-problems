#!/usr/bin/env python3
"""Build a visual status spreadsheet of the ChatGPT runs.

Scans the saved ChatGPT solutions and produces, for every open Erdős problem:
  * whether it has been run,
  * the verdict ([solved] / [unsolved]),
  * the model's completeness score.

Two files are written next to this script:
  * status.csv  — plain spreadsheet (problem, run, status, completeness)
  * status.html — color-coded table you can open in a browser

DeepSeek is intentionally excluded; this only reports the ChatGPT pipeline.
"""

import csv
import html
import re
from pathlib import Path

import erdos_common as C

BASE_DIR = Path(__file__).resolve().parent
SOLUTIONS_DIR = C.REPO_DIR / "solutions"
CSV_OUT = BASE_DIR / "status.csv"
HTML_OUT = BASE_DIR / "status.html"

HEADER_RE = re.compile(r"#\s*Erd\u0151s Problem #(\d+)\s*(\[[^\]]+\])?\s*(\S+?)%?\s*$")


def scan_category(category: str) -> list[dict]:
    """Return one row per open problem in *category*, in numeric order."""
    files = C.get_problem_files(category)
    sol_dir = SOLUTIONS_DIR / category
    rows = []
    for f in files:
        num = C.problem_number(f)
        sol = sol_dir / f"solution_{num}.md"
        status = ""
        completeness = ""
        run = False
        if sol.exists():
            text = sol.read_text(encoding="utf-8", errors="ignore")
            head = text.splitlines()[0] if text else ""
            # Verdict from the saved header (falls back to a re-parse).
            m = re.search(r"(\[[^\]]+\])", head)
            status = m.group(1).strip("[]") if m else (
                "solved" if C.is_solved(text) else "unsolved")
            completeness = C.extract_completeness(text)
            run = True
        rows.append({
            "problem": num,
            "category": category,
            "run": "yes" if run else "no",
            "status": status,
            "completeness": completeness,
        })
    return rows


def write_csv(rows: list[dict]):
    with CSV_OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(
            fh, fieldnames=["problem", "category", "run", "status", "completeness"])
        w.writeheader()
        w.writerows(rows)


def _completeness_color(value: str) -> str:
    """Green-to-red shading by completeness score; grey if unknown."""
    if not value or value == "?":
        return "#e9e9ee"
    try:
        pct = max(0, min(100, int(value)))
    except ValueError:
        return "#e9e9ee"
    # 0% -> red (0deg), 100% -> green (120deg)
    hue = int(120 * pct / 100)
    return f"hsl({hue}, 70%, 85%)"


def write_html(rows: list[dict]):
    total = len(rows)
    run_rows = [r for r in rows if r["run"] == "yes"]
    run = len(run_rows)
    solved = sum(1 for r in run_rows if r["status"] == "solved")
    unsolved = run - solved

    cells = []
    for r in rows:
        run_yes = r["run"] == "yes"
        comp = r["completeness"]
        comp_disp = f"{comp}%" if comp else ("\u2014" if run_yes else "")
        status_disp = r["status"] if run_yes else "not run"
        status_class = (
            "solved" if r["status"] == "solved"
            else "unsolved" if run_yes else "notrun")
        comp_bg = _completeness_color(comp) if run_yes else "transparent"
        cells.append(
            f'<tr class="{status_class}">'
            f'<td class="num">#{r["problem"]}</td>'
            f'<td class="run">{"&#10003;" if run_yes else ""}</td>'
            f'<td class="status">{html.escape(status_disp)}</td>'
            f'<td class="comp" style="background:{comp_bg}">{comp_disp}</td>'
            f"</tr>"
        )

    rows_html = "\n".join(cells)
    pct_run = (100 * run / total) if total else 0
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Erdős x ChatGPT — Run Status</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
          margin: 2rem; color: #1c2331; }}
  h1 {{ margin: 0 0 .25rem; font-size: 1.4rem; }}
  .sub {{ color: #5a5a6a; margin: 0 0 1.25rem; }}
  .cards {{ display: flex; gap: .75rem; flex-wrap: wrap; margin-bottom: 1.25rem; }}
  .card {{ background: #f4f4f6; border-radius: 10px; padding: .6rem 1rem;
           min-width: 90px; }}
  .card b {{ display: block; font-size: 1.4rem; }}
  .card span {{ color: #5a5a6a; font-size: .8rem; }}
  table {{ border-collapse: collapse; width: 100%; font-size: .9rem; }}
  th, td {{ padding: .35rem .6rem; text-align: left;
            border-bottom: 1px solid #ececf1; }}
  th {{ position: sticky; top: 0; background: #1c2331; color: #fff;
        font-weight: 600; }}
  td.num {{ font-variant-numeric: tabular-nums; font-weight: 600; }}
  td.run {{ text-align: center; color: #1a7f37; font-weight: 700; }}
  td.comp {{ text-align: right; font-variant-numeric: tabular-nums; }}
  tr.solved td.status {{ color: #1a7f37; font-weight: 700; }}
  tr.unsolved td.status {{ color: #9a3412; }}
  tr.notrun td {{ color: #9aa0ad; }}
  tr:hover td {{ background: #fafbff; }}
</style>
</head>
<body>
  <h1>Erdős Problems × ChatGPT — Run Status</h1>
  <p class="sub">Completeness score = how much of the argument the model rigorously
     established (not its confidence). DeepSeek excluded.</p>
  <div class="cards">
    <div class="card"><b>{total}</b><span>open problems</span></div>
    <div class="card"><b>{run}</b><span>run ({pct_run:.0f}%)</span></div>
    <div class="card"><b>{solved}</b><span>solved</span></div>
    <div class="card"><b>{unsolved}</b><span>unsolved</span></div>
  </div>
  <table>
    <thead>
      <tr><th>Problem</th><th>Run</th><th>Status</th><th>Completeness</th></tr>
    </thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
</body>
</html>
"""
    HTML_OUT.write_text(html_doc, encoding="utf-8")


def main():
    rows = scan_category("open")
    rows.sort(key=lambda r: r["problem"])
    write_csv(rows)
    write_html(rows)
    run = sum(1 for r in rows if r["run"] == "yes")
    print(f"wrote {CSV_OUT.name} and {HTML_OUT.name} "
          f"({run}/{len(rows)} problems run)")


if __name__ == "__main__":
    main()
