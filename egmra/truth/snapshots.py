"""Signed claim snapshots for the truth-plane to release-plane boundary."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import hmac
import math
import os
import time
from typing import Any

from egmra.provenance.hashing import canonical_json, content_id, is_sha256
from egmra.truth.events import EventLog


class TruthSnapshotError(RuntimeError):
    """A truth snapshot cannot be issued or authenticated."""


def _key(env: dict[str, str] | None = None) -> bytes:
    source = os.environ if env is None else env
    raw = source.get("EGMRA_TRUTH_SNAPSHOT_KEY", "").strip()
    if not raw:
        raise TruthSnapshotError("EGMRA_TRUTH_SNAPSHOT_KEY is required")
    encoded = raw.encode("utf-8")
    if len(encoded) < 32:
        raise TruthSnapshotError("EGMRA_TRUTH_SNAPSHOT_KEY must contain at least 32 bytes")
    return encoded


@dataclass(frozen=True)
class TruthSnapshot:
    claim_id: str
    canonical_hash: str
    truth_status: str
    evidence_profile: dict[str, Any]
    status_version: int
    evidence_digest: str
    run_id: str
    event_count: int
    event_head_id: str
    event_merkle_root: str
    issued_at: float
    attestor_id: str
    key_fingerprint: str
    signature: str = ""

    def attested_record(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "canonical_hash": self.canonical_hash,
            "truth_status": self.truth_status,
            "evidence_profile": self.evidence_profile,
            "status_version": self.status_version,
            "evidence_digest": self.evidence_digest,
            "run_id": self.run_id,
            "event_count": self.event_count,
            "event_head_id": self.event_head_id,
            "event_merkle_root": self.event_merkle_root,
            "issued_at": self.issued_at,
            "attestor_id": self.attestor_id,
            "key_fingerprint": self.key_fingerprint,
        }

    @property
    def snapshot_digest(self) -> str:
        return content_id(self.attested_record() | {"signature": self.signature})

    def verify(
        self, *, env: dict[str, str] | None = None, event_log: EventLog | None = None,
        expected_claim_id: str | None = None, now: float | None = None,
        max_age_seconds: float = 60.0,
    ) -> bool:
        try:
            secret = _key(env)
            current = time.time() if now is None else float(now)
            if not math.isfinite(current) or not math.isfinite(self.issued_at):
                return False
            age = current - self.issued_at
            if age < -5 or age > max_age_seconds:
                return False
            if expected_claim_id is not None and self.claim_id != expected_claim_id:
                return False
            if self.truth_status not in {"UNKNOWN", "SUPPORTED", "REFUTED", "CONFLICTED"}:
                return False
            if self.status_version <= 0 or self.event_count <= 0:
                return False
            if not all(is_sha256(value) for value in (
                self.canonical_hash, self.evidence_digest, self.event_head_id,
                self.event_merkle_root, self.key_fingerprint,
            )):
                return False
            if self.key_fingerprint != hashlib.sha256(secret).hexdigest():
                return False
            expected = hmac.new(
                secret, canonical_json(self.attested_record()).encode("utf-8"), hashlib.sha256
            ).hexdigest()
            if not self.signature or not hmac.compare_digest(expected, self.signature):
                return False
            if event_log is not None:
                if not event_log.verify_integrity() or event_log.run_id != self.run_id:
                    return False
                if (
                    len(event_log) != self.event_count
                    or event_log.last_event_id() != self.event_head_id
                    or event_log.merkle_root() != self.event_merkle_root
                ):
                    return False
            return True
        except (TruthSnapshotError, TypeError, ValueError):
            return False


def issue_truth_snapshot(
    *, claim_id: str, canonical_hash: str, truth_status: str,
    evidence_profile: dict[str, Any], status_version: int, evidence_digest: str,
    event_log: EventLog, env: dict[str, str] | None = None,
    issued_at: float | None = None, attestor_id: str = "egmra-truth-plane",
) -> TruthSnapshot:
    secret = _key(env)
    timestamp = time.time() if issued_at is None else float(issued_at)
    if not math.isfinite(timestamp):
        raise TruthSnapshotError("snapshot timestamp must be finite")
    if not event_log.verify_integrity():
        raise TruthSnapshotError("event log integrity failed")
    unsigned = TruthSnapshot(
        claim_id=claim_id,
        canonical_hash=canonical_hash,
        truth_status=truth_status,
        evidence_profile=evidence_profile,
        status_version=status_version,
        evidence_digest=evidence_digest,
        run_id=event_log.run_id,
        event_count=len(event_log),
        event_head_id=event_log.last_event_id(),
        event_merkle_root=event_log.merkle_root(),
        issued_at=timestamp,
        attestor_id=attestor_id,
        key_fingerprint=hashlib.sha256(secret).hexdigest(),
    )
    signature = hmac.new(
        secret, canonical_json(unsigned.attested_record()).encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return replace(unsigned, signature=signature)
