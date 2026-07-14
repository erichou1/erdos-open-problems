"""Deterministic proof-verification gate.

No model response can mark a problem solved directly. Only ``evaluate_gate``
can promote a candidate after multiple independent structured reviews.
"""

from dataclasses import asdict, dataclass, field, replace
from collections.abc import Iterator, Mapping, Sequence
from types import MappingProxyType
from typing import Iterable
import hashlib
import hmac
import json
import os
import re


@dataclass(frozen=True)
class Review:
    reviewer_id: str
    reviewer_role: str
    independent_context: bool
    verdict: str
    claims_checked: int
    claims_total: int
    checked_claim_ids: tuple[str, ...] = field(default_factory=tuple)
    open_gaps: tuple[str, ...] = field(default_factory=tuple)
    unchecked_imports: tuple[str, ...] = field(default_factory=tuple)
    material_errors: tuple[str, ...] = field(default_factory=tuple)
    statement_sha256: str = ""
    completeness_score: int = 0
    proof_confidence: int = 0
    adversarial_survival_score: int = 0
    adjudicated_outcome: str = ""
    context_id: str = ""
    candidate_sha256: str = ""
    authority_id: str = ""
    model_provider: str = ""
    model_name: str = ""
    model_version: str = ""
    model_lineage: str = ""
    schema_version: int = 2
    attestor_key_id: str = ""
    attestation: str = ""
    problem_number: int = 0
    run_contract_id: str = ""
    execution_id: str = ""
    run_context_id: str = ""


@dataclass(frozen=True)
class GateDecision:
    status: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class CandidateContract:
    outcome: str
    completeness_score: int
    proof_confidence: int
    adversarial_survival_score: int
    open_gaps: tuple[str, ...]
    unchecked_imports: tuple[str, ...]
    claims_checked: int
    claims_total: int
    claim_ids: tuple[str, ...]
    fields_complete: bool

    @property
    def valid_for_promotion(self) -> bool:
        scores = (
            self.completeness_score,
            self.proof_confidence,
            self.adversarial_survival_score,
        )
        return (
            self.outcome in {"candidate_proved", "candidate_disproved"}
            and all(0 <= score <= 100 for score in scores)
            and not self.open_gaps
            and not self.unchecked_imports
            and self.claims_total > 0
            and self.claims_checked == self.claims_total
            and self.claims_total == len(self.claim_ids)
            and len(self.claim_ids) == len(set(self.claim_ids))
            and self.fields_complete
        )


@dataclass(frozen=True)
class VerificationEvidence:
    kind: str
    verifier: str
    outcome: str
    statement_sha256: str
    candidate_sha256: str
    artifact_sha256: str
    passed: bool
    verification_method: str = ""
    validator_id: str = ""
    certificate_sha256: str = ""
    scope_sha256: str = ""
    coverage: str = ""
    statement_fidelity: str = ""
    schema_version: int = 2
    attestor_key_id: str = ""
    attestation: str = ""
    problem_number: int = 0
    run_contract_id: str = ""
    execution_id: str = ""
    run_context_id: str = ""


@dataclass(frozen=True)
class VerificationBinding:
    """Canonical production identity every review/evidence receipt must bind."""

    problem_number: int
    statement_sha256: str
    candidate_sha256: str
    run_contract_id: str
    execution_id: str
    run_context_id: str


class MaterializedVerificationEvidence(Sequence[VerificationEvidence]):
    """Evidence whose artifacts were opened, bounded, and hash-checked.

    This capability is issued only by the confined evidence loader.  A signed
    metadata receipt by itself cannot prove that the referenced certificate was
    present or that its bytes matched the receipt.
    """

    __slots__ = ("_items", "_artifact_payloads")

    def __init__(
        self,
        items: Iterable[VerificationEvidence],
        artifact_payloads: Mapping[str, bytes],
    ) -> None:
        self._items = tuple(items)
        copied: dict[str, bytes] = {}
        for digest, payload in artifact_payloads.items():
            if not isinstance(digest, str) or not isinstance(payload, bytes):
                raise TypeError("materialized evidence requires digest-to-bytes entries")
            copied[digest] = bytes(payload)
        self._artifact_payloads = MappingProxyType(copied)

    def __iter__(self) -> Iterator[VerificationEvidence]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    @property
    def artifact_payloads(self) -> Mapping[str, bytes]:
        return self._artifact_payloads


