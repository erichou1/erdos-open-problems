"""Adversarial tests for the durable campaign / bounded worker pool (task B3)."""

from __future__ import annotations

import threading

import pytest

from egmra.orchestrator.campaign import Campaign, CampaignError, FileCampaignStore


class _Clock:
    def __init__(self, t=1000.0):
        self.t = t

    def now(self):
        return self.t


def _campaign(tmp_path, workers=("w0",), **kw):
    return Campaign(tmp_path / "campaign.json", worker_ids=workers, **kw)


class _FlakyStore:
    """Wraps a real store and injects transient write failures on demand.

    Simulates a network/DB blip (psycopg.OperationalError etc.) mid-campaign.
    ``arm(skip=N, then_fail=M)`` lets the next N writes pass, then raises on the
    following M writes; reads/locks always delegate.
    """

    def __init__(self, inner):
        self.inner = inner
        self._skip = 0
        self._fail_n = 0
        self._lock = threading.Lock()

    def arm(self, *, skip: int, then_fail: int) -> None:
        with self._lock:
            self._skip = skip
            self._fail_n = then_fail

    def read(self, *, retry_seconds=None):
        return self.inner.read()

    def locked(self, *, deadline_seconds=None):
        return self.inner.locked(deadline_seconds=deadline_seconds)

    def write(self, body, *, retry_seconds=None):
        with self._lock:
            if self._skip > 0:
                self._skip -= 1
            elif self._fail_n > 0:
                self._fail_n -= 1
                raise RuntimeError("simulated DB disconnect (write)")
        self.inner.write(body)

    def close(self):
        self.inner.close()




def test_initialize_and_status(tmp_path):
    c = _campaign(tmp_path)
    c.initialize("camp-1", ["p1", "p2", "p3"])
    st = c.status()
    assert st["total"] == 3 and st["by_status"]["pending"] == 3 and st["complete"] is False


def test_machine_heartbeat_survives_assignment_transitions(tmp_path):
    c = _campaign(tmp_path, workers=("host-a:w0", "host-a:w1"))
    c.initialize("camp-machines", ["p1", "p2"])
    metadata = {
        "hostname": "host-a", "process_id": 123,
        "branch": "main", "code_commit": "a" * 40,
        "latest_commit": "a" * 40, "version_status": "current",
        "started_at": 900.0,
        "worker_ids": ["host-a:w0", "host-a:w1"],
    }
    c.machine_heartbeat("host-a", metadata=metadata, now=1000.0)
    assignment = c.lease("host-a:w0", now=1001.0)
    assert assignment is not None
    assert c.heartbeat("p1", "host-a:w0", assignment.fencing_token,
                       now=1002.0)
    status = c.status()
    machine = status["machines"]["host-a"]
    assert machine["hostname"] == "host-a"
    assert machine["heartbeat_at"] == 1000.0
    assert machine["version_status"] == "current"
    assert machine["worker_ids"] == ["host-a:w0", "host-a:w1"]


def test_heartbeat_uses_short_retry_budget_and_file_store_ignores_it(tmp_path):
    # The liveness heartbeat must NOT inherit the worker loop's long reconnect
    # budget (a beat that blocked for minutes would starve real work and make an
    # alive process look dead). The Campaign passes a short budget to the store;
    # the file store accepts and ignores it (no network to hang on).
    from egmra.orchestrator.campaign import (
        FileCampaignStore,
        _pg_heartbeat_retry_seconds,
        _pg_retry_seconds,
    )

    assert _pg_heartbeat_retry_seconds() < _pg_retry_seconds()   # short vs long

    store = FileCampaignStore(tmp_path / "state.json")
    # Interface parity: both accept the keyword and behave identically.
    store.write({"campaign_id": "c", "order": [], "fencing_counter": 0,
                 "assignments": {}, "machines": {}}, retry_seconds=15.0)
    assert store.read(retry_seconds=15.0)["campaign_id"] == "c"

    c = _campaign(tmp_path, workers=("host-a:w0",))
    c.initialize("camp-hb", ["p1"])
    metadata = {"hostname": "host-a", "process_id": 1,
                "worker_ids": ["host-a:w0"], "started_at": 100.0}
    c.machine_heartbeat("host-a", metadata=metadata, now=110.0)  # no exception
    assert c.status()["machines"]["host-a"]["heartbeat_at"] == 110.0


