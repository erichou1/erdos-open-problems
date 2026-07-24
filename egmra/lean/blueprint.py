"""L2 — formal blueprint with quarantined `sorry` (spec §9.2 L2).

The proof is represented as Lean declarations with ``sorry`` only inside a
*quarantined* development branch; production evidence never imports that branch.
Each hole is a graph node. Attempt the target directly before decomposing, and
reject helpers that merely restate the target or hide all difficulty.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from egmra.provenance.hashing import content_id, sha256_hex


class BlueprintError(RuntimeError):
    pass


@dataclass(frozen=True)
class FormalHole:
    node_id: str
    source_claim_id: str
    goal_state: str
    expected_premises: tuple[str, ...] = ()
    semantic_invariants: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()


@dataclass
class FormalBlueprint:
    target_declaration: str
    target_statement: str
    holes: list[FormalHole] = field(default_factory=list)
    branch: str = "quarantine"
    direct_attempt_made: bool = False

    def production_imports_quarantine(self) -> bool:
        # Production evidence must never import the quarantine branch.
        return self.branch != "quarantine"

    def add_hole(self, hole: FormalHole) -> FormalHole:
        self.require_direct_first()
        if any(existing.node_id == hole.node_id for existing in self.holes):
            raise BlueprintError(f"duplicate formal hole {hole.node_id}")
        if hole.node_id in hole.dependencies:
            raise BlueprintError(f"formal hole {hole.node_id} cannot depend on itself")
        if self._restates_target(hole):
            raise BlueprintError(
                f"helper {hole.node_id} restates or implies the target; rejected (spec §9.2 L2)"
            )
        self.holes.append(hole)
        return hole

    def _restates_target(self, hole: FormalHole) -> bool:
        target_norm = sha256_hex(_normalize(self.target_statement))
        return sha256_hex(_normalize(hole.goal_state)) == target_norm

    def require_direct_first(self) -> None:
        if not self.direct_attempt_made:
            raise BlueprintError("attempt the target directly before decomposing")

    def to_dict(self) -> dict:
        return {
            "target_declaration": self.target_declaration,
            "branch": self.branch,
            "direct_attempt_made": self.direct_attempt_made,
            "holes": [h.__dict__ | {} for h in self.holes],
            "blueprint_hash": content_id({
                "target": self.target_declaration,
                "holes": [h.node_id for h in self.holes],
            }),
        }


def _normalize(text: str) -> str:
    return " ".join(text.split()).lower()