REQUIRED_ROLES = frozenset({
    "statement_integrity", "structural_dependency", "logic",
    "counterexample", "theorem_hypotheses", "mechanical_evidence",
    "global_synthesis", "adjudicator",
})
# Natural-language/expert consensus is a release blocker and review record, not
# mathematical truth evidence.  Only typed, independently replayed mechanical
# evidence can satisfy this legacy gate.
TRUSTED_EVIDENCE_KINDS = frozenset({"formal_proof", "exact_computation"})
TRUSTED_EXACT_VALIDATORS = frozenset({"egmra.compute.exact-replay/v1"})
TRUSTED_FORMAL_VALIDATORS = frozenset({"egmra.lean.hardened-kernel/v1"})
LEGACY_REVIEW_KEY_ENV = "EGMRA_LEGACY_REVIEW_KEY"
LEGACY_EVIDENCE_KEY_ENV = "EGMRA_LEGACY_EVIDENCE_KEY"
_MIN_ATTESTATION_KEY_BYTES = 32
RESULT_FIELD_NAMES = (
    "OUTCOME", "COMPLETENESS_SCORE", "PROOF_CONFIDENCE",
    "ADVERSARIAL_SURVIVAL_SCORE", "OPEN_GAPS", "UNCHECKED_IMPORTS",
    "CLAIMS_CHECKED", "CLAIMS_TOTAL", "CLAIM_IDS",
)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    )


def _attestation_key(name: str, env: dict[str, str] | None) -> bytes:
    source = env if env is not None else dict(os.environ)
    raw = source.get(name, "").strip().encode("utf-8")
    if len(raw) < _MIN_ATTESTATION_KEY_BYTES:
        raise ValueError(f"{name} must contain at least 32 bytes")
    return raw


def _key_id(key: bytes) -> str:
    return hashlib.sha256(key).hexdigest()


def _review_record(review: Review) -> dict:
    record = asdict(review)
    record.pop("attestation", None)
    return record


def _evidence_record(evidence: VerificationEvidence) -> dict:
    record = asdict(evidence)
    record.pop("attestation", None)
    return record


def _is_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", value))


def sign_review(review: Review, *, env: dict[str, str] | None = None) -> Review:
    """Authenticate a review after an independent runner gateway identifies it.

    A conversation URL or caller label is not model/authority provenance.  The
    signing boundary therefore requires immutable runner identity, authority,
    statement and candidate bindings before it will issue an attestation.
    """
    required = (
        review.reviewer_id, review.reviewer_role, review.context_id,
        review.authority_id, review.model_provider, review.model_name,
        review.model_version, review.model_lineage,
    )
    if review.schema_version != 2 or any(not value.strip() for value in required):
        raise ValueError("review identity and provenance fields must be complete")
    if not _is_sha256(review.statement_sha256) \
            or not _is_sha256(review.candidate_sha256):
        raise ValueError("review must bind exact statement and candidate hashes")
    if type(review.problem_number) is not int or review.problem_number <= 0 \
            or not _is_sha256(review.run_contract_id) \
            or not review.execution_id.strip() \
            or not _is_sha256(review.run_context_id):
        raise ValueError("review must bind canonical problem and run identity")
    key = _attestation_key(LEGACY_REVIEW_KEY_ENV, env)
    unsigned = replace(
        review, attestor_key_id=_key_id(key), attestation="",
    )
    signature = hmac.new(
        key, _canonical_json(_review_record(unsigned)).encode("utf-8"), hashlib.sha256,
    ).hexdigest()
    return replace(unsigned, attestation=signature)


