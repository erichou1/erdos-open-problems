"""Runtime role layout (spec §13.5).

Only four concurrent roles are normally needed in M1; retrieval, OEIS, computation,
Lean, and the graph are *services*, not idle chat tabs. M2 scales workers only when
the queue contains independent bottlenecks.
"""

from __future__ import annotations

from dataclasses import dataclass

RUNTIME_ROLES = (
    "governor_intake",
    "program_worker",          # one or two, method-specific
    "compute_or_formal_worker",  # selected by the current bottleneck
    "adversarial_verifier",
)

SERVICES = (
    "retrieval", "oeis", "computation", "lean", "claim_graph",
)


@dataclass(frozen=True)
class RoleLayout:
    max_program_workers: int = 2
    reserved_verifier_workers: int = 1

    def concurrent_roles(self) -> tuple[str, ...]:
        return RUNTIME_ROLES

    def services(self) -> tuple[str, ...]:
        return SERVICES

    def total_concurrent(self) -> int:
        # governor + up to N program workers + 1 compute/formal + 1 verifier
        return 1 + self.max_program_workers + 1 + self.reserved_verifier_workers
