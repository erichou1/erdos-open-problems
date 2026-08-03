"""Evaluation plane (Section 12): levels, protocol, metrics, progress, ablations, stats, datasets."""

from egmra.eval.ablations import (
    REQUIRED_ABLATIONS,
    AblationRegistry,
    PreRegistration,
)
from egmra.eval.datasets import (
    EVAL_SET_COMPOSITION,
    FIXTURE_PROBLEMS,
    PINNED_BENCHMARKS,
    FixtureProblem,
    fixture,
)
from egmra.eval.levels import LEVELS, TRACKS, level, requires_tracks, scores_accuracy
from egmra.eval.metrics import (
    EfficiencyMetrics,
    FinalOutcomeMetrics,
    IntermediateProgressMetrics,
    SearchQualityMetrics,
    rfc,
)
from egmra.eval.progress import (
    DURABLE_OBJECTS,
    ZERO_VALUE_SIGNALS,
    ProgressLedger,
    is_progress,
    manuscript_beats_counterexample,
)
from egmra.eval.protocol import (
    REQUIRED_BASELINES,
    CausalAblationSpec,
    EvalRun,
    FrozenEvalConfig,
    TimeCapsule,
    baseline_comparison_valid,
)
from egmra.eval.stats import (
    ReportedResult,
    StatisticalPolicyError,
    compare_pass_at_k,
    dev_eval_separated,
    requires_two_blind_experts,
    treat_recent_preprint_as_hypothesis,
)

__all__ = [
    "REQUIRED_ABLATIONS", "AblationRegistry", "PreRegistration",
    "EVAL_SET_COMPOSITION", "FIXTURE_PROBLEMS", "PINNED_BENCHMARKS", "FixtureProblem", "fixture",
    "LEVELS", "TRACKS", "level", "requires_tracks", "scores_accuracy",
    "EfficiencyMetrics", "FinalOutcomeMetrics", "IntermediateProgressMetrics",
    "SearchQualityMetrics", "rfc",
    "DURABLE_OBJECTS", "ZERO_VALUE_SIGNALS", "ProgressLedger", "is_progress",
    "manuscript_beats_counterexample",
    "REQUIRED_BASELINES", "CausalAblationSpec", "EvalRun", "FrozenEvalConfig",
    "TimeCapsule", "baseline_comparison_valid",
    "ReportedResult", "StatisticalPolicyError", "compare_pass_at_k", "dev_eval_separated",
    "requires_two_blind_experts", "treat_recent_preprint_as_hypothesis",
]
