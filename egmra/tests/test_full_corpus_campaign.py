"""Realistic full-corpus campaigning: certified readings, fresh attempts,
provider-outage backoff, growth-only campaign merge, and intent derivation.

These pin the fixes for three observed production failure modes:

* problems with a binding intent certificate still labeled
  BLOCKED_BY_INTERPRETATION by a deterministic parser-integrity probe;
* later attempts silently re-booking prior budget/branches into zero-work
  "completed" runs;
* a globally down provider churning the queue and exhausting every problem's
  infrastructure budget without one mathematical attempt.
"""

from __future__ import annotations

import threading
from types import SimpleNamespace

import pytest

from egmra.intake import build_problem_contract
from egmra.intake.probes import Probe
from egmra.intake.review import interpretation_review_hash, sign_intent_certificate
from egmra.orchestrator.campaign import Campaign, CampaignError
from egmra.orchestrator.result_states import ResultState, classify_result
from egmra.provenance.hashing import sha256_hex
from egmra.truth.entities import (
    Claim,
    EvidenceProfile,
    IntentCertificate,
    TruthStatus,
    Verdict,
)

STATEMENT = b"Prove that for all natural numbers n, n squared is at least 0."
OTHER_STATEMENT = b"Prove that for all natural numbers n, n cubed is at least 0."


# ── certified reading vs interpretation-integrity probes ────────────────────

def _approved_contract(source_bytes: bytes = STATEMENT):
    contract = build_problem_contract(
        problem_id="p1", source_bytes=source_bytes, source_id="s1")
    for ambiguity in list(contract.lattice.open_ambiguities):
        contract.lattice.resolve_ambiguity(ambiguity)
    contract.lattice.approve(contract.lattice.nodes[0].interpretation_id)
    return contract


def _intent_certificate(contract):
    interp = contract.lattice.nodes[0]
    return sign_intent_certificate(IntentCertificate(
        certificate_id="intent-p1",
        source_bytes_hash=contract.source_bytes_hash,
        interpretation_hash=interpretation_review_hash(interp),
        informal_claim_hash=sha256_hex(interp.conclusion),
        methods=["independent_parse", "examples", "anti_examples",
                 "paraphrase", "local_mutation"],
        reviewer_ids=["reviewer"],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "reviewer",
            "independent_from": ["governor", "intake_retrieval"],
            "conflicts": [],
        }],
        verdict=Verdict.APPROVED,
    ))


def _failed_dimensional_probe():
    return Probe("dimensional_type", "dimensional", False,
                 "binders without a domain and no regime", executed=True)


def _result(contract, *, certificate=None, malformed=False, extra_probe=None):
    probes = list(contract.probes)
    if extra_probe is not None:
        probes.append(extra_probe)
    unresolved = ["malformed:forced"] if malformed else []
    shim = SimpleNamespace(
        probes=probes, lattice=contract.lattice,
        unresolved_decisions=unresolved,
        source_bytes_hash=contract.source_bytes_hash)
    claims = {"goal": Claim(
        claim_id="goal", interpretation_id="i", canonical_formula="phi",
        canonical_hash="h", truth_status=TruthStatus.UNKNOWN,
        scope="general", evidence_profile=EvidenceProfile())}
    certificates = ({certificate.certificate_id: certificate}
                    if certificate is not None else {})
    graph = SimpleNamespace(claims=claims, log=None,
                            intent_certificates=certificates)
    return SimpleNamespace(
        contract=shim, graph=graph, outcome="honest_triage_report",
        certificate=None, compiled_proof=None, promotion=None,
        gates=None, verified_debt={})


def test_integrity_probe_blocks_without_a_certificate():
    contract = _approved_contract()
    result = _result(contract, extra_probe=_failed_dimensional_probe())
    classification = classify_result(result)
    assert classification.state is ResultState.BLOCKED_BY_INTERPRETATION
    assert classification.signals[
        "interpretation_probe_lifted_by_intent_certificate"] is False


def test_binding_certificate_lifts_integrity_probe_to_open_no_progress():
    contract = _approved_contract()
    result = _result(contract, certificate=_intent_certificate(contract),
                     extra_probe=_failed_dimensional_probe())
    classification = classify_result(result)
    assert classification.state is ResultState.OPEN_NO_PROGRESS
    assert classification.signals[
        "interpretation_probe_lifted_by_intent_certificate"] is True


def test_certificate_for_a_different_statement_never_lifts():
    contract = _approved_contract()
    wrong = _intent_certificate(_approved_contract(OTHER_STATEMENT))
    result = _result(contract, certificate=wrong,
                     extra_probe=_failed_dimensional_probe())
    assert classify_result(result).state is ResultState.BLOCKED_BY_INTERPRETATION


def test_malformed_statement_stays_blocked_even_with_certificate():
    contract = _approved_contract()
    result = _result(contract, certificate=_intent_certificate(contract),
                     malformed=True, extra_probe=_failed_dimensional_probe())
    assert classify_result(result).state is ResultState.BLOCKED_BY_INTERPRETATION


# ── growth-only campaign merge ───────────────────────────────────────────────

