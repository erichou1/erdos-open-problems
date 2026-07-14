"""Evidence-kind validators (spec §10.2, §16 P0.2).

A general ``passed=true`` field is invalid. Each evidence kind has a *closed,
kind-specific* validator that checks its own obligations and contributes to
exactly the evidence-profile dimension it can support. A model referee can route
work and block release, but it cannot manufacture a truth tier.
"""

from __future__ import annotations

import hmac
import os
import re
from dataclasses import dataclass, field
from typing import Callable, TypeVar

from egmra.truth.entities import (
    Evidence,
    EvidenceKind,
    EvidenceProfile,
    ExactComputation,
    ExternalImport,
    FormalVerification,
    InformalReview,
    NumericalEvidence,
)
from egmra.provenance.hashing import canonical_json


_MIN_EVIDENCE_KEY_BYTES = 32


class EvidenceAttestationError(ValueError):
    """Raised when evidence attestation configuration is unsafe."""


def _evidence_key(env: dict[str, str] | None = None) -> bytes:
    env = env if env is not None else dict(os.environ)
    raw = env.get("EGMRA_EVIDENCE_KEY", "").strip()
    if not raw:
        raise EvidenceAttestationError("EGMRA_EVIDENCE_KEY is required")
    key = raw.encode("utf-8")
    if len(key) < _MIN_EVIDENCE_KEY_BYTES:
        raise EvidenceAttestationError(
            f"EGMRA_EVIDENCE_KEY must contain at least {_MIN_EVIDENCE_KEY_BYTES} bytes"
        )
    return key


def attest_evidence(
    evidence: Evidence, *, env: dict[str, str] | None = None, key_id: str = "truth-validator-v1"
) -> Evidence:
    """Authenticate immutable evidence fields before truth-plane admission."""

    if not key_id.strip():
        raise EvidenceAttestationError("evidence attestation key_id is required")
    evidence.attestation_key_id = key_id
    key = _evidence_key(env)
    evidence.attestation_signature = hmac.new(
        key,
        canonical_json(evidence.attestation_record()).encode("utf-8"),
        "sha256",
    ).hexdigest()
    return evidence


def verify_evidence_attestation(
    evidence: Evidence,
    *,
    env: dict[str, str] | None = None,
    expected_claim_hashes: dict[str, str] | None = None,
) -> bool:
    if not evidence.attestation_signature or not evidence.attestation_key_id.strip():
        return False
    try:
        key = _evidence_key(env)
    except EvidenceAttestationError:
        return False
    expected = hmac.new(
        key,
        canonical_json(evidence.attestation_record()).encode("utf-8"),
        "sha256",
    ).hexdigest()
    if not hmac.compare_digest(expected, evidence.attestation_signature):
        return False
    if expected_claim_hashes is not None:
        if set(evidence.claim_ids) != set(expected_claim_hashes):
            return False
        if evidence.claim_bindings != expected_claim_hashes:
            return False
    return True


@dataclass(frozen=True)
class Assessment:
    """One evidence item's contribution to a claim's profile."""

    admitted: bool
    obligations_discharged: tuple[str, ...] = ()
    obligations_missing: tuple[str, ...] = ()
    refutes: bool = False
    reason: str = ""
    # profile contributions (only the dimension this kind can touch)
    numerical: NumericalEvidence = NumericalEvidence.NONE
    exact_computation: ExactComputation = ExactComputation.NONE
    informal_review: InformalReview = InformalReview.NONE
    formal_verification: FormalVerification = FormalVerification.NONE
    external_import: ExternalImport = ExternalImport.NONE
    # review lineages so cross-item independence can be aggregated in merge
    review_lineages: tuple[str, ...] = ()
    human_reviewers: int = 0


def _meta(evidence: Evidence) -> dict:
    gen = evidence.generator_identity or {}
    return gen if isinstance(gen, dict) else {}


def _trust(evidence: Evidence) -> dict:
    # kind-specific structured findings live in generator_identity["findings"]
    return dict(_meta(evidence).get("findings", {}))


