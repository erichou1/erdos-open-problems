"""Wave 4: SAT leaves (R11), two-call extraction (R7), stop rules (R8),
mechanism tags (R10), and the in-loop sketch lane (R4 phase 2).

Trust invariants pinned here:

* SAT results are DATA checked by OUR canned code in the trusted sandbox +
  independent replay — solver testimony (an unsat claim without a checkable
  trace) is recorded and never executed or admitted.
* The two-call mode keeps the MAIN model as the recorded mathematician; the
  extractor is clerical and malformed extraction repairs re-ask the
  extractor, never the main model.
* Sketch children enter the claim graph only after the decomposition
  development-COMPILED, and the goal honestly gains the children as
  dependencies.
* Mechanism tags are write-time search metadata, bounded and deterministic.
"""

from __future__ import annotations

import json

from egmra.compute.service import ComputeService
from egmra.learning.mechanisms import mechanism_tags
from egmra.orchestrator.dossier import update_dossier
from egmra.orchestrator.rerank import PROGRESS_STATES
from egmra.orchestrator.runner_worker import (
    _CAPABILITY_AND_SCHEMA_TAIL,
    _MAX_REASONING_TRANSCRIPT_BYTES,
    _normalize_sat_experiment,
    _REASONING_TAIL,
    parse_worker_response,
    RunnerWorker,
    sketch_prompt,
)
from egmra.retrieval.lemma_library import append_sealed_lemma
from egmra.tests.test_wave2 import PromptRecordingRunner, _round_reply


# ── R11: SAT leaves — witness checked, testimony refused ─────────────────────

def test_sat_payload_normalization_bounds_and_types():
    good = _normalize_sat_experiment(
        {"cnf": [[1, -2], [2]], "model": {1: True, "2": True}},
        kind="sat_witness")
    assert good == {"cnf": [[1, -2], [2]], "model": {"1": True, "2": True}}
    # zero literals, boolean literals, and non-bool assignments are rejected
    assert _normalize_sat_experiment({"cnf": [[0]], "model": {}},
                                     kind="sat_witness") is None
    assert _normalize_sat_experiment({"cnf": [[True]], "model": {}},
                                     kind="sat_witness") is None
    assert _normalize_sat_experiment({"cnf": [[1]], "model": {1: 1}},
                                     kind="sat_witness") is None
    # unsat WITHOUT a proof keeps the cnf only — routing records testimony
    assert _normalize_sat_experiment({"cnf": [[1], [-1]]},
                                     kind="sat_unsat") == {"cnf": [[1], [-1]]}


def _sat_worker() -> RunnerWorker:
    return RunnerWorker(runner=PromptRecordingRunner([]), goal_claim_id="goal",
                        goal_formula="T", compute_service=ComputeService())


def test_sat_witness_is_checked_in_the_real_sandbox_and_yields_evidence():
    worker = _sat_worker()
    failures: list[str] = []
    evidence, replays = worker._run_experiments(
        [{"description": "2-SAT leaf", "kind": "sat_witness",
          "cnf": [[1, 2], [-1]], "model": {"1": False, "2": True},
          "claim_id": "goal", "coverage": ""}],
        branch_id="b1", seen={"goal"}, failures=failures)
    assert failures == []
    assert len(evidence) == 1 and evidence[0]["kind"] == "exact_computation"
    assert replays and replays[0].output_hash_matches


def test_false_sat_witness_is_a_recorded_failure_never_evidence():
    worker = _sat_worker()
    failures: list[str] = []
    evidence, _ = worker._run_experiments(
        [{"description": "bad witness", "kind": "sat_witness",
          "cnf": [[1], [-1]], "model": {"1": True},
          "claim_id": "goal", "coverage": ""}],
        branch_id="b1", seen={"goal"}, failures=failures)
    assert evidence == []
    assert any("predicate returned false" in f for f in failures)


