"""Tests for the CLI and configuration."""

import argparse
import json
import os

import pytest

import egmra.cli as cli_module
from egmra.cli import _fixture_worker, main
from egmra.eval.datasets import FixtureProblem, fixture
from egmra.config import SECRET_ENV_VARS, EgmraConfig
from egmra.intake import build_problem_contract
from egmra.intake.review import interpretation_review_hash, sign_intent_certificate
from egmra.policy import load_policy, sign_policy
from egmra.provenance.hashing import sha256_hex
from egmra.truth.entities import IntentCertificate, Verdict
from egmra.truth.events import EventLog
from egmra.ranking_queue import build_queue_projection


# ── liveness watchdog (fixes 'process alive but computer shows stale') ────────


@pytest.mark.parametrize("last_ok,now,threshold,expired", [
    (0.0, 100.0, 600.0, False),      # well within budget
    (0.0, 599.0, 600.0, False),      # just under
    (0.0, 601.0, 600.0, True),       # just over -> wedged
    (0.0, 10_000.0, 0.0, False),     # threshold 0 disables the watchdog
    (0.0, 10_000.0, -1.0, False),    # negative disables too
])
def test_liveness_watchdog_expiry_policy(last_ok, now, threshold, expired):
    from egmra.cli import _liveness_watchdog_expired
    assert _liveness_watchdog_expired(last_ok, now, threshold) is expired


def test_liveness_watchdog_seconds_clamps_and_disables(monkeypatch):
    from egmra.cli import _liveness_watchdog_seconds
    monkeypatch.delenv("EGMRA_LIVENESS_WATCHDOG_SECONDS", raising=False)
    assert _liveness_watchdog_seconds() == 600.0
    monkeypatch.setenv("EGMRA_LIVENESS_WATCHDOG_SECONDS", "0")
    assert _liveness_watchdog_seconds() == 0.0        # explicitly disabled
    monkeypatch.setenv("EGMRA_LIVENESS_WATCHDOG_SECONDS", "5")
    assert _liveness_watchdog_seconds() == 300.0      # clamped up to the floor
    monkeypatch.setenv("EGMRA_LIVENESS_WATCHDOG_SECONDS", "99999")
    assert _liveness_watchdog_seconds() == 7200.0     # clamped to the ceiling
    monkeypatch.setenv("EGMRA_LIVENESS_WATCHDOG_SECONDS", "garbage")
    assert _liveness_watchdog_seconds() == 600.0      # falls back to default


def _signed_policy_file(tmp_path, *, promotion: bool = False):
    flags = {
        "claim_graph": True,
        "literature_retrieval": True,
        "computation_service": True,
        "promotion": promotion,
        "formal_promotion": False,
    }
    policy = sign_policy(flags)
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(policy.to_document()))
    return path


def test_campaign_attempt_ids_are_namespaced_and_path_safe():
    first = cli_module._campaign_attempt_id("campaign/a", "erdos-601", 1)
    second = cli_module._campaign_attempt_id("campaign/b", "erdos-601", 1)
    assert first != second
    assert "/" not in first and ".." not in first
    assert ".erdos-601.1." in first
    # Same campaign name + fencing token must still yield a FRESH id: a
    # re-initialized campaign restarts its fencing counter, and a colliding
    # id would replay the previous incarnation's event log (live GraphError).
    again = cli_module._campaign_attempt_id("campaign/a", "erdos-601", 1)
    assert again != first


def _signed_intent_review_file(tmp_path, fixture_id: str):
    fx = fixture(fixture_id)
    contract = build_problem_contract(
        problem_id=fx.problem_id, source_bytes=fx.statement, source_id=fx.problem_id,
        predicate=fx.predicate(),
    )
    interp = contract.lattice.nodes[0]
    certificate = sign_intent_certificate(IntentCertificate(
        certificate_id=f"intent-{fixture_id}",
        source_bytes_hash=contract.source_bytes_hash,
        interpretation_hash=interpretation_review_hash(interp),
        informal_claim_hash=sha256_hex(interp.conclusion),
        methods=[
            "independent_parse", "examples", "anti_examples",
            "paraphrase", "local_mutation",
        ],
        reviewer_ids=["semantic-reviewer"],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "semantic-reviewer",
            "independent_from": ["governor", "intake_retrieval"],
            "conflicts": [],
        }],
        verdict=Verdict.APPROVED,
    ))
    path = tmp_path / f"{fixture_id}-intent-review.json"
    path.write_text(json.dumps(certificate.to_dict()))
    return path


