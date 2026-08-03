"""Evaluation protocol: baselines, freezing, causal ablations, time capsules (spec §12.2)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from types import MappingProxyType
from typing import Any

from egmra.provenance.hashing import canonical_json, content_id

# The four required baselines (spec §12.2 step 3).
REQUIRED_BASELINES = (
    "raw_strongest_model_with_tools",
    "raw_open_local_model",
    "current_repository_pipeline",
    "egmra_full_system",
)


@dataclass(frozen=True)
class FrozenEvalConfig:
    """Everything frozen for an evaluation run (spec §12.2 step 1)."""

    problem_bytes_hash: str
    status: str
    toolchain: str
    library_commit: str
    models: tuple[str, ...]
    prompts_hash: str
    tools: tuple[str, ...]
    budget: Mapping[str, Any]
    network_policy: str
    rubric_hash: str

    def __post_init__(self) -> None:
        for field_name in (
            "problem_bytes_hash", "status", "toolchain", "library_commit",
            "prompts_hash", "network_policy", "rubric_hash",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not isinstance(self.models, tuple) or not self.models \
                or any(not isinstance(item, str) or not item for item in self.models):
            raise ValueError("models must be a non-empty tuple of model identities")
        if not isinstance(self.tools, tuple) \
                or any(not isinstance(item, str) or not item for item in self.tools):
            raise ValueError("tools must be a tuple of tool identities")
        if not isinstance(self.budget, Mapping) or not self.budget:
            raise ValueError("budget must be a non-empty mapping")
        frozen_budget = _deep_freeze(dict(self.budget))
        canonical_json(frozen_budget)  # reject values that cannot be identity-bound
        object.__setattr__(self, "budget", frozen_budget)

    def config_hash(self) -> str:
        return content_id({
            "problem_bytes_hash": self.problem_bytes_hash,
            "status": self.status,
            "toolchain": self.toolchain,
            "library_commit": self.library_commit,
            "models": self.models,
            "prompts_hash": self.prompts_hash,
            "tools": self.tools,
            "budget": self.budget,
            "network_policy": self.network_policy,
            "rubric_hash": self.rubric_hash,
        })


@dataclass
class CausalAblationSpec:
    """A causal orchestration ablation holds everything fixed but one component."""

    component_under_test: str
    fixed_config_hash: str

    def valid_against(self, other: "CausalAblationSpec") -> bool:
        """Two ablation arms are causal only if they share the fixed config."""
        return self.fixed_config_hash == other.fixed_config_hash


@dataclass(frozen=True)
class TimeCapsule:
    """Level 6 time capsule: known open at cutoff t, solved later (spec §12.2)."""

    problem_id: str
    cutoff: str
    hidden_sources_after_cutoff: tuple[str, ...]
    held_out_solution_hash: str

    def __post_init__(self) -> None:
        _parse_iso_date(self.cutoff, field_name="cutoff")
        if not self.problem_id or not self.held_out_solution_hash:
            raise ValueError("time capsule identities must be non-empty")
        if not isinstance(self.hidden_sources_after_cutoff, tuple):
            raise ValueError("hidden_sources_after_cutoff must be a tuple")

    def leaks(self, source_date: str) -> bool:
        return _parse_iso_date(source_date, field_name="source_date") > _parse_iso_date(
            self.cutoff, field_name="cutoff"
        )


def _parse_iso_date(value: str, *, field_name: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 calendar date") from exc
    if value != parsed.isoformat():
        raise ValueError(f"{field_name} must use canonical YYYY-MM-DD form")
    return parsed


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(item) for item in value)
    return value


def baseline_comparison_valid(*, paired: bool, equal_cost_or_pareto: bool) -> bool:
    """A 'beats baseline' claim requires paired evaluation at equal cost or a Pareto curve."""
    return paired and equal_cost_or_pareto


@dataclass
class EvalRun:
    level: int
    config: FrozenEvalConfig
    baselines_present: set[str] = field(default_factory=set)

    def ready(self) -> bool:
        return set(REQUIRED_BASELINES).issubset(self.baselines_present)

    def missing_baselines(self) -> list[str]:
        return [b for b in REQUIRED_BASELINES if b not in self.baselines_present]
