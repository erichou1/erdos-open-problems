"""Human role + intervention log (spec §14.7).

The architecture minimizes routine human labor but does not hide it inside an
"autonomous" label. Every intervention is recorded with its phase and scope so the
release certificate's autonomy metadata is honest.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Humans remain required for these (spec §14.7).
HUMAN_RESPONSIBILITIES = (
    "resolve_ambiguous_intent",
    "access_specialized_literature",
    "adjudicate_significance_and_novelty",
    "review_incompletely_formalized_central_claims",
    "authorize_public_submissions_and_oeis",
    "set_value_weights_and_risk",
    "respond_to_potential_major_result",
)

# Autonomy phases (spec §11.5 autonomy taxonomy).
PHASES = ("pre_run", "in_run", "post_run")


@dataclass(frozen=True)
class Intervention:
    phase: str
    kind: str
    scope: str
    actor_id: str
    conflicts_of_interest: str = ""

    def __post_init__(self) -> None:
        if self.phase not in PHASES:
            raise ValueError(f"unknown phase {self.phase!r}")


@dataclass
class InterventionLog:
    interventions: list[Intervention] = field(default_factory=list)

    def record(self, intervention: Intervention) -> None:
        self.interventions.append(intervention)

    def counts_by_phase(self) -> dict[str, int]:
        counts = {p: 0 for p in PHASES}
        for i in self.interventions:
            counts[i.phase] += 1
        return counts

    def autonomy_metadata(self) -> dict:
        """The phase-by-phase intervention taxonomy for the release certificate."""
        return {
            "intervention_counts": self.counts_by_phase(),
            "total": len(self.interventions),
            "interventions": [i.__dict__ for i in self.interventions],
        }