def test_config_layering_and_env_override(tmp_path):
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps({"oeis_offline": False, "protected_exploration_fraction": 0.18}))
    config = EgmraConfig.load(cfg_file, env={"EGMRA_EVENTS_DIR": "/tmp/runs"})
    assert config.oeis_offline is False
    assert config.protected_exploration_fraction == 0.18
    assert config.events_dir == "/tmp/runs"


def test_config_rejects_secrets_in_file(tmp_path):
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps({"OPENAI_API_KEY": "leaked"}))
    with pytest.raises(ValueError):
        EgmraConfig.load(cfg_file)


def test_config_secret_denylist_covers_every_local_trust_key(tmp_path):
    required = {
        "EGMRA_POLICY_KEY", "EGMRA_EVENT_KEY", "EGMRA_EVIDENCE_KEY",
        "EGMRA_RELEASE_KEY", "EGMRA_GATE_KEY", "EGMRA_PROMOTION_KEY",
        "EGMRA_LEAN_CHECKER_KEY", "EGMRA_AUTHORITY_KEY",
        "EGMRA_TRUTH_SNAPSHOT_KEY", "EGMRA_MODEL_ATTESTATION_KEY",
        "EGMRA_INTENT_REVIEW_KEY", "EGMRA_FORMAL_CORRESPONDENCE_KEY",
        "EGMRA_CHECKPOINT_KEY", "EGMRA_LEGACY_REVIEW_KEY",
        "EGMRA_LEGACY_EVIDENCE_KEY",
    }
    assert required.issubset(set(SECRET_ENV_VARS))
    for name in required:
        cfg_file = tmp_path / f"{name}.json"
        cfg_file.write_text(json.dumps({name: "must-not-be-persisted"}))
        with pytest.raises(ValueError, match="secrets must not appear"):
            EgmraConfig.load(cfg_file)


def test_config_public_dict_has_no_secrets():
    config = EgmraConfig()
    public = config.to_public_dict()
    assert not any(s in public for s in SECRET_ENV_VARS)


def test_secret_read_from_env_only():
    assert EgmraConfig.secret("OPENAI_API_KEY", env={}) == ""
    assert EgmraConfig.secret("OPENAI_API_KEY", env={"OPENAI_API_KEY": "k"}) == "k"


def test_cli_run_fixture(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path, promotion=True)
    review = _signed_intent_review_file(tmp_path, "fx-true-square")
    rc = main(["--config", str(cfg), "run", "--fixture", "fx-true-square",
               "--policy", str(policy), "--intent-review", str(review)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["problem_id"] == "fx-true-square"
    assert out["expectation_met"]
    assert out["candidate_assembly_complete"]
    assert out["proof_complete"] is False
    assert out["result_state"]["state"] == "COMPUTATIONAL_EVIDENCE"
    assert out["release"] is not None
    assert out["outcome"] == "verified_finite_or_conditional_result"


def test_cli_fixture_closes_its_event_store(tmp_path, capsys, monkeypatch):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path, promotion=True)
    review = _signed_intent_review_file(tmp_path, "fx-true-square")
    closed = []
    original_close = cli_module._close_event_log

    def record_close(log):
        closed.append(log)
        original_close(log)

    monkeypatch.setattr(cli_module, "_close_event_log", record_close)

    rc = main(["--config", str(cfg), "run", "--fixture", "fx-true-square",
               "--policy", str(policy), "--intent-review", str(review)])

    assert rc == 0
    assert len(closed) == 1
    assert closed[0] is not None
    json.loads(capsys.readouterr().out)


def test_cli_verified_expectation_requires_actual_release_not_candidate_only(
    tmp_path, capsys,
):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path, promotion=False)
    review = _signed_intent_review_file(tmp_path, "fx-true-square")

    rc = main(["--config", str(cfg), "run", "--fixture", "fx-true-square",
               "--policy", str(policy), "--intent-review", str(review)])

    assert rc == 3
    out = json.loads(capsys.readouterr().out)
    assert out["candidate_assembly_complete"]
    assert not out["proof_complete"]
    assert out["release"] is None
    assert out["outcome"] == "release_blocked_by_policy"
    assert not out["expectation_met"]


