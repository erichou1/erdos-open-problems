"""M0 safety & provenance tests (spec §13.2, §16 P0)."""

import json


from egmra.m0 import (
    LEGACY_QUARANTINE_PROBLEMS,
    PromotionGuard,
    PromotionTelemetry,
    evidence_precedence,
    is_identity_incomplete,
    quarantine_manifest,
)
from egmra.policy import PolicyEnforcer, sign_policy


def _enforcer(flags):
    return PolicyEnforcer(sign_policy(flags))


def test_promotion_guard_blocks_when_disabled():
    guard = PromotionGuard(_enforcer({"promotion": False}))
    ok, reason = guard.check(formal=False)
    assert not ok and "promotion" in reason


def test_promotion_guard_allows_when_signed_enabled():
    guard = PromotionGuard(_enforcer({"promotion": True, "formal_promotion": True}))
    ok, _ = guard.check(formal=True)
    assert ok


def test_evidence_precedence_kernel_not_overruled_by_model_referee():
    d = evidence_precedence(clean_kernel_proof=True, model_referee_blocks_truth=True,
                            checked_same_scope_counterexample=False)
    assert d.truth_status == "SUPPORTED"  # model referee cannot overrule kernel truth
    assert any("cannot overrule" in r for r in d.reasons)


def test_evidence_precedence_counterexample_conflicts_kernel():
    d = evidence_precedence(clean_kernel_proof=True, model_referee_blocks_truth=False,
                            checked_same_scope_counterexample=True)
    assert d.truth_status == "CONFLICTED" and d.release_blocked


def test_evidence_precedence_intent_blocks_release_even_with_proof():
    d = evidence_precedence(clean_kernel_proof=True, model_referee_blocks_truth=False,
                            checked_same_scope_counterexample=False, intent_blocks=True)
    assert d.truth_status == "SUPPORTED" and d.release_blocked


def test_legacy_manifest_quarantine(tmp_path):
    # identity-incomplete manifest (null run_contract) -> quarantined
    incomplete = tmp_path / "601.json"
    incomplete.write_text(json.dumps({"problem_number": 601, "run_contract": None}))
    rec = quarantine_manifest(incomplete)
    assert rec.quarantined and rec.problem_number == 601
    # a named legacy problem is quarantined even if fields look present
    named = tmp_path / "849.json"
    named.write_text(json.dumps({"problem_number": 849, "run_contract": {"x": 1},
                                 "execution_id": "e", "run_contract_id": "c", "run_context_id": "x"}))
    rec2 = quarantine_manifest(named)
    assert rec2.quarantined and "legacy" in rec2.reason
    assert set(LEGACY_QUARANTINE_PROBLEMS) == {601, 661, 724, 782, 849}


def test_identity_incompleteness_detection():
    incomplete, missing = is_identity_incomplete({"problem_number": 1})
    assert incomplete and "run_contract" in missing
    complete, _ = is_identity_incomplete({
        "run_contract": {"x": 1}, "execution_id": "e", "run_contract_id": "c",
        "run_context_id": "x"})
    assert not complete


def test_promotion_telemetry_accumulates():
    tel = PromotionTelemetry()
    tel.record(tokens=100, calls=1, rate_limit_pauses=1)
    tel.record(tokens=50, calls=1, terminal_disposition="verified_proved")
    report = tel.report()
    assert report["tokens"] == 150 and report["calls"] == 2
    assert report["terminal_disposition"] == "verified_proved"


def test_promote_entrypoint_blocks_without_signed_policy(tmp_path):
    """The existing promote() entry point blocks promotion under the default policy."""
    from promote_verified_run import promote
    from proof_pipeline import ProofPipeline

    # Build a real run, then try to promote with the default (promotion-disabled) policy.
    class _Passing:
        def __init__(self):
            self.calls = []

        def run(self, prompt, *, stage, isolated):
            self.calls.append(stage)
            return _canned(stage)

        def context_id(self, stage):
            return f"ctx-{stage}"

        def restore_context(self, stage, context_id):
            pass

    result = ProofPipeline(_Passing(), tmp_path / "runs").solve(9, "Prove T.")
    evidence = tmp_path / "ev.json"
    candidate = (result.artifact_dir / "candidate.md").read_text()
    import hashlib
    from research_state import make_statement_lock
    evidence.write_text(json.dumps([{
        "kind": "expert_review", "verifier": "x", "outcome": "candidate_proved",
        "statement_sha256": make_statement_lock("Prove T.").sha256,
        "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
        "artifact_path": str(tmp_path / "a.txt"), "passed": True}]))
    (tmp_path / "a.txt").write_text("x")
    promoted = promote(result.artifact_dir, evidence, publish=False, category="open",
                       base_dir=tmp_path)
    assert promoted.gate.status == "promotion_disabled_by_policy"


def _canned(stage: str) -> str:
    result = """<result>
OUTCOME: CANDIDATE_PROVED
COMPLETENESS_SCORE: 100
PROOF_CONFIDENCE: 99
ADVERSARIAL_SURVIVAL_SCORE: 99
OPEN_GAPS: NONE
UNCHECKED_IMPORTS: NONE
CLAIMS_CHECKED: 7
CLAIMS_TOTAL: 7
CLAIM_IDS: C1; C2; C3; C4; C5; C6; C7
</result>"""
    if stage.startswith("scout") or stage == "synthesize":
        return '{"subgoals": [{"id": "GOAL", "claim": "T", "dependencies": [], "centrality": 5, "falsifiable": true}], "bottleneck_ids": ["GOAL"], "summary": "s"}'
    if stage.startswith("review") or stage.startswith("adjudication") or stage == "regulate":
        return result
    return result
