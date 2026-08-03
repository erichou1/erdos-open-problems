"""Adversarial authorization and least-privilege blackboard tests."""

from __future__ import annotations

from dataclasses import replace

import pytest

from egmra.agents import AuthorityError, AuthorityTokenIssuer
from egmra.provenance.hashing import content_id, sha256_hex
from egmra.truth import Branch, EpistemicGraph, EventLog, Interpretation, Problem
from egmra.truth.blackboard import Blackboard, BlackboardError


ACTOR = {"type": "service", "id": "truth-test"}


class _Clock:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


def _graph(tmp_path) -> EpistemicGraph:
    graph = EpistemicGraph(EventLog(tmp_path / "events.jsonl", run_id="auth"))
    graph.add_problem(Problem("p", sha256_hex("p")), actor=ACTOR)
    graph.add_interpretation(Interpretation("i", "p", "forall n, P n"), actor=ACTOR)
    graph.propose_claim(
        claim_id="goal", interpretation_id="i", canonical_formula="P", actor=ACTOR
    )
    graph.propose_claim(
        claim_id="secret", interpretation_id="i", canonical_formula="Q", actor=ACTOR
    )
    graph.add_branch(Branch(branch_id="b", goal_claim_ids=["goal"], interpretation_id="i"), actor=ACTOR)
    graph.add_branch(Branch(branch_id="other", goal_claim_ids=["secret"], interpretation_id="i"), actor=ACTOR)
    return graph


def _token(issuer: AuthorityTokenIssuer, packet_hash: str):
    return issuer.issue(
        authority_name="program_worker",
        subject="worker-1",
        resources=("branch:b", f"packet:{packet_hash}"),
    )


def test_blackboard_requires_authenticated_scoped_caller(tmp_path) -> None:
    clock = _Clock()
    issuer = AuthorityTokenIssuer(now_fn=clock)
    board = Blackboard(_graph(tmp_path), authority_guard=issuer)
    packet = {"sources": [{"id": "s1", "hash": "a" * 64}]}
    packet_hash = content_id(packet)

    with pytest.raises(BlackboardError, match="token"):
        board.read_slice(branch_id="b", packet_hash=packet_hash, packet=packet)

    token = _token(issuer, packet_hash)
    view = board.read_slice(
        branch_id="b", packet_hash=packet_hash, packet=packet, token=token
    )
    assert set(view.visible_claims) == {"goal"}
    assert "secret" not in view.usable_premises

    with pytest.raises(TypeError):
        view.packet["sources"] = []


def test_token_scope_tamper_expiry_and_cross_branch_access_fail(tmp_path) -> None:
    clock = _Clock()
    issuer = AuthorityTokenIssuer(now_fn=clock)
    board = Blackboard(_graph(tmp_path), authority_guard=issuer)
    packet = {"sources": []}
    packet_hash = content_id(packet)
    token = _token(issuer, packet_hash)

    with pytest.raises(AuthorityError):
        board.read_slice(
            branch_id="other", packet_hash=packet_hash, packet=packet, token=token
        )

    forged = replace(token, authority_name="release_auditor")
    with pytest.raises(AuthorityError, match="signature"):
        board.read_slice(
            branch_id="b", packet_hash=packet_hash, packet=packet, token=forged
        )

    clock.t = token.expires_at + 1
    with pytest.raises(AuthorityError, match="expired"):
        board.read_slice(
            branch_id="b", packet_hash=packet_hash, packet=packet, token=token
        )


def test_packet_hash_is_verified_and_proposals_are_authority_limited(tmp_path) -> None:
    issuer = AuthorityTokenIssuer()
    board = Blackboard(_graph(tmp_path), authority_guard=issuer)
    packet = {"sources": []}
    packet_hash = content_id(packet)
    token = _token(issuer, packet_hash)

    with pytest.raises(BlackboardError, match="packet hash"):
        board.read_slice(
            branch_id="b", packet_hash=packet_hash, packet={"sources": ["injected"]}, token=token
        )

    accepted = board.write_proposal(
        {"kind": "claim_proposal", "branch_id": "b", "canonical_formula": "R"},
        token=token,
    )
    assert accepted["canonical_formula"] == "R"
    with pytest.raises(BlackboardError):
        board.write_proposal(
            {"kind": "formal_artifact", "branch_id": "b", "source": "forged"},
            token=token,
        )
    with pytest.raises(AuthorityError):
        board.write_proposal(
            {"kind": "claim_proposal", "branch_id": "other", "canonical_formula": "R"},
            token=token,
        )


def test_program_worker_cannot_receive_release_permission_or_self_approve() -> None:
    issuer = AuthorityTokenIssuer()
    with pytest.raises(AuthorityError, match="not allowed"):
        issuer.issue(
            authority_name="program_worker",
            subject="worker-1",
            permissions=("issue_release",),
            resources=("*",),
        )

    referee = issuer.issue(
        authority_name="adversarial_referee",
        subject="worker-1",
        resources=("branch:b",),
    )
    with pytest.raises(AuthorityError, match="self-approval"):
        issuer.require_independent(
            referee, generator_subjects={"worker-1"}, generator_lineages=set()
        )
