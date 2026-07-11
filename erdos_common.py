#!/usr/bin/env python3
"""
Shared helpers for the Erdős/ChatGPT automation scripts.

Two scripts use this module:
  - solve_submit.py : opens chats in the project and submits prompts (no waiting)
  - solve_rename.py : revisits each chat, saves the answer, renames the chat

A mapping file (chat_map.json) links each Erdős problem number to the chat URL
that solve_submit created, so solve_rename can navigate directly to it.
"""

import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright  # noqa: F401  (re-exported)
from solver_prompts import CANDIDATE_PROMPT_TEMPLATE
from verification import candidate_status

# ── Load .env (no third-party library needed) ────────────────────────────────
_ENV_FILE = Path(__file__).parent / ".env"
if _ENV_FILE.exists():
    for _line in _ENV_FILE.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# ── Paths ────────────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent


def _detect_repo_dir() -> Path:
    """Locate the directory that holds the problem categories.

    Two layouts are supported transparently:
      * dev layout  — problems live under  <script_dir>/erdos_problems/<category>
      * clone layout — problems live directly at <script_dir>/<category>
    A directory qualifies if it contains a category folder with an
    'individual' subfolder (e.g. open/individual).
    """
    categories = ("open", "falsifiable", "verifiable")
    for base in (_SCRIPT_DIR / "erdos_problems", _SCRIPT_DIR):
        if any((base / c / "individual").is_dir() for c in categories):
            return base
    # Default to the dev layout; fetch scripts will create it.
    return _SCRIPT_DIR / "erdos_problems"


REPO_DIR      = _detect_repo_dir()
PROFILE_DIR   = Path(os.environ.get(
    "CHATGPT_PROFILE_DIR", str(_SCRIPT_DIR / ".chatgpt_profile")))
CHAT_MAP_FILE = _SCRIPT_DIR / ".chatgpt_chat_map.json"

# Human-named output copies live here, one subfolder per platform.
#   outputs/chatgpt/<category>/Erdős #N [candidate-proved] 88%.md
#   outputs/deepseek/<category>/Erdős #N [unsolved] 0%.md
OUTPUTS_DIR   = _SCRIPT_DIR / "outputs"

CHATGPT_URL = "https://chatgpt.com"
# The ChatGPT Project URL is set in .env (CHATGPT_PROJECT_URL=...).
# Edit .env to change it. Falls back to plain chatgpt.com if not set.
PROJECT_URL = os.environ.get("CHATGPT_PROJECT_URL", "https://chatgpt.com")

