import json
import hashlib
import re
import shutil
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path

from proof_pipeline import ProofPipeline
from promote_verified_run import promote
from run_verified_pipeline import publish_verified_result
from research_state import make_statement_lock
from verification import (
    Review,
    VerificationEvidence,
    VerificationBinding,
    sign_review,
    sign_verification_evidence,
)


REVIEW_ENV = {"EGMRA_LEGACY_REVIEW_KEY": "legacy-pipeline-review-key-at-least-32-bytes"}
EVIDENCE_ENV = {"EGMRA_LEGACY_EVIDENCE_KEY": "legacy-pipeline-evidence-key-at-least-32-bytes"}
TRUST_ENV = REVIEW_ENV | EVIDENCE_ENV
POLICY_ENV = {"EGMRA_POLICY_KEY": "legacy-pipeline-policy-key-at-least-32-bytes"}
SECURE_RUN_CONTEXT = {
    "pipeline_version": "test-pipeline-v1",
    "model_portfolio": "test-model-v1",
    "execution_config": {"stage_timeout_s": 30},
    "source_snapshot_id": "test-snapshot-v1",
    "source_snapshot_sha256": hashlib.sha256(b"test source snapshot").hexdigest(),
    "toolset": {"runner": "authenticated-test-runner"},
    "dependencies": {"requirements_lock_sha256": hashlib.sha256(b"test lock").hexdigest()},
    "runtime": {"python": "test-python", "platform": "test-platform"},
}


def _promotion_enforcer():
    """A signed policy that enables promotion, for the M0 promotion entry point."""
    from egmra.policy import PolicyEnforcer, sign_policy
    return PolicyEnforcer(sign_policy({
        "promotion": True,
        "formal_promotion": True,
        "automated_external_evidence": True,
    }, env=POLICY_ENV), verification_env=POLICY_ENV)


def candidate_result():
    return """<result>
OUTCOME: CANDIDATE_PROVED
COMPLETENESS_SCORE: 100
PROOF_CONFIDENCE: 99
ADVERSARIAL_SURVIVAL_SCORE: 99
OPEN_GAPS: NONE
UNCHECKED_IMPORTS: NONE
CLAIMS_CHECKED: 7
CLAIMS_TOTAL: 7
CLAIM_IDS: C1; C2; C3; C4; C5; C6; C7
</result>"""


def evidence_provider(binding: VerificationBinding):
    return (sign_verification_evidence(VerificationEvidence(
        kind="exact_computation",
        verifier="test-checker",
        outcome="candidate_proved",
        statement_sha256=binding.statement_sha256,
        candidate_sha256=binding.candidate_sha256,
        artifact_sha256="c" * 64,
        passed=True,
        verification_method="independent_exact_replay",
        validator_id="egmra.compute.exact-replay/v1",
        certificate_sha256="c" * 64,
        scope_sha256=binding.statement_sha256,
        coverage="complete",
        statement_fidelity="exact_scope_bound",
        problem_number=binding.problem_number,
        run_contract_id=binding.run_contract_id,
        execution_id=binding.execution_id,
        run_context_id=binding.run_context_id,
    ), env=EVIDENCE_ENV),)


def attest_test_review(review: Review, stage: str) -> Review:
    """Test gateway standing in for independently authenticated runner adapters."""
    identified = replace(
        review,
        authority_id=f"authority-{review.reviewer_id}",
        model_provider="test-provider",
        model_name=f"test-model-{review.reviewer_role}",
        model_version="immutable-v1",
        model_lineage=f"lineage-{review.reviewer_role}",
    )
    return sign_review(identified, env=REVIEW_ENV)