def test_heartbeat_budget_env_override_and_clamp(monkeypatch):
    from egmra.orchestrator.campaign import _pg_heartbeat_retry_seconds
    monkeypatch.delenv("EGMRA_PG_HEARTBEAT_RETRY_SECONDS", raising=False)
    assert _pg_heartbeat_retry_seconds() == 20.0
    monkeypatch.setenv("EGMRA_PG_HEARTBEAT_RETRY_SECONDS", "5")
    assert _pg_heartbeat_retry_seconds() == 5.0
    monkeypatch.setenv("EGMRA_PG_HEARTBEAT_RETRY_SECONDS", "9999")
    assert _pg_heartbeat_retry_seconds() == 120.0     # clamped to the ceiling
    monkeypatch.setenv("EGMRA_PG_HEARTBEAT_RETRY_SECONDS", "oops")
    assert _pg_heartbeat_retry_seconds() == 20.0      # falls back to default


def test_machine_graceful_stop_and_restart_preserve_start_time(tmp_path):
    c = _campaign(tmp_path)
    c.initialize("camp-machines", ["p1"])
    metadata = {"hostname": "host-a", "process_id": 1,
                "worker_ids": ["host-a:w0"], "started_at": 100.0}
    c.machine_heartbeat("host-a", metadata=metadata, now=110.0)
    c.machine_stopped("host-a", now=120.0)
    assert c.status()["machines"]["host-a"]["stopped_at"] == 120.0
    # A new heartbeat clears stopped_at but keeps the original registration
    # start time for this machine identity.
    metadata["process_id"] = 2
    c.machine_heartbeat("host-a", metadata=metadata, now=130.0)
    machine = c.status()["machines"]["host-a"]
    assert machine["stopped_at"] == 0.0
    assert machine["started_at"] == 100.0
    assert machine["process_id"] == 2


def test_five_workers_each_problem_assigned_exactly_once(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, workers=("w0", "w1", "w2", "w3", "w4"))
    problems = [f"p{i}" for i in range(12)]
    c.initialize("camp", problems)
    # Each worker leases in turn; no problem is handed out twice, none skipped.
    leased, tokens = [], set()
    while True:
        got = None
        for w in c.worker_ids:
            a = c.lease(w, now=clock.now())
            if a is not None:
                assert a.problem_id not in leased, "duplicate assignment"
                assert a.fencing_token not in tokens, "duplicate fencing token"
                leased.append(a.problem_id)
                tokens.add(a.fencing_token)
                c.complete(a.problem_id, w, a.fencing_token, result_state="OPEN_NO_PROGRESS")
                got = a
        if got is None:
            break
    assert sorted(leased) == sorted(problems)   # no index lost, none duplicated
    assert c.status()["complete"] is True


def test_stale_fencing_token_cannot_complete(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path)
    c.initialize("camp", ["p1"])
    a1 = c.lease("w0", now=clock.now())
    # Lease expires; the problem is re-leased with a new fencing token.
    clock.t += 10_000
    a2 = c.lease("w0", now=clock.now())
    assert a2.fencing_token != a1.fencing_token
    # The stale holder cannot complete or overwrite the problem.
    assert c.complete("p1", "w0", a1.fencing_token, result_state="X") is False
    # The current holder can.
    assert c.complete("p1", "w0", a2.fencing_token, result_state="OPEN_NO_PROGRESS") is True


def test_expired_lease_is_reassigned_no_problem_lost(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, lease_seconds=100.0)
    c.initialize("camp", ["p1"])
    c.lease("w0", now=clock.now())          # w0 "crashes" holding the lease
    assert c.pending_count() == 1
    clock.t += 200                          # lease expires
    a = c.lease("w0", now=clock.now())      # another attempt reclaims it
    assert a is not None and a.problem_id == "p1"


