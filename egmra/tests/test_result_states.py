"""Tests for the honest result-state taxonomy."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from egmra.intake.probes import Probe
from egmra.orchestrator.result_states import ResultState, classify_result
from egmra.truth.entities import (
    Claim,
    EvidenceProfile,
    ExactComputation,
    ExternalImport,
    FormalVerification,
    InformalReview,
    NumericalEvidence,
    TruthStatus,
)


def _claim(status=TruthStatus.UNKNOWN, *, scope="general", profile=None, claim_id="goal",
           canonical_hash="goalhash"):
    return Claim(
        claim_id=claim_id,
        interpretation_id="i",
        canonical_formula="phi",
        canonical_hash=canonical_hash,
        truth_status=status,
        scope=scope,
        evidence_profile=profile or EvidenceProfile(),
    )


def _probe(name, kind, *, passed, executed=True):
    return Probe(name=name, kind=kind, passed=passed, detail=f"{name} detail", executed=executed)


def _release_cert(*, claim_id="goal", claim_hash="goalhash", contract_hash="ch",
                  verifies=True):
    return SimpleNamespace(
        result_claim_id=claim_id,
        result_claim_hash=claim_hash,
        problem_contract_hash=contract_hash,
        verify=lambda **_k: verifies,
    )


def _valid_formal_gates():
    return SimpleNamespace(
        truth="T5", formal_correspondence="F2",
        formal_correspondence_certificate_id="fcc-1",
    )


def _result(
    *,
    claims=None,
    probes=(),
    lattice_blocked=False,
    unresolved=(),
    outcome="honest_triage_report",
    certificate=None,
    compiled_proof=None,
    promotion=None,
    gates=None,
    contract_hash=None,
):
    lattice = SimpleNamespace(release_blocked=lattice_blocked)
    contract = SimpleNamespace(
        probes=list(probes), lattice=lattice, unresolved_decisions=list(unresolved)
    )
    if contract_hash is not None:
        contract.contract_hash = lambda: contract_hash
    graph = SimpleNamespace(claims=claims or {}, log=None)
    return SimpleNamespace(
        contract=contract, graph=graph, outcome=outcome,
        certificate=certificate, compiled_proof=compiled_proof, promotion=promotion,
        gates=gates, verified_debt={},
    )


def _promoted_release(*, claim_id="goal", claim_hash="goalhash", contract_hash="ch",
                      verifies=True):
    """A minimal but internally consistent promoted-release trio for the classifier."""
    return {
        "certificate": _release_cert(claim_id=claim_id, claim_hash=claim_hash,
                                     contract_hash=contract_hash, verifies=verifies),
        "promotion": SimpleNamespace(promoted=True),
        "compiled_proof": SimpleNamespace(complete=True, goal_claim_id=claim_id),
        "contract_hash": contract_hash,
    }


def test_open_no_progress_when_attempted_without_evidence():
    result = _result(claims={"goal": _claim(TruthStatus.UNKNOWN)})
    assert classify_result(result).state is ResultState.OPEN_NO_PROGRESS


def test_blocked_by_interpretation_on_parser_disagreement():
    result = _result(claims={"goal": _claim()}, lattice_blocked=True)
    classification = classify_result(result)
    assert classification.state is ResultState.BLOCKED_BY_INTERPRETATION
    assert "parsers disagree" in classification.rationale


def test_blocked_by_interpretation_on_executed_integrity_probe_failure():
    probes = [_probe("dimensional_type", "dimensional", passed=False, executed=True)]
    result = _result(claims={"goal": _claim()}, probes=probes)
    assert classify_result(result).state is ResultState.BLOCKED_BY_INTERPRETATION


def test_not_executed_probe_does_not_block_interpretation():
    # A probe that could not run (no applicable rule / no predicate) must not be
    # read as an ambiguity; the honest state is still OPEN_NO_PROGRESS.
    probes = [
        _probe("counterexample_search", "counterexample", passed=False, executed=False),
        _probe("boundary_enumeration", "boundary", passed=False, executed=False),
    ]
    result = _result(claims={"goal": _claim()}, probes=probes)
    assert classify_result(result).state is ResultState.OPEN_NO_PROGRESS


def test_candidate_disproof_on_executed_counterexample():
    probes = [_probe("counterexample_search", "counterexample", passed=False, executed=True)]
    result = _result(claims={"goal": _claim(TruthStatus.UNKNOWN)}, probes=probes)
    assert classify_result(result).state is ResultState.CANDIDATE_DISPROOF


def test_candidate_disproof_on_refuted_goal():
    result = _result(claims={"goal": _claim(TruthStatus.REFUTED)})
    assert classify_result(result).state is ResultState.CANDIDATE_DISPROOF


def test_computational_evidence_for_finite_exact_support():
    profile = EvidenceProfile(exact_computation=ExactComputation.SCOPED_EXACT)
    result = _result(
        claims={"goal": _claim(TruthStatus.SUPPORTED, scope="finite_domain", profile=profile)},
        outcome="verified_finite_or_conditional_result",
    )
    assert classify_result(result).state is ResultState.COMPUTATIONAL_EVIDENCE


def test_numerical_reproducible_support_is_computational_evidence():
    profile = EvidenceProfile(numerical=NumericalEvidence.REPRODUCIBLE)
    result = _result(claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)})
    assert classify_result(result).state is ResultState.COMPUTATIONAL_EVIDENCE


def test_conditional_result_takes_precedence_over_computation():
    profile = EvidenceProfile(exact_computation=ExactComputation.SCOPED_EXACT)
    result = _result(
        claims={"goal": _claim(TruthStatus.SUPPORTED, scope="conditional", profile=profile)}
    )
    assert classify_result(result).state is ResultState.CONDITIONAL_RESULT


def test_candidate_proof_requires_argued_review():
    profile = EvidenceProfile(informal_review=InformalReview.DOUBLE_INDEPENDENT)
    result = _result(claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)})
    assert classify_result(result).state is ResultState.CANDIDATE_PROOF


def test_formally_verified_candidate_requires_claim_bound_certificate():
    profile = EvidenceProfile(
        exact_computation=ExactComputation.SCOPED_EXACT,
        formal_verification=FormalVerification.KERNEL_CHECKED,
    )
    result = _result(
        claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)},
        gates=_valid_formal_gates(),
    )
    assert classify_result(result).state is ResultState.FORMALLY_VERIFIED_CANDIDATE


def test_formal_flag_without_gate_artifact_is_not_formally_verified():
    # A bare evidence-profile flag with no T4/T5+F2 gate certificate is NOT formal.
    profile = EvidenceProfile(
        exact_computation=ExactComputation.SCOPED_EXACT,
        formal_verification=FormalVerification.KERNEL_CHECKED,
    )
    result = _result(claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)})
    assert classify_result(result).state is ResultState.COMPUTATIONAL_EVIDENCE


def test_blocked_interpretation_dominates_formal_evidence():
    # Adversarial (spec §4A): blocked interpretation + fake formal evidence.
    profile = EvidenceProfile(formal_verification=FormalVerification.INDEPENDENT_CHECKER)
    result = _result(
        claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)},
        gates=_valid_formal_gates(),
        lattice_blocked=True,
    )
    assert classify_result(result).state is ResultState.BLOCKED_BY_INTERPRETATION


def test_blocked_interpretation_dominates_external_evidence():
    # Adversarial: blocked interpretation + external corroboration + a release.
    profile = EvidenceProfile(external_import=ExternalImport.INDEPENDENTLY_CORROBORATED)
    result = _result(
        claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)},
        lattice_blocked=True,
        **_promoted_release(),
    )
    assert classify_result(result).state is ResultState.BLOCKED_BY_INTERPRETATION


def test_externally_validated_solution_requires_valid_release():
    profile = EvidenceProfile(
        formal_verification=FormalVerification.KERNEL_CHECKED,
        external_import=ExternalImport.INDEPENDENTLY_CORROBORATED,
    )
    result = _result(
        claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)},
        gates=_valid_formal_gates(),
        **_promoted_release(),
    )
    assert classify_result(result).state is ResultState.EXTERNALLY_VALIDATED_SOLUTION


def test_external_profile_without_release_is_not_validated():
    # Adversarial: external profile but NO release artifact -> never validated.
    profile = EvidenceProfile(external_import=ExternalImport.INDEPENDENTLY_CORROBORATED)
    result = _result(claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)})
    state = classify_result(result).state
    assert state is not ResultState.EXTERNALLY_VALIDATED_SOLUTION
    assert state in {ResultState.PARTIAL_PROGRESS, ResultState.COMPUTATIONAL_EVIDENCE}


def test_externally_validated_disproof_requires_valid_release():
    profile = EvidenceProfile(external_import=ExternalImport.INDEPENDENTLY_CORROBORATED)
    result = _result(
        claims={"goal": _claim(TruthStatus.REFUTED, profile=profile)},
        **_promoted_release(),
    )
    assert classify_result(result).state is ResultState.EXTERNALLY_VALIDATED_DISPROOF


def test_release_bound_to_wrong_claim_id_is_rejected():
    # Adversarial: proof attached to the wrong claim id.
    profile = EvidenceProfile(external_import=ExternalImport.INDEPENDENTLY_CORROBORATED)
    release = _promoted_release(claim_id="other-claim")
    result = _result(
        claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)}, **release
    )
    assert classify_result(result).state is not ResultState.EXTERNALLY_VALIDATED_SOLUTION


def test_release_for_strengthened_statement_is_rejected():
    # Adversarial: a certificate whose claim hash names a different (e.g.
    # strengthened/weakened) statement must not validate the original goal.
    profile = EvidenceProfile(external_import=ExternalImport.INDEPENDENTLY_CORROBORATED)
    release = _promoted_release(claim_hash="a-different-normalized-target")
    result = _result(
        claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)}, **release
    )
    assert classify_result(result).state is not ResultState.EXTERNALLY_VALIDATED_SOLUTION


def test_release_with_mismatched_contract_hash_is_rejected():
    profile = EvidenceProfile(external_import=ExternalImport.INDEPENDENTLY_CORROBORATED)
    release = _promoted_release(contract_hash="cert-contract")
    release["contract_hash"] = "actual-different-contract"
    result = _result(
        claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)}, **release
    )
    assert classify_result(result).state is not ResultState.EXTERNALLY_VALIDATED_SOLUTION


def test_stale_or_revoked_certificate_fails_closed():
    # Adversarial: a certificate whose signature/freshness verification fails.
    profile = EvidenceProfile(external_import=ExternalImport.INDEPENDENTLY_CORROBORATED)
    release = _promoted_release(verifies=False)
    result = _result(
        claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)}, **release
    )
    assert classify_result(result).state is not ResultState.EXTERNALLY_VALIDATED_SOLUTION


def test_unpromoted_release_is_not_externally_validated():
    profile = EvidenceProfile(external_import=ExternalImport.INDEPENDENTLY_CORROBORATED)
    release = _promoted_release()
    release["promotion"] = SimpleNamespace(promoted=False)
    result = _result(
        claims={"goal": _claim(TruthStatus.SUPPORTED, profile=profile)}, **release
    )
    assert classify_result(result).state is not ResultState.EXTERNALLY_VALIDATED_SOLUTION


def test_partial_progress_when_subclaims_supported_but_goal_open():
    claims = {
        "goal": _claim(TruthStatus.UNKNOWN),
        "lemma": _claim(TruthStatus.SUPPORTED, claim_id="lemma"),
    }
    result = _result(claims=claims)
    assert classify_result(result).state is ResultState.PARTIAL_PROGRESS


def test_to_dict_exposes_state_and_signals():
    result = _result(claims={"goal": _claim(TruthStatus.UNKNOWN)})
    payload = classify_result(result).to_dict()
    assert payload["state"] == "OPEN_NO_PROGRESS"
    assert "rationale" in payload and isinstance(payload["signals"], dict)


@pytest.mark.parametrize("state", list(ResultState))
def test_every_state_has_string_value(state):
    assert isinstance(state.value, str) and state.value == str(state)
