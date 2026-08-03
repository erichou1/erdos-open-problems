"""Tests for the truth plane: events, graph, validators, router, revocation."""

import pytest

from egmra.agents import AuthorityTokenIssuer
from egmra.provenance.hashing import content_id
from egmra.provenance.hashing import sha256_hex
from egmra.truth import (
    Branch,
    Evidence,
    EvidenceKind,
    EpistemicGraph,
    EventLog,
    EventLogError,
    ExactComputation,
    FormalCorrespondenceCertificate,
    FormalVerification,
    InformalReview,
    IntentCertificate,
    Interpretation,
    Lifecycle,
    NumericalEvidence,
    Problem,
    TruthStatus,
    Verdict,
    EvidenceRouter,
    invalidate_evidence,
    refute_claim,
    strongly_connected_components,
)
from egmra.truth.validators import attest_evidence
from egmra.truth.blackboard import Blackboard, BlackboardError
from egmra.truth.views import manifest_projection, materialize_sqlite

ACTOR = {"type": "agent", "id": "tester", "model": "det", "version": "1"}


# ── event log ──────────────────────────────────────────────────────────────────

def test_event_log_appends_chains_and_verifies(tmp_path):
    log = EventLog(tmp_path / "events.jsonl", run_id="r1")
    log.append(action="CLAIM_PROPOSED", actor=ACTOR, object_ids=["clm_1"])
    log.append(action="EVIDENCE_ATTACHED", actor=ACTOR, object_ids=["ev_1"])
    assert len(log) == 2
    assert log.verify_integrity()
    assert log.events[1].prev_event_id == log.events[0].event_id
    assert log.events[0].sequence == 0


def test_event_log_reload_preserves_integrity(tmp_path):
    path = tmp_path / "events.jsonl"
    log = EventLog(path, run_id="r1")
    log.append(action="CLAIM_PROPOSED", actor=ACTOR, object_ids=["clm_1"])
    reopened = EventLog(path, run_id="r1")
    assert len(reopened) == 1
    assert reopened.verify_integrity()


def test_event_log_detects_tampering(tmp_path):
    path = tmp_path / "events.jsonl"
    log = EventLog(path, run_id="r1")
    log.append(action="CLAIM_PROPOSED", actor=ACTOR, object_ids=["clm_1"],
               human_readable_reason="original")
    # Tamper with the persisted reason without recomputing the id/signature.
    lines = path.read_text().splitlines()
    lines[0] = lines[0].replace("original", "tampered")
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(EventLogError):
        EventLog(path, run_id="r1")


def test_unknown_action_is_rejected(tmp_path):
    log = EventLog(tmp_path / "e.jsonl")
    with pytest.raises(Exception):
        log.append(action="NOT_A_REAL_ACTION", actor=ACTOR, object_ids=[])


# ── graph basics ───────────────────────────────────────────────────────────────

def _graph(tmp_path) -> EpistemicGraph:
    log = EventLog(tmp_path / "events.jsonl", run_id="r1")
    graph = EpistemicGraph(log)
    graph.add_problem(Problem(problem_id="erdos-1", original_bytes_hash=sha256_hex("p")), actor=ACTOR)
    graph.add_interpretation(
        Interpretation(interpretation_id="int-1", parent_problem_id="erdos-1",
                       normalized_statement="S"), actor=ACTOR)
    return graph


def test_proposed_claim_enters_unknown_with_empty_profile(tmp_path):
    graph = _graph(tmp_path)
    claim = graph.propose_claim(claim_id="clm_1", interpretation_id="int-1",
                                canonical_formula="P(n)", actor=ACTOR)
    assert claim.truth_status == TruthStatus.UNKNOWN
    assert claim.evidence_profile.is_empty()
    assert claim.status_version == 1


