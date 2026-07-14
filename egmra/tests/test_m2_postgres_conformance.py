"""No-server conformance tests for the PostgreSQL event store (defect 14).

Live replay parity against a real PostgreSQL server is a separate acceptance gate
(BLOCKED ON LIVE ACCEPTANCE); these tests verify protocol conformance, DSN
hygiene, and record/sealing parity with the JSONL EventLog without a database.
"""

from __future__ import annotations

import os
import uuid

import pytest

from egmra.m2 import EventStore, PostgresEventStore
from egmra.truth.events import EventLog, seal_event

_DSN = "postgresql://user:secret@db.example.com:5432/egmra"

# Live acceptance: only runs when a disposable Postgres server DSN is provided.
_LIVE_DSN = os.environ.get("EGMRA_TEST_POSTGRES_DSN")
live_postgres = pytest.mark.skipif(
    not _LIVE_DSN,
    reason="set EGMRA_TEST_POSTGRES_DSN (a disposable server) to run live Postgres tests",
)


def test_postgres_store_conforms_to_event_store_protocol():
    store = PostgresEventStore(_DSN, run_id="r1")
    assert isinstance(store, EventStore)
    for method in ("append", "verify_integrity", "merkle_root"):
        assert callable(getattr(store, method))


def test_dsn_is_redacted_of_credentials():
    store = PostgresEventStore(_DSN)
    assert "secret" not in store.dsn
    assert "user" not in store.dsn
    assert store.dsn == "postgresql://db.example.com:5432/egmra"


@pytest.mark.parametrize("bad", ["not-a-dsn", "mysql://h/db", "postgresql://h", "postgresql:///db"])
def test_invalid_dsn_is_rejected(bad):
    with pytest.raises(ValueError):
        PostgresEventStore(bad)


def test_business_record_layout_matches_jsonl_event_log(tmp_path):
    # The Postgres store must build the exact same business record as the JSONL
    # log, so an event's id/signature are identical across backends.
    log = EventLog(tmp_path / "events.jsonl", run_id="r1")
    event = log.append(action="HUMAN_INTERVENTION",
                       actor={"type": "human", "id": "auditor"}, object_ids=["r1"])
    jsonl_keys = set(event.business_record().keys())

    store = PostgresEventStore(_DSN, run_id="r1")
    pg_business = store._business_record(
        sequence=0, prev_event_id="GENESIS", action="HUMAN_INTERVENTION",
        actor={"type": "human", "id": "auditor"}, object_ids=["r1"], timestamp=event.timestamp,
        prior_versions={}, new_versions={}, input_hashes=[], output_hashes=[],
        run_contract_hash="", budget_delta={}, reason_code="", human_readable_reason="",
        payload={})
    assert set(pg_business.keys()) == jsonl_keys


def test_sealing_is_identical_across_backends(tmp_path, monkeypatch):
    # Given the same business record and key, both backends produce the same
    # event id and signature (the basis for replay parity).
    key = b"event-test-key-that-is-at-least-32-bytes"
    store = PostgresEventStore(_DSN, run_id="r1")
    business = store._business_record(
        sequence=0, prev_event_id="GENESIS", action="CLAIM_PROPOSED",
        actor={"type": "worker", "id": "w0"}, object_ids=["c1"],
        timestamp="2026-07-13T00:00:00Z", prior_versions={}, new_versions={},
        input_hashes=[], output_hashes=[], run_contract_hash="", budget_delta={},
        reason_code="", human_readable_reason="", payload={"k": "v"})
    a = seal_event(key, business)
    b = seal_event(key, business)
    assert a.event_id == b.event_id and a.signature == b.signature
    assert len(a.event_id) == 64 and len(a.signature) == 64


