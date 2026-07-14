"""Build a retrieval corpus of TheoremRecords from the packaged Erdős snapshot.

Wires real literature retrieval into the production CLI (task 4.4): each open
problem in the corpus TeX becomes an auditable :class:`TheoremRecord` with a
source URI, content hash, and verbatim statement, so the frozen literature
packet handed to a worker after the blind cold pass has real provenance instead
of being empty. A retrieved record generates hypotheses/provenance only — it
never establishes proof status.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from egmra.corpus.tex_extract import SourceExtractionError, extract_tex_statement
from egmra.provenance.hashing import sha256_hex
from egmra.retrieval.records import TheoremRecord

_SECTION = re.compile(r"\\section\{Problem \\#(\d+)\}")
_MAX_TEX_BYTES = 64_000_000


def build_erdos_corpus(
    corpus_tex_path: str | Path,
    catalog_path: str | Path | None = None,
    *,
    limit: int | None = None,
) -> list[TheoremRecord]:
    """Parse the corpus TeX into auditable :class:`TheoremRecord` objects."""
    tex_path = Path(corpus_tex_path)
    if tex_path.is_symlink() or not tex_path.is_file():
        raise ValueError(f"corpus TeX must be a regular non-symlink file: {tex_path}")
    if tex_path.stat().st_size > _MAX_TEX_BYTES:
        raise ValueError(f"corpus TeX is too large: {tex_path}")
    tex = tex_path.read_text(encoding="utf-8")

    catalog: dict = {}
    if catalog_path and Path(catalog_path).is_file():
        try:
            catalog = json.loads(Path(catalog_path).read_text(encoding="utf-8")).get(
                "problems", {}) or {}
        except (OSError, ValueError):
            catalog = {}

    matches = list(_SECTION.finditer(tex))
    records: list[TheoremRecord] = []
    seen: set[int] = set()
    for index, match in enumerate(matches):
        if limit is not None and len(records) >= limit:
            break
        number = int(match.group(1))
        if number in seen:
            continue
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(tex)
        try:
            statement = extract_tex_statement(tex[start:end]).strip()
        except SourceExtractionError:
            continue
        if not statement:
            continue
        seen.add(number)
        meta = catalog.get(str(number), {}) if isinstance(catalog, dict) else {}
        tags = tuple(meta.get("tags", [])) if isinstance(meta.get("tags"), list) else ()
        state = str(meta.get("source_state", "")).strip().lower()
        records.append(TheoremRecord(
            theorem_id=f"erdos-{number}",
            canonical_statement=statement,
            conclusion=statement,
            source_uri=str(meta.get("source_problem_url")
                           or f"https://www.erdosproblems.com/{number}"),
            source_version=str(meta.get("source_last_update", "")) or "corpus-snapshot",
            source_content_hash=sha256_hex(statement),
            verbatim_theorem_and_hypothesis_extract=statement,
            extraction_method="tex_corpus",
            retrieved_at=str(meta.get("source_last_update", "")),
            authors=tags,  # topical tags stand in for the topical index
            proof_status="open" if state == "open" else "unknown",
            license="erdosproblems.com snapshot",
        ))
    return records