def test_registering_evidence_does_not_change_tier(tmp_path):
    graph = _graph(tmp_path)
    graph.propose_claim(claim_id="clm_1", interpretation_id="int-1",
                        canonical_formula="P", actor=ACTOR)
    ev = Evidence(evidence_id="ev_1", claim_ids=["clm_1"], kind=EvidenceKind.NUMERICAL)
    graph.register_evidence(ev, actor=ACTOR)
    # Raw registration alone must not upgrade the claim (only the router can).
    assert graph.claims["clm_1"].truth_status == TruthStatus.UNKNOWN


# ── validators / router ─────────────────────────────────────────────────────────

def _findings(**kw):
    return {"generator_identity": {"findings": kw}}


def _attest(graph: EpistemicGraph, evidence: Evidence) -> Evidence:
    evidence.claim_bindings = {
        claim_id: graph.claims[claim_id].canonical_hash for claim_id in evidence.claim_ids
    }
    if evidence.kind in {
        EvidenceKind.SOURCE_IMPORT, EvidenceKind.NUMERICAL, EvidenceKind.EXACT_COMPUTATION,
        EvidenceKind.COUNTEREXAMPLE, EvidenceKind.LEAN_PROOF, EvidenceKind.ATP_PROOF,
        EvidenceKind.SAT_CERTIFICATE,
    }:
        artifact_hash = sha256_hex(evidence.evidence_id)
        evidence.assertion_scope = evidence.assertion_scope or "test claim scope"
        evidence.artifact_hashes = evidence.artifact_hashes or [artifact_hash]
        if evidence.kind is EvidenceKind.SOURCE_IMPORT:
            evidence.generator_identity["findings"]["source_content_hash"] = artifact_hash
        else:
            evidence.environment_hash = evidence.environment_hash or sha256_hex("test environment")
            evidence.replay_command = evidence.replay_command or "test-replay --immutable-artifact"
            evidence.verifier_identities = evidence.verifier_identities or [
                {"id": "test-checker", "attested": True}
            ]
    findings = evidence.generator_identity.get("findings", {})
    if findings.get("classification") in {"exhaustive_finite", "finite_reduction"}:
        findings.setdefault("result_verified", True)
    if findings.get("classification") == "finite_reduction":
        findings.setdefault("finite_reduction_checked", True)
    return attest_evidence(evidence)


def _admit(router: EvidenceRouter, evidence: Evidence):
    return router.admit(_attest(router.graph, evidence), actor=ACTOR)


def test_lean_metadata_without_authenticated_envelope_is_rejected(tmp_path):
    graph = _graph(tmp_path)
    router = EvidenceRouter(graph)
    graph.propose_claim(claim_id="clm_1", interpretation_id="int-1",
                        canonical_formula="T", actor=ACTOR)
    # vendor-reported only -> rejected, stays UNKNOWN
    vendor = Evidence(
        evidence_id="ev_vendor", claim_ids=["clm_1"], kind=EvidenceKind.LEAN_PROOF,
        replay_result="pass",
        generator_identity={"findings": {"verification_method": "aristotle_reported",
                                          "kernel_verified": False}},
    )
    _admit(router, vendor)
    assert graph.claims["clm_1"].truth_status == TruthStatus.UNKNOWN

    # Even plausible kernel metadata plus a real correspondence certificate is
    # not proof authority without the authenticated FormalCertificate envelope.
    claim_hash = graph.claims["clm_1"].canonical_hash
    graph.issue_intent_certificate(
        IntentCertificate(
            certificate_id="ic_1",
            source_bytes_hash=sha256_hex("source"),
            interpretation_hash=sha256_hex("interpretation"),
            informal_claim_hash=claim_hash,
            methods=["independent semantic review"],
            reviewer_ids=["semantic-reviewer"],
            reviewer_independence_and_conflicts=[
                {"reviewer_id": "semantic-reviewer", "independent": True, "conflicts": []}
            ],
            verdict=Verdict.APPROVED,
        ),
        actor=ACTOR,
    )
    elaborated_type_hash = sha256_hex("theorem clm_1 : T")
    graph.issue_correspondence_certificate(
        FormalCorrespondenceCertificate(
            certificate_id="fcc_1",
            intent_certificate_id="ic_1",
            informal_claim_hash=claim_hash,
            lean_declaration_name="clm_1",
            elaborated_type_hash=elaborated_type_hash,
            methods=["elaborated type comparison"],
            reviewer_ids=["formal-reviewer"],
            reviewer_independence_and_conflicts=[
                {"reviewer_id": "formal-reviewer", "independent": True, "conflicts": []}
            ],
            verdict=Verdict.APPROVED,
        ),
        actor=ACTOR,
    )
    kernel = Evidence(
        evidence_id="ev_kernel", claim_ids=["clm_1"], kind=EvidenceKind.LEAN_PROOF,
        replay_result="pass", intent_certificate_id="ic_1",
        formal_correspondence_certificate_id="fcc_1",
        generator_identity={"findings": {"verification_method": "local_lean_kernel",
                                          "kernel_verified": True, "has_placeholders": False,
                                          "axiom_whitelist_ok": True,
                                          "target_type_matches": True,
                                          "elaborated_type_hash": elaborated_type_hash}},
    )
    _admit(router, kernel)
    claim = graph.claims["clm_1"]
    assert claim.truth_status == TruthStatus.UNKNOWN
    assert claim.evidence_profile.formal_verification == FormalVerification.NONE


