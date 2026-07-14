"""Tests for the agents plane: authorities, profiles/diversity, prompts, runners."""

import pytest

from egmra.agents import (
    AUTHORITIES,
    DeterministicRunner,
    DiversityAudit,
    MethodProfile,
    authority,
    differing_axes,
    is_forbidden,
    is_genuinely_diverse,
    role_prompt,
    role_prompt_hash,
)
from egmra.agents.runner import AttestedRunner


def test_seven_authorities_defined():
    assert len(AUTHORITIES) == 7
    assert set(AUTHORITIES) == {
        "research_governor", "intake_retrieval", "program_worker",
        "computational_falsifier", "formalization_authority",
        "adversarial_referee", "release_auditor",
    }


def test_governor_cannot_change_truth():
    assert is_forbidden("research_governor", "change_claim_evidence")
    assert is_forbidden("research_governor", "publish_theorem")
    assert not is_forbidden("research_governor", "open_branch")


def test_referee_not_rewarded_for_agreement_and_reports_to_auditor():
    ref = authority("adversarial_referee")
    assert "earn_reward_for_agreement" in ref.forbidden
    assert "report_to_research_governor" in ref.forbidden


def test_release_auditor_cannot_substitute_verdicts():
    assert is_forbidden("release_auditor", "substitute_one_positive_verdict_for_another")


def test_unknown_authority_raises():
    with pytest.raises(KeyError):
        authority("czar")


# ── diversity ────────────────────────────────────────────────────────────────

def test_same_context_creative_prompts_are_correlated():
    a = MethodProfile("a", method_prior="direct", model_lineage="fam1")
    b = MethodProfile("b", method_prior="direct", model_lineage="fam1")
    # identical except id -> zero differing axes -> not diverse
    assert not is_genuinely_diverse(a, b)


def test_two_axis_difference_is_diverse():
    a = MethodProfile("a", method_prior="direct", tool_access=("lean",), model_lineage="fam1")
    b = MethodProfile("b", method_prior="probabilistic", tool_access=("sat",), model_lineage="fam1")
    assert len(differing_axes(a, b)) >= 2
    assert is_genuinely_diverse(a, b)


def test_diversity_audit_collapses_correlated():
    profiles = [
        MethodProfile("p1", method_prior="direct", model_lineage="fam1"),
        MethodProfile("p2", method_prior="direct", model_lineage="fam1"),  # dup of p1
        MethodProfile("p3", method_prior="probabilistic", tool_access=("sat",),
                      model_lineage="fam2"),
    ]
    audit = DiversityAudit(profiles)
    assert ("p1", "p2") in audit.correlated_pairs()
    assert audit.independent_count() == 2


# ── prompts ──────────────────────────────────────────────────────────────────

def test_role_prompt_and_hash_stable():
    assert "maximize expected verified mathematical progress" in role_prompt("research_governor")
    assert role_prompt_hash("adversarial_referee") == role_prompt_hash("adversarial_referee")
    with pytest.raises(KeyError):
        role_prompt("nope")


# ── runner ────────────────────────────────────────────────────────────────────

def test_deterministic_runner_is_unattested():
    runner = DeterministicRunner(responses={"scout": "hello"})
    resp = runner.run("some prompt", stage="scout")
    assert resp.text == "hello"
    assert resp.model.attested is False           # never counts as independent evidence
    assert resp.prompt_hash and resp.context_id


def test_attested_runner_requires_configured_call():
    runner = AttestedRunner(runner_id="openai-r", provider="openai")
    with pytest.raises(RuntimeError):
        runner.run("p", stage="scout")

    def fake_call(prompt, stage):
        return ("proof text", "o-research", "2026-01", "build-xyz")

    runner2 = AttestedRunner(runner_id="openai-r", provider="openai", call=fake_call)
    resp = runner2.run("p", stage="scout")
    assert resp.model.attested and resp.model.version == "2026-01"
