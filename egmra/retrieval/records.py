"""Theorem and premise records (spec §6.4, §8.5).

Retrieved facts become :class:`TheoremRecord` objects with verbatim extracts and
full provenance. Formal-library results become :class:`PremiseCandidate` objects
that may only be used *after elaboration*; the source auditor separately checks
that an informal paper theorem was not silently strengthened during linkage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from types import MappingProxyType
from typing import Any

from egmra.provenance.hashing import content_id, is_sha256


@dataclass(frozen=True)
class TheoremRecord:
    theorem_id: str
    canonical_statement: str
    hypotheses: tuple[str, ...] = ()
    conclusion: str = ""
    notation_map: dict = field(default_factory=dict)
    source_uri: str = ""
    source_version: str = ""
    source_content_hash: str = ""
    source_span: str = ""
    retrieved_at: str = ""
    verbatim_theorem_and_hypothesis_extract: str = ""
    extraction_method: str = "manual"
    parser_or_ocr_version: str = ""
    extraction_confidence: float = 1.0
    authors: tuple[str, ...] = ()
    date: str = ""
    publication_status: str = "unknown"
    proof_status: str = "unknown"
    corrections: tuple[str, ...] = ()
    formal_declarations: tuple[str, ...] = ()
    applicability_conditions: tuple[str, ...] = ()
    applicability_checks: tuple[str, ...] = ()
    citation_edges: tuple[str, ...] = ()
    independent_verification_status: str = "unverified"
    license: str = ""
    access_constraints: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "notation_map", MappingProxyType(dict(self.notation_map)))
        if not math.isfinite(self.extraction_confidence) \
                or not 0 <= self.extraction_confidence <= 1:
            raise ValueError("extraction_confidence must be finite and in [0, 1]")

    def is_auditable(self) -> bool:
        """A record is auditable only with a verbatim extract and a versioned source."""
        return bool(
            self.verbatim_theorem_and_hypothesis_extract
            and self.source_uri
            and self.source_version
            and is_sha256(self.source_content_hash)
        )

    def to_dict(self) -> dict[str, Any]:
        out = dict(self.__dict__)
        out["notation_map"] = dict(self.notation_map)
        for key, value in list(out.items()):
            if isinstance(value, tuple):
                out[key] = list(value)
        return out

    def record_hash(self) -> str:
        return content_id(self.to_dict())


@dataclass(frozen=True)
class PremiseCandidate:
    declaration_name: str
    declaration_type: str
    imports: tuple[str, ...] = ()
    source_file: str = ""
    source_commit: str = ""
    dependencies: tuple[str, ...] = ()
    retrieval_scores: dict = field(default_factory=dict)
    compiled_in_context: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "retrieval_scores", MappingProxyType(dict(self.retrieval_scores))
        )

    def usable_after_elaboration(self) -> bool:
        """A candidate is only *usable* once it has compiled in the current context."""
        return self.compiled_in_context

    def to_dict(self) -> dict[str, Any]:
        out = dict(self.__dict__)
        out["imports"] = list(self.imports)
        out["dependencies"] = list(self.dependencies)
        out["retrieval_scores"] = dict(self.retrieval_scores)
        return out
