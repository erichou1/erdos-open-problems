"""Warm Lean development service (effectiveness report R5).

A long-lived Lean REPL (leanprover-community/repl protocol) that loads
Mathlib ONCE and then checks candidate sources in seconds instead of the
~1-2 minute cold ``lake env lean`` start. This is the difference between
~1-2 proof-repair iterations per hour and dozens.

TRUST BOUNDARY (deliberate, load-bearing):

* This service is DEVELOPMENT-GRADE ONLY. Its verdicts are search guidance —
  they gate which candidates are worth a sealed check and shape repair
  feedback. They can NEVER mint a :class:`FormalCertificate`; certificates
  require the pinned checker's HMAC key, which this module never sees.
* Every accepted candidate still goes through the sealed
  ``AttestedKernelRunner`` cold path unchanged.
* All failure modes fail OPEN to the cold path: a dead REPL, protocol
  garbage, or a timeout degrade throughput, never soundness.

Protocol (leanprover-community/repl): one JSON request per line on stdin
(``{"cmd": SOURCE, "env": N}``; the first request omits ``env``); one JSON
response per request on stdout (single-line or pretty-printed — the reader
accumulates lines until a complete JSON document parses). Responses carry
``env`` (new environment id), ``messages`` (severity/data) and ``sorries``.
"""

from __future__ import annotations

import json
import queue
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

_MAX_MESSAGES = 12
_MAX_MESSAGE_CHARS = 500
_MAX_RESPONSE_LINES = 4000


class WarmLeanUnavailable(RuntimeError):
    """The development REPL cannot serve checks; callers fall back to cold."""


@dataclass(frozen=True)
class DevCheckResult:
    """A development-grade compile verdict. NEVER a certificate."""

    ok: bool                       # no error-severity messages
    sorries: int                   # count of reported sorry placeholders
    messages: tuple[str, ...]      # bounded diagnostics (errors first)
    elapsed_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "sorries": self.sorries,
            "messages": list(self.messages),
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "authority": "development-only; never a formal certificate",
        }


class _PipeReader:
    """Background line reader so request waits can time out safely."""

    def __init__(self, stream):
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._thread = threading.Thread(
            target=self._pump, args=(stream,), daemon=True)
        self._thread.start()

    def _pump(self, stream) -> None:
        try:
            for line in stream:
                self._queue.put(line)
        except (ValueError, OSError):  # closed stream during shutdown
            pass
        self._queue.put(None)

    def readline(self, timeout: float) -> str | None:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            raise WarmLeanUnavailable("development REPL response timed out")


