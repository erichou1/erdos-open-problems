"""Per-stage execution identity and cache compatibility (spec §1, §4.2, §16 P0).

The current pipeline's stage cache does not bind the *actual* per-stage runner,
adjudicator, literature policy, formal environment, or validator, which lets a
resumed campaign reuse a same-model cached adjudication after switching models
and then report a distinct adjudicator. This module makes the binding complete
and makes incompatible cache replay impossible.

A caller-supplied model name (e.g. "ChatGPT 5.6") is an *unattested label*, not a
model identity. Only a provider-attested immutable model/version counts toward
independent-model evidence.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass, field
from typing import Any

from egmra.provenance.hashing import canonical_json, content_id, is_sha256


class StageIdentityError(ValueError):
    """Raised when a stage identity is incomplete or inconsistent."""


@dataclass(frozen=True)
class AttestedModelIdentity:
    """Identity of the model that actually produced a stage's output.

    ``attested`` is True only when the provider returned an immutable
    model/version/build id. A UI label such as "ChatGPT" is carried with
    ``attested=False`` and can never be counted as independent-model evidence.
    """

    provider: str
    model: str
    version: str = ""
    build_id: str = ""
    ui_surface: str = ""
    account_class: str = ""
    attestation: str = ""

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.model.strip():
            raise StageIdentityError("provider and model are required")
        if self.attestation and not (self.version.strip() or self.build_id.strip()):
            raise StageIdentityError(
                "an attested identity must carry a version or build id"
            )
        if self.attestation and not is_sha256(self.attestation):
            raise StageIdentityError("model attestation must be a lowercase HMAC-SHA256")

    @property
    def attested(self) -> bool:
        """Whether a trusted adapter authenticated this exact immutable identity."""
        return verify_model_attestation(self)

    @property
    def label(self) -> str:
        return f"{self.provider}:{self.model}:{self.version or self.build_id or 'unversioned'}"

    def identity_key(self) -> dict[str, Any]:
        return {
            "provider": self.provider.strip(),
            "model": self.model.strip(),
            "version": self.version.strip(),
            "build_id": self.build_id.strip(),
            "ui_surface": self.ui_surface.strip(),
            "account_class": self.account_class.strip(),
            "attestation": self.attestation,
            "attested": self.attested,
        }

    def independent_of(self, other: "AttestedModelIdentity") -> bool:
        """True only if both are attested and differ in provider or model lineage.

        Fresh conversation IDs or the same model twice are *not* independence.
        Two unattested labels are never independent evidence.
        """
        if not (self.attested and other.attested):
            return False
        return (self.provider, self.model) != (other.provider, other.model)


def attest_model_identity(
    *,
    provider: str,
    model: str,
    version: str = "",
    build_id: str = "",
    ui_surface: str = "",
    account_class: str = "",
    env: dict[str, str] | None = None,
) -> AttestedModelIdentity:
    """Issue a local trust-boundary attestation after a provider adapter validates a response.

    This does not prove that an arbitrary callback contacted a provider.  It prevents
    downstream code and workers from converting caller labels into independence by
    setting a boolean.  Deployment must keep the signing key outside worker sandboxes.
    """
    if not (version.strip() or build_id.strip()):
        raise StageIdentityError("an attested identity needs a version or build id")
    payload = _model_attestation_payload(
        provider, model, version, build_id, ui_surface, account_class
    )
    signature = hmac.new(
        _model_attestation_key(env), canonical_json(payload).encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return AttestedModelIdentity(
        provider=provider,
        model=model,
        version=version,
        build_id=build_id,
        ui_surface=ui_surface,
        account_class=account_class,
        attestation=signature,
    )


def verify_model_attestation(
    identity: AttestedModelIdentity, *, env: dict[str, str] | None = None
) -> bool:
    if not identity.attestation or not (identity.version.strip() or identity.build_id.strip()):
        return False
    try:
        key = _model_attestation_key(env)
    except StageIdentityError:
        return False
    payload = _model_attestation_payload(
        identity.provider,
        identity.model,
        identity.version,
        identity.build_id,
        identity.ui_surface,
        identity.account_class,
    )
    expected = hmac.new(
        key, canonical_json(payload).encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, identity.attestation)


def _model_attestation_payload(
    provider: str,
    model: str,
    version: str,
    build_id: str,
    ui_surface: str,
    account_class: str,
) -> dict[str, str]:
    if not provider.strip() or not model.strip():
        raise StageIdentityError("provider and model are required")
    return {
        "provider": provider.strip(),
        "model": model.strip(),
        "version": version.strip(),
        "build_id": build_id.strip(),
        "ui_surface": ui_surface.strip(),
        "account_class": account_class.strip(),
    }


def _model_attestation_key(env: dict[str, str] | None) -> bytes:
    source = os.environ if env is None else env
    raw = source.get("EGMRA_MODEL_ATTESTATION_KEY", "")
    if len(raw.encode("utf-8")) < 32:
        raise StageIdentityError(
            "EGMRA_MODEL_ATTESTATION_KEY must be configured with at least 32 bytes"
        )
    return raw.encode("utf-8")


# The set of policy/environment identities that any stage may bind. All are
# optional except ``stage``, ``runner_id`` and ``model``; a stage records only
# the identities that actually influenced it, but every recorded identity is
# hashed into the cache key so a change invalidates reuse.
_BINDING_FIELDS = (
    "prompt_hash",
    "adjudicator_policy_hash",
    "literature_packet_hash",
    "formal_env_hash",
    "validator_version",
    "toolset_hash",
    "import_closure_hash",
    "feature_policy_hash",
    "run_contract_id",
    "cache_schema_version",
)


@dataclass(frozen=True)
class StageIdentity:
    """Everything that makes a stage's cached output safe (or unsafe) to reuse."""

    stage: str
    runner_id: str
    model: AttestedModelIdentity
    prompt_hash: str = ""
    adjudicator_policy_hash: str = ""
    literature_packet_hash: str = ""
    formal_env_hash: str = ""
    validator_version: str = ""
    toolset_hash: str = ""
    import_closure_hash: str = ""
    feature_policy_hash: str = ""
    run_contract_id: str = ""
    cache_schema_version: int = 3
    # Context and input artifacts influence behavior and therefore bind replay.
    context_id: str = ""
    artifacts: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.stage.strip():
            raise StageIdentityError("stage is required")
        if not self.runner_id.strip():
            raise StageIdentityError("runner_id is required")
        for name in (
            "prompt_hash", "adjudicator_policy_hash", "literature_packet_hash",
            "formal_env_hash", "toolset_hash", "import_closure_hash",
            "feature_policy_hash", "run_contract_id",
        ):
            value = getattr(self, name)
            if value and not is_sha256(value):
                raise StageIdentityError(f"{name} must be empty or a SHA-256 digest")
        if type(self.cache_schema_version) is not int or self.cache_schema_version <= 0:
            raise StageIdentityError("cache_schema_version must be a positive integer")
        if not isinstance(self.artifacts, tuple):
            raise StageIdentityError("artifacts must be an immutable tuple")
        if any(not is_sha256(value) for value in self.artifacts):
            raise StageIdentityError("artifacts must contain only SHA-256 identities")
        if len(set(self.artifacts)) != len(self.artifacts):
            raise StageIdentityError("duplicate artifact identities are forbidden")

    def binding_key(self) -> dict[str, Any]:
        """The canonical identity that determines cache compatibility."""
        binding = {name: getattr(self, name) for name in _BINDING_FIELDS}
        binding["stage"] = self.stage.strip()
        binding["runner_id"] = self.runner_id.strip()
        binding["model"] = self.model.identity_key()
        binding["context_id"] = self.context_id
        binding["artifacts"] = self.artifacts
        return binding

    def cache_key(self) -> str:
        """Content-addressed cache key binding stage + runner + model + policies."""
        return content_id(self.binding_key())

    def compatible_with(self, other: "StageIdentity") -> bool:
        """True only if ``other``'s cached output is safe to reuse for ``self``.

        Any difference in stage, runner, model identity, prompt, or any bound
        policy/environment fingerprint makes reuse unsafe.
        """
        return self.cache_key() == other.cache_key()

    def incompatibility_reasons(self, other: "StageIdentity") -> list[str]:
        """Human-readable reasons ``other`` cannot be reused for ``self``."""
        reasons: list[str] = []
        mine, theirs = self.binding_key(), other.binding_key()
        for key in sorted(mine):
            if mine[key] != theirs.get(key):
                reasons.append(f"{key} differs")
        return reasons
