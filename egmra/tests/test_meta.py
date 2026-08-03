"""Tests for comms and meta modules: human, render, design_status, services, topology, models, risks."""

from pathlib import Path
import tempfile

import pytest

from egmra.comms import Intervention, InterventionLog, render_human_summary
from egmra.comms.render import render_certificate
from egmra.design_status import design_status, originals
from egmra.models import BakeOffResult, ModelRegistry
from egmra.policy import PolicyEnforcer, sign_policy
from egmra.provenance.hashing import sha256_hex
from egmra.provenance.stage_identity import AttestedModelIdentity
from egmra.release.certificate import ReleaseCertificate
from egmra.release.gates import run_five_gates
from egmra.release.policy import PromotionPolicy
from egmra.risks import all_risks, risk
from egmra.services import service_contract
from egmra.topology import ServiceTopology
from egmra.truth import EventLog, issue_truth_snapshot
from egmra.truth.entities import EvidenceProfile
from egmra.tests.conftest import TEST_KEYS


# ── human / autonomy ─────────────────────────────────────────────────────────

def test_intervention_log_autonomy_metadata():
    log = InterventionLog()
    log.record(Intervention("pre_run", "target_selection", "chose problem", "human-1"))
    log.record(Intervention("in_run", "hint", "suggested lemma", "human-1"))
    meta = log.autonomy_metadata()
    assert meta["total"] == 2
    assert meta["intervention_counts"]["pre_run"] == 1
    with pytest.raises(ValueError):
        Intervention("mid_run", "x", "y", "z")


# ── render ────────────────────────────────────────────────────────────────────

def test_render_never_emits_confidence():
    path = Path(tempfile.mkdtemp(prefix="egmra-meta-release-")) / "events.jsonl"
    event_log = EventLog(path, run_id=sha256_hex(str(path))[:16], env=dict(TEST_KEYS))
    event_log.append(
        action="HUMAN_INTERVENTION",
        actor={"type": "truth-service", "id": "meta-test"},
        object_ids=["clm"],
    )
    snapshot = issue_truth_snapshot(
        claim_id="clm",
        canonical_hash=sha256_hex("claim"),
        truth_status="UNKNOWN",
        evidence_profile=EvidenceProfile().to_dict(),
        status_version=1,
        evidence_digest=sha256_hex("evidence"),
        event_log=event_log,
        env=dict(TEST_KEYS),
    )
    gates = run_five_gates(
        truth_snapshot=snapshot,
        event_log=event_log,
        intent_cert=None,
        correspondence_cert=None,
        novelty_verdict="N0",
        informal_only=True,
        env=dict(TEST_KEYS),
    )
    cert = ReleaseCertificate(
        sha256_hex("problem-contract"), "int-1", sha256_hex("interpretation"),
        "clm", sha256_hex("claim"), gates,
        autonomy={
            "intervention_counts": {"pre_run": 0, "in_run": 0, "post_run": 0},
            "phase_boundaries": [],
            "model_tool_trace_hash": sha256_hex("model-tool-trace"),
        },
    )
    policy = sign_policy(
        {"promotion": True, "formal_promotion": True}, env=dict(TEST_KEYS)
    )
    enforcer = PolicyEnforcer(policy, verification_env=dict(TEST_KEYS))
    authorization = PromotionPolicy().authorize(
        gates, subject_hash=cert.subject_hash, enforcer=enforcer, informal_only=True,
        release_kind="triage", env=dict(TEST_KEYS), event_log=event_log,
    )
    cert.sign(
        authorization=authorization, env=dict(TEST_KEYS), event_log=event_log
    )
    rendered = render_certificate(cert, env=dict(TEST_KEYS), event_log=event_log)
    assert "gate_profile" in rendered
    summary = render_human_summary(cert, env=dict(TEST_KEYS), event_log=event_log)
    assert "truth=" in summary and "confidence" not in summary.lower()


# ── design status ────────────────────────────────────────────────────────────

def test_design_status_and_originals():
    assert design_status("interpretation_lattice").status == "original"
    assert design_status("kernel_certificate_validation").status == "established"
    assert "interpretation_lattice" in originals()
    with pytest.raises(KeyError):
        design_status("nope")


# ── services ──────────────────────────────────────────────────────────────────

def test_service_contracts_truth_upgrade_flags():
    assert not service_contract("literature").truth_upgrade
    assert service_contract("lean").truth_upgrade
    assert service_contract("claim_graph").truth_upgrade
    with pytest.raises(KeyError):
        service_contract("nope")


# ── topology ──────────────────────────────────────────────────────────────────

def test_topology_registration_and_authoritative_layers():
    topo = ServiceTopology()
    topo.register("event_transaction_store", "postgres://...")
    assert "artifact_store" in topo.missing_layers()
    assert topo.authoritative_layers() == ("event_transaction_store", "artifact_store")
    with pytest.raises(KeyError):
        topo.register("not_a_layer", "x")


# ── model registry ─────────────────────────────────────────────────────────────

def test_model_registry_pins_attested_local_best():
    reg = ModelRegistry()
    from egmra.provenance.stage_identity import attest_model_identity
    attested = attest_model_identity(provider="openai", model="o-research", version="2026-01")
    weak = attest_model_identity(provider="openai", model="o-mini", version="2026-01")
    reg.record_bakeoff(BakeOffResult("lean_proof_search", weak, 0.4, "2026-07"))
    reg.record_bakeoff(BakeOffResult("lean_proof_search", attested, 0.9, "2026-07"))
    pinned = reg.pin_best("lean_proof_search")
    assert pinned.model == "o-research"
    assert reg.resolve("lean_proof_search").model == "o-research"


def test_model_registry_refuses_unattested_pin():
    reg = ModelRegistry()
    label = AttestedModelIdentity("openai", "ChatGPT")
    reg.record_bakeoff(BakeOffResult("central_bottleneck", label, 0.9, "2026-07"))
    with pytest.raises(ValueError):
        reg.pin_best("central_bottleneck")


# ── risks ──────────────────────────────────────────────────────────────────────

def test_risk_register_complete():
    risks = all_risks()
    assert len(risks) == 24  # 17 general + 7 innovation
    assert risk("R02").mitigation_component.startswith("egmra.truth")
    with pytest.raises(KeyError):
        risk("R99")
