"""Verified-only expert iteration (spec §6.11, §16 P3).

Value/policy learning uses only *authenticated, replayable* outcomes, frozen
evaluation periods, exact pipeline fingerprints, and evaluators different from the
models being trained. Model consensus is never independent evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class ExpertIterationError(RuntimeError):
    pass


@dataclass(frozen=True)
class TrainingExample:
    example_id: str
    authenticated: bool
    replayed: bool
    pipeline_fingerprint: str
    evaluator_lineage: str
    generator_lineage: str
    payload: dict = field(default_factory=dict)

    def eligible(self) -> bool:
        # Must be authenticated + replayed, and the evaluator must differ from the
        # model being trained (no self-grading loop).
        return (self.authenticated and self.replayed
                and self.evaluator_lineage != self.generator_lineage)


@dataclass
class VerifiedOnlyExpertIteration:
    trained_lineage: str
    frozen_eval_period: str
    accepted: list[TrainingExample] = field(default_factory=list)
    rejected: list[tuple[str, str]] = field(default_factory=list)

    def admit(self, example: TrainingExample) -> bool:
        if not example.eligible():
            self.rejected.append((example.example_id, "unauthenticated/unreplayed/self-graded"))
            return False
        if example.generator_lineage == self.trained_lineage and \
                example.evaluator_lineage == self.trained_lineage:
            self.rejected.append((example.example_id, "evaluator same as trained model"))
            return False
        self.accepted.append(example)
        return True

    def training_set_hashable(self) -> list[str]:
        return sorted(e.example_id for e in self.accepted)
