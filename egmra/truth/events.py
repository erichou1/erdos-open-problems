"""Append-only, signed, hash-chained event log (spec §10.3, §10.4).

The event log and the artifact store are the authoritative record; every derived
view (materialized graph, ``manifest.json``) is a disposable projection. Each
event is content-addressed, HMAC-signed, and chained to its predecessor so any
insertion, deletion, or reordering is detectable, and a Merkle root commits to
the exact ordered sequence.
"""

from __future__ import annotations

import hmac
import json
import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import fcntl

from egmra.provenance.hashing import canonical_json, content_id, merkle_root, sha256_hex

_GENESIS = sha256_hex("egmra-genesis")
_MIN_KEY_BYTES = 32

# Canonical action vocabulary (extensible; unknown actions are rejected).
ACTIONS = frozenset(
    {
        "PROBLEM_FROZEN",
        "INTERPRETATION_ADDED",
        "INTENT_CERTIFICATE_ISSUED",
        "FORMAL_CORRESPONDENCE_ISSUED",
        "CLAIM_PROPOSED",
        "CLAIM_INTENT_BOUND",
        "EVIDENCE_ATTACHED",
        "EVIDENCE_INVALIDATED",
        "CLAIM_PROMOTED",
        "CLAIM_REVOKED",
        "CLAIM_REFUTED",
        "CLAIM_CONFLICTED",
        "CLAIM_SUPERSEDED",
        "RELATION_ADDED",
        "BRANCH_OPENED",
        "BRANCH_PAUSED",
        "BRANCH_REOPENED",
        "BRANCH_KILLED",
        "BRANCH_CLOSED",
        "GATE_DECIDED",
        "ADJUDICATION_RECORDED",
        "PROMOTION_RECORDED",
        "CHECKPOINT_TAKEN",
        "HUMAN_INTERVENTION",
        "RATE_LIMIT_PAUSE",
    }
)


class EventLogError(RuntimeError):
    """Raised when the event log is malformed or its chain is broken."""


@dataclass(frozen=True)
class Event:
    event_id: str
    sequence: int
    run_id: str
    timestamp: str
    actor: dict[str, Any]
    action: str
    object_ids: list[str]
    prev_event_id: str
    prior_versions: dict[str, int] = field(default_factory=dict)
    new_versions: dict[str, int] = field(default_factory=dict)
    input_hashes: list[str] = field(default_factory=list)
    output_hashes: list[str] = field(default_factory=list)
    run_contract_hash: str = ""
    budget_delta: dict[str, Any] = field(default_factory=dict)
    reason_code: str = ""
    human_readable_reason: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    signature: str = ""

    def business_record(self) -> dict[str, Any]:
        """The signed/hashed portion (everything except the signature)."""
        return {
            "sequence": self.sequence,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action,
            "object_ids": list(self.object_ids),
            "prev_event_id": self.prev_event_id,
            "prior_versions": dict(self.prior_versions),
            "new_versions": dict(self.new_versions),
            "input_hashes": list(self.input_hashes),
            "output_hashes": list(self.output_hashes),
            "run_contract_hash": self.run_contract_hash,
            "budget_delta": dict(self.budget_delta),
            "reason_code": self.reason_code,
            "human_readable_reason": self.human_readable_reason,
            "payload": self.payload,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"event_id": self.event_id, **self.business_record(), "signature": self.signature}


def _resolve_key(env: dict[str, str] | None = None) -> bytes:
    env = env if env is not None else dict(os.environ)
    raw = env.get("EGMRA_EVENT_KEY", "").strip()
    if not raw:
        raise EventLogError("EGMRA_EVENT_KEY is required for an authoritative event log")
    key = raw.encode("utf-8")
    if len(key) < _MIN_KEY_BYTES:
        raise EventLogError(f"EGMRA_EVENT_KEY must contain at least {_MIN_KEY_BYTES} bytes")
    return key


def seal_event(key: bytes, business: dict[str, Any]) -> Event:
    """Content-address and HMAC-sign a business record into an :class:`Event`.

    Shared by every event store (JSONL now, Postgres at scale) so an event's id
    and signature are computed identically regardless of backend — the basis for
    cross-backend replay parity.
    """
    event_id = content_id(business)
    signature = hmac.new(key, event_id.encode("utf-8"), "sha256").hexdigest()
    return Event(event_id=event_id, signature=signature, **business)


