"""Retrieval service: retriever, import auditor, novelty log (spec §6.4, §8.6)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from egmra.provenance.hashing import content_id, is_sha256
from egmra.retrieval.packet import (
    LiteratureQuery,
    LocalTheoremIndex,
    QueryEvent,
    SearchCoverage,
    SourcePacket,
)
from egmra.retrieval.records import TheoremRecord

_TOKEN = re.compile(r"[a-zA-Z0-9]+")


@dataclass(frozen=True)
class ImportAudit:
    """The independent auditor's verdict on using a retrieved theorem."""

    theorem_id: str
    admitted: bool
    reasons: tuple[str, ...]
    hypotheses_compatible: bool
    version_pinned: bool
    consequence_follows: bool

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__) | {"reasons": list(self.reasons)}


class RetrievalService:
    """Recall-maximizing retriever over a local corpus.

    Builds an immutable :class:`SourcePacket`. Retrieval never upgrades truth —
    only the import auditor's admitted imports can become source evidence.
    """

    def __init__(self, corpus: list[TheoremRecord]):
        theorem_ids = [record.theorem_id for record in corpus]
        if len(theorem_ids) != len(set(theorem_ids)):
            raise ValueError("duplicate theorem id in retrieval corpus")
        self.corpus = list(corpus)
        self.index = LocalTheoremIndex(self.corpus)

    def build_packet(
        self, query: LiteratureQuery, *, packet_id: str = "", limit: int = 5,
        snapshot_time: str = "", corpus_versions: dict | None = None,
    ) -> SourcePacket:
        text = query.query_text()
        hits = self.index.search(text, limit=limit)
        records = [r for r, _ in hits]
        event = QueryEvent(
            query_hash=content_id(query.to_dict()),
            query_text=text,
            result_ids=tuple(r.theorem_id for r in records),
            coverage="local_corpus",
        )
        negatives: list[SearchCoverage] = []
        if not records:
            negatives.append(SearchCoverage(query=text, databases=("local_corpus",), found=0,
                                            gaps=("no local match; external search required",)))
        return SourcePacket(
            packet_id=packet_id or ("pkt_" + content_id(query.to_dict())[:16]),
            query_log=(event,),
            theorem_records=tuple(records),
            negative_search_results=tuple(negatives),
            snapshot_time=snapshot_time,
            corpus_versions=dict(corpus_versions or {"local_corpus": "v1"}),
        )


class ImportAuditor:
    """Independent auditor: only audited imports may enter the claim graph."""

    def audit(
        self, record: TheoremRecord, *, target_hypotheses: list[str], desired_consequence: str
    ) -> ImportAudit:
        reasons: list[str] = []
        version_pinned = bool(record.source_version and is_sha256(record.source_content_hash))
        if not record.is_auditable():
            reasons.append("no verbatim extract or unversioned source")
        if not version_pinned:
            reasons.append("source version/content hash not pinned")

        # Hypotheses compatible: the theorem's hypotheses must be a subset (up to
        # token overlap) of what the target can supply — i.e. it did not silently
        # strengthen assumptions.
        supplied = {t for h in target_hypotheses for t in _semantic_tokens(h)}
        needed = {t for h in record.hypotheses for t in _semantic_tokens(h)}
        missing = needed - supplied
        hyp_compatible = not missing
        if not hyp_compatible:
            reasons.append(f"theorem needs unmet hypotheses: {sorted(missing)}")

        # Consequence follows: the desired consequence tokens are covered by the
        # theorem conclusion (a conservative check; a real auditor formalizes it).
        want = _semantic_tokens(desired_consequence)
        have = _semantic_tokens(record.conclusion or record.canonical_statement)
        # A lexical retriever is not a theorem prover.  Without a separately
        # attested applicability checker, the local auditor admits only a
        # normalized exact consequence; token containment erased negation and
        # previously fabricated implications.
        consequence = bool(want) and want == have
        if not consequence:
            reasons.append("desired consequence does not follow from the theorem conclusion")

        admitted = record.is_auditable() and version_pinned and hyp_compatible and consequence
        if admitted:
            reasons.append("audited: exact source, compatible hypotheses, consequence follows")
        return ImportAudit(
            theorem_id=record.theorem_id, admitted=admitted, reasons=tuple(reasons),
            hypotheses_compatible=hyp_compatible, version_pinned=version_pinned,
            consequence_follows=consequence,
        )


@dataclass
class NoveltyQueryLog:
    """A separate query log for novelty with no incentive to support the proof.

    "sequence/theorem not found" is recorded as *coverage*, never as evidence of
    novelty (spec §8.6: absence after search means "not found", never proof).
    """

    queries: list[QueryEvent] = field(default_factory=list)
    databases_searched: set[str] = field(default_factory=set)

    def record(self, query_text: str, result_ids: list[str], databases: list[str]) -> None:
        self.queries.append(QueryEvent(
            query_hash=content_id({"query_text": query_text, "databases": databases}), query_text=query_text,
            result_ids=tuple(result_ids), coverage=",".join(databases),
        ))
        self.databases_searched.update(databases)

    def novelty_verdict(self) -> str:
        """N0 unresolved / N1 logged search found no prior result. Never proves novelty."""
        if not self.queries:
            return "N0"
        found_any = any(q.result_ids for q in self.queries)
        return "known" if found_any else "N1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "queries": [q.__dict__ for q in self.queries],
            "databases_searched": sorted(self.databases_searched),
            "novelty_verdict": self.novelty_verdict(),
        }


_STOPWORDS = {"a", "an", "the", "of"}


def _semantic_tokens(text: str) -> set[str]:
    """Conservative lexical normalization that deliberately preserves negation."""
    return {token for token in _TOKEN.findall(text.lower()) if token not in _STOPWORDS}