class PassingRunner:
    def __init__(self):
        self.calls = []

    def context_id(self, stage):
        return f"fake-context-{stage}"

    def run(self, prompt, *, stage, isolated):
        self.calls.append((stage, isolated, prompt))
        if stage == "synthesis":
            return json.dumps({
                "summary": "prove the base claim, then the goal",
                "bottleneck_ids": ["L1"],
                "subgoals": [
                    {"id": "L1", "claim": "base claim", "dependencies": [], "centrality": 5, "falsifiable": True},
                    {"id": "GOAL", "claim": "original theorem", "dependencies": ["L1"], "centrality": 5, "falsifiable": True},
                ],
            })
        if stage.startswith("regulator_"):
            return json.dumps({
                "decision": "REVISE_PROOF",
                "rationale": "the plan remains sound",
                "broken_node_ids": [],
                "new_constraints": ["remove circularity"],
            })
        if stage == "construction":
            return candidate_result()
        if stage.startswith("review_") or stage.startswith("adjudication_"):
            role = (
                stage.removeprefix("review_").rsplit("_", 1)[0]
                if stage.startswith("review_") else "adjudicator"
            )
            return json.dumps({
                "reviewer_role": role,
                "verdict": "pass",
                "claims_checked": 7,
                "claims_total": 7,
                "checked_claim_ids": [f"C{i}" for i in range(1, 8)],
                "open_gaps": [],
                "unchecked_imports": [],
                "material_errors": [],
                "statement_sha256": re.search(
                    r"STATEMENT_SHA256: ([0-9a-f]{64})", prompt
                ).group(1),
                "completeness_score": 100,
                "proof_confidence": 99,
                "adversarial_survival_score": 99,
                "outcome": "proved",
            })
        return f"output for {stage}"