def test_provider_unavailable_retains_problem_not_failed(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path)
    c.initialize("camp", ["p1"])

    calls = {"n": 0}

    class Throttled(Exception):
        pass

    def runner(pid, token):
        calls["n"] += 1
        if calls["n"] == 1:
            raise Throttled()          # first attempt throttled -> retained
        return "OPEN_NO_PROGRESS"      # retried later -> done

    st = c.drain(runner, now=clock.now, provider_unavailable=Throttled)
    assert st["complete"] is True
    assert st["workers"]["p1"]["status"] == "done"
    assert calls["n"] == 2             # retained then retried, never failed


def test_runtime_probe_outage_is_infrastructure_and_refunds_math_attempt(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path)
    c.initialize("camp", ["p1"])
    calls = {"n": 0}

    def runner(_problem_id, _fencing_token, _worker_id):
        calls["n"] += 1
        raise ValueError("Python executable failed the isolated runtime probe")

    status = c.run_concurrent(
        runner, max_workers=1, now=clock.now,
        stop_requested=lambda: calls["n"] >= 1,
        outage_backoff=lambda _attempt: 0.0,
        sleep=lambda _seconds: None,
    )

    row = status["workers"]["p1"]
    assert row["status"] == "retained"
    assert row["attempts"] == 0
    assert row["result_state"] == (
        "ValueError: Python executable failed the isolated runtime probe")


def test_kill_and_restart_resumes_without_skip_or_duplicate(tmp_path):
    clock = _Clock()
    problems = [f"p{i}" for i in range(6)]
    # First "process": complete only the first 3, then die.
    c1 = _campaign(tmp_path)
    c1.initialize("camp", problems)
    done_first = []
    for _ in range(3):
        a = c1.lease("w0", now=clock.now())
        c1.complete(a.problem_id, "w0", a.fencing_token, result_state="OPEN_NO_PROGRESS")
        done_first.append(a.problem_id)

    # Second "process": a fresh Campaign object over the same durable state resumes.
    c2 = _campaign(tmp_path)
    processed = []
    st = c2.drain(lambda pid, tok: processed.append(pid) or "OPEN_NO_PROGRESS", now=clock.now)
    assert st["complete"] is True
    # Resume processed exactly the remaining problems — no dup, no skip.
    assert sorted(processed) == sorted(set(problems) - set(done_first))
    assert set(done_first).isdisjoint(processed)


def test_tampered_state_fails_closed(tmp_path):
    c = _campaign(tmp_path)
    c.initialize("camp", ["p1", "p2"])
    raw = (tmp_path / "campaign.json").read_text()
    tampered = raw.replace("p1", "pX")     # mutate body without re-signing
    (tmp_path / "campaign.json").write_text(tampered)
    with pytest.raises(CampaignError, match="signature"):
        c.status()


def test_max_attempts_marks_failed(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, max_attempts=2)
    c.initialize("camp", ["p1"])

    def runner(pid, tok):
        raise RuntimeError("boom")

    st = c.drain(runner, now=clock.now)
    assert st["workers"]["p1"]["status"] == "failed"
    assert st["complete"] is True


def test_requeue_failed_resets_only_failed_problems(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, max_attempts=1)
    c.initialize("camp", ["p1", "p2", "p3"])
    # p1 fails (exhausts its single attempt); p2 completes; p3 stays pending.
    a1 = c.lease("w0", now=clock.now())
    c.fail(a1.problem_id, "w0", a1.fencing_token, reason="RuntimeError: infra")
    a2 = c.lease("w0", now=clock.now())
    c.complete(a2.problem_id, "w0", a2.fencing_token, result_state="OPEN_NO_PROGRESS")
    assert c.status()["by_status"].get("failed") == 1

    requeued = c.requeue_failed()
    assert requeued == ["p1"]                       # only the failed one
    st = c.status()
    assert st["by_status"].get("failed") is None    # p1 no longer failed
    assert st["workers"]["p1"]["status"] == "pending" and st["workers"]["p1"]["attempts"] == 0
    assert st["workers"]["p2"]["status"] == "done"  # completed problem untouched
    # A requeued problem can be leased and completed on its fresh attempt.
    a = c.lease("w0", now=clock.now())
    assert a.problem_id == "p1" and a.attempts == 1
    assert c.requeue_failed() == []                 # nothing failed now -> no-op


