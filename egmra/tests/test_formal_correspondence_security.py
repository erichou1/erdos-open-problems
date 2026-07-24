"""Regression tests for formal-correspondence reviewer independence."""

from dataclasses import replace

import pytest

from egmra.lean.correspondence import (
    FormalCorrespondenceAuthError,
    sign_formal_correspondence_certificate,
    verify_formal_correspondence_certificate,
)
from egmra.provenance.hashing import sha256_hex
from egmra.truth.entities import FormalCorrespondenceCertificate, Verdict


def _certificate(**changes):
    values = {
        "certificate_id": "fcc",
        "intent_certificate_id": "intent",
        "informal_claim_hash": sha256_hex("claim"),
        "lean_declaration_name": "target",
        "elaborated_type_hash": sha256_hex("type"),
        "notation_and_definition_map_hash": sha256_hex("notation"),
        "methods": [
            "backtranslation", "examples", "anti_examples", "paraphrase",
            "local_mutation",
        ],
        "reviewer_ids": ["independent-formal-reviewer"],
        "reviewer_independence_and_conflicts": [{
            "reviewer_id": "independent-formal-reviewer",
            "independent_from": ["formalization_authority", "governor"],
            "conflicts": [],
        }],
        "verdict": Verdict.APPROVED,
    }
    values.update(changes)
    return FormalCorrespondenceCertificate(**values)


@pytest.mark.parametrize(
    "changes",
    [
        {"reviewer_ids": [], "reviewer_independence_and_conflicts": []},
        {"reviewer_ids": ["formalization_authority"],
         "reviewer_independence_and_conflicts": [{
             "reviewer_id": "formalization_authority",
             "independent_from": ["formalization_authority", "governor"],
             "conflicts": [],
         }]},
        {"reviewer_ids": ["r"], "reviewer_independence_and_conflicts": []},
        {"reviewer_ids": ["r"], "reviewer_independence_and_conflicts": [{
            "reviewer_id": "r", "independent_from": ["governor"], "conflicts": [],
        }]},
        {"reviewer_ids": ["r"], "reviewer_independence_and_conflicts": [{
            "reviewer_id": "r",
            "independent_from": ["formalization_authority", "governor"],
            "conflicts": ["authored-proof"],
        }]},
    ],
)
def test_correspondence_signer_rejects_missing_or_conflicted_independence(changes):
    with pytest.raises(FormalCorrespondenceAuthError):
        sign_formal_correspondence_certificate(_certificate(**changes))


def test_correspondence_signature_binds_disclosures_and_reviewer_identity():
    signed = sign_formal_correspondence_certificate(_certificate())
    assert verify_formal_correspondence_certificate(signed)
    assert not verify_formal_correspondence_certificate(
        replace(signed, reviewer_ids=["substituted-reviewer"])
    )
    changed = [dict(signed.reviewer_independence_and_conflicts[0])]
    changed[0]["conflicts"] = ["late-conflict"]
    assert not verify_formal_correspondence_certificate(
        replace(signed, reviewer_independence_and_conflicts=changed)
    )
