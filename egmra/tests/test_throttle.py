"""Tests for the shared cross-worker browser throttle coordinator."""

from __future__ import annotations

from egmra.agents.browser_runner import MAX_COOLDOWN_CEILING_SECONDS, BrowserChatGPTRunner
from egmra.agents.throttle import SharedThrottle


class _Clock:
    def __init__(self):
        self.t = 1000.0
        self.slept = []

    def now(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def test_cooldown_is_shared_across_workers(tmp_path):
    clock = _Clock()
    state = tmp_path / "throttle.json"
    worker_a = SharedThrottle(state, now=clock.now, sleep=clock.sleep, base_cooldown_s=5.0)
    worker_b = SharedThrottle(state, now=clock.now, sleep=clock.sleep, base_cooldown_s=5.0)

    # Worker A hits a rate limit; worker B must observe the shared cooldown.
    cooldown = worker_a.record_rate_limit()
    assert cooldown == 5.0
    assert worker_b.cooldown_remaining() > 0
    slept = worker_b.wait_if_cooling()
    assert slept > 0
    assert worker_b.cooldown_remaining() == 0


def test_backoff_escalates_and_clamps_to_120(tmp_path):
    clock = _Clock()
    throttle = SharedThrottle(tmp_path / "t.json", now=clock.now, sleep=clock.sleep,
                              base_cooldown_s=50.0, cooldown_factor=10.0)
    first = throttle.record_rate_limit()
    second = throttle.record_rate_limit()
    assert first == 50.0
    assert second == MAX_COOLDOWN_CEILING_SECONDS  # 500 clamped to 120


def test_retry_after_is_honored_when_larger(tmp_path):
    clock = _Clock()
    throttle = SharedThrottle(tmp_path / "t.json", now=clock.now, sleep=clock.sleep,
                              base_cooldown_s=5.0)
    assert throttle.record_rate_limit(retry_after=30.0) == 30.0
    # But still clamped to the 120s ceiling.
    throttle.clear()
    assert throttle.record_rate_limit(retry_after=9999.0) == MAX_COOLDOWN_CEILING_SECONDS


def test_clear_resets_consecutive_backoff(tmp_path):
    clock = _Clock()
    throttle = SharedThrottle(tmp_path / "t.json", now=clock.now, sleep=clock.sleep,
                              base_cooldown_s=5.0, cooldown_factor=2.0)
    throttle.record_rate_limit()
    throttle.record_rate_limit()
    throttle.clear()
    assert throttle.record_rate_limit() == 5.0  # backoff restarted from base


class _RateLimitedBackend:
    """Rate-limited for the first N checks, then clear; records one good response."""

    def __init__(self, limited_checks):
        self._limited = limited_checks
        self.dismissed = 0

    def open_conversation(self):
        pass

    def send(self, prompt):
        pass

    def wait_response(self, *, timeout_s):
        return "a candidate argument"

    def conversation_url(self):
        return "https://chatgpt.com/c/abc"

    def is_rate_limited(self):
        if self._limited > 0:
            self._limited -= 1
            return True
        return False

    def dismiss_rate_limit(self):
        self.dismissed += 1
        return True

    def close(self):
        pass


def test_runner_uses_shared_throttle_for_cooldowns(tmp_path):
    clock = _Clock()
    throttle = SharedThrottle(tmp_path / "t.json", now=clock.now, sleep=clock.sleep,
                              base_cooldown_s=5.0, cooldown_factor=2.0)
    runner = BrowserChatGPTRunner(
        backend=_RateLimitedBackend(limited_checks=2),
        sleep=clock.sleep, now=clock.now, throttle=throttle,
    )
    resp = runner.run("prompt", stage="branch:b1")
    assert resp.text == "a candidate argument"
    assert runner.records[0].rate_limit_pauses == 2
    # Every sleep respected the hard ceiling.
    assert all(s <= MAX_COOLDOWN_CEILING_SECONDS for s in clock.slept)
    # A peer worker sharing the file sees a cleared cooldown after success.
    peer = SharedThrottle(tmp_path / "t.json", now=clock.now, sleep=clock.sleep)
    assert peer.cooldown_remaining() == 0
