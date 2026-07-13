import subprocess
import tempfile
import unittest
from pathlib import Path

from lean_verify import (
    BUILD_FAILED,
    HAS_SORRY,
    KERNEL_VERIFIED,
    NO_PROJECT,
    TOOL_UNAVAILABLE,
    extract_formal_statements,
    has_incomplete_proof,
    verify_project,
)


class FakeLake:
    def __init__(self, build_rc=0):
        self.build_rc = build_rc
        self.calls = []

    def __call__(self, args, cwd):
        self.calls.append((args, cwd))
        rc = 0 if args[:2] == ["exe", "cache"] else self.build_rc
        return subprocess.CompletedProcess(args, rc, "out", "boom" if rc else "")


def make_project(root: Path, *, lean="import Mathlib\ntheorem t : True := trivial\n") -> Path:
    proj = root / "proj"
    (proj / "RequestProject").mkdir(parents=True)
    (proj / "lakefile.toml").write_text("[[require]]\nname = \"mathlib\"\n", encoding="utf-8")
    (proj / "lean-toolchain").write_text("leanprover/lean4:v4.28.0", encoding="utf-8")
    (proj / "RequestProject" / "Main.lean").write_text(lean, encoding="utf-8")
    return proj


class LeanVerifyTests(unittest.TestCase):
    def test_kernel_verified_on_successful_build(self):
        with tempfile.TemporaryDirectory() as directory:
            make_project(Path(directory))
            lake = FakeLake(build_rc=0)
            result = verify_project(Path(directory), runner=lake)
            self.assertEqual(result.status, KERNEL_VERIFIED)
            self.assertTrue(result.kernel_verified)
            self.assertEqual(result.lean_toolchain, "leanprover/lean4:v4.28.0")
            self.assertIn((["build"], result.project_root), lake.calls)

    def test_build_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            make_project(Path(directory))
            result = verify_project(Path(directory), runner=FakeLake(build_rc=1))
            self.assertEqual(result.status, BUILD_FAILED)
            self.assertFalse(result.kernel_verified)

    def test_sorry_short_circuits_before_build(self):
        with tempfile.TemporaryDirectory() as directory:
            make_project(Path(directory), lean="theorem t : True := by sorry\n")
            lake = FakeLake(build_rc=0)
            result = verify_project(Path(directory), runner=lake)
            self.assertEqual(result.status, HAS_SORRY)
            self.assertEqual(lake.calls, [])  # never ran lake

    def test_no_project(self):
        with tempfile.TemporaryDirectory() as directory:
            result = verify_project(Path(directory), runner=FakeLake())
            self.assertEqual(result.status, NO_PROJECT)

    def test_tool_unavailable_when_lake_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            make_project(Path(directory))
            result = verify_project(Path(directory), lake_path="/nonexistent/lake/binary")
            self.assertEqual(result.status, TOOL_UNAVAILABLE)
            self.assertFalse(result.kernel_verified)


class HelperTests(unittest.TestCase):
    def test_has_incomplete_proof(self):
        self.assertFalse(has_incomplete_proof("theorem t : True := trivial"))
        self.assertTrue(has_incomplete_proof("theorem t := by sorry"))
        self.assertFalse(has_incomplete_proof("-- sorry, not really\ntheorem t := trivial"))

    def test_extract_formal_statements(self):
        source = (
            "import Mathlib\n"
            "theorem foo (n : Nat) : n + 0 = n := by simp\n"
            "lemma bar : True := trivial\n"
        )
        statements = extract_formal_statements(source)
        self.assertEqual(statements, [
            "theorem foo (n : Nat) : n + 0 = n",
            "lemma bar : True",
        ])


if __name__ == "__main__":
    unittest.main()
