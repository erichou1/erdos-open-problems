"""Prompting improvements grounded in live-exchange analysis (2026-07).

Mined from 260 cached production exchanges (egmra_campaigns/ckpts-shared):

* 98% of executable experiments were bound to the model's own lemma ids and
  therefore executed but silently inadmissible as evidence (only target-bound
  computations pass the intent-certificate hash gate); sandbox replays showed
  86% of them WOULD have produced genuine evidence if goal-bound.  The schema
  tail now states the admissibility rule, and every executed experiment feeds
  a ground-truth verdict line into the next round's prompt (the ToRA finding:
  execution feedback interleaved with reasoning is the main lever, arXiv
  2309.17452).
* 14 full browser rounds died only because falsifiers were structured objects
  instead of strings; falsifier parsing now coerces objects to compact
  strings (advisory field only — claims/experiments/Lean stay strict).
* Truncated replies (28 observed) motivated an explicit reply budget in the
  schema tail (format pressure also degrades reasoning: arXiv 2408.02442).

All epistemic boundaries are unchanged: verdict lines are rendered prompt
context, never evidence; lemma-bound experiments still run (exploration) and
are still never admitted.
"""

from __future__ import annotations

import base64
import json

import pytest

from egmra.compute.service import ComputeService
from egmra.orchestrator.runner_worker import (
    _CAPABILITY_AND_SCHEMA_TAIL,
    _EXTRACTION_SCHEMA_TAIL,
    _REASONING_TAIL,
    RunnerWorker,
    WorkerResponseSchemaError,
    branch_prompt,
    continuation_prompt,
    parse_worker_response,
    problem_research_protocol,
)
from egmra.tests.test_multi_turn_worker import PromptRecordingRunner


def _reply(*, claims=(), experiments=(), falsifiers=(), open_subgoals=("keep going",)):
    return json.dumps({
        "goal_restatement": "restated",
        "claims": [
            {"claim_id": cid, "statement": statement, "depends_on": [],
             "scope": "general"}
            for cid, statement in claims
        ],
        "falsifiers": list(falsifiers),
        "search_queries": [],
        "candidate_sequences": [],
        "experiments": list(experiments),
        "formalization_requests": [],
        "lean_declaration_candidates": [],
        "open_subgoals": list(open_subgoals),
        "bottleneck": "b",
    })


def _b64(code: str) -> str:
    return base64.b64encode(code.encode()).decode()


# --- lenient falsifier coercion -------------------------------------------


def test_falsifier_objects_are_coerced_to_compact_strings():
    # The exact live shape that killed 14 production rounds.
    text = _reply(falsifiers=[
        {"claim_id": "F1", "target": "C1",
         "test": "Enumerate all graphs on six vertices and compare maxima."},
        "plain string survives",
    ])
    parsed = parse_worker_response(text)
    assert parsed["falsifiers"] == [
        "[C1] Enumerate all graphs on six vertices and compare maxima.",
        "plain string survives",
    ]


def test_falsifier_object_without_known_text_key_uses_json_dump():
    parsed = parse_worker_response(_reply(falsifiers=[{"idea": "n=3 fails"}]))
    assert parsed["falsifiers"] == ['{"idea": "n=3 fails"}']


def test_falsifier_non_string_non_object_entries_still_rejected():
    with pytest.raises(WorkerResponseSchemaError):
        parse_worker_response(_reply(falsifiers=[7]))


# --- schema tail: admissibility rule + reply budget ------------------------


def test_tail_states_goal_binding_rule_and_reply_budget():
    assert "EXPERIMENT ADMISSIBILITY" in _CAPABILITY_AND_SCHEMA_TAIL
    assert "advisory" in _CAPABILITY_AND_SCHEMA_TAIL
    assert "REPLY BUDGET" in _CAPABILITY_AND_SCHEMA_TAIL
    # Existing wave4 pins must survive the rewrite.
    assert "OUTPUT CONSTRAINTS" in _CAPABILITY_AND_SCHEMA_TAIL
    assert "dependency cone" in _CAPABILITY_AND_SCHEMA_TAIL
    assert "sat_witness" in _CAPABILITY_AND_SCHEMA_TAIL
    assert "confidence" not in _CAPABILITY_AND_SCHEMA_TAIL
    assert "TARGET" in _REASONING_TAIL  # two-call parity for the rule


