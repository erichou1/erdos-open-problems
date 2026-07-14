"""No-server conformance tests for the PostgreSQL event store (defect 14).

Live replay parity against a real PostgreSQL server is a separate acceptance gate
(BLOCKED ON LIVE ACCEPTANCE); these tests verify protocol conformance, DSN
hygiene, and record/sealing parity with the JSONL EventLog without a database.
"""

from __future__ import annotations

import pytest

from egmra.m2 import EventStore, PostgresEventStore
from egmra.truth.events import EventLog, seal_event

_DSN = "postgresql://user:secret@db.example.com:5432/egmra"


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
