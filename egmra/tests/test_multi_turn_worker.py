"""Multi-turn branch development in RunnerWorker (audit R3).

Round 1 uses the branch prompt; later rounds replay the lemma ledger, open
subgoals, objections, and failed-approach memory and ask the model to close or
repair.  These tests pin the control flow (round count, stagnation stop,
malformed-round preservation, cross-round experiment cap, shared failure
memory) and the epistemic boundary: rounds only ever add *proposals*.
"""

from __future__ import annotations

import json

from egmra.agents.runner import RunnerResponse
from egmra.orchestrator.runner_worker import (
    RunnerWorker,
    branch_prompt,
    continuation_prompt,
)
from egmra.provenance.hashing import sha256_hex
from egmra.provenance.stage_identity import AttestedModelIdentity


class PromptRecordingRunner:
    """Returns canned text per call and records (stage, prompt) pairs."""

    def __init__(self, replies):
        self.runner_id = "recording"
        self._replies = list(replies)
        self.calls: list[tuple[str, str]] = []

    def run(self, prompt, *, stage):
        self.calls.append((stage, prompt))
        text = self._replies.pop(0) if self._replies else "{}"
        return RunnerResponse(
            text=text,
            model=AttestedModelIdentity(provider="local", model="recording",
                                        ui_surface="test", account_class="local"),
            context_id=sha256_hex(f"recording:{len(self.calls)}"),
            prompt_hash=sha256_hex(prompt),
        )


def _round_reply(*, claims=(), open_subgoals=(), bottleneck="", falsifiers=()):
    return json.dumps({
        "goal_restatement": "restated",
        "claims": [
            {"claim_id": cid, "statement": statement, "depends_on": [],
             "scope": "general", "confidence": 0.5}
            for cid, statement in claims
        ],
        "falsifiers": list(falsifiers),
        "search_queries": [],
        "candidate_sequences": [],
        "experiments": [],
        "formalization_requests": [],
        "lean_declaration_candidates": [],
        "open_subgoals": list(open_subgoals),
        "bottleneck": bottleneck,
        "confidence": 0.5,
    })


def test_single_round_default_is_one_model_call():
    runner = PromptRecordingRunner([_round_reply(claims=[("lem1", "L1")])])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T")
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert [stage for stage, _ in runner.calls] == ["branch:b1"]
    assert {p["claim_id"] for p in out.claim_proposals} == {"goal", "lem1"}


def test_rounds_accumulate_claims_and_merge_deduped_lists():
    runner = PromptRecordingRunner([
        _round_reply(claims=[("lem1", "L1")], open_subgoals=["close L2"],
                     falsifiers=["check n=0"]),
        _round_reply(claims=[("lem2", "L2")], open_subgoals=["close L3"],
                     falsifiers=["check n=0", "check n=1"]),
        _round_reply(claims=[("lem3", "L3")], bottleneck="assemble"),
    ])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T",
                          max_rounds=3)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert [stage for stage, _ in runner.calls] == [
        "branch:b1", "branch:b1:round2", "branch:b1:round3"]
    assert {p["claim_id"] for p in out.claim_proposals} == {
        "goal", "lem1", "lem2", "lem3"}
    assert out.falsifiers == ["check n=0", "check n=1"]
    assert out.bottleneck == "assemble"


def test_stagnant_round_stops_early():
    runner = PromptRecordingRunner([
        _round_reply(claims=[("lem1", "L1")], open_subgoals=["close L2"]),
        # Round 2 repeats the same claim (deduped -> nothing new) and reports
        # no open subgoals: the branch must stop instead of burning round 3.
        _round_reply(claims=[("lem1", "L1")]),
        _round_reply(claims=[("lem9", "never reached")]),
    ])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T",
                          max_rounds=3)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert len(runner.calls) == 2
    assert "lem9" not in {p["claim_id"] for p in out.claim_proposals}


def test_continuation_prompt_carries_ledger_subgoals_objections_and_memory():
    runner = PromptRecordingRunner([
        _round_reply(claims=[("lem1", "the key lemma")],
                     open_subgoals=["bound the second moment"],
                     falsifiers=["objection: variance blow-up"]),
        _round_reply(claims=[("lem2", "L2")]),
    ])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal",
                          goal_formula="THE TARGET", max_rounds=2)
    worker.failed_approach_memory.append("b0: greedy packing dead end")
    worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    _, round2_prompt = runner.calls[1]
    assert "THE TARGET" in round2_prompt
    assert "lem1" in round2_prompt and "the key lemma" in round2_prompt
    assert "bound the second moment" in round2_prompt
    assert "objection: variance blow-up" in round2_prompt
    assert "greedy packing dead end" in round2_prompt
    assert "REPLACE" in round2_prompt
    # Later rounds must never relax the no-self-verification boundary.
    assert "Do NOT assert the target is proved" in round2_prompt


def test_malformed_later_round_preserves_earlier_rounds():
    runner = PromptRecordingRunner([
        _round_reply(claims=[("lem1", "L1")], open_subgoals=["more"]),
        "not json at all", "still not json",
    ])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T",
                          max_rounds=3)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert {p["claim_id"] for p in out.claim_proposals} == {"goal", "lem1"}
    assert any(f.startswith("unparseable_model_output") for f in out.failures)


def test_malformed_first_round_still_returns_goal_only():
    runner = PromptRecordingRunner(["nope", "nope"])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T",
                          max_rounds=3)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert [p["claim_id"] for p in out.claim_proposals] == ["goal"]
    assert worker.failed_approach_memory  # recorded for the next branch


def test_open_subgoals_enter_failed_approach_memory_and_are_shared_by_role_views():
    runner = PromptRecordingRunner([
        _round_reply(claims=[("lem1", "L1")], open_subgoals=["unclosed gap"]),
    ])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T")
    worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert any("unclosed gap" in entry for entry in worker.failed_approach_memory)
    view = worker.for_role("experimentalist")
    assert view.failed_approach_memory is worker.failed_approach_memory


def test_experiment_cap_is_shared_across_rounds():
    worker = RunnerWorker(runner=PromptRecordingRunner([]), goal_claim_id="goal",
                          goal_formula="T", compute_service=object())
    # already_executed at the cap: the loop must break before any service call
    # (compute_service here is a sentinel that would explode if touched).
    evidence, replays = worker._run_experiments(
        [{"description": "d", "kind": "k", "code": "def experiment(inputs): ..."}],
        branch_id="b1", seen={"goal"}, failures=[], already_executed=3)
    assert evidence == [] and replays == []


def test_formal_target_appears_in_both_prompt_kinds():
    lean = "theorem erdos_336 : ∀ r, ... := by sorry"
    first = branch_prompt("S", role="prover", branch_id="b1", packet_summary="",
                          formal_target=lean)
    later = continuation_prompt(
        "S", role="prover", branch_id="b1", round_index=2, ledger_summary="",
        open_subgoals=[], objections=[], failed_approaches=[], formal_target=lean)
    for prompt in (first, later):
        assert "COMMUNITY-REVIEWED FORMAL TARGET" in prompt
        assert lean in prompt
        assert "untrusted for" in prompt  # never truth authority
    bare = branch_prompt("S", role="prover", branch_id="b1", packet_summary="")
    assert "COMMUNITY-REVIEWED FORMAL TARGET" not in bare