def test_cli_verified_expectation_rejects_certificate_misbound_to_contract(
    tmp_path, capsys, monkeypatch,
):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path, promotion=True)
    review = _signed_intent_review_file(tmp_path, "fx-true-square")
    original_research = cli_module.research

    def return_misbound_result(**kwargs):
        result = original_research(**kwargs)
        result.problem_id = "foreign-problem"
        result.contract.problem_id = "foreign-problem"
        result.contract.source_id = "foreign-source"
        assert result.contract.contract_hash() != result.certificate.problem_contract_hash
        return result

    monkeypatch.setattr(cli_module, "research", return_misbound_result)

    rc = main(["--config", str(cfg), "run", "--fixture", "fx-true-square",
               "--policy", str(policy), "--intent-review", str(review)])

    assert rc == 3
    out = json.loads(capsys.readouterr().out)
    assert not out["expectation_met"]


@pytest.mark.parametrize(
    ("failure", "expected_rc"),
    (("missing", 3), ("forged", 2), ("stale", 2)),
)
def test_cli_verified_expectation_fails_closed_for_invalid_certificate(
    tmp_path, capsys, monkeypatch, failure, expected_rc,
):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path, promotion=True)
    review = _signed_intent_review_file(tmp_path, "fx-true-square")
    original_research = cli_module.research

    def return_invalid_release(**kwargs):
        result = original_research(**kwargs)
        if failure == "missing":
            result.certificate = None
        elif failure == "forged":
            result.certificate.signature = "0" * 64
        else:
            # Keep the authentic certificate bytes unchanged and advance the
            # verifier clock past both the gate and release freshness windows.
            monkeypatch.setattr("egmra.release.certificate.time.time", lambda: 4_000_000_000)
        return result

    monkeypatch.setattr(cli_module, "research", return_invalid_release)

    rc = main(["--config", str(cfg), "run", "--fixture", "fx-true-square",
               "--policy", str(policy), "--intent-review", str(review)])

    captured = capsys.readouterr()
    assert rc == expected_rc
    if failure == "missing":
        out = json.loads(captured.out)
        assert out["release"] is None
        assert not out["expectation_met"]
    else:
        assert captured.out == ""
        assert json.loads(captured.err)["error"] == "ReleaseSecurityError"


