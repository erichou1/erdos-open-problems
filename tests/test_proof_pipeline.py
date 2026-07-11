import json
import hashlib
import re
import tempfile
import unittest
from pathlib import Path

from proof_pipeline import ProofPipeline
from promote_verified_run import promote
from research_state import make_statement_lock
from verification import VerificationEvidence


def candidate_result():
    return """<result>
OUTCOME: CANDIDATE_PROVED
COMPLETENESS_SCORE: 100
PROOF_CONFIDENCE: 99
ADVERSARIAL_SURVIVAL_SCORE: 99
OPEN_GAPS: NONE
UNCHECKED_IMPORTS: NONE
CLAIMS_CHECKED: 7
CLAIMS_TOTAL: 7
CLAIM_IDS: C1; C2; C3; C4; C5; C6; C7
</result>"""


def evidence_for(problem):
    return (VerificationEvidence(
        kind="exact_computation",
        verifier="test-checker",
        outcome="candidate_proved",
        statement_sha256=make_statement_lock(problem).sha256,
        candidate_sha256=hashlib.sha256(candidate_result().encode("utf-8")).hexdigest(),
        artifact_sha256="c" * 64,
        passed=True,
    ),)


class PassingRunner:
    def __init__(self):
        self.calls = []

    def context_id(self, stage):
        return f"fake-context-{stage}"

    def run(self, prompt, *, stage, isolated):
        self.calls.append((stage, isolated, prompt))
        if stage == "synthesis":
            return json.dumps({
                "summary": "prove the base claim, then the goal",
                "bottleneck_ids": ["L1"],
                "subgoals": [
                    {"id": "L1", "claim": "base claim", "dependencies": [], "centrality": 5, "falsifiable": True},
                    {"id": "GOAL", "claim": "original theorem", "dependencies": ["L1"], "centrality": 5, "falsifiable": True},
                ],
            })
        if stage.startswith("regulator_"):
            return json.dumps({
                "decision": "REVISE_PROOF",
                "rationale": "the plan remains sound",
                "broken_node_ids": [],
                "new_constraints": ["remove circularity"],
            })
        if stage == "construction":
            return candidate_result()
        if stage.startswith("review_") or stage.startswith("adjudication_"):
            role = (
                stage.removeprefix("review_").rsplit("_", 1)[0]
                if stage.startswith("review_") else "adjudicator"
            )
            return json.dumps({
                "reviewer_role": role,
                "verdict": "pass",
                "claims_checked": 7,
                "claims_total": 7,
                "checked_claim_ids": [f"C{i}" for i in range(1, 8)],
                "open_gaps": [],
                "unchecked_imports": [],
                "material_errors": [],
                "statement_sha256": re.search(
                    r"STATEMENT_SHA256: ([0-9a-f]{64})", prompt
                ).group(1),
                "completeness_score": 100,
                "proof_confidence": 99,
                "adversarial_survival_score": 99,
                "outcome": "proved",
            })
        return f"output for {stage}"


