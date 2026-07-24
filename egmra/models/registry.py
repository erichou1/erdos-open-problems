"""Model registry + local bake-off (spec §14.2).

Model names change faster than the architecture. Select exact versions through a
monthly *local* bake-off by task/domain, then pin them for a campaign. Never route
by vendor benchmark score alone. Persist the exact model identity; "ChatGPT",
"Claude", or "Gemini" is not a reproducible version.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from egmra.provenance.stage_identity import AttestedModelIdentity

# Task classes and their selection criteria (spec §14.2 table).
TASK_SELECTION_CRITERIA = {
    "intake_reconciliation": "semantic mutation/faithfulness accuracy",
    "broad_program_generation": "verified novel-branch yield per cost",
    "central_bottleneck": "blind historical-Erdos verified progress",
    "literature_extraction": "theorem/hypothesis recall and precision",
    "code_experiments": "exact artifact validity and repair rate",
    "lean_proof_search": "clean proof rate at matched cost/toolchain",
    "high_budget_formal": "additional clean locally-replayed proofs",
    "informal_referee": "first-error recall, low false acceptance",
    "final_truth": "deterministic acceptance only",
    "novelty_significance": "audited search coverage and expert agreement",
}


@dataclass(frozen=True)
class BakeOffResult:
    task: str
    model: AttestedModelIdentity
    local_score: float
    measured_at: str


@dataclass
class ModelRegistry:
    """Pin exact models per task from local bake-off results."""

    pinned: dict[str, AttestedModelIdentity] = field(default_factory=dict)
    bakeoffs: list[BakeOffResult] = field(default_factory=list)

    def record_bakeoff(self, result: BakeOffResult) -> None:
        if result.task not in TASK_SELECTION_CRITERIA:
            raise KeyError(f"unknown task {result.task!r}")
        self.bakeoffs.append(result)

    def pin_best(self, task: str) -> AttestedModelIdentity:
        """Pin the locally-best model for a task (never by vendor benchmark)."""
        candidates = [b for b in self.bakeoffs if b.task == task]
        if not candidates:
            raise ValueError(f"no local bake-off results for task {task!r}")
        best = max(candidates, key=lambda b: b.local_score)
        if not best.model.attested:
            raise ValueError("cannot pin an unattested model label as a reproducible version")
        self.pinned[task] = best.model
        return best.model

    def resolve(self, task: str) -> AttestedModelIdentity:
        if task not in self.pinned:
            raise KeyError(f"no pinned model for task {task!r}; run a bake-off and pin first")
        return self.pinned[task]
