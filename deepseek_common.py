#!/usr/bin/env python3
"""
Shared helpers for the DeepSeek automation scripts.

Reuses the prompt, problem-file parsing and answer-classification from
erdos_common, but provides DeepSeek-specific browser/page automation.

DeepSeek web has no "projects", so each problem just starts a new chat at the
root. Conversation URLs look like https://chat.deepseek.com/a/chat/s/<id>.
"""

import json
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright  # noqa: F401  (re-exported)

# Reuse everything generic from the ChatGPT module
from erdos_common import (  # noqa: F401
    REPO_DIR,
    PROMPT_TEMPLATE,
    REFUSAL_PHRASES,
    extract_problem_statement,
    problem_number,
    get_problem_files,
    is_solved,
    extract_confidence,
    extract_completeness,
    output_title,
    save_output,
    restore_output_from_solution,
)

# ── DeepSeek-specific paths / URLs ────────────────────────────────────────────
DS_PROFILE_DIR   = Path(__file__).resolve().parent / ".deepseek_profile"
DS_CHAT_MAP_FILE = Path(__file__).resolve().parent / ".deepseek_chat_map.json"

DEEPSEEK_URL = "https://chat.deepseek.com"

RATE_LIMIT_PHRASES = [
    "rate limit", "too many requests", "please wait", "try again later",
    "server is busy", "the server is busy", "you are sending messages too",
]


# ── Chat-map persistence ──────────────────────────────────────────────────────

def load_chat_map() -> dict:
    if DS_CHAT_MAP_FILE.exists():
        return json.loads(DS_CHAT_MAP_FILE.read_text())
    return {}


def save_chat_map(m: dict):
    DS_CHAT_MAP_FILE.write_text(json.dumps(m, indent=2))


# ── Browser ───────────────────────────────────────────────────────────────────

def launch_browser(pw, headless=False):
    return pw.chromium.launch_persistent_context(
        user_data_dir=str(DS_PROFILE_DIR),
        headless=headless,
        args=["--disable-blink-features=AutomationControlled"],
        no_viewport=False,
        viewport={"width": 1280, "height": 900},
    )


def ensure_logged_in(page):
    page.goto(DEEPSEEK_URL, wait_until="domcontentloaded")
    time.sleep(3)
    # DeepSeek shows a login form if not authenticated
    if "login" in page.url.lower() or "sign_in" in page.url.lower():
        raise SystemExit(
            "Not logged in to DeepSeek! Run with --login first:\n"
            "  python3 deepseek_submit.py --login"
        )


# ── Page helpers ──────────────────────────────────────────────────────────────

# Candidate selectors (DeepSeek's UI changes; we try several).
INPUT_SELECTORS = [
    'textarea[placeholder]',
    'textarea#chat-input',
    'div[contenteditable="true"]',
    'textarea',
]
# The send button is the bottom-right primary filled circle button.
SEND_SELECTORS = [
    'div.ds-button--primary.ds-button--filled.ds-button--circle',
    'div[role="button"][aria-label*="send" i]',
    'button[aria-label*="send" i]',
]


def find_input(page):
    for sel in INPUT_SELECTORS:
        el = page.query_selector(sel)
        if el:
            return el
    return None


def is_generating(page) -> bool:
    """
    Detect whether DeepSeek is still streaming a response.

    DeepThink reasoning has no reliable stop-button aria-label, so the robust
    signal is content growth: sample the assistant text, wait briefly, and see
    if it changed. Also treat a visible stop control as generating.
    """
    try:
        for sel in ['div[role="button"][aria-label*="stop" i]',
                    'button[aria-label*="stop" i]',
                    'div[aria-label*="stop" i]']:
            if page.query_selector(sel):
                return True
    except Exception:
        pass
    # Content-growth check (works for both thinking trace and answer streaming)
    try:
        def _len():
            return page.evaluate(
                """() => {
                    let n = 0;
                    for (const el of document.querySelectorAll('.ds-markdown, .ds-think-content')) {
                        n += (el.innerText || '').length;
                    }
                    return n;
                }"""
            )
        a = _len()
        time.sleep(2.5)
        b = _len()
        return b != a
    except Exception:
        return False


