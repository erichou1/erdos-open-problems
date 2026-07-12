import json
import tempfile
import unittest
from pathlib import Path

from aristotle_verifier import (
    AristotleResult,
    parse_aristotle_response,
    verify_run,
    write_formal_proof_evidence,
)
from run_verified_pipeline import load_evidence


def make_run(run_dir: Path, *, candidate_outcome: str = "candidate_proved",
             statement_sha: str = "a" * 64) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "candidate.md").write_text("# candidate\nbody", encoding="utf-8")
    (run_dir / "problem.txt").write_text("Is it true that P?", encoding="utf-8")
    (run_dir / "manifest.json").write_text(json.dumps({
        "problem_number": 137,
        "candidate_outcome": candidate_outcome,
        "statement_sha256": statement_sha,
    }), encoding="utf-8")


class FakeClient:
    def __init__(self, result: AristotleResult):
        self._result = result
        self.calls: list[str] = []

    def prove(self, statement: str) -> AristotleResult:
        self.calls.append(statement)
        return self._result


PROVED = AristotleResult(
    verified=True, verdict="proved",
    lean_source="theorem p : True := trivial",
    formal_statement="theorem p : True", raw={"verified": True},
)


class ParseTests(unittest.TestCase):
    def test_proved_with_lean_is_verified(self):
        result = parse_aristotle_response(
            {"verified": True, "lean": "theorem t : True := trivial", "outcome": "proved"})
        self.assertTrue(result.verified)
        self.assertEqual(result.verdict, "proved")

    def test_verified_flag_without_lean_is_not_trusted(self):
        result = parse_aristotle_response({"verified": True})
        self.assertFalse(result.verified)

    def test_disproved_mapping(self):
        result = parse_aristotle_response(
            {"result": "disproved", "lean_code": "example : ¬ P := ..."})
        self.assertEqual(result.verdict, "disproved")


class EvidenceTests(unittest.TestCase):
    def test_passed_when_aristotle_agrees_with_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            make_run(run, candidate_outcome="candidate_proved")
            evidence_path = write_formal_proof_evidence(run, PROVED)
            record = json.loads(evidence_path.read_text())[0]
            self.assertEqual(record["kind"], "formal_proof")
            self.assertEqual(record["verifier"], "aristotle")
            self.assertEqual(record["outcome"], "candidate_proved")
            self.assertTrue(record["passed"])
            self.assertTrue((run / "aristotle" / "proof.lean").is_file())

    def test_failed_when_aristotle_contradicts_candidate(self):
        disproved = AristotleResult(True, "disproved", "example : ¬P := by sorry",
                                    "theorem", {"result": "disproved"})
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            make_run(run, candidate_outcome="candidate_proved")
            record = json.loads(write_formal_proof_evidence(run, disproved).read_text())[0]
            self.assertFalse(record["passed"])
            self.assertFalse(record["aristotle_agrees_with_candidate"])

    def test_failed_when_unverified(self):
        unverified = AristotleResult(False, "unknown", "", "", {})
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            make_run(run)
            record = json.loads(write_formal_proof_evidence(run, unverified).read_text())[0]
            self.assertFalse(record["passed"])

    def test_emitted_evidence_is_consumable_by_the_gate_loader(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            make_run(run, statement_sha="b" * 64)
            evidence_path = write_formal_proof_evidence(run, PROVED)
            evidence = load_evidence(evidence_path)
            self.assertEqual(len(evidence), 1)
            item = evidence[0]
            self.assertEqual(item.kind, "formal_proof")
            self.assertEqual(item.outcome, "candidate_proved")
            self.assertTrue(item.passed)
            self.assertRegex(item.artifact_sha256, r"^[0-9a-f]{64}$")
            self.assertEqual(item.statement_sha256, "b" * 64)


class VerifyRunTests(unittest.TestCase):
    def test_verify_run_uses_injected_client_and_writes_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            make_run(run)
            client = FakeClient(PROVED)
            result, evidence_path, promoted = verify_run(run, client=client)
            self.assertEqual(result.verdict, "proved")
            self.assertEqual(client.calls, ["Is it true that P?"])
            self.assertTrue(evidence_path.is_file())
            self.assertIsNone(promoted)


if __name__ == "__main__":
    unittest.main()
