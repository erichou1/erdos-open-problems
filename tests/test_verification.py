import unittest

from verification import (
    candidate_contract, Review, candidate_status, evaluate_gate,
    VerificationEvidence,
)

REQUIRED_TEST_ROLES = (
    "statement_integrity", "structural_dependency", "logic",
    "counterexample", "theorem_hypotheses", "mechanical_evidence",
    "global_synthesis", "adjudicator",
)


def passing_review(role: str) -> Review:
    return Review(
        reviewer_id=f"reviewer-{role}",
        reviewer_role=role,
        independent_context=True,
        verdict="pass",
        claims_checked=12,
        claims_total=12,
        checked_claim_ids=tuple(f"C{i}" for i in range(1, 13)),
        completeness_score=100,
        proof_confidence=99,
        adversarial_survival_score=98,
        adjudicated_outcome=("proved" if role == "adjudicator" else ""),
        context_id=f"context-{role}",
    )


def passing_evidence(statement_sha="a" * 64):
    return VerificationEvidence(
        kind="expert_review", verifier="expert", statement_sha256=statement_sha,
        outcome="candidate_proved", artifact_sha256="b" * 64, passed=True,
        candidate_sha256="c" * 64,
    )


class VerificationGateTests(unittest.TestCase):
    def test_promotes_only_after_all_review_roles_pass(self):
        reviews = [passing_review(role) for role in REQUIRED_TEST_ROLES]
        decision = evaluate_gate(
            "candidate_proved", reviews, verification_evidence=[passing_evidence()]
        )
        self.assertEqual(decision.status, "verified_proved")

    def test_rejects_a_single_open_gap(self):
        reviews = [
            passing_review("statement_integrity"),
            passing_review("structural_dependency"),
            passing_review("logic"),
            passing_review("counterexample"),
            Review(
                **{
                    **passing_review("theorem_hypotheses").__dict__,
                    "open_gaps": ("compactness hypothesis is unchecked",),
                }
            ),
            passing_review("mechanical_evidence"),
            passing_review("global_synthesis"),
            passing_review("adjudicator"),
        ]
        decision = evaluate_gate("candidate_proved", reviews)
        self.assertEqual(decision.status, "candidate_rejected")
        self.assertTrue(any("open gaps" in reason for reason in decision.reasons))

    def test_rejects_self_review_and_missing_role(self):
        review = Review(
            **{**passing_review("logic").__dict__, "independent_context": False}
        )
        decision = evaluate_gate("candidate_disproved", [review])
        self.assertEqual(decision.status, "candidate_rejected")
        self.assertTrue(any("not independent" in reason for reason in decision.reasons))

    def test_rejects_wrong_statement_attestation(self):
        reviews = [passing_review(role) for role in REQUIRED_TEST_ROLES]
        decision = evaluate_gate(
            "candidate_proved", reviews, expected_statement_sha256="expected"
        )
        self.assertEqual(decision.status, "candidate_rejected")
        self.assertTrue(any("immutable statement" in reason for reason in decision.reasons))

    def test_candidate_parser_never_returns_verified_status(self):
        response = "<result>\nOUTCOME: CANDIDATE_PROVED\n</result>"
        self.assertEqual(candidate_status(response), "candidate_proved")

    def test_candidate_contract_fails_closed_on_missing_claim_ledger(self):
        contract = candidate_contract(
            "OUTCOME: CANDIDATE_PROVED\nOPEN_GAPS: NONE\nUNCHECKED_IMPORTS: NONE"
        )
        self.assertFalse(contract.valid_for_promotion)

    def test_candidate_parser_ignores_prose_and_rejects_multiple_blocks(self):
        disproved = """Prose mentions OUTCOME: CANDIDATE_PROVED.
<result>
OUTCOME: CANDIDATE_DISPROVED
</result>"""
        self.assertEqual(candidate_status(disproved), "candidate_disproved")
        contradictory = disproved + "\n<result>\nOUTCOME: CANDIDATE_PROVED\n</result>"
        self.assertEqual(candidate_status(contradictory), "candidate_unclassified")

    def test_missing_gap_fields_and_external_evidence_fail_closed(self):
        response = """<result>
OUTCOME: CANDIDATE_PROVED
COMPLETENESS_SCORE: 100
PROOF_CONFIDENCE: 100
ADVERSARIAL_SURVIVAL_SCORE: 100
CLAIMS_CHECKED: 1
CLAIMS_TOTAL: 1
CLAIM_IDS: C1
</result>"""
        self.assertFalse(candidate_contract(response).valid_for_promotion)
        reviews = [passing_review(role) for role in REQUIRED_TEST_ROLES]
        decision = evaluate_gate("candidate_proved", reviews)
        self.assertIn(
            "no trusted external or mechanical verification evidence",
            decision.reasons,
        )

    def test_adjudicator_must_agree_with_outcome(self):
        reviews = [passing_review(role) for role in REQUIRED_TEST_ROLES]
        reviews[-1] = Review(
            **{**reviews[-1].__dict__, "adjudicated_outcome": "disproved"}
        )
        decision = evaluate_gate(
            "candidate_proved", reviews, verification_evidence=[passing_evidence()]
        )
        self.assertTrue(any("outcome does not match" in r for r in decision.reasons))


if __name__ == "__main__":
    unittest.main()
