import io
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import aristotle_verifier as aristotle_module

from aristotle_verifier import (
    AristotleClient,
    AristotleConfig,
    AristotleResult,
    AristotleError,
    _load_dotenv_files,
    assess_project,
    has_incomplete_proof,
    parse_project_id,
    parse_state,
    verify_run,
    write_formal_proof_evidence,
)
from run_verified_pipeline import load_evidence
from egmra.policy import PolicyEnforcer, sign_policy

PROJECT_ID = "265eb121-51bf-4250-874b-fe85aafde008"
GOOD_LEAN = "import Mathlib\n\ntheorem erdos_x : True := by trivial\n"
SORRY_LEAN = "theorem erdos_x : True := by sorry\n"
POLICY_ENV = {"EGMRA_POLICY_KEY": "aristotle-loader-test-key-at-least-32-bytes"}


def evidence_loader_enforcer():
    return PolicyEnforcer(
        sign_policy({"automated_external_evidence": True}, env=POLICY_ENV),
        verification_env=POLICY_ENV,
    )


def aristotle_enforcer():
    return PolicyEnforcer(
        sign_policy({
            "external_prover_routing": True,
            "automated_external_evidence": True,
        }, env=POLICY_ENV),
        verification_env=POLICY_ENV,
    )


def make_run(run_dir: Path, *, candidate_outcome="candidate_proved",
             statement_sha="a" * 64) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "candidate.md").write_text("# candidate\nbody", encoding="utf-8")
    (run_dir / "problem.txt").write_text("Is it true that P?", encoding="utf-8")
    (run_dir / "manifest.json").write_text(json.dumps({
        "problem_number": 137,
        "candidate_outcome": candidate_outcome,
        "statement_sha256": statement_sha,
    }), encoding="utf-8")


def make_archive(path: Path, *, lean=GOOD_LEAN, summary="builds cleanly; no sorry") -> None:
    with tarfile.open(path, "w:gz") as tar:
        for name, content in (
            ("proj/RequestProject/Main.lean", lean),
            ("proj/ARISTOTLE_SUMMARY.md", summary),
        ):
            data = content.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


class FakeCLI:
    """Emulates the `aristotle` CLI runner for submit/show/download."""

    def __init__(self, archive_path: Path, *, state="COMPLETE", project_id=PROJECT_ID):
        self.archive_path = archive_path
        self.state = state
        self.project_id = project_id
        self.calls = []

    def __call__(self, args):
        self.calls.append(args)
        sub = args[0]
        if sub == "submit":
            if "--destination" in args:  # submit --wait writes the archive
                shutil.copy(self.archive_path, args[args.index("--destination") + 1])
            return subprocess.CompletedProcess(
                args, 0, "", f"Project created: {self.project_id}\n")  # id on stderr
        if sub == "show":
            return subprocess.CompletedProcess(args, 0, f"{self.state} (started 1m ago)\nsummary\n", "")
        if sub == "download":
            dest = args[args.index("--destination") + 1]
            shutil.copy(self.archive_path, dest)
            return subprocess.CompletedProcess(args, 0, "downloaded\n", "")
        if sub == "list":
            return subprocess.CompletedProcess(args, 0, f"{self.project_id} name IDLE\n", "")
        return subprocess.CompletedProcess(args, 1, "", "unknown command")


class ParseTests(unittest.TestCase):
    def test_parse_project_id(self):
        self.assertEqual(parse_project_id(f"Project {PROJECT_ID} submitted"), PROJECT_ID)
        self.assertEqual(parse_project_id("no id here"), "")

    def test_parse_state(self):
        self.assertEqual(parse_state("COMPLETE (started 785h ago)"), "COMPLETE")
        self.assertEqual(parse_state("status: RUNNING"), "RUNNING")
        self.assertEqual(parse_state("nothing"), "UNKNOWN")

    def test_has_incomplete_proof_ignores_comments(self):
        self.assertFalse(has_incomplete_proof(GOOD_LEAN))
        self.assertTrue(has_incomplete_proof(SORRY_LEAN))
        self.assertFalse(has_incomplete_proof("-- no sorry here\ntheorem t : True := trivial"))


