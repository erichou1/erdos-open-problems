"""Independent adversarial regressions found during the FABLE audit.

These tests exercise production entry points.  They intentionally avoid the
implementation helpers that previously supplied self-affirming expected values.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor

import pytest

from egmra.compute import ComputeService, ExperimentSpec
from egmra.lean import AttestedKernelRunner, LeanService
from egmra.lean import sign_formal_correspondence_certificate
from egmra.intake.review import sign_intent_certificate
from egmra.policy import (
    FeaturePolicy,
    PolicyEnforcer,
    PolicyError,
    default_policy_path,
    load_policy,
    sign_policy,
)
from egmra.truth import (
    Branch,
    EpistemicGraph,
    EventLog,
    EventLogError,
    Evidence,
    EvidenceProfile,
    EvidenceKind,
    EvidenceRouter,
    ExactComputation,
    FormalCorrespondenceCertificate,
    GraphError,
    Interpretation,
    IntentCertificate,
    Problem,
    TruthStatus,
    Verdict,
    invalidate_evidence,
)
from egmra.truth.validators import attest_evidence
from egmra.provenance.hashing import sha256_bytes, sha256_hex


ACTOR = {"type": "agent", "id": "audit", "model": "none", "version": "1"}
EVENT_ENV = {"EGMRA_EVENT_KEY": "event-test-key-that-is-at-least-32-bytes"}
POLICY_ENV = {"EGMRA_POLICY_KEY": "policy-test-key-that-is-at-least-32-bytes"}
EVIDENCE_ENV = {"EGMRA_EVIDENCE_KEY": "evidence-test-key-that-is-at-least-32-bytes"}
LEAN_ENV = {
    "EGMRA_LEAN_CHECKER_KEY": "lean-checker-test-key-that-is-at-least-32-bytes",
    "EGMRA_INTENT_REVIEW_KEY": "intent-review-test-key-that-is-at-least-32-bytes",
    "EGMRA_FORMAL_CORRESPONDENCE_KEY": (
        "formal-correspondence-test-key-that-is-at-least-32-bytes"
    ),
}


def _graph(path) -> EpistemicGraph:
    graph = EpistemicGraph(EventLog(path, run_id="audit", env=EVENT_ENV))
    graph.add_problem(Problem(problem_id="p"), actor=ACTOR)
    graph.add_interpretation(Interpretation("i", "p", "S"), actor=ACTOR)
    graph.propose_claim(
        claim_id="c",
        interpretation_id="i",
        canonical_formula="False",
        scope="finite_domain",
        actor=ACTOR,
    )
    return graph


def test_unsigned_feature_policy_fails_closed() -> None:
    """An unsigned/default or caller-constructed policy is not a signed policy."""

    with pytest.raises(PolicyError):
        load_policy(default_policy_path(), env={})
    with pytest.raises(PolicyError):
        sign_policy({"claim_graph": True}, env={})
    with pytest.raises(PolicyError):
        PolicyEnforcer(FeaturePolicy(flags={"promotion": True}))


def test_signed_feature_policy_is_bound_to_the_verification_key() -> None:
    policy = sign_policy({"claim_graph": True, "promotion": False}, env=POLICY_ENV)
    enforcer = PolicyEnforcer(policy, verification_env=POLICY_ENV)
    enforcer.require("claim_graph", entry_point="audit")
    with pytest.raises(PolicyError):
        PolicyEnforcer(policy, verification_env={"EGMRA_POLICY_KEY": "x" * 32})


def test_event_log_requires_a_nonpublic_key(tmp_path) -> None:
    with pytest.raises(EventLogError):
        EventLog(tmp_path / "events.jsonl", env={})


def test_event_log_detects_valid_prefix_truncation(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    log = EventLog(path, run_id="r", env=EVENT_ENV)
    for object_id in ("a", "b", "c"):
        log.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=[object_id])

    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

    with pytest.raises(EventLogError):
        EventLog(path, run_id="r", env=EVENT_ENV)


def test_event_log_serializes_concurrent_writers(tmp_path) -> None:
    """Two stale handles must not both append sequence zero/genesis."""

    path = tmp_path / "events.jsonl"
    first = EventLog(path, run_id="r", env=EVENT_ENV)
    second = EventLog(path, run_id="r", env=EVENT_ENV)
    first.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=["a"])
    second.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=["b"])

    reopened = EventLog(path, run_id="r", env=EVENT_ENV)
    assert len(reopened) == 2
    assert reopened.verify_integrity()
    assert [event.sequence for event in reopened.events] == [0, 1]


def test_event_log_rejects_duplicate_json_record(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    log = EventLog(path, run_id="r", env=EVENT_ENV)
    log.append(action="PROBLEM_FROZEN", actor=ACTOR, object_ids=["a"])
    original = path.read_text(encoding="utf-8")
    path.write_text(original + original, encoding="utf-8")
    with pytest.raises(EventLogError):
        EventLog(path, run_id="r", env=EVENT_ENV)


@pytest.mark.parametrize("attack", ["delete_middle", "reorder", "forge_signature"])
def test_event_log_rejects_nontruncation_history_attacks(tmp_path, attack: str) -> None:
    path = tmp_path / "events.jsonl"
    log = EventLog(path, run_id="r", env=EVENT_ENV)
    for object_id in ("a", "b", "c"):
        log.append(action="HUMAN_INTERVENTION", actor=ACTOR, object_ids=[object_id])
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if attack == "delete_middle":
        del rows[1]
    elif attack == "reorder":
        rows[0], rows[1] = rows[1], rows[0]
    else:
        rows[1]["signature"] = "0" * 64
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")
    with pytest.raises(EventLogError):
        EventLog(path, run_id="r", env=EVENT_ENV)


def test_event_log_concurrent_threads_commit_one_ordered_history(tmp_path) -> None:
    path = tmp_path / "events.jsonl"

    def append(index: int) -> None:
        EventLog(path, run_id="r", env=EVENT_ENV).append(
            action="HUMAN_INTERVENTION", actor=ACTOR, object_ids=[str(index)]
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(append, range(32)))
    replayed = EventLog(path, run_id="r", env=EVENT_ENV)
    assert len(replayed) == 32
    assert replayed.verify_integrity()
    assert [event.sequence for event in replayed.events] == list(range(32))


def test_graph_rehydrates_semantic_state_from_authoritative_events(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    graph = _graph(path)
    expected_hash = graph.claims["c"].canonical_hash

    replayed = EpistemicGraph(EventLog(path, run_id="audit", env=EVENT_ENV))
    assert replayed.problems["p"].problem_id == "p"
    assert replayed.interpretations["i"].normalized_statement == "S"
    assert replayed.claims["c"].canonical_formula == "False"
    assert replayed.claims["c"].canonical_hash == expected_hash


def test_unsigned_self_reported_computation_cannot_promote_claim(tmp_path) -> None:
    graph = _graph(tmp_path / "events.jsonl")
    forged = Evidence(
        evidence_id="forged",
        claim_ids=["c"],
        kind=EvidenceKind.EXACT_COMPUTATION,
        replay_result="pass",
        generator_identity={
            "findings": {
                "classification": "exhaustive_finite",
                "exact_arithmetic": True,
                "coverage_statement": True,
                "result_verified": True,
            }
        },
    )

    EvidenceRouter(graph, evidence_env=EVIDENCE_ENV).admit(forged, actor=ACTOR)
    assert graph.claims["c"].truth_status is TruthStatus.UNKNOWN


def test_attested_evidence_is_claim_bound_and_tamper_evident(tmp_path) -> None:
    graph = _graph(tmp_path / "events.jsonl")
    claim_hash = graph.claims["c"].canonical_hash
    evidence = Evidence(
        evidence_id="checked",
        claim_ids=["c"],
        claim_bindings={"c": claim_hash},
        kind=EvidenceKind.EXACT_COMPUTATION,
        assertion_scope="complete finite domain",
        artifact_hashes=["a" * 64],
        replay_result="pass",
        replay_command="checker --artifact " + "a" * 64,
        environment_hash="b" * 64,
        verifier_identities=[{"id": "independent-replay", "attested": True}],
        generator_identity={
            "findings": {
                "classification": "exhaustive_finite",
                "exact_arithmetic": True,
                "coverage_statement": True,
                "result_verified": True,
            }
        },
    )
    attest_evidence(evidence, env=EVIDENCE_ENV)
    EvidenceRouter(graph, evidence_env=EVIDENCE_ENV).admit(evidence, actor=ACTOR)
    assert graph.claims["c"].truth_status is TruthStatus.SUPPORTED

    # A post-attestation metadata change invalidates the HMAC and downgrades the
    # claim on revalidation; a status field cannot preserve forged support.
    evidence.generator_identity["findings"]["coverage_statement"] = False
    EvidenceRouter(graph, evidence_env=EVIDENCE_ENV).revalidate("c", actor=ACTOR)
    assert graph.claims["c"].truth_status is TruthStatus.UNKNOWN


def test_attestation_does_not_substitute_for_artifact_semantics(tmp_path) -> None:
    graph = _graph(tmp_path / "events.jsonl")
    claim_hash = graph.claims["c"].canonical_hash
    metadata_only = Evidence(
        evidence_id="metadata-only",
        claim_ids=["c"],
        claim_bindings={"c": claim_hash},
        kind=EvidenceKind.EXACT_COMPUTATION,
        replay_result="pass",
        generator_identity={"findings": {
            "classification": "exhaustive_finite",
            "exact_arithmetic": True,
            "coverage_statement": True,
            "result_verified": True,
        }},
    )
    router = EvidenceRouter(graph, evidence_env=EVIDENCE_ENV)
    router.admit(attest_evidence(metadata_only, env=EVIDENCE_ENV), actor=ACTOR)
    assert graph.claims["c"].truth_status is TruthStatus.UNKNOWN

    false_result = Evidence(
        evidence_id="false-result",
        claim_ids=["c"],
        claim_bindings={"c": claim_hash},
        kind=EvidenceKind.EXACT_COMPUTATION,
        assertion_scope="finite domain",
        artifact_hashes=["a" * 64],
        replay_result="pass",
        replay_command="replay",
        environment_hash="b" * 64,
        verifier_identities=[{"id": "checker", "attested": True}],
        generator_identity={"findings": {
            "classification": "exhaustive_finite",
            "exact_arithmetic": True,
            "coverage_statement": True,
            "result_verified": False,
        }},
    )
    router.admit(attest_evidence(false_result, env=EVIDENCE_ENV), actor=ACTOR)
    assert graph.claims["c"].truth_status is TruthStatus.UNKNOWN


def test_forged_formal_correspondence_identifier_cannot_promote(tmp_path) -> None:
    graph = _graph(tmp_path / "events.jsonl")
    evidence = Evidence(
        evidence_id="fake-lean",
        claim_ids=["c"],
        claim_bindings={"c": graph.claims["c"].canonical_hash},
        kind=EvidenceKind.LEAN_PROOF,
        assertion_scope="locked theorem",
        artifact_hashes=["a" * 64],
        replay_result="pass",
        replay_command="lake build",
        environment_hash="b" * 64,
        verifier_identities=[{"id": "lean-kernel", "attested": True}],
        formal_correspondence_certificate_id="forged-fcc",
        generator_identity={"findings": {
            "verification_method": "local_lean_kernel",
            "kernel_verified": True,
            "has_placeholders": False,
            "axiom_whitelist_ok": True,
            "target_type_matches": True,
            "elaborated_type_hash": "c" * 64,
        }},
    )
    EvidenceRouter(graph, evidence_env=EVIDENCE_ENV).admit(
        attest_evidence(evidence, env=EVIDENCE_ENV), actor=ACTOR
    )
    assert graph.claims["c"].truth_status is TruthStatus.UNKNOWN


def test_signed_lean_booleans_with_real_correspondence_but_no_envelope_cannot_promote(
    tmp_path,
) -> None:
    graph = _graph(tmp_path / "events.jsonl")
    claim_hash = graph.claims["c"].canonical_hash
    graph.issue_intent_certificate(
        sign_intent_certificate(IntentCertificate(
            certificate_id="ic-real",
            source_bytes_hash="d" * 64,
            interpretation_hash="e" * 64,
            informal_claim_hash=claim_hash,
            methods=["independent_parse", "examples", "anti_examples", "paraphrase", "local_mutation"],
            reviewer_ids=["intent-reviewer"],
            reviewer_independence_and_conflicts=[{
                "reviewer_id": "intent-reviewer",
                "independent_from": ["governor", "intake_retrieval"],
                "conflicts": [],
            }],
            verdict=Verdict.APPROVED,
        ), env=LEAN_ENV),
        actor=ACTOR,
    )
    graph.issue_correspondence_certificate(
        sign_formal_correspondence_certificate(FormalCorrespondenceCertificate(
            certificate_id="fcc-real",
            intent_certificate_id="ic-real",
            informal_claim_hash=claim_hash,
            lean_declaration_name="target",
            elaborated_type_hash="f" * 64,
            notation_and_definition_map_hash="a" * 64,
            methods=["backtranslation", "examples", "anti_examples", "paraphrase", "local_mutation"],
            reviewer_ids=["formal-reviewer"],
            reviewer_independence_and_conflicts=[{
                "reviewer_id": "formal-reviewer",
                "independent_from": ["formalization_authority", "governor"],
                "conflicts": [],
            }],
            verdict=Verdict.APPROVED,
        ), env=LEAN_ENV),
        actor=ACTOR,
    )
    forged = Evidence(
        evidence_id="signed-booleans",
        claim_ids=["c"],
        claim_bindings={"c": claim_hash},
        kind=EvidenceKind.LEAN_PROOF,
        assertion_scope="locked theorem",
        artifact_hashes=["a" * 64],
        replay_result="pass",
        replay_command="lake build",
        environment_hash="b" * 64,
        verifier_identities=[{"id": "lean-kernel", "attested": True}],
        intent_certificate_id="ic-real",
        formal_correspondence_certificate_id="fcc-real",
        generator_identity={
            "source_hash": "c" * 64,
            "findings": {
                "verification_method": "local_lean_kernel",
                "kernel_verified": True,
                "has_placeholders": False,
                "axiom_whitelist_ok": True,
                "target_type_matches": True,
                "elaborated_type_hash": "f" * 64,
                "independent_checker": True,
            },
        },
    )
    EvidenceRouter(graph, evidence_env=EVIDENCE_ENV).admit(
        attest_evidence(forged, env=EVIDENCE_ENV), actor=ACTOR
    )
    assert graph.claims["c"].truth_status is TruthStatus.UNKNOWN
    assert graph.claims["c"].evidence_profile.formal_verification.name == "NONE"


def test_authenticated_formal_envelope_bound_to_graph_promotes_exact_claim(
    tmp_path, monkeypatch,
) -> None:
    graph = _graph(tmp_path / "events.jsonl")
    claim_hash = graph.claims["c"].canonical_hash
    source = "theorem target : False := by exact proof"
    source_hash = sha256_hex(source)
    type_hash = sha256_hex("False")
    proof_bundle_hash = sha256_hex("proof-bundle")
    executable = Path("/usr/bin/true")
    runner = AttestedKernelRunner(
        command=(str(executable),),
        checker_id="lean4checker",
        checker_version="pinned",
        checker_binary_hash=sha256_bytes(executable.read_bytes()),
        checker_trust_base="lean-kernel",
        env=LEAN_ENV,
    )

    def complete_checker(command, **kwargs):
        request = json.loads(kwargs["input"])
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({
                "kernel_verified": True,
                "candidate_type_hash": request["expected_type_hash"],
                "candidate_declaration_hash": sha256_hex("declaration"),
                "proof_term_hash": sha256_hex("proof-term"),
                "source_tree_hash": sha256_hex("tree"),
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

    monkeypatch.setattr("egmra.lean.service.subprocess.run", complete_checker)
    service = LeanService(kernel_runner=runner, checker_env=LEAN_ENV)
    environment = service.create_environment(
        lean_version="4.9.0", mathlib_commit="pinned", project_hash=sha256_hex("project")
    )
    certificate = service.verify_declaration(
        environment=environment,
        source=source,
        declaration_name="target",
        expected_type_hash=type_hash,
        immutable_target_module_hash=sha256_hex("target-module"),
        claim_bindings={"c": claim_hash},
        artifact_hashes=(proof_bundle_hash,),
    )
    assert certificate.verify(env=LEAN_ENV)

    graph.issue_intent_certificate(
        sign_intent_certificate(IntentCertificate(
            certificate_id="ic-envelope",
            source_bytes_hash=source_hash,
            interpretation_hash=sha256_hex("interpretation"),
            informal_claim_hash=claim_hash,
            methods=["independent_parse", "examples", "anti_examples", "paraphrase", "local_mutation"],
            reviewer_ids=["intent-reviewer"],
            reviewer_independence_and_conflicts=[{
                "reviewer_id": "intent-reviewer",
                "independent_from": ["governor", "intake_retrieval"],
                "conflicts": [],
            }],
            verdict=Verdict.APPROVED,
        ), env=LEAN_ENV),
        actor=ACTOR,
    )
    graph.issue_correspondence_certificate(
        sign_formal_correspondence_certificate(FormalCorrespondenceCertificate(
            certificate_id="fcc-envelope",
            intent_certificate_id="ic-envelope",
            informal_claim_hash=claim_hash,
            lean_declaration_name="target",
            elaborated_type_hash=type_hash,
            notation_and_definition_map_hash=sha256_hex("notation"),
            methods=["backtranslation", "examples", "anti_examples", "paraphrase", "local_mutation"],
            reviewer_ids=["formal-reviewer"],
            reviewer_independence_and_conflicts=[{
                "reviewer_id": "formal-reviewer",
                "independent_from": ["formalization_authority", "governor"],
                "conflicts": [],
            }],
            verdict=Verdict.APPROVED,
        ), env=LEAN_ENV),
        actor=ACTOR,
    )
    evidence = Evidence(
        evidence_id="formal-envelope",
        claim_ids=["c"],
        claim_bindings={"c": claim_hash},
        kind=EvidenceKind.LEAN_PROOF,
        assertion_scope="exact locked theorem",
        artifact_hashes=[certificate.certificate_digest, proof_bundle_hash],
        replay_result="pass",
        replay_command="attested-checker replay",
        environment_hash=environment.environment_id,
        verifier_identities=[{"id": certificate.checker_id, "attested": True}],
        intent_certificate_id="ic-envelope",
        formal_correspondence_certificate_id="fcc-envelope",
        generator_identity={
            "source_hash": source_hash,
            "formal_certificate": certificate.to_dict(),
        },
    )
    EvidenceRouter(
        graph, evidence_env=EVIDENCE_ENV, formal_env=LEAN_ENV
    ).admit(attest_evidence(evidence, env=EVIDENCE_ENV), actor=ACTOR)
    assert graph.claims["c"].truth_status is TruthStatus.SUPPORTED
    assert graph.claims["c"].evidence_profile.formal_verification.name == "KERNEL_CHECKED"


def test_false_computation_output_cannot_claim_exhaustive_success() -> None:
    service = ComputeService()
    spec = ExperimentSpec(
        purpose="audit false result", inputs={}, arithmetic_mode="exact", coverage="all cases"
    )
    code = "def experiment(inputs):\n    return {'result': False, 'coverage': 'all cases'}\n"
    job_id = service.submit_experiment(
        spec, code, claimed_classification="exhaustive_finite_subcase"
    )
    artifact = service.artifact(job_id)
    assert artifact.output["result"] is False
    assert artifact.effective_classification() == "heuristic_numerical"


def test_event_payload_mutation_is_detected(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    _graph(path)
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    claim_row = next(row for row in rows if row["action"] == "CLAIM_PROPOSED")
    claim_row["payload"]["claim"]["canonical_formula"] = "True"
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")
    with pytest.raises(EventLogError):
        EventLog(path, run_id="audit", env=EVENT_ENV)


def test_direct_status_mutation_without_router_capability_is_denied(tmp_path) -> None:
    graph = _graph(tmp_path / "events.jsonl")
    with pytest.raises(GraphError):
        graph.apply_validated_admission(
            claim_id="c",
            new_profile=EvidenceProfile(exact_computation=ExactComputation.SCOPED_EXACT),
            truth_status=TruthStatus.SUPPORTED,
            validator_id="forged",
            reason_code="forged",
            actor={"id": "attacker"},
        )
    assert graph.claims["c"].truth_status is TruthStatus.UNKNOWN


def test_failed_event_append_does_not_mutate_materialized_graph(tmp_path, monkeypatch) -> None:
    log = EventLog(tmp_path / "events.jsonl", run_id="r", env=EVENT_ENV)
    graph = EpistemicGraph(log)

    def fail_append(**_kwargs):
        raise EventLogError("injected disk failure")

    monkeypatch.setattr(log, "append", fail_append)
    with pytest.raises(EventLogError):
        graph.add_problem(Problem(problem_id="not-committed"), actor=ACTOR)
    assert "not-committed" not in graph.problems


def test_stale_graph_writer_cannot_commit_lost_update(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    _graph(path)
    first = EpistemicGraph(EventLog(path, run_id="audit", env=EVENT_ENV))
    stale = EpistemicGraph(EventLog(path, run_id="audit", env=EVENT_ENV))

    def signed(graph: EpistemicGraph, evidence_id: str) -> Evidence:
        evidence = Evidence(
            evidence_id=evidence_id,
            claim_ids=["c"],
            claim_bindings={"c": graph.claims["c"].canonical_hash},
            kind=EvidenceKind.EXACT_COMPUTATION,
            assertion_scope="finite domain",
            artifact_hashes=[(evidence_id[-1] * 64)[:64]],
            replay_result="pass",
            replay_command="replay",
            environment_hash="e" * 64,
            verifier_identities=[{"id": "checker", "attested": True}],
            generator_identity={"findings": {
                "classification": "exhaustive_finite",
                "exact_arithmetic": True,
                "coverage_statement": True,
                "result_verified": True,
            }},
        )
        return attest_evidence(evidence, env=EVIDENCE_ENV)

    EvidenceRouter(first, evidence_env=EVIDENCE_ENV).admit(signed(first, "ev_1"), actor=ACTOR)
    with pytest.raises(EventLogError):
        EvidenceRouter(stale, evidence_env=EVIDENCE_ENV).admit(signed(stale, "ev_2"), actor=ACTOR)

    replayed = EpistemicGraph(EventLog(path, run_id="audit", env=EVENT_ENV))
    assert replayed.claims["c"].status_version == 2
    assert replayed.claims["c"].truth_status is TruthStatus.SUPPORTED


def test_full_graph_revocation_and_branch_state_survive_restart(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    graph = _graph(path)
    graph.add_branch(
        Branch(branch_id="b", goal_claim_ids=["c"], interpretation_id="i"), actor=ACTOR
    )
    graph.set_branch_status("b", "paused", reason="awaiting verification", actor=ACTOR)
    evidence = Evidence(
        evidence_id="ev",
        claim_ids=["c"],
        claim_bindings={"c": graph.claims["c"].canonical_hash},
        kind=EvidenceKind.EXACT_COMPUTATION,
        assertion_scope="finite domain",
        artifact_hashes=["a" * 64],
        replay_result="pass",
        replay_command="replay",
        environment_hash="b" * 64,
        verifier_identities=[{"id": "checker", "attested": True}],
        generator_identity={"findings": {
            "classification": "exhaustive_finite",
            "exact_arithmetic": True,
            "coverage_statement": True,
            "result_verified": True,
        }},
    )
    router = EvidenceRouter(graph, evidence_env=EVIDENCE_ENV)
    router.admit(attest_evidence(evidence, env=EVIDENCE_ENV), actor=ACTOR)
    invalidate_evidence(graph, router, "ev", reason="audit replay failed", actor=ACTOR)

    replayed = EpistemicGraph(EventLog(path, run_id="audit", env=EVENT_ENV))
    assert replayed.materialized_view() == graph.materialized_view()
    assert replayed.claims["c"].truth_status is TruthStatus.UNKNOWN
    assert not replayed.evidence["ev"].valid
    assert replayed.branches["b"].status == "active"
