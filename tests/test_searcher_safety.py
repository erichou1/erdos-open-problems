import hashlib
import json
import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from erdos_searcher import (
    DEFAULT_BUDGET,
    DEFAULT_BUDGET_CONFIG,
    add_corpus_unlock_posteriors,
    append_ledger,
    build_card,
    canonical_json,
    estimate_posteriors,
    extract_subproblems,
    load_outcome_records,
    matching_outcome_records,
    pipeline_fingerprint,
    protected_exploration,
    register_evidence_certificate,
    research_budget_id,
    route_problem,
    split_run_budget,
)
from run_contract import make_run_contract, run_contract_id, run_context_id


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


TEST_STATEMENT = "Exact test statement."
TEST_STATEMENT_SHA = hashlib.sha256(TEST_STATEMENT.encode()).hexdigest()
TEST_SOURCE_RECORD = {
    "problem_number": 1,
    "sections": {
        "statement": {"text": TEST_STATEMENT, "sha256": TEST_STATEMENT_SHA},
    },
}
TEST_SOURCE_RECORD_BYTES = json_bytes(TEST_SOURCE_RECORD)
TEST_SOURCE_MANIFEST = {
    "snapshot_id": "20260712-snapshot",
    "canonical": True,
    "corpus_complete": True,
    "records": [{
        "problem_number": 1,
        "source_record_sha256": hashlib.sha256(TEST_SOURCE_RECORD_BYTES).hexdigest(),
        "statement_sha256": TEST_STATEMENT_SHA,
    }],
}
TEST_SOURCE_MANIFEST_BYTES = json_bytes(TEST_SOURCE_MANIFEST)
TEST_SOURCE_MANIFEST_SHA = hashlib.sha256(TEST_SOURCE_MANIFEST_BYTES).hexdigest()
TEST_CANDIDATE_BYTES = b"# Candidate\n\nSynthetic exact test candidate.\n"
TEST_CANDIDATE_SHA = hashlib.sha256(TEST_CANDIDATE_BYTES).hexdigest()
TEST_TOOLSET = {"runner": "test-runner-v1"}
TEST_DEPENDENCIES = {"lock_sha256": "1" * 64}
TEST_RUNTIME = {"python": "test-runtime-v1"}


def contract_for_record(record: dict) -> dict:
    budget, execution = split_run_budget(record["budget_config"])
    return make_run_contract(
        statement_sha256=record["statement_sha256"],
        source_snapshot_id=record["snapshot_id"],
        source_snapshot_sha256=record["source_snapshot_sha256"],
        pipeline_fingerprint=record["pipeline_version"],
        research_directive_sha256="f" * 64,
        model_portfolio=record["model_portfolio"],
        toolset=TEST_TOOLSET,
        budget=budget,
        execution_config=execution,
        dependencies=TEST_DEPENDENCIES,
        runtime=TEST_RUNTIME,
    )


def base_card() -> dict:
    return {
        "problem_id": "erdos-1",
        "problem_number": 1,
        "snapshot_id": "20260712-test",
        "pipeline_version": "pipeline-v1",
        "model_portfolio": "model-a",
        "budget": DEFAULT_BUDGET,
        "budget_config": dict(DEFAULT_BUDGET_CONFIG),
        "toolset_version": "toolset-v1",
        "run_contract_id": "d" * 64,
        "allocation_status": "exact_context_ready",
        "statement": {
            "ambiguity_status": "clear",
            "statement_sha256": "a" * 64,
        },
        "provenance": {
            "source_snapshot_id": "20260712-test",
            "source_snapshot_sha256": "e" * 64,
        },
        "metadata": {
            "source_reports_resolved": False,
            "references": [],
        },
        "problem_type": {
            "goal": "prove",
            "finite_signal": False,
            "asymptotic": False,
            "multi_part": False,
            "exact_search_affordance": False,
            "primary_domain": "number theory",
        },
        "probe_summary": {
            "statement": {
                "ambiguity_status": "clear",
                "quantifier_signal_count": 1,
                "statement_tokens_approx": 30,
            },
            "structure": {
                "goal": "prove",
                "finite_signal": False,
                "asymptotic": False,
                "multi_part": False,
                "exact_search_affordance": False,
                "primary_domain": "number theory",
            },
            "literature": {
                "comment_count": 0,
                "recent_claim_signal": False,
                "snapshot_available": False,
            },
            "formal": {
                "lean_route_available": False,
                "source_reports_formalized": False,
            },
            "early_research": {
                "attempts": 0,
                "runs": 0,
                "censored": False,
                "gate_statuses": [],
            },
        },
        "routes": ["natural_language_research"],
        "cost": {
            "relative_compute_units": 1.0,
            "expected_expert_review_cost": "unknown",
        },
    }


