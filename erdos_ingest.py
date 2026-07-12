#!/usr/bin/env python3
"""Versioned, provenance-preserving ingestion for the first-party Erdős corpus."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import stat
import tempfile
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Iterable

import yaml


CATALOG_URL = "https://raw.githubusercontent.com/teorth/erdosproblems/main/data/problems.yaml"
UPSTREAM_REPOSITORY_URL = "https://github.com/teorth/erdosproblems"
UPSTREAM_COMMIT_API = "https://api.github.com/repos/teorth/erdosproblems/commits/main"
COMMIT_CATALOG_URL = (
    "https://raw.githubusercontent.com/teorth/erdosproblems/{commit}/data/problems.yaml"
)
PROBLEM_URL = "https://www.erdosproblems.com/latex/{number}"
USER_AGENT = "erdos-research-ingester/1.0 (+https://www.erdosproblems.com/)"
EXTRACTOR_VERSION = "canonical-sections-v2"


class SourceExtractionError(ValueError):
    """Raised when an exact source section cannot be bounded safely."""


class ProvenanceError(RuntimeError):
    """Raised when canonical source evidence is absent or fails validation."""


class UnsafeDestinationError(RuntimeError):
    """Raised before apply when either mirrored destination is unsafe."""


class ApplyTransactionError(RuntimeError):
    """Raised when an atomic mirrored apply fails (after rollback is attempted)."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_url(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def resolve_upstream_commit(
    fetch_bytes: Callable[[str], bytes] = fetch_url,
) -> str:
    """Resolve the mutable upstream branch to one exact Git commit."""
    try:
        response = json.loads(fetch_bytes(UPSTREAM_COMMIT_API).decode("utf-8"))
        commit = str(response["sha"])
    except (KeyError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        raise ProvenanceError("upstream commit identity is unavailable") from error
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ProvenanceError("upstream commit identity is not a 40-hex Git SHA")
    return commit


_TEX_STATEMENT_LABEL = re.compile(
    r"\\noindent\s*\\textbf\{(?:Problem Statement|Statement):\}"
    r"[ \t]*(?:\r?\n[ \t]*){1,2}",
    re.IGNORECASE,
)
_TEX_STATEMENT_BOUNDARY = re.compile(
    r"\n(?:[ \t]*\n){3,}"
    r"|\n[ \t]*\\bigskip\b"
    r"|\n[ \t]*\\noindent\s*\\textbf\{"
    r"(?:Remarks|References|Related OEIS sequences):\}"
    r"|\n[ \t]*References[ \t]*(?=\n|$)"
    r"|\n[ \t]*\\noindent\s*\\small\{Source:"
    r"|\n[ \t]*\\end\{document\}",
    re.IGNORECASE,
)
_TEX_REFERENCE_MARKER = re.compile(
    r"(?:^|\n)[ \t]*(?:\\bigskip[ \t]*(?:\n[ \t]*)?)?"
    r"(?:\\noindent\s*)?\\textbf\{References:\}[ \t]*"
    r"(?:\n[ \t]*)*"
    r"|(?:^|\n)[ \t]*References[ \t]*(?:\n[ \t]*)+",
    re.IGNORECASE,
)
_TEX_SOURCE_FOOTER = re.compile(
    r"(?:^|\n)[ \t]*\\bigskip[ \t]*\n[ \t]*"
    r"\\noindent\s*\\small\{Source:"
    r"|(?:^|\n)[ \t]*\\noindent\s*\\small\{Source:"
    r"|(?:^|\n)[ \t]*\\end\{document\}",
    re.IGNORECASE,
)


def _decode_source_text(value: str) -> str:
    return html.unescape(value.replace("\r\n", "\n").replace("\r", "\n")).strip()


def _strip_leading_tex_section_marker(value: str, name: str) -> str:
    value = value.strip()
    value = re.sub(r"^\\bigskip\s*", "", value, flags=re.IGNORECASE)
    value = re.sub(
        rf"^(?:\\noindent\s*)?\\textbf\{{{re.escape(name)}:\}}\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )
    return value.strip()


def extract_tex_sections(tex: str) -> dict[str, str]:
    """Extract the theorem and non-theorem sections from a corpus TeX file.

    Legacy corpus files have no ``Remarks:`` heading.  Their scraper emits a
    run of at least four newlines between the exact theorem and commentary.
    Modern ingested files have explicit section headings.  A file matching
    neither contract is rejected rather than falling back to the whole body.
    """
    normalized = tex.replace("\r\n", "\n").replace("\r", "\n")
    label = _TEX_STATEMENT_LABEL.search(normalized)
    if not label:
        raise SourceExtractionError("TeX source has no Problem Statement label")
    tail = normalized[label.end():]
    boundary = _TEX_STATEMENT_BOUNDARY.search(tail)
    if not boundary:
        raise SourceExtractionError("TeX problem statement has no auditable boundary")
    statement = _decode_source_text(tail[:boundary.start()])
    if not statement:
        raise SourceExtractionError("TeX problem statement is empty")

    non_statement = tail[boundary.start():]
    footer = _TEX_SOURCE_FOOTER.search(non_statement)
    content = non_statement[:footer.start()] if footer else non_statement
    reference_marker = _TEX_REFERENCE_MARKER.search(content)
    if reference_marker:
        remarks_raw = content[:reference_marker.start()]
        references_raw = content[reference_marker.end():]
    else:
        remarks_raw = content
        references_raw = ""
    remarks = _decode_source_text(
        _strip_leading_tex_section_marker(remarks_raw, "Remarks")
    )
    references = _decode_source_text(
        _strip_leading_tex_section_marker(references_raw, "References")
    )
    return {
        "statement": statement,
        "remarks": remarks,
        "references": references,
    }


def extract_tex_statement(tex: str) -> str:
    """Return only the exact theorem statement, never remarks or references."""
    return extract_tex_sections(tex)["statement"]


def _plain_fragment(fragment: str) -> str:
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.IGNORECASE)
    fragment = re.sub(r"</?(?:p|li|ul|ol|h[1-6])[^>]*>", "\n", fragment,
                      flags=re.IGNORECASE)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    value = html.unescape(fragment).replace("\r\n", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n\s*\n\s*\n+", "\n\n", value)
    return value.strip()


@dataclass
class _HTMLRegion:
    kind: str
    container_depth: int
    parts: list[str]
    reference_heading: bool = False
    heading_depth: int | None = None
    heading_tag: str | None = None
    heading_parts: list[str] | None = None


class _CanonicalPageParser(HTMLParser):
    _BLOCK_TAGS = {"br", "div", "p", "li", "ul", "ol", *(f"h{i}" for i in range(1, 7))}
    _VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.active: list[_HTMLRegion] = []
        self.statements: list[_HTMLRegion] = []
        self.additional: list[_HTMLRegion] = []
        self.errors: list[str] = []

    @staticmethod
    def _attributes(attributes: list[tuple[str, str | None]]) -> dict[str, str]:
        return {str(key).lower(): str(value or "") for key, value in attributes}

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        existing = list(self.active)
        if tag in self._BLOCK_TAGS:
            for region in existing:
                region.parts.append("\n")
        if tag not in self._VOID_TAGS:
            self.stack.append(tag)
            if tag in {f"h{i}" for i in range(1, 7)}:
                for region in existing:
                    if region.heading_depth is None:
                        region.heading_depth = len(self.stack)
                        region.heading_tag = tag
                        region.heading_parts = []

        attrs = self._attributes(attributes)
        classes = set(attrs.get("class", "").split())
        kind = (
            "statement"
            if tag == "div" and attrs.get("id") == "content"
            else "additional"
            if tag == "div" and "problem-additional-text" in classes
            else None
        )
        if kind is not None:
            if tag in self._VOID_TAGS or existing:
                self.errors.append("canonical source regions overlap or are self-closing")
                return
            region = _HTMLRegion(kind=kind, container_depth=len(self.stack), parts=[])
            self.active.append(region)

    def handle_startendtag(
        self, tag: str, attributes: list[tuple[str, str | None]]
    ) -> None:
        attrs = self._attributes(attributes)
        classes = set(attrs.get("class", "").split())
        if (
            (tag.lower() == "div" and attrs.get("id") == "content")
            or (tag.lower() == "div" and "problem-additional-text" in classes)
        ):
            self.errors.append("canonical source region is self-closing")
        if tag.lower() in self._BLOCK_TAGS:
            for region in self.active:
                region.parts.append("\n")

    def handle_data(self, data: str) -> None:
        for region in self.active:
            region.parts.append(data)
            if region.heading_depth is not None and region.heading_parts is not None:
                region.heading_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if not self.stack or self.stack[-1] != tag:
            if self.active:
                self.errors.append(f"unbalanced HTML close tag inside source region: {tag}")
                return
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.stack.pop()
                if self.stack:
                    self.stack.pop()
            return
        depth = len(self.stack)
        closing_regions = [
            region for region in self.active
            if region.container_depth == depth and tag == "div"
        ]
        for region in self.active:
            if (
                region.heading_depth == depth
                and region.heading_tag == tag
                and region.heading_parts is not None
            ):
                if "".join(region.heading_parts).strip().lower() == "references":
                    region.reference_heading = True
                region.heading_depth = None
                region.heading_tag = None
                region.heading_parts = None
            if region not in closing_regions and tag in self._BLOCK_TAGS:
                region.parts.append("\n")
        for region in closing_regions:
            self.active.remove(region)
            if region.kind == "statement":
                self.statements.append(region)
            else:
                self.additional.append(region)
        self.stack.pop()

    def close(self) -> None:
        super().close()
        if self.active:
            self.errors.append("canonical source region is unclosed")


def _plain_region(parts: list[str]) -> str:
    value = "".join(parts).replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n\s*\n\s*\n+", "\n\n", value)
    return value.strip()


def extract_source_page(page: bytes) -> tuple[str, str, str]:
    text = page.decode("utf-8", errors="strict")
    parser = _CanonicalPageParser()
    parser.feed(text)
    parser.close()
    if parser.errors:
        raise SourceExtractionError("; ".join(parser.errors))
    if len(parser.statements) != 1:
        raise SourceExtractionError(
            f"first-party page has {len(parser.statements)} #content statement blocks"
        )
    statement = _plain_region(parser.statements[0].parts)
    if not statement:
        raise SourceExtractionError("first-party statement block is empty")

    remarks: list[str] = []
    references: list[str] = []
    for region in parser.additional:
        value = _plain_region(region.parts)
        if not value or "Back to the problem" in value:
            continue
        if region.reference_heading:
            value = re.sub(r"^\s*References\s*", "", value, flags=re.IGNORECASE)
            if value:
                references.append(value)
        else:
            remarks.append(value)
    return statement, "\n\n".join(remarks), "\n\n".join(references)


def _prize_text(raw: object) -> str:
    prize = str(raw or "no")
    if prize.startswith("$"):
        return f"Prize: \\${prize[1:]}"
    return "No prize" if prize.lower() == "no" else f"Prize: {prize}"


def render_tex(entry: dict, statement: str, remarks: str, references: str) -> str:
    number = int(entry["number"])
    status = entry.get("status") or {}
    tags = ", ".join(str(tag) for tag in entry.get("tags") or [])
    last_update = str(status.get("last_update", "unknown"))
    chunks = [rf"""\documentclass{{article}}
\usepackage{{amsmath, amssymb, amsthm}}
\usepackage{{hyperref}}
\usepackage{{geometry}}
\geometry{{margin=1in}}

\title{{Erd\H{{o}}s Problem \#{number}}}
\date{{Last updated: {last_update}}}
\author{{Source: erdosproblems.com}}

\begin{{document}}
\maketitle

\noindent\textbf{{Status:}} OPEN \quad \textbf{{{_prize_text(entry.get('prize'))}}}

\noindent\textbf{{Tags:}} {tags}

\medskip
\noindent\textbf{{Problem Statement:}}

{statement}
"""]
    if remarks:
        chunks.append(f"\n\\bigskip\n\\noindent\\textbf{{Remarks:}}\n\n{remarks}\n")
    if references:
        chunks.append(
            f"\n\\bigskip\n\\noindent\\textbf{{References:}}\n\n{references}\n"
        )
    chunks.append(
        f"\n\\bigskip\n\\noindent\\small{{Source: "
        f"\\url{{https://www.erdosproblems.com/{number}}}}}\n\\end{{document}}\n"
    )
    return "".join(chunks)


@dataclass
class _DestinationState:
    item_key: int
    relative_path: str
    path: Path
    before: bytes | None
    before_mode: int | None
    after: bytes
    after_mode: int
    staged_path: Path | None = None


def _ensure_real_directory_tree(root: Path, relative: Path) -> Path:
    root = Path(root)
    if not root.exists():
        root.mkdir(parents=True)
    root_stat = os.lstat(root)
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        raise UnsafeDestinationError(f"apply root is not a real directory: {root}")
    current = root
    for part in relative.parts:
        current = current / part
        try:
            current_stat = os.lstat(current)
        except FileNotFoundError:
            current.mkdir()
            current_stat = os.lstat(current)
        if stat.S_ISLNK(current_stat.st_mode) or not stat.S_ISDIR(current_stat.st_mode):
            raise UnsafeDestinationError(
                f"destination parent is not a real directory: {current}"
            )
    return current


def _destination_bytes(path: Path) -> bytes | None:
    try:
        destination_stat = os.lstat(path)
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(destination_stat.st_mode) or not stat.S_ISREG(destination_stat.st_mode):
        raise UnsafeDestinationError(
            f"destination is a symlink or non-regular file: {path}"
        )
    value = path.read_bytes()
    after_read_stat = os.lstat(path)
    if (
        after_read_stat.st_dev != destination_stat.st_dev
        or after_read_stat.st_ino != destination_stat.st_ino
    ):
        raise UnsafeDestinationError(f"destination changed during preflight: {path}")
    return value


def _stage_bytes(destination: Path, value: bytes, label: str, mode: int) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.{label}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _restore_destination(state: _DestinationState) -> None:
    current = _destination_bytes(state.path)
    current_mode = (
        stat.S_IMODE(os.lstat(state.path).st_mode)
        if current is not None else None
    )
    if current == state.before and current_mode == state.before_mode:
        return
    if state.before is None:
        if current is not None:
            state.path.unlink()
            _fsync_directory(state.path.parent)
        return
    rollback_stage = _stage_bytes(
        state.path,
        state.before,
        "rollback",
        state.before_mode if state.before_mode is not None else 0o644,
    )
    try:
        os.replace(rollback_stage, state.path)
        _fsync_directory(state.path.parent)
    finally:
        rollback_stage.unlink(missing_ok=True)


def safe_apply_tex_batch(
    root: Path,
    items: Iterable[tuple[int, str, bytes]],
    *,
    replace_file: Callable[[object, object], object] | None = None,
) -> dict[int, list[dict]]:
    """Transactionally apply generated TeX to both mirrored corpus paths.

    All destinations are checked with ``lstat`` before any file is staged.
    Existing mirrored copies must agree.  Every changed destination is staged
    on its own filesystem, then replaced atomically.  Any replacement or
    post-write verification failure triggers a best-effort full rollback.
    """
    root = Path(root)
    replace_file = replace_file or os.replace
    material = list(items)
    filenames = [filename for _, filename, _ in material]
    if len(filenames) != len(set(filenames)):
        raise UnsafeDestinationError("duplicate destination filename in apply batch")

    states: list[_DestinationState] = []
    for item_key, filename, payload in material:
        if Path(filename).name != filename:
            raise UnsafeDestinationError(f"unsafe destination filename: {filename}")
        if not isinstance(payload, bytes):
            raise TypeError("generated TeX payload must be bytes")
        pair: list[_DestinationState] = []
        for relative_parent in (Path("open") / "individual", Path("individual")):
            parent = _ensure_real_directory_tree(root, relative_parent)
            destination = parent / filename
            before = _destination_bytes(destination)
            before_mode = (
                stat.S_IMODE(os.lstat(destination).st_mode)
                if before is not None else None
            )
            pair.append(_DestinationState(
                item_key=item_key,
                relative_path=destination.relative_to(root).as_posix(),
                path=destination,
                before=before,
                before_mode=before_mode,
                after=payload,
                after_mode=before_mode if before_mode is not None else 0o644,
            ))
        present = [state.before for state in pair if state.before is not None]
        if len(present) == 2 and present[0] != present[1]:
            raise UnsafeDestinationError(
                f"conflicting existing mirrored contents for {filename}"
            )
        if len(present) == 1 and present[0] != payload:
            raise UnsafeDestinationError(
                f"only one mirrored destination exists with conflicting contents: {filename}"
            )
        states.extend(pair)

    try:
        for state in states:
            if state.before != state.after:
                state.staged_path = _stage_bytes(
                    state.path, state.after, "apply", state.after_mode
                )
    except BaseException as error:
        for state in states:
            if state.staged_path is not None:
                state.staged_path.unlink(missing_ok=True)
        raise ApplyTransactionError(f"failed to stage mirrored apply: {error}") from error

    try:
        for state in states:
            current_bytes = _destination_bytes(state.path)
            current_mode = (
                stat.S_IMODE(os.lstat(state.path).st_mode)
                if current_bytes is not None else None
            )
            if current_bytes != state.before or current_mode != state.before_mode:
                raise UnsafeDestinationError(
                    f"destination changed after preflight: {state.path}"
                )
        for state in states:
            if state.staged_path is None:
                continue
            replace_file(state.staged_path, state.path)
            state.staged_path = None
        for parent in {state.path.parent for state in states}:
            _fsync_directory(parent)
        for state in states:
            if (
                _destination_bytes(state.path) != state.after
                or stat.S_IMODE(os.lstat(state.path).st_mode) != state.after_mode
            ):
                raise OSError(f"post-apply hash verification failed: {state.path}")
    except BaseException as error:
        rollback_errors = []
        for state in reversed(states):
            try:
                _restore_destination(state)
            except BaseException as rollback_error:  # pragma: no cover - catastrophic I/O
                rollback_errors.append(f"{state.relative_path}: {rollback_error}")
        for state in states:
            if state.staged_path is not None:
                state.staged_path.unlink(missing_ok=True)
        detail = (
            f"; rollback errors: {'; '.join(rollback_errors)}"
            if rollback_errors else ""
        )
        raise ApplyTransactionError(f"mirrored apply failed and was rolled back: {error}{detail}") from error

    results: dict[int, list[dict]] = {}
    for state in states:
        results.setdefault(state.item_key, []).append({
            "path": state.relative_path,
            "before_sha256": sha256(state.before) if state.before is not None else None,
            "after_sha256": sha256(state.after),
            "action": "unchanged" if state.before == state.after else "replaced",
        })
    return results


def safe_apply_tex_pair(
    root: Path,
    filename: str,
    payload: bytes,
    *,
    replace_file: Callable[[object, object], object] | None = None,
) -> list[dict]:
    """Apply one generated file to the mirrored corpus paths safely."""
    return safe_apply_tex_batch(
        root,
        [(0, filename, payload)],
        replace_file=replace_file,
    )[0]


def _problem_number(path: Path) -> int:
    match = re.search(r"\d+", path.stem)
    return int(match.group()) if match else -1


def ingest_corpus(
    root: Path,
    output_root: Path,
    *,
    fetch_bytes: Callable[[str], bytes] = fetch_url,
    apply: bool = False,
    missing_only: bool = True,
    numbers: Iterable[int] | None = None,
    canonical: bool = False,
    upstream_commit: str | None = None,
    commit_catalog_bytes: bytes | None = None,
    snapshot_time: str | None = None,
    delay_s: float = 0.25,
) -> dict:
    """Fetch selected source-open records into a new immutable ingestion snapshot."""
    root = Path(root)
    output_root = Path(output_root)
    if canonical:
        if numbers is not None:
            raise ValueError("canonical ingestion cannot select a problem subset")
        missing_only = False
    snapshot_time = snapshot_time or datetime.now(timezone.utc).isoformat()
    catalog_bytes = fetch_bytes(CATALOG_URL)
    commit_pinned_catalog_url = None
    commit_pinned_catalog_sha256 = None
    if canonical:
        upstream_commit = upstream_commit or resolve_upstream_commit(fetch_bytes)
        if not re.fullmatch(r"[0-9a-f]{40}", str(upstream_commit)):
            raise ProvenanceError("canonical ingestion requires a 40-hex upstream commit")
        commit_pinned_catalog_url = COMMIT_CATALOG_URL.format(commit=upstream_commit)
        if commit_catalog_bytes is None:
            commit_catalog_bytes = fetch_bytes(commit_pinned_catalog_url)
        if not isinstance(commit_catalog_bytes, bytes):
            raise ProvenanceError("commit-pinned catalog response is not bytes")
        commit_pinned_catalog_sha256 = sha256(commit_catalog_bytes)
        if commit_catalog_bytes != catalog_bytes:
            raise ProvenanceError(
                "mutable branch catalog differs from the resolved commit-pinned catalog"
            )
    elif upstream_commit is not None or commit_catalog_bytes is not None:
        raise ValueError("upstream commit provenance is only accepted in canonical mode")
    parsed = yaml.safe_load(catalog_bytes.decode("utf-8"))
    if not isinstance(parsed, list):
        raise ValueError("first-party catalog is not a list")
    open_entries = {
        int(entry["number"]): entry
        for entry in parsed
        if isinstance(entry, dict)
        and str((entry.get("status") or {}).get("state", "")).lower() == "open"
    }
    selected = set(open_entries)
    if numbers is not None:
        selected &= {int(number) for number in numbers}
    existing = {
        _problem_number(path)
        for path in (root / "open" / "individual").glob("problem_*.tex")
    }
    if missing_only:
        selected -= existing
    selected_numbers = sorted(selected)

    time_component = re.sub(r"[^0-9A-Za-z]", "", snapshot_time)
    snapshot_id = f"{time_component}-{sha256(catalog_bytes)[:12]}"
    snapshot = output_root / "ingestion" / snapshot_id
    if snapshot.exists():
        raise FileExistsError(f"immutable ingestion snapshot already exists: {snapshot}")
    raw_pages = snapshot / "raw" / "pages"
    generated = snapshot / "generated"
    source_records = snapshot / "source_records"
    raw_pages.mkdir(parents=True)
    generated.mkdir(parents=True)
    source_records.mkdir(parents=True)
    (snapshot / "raw" / "problems.yaml").write_bytes(catalog_bytes)

    records: list[dict] = []
    generated_payloads: dict[int, bytes] = {}
    for index, number in enumerate(selected_numbers):
        entry = open_entries[number]
        url = PROBLEM_URL.format(number=number)
        record = {
            "problem_number": number,
            "source_state": "open",
            "source_url": url,
        }
        try:
            page = fetch_bytes(url)
            raw_path = raw_pages / f"problem_{number}.html"
            raw_path.write_bytes(page)
            statement, remarks, references = extract_source_page(page)
            tex = render_tex(entry, statement, remarks, references)
            tex_bytes = tex.encode("utf-8")
            generated_path = generated / f"problem_{number}.tex"
            generated_path.write_bytes(tex_bytes)
            section_values = {
                "statement": statement,
                "remarks": remarks,
                "references": references,
            }
            section_sha256 = {
                name: sha256(value.encode("utf-8"))
                for name, value in section_values.items()
            }
            source_record_path = source_records / f"problem_{number}.json"
            source_record = {
                "schema_version": 1,
                "problem_number": number,
                "source_url": url,
                "retrieved_at": snapshot_time,
                "raw_page": {
                    "path": raw_path.relative_to(snapshot).as_posix(),
                    "sha256": sha256(page),
                },
                "extraction": {
                    "extractor_version": EXTRACTOR_VERSION,
                    "statement_region": "div#content",
                    "additional_text_region": "div.problem-additional-text",
                    "html_entities_decoded": True,
                },
                "sections": {
                    name: {
                        "text": value,
                        "sha256": section_sha256[name],
                        "source_region": (
                            "div#content"
                            if name == "statement"
                            else "div.problem-additional-text"
                        ),
                    }
                    for name, value in section_values.items()
                },
            }
            source_record_path.write_text(
                json.dumps(source_record, indent=2, ensure_ascii=False, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )
            record.update({
                "raw_html_path": raw_path.relative_to(snapshot).as_posix(),
                "raw_html_sha256": sha256(page),
                "source_record_path": source_record_path.relative_to(snapshot).as_posix(),
                "source_record_sha256": sha256(source_record_path.read_bytes()),
                "section_sha256": section_sha256,
                "statement_sha256": section_sha256["statement"],
                "remarks_sha256": section_sha256["remarks"],
                "references_sha256": section_sha256["references"],
                "generated_tex_path": generated_path.relative_to(snapshot).as_posix(),
                "generated_tex_sha256": sha256(tex_bytes),
                "status": "generated",
            })
            generated_payloads[number] = tex_bytes
        except Exception as error:
            record.update({"status": "error", "error": str(error)})
        records.append(record)
        if delay_s > 0 and index + 1 < len(selected_numbers):
            time.sleep(delay_s)

    source_complete = (
        set(selected_numbers) == set(open_entries)
        and len(records) == len(open_entries)
        and all(record.get("status") == "generated" for record in records)
    )
    application = {
        "requested": apply,
        "status": "not_requested",
        "destination_count": 0,
    }
    if apply:
        if any(record.get("status") == "error" for record in records):
            application["status"] = "skipped_source_errors"
        else:
            try:
                destination_results = safe_apply_tex_batch(
                    root,
                    [
                        (number, f"problem_{number}.tex", generated_payloads[number])
                        for number in selected_numbers
                    ],
                )
            except Exception as error:
                application.update({"status": "error", "error": str(error)})
                for record in records:
                    if record.get("status") == "generated":
                        record.update({"status": "apply_error", "error": str(error)})
            else:
                application.update({
                    "status": "applied",
                    "destination_count": sum(map(len, destination_results.values())),
                })
                for record in records:
                    destinations = destination_results[int(record["problem_number"])]
                    record["applied_destinations"] = destinations
                    record["applied_paths"] = [item["path"] for item in destinations]
                    record["status"] = "applied"

    manifest = {
        "schema_version": 2,
        "snapshot_id": snapshot_id,
        "snapshot_time": snapshot_time,
        "extractor_version": EXTRACTOR_VERSION,
        "upstream_repository_url": UPSTREAM_REPOSITORY_URL,
        "upstream_commit": upstream_commit,
        "catalog_url": CATALOG_URL,
        "catalog_sha256": sha256(catalog_bytes),
        "commit_pinned_catalog_url": commit_pinned_catalog_url,
        "commit_pinned_catalog_sha256": commit_pinned_catalog_sha256,
        "catalog_records": len(parsed),
        "catalog_open_records": len(open_entries),
        "selected_open_problems": selected_numbers,
        "missing_only": missing_only,
        "canonical": canonical,
        "corpus_complete": source_complete,
        "apply": apply,
        "application": application,
        "records": records,
    }
    (snapshot / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def seal_canonical_snapshot_upstream_provenance(
    snapshot: Path,
    *,
    upstream_commit: str,
    commit_catalog_bytes: bytes,
) -> dict:
    """Pre-release seal for a legacy unpinned canonical snapshot.

    This is intentionally one-way: an already sealed snapshot must carry the
    identical commit.  The stored catalog, mutable-branch retrieval, and
    commit-pinned catalog must be byte-identical before the manifest is
    atomically amended and fully revalidated.
    """
    snapshot = Path(snapshot)
    if not re.fullmatch(r"[0-9a-f]{40}", str(upstream_commit)):
        raise ProvenanceError("snapshot seal requires a 40-hex upstream commit")
    if not isinstance(commit_catalog_bytes, bytes):
        raise ProvenanceError("snapshot seal commit catalog is not bytes")
    manifest_path = _provenance_regular_file(snapshot, "manifest.json", "manifest")
    catalog_path = _provenance_regular_file(
        snapshot, "raw/problems.yaml", "catalog snapshot"
    )
    original_manifest_bytes = manifest_path.read_bytes()
    manifest = _load_json_provenance(manifest_path, "manifest")
    catalog_bytes = catalog_path.read_bytes()
    if (
        manifest.get("canonical") is not True
        or manifest.get("corpus_complete") is not True
        or manifest.get("catalog_url") != CATALOG_URL
        or sha256(catalog_bytes) != manifest.get("catalog_sha256")
        or commit_catalog_bytes != catalog_bytes
    ):
        raise ProvenanceError(
            "snapshot cannot be sealed: canonical catalog identity/hash mismatch"
        )
    pinned_url = COMMIT_CATALOG_URL.format(commit=upstream_commit)
    provenance = {
        "upstream_repository_url": UPSTREAM_REPOSITORY_URL,
        "upstream_commit": upstream_commit,
        "commit_pinned_catalog_url": pinned_url,
        "commit_pinned_catalog_sha256": sha256(commit_catalog_bytes),
    }
    existing_values = {key: manifest.get(key) for key in provenance}
    if any(value is not None for value in existing_values.values()):
        if existing_values != provenance:
            raise ProvenanceError("snapshot is already sealed to different provenance")
        validated, _ = _load_complete_canonical_snapshot(snapshot)
        return validated
    amended = {**manifest, **provenance}
    amended_bytes = (
        json.dumps(amended, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    def replace_manifest(payload: bytes, label: str) -> None:
        staged = _stage_bytes(manifest_path, payload, label, 0o644)
        try:
            os.replace(staged, manifest_path)
            _fsync_directory(manifest_path.parent)
        finally:
            staged.unlink(missing_ok=True)

    replace_manifest(amended_bytes, "seal")
    try:
        validated, _ = _load_complete_canonical_snapshot(snapshot)
    except BaseException:
        replace_manifest(original_manifest_bytes, "seal-rollback")
        raise
    return validated


def _provenance_regular_file(snapshot: Path, relative_value: object, label: str) -> Path:
    if not isinstance(relative_value, str):
        raise ProvenanceError(f"{label} path is absent")
    relative = Path(relative_value)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ProvenanceError(f"{label} path is unsafe: {relative_value!r}")
    snapshot_stat = os.lstat(snapshot)
    if stat.S_ISLNK(snapshot_stat.st_mode) or not stat.S_ISDIR(snapshot_stat.st_mode):
        raise ProvenanceError(f"canonical snapshot is not a real directory: {snapshot}")
    current = snapshot
    for part in relative.parts[:-1]:
        current = current / part
        try:
            current_stat = os.lstat(current)
        except FileNotFoundError as error:
            raise ProvenanceError(f"{label} parent is absent: {current}") from error
        if stat.S_ISLNK(current_stat.st_mode) or not stat.S_ISDIR(current_stat.st_mode):
            raise ProvenanceError(f"{label} parent is unsafe: {current}")
    path = snapshot / relative
    try:
        path_stat = os.lstat(path)
    except FileNotFoundError as error:
        raise ProvenanceError(f"{label} is absent: {path}") from error
    if stat.S_ISLNK(path_stat.st_mode) or not stat.S_ISREG(path_stat.st_mode):
        raise ProvenanceError(f"{label} is not a regular file: {path}")
    return path


def _load_json_provenance(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ProvenanceError(f"{label} is unreadable: {path}") from error
    if not isinstance(value, dict):
        raise ProvenanceError(f"{label} is not a JSON object: {path}")
    return value


def _declares_complete_canonical_inventory(manifest: dict, snapshot_name: str) -> bool:
    if (
        manifest.get("schema_version") != 2
        or manifest.get("snapshot_id") != snapshot_name
        or manifest.get("canonical") is not True
        or manifest.get("corpus_complete") is not True
        or manifest.get("extractor_version") != EXTRACTOR_VERSION
        or manifest.get("upstream_repository_url") != UPSTREAM_REPOSITORY_URL
        or not re.fullmatch(r"[0-9a-f]{40}", str(manifest.get("upstream_commit", "")))
    ):
        return False
    expected_pinned_url = COMMIT_CATALOG_URL.format(
        commit=manifest["upstream_commit"]
    )
    if (
        manifest.get("commit_pinned_catalog_url") != expected_pinned_url
        or manifest.get("commit_pinned_catalog_sha256")
        != manifest.get("catalog_sha256")
    ):
        return False
    selected = manifest.get("selected_open_problems")
    records = manifest.get("records")
    if not isinstance(selected, list) or not isinstance(records, list):
        return False
    try:
        selected_numbers = [int(value) for value in selected]
        record_numbers = [int(record["problem_number"]) for record in records]
        catalog_open_records = int(manifest["catalog_open_records"])
    except (TypeError, ValueError, KeyError):
        return False
    if (
        len(selected_numbers) != len(set(selected_numbers))
        or len(record_numbers) != len(set(record_numbers))
        or set(record_numbers) != set(selected_numbers)
        or len(selected_numbers) != catalog_open_records
    ):
        return False
    required_record_fields = (
        "source_record_path",
        "source_record_sha256",
        "raw_html_path",
        "raw_html_sha256",
        "section_sha256",
    )
    return all(
        isinstance(record, dict)
        and record.get("status") in {"generated", "applied", "apply_error"}
        and all(record.get(field) is not None for field in required_record_fields)
        for record in records
    )


def _load_complete_canonical_snapshot(snapshot: Path) -> tuple[dict, dict[int, dict]]:
    snapshot = Path(snapshot)
    manifest_path = _provenance_regular_file(snapshot, "manifest.json", "manifest")
    manifest = _load_json_provenance(manifest_path, "manifest")
    if not _declares_complete_canonical_inventory(manifest, snapshot.name):
        raise ProvenanceError("snapshot does not declare a complete canonical inventory")
    if manifest.get("catalog_url") != CATALOG_URL or manifest.get("missing_only") is not False:
        raise ProvenanceError("snapshot catalog identity or canonical selection mode is invalid")

    catalog_path = _provenance_regular_file(
        snapshot, "raw/problems.yaml", "catalog snapshot"
    )
    catalog_bytes = catalog_path.read_bytes()
    if sha256(catalog_bytes) != manifest.get("catalog_sha256"):
        raise ProvenanceError("catalog snapshot hash mismatch")
    try:
        catalog_data = yaml.safe_load(catalog_bytes.decode("utf-8"))
    except (UnicodeError, yaml.YAMLError) as error:
        raise ProvenanceError("catalog snapshot is unreadable") from error
    if not isinstance(catalog_data, list):
        raise ProvenanceError("catalog snapshot is not a record list")
    try:
        open_entries = {
            int(entry["number"]): entry
            for entry in catalog_data
            if isinstance(entry, dict)
            and str((entry.get("status") or {}).get("state", "")).lower() == "open"
        }
        raw_open_count = sum(
            isinstance(entry, dict)
            and str((entry.get("status") or {}).get("state", "")).lower() == "open"
            for entry in catalog_data
        )
    except (TypeError, ValueError, KeyError) as error:
        raise ProvenanceError("catalog open-problem inventory is malformed") from error
    if len(open_entries) != raw_open_count:
        raise ProvenanceError("catalog open-problem inventory contains duplicates")
    if (
        manifest.get("catalog_records") != len(catalog_data)
        or manifest.get("catalog_open_records") != len(open_entries)
    ):
        raise ProvenanceError("catalog counts disagree with the raw catalog snapshot")

    selected_numbers = [int(value) for value in manifest["selected_open_problems"]]
    records = manifest["records"]
    if set(selected_numbers) != set(open_entries):
        raise ProvenanceError("manifest omits or adds source-open catalog problems")

    sources: dict[int, dict] = {}
    for record in records:
        try:
            problem_number = int(record["problem_number"])
        except (TypeError, ValueError, KeyError) as error:
            raise ProvenanceError("manifest problem record identity is malformed") from error
        expected_url = PROBLEM_URL.format(number=problem_number)
        if (
            record.get("problem_number") != problem_number
            or record.get("source_state") != "open"
            or record.get("source_url") != expected_url
            or record.get("status") not in {"generated", "applied", "apply_error"}
        ):
            raise ProvenanceError(f"problem {problem_number} manifest record is invalid")
        expected_source_path = f"source_records/problem_{problem_number}.json"
        expected_raw_path = f"raw/pages/problem_{problem_number}.html"
        expected_generated_path = f"generated/problem_{problem_number}.tex"
        if (
            record.get("source_record_path") != expected_source_path
            or record.get("raw_html_path") != expected_raw_path
            or record.get("generated_tex_path") != expected_generated_path
        ):
            raise ProvenanceError(f"problem {problem_number} evidence path mismatch")

        source_record_path = _provenance_regular_file(
            snapshot, expected_source_path, f"problem {problem_number} source record"
        )
        source_record_bytes = source_record_path.read_bytes()
        if sha256(source_record_bytes) != record.get("source_record_sha256"):
            raise ProvenanceError(f"problem {problem_number} source record hash mismatch")
        source_record = _load_json_provenance(source_record_path, "source record")
        extraction = source_record.get("extraction")
        if (
            source_record.get("schema_version") != 1
            or source_record.get("problem_number") != problem_number
            or source_record.get("source_url") != expected_url
            or source_record.get("retrieved_at") != manifest.get("snapshot_time")
            or not isinstance(extraction, dict)
            or extraction.get("extractor_version") != EXTRACTOR_VERSION
            or extraction.get("html_entities_decoded") is not True
        ):
            raise ProvenanceError(f"problem {problem_number} source record identity mismatch")

        raw_page = source_record.get("raw_page")
        if not isinstance(raw_page, dict) or raw_page.get("path") != expected_raw_path:
            raise ProvenanceError(f"problem {problem_number} raw-page provenance is absent")
        raw_path = _provenance_regular_file(
            snapshot, expected_raw_path, f"problem {problem_number} raw page"
        )
        raw_bytes = raw_path.read_bytes()
        if (
            sha256(raw_bytes) != raw_page.get("sha256")
            or raw_page.get("sha256") != record.get("raw_html_sha256")
        ):
            raise ProvenanceError(f"problem {problem_number} raw-page hash mismatch")

        sections = source_record.get("sections")
        record_section_hashes = record.get("section_sha256")
        if not isinstance(sections, dict) or not isinstance(record_section_hashes, dict):
            raise ProvenanceError(f"problem {problem_number} section provenance is absent")
        values: dict[str, str] = {}
        for name in ("statement", "remarks", "references"):
            section = sections.get(name)
            if not isinstance(section, dict):
                raise ProvenanceError(f"problem {problem_number} {name} provenance is absent")
            section_text = section.get("text")
            expected_hash = section.get("sha256")
            if (
                not isinstance(section_text, str)
                or not isinstance(section.get("source_region"), str)
                or sha256(section_text.encode("utf-8")) != expected_hash
                or expected_hash != record_section_hashes.get(name)
                or record.get(f"{name}_sha256") != expected_hash
            ):
                raise ProvenanceError(f"problem {problem_number} {name} hash mismatch")
            values[name] = section_text
        try:
            extracted = extract_source_page(raw_bytes)
        except (UnicodeError, ValueError) as error:
            raise ProvenanceError(
                f"problem {problem_number} raw page no longer extracts cleanly"
            ) from error
        if tuple(values[name] for name in ("statement", "remarks", "references")) != extracted:
            raise ProvenanceError(f"problem {problem_number} sections disagree with raw page")

        generated_path = _provenance_regular_file(
            snapshot, expected_generated_path, f"problem {problem_number} generated TeX"
        )
        if sha256(generated_path.read_bytes()) != record.get("generated_tex_sha256"):
            raise ProvenanceError(f"problem {problem_number} generated TeX hash mismatch")
        sources[problem_number] = {
            "problem_number": problem_number,
            "source_url": expected_url,
            **values,
            "provenance": {
                "snapshot_id": manifest["snapshot_id"],
                "snapshot_time": manifest["snapshot_time"],
                "upstream_repository_url": manifest["upstream_repository_url"],
                "upstream_commit": manifest["upstream_commit"],
                "commit_pinned_catalog_url": manifest["commit_pinned_catalog_url"],
                "commit_pinned_catalog_sha256": manifest[
                    "commit_pinned_catalog_sha256"
                ],
                "extractor_version": EXTRACTOR_VERSION,
                "source_record_path": expected_source_path,
                "source_record_sha256": record["source_record_sha256"],
                "raw_html_path": expected_raw_path,
                "raw_html_sha256": record["raw_html_sha256"],
                "section_sha256": dict(record_section_hashes),
            },
        }
    if set(sources) != set(open_entries):
        raise ProvenanceError("validated source evidence is not corpus-complete")
    return manifest, sources


def find_latest_canonical_snapshot(output_root: Path) -> Path:
    """Return the newest complete canonical ingestion, or fail closed."""
    ingestion_root = Path(output_root) / "ingestion"
    candidates: list[tuple[datetime, str, Path]] = []
    if not ingestion_root.is_dir():
        raise ProvenanceError(f"canonical ingestion directory is absent: {ingestion_root}")
    for snapshot in ingestion_root.iterdir():
        try:
            snapshot_stat = os.lstat(snapshot)
        except OSError:
            continue
        if stat.S_ISLNK(snapshot_stat.st_mode) or not stat.S_ISDIR(snapshot_stat.st_mode):
            continue
        try:
            manifest, _ = _load_complete_canonical_snapshot(snapshot)
        except ProvenanceError:
            continue
        raw_time = manifest.get("snapshot_time")
        if not isinstance(raw_time, str):
            continue
        try:
            parsed_time = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
        except ValueError:
            continue
        if parsed_time.tzinfo is None:
            continue
        candidates.append((parsed_time, snapshot.name, snapshot))
    if not candidates:
        raise ProvenanceError("no complete canonical ingestion snapshot is available")
    return max(candidates, key=lambda item: (item[0], item[1]))[2]


def load_canonical_corpus(snapshot: Path) -> dict[int, dict]:
    """Validate and load every exact source record in one immutable snapshot."""
    _, sources = _load_complete_canonical_snapshot(snapshot)
    return sources


def load_canonical_problem_source(snapshot: Path, problem_number: int) -> dict:
    """Load one exact canonical statement only after all provenance validates.

    This is the fail-closed integration API for ranking and solving.  It rejects
    partial/non-canonical snapshots, missing provenance, symlinks, hash drift,
    extractor drift, or any disagreement with a fresh extraction of raw HTML.
    """
    sources = load_canonical_corpus(snapshot)
    try:
        return sources[int(problem_number)]
    except (KeyError, TypeError, ValueError) as error:
        raise ProvenanceError(
            f"problem {problem_number} has no validated canonical source record"
        ) from error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path, default=Path("triage"))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--all", action="store_true",
                        help="Fetch every source-open problem, not only missing files")
    parser.add_argument(
        "--canonical",
        action="store_true",
        help="Require a complete all-open-problem snapshot with validated provenance",
    )
    parser.add_argument("--numbers", nargs="*", type=int)
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--upstream-commit",
                        help="Exact 40-hex teorth/erdosproblems commit")
    parser.add_argument(
        "--seal-snapshot", type=Path,
        help="Pre-release seal an existing legacy canonical snapshot, then exit",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    if args.seal_snapshot is not None:
        snapshot = (
            args.seal_snapshot
            if args.seal_snapshot.is_absolute()
            else root / args.seal_snapshot
        )
        commit = args.upstream_commit or resolve_upstream_commit()
        pinned_catalog = fetch_url(COMMIT_CATALOG_URL.format(commit=commit))
        manifest = seal_canonical_snapshot_upstream_provenance(
            snapshot,
            upstream_commit=commit,
            commit_catalog_bytes=pinned_catalog,
        )
        print(
            f"sealed {manifest['snapshot_id']} to upstream commit "
            f"{manifest['upstream_commit']}"
        )
        return
    manifest = ingest_corpus(
        root, output, apply=args.apply,
        missing_only=not (args.all or args.canonical),
        numbers=args.numbers, canonical=args.canonical,
        upstream_commit=args.upstream_commit, delay_s=args.delay,
    )
    errors = sum(
        str(record.get("status", "")).endswith("error")
        for record in manifest["records"]
    )
    print(
        f"ingestion {manifest['snapshot_id']}: "
        f"{len(manifest['records'])} selected, {errors} errors, apply={args.apply}"
    )
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
