"""L4 — informal/formal assembly & synchronization (spec §9.2 L4).

The informal and formal artifacts share claim IDs. Every informal sentence that
does real logical work points to a Lean declaration, a rigorous informal claim
with an explicit formalization-debt marker, or an audited source theorem. Changes
propagate both ways.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SyncLink:
    claim_id: str
    lean_declaration: str = ""
    informal_debt_marker: str = ""
    source_theorem_id: str = ""

    def is_grounded(self) -> bool:
        """A load-bearing sentence must map to exactly one of the three grounds."""
        grounds = [bool(self.lean_declaration), bool(self.informal_debt_marker),
                   bool(self.source_theorem_id)]
        return sum(grounds) == 1


@dataclass
class ProofSync:
    links: dict[str, SyncLink] = field(default_factory=dict)
    invalidated: set[str] = field(default_factory=set)

    def link(self, sync: SyncLink) -> None:
        if not sync.is_grounded():
            raise ValueError(
                f"claim {sync.claim_id} is a load-bearing sentence with no Lean decl, "
                "debt marker, or audited source"
            )
        self.links[sync.claim_id] = sync

    def validate_coverage(self, load_bearing_claim_ids: list[str]) -> list[str]:
        """Return the load-bearing claims lacking any grounding (must be empty)."""
        return [cid for cid in load_bearing_claim_ids
                if cid not in self.links or not self.links[cid].is_grounded()]

    def propagate_formal_change(self, lean_declaration: str) -> list[str]:
        """A formal counterexample/hypothesis change invalidates the prose cone."""
        affected = [cid for cid, link in self.links.items()
                    if link.lean_declaration == lean_declaration]
        self.invalidated.update(affected)
        return affected

    def propagate_informal_change(self, claim_id: str) -> list[str]:
        """An informal clarification invalidates the formal statement until reapproved."""
        self.invalidated.add(claim_id)
        return [claim_id]
