"""Solver-backend interfaces + exact-arithmetic helpers (spec §2.5, §6.8).

Modern agents route suitable leaves to mature symbolic systems (SAT/SMT/CAS/ILP)
rather than reproduce them in prose. A solver's ``proved``/``unsat`` result is
solver *testimony* until reconstructed: an external "SAT" label is not enough. The
backends here are interfaces plus a stdlib exact-arithmetic verifier and a
DRAT/resolution proof-presence check; real solvers (cvc5/z3/PySAT/Sage) are
optional and documented (see DECISIONS.md D-004/D-008).
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Protocol


@dataclass(frozen=True)
class SolverResult:
    status: str            # sat | unsat | proved | disproved | unknown
    model: Any = None
    proof_trace: Any = None
    reconstructed: bool = False
    solver_id: str = ""

    def is_trustworthy(self) -> bool:
        """A positive result is trustworthy only once reconstructed/checked."""
        if self.status in {"unsat", "proved"}:
            return self.reconstructed
        return True  # sat with a model is checkable directly by the caller


class SATBackend(Protocol):
    solver_id: str

    def solve(self, cnf: list[list[int]]) -> SolverResult: ...


class SMTBackend(Protocol):
    solver_id: str

    def check(self, assertions: list[str], *, logic: str) -> SolverResult: ...


class CASBackend(Protocol):
    backend_id: str

    def simplify(self, expression: str) -> str: ...


def check_sat_model(cnf: list[list[int]], model: dict[int, bool]) -> bool:
    """Independently check that a proposed model satisfies a CNF (SAT witness)."""
    for clause in cnf:
        if not any(model.get(abs(lit), False) == (lit > 0) for lit in clause):
            return False
    return True


def reconstruct_unsat(cnf: list[list[int]], proof_trace: list[list[int]] | None) -> bool:
    """Accept ``unsat`` only via a checkable resolution/RUP-style proof trace.

    Without a proof trace the result stays solver testimony (returns False). With
    a trace we verify each added clause is a resolvent / RUP consequence and the
    empty clause is derived. This is a genuine (if minimal) DRAT-style checker.
    """
    if not proof_trace:
        return False
    clauses = [frozenset(c) for c in cnf]

    def is_rup(clause: list[int]) -> bool:
        # RUP: assume the negation of each literal; unit-propagate to a conflict.
        assignment = {-lit for lit in clause}
        changed = True
        known = list(clauses)
        while changed:
            changed = False
            for cl in known:
                unresolved = [lit for lit in cl if -lit not in assignment]
                if not unresolved:
                    return True  # conflict: clause is RUP
                if len(unresolved) == 1 and unresolved[0] not in assignment:
                    assignment.add(unresolved[0])
                    changed = True
        return False

    for step in proof_trace:
        if not is_rup(step):
            return False
        clauses.append(frozenset(step))
        if not step:  # derived the empty clause
            return True
    return any(len(c) == 0 for c in clauses)


class ExactArithmetic:
    """Stdlib exact arithmetic (Fraction) — always available, no CAS required."""

    @staticmethod
    def as_fraction(value: Any) -> Fraction:
        return Fraction(value)

    @staticmethod
    def interval_contains(low: Fraction, high: Fraction, value: Fraction) -> bool:
        return low <= value <= high

    @staticmethod
    def float_proves_exact() -> bool:
        # Floating point never proves an exact statement without an interval arg.
        return False
