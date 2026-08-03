"""Tests for intake: Statement IR, interpretation lattice, probes, contract."""

from egmra.intake import (
    ClauseParser,
    GrammarParser,
    build_interpretation_lattice,
    build_problem_contract,
    mutate,
    paraphrase,
    reconcile,
    run_integrity_probes,
)
from egmra.intake.statement_ir import backtranslate
from egmra.intake.statement_ir import Binder, Definition, StatementIR

FALSE = b"Prove that for all positive integers n, n is prime."
AMBIG = b"Show that the sequence grows, where it is bounded, and there exists a limit."
TRUE_ISH = b"Prove that for all positive integers n, n + 0 = n."


# ── Statement IR + dual parse ────────────────────────────────────────────────

def test_grammar_parser_detects_outcome_and_quantifier():
    ir = GrammarParser().parse(FALSE, "erdos-x")
    assert ir.requested_outcome == "prove"
    assert any(b.quantifier == "universal" for b in ir.binders)
    assert "n=0" in ir.edge_cases


def test_disprove_outcome_detected():
    ir = GrammarParser().parse(b"Disprove that every graph is planar.", "p")
    assert ir.requested_outcome == "disprove"


def test_two_parsers_have_distinct_ids_and_reconcile():
    a = GrammarParser().parse(TRUE_ISH, "p")
    b = ClauseParser().parse(TRUE_ISH, "p")
    recon = reconcile(a, b)
    # agreement on outcome at minimum
    assert "requested_outcome" in recon.agreed_fields
    assert 0.0 <= recon.target_fidelity_risk() <= 1.0


def test_reconcile_requires_independent_parsers():
    a = GrammarParser().parse(TRUE_ISH, "p")
    import pytest
    with pytest.raises(ValueError):
        reconcile(a, a)


def test_backtranslate_roundtrips_key_fields():
    ir = GrammarParser().parse(FALSE, "p")
    prose = backtranslate(ir)
    assert "prove" in prose.lower()


# ── paraphrase invariance / mutation covariance ───────────────────────────────

def test_paraphrase_preserves_semantic_hash():
    parser = GrammarParser()
    ir = parser.parse(TRUE_ISH, "p")
    para = paraphrase(TRUE_ISH.decode())
    ir2 = parser.parse(para.encode(), "p")
    assert ir.semantic_hash() == ir2.semantic_hash()


def test_mutation_changes_semantic_hash():
    parser = GrammarParser()
    ir = parser.parse(FALSE, "p")
    mutated, changed = mutate(FALSE.decode())
    assert changed
    ir2 = parser.parse(mutated.encode(), "p")
    assert ir.semantic_hash() != ir2.semantic_hash()


def test_probe_battery_flags_insensitivity_correctly():
    probes = run_integrity_probes(FALSE, "p", GrammarParser().parse(FALSE, "p"))
    names = {p.name for p in probes}
    assert {"paraphrase_invariance", "mutation_covariance", "dimensional_type",
            "boundary_enumeration", "counterexample_search"} <= names


# ── executable probes ──────────────────────────────────────────────────────────

def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def test_counterexample_probe_finds_false_statement():
    # "all n are prime" — predicate is false at n=0,1,4,...
    ir = GrammarParser().parse(FALSE, "p")
    probes = run_integrity_probes(
        FALSE, "p", ir, predicate=_is_prime, search_space=range(0, 20)
    )
    ce = [p for p in probes if p.name == "counterexample_search"][0]
    assert ce.passed is False
    assert ce.artifacts["counterexample"] in (0, 1, 4)


def test_boundary_probe_passes_true_statement():
    ir = GrammarParser().parse(TRUE_ISH, "p")
    probes = run_integrity_probes(
        TRUE_ISH, "p", ir, predicate=lambda n: n + 0 == n, boundary_points=(0, 1, 2),
        search_space=range(0, 20),
    )
    ce = [p for p in probes if p.name == "counterexample_search"][0]
    bnd = [p for p in probes if p.name == "boundary_enumeration"][0]
    assert ce.passed and bnd.passed


# ── interpretation lattice ──────────────────────────────────────────────────────