def ledger_record(**overrides) -> dict:
    value = {
        "problem_id": "erdos-1",
        "problem_number": 1,
        "execution_id": "exec-0001",
        "snapshot_id": "20260712-snapshot",
        "source_snapshot_sha256": TEST_SOURCE_MANIFEST_SHA,
        "statement_sha256": TEST_STATEMENT_SHA,
        "pipeline_version": "pipeline-v1",
        "model_portfolio": "model-a",
        "toolset_version": hashlib.sha256(canonical_json({
            "toolset": TEST_TOOLSET,
            "dependencies": TEST_DEPENDENCIES,
            "runtime": TEST_RUNTIME,
        }).encode()).hexdigest(),
        "budget": DEFAULT_BUDGET,
        "budget_config": dict(DEFAULT_BUDGET_CONFIG),
        "status": "no_progress_within_budget",
        "gate_status": "candidate_rejected",
        "candidate_outcome": "resource_exhausted",
        "learning_eligible": False,
    }
    value.update(overrides)
    value["run_contract_id"] = overrides.get(
        "run_contract_id", run_contract_id(contract_for_record(value))
    )
    value["run_context_id"] = overrides.get(
        "run_context_id",
        run_context_id(
            run_contract_id_value=value["run_contract_id"],
            execution_id=value["execution_id"],
        ),
    )
    return value


def certificate_evidence(kind: str, record: dict, *, decision: str = "novel"):
    contract = contract_for_record(record)
    gate = {"status": record["gate_status"]}
    failure_plane = {
        "wrong_interpretation": "statement",
        "fundamentally_flawed_candidate": "mathematical",
    }.get(record["status"])
    manifest = {
        "schema_version": 1,
        "projection_type": "ledger-disposition-input-v1",
        "problem_number": 1,
        "execution_id": record["execution_id"],
        "run_contract": contract,
        "run_contract_id": record["run_contract_id"],
        "run_context_id": record["run_context_id"],
        "statement_sha256": record["statement_sha256"],
        "candidate_sha256": record["candidate_sha256"],
        "gate_status": record["gate_status"],
        "manifest_candidate_outcome": record["candidate_outcome"],
        "failure_plane": failure_plane,
    }
    manifest_bytes = json_bytes(manifest)
    common_support = {
        "manifest": manifest_bytes,
        "candidate": TEST_CANDIDATE_BYTES,
    }
    if kind == "gate":
        return "proof_pipeline:deterministic_gate_v2", {
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "gate_status": "verified_proved",
            "gate_object_sha256": hashlib.sha256(
                canonical_json(gate).encode()
            ).hexdigest(),
        }, common_support
    if kind == "intent":
        return "proof_pipeline:canonical_statement_lock_v2", {
            "source_snapshot_id": record["snapshot_id"],
            "source_snapshot_sha256": record["source_snapshot_sha256"],
            "statement_sha256": record["statement_sha256"],
            "run_contract_id": record["run_contract_id"],
        }, {
            **common_support,
            "source_manifest": TEST_SOURCE_MANIFEST_BYTES,
            "source_record": TEST_SOURCE_RECORD_BYTES,
        }
    if kind == "disposition":
        disposition = {
            "status": record["status"],
            "gate_status": record["gate_status"],
            "candidate_outcome": record["candidate_outcome"],
        }
        return "proof_pipeline:deterministic_disposition_v1", {
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            **disposition,
            "disposition_object_sha256": hashlib.sha256(
                canonical_json(disposition).encode()
            ).hexdigest(),
        }, common_support
    if kind == "partial_progress":
        return "external:qualified-partial-review-v1", {
            "decision": "verified_partial_progress",
            "verification_method": "qualified_human_review",
            "verifier_identity": "test-qualified-reviewer",
            "evidence_report_sha256": "3" * 64,
            "verified_claim_sha256": "4" * 64,
            "adapter_version": "unregistered-audit-v1",
        }, {}
    return "external:qualified-novelty-review-v1", {
        "decision": decision,
        "reviewer_identity": "test-qualified-reviewer",
        "review_scope": "theorem-level-current-literature",
        "evidence_report_sha256": "5" * 64,
        "source_inventory_sha256": "6" * 64,
        "source_count": 3,
        "adapter_version": "unregistered-audit-v1",
    }, {}


