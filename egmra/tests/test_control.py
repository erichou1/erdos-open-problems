"""Tests for the control plane: leases, throttle, parallel, recovery, congestion."""

import pytest

from egmra.control import (
    CongestionController,
    LeaseError,
    LeaseManager,
    ProviderThrottle,
    VerifierPool,
    can_parallelize,
    congestion_price,
    must_serialize,
    recovery_for,
    truth_effect,
)


# ── leases ────────────────────────────────────────────────────────────────────

class _Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_lease_acquire_renew_and_expiry_transfer():
    clock = _Clock()
    mgr = LeaseManager(now_fn=clock)
    lease = mgr.acquire(branch_id="b1", holder="host:1", stage="scout",
                        run_contract_id="rc1", grace_seconds=10.0)
    assert lease.holder == "host:1"
    with pytest.raises(LeaseError):
        mgr.acquire(branch_id="b1", holder="host:2", stage="scout", run_contract_id="rc1")
    # advance past grace -> another worker can transfer (compatible contract)
    clock.t = 20.0
    transferred = mgr.transfer_if_expired(branch_id="b1", new_holder="host:2", run_contract_id="rc1")
    assert transferred and transferred.holder == "host:2"


def test_lease_transfer_refused_across_incompatible_contract():
    clock = _Clock()
    mgr = LeaseManager(now_fn=clock)
    mgr.acquire(branch_id="b1", holder="h1", stage="s", run_contract_id="rc1", grace_seconds=1.0)
    clock.t = 5.0
    with pytest.raises(LeaseError):
        mgr.transfer_if_expired(branch_id="b1", new_holder="h2", run_contract_id="rc2")


# ── throttle ────────────────────────────────────────────────────────────────────

def test_backoff_capped_at_120s_and_honors_retry_after():
    t = ProviderThrottle(provider="openai", seed=1)
    assert t.backoff_seconds(20) <= 120.0
    assert t.backoff_seconds(1, retry_after=45.0) == 45.0
    assert t.backoff_seconds(1, retry_after=500.0) == 120.0


def test_rate_limit_pauses_never_consumes_math_retry():
    t = ProviderThrottle(provider="openai", seed=1)
    result = t.on_rate_limit(2)
    assert result["action"] == "pause" and result["consumes_math_retry"] is False
    assert t.math_retries_consumed == 0 and t.censored_pauses == 1


# ── parallel ─────────────────────────────────────────────────────────────────────

def test_parallel_policy_classification():
    assert can_parallelize("different_research_programs")
    assert must_serialize("claim_promotion")
    with pytest.raises(Exception):
        can_parallelize("mystery_op")


def test_verifier_pool_reserves_capacity():
    pool = VerifierPool(total_workers=4, reserved_for_verification=2)
    # only 2 non-reserved slots for generation
    assert pool.start_generation()
    assert pool.start_generation()
    assert not pool.start_generation()      # reserved slots protected
    assert pool.start_verification()         # verification can still start


# ── recovery ─────────────────────────────────────────────────────────────────────

def test_recovery_table_truth_effects():
    assert truth_effect("rate_limit_quota").startswith("none")
    assert "revoke" in recovery_for("false_lemma").automatic_response
    assert truth_effect("verification_backlog") == "no truth downgrade"
    with pytest.raises(KeyError):
        recovery_for("nope")


# ── congestion ───────────────────────────────────────────────────────────────────

def test_congestion_pricing_grows_and_is_not_truth():
    assert congestion_price(0, 10) < congestion_price(20, 10)
    cc = CongestionController(capacity=10)
    assert cc.should_throttle_generation(10)
    assert not cc.should_throttle_generation(3)
    assert cc.affects_truth() is False
