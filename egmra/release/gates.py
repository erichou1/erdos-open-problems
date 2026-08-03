"""Five independent release gates (spec §1, §11.3, §11.5).

Truth, target correspondence, novelty, significance, and reproducibility are
decided *separately*. A result may be "formally proved but novelty unresolved" or
"rigorous informal partial progress" without being called solved. No single
positive verdict substitutes for another.
"""

from __future__ import annotations

import calendar
import hmac
import os
import time
from dataclasses import dataclass
from typing import Any, Mapping

from egmra.compute.artifact import ReplayReport
from egmra.lean.correspondence import verify_formal_correspondence_certificate
from egmra.intake.review import verify_intent_certificate
from egmra.provenance.hashing import canonical_json, content_id, is_sha256, sha256_bytes
from egmra.truth.entities import (
    EvidenceProfile,
    ExactComputation,
    ExternalImport,
    FormalCorrespondenceCertificate,
    FormalVerification,
    InformalReview,
    IntentCertificate,
    NumericalEvidence,
    Verdict,
)
from egmra.truth.events import EventLog
from egmra.truth.snapshots import TruthSnapshot
from egmra.verification.standards import truth_level

_MIN_GATE_KEY_BYTES = 32
_INTENT_METHODS = frozenset(
    {"independent_parse", "examples", "anti_examples", "paraphrase", "local_mutation"}
)
_CORRESPONDENCE_METHODS = frozenset(
    {"backtranslation", "examples", "anti_examples", "paraphrase", "local_mutation"}
)


class GateSecurityError(ValueError):
    """A gate record is malformed, unsigned, forged, or stale."""


def _utc_now(timestamp: float | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(timestamp))


def _parse_utc(value: str) -> float:
    try:
        return float(calendar.timegm(time.strptime(value, "%Y-%m-%dT%H:%M:%SZ")))
    except (TypeError, ValueError, OverflowError) as exc:
        raise GateSecurityError("timestamp must be UTC YYYY-MM-DDTHH:MM:SSZ") from exc


def _gate_key(env: dict[str, str] | None = None) -> bytes:
    values = env if env is not None else dict(os.environ)
    key = values.get("EGMRA_GATE_KEY", "").strip().encode("utf-8")
    if len(key) < _MIN_GATE_KEY_BYTES:
        raise GateSecurityError(
            f"EGMRA_GATE_KEY must contain at least {_MIN_GATE_KEY_BYTES} bytes"
        )
    return key


def _profile_from_snapshot(snapshot: TruthSnapshot) -> EvidenceProfile:
    try:
        doc = snapshot.evidence_profile
        if not isinstance(doc, dict):
            raise TypeError("profile is not an object")
        return EvidenceProfile(
            numerical=NumericalEvidence(doc.get("numerical", "NONE")),
            exact_computation=ExactComputation(doc.get("exact_computation", "NONE")),
            informal_review=InformalReview(doc.get("informal_review", "NONE")),
            formal_verification=FormalVerification(doc.get("formal_verification", "NONE")),
            external_import=ExternalImport(doc.get("external_import", "NONE")),
            intent_certificate_id=doc.get("intent_certificate_id"),
            formal_correspondence_certificate_id=doc.get(
                "formal_correspondence_certificate_id"
            ),
        )
    except (TypeError, ValueError) as exc:
        raise GateSecurityError("truth snapshot has a malformed evidence profile") from exc


def intent_gate(
    cert: IntentCertificate | None, *, source_bytes_hash: str = "",
    interpretation_hash: str = "", informal_claim_hash: str = "",
    verification_env: Mapping[str, str] | None = None,
) -> str:
    """I0 unresolved | I1 reviewed with caveats | I2 approved certificate."""
    if cert is None:
        return "I0"
    bindings_ok = bool(
        source_bytes_hash
        and interpretation_hash
        and informal_claim_hash
        and all(is_sha256(value) for value in (
            source_bytes_hash, interpretation_hash, informal_claim_hash,
        ))
        and cert.source_bytes_hash == source_bytes_hash
        and cert.interpretation_hash == interpretation_hash
        and cert.informal_claim_hash == informal_claim_hash
        and _INTENT_METHODS.issubset(set(cert.methods))
        and verify_intent_certificate(cert, env=verification_env)
    )
    if cert.verdict == Verdict.APPROVED and bindings_ok:
        return "I2"
    if cert.reviewer_ids:
        return "I1"
    return "I0"


