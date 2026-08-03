"""Frozen literature packet + service (spec §6.4, §8.4).

The solver packet is immutable and content-addressed. Targeted re-entry creates a
*new version* linked to the old packet, stating the exact missing theorem/query —
this preserves provenance while avoiding a rigid "literature once at the
beginning" policy. Retriever and import auditor are two independent functions: the
retriever maximizes recall and may propose uncertain matches; the auditor checks
the exact source, hypotheses, scope, version, and whether the desired consequence
follows.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from egmra.provenance.hashing import content_id
from egmra.retrieval.records import TheoremRecord


@dataclass(frozen=True)
class LiteratureQuery:
    problem_contract_hash: str
    interpretation_id: str
    exact_statements: tuple[str, ...] = ()
    normalized_formulas: tuple[str, ...] = ()
    objects: tuple[str, ...] = ()
    techniques: tuple[str, ...] = ()
    equivalent_formulations: tuple[str, ...] = ()
    authors: tuple[str, ...] = ()
    seed_sources: tuple[str, ...] = ()
    date_cutoff: str = ""
    include_citation_expansion: bool = True
    include_formal_libraries: bool = True

    def query_text(self) -> str:
        return " ".join([*self.exact_statements, *self.objects, *self.techniques,
                         *self.equivalent_formulations])

    def to_dict(self) -> dict[str, Any]:
        out = dict(self.__dict__)
        for k, v in list(out.items()):
            if isinstance(v, tuple):
                out[k] = list(v)
        return out


@dataclass(frozen=True)
class QueryEvent:
    query_hash: str
    query_text: str
    result_ids: tuple[str, ...]
    coverage: str


@dataclass(frozen=True)
class SearchCoverage:
    query: str
    databases: tuple[str, ...]
    found: int
    gaps: tuple[str, ...] = ()


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class SourcePacket:
    """An immutable, versioned literature packet (spec §8.4)."""

    packet_id: str
    query_log: tuple[QueryEvent, ...] = field(default_factory=tuple)
    theorem_records: tuple[TheoremRecord, ...] = field(default_factory=tuple)
    negative_search_results: tuple[SearchCoverage, ...] = field(default_factory=tuple)
    unresolved_conflicts: tuple[dict, ...] = field(default_factory=tuple)
    snapshot_time: str = ""
    corpus_versions: dict = field(default_factory=dict)
    predecessor_packet_id: str | None = None
    reentry_reason: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "query_log", tuple(self.query_log))
        object.__setattr__(self, "theorem_records", tuple(self.theorem_records))
        object.__setattr__(self, "negative_search_results", tuple(self.negative_search_results))
        object.__setattr__(
            self, "unresolved_conflicts", tuple(_freeze(dict(item)) for item in self.unresolved_conflicts)
        )
        object.__setattr__(self, "corpus_versions", _freeze(dict(self.corpus_versions)))
        theorem_ids = [record.theorem_id for record in self.theorem_records]
        if len(theorem_ids) != len(set(theorem_ids)):
            raise ValueError("source packet contains duplicate theorem ids")

    def packet_hash(self) -> str:
        return content_id({
            "theorem_records": [r.record_hash() for r in self.theorem_records],
            "query_log": [{
                "query_hash": q.query_hash,
                "query_text": q.query_text,
                "result_ids": list(q.result_ids),
                "coverage": q.coverage,
            } for q in self.query_log],
            "negative_search_results": [
                {"query": c.query, "databases": list(c.databases), "found": c.found,
                 "gaps": list(c.gaps)} for c in self.negative_search_results
            ],
            "unresolved_conflicts": list(self.unresolved_conflicts),
            "snapshot_time": self.snapshot_time,
            "corpus_versions": dict(self.corpus_versions),
            "predecessor": self.predecessor_packet_id,
            "reentry_reason": self.reentry_reason,
        })

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "packet_hash": self.packet_hash(),
            "theorem_records": [r.to_dict() for r in self.theorem_records],
            "query_log": [{**q.__dict__, "result_ids": list(q.result_ids)} for q in self.query_log],
            "negative_search_results": [
                {**c.__dict__, "databases": list(c.databases), "gaps": list(c.gaps)}
                for c in self.negative_search_results
            ],
            "unresolved_conflicts": [dict(item) for item in self.unresolved_conflicts],
            "snapshot_time": self.snapshot_time,
            "corpus_versions": dict(self.corpus_versions),
            "predecessor_packet_id": self.predecessor_packet_id,
            "reentry_reason": self.reentry_reason,
        }

    def reentry(self, *, new_records: list[TheoremRecord], reason: str,
                new_packet_id: str) -> "SourcePacket":
        """Create a new packet version linked to this one (never mutate in place)."""
        if not reason.strip():
            raise ValueError("targeted re-entry requires an exact missing-theorem reason")
        if not new_packet_id or new_packet_id == self.packet_id:
            raise ValueError("re-entry requires a distinct non-empty packet id")
        return SourcePacket(
            packet_id=new_packet_id,
            query_log=self.query_log,
            theorem_records=(*self.theorem_records, *new_records),
            negative_search_results=self.negative_search_results,
            unresolved_conflicts=self.unresolved_conflicts,
            snapshot_time=self.snapshot_time,
            corpus_versions=dict(self.corpus_versions),
            predecessor_packet_id=self.packet_id,
            reentry_reason=reason,
        )


# ── local retrieval index (TF-IDF cosine, pure python) ────────────────────────

_TOKEN = re.compile(r"[a-zA-Z0-9]+")


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class LocalTheoremIndex:
    """A pure-Python TF-IDF cosine index over a corpus of TheoremRecords.

    This is the recall-maximizing *retriever*. A real deployment adds dense/vector
    and formula/type indexes (see DECISIONS.md D-004); this local index is what the
    tests exercise deterministically.
    """

    def __init__(self, corpus: list[TheoremRecord]):
        self.corpus = list(corpus)
        self._docs = [_tokens(r.canonical_statement + " " + " ".join(r.hypotheses)
                              + " " + r.conclusion) for r in self.corpus]
        self._df: dict[str, int] = {}
        for doc in self._docs:
            for tok in set(doc):
                self._df[tok] = self._df.get(tok, 0) + 1
        self._n = max(1, len(self._docs))

    def _tfidf(self, tokens: list[str]) -> dict[str, float]:
        counts: dict[str, int] = {}
        for tok in tokens:
            counts[tok] = counts.get(tok, 0) + 1
        vec: dict[str, float] = {}
        for tok, count in counts.items():
            idf = math.log((1 + self._n) / (1 + self._df.get(tok, 0))) + 1.0
            vec[tok] = count * idf
        return vec

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        common = set(a) & set(b)
        dot = sum(a[t] * b[t] for t in common)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def search(self, query: str, *, limit: int = 5) -> list[tuple[TheoremRecord, float]]:
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
            raise ValueError("retrieval limit must be a non-negative integer")
        qvec = self._tfidf(_tokens(query))
        scored = [
            (self.corpus[i], round(self._cosine(qvec, self._tfidf(self._docs[i])), 4))
            for i in range(len(self.corpus))
        ]
        scored = [(r, s) for r, s in scored if s > 0.0]
        scored.sort(key=lambda rs: rs[1], reverse=True)
        return scored[:limit]
