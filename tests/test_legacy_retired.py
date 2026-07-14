"""The legacy pipeline entry points are retired (single-pipeline pivot).

`run_continuous.py`, `run_verified_pipeline.py`, and `run_sol2_batch.py` drove
the legacy `ProofPipeline`, which terminates at `awaiting_authenticated_release`
and can never emit a `ReleaseCertificate`.  They must refuse to run by default
and point at the EGMRA single pipeline; `--force-legacy` remains a deliberate
escape hatch, and the read-only sha utility stays usable.

These invoke each script as a subprocess (argparse ``parser.error`` exits 2) so
the deprecation gate is exercised end-to-end without importing browser deps.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO / script), *args],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )


@pytest.mark.parametrize("script,args", [
    ("run_continuous.py", ["--model-id", "chatgpt-5.6"]),
    ("run_verified_pipeline.py", ["--problem", "312", "--model-id", "chatgpt-5.6"]),
    ("run_sol2_batch.py", ["--model-id", "chatgpt-5.6", "--min", "601", "--max", "602"]),
    ("run_verified_range.py", ["--start", "601", "--end", "602", "--model-id", "chatgpt-5.6"]),
    ("run_adjudication.py", []),
])
def test_legacy_entry_points_refuse_by_default(script, args):
    result = _run(script, *args)
    assert result.returncode == 2, result.stderr
    combined = result.stderr + result.stdout
    assert "RETIRED" in combined
    assert "egmra" in combined  # points at the supported pipeline


def test_run_verified_pipeline_sha_utility_still_works():
    # The read-only --print-statement-sha path must remain usable without
    # --force-legacy (it drives no pipeline).
    result = _run("run_verified_pipeline.py", "--problem", "312",
                  "--model-id", "chatgpt-5.6", "--print-statement-sha")
    assert result.returncode == 0, result.stderr
    assert len(result.stdout.strip()) == 64  # a sha256 hex digest


def test_force_legacy_passes_the_deprecation_gate():
    # With --force-legacy the gate is bypassed; the run then fails later for an
    # environment reason (no browser/creds), NOT the retirement refusal.
    result = _run("run_continuous.py", "--model-id", "chatgpt-5.6",
                  "--force-legacy", "--max-problems", "0")
    combined = result.stderr + result.stdout
    assert "is RETIRED as the production drainer" not in combined
