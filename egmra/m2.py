"""M2 scalable MVP layer (spec §13.4, §14.1).

M1's capabilities (leases, containerized-sandbox interface, SAT/SMT/CAS adapters,
OEIS caching, proof-state caching, verified-only expert iteration, SCC revocation)
already exist in their planes. M2 adds the *scale interfaces* with local backends:
a Postgres-shaped event store contract satisfied by the JSONL store, object
storage, and an assembly that wires them. Real Postgres/OCI require servers and are
documented (see DECISIONS.md D-004/D-005).
"""

from __future__ import annotations

import json
import os
import stat
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable
from urllib.parse import urlsplit, urlunsplit

from egmra.compute.sandbox import ContainerSandbox
from egmra.provenance.hashing import canonical_json, content_id, is_sha256, sha256_bytes
from egmra.truth.events import (
    ACTIONS,
    Event,
    EventLog,
    EventLogError,
    _GENESIS,
    _now,
    _resolve_key,
    merkle_root,
    seal_event,
)


@runtime_checkable
class EventStore(Protocol):
    """The append-only event-store contract (JSONL now, Postgres at scale)."""

    def append(self, **kwargs: Any) -> Any: ...
    def verify_integrity(self, **kwargs: Any) -> bool: ...
    def merkle_root(self) -> str: ...