def test_rejects_more_than_five_workers(tmp_path):
    with pytest.raises(CampaignError):
        _campaign(tmp_path, workers=tuple(f"w{i}" for i in range(6)))


# ── crash-burned attempt budgets are infrastructure, not math (live incident) ──

def test_expired_lease_refunds_attempt_and_charges_infra_budget(tmp_path):
    """A dead process's expired lease never spends the mathematical budget.

    Live incident: a repeatedly-crashing machine leased the same problem five
    times (each expiry burning an attempt) and the problem was marked failed
    without a single recorded outcome. Expired-lease pickup now mirrors
    ``retain``: refund the attempt, charge the infrastructure budget.
    """
    clock = _Clock()
    c = _campaign(tmp_path, max_attempts=2, lease_seconds=10.0)
    c.initialize("camp", ["p1"])
    for crash in range(1, 4):     # three crash/expiry cycles > max_attempts
        assignment = c.lease("w0", now=clock.now())
        assert assignment is not None and assignment.problem_id == "p1"
        clock.t += 11.0           # holder dies; lease expires; nothing recorded
        row = c.status()["workers"]["p1"]
        assert row["attempts"] == 1  # the single live lease, never accumulating
    # After all those crashes the problem is still leasable with a full
    # mathematical budget, and the crashes were charged to infrastructure.
    assignment = c.lease("w0", now=clock.now())
    assert assignment is not None
    row = c.status()["workers"]["p1"]
    assert row["attempts"] == 1
    assert row["infra_retries"] == 3
    # A genuinely recorded outcome still completes normally.
    assert c.complete("p1", "w0", assignment.fencing_token,
                      result_state="OPEN_NO_PROGRESS")


def test_crash_looping_problem_is_bounded_by_infra_budget(tmp_path):
    """A permanently crashing environment terminates honestly (never spins)."""
    clock = _Clock()
    c = _campaign(tmp_path, max_attempts=5, max_infra_retries=3,
                  lease_seconds=10.0)
    c.initialize("camp", ["p1"])
    for _ in range(3):            # each cycle: lease, die, expire
        assert c.lease("w0", now=clock.now()) is not None
        clock.t += 11.0
    assert c.lease("w0", now=clock.now()) is None   # infra budget spent
    row = c.status()["workers"]["p1"]
    assert row["status"] == "failed"
    assert row["result_state"].startswith("infrastructure_budget_exhausted")
    # And the automatic startup requeue gives it a fresh run next launch.
    assert c.requeue_failed(infra_only=True) == ["p1"]


def test_is_infrastructure_failure_classification():
    from egmra.orchestrator.campaign import _is_infrastructure_failure

    assert _is_infrastructure_failure("")                       # legacy crash-burn
    assert _is_infrastructure_failure("  ")
    assert _is_infrastructure_failure(
        "attempt_budget_exhausted_without_result")
    assert _is_infrastructure_failure(
        "infrastructure_budget_exhausted: provider_unavailable")
    assert _is_infrastructure_failure(
        "ValueError: Python executable failed the isolated runtime probe")
    assert not _is_infrastructure_failure(
        "SourceResolutionError: no statement")                  # genuine verdicts
    assert not _is_infrastructure_failure("ValueError: malformed")


