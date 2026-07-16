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
    _REASONING_TAIL,
    RunnerWorker,
    WorkerResponseSchemaError,
    branch_prompt,
    continuation_prompt,
    parse_worker_response,
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


def test_branch_prompt_is_decision_first():
    prompt = branch_prompt("S", role="prover", branch_id="b1", packet_summary="")
    assert "single most decisive next artifact" in prompt


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
