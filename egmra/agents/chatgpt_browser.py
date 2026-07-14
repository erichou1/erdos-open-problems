"""Self-contained ChatGPT browser glue (vendored from ``erdos_common``).

The packaged browser adapter must not import the repository's loose top-level
``erdos_common`` module, or a wheel installed outside the checkout would break.
This module re-implements exactly the Playwright helpers the browser backend
needs — profile launch, login check, prompt submission via a synthetic paste,
conversation-URL capture, generation-start/settle detection, and rate-limit
handling — with no dependency on the repository root.

Only :func:`is_conversation_url` is a pure function exercised by tests; the
page-driving helpers require a live authenticated browser and are marked
no-cover.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from urllib.parse import urlparse

CHATGPT_URL = "https://chatgpt.com"
PROJECT_URL = os.environ.get("CHATGPT_PROJECT_URL", "https://chatgpt.com")


def profile_dir() -> Path:
    """Chromium persistent-profile directory (configurable via env)."""
    return Path(os.environ.get("CHATGPT_PROFILE_DIR", str(Path.cwd() / ".chatgpt_profile")))


# Phrases that indicate ChatGPT is rate-limiting / refusing to generate.
RATE_LIMIT_PHRASES = [
    "you've reached our limit of messages",
    "you've hit the free plan limit",
    "you're sending messages too quickly",
    "too many requests",
]


def is_conversation_url(url: str, start_url: str = "") -> bool:
    """Validate classic and project-scoped ChatGPT conversation routes."""
    if not url:
        return False
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {"chatgpt.com", "www.chatgpt.com"}:
        return False
    if "/c/" in parsed.path:
        return True
    if start_url:
        return url != start_url and url != "about:blank"
    return url.rstrip("/") != PROJECT_URL.rstrip("/") and parsed.path not in {"", "/"}


def launch_browser(pw, *, headless: bool = False):  # pragma: no cover - needs a browser
    return pw.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir()),
        headless=headless,
        args=["--disable-blink-features=AutomationControlled"],
        no_viewport=False,
        viewport={"width": 1280, "height": 900},
    )


def ensure_logged_in(page) -> None:  # pragma: no cover - needs a browser
    page.goto(CHATGPT_URL, wait_until="domcontentloaded")
    time.sleep(3)
    if "login" in page.url or "auth" in page.url:
        raise RuntimeError(
            "ChatGPT browser profile is not logged in; authenticate the profile once "
            "(e.g. python3 solve_submit.py --login) before using --provider browser"
        )


def current_url(page) -> str:  # pragma: no cover - needs a browser
    try:
        return page.evaluate("() => location.href")
    except Exception:
        try:
            return page.url
        except Exception:
            return ""


def is_generating(page) -> bool:  # pragma: no cover - needs a browser
    try:
        return page.query_selector('[data-testid="stop-button"]') is not None
    except Exception:
        return False


def extract_response(page) -> str:  # pragma: no cover - needs a browser
    try:
        msgs = page.query_selector_all('[data-message-author-role="assistant"]')
        if msgs:
            return msgs[-1].inner_text()
        blocks = page.query_selector_all('.markdown')
        if blocks:
            return blocks[-1].inner_text()
    except Exception:
        pass
    return "[Could not extract response]"


def detect_rate_limit(page) -> bool:  # pragma: no cover - needs a browser
    try:
        if page.query_selector(
                '[data-testid="modal-conversation-history-rate-limit"], '
                '[id*="rate-limit" i]'):
            return True
    except Exception:
        pass
    try:
        body_text = (page.inner_text("body") or "").lower()
    except Exception:
        return False
    return any(p in body_text for p in RATE_LIMIT_PHRASES)


def dismiss_rate_limit_modal(page) -> bool:  # pragma: no cover - needs a browser
    try:
        for btn in page.query_selector_all('button, [role="button"]'):
            try:
                label = (btn.inner_text() or "").strip().lower()
            except Exception:
                continue
            if label in ("got it", "ok", "okay", "dismiss", "close", "try again"):
                try:
                    page.evaluate("el => el.click()", btn)
                    time.sleep(0.5)
                    return True
                except Exception:
                    pass
        if page.query_selector('[role="dialog"], '
                               '[data-testid="modal-conversation-history-rate-limit"]'):
            page.keyboard.press("Escape")
            time.sleep(0.5)
            return True
    except Exception:
        pass
    return False


def start_new_chat(page) -> None:  # pragma: no cover - needs a browser
    page.goto(PROJECT_URL, wait_until="domcontentloaded")
    time.sleep(2.5)
    for sel in ['#prompt-textarea', '[data-testid="prompt-textarea"]',
                'div[contenteditable="true"]']:
        if page.query_selector(sel):
            break
    else:
        time.sleep(2)


def send_prompt(page, prompt_text: str) -> None:  # pragma: no cover - needs a browser
    box = None
    for sel in ['#prompt-textarea', '[data-testid="prompt-textarea"]',
                'div[contenteditable="true"]', 'textarea[placeholder]']:
        box = page.query_selector(sel)
        if box:
            break
    if box is None:
        raise RuntimeError("Could not find ChatGPT input box")

    page.evaluate("el => el.focus()", box)
    time.sleep(0.3)
    tag = box.evaluate("el => el.tagName.toLowerCase()")
    if tag == "textarea":
        page.evaluate(
            """(args) => {
                const [el, text] = args;
                const setter = Object.getOwnPropertyDescriptor(
                    window.HTMLTextAreaElement.prototype, 'value').set;
                setter.call(el, text);
                el.dispatchEvent(new Event('input', {bubbles: true}));
            }""",
            [box, prompt_text],
        )
    else:
        page.evaluate("el => el.focus()", box)
        time.sleep(0.2)
        page.keyboard.press("Meta+A")
        page.keyboard.press("Delete")
        time.sleep(0.1)
        page.evaluate(
            """(args) => {
                const [el, text] = args;
                el.focus();
                const dt = new DataTransfer();
                dt.setData('text/plain', text);
                el.dispatchEvent(new ClipboardEvent('paste',
                    {clipboardData: dt, bubbles: true, cancelable: true}));
            }""",
            [box, prompt_text],
        )

    deadline = time.time() + 5
    while time.time() < deadline:
        if box.evaluate(
            "el => (el.value !== undefined ? el.value : el.innerText).trim().length > 0"
        ):
            break
        time.sleep(0.2)

    start_url = current_url(page)

    def _box_has_text():
        try:
            return box.evaluate(
                "el => (el.value !== undefined ? el.value : el.innerText).trim().length > 0"
            )
        except Exception:
            return False

    def _click_send():
        btn = page.query_selector('[data-testid="send-button"], button[aria-label*="send" i]')
        if btn:
            try:
                page.evaluate("el => el.click()", btn)
                return
            except Exception:
                pass
        page.keyboard.press("Enter")

    for _attempt in range(3):
        time.sleep(0.4)
        _click_send()
        for _ in range(10):
            time.sleep(0.5)
            if "/c/" in current_url(page) and current_url(page) != start_url:
                return
            if not _box_has_text():
                return
        try:
            page.evaluate("el => el.focus()", box)
        except Exception:
            pass


def wait_for_generation_start(page, *, timeout_s: float = 30.0) -> bool:  # pragma: no cover
    """Wait until generation visibly begins (stop-button appears)."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if is_generating(page):
            return True
        time.sleep(0.4)
    return False


def wait_for_conversation_url(page, timeout_s: int = 30,
                              start_url: str = "") -> str:  # pragma: no cover - needs a browser
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        url = current_url(page)
        if "/c/" in url:
            return url
        if start_url and url != start_url and url not in ("", "about:blank"):
            return url
        time.sleep(0.5)
    return current_url(page)