class EventLog:
    """An append-only JSONL event log with hash chaining and signatures."""

    def __init__(self, path: str | Path, *, run_id: str = "run", env: dict[str, str] | None = None):
        self.path = Path(path)
        self.run_id = run_id
        self._key = _resolve_key(env)
        self._head_path = self.path.with_name(self.path.name + ".head")
        self._lock_path = self.path.with_name(self.path.name + ".lock")
        self._events: list[Event] = []
        if self.path.exists():
            with self._lock_path.open("a+b") as lock_handle:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_SH)
                try:
                    self._load()
                finally:
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    # ── read ───────────────────────────────────────────────────────────────────

    def _load(self) -> None:
        events: list[Event] = []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise EventLogError(f"cannot read event log: {exc}") from exc
        if not lines:
            raise EventLogError("existing event log is empty and has no valid committed history")
        for line_number, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                raise EventLogError(f"blank record at event-log line {line_number}")
            try:
                doc = json.loads(line, object_pairs_hook=_reject_duplicate_keys)
                event = Event(
                    event_id=doc["event_id"],
                    sequence=doc["sequence"],
                    run_id=doc["run_id"],
                    timestamp=doc["timestamp"],
                    actor=doc["actor"],
                    action=doc["action"],
                    object_ids=doc["object_ids"],
                    prev_event_id=doc["prev_event_id"],
                    prior_versions=doc.get("prior_versions", {}),
                    new_versions=doc.get("new_versions", {}),
                    input_hashes=doc.get("input_hashes", []),
                    output_hashes=doc.get("output_hashes", []),
                    run_contract_hash=doc.get("run_contract_hash", ""),
                    budget_delta=doc.get("budget_delta", {}),
                    reason_code=doc.get("reason_code", ""),
                    human_readable_reason=doc.get("human_readable_reason", ""),
                    payload=doc.get("payload", {}),
                    signature=doc.get("signature", ""),
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                raise EventLogError(f"malformed event at line {line_number}: {exc}") from exc
            events.append(event)
        if not self._verify_events(events):
            raise EventLogError("event sequence, hash chain, or signature is invalid")
        self._verify_head(events)
        self._events = events

    @property
    def events(self) -> list[Event]:
        return list(self._events)

    def __len__(self) -> int:
        return len(self._events)

    def last_event_id(self) -> str:
        return self._events[-1].event_id if self._events else _GENESIS

    def merkle_root(self) -> str:
        return merkle_root([e.event_id for e in self._events])

    def by_action(self, action: str) -> list[Event]:
        return [e for e in self._events if e.action == action]

    def actions_in_order(self) -> list[str]:
        return [e.action for e in self._events]

    # ── write ──────────────────────────────────────────────────────────────────

    def append(
        self,
        *,
        action: str,
        actor: dict[str, Any],
        object_ids: list[str],
        reason_code: str = "",
        human_readable_reason: str = "",
        prior_versions: dict[str, int] | None = None,
        new_versions: dict[str, int] | None = None,
        input_hashes: list[str] | None = None,
        output_hashes: list[str] | None = None,
        run_contract_hash: str = "",
        budget_delta: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        timestamp: str | None = None,
    ) -> Event:
        if action not in ACTIONS:
            raise EventLogError(f"unknown event action: {action}")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock_path.open("a+b") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            try:
                if self.path.exists():
                    self._load()
                else:
                    if self._head_path.exists():
                        raise EventLogError("event log is missing but its committed head remains")
                    self._events = []
                sequence = len(self._events)
                prev = self.last_event_id()
                prior_versions_doc = dict(prior_versions or {})
                new_versions_doc = dict(new_versions or {})
                self._validate_optimistic_versions(
                    prior_versions_doc, new_versions_doc, self._events
                )
                business = {
                    "sequence": sequence,
                    "run_id": self.run_id,
                    "timestamp": timestamp or _now(),
                    "actor": actor,
                    "action": action,
                    "object_ids": list(object_ids),
                    "prev_event_id": prev,
                    "prior_versions": prior_versions_doc,
                    "new_versions": new_versions_doc,
                    "input_hashes": list(input_hashes or []),
                    "output_hashes": list(output_hashes or []),
                    "run_contract_hash": run_contract_hash,
                    "budget_delta": dict(budget_delta or {}),
                    "reason_code": reason_code,
                    "human_readable_reason": human_readable_reason,
                    "payload": json.loads(canonical_json(payload or {})),
                }
                event = seal_event(self._key, business)
                serialized = json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n"
                with self.path.open("a", encoding="utf-8") as handle:
                    handle.write(serialized)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.chmod(self.path, 0o600)
                self._events.append(event)
                self._write_head(self._events)
                return event
            finally:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)

    # ── integrity ────────────────────────────────────────────────────────────────

    def verify_integrity(self, *, env: dict[str, str] | None = None) -> bool:
        """Verify sequence numbering, hash chaining, ids, and signatures."""
        key = _resolve_key(env) if env is not None else self._key
        prior_key = self._key
        self._key = key
        try:
            if not self.path.exists():
                return not self._events and not self._head_path.exists()
            with self._lock_path.open("a+b") as lock_handle:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_SH)
                try:
                    self._load()
                finally:
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            return True
        except EventLogError:
            return False
        finally:
            self._key = prior_key

    def _verify_events(self, events: list[Event]) -> bool:
        prev = _GENESIS
        seen_ids: set[str] = set()
        for i, event in enumerate(events):
            if event.sequence != i:
                return False
            if event.run_id != self.run_id:
                return False
            if event.action not in ACTIONS:
                return False
            if event.prev_event_id != prev:
                return False
            if event.event_id in seen_ids:
                return False
            if content_id(event.business_record()) != event.event_id:
                return False
            expected_sig = hmac.new(self._key, event.event_id.encode("utf-8"), "sha256").hexdigest()
            if not hmac.compare_digest(expected_sig, event.signature):
                return False
            seen_ids.add(event.event_id)
            prev = event.event_id
        return True

    def _head_record(self, events: list[Event]) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "count": len(events),
            "last_event_id": events[-1].event_id if events else _GENESIS,
            "merkle_root": merkle_root([event.event_id for event in events]),
        }

    @staticmethod
    def _validate_optimistic_versions(
        prior_versions: dict[str, int], new_versions: dict[str, int], events: list[Event]
    ) -> None:
        current: dict[str, int] = {}
        for event in events:
            current.update(event.new_versions)
        for object_id, prior in prior_versions.items():
            if not isinstance(prior, int) or current.get(object_id) != prior:
                raise EventLogError(
                    f"stale optimistic version for {object_id!r}: "
                    f"expected {current.get(object_id)!r}, got {prior!r}"
                )
        for object_id, new in new_versions.items():
            if not isinstance(new, int) or new < 1:
                raise EventLogError(f"invalid new version for {object_id!r}: {new!r}")
            if object_id in prior_versions:
                if new != prior_versions[object_id] + 1:
                    raise EventLogError(
                        f"non-sequential version for {object_id!r}: "
                        f"{prior_versions[object_id]!r} -> {new!r}"
                    )
            elif object_id in current:
                raise EventLogError(
                    f"versioned object {object_id!r} already exists at {current[object_id]}"
                )

    def _write_head(self, events: list[Event]) -> None:
        record = self._head_record(events)
        signature = hmac.new(
            self._key, canonical_json(record).encode("utf-8"), "sha256"
        ).hexdigest()
        document = {**record, "signature": signature}
        fd, temp_name = tempfile.mkstemp(prefix=self._head_path.name + ".", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(json.dumps(document, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temp_name, 0o600)
            os.replace(temp_name, self._head_path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def _verify_head(self, events: list[Event]) -> None:
        if not self._head_path.exists():
            raise EventLogError("committed event-log head is missing")
        try:
            doc = json.loads(
                self._head_path.read_text(encoding="utf-8"),
                object_pairs_hook=_reject_duplicate_keys,
            )
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise EventLogError(f"invalid event-log head: {exc}") from exc
        signature = doc.pop("signature", "")
        expected_record = self._head_record(events)
        expected_signature = hmac.new(
            self._key, canonical_json(expected_record).encode("utf-8"), "sha256"
        ).hexdigest()
        if doc != expected_record or not hmac.compare_digest(expected_signature, signature):
            raise EventLogError("event log does not match its committed head (possible truncation)")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise EventLogError(f"duplicate JSON key {key!r}")
        out[key] = value
    return out
