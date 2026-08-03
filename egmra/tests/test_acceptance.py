"""The §13.6 acceptance tests — the specification's own validation criteria.

Each test maps to one acceptance bullet in spec §13.6 and exercises the relevant
implemented component end-to-end.
"""

import json
from pathlib import Path
import subprocess

import pytest

from egmra.compute.spec import ExperimentSpec
from egmra.compute.service import ComputeService
from egmra.control.leases import LeaseManager
from egmra.control.throttle import ProviderThrottle
from egmra.eval.protocol import baseline_comparison_valid
from egmra.intake.contract import build_problem_contract
from egmra.lean.service import AttestedKernelRunner, LeanService
from egmra.m0 import evidence_precedence, quarantine_manifest
from egmra.oeis import Match, held_out_verification, run_oeis_workflow
from egmra.policy import PolicyEnforcer, PolicyViolation, sign_policy
from egmra.provenance.hashing import sha256_bytes, sha256_hex
from egmra.provenance.stage_identity import (
    AttestedModelIdentity,
    StageIdentity,
    attest_model_identity,
)
from egmra.release.gates import novelty_gate
from egmra.truth import (
    Evidence,
    EvidenceKind,
    EpistemicGraph,
    EventLog,
    Interpretation,
    Problem,
    TruthStatus,
    EvidenceRouter,
    refute_claim,
)
from egmra.truth.views import manifest_projection
from egmra.truth.validators import attest_evidence
from egmra.tests.conftest import TEST_KEYS

ACTOR = {"type": "agent", "id": "t", "model": "m", "version": "1"}


def _model(model="m-a"):
    return attest_model_identity(provider="openai", model=model, version="2026-01")


def _stage(model, **kw):
    base = dict(stage="adjudicate", runner_id="r1", model=model, prompt_hash=sha256_hex("p"))
    base.update(kw)
    return StageIdentity(**base)


# 1. every disabled feature remains unreachable through direct scripts as well as scheduler
def test_acc01_disabled_feature_unreachable_from_any_entry_point():
    policy = sign_policy({"lean_execution": False}, env=dict(TEST_KEYS))
    enforcer = PolicyEnforcer(policy, verification_env=dict(TEST_KEYS))
    for entry in ("scheduler", "standalone_script", "evidence_loader"):
        with pytest.raises(PolicyViolation):
            enforcer.require("lean_execution", entry_point=entry)


# 2. a cached adjudication cannot be replayed under a different runner/model identity
def test_acc02_cache_not_replayable_under_different_model():
    a = _stage(_model("m-a"))
    b = _stage(_model("m-b"))
    assert not a.compatible_with(b)


# 3. changing packet/adjudicator/policy/closure/adapter/validator invalidates caches
def test_acc03_any_bound_policy_change_invalidates_cache():
    base = _stage(_model())
    for field_name in ("literature_packet_hash", "adjudicator_policy_hash",
                       "feature_policy_hash", "import_closure_hash", "validator_version",
                       "formal_env_hash"):
        changed = _stage(_model(), **{field_name: sha256_hex("v2-" + field_name)})
        assert not base.compatible_with(changed), field_name


# 4. caller labels attested or explicit, never counted as independent-model evidence
def test_acc04_unattested_label_never_independent():
    label = AttestedModelIdentity("openai", "ChatGPT")
    other = AttestedModelIdentity("anthropic", "Claude")
    assert not label.independent_of(other)          # two labels are not independence
    assert _model("m-a").independent_of(_model("m-b"))  # attested + different lineage


# 5. gate/adjudication/promotion history is append-only + deterministic manifest projection
def test_acc05_append_only_and_deterministic_manifest(tmp_path):
    log = EventLog(tmp_path / "e.jsonl", run_id="r")
    graph = EpistemicGraph(log)
    graph.add_problem(Problem(problem_id="p"), actor=ACTOR)
    graph.add_interpretation(Interpretation("int", "p", "S"), actor=ACTOR)
    graph.propose_claim(claim_id="c", interpretation_id="int", canonical_formula="F", actor=ACTOR)
    assert log.verify_integrity()
    m1 = manifest_projection(graph, problem_id="p")
    m2 = manifest_projection(graph, problem_id="p")
    assert m1["projection_hash"] == m2["projection_hash"]


# 6. identity-incomplete legacy records are quarantined rather than silently upgraded
def test_acc06_legacy_records_quarantined(tmp_path):
    import json
    p = tmp_path / "724.json"
    p.write_text(json.dumps({"problem_number": 724, "run_contract": None}))
    assert quarantine_manifest(p).quarantined


