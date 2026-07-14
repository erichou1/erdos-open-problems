"""Lean formal-verification plane (Module I): staged L0-L5 + service API."""

from egmra.lean.aristotle_routing import (
    QUARANTINE_SANDBOX_POLICY,
    RETURNED_LEAN_PIPELINE,
    AristotleRequest,
    AristotleRouting,
    ProviderAttestation,
)
from egmra.lean.aristotle_api import (
    VENDOR_COMPLETE_STATUSES,
    VENDOR_FAILURE_STATUSES,
    AristotleApiClient,
    AristotleArtifact,
    AristotleClientError,
    AristotleStatus,
    AristotleTransport,
    AristotleTransportError,
    HttpAristotleTransport,
    LocalLeanReplayAttestation,
    LocalReplayResult,
    UnsafeArchiveError,
    UnsafeJobIdError,
    hash_quarantine_tree,
    safe_extract_archive,
    scan_quarantine_tree,
    seal_local_lean_replay_attestation,
    validate_job_id,
    verify_local_lean_replay_attestation,
    verify_local_replay,
)
from egmra.lean.aristotle_sdk import (
    ARISTOTLE_LEAN_TOOLCHAIN,
    ARISTOTLE_MATHLIB_REV,
    AristotleSdkClient,
    AristotleSdkUnavailable,
    AristotleSubmission,
)
from egmra.lean.blueprint import BlueprintError, FormalBlueprint, FormalHole
from egmra.lean.coverage import (
    CoverageClaim,
    ExpensiveClaimPolicy,
    FrozenBlueprintWeights,
    freeze_blueprint,
    risk_weighted_formal_coverage,
)
from egmra.lean.correspondence import (
    FormalCorrespondenceAuthError,
    sign_formal_correspondence_certificate,
    verify_formal_correspondence_certificate,
)
from egmra.lean.hardening import ArchiveManifest, HardeningReport, harden
from egmra.lean.missing_library import MISSING_LIBRARY_STEPS, MissingLibraryWorkflow
from egmra.lean.proof_state import (
    PROOF_PORTFOLIO,
    ProofAction,
    TranspositionTable,
    puct_score,
    route_diagnostic,
)
from egmra.lean.replay import KernelChecker, LeanReplayTarget, LeanReplayVerifier
from egmra.lean.sentinels import (
    SENTINEL_KINDS,
    FormalizationPriority,
    formalization_priority,
    select_sentinels,
)
from egmra.lean.service import (
    AttestedKernelRunner,
    CheckedEquivalenceProof,
    CheckerAttestation,
    CheckerConfigurationError,
    CheckerRequest,
    DEFAULT_AXIOM_WHITELIST,
    FORBIDDEN_AXIOMS,
    EquivalenceAttempt,
    FormalCertificate,
    GoalCapsule,
    LeanEnvironment,
    LeanService,
    LeanServiceError,
    verify_formal_certificate,
)
from egmra.lean.sync import ProofSync, SyncLink
from egmra.lean.target_package import LeanCandidate, TargetPackage, build_target_package

__all__ = [
    "QUARANTINE_SANDBOX_POLICY", "RETURNED_LEAN_PIPELINE", "AristotleRequest",
    "AristotleRouting", "ProviderAttestation",
    "VENDOR_COMPLETE_STATUSES", "VENDOR_FAILURE_STATUSES", "AristotleApiClient",
    "AristotleArtifact", "AristotleClientError", "AristotleStatus", "AristotleTransport",
    "AristotleTransportError", "HttpAristotleTransport", "LocalReplayResult",
    "LocalLeanReplayAttestation", "UnsafeArchiveError", "UnsafeJobIdError",
    "hash_quarantine_tree", "safe_extract_archive", "scan_quarantine_tree",
    "seal_local_lean_replay_attestation", "validate_job_id",
    "verify_local_lean_replay_attestation", "verify_local_replay",
    "ARISTOTLE_LEAN_TOOLCHAIN", "ARISTOTLE_MATHLIB_REV", "AristotleSdkClient",
    "AristotleSdkUnavailable", "AristotleSubmission",
    "BlueprintError", "FormalBlueprint", "FormalHole",
    "CoverageClaim", "ExpensiveClaimPolicy", "FrozenBlueprintWeights",
    "freeze_blueprint", "risk_weighted_formal_coverage",
    "FormalCorrespondenceAuthError", "sign_formal_correspondence_certificate",
    "verify_formal_correspondence_certificate",
    "ArchiveManifest", "HardeningReport", "harden",
    "MISSING_LIBRARY_STEPS", "MissingLibraryWorkflow",
    "PROOF_PORTFOLIO", "ProofAction", "TranspositionTable", "puct_score", "route_diagnostic",
    "KernelChecker", "LeanReplayTarget", "LeanReplayVerifier",
    "SENTINEL_KINDS", "FormalizationPriority", "formalization_priority", "select_sentinels",
    "DEFAULT_AXIOM_WHITELIST", "FORBIDDEN_AXIOMS", "EquivalenceAttempt",
    "AttestedKernelRunner", "CheckedEquivalenceProof", "CheckerAttestation",
    "CheckerConfigurationError", "CheckerRequest",
    "FormalCertificate", "GoalCapsule", "LeanEnvironment", "LeanService", "LeanServiceError",
    "verify_formal_certificate",
    "ProofSync", "SyncLink",
    "LeanCandidate", "TargetPackage", "build_target_package",
]
