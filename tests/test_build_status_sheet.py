import unittest

from build_status_sheet import feed_problem_numbers


class BuildStatusSheetTests(unittest.TestCase):
    def test_current_open_corpus_does_not_reinclude_resolved_output_files(self):
        records = {
            1: {"n": 1, "source_reports_resolved": False},
            2: {"n": 2, "source_reports_resolved": True},
        }
        self.assertEqual(feed_problem_numbers([1], records), [1])

    def test_output_records_are_fallback_only_when_no_corpus_exists(self):
        self.assertEqual(feed_problem_numbers([], {2: {"n": 2}}), [2])


if __name__ == "__main__":
    unittest.main()
