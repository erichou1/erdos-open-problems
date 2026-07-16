"""Tests for the pluggable campaign store (DB-backed leases, audit follow-up).

The Postgres store's SQL is verified live against a disposable server (gated on
EGMRA_TEST_POSTGRES_DSN); here we test its construction/DSN hygiene without a
server, and exercise the full Campaign lifecycle over the pluggable store seam
with an in-memory store that signs exactly like the file/Postgres stores.
"""

from __future__ import annotations

import hmac
import json
import os
import threading
import uuid
from contextlib import contextmanager

import pytest

from egmra.orchestrator import Campaign, CampaignError, PostgresCampaignStore
from egmra.orchestrator.campaign import _campaign_key, _hmac_hex
from egmra.provenance.hashing import canonical_json

_LIVE_DSN = os.environ.get("EGMRA_TEST_POSTGRES_DSN")
live_postgres = pytest.mark.skipif(
    not _LIVE_DSN,
    reason="set EGMRA_TEST_POSTGRES_DSN (a disposable server) to run live Postgres tests",
)


class _MemoryCampaignStore:
    """An in-memory CampaignStore that signs exactly like the durable stores."""

    def __init__(self, env=None) -> None:
        self._key = _campaign_key(env)
        self._row: tuple[str, str] | None = None
        self._lock = threading.RLock()

    def read(self):
        if self._row is None:
            return None
        body_text, signature = self._row
        if not hmac.compare_digest(_hmac_hex(self._key, body_text), signature):
            raise CampaignError("campaign state signature is invalid (tampered or wrong key)")
        return json.loads(body_text)

    def write(self, body):
        body_text = canonical_json(body)
        self._row = (body_text, _hmac_hex(self._key, body_text))

    @contextmanager
    def locked(self):
        with self._lock:
            yield

    def close(self):
        return None


# ── construction / DSN hygiene (no server) ──────────────────────────────────

def test_postgres_campaign_store_validates_and_redacts_dsn():
    store = PostgresCampaignStore(
        "postgresql://user:secret@db.example.com:5432/egmra", name="camp")
    assert "secret" not in store.dsn and "user" not in store.dsn
    assert store.dsn == "postgresql://db.example.com:5432/egmra"


@pytest.mark.parametrize("bad", ["not-a-dsn", "mysql://h/db", "postgresql://h", "postgresql:///db"])
def test_postgres_campaign_store_rejects_bad_dsn(bad):
    with pytest.raises(ValueError):
        PostgresCampaignStore(bad, name="camp")


def test_postgres_campaign_store_requires_name_and_key():
    with pytest.raises(CampaignError):
        PostgresCampaignStore("postgresql://db.example.com:5432/egmra", name="")
    with pytest.raises(CampaignError):  # signing key missing
        PostgresCampaignStore("postgresql://db.example.com:5432/egmra", name="c", env={})


def test_postgres_connect_kwargs_survive_a_sleep_dropped_link():
    # A laptop sleeping on battery drops the Neon TCP link; without keepalives
    # the next write blocks forever, freezing lease renewals + heartbeats while
    # the process keeps computing (nothing recorded). Keepalives are all
    # client-side TCP params, so they stay safe through the Neon pooler (a
    # server-side statement_timeout GUC would be rejected by PgBouncer).
    store = PostgresCampaignStore(
        "postgresql://db.example.com:5432/egmra", name="camp")
    kwargs = store._connect_kwargs()
    assert kwargs["keepalives"] == 1
    assert kwargs["connect_timeout"] >= 5
    assert all(kwargs[k] > 0 for k in
               ("keepalives_idle", "keepalives_interval", "keepalives_count"))
    assert "options" not in kwargs   # pooler-incompatible startup GUCs excluded


# ── stale-connection resilience (Neon drops idle connections) ────────────────

class _FakeCursor:
    def __init__(self, conn):
        self._conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        if self._conn.dead:
            # A server-side drop surfaces only on the NEXT statement.
            import psycopg
            raise psycopg.OperationalError(
                "consuming input failed: SSL connection has been closed unexpectedly")
        self._conn.executed.append(sql.split()[0])

    def fetchone(self):
        return (self._conn.store_body, self._conn.store_sig)


class _FakeConn:
    def __init__(self):
        self.dead = False
        self.closed = False
        self.executed: list[str] = []
        self.store_body = None
        self.store_sig = None

    def cursor(self):
        return _FakeCursor(self)

    def close(self):
        self.closed = True


def _pg_store_with_fake_conns(conns):
    """A PostgresCampaignStore whose connect() hands out fake conns in order."""
    store = PostgresCampaignStore(
        "postgresql://db.example.com:5432/egmra", name="camp")
    it = iter(conns)
    store.connect = lambda: next(it)  # type: ignore[method-assign]
    return store


