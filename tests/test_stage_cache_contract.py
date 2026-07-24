import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from proof_pipeline import ProofPipeline
from tests.test_proof_pipeline import (
    PassingRunner,
    TRUST_ENV,
    evidence_provider,
    attest_test_review,
)


ROOT = Path(__file__).resolve().parents[1]
STATEMENT_A = hashlib.sha256(b"exact statement A").hexdigest()
STATEMENT_B = hashlib.sha256(b"exact statement B").hexdigest()
SOURCE_A = hashlib.sha256(b"source snapshot A").hexdigest()
SOURCE_B = hashlib.sha256(b"source snapshot B").hexdigest()


class ContextRunner:
    def __init__(self):
        self.calls = []
        self.contexts = {}
        self.restored = []

    def run(self, prompt, *, stage, isolated):
        self.calls.append((prompt, stage, isolated))
        self.contexts[stage] = f"https://chat.test/{stage}/{len(self.calls)}"
        return f"fresh response {len(self.calls)}"

    def context_id(self, stage):
        return self.contexts.get(stage, "")

    def restore_context(self, stage, context_id):
        self.restored.append((stage, context_id))
        self.contexts[stage] = context_id


def contract(
    *,
    statement_sha256=STATEMENT_A,
    source_snapshot_id="snapshot-a",
    source_snapshot_sha256=SOURCE_A,
    pipeline_fingerprint="commit-a+pipeline-a",
    model_portfolio="model-a",
    max_revisions=2,
    stage_timeout_s=1800,
    toolset=None,
    dependencies=None,
    runtime=None,
):
    return {
        "run_contract_schema_version": 2,
        "statement_sha256": statement_sha256,
        "source_snapshot": {
            "id": source_snapshot_id,
            "sha256": source_snapshot_sha256,
        },
        "pipeline_fingerprint": pipeline_fingerprint,
        "research_directive_sha256": "f" * 64,
        "model_portfolio": model_portfolio,
        "toolset": toolset or {
            "runner": "test-browser-runner",
            "browser_automation": "test-playwright",
        },
        "budget": {
            "max_revisions": max_revisions,
            "scout_contexts": 4,
            "review_roles_per_attempt": 8,
        },
        "execution_config": {
            "stage_timeout_s": stage_timeout_s,
            "request_spacing_s": 12.0,
            "initial_backoff_s": 15.0,
            "max_backoff_s": 120.0,
        },
        "dependencies": dependencies or {
            "requirements_lock_sha256": hashlib.sha256(b"lock-a").hexdigest(),
        },
        "runtime": runtime or {
            "python": "3.14.4",
            "platform": "test-platform-a",
        },
    }


def pipeline(cache: Path, runner: ContextRunner, run_contract: dict) -> ProofPipeline:
    result = ProofPipeline(
        runner,
        cache,
        max_revisions=run_contract["budget"]["max_revisions"],
        pipeline_version=run_contract["pipeline_fingerprint"],
        model_portfolio=run_contract["model_portfolio"],
        execution_config=run_contract["execution_config"],
    )
    result._stage_cache = cache
    # The contract is persisted for audit, but the adjacent files are not an
    # authentication boundary and therefore are never replayed as model output.
    result._active_run_contract = run_contract
    return result


def solver_pipeline(
    artifact_root: Path,
    runner,
    problem: str,
    *,
    model_portfolio: str = "model-a",
) -> ProofPipeline:
    return ProofPipeline(
        runner,
        artifact_root,
        verification_evidence_provider=evidence_provider,
        review_attestor=attest_test_review,
        attestation_env=TRUST_ENV,
        pipeline_version="commit-a+pipeline-a",
        model_portfolio=model_portfolio,
        execution_config={
            "stage_timeout_s": 1800,
            "request_spacing_s": 12.0,
            "initial_backoff_s": 15.0,
            "max_backoff_s": 120.0,
        },
        source_snapshot_id="snapshot-a",
        source_snapshot_sha256=SOURCE_A,
        toolset={"runner": "test-browser-runner"},
        dependencies={
            "requirements_lock_sha256": hashlib.sha256(b"lock-a").hexdigest()
        },
        runtime={"python": "3.14.4", "platform": "test-platform-a"},
    )


