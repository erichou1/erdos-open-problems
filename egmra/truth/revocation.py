"""Transactional revocation with SCC-aware propagation (spec §10.2).

Evidence invalidation and mathematical refutation are different operations:

* :func:`invalidate_evidence` — losing support *downgrades* a claim (an imported
  theorem was corrected, a replay failed, a formal statement changed). The claim
  is not thereby false.
* :func:`refute_claim` — only an exact counterexample or a checked proof of the
  negation makes a claim ``REFUTED`` (or ``CONFLICTED`` if strong same-scope
  support survives).

Both propagate transactionally over the reverse-dependency closure. Because
``EQUIVALENT_TO`` / mutual-reduction edges can form cycles, propagation operates
on the strongly-connected-component (SCC) condensation in reverse-topological
order.
"""

from __future__ import annotations

import copy

from egmra.truth.entities import TruthStatus
from egmra.truth.graph import EpistemicGraph
from egmra.truth.router import EvidenceRouter


class RevocationError(RuntimeError):
    pass


# ── Tarjan SCC ────────────────────────────────────────────────────────────────

def strongly_connected_components(adjacency: dict[str, set[str]]) -> list[list[str]]:
    """Return SCCs of a directed graph in reverse-topological order.

    (Tarjan's algorithm already yields components in reverse-topological order:
    a component is emitted only after all components it can reach.)
    """
    index_counter = [0]
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    result: list[list[str]] = []

    def strongconnect(node: str) -> None:
        indices[node] = index_counter[0]
        lowlink[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)
        for successor in adjacency.get(node, ()):  # noqa: B007
            if successor not in indices:
                strongconnect(successor)
                lowlink[node] = min(lowlink[node], lowlink[successor])
            elif successor in on_stack:
                lowlink[node] = min(lowlink[node], indices[successor])
        if lowlink[node] == indices[node]:
            component: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                component.append(w)
                if w == node:
                    break
            result.append(component)

    for node in adjacency:
        if node not in indices:
            strongconnect(node)
    return result


def _reverse_dependency_closure(graph: EpistemicGraph, roots: list[str]) -> set[str]:
    """All claims reachable from ``roots`` along claim→dependent edges."""
    edges = graph.dependency_edges()  # claim -> {claims that depend on it}
    seen: set[str] = set()
    frontier = list(roots)
    while frontier:
        node = frontier.pop()
        if node in seen:
            continue
        seen.add(node)
        frontier.extend(edges.get(node, ()))
    return seen


def _ordered_components(graph: EpistemicGraph, affected: set[str]) -> list[list[str]]:
    edges = graph.dependency_edges()
    sub = {n: {m for m in edges.get(n, ()) if m in affected} for n in affected}
    # SCCs in reverse-topological order; reverse so dependencies precede dependents.
    return list(reversed(strongly_connected_components(sub)))


def invalidate_evidence(
    graph: EpistemicGraph, router: EvidenceRouter, evidence_id: str, *, reason: str, actor: dict
) -> set[str]:
    """Mark evidence invalid and propagate downgrades. Returns affected claims."""
    evidence = graph.evidence.get(evidence_id)
    if evidence is None:
        raise RevocationError(f"unknown evidence {evidence_id}")
    invalidated = copy.deepcopy(evidence)
    prior_version = invalidated.status_version
    invalidated.valid = False
    invalidated.invalidation_reason = reason
    invalidated.status_version = prior_version + 1
    graph.log.append(
        action="EVIDENCE_INVALIDATED", actor=actor,
        object_ids=[evidence_id, *evidence.claim_ids], reason_code="EVIDENCE_INVALIDATED",
        prior_versions={evidence_id: prior_version},
        new_versions={evidence_id: invalidated.status_version},
        human_readable_reason=reason,
        payload={"evidence": invalidated.to_dict()},
    )
    graph.evidence[evidence_id] = invalidated
    roots = graph.claims_supported_by(evidence_id) or list(evidence.claim_ids)
    affected = _reverse_dependency_closure(graph, roots)
    for component in _ordered_components(graph, affected):
        for claim_id in component:
            router.revalidate(claim_id, actor=actor)
            _pause_publication_and_reopen(graph, claim_id, actor=actor)
    return affected


def refute_claim(
    graph: EpistemicGraph, router: EvidenceRouter, claim_id: str, *,
    counterevidence_id: str, actor: dict,
) -> set[str]:
    """Refute a claim with a checked counterexample/negation and propagate."""
    claim = graph.claims.get(claim_id)
    if claim is None:
        raise RevocationError(f"unknown claim {claim_id}")
    counter = graph.evidence.get(counterevidence_id)
    if counter is None or counterevidence_id not in claim.evidence_ids:
        raise RevocationError("counterevidence must be attached to the claim")
    # The counterexample's own validation decides REFUTED vs CONFLICTED via revalidate.
    router.revalidate(claim_id, actor=actor)
    if graph.claims[claim_id].truth_status not in (TruthStatus.REFUTED, TruthStatus.CONFLICTED):
        raise RevocationError(
            "refute_claim requires an admitted exact counterexample or checked negation"
        )
    affected = _reverse_dependency_closure(graph, [claim_id])
    for component in _ordered_components(graph, affected):
        for cid in component:
            if cid == claim_id:
                continue
            router.revalidate(cid, actor=actor)
            _pause_publication_and_reopen(graph, cid, actor=actor)
    return affected


def _pause_publication_and_reopen(graph: EpistemicGraph, claim_id: str, *, actor: dict) -> None:
    """Reopen any branch whose goal claim just lost SUPPORTED status."""
    claim = graph.claims[claim_id]
    if claim.truth_status == TruthStatus.SUPPORTED:
        return
    for branch in graph.branches.values():
        if claim_id in branch.goal_claim_ids and branch.status in ("paused", "closed"):
            graph.set_branch_status(
                branch.branch_id, "active", reason="dependency_revocation", actor=actor
            )