class ProofPipelineTests(unittest.TestCase):
    def test_runs_isolated_stages_and_persists_gate_evidence(self):
        runner = PassingRunner()
        with tempfile.TemporaryDirectory() as directory:
            problem = "For every n, prove P(n)."
            result = ProofPipeline(
                runner, Path(directory), verification_evidence=evidence_for(problem)
            ).solve(1, problem)
            self.assertEqual(result.gate.status, "verified_proved")
            self.assertTrue((result.artifact_dir / "manifest.json").exists())
        self.assertEqual(len(runner.calls), 14)
        self.assertTrue(all(isolated for _, isolated, _ in runner.calls))
        self.assertTrue(all("Do not browse" in prompt for _, _, prompt in runner.calls))

    def test_revises_after_rejection_and_keeps_failure_memory(self):
        class RevisingRunner(PassingRunner):
            def run(self, prompt, *, stage, isolated):
                response = super().run(prompt, stage=stage, isolated=isolated)
                if stage == "review_logic_1":
                    data = json.loads(response)
                    data["verdict"] = "fail"
                    data["material_errors"] = ["L1 assumes the conclusion"]
                    return json.dumps(data)
                if stage == "revision_1":
                    return candidate_result()
                return response

        runner = RevisingRunner()
        with tempfile.TemporaryDirectory() as directory:
            problem = "Prove Q."
            result = ProofPipeline(
                runner, Path(directory), max_revisions=1,
                verification_evidence=evidence_for(problem),
            ).solve(2, problem)
            state = json.loads((result.artifact_dir / "research_state.json").read_text())
            self.assertEqual(result.gate.status, "verified_proved")
            self.assertEqual(len(state["attempts"]), 2)
            self.assertIn("assumes the conclusion", state["failed_approaches"][0]["obstructions"][0])

    def test_repeated_runs_use_distinct_audit_directories(self):
        runner = PassingRunner()
        problem = "Prove R."
        with tempfile.TemporaryDirectory() as directory:
            pipeline = ProofPipeline(
                runner, Path(directory), verification_evidence=evidence_for(problem)
            )
            first = pipeline.solve(3, problem)
            second = pipeline.solve(3, problem)
            self.assertNotEqual(first.artifact_dir, second.artifact_dir)
            self.assertTrue(first.artifact_dir.exists())
            self.assertTrue(second.artifact_dir.exists())

    def test_malformed_review_rejects_without_aborting(self):
        class MalformedRunner(PassingRunner):
            def run(self, prompt, *, stage, isolated):
                if stage == "review_logic_1":
                    self.calls.append((stage, isolated, prompt))
                    return '{"reviewer_role":"logic","claims_checked":"all"}'
                return super().run(prompt, stage=stage, isolated=isolated)

        problem = "Prove S."
        with tempfile.TemporaryDirectory() as directory:
            result = ProofPipeline(
                MalformedRunner(), Path(directory), max_revisions=0,
                verification_evidence=evidence_for(problem),
            ).solve(4, problem)
            self.assertEqual(result.gate.status, "candidate_rejected")
            self.assertTrue((result.artifact_dir / "manifest.json").exists())

    def test_malformed_replan_continues_with_last_valid_graph(self):
        class MalformedReplanRunner(PassingRunner):
            def run(self, prompt, *, stage, isolated):
                if stage == "review_logic_1":
                    data = json.loads(super().run(prompt, stage=stage, isolated=isolated))
                    data["verdict"] = "fail"
                    data["material_errors"] = ["L1 is unsupported"]
                    return json.dumps(data)
                if stage == "regulator_1":
                    return json.dumps({
                        "decision": "REVISE_PLAN",
                        "rationale": "replace L1",
                        "broken_node_ids": ["L1"],
                        "new_constraints": ["supply evidence"],
                    })
                if stage == "replan_1":
                    return '{"summary": "unterminated"'
                return super().run(prompt, stage=stage, isolated=isolated)

        problem = "Prove U."
        with tempfile.TemporaryDirectory() as directory:
            result = ProofPipeline(
                MalformedReplanRunner(), Path(directory), max_revisions=1,
                verification_evidence=evidence_for(problem),
            ).solve(6, problem)
            self.assertTrue((result.artifact_dir / "manifest.json").exists())
            self.assertTrue((result.artifact_dir / "attempt_1" / "replan_error.txt").exists())

    def test_external_evidence_promotes_existing_run_and_publishes(self):
        runner = PassingRunner()
        problem = "Prove T."
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            result = ProofPipeline(
                runner, base / "runs"
            ).solve(5, problem)
            self.assertEqual(result.gate.status, "awaiting_external_evidence")
            artifact = base / "expert-review.txt"
            artifact.write_text("independent expert approval", encoding="utf-8")
            candidate = (result.artifact_dir / "candidate.md").read_text()
            evidence_path = base / "evidence.json"
            evidence_path.write_text(json.dumps([{
                "kind": "expert_review",
                "verifier": "test expert",
                "outcome": "candidate_proved",
                "statement_sha256": make_statement_lock(problem).sha256,
                "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
                "artifact_path": str(artifact),
                "passed": True,
            }]))
            promoted = promote(
                result.artifact_dir, evidence_path, publish=True,
                category="open", base_dir=base,
            )
            self.assertEqual(promoted.gate.status, "verified_proved")
            output = next((base / "outputs" / "chatgpt" / "open").glob("*.md"))
            self.assertIn("[verified-proved]", output.name)
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
