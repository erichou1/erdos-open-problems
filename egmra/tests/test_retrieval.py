"""Tests for corpus status hygiene and retrieval (Module D)."""

import pytest

from egmra.corpus import StatusClaim, reconcile_status
from egmra.retrieval import (
    ImportAuditor,
    LiteratureQuery,
    NoveltyQueryLog,
    PremiseCandidate,
    PremiseLibrary,
    PremiseRetrievalRequest,
    RetrievalService,
    SourcePacket,
    TheoremRecord,
    source_priority,
    usable_premises,
)


# ── corpus status ────────────────────────────────────────────────────────────

def test_status_conflict_becomes_uncertain_and_blocks_campaign():
    claims = [
        StatusClaim("erdos-1", "open", source="website", review_date="2026-07-01"),
        StatusClaim("erdos-1", "known", source="paper", review_date="2026-07-05"),
    ]
    res = reconcile_status("erdos-1", claims)
    assert res.resolved_status == "status_uncertain"
    assert res.conflict and res.blocks_proof_campaign
    assert res.literature_task["action"] == "resolve_status_conflict"


def test_agreeing_status_resolves_cleanly():
    claims = [
        StatusClaim("erdos-1", "open", source="a", review_date="2026-07-01"),
        StatusClaim("erdos-1", "open", source="b", review_date="2026-07-02"),
    ]
    res = reconcile_status("erdos-1", claims)
    assert res.resolved_status == "open" and not res.conflict


def test_no_status_source_is_uncertain():
    res = reconcile_status("erdos-1", [])
    assert res.resolved_status == "status_uncertain"


def test_invalid_status_rejected():
    with pytest.raises(ValueError):
        StatusClaim("erdos-1", "solved-ish", source="x", review_date="2026")


# ── retrieval ─────────────────────────────────────────────────────────────────

def _corpus():
    return [
        TheoremRecord(
            theorem_id="thm-green-tao", canonical_statement="primes contain arbitrarily long arithmetic progressions",
            hypotheses=("set of primes",), conclusion="arbitrarily long arithmetic progressions exist",
            source_uri="arxiv:math/0404188", source_version="v2", source_content_hash="1" * 64,
            verbatim_theorem_and_hypothesis_extract="The primes contain arbitrarily long APs.",
        ),
        TheoremRecord(
            theorem_id="thm-szemeredi", canonical_statement="dense sets contain arithmetic progressions",
            hypotheses=("positive upper density set",), conclusion="contains arithmetic progressions",
            source_uri="acta:1975", source_version="v1", source_content_hash="2" * 64,
            verbatim_theorem_and_hypothesis_extract="Every set of positive density contains APs.",
        ),
        TheoremRecord(
            theorem_id="thm-unrelated", canonical_statement="every planar graph is four colorable",
            hypotheses=("planar graph",), conclusion="four colorable",
            source_uri="ill:1977", source_version="v1", source_content_hash="3" * 64,
            verbatim_theorem_and_hypothesis_extract="Planar graphs are 4-colorable.",
        ),
    ]


def test_retrieval_ranks_relevant_theorem_first():
    svc = RetrievalService(_corpus())
    query = LiteratureQuery(
        problem_contract_hash="c", interpretation_id="int-1",
        exact_statements=("primes contain long arithmetic progressions",),
        objects=("primes", "arithmetic progressions"),
    )
    packet = svc.build_packet(query, limit=2)
    assert packet.theorem_records
    assert packet.theorem_records[0].theorem_id == "thm-green-tao"
    # packet is content-addressed and hash-stable
    assert packet.packet_hash() == SourcePacket(
        packet_id=packet.packet_id, query_log=packet.query_log,
        theorem_records=packet.theorem_records,
        corpus_versions=packet.corpus_versions,
    ).packet_hash()


def test_packet_reentry_links_predecessor():
    svc = RetrievalService(_corpus())
    q = LiteratureQuery(problem_contract_hash="c", interpretation_id="int-1",
                        objects=("primes",))
    packet = svc.build_packet(q, packet_id="pkt-1")
    extra = TheoremRecord(theorem_id="thm-new", canonical_statement="new lemma",
                          source_uri="u", source_version="v1", source_content_hash="4" * 64,
                          verbatim_theorem_and_hypothesis_extract="x")
    packet2 = packet.reentry(new_records=[extra], reason="missing lemma X", new_packet_id="pkt-2")
    assert packet2.predecessor_packet_id == "pkt-1"
    assert packet2.packet_hash() != packet.packet_hash()


def test_import_auditor_admits_only_compatible_versioned_import():
    auditor = ImportAuditor()
    rec = _corpus()[1]  # szemeredi
    ok = auditor.audit(rec, target_hypotheses=["a set of positive upper density"],
                       desired_consequence="contains arithmetic progressions")
    assert ok.admitted
    # unmet hypothesis -> rejected (no silent strengthening)
    bad = auditor.audit(rec, target_hypotheses=["a finite set"],
                        desired_consequence="contains arithmetic progressions")
    assert not bad.admitted and not bad.hypotheses_compatible


def test_import_auditor_rejects_unversioned_source():
    auditor = ImportAuditor()
    rec = TheoremRecord(theorem_id="t", canonical_statement="x", conclusion="y",
                        verbatim_theorem_and_hypothesis_extract="x")  # no version/hash
    audit = auditor.audit(rec, target_hypotheses=[], desired_consequence="y")
    assert not audit.admitted and not audit.version_pinned


def test_novelty_log_never_proves_novelty():
    log = NoveltyQueryLog()
    log.record("exact statement", result_ids=[], databases=["arxiv", "mathscinet"])
    assert log.novelty_verdict() == "N1"  # "not found", not proof of novelty
    log.record("statement", result_ids=["prior-work"], databases=["arxiv"])
    assert log.novelty_verdict() == "known"


def test_premise_only_usable_after_elaboration():
    lib = PremiseLibrary(declarations=[
        PremiseCandidate("Nat.add_comm", "∀ a b : ℕ, a + b = b + a", compiled_in_context=False),
        PremiseCandidate("Nat.add_assoc", "∀ a b c : ℕ, a + b + c = a + (b + c)",
                         compiled_in_context=True),
    ])
    got = lib.retrieve_premises(PremiseRetrievalRequest(natural_claim="add comm nat", max_premises=5))
    assert any(c.declaration_name == "Nat.add_comm" for c in got)
    # only elaborated premises are usable
    usable = usable_premises(got)
    assert usable
    assert {c.declaration_name for c in usable} == {"Nat.add_assoc"}
    assert all(c.declaration_name != "Nat.add_comm" for c in usable)
    assert all(c.compiled_in_context for c in usable)


def test_source_priority_matrix():
    assert "formal compilation cannot decide intent" in source_priority("intended_interpretation").critical_caveat
    assert "never proof of novelty" in source_priority("novelty").critical_caveat
    with pytest.raises(KeyError):
        source_priority("not_a_kind")