def formal_correspondence_gate(
    cert: FormalCorrespondenceCertificate | None, *, informal_only: bool,
    intent_cert: IntentCertificate | None = None, informal_claim_hash: str = "",
    elaborated_type_hash: str = "", parent_intent_level: str = "I0",
    verification_env: dict[str, str] | None = None,
) -> str:
    """F0 | F1 | F2 | N/A (for an informal-only result)."""
    if informal_only:
        return "N/A"
    if cert is None:
        return "F0"
    bindings_ok = bool(
        intent_cert is not None
        and intent_cert.verdict == Verdict.APPROVED
        and parent_intent_level == "I2"
        and verify_formal_correspondence_certificate(cert, env=verification_env)
        and cert.intent_certificate_id == intent_cert.certificate_id
        and informal_claim_hash
        and cert.informal_claim_hash == informal_claim_hash
        and elaborated_type_hash
        and is_sha256(informal_claim_hash)
        and is_sha256(elaborated_type_hash)
        and cert.elaborated_type_hash == elaborated_type_hash
        and is_sha256(cert.notation_and_definition_map_hash)
        and _CORRESPONDENCE_METHODS.issubset(set(cert.methods))
    )
    if cert.verdict == Verdict.APPROVED and bindings_ok:
        return "F2"
    if verify_formal_correspondence_certificate(cert, env=verification_env):
        return "F1"
    return "F0"


def truth_gate(profile: EvidenceProfile, *, high_value: bool = False,
               dependency_audit_complete: bool = False, hardened: bool = False) -> str:
    # A caller-owned boolean is not a hardening certificate.  T5 is represented
    # only by the independently checked formal-evidence state in the profile.
    return truth_level(profile, high_value=high_value,
                       dependency_audit_complete=dependency_audit_complete, hardened=False)


def novelty_gate(novelty_verdict: str) -> str:
    """N0 unresolved | N1 logged search found none | N2 expert-audited | known."""
    if novelty_verdict in ("N0", "N1", "N2", "known"):
        return novelty_verdict
    return "N0"


def significance_gate(*, responsive: bool, non_vacuous: bool, expert_reviewed: bool) -> str:
    """S0 unresolved | S1 responsive partial/non-vacuous | S2 full + expert review."""
    if responsive and non_vacuous and expert_reviewed:
        return "S2"
    if responsive and non_vacuous:
        return "S1"
    return "S0"


def reproducibility_gate(reports: list[ReplayReport]) -> str:
    """R0 unreplayed | R1 same-environment | R2 independent-environment replay."""
    if not reports:
        return "R0"
    passed = [
        r for r in reports
        if r.replayed
        and r.output_hash_matches
        and r.original_environment_hash
        and r.environment_hash
    ]
    if not passed:
        return "R0"
    return "R2" if any(r.independent_environment for r in passed) else "R1"


