"""Shared, durable browser-throttle coordinator (spec §C: cross-worker throttling).

A per-instance cooldown is insufficient when up to five browser workers share one
ChatGPT account: a rate limit hit by one worker must pause the others too. This
coordinator persists cooldown state to a JSON file guarded by an OS advisory lock,
so cooldowns are shared across processes and survive a restart. Cooldowns honor an
optional ``Retry-After`` and are always clamped to a hard 120-second ceiling.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path

MAX_COOLDOWN_CEILING_SECONDS = 120.0


class SharedThrottle:
    """Cross-process cooldown state for the browser worker pool."""

    def __init__(
        self,
        state_path: str | Path,
        *,
        base_cooldown_s: float = 5.0,
        cooldown_factor: float = 2.0,
        max_cooldown_s: float = MAX_COOLDOWN_CEILING_SECONDS,
        now: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.state_path = Path(state_path)
        self.base_cooldown_s = base_cooldown_s
        self.cooldown_factor = cooldown_factor
        self.max_cooldown_s = min(float(max_cooldown_s), MAX_COOLDOWN_CEILING_SECONDS)
        self.now = now
        self.sleep = sleep
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _locked_state(self):
        # Advisory lock for cross-process mutual exclusion; degrade gracefully if
        # the platform lacks fcntl (state is still atomically rewritten).
        lock_path = self.state_path.with_suffix(self.state_path.suffix + ".lock")
        handle = open(lock_path, "a+")
        try:
            try:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            except (ImportError, OSError):
                pass
            state = self._read()
            yield state
            self._write(state)
        finally:
            handle.close()

    def _read(self) -> dict:
        try:
            text = self.state_path.read_text(encoding="utf-8")
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
        return {"cooldown_until": 0.0, "consecutive": 0}

    def _write(self, state: dict) -> None:
        tmp = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
        tmp.write_text(json.dumps(state), encoding="utf-8")
        os.replace(tmp, self.state_path)

    def cooldown_remaining(self) -> float:
        state = self._read()
        return max(0.0, float(state.get("cooldown_until", 0.0)) - self.now())

    def record_rate_limit(self, *, retry_after: float | None = None) -> float:
        """Register a rate-limit hit and return the (clamped) cooldown seconds."""
        with self._locked_state() as state:
            consecutive = int(state.get("consecutive", 0))
            backoff = self.base_cooldown_s * (self.cooldown_factor ** consecutive)
            if retry_after is not None:
                backoff = max(backoff, float(retry_after))
            cooldown = min(backoff, self.max_cooldown_s)
            state["consecutive"] = consecutive + 1
            state["cooldown_until"] = self.now() + cooldown
            return cooldown

    def clear(self) -> None:
        """Reset the shared cooldown after a successful exchange."""
        with self._locked_state() as state:
            state["consecutive"] = 0
            state["cooldown_until"] = 0.0

    def wait_if_cooling(self) -> float:
        """Sleep out any shared cooldown (bounded by the ceiling). Returns slept seconds."""
        remaining = min(self.cooldown_remaining(), self.max_cooldown_s)
        if remaining > 0:
            self.sleep(remaining)
        return max(0.0, remaining)
