#!/usr/bin/env python3
"""Decoupled distinct-model adjudication pass (DeepSeek).

DeepSeek allows only one in-flight message and one browser profile, so the
distinct adjudicator cannot run inside every parallel ChatGPT worker. This pass
runs as a SINGLE process. A browser URL or caller-supplied ``deepseek`` label is
not authenticated model identity, so the default CLI records an advisory result
only. Gate mutation additionally requires a separately configured review-
attestation gateway binding the exact model/version, authority, candidate,
statement, and response to the review trust key.

The distinct verdict replaces the same-model adjudicator in the gate, so a
correlated blind spot in the ChatGPT self-review is caught *before* expensive
Aristotle verification is spent on it:

  * DeepSeek agrees  -> gate stays ``awaiting_external_evidence`` (proceed to
    formal verification).
  * DeepSeek dissents -> gate becomes ``candidate_rejected`` (do not spend
    Aristotle; the run is flagged for attention).
  * malformed DeepSeek output -> advisory only; the gate is left untouched.

A kernel-verified formal proof always overrides this signal, so a false dissent
only defers, never permanently blocks, a genuine proof.

Usage (single process, honours DeepSeek's one-at-a-time limit):
  .venv/bin/python run_adjudication.py --artifacts proof_runs_sol2
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from research_state import StatementLock, statement_lock_text
from solver_prompts import ADJUDICATOR_PROMPT_TEMPLATE, OFFLINE_POLICY
from proof_pipeline import (
    REVIEW_MANDATES,
    _failed_review,
    _json_object,
    _require_real_directory,
    _review,
)
from verification import (
    GateDecision,
    Review,
    VerificationEvidence,
    candidate_contract,
    evaluate_gate,
    verify_review_attestation,
)
from promote_verified_run import load_reviews
from run_status import has_verified_result

AWAITING = "awaiting_external_evidence"
ADJ_FILE = "deepseek_adjudication.json"
ADJ_STAGE = "deepseek_adjudication"
ONLY_EVIDENCE_MISSING = ("no trusted external or mechanical verification evidence",)
_MAX_ARTIFACT_BYTES = 8 * 1024 * 1024


def _read_text_nofollow(path: Path, *, max_bytes: int = _MAX_ARTIFACT_BYTES) -> str:
    """Read one bounded regular file without following its final symlink."""
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"adjudication input is not a regular file: {path}")
        if metadata.st_size > max_bytes:
            raise ValueError(f"adjudication input exceeds {max_bytes} bytes: {path}")
        remaining = max_bytes + 1
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(65536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > max_bytes:
            raise ValueError(f"adjudication input exceeds {max_bytes} bytes: {path}")
        return payload.decode("utf-8")
    finally:
        os.close(descriptor)


def _require_confined_run_directory(run_dir: Path) -> None:
    """Validate the artifact/problem/run chain without following symlinks."""
    run_dir = Path(run_dir)
    problem_dir = run_dir.parent
    artifact_root = problem_dir.parent
    if not re.fullmatch(r"problem_[1-9][0-9]*", problem_dir.name):
        raise ValueError(f"invalid problem directory: {problem_dir}")
    _require_real_directory(artifact_root, label="adjudication artifact root")
    _require_real_directory(problem_dir, label="adjudication problem directory")
    _require_real_directory(run_dir, label="adjudication execution directory")


def _write_json_confined(run_dir: Path, filename: str, value: object) -> None:
    """Atomically write directly through no-follow root/problem/run dirfds."""
    if Path(filename).name != filename:
        raise ValueError("adjudication output filename must be a basename")
    _require_confined_run_directory(run_dir)
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    artifact_root = run_dir.parent.parent
    root_fd = os.open(artifact_root, directory_flags)
    problem_fd = run_fd = None
    temporary = f".{filename}.{uuid.uuid4().hex}.tmp"
    try:
        problem_fd = os.open(run_dir.parent.name, directory_flags, dir_fd=root_fd)
        run_fd = os.open(run_dir.name, directory_flags, dir_fd=problem_fd)
        payload = (
            json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        ).encode("utf-8")
        output_fd = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=run_fd,
        )
        try:
            with os.fdopen(output_fd, "wb", closefd=False) as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            os.close(output_fd)
        os.replace(
            temporary,
            filename,
            src_dir_fd=run_fd,
            dst_dir_fd=run_fd,
        )
        os.fsync(run_fd)
    finally:
        if run_fd is not None:
            try:
                os.unlink(temporary, dir_fd=run_fd)
            except FileNotFoundError:
                pass
            os.close(run_fd)
        if problem_fd is not None:
            os.close(problem_fd)
        os.close(root_fd)


def _run_dirs(artifacts: Path):
    artifacts = Path(artifacts)
    try:
        _require_real_directory(artifacts, label="adjudication artifact root")
    except ValueError:
        if not artifacts.exists() and not artifacts.is_symlink():
            return
        raise
    for problem_dir in sorted(artifacts.iterdir()):
        if not problem_dir.name.startswith("problem_"):
            continue
        try:
            _require_real_directory(problem_dir, label="adjudication problem directory")
        except ValueError:
            continue
        for run_dir in sorted(problem_dir.iterdir()):
            try:
                _require_real_directory(run_dir, label="adjudication execution directory")
            except ValueError:
                continue
            yield run_dir


def find_adjudicatable_runs(artifacts: Path) -> list[Path]:
    """Awaiting runs not yet distinct-adjudicated and not already verified."""
    out: list[Path] = []
    artifacts = Path(artifacts)
    for run_dir in _run_dirs(artifacts):
        marker = run_dir / ADJ_FILE
        if marker.exists() or marker.is_symlink():
            try:
                marker_record = json.loads(_read_text_nofollow(marker))
            except (OSError, ValueError, json.JSONDecodeError):
                marker_record = None
            if (
                isinstance(marker_record, dict)
                and marker_record.get("authenticated") is True
                and marker_record.get("applied") is True
            ):
                continue
        try:
            manifest = json.loads(_read_text_nofollow(run_dir / "manifest.json"))
        except (OSError, ValueError):
            continue
        gate_status = str(manifest.get("gate", {}).get("status", ""))
        problem = manifest.get("problem_number")
        if (gate_status == AWAITING and isinstance(problem, int)
                and not has_verified_result(artifacts, problem)):
            out.append(run_dir)
    return out


# ── prompt reconstruction from persisted artifacts ───────────────────────────

def _latest_attempt_dir(run_dir: Path) -> Path | None:
    attempts = []
    for directory in run_dir.glob("attempt_*"):
        try:
            _require_real_directory(directory, label="adjudication attempt directory")
        except ValueError:
            if directory.is_symlink():
                raise
            continue
        attempts.append(directory)
    if not attempts:
        return None
    return max(attempts, key=lambda d: int(d.name.rsplit("_", 1)[-1]))


def _graph_text(run_dir: Path) -> str:
    revisions = sorted(
        run_dir.glob("subgoal_graph_revision_*.json"),
        key=lambda p: int(p.stem.rsplit("_", 1)[-1]),
    )
    source = revisions[-1] if revisions else (run_dir / "subgoal_graph.json")
    try:
        return _read_text_nofollow(source)
    except (OSError, ValueError, UnicodeDecodeError):
        return "{}"


def _raw_reviews(attempt_dir: Path | None) -> str:
    if attempt_dir is None:
        return ""
    parts = []
    for role in REVIEW_MANDATES:  # deterministic order matches the inline pass
        review_file = attempt_dir / f"review_{role}.json"
        if review_file.exists() or review_file.is_symlink():
            parts.append(_read_text_nofollow(review_file))
    return "\n\n".join(parts)


def _statement_lock_text(run_dir: Path) -> str:
    data = json.loads(_read_text_nofollow(run_dir / "statement_lock.json"))
    lock = StatementLock(
        original_statement=str(data["original_statement"]),
        sha256=str(data["sha256"]),
        acceptance_criteria=tuple(data.get("acceptance_criteria", ())),
    )
    return statement_lock_text(lock)


def build_adjudicator_prompt(run_dir: Path) -> str:
    """Rebuild the exact adjudicator prompt the inline stage would have used."""
    run_dir = Path(run_dir)
    _require_confined_run_directory(run_dir)
    candidate = _read_text_nofollow(run_dir / "candidate.md")
    return ADJUDICATOR_PROMPT_TEMPLATE.format(
        offline=OFFLINE_POLICY,
        statement_lock=_statement_lock_text(run_dir),
        subgoal_graph=_graph_text(run_dir),
        candidate=candidate,
        reviews=_raw_reviews(_latest_attempt_dir(run_dir)),
    )


# ── one run ──────────────────────────────────────────────────────────────────

def _evidence_from_manifest(manifest: dict) -> tuple[VerificationEvidence, ...]:
    return tuple(
        VerificationEvidence(**item)
        for item in manifest.get("verification_evidence", [])
    )


def adjudicate_run(
    run_dir: Path,
    runner,
    *,
    apply_gate: bool = True,
    review_attestor=None,
    attestation_env: dict[str, str] | None = None,
) -> dict:
    """Re-adjudicate one run with ``runner`` (a distinct model) and record it."""
    run_dir = Path(run_dir)
    _require_confined_run_directory(run_dir)
    if apply_gate and review_attestor is None:
        # Do not spend provider calls or write a permanent "completed" marker
        # when this process cannot authenticate the claimed model identity.
        raise ValueError("gate-mutating adjudication requires an authenticated review gateway")

    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(_read_text_nofollow(manifest_path))

    prompt = build_adjudicator_prompt(run_dir)
    raw = runner.run(prompt, stage=ADJ_STAGE, isolated=True)
    context_id = runner.context_id(ADJ_STAGE)
    candidate = _read_text_nofollow(run_dir / "candidate.md")
    candidate_sha256 = hashlib.sha256(candidate.encode("utf-8")).hexdigest()

    malformed = False
    try:
        review = _review(
            _json_object(raw), reviewer_id="adjudicator-deepseek",
            expected_role="adjudicator", context_id=context_id,
            candidate_sha256=candidate_sha256,
            problem_number=int(manifest.get("problem_number", 0)),
            run_contract_id_value=str(manifest.get("run_contract_id", "")),
            execution_id=str(manifest.get("execution_id", "")),
            run_context_id_value=str(manifest.get("run_context_id", "")),
        )
        if review_attestor is not None:
            attested = review_attestor(review, ADJ_STAGE)
            if not isinstance(attested, Review) \
                    or not verify_review_attestation(attested, env=attestation_env):
                raise ValueError("distinct-model review attestation is invalid")
            review = attested
        elif apply_gate:
            # The preflight above should make this unreachable, but retain a
            # local fail-closed check if control flow is changed later.
            raise ValueError("distinct-model identity is not authenticated")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        review = _failed_review(
            reviewer_id="adjudicator-deepseek", expected_role="adjudicator",
            context_id=context_id, error=error,
        )
        malformed = True

    # In advisory mode ``agrees`` describes only the parsed response.  It is
    # never an authenticated review and cannot mutate the gate.
    agrees = (
        not malformed
        and review.verdict.lower() == "pass"
        and not review.open_gaps
        and not review.unchecked_imports
        and not review.material_errors
    )

    gate_before = str(manifest.get("gate", {}).get("status", ""))
    gate_after = gate_before
    # A malformed distinct verdict is advisory only: never let DeepSeek's own
    # formatting failure reject an otherwise-passing candidate.
    if apply_gate and not malformed:
        swapped = [
            record for record in manifest["reviews"]
            if record.get("reviewer_role") != "adjudicator"
        ]
        swapped.append(asdict(review))
        decision = evaluate_gate(
            manifest["candidate_outcome"],
            load_reviews(swapped),
            expected_statement_sha256=manifest["statement_sha256"],
            candidate_contract=candidate_contract(candidate),
            verification_evidence=_evidence_from_manifest(manifest),
            expected_candidate_sha256=hashlib.sha256(
                candidate.encode("utf-8")
            ).hexdigest(),
            attestation_env=attestation_env,
            expected_problem_number=manifest.get("problem_number"),
            expected_run_contract_id=str(manifest.get("run_contract_id", "")),
            expected_execution_id=str(manifest.get("execution_id", "")),
            expected_run_context_id=str(manifest.get("run_context_id", "")),
        )
        # Mirror ProofPipeline.solve: "reviews pass, only evidence missing" is
        # the awaiting state, not a rejection.
        if decision.reasons == ONLY_EVIDENCE_MISSING:
            decision = GateDecision(AWAITING, decision.reasons)
        manifest["reviews"] = swapped
        manifest["gate"] = asdict(decision)
        manifest["adjudicator_distinct_model"] = True
        gate_after = decision.status

    record = {
        "model": "deepseek",
        "authenticated": review_attestor is not None and not malformed,
        "applied": bool(apply_gate and not malformed),
        "reviewer_role": "adjudicator",
        "agrees": agrees,
        "malformed": malformed,
        "verdict": review.verdict,
        "outcome": review.adjudicated_outcome,
        "context_id": context_id,
        "open_gaps": list(review.open_gaps),
        "unchecked_imports": list(review.unchecked_imports),
        "material_errors": list(review.material_errors),
        "gate_before": gate_before,
        "gate_after": gate_after,
        "adjudicated_at": datetime.now(timezone.utc).isoformat(),
        "raw": raw,
    }
    manifest["distinct_adjudicator"] = {
        "model": "deepseek",
        "authenticated": review_attestor is not None and not malformed,
        "applied": bool(apply_gate and not malformed),
        "agrees": agrees,
        "malformed": malformed,
        "verdict": review.verdict,
        "context_id": context_id,
        "gate_before": gate_before,
        "gate_after": gate_after,
        "adjudicated_at": record["adjudicated_at"],
    }
    _write_json_confined(run_dir, manifest_path.name, manifest)
    _write_json_confined(run_dir, ADJ_FILE, record)
    return record


def adjudicate_awaiting(
    artifacts: Path, runner, *, limit: int = 0, apply_gate: bool = True,
) -> list[tuple[Path, dict | str]]:
    """Serially re-adjudicate every awaiting run (honours one-at-a-time)."""
    runs = find_adjudicatable_runs(Path(artifacts))
    if limit:
        runs = runs[:limit]
    results: list[tuple[Path, dict | str]] = []
    for run_dir in runs:
        try:
            record = adjudicate_run(run_dir, runner, apply_gate=apply_gate)
            print(f"[adjudicate] {run_dir.parent.name}/{run_dir.name}: "
                  f"deepseek agrees={record['agrees']} "
                  f"malformed={record['malformed']} gate={record['gate_after']}",
                  flush=True)
            results.append((run_dir, record))
        except Exception as exc:  # one bad run must not stop the pass
            print(f"[adjudicate] {run_dir}: FAILED ({exc})", flush=True)
            results.append((run_dir, f"error: {exc}"))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, default=Path("proof_runs_sol2"))
    parser.add_argument("--limit", type=int, default=0, help="0 = all awaiting runs")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--stage-timeout", type=float, default=1800)
    parser.add_argument("--backoff", type=float, default=15.0)
    parser.add_argument("--max-backoff", type=float, default=120.0)
    parser.add_argument("--request-spacing", type=float, default=12.0)
    parser.add_argument("--max-attempts", type=int, default=8)
    parser.add_argument(
        "--advisory-only", action="store_true",
        help="record the distinct verdict without changing the gate",
    )
    parser.add_argument(
        "--force-legacy", action="store_true",
        help="Run the RETIRED legacy adjudication pass anyway. It only adjudicates "
             "legacy ProofPipeline candidates, which the EGMRA pipeline no longer "
             "produces.",
    )
    args = parser.parse_args()
    if not args.force_legacy:
        parser.error(
            "run_adjudication.py is RETIRED: it mutates the legacy gate on legacy "
            "ProofPipeline candidates. The verified EGMRA pipeline runs its own "
            "independent referee inside `egmra run`/`egmra campaign`. Pass "
            "--force-legacy only to adjudicate old legacy candidates deliberately."
        )

    pending = find_adjudicatable_runs(args.artifacts)
    if not pending:
        print("[adjudicate] no awaiting runs to adjudicate.", flush=True)
        return

    # Imported here so the module is unit-testable without Playwright/DeepSeek.
    import deepseek_common as DS
    from deepseek_runner import DeepSeekBrowserRunner

    with DS.sync_playwright() as playwright:
        browser = DS.launch_browser(playwright, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()
        DS.ensure_logged_in(page)
        runner = DeepSeekBrowserRunner(
            browser, page, timeout_s=args.stage_timeout,
            backoff_s=args.backoff, max_backoff_s=args.max_backoff,
            request_spacing_s=args.request_spacing, max_attempts=args.max_attempts,
        )
        results = adjudicate_awaiting(
            args.artifacts, runner, limit=args.limit,
            apply_gate=not args.advisory_only,
        )

    agreed = sum(1 for _, r in results if isinstance(r, dict) and r["agrees"])
    dissented = sum(
        1 for _, r in results
        if isinstance(r, dict) and not r["agrees"] and not r["malformed"]
    )
    print(f"[adjudicate] done: {len(results)} runs, {agreed} agreed, "
          f"{dissented} dissented.", flush=True)


if __name__ == "__main__":
    main()