def test_float_computation_never_proves_exact(tmp_path):
    graph = _graph(tmp_path)
    router = EvidenceRouter(graph)
    graph.propose_claim(claim_id="clm_1", interpretation_id="int-1",
                        canonical_formula="P", scope="general", actor=ACTOR)
    ev = Evidence(evidence_id="ev_1", claim_ids=["clm_1"], kind=EvidenceKind.NUMERICAL,
                  replay_result="pass",
                  generator_identity={"findings": {"classification": "heuristic",
                                                    "exact_arithmetic": False}})
    _admit(router, ev)
    claim = graph.claims["clm_1"]
    assert claim.evidence_profile.numerical == NumericalEvidence.REPRODUCIBLE
    assert claim.truth_status == TruthStatus.UNKNOWN  # numerical alone is not support


def test_exact_finite_computation_supports_scoped_claim(tmp_path):
    graph = _graph(tmp_path)
    router = EvidenceRouter(graph)
    graph.propose_claim(claim_id="clm_1", interpretation_id="int-1",
                        canonical_formula="P for n<=10", scope="finite_domain", actor=ACTOR)
    ev = Evidence(evidence_id="ev_1", claim_ids=["clm_1"], kind=EvidenceKind.EXACT_COMPUTATION,
                  replay_result="pass",
                  generator_identity={"findings": {"classification": "exhaustive_finite",
                                                    "exact_arithmetic": True,
                                                    "coverage_statement": True}})
    _admit(router, ev)
    claim = graph.claims["clm_1"]
    assert claim.evidence_profile.exact_computation == ExactComputation.SCOPED_EXACT
    assert claim.truth_status == TruthStatus.SUPPORTED


def test_single_vs_double_independent_review(tmp_path):
    graph = _graph(tmp_path)
    router = EvidenceRouter(graph)
    graph.propose_claim(claim_id="clm_1", interpretation_id="int-1",
                        canonical_formula="P", actor=ACTOR)
    single = Evidence(evidence_id="ev_1", claim_ids=["clm_1"], kind=EvidenceKind.INFORMAL_REVIEW,
                      generator_identity={"findings": {"reviewers": [
                          {"reviewer_id": "a", "lineage": "fam1", "verdict": "pass"}]}})
    _admit(router, single)
    assert graph.claims["clm_1"].evidence_profile.informal_review == InformalReview.SINGLE
    assert graph.claims["clm_1"].truth_status == TruthStatus.UNKNOWN

    dbl = Evidence(evidence_id="ev_2", claim_ids=["clm_1"], kind=EvidenceKind.INFORMAL_REVIEW,
                   generator_identity={"findings": {"reviewers": [
                       {"reviewer_id": "b", "lineage": "fam2", "verdict": "pass"}]}})
    _admit(router, dbl)
    assert graph.claims["clm_1"].evidence_profile.informal_review == InformalReview.DOUBLE_INDEPENDENT
    assert graph.claims["clm_1"].truth_status == TruthStatus.SUPPORTED


