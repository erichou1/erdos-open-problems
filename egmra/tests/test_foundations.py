"""Tests for provenance hashing, feature policy, and stage identity (foundations)."""

import pytest

from egmra.policy import (
    KNOWN_FEATURES,
    FeaturePolicy,
    PolicyEnforcer,
    PolicyError,
    PolicyViolation,
    load_policy,
    sign_policy,
    verify_signature,
)
from egmra.provenance.hashing import (
    ProvenanceError,
    canonical_json,
    content_id,
    is_sha256,
    merkle_root,
    sha256_hex,
)
from egmra.provenance.stage_identity import (
    AttestedModelIdentity,
    StageIdentity,
    StageIdentityError,
    attest_model_identity,
)


# ── hashing ──────────────────────────────────────────────────────────────────

def test_canonical_json_is_key_order_independent():
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})
    assert content_id({"a": 1, "b": [1, 2]}) == content_id({"b": [1, 2], "a": 1})


def test_canonical_json_rejects_non_finite_and_unsupported():
    with pytest.raises(ProvenanceError):
        canonical_json({"x": float("inf")})
    with pytest.raises(ProvenanceError):
        canonical_json({"x": {1, 2}})  # set is not JSON-compatible


def test_sha256_and_is_sha256():
    digest = sha256_hex("hello")
    assert is_sha256(digest)
    assert not is_sha256("ZZZ")
    assert not is_sha256(digest.upper())


def test_merkle_root_is_order_sensitive():
    a, b = sha256_hex("a"), sha256_hex("b")
    assert merkle_root([a, b]) != merkle_root([b, a])
    assert merkle_root([]) == sha256_hex("")
    assert merkle_root([a]) == a


# ── feature policy ─────────────────────────────────────────────────────────────

POLICY_ENV = {"EGMRA_POLICY_KEY": "policy-test-key-that-is-at-least-32-bytes"}


def _enforcer(flags):
    return PolicyEnforcer(sign_policy(flags, env=POLICY_ENV), verification_env=POLICY_ENV)

def test_policy_rejects_unknown_flags():
    with pytest.raises(PolicyError):
        FeaturePolicy(flags={"not_a_feature": True})


def test_sign_and_verify_policy_roundtrip():
    env = POLICY_ENV
    policy = sign_policy({"claim_graph": True, "promotion": False}, env=env)
    assert policy.signature_trust == "signed"
    assert verify_signature(policy, env=env)
    # A different key must fail verification.
    assert not verify_signature(policy, env={"EGMRA_POLICY_KEY": "other-key-that-is-at-least-32-bytes"})


def test_policy_hash_is_stable_across_flag_order():
    p1 = FeaturePolicy(flags={"claim_graph": True, "promotion": False})
    p2 = FeaturePolicy(flags={"promotion": False, "claim_graph": True})
    assert p1.policy_hash == p2.policy_hash


def test_unsigned_default_policy_fails_closed():
    with pytest.raises(PolicyError):
        load_policy(
            __import__("egmra.policy", fromlist=["default_policy_path"]).default_policy_path()
        )


def test_enforcer_blocks_disabled_feature_and_records_check():
    enforcer = _enforcer({"promotion": False, "claim_graph": True})
    policy = enforcer.policy
    enforcer.require("claim_graph", entry_point="truth.graph")
    with pytest.raises(PolicyViolation):
        enforcer.require("promotion", entry_point="release.promote")
    # Both checks are recorded with the policy hash.
    assert len(enforcer.checks) == 2
    assert all(c["policy_hash"] == policy.policy_hash for c in enforcer.checks)
    assert enforcer.checks[0]["allowed"] is True
    assert enforcer.checks[1]["allowed"] is False


def test_promotion_override_is_refused_because_non_overridable():
    enforcer = _enforcer({"promotion": False})
    # Even an explicit override cannot enable a non-overridable release feature.
    with pytest.raises(PolicyViolation):
        enforcer.require("promotion", entry_point="release.promote", override=True)


