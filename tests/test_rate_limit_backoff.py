import unittest
from unittest.mock import patch

from run_verified_pipeline import ChatGPTBrowserRunner


class RateLimitBackoffTests(unittest.TestCase):
    def test_backoff_doubles_and_is_capped(self):
        runner = ChatGPTBrowserRunner(
            browser=None,
            page=None,
            timeout_s=60,
            backoff_s=10,
            max_backoff_s=40,
        )
        with patch("run_verified_pipeline.C.dismiss_rate_limit_modal"), \
                patch("run_verified_pipeline.time.sleep") as sleep:
            for streak in range(1, 5):
                runner._cool_down("review", "rate-limited", streak)

        self.assertEqual([call.args[0] for call in sleep.call_args_list],
                         [10, 20, 40, 40])


if __name__ == "__main__":
    unittest.main()
