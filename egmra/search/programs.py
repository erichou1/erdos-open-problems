"""Research-program families and conditional dispatch (spec §14.4, §6.5).

At scale the system maintains a quality-diversity archive of program families rather
than a fixed "20 agents" org. The governor instantiates only profiles compatible
with the current domain and bottleneck; each active program declares a falsifier,
budget, and kill/pause criterion.
"""

from __future__ import annotations

from dataclasses import dataclass

from egmra.search.mechanism import METHOD_FAMILIES

# Domain compatibility hints per family (which domains a profile suits).
_DOMAIN_FIT = {
    "direct_structural": {"any"},
    "contradiction_minimal_counterexample": {"any"},
    "extremal_invariant": {"combinatorics", "graph_theory", "number_theory"},
    "probabilistic_analytic": {"combinatorics", "analysis", "number_theory"},
    "additive_combinatorial": {"number_theory", "combinatorics"},
    "algebraic_spectral": {"algebra", "graph_theory"},
    "geometric_topological": {"geometry", "topology"},
    "ergodic_dynamical": {"dynamics", "number_theory"},
    "computational_finite_reduction": {"any"},
    "formal_library_first": {"any"},
    "literature_derived_transfer": {"any"},
    "counterexample_model_construction": {"any"},
}


@dataclass(frozen=True)
class ResearchProgram:
    family: str
    falsifier: str
    budget: float
    kill_criterion: str

    def __post_init__(self) -> None:
        if self.family not in METHOD_FAMILIES:
            raise ValueError(f"unknown family {self.family!r}")
        if not self.falsifier:
            raise ValueError("every research program must declare a falsifier")


def compatible_families(domain: str, *, cross_domain_exploration: bool = False) -> list[str]:
    """Families the governor may instantiate for a domain."""
    out = []
    for family in METHOD_FAMILIES:
        fit = _DOMAIN_FIT[family]
        if "any" in fit or domain in fit or cross_domain_exploration:
            out.append(family)
    return out


def instantiate_programs(
    domain: str, *, bottleneck: str = "", budget_each: float = 1.0,
    max_programs: int = 8, cross_domain_exploration: bool = False,
) -> list[ResearchProgram]:
    """Governor: instantiate compatible, bottleneck-appropriate programs only."""
    families = compatible_families(domain, cross_domain_exploration=cross_domain_exploration)
    if bottleneck == "counterexample":
        families = [f for f in families if "counterexample" in f or "computational" in f] or families
    elif bottleneck == "formalization":
        families = [f for f in families if "formal" in f] or families
    programs = [
        ResearchProgram(
            family=f,
            falsifier=f"counterexample twin for {f}",
            budget=budget_each,
            kill_criterion="valid_counterexample or dominated_identical_state",
        )
        for f in families[:max_programs]
    ]
    return programs
