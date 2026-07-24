#!/usr/bin/env python3
"""Aristotle (Harmonic) Lean-verification adapter — `aristotle` CLI wrapper.

Harmonic's Aristotle (https://aristotle.harmonic.fun) is driven through the
`aristotle` CLI from the `aristotlelib` package (NOT a raw HTTP API):

    aristotle submit "<prompt>" [--project-dir DIR]   -> prints a project id
    aristotle show <project_id>                        -> "COMPLETE ..." + summary
    aristotle download <project_id> --destination <a>  -> tar.gz project archive

The API key is read from ARISTOTLE_API_KEY (env or .env); no base URL is used.
A completed archive contains `RequestProject/Main.lean` (the Lean proof) and
`ARISTOTLE_SUMMARY.md`. The downloaded project is quarantined and never built:
its vendor-controlled lakefile, toolchain, imports, and build hooks are not a
safe local-kernel boundary. This adapter therefore cannot itself issue trusted
formal evidence.

This adapter submits a run's locked statement (with the candidate as reference),
waits for completion, extracts the Lean proof, and emits a `formal_proof`
VerificationEvidence that `promote_verified_run` feeds to the deterministic gate.

Usage:
    ARISTOTLE_API_KEY=... .venv/bin/python aristotle_verifier.py \\
        --run-dir <run> --promote --publish
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from lean_verify import (
    extract_formal_statements,
    has_incomplete_proof,
)
from egmra.policy import PolicyEnforcer, default_policy_path, load_policy

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
_ARISTOTLE_ENV_KEYS = frozenset({
    "ARISTOTLE_API_KEY",
    "ARISTOTLE_CLI",
    "ARISTOTLE_POLL_INTERVAL_S",
    "ARISTOTLE_TIMEOUT_S",
})
_CHILD_ENV_KEYS = frozenset({
    "PATH",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "TMPDIR",
    "TEMP",
    "TMP",
    "SSL_CERT_FILE",
    "REQUESTS_CA_BUNDLE",
    "CURL_CA_BUNDLE",
})
_SENSITIVE_ENV_NAME_RE = re.compile(
    r"(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH)", re.IGNORECASE,
)

_MAX_MANIFEST_BYTES = 1_000_000
_MAX_STATEMENT_BYTES = 2_000_000
_MAX_CANDIDATE_BYTES = 16 * 1024 * 1024
_MAX_LEAN_BYTES = 16 * 1024 * 1024
_MAX_SUMMARY_BYTES = 2_000_000
_MAX_FIDELITY_BYTES = 4_000_000
_MAX_EVIDENCE_BYTES = 4_000_000
_MAX_VENDOR_TREE_ENTRIES = 10_000
_MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
_MAX_ARCHIVE_MEMBERS = 4_096
_MAX_ARCHIVE_MEMBER_BYTES = 64 * 1024 * 1024
_MAX_ARCHIVE_EXTRACTED_BYTES = 256 * 1024 * 1024


class AristotleError(RuntimeError):
    """Raised when the Aristotle CLI is missing, fails, or returns no proof."""


def _directory_flags() -> int:
    if not hasattr(os, "O_NOFOLLOW"):
        raise AristotleError("safe no-follow filesystem operations are unavailable")
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | os.O_NOFOLLOW
        | getattr(os, "O_NONBLOCK", 0)
    )


def _open_run_root(run_dir: Path) -> int:
    """Pin a run directory without following its last three path components."""
    path = Path(run_dir)
    if ".." in path.parts:
        raise AristotleError("run root may not contain parent traversal")
    absolute = Path(os.path.abspath(os.fspath(path)))
    parent = absolute.parent
    grandparent = parent.parent
    if absolute == parent or parent == grandparent:
        raise AristotleError("run root must have a distinct parent and grandparent")
    grandparent_fd: int | None = None
    parent_fd: int | None = None
    try:
        grandparent_fd = os.open(grandparent, _directory_flags())
        parent_fd = os.open(parent.name, _directory_flags(), dir_fd=grandparent_fd)
        descriptor = os.open(absolute.name, _directory_flags(), dir_fd=parent_fd)
    except OSError as exc:
        raise AristotleError(
            f"run root or its parent/grandparent is not a safe non-symlink directory: {path}"
        ) from exc
    finally:
        if parent_fd is not None:
            os.close(parent_fd)
        if grandparent_fd is not None:
            os.close(grandparent_fd)
    if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise AristotleError(f"run root is not a directory: {path}")
    return descriptor


def _open_child_directory(
    parent_fd: int, name: str, *, label: str, create: bool = False,
) -> int:
    if not name or name in {".", ".."} or "/" in name:
        raise AristotleError(f"{label} has an invalid directory name")
    if create:
        try:
            os.mkdir(name, mode=0o700, dir_fd=parent_fd)
        except FileExistsError:
            pass
        except OSError as exc:
            raise AristotleError(f"cannot create safe {label}") from exc
    try:
        descriptor = os.open(name, _directory_flags(), dir_fd=parent_fd)
    except OSError as exc:
        raise AristotleError(f"{label} is not a safe non-symlink directory") from exc
    if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise AristotleError(f"{label} is not a directory")
    os.fchmod(descriptor, 0o700)
    return descriptor


def _read_regular_at(
    parent_fd: int,
    name: str,
    *,
    max_bytes: int,
    label: str,
    optional: bool = False,
) -> bytes | None:
    """Read one bounded regular child while refusing symlinks and special files."""
    if not name or name in {".", ".."} or "/" in name:
        raise AristotleError(f"{label} has an invalid filename")
    flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
    try:
        descriptor = os.open(name, flags, dir_fd=parent_fd)
    except OSError as exc:
        if optional and exc.errno == errno.ENOENT:
            return None
        raise AristotleError(f"{label} is missing or not a safe regular file") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise AristotleError(f"{label} must be a regular file")
        if metadata.st_size > max_bytes:
            raise AristotleError(f"{label} exceeds the {max_bytes}-byte limit")
        chunks: list[bytes] = []
        remaining = max_bytes + 1
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > max_bytes:
            raise AristotleError(f"{label} exceeds the {max_bytes}-byte limit")
        return payload
    finally:
        os.close(descriptor)


def _write_regular_at(parent_fd: int, name: str, payload: bytes, *, label: str) -> None:
    """Replace/create one regular child without following an existing symlink."""
    if not name or name in {".", ".."} or "/" in name:
        raise AristotleError(f"{label} has an invalid filename")
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_NOFOLLOW
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        descriptor = os.open(name, flags, 0o600, dir_fd=parent_fd)
    except OSError as exc:
        raise AristotleError(f"{label} is not a safe regular output file") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise AristotleError(f"{label} must be a regular output file")
        os.fchmod(descriptor, 0o600)
        os.ftruncate(descriptor, 0)
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise AristotleError(f"short write while persisting {label}")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _decode_utf8(payload: bytes, *, label: str) -> str:
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AristotleError(f"{label} is not valid UTF-8") from exc


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise AristotleError(f"manifest contains duplicate JSON key {key!r}")
        result[key] = value
    return result


def _manifest_from_fd(run_fd: int) -> dict:
    payload = _read_regular_at(
        run_fd, "manifest.json", max_bytes=_MAX_MANIFEST_BYTES, label="run manifest",
    )
    assert payload is not None
    try:
        manifest = json.loads(
            _decode_utf8(payload, label="run manifest"),
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=lambda value: (_ for _ in ()).throw(
                AristotleError(f"manifest contains non-finite JSON value {value}")
            ),
        )
    except json.JSONDecodeError as exc:
        raise AristotleError("run manifest is malformed JSON") from exc
    if not isinstance(manifest, dict):
        raise AristotleError("run manifest must be a JSON object")
    return manifest


def _statement_from_fd(run_fd: int, manifest: dict) -> str:
    payload = _read_regular_at(
        run_fd,
        "problem.txt",
        max_bytes=_MAX_STATEMENT_BYTES,
        label="run problem statement",
        optional=True,
    )
    if payload is not None:
        return _decode_utf8(payload, label="run problem statement")
    statement = manifest.get("statement", "")
    if not isinstance(statement, str):
        raise AristotleError("manifest statement must be a string")
    if len(statement.encode("utf-8")) > _MAX_STATEMENT_BYTES:
        raise AristotleError("manifest statement exceeds the size limit")
    return statement


def _candidate_from_fd(run_fd: int) -> bytes:
    payload = _read_regular_at(
        run_fd, "candidate.md", max_bytes=_MAX_CANDIDATE_BYTES, label="run candidate",
    )
    assert payload is not None
    _decode_utf8(payload, label="run candidate")
    return payload


def _require_policy_enforcer(enforcer) -> PolicyEnforcer:
    # A subclass can override ``require`` and silently approve every feature.
    if type(enforcer) is not PolicyEnforcer:
        raise TypeError("Aristotle entry points require the concrete PolicyEnforcer")
    return enforcer


def _redact_sensitive(text: str, *, explicit: tuple[str, ...] = ()) -> str:
    redacted = str(text or "")
    secrets = {value for value in explicit if value}
    secrets.update(
        value
        for key, value in os.environ.items()
        if value and _SENSITIVE_ENV_NAME_RE.search(key)
    )
    for secret in sorted(secrets, key=len, reverse=True):
        redacted = redacted.replace(secret, "[REDACTED]")
    return redacted


def _load_dotenv_files() -> None:
    """Populate only Aristotle configuration from approved dotenv files.

    The first non-empty value for a key wins and a real environment variable
    always wins (empty placeholder lines are ignored). Other provider, policy,
    signing, and application secrets are deliberately not imported into this
    process as a side effect of configuring Aristotle.
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
            if key in _ARISTOTLE_ENV_KEYS and value and os.environ.get(key, "") == "":
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
    def from_env(
        cls, env: Mapping[str, str] | None = None,
    ) -> "AristotleConfig":
        if env is None:
            _load_dotenv_files()
            active_env: Mapping[str, str] = os.environ
        else:
            active_env = env
        key = str(active_env.get("ARISTOTLE_API_KEY", "")).strip()
        if not key:
            raise AristotleError(
                "ARISTOTLE_API_KEY is not set; put the Harmonic Aristotle key in .env"
            )
        return cls(
            api_key=key,
            cli_path=str(active_env.get("ARISTOTLE_CLI", "")).strip()
            or _default_cli_path(),
            poll_interval_s=float(
                active_env.get(
                    "ARISTOTLE_POLL_INTERVAL_S", str(DEFAULT_POLL_INTERVAL_S),
                )
            ),
            timeout_s=float(
                active_env.get("ARISTOTLE_TIMEOUT_S", str(DEFAULT_TIMEOUT_S))
            ),
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


def _walk_vendor_tree(root: Path) -> tuple[list[Path], list[Path]]:
    """Inventory a quarantined vendor tree without following any symlink."""
    root = Path(root)
    root_fd = _open_run_root(root)
    os.close(root_fd)
    lean_files: list[Path] = []
    summaries: list[Path] = []
    entries = 0
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        safe_directories = []
        for name in directories:
            entries += 1
            candidate = current_path / name
            if candidate.is_symlink():
                raise AristotleError("vendor archive contains a directory symlink")
            safe_directories.append(name)
        directories[:] = safe_directories
        for name in files:
            entries += 1
            candidate = current_path / name
            try:
                metadata = candidate.lstat()
            except OSError as exc:
                raise AristotleError("vendor archive changed during quarantine scan") from exc
            if not stat.S_ISREG(metadata.st_mode):
                raise AristotleError("vendor archive contains a non-regular file")
            if name == "ARISTOTLE_SUMMARY.md":
                summaries.append(candidate)
            elif name.endswith(".lean") and name != "lakefile.lean":
                lean_files.append(candidate)
            if entries > _MAX_VENDOR_TREE_ENTRIES:
                raise AristotleError("vendor archive exceeds the quarantine entry limit")
    lean_files.sort(key=lambda path: (path.name != "Main.lean", str(path)))
    summaries.sort()
    return lean_files, summaries


def _read_bounded_path(path: Path, *, max_bytes: int, label: str) -> str:
    parent_fd = _open_run_root(Path(path).parent)
    try:
        payload = _read_regular_at(
            parent_fd, Path(path).name, max_bytes=max_bytes, label=label,
        )
        assert payload is not None
        return _decode_utf8(payload, label=label)
    finally:
        os.close(parent_fd)


def _read_bounded_file_bytes(path: Path, *, max_bytes: int, label: str) -> bytes:
    parent_fd = _open_run_root(Path(path).parent)
    try:
        payload = _read_regular_at(
            parent_fd, Path(path).name, max_bytes=max_bytes, label=label,
        )
        assert payload is not None
        return payload
    finally:
        os.close(parent_fd)


def _extract_quarantined_archive(payload: bytes, destination: Path) -> None:
    """Validate archive shape and resource bounds before private extraction."""
    members = []
    member_kinds: dict[str, str] = {}
    extracted_bytes = 0
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:*") as archive:
            for index, member in enumerate(archive, start=1):
                if index > _MAX_ARCHIVE_MEMBERS:
                    raise AristotleError(
                        f"Aristotle archive exceeds {_MAX_ARCHIVE_MEMBERS} members"
                    )
                name = member.name
                path = PurePosixPath(name)
                if (
                    not name
                    or len(name.encode("utf-8", errors="ignore")) > 4_096
                    or path.is_absolute()
                    or any(part in {"", ".", ".."} for part in path.parts)
                ):
                    raise AristotleError("Aristotle archive contains an unsafe path")
                if not (member.isdir() or member.isreg()):
                    raise AristotleError(
                        "Aristotle archive contains a link or non-regular member"
                    )
                if getattr(member, "sparse", None) is not None:
                    raise AristotleError("Aristotle archive contains a sparse member")
                if member.size < 0 or member.size > _MAX_ARCHIVE_MEMBER_BYTES:
                    raise AristotleError("Aristotle archive member exceeds the size limit")

                key = "/".join(path.parts)
                if key in member_kinds:
                    raise AristotleError("Aristotle archive contains duplicate member paths")
                for offset in range(1, len(path.parts)):
                    ancestor = "/".join(path.parts[:offset])
                    if member_kinds.get(ancestor) == "file":
                        raise AristotleError(
                            "Aristotle archive nests content below a regular file"
                        )
                if member.isreg() and any(
                    existing.startswith(key + "/") for existing in member_kinds
                ):
                    raise AristotleError(
                        "Aristotle archive replaces a directory with a regular file"
                    )
                member_kinds[key] = "directory" if member.isdir() else "file"
                if member.isreg():
                    extracted_bytes += member.size
                    if extracted_bytes > _MAX_ARCHIVE_EXTRACTED_BYTES:
                        raise AristotleError(
                            "Aristotle archive exceeds the aggregate extraction limit"
                        )
                members.append(member)
            archive.extractall(destination, members=members, filter="data")
    except AristotleError:
        raise
    except (tarfile.TarError, OSError, UnicodeError) as exc:
        raise AristotleError("Aristotle archive is malformed or unsafe") from exc


def read_summary(root: Path) -> str:
    _, summaries = _walk_vendor_tree(root)
    if not summaries:
        return ""
    return _read_bounded_path(
        summaries[0], max_bytes=_MAX_SUMMARY_BYTES, label="Aristotle summary",
    )


def assess_project(state: str, extracted_root: Path, *, project_id: str = "",
                   target_outcome: str = "candidate_proved",
                   run_kernel: bool = True, kernel_runner=None,
                   fetch_cache: bool = True) -> AristotleResult:
    """Quarantine a downloaded vendor project without executing its build files.

    A vendor archive controls its ``lakefile.lean``/``lakefile.toml``, toolchain,
    imports, and build hooks. Running ``lake build`` in that tree would execute
    attacker-controlled configuration outside the hardened Lean service. This
    legacy adapter therefore performs bounded, no-follow artifact inspection
    only and always returns an unverified quarantine result. ``run_kernel`` and
    ``kernel_runner`` remain accepted for API compatibility but are never used.
    """
    root = Path(extracted_root)
    lean_files, summaries = _walk_vendor_tree(root)
    lean_file = lean_files[0] if lean_files else None
    lean_source = (
        _read_bounded_path(lean_file, max_bytes=_MAX_LEAN_BYTES, label="vendor Lean source")
        if lean_file else ""
    )
    summary = (
        _read_bounded_path(
            summaries[0], max_bytes=_MAX_SUMMARY_BYTES, label="Aristotle summary",
        )
        if summaries else ""
    )
    formal_statements = tuple(extract_formal_statements(lean_source))

    vendor_report_looks_complete = bool(
        state.upper() in _TERMINAL_OK
        and lean_source.strip()
        and not has_incomplete_proof(lean_source)
    )
    # Explicitly reference compatibility parameters so linters do not suggest
    # restoring the unsafe execution path.
    _ = (run_kernel, kernel_runner, fetch_cache, target_outcome)
    return AristotleResult(
        verified=False, verdict="unknown", state=state.upper(),
        project_id=project_id, lean_source=lean_source, summary=summary,
        verification_method="vendor_artifact_quarantined",
        lean_status="untrusted_project_not_executed",
        formal_statements=formal_statements,
        raw={
            "lean_file": str(lean_file) if lean_file else "",
            "vendor_report_looks_complete": vendor_report_looks_complete,
            "quarantine_reason": "vendor build configuration was not executed",
        },
    )


# ── CLI client ───────────────────────────────────────────────────────────────

class AristotleClient:
    """Wraps the `aristotle` CLI; the command runner is injectable for tests."""

    def __init__(self, config: AristotleConfig, runner=None, *, enforcer=None):
        self.config = config
        self._runner = runner or self._default_runner
        self.enforcer: PolicyEnforcer | None = (
            _require_policy_enforcer(enforcer) if enforcer is not None else None
        )

    def _require_external_routing(self) -> None:
        active_enforcer = self.enforcer
        if active_enforcer is None:
            active_enforcer = PolicyEnforcer(load_policy(default_policy_path()))
        active_enforcer = _require_policy_enforcer(active_enforcer)
        self.enforcer = active_enforcer
        active_enforcer.require(
            "external_prover_routing",
            entry_point="aristotle_verifier.AristotleClient._run",
        )

    def _default_runner(self, args: list[str]) -> subprocess.CompletedProcess:
        # Provider subprocesses receive a deliberately tiny environment. In
        # particular, EGMRA signing keys, model-provider keys, cloud tokens,
        # user HOME configuration, and unrelated credentials are never copied.
        env = {
            key: os.environ[key]
            for key in _CHILD_ENV_KEYS
            if os.environ.get(key)
        }
        env["ARISTOTLE_API_KEY"] = self.config.api_key
        return subprocess.run(
            [self.config.cli_path, *args],
            capture_output=True, text=True, env=env, check=False,
            timeout=self.config.timeout_s,
        )

    def _run(self, args: list[str]) -> str:
        # Check the signed feature policy before spawning a process or sending a
        # prompt. Direct client methods are public entry points, not trusted
        # merely because verify_run also checks policy.
        self._require_external_routing()
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
            detail = _redact_sensitive(
                (proc.stderr or proc.stdout or "").strip(),
                explicit=(self.config.api_key,),
            )[:400]
            raise AristotleError(
                f"aristotle {args[0]} failed (exit {proc.returncode}): "
                f"{detail}"
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
            archive_payload = _read_bounded_file_bytes(
                archive, max_bytes=_MAX_ARCHIVE_BYTES, label="Aristotle archive",
            )
            extracted = Path(work) / "extracted"
            extracted.mkdir()
            _extract_quarantined_archive(archive_payload, extracted)
            return assess_project(
                "COMPLETE", extracted, project_id=project_id,
                target_outcome=target_outcome,
            )


# ── evidence emission + run integration ──────────────────────────────────────

def _read_manifest(run_dir: Path) -> dict:
    run_fd = _open_run_root(Path(run_dir))
    try:
        return _manifest_from_fd(run_fd)
    finally:
        os.close(run_fd)


def _statement_for_run(run_dir: Path, manifest: dict) -> str:
    run_fd = _open_run_root(Path(run_dir))
    try:
        return _statement_from_fd(run_fd, manifest)
    finally:
        os.close(run_fd)


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

    This legacy adapter deliberately emits ``passed=false``.  A vendor COMPLETE
    result or even a local ``lake build`` is not the hardened T5 certificate the
    release architecture requires: it still lacks independent checker replay and
    approved intent/formal-correspondence certificates.  The artifact remains
    available for quarantine/audit and can be promoted only after the EGMRA Lean
    service issues a separately authenticated, scope-bound certificate.
    """
    run_dir = Path(run_dir)
    run_fd = _open_run_root(run_dir)
    artifact_fd: int | None = None
    try:
        manifest = _manifest_from_fd(run_fd)
        candidate_payload = _candidate_from_fd(run_fd)
        statement = _statement_from_fd(run_fd, manifest)
        artifact_fd = _open_child_directory(
            run_fd, "aristotle", label="Aristotle artifact directory", create=True,
        )
        os.fsync(run_fd)
        candidate_sha256 = hashlib.sha256(candidate_payload).hexdigest()
        statement_sha256 = str(manifest.get("statement_sha256", ""))
        target = (
            target_outcome
            if target_outcome in {"candidate_proved", "candidate_disproved"}
            else "candidate_proved"
        )
        kernel_ok = result.verification_method == "local_lean_kernel"

        lean_payload = (result.lean_source or "").encode("utf-8")
        summary_payload = (result.summary or "").encode("utf-8")
        if len(lean_payload) > _MAX_LEAN_BYTES:
            raise AristotleError("Lean artifact exceeds the output size limit")
        if len(summary_payload) > _MAX_SUMMARY_BYTES:
            raise AristotleError("Aristotle summary exceeds the output size limit")
        formal_statements = list(result.formal_statements)
        if len(formal_statements) > 256 or any(
            not isinstance(item, str) for item in formal_statements
        ):
            raise AristotleError("formal statement inventory is invalid or too large")
        fidelity_payload = (json.dumps({
            "informal_statement": statement,
            "formal_statements": formal_statements,
            "statement_fidelity": "unreviewed",
            "note": "A separately isolated kernel replay and independent review must "
                    "confirm both the proof and its correspondence to the Erdos problem.",
        }, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        if len(fidelity_payload) > _MAX_FIDELITY_BYTES:
            raise AristotleError("fidelity record exceeds the output size limit")

        record = {
            "schema_version": 2,
            "kind": "formal_proof",
            "verifier": verifier,
            "outcome": target,
            "statement_sha256": statement_sha256,
            "candidate_sha256": candidate_sha256,
            "artifact_path": "Main.lean",
            "artifact_sha256": hashlib.sha256(lean_payload).hexdigest(),
            "passed": False,
            "verification_method": result.verification_method,
            "validator_id": (
                "unattested.local-lean-kernel/v1" if kernel_ok
                else "untrusted.aristotle-report/v1"
            ),
            "certificate_sha256": hashlib.sha256(json.dumps({
                "project_id": result.project_id,
                "state": result.state,
                "verdict": result.verdict,
                "lean_status": result.lean_status,
                "formal_statements": formal_statements,
            }, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
            "scope_sha256": statement_sha256,
            "coverage": "encoded_theorem_only",
            "statement_fidelity": "unreviewed",
            "attestor_key_id": "",
            "attestation": "",
            "problem_number": manifest.get("problem_number", 0),
            "run_contract_id": manifest.get("run_contract_id", ""),
            "execution_id": manifest.get("execution_id", ""),
            "run_context_id": manifest.get("run_context_id", ""),
        }
        evidence_payload = (
            json.dumps([record], indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8")
        if len(evidence_payload) > _MAX_EVIDENCE_BYTES:
            raise AristotleError("evidence record exceeds the output size limit")
        _write_regular_at(
            artifact_fd, "Main.lean", lean_payload, label="Lean artifact",
        )
        _write_regular_at(
            artifact_fd,
            "ARISTOTLE_SUMMARY.md",
            summary_payload,
            label="Aristotle summary",
        )
        _write_regular_at(
            artifact_fd, "fidelity.json", fidelity_payload, label="fidelity record",
        )
        _write_regular_at(
            artifact_fd, "evidence.json", evidence_payload, label="evidence record",
        )
        os.fsync(artifact_fd)
    finally:
        if artifact_fd is not None:
            os.close(artifact_fd)
        os.close(run_fd)
    return run_dir / "aristotle" / "evidence.json"


def verify_run(
    run_dir: Path, *,
    config: AristotleConfig | None = None,
    client: AristotleClient | None = None,
    promote_result: bool = False,
    publish: bool = False,
    triage_dir: Path | None = None,
    category: str = "open",
    require_kernel: bool = False,
    enforcer=None,
    attestation_env: dict[str, str] | None = None,
):
    """Verify a completed proof run with Aristotle and emit formal evidence.

    Returns ``(AristotleResult, evidence_path, promoted_or_None)``.
    """
    active_enforcer = enforcer or getattr(client, "enforcer", None)
    if active_enforcer is None:
        active_enforcer = PolicyEnforcer(load_policy(default_policy_path()))
    active_enforcer = _require_policy_enforcer(active_enforcer)
    # Both external routing and automated evidence generation are independently
    # gated. Enforce before reading provider credentials or invoking the CLI.
    active_enforcer.require(
        "external_prover_routing", entry_point="aristotle_verifier.verify_run",
    )
    active_enforcer.require(
        "automated_external_evidence", entry_point="aristotle_verifier.verify_run",
    )

    run_dir = Path(run_dir)
    run_fd = _open_run_root(run_dir)
    try:
        manifest = _manifest_from_fd(run_fd)
        statement = _statement_from_fd(run_fd, manifest)
        candidate_payload = _candidate_from_fd(run_fd)
        artifact_fd = _open_child_directory(
            run_fd, "aristotle", label="Aristotle artifact directory", create=True,
        )
        try:
            input_fd = _open_child_directory(
                artifact_fd, "input", label="Aristotle input directory", create=True,
            )
            try:
                _write_regular_at(
                    input_fd,
                    "statement.md",
                    statement.encode("utf-8"),
                    label="Aristotle statement input",
                )
                _write_regular_at(
                    input_fd,
                    "candidate.md",
                    candidate_payload,
                    label="Aristotle candidate input",
                )
                os.fsync(input_fd)
            finally:
                os.close(input_fd)
        finally:
            os.close(artifact_fd)
    finally:
        os.close(run_fd)
    if not statement.strip():
        raise AristotleError(f"run {run_dir} has no statement to verify")
    target = str(manifest.get("candidate_outcome", "")).strip().lower()
    if target not in {"candidate_proved", "candidate_disproved"}:
        target = "candidate_proved"

    client = client or AristotleClient(
        config or AristotleConfig.from_env(), enforcer=active_enforcer,
    )
    client_enforcer = _require_policy_enforcer(client.enforcer)
    if client_enforcer.policy.policy_hash != active_enforcer.policy.policy_hash:
        raise AristotleError("client and verification feature policies do not match")
    # Never hand a provider a path that an untrusted run owner could replace
    # between validation and subprocess traversal. The run-local input copy is
    # retained for audit, while the provider receives a private staging copy.
    with tempfile.TemporaryDirectory(prefix="egmra-aristotle-input-") as staging:
        staging_dir = Path(staging)
        (staging_dir / "statement.md").write_bytes(statement.encode("utf-8"))
        (staging_dir / "candidate.md").write_bytes(candidate_payload)
        result = client.prove(
            _build_prompt(statement, target),
            project_dir=staging_dir,
            target_outcome=target,
        )
    # M0 (spec §9.1): local pinned-kernel replay is the non-overridable default for
    # promotion. A vendor-reported COMPLETE can never yield passed=true on a path
    # that feeds the gate.
    require_kernel_for_evidence = require_kernel or promote_result or publish
    evidence_path = write_formal_proof_evidence(
        run_dir, result, target_outcome=target, require_kernel=require_kernel_for_evidence)
    promoted = None
    if promote_result or publish:
        from promote_verified_run import promote
        promoted = promote(
            run_dir, evidence_path, publish=publish, category=category,
            triage_dir=Path(triage_dir) if triage_dir is not None else None,
            enforcer=active_enforcer,
            attestation_env=attestation_env,
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
    parser.add_argument(
        "--policy", type=Path, required=True,
        help="signed policy enabling external routing and evidence generation",
    )
    args = parser.parse_args()
    enforcer = PolicyEnforcer(load_policy(args.policy))
    result, evidence_path, promoted = verify_run(
        args.run_dir.expanduser(),
        config=AristotleConfig.from_env(),
        promote_result=args.promote or args.publish,
        publish=args.publish,
        triage_dir=args.triage.resolve(),
        category=args.category,
        enforcer=enforcer,
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
