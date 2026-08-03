"""Progress-vs-verbose scoring (spec §12.4).

An output counts as research progress only if it creates at least one *durable
object*. Token count, number of agents, number of candidate lemmas, self-rated
completeness, reviewer consensus, and polished exposition have zero direct
progress value. A long manuscript assembled from UNVERIFIED nodes scores below a
one-line exact counterexample.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DURABLE_OBJECTS = (
    "admitted_claim_with_new_evidence",
    "exact_counterexample",
    "verified_reduction_or_equivalence",
    "reproducible_experiment_crossing_threshold",
    "audited_prior_art_or_status_correction",
    "reusable_formal_or_computational_component",
    "failure_certificate_preventing_repeat_error",
)

# These have ZERO direct progress value (spec §12.4).
ZERO_VALUE_SIGNALS = (
    "token_count", "number_of_agents", "number_of_candidate_lemmas",
    "self_rated_completeness", "reviewer_consensus", "polished_exposition",
)


@dataclass
class ProgressLedger:
    durable_objects: list[str] = field(default_factory=list)

    def add(self, obj_kind: str) -> None:
        if obj_kind not in DURABLE_OBJECTS:
            raise ValueError(f"'{obj_kind}' is not a durable progress object")
        self.durable_objects.append(obj_kind)

    def progress_score(self) -> int:
        return len(self.durable_objects)

    @staticmethod
    def signal_value(signal: str) -> int:
        # Verbose signals contribute nothing.
        return 0 if signal in ZERO_VALUE_SIGNALS else 0


def is_progress(durable_object_count: int) -> bool:
    return durable_object_count >= 1


def manuscript_beats_counterexample(*, manuscript_unverified_nodes: int,
                                    exact_counterexamples: int) -> bool:
    """A long UNVERIFIED manuscript never beats one exact counterexample."""
    manuscript_progress = 0                    # UNVERIFIED nodes are not durable objects
    counterexample_progress = exact_counterexamples
    return manuscript_progress > counterexample_progress
