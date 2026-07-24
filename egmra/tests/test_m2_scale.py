"""Tests for the M2 scale layer: event-store contract, object store, assembly."""

import pytest

from egmra.m2 import (
    ContentAddressedObjectStore,
    EventStore,
    M2Assembly,
    PostgresEventStore,
)
from egmra.truth.events import EventLog


def test_jsonl_event_log_satisfies_event_store_contract(tmp_path):
    log = EventLog(tmp_path / "e.jsonl", run_id="r")
    assert isinstance(log, EventStore)   # same append-only contract as Postgres


def test_object_store_is_content_addressed(tmp_path):
    store = ContentAddressedObjectStore(tmp_path / "objects")
    digest = store.put(b"hello world")
    assert store.exists(digest)
    assert store.get(digest) == b"hello world"
    # identical content -> identical digest (dedup)
    assert store.put(b"hello world") == digest


def test_postgres_event_store_documents_but_does_not_fake(tmp_path):
    pg = PostgresEventStore("postgres://localhost/egmra")
    assert "CREATE TABLE" in pg.schema_ddl
    with pytest.raises(RuntimeError):
        pg.connect()   # requires a real server; never faked


def test_m2_assembly_wires_local_backends(tmp_path):
    log = EventLog(tmp_path / "e.jsonl", run_id="r")
    store = ContentAddressedObjectStore(tmp_path / "obj")
    assembly = M2Assembly(event_log=log, object_store=store, concurrent_programs=4)
    assert assembly.event_store_is_valid()
    assert assembly.container_backend("egmra/lean:pinned").policy == "container"
    assert assembly.topology_hash() == assembly.topology_hash()
