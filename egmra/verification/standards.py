"""Verification standards: truth tiers T0-T5 + orthogonal dimensions (spec §11.3).

"Lean-verified" is available at T4 for the exact encoded theorem. Publication of
untrusted generated Lean requires T5. An informal proof establishes the intended
statement only with T3 plus I2. The dimensions are reported as a *profile*, never
collapsed into one V-level or a "confidence %".
"""

from __future__ import annotations

from egmra.truth.entities import (
    EvidenceProfile,
    ExactComputation,
    ExternalImport,
    FormalVerification,
    InformalReview,
    NumericalEvidence,
)

TRUTH_LEVELS = ("T0", "T1", "T2", "T3", "T4", "T5")

TRUTH_REQUIREMENTS = {
    "T0": "clearly marked hypothesis; no evidential claim",
    "T1": "reproducible tests/numerics with scope and counterexample search",
    "T2": "exact witness, exhaustive finite coverage, or checked certificate; scope explicit",
    "T3": "complete dependency/source audit plus two genuinely independent hostile reconstructions",
    "T4": "clean pinned kernel replay, exact expected-type check, transitive axiom/import audit, no holes",
    "T5": "T4 plus isolated immutable target module and an independent checker for untrusted Lean",
}

INTENT_STATES = ("I0", "I1", "I2")
FORMAL_STATES = ("F0", "F1", "F2", "N/A")
NOVELTY_STATES = ("N0", "N1", "N2", "known")
SIGNIFICANCE_STATES = ("S0", "S1", "S2")
REPRODUCIBILITY_STATES = ("R0", "R1", "R2")


def truth_level(
    profile: EvidenceProfile, *, high_value: bool = False, hardened: bool = False,
    dependency_audit_complete: bool = False,
) -> str:
    """Compute the truth tier for a claim from its evidence profile.

    ``high_value`` claims need T3's *two* independent reviews; ``hardened`` marks
    the T4->T5 promotion (isolated module + independent checker).
    """
    fv = profile.formal_verification
    # A caller-owned ``hardened`` flag is not an independent-checker artifact.
    # T5 is encoded only by the separately validated INDEPENDENT_CHECKER state.
    if fv == FormalVerification.INDEPENDENT_CHECKER:
        return "T5"
    if fv == FormalVerification.KERNEL_CHECKED:
        return "T4"
    if profile.informal_review == InformalReview.DOUBLE_INDEPENDENT and dependency_audit_complete:
        return "T3"
    if profile.exact_computation in (ExactComputation.SCOPED_EXACT, ExactComputation.CERTIFICATE_CHECKED):
        return "T2"
    if profile.external_import == ExternalImport.INDEPENDENTLY_CORROBORATED:
        return "T2"
    if profile.numerical == NumericalEvidence.REPRODUCIBLE:
        return "T1"
    if profile.informal_review == InformalReview.SINGLE:
        return "T1"
    return "T0"


def lean_verified_available(level: str) -> bool:
    """'Lean-verified' language is only available at T4+ (spec §11.3)."""
    return level in ("T4", "T5")


def publication_requirements(*, informal_only: bool) -> dict[str, str]:
    """The tier profile required for a claimed resolution (spec §11.3)."""
    if informal_only:
        return {"truth": "T3", "intent": "I2", "formal": "N/A"}
    return {"truth": "T5", "intent": "I2", "formal": "F2"}


def novel_autonomous_resolution_requirements() -> dict[str, str]:
    """A 'novel autonomous resolution' additionally needs N2, S2, R2 + autonomy metadata."""
    return {"novelty": "N2", "significance": "S2", "reproducibility": "R2",
            "autonomy": "phase-by-phase intervention taxonomy required"}