def extract_response(page) -> str:
    """
    Grab the final assistant ANSWER from the DeepSeek transcript.

    In DeepThink mode the assistant message contains a reasoning trace inside
    `.ds-think-content` followed by the actual answer in one or more
    `.ds-markdown` blocks that are NOT inside the think-content. We want the
    answer, not the reasoning. If no answer block exists yet (e.g. the model is
    still thinking or generation was cut off), return "" so the caller treats
    it as not-ready.
    """
    try:
        text = page.evaluate(
            """() => {
                // Collect all answer markdown blocks (outside the think trace).
                const answer = [];
                for (const el of document.querySelectorAll('.ds-markdown')) {
                    if (el.closest('.ds-think-content')) continue;
                    const t = (el.innerText || '').trim();
                    if (t) answer.push(t);
                }
                if (answer.length) return answer.join('\\n\\n');
                return '';
            }"""
        )
        if text and text.strip():
            return text
        # Fallback for older/non-DeepThink layouts that have NO think-content:
        # the last markdown block is the answer. If a think-content exists but
        # produced no answer block, do NOT fall back (would return reasoning).
        has_think = page.query_selector('.ds-think-content') is not None
        if not has_think:
            blocks = page.query_selector_all('div[class*="markdown" i]')
            if blocks and blocks[-1].inner_text().strip():
                return blocks[-1].inner_text()
    except Exception:
        pass
    return ""


def _find_continue_button(page):
    """
    Locate DeepSeek's "Continue" button shown when a response is truncated
    (e.g. it hit the per-message length cap). Matches English and Chinese
    labels. Returns the element handle or None.
    """
    try:
        return page.evaluate_handle(
            """() => {
                const wants = ['continue generating', 'continue', '继续生成', '继续'];
                const cand = document.querySelectorAll(
                    'div[role="button"], button, span[role="button"], [tabindex]'
                );
                for (const el of cand) {
                    const t = (el.innerText || '').trim().toLowerCase();
                    if (!t || t.length > 24) continue;
                    if (wants.some(w => t === w || t.startsWith('continue'))) {
                        const r = el.getBoundingClientRect();
                        if (r.width > 0 && r.height > 0) return el;
                    }
                }
                return null;
            }"""
        ).as_element()
    except Exception:
        return None


def click_continue_if_needed(page, max_clicks: int = 6, gen_wait_s: int = 240) -> int:
    """
    Repeatedly click DeepSeek's "Continue" button while it appears, waiting for
    each continuation to finish generating. Returns how many times it clicked.

    This must run AFTER generation has stopped (no point clicking mid-stream).
    """
    clicks = 0
    for _ in range(max_clicks):
        btn = _find_continue_button(page)
        if btn is None:
            break
        try:
            _js_click(page, btn)
        except Exception:
            break
        clicks += 1
        time.sleep(2)
        # Wait for the continued generation to finish.
        waited = 0
        while is_generating(page) and waited < gen_wait_s:
            time.sleep(3)
            waited += 3
        time.sleep(1)
    return clicks


def detect_rate_limit(page) -> bool:
    try:
        body_text = (page.inner_text("body") or "").lower()
    except Exception:
        return False
    return any(p in body_text for p in RATE_LIMIT_PHRASES)


def start_new_chat(page):
    """Open a fresh DeepSeek chat at the root."""
    page.goto(DEEPSEEK_URL, wait_until="domcontentloaded")
    time.sleep(2.5)
    # Click a "New chat" control if the previous conversation is still loaded
    for sel in ['a[href="/"]', 'button[aria-label*="new chat" i]',
                'div[class*="new-chat" i]', '[data-testid*="new-chat"]']:
        btn = page.query_selector(sel)
        if btn:
            try:
                page.evaluate("el => el.click()", btn)
                time.sleep(1.0)
            except Exception:
                pass
            break
    # Ensure input is present
    for _ in range(4):
        if find_input(page):
            break
        time.sleep(1)
    # Select Expert model + turn on DeepThink (R1 reasoning) for this chat
    enable_expert(page)
    enable_deepthink(page)


