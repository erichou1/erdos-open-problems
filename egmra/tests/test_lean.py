"""Tests for the Lean plane: service API, L0-L5, coverage, aristotle routing."""

import pytest

from egmra.lean import (
    AristotleRequest,
    AristotleRouting,
    ArchiveManifest,
    BlueprintError,
    CoverageClaim,
    FormalBlueprint,
    FormalHole,
    LeanCandidate,
    LeanService,
    MissingLibraryWorkflow,
    ProofSync,
    ProviderAttestation,
    SyncLink,
    build_target_package,
    freeze_blueprint,
    harden,
    puct_score,
    risk_weighted_formal_coverage,
    route_diagnostic,
    select_sentinels,
)
from egmra.provenance.hashing import sha256_hex

LOCKED = "theorem target : ∀ n : ℕ, n + 0 = n := by intro n; simp"
LOCKED_TYPE = "∀ n : ℕ, n + 0 = n"


def _service(**kw):
    return LeanService(**kw)


# ── service: verify_declaration ─────────────────────────────────────────────────

def test_injected_status_callback_is_not_a_kernel_certificate():
    svc = _service(kernel_runner=lambda **kw: "kernel_verified")
    env = svc.create_environment(lean_version="4.9.0", mathlib_commit="abc",
                                 project_hash="p", imports=("Mathlib",))
    cert = svc.verify_declaration(
        environment=env, source=LOCKED, declaration_name="target",
        expected_type_hash=sha256_hex(LOCKED_TYPE),
        immutable_target_module_hash="mod-hash",
    )
    assert not cert.kernel_verified
    assert not cert.target_type_matches
    assert not cert.passed
    assert cert.axiom_whitelist_ok  # static diagnostic only, not an attested closure


def test_vendor_reported_never_passes():
    svc = _service(kernel_runner=lambda **kw: "kernel_verified")
    env = svc.create_environment(lean_version="4.9.0", mathlib_commit="abc", project_hash="p")
    cert = svc.verify_declaration(
        environment=env, source=LOCKED, declaration_name="target",
        expected_type_hash=sha256_hex(LOCKED_TYPE), immutable_target_module_hash="m",
        verification_method="aristotle_reported",
    )
    assert not cert.kernel_verified and not cert.passed


def test_placeholder_and_wrong_type_fail():
    svc = _service(kernel_runner=lambda **kw: "kernel_verified")
    env = svc.create_environment(lean_version="4.9.0", mathlib_commit="abc", project_hash="p")
    src = "theorem target : ∀ n : ℕ, n + 0 = n := by sorry"
    cert = svc.verify_declaration(
        environment=env, source=src, declaration_name="target",
        expected_type_hash=sha256_hex(LOCKED_TYPE), immutable_target_module_hash="m",
    )
    assert cert.placeholder_findings and not cert.passed
    # wrong expected type -> target mismatch
    cert2 = svc.verify_declaration(
        environment=env, source=LOCKED, declaration_name="target",
        expected_type_hash=sha256_hex("different type"), immutable_target_module_hash="m",
    )
    assert not cert2.target_type_matches and not cert2.passed


def test_no_kernel_runner_cannot_verify():
    svc = _service()  # no kernel available
    env = svc.create_environment(lean_version="4.9.0", mathlib_commit="abc", project_hash="p")
    cert = svc.verify_declaration(
        environment=env, source=LOCKED, declaration_name="target",
        expected_type_hash=sha256_hex(LOCKED_TYPE), immutable_target_module_hash="m",
    )
    assert not cert.kernel_verified and not cert.passed


def test_native_decide_flagged_unsafe():
    svc = _service(kernel_runner=lambda **kw: "kernel_verified")
    env = svc.create_environment(lean_version="4.9.0", mathlib_commit="abc", project_hash="p")
    src = "theorem target : ∀ n : ℕ, n + 0 = n := by native_decide"
    cert = svc.verify_declaration(
        environment=env, source=src, declaration_name="target",
        expected_type_hash=sha256_hex(LOCKED_TYPE), immutable_target_module_hash="m",
    )
    assert cert.unsafe_findings and not cert.passed


