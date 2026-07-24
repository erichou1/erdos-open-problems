"""Parallel Aristotle formalization: dispatch concurrency without trust changes.

The vendor account allows up to 5 concurrent proof tasks; these tests pin the
three coordinated pieces that exploit that safely:

* ``RunnerWorker._build_formal_candidates`` dispatches source-less candidates
  concurrently — but emits byte-identical artifacts/failures in candidate order.
* ``AristotleFormalizer`` holds a process-wide slot for each task's full
  submit→completion window, so total in-flight vendor tasks can never exceed
  the account limit no matter how many workers/branches dispatch at once.
* ``AristotleSdkClient._await`` marshals every awaitable to one client-owned
  loop thread, so concurrent callers are safe (no shared run_until_complete).
"""

from __future__ import annotations

import asyncio
import threading
import time
from types import SimpleNamespace

import pytest

from egmra.agents.runner import DeterministicRunner
from egmra.lean.aristotle_sdk import AristotleSdkClient
from egmra.lean.formalizer import (
    _aristotle_max_concurrent,
    AristotleFormalizer,
)
from egmra.orchestrator.runner_worker import RunnerWorker


def _worker(formalizer) -> RunnerWorker:
    return RunnerWorker(runner=DeterministicRunner(), goal_claim_id="goal",
                        goal_formula="T", lean_version="4.28.0",
                        mathlib_commit="v4.28.0", formalizer=formalizer)


def _candidates(n: int) -> list[dict]:
    return [{"claim_id": "", "declaration_name": f"decl_{i}",
             "expected_type": f"Type{i}", "source": ""} for i in range(n)]


# ---------------------------------------------------------------------------
# parallel dispatch in _build_formal_candidates


class _BarrierFormalizer:
    """Releases only if ``parties`` formalize calls are in flight AT ONCE."""

    formalizer_id = "barrier"

    def __init__(self, parties: int):
        self.barrier = threading.Barrier(parties, timeout=10.0)

    def formalize(self, *, declaration_name, expected_type,
                  informal_statement, previous_source="", kernel_feedback=""):
        self.barrier.wait()  # deadlocks (timeout → BrokenBarrier) if serial
        return f"theorem {declaration_name} : {expected_type} := trivial"


def test_multiple_candidates_are_dispatched_concurrently():
    worker = _worker(_BarrierFormalizer(parties=3))
    failures: list[str] = []
    out = worker._build_formal_candidates(
        _candidates(3), branch_id="b1", seen=set(), failures=failures)
    assert failures == []
    # Deterministic assembly: candidate order preserved exactly.
    assert [c["declaration_name"] for c in out] == ["decl_0", "decl_1", "decl_2"]
    assert all(c["claim_id"] == "goal" for c in out)


def test_failures_stay_isolated_ordered_and_identical_to_serial():
    class _OneBadFormalizer:
        formalizer_id = "one-bad"

        def formalize(self, *, declaration_name, **_kw):
            if declaration_name == "decl_1":
                raise TimeoutError("vendor hiccup")
            if declaration_name == "decl_2":
                return ""  # vendor returned nothing
            return f"theorem {declaration_name} : X := trivial"

    worker = _worker(_OneBadFormalizer())
    failures: list[str] = []
    out = worker._build_formal_candidates(
        _candidates(3), branch_id="b2", seen=set(), failures=failures)
    assert [c["declaration_name"] for c in out] == ["decl_0"]
    # Exactly the serial path's failure strings, in candidate order.
    assert failures == [
        "formalizer_error:b2:TimeoutError",
        "formalization_unavailable:b2:decl_1",
        "formalization_unavailable:b2:decl_2",
    ]


def test_single_candidate_runs_on_the_caller_thread():
    calls: list[str] = []

    class _ThreadRecorder:
        formalizer_id = "recorder"

        def formalize(self, *, declaration_name, expected_type, **_kw):
            calls.append(threading.current_thread().name)
            return f"theorem {declaration_name} : {expected_type} := trivial"

    worker = _worker(_ThreadRecorder())
    out = worker._build_formal_candidates(
        _candidates(1), branch_id="b3", seen=set(), failures=[])
    assert len(out) == 1
    assert calls == [threading.current_thread().name]