@dataclass
class WarmLeanService:
    """One warm REPL process; restart-once on failure, then unavailable.

    ``command`` is the operator-supplied REPL invocation (e.g.
    ``lake env /path/to/repl``) run with ``cwd`` = the pinned Lean project.
    ``header`` is compiled once at startup to build the shared environment
    (default ``import Mathlib`` — the whole point of staying warm).
    """

    command: str
    cwd: str | Path
    header: str = "import Mathlib"
    startup_timeout: float = 900.0     # cold Mathlib load happens once, here
    check_timeout: float = 120.0
    spawn: Callable[..., Any] | None = None   # test seam: fake process factory
    _process: Any = field(default=None, repr=False)
    _reader: _PipeReader | None = field(default=None, repr=False)
    _base_env: int | None = field(default=None, repr=False)
    _restarted: bool = field(default=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    # ── lifecycle ────────────────────────────────────────────────────────────

    def _spawn_process(self) -> Any:
        factory = self.spawn or (lambda: subprocess.Popen(  # pragma: no cover
            self.command, shell=True, cwd=str(self.cwd),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1,
        ))
        return factory()

    def start(self) -> None:
        """Spawn the REPL and compile the header environment once."""
        with self._lock:
            self._start_locked()

    def _start_locked(self) -> None:
        try:
            self._process = self._spawn_process()
            self._reader = _PipeReader(self._process.stdout)
        except (OSError, ValueError) as exc:
            raise WarmLeanUnavailable(f"failed to spawn REPL: {exc}") from exc
        response = self._request_locked(
            {"cmd": self.header}, timeout=self.startup_timeout)
        env = response.get("env")
        if not isinstance(env, int):
            raise WarmLeanUnavailable("REPL header produced no environment id")
        header_errors = [m for m in self._parse_messages(response)
                         if m.startswith("error:")]
        if header_errors:
            raise WarmLeanUnavailable(
                f"REPL header failed to compile: {header_errors[0]}")
        self._base_env = env

    def close(self) -> None:
        with self._lock:
            process, self._process, self._reader = self._process, None, None
            self._base_env = None
        if process is None:
            return
        for method in ("terminate", "kill"):
            try:
                getattr(process, method)()
                break
            except (OSError, AttributeError):
                continue

    @property
    def environment_label(self) -> str:
        """Telemetry-only identity. Never bound into certificates."""
        return f"warm-lean-dev:{self.command}:{self.header}"

    # ── protocol ─────────────────────────────────────────────────────────────

    def _request_locked(self, payload: dict[str, Any], *,
                        timeout: float) -> dict[str, Any]:
        if self._process is None or self._reader is None:
            raise WarmLeanUnavailable("REPL process is not running")
        try:
            # repl protocol: commands are one JSON document TERMINATED BY A
            # BLANK LINE (REPL.Main.getLines reads until an empty line).
            self._process.stdin.write(json.dumps(payload) + "\n\n")
            self._process.stdin.flush()
        except (OSError, ValueError, BrokenPipeError) as exc:
            raise WarmLeanUnavailable(f"REPL write failed: {exc}") from exc
        deadline = time.monotonic() + timeout
        buffer = ""
        for _ in range(_MAX_RESPONSE_LINES):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise WarmLeanUnavailable("development REPL response timed out")
            line = self._reader.readline(timeout=remaining)
            if line is None:
                raise WarmLeanUnavailable("REPL closed its output stream")
            if not buffer and not line.strip():
                continue
            buffer += line
            try:
                document = json.loads(buffer)
            except json.JSONDecodeError:
                continue
            if isinstance(document, dict):
                return document
            raise WarmLeanUnavailable("REPL returned a non-object response")
        raise WarmLeanUnavailable("REPL response exceeded the line budget")

    @staticmethod
    def _parse_messages(response: dict[str, Any]) -> tuple[str, ...]:
        messages: list[str] = []
        raw = response.get("messages")
        for item in raw if isinstance(raw, list) else ():
            if not isinstance(item, dict):
                continue
            severity = str(item.get("severity", ""))
            data = str(item.get("data", ""))[:_MAX_MESSAGE_CHARS]
            messages.append(f"{severity}:{data}")
        messages.sort(key=lambda m: 0 if m.startswith("error:") else 1)
        return tuple(messages[:_MAX_MESSAGES])

    # ── the one public verb ──────────────────────────────────────────────────

    def check(self, source: str) -> DevCheckResult:
        """Development-compile ``source`` against the warm header environment.

        Restarts the REPL at most once per service lifetime on transport
        failure; a second failure raises :class:`WarmLeanUnavailable` so the
        caller falls back to the cold path.
        """
        if not str(source).strip():
            raise WarmLeanUnavailable("empty source")
        with self._lock:
            if self._base_env is None:
                try:
                    self._start_locked()
                except WarmLeanUnavailable:
                    if self._restarted:
                        raise
                    self._restarted = True
                    self._teardown_locked()
                    self._start_locked()
            started = time.monotonic()
            try:
                response = self._request_locked(
                    {"cmd": source, "env": self._base_env},
                    timeout=self.check_timeout)
            except WarmLeanUnavailable:
                if self._restarted:
                    raise
                self._restarted = True
                self._teardown_locked()
                self._start_locked()
                started = time.monotonic()
                response = self._request_locked(
                    {"cmd": source, "env": self._base_env},
                    timeout=self.check_timeout)
            elapsed = time.monotonic() - started
        messages = self._parse_messages(response)
        sorries = response.get("sorries")
        return DevCheckResult(
            ok=not any(m.startswith("error:") for m in messages),
            sorries=len(sorries) if isinstance(sorries, list) else 0,
            messages=messages,
            elapsed_seconds=elapsed,
        )

    def _teardown_locked(self) -> None:
        process, self._process, self._reader = self._process, None, None
        self._base_env = None
        if process is None:
            return
        try:
            process.kill()
        except (OSError, AttributeError):
            pass


def dev_obligation_source(source: str, *, declaration_name: str,
                          expected_type_source: str) -> str:
    """The development mirror of the sealed checker's definitional obligation.

    The warm pre-check compiles the candidate PLUS
    ``example : <expected_type> := @<decl>`` so a candidate that would fail
    the sealed obligation is filtered before spending a cold kernel run.
    """
    body = str(source).rstrip()
    expected = str(expected_type_source).strip()
    name = str(declaration_name).strip()
    if expected and name:
        body += f"\n\nexample : {expected} := @{name}"
    return body + "\n"
