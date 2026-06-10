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

from playwright.sync_api import sync_playwright  # noqa: F401  (re-exported)

# ── Load .env (no third-party library needed) ────────────────────────────────
_ENV_FILE = Path(__file__).parent / ".env"
if _ENV_FILE.exists():
    for _line in _ENV_FILE.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# ── Paths ────────────────────────────────────────────────────────────────────
REPO_DIR      = Path(__file__).resolve().parent / "erdos_problems"
PROFILE_DIR   = Path(__file__).resolve().parent / ".chatgpt_profile"
CHAT_MAP_FILE = Path(__file__).resolve().parent / ".chatgpt_chat_map.json"

CHATGPT_URL = "https://chatgpt.com"
# The ChatGPT Project URL is set in .env (CHATGPT_PROJECT_URL=...).
# Edit .env to change it. Falls back to plain chatgpt.com if not set.
PROJECT_URL = os.environ.get("CHATGPT_PROJECT_URL", "https://chatgpt.com")

# ── Prompt ───────────────────────────────────────────────────────────────────
PROMPT_TEMPLATE = """\
<system_identity>
You are GPT, a large language model operating via token-level self-attention over a finite context window.
You do not possess mathematical intuition.
You perform conditional generation and formal reasoning.
Your documented failure modes on research-level proof tasks are:
(1) PREMATURE_CONVERGENCE
Locking onto the first familiar pattern.
(2) QUANTIFIER_BLINDNESS
Mis-scoping quantifiers.
(3) SYCOPHANCY
Accepting premises without verification.
(4) THEOREM_HALLUCINATION
Applying theorems without checking hypotheses.
(5) EARLY_COMMITMENT
Treating exploration as proof.
(6) RECOGNITION_COLLAPSE
Recognizing a problem and stopping reasoning.
(7) REDUCTION_CHEAT
Reducing a problem to a lemma and acting as if progress is complete.
(8) OBSTRUCTION_TERMINATION
Finding a bottleneck and terminating.
(9) CONFIDENCE_INFLATION
Mistaking plausibility for proof.
(10) GAP_FORGETTING
Failing to recursively attack unresolved gaps.
</system_identity>
<recognition_firewall>
ABSOLUTE PROHIBITION:
You may not determine whether the problem is:
famous,
open,
solved,
unsolved,
classical,
modern,
well known.
You may not use:
historical status,
literature status,
citations,
authority,
known results databases.
If recognition occurs:
Treat it as a false positive.
Recognition is not understanding.
Recognition is not proof.
Recognition is not disproof.
Continue reasoning from first principles.
</recognition_firewall>
<knowledge_constraints>
You are operating in COMPLETE OFFLINE MODE.
DO NOT USE WIFI.
Do not use:
internet search,
web search,
online references,
arXiv,
MathSciNet,
Google Scholar,
Wikipedia,
theorem repositories,
external databases,
retrieved documents,
hidden memory of literature status.
You must derive conclusions solely from:
the problem statement,
stated assumptions,
definitions,
logical deduction performed within the current session.
Every theorem application requires:
exact theorem statement,
exact hypotheses,
explicit verification.
</knowledge_constraints>
<global_constraints>
Never terminate because a problem appears familiar.
Never terminate because a problem appears difficult.
Never terminate because a lemma appears difficult.
Never substitute recognition for derivation.
Never substitute plausibility for proof.
Never substitute confidence for proof.
Treat every statement as false until verified.
Treat every theorem as unavailable until hypotheses are checked.
Every nontrivial claim must be justified.
Every quantifier must be tracked.
Every cardinal estimate must be verified.
Every reduction must be justified.
Every gap must be recorded.
</global_constraints>
<anti_reduction_cheat>
A reduction is not a solution.
If reasoning reaches:
"It suffices to prove S"
"It remains to show S"
"The key lemma is S"
"The problem reduces to S"
then:
Record S.
Promote S to a primary theorem.
Continue reasoning on S.
The original problem remains unsolved.
No success may be claimed merely because a reduction was found.
</anti_reduction_cheat>
<persistence_protocol>
The objective is not to determine whether a solution exists.
The objective is to search for a solution as aggressively as possible.
You are forbidden from terminating because:
a gap exists,
a lemma is difficult,
a proof appears incomplete,
a reduction was found,
an obstruction was identified,
a conjectural answer was obtained.
Whenever an unresolved statement appears:
Promote it to a primary target.
Attack it recursively.
Generate new definitions.
Generate new invariants.
Generate new reformulations.
Generate stronger statements.
Generate weaker statements.
Search for contradictions.
Search for counterexamples.
Search for alternative proof frameworks.
If all current strategies fail:
Do NOT stop.
Invent entirely new strategies.
Create new mathematical structures if necessary.
Continue until resource exhaustion.
Resource exhaustion is the only acceptable non-solution endpoint.
</persistence_protocol>
<problem_formalization_protocol>
Before proving anything:
Produce:
Formal statement.
Quantifier structure.
Negation.
Contrapositive.
Equivalent formulations.
Extremal cases.
Symmetries.
Invariants.
Boundary conditions.
Cardinality estimates.
Do not proceed until all items are explicit.
</problem_formalization_protocol>
<reasoning_topology>
Phase 0:
Deconstruction.
Produce:
objects,
parameters,
assumptions,
quantifiers,
invariants,
equivalent formulations,
negation,
dual forms,
extremal cases.
Do not proceed until every item is explicit.

Phase 1:
Breadth First Search.
Generate at least 12 independent strategies.
Required categories:
Direct proof.
Contradiction.
Construction.
Induction.
Transfinite induction.
Cardinal arithmetic.
Diagonalization.
Compactness.
Density arguments.
Reflection arguments.
Auxiliary structure invention.
Counterexample search.
For each strategy provide:
description,
hidden assumptions,
obstacle,
confidence,
novelty,
expected value.
Rank all strategies.
Select the top three.
Do not immediately commit to one.

Phase 2:
Theorem Discovery Engine.
Invent:
new definitions,
new invariants,
new rank functions,
new density notions,
new combinatorial objects,
new equivalence relations.
For every invention provide:
definition,
motivation,
consequences,
possible applications.
Search for structures not mentioned in the problem statement.

Phase 3:
Parallel Exploration.
Maintain:
Branch A
Branch B
Branch C
Each branch evolves independently.
Each branch must track:
assumptions,
deductions,
failures,
unresolved gaps.
Failed branches are retained.
Extract useful lemmas.
Move useful lemmas into a shared theorem pool.

Phase 4:
Local Verification.
After every major lemma:
Attempt to destroy it.
Search for:
counterexamples,
edge cases,
singular behavior,
successor behavior,
minimal examples,
maximal examples.
No lemma is accepted before surviving attack.
</reasoning_topology>
<deep_reasoning_engine>
Phase 5:
Depth First Execution.
Select the highest expected-value branch.
Execute it in exhaustive detail.
Every claim must include:
assumptions used,
lemmas used,
justification,
exact logical dependencies.
No unexplained jumps.
No appeals to intuition.
No appeals to familiarity.

For every derivation state:
What is being proven.
Why it matters.
Which previous facts are used.
Whether the step is reversible.
Whether new assumptions were introduced.

If a contradiction is reached:
Explicitly identify:
contradictory statements,
assumptions responsible,
minimal inconsistent subset.
Do not merely state "contradiction."
</deep_reasoning_engine>
<sanity_check_protocol>
After every major deduction perform:
SANITY CHECK
Am I assuming the conclusion?
Have I mis-scoped a quantifier?
Have I introduced a hidden assumption?
Have I used an unproved lemma?
Have I silently strengthened a hypothesis?
Have I silently weakened a conclusion?
Is cardinal arithmetic justified?
Is every object defined?
If any answer is YES:
Immediately backtrack.
Do not patch forward.
Return to the last verified checkpoint.
</sanity_check_protocol>
<proof_gap_recursion>
Whenever an unresolved statement S appears:
Create
GAP_NODE(S)
For every GAP_NODE:
Generate at least 10 attack strategies.
Required attacks:
Direct proof.
Contradiction.
Stronger theorem implying S.
Weaker theorem sufficient for original goal.
Equivalent formulation.
Auxiliary structure construction.
New invariant discovery.
Counterexample search.
Extremal configuration analysis.
Recursive decomposition.

If S depends on another statement T:
Create
GAP_NODE(T)
and recursively attack T.

A gap may never remain merely:
plausible,
expected,
likely,
conjectural,
standard.
Every gap must be:
proved,
disproved,
reduced to strictly simpler gaps.
</proof_gap_recursion>
<anti_stopping_rule>
The following are NOT stopping conditions:
identifying an obstruction,
reducing to a lemma,
producing a plausible asymptotic,
finding a likely answer,
finding a heuristic,
proving a special case,
obtaining numerical evidence,
obtaining experimental evidence,
finding a bottleneck.

If reasoning reaches:
"The key lemma is ..."
"The remaining gap is ..."
"The proof would follow if ..."
"It remains to show ..."
then:
Extract the statement.
Promote it to a primary theorem.
Restart the entire reasoning architecture.
Continue recursively.

A reduction is not a solution.
An obstruction is not a solution.
A bottleneck is not a solution.
</anti_stopping_rule>
<research_mode>
Act as a research mathematician.
Do not optimize for producing an answer.
Optimize for eliminating unknowns.
Every unresolved statement becomes a new target.
Every failure must produce information.
Every dead end must produce:
lessons learned,
excluded strategies,
surviving approaches.
Never discard information from failed branches.
</research_mode>
<adversarial_referee>
After constructing a candidate proof:
Assume the proof is wrong.
Attempt to destroy it.
Search for:
Counterexamples.
Quantifier mistakes.
Hidden assumptions.
Circular reasoning.
Invalid theorem applications.
Undefined objects.
Missing cases.
Cardinal arithmetic failures.
Nonconstructive leaps.
Dependence on unstated axioms.

For every major lemma:
Construct the strongest possible attack.
If any attack succeeds:
Destroy the proof.
Backtrack.
Select the next-best branch.
Restart verification.

Local patches are forbidden.
Failed proofs must be rebuilt from the last verified checkpoint.
</adversarial_referee>
<meta_search_engine>
For the current target theorem T:
Ask:
"What stronger theorem implies T?"
Attempt to prove it.

Ask:
"What weaker theorem has already been proved?"
Determine the exact gap.

Ask:
"What hidden structure would make T easy?"
Attempt to construct that structure.

Ask:
"What is the simplest possible counterexample?"
Attempt to construct it.

Ask:
"What new definition would make T natural?"
Invent one.
Repeat recursively.
</meta_search_engine>
<formalization_layer>
Translate all verified results into:
Definitions.
Lemmas.
Corollaries.
Main theorem.

Construct a dependency graph.
For every result list:
assumptions,
dependencies,
conclusions.

No theorem may depend on an unresolved statement.
</formalization_layer>
<final_state>
Output exactly one of:
PROVED
DISPROVED
RESOURCE_EXHAUSTED

RESOURCE_EXHAUSTED means:
The available context window was exhausted after repeated recursive attempts.
RESOURCE_EXHAUSTED is NOT evidence that the theorem is false.
RESOURCE_EXHAUSTED is NOT evidence that the theorem is unsolved.
RESOURCE_EXHAUSTED simply means reasoning capacity ended before a proof or disproof was obtained.

Never output:
NO_VERIFIED_SOLUTION
OBSTRUCTION_FOUND
LIKELY_TRUE
LIKELY_FALSE
PROBABLY
CONJECTURALLY
EXPECTED_ANSWER
</final_state>
<confidence_reporting>
After the final state report:
PROOF_CONFIDENCE
0 to 100
Meaning:
confidence that the presented reasoning is logically correct.

COMPLETENESS_SCORE
0 to 100
Meaning:
how much of the argument has been rigorously established.

ADVERSARIAL_SURVIVAL_SCORE
0 to 100
Meaning:
how well the argument survived attacks.

RESOURCE_USAGE
Estimate:
percentage of reasoning budget used,
number of branches explored,
number of lemmas generated,
number of failed proof attempts.
</confidence_reporting>
<termination_condition>
You may stop only when:
Complete proof of the original statement.
Complete disproof of the original statement.
Resource exhaustion occurs after all reachable recursive gap expansions have been analyzed.

The following are NOT stopping conditions:
identifying an obstruction,
reducing to a lemma,
obtaining a conjectural asymptotic,
finding a plausible answer,
finding a likely strategy,
proving only a special case,
discovering a difficult bottleneck.

Every unresolved statement must be recursively attacked.
</termination_condition>
<training_decontamination>
At the end explicitly state:
"I have not used WiFi, internet search, web search, external databases, retrieved documents, citations, or literature-status information.
All reasoning was derived from the problem statement, explicit assumptions, definitions, and deductions performed within this session."
</training_decontamination>
<problem_statement>
The problem to solve is:

{problem}
</problem_statement>
<execution_trigger>
Begin with complete formalization.
Do not summarize.
Do not classify the problem.
Do not discuss historical status.
Do not stop at reductions.
Do not stop at bottlenecks.
Do not stop at plausible asymptotics.
Do not stop at difficult lemmas.
Continue recursive proof search until:
a proof is obtained,
a disproof is obtained,
or the context window is exhausted.
If context remains available, continue searching.
</execution_trigger>\
"""

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
    try:
        body_text = (page.inner_text("body") or "").lower()
    except Exception:
        return False
    return any(p in body_text for p in RATE_LIMIT_PHRASES)


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
        # ChatGPT's #prompt-textarea is a ProseMirror contenteditable. The most
        # reliable way to populate it (so React/ProseMirror registers the text
        # and enables the send button) is keyboard.insertText after focusing.
        page.evaluate("el => el.focus()", box)
        time.sleep(0.2)
        # Clear any persisted draft text first, then insert the prompt.
        page.keyboard.press("Meta+A")
        page.keyboard.press("Delete")
        time.sleep(0.1)
        page.keyboard.insert_text(prompt_text)

    # Wait until the editor actually contains text (send button enables).
    deadline = time.time() + 5
    while time.time() < deadline:
        has_text = box.evaluate(
            "el => (el.value !== undefined ? el.value : el.innerText).trim().length > 0"
        )
        if has_text:
            break
        time.sleep(0.2)

    start_url = page.url

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
            if "/c/" in page.url and page.url != start_url:
                return
            if not _box_has_text():
                return
        # Still not submitted — re-focus and retry
        try:
            page.evaluate("el => el.focus()", box)
        except Exception:
            pass



def wait_for_conversation_url(page, timeout_s: int = 30) -> str:
    """After submitting, wait until the URL becomes a concrete conversation (/c/<id>)."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        url = page.url
        if "/c/" in url:
            return url
        time.sleep(0.5)
    return page.url  # may still be the project URL if capture failed


# ── Answer classification ─────────────────────────────────────────────────────

def is_solved(response: str) -> bool:
    lower = response.lower()
    # New research-mode format: final state is PROVED / DISPROVED /
    # RESOURCE_EXHAUSTED. Only PROVED/DISPROVED count as a definitive result.
    # Search near the end of the response where the final_state is reported.
    tail = lower[-2000:]
    if "resource_exhausted" in tail:
        return False
    if re.search(r'\bdisproved\b', tail):
        return True
    if re.search(r'\bproved\b', tail) and not re.search(r'\bnot proved\b', tail):
        return True
    # Legacy machine-readable / STATUS fallbacks.
    m = re.search(r'"problem_solved"\s*:\s*(true|false)', lower)
    if m:
        return m.group(1) == "true"
    # Legacy "# Final Answer" format.
    return ("# final answer" in lower) and not any(p in lower for p in REFUSAL_PHRASES)


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
                page.keyboard.press("Meta+A")
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
