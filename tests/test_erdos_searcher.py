import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from erdos_ingest import CATALOG_URL, ingest_corpus
from erdos_searcher import (
    DEFAULT_BUDGET,
    append_ledger,
    audit_corpus,
    build_searcher,
    canonical_problem_run_inputs,
    formal_probe,
    pipeline_fingerprint,
    register_evidence_certificate,
    research_budget_id,
)
from run_contract import run_context_id


TEX = r"""\documentclass{article}
\begin{document}
\noindent\textbf{Problem Statement:}

Is it true that for every finite graph there exists a coloring with exactly 3 colors?

\bigskip
\end{document}
"""


class ErdosSearcherTests(unittest.TestCase):
    def outcome_record(
        self, output: Path, *, status: str, execution_id: str = "execution-0001",
        **overrides,
    ) -> dict:
        card = json.loads(
            (output / "normalized" / "problem_cards" / "1.json").read_text()
        )
        record = {
            "problem_id": "erdos-1",
            "problem_number": 1,
            "execution_id": execution_id,
            "run_contract_id": card["run_contract_id"],
            "snapshot_id": card["provenance"]["source_snapshot_id"],
            "source_snapshot_sha256": card["provenance"]["source_snapshot_sha256"],
            "statement_sha256": card["statement"]["statement_sha256"],
            "pipeline_version": card["pipeline_version"],
            "model_portfolio": card["model_portfolio"],
            "toolset_version": card["toolset_version"],
            "budget": card["budget"],
            "budget_config": card["budget_config"],
            "status": status,
            "gate_status": "candidate_rejected",
            "candidate_outcome": "resource_exhausted",
            "learning_eligible": status in {
                "wrong_interpretation", "fundamentally_flawed_candidate",
                "no_progress_within_budget",
            },
        }
        record.update(overrides)
        record["run_context_id"] = run_context_id(
            run_contract_id_value=record["run_contract_id"],
            execution_id=record["execution_id"],
        )
        if status.startswith("verified_"):
            record["gate_status"] = "verified_proved"
            record["candidate_outcome"] = "candidate_proved"
            record["learning_eligible"] = False
            candidate_bytes = f"candidate:{record['execution_id']}".encode()
            candidate_sha = hashlib.sha256(candidate_bytes).hexdigest()
            record["candidate_sha256"] = candidate_sha
            gate = {"status": "verified_proved"}
            manifest = {
                "schema_version": 1,
                "projection_type": "ledger-disposition-input-v1",
                "problem_number": 1,
                "execution_id": record["execution_id"],
                "run_contract": card["run_contract"],
                "run_contract_id": record["run_contract_id"],
                "run_context_id": record["run_context_id"],
                "statement_sha256": record["statement_sha256"],
                "candidate_sha256": candidate_sha,
                "gate_status": "verified_proved",
                "manifest_candidate_outcome": "candidate_proved",
                "failure_plane": None,
            }
            manifest_bytes = (
                json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            ).encode()
            snapshot = output / "ingestion" / record["snapshot_id"]
            common_support = {
                "manifest": manifest_bytes,
                "candidate": candidate_bytes,
            }
            kinds = ["gate", "intent"]
            if status == "verified_partial_progress":
                kinds.append("partial_progress")
            if status == "verified_novel_resolution":
                kinds.append("novelty")
            def evidence(kind):
                if kind == "gate":
                    return (
                        "proof_pipeline:deterministic_gate_v2",
                        {
                            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                            "gate_status": "verified_proved",
                            "gate_object_sha256": hashlib.sha256(
                                json.dumps(
                                    gate, sort_keys=True, separators=(",", ":")
                                ).encode()
                            ).hexdigest(),
                        },
                        common_support,
                    )
                if kind == "intent":
                    return (
                        "proof_pipeline:canonical_statement_lock_v2",
                        {
                            "source_snapshot_id": record["snapshot_id"],
                            "source_snapshot_sha256": record["source_snapshot_sha256"],
                            "statement_sha256": record["statement_sha256"],
                            "run_contract_id": record["run_contract_id"],
                        },
                        {
                            **common_support,
                            "source_manifest": (snapshot / "manifest.json").read_bytes(),
                            "source_record": (
                                snapshot / "source_records" / "problem_1.json"
                            ).read_bytes(),
                        },
                    )
                if kind == "partial_progress":
                    return (
                        "external:qualified-partial-review-v1",
                        {
                            "decision": "verified_partial_progress",
                            "verification_method": "qualified_human_review",
                            "verifier_identity": "test-qualified-reviewer",
                            "evidence_report_sha256": "3" * 64,
                            "verified_claim_sha256": "4" * 64,
                            "adapter_version": "unregistered-audit-v1",
                        },
                        {},
                    )
                return (
                    "external:qualified-novelty-review-v1",
                    {
                        "decision": "novel",
                        "reviewer_identity": "test-qualified-reviewer",
                        "review_scope": "theorem-level-current-literature",
                        "evidence_report_sha256": "5" * 64,
                        "source_inventory_sha256": "6" * 64,
                        "source_count": 3,
                        "adapter_version": "unregistered-audit-v1",
                    },
                    {},
                )

            certificate_material = [evidence(kind) for kind in kinds]
            record["evidence_certificate_ids"] = [
                register_evidence_certificate(
                    output,
                    kind=kind,
                    run_contract_id_value=record["run_contract_id"],
                    run_context_id_value=record["run_context_id"],
                    statement_sha256=record["statement_sha256"],
                    candidate_sha256=candidate_sha,
                    evidence_payload=payload,
                    issuer=issuer,
                    supporting_artifacts=support,
                )
                for kind, (issuer, payload, support) in zip(kinds, certificate_material)
            ]
        return record

    def test_research_budget_id_binds_revision_and_timeout_limits(self):
        self.assertEqual(
            research_budget_id(max_revisions=2, stage_timeout_s=1800),
            DEFAULT_BUDGET,
        )
        self.assertNotEqual(
            research_budget_id(max_revisions=3, stage_timeout_s=1800),
            DEFAULT_BUDGET,
        )

    def test_corpus_audit_rejects_malformed_problem_source_filename(self):
        with self.assertRaisesRegex(
            ValueError,
            "invalid problem source filename: problem_not-a-number.tex",
        ):
            audit_corpus(
                {"problems": {}},
                [Path("problem_not-a-number.tex")],
            )

    def test_pipeline_fingerprint_changes_with_pipeline_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "proof_pipeline.py"
            source.write_text("VERSION = 1\n")
            first = pipeline_fingerprint(root)
            source.write_text("VERSION = 2\n")
            self.assertNotEqual(first, pipeline_fingerprint(root))

    def test_ranking_binds_declared_model_portfolio(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            ranking = build_searcher(
                root, root / "triage", snapshot_date="2026-07-12", top_k=5,
                model_portfolio="chatgpt-5.5-pro-2026-07",
            )
            self.assertEqual(
                ranking["direct_solve_probability"][0]["model_portfolio"],
                "chatgpt-5.5-pro-2026-07",
            )

    def test_formalization_probe_reads_catalog_state_not_mapping_truthiness(self):
        self.assertFalse(formal_probe({"formalized": {"state": "no"}}, "Prove P.")
                         ["lean_route_available"])
        self.assertTrue(formal_probe({"formalized": {"state": "yes"}}, "Prove P.")
                        ["lean_route_available"])

    def make_repo(self, root: Path) -> None:
        (root / "open" / "individual").mkdir(parents=True)
        (root / "forum_threads").mkdir()
        (root / "open" / "individual" / "problem_1.tex").write_text(TEX)
        (root / "open" / "individual" / "problem_2.tex").write_text(TEX)
        (root / "forum_threads" / "1.json").write_text(json.dumps({
            "comment_count": 1,
            "comments": [{"text": "A possible counterexample was proposed."}],
        }))
        (root / "problem_catalog.json").write_text(json.dumps({
            "fetched_at": "2026-07-12T00:00:00Z",
            "source_data_url": "https://example.test/problems.yaml",
            "problems": {
                "1": {
                    "problem": 1,
                    "source_state": "open",
                    "source_reports_resolved": False,
                    "formalized": True,
                    "tags": ["graph theory"],
                },
                "2": {
                    "problem": 2,
                    "source_state": "proved",
                    "source_reports_resolved": True,
                    "formalized": False,
                    "tags": ["graph theory"],
                },
                "3": {
                    "problem": 3,
                    "source_state": "open",
                    "source_reports_resolved": False,
                    "formalized": False,
                    "tags": ["number theory"],
                },
            },
        }))
        catalog = b"""\
- number: 1
  status: {state: open, last_update: 2026-07-12}
  tags: [graph theory]
- number: 2
  status: {state: proved, last_update: 2026-07-12}
  tags: [graph theory]
- number: 3
  status: {state: open, last_update: 2026-07-12}
  tags: [number theory]
"""

        def fetch(url: str) -> bytes:
            if url == CATALOG_URL:
                return catalog
            number = int(url.rsplit("/", 1)[1])
            return (
                '<div id="content">Is it true that for every finite graph '
                f'there exists a coloring with exactly {number + 2} colors?</div>'
                '<div class="problem-additional-text"><p>Test remark.</p></div>'
            ).encode()

        ingest_corpus(
            root,
            root / "triage",
            fetch_bytes=fetch,
            canonical=True,
            upstream_commit="a" * 40,
            commit_catalog_bytes=catalog,
            snapshot_time="2026-07-12T00:00:00+00:00",
            delay_s=0,
        )

    def test_builds_immutable_snapshot_cards_routes_and_rankings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            output = root / "triage"
            stale_cards = output / "normalized" / "problem_cards"
            stale_cards.mkdir(parents=True)
            (stale_cards / "999.json").write_text("{}")
            first = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )
            second = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )

            self.assertEqual(first["snapshot_id"], second["snapshot_id"])
            snapshots = list((output / "snapshots").glob("*"))
            self.assertEqual(len(snapshots), 1)
            self.assertFalse((stale_cards / "999.json").exists())
            self.assertTrue((snapshots[0] / "raw" / "latex" / "problem_1.tex").exists())
            card = json.loads((output / "normalized" / "problem_cards" / "1.json").read_text())
            self.assertIn("formal_search", card["routes"])
            self.assertIn("counterexample_search", card["routes"])
            self.assertEqual(card["posterior"]["calibration_status"],
                             "uncalibrated_weak_prior_mvp")
            for subproblem in card["subproblems"]:
                self.assertRegex(subproblem["run_contract_id"], r"^[0-9a-f]{64}$")
            self.assertEqual(first["eligible_problems"], 1)
            run_inputs = canonical_problem_run_inputs(
                root, output, 1, model_portfolio="model-a",
                budget_config=card["budget_config"],
            )
            self.assertEqual(run_inputs["run_contract_id"], card["run_contract_id"])
            self.assertEqual(run_inputs["research_directive"], card["research_directive"])
            self.assertEqual(first["direct_solve_probability"][0]["problem_number"], 1)
            expected_rankings = {
                "highest_probability_verified_novel_solution",
                "highest_probability_verified_partial_progress",
                "highest_probability_lean_verification",
                "best_finite_computation_targets",
                "tractable_frontier",
                "most_likely_stale_literature_records",
                "highest_value_uncertain_problems",
                "highest_mathematical_value_targets",
                "highest_reusable_formal_infrastructure_value",
                "highest_expected_corpus_wide_unlock",
                "protected_exploration",
            }
            self.assertTrue(expected_rankings <= set(first))
            for ranking_name in expected_rankings:
                self.assertTrue((output / "rankings" / f"{ranking_name}.md").exists())
            ranking_card = first["highest_probability_verified_novel_solution"][0]
            for field in (
                "snapshot_date", "model_portfolio", "uncertainty",
                "estimated_review_cost", "reason_selected",
            ):
                self.assertIn(field, ranking_card)
            self.assertEqual(first["protected_exploration"][0]["problem_number"], 1)
            self.assertEqual(first["corpus_integrity"]["status"], "degraded")
            self.assertEqual(first["corpus_integrity"]["missing_open_problem_numbers"], [3])
            self.assertEqual(first["corpus_integrity"]["unexpected_problem_numbers"], [2])
            self.assertEqual(first["unranked_missing_source_records"], [3])
            manifest = json.loads((snapshots[0] / "source_manifest.json").read_text())
            self.assertEqual(manifest["corpus_integrity"], first["corpus_integrity"])

    def test_canonical_catalog_local_set_mismatch_withholds_allocation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            (root / "open" / "individual" / "problem_2.tex").unlink()
            catalog_path = root / "problem_catalog.json"
            catalog = json.loads(catalog_path.read_text())
            catalog["problems"] = {"1": catalog["problems"]["1"]}
            catalog_path.write_text(json.dumps(catalog))

            ranking = build_searcher(
                root, root / "triage", snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )
            integrity = ranking["corpus_integrity"]
            self.assertEqual(integrity["status"], "degraded")
            self.assertEqual(integrity["canonical_sources_missing_catalog_record"], [3])
            self.assertEqual(ranking["allocation_queue"], [])
            self.assertEqual(
                ranking["allocation_status"],
                "withheld_until_complete_exact_recorded_context",
            )

    def test_append_only_ledger_rejects_legacy_unbound_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record = root / "attempt.json"
            record.write_text(json.dumps({
                "problem_id": "erdos-1",
                "pipeline_version": "abc",
                "budget": DEFAULT_BUDGET,
                "status": "CENSORED",
                "schema_version": 999,
                "recorded_at": "1900-01-01T00:00:00Z",
            }))
            with self.assertRaises(ValueError):
                append_ledger(root / "triage", "attempts", record)

    def test_snapshot_identity_changes_when_local_source_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            output = root / "triage"
            first = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )

            source = root / "open" / "individual" / "problem_1.tex"
            source.write_text(TEX.replace("exactly 3 colors", "at most 3 colors"))
            second = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )

            self.assertNotEqual(first["snapshot_id"], second["snapshot_id"])
            self.assertEqual(len(list((output / "snapshots").glob("*"))), 2)

    def test_existing_source_snapshot_manifest_is_not_rewritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            (root / "forum_threads" / "999.json").write_text(json.dumps({
                "comment_count": 1,
                "comments": [{"text": "Resolved-problem forum record."}],
            }))
            output = root / "triage"
            first = build_searcher(root, output, snapshot_date="2026-07-12", top_k=5)
            manifest = (
                output / "snapshots" / first["snapshot_id"] / "source_manifest.json"
            )
            original = manifest.read_bytes()
            build_searcher(root, output, snapshot_date="2026-07-12", top_k=5)
            self.assertEqual(manifest.read_bytes(), original)
            self.assertFalse((manifest.parent / "raw" / "forum" / "999.json").exists())

            raw_forum = manifest.parent / "raw" / "forum" / "1.json"
            forum_original = raw_forum.read_bytes()
            raw_forum.write_text("{}")
            with self.assertRaises(RuntimeError):
                build_searcher(root, output, snapshot_date="2026-07-12", top_k=5)
            raw_forum.write_bytes(forum_original)

            manifest.unlink()
            with self.assertRaises(RuntimeError):
                build_searcher(root, output, snapshot_date="2026-07-12", top_k=5)

    def test_ranking_history_is_immutable_across_pipeline_versions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            source = root / "proof_pipeline.py"
            source.write_text("VERSION = 1\n")
            output = root / "triage"
            first = build_searcher(root, output, snapshot_date="2026-07-12", top_k=5)
            source.write_text("VERSION = 2\n")
            second = build_searcher(root, output, snapshot_date="2026-07-12", top_k=5)

            self.assertEqual(first["snapshot_id"], second["snapshot_id"])
            self.assertNotEqual(
                first["direct_solve_probability"][0]["pipeline_version"],
                second["direct_solve_probability"][0]["pipeline_version"],
            )
            self.assertEqual(len(list((output / "rankings" / "history").glob("*.json"))), 2)

    def test_content_addressed_ranking_context_rejects_existing_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            output = root / "triage"
            ranking = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )
            context_path = (
                output / "rankings" / "contexts"
                / ranking["allocation_context_id"]
                / f"{ranking['ranking_content_sha256']}.json"
            )
            tampered = json.loads(context_path.read_text())
            tampered["eligible_problems"] = 999
            context_path.write_text(json.dumps(tampered))
            with self.assertRaises(RuntimeError):
                build_searcher(
                    root, output, snapshot_date="2026-07-12", top_k=5,
                    model_portfolio="model-a",
                )

    def test_external_partial_outcome_is_audit_only_without_replay_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            output = root / "triage"
            first = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )
            before = first["highest_probability_verified_partial_progress"][0]["probability"]

            record = root / "outcome.json"
            record.write_text(json.dumps(self.outcome_record(
                output, status="verified_partial_progress",
            )))
            append_ledger(output, "outcomes", record)
            second = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )
            after = second["highest_probability_verified_partial_progress"][0]["probability"]

            self.assertEqual(after, before)
            card = json.loads((output / "normalized" / "problem_cards" / "1.json").read_text())
            self.assertEqual(card["posterior"]["matching_verified_outcome_records"], 0)

    def test_manual_no_progress_import_is_audit_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            output = root / "triage"
            first = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )
            before = first["direct_solve_probability"][0]["probability"]
            record = root / "manual-negative.json"
            record.write_text(json.dumps(self.outcome_record(
                output,
                status="no_progress_within_budget",
                learning_eligible=False,
            )))
            self.assertTrue(append_ledger(output, "outcomes", record))
            second = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )
            self.assertEqual(second["direct_solve_probability"][0]["probability"], before)

    def test_outcome_from_different_pipeline_does_not_update_posterior(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            output = root / "triage"
            first = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )
            before = first["highest_probability_verified_partial_progress"][0]["probability"]

            record = root / "outcome.json"
            record.write_text(json.dumps(self.outcome_record(
                output, status="verified_partial_progress",
                pipeline_version="a-different-pipeline",
            )))
            with self.assertRaises(ValueError):
                append_ledger(output, "outcomes", record)
            second = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )

            self.assertEqual(
                second["highest_probability_verified_partial_progress"][0]["probability"],
                before,
            )

    def test_outcome_from_different_model_portfolio_does_not_update_posterior(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            output = root / "triage"
            first = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )
            before = first["highest_probability_verified_partial_progress"][0]["probability"]
            record = root / "outcome.json"
            record.write_text(json.dumps(self.outcome_record(
                output, status="verified_partial_progress",
                model_portfolio="model-b",
            )))
            with self.assertRaises(ValueError):
                append_ledger(output, "outcomes", record)
            second = build_searcher(
                root, output, snapshot_date="2026-07-12", top_k=5,
                model_portfolio="model-a",
            )
            self.assertEqual(
                second["highest_probability_verified_partial_progress"][0]["probability"],
                before,
            )

    def test_unrecorded_model_portfolio_is_not_used_for_learning(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            output = root / "triage"
            first = build_searcher(root, output, snapshot_date="2026-07-12", top_k=5)
            before = first["highest_probability_verified_partial_progress"][0]["probability"]
            card = json.loads(
                (output / "normalized" / "problem_cards" / "1.json").read_text()
            )
            self.assertIsNone(card["run_contract_id"])
            self.assertTrue(card["allocation_status"].startswith("withheld:"))
            second = build_searcher(root, output, snapshot_date="2026-07-12", top_k=5)
            self.assertEqual(
                second["highest_probability_verified_partial_progress"][0]["probability"],
                before,
            )

    def test_censored_run_is_not_a_negative_ranking_example(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            clean = build_searcher(
                root, root / "triage_clean", snapshot_date="2026-07-12", top_k=5,
            )
            clean_probability = clean["direct_solve_probability"][0]["probability"]

            (root / "proof_runs_sol2" / "problem_1" / "incomplete").mkdir(parents=True)
            censored = build_searcher(
                root, root / "triage_censored", snapshot_date="2026-07-12", top_k=5,
            )
            censored_probability = censored["direct_solve_probability"][0]["probability"]

            self.assertEqual(censored_probability, clean_probability)

    def test_probe_ignores_mixed_private_proof_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            completed = root / "proof_runs_sol2" / "problem_1" / "run_complete"
            completed.mkdir(parents=True)
            (completed / "manifest.json").write_text(json.dumps({
                "gate": {"status": "candidate_rejected"},
            }))
            (root / "proof_runs_sol2" / "problem_1" / "run_incomplete").mkdir()

            output = root / "triage"
            build_searcher(root, output, snapshot_date="2026-07-12", top_k=5)
            card = json.loads(
                (output / "normalized" / "problem_cards" / "1.json").read_text()
            )
            self.assertFalse(card["probe_summary"]["early_research"]["censored"])
            self.assertEqual(card["probe_summary"]["early_research"]["runs"], 0)


if __name__ == "__main__":
    unittest.main()
