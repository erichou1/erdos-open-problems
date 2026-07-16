import unittest

from sync_problem_catalog import build_catalog, parse_ai_wiki

WIKI_SAMPLE = """
# AI contributions to Erdős problems

- [1. Primary contributions](#1-primary-contributions)

### 1(a). AI standalone

|  |
|  |
| [38] | GPT-5.5 Pro | 25 Apr, 2026 | \U0001f7e2 Full solution |
| [11] | Aristotle, GPT | 24 Jan, 2026 | \U0001f534 Incorrect claim made |
| [36] | GPT-5.5 Pro | 29 Jun, 2026 | \u26aa Candidate partial result |
| [124] | Aristotle | 29 Nov, 2025 | \U0001f7e1 Partial result (Lean) |

### 2(a). Literature search

|  |
|  |
| [94] | GPT-5 | 2 Nov, 2025 | \U0001f7e2 Full solution found |
| [35] | GPT-5 | 13 Oct, 2025 | \U0001f7e1 Partial results found |

### 2(b). Formalization

|  |
|  |
| [16] | \U0001f7e2 Chen (2023) | Antigravity | 25 Feb, 2026 |
"""


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

    def test_parse_ai_wiki_sections_and_colors(self):
        signals = parse_ai_wiki(WIKI_SAMPLE)
        self.assertTrue(signals["38"]["primary_full"])
        self.assertFalse(signals["38"]["primary_partial"])
        self.assertTrue(signals["11"]["incorrect"])
        self.assertFalse(signals["11"]["primary_full"])
        self.assertTrue(signals["36"]["unverified"])
        self.assertTrue(signals["124"]["primary_partial"])
        # 2(a) literature full solution is decisive but distinct from a primary
        # AI solution.
        self.assertTrue(signals["94"]["secondary_full"])
        self.assertFalse(signals["94"]["primary_full"])
        # A green marker in 2(b) formalization is neither kind of full solution.
        self.assertFalse(signals["16"]["primary_full"])
        self.assertFalse(signals["16"]["secondary_full"])
        self.assertEqual(signals["16"]["sections"], ["2(b)"])

    def test_parse_ai_wiki_ignores_prose_and_toc(self):
        signals = parse_ai_wiki(WIKI_SAMPLE)
        # The "[1. Primary contributions]" table-of-contents link must not
        # create a signal for problem 1.
        self.assertNotIn("1", signals)

    def test_build_catalog_folds_in_wiki_signals(self):
        source = [
            {"number": "38", "status": {"state": "open"}},
            {"number": "2", "status": {"state": "proved"}},
        ]
        catalog = build_catalog(
            source, fetched_at="now", source_url="source",
            ai_wiki=parse_ai_wiki(WIKI_SAMPLE), ai_wiki_url="wiki",
        )
        self.assertTrue(catalog["problems"]["38"]["ai_wiki"]["primary_full"])
        self.assertNotIn("ai_wiki", catalog["problems"]["2"])
        self.assertEqual(catalog["counts"]["ai_wiki_primary_full"], 1)
        self.assertEqual(catalog["ai_wiki_url"], "wiki")

    def test_build_catalog_without_wiki_stays_compatible(self):
        source = [{"number": "1", "status": {"state": "open"}}]
        catalog = build_catalog(source, fetched_at="now", source_url="source")
        self.assertNotIn("ai_wiki", catalog["problems"]["1"])
        self.assertNotIn("ai_wiki_url", catalog)
        self.assertEqual(catalog["counts"]["ai_wiki_primary_full"], 0)

    def test_build_catalog_preserves_raw_prize_and_counts_states(self):
        source = [
            {"number": "1", "prize": "no", "status": {"state": "open"}},
            {"number": "2", "prize": "$5000", "status": {"state": "open"}},
            {"number": "3", "status": {"state": "open"}},
            {"number": "4", "prize": "€500", "status": {"state": "proved"}},
            {"number": "5", "prize": "$100", "status": {"state": "unknown"}},
        ]
        catalog = build_catalog(source, fetched_at="now", source_url="source")
        self.assertEqual(catalog["problems"]["1"]["prize"], "no")
        self.assertEqual(catalog["problems"]["1"]["prize_status"], "unpaid")
        self.assertEqual(catalog["problems"]["2"]["prize"], "$5000")
        self.assertEqual(catalog["problems"]["2"]["prize_status"], "paid")
        self.assertIsNone(catalog["problems"]["3"]["prize"])
        self.assertEqual(catalog["problems"]["3"]["prize_status"], "unknown")
        self.assertEqual(catalog["counts"]["monetary_prize"], 3)
        self.assertEqual(catalog["counts"]["open_monetary_prize"], 1)
        self.assertEqual(catalog["counts"]["unknown_prize"], 1)


if __name__ == "__main__":
    unittest.main()