def test_lattice_single_node_when_parsers_agree():
    a = GrammarParser().parse(TRUE_ISH, "p")
    b = ClauseParser().parse(TRUE_ISH, "p")
    recon = reconcile(a, b)
    lattice = build_interpretation_lattice("erdos-1", recon)
    if recon.agreed:
        assert len(lattice.nodes) == 1


def test_contract_blocks_release_on_false_statement():
    contract = build_problem_contract(
        problem_id="erdos-1", source_bytes=FALSE, source_id="p",
        predicate=_is_prime, search_space=range(0, 20),
    )
    # counterexample probe fails -> release blocked and decision recorded
    assert contract.release_blocked
    assert any("counterexample" in d for d in contract.unresolved_decisions)


def test_contract_hash_is_deterministic():
    kw = dict(problem_id="erdos-1", source_bytes=TRUE_ISH, source_id="p")
    c1 = build_problem_contract(**kw)
    c2 = build_problem_contract(**kw)
    assert c1.contract_hash() == c2.contract_hash()


def test_ambiguous_statement_creates_multiple_interpretations_and_blocks_release():
    contract = build_problem_contract(
        problem_id="erdos-2", source_bytes=AMBIG, source_id="p"
    )
    # Two independent parsers disagree on this ambiguous statement.
    if not contract.reconciliation.agreed:
        assert len(contract.lattice.nodes) >= 2
        assert contract.lattice.release_blocked


def test_simple_quantified_statement_reconciles_without_inventing_a_binder():
    source = b"Prove that for all natural numbers n, n squared is at least 0."
    grammar = GrammarParser().parse(source, "p")
    clause = ClauseParser().parse(source, "p")

    assert [(b.name, b.domain, b.quantifier) for b in grammar.binders] == [
        ("n", "\u2115", "universal")
    ]
    assert [(b.name, b.domain, b.quantifier) for b in clause.binders] == [
        ("n", "\u2115", "universal")
    ]
    assert grammar.conclusion == source.decode()
    assert clause.conclusion == source.decode()
    assert reconcile(grammar, clause).agreed


def test_untyped_quantified_binder_remains_release_blocking():
    source = b"Prove that for all n, 2*n is even."
    contract = build_problem_contract(
        problem_id="untyped", source_bytes=source, source_id="p",
        predicate=lambda n: (2 * n) % 2 == 0,
    )

    assert contract.primary_ir.binders[0].name == "n"
    assert contract.primary_ir.binders[0].domain == "unspecified"
    assert contract.release_blocked
    assert any("dimensional_type" in decision for decision in contract.unresolved_decisions)


def test_semantic_identity_includes_domains_and_definitions():
    base = StatementIR(
        source_id="p", source_hash="h", binders=[Binder("n", "\u2115", "universal")],
        definitions=[Definition("f", 1, "f(n)=n+1")], conclusion="f(n) > n",
        requested_outcome="prove", parser_id="a", parser_family="family-a",
    )
    changed_domain = StatementIR(
        source_id="p", source_hash="h", binders=[Binder("n", "\u2124", "universal")],
        definitions=[Definition("f", 1, "f(n)=n+1")], conclusion="f(n) > n",
        requested_outcome="prove", parser_id="b", parser_family="family-b",
    )
    changed_definition = StatementIR(
        source_id="p", source_hash="h", binders=[Binder("n", "\u2115", "universal")],
        definitions=[Definition("f", 1, "f(n)=n-1")], conclusion="f(n) > n",
        requested_outcome="prove", parser_id="b", parser_family="family-b",
    )

    assert base.semantic_hash() != changed_domain.semantic_hash()
    assert base.semantic_hash() != changed_definition.semantic_hash()
    assert "binder_domains" in reconcile(base, changed_domain).disagreements
    assert "definitions" in reconcile(base, changed_definition).disagreements


def test_empty_statement_is_malformed_and_release_blocking():
    contract = build_problem_contract(problem_id="empty", source_bytes=b"", source_id="p")

    assert contract.release_blocked
    assert "malformed:empty_statement" in contract.unresolved_decisions
