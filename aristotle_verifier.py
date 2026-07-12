#!/usr/bin/env python3
"""Aristotle (Harmonic) Lean-verification adapter for the deterministic gate.

The verified pipeline already *consumes* external formal evidence: ``verification
.evaluate_gate`` promotes a run to ``verified_proved`` only when the independent
reviews pass AND a trusted ``formal_proof`` ``VerificationEvidence`` is present,
and ``promote_verified_run.py`` applies such evidence to a run. This module is the
missing *producer*: it sends a run's locked informal statement to Aristotle, which
autoformalizes and proves it in Lean, then emits the ``formal_proof`` evidence JSON
(plus the Lean artifact) in exactly the shape ``promote_verified_run`` expects.

Access is HTTP + bearer token, configured entirely from the environment so no
vendor endpoint or schema is hard-coded:

    ARISTOTLE_API_BASE      full URL of the prove endpoint (required)
    ARISTOTLE_API_KEY       bearer token, read from env/.env only (required)
    ARISTOTLE_STATEMENT_FIELD  request field carrying the statement (default "statement")
    ARISTOTLE_MODEL         optional model/profile field sent in the request
    ARISTOTLE_AUTH_SCHEME   auth scheme (default "Bearer")
    ARISTOTLE_RESULT_URL    optional async result URL template containing "{job_id}"
    ARISTOTLE_POLL_INTERVAL_S / ARISTOTLE_TIMEOUT_S

The response field mapping is centralized in ``parse_aristotle_response`` (it tries
the common field names); confirm it against Harmonic's live API and adjust there.

Usage:
    ARISTOTLE_API_BASE=... ARISTOTLE_API_KEY=... \\
      .venv/bin/python aristotle_verifier.py --run-dir <run> --promote --publish
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_TIMEOUT_S = 1800.0
DEFAULT_POLL_INTERVAL_S = 10.0
_TRUTHY = {"true", "1", "yes", "ok", "success", "valid"}
_PROVED = {"proved", "verified", "valid", "success", "true", "ok", "qed"}
_DISPROVED = {"disproved", "refuted", "false", "counterexample"}


class AristotleError(RuntimeError):
    """Raised when Aristotle cannot be reached or returns an unusable response."""


@dataclass(frozen=True)
class AristotleConfig:
    base_url: str
    api_key: str
    statement_field: str = "statement"
    auth_scheme: str = "Bearer"
    model: str = ""
    extra_fields: dict = field(default_factory=dict)
    result_url: str = ""
    poll_interval_s: float = DEFAULT_POLL_INTERVAL_S
    timeout_s: float = DEFAULT_TIMEOUT_S

    @classmethod
    def from_env(cls, env: dict | None = None) -> "AristotleConfig":
        env = env if env is not None else os.environ
        base = str(env.get("ARISTOTLE_API_BASE", "")).strip()
        key = str(env.get("ARISTOTLE_API_KEY", "")).strip()
        if not base:
            raise AristotleError(
                "ARISTOTLE_API_BASE is not set; point it at the Aristotle prove endpoint"
            )
        if not key:
            raise AristotleError(
                "ARISTOTLE_API_KEY is not set; put the token in the environment or .env"
            )
        return cls(
            base_url=base,
            api_key=key,
            statement_field=str(env.get("ARISTOTLE_STATEMENT_FIELD", "statement")),
            auth_scheme=str(env.get("ARISTOTLE_AUTH_SCHEME", "Bearer")),
            model=str(env.get("ARISTOTLE_MODEL", "")),
            result_url=str(env.get("ARISTOTLE_RESULT_URL", "")),
            poll_interval_s=float(env.get("ARISTOTLE_POLL_INTERVAL_S", DEFAULT_POLL_INTERVAL_S)),
            timeout_s=float(env.get("ARISTOTLE_TIMEOUT_S", DEFAULT_TIMEOUT_S)),
        )


@dataclass(frozen=True)
class AristotleResult:
    verified: bool
    verdict: str          # "proved" | "disproved" | "unknown"
    lean_source: str
    formal_statement: str
    raw: dict


def _first(raw: dict, *keys: str, default: Any = "") -> Any:
    for key in keys:
        value = raw.get(key)
        if value not in (None, ""):
            return value
    return default


def parse_aristotle_response(raw: Any) -> AristotleResult:
    """Normalize Aristotle's JSON. Field names are best-effort across common
    shapes; this is the single place to adjust for the live API."""
    if not isinstance(raw, dict):
        raise AristotleError("Aristotle response was not a JSON object")
    lean_source = str(_first(raw, "lean", "lean_code", "lean_proof", "proof", "code"))
    formal_statement = str(_first(raw, "formal_statement", "lean_statement", "theorem"))
    verdict_raw = str(_first(raw, "outcome", "result", "verdict", "status")).strip().lower()
    verified_flag = _first(raw, "verified", "is_verified", "kernel_verified", "success", default=None)
    verified = (
        verified_flag is True
        or (isinstance(verified_flag, str) and verified_flag.strip().lower() in _TRUTHY)
        or verdict_raw in _PROVED
    )
    if verdict_raw in _PROVED:
        verdict = "proved"
    elif verdict_raw in _DISPROVED:
        verdict = "disproved"
    else:
        verdict = "proved" if verified else "unknown"
    # A formal proof is trustworthy only if the kernel accepted it AND we were
    # actually handed Lean source to persist as the audit artifact.
    verified = bool(verified and lean_source.strip())
    return AristotleResult(verified, verdict, lean_source, formal_statement, raw)


class AristotleClient:
    """Thin HTTP client; stdlib-only so the module has no runtime dependency."""

    def __init__(self, config: AristotleConfig):
        self.config = config

    def _headers(self) -> dict[str, str]:
        token = f"{self.config.auth_scheme} {self.config.api_key}".strip()
        return {"Content-Type": "application/json", "Authorization": token}

    def _send(self, request: urllib.request.Request) -> dict:
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_s) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            raise AristotleError(f"Aristotle HTTP {error.code}: {error.reason}") from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise AristotleError(f"Aristotle request failed: {error}") from error
        try:
            return json.loads(body)
        except ValueError as error:
            raise AristotleError("Aristotle returned a non-JSON response") from error

    def _post(self, url: str, payload: dict) -> dict:
        data = json.dumps(payload).encode("utf-8")
        return self._send(urllib.request.Request(
            url, data=data, headers=self._headers(), method="POST"))

    def _get(self, url: str) -> dict:
        return self._send(urllib.request.Request(
            url, headers=self._headers(), method="GET"))

    def _poll(self, job_id: str) -> dict:
        deadline = time.time() + self.config.timeout_s
        url = self.config.result_url.format(job_id=job_id)
        while time.time() < deadline:
            raw = self._get(url)
            status = str(raw.get("status", "")).strip().lower()
            terminal = status in {
                "completed", "complete", "done", "succeeded", "finished",
                "failed", "error", *(_PROVED | _DISPROVED),
            }
            if terminal or raw.get("verified") is not None or _first(
                raw, "lean", "lean_code", "proof", default=None
            ) is not None:
                return raw
            time.sleep(self.config.poll_interval_s)
        raise AristotleError("Aristotle result polling timed out")

    def prove(self, statement: str) -> AristotleResult:
        payload: dict[str, Any] = {self.config.statement_field: statement}
        if self.config.model:
            payload["model"] = self.config.model
        payload.update(self.config.extra_fields)
        raw = self._post(self.config.base_url, payload)
        if self.config.result_url:
            job_id = str(_first(raw, "id", "job_id", "task_id", "request_id"))
            if job_id:
                raw = self._poll(job_id)
        return parse_aristotle_response(raw)


def _read_manifest(run_dir: Path) -> dict:
    return json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))


def _statement_for_run(run_dir: Path, manifest: dict) -> str:
    problem_txt = run_dir / "problem.txt"
    if problem_txt.is_file():
        return problem_txt.read_text(encoding="utf-8")
    return str(manifest.get("statement", ""))


def write_formal_proof_evidence(
    run_dir: Path, result: AristotleResult, *, verifier: str = "aristotle",
) -> Path:
    """Persist the Lean artifact and a ``formal_proof`` evidence JSON for the gate.

    ``passed`` is true only when Aristotle's kernel-checked verdict *agrees with
    the candidate's own claimed direction* — a formal proof of the opposite of
    what ChatGPT claimed must never promote the candidate.
    """
    run_dir = Path(run_dir)
    manifest = _read_manifest(run_dir)
    candidate_path = run_dir / "candidate.md"
    candidate_sha256 = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
    statement_sha256 = str(manifest.get("statement_sha256", ""))
    candidate_outcome = str(manifest.get("candidate_outcome", "")).strip().lower()
    target_outcome = (
        candidate_outcome
        if candidate_outcome in {"candidate_proved", "candidate_disproved"}
        else "candidate_proved"
    )
    aristotle_outcome = {
        "proved": "candidate_proved", "disproved": "candidate_disproved",
    }.get(result.verdict, "")
    agrees = aristotle_outcome == target_outcome
    passed = bool(result.verified and agrees)

    artifact_dir = run_dir / "aristotle"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / "proof.lean"
    artifact_path.write_text(result.lean_source or "", encoding="utf-8")
    # Persist the autoformalized statement + raw response for statement-fidelity
    # review (the Lean statement faithfully matching the Erdos problem is a
    # separate, still-manual audit).
    (artifact_dir / "formal_statement.lean").write_text(
        result.formal_statement or "", encoding="utf-8")
    (artifact_dir / "aristotle_response.json").write_text(
        json.dumps(result.raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    record = {
        "kind": "formal_proof",
        "verifier": verifier,
        "outcome": target_outcome,
        "statement_sha256": statement_sha256,
        "candidate_sha256": candidate_sha256,
        "artifact_path": str(artifact_path),
        "passed": passed,
        "aristotle_verdict": result.verdict,
        "aristotle_agrees_with_candidate": agrees,
    }
    evidence_path = artifact_dir / "evidence.json"
    evidence_path.write_text(
        json.dumps([record], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return evidence_path


def verify_run(
    run_dir: Path,
    *,
    config: AristotleConfig | None = None,
    client: AristotleClient | None = None,
    promote_result: bool = False,
    publish: bool = False,
    triage_dir: Path | None = None,
    category: str = "open",
):
    """Run Aristotle on a completed proof run and emit formal evidence.

    Returns ``(AristotleResult, evidence_path, promoted_or_None)``. Passing
    ``promote_result`` (or ``publish``) applies the evidence through the gate via
    ``promote_verified_run.promote``.
    """
    run_dir = Path(run_dir)
    manifest = _read_manifest(run_dir)
    statement = _statement_for_run(run_dir, manifest)
    if not statement.strip():
        raise AristotleError(f"run {run_dir} has no statement to verify")
    client = client or AristotleClient(config or AristotleConfig.from_env())
    result = client.prove(statement)
    evidence_path = write_formal_proof_evidence(run_dir, result)
    promoted = None
    if promote_result or publish:
        from promote_verified_run import promote  # lazy: avoids heavy imports
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
    print(f"aristotle verdict: {result.verdict}  verified={result.verified}")
    print(f"evidence: {evidence_path}")
    if promoted is not None:
        print(f"gate: {promoted.gate.status}")
        for reason in promoted.gate.reasons:
            print(f"- {reason}")


if __name__ == "__main__":
    main()
