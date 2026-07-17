"""Tests for the Kimi browser provider (driver logic + CLI wiring)."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from egmra.agents import kimi_browser
from egmra.agents.async_browser import build_browser_runner_pool
from egmra.agents.kimi_browser import KimiAsyncPageDriver, kimi_profile_dir
from egmra.cli import _KIMI_RUNNER_KWARGS, build_parser, main
from egmra.tests.test_cli_arbitrary import _config_file, _signed_policy_file


# ── configuration surface ────────────────────────────────────────────────────

def test_kimi_profile_dir_defaults_and_env_override(monkeypatch, tmp_path):
    monkeypatch.delenv("KIMI_PROFILE_DIR", raising=False)
    assert kimi_profile_dir() == Path.cwd() / ".kimi_profile"
    monkeypatch.setenv("KIMI_PROFILE_DIR", str(tmp_path / "profile"))
    assert kimi_profile_dir() == tmp_path / "profile"


def test_live_verified_selectors_are_pinned():
    # These two were verified against kimi.com live; the driver must try them first.
    assert kimi_browser.COMPOSER_SELECTORS[0] == "div.chat-input-editor"
    assert kimi_browser.SEND_SELECTORS[0] == "div.send-button-container"
    assert kimi_browser.CONVERSATION_URL_MARKER == "/chat/"
    assert all(kimi_browser.RATE_LIMIT_PHRASES)


# ── driver logic against a fake page (no playwright needed) ─────────────────

class _FakeElement:
    def __init__(self, text: str = "", on_evaluate=None):
        self._text = text
        self._on_evaluate = on_evaluate
        self.evaluated: list[tuple] = []

    async def inner_text(self):
        return self._text

    async def evaluate(self, script, *args):
        self.evaluated.append((script, args))
        if self._on_evaluate is not None:
            self._on_evaluate(script, args)


class _FakePage:
    """Selector-keyed fake page; values may be elements, callables, or None."""

    def __init__(self):
        self.selectors: dict[str, object] = {}
        self.body_text = ""
        self.url = "https://www.kimi.com/"
        self.keyboard = SimpleNamespace(press=self._press)
        self.pressed: list[str] = []

    async def _press(self, key):
        self.pressed.append(key)

    def _lookup(self, selector):
        value = self.selectors.get(selector)
        return value() if callable(value) else value

    async def query_selector(self, selector):
        return self._lookup(selector)

    async def query_selector_all(self, selector):
        value = self._lookup(selector)
        if value is None:
            return []
        return value if isinstance(value, list) else [value]

    async def evaluate(self, script):
        return self.url

    async def inner_text(self, selector):
        return self.body_text

    async def goto(self, url, **kw):
        return None

    async def wait_for_selector(self, selector, **kw):
        return None


def test_wait_response_settles_on_stable_text():
    driver = KimiAsyncPageDriver(generation_poll_s=0.01,
                                 generation_start_timeout_s=0.05, stable_polls=2)
    page = _FakePage()
    texts = iter(["partial", "partial answer", "final answer",
                  "final answer", "final answer", "final answer"])
    current = {"value": "starting"}

    def _next_element():
        try:
            current["value"] = next(texts)
        except StopIteration:
            pass
        return _FakeElement(current["value"])

    page.selectors[kimi_browser.ASSISTANT_SELECTORS[0]] = _next_element
    text = asyncio.run(driver.wait_response(page, timeout_s=5.0))
    assert text == "final answer"


def test_wait_response_times_out_to_sentinel_when_no_reply():
    driver = KimiAsyncPageDriver(generation_poll_s=0.01,
                                 generation_start_timeout_s=0.02, stable_polls=2)
    page = _FakePage()  # no assistant elements at all
    text = asyncio.run(driver.wait_response(page, timeout_s=0.05))
    assert text == "[Could not extract response]"


def test_wait_response_waits_out_generation_indicator():
    driver = KimiAsyncPageDriver(generation_poll_s=0.01,
                                 generation_start_timeout_s=0.05, stable_polls=2)
    page = _FakePage()
    generating = {"count": 3}

    def _stop_element():
        if generating["count"] > 0:
            generating["count"] -= 1
            return _FakeElement("stop")
        return None

    page.selectors[kimi_browser.STOP_SELECTORS[0]] = _stop_element
    page.selectors[kimi_browser.ASSISTANT_SELECTORS[0]] = _FakeElement("done text")
    text = asyncio.run(driver.wait_response(page, timeout_s=5.0))
    assert text == "done text"


def test_send_pastes_prompt_and_clicks_send_control():
    driver = KimiAsyncPageDriver()
    page = _FakePage()
    pasted: list = []
    composer = _FakeElement("", on_evaluate=lambda s, a: pasted.append(a))
    send_control = _FakeElement("")
    page.selectors[kimi_browser.COMPOSER_SELECTORS[0]] = composer
    page.selectors[kimi_browser.SEND_SELECTORS[0]] = send_control

    async def _run():
        await driver.open_conversation(page)
        page.url = "https://www.kimi.com/chat/abc123"  # post-send URL
        await driver.send(page, "prove the lemma")

    asyncio.run(_run())
    assert pasted and pasted[0] == (("prove the lemma",))
    assert send_control.evaluated  # the send control was clicked
    assert asyncio.run(driver.conversation_url(page)).endswith("/chat/abc123")


def test_is_rate_limited_matches_phrases():
    driver = KimiAsyncPageDriver()
    page = _FakePage()
    page.body_text = "You have sent Too Many Requests. Try again later."
    assert asyncio.run(driver.is_rate_limited(page)) is True
    page.body_text = "Ask anything, or task an agent..."
    assert asyncio.run(driver.is_rate_limited(page)) is False


# ── CLI wiring ───────────────────────────────────────────────────────────────

def test_parser_accepts_kimi_browser_provider():
    parser = build_parser()
    args = parser.parse_args(["campaign", "--provider", "kimi-browser"])
    assert args.provider == "kimi-browser"
    args = parser.parse_args(["run", "--statement", "S",
                              "--provider", "kimi-browser"])
    assert args.provider == "kimi-browser"


def test_runner_pool_carries_kimi_identity():
    engine = SimpleNamespace(pages=["tab-a", "tab-b"])
    pool = build_browser_runner_pool(engine, **dict(_KIMI_RUNNER_KWARGS))
    assert [r.runner_id for r in pool] == ["browser-kimi-tab0", "browser-kimi-tab1"]
    assert all(r.model_label == "Kimi (browser UI)" for r in pool)
    assert all(r.provider == "moonshot" for r in pool)


def test_browser_throttles_are_per_provider(tmp_path):
    from egmra.cli import _browser_throttle
    from egmra.config import EgmraConfig

    config = EgmraConfig(events_dir=str(tmp_path))
    chatgpt = _browser_throttle(config, "browser")
    kimi = _browser_throttle(config, "kimi-browser")
    assert chatgpt is not None and kimi is not None
    assert chatgpt.state_path != kimi.state_path
    assert _browser_throttle(config, "deterministic") is None
    assert _browser_throttle(config, "deepseek-api") is None


class _FakeEngine:
    def __init__(self, workers: int) -> None:
        self.pages = [f"tab{i}" for i in range(workers)]
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_campaign_kimi_browser_builds_kimi_runner_pool(tmp_path, monkeypatch):
    """--provider kimi-browser drives Kimi-labelled tab runners end to end."""
    import egmra.cli as cli_module

    built: dict = {}

    def _fake_engine(workers, **kw):
        built["workers"], built["provider"] = workers, kw.get("provider")
        built["engine"] = _FakeEngine(workers)
        return built["engine"]

    monkeypatch.setattr(cli_module, "_build_browser_engine", _fake_engine)
    monkeypatch.setattr(cli_module, "from_erdos_number",
                        lambda number, **kw: SimpleNamespace(
                            problem_id=f"erdos-{number}", source_bytes=b"S",
                            source_id="fx", display_statement="S",
                            status_claims=[], novelty_verdict="N1"))
    captured: list = []

    def _fake_research(**kwargs):
        captured.append(kwargs["runner"])
        return object()

    monkeypatch.setattr(cli_module, "research", _fake_research)
    monkeypatch.setattr(cli_module, "classify_result",
                        lambda result, **kw: SimpleNamespace(state="OPEN_NO_PROGRESS"))
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "campaign", "--provider", "kimi-browser",
               "--workers", "2", "--erdos-range", "5-6", "--policy", str(policy),
               "--state", str(tmp_path / "camp.json")])
    assert rc == 0
    assert built["provider"] == "kimi-browser" and built["workers"] == 2
    assert built["engine"].closed is True
    assert captured and all(
        runner.runner_id.startswith("browser-kimi-tab") for runner in captured)
    assert all(runner.model_label == "Kimi (browser UI)" for runner in captured)
    assert all(runner.provider == "moonshot" for runner in captured)


def test_campaign_chatgpt_browser_identity_unchanged(tmp_path, monkeypatch):
    """Default browser provider keeps its ChatGPT identity (regression)."""
    import egmra.cli as cli_module

    monkeypatch.setattr(cli_module, "_build_browser_engine",
                        lambda workers, **kw: _FakeEngine(workers))
    monkeypatch.setattr(cli_module, "from_erdos_number",
                        lambda number, **kw: SimpleNamespace(
                            problem_id=f"erdos-{number}", source_bytes=b"S",
                            source_id="fx", display_statement="S",
                            status_claims=[], novelty_verdict="N1"))
    captured: list = []
    monkeypatch.setattr(cli_module, "research",
                        lambda **kw: captured.append(kw["runner"]) or object())
    monkeypatch.setattr(cli_module, "classify_result",
                        lambda result, **kw: SimpleNamespace(state="OPEN_NO_PROGRESS"))
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "campaign", "--provider", "browser",
               "--workers", "1", "--erdos-range", "5", "--policy", str(policy),
               "--state", str(tmp_path / "camp.json")])
    assert rc == 0
    assert captured and captured[0].runner_id.startswith("browser-chatgpt-tab")
    assert captured[0].model_label == "ChatGPT (browser UI)"
    assert captured[0].provider == "openai"
