"""Durable authentication for independent semantic-intent review.

Reviewer names in a JSON object are not an authority boundary.  An I2 review is
therefore accepted only when a separately provisioned review service has signed
the exact source, interpretation, and informal-claim bindings.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
import hmac
import os
from typing import Mapping

from egmra.provenance.hashing import canonical_json, content_id
from egmra.truth.entities import IntentCertificate, Interpretation


INTENT_REVIEW_KEY_ENV = "EGMRA_INTENT_REVIEW_KEY"
_GENERATOR_IDENTITIES = frozenset({"governor", "intake_retrieval", "intake_authority"})


class IntentReviewError(ValueError):
    """An intent review is unauthenticated, self-approved, or malformed."""


def interpretation_review_hash(interpretation: Interpretation) -> str:
    """Hash the locked semantics, excluding mutable workflow/status fields."""
    return content_id({
        "interpretation_id": interpretation.interpretation_id,
        "parent_problem_id": interpretation.parent_problem_id,
        "normalized_statement": interpretation.normalized_statement,
        "binders": interpretation.binders,
        "hypotheses": interpretation.hypotheses,
        "conclusion": interpretation.conclusion,
        "relation_to_parent": interpretation.relation_to_parent,
        "ambiguities_resolved": interpretation.ambiguities_resolved,
        "ambiguities_open": interpretation.ambiguities_open,
    })


def _key(env: Mapping[str, str] | None) -> bytes:
    source = os.environ if env is None else env
    value = source.get(INTENT_REVIEW_KEY_ENV, "")
    encoded = value.encode("utf-8")
    if len(encoded) < 32:
        raise IntentReviewError(
            f"{INTENT_REVIEW_KEY_ENV} must contain at least 32 bytes"
        )
    return encoded


def _record(certificate: IntentCertificate) -> dict:
    record = certificate.to_dict()
    record.pop("review_signature", None)
    return record


def _validate_independence(certificate: IntentCertificate) -> None:
    reviewers = set(certificate.reviewer_ids)
    if not reviewers:
        raise IntentReviewError("intent review requires an identified reviewer")
    if reviewers & _GENERATOR_IDENTITIES:
        raise IntentReviewError("intent reviewer must be independent of generation")
    disclosures = {
        item.get("reviewer_id"): item
        for item in certificate.reviewer_independence_and_conflicts
        if isinstance(item, dict) and isinstance(item.get("reviewer_id"), str)
    }
    if not reviewers.issubset(disclosures):
        raise IntentReviewError("every intent reviewer requires an independence disclosure")
    for reviewer in reviewers:
        disclosure = disclosures[reviewer]
        if disclosure.get("conflicts"):
            raise IntentReviewError("conflicted reviewers cannot issue an approved intent review")
        independent_from = set(disclosure.get("independent_from", ()))
        if not {"governor", "intake_retrieval"}.issubset(independent_from):
            raise IntentReviewError("reviewer independence from intake and generation is unproven")


def sign_intent_certificate(
    certificate: IntentCertificate, *, env: Mapping[str, str] | None = None,
) -> IntentCertificate:
    """Sign an exact review result in the independently held review domain."""
    _validate_independence(certificate)
    key = _key(env)
    key_id = hashlib.sha256(key).hexdigest()[:16]
    unsigned = replace(certificate, reviewer_key_id=key_id, review_signature="")
    signature = hmac.new(
        key, canonical_json(_record(unsigned)).encode("utf-8"), hashlib.sha256,
    ).hexdigest()
    return replace(unsigned, review_signature=signature)


def verify_intent_certificate(
    certificate: IntentCertificate, *, env: Mapping[str, str] | None = None,
) -> bool:
    """Fail closed for absent keys, malformed disclosures, or changed bindings."""
    try:
        _validate_independence(certificate)
        key = _key(env)
    except (IntentReviewError, TypeError, AttributeError):
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

