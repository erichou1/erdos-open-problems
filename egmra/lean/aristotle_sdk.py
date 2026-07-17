"""Official Aristotle SDK adapter (task B2, DECISIONS.md D-B).

The operator supplied the official Aristotle docs: it is distributed as the
``aristotlelib`` package (CLI ``aristotle``) and is Lean-native (Lean v4.28.0 +
Mathlib v4.28.0). Per the task ("prefer the supported official SDK rather than
guessing HTTP endpoints"), this adapter drives the official SDK's
``Project.create_from_directory`` → ``AgentTask.wait_for_completion`` →
``project.get_files`` workflow instead of hand-rolled REST calls.

Trust boundary is unchanged: the vendor's ``COMPLETE`` status is **never** a
promotion. The produced Lean is downloaded into a hardened quarantine, scanned
for symlinks/escapes/oversize, and promoted only after an independent local Lean
kernel replay seals a :class:`LocalLeanReplayAttestation`
(:func:`egmra.lean.aristotle_api.verify_local_replay` + the B1
:class:`~egmra.lean.replay.LeanReplayVerifier`).
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import os
import threading
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from egmra.lean.aristotle_api import (
    _DEFAULT_MAX_ENTRIES,
    _DEFAULT_MAX_ENTRY_BYTES,
    _DEFAULT_MAX_TOTAL_BYTES,
    VENDOR_COMPLETE_STATUSES,
    AristotleArtifact,
    AristotleClientError,
    AristotleStatus,
    LocalLeanReplayAttestation,
    LocalReplayResult,
    UnsafeJobIdError,
    resolve_quarantine_dir,
    safe_extract_archive,
    scan_quarantine_tree,
    validate_job_id,
    verify_local_replay,
)

# The pinned toolchain the official Aristotle service is compatible with.
ARISTOTLE_LEAN_TOOLCHAIN = "leanprover/lean4:v4.28.0"
ARISTOTLE_MATHLIB_REV = "v4.28.0"

# Map the SDK's TaskStatus names onto our normalized vocabulary.
_SDK_COMPLETE = frozenset({"complete", "complete_with_errors"})
_SDK_FAILED = frozenset({"failed", "canceled", "cancelled", "out_of_budget"})

# Long-poll phrases the vendor explicitly labels transient ("try again"). A
# proof task keeps running server-side through such a blip; treating it as
# fatal discards a 10-15 minute proof and resubmits a NEW task — burning both
# wall-clock and the 5-slot account quota on orphans.
_TRANSIENT_PHRASES = (
    "connection to server was interrupted",
    "connection reset",
    "timed out",
    "timeout",
    "temporarily unavailable",
    "service unavailable",
    "bad gateway",
    "gateway time",
)


def _is_transient(exc: BaseException) -> bool:
    text = f"{type(exc).__name__}: {exc}".lower()
    return any(phrase in text for phrase in _TRANSIENT_PHRASES)


def _aristotle_max_wait_s() -> float:
    """Hard ceiling on ONE vendor completion wait (default 1800s = 30 min).

    A proof legitimately runs 10-15 min server-side, but a task the vendor
    leaves QUEUED indefinitely (or a long-poll that never resolves after a
    server disconnect) must not block the worker thread forever — that is the
    exact hang that wedges a campaign worker and, downstream, starves the
    machine liveness heartbeat. Exceeding the budget raises a clean failure so
    the worker records it and moves on. Override with
    ``EGMRA_ARISTOTLE_MAX_WAIT_S`` (clamped 60-14400); 0 disables the ceiling.
    """
    raw = os.environ.get("EGMRA_ARISTOTLE_MAX_WAIT_S", "").strip()
    try:
        value = float(raw) if raw else 1800.0
    except ValueError:
        return 1800.0
    if value <= 0:
        return 0.0
    return min(14400.0, max(60.0, value))


class AristotleSdkUnavailable(AristotleClientError):
    """The official ``aristotlelib`` package is not installed."""


@dataclass(frozen=True)
class AristotleSubmission:
    """A submitted Aristotle project/task pair (both are safe tokens)."""

    project_id: str
    agent_task_id: str


def _load_sdk():  # pragma: no cover - exercised via injection in tests
    try:
        import aristotlelib  # type: ignore[import-not-found]
    except ImportError as exc:
        raise AristotleSdkUnavailable(
            "aristotlelib is not installed; `pip install -e .[aristotle]`"
        ) from exc
    return aristotlelib


@dataclass
class AristotleSdkClient:
    """Drive the official Aristotle SDK; verify locally before any trust.

    ``sdk`` defaults to the real ``aristotlelib`` module and is injectable so the
    submit/poll/fetch control flow is exercised by a fake in tests (no network,
    no key). The API key is read from the environment only and never logged.
    """

    quarantine_root: Path
    project_dir: Path
    sdk: Any = None
    env: dict[str, str] | None = None
    max_entries: int = _DEFAULT_MAX_ENTRIES
    max_entry_bytes: int = _DEFAULT_MAX_ENTRY_BYTES
    max_total_bytes: int = _DEFAULT_MAX_TOTAL_BYTES
    _projects: dict[str, Any] = field(default_factory=dict, init=False, repr=False)
    _tasks: dict[str, Any] = field(default_factory=dict, init=False, repr=False)
    _loop_obj: Any = field(default=None, init=False, repr=False)
    _bg_loop: Any = field(default=None, init=False, repr=False)
    _bg_thread: Any = field(default=None, init=False, repr=False)
    _bg_lock: Any = field(default_factory=threading.Lock, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.sdk is None:
            self.sdk = _load_sdk()
        from egmra.config import EgmraConfig

        key = EgmraConfig.secret("ARISTOTLE_API_KEY", env=self.env)
        if not key:
            raise AristotleClientError(
                "ARISTOTLE_API_KEY is not configured; export it in the environment"
            )
        self._await(self.sdk.set_api_key(key))  # sync in the real SDK; never logged

    # The official ``aristotlelib`` SDK is async (every Project/AgentTask method
    # is a coroutine); the orchestrator/CLI drive this client synchronously. We
    # run each awaitable to completion on a persistent, client-owned event loop.
    # Non-awaitable values (the synchronous fake SDK in tests) pass through
    # unchanged, so the same control flow exercises both.
    def _await(self, value: Any, *, timeout: float | None = None) -> Any:
        if not inspect.isawaitable(value):
            return value
        # Marshal EVERY awaitable to a single client-owned loop thread. This one
        # path covers both hazards at once: (1) the calling thread may already
        # have a running loop (sync Playwright keeps one active between browser
        # calls — the normal state inside a browser-provider research run),
        # where run_until_complete would deadlock; (2) CONCURRENT formalization
        # calls (parallel Aristotle proofs) would race a shared
        # run_until_complete loop — run_coroutine_threadsafe is safe for
        # concurrent submitters, and the coroutines make genuinely concurrent
        # progress on the one loop.
        with self._bg_lock:
            if self._bg_loop is None or not (
                self._bg_thread is not None and self._bg_thread.is_alive()
            ):
                self._bg_loop = asyncio.new_event_loop()
                self._bg_thread = threading.Thread(
                    target=self._bg_loop.run_forever,
                    name="aristotle-sdk-loop", daemon=True)
                self._bg_thread.start()
        future = asyncio.run_coroutine_threadsafe(value, self._bg_loop)
        # A bounded wait (used for the long completion poll) prevents a stuck or
        # never-resolving vendor task from blocking the worker thread forever.
        # On expiry the orphaned coroutine is cancelled on its own loop and a
        # non-transient error is raised so the caller fails cleanly and moves on.
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError as exc:
            future.cancel()
            raise AristotleClientError(
                f"aristotle wait exceeded {timeout:.0f}s budget") from exc

    def close(self) -> None:
        """Close the client-owned event loops (best-effort teardown)."""
        loop = self._loop_obj
        self._loop_obj = None
        if loop is not None and not loop.is_closed():  # pragma: no cover - teardown
            loop.close()
        bg_loop, bg_thread = self._bg_loop, self._bg_thread
        self._bg_loop = self._bg_thread = None
        if bg_loop is not None and bg_loop.is_running():  # pragma: no cover - teardown
            bg_loop.call_soon_threadsafe(bg_loop.stop)
            if bg_thread is not None:
                bg_thread.join(timeout=5.0)
            bg_loop.close()

    def submit(self, prompt: str) -> AristotleSubmission:
        """Create a project from the pinned Lean dir and start the first task."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise AristotleClientError("prompt must be a non-empty string")
        try:
            project = self._await(
                self.sdk.Project.create_from_directory(prompt, str(self.project_dir)))
            tasks, _ = self._await(project.get_tasks(limit=1))
        except AristotleClientError:
            raise
        except Exception as exc:  # normalize SDK errors
            raise AristotleClientError(f"aristotle submit failed: {exc}") from exc
        if not tasks:
            raise AristotleClientError("aristotle returned no agent task for the project")
        task = tasks[0]
        project_id = validate_job_id(str(project.project_id))
        agent_task_id = validate_job_id(str(task.agent_task_id))
        self._projects[project_id] = project
        self._tasks[agent_task_id] = task
        return AristotleSubmission(project_id=project_id, agent_task_id=agent_task_id)

    def _task(self, submission: AristotleSubmission):
        task = self._tasks.get(submission.agent_task_id)
        if task is None:
            task = self._await(
                self.sdk.AgentTask.from_id(validate_job_id(submission.agent_task_id)))
            self._tasks[submission.agent_task_id] = task
        return task

    def poll(self, submission: AristotleSubmission) -> AristotleStatus:
        task = self._task(submission)
        try:
            self._await(task.refresh())
        except Exception as exc:
            raise AristotleClientError(f"aristotle poll failed: {exc}") from exc
        raw = str(getattr(task.status, "name", task.status)).strip().lower()
        return AristotleStatus(
            job_id=submission.agent_task_id,
            raw_status=raw,
            vendor_reports_complete=raw in _SDK_COMPLETE or raw in VENDOR_COMPLETE_STATUSES,
            failed=raw in _SDK_FAILED,
            detail={"project_id": submission.project_id,
                    "percent_complete": getattr(task, "percent_complete", None)},
        )

    def fetch(self, submission: AristotleSubmission, *, wait: bool = True,
              transient_retries: int = 4,
              retry_sleep: Callable[[float], None] | None = None) -> AristotleArtifact:
        """Download the produced Lean into a hardened quarantine (never promotable).

        A dropped long-poll connection is NOT a failed proof: the vendor task
        keeps running server-side and the SDK error says "try again". The
        wait/download phase therefore retries transient interruptions a
        bounded number of times (with short growing pauses) before giving up;
        genuine task failures and safety violations are never retried.
        """
        sleep = retry_sleep if retry_sleep is not None else time.sleep
        project = self._projects.get(submission.project_id)
        if project is None:
            project = self._await(
                self.sdk.Project.from_id(validate_job_id(submission.project_id)))
        task = self._task(submission)
        quarantine_dir = self._resolve_quarantine_dir(submission.project_id)
        attempts = max(1, int(transient_retries) + 1)
        archive_bytes = None
        for attempt in range(1, attempts + 1):
            try:
                if wait:
                    self._await(task.wait_for_completion(),
                                timeout=_aristotle_max_wait_s() or None)
                # The official SDK writes the result as a SINGLE archive blob to a
                # file path (not a directory). Download it to a throwaway temp file,
                # read the bytes, then extract it ourselves under strict
                # traversal/symlink/bomb-safe limits into the quarantine dir.
                with tempfile.NamedTemporaryFile(
                        prefix="aristotle_", suffix=".tar.gz", delete=False) as handle:
                    archive_path = Path(handle.name)
                try:
                    self._await(project.get_files(str(archive_path)))
                    archive_bytes = archive_path.read_bytes()
                finally:
                    archive_path.unlink(missing_ok=True)
                break
            except UnsafeJobIdError:
                raise
            except Exception as exc:
                if attempt < attempts and _is_transient(exc):
                    sleep(min(30.0, 5.0 * attempt))
                    continue
                raise AristotleClientError(f"aristotle fetch failed: {exc}") from exc
        # Extract the vendor archive under strict limits (rejects traversal,
        # symlinks, and archive bombs), then re-scan the written tree as defense
        # in depth. A vendor archive is never trusted on arrival.
        files, total = safe_extract_archive(
            archive_bytes, quarantine_dir, max_entries=self.max_entries,
            max_entry_bytes=self.max_entry_bytes, max_total_bytes=self.max_total_bytes,
        )
        scan_quarantine_tree(
            quarantine_dir, max_entries=self.max_entries,
            max_entry_bytes=self.max_entry_bytes, max_total_bytes=self.max_total_bytes,
        )
        # The archive is already safely on disk: a status-poll blip here must
        # not discard it. Trust is unaffected — promotion needs the local
        # kernel replay regardless of what the vendor status claims.
        try:
            status = self.poll(submission)
            vendor_status = status.raw_status
            vendor_complete = status.vendor_reports_complete
        except AristotleClientError:
            vendor_status = "unknown_poll_failed"
            vendor_complete = False
        return AristotleArtifact(
            job_id=submission.project_id,
            vendor_status=vendor_status,
            vendor_reports_complete=vendor_complete,
            quarantine_dir=quarantine_dir,
            extracted_files=files,
            total_bytes=total,
            promotable=False,
        )

    def _resolve_quarantine_dir(self, job_id: str) -> Path:
        quarantine_dir = resolve_quarantine_dir(self.quarantine_root, job_id)
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        return quarantine_dir

    def bind_local_replay(
        self,
        artifact: AristotleArtifact,
        verifier: Callable[[Path], "LocalLeanReplayAttestation | None"],
        *,
        expected_claim_id: str | None = None,
        key_env: dict[str, str] | None = None,
    ) -> LocalReplayResult:
        """Promote only after a sealed, artifact-bound local Lean replay (never the vendor).

        ``key_env`` selects where the HMAC signing keys are read from (default:
        the process environment). This is deliberately distinct from the client's
        ``env`` (which only supplies ``ARISTOTLE_API_KEY``), so the local checker
        key and the vendor API key are never conflated.
        """
        return verify_local_replay(
            artifact, verifier, expected_claim_id=expected_claim_id, env=key_env,
        )
