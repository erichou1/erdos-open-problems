import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from problem_queue import (
    AllocationPlan,
    claim,
    claim_next,
    load_allocation_plan,
    ranked_queue,
    release_incomplete_claims,
    release_unverified_claims,
)
from erdos_searcher import (
    DEFAULT_BUDGET,
    DEFAULT_BUDGET_CONFIG,
    pipeline_fingerprint,
    toolset_version,
)
from run_contract import canonical_json, run_contract_id, run_context_id
import hashlib
from outcome_ledger import record_outcome
from run_continuous import maybe_rerank


def make_card(triage: Path, number: int, probability: float,
              resolved: bool = False) -> None:
    cards = triage / "normalized" / "problem_cards"
    cards.mkdir(parents=True, exist_ok=True)
    (cards / f"{number}.json").write_text(json.dumps({
        "problem_number": number,
        "metadata": {"source_reports_resolved": resolved},
        "posterior": {"p_verified_novel_resolution": {"probability": probability}},
    }), encoding="utf-8")


def make_ranking(
    triage: Path, *, overlap: bool = False, reorder: bool = False,
    first_problem_number: int = 2,
) -> tuple[AllocationPlan, dict]:
    context = {
        "snapshot_id": "20260712-test",
        "source_snapshot_sha256": "a" * 64,
        "pipeline_version": "pipeline-v2",
        "model_portfolio": "model-v3",
        "toolset_version": "b" * 64,
        "budget": DEFAULT_BUDGET,
        "budget_config": {
            "browser_channel": "playwright-chromium",
            "browser_headless": False,
            "initial_backoff_s": 15.0,
            "max_attempts": 8,
            "max_backoff_s": 120.0,
            "max_revisions": 2,
            "profile_capability": "persistent-authenticated-user-profile-v1",
            "rate_limit_policy": "shared-host-tempdir-v1",
            "request_spacing_s": 12.0,
            "review_roles_per_attempt": 8,
            "scout_contexts": 4,
            "stage_timeout_s": 1800.0,
        },
        "dependencies": {"requirements_lock_sha256": "c" * 64},
        "runtime": {"python": "3.14.4"},
    }
    context_id = hashlib.sha256(canonical_json(context).encode()).hexdigest()

    def row(number: int, lane: str, rank: int) -> dict:
        return {
            "problem_number": number,
            "rank": rank,
            "allocation_rank": rank,
            "allocation_lane": lane,
            "allocation_context_id": context_id,
            "run_contract_id": f"{number:x}".rjust(64, "0"),
        }

    exploit = [
        row(first_problem_number, "exploitation", 1),
        row(1, "exploitation", 2),
    ]
    explore_number = first_problem_number if overlap else 3
    explore = [row(explore_number, "protected_exploration", 1)]
    allocation = [
        row(first_problem_number, "exploitation", 1),
        row(1, "exploitation", 2),
        row(explore_number, "protected_exploration", 3),
    ]
    if reorder:
        allocation[1], allocation[2] = allocation[2], allocation[1]
        for rank, record in enumerate(allocation, 1):
            record["rank"] = rank
            record["allocation_rank"] = rank
    rankings = triage / "rankings"
    rankings.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 2,
        "allocation_status": "ready",
        "allocation_context": context,
        "allocation_context_id": context_id,
        "diversified_attack_queue": exploit,
        "protected_exploration": explore,
        "allocation_queue": allocation,
    }
    immutable = {
        key: value for key, value in payload.items()
        if key not in {"generated_at", "ranking_content_sha256", "allocation_id"}
    }
    ranking_hash = hashlib.sha256(
        json.dumps(immutable, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    allocation_id = hashlib.sha256(canonical_json({
        "allocation_context_id": context_id,
        "ranking_content_sha256": ranking_hash,
    }).encode()).hexdigest()
    payload.update({
        "ranking_content_sha256": ranking_hash,
        "allocation_id": allocation_id,
    })
    (rankings / "current.json").write_text(json.dumps(payload))
    context_dir = rankings / "contexts" / context_id
    context_dir.mkdir(parents=True, exist_ok=True)
    (context_dir / f"{ranking_hash}.json").write_text(json.dumps(payload))
    return load_allocation_plan(
        triage,
        expected_allocation_context_id=context_id,
        expected_ranking_content_sha256=ranking_hash,
    ), context


def make_manifest(
    artifacts: Path, number: int, gate_status: str, run_contract: str,
) -> None:
    run = artifacts / f"problem_{number}" / "run1"
    run.mkdir(parents=True, exist_ok=True)
    (run / "manifest.json").write_text(
        json.dumps({
            "run_contract_id": run_contract,
            "gate": {"status": gate_status},
        }), encoding="utf-8")


class ProblemQueueTests(unittest.TestCase):
    def test_rerank_reuse_binds_requested_top_k(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            triage = root / "triage"
            context_dir = triage / "rankings" / "contexts" / ("a" * 64)
            context_dir.mkdir(parents=True)
            budget_config = dict(DEFAULT_BUDGET_CONFIG)
            cached = {
                "allocation_status": "ready",
                "pipeline_version": pipeline_fingerprint(root),
                "model_portfolio": "model-v3",
                "budget": DEFAULT_BUDGET,
                "budget_config": budget_config,
                "toolset_version": toolset_version(root),
                "source_snapshot_id": "source-v1",
                "source_snapshot_sha256": "b" * 64,
                "canonical_open_source_records": 616,
                "allocation_top_k": 5,
            }
            (context_dir / f"{'c' * 64}.json").write_text(json.dumps(cached))
            self.assertIsNone(maybe_rerank(
                triage, root, 3600, 600, "model-v3", DEFAULT_BUDGET,
                budget_config,
                source_snapshot_id="source-v1",
                source_snapshot_sha256="b" * 64,
                canonical_open_source_records=616,
            ))

    def test_continuous_outcome_ledger_uses_normalized_disposition(self):
        with tempfile.TemporaryDirectory() as directory:
            triage = Path(directory)
            run = triage / "run1"
            run.mkdir()
            contract = {
                "run_contract_schema_version": 2,
                "statement_sha256": "e" * 64,
                "source_snapshot": {"id": "source-v1", "sha256": "a" * 64},
                "pipeline_fingerprint": "pipeline-v2",
                "research_directive_sha256": "f" * 64,
                "model_portfolio": "model-v3",
                "toolset": {"runner": "test"},
                "budget": {
                    "max_revisions": 2,
                    "scout_contexts": 4,
                    "review_roles_per_attempt": 8,
                },
                "execution_config": {
                    "stage_timeout_s": 1800.0,
                    "initial_backoff_s": 15.0,
                    "max_backoff_s": 120.0,
                    "request_spacing_s": 12.0,
                    "max_attempts": 8,
                    "rate_limit_policy": "shared-host-tempdir-v1",
                    "browser_headless": False,
                    "browser_channel": "playwright-chromium",
                    "profile_capability": "persistent-authenticated-user-profile-v1",
                },
                "dependencies": {"requirements_lock_sha256": "c" * 64},
                "runtime": {"python": "3.14.4"},
            }
            contract_id = run_contract_id(contract)
            execution_id = "execution-0601"
            context_id = run_context_id(
                run_contract_id_value=contract_id, execution_id=execution_id,
            )
            manifest = run / "manifest.json"
            manifest.write_text(json.dumps({
                "problem_number": 601,
                "execution_id": execution_id,
                "run_contract_id": contract_id,
                "run_context_id": context_id,
                "run_contract": contract,
                "gate": {"status": "candidate_rejected"},
                "candidate_outcome": "resource_exhausted",
            }))
            (run / "candidate.md").write_text(
                "<result>OUTCOME: resource_exhausted; CLAIMS_TOTAL: 0; "
                "OPEN_GAPS: budget exhausted</result>"
            )
            unrelated = triage / "run9" / "manifest.json"
            unrelated.parent.mkdir()
            unrelated.write_text(json.dumps({
                "problem_number": 601,
                "gate": {"status": "verified_proved"},
                "candidate_outcome": "candidate_proved",
            }))
            record_outcome(triage, 601, manifest)
            record = json.loads(
                (triage / "labels" / "outcomes.jsonl").read_text().splitlines()[0]
            )
            self.assertEqual(record["status"], "no_progress_within_budget")
            self.assertEqual(record["gate_status"], "candidate_rejected")
            self.assertEqual(record["budget"], DEFAULT_BUDGET)
            self.assertEqual(record["model_portfolio"], "model-v3")
            self.assertEqual(record["run_context_id"], context_id)
            self.assertFalse(record["learning_eligible"])
            self.assertNotIn("evidence_certificate_ids", record)

            evidence_root = triage / "labels" / "evidence"
            before = {
                path.relative_to(evidence_root)
                for path in evidence_root.rglob("*") if path.is_file()
            }
            failed_run = triage / "run2"
            failed_run.mkdir()
            failed_execution_id = "execution-0601-ledger-failure"
            failed_context_id = run_context_id(
                run_contract_id_value=contract_id,
                execution_id=failed_execution_id,
            )
            failed_manifest = failed_run / "manifest.json"
            failed_manifest.write_text(json.dumps({
                "problem_number": 601,
                "execution_id": failed_execution_id,
                "run_contract_id": contract_id,
                "run_context_id": failed_context_id,
                "run_contract": contract,
                "gate": {"status": "candidate_rejected"},
                "candidate_outcome": "resource_exhausted",
            }))
            (failed_run / "candidate.md").write_text(
                "<result>OUTCOME: resource_exhausted; CLAIMS_TOTAL: 0; "
                "OPEN_GAPS: budget exhausted</result>"
            )
            with mock.patch(
                "outcome_ledger.append_ledger",
                side_effect=RuntimeError("synthetic ledger failure"),
            ):
                with self.assertRaises(RuntimeError):
                    record_outcome(triage, 601, failed_manifest)
            after = {
                path.relative_to(evidence_root)
                for path in evidence_root.rglob("*") if path.is_file()
            }
            self.assertEqual(after, before)

            verified_run = triage / "run3"
            verified_run.mkdir()
            verified_execution_id = "execution-0601-intent-failure"
            verified_context_id = run_context_id(
                run_contract_id_value=contract_id,
                execution_id=verified_execution_id,
            )
            verified_manifest = verified_run / "manifest.json"
            verified_manifest.write_text(json.dumps({
                "problem_number": 601,
                "execution_id": verified_execution_id,
                "run_contract_id": contract_id,
                "run_context_id": verified_context_id,
                "run_contract": contract,
                "gate": {"status": "verified_proved"},
                "candidate_outcome": "candidate_proved",
            }))
            (verified_run / "candidate.md").write_text(
                "<result>OUTCOME: candidate_proved; CLAIMS_TOTAL: 1; "
                "OPEN_GAPS: none</result>"
            )
            # A mutable legacy verified_* label is not an authenticated release
            # certificate and must be quarantined as operational, without
            # creating gate/intent truth evidence.
            self.assertTrue(record_outcome(triage, 601, verified_manifest))
            final_evidence = {
                path.relative_to(evidence_root)
                for path in evidence_root.rglob("*") if path.is_file()
            }
            self.assertEqual(final_evidence, before)
            latest = json.loads(
                (triage / "labels" / "outcomes.jsonl").read_text().splitlines()[-1]
            )
            self.assertEqual(latest["status"], "operational_failure")
            self.assertFalse(latest["learning_eligible"])
            self.assertNotIn("evidence_certificate_ids", latest)

    def test_ranked_queue_orders_by_probability_and_skips_resolved(self):
        with tempfile.TemporaryDirectory() as directory:
            triage = Path(directory)
            plan, _ = make_ranking(triage)
            self.assertEqual(
                ranked_queue(
                    triage,
                    expected_allocation_context_id=plan.allocation_context_id,
                    expected_ranking_content_sha256=plan.ranking_content_sha256,
                ),
                [2, 1, 3],
            )

    def test_ranked_queue_rejects_context_mismatch_and_overlapping_lanes(self):
        with tempfile.TemporaryDirectory() as directory:
            triage = Path(directory)
            plan, _ = make_ranking(triage)
            with self.assertRaises(ValueError):
                ranked_queue(
                    triage,
                    expected_allocation_context_id="f" * 64,
                    expected_ranking_content_sha256=plan.ranking_content_sha256,
                )
            with self.assertRaises(ValueError):
                make_ranking(triage, overlap=True)

    def test_ranked_queue_rejects_validly_rehashed_cadence_reordering(self):
        with tempfile.TemporaryDirectory() as directory:
            triage = Path(directory)
            with self.assertRaises(ValueError):
                make_ranking(triage, reorder=True)

    def test_ranked_queue_rejects_zero_problem_number(self):
        with tempfile.TemporaryDirectory() as directory:
            triage = Path(directory)
            with self.assertRaisesRegex(ValueError, "invalid record"):
                make_ranking(triage, first_problem_number=0)

    def test_claim_is_atomic_single_winner(self):
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            allocation = "a" * 64
            contract = "7" * 64
            self.assertTrue(claim(
                artifacts, 7, "a", allocation_id=allocation,
                run_contract_id=contract,
            ))
            self.assertFalse(claim(
                artifacts, 7, "b", allocation_id=allocation,
                run_contract_id=contract,
            ))
            self.assertTrue(claim(
                artifacts, 7, "b", allocation_id="b" * 64,
                run_contract_id=contract,
            ))

    def test_claim_next_does_not_trust_mutable_verified_manifest_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            triage = artifacts / "triage"
            plan, _ = make_ranking(triage)
            contract = plan.records[0]["run_contract_id"]
            make_manifest(artifacts, 2, "verified_proved", contract)
            self.assertEqual(claim_next(artifacts, plan, "w1"), 2)
            self.assertEqual(claim_next(artifacts, plan, "w2"), 1)
            self.assertEqual(claim_next(artifacts, plan, "w3"), 3)
            self.assertIsNone(claim_next(artifacts, plan, "w4"))

    def test_release_incomplete_keeps_verified_and_completed(self):
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            allocation = "a" * 64
            contracts = {number: f"{number:x}".rjust(64, "0") for number in (1, 2, 3)}
            claim(artifacts, 1, "w", allocation_id=allocation,
                  run_contract_id=contracts[1])  # no run dir -> released
            make_manifest(artifacts, 2, "verified_proved", contracts[2])
            claim(artifacts, 2, "w", allocation_id=allocation,
                  run_contract_id=contracts[2])  # verified -> kept
            make_manifest(artifacts, 3, "candidate_rejected", contracts[3])
            claim(artifacts, 3, "w", allocation_id=allocation,
                  run_contract_id=contracts[3])  # has matching manifest -> kept
            released = release_incomplete_claims(artifacts)
            self.assertEqual(released, 1)
            claims = artifacts / ".claims" / allocation
            self.assertFalse((claims / "problem_1").exists())
            self.assertTrue((claims / "problem_2").exists())
            self.assertTrue((claims / "problem_3").exists())

    def test_new_campaign_can_release_completed_but_unverified_claims(self):
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            allocation = "a" * 64
            contracts = {number: f"{number:x}".rjust(64, "0") for number in (2, 3)}
            make_manifest(artifacts, 2, "verified_proved", contracts[2])
            claim(artifacts, 2, "old", allocation_id=allocation,
                  run_contract_id=contracts[2])
            make_manifest(artifacts, 3, "candidate_rejected", contracts[3])
            claim(artifacts, 3, "old", allocation_id=allocation,
                  run_contract_id=contracts[3])

            self.assertEqual(release_unverified_claims(artifacts), 2)
            claims = artifacts / ".claims" / allocation
            self.assertFalse((claims / "problem_2").exists())
            self.assertFalse((claims / "problem_3").exists())


if __name__ == "__main__":
    unittest.main()
