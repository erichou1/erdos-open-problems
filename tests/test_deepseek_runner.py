import unittest

from deepseek_runner import DeepSeekBrowserRunner


CONV_URL = "https://chat.deepseek.com/a/chat/s/abc123def456"
LONG = "This is a sufficiently long adjudication verdict. " * 4  # > 100 chars


class FakePage:
    def __init__(self):
        self.url = "https://chat.deepseek.com/"


class FakeRateLimiter:
    def __init__(self):
        self.rate_limits = 0
        self.successes = 0

    def wait_for_slot(self, stage):
        pass

    def record_rate_limit(self):
        self.rate_limits += 1
        return (self.rate_limits, 0.0)

    def record_success(self):
        self.successes += 1


class FakeDeepSeek:
    """Minimal stand-in for the deepseek_common module."""

    def __init__(self, responses, *, conv_url=CONV_URL, generating=False,
                 rate_limited=False):
        self._responses = list(responses)
        self.conv_url = conv_url
        self._generating = generating
        self._rate_limited = rate_limited
        self.sent = []
        self.continue_clicks = 0

    def start_new_chat(self, page):
        page.url = "https://chat.deepseek.com/"

    def detect_rate_limit(self, page):
        return self._rate_limited

    def send_prompt(self, page, prompt):
        self.sent.append(prompt)
        page.url = self.conv_url

    def wait_for_conversation_url(self, page, timeout_s=120):
        return page.url

    def is_generating(self, page):
        return self._generating

    def click_continue_if_needed(self, page, *a, **k):
        self.continue_clicks += 1
        return 0

    def extract_response(self, page):
        return self._responses.pop(0) if self._responses else ""


def make_runner(fake, **kw):
    return DeepSeekBrowserRunner(
        browser=object(), page=FakePage(), timeout_s=5,
        backoff_s=0, max_backoff_s=0, request_spacing_s=0, max_attempts=3,
        deepseek=fake, sleep=lambda *_: None,
        rate_limiter=kw.pop("rate_limiter", FakeRateLimiter()), **kw,
    )


class DeepSeekBrowserRunnerTests(unittest.TestCase):
    def test_run_returns_response_and_records_context(self):
        fake = FakeDeepSeek([LONG])
        runner = make_runner(fake)
        out = runner.run("adjudicate this", stage="adjudication_0", isolated=True)
        self.assertEqual(out, LONG)
        self.assertEqual(runner.context_id("adjudication_0"), CONV_URL)
        self.assertEqual(fake.sent, ["adjudicate this"])
        # long answers must be expanded past DeepSeek's per-message cap
        self.assertEqual(fake.continue_clicks, 1)

    def test_non_isolated_is_rejected(self):
        runner = make_runner(FakeDeepSeek([LONG]))
        with self.assertRaises(ValueError):
            runner.run("x", stage="adjudication_0", isolated=False)

    def test_restore_context_roundtrip(self):
        runner = make_runner(FakeDeepSeek([LONG]))
        runner.restore_context("adjudication_1", CONV_URL)
        self.assertEqual(runner.context_id("adjudication_1"), CONV_URL)

    def test_empty_response_retries_then_succeeds(self):
        rl = FakeRateLimiter()
        fake = FakeDeepSeek(["", LONG])  # first extract empty, then a real answer
        runner = make_runner(fake, rate_limiter=rl)
        out = runner.run("p", stage="adjudication_0", isolated=True)
        self.assertEqual(out, LONG)
        self.assertEqual(rl.successes, 1)

    def test_exhausts_attempts_when_always_empty(self):
        fake = FakeDeepSeek(["", "", "", ""])
        runner = make_runner(fake)
        with self.assertRaises(RuntimeError):
            runner.run("p", stage="adjudication_0", isolated=True)


if __name__ == "__main__":
    unittest.main()
