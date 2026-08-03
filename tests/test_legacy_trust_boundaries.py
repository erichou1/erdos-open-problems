"""Adversarial regressions for the pre-EGMRA proof-promotion entry points."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from egmra.policy import PolicyEnforcer, sign_policy
from promote_verified_run import promote
from run_verified_pipeline import inspect_evidence, load_evidence
from verification import (
    MaterializedVerificationEvidence,
    REQUIRED_ROLES,
    Review,
    VerificationEvidence,
    candidate_contract,
    evaluate_gate,
    sign_review,
    sign_verification_evidence,
)


REVIEW_ENV = {"EGMRA_LEGACY_REVIEW_KEY": "review-boundary-test-key-at-least-32-bytes"}
EVIDENCE_ENV = {
    "EGMRA_LEGACY_EVIDENCE_KEY": "evidence-boundary-test-key-at-least-32-bytes"
}
TRUST_ENV = REVIEW_ENV | EVIDENCE_ENV
POLICY_ENV = {"EGMRA_POLICY_KEY": "policy-boundary-test-key-at-least-32-bytes"}
RUN_ID = "20260713T000000Z-audit001"
RUN_CONTRACT_ID = "f" * 64
RUN_CONTEXT_ID = "9" * 64


def _candidate_contract():
    return candidate_contract("""<result>