# ── revocation ──────────────────────────────────────────────────────────────────

def test_false_central_lemma_refuted_and_dependents_downgraded(tmp_path):
    graph = _graph(tmp_path)
    router = EvidenceRouter(graph)
    # central lemma supported by (mistaken) double review, target depends on it
    graph.propose_claim(claim_id="lemma", interpretation_id="int-1",
                        canonical_formula="L", actor=ACTOR)
    graph.propose_claim(claim_id="target", interpretation_id="int-1",
                        canonical_formula="T", dependencies=["lemma"], actor=ACTOR)
    review = Evidence(evidence_id="ev_r", claim_ids=["lemma"], kind=EvidenceKind.INFORMAL_REVIEW,
                      generator_identity={"findings": {"reviewers": [
                          {"reviewer_id": "a", "lineage": "f1", "verdict": "pass"},
                          {"reviewer_id": "b", "lineage": "f2", "verdict": "pass"}]}})
    _admit(router, review)
    # target supported by its own double review, presuming the lemma
    trev = Evidence(evidence_id="ev_t", claim_ids=["target"], kind=EvidenceKind.INFORMAL_REVIEW,
                    generator_identity={"findings": {"reviewers": [
                        {"reviewer_id": "c", "lineage": "f1", "verdict": "pass"},
                        {"reviewer_id": "d", "lineage": "f2", "verdict": "pass"}]}})
    _admit(router, trev)
    assert graph.claims["target"].truth_status == TruthStatus.SUPPORTED

    # Now a checked counterexample refutes the lemma.
    counter = Evidence(evidence_id="ev_c", claim_ids=["lemma"], kind=EvidenceKind.COUNTEREXAMPLE,
                       replay_result="pass",
                       generator_identity={"findings": {"exact_witness_checked": True,
                                                         "in_stated_domain": True}})
    graph.register_evidence(_attest(graph, counter), actor=ACTOR)
    affected = refute_claim(graph, router, "lemma", counterevidence_id="ev_c", actor=ACTOR)
    assert graph.claims["lemma"].truth_status == TruthStatus.REFUTED
    assert "target" in affected
    # dependent downgraded because its support presumed the refuted lemma
    assert graph.claims["target"].truth_status == TruthStatus.UNKNOWN


def test_invalidate_evidence_downgrades_without_refuting(tmp_path):
    graph = _graph(tmp_path)
    router = EvidenceRouter(graph)
    graph.propose_claim(claim_id="clm_1", interpretation_id="int-1",
                        canonical_formula="P", actor=ACTOR)
    imp = Evidence(evidence_id="ev_i", claim_ids=["clm_1"], kind=EvidenceKind.SOURCE_IMPORT,
                   generator_identity={"findings": {"verbatim_extract": "thm",
                                                     "source_uri": "u", "source_version": "1",
                                                     "applicability_check_passed": True,
                                                     "independently_corroborated": True}})
    _admit(router, imp)
    assert graph.claims["clm_1"].truth_status == TruthStatus.SUPPORTED
    invalidate_evidence(graph, router, "ev_i", reason="source corrected", actor=ACTOR)
    # losing support downgrades but does not mark the claim false
    assert graph.claims["clm_1"].truth_status == TruthStatus.UNKNOWN
    assert graph.claims["clm_1"].lifecycle_status == Lifecycle.ACTIVE


