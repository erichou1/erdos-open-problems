"""Regression tests for the two defects observed in the LIVE shared campaign.

Both were found by auditing the running campaign's Neon state, where problems
failed with infrastructure errors that burned mathematical attempts:

* ``AuthorityError: authority token has expired`` — the per-branch worker
  token (300s TTL) was issued BEFORE ``work_branch`` and used for writes
  AFTER it; every browser branch longer than five minutes crashed at write
  time. Elapsed-time staleness is the lease's job (heartbeat + fence); the
  fix issues a fresh short-lived write-phase token once the fence validates
  the batch.
* ``GraphError: duplicate problem`` — re-initializing a campaign under the
  same name (the documented fresh-relaunch flow) restarts the fencing
  counter, so attempt ids collided with the previous incarnation's and the
  stale event log was REPLAYED into the new run's graph. Attempt ids now
  carry a unique suffix.
"""

from __future__ import annotations

import time

import egmra.orchestrator.loop as loop_mod
from egmra.agents.authorities import AuthorityTokenIssuer
from egmra.cli import _campaign_attempt_id
from egmra.orchestrator.loop import WorkerOutput, research
from egmra.tests.test_gap_closures import TRUE_STATEMENT, _corpus, _enforcer, _status


class _ShortTTLIssuer(AuthorityTokenIssuer):
    """Every token expires almost immediately — a stand-in for hours-long
    branches against the real 300s TTL."""

    def issue(self, **kwargs):
        kwargs["ttl_seconds"] = 0.2
        return super().issue(**kwargs)


class _SlowClaimWorker:
    """Outlives the worker token inside work_branch, then proposes a claim."""

    def cold_pass(self, contract, *, budget):
        return WorkerOutput(falsifiers=["check small cases"],
                            search_queries=["smallest cases"])

    def work_branch(self, contract, packet, *, branch_id, budget,
                    fencing_token, branch_slice=None):
        time.sleep(0.3)                      # pre-branch token is now expired
        return WorkerOutput(claim_proposals=[{
            "claim_id": f"{branch_id}_lemma",
            "canonical_formula": f"subsidiary fact via {branch_id}",
            "informal_text": "",
            "scope": "general",
            "dependencies": [],
        }])


def test_branch_outliving_the_worker_token_still_lands_its_proposals(
        tmp_path, monkeypatch):
    monkeypatch.setattr(loop_mod, "AuthorityTokenIssuer", _ShortTTLIssuer)
    result = research(
        problem_id="token-ttl", source_bytes=TRUE_STATEMENT,
        source_id="token-ttl", budget=40.0, enforcer=_enforcer(),
        worker=_SlowClaimWorker(), goal_claim_id="goal",
        events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), status_claims=_status("token-ttl"),
        max_iterations=1,
    )
    # Before the fix this run CRASHED with AuthorityError at the first
    # post-branch write. Now the branch's batch is consumed normally.
    assert any(cid.endswith("_lemma") for cid in result.graph.claims)
    assert not any("authority token has expired" in f for f in result.failures)


def test_campaign_attempt_ids_never_collide_across_incarnations():
    first = _campaign_attempt_id("shared-current-v1", "erdos-153", 3)
    second = _campaign_attempt_id("shared-current-v1", "erdos-153", 3)
    assert first != second                       # same name+token, fresh id
    prefix = "camp-"
    assert first.startswith(prefix) and ".erdos-153.3." in first
