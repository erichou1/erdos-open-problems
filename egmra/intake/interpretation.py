"""Interpretation lattice (spec §6.1, §4.3).

Ambiguous but separable readings coexist as children of the original statement.
Exploration may proceed per node, but *release against "the intended problem" is
blocked* while any interpretation-level ambiguity is unresolved. This directly
implements §4.3 item 3: a statement adversary blocks publication, not necessarily
all exploration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from egmra.intake.statement_ir import Reconciliation, StatementIR
from egmra.provenance.hashing import content_id
from egmra.truth.entities import Interpretation


@dataclass
class InterpretationLattice:
    parent_problem_id: str
    nodes: list[Interpretation] = field(default_factory=list)
    open_ambiguities: list[str] = field(default_factory=list)

    @property
    def release_blocked(self) -> bool:
        """Release against the intended problem is blocked while ambiguities remain
        OR more than one interpretation is active without an approved intent verdict."""
        if self.open_ambiguities:
            return True
        approved = [n for n in self.nodes if n.intent_verdict == "approved"]
        # Multiple materially-different unapproved readings block release.
        return len(self.nodes) > 1 and len(approved) != 1

    @property
    def explorable_nodes(self) -> list[Interpretation]:
        """Every node may be explored, even while release is blocked."""
        return list(self.nodes)

    def approved_interpretation(self) -> Interpretation | None:
        approved = [n for n in self.nodes if n.intent_verdict == "approved"]
        return approved[0] if len(approved) == 1 else None

    def resolve_ambiguity(self, ambiguity: str) -> None:
        self.open_ambiguities = [a for a in self.open_ambiguities if a != ambiguity]

    def approve(self, interpretation_id: str) -> None:
        for node in self.nodes:
            node.intent_verdict = "approved" if node.interpretation_id == interpretation_id else "rejected"

    def to_dict(self) -> dict:
        return {
            "parent_problem_id": self.parent_problem_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "open_ambiguities": list(self.open_ambiguities),
            "release_blocked": self.release_blocked,
        }


def _interp_id(problem_id: str, ir: StatementIR, tag: str) -> str:
    return "int_" + content_id({"p": problem_id, "sem": ir.semantic_key(), "tag": tag})[:16]


def build_interpretation_lattice(
    problem_id: str, reconciliation: Reconciliation
) -> InterpretationLattice:
    """Build the lattice: a primary reading plus a child per material disagreement."""
    primary_ir = reconciliation.primary
    primary = _to_interpretation(problem_id, primary_ir, "primary",
                                 relation="exact" if reconciliation.agreed else "plausible")
    primary.ambiguities_open = list(reconciliation.ambiguity_nodes)
    nodes = [primary]

    if not reconciliation.agreed:
        # The secondary parse is a materially different, separable reading.
        secondary = _to_interpretation(
            problem_id, reconciliation.secondary, "alternative", relation="plausible"
        )
        secondary.ambiguities_open = list(reconciliation.ambiguity_nodes)
        nodes.append(secondary)

    return InterpretationLattice(
        parent_problem_id=problem_id,
        nodes=nodes,
        open_ambiguities=list(reconciliation.ambiguity_nodes),
    )


def _to_interpretation(
    problem_id: str, ir: StatementIR, tag: str, *, relation: str
) -> Interpretation:
    return Interpretation(
        interpretation_id=_interp_id(problem_id, ir, tag),
        parent_problem_id=problem_id,
        normalized_statement=ir.conclusion,
        binders=[b.to_dict() for b in ir.binders],
        hypotheses=list(ir.hypotheses),
        conclusion=ir.conclusion,
        relation_to_parent=relation,
        ambiguities_open=[],
        formal_candidates=[],
        intent_verdict="pending",
    )