def test_unsat_with_rup_trace_reconstructs_and_without_stays_testimony():
    worker = _sat_worker()
    failures: list[str] = []
    evidence, _ = worker._run_experiments(
        [{"description": "unsat leaf", "kind": "sat_unsat",
          "cnf": [[1], [-1]], "proof": [[]],
          "claim_id": "goal", "coverage": ""}],
        branch_id="b1", seen={"goal"}, failures=failures)
    assert failures == []
    assert len(evidence) == 1               # empty clause is RUP from {1},{-1}
    # no proof trace → recorded testimony, nothing executed, no evidence
    worker2 = _sat_worker()
    failures2: list[str] = []
    evidence2, replays2 = worker2._run_experiments(
        [{"description": "testimony", "kind": "sat_unsat",
          "cnf": [[1], [-1]], "claim_id": "goal", "coverage": ""}],
        branch_id="b1", seen={"goal"}, failures=failures2)
    assert evidence2 == [] and replays2 == []
    assert any(f.startswith("sat_unsat_unreconstructed:") for f in failures2)


def test_parser_carries_sat_payloads_through():
    reply = json.dumps({
        "goal_restatement": "r", "claims": [], "falsifiers": [],
        "search_queries": [], "candidate_sequences": [],
        "experiments": [
            {"description": "sat leaf", "kind": "sat_witness",
             "cnf": [[1]], "model": {"1": True}, "claim_id": "goal"},
            {"description": "junk sat", "kind": "sat_witness",
             "cnf": "not-a-list", "model": {}},
        ],
        "formalization_requests": [], "lean_declaration_candidates": [],
        "open_subgoals": [], "bottleneck": "", "confidence": 0.2,
    })
    parsed = parse_worker_response(reply)
    assert parsed["experiments"][0]["cnf"] == [[1]]
    assert parsed["experiments"][0]["model"] == {"1": True}
    assert "cnf" not in parsed["experiments"][1]      # malformed payload dropped


# ── R7: trimmed contract + two-call extraction ───────────────────────────────

def test_schema_tail_is_trimmed_and_constraint_first():
    assert "confidence" not in _CAPABILITY_AND_SCHEMA_TAIL
    assert "OUTPUT CONSTRAINTS" in _CAPABILITY_AND_SCHEMA_TAIL
    assert "dependency cone" in _CAPABILITY_AND_SCHEMA_TAIL
    assert "sat_witness" in _CAPABILITY_AND_SCHEMA_TAIL


def test_two_call_mode_keeps_main_identity_and_repairs_the_extractor():
    main = PromptRecordingRunner(["I believe lemma L1 (statement: T holds "
                                  "for even n) follows by induction."])
    extractor = PromptRecordingRunner([
        "not json", _round_reply(claims=[("lem1", "L1 for even n", [])])])
    worker = RunnerWorker(runner=main, goal_claim_id="goal", goal_formula="T",
                          extractor_runner=extractor)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0,
                             fencing_token=1)
    # main model reasoned once, free of the JSON schema
    assert [s for s, _ in main.calls] == ["branch:b1:reasoning"]
    assert _REASONING_TAIL[:40] in main.calls[0][1]
    assert "OUTPUT CONSTRAINTS" not in main.calls[0][1]
    # extraction happened on the cheap model, repaired once, same transcript
    assert [s for s, _ in extractor.calls] == ["branch:b1:extract"] * 2
    assert "I believe lemma L1" in extractor.calls[1][1]
    assert {p["claim_id"] for p in out.claim_proposals} == {"goal", "lem1"}
    # the recorded mathematician is the MAIN model, not the extractor
    assert worker.last_model_identity.model == "recording"
    assert any("malformed_model_output:branch:b1:extract0" in f
               for f in out.failures)


def test_two_call_mode_preserves_reasoning_beyond_old_60k_cutoff():
    marker = "DECISIVE_END_OF_PROOF_MARKER"
    transcript = "A" * 65_000 + marker
    main = PromptRecordingRunner([transcript])
    extractor = PromptRecordingRunner([
        _round_reply(claims=[("lem1", "L1", [])])])
    worker = RunnerWorker(runner=main, goal_claim_id="goal", goal_formula="T",
                          extractor_runner=extractor)
    worker.work_branch(None, None, branch_id="b1", budget=5.0,
                       fencing_token=1)
    assert marker in extractor.calls[0][1]


