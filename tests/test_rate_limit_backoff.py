import tempfile
import unittest
import json
import time
from unittest.mock import patch

from pathlib import Path

from run_verified_pipeline import ChatGPTBrowserRunner, SharedRateLimiter
from run_verified_range import rate_limit_defaults


class RateLimitBackoffTests(unittest.TestCase):
    def test_backoff_doubles_and_is_capped(self):
        with tempfile.TemporaryDirectory() as directory:
            limiter = SharedRateLimiter(
                Path(directory) / "rate-limit.json",
                backoff_s=10,
                max_backoff_s=40,
                request_spacing_s=1,
            )
            penalties = [limiter.record_rate_limit() for _ in range(4)]

        self.assertEqual(penalties, [(1, 10), (2, 20), (3, 40), (4, 40)])

    def test_runner_clamps_initial_backoff_to_120_second_cap(self):
        class Page:
            url = "https://chat.test/"

        runner = ChatGPTBrowserRunner(
            object(), Page(), timeout_s=10,
            backoff_s=180, max_backoff_s=120,
        )
        self.assertEqual(runner.backoff_s, 120)
        self.assertEqual(runner.max_backoff_s, 120)
        self.assertEqual(runner.rate_limiter.backoff_s, 120)

        overlarge = ChatGPTBrowserRunner(
            object(), Page(), timeout_s=10,
            backoff_s=180, max_backoff_s=999,
        )
        self.assertEqual(overlarge.max_backoff_s, 120)
        self.assertEqual(overlarge.backoff_s, 120)

    def test_range_runner_uses_short_initial_backoff_and_120_second_cap(self):
        self.assertEqual(rate_limit_defaults(), {
            "backoff_s": 15.0,
            "max_backoff_s": 120.0,
            "request_spacing_s": 12.0,
        })

    def test_penalty_resets_only_after_complete_response(self):
        class Page:
            url = "https://chat.test/"

        class Limiter:
            def __init__(self):
                self.successes = 0

            def wait_for_slot(self, stage):
                return None

            def record_success(self):
                self.successes += 1

        runner = ChatGPTBrowserRunner(
            object(), Page(), timeout_s=10, max_attempts=2,
        )
        limiter = Limiter()
        runner.rate_limiter = limiter
        with (
            patch("run_verified_pipeline.C.start_new_chat"),
            patch("run_verified_pipeline.C.detect_rate_limit", return_value=False),
            patch("run_verified_pipeline.C.current_url", return_value="https://chat.test/"),
            patch("run_verified_pipeline.C.send_prompt"),
            patch("run_verified_pipeline.C.wait_for_conversation_url",
                  return_value="https://chat.test/c/1"),
            patch("run_verified_pipeline.C.is_generating", return_value=False),
            patch("run_verified_pipeline.C.extract_response",
                  side_effect=["", "complete response " * 10]),
            patch("run_verified_pipeline.time.sleep"),
        ):
            response = runner.run("prompt", stage="scout_1", isolated=True)

        self.assertTrue(response.startswith("complete response"))
        self.assertEqual(limiter.successes, 1)

    def test_success_does_not_erase_another_workers_future_cooldown(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rate-limit.json"
            future = time.time() + 90
            path.write_text(json.dumps({
                "rate_limit_streak": 4,
                "cooldown_until": future,
                "next_request_at": future,
            }))
            limiter = SharedRateLimiter(
                path, backoff_s=15, max_backoff_s=120,
                request_spacing_s=12,
            )
            limiter.record_success()
            state = json.loads(path.read_text())
            self.assertEqual(state["rate_limit_streak"], 0)
            self.assertEqual(state["cooldown_until"], future)
            self.assertEqual(state["next_request_at"], future)

    def test_legacy_oversized_shared_state_is_clamped_to_current_120_second_cap(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rate.json"
            future = time.time() + 3600
            path.write_text(json.dumps({
                "cooldown_until": future,
                "next_request_at": future,
                "rate_limit_streak": 20,
            }))
            limiter = SharedRateLimiter(
                path, backoff_s=15, max_backoff_s=120,
                request_spacing_s=999,
            )
            limiter.record_rate_limit()
            state = json.loads(path.read_text())
            self.assertLessEqual(state["cooldown_until"], time.time() + 120.1)
            self.assertLessEqual(state["next_request_at"], time.time() + 120.1)
            self.assertEqual(limiter.request_spacing_s, 120)


if __name__ == "__main__":
    unittest.main()
