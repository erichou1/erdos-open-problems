"""Provider-aware rate-limit throttling (spec §7.10, §14.5, §4.4).

Rate limiting uses provider-specific state, honors ``Retry-After`` when present,
and applies exponential backoff with jitter and a **120-second per-attempt cap**.
A rate limit *pauses* leases and is recorded as censored operational data — it
never consumes a mathematical retry.
"""

from __future__ import annotations

import random
import math
from dataclasses import dataclass, field

MAX_BACKOFF_SECONDS = 120.0


@dataclass
class ProviderThrottle:
    provider: str
    base_seconds: float = 2.0
    max_seconds: float = MAX_BACKOFF_SECONDS
    seed: int = 0
    math_retries_consumed: int = 0
    censored_pauses: int = 0
    _rng: random.Random = field(default_factory=lambda: random.Random(0))

    def __post_init__(self) -> None:
        if not isinstance(self.provider, str) or not self.provider.strip():
            raise ValueError("provider must be a non-empty string")
        if not math.isfinite(self.base_seconds) or self.base_seconds <= 0:
            raise ValueError("base_seconds must be finite and positive")
        if not math.isfinite(self.max_seconds) or self.max_seconds <= 0:
            raise ValueError("max_seconds must be finite and positive")
        self._rng = random.Random(self.seed)
        # Enforce the user-specified 120-second maximum cooldown.
        self.max_seconds = min(self.max_seconds, MAX_BACKOFF_SECONDS)

    def backoff_seconds(self, attempt: int, *, retry_after: float | None = None) -> float:
        """Compute the next cooldown, capped at 120s, with jitter."""
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 0:
            raise ValueError("attempt must be a non-negative integer")
        if retry_after is not None:
            if not math.isfinite(retry_after) or retry_after < 0:
                raise ValueError("Retry-After must be finite and non-negative")
            return min(self.max_seconds, retry_after)
        # Avoid constructing an attacker-controlled enormous integer before the
        # cap is applied.  Once the unjittered value reaches the cap the exact
        # result is necessarily the cap.
        cap_attempt = max(0, math.ceil(math.log2(self.max_seconds / self.base_seconds)))
        if attempt >= cap_attempt:
            return self.max_seconds
        raw = math.ldexp(self.base_seconds, attempt)
        jitter = self._rng.uniform(0.0, self.base_seconds)
        return round(min(self.max_seconds, raw + jitter), 3)

    def on_rate_limit(self, attempt: int, *, retry_after: float | None = None) -> dict:
        """A rate limit pauses (censored); it does not consume a math retry."""
        self.censored_pauses += 1
        return {
            "action": "pause",
            "provider": self.provider,
            "cooldown_seconds": self.backoff_seconds(attempt, retry_after=retry_after),
            "consumes_math_retry": False,
            "classification": "censored_operational_event",
        }

    def on_math_retry(self) -> None:
        """A genuine mathematical retry (e.g. malformed output) consumes budget."""
        self.math_retries_consumed += 1
