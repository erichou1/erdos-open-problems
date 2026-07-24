"""Independent adversarial tests for Lean and release trust boundaries.

These tests intentionally exercise public/direct entry points.  A caller-owned
boolean, string, mock callback, unsigned gate profile, or public development key
must never become production proof or a releasable result.
"""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import tempfile

import pytest

from egmra.comms.render import render_certificate, render_human_summary
from egmra.intake.review import sign_intent_certificate
from egmra.compute.artifact import ReplayReport
from egmra.lean import (
    ArchiveManifest,
    AttestedKernelRunner,
    CheckerAttestation,
    CheckerRequest,
    CheckedEquivalenceProof,
    FormalCertificate,
    CoverageClaim,
    FormalBlueprint,
    FormalHole,
    LeanCandidate,
    LeanService,
    ProofSync,
    SyncLink,
    build_target_package,
    freeze_blueprint,
    harden,
    risk_weighted_formal_coverage,
    sign_formal_correspondence_certificate,
    verify_formal_certificate,
)
from egmra.policy import PolicyEnforcer, sign_policy
from egmra.provenance.hashing import is_sha256, sha256_bytes, sha256_hex
from egmra.release import PromotionPolicy, ReleaseCertificate, run_five_gates
from egmra.release.gates import formal_correspondence_gate, reproducibility_gate
from egmra.truth import (
    EvidenceProfile,
    EventLog,
    ExactComputation,
    FormalCorrespondenceCertificate,
    FormalVerification,
    IntentCertificate,
    Verdict,
    issue_truth_snapshot,
)
from egmra.tests.conftest import TEST_KEYS


LOCKED = "theorem target : ∀ n : ℕ, n + 0 = n := by intro n; simp"
LOCKED_TYPE = "∀ n : ℕ, n + 0 = n"
SOURCE_HASH = sha256_hex("source")
INTERPRETATION_HASH = sha256_hex("interpretation")
CLAIM_HASH = sha256_hex("claim")


def _environment(service: LeanService):
    return service.create_environment(
        lean_version="4.9.0",
        mathlib_commit="abc",
        project_hash="project",
        imports=("Mathlib",),
    )


def _verify(service: LeanService, **overrides):
    arguments = {
        "environment": _environment(service),
        "source": LOCKED,
        "declaration_name": "target",
        "expected_type_hash": sha256_hex(LOCKED_TYPE),
        "immutable_target_module_hash": "target-module",
    }
    arguments.update(overrides)
    return service.verify_declaration(**arguments)


def test_caller_boolean_cannot_claim_kernel_verification():
    certificate = _verify(LeanService(), kernel_result=True)
    assert not certificate.kernel_verified
    assert not certificate.passed


def test_injected_lambda_or_status_string_is_nonproduction():
    for callback in (lambda **_: True, lambda **_: "kernel_verified"):
        certificate = _verify(LeanService(kernel_runner=callback))
        assert not certificate.kernel_verified
        assert not certificate.passed


def test_arbitrary_verification_method_never_passes():
    certificate = _verify(
        LeanService(kernel_runner=lambda **_: "kernel_verified"),
        verification_method="trust_me_bro",
    )
    assert not certificate.passed


def test_arbitrary_proof_text_does_not_establish_formal_equivalence():
    result = LeanService().compare_statements(
        declaration_a="A",
        declaration_b="B",
        relation="iff",
        proof_artifact="this is merely an unchecked string",
    )
    assert result.verdict != "equivalent"
    assert not result.proof_artifact_hash


def _forged_formal_certificate() -> FormalCertificate:
    """A structurally perfect caller-owned object with no trusted signature."""
    return FormalCertificate(
        expected_type_hash=sha256_hex("A iff B"),
        candidate_declaration_hash=sha256_hex("declaration"),
        proof_term_hash=sha256_hex("proof"),
        immutable_target_module_hash=sha256_hex("target-module"),
        source_tree_hash=sha256_hex("tree"),
        transitive_axioms=(),
        axiom_whitelist_ok=True,
        placeholder_findings=(),
        unsafe_findings=(),
        trust_policy_hash=sha256_hex("policy"),
        checker_id="forged-checker",
        checker_version="forged-version",
        independent_checker_id="forged-independent",
        checker_log_hash=sha256_hex("log"),
        kernel_verified=True,
        target_type_matches=True,
        verification_method="local_lean_kernel",
        candidate_type_hash=sha256_hex("A iff B"),
        environment_id=sha256_hex("environment"),
        checker_attestation_hash=sha256_hex("attestation"),
        production_checker=True,
        clean_replay=True,
        network_disabled=True,
        axiom_closure_verified=True,
        import_audit_verified=True,
        immutable_target_isolated=True,
        checker_trust_base="forged-trust-base",
        source_environment_bound=True,
    )