# ── per-kind validators ─────────────────────────────────────────────────────────

def validate_source_import(evidence: Evidence) -> Assessment:
    f = _trust(evidence)
    missing = []
    if not f.get("verbatim_extract"):
        missing.append("verbatim_theorem_and_hypothesis_extract")
    if not f.get("source_uri") or not f.get("source_version"):
        missing.append("source_uri+version")
    if not f.get("applicability_check_passed"):
        missing.append("applicability_check")
    if missing:
        return Assessment(False, obligations_missing=tuple(missing),
                          reason="unaudited source import")
    corroborated = bool(f.get("independently_corroborated"))
    return Assessment(
        True,
        obligations_discharged=("verbatim_extract", "source_version", "applicability"),
        external_import=(ExternalImport.INDEPENDENTLY_CORROBORATED if corroborated
                         else ExternalImport.AUDITED_SOURCE),
        reason="audited source import",
    )


def validate_computation(evidence: Evidence) -> Assessment:
    f = _trust(evidence)
    classification = str(f.get("classification", ""))
    replayed = evidence.replay_result == "pass"
    exact = bool(f.get("exact_arithmetic"))
    coverage = bool(f.get("coverage_statement"))
    if not replayed:
        return Assessment(False, obligations_missing=("independent_replay",),
                          reason="computation not independently replayed")
    # a candidate/exact counterexample refutes the claim it targets
    if classification in {"exact_counterexample", "candidate_counterexample"}:
        if classification == "exact_counterexample" and exact and f.get("exact_witness_checked"):
            return Assessment(True, refutes=True,
                              obligations_discharged=("exact_witness", "replay"),
                              exact_computation=ExactComputation.SCOPED_EXACT,
                              reason="exact counterexample")
        return Assessment(False, obligations_missing=("exact_witness_validation",),
                          reason="counterexample awaiting exact validation")
    if classification == "certificate_checked":
        if not f.get("checker_passed"):
            return Assessment(False, obligations_missing=("certificate_checker",),
                              reason="certificate was not accepted by its checker")
        return Assessment(True, obligations_discharged=("certificate", "replay"),
                          exact_computation=ExactComputation.CERTIFICATE_CHECKED,
                          reason="certificate-checked computation")
    if classification == "finite_reduction" and not f.get("finite_reduction_checked"):
        return Assessment(False, obligations_missing=("finite_reduction_checker",),
                          reason="finite reduction lacks a checked reduction certificate")
    if classification in {"exhaustive_finite", "finite_reduction"} and exact and coverage \
            and f.get("result_verified") is True:
        return Assessment(True, obligations_discharged=("exact_arithmetic", "coverage", "replay"),
                          exact_computation=ExactComputation.SCOPED_EXACT,
                          reason="exact finite computation")
    # heuristic / floating point: reproducible evidence only, never proves exact
    return Assessment(True, obligations_discharged=("replay",),
                      numerical=NumericalEvidence.REPRODUCIBLE,
                      reason="reproducible numerical evidence (not a proof)")


def validate_informal_review(evidence: Evidence) -> Assessment:
    f = _trust(evidence)
    reviewers = f.get("reviewers", [])
    if not isinstance(reviewers, list) or not reviewers:
        return Assessment(False, obligations_missing=("at_least_one_reviewer",),
                          reason="no reviewers")
    passing = [r for r in reviewers if r.get("verdict") == "pass" and not r.get("material_errors")]
    if not passing:
        return Assessment(False, obligations_missing=("passing_review",),
                          reason="no passing review without material errors")
    # genuine independence: distinct model families or human reviewers
    lineages = tuple(sorted({str(r.get("lineage", r.get("reviewer_id"))) for r in passing}))
    humans = sum(1 for r in passing if r.get("type") == "human")
    independent = len(lineages) >= 2 or humans >= 2
    return Assessment(
        True,
        obligations_discharged=("two_independent_reviews",) if independent else ("single_review",),
        informal_review=(InformalReview.DOUBLE_INDEPENDENT if independent else InformalReview.SINGLE),
        review_lineages=lineages,
        human_reviewers=humans,
        reason="two genuinely independent hostile reviews" if independent else "single informal review",
    )