class StageCacheContractTests(unittest.TestCase):
    def test_stage_cache_schema_requires_the_complete_v3_context(self):
        schema = json.loads(
            (ROOT / "schemas" / "stage-cache-metadata.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(schema["properties"]["cache_schema_version"]["const"], 3)
        self.assertFalse(schema["additionalProperties"])
        self.assertTrue(
            {
                "run_contract",
                "run_contract_id",
                "cache_context_id",
            }.issubset(schema["required"])
        )

    def test_exact_contract_is_recorded_but_never_replays_model_output(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            original_runner = ContextRunner()
            original = pipeline(cache, original_runner, contract())
            self.assertEqual(
                original._run("identical prompt", "review_logic_1"),
                "fresh response 1",
            )

            resumed_runner = ContextRunner()
            resumed = pipeline(cache, resumed_runner, contract())
            self.assertEqual(
                resumed._run("identical prompt", "review_logic_1"),
                "fresh response 1",
            )
            self.assertEqual(len(resumed_runner.calls), 1)
            self.assertEqual(resumed_runner.restored, [])
            metadata = json.loads(
                (cache / "review_logic_1.meta.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["cache_schema_version"], 3)
            self.assertEqual(metadata["stage"], "review_logic_1")
            self.assertEqual(metadata["run_contract"], contract())
            expected_contract_id = hashlib.sha256(
                json.dumps(
                    contract(),
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                ).encode("utf-8")
            ).hexdigest()
            self.assertEqual(metadata["run_contract_id"], expected_contract_id)
            expected_cache_context_id = hashlib.sha256(
                json.dumps(
                    {
                        "cache_schema_version": 3,
                        "prompt_sha256": hashlib.sha256(
                            b"identical prompt"
                        ).hexdigest(),
                        "run_contract_id": expected_contract_id,
                        "stage": "review_logic_1",
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                ).encode("utf-8")
            ).hexdigest()
            self.assertEqual(
                metadata["cache_context_id"], expected_cache_context_id
            )

    def assert_contract_change_forces_fresh_call(self, changed_contract):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            original = pipeline(cache, ContextRunner(), contract())
            original._run("identical prompt", "review_logic_1")

            runner = ContextRunner()
            resumed = pipeline(cache, runner, changed_contract)
            self.assertEqual(
                resumed._run("identical prompt", "review_logic_1"),
                "fresh response 1",
            )
            self.assertEqual(len(runner.calls), 1)
            self.assertEqual(runner.restored, [])

    def test_changed_model_portfolio_invalidates_cache(self):
        self.assert_contract_change_forces_fresh_call(
            contract(model_portfolio="model-b")
        )

    def test_changed_budget_invalidates_cache(self):
        self.assert_contract_change_forces_fresh_call(
            contract(max_revisions=3, stage_timeout_s=900)
        )

    def test_changed_pipeline_fingerprint_invalidates_cache(self):
        self.assert_contract_change_forces_fresh_call(
            contract(pipeline_fingerprint="commit-b+pipeline-b")
        )

    def test_changed_statement_source_toolset_dependency_or_runtime_invalidates_cache(self):
        cases = {
            "statement": contract(statement_sha256=STATEMENT_B),
            "source": contract(
                source_snapshot_id="snapshot-b",
                source_snapshot_sha256=SOURCE_B,
            ),
            "toolset": contract(toolset={"runner": "different-runner"}),
            "dependencies": contract(
                dependencies={
                    "requirements_lock_sha256": hashlib.sha256(b"lock-b").hexdigest()
                }
            ),
            "runtime": contract(
                runtime={"python": "3.15.0", "platform": "test-platform-b"}
            ),
        }
        for name, changed in cases.items():
            with self.subTest(name=name):
                self.assert_contract_change_forces_fresh_call(changed)

    def test_copied_metadata_from_another_stage_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            original = pipeline(cache, ContextRunner(), contract())
            original._run("identical prompt", "scout_1")
            shutil.copyfile(cache / "scout_1.txt", cache / "scout_2.txt")
            shutil.copyfile(
                cache / "scout_1.meta.json", cache / "scout_2.meta.json"
            )

            runner = ContextRunner()
            resumed = pipeline(cache, runner, contract())
            self.assertEqual(
                resumed._run("identical prompt", "scout_2"), "fresh response 1"
            )
            self.assertEqual(len(runner.calls), 1)
            self.assertEqual(runner.restored, [])

    def test_legacy_or_incomplete_metadata_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            response = "legacy cached response"
            (cache / "review_logic_1.txt").write_text(response, encoding="utf-8")
            (cache / "review_logic_1.meta.json").write_text(
                json.dumps(
                    {
                        "cache_schema_version": 2,
                        "stage": "review_logic_1",
                        "prompt_sha256": hashlib.sha256(
                            b"identical prompt"
                        ).hexdigest(),
                        "response_sha256": hashlib.sha256(
                            response.encode("utf-8")
                        ).hexdigest(),
                        "context_id": "https://chat.test/legacy",
                        "recorded_at": "2026-07-12T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )

            runner = ContextRunner()
            resumed = pipeline(cache, runner, contract())
            self.assertEqual(
                resumed._run("identical prompt", "review_logic_1"),
                "fresh response 1",
            )
            self.assertEqual(len(runner.calls), 1)
            self.assertEqual(runner.restored, [])

    def test_solve_persists_contract_before_the_first_stage_executes(self):
        problem = "Prove the run contract is immutable."
        with tempfile.TemporaryDirectory() as directory:
            artifact_root = Path(directory)

            class ObservingRunner(PassingRunner):
                def __init__(self):
                    super().__init__()
                    self.contract_was_visible = False

                def run(self, prompt, *, stage, isolated):
                    records = list(
                        artifact_root.glob("problem_77/*/run_contract.json")
                    )
                    if records:
                        self.contract_was_visible = True
                    return super().run(prompt, stage=stage, isolated=isolated)

            runner = ObservingRunner()
            result = solver_pipeline(
                artifact_root, runner, problem
            ).solve(77, problem)
            self.assertTrue(runner.contract_was_visible)
            record = json.loads(
                (result.artifact_dir / "run_contract.json").read_text(
                    encoding="utf-8"
                )
            )
            manifest = json.loads(
                (result.artifact_dir / "manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                record["run_contract_id"], manifest["run_contract_id"]
            )
            expected_run_context_id = hashlib.sha256(
                json.dumps(
                    {
                        "execution_id": manifest["execution_id"],
                        "run_contract_id": manifest["run_contract_id"],
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                ).encode("utf-8")
            ).hexdigest()
            self.assertEqual(
                manifest.get("run_context_id"), expected_run_context_id
            )

    def test_incomplete_run_with_a_different_contract_gets_new_execution_dir(self):
        problem = "Prove a changed model cannot inherit an old execution."
        with tempfile.TemporaryDirectory() as directory:
            artifact_root = Path(directory)
            first = solver_pipeline(
                artifact_root, PassingRunner(), problem, model_portfolio="model-a"
            ).solve(78, problem)
            (first.artifact_dir / "manifest.json").unlink()

            second = solver_pipeline(
                artifact_root, PassingRunner(), problem, model_portfolio="model-b"
            ).solve(78, problem)
            self.assertNotEqual(first.artifact_dir, second.artifact_dir)
            old_record = json.loads(
                (first.artifact_dir / "run_contract.json").read_text(
                    encoding="utf-8"
                )
            )
            new_record = json.loads(
                (second.artifact_dir / "run_contract.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertNotEqual(
                old_record["run_contract_id"], new_record["run_contract_id"]
            )

    def test_no_caller_writable_incomplete_execution_directory_is_resumed(self):
        problem = "Prove copied execution metadata is not authoritative."
        with tempfile.TemporaryDirectory() as directory:
            artifact_root = Path(directory)
            first = solver_pipeline(
                artifact_root, PassingRunner(), problem
            ).solve(79, problem)
            (first.artifact_dir / "manifest.json").unlink()
            copied = first.artifact_dir.parent / "zzzz-copied-execution"
            shutil.copytree(first.artifact_dir, copied)

            resumed = solver_pipeline(
                artifact_root, PassingRunner(), problem
            ).solve(79, problem)
            self.assertNotEqual(resumed.artifact_dir, first.artifact_dir)
            self.assertNotEqual(resumed.artifact_dir, copied)
            self.assertFalse((copied / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
