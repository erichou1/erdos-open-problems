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
