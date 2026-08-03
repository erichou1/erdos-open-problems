"""Adversarial provenance and semantic-boundary tests for retrieval."""

from __future__ import annotations

from dataclasses import replace

import pytest

from egmra.provenance.hashing import sha256_hex
from egmra.retrieval import (
    ImportAuditor,
    LiteratureQuery,
    RetrievalService,
    SourcePacket,
    TheoremRecord,
)
from egmra.retrieval.packet import QueryEvent


def _record(theorem_id: str = "t") -> TheoremRecord:
    return TheoremRecord(
        theorem_id=theorem_id,
        canonical_statement="every even integer is composite",
        hypotheses=("integer n is even and n greater than two",),
        conclusion="n is composite",
        source_uri="https://example.invalid/paper",
        source_version="v1",
        source_content_hash=sha256_hex("paper bytes"),
        verbatim_theorem_and_hypothesis_extract="If n is even and n > 2, n is composite.",
    )


def test_packet_hash_commits_every_provenance_and_conflict_field() -> None:
    base = SourcePacket(
        packet_id="p",
        query_log=[QueryEvent("a" * 64, "query", ("t",), "local")],
        theorem_records=[_record()],
        unresolved_conflicts=[{"source": "A", "status": "open"}],
        snapshot_time="2026-07-13T00:00:00Z",
        corpus_versions={"corpus": "v1"},
    )
    changed_conflict = replace(
        base, unresolved_conflicts=({"source": "A", "status": "known"},)
    )
    changed_snapshot = replace(base, snapshot_time="2026-07-14T00:00:00Z")
    changed_results = replace(
        base, query_log=(QueryEvent("a" * 64, "query", ("other",), "local"),)
    )
    assert len({base.packet_hash(), changed_conflict.packet_hash(),
                changed_snapshot.packet_hash(), changed_results.packet_hash()}) == 4


def test_source_packet_collections_are_deeply_immutable() -> None:
    packet = SourcePacket(
        packet_id="p", theorem_records=[_record()], corpus_versions={"c": "v1"},
        unresolved_conflicts=[{"status": "uncertain"}],
    )
    with pytest.raises((AttributeError, TypeError)):
        packet.theorem_records.append(_record("other"))
    with pytest.raises(TypeError):
        packet.corpus_versions["c"] = "attacker-version"
    with pytest.raises(TypeError):
        packet.unresolved_conflicts[0]["status"] = "open"


def test_query_event_hash_binds_full_query_contract_not_only_display_text() -> None:
    service = RetrievalService([_record()])
    first = LiteratureQuery(
        problem_contract_hash="pc", interpretation_id="i",
        exact_statements=("even composite",), date_cutoff="2025-01-01",
    )
    second = replace(first, date_cutoff="2026-01-01")
    first_event = service.build_packet(first).query_log[0]
    second_event = service.build_packet(second).query_log[0]
    assert first_event.query_text == second_event.query_text
    assert first_event.query_hash != second_event.query_hash


def test_retrieval_rejects_invalid_limits_and_conflicting_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="duplicate theorem id"):
        RetrievalService([_record(), replace(_record(), conclusion="different")])
    service = RetrievalService([_record()])
    with pytest.raises(ValueError, match="limit"):
        service.build_packet(
            LiteratureQuery(problem_contract_hash="pc", interpretation_id="i"), limit=-1
        )


def test_import_auditor_does_not_erase_negation_or_accept_non_hash_provenance() -> None:
    auditor = ImportAuditor()
    negated = TheoremRecord(
        theorem_id="neg",
        canonical_statement="not all primes are odd",
        conclusion="not all primes are odd",
        source_uri="u",
        source_version="v1",
        source_content_hash=sha256_hex("negated source"),
        verbatim_theorem_and_hypothesis_extract="Not all primes are odd.",
    )
    audit = auditor.audit(
        negated, target_hypotheses=[], desired_consequence="all primes are odd"
    )
    assert not audit.admitted and not audit.consequence_follows

    malformed_hash = replace(_record(), source_content_hash="looks-versioned")
    malformed = auditor.audit(
        malformed_hash,
        target_hypotheses=["integer n is even and n greater than two"],
        desired_consequence="n is composite",
    )
    assert not malformed.admitted and not malformed.version_pinned