def _campaign(tmp_path, workers=("w0",), **kw):
    return Campaign(tmp_path / "campaign.json", worker_ids=workers, **kw)


def test_initialize_grows_the_problem_set_without_touching_existing(tmp_path):
    c = _campaign(tmp_path)
    assert c.initialize("camp", ["p1", "p2"]) == ["p1", "p2"]
    lease = c.lease("w0", now=1000.0)
    c.complete(lease.problem_id, "w0", lease.fencing_token,
               result_state="OPEN_NO_PROGRESS")
    order = c.initialize("camp", ["p1", "p2", "p3", "p4"])
    assert order == ["p1", "p2", "p3", "p4"]
    status = c.status()
    assert status["total"] == 4
    assert status["workers"]["p1"]["status"] == "done"
    assert status["workers"]["p3"]["status"] == "pending"
    # A smaller launch list resumes without dropping anything.
    assert c.initialize("camp", ["p2"]) == ["p1", "p2", "p3", "p4"]
    with pytest.raises(CampaignError, match="different campaign"):
        c.initialize("other-campaign", ["p1", "p2"])


# ── infra-only requeue ───────────────────────────────────────────────────────

def test_requeue_failed_infra_only_skips_genuine_failures(tmp_path):
    c = _campaign(tmp_path, max_infra_retries=1)
    c.initialize("camp", ["p1", "p2"])
    first = c.lease("w0", now=1000.0)
    c.retain(first.problem_id, "w0", first.fencing_token)   # infra exhausted
    second = c.lease("w0", now=1001.0)
    c.fail(second.problem_id, "w0", second.fencing_token,
           reason="SourceResolutionError: missing", permanent=True)
    status = c.status()["workers"]
    assert status["p1"]["result_state"].startswith("infrastructure_budget_exhausted")
    assert c.requeue_failed(infra_only=True) == ["p1"]
    status = c.status()["workers"]
    assert status["p1"]["status"] == "pending"
    assert status["p2"]["status"] == "failed"


# ── provider-outage backoff ──────────────────────────────────────────────────

class _Outage(Exception):
    pass


def test_consecutive_provider_outages_pause_instead_of_churning(tmp_path):
    c = _campaign(tmp_path)
    c.initialize("camp", ["p1", "p2"])
    sleeps: list[float] = []
    calls = {"n": 0}

    def runner(problem_id, token, worker_id):
        calls["n"] += 1
        if calls["n"] <= 3:
            raise _Outage()
        return "OPEN_NO_PROGRESS"

    status = c.run_concurrent(
        runner, max_workers=1, now=lambda: 1000.0,
        provider_unavailable=_Outage,
        outage_backoff=lambda consecutive: float(consecutive),
        sleep=sleeps.append,
    )
    # Three consecutive outages back off 1s, 2s, 3s; recovery completes both.
    assert sleeps == [1.0, 2.0, 3.0]
    assert status["by_status"] == {"done": 2}
    assert all(row["infra_retries"] <= 3 for row in status["workers"].values())


def test_outage_counter_resets_after_a_successful_run(tmp_path):
    c = _campaign(tmp_path)
    c.initialize("camp", ["p1", "p2", "p3"])
    sleeps: list[float] = []
    script = iter(["outage", "ok", "outage", "ok", "ok"])

    def runner(problem_id, token, worker_id):
        if next(script) == "outage":
            raise _Outage()
        return "OPEN_NO_PROGRESS"

    c.run_concurrent(
        runner, max_workers=1, now=lambda: 1000.0,
        provider_unavailable=_Outage,
        outage_backoff=lambda consecutive: float(consecutive),
        sleep=sleeps.append,
    )
    assert sleeps == [1.0, 1.0]   # the success in between reset the counter


def test_stop_request_interrupts_an_outage_pause(tmp_path):
    c = _campaign(tmp_path)
    c.initialize("camp", ["p1"])
    stop = threading.Event()
    sleeps: list[float] = []

    def runner(problem_id, token, worker_id):
        stop.set()
        raise _Outage()

    status = c.run_concurrent(
        runner, max_workers=1, now=lambda: 1000.0,
        provider_unavailable=_Outage,
        outage_backoff=lambda consecutive: 600.0,
        sleep=sleeps.append,
        stop_requested=stop.is_set,
    )
    assert sleeps == []            # the pause saw the stop request immediately
    assert status["stop_requested"] is True


# ── launch-time intent derivation ────────────────────────────────────────────

def test_derive_missing_intents_signs_only_absent_certificates(tmp_path):
    from egmra.cli import _derive_missing_intent_certificates

    derived = _derive_missing_intent_certificates(
        ["erdos-312"], reviews_dir=tmp_path)
    assert [row["problem_id"] for row in derived] == ["erdos-312"]
    assert "certificate" in derived[0]
    assert (tmp_path / "intent-erdos-312.json").is_file()
    assert (tmp_path / "evidence-intent-erdos-312.json").is_file()
    # Existing certificates are never re-derived; bad ids are recorded, not fatal.
    again = _derive_missing_intent_certificates(
        ["erdos-312", "erdos-999999"], reviews_dir=tmp_path)
    assert [row["problem_id"] for row in again] == ["erdos-999999"]
    assert "error" in again[0]