def test_caller_constructed_formal_certificate_cannot_self_authenticate_or_harden():
    forged = _forged_formal_certificate()
    assert not forged.passed
    report = harden(
        forged,
        clean_offline_build=True,
        imports_minimized=True,
        untrusted_generated=True,
        archive=ArchiveManifest(
            forged.source_tree_hash,
            sha256_hex("lake-manifest"),
            "lean-4.9.0",
            sha256_hex("build-log"),
            sha256_hex("container"),
            (forged.candidate_declaration_hash,),
        ),
    )
    assert not report.releasable


def test_legitimate_unrelated_certificate_cannot_be_relabelled_as_equivalence():
    forged = _forged_formal_certificate()
    proof = CheckedEquivalenceProof(
        declaration_a_hash=sha256_hex("A"),
        declaration_b_hash=sha256_hex("B"),
        relation="iff",
        certificate=forged,
        proof_artifact_hash=sha256_hex("caller-selected-artifact"),
    )
    result = LeanService(checker_env=dict(TEST_KEYS)).compare_statements(
        declaration_a="A",
        declaration_b="B",
        relation="iff",
        proof_artifact=proof,
    )
    assert result.verdict != "equivalent"


def test_regex_parse_is_not_reported_as_trusted_elaboration():
    result = LeanService().elaborate(
        environment=_environment(LeanService()),
        source=LOCKED,
        declaration_name="target",
    )
    assert result["trusted_elaboration"] is False
    assert result["backend"] == "static_source_scan"


def test_l0_rejects_one_candidate_and_requires_semantic_probe_results_before_freeze():
    candidate_a = LeanCandidate("a", "P", "P in prose")
    candidate_b = LeanCandidate("b", "Q", "Q in prose")
    with pytest.raises(ValueError):
        build_target_package(
            interpretation_id="i", informal_claim="P", candidates=[candidate_a]
        )
    unreviewed = build_target_package(
        interpretation_id="i", informal_claim="P", candidates=[candidate_a, candidate_b]
    )
    with pytest.raises(Exception):
        unreviewed.approve("a")
    reviewed = build_target_package(
        interpretation_id="i",
        informal_claim="P",
        candidates=[candidate_a, candidate_b],
        example_lemmas=["example passed"],
        anti_example_lemmas=["anti-example rejected"],
        interpretation_approved=True,
    )
    assert reviewed.approve("a") == sha256_hex("P")


def test_l2_holes_cannot_bypass_direct_target_attempt():
    blueprint = FormalBlueprint(target_declaration="target", target_statement="P")
    with pytest.raises(Exception):
        blueprint.add_hole(FormalHole("helper", "claim", "Q"))


def test_frozen_rfc_rejects_post_freeze_weight_manipulation():
    original = [CoverageClaim("central", 1.0, 1.0, 1.0, False)]
    frozen = freeze_blueprint(original)
    manipulated = [CoverageClaim("central", 0.0, 0.0, 0.0, True)]
    with pytest.raises(ValueError):
        risk_weighted_formal_coverage(manipulated, frozen)


def test_sync_link_rejects_ambiguous_multiple_groundings():
    sync = ProofSync()
    with pytest.raises(ValueError):
        sync.link(SyncLink(
            claim_id="c",
            lean_declaration="lemma_c",
            source_theorem_id="source_c",
        ))


def test_boolean_hardening_inputs_and_dummy_archive_cannot_create_t5():
    certificate = _verify(LeanService(kernel_runner=lambda **_: True))
    report = harden(
        certificate,
        clean_offline_build=True,
        imports_minimized=True,
        untrusted_generated=True,
        archive=ArchiveManifest("s", "l", "lean", "log", "container"),
    )
    assert not report.releasable


def _snapshot_context(
    profile: EvidenceProfile, *, status: str, now: float | None = None,
):
    path = Path(tempfile.mkdtemp(prefix="egmra-release-test-")) / "events.jsonl"
    log = EventLog(path, run_id=sha256_hex(str(path))[:16], env=dict(TEST_KEYS))
    log.append(
        action="HUMAN_INTERVENTION",
        actor={"type": "truth-service", "id": "release-test"},
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
        env=dict(TEST_KEYS),
        issued_at=now,
    )
    return snapshot, log


