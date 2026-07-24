"""Authenticated semantic-review boundary for formal correspondence certificates."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import hmac
import os

from egmra.provenance.hashing import canonical_json
from egmra.truth.entities import FormalCorrespondenceCertificate


class FormalCorrespondenceAuthError(ValueError):
    """A formal-correspondence review key or signature is invalid."""


def _review_key(env: dict[str, str] | None = None) -> bytes:
    values = os.environ if env is None else env
    key = values.get("EGMRA_FORMAL_CORRESPONDENCE_KEY", "").strip().encode("utf-8")
    if len(key) < 32:
        raise FormalCorrespondenceAuthError(
            "EGMRA_FORMAL_CORRESPONDENCE_KEY must contain at least 32 bytes"
        )
    return key


def _review_record(certificate: FormalCorrespondenceCertificate) -> dict:
    record = certificate.to_dict()
    record.pop("review_signature", None)
    return record


_GENERATOR_IDENTITIES = frozenset({"formalization_authority", "governor"})


def _validate_reviewer_independence(
    certificate: FormalCorrespondenceCertificate,
) -> None:
    reviewers = certificate.reviewer_ids
    if not reviewers or any(not isinstance(item, str) or not item.strip() for item in reviewers):
        raise FormalCorrespondenceAuthError(
            "formal correspondence requires an identified reviewer"
        )
    if len(set(reviewers)) != len(reviewers):
        raise FormalCorrespondenceAuthError("duplicate formal reviewers are forbidden")
    if set(reviewers) & _GENERATOR_IDENTITIES:
        raise FormalCorrespondenceAuthError(
            "formal correspondence reviewer must be independent of generation and release"
        )
    disclosures: dict[str, dict] = {}
    for item in certificate.reviewer_independence_and_conflicts:
        if not isinstance(item, dict) or not isinstance(item.get("reviewer_id"), str):
            raise FormalCorrespondenceAuthError("reviewer disclosure is malformed")
        reviewer_id = item["reviewer_id"]
        if reviewer_id in disclosures:
            raise FormalCorrespondenceAuthError("duplicate reviewer disclosure")
        disclosures[reviewer_id] = item
    if set(reviewers) != set(disclosures):
        raise FormalCorrespondenceAuthError(
            "every and only named formal reviewers require an independence disclosure"
        )
    for reviewer in reviewers:
        disclosure = disclosures[reviewer]
        conflicts = disclosure.get("conflicts")
        if not isinstance(conflicts, list) or conflicts:
            raise FormalCorrespondenceAuthError(
                "conflicted or undisclosed reviewers cannot approve correspondence"
            )
        independent_from = disclosure.get("independent_from")
        if not isinstance(independent_from, list) or not _GENERATOR_IDENTITIES.issubset(
            set(independent_from)
        ):
            raise FormalCorrespondenceAuthError(
                "reviewer independence from formalization and governor is unproven"
            )


def sign_formal_correspondence_certificate(
    certificate: FormalCorrespondenceCertificate, *,
    env: dict[str, str] | None = None,
    reviewer_key_id: str | None = None,
) -> FormalCorrespondenceCertificate:
    """Sign the exact I2/claim/declaration/type/review-method bindings."""
    _validate_reviewer_independence(certificate)
    key = _review_key(env)
    expected_key_id = hashlib.sha256(key).hexdigest()[:16]
    if reviewer_key_id is not None and reviewer_key_id != expected_key_id:
        raise FormalCorrespondenceAuthError("reviewer_key_id does not identify the review key")
    unsigned = replace(
        certificate,
        reviewer_key_id=expected_key_id,
        review_signature="",
    )
    signature = hmac.new(
        key, canonical_json(_review_record(unsigned)).encode("utf-8"), "sha256"
    ).hexdigest()
    return replace(unsigned, review_signature=signature)


def verify_formal_correspondence_certificate(
    certificate: FormalCorrespondenceCertificate, *,
    env: dict[str, str] | None = None,
) -> bool:
    """Verify the durable review signature; raw reviewer labels have no authority."""
    if not certificate.reviewer_key_id.strip() or not certificate.review_signature:
        return False
    try:
        _validate_reviewer_independence(certificate)
        key = _review_key(env)
    except (FormalCorrespondenceAuthError, TypeError, AttributeError):
        return False
    if not hmac.compare_digest(
        certificate.reviewer_key_id, hashlib.sha256(key).hexdigest()[:16]
    ):
        return False
    expected = hmac.new(
        key, canonical_json(_review_record(certificate)).encode("utf-8"), "sha256"
    ).hexdigest()
    return hmac.compare_digest(expected, certificate.review_signature)