@dataclass(frozen=True)
class FiveGateResult:
    truth: str
    intent: str
    formal_correspondence: str
    novelty: str
    significance: str
    reproducibility: str
    evidence_hash: str = ""
    truth_claim_id: str = ""
    truth_claim_hash: str = ""
    truth_run_id: str = ""
    truth_event_count: int = 0
    truth_event_head_id: str = ""
    truth_event_merkle_root: str = ""
    source_bytes_hash: str = ""
    interpretation_hash: str = ""
    informal_claim_hash: str = ""
    intent_certificate_id: str = ""
    formal_correspondence_certificate_id: str = ""
    elaborated_type_hash: str = ""
    issued_at: str = ""
    attestor_id: str = ""
    key_fingerprint: str = ""
    signature: str = ""

    def __post_init__(self) -> None:
        vocabularies = {
            "truth": {"T0", "T1", "T2", "T3", "T4", "T5"},
            "intent": {"I0", "I1", "I2"},
            "formal_correspondence": {"F0", "F1", "F2", "N/A"},
            "novelty": {"N0", "N1", "N2", "known"},
            "significance": {"S0", "S1", "S2"},
            "reproducibility": {"R0", "R1", "R2"},
        }
        for name, allowed in vocabularies.items():
            if getattr(self, name) not in allowed:
                raise GateSecurityError(f"invalid {name} gate value {getattr(self, name)!r}")

    def profile(self) -> dict[str, str]:
        return {
            "truth": self.truth,
            "intent": self.intent,
            "formal_correspondence": self.formal_correspondence,
            "novelty": self.novelty,
            "significance": self.significance,
            "reproducibility": self.reproducibility,
        }

    def is_novel_autonomous_resolution(self) -> bool:
        """The strongest claim needs T5+I2+F2 (or T3+I2 informal) AND N2,S2,R2."""
        formal_full = self.truth == "T5" and self.intent == "I2" and self.formal_correspondence == "F2"
        informal_full = self.truth == "T3" and self.intent == "I2" and self.formal_correspondence == "N/A"
        return (formal_full or informal_full) and self.novelty == "N2" \
            and self.significance == "S2" and self.reproducibility == "R2"

    def summary_label(self) -> str:
        """Honest, non-collapsed label (never a confidence %)."""
        # Positive result vocabulary is unavailable until the target, current
        # status, significance, and replay dimensions have each discharged their
        # minimum obligation.  The full profile remains visible for triage.
        common_axes = (
            self.intent == "I2"
            and self.novelty != "N0"
            and self.significance in {"S1", "S2"}
            and self.reproducibility in {"R1", "R2"}
        )
        if not common_axes:
            return "honest_no_result"
        if self.is_novel_autonomous_resolution():
            return "novel_autonomous_resolution"
        if self.truth == "T5" and self.formal_correspondence == "F2" \
                and self.novelty != "N2":
            return "formally_proved_novelty_unresolved"
        if self.truth == "T4" and self.formal_correspondence == "F2":
            return "kernel_checked_encoded_theorem"
        if self.truth == "T3" and self.formal_correspondence == "N/A":
            return "rigorous_informal_result"
        if self.truth == "T2" and self.formal_correspondence == "N/A":
            return "verified_finite_or_conditional_result"
        if self.truth == "T1" and self.formal_correspondence == "N/A":
            return "supported_conjecture"
        return "honest_no_result"

    def attested_record(self) -> dict[str, Any]:
        return {
            "profile": self.profile(),
            "evidence_hash": self.evidence_hash,
            "truth_claim_id": self.truth_claim_id,
            "truth_claim_hash": self.truth_claim_hash,
            "truth_run_id": self.truth_run_id,
            "truth_event_count": self.truth_event_count,
            "truth_event_head_id": self.truth_event_head_id,
            "truth_event_merkle_root": self.truth_event_merkle_root,
            "source_bytes_hash": self.source_bytes_hash,
            "interpretation_hash": self.interpretation_hash,
            "informal_claim_hash": self.informal_claim_hash,
            "intent_certificate_id": self.intent_certificate_id,
            "formal_correspondence_certificate_id": (
                self.formal_correspondence_certificate_id
            ),
            "elaborated_type_hash": self.elaborated_type_hash,
            "issued_at": self.issued_at,
            "attestor_id": self.attestor_id,
            "key_fingerprint": self.key_fingerprint,
        }

    @property
    def gate_digest(self) -> str:
        return content_id(self.attested_record() | {"signature": self.signature})

    def verify_attestation(
        self, *, env: dict[str, str] | None = None, now: float | None = None,
        max_age_s: float = 900.0, event_log: EventLog | None = None,
    ) -> bool:
        try:
            key = _gate_key(env)
            issued = _parse_utc(self.issued_at)
        except GateSecurityError:
            return False
        current = time.time() if now is None else float(now)
        age = current - issued
        expected = hmac.new(
            key, canonical_json(self.attested_record()).encode("utf-8"), "sha256"
        ).hexdigest()
        return bool(
            self.signature
            and is_sha256(self.evidence_hash)
            and self.attestor_id
            and self.truth_claim_id
            and is_sha256(self.truth_claim_hash)
            and self.truth_run_id
            and self.truth_event_count > 0
            and is_sha256(self.truth_event_head_id)
            and is_sha256(self.truth_event_merkle_root)
            and self.key_fingerprint == sha256_bytes(key)
            and -5.0 <= age <= max_age_s
            and event_log is not None
            and event_log.verify_integrity()
            and event_log.run_id == self.truth_run_id
            and len(event_log) == self.truth_event_count
            and event_log.last_event_id() == self.truth_event_head_id
            and event_log.merkle_root() == self.truth_event_merkle_root
            and hmac.compare_digest(expected, self.signature)
        )

    def attest(
        self, *, env: dict[str, str] | None = None, issued_at: str | None = None,
        attestor_id: str = "egmra-release-gate-auditor",
    ) -> "FiveGateResult":
        key = _gate_key(env)
        unsigned = FiveGateResult(
            **self.profile(),
            evidence_hash=self.evidence_hash,
            truth_claim_id=self.truth_claim_id,
            truth_claim_hash=self.truth_claim_hash,
            truth_run_id=self.truth_run_id,
            truth_event_count=self.truth_event_count,
            truth_event_head_id=self.truth_event_head_id,
            truth_event_merkle_root=self.truth_event_merkle_root,
            source_bytes_hash=self.source_bytes_hash,
            interpretation_hash=self.interpretation_hash,
            informal_claim_hash=self.informal_claim_hash,
            intent_certificate_id=self.intent_certificate_id,
            formal_correspondence_certificate_id=(
                self.formal_correspondence_certificate_id
            ),
            elaborated_type_hash=self.elaborated_type_hash,
            issued_at=issued_at or _utc_now(),
            attestor_id=attestor_id,
            key_fingerprint=sha256_bytes(key),
        )
        signature = hmac.new(
            key, canonical_json(unsigned.attested_record()).encode("utf-8"), "sha256"
        ).hexdigest()
        return FiveGateResult(**(unsigned.__dict__ | {"signature": signature}))