def validate_lean_proof(
    evidence: Evidence, *, formal_certificate_valid: bool | None,
    formal_certificate_independent: bool,
) -> Assessment:
    # Evidence HMAC authenticates who asserted metadata; it does not make those
    # assertions kernel facts.  Only the separately authenticated, graph-bound
    # FormalCertificate envelope may discharge formal obligations.
    if formal_certificate_valid is not True:
        return Assessment(
            False,
            obligations_missing=("authenticated_bound_formal_certificate",),
            reason="formal evidence lacks a valid source/environment/type/claim/artifact envelope",
        )
    if evidence.formal_correspondence_certificate_id is None:
        return Assessment(False, obligations_missing=("formal_correspondence_certificate",),
                          reason="no approved formal-correspondence certificate")
    return Assessment(
        True,
        obligations_discharged=("kernel_replay", "no_placeholders", "axiom_whitelist",
                                "target_type_match", "correspondence_certificate"),
        formal_verification=(FormalVerification.INDEPENDENT_CHECKER
                             if formal_certificate_independent
                             else FormalVerification.KERNEL_CHECKED),
        reason="clean kernel-checked proof of the locked target",
    )


def validate_counterexample(evidence: Evidence) -> Assessment:
    f = _trust(evidence)
    if not f.get("exact_witness_checked") or evidence.replay_result != "pass":
        return Assessment(False, obligations_missing=("exact_witness_checked", "replay"),
                          reason="counterexample witness not exactly checked/replayed")
    if not f.get("in_stated_domain", True):
        return Assessment(False, obligations_missing=("domain_membership",),
                          reason="witness outside the stated domain")
    return Assessment(True, refutes=True,
                      obligations_discharged=("exact_witness", "domain", "replay"),
                      exact_computation=ExactComputation.SCOPED_EXACT,
                      reason="checked exact counterexample")


def validate_expert_review(evidence: Evidence) -> Assessment:
    f = _trust(evidence)
    reviewers = f.get("reviewers", [])
    authed = [r for r in reviewers if r.get("authenticated") and r.get("scope")]
    if not authed:
        return Assessment(False, obligations_missing=("authenticated_reviewer_with_scope",),
                          reason="no authenticated expert with recorded scope")
    passing = [r for r in authed if r.get("verdict") == "pass"]
    if not passing:
        return Assessment(True, obligations_discharged=("authenticated_scope",),
                          reason="authenticated expert review recorded (not passing)")
    lineages = tuple(sorted({str(r.get("reviewer_id")) for r in passing}))
    independent = len(lineages) >= 2
    return Assessment(True, obligations_discharged=("authenticated_scope", "expert_pass"),
                      informal_review=(InformalReview.DOUBLE_INDEPENDENT if independent
                                       else InformalReview.SINGLE),
                      review_lineages=lineages, human_reviewers=len(passing),
                      reason="authenticated expert review")


_VALIDATORS: dict[EvidenceKind, Callable[[Evidence], Assessment]] = {
    EvidenceKind.SOURCE_IMPORT: validate_source_import,
    EvidenceKind.NUMERICAL: validate_computation,
    EvidenceKind.EXACT_COMPUTATION: validate_computation,
    EvidenceKind.COUNTEREXAMPLE: validate_counterexample,
    EvidenceKind.INFORMAL_REVIEW: validate_informal_review,
    EvidenceKind.SAT_CERTIFICATE: validate_computation,
    EvidenceKind.EXPERT_REVIEW: validate_expert_review,
}