# ── Prompt ───────────────────────────────────────────────────────────────────
PROMPT_TEMPLATE = """\
You are investigating Erdős Problem #{problem_number}.

Canonical problem page:
{problem_url}

Locally extracted statement:

<problem_statement>
{problem}
</problem_statement>

Your goal is to investigate and attempt the intended mathematical research
problem. Do not solve only an accidentally literal, weakened, malformed, or
context-free interpretation of the extracted sentence.

You are expected to use web search and relevant mathematical literature.

PHASE 1 — IDENTIFY THE INTENDED PROBLEM

1. Open the canonical Erdős Problems page.
2. Read the complete statement, remarks, definitions, comments, references,
   related problems, and linked sources.
3. Search for the original source and relevant later literature, including
   papers, surveys, books, preprints, and serious mathematical discussions.
4. Determine the intended interpretation of all potentially ambiguous parts:
   - quantifier order;
   - parameter dependencies;
   - standard conventions;
   - the class of admissible objects;
   - whether constants are absolute or parameter-dependent;
   - whether the displayed statement abbreviates a standard formulation;
   - whether remarks or cited literature clarify the intended claim.
5. Compare the locally extracted statement with the canonical page and the
   literature.
6. Explicitly state whether the literal reading differs from the intended
   research problem.
7. When ambiguity remains, use the interpretation best supported by the
   canonical page, the original source, and subsequent literature. Record any
   unresolved ambiguity.

Do not begin a proof until this interpretation step is complete.

PHASE 2 — LITERATURE MAP

Produce a concise, technically precise account of:

1. the original source of the problem, when identifiable;
2. standard definitions and conventions;
3. known special cases;
4. known upper and lower bounds;
5. equivalent or closely related formulations;
6. the strongest relevant published or publicly available results;
7. known extremal examples, constructions, and obstructions;
8. prior approaches that appear relevant;
9. what remains genuinely unresolved.

Give citations or direct source references for external results.

Do not rely on a theorem merely because its title or summary sounds relevant.
State its hypotheses and verify that they apply.

If the literature already contains a complete solution, explain that clearly,
identify the source, and independently audit the argument rather than claiming
a new solution.

PHASE 3 — FORMALIZE THE TARGET

Write the intended target formally, with all quantifiers and parameter
dependencies explicit.

Separate:

- assumptions and definitions;
- results already known from the literature;
- the exact remaining target;
- stronger and weaker variants;
- interpretation-dependent assumptions.

If the extracted statement differs from the canonical intended formulation,
work on the canonical intended formulation and explain the discrepancy.

PHASE 4 — ATTEMPT THE PROBLEM

Make a serious attempt to prove or disprove the remaining target.

You may use established literature results only after:

1. stating the exact result;
2. identifying its source;
3. checking each hypothesis;
4. explaining exactly how it applies.

Explore multiple approaches when useful, including:

- extremal methods;
- probabilistic methods;
- algebraic methods;
- analytic methods;
- geometric methods;
- number-theoretic methods;
- graph-theoretic or combinatorial reformulations;
- reductions to established theorems;
- constructions and counterexample searches;
- computational experiments used as evidence rather than proof;
- analysis of known extremal examples;
- stronger or weaker intermediate statements.

Do not stop solely because the problem is described as open. Attempt to obtain
the strongest rigorous progress possible.

Do not treat a reduction, analogy, citation, numerical experiment, or plausible
heuristic as a proof.

PHASE 5 — ADVERSARIAL AUDIT

Before giving the final verdict:

1. check every quantifier;
2. verify every parameter dependency;
3. test boundary and degenerate cases;
4. identify all uses of compactness, limits, asymptotics, or choice;
5. verify that every cited theorem has matching hypotheses;
6. distinguish uniform bounds from pointwise bounds;
7. distinguish existence from effective construction;
8. search for hidden assumptions and circular reasoning;
9. attempt to construct counterexamples to every major lemma;
10. list every unresolved gap.

FINAL RESPONSE FORMAT

Use these sections:

1. Intended formulation
2. Literal-versus-intended interpretation
3. Literature and known results
4. Formal target
5. Proof or disproof attempts
6. Rigorous progress obtained
7. Failed approaches and obstructions
8. Gap audit
9. Sources consulted
10. Final classification

The final classification must be exactly one of:

- SOLVED
- DISPROVED
- PARTIAL
- NO VERIFIED PROGRESS

Use SOLVED only if every step of a complete proof of the intended target has
been established.

Use DISPROVED only if a valid counterexample or complete disproof has been
established.

Use PARTIAL only when a new, rigorously justified special case, reduction,
bound, lemma, construction, or obstruction has been established beyond merely
restating the literature.

Otherwise use NO VERIFIED PROGRESS.

Finish with:

Classification: <one classification>
Completeness: <integer from 0 to 100>%
Unresolved gaps:
1. ...
2. ...

Clearly distinguish:

- facts obtained from cited sources;
- deductions established in this response;
- computational observations;
- heuristic or speculative ideas.
"""

# Existing batch submitters keep the public name, but solving is now offline and
# candidate-only. Online source status is maintained separately in the catalog.
PROMPT_TEMPLATE = CANDIDATE_PROMPT_TEMPLATE

REFUSAL_PHRASES = [
    "open", "unresolved", "partial progress", "not obtained",
    "cannot solve", "cannot fabricate", "won't fabricate", "no complete proof",
    "requires a deep theorem", "known conjecture", "famous problem",
    "i can't comply", "i cannot comply", "the problem remains",
    "no full solution", "partial result",
]

# Phrases that indicate ChatGPT is rate-limiting / refusing to generate.
RATE_LIMIT_PHRASES = [
    "you've reached our limit of messages",
    "you've hit the free plan limit",
    "you're sending messages too quickly",
    "too many requests",
]


# ── Problem files ─────────────────────────────────────────────────────────────

def extract_problem_statement(tex_path: Path) -> str:
    text = tex_path.read_text(encoding="utf-8")
    m = re.search(
        r'\\noindent\\textbf\{(?:Problem Statement|Statement):\}\s*\n\n(.*?)'
        r'(?=\n\n\\noindent\\textbf|\n\\bigskip|\n\\end\{document\})',
        text, re.DOTALL,
    )
    if m:
        return m.group(1).strip()
    body = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', text, re.DOTALL)
    if body:
        return body.group(1).strip()
    return text.strip()


