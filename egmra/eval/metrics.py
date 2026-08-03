"""Evaluation metrics (spec §12.3): outcomes, progress, RFC, search, efficiency, calibration."""

from __future__ import annotations

from dataclasses import dataclass

# Re-export the frozen-blueprint RFC from the Lean coverage module (single source).
from egmra.lean.coverage import (
    CoverageClaim,
    FrozenBlueprintWeights,
    freeze_blueprint as freeze_blueprint,
    risk_weighted_formal_coverage,
)


@dataclass
class FinalOutcomeMetrics:
    exact_full_proofs: int = 0
    detections: int = 0            # false/ambiguity/misquotation/already-solved
    correct_abstentions: int = 0
    incorrect_solved_declarations: int = 0   # reported prominently, never averaged away

    def report(self) -> dict:
        return dict(self.__dict__)


@dataclass
class SearchQualityMetrics:
    unique_mechanism_families: int = 0
    semantic_duplicate_rate: float = 0.0
    repeated_error_rate: float = 0.0
    counterexample_discovery_rate: float = 0.0
    useful_branch_budget_fraction: float = 0.0
    verification_backlog: int = 0

    def report(self) -> dict:
        return dict(self.__dict__)


@dataclass
class EfficiencyMetrics:
    cost_per_verified_lemma: float = 0.0
    cost_per_central_debt_unit: float = 0.0
    time_to_first_counterexample: float = 0.0
    time_to_first_admitted_lemma: float = 0.0
    time_to_final_certificate: float = 0.0
    cache_hit_rate: float = 0.0
    orchestration_gain_over_baseline: float = 0.0

    def report(self) -> dict:
        return dict(self.__dict__)


@dataclass
class IntermediateProgressMetrics:
    newly_verified_lemmas: int = 0
    useful_counterexamples: int = 0
    killed_false_conjectures: int = 0
    verified_debt_reduction: float = 0.0
    reusable_components: int = 0
    confirmed_status_corrections: int = 0
    open_subgoals_closed_fraction: float = 0.0

    def report(self) -> dict:
        return dict(self.__dict__)


def rfc(claims: list[CoverageClaim], frozen: FrozenBlueprintWeights) -> float:
    """Risk-weighted formal coverage over a frozen blueprint (spec §12.3)."""
    return risk_weighted_formal_coverage(claims, frozen)