def test_two_call_mode_rejects_oversize_reasoning_instead_of_truncating():
    transcript = "x" * (_MAX_REASONING_TRANSCRIPT_BYTES + 1)
    main = PromptRecordingRunner([transcript])
    extractor = PromptRecordingRunner([])
    worker = RunnerWorker(runner=main, goal_claim_id="goal", goal_formula="T",
                          extractor_runner=extractor)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0,
                             fencing_token=1)
    assert extractor.calls == []
    assert any(f.startswith("reasoning_output_too_large:branch:b1")
               for f in out.failures)


def test_without_extractor_single_call_behavior_is_unchanged():
    runner = PromptRecordingRunner([_round_reply(claims=[("lem1", "L1", [])])])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T")
    worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert [s for s, _ in runner.calls] == ["branch:b1"]
    assert "OUTPUT CONSTRAINTS" in runner.calls[0][1]


# ── R8: repeated-bottleneck stop rule ────────────────────────────────────────

def test_repeated_bottleneck_with_no_new_claims_stalls_despite_open_subgoals():
    def reply(claims, bottleneck):
        return json.dumps({
            "goal_restatement": "r",
            "claims": [{"claim_id": c, "statement": s, "depends_on": [],
                        "scope": "general", "confidence": 0.5}
                       for c, s in claims],
            "falsifiers": [], "search_queries": [], "candidate_sequences": [],
            "experiments": [], "formalization_requests": [],
            "lean_declaration_candidates": [],
            "open_subgoals": ["still open"], "bottleneck": bottleneck,
            "confidence": 0.5,
        })

    runner = PromptRecordingRunner([
        reply([("lem1", "L1")], "stuck on the density step"),
        reply([], "stuck on the density step"),      # stall: same bottleneck
        reply([], "stuck on the density step"),      # reframe also stalls
        reply([("lem2", "L2")], "would have continued"),
    ])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T",
                          max_rounds=4)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0,
                             fencing_token=1)
    assert len(runner.calls) == 3                    # round 4 never ran
    assert "STAGNATION" in runner.calls[2][1]        # one reframe was spent
    assert "lem2" not in {p["claim_id"] for p in out.claim_proposals}


def test_progress_states_export_matches_rerank():
    assert "CANDIDATE_SOLUTION" in PROGRESS_STATES
    assert "BLOCKED_BY_INTERPRETATION" not in PROGRESS_STATES


# ── R10: mechanism tags at write time ────────────────────────────────────────

def test_mechanism_tags_are_bounded_deterministic_search_metadata():
    tags = mechanism_tags(
        "blocked: the density increment via Fourier/exponential sums fails; "
        "try a probabilistic deletion argument or a greedy construction")
    assert "density_increment" in tags
    assert "fourier_analytic" in tags
    assert "probabilistic" in tags
    assert mechanism_tags("") == ()
    assert len(mechanism_tags("density " * 500)) <= 8


def test_dossier_and_lemma_library_record_tags(tmp_path):
    path = tmp_path / "dossier.json"
    update_dossier(path, problem_id="erdos-1", public_state="OPEN_NO_PROGRESS",
                   harvest={"family_outcomes": [], "failed_approaches": [],
                            "mechanism_tags": ["pigeonhole"]})
    update_dossier(path, problem_id="erdos-1", public_state="OPEN_NO_PROGRESS",
                   harvest={"family_outcomes": [], "failed_approaches": [],
                            "mechanism_tags": ["coloring"]})
    stored = json.loads(path.read_text())
    assert stored["mechanism_tags"] == ["coloring", "pigeonhole"]   # merged
    library = tmp_path / "lemmas.jsonl"
    assert append_sealed_lemma(
        library, problem_id="erdos-1", declaration_name="ramsey_step",
        expected_type_source="∀ n, ramseyNumber n ≤ 4 ^ n",
        source="theorem ramsey_step : ∀ n, ramseyNumber n ≤ 4 ^ n := proof",
        certificate={"expected_type_hash": "h"})
    record = json.loads(library.read_text().splitlines()[0])
    assert "coloring" in record["mechanism_tags"]


