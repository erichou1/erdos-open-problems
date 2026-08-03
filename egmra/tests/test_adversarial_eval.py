"""Independent adversarial tests for evaluation identity and fixture safety."""

import builtins
from dataclasses import FrozenInstanceError

import pytest

from egmra.eval.ablations import AblationError, AblationRegistry, PreRegistration
from egmra.eval.datasets import FixtureProblem
from egmra.eval.protocol import FrozenEvalConfig, TimeCapsule
from egmra.eval.stats import ReportedResult, StatisticalPolicyError


def _config(**changes):
    values = {
        "problem_bytes_hash": "problem-hash",
        "status": "open",
        "toolchain": "python-3.12",
        "library_commit": "mathlib@abc",
        "models": ("model-a",),
        "prompts_hash": "prompt-hash",
        "tools": ("lean",),
        "budget": {"tokens": 1000, "seconds": 60},
        "network_policy": "off",
        "rubric_hash": "rubric-hash",
    }
    values.update(changes)
    return FrozenEvalConfig(**values)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "solved"),
        ("tools", ("lean", "oeis")),
        ("budget", {"tokens": 1001, "seconds": 60}),
        ("network_policy", "retrieval-only"),
    ],
)
def test_eval_identity_commits_every_behavior_and_cost_field(field, value):
    baseline = _config()
    assert baseline.config_hash() != _config(**{field: value}).config_hash()


def test_frozen_eval_budget_cannot_mutate_after_hashing():
    config = _config()
    before = config.config_hash()
    with pytest.raises((TypeError, FrozenInstanceError)):
        config.budget["tokens"] = 1
    assert config.config_hash() == before


@pytest.mark.parametrize(
    "kwargs",
    [
        {"numerator": -1, "denominator": 10, "interval_low": 0, "interval_high": 1,
         "censored": 0, "paired": True},
        {"numerator": 11, "denominator": 10, "interval_low": 0, "interval_high": 1,
         "censored": 0, "paired": True},
        {"numerator": 1, "denominator": 10, "interval_low": -0.1, "interval_high": 1,
         "censored": 0, "paired": True},
        {"numerator": 1, "denominator": 10, "interval_low": 0, "interval_high": 1.1,
         "censored": 0, "paired": True},
        {"numerator": 1, "denominator": 10, "interval_low": 0, "interval_high": 1,
         "censored": -1, "paired": True},
        {"numerator": 9, "denominator": 10, "interval_low": 0.1, "interval_high": 0.2,
         "censored": 0, "paired": True},
    ],
)
def test_reported_results_reject_impossible_statistics(kwargs):
    with pytest.raises(StatisticalPolicyError):
        ReportedResult(**kwargs)


def test_time_capsule_dates_are_validated_not_compared_lexicographically():
    capsule = TimeCapsule("p", "2025-01-02", (), "solution-hash")
    assert capsule.leaks("2025-01-10")
    assert not capsule.leaks("2024-12-31")
    with pytest.raises(ValueError):
        capsule.leaks("not-a-date")
    with pytest.raises(ValueError):
        TimeCapsule("p", "2025-13-99", (), "solution-hash")


@pytest.mark.parametrize(
    "payload",
    [
        "__import__('os').system('id') == 0",
        "(1).__class__.__mro__",
        "open('/etc/passwd').read()",
        "[n for n in range(10)]",
    ],
)
def test_fixture_predicates_reject_code_execution(payload):
    with pytest.raises(ValueError, match="unsafe fixture predicate"):
        FixtureProblem("evil", b"x", "triage", payload).predicate()


def test_fixture_predicates_still_support_the_audited_expression_subset():
    predicate = FixtureProblem(
        "safe", b"x", "verified", "n >= 0 and (2 * n) % 2 == 0"
    ).predicate()
    assert predicate(4) is True


def test_fixture_predicates_do_not_execute_through_python_eval(monkeypatch):
    def forbidden_eval(*_args, **_kwargs):
        raise AssertionError("Python eval must not be part of the fixture boundary")

    monkeypatch.setattr(builtins, "eval", forbidden_eval)
    predicate = FixtureProblem("safe", b"x", "verified", "n * n >= 0").predicate()
    assert predicate(7) is True


def test_fixture_predicate_rejects_bare_helper_as_constant_success():
    with pytest.raises(ValueError, match="must be called"):
        FixtureProblem("constant-success", b"x", "verified", "_isprime").predicate()


def test_ablation_preregistration_rejects_blank_or_duplicate_entries():
    with pytest.raises(AblationError):
        PreRegistration(
            "no_oeis_vs_structured_oeis_service", "", "n >= 30"
        )
    registry = AblationRegistry()
    prereg = PreRegistration(
        "no_oeis_vs_structured_oeis_service", "verified_progress", "n >= 30"
    )
    registry.register(prereg)
    with pytest.raises(AblationError, match="already registered"):
        registry.register(prereg)