OUTCOME: CANDIDATE_PROVED
COMPLETENESS_SCORE: 100
PROOF_CONFIDENCE: 100
ADVERSARIAL_SURVIVAL_SCORE: 100
OPEN_GAPS: NONE
UNCHECKED_IMPORTS: NONE
CLAIMS_CHECKED: 1
CLAIMS_TOTAL: 1
CLAIM_IDS: C1
</result>""")


def _loader_enforcer() -> PolicyEnforcer:
    return PolicyEnforcer(
        sign_policy({"automated_external_evidence": True}, env=POLICY_ENV),
        verification_env=POLICY_ENV,
    )


def _review(role: str, *, lineage: str | None = None) -> Review:
    review = Review(
        reviewer_id=f"reviewer-{role}",
        reviewer_role=role,
        independent_context=True,
        verdict="pass",
        claims_checked=1,
        claims_total=1,
        checked_claim_ids=("C1",),
        completeness_score=100,
        proof_confidence=100,
        adversarial_survival_score=100,
        adjudicated_outcome="proved" if role == "adjudicator" else "",
        context_id=f"context-{role}",
        statement_sha256="a" * 64,
        candidate_sha256="b" * 64,
        authority_id=f"authority-{role}",
        model_provider="test-provider",
        model_name=f"model-{role}",
        model_version="immutable-v1",
        model_lineage=lineage or f"lineage-{role}",
        problem_number=1,
        run_contract_id=RUN_CONTRACT_ID,
        execution_id=RUN_ID,
        run_context_id=RUN_CONTEXT_ID,
    )
    return sign_review(review, env=REVIEW_ENV)


def _evidence(*, kind: str = "exact_computation") -> VerificationEvidence:
    evidence = VerificationEvidence(
        kind=kind,
        verifier="egmra-compute-replay",
        outcome="candidate_proved",
        statement_sha256="a" * 64,
        candidate_sha256="b" * 64,
        artifact_sha256="c" * 64,
        passed=True,
        verification_method="independent_exact_replay",
        validator_id="egmra.compute.exact-replay/v1",
        certificate_sha256="c" * 64,
        scope_sha256="a" * 64,
        coverage="complete",
        statement_fidelity="exact_scope_bound",
        problem_number=1,
        run_contract_id=RUN_CONTRACT_ID,
        execution_id=RUN_ID,
        run_context_id=RUN_CONTEXT_ID,
    )
    if kind == "expert_review":
        evidence = dataclasses.replace(
            evidence,
            verifier="expert",
            verification_method="authenticated_expert_review",
            validator_id="egmra.review.identity/v1",
            statement_fidelity="reviewed",
        )
    return sign_verification_evidence(evidence, env=EVIDENCE_ENV)


class LegacyTrustBoundaryTests(unittest.TestCase):
    def test_shipped_evidence_example_matches_closed_loader_schema(self):
        inspection = inspect_evidence(
            Path(__file__).resolve().parents[1] / "verification-evidence.example.json",
            enforcer=_loader_enforcer(),
        )
        self.assertEqual(inspection.kinds, frozenset({"exact_computation"}))

    def test_caller_forged_reviews_and_evidence_cannot_promote(self):
        reviews = [dataclasses.replace(_review(role), attestation="0" * 64)
                   for role in REQUIRED_ROLES]
        evidence = dataclasses.replace(_evidence(), attestation="0" * 64)
        decision = evaluate_gate(
            "candidate_proved", reviews, verification_evidence=[evidence],
            attestation_env=TRUST_ENV,
        )
        self.assertEqual(decision.status, "candidate_rejected")
        self.assertTrue(any("attestation" in reason for reason in decision.reasons))

    def test_authenticated_metadata_without_loaded_artifact_cannot_satisfy_gate(self):
        decision = evaluate_gate(
            "candidate_proved",
            [_review(role) for role in REQUIRED_ROLES],
            verification_evidence=[_evidence()],
            expected_statement_sha256="a" * 64,
            expected_candidate_sha256="b" * 64,
            candidate_contract=_candidate_contract(),
            expected_problem_number=1,
            expected_run_contract_id=RUN_CONTRACT_ID,
            expected_execution_id=RUN_ID,
            expected_run_context_id=RUN_CONTEXT_ID,
            attestation_env=TRUST_ENV,
        )
        self.assertEqual(decision.status, "candidate_rejected")
        self.assertIn(
            "no trusted external or mechanical verification evidence",
            decision.reasons,
        )

    def test_claimed_materialization_hash_is_recomputed_from_actual_bytes(self):
        evidence = _evidence()
        forged_bundle = MaterializedVerificationEvidence(
            [evidence], {evidence.artifact_sha256: b"not the signed artifact"},
        )
        decision = evaluate_gate(
            "candidate_proved", [_review(role) for role in REQUIRED_ROLES],
            verification_evidence=forged_bundle,
            expected_statement_sha256="a" * 64,
            expected_candidate_sha256="b" * 64,
            candidate_contract=_candidate_contract(),
            expected_problem_number=1,
            expected_run_contract_id=RUN_CONTRACT_ID,
            expected_execution_id=RUN_ID,
            expected_run_context_id=RUN_CONTEXT_ID,
            attestation_env=TRUST_ENV,
        )
        self.assertEqual(decision.status, "candidate_rejected")

    def test_hardened_formal_truth_is_not_overruled_by_model_dissent(self):
        artifact = b"authenticated hardened proof certificate"
        digest = hashlib.sha256(artifact).hexdigest()
        formal = sign_verification_evidence(VerificationEvidence(
            kind="formal_proof", verifier="independent-kernel",
            outcome="candidate_proved", statement_sha256="a" * 64,
            candidate_sha256="b" * 64, artifact_sha256=digest, passed=True,
            verification_method="hardened_independent_kernel_replay",
            validator_id="egmra.lean.hardened-kernel/v1",
            certificate_sha256=digest, scope_sha256="a" * 64,
            coverage="complete", statement_fidelity="approved_i2_f2",
            problem_number=1, run_contract_id=RUN_CONTRACT_ID,
            execution_id=RUN_ID, run_context_id=RUN_CONTEXT_ID,
        ), env=EVIDENCE_ENV)
        reviews = [_review(role) for role in REQUIRED_ROLES]
        reviews[-1] = sign_review(dataclasses.replace(
            reviews[-1], verdict="fail", material_errors=("model dissent",),
            attestor_key_id="", attestation="",
        ), env=REVIEW_ENV)
        decision = evaluate_gate(
            "candidate_proved", reviews,
            verification_evidence=MaterializedVerificationEvidence(
                [formal], {digest: artifact},
            ),
            expected_statement_sha256="a" * 64,
            expected_candidate_sha256="b" * 64,
            candidate_contract=_candidate_contract(),
            expected_problem_number=1,
            expected_run_contract_id=RUN_CONTRACT_ID,
            expected_execution_id=RUN_ID,
            expected_run_context_id=RUN_CONTEXT_ID,
            attestation_env=TRUST_ENV,
        )
        self.assertEqual(decision.status, "awaiting_authenticated_release")

    def test_gate_cannot_verify_when_caller_omits_canonical_anchors(self):
        decision = evaluate_gate(
            "candidate_proved", [_review(role) for role in REQUIRED_ROLES],
            verification_evidence=[_evidence()], attestation_env=TRUST_ENV,
        )
        self.assertEqual(decision.status, "candidate_rejected")
        self.assertTrue(any("canonical" in reason or "contract" in reason
                            for reason in decision.reasons))

    def test_expert_approval_is_not_truth_evidence_even_when_authenticated(self):
        with self.assertRaises(ValueError):
            _evidence(kind="expert_review")

    def test_same_model_lineage_does_not_count_as_independent(self):
        reviews = [_review(role, lineage="same-correlated-model") for role in REQUIRED_ROLES]
        decision = evaluate_gate(
            "candidate_proved", reviews, verification_evidence=[_evidence()],
            attestation_env=TRUST_ENV,
        )
        self.assertEqual(decision.status, "candidate_rejected")
        self.assertTrue(any("model lineage" in reason for reason in decision.reasons))

    def test_individually_valid_receipts_cannot_be_mixed_across_candidates(self):
        other = sign_verification_evidence(
            dataclasses.replace(_evidence(), candidate_sha256="e" * 64,
                                attestor_key_id="", attestation=""),
            env=EVIDENCE_ENV,
        )
        decision = evaluate_gate(
            "candidate_proved", [_review(role) for role in REQUIRED_ROLES],
            verification_evidence=[other], attestation_env=TRUST_ENV,
        )
        self.assertEqual(decision.status, "candidate_rejected")
        self.assertTrue(any("candidate bindings disagree" in reason
                            for reason in decision.reasons))

    def test_post_signature_mutation_is_detected(self):
        review = dataclasses.replace(_review("logic"), verdict="fail")
        evidence = dataclasses.replace(_evidence(), coverage="sampled")
        others = [_review(role) for role in REQUIRED_ROLES if role != "logic"]
        decision = evaluate_gate(
            "candidate_proved", [*others, review], verification_evidence=[evidence],
            attestation_env=TRUST_ENV,
        )
        self.assertTrue(any("attestation" in reason for reason in decision.reasons))
        self.assertTrue(any("mechanical verification evidence" in reason
                            for reason in decision.reasons))

    def test_disabled_policy_is_checked_before_attacker_controlled_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()
            (run / "manifest.json").write_text(json.dumps({
                "problem_number": 1,
                "candidate_outcome": "candidate_proved",
                "statement_sha256": "a" * 64,
                "reviews": [],
            }), encoding="utf-8")
            (run / "candidate.md").write_text("candidate", encoding="utf-8")
            evidence = Path(directory) / "attacker.json"
            evidence.write_text("not json", encoding="utf-8")
            enforcer = PolicyEnforcer(
                sign_policy({"promotion": False}, env=POLICY_ENV),
                verification_env=POLICY_ENV,
            )
            with mock.patch("promote_verified_run.load_evidence",
                            side_effect=AssertionError("evidence was touched")) as loader:
                result = promote(
                    run, evidence, publish=False, category="open", enforcer=enforcer,
                    attestation_env=TRUST_ENV,
                )
            self.assertEqual(result.gate.status, "promotion_disabled_by_policy")
            loader.assert_not_called()

    def test_disabled_policy_precedes_even_manifest_reads(self):
        enforcer = PolicyEnforcer(
            sign_policy({"promotion": False}, env=POLICY_ENV),
            verification_env=POLICY_ENV,
        )
        with mock.patch(
            "promote_verified_run._read_regular_file",
            side_effect=AssertionError("run bytes were touched"),
        ) as reader:
            result = promote(
                Path("attacker-run"), Path("attacker-evidence"),
                publish=False, category="open", enforcer=enforcer,
            )
        self.assertEqual(result.gate.status, "promotion_disabled_by_policy")
        reader.assert_not_called()

    def test_formal_policy_is_checked_before_artifact_loader(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "problem_1" / RUN_ID
            run.mkdir(parents=True)
            (run / "manifest.json").write_text(json.dumps({
                "problem_number": 1,
                "candidate_outcome": "candidate_proved",
            }), encoding="utf-8")
            formal_record = dataclasses.asdict(VerificationEvidence(
                kind="formal_proof", verifier="quarantine", outcome="candidate_proved",
                statement_sha256="a" * 64, candidate_sha256="b" * 64,
                artifact_sha256="c" * 64, passed=False,
                verification_method="untrusted", validator_id="untrusted",
                certificate_sha256="c" * 64, scope_sha256="a" * 64,
                coverage="encoded_theorem_only", statement_fidelity="unreviewed",
                problem_number=1, run_contract_id=RUN_CONTRACT_ID,
                execution_id=RUN_ID, run_context_id=RUN_CONTEXT_ID,
            ))
            formal_record["artifact_path"] = "must-not-open.lean"
            evidence_path = root / "formal.json"
            evidence_path.write_text(json.dumps([formal_record]), encoding="utf-8")
            enforcer = PolicyEnforcer(sign_policy({
                "promotion": True,
                "formal_promotion": False,
                "automated_external_evidence": True,
            }, env=POLICY_ENV), verification_env=POLICY_ENV)
            with mock.patch(
                "promote_verified_run._validated_run_candidate",
                return_value="candidate",
            ), mock.patch(
                "promote_verified_run.load_evidence",
                side_effect=AssertionError("formal artifact loader was called"),
            ) as loader:
                result = promote(
                    run, evidence_path, publish=False, category="open",
                    enforcer=enforcer,
                )
            self.assertEqual(result.gate.status, "promotion_disabled_by_policy")
            loader.assert_not_called()

    def test_evidence_loader_rejects_symlink_escape_duplicate_keys_and_hash_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "artifact.txt"
            artifact.write_text("certificate", encoding="utf-8")
            link = root / "link.txt"
            link.symlink_to(artifact)

            record = dataclasses.asdict(_evidence())
            record["artifact_path"] = "link.txt"
            path = root / "evidence.json"
            path.write_text(json.dumps([record]), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_evidence(
                    path, enforcer=_loader_enforcer(), attestation_env=TRUST_ENV,
                )

            record["artifact_path"] = "artifact.txt"
            record["artifact_sha256"] = hashlib.sha256(b"different").hexdigest()
            path.write_text(json.dumps([record]), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_evidence(
                    path, enforcer=_loader_enforcer(), attestation_env=TRUST_ENV,
                )

            path.write_text('[{"kind":"a","kind":"b"}]', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_evidence(
                    path, enforcer=_loader_enforcer(), attestation_env=TRUST_ENV,
                )

    def test_evidence_loader_rejects_fake_policy_fifo_and_record_flood(self):
        class FakeEnforcer:
            def require(self, *args, **kwargs):
                return None

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "evidence.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaises(TypeError):
                load_evidence(path, enforcer=FakeEnforcer())

            if hasattr(os, "mkfifo"):
                fifo = root / "certificate.fifo"
                os.mkfifo(fifo)
                record = dataclasses.asdict(_evidence())
                record["artifact_path"] = fifo.name
                path.write_text(json.dumps([record]), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_evidence(
                        path, enforcer=_loader_enforcer(),
                        attestation_env=TRUST_ENV,
                    )

            record = dataclasses.asdict(_evidence())
            record["artifact_path"] = "missing.txt"
            path.write_text(
                json.dumps([record for _ in range(33)]), encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "record limit"):
                load_evidence(
                    path, enforcer=_loader_enforcer(), attestation_env=TRUST_ENV,
                )


if __name__ == "__main__":
    unittest.main()