def _find_expert_radio(page):
    """Locate the 'Expert' radio in the Instant/Expert model selector."""
    for sel in ('div[role="radio"][data-model-type="expert"]',
                'div[data-model-type="expert"]'):
        el = page.query_selector(sel)
        if el:
            return el
    # Fallback: match by text
    for el in page.query_selector_all('div[role="radio"]'):
        try:
            if (el.inner_text() or "").strip().lower() == "expert":
                return el
        except Exception:
            pass
    return None


def enable_expert(page, retries: int = 3) -> bool:
    """
    Ensure the 'Expert' model (not 'Instant') is selected. The selector is a
    radiogroup; Expert is `div[role="radio"][data-model-type="expert"]` and is
    active when aria-checked="true".
    Returns True if Expert ends up selected.
    """
    try:
        for _ in range(retries):
            el = _find_expert_radio(page)
            if el is None:
                time.sleep(0.5)
                continue
            if (el.get_attribute("aria-checked") or "").lower() == "true":
                return True
            try:
                page.evaluate("el => el.click()", el)
            except Exception:
                try:
                    el.click()
                except Exception:
                    pass
            time.sleep(0.6)
            el2 = _find_expert_radio(page)
            if el2 and (el2.get_attribute("aria-checked") or "").lower() == "true":
                return True
        el = _find_expert_radio(page)
        return bool(el and (el.get_attribute("aria-checked") or "").lower() == "true")
    except Exception as e:
        print(f"  WARN: could not select Expert mode: {e}")
        return False


def _toggle_is_on(el) -> bool:
    """
    Determine whether a DeepSeek mode pill is active. DeepSeek marks the active
    toggle with the class `ds-toggle-button--selected` and aria-pressed=true.
    """
    try:
        cls = (el.get_attribute("class") or "").lower()
        if "ds-toggle-button--selected" in cls or "--selected" in cls:
            return True
        pressed = (el.get_attribute("aria-pressed") or "").lower()
        if pressed == "true":
            return True
        if pressed == "false":
            return False
        return False
    except Exception:
        return False


def _find_deepthink_button(page):
    """Locate the DeepThink (R1) toggle pill near the input box."""
    # DeepSeek's toggle is a div.ds-toggle-button (no role=button), so also
    # search that class explicitly.
    selectors = (
        '.ds-toggle-button, div[role="button"], button, span[role="button"], '
        '[tabindex]'
    )
    for el in page.query_selector_all(selectors):
        try:
            label = (el.inner_text() or "").lower()
        except Exception:
            label = ""
        aria = (el.get_attribute("aria-label") or "").lower()
        text = label + " " + aria
        if "deepthink" in text or "deep think" in text or "r1" in text:
            return el
    return None


def enable_deepthink(page, retries: int = 3) -> bool:
    """
    Ensure DeepThink (R1) mode is ON. Clicks the toggle if it is off and
    verifies the state actually changed (retrying up to `retries` times).
    Returns True if DeepThink ends up enabled.
    """
    try:
        for _ in range(retries):
            btn = _find_deepthink_button(page)
            if btn is None:
                time.sleep(0.5)
                continue
            if _toggle_is_on(btn):
                return True
            # Click to turn it on
            try:
                page.evaluate("el => el.click()", btn)
            except Exception:
                try:
                    btn.click()
                except Exception:
                    pass
            time.sleep(0.7)
            # Re-fetch (DOM may have re-rendered) and verify
            btn2 = _find_deepthink_button(page)
            if btn2 and _toggle_is_on(btn2):
                return True
        # Last check
        btn = _find_deepthink_button(page)
        return bool(btn and _toggle_is_on(btn))
    except Exception as e:
        print(f"  WARN: could not enable DeepThink: {e}")
        return False


def send_prompt(page, prompt_text: str):
    """Type and submit a prompt to DeepSeek (JS-based to avoid pointer issues)."""
    # Make sure Expert model + DeepThink (R1) are enabled before sending
    enable_expert(page)
    enable_deepthink(page)

    box = find_input(page)
    if box is None:
        raise RuntimeError("Could not find DeepSeek input box")

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
        page.evaluate(
            """(args) => {
                const [el, text] = args;
                el.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('insertText', false, text);
            }""",
            [box, prompt_text],
        )

    time.sleep(0.5)

    # Try the send button; fall back to Enter
    sent = False
    for sel in SEND_SELECTORS:
        btn = page.query_selector(sel)
        if btn:
            try:
                page.evaluate("el => el.click()", btn)
                sent = True
                break
            except Exception:
                continue
    if not sent:
        page.keyboard.press("Enter")


