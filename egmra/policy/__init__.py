"""Signed feature policy with central enforcement (spec §4.2, §9.1, §16 P0).

The spec requires *one* signed feature policy that every scheduler, verifier,
evidence loader, cache-replay, gate, promotion, and standalone-script entry
point records and checks. This module is that single source of truth.

Signature model: the policy is content-addressed (SHA-256 over canonical JSON of
the schema and flags) and carries an HMAC signature keyed by
``EGMRA_POLICY_KEY``. Missing, short, unsigned, stale-schema, wrong-key, and
caller-mutated policies fail closed. There is deliberately no public development
key: tests provide explicit process-local keys.
"""

from __future__ import annotations

import hmac
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from egmra.provenance.hashing import canonical_json, content_id

POLICY_SCHEMA_VERSION = 1

# The complete set of gated features. Every entry point must declare the feature
# it needs from this set; unknown features fail closed.
KNOWN_FEATURES: frozenset[str] = frozenset(
    {
        # scheduling / execution
        "continuous_scheduler",
        "parallel_workers",
        # evidence & verification
        "lean_execution",
        "external_prover_routing",
        "automated_external_evidence",
        "computation_service",
        # truth plane
        "claim_graph",
        "claim_revocation",
        # release
        "promotion",
        "formal_promotion",
        # retrieval
        "literature_retrieval",
        "oeis_service",
        # learning
        "verified_learning",
    }
)

_MIN_KEY_BYTES = 32


class PolicyViolation(RuntimeError):
    """Raised when a disabled feature is used at an enforced entry point."""


class PolicyError(ValueError):
    """Raised when a policy document is malformed or its signature is invalid."""


@dataclass(frozen=True)
class FeaturePolicy:
    """An immutable, content-addressed, signed feature policy."""

    flags: Mapping[str, bool]
    schema_version: int = POLICY_SCHEMA_VERSION
    signature: str = ""
    signature_trust: str = "local-dev"

    def __post_init__(self) -> None:
        unknown = set(self.flags) - KNOWN_FEATURES
        if unknown:
            raise PolicyError(f"unknown feature flags: {sorted(unknown)}")
        if any(not isinstance(v, bool) for v in self.flags.values()):
            raise PolicyError("feature flag values must be booleans")
        if self.schema_version != POLICY_SCHEMA_VERSION:
            raise PolicyError(
                f"unsupported policy schema {self.schema_version}; expected {POLICY_SCHEMA_VERSION}"
            )
        # A frozen dataclass does not freeze a mutable dict.  Copy and wrap it so a
        # caller cannot change an already-verified policy after enforcement starts.
        object.__setattr__(self, "flags", MappingProxyType(dict(self.flags)))

    @property
    def payload(self) -> dict[str, Any]:
        """The signed portion: schema + sorted flags."""
        return {
            "schema_version": self.schema_version,
            "flags": {k: bool(self.flags[k]) for k in sorted(self.flags)},
        }

    @property
    def policy_hash(self) -> str:
        """Content-addressed identity of the policy payload."""
        return content_id(self.payload)

    def enabled(self, feature: str) -> bool:
        if feature not in KNOWN_FEATURES:
            raise PolicyError(f"unknown feature flag: {feature}")
        return bool(self.flags.get(feature, False))

    def to_document(self) -> dict[str, Any]:
        return {
            **self.payload,
            "policy_hash": self.policy_hash,
            "signature": self.signature,
            "signature_trust": self.signature_trust,
        }


def _sign(payload: dict[str, Any], key: bytes) -> str:
    return hmac.new(key, canonical_json(payload).encode("utf-8"), "sha256").hexdigest()


def _resolve_key(env: dict[str, str] | None = None) -> tuple[bytes, str]:
    env = env if env is not None else dict(os.environ)
    raw = env.get("EGMRA_POLICY_KEY", "").strip()
    if not raw:
        raise PolicyError("EGMRA_POLICY_KEY is required to sign or verify feature policy")
    key = raw.encode("utf-8")
    if len(key) < _MIN_KEY_BYTES:
        raise PolicyError(f"EGMRA_POLICY_KEY must contain at least {_MIN_KEY_BYTES} bytes")
    return key, "signed"


