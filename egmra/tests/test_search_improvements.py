"""Search-side improvements from the CDC-prompt / ErdosBench / agentic-erdos study.

Five mechanisms, all SEARCH guidance — none changes what the referee attacks,
what the gates require, or how evidence is admitted:

* skeptic role — refutation-first branch directive (counterexample families);
* anti-circularity — a near-restatement of the target is rejected mechanically
  and the rule is stated in every proposing prompt;
* problem traps — an adversarial checklist derived from the contract's
  ambiguity nodes + failed integrity probes, rendered into worker prompts;
* approach-family registry — prior blocked routes surfaced to the model;
* attempt-salt — post-outcome retries draw independent samples from the
  exchange cache while crash retries still replay free.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from egmra.agents.exchange_cache import CachedRunner
from egmra.agents.runner import RunnerResponse
from egmra.orchestrator.loop import (
    WORKER_ROLE_BY_FAMILY,
    _derive_problem_traps,
    _family_history_lines,
)
from egmra.orchestrator.runner_worker import (
    RunnerWorker,
    _is_goal_equivalent,
    branch_prompt,
    continuation_prompt,
)
from egmra.provenance.hashing import sha256_hex
from egmra.provenance.stage_identity import AttestedModelIdentity
from egmra.tests.test_multi_turn_worker import PromptRecordingRunner, _round_reply


# ---------------------------------------------------------------------------
# skeptic role (refutation-first)


def test_counterexample_families_map_to_skeptic_role():
    assert WORKER_ROLE_BY_FAMILY["counterexample_model_construction"] == "skeptic"
    assert WORKER_ROLE_BY_FAMILY["contradiction_minimal_counterexample"] == "skeptic"


def test_skeptic_prompt_attacks_the_stated_form():
    prompt = branch_prompt("T", role="skeptic", branch_id="b", packet_summary="")
    assert "Assume the stated form is WRONG" in prompt
    assert "counterexample" in prompt
    # Other roles keep their own directives.
    assert "Assume the stated form is WRONG" not in branch_prompt(
        "T", role="prover", branch_id="b", packet_summary="")


# ---------------------------------------------------------------------------
# anti-circularity


def test_goal_equivalence_flags_restatements_not_lemmas():
    goal = "Every finite bridgeless loopless multigraph has a cycle double cover."
    # Trivial reordering/case change = flagged.
    assert _is_goal_equivalent(
        "every finite loopless bridgeless multigraph has a cycle double cover", goal)
    # A genuinely weaker lemma (new quantifiers/objects) = NOT flagged.
    assert not _is_goal_equivalent(
        "Every cubic bridgeless graph with a proper 3-edge-coloring has a "
        "cycle double cover induced by the color classes.", goal)
    assert not _is_goal_equivalent("", goal)


def test_circular_claim_is_rejected_and_recorded():
    goal = "Every triangle-free graph on n vertices has an independent set of size k."
    runner = PromptRecordingRunner([_round_reply(claims=[
        ("circ", "every triangle-free graph on n vertices has an "
                 "independent set of size k"),
        ("lem1", "Ramsey bound R(3,t) exceeds n implies alpha at least t."),
    ])])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula=goal)
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    ids = {p["claim_id"] for p in out.claim_proposals}
    assert "lem1" in ids and "circ" not in ids
    assert any(f.startswith("circular_claim_rejected:b1:circ")
               for f in out.failures)


def test_anti_circularity_rule_is_stated_in_prompts():
    assert "ANTI-CIRCULARITY RULE" in branch_prompt(
        "T", role="prover", branch_id="b", packet_summary="")
    assert "ANTI-CIRCULARITY RULE" in continuation_prompt(
        "T", role="prover", branch_id="b", round_index=2, ledger_summary="",
        open_subgoals=[], objections=[], failed_approaches=[])


# ---------------------------------------------------------------------------
# problem traps (adversarial checklist from the contract)


def _contract(ambiguities=(), failed_probes=()):
    probes = [SimpleNamespace(name=name, passed=False, detail=detail, reason="")
              for name, detail in failed_probes]
    probes.append(SimpleNamespace(name="ok_probe", passed=True, detail="", reason=""))
    return SimpleNamespace(
        reconciliation=SimpleNamespace(ambiguity_nodes=list(ambiguities)),
        probes=probes)


def test_traps_derived_from_ambiguities_and_failed_probes_only():
    contract = _contract(
        ambiguities=["quantifier order of 'for all n there is k'"],
        failed_probes=[("boundary_enumeration", "no executable predicate")])
    traps = _derive_problem_traps(contract)
    assert len(traps) == 2
    assert "quantifier order" in traps[0] and "BOTH" in traps[0]
    assert "boundary_enumeration" in traps[1] and "degenerate" in traps[1]
    assert _derive_problem_traps(_contract()) == []


def test_traps_render_into_worker_prompts():
    traps = ["ambiguous reading — check both resolutions of: X"]
    prompt = branch_prompt("T", role="prover", branch_id="b", packet_summary="",
                           traps=traps)
    assert "ADVERSARIAL CHECKLIST" in prompt and "resolutions of: X" in prompt
    cont = continuation_prompt("T", role="prover", branch_id="b", round_index=2,
                               ledger_summary="", open_subgoals=[], objections=[],
                               failed_approaches=[], traps=traps)
    assert "ADVERSARIAL CHECKLIST" in cont
    # Absent traps add no block at all.
    assert "ADVERSARIAL CHECKLIST" not in branch_prompt(
        "T", role="prover", branch_id="b", packet_summary="")


# ---------------------------------------------------------------------------
# approach-family registry


class _Memory:
    def __init__(self, records):
        self.procedural = SimpleNamespace(records=list(records))


def test_family_history_marks_blocked_routes_for_this_problem_only():
    memory = _Memory([
        {"kind": "branch_family_outcome", "problem_id": "erdos-1",
         "branch_family": "direct_structural", "supported": False},
        {"kind": "branch_family_outcome", "problem_id": "erdos-1",
         "branch_family": "direct_structural", "supported": False},
        {"kind": "branch_family_outcome", "problem_id": "erdos-1",
         "branch_family": "computational_finite_reduction", "supported": True},
        {"kind": "branch_family_outcome", "problem_id": "erdos-2",
         "branch_family": "formal_library_first", "supported": False},
        {"kind": "other"},
    ])
    lines = _family_history_lines(memory, "erdos-1")
    joined = "\n".join(lines)
    assert "direct_structural: BLOCKED — 2 attempts" in joined
    assert "computational_finite_reduction: produced supported claims" in joined
    assert "formal_library_first" not in joined  # other problem's record
    assert _family_history_lines(memory, "erdos-99") == []


def test_family_history_renders_into_round_one_prompt():
    history = ["direct_structural: BLOCKED — 2 attempts, no supported claims; "
               "reopen only with a materially new mechanism"]
    prompt = branch_prompt("T", role="prover", branch_id="b", packet_summary="",
                           family_history=history)
    assert "APPROACH-FAMILY REGISTRY" in prompt
    assert "materially new ingredient" in prompt


# ---------------------------------------------------------------------------
# attempt-salt (pass@k retries vs crash replay)


class _CountingRunner:
    runner_id = "live"

    def __init__(self):
        self.calls = 0

    def run(self, prompt, *, stage):
        self.calls += 1
        return RunnerResponse(
            text=f"reply {self.calls}",
            model=AttestedModelIdentity(provider="local", model="m",
                                        ui_surface="test", account_class="local"),
            context_id=f"ctx-{self.calls}", prompt_hash=sha256_hex(prompt))


def test_salted_cache_gives_fresh_samples_but_unsalted_replays(tmp_path):
    live = _CountingRunner()
    cache_dir = tmp_path / "exchanges"

    first = CachedRunner(live, cache_dir)               # attempt 1
    crash_retry = CachedRunner(live, cache_dir)         # crash retry: no salt
    fresh_retry = CachedRunner(live, cache_dir,          # post-outcome retry
                               salt="retry-sample-1")

    a = first.run("prove it", stage="branch:b1")
    b = crash_retry.run("prove it", stage="branch:b1")
    assert (a.text, b.text) == ("reply 1", "reply 1")   # byte-identical replay
    assert live.calls == 1 and crash_retry.hits == 1

    c = fresh_retry.run("prove it", stage="branch:b1")
    assert c.text == "reply 2"                          # independent sample
    assert live.calls == 2
    # The fresh sample is itself durably cached under its salted key.
    again = CachedRunner(live, cache_dir, salt="retry-sample-1")
    assert again.run("prove it", stage="branch:b1").text == "reply 2"
    assert live.calls == 2


def test_presalt_cache_entries_still_replay(tmp_path):
    """Entries written before the salt feature (no cache_key field) stay valid."""
    live = _CountingRunner()
    cache_dir = tmp_path / "exchanges"
    cache_dir.mkdir()
    prompt = "old prompt"
    key = sha256_hex(prompt)
    (cache_dir / f"branch_b1.{key}.json").write_text(json.dumps({
        "schema_version": 1, "stage": "branch:b1", "prompt_hash": key,
        "response_hash": sha256_hex("old reply"), "text": "old reply",
        "context_id": "ctx-old",
        "model": {"provider": "local", "model": "m", "version": "",
                  "build_id": "", "ui_surface": "test",
                  "account_class": "local", "attestation": None},
    }))
    cached = CachedRunner(live, cache_dir)
    assert cached.run(prompt, stage="branch:b1").text == "old reply"
    assert live.calls == 0


# ── yield-report telemetry (report R13-core) ─────────────────────────────────

def test_yield_report_computes_ratios_and_fails_open(tmp_path):
    from egmra.orchestrator.yield_report import build_yield_report

    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "a.jsonl").write_text("\n".join([
        json.dumps({"action": "PROBLEM_FROZEN"}),
        json.dumps({"action": "BRANCH_OPENED"}),
        json.dumps({"action": "BRANCH_OPENED"}),
        json.dumps({"action": "CLAIM_PROPOSED"}),
        json.dumps({"action": "MODEL_EXCHANGE_RECORDED"}),
        json.dumps({"action": "EVIDENCE_ATTACHED"}),
        "not json at all",
    ]))
    (runs / "b.jsonl").write_text("\n".join([
        json.dumps({"action": "PROBLEM_FROZEN"}),
        json.dumps({"action": "INTERPRETATION_ADDED"}),
    ]))
    ledger = tmp_path / "outcomes.jsonl"
    ledger.write_text(json.dumps({
        "problem_id": "erdos-1", "public_state": "PARTIAL_PROGRESS",
        "salvage": {"supported": [{"claim_id": "lem1"}]},
    }) + "\n")

    report = build_yield_report(runs, (ledger,))
    assert report["runs"]["files"] == 2
    assert report["runs"]["two_event_runs"] == 1
    assert report["runs"]["runs_with_admissible_evidence"] == 1
    assert report["events_by_action"]["BRANCH_OPENED"] == 2
    assert report["yield"]["evidence_per_100_branches"] == 50.0
    assert report["yield"]["evidence_per_100_model_exchanges"] == 100.0
    assert report["yield"]["progress_outcomes"] == 1
    assert report["yield"]["salvaged_supported_claims"] == 1
    assert report["malformed_lines"] == 1
    # No exchanges recorded -> ratio None, never a division error.
    empty = build_yield_report(tmp_path / "missing", ())
    assert empty["yield"]["evidence_per_100_branches"] is None


def test_yield_report_cli_command(tmp_path, capsys):
    import egmra.cli as cli_module

    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "r.jsonl").write_text(json.dumps({"action": "BRANCH_OPENED"}) + "\n")
    rc = cli_module.main(["yield-report", "--runs", str(runs)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["events_by_action"] == {"BRANCH_OPENED": 1}
    assert "never a truth" in out["note"]