def test_compare_statements_unchecked_proof_text_is_only_plausible():
    svc = _service()
    plausible = svc.compare_statements(declaration_a="A", declaration_b="B", relation="iff")
    assert plausible.verdict == "plausibly_corresponding"
    unchecked = svc.compare_statements(declaration_a="A", declaration_b="B", relation="iff",
                                       proof_artifact="A <-> B proof term")
    assert unchecked.verdict == "plausibly_corresponding"
    assert not unchecked.proof_artifact_hash


def test_goal_capsule_key_is_context_sensitive():
    svc = _service()
    env = svc.create_environment(lean_version="4.9.0", mathlib_commit="abc", project_hash="p")
    g1 = svc.goal_state(environment=env, local_context=("h : n > 0",), target_expression="P n")
    g2 = svc.goal_state(environment=env, local_context=("h : n ≥ 0",), target_expression="P n")
    assert g1.key() != g2.key()


# ── L0 target package ───────────────────────────────────────────────────────────

def test_target_package_freezes_declaration_hash():
    pkg = build_target_package(
        interpretation_id="int-1", informal_claim="n+0=n",
        candidates=[
            LeanCandidate("cand_a", LOCKED_TYPE, "for all naturals n, n+0=n"),
            LeanCandidate("cand_b", "∀ n : ℕ, 0 + n = n", "for all naturals n, 0+n=n"),
        ],
        example_lemmas=["checked n=0,1"],
        anti_example_lemmas=["rejected integer-domain mutation"],
        interpretation_approved=True,
    )
    assert not pkg.frozen
    h = pkg.approve("cand_a")
    assert pkg.frozen and h == sha256_hex(LOCKED_TYPE)


def test_target_package_requires_2_to_3_candidates():
    with pytest.raises(ValueError):
        build_target_package(interpretation_id="i", informal_claim="c", candidates=[])
    with pytest.raises(ValueError):
        build_target_package(
            interpretation_id="i",
            informal_claim="c",
            candidates=[LeanCandidate("only", "P", "P")],
        )


# ── L1 sentinels + F(c) ─────────────────────────────────────────────────────────

def test_sentinel_selection_prioritizes_central_risky_lemmas():
    claims = [
        {"claim_id": "glue", "centrality": 0.1, "semantic_risk": 0.1, "formalization_cost": 1.0},
        {"claim_id": "central", "centrality": 0.9, "semantic_risk": 0.8, "formalization_cost": 1.0},
        {"claim_id": "bdry", "sentinel_kind": "boundary", "centrality": 0.2, "semantic_risk": 0.2,
         "formalization_cost": 0.5},
    ]
    picks = select_sentinels(claims)
    by_id = {p.claim_id: p for p in picks}
    assert by_id["central"].is_sentinel
    assert by_id["bdry"].is_sentinel        # structural sentinel regardless of score
    assert not by_id["glue"].is_sentinel


# ── L2 blueprint quarantine ─────────────────────────────────────────────────────

def test_blueprint_rejects_restating_helper():
    bp = FormalBlueprint(target_declaration="target", target_statement=LOCKED_TYPE)
    bp.direct_attempt_made = True
    bp.require_direct_first()
    with pytest.raises(BlueprintError):
        bp.add_hole(FormalHole("h1", "c1", goal_state=LOCKED_TYPE))  # restates target
    bp.add_hole(FormalHole("h2", "c2", goal_state="lemma about divisibility"))
    assert not bp.production_imports_quarantine()


def test_blueprint_requires_direct_first():
    bp = FormalBlueprint(target_declaration="t", target_statement="S")
    with pytest.raises(BlueprintError):
        bp.require_direct_first()


# ── L3 proof state ─────────────────────────────────────────────────────────────

def test_puct_prefers_debt_reduction():
    high = puct_score(q=0.5, prior=0.3, parent_visits=10, action_visits=1,
                      delta_verified_debt=2.0, cost=0.1)
    low = puct_score(q=0.5, prior=0.3, parent_visits=10, action_visits=1,
                     delta_verified_debt=0.0, cost=0.1)
    assert high > low


