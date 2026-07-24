#!/usr/bin/env python3
"""Build a source-provenance catalog from the online Erdős database.

Besides the upstream ``data/problems.yaml`` status labels, the catalog folds in
the community "AI contributions to Erdős problems" wiki (frozen 2026-06-30) as
per-problem *rediscovery-risk signals*: a wiki-reported full solution means a
"verified novel solution" claim against that problem is very likely a
rediscovery.  Wiki rows are community-reported and unverified — they are
novelty/status metadata only and are never supplied to offline solver prompts.
"""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

from erdos_ingest import MAX_REMOTE_RESPONSE_BYTES, fetch_url

SOURCE_DATA_URL = "https://raw.githubusercontent.com/teorth/erdosproblems/main/data/problems.yaml"
AI_WIKI_URL = (
    "https://raw.githubusercontent.com/wiki/teorth/erdosproblems/"
    "AI-contributions-to-Erd%C5%91s-problems.md"
)
SOURCE_PROBLEM_URL = "https://www.erdosproblems.com/{number}"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "problem_catalog.json"
RESOLVED_STATES = frozenset({
    "proved", "proved (lean)", "disproved", "disproved (lean)",
    "solved", "solved (lean)", "not provable", "not disprovable", "independent",
})

# Wiki table sections.  1(a)-1(d) are primary mathematical contributions;
# 2(a) is literature search (a "full solution found" there means the problem is
# solved in the literature); 2(b)-2(d) are formalization/rewriting/computation.
_WIKI_SECTION_RE = re.compile(r"^#{2,6}\s*(?P<section>[12]\([a-d]\))\.", re.MULTILINE)
_WIKI_PROBLEM_RE = re.compile(r"\[(\d{1,4})\]")
_PRIMARY_SECTIONS = frozenset({"1(a)", "1(b)", "1(c)", "1(d)"})
_LITERATURE_SECTION = "2(a)"
_GREEN, _YELLOW, _RED, _WHITE = "\U0001f7e2", "\U0001f7e1", "\U0001f534", "\u26aa"


def fetch_source(url: str = SOURCE_DATA_URL) -> str:
    return fetch_url(
        url,
        timeout=30,
        max_bytes=MAX_REMOTE_RESPONSE_BYTES,
        user_agent="erdos-proof-catalog/1.0",
    ).decode("utf-8")


def parse_ai_wiki(markdown: str) -> dict[str, dict]:
    """Extract per-problem contribution signals from the wiki markdown.

    Only table rows (lines starting with ``|``) inside a recognized section are
    counted.  The problem number is taken from the row's *first* cell so column
    reordering across sections cannot mislabel a citation as a contribution;
    the color indicator may appear in any cell of the row.
    """
    signals: dict[str, dict] = {}
    current_section = ""
    for line in markdown.splitlines():
        header = _WIKI_SECTION_RE.match(line.strip())
        if header:
            current_section = header.group("section")
            continue
        stripped = line.strip()
        if not current_section or not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells:
            continue
        first_cell_numbers = _WIKI_PROBLEM_RE.findall(cells[0])
        if not first_cell_numbers:
            continue
        row_text = stripped
        for number in first_cell_numbers:
            key = str(int(number))
            entry = signals.setdefault(key, {
                "sections": [],
                "primary_full": False,
                "primary_partial": False,
                "secondary_full": False,
                "incorrect": False,
                "unverified": False,
                "rows": 0,
            })
            entry["rows"] += 1
            if current_section not in entry["sections"]:
                entry["sections"].append(current_section)
            is_primary = current_section in _PRIMARY_SECTIONS
            if _GREEN in row_text:
                if is_primary:
                    entry["primary_full"] = True
                elif current_section == _LITERATURE_SECTION:
                    entry["secondary_full"] = True
            if _YELLOW in row_text and is_primary:
                entry["primary_partial"] = True
            if _RED in row_text:
                entry["incorrect"] = True
            if _WHITE in row_text:
                entry["unverified"] = True
    for entry in signals.values():
        entry["sections"].sort()
    return signals


def build_catalog(
    problems: list[dict], *, fetched_at: str, source_url: str,
    ai_wiki: dict[str, dict] | None = None, ai_wiki_url: str | None = None,
) -> dict:
    entries = {}
    ai_wiki = ai_wiki or {}
    for problem in problems:
        number = str(problem["number"])
        status = problem.get("status") or {}
        state = str(status.get("state", "unknown"))
        entry = {
            "problem": int(number),
            "source_state": state,
            "source_reports_resolved": state.lower() in RESOLVED_STATES,
            "source_last_update": status.get("last_update"),
            "source_problem_url": SOURCE_PROBLEM_URL.format(number=number),
            "formalized": problem.get("formalized"),
            "tags": problem.get("tags", []),
        }
        wiki_entry = ai_wiki.get(number)
        if wiki_entry:
            entry["ai_wiki"] = wiki_entry
        entries[number] = entry
    catalog = {
        "schema_version": 2,
        "fetched_at": fetched_at,
        "source_data_url": source_url,
        "note": "Source status is metadata only and is never supplied to offline solver prompts.",
        "counts": {
            "total": len(entries),
            "source_reports_resolved": sum(
                item["source_reports_resolved"] for item in entries.values()
            ),
            "ai_wiki_primary_full": sum(
                bool(item.get("ai_wiki", {}).get("primary_full"))
                for item in entries.values()
            ),
            "ai_wiki_any_signal": sum(
                "ai_wiki" in item for item in entries.values()
            ),
        },
        "problems": dict(sorted(entries.items(), key=lambda item: int(item[0]))),
    }
    if ai_wiki_url is not None:
        catalog["ai_wiki_url"] = ai_wiki_url
        catalog["ai_wiki_note"] = (
            "Community-reported, unverified rediscovery-risk signals from the "
            "AI-contributions wiki (frozen 2026-06-30); never proof or status "
            "authority."
        )
    return catalog


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=SOURCE_DATA_URL)
    parser.add_argument("--ai-wiki", default=AI_WIKI_URL,
                        help="AI-contributions wiki markdown URL")
    parser.add_argument("--skip-ai-wiki", action="store_true",
                        help="Do not fetch or fold in the AI-contributions wiki")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    problems = yaml.safe_load(fetch_source(args.source))
    ai_wiki = None
    ai_wiki_url = None
    if not args.skip_ai_wiki:
        try:
            ai_wiki = parse_ai_wiki(fetch_source(args.ai_wiki))
            ai_wiki_url = args.ai_wiki
        except Exception as exc:  # noqa: BLE001 - wiki is optional enrichment
            print(f"warning: AI wiki unavailable ({exc}); catalog built without it")
    catalog = build_catalog(
        problems,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        source_url=args.source,
        ai_wiki=ai_wiki,
        ai_wiki_url=ai_wiki_url,
    )
    args.output.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    print(
        f"Wrote {catalog['counts']['total']} problems to {args.output}; "
        f"{catalog['counts']['source_reports_resolved']} reported resolved by source; "
        f"{catalog['counts']['ai_wiki_primary_full']} with wiki-reported full AI solutions."
    )


if __name__ == "__main__":
    main()
