"""Required ablations + pre-registration (spec §12.5)."""

from __future__ import annotations

from dataclasses import dataclass, field

REQUIRED_ABLATIONS = (
    "no_literature_vs_cold_pass_only_vs_two_pass_retrieval",
    "no_oeis_vs_structured_oeis_service",
    "transcript_memory_vs_claim_graph_vs_claim_graph_with_revocation",
    "fixed_four_scouts_vs_tool_differentiated_program_archive",
    "fixed_revisions_vs_dynamic_branch_controller",
    "late_formalization_vs_risk_weighted_lean_sentinels",
    "same_model_review_vs_different_family_tool_backed_referee",
    "no_computation_vs_executable_falsification",
    "no_protected_exploration_vs_10_20_adaptive",
    "multiplicative_heuristic_vs_posterior_expected_utility",
    "no_expert_iteration_vs_verified_only_expert_iteration",
    "single_model_vs_routed_model_portfolio",
    "full_orchestration_vs_equal_cost_raw_model",
)


class AblationError(RuntimeError):
    pass


@dataclass
class PreRegistration:
    """Pre-register primary metrics + stop conditions before running ablations."""

    ablation: str
    primary_metric: str
    stop_condition: str

    def __post_init__(self) -> None:
        if self.ablation not in REQUIRED_ABLATIONS:
            raise AblationError(f"unknown ablation {self.ablation!r}")
        if not isinstance(self.primary_metric, str) or not self.primary_metric.strip():
            raise AblationError("primary_metric must be non-empty")
        if not isinstance(self.stop_condition, str) or not self.stop_condition.strip():
            raise AblationError("stop_condition must be non-empty")


@dataclass
class AblationRegistry:
    registered: dict[str, PreRegistration] = field(default_factory=dict)

    def register(self, prereg: PreRegistration) -> None:
        if prereg.ablation in self.registered:
            raise AblationError(f"ablation {prereg.ablation!r} is already registered")
        self.registered[prereg.ablation] = prereg

    def missing(self) -> list[str]:
        return [a for a in REQUIRED_ABLATIONS if a not in self.registered]

    def complete(self) -> bool:
        return not self.missing()
