"""Expert significance review — the S2 gate's missing workflow (R10).

``significance_gate`` has always accepted ``expert_reviewed=True`` (S1→S2),
but nothing could ever produce that input: there was no artifact, no signing
key, and no CLI.  This module is that producer.

An expert review is a *human* judgement that the released result genuinely
resolves the stated problem in full — it is NOT a correctness check (the
truth plane owns correctness) and it can never be produced by a model.  The
certificate binds the exact problem source bytes and the locked informal
claim, so a review of one statement can never be stretched over another.

Honesty invariants:

* signed with its own key (``EGMRA_EXPERT_REVIEW_KEY``) so holding the intent
  or correspondence keys does not let anyone mint expert significance;
* the reviewer must declare independence from generation and release, and a
  conflicted reviewer cannot approve;
* verification fails closed: absent key, changed bindings, or a rejected
  verdict simply mean ``expert_reviewed=False`` — S1, exactly as before.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from collections.abc import Mapping
from dataclasses import dataclass, field, replace

from egmra.provenance.hashing import canonical_json

EXPERT_REVIEW_KEY_ENV = "EGMRA_EXPERT_REVIEW_KEY"
_GENERATOR_IDENTITIES = {"governor", "worker", "formalization_authority", "release"}


class ExpertReviewError(ValueError):
    """Expert-review input is malformed or unsigned."""


@dataclass(frozen=True)
class ExpertReviewCertificate:
    """A human expert's signed significance judgement for one locked claim."""

    certificate_id: str
    source_bytes_hash: str
    informal_claim_hash: str
    reviewer_id: str
    verdict: str                       # "approved" | "rejected"
    statement_of_significance: str
    independent_from: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    created_at: str = ""
    reviewer_key_id: str = ""
    review_signature: str = ""

    def to_dict(self) -> dict:
        return {
            "certificate_id": self.certificate_id,
            "source_bytes_hash": self.source_bytes_hash,
            "informal_claim_hash": self.informal_claim_hash,
            "reviewer_id": self.reviewer_id,
            "verdict": self.verdict,
            "statement_of_significance": self.statement_of_significance,
            "independent_from": list(self.independent_from),
            "conflicts": list(self.conflicts),
            "created_at": self.created_at,
            "reviewer_key_id": self.reviewer_key_id,
            "review_signature": self.review_signature,
        }

    @classmethod
    def from_dict(cls, record: Mapping) -> "ExpertReviewCertificate":
        if not isinstance(record, Mapping):
            raise ExpertReviewError("expert review record must be an object")
        try:
            return cls(
                certificate_id=str(record["certificate_id"]),
                source_bytes_hash=str(record["source_bytes_hash"]),
                informal_claim_hash=str(record["informal_claim_hash"]),
                reviewer_id=str(record["reviewer_id"]),
                verdict=str(record["verdict"]),
                statement_of_significance=str(
                    record.get("statement_of_significance", "")),
                independent_from=tuple(record.get("independent_from", ())),
                conflicts=tuple(record.get("conflicts", ())),
                created_at=str(record.get("created_at", "")),
                reviewer_key_id=str(record.get("reviewer_key_id", "")),
                review_signature=str(record.get("review_signature", "")),
            )
        except KeyError as exc:
            raise ExpertReviewError(f"expert review record is missing {exc}") from exc


def _key(env: Mapping[str, str] | None) -> bytes:
    source = os.environ if env is None else env
    value = source.get(EXPERT_REVIEW_KEY_ENV, "")
    encoded = value.encode("utf-8")
    if len(encoded) < 32:
        raise ExpertReviewError(
            f"{EXPERT_REVIEW_KEY_ENV} must contain at least 32 bytes")
    return encoded


def _record(certificate: ExpertReviewCertificate) -> dict:
    record = certificate.to_dict()
    record.pop("review_signature", None)
    return record


def _validate(certificate: ExpertReviewCertificate) -> None:
    if not certificate.reviewer_id.strip():
        raise ExpertReviewError("expert review requires an identified reviewer")
    if certificate.reviewer_id in _GENERATOR_IDENTITIES:
        raise ExpertReviewError("expert reviewer must be independent of generation")
    if certificate.verdict not in {"approved", "rejected"}:
        raise ExpertReviewError("verdict must be approved|rejected")
    if certificate.verdict == "approved":
        if certificate.conflicts:
            raise ExpertReviewError(
                "conflicted reviewers cannot approve significance")
        if not {"governor", "release"}.issubset(set(certificate.independent_from)):
            raise ExpertReviewError(
                "reviewer independence from generation and release is unproven")
        if not certificate.statement_of_significance.strip():
            raise ExpertReviewError(
                "an approval requires a written statement of significance")


def sign_expert_review(
    certificate: ExpertReviewCertificate, *, env: Mapping[str, str] | None = None,
) -> ExpertReviewCertificate:
    """Sign an expert significance judgement in its own key domain."""
    _validate(certificate)
    key = _key(env)
    key_id = hashlib.sha256(key).hexdigest()[:16]
    unsigned = replace(certificate, reviewer_key_id=key_id, review_signature="")
    signature = hmac.new(
        key, canonical_json(_record(unsigned)).encode("utf-8"), hashlib.sha256,
    ).hexdigest()
    return replace(unsigned, review_signature=signature)


def verify_expert_review(
    certificate: ExpertReviewCertificate, *, env: Mapping[str, str] | None = None,
) -> bool:
    """Fail closed for absent keys, bad disclosures, or changed bindings."""
    try:
        _validate(certificate)
        key = _key(env)
    except (ExpertReviewError, TypeError, AttributeError):
        return False
    expected_key_id = hashlib.sha256(key).hexdigest()[:16]
    if not hmac.compare_digest(certificate.reviewer_key_id, expected_key_id):
        return False
    unsigned = replace(certificate, review_signature="")
    expected = hmac.new(
        key, canonical_json(_record(unsigned)).encode("utf-8"), hashlib.sha256,
    ).hexdigest()
    return bool(certificate.review_signature) and hmac.compare_digest(
        certificate.review_signature, expected,
    )


def expert_reviewed_for_run(
    certificate: ExpertReviewCertificate | None, *,
    source_bytes_hash: str, informal_claim_hash: str,
    env: Mapping[str, str] | None = None,
) -> bool:
    """The single gate input: an authenticated APPROVAL bound to THIS claim."""
    if certificate is None:
        return False
    return (
        certificate.verdict == "approved"
        and certificate.source_bytes_hash == source_bytes_hash
        and certificate.informal_claim_hash == informal_claim_hash
        and verify_expert_review(certificate, env=env)
    )
