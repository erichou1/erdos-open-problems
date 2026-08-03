"""Tests for the search plane: mechanism, debt, blueprint, dedup, failure, bands, controller."""

import pytest

from egmra.search import (
    ActionComponents,
    AndOrBlueprint,
    BranchPosterior,
    Controller,
    DebtPolicy,
    MechanismFingerprint,
    Node,
    Obligation,
    QualityDiversityArchive,
    UtilityWeights,
    ao_star_next_leaf,
    band,
    branch_action_utility,
    can_expand,
    compatible_families,
    credit_for_action,
    dedup_cascade,
    delta_verified_debt,
    disposition,
    evolution_allowed,
    instantiate_programs,
    is_censored,
    make_failure_certificate,
    reserve_amount,
    route_search_level,
    ucb1,
)


def _fp(family="direct_structural", **kw):
    base = dict(target_interpretation="int-1", reformulation="r", method_family=family,
                central_proposed_lemma="L")
    base.update(kw)
    return MechanismFingerprint(**base)


# ── mechanism / QD archive ──────────────────────────────────────────────────────

def test_mechanism_fingerprint_rejects_unknown_family():
    with pytest.raises(ValueError):
        _fp(family="not_a_family")


def test_qd_archive_preserves_diverse_mechanisms():
    arc = QualityDiversityArchive()
    assert arc.consider(_fp("direct_structural"), quality=0.5, branch_id="b1")
    assert arc.consider(_fp("probabilistic_analytic"), quality=0.4, branch_id="b2")
    # same bin, lower quality -> not admitted
    assert not arc.consider(_fp("direct_structural"), quality=0.3, branch_id="b3")
    # same bin, higher quality -> replaces
    assert arc.consider(_fp("direct_structural"), quality=0.9, branch_id="b4")
    assert arc.diversity_coverage() == 2


# ── verified debt ────────────────────────────────────────────────────────────────

def test_verified_debt_and_delta():
    policy = DebtPolicy()
    before = [Obligation("o1", closed=False, risk=1.0, cost=1.0),
              Obligation("o2", closed=False, risk=1.0, cost=1.0)]
    after = [Obligation("o1", closed=True, risk=1.0, cost=1.0),
             Obligation("o2", closed=False, risk=1.0, cost=1.0)]
    assert delta_verified_debt(before, after, policy) > 0


def test_restating_helper_gets_nonpositive_credit():
    policy = DebtPolicy()
    before = [Obligation("target", closed=False, risk=2.0, cost=2.0)]
    # "closing" the target by introducing a helper that restates it
    after = [Obligation("target", closed=True, risk=2.0, cost=2.0),
             Obligation("helper", closed=False, risk=2.0, cost=2.0, restates_target=True)]
    assert credit_for_action(before, after, policy) <= 0


def test_debt_policy_hash_stable():
    assert DebtPolicy().policy_hash() == DebtPolicy().policy_hash()


# ── AND/OR blueprint ─────────────────────────────────────────────────────────────

def test_andor_closure_semantics():
    bp = AndOrBlueprint(goal_id="GOAL")
    bp.add_node(Node("l1", "lemma1", "LEAF", closed=False))
    bp.add_node(Node("l2", "lemma2", "LEAF", closed=False))
    bp.add_node(Node("GOAL", "target", "OR", children=[]))
    bp.add_sufficient_lemma_set(["l1"], or_parent="GOAL")
    bp.add_sufficient_lemma_set(["l2"], or_parent="GOAL")
    assert not bp.is_closed()
    bp.nodes["l1"].closed = True
    assert bp.is_closed()  # OR: one sufficient set closed


def test_failed_dependency_cone():
    bp = AndOrBlueprint(goal_id="GOAL")
    bp.add_node(Node("l1", "lemma1", "LEAF"))
    bp.add_node(Node("and1", "and", "AND", children=["l1"]))
    bp.add_node(Node("GOAL", "t", "AND", children=["and1"]))
    cone = bp.failed_dependency_cone("l1")
    assert "and1" in cone and "GOAL" in cone


# ── dedup ─────────────────────────────────────────────────────────────────────────

def test_dedup_exact_merges():
    v = dedup_cascade(a_target_hash="h", b_target_hash="h",
                      a_assumptions=["x"], b_assumptions=["x"])
    assert v.is_duplicate and v.action == "merge"


def test_dedup_distinct_kept():
    v = dedup_cascade(a_target_hash="h1", b_target_hash="h2",
                      a_assumptions=["x"], b_assumptions=["y"],
                      a_mechanism=_fp("direct_structural"), b_mechanism=_fp("algebraic_spectral"))
    assert not v.is_duplicate and v.action == "keep"


# ── failure ────────────────────────────────────────────────────────────────────────

def test_failure_disposition():
    assert disposition("valid_counterexample") == "kill"
    assert disposition("resource_exhaustion") == "pause"
    assert is_censored("timeout")
    with pytest.raises(ValueError):
        disposition("nonsense")


def test_failure_certificate_censors_resource_exhaustion():
    cert = make_failure_certificate(branch_id="b1", mechanism_fingerprint="fp",
                                    reason="resource_exhaustion")
    assert "censored" in cert.what_was_learned
    assert cert.reopen_condition


# ── bands ──────────────────────────────────────────────────────────────────────────

def test_bands_and_reserve():
    assert band(0).purpose == "integrity"
    assert band(5).purpose == "release"
    assert can_expand(2, condition_met=True)
    assert not can_expand(5, condition_met=True)
    assert 0.10 <= reserve_amount(100.0, 0.15) / 100.0 <= 0.20