def test_branch_prompt_searches_portfolio_before_final_artifact_selection():
    prompt = branch_prompt("S", role="prover", branch_id="b1", packet_summary="")
    assert "elapsed time and verbosity are not goals" in prompt
    assert "Test several genuinely independent attacks" in prompt
    assert "Depth means closing dependencies" in prompt
    search = prompt.index("Do not commit to the first plausible route")
    decision = prompt.index("After completing the internal portfolio search and audit")
    assert search < decision
    assert "single most decisive surviving artifact" in prompt


def test_branch_prompt_derives_problem_specific_completion_and_exclusions():
    prompt = branch_prompt(
        "For every n, estimate the limsup and determine whether it equals 2.",
        role="formalizer", branch_id="b1", packet_summary="",
        formal_target="theorem target : True := by trivial")
    assert "COMPLETION CONTRACT" in prompt
    assert "RESULTS THAT DO NOT COUNT" in prompt
    assert "universal or infinite quantifier" in prompt
    assert "asymptotic regime" in prompt
    assert "one-sided implication" in prompt
    assert "exact community formal target" in prompt
    assert "BASELINE ALIGNMENT" in prompt
    assert "AUDIT ROUTING" in prompt


def test_role_specific_exclusion_is_rendered_without_schema_growth():
    prompt = branch_prompt(
        "Does the proposed construction exist?", role="skeptic",
        branch_id="b1", packet_summary="")
    assert "heuristic obstruction without a checkable witness" in prompt
    # Prompt guidance reuses existing fields; no response-schema key was added.
    assert "results_that_do_not_count" not in _CAPABILITY_AND_SCHEMA_TAIL


# --- sandbox verdicts feed later rounds ------------------------------------

_TRUE_CODE = 'def experiment(inputs):\n    return {"result": True, "coverage": "n <= 4"}\n'
_FALSE_CODE = 'def experiment(inputs):\n    return {"result": False, "coverage": "n <= 4"}\n'


def test_experiment_results_render_in_continuation_prompt():
    later = continuation_prompt(
        "S", role="prover", branch_id="b1", round_index=2, ledger_summary="",
        open_subgoals=[], objections=[], failed_approaches=[],
        experiment_results=["exp A: PASSED (result True, independently replayed)"])
    assert "SANDBOX EXPERIMENT RESULTS" in later
    assert "exp A: PASSED" in later
    bare = continuation_prompt(
        "S", role="prover", branch_id="b1", round_index=2, ledger_summary="",
        open_subgoals=[], objections=[], failed_approaches=[])
    assert "SANDBOX EXPERIMENT RESULTS" not in bare


def test_repeated_exact_bottleneck_triggers_blocker_only_round():
    runner = PromptRecordingRunner([
        _reply(claims=[("lem1", "A useful strict sublemma")],
               open_subgoals=("prove frame balancing",)),
        _reply(open_subgoals=("prove frame balancing",)),
        _reply(claims=[("lem2", "The frame balancing lemma")],
               open_subgoals=()),
    ])
    worker = RunnerWorker(
        runner=runner, goal_claim_id="goal", goal_formula="Target",
        max_rounds=3)
    out = worker.work_branch(
        None, None, branch_id="b1", budget=5.0, fencing_token=1)
    third_prompt = runner.calls[2][1]
    assert "BLOCKER-ONLY ROUND (Sabidussi protocol)" in third_prompt
    assert "EXACT BLOCKER: b" in third_prompt
    assert "Freeze the target-level plan" in third_prompt
    assert any(p["claim_id"] == "lem2" for p in out.claim_proposals)


def test_work_branch_feeds_sandbox_verdicts_into_next_round():
    runner = PromptRecordingRunner([
        _reply(
            claims=[("lem1", "L1 holds for small n")],
            experiments=[
                {"description": "goal-bound finite check", "kind": "finite",
                 "code_b64": _b64(_TRUE_CODE), "inputs": {}, "claim_id": "goal",
                 "coverage": "n <= 4"},
                {"description": "lemma-bound check", "kind": "finite",
                 "code_b64": _b64(_FALSE_CODE), "inputs": {}, "claim_id": "lem1",
                 "coverage": "n <= 4"},
            ]),
        _reply(claims=[("lem2", "L2")], open_subgoals=()),
    ])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T",
                          max_rounds=2, compute_service=ComputeService())
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    round2_prompt = runner.calls[1][1]
    assert "SANDBOX EXPERIMENT RESULTS" in round2_prompt
    assert "goal-bound finite check: PASSED" in round2_prompt
    assert "lemma-bound check: returned FALSE" in round2_prompt
    assert "advisory only" in round2_prompt          # lemma-bound annotation
    # Epistemic boundary unchanged: only the goal-bound True run yields evidence.
    assert len(out.evidence) == 1
    assert out.evidence[0]["claim_ids"] == ["goal"]


