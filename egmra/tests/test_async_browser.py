"""Tests for the asynchronous multi-tab browser engine (genuine multi-worker).

The live Playwright driver is exercised only with an authenticated profile (never
in CI); here a fake async driver proves the engine's genuine concurrency (N tabs
make progress simultaneously on one shared event loop), the per-tab backend
delegation, the runner pool, and the lifecycle.
"""

from __future__ import annotations

import asyncio
import threading

import pytest

from egmra.agents.async_browser import (
    AsyncBrowserEngine,
    PlaywrightAsyncPageDriver,
    TabBackend,
    build_browser_runner_pool,
)


class _FakePage:
    def __init__(self, index: int) -> None:
        self.index = index


class _ConcurrentFakeDriver:
    """A fake async driver whose ``wait_response`` only returns once ALL tabs are
    waiting simultaneously (an ``asyncio.Barrier``) — so a passing test proves the
    N tabs ran concurrently on the shared loop, not one-at-a-time."""

    def __init__(self, tab_count: int) -> None:
        self._tab_count = tab_count
        self._barrier: asyncio.Barrier | None = None
        self.started = False
        self.closed = False

    async def start(self, tab_count: int) -> list[_FakePage]:
        self._barrier = asyncio.Barrier(tab_count)
        self.started = True
        return [_FakePage(i) for i in range(tab_count)]

    async def open_conversation(self, page: _FakePage) -> None:
        return None

    async def send(self, page: _FakePage, prompt: str) -> None:
        return None

    async def wait_response(self, page: _FakePage, *, timeout_s: float) -> str:
        # Blocks until every tab's coroutine is here at once (genuine overlap).
        await asyncio.wait_for(self._barrier.wait(), timeout=4.0)
        return f"resp-tab-{page.index}"

    async def conversation_url(self, page: _FakePage) -> str:
        return f"https://chatgpt.com/c/tab{page.index}"

    async def is_rate_limited(self, page: _FakePage) -> bool:
        return False

    async def dismiss_rate_limit(self, page: _FakePage) -> bool:
        return False

    async def close(self) -> None:
        self.closed = True


def test_async_engine_runs_tabs_concurrently():
    driver = _ConcurrentFakeDriver(3)
    engine = AsyncBrowserEngine(driver, tab_count=3, op_timeout_s=6.0).start()
    try:
        assert len(engine.pages) == 3
        results: dict[int, str] = {}
        errors: list[BaseException] = []

        def _drive(page: _FakePage) -> None:
            try:
                results[page.index] = engine.wait_response(page, timeout_s=1.0)
            except BaseException as exc:  # noqa: BLE001 - surface in the assertion
                errors.append(exc)

        threads = [threading.Thread(target=_drive, args=(p,)) for p in engine.pages]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=6.0)
        # The barrier only releases when all three tabs are waiting at once.
        assert not errors, errors
        assert results == {0: "resp-tab-0", 1: "resp-tab-1", 2: "resp-tab-2"}
    finally:
        engine.close()


def test_response_wait_uses_generation_budget_not_short_bridge_budget():
    class _SlowResponseDriver(_ConcurrentFakeDriver):
        async def wait_response(self, page, *, timeout_s):
            await asyncio.sleep(0.08)
            return f"slow-{page.index}"

    driver = _SlowResponseDriver(1)
    # Ordinary bridge calls have a deliberately tiny budget. A model response
    # with its own larger generation budget must not be killed by that cap.
    engine = AsyncBrowserEngine(driver, tab_count=1, op_timeout_s=0.02).start()
    try:
        assert engine.wait_response(engine.pages[0], timeout_s=0.2) == "slow-0"
    finally:
        engine.close()


def test_async_engine_rejects_out_of_range_tab_count():
    with pytest.raises(ValueError):
        AsyncBrowserEngine(_ConcurrentFakeDriver(0), tab_count=0)
    with pytest.raises(ValueError):
        AsyncBrowserEngine(_ConcurrentFakeDriver(6), tab_count=6)


def test_async_engine_close_is_idempotent_and_stops_thread():
    driver = _ConcurrentFakeDriver(1)
    engine = AsyncBrowserEngine(driver, tab_count=1, op_timeout_s=6.0).start()
    engine.close()
    engine.close()  # idempotent
    assert driver.closed is True
    assert not engine._thread.is_alive()
    with pytest.raises(RuntimeError):
        engine.wait_response(_FakePage(0), timeout_s=1.0)  # closed -> no dispatch


def test_async_engine_ops_before_start_raise():
    engine = AsyncBrowserEngine(_ConcurrentFakeDriver(1), tab_count=1)
    with pytest.raises(RuntimeError):
        engine.send(_FakePage(0), "hi")


class _RecordingEngine:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def open_conversation(self, page):
        self.calls.append(("open", page))

    def send(self, page, prompt):
        self.calls.append(("send", page, prompt))

    def wait_response(self, page, *, timeout_s):
        self.calls.append(("wait", page, timeout_s))
        return "r"

    def conversation_url(self, page):
        self.calls.append(("url", page))
        return "u"

    def is_rate_limited(self, page):
        self.calls.append(("rl", page))
        return False

    def dismiss_rate_limit(self, page):
        self.calls.append(("dismiss", page))
        return True


def test_tab_backend_delegates_each_op_to_its_own_page():
    engine = _RecordingEngine()
    backend = TabBackend(engine, "PAGE-A")
    backend.open_conversation()
    backend.send("hello")
    assert backend.wait_response(timeout_s=5.0) == "r"
    assert backend.conversation_url() == "u"
    assert backend.is_rate_limited() is False
    assert backend.dismiss_rate_limit() is True
    backend.close()  # a single tab is never torn down (engine owns teardown)
    assert all(call[1] == "PAGE-A" for call in engine.calls)
    assert ("send", "PAGE-A", "hello") in engine.calls


def test_build_browser_runner_pool_binds_one_runner_per_tab():
    driver = _ConcurrentFakeDriver(3)
    engine = AsyncBrowserEngine(driver, tab_count=3, op_timeout_s=6.0).start()
    try:
        pool = build_browser_runner_pool(engine)
        assert len(pool) == 3
        # Each runner drives a distinct tab and carries a distinct runner id.
        assert {runner.backend._page.index for runner in pool} == {0, 1, 2}
        assert len({runner.runner_id for runner in pool}) == 3
    finally:
        engine.close()


class _DelayedComposerPage:
    def __init__(self, *, appears: bool = True) -> None:
        self.appears = appears
        self.ready = False
        self.waited = False

    async def goto(self, _url, **_kwargs):
        return None

    async def wait_for_selector(self, _selector, **_kwargs):
        self.waited = True
        if not self.appears:
            raise TimeoutError("composer stayed unavailable")
        self.ready = True
        return object()

    async def query_selector(self, _selector):
        return object() if self.ready else None

    async def evaluate(self, _script):
        return "https://chatgpt.com/g/project"


def test_live_async_driver_waits_for_delayed_composer_before_returning():
    driver = PlaywrightAsyncPageDriver()
    driver._cb = type("CB", (), {"PROJECT_URL": "https://chatgpt.com/g/project"})
    page = _DelayedComposerPage()

    asyncio.run(driver.open_conversation(page))

    assert page.waited and page.ready


def test_live_async_driver_fails_explicitly_when_composer_never_appears():
    driver = PlaywrightAsyncPageDriver()
    driver._cb = type("CB", (), {"PROJECT_URL": "https://chatgpt.com/g/project"})
    page = _DelayedComposerPage(appears=False)

    with pytest.raises(RuntimeError, match="input box"):
        asyncio.run(driver.open_conversation(page))
