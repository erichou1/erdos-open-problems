#!/usr/bin/env python3
"""Build a source-provenance catalog from the online Erdős database."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import yaml

SOURCE_DATA_URL = "https://raw.githubusercontent.com/teorth/erdosproblems/main/data/problems.yaml"
SOURCE_PROBLEM_URL = "https://www.erdosproblems.com/{number}"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "problem_catalog.json"
RESOLVED_STATES = frozenset({
    "proved", "proved (lean)", "disproved", "disproved (lean)",
    "solved", "solved (lean)", "not provable", "not disprovable", "independent",
})


def fetch_source(url: str = SOURCE_DATA_URL) -> str:
    request = Request(url, headers={"User-Agent": "erdos-proof-catalog/1.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def build_catalog(problems: list[dict], *, fetched_at: str, source_url: str) -> dict:
    entries = {}
    for problem in problems:
        number = str(problem["number"])
        status = problem.get("status") or {}
        state = str(status.get("state", "unknown"))
        entries[number] = {
            "problem": int(number),
            "source_state": state,
            "source_reports_resolved": state.lower() in RESOLVED_STATES,
            "source_last_update": status.get("last_update"),
            "source_problem_url": SOURCE_PROBLEM_URL.format(number=number),
            "formalized": problem.get("formalized"),
            "tags": problem.get("tags", []),
        }
    return {
        "schema_version": 1,
        "fetched_at": fetched_at,
        "source_data_url": source_url,
        "note": "Source status is metadata only and is never supplied to offline solver prompts.",
        "counts": {
            "total": len(entries),
            "source_reports_resolved": sum(
                item["source_reports_resolved"] for item in entries.values()
            ),
        },
        "problems": dict(sorted(entries.items(), key=lambda item: int(item[0]))),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=SOURCE_DATA_URL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    problems = yaml.safe_load(fetch_source(args.source))
    catalog = build_catalog(
        problems,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        source_url=args.source,
    )
    args.output.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    print(
        f"Wrote {catalog['counts']['total']} problems to {args.output}; "
        f"{catalog['counts']['source_reports_resolved']} reported resolved by source."
    )


if __name__ == "__main__":
    main()
