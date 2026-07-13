#!/usr/bin/env python3
"""Operational novelty / rediscovery check from first-party corpus data.

A "verified" result is worthless as *new mathematics* if the problem is already
solved (in the DB, in the forum, or formalized elsewhere). This probe reads the
catalog record and the fetched forum thread for a problem and flags prior-work
signals, so a promotion can be labelled `independent_rediscovery` /
`literature_identification` instead of a novel resolution.

It is deliberately heuristic and offline (no web calls); it only surfaces
signals from data already in the repository for a human/independent decision.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

CLAIM_PATTERNS = {
    "solution_claim": r"\b(solved|resolved|proof of|proved|disproved|counterexample|settles?)\b",
    "formalization": r"\b(lean\b|mathlib|formaliz|aristotle|coq\b|isabelle)\b",
    "already_known": r"\b(already (?:known|proved|solved)|well[- ]known|in the literature|classical result|due to)\b",
}
_RESOLVED_STATES = {"solved", "proved", "proven", "disproved", "resolved", "closed"}


def _catalog_entry(root: Path, problem_number: int) -> dict:
    try:
        catalog = json.loads((Path(root) / "problem_catalog.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    entry = catalog.get("problems", {}).get(str(problem_number), {})
    return entry if isinstance(entry, dict) else {}


def _forum_comments(root: Path, problem_number: int) -> list[str]:
    path = Path(root) / "forum_threads" / f"{problem_number}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    comments = data.get("comments", []) if isinstance(data, dict) else []
    return [str(c.get("text", "")) for c in comments if isinstance(c, dict)]


def _is_formalized(value) -> bool:
    if isinstance(value, dict):
        return str(value.get("state", "")).strip().lower() in {
            "yes", "true", "formalized", "proved", "proved (lean)",
        }
    if isinstance(value, str):
        return value.strip().lower() in {"yes", "true", "formalized"}
    return value is True


def probe_novelty(root: Path, problem_number: int) -> dict:
    """Classify prior-work signals for one problem."""
    entry = _catalog_entry(Path(root), problem_number)
    source_state = str(entry.get("source_state", "unknown")).strip().lower()
    resolved = bool(entry.get("source_reports_resolved"))
    comments = _forum_comments(Path(root), problem_number)
    text = "\n".join(comments)
    signals = sorted(
        name for name, pattern in CLAIM_PATTERNS.items()
        if re.search(pattern, text, re.IGNORECASE)
    )
    formalized = _is_formalized(entry.get("formalized")) or "formalization" in signals

    if resolved or source_state in _RESOLVED_STATES:
        status = "source_resolved"
    elif formalized or "solution_claim" in signals or "already_known" in signals:
        status = "prior_work_signal"
    else:
        status = "no_signal"

    return {
        "problem_number": problem_number,
        "novelty_status": status,
        "source_state": source_state,
        "source_reports_resolved": resolved,
        "formalized": formalized,
        "forum_comment_count": len(comments),
        "forum_claim_signals": signals,
        "is_likely_novel": status == "no_signal",
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem_number", type=int)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(probe_novelty(args.root, args.problem_number), indent=2))


if __name__ == "__main__":
    main()
