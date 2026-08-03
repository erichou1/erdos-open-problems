"""OEIS service (Module C): typed transforms, read-only client, matching workflow."""

from egmra.oeis.client import (
    OEIS_AI_SUBMISSION_FORBIDDEN,
    OEISClient,
    OEISPolicyError,
    OEISResponse,
    OEISUnavailable,
)
from egmra.oeis.matching import (
    HeldOutResult,
    Match,
    OEISWorkflowResult,
    build_conjecture_claim,
    enumerate_transform_paths,
    held_out_verification,
    prefix_overlap,
    run_oeis_workflow,
    score_match,
)
from egmra.oeis.transforms import (
    REGISTERED_TRANSFORMS,
    TransformError,
    TransformSpec,
    TransformStep,
    apply_path,
    apply_transform,
    get_transform,
)

__all__ = [
    "OEIS_AI_SUBMISSION_FORBIDDEN", "OEISClient", "OEISPolicyError",
    "OEISResponse", "OEISUnavailable",
    "HeldOutResult", "Match", "OEISWorkflowResult", "build_conjecture_claim",
    "enumerate_transform_paths", "held_out_verification", "prefix_overlap",
    "run_oeis_workflow", "score_match",
    "REGISTERED_TRANSFORMS", "TransformError", "TransformSpec", "TransformStep",
    "apply_path", "apply_transform", "get_transform",
]