def sign_policy(flags: dict[str, bool], *, env: dict[str, str] | None = None) -> FeaturePolicy:
    """Build a signed policy from a flag mapping."""
    policy = FeaturePolicy(flags=dict(flags))
    key, trust = _resolve_key(env)
    signature = _sign(policy.payload, key)
    return FeaturePolicy(
        flags=dict(policy.flags),
        schema_version=policy.schema_version,
        signature=signature,
        signature_trust=trust,
    )


def verify_signature(policy: FeaturePolicy, *, env: dict[str, str] | None = None) -> bool:
    """True if the policy signature matches under the resolved key."""
    if not policy.signature:
        return False
    key, trust = _resolve_key(env)
    if policy.signature_trust != trust:
        return False
    expected = _sign(policy.payload, key)
    return hmac.compare_digest(expected, policy.signature)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise PolicyError(f"duplicate policy key: {key}")
        out[key] = value
    return out


def load_policy(path: str | Path, *, env: dict[str, str] | None = None) -> FeaturePolicy:
    """Load and validate a policy document from disk.

    Unsigned and legacy bare-flag documents fail closed.  Migration is an
    explicit administrative operation through :func:`sign_policy`; loading must
    never silently turn attacker-controlled bytes into an authenticated policy.
    """
    try:
        doc = json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError(f"cannot load feature policy: {exc}") from exc
    if not isinstance(doc, dict):
        raise PolicyError("policy document must be a JSON object")

    if "flags" not in doc:
        raise PolicyError("unsigned legacy policy is not accepted; sign it explicitly")
    flags = doc["flags"]
    if not isinstance(flags, dict):
        raise PolicyError("policy 'flags' must be an object")
    schema_version = doc.get("schema_version", POLICY_SCHEMA_VERSION)
    if not isinstance(schema_version, int):
        raise PolicyError("policy schema_version must be an integer")
    policy = FeaturePolicy(
        flags=flags,
        schema_version=schema_version,
        signature=str(doc.get("signature", "")),
        signature_trust=str(doc.get("signature_trust", "")),
    )
    if not policy.signature:
        raise PolicyError("feature policy is unsigned")
    if doc.get("policy_hash", policy.policy_hash) != policy.policy_hash:
        raise PolicyError("feature policy hash does not match its signed payload")
    if not verify_signature(policy, env=env):
        raise PolicyError("policy signature does not verify under the current key")
    return policy


@dataclass
class PolicyEnforcer:
    """Central checker: every gated entry point calls :meth:`require`.

    Each check is recorded so an audit can prove that a given policy hash was in
    force at each entry point (spec §16 P0.1).
    """

    policy: FeaturePolicy
    verification_env: dict[str, str] | None = field(default=None, repr=False)
    checks: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.policy.signature:
            raise PolicyError("PolicyEnforcer requires a signed feature policy")
        if not verify_signature(self.policy, env=self.verification_env):
            raise PolicyError("PolicyEnforcer received an invalid or wrong-key policy")

    def require(self, feature: str, *, entry_point: str, override: bool = False) -> None:
        """Allow the entry point to proceed only if ``feature`` is enabled.

        ``override`` is an explicit, recorded experimental bypass. It never
        applies to the non-overridable release features below.
        """
        if feature not in KNOWN_FEATURES:
            raise PolicyError(f"unknown feature flag: {feature}")
        enabled = self.policy.enabled(feature)
        non_overridable = feature in {"promotion", "formal_promotion"}
        allowed = enabled or (override and not non_overridable)
        self.checks.append(
            {
                "entry_point": entry_point,
                "feature": feature,
                "policy_hash": self.policy.policy_hash,
                "enabled": enabled,
                "override": bool(override),
                "allowed": allowed,
            }
        )
        if not allowed:
            reason = (
                "non-overridable release feature is disabled"
                if non_overridable
                else "feature is disabled and no override was given"
            )
            raise PolicyViolation(
                f"entry point '{entry_point}' requires feature '{feature}': {reason} "
                f"(policy {self.policy.policy_hash[:12]})"
            )

    def audit_hash(self) -> str:
        """Content id over the recorded checks — bindable into an event."""
        return content_id(self.checks)


def default_policy_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "config" / "egmra_policy.json"
