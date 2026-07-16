"""Gap closures, wave 2: attested API runners, expert review, blocked
exploration, checkpoint resume, formalizer portfolio, calibration, salvage,
and cross-problem priors.

Every fix is fail-closed: a missing key, a tampered certificate, a rejected
checkpoint, or a dead portfolio member degrades to exactly the prior
behavior — never to fabricated support.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from egmra.agents.api_runner import (
    ApiProviderError,
    PROVIDERS,
    build_api_runner,
)
from egmra.lean.formalizer import (
    ApiFormalizer,
    PortfolioFormalizer,
    extract_lean_source,
)
from egmra.orchestrator import research
from egmra.orchestrator.calibration import build_calibration_report
from egmra.orchestrator.outcome_ledger import build_outcome_record
from egmra.corpus.status import StatusClaim
from egmra.release.expert_review import (
    ExpertReviewCertificate,
    ExpertReviewError,
    expert_reviewed_for_run,
    sign_expert_review,
    verify_expert_review,
)
from egmra.tests.test_gap_closures import (
    TRUE_STATEMENT,
    _corpus,
    _enforcer,
    _fixture_worker,
    _intent,
    _status,
)

# ---------------------------------------------------------------------------
# attested API runners


def _openai_document(text="hello", model="gpt-4o-2024-11-20", rid="req-1"):
    return {"id": rid, "model": model,
            "choices": [{"message": {"role": "assistant", "content": text}}]}


def _anthropic_document(text="hello", model="claude-sonnet-4-5", rid="msg-1"):
    return {"id": rid, "model": model,
            "content": [{"type": "text", "text": text}]}


ENV = {
    "OPENAI_API_KEY": "test-openai-key",
    "DEEPSEEK_API_KEY": "test-deepseek-key",
    "ANTHROPIC_API_KEY": "test-anthropic-key",
}


def test_openai_style_runner_is_attested_with_response_identity():
    seen: dict = {}

    def transport(url, headers, payload):
        seen.update(url=url, headers=headers, payload=payload)
        return _openai_document()

    runner = build_api_runner("openai-api", transport=transport, env=ENV)
    response = runner.run("prove it", stage="hostile_review:r1")
    assert response.text == "hello"
    assert response.model.attested                    # the whole point
    assert response.model.provider == "openai"
    assert response.model.model == "gpt-4o-2024-11-20"  # response body, not alias
    assert seen["url"] == "https://api.openai.com/v1/chat/completions"
    assert seen["headers"]["Authorization"] == "Bearer test-openai-key"


def test_anthropic_runner_is_attested():
    runner = build_api_runner(
        "anthropic-api", transport=lambda *a: _anthropic_document(), env=ENV)
    response = runner.run("p", stage="s")
    assert response.model.attested and response.model.provider == "anthropic"


def test_two_providers_carry_distinct_lineages():
    openai = build_api_runner(
        "openai-api", transport=lambda *a: _openai_document(), env=ENV)
    anthropic = build_api_runner(
        "anthropic-api", transport=lambda *a: _anthropic_document(), env=ENV)
    a = openai.run("p", stage="s").model
    b = anthropic.run("p", stage="s").model
    assert a.attested and b.attested
    assert (a.provider, a.model) != (b.provider, b.model)


def test_missing_key_fails_closed():
    with pytest.raises(ApiProviderError):
        build_api_runner("openai-api", env={})
    with pytest.raises(ApiProviderError):
        build_api_runner("unknown-provider", env=ENV)


@pytest.mark.parametrize("document", [
    {},                                     # no choices
    {"choices": []},
    {"choices": [{"message": {"content": ""}}], "model": "m"},
    {"choices": [{"message": {"content": "x"}}]},   # no model id
])
def test_malformed_openai_response_raises(document):
    runner = build_api_runner("openai-api", transport=lambda *a: document, env=ENV)
    with pytest.raises(ApiProviderError):
        runner.run("p", stage="s")


def test_all_registered_providers_have_https_hosts():
    for spec in PROVIDERS.values():
        assert spec.host and "/" not in spec.host
        assert spec.api_key_env.endswith("_API_KEY")


# ---------------------------------------------------------------------------
# expert significance review (S1 -> S2)


def _expert_cert(**overrides):
    base = dict(
        certificate_id="expert-1",
        source_bytes_hash="a" * 64,
        informal_claim_hash="b" * 64,
        reviewer_id="prof-x",
        verdict="approved",
        statement_of_significance="fully resolves the stated problem",
        independent_from=("governor", "release"),
    )
    base.update(overrides)
    return ExpertReviewCertificate(**base)


def test_expert_review_sign_verify_roundtrip():
    signed = sign_expert_review(_expert_cert())
    assert verify_expert_review(signed)
    tampered = ExpertReviewCertificate.from_dict(
        {**signed.to_dict(), "verdict": "rejected"})
    assert not verify_expert_review(tampered)


@pytest.mark.parametrize("mutation", [
    {"conflicts": ("paid-by-author",)},
    {"independent_from": ()},
    {"statement_of_significance": ""},
    {"reviewer_id": "governor"},
    {"verdict": "maybe"},
])
def test_dishonest_approvals_are_refused_at_signing(mutation):
    with pytest.raises(ExpertReviewError):
        sign_expert_review(_expert_cert(**mutation))


def test_expert_reviewed_for_run_binds_the_exact_claim():
    signed = sign_expert_review(_expert_cert())
    assert expert_reviewed_for_run(
        signed, source_bytes_hash="a" * 64, informal_claim_hash="b" * 64)
    assert not expert_reviewed_for_run(
        signed, source_bytes_hash="c" * 64, informal_claim_hash="b" * 64)
    assert not expert_reviewed_for_run(
        None, source_bytes_hash="a" * 64, informal_claim_hash="b" * 64)
    rejected = sign_expert_review(_expert_cert(
        verdict="rejected", statement_of_significance=""))
    assert not expert_reviewed_for_run(
        rejected, source_bytes_hash="a" * 64, informal_claim_hash="b" * 64)


def test_expert_review_raises_significance_gate_to_s2(tmp_path):
    from egmra.intake import build_problem_contract
    from egmra.provenance.hashing import sha256_hex

    contract = build_problem_contract(
        problem_id="s2-run", source_bytes=TRUE_STATEMENT, source_id="s2",
        predicate=lambda n: n * n >= 0)
    interp = contract.lattice.nodes[0]
    expert = sign_expert_review(_expert_cert(
        source_bytes_hash=contract.source_bytes_hash,
        informal_claim_hash=sha256_hex(interp.conclusion)))
    baseline = research(
        problem_id="s2-run", source_bytes=TRUE_STATEMENT, source_id="s2",
        budget=100.0, enforcer=_enforcer(), worker=_fixture_worker(),
        goal_claim_id="goal", events_path=tmp_path / "e1.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        informal_only=True, status_claims=_status("s2-run"),
        intent_review=_intent("s2-run", source_id="s2"),
    )
    assert baseline.gates is not None and baseline.gates.significance == "S1"
    reviewed = research(
        problem_id="s2-run", source_bytes=TRUE_STATEMENT, source_id="s2",
        budget=100.0, enforcer=_enforcer(), worker=_fixture_worker(),
        goal_claim_id="goal", events_path=tmp_path / "e2.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        informal_only=True, status_claims=_status("s2-run"),
        intent_review=_intent("s2-run", source_id="s2"),
        expert_review=expert,
    )
    assert reviewed.gates is not None and reviewed.gates.significance == "S2"


# ---------------------------------------------------------------------------
# exploring blocked problems (release stays blocked)


# Deterministically parser-disputed: two interpretations, two open ambiguities
# -> release_blocked, and the selector declines acquisition (the live funnel).
AMBIGUOUS_STATEMENT = (
    b"Show that the sequence grows, where it is bounded, and there exists a limit."
)


def _blocked_research(tmp_path, problem_id, *, explore_blocked):
    return research(
        problem_id=problem_id, source_bytes=AMBIGUOUS_STATEMENT,
        source_id=problem_id, budget=100.0, enforcer=_enforcer(),
        worker=_fixture_worker(), goal_claim_id="goal",
        events_path=tmp_path / "e.jsonl", retrieval_corpus=_corpus(),
        informal_only=True, status_claims=_status(problem_id),
        explore_blocked=explore_blocked,
    )


def test_blocked_problem_is_not_explored_by_default(tmp_path):
    result = _blocked_research(tmp_path, "blocked-off", explore_blocked=False)
    assert not result.acquired
    assert "explore_blocked_override" not in result.phases
    assert len(result.graph.log) == 2          # frozen + interpretation only


def test_explore_blocked_researches_but_never_releases(tmp_path):
    result = _blocked_research(tmp_path, "blocked-on", explore_blocked=True)
    assert result.acquired
    assert "explore_blocked_override" in result.phases
    assert "acquisition_overridden_for_blocked_exploration" in result.failures
    # real branch work happened...
    assert len(result.graph.log) > 2
    # ...but a blocked interpretation can never certify.
    assert result.certificate is None and result.gates is None


# ---------------------------------------------------------------------------
# intent review resolves parser ambiguity (the I2 lift)


def _ambiguous_intent(problem_id, *, source_id):
    from egmra.intake import build_problem_contract
    from egmra.intake.review import (
        interpretation_review_hash,
        sign_intent_certificate,
    )
    from egmra.provenance.hashing import sha256_hex
    from egmra.truth.entities import IntentCertificate, Verdict

    contract = build_problem_contract(
        problem_id=problem_id, source_bytes=AMBIGUOUS_STATEMENT,
        source_id=source_id)
    interp = contract.lattice.nodes[0]
    return sign_intent_certificate(IntentCertificate(
        certificate_id=f"intent-{problem_id}",
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


def test_valid_intent_review_resolves_parser_ambiguity(tmp_path):
    result = research(
        problem_id="lift-1", source_bytes=AMBIGUOUS_STATEMENT, source_id="l1",
        budget=100.0, enforcer=_enforcer(), worker=_fixture_worker(),
        goal_claim_id="goal", events_path=tmp_path / "e.jsonl",
        retrieval_corpus=_corpus(), informal_only=True,
        status_claims=_status("lift-1"),
        intent_review=_ambiguous_intent("lift-1", source_id="l1"),
    )
    assert "interpretation_resolved_by_intent_review" in result.phases
    assert "intent_review_rejected" not in result.failures
    assert not result.contract.lattice.release_blocked   # ambiguity resolved
    # honest residue: intake probes without a predicate still gate RELEASE
    assert result.certificate is None


def test_mismatched_intent_review_never_lifts_ambiguity(tmp_path):
    # a certificate signed for a DIFFERENT statement cannot resolve this one
    wrong = _intent("lift-2", source_id="l2")     # bound to TRUE_STATEMENT
    result = research(
        problem_id="lift-2", source_bytes=AMBIGUOUS_STATEMENT, source_id="l2",
        budget=100.0, enforcer=_enforcer(), worker=_fixture_worker(),
        goal_claim_id="goal", events_path=tmp_path / "e.jsonl",
        retrieval_corpus=_corpus(), informal_only=True,
        status_claims=_status("lift-2"), intent_review=wrong,
    )
    assert "interpretation_resolved_by_intent_review" not in result.phases
    assert "intent_review_rejected" in result.failures
    assert result.contract.lattice.release_blocked


def test_intent_review_never_lifts_a_status_conflict(tmp_path):
    conflicted = [
        StatusClaim(problem_id="lift-3", status="open", source="local://a",
                    review_date="2026-07-13", source_independence="a"),
        StatusClaim(problem_id="lift-3", status="known", source="local://b",
                    review_date="2026-07-13", source_independence="b"),
    ]
    result = research(
        problem_id="lift-3", source_bytes=AMBIGUOUS_STATEMENT, source_id="l3",
        budget=100.0, enforcer=_enforcer(), worker=_fixture_worker(),
        goal_claim_id="goal", events_path=tmp_path / "e.jsonl",
        retrieval_corpus=_corpus(), informal_only=True,
        status_claims=conflicted,
        intent_review=_ambiguous_intent("lift-3", source_id="l3"),
    )
    assert "interpretation_resolved_by_intent_review" not in result.phases
    assert result.certificate is None


# ---------------------------------------------------------------------------
# checkpoint resume consumption


def _checkpointed_run(tmp_path, problem_id, *, ckpt_dir, resume_from=None,
                      events_name="e1.jsonl"):
    return research(
        problem_id=problem_id, source_bytes=TRUE_STATEMENT, source_id=problem_id,
        budget=100.0, enforcer=_enforcer(), worker=_fixture_worker(),
        goal_claim_id="goal", events_path=tmp_path / events_name,
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        informal_only=True, status_claims=_status(problem_id),
        intent_review=_intent(problem_id, source_id=problem_id),
        checkpoint_dir=ckpt_dir, resume_from=resume_from,
    )


def test_resume_treats_a_new_attempt_as_a_fresh_independent_sample(tmp_path):
    ckpt_dir = tmp_path / "ckpts"
    first = _checkpointed_run(tmp_path, "res-1", ckpt_dir=ckpt_dir)
    assert "checkpoint" in first.phases
    record = json.loads(sorted(
        (ckpt_dir / "res-1").glob("checkpoint_*.json"))[-1].read_text())
    assert record["controller_posteriors"]["attempted_branches"]
    second = _checkpointed_run(
        tmp_path, "res-1", ckpt_dir=ckpt_dir, resume_from=ckpt_dir,
        events_name="e2.jsonl")
    # An unverified chain (new event log) is a NEW attempt: no prior-branch
    # seeding, no prior-spend re-booking — the fresh sample must do real work.
    assert "resume_fresh_attempt" in second.phases
    assert "resume_verified" not in second.phases
    assert not any(f.startswith("resume_rejected") for f in second.failures)
    assert second.graph.claims["goal"].truth_status.value == "SUPPORTED"


def test_tampered_checkpoint_is_rejected_and_run_starts_fresh(tmp_path):
    ckpt_dir = tmp_path / "ckpts"
    _checkpointed_run(tmp_path, "res-2", ckpt_dir=ckpt_dir)
    path = sorted((ckpt_dir / "res-2").glob("checkpoint_*.json"))[-1]
    record = json.loads(path.read_text())
    record["controller_posteriors"] = {
        "attempted_branches": ["forged_branch_never_attempted"]}
    path.write_text(json.dumps(record))
    second = _checkpointed_run(
        tmp_path, "res-2", ckpt_dir=ckpt_dir, resume_from=ckpt_dir,
        events_name="e2.jsonl")
    assert any(f.startswith("resume_rejected") for f in second.failures)
    assert "resume_fresh_attempt" not in second.phases
    # fresh run is unharmed
    assert second.graph.claims["goal"].truth_status.value == "SUPPORTED"


def test_resume_from_empty_directory_is_a_plain_fresh_run(tmp_path):
    result = _checkpointed_run(
        tmp_path, "res-3", ckpt_dir=tmp_path / "ckpts",
        resume_from=tmp_path / "nothing-here")
    assert not any(f.startswith("resume_rejected") for f in result.failures)
    assert result.graph.claims["goal"].truth_status.value == "SUPPORTED"


# ---------------------------------------------------------------------------
# formalizer portfolio


def test_extract_lean_source_variants():
    fenced = "Sure!\n```lean\nimport Mathlib\ntheorem t : True := trivial\n```\nDone."
    assert extract_lean_source(fenced).startswith("import Mathlib")
    bare = "import Mathlib\n\ntheorem t : True := trivial"
    assert extract_lean_source(bare) == bare
    assert extract_lean_source("I could not prove this.") == ""
    assert extract_lean_source("") == ""


def test_api_formalizer_builds_prompt_and_extracts_source():
    calls = []

    class FakeRunner:
        def run(self, prompt, stage):
            calls.append((prompt, stage))
            return SimpleNamespace(
                text="```lean\nimport Mathlib\ntheorem x : True := trivial\n```")

    formalizer = ApiFormalizer(runner=FakeRunner())
    produced = formalizer.formalize(
        declaration_name="x", expected_type="True", informal_statement="s",
        kernel_feedback="unknown identifier")
    assert produced and "theorem x" in produced
    assert calls[0][1] == "formalize"
    assert "REPAIR ROUND" in calls[0][0] and "unknown identifier" in calls[0][0]


def test_portfolio_falls_through_dead_and_empty_members():
    class Dead:
        formalizer_id = "dead"

        def formalize(self, **kwargs):
            raise RuntimeError("outage")

    class Empty:
        formalizer_id = "empty"

        def formalize(self, **kwargs):
            return None

    class Live:
        formalizer_id = "live"

        def formalize(self, *, declaration_name, expected_type,
                      informal_statement, previous_source="", kernel_feedback=""):
            return "import Mathlib\ntheorem t : True := trivial"

    portfolio = PortfolioFormalizer(members=[Dead(), Empty(), Live()])
    produced = portfolio.formalize(
        declaration_name="t", expected_type="True", informal_statement="s")
    assert produced and "theorem t" in produced


def test_portfolio_legacy_member_serves_round_one_but_never_repairs():
    class Legacy:
        formalizer_id = "legacy"
        calls = 0

        def formalize(self, *, declaration_name, expected_type,
                      informal_statement):
            Legacy.calls += 1
            return "import Mathlib\ntheorem l : True := trivial"

    portfolio = PortfolioFormalizer(members=[Legacy()])
    assert portfolio.formalize(
        declaration_name="l", expected_type="True", informal_statement="s")
    # repair round: the legacy member cannot accept feedback -> no member serves
    assert portfolio.formalize(
        declaration_name="l", expected_type="True", informal_statement="s",
        kernel_feedback="error") is None
    assert Legacy.calls == 1


def test_portfolio_all_members_dead_returns_none():
    class Dead:
        formalizer_id = "dead"

        def formalize(self, **kwargs):
            raise RuntimeError("outage")

    assert PortfolioFormalizer(members=[Dead()]).formalize(
        declaration_name="x", expected_type="True",
        informal_statement="s") is None


# ---------------------------------------------------------------------------
# calibration report (R11)


def test_calibration_report_counts_honestly(tmp_path):
    ledger = tmp_path / "outcomes.jsonl"
    rows = [
        {"problem_id": "erdos-1", "public_state": "OPEN_NO_PROGRESS",
         "recorded_at": "2026-07-14T01:00:00Z", "released": False,
         "salvage": {"supported": [{"claim_id": "lem"}], "refuted": []}},
        {"problem_id": "erdos-1", "public_state": "COMPUTATIONAL_EVIDENCE",
         "recorded_at": "2026-07-14T02:00:00Z", "released": False,
         "gate_profile": {"truth": "T2"}},
        {"problem_id": "erdos-2", "public_state": "BLOCKED_BY_INTERPRETATION",
         "recorded_at": "2026-07-14T01:30:00Z", "released": False},
    ]
    ledger.write_text(
        "\n".join(json.dumps(r) for r in rows) + "\nnot json\n")
    report = build_calibration_report([ledger])
    assert report["total_runs"] == 3
    assert report["malformed_lines"] == 1
    assert report["by_state"]["OPEN_NO_PROGRESS"] == 1
    assert report["by_problem"]["erdos-1"]["attempts"] == 2
    assert report["by_problem"]["erdos-1"]["last_state"] == "COMPUTATIONAL_EVIDENCE"
    assert report["gate_truth_distribution"] == {"T2": 1}
    assert report["salvaged_supported_claims"] == 1
    assert report["released_problem_ids"] == []
    assert "not posteriors" in report["note"]


def test_calibration_rejects_symlinked_ledger(tmp_path):
    real = tmp_path / "real.jsonl"
    real.write_text("")
    link = tmp_path / "link.jsonl"
    link.symlink_to(real)
    with pytest.raises(ValueError):
        build_calibration_report([link])


# ---------------------------------------------------------------------------
# salvage (R7) + cross-problem priors (R12-lite)


def test_outcome_record_salvages_subsidiary_claims(tmp_path):
    result = _checkpointed_run(tmp_path, "salvage-1", ckpt_dir=None)
    record = build_outcome_record(
        problem_id="salvage-1", result=result, run_id="r1",
        state="COMPUTATIONAL_EVIDENCE")
    assert "salvage" in record
    salvaged_ids = {c["claim_id"] for c in record["salvage"]["supported"]}
    assert "goal" not in salvaged_ids          # the goal is never "salvage"
    for claim in record["salvage"]["supported"]:
        assert claim["canonical_hash"] and claim["profile"] is not None


def test_cross_problem_priors_accumulate_in_shared_memory(tmp_path):
    from egmra.learning import LongTermMemory

    memory = LongTermMemory()
    research(
        problem_id="prior-1", source_bytes=TRUE_STATEMENT, source_id="p1",
        budget=100.0, enforcer=_enforcer(), worker=_fixture_worker(),
        goal_claim_id="goal", events_path=tmp_path / "e1.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        informal_only=True, status_claims=_status("prior-1"),
        intent_review=_intent("prior-1", source_id="p1"), memory=memory,
    )
    outcomes = [r for r in memory.procedural.records
                if r.get("kind") == "branch_family_outcome"]
    assert outcomes and any(r["supported"] for r in outcomes)
    # a second run sharing the memory replays those priors and still succeeds
    second = research(
        problem_id="prior-2", source_bytes=TRUE_STATEMENT, source_id="p2",
        budget=100.0, enforcer=_enforcer(), worker=_fixture_worker(),
        goal_claim_id="goal", events_path=tmp_path / "e2.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        informal_only=True, status_claims=_status("prior-2"),
        intent_review=_intent("prior-2", source_id="p2"), memory=memory,
    )
    assert second.graph.claims["goal"].truth_status.value == "SUPPORTED"