def test_cli_run_false_fixture_is_triage(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--fixture", "fx-false-prime",
               "--policy", str(policy)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["outcome"] == "honest_triage_report"


def test_cli_policy_show(tmp_path, capsys):
    policy = _signed_policy_file(tmp_path)
    rc = main(["policy-show", "--policy", str(policy)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert "policy_hash" in out and out["flags"]["promotion"] is False


def test_cli_fixtures_lists(capsys):
    rc = main(["fixtures"])
    assert rc == 0
    assert "fx-true-square" in capsys.readouterr().out


def test_cli_verify_events_requires_exact_run_binding_and_fails_closed(
    tmp_path, capsys,
):
    events = tmp_path / "events.jsonl"
    log = EventLog(events, run_id="bound-run")
    log.append(
        action="HUMAN_INTERVENTION",
        actor={"type": "human", "id": "auditor"},
        object_ids=["bound-run"],
    )

    rc = main(["verify-events", "--events", str(events), "--run-id", "bound-run"])
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    assert result["integrity"] is True
    assert result["run_id"] == "bound-run"

    rc = main(["verify-events", "--events", str(events), "--run-id", "other-run"])
    assert rc == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error"] == "EventLogError"

    first = json.loads(events.read_text().splitlines()[0])
    first["object_ids"] = ["tampered"]
    events.write_text(json.dumps(first) + "\n")
    rc = main(["verify-events", "--events", str(events), "--run-id", "bound-run"])
    assert rc == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error"] == "EventLogError"


def test_cli_default_unsigned_policy_fails_explicitly(capsys):
    rc = main(["policy-show"])

    assert rc == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error"] == "PolicyError"
    assert "unsigned" in error["detail"]


def test_cli_policy_sign_creates_authenticated_file_without_exposing_key(tmp_path, capsys):
    template = tmp_path / "template.json"
    template.write_text(json.dumps({"flags": {
        "claim_graph": True, "literature_retrieval": True,
        "computation_service": True, "promotion": False,
    }}))
    output = tmp_path / "signed.json"

    rc = main(["policy-sign", "--input", str(template), "--output", str(output)])

    assert rc == 0
    rendered = capsys.readouterr().out
    assert os.environ["EGMRA_POLICY_KEY"] not in rendered
    assert load_policy(output).signature_trust == "signed"
    assert output.stat().st_mode & 0o777 == 0o600


def test_cli_policy_sign_refuses_overwrite_and_symlink(tmp_path, capsys):
    template = tmp_path / "template.json"
    template.write_text(json.dumps({"flags": {"claim_graph": True}}))
    existing = tmp_path / "existing.json"
    existing.write_text("do not overwrite")

    assert main(["policy-sign", "--input", str(template), "--output", str(existing)]) == 2
    assert existing.read_text() == "do not overwrite"
    capsys.readouterr()

    target = tmp_path / "target.json"
    target.write_text("target")
    link = tmp_path / "link.json"
    link.symlink_to(target)
    assert main(["policy-sign", "--input", str(template), "--output", str(link)]) == 2
    assert target.read_text() == "target"


def test_cli_finite_prime_fixture_does_not_replace_predicate_with_true():
    fx = FixtureProblem(
        "finite-prime", b"Check primality on a finite range.", "honest_triage",
        "_isprime(n)", scope="finite_domain",
    )

    output = _fixture_worker(fx).work_branch(
        None, None, branch_id="finite", budget=1.0, fencing_token=1,
    )

    assert output.evidence == []
    assert "experiment predicate returned false" in output.failures


def test_cli_expectation_mismatch_has_distinct_exit_code(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)

    rc = main(["--config", str(cfg), "run", "--fixture", "fx-true-even-sum",
               "--policy", str(policy)])

    assert rc == 3
    out = json.loads(capsys.readouterr().out)
    assert out["expected_outcome"] == "verified"
    assert not out["expectation_met"]
    assert out["proof_complete"] is False


def test_cli_reports_missing_truth_snapshot_key_as_configuration_error(
    tmp_path, capsys, monkeypatch,
):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)
    review = _signed_intent_review_file(tmp_path, "fx-true-square")
    monkeypatch.delenv("EGMRA_TRUTH_SNAPSHOT_KEY")

    rc = main(["--config", str(cfg), "run", "--fixture", "fx-true-square",
               "--policy", str(policy), "--intent-review", str(review)])

    assert rc == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error"] == "TruthSnapshotError"


def test_cli_does_not_count_unattested_gate_profile_as_verified(
    tmp_path, capsys, monkeypatch,
):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)
    review = _signed_intent_review_file(tmp_path, "fx-true-square")
    monkeypatch.delenv("EGMRA_GATE_KEY")

    rc = main(["--config", str(cfg), "run", "--fixture", "fx-true-square",
               "--policy", str(policy), "--intent-review", str(review)])

    assert rc == 3
    out = json.loads(capsys.readouterr().out)
    assert not out["expectation_met"]


def test_cli_verified_fixture_requires_independent_intent_review(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)

    rc = main(["--config", str(cfg), "run", "--fixture", "fx-true-square",
               "--policy", str(policy)])

    assert rc == 3
    out = json.loads(capsys.readouterr().out)
    assert out["gate_profile"] is None
    assert out["proof_complete"] is False


# --- Single-pipeline: campaign --triage drainer + legacy retirement -------------


def _write_triage(tmp_path):
    rankings = tmp_path / "triage" / "rankings"
    rankings.mkdir(parents=True)
    rows = [
        {
            "problem_id": f"erdos-{number}",
            "problem_number": number,
            "allocation_rank": rank,
            "allocation_lane": "exploitation",
            "prize": "no",
            "prize_status": "unpaid",
            "selection_priority_tier": 0,
            "literature_coverage_status": "local_only",
            "base_acquisition_score": 0.1,
            "literature_adjustment": 0.0,
            "selection_score": 0.1,
            "reason_selected": "test",
        }
        for rank, number in enumerate((312, 1104), start=1)
    ]
    projection = build_queue_projection({
        "allocation_status": "ready",
        "allocation_context_id": "a" * 64,
        "ranking_content_sha256": "b" * 64,
        "source_snapshot_id": "source-1",
        "source_snapshot_sha256": "c" * 64,
        "prize_policy_version": "prize-tier-v1",
        "literature_policy_version": "literature-ranking-v1",
        "literature_model_version": "literature-opportunity-v1",
        "literature_coverage": {},
        "corpus_integrity": {"status": "complete"},
        "attempt_exclusions": [],
        "allocation_queue": rows,
    })
    (rankings / "current_queue.json").write_text(json.dumps(projection))
    return tmp_path / "triage"


def test_campaign_triage_startup_adopts_ranked_order(
    tmp_path, capsys, monkeypatch,
):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)
    triage = _write_triage(tmp_path)
    adopted: list[list[str]] = []
    real_adopt = cli_module.Campaign.adopt_ranked_order

    def recording_adopt(self, campaign_id, problem_ids):
        adopted.append(list(problem_ids))
        return real_adopt(self, campaign_id, problem_ids)

    monkeypatch.setattr(
        cli_module.Campaign, "adopt_ranked_order", recording_adopt,
        raising=False,
    )
    rc = main([
        "--config", str(cfg), "campaign",
        "--triage", str(triage), "--triage-lane", "current",
        "--provider", "deterministic", "--policy", str(policy),
        "--retrieval", "none", "--oeis", "offline",
        "--state", str(tmp_path / "camp.json"),
    ])

    assert rc == 0
    assert adopted == [["erdos-312", "erdos-1104"]]


