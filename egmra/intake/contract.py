"""ProblemContract: the frozen output of intake (spec §6.1).

Builds on the current byte-level lock without discarding it. Runs two independent
parses, reconciles, builds the interpretation lattice, and runs integrity probes,
producing a content-addressed contract plus a target-fidelity risk score and the
set of unresolved decisions. Directly addresses the wrong-intent / vacuity failure
mode from the Aletheia Erdős sweep.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Callable, Iterable

from egmra.intake.interpretation import InterpretationLattice, build_interpretation_lattice
from egmra.intake.probes import Probe, probes_hash, run_integrity_probes
from egmra.intake.statement_ir import (
    ClauseParser,
    GrammarParser,
    Parser,
    Reconciliation,
    StatementIR,
    reconcile,
)
from egmra.provenance.hashing import content_id, sha256_bytes


@dataclass
class ProblemContract:
    problem_id: str
    source_id: str
    source_bytes_hash: str
    source_bytes_b64: str
    source_spans: list[dict]
    statement_ir_hash: str
    primary_ir: StatementIR
    reconciliation: Reconciliation
    lattice: InterpretationLattice
    probes: list[Probe]
    target_fidelity_risk: float
    unresolved_decisions: list[str]
    status_audit_request: dict = field(default_factory=dict)

    @property
    def release_blocked(self) -> bool:
        return (
            self.lattice.release_blocked
            or any(not p.passed for p in self.probes)
            or any(decision.startswith("malformed:") for decision in self.unresolved_decisions)
        )

    def contract_hash(self) -> str:
        return content_id(
            {
                "problem_id": self.problem_id,
                "source_id": self.source_id,
                "source_bytes_hash": self.source_bytes_hash,
                "statement_ir_hash": self.statement_ir_hash,
                "lattice": self.lattice.to_dict(),
                "probes_hash": probes_hash(self.probes),
                "target_fidelity_risk": self.target_fidelity_risk,
            }
        )

    def to_dict(self) -> dict:
        return {
            "problem_id": self.problem_id,
            "source_id": self.source_id,
            "source_bytes_hash": self.source_bytes_hash,
            "source_bytes_b64": self.source_bytes_b64,
            "source_spans": list(self.source_spans),
            "statement_ir_hash": self.statement_ir_hash,
            "primary_ir": self.primary_ir.to_dict(),
            "reconciliation": {
                "agreed": self.reconciliation.agreed,
                "disagreements": list(self.reconciliation.disagreements),
                "ambiguity_nodes": list(self.reconciliation.ambiguity_nodes),
            },
            "lattice": self.lattice.to_dict(),
            "probes": [p.to_dict() for p in self.probes],
            "target_fidelity_risk": self.target_fidelity_risk,
            "unresolved_decisions": list(self.unresolved_decisions),
            "status_audit_request": dict(self.status_audit_request),
            "contract_hash": self.contract_hash(),
            "release_blocked": self.release_blocked,
        }


def build_problem_contract(
    *,
    problem_id: str,
    source_bytes: bytes,
    source_id: str,
    parser_a: Parser | None = None,
    parser_b: Parser | None = None,
    predicate: Callable[[int], bool] | None = None,
    boundary_points: Iterable[int] = (0, 1, 2),
    search_space: Iterable[int] = range(0, 64),
) -> ProblemContract:
    """Run the full intake pipeline and freeze a ProblemContract."""
    parser_a = parser_a or GrammarParser()
    parser_b = parser_b or ClauseParser()
    primary = parser_a.parse(source_bytes, source_id)
    secondary = parser_b.parse(source_bytes, source_id)
    recon = reconcile(primary, secondary)
    lattice = build_interpretation_lattice(problem_id, recon)
    probes = run_integrity_probes(
        source_bytes, source_id, primary, parser=parser_a,
        predicate=predicate, boundary_points=boundary_points, search_space=search_space,
    )

    unresolved = list(recon.ambiguity_nodes)
    unresolved += [f"probe_failed:{p.name}" for p in probes if not p.passed]
    if not source_bytes.strip() or not primary.conclusion.strip():
        unresolved.append("malformed:empty_statement")

    return ProblemContract(
        problem_id=problem_id,
        source_id=source_id,
        source_bytes_hash=sha256_bytes(source_bytes),
        source_bytes_b64=base64.b64encode(source_bytes).decode("ascii"),
        source_spans=[dict(span) for span in primary.source_spans],
        statement_ir_hash=primary.semantic_hash(),
        primary_ir=primary,
        reconciliation=recon,
        lattice=lattice,
        probes=probes,
        target_fidelity_risk=recon.target_fidelity_risk(),
        unresolved_decisions=unresolved,
        status_audit_request={
            "problem_id": problem_id,
            "exact_wording": source_bytes.decode("utf-8", errors="replace")[:2000],
            "requested": ["known", "open", "false", "misquoted", "ambiguous", "status_uncertain"],
        },
    )