def test_run_experiments_outcomes_kwarg_is_optional():
    worker = RunnerWorker(runner=PromptRecordingRunner([]), goal_claim_id="goal",
                          goal_formula="T", compute_service=ComputeService())
    outcomes: list[str] = []
    evidence, replays = worker._run_experiments(
        [{"description": "d", "kind": "finite", "code": _TRUE_CODE,
          "inputs": {}, "claim_id": "", "coverage": "n <= 2"}],
        branch_id="b1", seen={"goal"}, failures=[], outcomes=outcomes)
    assert len(evidence) == 1 and len(replays) == 1
    assert outcomes and "PASSED" in outcomes[0]
    # Legacy call shape (no outcomes kwarg) still works.
    evidence2, _ = worker._run_experiments(
        [], branch_id="b1", seen={"goal"}, failures=[])
    assert evidence2 == []


def test_outcome_line_reports_crash_diagnostics():
    worker = RunnerWorker(runner=PromptRecordingRunner([]), goal_claim_id="goal",
                          goal_formula="T", compute_service=ComputeService())
    outcomes: list[str] = []
    worker._run_experiments(
        [{"description": "bad code", "kind": "finite",
          "code": "def experiment(inputs):\n    return {\"result\": undefined_name}\n",
          "inputs": {}, "claim_id": "", "coverage": "n <= 2"}],
        branch_id="b1", seen={"goal"}, failures=[], outcomes=outcomes)
    assert len(outcomes) == 1
    assert "PASSED" not in outcomes[0]


# --- Kerger concreteness + hand-wave discipline -----------------------------


def test_handwave_phrases_become_recorded_objections_for_next_round():
    reply1 = json.dumps({
        "goal_restatement": "r",
        "claims": [{"claim_id": "lem1",
                    "statement": "The extension step is standard argument",
                    "depends_on": [], "scope": "general"}],
        "proof_steps": ["The compatibility step is routine and omitted"],
        "falsifiers": [], "search_queries": [], "candidate_sequences": [],
        "experiments": [], "formalization_requests": [],
        "lean_declaration_candidates": [],
        "open_subgoals": ["close it"], "bottleneck": "b1",
    })
    runner = PromptRecordingRunner([
        reply1,
        _reply(claims=[("lem2", "L2")], open_subgoals=()),
    ])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T",
                          max_rounds=2)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0,
                             fencing_token=1)
    assert any("hand-wave flagged" in f for f in out.falsifiers)
    round2_prompt = runner.calls[1][1]
    assert "hand-wave flagged" in round2_prompt          # rendered as objection
    assert "justify this step rigorously or replace it" in round2_prompt


def test_schema_tail_forbids_status_reports_and_routine_steps():
    assert "non-actionable status report" in _CAPABILITY_AND_SCHEMA_TAIL
    assert "'standard' or 'routine'" in _CAPABILITY_AND_SCHEMA_TAIL


def test_artifact_free_round_is_recorded_and_treated_as_stalled():
    empty = json.dumps({
        "goal_restatement": "still thinking",
        "claims": [], "proof_steps": [], "falsifiers": [],
        "search_queries": [], "candidate_sequences": [], "experiments": [],
        "formalization_requests": [], "lean_declaration_candidates": [],
        "open_subgoals": ["promising directions remain"],
        "bottleneck": "different each time 1",
    })
    runner = PromptRecordingRunner([
        _reply(claims=[("lem1", "L1")], open_subgoals=("g",)),
        empty,
        _reply(claims=[("lem2", "L2")], open_subgoals=()),
    ])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T",
                          max_rounds=3)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0,
                             fencing_token=1)
    assert any(f.startswith("non_actionable_round:b1:round2")
               for f in out.failures)
    # The stall consumed the recovery escalation (round 3 is a recovery round).
    third = runner.calls[2][1]
    assert ("STAGNATION" in third) or ("BLOCKER-ONLY" in third)


def test_continuation_prompt_states_regulator_decision_priors():
    later = continuation_prompt(
        "S", role="prover", branch_id="b1", round_index=2, ledger_summary="",
        open_subgoals=[], objections=[], failed_approaches=[])
    assert "local execution slip" in later               # REVISE_PROOF prior
    assert "misordered, or refuted" in later             # REVISE_PLAN prior
    assert "same mechanism failing the same way" in later  # REWRITE prior
    assert "theorem-strength gap is FOCUS_BLOCKER" in later
    assert "the evidence overrides it" in later          # prior, not verdict