def validate_evidence(
    evidence: Evidence, *, env: dict[str, str] | None = None,
    expected_claim_hashes: dict[str, str] | None = None,
    formal_correspondence_valid: bool | None = None,
    formal_certificate_valid: bool | None = None,
    formal_certificate_independent: bool = False,
) -> Assessment:
    """Dispatch to the closed validator for this evidence kind."""
    if not verify_evidence_attestation(
        evidence, env=env, expected_claim_hashes=expected_claim_hashes
    ):
        return Assessment(
            False,
            obligations_missing=("authenticated_evidence", "claim_hash_binding"),
            reason="evidence attestation missing, invalid, or bound to another claim",
        )
    provenance_missing: list[str] = []
    artifact_kinds = {
        EvidenceKind.SOURCE_IMPORT,
        EvidenceKind.NUMERICAL,
        EvidenceKind.EXACT_COMPUTATION,
        EvidenceKind.COUNTEREXAMPLE,
        EvidenceKind.LEAN_PROOF,
        EvidenceKind.ATP_PROOF,
        EvidenceKind.SAT_CERTIFICATE,
    }
    replay_kinds = artifact_kinds - {EvidenceKind.SOURCE_IMPORT}
    if evidence.kind in artifact_kinds:
        if not evidence.assertion_scope.strip():
            provenance_missing.append("assertion_scope")
        if not evidence.artifact_hashes or any(
            re.fullmatch(r"[0-9a-f]{64}", digest) is None for digest in evidence.artifact_hashes
        ):
            provenance_missing.append("content_addressed_artifact")
    if evidence.kind in replay_kinds:
        if re.fullmatch(r"[0-9a-f]{64}", evidence.environment_hash) is None:
            provenance_missing.append("environment_hash")
        if not evidence.replay_command.strip():
            provenance_missing.append("replay_command")
        if not any(
            isinstance(identity, dict) and identity.get("attested") and identity.get("id")
            for identity in evidence.verifier_identities
        ):
            provenance_missing.append("attested_verifier_identity")
    if evidence.kind is EvidenceKind.SOURCE_IMPORT:
        source_hash = str(_trust(evidence).get("source_content_hash", ""))
        if source_hash not in evidence.artifact_hashes:
            provenance_missing.append("source_content_hash_binding")
    if provenance_missing:
        return Assessment(
            False,
            obligations_missing=tuple(provenance_missing),
            reason="evidence lacks required immutable provenance",
        )
    if evidence.kind in {EvidenceKind.LEAN_PROOF, EvidenceKind.ATP_PROOF} \
            and formal_correspondence_valid is not True:
        return Assessment(
            False,
            obligations_missing=("approved_bound_formal_correspondence",),
            reason="formal evidence lacks an approved certificate bound to this exact claim/type",
        )
    if evidence.kind in {EvidenceKind.LEAN_PROOF, EvidenceKind.ATP_PROOF}:
        return validate_lean_proof(
            evidence,
            formal_certificate_valid=formal_certificate_valid,
            formal_certificate_independent=formal_certificate_independent,
        )
    validator = _VALIDATORS.get(evidence.kind)
    if validator is None:  # pragma: no cover - EvidenceKind is exhaustive
        return Assessment(False, reason=f"no validator for kind {evidence.kind}")
    return validator(evidence)


# ── profile merge / support decision ─────────────────────────────────────────────

_NUMERICAL_ORDER = (NumericalEvidence.NONE, NumericalEvidence.REPRODUCIBLE)
_EXACT_COMPUTATION_ORDER = (
    ExactComputation.NONE,
    ExactComputation.SCOPED_EXACT,
    ExactComputation.CERTIFICATE_CHECKED,
)
_INFORMAL_REVIEW_ORDER = (
    InformalReview.NONE,
    InformalReview.SINGLE,
    InformalReview.DOUBLE_INDEPENDENT,
)
_FORMAL_VERIFICATION_ORDER = (
    FormalVerification.NONE,
    FormalVerification.KERNEL_CHECKED,
    FormalVerification.INDEPENDENT_CHECKER,
)
_EXTERNAL_IMPORT_ORDER = (
    ExternalImport.NONE,
    ExternalImport.AUDITED_SOURCE,
    ExternalImport.INDEPENDENTLY_CORROBORATED,
)
_Level = TypeVar("_Level")


