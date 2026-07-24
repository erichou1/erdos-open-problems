"""Verification plane (Module J): referee, attacks, standards, aggregation."""

from egmra.verification.aggregation import (
    AggregationResult,
    ConflictResolution,
    ReviewVerdict,
    aggregate,
)
from egmra.verification.attacks import (
    REQUIRED_ATTACKS,
    TAINT_LABELS,
    AttackReport,
    AttackResult,
    propagate_taint,
)
from egmra.verification.referee import (
    AdversarialReferee,
    DiversityProfile,
    RefereeResult,
)
from egmra.verification.standards import (
    FORMAL_STATES,
    INTENT_STATES,
    NOVELTY_STATES,
    REPRODUCIBILITY_STATES,
    SIGNIFICANCE_STATES,
    TRUTH_LEVELS,
    TRUTH_REQUIREMENTS,
    lean_verified_available,
    novel_autonomous_resolution_requirements,
    publication_requirements,
    truth_level,
)

__all__ = [
    "AggregationResult", "ConflictResolution", "ReviewVerdict", "aggregate",
    "REQUIRED_ATTACKS", "TAINT_LABELS", "AttackReport", "AttackResult", "propagate_taint",
    "AdversarialReferee", "DiversityProfile", "RefereeResult",
    "FORMAL_STATES", "INTENT_STATES", "NOVELTY_STATES", "REPRODUCIBILITY_STATES",
    "SIGNIFICANCE_STATES", "TRUTH_LEVELS", "TRUTH_REQUIREMENTS", "lean_verified_available",
    "novel_autonomous_resolution_requirements", "publication_requirements", "truth_level",
]