def test_referee_prompt_hunts_first_error_with_defect_classes():
    from egmra.orchestrator.runner_worker import referee_prompt

    prompt = referee_prompt(
        "T", [{"claim_id": "c1", "statement": "s",
               "depends_on": ["c0"]}])
    assert "FIRST unjustified step" in prompt
    assert "dependency order" in prompt
    assert "c1 [deps: c0]: s" in prompt
    assert "import-mismatch" in prompt and "hand-wave" in prompt
    assert "it is NOT established" in prompt             # uncertain => fail
    assert "LOCKED TARGET STATEMENT (immutable)" in prompt
    assert "RESULTS THAT DO NOT COUNT" in prompt
    assert "smallest, degenerate, equality" in prompt
    assert "has no authority to approve a proof" in prompt
    assert "Do NOT approve or assert any proof." in prompt


def test_cold_pass_is_specific_rigid_and_model_locked():
    from egmra.orchestrator.runner_worker import cold_pass_prompt

    prompt = cold_pass_prompt(
        "For every integer n, prove P(n).", role="skeptic",
        exact_model="- binder: for all n ranging over integers",
        traps=["n=0 changes the convention"],
    )
    assert "LOCKED TARGET STATEMENT (immutable)" in prompt
    assert "EXACT MODEL (locked interpretation)" in prompt
    assert "for all n ranging over integers" in prompt
    assert "n=0 changes the convention" in prompt
    assert "at least four materially different failure mechanisms" in prompt
    assert "RESULTS THAT DO NOT COUNT" in prompt
    assert "retrieval queries" in prompt and "parameter regime" in prompt
    assert "no evidentiary authority" in prompt


def test_every_active_reasoning_prompt_has_a_purpose_specific_rigorous_contract():
    from egmra.lean.formalizer import build_formalization_prompt
    from egmra.orchestrator.runner_worker import (
        cold_pass_prompt,
        referee_prompt,
        sketch_prompt,
    )
    from egmra.verification.informal_review import hostile_review_prompt

    prompts = {
        "branch": branch_prompt(
            "For every n, prove P(n).", role="prover", branch_id="b1",
            packet_summary="", exact_model="- binder: for all n"),
        "continuation": continuation_prompt(
            "For every n, prove P(n).", role="prover", branch_id="b1",
            round_index=2, ledger_summary="", open_subgoals=["bridge"],
            objections=[], failed_approaches=[], exact_model="- binder: for all n"),
        "cold": cold_pass_prompt(
            "For every n, prove P(n).", role="skeptic",
            exact_model="- binder: for all n"),
        "sketch": sketch_prompt(
            "For every n, prove P(n).",
            formal_target="theorem target : True := by trivial",
            target_declaration="target"),
        "referee": referee_prompt(
            "For every n, prove P(n).",
            [{"claim_id": "c1", "statement": "P(0)"}]),
        "formalizer": build_formalization_prompt(
            declaration_name="target", expected_type="True",
            informal_statement="For every n, prove P(n)."),
        "hostile_review": hostile_review_prompt(
            "For every n, prove P(n).", [], []),
    }
    required_markers = {
        "branch": (
            "TARGET STATEMENT", "LONG-HORIZON SEARCH DISCIPLINE",
            "RESULTS THAT DO NOT COUNT", "REQUIRED ADVERSARIAL AUDIT",
            "independent pipeline"),
        "continuation": (
            "immutable TARGET STATEMENT", "LONG-HORIZON SEARCH DISCIPLINE",
            "RESULTS THAT DO NOT COUNT", "REQUIRED ADVERSARIAL AUDIT",
            "independent verification"),
        "cold": (
            "LOCKED TARGET STATEMENT", "DELIBERATION CONTRACT",
            "materially different failure mechanisms",
            "RESULTS THAT DO NOT COUNT", "no evidentiary authority"),
        "sketch": (
            "LOCKED COMMUNITY FORMAL TARGET", "INTERNAL SEARCH PROTOCOL",
            "materially different assembly plans", "RESULTS THAT DO NOT COUNT",
            "downstream sealed kernel"),
        "referee": (
            "LOCKED TARGET STATEMENT", "AUDIT PROTOCOL",
            "RESULTS THAT DO NOT COUNT", "FIRST unjustified step",
            "no authority to approve a proof"),
        "formalizer": (
            "LOCKED FORMAL OBLIGATION", "PROOF-DEVELOPMENT PROTOCOL",
            "materially different routes", "RESULTS THAT DO NOT COUNT",
            "Independent kernel replay decides success"),
        "hostile_review": (
            "LOCKED TARGET STATEMENT", "REVIEW COMPLETION CONTRACT",
            "at least four distinct passes", "RESULTS THAT DO NOT COUNT AS A PASS",
            "it is NOT established"),
    }
    for name, markers in required_markers.items():
        for marker in markers:
            assert marker in prompts[name], f"{name} prompt lost {marker!r}"
        assert "Assume for purposes of this task that" not in prompts[name]
        assert "Return only when the problem is solved" not in prompts[name]


