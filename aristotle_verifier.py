#!/usr/bin/env python3
"""Aristotle (Harmonic) Lean-verification adapter — `aristotle` CLI wrapper.

Harmonic's Aristotle (https://aristotle.harmonic.fun) is driven through the
`aristotle` CLI from the `aristotlelib` package (NOT a raw HTTP API):

    aristotle submit "<prompt>" [--project-dir DIR]   -> prints a project id
    aristotle show <project_id>                        -> "COMPLETE ..." + summary
    aristotle download <project_id> --destination <a>  -> tar.gz project archive

The API key is read from ARISTOTLE_API_KEY (env or .env); no base URL is used.
A completed archive contains `RequestProject/Main.lean` (the Lean proof) and
`ARISTOTLE_SUMMARY.md`. A proof is trusted only when the project is COMPLETE and
`Main.lean` exists with no `sorry`/`admit`.

This adapter submits a run's locked statement (with the candidate as reference),
waits for completion, extracts the Lean proof, and emits a `formal_proof`
VerificationEvidence that `promote_verified_run` feeds to the deterministic gate.

Usage:
    ARISTOTLE_API_KEY=... .venv/bin/python aristotle_verifier.py \\
        --run-dir <run> --promote --publish
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from lean_verify import (
    BUILD_FAILED,
    HAS_SORRY,
    KERNEL_VERIFIED,
    TOOL_UNAVAILABLE,
    extract_formal_statements,
    find_lean_proof,
    has_incomplete_proof,
    verify_project,
)

DEFAULT_TIMEOUT_S = 6 * 60 * 60.0
DEFAULT_POLL_INTERVAL_S = 30.0
_UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
_STATE_RE = re.compile(
    r"\b(COMPLETE|COMPLETED|SUCCEEDED|RUNNING|IDLE|QUEUED|PENDING|FAILED|ERROR|CANCELLED|CANCELED)\b",
    re.IGNORECASE,
)
_TERMINAL_OK = {"COMPLETE", "COMPLETED", "SUCCEEDED"}
_TERMINAL_BAD = {"FAILED", "ERROR", "CANCELLED", "CANCELED"}


class AristotleError(RuntimeError):
    """Raised when the Aristotle CLI is missing, fails, or returns no proof."""


def _load_dotenv_files() -> None:
    """Populate os.environ from the repo .env and the workspace-level .env.

    The first non-empty value for a key wins and a real environment variable
    always wins (empty placeholder lines are ignored).
    """
    here = Path(__file__).resolve().parent
    for path in (here / ".env", here.parent / ".env"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if value and os.environ.get(key, "") == "":
                os.environ[key] = value


def _default_cli_path() -> str:
    # Do not resolve() sys.executable: that follows the venv symlink to the real
    # interpreter and loses the venv's bin dir where the console script lives.
    for candidate in (
        Path(sys.executable).parent / "aristotle",
        Path(sys.prefix) / "bin" / "aristotle",
    ):
        if candidate.exists():
            return str(candidate)
    return shutil.which("aristotle") or "aristotle"


@dataclass(frozen=True)
class AristotleConfig:
    api_key: str
    cli_path: str = ""
    poll_interval_s: float = DEFAULT_POLL_INTERVAL_S
    timeout_s: float = DEFAULT_TIMEOUT_S

    @classmethod
    def from_env(cls, env: dict | None = None) -> "AristotleConfig":
        if env is None:
            _load_dotenv_files()
            env = os.environ
        key = str(env.get("ARISTOTLE_API_KEY", "")).strip()
        if not key:
            raise AristotleError(
                "ARISTOTLE_API_KEY is not set; put the Harmonic Aristotle key in .env"
            )
        return cls(
            api_key=key,
            cli_path=str(env.get("ARISTOTLE_CLI", "")).strip() or _default_cli_path(),
            poll_interval_s=float(env.get("ARISTOTLE_POLL_INTERVAL_S", DEFAULT_POLL_INTERVAL_S)),
            timeout_s=float(env.get("ARISTOTLE_TIMEOUT_S", DEFAULT_TIMEOUT_S)),
        )


@dataclass(frozen=True)
class AristotleResult:
    verified: bool
    verdict: str          # "proved" | "disproved" | "unknown"
    state: str
    project_id: str
    lean_source: str
    summary: str
    verification_method: str = "aristotle_reported"  # or "local_lean_kernel"
    lean_status: str = "not_checked"
    formal_statements: tuple = ()
    raw: dict = field(default_factory=dict)


# ── pure parsing / assessment helpers (unit-testable, no CLI) ────────────────

def parse_project_id(text: str) -> str:
    match = _UUID_RE.search(text or "")
    return match.group(0) if match else ""


def parse_state(show_output: str) -> str:
    match = _STATE_RE.search(show_output or "")
    return match.group(1).upper() if match else "UNKNOWN"


def read_summary(root: Path) -> str:
    summaries = sorted(root.rglob("ARISTOTLE_SUMMARY.md"))
    if not summaries:
        return ""
    return summaries[0].read_text(encoding="utf-8", errors="ignore")


def assess_project(state: str, extracted_root: Path, *, project_id: str = "",
                   target_outcome: str = "candidate_proved",
                   run_kernel: bool = True, kernel_runner=None,
                   fetch_cache: bool = True) -> AristotleResult:
    """Turn a downloaded, extracted project into a trust decision.

    When Lean/lake is available the proof is independently re-checked by the
    local kernel (``verification_method="local_lean_kernel"``); otherwise it
    falls back to Aristotle's own COMPLETE + no-sorry report
    (``"aristotle_reported"``), which is recorded so a strict policy can refuse
    to promote on an unverified-by-kernel proof.
    """
    root = Path(extracted_root)
    lean_file = find_lean_proof(root)
    lean_source = lean_file.read_text(encoding="utf-8", errors="ignore") if lean_file else ""
    summary = read_summary(root)
    formal_statements = tuple(extract_formal_statements(lean_source))

    complete = bool(
        state.upper() in _TERMINAL_OK
        and lean_source.strip()
        and not has_incomplete_proof(lean_source)
    )
    method = "aristotle_reported"
    lean_status = "not_checked"
    if run_kernel and complete:
        verification = verify_project(root, runner=kernel_runner, fetch_cache=fetch_cache)
        lean_status = verification.status
        if verification.status == KERNEL_VERIFIED:
            method = "local_lean_kernel"
        elif verification.status in (BUILD_FAILED, HAS_SORRY):
            method = "local_lean_kernel"
            complete = False  # the kernel overrides a vendor-reported "complete"

    verified = bool(complete)
    if verified:
        verdict = "disproved" if target_outcome == "candidate_disproved" else "proved"
    else:
        verdict = "unknown"
    return AristotleResult(
        verified=verified, verdict=verdict, state=state.upper(),
        project_id=project_id, lean_source=lean_source, summary=summary,
        verification_method=method, lean_status=lean_status,
        formal_statements=formal_statements,
        raw={"lean_file": str(lean_file) if lean_file else ""},
    )


# ── CLI client ───────────────────────────────────────────────────────────────

class AristotleClient:
    """Wraps the `aristotle` CLI; the command runner is injectable for tests."""

    def __init__(self, config: AristotleConfig, runner=None):
        self.config = config
        self._runner = runner or self._default_runner

    def _default_runner(self, args: list[str]) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env["ARISTOTLE_API_KEY"] = self.config.api_key
        return subprocess.run(
            [self.config.cli_path, *args],
            capture_output=True, text=True, env=env, check=False,
            timeout=self.config.timeout_s,
        )

    def _run(self, args: list[str]) -> str:
        try:
            proc = self._runner(args)
        except FileNotFoundError as error:
            raise AristotleError(
                f"aristotle CLI not found at '{self.config.cli_path}'; "
                "install with `pip install aristotlelib`"
            ) from error
        except subprocess.TimeoutExpired as error:
            raise AristotleError(
                f"aristotle {args[0]} timed out after {self.config.timeout_s:.0f}s"
            ) from error
        if getattr(proc, "returncode", 1) != 0:
            raise AristotleError(
                f"aristotle {args[0]} failed (exit {proc.returncode}): "
                f"{(proc.stderr or proc.stdout or '').strip()[:400]}"
            )
        # The CLI prints identifiers/status to stdout or stderr depending on the
        # subcommand (e.g. `submit` writes "Project created: <id>" to stderr), so
        # parse from both streams.
        return "\n".join(part for part in (proc.stdout, proc.stderr) if part)

    def submit(self, prompt: str, *, project_dir: Path | None = None) -> str:
        args = ["submit", prompt]
        if project_dir is not None:
            args += ["--project-dir", str(project_dir)]
        project_id = parse_project_id(self._run(args))
        if not project_id:
            raise AristotleError("aristotle submit did not return a project id")
        return project_id

    def show(self, project_id: str) -> str:
        return self._run(["show", project_id])

    def project_status(self, project_id: str) -> str:
        """Non-streaming project status (RUNNING/IDLE/...) via `list`.

        `show` follows a running project and never returns, so status polling
        must go through `list` instead.
        """
        for line in self._run(["list", "--limit", "100"]).splitlines():
            if project_id in line:
                tokens = line.split()
                return tokens[-1].upper() if tokens else "UNKNOWN"
        return "UNKNOWN"

    def download(self, project_id: str, destination: Path) -> Path:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._run(["download", project_id, "--destination", str(destination)])
        if not destination.exists():
            raise AristotleError("aristotle download produced no archive")
        return destination

    def prove(self, prompt: str, *, project_dir: Path | None = None,
              target_outcome: str = "candidate_proved") -> AristotleResult:
        # `submit --wait` blocks server-side until the proof finishes and writes
        # the completed project archive; this avoids `show`, which streams a
        # running project's events and never returns.
        with tempfile.TemporaryDirectory() as work:
            archive = Path(work) / "project.tar.gz"
            args = ["submit", prompt]
            if project_dir is not None:
                args += ["--project-dir", str(project_dir)]
            args += ["--wait", "--destination", str(archive)]
            output = self._run(args)
            project_id = parse_project_id(output)
            if not archive.exists():
                raise AristotleError("aristotle submit --wait produced no archive")
            extracted = Path(work) / "extracted"
            extracted.mkdir()
            with tarfile.open(archive, "r:*") as tar:
                tar.extractall(extracted, filter="data")  # guard path traversal
            return assess_project(
                "COMPLETE", extracted, project_id=project_id,
                target_outcome=target_outcome,
            )


# ── evidence emission + run integration ──────────────────────────────────────

def _read_manifest(run_dir: Path) -> dict:
    return json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))


def _statement_for_run(run_dir: Path, manifest: dict) -> str:
    problem_txt = run_dir / "problem.txt"
    if problem_txt.is_file():
        return problem_txt.read_text(encoding="utf-8")
    return str(manifest.get("statement", ""))


def _build_prompt(statement: str, target_outcome: str) -> str:
    goal = (
        "prove that it is FALSE (i.e. prove its negation)"
        if target_outcome == "candidate_disproved"
        else "prove that it is TRUE"
    )
    return (
        "Formalize the following mathematical statement in Lean 4 using Mathlib "
        f"and {goal}. Produce a complete Lean proof with no `sorry`.\n\n"
        f"Statement:\n{statement.strip()}\n"
    )


def write_formal_proof_evidence(
    run_dir: Path, result: AristotleResult, *,
    target_outcome: str, verifier: str = "aristotle",
    require_kernel: bool = False,
) -> Path:
    """Persist the Lean artifact and a `formal_proof` evidence JSON for the gate.

    ``passed`` requires a COMPLETE, sorry-free Lean proof for the candidate's own
    claimed direction. With ``require_kernel`` it additionally requires that the
    proof was re-checked by the local Lean kernel (not merely Aristotle-reported).
    The autoformalized theorem statements are captured for a separate
    statement-fidelity review (``statement_fidelity="unreviewed"``): a kernel pass
    proves the Lean theorem, not that it faithfully models the Erdos problem.
    """
    run_dir = Path(run_dir)
    manifest = _read_manifest(run_dir)
    candidate_path = run_dir / "candidate.md"
    candidate_sha256 = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
    statement_sha256 = str(manifest.get("statement_sha256", ""))
    target = (
        target_outcome
        if target_outcome in {"candidate_proved", "candidate_disproved"}
        else "candidate_proved"
    )
    kernel_ok = result.verification_method == "local_lean_kernel"
    passed = bool(
        result.verified
        and result.verdict != "unknown"
        and (not require_kernel or kernel_ok)
    )

    artifact_dir = run_dir / "aristotle"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / "Main.lean"
    artifact_path.write_text(result.lean_source or "", encoding="utf-8")
    (artifact_dir / "ARISTOTLE_SUMMARY.md").write_text(result.summary or "", encoding="utf-8")
    # Capture informal vs formal statements for the fidelity review.
    (artifact_dir / "fidelity.json").write_text(json.dumps({
        "informal_statement": _statement_for_run(run_dir, manifest),
        "formal_statements": list(result.formal_statements),
        "statement_fidelity": "unreviewed",
        "note": "A kernel pass proves the Lean theorem; a human/independent review "
                "must confirm the Lean statement faithfully models the Erdos problem.",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    record = {
        "kind": "formal_proof",
        "verifier": verifier,
        "outcome": target,
        "statement_sha256": statement_sha256,
        "candidate_sha256": candidate_sha256,
        "artifact_path": str(artifact_path),
        "passed": passed,
        "verification_method": result.verification_method,
        "lean_status": result.lean_status,
        "statement_fidelity": "unreviewed",
        "formal_statements": list(result.formal_statements),
        "aristotle_project_id": result.project_id,
        "aristotle_state": result.state,
        "aristotle_verdict": result.verdict,
    }
    evidence_path = artifact_dir / "evidence.json"
    evidence_path.write_text(
        json.dumps([record], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return evidence_path


def verify_run(
    run_dir: Path, *,
    config: AristotleConfig | None = None,
    client: AristotleClient | None = None,
    promote_result: bool = False,
    publish: bool = False,
    triage_dir: Path | None = None,
    category: str = "open",
    require_kernel: bool = False,
):
    """Verify a completed proof run with Aristotle and emit formal evidence.

    Returns ``(AristotleResult, evidence_path, promoted_or_None)``.
    """
    run_dir = Path(run_dir)
    manifest = _read_manifest(run_dir)
    statement = _statement_for_run(run_dir, manifest)
    if not statement.strip():
        raise AristotleError(f"run {run_dir} has no statement to verify")
    target = str(manifest.get("candidate_outcome", "")).strip().lower()
    if target not in {"candidate_proved", "candidate_disproved"}:
        target = "candidate_proved"

    project_dir = run_dir / "aristotle" / "input"
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "statement.md").write_text(statement, encoding="utf-8")
    candidate = run_dir / "candidate.md"
    if candidate.exists():
        (project_dir / "candidate.md").write_text(
            candidate.read_text(encoding="utf-8"), encoding="utf-8")

    client = client or AristotleClient(config or AristotleConfig.from_env())
    result = client.prove(
        _build_prompt(statement, target), project_dir=project_dir, target_outcome=target,
    )
    evidence_path = write_formal_proof_evidence(
        run_dir, result, target_outcome=target, require_kernel=require_kernel)
    promoted = None
    if promote_result or publish:
        from promote_verified_run import promote
        promoted = promote(
            run_dir, evidence_path, publish=publish, category=category,
            triage_dir=Path(triage_dir) if triage_dir is not None else None,
        )
    return result, evidence_path, promoted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--promote", action="store_true",
                        help="apply the evidence to the gate via promote_verified_run")
    parser.add_argument("--publish", action="store_true",
                        help="publish if the gate promotes (implies --promote)")
    parser.add_argument("--triage", type=Path, default=Path("triage"))
    parser.add_argument("--category", default="open")
    args = parser.parse_args()
    result, evidence_path, promoted = verify_run(
        args.run_dir.resolve(),
        config=AristotleConfig.from_env(),
        promote_result=args.promote or args.publish,
        publish=args.publish,
        triage_dir=args.triage.resolve(),
        category=args.category,
    )
    print(f"aristotle: project={result.project_id} state={result.state} "
          f"verified={result.verified}")
    print(f"evidence: {evidence_path}")
    if promoted is not None:
        print(f"gate: {promoted.gate.status}")
        for reason in promoted.gate.reasons:
            print(f"- {reason}")


if __name__ == "__main__":
    main()
