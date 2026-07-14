"""Browser ChatGPT model-runner adapter (DECISIONS.md D-A: primary informal provider).

The primary informal-reasoning provider is a human-authenticated ChatGPT browser
session driven through Playwright. Because a browser UI cannot cryptographically
attest an immutable model/version, every response produced here carries an
**unattested** :class:`AttestedModelIdentity` (``attested=False``) and can never
be counted as independent-model evidence — exactly the honest boundary the truth
plane requires.

The runner is written against a small :class:`BrowserBackend` protocol so its
control logic — conversation isolation, bounded rate-limit pauses, and
malformed-response retries — is fully exercised by a fake backend in tests. The
live :class:`PlaywrightChatGPTBackend` wraps the repository's ``erdos_common``
Playwright helpers and is only reachable with an authenticated profile.

Non-negotiable behaviors (task decisions A, D):
* Rate limiting **pauses** (cooldown clamped to ``<= 120s``) and retries; it never
  terminates the run or marks the mathematical problem failed. Persistent throttle
  raises :class:`BrowserProviderUnavailable`, a *transient provider outage* the
  caller is expected to pause/resume on — not a mathematical verdict.
* Each ``run`` uses a fresh, isolated conversation; the browser tab lifecycle is
  bounded to active jobs (``close`` / context-manager exit tears it down).
* Every exchange records the UI model label, conversation URL, account class,
  timestamp, prompt/response hashes, and the browser-runner version.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

from egmra.agents.runner import RunnerResponse
from egmra.agents.throttle import SharedThrottle
from egmra.provenance.hashing import sha256_hex
from egmra.provenance.stage_identity import AttestedModelIdentity

# Bump when the capture contract (recorded fields / hashing) changes.
BROWSER_RUNNER_VERSION = "browser-chatgpt/1"

# Hard ceiling on any single cooldown, per task decision D.
MAX_COOLDOWN_CEILING_SECONDS = 120.0


class BrowserRunnerError(RuntimeError):
    """Base class for browser-runner failures."""


class BrowserProviderUnavailable(BrowserRunnerError):
    """The browser provider is throttling beyond the retry budget.

    This is a *transient provider outage*, never a mathematical verdict. The
    caller should pause and resume the campaign, not mark the problem failed.
    """


class BrowserResponseError(BrowserRunnerError):
    """The browser returned an empty/malformed response beyond the retry budget."""


class BrowserBackend(Protocol):
    """The minimal browser surface the runner drives (wraps ``erdos_common``)."""

    def open_conversation(self) -> None:
        """Open a fresh, isolated conversation (new chat)."""

    def send(self, prompt: str) -> None:
        """Type and submit the prompt into the active conversation."""

    def wait_response(self, *, timeout_s: float) -> str:
        """Block until generation settles and return the assistant's text."""

    def conversation_url(self) -> str:
        """Return the concrete conversation URL for provenance."""

    def is_rate_limited(self) -> bool:
        """Return True when the UI is showing a rate-limit / throttle state."""

    def dismiss_rate_limit(self) -> bool:
        """Best-effort dismissal of a rate-limit modal so the UI is usable."""

    def close(self) -> None:
        """Tear down the browser tab/context (bounded tab lifecycle)."""