def problem_number(tex_path: Path) -> int:
    m = re.search(r'(\d+)', tex_path.stem)
    return int(m.group(1)) if m else 0


def get_problem_files(category: str) -> list:
    ind_dir = REPO_DIR / category / "individual"
    if not ind_dir.exists():
        raise SystemExit(f"Directory not found: {ind_dir}")
    return sorted(ind_dir.glob("problem_*.tex"), key=problem_number)


# ── Chat-map persistence ──────────────────────────────────────────────────────

def load_chat_map() -> dict:
    if CHAT_MAP_FILE.exists():
        return json.loads(CHAT_MAP_FILE.read_text())
    return {}


def save_chat_map(m: dict):
    CHAT_MAP_FILE.write_text(json.dumps(m, indent=2))


# ── Output copies (named like the chat tab) ───────────────────────────────────

def output_title(num: int, status_tag: str, completeness: str) -> str:
    """The tab/title naming convention, e.g. 'Erdős #12 [candidate-proved] 88%'.
    The percentage is the COMPLETENESS_SCORE reported by the model."""
    return f"Erdős #{num} {status_tag} {completeness}%"


def save_output(platform: str, category: str, num: int, title: str, body: str):
    """
    Write a human-named copy of a solution into
    outputs/<platform>/<category>/<title>.md, mirroring the chat tab name.

    Idempotent: if a copy with this exact title already exists it does nothing;
    otherwise it removes any stale copy for the same problem number (the status
    or completeness may have changed between runs) and writes the new one.
    """
    out_dir = OUTPUTS_DIR / platform / category
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = title.replace("/", "-")
    target = out_dir / f"{safe}.md"
    if target.exists():
        return target
    for old in out_dir.glob(f"Erdős #{num} *.md"):
        if old != target:
            try:
                old.unlink()
            except OSError:
                pass
    target.write_text(body, encoding="utf-8")
    return target


def restore_output_from_solution(platform: str, category: str, num: int,
                                 solution_text: str):
    """
    Rebuild the named output copy from an already-saved solution file, so
    progress is restored even if the outputs/ folder was deleted or the run was
    interrupted.

    The status tag is taken from the solution header, but the percentage is
    re-derived from the response body via extract_completeness() rather than
    trusting the header number (older solutions were named by confidence). The
    header line is rewritten so the file content matches the completeness-based
    filename.
    """
    lines = solution_text.split("\n")
    header = lines[0] if lines else ""
    m = re.search(r"(\[[^\]]+\])", header)
    status_tag = m.group(1) if m else "[unsolved]"
    marker = " (DeepSeek)" if "(DeepSeek)" in header else ""
    completeness = extract_completeness(solution_text)
    title = output_title(num, status_tag, completeness)
    new_header = f"# Erdős Problem #{num} {status_tag} {completeness}%{marker}"
    body = "\n".join([new_header] + lines[1:]) if lines else solution_text
    return save_output(platform, category, num, title, body)


# ── Browser ───────────────────────────────────────────────────────────────────

def launch_browser(pw, headless=False):
    return pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=headless,
        args=["--disable-blink-features=AutomationControlled"],
        no_viewport=False,
        viewport={"width": 1280, "height": 900},
    )


def ensure_logged_in(page):
    page.goto(CHATGPT_URL, wait_until="domcontentloaded")
    time.sleep(3)
    if "login" in page.url or "auth" in page.url:
        raise SystemExit(
            "Not logged in! Run with --login first:\n"
            "  python3 solve_submit.py --login"
        )


# ── ChatGPT page helpers ──────────────────────────────────────────────────────

def current_url(page) -> str:
    """Read the live URL after ChatGPT client-side navigation."""
    try:
        return page.evaluate("() => location.href")
    except Exception:
        try:
            return page.url
        except Exception:
            return ""


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

def is_generating(page) -> bool:
    try:
        return page.query_selector('[data-testid="stop-button"]') is not None
    except Exception:
        return False


def extract_response(page) -> str:
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


def detect_rate_limit(page) -> bool:
    """Return True if the page is showing a rate-limit / throttle message."""
    # ChatGPT throttles rapid new-conversation creation with a blocking modal
    # (often with a "Got it" button); detect the dialog explicitly as well as
    # the text, since the modal can intercept clicks.
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