class SearcherSafetyTests(unittest.TestCase):
    def test_pipeline_fingerprint_includes_statement_code_and_dependency_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "proof_pipeline.py").write_text("PIPELINE = 1\n")
            (root / "erdos_common.py").write_text("EXTRACTOR = 1\n")
            (root / "requirements.lock").write_text("example==1\n")
            first = pipeline_fingerprint(root)
            (root / "erdos_common.py").write_text("EXTRACTOR = 2\n")
            second = pipeline_fingerprint(root)
            self.assertNotEqual(first, second)
            (root / "requirements.lock").write_text("example==2\n")
            self.assertNotEqual(second, pipeline_fingerprint(root))

    def test_pipeline_fingerprint_ignores_unrelated_git_head_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "proof_pipeline.py").write_text("PIPELINE = 1\n")
            (root / "requirements.lock").write_text("example==1\n")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "pipeline"], cwd=root, check=True)
            first = pipeline_fingerprint(root)
            (root / "README.md").write_text("unrelated release metadata\n")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "docs"], cwd=root, check=True)
            self.assertEqual(first, pipeline_fingerprint(root))

    def test_budget_identity_covers_rate_limit_and_spacing_controls(self):
        common = dict(
            max_revisions=2,
            stage_timeout_s=1800,
            initial_backoff_s=15,
            max_backoff_s=120,
            request_spacing_s=12,
        )
        first = research_budget_id(**common)
        changed = research_budget_id(**{**common, "max_backoff_s": 60})
        self.assertNotEqual(first, changed)
        with self.assertRaises(ValueError):
            research_budget_id(**{**common, "scout_contexts": 5})

    def test_bare_attempts_never_raise_partial_progress_probability(self):
        clean = base_card()
        attempted = deepcopy(clean)
        attempted["probe_summary"]["early_research"]["attempts"] = 9
        self.assertEqual(
            estimate_posteriors(clean)["p_verified_partial_progress"]["probability"],
            estimate_posteriors(attempted)["p_verified_partial_progress"]["probability"],
        )

    def test_problem_cards_never_read_private_proof_run_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tex = root / "open" / "individual" / "problem_1.tex"
            tex.parent.mkdir(parents=True)
            tex.write_text("\\noindent\\textbf{Problem Statement:} Is one equal to one?")
            private_run = root / "proof_runs_sol2" / "problem_1" / "private-run"
            (private_run / "attempt_1").mkdir(parents=True)
            (private_run / "manifest.json").write_text(json.dumps({
                "gate": {"status": {"private": "unvalidated"}},
            }))
            canonical_source = {
                "statement": "Is one equal to one?",
                "references": "",
                "remarks": "",
                "provenance": {
                    "snapshot_id": "canonical-test",
                    "source_record_sha256": "a" * 64,
                    "raw_html_sha256": "b" * 64,
                    "section_sha256": {"statement": "c" * 64},
                    "extractor_version": "test-v1",
                },
            }
            card = build_card(
                root,
                "local-test",
                "pipeline-test",
                1,
                {"source_state": "open", "tags": []},
                tex,
                canonical_source=canonical_source,
                source_snapshot_sha256="d" * 64,
            )
            self.assertEqual(card["probe_summary"]["early_research"]["attempts"], 0)
            self.assertEqual(card["probe_summary"]["early_research"]["runs"], 0)
            self.assertEqual(card["probe_summary"]["early_research"]["gate_statuses"], [])

    def test_only_novelty_cleared_resolution_updates_novel_target(self):
        card = base_card()
        baseline = estimate_posteriors(card)
        pending = estimate_posteriors(card, [{"status": "verified_novelty_pending"}])
        novel = estimate_posteriors(
            card, [{"status": "verified_novel_resolution"}]
        )
        key = "p_verified_novel_resolution"
        self.assertEqual(baseline[key]["probability"], pending[key]["probability"])
        self.assertGreater(novel[key]["probability"], baseline[key]["probability"])

    def test_outcome_taxonomy_is_censoring_aware_and_directional(self):
        card = base_card()
        baseline = estimate_posteriors(card)
        censored = estimate_posteriors(card, [{"status": "censored_attempt"}])
        failed = estimate_posteriors(
            card, [{"status": "no_progress_within_budget"}]
        )
        wrong = estimate_posteriors(card, [{"status": "wrong_interpretation"}])
        novel_key = "p_verified_novel_resolution"
        statement_key = "p_statement_or_interpretation_failure"
        self.assertEqual(
            baseline[novel_key]["probability"], censored[novel_key]["probability"]
        )
        self.assertLess(failed[novel_key]["probability"], baseline[novel_key]["probability"])
        self.assertGreater(
            wrong[statement_key]["probability"], baseline[statement_key]["probability"]
        )

    def test_all_external_judgment_statuses_are_excluded_without_adapter(self):
        card = base_card()
        records = []
        for status in (
            "verified_novel_resolution", "verified_partial_progress",
            "independent_rediscovery", "literature_identification",
        ):
            records.append({
                "status": status,
                "learning_eligible": False,
                "run_contract_id": card["run_contract_id"],
                "snapshot_id": card["provenance"]["source_snapshot_id"],
                "source_snapshot_sha256": card["provenance"]["source_snapshot_sha256"],
                "statement_sha256": card["statement"]["statement_sha256"],
                "pipeline_version": card["pipeline_version"],
                "model_portfolio": card["model_portfolio"],
                "toolset_version": card["toolset_version"],
                "budget": card["budget"],
                "budget_config": card["budget_config"],
            })
        self.assertEqual(matching_outcome_records(card, records), [])

    def test_construction_and_multipart_routes_are_explicit(self):
        card = base_card()
        card["probe_summary"]["structure"].update(
            {"goal": "construct", "multi_part": True, "exact_search_affordance": True}
        )
        routes = route_problem(card)
        self.assertIn("exact_construction_search", routes)
        self.assertIn("construction_verification", routes)
        self.assertIn("shared_infrastructure_search", routes)
        self.assertIn("subproblem_decomposition", routes)

    def test_dedicated_value_and_unlock_targets_are_not_posterior_aliases(self):
        cards = []
        for number in range(1, 5):
            card = base_card()
            card["problem_id"] = f"erdos-{number}"
            card["problem_number"] = number
            cards.append(card)
        cards[0]["probe_summary"]["formal"]["lean_route_available"] = True
        cards[0]["routes"] = ["formal_search", "shared_infrastructure_search"]
        cards[1]["probe_summary"]["literature"].update(
            {"comment_count": 90, "recent_claim_signal": True}
        )
        cards[1]["metadata"]["references"] = ["a", "b", "c", "d"]
        cards[1]["probe_summary"]["structure"]["asymptotic"] = True
        cards[1]["problem_type"]["asymptotic"] = True
        cards[2]["probe_summary"]["structure"]["multi_part"] = True
        cards[2]["problem_type"]["multi_part"] = True
        cards[2]["routes"] = ["subproblem_decomposition", "shared_infrastructure_search"]
        cards[3]["probe_summary"]["structure"].update(
            {"finite_signal": True, "exact_search_affordance": True, "goal": "construct"}
        )
        cards[3]["problem_type"].update(
            {"finite_signal": True, "exact_search_affordance": True, "goal": "construct"}
        )
        cards[3]["problem_type"]["primary_domain"] = "graph theory"
        for card in cards:
            card["posterior"] = estimate_posteriors(card)
        add_corpus_unlock_posteriors(cards)

        def order(key):
            return [
                card["problem_number"]
                for card in sorted(
                    cards, key=lambda item: -item["posterior"][key]["probability"]
                )
            ]

        self.assertNotEqual(
            order("p_high_mathematical_value"), order("p_verified_novel_resolution")
        )
        self.assertNotEqual(
            order("p_expected_corpus_wide_unlock"),
            order("p_reusable_formal_infrastructure"),
        )

    def test_multipart_subproblem_ids_and_statement_locks_are_stable(self):
        statement = "Let $G$ be a finite graph. Is $G$ colorable? Must it be connected?"
        first = extract_subproblems(17, statement)
        second = extract_subproblems(17, statement)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 2)
        self.assertNotEqual(first[0]["subproblem_id"], first[1]["subproblem_id"])
        self.assertEqual(
            first[0]["statement"]["statement_sha256"],
            first[1]["statement"]["statement_sha256"],
        )
        self.assertNotEqual(
            first[0]["statement"]["focus_question_sha256"],
            first[1]["statement"]["focus_question_sha256"],
        )
        self.assertNotEqual(
            first[0]["subproblem_contract_sha256"],
            first[1]["subproblem_contract_sha256"],
        )
        for part in first:
            self.assertEqual(part["statement"]["original"], statement)
            self.assertIn("Let $G$ be a finite graph.", part["statement"]["original"])
            self.assertTrue(part["statement"]["focus_question"].endswith("?"))

    def test_protected_exploration_is_disjoint_from_exploitation(self):
        cards = []
        for number in range(1, 11):
            card = base_card()
            card["problem_id"] = f"erdos-{number}"
            card["problem_number"] = number
            card["posterior"] = estimate_posteriors(card)
            card["posterior"]["p_verified_novel_resolution"]["probability"] = 1 - number / 20
            cards.append(card)
        exploration = protected_exploration(cards, 10, excluded_problem_numbers={1, 2, 3, 4, 5})
        self.assertTrue(exploration)
        self.assertTrue(
            {row["problem_number"] for row in exploration}.isdisjoint({1, 2, 3, 4, 5})
        )

    def test_ledger_is_closed_context_bound_evidenced_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            unknown = root / "unknown.json"
            unknown.write_text(json.dumps(ledger_record(debug_url="https://chatgpt.com/c/x")))
            with self.assertRaises(ValueError):
                append_ledger(root / "triage", "outcomes", unknown)

            uncited = root / "uncited.json"
            uncited.write_text(json.dumps(ledger_record(
                status="verified_novel_resolution",
                gate_status="verified_proved",
                candidate_outcome="candidate_proved",
                learning_eligible=False,
            )))
            with self.assertRaises(ValueError):
                append_ledger(root / "triage", "outcomes", uncited)

            valid = root / "valid.json"
            valid.write_text(json.dumps(ledger_record()))
            self.assertTrue(append_ledger(root / "triage", "outcomes", valid))
            self.assertFalse(append_ledger(root / "triage", "outcomes", valid))
            lines = (
                root / "triage" / "labels" / "outcomes.jsonl"
            ).read_text().splitlines()
            self.assertEqual(len(lines), 1)

            cited_record = ledger_record(
                execution_id="exec-0002",
                status="verified_novel_resolution",
                candidate_sha256=TEST_CANDIDATE_SHA,
                evidence_certificate_ids=["e" * 64],
                gate_status="verified_proved",
                candidate_outcome="candidate_proved",
                learning_eligible=False,
            )
            cited = root / "cited.json"
            cited.write_text(json.dumps(cited_record))
            with self.assertRaises(ValueError):
                append_ledger(root / "triage", "outcomes", cited)

            with self.assertRaises(ValueError):
                register_evidence_certificate(
                    root / "triage", kind="novelty",
                    run_contract_id_value=cited_record["run_contract_id"],
                    run_context_id_value=cited_record["run_context_id"],
                    statement_sha256=cited_record["statement_sha256"],
                    candidate_sha256=cited_record["candidate_sha256"],
                    evidence_payload={"assertion": "trust me", "transcript": "private"},
                    issuer="self:unreviewed",
                )
            with self.assertRaises(ValueError):
                register_evidence_certificate(
                    root / "triage", kind="novelty",
                    run_contract_id_value=cited_record["run_contract_id"],
                    run_context_id_value=cited_record["run_context_id"],
                    statement_sha256=cited_record["statement_sha256"],
                    candidate_sha256=cited_record["candidate_sha256"],
                    evidence_payload={"assertion": "trust me", "transcript": "private"},
                    issuer="external:qualified-novelty-review-v1",
                )

            novelty_issuer, novelty_payload, novelty_support = certificate_evidence(
                "novelty", cited_record
            )
            novelty_payload = {
                **novelty_payload,
                "reviewer_identity": "private\ntranscript payload",
            }
            with self.assertRaises(ValueError):
                register_evidence_certificate(
                    root / "triage", kind="novelty",
                    run_contract_id_value=cited_record["run_contract_id"],
                    run_context_id_value=cited_record["run_context_id"],
                    statement_sha256=cited_record["statement_sha256"],
                    candidate_sha256=cited_record["candidate_sha256"],
                    evidence_payload=novelty_payload,
                    issuer=novelty_issuer,
                    supporting_artifacts=novelty_support,
                )

            gate_issuer, gate_payload, gate_support = certificate_evidence(
                "gate", cited_record
            )
            with self.assertRaises(ValueError):
                register_evidence_certificate(
                    root / "triage", kind="gate",
                    run_contract_id_value=cited_record["run_contract_id"],
                    run_context_id_value=cited_record["run_context_id"],
                    statement_sha256=cited_record["statement_sha256"],
                    candidate_sha256=cited_record["candidate_sha256"],
                    evidence_payload=gate_payload,
                    issuer=gate_issuer,
                )
            with self.assertRaises(ValueError):
                register_evidence_certificate(
                    root / "triage", kind="gate",
                    run_contract_id_value=cited_record["run_contract_id"],
                    run_context_id_value=cited_record["run_context_id"],
                    statement_sha256=cited_record["statement_sha256"],
                    candidate_sha256=cited_record["candidate_sha256"],
                    evidence_payload=gate_payload,
                    issuer=gate_issuer,
                    supporting_artifacts={
                        **gate_support,
                        "candidate": b"different candidate bytes",
                    },
                )

            cited_record["evidence_certificate_ids"] = [
                register_evidence_certificate(
                    root / "triage",
                    kind=kind,
                    run_contract_id_value=cited_record["run_contract_id"],
                    run_context_id_value=cited_record["run_context_id"],
                    statement_sha256=cited_record["statement_sha256"],
                    candidate_sha256=cited_record["candidate_sha256"],
                    evidence_payload=payload,
                    issuer=issuer,
                    supporting_artifacts=support,
                )
                for kind in ("gate", "intent", "novelty")
                for issuer, payload, support in [certificate_evidence(kind, cited_record)]
            ]
            cited.write_text(json.dumps(cited_record))
            self.assertTrue(append_ledger(root / "triage", "outcomes", cited))

    def test_ledger_rejects_cross_field_and_unbounded_payloads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid_records = (
                ledger_record(problem_number=2),
                ledger_record(problem_number="1"),
                ledger_record(gate_status={"private": "payload"}),
                ledger_record(candidate_outcome=["candidate_proved"]),
                ledger_record(pipeline_version="pipeline\nsmuggled"),
                ledger_record(model_portfolio="m" * 129),
                ledger_record(
                    status="verified_novel_resolution",
                    gate_status="verified_proved",
                    candidate_outcome="candidate_proved",
                    learning_eligible=True,
                ),
            )
            for index, invalid in enumerate(invalid_records):
                with self.subTest(index=index):
                    path = root / f"invalid-{index}.json"
                    path.write_text(json.dumps(invalid))
                    with self.assertRaises(ValueError):
                        append_ledger(root / f"triage-{index}", "outcomes", path)

    def test_evidence_support_rejects_private_manifest_before_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "triage"
            record = ledger_record(
                status="verified_novelty_pending",
                candidate_sha256=TEST_CANDIDATE_SHA,
                gate_status="verified_proved",
                candidate_outcome="candidate_proved",
                learning_eligible=False,
            )
            issuer, payload, support = certificate_evidence("gate", record)
            manifest = json.loads(support["manifest"])
            manifest["reviews"] = [{
                "context_id": "https://chatgpt.com/c/private-conversation-id",
            }]
            private_manifest = json_bytes(manifest)
            payload = {
                **payload,
                "manifest_sha256": hashlib.sha256(private_manifest).hexdigest(),
            }
            with self.assertRaises(ValueError):
                register_evidence_certificate(
                    output,
                    kind="gate",
                    run_contract_id_value=record["run_contract_id"],
                    run_context_id_value=record["run_context_id"],
                    statement_sha256=record["statement_sha256"],
                    candidate_sha256=record["candidate_sha256"],
                    evidence_payload=payload,
                    issuer=issuer,
                    supporting_artifacts={**support, "manifest": private_manifest},
                )
            support_root = output / "labels" / "evidence" / "support"
            self.assertFalse(any(support_root.glob("*.bin")))
            with self.assertRaises(ValueError):
                register_evidence_certificate(
                    output,
                    kind="gate",
                    run_contract_id_value=record["run_contract_id"],
                    run_context_id_value=record["run_context_id"],
                    statement_sha256=record["statement_sha256"],
                    candidate_sha256=record["candidate_sha256"],
                    evidence_payload=certificate_evidence("gate", record)[1],
                    issuer=issuer,
                    supporting_artifacts={
                        **certificate_evidence("gate", record)[2],
                        "extra_support": b"safe but unsupported orphan candidate",
                    },
                )
            self.assertFalse(any(support_root.glob("*.bin")))
            for private_url in (
                "https://chat.deepseek.com/a/chat/private-conversation-id",
                "https://chat.deepseek.com/chat/s/private-conversation-id",
            ):
                issuer, payload, support = certificate_evidence("gate", record)
                with self.assertRaisesRegex(ValueError, "private content"):
                    register_evidence_certificate(
                        output,
                        kind="gate",
                        run_contract_id_value=record["run_contract_id"],
                        run_context_id_value=record["run_context_id"],
                        statement_sha256=record["statement_sha256"],
                        candidate_sha256=record["candidate_sha256"],
                        evidence_payload=payload,
                        issuer=issuer,
                        supporting_artifacts={
                            **support,
                            "candidate": private_url.encode(),
                        },
                    )
            self.assertFalse(any(support_root.glob("*.bin")))

    def test_manual_negative_event_cannot_claim_learning_eligibility(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            forged = root / "forged.json"
            forged.write_text(json.dumps(ledger_record(learning_eligible=True)))
            with self.assertRaises(ValueError):
                append_ledger(root / "triage", "outcomes", forged)

    def test_disposition_certificate_recomputes_the_production_classifier(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "triage"
            contradictory = ledger_record(
                status="wrong_interpretation",
                gate_status="candidate_rejected",
                candidate_outcome="resource_exhausted",
                learning_eligible=True,
                candidate_sha256=TEST_CANDIDATE_SHA,
            )
            issuer, payload, support = certificate_evidence(
                "disposition", contradictory
            )
            with self.assertRaises(ValueError):
                register_evidence_certificate(
                    output,
                    kind="disposition",
                    run_contract_id_value=contradictory["run_contract_id"],
                    run_context_id_value=contradictory["run_context_id"],
                    statement_sha256=contradictory["statement_sha256"],
                    candidate_sha256=contradictory["candidate_sha256"],
                    evidence_payload=payload,
                    issuer=issuer,
                    supporting_artifacts=support,
                )

    def test_self_issued_disposition_certificate_cannot_enable_learning(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "triage"
            forged = ledger_record(
                status="no_progress_within_budget",
                gate_status="candidate_rejected",
                candidate_outcome="resource_exhausted",
                learning_eligible=True,
                candidate_sha256=TEST_CANDIDATE_SHA,
            )
            issuer, payload, support = certificate_evidence("disposition", forged)
            certificate_id = register_evidence_certificate(
                output,
                kind="disposition",
                run_contract_id_value=forged["run_contract_id"],
                run_context_id_value=forged["run_context_id"],
                statement_sha256=forged["statement_sha256"],
                candidate_sha256=forged["candidate_sha256"],
                evidence_payload=payload,
                issuer=issuer,
                supporting_artifacts=support,
            )
            forged["evidence_certificate_ids"] = [certificate_id]
            record_path = root / "forged.json"
            record_path.write_text(json.dumps(forged))
            with self.assertRaises(ValueError):
                append_ledger(output, "outcomes", record_path)

    def test_failed_evidence_registration_rolls_back_new_support(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "triage"
            record = ledger_record(
                status="verified_novelty_pending",
                candidate_sha256=TEST_CANDIDATE_SHA,
                gate_status="verified_proved",
                candidate_outcome="candidate_proved",
                learning_eligible=False,
            )
            issuer, payload, support = certificate_evidence("gate", record)
            references = {
                name: {
                    "path": f"support/{hashlib.sha256(value).hexdigest()}.bin",
                    "sha256": hashlib.sha256(value).hexdigest(),
                    "size_bytes": len(value),
                }
                for name, value in support.items()
            }
            artifact = {
                "schema_version": 2,
                "kind": "gate",
                "issuer": issuer,
                "evidence": payload,
                "supporting_artifacts": references,
            }
            artifact_sha = hashlib.sha256(json_bytes(artifact)).hexdigest()
            artifact_path = (
                output / "labels" / "evidence" / "artifacts"
                / f"{artifact_sha}.json"
            )
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text("{}")
            with self.assertRaises(ValueError):
                register_evidence_certificate(
                    output,
                    kind="gate",
                    run_contract_id_value=record["run_contract_id"],
                    run_context_id_value=record["run_context_id"],
                    statement_sha256=record["statement_sha256"],
                    candidate_sha256=record["candidate_sha256"],
                    evidence_payload=payload,
                    issuer=issuer,
                    supporting_artifacts=support,
                )
            self.assertFalse(any(
                (output / "labels" / "evidence" / "support").glob("*.bin")
            ))

    def test_ledger_evidence_is_live_and_outcomes_can_be_superseded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "triage"
            pending = ledger_record(
                status="verified_novelty_pending",
                candidate_sha256=TEST_CANDIDATE_SHA,
                gate_status="verified_proved",
                candidate_outcome="candidate_proved",
                learning_eligible=False,
            )

            def certificate(kind: str) -> str:
                issuer, payload, support = certificate_evidence(kind, pending)
                return register_evidence_certificate(
                    output,
                    kind=kind,
                    run_contract_id_value=pending["run_contract_id"],
                    run_context_id_value=pending["run_context_id"],
                    statement_sha256=pending["statement_sha256"],
                    candidate_sha256=pending["candidate_sha256"],
                    evidence_payload=payload,
                    issuer=issuer,
                    supporting_artifacts=support,
                )

            gate = certificate("gate")
            intent = certificate("intent")
            pending["evidence_certificate_ids"] = [gate, intent]
            record_path = root / "outcome.json"
            record_path.write_text(json.dumps(pending))
            self.assertTrue(append_ledger(output, "outcomes", record_path))

            novel = {
                **pending,
                "status": "verified_novel_resolution",
                "evidence_certificate_ids": [gate, intent, certificate("novelty")],
            }
            record_path.write_text(json.dumps(novel))
            self.assertTrue(append_ledger(output, "outcomes", record_path))
            events = [
                json.loads(line)
                for line in (output / "labels" / "outcomes.jsonl").read_text().splitlines()
            ]
            self.assertEqual([event["event_sequence"] for event in events], [1, 2])
            self.assertEqual(events[1]["supersedes_event_id"], events[0]["event_id"])
            loaded = load_outcome_records(output)["erdos-1"]
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["status"], "verified_novel_resolution")

            evidence_root = output / "labels" / "evidence"
            gate_certificate = json.loads(
                (evidence_root / "certificates" / f"{gate}.json").read_text()
            )
            gate_artifact = json.loads(
                (evidence_root / gate_certificate["artifact_path"]).read_text()
            )
            candidate_support = (
                evidence_root
                / gate_artifact["supporting_artifacts"]["candidate"]["path"]
            )
            candidate_original = candidate_support.read_bytes()
            candidate_support.write_bytes(b"tampered candidate")
            self.assertNotIn("erdos-1", load_outcome_records(output))
            candidate_support.write_bytes(candidate_original)
            self.assertEqual(
                load_outcome_records(output)["erdos-1"][0]["status"],
                "verified_novel_resolution",
            )

            issuer, payload, support = certificate_evidence(
                "novelty", pending, decision="independent_rediscovery"
            )
            correction_certificate = register_evidence_certificate(
                output,
                kind="novelty",
                run_contract_id_value=pending["run_contract_id"],
                run_context_id_value=pending["run_context_id"],
                statement_sha256=pending["statement_sha256"],
                candidate_sha256=pending["candidate_sha256"],
                evidence_payload=payload,
                issuer=issuer,
                supporting_artifacts=support,
            )
            corrected = {
                **pending,
                "status": "independent_rediscovery",
                "evidence_certificate_ids": [gate, intent, correction_certificate],
            }
            record_path.write_text(json.dumps(corrected))
            self.assertTrue(append_ledger(output, "outcomes", record_path))
            self.assertEqual(
                load_outcome_records(output)["erdos-1"][0]["status"],
                "independent_rediscovery",
            )

            (output / "labels" / "evidence" / "certificates" /
             f"{correction_certificate}.json").unlink()
            self.assertEqual(
                load_outcome_records(output)["erdos-1"][0]["status"],
                "verified_novel_resolution",
            )

            novelty_id = novel["evidence_certificate_ids"][-1]
            (output / "labels" / "evidence" / "certificates" /
             f"{novelty_id}.json").unlink()
            loaded = load_outcome_records(output)["erdos-1"]
            self.assertEqual(loaded[0]["status"], "verified_novelty_pending")


if __name__ == "__main__":
    unittest.main()
