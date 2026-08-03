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


# Stratified first-wave selection (report R2). The old behavior truncated the
# compatible list in REGISTRY order, so for classified domains the first three
# were always direct_structural / contradiction_minimal_counterexample /
# extremal_invariant — the computational, formal-library, and
# model-construction families (and with them the experimentalist and
# formalizer worker roles) were unreachable. A first wave must instead contain
# materially different mechanisms: one proof route, one refutation or
# construction route, one tool route.
_PROOF_FAMILIES = (
    "direct_structural", "extremal_invariant", "probabilistic_analytic",
    "additive_combinatorial", "algebraic_spectral", "geometric_topological",
    "ergodic_dynamical",
)
_REFUTATION_FAMILIES = (
    "contradiction_minimal_counterexample", "counterexample_model_construction",
)
_TOOL_FAMILIES = (
    "computational_finite_reduction", "formal_library_first",
    "literature_derived_transfer",
)


def _pick(stratum: tuple[str, ...], available: list[str],
          prefer: tuple[str, ...] = ()) -> str | None:
    for family in prefer:
        if family in stratum and family in available:
            return family
    for family in stratum:
        if family in available:
            return family
    return None


def instantiate_programs(
    domain: str, *, bottleneck: str = "", budget_each: float = 1.0,
    max_programs: int = 8, cross_domain_exploration: bool = False,
    has_formal_target: bool = False, has_predicate: bool = False,
) -> list[ResearchProgram]:
    """Governor: a stratified, materially-diverse program wave.

    Deterministic in its inputs. The wave is built one stratum at a time —
    proof, refutation/construction, tool — then remaining slots fill from the
    leftover compatible families in registry order. Signals steer the tool
    stratum: a community formal target prefers ``formal_library_first``; an
    executable predicate prefers ``computational_finite_reduction``; the
    cold-pass bottleneck keeps its original hard filter.
    """
    families = compatible_families(domain, cross_domain_exploration=cross_domain_exploration)
    if bottleneck == "counterexample":
        families = [f for f in families if "counterexample" in f or "computational" in f] or families
    elif bottleneck == "formalization":
        families = [f for f in families if "formal" in f] or families

    tool_prefer: tuple[str, ...] = ()
    if has_formal_target:
        tool_prefer = ("formal_library_first", "computational_finite_reduction")
    elif has_predicate:
        tool_prefer = ("computational_finite_reduction", "formal_library_first")

    selected: list[str] = []
    remaining = list(families)
    for stratum, prefer in (
        (_PROOF_FAMILIES, ()),
        (_REFUTATION_FAMILIES, ()),
        (_TOOL_FAMILIES, tool_prefer),
    ):
        if len(selected) >= max_programs:
            break
        choice = _pick(stratum, remaining, prefer)
        if choice is not None:
            selected.append(choice)
            remaining.remove(choice)
    for family in remaining:
        if len(selected) >= max_programs:
            break
        selected.append(family)

    return [
        ResearchProgram(
            family=f,
            falsifier=f"counterexample twin for {f}",
            budget=budget_each,
            kill_criterion="valid_counterexample or dominated_identical_state",
        )
        for f in selected[:max_programs]
    ]
