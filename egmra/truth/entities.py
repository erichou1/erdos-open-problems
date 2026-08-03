"""Core epistemic-graph entities (spec §10.1).

Every entity is a dataclass with a canonical ``to_dict`` for content-addressing.
Evidence is deliberately *multidimensional*: an exact finite computation, an
audited paper import, a kernel proof, and a human review are separate axes that
never collapse into one scalar. Truth status, lifecycle, formal status,
informal-review status, external-import status, and the target-fidelity
certificates all travel independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── controlled vocabularies ────────────────────────────────────────────────────

class StrEnum(str, Enum):
    """A string enum whose members serialize as their value."""

    def __str__(self) -> str:  # pragma: no cover - trivial
        return str(self.value)


class Lifecycle(StrEnum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    RETRACTED = "RETRACTED"


class TruthStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    CONFLICTED = "CONFLICTED"


class NumericalEvidence(StrEnum):
    NONE = "NONE"
    REPRODUCIBLE = "REPRODUCIBLE"


class ExactComputation(StrEnum):
    NONE = "NONE"
    SCOPED_EXACT = "SCOPED_EXACT"
    CERTIFICATE_CHECKED = "CERTIFICATE_CHECKED"


class InformalReview(StrEnum):
    NONE = "NONE"
    SINGLE = "SINGLE"
    DOUBLE_INDEPENDENT = "DOUBLE_INDEPENDENT"


class FormalVerification(StrEnum):
    NONE = "NONE"
    KERNEL_CHECKED = "KERNEL_CHECKED"
    INDEPENDENT_CHECKER = "INDEPENDENT_CHECKER"


class ExternalImport(StrEnum):
    NONE = "NONE"
    AUDITED_SOURCE = "AUDITED_SOURCE"
    INDEPENDENTLY_CORROBORATED = "INDEPENDENTLY_CORROBORATED"


class RelationType(StrEnum):
    DEPENDS_ON = "DEPENDS_ON"
    IMPLIES = "IMPLIES"
    EQUIVALENT_TO = "EQUIVALENT_TO"
    REFUTES = "REFUTES"
    SPECIAL_CASE_OF = "SPECIAL_CASE_OF"
    GENERALIZES = "GENERALIZES"
    FORMALIZES = "FORMALIZES"
    IMPORTED_FROM = "IMPORTED_FROM"
    TESTED_BY = "TESTED_BY"
    SUPERSEDES = "SUPERSEDES"


class EvidenceKind(StrEnum):
    SOURCE_IMPORT = "source_import"
    NUMERICAL = "numerical"
    EXACT_COMPUTATION = "exact_computation"
    COUNTEREXAMPLE = "counterexample"
    INFORMAL_REVIEW = "informal_review"
    LEAN_PROOF = "lean_proof"
    ATP_PROOF = "atp_proof"
    SAT_CERTIFICATE = "sat_certificate"
    EXPERT_REVIEW = "expert_review"


class Verdict(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


# ── evidence profile ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EvidenceProfile:
    """The multidimensional evidence attached to a claim (spec §10.1)."""

    numerical: NumericalEvidence = NumericalEvidence.NONE
    exact_computation: ExactComputation = ExactComputation.NONE
    informal_review: InformalReview = InformalReview.NONE
    formal_verification: FormalVerification = FormalVerification.NONE
    external_import: ExternalImport = ExternalImport.NONE
    intent_certificate_id: str | None = None
    formal_correspondence_certificate_id: str | None = None

    def is_empty(self) -> bool:
        return (
            self.numerical == NumericalEvidence.NONE
            and self.exact_computation == ExactComputation.NONE
            and self.informal_review == InformalReview.NONE
            and self.formal_verification == FormalVerification.NONE
            and self.external_import == ExternalImport.NONE
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "numerical": str(self.numerical),
            "exact_computation": str(self.exact_computation),
            "informal_review": str(self.informal_review),
            "formal_verification": str(self.formal_verification),
            "external_import": str(self.external_import),
            "intent_certificate_id": self.intent_certificate_id,
            "formal_correspondence_certificate_id": self.formal_correspondence_certificate_id,
        }


# ── entities ────────────────────────────────────────────────────────────────────

@dataclass
class Interpretation:
    interpretation_id: str
    parent_problem_id: str
    normalized_statement: str
    binders: list[dict] = field(default_factory=list)
    hypotheses: list[str] = field(default_factory=list)
    conclusion: str = ""
    relation_to_parent: str = "exact"  # exact|plausible|stronger|weaker|special_case
    ambiguities_resolved: list[str] = field(default_factory=list)
    ambiguities_open: list[str] = field(default_factory=list)
    formal_candidates: list[str] = field(default_factory=list)
    intent_verdict: str = "pending"  # pending|approved|rejected
    status_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class Problem:
    problem_id: str
    source_versions: list[dict] = field(default_factory=list)
    original_bytes_hash: str = ""
    statement_ir_hash: str = ""
    status_claims: list[dict] = field(default_factory=list)
    interpretations: list[str] = field(default_factory=list)
    active_interpretation: str | None = None
    status_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class Claim:
    claim_id: str
    interpretation_id: str
    canonical_formula: str
    canonical_hash: str = ""
    informal_text: str = ""
    quantifiers: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    scope: str = "general"  # general|parameter_range|finite_domain|conditional
    lifecycle_status: Lifecycle = Lifecycle.ACTIVE
    truth_status: TruthStatus = TruthStatus.UNKNOWN
    evidence_profile: EvidenceProfile = field(default_factory=EvidenceProfile)
    evidence_ids: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    contradicts: list[str] = field(default_factory=list)
    equivalent_to: list[str] = field(default_factory=list)
    generalizes: list[str] = field(default_factory=list)
    special_cases: list[str] = field(default_factory=list)
    formal_declarations: list[str] = field(default_factory=list)
    source_records: list[str] = field(default_factory=list)
    branch_ids: list[str] = field(default_factory=list)
    verification_attempts: list[dict] = field(default_factory=list)
    semantic_risk: float = 0.0
    centrality: float = 0.0
    compute_spend: dict = field(default_factory=dict)
    status_version: int = 1
    created_by: str = ""
    created_at: str = ""
    supersedes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out = dict(self.__dict__)
        out["lifecycle_status"] = str(self.lifecycle_status)
        out["truth_status"] = str(self.truth_status)
        out["evidence_profile"] = self.evidence_profile.to_dict()
        return out


@dataclass
class Branch:
    branch_id: str
    goal_claim_ids: list[str] = field(default_factory=list)
    interpretation_id: str = ""
    mechanism_fingerprint: dict = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)
    dependency_cone_hash: str = ""
    parent_branches: list[str] = field(default_factory=list)
    children: list[str] = field(default_factory=list)
    status: str = "proposed"  # proposed|active|paused|killed|closed
    value_posterior: dict = field(default_factory=dict)
    cost_posterior: dict = field(default_factory=dict)
    budget_spent: dict = field(default_factory=dict)
    verified_debt: dict = field(default_factory=dict)
    failure_certificates: list[str] = field(default_factory=list)
    pause_reason: str | None = None
    reopen_conditions: list[str] = field(default_factory=list)
    lease: dict = field(default_factory=dict)
    status_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class Evidence:
    evidence_id: str
    claim_ids: list[str]
    kind: EvidenceKind
    assertion_scope: str = ""
    claim_bindings: dict[str, str] = field(default_factory=dict)
    artifact_hashes: list[str] = field(default_factory=list)
    generator_identity: dict = field(default_factory=dict)
    verifier_identities: list[dict] = field(default_factory=list)
    diversity_profile: dict = field(default_factory=dict)
    environment_hash: str = ""
    replay_command: str = ""
    replay_result: str = "pending"  # pass|fail|not_applicable|pending
    intent_certificate_id: str | None = None
    formal_correspondence_certificate_id: str | None = None
    trust_assumptions: list[str] = field(default_factory=list)
    attestation_key_id: str = ""
    attestation_signature: str = ""
    valid: bool = True
    invalidation_reason: str = ""
    created_at: str = ""
    status_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        out = dict(self.__dict__)
        out["kind"] = str(self.kind)
        return out

    def attestation_record(self) -> dict[str, Any]:
        """Immutable evidence fields authenticated by a validator/service key."""

        record = self.to_dict()
        record.pop("attestation_signature", None)
        # Revocation is a later truth-plane event; it must not invalidate the
        # signature over the evidence as originally admitted.
        record.pop("valid", None)
        record.pop("invalidation_reason", None)
        return record


@dataclass
class Relation:
    """A typed graph relation, itself a first-class mathematical claim (§10.1)."""

    edge_id: str
    relation_type: RelationType
    source_id: str
    target_id: str
    formula: str = ""
    scope: str = "general"
    evidence_profile: EvidenceProfile = field(default_factory=EvidenceProfile)
    provenance: dict = field(default_factory=dict)
    lifecycle_status: Lifecycle = Lifecycle.ACTIVE
    status_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        out = dict(self.__dict__)
        out["relation_type"] = str(self.relation_type)
        out["lifecycle_status"] = str(self.lifecycle_status)
        out["evidence_profile"] = self.evidence_profile.to_dict()
        return out


@dataclass
class IntentCertificate:
    certificate_id: str
    source_bytes_hash: str
    interpretation_hash: str
    informal_claim_hash: str
    methods: list[str] = field(default_factory=list)
    reviewer_ids: list[str] = field(default_factory=list)
    reviewer_independence_and_conflicts: list[dict] = field(default_factory=list)
    verdict: Verdict = Verdict.UNRESOLVED
    version: str = "1"
    created_at: str = ""
    reviewer_key_id: str = ""
    review_signature: str = ""

    def to_dict(self) -> dict[str, Any]:
        out = dict(self.__dict__)
        out["verdict"] = str(self.verdict)
        return out


@dataclass
class FormalCorrespondenceCertificate:
    certificate_id: str
    intent_certificate_id: str
    informal_claim_hash: str
    lean_declaration_name: str
    elaborated_type_hash: str
    notation_and_definition_map_hash: str = ""
    methods: list[str] = field(default_factory=list)
    reviewer_ids: list[str] = field(default_factory=list)
    reviewer_independence_and_conflicts: list[dict] = field(default_factory=list)
    verdict: Verdict = Verdict.UNRESOLVED
    version: str = "1"
    created_at: str = ""
    reviewer_key_id: str = ""
    review_signature: str = ""

    def to_dict(self) -> dict[str, Any]:
        out = dict(self.__dict__)
        out["verdict"] = str(self.verdict)
        return out
