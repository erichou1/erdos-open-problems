import io
import json
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

from aristotle_verifier import (
    AristotleClient,
    AristotleConfig,
    AristotleResult,
    assess_project,
    has_incomplete_proof,
    parse_project_id,
    parse_state,
    verify_run,
    write_formal_proof_evidence,
)
from run_verified_pipeline import load_evidence

PROJECT_ID = "265eb121-51bf-4250-874b-fe85aafde008"
GOOD_LEAN = "import Mathlib\n\ntheorem erdos_x : True := by trivial\n"
SORRY_LEAN = "theorem erdos_x : True := by sorry\n"


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
    def test_complete_no_sorry_is_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "RequestProject").mkdir()
            (root / "RequestProject" / "Main.lean").write_text(GOOD_LEAN, encoding="utf-8")
            result = assess_project("COMPLETE", root, project_id=PROJECT_ID)
            self.assertTrue(result.verified)
            self.assertEqual(result.verdict, "proved")

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
            self.assertEqual(result.verdict, "disproved")


class EvidenceTests(unittest.TestCase):
    def test_emitted_evidence_is_consumable_by_the_gate_loader(self):
        proved = AristotleResult(True, "proved", "COMPLETE", PROJECT_ID, GOOD_LEAN, "ok")
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            make_run(run, statement_sha="b" * 64)
            evidence_path = write_formal_proof_evidence(run, proved, target_outcome="candidate_proved")
            evidence = load_evidence(evidence_path)
            self.assertEqual(len(evidence), 1)
            item = evidence[0]
            self.assertEqual(item.kind, "formal_proof")
            self.assertEqual(item.verifier, "aristotle")
            self.assertTrue(item.passed)
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
    def test_prove_end_to_end_with_fake_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "proj.tar.gz"
            make_archive(archive)
            cli = FakeCLI(archive)
            client = AristotleClient(AristotleConfig(api_key="k"), runner=cli)
            result = client.prove("prove it", target_outcome="candidate_proved")
            self.assertTrue(result.verified)
            self.assertEqual(result.state, "COMPLETE")
            self.assertEqual(result.project_id, PROJECT_ID)
            self.assertIn("theorem", result.lean_source)
            self.assertEqual([c[0] for c in cli.calls], ["submit"])

    def test_prove_reports_sorry_archive_as_unverified(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "proj.tar.gz"
            make_archive(archive, lean=SORRY_LEAN)
            client = AristotleClient(AristotleConfig(api_key="k"), runner=FakeCLI(archive))
            self.assertFalse(client.prove("prove it").verified)

    def test_verify_run_uses_injected_client(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "proj.tar.gz"
            make_archive(archive)
            run = Path(directory) / "run"
            make_run(run)
            client = AristotleClient(AristotleConfig(api_key="k"), runner=FakeCLI(archive))
            result, evidence_path, promoted = verify_run(run, client=client)
            self.assertTrue(result.verified)
            self.assertTrue(evidence_path.is_file())
            self.assertIsNone(promoted)


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

    def test_local_kernel_verification_method(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._project(Path(directory))
            result = assess_project("COMPLETE", root, kernel_runner=FakeLake(0))
            self.assertTrue(result.verified)
            self.assertEqual(result.verification_method, "local_lean_kernel")
            self.assertEqual(result.lean_status, "kernel_verified")

    def test_kernel_build_failure_overrides_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._project(Path(directory))
            result = assess_project("COMPLETE", root, kernel_runner=FakeLake(1))
            self.assertFalse(result.verified)
            self.assertEqual(result.verification_method, "local_lean_kernel")

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
            self.assertEqual(record["formal_statements"], ["theorem t : True"])
            self.assertTrue((run / "aristotle" / "fidelity.json").is_file())

    def test_kernel_verified_passes_require_kernel(self):
        proved = AristotleResult(
            True, "proved", "COMPLETE", PROJECT_ID, GOOD_LEAN, "ok",
            verification_method="local_lean_kernel")
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            make_run(run)
            record = json.loads(write_formal_proof_evidence(
                run, proved, target_outcome="candidate_proved",
                require_kernel=True).read_text())[0]
            self.assertTrue(record["passed"])
            self.assertEqual(record["verification_method"], "local_lean_kernel")


if __name__ == "__main__":
    unittest.main()