# ---------------------------------------------------------------------------
# account-wide slot budget in AristotleFormalizer


class _CountingClient:
    """Tracks peak concurrent submit→fetch windows (one vendor task each)."""

    def __init__(self, quarantine_dir):
        self.quarantine_dir = quarantine_dir
        self._lock = threading.Lock()
        self.active = 0
        self.peak = 0

    def submit(self, prompt):
        with self._lock:
            self.active += 1
            self.peak = max(self.peak, self.active)
        time.sleep(0.03)  # keep the task window open long enough to overlap
        return SimpleNamespace(project_id="p", agent_task_id="t")

    def fetch(self, submission, *, wait=True):
        with self._lock:
            self.active -= 1
        return SimpleNamespace(quarantine_dir=self.quarantine_dir)


def test_slot_semaphore_caps_concurrent_vendor_tasks(tmp_path):
    quarantine = tmp_path / "q"
    quarantine.mkdir()
    (quarantine / "Proof.lean").write_text("theorem t : True := trivial")
    client = _CountingClient(quarantine)
    formalizer = AristotleFormalizer(
        client=client, slots=threading.BoundedSemaphore(2))

    threads = [threading.Thread(target=lambda: formalizer.formalize(
        declaration_name="d", expected_type="True", informal_statement="s"))
        for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10.0)
    assert client.peak <= 2  # never more vendor tasks in flight than slots
    assert client.active == 0


def test_max_concurrent_env_clamped_to_account_limit():
    assert _aristotle_max_concurrent({}) == 5
    assert _aristotle_max_concurrent({"EGMRA_ARISTOTLE_MAX_CONCURRENT": "3"}) == 3
    assert _aristotle_max_concurrent({"EGMRA_ARISTOTLE_MAX_CONCURRENT": "0"}) == 1
    assert _aristotle_max_concurrent({"EGMRA_ARISTOTLE_MAX_CONCURRENT": "99"}) == 5
    assert _aristotle_max_concurrent({"EGMRA_ARISTOTLE_MAX_CONCURRENT": "x"}) == 5


# ---------------------------------------------------------------------------
# SDK client: concurrent callers share one marshalling loop safely


def test_sdk_await_is_safe_for_concurrent_callers(tmp_path):
    (tmp_path / "lean_project").mkdir()

    class _SyncSdk:  # set_api_key path only; not used by _await test jobs
        def set_api_key(self, key):
            return key

    client = AristotleSdkClient(
        quarantine_root=tmp_path / "quar", project_dir=tmp_path / "lean_project",
        sdk=_SyncSdk(), env={"ARISTOTLE_API_KEY": "arstl_test_key_not_real"})

    state = SimpleNamespace(active=0, peak=0)

    async def _job():
        state.active += 1
        state.peak = max(state.peak, state.active)
        await asyncio.sleep(0.03)
        state.active -= 1
        return "ok"

    results: list[str] = []
    errors: list[BaseException] = []

    def _call():
        try:
            results.append(client._await(_job()))
        except BaseException as exc:  # noqa: BLE001 - the assertion below reports it
            errors.append(exc)

    threads = [threading.Thread(target=_call) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10.0)
    client.close()
    assert errors == []
    assert results == ["ok"] * 5
    # All five coroutines shared one loop and genuinely overlapped.
    assert state.peak >= 2


def test_sdk_await_still_passes_sync_values_through(tmp_path):
    (tmp_path / "lean_project").mkdir()

    class _SyncSdk:
        def set_api_key(self, key):
            return key

    client = AristotleSdkClient(
        quarantine_root=tmp_path / "quar", project_dir=tmp_path / "lean_project",
        sdk=_SyncSdk(), env={"ARISTOTLE_API_KEY": "arstl_test_key_not_real"})
    assert client._await("plain-value") == "plain-value"
    client.close()
