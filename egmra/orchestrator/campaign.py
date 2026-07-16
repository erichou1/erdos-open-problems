"""Durable multi-problem campaign with a bounded worker pool (task B3).

A single ``egmra run`` handles one problem. A *campaign* drives many problems
across up to five bounded workers with durable, resumable state so that a crash,
lost lease, throttle, or restart never drops or duplicates a problem:

* Each problem is leased to exactly one worker with a monotonic fencing token; a
  stale fencing token can never complete or overwrite a problem (no duplicates).
* Expired leases (a crashed/hung worker) return the problem to the queue and are
  re-leased (no lost problems).
* Provider throttling retains the problem for a later attempt — never a failure.
* State is content-addressed + HMAC-signed and written atomically under an OS
  lock; a tampered state file fails closed; resume reconciles and continues with
  no skipped or duplicated index.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol

from egmra.provenance.hashing import canonical_json, content_id

_SCHEMA_VERSION = 1
_MIN_KEY_BYTES = 32
_TERMINAL = frozenset({"done", "failed"})


class CampaignError(RuntimeError):
    """Campaign state is malformed, tampered, or used inconsistently."""


class _NoConfiguredProviderOutage(Exception):
    """Sentinel: ``drain`` retains only provider outages the caller opts into.

    Used as the default ``provider_unavailable`` so a generic runner error is a
    recoverable *failure*, not silently retained forever.
    """


class _NoConfiguredPermanentFailure(Exception):
    """Sentinel used when the caller has no typed permanent failure class."""


def _campaign_key(env: dict[str, str] | None = None) -> bytes:
    source = os.environ if env is None else env
    raw = source.get("EGMRA_CHECKPOINT_KEY", "")
    key = raw.encode("utf-8")
    if len(key) < _MIN_KEY_BYTES:
        raise CampaignError("EGMRA_CHECKPOINT_KEY must contain at least 32 bytes")
    return key


@dataclass
class Assignment:
    problem_id: str
    status: str = "pending"          # pending|leased|retained|done|failed
    worker_id: str = ""
    fencing_token: int = 0
    lease_expires_at: float = 0.0
    attempts: int = 0
    # Infrastructure retries (throttle, dropped connection, closed tab) are
    # counted SEPARATELY from mathematical attempts: they refund the attempt
    # they interrupted, but exhaust their own (much larger) budget so a
    # permanently broken environment still terminates honestly.
    infra_retries: int = 0
    # Evidence-based resamples: a COMPLETED problem whose outcome showed real
    # progress may be requeued for another independent run (bounded).
    resamples: int = 0
    result_state: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


# ── pluggable durable state stores (signed; file default, Postgres opt-in) ────

def _hmac_hex(key: bytes, message: str) -> str:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).hexdigest()


def _sign_body(key: bytes, body: dict[str, Any]) -> str:
    return _hmac_hex(key, canonical_json(body))


class CampaignStore(Protocol):
    """Durable, mutually-exclusive storage for one campaign's signed state."""

    def read(self) -> dict[str, Any] | None: ...
    def write(self, body: dict[str, Any]) -> None: ...
    def locked(self): ...  # cross-process mutual-exclusion context manager
    def close(self) -> None: ...


