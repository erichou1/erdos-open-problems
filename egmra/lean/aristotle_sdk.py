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
import inspect
import tempfile
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
    def _await(self, value: Any) -> Any:
        if not inspect.isawaitable(value):
            return value
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:  # pragma: no cover - the sync CLI/orchestrator never nest a loop
            raise AristotleClientError(
                "AristotleSdkClient must be driven from synchronous code, "
                "not from within a running event loop"
            )
        if self._loop_obj is None or self._loop_obj.is_closed():
            self._loop_obj = asyncio.new_event_loop()
        return self._loop_obj.run_until_complete(value)

    def close(self) -> None:
        """Close the client-owned event loop (best-effort teardown)."""
        loop = self._loop_obj
        self._loop_obj = None
        if loop is not None and not loop.is_closed():  # pragma: no cover - teardown
            loop.close()

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

    def fetch(self, submission: AristotleSubmission, *, wait: bool = True) -> AristotleArtifact:
        """Download the produced Lean into a hardened quarantine (never promotable)."""
        project = self._projects.get(submission.project_id)
        if project is None:
            project = self._await(
                self.sdk.Project.from_id(validate_job_id(submission.project_id)))
        task = self._task(submission)
        quarantine_dir = self._resolve_quarantine_dir(submission.project_id)
        try:
            if wait:
                self._await(task.wait_for_completion())
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
        except UnsafeJobIdError:
            raise
        except Exception as exc:
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
        status = self.poll(submission)
        return AristotleArtifact(
            job_id=submission.project_id,
            vendor_status=status.raw_status,
            vendor_reports_complete=status.vendor_reports_complete,
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
