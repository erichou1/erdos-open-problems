"""Kimi (Moonshot AI) browser provider: an async multi-tab page driver.

The user's direction is to drive Kimi through its web UI (kimi.com) exactly
like the primary ChatGPT browser provider — an authenticated persistent
Chromium profile, synthetic-paste prompt submission, and settle-detection on
the streamed reply. Kimi is a *weaker* model than the primary provider, so
campaigns allocate it the easier lanes (e.g. ``--triage-lane t2_closable``);
nothing in this module encodes that policy — allocation is an operator choice.

Trust posture is identical to the ChatGPT browser provider: a UI label can
never prove which model produced text, so every emitted identity is
UNATTESTED. Kimi tabs can therefore never manufacture independent-model
evidence, and hostile reviews driven from Kimi tabs collapse to the single
``unattested-model`` lineage (D-013).

Selector strategy (live-verified against kimi.com 2026-07): the composer is a
ProseMirror-style ``div.chat-input-editor[contenteditable="true"]`` that
accepts the same synthetic-paste path ChatGPT needs, and submission is a
``div.send-button-container`` click (Enter as fallback). Reply settlement uses
generation-indicator polling with a text-stability fallback so a DOM drift in
Kimi's stop button degrades to a slower-but-honest settle instead of a
truncated response.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

KIMI_URL = os.environ.get("KIMI_URL", "https://www.kimi.com/")

#: Composer selectors, most specific first (live-verified 2026-07).
COMPOSER_SELECTORS = (
    "div.chat-input-editor",
    '[data-testid="msh-chatinput-editor"]',
    'div[contenteditable="true"]',
    "textarea[placeholder]",
)

#: Send-control selectors (the live control is a DIV, not a BUTTON).
SEND_SELECTORS = (
    "div.send-button-container",
    '[data-testid="msh-chatinput-send-button"]',
    'button[aria-label*="send" i]',
)

#: Generation-in-progress indicators; absence + stable text = settled.
STOP_SELECTORS = (
    ".stop-message-btn",
    '[data-testid="msh-chat-stop-button"]',
    'button[aria-label*="stop" i]',
    '[class*="stop-btn"]',
)

#: Assistant reply containers, most specific first.
ASSISTANT_SELECTORS = (
    '[data-testid="msh-chat-segment-assistant"]',
    '[class*="chat-content-item-assistant"]',
    '[class*="segment-assistant"]',
    ".markdown",
    '[class*="assistant"]',
)

#: Substrings (lowercased body text) that indicate a throttle/usage limit.
RATE_LIMIT_PHRASES = (
    "too many requests",
    "rate limit",
    "usage limit",
    "reached the limit",
    "try again later",
    "high demand",
    "服务器繁忙",
    "操作频繁",
)

#: Marker present in conversation URLs once a chat exists.
CONVERSATION_URL_MARKER = "/chat/"

_LOGIN_BUTTON_SELECTOR = 'button:has-text("Log In"), button:has-text("Log in")'


def kimi_profile_dir() -> Path:
    """Chromium persistent-profile directory for Kimi (configurable via env)."""
    return Path(os.environ.get("KIMI_PROFILE_DIR", str(Path.cwd() / ".kimi_profile")))


class KimiAsyncPageDriver:  # pragma: no cover - requires an authenticated browser
    """Live :class:`~egmra.agents.async_browser.AsyncPageDriver` for kimi.com.

    One persistent authenticated Chromium (``kimi_profile_dir()``), ``tab_count``
    pages, prompt submission via the synthetic-paste contenteditable path, and
    settle detection via generation indicators with a text-stability fallback.
    Reachable only with an authenticated profile (log in once headed); verified
    live, never in CI — the same posture as the ChatGPT drivers.
    """

    def __init__(self, *, headless: bool = False, generation_poll_s: float = 2.0,
                 generation_start_timeout_s: float = 30.0,
                 stable_polls: int = 3) -> None:
        self.headless = headless
        self.generation_poll_s = generation_poll_s
        self.generation_start_timeout_s = generation_start_timeout_s
        self.stable_polls = max(2, int(stable_polls))
        self._pw = None
        self._context = None
        self._start_urls: dict[int, str] = {}

    async def start(self, tab_count: int) -> list[Any]:
        from playwright.async_api import async_playwright

        self._pw = await async_playwright().start()
        self._context = await self._pw.chromium.launch_persistent_context(
            user_data_dir=str(kimi_profile_dir()),
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"],
            no_viewport=False,
            viewport={"width": 1280, "height": 900},
        )
        pages: list[Any] = []
        for index in range(tab_count):
            page = (self._context.pages[0]
                    if (index == 0 and self._context.pages)
                    else await self._context.new_page())
            pages.append(page)
        await pages[0].goto(KIMI_URL, wait_until="domcontentloaded")
        try:
            await pages[0].wait_for_selector(
                ", ".join(COMPOSER_SELECTORS), state="visible", timeout=30_000)
        except Exception:  # noqa: BLE001 - login check below gives the real error
            pass
        if await pages[0].query_selector(_LOGIN_BUTTON_SELECTOR):
            raise RuntimeError(
                "Kimi browser profile is not logged in; open the profile once "
                "headed and complete login (see AGENT_SETUP.md kimi login step) "
                "before using --provider kimi-browser")
        return pages

    async def _current_url(self, page: Any) -> str:
        try:
            return await page.evaluate("() => location.href")
        except Exception:
            try:
                return page.url
            except Exception:
                return ""

    async def _find_first(self, page: Any, selectors: tuple[str, ...]) -> Any:
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
            except Exception:
                continue
            if element:
                return element
        return None

    async def open_conversation(self, page: Any) -> None:
        await page.goto(KIMI_URL, wait_until="domcontentloaded")
        try:
            await page.wait_for_selector(
                ", ".join(COMPOSER_SELECTORS), state="visible", timeout=30_000)
        except Exception:  # noqa: BLE001 - normalized to the explicit check below
            pass
        if await self._find_first(page, COMPOSER_SELECTORS) is None:
            raise RuntimeError(
                "Could not find the Kimi composer after waiting for the page")
        self._start_urls[id(page)] = await self._current_url(page)

    async def send(self, page: Any, prompt: str) -> None:
        box = await self._find_first(page, COMPOSER_SELECTORS)
        if box is None:
            raise RuntimeError("Could not find the Kimi composer")
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
            control = await self._find_first(page, SEND_SELECTORS)
            if control is not None:
                await control.evaluate("el => el.click()")
            else:
                await page.keyboard.press("Enter")
            for _ in range(10):
                url = await self._current_url(page)
                if CONVERSATION_URL_MARKER in url and url != start_url:
                    return
                # A cleared composer also proves submission (URL may lag).
                box = await self._find_first(page, COMPOSER_SELECTORS)
                if box is not None:
                    text = ((await box.inner_text()) or "").strip()
                    if not text:
                        return
                await asyncio.sleep(0.5)

    async def _generating(self, page: Any) -> bool:
        return await self._find_first(page, STOP_SELECTORS) is not None

    async def _last_reply_text(self, page: Any) -> str:
        for selector in ASSISTANT_SELECTORS:
            try:
                elements = await page.query_selector_all(selector)
            except Exception:
                continue
            if elements:
                try:
                    return (await elements[-1].inner_text()) or ""
                except Exception:
                    continue
        return ""

    async def wait_response(self, page: Any, *, timeout_s: float) -> str:
        loop = asyncio.get_running_loop()
        start_deadline = loop.time() + min(self.generation_start_timeout_s, timeout_s)
        while loop.time() < start_deadline:
            if await self._generating(page) or (await self._last_reply_text(page)).strip():
                break
            await asyncio.sleep(0.4)
        deadline = loop.time() + timeout_s
        previous = ""
        stable = 0
        while loop.time() < deadline:
            if await self._generating(page):
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
            if CONVERSATION_URL_MARKER in url:
                return url
            if start_url and url != start_url and url not in ("", "about:blank"):
                return url
            await asyncio.sleep(0.5)
        return await self._current_url(page)

    async def is_rate_limited(self, page: Any) -> bool:
        try:
            body_text = ((await page.inner_text("body")) or "").lower()
        except Exception:
            return False
        return any(phrase in body_text for phrase in RATE_LIMIT_PHRASES)

    async def dismiss_rate_limit(self, page: Any) -> bool:
        try:
            for btn in await page.query_selector_all('button, [role="button"]'):
                label = ((await btn.inner_text()) or "").strip().lower()
                if label in ("got it", "ok", "okay", "dismiss", "close", "try again",
                             "我知道了", "确定"):
                    await btn.evaluate("el => el.click()")
                    return True
            if await page.query_selector('[role="dialog"]'):
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
            self._start_urls = {}