def test_infra_only_requeue_still_skips_genuine_failures(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, max_attempts=1)
    c.initialize("camp", ["p1"])
    a = c.lease("w0", now=clock.now())
    c.fail(a.problem_id, "w0", a.fencing_token,
           reason="ValueError: genuinely malformed statement", permanent=True)
    assert c.status()["workers"]["p1"]["status"] == "failed"
    # A recorded genuine failure reason is NOT an infrastructure artifact.
    assert c.requeue_failed(infra_only=True) == []
    # The unrestricted (operator-invoked) requeue still can.
    assert c.requeue_failed() == ["p1"]


def test_pg_retry_seconds_default_override_and_clamp(monkeypatch):
    from egmra.orchestrator.campaign import _pg_retry_seconds

    monkeypatch.delenv("EGMRA_PG_RETRY_SECONDS", raising=False)
    assert _pg_retry_seconds() == 300.0
    monkeypatch.setenv("EGMRA_PG_RETRY_SECONDS", "45")
    assert _pg_retry_seconds() == 45.0
    monkeypatch.setenv("EGMRA_PG_RETRY_SECONDS", "999999")
    assert _pg_retry_seconds() == 3600.0
    monkeypatch.setenv("EGMRA_PG_RETRY_SECONDS", "-5")
    assert _pg_retry_seconds() == 0.0
    monkeypatch.setenv("EGMRA_PG_RETRY_SECONDS", "not-a-number")
    assert _pg_retry_seconds() == 300.0


# ── real concurrency (defect 4.2) ───────────────────────────────────────────

def test_run_concurrent_has_real_overlap_across_five_workers(tmp_path):
    # A Barrier(5) only releases if five workers run the runner SIMULTANEOUSLY;
    # sequential/fake concurrency would deadlock the barrier and fail the tasks.
    clock = _Clock()
    c = _campaign(tmp_path, workers=tuple(f"w{i}" for i in range(5)), lease_seconds=1000.0)
    problems = [f"p{i}" for i in range(5)]
    c.initialize("camp", problems)
    barrier = threading.Barrier(5, timeout=10)

    def runner(problem_id, token, worker_id):
        barrier.wait()          # all five must arrive together
        return "OPEN_NO_PROGRESS"

    status = c.run_concurrent(runner, max_workers=5, now=clock.now)
    assert status["complete"] is True
    assert status["by_status"].get("done") == 5
    report = status["concurrency"]
    assert report["max_observed_concurrency"] == 5   # genuine 5-way overlap
    assert report["distinct_workers"] == 5           # every worker id did work


# ── lease heartbeat: a long-running problem must not expire mid-work ─────────

def test_heartbeat_extends_lease_only_for_current_holder(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, lease_seconds=100.0)
    c.initialize("camp", ["p1"])
    a = c.lease("w0", now=clock.now())
    assert c.heartbeat("p1", "w0", a.fencing_token, now=clock.now() + 50) is True
    # A stale/superseded token can never renew (prevents zombie extension).
    assert c.heartbeat("p1", "w0", a.fencing_token - 1, now=clock.now() + 60) is False


def test_run_concurrent_heartbeats_lease_during_a_long_runner(tmp_path):
    """A runner longer than lease_seconds keeps its problem (renewed), never re-leased.

    This is THE fix for 'every browser problem fails at attempt 5': a real
    problem takes far longer than the lease, so without renewal it would expire
    mid-work, get re-leased (attempt++), and eventually be marked failed despite
    progress. The heartbeat renews it while the worker is genuinely running.
    """
    import time
    c = _campaign(tmp_path, workers=("w0",), lease_seconds=10.0)
    c.initialize("camp", ["p1"])
    beats = {"n": 0}
    real_hb = c.heartbeat

    def counting_hb(*a, **k):
        beats["n"] += 1
        return real_hb(*a, **k)
    c.heartbeat = counting_hb

    def runner(problem_id, token, worker_id):
        time.sleep(0.3)                      # several heartbeat intervals long
        return "OPEN_NO_PROGRESS"

    status = c.run_concurrent(runner, max_workers=1, now=time.time,
                              heartbeat_interval=0.05)
    assert status["by_status"].get("done") == 1     # completed, not failed
    assert status["workers"]["p1"]["attempts"] == 1  # never re-leased
    assert beats["n"] >= 3                            # lease renewed repeatedly