# ── controller ────────────────────────────────────────────────────────────────────

def test_additive_utility_not_multiplicative():
    # A near-zero factor must not veto the whole branch (additive, not multiplicative).
    comps = ActionComponents(expected_outcome_value=1.0, diversity=0.0, unlock=2.0,
                             expected_cost=0.5)
    util = branch_action_utility(comps, UtilityWeights())
    assert util > 0  # unlock still contributes despite zero diversity


def test_controller_protected_fraction_clamped():
    c = Controller(global_budget=100.0, protected_fraction=0.05)
    assert 0.15 <= c.protected_fraction <= 0.25


def test_controller_branch_cap_needs_governor_event():
    c = Controller(global_budget=10.0, max_branch_fraction=0.4, seed=1)
    c.register(BranchPosterior("b1"))
    # push branch b1 past its cap without justification -> refused
    ok = True
    for _ in range(10):
        ok = c.allocate("b1", amount=1.0, verified_debt_reduction=0.0, info_gain=0.0)
        if not ok:
            break
    assert ok is False
    # with justification a governor event is recorded and allocation proceeds
    c2 = Controller(global_budget=10.0, max_branch_fraction=0.4, seed=1)
    c2.register(BranchPosterior("b1", attempts=5))
    assert c2.allocate("b1", amount=5.0, verified_debt_reduction=1.0, info_gain=0.5)
    assert c2.governor_events


def test_controller_pause_and_terminate_rules():
    c = Controller(global_budget=100.0)
    assert not c.should_pause("b1", marginal_value=0.1, expected_cost=1.0, debt_reduction=0.0,
                              info_gain=0.0, repeated=True, protected_obligation=True, review_count=5)
    assert c.should_pause("b1", marginal_value=0.1, expected_cost=1.0, debt_reduction=0.0,
                          info_gain=0.0, repeated=True, protected_obligation=False, review_count=5)
    assert c.can_terminate("valid_counterexample")
    assert not c.can_terminate("timeout")
    assert c.should_reopen("new_counterexample_changes_lattice")


def test_controller_selection_reserves_exploration():
    c = Controller(global_budget=100.0, protected_fraction=0.2, seed=3)
    for i in range(5):
        c.register(BranchPosterior(f"b{i}", attempts=i))
    cands = [(f"b{i}", ActionComponents(expected_outcome_value=float(i))) for i in range(5)]
    picks = c.select_posterior_actions(cands, k=4)
    assert len(picks) == len(set(picks)) <= 4


# ── programs / algorithms ─────────────────────────────────────────────────────────

def test_program_families_and_dispatch():
    fams = compatible_families("number_theory")
    assert "additive_combinatorial" in fams
    programs = instantiate_programs("number_theory", bottleneck="counterexample", max_programs=4)
    assert programs and all(p.falsifier for p in programs)


def test_search_level_routing():
    assert route_search_level("lean_proof_state") == "puct_mcts_beam"
    assert route_search_level("executable_candidates") == "evolutionary_islands"
    with pytest.raises(KeyError):
        route_search_level("nope")


def test_evolution_only_with_hard_evaluator():
    assert evolution_allowed(has_executable_fitness=True, has_independent_checker=True)
    assert not evolution_allowed(has_executable_fitness=True, has_independent_checker=False)


def test_ucb_and_ao_star():
    assert ucb1(0.5, 10, 0) == float("inf")
    assert ao_star_next_leaf([{"node_id": "a", "centrality": 0.9, "cost": 1.0},
                              {"node_id": "b", "centrality": 0.2, "cost": 1.0}]) == "a"


# ── stratified first-wave selection (report R2) ──────────────────────────────

def test_first_wave_is_stratified_not_registry_prefix():
    """The old prefix bias always chose direct/contradiction/extremal for
    classified domains, silencing the computational/formal/model-construction
    families (and the experimentalist and formalizer roles). A first wave must
    span the proof, refutation, and tool strata."""
    programs = instantiate_programs("number_theory", max_programs=3)
    families = [p.family for p in programs]
    assert families[0] == "direct_structural"                      # proof route
    assert families[1] == "contradiction_minimal_counterexample"   # refutation
    assert families[2] in {"computational_finite_reduction",
                           "formal_library_first",
                           "literature_derived_transfer"}          # tool route
    assert families != ["direct_structural",
                        "contradiction_minimal_counterexample",
                        "extremal_invariant"]                      # the old bug


def test_formal_target_and_predicate_steer_the_tool_stratum():
    with_target = instantiate_programs("number_theory", max_programs=3,
                                       has_formal_target=True)
    assert with_target[2].family == "formal_library_first"
    with_predicate = instantiate_programs("number_theory", max_programs=3,
                                          has_predicate=True)
    assert with_predicate[2].family == "computational_finite_reduction"


def test_stratified_selection_is_deterministic_and_fills_remaining_slots():
    a = [p.family for p in instantiate_programs("graph_theory", max_programs=5)]
    b = [p.family for p in instantiate_programs("graph_theory", max_programs=5)]
    assert a == b                                   # deterministic
    assert len(a) == len(set(a)) == 5               # no duplicates
    # After the three strata, remaining slots fill in registry order.
    assert set(a[:3]) < set(a)


def test_bottleneck_filter_still_dominates():
    programs = instantiate_programs("number_theory", bottleneck="formalization",
                                    max_programs=3)
    assert all("formal" in p.family for p in programs)
