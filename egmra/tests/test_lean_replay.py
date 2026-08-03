"""Tests for the Lean replay → sealed attestation bridge (task B1)."""

from __future__ import annotations

import hmac
import io
import zipfile

import pytest

from egmra.lean.aristotle_api import AristotleApiClient
from egmra.lean.replay import LeanReplayTarget, LeanReplayVerifier
from egmra.lean.service import (
    CheckerAttestation,
    CheckerRequest,
    LeanEnvironment,
    _checker_key,
)
from egmra.provenance.hashing import canonical_json, sha256_bytes, sha256_hex

_ENV = LeanEnvironment(lean_version="4.9.0", mathlib_commit="deadbeefcafe",
                       project_hash=sha256_hex("project"))
_TARGET = LeanReplayTarget(
    claim_id="goal",
    declaration_name="egmra_target",
    normalized_target_hash=sha256_hex("normalized-target"),
    expected_type_hash=sha256_hex("expected-type"),
    immutable_target_module_hash=sha256_hex("target-module"),
    trust_policy_hash=sha256_hex("trust-policy"),
)


def _sign(attestation: CheckerAttestation) -> CheckerAttestation:
    key = _checker_key(None)
    sig = hmac.new(key, canonical_json(attestation.signed_record()).encode("utf-8"),
                   "sha256").hexdigest()
    return CheckerAttestation(**(attestation.__dict__ | {"signature": sig}))


def _valid_attestation(request: CheckerRequest, *, axioms=("propext",),
                       candidate_type_hash=None) -> CheckerAttestation:
    """A correctly-signed, kernel-verified attestation bound to the request."""
    key = _checker_key(None)
    att = CheckerAttestation(
        environment_id=request.environment_id,
        source_hash=request.source_hash,
        declaration_name=request.declaration_name,
        expected_type_hash=request.expected_type_hash,
        candidate_type_hash=candidate_type_hash or request.expected_type_hash,
        candidate_declaration_hash=sha256_hex("candidate-decl"),
        proof_term_hash=sha256_hex("proof-term"),
        immutable_target_module_hash=request.immutable_target_module_hash,
        trust_policy_hash=request.trust_policy_hash,
        source_tree_hash=sha256_hex("source-tree"),
        imports_hash=sha256_hex("imports"),
        checker_id="local-kernel", checker_version="1", checker_trust_base="lean4-kernel",
        checker_binary_hash=sha256_hex("binary"), checker_log_hash=sha256_hex("log"),
        transitive_axioms=tuple(axioms), placeholder_findings=(), unsafe_findings=(),
        imports_audited=True, axiom_closure_verified=True, immutable_target_isolated=True,
        clean_replay=True, network_disabled=True, kernel_verified=True, production=True,
        issued_at="2026-07-13T00:00:00Z", key_fingerprint=sha256_bytes(key),
    )
    return _sign(att)


class _Checker:
    def __init__(self, factory):
        self._factory = factory

    def run(self, request: CheckerRequest) -> CheckerAttestation:
        return self._factory(request)


def _client_with_artifact(tmp_path):
    class T:
        def submit(self, p): return "job-1"
        def poll(self, j): return {"status": "solved"}
        def download(self, j):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as z:
                z.writestr("Target.lean", "theorem egmra_target : True := trivial")
            return buf.getvalue()
    client = AristotleApiClient(transport=T(), quarantine_root=tmp_path)
    return client, client.download("job-1", vendor_status="solved")


def test_real_replay_seals_attestation_and_promotes(tmp_path):
    client, artifact = _client_with_artifact(tmp_path)
    verifier = LeanReplayVerifier(checker=_Checker(_valid_attestation),
                                  environment=_ENV, target=_TARGET)
    result = client.bind_local_replay(artifact, verifier, expected_claim_id="goal")
    assert result.verified is True and result.promotable is True
    assert result.attestation is not None
    # The sealed attestation is bound to the exact quarantined tree.
    assert result.attestation.artifact_hash == client.artifact_hash(artifact)


def test_failed_kernel_replay_is_rejected(tmp_path):
    client, artifact = _client_with_artifact(tmp_path)

    def _raise(_request):
        raise RuntimeError("lake build failed")

    result = client.bind_local_replay(artifact, LeanReplayVerifier(
        checker=_Checker(_raise), environment=_ENV, target=_TARGET))
    assert result.verified is False and result.promotable is False


def test_proof_of_a_different_type_is_rejected(tmp_path):
    # candidate_type_hash != expected_type_hash → verify_for fails → no promotion.
    client, artifact = _client_with_artifact(tmp_path)
    factory = lambda req: _valid_attestation(req, candidate_type_hash="9" * 64)  # noqa: E731
    result = client.bind_local_replay(artifact, LeanReplayVerifier(
        checker=_Checker(factory), environment=_ENV, target=_TARGET))
    assert result.verified is False


def test_axiom_whitelist_violation_is_rejected(tmp_path):
    client, artifact = _client_with_artifact(tmp_path)
    factory = lambda req: _valid_attestation(req, axioms=("propext", "sorryAx"))  # noqa: E731
    result = client.bind_local_replay(artifact, LeanReplayVerifier(
        checker=_Checker(factory), environment=_ENV, target=_TARGET))
    assert result.verified is False


def test_forged_checker_signature_is_rejected(tmp_path):
    client, artifact = _client_with_artifact(tmp_path)

    def _forged(request):
        att = _valid_attestation(request)
        return CheckerAttestation(**(att.__dict__ | {"signature": "0" * 64}))

    result = client.bind_local_replay(artifact, LeanReplayVerifier(
        checker=_Checker(_forged), environment=_ENV, target=_TARGET))
    assert result.verified is False


def test_wrong_expected_claim_id_is_rejected(tmp_path):
    client, artifact = _client_with_artifact(tmp_path)
    verifier = LeanReplayVerifier(checker=_Checker(_valid_attestation),
                                  environment=_ENV, target=_TARGET)
    result = client.bind_local_replay(artifact, verifier, expected_claim_id="different-claim")
    assert result.verified is False
