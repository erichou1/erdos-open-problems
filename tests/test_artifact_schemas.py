import json
import unittest
from pathlib import Path

from feature_flags import feature_enabled, require_feature


ROOT = Path(__file__).resolve().parents[1]


class ArtifactSchemaTests(unittest.TestCase):
    def test_required_json_schemas_are_parseable_and_versioned(self):
        names = (
            "problem-card.schema.json",
            "subproblem-card.schema.json",
            "ranking-card.schema.json",
            "ledger-record.schema.json",
            "stage-cache-metadata.schema.json",
            "ingestion-manifest.schema.json",
            "literature-ranking-artifact.schema.json",
        )
        for name in names:
            with self.subTest(name=name):
                schema = json.loads((ROOT / "schemas" / name).read_text())
                self.assertEqual(schema["$schema"],
                                 "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["type"], "object")
                self.assertTrue(schema["required"])

    def test_feature_flags_default_experimental_subsystems_off(self):
        flags = json.loads((ROOT / "config" / "pipeline_features.json").read_text())
        self.assertTrue(flags["validated_stage_cache_v3"])
        self.assertTrue(flags["erdos_searcher_mvp"])
        for experimental in (
            "continuous_scheduler", "lean_execution", "fact_graph",
            "automated_external_evidence",
        ):
            self.assertFalse(flags[experimental])
        self.assertTrue(feature_enabled("erdos_searcher_mvp"))
        with self.assertRaises(RuntimeError):
            require_feature("continuous_scheduler")
        require_feature("continuous_scheduler", override=True)

    def test_ranking_and_problem_schemas_require_selection_audit_fields(self):
        ranking = json.loads(
            (ROOT / "schemas" / "ranking-card.schema.json").read_text()
        )
        self.assertTrue({
            "prize", "prize_status", "selection_priority_tier",
            "literature_policy_version", "literature_coverage_status",
            "local_literature_artifact_hash", "live_literature_artifact_hashes",
            "literature_features", "base_acquisition_score",
            "literature_adjustment", "selection_score",
        } <= set(ranking["required"]))
        problem = json.loads(
            (ROOT / "schemas" / "problem-card.schema.json").read_text()
        )
        self.assertTrue(
            {"prize", "prize_status", "ai_wiki"}
            <= set(problem["properties"]["metadata"]["required"])
        )
        self.assertIn(
            "literature_ranking",
            problem["properties"]["probe_summary"]["required"],
        )


if __name__ == "__main__":
    unittest.main()