@dataclass(frozen=True)
class BrowserTranscript:
    """Immutable provenance record of one browser exchange (no response text)."""

    stage: str
    model_label: str
    account_class: str
    conversation_url: str
    prompt_hash: str
    response_hash: str
    runner_version: str
    attested: bool
    rate_limit_pauses: int
    response_retries: int
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class BrowserChatGPTRunner:
    """A ``ModelRunner`` backed by a human-authenticated ChatGPT browser session.

    All emitted identities are unattested (``attested=False``); this runner can
    never manufacture independent-model evidence.
    """

    backend: BrowserBackend
    runner_id: str = "browser-chatgpt"
    model_label: str = "ChatGPT (browser UI)"
    account_class: str = "browser-authenticated"
    provider: str = "openai"
    response_timeout_s: float = 300.0
    base_cooldown_s: float = 5.0
    cooldown_factor: float = 2.0
    max_cooldown_s: float = MAX_COOLDOWN_CEILING_SECONDS
    max_rate_limit_pauses: int = 6
    max_response_retries: int = 2
    min_response_chars: int = 1
    sleep: Callable[[float], None] = time.sleep
    now: Callable[[], float] = time.time
    throttle: "SharedThrottle | None" = None
    records: list[BrowserTranscript] = field(default_factory=list)

    def __post_init__(self) -> None:
        # The cooldown ceiling can be tightened below the hard cap but never above it.
        self.max_cooldown_s = min(float(self.max_cooldown_s), MAX_COOLDOWN_CEILING_SECONDS)
        if self.base_cooldown_s <= 0 or self.cooldown_factor < 1:
            raise ValueError("base_cooldown_s must be > 0 and cooldown_factor >= 1")
        if self.max_rate_limit_pauses < 0 or self.max_response_retries < 0:
            raise ValueError("retry budgets cannot be negative")

    # ── context-manager: bound the tab lifecycle to active jobs ──────────────
    def __enter__(self) -> "BrowserChatGPTRunner":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        self.backend.close()

    def _cooldown_for(self, pause_index: int) -> float:
        raw = self.base_cooldown_s * (self.cooldown_factor ** pause_index)
        return min(raw, self.max_cooldown_s)

    def _await_capacity(self) -> int:
        """Pause through rate-limit throttling; return the number of pauses taken.

        A shared throttle (when configured) coordinates cooldowns across the five
        browser workers and persists them across restarts. Raises
        :class:`BrowserProviderUnavailable` only after exhausting the pause budget
        — a transient outage signal, not a mathematical failure.
        """
        pauses = 0
        # Honor any cross-worker cooldown a peer already registered.
        if self.throttle is not None:
            self.throttle.wait_if_cooling()
        while self.backend.is_rate_limited():
            if pauses >= self.max_rate_limit_pauses:
                raise BrowserProviderUnavailable(
                    f"ChatGPT browser throttled after {pauses} cooldown(s); "
                    "pause and resume — this is not a mathematical result"
                )
            self.backend.dismiss_rate_limit()
            retry_after = self._retry_after()
            if self.throttle is not None:
                # Register the hit centrally so peer workers also pause.
                cooldown = self.throttle.record_rate_limit(retry_after=retry_after)
                self.sleep(cooldown)
            else:
                base = self._cooldown_for(pauses)
                self.sleep(base if retry_after is None else min(
                    max(base, retry_after), self.max_cooldown_s))
            pauses += 1
        if self.throttle is not None and pauses:
            self.throttle.clear()
        return pauses

    def _retry_after(self) -> float | None:
        getter = getattr(self.backend, "retry_after", None)
        if not callable(getter):
            return None
        try:
            value = getter()
        except Exception:  # noqa: BLE001 - a missing hint is not fatal
            return None
        return float(value) if isinstance(value, (int, float)) and value > 0 else None

    def _looks_malformed(self, text: str) -> bool:
        stripped = (text or "").strip()
        if len(stripped) < self.min_response_chars:
            return True
        return stripped == "[Could not extract response]"

    def run(self, prompt: str, *, stage: str) -> RunnerResponse:
        prompt_hash = sha256_hex(prompt)
        total_pauses = 0
        last_text = ""
        for attempt in range(self.max_response_retries + 1):
            total_pauses += self._await_capacity()
            # Conversation isolation: a fresh chat per attempt.
            self.backend.open_conversation()
            self.backend.send(prompt)
            text = self.backend.wait_response(timeout_s=self.response_timeout_s)
            last_text = text
            if not self._looks_malformed(text):
                return self._record(stage, prompt_hash, text, total_pauses, attempt)
        raise BrowserResponseError(
            f"browser returned an unusable response for stage {stage!r} after "
            f"{self.max_response_retries + 1} attempt(s)"
        )

    def _record(
        self, stage: str, prompt_hash: str, text: str, pauses: int, retries: int
    ) -> RunnerResponse:
        conversation_url = self.backend.conversation_url()
        response_hash = sha256_hex(text)
        # Unattested by construction: a browser UI cannot attest an immutable
        # model id, so this identity can never count as independent evidence.
        identity = AttestedModelIdentity(
            provider=self.provider,
            model=self.model_label,
            ui_surface="browser",
            account_class=self.account_class,
        )
        transcript = BrowserTranscript(
            stage=stage,
            model_label=self.model_label,
            account_class=self.account_class,
            conversation_url=conversation_url,
            prompt_hash=prompt_hash,
            response_hash=response_hash,
            runner_version=BROWSER_RUNNER_VERSION,
            attested=identity.attested,
            rate_limit_pauses=pauses,
            response_retries=retries,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.now())),
        )
        self.records.append(transcript)
        # The context id binds the exchange to its isolated conversation and the
        # exact prompt, so cache replay across conversations is impossible.
        context_id = sha256_hex(
            f"{self.runner_id}:{stage}:{conversation_url}:{prompt_hash}:{BROWSER_RUNNER_VERSION}"
        )
        return RunnerResponse(
            text=text, model=identity, context_id=context_id, prompt_hash=prompt_hash
        )


