"""Proof compiler: assemble only from admitted claims (spec §4.2).

The whole-proof constructor is *demoted to a compiler*. It assembles an informal
proof only from admitted (SUPPORTED) claims in the epistemic graph; it never
invents premises and refuses to include UNKNOWN/REFUTED/CONFLICTED claims.
"""

from __future__ import annotations

from dataclasses import dataclass

from egmra.truth.entities import TruthStatus
from egmra.truth.graph import EpistemicGraph


class CompilerError(RuntimeError):
    pass


@dataclass(frozen=True)
class CompiledProof:
    goal_claim_id: str
    steps: tuple[str, ...]
    used_claim_ids: tuple[str, ...]
    complete: bool
    missing: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "goal_claim_id": self.goal_claim_id,
            "steps": list(self.steps),
            "used_claim_ids": list(self.used_claim_ids),
            "complete": self.complete,
            "missing": list(self.missing),
        }


def assemble_from_admitted_graph(graph: EpistemicGraph, goal_claim_id: str) -> CompiledProof:
    """Compile a proof of the goal from admitted claims only, in dependency order."""
    if goal_claim_id not in graph.claims:
        raise CompilerError(f"unknown goal claim {goal_claim_id}")

    ordered: list[str] = []
    missing: list[str] = []
    visiting: set[str] = set()
    done: set[str] = set()

    def visit(cid: str) -> None:
        if cid in done:
            return
        if cid in visiting:
            raise CompilerError(f"dependency cycle at {cid}")
        visiting.add(cid)
        claim = graph.claims.get(cid)
        if claim is None:
            missing.append(cid)
            visiting.discard(cid)
            return
        for dep in claim.dependencies:
            visit(dep)
        visiting.discard(cid)
        done.add(cid)
        # Only admitted (SUPPORTED) claims may enter the assembled proof.
        if claim.truth_status == TruthStatus.SUPPORTED:
            ordered.append(cid)
        else:
            missing.append(cid)

    visit(goal_claim_id)
    steps = tuple(
        f"{cid}: {graph.claims[cid].informal_text or graph.claims[cid].canonical_formula}"
        for cid in ordered
    )
    complete = goal_claim_id in ordered and not missing
    return CompiledProof(
        goal_claim_id=goal_claim_id, steps=steps, used_claim_ids=tuple(ordered),
        complete=complete, missing=tuple(dict.fromkeys(missing)),
    )
