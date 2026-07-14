"""Adversarial provenance/configuration tests missing from the original suite."""

import json

import pytest

from egmra.config import EgmraConfig
from egmra.provenance.hashing import sha256_hex
from egmra.provenance.stage_identity import (
    AttestedModelIdentity,
    StageIdentity,
    StageIdentityError,
    attest_model_identity,
)


def _model():
    return attest_model_identity(
        provider="local", model="fixture", version="v1"
    )


def _stage(**changes):
    values = {
        "stage": "review",
        "runner_id": "runner-v1",
        "model": _model(),
        "prompt_hash": sha256_hex("prompt"),
        "adjudicator_policy_hash": sha256_hex("adjudicator"),
        "literature_packet_hash": sha256_hex("packet"),
        "formal_env_hash": sha256_hex("formal-env"),
        "validator_version": "validator-v1",
        "toolset_hash": sha256_hex("tools"),
        "import_closure_hash": sha256_hex("imports"),
        "feature_policy_hash": sha256_hex("features"),
        "run_contract_id": sha256_hex("contract"),
        "context_id": "context-1",
        "artifacts": (sha256_hex("artifact-1"),),
    }
    values.update(changes)
    return StageIdentity(**values)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("context_id", "context-2"),
        ("artifacts", (sha256_hex("artifact-2"),)),
        ("cache_schema_version", 4),
    ],
)
def test_cache_identity_includes_context_artifacts_and_schema(field, value):
    assert not _stage().compatible_with(_stage(**{field: value}))


@pytest.mark.parametrize(
    "field",
    [
        "prompt_hash", "adjudicator_policy_hash", "literature_packet_hash",
        "formal_env_hash", "toolset_hash", "import_closure_hash",
        "feature_policy_hash", "run_contract_id",
    ],
)
def test_stage_identity_rejects_fake_digest_fields(field):
    with pytest.raises(StageIdentityError, match=field):
        _stage(**{field: "not-a-sha256"})


def test_stage_identity_rejects_forged_attestation_and_duplicate_artifacts():
    forged = AttestedModelIdentity(
        provider="local", model="fixture", version="v1", attestation="0" * 64
    )
    assert forged.attested is False
    digest = sha256_hex("same")
    with pytest.raises(StageIdentityError, match="duplicate"):
        _stage(artifacts=(digest, digest))


def test_caller_version_label_is_not_attested_without_authenticated_envelope():
    label = AttestedModelIdentity(provider="local", model="fixture", version="v1")
    issued = attest_model_identity(provider="local", model="fixture", version="v1")
    assert label.attested is False
    assert issued.attested is True
    assert not label.independent_of(issued)


def test_config_rejects_missing_explicit_file_unknown_keys_and_duplicates(tmp_path):
    with pytest.raises(FileNotFoundError):
        EgmraConfig.load(tmp_path / "missing.json")
    unknown = tmp_path / "unknown.json"
    unknown.write_text(json.dumps({"not_a_setting": True}), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown configuration"):
        EgmraConfig.load(unknown)
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"oeis_offline": true, "oeis_offline": false}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        EgmraConfig.load(duplicate)


@pytest.mark.parametrize(
    "document",
    [
        {"openai_api_key": "secret"},
        {"nested": {"EGMRA_EVENT_KEY": "secret"}},
        {"api_keys": {"anthropic_api_key": "secret"}},
    ],
)
def test_config_rejects_nested_or_case_changed_secrets(tmp_path, document):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError, match="secret"):
        EgmraConfig.load(path)


def test_config_secret_reader_is_allowlisted():
    with pytest.raises(ValueError, match="not an allowlisted secret"):
        EgmraConfig.secret("HOME", env={"HOME": "/private"})


@pytest.mark.parametrize(
    "env",
    [
        {"EGMRA_PROTECTED_EXPLORATION_FRACTION": "nan"},
        {"EGMRA_PROTECTED_EXPLORATION_FRACTION": "1.1"},
        {"EGMRA_MAX_BACKOFF_SECONDS": "121"},
        {"EGMRA_OEIS_OFFLINE": "perhaps"},
    ],
)
def test_config_rejects_invalid_or_unsafe_values(env):
    with pytest.raises(ValueError):
        EgmraConfig.load(env=env)