def test_run_concurrent_no_duplicate_or_skipped_problems(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, workers=tuple(f"w{i}" for i in range(3)))
    problems = [f"p{i}" for i in range(15)]
    c.initialize("camp", problems)
    processed: list[str] = []
    lock = threading.Lock()

    def runner(problem_id, token, worker_id):
        with lock:
            processed.append(problem_id)
        return "OPEN_NO_PROGRESS"

    status = c.run_concurrent(runner, max_workers=3, now=clock.now)
    assert status["complete"] is True
    assert sorted(processed) == sorted(problems)     # none skipped
    assert len(processed) == len(set(processed))     # none duplicated
    assert status["concurrency"]["distinct_workers"] <= 3


def test_worker_does_not_exit_permanently_on_a_transient_unleasable_pool(tmp_path):
    """A worker that momentarily can't lease must stay alive while work exists.

    Regression for the observed 'a machine sits at <3 workers with hundreds of
    problems still waiting' degradation: with a shared cross-machine pool a
    worker can briefly get no leasable problem (another machine holds them all)
    while its own machine has no other busy worker at that instant. The old
    ``busy and pending>0`` guard let it EXIT permanently (no respawn). It must
    instead keep polling until the pool is genuinely drained.
    """
    c = _campaign(tmp_path, workers=("w0",))
    c.initialize("camp", ["p1"])
    real_lease = c.lease
    calls = {"n": 0}

    def flaky_lease(worker_id, *, now):
        # First few attempts: nothing leasable (held by 'another machine'),
        # but the problem is still pending so pending_count() > 0.
        calls["n"] += 1
        if calls["n"] <= 3:
            return None
        return real_lease(worker_id, now=now)

    c.lease = flaky_lease
    ran = {"n": 0}

    def runner(problem_id, token, worker_id):
        ran["n"] += 1
        return "OPEN_NO_PROGRESS"

    status = c.run_concurrent(
        runner, max_workers=1, now=_Clock().now,
        poll_interval=0.0, idle_poll_interval=0.0, sleep=lambda _s: None)
    assert ran["n"] == 1                          # resumed and worked the problem
    assert calls["n"] >= 4                         # polled through the transient Nones
    assert status["by_status"].get("done") == 1    # and the pool drained cleanly


def test_persistent_fleet_worker_outlives_the_old_idle_retry_window(tmp_path):
    c = _campaign(tmp_path, workers=("w0",))
    c.initialize("camp", ["p1"])
    real_lease = c.lease
    calls = {"n": 0}

    def delayed_lease(worker_id, *, now):
        calls["n"] += 1
        if calls["n"] <= 40:  # longer than the former 15-poll fleet window
            return None
        return real_lease(worker_id, now=now)

    c.lease = delayed_lease
    status = c.run_concurrent(
        lambda _problem, _token, _worker: "OPEN_NO_PROGRESS",
        max_workers=1, now=_Clock().now, max_idle_resume_polls=None,
        idle_poll_interval=0.0, sleep=lambda _seconds: None,
    )
    assert calls["n"] == 42  # includes the final terminal-queue check
    assert status["by_status"] == {"done": 1}


def test_run_concurrent_cooperative_stop_finishes_current_problem(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, workers=("w0",))
    c.initialize("camp", ["p1", "p2"])
    stop = threading.Event()

    def runner(problem_id, token, worker_id):
        stop.set()
        return "OPEN_NO_PROGRESS"

    status = c.run_concurrent(
        runner, max_workers=1, now=clock.now, stop_requested=stop.is_set)
    assert status["stop_requested"] is True
    assert status["by_status"]["done"] == 1
    assert status["by_status"]["pending"] == 1
    assert status["workers"]["p1"]["status"] == "done"
    assert status["workers"]["p2"]["status"] == "pending"


