"""Arbitrary-problem source resolution (spec §8.1, §13.6 arbitrary entry point).

The production run path must accept a *real* problem, not a bundled fixture.
This module turns three honest inputs into a frozen :class:`ProblemInput`:

* a verbatim statement string (``--statement``),
* a statement file (``--statement-file``), or
* an Erdős problem number resolved from the local corpus snapshot
  (``--erdos N``), which extracts the exact theorem statement from
  ``all_open_problems.tex`` and its dated status claim from
  ``problem_catalog.json``.

No input is fabricated: an unknown Erdős number or a corpus without the exact
``\\textbf{Statement:}`` boundary raises :class:`SourceResolutionError` rather
than inventing a statement. File reads reject symlinks, non-regular files, and
oversized payloads, matching the rest of the codebase's boundary hardening.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import egmra
from egmra.corpus.status import STATUS_VALUES, StatusClaim
from egmra.provenance.hashing import sha256_hex

# Upstream ``source_state`` values are mapped onto the reconciler's vocabulary.
# The three machine-status states are upstream-defined as "appear to be open,
# but ..." (reduced to / provable by / disprovable by a finite computation), so
# they honestly map to ``open`` — the finite reduction is metadata for the
# T2-closable lane, not a resolution claim.
_STATUS_MAP = {
    "open": "open",
    "decidable": "open",
    "falsifiable": "open",
    "verifiable": "open",
    "solved": "known",
    "known": "known",
    "false": "false",
    "disproved": "false",
    "refuted": "false",
    "misquoted": "misquoted",
    "ambiguous": "ambiguous",
}

_MAX_STATEMENT_BYTES = 1_000_000
_MAX_CATALOG_BYTES = 16_000_000
_MAX_CORPUS_BYTES = 64_000_000

_SECTION_RE = r"\\section\{Problem \\#%d\}(?![0-9])"
_NEXT_SECTION_RE = re.compile(r"\n%%\s*=+|\\section\{Problem \\#\d+\}")


class SourceResolutionError(ValueError):
    """Raised when a requested problem source cannot be honestly resolved."""


@dataclass(frozen=True)
class ProblemInput:
    """A frozen, run-ready description of one real problem to research."""

    problem_id: str
    source_bytes: bytes
    source_id: str
    display_statement: str
    status_claims: tuple[StatusClaim, ...] = ()
    novelty_verdict: str = "N1"
    metadata: dict[str, Any] = field(default_factory=dict)


def _repo_root() -> Path:
    """Directory that holds the bundled corpus snapshot in a source checkout."""
    return Path(egmra.__file__).resolve().parent.parent


def _packaged_data_dir() -> Path:
    """Package-internal data directory shipped inside the wheel."""
    return Path(egmra.__file__).resolve().parent / "data"


def default_corpus_tex_path() -> Path:
    """Prefer the packaged corpus (works from an installed wheel), else the checkout."""
    packaged = _packaged_data_dir() / "all_open_problems.tex"
    return packaged if packaged.is_file() else _repo_root() / "all_open_problems.tex"


def default_catalog_path() -> Path:
    packaged = _packaged_data_dir() / "problem_catalog.json"
    return packaged if packaged.is_file() else _repo_root() / "problem_catalog.json"


def default_supplement_dir() -> Path:
    """Per-problem supplemental TeX statements (problems outside the open-only
    corpus snapshot, e.g. the T2-closable decidable/falsifiable/verifiable lane).

    Populate with ``fetch_corpus_supplement.py`` — files are fetched verbatim
    from erdosproblems.com/latex/N with a provenance header, never fabricated.
    """
    packaged = _packaged_data_dir() / "corpus_supplement"
    return packaged if packaged.is_dir() else _repo_root() / "corpus_supplement"


def _read_text_file(path: Path, *, max_bytes: int, label: str) -> str:
    if path.is_symlink() or not path.is_file():
        raise SourceResolutionError(f"{label} path must be a regular non-symlink file: {path}")
    size = path.stat().st_size
    if size > max_bytes:
        raise SourceResolutionError(f"{label} file is too large ({size} bytes): {path}")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SourceResolutionError(f"cannot read {label} file {path}: {exc}") from exc


def _normalize_statement(text: str) -> str:
    statement = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not statement:
        raise SourceResolutionError("problem statement is empty")
    return statement


def from_statement(
    text: str, *, problem_id: str | None = None, source_id: str = ""
) -> ProblemInput:
    """Build a run-ready input from a verbatim statement string."""
    statement = _normalize_statement(text)
    statement_hash = sha256_hex(statement)
    problem_id = problem_id or f"adhoc-{statement_hash[:16]}"
    return ProblemInput(
        problem_id=problem_id,
        source_bytes=statement.encode("utf-8"),
        source_id=source_id or f"inline://{problem_id}",
        display_statement=statement,
        status_claims=(),
        novelty_verdict="N1",
        metadata={"input_kind": "statement"},
    )


def from_statement_file(path: str | Path, *, problem_id: str | None = None) -> ProblemInput:
    """Build a run-ready input from a statement file on disk."""
    source_path = Path(path)
    text = _read_text_file(source_path, max_bytes=_MAX_STATEMENT_BYTES, label="statement")
    statement = _normalize_statement(text)
    pid = problem_id or f"file-{source_path.stem}-{sha256_hex(statement)[:16]}"
    return ProblemInput(
        problem_id=pid,
        source_bytes=statement.encode("utf-8"),
        source_id=f"file://{source_path.resolve()}",
        display_statement=statement,
        status_claims=(),
        novelty_verdict="N1",
        metadata={"input_kind": "statement_file", "path": str(source_path)},
    )


def _slice_problem_section(corpus_tex: str, number: int) -> str:
    start = re.search(_SECTION_RE % number, corpus_tex)
    if not start:
        raise SourceResolutionError(
            f"Erdős problem #{number} has no section in the local corpus snapshot"
        )
    rest = corpus_tex[start.end():]
    nxt = _NEXT_SECTION_RE.search(rest)
    return rest[: nxt.start()] if nxt else rest


def _catalog_entry(catalog_path: Path, number: int) -> dict[str, Any]:
    import json

    text = _read_text_file(catalog_path, max_bytes=_MAX_CATALOG_BYTES, label="catalog")
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SourceResolutionError(f"catalog {catalog_path} is not valid JSON: {exc}") from exc
    problems = document.get("problems") if isinstance(document, dict) else None
    if not isinstance(problems, dict):
        raise SourceResolutionError(f"catalog {catalog_path} has no 'problems' object")
    entry = problems.get(str(number))
    return entry if isinstance(entry, dict) else {}


def _status_claim_from_entry(number: int, entry: dict[str, Any]) -> tuple[StatusClaim, ...]:
    raw_state = str(entry.get("source_state", "")).strip().lower()
    if not raw_state:
        return ()
    status = _STATUS_MAP.get(raw_state, "status_uncertain")
    if status not in STATUS_VALUES:
        status = "status_uncertain"
    source = str(entry.get("source_problem_url") or f"erdosproblems://{number}")
    review_date = str(entry.get("source_last_update", "")) or "unknown"
    return (
        StatusClaim(
            problem_id=f"erdos-{number}",
            status=status,
            source=source,
            review_date=review_date,
            source_independence="erdosproblems.com upstream snapshot",
        ),
    )


def from_erdos_number(
    number: int,
    *,
    corpus_tex_path: str | Path | None = None,
    catalog_path: str | Path | None = None,
    supplement_dir: str | Path | None = None,
) -> ProblemInput:
    """Resolve an Erdős problem number to a run-ready input from local corpus data.

    The exact theorem statement is extracted from the corpus TeX; the dated
    status claim (open/known/…) comes from the problem catalog. Neither is
    fabricated — a missing number or an unparseable section raises. Problems
    outside the open-only snapshot (e.g. the T2-closable machine-status lane)
    resolve from a per-problem supplemental TeX file fetched verbatim from the
    upstream site (see :func:`default_supplement_dir`).
    """
    if isinstance(number, bool) or not isinstance(number, int) or number <= 0:
        raise SourceResolutionError("Erdős problem number must be a positive integer")

    from egmra.corpus.tex_extract import SourceExtractionError, extract_tex_statement

    tex_path = Path(corpus_tex_path) if corpus_tex_path else default_corpus_tex_path()
    corpus_tex = _read_text_file(tex_path, max_bytes=_MAX_CORPUS_BYTES, label="corpus TeX")
    statement_source = "corpus_snapshot"
    try:
        section = _slice_problem_section(corpus_tex, number)
    except SourceResolutionError:
        section = _read_supplement_section(number, supplement_dir=supplement_dir)
        statement_source = "corpus_supplement"
    try:
        statement = _normalize_statement(extract_tex_statement(section))
    except SourceExtractionError as exc:
        raise SourceResolutionError(
            f"Erdős problem #{number} has no extractable statement: {exc}"
        ) from exc

    cat_path = Path(catalog_path) if catalog_path else default_catalog_path()
    entry: dict[str, Any] = {}
    if cat_path.exists():
        entry = _catalog_entry(cat_path, number)
    status_claims = _status_claim_from_entry(number, entry)

    metadata: dict[str, Any] = {
        "input_kind": "erdos",
        "erdos_number": number,
        "source_url": entry.get("source_problem_url", f"https://www.erdosproblems.com/{number}"),
        "tags": list(entry.get("tags", [])),
        "source_state": entry.get("source_state", ""),
        "source_last_update": entry.get("source_last_update", ""),
        "formalized": entry.get("formalized", {}),
        "statement_source": statement_source,
    }
    return ProblemInput(
        problem_id=f"erdos-{number}",
        source_bytes=statement.encode("utf-8"),
        source_id=str(metadata["source_url"]),
        display_statement=statement,
        status_claims=status_claims,
        novelty_verdict="N1",
        metadata=metadata,
    )


def _read_supplement_section(
    number: int, *, supplement_dir: str | Path | None = None,
) -> str:
    directory = Path(supplement_dir) if supplement_dir else default_supplement_dir()
    path = directory / f"problem_{number}.tex"
    if not path.is_file() or path.is_symlink():
        raise SourceResolutionError(
            f"Erdős problem #{number} has no section in the local corpus snapshot "
            f"and no supplemental statement at {path} "
            "(fetch one with fetch_corpus_supplement.py)"
        )
    return _read_text_file(path, max_bytes=_MAX_STATEMENT_BYTES, label="supplement TeX")
