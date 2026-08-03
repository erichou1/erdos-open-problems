"""Search plane (Module G): mechanism, debt, blueprint, dedup, failure, bands, controller."""

from egmra.search.algorithms import (
    SEARCH_LEVEL_ALGORITHMS,
    ao_star_next_leaf,
    debate_output_role,
    evolution_allowed,
    route_search_level,
    ucb1,
)
from egmra.search.bands import BANDS, ComputeBand, band, can_expand, reserve_amount
from egmra.search.blueprint import AndOrBlueprint, Node
from egmra.search.controller import (
    ActionComponents,
    BranchPosterior,
    Controller,
    UtilityWeights,
    branch_action_utility,
)
from egmra.search.dedup import DedupVerdict, dedup_cascade, exact_key, jaccard
from egmra.search.failure import (
    CENSORED_REASONS,
    KILL_REASONS,
    FailureCertificate,
    disposition,
    is_censored,
    make_failure_certificate,
)
from egmra.search.mechanism import (
    METHOD_FAMILIES,
    MechanismFingerprint,
    QualityDiversityArchive,
)
from egmra.search.programs import (
    ResearchProgram,
    compatible_families,
    instantiate_programs,
)
from egmra.search.verified_debt import (
    DebtPolicy,
    Obligation,
    credit_for_action,
    delta_verified_debt,
    verified_debt,
)

__all__ = [
    "SEARCH_LEVEL_ALGORITHMS", "ao_star_next_leaf", "debate_output_role",
    "evolution_allowed", "route_search_level", "ucb1",
    "BANDS", "ComputeBand", "band", "can_expand", "reserve_amount",
    "AndOrBlueprint", "Node",
    "ActionComponents", "BranchPosterior", "Controller", "UtilityWeights",
    "branch_action_utility",
    "DedupVerdict", "dedup_cascade", "exact_key", "jaccard",
    "CENSORED_REASONS", "KILL_REASONS", "FailureCertificate", "disposition",
    "is_censored", "make_failure_certificate",
    "METHOD_FAMILIES", "MechanismFingerprint", "QualityDiversityArchive",
    "ResearchProgram", "compatible_families", "instantiate_programs",
    "DebtPolicy", "Obligation", "credit_for_action", "delta_verified_debt", "verified_debt",
]