def _unresolved_gates():
    snapshot, log = _snapshot_context(
        EvidenceProfile(formal_verification=FormalVerification.KERNEL_CHECKED),
        status="SUPPORTED",
    )
    gates = run_five_gates(
        truth_snapshot=snapshot,
        event_log=log,
        intent_cert=None,
        correspondence_cert=None,
        novelty_verdict="N0",
        informal_only=False,
        env=dict(TEST_KEYS),
    )
    return gates, log


def test_unresolved_axes_never_render_verified_sounding_result():
    gates, _ = _unresolved_gates()
    assert gates.truth == "T4"
    assert gates.intent == "I0"
    assert gates.novelty == "N0"
    assert gates.significance == "S0"
    assert gates.reproducibility == "R0"
    assert gates.summary_label() == "honest_no_result"


def test_caller_hardened_boolean_cannot_upgrade_t4_to_t5():
    snapshot, log = _snapshot_context(
        EvidenceProfile(formal_verification=FormalVerification.KERNEL_CHECKED),
        status="SUPPORTED",
    )
    gates = run_five_gates(
        truth_snapshot=snapshot,
        event_log=log,
        intent_cert=None,
        correspondence_cert=None,
        novelty_verdict="N0",
        informal_only=False,
        hardened=True,
        env=dict(TEST_KEYS),
    )
    assert gates.truth == "T4"


def test_raw_caller_evidence_profile_is_not_a_release_gate_authority():
    with pytest.raises(Exception):
        run_five_gates(
            profile=EvidenceProfile(
                formal_verification=FormalVerification.INDEPENDENT_CHECKER
            ),
            intent_cert=None,
            correspondence_cert=None,
            novelty_verdict="N2",
            informal_only=False,
            env=dict(TEST_KEYS),
        )


def test_reproducibility_gate_compares_original_and_replay_environments():
    missing_identity = ReplayReport("a", True, True, "h", "h", "replay")
    same = ReplayReport(
        "a", True, True, "h", "h", "same", original_environment_hash="same"
    )
    independent = ReplayReport(
        "a", True, True, "h", "h", "replay", original_environment_hash="original"
    )
    assert reproducibility_gate([missing_identity]) == "R0"
    assert reproducibility_gate([same]) == "R1"
    assert reproducibility_gate([independent]) == "R2"


def test_release_signing_has_no_public_or_missing_key_fallback():
    gates, log = _unresolved_gates()
    certificate = ReleaseCertificate(
        "pc", "int", "ih", "claim", "ch", gates
    )
    with pytest.raises(Exception):
        certificate.sign(env={}, event_log=log)
    with pytest.raises(Exception):
        certificate.sign(env={"EGMRA_RELEASE_KEY": "weak"}, event_log=log)


def test_release_cannot_be_signed_before_promotion_authorization():
    gates, log = _unresolved_gates()
    certificate = ReleaseCertificate(
        "pc", "int", "ih", "claim", "ch", gates
    )
    with pytest.raises(Exception):
        certificate.sign(env={"EGMRA_RELEASE_KEY": "r" * 32}, event_log=log)


def test_unsigned_and_forged_certificates_cannot_use_any_render_path():
    gates, log = _unresolved_gates()
    certificate = ReleaseCertificate(
        "pc", "int", "ih", "claim", "ch", gates
    )
    env = {
        "EGMRA_GATE_KEY": "g" * 32,
        "EGMRA_PROMOTION_KEY": "p" * 32,
        "EGMRA_RELEASE_KEY": "r" * 32,
    }
    for renderer in (
        lambda: certificate.render(env=env, event_log=log),
        lambda: render_certificate(certificate, env=env, event_log=log),
        lambda: render_human_summary(certificate, env=env, event_log=log),
    ):
        with pytest.raises(Exception):
            renderer()


def test_stale_signed_timestamp_is_rejected_even_with_matching_hmac():
    """Freshness is mandatory; recomputing an HMAC over stale state is not enough."""
    gates, log = _unresolved_gates()
    certificate = ReleaseCertificate(
        "pc", "int", "ih", "claim", "ch", gates,
        signed_at="2000-01-01T00:00:00Z",
    )
    # Current code signs this stale object; hardened code must reject it before
    # signing because it has no current gate/promotion authorization.
    with pytest.raises(Exception):
        certificate.sign(env={"EGMRA_RELEASE_KEY": "r" * 32}, event_log=log)


def _enforcer(env=TEST_KEYS):
    policy = sign_policy(
        {"promotion": True, "formal_promotion": True}, env=dict(env)
    )
    return PolicyEnforcer(policy, verification_env=dict(env))