class PostgresEventStore:
    """Production Postgres event store (spec §13.4, §14.1).

    Requires a Postgres server. This class validates configuration and documents
    the exact DDL/connection; it does not fake a database. Use the JSONL
    :class:`~egmra.truth.events.EventLog` for M1/CI (same append-only contract).
    """

    schema_ddl = (
        "CREATE TABLE IF NOT EXISTS events ("
        " event_id TEXT PRIMARY KEY, sequence BIGINT NOT NULL,"
        " prev_event_id TEXT NOT NULL, run_id TEXT NOT NULL, payload JSONB NOT NULL,"
        " signature TEXT NOT NULL, UNIQUE (run_id, sequence));"
    )

    def __init__(self, dsn: str, *, run_id: str = "run", env: dict[str, str] | None = None):
        if not isinstance(dsn, str):
            raise ValueError("Postgres DSN must be a string")
        parsed = urlsplit(dsn)
        if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname \
                or not parsed.path or parsed.path == "/":
            raise ValueError("Postgres DSN must identify a postgres host and database")
        self._dsn = dsn
        self.run_id = run_id
        self._key = _resolve_key(env)
        host = parsed.hostname
        if parsed.port:
            host = f"{host}:{parsed.port}"
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
            return connection
        except Exception as exc:
            raise RuntimeError(
                f"Postgres connection/schema initialization failed for {self.dsn}"
            ) from exc

    def _business_record(self, *, sequence: int, prev_event_id: str, action: str,
                         actor: dict, object_ids: list, timestamp: str | None,
                         prior_versions, new_versions, input_hashes, output_hashes,
                         run_contract_hash, budget_delta, reason_code,
                         human_readable_reason, payload) -> dict[str, Any]:
        """Build the exact same business record layout as the JSONL EventLog."""
        if action not in ACTIONS:
            raise EventLogError(f"unknown event action: {action}")
        return {
            "sequence": sequence,
            "run_id": self.run_id,
            "timestamp": timestamp or _now(),
            "actor": actor,
            "action": action,
            "object_ids": list(object_ids),
            "prev_event_id": prev_event_id,
            "prior_versions": dict(prior_versions or {}),
            "new_versions": dict(new_versions or {}),
            "input_hashes": list(input_hashes or []),
            "output_hashes": list(output_hashes or []),
            "run_contract_hash": run_contract_hash,
            "budget_delta": dict(budget_delta or {}),
            "reason_code": reason_code,
            "human_readable_reason": human_readable_reason,
            "payload": json.loads(canonical_json(payload or {})),
        }

    def append(  # pragma: no cover - requires a database server
        self, *, action: str, actor: dict[str, Any], object_ids: list[str],
        reason_code: str = "", human_readable_reason: str = "",
        prior_versions: dict[str, int] | None = None,
        new_versions: dict[str, int] | None = None,
        input_hashes: list[str] | None = None, output_hashes: list[str] | None = None,
        run_contract_hash: str = "", budget_delta: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None, timestamp: str | None = None,
    ) -> Event:
        """Append a signed, hash-chained event using the shared sealing logic."""
        connection = self.connect()
        try:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT sequence, event_id FROM events WHERE run_id = %s "
                        "ORDER BY sequence DESC LIMIT 1 FOR UPDATE", (self.run_id,))
                    row = cursor.fetchone()
                    sequence = 0 if row is None else int(row[0]) + 1
                    prev_event_id = _GENESIS if row is None else str(row[1])
                    business = self._business_record(
                        sequence=sequence, prev_event_id=prev_event_id, action=action,
                        actor=actor, object_ids=object_ids, timestamp=timestamp,
                        prior_versions=prior_versions, new_versions=new_versions,
                        input_hashes=input_hashes, output_hashes=output_hashes,
                        run_contract_hash=run_contract_hash, budget_delta=budget_delta,
                        reason_code=reason_code, human_readable_reason=human_readable_reason,
                        payload=payload)
                    event = seal_event(self._key, business)
                    cursor.execute(
                        "INSERT INTO events (event_id, sequence, prev_event_id, run_id, "
                        "payload, signature) VALUES (%s, %s, %s, %s, %s, %s)",
                        (event.event_id, event.sequence, event.prev_event_id, self.run_id,
                         canonical_json(event.to_dict()), event.signature))
            return event
        finally:
            connection.close()

    def _load_events(self, connection) -> list[Event]:  # pragma: no cover - needs a server
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT payload FROM events WHERE run_id = %s ORDER BY sequence ASC",
                (self.run_id,))
            rows = cursor.fetchall()
        events: list[Event] = []
        for (payload,) in rows:
            doc = json.loads(payload) if isinstance(payload, (str, bytes)) else payload
            events.append(Event(
                event_id=doc["event_id"], sequence=doc["sequence"], run_id=doc["run_id"],
                timestamp=doc["timestamp"], actor=doc["actor"], action=doc["action"],
                object_ids=doc["object_ids"], prev_event_id=doc["prev_event_id"],
                prior_versions=doc.get("prior_versions", {}),
                new_versions=doc.get("new_versions", {}),
                input_hashes=doc.get("input_hashes", []),
                output_hashes=doc.get("output_hashes", []),
                run_contract_hash=doc.get("run_contract_hash", ""),
                budget_delta=doc.get("budget_delta", {}),
                reason_code=doc.get("reason_code", ""),
                human_readable_reason=doc.get("human_readable_reason", ""),
                payload=doc.get("payload", {}), signature=doc.get("signature", "")))
        return events

    def verify_integrity(self, **kwargs: Any) -> bool:  # pragma: no cover - needs a server
        """Verify sequence numbering, hash chaining, ids, and signatures."""
        import hmac as _hmac

        connection = self.connect()
        try:
            events = self._load_events(connection)
        finally:
            connection.close()
        prev = _GENESIS
        seen: set[str] = set()
        for i, event in enumerate(events):
            if event.sequence != i or event.run_id != self.run_id:
                return False
            if event.action not in ACTIONS or event.prev_event_id != prev:
                return False
            if event.event_id in seen or content_id(event.business_record()) != event.event_id:
                return False
            expected = _hmac.new(self._key, event.event_id.encode("utf-8"), "sha256").hexdigest()
            if not _hmac.compare_digest(expected, event.signature):
                return False
            seen.add(event.event_id)
            prev = event.event_id
        return True

    def merkle_root(self) -> str:  # pragma: no cover - needs a server
        connection = self.connect()
        try:
            events = self._load_events(connection)
        finally:
            connection.close()
        return merkle_root([e.event_id for e in events])


