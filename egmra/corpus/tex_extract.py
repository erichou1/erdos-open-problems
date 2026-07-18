"""Exact Erdős corpus TeX statement extraction (vendored from ``erdos_ingest``).

The packaged ``egmra`` library must resolve ``--erdos N`` without depending on
the repository's loose top-level scripts, so the *exact* statement-extraction
regexes and functions are mirrored here verbatim to preserve mathematical
semantics (task decision F). Only the pure extraction logic is vendored — the
network/ingest machinery stays in ``erdos_ingest.py``.
"""

from __future__ import annotations

import html
import re


class SourceExtractionError(ValueError):
    """Raised when a TeX source has no auditable problem-statement boundary."""


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
    # The monolithic corpus generator terminates every problem section with
    # this exact line before the next ``\\section{Problem ...}``.  It is a
    # structural separator, not theorem text; omitting it left sections with
    # no Remarks/References falsely unextractable even though their source
    # statement and boundary were explicit.
    r"|\n[ \t]*\\noindent\s*\\rule\{\\linewidth\}\{0\.4pt\}[ \t]*(?=\n|$)"
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
    """Extract the theorem and non-theorem sections from a corpus TeX file."""
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