class AssessTests(unittest.TestCase):
    def test_complete_no_sorry_is_quarantined_not_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "RequestProject").mkdir()
            (root / "RequestProject" / "Main.lean").write_text(GOOD_LEAN, encoding="utf-8")
            result = assess_project("COMPLETE", root, project_id=PROJECT_ID)
            self.assertFalse(result.verified)
            self.assertEqual(result.verdict, "unknown")
            self.assertEqual(result.verification_method, "vendor_artifact_quarantined")
            self.assertEqual(result.lean_status, "untrusted_project_not_executed")

    def test_sorry_is_not_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Main.lean").write_text(SORRY_LEAN, encoding="utf-8")
            self.assertFalse(assess_project("COMPLETE", root).verified)

    def test_incomplete_state_is_not_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Main.lean").write_text(GOOD_LEAN, encoding="utf-8")
            self.assertFalse(assess_project("FAILED", root).verified)

    def test_disproof_target_verdict(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Main.lean").write_text(GOOD_LEAN, encoding="utf-8")
            result = assess_project("COMPLETE", root, target_outcome="candidate_disproved")
            self.assertEqual(result.verdict, "unknown")

    def test_vendor_project_is_never_executed_even_with_injected_kernel_runner(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "RequestProject").mkdir()
            (root / "lakefile.lean").write_text(
                'run_cmd IO.FS.writeFile "/tmp/vendor-project-executed" "owned"\n',
                encoding="utf-8",
            )
            (root / "RequestProject" / "Main.lean").write_text(
                GOOD_LEAN, encoding="utf-8",
            )
            calls = []

            def forbidden_runner(args, cwd):
                calls.append((args, cwd))
                raise AssertionError("vendor-supplied project must never execute")

            result = assess_project(
                "COMPLETE", root, kernel_runner=forbidden_runner, run_kernel=True,
            )
            self.assertFalse(result.verified)
            self.assertEqual(calls, [])


class EvidenceTests(unittest.TestCase):
    def test_emitted_evidence_is_consumable_by_the_gate_loader(self):
        proved = AristotleResult(True, "proved", "COMPLETE", PROJECT_ID, GOOD_LEAN, "ok")
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            make_run(run, statement_sha="b" * 64)
            evidence_path = write_formal_proof_evidence(run, proved, target_outcome="candidate_proved")
            evidence = load_evidence(
                evidence_path, enforcer=evidence_loader_enforcer(),
            )
            self.assertEqual(len(evidence), 1)
            item = evidence[0]
            self.assertEqual(item.kind, "formal_proof")
            self.assertEqual(item.verifier, "aristotle")
            self.assertFalse(item.passed)
            self.assertRegex(item.artifact_sha256, r"^[0-9a-f]{64}$")
            self.assertEqual(item.statement_sha256, "b" * 64)

    def test_unverified_result_is_not_passed(self):
        unverified = AristotleResult(False, "unknown", "FAILED", PROJECT_ID, "", "")
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            make_run(run)
            record = json.loads(write_formal_proof_evidence(
                run, unverified, target_outcome="candidate_proved").read_text())[0]
            self.assertFalse(record["passed"])


class ClientTests(unittest.TestCase):
    def test_external_command_is_blocked_without_authenticated_feature_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "proj.tar.gz"
            make_archive(archive)
            cli = FakeCLI(archive)
            client = AristotleClient(AristotleConfig(api_key="k"), runner=cli)
            with self.assertRaises(Exception):
                client.prove("prove it")
            self.assertEqual(cli.calls, [])

    def test_prove_end_to_end_with_fake_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "proj.tar.gz"
            make_archive(archive)
            cli = FakeCLI(archive)
            client = AristotleClient(
                AristotleConfig(api_key="k"), runner=cli,
                enforcer=aristotle_enforcer(),
            )
            result = client.prove("prove it", target_outcome="candidate_proved")
            self.assertFalse(result.verified)
            self.assertEqual(result.verification_method, "vendor_artifact_quarantined")
            self.assertEqual(result.state, "COMPLETE")
            self.assertEqual(result.project_id, PROJECT_ID)
            self.assertIn("theorem", result.lean_source)
            self.assertEqual([c[0] for c in cli.calls], ["submit"])

    def test_prove_reports_sorry_archive_as_unverified(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "proj.tar.gz"
            make_archive(archive, lean=SORRY_LEAN)
            client = AristotleClient(
                AristotleConfig(api_key="k"), runner=FakeCLI(archive),
                enforcer=aristotle_enforcer(),
            )
            self.assertFalse(client.prove("prove it").verified)

    def test_prove_rejects_vendor_archive_link_member(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "link.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                link = tarfile.TarInfo("proj/RequestProject/Main.lean")
                link.type = tarfile.SYMTYPE
                link.linkname = "/etc/passwd"
                tar.addfile(link)
            client = AristotleClient(
                AristotleConfig(api_key="k"), runner=FakeCLI(archive),
                enforcer=aristotle_enforcer(),
            )
            with self.assertRaises(AristotleError):
                client.prove("prove it")

    def test_prove_rejects_vendor_archive_member_flood(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "flood.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                for index in range(aristotle_module._MAX_ARCHIVE_MEMBERS + 1):
                    item = tarfile.TarInfo(f"proj/item-{index}.txt")
                    item.size = 0
                    tar.addfile(item, io.BytesIO())
            client = AristotleClient(
                AristotleConfig(api_key="k"), runner=FakeCLI(archive),
                enforcer=aristotle_enforcer(),
            )
            with self.assertRaises(AristotleError):
                client.prove("prove it")

    def test_prove_rejects_oversized_compressed_archive_before_parsing(self):
        class OversizedArchiveCLI:
            def __call__(self, args):
                destination = Path(args[args.index("--destination") + 1])
                with destination.open("wb") as handle:
                    handle.truncate(aristotle_module._MAX_ARCHIVE_BYTES + 1)
                return subprocess.CompletedProcess(
                    args, 0, "", f"Project created: {PROJECT_ID}\n",
                )

        client = AristotleClient(
            AristotleConfig(api_key="k"), runner=OversizedArchiveCLI(),
            enforcer=aristotle_enforcer(),
        )
        with self.assertRaises(AristotleError):
            client.prove("prove it")

    def test_verify_run_uses_injected_client(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "proj.tar.gz"
            make_archive(archive)
            run = Path(directory) / "run"
            make_run(run)
            client = AristotleClient(
                AristotleConfig(api_key="k"), runner=FakeCLI(archive),
                enforcer=aristotle_enforcer(),
            )
            result, evidence_path, promoted = verify_run(
                run, client=client, enforcer=aristotle_enforcer(),
            )
            self.assertFalse(result.verified)
            self.assertTrue(evidence_path.is_file())
            self.assertIsNone(promoted)

    def test_default_runner_passes_only_minimal_environment(self):
        captured = {}

        def fake_run(*args, **kwargs):
            captured.update(kwargs)
            return subprocess.CompletedProcess(args, 0, "ok", "")

        inherited = {
            "PATH": "/safe/bin",
            "LANG": "C.UTF-8",
            "HOME": "/sensitive/home",
            "EGMRA_POLICY_KEY": "egmra-secret",
            "OPENAI_API_KEY": "openai-secret",
            "AWS_SECRET_ACCESS_KEY": "aws-secret",
        }
        with mock.patch.dict(os.environ, inherited, clear=True), mock.patch.object(
            aristotle_module.subprocess, "run", side_effect=fake_run,
        ):
            AristotleClient(AristotleConfig(api_key="aristotle-secret"))._default_runner(
                ["list"]
            )
        self.assertEqual(captured["env"], {
            "PATH": "/safe/bin",
            "LANG": "C.UTF-8",
            "ARISTOTLE_API_KEY": "aristotle-secret",
        })

    def test_cli_failure_redacts_provider_and_process_secrets(self):
        secret = "aristotle-secret-value"
        process_secret = "egmra-secret-value"

        def failed(args):
            return subprocess.CompletedProcess(
                args, 1, "", f"auth {secret}; signing {process_secret}",
            )

        with mock.patch.dict(
            os.environ, {"EGMRA_POLICY_KEY": process_secret}, clear=False,
        ):
            client = AristotleClient(
                AristotleConfig(api_key=secret), runner=failed,
                enforcer=aristotle_enforcer(),
            )
            with self.assertRaises(AristotleError) as caught:
                client.show(PROJECT_ID)
        message = str(caught.exception)
        self.assertNotIn(secret, message)
        self.assertNotIn(process_secret, message)
        self.assertIn("[REDACTED]", message)

    def test_duck_typed_policy_enforcer_is_rejected(self):
        class FakeEnforcer:
            def require(self, *args, **kwargs):
                return None

        with self.assertRaises(TypeError):
            AristotleClient(AristotleConfig(api_key="k"), enforcer=FakeEnforcer())

    def test_verify_run_rejects_duck_typed_active_enforcer_before_file_access(self):
        class FakeEnforcer:
            def require(self, *args, **kwargs):
                return None

        with self.assertRaises(TypeError):
            verify_run(Path("must-not-be-read"), enforcer=FakeEnforcer())


class ConfigurationBoundaryTests(unittest.TestCase):
    def test_dotenv_loader_ignores_non_aristotle_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            fake_module = repo / "aristotle_verifier.py"
            (repo / ".env").write_text(
                "ARISTOTLE_API_KEY=allowed\n"
                "ARISTOTLE_TIMEOUT_S=9\n"
                "OPENAI_API_KEY=must-not-load\n"
                "EGMRA_POLICY_KEY=must-not-load-either\n",
                encoding="utf-8",
            )
            with mock.patch.object(aristotle_module, "__file__", str(fake_module)), \
                    mock.patch.dict(os.environ, {}, clear=True):
                _load_dotenv_files()
                self.assertEqual(os.environ["ARISTOTLE_API_KEY"], "allowed")
                self.assertEqual(os.environ["ARISTOTLE_TIMEOUT_S"], "9")
                self.assertNotIn("OPENAI_API_KEY", os.environ)
                self.assertNotIn("EGMRA_POLICY_KEY", os.environ)


class RunFilesystemBoundaryTests(unittest.TestCase):
    def _client(self, archive: Path) -> AristotleClient:
        return AristotleClient(
            AristotleConfig(api_key="k"), runner=FakeCLI(archive),
            enforcer=aristotle_enforcer(),
        )

    def test_run_root_symlink_is_rejected_before_provider_call(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real_run = root / "real"
            make_run(real_run)
            linked_run = root / "linked"
            linked_run.symlink_to(real_run, target_is_directory=True)
            archive = root / "project.tar.gz"
            make_archive(archive)
            client = self._client(archive)
            with self.assertRaises(AristotleError):
                verify_run(linked_run, client=client, enforcer=aristotle_enforcer())
            self.assertEqual(client._runner.calls, [])

    def test_non_directory_run_root_is_rejected_before_provider_call(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_file = root / "run"
            run_file.write_text("not a directory", encoding="utf-8")
            archive = root / "project.tar.gz"
            make_archive(archive)
            client = self._client(archive)
            with self.assertRaises(AristotleError):
                verify_run(run_file, client=client, enforcer=aristotle_enforcer())
            self.assertEqual(client._runner.calls, [])

    def test_symlinked_parent_or_grandparent_is_rejected_before_provider_call(self):
        for depth in ("parent", "grandparent"):
            with self.subTest(depth=depth), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                archive = root / "project.tar.gz"
                make_archive(archive)
                if depth == "parent":
                    real_parent = root / "real-parent"
                    run = real_parent / "run"
                    make_run(run)
                    alias = root / "alias-parent"
                    alias.symlink_to(real_parent, target_is_directory=True)
                    supplied_run = alias / "run"
                else:
                    real_grandparent = root / "real-grandparent"
                    run = real_grandparent / "child" / "run"
                    make_run(run)
                    alias = root / "alias-grandparent"
                    alias.symlink_to(real_grandparent, target_is_directory=True)
                    supplied_run = alias / "child" / "run"
                client = self._client(archive)
                with self.assertRaises(AristotleError):
                    verify_run(
                        supplied_run, client=client, enforcer=aristotle_enforcer(),
                    )
                self.assertEqual(client._runner.calls, [])

    def test_manifest_problem_and_candidate_symlinks_are_rejected(self):
        for filename in ("manifest.json", "problem.txt", "candidate.md"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                run = root / "run"
                make_run(run)
                outside = root / f"outside-{filename.replace('.', '-')}"
                outside.write_text("{}" if filename.endswith(".json") else "secret")
                (run / filename).unlink()
                (run / filename).symlink_to(outside)
                archive = root / "project.tar.gz"
                make_archive(archive)
                client = self._client(archive)
                with self.assertRaises(AristotleError):
                    verify_run(run, client=client, enforcer=aristotle_enforcer())
                self.assertEqual(client._runner.calls, [])

    def test_aristotle_directory_symlink_is_rejected_without_outside_write(self):
        proved = AristotleResult(False, "unknown", "COMPLETE", PROJECT_ID, GOOD_LEAN, "ok")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "run"
            make_run(run)
            outside = root / "outside"
            outside.mkdir()
            (run / "aristotle").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(AristotleError):
                write_formal_proof_evidence(
                    run, proved, target_outcome="candidate_proved",
                )
            self.assertEqual(list(outside.iterdir()), [])

    def test_input_directory_symlink_is_rejected_before_provider_call(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "run"
            make_run(run)
            (run / "aristotle").mkdir()
            outside = root / "outside"
            outside.mkdir()
            (run / "aristotle" / "input").symlink_to(
                outside, target_is_directory=True,
            )
            archive = root / "project.tar.gz"
            make_archive(archive)
            client = self._client(archive)
            with self.assertRaises(AristotleError):
                verify_run(run, client=client, enforcer=aristotle_enforcer())
            self.assertEqual(client._runner.calls, [])
            self.assertEqual(list(outside.iterdir()), [])

    def test_manifest_problem_and_candidate_reads_are_bounded(self):
        cases = (
            ("manifest.json", aristotle_module._MAX_MANIFEST_BYTES),
            ("problem.txt", aristotle_module._MAX_STATEMENT_BYTES),
            ("candidate.md", aristotle_module._MAX_CANDIDATE_BYTES),
        )
        for filename, limit in cases:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                run = root / "run"
                make_run(run)
                with (run / filename).open("wb") as handle:
                    handle.truncate(limit + 1)
                archive = root / "project.tar.gz"
                make_archive(archive)
                client = self._client(archive)
                with self.assertRaises(AristotleError):
                    verify_run(run, client=client, enforcer=aristotle_enforcer())
                self.assertEqual(client._runner.calls, [])

    def test_existing_output_symlink_is_rejected_without_target_truncation(self):
        proved = AristotleResult(False, "unknown", "COMPLETE", PROJECT_ID, GOOD_LEAN, "ok")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "run"
            make_run(run)
            (run / "aristotle").mkdir()
            outside = root / "outside.lean"
            outside.write_text("do not overwrite", encoding="utf-8")
            (run / "aristotle" / "Main.lean").symlink_to(outside)
            with self.assertRaises(AristotleError):
                write_formal_proof_evidence(
                    run, proved, target_outcome="candidate_proved",
                )
            self.assertEqual(outside.read_text(encoding="utf-8"), "do not overwrite")


class FakeLake:
    def __init__(self, rc=0):
        self.rc = rc

    def __call__(self, args, cwd):
        rc = 0 if args[:2] == ["exe", "cache"] else self.rc
        return subprocess.CompletedProcess(args, rc, "", "")


class KernelFidelityTests(unittest.TestCase):
    def _project(self, root: Path, lean=GOOD_LEAN) -> Path:
        proj = root / "proj"
        (proj / "RequestProject").mkdir(parents=True)
        (proj / "lakefile.toml").write_text("[[require]]\n", encoding="utf-8")
        (proj / "lean-toolchain").write_text("leanprover/lean4:v4.28.0", encoding="utf-8")
        (proj / "RequestProject" / "Main.lean").write_text(lean, encoding="utf-8")
        return root

    def test_vendor_project_is_quarantined_even_when_runner_would_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._project(Path(directory))
            runner = FakeLake(0)
            result = assess_project("COMPLETE", root, kernel_runner=runner)
            self.assertFalse(result.verified)
            self.assertEqual(result.verification_method, "vendor_artifact_quarantined")
            self.assertEqual(result.lean_status, "untrusted_project_not_executed")

    def test_vendor_project_is_quarantined_without_invoking_failing_runner(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._project(Path(directory))
            result = assess_project("COMPLETE", root, kernel_runner=FakeLake(1))
            self.assertFalse(result.verified)
            self.assertEqual(result.verification_method, "vendor_artifact_quarantined")

    def test_require_kernel_blocks_aristotle_reported(self):
        proved = AristotleResult(
            True, "proved", "COMPLETE", PROJECT_ID, GOOD_LEAN, "ok",
            verification_method="aristotle_reported",
            formal_statements=("theorem t : True",))
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            make_run(run)
            evidence = write_formal_proof_evidence(
                run, proved, target_outcome="candidate_proved", require_kernel=True)
            record = json.loads(evidence.read_text())[0]
            self.assertFalse(record["passed"])
            self.assertEqual(record["statement_fidelity"], "unreviewed")
            fidelity_path = run / "aristotle" / "fidelity.json"
            self.assertTrue(fidelity_path.is_file())
            self.assertEqual(
                json.loads(fidelity_path.read_text())["formal_statements"],
                ["theorem t : True"],
            )

    def test_kernel_verified_still_requires_hardened_fidelity_certificate(self):
        proved = AristotleResult(
            True, "proved", "COMPLETE", PROJECT_ID, GOOD_LEAN, "ok",
            verification_method="local_lean_kernel")
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            make_run(run)
            record = json.loads(write_formal_proof_evidence(
                run, proved, target_outcome="candidate_proved",
                require_kernel=True).read_text())[0]
            self.assertFalse(record["passed"])
            self.assertEqual(record["verification_method"], "local_lean_kernel")


if __name__ == "__main__":
    unittest.main()
