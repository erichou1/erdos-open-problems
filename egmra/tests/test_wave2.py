"""Wave 2 search-effectiveness improvements (effectiveness report R3/R6/R9/R12).

Pins four behaviors:

* R9 identity corroboration — literature corroboration counts independent
  mathematical SOURCES (arXiv id / DOI), not web hosts: two mirrors of one
  paper are one source.
* R9 packet re-entry — ``SourcePacket.reentry`` versions are chained and the
  ``PACKET_REENTRY`` action is a whitelisted, appendable event.
* R3 phase 1 — workers RETURN their unclosed subgoals; the round-1 branch
  prompt renders subgoals carried over from prior branches.
* R6 dispatch gate — per branch, only the most valuable source-less
  obligations dispatch to the vendor (goal first, then dependency
  centrality); deferrals are recorded and release their dedupe slot.
* R12 — ``escalation-packet`` renders one bounded, read-only expert packet.
"""

from __future__ import annotations

import json

from egmra.agents.runner import RunnerResponse
from egmra.cli import main
from egmra.orchestrator.loop import _source_identity
from egmra.orchestrator.runner_worker import RunnerWorker, branch_prompt
from egmra.provenance.hashing import sha256_hex
from egmra.provenance.stage_identity import AttestedModelIdentity
from egmra.retrieval.records import TheoremRecord
from egmra.retrieval.packet import SourcePacket
from egmra.truth.events import ACTIONS, EventLog


# ── R9: corroboration by mathematical source identity ────────────────────────

def test_source_identity_canonicalizes_arxiv_mirrors_and_doi():
    # abs page, pdf, and a mirror host are ONE source.
    assert _source_identity("https://arxiv.org/abs/2401.00001") == "arxiv:2401.00001"
    assert _source_identity("https://arxiv.org/pdf/2401.00001.pdf") == "arxiv:2401.00001"
    assert _source_identity("http://export.arxiv.org/abs/2401.00001") == "arxiv:2401.00001"
    assert _source_identity("https://doi.org/10.1000/XYZ") == "doi:10.1000/xyz"
    # No canonical identity → host fallback (old behavior preserved).
    assert _source_identity("https://example.com/paper") == "host:example.com"


def test_mirrors_of_one_paper_are_not_corroboration():
    # Distinct HOSTS, same paper: under the old host rule this corroborated.
    identities = {
        _source_identity("https://arxiv.org/abs/2401.00001"),
        _source_identity("http://export.arxiv.org/abs/2401.00001v2"),
    }
    assert len(identities) == 1
    # Genuinely independent sources still count as two.
    independent = {
        _source_identity("https://arxiv.org/abs/2401.00001"),
        _source_identity("https://doi.org/10.1000/other"),
    }
    assert len(independent) == 2


# ── R9: packet re-entry is versioned, chained, and auditable ─────────────────

def _record(theorem_id: str) -> TheoremRecord:
    return TheoremRecord(
        theorem_id=theorem_id, canonical_statement=f"statement {theorem_id}",
        hypotheses=(), conclusion="C", source_uri=f"https://example.com/{theorem_id}",
    )


def test_packet_reentry_event_is_whitelisted_and_chained(tmp_path):
    assert "PACKET_REENTRY" in ACTIONS
    base = SourcePacket(packet_id="pkt-1", theorem_records=(_record("t1"),))
    extended = base.reentry(new_records=[_record("t2")],
                            reason="branch queries named a missing lemma",
                            new_packet_id="pkt-1-r1")
    assert extended.predecessor_packet_id == "pkt-1"
    assert {r.theorem_id for r in extended.theorem_records} == {"t1", "t2"}
    # The signed audit event for the re-entry appends cleanly.
    log = EventLog(tmp_path / "events.jsonl", run_id="wave2")
    event = log.append(
        action="PACKET_REENTRY", actor={"id": "test"}, object_ids=["erdos-1"],
        reason_code="retrieval_reentry",
        human_readable_reason="packet re-entry after direct_structural",
        payload={"parent_packet_hash": base.packet_hash(),
                 "new_packet_hash": extended.packet_hash(),
                 "queries": ["missing lemma"],
                 "added_theorem_ids": ["t2"]},
    )
    assert event.payload["parent_packet_hash"] != event.payload["new_packet_hash"]


# ── R3 phase 1: subgoals flow out of workers and into later branch prompts ───

class PromptRecordingRunner:
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


def _round_reply(*, claims=(), open_subgoals=(), candidates=()):
    return json.dumps({
        "goal_restatement": "restated",
        "claims": [
            {"claim_id": cid, "statement": statement, "depends_on": list(deps),
             "scope": "general", "confidence": 0.5}
            for cid, statement, deps in claims
        ],
        "falsifiers": [], "search_queries": [], "candidate_sequences": [],
        "experiments": [], "formalization_requests": [],
        "lean_declaration_candidates": list(candidates),
        "open_subgoals": list(open_subgoals),
        "bottleneck": "", "confidence": 0.5,
    })


def test_work_branch_returns_open_subgoals():
    runner = PromptRecordingRunner([_round_reply(
        claims=[("lem1", "L1", [])], open_subgoals=["close the density gap"])])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T")
    out = worker.work_branch(None, None, branch_id="b1", budget=5.0, fencing_token=1)
    assert out.open_subgoals == ["close the density gap"]


