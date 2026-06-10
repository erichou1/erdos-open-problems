#!/usr/bin/env python3
"""Build a visual status spreadsheet of the ChatGPT runs.

Scans the saved ChatGPT solutions and produces, for every open Erdős problem:
  * whether it has been run,
  * the verdict ([solved] / [unsolved]),
  * the model's completeness score (>= 60% is shown green),
  * a link to the full solution rendered on GitHub,
  * editable "Fable" and "Cooked" checkboxes that persist across computers.

Files written next to this script:
  * status.csv         — plain spreadsheet (incl. fable/cooked columns)
  * index.html         — interactive, color-coded table (GitHub Pages home)
  * status_state.json  — the checkbox state (created if missing). Commit this
                         file to share Fable/Cooked marks with other computers.

DeepSeek is intentionally excluded; this only reports the ChatGPT pipeline.
"""

import csv
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

import erdos_common as C

BASE_DIR = Path(__file__).resolve().parent
SOLUTIONS_DIR = C.REPO_DIR / "solutions"
OUTPUTS_DIR = BASE_DIR / "outputs" / "chatgpt"
CSV_OUT = BASE_DIR / "status.csv"
HTML_OUT = BASE_DIR / "index.html"
STATE_OUT = BASE_DIR / "status_state.json"

# Repo the solution links point at, and the branch they live on.
REPO = "erichou1/erdos-open-problems"
BRANCH = "main"
BLOB_BASE = f"https://github.com/{REPO}/blob/{BRANCH}/"

GREEN_THRESHOLD = 60  # completeness >= this is shown green


def load_state() -> dict:
    """Persisted Fable/Cooked marks: {"349": {"fable": true, "cooked": false}}."""
    if STATE_OUT.exists():
        try:
            return json.loads(STATE_OUT.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return {}
    return {}


def find_output_file(category: str, num: int):
    """Repo-relative path to the human-named output copy for a problem, if any."""
    cat_dir = OUTPUTS_DIR / category
    if not cat_dir.is_dir():
        return None
    for f in cat_dir.glob(f"Erd\u0151s #{num} *.md"):
        return f"outputs/chatgpt/{category}/{f.name}"
    return None


def scan_category(category: str, state: dict) -> list:
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
        link = None
        if sol.exists():
            text = sol.read_text(encoding="utf-8", errors="ignore")
            head = text.splitlines()[0] if text else ""
            m = re.search(r"(\[[^\]]+\])", head)
            status = m.group(1).strip("[]") if m else (
                "solved" if C.is_solved(text) else "unsolved")
            completeness = C.extract_completeness(text)
            run = True
            rel = find_output_file(category, num)
            if rel:
                link = BLOB_BASE + quote(rel)
        marks = state.get(str(num), {})
        rows.append({
            "problem": num,
            "category": category,
            "run": "yes" if run else "no",
            "status": status,
            "completeness": completeness,
            "link": link or "",
            "fable": "yes" if marks.get("fable") else "no",
            "cooked": "yes" if marks.get("cooked") else "no",
        })
    return rows


def write_csv(rows: list):
    with CSV_OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "problem", "category", "run", "status", "completeness",
            "fable", "cooked", "link"])
        w.writeheader()
        w.writerows(rows)


def write_state_if_missing(rows: list):
    """Create status_state.json from current marks if it does not yet exist."""
    if STATE_OUT.exists():
        return
    state = {
        str(r["problem"]): {
            "fable": r["fable"] == "yes",
            "cooked": r["cooked"] == "yes",
        }
        for r in rows if r["run"] == "yes"
    }
    STATE_OUT.write_text(json.dumps(state, indent=2, ensure_ascii=False),
                         encoding="utf-8")