def _attested_scoped_gates(*, now: float = 1_800_000_000.0, env=TEST_KEYS):
    intent = sign_intent_certificate(IntentCertificate(
        certificate_id="ic",
        source_bytes_hash=SOURCE_HASH,
        interpretation_hash=INTERPRETATION_HASH,
        informal_claim_hash=CLAIM_HASH,
        methods=[
            "independent_parse",
            "examples",
            "anti_examples",
            "paraphrase",
            "local_mutation",
        ],
        reviewer_ids=["intent-reviewer"],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "intent-reviewer",
            "independent_from": ["governor", "intake_retrieval"],
            "conflicts": [],
        }],
        verdict=Verdict.APPROVED,
    ), env=dict(env))
    snapshot, log = _snapshot_context(
        EvidenceProfile(
            exact_computation=ExactComputation.SCOPED_EXACT,
            intent_certificate_id="ic",
        ),
        status="SUPPORTED",
        now=now,
    )
    gates = run_five_gates(
        truth_snapshot=snapshot,
        event_log=log,
        intent_cert=intent,
        correspondence_cert=None,
        novelty_verdict="N1",
        informal_only=True,
        responsive=True,
        non_vacuous=True,
        replay_reports=[ReplayReport(
            "a", True, True, "h", "h", "env-a", original_environment_hash="env-a"
        )],
        source_bytes_hash=SOURCE_HASH,
        interpretation_hash=INTERPRETATION_HASH,
        informal_claim_hash=CLAIM_HASH,
        env=dict(env),
        issued_at="2027-01-15T08:00:00Z",
        now=now,
    )
    return gates, log


def _scoped_certificate(gates):
    return ReleaseCertificate(
        problem_contract_hash=sha256_hex("problem-contract"),
        active_interpretation_id="int",
        active_interpretation_hash=INTERPRETATION_HASH,
        result_claim_id="claim",
        result_claim_hash=CLAIM_HASH,
        gates=gates,
        truth_certificate_ids=("truth-cert",),
        intent_certificate_id="ic",
        novelty_search_packet_hash=sha256_hex("novelty-packet"),
        reproducibility_environments=("env-a",),
        autonomy={
            "intervention_counts": {"pre_run": 0, "in_run": 0, "post_run": 0},
            "phase_boundaries": [],
            "model_tool_trace_hash": sha256_hex("model-tool-trace"),
        },
    )


def test_attested_gates_authorization_signature_and_render_form_one_chain():
    now = 1_800_000_000.0
    gates, log = _attested_scoped_gates(now=now)
    assert gates.verify_attestation(env=dict(TEST_KEYS), now=now, event_log=log)
    assert gates.summary_label() == "verified_finite_or_conditional_result"
    certificate = _scoped_certificate(gates)
    authorization = PromotionPolicy().authorize(
        gates,
        subject_hash=certificate.subject_hash,
        enforcer=_enforcer(),
        informal_only=True,
        release_kind="scoped_result",
        env=dict(TEST_KEYS),
        now=now,
        event_log=log,
    )
    assert authorization.promoted and authorization.authorization_signature
    certificate.sign(
        authorization=authorization, env=dict(TEST_KEYS), now=now, event_log=log
    )
    assert certificate.verify(env=dict(TEST_KEYS), now=now, event_log=log)
    assert render_certificate(
        certificate, env=dict(TEST_KEYS), now=now, event_log=log
    )["label"] \
        == "verified_finite_or_conditional_result"


def test_gate_status_mutation_invalidates_attestation_and_promotion():
    now = 1_800_000_000.0
    gates, log = _attested_scoped_gates(now=now)
    forged = replace(gates, truth="T5")
    assert not forged.verify_attestation(env=dict(TEST_KEYS), now=now, event_log=log)
    decision = PromotionPolicy().decide(
        forged,
        enforcer=_enforcer(),
        informal_only=False,
        env=dict(TEST_KEYS),
        now=now,
        event_log=log,
    )
    assert not decision.promoted
    assert any("forged" in reason for reason in decision.reasons)


def test_promotion_authorization_cannot_be_reused_for_another_subject():
    now = 1_800_000_000.0
    gates, log = _attested_scoped_gates(now=now)
    first = _scoped_certificate(gates)
    authorization = PromotionPolicy().authorize(
        gates,
        subject_hash=first.subject_hash,
        enforcer=_enforcer(),
        informal_only=True,
        release_kind="scoped_result",
        env=dict(TEST_KEYS),
        now=now,
        event_log=log,
    )
    second = _scoped_certificate(gates)
    second.result_claim_hash = "different"
    with pytest.raises(Exception):
        second.sign(
            authorization=authorization, env=dict(TEST_KEYS), now=now, event_log=log
        )