def test_conflicted_when_counterexample_meets_surviving_support(tmp_path):
    graph = _graph(tmp_path)
    router = EvidenceRouter(graph)
    graph.propose_claim(claim_id="clm_1", interpretation_id="int-1",
                        canonical_formula="P for n<=5", scope="finite_domain", actor=ACTOR)
    exact = Evidence(evidence_id="ev_e", claim_ids=["clm_1"], kind=EvidenceKind.EXACT_COMPUTATION,
                     replay_result="pass",
                     generator_identity={"findings": {"classification": "exhaustive_finite",
                                                       "exact_arithmetic": True,
                                                       "coverage_statement": True}})
    _admit(router, exact)
    counter = Evidence(evidence_id="ev_c", claim_ids=["clm_1"], kind=EvidenceKind.COUNTEREXAMPLE,
                       replay_result="pass",
                       generator_identity={"findings": {"exact_witness_checked": True,
                                                         "in_stated_domain": True}})
    _admit(router, counter)
    assert graph.claims["clm_1"].truth_status == TruthStatus.CONFLICTED


def test_scc_handles_equivalence_cycle(tmp_path):
    # A <-> B equivalence cycle must not infinite-loop during propagation.
    adjacency = {"A": {"B"}, "B": {"A"}, "C": {"A"}}
    comps = strongly_connected_components(adjacency)
    sizes = sorted(len(c) for c in comps)
    assert sizes == [1, 2]


# ── blackboard ──────────────────────────────────────────────────────────────────

def test_blackboard_proposal_cannot_assert_status(tmp_path):
    graph = _graph(tmp_path)
    graph.propose_claim(claim_id="goal", interpretation_id="int-1",
                        canonical_formula="G", actor=ACTOR)
    graph.add_branch(Branch(branch_id="br1", goal_claim_ids=["goal"],
                            interpretation_id="int-1"), actor=ACTOR)
    issuer = AuthorityTokenIssuer()
    token = issuer.issue(
        authority_name="program_worker", subject="worker",
        resources=("branch:br1",),
    )
    bb = Blackboard(graph, authority_guard=issuer)
    with pytest.raises(BlackboardError):
        bb.write_proposal(
            {"kind": "claim_proposal", "branch_id": "br1", "truth_status": "SUPPORTED"},
            token=token,
        )
    bb.write_proposal(
        {"kind": "claim_proposal", "branch_id": "br1", "canonical_formula": "P"},
        token=token,
    )
    assert len(bb.pending("claim_proposal", token=token)) == 1


def test_blackboard_slice_exposes_true_tier(tmp_path):
    from egmra.truth import Branch
    graph = _graph(tmp_path)
    graph.propose_claim(claim_id="goal", interpretation_id="int-1",
                        canonical_formula="G", actor=ACTOR)
    graph.add_branch(Branch(branch_id="br1", goal_claim_ids=["goal"],
                            interpretation_id="int-1"), actor=ACTOR)
    issuer = AuthorityTokenIssuer()
    packet = {"x": 1}
    packet_hash = content_id(packet)
    token = issuer.issue(
        authority_name="program_worker", subject="worker",
        resources=("branch:br1", f"packet:{packet_hash}"),
    )
    bb = Blackboard(graph, authority_guard=issuer)
    sl = bb.read_slice(
        branch_id="br1", packet_hash=packet_hash, packet=packet, token=token
    )
    assert sl.visible_claims["goal"]["truth_status"] == "UNKNOWN"
    assert sl.packet_hash == packet_hash


# ── views ───────────────────────────────────────────────────────────────────────

def test_sqlite_materialization_and_manifest(tmp_path):
    graph = _graph(tmp_path)
    graph.propose_claim(claim_id="clm_1", interpretation_id="int-1",
                        canonical_formula="P", actor=ACTOR)
    db = materialize_sqlite(graph, tmp_path / "view.db")
    assert db.exists()
    m1 = manifest_projection(graph, problem_id="erdos-1")
    m2 = manifest_projection(graph, problem_id="erdos-1")
    assert m1["projection_hash"] == m2["projection_hash"]  # deterministic
    assert m1["claim_count"] == 1