def verify_review_attestation(
    review: Review, *, env: dict[str, str] | None = None,
) -> bool:
    try:
        key = _attestation_key(LEGACY_REVIEW_KEY_ENV, env)
    except ValueError:
        return False
    if review.schema_version != 2 \
            or review.attestor_key_id != _key_id(key) \
            or not _is_sha256(review.attestation):
        return False
    expected = hmac.new(
        key, _canonical_json(_review_record(review)).encode("utf-8"), hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, review.attestation)


def _evidence_semantic_errors(evidence: VerificationEvidence) -> tuple[str, ...]:
    errors: list[str] = []
    if evidence.schema_version != 2:
        errors.append("unsupported evidence schema")
    if evidence.kind not in TRUSTED_EVIDENCE_KINDS:
        errors.append("evidence kind cannot establish mathematical truth")
    if evidence.outcome not in {"candidate_proved", "candidate_disproved"}:
        errors.append("invalid evidence outcome")
    if not evidence.verifier.strip():
        errors.append("missing verifier identity")
    for label, digest in (
        ("statement", evidence.statement_sha256),
        ("candidate", evidence.candidate_sha256),
        ("artifact", evidence.artifact_sha256),
        ("certificate", evidence.certificate_sha256),
        ("scope", evidence.scope_sha256),
    ):
        if not _is_sha256(digest):
            errors.append(f"invalid {label} hash")
    if evidence.scope_sha256 != evidence.statement_sha256:
        errors.append("evidence scope is not the locked statement")
    if evidence.certificate_sha256 != evidence.artifact_sha256:
        errors.append("validator certificate hash is not the loaded artifact hash")
    if type(evidence.problem_number) is not int or evidence.problem_number <= 0:
        errors.append("evidence lacks canonical problem identity")
    if not _is_sha256(evidence.run_contract_id) \
            or not evidence.execution_id.strip() \
            or not _is_sha256(evidence.run_context_id):
        errors.append("evidence lacks canonical run identity")
    if evidence.coverage != "complete":
        errors.append("evidence coverage is not complete")
    if type(evidence.passed) is not bool or not evidence.passed:
        errors.append("evidence did not pass its validator")
    if evidence.kind == "exact_computation":
        if evidence.verification_method != "independent_exact_replay":
            errors.append("exact computation lacks independent exact replay")
        if evidence.validator_id not in TRUSTED_EXACT_VALIDATORS:
            errors.append("exact computation used an untrusted validator")
        if evidence.statement_fidelity != "exact_scope_bound":
            errors.append("exact computation is not bound to the claimed scope")
    elif evidence.kind == "formal_proof":
        if evidence.verification_method != "hardened_independent_kernel_replay":
            errors.append("formal proof lacks hardened independent kernel replay")
        if evidence.validator_id not in TRUSTED_FORMAL_VALIDATORS:
            errors.append("formal proof used an untrusted validator")
        if evidence.statement_fidelity != "approved_i2_f2":
            errors.append("formal proof lacks approved intent/correspondence fidelity")
    return tuple(errors)


