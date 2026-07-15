"""Deep-research efficiency: dossier, targeted literature, obligation dedupe.

Three mechanisms closing the "medium tier" of the CDC/ErdosBench/agentic-erdos
study, all search/efficiency only — the frozen-packet trust boundary, the
kernel, and the gates are untouched:

* research dossier — per-problem learning survives across campaign PROCESSES;
* multi-query packet + refocused continuation literature — the worker can pull
  the theorem it just asked for into view (from the SAME frozen packet);
* obligation dedupe — the same pinned obligation is never paid for twice
  (vendor proof or kernel re-check); failed dispatches release their slot.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

from egmra.orchestrator.dossier import (
    harvest_for_dossier,
    load_dossier,
    seed_from_dossier,
    update_dossier,
)
from egmra.orchestrator.loop import _family_history_lines
from egmra.orchestrator.runner_worker import RunnerWorker, continuation_prompt
from egmra.retrieval.packet import LiteratureQuery
from egmra.retrieval.records import TheoremRecord
from egmra.retrieval.service import RetrievalService
from egmra.tests.test_multi_turn_worker import PromptRecordingRunner, _round_reply


class _Memory:
    def __init__(self, records=()):
        self.procedural = SimpleNamespace(
            records=list(records),
            admit=lambda rec: self.procedural.records.append(rec))


# ---------------------------------------------------------------------------
# dossier


def test_dossier_load_fails_open_on_degenerate_states(tmp_path):
    assert load_dossier(None) == {}
    assert load_dossier(tmp_path / "missing.json") == {}
    bad = tmp_path / "bad.json"
    bad.write_text("not json{")
    assert load_dossier(bad) == {}
    wrong = tmp_path / "wrong.json"
    wrong.write_text(json.dumps({"schema_version": 99}))
    assert load_dossier(wrong) == {}
    real = tmp_path / "real.json"
    real.write_text(json.dumps({"schema_version": 1, "problem_id": "erdos-1"}))
    link = tmp_path / "link.json"
    link.symlink_to(real)
    assert load_dossier(link) == {}
    assert load_dossier(real)["problem_id"] == "erdos-1"


def test_dossier_update_seed_harvest_round_trip(tmp_path):
    path = tmp_path / "d" / "dossier.json"
    memory = _Memory([
        {"kind": "branch_family_outcome", "problem_id": "erdos-1",
         "branch_family": "direct_structural", "supported": False},
    ])
    worker = SimpleNamespace(failed_approach_memory=["b1: dead end via Ramsey"])

    written = update_dossier(path, problem_id="erdos-1",
                             public_state="BLOCKED_BY_INTERPRETATION",
                             harvest=harvest_for_dossier(memory, worker, "erdos-1"))
    assert written["attempts"] == 1
    assert path.stat().st_mode & 0o777 == 0o600

    # A NEW process: seed an empty memory/worker from the stored dossier.
    memory2 = _Memory()
    worker2 = SimpleNamespace(failed_approach_memory=[])
    assert seed_from_dossier(load_dossier(path), memory=memory2, worker=worker2,
                             problem_id="erdos-1") == 1
    assert worker2.failed_approach_memory == ["b1: dead end via Ramsey"]
    # The seeded record feeds the family registry with zero extra plumbing.
    assert any("direct_structural: BLOCKED" in line
               for line in _family_history_lines(memory2, "erdos-1"))
    # Idempotent within one process: a retry does not double-count attempts.
    assert seed_from_dossier(load_dossier(path), memory=memory2, worker=worker2,
                             problem_id="erdos-1") == 0
    # Harvest excludes dossier-seeded records — no inflation loop.
    assert harvest_for_dossier(memory2, worker2, "erdos-1")["family_outcomes"] == []

    # Second attempt merges instead of resetting.
    written2 = update_dossier(path, problem_id="erdos-1", public_state="OPEN_NO_PROGRESS",
                              harvest={"family_outcomes": [
                                  {"branch_family": "formal_library_first",
                                   "supported": True}],
                                  "failed_approaches": []})
    assert written2["attempts"] == 2
    assert written2["terminal_states"] == ["BLOCKED_BY_INTERPRETATION",
                                           "OPEN_NO_PROGRESS"]
    assert len(written2["family_outcomes"]) == 2


def test_dossier_for_other_problem_never_seeds():
    memory = _Memory()
    worker = SimpleNamespace(failed_approach_memory=[])
    assert seed_from_dossier({"schema_version": 1, "problem_id": "erdos-2",
                              "family_outcomes": [{"branch_family": "x"}]},
                             memory=memory, worker=worker,
                             problem_id="erdos-1") == 0
    assert memory.procedural.records == []


# ---------------------------------------------------------------------------
# multi-query packet + refocused continuation literature


def _record(rid, statement):
    return TheoremRecord(theorem_id=rid, canonical_statement=statement,
                         conclusion=statement, source_uri=f"https://ex/{rid}")


def test_build_packet_unions_targeted_extra_queries():
    corpus = [
        _record("t-ramsey", "Ramsey number R(3,t) grows like t squared over log t"),
        _record("t-sidon", "Sidon sets in the integers have size sqrt n"),
        _record("t-beatty", "Beatty sequences partition the natural numbers"),
    ]
    svc = RetrievalService(corpus)
    packet = svc.build_packet(
        LiteratureQuery(problem_contract_hash="h", interpretation_id="i",
                        exact_statements=("Ramsey number growth",)),
        limit=1, extra_queries=("Sidon sets size", "Beatty partition"))
    ids = {r.theorem_id for r in packet.theorem_records}
    assert {"t-ramsey", "t-sidon", "t-beatty"} <= ids
    # Every query is its own auditable event; no duplicate records.
    assert len(packet.query_log) == 3
    assert len(ids) == len(packet.theorem_records)


def test_continuation_round_refocuses_frozen_packet_on_own_queries():
    # 14 filler records ahead of the one the worker will ask for: the default
    # render (12-record cap) cuts it; the round-2 refocus must surface it.
    records = [_record(f"t-fill-{i}", f"unrelated filler lemma number {i} about widgets")
               for i in range(14)]
    records.append(_record(
        "t-needed", "Vinogradov equidistribution of primes in Beatty sequences"))
    packet = SimpleNamespace(theorem_records=tuple(records))
    runner = PromptRecordingRunner([
        _round_reply(claims=[("lem1", "L1")], open_subgoals=["apply Vinogradov"]),
        _round_reply(claims=[("lem2", "L2")]),
    ])
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="T",
                          max_rounds=2)
    # Round-1 reply carries the search query via parsed["search_queries"]:
    reply1 = json.loads(runner._replies[0])
    reply1["search_queries"] = ["Vinogradov equidistribution Beatty"]
    runner._replies[0] = json.dumps(reply1)

    worker.work_branch(None, packet, branch_id="b1", budget=5.0, fencing_token=1)
    round1_prompt = runner.calls[0][1]
    round2_prompt = runner.calls[1][1]
    assert "t-needed" not in round1_prompt.replace("Vinogradov", "")  # cut by cap
    assert "Vinogradov equidistribution of primes" not in round1_prompt
    assert "REFOCUSED LITERATURE" in round2_prompt
    assert "Vinogradov equidistribution of primes" in round2_prompt


def test_continuation_without_queries_or_subgoals_adds_no_literature_block():
    prompt = continuation_prompt("T", role="prover", branch_id="b", round_index=2,
                                 ledger_summary="", open_subgoals=[],
                                 objections=[], failed_approaches=[])
    assert "REFOCUSED LITERATURE" not in prompt


# ---------------------------------------------------------------------------
# obligation dedupe


class _CountingFormalizer:
    formalizer_id = "counting"

    def __init__(self, reply="theorem t : X := trivial", fail_first=0):
        self.calls: list[str] = []
        self.reply = reply
        self.fail_first = fail_first

    def formalize(self, *, declaration_name, **_kw):
        self.calls.append(declaration_name)
        if len(self.calls) <= self.fail_first:
            raise TimeoutError("vendor outage")
        return self.reply


def _worker(formalizer):
    from egmra.agents.runner import DeterministicRunner

    return RunnerWorker(runner=DeterministicRunner(), goal_claim_id="goal",
                        goal_formula="T", lean_version="4.28.0",
                        mathlib_commit="v4.28.0", formalizer=formalizer)


def _cand(decl="erdos_x", typ="True", source=""):
    return {"claim_id": "", "declaration_name": decl, "expected_type": typ,
            "source": source}


def test_same_obligation_is_dispatched_to_the_vendor_once():
    formalizer = _CountingFormalizer()
    worker = _worker(formalizer)
    out1 = worker._build_formal_candidates([_cand()], branch_id="b1",
                                           seen=set(), failures=[])
    # Same obligation again (later round / different branch view): no new call.
    out2 = worker.for_role("skeptic")._build_formal_candidates(
        [_cand()], branch_id="b2", seen=set(), failures=[])
    assert len(formalizer.calls) == 1
    assert len(out1) == 1 and out2 == []


def test_failed_dispatch_releases_the_slot_for_retry():
    formalizer = _CountingFormalizer(fail_first=1)
    worker = _worker(formalizer)
    failures: list[str] = []
    out1 = worker._build_formal_candidates([_cand()], branch_id="b1",
                                           seen=set(), failures=failures)
    assert out1 == [] and any(f.startswith("formalizer_error") for f in failures)
    out2 = worker._build_formal_candidates([_cand()], branch_id="b1",
                                           seen=set(), failures=[])
    assert len(out2) == 1 and len(formalizer.calls) == 2


def test_identical_sourced_candidates_emit_one_kernel_obligation():
    worker = _worker(None)
    src = "theorem erdos_x : True := trivial"
    out1 = worker._build_formal_candidates([_cand(source=src)], branch_id="b1",
                                           seen=set(), failures=[])
    out2 = worker._build_formal_candidates([_cand(source=src)], branch_id="b2",
                                           seen=set(), failures=[])
    assert len(out1) == 1 and out2 == []
    # A DIFFERENT proof of the same obligation still emits (repair produces
    # genuinely new sources worth re-checking).
    out3 = worker._build_formal_candidates(
        [_cand(source="theorem erdos_x : True := by trivial")],
        branch_id="b3", seen=set(), failures=[])
    assert len(out3) == 1
