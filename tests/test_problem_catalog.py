import unittest

from sync_problem_catalog import build_catalog


class ProblemCatalogTests(unittest.TestCase):
    def test_records_source_resolution_separately(self):
        source = [
            {"number": "1", "status": {"state": "open", "last_update": "2026-01-01"}},
            {"number": "2", "status": {"state": "proved", "last_update": "2026-02-01"}},
        ]
        catalog = build_catalog(source, fetched_at="now", source_url="source")
        self.assertFalse(catalog["problems"]["1"]["source_reports_resolved"])
        self.assertTrue(catalog["problems"]["2"]["source_reports_resolved"])
        self.assertEqual(catalog["counts"]["source_reports_resolved"], 1)


if __name__ == "__main__":
    unittest.main()
