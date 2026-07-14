"""Parallelization policy + reserved verifier pool (spec §14.3).

Parallelize independent work; serialize or transactionally coordinate interpretation
approval, target-hash changes, claim promotion/revocation, schema migrations, final
assembly, release certificates, and shared quota/backoff state. Work stealing is
allowed only among compatible workers. Verification workers have a *reserved pool*
so proof generation cannot starve truth admission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import threading

PARALLELIZABLE = frozenset({
    "independent_interpretations", "status_queries", "different_research_programs",
    "and_node_leaves", "proof_counterexample_twins", "retrieval_modes",
    "citation_expansion", "finite_experiments", "lean_tactic_branches",
    "independent_verification_replay",
})

SERIALIZE = frozenset({
    "interpretation_approval", "target_hash_change", "claim_promotion",
    "claim_revocation", "graph_schema_migration", "final_proof_assembly",
    "release_certificate", "provider_quota_backoff",
})


class ParallelPolicyError(RuntimeError):
    pass


def can_parallelize(operation: str) -> bool:
    if operation in PARALLELIZABLE:
        return True
    if operation in SERIALIZE:
        return False
    raise ParallelPolicyError(f"unclassified operation {operation!r}")


def must_serialize(operation: str) -> bool:
    return not can_parallelize(operation)


@dataclass
class VerifierPool:
    """Reserved verification capacity so proof generation can't starve truth."""

    total_workers: int
    reserved_for_verification: int
    active_verification: int = 0
    active_generation: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.total_workers <= 0:
            raise ParallelPolicyError("total workers must be positive")
        if not 0 <= self.reserved_for_verification <= self.total_workers:
            raise ParallelPolicyError("reserved verification workers must be between zero and total")
        if self.active_generation < 0 or self.active_verification < 0:
            raise ParallelPolicyError("active worker counts cannot be negative")
        if self.active_generation + self.active_verification > self.total_workers:
            raise ParallelPolicyError("active workers exceed total capacity")

    def can_start_generation(self) -> bool:
        # Generation may use only the non-reserved capacity.
        available = self.total_workers - self.reserved_for_verification
        return (self.active_generation < available
                and self.active_generation + self.active_verification < self.total_workers)

    def can_start_verification(self) -> bool:
        return self.active_generation + self.active_verification < self.total_workers

    def start_generation(self) -> bool:
        with self._lock:
            if not self.can_start_generation():
                return False
            self.active_generation += 1
            return True

    def start_verification(self) -> bool:
        with self._lock:
            if not self.can_start_verification():
                return False
            self.active_verification += 1
            return True

    def finish_generation(self) -> None:
        with self._lock:
            if self.active_generation <= 0:
                raise ParallelPolicyError("generation worker count underflow")
            self.active_generation -= 1

    def finish_verification(self) -> None:
        with self._lock:
            if self.active_verification <= 0:
                raise ParallelPolicyError("verification worker count underflow")
            self.active_verification -= 1
