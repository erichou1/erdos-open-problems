"""Risk-weighted formal coverage (RFC) and expensive-claim policy (spec §9.5, §12.3).

RFC is a *rigor metric*, not a truth score, and its weights/blueprint must be
frozen before scoring so a system cannot game it by replacing one hard target
with many easy nodes. Expensive-to-formalize but convincing claims retain an
explicit informal-review tier and never get labeled "formally verified".
"""

from __future__ import annotations

from dataclasses import dataclass

from egmra.provenance.hashing import content_id


@dataclass(frozen=True)
class CoverageClaim:
    claim_id: str
    centrality: float
    semantic_risk: float
    downstream_loss: float
    adequately_verified: bool

    def weight(self) -> float:
        return self.centrality * self.semantic_risk * self.downstream_loss


@dataclass(frozen=True)
class FrozenBlueprintWeights:
    """Weights + blueprint frozen before scoring (spec §12.3)."""

    weights_hash: str
    claim_ids: tuple[str, ...]


def freeze_blueprint(claims: list[CoverageClaim]) -> FrozenBlueprintWeights:
    if len({claim.claim_id for claim in claims}) != len(claims):
        raise ValueError("RFC blueprint claim IDs must be unique")
    return FrozenBlueprintWeights(
        weights_hash=content_id({c.claim_id: c.weight() for c in claims}),
        claim_ids=tuple(sorted(c.claim_id for c in claims)),
    )


def risk_weighted_formal_coverage(
    claims: list[CoverageClaim], frozen: FrozenBlueprintWeights
) -> float:
    """RFC = sum(w_c · verified) / sum(w_c) over the *frozen* blueprint."""
    if tuple(sorted(c.claim_id for c in claims)) != frozen.claim_ids:
        raise ValueError("RFC claims differ from the frozen blueprint; refreeze required")
    current_weights_hash = content_id({c.claim_id: c.weight() for c in claims})
    if current_weights_hash != frozen.weights_hash:
        raise ValueError("RFC weights changed after blueprint freeze; refreeze required")
    denom = sum(c.weight() for c in claims)
    if denom <= 0:
        return 0.0
    numer = sum(c.weight() for c in claims if c.adequately_verified)
    return round(numer / denom, 4)


@dataclass(frozen=True)
class ExpensiveClaimPolicy:
    """Policy for a convincing but prohibitively-expensive-to-formalize claim."""

    claim_id: str
    informal_review: str          # SINGLE | DOUBLE_INDEPENDENT
    sentinels_formalized: bool
    formalization_debt_published: bool

    def label_allowed(self) -> str:
        # Never imply a full formal proof for an unformalized central claim.
        if self.informal_review == "DOUBLE_INDEPENDENT" and self.sentinels_formalized:
            return "rigorous_informal_proof"
        return "informal_partial"

    def may_claim_formally_verified(self) -> bool:
        return False