def test_diagnostic_routing():
    assert route_diagnostic("missing_premise") == "retrieve_premises"
    assert route_diagnostic("false_target") == "revise_target_or_search_counterexample"
    assert route_diagnostic("unknown_diag") == "escalate_to_governor"


# ── L4 sync ──────────────────────────────────────────────────────────────────────

def test_sync_requires_grounding_for_load_bearing():
    sync = ProofSync()
    with pytest.raises(ValueError):
        sync.link(SyncLink(claim_id="c1"))  # no grounding
    sync.link(SyncLink(claim_id="c1", lean_declaration="lemma1"))
    assert sync.validate_coverage(["c1"]) == []
    assert sync.validate_coverage(["c1", "c2"]) == ["c2"]
    assert sync.propagate_formal_change("lemma1") == ["c1"]


# ── L5 hardening ────────────────────────────────────────────────────────────────

def test_hardening_rejects_mock_checkers_and_dummy_archive():
    svc = _service(kernel_runner=lambda **kw: "kernel_verified",
                   independent_checker=lambda **kw: True)
    env = svc.create_environment(lean_version="4.9.0", mathlib_commit="abc", project_hash="p",
                                 imports=("Mathlib",))
    cert = svc.verify_declaration(
        environment=env, source=LOCKED, declaration_name="target",
        expected_type_hash=sha256_hex(LOCKED_TYPE), immutable_target_module_hash="m",
    )
    archive = ArchiveManifest("s", "l", "lean4.9", "log", "container")
    report = harden(cert, clean_offline_build=True, imports_minimized=True,
                    untrusted_generated=True, archive=archive)
    assert not report.releasable
    assert not report.certificate_passed
    assert not report.archived
    # without independent checker on untrusted lean -> not releasable
    svc_no_indep = _service(kernel_runner=lambda **kw: "kernel_verified")
    cert3 = svc_no_indep.verify_declaration(
        environment=env, source=LOCKED, declaration_name="target",
        expected_type_hash=sha256_hex(LOCKED_TYPE), immutable_target_module_hash="m",
    )
    report2 = harden(cert3, clean_offline_build=True, imports_minimized=True,
                     untrusted_generated=True, archive=archive)
    assert not report2.releasable


# ── §9.5 RFC ───────────────────────────────────────────────────────────────────

def test_rfc_requires_frozen_blueprint():
    claims = [
        CoverageClaim("c1", 0.9, 0.9, 0.9, adequately_verified=True),
        CoverageClaim("c2", 0.2, 0.2, 0.2, adequately_verified=False),
    ]
    frozen = freeze_blueprint(claims)
    rfc = risk_weighted_formal_coverage(claims, frozen)
    assert 0.0 < rfc < 1.0
    # adding a claim changes the blueprint -> must refreeze
    claims.append(CoverageClaim("c3", 0.1, 0.1, 0.1, adequately_verified=True))
    with pytest.raises(ValueError):
        risk_weighted_formal_coverage(claims, frozen)


# ── §9.4 missing library ─────────────────────────────────────────────────────────

def test_missing_library_workflow_in_order():
    wf = MissingLibraryWorkflow("MyLemma")
    wf.complete("verify_truly_absent")
    with pytest.raises(ValueError):
        wf.complete("assign_reuse_value")  # out of order
    for step in ["import_audit_informal", "create_local_namespace", "decompose_reusable_lemmas",
                 "prove_independent_of_target", "assign_reuse_value", "upstream_after_review"]:
        wf.complete(step)
    assert wf.ready_to_upstream


# ── §9.6 aristotle routing ───────────────────────────────────────────────────────

def test_aristotle_routing_requires_licensing_and_attestation():
    routing = AristotleRouting()
    with pytest.raises(PermissionError):
        routing.prepare_request(AristotleRequest("t", "tc", "leaf", "pkt", licensing_ok=False))
    req = routing.prepare_request(AristotleRequest("t", "tc", "leaf", "pkt", licensing_ok=True))
    assert req.locked_target_hash == "t"
    unattested = ProviderAttestation("r", "m", "b", "ts", "client-1", server_attested_revision=False)
    assert not routing.generation_reproducible(unattested)
    assert routing.sandbox_policy()["network"] == "off"
    assert "independent_check" in routing.admission_pipeline()