def run_five_gates(
    *,
    truth_snapshot: TruthSnapshot | None = None,
    event_log: EventLog | None = None,
    profile: EvidenceProfile | None = None,
    intent_cert: IntentCertificate | None,
    correspondence_cert: FormalCorrespondenceCertificate | None,
    novelty_verdict: str,
    informal_only: bool,
    responsive: bool = False,
    non_vacuous: bool = False,
    expert_reviewed: bool = False,
    dependency_audit_complete: bool = False,
    hardened: bool = False,
    replay_reports: list[ReplayReport] | None = None,
    high_value: bool = False,
    source_bytes_hash: str = "",
    interpretation_hash: str = "",
    informal_claim_hash: str = "",
    elaborated_type_hash: str = "",
    env: dict[str, str] | None = None,
    issued_at: str | None = None,
    now: float | None = None,
) -> FiveGateResult:
    if profile is not None:
        raise GateSecurityError(
            "raw EvidenceProfile is not release authority; provide a signed TruthSnapshot"
        )
    if truth_snapshot is None or event_log is None:
        raise GateSecurityError("truth_snapshot and current event_log are required")
    current = time.time() if now is None else float(now)
    if not truth_snapshot.verify(
        env=env,
        event_log=event_log,
        expected_claim_id=truth_snapshot.claim_id,
        now=current,
    ):
        raise GateSecurityError("truth snapshot is unsigned, forged, stale, or not current")
    snapshot_profile = _profile_from_snapshot(truth_snapshot)
    # Only a replay-derived SUPPORTED claim may contribute positive truth axes.
    profile = snapshot_profile if truth_snapshot.truth_status == "SUPPORTED" else EvidenceProfile()
    if intent_cert is not None and (
        profile.intent_certificate_id != intent_cert.certificate_id
    ):
        intent_cert = None
    if correspondence_cert is not None and (
        profile.formal_correspondence_certificate_id != correspondence_cert.certificate_id
    ):
        correspondence_cert = None
    reports = replay_reports or []
    # Intent approval is authority for this exact truth claim, never a nearby
    # or substituted claim with a reused certificate identifier.
    bound_informal_claim_hash = (
        informal_claim_hash
        if informal_claim_hash == truth_snapshot.canonical_hash
        else ""
    )
    computed_intent = intent_gate(
        intent_cert,
        source_bytes_hash=source_bytes_hash,
        interpretation_hash=interpretation_hash,
        informal_claim_hash=bound_informal_claim_hash,
    )
    computed_formal_correspondence = formal_correspondence_gate(
        correspondence_cert,
        informal_only=informal_only,
        intent_cert=intent_cert,
        informal_claim_hash=bound_informal_claim_hash,
        elaborated_type_hash=elaborated_type_hash,
        parent_intent_level=computed_intent,
        verification_env=env,
    )
    result = FiveGateResult(
        truth=truth_gate(profile, high_value=high_value,
                         dependency_audit_complete=dependency_audit_complete, hardened=hardened),
        intent=computed_intent,
        formal_correspondence=computed_formal_correspondence,
        novelty=novelty_gate(novelty_verdict),
        significance=significance_gate(responsive=responsive, non_vacuous=non_vacuous,
                                       expert_reviewed=expert_reviewed),
        reproducibility=reproducibility_gate(reports),
        evidence_hash=truth_snapshot.snapshot_digest,
        truth_claim_id=truth_snapshot.claim_id,
        truth_claim_hash=truth_snapshot.canonical_hash,
        truth_run_id=truth_snapshot.run_id,
        truth_event_count=truth_snapshot.event_count,
        truth_event_head_id=truth_snapshot.event_head_id,
        truth_event_merkle_root=truth_snapshot.event_merkle_root,
        source_bytes_hash=source_bytes_hash if computed_intent == "I2" else "",
        interpretation_hash=interpretation_hash if computed_intent == "I2" else "",
        informal_claim_hash=(
            bound_informal_claim_hash if computed_intent == "I2" else ""
        ),
        intent_certificate_id=(
            intent_cert.certificate_id
            if computed_intent == "I2" and intent_cert is not None
            else ""
        ),
        formal_correspondence_certificate_id=(
            correspondence_cert.certificate_id
            if correspondence_cert is not None
            and computed_formal_correspondence == "F2"
            else ""
        ),
        elaborated_type_hash=(
            elaborated_type_hash
            if correspondence_cert is not None
            and computed_formal_correspondence == "F2"
            else ""
        ),
    )
    try:
        return result.attest(
            env=env, issued_at=issued_at or _utc_now(current)
        )
    except GateSecurityError:
        # Profiles remain useful for local analysis, but an unattested result is
        # rejected by promotion and every communication/release entry point.
        return result