def wait_for_conversation_url(page, timeout_s: int = 30) -> str:
    """
    After submitting, wait until the URL becomes a concrete conversation AND
    has settled to its permanent id.

    DeepSeek first shows a transient chat id in the URL, then swaps it to a
    permanent id a few seconds later. The transient id is dead (navigating to
    it later redirects to '/'), so we must wait for the URL to stop changing
    before recording it.
    """
    deadline = time.time() + timeout_s
    last_url = None
    stable_since = None
    settle_s = 4.0  # require the URL to be unchanged this long before trusting it

    while time.time() < deadline:
        url = page.url
        is_conv = ("/chat/s/" in url) or ("/a/chat/" in url)
        if is_conv:
            if url == last_url:
                if stable_since and (time.time() - stable_since) >= settle_s:
                    return url
            else:
                last_url = url
                stable_since = time.time()
        time.sleep(0.5)

    return last_url or page.url



# ── Rename ────────────────────────────────────────────────────────────────────

def _js_click(page, element):
    page.evaluate("el => el.click()", element)


def _js_hover(page, element):
    page.evaluate(
        """el => {
            el.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
            el.dispatchEvent(new MouseEvent('mouseover',  {bubbles: true}));
        }""",
        element,
    )


def rename_chat(page, title: str) -> bool:
    """
    Rename the currently-open DeepSeek conversation.

    The active sidebar item is the anchor `a._546d736` whose href contains the
    current chat id (it also carries an extra `b64fb9ae` class). Hovering it
    reveals a `div[role="button"]` ("...") that opens a dropdown with
    `.ds-dropdown-menu-option` entries (Rename / Pin / Share / Delete).
    """
    try:
        page.set_default_timeout(8_000)
        time.sleep(0.3)

        # Locate the active conversation item by its chat id in the href.
        cur = page.url.rstrip("/")
        cid = cur.split("/")[-1] if ("/chat/s/" in cur or "/a/chat/" in cur) else ""
        item = None
        if cid:
            item = page.query_selector(f'a[href*="{cid}"]')
        if item is None:
            item = page.query_selector('a._546d736.b64fb9ae')
        if item is None:
            print("  WARN: could not locate active DeepSeek chat")
            return False

        # Hover near the right edge to reveal the options ("...") button.
        box = item.bounding_box()
        if box:
            page.mouse.move(box["x"] + box["width"] - 18, box["y"] + box["height"] / 2)
            time.sleep(0.5)

        opt = item.query_selector('div[role="button"]')
        if opt is None:
            print("  WARN: DeepSeek options button not found")
            return False
        ob = opt.bounding_box()
        if ob:
            page.mouse.click(ob["x"] + ob["width"] / 2, ob["y"] + ob["height"] / 2)
        else:
            _js_click(page, opt)
        time.sleep(0.6)

        # Click "Rename" in the dropdown menu.
        rename_item = None
        for el in page.query_selector_all('.ds-dropdown-menu-option'):
            if (el.inner_text() or "").strip().lower().startswith("rename"):
                rename_item = el
                break
        if rename_item is None:
            print("  WARN: DeepSeek Rename item not found")
            page.keyboard.press("Escape")
            return False
        _js_click(page, rename_item)
        time.sleep(0.5)

        # An editable input replaces the title; fill it and confirm.
        editable = page.query_selector(
            'input:focus, [contenteditable="true"]:focus, input[type="text"], input'
        )
        if editable is None:
            print("  WARN: DeepSeek rename input not found")
            page.keyboard.press("Escape")
            return False
        try:
            editable.fill(title)
        except Exception:
            editable.click()
            page.keyboard.press("Meta+A")
            page.keyboard.insert_text(title)
        editable.press("Enter")
        time.sleep(0.4)
        return True

    except Exception as e:
        print(f"  WARN: DeepSeek rename failed (non-fatal): {e}")
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        return False
    finally:
        try:
            page.set_default_timeout(30_000)
        except Exception:
            pass

