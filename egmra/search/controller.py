"""Branch/action controller: additive utility, posterior selection, pause/reopen
(spec §7.2, §7.3, §7.7, §4.3 item 2).

The controller does *not* multiply subjective factors (one near-zero estimate must
not veto a valuable branch). It uses an additive utility ``U(b,a)`` and selects by
posterior (Thompson) sampling under a global budget, reserving 15-25% for protected
exploration. Rate limits pause work; they never mark a branch failed.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from egmra.search.failure import KILL_REASONS


@dataclass(frozen=True)
class UtilityWeights:
    info_gain: float = 1.0          # λ
    unlock: float = 1.0             # ρ
    reuse: float = 0.5              # χ
    diversity: float = 0.5          # δ
    falsification: float = 0.8      # ζ
    duplicate: float = 1.0          # κ
    semantic_risk: float = 1.0      # ξ

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"utility weight {name} must be finite and non-negative")


@dataclass(frozen=True)
class ActionComponents:
    expected_outcome_value: float   # sum_o P(o|x,a) V_o
    info_gain: float = 0.0
    unlock: float = 0.0
    reuse: float = 0.0
    diversity: float = 0.0
    falsification_value: float = 0.0
    expected_cost: float = 0.0
    duplicate: float = 0.0
    semantic_risk: float = 0.0

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if not math.isfinite(value):
                raise ValueError(f"action component {name} must be finite")
            if name != "expected_outcome_value" and value < 0:
                raise ValueError(f"action component {name} must be non-negative")


def branch_action_utility(c: ActionComponents, w: UtilityWeights = UtilityWeights()) -> float:
    """Additive U(b,a) (spec §7.3). Never multiplicative."""
    return round(
        c.expected_outcome_value
        + w.info_gain * c.info_gain
        + w.unlock * c.unlock
        + w.reuse * c.reuse
        + w.diversity * c.diversity
        + w.falsification * c.falsification_value
        - c.expected_cost
        - w.duplicate * c.duplicate
        - w.semantic_risk * c.semantic_risk,
        6,
    )


@dataclass
class BranchPosterior:
    branch_id: str
    alpha: float = 1.0              # Beta prior successes+1
    beta: float = 1.0              # Beta prior failures+1
    attempts: int = 0
    last_debt_reduction: float = 0.0
    repeated_signatures: int = 0
    protected: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.branch_id, str) or not self.branch_id:
            raise ValueError("branch_id must be a non-empty string")
        if not math.isfinite(self.alpha) or not math.isfinite(self.beta) \
                or self.alpha <= 0 or self.beta <= 0:
            raise ValueError("Beta posterior parameters must be finite and positive")
        if not isinstance(self.attempts, int) or self.attempts < 0:
            raise ValueError("attempts must be a non-negative integer")

    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def stdev(self) -> float:
        a, b = self.alpha, self.beta
        n = a + b
        return (a * b / (n * n * (n + 1))) ** 0.5


@dataclass
class Controller:
    global_budget: float
    protected_fraction: float = 0.20
    max_branch_fraction: float = 0.4
    pause_review_threshold: int = 3
    seed: int = 0
    spent: float = 0.0
    posteriors: dict[str, BranchPosterior] = field(default_factory=dict)
    branch_spend: dict[str, float] = field(default_factory=dict)
    governor_events: list[dict] = field(default_factory=list)
    _rng: random.Random = field(default_factory=lambda: random.Random(0))

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        if not math.isfinite(self.global_budget) or self.global_budget <= 0:
            raise ValueError("global_budget must be finite and positive")
        if not math.isfinite(self.max_branch_fraction) or not 0 < self.max_branch_fraction <= 1:
            raise ValueError("max_branch_fraction must be in (0, 1]")
        if not math.isfinite(self.spent) or not 0 <= self.spent <= self.global_budget:
            raise ValueError("spent budget must be finite and within the global budget")
        if not isinstance(self.pause_review_threshold, int) or self.pause_review_threshold <= 0:
            raise ValueError("pause_review_threshold must be a positive integer")
        if not 0.15 <= self.protected_fraction <= 0.25:
            # spec §7.2: reserve 15-25% for protected exploration
            self.protected_fraction = min(0.25, max(0.15, self.protected_fraction))

    def register(self, posterior: BranchPosterior) -> None:
        if posterior.branch_id in self.posteriors:
            raise ValueError(f"duplicate branch posterior {posterior.branch_id!r}")
        self.posteriors[posterior.branch_id] = posterior
        self.branch_spend.setdefault(posterior.branch_id, 0.0)

    def has_budget(self) -> bool:
        return self.spent < self.global_budget

    # ── selection ──────────────────────────────────────────────────────────────

    def select_posterior_actions(
        self, candidates: list[tuple[str, ActionComponents]], *, k: int = 3,
        weights: UtilityWeights = UtilityWeights(),
    ) -> list[str]:
        """Select up to k branches by Thompson-sampled utility with protected lane."""
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError("k must be a positive integer")
        seen: set[str] = set()
        for branch_id, _ in candidates:
            if branch_id in seen:
                raise ValueError(f"duplicate selection candidate {branch_id!r}")
            if branch_id not in self.posteriors:
                raise KeyError(f"unregistered branch {branch_id!r}")
            seen.add(branch_id)
        if not candidates:
            return []
        k = min(k, len(candidates))
        exploit_k = max(1, round(k * (1 - self.protected_fraction)))
        explore_k = max(0, k - exploit_k)

        scored: list[tuple[float, str]] = []
        for branch_id, comps in candidates:
            post = self.posteriors[branch_id]
            theta = self._rng.betavariate(post.alpha, post.beta)
            base = branch_action_utility(comps, weights)
            # Thompson-sample only the posterior outcome contribution.  Information,
            # diversity, cost, duplicate, and risk terms remain additive rather
            # than being accidentally multiplied by one sampled scalar.
            sampled = base + (theta - post.mean()) * abs(comps.expected_outcome_value)
            scored.append((sampled, branch_id))
        scored.sort(reverse=True)
        exploit = [bid for _, bid in scored[:exploit_k]]

        # protected exploration: highest-uncertainty / lowest-attempt branches
        explore_pool = sorted(
            (self.posteriors[bid] for _, bid in scored),
            key=lambda p: (not p.protected, p.attempts, -p.stdev()),
        )
        explore = [p.branch_id for p in explore_pool if p.branch_id not in exploit][:explore_k]
        return exploit + explore

    # ── budget guard ─────────────────────────────────────────────────────────────

    def allocate(self, branch_id: str, amount: float, *, verified_debt_reduction: float,
                 info_gain: float) -> bool:
        """Allocate budget; a branch cannot exceed the cap without a governor event."""
        if branch_id not in self.posteriors:
            raise KeyError(f"unregistered branch {branch_id!r}")
        for name, value in {
            "amount": amount,
            "verified_debt_reduction": verified_debt_reduction,
            "info_gain": info_gain,
        }.items():
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if amount <= 0:
            raise ValueError("allocation amount must be positive")
        if self.spent + amount > self.global_budget:
            return False
        cap = self.max_branch_fraction * self.global_budget
        post = self.posteriors[branch_id]
        spent_on_branch = self.branch_spend.get(branch_id, 0.0)
        if spent_on_branch + amount > cap:
            if verified_debt_reduction <= 0 and info_gain <= 0:
                return False
            self.governor_events.append({
                "branch_id": branch_id, "reason": "exceed_cap_with_justification",
                "verified_debt_reduction": verified_debt_reduction, "info_gain": info_gain,
            })
        self.spent += amount
        self.branch_spend[branch_id] = spent_on_branch + amount
        post.attempts += 1
        return True

    # ── pause / terminate / reopen (spec §7.7) ────────────────────────────────

    def should_pause(self, branch_id: str, *, marginal_value: float, expected_cost: float,
                     debt_reduction: float, info_gain: float, repeated: bool,
                     protected_obligation: bool, review_count: int) -> bool:
        if protected_obligation:
            return False
        if review_count < self.pause_review_threshold:
            return False
        return (marginal_value < expected_cost and debt_reduction <= 0.0
                and info_gain <= 0.0 and repeated)

    @staticmethod
    def can_terminate(reason: str) -> bool:
        return reason in KILL_REASONS

    @staticmethod
    def reopen_conditions() -> tuple[str, ...]:
        return (
            "new_admitted_lemma_closes_dependency",
            "new_counterexample_changes_lattice",
            "literature_or_oeis_exposes_theorem",
            "toolchain_or_model_capability_change",
            "cost_value_posterior_changed_materially",
            "human_resolves_ambiguity",
        )

    def should_reopen(self, condition: str) -> bool:
        return condition in self.reopen_conditions()

    def update_posterior(self, branch_id: str, *, success: bool,
                         debt_reduction: float = 0.0,
                         censored_reason: str | None = None) -> None:
        from egmra.search.failure import is_censored

        if branch_id not in self.posteriors:
            raise KeyError(f"unregistered branch {branch_id!r}")
        post = self.posteriors[branch_id]
        if censored_reason is not None:
            if not is_censored(censored_reason):
                raise ValueError(f"reason {censored_reason!r} is not operationally censored")
            self.governor_events.append({
                "branch_id": branch_id,
                "reason": censored_reason,
                "classification": "censored_operational_event",
                "posterior_updated": False,
            })
            return
        if not isinstance(success, bool):
            raise ValueError("success must be a boolean")
        if not math.isfinite(debt_reduction):
            raise ValueError("debt_reduction must be finite")
        if success:
            post.alpha += 1
        else:
            post.beta += 1
        post.last_debt_reduction = debt_reduction
