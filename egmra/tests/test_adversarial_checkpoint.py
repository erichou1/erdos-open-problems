"""Adversarial checkpoint/resume tests for the durable-run trust boundary."""

from __future__ import annotations

from dataclasses import replace

import pytest

from egmra.orchestrator.checkpoint import resume, take_checkpoint
from egmra.provenance.hashing import sha256_hex
from egmra.truth.events import EventLog


ACTOR = {"type": "agent", "id": "checkpoint-auditor"}


def _h(label: str) -> str:
    return sha256_hex(label)


def _log(tmp_path, name: str = "events.jsonl", *, run_id: str = "run-a") -> EventLog:
    return EventLog(tmp_path / name, run_id=run_id)


def _checkpoint(log: EventLog, **overrides):
    values = {
        "problem_contract_hash": _h("problem-contract"),
        "interpretation_hashes": (_h("interpretation"),),
        "graph_view_hash": _h("graph-view"),
        "controller_posteriors": {"branch": {"alpha": 2.0, "beta": 3.0}},
        "budgets": {"tokens": 100.0},
        "seeds": {"controller": 7},
        "active_leases": ("lease-1",),
        "behavior_closure_fingerprint": _h("closure-v1"),
        "stage_caches": {
            "scout": {
                "artifact_hash": _h("scout-artifact"),
                "compatibility_fingerprint": _h("scout-identity"),
                "replay_policy_hash": _h("scout-replay-policy"),
                "durable_stage": 1,
            }
        },
        "rate_limit_state": {
            "provider": {"blocked_until": 12.5, "quota_remaining": 4}
        },
    }
    values.update(overrides)
    return take_checkpoint(log=log, **values)


def test_checkpoint_is_deeply_immutable_and_detached_from_inputs(tmp_path) -> None:
    log = _log(tmp_path)
    log.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=["p"])
    posteriors = {"branch": {"alpha": 2.0, "beta": 3.0}}
    caches = {
        "scout": {
            "artifact_hash": _h("scout-artifact"),
            "compatibility_fingerprint": _h("scout-identity"),
            "replay_policy_hash": _h("scout-replay-policy"),
            "durable_stage": 1,
        }
    }
    checkpoint = _checkpoint(
        log, controller_posteriors=posteriors, stage_caches=caches
    )

    posteriors["branch"]["alpha"] = 999.0
    caches["scout"]["durable_stage"] = 999
    assert checkpoint.controller_posteriors["branch"]["alpha"] == 2.0
    assert checkpoint.stage_caches["scout"]["durable_stage"] == 1
    with pytest.raises(TypeError):
        checkpoint.controller_posteriors["branch"]["alpha"] = 4.0
    with pytest.raises(TypeError):
        checkpoint.stage_caches["new"] = {}


def test_checkpoint_hash_commits_every_semantic_field(tmp_path) -> None:
    log = _log(tmp_path)
    log.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=["p"])
    checkpoint = _checkpoint(log)

    mutations = (
        {"problem_contract_hash": _h("other-problem-contract")},
        {"interpretation_hashes": (_h("other-interpretation"),)},
        {"graph_view_hash": _h("other-graph-view")},
        {"controller_posteriors": {"branch": {"alpha": 9.0, "beta": 3.0}}},
        {"budgets": {"tokens": 99.0}},
        {"seeds": {"controller": 8}},
        {"active_leases": ("lease-2",)},
        {"in_flight_calls": ("call-2",)},
        {"behavior_closure_fingerprint": _h("closure-v2")},
        {"stage_caches": {}},
        {"rate_limit_state": {}},
    )
    for change in mutations:
        changed = _checkpoint(log, **change)
        assert changed.checkpoint_hash() != checkpoint.checkpoint_hash(), change

    for change in (
        {"run_id": "another-run"},
        {"last_sequence": checkpoint.last_sequence + 1},
        {"last_event_id": _h("another-last-event")},
        {"merkle_root": _h("another-prefix-root")},
    ):
        changed = replace(checkpoint, _sealed_hash="", **change)
        assert changed.checkpoint_hash() != checkpoint.checkpoint_hash(), change

    corrupted_schema = replace(checkpoint)
    object.__setattr__(corrupted_schema, "schema_version", 2)
    assert corrupted_schema.checkpoint_hash() != checkpoint.checkpoint_hash()
    assert not corrupted_schema.verify_checkpoint_hash()