# --- Kerger information density: exact model + family guidance ---------------


def test_every_method_family_has_mechanism_guidance():
    from egmra.orchestrator.runner_worker import _FAMILY_GUIDANCE
    from egmra.search.mechanism import METHOD_FAMILIES

    assert set(_FAMILY_GUIDANCE) == set(METHOD_FAMILIES)
    for family, guidance in _FAMILY_GUIDANCE.items():
        assert len(guidance.split()) >= 20, family   # real guidance, not a label


def test_branch_prompt_renders_family_guidance_for_known_family_only():
    known = branch_prompt("S", role="prover",
                          branch_id="probabilistic_analytic", packet_summary="")
    assert "BRANCH MECHANISM (probabilistic_analytic)" in known
    assert "independence or negative-correlation" in known
    adhoc = branch_prompt("S", role="prover", branch_id="b1", packet_summary="")
    assert "BRANCH MECHANISM" not in adhoc


def test_exact_model_block_renders_binders_and_hypotheses_from_contract():
    from types import SimpleNamespace

    node = SimpleNamespace(
        conclusion="the target",
        binders=[{"name": "n", "domain": "natural numbers",
                  "quantifier": "for all"}],
        hypotheses=["A is a basis of order 2", "A is infinite"],
    )
    contract = SimpleNamespace(lattice=SimpleNamespace(nodes=[node]))
    worker = RunnerWorker(runner=PromptRecordingRunner([]), goal_claim_id="goal",
                          goal_formula="T")
    model = worker._exact_model(contract)
    assert "- binder: for all n ranging over natural numbers" in model
    assert "- hypothesis: A is a basis of order 2" in model
    prompt = branch_prompt("T", role="prover", branch_id="b1",
                           packet_summary="", exact_model=model)
    assert "EXACT MODEL (locked interpretation" in prompt
    assert "for all n ranging over natural numbers" in prompt
    # No contract -> no block, prompts unchanged.
    assert worker._exact_model(None) == ""
    assert "EXACT MODEL" not in branch_prompt(
        "T", role="prover", branch_id="b1", packet_summary="")


def test_exact_model_persists_into_continuation_rounds():
    later = continuation_prompt(
        "S", role="prover", branch_id="b1", round_index=2, ledger_summary="",
        open_subgoals=[], objections=[], failed_approaches=[],
        exact_model="- binder: for all n ranging over integers")
    assert "EXACT MODEL (locked interpretation" in later
    assert "for all n ranging over integers" in later


def test_packet_budget_was_raised_for_information_density():
    from egmra.orchestrator.runner_worker import (
        _PACKET_CHAR_BUDGET,
        _PACKET_MAX_RECORDS,
    )
    assert _PACKET_CHAR_BUDGET >= 8000
    assert _PACKET_MAX_RECORDS >= 16


# --- per-problem Kerger/CDC protocol compiler -------------------------------


