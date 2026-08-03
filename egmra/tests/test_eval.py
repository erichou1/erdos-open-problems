"""Tests for the evaluation plane and the dataset fixtures running end-to-end."""

import pytest

from egmra.compute.spec import ExperimentSpec
from egmra.corpus.status import StatusClaim
from egmra.eval import (
    FIXTURE_PROBLEMS,
    PINNED_BENCHMARKS,
    AblationRegistry,
    EvalRun,
    FrozenEvalConfig,
    PreRegistration,
    ProgressLedger,
    ReportedResult,
    REQUIRED_ABLATIONS,
    REQUIRED_BASELINES,
    baseline_comparison_valid,
    compare_pass_at_k,
    fixture,
    is_progress,
    level,
    manuscript_beats_counterexample,
    requires_tracks,
    rfc,
    scores_accuracy,
)
from egmra.eval.metrics import CoverageClaim, freeze_blueprint
from egmra.eval.stats import StatisticalPolicyError
from egmra.orchestrator import DeterministicWorker, research
from egmra.policy import PolicyEnforcer, sign_policy
from egmra.retrieval.records import TheoremRecord


# ── levels ────────────────────────────────────────────────────────────────────

def test_seven_levels_and_tracks():
    assert level(1).primary_capability.startswith("parsing")
    assert level(7).ground_truth.startswith("no answer key")
    assert requires_tracks(2) and requires_tracks(3)
    assert not scores_accuracy(7)   # Level 7 never scores accuracy
    with pytest.raises(KeyError):
        level(8)


# ── protocol / baselines ─────────────────────────────────────────────────────

def test_eval_run_requires_four_baselines():
    cfg = FrozenEvalConfig("h", "open", "lean4.9", "mathlib@abc", ("m1",), "ph", ("lean",),
                           {"tokens": 1000}, "off", "rubric")
    run = EvalRun(level=2, config=cfg)
    assert not run.ready()
    for b in REQUIRED_BASELINES:
        run.baselines_present.add(b)
    assert run.ready() and not run.missing_baselines()


def test_baseline_comparison_requires_paired_equal_cost():
    assert baseline_comparison_valid(paired=True, equal_cost_or_pareto=True)
    assert not baseline_comparison_valid(paired=False, equal_cost_or_pareto=True)


# ── metrics / RFC ─────────────────────────────────────────────────────────────

def test_rfc_metric():
    claims = [CoverageClaim("c1", 0.9, 0.9, 0.9, True),
              CoverageClaim("c2", 0.5, 0.5, 0.5, False)]
    frozen = freeze_blueprint(claims)
    assert 0.0 < rfc(claims, frozen) < 1.0


# ── progress vs verbose ──────────────────────────────────────────────────────

def test_progress_requires_durable_object():
    ledger = ProgressLedger()
    assert not is_progress(ledger.progress_score())
    ledger.add("exact_counterexample")
    assert is_progress(ledger.progress_score())
    with pytest.raises(ValueError):
        ledger.add("polished_exposition")   # not a durable object


def test_manuscript_never_beats_counterexample():
    assert not manuscript_beats_counterexample(manuscript_unverified_nodes=10000,
                                               exact_counterexamples=1)


# ── ablations ────────────────────────────────────────────────────────────────

def test_ablation_registry_completeness():
    reg = AblationRegistry()
    assert len(reg.missing()) == len(REQUIRED_ABLATIONS)
    for ablation in REQUIRED_ABLATIONS:
        reg.register(PreRegistration(ablation, "verified_progress_per_cost", "n>=30 or CI excludes 0"))
    assert reg.complete()


# ── stats ─────────────────────────────────────────────────────────────────────

def test_stats_forbids_pass_at_k_mismatch():
    compare_pass_at_k(1, 1)
    with pytest.raises(StatisticalPolicyError):
        compare_pass_at_k(1, 32)


def test_reported_result_requires_denominator():
    with pytest.raises(StatisticalPolicyError):
        ReportedResult(0, 0, 0.0, 1.0, 0, True)
    r = ReportedResult(3, 10, 0.1, 0.6, 2, True)
    assert r.rate() == 0.3


# ── datasets ────────────────────────────────────────────────────────────────────

def test_fixture_predicates_execute():
    true_sq = fixture("fx-true-square")
    assert true_sq.predicate()(5) is True
    false_prime = fixture("fx-false-prime")
    assert false_prime.predicate()(4) is False   # 4 is not prime
    assert len(FIXTURE_PROBLEMS) >= 5
    assert "PutnamBench" in PINNED_BENCHMARKS


def test_fixtures_run_through_the_research_loop(tmp_path):
    """The executable fixtures actually flow through research() and match expectations."""
    policy_env = {"EGMRA_POLICY_KEY": "eval-test-policy-key-that-is-at-least-32-bytes"}
    enforcer = PolicyEnforcer(sign_policy({
        "claim_graph": True, "literature_retrieval": True, "computation_service": True,
        "promotion": False, "formal_promotion": False,
    }, env=policy_env), verification_env=policy_env)
    corpus = [TheoremRecord(theorem_id="t", canonical_statement="x", conclusion="y",
                            source_uri="u", source_version="v", source_content_hash="h",
                            verbatim_theorem_and_hypothesis_extract="x")]
    # a true finite fixture -> verified; a false fixture -> honest triage
    checks = {"fx-true-square": "verified", "fx-false-prime": "honest_triage"}
    for pid, expected in checks.items():
        fx = fixture(pid)
        body = fx.predicate_src
        helper = ""
        if "_isprime" in body:
            body = body.replace("_isprime", "isprime")
            helper = (
                "def isprime(n):\n"
                "    if n < 2:\n"
                "        return False\n"
                "    i = 2\n"
                "    while i * i <= n:\n"
                "        if n % i == 0:\n"
                "            return False\n"
                "        i += 1\n"
                "    return True\n\n"
            )
        code = (helper + "def experiment(inputs):\n"
                "    n = inputs['n']\n"
                "    ok = all((lambda k: %s)(k) for k in range(n+1))\n"
                "    return {'result': ok, 'coverage': 'exhaustive 0..n'}\n" % body)
        spec = ExperimentSpec(purpose=pid, inputs={"n": 30}, arithmetic_mode="exact",
                              coverage="0..n", claim_ids=("goal",)) \
            if fx.scope == "finite_domain" else None
        worker = DeterministicWorker(
            goal_claim_id="goal", goal_formula=fx.statement.decode(), goal_scope=fx.scope,
            experiment_code=code if spec else "", experiment_spec=spec)
        result = research(
            problem_id=pid, source_bytes=fx.statement, source_id=pid, budget=100.0,
            enforcer=enforcer, worker=worker, goal_claim_id="goal",
            events_path=tmp_path / f"{pid}.jsonl", retrieval_corpus=corpus,
            probe_predicate=fx.predicate(), novelty_verdict="known",
            status_claims=[StatusClaim(
                problem_id=pid, status="known", source="local://fixture-manifest",
                review_date="2026-07-13", source_independence="test-fixture",
            )])
        if expected == "honest_triage":
            assert result.outcome == "honest_triage_report"
        else:
            assert result.outcome != "honest_triage_report"
