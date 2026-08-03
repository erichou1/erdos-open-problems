"""§9.4 — missing library results workflow (spec §9.4)."""

from __future__ import annotations

from dataclasses import dataclass, field


# ── §9.4 missing library workflow ────────────────────────────────────────────

MISSING_LIBRARY_STEPS = (
    "verify_truly_absent",
    "import_audit_informal",
    "create_local_namespace",
    "decompose_reusable_lemmas",
    "prove_independent_of_target",
    "assign_reuse_value",
    "upstream_after_review",
)


@dataclass
class MissingLibraryWorkflow:
    theorem_name: str
    completed_steps: list[str] = field(default_factory=list)
    reuse_value: float = 0.0

    def complete(self, step: str) -> None:
        if step not in MISSING_LIBRARY_STEPS:
            raise ValueError(f"unknown step {step!r}")
        expected = MISSING_LIBRARY_STEPS[len(self.completed_steps)] if len(self.completed_steps) < len(MISSING_LIBRARY_STEPS) else None
        if step != expected:
            raise ValueError(f"steps must be completed in order; expected {expected!r}")
        self.completed_steps.append(step)

    @property
    def ready_to_upstream(self) -> bool:
        return self.completed_steps == list(MISSING_LIBRARY_STEPS)