def test_protocol_compiler_contains_full_operational_architecture():
    protocol = problem_research_protocol(
        "For every graph G, prove the matching upper and lower bounds.",
        role="prover", branch_id="direct_structural",
        packet_summary="- t1: exact baseline theorem",
        exact_model="- binder: for all G ranging over finite graphs",
        formal_target="theorem target : True := by trivial",
        traps=["parallel edges are distinct"],
        family_history=["extremal_invariant: BLOCKED at compatibility lemma"],
        carried_subgoals=["prove the extension lemma"],
    )
    for heading in (
        "1. LOCKED TASK AND MODEL",
        "2. COMPLETION STANDARD AND NEGATIVE SPECIFICATION",
        "3. VERIFIED BASELINE AND LITERATURE CHECKPOINT",
        "4. INDEPENDENT BRANCH ASSIGNMENT",
        "5. APPROACH-FAMILY REGISTRY AND PRIOR FAILURES",
        "6. CARRIED OBLIGATIONS",
        "7. LONG-HORIZON SEARCH DISCIPLINE",
        "8. CONCRETE MATHEMATICS REQUIREMENT",
        "9. REQUIRED ADVERSARIAL AUDIT",
        "10. ROOT-SYNTHESIS AND REPORTING CONTRACT",
    ):
        assert heading in protocol
    assert "RESULTS THAT DO NOT COUNT" in protocol
    assert "exact baseline theorem" in protocol
    assert "parallel edges are distinct" in protocol
    assert "prove the extension lemma" in protocol
    assert "After a failed wave, run at least one materially independent" in protocol
    assert "Do not commit to the first plausible route" in protocol
    assert "A wave is PRODUCTIVE only if" in protocol
    assert "marginal mathematical yield remains positive" in protocol
    assert "Stop efficiently when all surviving routes" in protocol
    assert "Do not continue merely to consume time" in protocol
    assert "Search broadly internally; report selectively externally" in protocol
    assert "independent pipeline alone assigns truth status" in protocol
    # Unsafe benchmark truth pressure is deliberately not generalized to open work.
    assert "Assume for purposes of this task that" not in protocol
    assert "Return only when" not in protocol


def test_free_reasoning_separates_deep_search_from_compact_reporting():
    from egmra.orchestrator.runner_worker import _REASONING_TAIL, branch_prompt

    prompt = branch_prompt(
        "Prove T.", role="prover", branch_id="direct_structural",
        packet_summary="")
    assert "After completing the internal portfolio search and audit" in prompt
    assert "must not truncate the preceding search" in prompt
    assert "Do not draft the answer or commit to the first elegant route" in (
        _REASONING_TAIL)
    assert "productive wave must add" in _REASONING_TAIL
    assert "mechanisms are genuinely saturated" in _REASONING_TAIL
    assert "not at an arbitrary time" in _REASONING_TAIL
    assert "compact reporting is not a cap on exploration" in _REASONING_TAIL


def test_protocol_audit_is_problem_and_role_specific():
    graph = problem_research_protocol(
        "For every finite multigraph prove a probabilistic asymptotic bound.",
        role="skeptic", branch_id="counterexample_model_construction",
        packet_summary="")
    assert "Combinatorial-model audit" in graph
    assert "Probability audit" in graph
    assert "Error accounting" in graph
    assert "Counterexample audit" in graph


def test_exact_model_renders_full_primary_ir_fields():
    from types import SimpleNamespace

    definition = SimpleNamespace(
        symbol="f", semantics="f(n) is the extremal count", conventions="n >= 1")
    ir = SimpleNamespace(
        definitions=[definition], requested_outcome="prove",
        parameter_regime="n tends to infinity", constraints=["n is even"],
        edge_cases=["n=2"])
    node = SimpleNamespace(
        conclusion="target", binders=[], hypotheses=[],
        ambiguities_open=["ordered versus unordered pairs"])
    contract = SimpleNamespace(
        lattice=SimpleNamespace(nodes=[node]), primary_ir=ir)
    worker = RunnerWorker(runner=PromptRecordingRunner([]), goal_formula="T")
    model = worker._exact_model(contract)
    assert "definition f: f(n) is the extremal count" in model
    assert "requested outcome: prove" in model
    assert "parameter regime: n tends to infinity" in model
    assert "constraint: n is even" in model
    assert "required edge case: n=2" in model
    assert "unresolved interpretation risk: ordered versus unordered pairs" in model


def test_extraction_schema_preserves_detailed_proof_instead_of_10k_compression():
    assert "aim under 10000 characters" in _CAPABILITY_AND_SCHEMA_TAIL
    assert "aim under 10000 characters" not in _EXTRACTION_SCHEMA_TAIL
    assert "preserve the COMPLETE mathematical content" in _EXTRACTION_SCHEMA_TAIL
    assert "250000 characters" in _EXTRACTION_SCHEMA_TAIL


def test_continuation_preserves_long_prior_proof_detail():
    marker = "DETAIL_AT_END_OF_LONG_DERIVATION"
    long_step = "equation " + "x" * 2_000 + marker
    prompt = continuation_prompt(
        "S", role="prover", branch_id="b1", round_index=2,
        ledger_summary="", open_subgoals=["finish"], objections=[],
        failed_approaches=[], prior_proof_steps=[long_step])
    assert marker in prompt
    assert "PER-PROBLEM LONG-HORIZON RESEARCH PROTOCOL" in prompt
