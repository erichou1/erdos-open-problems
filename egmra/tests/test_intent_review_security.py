"""Adversarial checks for durable, independently authenticated intent review."""

from __future__ import annotations

from dataclasses import replace

from egmra.intake import build_problem_contract
from egmra.intake.review import (
    interpretation_review_hash,
    sign_intent_certificate,
)
from egmra.provenance.hashing import sha256_hex
from egmra.release.gates import intent_gate
from egmra.truth.entities import IntentCertificate, Verdict


SOURCE = b"Prove that for all natural numbers n, n squared is at least 0."
REVIEW_ENV = {
    "EGMRA_INTENT_REVIEW_KEY": "intent-review-test-key-that-is-at-least-32-bytes",
}


def _unsigned_certificate() -> tuple[IntentCertificate, str, str, str]:
    contract = build_problem_contract(
        problem_id="intent-review", source_bytes=SOURCE, source_id="fixture",
        predicate=lambda n: n * n >= 0,
    )
    interpretation_hash = interpretation_review_hash(contract.lattice.nodes[0])
    claim_hash = sha256_hex(contract.lattice.nodes[0].conclusion)
    certificate = IntentCertificate(
        certificate_id="intent-review-1",
        source_bytes_hash=contract.source_bytes_hash,
        interpretation_hash=interpretation_hash,
        informal_claim_hash=claim_hash,
        methods=[
            "independent_parse", "examples", "anti_examples",
            "paraphrase", "local_mutation",
        ],
        reviewer_ids=["independent-semantic-reviewer"],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "independent-semantic-reviewer",
            "independent_from": ["governor", "intake_retrieval"],
            "conflicts": [],
        }],
        verdict=Verdict.APPROVED,
    )
    return certificate, contract.source_bytes_hash, interpretation_hash, claim_hash


def test_raw_reviewer_strings_cannot_create_i2() -> None:
    certificate, source_hash, interpretation_hash, claim_hash = _unsigned_certificate()

    assert intent_gate(
        certificate,
        source_bytes_hash=source_hash,
        interpretation_hash=interpretation_hash,
        informal_claim_hash=claim_hash,
        verification_env=REVIEW_ENV,
    ) != "I2"


def test_authenticated_intent_review_is_bound_to_exact_semantics() -> None:
    certificate, source_hash, interpretation_hash, claim_hash = _unsigned_certificate()
    signed = sign_intent_certificate(certificate, env=REVIEW_ENV)

    assert intent_gate(
        signed,
        source_bytes_hash=source_hash,
        interpretation_hash=interpretation_hash,
        informal_claim_hash=claim_hash,
        verification_env=REVIEW_ENV,
    ) == "I2"
    forged = replace(signed, informal_claim_hash="0" * 64)
    assert intent_gate(
        forged,
        source_bytes_hash=source_hash,
        interpretation_hash=interpretation_hash,
        informal_claim_hash="0" * 64,
        verification_env=REVIEW_ENV,
    ) != "I2"
