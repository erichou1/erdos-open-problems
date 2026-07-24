"""Claim-specific source-priority matrix (spec §8.6).

There is no sound *total* ordering of "paper vs formal declaration vs database."
Priority is claim-specific: what counts as primary evidence depends on what is
being assessed. Search snippets and model summaries are query leads only.
"""

from __future__ import annotations

from dataclasses import dataclass

CLAIM_KINDS = (
    "historical_provenance",
    "current_mathematical_truth",
    "encoded_formal_truth",
    "intended_interpretation",
    "current_status",
    "novelty",
)


@dataclass(frozen=True)
class SourcePriority:
    claim_kind: str
    primary_evidence: str
    corroboration: str
    critical_caveat: str


_MATRIX = {
    "historical_provenance": SourcePriority(
        "historical_provenance",
        "exact original source bytes and version history",
        "later scholarly transcription",
        "the original may contain an error later corrected",
    ),
    "current_mathematical_truth": SourcePriority(
        "current_mathematical_truth",
        "latest corrected author/publisher version and explicit errata",
        "independent later proof/counterexample",
        "an erratum supersedes the original for truth",
    ),
    "encoded_formal_truth": SourcePriority(
        "encoded_formal_truth",
        "pinned formal declaration, proof artifact, axiom/trust report",
        "independent checker/formalization",
        "proves only the exact encoding",
    ),
    "intended_interpretation": SourcePriority(
        "intended_interpretation",
        "original context, definitions, revisions, expert intent review",
        "examples and equivalent formulations",
        "formal compilation cannot decide intent",
    ),
    "current_status": SourcePriority(
        "current_status",
        "fresh multi-database literature search plus dated curated records",
        "author/expert confirmation",
        "databases and websites lag",
    ),
    "novelty": SourcePriority(
        "novelty",
        "original and later literature, backward/forward citations, synonyms/equivalents",
        "domain-expert review",
        "absence after search means 'not found', never proof of novelty",
    ),
}


def source_priority(claim_kind: str) -> SourcePriority:
    if claim_kind not in _MATRIX:
        raise KeyError(f"unknown claim kind {claim_kind!r}; expected one of {CLAIM_KINDS}")
    return _MATRIX[claim_kind]