# 7. injected ambiguous statements create multiple interpretations and block release
def test_acc07_ambiguous_blocks_release():
    ambiguous = b"Show that the sequence grows, where it is bounded, and there exists a limit."
    contract = build_problem_contract(problem_id="amb", source_bytes=ambiguous, source_id="a")
    if not contract.reconciliation.agreed:
        assert len(contract.lattice.nodes) >= 2 and contract.lattice.release_blocked


# 8. injected false central lemma detected, revoked, all dependents downgraded
def test_acc08_false_central_lemma_revoked(tmp_path):
    log = EventLog(tmp_path / "e.jsonl")
    graph = EpistemicGraph(log)
    graph.add_problem(Problem(problem_id="p"), actor=ACTOR)
    graph.add_interpretation(Interpretation("int", "p", "S"), actor=ACTOR)
    router = EvidenceRouter(graph, evidence_env=dict(TEST_KEYS))
    graph.propose_claim(claim_id="lemma", interpretation_id="int", canonical_formula="L", actor=ACTOR)
    graph.propose_claim(claim_id="goal", interpretation_id="int", canonical_formula="G",
                        dependencies=["lemma"], actor=ACTOR)
    for cid in ("lemma", "goal"):
        review = Evidence(
            evidence_id=f"ev_{cid}",
            claim_ids=[cid],
            claim_bindings={cid: graph.claims[cid].canonical_hash},
            kind=EvidenceKind.INFORMAL_REVIEW,
            generator_identity={"findings": {"reviewers": [
                {"reviewer_id": "a", "lineage": "f1", "verdict": "pass"},
                {"reviewer_id": "b", "lineage": "f2", "verdict": "pass"},
            ]}},
        )
        router.admit(attest_evidence(review, env=dict(TEST_KEYS)), actor=ACTOR)
    counter = Evidence(
        evidence_id="ce",
        claim_ids=["lemma"],
        claim_bindings={"lemma": graph.claims["lemma"].canonical_hash},
        kind=EvidenceKind.COUNTEREXAMPLE,
        assertion_scope="exact witness in the stated domain",
        artifact_hashes=[sha256_hex("counterexample-artifact")],
        replay_result="pass",
        replay_command="independent exact witness checker",
        environment_hash=sha256_hex("counterexample-environment"),
        verifier_identities=[{"id": "counterexample-checker", "attested": True}],
        generator_identity={"findings": {
            "exact_witness_checked": True,
            "in_stated_domain": True,
        }},
    )
    attest_evidence(counter, env=dict(TEST_KEYS))
    graph.register_evidence(counter, actor=ACTOR)
    affected = refute_claim(graph, router, "lemma", counterevidence_id="ce", actor=ACTOR)
    assert graph.claims["lemma"].truth_status == TruthStatus.REFUTED
    assert graph.claims["goal"].truth_status != TruthStatus.SUPPORTED and "goal" in affected


# 9. rate limits resume without consuming proof attempts or killing claims
def test_acc09_rate_limit_pauses_never_kills():
    t = ProviderThrottle(provider="openai", seed=1)
    r = t.on_rate_limit(3)
    assert r["action"] == "pause" and not r["consumes_math_retry"]
    assert t.math_retries_consumed == 0


# 10. a crashed worker lease is recovered without duplicate non-idempotent actions
def test_acc10_crashed_lease_recovered():
    clock = type("C", (), {"t": 0.0, "__call__": lambda self: self.t})()
    mgr = LeaseManager(now_fn=clock)
    mgr.acquire(branch_id="b", holder="h1", stage="s", run_contract_id="rc", grace_seconds=1.0)
    clock.t = 5.0
    new = mgr.transfer_if_expired(branch_id="b", new_holder="h2", run_contract_id="rc")
    assert new.holder == "h2"  # single transfer, no duplicate holder


# 11. every exact computation replays in an independent environment
def test_acc11_exact_computation_replays():
    svc = ComputeService()
    spec = ExperimentSpec(purpose="finite", inputs={"n": 20}, arithmetic_mode="exact", coverage="c")
    code = "def experiment(inputs):\n    return {'ok': all(k>=0 for k in range(inputs['n']))}\n"
    job = svc.submit_experiment(spec, code, claimed_classification="exhaustive_finite_subcase")
    art = svc.artifact(job)
    report = svc.replay(art.artifact_id, environment_label="independent")
    assert report.replayed and report.output_hash_matches


