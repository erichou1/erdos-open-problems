"""Target-relative verified debt with a frozen policy (spec §7.3).

``verifiedDebt`` is the risk/cost-weighted frontier of *all* unclosed obligations
reachable from the locked target, including every newly-introduced helper plus
semantic-correspondence and import debt. Replacing one hard goal with an unproved
helper that restates or implies the target receives zero (or negative) credit —
this prevents the AlphaProof-Nexus "move difficulty into one helper" failure. The
debt definition and weights are frozen per evaluation run (see DECISIONS.md D-006).
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from egmra.provenance.hashing import content_id


@dataclass(frozen=True)
class DebtPolicy:
    """Immutable, content-addressed weights, frozen for an evaluation run."""

    risk_weight: float = 1.0
    cost_weight: float = 1.0
    correspondence_weight: float = 1.5
    import_weight: float = 1.2
    restates_target_penalty: float = 2.0

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"debt policy weight {name} must be finite and non-negative")

    def policy_hash(self) -> str:
        return content_id({
            "risk": self.risk_weight, "cost": self.cost_weight,
            "correspondence": self.correspondence_weight, "import": self.import_weight,
            "restates_penalty": self.restates_target_penalty,
        })


@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    closed: bool
    risk: float
    cost: float
    kind: str = "goal"          # goal | correspondence | import | helper
    restates_target: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.obligation_id, str) or not self.obligation_id:
            raise ValueError("obligation_id must be a non-empty string")
        if not isinstance(self.closed, bool):
            raise ValueError("closed must be boolean")
        if not math.isfinite(self.risk) or not math.isfinite(self.cost) \
                or self.risk < 0 or self.cost < 0:
            raise ValueError("obligation risk and cost must be finite and non-negative")


@dataclass(frozen=True)
class DebtResult:
    debt: float
    policy_hash: str
    open_obligations: int


def verified_debt(obligations: list[Obligation], policy: DebtPolicy) -> DebtResult:
    """Weighted frontier of unclosed obligations reachable from the target."""
    ids = [ob.obligation_id for ob in obligations]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate obligations are not permitted")
    total = 0.0
    open_count = 0
    for ob in obligations:
        if ob.closed:
            continue
        open_count += 1
        weight = policy.risk_weight * ob.risk + policy.cost_weight * ob.cost
        if ob.kind == "correspondence":
            weight *= policy.correspondence_weight
        elif ob.kind == "import":
            weight *= policy.import_weight
        if ob.restates_target:
            # A helper restating/implying the target adds debt, never removes it.
            weight += policy.restates_target_penalty
        total += weight
    return DebtResult(round(total, 6), policy.policy_hash(), open_count)


def delta_verified_debt(
    before: list[Obligation], after: list[Obligation], policy: DebtPolicy
) -> float:
    """ΔverifiedDebt = D_before − D_after (positive = genuine progress)."""
    after_ids = {ob.obligation_id for ob in after}
    missing = {ob.obligation_id for ob in before} - after_ids
    if missing:
        raise ValueError(f"obligations disappeared without an explicit closed record: {sorted(missing)}")
    return round(
        verified_debt(before, policy).debt - verified_debt(after, policy).debt, 6
    )


def credit_for_action(
    before: list[Obligation], after: list[Obligation], policy: DebtPolicy
) -> float:
    """Credit an action gets. Restating the target yields zero or negative credit."""
    delta = delta_verified_debt(before, after, policy)
    # If the "after" set added a restating helper, the debt went up -> delta<=0.
    return delta
