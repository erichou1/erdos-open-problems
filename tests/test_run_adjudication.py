import hashlib
import json
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

import run_adjudication as A
from proof_pipeline import REVIEW_MANDATES
from research_state import make_statement_lock

PROBLEM = "Prove that every even integer > 2 is a sum of two primes."
CANDIDATE = """<result>
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
CLAIM_IDS = [f"C{i}" for i in range(1, 8)]


def _review_dict(role, sha, reviewer_id, context_id):
    return {
        "reviewer_id": reviewer_id,
        "reviewer_role": role,
        "independent_context": True,
        "verdict": "pass",
        "claims_checked": 7,
        "claims_total": 7,
        "checked_claim_ids": list(CLAIM_IDS),
        "open_gaps": [],
        "unchecked_imports": [],
        "material_errors": [],
        "statement_sha256": sha,
        "completeness_score": 100,
        "proof_confidence": 99,
        "adversarial_survival_score": 99,
        "adjudicated_outcome": "proved",
        "context_id": context_id,
    }


def _adjudicator_json(sha, *, verdict="pass", **override):
    data = {
        "reviewer_role": "adjudicator",
        "verdict": verdict,
        "outcome": "proved",
        "claims_checked": 7,
        "claims_total": 7,
        "checked_claim_ids": list(CLAIM_IDS),
        "open_gaps": [],
        "unchecked_imports": [],
        "material_errors": [],
        "completeness_score": 100,
        "proof_confidence": 99,
        "adversarial_survival_score": 99,
        "statement_sha256": sha,
        "notes": "checked",
    }
    data.update(override)
    return json.dumps(data)


class FakeRunner:
    def __init__(self, response, context="https://chat.deepseek.com/a/chat/s/zz9"):
        self._response = response
        self._context = context
        self.calls = []

    def run(self, prompt, *, stage, isolated):
        self.calls.append((stage, isolated, prompt))
        return self._response

    def context_id(self, stage):
        return self._context

    def restore_context(self, stage, context_id):
        self._context = context_id


def make_run(artifacts: Path, problem_number: int = 7) -> tuple[Path, str]:
    lock = make_statement_lock(PROBLEM)
    sha = lock.sha256
    run_dir = artifacts / f"problem_{problem_number}" / "20260101T000000Z-abcd1234"
    (run_dir / "attempt_1").mkdir(parents=True)
    (run_dir / "candidate.md").write_text(CANDIDATE, encoding="utf-8")
    (run_dir / "statement_lock.json").write_text(json.dumps(asdict(lock)), encoding="utf-8")
    (run_dir / "subgoal_graph.json").write_text('{"nodes": []}', encoding="utf-8")
    for role in REVIEW_MANDATES:
        (run_dir / "attempt_1" / f"review_{role}.json").write_text(
            json.dumps({"reviewer_role": role, "verdict": "pass"}), encoding="utf-8"
        )
    reviews = [
        _review_dict(role, sha, f"{role}-1", f"https://chat.openai.com/{role}")
        for role in REVIEW_MANDATES
    ]
    reviews.append(_review_dict("adjudicator", sha, "adjudicator-1",
                                "https://chat.openai.com/adjudicator"))
    manifest = {
        "problem_number": problem_number,
        "candidate_outcome": "candidate_proved",
        "statement_sha256": sha,
        "candidate_sha256": hashlib.sha256(CANDIDATE.encode("utf-8")).hexdigest(),
        "verification_evidence": [],
        "reviews": reviews,
        "gate": {"status": A.AWAITING, "reasons": list(A.ONLY_EVIDENCE_MISSING)},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return run_dir, sha


class RunAdjudicationTests(unittest.TestCase):
    def test_agreement_keeps_run_awaiting(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir, sha = make_run(Path(directory))
            record = A.adjudicate_run(run_dir, FakeRunner(_adjudicator_json(sha)))
            self.assertTrue(record["agrees"])
            self.assertFalse(record["malformed"])
            self.assertEqual(record["gate_after"], A.AWAITING)
            # artifact + manifest updated
            self.assertTrue((run_dir / A.ADJ_FILE).exists())
            manifest = json.loads((run_dir / "manifest.json").read_text())
            self.assertEqual(manifest["gate"]["status"], A.AWAITING)
            self.assertTrue(manifest["adjudicator_distinct_model"])
            roles = {r["reviewer_id"] for r in manifest["reviews"]}
            self.assertIn("adjudicator-deepseek", roles)
            self.assertNotIn("adjudicator-1", roles)

    def test_dissent_rejects_the_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir, sha = make_run(Path(directory))
            runner = FakeRunner(_adjudicator_json(
                sha, verdict="fail", material_errors=["gap in lemma 3"]))
            record = A.adjudicate_run(run_dir, runner)
            self.assertFalse(record["agrees"])
            self.assertEqual(record["gate_after"], "candidate_rejected")
            manifest = json.loads((run_dir / "manifest.json").read_text())
            self.assertEqual(manifest["gate"]["status"], "candidate_rejected")

    def test_malformed_output_is_advisory_only(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir, _sha = make_run(Path(directory))
            record = A.adjudicate_run(run_dir, FakeRunner("not json at all"))
            self.assertTrue(record["malformed"])
            self.assertFalse(record["agrees"])
            # gate must be left untouched on a distinct-model formatting failure
            self.assertEqual(record["gate_after"], A.AWAITING)
            manifest = json.loads((run_dir / "manifest.json").read_text())
            self.assertEqual(manifest["gate"]["status"], A.AWAITING)
            self.assertNotIn("adjudicator_distinct_model", manifest)

    def test_advisory_only_never_touches_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir, sha = make_run(Path(directory))
            runner = FakeRunner(_adjudicator_json(sha, verdict="fail"))
            record = A.adjudicate_run(run_dir, runner, apply_gate=False)
            self.assertFalse(record["agrees"])
            self.assertEqual(record["gate_after"], A.AWAITING)
            manifest = json.loads((run_dir / "manifest.json").read_text())
            self.assertEqual(manifest["gate"]["status"], A.AWAITING)

    def test_prompt_contains_statement_candidate_and_reviews(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir, sha = make_run(Path(directory))
            prompt = A.build_adjudicator_prompt(run_dir)
            self.assertIn(sha, prompt)
            self.assertIn("CANDIDATE_PROVED", prompt)
            self.assertIn("structural_dependency", prompt)

    def test_find_adjudicatable_runs_skips_already_done(self):
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            run_dir, _sha = make_run(artifacts)
            self.assertEqual(A.find_adjudicatable_runs(artifacts), [run_dir])
            (run_dir / A.ADJ_FILE).write_text("{}", encoding="utf-8")
            self.assertEqual(A.find_adjudicatable_runs(artifacts), [])


if __name__ == "__main__":
    unittest.main()
