#!/usr/bin/env python3
"""Build the T2-closable lane: problems a finite computation can settle.

The upstream community database labels a small set of problems ``decidable``
(reduced to a finite computation), ``verifiable`` (a finite computation proves
it if true), or ``falsifiable`` (a finite computation disproves it if false).
These states are exactly the lane where this repository's strongest verified
capability — sandboxed exact computation with independent replay, released as a
T2 ``verified_finite_or_conditional_result`` — can genuinely close something.

The lane is derived *directly from upstream labels* in ``problem_catalog.json``
(build it with ``sync_problem_catalog.py``).  It deliberately carries no
searcher posteriors: these problems are excluded from the searcher's "open"
ranking universe, and a community label is a reduction claim to audit, not a
probability.  Honesty requirements are printed in the lane header:

* the finite computation may still be infeasibly large — estimate the state
  space before committing compute;
* the "finite computation suffices" reduction must be independently audited
  (human intent review) before any release; and
* ``falsifiable`` is decisive only when the statement is false.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

T2_STATES = ("decidable", "verifiable", "falsifiable")
_STATE_MEANING = {
    "decidable": "a finite computation decides the problem either way",
    "verifiable": "a finite computation proves the statement if it is true",
    "falsifiable": "a finite computation disproves the statement if it is false",
}
# Decidable settles the problem unconditionally, verifiable proves on success,
# falsifiable is decisive only on refutation — rank in that order.
_STATE_PRIORITY = {state: rank for rank, state in enumerate(T2_STATES)}

DEFAULT_CATALOG = Path(__file__).resolve().parent / "problem_catalog.json"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "triage" / "rankings"


def _is_formalized(value) -> bool:
    if isinstance(value, dict):
        return str(value.get("state", "")).strip().lower() in {"yes", "true", "formalized"}
    if isinstance(value, str):
        return value.strip().lower() in {"yes", "true", "formalized"}
    return value is True


def build_t2_lane(catalog: dict) -> dict:
    """Select and order the finite-computation-closable problems."""
    problems = catalog.get("problems", {})
    records = []
    for number, entry in problems.items():
        if not isinstance(entry, dict):
            continue
        state = str(entry.get("source_state", "")).strip().lower()
        if state not in _STATE_MEANING:
            continue
        ai_wiki = entry.get("ai_wiki") if isinstance(entry.get("ai_wiki"), dict) else {}
        records.append({
            "problem": int(number),
            "state": state,
            "meaning": _STATE_MEANING[state],
            "formalized": _is_formalized(entry.get("formalized")),
            "tags": list(entry.get("tags", [])),
            "source_last_update": entry.get("source_last_update"),
            "source_problem_url": entry.get("source_problem_url"),
            "ai_wiki_primary_full": bool(ai_wiki.get("primary_full")),
            "ai_wiki_any_signal": bool(ai_wiki),
        })
    records.sort(key=lambda item: (
        _STATE_PRIORITY[item["state"]],
        not item["formalized"],  # formalized statements first: cheaper locked target
        item["problem"],
    ))
    for rank, record in enumerate(records, 1):
        record["rank"] = rank
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "catalog_fetched_at": catalog.get("fetched_at"),
        "source_data_url": catalog.get("source_data_url"),
        "provenance": (
            "Upstream machine-status labels from data/problems.yaml; NOT "
            "searcher posteriors. Each label is a community reduction claim "
            "that must be independently audited before use."
        ),
        "counts": {
            "total": len(records),
            **{state: sum(r["state"] == state for r in records) for state in T2_STATES},
        },
        "problems": records,
    }


def render_t2_markdown(lane: dict) -> str:
    lines = [
        "# T2-Closable Lane — Finite-Computation-Decidable Problems",
        "",
        f"Generated: `{lane['generated_at']}` from catalog fetched "
        f"`{lane.get('catalog_fetched_at')}`.",
        "",
        "> Upstream community machine-status labels (`data/problems.yaml`), **not**",
        "> searcher posteriors. Before attacking any entry: (1) independently audit",
        "> the \"finite computation suffices\" reduction (human intent review);",
        "> (2) estimate the state-space size — a labeled computation may still be",
        "> infeasibly large; (3) remember `falsifiable` is decisive only if the",
        "> statement is false. A completed computation supports at most a",
        "> T2 `verified_finite_or_conditional_result` under the labeled reduction.",
        "",
        "| Rank | Problem | State | Lean statement | AI-wiki signal | Tags |",
        "| ---: | ---: | --- | --- | --- | --- |",
    ]
    for record in lane["problems"]:
        wiki = (
            "full solution reported" if record["ai_wiki_primary_full"]
            else ("activity" if record["ai_wiki_any_signal"] else "none")
        )
        lines.append(
            f"| {record['rank']} | [{record['problem']}]({record['source_problem_url']}) "
            f"| {record['state']} | {'yes' if record['formalized'] else 'no'} "
            f"| {wiki} | {', '.join(record['tags'][:4])} |"
        )
    counts = lane["counts"]
    lines.extend([
        "",
        f"Totals: {counts['total']} problems — "
        + ", ".join(f"{counts[state]} {state}" for state in T2_STATES) + ".",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    lane = build_t2_lane(catalog)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "t2_closable.json").write_text(
        json.dumps(lane, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.output_dir / "t2_closable.md").write_text(
        render_t2_markdown(lane), encoding="utf-8")
    print(
        f"Wrote {lane['counts']['total']} T2-closable problems "
        f"({', '.join(f'{lane['counts'][s]} {s}' for s in T2_STATES)}) to "
        f"{args.output_dir / 't2_closable.md'}"
    )


if __name__ == "__main__":
    main()