def test_campaign_triage_drains_ranked_problems_and_records_outcomes(
    tmp_path, capsys, monkeypatch,
):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)
    triage = _write_triage(tmp_path)
    ledger = tmp_path / "outcomes.jsonl"

    drained: list[str] = []
    real_from_erdos = cli_module.from_erdos_number

    def fake_from_erdos(number, **kwargs):
        drained.append(f"erdos-{number}")
        return real_from_erdos(number, **kwargs)

    monkeypatch.setattr(cli_module, "from_erdos_number", fake_from_erdos)

    rc = main(["--config", str(cfg), "campaign",
               "--triage", str(triage), "--triage-lane", "current",
               "--provider", "deterministic", "--policy", str(policy),
               "--retrieval", "none", "--oeis", "offline",
               "--state", str(tmp_path / "camp.json"),
               "--outcome-ledger", str(ledger)])

    assert rc == 0
    status = json.loads(capsys.readouterr().out)
    assert status["total"] == 2
    # Drained in the ranking's own order.
    assert drained == ["erdos-312", "erdos-1104"]
    # Honest outcomes recorded, one JSON record per line.
    from egmra.orchestrator.outcome_ledger import EgmraOutcomeLedger
    recorded = EgmraOutcomeLedger(ledger).latest_by_problem()
    assert set(recorded) == {"erdos-312", "erdos-1104"}
    assert all(not r["released"] for r in recorded.values())


def test_campaign_rejects_both_triage_and_range(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)
    triage = _write_triage(tmp_path)

    rc = main(["--config", str(cfg), "campaign",
               "--triage", str(triage), "--erdos-range", "900-905",
               "--provider", "deterministic", "--policy", str(policy),
               "--state", str(tmp_path / "camp.json")])

    assert rc == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error"] == "ValueError"


# --- Retrieval / OEIS wiring (task 4.4) -----------------------------------------


def test_cli_run_arbitrary_wires_retrieval_corpus_and_oeis(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs"),
                               "oeis_cache_dir": str(tmp_path / "oeis")}))
    policy = _signed_policy_file(tmp_path)

    rc = main(["--config", str(cfg), "run", "--provider", "deterministic",
               "--policy", str(policy), "--statement",
               "For every n there exist infinitely many twin primes.",
               "--retrieval", "corpus", "--oeis", "offline"])

    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["event_store"] == "jsonl"
    assert out["retrieval"]["mode"] == "corpus"
    assert out["retrieval"]["corpus_records"] > 100
    assert out["retrieval"]["oeis_mode"] == "offline"


def test_cli_run_arbitrary_retrieval_none_is_empty_corpus(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs"),
                               "oeis_cache_dir": str(tmp_path / "oeis")}))
    policy = _signed_policy_file(tmp_path)

    rc = main(["--config", str(cfg), "run", "--provider", "deterministic",
               "--policy", str(policy), "--statement", "A test statement.",
               "--retrieval", "none", "--oeis", "offline"])

    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["retrieval"]["mode"] == "none"
    assert out["retrieval"]["corpus_records"] == 0


