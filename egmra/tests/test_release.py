"""Tests for the release plane: five gates, certificate, compiler, promotion policy."""

from dataclasses import replace
from pathlib import Path
import tempfile


from egmra.compute.artifact import ReplayReport
from egmra.intake.review import sign_intent_certificate
from egmra.lean import sign_formal_correspondence_certificate
from egmra.policy import PolicyEnforcer, sign_policy
from egmra.provenance.hashing import sha256_hex
from egmra.release import (
    PromotionPolicy,
    ReleaseCertificate,
    assemble_from_admitted_graph,
    run_five_gates,
)
from egmra.release.gates import reproducibility_gate
from egmra.tests.conftest import TEST_KEYS
from egmra.truth import (
    Evidence,
    EvidenceKind,
    EpistemicGraph,
    EventLog,
    EvidenceProfile,
    FormalCorrespondenceCertificate,
    FormalVerification,
    IntentCertificate,
    Interpretation,
    Problem,
    Verdict,
    EvidenceRouter,
    issue_truth_snapshot,
)
from egmra.truth.validators import attest_evidence

ACTOR = {"type": "agent", "id": "t", "model": "m", "version": "1"}
SOURCE_HASH = sha256_hex("source")
INTERPRETATION_HASH = sha256_hex("interpretation")
CLAIM_HASH = sha256_hex("claim")
TYPE_HASH = sha256_hex("type")


def _intent(approved=True):
    return sign_intent_certificate(IntentCertificate(
        certificate_id="ic_1", source_bytes_hash=SOURCE_HASH,
        interpretation_hash=INTERPRETATION_HASH,
        informal_claim_hash=CLAIM_HASH, reviewer_ids=["r1"], methods=[
            "independent_parse", "examples", "anti_examples", "paraphrase", "local_mutation",
        ],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "r1",
            "independent_from": ["governor", "intake_retrieval"],
            "conflicts": [],
        }],
        verdict=Verdict.APPROVED if approved else Verdict.UNRESOLVED),
        env=dict(TEST_KEYS),
    )


def _corr(approved=True):
    return sign_formal_correspondence_certificate(FormalCorrespondenceCertificate(
        certificate_id="fcc_1", intent_certificate_id="ic_1", informal_claim_hash=CLAIM_HASH,
        lean_declaration_name="target", elaborated_type_hash=TYPE_HASH, reviewer_ids=["r1"],
        notation_and_definition_map_hash=sha256_hex("notation"), methods=[
            "backtranslation", "examples", "anti_examples", "paraphrase", "local_mutation",
        ],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "r1",
            "independent_from": ["formalization_authority", "governor"],
            "conflicts": [],
        }],
        verdict=Verdict.APPROVED if approved else Verdict.UNRESOLVED),
        env=dict(TEST_KEYS),
    )


def _bindings():
    return {
        "source_bytes_hash": SOURCE_HASH,
        "interpretation_hash": INTERPRETATION_HASH,
        "informal_claim_hash": CLAIM_HASH,
        "elaborated_type_hash": TYPE_HASH,
        "env": dict(TEST_KEYS),
    }


def _run_authenticated_gates(
    *, profile, intent_cert, correspondence_cert, status="SUPPORTED", now=None, **kwargs
):
    """Issue a current truth-plane snapshot and exercise the production gate boundary."""
    gate_env = kwargs.pop("env", dict(TEST_KEYS))
    if intent_cert is not None:
        profile = replace(profile, intent_certificate_id=intent_cert.certificate_id)
    if correspondence_cert is not None:
        profile = replace(
            profile,
            formal_correspondence_certificate_id=correspondence_cert.certificate_id,
        )
    path = Path(tempfile.mkdtemp(prefix="egmra-release-unit-")) / "events.jsonl"
    log = EventLog(path, run_id=sha256_hex(str(path))[:16], env=gate_env)
    log.append(
        action="HUMAN_INTERVENTION",
        actor={"type": "truth-service", "id": "release-unit"},
        object_ids=["claim"],
    )
    snapshot = issue_truth_snapshot(
        claim_id="claim",
        canonical_hash=CLAIM_HASH,
        truth_status=status,
        evidence_profile=profile.to_dict(),
        status_version=1,
        evidence_digest=sha256_hex("evidence"),
        event_log=log,
        env=gate_env,
        issued_at=now,
    )
    gates = run_five_gates(
        truth_snapshot=snapshot,
        event_log=log,
        intent_cert=intent_cert,
        correspondence_cert=correspondence_cert,
        env=gate_env,
        now=now,
        **kwargs,
    )
    return gates, log


