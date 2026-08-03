"""Promotion policy: kernel + intent + correspondence + feature policy (spec §9.1, §16 P0).

Promotion is disabled until every evidence kind has a validator (the truth plane)
AND the signed feature policy enables it. Formal promotion additionally requires a
clean kernel replay, an approved intent certificate, and an approved
formal-correspondence certificate. These release features are non-overridable.
"""

from __future__ import annotations

import calendar
import hmac
import os
import time
from dataclasses import dataclass
from typing import Any

from egmra.policy import PolicyEnforcer, PolicyViolation
from egmra.provenance.hashing import canonical_json, is_sha256, sha256_bytes
from egmra.release.gates import FiveGateResult
from egmra.truth.events import EventLog

_MIN_PROMOTION_KEY_BYTES = 32
_RELEASE_KINDS = frozenset({"resolution", "scoped_result", "encoded_theorem", "triage"})


class PromotionSecurityError(ValueError):
    """Promotion authorization is missing, forged, stale, or misbound."""


def _utc_now(timestamp: float | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(timestamp))


def _parse_utc(value: str) -> float:
    try:
        return float(calendar.timegm(time.strptime(value, "%Y-%m-%dT%H:%M:%SZ")))
    except (TypeError, ValueError, OverflowError) as exc:
        raise PromotionSecurityError("invalid UTC promotion timestamp") from exc


def _promotion_key(env: dict[str, str] | None = None) -> bytes:
    values = env if env is not None else dict(os.environ)
    key = values.get("EGMRA_PROMOTION_KEY", "").strip().encode("utf-8")
    if len(key) < _MIN_PROMOTION_KEY_BYTES:
        raise PromotionSecurityError(
            f"EGMRA_PROMOTION_KEY must contain at least {_MIN_PROMOTION_KEY_BYTES} bytes"
        )
    return key


@dataclass(frozen=True)
class PromotionDecision:
    promoted: bool
    reasons: tuple[str, ...]
    gate_digest: str = ""
    subject_hash: str = ""
    policy_hash: str = ""
    informal_only: bool = False
    release_kind: str = "resolution"
    authorized_at: str = ""
    expires_at: str = ""
    authorizer_id: str = ""
    key_fingerprint: str = ""
    authorization_signature: str = ""

    def to_dict(self) -> dict:
        out = dict(self.__dict__)
        out["reasons"] = list(self.reasons)
        return out

    def authorization_record(self) -> dict[str, Any]:
        record = self.to_dict()
        record.pop("authorization_signature", None)
        return record

    def verify_authorization(
        self, *, gates: FiveGateResult, subject_hash: str,
        env: dict[str, str] | None = None, now: float | None = None,
        event_log: EventLog | None = None,
    ) -> bool:
        try:
            key = _promotion_key(env)
            authorized = _parse_utc(self.authorized_at)
            expires = _parse_utc(self.expires_at)
        except PromotionSecurityError:
            return False
        current = time.time() if now is None else float(now)
        expected = hmac.new(
            key, canonical_json(self.authorization_record()).encode("utf-8"), "sha256"
        ).hexdigest()
        return bool(
            self.promoted
            and not self.reasons
            and self.authorization_signature
            and is_sha256(subject_hash)
            and self.subject_hash == subject_hash
            and self.gate_digest == gates.gate_digest
            and is_sha256(self.policy_hash)
            and self.release_kind in _RELEASE_KINDS
            and self.authorizer_id
            and self.key_fingerprint == sha256_bytes(key)
            and authorized - 5.0 <= current <= expires
            and gates.verify_attestation(env=env, now=current, event_log=event_log)
            and hmac.compare_digest(expected, self.authorization_signature)
        )


