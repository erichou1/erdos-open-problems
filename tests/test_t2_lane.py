import unittest

from build_t2_lane import build_t2_lane, render_t2_markdown


def _catalog(problems: dict) -> dict:
    return {
        "fetched_at": "2026-07-14T00:00:00+00:00",
        "source_data_url": "source",
        "problems": problems,
    }


class T2LaneTests(unittest.TestCase):
    def test_selects_only_finite_computation_states(self):
        lane = build_t2_lane(_catalog({
            "1": {"source_state": "open"},
            "2": {"source_state": "proved"},
            "7": {"source_state": "verifiable", "tags": ["covering systems"]},
            "19": {"source_state": "decidable"},
            "23": {"source_state": "falsifiable"},
        }))
        self.assertEqual(lane["counts"]["total"], 3)
        self.assertEqual(
            [record["problem"] for record in lane["problems"]], [19, 7, 23])
        self.assertEqual(lane["counts"]["decidable"], 1)
        self.assertEqual(lane["counts"]["verifiable"], 1)
        self.assertEqual(lane["counts"]["falsifiable"], 1)

    def test_orders_decidable_then_verifiable_then_falsifiable(self):
        lane = build_t2_lane(_catalog({
            "5": {"source_state": "falsifiable"},
            "6": {"source_state": "verifiable"},
            "8": {"source_state": "decidable"},
        }))
        self.assertEqual(
            [record["state"] for record in lane["problems"]],
            ["decidable", "verifiable", "falsifiable"])
        self.assertEqual(
            [record["rank"] for record in lane["problems"]], [1, 2, 3])

    def test_formalized_statements_rank_first_within_state(self):
        lane = build_t2_lane(_catalog({
            "10": {"source_state": "decidable", "formalized": {"state": "no"}},
            "20": {"source_state": "decidable", "formalized": {"state": "yes"}},
        }))
        self.assertEqual(
            [record["problem"] for record in lane["problems"]], [20, 10])
        self.assertTrue(lane["problems"][0]["formalized"])

    def test_ai_wiki_signals_surface_in_lane(self):
        lane = build_t2_lane(_catalog({
            "7": {
                "source_state": "verifiable",
                "ai_wiki": {"primary_full": True, "sections": ["1(a)"]},
            },
        }))
        self.assertTrue(lane["problems"][0]["ai_wiki_primary_full"])

    def test_markdown_carries_honesty_header_and_rows(self):
        lane = build_t2_lane(_catalog({
            "7": {
                "source_state": "verifiable",
                "source_problem_url": "https://www.erdosproblems.com/7",
                "tags": ["number theory", "covering systems"],
            },
        }))
        rendered = render_t2_markdown(lane)
        self.assertIn("searcher posteriors", rendered)
        self.assertIn("independently audit", rendered)
        self.assertIn("infeasibly large", rendered)
        self.assertIn("[7](https://www.erdosproblems.com/7)", rendered)
        self.assertIn("verified_finite_or_conditional_result", rendered)

    def test_provenance_never_claims_posteriors(self):
        lane = build_t2_lane(_catalog({}))
        self.assertIn("NOT", lane["provenance"])
        self.assertEqual(lane["counts"]["total"], 0)


if __name__ == "__main__":
    unittest.main()