# ── gates ─────────────────────────────────────────────────────────────────────

def test_five_gates_are_independent_profile():
    gates, _ = _run_authenticated_gates(
        profile=EvidenceProfile(formal_verification=FormalVerification.KERNEL_CHECKED),
        intent_cert=_intent(True), correspondence_cert=_corr(True),
        novelty_verdict="N0", informal_only=False,
        **_bindings(),
    )
    p = gates.profile()
    assert p["truth"] == "T4" and p["intent"] == "I2" and p["formal_correspondence"] == "F2"
    # Missing status/significance/replay axes block a positive release label.
    assert gates.summary_label() == "honest_no_result"
    assert not gates.is_novel_autonomous_resolution()


def test_novel_autonomous_resolution_requires_all_axes():
    gates, _ = _run_authenticated_gates(
        profile=EvidenceProfile(formal_verification=FormalVerification.INDEPENDENT_CHECKER),
        intent_cert=_intent(True), correspondence_cert=_corr(True),
        novelty_verdict="N2", informal_only=False,
        responsive=True, non_vacuous=True, expert_reviewed=True,
        replay_reports=[ReplayReport(
            "a", True, True, "h", "h", "envB", original_environment_hash="envA"
        )],
        **_bindings(),
    )
    assert gates.reproducibility == "R2"
    assert gates.is_novel_autonomous_resolution()


def test_reproducibility_requires_independent_environments():
    same = [ReplayReport(
        "a", True, True, "h", "h", "envA", original_environment_hash="envA"
    )]
    two = [ReplayReport(
        "a", True, True, "h", "h", "envB", original_environment_hash="envA"
    )]
    assert reproducibility_gate([]) == "R0"
    assert reproducibility_gate(same) == "R1"
    assert reproducibility_gate(two) == "R2"


# ── certificate ─────────────────────────────────────────────────────────────────

def test_release_certificate_signs_and_verifies_and_renders_profile():
    gates, log = _run_authenticated_gates(
        profile=EvidenceProfile(), intent_cert=None, correspondence_cert=None,
        novelty_verdict="N0", informal_only=True, status="UNKNOWN",
    )
    cert = ReleaseCertificate(
        problem_contract_hash=sha256_hex("problem-contract"), active_interpretation_id="int-1",
        active_interpretation_hash=INTERPRETATION_HASH, result_claim_id="claim",
        result_claim_hash=CLAIM_HASH,
        gates=gates,
        autonomy={
            "intervention_counts": {"pre_run": 0, "in_run": 0, "post_run": 0},
            "phase_boundaries": [],
            "model_tool_trace_hash": sha256_hex("model-tool-trace"),
        },
    )
    authorization = PromotionPolicy().authorize(
        gates, subject_hash=cert.subject_hash, enforcer=_enforcer(), informal_only=True,
        release_kind="triage", env=dict(TEST_KEYS), event_log=log,
    )
    cert.sign(authorization=authorization, env=dict(TEST_KEYS), event_log=log)
    assert cert.verify(env=dict(TEST_KEYS), event_log=log)
    wrong = dict(TEST_KEYS)
    wrong["EGMRA_RELEASE_KEY"] = "other-release-key-that-is-at-least-32-bytes"
    assert not cert.verify(env=wrong, event_log=log)
    rendered = cert.render(env=dict(TEST_KEYS), event_log=log)
    assert "gate_profile" in rendered and "confidence" not in rendered


# ── compiler ───────────────────────────────────────────────────────────────────

def _graph(tmp_path):
    log = EventLog(tmp_path / "e.jsonl")
    g = EpistemicGraph(log)
    g.add_problem(Problem(problem_id="p1"), actor=ACTOR)
    g.add_interpretation(Interpretation("int-1", "p1", "S"), actor=ACTOR)
    return g


def _support(g, cid):
    router = EvidenceRouter(g)
    ev = Evidence(evidence_id=f"ev_{cid}", claim_ids=[cid],
                  claim_bindings={cid: g.claims[cid].canonical_hash},
                  kind=EvidenceKind.INFORMAL_REVIEW,
                  generator_identity={"findings": {"reviewers": [
                      {"reviewer_id": "a", "lineage": "f1", "verdict": "pass"},
                      {"reviewer_id": "b", "lineage": "f2", "verdict": "pass"}]}})
    router.admit(attest_evidence(ev, env=dict(TEST_KEYS)), actor=ACTOR)


