import tempfile
import unittest

from pathlib import Path

from run_verified_pipeline import SharedRateLimiter


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


if __name__ == "__main__":
    unittest.main()