def test_resume_rejects_checkpoint_from_another_valid_log(tmp_path) -> None:
    first = _log(tmp_path, "first.jsonl", run_id="same-run-label")
    second = _log(tmp_path, "second.jsonl", run_id="same-run-label")
    first.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=["p-one"])
    second.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=["p-two"])
    checkpoint = _checkpoint(first)

    report = resume(
        checkpoint,
        log=second,
        current_closure_fingerprint=checkpoint.behavior_closure_fingerprint,
    )
    assert not report.ok
    assert not report.chain_verified
    assert report.resumed_from_sequence == -1


def test_resume_accepts_the_exact_prefix_with_a_valid_appended_tail(tmp_path) -> None:
    log = _log(tmp_path)
    log.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=["p"])
    checkpoint = _checkpoint(log)
    log.append(action="BRANCH_OPENED", actor=ACTOR, object_ids=["b"])

    report = resume(
        checkpoint,
        log=log,
        current_closure_fingerprint=checkpoint.behavior_closure_fingerprint,
    )
    assert report.ok and report.chain_verified
    assert report.resumed_from_sequence == checkpoint.last_sequence


def test_resume_fails_closed_if_checkpoint_contents_are_corrupted(tmp_path) -> None:
    log = _log(tmp_path)
    log.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=["p"])
    checkpoint = _checkpoint(log)
    object.__setattr__(checkpoint, "graph_view_hash", _h("forged-graph-view"))

    report = resume(
        checkpoint,
        log=log,
        current_closure_fingerprint=checkpoint.behavior_closure_fingerprint,
    )
    assert not report.ok
    assert report.resumed_from_sequence == -1


def test_recomputing_a_plain_content_hash_cannot_forge_checkpoint_state(tmp_path) -> None:
    log = _log(tmp_path)
    checkpoint = _checkpoint(log)
    forged = replace(
        checkpoint,
        budgets={"tokens": 1_000_000_000.0},
        _sealed_hash="",
    )
    assert forged.checkpoint_hash() != checkpoint.checkpoint_hash()

    report = resume(
        forged,
        log=log,
        current_closure_fingerprint=forged.behavior_closure_fingerprint,
    )
    assert not report.ok, "a self-computed content hash is not an authority signature"


def test_checkpoint_requires_a_secret_and_rejects_the_wrong_verification_key(
    tmp_path, monkeypatch
) -> None:
    log = _log(tmp_path)
    checkpoint = _checkpoint(log)
    assert not checkpoint.verify_checkpoint_hash(
        env={"EGMRA_CHECKPOINT_KEY": "wrong-checkpoint-key-that-is-at-least-32-bytes"}
    )

    monkeypatch.delenv("EGMRA_CHECKPOINT_KEY")
    with pytest.raises((TypeError, ValueError)):
        _checkpoint(log)


def test_resume_rejects_a_resealed_but_inconsistent_sequence_and_merkle(tmp_path) -> None:
    log = _log(tmp_path)
    log.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=["p"])
    checkpoint = _checkpoint(log)
    inconsistent = replace(
        checkpoint,
        last_sequence=checkpoint.last_sequence + 1,
        merkle_root=_h("invented-prefix-root"),
        _sealed_hash="",
    )
    # Model a buggy/compromised checkpoint issuer: even a valid signature must
    # not substitute for proving the claimed event prefix.
    inconsistent._sign()
    assert inconsistent.verify_checkpoint_hash(), "self-consistent content is not a log proof"

    report = resume(
        inconsistent,
        log=log,
        current_closure_fingerprint=inconsistent.behavior_closure_fingerprint,
    )
    assert not report.ok and not report.chain_verified