@dataclass
class ContentAddressedObjectStore:
    """Local content-addressed artifact store (object storage at scale)."""

    root: Path
    max_object_bytes: int = 64 * 1024 * 1024
    _root_identity: tuple[int, int] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if type(self.max_object_bytes) is not int or self.max_object_bytes <= 0:
            raise ValueError("max_object_bytes must be a positive integer")
        root = Path(self.root)
        if root.exists() and (root.is_symlink() or not root.is_dir()):
            raise ValueError("object-store root must be a regular directory, not a symlink")
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(root, 0o700)
        resolved = root.resolve(strict=True)
        info = resolved.stat()
        self.root = resolved
        self._root_identity = (info.st_dev, info.st_ino)

    def put(self, data: bytes) -> str:
        if not isinstance(data, bytes):
            raise TypeError("object-store data must be bytes")
        if len(data) > self.max_object_bytes:
            raise ValueError("object is too large")
        self._check_root()
        digest = sha256_bytes(data)
        path = self._object_path(digest)
        path.parent.mkdir(parents=False, exist_ok=True, mode=0o700)
        if path.parent.is_symlink() or path.parent.resolve(strict=True).parent != self.root:
            raise ValueError("object-store prefix directory is unsafe")
        os.chmod(path.parent, 0o700)
        if path.exists() or path.is_symlink():
            existing = self.get(digest)
            if existing != data:  # defensive; get already verifies the content hash
                raise ValueError("existing object failed integrity verification")
            return digest
        fd, temporary = tempfile.mkstemp(prefix=".staging-", dir=path.parent)
        temporary_path = Path(temporary)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "wb", closefd=True) as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary_path, path)
            except FileExistsError:
                if self.get(digest) != data:
                    raise ValueError("concurrent object publication failed integrity verification")
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
        return digest

    def get(self, digest: str) -> bytes:
        self._check_root()
        path = self._object_path(digest)
        if path.parent.is_symlink() or not path.parent.is_dir() \
                or path.parent.resolve(strict=True).parent != self.root:
            raise ValueError("object-store prefix directory is unsafe")
        try:
            info = path.lstat()
        except FileNotFoundError:
            raise
        if not stat.S_ISREG(info.st_mode) or path.is_symlink():
            raise ValueError("object must be a regular non-symlink file")
        if info.st_size > self.max_object_bytes:
            raise ValueError("stored object is too large")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        try:
            with os.fdopen(fd, "rb", closefd=True) as handle:
                data = handle.read(self.max_object_bytes + 1)
        finally:
            # fdopen owns the descriptor; this branch is only for failures before it does.
            pass
        if len(data) > self.max_object_bytes or sha256_bytes(data) != digest:
            raise ValueError("object integrity check failed")
        return data

    def exists(self, digest: str) -> bool:
        self._check_root()
        path = self._object_path(digest)
        if not path.exists() and not path.is_symlink():
            return False
        self.get(digest)
        return True

    def _object_path(self, digest: str) -> Path:
        if not is_sha256(digest):
            raise ValueError("object identity must be a lowercase SHA-256 digest")
        return self.root / digest[:2] / digest

    def _check_root(self) -> None:
        try:
            info = self.root.lstat()
        except FileNotFoundError as exc:
            raise ValueError("object-store root changed or disappeared") from exc
        if self.root.is_symlink() or not stat.S_ISDIR(info.st_mode) \
                or (info.st_dev, info.st_ino) != self._root_identity:
            raise ValueError("object-store root changed after initialization")


@dataclass
class M2Assembly:
    """Wires the scale layer with local backends (production swaps the backends)."""

    event_log: EventLog
    object_store: ContentAddressedObjectStore
    sandbox: ContainerSandbox | None = None
    concurrent_programs: int = 3
    reserved_verifier_workers: int = 1

    def __post_init__(self) -> None:
        if type(self.concurrent_programs) is not int or self.concurrent_programs <= 0:
            raise ValueError("concurrent_programs must be a positive integer")
        if type(self.reserved_verifier_workers) is not int \
                or not 0 < self.reserved_verifier_workers <= self.concurrent_programs:
            raise ValueError("reserved verifier workers must fit within total capacity")
        if self.sandbox is not None and not isinstance(self.sandbox, ContainerSandbox):
            raise ValueError("M2 assembly accepts only an OCI ContainerSandbox")

    def event_store_is_valid(self) -> bool:
        return isinstance(self.event_log, EventStore)

    def container_backend(self, image: str) -> ContainerSandbox:
        return ContainerSandbox(image)

    def m2_ready(self) -> bool:
        """Full M2 is not ready with the local JSONL substitute or no OCI backend."""
        return isinstance(self.event_log, PostgresEventStore) \
            and isinstance(self.sandbox, ContainerSandbox)

    def topology_hash(self) -> str:
        return content_id({
            "concurrent_programs": self.concurrent_programs,
            "reserved_verifier_workers": self.reserved_verifier_workers,
            "sandbox": getattr(self.sandbox, "policy", "unconfigured"),
            "event_store": type(self.event_log).__name__,
            "object_store_root": str(self.object_store.root),
        })
