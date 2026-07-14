"""Adversarial Statement IR tests for semantic loss and false-success probes."""

from dataclasses import FrozenInstanceError

import pytest

from egmra.intake import GrammarParser, build_problem_contract, reconcile
from egmra.intake.statement_ir import ClauseParser, ModelParser, StatementIR
from egmra.provenance.hashing import sha256_bytes


def test_nested_quantifiers_preserve_each_binder_scope_and_kind():
    source = b"Prove that for every integer n there exists an integer m such that m > n."
    ir = GrammarParser().parse(source, "nested")
    assert [(b.name, b.domain, b.quantifier) for b in ir.binders] == [
        ("n", "ℤ", "universal"),
        ("m", "ℤ", "existential"),
    ]


def test_positive_domain_constraint_is_not_erased_or_tested_outside_scope():
    source = b"Prove that for every positive integer n, n > 0."
    contract = build_problem_contract(
        problem_id="positive",
        source_bytes=source,
        source_id="positive",
        predicate=lambda n: n > 0,
        boundary_points=(0, 1, 2),
        search_space=range(-4, 5),
    )
    binder = contract.primary_ir.binders[0]
    assert "positive" in binder.constraints
    assert not any("counterexample" in item for item in contract.unresolved_decisions)
    boundary = next(p for p in contract.probes if p.name == "boundary_enumeration")
    assert boundary.artifacts["tested_points"] == [1, 2]


def test_definition_and_constraint_text_are_semantically_bound():
    source = b"Let f(n) = n + 1. Prove that for all integers n with n >= 0, f(n) > n."
    ir = GrammarParser().parse(source, "definition")
    assert any(d.symbol == "f" and "n + 1" in d.semantics for d in ir.definitions)
    assert any("n >= 0" in constraint for constraint in ir.constraints)
    assert "definitions" in ir.semantic_key()
    assert "constraints" in ir.semantic_key()


def test_unexecuted_probes_are_unknown_and_block_release():
    source = b"Prove that for all integers n, n = n."
    contract = build_problem_contract(
        problem_id="no-executable-probe", source_bytes=source, source_id="source"
    )
    unexecuted = [p for p in contract.probes if not p.executed]
    assert unexecuted
    assert all(not p.passed for p in unexecuted)
    assert contract.release_blocked


def test_ir_source_hash_commits_exact_raw_bytes_and_invalid_utf8_is_rejected():
    source = b"  Prove that for all integers n, n = n.\n"
    ir = GrammarParser().parse(source, "raw")
    assert ir.source_hash == sha256_bytes(source)
    assert ir.source_spans == ({"start": 0, "end": len(source)},)
    with pytest.raises(ValueError, match="UTF-8"):
        GrammarParser().parse(b"\xff\xfe", "bad")


def test_statement_ir_is_immutable_after_identity_is_computed():
    ir = GrammarParser().parse(b"Prove that for all integers n, n = n.", "p")
    before = ir.semantic_hash()
    with pytest.raises(FrozenInstanceError):
        ir.conclusion = "False"
    with pytest.raises(AttributeError):
        ir.binders.append("forged")
    assert ir.semantic_hash() == before


def test_reconciliation_rejects_same_parser_family_with_forged_id():
    source = b"Prove that for all integers n, n = n."
    first = GrammarParser().parse(source, "p")
    forged = StatementIR(
        **{**first.to_dict(), "parser_id": "renamed", "parser_family": first.parser_family}
    )
    with pytest.raises(ValueError, match="independent parser families"):
        reconcile(first, forged)


@pytest.mark.parametrize(
    "result",
    [
        None,
        {"requested_outcome": "declare-victory", "conclusion": "x"},
        {"requested_outcome": "prove", "conclusion": "", "binders": "bad"},
    ],
)
def test_model_parser_rejects_malformed_or_semantically_invalid_results(result):
    parser = ModelParser("model-family-a", runner=lambda _: result)
    with pytest.raises((TypeError, ValueError)):
        parser.parse(b"Prove x.", "p")


def test_two_local_parser_families_still_reconcile_normally():
    source = b"Prove that for all integers n, n = n."
    first = GrammarParser().parse(source, "p")
    second = ClauseParser().parse(source, "p")
    assert first.parser_family != second.parser_family
    assert reconcile(first, second).agreed
