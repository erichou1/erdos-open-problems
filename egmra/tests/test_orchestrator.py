"""Orchestration tests: end-to-end research loop (M1 slice), checkpoint, roles."""

from egmra.compute.spec import ExperimentSpec
from egmra.corpus.status import StatusClaim
from egmra.intake import build_problem_contract
from egmra.intake.review import interpretation_review_hash, sign_intent_certificate
from egmra.orchestrator import (
    DeterministicWorker,
    RoleLayout,
    research,
    resume,
    take_checkpoint,
)
from egmra.policy import PolicyEnforcer, sign_policy
from egmra.retrieval.records import TheoremRecord
from egmra.provenance.hashing import sha256_hex
from egmra.truth.events import EventLog
from egmra.truth.entities import IntentCertificate, Verdict

# A true finite claim: "for all n in 0..50, n*n >= 0".
FINITE_CODE = """
def experiment(inputs):
    n = inputs["n"]
    ok = all((k * k) >= 0 for k in range(n + 1))
    return {"result": ok, "coverage": "k in 0..n exhaustive"}
"""

TRUE_STATEMENT = b"Prove that for all natural numbers n, n squared is at least 0."
FALSE_STATEMENT = b"Prove that for all positive integers n, n is prime."


POLICY_ENV = {"EGMRA_POLICY_KEY": "orchestrator-test-policy-key-32-bytes"}


def _enforcer():
    policy = sign_policy({
        "claim_graph": True, "literature_retrieval": True, "computation_service": True,
        "promotion": False, "formal_promotion": False,
    }, env=POLICY_ENV)
    return PolicyEnforcer(policy, verification_env=POLICY_ENV)


def _corpus():
    return [TheoremRecord(theorem_id="thm-sq", canonical_statement="squares are nonnegative",
                          conclusion="n squared is nonnegative", source_uri="u", source_version="v1",
                          source_content_hash="h", verbatim_theorem_and_hypothesis_extract="x")]


def _worker():
    spec = ExperimentSpec(
        purpose="finite nonneg", inputs={"n": 50}, arithmetic_mode="exact",
        coverage="k in 0..n", claim_ids=("goal",),
    )
    return DeterministicWorker(
        goal_claim_id="goal", goal_formula="for all n, n*n >= 0", goal_scope="finite_domain",
        experiment_code=FINITE_CODE, experiment_spec=spec)


def _current_status(problem_id: str):
    return [StatusClaim(
        problem_id=problem_id, status="open", source="local://test-status",
        review_date="2026-07-13", source_independence="test-fixture",
    )]


