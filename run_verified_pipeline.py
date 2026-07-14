#!/usr/bin/env python3
"""Run the full verified pipeline for one problem through ChatGPT browser UI."""

import argparse
import fcntl
import hashlib
import json
import os
import stat
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import erdos_common as C
from erdos_searcher import (
    canonical_problem_run_inputs,
    find_latest_canonical_snapshot,
    load_canonical_corpus,
    normalized_budget_config,
)
from proof_pipeline import ProofPipeline
from literature_research import research_literature
from outcome_ledger import record_outcome
from research_state import make_statement_lock
from verification import (
    VerificationEvidence,
    MaterializedVerificationEvidence,
    verify_verification_evidence,
)
from egmra.policy import (
    PolicyEnforcer,
    default_policy_path,
    load_policy,
)


_MAX_EVIDENCE_DOCUMENT_BYTES = 1_000_000
_MAX_EVIDENCE_ARTIFACT_BYTES = 64 * 1024 * 1024
_MAX_EVIDENCE_RECORDS = 32
_MAX_EVIDENCE_ARTIFACT_TOTAL_BYTES = 128 * 1024 * 1024
_EVIDENCE_RECORD_FIELDS = frozenset({
    "schema_version", "kind", "verifier", "outcome", "statement_sha256",
    "candidate_sha256", "artifact_path", "artifact_sha256", "passed",
    "verification_method", "validator_id", "certificate_sha256",
    "scope_sha256", "coverage", "statement_fidelity", "attestor_key_id",
    "attestation", "problem_number", "run_contract_id", "execution_id",
    "run_context_id",
})


def _strict_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate evidence key: {key}")
        result[key] = value
    return result


def _read_regular_file(path: Path, *, max_bytes: int, label: str) -> bytes:
    """Read a bounded regular file without following the final symlink."""
    flags = (
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ValueError(f"{label} is unreadable or not a safe regular file: {exc}") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"{label} must be a regular file")
        if metadata.st_size > max_bytes:
            raise ValueError(f"{label} exceeds the {max_bytes}-byte limit")
        chunks = []
        remaining = max_bytes + 1
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > max_bytes:
            raise ValueError(f"{label} exceeds the {max_bytes}-byte limit")
        return payload
    finally:
        os.close(descriptor)


def _open_directory(path: Path, *, label: str) -> int:
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ValueError(f"{label} is not a safe directory: {exc}") from exc
    if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise ValueError(f"{label} must be a directory")
    return descriptor