def test_postgres_store_reconnects_when_neon_drops_the_idle_connection():
    dead_conn, fresh_conn = _FakeConn(), _FakeConn()
    dead_conn.dead = True                      # Neon closed it while idle
    store = _pg_store_with_fake_conns([dead_conn, fresh_conn])

    # First use establishes dead_conn; acquiring the advisory lock fails with a
    # disconnect error, so the store must reset and retry on a fresh connection.
    with store.locked():
        pass
    assert dead_conn.closed and not fresh_conn.closed
    assert "SELECT" in fresh_conn.executed        # lock acquired on the retry conn


def test_postgres_store_reraises_non_disconnect_errors():
    class _BoomConn(_FakeConn):
        def cursor(self):
            raise RuntimeError("not a disconnect")
    store = _pg_store_with_fake_conns([_BoomConn(), _FakeConn()])
    with pytest.raises(RuntimeError, match="not a disconnect"):
        store.read()



# ── the store seam drives the full Campaign lifecycle + fail-closed tamper ────

def test_campaign_over_pluggable_store_full_lifecycle_and_resume():
    store = _MemoryCampaignStore()
    campaign = Campaign("unused.json", worker_ids=("w0",), store=store)
    campaign.initialize("camp", ["p1", "p2"])
    assignment = campaign.lease("w0", now=0.0)
    assert assignment.problem_id == "p1" and assignment.fencing_token >= 1
    assert campaign.complete(assignment.problem_id, "w0", assignment.fencing_token,
                             result_state="OPEN_NO_PROGRESS")
    # A fresh Campaign over the SAME durable store resumes (no re-init, no dup).
    resumed = Campaign("unused.json", worker_ids=("w0",), store=store)
    status = resumed.status()
    assert status["by_status"].get("done") == 1
    assert resumed.pending_count() == 1  # p2 still pending
    assert resumed.lease("w0", now=0.0).problem_id == "p2"


def test_campaign_over_pluggable_store_detects_tamper():
    store = _MemoryCampaignStore()
    campaign = Campaign("unused.json", worker_ids=("w0",), store=store)
    campaign.initialize("camp", ["p1"])
    body_text, signature = store._row  # corrupt the body without re-signing
    store._row = (body_text.replace("p1", "p9"), signature)
    with pytest.raises(CampaignError):
        campaign.status()


def test_second_machine_joins_despite_reranked_order():
    """A rerank must not lock a second machine out of the shared campaign.

    Continuous rerank legitimately permutes the shared order; a machine
    launching later with the ORIGINAL triage order joins as a resume. A grown
    ranked set EXTENDS the campaign in place (nothing dropped, reranked order
    and in-flight statuses preserved); a different campaign id still fails
    closed.
    """
    store = _MemoryCampaignStore()
    machine_a = Campaign("unused.json", worker_ids=("A-w0",), store=store)
    machine_a.initialize("camp", ["p1", "p2", "p3"])
    lease_a = machine_a.lease("A-w0", now=0.0)
    assert machine_a.reorder_pending(["p3", "p2", "p1"])  # rerank permutes the order

    machine_b = Campaign("unused.json", worker_ids=("B-w0",), store=store)
    machine_b.initialize("camp", ["p1", "p2", "p3"])   # original order: joins
    lease_b = machine_b.lease("B-w0", now=0.0)
    assert lease_b.problem_id == "p3"                  # reranked order preserved
    assert lease_b.problem_id != lease_a.problem_id    # and no double-lease

    # A grown ranked set extends in place: new problem appended pending, the
    # reranked order and both live leases untouched.
    order = machine_b.initialize("camp", ["p1", "p2", "p9"])
    assert order == ["p3", "p2", "p1", "p9"]
    workers = machine_b.status()["workers"]
    assert workers["p9"]["status"] == "pending"
    assert workers[lease_a.problem_id]["status"] == "leased"
    with pytest.raises(CampaignError):                 # different id still refused
        machine_b.initialize("other-camp", ["p1", "p2", "p3"])


# ── live Postgres round-trip (gated) ─────────────────────────────────────────

@live_postgres
def test_postgres_backed_campaign_round_trip():  # pragma: no cover - needs a server
    name = f"egmra-test-{uuid.uuid4().hex[:12]}"
    store = PostgresCampaignStore(_LIVE_DSN, name=name)
    try:
        campaign = Campaign("unused.json", worker_ids=("w0", "w1"), store=store)
        campaign.initialize("camp", ["p1", "p2"])
        assignment = campaign.lease("w0", now=0.0)
        assert campaign.complete(assignment.problem_id, "w0", assignment.fencing_token,
                                 result_state="OPEN_NO_PROGRESS")
        # A fresh store/connection reconnects and sees the durable DB-backed state.
        reconnected = PostgresCampaignStore(_LIVE_DSN, name=name)
        try:
            resumed = Campaign("unused.json", worker_ids=("w0", "w1"), store=reconnected)
            assert resumed.status()["by_status"].get("done") == 1
            assert resumed.pending_count() == 1
        finally:
            reconnected.close()
    finally:
        store.close()
