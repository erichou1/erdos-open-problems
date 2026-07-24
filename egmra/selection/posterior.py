"""Competing-risk outcome posterior with censoring (spec §6.2, §7.2).

Model competing outcomes separately with a Dirichlet posterior. A timeout or rate
limit is *censored operational data*, not mathematical failure, so it does not
increment the ``no_progress`` count. Until enough verified outcomes exist, publish
wide intervals with weak priors.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

OUTCOMES = (
    "novel_full", "refutation", "verified_partial", "status_fix",
    "reusable_infrastructure", "rediscovery", "no_progress", "invalid",
)


@dataclass
class CompetingRiskPosterior:
    """Dirichlet posterior over the competing outcome classes."""

    alpha: dict[str, float] = field(default_factory=lambda: {o: 0.5 for o in OUTCOMES})
    censored: int = 0

    def __post_init__(self) -> None:
        if set(self.alpha) != set(OUTCOMES):
            raise ValueError("posterior alpha must contain exactly the competing outcomes")
        self.alpha = dict(self.alpha)
        if any(not math.isfinite(value) or value <= 0 for value in self.alpha.values()):
            raise ValueError("posterior alpha values must be finite and positive")
        if not isinstance(self.censored, int) or isinstance(self.censored, bool) \
                or self.censored < 0:
            raise ValueError("censored count must be a non-negative integer")

    def observe(self, outcome: str, *, censored: bool = False) -> None:
        if not isinstance(censored, bool):
            raise ValueError("censored must be boolean")
        if censored or outcome in {"timeout", "rate_limit", "resource_exhaustion"}:
            self.censored += 1
            return  # censored data does not count as a mathematical outcome
        if outcome not in OUTCOMES:
            raise ValueError(f"unknown outcome {outcome!r}")
        self.alpha[outcome] += 1.0

    def total(self) -> float:
        return sum(self.alpha.values())

    def mean(self) -> dict[str, float]:
        t = self.total()
        return {o: self.alpha[o] / t for o in OUTCOMES}

    def stdev(self, outcome: str) -> float:
        a = self.alpha[outcome]
        t = self.total()
        return math.sqrt(a * (t - a) / (t * t * (t + 1)))

    def credible_width(self) -> float:
        """A coarse interval width: wide when few observations exist."""
        return round(1.0 / math.sqrt(self.total()), 4)

    def expected_value(self, values: dict[str, float]) -> float:
        if any(not math.isfinite(value) for value in values.values()):
            raise ValueError("outcome values must be finite")
        mean = self.mean()
        return round(sum(mean[o] * values.get(o, 0.0) for o in OUTCOMES), 6)

    def value_stdev(self, values: dict[str, float]) -> float:
        """SD of the value functional (uncertainty bonus source, protected lane)."""
        if any(not math.isfinite(value) for value in values.values()):
            raise ValueError("outcome values must be finite")
        mean = self.mean()
        ev = self.expected_value(values)
        var = sum(mean[o] * (values.get(o, 0.0) - ev) ** 2 for o in OUTCOMES)
        return round(math.sqrt(max(0.0, var)), 6)


# Default mathematical values V_o, set by project policy (not the model) (§7.2).
DEFAULT_OUTCOME_VALUES = {
    "novel_full": 10.0,
    "refutation": 8.0,
    "verified_partial": 4.0,
    "status_fix": 3.0,
    "reusable_infrastructure": 3.0,
    "rediscovery": 1.0,
    "no_progress": 0.0,
    "invalid": -5.0,          # a false promotion is strongly penalized
}
