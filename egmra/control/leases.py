"""Durable worker leases, heartbeats, and fencing tokens.

The materialized JSON file is a local M1 scheduler store.  Every mutation is
serialized with an OS lock and atomically replaced.  A production M2 deployment
must provide the same compare-and-swap semantics in PostgreSQL; it must not use
separate in-memory managers as an authority.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
import fcntl
import json
import math
import os
from pathlib import Path
import tempfile
import threading
import time
from typing import Callable, Iterator


class LeaseError(RuntimeError):
    """Lease state is invalid, stale, corrupt, or unavailable."""


@dataclass(frozen=True)
class Lease:
    branch_id: str
    holder: str                 # host:pid
    stage: str
    run_contract_id: str
    acquired_at: float
    heartbeat_at: float
    grace_seconds: float = 60.0
    fencing_token: int = 1

    def is_expired(self, now: float) -> bool:
        return (now - self.heartbeat_at) > self.grace_seconds


@dataclass
class LeaseManager:
    """Lease authority with optional durable state and monotonic fencing.

    ``state_path=None`` is intentionally an ephemeral single-process mode for
    tests and a small local run.  It is not represented as durable scheduling.
    """

    now_fn: Callable[[], float] = time.time
    state_path: str | Path | None = None
    leases: dict[str, Lease] = field(default_factory=dict, init=False)
    generations: dict[str, int] = field(default_factory=dict, init=False)
    _thread_lock: threading.RLock = field(default_factory=threading.RLock, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.state_path is not None:
            self.state_path = Path(self.state_path)
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with self._locked_state(exclusive=False):
                pass

    def _now(self) -> float:
        now = float(self.now_fn())
        if not math.isfinite(now):
            raise LeaseError("lease clock returned a non-finite timestamp")
        return now

    @staticmethod
    def _validate_identity(*, branch_id: str, holder: str, stage: str, run_contract_id: str,
                           grace_seconds: float) -> None:
        if not all(isinstance(value, str) and value.strip()
                   for value in (branch_id, holder, stage, run_contract_id)):
            raise LeaseError("branch, holder, stage, and run contract must be non-empty strings")
        if not math.isfinite(float(grace_seconds)) or grace_seconds <= 0:
            raise LeaseError("lease grace_seconds must be finite and positive")

    @property
    def _lock_path(self) -> Path:
        if not isinstance(self.state_path, Path):
            raise LeaseError("durable lease path is not configured")
        return self.state_path.with_name(self.state_path.name + ".lock")

    @contextmanager
    def _locked_state(self, *, exclusive: bool) -> Iterator[None]:
        with self._thread_lock:
            if self.state_path is None:
                yield
                return
            lock_fd = os.open(self._lock_path, os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
                self._load()
                yield
            finally:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)

    def _load(self) -> None:
        if not isinstance(self.state_path, Path):
            raise LeaseError("durable lease path is not configured")
        if not self.state_path.exists():
            self.leases = {}
            self.generations = {}
            return
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
            if set(raw) != {"schema_version", "leases", "generations"} or raw["schema_version"] != 1:
                raise ValueError("unexpected lease-state schema")
            if not isinstance(raw["leases"], dict) or not isinstance(raw["generations"], dict):
                raise ValueError("lease state collections are not objects")
            leases = {branch_id: Lease(**value) for branch_id, value in raw["leases"].items()}
            generations = {str(branch_id): int(value)
                           for branch_id, value in raw["generations"].items()}
            for branch_id, lease in leases.items():
                if branch_id != lease.branch_id or lease.fencing_token <= 0:
                    raise ValueError("lease identity/token mismatch")
                if generations.get(branch_id, 0) < lease.fencing_token:
                    raise ValueError("fence generation regressed")
            self.leases = leases
            self.generations = generations
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise LeaseError(f"corrupt persisted lease state: {exc}") from exc

    def _persist(self) -> None:
        if self.state_path is None:
            return
        if not isinstance(self.state_path, Path):
            raise LeaseError("durable lease path is invalid")
        payload = {
            "schema_version": 1,
            "leases": {key: asdict(value) for key, value in sorted(self.leases.items())},
            "generations": dict(sorted(self.generations.items())),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
        fd, temp_name = tempfile.mkstemp(
            prefix=self.state_path.name + ".", suffix=".tmp", dir=self.state_path.parent
        )
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, self.state_path)
            directory_fd = os.open(self.state_path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def _next_token(self, branch_id: str) -> int:
        token = self.generations.get(branch_id, 0) + 1
        self.generations[branch_id] = token
        return token

    def acquire(self, *, branch_id: str, holder: str, stage: str, run_contract_id: str,
                grace_seconds: float = 60.0) -> Lease:
        self._validate_identity(
            branch_id=branch_id, holder=holder, stage=stage,
            run_contract_id=run_contract_id, grace_seconds=grace_seconds,
        )
        with self._locked_state(exclusive=True):
            existing = self.leases.get(branch_id)
            now = self._now()
            if existing is not None and not existing.is_expired(now):
                raise LeaseError(f"branch {branch_id} is already leased by {existing.holder}")
            lease = Lease(
                branch_id, holder, stage, run_contract_id, now, now, float(grace_seconds),
                self._next_token(branch_id),
            )
            self.leases[branch_id] = lease
            self._persist()
            return lease

    def renew(self, branch_id: str, holder: str, *, fencing_token: int) -> Lease:
        with self._locked_state(exclusive=True):
            lease = self._require_current(branch_id, holder, fencing_token, allow_expired=False)
            now = self._now()
            renewed = Lease(**{**asdict(lease), "heartbeat_at": now})
            self.leases[branch_id] = renewed
            self._persist()
            return renewed

    def transfer_if_expired(self, *, branch_id: str, new_holder: str,
                            run_contract_id: str) -> Lease | None:
        if not isinstance(new_holder, str) or not new_holder.strip():
            raise LeaseError("new holder must be a non-empty string")
        if not isinstance(run_contract_id, str) or not run_contract_id.strip():
            raise LeaseError("run contract must be a non-empty string")
        with self._locked_state(exclusive=True):
            lease = self.leases.get(branch_id)
            now = self._now()
            if lease is None or not lease.is_expired(now):
                return None
            if lease.run_contract_id != run_contract_id:
                raise LeaseError("cannot transfer lease across incompatible run contracts")
            new_lease = Lease(
                branch_id, new_holder, lease.stage, run_contract_id, now, now,
                lease.grace_seconds, self._next_token(branch_id),
            )
            self.leases[branch_id] = new_lease
            self._persist()
            return new_lease

    def _require_current(self, branch_id: str, holder: str, fencing_token: int,
                         *, allow_expired: bool) -> Lease:
        lease = self.leases.get(branch_id)
        if lease is None:
            raise LeaseError(f"branch {branch_id} has no active lease")
        if lease.fencing_token != fencing_token:
            raise LeaseError("stale fencing token")
        if lease.holder != holder:
            raise LeaseError("lease holder mismatch")
        if not allow_expired and lease.is_expired(self._now()):
            raise LeaseError("lease has expired")
        return lease

    def assert_current(self, branch_id: str, holder: str, fencing_token: int) -> Lease:
        """Validate the fence immediately before accepting a worker side effect."""
        with self._locked_state(exclusive=False):
            return self._require_current(branch_id, holder, fencing_token, allow_expired=False)

    def release(self, branch_id: str, holder: str, *, fencing_token: int) -> None:
        with self._locked_state(exclusive=True):
            self._require_current(branch_id, holder, fencing_token, allow_expired=True)
            del self.leases[branch_id]
            self._persist()
