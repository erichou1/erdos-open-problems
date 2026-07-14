"""Mechanism fingerprint + quality-diversity archive (spec §7.4).

Every top-level research program supplies a nine-field mechanism fingerprint. The
archive uses quality-diversity bins (method family, proof/disproof,
analytic/combinatorial/algebraic/computational, finite/infinite, literature
dependence) so genuinely different mechanisms are preserved rather than collapsed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

from egmra.provenance.hashing import content_id

METHOD_FAMILIES = (
    "direct_structural", "contradiction_minimal_counterexample", "extremal_invariant",
    "probabilistic_analytic", "additive_combinatorial", "algebraic_spectral",
    "geometric_topological", "ergodic_dynamical", "computational_finite_reduction",
    "formal_library_first", "literature_derived_transfer", "counterexample_model_construction",
)


@dataclass(frozen=True)
class MechanismFingerprint:
    target_interpretation: str
    reformulation: str
    method_family: str
    central_proposed_lemma: str
    objects_invariants: tuple[str, ...] = ()
    external_theorems: tuple[str, ...] = ()
    computational_signature: str = ""
    expected_falsifiers: tuple[str, ...] = ()
    formalization_route: str = ""

    def __post_init__(self) -> None:
        if self.method_family not in METHOD_FAMILIES:
            raise ValueError(f"unknown method family {self.method_family!r}")

    def fingerprint_hash(self) -> str:
        return content_id({
            "interp": self.target_interpretation,
            "reformulation": self.reformulation,
            "method_family": self.method_family,
            "central_lemma": self.central_proposed_lemma,
            "objects": sorted(self.objects_invariants),
            "external": sorted(self.external_theorems),
            "computational": self.computational_signature,
            "expected_falsifiers": sorted(self.expected_falsifiers),
            "formalization": self.formalization_route,
        })

    def quality_diversity_bin(self) -> tuple[str, ...]:
        """The QD archive bin (spec §7.4)."""
        analytic = _analytic_axis(self.method_family)
        finite = "finite" if "finite" in self.computational_signature or "finite" in self.reformulation.lower() else "infinite"
        lit = "literature" if self.external_theorems else "self_contained"
        goal = "disproof" if "counterexample" in self.method_family else "proof"
        return (self.method_family, goal, analytic, finite, lit)


def _analytic_axis(family: str) -> str:
    mapping = {
        "probabilistic_analytic": "analytic",
        "additive_combinatorial": "combinatorial",
        "extremal_invariant": "combinatorial",
        "algebraic_spectral": "algebraic",
        "geometric_topological": "algebraic",
        "computational_finite_reduction": "computational",
        "counterexample_model_construction": "computational",
    }
    return mapping.get(family, "structural")


@dataclass
class QualityDiversityArchive:
    """MAP-Elites-style archive: one champion per (bin, quality) cell (spec §6.7)."""

    cells: dict[tuple, dict] = field(default_factory=dict)

    def consider(self, fingerprint: MechanismFingerprint, *, quality: float, branch_id: str) -> bool:
        """Admit a branch if it wins its diversity cell. Returns True if admitted."""
        if not math.isfinite(quality):
            raise ValueError("archive quality must be finite")
        if not isinstance(branch_id, str) or not branch_id:
            raise ValueError("branch_id must be a non-empty string")
        bin_key = fingerprint.quality_diversity_bin()
        current = self.cells.get(bin_key)
        if current is None or quality > current["quality"]:
            self.cells[bin_key] = {"branch_id": branch_id, "quality": quality,
                                   "fingerprint": fingerprint.fingerprint_hash()}
            return True
        return False

    def diversity_coverage(self) -> int:
        return len(self.cells)

    def champions(self) -> list[str]:
        return [cell["branch_id"] for cell in self.cells.values()]
