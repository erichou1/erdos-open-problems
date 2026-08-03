"""Tests for the browser ChatGPT model-runner adapter (fake backend)."""

from __future__ import annotations

import pytest

from egmra.agents.browser_runner import (
    BROWSER_RUNNER_VERSION,
    MAX_COOLDOWN_CEILING_SECONDS,
    BrowserChatGPTRunner,
    BrowserProviderUnavailable,
    BrowserResponseError,
)


class FakeBackend:
    """A scriptable, network-free stand-in for the Playwright browser."""

    def __init__(self, responses, *, rate_limited_before=0):
        self._responses = list(responses)
        self._rate_limited_before = rate_limited_before
        self.conversations = 0
        self.sends = []
        self.dismissed = 0
        self.closed = False

    def open_conversation(self):
        self.conversations += 1

    def send(self, prompt):
        self.sends.append(prompt)

    def wait_response(self, *, timeout_s):
        return self._responses.pop(0)

    def conversation_url(self):
        return f"https://chatgpt.com/c/conv-{self.conversations}"

    def is_rate_limited(self):
        if self._rate_limited_before > 0:
            self._rate_limited_before -= 1
            return True
        return False

    def dismiss_rate_limit(self):
        self.dismissed += 1
        return True

    def close(self):
        self.closed = True


def _runner(backend, **kw):
    kw.setdefault("sleep", lambda _s: None)  # never really sleep in tests
    return BrowserChatGPTRunner(backend=backend, **kw)


def test_runner_satisfies_model_runner_protocol():
    runner = _runner(FakeBackend(["a proof sketch"]))
    # ModelRunner is a (non-runtime-checkable) structural protocol: assert the
    # shape the orchestrator relies on rather than a nominal isinstance check.
    assert hasattr(runner, "runner_id") and callable(runner.run)
    resp = runner.run("hi", stage="cold_pass")
    assert set(vars(resp)) >= {"text", "model", "context_id", "prompt_hash"}


def test_run_returns_unattested_identity_and_records_provenance():
    backend = FakeBackend(["Here is a candidate argument."])
    runner = _runner(backend, model_label="ChatGPT 5.x (browser)")
    resp = runner.run("Analyze problem 312.", stage="cold_pass")

    assert resp.text == "Here is a candidate argument."
    # A browser UI label can NEVER be independent-model evidence.
    assert resp.model.attested is False
    assert resp.model.ui_surface == "browser"
    assert resp.model.model == "ChatGPT 5.x (browser)"

    assert len(runner.records) == 1
    rec = runner.records[0]
    assert rec.attested is False
    assert rec.runner_version == BROWSER_RUNNER_VERSION
    assert rec.conversation_url.startswith("https://chatgpt.com/c/")
    assert resp.conversation_url == rec.conversation_url
    assert rec.prompt_hash == resp.prompt_hash
    assert rec.response_hash and rec.response_hash != rec.prompt_hash


def test_each_run_uses_an_isolated_conversation():
    backend = FakeBackend(["one", "two"])
    runner = _runner(backend)
    r1 = runner.run("p1", stage="s1")
    r2 = runner.run("p2", stage="s2")
    assert backend.conversations == 2
    # Distinct conversations -> distinct context ids (no cross-conversation replay).
    assert r1.context_id != r2.context_id


def test_rate_limit_pauses_then_succeeds_without_failing():
    backend = FakeBackend(["recovered answer"], rate_limited_before=2)
    slept = []
    runner = _runner(backend, sleep=slept.append, base_cooldown_s=5.0, cooldown_factor=2.0)
    resp = runner.run("prompt", stage="stage")
    assert resp.text == "recovered answer"
    assert backend.dismissed == 2
    assert runner.records[0].rate_limit_pauses == 2
    # Cooldowns follow the backoff schedule and never exceed the hard ceiling.
    assert slept == [5.0, 10.0]
    assert all(s <= MAX_COOLDOWN_CEILING_SECONDS for s in slept)


def test_cooldown_is_clamped_to_120_seconds():
    backend = FakeBackend(["ok"], rate_limited_before=5)
    slept = []
    runner = _runner(
        backend, sleep=slept.append,
        base_cooldown_s=50.0, cooldown_factor=10.0, max_rate_limit_pauses=6,
    )
    runner.run("p", stage="s")
    assert max(slept) == MAX_COOLDOWN_CEILING_SECONDS
    assert all(s <= MAX_COOLDOWN_CEILING_SECONDS for s in slept)


