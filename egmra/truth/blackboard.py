"""Authenticated least-privilege blackboard over the claim graph."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from types import MappingProxyType
from typing import Any, Mapping

from egmra.agents.authorities import AuthorityToken, AuthorityTokenIssuer
from egmra.provenance.hashing import canonical_json, content_id
from egmra.truth.entities import TruthStatus
from egmra.truth.graph import EpistemicGraph


def _deep_frozen(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _deep_frozen(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_deep_frozen(item) for item in value)
    return value


@dataclass(frozen=True)
class ReadSlice:
    interpretation_id: str
    goal_claim_ids: tuple[str, ...]
    visible_claims: Mapping[str, Mapping[str, Any]]
    usable_premises: tuple[str, ...]
    packet_hash: str
    packet: Mapping[str, Any]


PROPOSAL_KINDS = frozenset({
    "claim_proposal", "evidence_proposal", "counterexample", "source_import",
    "experiment_request", "formal_artifact", "next_experiment", "falsifier",
    "bottleneck", "defect_report",
})

PROPOSALS_BY_AUTHORITY: dict[str, frozenset[str]] = {
    "intake_retrieval": frozenset({"claim_proposal", "source_import", "bottleneck"}),
    "program_worker": frozenset({
        "claim_proposal", "evidence_proposal", "experiment_request", "next_experiment",
        "falsifier", "bottleneck",
    }),
    "computational_falsifier": frozenset({
        "counterexample", "experiment_request", "next_experiment", "falsifier",
    }),
    "formalization_authority": frozenset({"formal_artifact", "evidence_proposal", "bottleneck"}),
    "adversarial_referee": frozenset({"counterexample", "defect_report", "bottleneck"}),
}


class BlackboardError(RuntimeError):
    pass


@dataclass
class Blackboard:
    graph: EpistemicGraph
    authority_guard: AuthorityTokenIssuer | None = None
    proposals: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.authority_guard is None:
            self.authority_guard = AuthorityTokenIssuer()

    def _require_token(
        self, token: AuthorityToken | None, *, action: str, resource: str | None = None,
    ) -> AuthorityToken:
        if token is None:
            raise BlackboardError("an authenticated authority token is required")
        guard = self.authority_guard
        if guard is None:
            raise BlackboardError("authority verifier is unavailable")
        return guard.verify(token, action=action, resource=resource)

    def read_slice(
        self, *, branch_id: str, packet_hash: str = "", packet: dict[str, Any] | None = None,
        token: AuthorityToken | None = None,
    ) -> ReadSlice:
        principal = self._require_token(
            token, action="read_branch_slice", resource=f"branch:{branch_id}"
        )
        del principal
        branch = self.graph.branches.get(branch_id)
        if branch is None:
            raise BlackboardError(f"unknown branch {branch_id}")
        packet_value = packet or {}
        try:
            actual_packet_hash = content_id(packet_value)
        except Exception as exc:
            raise BlackboardError(f"packet cannot be canonicalized: {exc}") from exc
        if packet_hash != actual_packet_hash:
            raise BlackboardError("packet hash does not match packet content")
        self._require_token(token, action="read_branch_slice", resource=f"packet:{packet_hash}")

        goal_ids = tuple(branch.goal_claim_ids)
        visible: dict[str, dict] = {}
        frontier = list(goal_ids)
        seen: set[str] = set()
        while frontier:
            cid = frontier.pop()
            if cid in seen or cid not in self.graph.claims:
                continue
            seen.add(cid)
            claim = self.graph.claims[cid]
            visible[cid] = self._public_projection(claim)
            frontier.extend(claim.dependencies)
        usable = tuple(
            cid for cid in sorted(seen)
            if self.graph.claims[cid].truth_status == TruthStatus.SUPPORTED
        )
        return ReadSlice(
            interpretation_id=branch.interpretation_id,
            goal_claim_ids=goal_ids,
            visible_claims=_deep_frozen(visible),
            usable_premises=usable,
            packet_hash=packet_hash,
            packet=_deep_frozen(json.loads(canonical_json(packet_value))),
        )

    @staticmethod
    def _public_projection(claim) -> dict:
        return {
            "claim_id": claim.claim_id,
            "canonical_formula": claim.canonical_formula,
            "informal_text": claim.informal_text,
            "scope": claim.scope,
            "truth_status": str(claim.truth_status),
            "evidence_profile": claim.evidence_profile.to_dict(),
            "assumptions": list(claim.assumptions),
            "dependencies": list(claim.dependencies),
        }

    def write_proposal(
        self, proposal: dict[str, Any], *, token: AuthorityToken | None = None,
    ) -> dict[str, Any]:
        if not isinstance(proposal, dict):
            raise BlackboardError("proposal must be an object")
        kind = proposal.get("kind")
        if kind not in PROPOSAL_KINDS:
            raise BlackboardError(f"unknown proposal kind: {kind!r}")
        branch_id = proposal.get("branch_id")
        if not isinstance(branch_id, str) or branch_id not in self.graph.branches:
            raise BlackboardError("proposal must reference an existing branch")
        principal = self._require_token(
            token, action="write_proposal", resource=f"branch:{branch_id}"
        )
        if kind not in PROPOSALS_BY_AUTHORITY.get(principal.authority_name, frozenset()):
            raise BlackboardError(
                f"authority {principal.authority_name} cannot submit {kind!r}"
            )
        if "truth_status" in proposal or "evidence_profile" in proposal:
            raise BlackboardError("proposals may not assert epistemic status")
        try:
            stored = json.loads(canonical_json(proposal))
        except Exception as exc:
            raise BlackboardError(f"proposal is not canonicalizable: {exc}") from exc
        stored["_submitted_by"] = principal.subject
        stored["_authority"] = principal.authority_name
        self.proposals.append(stored)
        return json.loads(canonical_json(proposal))

    def pending(
        self, kind: str | None = None, *, token: AuthorityToken | None = None,
    ) -> list[dict[str, Any]]:
        principal = self._require_token(token, action="read_own_proposals")
        selected = [
            proposal for proposal in self.proposals
            if proposal.get("_submitted_by") == principal.subject
            and (kind is None or proposal.get("kind") == kind)
        ]
        return [
            {key: value for key, value in proposal.items() if not key.startswith("_")}
            for proposal in selected
        ]
