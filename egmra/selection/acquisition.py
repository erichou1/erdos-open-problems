"""Problem acquisition score A_p + Thompson sampling + protected exploration
(spec §6.2, §7.2).

Hard constraints (unsupported source access, malformed statement, incompatible
license, unacceptable false-promotion risk) block allocation separately; a low
score never means "mathematically impossible".
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from egmra.selection.features import ProblemFeatures
from egmra.selection.posterior import CompetingRiskPosterior, DEFAULT_OUTCOME_VALUES


@dataclass(frozen=True)
class AcquisitionWeights:
    exploration_sd: float = 0.5      # λ (protected lane only)
    info_gain: float = 0.5           # η
    reuse: float = 0.5               # ρ
    portfolio: float = 0.3           # δ
    freshness: float = 0.3           # φ
    cost_exponent: float = 0.85      # α ∈ [0.7, 1]

    def __post_init__(self) -> None:
        for name in ("exploration_sd", "info_gain", "reuse", "portfolio", "freshness"):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"acquisition weight {name} must be finite and non-negative")
        if not math.isfinite(self.cost_exponent) or not 0.7 <= self.cost_exponent <= 1:
            raise ValueError("cost_exponent must be in [0.7, 1]")


@dataclass(frozen=True)
class AcquisitionScore:
    problem_id: str
    score: float
    numerator: float
    expected_cost: float
    penalties: float
    interval_width: float


def acquisition_score(
    features: ProblemFeatures,
    posterior: CompetingRiskPosterior,
    *,
    values: dict[str, float] = DEFAULT_OUTCOME_VALUES,
    weights: AcquisitionWeights = AcquisitionWeights(),
    protected_lane: bool = False,
    expected_information_gain: float = 0.0,
    portfolio_bonus: float = 0.0,
) -> AcquisitionScore:
    if not math.isfinite(expected_information_gain) or expected_information_gain < 0:
        raise ValueError("expected_information_gain must be finite and non-negative")
    if not math.isfinite(portfolio_bonus) or portfolio_bonus < 0:
        raise ValueError("portfolio_bonus must be finite and non-negative")
    ev = posterior.expected_value(values)
    sd = posterior.value_stdev(values) if protected_lane else 0.0
    reuse = features.reuse_probability
    freshness = 1.0 if features.database_conflicts or not features.last_status_review else 0.0

    numerator = (
        ev
        + weights.exploration_sd * sd
        + weights.info_gain * expected_information_gain
        + weights.reuse * reuse
        + weights.portfolio * portfolio_bonus
        + weights.freshness * freshness
    )
    cost = max(1e-6, features.expected_cost) ** weights.cost_exponent

    penalties = (
        _ambiguity_penalty(features)
        + _stale_penalty(features)
        + _library_gap_penalty(features)
    )
    score = round(numerator / cost - penalties, 6)
    return AcquisitionScore(
        problem_id=features.problem_id, score=score, numerator=round(numerator, 6),
        expected_cost=round(cost, 6), penalties=round(penalties, 6),
        interval_width=posterior.credible_width(),
    )


def _ambiguity_penalty(f: ProblemFeatures) -> float:
    return 0.25 * f.ambiguity_count


def _stale_penalty(f: ProblemFeatures) -> float:
    return 0.5 if not f.last_status_review else 0.0


def _library_gap_penalty(f: ProblemFeatures) -> float:
    return max(0.0, 0.5 * (1.0 - f.mathlib_coverage)) if f.existing_lean_statement else 0.0


@dataclass
class ProblemSelector:
    """Selects problems by Thompson sampling with a protected-exploration reserve."""

    protected_fraction: float = 0.20
    seed: int = 0

    def __post_init__(self) -> None:
        self.protected_fraction = min(0.25, max(0.15, self.protected_fraction))
        self._rng = random.Random(self.seed)

    def hard_constraints_ok(self, features: ProblemFeatures) -> tuple[bool, str]:
        excluded, reason = features.hard_excluded()
        return (not excluded), reason

    def select(
        self, candidates: list[tuple[ProblemFeatures, CompetingRiskPosterior]], *, k: int = 3,
        values: dict[str, float] = DEFAULT_OUTCOME_VALUES,
    ) -> list[str]:
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError("k must be a positive integer")
        ids = [features.problem_id for features, _ in candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate problem ids in selection candidates")
        if any(not math.isfinite(value) for value in values.values()):
            raise ValueError("outcome values must be finite")
        eligible = [(f, p) for f, p in candidates if self.hard_constraints_ok(f)[0]]
        if not eligible:
            return []
        k = min(k, len(eligible))
        exploit_k = max(1, round(k * (1 - self.protected_fraction)))
        explore_k = max(0, k - exploit_k)

        # Exploit: Thompson-sample outcome params, score, take top.
        exploit_scored = []
        for f, p in eligible:
            sampled = {o: self._rng.gammavariate(p.alpha[o], 1.0) for o in p.alpha}
            norm = sum(sampled.values()) or 1.0
            sampled_ev = sum((sampled[o] / norm) * values.get(o, 0.0) for o in p.alpha)
            exploit_scored.append((sampled_ev / max(1e-6, f.expected_cost), f.problem_id))
        exploit_scored.sort(reverse=True)
        exploit = [pid for _, pid in exploit_scored[:exploit_k]]

        # Protected exploration: widest intervals / fewest attempts / diverse domains.
        explore_pool = sorted(
            eligible, key=lambda fp: (fp[0].prior_attempts, -fp[1].credible_width()))
        explore = [f.problem_id for f, _ in explore_pool if f.problem_id not in exploit][:explore_k]
        return exploit + explore
