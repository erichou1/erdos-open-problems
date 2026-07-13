import json
import tempfile
import unittest
from pathlib import Path

from novelty_probe import probe_novelty


def setup_repo(root: Path, catalog: dict, forum: dict | None = None) -> None:
    (root / "forum_threads").mkdir(parents=True, exist_ok=True)
    (root / "problem_catalog.json").write_text(
        json.dumps({"problems": catalog}), encoding="utf-8")
    for number, comments in (forum or {}).items():
        (root / "forum_threads" / f"{number}.json").write_text(json.dumps({
            "comment_count": len(comments),
            "comments": [{"text": c} for c in comments],
        }), encoding="utf-8")


class NoveltyTests(unittest.TestCase):
    def test_source_resolved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            setup_repo(root, {"1": {"source_state": "open", "source_reports_resolved": True}})
            result = probe_novelty(root, 1)
            self.assertEqual(result["novelty_status"], "source_resolved")
            self.assertFalse(result["is_likely_novel"])

    def test_formalized_is_prior_work(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            setup_repo(root, {"2": {"source_state": "open", "formalized": True}})
            self.assertEqual(probe_novelty(root, 2)["novelty_status"], "prior_work_signal")

    def test_forum_solution_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            setup_repo(root, {"3": {"source_state": "open"}},
                       forum={"3": ["Here is a proof of the problem; it is solved."]})
            result = probe_novelty(root, 3)
            self.assertEqual(result["novelty_status"], "prior_work_signal")
            self.assertIn("solution_claim", result["forum_claim_signals"])

    def test_no_signal_is_likely_novel(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            setup_repo(root, {"4": {"source_state": "open", "source_reports_resolved": False}},
                       forum={"4": ["An interesting remark about the general strategy."]})
            result = probe_novelty(root, 4)
            self.assertEqual(result["novelty_status"], "no_signal")
            self.assertTrue(result["is_likely_novel"])


if __name__ == "__main__":
    unittest.main()