def _intent_review(problem_id: str, *, source_id: str) -> IntentCertificate:
    contract = build_problem_contract(
        problem_id=problem_id, source_bytes=TRUE_STATEMENT, source_id=source_id,
        predicate=lambda n: n * n >= 0,
    )
    interp = contract.lattice.nodes[0]
    return sign_intent_certificate(IntentCertificate(
        certificate_id=f"intent-{problem_id}",
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


def test_end_to_end_finite_claim_reaches_verified_result(tmp_path):
    result = research(
        problem_id="erdos-fixture-1", source_bytes=TRUE_STATEMENT, source_id="fx1",
        budget=100.0, enforcer=_enforcer(), worker=_worker(), goal_claim_id="goal",
        events_path=tmp_path / "events.jsonl", retrieval_corpus=_corpus(),
        probe_predicate=lambda n: n * n >= 0, informal_only=True,
        status_claims=_current_status("erdos-fixture-1"),
        intent_review=_intent_review("erdos-fixture-1", source_id="fx1"),
    )
    # cold pass precedes packet freeze precedes deep branches (two-pass protocol)
    assert result.phases.index("cold_pass") < result.phases.index("freeze_solver_packet")
    assert result.phases.index("freeze_solver_packet") < result.phases.index("deep_branches")
    # the goal claim reached SUPPORTED via exact finite computation (T2)
    assert result.graph.claims["goal"].truth_status.value == "SUPPORTED"
    assert result.gates is not None and result.gates.truth == "T2"
    assert result.compiled_proof.complete
    # event log integrity holds
    assert result.graph.log.verify_integrity()


def test_false_statement_produces_honest_triage(tmp_path):
    result = research(
        problem_id="erdos-fixture-false", source_bytes=FALSE_STATEMENT, source_id="fx2",
        budget=100.0, enforcer=_enforcer(),
        worker=DeterministicWorker(goal_claim_id="goal", goal_formula="all n prime"),
        goal_claim_id="goal", events_path=tmp_path / "events2.jsonl",
        retrieval_corpus=_corpus(),
        probe_predicate=lambda n: _is_prime(n),
        status_claims=_current_status("erdos-fixture-false"),
    )
    # counterexample probe blocks release -> honest triage, never promoted
    assert result.outcome == "honest_triage_report"
    assert result.certificate is None


def test_promotion_blocked_by_feature_policy_even_when_supported(tmp_path):
    result = research(
        problem_id="erdos-fixture-2", source_bytes=TRUE_STATEMENT, source_id="fx3",
        budget=100.0, enforcer=_enforcer(), worker=_worker(), goal_claim_id="goal",
        events_path=tmp_path / "events3.jsonl", retrieval_corpus=_corpus(),
        probe_predicate=lambda n: n * n >= 0, informal_only=True,
        status_claims=_current_status("erdos-fixture-2"),
        intent_review=_intent_review("erdos-fixture-2", source_id="fx3"),
    )
    # T2 verified finite result, but informal promotion needs T3 AND the feature is off
    assert result.promotion is not None and not result.promotion.promoted


def test_research_result_render(tmp_path):
    result = research(
        problem_id="erdos-fixture-3", source_bytes=TRUE_STATEMENT, source_id="fx4",
        budget=100.0, enforcer=_enforcer(), worker=_worker(), goal_claim_id="goal",
        events_path=tmp_path / "events4.jsonl", retrieval_corpus=_corpus(),
        probe_predicate=lambda n: n * n >= 0,
        status_claims=_current_status("erdos-fixture-3"),
        intent_review=_intent_review("erdos-fixture-3", source_id="fx4"),
    )
    rendered = result.render()
    assert not rendered["proof_complete"]
    assert rendered["candidate_assembly_complete"] and rendered["event_count"] > 0
    assert "confidence" not in str(rendered)  # never a confidence %


# ── checkpoint / resume ──────────────────────────────────────────────────────

def test_checkpoint_and_resume_detects_closure_change(tmp_path):
    log = EventLog(tmp_path / "e.jsonl", run_id="r")
    log.append(action="PROBLEM_FROZEN", actor={"type": "agent", "id": "g"}, object_ids=["p"])
    cache_identity_v1 = sha256_hex("scout-cache-identity-v1")
    ckpt = take_checkpoint(
        log=log, problem_contract_hash=sha256_hex("pc"),
        interpretation_hashes=(sha256_hex("ih"),),
        graph_view_hash=sha256_hex("gv"), controller_posteriors={}, budgets={}, seeds={},
        active_leases=(), behavior_closure_fingerprint=sha256_hex("closure-v1"),
        in_flight_calls=("scout_call",),
        stage_caches={"scout": {
            "artifact_hash": sha256_hex("cache1"),
            "compatibility_fingerprint": cache_identity_v1,
            "replay_policy_hash": sha256_hex("replay-policy-v1"),
            "durable_stage": 1,
        }})
    # same closure -> compatible, caches reused
    same = resume(
        ckpt, log=log, current_closure_fingerprint=sha256_hex("closure-v1"),
        current_stage_fingerprints={"scout": cache_identity_v1},
    )
    assert same.ok and same.closure_compatible and same.invalidated_caches == ()
    # changed closure -> incompatible caches invalidated (no math retry consumed)
    changed = resume(
        ckpt, log=log, current_closure_fingerprint=sha256_hex("closure-v2"),
        interrupted_calls=("scout_call",),
        current_stage_fingerprints={"scout": sha256_hex("scout-cache-identity-v2")},
    )
    assert changed.chain_verified and not changed.closure_compatible
    assert "scout" in changed.invalidated_caches
    assert changed.censored_calls == ("scout_call",)


def test_role_layout():
    layout = RoleLayout()
    assert "governor_intake" in layout.concurrent_roles()
    assert "retrieval" in layout.services()
    assert layout.total_concurrent() >= 4


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True