def _max_level(order: tuple[_Level, ...], a: _Level, b: _Level) -> _Level:
    return a if order.index(a) >= order.index(b) else b


@dataclass
class MergedProfile:
    profile: EvidenceProfile
    refuted: bool = False
    supporting_dimensions: tuple[str, ...] = ()
    strong_supporting_dimensions: tuple[str, ...] = ()
    obligations: list[str] = field(default_factory=list)


def merge_assessments(
    assessments: list[Assessment],
    *,
    scope: str = "general",
    intent_certificate_id: str | None = None,
    formal_correspondence_certificate_id: str | None = None,
) -> MergedProfile:
    """Combine per-evidence assessments into one claim profile + truth signal."""
    numerical = NumericalEvidence.NONE
    exact_computation = ExactComputation.NONE
    informal_review = InformalReview.NONE
    formal_verification = FormalVerification.NONE
    external_import = ExternalImport.NONE
    refuted = False
    obligations: list[str] = []
    lineages: set[str] = set()
    humans = 0
    for a in assessments:
        if not a.admitted:
            continue
        refuted = refuted or a.refutes
        numerical = _max_level(_NUMERICAL_ORDER, numerical, a.numerical)
        exact_computation = _max_level(
            _EXACT_COMPUTATION_ORDER, exact_computation, a.exact_computation
        )
        informal_review = _max_level(
            _INFORMAL_REVIEW_ORDER, informal_review, a.informal_review
        )
        formal_verification = _max_level(
            _FORMAL_VERIFICATION_ORDER, formal_verification, a.formal_verification
        )
        external_import = _max_level(
            _EXTERNAL_IMPORT_ORDER, external_import, a.external_import
        )
        obligations.extend(a.obligations_discharged)
        lineages.update(a.review_lineages)
        humans += a.human_reviewers

    # Independence can accrue across separate review evidence items.
    if len(lineages) >= 2 or humans >= 2:
        informal_review = _max_level(
            _INFORMAL_REVIEW_ORDER,
            informal_review,
            InformalReview.DOUBLE_INDEPENDENT,
        )

    profile = EvidenceProfile(
        numerical=numerical,
        exact_computation=exact_computation,
        informal_review=informal_review,
        formal_verification=formal_verification,
        external_import=external_import,
        intent_certificate_id=intent_certificate_id,
        formal_correspondence_certificate_id=formal_correspondence_certificate_id,
    )
    supporting = _supporting_dimensions(profile, scope)
    # Strong support = hard evidence (formal / exact / corroborated import). An
    # informal review contradicted by a checked counterexample was simply wrong,
    # so it does not create a genuine CONFLICTED state.
    strong = tuple(d for d in supporting if d != "informal_review")
    return MergedProfile(profile=profile, refuted=refuted,
                         supporting_dimensions=tuple(supporting),
                         strong_supporting_dimensions=strong, obligations=obligations)


def _supporting_dimensions(profile: EvidenceProfile, scope: str) -> list[str]:
    """Which dimensions independently *support* the claim (T2+), not merely hint."""
    out: list[str] = []
    if profile.formal_verification in (FormalVerification.KERNEL_CHECKED,
                                       FormalVerification.INDEPENDENT_CHECKER):
        out.append("formal_verification")
    if profile.exact_computation == ExactComputation.CERTIFICATE_CHECKED:
        out.append("exact_computation")
    if profile.exact_computation == ExactComputation.SCOPED_EXACT and scope in {
        "finite_domain", "parameter_range", "conditional"
    }:
        out.append("exact_computation")
    if profile.informal_review == InformalReview.DOUBLE_INDEPENDENT:
        out.append("informal_review")
    if profile.external_import == ExternalImport.INDEPENDENTLY_CORROBORATED:
        out.append("external_import")
    return out