def dismiss_rate_limit_modal(page) -> bool:
    """Dismiss a 'too many requests' / rate-limit alert (click its "Got it" /
    close button, else press Escape) so the UI is interactable again.

    Returns True if something was dismissed."""
    try:
        # Prefer an explicit acknowledge button (the too-many-requests alert
        # uses "Got it"); match a few common labels case-insensitively.
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
        # Fall back to closing any open dialog.
        if page.query_selector('[role="dialog"], '
                               '[data-testid="modal-conversation-history-rate-limit"]'):
            page.keyboard.press("Escape")
            time.sleep(0.5)
            return True
    except Exception:
        pass
    return False



def start_new_chat(page):
    """Open a fresh chat inside the target Project."""
    page.goto(PROJECT_URL, wait_until="domcontentloaded")
    time.sleep(2.5)
    for sel in ['#prompt-textarea', '[data-testid="prompt-textarea"]', 'div[contenteditable="true"]']:
        if page.query_selector(sel):
            break
    else:
        time.sleep(2)


def send_prompt(page, prompt_text: str):
    """Type and submit a prompt. Fully JS-based to avoid pointer interception."""
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
        # ChatGPT's #prompt-textarea is a ProseMirror contenteditable. A bulk
        # keyboard.insert_text() does NOT register with ProseMirror (the send
        # then fires on an empty editor), so populate it with a synthetic paste
        # event instead — instant and reliable even for very large prompts.
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

    # Wait until the editor actually contains text (send button enables).
    deadline = time.time() + 5
    while time.time() < deadline:
        has_text = box.evaluate(
            "el => (el.value !== undefined ? el.value : el.innerText).trim().length > 0"
        )
        if has_text:
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

    # Try to submit, and verify it actually went through (URL changes to /c/ or
    # the composer clears). Retry a couple of times if it didn't register.
    for attempt in range(3):
        time.sleep(0.4)
        _click_send()
        # Give the submission a moment to register
        for _ in range(10):
            time.sleep(0.5)
            if "/c/" in current_url(page) and current_url(page) != start_url:
                return
            if not _box_has_text():
                return
        # Still not submitted — re-focus and retry
        try:
            page.evaluate("el => el.focus()", box)
        except Exception:
            pass