class PromotionPolicy:
    def decide(
        self, gates: FiveGateResult, *, enforcer: PolicyEnforcer, informal_only: bool,
        entry_point: str = "release.promote",
        release_kind: str = "resolution",
        env: dict[str, str] | None = None,
        now: float | None = None,
        event_log: EventLog | None = None,
    ) -> PromotionDecision:
        reasons: list[str] = []

        if release_kind not in _RELEASE_KINDS:
            return PromotionDecision(False, (f"unknown release kind {release_kind!r}",))

        # 1. feature policy must enable promotion (non-overridable release feature)
        try:
            enforcer.require("promotion", entry_point=entry_point)
            if not informal_only:
                enforcer.require("formal_promotion", entry_point=entry_point)
        except PolicyViolation as exc:
            return PromotionDecision(False, (f"feature policy blocks promotion: {exc}",))

        # Gate strings are not authority.  Promotion consumes only a fresh gate
        # attestation bound to the evidence record.
        if not gates.verify_attestation(env=env, now=now, event_log=event_log):
            reasons.append("gate profile is unsigned, forged, or stale")

        if release_kind == "triage":
            if gates.summary_label() != "honest_no_result":
                reasons.append("triage authorization cannot carry a positive result label")
            return PromotionDecision(not reasons, tuple(reasons), release_kind=release_kind)

        # 2. intent fidelity approved
        if gates.intent != "I2":
            reasons.append("intent fidelity not approved (need I2)")

        # 3. truth tier sufficient
        if release_kind == "scoped_result":
            if gates.truth not in ("T1", "T2"):
                reasons.append("scoped result promotion needs T1/T2 scoped evidence")
            if gates.formal_correspondence != "N/A":
                reasons.append("scoped informal result must have formal_correspondence N/A")
        elif release_kind == "encoded_theorem":
            if gates.truth not in ("T4", "T5"):
                reasons.append("encoded theorem promotion needs T4/T5")
            if gates.formal_correspondence not in ("F1", "F2"):
                reasons.append("encoded theorem needs reviewed formal correspondence")
        elif informal_only:
            if gates.truth != "T3":
                reasons.append("informal promotion needs T3 (rigorous informal result)")
            if gates.formal_correspondence != "N/A":
                reasons.append("informal-only result must have formal_correspondence N/A")
        else:
            # T4 labels the exact encoding only; publication as an intended
            # formal resolution requires hardened T5 plus F2.
            if gates.truth != "T5":
                reasons.append("formal resolution promotion needs hardened T5")
            if gates.formal_correspondence != "F2":
                reasons.append("formal promotion needs an approved correspondence certificate (F2)")

        # 4. a current status decision is always required (novelty must be resolved
        #    to at least N1 or 'known'; N0 blocks a *resolution* claim)
        if gates.novelty == "N0":
            reasons.append("novelty/status unresolved (N0) — cannot claim a resolution")

        if gates.significance == "S0":
            reasons.append("significance/responsiveness unresolved (S0)")
        if gates.reproducibility == "R0":
            reasons.append("result has not been replayed (R0)")

        return PromotionDecision(not reasons, tuple(reasons), release_kind=release_kind)

    def authorize(
        self, gates: FiveGateResult, *, subject_hash: str, enforcer: PolicyEnforcer,
        informal_only: bool, release_kind: str = "resolution",
        entry_point: str = "release.authorize", env: dict[str, str] | None = None,
        now: float | None = None, ttl_s: float = 300.0,
        authorizer_id: str = "egmra-release-auditor",
        event_log: EventLog | None = None,
    ) -> PromotionDecision:
        """Return a short-lived, subject-bound authorization after all gates pass."""
        if not is_sha256(subject_hash):
            raise PromotionSecurityError("release subject_hash must be a SHA-256 digest")
        current = time.time() if now is None else float(now)
        decision = self.decide(
            gates,
            enforcer=enforcer,
            informal_only=informal_only,
            entry_point=entry_point,
            release_kind=release_kind,
            env=env,
            now=current,
            event_log=event_log,
        )
        if not decision.promoted:
            return decision
        key = _promotion_key(env)
        authorized = PromotionDecision(
            promoted=True,
            reasons=(),
            gate_digest=gates.gate_digest,
            subject_hash=subject_hash,
            policy_hash=enforcer.policy.policy_hash,
            informal_only=informal_only,
            release_kind=release_kind,
            authorized_at=_utc_now(current),
            expires_at=_utc_now(current + float(ttl_s)),
            authorizer_id=authorizer_id,
            key_fingerprint=sha256_bytes(key),
        )
        signature = hmac.new(
            key, canonical_json(authorized.authorization_record()).encode("utf-8"), "sha256"
        ).hexdigest()
        return PromotionDecision(
            **(authorized.__dict__ | {"authorization_signature": signature})
        )