def test_valid_gate_for_one_claim_cannot_authorize_release_of_another_claim():
    now = 1_800_000_000.0
    gates, log = _attested_scoped_gates(now=now)
    substituted = _scoped_certificate(gates)
    substituted.result_claim_id = "different-claim"
    substituted.result_claim_hash = sha256_hex("different-claim")
    authorization = PromotionPolicy().authorize(
        gates,
        subject_hash=substituted.subject_hash,
        enforcer=_enforcer(),
        informal_only=True,
        release_kind="scoped_result",
        env=dict(TEST_KEYS),
        now=now,
        event_log=log,
    )
    assert authorization.promoted
    with pytest.raises(Exception):
        substituted.sign(
            authorization=authorization,
            env=dict(TEST_KEYS),
            now=now,
            event_log=log,
        )


def test_intent_gate_cannot_authorize_a_different_active_interpretation():
    now = 1_800_000_000.0
    gates, log = _attested_scoped_gates(now=now)
    substituted = _scoped_certificate(gates)
    substituted.active_interpretation_hash = sha256_hex("different-interpretation")
    authorization = PromotionPolicy().authorize(
        gates,
        subject_hash=substituted.subject_hash,
        enforcer=_enforcer(),
        informal_only=True,
        release_kind="scoped_result",
        env=dict(TEST_KEYS),
        now=now,
        event_log=log,
    )
    assert authorization.promoted
    with pytest.raises(Exception):
        substituted.sign(
            authorization=authorization,
            env=dict(TEST_KEYS),
            now=now,
            event_log=log,
        )


def test_signed_release_mutation_and_stale_render_fail_closed():
    now = 1_800_000_000.0
    gates, log = _attested_scoped_gates(now=now)
    certificate = _scoped_certificate(gates)
    authorization = PromotionPolicy().authorize(
        gates,
        subject_hash=certificate.subject_hash,
        enforcer=_enforcer(),
        informal_only=True,
        release_kind="scoped_result",
        env=dict(TEST_KEYS),
        now=now,
        event_log=log,
    )
    certificate.sign(
        authorization=authorization, env=dict(TEST_KEYS), now=now, event_log=log
    )
    certificate.result_claim_hash = "tampered"
    assert not certificate.verify(env=dict(TEST_KEYS), now=now, event_log=log)
    with pytest.raises(Exception):
        render_human_summary(certificate, env=dict(TEST_KEYS), now=now, event_log=log)

    fresh = _scoped_certificate(gates)
    authorization = PromotionPolicy().authorize(
        gates,
        subject_hash=fresh.subject_hash,
        enforcer=_enforcer(),
        informal_only=True,
        release_kind="scoped_result",
        env=dict(TEST_KEYS),
        now=now,
        event_log=log,
    )
    fresh.sign(authorization=authorization, env=dict(TEST_KEYS), now=now, event_log=log)
    with pytest.raises(Exception):
        fresh.render(env=dict(TEST_KEYS), now=now + 901.0, event_log=log)


def test_reused_intent_approval_does_not_survive_binding_change():
    gates, _ = _attested_scoped_gates()
    assert gates.intent == "I2"
    snapshot, log = _snapshot_context(
        EvidenceProfile(
            exact_computation=ExactComputation.SCOPED_EXACT,
            intent_certificate_id="ic",
        ),
        status="SUPPORTED",
    )
    stale = run_five_gates(
        truth_snapshot=snapshot,
        event_log=log,
        intent_cert=IntentCertificate(
            certificate_id="ic",
            source_bytes_hash="old-source",
            interpretation_hash="interpretation-hash",
            informal_claim_hash="claim-hash",
            methods=[
                "independent_parse", "examples", "anti_examples", "paraphrase",
                "local_mutation",
            ],
            reviewer_ids=["r"],
            verdict=Verdict.APPROVED,
        ),
        correspondence_cert=None,
        novelty_verdict="N1",
        informal_only=True,
        source_bytes_hash="new-source",
        interpretation_hash="interpretation-hash",
        informal_claim_hash="claim-hash",
        env=dict(TEST_KEYS),
    )
    assert stale.intent != "I2"


