"""ReleaseCertificate + signature (spec §11.5).

The communication layer renders these fields separately; it never compresses them
into a self-reported "confidence 95%".
"""

from __future__ import annotations

import calendar
import hmac
import os
import time
from dataclasses import dataclass, field
from typing import Any

from egmra.provenance.hashing import canonical_json, content_id, is_sha256, sha256_bytes
from egmra.release.gates import FiveGateResult
from egmra.release.policy import PromotionDecision
from egmra.truth.events import EventLog

_MIN_RELEASE_KEY_BYTES = 32


class ReleaseSecurityError(ValueError):
    """A release is unsigned, forged, stale, or lacks promotion authority."""


def _release_key(env: dict[str, str] | None = None) -> bytes:
    values = env if env is not None else dict(os.environ)
    key = values.get("EGMRA_RELEASE_KEY", "").strip().encode("utf-8")
    if len(key) < _MIN_RELEASE_KEY_BYTES:
        raise ReleaseSecurityError(
            f"EGMRA_RELEASE_KEY must contain at least {_MIN_RELEASE_KEY_BYTES} bytes"
        )
    return key


def _separated_keys(env: dict[str, str] | None = None) -> bool:
    values = env if env is not None else dict(os.environ)
    raw = [
        values.get("EGMRA_GATE_KEY", "").strip().encode("utf-8"),
        values.get("EGMRA_PROMOTION_KEY", "").strip().encode("utf-8"),
        values.get("EGMRA_RELEASE_KEY", "").strip().encode("utf-8"),
    ]
    return all(len(value) >= 32 for value in raw) and len(set(raw)) == len(raw)


def _parse_utc(value: str) -> float:
    try:
        return float(calendar.timegm(time.strptime(value, "%Y-%m-%dT%H:%M:%SZ")))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ReleaseSecurityError("invalid UTC release timestamp") from exc