def test_build_retrieval_corpus_helper_builds_or_disables():
    config = EgmraConfig()
    corpus = cli_module._build_retrieval_corpus(
        argparse.Namespace(retrieval="corpus", corpus_tex=None, catalog=None), config)
    assert corpus is not None and len(corpus) > 100
    assert all(r.is_auditable() for r in corpus[:5])
    disabled = cli_module._build_retrieval_corpus(
        argparse.Namespace(retrieval="none", corpus_tex=None, catalog=None), config)
    assert disabled is None


def test_build_oeis_client_helper_modes():
    live = cli_module._build_oeis_client(argparse.Namespace(oeis="live"), EgmraConfig())
    assert live.offline is False
    offline = cli_module._build_oeis_client(argparse.Namespace(oeis="offline"), EgmraConfig())
    assert offline.offline is True
    auto = cli_module._build_oeis_client(
        argparse.Namespace(oeis="auto"), EgmraConfig(oeis_offline=True))
    assert auto.offline is True


# --- Postgres event store wiring (task 4.9) -------------------------------------


def test_cli_run_postgres_event_store_requires_dsn(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("EGMRA_POSTGRES_DSN", raising=False)
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)

    rc = main(["--config", str(cfg), "run", "--provider", "deterministic",
               "--policy", str(policy), "--statement", "A statement.",
               "--event-store", "postgres"])

    assert rc == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error"] == "ValueError"
    assert "DSN" in error["detail"]


def test_cli_init_db_and_migrate_db_require_dsn(capsys, monkeypatch):
    monkeypatch.delenv("EGMRA_POSTGRES_DSN", raising=False)
    for command in ("init-db", "migrate-db"):
        assert main([command]) == 2
        error = json.loads(capsys.readouterr().err)
        assert error["error"] == "ValueError"
        assert "DSN" in error["detail"]


def test_cli_verify_events_postgres_requires_dsn(capsys, monkeypatch):
    monkeypatch.delenv("EGMRA_POSTGRES_DSN", raising=False)
    assert main(["verify-events", "--event-store", "postgres", "--run-id", "r1"]) == 2
    error = json.loads(capsys.readouterr().err)
    assert "DSN" in error["detail"]


def test_cli_verify_events_jsonl_requires_events_path(capsys):
    assert main(["verify-events", "--run-id", "r1"]) == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error"] == "ValueError"
    assert "--events" in error["detail"]


def test_resolve_postgres_dsn_reads_env_and_cli(monkeypatch):
    monkeypatch.setenv("EGMRA_POSTGRES_DSN", "postgresql://h:1/db")
    assert cli_module._resolve_postgres_dsn(
        argparse.Namespace(dsn=None)) == "postgresql://h:1/db"
    assert cli_module._resolve_postgres_dsn(
        argparse.Namespace(dsn="postgresql://other:2/db2")) == "postgresql://other:2/db2"


def test_make_event_log_defaults_to_jsonl_backend():
    # jsonl is the default: research builds its own file log, so the helper
    # returns None rather than a Postgres connection.
    assert cli_module._make_event_log(argparse.Namespace(event_store="jsonl"), "r1") is None


# --- Campaign signed-review parity (release capability, not just egmra run) -----


def _signed_intent_for_erdos(number: int) -> dict:
    problem = cli_module.from_erdos_number(number)
    contract = build_problem_contract(
        problem_id=problem.problem_id, source_bytes=problem.source_bytes,
        source_id=problem.source_id)
    interp = contract.lattice.nodes[0]
    certificate = sign_intent_certificate(IntentCertificate(
        certificate_id=f"intent-{problem.problem_id}",
        source_bytes_hash=contract.source_bytes_hash,
        interpretation_hash=interpretation_review_hash(interp),
        informal_claim_hash=sha256_hex(interp.conclusion),
        methods=["independent_parse", "examples", "anti_examples",
                 "paraphrase", "local_mutation"],
        reviewer_ids=["semantic-reviewer"],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "semantic-reviewer",
            "independent_from": ["governor", "intake_retrieval"],
            "conflicts": [],
        }],
        verdict=Verdict.APPROVED,
    ))
    return certificate.to_dict()


