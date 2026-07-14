"""Adversarial control-plane tests derived independently from §§10.4, 14.3-14.5."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import math

import pytest

from egmra.control import (
    LeaseError,
    LeaseManager,
    ParallelPolicyError,
    ProviderThrottle,
    VerifierPool,
)


class _Clock:
    def __init__(self) -> None:
        self.t = 10.0

    def __call__(self) -> float:
        return self.t


def test_expired_holder_cannot_renew_and_stale_fence_is_rejected(tmp_path) -> None:
    clock = _Clock()
    manager = LeaseManager(now_fn=clock, state_path=tmp_path / "leases.json")
    first = manager.acquire(
        branch_id="b", holder="host:1", stage="compute", run_contract_id="rc", grace_seconds=2
    )
    clock.t = 13.0

    with pytest.raises(LeaseError, match="expired"):
        manager.renew("b", "host:1", fencing_token=first.fencing_token)

    second = manager.transfer_if_expired(
        branch_id="b", new_holder="host:2", run_contract_id="rc"
    )
    assert second is not None
    assert second.fencing_token > first.fencing_token
    with pytest.raises(LeaseError, match="stale fencing token"):
        manager.assert_current("b", "host:1", first.fencing_token)
    with pytest.raises(LeaseError):
        manager.release("b", "host:1", fencing_token=first.fencing_token)


def test_lease_state_survives_restart_and_fence_counter_never_reuses(tmp_path) -> None:
    clock = _Clock()
    state = tmp_path / "leases.json"
    first_manager = LeaseManager(now_fn=clock, state_path=state)
    first = first_manager.acquire(
        branch_id="b", holder="h1", stage="proof", run_contract_id="rc", grace_seconds=1
    )

    restarted = LeaseManager(now_fn=clock, state_path=state)
    with pytest.raises(LeaseError, match="already leased"):
        restarted.acquire(
            branch_id="b", holder="h2", stage="proof", run_contract_id="rc", grace_seconds=1
        )
    clock.t += 2
    second = restarted.transfer_if_expired(
        branch_id="b", new_holder="h2", run_contract_id="rc"
    )
    assert second is not None and second.fencing_token == first.fencing_token + 1

    restarted_again = LeaseManager(now_fn=clock, state_path=state)
    restarted_again.assert_current("b", "h2", second.fencing_token)


def test_concurrent_acquire_has_exactly_one_winner(tmp_path) -> None:
    clock = _Clock()
    state = tmp_path / "leases.json"

    def try_acquire(index: int) -> tuple[str, int] | None:
        manager = LeaseManager(now_fn=clock, state_path=state)
        try:
            lease = manager.acquire(
                branch_id="b", holder=f"h{index}", stage="s", run_contract_id="rc"
            )
            return lease.holder, lease.fencing_token
        except LeaseError:
            return None

    with ThreadPoolExecutor(max_workers=16) as pool:
        winners = [result for result in pool.map(try_acquire, range(32)) if result]
    assert len(winners) == 1


def test_corrupt_persisted_lease_state_fails_closed(tmp_path) -> None:
    state = tmp_path / "leases.json"
    state.write_text('{"leases":', encoding="utf-8")
    with pytest.raises(LeaseError, match="corrupt"):
        LeaseManager(state_path=state)


def test_lease_inputs_fail_closed() -> None:
    manager = LeaseManager()
    with pytest.raises(LeaseError):
        manager.acquire(
            branch_id="", holder="h", stage="s", run_contract_id="rc", grace_seconds=1
        )
    with pytest.raises(LeaseError):
        manager.acquire(
            branch_id="b", holder="h", stage="s", run_contract_id="rc", grace_seconds=0
        )


def test_verifier_pool_is_bounded_thread_safe_and_releasable() -> None:
    pool = VerifierPool(total_workers=4, reserved_for_verification=2)
    assert pool.start_generation()
    assert pool.start_generation()
    assert not pool.start_generation()
    assert pool.start_verification()
    assert pool.start_verification()
    assert not pool.start_verification()
    assert pool.active_generation + pool.active_verification == 4

    pool.finish_generation()
    assert pool.start_verification()
    pool.finish_verification()
    pool.finish_verification()
    pool.finish_verification()
    with pytest.raises(ParallelPolicyError, match="underflow"):
        pool.finish_verification()


@pytest.mark.parametrize(
    ("total", "reserved"), [(0, 0), (-1, 0), (2, -1), (2, 3)]
)
def test_verifier_pool_rejects_invalid_capacity(total: int, reserved: int) -> None:
    with pytest.raises(ParallelPolicyError):
        VerifierPool(total_workers=total, reserved_for_verification=reserved)


def test_throttle_rejects_nonfinite_or_invalid_inputs_without_overflow() -> None:
    with pytest.raises(ValueError):
        ProviderThrottle(provider="", base_seconds=1)
    with pytest.raises(ValueError):
        ProviderThrottle(provider="p", base_seconds=-1)
    throttle = ProviderThrottle(provider="p", base_seconds=2, seed=1)
    assert throttle.backoff_seconds(10**9) == 120.0
    for invalid in (-1.0, math.nan, math.inf):
        with pytest.raises(ValueError):
            throttle.backoff_seconds(1, retry_after=invalid)