def test_compiler_uses_only_admitted_claims(tmp_path):
    g = _graph(tmp_path)
    g.propose_claim(claim_id="lemma", interpretation_id="int-1", canonical_formula="L", actor=ACTOR)
    g.propose_claim(claim_id="goal", interpretation_id="int-1", canonical_formula="G",
                    dependencies=["lemma"], actor=ACTOR)
    _support(g, "lemma")
    _support(g, "goal")
    proof = assemble_from_admitted_graph(g, "goal")
    assert proof.complete and set(proof.used_claim_ids) == {"lemma", "goal"}


def test_compiler_refuses_unsupported_claim(tmp_path):
    g = _graph(tmp_path)
    g.propose_claim(claim_id="goal", interpretation_id="int-1", canonical_formula="G", actor=ACTOR)
    proof = assemble_from_admitted_graph(g, "goal")  # goal is UNKNOWN
    assert not proof.complete and "goal" in proof.missing


# ── promotion policy ─────────────────────────────────────────────────────────────

def _enforcer(promotion=True, formal=True):
    policy = sign_policy(
        {"promotion": promotion, "formal_promotion": formal}, env=dict(TEST_KEYS)
    )
    return PolicyEnforcer(policy, verification_env=dict(TEST_KEYS))


def test_promotion_blocked_when_feature_disabled():
    gates, log = _run_authenticated_gates(
        profile=EvidenceProfile(formal_verification=FormalVerification.INDEPENDENT_CHECKER),
        intent_cert=_intent(True), correspondence_cert=_corr(True),
        novelty_verdict="N1", informal_only=False, responsive=True, non_vacuous=True,
        replay_reports=[ReplayReport(
            "a", True, True, "h", "h", "envA", original_environment_hash="envA"
        )], **_bindings())
    decision = PromotionPolicy().decide(
        gates, enforcer=_enforcer(promotion=False), informal_only=False,
        env=dict(TEST_KEYS), event_log=log,
    )
    assert not decision.promoted and "feature policy" in decision.reasons[0]


def test_formal_promotion_requires_kernel_intent_correspondence():
    enforcer = _enforcer()
    # missing correspondence -> blocked
    gates_no_corr, no_corr_log = _run_authenticated_gates(
        profile=EvidenceProfile(formal_verification=FormalVerification.INDEPENDENT_CHECKER),
        intent_cert=_intent(True), correspondence_cert=_corr(False),
        novelty_verdict="N1", informal_only=False, responsive=True, non_vacuous=True,
        replay_reports=[ReplayReport(
            "a", True, True, "h", "h", "envA", original_environment_hash="envA"
        )], **_bindings())
    d1 = PromotionPolicy().decide(
        gates_no_corr, enforcer=enforcer, informal_only=False, env=dict(TEST_KEYS),
        event_log=no_corr_log,
    )
    assert not d1.promoted
    # full formal profile -> promoted
    gates_ok, ok_log = _run_authenticated_gates(
        profile=EvidenceProfile(formal_verification=FormalVerification.INDEPENDENT_CHECKER),
        intent_cert=_intent(True), correspondence_cert=_corr(True),
        novelty_verdict="N1", informal_only=False, responsive=True, non_vacuous=True,
        replay_reports=[ReplayReport(
            "a", True, True, "h", "h", "envA", original_environment_hash="envA"
        )], **_bindings())
    d2 = PromotionPolicy().decide(
        gates_ok, enforcer=_enforcer(), informal_only=False, env=dict(TEST_KEYS),
        event_log=ok_log,
    )
    assert d2.promoted


def test_informal_promotion_needs_t3():
    enforcer = _enforcer()
    gates, log = _run_authenticated_gates(
        profile=EvidenceProfile(),  # T0
        intent_cert=_intent(True), correspondence_cert=None,
        novelty_verdict="N1", informal_only=True, responsive=True, non_vacuous=True,
        replay_reports=[ReplayReport(
            "a", True, True, "h", "h", "envA", original_environment_hash="envA"
        )], **_bindings())
    d = PromotionPolicy().decide(
        gates, enforcer=enforcer, informal_only=True, env=dict(TEST_KEYS),
        event_log=log,
    )
    assert not d.promoted and any("T3" in r for r in d.reasons)
