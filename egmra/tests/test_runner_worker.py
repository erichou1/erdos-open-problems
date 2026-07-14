"""Tests for the runner-backed worker (model responses -> WorkerOutput)."""

from __future__ import annotations

import json

from egmra.agents.runner import RunnerResponse
from egmra.orchestrator.runner_worker import RunnerWorker, StructuredDemoRunner
from egmra.provenance.hashing import sha256_hex
from egmra.provenance.stage_identity import AttestedModelIdentity


class ScriptedRunner:
    """A ModelRunner returning canned text keyed by stage (with retry support)."""

    def __init__(self, by_stage):
        self.runner_id = "scripted"
        self._by_stage = by_stage
        self.calls = []

    def run(self, prompt, *, stage):
        self.calls.append(stage)
        value = self._by_stage.get(stage, self._by_stage.get("*", ""))
        text = value.pop(0) if isinstance(value, list) else value
        return RunnerResponse(
            text=text,
            model=AttestedModelIdentity(provider="local", model="scripted",
                                        ui_surface="test", account_class="local"),
            context_id=sha256_hex(f"scripted:{stage}"),
            prompt_hash=sha256_hex(prompt),
        )


_VALID_BRANCH = json.dumps({
    "goal_restatement": "the target restated",
    "claims": [
        {"claim_id": "lemma1", "statement": "a helpful lemma", "depends_on": [],
         "scope": "general", "confidence": 0.5},
        {"claim_id": "goal", "statement": "attempt to hijack the goal", "depends_on": []},
    ],
    "falsifiers": ["check n=1"],
    "search_queries": ["subset-sum lower bounds"],
    "candidate_sequences": [[1, 2, 4, 8]],
    "experiments": [{"description": "enumerate small cases", "kind": "finite_enumeration"}],
    "bottleneck": "need a counting bound",
    "confidence": 0.4,
})


def _worker(by_stage, **kw):
    return RunnerWorker(runner=ScriptedRunner(by_stage), goal_claim_id="goal",
                        goal_formula="THE LOCKED TARGET", **kw)


def test_cold_pass_parses_hypotheses_only():
    cold = json.dumps({"falsifiers": ["small cases"], "search_queries": ["q1"],
                       "bottleneck": "no literature yet", "confidence": 0.1})
    worker = _worker({"cold_pass": cold})
    out = worker.cold_pass(None, budget=1.0)
    assert out.falsifiers == ["small cases"]
    assert out.search_queries == ["q1"]
    assert out.claim_proposals == []      # a cold pass proposes no claims
    assert out.evidence == []             # and never any evidence


def test_work_branch_converts_model_output_to_claims():
    worker = _worker({"branch:b1": _VALID_BRANCH})
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    ids = [p["claim_id"] for p in out.claim_proposals]
    # The goal is always tracked as the locked target; a model-proposed lemma is kept.
    assert "goal" in ids
    assert any(cid != "goal" for cid in ids)
    goal_prop = next(p for p in out.claim_proposals if p["claim_id"] == "goal")
    assert goal_prop["canonical_formula"] == "THE LOCKED TARGET"  # not model prose
    assert out.search_queries == ["subset-sum lower bounds"]
    assert out.generated_sequences == [[1, 2, 4, 8]]
    # A text model NEVER produces proof/verification evidence.
    assert out.evidence == []


def test_model_cannot_hijack_the_goal_claim_formula():
    worker = _worker({"branch:b1": _VALID_BRANCH})
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    goal_props = [p for p in out.claim_proposals if p["claim_id"] == "goal"]
    assert len(goal_props) == 1
    assert goal_props[0]["canonical_formula"] == "THE LOCKED TARGET"


def test_malformed_output_is_rejected_not_treated_as_progress():
    # Two malformed replies (original + repair) -> rejection, no lemma claims.
    worker = _worker({"branch:b1": ["not json", "still not json"]}, max_repair_attempts=1)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert [p["claim_id"] for p in out.claim_proposals] == ["goal"]  # only the tracked target
    assert out.evidence == []
    assert any(f.startswith("unparseable_model_output") for f in out.failures)


def test_malformed_then_valid_after_repair():
    worker = _worker({"branch:b1": ["garbage", _VALID_BRANCH]}, max_repair_attempts=1)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert any(cid != "goal" for cid in [p["claim_id"] for p in out.claim_proposals])
    assert any(f.startswith("malformed_model_output") for f in out.failures)


def test_referee_pass_merges_objections_without_approving():
    referee_reply = json.dumps({"falsifiers": ["lemma1 is unproven"],
                                "bottleneck": "claims need verification"})
    worker = RunnerWorker(
        runner=ScriptedRunner({"branch:b1": _VALID_BRANCH}),
        goal_claim_id="goal", goal_formula="T",
        referee=ScriptedRunner({"referee": referee_reply}),
    )
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert "lemma1 is unproven" in out.falsifiers
    assert out.evidence == []  # a referee never manufactures evidence either


def test_structured_demo_runner_emits_parseable_output():
    worker = RunnerWorker(runner=StructuredDemoRunner(), goal_claim_id="goal",
                          goal_formula="T")
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert [p["claim_id"] for p in out.claim_proposals][0] == "goal"
    assert len(out.claim_proposals) >= 2   # goal + at least one demo lemma
    assert out.evidence == []
