"""Exchange-level durability (finer-grained than branch checkpoints).

A cached exchange is returned only for a byte-identical prompt; the recorded
model identity round-trips verbatim (attestation re-verified on load, never
upgraded); every degenerate cache state falls open to a LIVE call.  The
end-to-end test reproduces the actual production failure: a worker killed
mid-branch replays its completed exchanges for free on retry and only goes
live for the missing ones.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from egmra.agents.exchange_cache import CachedRunner
from egmra.agents.runner import RunnerResponse
from egmra.provenance.hashing import sha256_hex
from egmra.provenance.stage_identity import AttestedModelIdentity, attest_model_identity


class CountingRunner:
    def __init__(self, text="reply body", identity=None,
                 conversation_url="https://chatgpt.com/c/cache-test"):
        self.runner_id = "counting"
        self.calls = 0
        self.records = ["transcript-sentinel"]
        self._text = text
        self._conversation_url = conversation_url
        self._identity = identity or AttestedModelIdentity(
            provider="local", model="counting", ui_surface="test")

    def run(self, prompt, *, stage):
        self.calls += 1
        return RunnerResponse(
            text=self._text, model=self._identity,
            context_id=f"ctx-{self.calls}", prompt_hash=sha256_hex(prompt),
            conversation_url=self._conversation_url)


def test_identical_prompt_replays_without_a_live_call(tmp_path):
    inner = CountingRunner()
    cached = CachedRunner(inner, tmp_path / "exchanges")
    first = cached.run("prove it", stage="branch:b1")
    second = cached.run("prove it", stage="branch:b1")
    assert inner.calls == 1
    assert (cached.hits, cached.misses) == (1, 1)
    assert second.text == first.text and second.prompt_hash == first.prompt_hash


def test_different_prompt_or_divergent_context_goes_live(tmp_path):
    inner = CountingRunner()
    cached = CachedRunner(inner, tmp_path / "exchanges")
    cached.run("round 1 prompt", stage="branch:b1")
    cached.run("round 2 prompt built on DIFFERENT round-1 ledger", stage="branch:b1")
    assert inner.calls == 2                    # no cross-prompt replay, ever


def test_cache_survives_process_death(tmp_path):
    """The production scenario: the run dies, a fresh attempt replays for free."""
    first_attempt = CountingRunner()
    CachedRunner(first_attempt, tmp_path / "exchanges").run("p1", stage="cold_pass")
    assert first_attempt.calls == 1

    # ...process killed; a NEW wrapper over a NEW runner, same cache dir:
    second_attempt = CountingRunner(text="would be different live")
    replayed = CachedRunner(second_attempt, tmp_path / "exchanges").run(
        "p1", stage="cold_pass")
    assert second_attempt.calls == 0           # zero live cost
    assert replayed.text == "reply body"       # the ORIGINAL exchange


def test_conversation_url_round_trips_with_cached_exchange(tmp_path):
    directory = tmp_path / "exchanges"
    original = CountingRunner(
        conversation_url="https://chatgpt.com/c/exact-conversation")
    live = CachedRunner(original, directory).run("p", stage="branch:b1")
    replayed = CachedRunner(CountingRunner(), directory).run(
        "p", stage="branch:b1")
    assert live.conversation_url == "https://chatgpt.com/c/exact-conversation"
    assert replayed.conversation_url == live.conversation_url
    record = json.loads(next(directory.glob("*.json")).read_text())
    assert record["conversation_url"] == live.conversation_url


def test_attested_identity_round_trips_and_reverifies(tmp_path):
    attested = attest_model_identity(
        provider="openai", model="gpt-4o-2024-11-20", version="2024-11-20",
        build_id="req-1", ui_surface="api")
    assert attested.attested
    inner = CountingRunner(identity=attested)
    cached = CachedRunner(inner, tmp_path / "exchanges")
    cached.run("p", stage="s")
    replay = CachedRunner(CountingRunner(), tmp_path / "exchanges").run("p", stage="s")
    assert replay.model.attested                # HMAC re-verified on load
    assert replay.model.provider == "openai"


def test_tampered_cached_identity_is_not_attested(tmp_path):
    attested = attest_model_identity(
        provider="openai", model="gpt-4o", version="v1", build_id="b1")
    cached = CachedRunner(CountingRunner(identity=attested), tmp_path / "x")
    cached.run("p", stage="s")
    entry = next((tmp_path / "x").glob("*.json"))
    record = json.loads(entry.read_text())
    record["model"]["model"] = "gpt-5-forged"   # upgrade attempt
    entry.write_text(json.dumps(record))
    replay = CachedRunner(CountingRunner(), tmp_path / "x").run("p", stage="s")
    assert not replay.model.attested            # attestation no longer verifies


def test_degenerate_cache_states_fall_open_to_live(tmp_path):
    directory = tmp_path / "exchanges"
    inner = CountingRunner()
    cached = CachedRunner(inner, directory)
    cached.run("p", stage="s")
    entry = next(directory.glob("*.json"))

    # malformed JSON -> miss -> live call and the entry is repaired
    entry.write_text("not json")
    assert CachedRunner(inner, directory).run("p", stage="s").text == "reply body"
    assert inner.calls == 2

    # symlinked entry -> never followed -> live call
    target = tmp_path / "outside.json"
    target.write_text(entry.read_text())
    entry.unlink()
    entry.symlink_to(target)
    CachedRunner(inner, directory).run("p", stage="s")
    assert inner.calls == 3


def test_empty_reply_is_never_cached(tmp_path):
    inner = CountingRunner(text="   ")
    cached = CachedRunner(inner, tmp_path / "exchanges")
    cached.run("p", stage="s")
    cached.run("p", stage="s")
    assert inner.calls == 2                     # nothing durable to replay


def test_wrapper_is_transparent_to_provenance_recording(tmp_path):
    inner = CountingRunner()
    cached = CachedRunner(inner, tmp_path / "exchanges")
    assert cached.runner_id == "counting"
    assert list(cached.records) == ["transcript-sentinel"]   # __getattr__ delegation


def test_cache_entries_are_private_files(tmp_path):
    cached = CachedRunner(CountingRunner(), tmp_path / "exchanges")
    cached.run("p", stage="branch:b1:round2")
    entry = next((tmp_path / "exchanges").glob("*.json"))
    assert oct(entry.stat().st_mode & 0o777) == "0o600"
    assert ":" not in entry.name                # stage sanitised for the filesystem