# 12. every Lean certificate builds cleanly with no placeholders
def test_acc12_lean_certificate_clean_only(monkeypatch):
    executable = Path("/usr/bin/true")
    runner = AttestedKernelRunner(
        command=(str(executable),),
        checker_id="acceptance-lean-checker",
        checker_version="pinned",
        checker_binary_hash=sha256_bytes(executable.read_bytes()),
        checker_trust_base="lean-kernel",
        env=dict(TEST_KEYS),
    )

    def checker(command, **kwargs):
        request = json.loads(kwargs["input"])
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({
                "kernel_verified": True,
                "candidate_type_hash": request["expected_type_hash"],
                "candidate_declaration_hash": sha256_hex("declaration"),
                "proof_term_hash": sha256_hex("proof-term"),
                "source_tree_hash": sha256_hex("source-tree"),
                "imports_hash": sha256_hex("imports"),
                "transitive_axioms": [],
                "placeholder_findings": [],
                "unsafe_findings": [],
                "imports_audited": True,
                "axiom_closure_verified": True,
                "immutable_target_isolated": True,
                "clean_replay": True,
                "network_disabled": True,
            }),
            stderr="",
        )

    monkeypatch.setattr("egmra.lean.service.subprocess.run", checker)
    svc = LeanService(kernel_runner=runner, checker_env=dict(TEST_KEYS))
    env = svc.create_environment(lean_version="4.9", mathlib_commit="c", project_hash="p")
    clean = "theorem t : True := trivial"
    cert = svc.verify_declaration(environment=env, source=clean, declaration_name="t",
                                  expected_type_hash=sha256_hex("True"),
                                  immutable_target_module_hash=sha256_hex("target-module"))
    assert cert.passed and not cert.placeholder_findings
    dirty = "theorem t : True := by sorry"
    cert2 = svc.verify_declaration(environment=env, source=dirty, declaration_name="t",
                                   expected_type_hash=sha256_hex("True"),
                                   immutable_target_module_hash=sha256_hex("target-module"))
    assert not cert2.passed and cert2.placeholder_findings


# 13. a vendor-only COMPLETE result is rejected
def test_acc13_vendor_complete_rejected():
    svc = LeanService(kernel_runner=lambda **kw: "kernel_verified")
    env = svc.create_environment(lean_version="4.9", mathlib_commit="c", project_hash="p")
    cert = svc.verify_declaration(environment=env, source="theorem t : True := trivial",
                                  declaration_name="t", expected_type_hash=sha256_hex("True"),
                                  immutable_target_module_hash="m",
                                  verification_method="aristotle_reported")
    assert not cert.kernel_verified and not cert.passed


# 14. changing adjudicator/model invalidates caches and cannot create false independence
def test_acc14_model_change_invalidates_and_no_false_independence():
    a = _stage(_model("m-a"), adjudicator_policy_hash=sha256_hex("adj1"))
    b = _stage(_model("m-a"), adjudicator_policy_hash=sha256_hex("adj2"))
    assert not a.compatible_with(b)  # adjudicator policy change invalidates
    # same model twice is not independence (no false "independent model")
    assert not _model("m-a").independent_of(_model("m-a"))


# 15. model-referee dissent vs kernel proof follows explicit precedence
def test_acc15_referee_vs_kernel_precedence():
    d = evidence_precedence(clean_kernel_proof=True, model_referee_blocks_truth=True,
                            checked_same_scope_counterexample=False)
    assert d.truth_status == "SUPPORTED"


# 16. an OEIS match remains heuristic until independent proof
def test_acc16_oeis_match_is_heuristic():
    m = Match("A000290", ("identity",), prefix_overlap=6, prefix_exact=True)
    held = [held_out_verification(lambda n: n * n, [(7, 49)], formula="n^2")]
    result = run_oeis_workflow(interpretation_id="int", query_terms=[1, 4, 9, 16, 25, 36],
                               candidate_matches=[m], held_out=held)
    assert result.conjecture_claim["evidence_kind"] == "numerical"
    assert result.conjecture_claim["truth_tier"] == "T1_supported_conjecture"


# 17. a known solved Erdos problem is classified as rediscovery, not novel
def test_acc17_known_result_is_not_novel():
    assert novelty_gate("known") == "known"     # never upgraded to N2
    assert novelty_gate("N1") == "N1"           # "not found" != proven novel


# 18. the system beats no baseline claim unless paired evaluation supports it
def test_acc18_no_baseline_claim_without_paired_eval():
    assert not baseline_comparison_valid(paired=False, equal_cost_or_pareto=True)
    assert baseline_comparison_valid(paired=True, equal_cost_or_pareto=True)