def test_overridable_feature_allows_recorded_override():
    enforcer = _enforcer({"continuous_scheduler": False})
    enforcer.require("continuous_scheduler", entry_point="scheduler", override=True)
    assert enforcer.checks[-1]["override"] is True
    assert enforcer.checks[-1]["allowed"] is True


def test_all_known_features_are_boolean_defaultable():
    policy = FeaturePolicy(flags={f: False for f in KNOWN_FEATURES})
    for feature in KNOWN_FEATURES:
        assert policy.enabled(feature) is False


# ── stage identity ─────────────────────────────────────────────────────────────

def _identity(**kw) -> AttestedModelIdentity:
    base = dict(provider="openai", model="o-research", version="2026-01")
    base.update(kw)
    return attest_model_identity(**base)


def test_attested_identity_requires_version():
    with pytest.raises(StageIdentityError):
        attest_model_identity(provider="p", model="m")
    # unattested label does not need a version
    AttestedModelIdentity(provider="p", model="ChatGPT")


def test_independence_requires_two_attested_different_models():
    a = _identity(model="model-a")
    b = _identity(model="model-b")
    same = _identity(model="model-a")
    label = AttestedModelIdentity(provider="openai", model="ChatGPT")
    assert a.independent_of(b)
    assert not a.independent_of(same)          # same model is not independence
    assert not a.independent_of(label)         # unattested label never independent
    assert not label.independent_of(label)


def test_stage_cache_key_changes_with_runner_or_model():
    m1, m2 = _identity(model="a"), _identity(model="b")
    s1 = StageIdentity(stage="adjudicate", runner_id="r1", model=m1,
                       prompt_hash=sha256_hex("p"))
    s2 = StageIdentity(stage="adjudicate", runner_id="r1", model=m2,
                       prompt_hash=sha256_hex("p"))
    s3 = StageIdentity(stage="adjudicate", runner_id="r2", model=m1,
                       prompt_hash=sha256_hex("p"))
    assert not s1.compatible_with(s2)          # different model
    assert not s1.compatible_with(s3)          # different runner
    assert s1.compatible_with(
        StageIdentity(stage="adjudicate", runner_id="r1", model=_identity(model="a"),
                      prompt_hash=sha256_hex("p"))
    )


def test_changing_any_bound_policy_invalidates_cache():
    m = _identity()
    base = dict(stage="review", runner_id="r1", model=m, prompt_hash=sha256_hex("p"))
    s = StageIdentity(**base)
    for field_name, value in [
        ("literature_packet_hash", sha256_hex("packet-v2")),
        ("adjudicator_policy_hash", sha256_hex("adj-v2")),
        ("feature_policy_hash", sha256_hex("pol-v2")),
        ("import_closure_hash", sha256_hex("imp-v2")),
        ("validator_version", "val-v2"),
        ("formal_env_hash", sha256_hex("lean-v2")),
    ]:
        changed = StageIdentity(**{**base, field_name: value})
        assert not s.compatible_with(changed), field_name
        assert any(field_name in r for r in s.incompatibility_reasons(changed))


def test_context_id_and_artifacts_affect_cache_key():
    m = _identity()
    base = dict(stage="scout", runner_id="r1", model=m)
    s1 = StageIdentity(**base, context_id="ctx-1", artifacts=(sha256_hex("a"),))
    s2 = StageIdentity(**base, context_id="ctx-2", artifacts=(sha256_hex("b"),))
    assert not s1.compatible_with(s2)


# ── provenance rules (§10.5) ────────────────────────────────────────────────────

def test_provenance_rules_require_fields():
    from egmra.provenance import check_provenance, hidden_reasoning_is_provenance, is_auditable
    incomplete = check_provenance("imported_claim", {"source_uri": "u"})
    assert not incomplete.complete and "verbatim_extract" in incomplete.missing
    complete = check_provenance("human_review", {"scope": "sec 3", "conflicts_of_interest": "none"})
    assert complete.complete
    # model-hidden reasoning is never provenance
    assert hidden_reasoning_is_provenance() is False
    assert is_auditable({"content_hash": "abc"})
    assert not is_auditable({"scratchpad": "thoughts"})