def _read_regular_at(
    directory_fd: int,
    relative: Path,
    *,
    max_bytes: int,
    label: str,
) -> bytes:
    """Open a relative file under a pinned directory without symlink traversal."""
    parts = relative.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"{label} has an invalid confined path")
    current = os.dup(directory_fd)
    try:
        directory_flags = (
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0)
        )
        for component in parts[:-1]:
            try:
                child = os.open(component, directory_flags, dir_fd=current)
            except OSError as exc:
                raise ValueError(
                    f"{label} contains an unsafe directory component: {exc}"
                ) from exc
            if not stat.S_ISDIR(os.fstat(child).st_mode):
                os.close(child)
                raise ValueError(f"{label} contains a non-directory component")
            os.close(current)
            current = child
        file_flags = (
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0)
        )
        try:
            descriptor = os.open(parts[-1], file_flags, dir_fd=current)
        except OSError as exc:
            raise ValueError(
                f"{label} is unreadable or not a safe regular file: {exc}"
            ) from exc
        try:
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError(f"{label} must be a regular file")
            if metadata.st_size > max_bytes:
                raise ValueError(f"{label} exceeds the {max_bytes}-byte limit")
            chunks = []
            remaining = max_bytes + 1
            while remaining:
                chunk = os.read(descriptor, min(1024 * 1024, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            payload = b"".join(chunks)
            if len(payload) > max_bytes:
                raise ValueError(f"{label} exceeds the {max_bytes}-byte limit")
            return payload
        finally:
            os.close(descriptor)
    finally:
        os.close(current)


@dataclass(frozen=True)
class EvidenceInspection:
    kinds: frozenset[str]
    document_sha256: str


def _open_evidence_document(path: Path) -> tuple[list[dict], int, str]:
    evidence_path = Path(path).expanduser()
    if not evidence_path.name or evidence_path.name in {".", ".."}:
        raise ValueError("evidence document path is invalid")
    try:
        base = evidence_path.parent.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"evidence directory is unavailable: {exc}") from exc
    directory_fd = _open_directory(base, label="evidence directory")
    try:
        raw = _read_regular_at(
            directory_fd, Path(evidence_path.name),
            max_bytes=_MAX_EVIDENCE_DOCUMENT_BYTES,
            label="evidence document",
        )
        try:
            records = json.loads(
                raw.decode("utf-8"), object_pairs_hook=_strict_json_object,
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"evidence document is not strict UTF-8 JSON: {exc}"
            ) from exc
        if not isinstance(records, list):
            raise ValueError("evidence JSON must be a list")
        if not records:
            raise ValueError("evidence JSON must contain at least one record")
        if len(records) > _MAX_EVIDENCE_RECORDS:
            raise ValueError(
                f"evidence JSON exceeds the {_MAX_EVIDENCE_RECORDS}-record limit"
            )
        for index, record in enumerate(records):
            if not isinstance(record, dict) or set(record) != _EVIDENCE_RECORD_FIELDS:
                raise ValueError(
                    f"evidence record {index} does not match the closed schema"
                )
        return records, directory_fd, hashlib.sha256(raw).hexdigest()
    except Exception:
        os.close(directory_fd)
        raise


def _evidence_enforcer(enforcer):
    if enforcer is not None:
        if type(enforcer) is not PolicyEnforcer:
            raise TypeError("evidence policy must be an authenticated PolicyEnforcer")
        return enforcer
    return PolicyEnforcer(load_policy(default_policy_path()))


def inspect_evidence(path: Path, *, enforcer=None) -> EvidenceInspection:
    """Authenticate policy and inspect bounded metadata without opening artifacts."""
    policy = _evidence_enforcer(enforcer)
    policy.require(
        "automated_external_evidence",
        entry_point="run_verified_pipeline.inspect_evidence",
    )
    records, descriptor, document_sha256 = _open_evidence_document(path)
    try:
        return EvidenceInspection(
            kinds=frozenset(str(record["kind"]) for record in records),
            document_sha256=document_sha256,
        )
    finally:
        os.close(descriptor)


def load_evidence(
    path: Path | None, *, enforcer=None,
    attestation_env: dict[str, str] | None = None,
    expected_document_sha256: str | None = None,
) -> MaterializedVerificationEvidence:
    """Load closed, authenticated mechanical evidence from a confined directory.

    The evidence document and every referenced artifact must be bounded regular
    files.  Artifact references are relative to the document directory so a
    supplied JSON file cannot hash arbitrary host files or follow symlink escapes.
    A signed feature policy is checked before any attacker-controlled path is read.
    """
    if path is None:
        return MaterializedVerificationEvidence(
            (), {},
        )
    policy = _evidence_enforcer(enforcer)
    policy.require(
        "automated_external_evidence",
        entry_point="run_verified_pipeline.load_evidence",
    )
    records, directory_fd, document_sha256 = _open_evidence_document(Path(path))
    if expected_document_sha256 is not None \
            and document_sha256 != expected_document_sha256:
        os.close(directory_fd)
        raise ValueError("evidence document changed after policy inspection")
    evidence = []
    artifact_payloads: dict[str, bytes] = {}
    artifact_names: set[str] = set()
    total_artifact_bytes = 0
    try:
      for index, record in enumerate(records):
        artifact_name = record["artifact_path"]
        if not isinstance(artifact_name, str) or not artifact_name.strip() \
                or "\x00" in artifact_name:
            raise ValueError(f"evidence record {index} has an invalid artifact path")
        relative = Path(artifact_name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(
                f"evidence record {index} artifact must be relative and confined"
            )
        normalized_name = relative.as_posix()
        if normalized_name in artifact_names:
            raise ValueError(f"evidence record {index} duplicates an artifact path")
        artifact_names.add(normalized_name)
        artifact_bytes = _read_regular_at(
            directory_fd, relative, max_bytes=_MAX_EVIDENCE_ARTIFACT_BYTES,
            label=f"evidence artifact {index}",
        )
        total_artifact_bytes += len(artifact_bytes)
        if total_artifact_bytes > _MAX_EVIDENCE_ARTIFACT_TOTAL_BYTES:
            raise ValueError(
                "evidence artifacts exceed the aggregate byte limit"
            )
        artifact_sha = hashlib.sha256(artifact_bytes).hexdigest()
        if artifact_sha in artifact_payloads:
            raise ValueError(f"evidence record {index} duplicates an artifact digest")
        if record["artifact_sha256"] != artifact_sha:
            raise ValueError(f"evidence record {index} artifact hash mismatch")
        item = VerificationEvidence(
            kind=str(record["kind"]),
            verifier=str(record["verifier"]),
            outcome=str(record["outcome"]),
            statement_sha256=str(record["statement_sha256"]),
            candidate_sha256=str(record["candidate_sha256"]),
            artifact_sha256=artifact_sha,
            passed=record["passed"] if type(record["passed"]) is bool else False,
            verification_method=str(record["verification_method"]),
            validator_id=str(record["validator_id"]),
            certificate_sha256=str(record["certificate_sha256"]),
            scope_sha256=str(record["scope_sha256"]),
            coverage=str(record["coverage"]),
            statement_fidelity=str(record["statement_fidelity"]),
            schema_version=(record["schema_version"]
                            if type(record["schema_version"]) is int else -1),
            attestor_key_id=str(record["attestor_key_id"]),
            attestation=str(record["attestation"]),
            problem_number=(record["problem_number"]
                            if type(record["problem_number"]) is int else 0),
            run_contract_id=str(record["run_contract_id"]),
            execution_id=str(record["execution_id"]),
            run_context_id=str(record["run_context_id"]),
        )
        if type(record["passed"]) is not bool:
            raise ValueError(f"evidence record {index} passed must be a boolean")
        if item.passed and not verify_verification_evidence(
            item, env=attestation_env,
        ):
            raise ValueError(
                f"evidence record {index} claims success without a valid semantic attestation"
            )
        evidence.append(item)
        artifact_payloads[artifact_sha] = artifact_bytes
    finally:
        os.close(directory_fd)
    return MaterializedVerificationEvidence(
        evidence, artifact_payloads,
    )


def publish_verified_result(result, category: str, base_dir: Path) -> Path:
    """Legacy publisher is intentionally disabled.

    A mutable ``GateDecision``/manifest is not an authoritative release
    certificate, and a same-process signer would merely turn it into a signing
    oracle. Publication must go through the EGMRA event-derived, independently
    signed ``ReleaseCertificate`` renderer. Keeping this entry point fail-closed
    also eliminates category/path traversal from legacy callers.
    """
    raise RuntimeError(
        "legacy publication is disabled; use an authenticated EGMRA "
        "ReleaseCertificate and communication renderer"
    )


class ChatGPTBrowserRunner:
    """Fresh-chat adapter for ProofPipeline's isolated model calls."""

    def __init__(self, browser, page, *, timeout_s: float,
                 backoff_s: float = 15.0, max_backoff_s: float = 120.0,
                 request_spacing_s: float = 12.0, max_attempts: int = 8):
        self.browser = browser
        self.page = page
        self.timeout_s = timeout_s
        self.max_backoff_s = max(0.0, min(120.0, max_backoff_s))
        self.backoff_s = min(max(0.0, backoff_s), self.max_backoff_s)
        self.rate_limiter = SharedRateLimiter(
            Path(tempfile.gettempdir()) / "erdos_chatgpt_rate_limit.json",
            backoff_s=self.backoff_s,
            max_backoff_s=self.max_backoff_s,
            request_spacing_s=request_spacing_s,
        )
        self.max_attempts = max_attempts
        self.contexts: dict[str, str] = {}

    def context_id(self, stage: str) -> str:
        return self.contexts.get(stage, "")

    def restore_context(self, stage: str, context_id: str) -> None:
        """Restore durable provenance when ProofPipeline replays a cache entry."""
        self.contexts[stage] = context_id

    def _cool_down(self, stage: str, reason: str) -> None:
        """Apply one shared cooldown across every browser worker."""
        streak, wait_s = self.rate_limiter.record_rate_limit()
        C.dismiss_rate_limit_modal(self.page)
        print(f"{stage}: {reason}; shared rate-limit streak={streak}; "
              f"all workers paused for up to {wait_s:.0f}s", flush=True)

    def run(self, prompt: str, *, stage: str, isolated: bool) -> str:
        if not isolated:
            raise ValueError("verified pipeline stages must use isolated contexts")

        last_error = "unknown"
        attempts_used = 0
        # A rate limit is a provider-side temporary condition, not a failed
        # proof stage. Keep the problem alive until ChatGPT accepts the prompt;
        # only real navigation/generation/response failures consume retries.
        while attempts_used < self.max_attempts:
            self.rate_limiter.wait_for_slot(stage)
            try:
                _ = self.page.url
            except Exception:
                self.page = self.browser.new_page()

            try:
                C.start_new_chat(self.page)

                # A rate-limit alert blocks chat creation — clear it and back off.
                if C.detect_rate_limit(self.page):
                    last_error = "rate-limited before send"
                    self._cool_down(stage, last_error)
                    continue

                start_url = C.current_url(self.page)
                C.send_prompt(self.page, prompt)
                url = C.wait_for_conversation_url(
                    self.page, timeout_s=120, start_url=start_url)

                if not url or url == start_url:
                    if C.detect_rate_limit(self.page):
                        last_error = "rate-limited after send"
                        self._cool_down(stage, last_error)
                        continue
                    attempts_used += 1
                    last_error = "no conversation URL"
                    print(f"{stage}: no conversation URL (attempt {attempts_used}); retrying",
                          flush=True)
                    time.sleep(15)
                    continue

                self.contexts[stage] = url
                print(f"{stage}: waiting for response at {url}", flush=True)
                time.sleep(5)

                deadline = time.time() + self.timeout_s
                while time.time() < deadline and C.is_generating(self.page):
                    # A throttle can pop up mid-generation; keep the UI clear.
                    if C.detect_rate_limit(self.page):
                        self._cool_down(stage, "rate-limited while generating")
                        self.rate_limiter.wait_for_slot(stage)
                    time.sleep(5)

                if C.is_generating(self.page):
                    attempts_used += 1
                    last_error = f"generation exceeded {self.timeout_s:.0f}s"
                    print(f"{stage}: {last_error} (attempt {attempts_used}); backing off",
                          flush=True)
                    time.sleep(self.backoff_s)
                    continue

                time.sleep(2)
                response = C.extract_response(self.page)
                if not response or len(response.strip()) < 100:
                    attempts_used += 1
                    last_error = "empty/incomplete response"
                    print(f"{stage}: {last_error} (attempt {attempts_used}); retrying",
                          flush=True)
                    time.sleep(15)
                    continue

                self.rate_limiter.record_success()
                return response

            except Exception as exc:
                last_error = str(exc)
                print(f"{stage}: error '{exc}'", flush=True)
                try:
                    if C.detect_rate_limit(self.page):
                        last_error = "rate-limited during browser exception"
                        self._cool_down(stage, last_error)
                        continue
                except Exception:
                    pass
                attempts_used += 1
                print(f"{stage}: retrying after browser error "
                      f"(attempt {attempts_used})", flush=True)
                time.sleep(15)

        raise RuntimeError(
            f"{stage}: failed after {self.max_attempts} non-rate-limit attempts "
            f"({last_error})")


class SharedRateLimiter:
    """Cross-process request gate for the single shared ChatGPT quota."""

    def __init__(self, path: Path, *, backoff_s: float,
                 max_backoff_s: float, request_spacing_s: float):
        self.path = path
        self.max_backoff_s = max(0.0, min(120.0, max_backoff_s))
        self.backoff_s = min(max(0.0, backoff_s), self.max_backoff_s)
        self.request_spacing_s = max(0.0, min(120.0, request_spacing_s))
        self.path.touch(exist_ok=True)

    def _update(self, action):
        with self.path.open("r+", encoding="utf-8") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                try:
                    state = json.load(handle)
                except (json.JSONDecodeError, ValueError):
                    state = {}
                result = action(state)
                handle.seek(0)
                handle.truncate()
                json.dump(state, handle)
                handle.flush()
                return result
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def wait_for_slot(self, stage: str) -> None:
        """Serialize sends and honor a cooldown imposed by any worker."""
        while True:
            now = time.time()

            def reserve(state):
                ceiling = now + 120.0
                state["cooldown_until"] = min(
                    float(state.get("cooldown_until", 0)), ceiling
                )
                state["next_request_at"] = min(
                    float(state.get("next_request_at", 0)), ceiling
                )
                ready_at = max(state["cooldown_until"], state["next_request_at"])
                if ready_at <= now:
                    state["next_request_at"] = now + self.request_spacing_s
                    return 0.0
                return ready_at - now

            delay = self._update(reserve)
            if delay <= 0:
                return
            print(f"{stage}: waiting {delay:.0f}s for the shared ChatGPT quota",
                  flush=True)
            time.sleep(delay)

    def record_rate_limit(self) -> tuple[int, float]:
        now = time.time()

        def penalize(state):
            streak = int(state.get("rate_limit_streak", 0)) + 1
            wait_s = min(self.backoff_s * (2 ** max(0, streak - 1)),
                         self.max_backoff_s)
            state["rate_limit_streak"] = streak
            ceiling = now + 120.0
            existing_cooldown = min(
                float(state.get("cooldown_until", 0)), ceiling
            )
            existing_request = min(
                float(state.get("next_request_at", 0)), ceiling
            )
            state["cooldown_until"] = max(existing_cooldown, now + wait_s)
            state["next_request_at"] = max(
                existing_request, state["cooldown_until"]
            )
            return streak, wait_s

        return self._update(penalize)

    def record_success(self) -> None:
        def clear_penalty(state):
            state["rate_limit_streak"] = 0
            # Another worker may have recorded a newer 429 while this request
            # was in flight. Never erase shared future cooldown/spacing state.

        self._update(clear_penalty)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem", type=int, required=True)
    parser.add_argument("--category", default="open")
    parser.add_argument("--artifacts", type=Path, default=Path("proof_runs"))
    parser.add_argument("--triage", type=Path, default=Path("triage"))
    parser.add_argument("--stage-timeout", type=float, default=1800)
    parser.add_argument("--backoff", type=float, default=15.0,
                        help="Initial seconds to wait after a rate-limit alert")
    parser.add_argument("--max-backoff", type=float, default=120.0,
                        help="Maximum adaptive rate-limit backoff in seconds")
    parser.add_argument("--request-spacing", type=float, default=12.0,
                        help="Minimum seconds between any two worker requests")
    parser.add_argument("--max-revisions", type=int, default=2)
    parser.add_argument("--max-attempts", type=int, default=8)
    parser.add_argument(
        "--model-id", required=True,
        help="Exact ChatGPT UI model/version disclosure stored in the manifest",
    )
    parser.add_argument("--print-statement-sha", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument(
        "--research-similar", action="store_true",
        help="Ground the search stages in related problems and known results "
             "retrieved offline from the local corpus (rediscovery-eligible).",
    )
    parser.add_argument(
        "--force-legacy", action="store_true",
        help="Run the RETIRED legacy per-problem pipeline anyway. The supported "
             "path is `egmra run --erdos N` (verified EGMRA loop). The read-only "
             "--print-statement-sha utility remains available without this flag.",
    )
    args = parser.parse_args()

    triage_dir = args.triage if args.triage.is_absolute() else C.REPO_DIR / args.triage
    if args.print_statement_sha:
        snapshot = find_latest_canonical_snapshot(triage_dir)
        sources = load_canonical_corpus(snapshot)
        if args.problem not in sources:
            raise SystemExit(f"problem {args.problem} is not source-open")
        print(make_statement_lock(sources[args.problem]["statement"]).sha256)
        return
    if not args.force_legacy:
        parser.error(
            "run_verified_pipeline.py is RETIRED as a production runner: it drives "
            "the legacy ProofPipeline, which terminates at "
            "'awaiting_authenticated_release' and can never emit a ReleaseCertificate. "
            "Use the single verified pipeline instead:\n"
            "  egmra run --erdos N --provider browser --policy <signed-policy>\n"
            "Pass --force-legacy only to run the retired path deliberately."
        )
    if "unrecorded" in args.model_id.lower() or not args.model_id.strip():
        parser.error("--model-id must be the exact recorded UI model identity")
    budget_config = normalized_budget_config(
        max_revisions=args.max_revisions,
        stage_timeout_s=args.stage_timeout,
        initial_backoff_s=args.backoff,
        max_backoff_s=args.max_backoff,
        request_spacing_s=args.request_spacing,
        max_attempts=args.max_attempts,
        browser_headless=args.headless,
    )
    try:
        run_inputs = canonical_problem_run_inputs(
            C.REPO_DIR,
            triage_dir,
            args.problem,
            model_portfolio=args.model_id,
            budget_config=budget_config,
        )
    except Exception as error:
        raise SystemExit(f"exact canonical run context unavailable: {error}") from error
    statement = run_inputs["statement"]
    C.PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with C.sync_playwright() as playwright:
        browser = C.launch_browser(playwright, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()
        C.ensure_logged_in(page)
        runner = ChatGPTBrowserRunner(
            browser, page, timeout_s=budget_config["stage_timeout_s"],
            backoff_s=budget_config["initial_backoff_s"],
            max_backoff_s=budget_config["max_backoff_s"],
            request_spacing_s=budget_config["request_spacing_s"],
            max_attempts=budget_config["max_attempts"],
        )
        literature = (
            research_literature(C.REPO_DIR, args.problem)
            if args.research_similar else None
        )
        result = ProofPipeline(
            runner,
            args.artifacts,
            max_revisions=args.max_revisions,
            pipeline_version=run_inputs["pipeline_version"],
            model_portfolio=args.model_id,
            execution_config=run_inputs["execution_config"],
            source_snapshot_id=run_inputs["source_snapshot_id"],
            source_snapshot_sha256=run_inputs["source_snapshot_sha256"],
            toolset=run_inputs["toolset"],
            dependencies=run_inputs["dependencies"],
            runtime=run_inputs["runtime"],
            literature_context=literature.rendered if literature else "",
            literature_grounding=(
                literature.grounding_record() if literature else None
            ),
        ).solve(
            args.problem, statement,
            research_directive=run_inputs["research_directive"],
        )
        record_outcome(
            triage_dir, args.problem, result.artifact_dir / "manifest.json",
        )
        browser.close()

    print(f"candidate: {result.candidate_outcome}")
    print(f"gate: {result.gate.status}")
    for reason in result.gate.reasons:
        print(f"- {reason}")
    print(f"artifacts: {result.artifact_dir}")
    print("External evidence is applied afterward with promote_verified_run.py.")


if __name__ == "__main__":
    main()