def test_persistent_rate_limit_raises_provider_unavailable_not_math_failure():
    backend = FakeBackend(["never reached"], rate_limited_before=999)
    runner = _runner(backend, sleep=lambda _s: None, max_rate_limit_pauses=3)
    with pytest.raises(BrowserProviderUnavailable):
        runner.run("p", stage="s")


def test_max_cooldown_cannot_exceed_ceiling_even_if_configured_higher():
    runner = _runner(FakeBackend(["x"]), max_cooldown_s=10_000.0)
    assert runner.max_cooldown_s == MAX_COOLDOWN_CEILING_SECONDS


def test_malformed_response_is_retried_in_a_fresh_conversation():
    backend = FakeBackend(["", "[Could not extract response]", "a real answer"])
    runner = _runner(backend, max_response_retries=2)
    resp = runner.run("p", stage="s")
    assert resp.text == "a real answer"
    assert backend.conversations == 3
    assert runner.records[0].response_retries == 2


def test_persistent_malformed_response_raises_response_error():
    backend = FakeBackend(["", "", ""])
    runner = _runner(backend, max_response_retries=2)
    with pytest.raises(BrowserResponseError):
        runner.run("p", stage="s")


def test_context_manager_closes_backend():
    backend = FakeBackend(["answer"])
    with _runner(backend) as runner:
        runner.run("p", stage="s")
    assert backend.closed is True


class _MidGenBackend:
    """Not throttled pre-submission, but shows a rate limit right AFTER generation
    for the first ``throttled_generations`` responses (models often surface a
    throttle only once reasoning has run for a while)."""

    def __init__(self, responses, *, throttled_generations):
        self._responses = list(responses)
        self._throttled = throttled_generations
        self._generated = 0
        self._just_generated = False
        self.conversations = 0
        self.dismissed = 0
        self.closed = False

    def open_conversation(self):
        self.conversations += 1

    def send(self, prompt):
        pass

    def wait_response(self, *, timeout_s):
        self._just_generated = True
        return self._responses.pop(0)

    def conversation_url(self):
        return f"https://chatgpt.com/c/{self.conversations}"

    def is_rate_limited(self):
        throttled = self._just_generated and self._generated < self._throttled
        if self._just_generated:
            self._just_generated = False
            if throttled:
                self._generated += 1
        return throttled

    def dismiss_rate_limit(self):
        self.dismissed += 1
        return True

    def close(self):
        self.closed = True


def test_mid_generation_rate_limit_is_detected_and_retried():
    # A throttle that appears WHILE generating is discarded and retried on the
    # cooldown budget — the throttle text is never returned as a result, and it is
    # counted as a rate-limit pause, not a malformed-response retry.
    backend = _MidGenBackend(["throttled 1", "throttled 2", "recovered answer"],
                             throttled_generations=2)
    slept = []
    runner = _runner(backend, sleep=slept.append, base_cooldown_s=5.0, cooldown_factor=2.0)
    resp = runner.run("p", stage="s")
    assert resp.text == "recovered answer"
    assert backend.dismissed == 2 and backend.conversations == 3
    assert runner.records[0].rate_limit_pauses == 2
    assert runner.records[0].response_retries == 0
    assert slept == [5.0, 10.0]


def test_persistent_mid_generation_rate_limit_is_provider_unavailable_not_a_result():
    # A perpetual mid-generation throttle exhausts the shared pause budget and
    # signals a transient outage (retained/resumed by the caller) — never a
    # mathematical result, never a BrowserResponseError.
    backend = _MidGenBackend(["x"] * 10, throttled_generations=999)
    runner = _runner(backend, sleep=lambda _s: None, max_rate_limit_pauses=3)
    with pytest.raises(BrowserProviderUnavailable):
        runner.run("p", stage="s")


def test_pre_and_mid_generation_throttles_share_one_pause_budget():
    # 2 pre-submission + 2 mid-generation throttles with a budget of 3 -> the 4th
    # cooldown trips the budget (they are not counted independently).
    class _BothBackend(_MidGenBackend):
        def __init__(self):
            super().__init__(["a", "b", "c"], throttled_generations=2)
            self._pre = 2

        def is_rate_limited(self):
            if not self._just_generated and self._pre > 0:
                self._pre -= 1
                return True  # pre-submission throttle
            return super().is_rate_limited()

    runner = _runner(_BothBackend(), sleep=lambda _s: None, max_rate_limit_pauses=3)
    with pytest.raises(BrowserProviderUnavailable):
        runner.run("p", stage="s")
