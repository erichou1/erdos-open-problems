"""Dispatchable method profiles and genuine-diversity check (spec §6.5).

"Direct proof", "minimal counterexample", "probabilistic method" and similar labels
are *dispatchable method profiles*, not permanent agents. Genuine diversity requires
workers to differ in at least two of: method prior, tool access, source packet,
objective, model family/lineage, target representation, or counterfactual assumption.
Two same-model chats with identical context and "be creative" prompts count as one
correlated method, not two independent agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DIVERSITY_AXES = (
    "method_prior", "tool_access", "source_packet", "objective",
    "model_lineage", "target_representation", "counterfactual_assumption",
)


@dataclass(frozen=True)
class MethodProfile:
    profile_id: str
    method_prior: str
    prohibited_methods: tuple[str, ...] = ()
    tool_access: tuple[str, ...] = ()
    source_packet: str = ""
    objective: str = "construct"          # construct | falsify | simplify
    model_lineage: str = ""
    target_representation: str = "informal"  # informal | combinatorial_program | formal_goal
    counterfactual_assumption: str = ""

    def axis_values(self) -> dict[str, object]:
        return {
            "method_prior": self.method_prior,
            "tool_access": tuple(sorted(self.tool_access)),
            "source_packet": self.source_packet,
            "objective": self.objective,
            "model_lineage": self.model_lineage,
            "target_representation": self.target_representation,
            "counterfactual_assumption": self.counterfactual_assumption,
        }


def differing_axes(a: MethodProfile, b: MethodProfile) -> list[str]:
    av, bv = a.axis_values(), b.axis_values()
    return [axis for axis in DIVERSITY_AXES if av[axis] != bv[axis]]


def is_genuinely_diverse(a: MethodProfile, b: MethodProfile) -> bool:
    """Two workers are genuinely diverse only if they differ in >= 2 axes."""
    return len(differing_axes(a, b)) >= 2


@dataclass
class DiversityAudit:
    profiles: list[MethodProfile] = field(default_factory=list)

    def correlated_pairs(self) -> list[tuple[str, str]]:
        """Pairs that are NOT genuinely diverse (correlated methods)."""
        out: list[tuple[str, str]] = []
        for i, a in enumerate(self.profiles):
            for b in self.profiles[i + 1:]:
                if not is_genuinely_diverse(a, b):
                    out.append((a.profile_id, b.profile_id))
        return out

    def independent_count(self) -> int:
        """Number of profiles after collapsing correlated ones (upper bound)."""
        collapsed: list[MethodProfile] = []
        for profile in self.profiles:
            if all(is_genuinely_diverse(profile, kept) for kept in collapsed):
                collapsed.append(profile)
        return len(collapsed)