class ProofPipelineTests(unittest.TestCase):
    def test_stage_cache_is_never_trusted_even_if_response_and_metadata_match(self):
        class ContextRunner:
            def __init__(self):
                self.calls = []
                self.contexts = {}

            def run(self, prompt, *, stage, isolated):
                self.calls.append((prompt, stage, isolated))
                self.contexts[stage] = f"https://chat.test/{stage}/{len(self.calls)}"
                return f"response {len(self.calls)}"

            def context_id(self, stage):
                return self.contexts.get(stage, "")

            def restore_context(self, stage, context_id):
                self.contexts[stage] = context_id

        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            def configured_pipeline(runner):
                configured = ProofPipeline(
                    runner,
                    cache,
                    pipeline_version="test-pipeline-v1",
                    model_portfolio="test-model-v1",
                    execution_config={"stage_timeout_s": 30},
                    source_snapshot_id="test-snapshot-v1",
                    source_snapshot_sha256=hashlib.sha256(
                        b"test source snapshot"
                    ).hexdigest(),
                    toolset={"runner": "context-test-runner"},
                    dependencies={
                        "requirements_lock_sha256": hashlib.sha256(
                            b"test dependency lock"
                        ).hexdigest()
                    },
                    runtime={"python": "test-python"},
                )
                configured._stage_cache = cache
                configured._bind_run_contract(
                    hashlib.sha256(b"test exact statement").hexdigest()
                )
                return configured

            first_runner = ContextRunner()
            first = configured_pipeline(first_runner)
            self.assertEqual(first._run("original prompt", "review_logic_1"), "response 1")
            metadata = json.loads((cache / "review_logic_1.meta.json").read_text())
            self.assertEqual(metadata["context_id"], "https://chat.test/review_logic_1/1")
            self.assertEqual(
                metadata["prompt_sha256"],
                hashlib.sha256(b"original prompt").hexdigest(),
            )

            resumed_runner = ContextRunner()
            resumed = configured_pipeline(resumed_runner)
            self.assertEqual(resumed._run("original prompt", "review_logic_1"), "response 1")
            self.assertEqual(len(resumed_runner.calls), 1)
            self.assertEqual(
                resumed_runner.context_id("review_logic_1"),
                "https://chat.test/review_logic_1/1",
            )

            # A caller can make the old circular integrity check pass by
            # replacing both the response and its adjacent digest metadata.
            forged = "forged reviewer approval"
            (cache / "review_logic_1.txt").write_text(forged, encoding="utf-8")
            metadata = json.loads(
                (cache / "review_logic_1.meta.json").read_text(encoding="utf-8")
            )
            metadata["response_sha256"] = hashlib.sha256(
                forged.encode("utf-8")
            ).hexdigest()
            metadata["context_id"] = "https://attacker.invalid/forged"
            (cache / "review_logic_1.meta.json").write_text(
                json.dumps(metadata), encoding="utf-8"
            )

            fresh_runner = ContextRunner()
            fresh = configured_pipeline(fresh_runner)
            self.assertEqual(
                fresh._run("original prompt", "review_logic_1"), "response 1"
            )
            self.assertEqual(len(fresh_runner.calls), 1)
            self.assertNotEqual(
                fresh_runner.context_id("review_logic_1"),
                "https://attacker.invalid/forged",
            )

    def test_stage_path_traversal_and_unbounded_response_fail_closed(self):
        class OversizedRunner(PassingRunner):
            def run(self, prompt, *, stage, isolated):
                return "x" * (16 * 1024 * 1024 + 1)

        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            pipeline = ProofPipeline(
                PassingRunner(), cache, **SECURE_RUN_CONTEXT,
            )
            pipeline._stage_cache = cache
            pipeline._bind_run_contract(hashlib.sha256(b"statement").hexdigest())
            with self.assertRaises(ValueError):
                pipeline._run("prompt", "../../outside")
            self.assertFalse((cache.parent / "outside.txt").exists())

            pipeline.runner = OversizedRunner()
            with self.assertRaisesRegex(ValueError, "response exceeds"):
                pipeline._run("prompt", "scout_1")
            self.assertFalse((cache / "scout_1.txt").exists())

    def test_uninitialized_stage_cache_fails_before_provider_call(self):
        runner = PassingRunner()
        with tempfile.TemporaryDirectory() as directory:
            pipeline = ProofPipeline(
                runner, Path(directory), **SECURE_RUN_CONTEXT,
            )
            pipeline._bind_run_contract(hashlib.sha256(b"statement").hexdigest())

            with self.assertRaisesRegex(ValueError, "stage cache is not initialized"):
                pipeline._run("prompt", "scout_1")

            self.assertEqual(runner.calls, [])

    def test_symlinked_artifact_root_and_problem_directory_fail_before_writes(self):
        problem = "Prove that the artifact boundary is confined."
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            outside = base / "outside"
            outside.mkdir()
            linked_root = base / "linked-artifacts"
            linked_root.symlink_to(outside, target_is_directory=True)
            runner = PassingRunner()

            with self.assertRaisesRegex(ValueError, "artifact root"):
                ProofPipeline(runner, linked_root, **SECURE_RUN_CONTEXT).solve(
                    91, problem
                )
            self.assertEqual(runner.calls, [])
            self.assertEqual(list(outside.iterdir()), [])

            real_root = base / "real-artifacts"
            real_root.mkdir()
            linked_problem = real_root / "problem_92"
            linked_problem.symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "problem directory"):
                ProofPipeline(runner, real_root, **SECURE_RUN_CONTEXT).solve(
                    92, problem
                )
            self.assertEqual(runner.calls, [])
            self.assertEqual(list(outside.iterdir()), [])

    def test_runs_isolated_stages_and_persists_gate_evidence(self):
        runner = PassingRunner()
        with tempfile.TemporaryDirectory() as directory:
            problem = "For every n, prove P(n)."
            result = ProofPipeline(
                runner, Path(directory),
                verification_evidence_provider=evidence_provider,
                review_attestor=attest_test_review,
                attestation_env=TRUST_ENV,
                **SECURE_RUN_CONTEXT,
            ).solve(1, problem, research_directive={
                "schema_version": 1,
                "parent_statement_sha256": make_statement_lock(problem).sha256,
                "recommended_attack_modes": ["exact_construction_search"],
                "subproblem_targets": [],
            })
            self.assertEqual(result.gate.status, "awaiting_external_evidence")
            self.assertTrue((result.artifact_dir / "manifest.json").exists())
            manifest = json.loads((result.artifact_dir / "manifest.json").read_text())
            self.assertEqual(manifest["pipeline_version"], "test-pipeline-v1")
            self.assertEqual(manifest["model_portfolio"], "test-model-v1")
            self.assertEqual(manifest["budget"]["max_revisions"], 2)
            self.assertEqual(manifest["budget"]["stage_timeout_s"], 30)
            self.assertEqual(
                manifest["research_directive"]["recommended_attack_modes"],
                ["exact_construction_search"],
            )
            persisted_directive = json.loads(
                (result.artifact_dir / "research_directive.json").read_text()
            )
            self.assertEqual(
                persisted_directive["research_directive_sha256"],
                manifest["research_directive_sha256"],
            )
            for stage in ("scout_1", "synthesis", "construction"):
                prompt = next(prompt for name, _, prompt in runner.calls if name == stage)
                self.assertIn("exact_construction_search", prompt)
                self.assertIn("RESEARCH ROUTING DIRECTIVE", prompt)
        self.assertEqual(len(runner.calls), 14)
        self.assertTrue(all(isolated for _, isolated, _ in runner.calls))
        self.assertTrue(all("Do not browse" in prompt for _, _, prompt in runner.calls))

    def test_revises_after_rejection_and_keeps_failure_memory(self):
        class RevisingRunner(PassingRunner):
            def run(self, prompt, *, stage, isolated):
                response = super().run(prompt, stage=stage, isolated=isolated)
                if stage == "review_logic_1":
                    data = json.loads(response)
                    data["verdict"] = "fail"
                    data["material_errors"] = ["L1 assumes the conclusion"]
                    return json.dumps(data)
                if stage == "revision_1":
                    return candidate_result()
                return response

        runner = RevisingRunner()
        with tempfile.TemporaryDirectory() as directory:
            problem = "Prove Q."
            result = ProofPipeline(
                runner, Path(directory), max_revisions=1,
                verification_evidence_provider=evidence_provider,
                review_attestor=attest_test_review,
                attestation_env=TRUST_ENV,
                **SECURE_RUN_CONTEXT,
            ).solve(2, problem)
            state = json.loads((result.artifact_dir / "research_state.json").read_text())
            self.assertEqual(result.gate.status, "awaiting_external_evidence")
            self.assertEqual(len(state["attempts"]), 2)
            self.assertIn("assumes the conclusion", state["failed_approaches"][0]["obstructions"][0])

    def test_repeated_runs_use_distinct_audit_directories(self):
        runner = PassingRunner()
        problem = "Prove R."
        with tempfile.TemporaryDirectory() as directory:
            pipeline = ProofPipeline(
                runner, Path(directory),
                verification_evidence_provider=evidence_provider,
                review_attestor=attest_test_review,
                attestation_env=TRUST_ENV,
                **SECURE_RUN_CONTEXT,
            )
            first = pipeline.solve(3, problem)
            second = pipeline.solve(3, problem)
            self.assertNotEqual(first.artifact_dir, second.artifact_dir)
            self.assertTrue(first.artifact_dir.exists())
            self.assertTrue(second.artifact_dir.exists())

    def test_malformed_review_rejects_without_aborting(self):
        class MalformedRunner(PassingRunner):
            def run(self, prompt, *, stage, isolated):
                if stage == "review_logic_1":
                    self.calls.append((stage, isolated, prompt))
                    return '{"reviewer_role":"logic","claims_checked":"all"}'
                return super().run(prompt, stage=stage, isolated=isolated)

        problem = "Prove S."
        with tempfile.TemporaryDirectory() as directory:
            result = ProofPipeline(
                MalformedRunner(), Path(directory), max_revisions=0,
                verification_evidence_provider=evidence_provider,
                review_attestor=attest_test_review,
                attestation_env=TRUST_ENV,
                **SECURE_RUN_CONTEXT,
            ).solve(4, problem)
            self.assertEqual(result.gate.status, "candidate_rejected")
            self.assertTrue((result.artifact_dir / "manifest.json").exists())

    def test_prompt_generated_descriptive_reviewer_role_is_normalized(self):
        class DescriptiveRoleRunner(PassingRunner):
            def run(self, prompt, *, stage, isolated):
                response = super().run(prompt, stage=stage, isolated=isolated)
                if stage.startswith("review_"):
                    data = json.loads(response)
                    data["reviewer_role"] = (
                        f"independent adversarial referee ({data['reviewer_role']})"
                    )
                    return json.dumps(data)
                return response

        problem = "Prove the reviewer schema is stable."
        with tempfile.TemporaryDirectory() as directory:
            result = ProofPipeline(
                DescriptiveRoleRunner(), Path(directory),
                verification_evidence_provider=evidence_provider,
                review_attestor=attest_test_review,
                attestation_env=TRUST_ENV,
                **SECURE_RUN_CONTEXT,
            ).solve(41, problem)
            self.assertEqual(result.gate.status, "awaiting_external_evidence")

    def test_duplicate_review_keys_fail_closed_instead_of_last_wins(self):
        class DuplicateKeyRunner(PassingRunner):
            def run(self, prompt, *, stage, isolated):
                if stage == "review_logic_1":
                    self.calls.append((stage, isolated, prompt))
                    sha = re.search(
                        r"STATEMENT_SHA256: ([0-9a-f]{64})", prompt
                    ).group(1)
                    return (
                        '{"reviewer_role":"logic","verdict":"fail",'
                        '"verdict":"pass","claims_checked":7,"claims_total":7,'
                        '"checked_claim_ids":["C1","C2","C3","C4","C5","C6","C7"],'
                        '"open_gaps":[],"unchecked_imports":[],"material_errors":[],'
                        f'"statement_sha256":"{sha}","completeness_score":100,'
                        '"proof_confidence":99,"adversarial_survival_score":99,'
                        '"outcome":"proved"}'
                    )
                return super().run(prompt, stage=stage, isolated=isolated)

        with tempfile.TemporaryDirectory() as directory:
            result = ProofPipeline(
                DuplicateKeyRunner(), Path(directory), max_revisions=0,
                verification_evidence_provider=evidence_provider,
                review_attestor=attest_test_review,
                attestation_env=TRUST_ENV,
                **SECURE_RUN_CONTEXT,
            ).solve(42, "Prove duplicate keys cannot choose a verdict.")
            self.assertEqual(result.gate.status, "candidate_rejected")

    def test_malformed_replan_continues_with_last_valid_graph(self):
        class MalformedReplanRunner(PassingRunner):
            def run(self, prompt, *, stage, isolated):
                if stage == "review_logic_1":
                    data = json.loads(super().run(prompt, stage=stage, isolated=isolated))
                    data["verdict"] = "fail"
                    data["material_errors"] = ["L1 is unsupported"]
                    return json.dumps(data)
                if stage == "regulator_1":
                    return json.dumps({
                        "decision": "REVISE_PLAN",
                        "rationale": "replace L1",
                        "broken_node_ids": ["L1"],
                        "new_constraints": ["supply evidence"],
                    })
                if stage == "replan_1":
                    return '{"summary": "unterminated"'
                return super().run(prompt, stage=stage, isolated=isolated)

        problem = "Prove U."
        with tempfile.TemporaryDirectory() as directory:
            result = ProofPipeline(
                MalformedReplanRunner(), Path(directory), max_revisions=1,
                verification_evidence_provider=evidence_provider,
                review_attestor=attest_test_review,
                attestation_env=TRUST_ENV,
                **SECURE_RUN_CONTEXT,
            ).solve(6, problem)
            self.assertTrue((result.artifact_dir / "manifest.json").exists())
            self.assertTrue((result.artifact_dir / "attempt_1" / "replan_error.txt").exists())

    def test_external_evidence_promotes_but_legacy_publication_is_disabled(self):
        runner = PassingRunner()
        problem = "Prove T."
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            result = ProofPipeline(
                runner, base / "runs",
                review_attestor=attest_test_review,
                attestation_env=TRUST_ENV,
                **SECURE_RUN_CONTEXT,
            ).solve(5, problem)
            self.assertEqual(result.gate.status, "awaiting_external_evidence")
            artifact = base / "exact-replay-certificate.txt"
            artifact.write_text("independent exact replay certificate", encoding="utf-8")
            candidate = (result.artifact_dir / "candidate.md").read_text()
            run_manifest = json.loads(
                (result.artifact_dir / "manifest.json").read_text()
            )
            evidence_path = base / "evidence.json"
            item = sign_verification_evidence(VerificationEvidence(
                kind="exact_computation",
                verifier="test exact replay",
                outcome="candidate_proved",
                statement_sha256=make_statement_lock(problem).sha256,
                candidate_sha256=hashlib.sha256(candidate.encode()).hexdigest(),
                artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
                passed=True,
                verification_method="independent_exact_replay",
                validator_id="egmra.compute.exact-replay/v1",
                certificate_sha256=hashlib.sha256(
                    b"independent exact replay certificate"
                ).hexdigest(),
                scope_sha256=make_statement_lock(problem).sha256,
                coverage="complete",
                statement_fidelity="exact_scope_bound",
                problem_number=run_manifest["problem_number"],
                run_contract_id=run_manifest["run_contract_id"],
                execution_id=run_manifest["execution_id"],
                run_context_id=run_manifest["run_context_id"],
            ), env=EVIDENCE_ENV)
            record = asdict(item)
            record["artifact_path"] = artifact.name
            evidence_path.write_text(json.dumps([record]))

            tampered_run = result.artifact_dir.parent / "tampered-copy"
            shutil.copytree(result.artifact_dir, tampered_run)
            tampered_manifest_path = tampered_run / "manifest.json"
            tampered_manifest = json.loads(tampered_manifest_path.read_text())
            tampered_manifest["problem_number"] = 999999
            tampered_manifest_path.write_text(json.dumps(tampered_manifest))
            with self.assertRaises(ValueError):
                promote(
                    tampered_run, evidence_path, publish=False, category="open",
                    enforcer=_promotion_enforcer(), attestation_env=TRUST_ENV,
                )

            promoted = promote(
                result.artifact_dir, evidence_path, publish=False,
                category="open", base_dir=base,
                enforcer=_promotion_enforcer(),
                attestation_env=TRUST_ENV,
            )
            self.assertEqual(
                promoted.gate.status, "awaiting_authenticated_release"
            )
            with self.assertRaises(RuntimeError):
                publish_verified_result(promoted, "../../outside", base)
            self.assertFalse((base / "outputs").exists())

    def test_distinct_adjudicator_runner_handles_only_adjudication(self):
        primary = PassingRunner()
        adjudicator = PassingRunner()
        with tempfile.TemporaryDirectory() as directory:
            ProofPipeline(
                primary, Path(directory) / "runs",
                adjudicator_runner=adjudicator,
            ).solve(7, "Prove T.")
            primary_stages = [stage for stage, _, _ in primary.calls]
            adjudicator_stages = [stage for stage, _, _ in adjudicator.calls]
            self.assertTrue(any(s.startswith("adjudication_") for s in adjudicator_stages))
            self.assertFalse(any(s.startswith("adjudication_") for s in primary_stages))
            self.assertTrue(any(s.startswith("scout_") for s in primary_stages))
            self.assertFalse(any(s.startswith("scout_") for s in adjudicator_stages))

    def test_distinct_adjudicator_provenance_reads_from_adjudicator(self):
        class RecordingContextRunner(PassingRunner):
            def __init__(self):
                super().__init__()
                self.context_id_calls = []

            def context_id(self, stage):
                self.context_id_calls.append(stage)
                return super().context_id(stage)

        primary = RecordingContextRunner()
        adjudicator = RecordingContextRunner()
        with tempfile.TemporaryDirectory() as directory:
            ProofPipeline(
                primary, Path(directory) / "runs",
                adjudicator_runner=adjudicator,
            ).solve(7, "Prove T.")
            # The adjudication's provenance must be looked up on the adjudicator
            # runner (the distinct model), never the primary that reviewed itself.
            self.assertTrue(
                any(s.startswith("adjudication_") for s in adjudicator.context_id_calls)
            )
            self.assertFalse(
                any(s.startswith("adjudication_") for s in primary.context_id_calls)
            )

    def test_literature_grounds_search_stages_only(self):
        runner = PassingRunner()
        marker = "LITMARKER_UNIQUE_TOKEN"
        grounding = {"enabled": True, "source": "local_corpus",
                     "rediscovery_eligible": True, "related_problems": [1, 2]}
        with tempfile.TemporaryDirectory() as directory:
            result = ProofPipeline(
                runner, Path(directory) / "runs",
                literature_context=marker,
                literature_grounding=grounding,
            ).solve(7, "Prove T.")
            first_prompt = {}
            for stage, _isolated, prompt in runner.calls:
                first_prompt.setdefault(stage, prompt)
            self.assertTrue(any(s.startswith("scout_") for s in first_prompt))
            for stage, prompt in first_prompt.items():
                if stage.startswith("scout_") or stage == "construction":
                    self.assertIn(marker, prompt)
                if stage.startswith("review_") or stage.startswith("adjudication_"):
                    self.assertNotIn(marker, prompt)
            manifest = json.loads(
                (result.artifact_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["literature_grounding"], grounding)
            # grounding must never alter the locked statement
            lock = json.loads(
                (result.artifact_dir / "statement_lock.json").read_text(encoding="utf-8"))
            self.assertEqual(lock["sha256"], make_statement_lock("Prove T.").sha256)

    def test_malformed_synthesis_falls_back_to_minimal_graph(self):
        class BadSynthesisRunner(PassingRunner):
            def run(self, prompt, *, stage, isolated):
                if stage == "synthesis":
                    self.calls.append((stage, isolated, prompt))
                    return '{\n"summary": "a "quoted" phrase breaks json", "subgoals": []\n}'
                return super().run(prompt, stage=stage, isolated=isolated)

        runner = BadSynthesisRunner()
        with tempfile.TemporaryDirectory() as directory:
            result = ProofPipeline(runner, Path(directory) / "runs").solve(7, "Prove T.")
            # the run completes despite the unparseable planner response
            self.assertTrue((result.artifact_dir / "manifest.json").exists())
            self.assertTrue((result.artifact_dir / "synthesis_error.txt").exists())
            graph = json.loads(
                (result.artifact_dir / "subgoal_graph.json").read_text(encoding="utf-8"))
            self.assertIn("GOAL", json.dumps(graph))


if __name__ == "__main__":
    unittest.main()
