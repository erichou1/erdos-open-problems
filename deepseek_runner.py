#!/usr/bin/env python3
"""DeepSeek (Expert + DeepThink / R1) browser runner for ProofPipeline.

Used as a **distinct adjudicator** model. Routing the final adjudication through
a different model than the one that produced and reviewed the candidate breaks
the correlated blind spots of a model grading its own work — the single most
common way an automated proof pipeline fools itself.

Implements the same ``IsolatedRunner`` protocol as
``run_verified_pipeline.ChatGPTBrowserRunner`` (a fresh, isolated chat per
stage) but drives DeepSeek's web UI via ``deepseek_common``. All heavy imports
(the browser automation module and the cross-process rate limiter) are lazy so
the runner can be unit-tested with injected fakes and no Playwright install.
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path


class DeepSeekBrowserRunner:
    """Fresh-chat DeepSeek adapter (Expert + DeepThink) for isolated model calls."""

    def __init__(
        self, browser, page, *, timeout_s: float,
        backoff_s: float = 15.0, max_backoff_s: float = 120.0,
        request_spacing_s: float = 12.0, max_attempts: int = 8,
        deepseek=None, sleep=time.sleep, rate_limiter=None,
    ):
        if deepseek is None:  # pragma: no cover - exercised only with a real browser
            import deepseek_common as deepseek
        self.D = deepseek
        self.browser = browser
        self.page = page
        self.timeout_s = timeout_s
        self.max_backoff_s = max(0.0, min(120.0, max_backoff_s))
        self.backoff_s = min(max(0.0, backoff_s), self.max_backoff_s)
        self.request_spacing_s = max(0.0, min(120.0, request_spacing_s))
        self.max_attempts = max_attempts
        self._sleep = sleep
        if rate_limiter is None:  # pragma: no cover - real cross-process limiter
            from run_verified_pipeline import SharedRateLimiter
            rate_limiter = SharedRateLimiter(
                Path(tempfile.gettempdir()) / "erdos_deepseek_rate_limit.json",
                backoff_s=self.backoff_s,
                max_backoff_s=self.max_backoff_s,
                request_spacing_s=self.request_spacing_s,
            )
        self.rate_limiter = rate_limiter
        # A DeepSeek-specific quota is tracked separately from ChatGPT's.
        self.contexts: dict[str, str] = {}

    # ── IsolatedRunner protocol ──────────────────────────────────────────────
    def context_id(self, stage: str) -> str:
        return self.contexts.get(stage, "")

    def restore_context(self, stage: str, context_id: str) -> None:
        """Restore durable provenance when ProofPipeline replays a cache entry."""
        self.contexts[stage] = context_id

    # ── helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _is_conversation_url(url: str) -> bool:
        return bool(url) and ("/chat/s/" in url or "/a/chat/" in url)

    def _cool_down(self, stage: str, reason: str) -> None:
        streak, wait_s = self.rate_limiter.record_rate_limit()
        print(f"{stage}: {reason}; shared DeepSeek rate-limit streak={streak}; "
              f"all DeepSeek workers paused for up to {wait_s:.0f}s", flush=True)

    def run(self, prompt: str, *, stage: str, isolated: bool) -> str:
        if not isolated:
            raise ValueError("verified pipeline stages must use isolated contexts")

        last_error = "unknown"
        attempts_used = 0
        # A rate limit is a provider-side condition, not a failed proof stage;
        # only real navigation/generation/response failures consume retries.
        while attempts_used < self.max_attempts:
            self.rate_limiter.wait_for_slot(stage)
            try:
                _ = self.page.url
            except Exception:
                self.page = self.browser.new_page()

            try:
                self.D.start_new_chat(self.page)  # also enables Expert + DeepThink

                if self.D.detect_rate_limit(self.page):
                    last_error = "rate-limited before send"
                    self._cool_down(stage, last_error)
                    continue

                self.D.send_prompt(self.page, prompt)
                url = self.D.wait_for_conversation_url(self.page, timeout_s=120)

                if not self._is_conversation_url(url):
                    if self.D.detect_rate_limit(self.page):
                        last_error = "rate-limited after send"
                        self._cool_down(stage, last_error)
                        continue
                    attempts_used += 1
                    last_error = "no conversation URL"
                    print(f"{stage}: {last_error} (attempt {attempts_used}); retrying",
                          flush=True)
                    self._sleep(15)
                    continue

                self.contexts[stage] = url
                print(f"{stage}: waiting for DeepSeek (DeepThink) at {url}", flush=True)
                self._sleep(5)

                deadline = time.time() + self.timeout_s
                while time.time() < deadline and self.D.is_generating(self.page):
                    if self.D.detect_rate_limit(self.page):
                        self._cool_down(stage, "rate-limited while generating")
                        self.rate_limiter.wait_for_slot(stage)
                    self._sleep(5)

                if self.D.is_generating(self.page):
                    attempts_used += 1
                    last_error = f"generation exceeded {self.timeout_s:.0f}s"
                    print(f"{stage}: {last_error} (attempt {attempts_used}); backing off",
                          flush=True)
                    self._sleep(self.backoff_s)
                    continue

                # DeepSeek caps a single message and hides the rest behind a
                # "Continue" button; a long adjudication must be fully expanded.
                try:
                    self.D.click_continue_if_needed(self.page)
                except Exception:
                    pass

                self._sleep(2)
                response = self.D.extract_response(self.page)
                if not response or len(response.strip()) < 100:
                    attempts_used += 1
                    last_error = "empty/incomplete response"
                    print(f"{stage}: {last_error} (attempt {attempts_used}); retrying",
                          flush=True)
                    self._sleep(15)
                    continue

                self.rate_limiter.record_success()
                return response

            except Exception as exc:
                last_error = str(exc)
                print(f"{stage}: error '{exc}'", flush=True)
                try:
                    if self.D.detect_rate_limit(self.page):
                        last_error = "rate-limited during browser exception"
                        self._cool_down(stage, last_error)
                        continue
                except Exception:
                    pass
                attempts_used += 1
                print(f"{stage}: retrying after DeepSeek browser error "
                      f"(attempt {attempts_used})", flush=True)
                self._sleep(15)

        raise RuntimeError(
            f"{stage}: DeepSeek failed after {self.max_attempts} non-rate-limit "
            f"attempts ({last_error})")