def wait_for_conversation_url(page, timeout_s: int = 30, start_url: str = "") -> str:
    """Wait for a concrete conversation URL or a project-route transition."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        url = current_url(page)
        if "/c/" in url:
            return url
        if start_url and url != start_url and url not in ("", "about:blank"):
            return url
        time.sleep(0.5)
    return current_url(page)


# ── Answer classification ─────────────────────────────────────────────────────

def is_solved(response: str) -> bool:
    """Return True only for a definitive SOLVED or DISPROVED classification."""
    tail = response[-4000:]

    # Preferred literature-aware output format.
    matches = re.findall(
        r"Classification:\s*(SOLVED|DISPROVED|PARTIAL|NO VERIFIED PROGRESS)",
        tail,
        re.IGNORECASE,
    )
    if matches:
        return matches[-1].upper() in {"SOLVED", "DISPROVED"}

    # Backward compatibility with the older research-mode format.
    lower_tail = tail.lower()
    if "resource_exhausted" in lower_tail:
        return False
    if re.search(r"\bdisproved\b", lower_tail):
        return True
    if re.search(r"\bproved\b", lower_tail) and not re.search(
        r"\bnot proved\b", lower_tail
    ):
        return True

    # Legacy machine-readable / STATUS fallbacks.
    m = re.search(r'"problem_solved"\s*:\s*(true|false)', response, re.IGNORECASE)
    if m:
        return m.group(1).lower() == "true"

    return ("# final answer" in response.lower()) and not any(
        phrase in response.lower() for phrase in REFUSAL_PHRASES
    )


def extract_confidence(response: str) -> str:
    # New research-mode format reports PROOF_CONFIDENCE (0-100). Prefer it,
    # then COMPLETENESS_SCORE, then legacy fields.
    for pat in (
        r'PROOF_CONFIDENCE[^\d]{0,40}?(\d{1,3})',
        r'"proof_confidence"\s*:\s*(\d{1,3})',
        r'COMPLETENESS_SCORE[^\d]{0,40}?(\d{1,3})',
        r'"solution_probability"\s*:\s*(\d{1,3})',
        r'SOLUTION_PROBABILITY[^\d]{0,40}?(\d{1,3})\s*%?',
        r'Confidence:\s*(\d{1,3})\s*%',
    ):
        m = re.search(pat, response, re.IGNORECASE)
        if m:
            return m.group(1)
    return "?"


def extract_completeness(response: str) -> str:
    # New research-mode format reports COMPLETENESS_SCORE (0-100): how much of
    # the argument has been rigorously established. Prefer it, then fall back to
    # related phrasings of *completeness* only. Never fall back to the
    # confidence score — completeness and confidence are distinct, and the
    # output filenames are named by completeness.
    for pat in (
        r'COMPLETENESS_SCORE[^\d]{0,40}?(\d{1,3})',
        r'"completeness_score"\s*:\s*(\d{1,3})',
        r'"completeness"\s*:\s*(\d{1,3})',
        r'Completeness[^\d]{0,40}?(\d{1,3})\s*%?',
    ):
        m = re.search(pat, response, re.IGNORECASE)
        if m:
            return m.group(1)
    return "?"


# ── Rename ────────────────────────────────────────────────────────────────────

def _js_click(page, element):
    page.evaluate("el => el.click()", element)


def _dismiss_dialogs(page):
    try:
        for dlg in page.query_selector_all('dialog[open]'):
            close_btn = dlg.query_selector(
                'button[aria-label*="close" i], button[aria-label*="dismiss" i], '
                'button[data-testid*="close"]'
            )
            if close_btn:
                _js_click(page, close_btn)
            else:
                page.keyboard.press("Escape")
            time.sleep(0.3)
    except Exception:
        pass


def _js_hover(page, element):
    page.evaluate(
        """el => {
            el.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
            el.dispatchEvent(new MouseEvent('mouseover',  {bubbles: true}));
        }""",
        element,
    )


def rename_chat(page, title: str):
    """
    Rename the currently-open conversation. Navigate to the chat URL *first*
    (so it becomes the active item) before calling this.

    ChatGPT's sidebar uses an anchor `a.__menu-item[href*="/c/<id>"]` that
    carries `data-active` for the open conversation. Hovering it reveals a
    trailing options button `button[aria-haspopup="menu"]` which opens a menu
    containing "Rename".
    """
    try:
        page.set_default_timeout(8_000)
        _dismiss_dialogs(page)
        time.sleep(0.3)

        # Locate the active sidebar anchor (prefer the one matching this chat id).
        cur = page.url.rstrip("/")
        cid = cur.split("/c/")[-1].split("?")[0] if "/c/" in cur else ""
        active_item = None
        for sel in [
            (f'a[data-sidebar-item][href*="{cid}"]' if cid else None),
            'a.__menu-item[data-active]',
            'a[data-active][href*="/c/"]',
            'nav a[href*="/c/"]',
        ]:
            if not sel:
                continue
            active_item = page.query_selector(sel)
            if active_item:
                break
        if active_item is None:
            print("  WARN: could not locate active chat in sidebar")
            return False

        # Hover to reveal the trailing options button.
        box = active_item.bounding_box()
        if box:
            page.mouse.move(box["x"] + box["width"] - 14, box["y"] + box["height"] / 2)
            time.sleep(0.4)
        _js_hover(page, active_item)
        time.sleep(0.4)

        options_btn = active_item.query_selector(
            'button[aria-haspopup="menu"], '
            'button[data-testid*="options"], '
            'button[aria-label*="options" i], '
            'button[aria-label*="more" i]'
        )
        if options_btn is None:
            btns = active_item.query_selector_all('button')
            options_btn = btns[-1] if btns else None
        if options_btn is None:
            print("  WARN: options button not found")
            return False

        _js_click(page, options_btn)
        time.sleep(0.6)

        rename_item = None
        for item in page.query_selector_all('[role="menuitem"]'):
            if "rename" in (item.inner_text() or "").lower():
                rename_item = item
                break
        if rename_item is None:
            print("  WARN: Rename menu item not found")
            page.keyboard.press("Escape")
            return False

        _js_click(page, rename_item)
        time.sleep(0.5)

        editable = page.query_selector(
            'a[data-active] input[type="text"], '
            'input[data-testid*="rename"], '
            'nav input[type="text"], '
            'nav li [contenteditable="true"], '
            'input[type="text"]:focus, [contenteditable="true"]:focus'
        )
        if editable:
            try:
                editable.fill(title)
            except Exception:
                editable.click()
                page.keyboard.press("Control+A")
                page.keyboard.insert_text(title)
            editable.press("Enter")
            time.sleep(0.4)
            return True
        else:
            page.keyboard.press("Escape")
            print("  WARN: rename input not found")
            return False


    except Exception as e:
        print(f"  WARN: rename failed (non-fatal): {e}")
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