def test_load_campaign_reviews_directory_convention(tmp_path):
    assert cli_module._load_campaign_reviews(None) == {}
    with pytest.raises(ValueError):
        cli_module._load_campaign_reviews(tmp_path / "missing")

    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "intent-erdos-312.json").write_text(
        json.dumps(_signed_intent_for_erdos(312)))
    (reviews / "unrelated-notes.json").write_text("{}")

    loaded = cli_module._load_campaign_reviews(reviews)
    assert set(loaded) == {"erdos-312"}
    assert loaded["erdos-312"]["intent"].certificate_id == "intent-erdos-312"
    assert "expert" not in loaded["erdos-312"]

    # malformed artifacts fail the LAUNCH, never a worker mid-run
    (reviews / "intent-erdos-1104.json").write_text("not json")
    with pytest.raises(Exception):
        cli_module._load_campaign_reviews(reviews)


def test_campaign_reviews_dir_binds_intent_per_problem(tmp_path, capsys):
    """A campaign problem with a signed intent binds it; others stay unchanged."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)
    triage = _write_triage(tmp_path)
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "intent-erdos-312.json").write_text(
        json.dumps(_signed_intent_for_erdos(312)))

    rc = main(["--config", str(cfg), "campaign",
               "--triage", str(triage), "--triage-lane", "current",
               "--provider", "deterministic", "--policy", str(policy),
               "--retrieval", "none", "--oeis", "offline",
               "--reviews-dir", str(reviews),
               "--state", str(tmp_path / "camp.json"),
               "--outcome-ledger", str(tmp_path / "outcomes.jsonl")])
    assert rc == 0

    def actions_for(problem: str) -> set[str]:
        out = set()
        for events_file in (tmp_path / "runs").glob(f"*{problem}*.jsonl"):
            for line in events_file.read_text().splitlines():
                out.add(json.loads(line).get("action"))
        return out

    # the signed intent bound on erdos-312 (and resolved its disputed parse)...
    assert "INTENT_CERTIFICATE_ISSUED" in actions_for("erdos-312")
    # ...while erdos-1104, with no artifact, ran exactly as before.
    assert "INTENT_CERTIFICATE_ISSUED" not in actions_for("erdos-1104")


def test_checkpoint_dir_enables_exchange_cache(tmp_path, capsys):
    """--checkpoint-dir now also persists per-exchange replay entries."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)

    rc = main(["--config", str(cfg), "run", "--provider", "deterministic",
               "--policy", str(policy), "--statement",
               "Prove that for all natural numbers n, n squared is at least 0.",
               "--retrieval", "none", "--oeis", "offline",
               "--checkpoint-dir", str(tmp_path / "ckpts")])
    assert rc == 0
    exchange_dirs = list((tmp_path / "ckpts").glob("*/exchanges/*.json"))
    assert exchange_dirs                      # exchanges persisted durably


def test_campaign_auto_rerank_adjusts_pending_order_from_outcomes(tmp_path, capsys):
    """--auto-rerank: observed outcomes rewrite the pending order mid-campaign."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    policy = _signed_policy_file(tmp_path)
    triage = _write_triage(tmp_path)          # searcher order: 312, 1104
    ledger = tmp_path / "outcomes.jsonl"
    # Prior campaigns observed 312 repeatedly interpretation-blocked.
    ledger.write_text("\n".join(json.dumps({
        "problem_id": "erdos-312", "public_state": "BLOCKED_BY_INTERPRETATION",
        "released": False}) for _ in range(2)) + "\n")

    rc = main(["--config", str(cfg), "campaign",
               "--triage", str(triage), "--triage-lane", "current",
               "--provider", "deterministic", "--policy", str(policy),
               "--retrieval", "none", "--oeis", "offline", "--auto-rerank",
               "--state", str(tmp_path / "camp.json"),
               "--outcome-ledger", str(ledger)])
    assert rc == 0
    state = json.loads((tmp_path / "camp.json").read_text())
    # after the first completion the dead-end history demoted 312 behind 1104
    assert state["order"] == ["erdos-1104", "erdos-312"]
    # and both problems still completed (rerank never drops work)
    assert {a["status"] for a in state["assignments"].values()} == {"done"}
