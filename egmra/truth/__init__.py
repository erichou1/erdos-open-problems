"""Truth plane: interpretations, claims, evidence, dependencies, revocation, gates."""

from egmra.truth.entities import (
    Branch,
    Claim,
    Evidence,
    EvidenceKind,
    EvidenceProfile,
    ExactComputation,
    ExternalImport,
    FormalCorrespondenceCertificate,
    FormalVerification,
    InformalReview,
    IntentCertificate,
    Interpretation,
    Lifecycle,
    NumericalEvidence,
    Problem,
    Relation,
    RelationType,
    TruthStatus,
    Verdict,
)
from egmra.truth.events import ACTIONS, Event, EventLog, EventLogError
from egmra.truth.graph import EpistemicGraph, GraphError
from egmra.truth.revocation import (
    invalidate_evidence,
    refute_claim,
    strongly_connected_components,
)
from egmra.truth.router import EvidenceRouter
from egmra.truth.snapshots import TruthSnapshot, TruthSnapshotError, issue_truth_snapshot

__all__ = [
    "Branch", "Claim", "Evidence", "EvidenceKind", "EvidenceProfile",
    "ExactComputation", "ExternalImport", "FormalCorrespondenceCertificate",
    "FormalVerification", "InformalReview", "IntentCertificate", "Interpretation",
    "Lifecycle", "NumericalEvidence", "Problem", "Relation", "RelationType",
    "TruthStatus", "Verdict",
    "ACTIONS", "Event", "EventLog", "EventLogError",
    "EpistemicGraph", "GraphError", "EvidenceRouter",
    "invalidate_evidence", "refute_claim", "strongly_connected_components",
    "TruthSnapshot", "TruthSnapshotError", "issue_truth_snapshot",
]