def test_formal_correspondence_cannot_be_f2_when_parent_intent_binding_is_stale():
    intent = IntentCertificate(
        certificate_id="ic",
        source_bytes_hash="old-source",
        interpretation_hash="interpretation",
        informal_claim_hash="claim",
        methods=[
            "independent_parse", "examples", "anti_examples", "paraphrase", "local_mutation",
        ],
        reviewer_ids=["intent-reviewer"],
        verdict=Verdict.APPROVED,
    )
    correspondence = FormalCorrespondenceCertificate(
        certificate_id="fcc",
        intent_certificate_id="ic",
        informal_claim_hash="claim",
        lean_declaration_name="target",
        elaborated_type_hash="type",
        notation_and_definition_map_hash=sha256_hex("notation"),
        methods=[
            "backtranslation", "examples", "anti_examples", "paraphrase", "local_mutation",
        ],
        reviewer_ids=["correspondence-reviewer"],
        verdict=Verdict.APPROVED,
    )
    snapshot, log = _snapshot_context(
        EvidenceProfile(
            formal_verification=FormalVerification.INDEPENDENT_CHECKER,
            intent_certificate_id="ic",
            formal_correspondence_certificate_id="fcc",
        ),
        status="SUPPORTED",
    )
    gates = run_five_gates(
        truth_snapshot=snapshot,
        event_log=log,
        intent_cert=intent,
        correspondence_cert=correspondence,
        novelty_verdict="N1",
        informal_only=False,
        source_bytes_hash="new-source",
        interpretation_hash="interpretation",
        informal_claim_hash="claim",
        elaborated_type_hash="type",
        env=dict(TEST_KEYS),
    )
    assert gates.intent != "I2"
    assert gates.formal_correspondence != "F2"


def test_raw_formal_reviewer_labels_cannot_create_f2_and_signature_is_binding_exact():
    intent = IntentCertificate(
        certificate_id="ic-auth",
        source_bytes_hash=SOURCE_HASH,
        interpretation_hash=INTERPRETATION_HASH,
        informal_claim_hash=CLAIM_HASH,
        verdict=Verdict.APPROVED,
    )
    certificate = FormalCorrespondenceCertificate(
        certificate_id="fcc-auth",
        intent_certificate_id="ic-auth",
        informal_claim_hash=CLAIM_HASH,
        lean_declaration_name="target",
        elaborated_type_hash=sha256_hex(LOCKED_TYPE),
        notation_and_definition_map_hash=sha256_hex("notation"),
        methods=[
            "backtranslation", "examples", "anti_examples", "paraphrase",
            "local_mutation",
        ],
        reviewer_ids=["formal-reviewer"],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "formal-reviewer",
            "independent_from": ["formalization_authority", "governor"],
            "conflicts": [],
        }],
        verdict=Verdict.APPROVED,
    )
    arguments = {
        "informal_only": False,
        "intent_cert": intent,
        "informal_claim_hash": CLAIM_HASH,
        "elaborated_type_hash": sha256_hex(LOCKED_TYPE),
        "parent_intent_level": "I2",
        "verification_env": dict(TEST_KEYS),
    }
    assert formal_correspondence_gate(certificate, **arguments) != "F2"
    signed = sign_formal_correspondence_certificate(
        certificate, env=dict(TEST_KEYS)
    )
    assert formal_correspondence_gate(signed, **arguments) == "F2"
    assert formal_correspondence_gate(
        replace(signed, elaborated_type_hash=sha256_hex("substituted-type")),
        **(arguments | {"elaborated_type_hash": sha256_hex("substituted-type")}),
    ) != "F2"


def test_caller_constructed_checker_attestation_is_not_a_runner():
    forged = CheckerAttestation(
        environment_id="x",
        source_hash=sha256_hex(LOCKED),
        declaration_name="target",
        expected_type_hash=sha256_hex(LOCKED_TYPE),
        candidate_type_hash=sha256_hex(LOCKED_TYPE),
        candidate_declaration_hash=sha256_hex("declaration"),
        proof_term_hash=sha256_hex("proof-term"),
        immutable_target_module_hash=sha256_hex("module"),
        trust_policy_hash=sha256_hex("policy"),
        source_tree_hash=sha256_hex("tree"),
        imports_hash=sha256_hex("imports"),
        checker_id="forged",
        checker_version="forged",
        checker_trust_base="forged",
        checker_binary_hash=sha256_hex("binary"),
        checker_log_hash=sha256_hex("log"),
        transitive_axioms=(),
        placeholder_findings=(),
        unsafe_findings=(),
        imports_audited=True,
        axiom_closure_verified=True,
        immutable_target_isolated=True,
        clean_replay=True,
        network_disabled=True,
        kernel_verified=True,
        production=True,
        issued_at="2027-01-01T00:00:00Z",
        key_fingerprint=sha256_hex(TEST_KEYS["EGMRA_LEAN_CHECKER_KEY"]),
        signature="forged",
    )
    certificate = _verify(LeanService(checker_env=dict(TEST_KEYS)), kernel_result=forged)
    assert not certificate.passed