def test_run_concurrent_is_bounded_by_max_workers(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, workers=tuple(f"w{i}" for i in range(5)), lease_seconds=1000.0)
    c.initialize("camp", [f"p{i}" for i in range(8)])
    seen = {"peak": 0}
    lock = threading.Lock()
    live = {"n": 0}

    def runner(problem_id, token, worker_id):
        with lock:
            live["n"] += 1
            seen["peak"] = max(seen["peak"], live["n"])
        import time as _t
        _t.sleep(0.02)
        with lock:
            live["n"] -= 1
        return "OPEN_NO_PROGRESS"

    status = c.run_concurrent(runner, max_workers=2, now=clock.now)
    assert status["complete"] is True
    assert seen["peak"] <= 2                          # never exceeds the bound
    assert status["concurrency"]["max_observed_concurrency"] <= 2


def test_run_concurrent_recovers_from_worker_crash(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, workers=tuple(f"w{i}" for i in range(3)), max_attempts=5)
    c.initialize("camp", [f"p{i}" for i in range(6)])
    crashed = {"once": set()}
    lock = threading.Lock()

    def runner(problem_id, token, worker_id):
        with lock:
            first = problem_id not in crashed["once"]
            crashed["once"].add(problem_id)
        if first and problem_id == "p3":
            raise RuntimeError("worker crashed mid-problem")
        return "OPEN_NO_PROGRESS"

    status = c.run_concurrent(runner, max_workers=3, now=clock.now)
    assert status["complete"] is True                 # crashed problem recovered
    assert status["workers"]["p3"]["status"] == "done"


def test_run_concurrent_survives_transient_store_outage_during_lease(tmp_path):
    # Live 2026-07-16: the internet dropped, the Neon pooler became
    # unreachable, and uncaught psycopg errors from the lease/complete writes
    # killed every worker thread — the process stayed alive (heartbeat daemon)
    # but did zero research. A store blip during leasing must now back off and
    # retry, never kill the worker; the campaign still drains.
    clock = _Clock()
    flaky = _FlakyStore(FileCampaignStore(tmp_path / "campaign.json"))
    c = Campaign(tmp_path / "campaign.json", worker_ids=("w0",), store=flaky)
    c.initialize("camp", ["p0", "p1"])
    flaky.arm(skip=0, then_fail=3)          # the next 3 writes (leasing p0) raise

    def runner(problem_id, token, worker_id):
        return "OPEN_NO_PROGRESS"

    status = c.run_concurrent(
        runner, max_workers=1, now=clock.now,
        outage_backoff=lambda _n: 0.0, sleep=lambda _s: None)
    assert status["complete"] is True                  # drained despite the blip
    assert status["by_status"]["done"] == 2


def test_run_concurrent_completion_write_failure_does_not_kill_worker(tmp_path):
    # A blip that loses the COMPLETION write must not crash the worker or burn
    # the attempt: the worker survives to finish the next problem, and the
    # unrecorded one stays leased for the normal expiry-reclaim path.
    clock = _Clock(1000.0)                              # static: leases never expire here
    flaky = _FlakyStore(FileCampaignStore(tmp_path / "campaign.json"))
    c = Campaign(tmp_path / "campaign.json", worker_ids=("w0",),
                 lease_seconds=1000.0, store=flaky)
    c.initialize("camp", ["p0", "p1"])
    flaky.arm(skip=1, then_fail=1)          # lease p0 ok (#1), complete p0 fails (#2)

    def runner(problem_id, token, worker_id):
        return "OPEN_NO_PROGRESS"

    status = c.run_concurrent(
        runner, max_workers=1, now=clock.now,
        outage_backoff=lambda _n: 0.0, sleep=lambda _s: None)
    # The worker survived the lost completion and finished p1.
    assert status["workers"]["p1"]["status"] == "done"
    # p0's completion was lost to the blip -> left leased for reclaim, never a
    # spurious done/failed, and its attempt is not wrongly spent.
    assert status["workers"]["p0"]["status"] == "leased"
    assert status["workers"]["p0"]["attempts"] == 1


