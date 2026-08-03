"""Nine feature families for problem selection (spec §6.2)."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any


@dataclass(frozen=True)
class ProblemFeatures:
    problem_id: str
    # status
    open_state_source_count: int = 0
    last_status_review: str = ""
    source_independence: float = 0.0
    database_conflicts: int = 0
    # statement
    ambiguity_count: int = 0
    formal_clarity: float = 0.0
    number_of_parts: int = 1
    parameter_regimes: int = 1
    # literature
    theorem_density: float = 0.0
    partial_result_ladder: int = 0
    citation_depth: int = 0
    # formal
    existing_lean_statement: bool = False
    mathlib_coverage: float = 0.0
    expected_formal_debt: float = 0.0
    # computational
    finite_reductions: int = 0
    falsifiability: float = 0.0
    enumeration_growth: str = "unknown"
    certificate_available: bool = False
    # mathematical
    domain: str = "unknown"
    expected_conceptual_depth: float = 0.0
    deep_machinery_dependence: float = 0.0
    # operational
    prior_attempts: int = 0
    censoring_reason: str = ""
    verified_lemma_yield: float = 0.0
    expected_cost: float = 1.0
    # reuse
    reuse_probability: float = 0.0
    # fit (locally measured, never vendor reputation)
    local_model_fit: float = 0.0
    # hard allocation constraints (§7.2), kept separate from numerical score
    source_access_authorized: bool = True
    license_compatible: bool = True
    statement_well_formed: bool = True
    false_promotion_risk_acceptable: bool = True
    provable_duplicate: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.problem_id, str) or not self.problem_id:
            raise ValueError("problem_id must be a non-empty string")
        for name in (
            "open_state_source_count", "database_conflicts", "ambiguity_count",
            "partial_result_ladder", "citation_depth", "finite_reductions", "prior_attempts",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        for name in ("number_of_parts", "parameter_regimes"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        for name in (
            "source_independence", "formal_clarity", "mathlib_coverage", "falsifiability",
            "reuse_probability", "local_model_fit",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be finite and in [0, 1]")
        for name in (
            "theorem_density", "expected_formal_debt", "expected_conceptual_depth",
            "deep_machinery_dependence", "verified_lemma_yield",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if not math.isfinite(self.expected_cost) or self.expected_cost <= 0:
            raise ValueError("expected_cost must be finite and positive")

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)

    def hard_excluded(self) -> tuple[bool, str]:
        """Only malformed, unauthorized, or provably-duplicate tasks are excluded."""
        if self.number_of_parts <= 0 or self.parameter_regimes <= 0:
            return True, "malformed statement"
        if not self.statement_well_formed:
            return True, "malformed statement"
        if not self.source_access_authorized:
            return True, "unsupported source access"
        if not self.license_compatible:
            return True, "incompatible license"
        if not self.false_promotion_risk_acceptable:
            return True, "unacceptable false-promotion risk"
        if self.provable_duplicate:
            return True, "provable duplicate"
        return False, ""