def test_resume_fails_closed_on_event_log_corruption(tmp_path) -> None:
    log = _log(tmp_path)
    log.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=["p"])
    checkpoint = _checkpoint(log)
    log.path.write_text(
        log.path.read_text(encoding="utf-8").replace('"p"', '"forged"'),
        encoding="utf-8",
    )

    report = resume(
        checkpoint,
        log=log,
        current_closure_fingerprint=checkpoint.behavior_closure_fingerprint,
    )
    assert not report.ok and not report.chain_verified


def test_take_checkpoint_rejects_malformed_schema_and_digests(tmp_path) -> None:
    log = _log(tmp_path)
    with pytest.raises((TypeError, ValueError)):
        _checkpoint(log, problem_contract_hash="not-a-digest")
    with pytest.raises((TypeError, ValueError)):
        _checkpoint(log, interpretation_hashes=[_h("mutable-list")])
    with pytest.raises((TypeError, ValueError)):
        _checkpoint(log, seeds={"controller": True})
    with pytest.raises((TypeError, ValueError)):
        _checkpoint(log, budgets={"tokens": float("inf")})
    with pytest.raises((TypeError, ValueError)):
        _checkpoint(log, stage_caches={"scout": {"artifact_hash": _h("only-one")}})
    with pytest.raises((TypeError, ValueError)):
        _checkpoint(log, rate_limit_state={"provider": {"unknown": 1}})
    with pytest.raises((TypeError, ValueError)):
        replace(_checkpoint(log), schema_version=2)


def test_interrupted_calls_must_be_unique_nonempty_identifiers(tmp_path) -> None:
    log = _log(tmp_path)
    checkpoint = _checkpoint(log)
    for bad in (("",), ("call", "call"), (1,), ["call"]):
        with pytest.raises((TypeError, ValueError)):
            resume(
                checkpoint,
                log=log,
                current_closure_fingerprint=checkpoint.behavior_closure_fingerprint,
                interrupted_calls=bad,
            )


def test_resume_cannot_mark_an_unrecorded_call_as_censored(tmp_path) -> None:
    log = _log(tmp_path)
    checkpoint = _checkpoint(log)
    with pytest.raises((TypeError, ValueError)):
        resume(
            checkpoint,
            log=log,
            current_closure_fingerprint=checkpoint.behavior_closure_fingerprint,
            interrupted_calls=("not-in-flight-at-checkpoint",),
        )


def test_resume_supports_precise_per_stage_cache_invalidation(tmp_path) -> None:
    log = _log(tmp_path)
    checkpoint = _checkpoint(
        log,
        stage_caches={
            "scout": {
                "artifact_hash": _h("scout-artifact"),
                "compatibility_fingerprint": _h("scout-v1"),
                "replay_policy_hash": _h("scout-replay"),
                "durable_stage": 1,
            },
            "formal": {
                "artifact_hash": _h("formal-artifact"),
                "compatibility_fingerprint": _h("formal-v1"),
                "replay_policy_hash": _h("formal-replay"),
                "durable_stage": 2,
            },
        },
    )
    try:
        report = resume(
            checkpoint,
            log=log,
            current_closure_fingerprint=_h("closure-v2"),
            current_stage_fingerprints={
                "scout": _h("scout-v1"),
                "formal": _h("formal-v2"),
            },
        )
    except TypeError as exc:
        pytest.fail(f"resume lacks per-stage compatibility input: {exc}")
    assert report.invalidated_caches == ("formal",)


def test_missing_stage_identity_invalidates_cache_even_when_global_closure_matches(
    tmp_path,
) -> None:
    log = _log(tmp_path)
    checkpoint = _checkpoint(log)
    try:
        report = resume(
            checkpoint,
            log=log,
            current_closure_fingerprint=checkpoint.behavior_closure_fingerprint,
            current_stage_fingerprints={},
        )
    except TypeError as exc:
        pytest.fail(f"resume lacks fail-closed per-stage compatibility input: {exc}")
    assert report.invalidated_caches == ("scout",)