class FileCampaignStore:
    """Signed-JSON file store (default): atomic write + an OS advisory file lock."""

    def __init__(self, state_path: str | Path, *, env: dict[str, str] | None = None) -> None:
        self.state_path = Path(state_path)
        self._key = _campaign_key(env)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def read(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise CampaignError(f"cannot read campaign state: {exc}") from exc
        if not isinstance(state, dict) or "signature" not in state:
            raise CampaignError("campaign state is malformed")
        body = {k: v for k, v in state.items() if k != "signature"}
        if not hmac.compare_digest(_sign_body(self._key, body), state["signature"]):
            raise CampaignError("campaign state signature is invalid (tampered or wrong key)")
        return body

    def write(self, body: dict[str, Any]) -> None:
        state = dict(body) | {"signature": _sign_body(self._key, body)}
        tmp = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
        tmp.write_text(json.dumps(state), encoding="utf-8")
        os.chmod(tmp, 0o600)
        os.replace(tmp, self.state_path)

    @contextmanager
    def locked(self):
        lock_path = self.state_path.with_suffix(self.state_path.suffix + ".lock")
        handle = open(lock_path, "a+")
        try:
            try:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            except (ImportError, OSError):
                pass
            yield
        finally:
            handle.close()

    def close(self) -> None:
        return None


class PostgresCampaignStore:
    """DB-backed campaign store: signed state in one row + a cross-process advisory
    lock (``pg_advisory_lock``), so leases/checkpoints are durable and coordinated
    across processes/hosts sharing the database (not just a local JSON file).

    Requires a Postgres server + the optional psycopg dependency. The signed body
    is stored as canonical JSON *text* (never JSONB) so the tamper-evident
    signature is verified against the exact stored bytes. Same signing key and
    ``CampaignError`` fail-closed contract as the file store.
    """

    schema_ddl = (
        "CREATE TABLE IF NOT EXISTS campaign_state ("
        " name TEXT PRIMARY KEY, body TEXT NOT NULL, signature TEXT NOT NULL,"
        " updated_at TIMESTAMPTZ NOT NULL DEFAULT now());"
    )

    def __init__(self, dsn: str, *, name: str, env: dict[str, str] | None = None) -> None:
        from urllib.parse import urlsplit, urlunsplit

        if not isinstance(dsn, str):
            raise ValueError("Postgres DSN must be a string")
        parsed = urlsplit(dsn)
        if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname \
                or not parsed.path or parsed.path == "/":
            raise ValueError("Postgres DSN must identify a postgres host and database")
        if not isinstance(name, str) or not name.strip():
            raise CampaignError("campaign store name must be a non-empty string")
        self._dsn = dsn
        self.name = name
        self._key = _campaign_key(env)
        self._conn = None
        self._lock = threading.RLock()
        # A stable 64-bit advisory-lock key derived from the campaign name.
        self._lock_key = int.from_bytes(
            hashlib.sha256(name.encode("utf-8")).digest()[:8], "big", signed=True)
        host = parsed.hostname + (f":{parsed.port}" if parsed.port else "")
        self.dsn = urlunsplit((parsed.scheme, host, parsed.path, parsed.query, ""))

    def connect(self):  # pragma: no cover - requires a database server
        try:
            import psycopg  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "Postgres adapter unavailable: install the optional psycopg dependency"
            ) from exc
        try:
            connection = psycopg.connect(self._dsn, connect_timeout=5)
            with connection.cursor() as cursor:
                cursor.execute(self.schema_ddl)
            connection.commit()
            connection.autocommit = True
            return connection
        except Exception as exc:
            raise RuntimeError(
                f"Postgres connection/schema initialization failed for {self.dsn}") from exc

    def migrate(self) -> None:  # pragma: no cover - requires a database server
        self.connect().close()

    def _connection(self):  # pragma: no cover - requires a database server
        if self._conn is None or getattr(self._conn, "closed", False):
            self._conn = self.connect()
        return self._conn

    @staticmethod
    def _is_disconnect(exc: BaseException) -> bool:
        """True for a dropped/stale connection (reconnect + retry is safe).

        Neon (serverless Postgres) closes idle connections, and a campaign
        holds one idle across each multi-minute browser generation, so a
        server-side drop is the common case — the client only discovers it on
        the NEXT statement (``closed`` stays False until then).
        """
        try:
            import psycopg  # type: ignore[import-not-found]
        except ImportError:  # pragma: no cover
            return False
        return isinstance(exc, (psycopg.OperationalError, psycopg.InterfaceError))

    def _reset(self) -> None:  # pragma: no cover - requires a database server
        conn, self._conn = self._conn, None
        if conn is not None:
            try:
                conn.close()
            except Exception:  # noqa: BLE001 - discarding a dead connection
                pass

    def _with_connection(self, operation, *, _retries: int = 1):  # pragma: no cover
        """Run ``operation(connection)``, reconnecting ONCE on a dropped connection."""
        try:
            return operation(self._connection())
        except Exception as exc:  # noqa: BLE001 - reconnect only on disconnects
            if _retries > 0 and self._is_disconnect(exc):
                self._reset()
                return self._with_connection(operation, _retries=_retries - 1)
            raise

    def read(self) -> dict[str, Any] | None:  # pragma: no cover - requires a server
        def _op(connection):
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT body, signature FROM campaign_state WHERE name = %s",
                    (self.name,))
                return cursor.fetchone()
        row = self._with_connection(_op)
        if row is None:
            return None
        body_text, signature = str(row[0]), str(row[1])
        if not hmac.compare_digest(_hmac_hex(self._key, body_text), signature):
            raise CampaignError("campaign state signature is invalid (tampered or wrong key)")
        return json.loads(body_text)

    def write(self, body: dict[str, Any]) -> None:  # pragma: no cover - requires a server
        body_text = canonical_json(body)
        signature = _hmac_hex(self._key, body_text)

        def _op(connection):
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO campaign_state (name, body, signature, updated_at) "
                    "VALUES (%s, %s, %s, now()) ON CONFLICT (name) DO UPDATE SET "
                    "body = EXCLUDED.body, signature = EXCLUDED.signature, updated_at = now()",
                    (self.name, body_text, signature))
        self._with_connection(_op)

    @contextmanager
    def locked(self):  # pragma: no cover - requires a database server
        # Reconnect at ACQUIRE time if the idle connection was dropped; the
        # advisory lock is session-scoped, so a dropped connection has already
        # released any prior lock server-side (unlock below is best-effort).
        def _acquire(connection):
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_lock(%s)", (self._lock_key,))
            return connection
        connection = self._with_connection(_acquire)
        try:
            yield
        finally:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_advisory_unlock(%s)", (self._lock_key,))
            except Exception:  # noqa: BLE001 - a dropped connection freed the lock already
                pass

    def close(self) -> None:  # pragma: no cover - requires a database server
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                finally:
                    self._conn = None