def sign_verification_evidence(
    evidence: VerificationEvidence, *, env: dict[str, str] | None = None,
) -> VerificationEvidence:
    """Issue a capability receipt only for closed, promotable evidence records."""
    errors = _evidence_semantic_errors(evidence)
    if errors:
        raise ValueError("invalid verification evidence: " + "; ".join(errors))
    key = _attestation_key(LEGACY_EVIDENCE_KEY_ENV, env)
    unsigned = replace(
        evidence, attestor_key_id=_key_id(key), attestation="",
    )
    signature = hmac.new(
        key, _canonical_json(_evidence_record(unsigned)).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return replace(unsigned, attestation=signature)


def verify_verification_evidence(
    evidence: VerificationEvidence, *, env: dict[str, str] | None = None,
) -> bool:
    if _evidence_semantic_errors(evidence):
        return False
    try:
        key = _attestation_key(LEGACY_EVIDENCE_KEY_ENV, env)
    except ValueError:
        return False
    if evidence.attestor_key_id != _key_id(key) \
            or not _is_sha256(evidence.attestation):
        return False
    expected = hmac.new(
        key, _canonical_json(_evidence_record(evidence)).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, evidence.attestation)


def evaluate_gate(
    candidate_outcome: str,
    reviews: Iterable[Review],
    *,
    min_completeness: int = 98,
    min_confidence: int = 95,
    min_adversarial_survival: int = 95,
    expected_statement_sha256: str = "",
    candidate_contract: CandidateContract | None = None,
    verification_evidence: Iterable[VerificationEvidence] = (),
    expected_candidate_sha256: str = "",
    attestation_env: dict[str, str] | None = None,
    expected_problem_number: int | None = None,
    expected_run_contract_id: str = "",
    expected_execution_id: str = "",
    expected_run_context_id: str = "",
) -> GateDecision:
    """Promote only unanimous, complete, independent, role-diverse reviews."""
    reviews = tuple(reviews)
    reasons: list[str] = []
    outcome = candidate_outcome.lower().strip()
    materialized_artifact_sha256s = frozenset(
        digest
        for digest, payload in (
            verification_evidence.artifact_payloads.items()
            if type(verification_evidence) is MaterializedVerificationEvidence
            else ()
        )
        if _is_sha256(digest)
        and hashlib.sha256(payload).hexdigest() == digest
    )
    verification_evidence = tuple(verification_evidence)
    if not _is_sha256(expected_statement_sha256) \
            or not _is_sha256(expected_candidate_sha256):
        reasons.append("canonical statement and candidate anchors are required")
    if candidate_contract is None:
        reasons.append("candidate contract is required for promotion")
    if type(expected_problem_number) is not int or expected_problem_number <= 0:
        reasons.append("canonical problem identity is required")
    if not _is_sha256(expected_run_contract_id) \
            or not expected_execution_id.strip() \
            or not _is_sha256(expected_run_context_id):
        reasons.append("canonical run identity is required")
    if outcome not in {"candidate_proved", "candidate_disproved"}:
        reasons.append("candidate has no proof or disproof claim")
    if candidate_contract is not None:
        if candidate_contract.outcome != outcome or not candidate_contract.valid_for_promotion:
            reasons.append("candidate result contract is incomplete or internally inconsistent")
    authenticated_evidence = [
        evidence for evidence in verification_evidence
        if verify_verification_evidence(evidence, env=attestation_env)
        and evidence.outcome == outcome
    ]
    valid_evidence = [
        evidence for evidence in authenticated_evidence
        if evidence.outcome == outcome
        and (not expected_candidate_sha256
             or evidence.candidate_sha256 == expected_candidate_sha256)
        and (not expected_statement_sha256
             or evidence.statement_sha256 == expected_statement_sha256)
        and evidence.problem_number == expected_problem_number
        and evidence.run_contract_id == expected_run_contract_id
        and evidence.execution_id == expected_execution_id
        and evidence.run_context_id == expected_run_context_id
        and evidence.artifact_sha256 in materialized_artifact_sha256s
    ]
    if not valid_evidence:
        reasons.append("no trusted external or mechanical verification evidence")
    for evidence in verification_evidence:
        if not verify_verification_evidence(evidence, env=attestation_env):
            reasons.append(
                f"verification evidence from {evidence.verifier or '<unknown>'} "
                "has invalid semantics or attestation"
            )
    authenticated_reviews = tuple(
        review for review in reviews
        if verify_review_attestation(review, env=attestation_env)
    )
    candidate_bindings = {
        *(evidence.candidate_sha256 for evidence in authenticated_evidence),
        *(review.candidate_sha256 for review in authenticated_reviews),
    }
    statement_bindings = {
        *(evidence.statement_sha256 for evidence in authenticated_evidence),
        *(review.statement_sha256 for review in authenticated_reviews),
    }
    if len(candidate_bindings) > 1:
        reasons.append("authenticated candidate bindings disagree")
    if len(statement_bindings) > 1:
        reasons.append("authenticated statement bindings disagree")

    # A hardened independent-kernel receipt with approved intent/formal
    # correspondence is truth evidence. A model referee cannot overrule that
    # truth status (§11.4), although the retired legacy path still cannot issue
    # a release certificate.
    if any(item.kind == "formal_proof" for item in valid_evidence) and not reasons:
        return GateDecision(
            "awaiting_authenticated_release",
            ("hardened formal evidence supports truth; release requires the "
             "event-derived EGMRA ReleaseCertificate path",),
        )

    roles = {r.reviewer_role for r in reviews if r.independent_context}
    missing_roles = sorted(REQUIRED_ROLES - roles)
    if missing_roles:
        reasons.append("missing independent review roles: " + ", ".join(missing_roles))

    reviewer_ids = [r.reviewer_id for r in reviews]
    if len(reviewer_ids) != len(set(reviewer_ids)):
        reasons.append("reviewer ids are not unique")
    context_ids = [r.context_id for r in reviews]
    if any(not context_id for context_id in context_ids):
        reasons.append("one or more reviews lack context provenance")
    if len(context_ids) != len(set(context_ids)):
        reasons.append("review contexts are not unique")
    authority_ids = [r.authority_id for r in reviews]
    if any(not authority_id for authority_id in authority_ids):
        reasons.append("one or more reviews lack authenticated authority provenance")
    if len(authority_ids) != len(set(authority_ids)):
        reasons.append("review authorities are not independent")
    lineages = [r.model_lineage for r in reviews]
    if any(not lineage for lineage in lineages):
        reasons.append("one or more reviews lack authenticated model lineage")
    adjudicator_lineages = {
        r.model_lineage for r in reviews if r.reviewer_role == "adjudicator"
    }
    other_lineages = {
        r.model_lineage for r in reviews if r.reviewer_role != "adjudicator"
    }
    if not adjudicator_lineages or adjudicator_lineages & other_lineages:
        reasons.append("adjudicator model lineage is not independent")

    for review in reviews:
        prefix = f"review {review.reviewer_id}"
        if not verify_review_attestation(review, env=attestation_env):
            reasons.append(f"{prefix} has invalid or missing attestation")
        if not review.independent_context:
            reasons.append(f"{prefix} is not independent")
        if review.verdict.lower() != "pass":
            reasons.append(f"{prefix} did not pass")
        if review.claims_total <= 0 or review.claims_checked != review.claims_total:
            reasons.append(f"{prefix} did not check every claim")
        if (candidate_contract is not None
                and review.claims_total != candidate_contract.claims_total):
            reasons.append(f"{prefix} used a claim count inconsistent with the candidate")
        if (candidate_contract is not None
                and set(review.checked_claim_ids) != set(candidate_contract.claim_ids)):
            reasons.append(f"{prefix} did not attest to the complete claim ledger")
        if review.open_gaps:
            reasons.append(f"{prefix} reports open gaps")
        if review.unchecked_imports:
            reasons.append(f"{prefix} reports unchecked imports")
        if review.material_errors:
            reasons.append(f"{prefix} reports material errors")
        if (expected_statement_sha256
                and review.statement_sha256 != expected_statement_sha256):
            reasons.append(f"{prefix} did not attest to the immutable statement")
        if (expected_candidate_sha256
                and review.candidate_sha256 != expected_candidate_sha256):
            reasons.append(f"{prefix} did not attest to the immutable candidate")
        if review.problem_number != expected_problem_number:
            reasons.append(f"{prefix} did not attest to the canonical problem")
        if review.run_contract_id != expected_run_contract_id \
                or review.execution_id != expected_execution_id \
                or review.run_context_id != expected_run_context_id:
            reasons.append(f"{prefix} did not attest to the canonical run")
        if review.completeness_score < min_completeness:
            reasons.append(f"{prefix} completeness below {min_completeness}")
        if review.proof_confidence < min_confidence:
            reasons.append(f"{prefix} confidence below {min_confidence}")
        if review.adversarial_survival_score < min_adversarial_survival:
            reasons.append(f"{prefix} adversarial survival below {min_adversarial_survival}")
        if not all(0 <= score <= 100 for score in (
            review.completeness_score,
            review.proof_confidence,
            review.adversarial_survival_score,
        )):
            reasons.append(f"{prefix} reports a score outside 0..100")
        if review.reviewer_role == "adjudicator":
            expected = "proved" if outcome == "candidate_proved" else "disproved"
            if review.adjudicated_outcome.lower() != expected:
                reasons.append(f"{prefix} outcome does not match the candidate")

    if reasons:
        return GateDecision("candidate_rejected", tuple(reasons))
    # This pre-EGMRA HMAC gate cannot safely be a release authority: its signing
    # helpers and symmetric keys live in the same Python trust domain. Keep its
    # verified metadata as quarantined input and require the event-derived,
    # independently authorized ReleaseCertificate chain for any release.
    return GateDecision(
        "awaiting_authenticated_release",
        ("legacy verification checks passed, but legacy truth promotion is "
         "retired; use the EGMRA ReleaseCertificate path",),
    )


def _result_fields(response: str) -> dict[str, list[str]]:
    """Extract labeled fields from one bounded block, independent of line layout."""
    blocks = re.findall(r"<result>\s*(.*?)\s*</result>", response,
                        re.IGNORECASE | re.DOTALL)
    if len(blocks) != 1:
        return {}
    label = "|".join(RESULT_FIELD_NAMES)
    matches = list(re.finditer(
        rf"(?<![A-Z0-9_])({label})\s*:\s*",
        blocks[0], re.IGNORECASE,
    ))
    fields: dict[str, list[str]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(blocks[0])
        value = blocks[0][match.end():end].strip().strip(";").strip()
        fields.setdefault(match.group(1).upper(), []).append(value)
    return fields


def candidate_status(response: str) -> str:
    """Extract the outcome from exactly one bounded result block."""
    fields = _result_fields(response)
    outcomes = fields.get("OUTCOME", [])
    if len(outcomes) != 1:
        return "candidate_unclassified"
    match = re.fullmatch(
        r"CANDIDATE_PROVED|CANDIDATE_DISPROVED|RESOURCE_EXHAUSTED",
        outcomes[0], re.IGNORECASE,
    )
    if not match:
        return "candidate_unclassified"
    return match.group(0).lower()


def candidate_contract(response: str) -> CandidateContract:
    """Parse the complete candidate result block; missing fields fail closed."""
    fields = _result_fields(response)
    present: set[str] = set()

    def integer(name: str) -> int:
        values = fields.get(name, [])
        # Bound before int() so hostile model output cannot trip Python's
        # interpreter-wide maximum-digit exception or allocate enormous ints.
        if (
            len(values) == 1
            and len(values[0]) <= 9
            and re.fullmatch(r"\d+", values[0])
        ):
            present.add(name)
            return int(values[0])
        return -1

    def items(name: str) -> tuple[str, ...]:
        values = fields.get(name, [])
        if len(values) != 1 or not values[0]:
            return ()
        present.add(name)
        if values[0].strip().upper() == "NONE":
            return ()
        return tuple(item.strip() for item in values[0].split(";") if item.strip())

    contract = CandidateContract(
        outcome=candidate_status(response),
        completeness_score=integer("COMPLETENESS_SCORE"),
        proof_confidence=integer("PROOF_CONFIDENCE"),
        adversarial_survival_score=integer("ADVERSARIAL_SURVIVAL_SCORE"),
        open_gaps=items("OPEN_GAPS"),
        unchecked_imports=items("UNCHECKED_IMPORTS"),
        claims_checked=integer("CLAIMS_CHECKED"),
        claims_total=integer("CLAIMS_TOTAL"),
        claim_ids=items("CLAIM_IDS"),
        fields_complete=False,
    )
    required = {
        "COMPLETENESS_SCORE", "PROOF_CONFIDENCE", "ADVERSARIAL_SURVIVAL_SCORE",
        "OPEN_GAPS", "UNCHECKED_IMPORTS", "CLAIMS_CHECKED", "CLAIMS_TOTAL",
        "CLAIM_IDS",
    }
    return CandidateContract(
        **{**contract.__dict__, "fields_complete": required <= present}
    )
