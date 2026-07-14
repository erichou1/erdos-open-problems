"""Tests for the CLI and configuration."""

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
    assert out["proof_complete"]
    assert out["release"] is not None
    assert out["outcome"] == "verified_finite_or_conditional_result"


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