class Campaign:
    """A durable, resumable campaign over an ordered list of problems."""

    def __init__(
        self,
        state_path: str | Path,
        *,
        worker_ids: tuple[str, ...],
        lease_seconds: float = 900.0,
        max_attempts: int = 5,
        max_infra_retries: int = 24,
        env: dict[str, str] | None = None,
        store: CampaignStore | None = None,
    ) -> None:
        if not 1 <= len(worker_ids) <= 5:
            raise CampaignError("a campaign runs between 1 and 5 workers")
        if len(set(worker_ids)) != len(worker_ids):
            raise CampaignError("worker ids must be unique")
        self.state_path = Path(state_path)
        self.worker_ids = tuple(worker_ids)
        self.lease_seconds = float(lease_seconds)
        self.max_attempts = int(max_attempts)
        self.max_infra_retries = int(max_infra_retries)
        self._thread_lock = threading.RLock()
        # Durable state lives behind a pluggable store: a signed local JSON file by
        # default, or an opt-in DB-backed store so leases/checkpoints are coordinated
        # across processes/hosts sharing a database.
        self._store: CampaignStore = store if store is not None \
            else FileCampaignStore(state_path, env=env)

    def close(self) -> None:
        """Release any store resources (a no-op for the file store)."""
        self._store.close()

    # ── durable state (delegated to the pluggable store) ─────────────────────
    def _write(self, state: dict[str, Any]) -> None:
        self._store.write(state)

    def _read(self) -> dict[str, Any] | None:
        return self._store.read()

    @contextmanager
    def _locked(self):
        # In-process mutual exclusion (threads) plus the store's cross-process lock.
        with self._thread_lock:
            with self._store.locked():
                yield

    def _decode(self, state: dict[str, Any]) -> dict[str, Assignment]:
        return {pid: Assignment(**a) for pid, a in state["assignments"].items()}

    def _encode(self, campaign_id: str, order: list[str],
                assignments: dict[str, Assignment], fencing: int,
                machines: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
        return {
            "schema_version": _SCHEMA_VERSION,
            "campaign_id": campaign_id,
            "order": list(order),
            "fencing_counter": fencing,
            "assignments": {pid: a.to_dict() for pid, a in assignments.items()},
            # Signed cross-machine liveness/version registry. Optional for
            # backward compatibility with pre-registry campaign states.
            "machines": dict(machines or {}),
        }

    def machine_heartbeat(self, machine_id: str, *, metadata: dict[str, Any],
                          now: float) -> None:
        """Register/renew one physical computer in signed shared state.

        A process crash simply stops heartbeats; readers classify it stale.
        This registry is operational metadata only — it never affects leases,
        truth, ranking, or release.
        """
        if not isinstance(machine_id, str) or not machine_id.strip():
            raise CampaignError("machine id must be non-empty")
        with self._locked():
            state = self._read()
            if state is None:
                raise CampaignError("campaign is not initialized")
            machines = dict(state.get("machines") or {})
            previous = machines.get(machine_id) or {}
            record = {
                "machine_id": machine_id,
                "hostname": str(metadata.get("hostname", machine_id))[:200],
                "process_id": int(metadata.get("process_id", 0) or 0),
                "branch": str(metadata.get("branch", ""))[:300],
                "code_commit": str(metadata.get("code_commit", ""))[:64],
                "latest_commit": str(metadata.get("latest_commit", ""))[:64],
                "pipeline_tree": str(metadata.get("pipeline_tree", ""))[:64],
                "latest_pipeline_tree": str(
                    metadata.get("latest_pipeline_tree", ""))[:64],
                "version_status": str(metadata.get("version_status", "unknown"))[:32],
                "started_at": float(previous.get(
                    "started_at", metadata.get("started_at", now))),
                "heartbeat_at": float(now),
                "worker_ids": [str(item)[:250]
                               for item in metadata.get("worker_ids", ())][:5],
                "stopped_at": 0.0,
            }
            machines[machine_id] = record
            self._write(self._encode(
                state["campaign_id"], state["order"], self._decode(state),
                int(state["fencing_counter"]), machines))

    def machine_stopped(self, machine_id: str, *, now: float) -> None:
        """Mark a graceful shutdown; crashes remain detectable as stale."""
        with self._locked():
            state = self._read()
            if state is None:
                return
            machines = dict(state.get("machines") or {})
            if machine_id not in machines:
                return
            machines[machine_id] = {
                **machines[machine_id], "stopped_at": float(now),
                "heartbeat_at": float(now),
            }
            self._write(self._encode(
                state["campaign_id"], state["order"], self._decode(state),
                int(state["fencing_counter"]), machines))

    # ── lifecycle ────────────────────────────────────────────────────────────
    def initialize(self, campaign_id: str, problem_ids: list[str]) -> list[str]:
        """Create or grow campaign state; returns the campaign's full order.

        Joining an EXISTING campaign tolerates a permutation of the same
        problem set (continuous rerank legitimately reorders shared state) and
        GROWS the set when new ranked problems appear: unknown ids are
        appended as fresh pending assignments, and existing assignments —
        leased, done, failed, retained — are never touched or dropped.  A
        different campaign id still fails closed.
        """
        if len(set(problem_ids)) != len(problem_ids):
            raise CampaignError("problem ids must be unique")
        with self._locked():
            existing = self._read()
            if existing is not None:
                if existing["campaign_id"] != campaign_id:
                    raise CampaignError(
                        "campaign state already exists for a different campaign; "
                        "use resume or a fresh state path"
                    )
                known = set(existing["order"])
                added = [pid for pid in problem_ids if pid not in known]
                if not added:
                    return list(existing["order"])
                assignments = self._decode(existing)
                for pid in added:
                    assignments[pid] = Assignment(problem_id=pid)
                order = list(existing["order"]) + added
                self._write(self._encode(
                    campaign_id, order, assignments,
                    int(existing["fencing_counter"]),
                    existing.get("machines")))
                return order
            assignments = {pid: Assignment(problem_id=pid) for pid in problem_ids}
            self._write(self._encode(campaign_id, list(problem_ids), assignments, 0))
            return list(problem_ids)

    def lease(self, worker_id: str, *, now: float) -> Assignment | None:
        """Atomically lease the next available problem to ``worker_id``.

        Available = pending, retained, or a leased problem whose lease expired.
        Returns a fresh fencing token; never returns a problem twice concurrently.
        """
        if worker_id not in self.worker_ids:
            raise CampaignError(f"unknown worker id: {worker_id!r}")
        with self._locked():
            state = self._read()
            if state is None:
                raise CampaignError("campaign is not initialized")
            assignments = self._decode(state)
            fencing = int(state["fencing_counter"])
            for pid in state["order"]:
                a = assignments[pid]
                available = (
                    a.status in {"pending", "retained"}
                    or (a.status == "leased" and a.lease_expires_at <= now)
                )
                if not available:
                    continue
                if a.attempts >= self.max_attempts:
                    a.status = "failed"
                    self._write(self._encode(state["campaign_id"], state["order"],
                                             assignments, fencing,
                                             state.get("machines")))
                    continue
                fencing += 1
                a.status = "leased"
                a.worker_id = worker_id
                a.fencing_token = fencing
                a.lease_expires_at = now + self.lease_seconds
                a.attempts += 1
                self._write(self._encode(state["campaign_id"], state["order"],
                                         assignments, fencing,
                                         state.get("machines")))
                return Assignment(**a.to_dict())
            return None

    def reorder_pending(self, new_order: list[str]) -> bool:
        """Atomically adopt a new problem order (continuous rerank support).

        Fail-closed: the new order must be a permutation of the EXACT existing
        problem set — nothing may be added or dropped by a reorder.  Order only
        affects which available problem ``lease`` picks next; leased and
        completed problems are untouched (lease skips them regardless of
        position).  The rewritten state is re-signed like every other write.
        """
        with self._locked():
            state = self._read()
            if state is None:
                raise CampaignError("campaign is not initialized")
            if sorted(new_order) != sorted(state["order"]) \
                    or len(set(new_order)) != len(new_order):
                raise CampaignError(
                    "reorder must be a permutation of the existing problem set")
            if list(new_order) == list(state["order"]):
                return False
            self._write(self._encode(
                state["campaign_id"], list(new_order), self._decode(state),
                int(state["fencing_counter"]), state.get("machines")))
            return True

    def _update(self, problem_id: str, worker_id: str, fencing_token: int,
                mutate: Callable[[Assignment], None]) -> bool:
        with self._locked():
            state = self._read()
            if state is None:
                raise CampaignError("campaign is not initialized")
            assignments = self._decode(state)
            a = assignments.get(problem_id)
            if a is None:
                raise CampaignError(f"unknown problem id: {problem_id!r}")
            # Fencing guard: only the current lease holder may transition the problem.
            if a.status != "leased" or a.worker_id != worker_id or a.fencing_token != fencing_token:
                return False
            mutate(a)
            self._write(self._encode(state["campaign_id"], state["order"], assignments,
                                     int(state["fencing_counter"]),
                                     state.get("machines")))
            return True

    def complete(self, problem_id: str, worker_id: str, fencing_token: int, *,
                 result_state: str) -> bool:
        def _m(a: Assignment) -> None:
            a.status = "done"
            a.result_state = result_state
            a.lease_expires_at = 0.0
        return self._update(problem_id, worker_id, fencing_token, _m)

    def retain(self, problem_id: str, worker_id: str, fencing_token: int, *,
               reason: str = "provider_unavailable") -> bool:
        """Return a problem to the queue after an INFRASTRUCTURE interruption.

        A throttle, dropped connection, or closed browser tab is never a
        mathematical dead end: the interrupted attempt is refunded so the
        problem keeps its full mathematical budget. Each retain spends the
        separate (much larger) infrastructure budget instead — exhausting THAT
        marks the problem failed honestly, so a permanently broken environment
        cannot cycle forever.
        """
        def _m(a: Assignment) -> None:
            a.infra_retries += 1
            a.lease_expires_at = 0.0
            a.attempts = max(0, a.attempts - 1)  # a retained problem is not a spent attempt
            if a.infra_retries >= self.max_infra_retries:
                a.status = "failed"
                a.result_state = f"infrastructure_budget_exhausted: {reason}"
            else:
                a.status = "retained"
                a.result_state = reason
        return self._update(problem_id, worker_id, fencing_token, _m)

    def fail(self, problem_id: str, worker_id: str, fencing_token: int, *,
             reason: str, permanent: bool = False) -> bool:
        def _m(a: Assignment) -> None:
            a.status = (
                "failed" if permanent or a.attempts >= self.max_attempts else "retained"
            )
            a.result_state = reason
            a.lease_expires_at = 0.0
        return self._update(problem_id, worker_id, fencing_token, _m)

    def heartbeat(self, problem_id: str, worker_id: str, fencing_token: int, *,
                  now: float) -> bool:
        """Extend a held lease (fencing-guarded). A stale token cannot heartbeat."""
        def _m(a: Assignment) -> None:
            a.lease_expires_at = now + self.lease_seconds
        return self._update(problem_id, worker_id, fencing_token, _m)

    def requeue_failed(self, *, infra_only: bool = False) -> list[str]:
        """Reset FAILED problems back to pending for a fresh set of attempts.

        Infrastructure failures — a provider throttle, a dropped DB connection,
        a closed browser tab — can exhaust a problem's attempt budget with no
        genuine mathematical dead end. Requeuing clears those problems' attempt
        counts so they get a fair run. Only ``failed`` problems are touched;
        pending/leased/retained/done are left exactly as they are, so a live
        campaign's in-flight work is never disturbed. Atomic under the same
        (cross-process) lock the campaign uses, so it is safe to call against a
        running campaign — the next lease picks the requeued problems up.

        ``infra_only`` restricts the reset to problems whose failure was an
        exhausted INFRASTRUCTURE budget (the provider was unavailable), so an
        automatic startup requeue can never loop a genuinely crashing problem.
        """
        with self._locked():
            state = self._read()
            if state is None:
                return []
            assignments = self._decode(state)
            requeued: list[str] = []
            for pid, a in assignments.items():
                if a.status != "failed":
                    continue
                if infra_only and not str(a.result_state).startswith(
                        "infrastructure_budget_exhausted"):
                    continue
                a.status = "pending"
                a.attempts = 0
                a.infra_retries = 0
                a.worker_id = ""
                a.fencing_token = 0
                a.lease_expires_at = 0.0
                a.result_state = ""
                requeued.append(pid)
            if requeued:
                self._write(self._encode(
                    state["campaign_id"], state["order"], assignments,
                    int(state["fencing_counter"]), state.get("machines")))
            return requeued

    def requeue_promising(self, problem_ids: list[str], *,
                          max_resamples: int = 2) -> list[str]:
        """Requeue COMPLETED problems that showed progress for another sample.

        The adaptive-effort principle: total effort should follow evidence of
        tractability, not a fixed constant. The CALLER decides which outcomes
        count as progress (from the outcome ledger — e.g. PARTIAL_PROGRESS,
        COMPUTATIONAL_EVIDENCE, CANDIDATE_*, or salvaged supported claims);
        this method only performs the bounded state transition: done → pending
        with fresh budgets, at most ``max_resamples`` times per problem, so a
        problem can never be resampled forever on weak signals. The exchange
        cache's attempt-salt makes each resample an INDEPENDENT draw, and the
        problem's dossier carries everything already learned.
        """
        wanted = set(problem_ids)
        with self._locked():
            state = self._read()
            if state is None:
                return []
            assignments = self._decode(state)
            requeued: list[str] = []
            for pid, a in assignments.items():
                if pid not in wanted or a.status != "done":
                    continue
                if a.resamples >= max_resamples:
                    continue
                a.status = "pending"
                a.attempts = 0
                a.infra_retries = 0
                a.resamples += 1
                a.worker_id = ""
                a.fencing_token = 0
                a.lease_expires_at = 0.0
                a.result_state = ""
                requeued.append(pid)
            if requeued:
                self._write(self._encode(
                    state["campaign_id"], state["order"], assignments,
                    int(state["fencing_counter"]), state.get("machines")))
            return requeued

    # ── status ───────────────────────────────────────────────────────────────
    def status(self) -> dict[str, Any]:
        state = self._read()
        if state is None:
            return {"initialized": False}
        assignments = self._decode(state)
        by_status: dict[str, int] = {}
        for a in assignments.values():
            by_status[a.status] = by_status.get(a.status, 0) + 1
        return {
            "initialized": True,
            "campaign_id": state["campaign_id"],
            "total": len(assignments),
            "by_status": by_status,
            "complete": all(a.status in _TERMINAL for a in assignments.values()),
            "workers": {
                pid: {"worker_id": a.worker_id, "status": a.status,
                      "attempts": a.attempts, "infra_retries": a.infra_retries,
                      "result_state": a.result_state}
                for pid, a in assignments.items()
            },
            "machines": dict(state.get("machines") or {}),
        }

    def pending_count(self) -> int:
        state = self._read()
        if state is None:
            return 0
        return sum(1 for a in self._decode(state).values() if a.status not in _TERMINAL)

    # ── convenience driver ─────────────────────────────────────────────────────
    def drain(
        self,
        runner: Callable[[str, int], str],
        *,
        now: Callable[[], float],
        provider_unavailable: type[BaseException] = _NoConfiguredProviderOutage,
        max_rounds: int = 10_000,
    ) -> dict[str, Any]:
        """Drive the campaign to completion with a single logical worker slot.

        ``runner(problem_id, fencing_token) -> result_state``. Raising
        ``provider_unavailable`` retains the problem; any other exception is a
        recoverable failure (retained until max attempts). Real multi-worker
        concurrency is a thin wrapper that calls ``lease``/``complete`` per thread.
        """
        worker = self.worker_ids[0]
        rounds = 0
        while self.pending_count() > 0 and rounds < max_rounds:
            rounds += 1
            assignment = self.lease(worker, now=now())
            if assignment is None:
                break
            try:
                result_state = runner(assignment.problem_id, assignment.fencing_token)
            except provider_unavailable:
                self.retain(assignment.problem_id, worker, assignment.fencing_token)
                continue
            except Exception as exc:  # noqa: BLE001 - recoverable per-problem failure
                self.fail(assignment.problem_id, worker, assignment.fencing_token,
                          reason=f"{type(exc).__name__}: {exc}")
                continue
            self.complete(assignment.problem_id, worker, assignment.fencing_token,
                          result_state=result_state)
        return self.status()

    # ── real concurrent driver ──────────────────────────────────────────────
    def run_concurrent(
        self,
        runner: Callable[[str, int, str], str],
        *,
        max_workers: int,
        now: Callable[[], float],
        provider_unavailable: type[BaseException] = _NoConfiguredProviderOutage,
        permanent_failure: type[BaseException] = _NoConfiguredPermanentFailure,
        poll_interval: float = 0.01,
        heartbeat_interval: float | None = None,
        stop_requested: Callable[[], bool] | None = None,
        outage_backoff: Callable[[int], float] | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> dict[str, Any]:
        """Drive the campaign with genuine bounded concurrency across worker threads.

        ``runner(problem_id, fencing_token, worker_id) -> result_state`` runs in
        parallel across ``min(max_workers, len(worker_ids))`` threads. Leases are
        atomic (fencing + lock), so no problem is assigned twice or skipped; the
        returned status includes a ``concurrency`` report with the observed
        maximum simultaneity and per-worker activity.
        """
        slots = list(self.worker_ids)[: max(1, min(int(max_workers), len(self.worker_ids)))]
        state_lock = threading.Lock()
        active = {"n": 0}
        timeline: list[tuple[str, str, float, float]] = []
        should_stop = stop_requested or (lambda: False)
        # Provider outages are usually GLOBAL (one throttled account, one dead
        # browser).  Without a shared backoff, one worker cycles the entire
        # pending queue in minutes, charging every problem an infrastructure
        # retry per pass — an overnight outage then marks the whole campaign
        # failed without a single mathematical attempt.  Consecutive outages
        # now pause the leasing worker (bounded exponential), and any
        # completed run resets the counter.
        backoff = outage_backoff or (
            lambda consecutive: min(30.0 * (2 ** max(0, consecutive - 1)), 600.0))
        outages = {"consecutive": 0}

        def _outage_pause() -> None:
            with state_lock:
                outages["consecutive"] += 1
                pause = max(0.0, float(backoff(outages["consecutive"])))
            remaining_pause = pause
            while remaining_pause > 0 and not should_stop():
                step = min(5.0, remaining_pause)
                sleep(step)
                remaining_pause -= step

        def worker_loop(worker_id: str) -> None:
            while True:
                if should_stop():
                    return
                assignment = self.lease(worker_id, now=now())
                if assignment is None:
                    with state_lock:
                        busy = active["n"] > 0
                    if busy and self.pending_count() > 0:
                        time.sleep(poll_interval)
                        continue
                    return
                with state_lock:
                    active["n"] += 1
                started = time.monotonic()
                # Keep the assignment lease alive WHILE the (long) runner works:
                # a browser problem takes far longer than lease_seconds, so
                # without renewal its lease would expire, another worker would
                # re-lease it (burning an attempt), and after max_attempts it
                # would be marked failed despite genuine progress. The heartbeat
                # is fencing-guarded, so a superseded worker's renewal no-ops.
                stop_heartbeat = threading.Event()
                interval = (
                    heartbeat_interval if heartbeat_interval is not None
                    else max(5.0, self.lease_seconds / 3.0))

                def _heartbeat(pid=assignment.problem_id,
                               token=assignment.fencing_token) -> None:
                    while not stop_heartbeat.wait(interval):
                        try:
                            if not self.heartbeat(pid, worker_id, token, now=now()):
                                return  # lost the lease (superseded) — stop renewing
                        except Exception:  # noqa: BLE001 - renewal is best-effort
                            return
                heart = threading.Thread(
                    target=_heartbeat, name=f"egmra-hb-{worker_id}", daemon=True)
                heart.start()
                try:
                    result_state = runner(assignment.problem_id, assignment.fencing_token,
                                          worker_id)
                except provider_unavailable:
                    self.retain(assignment.problem_id, worker_id, assignment.fencing_token)
                    _outage_pause()
                except permanent_failure as exc:
                    self.fail(
                        assignment.problem_id, worker_id, assignment.fencing_token,
                        reason=f"{type(exc).__name__}: {exc}", permanent=True,
                    )
                except Exception as exc:  # noqa: BLE001 - recoverable per-problem failure
                    self.fail(assignment.problem_id, worker_id, assignment.fencing_token,
                              reason=f"{type(exc).__name__}: {exc}")
                    with state_lock:
                        outages["consecutive"] = 0
                else:
                    self.complete(assignment.problem_id, worker_id, assignment.fencing_token,
                                  result_state=result_state)
                    with state_lock:
                        outages["consecutive"] = 0
                finally:
                    stop_heartbeat.set()
                    heart.join(timeout=1.0)
                    with state_lock:
                        active["n"] -= 1
                        timeline.append((worker_id, assignment.problem_id, started,
                                         time.monotonic()))

        threads = [threading.Thread(target=worker_loop, args=(w,), name=f"egmra-{w}")
                   for w in slots]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        status = self.status()
        status["concurrency"] = _concurrency_report(timeline)
        status["stop_requested"] = bool(should_stop())
        return status


def _concurrency_report(timeline: list[tuple[str, str, float, float]]) -> dict[str, Any]:
    """Compute observed max simultaneity + per-worker activity from run intervals."""
    events: list[tuple[float, int]] = []
    for _worker, _problem, start, end in timeline:
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda e: (e[0], e[1]))  # close (-1) before open (+1) on ties
    current = peak = 0
    for _t, delta in events:
        current += delta
        peak = max(peak, current)
    activity: dict[str, int] = {}
    for worker, _problem, _s, _e in timeline:
        activity[worker] = activity.get(worker, 0) + 1
    return {
        "max_observed_concurrency": peak,
        "distinct_workers": len(activity),
        "worker_activity": activity,
        "total_runs": len(timeline),
    }