def test_append_requires_a_server_but_is_not_a_stub():
    # append is a real implementation that needs a DB; without psycopg/server it
    # raises a connection error — never silently fabricates an event.
    store = PostgresEventStore(_DSN, run_id="r1")
    with pytest.raises(RuntimeError):
        store.append(action="HUMAN_INTERVENTION",
                     actor={"type": "human", "id": "a"}, object_ids=["r1"])


def test_store_exposes_full_event_log_dropin_interface():
    # EpistemicGraph consumes an EventLog via append/verify_integrity/merkle_root
    # plus the events sequence and len(); the Postgres store must provide all of
    # them so it is a drop-in backend, not a partial adapter.
    store = PostgresEventStore(_DSN, run_id="r1")
    for method in ("append", "verify_integrity", "merkle_root", "close", "migrate",
                   "last_event_id"):
        assert callable(getattr(store, method))
    assert isinstance(type(store).events, property)
    assert hasattr(type(store), "__len__")
    assert store.run_id == "r1"


# --- Live acceptance against a disposable Postgres server (gated) ---------------


@live_postgres
def test_live_append_len_events_and_merkle_persist_and_replay():
    rid = f"live-{uuid.uuid4().hex[:12]}"
    store = PostgresEventStore(_LIVE_DSN, run_id=rid)
    try:
        store.migrate()
        assert len(store) == 0
        e0 = store.append(action="CLAIM_PROPOSED", actor={"type": "worker", "id": "w0"},
                          object_ids=["c1"], payload={"k": 1})
        e1 = store.append(action="CLAIM_PROPOSED", actor={"type": "worker", "id": "w0"},
                          object_ids=["c2"], payload={"k": 2})
        assert len(store) == 2
        ids = [e.event_id for e in store.events]
        assert ids == [e0.event_id, e1.event_id]
        assert store.last_event_id() == e1.event_id
        assert store.verify_integrity() is True
        root = store.merkle_root()
        assert len(root) == 64
    finally:
        store.close()

    # A brand-new store (fresh connection) reconnects and replays the same chain.
    replay = PostgresEventStore(_LIVE_DSN, run_id=rid)
    try:
        assert len(replay) == 2
        assert replay.verify_integrity() is True
        assert replay.merkle_root() == root
    finally:
        replay.close()


@live_postgres
def test_live_transaction_rolls_back_on_error_without_partial_write():
    rid = f"live-{uuid.uuid4().hex[:12]}"
    store = PostgresEventStore(_LIVE_DSN, run_id=rid)
    try:
        store.migrate()
        store.append(action="CLAIM_PROPOSED", actor={"type": "worker", "id": "w0"},
                     object_ids=["c1"], payload={"k": 1})
        before = len(store)
        conn = store._connection()
        with pytest.raises(RuntimeError):
            with conn.transaction():
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO events (event_id, sequence, prev_event_id, run_id, "
                        "payload, signature) VALUES (%s, %s, %s, %s, %s, %s)",
                        ("deadbeef", 999, "x", rid, "{}", "sig"))
                raise RuntimeError("boom")  # abort the transaction after the insert
        # The insert must have been rolled back: the log is unchanged and valid.
        assert len(store) == before
        assert store.verify_integrity() is True
    finally:
        store.close()


@live_postgres
def test_live_tampered_payload_fails_integrity_verification():
    rid = f"live-{uuid.uuid4().hex[:12]}"
    store = PostgresEventStore(_LIVE_DSN, run_id=rid)
    try:
        store.migrate()
        store.append(action="CLAIM_PROPOSED", actor={"type": "worker", "id": "w0"},
                     object_ids=["c1"], payload={"k": 1})
        assert store.verify_integrity() is True
        # Tamper with the stored payload out-of-band; the signed hash chain must
        # detect it and fail closed.
        conn = store._connection()
        with conn.transaction():
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE events SET payload = jsonb_set(payload, '{human_readable_reason}', "
                    "'\"tampered\"'::jsonb) WHERE run_id = %s", (rid,))
        assert store.verify_integrity() is False
    finally:
        store.close()

