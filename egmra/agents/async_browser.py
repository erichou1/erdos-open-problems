"""Asynchronous multi-tab browser engine (DECISIONS.md D-A: multi-worker browser).

Playwright's *sync* API is single-threaded, so N browser workers cannot share one
browser across threads — which is why the sync :class:`PlaywrightChatGPTBackend`
only ever drives a single worker. This module drives ONE authenticated Chromium
through Playwright's *async* API on a dedicated event-loop thread, with a POOL of
N pages (tabs). Worker threads keep calling the ordinary synchronous
:class:`~egmra.agents.browser_runner.BrowserBackend` surface; each call is
dispatched onto the shared loop with :func:`asyncio.run_coroutine_threadsafe`, so
the N tabs make genuine concurrent progress on one browser and one account (the
:class:`~egmra.agents.throttle.SharedThrottle` still coordinates cooldowns).

The per-page operations live behind the async :class:`AsyncPageDriver` seam, so
the engine's concurrency is fully exercised by a fake driver in tests; the live
:class:`PlaywrightAsyncPageDriver` is reachable only with an authenticated
Chromium profile and is verified live (never in CI), exactly like the sync
backend it complements.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any, Protocol

from egmra.agents.browser_runner import BrowserChatGPTRunner
from egmra.agents.throttle import SharedThrottle

# Bump when the tab-pool / dispatch contract changes.
ASYNC_BROWSER_ENGINE_VERSION = "async-browser/1"

# Genuine multi-tab overlap is bounded to the same 1..5 window as the campaign
# worker pool (one shared account; more tabs only invite throttling).
MAX_TABS = 5


class AsyncPageDriver(Protocol):
    """Async per-page operations over one authenticated browser (``tab_count`` pages).

    Every method (except :meth:`start`/:meth:`close`) receives an opaque ``page``
    handle returned by :meth:`start`, so the engine can route each worker's call
    to its own tab. Implementations must be safe to interleave on one event loop.
    """

    async def start(self, tab_count: int) -> list[Any]:
        """Launch/authenticate the browser and open ``tab_count`` pages; return them."""

    async def open_conversation(self, page: Any) -> None: ...
    async def send(self, page: Any, prompt: str) -> None: ...
    async def wait_response(self, page: Any, *, timeout_s: float) -> str: ...
    async def conversation_url(self, page: Any) -> str: ...
    async def is_rate_limited(self, page: Any) -> bool: ...
    async def dismiss_rate_limit(self, page: Any) -> bool: ...
    async def close(self) -> None: ...


class AsyncBrowserEngine:
    """One browser + N tabs on a dedicated asyncio loop, with a synchronous bridge.

    The engine owns a background thread running a private event loop. Synchronous
    per-tab calls are marshalled onto that loop and awaited to completion, so many
    worker threads can drive many tabs with genuine concurrency while the callers
    keep the simple blocking :class:`BrowserBackend` contract.
    """

    def __init__(self, driver: AsyncPageDriver, *, tab_count: int,
                 op_timeout_s: float = 900.0) -> None:
        if not 1 <= int(tab_count) <= MAX_TABS:
            raise ValueError(f"tab_count must be between 1 and {MAX_TABS}")
        if not (op_timeout_s and op_timeout_s > 0):
            raise ValueError("op_timeout_s must be positive")
        self._driver = driver
        self._tab_count = int(tab_count)
        self._op_timeout_s = float(op_timeout_s)
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop, name="egmra-async-browser", daemon=True)
        self._pages: list[Any] = []
        self._started = False
        self._closed = False

    # ── loop lifecycle ───────────────────────────────────────────────────────
    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_forever()
        finally:
            # Drain any residual tasks so the loop closes cleanly.
            pending = asyncio.all_tasks(self._loop)
            for task in pending:
                task.cancel()
            self._loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True))
            self._loop.close()

    def _ensure_live(self) -> None:
        # Checked BEFORE the caller builds a coroutine, so a rejected op never
        # leaves an un-awaited coroutine behind.
        if self._closed:
            raise RuntimeError("async browser engine is closed")
        if not self._started:
            raise RuntimeError("async browser engine has not been started")

    def _await(self, coro: "Any", *, timeout_s: float | None = None) -> Any:
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        timeout = self._op_timeout_s if timeout_s is None else max(
            self._op_timeout_s, float(timeout_s))
        return future.result(timeout=timeout)

    def start(self) -> "AsyncBrowserEngine":
        if self._started:
            return self
        if self._closed:
            raise RuntimeError("async browser engine is closed")
        self._thread.start()
        self._started = True
        try:
            pages = asyncio.run_coroutine_threadsafe(
                self._driver.start(self._tab_count), self._loop
            ).result(timeout=self._op_timeout_s)
        except BaseException:
            self.close()
            raise
        if not isinstance(pages, list) or len(pages) != self._tab_count:
            self.close()
            raise RuntimeError(
                f"driver returned {len(pages) if isinstance(pages, list) else '?'} "
                f"tabs; expected {self._tab_count}")
        self._pages = pages
        return self

    @property
    def pages(self) -> list[Any]:
        return list(self._pages)

    # ── synchronous per-tab bridge (BrowserBackend semantics) ────────────────
    def open_conversation(self, page: Any) -> None:
        self._ensure_live()
        self._await(self._driver.open_conversation(page))

    def send(self, page: Any, prompt: str) -> None:
        self._ensure_live()
        self._await(self._driver.send(page, prompt))

    def wait_response(self, page: Any, *, timeout_s: float) -> str:
        self._ensure_live()
        # Generation is the one operation intentionally allowed to run for
        # hours.  The old generic 900-second bridge timeout killed the Future
        # at 15 minutes even when BrowserChatGPTRunner requested the configured
        # 10-hour response ceiling.  Leave one minute for the driver's final
        # stable-text settlement after its own generation deadline.
        return self._await(
            self._driver.wait_response(page, timeout_s=timeout_s),
            timeout_s=float(timeout_s) + 60.0,
        )

    def conversation_url(self, page: Any) -> str:
        self._ensure_live()
        return self._await(self._driver.conversation_url(page))

    def is_rate_limited(self, page: Any) -> bool:
        self._ensure_live()
        return bool(self._await(self._driver.is_rate_limited(page)))

    def dismiss_rate_limit(self, page: Any) -> bool:
        self._ensure_live()
        return bool(self._await(self._driver.dismiss_rate_limit(page)))

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._started:
            try:
                asyncio.run_coroutine_threadsafe(
                    self._driver.close(), self._loop
                ).result(timeout=self._op_timeout_s)
            except BaseException:  # noqa: BLE001 - best-effort teardown
                pass
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join(timeout=self._op_timeout_s)
        else:
            self._loop.close()

    def __enter__(self) -> "AsyncBrowserEngine":
        return self.start()

    def __exit__(self, *_exc: object) -> None:
        self.close()


class TabBackend:
    """A synchronous :class:`BrowserBackend` bound to one tab of a shared engine.

    Each concurrent worker holds its own ``TabBackend`` (its own page); teardown
    is owned by the engine, so an individual tab is never closed on its own.
    """

    def __init__(self, engine: AsyncBrowserEngine, page: Any) -> None:
        self._engine = engine
        self._page = page

    def open_conversation(self) -> None:
        self._engine.open_conversation(self._page)

    def send(self, prompt: str) -> None:
        self._engine.send(self._page, prompt)

    def wait_response(self, *, timeout_s: float) -> str:
        return self._engine.wait_response(self._page, timeout_s=timeout_s)

    def conversation_url(self) -> str:
        return self._engine.conversation_url(self._page)

    def is_rate_limited(self) -> bool:
        return self._engine.is_rate_limited(self._page)

    def dismiss_rate_limit(self) -> bool:
        return self._engine.dismiss_rate_limit(self._page)

    def close(self) -> None:
        # The engine owns the browser + all tabs; a single tab is not torn down.
        return None


def build_browser_runner_pool(
    engine: AsyncBrowserEngine, *, throttle: SharedThrottle | None = None,
    **runner_kwargs: Any,
) -> list[BrowserChatGPTRunner]:
    """Build one :class:`BrowserChatGPTRunner` per tab of a started engine.

    Every runner drives a distinct tab through its own :class:`TabBackend` but
    shares the cross-worker :class:`SharedThrottle`, so the pool coordinates
    cooldowns on the single underlying account. Runner ids are made distinct so
    per-tab transcripts never collide.
    """
    runner_kwargs.pop("backend", None)
    runner_kwargs.pop("throttle", None)
    base_id = runner_kwargs.pop("runner_id", "browser-chatgpt")
    return [
        BrowserChatGPTRunner(
            backend=TabBackend(engine, page),
            runner_id=f"{base_id}-tab{index}",
            throttle=throttle,
            **runner_kwargs,
        )
        for index, page in enumerate(engine.pages)
    ]


class PlaywrightAsyncPageDriver:  # pragma: no cover - requires an authenticated browser
    """Live :class:`AsyncPageDriver` over one persistent Chromium (N tabs).

    A faithful async port of the sync ``chatgpt_browser`` helpers: one persistent
    context (shared authenticated profile), ``tab_count`` pages, prompt submission
    via the synthetic-paste ProseMirror path, generation-start/settle detection,
    conversation-URL capture, and rate-limit handling. Reachable only with an
    authenticated profile (set ``CHATGPT_PROFILE_DIR`` and log in once); it is
    verified live, never in CI — the same posture as the sync backend.
    """

    def __init__(self, *, headless: bool = False, generation_poll_s: float = 1.0,
                 generation_start_timeout_s: float = 30.0,
                 stable_polls: int = 2) -> None:
        self.headless = headless
        self.generation_poll_s = generation_poll_s
        self.generation_start_timeout_s = generation_start_timeout_s
        self.stable_polls = max(1, int(stable_polls))
        self._pw = None
        self._context = None
        self._start_urls: dict[int, str] = {}

    async def start(self, tab_count: int) -> list[Any]:
        from playwright.async_api import async_playwright

        from egmra.agents import chatgpt_browser as cb

        self._cb = cb
        self._pw = await async_playwright().start()
        self._context = await self._pw.chromium.launch_persistent_context(
            user_data_dir=str(cb.profile_dir()),
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"],
            no_viewport=False,
            viewport={"width": 1280, "height": 900},
        )
        pages: list[Any] = []
        for index in range(tab_count):
            page = self._context.pages[0] if (index == 0 and self._context.pages) \
                else await self._context.new_page()
            pages.append(page)
        # Authenticate once on the first tab (the profile is shared across tabs).
        await pages[0].goto(cb.CHATGPT_URL, wait_until="domcontentloaded")
        if "login" in pages[0].url or "auth" in pages[0].url:
            raise RuntimeError(
                "ChatGPT browser profile is not logged in; authenticate the profile "
                "once before using --provider browser --workers N")
        return pages

    async def _current_url(self, page: Any) -> str:
        try:
            return await page.evaluate("() => location.href")
        except Exception:
            try:
                return page.url
            except Exception:
                return ""

    async def open_conversation(self, page: Any) -> None:
        await page.goto(self._cb.PROJECT_URL, wait_until="domcontentloaded")
        selectors = (
            '#prompt-textarea', '[data-testid="prompt-textarea"]',
            'div[contenteditable="true"]', 'textarea[placeholder]',
        )
        # ``domcontentloaded`` fires well before the React composer is mounted.
        # Returning immediately made all N tabs race into ``send`` and burn the
        # campaign retry budget on a normal page-load delay.  Wait for a visible
        # composer just as the synchronous backend does, but with an explicit
        # bounded failure when the project/login page never becomes usable.
        try:
            await page.wait_for_selector(
                ", ".join(selectors), state="visible", timeout=30_000,
            )
        except Exception:  # noqa: BLE001 - normalize Playwright timeout variants
            pass
        if not any([await page.query_selector(sel) for sel in selectors]):
            raise RuntimeError(
                "Could not find ChatGPT input box after waiting for the page composer"
            )
        self._start_urls[id(page)] = await self._current_url(page)

    async def send(self, page: Any, prompt: str) -> None:
        box = None
        for sel in ('#prompt-textarea', '[data-testid="prompt-textarea"]',
                    'div[contenteditable="true"]', 'textarea[placeholder]'):
            box = await page.query_selector(sel)
            if box:
                break
        if box is None:
            raise RuntimeError("Could not find ChatGPT input box")
        await box.evaluate(
            """(el, text) => {
                el.focus();
                if (el.value !== undefined) {
                    const setter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value').set;
                    setter.call(el, text);
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                } else {
                    const dt = new DataTransfer();
                    dt.setData('text/plain', text);
                    el.dispatchEvent(new ClipboardEvent('paste',
                        {clipboardData: dt, bubbles: true, cancelable: true}));
                }
            }""",
            prompt,
        )
        start_url = self._start_urls.get(id(page), "")
        for _attempt in range(3):
            btn = await page.query_selector(
                '[data-testid="send-button"], button[aria-label*="send" i]')
            if btn:
                await btn.evaluate("el => el.click()")
            else:
                await page.keyboard.press("Enter")
            for _ in range(10):
                url = await self._current_url(page)
                if "/c/" in url and url != start_url:
                    return
                await asyncio.sleep(0.5)

    async def _last_reply_text(self, page: Any) -> str:
        msgs = await page.query_selector_all('[data-message-author-role="assistant"]')
        if msgs:
            return (await msgs[-1].inner_text()) or ""
        blocks = await page.query_selector_all('.markdown')
        if blocks:
            return (await blocks[-1].inner_text()) or ""
        return ""

    async def wait_response(self, page: Any, *, timeout_s: float) -> str:
        loop = asyncio.get_running_loop()
        start_deadline = loop.time() + min(self.generation_start_timeout_s, timeout_s)
        while loop.time() < start_deadline:
            if (await page.query_selector('[data-testid="stop-button"]')
                    or (await self._last_reply_text(page)).strip()):
                break
            await asyncio.sleep(0.4)
        deadline = loop.time() + timeout_s
        previous = ""
        stable = 0
        while loop.time() < deadline:
            if await page.query_selector('[data-testid="stop-button"]'):
                previous, stable = "", 0
                await asyncio.sleep(self.generation_poll_s)
                continue
            text = await self._last_reply_text(page)
            if text.strip() and text == previous:
                stable += 1
                if stable >= self.stable_polls:
                    return text
            else:
                previous, stable = text, 0
            await asyncio.sleep(self.generation_poll_s)
        text = await self._last_reply_text(page)
        return text if text.strip() else "[Could not extract response]"

    async def conversation_url(self, page: Any) -> str:
        start_url = self._start_urls.get(id(page), "")
        loop = asyncio.get_running_loop()
        deadline = loop.time() + 30.0
        while loop.time() < deadline:
            url = await self._current_url(page)
            if "/c/" in url:
                return url
            if start_url and url != start_url and url not in ("", "about:blank"):
                return url
            await asyncio.sleep(0.5)
        return await self._current_url(page)

    async def is_rate_limited(self, page: Any) -> bool:
        try:
            if await page.query_selector(
                    '[data-testid="modal-conversation-history-rate-limit"], '
                    '[id*="rate-limit" i]'):
                return True
            body_text = (await page.inner_text("body") or "").lower()
        except Exception:
            return False
        return any(p in body_text for p in self._cb.RATE_LIMIT_PHRASES)

    async def dismiss_rate_limit(self, page: Any) -> bool:
        try:
            for btn in await page.query_selector_all('button, [role="button"]'):
                label = ((await btn.inner_text()) or "").strip().lower()
                if label in ("got it", "ok", "okay", "dismiss", "close", "try again"):
                    await btn.evaluate("el => el.click()")
                    return True
            if await page.query_selector('[role="dialog"], '
                                         '[data-testid="modal-conversation-history-rate-limit"]'):
                await page.keyboard.press("Escape")
                return True
        except Exception:
            pass
        return False

    async def close(self) -> None:
        try:
            if self._context is not None:
                await self._context.close()
        finally:
            if self._pw is not None:
                await self._pw.stop()
            self._context = None
            self._pw = None