def test_run_concurrent_does_not_retry_declared_permanent_failure(tmp_path):
    class PermanentInputError(Exception):
        pass

    clock = _Clock()
    c = _campaign(tmp_path, workers=("w0",), max_attempts=5)
    c.initialize("permanent", ["missing-source"])
    calls = 0

    def runner(_problem_id, _fencing_token, _worker_id):
        nonlocal calls
        calls += 1
        raise PermanentInputError("source is absent")

    status = c.run_concurrent(
        runner, max_workers=1, now=clock.now,
        permanent_failure=PermanentInputError,
    )
    assert calls == 1
    assert status["workers"]["missing-source"]["status"] == "failed"
    assert status["workers"]["missing-source"]["attempts"] == 1
    assert "PermanentInputError" in status["workers"]["missing-source"]["result_state"]


def test_heartbeat_extends_lease_and_rejects_stale_token(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, lease_seconds=100.0)
    c.initialize("camp", ["p1"])
    a = c.lease("w0", now=clock.now())
    assert c.heartbeat("p1", "w0", a.fencing_token, now=clock.now()) is True
    assert c.heartbeat("p1", "w0", a.fencing_token + 99, now=clock.now()) is False


# ── infrastructure failures must not burn the mathematical attempt budget ────

def test_retain_refunds_attempt_and_spends_infra_budget(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, max_attempts=2)
    c.initialize("camp", ["p1"])
    # Throttle/closed-tab retains far more often than max_attempts allows...
    for _ in range(6):
        a = c.lease("w0", now=clock.now())
        assert a is not None, "problem must survive repeated infra retains"
        assert c.retain(a.problem_id, "w0", a.fencing_token, reason="throttled")
    st = c.status()["workers"]["p1"]
    # ...yet the MATHEMATICAL budget is untouched (every attempt refunded)
    assert st["attempts"] == 0 and st["status"] == "retained"
    assert st["infra_retries"] == 6
    # and the problem still completes normally afterwards.
    a = c.lease("w0", now=clock.now())
    assert c.complete(a.problem_id, "w0", a.fencing_token,
                      result_state="OPEN_NO_PROGRESS")


def test_infra_budget_exhaustion_fails_honestly(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path, max_infra_retries=3)
    c.initialize("camp", ["p1"])
    for _ in range(3):
        a = c.lease("w0", now=clock.now())
        c.retain(a.problem_id, "w0", a.fencing_token, reason="provider down")
    st = c.status()["workers"]["p1"]
    assert st["status"] == "failed"
    assert st["result_state"].startswith("infrastructure_budget_exhausted")
    # A permanently broken environment terminates: nothing left to lease.
    assert c.lease("w0", now=clock.now()) is None


def test_requeue_promising_is_evidence_bounded(tmp_path):
    clock = _Clock()
    c = _campaign(tmp_path)
    c.initialize("camp", ["p1", "p2"])
    for pid in ("p1", "p2"):
        a = c.lease("w0", now=clock.now())
        c.complete(a.problem_id, "w0", a.fencing_token,
                   result_state="PARTIAL_PROGRESS" if pid == "p1" else "OPEN_NO_PROGRESS")
    # Caller (the CLI) decides which are promising; only DONE + wanted requeue.
    assert c.requeue_promising(["p1"]) == ["p1"]
    st = c.status()["workers"]
    assert st["p1"]["status"] == "pending" and st["p2"]["status"] == "done"
    # Bounded: after max_resamples completions, no further resample.
    a = c.lease("w0", now=clock.now())
    c.complete(a.problem_id, "w0", a.fencing_token, result_state="PARTIAL_PROGRESS")
    assert c.requeue_promising(["p1"]) == ["p1"]           # resample 2
    a = c.lease("w0", now=clock.now())
    c.complete(a.problem_id, "w0", a.fencing_token, result_state="PARTIAL_PROGRESS")
    assert c.requeue_promising(["p1"]) == []               # budget spent
    assert c.requeue_promising(["p2", "missing"]) == ["p2"]  # p2's first resample
