"""Deterministic proof-verification gate.

No model response can mark a problem solved directly. Only ``evaluate_gate``
can promote a candidate after multiple independent structured reviews.
"""

from dataclasses import dataclass, field
from typing import Iterable
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


REQUIRED_ROLES = frozenset({
    "statement_integrity", "structural_dependency", "logic",
    "counterexample", "theorem_hypotheses", "mechanical_evidence",
    "global_synthesis", "adjudicator",
})
TRUSTED_EVIDENCE_KINDS = frozenset({
    "formal_proof", "exact_computation", "expert_review"
})
RESULT_FIELD_NAMES = (
    "OUTCOME", "COMPLETENESS_SCORE", "PROOF_CONFIDENCE",
    "ADVERSARIAL_SURVIVAL_SCORE", "OPEN_GAPS", "UNCHECKED_IMPORTS",
    "CLAIMS_CHECKED", "CLAIMS_TOTAL", "CLAIM_IDS",
)


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
) -> GateDecision:
    """Promote only unanimous, complete, independent, role-diverse reviews."""
    reviews = tuple(reviews)
    reasons: list[str] = []
    outcome = candidate_outcome.lower().strip()
    verification_evidence = tuple(verification_evidence)
    if outcome not in {"candidate_proved", "candidate_disproved"}:
        reasons.append("candidate has no proof or disproof claim")
    if candidate_contract is not None:
        if candidate_contract.outcome != outcome or not candidate_contract.valid_for_promotion:
            reasons.append("candidate result contract is incomplete or internally inconsistent")
    valid_evidence = [
        evidence for evidence in verification_evidence
        if evidence.passed
        and evidence.kind in TRUSTED_EVIDENCE_KINDS
        and evidence.outcome == outcome
        and bool(evidence.verifier.strip())
        and bool(re.fullmatch(r"[0-9a-f]{64}", evidence.artifact_sha256))
        and (not expected_candidate_sha256
             or evidence.candidate_sha256 == expected_candidate_sha256)
        and (not expected_statement_sha256
             or evidence.statement_sha256 == expected_statement_sha256)
    ]
    if not valid_evidence:
        reasons.append("no trusted external or mechanical verification evidence")

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

    for review in reviews:
        prefix = f"review {review.reviewer_id}"
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
    promoted = "verified_proved" if outcome == "candidate_proved" else "verified_disproved"
    return GateDecision(promoted, ("all mandatory independent reviews passed",))


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
        if len(values) == 1 and re.fullmatch(r"\d+", values[0]):
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