def write_html(rows: list, state: dict):
    total = len(rows)
    run_rows = [r for r in rows if r["run"] == "yes"]
    run = len(run_rows)
    solved = sum(1 for r in run_rows if r["status"] == "solved")
    green = sum(1 for r in run_rows
                if r["completeness"].isdigit()
                and int(r["completeness"]) >= GREEN_THRESHOLD)

    cells = []
    for r in rows:
        run_yes = r["run"] == "yes"
        comp = r["completeness"]
        is_green = comp.isdigit() and int(comp) >= GREEN_THRESHOLD
        comp_disp = f"{comp}%" if comp else ("\u2014" if run_yes else "")
        status_disp = r["status"] if run_yes else "not run"
        row_class = []
        if not run_yes:
            row_class.append("notrun")
        elif is_green:
            row_class.append("green")
        else:
            row_class.append("amber")

        if run_yes and r["link"]:
            prob_cell = (f'<a href="{html.escape(r["link"])}" target="_blank" '
                         f'rel="noopener">#{r["problem"]}</a>')
        else:
            prob_cell = f'#{r["problem"]}'

        pid = r["problem"]
        if run_yes:
            fable_box = (f'<input type="checkbox" data-kind="fable" '
                         f'data-id="{pid}">')
            cooked_box = (f'<input type="checkbox" data-kind="cooked" '
                          f'data-id="{pid}">')
        else:
            fable_box = cooked_box = ""

        cells.append(
            f'<tr class="{" ".join(row_class)}" data-id="{pid}">'
            f'<td class="num">{prob_cell}</td>'
            f'<td class="run">{"&#10003;" if run_yes else ""}</td>'
            f'<td class="status">{html.escape(status_disp)}</td>'
            f'<td class="comp">{comp_disp}</td>'
            f'<td class="chk">{fable_box}</td>'
            f'<td class="chk">{cooked_box}</td>'
            f"</tr>"
        )

    rows_html = "\n".join(cells)
    pct_run = (100 * run / total) if total else 0
    initial_state = json.dumps(state, ensure_ascii=False)

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Erdős x ChatGPT - Run Status</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
          margin: 2rem; color: #1c2331; }}
  h1 {{ margin: 0 0 .25rem; font-size: 1.4rem; }}
  .sub {{ color: #5a5a6a; margin: 0 0 1rem; max-width: 60rem; }}
  .cards {{ display: flex; gap: .75rem; flex-wrap: wrap; margin-bottom: 1rem; }}
  .card {{ background: #f4f4f6; border-radius: 10px; padding: .6rem 1rem;
           min-width: 88px; }}
  .card b {{ display: block; font-size: 1.4rem; }}
  .card span {{ color: #5a5a6a; font-size: .8rem; }}
  .bar {{ display: flex; gap: .5rem; align-items: center; margin-bottom: 1rem;
          flex-wrap: wrap; }}
  button {{ font: inherit; padding: .45rem .8rem; border: 1px solid #c9ccd6;
            background: #fff; border-radius: 8px; cursor: pointer; }}
  button.primary {{ background: #1c2331; color: #fff; border-color: #1c2331; }}
  #saved {{ color: #1a7f37; font-size: .85rem; }}
  input[type=search] {{ font: inherit; padding: .45rem .6rem; border: 1px solid #c9ccd6;
            border-radius: 8px; min-width: 12rem; }}
  table {{ border-collapse: collapse; width: 100%; font-size: .9rem; }}
  th, td {{ padding: .35rem .6rem; text-align: left;
            border-bottom: 1px solid #ececf1; }}
  th {{ position: sticky; top: 0; background: #1c2331; color: #fff;
        font-weight: 600; }}
  td.num a {{ font-weight: 600; color: #0b62d6; text-decoration: none; }}
  td.num a:hover {{ text-decoration: underline; }}
  td.run {{ text-align: center; color: #1a7f37; font-weight: 700; }}
  td.comp {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.chk {{ text-align: center; }}
  td.chk input {{ width: 1.05rem; height: 1.05rem; cursor: pointer; }}
  tr.green td.status {{ color: #1a7f37; font-weight: 700; }}
  tr.green td.comp {{ background: #d7f4dd; font-weight: 700; }}
  tr.amber td.comp {{ background: #fdeede; }}
  tr.notrun td {{ color: #9aa0ad; }}
  tr:hover td {{ background: #fafbff; }}
</style>
</head>
<body>
  <h1>Erdos Problems x ChatGPT - Run Status</h1>
  <p class="sub">Each problem links to its full solution on GitHub. Completeness =
     how much of the argument the model rigorously established (not its confidence);
     {GREEN_THRESHOLD}%+ is green. Tick <b>Fable</b> once a solution has been run
     through Fable, and <b>Cooked</b> if it's cooked. DeepSeek excluded.</p>
  <div class="cards">
    <div class="card"><b>{total}</b><span>open problems</span></div>
    <div class="card"><b>{run}</b><span>run ({pct_run:.0f}%)</span></div>
    <div class="card"><b>{solved}</b><span>solved</span></div>
    <div class="card"><b>{green}</b><span>&ge;{GREEN_THRESHOLD}% complete</span></div>
  </div>
  <div class="bar">
    <input type="search" id="filter" placeholder="Filter by problem #...">
    <button id="onlyrun">Show only run</button>
    <button class="primary" id="save">Save marks (download JSON)</button>
    <span id="saved"></span>
  </div>
  <table id="t">
    <thead>
      <tr>
        <th>Problem</th>
        <th>Run</th>
        <th>Status</th>
        <th>Completeness</th>
        <th>Fable</th>
        <th>Cooked</th>
      </tr>
    </thead>
    <tbody>
{rows_html}
    </tbody>
  </table>

<script>
const LS_KEY = "erdos_chatgpt_marks_v1";
const INITIAL_STATE = {initial_state};

function loadLocal() {{
  try {{ return JSON.parse(localStorage.getItem(LS_KEY)) || {{}}; }}
  catch (e) {{ return {{}}; }}
}}
let state = Object.assign({{}}, INITIAL_STATE, loadLocal());

function applyState() {{
  document.querySelectorAll('input[type=checkbox]').forEach(cb => {{
    const id = cb.dataset.id, kind = cb.dataset.kind;
    cb.checked = !!(state[id] && state[id][kind]);
  }});
}}

// Pull the freshest committed marks (works when served via GitHub Pages).
fetch('status_state.json', {{cache: 'no-store'}})
  .then(r => r.ok ? r.json() : null)
  .then(remote => {{
    if (remote) {{
      state = Object.assign({{}}, remote, loadLocal());
      applyState();
    }}
  }})
  .catch(() => {{}});

function saveLocal() {{
  localStorage.setItem(LS_KEY, JSON.stringify(state));
  const s = document.getElementById('saved');
  s.textContent = 'saved locally';
  setTimeout(() => {{ s.textContent = ''; }}, 1500);
}}

document.querySelector('tbody').addEventListener('change', e => {{
  const cb = e.target;
  if (cb.type !== 'checkbox') return;
  const id = cb.dataset.id, kind = cb.dataset.kind;
  state[id] = state[id] || {{}};
  state[id][kind] = cb.checked;
  saveLocal();
}});

document.getElementById('save').addEventListener('click', () => {{
  const blob = new Blob([JSON.stringify(state, null, 2)],
                        {{type: 'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'status_state.json';
  a.click();
  URL.revokeObjectURL(a.href);
}});

document.getElementById('filter').addEventListener('input', e => {{
  const q = e.target.value.trim();
  document.querySelectorAll('tbody tr').forEach(tr => {{
    tr.style.display = (q && !('#' + tr.dataset.id).includes(q)) ? 'none' : '';
  }});
}});

let onlyRun = false;
document.getElementById('onlyrun').addEventListener('click', e => {{
  onlyRun = !onlyRun;
  e.target.textContent = onlyRun ? 'Show all' : 'Show only run';
  document.querySelectorAll('tbody tr').forEach(tr => {{
    if (onlyRun && tr.classList.contains('notrun')) tr.style.display = 'none';
    else tr.style.display = '';
  }});
}});

applyState();
</script>
</body>
</html>
"""
    HTML_OUT.write_text(html_doc, encoding="utf-8")


def main():
    state = load_state()
    rows = scan_category("open", state)
    rows.sort(key=lambda r: r["problem"])
    write_csv(rows)
    write_state_if_missing(rows)
    state = load_state()  # reload in case it was just created
    write_html(rows, state)
    run = sum(1 for r in rows if r["run"] == "yes")
    print(f"wrote {CSV_OUT.name}, {HTML_OUT.name}, {STATE_OUT.name} "
          f"({run}/{len(rows)} problems run)")


if __name__ == "__main__":
    main()