@dataclass
class ReleaseCertificate:
    problem_contract_hash: str
    active_interpretation_id: str
    active_interpretation_hash: str
    result_claim_id: str
    result_claim_hash: str
    gates: FiveGateResult
    formal_target_elaborated_type_hash: str = ""
    proof_bundle_hash: str = ""
    truth_certificate_ids: tuple[str, ...] = ()
    trust_policy_hash: str = ""
    transitive_axiom_report_hash: str = ""
    checker_ids: tuple[str, ...] = ()
    intent_certificate_id: str = ""
    formal_correspondence_certificate_id: str = ""
    novelty_search_packet_hash: str = ""
    reproducibility_environments: tuple[str, ...] = ()
    autonomy: dict = field(default_factory=dict)
    unresolved_risks: tuple[str, ...] = ()
    signer_id: str = "egmra-release-auditor"
    signature_algorithm: str = "HMAC-SHA256"
    key_fingerprint: str = ""
    promotion_authorization: dict[str, Any] = field(default_factory=dict)
    signed_at: str = ""
    signature: str = ""

    def subject_record(self) -> dict[str, Any]:
        return {
            "problem_contract_hash": self.problem_contract_hash,
            "active_interpretation_id": self.active_interpretation_id,
            "active_interpretation_hash": self.active_interpretation_hash,
            "result_claim_id": self.result_claim_id,
            "result_claim_hash": self.result_claim_hash,
            "gates": {
                "profile": self.gates.profile(),
                "evidence_hash": self.gates.evidence_hash,
                "truth_claim_id": self.gates.truth_claim_id,
                "truth_claim_hash": self.gates.truth_claim_hash,
                "truth_run_id": self.gates.truth_run_id,
                "truth_event_count": self.gates.truth_event_count,
                "truth_event_head_id": self.gates.truth_event_head_id,
                "truth_event_merkle_root": self.gates.truth_event_merkle_root,
                "source_bytes_hash": self.gates.source_bytes_hash,
                "interpretation_hash": self.gates.interpretation_hash,
                "informal_claim_hash": self.gates.informal_claim_hash,
                "intent_certificate_id": self.gates.intent_certificate_id,
                "formal_correspondence_certificate_id": (
                    self.gates.formal_correspondence_certificate_id
                ),
                "elaborated_type_hash": self.gates.elaborated_type_hash,
                "issued_at": self.gates.issued_at,
                "attestor_id": self.gates.attestor_id,
                "key_fingerprint": self.gates.key_fingerprint,
                "signature": self.gates.signature,
            },
            "formal_target_elaborated_type_hash": self.formal_target_elaborated_type_hash,
            "proof_bundle_hash": self.proof_bundle_hash,
            "truth_certificate_ids": list(self.truth_certificate_ids),
            "trust_policy_hash": self.trust_policy_hash,
            "transitive_axiom_report_hash": self.transitive_axiom_report_hash,
            "checker_ids": list(self.checker_ids),
            "intent_certificate_id": self.intent_certificate_id,
            "formal_correspondence_certificate_id": self.formal_correspondence_certificate_id,
            "novelty_search_packet_hash": self.novelty_search_packet_hash,
            "reproducibility_environments": list(self.reproducibility_environments),
            "autonomy": self.autonomy,
            "unresolved_risks": list(self.unresolved_risks),
        }

    @property
    def subject_hash(self) -> str:
        return content_id(self.subject_record())

    def _validate_mandatory_fields(self) -> None:
        hashes = {
            "problem_contract_hash": self.problem_contract_hash,
            "active_interpretation_hash": self.active_interpretation_hash,
            "result_claim_hash": self.result_claim_hash,
        }
        invalid = [name for name, value in hashes.items() if not is_sha256(value)]
        if invalid:
            raise ReleaseSecurityError(
                f"release certificate has invalid mandatory hashes: {sorted(invalid)}"
            )
        if not self.active_interpretation_id or not self.result_claim_id:
            raise ReleaseSecurityError("interpretation and result claim IDs are required")
        if (
            self.result_claim_id != self.gates.truth_claim_id
            or self.result_claim_hash != self.gates.truth_claim_hash
        ):
            raise ReleaseSecurityError(
                "release result claim is not the claim authenticated by the truth snapshot"
            )

        if self.gates.truth != "T0" and not self.truth_certificate_ids:
            raise ReleaseSecurityError("positive truth level requires truth certificate IDs")
        if self.gates.intent == "I2" and not self.intent_certificate_id:
            raise ReleaseSecurityError("I2 requires an intent certificate ID")
        if self.gates.intent == "I2" and (
            self.active_interpretation_hash != self.gates.interpretation_hash
            or self.result_claim_hash != self.gates.informal_claim_hash
            or self.intent_certificate_id != self.gates.intent_certificate_id
        ):
            raise ReleaseSecurityError(
                "release interpretation/claim/intent ID is not bound to the I2 gate"
            )
        if self.gates.formal_correspondence == "F2" and not (
            self.formal_correspondence_certificate_id
        ):
            raise ReleaseSecurityError("F2 requires a formal-correspondence certificate ID")
        if self.gates.formal_correspondence == "F2" and (
            self.formal_correspondence_certificate_id
            != self.gates.formal_correspondence_certificate_id
            or self.formal_target_elaborated_type_hash != self.gates.elaborated_type_hash
        ):
            raise ReleaseSecurityError(
                "release formal target/correspondence ID is not bound to the F2 gate"
            )
        if self.gates.novelty in {"N1", "N2"} and not is_sha256(
            self.novelty_search_packet_hash
        ):
            raise ReleaseSecurityError("N1/N2 requires a hashed novelty search packet")

        if self.gates.truth in {"T4", "T5"}:
            formal_hashes = {
                "formal_target_elaborated_type_hash": self.formal_target_elaborated_type_hash,
                "proof_bundle_hash": self.proof_bundle_hash,
                "trust_policy_hash": self.trust_policy_hash,
                "transitive_axiom_report_hash": self.transitive_axiom_report_hash,
            }
            bad_formal = [
                name for name, value in formal_hashes.items() if not is_sha256(value)
            ]
            if bad_formal or not self.checker_ids:
                raise ReleaseSecurityError(
                    "formal release is missing target/proof/trust/axiom hashes or checker IDs"
                )
            if self.gates.truth == "T5" and len(set(self.checker_ids)) < 2:
                raise ReleaseSecurityError("T5 requires two distinct checker identities")

        expected_environments = 2 if self.gates.reproducibility == "R2" else (
            1 if self.gates.reproducibility == "R1" else 0
        )
        if len(set(self.reproducibility_environments)) < expected_environments:
            raise ReleaseSecurityError(
                f"{self.gates.reproducibility} requires {expected_environments} replay environment(s)"
            )

        counts = self.autonomy.get("intervention_counts") if isinstance(self.autonomy, dict) else None
        if not isinstance(counts, dict) or any(
            not isinstance(counts.get(phase), int) or counts.get(phase, -1) < 0
            for phase in ("pre_run", "in_run", "post_run")
        ):
            raise ReleaseSecurityError(
                "autonomy metadata requires nonnegative pre_run/in_run/post_run counts"
            )
        if not is_sha256(self.autonomy.get("model_tool_trace_hash")):
            raise ReleaseSecurityError("autonomy metadata requires a model/tool trace hash")
        boundaries = self.autonomy.get("phase_boundaries")
        if not isinstance(boundaries, list):
            raise ReleaseSecurityError("autonomy metadata requires phase boundaries")

    def business_record(self) -> dict[str, Any]:
        return {
            **self.subject_record(),
            "promotion_authorization": self.promotion_authorization,
            "signer_id": self.signer_id,
            "signature_algorithm": self.signature_algorithm,
            "key_fingerprint": self.key_fingerprint,
            "signed_at": self.signed_at,
        }

    def sign(
        self, *, authorization: PromotionDecision | None = None,
        env: dict[str, str] | None = None, now: float | None = None,
        event_log: EventLog | None = None,
    ) -> "ReleaseCertificate":
        current = time.time() if now is None else float(now)
        key = _release_key(env)
        if not _separated_keys(env):
            raise ReleaseSecurityError(
                "gate, promotion, and release keys must all be strong and distinct"
            )
        if authorization is None:
            raise ReleaseSecurityError("promotion authorization is required before signing")
        self._validate_mandatory_fields()
        if not self.gates.verify_attestation(
            env=env, now=current, event_log=event_log
        ):
            raise ReleaseSecurityError("gate attestation is unsigned, forged, or stale")
        if not authorization.verify_authorization(
            gates=self.gates, subject_hash=self.subject_hash, env=env, now=current,
            event_log=event_log,
        ):
            raise ReleaseSecurityError("promotion authorization is forged, stale, or misbound")
        if self.signed_at:
            try:
                if abs(current - _parse_utc(self.signed_at)) > 5.0:
                    raise ReleaseSecurityError("caller-supplied signed_at is stale or future-dated")
            except ReleaseSecurityError:
                raise
        else:
            self.signed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(current))
        self.promotion_authorization = authorization.to_dict()
        self.key_fingerprint = sha256_bytes(key)
        payload = content_id(self.business_record())
        self.signature = hmac.new(key, payload.encode("utf-8"), "sha256").hexdigest()
        return self

    def verify(
        self, *, env: dict[str, str] | None = None, now: float | None = None,
        max_age_s: float = 900.0,
        event_log: EventLog | None = None,
    ) -> bool:
        try:
            key = _release_key(env)
            signed = _parse_utc(self.signed_at)
            authorization = PromotionDecision(
                **{
                    **self.promotion_authorization,
                    "reasons": tuple(self.promotion_authorization.get("reasons", ())),
                }
            )
        except (ReleaseSecurityError, TypeError, ValueError):
            return False
        current = time.time() if now is None else float(now)
        payload = content_id(self.business_record())
        expected = hmac.new(key, payload.encode("utf-8"), "sha256").hexdigest()
        age = current - signed
        return bool(
            self.signature
            and self.signature_algorithm == "HMAC-SHA256"
            and self.key_fingerprint == sha256_bytes(key)
            and _separated_keys(env)
            and -5.0 <= age <= max_age_s
            and self.gates.verify_attestation(
                env=env, now=current, event_log=event_log
            )
            and authorization.verify_authorization(
                gates=self.gates,
                subject_hash=self.subject_hash,
                env=env,
                now=signed,
                event_log=event_log,
            )
            and hmac.compare_digest(expected, self.signature)
        )

    def render(
        self, *, env: dict[str, str] | None = None, now: float | None = None,
        max_age_s: float = 900.0,
        event_log: EventLog | None = None,
    ) -> dict[str, Any]:
        """Render the five-gate profile separately — never a single confidence."""
        if not self.verify(
            env=env, now=now, max_age_s=max_age_s, event_log=event_log
        ):
            raise ReleaseSecurityError(
                "release certificate is unsigned, forged, stale, or unauthorized"
            )
        return {
            "label": self.gates.summary_label(),
            "gate_profile": self.gates.profile(),
            "unresolved_risks": list(self.unresolved_risks),
            "autonomy": self.autonomy,
            "signature_present": True,
            "signer_id": self.signer_id,
            "signed_at": self.signed_at,
            "key_fingerprint": self.key_fingerprint,
            "promotion_policy_hash": self.promotion_authorization.get("policy_hash", ""),
        }

    def canonical(self) -> str:
        return canonical_json(self.business_record() | {"signature": self.signature})