def test_trusted_checker_subprocess_never_receives_signing_or_service_secrets(monkeypatch):
    executable = Path("/usr/bin/true")
    runner = AttestedKernelRunner(
        command=(str(executable),),
        checker_id="lean4checker",
        checker_version="pinned",
        checker_binary_hash=sha256_bytes(executable.read_bytes()),
        checker_trust_base="lean-kernel",
        env=dict(TEST_KEYS),
    )
    request = CheckerRequest(
        environment_id=sha256_hex("environment"),
        source_hash=sha256_hex(LOCKED),
        declaration_name="target",
        expected_type_hash=sha256_hex(LOCKED_TYPE),
        immutable_target_module_hash=sha256_hex("target-module"),
        trust_policy_hash=sha256_hex("trust-policy"),
    )
    captured = {}

    def fake_run(command, **kwargs):
        captured["env"] = kwargs["env"]
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({
                "kernel_verified": True,
                "candidate_type_hash": request.expected_type_hash,
                "candidate_declaration_hash": sha256_hex("declaration"),
                "proof_term_hash": sha256_hex("proof-term"),
                "source_tree_hash": sha256_hex("tree"),
                "imports_hash": sha256_hex("imports"),
                "transitive_axioms": [],
                "placeholder_findings": [],
                "unsafe_findings": [],
                "imports_audited": True,
                "axiom_closure_verified": True,
                "immutable_target_isolated": True,
                "clean_replay": True,
                "network_disabled": True,
            }),
            stderr="",
        )

    monkeypatch.setattr("egmra.lean.service.subprocess.run", fake_run)
    runner.run(request)
    assert not (set(captured["env"]) & set(TEST_KEYS))


def test_checker_response_missing_full_import_and_proof_audit_cannot_qualify(monkeypatch):
    executable = Path("/usr/bin/true")
    runner = AttestedKernelRunner(
        command=(str(executable),),
        checker_id="lean4checker",
        checker_version="pinned",
        checker_binary_hash=sha256_bytes(executable.read_bytes()),
        checker_trust_base="lean-kernel",
        env=dict(TEST_KEYS),
    )

    def incomplete_checker(command, **kwargs):
        request = json.loads(kwargs["input"])
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({
                "kernel_verified": True,
                "candidate_type_hash": request["expected_type_hash"],
                "source_tree_hash": sha256_hex("tree"),
                "imports_hash": sha256_hex("imports"),
                "transitive_axioms": [],
                "clean_replay": True,
                "network_disabled": True,
            }),
            stderr="",
        )

    monkeypatch.setattr("egmra.lean.service.subprocess.run", incomplete_checker)
    service = LeanService(kernel_runner=runner, checker_env=dict(TEST_KEYS))
    certificate = _verify(
        service,
        immutable_target_module_hash=sha256_hex("target-module"),
    )
    assert not certificate.passed


def _structured_checker_service(monkeypatch) -> LeanService:
    executable = Path("/usr/bin/true")
    runner = AttestedKernelRunner(
        command=(str(executable),),
        checker_id="lean4checker",
        checker_version="pinned",
        checker_binary_hash=sha256_bytes(executable.read_bytes()),
        checker_trust_base="lean-kernel",
        env=dict(TEST_KEYS),
    )

    def complete_checker(command, **kwargs):
        request = json.loads(kwargs["input"])
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({
                "kernel_verified": True,
                "candidate_type_hash": request["expected_type_hash"],
                "candidate_declaration_hash": sha256_hex("declaration"),
                "proof_term_hash": sha256_hex("proof-term"),
                "source_tree_hash": sha256_hex("tree"),
                "imports_hash": sha256_hex("imports"),
                "transitive_axioms": [],
                "placeholder_findings": [],
                "unsafe_findings": [],
                "imports_audited": True,
                "axiom_closure_verified": True,
                "immutable_target_isolated": True,
                "clean_replay": True,
                "network_disabled": True,
            }),
            stderr="",
        )

    monkeypatch.setattr("egmra.lean.service.subprocess.run", complete_checker)
    return LeanService(kernel_runner=runner, checker_env=dict(TEST_KEYS))


