"""Selection plane (Module B): features, competing-risk posterior, acquisition."""

from egmra.selection.acquisition import (
    AcquisitionScore,
    AcquisitionWeights,
    ProblemSelector,
    acquisition_score,
)
from egmra.selection.features import ProblemFeatures
from egmra.selection.posterior import (
    DEFAULT_OUTCOME_VALUES,
    OUTCOMES,
    CompetingRiskPosterior,
)

__all__ = [
    "AcquisitionScore", "AcquisitionWeights", "ProblemSelector", "acquisition_score",
    "ProblemFeatures",
    "DEFAULT_OUTCOME_VALUES", "OUTCOMES", "CompetingRiskPosterior",
]
