"""Live-run scaffolding: the operator ``run --predicate`` flag and the
``sign-review`` CLI.

These close the two gaps that kept a genuine scenario-4 (formally-verified
candidate) run from being *reachable* on the arbitrary/browser path:

* the arbitrary path had no executable countermodel predicate, so the referee's
  ``countermodel_search`` attack could never pass live; and
* there was no CLI to produce the independently signed intent- and
  formal-correspondence-review artifacts the orchestrator requires.

The predicate is a safe, AST-restricted bounded expression (not arbitrary code),
and ``sign-review`` signs with the review keys — it records a genuine reviewer's
verdict, it does not manufacture independence.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import egmra.cli as cli_module
from egmra.cli import main
from egmra.corpus import from_statement
from egmra.intake import build_problem_contract
from egmra.intake.predicate import PredicateError, compile_bounded_predicate
from egmra.intake.review import interpretation_review_hash, verify_intent_certificate
from egmra.lean.correspondence import verify_formal_correspondence_certificate
from egmra.lean.kernel_checker import expected_type_hash
from egmra.provenance.hashing import sha256_hex
from egmra.policy import sign_policy
from egmra.truth.entities import Verdict


def _policy_file(tmp_path) -> Path:
    policy = sign_policy({
        "claim_graph": True, "literature_retrieval": True, "computation_service": True,
        "promotion": False, "formal_promotion": False,
    })
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(policy.to_document()))
    return path


# ── safe bounded predicate compiler ─────────────────────────────────────────────

def test_compile_bounded_predicate_evaluates_numeric_expression():
    predicate = compile_bounded_predicate("n*n >= 0")
    assert all(predicate(n) for n in range(-4, 64))


def test_compile_bounded_predicate_body_can_reference_the_variable():
    # Comprehension-nested scopes must still see ``n`` (globals-based binding).
    predicate = compile_bounded_predicate("all(k >= n for k in range(n, n + 3))")
    assert predicate(7) is True
    assert predicate(0) is True


def test_compile_bounded_predicate_detects_a_counterexample():
    predicate = compile_bounded_predicate("n < 5")
    assert any(not predicate(n) for n in range(64))


@pytest.mark.parametrize("expression", [
    "__import__('os').system('echo x')",
    "().__class__.__bases__",
    "n.__class__",
    "open('x')",
    "lambda: 1",
    "n[0]",
    "'a string'",
    "sorted([n])",
    "n if n else no_such_name",
    "",
    "   ",
])
def test_compile_bounded_predicate_rejects_unsafe_or_malformed(expression):
    with pytest.raises(PredicateError):
        compile_bounded_predicate(expression)


def test_compile_bounded_predicate_rejects_oversized_expression():
    with pytest.raises(PredicateError):
        compile_bounded_predicate("n >= 0 and " * 400 + "n >= 0")


# ── the predicate makes the arbitrary path's countermodel search executable ─────

def test_predicate_makes_counterexample_probe_executable_and_passing():
    # This is the exact precondition the referee's ``countermodel_search`` attack
    # requires: an executable counterexample search that passed.
    contract = build_problem_contract(
        problem_id="p", source_bytes=b"For all n, n^2 >= 0.", source_id="p",
        predicate=compile_bounded_predicate("n*n >= 0"),
    )
    probe = next(p for p in contract.probes if p.name == "counterexample_search")
    assert probe.passed is True
    assert probe.artifacts["executable"] is True


def test_without_predicate_counterexample_probe_is_not_executable():
    contract = build_problem_contract(
        problem_id="p", source_bytes=b"For all n, n^2 >= 0.", source_id="p",
    )
    probe = next(p for p in contract.probes if p.name == "counterexample_search")
    assert probe.passed is False
    assert probe.artifacts["executable"] is False


# ── run --predicate CLI wiring ──────────────────────────────────────────────────

def test_cli_run_predicate_is_wired_into_the_arbitrary_path(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs"),
                               "oeis_cache_dir": str(tmp_path / "oeis")}))
    rc = main(["--config", str(cfg), "run", "--provider", "deterministic",
               "--policy", str(_policy_file(tmp_path)), "--statement",
               "For every natural number n, n squared is at least zero.",
               "--predicate", "n*n >= 0", "--retrieval", "none", "--oeis", "offline"])
    assert rc == 0


def test_cli_run_rejects_an_unsafe_predicate_before_running(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    rc = main(["--config", str(cfg), "run", "--provider", "deterministic",
               "--policy", str(_policy_file(tmp_path)), "--statement", "x",
               "--predicate", "__import__('os')", "--retrieval", "none", "--oeis", "offline"])
    assert rc == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error"] == "PredicateError"


# ── sign-review intent ──────────────────────────────────────────────────────────

def test_sign_review_intent_binds_the_problem_and_verifies(tmp_path, capsys):
    text = "For every natural number n, n squared is at least zero."
    out = tmp_path / "intent.json"
    rc = main(["sign-review", "intent", "--statement", text,
               "--reviewer-id", "rev-a", "-o", str(out)])
    assert rc == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["verdict"] == "APPROVED"
    assert "self-review" in printed["note"]
    # 0600, never group/world readable.
    assert (out.stat().st_mode & 0o777) == 0o600

    cert = cli_module._load_intent_review(out)
    assert verify_intent_certificate(cert)
    assert cert.verdict is Verdict.APPROVED

    # The artifact binds a contract rebuilt exactly as the orchestrator would.
    problem = from_statement(text)
    contract = build_problem_contract(
        problem_id=problem.problem_id, source_bytes=problem.source_bytes,
        source_id=problem.source_id)
    interp = contract.lattice.nodes[0]
    assert cert.source_bytes_hash == contract.source_bytes_hash
    assert cert.interpretation_hash == interpretation_review_hash(interp)
    assert cert.informal_claim_hash == sha256_hex(interp.conclusion)
    assert {"independent_parse", "examples", "anti_examples", "paraphrase",
            "local_mutation"}.issubset(set(cert.methods))


def test_sign_review_intent_refuses_to_overwrite(tmp_path):
    text = "For every natural number n, n squared is at least zero."
    out = tmp_path / "intent.json"
    assert main(["sign-review", "intent", "--statement", text, "-o", str(out)]) == 0
    rc = main(["sign-review", "intent", "--statement", text, "-o", str(out)])
    assert rc == 2  # FileExistsError -> OSError -> handled


def test_sign_review_intent_can_sign_a_rejection(tmp_path, capsys):
    out = tmp_path / "intent.json"
    rc = main(["sign-review", "intent", "--statement", "A dubious claim.",
               "--verdict", "rejected", "-o", str(out)])
    assert rc == 0
    cert = cli_module._load_intent_review(out)
    assert cert.verdict is Verdict.REJECTED
    assert verify_intent_certificate(cert)


# ── sign-review correspondence ──────────────────────────────────────────────────

def _sign_intent(tmp_path, text: str) -> Path:
    out = tmp_path / "intent.json"
    assert main(["sign-review", "intent", "--statement", text, "-o", str(out)]) == 0
    return out


def test_sign_review_correspondence_binds_intent_declaration_and_type(tmp_path, capsys):
    text = "For every natural number n, n squared is at least zero."
    intent_path = _sign_intent(tmp_path, text)
    intent = cli_module._load_intent_review(intent_path)

    corr = tmp_path / "correspondence.json"
    rc = main(["sign-review", "correspondence", "--intent-review", str(intent_path),
               "--declaration", "egmra_demo", "--expected-type", "2 + 2 = 4",
               "-o", str(corr)])
    assert rc == 0
    assert (corr.stat().st_mode & 0o777) == 0o600

    reviews = cli_module._load_formal_correspondence_reviews([str(corr)])
    assert set(reviews) == {"goal"}
    cert = reviews["goal"]
    assert verify_formal_correspondence_certificate(cert)
    assert cert.verdict is Verdict.APPROVED
    # These are the exact bindings the orchestrator's correspondence check enforces.
    assert cert.intent_certificate_id == intent.certificate_id
    assert cert.informal_claim_hash == intent.informal_claim_hash
    assert cert.lean_declaration_name == "egmra_demo"
    assert cert.elaborated_type_hash == expected_type_hash("2 + 2 = 4")


def test_sign_review_correspondence_requires_an_intent_review(tmp_path):
    missing = tmp_path / "nope.json"
    rc = main(["sign-review", "correspondence", "--intent-review", str(missing),
               "--declaration", "d", "--expected-type", "2 + 2 = 4",
               "-o", str(tmp_path / "c.json")])
    assert rc == 2


# ── end-to-end: CLI-signed artifacts + predicate admit a kernel-checked proof ───

def test_cli_signed_reviews_reach_a_kernel_checked_formal_proof(tmp_path):
    # The whole point of the scaffolding: artifacts produced ONLY through the
    # sign-review CLI (with CLI-computed hashes) bind a real research run, and the
    # operator predicate makes the intake probes pass — so the kernel-verified Lean
    # declaration is admitted as a formal proof of the informal claim.
    from egmra.lean.service import LeanService
    from egmra.orchestrator import RunnerWorker, research
    from egmra.truth.entities import EvidenceKind
    from egmra.tests.test_production_wiring import (
        _FormalRunner, _corpus, _enforcer, _fake_attested_checker_runner, _status,
    )

    text = "Prove that for all natural numbers n, n squared is at least 0."
    problem = from_statement(text)

    intent_path = tmp_path / "intent.json"
    assert main(["sign-review", "intent", "--statement", text,
                 "-o", str(intent_path)]) == 0
    corr_path = tmp_path / "correspondence.json"
    assert main(["sign-review", "correspondence", "--intent-review", str(intent_path),
                 "--declaration", "egmra_demo", "--expected-type", "2 + 2 = 4",
                 "-o", str(corr_path)]) == 0

    intent = cli_module._load_intent_review(intent_path)
    reviews = cli_module._load_formal_correspondence_reviews([str(corr_path)])

    result = research(
        problem_id=problem.problem_id, source_bytes=problem.source_bytes,
        source_id=problem.source_id, budget=100.0, enforcer=_enforcer(),
        goal_claim_id="goal",
        worker=RunnerWorker(runner=_FormalRunner(), goal_claim_id="goal",
                            goal_formula=problem.display_statement, lean_version="4.28.0",
                            mathlib_commit="v4.28.0"),
        events_path=tmp_path / "e.jsonl", retrieval_corpus=_corpus(),
        runner=_FormalRunner(),
        lean_service=LeanService(kernel_runner=_fake_attested_checker_runner(tmp_path)),
        probe_predicate=compile_bounded_predicate("n*n >= 0"),
        status_claims=_status(problem.problem_id), informal_only=False,
        intent_review=intent, formal_correspondence_reviews=reviews)

    # The CLI intent bound (interpretation approved) and the CLI correspondence
    # discharged the formal-correspondence requirement.
    assert "intent_review_rejected" not in result.failures
    assert "intent_review_unavailable" not in result.failures
    assert not any("formal_correspondence_required" in f for f in result.failures)
    lean_evidence = [e for e in result.graph.evidence.values()
                     if e.kind is EvidenceKind.LEAN_PROOF]
    assert len(lean_evidence) == 1
    assert lean_evidence[0].formal_correspondence_certificate_id \
        == "formal-correspondence-egmra_demo"
    assert lean_evidence[0].intent_certificate_id == intent.certificate_id
    assert result.graph.claims["goal"].truth_status.value == "SUPPORTED"
