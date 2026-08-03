import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from run_verification import find_awaiting_runs, verify_awaiting


def make_run(artifacts: Path, problem: int, gate_status: str, run_name="run1") -> Path:
    run = artifacts / f"problem_{problem}" / run_name
    run.mkdir(parents=True)
    (run / "manifest.json").write_text(json.dumps({
        "problem_number": problem,
        "gate": {"status": gate_status},
    }), encoding="utf-8")
    return run


class FindAwaitingTests(unittest.TestCase):
    def test_finds_only_awaiting_and_unverified(self):
        with tempfile.TemporaryDirectory() as directory:
            art = Path(directory)
            awaiting = make_run(art, 1, "awaiting_external_evidence")
            make_run(art, 2, "candidate_rejected")
            make_run(art, 3, "verified_proved")
            self.assertEqual(find_awaiting_runs(art), [awaiting])

    def test_forged_verified_label_elsewhere_does_not_suppress_work(self):
        with tempfile.TemporaryDirectory() as directory:
            art = Path(directory)
            awaiting = make_run(art, 5, "awaiting_external_evidence", "runA")
            make_run(art, 5, "verified_proved", "runB")
            self.assertEqual(find_awaiting_runs(art), [awaiting])

    def test_symlinked_problem_directory_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            art = root / "artifacts"
            art.mkdir()
            outside = root / "outside"
            make_run(outside, 8, "awaiting_external_evidence")
            (art / "problem_8").symlink_to(
                outside / "problem_8", target_is_directory=True,
            )
            self.assertEqual(find_awaiting_runs(art), [])


class VerifyAwaitingTests(unittest.TestCase):
    def test_calls_verify_for_awaiting_and_respects_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            art = Path(directory)
            make_run(art, 1, "awaiting_external_evidence")
            make_run(art, 2, "awaiting_external_evidence")
            calls = []

            def fake_verify(run_dir, **kwargs):
                calls.append((run_dir, kwargs))
                promoted = SimpleNamespace(
                    gate=SimpleNamespace(status="verified_proved", reasons=()))
                result = SimpleNamespace(
                    verified=True, verification_method="local_lean_kernel")
                return result, run_dir / "evidence.json", promoted

            results = verify_awaiting(
                art, verify=fake_verify, limit=1, require_kernel=True)
            self.assertEqual(len(calls), 1)               # limit respected
            self.assertEqual(results[0][1], "verified_proved")
            self.assertTrue(calls[0][1]["require_kernel"])
            self.assertTrue(calls[0][1]["promote_result"])

    def test_one_failure_does_not_stop_the_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            art = Path(directory)
            make_run(art, 1, "awaiting_external_evidence")
            make_run(art, 2, "awaiting_external_evidence")

            def flaky(run_dir, **kwargs):
                if run_dir.parent.name == "problem_1":
                    raise RuntimeError("boom")
                result = SimpleNamespace(verified=True, verification_method="x")
                return result, None, None

            results = verify_awaiting(art, verify=flaky)
            self.assertEqual(len(results), 2)
            self.assertTrue(any(s.startswith("error:") for _, s in results))


if __name__ == "__main__":
    unittest.main()