def test_complete_structured_checker_produces_authenticated_tamper_evident_certificate(
    monkeypatch,
):
    claim_bindings = {"claim": sha256_hex("claim")}
    artifact_hash = sha256_hex("proof-bundle")
    certificate = _verify(
        _structured_checker_service(monkeypatch),
        immutable_target_module_hash=sha256_hex("target-module"),
        claim_bindings=claim_bindings,
        artifact_hashes=(artifact_hash,),
    )
    assert certificate.passed
    assert certificate.verify(env=dict(TEST_KEYS))
    assert is_sha256(certificate.certificate_digest)
    assert verify_formal_certificate(
        certificate.to_dict(),
        env=dict(TEST_KEYS),
        expected_source_hash=sha256_hex(LOCKED),
        expected_environment_id=certificate.environment_id,
        expected_type_hash=sha256_hex(LOCKED_TYPE),
        expected_claim_bindings=claim_bindings,
        required_artifact_hashes=(artifact_hash,),
        expected_declaration_name="target",
    )
    assert not verify_formal_certificate(
        certificate.to_dict(),
        env=dict(TEST_KEYS),
        expected_source_hash=sha256_hex("substituted-source"),
        expected_environment_id=certificate.environment_id,
        expected_type_hash=sha256_hex(LOCKED_TYPE),
        expected_claim_bindings=claim_bindings,
        required_artifact_hashes=(artifact_hash,),
        expected_declaration_name="target",
    )
    assert not replace(
        certificate, proof_term_hash=sha256_hex("substituted-proof")
    ).verify(env=dict(TEST_KEYS))


def test_checked_equivalence_is_bound_to_exact_relation_and_checker_proof(monkeypatch):
    service = _structured_checker_service(monkeypatch)
    source = "theorem target : (A) ↔ (B) := by exact proof"
    certificate = _verify(
        service,
        source=source,
        expected_type_hash=sha256_hex("(A) ↔ (B)"),
        immutable_target_module_hash=sha256_hex("target-module"),
    )
    proof = CheckedEquivalenceProof(
        declaration_a_hash=sha256_hex("A"),
        declaration_b_hash=sha256_hex("B"),
        relation="iff",
        certificate=certificate,
        proof_artifact_hash=certificate.proof_term_hash,
    )
    assert service.compare_statements(
        declaration_a="A", declaration_b="B", relation="iff", proof_artifact=proof
    ).verdict == "equivalent"
    substituted = replace(proof, proof_artifact_hash=sha256_hex("different-proof"))
    assert service.compare_statements(
        declaration_a="A", declaration_b="B", relation="iff", proof_artifact=substituted
    ).verdict != "equivalent"


def test_authorized_release_still_rejects_placeholder_hashes_and_missing_autonomy():
    now = 1_800_000_000.0
    gates, log = _attested_scoped_gates(now=now)
    certificate = ReleaseCertificate(
        problem_contract_hash="not-a-hash",
        active_interpretation_id="int",
        active_interpretation_hash="also-not-a-hash",
        result_claim_id="claim",
        result_claim_hash="still-not-a-hash",
        gates=gates,
        intent_certificate_id="ic",
    )
    authorization = PromotionPolicy().authorize(
        gates,
        subject_hash=certificate.subject_hash,
        enforcer=_enforcer(),
        informal_only=True,
        release_kind="scoped_result",
        env=dict(TEST_KEYS),
        now=now,
        event_log=log,
    )
    assert authorization.promoted
    with pytest.raises(Exception):
        certificate.sign(
            authorization=authorization,
            env=dict(TEST_KEYS),
            now=now,
            event_log=log,
        )


def test_new_truth_event_immediately_invalidates_gate_authorization_and_release():
    """Cached approval must not outlive the exact truth-log head it authenticated."""
    now = 1_800_000_000.0
    gates, log = _attested_scoped_gates(now=now)
    certificate = _scoped_certificate(gates)
    authorization = PromotionPolicy().authorize(
        gates,
        subject_hash=certificate.subject_hash,
        enforcer=_enforcer(),
        informal_only=True,
        release_kind="scoped_result",
        env=dict(TEST_KEYS),
        now=now,
        event_log=log,
    )
    certificate.sign(
        authorization=authorization,
        env=dict(TEST_KEYS),
        now=now,
        event_log=log,
    )
    assert certificate.verify(env=dict(TEST_KEYS), now=now, event_log=log)

    log.append(
        action="HUMAN_INTERVENTION",
        actor={"type": "truth-service", "id": "post-approval-update"},
        object_ids=["claim"],
    )

    assert not gates.verify_attestation(env=dict(TEST_KEYS), now=now, event_log=log)
    assert not authorization.verify_authorization(
        gates=gates,
        subject_hash=certificate.subject_hash,
        env=dict(TEST_KEYS),
        now=now,
        event_log=log,
    )
    assert not certificate.verify(env=dict(TEST_KEYS), now=now, event_log=log)
    with pytest.raises(Exception):
        certificate.render(env=dict(TEST_KEYS), now=now, event_log=log)
