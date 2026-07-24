"""Provenance rules (spec §10.5).

Every imported claim, generated artifact, formal artifact, novelty claim, and human
review must carry specific provenance. Model-hidden reasoning is NOT provenance;
only durable artifacts and explicit events are auditable.
"""

from __future__ import annotations

from dataclasses import dataclass

_REQUIRED_FIELDS = {
    "imported_claim": (
        "source_bytes_hash", "verbatim_extract", "source_uri", "source_version",
        "source_span", "publication_status", "extraction_method",
    ),
    "generated_artifact": (
        "content_hash", "producing_code", "prompt_hash", "model", "inputs", "seed",
        "environment_hash",
    ),
    "formal_artifact": (
        "theorem_hash", "source_tree_hash", "imports", "toolchain", "axiom_report",
        "replay_result",
    ),
    "novelty_claim": (
        "query_log", "databases", "date_cutoff", "synonyms_searched", "access_gaps",
    ),
    "human_review": ("scope", "conflicts_of_interest"),
}


class ProvenanceError(ValueError):
    pass


@dataclass(frozen=True)
class ProvenanceCheck:
    kind: str
    complete: bool
    missing: tuple[str, ...]


def required_fields(kind: str) -> tuple[str, ...]:
    if kind not in _REQUIRED_FIELDS:
        raise ProvenanceError(f"unknown provenance kind {kind!r}")
    return _REQUIRED_FIELDS[kind]


def check_provenance(kind: str, record: dict) -> ProvenanceCheck:
    """Validate that a record carries the provenance required for its kind."""
    fields = required_fields(kind)
    missing = tuple(f for f in fields if record.get(f) in (None, "", [], {}))
    return ProvenanceCheck(kind=kind, complete=not missing, missing=missing)


def hidden_reasoning_is_provenance() -> bool:
    """Model-hidden reasoning (chain-of-thought) is never auditable provenance."""
    return False


def is_auditable(record: dict) -> bool:
    """Only durable artifacts + explicit events are auditable provenance."""
    return bool(record.get("content_hash") or record.get("artifact_hash")
                or record.get("event_id"))