def test_branch_prompt_renders_carried_subgoals_and_worker_passes_them():
    text = branch_prompt("Statement.", role="prover", branch_id="b2",
                         packet_summary="", carried_subgoals=["close the gap"])
    assert "OPEN SUBGOALS FROM PRIOR BRANCHES" in text
    assert "- close the gap" in text
    # Absent when nothing is carried.
    empty = branch_prompt("Statement.", role="prover", branch_id="b2",
                          packet_summary="")
    assert "OPEN SUBGOALS FROM PRIOR BRANCHES" not in empty
    # The worker feeds its carried_subgoals field into round 1.
    runner = PromptRecordingRunner([_round_reply()])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T",
                          carried_subgoals=["close the gap"])
    worker.work_branch(None, None, branch_id="b3", budget=5.0, fencing_token=1)
    assert "close the gap" in runner.calls[0][1]
    # Role views share the same list object, so orchestrator updates propagate.
    assert worker.for_role("skeptic").carried_subgoals is worker.carried_subgoals


# ── R6: value-aware formalization dispatch gate ──────────────────────────────

class _OkFormalizer:
    formalizer_id = "ok"

    def __init__(self):
        self.dispatched: list[str] = []

    def formalize(self, *, declaration_name, expected_type,
                  informal_statement, previous_source="", kernel_feedback=""):
        self.dispatched.append(declaration_name)
        return f"theorem {declaration_name} : {expected_type} := trivial"


def _gate_worker(cap: int | None = None) -> tuple[RunnerWorker, _OkFormalizer]:
    formalizer = _OkFormalizer()
    kwargs = {} if cap is None else {"max_formalizations_per_branch": cap}
    return RunnerWorker(runner=PromptRecordingRunner([]), goal_claim_id="goal",
                        goal_formula="T", lean_version="4.28.0",
                        mathlib_commit="v4.28.0", formalizer=formalizer,
                        **kwargs), formalizer


def test_dispatch_gate_defers_beyond_cap_and_records_deferrals():
    worker, formalizer = _gate_worker(cap=2)
    candidates = [{"claim_id": "", "declaration_name": f"decl_{i}",
                   "expected_type": f"Type{i}", "source": ""} for i in range(5)]
    failures: list[str] = []
    out = worker._build_formal_candidates(candidates, branch_id="b1",
                                          seen=set(), failures=failures)
    assert len(out) == 2 and len(formalizer.dispatched) == 2
    deferred = [f for f in failures if f.startswith("formalization_deferred:b1:")]
    assert len(deferred) == 3
    # Deferred obligations release their dedupe slot: a later round may dispatch.
    failures2: list[str] = []
    out2 = worker._build_formal_candidates([candidates[4]], branch_id="b1",
                                           seen=set(), failures=failures2)
    assert len(out2) == 1 and failures2 == []


def test_dispatch_gate_prioritizes_goal_then_dependency_centrality():
    worker, formalizer = _gate_worker(cap=2)
    candidates = [
        {"claim_id": "lem_a", "declaration_name": "decl_a",
         "expected_type": "A", "source": ""},
        {"claim_id": "lem_b", "declaration_name": "decl_b",
         "expected_type": "B", "source": ""},
        {"claim_id": "", "declaration_name": "decl_goal",
         "expected_type": "G", "source": ""},
    ]
    failures: list[str] = []
    out = worker._build_formal_candidates(
        candidates, branch_id="b1", seen={"lem_a", "lem_b"}, failures=failures,
        dependency_counts={"lem_b": 3, "lem_a": 0})
    kept = {c["declaration_name"] for c in out}
    # Goal obligation always dispatches; the central lemma beats the leaf.
    assert kept == {"decl_goal", "decl_b"}
    assert any("decl_a" in f for f in failures)


def test_default_cap_keeps_existing_three_candidate_behavior():
    worker, formalizer = _gate_worker()
    candidates = [{"claim_id": "", "declaration_name": f"decl_{i}",
                   "expected_type": f"T{i}", "source": ""} for i in range(3)]
    failures: list[str] = []
    out = worker._build_formal_candidates(candidates, branch_id="b1",
                                          seen=set(), failures=failures)
    assert len(out) == 3 and failures == []


# ── R12: bounded expert-escalation packet ────────────────────────────────────

def test_escalation_packet_renders_bounded_question(tmp_path, capsys):
    dossier_dir = tmp_path / "ckpts" / "erdos-312"
    dossier_dir.mkdir(parents=True)
    (dossier_dir / "dossier.json").write_text(json.dumps({
        "schema_version": 1, "problem_id": "erdos-312", "attempts": 3,
        "terminal_states": ["BLOCKED_BY_INTERPRETATION"],
        "family_outcomes": [], "failed_approaches": [],
    }))
    rc = main(["escalation-packet", "--erdos", "312",
               "--runs", str(tmp_path / "runs"),
               "--checkpoint-dir", str(tmp_path / "ckpts")])
    assert rc == 0
    packet = json.loads(capsys.readouterr().out)
    assert packet["problem_id"] == "erdos-312"
    assert packet["attempts"] == 3
    assert "interpretation" in packet["question"].lower()
    assert "signed-review" in packet["note"]
    # Read-only: nothing was written anywhere.
    assert not (tmp_path / "runs").exists()


def test_escalation_packet_without_dossier_still_asks_one_question(tmp_path, capsys):
    rc = main(["escalation-packet", "--erdos", "312",
               "--runs", str(tmp_path / "runs")])
    assert rc == 0
    packet = json.loads(capsys.readouterr().out)
    assert packet["question"]
    assert packet["statement"]
