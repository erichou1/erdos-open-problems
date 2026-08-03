"""Ten required adversarial attacks + taint-aware dependency labels (spec §11.2)."""

from __future__ import annotations

from dataclasses import dataclass, field

REQUIRED_ATTACKS = (
    "target_diff",
    "quantifier_domain_audit",
    "dependency_trace",
    "circularity",
    "import_challenge",
    "countermodel_search",
    "independent_computation",
    "formal_audit",
    "proof_reconstruction",
    "novelty_significance_firewall",
)

# Taint labels that propagate to every dependent conclusion until discharged.
TAINT_LABELS = ("circular", "unreviewed_import", "numerical_only", "semantic_risk")


@dataclass(frozen=True)
class AttackResult:
    attack: str
    passed: bool
    defect: str = ""
    affected_claims: tuple[str, ...] = ()
    taint: str = ""

    def __post_init__(self) -> None:
        if self.attack not in REQUIRED_ATTACKS:
            raise ValueError(f"unknown attack {self.attack!r}")
        if self.taint and self.taint not in TAINT_LABELS:
            raise ValueError(f"unknown taint label {self.taint!r}")
        if self.passed and (self.defect or self.taint or self.affected_claims):
            raise ValueError("a passing attack cannot report a defect, taint, or affected claim")
        if not self.passed and not self.defect:
            raise ValueError("a failing attack requires a reproducible defect description")


@dataclass(frozen=True)
class AttackReport:
    results: tuple[AttackResult, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        attacks = [result.attack for result in self.results]
        if len(attacks) != len(set(attacks)):
            raise ValueError("duplicate attack results are not independent coverage")

    def missing_attacks(self) -> list[str]:
        run = {r.attack for r in self.results}
        return [a for a in REQUIRED_ATTACKS if a not in run]

    def complete(self) -> bool:
        return not self.missing_attacks()

    def defects(self) -> list[AttackResult]:
        return [r for r in self.results if not r.passed]

    def first_invalid_dependency(self) -> str:
        for r in self.results:
            if not r.passed and r.affected_claims:
                return r.affected_claims[0]
        return ""


def propagate_taint(
    dependency_edges: dict[str, list[str]], tainted: dict[str, str]
) -> dict[str, str]:
    """Propagate taint labels along claim -> dependent edges until fixpoint."""
    result = dict(tainted)
    changed = True
    while changed:
        changed = False
        for claim, dependents in dependency_edges.items():
            if claim in result:
                for dep in dependents:
                    if dep not in result:
                        result[dep] = result[claim]
                        changed = True
    return result