class PlaywrightChatGPTBackend:  # pragma: no cover - requires an authenticated browser
    """Live :class:`BrowserBackend` over the packaged ``chatgpt_browser`` helpers.

    Reachable only with an authenticated Chromium profile (set ``CHATGPT_PROFILE_DIR``
    and authenticate it once). It performs no network access at import time;
    Playwright is imported lazily on ``start``, and the browser glue is packaged
    (no dependency on the repository root).
    """

    def __init__(self, *, headless: bool = False, generation_poll_s: float = 1.0,
                 generation_start_timeout_s: float = 30.0) -> None:
        self.headless = headless
        self.generation_poll_s = generation_poll_s
        self.generation_start_timeout_s = generation_start_timeout_s
        self._pw = None
        self._context = None
        self._page = None
        self._start_url = ""

    def start(self) -> "PlaywrightChatGPTBackend":
        from playwright.sync_api import sync_playwright

        from egmra.agents import chatgpt_browser as cb

        self._cb = cb
        self._pw = sync_playwright().start()
        self._context = cb.launch_browser(self._pw, headless=self.headless)
        self._page = self._context.new_page()
        cb.ensure_logged_in(self._page)
        return self

    def open_conversation(self) -> None:
        self._cb.start_new_chat(self._page)
        self._start_url = self._cb.current_url(self._page)

    def send(self, prompt: str) -> None:
        self._cb.send_prompt(self._page, prompt)

    def wait_response(self, *, timeout_s: float) -> str:
        # Wait for generation to visibly BEGIN before deciding it has settled, so
        # a response is never extracted before the model starts (delayed start).
        self._cb.wait_for_generation_start(
            self._page, timeout_s=min(self.generation_start_timeout_s, timeout_s)
        )
        deadline = time.time() + timeout_s
        while time.time() < deadline and self._cb.is_generating(self._page):
            time.sleep(self.generation_poll_s)
        return self._cb.extract_response(self._page)

    def conversation_url(self) -> str:
        return self._cb.wait_for_conversation_url(self._page, start_url=self._start_url)

    def is_rate_limited(self) -> bool:
        return self._cb.detect_rate_limit(self._page)

    def dismiss_rate_limit(self) -> bool:
        return self._cb.dismiss_rate_limit_modal(self._page)

    def close(self) -> None:
        try:
            if self._context is not None:
                self._context.close()
        finally:
            if self._pw is not None:
                self._pw.stop()
            self._context = None
            self._page = None
            self._pw = None
