"""Truth snapshots bind release gates to replayed authoritative graph state."""

from __future__ import annotations

from dataclasses import replace

import pytest

from egmra.provenance.hashing import sha256_hex
from egmra.truth import (
    Branch,
    EpistemicGraph,
    EventLog,
    FormalVerification,
    IntentCertificate,
    Interpretation,
    Problem,
    TruthSnapshotError,
    TruthStatus,
    Verdict,
)


ACTOR = {"type": "truth-service", "id": "snapshot-test"}


def _graph(tmp_path) -> EpistemicGraph:
    graph = EpistemicGraph(EventLog(tmp_path / "events.jsonl", run_id="snapshot"))
    graph.add_problem(Problem("p", sha256_hex("source")), actor=ACTOR)
    graph.add_interpretation(Interpretation("i", "p", "P"), actor=ACTOR)
    graph.propose_claim(claim_id="c", interpretation_id="i", canonical_formula="P", actor=ACTOR)
    return graph


def test_snapshot_is_issued_from_replay_not_mutable_caller_view(tmp_path) -> None:
    graph = _graph(tmp_path)
    graph.claims["c"].truth_status = TruthStatus.SUPPORTED
    graph.claims["c"].evidence_profile = replace(
        graph.claims["c"].evidence_profile,
        formal_verification=FormalVerification.KERNEL_CHECKED,
    )

    snapshot = graph.snapshot_claim("c")
    assert snapshot.truth_status == "UNKNOWN"
    assert snapshot.evidence_profile["formal_verification"] == "NONE"
    assert snapshot.verify(event_log=graph.log)


def test_snapshot_signature_claim_binding_and_current_head_are_verified(tmp_path) -> None:
    graph = _graph(tmp_path)
    snapshot = graph.snapshot_claim("c")
    assert snapshot.verify(event_log=graph.log, expected_claim_id="c")
    assert not snapshot.verify(event_log=graph.log, expected_claim_id="other")
    assert not replace(snapshot, truth_status="SUPPORTED").verify(event_log=graph.log)

    graph.add_branch(
        Branch(branch_id="b", goal_claim_ids=["c"], interpretation_id="i"), actor=ACTOR
    )
    assert not snapshot.verify(event_log=graph.log), "cached approval must become stale at a new head"


def test_snapshot_requires_a_distinct_strong_key(tmp_path, monkeypatch) -> None:
    graph = _graph(tmp_path)
    monkeypatch.delenv("EGMRA_TRUTH_SNAPSHOT_KEY")
    with pytest.raises(TruthSnapshotError, match="required"):
        graph.snapshot_claim("c")


def test_approved_exact_intent_binding_is_versioned_and_replayed(tmp_path) -> None:
    graph = _graph(tmp_path)
    claim_hash = graph.claims["c"].canonical_hash
    graph.issue_intent_certificate(
        IntentCertificate(
            certificate_id="intent",
            source_bytes_hash=sha256_hex("source"),
            interpretation_hash=sha256_hex("interpretation"),
            informal_claim_hash=claim_hash,
            verdict=Verdict.APPROVED,
        ),
        actor=ACTOR,
    )
    graph.bind_intent_certificate("c", "intent", actor=ACTOR)
    assert graph.claims["c"].evidence_profile.intent_certificate_id == "intent"
    restarted = EpistemicGraph(EventLog(graph.log.path, run_id="snapshot"))
    assert restarted.claims["c"].evidence_profile.intent_certificate_id == "intent"
    assert restarted.snapshot_claim("c").evidence_profile["intent_certificate_id"] == "intent"

    graph.issue_intent_certificate(
        IntentCertificate(
            certificate_id="wrong",
            source_bytes_hash=sha256_hex("source"),
            interpretation_hash=sha256_hex("interpretation"),
            informal_claim_hash=sha256_hex("different claim"),
            verdict=Verdict.APPROVED,
        ),
        actor=ACTOR,
    )
    with pytest.raises(Exception, match="claim hash"):
        graph.bind_intent_certificate("c", "wrong", actor=ACTOR)