# ── R4 phase 2: in-loop sketch lane ──────────────────────────────────────────

_TARGET = ("import Mathlib\n\n"
           "theorem erdos_demo : ∀ (K : ℕ), ∃ N, partitionProperty K N := "
           "sorry\n")

_SKETCH_REPLY = """Here is the sketch:
```lean
lemma child_step : ∀ K : ℕ, K ≤ K + 1 := sorry

theorem erdos_demo : ∀ (K : ℕ), ∃ N, partitionProperty K N := by
  intro K
  exact partition_of (child_step K)
```
"""


class _DevOk:
    def __init__(self, sorries=1, ok=True):
        self.sorries, self.ok = sorries, ok
        self.checked: list[str] = []

    def check(self, source):
        from egmra.lean.warm import DevCheckResult

        self.checked.append(source)
        return DevCheckResult(ok=self.ok, sorries=self.sorries, messages=()
                              if self.ok else ("error:boom",),
                              elapsed_seconds=0.01)


class _ChildProver:
    formalizer_id = "child-prover"

    def formalize(self, *, declaration_name, expected_type,
                  informal_statement, previous_source="", kernel_feedback=""):
        return f"theorem {declaration_name} : {expected_type} := trivial"


def _sketch_worker(dev, *, formal_target=_TARGET) -> tuple[RunnerWorker, PromptRecordingRunner]:
    runner = PromptRecordingRunner([_round_reply(), _SKETCH_REPLY])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T",
                          lean_version="4.28.0", mathlib_commit="v4.28.0",
                          formal_target=formal_target, dev_lean_service=dev,
                          formalizer=_ChildProver())
    return worker, runner


def test_compiled_sketch_admits_children_and_goal_dependencies():
    dev = _DevOk(sorries=1)
    worker, runner = _sketch_worker(dev)
    out = worker.work_branch(None, None, branch_id="formal_library_first",
                             budget=5.0, fencing_token=1)
    assert [s for s, _ in runner.calls] == [
        "branch:formal_library_first", "sketch:formal_library_first"]
    ids = {p["claim_id"] for p in out.claim_proposals}
    assert "child_step" in ids
    goal = out.claim_proposals[0]
    assert "child_step" in goal["dependencies"]       # honest AND-semantics
    assert any(c["declaration_name"] == "child_step"
               for c in out.formal_candidates)
    assert any("sketch decomposition machine-checked" in step
               for step in out.proof_steps)
    # the dev compile saw the import-stripped sketch
    assert dev.checked and "import Mathlib" not in dev.checked[0]


def test_uncompiled_sketch_admits_nothing():
    worker, _ = _sketch_worker(_DevOk(ok=False))
    out = worker.work_branch(None, None, branch_id="formal_library_first",
                             budget=5.0, fencing_token=1)
    assert {p["claim_id"] for p in out.claim_proposals} == {"goal"}
    assert out.claim_proposals[0]["dependencies"] == []
    assert any(f.startswith("sketch_not_compiled:") for f in out.failures)


def test_sketch_lane_is_scoped_to_formal_target_branch_with_dev_service():
    # other branches never spend the sketch call
    dev = _DevOk()
    worker, runner = _sketch_worker(dev)
    worker.work_branch(None, None, branch_id="direct_structural",
                       budget=5.0, fencing_token=1)
    assert [s for s, _ in runner.calls] == ["branch:direct_structural"]
    # no dev service → no sketch call either
    worker2, runner2 = _sketch_worker(None)
    worker2.dev_lean_service = None
    worker2.work_branch(None, None, branch_id="formal_library_first",
                        budget=5.0, fencing_token=1)
    assert [s for s, _ in runner2.calls] == ["branch:formal_library_first"]


def test_sketch_prompt_pins_the_contract():
    text = sketch_prompt("Statement.", formal_target=_TARGET,
                         target_declaration="erdos_demo")
    assert "lemma name : TYPE := sorry" in text
    assert "erdos_demo" in text and "must NOT be sorry" in text
    assert "machine-checked" in text
