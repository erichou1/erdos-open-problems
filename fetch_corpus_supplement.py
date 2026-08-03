#!/usr/bin/env python3
"""Fetch supplemental corpus statements for problems outside the open snapshot.

The open-only corpus snapshot (``all_open_problems.tex``) omits problems whose
upstream state is ``decidable``/``falsifiable``/``verifiable`` — exactly the
T2-closable lane where a finite computation can genuinely settle a problem.
This script fetches each missing statement verbatim from
``https://www.erdosproblems.com/latex/{n}`` (the same source the open corpus was
built from) into ``corpus_supplement/problem_{n}.tex``, where
``egmra.corpus.sources.from_erdos_number`` resolves it as a fallback.

Honesty properties: statements are fetched byte-for-byte with a provenance
comment header (URL, UTC time, sha256 of the payload) — never fabricated or
edited; existing files are never overwritten unless ``--refresh``; each file is
re-validated through the exact production extractor before being written, so an
unextractable payload is reported, not stored silently.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from egmra.corpus.tex_extract import SourceExtractionError, extract_tex_statement
from erdos_ingest import (
    MAX_REMOTE_RESPONSE_BYTES,
    extract_source_page,
    fetch_url,
    render_tex,
)

STATEMENT_URL = "https://www.erdosproblems.com/latex/{number}"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "corpus_supplement"
DEFAULT_T2_LANE = (
    Path(__file__).resolve().parent / "triage" / "rankings" / "t2_closable.json"
)
DEFAULT_CATALOG = Path(__file__).resolve().parent / "problem_catalog.json"


def t2_lane_numbers(lane_path: Path) -> list[int]:
    document = json.loads(lane_path.read_text(encoding="utf-8"))
    return [
        int(row["problem"]) for row in document.get("problems", [])
        if isinstance(row, dict) and isinstance(row.get("problem"), int)
    ]


def _catalog_entry(catalog_path: Path, number: int) -> dict:
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        entry = catalog.get("problems", {}).get(str(number), {})
    except (OSError, ValueError):
        entry = {}
    return entry if isinstance(entry, dict) else {}


def fetch_statement_tex(number: int, *, fetcher=None) -> bytes:
    fetch = fetcher or (lambda url: fetch_url(
        url, timeout=30, max_bytes=MAX_REMOTE_RESPONSE_BYTES,
        user_agent="erdos-corpus-supplement/1.0",
    ))
    return fetch(STATEMENT_URL.format(number=number))


def build_supplement_file(
    number: int, payload: bytes, *, fetched_at: str, catalog_entry: dict | None = None,
) -> str:
    """Provenance header + canonical TeX rendered by the production extractor.

    ``payload`` is the first-party HTML page from ``/latex/{n}``; the statement,
    remarks, and references are extracted by the exact hardened parser the
    corpus ingest uses (:func:`erdos_ingest.extract_source_page`) and rendered
    with :func:`erdos_ingest.render_tex` — the same format as the open-corpus
    ``problem_N.tex`` files.  The result is re-validated through the production
    statement extractor before it is returned; nothing is fabricated.
    """
    statement, remarks, references = extract_source_page(payload)
    entry = dict(catalog_entry or {})
    tex = render_tex(
        {
            "number": number,
            "status": {"last_update": entry.get("source_last_update") or "unknown"},
            "tags": entry.get("tags") or [],
            "prize": entry.get("prize") or "no",
        },
        statement, remarks, references,
    )
    check = extract_tex_statement(tex)  # raises SourceExtractionError
    if not check.strip():
        raise SourceExtractionError(f"problem {number}: extracted statement is empty")
    header = (
        f"% corpus_supplement: Erd\u0151s problem #{number}\n"
        f"% source: {STATEMENT_URL.format(number=number)}\n"
        f"% fetched_at: {fetched_at}\n"
        f"% payload_sha256: {hashlib.sha256(payload).hexdigest()}\n"
        "% statement/remarks/references extracted by erdos_ingest.extract_source_page;\n"
        "% rendered by erdos_ingest.render_tex — do not edit\n"
    )
    return header + tex


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problems", default="",
                        help="comma/space-separated problem numbers; default = "
                             "every problem in the T2-closable lane")
    parser.add_argument("--t2-lane", type=Path, default=DEFAULT_T2_LANE,
                        help="t2_closable.json used when --problems is empty")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG,
                        help="problem catalog supplying tags/prize/last-update metadata")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--refresh", action="store_true",
                        help="re-fetch and overwrite existing supplement files")
    args = parser.parse_args()

    if args.problems.strip():
        numbers = [int(tok) for tok in args.problems.replace(",", " ").split()]
    else:
        numbers = t2_lane_numbers(args.t2_lane)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    written, skipped, failed = [], [], []
    for number in numbers:
        target = args.output_dir / f"problem_{number}.tex"
        if target.exists() and not args.refresh:
            skipped.append(number)
            continue
        fetched_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            payload = fetch_statement_tex(number)
            content = build_supplement_file(
                number, payload, fetched_at=fetched_at,
                catalog_entry=_catalog_entry(args.catalog, number))
        except (SourceExtractionError, UnicodeDecodeError, OSError, ValueError) as exc:
            failed.append((number, f"{type(exc).__name__}: {exc}"))
            continue
        target.write_text(content, encoding="utf-8")
        written.append(number)
        time.sleep(1.0)  # be polite to the upstream site

    print(f"written: {len(written)} {written}")
    print(f"skipped (already present): {len(skipped)} {skipped}")
    for number, reason in failed:
        print(f"FAILED #{number}: {reason}")
    if failed:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
