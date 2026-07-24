import json
import tempfile
import unittest
from pathlib import Path

from run_status import has_verified_result, problem_disposition
from run_sol2_batch import should_skip_problem
from run_verified_range import already_verified


class RunStatusTests(unittest.TestCase):
    def write_manifest(self, root: Path, problem: int, run: str,
                       candidate: str, gate: str,
                       run_contract_id: str = "a" * 64) -> Path:
        run_dir = root / f"problem_{problem}" / run
        run_dir.mkdir(parents=True)
        (run_dir / "manifest.json").write_text(json.dumps({
            "problem_number": problem,
            "candidate_outcome": candidate,
            "run_contract_id": run_contract_id,
            "gate": {"status": gate, "reasons": []},
        }))
        return run_dir

    def test_resource_exhaustion_is_budget_limited_not_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_manifest(
                root, 601, "20260711T160037Z-test",
                "resource_exhausted", "candidate_rejected",
            )
            self.assertFalse(has_verified_result(root, 601))
            self.assertEqual(
                problem_disposition(root, 601)["outcome_class"],
                "no_progress_within_budget",
            )
            marker = root / ".done" / "problem_601"
            marker.parent.mkdir()
            marker.write_text("ok\n")
            self.assertFalse(should_skip_problem(root, 601, marker))
            self.assertFalse(already_verified(root, 601))

    def test_legacy_unclassified_manifest_recovers_bounded_candidate_outcome(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = self.write_manifest(
                root, 601, "20260711T160037Z-test",
                "candidate_unclassified", "candidate_rejected",
            )
            (run_dir / "candidate.md").write_text(
                "<result> OUTCOME: RESOURCE_EXHAUSTED COMPLETENESS_SCORE: 67 "
                "PROOF_CONFIDENCE: 90 ADVERSARIAL_SURVIVAL_SCORE: 84 "
                "OPEN_GAPS: classification UNCHECKED_IMPORTS: NONE "
                "CLAIMS_CHECKED: 1 CLAIMS_TOTAL: 1 CLAIM_IDS: GOAL </result>"
            )
            disposition = problem_disposition(root, 601)
            self.assertEqual(disposition["candidate_outcome"], "resource_exhausted")
            self.assertEqual(disposition["outcome_class"], "no_progress_within_budget")

    def test_forged_verified_manifest_is_quarantined_not_completed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_manifest(
                root, 1, "20260712T000000Z-test",
                "candidate_proved", "verified_proved",
            )
            self.assertFalse(has_verified_result(root, 1))
            self.assertFalse(has_verified_result(
                root, 1, expected_run_contract_id="a" * 64,
            ))
            self.assertFalse(has_verified_result(
                root, 1, expected_run_contract_id="b" * 64,
            ))
            marker = root / ".done" / "problem_1"
            marker.parent.mkdir()
            marker.write_text("verified\n")
            self.assertFalse(should_skip_problem(
                root, 1, marker, expected_run_contract_id="a" * 64,
            ))
            self.assertFalse(should_skip_problem(
                root, 1, marker, expected_run_contract_id="b" * 64,
            ))
            self.assertFalse(already_verified(
                root, 1, expected_run_contract_id="a" * 64,
            ))
            self.assertFalse(already_verified(
                root, 1, expected_run_contract_id="b" * 64,
            ))
            self.assertFalse(problem_disposition(root, 1)["is_negative_training_example"])
            disposition = problem_disposition(root, 1)
            self.assertFalse(disposition["is_verified"])
            self.assertFalse(disposition["is_labeled_outcome"])
            self.assertEqual(disposition["outcome_class"], "operational_failure")

    def test_incomplete_run_is_censored_not_negative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "problem_2" / "20260712T000000Z-test").mkdir(parents=True)
            self.assertFalse(has_verified_result(root, 2))
            self.assertEqual(problem_disposition(root, 2)["outcome_class"],
                             "censored_attempt")

    def test_awaiting_evidence_is_not_mislabeled_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_manifest(
                root, 3, "20260712T000000Z-test",
                "candidate_proved", "awaiting_external_evidence",
            )
            self.assertFalse(has_verified_result(root, 3))
            disposition = problem_disposition(root, 3)
            self.assertEqual(disposition["outcome_class"],
                             "awaiting_external_evidence")
            self.assertFalse(disposition["is_negative_training_example"])

    def test_reviewer_or_schema_failure_is_operational_not_mathematical_negative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = self.write_manifest(
                root, 4, "run1", "candidate_proved", "candidate_rejected",
            )
            disposition = problem_disposition(root, 4)
            self.assertEqual(disposition["outcome_class"], "operational_failure")
            self.assertFalse(disposition["is_negative_training_example"])

            manifest_path = run_dir / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["failure_plane"] = "mathematical"
            manifest["failure_evidence"] = ["counterexample at n=3"]
            manifest_path.write_text(json.dumps(manifest))
            disposition = problem_disposition(root, 4)
            self.assertEqual(
                disposition["outcome_class"], "fundamentally_flawed_candidate"
            )
            self.assertTrue(disposition["is_negative_training_example"])

    def test_symlinked_problem_and_candidate_are_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "artifacts"
            artifacts.mkdir()
            outside = root / "outside"
            run = outside / "run1"
            run.mkdir(parents=True)
            (run / "manifest.json").write_text(json.dumps({
                "problem_number": 9,
                "candidate_outcome": "resource_exhausted",
                "gate": {"status": "candidate_rejected"},
            }))
            (artifacts / "problem_9").symlink_to(outside, target_is_directory=True)
            self.assertEqual(problem_disposition(artifacts, 9)["outcome_class"],
                             "unattempted")

            safe_run = self.write_manifest(
                artifacts, 10, "run1", "candidate_unclassified",
                "candidate_rejected",
            )
            outside_candidate = root / "secret.txt"
            outside_candidate.write_text(
                "<result>OUTCOME: RESOURCE_EXHAUSTED</result>"
            )
            (safe_run / "candidate.md").symlink_to(outside_candidate)
            self.assertEqual(
                problem_disposition(artifacts, 10)["candidate_outcome"],
                "candidate_unclassified",
            )


if __name__ == "__main__":
    unittest.main()
