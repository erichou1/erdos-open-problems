#!/usr/bin/env python3
"""Fail unless local open-problem files exactly match catalog state `open`."""

import json
from pathlib import Path

from erdos_searcher import audit_corpus


def main() -> None:
    root = Path(__file__).resolve().parent
    catalog = json.loads((root / "problem_catalog.json").read_text(encoding="utf-8"))
    paths = list((root / "open" / "individual").glob("problem_*.tex"))
    result = audit_corpus(catalog, paths)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
