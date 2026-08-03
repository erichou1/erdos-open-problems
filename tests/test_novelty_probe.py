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

    def test_ai_wiki_full_solution_blocks_novelty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            setup_repo(root, {"5": {
                "source_state": "open",
                "ai_wiki": {"primary_full": True, "sections": ["1(a)"]},
            }})
            result = probe_novelty(root, 5)
            self.assertEqual(result["novelty_status"], "ai_reported_solution")
            self.assertTrue(result["ai_wiki_full_solution"])
            self.assertFalse(result["is_likely_novel"])

    def test_ai_wiki_literature_hit_blocks_novelty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            setup_repo(root, {"6": {
                "source_state": "open",
                "ai_wiki": {"secondary_full": True, "sections": ["2(a)"]},
            }})
            self.assertEqual(
                probe_novelty(root, 6)["novelty_status"], "ai_reported_solution")

    def test_ai_wiki_partial_is_prior_work_signal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            setup_repo(root, {"7": {
                "source_state": "open",
                "ai_wiki": {"primary_partial": True, "sections": ["1(d)"]},
            }})
            result = probe_novelty(root, 7)
            self.assertEqual(result["novelty_status"], "prior_work_signal")
            self.assertTrue(result["ai_wiki_partial"])
            self.assertFalse(result["is_likely_novel"])

    def test_source_resolution_outranks_ai_wiki(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            setup_repo(root, {"8": {
                "source_state": "proved",
                "source_reports_resolved": True,
                "ai_wiki": {"primary_full": True, "sections": ["1(a)"]},
            }})
            self.assertEqual(
                probe_novelty(root, 8)["novelty_status"], "source_resolved")


if __name__ == "__main__":
    unittest.main()
