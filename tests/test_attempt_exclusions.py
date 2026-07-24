import json
import tempfile
import unittest
from pathlib import Path

from erdos_searcher import load_attempt_exclusions


class AttemptExclusionTests(unittest.TestCase):
    def test_loads_problem_numbers_from_objects_ints_and_strings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "attempt_exclusions.json").write_text(json.dumps({
                "excluded": [
                    {"problem": 260, "source": "x"},
                    306,
                    "421",
                    {"problem": True},            # bool ignored
                    {"note": "no problem key"},   # ignored
                ]
            }), encoding="utf-8")
            self.assertEqual(load_attempt_exclusions(root), {260, 306, 421})

    def test_missing_file_returns_empty_set(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_attempt_exclusions(Path(directory)), set())

    def test_malformed_file_returns_empty_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "attempt_exclusions.json").write_text("{not json", encoding="utf-8")
            self.assertEqual(load_attempt_exclusions(root), set())

    def test_repository_exclusions_include_the_known_solved_set(self):
        repo_root = Path(__file__).resolve().parent.parent
        excluded = load_attempt_exclusions(repo_root)
        known = {
            260, 306, 326, 421, 514, 521, 522, 550, 569, 638, 671, 689, 750,
            856, 870, 906, 953, 956, 995, 996, 1005, 1039, 1054, 1133, 1151,
        }
        self.assertTrue(known <= excluded)


if __name__ == "__main__":
    unittest.main()
