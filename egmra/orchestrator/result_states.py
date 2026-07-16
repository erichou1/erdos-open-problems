"""Honest result-state taxonomy (spec §13.6 result honesty; task decision F).

The orchestrator's internal ``outcome`` label is gate-centric ("honest_triage
_report", "verified_finite_or_conditional_result", …). This module maps a
completed :class:`~egmra.orchestrator.loop.ResearchResult` onto the ten public,
non-overlapping epistemic states the operator contract enumerates, using only
*real* signals already recorded on the result: the frozen contract's parser
agreement and executed integrity probes, the goal claim's truth status and
multidimensional evidence profile, and whether a release/formal/external
validation actually exists.

Design rule: never upgrade. A weaker signal can never be reported as a stronger
state. In particular a locally assembled/released proof is a *candidate* — it is
never reported as externally validated, and a finite/scoped computation is never
reported as a general proof.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from egmra.truth.entities import (
    ExactComputation,
    ExternalImport,
    FormalVerification,
    InformalReview,
    NumericalEvidence,
    StrEnum,
    TruthStatus,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from egmra.truth.entities import Claim, EvidenceProfile
    from egmra.orchestrator.loop import ResearchResult

# Probe kinds that indicate the *reading* is untrustworthy (not that the
# statement is false): the parser was insensitive, ambiguous, or ill-typed.
_INTERPRETATION_PROBE_KINDS = frozenset({"invariance", "covariance", "dimensional"})
# Probe kinds that, when an executable predicate found a real failure, indicate
# the statement as posed does not hold (a concrete counterexample exists).
_REFUTATION_PROBE_KINDS = frozenset({"boundary", "counterexample"})


class ResultState(StrEnum):
    """The ten enumerated honest outcomes of a research attempt."""

    BLOCKED_BY_INTERPRETATION = "BLOCKED_BY_INTERPRETATION"
    OPEN_NO_PROGRESS = "OPEN_NO_PROGRESS"
    PARTIAL_PROGRESS = "PARTIAL_PROGRESS"
    CONDITIONAL_RESULT = "CONDITIONAL_RESULT"
    COMPUTATIONAL_EVIDENCE = "COMPUTATIONAL_EVIDENCE"
    CANDIDATE_PROOF = "CANDIDATE_PROOF"
    CANDIDATE_DISPROOF = "CANDIDATE_DISPROOF"
    FORMALLY_VERIFIED_CANDIDATE = "FORMALLY_VERIFIED_CANDIDATE"
    EXTERNALLY_VALIDATED_SOLUTION = "EXTERNALLY_VALIDATED_SOLUTION"
    EXTERNALLY_VALIDATED_DISPROOF = "EXTERNALLY_VALIDATED_DISPROOF"


@dataclass(frozen=True)
class ResultClassification:
    """A public result state plus the exact signals that justify it."""

    state: ResultState
    rationale: str
    signals: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": str(self.state),
            "rationale": self.rationale,
            "signals": dict(self.signals),
        }


def _goal_claim(result: "ResearchResult", goal_claim_id: str | None) -> "Claim | None":
    claims = result.graph.claims
    candidates = []
    if result.certificate is not None:
        candidates.append(getattr(result.certificate, "result_claim_id", None))
    if result.compiled_proof is not None:
        candidates.append(getattr(result.compiled_proof, "goal_claim_id", None))
    candidates.append(goal_claim_id)
    candidates.append("goal")
    for cid in candidates:
        if cid and cid in claims:
            return claims[cid]
    return None


def _executed_probe_failure(result: "ResearchResult", kinds: frozenset[str]):
    for probe in result.contract.probes:
        if probe.executed and not probe.passed and probe.kind in kinds:
            return probe
    return None


_INTENT_REVIEW_METHODS = frozenset({
    "independent_parse", "examples", "anti_examples", "paraphrase",
    "local_mutation",
})


def _certified_reading(result: "ResearchResult") -> bool:
    """True when a VALID intent certificate binds this exact source + reading.

    Interpretation-integrity probes measure whether the MACHINE parser's
    reading can be trusted.  An authenticated intent certificate whose hashes
    bind this exact source and primary interpretation certifies the reading
    through a stronger channel (its methods include the independent versions
    of the same checks), so a parser-integrity wobble no longer makes "the
    reading is unknown" the honest headline.  Fail-closed: any missing hash,
    wrong verdict, missing method, or signature failure keeps the block.
    """
    contract = result.contract
    graph = getattr(result, "graph", None)
    certificates = getattr(graph, "intent_certificates", None) or {}
    source_hash = getattr(contract, "source_bytes_hash", None)
    lattice_nodes = getattr(contract.lattice, "nodes", None)
    if not certificates or not source_hash or not lattice_nodes:
        return False
    try:
        from egmra.intake.review import (
            interpretation_review_hash,
            verify_intent_certificate,
        )
        from egmra.truth.entities import Verdict

        expected_interpretation = interpretation_review_hash(lattice_nodes[0])
    except Exception:  # noqa: BLE001 - classification must never crash a run
        return False
    for certificate in certificates.values():
        try:
            if (
                certificate.verdict is Verdict.APPROVED
                and certificate.source_bytes_hash == source_hash
                and certificate.interpretation_hash == expected_interpretation
                and _INTENT_REVIEW_METHODS.issubset(set(certificate.methods))
                and verify_intent_certificate(certificate)
            ):
                return True
        except Exception:  # noqa: BLE001 - a malformed certificate never lifts
            continue
    return False


def _valid_release(result: "ResearchResult", goal: "Claim | None") -> bool:
    """A release artifact that is actually bound to *this* claim and contract.

    A positive terminal (externally validated) state may never rest on a bare
    evidence-profile flag: it requires a promoted release certificate whose claim
    id, claim hash, and contract hash bind the exact goal, and whose signature
    verifies. Any binding mismatch, missing promotion, or failed integrity check
    denies the release.
    """
    cert = result.certificate
    promotion = result.promotion
    compiled = result.compiled_proof
    if cert is None or goal is None:
        return False
    if promotion is None or not getattr(promotion, "promoted", False):
        return False
    if compiled is None or not getattr(compiled, "complete", False):
        return False
    # Claim identity: the certificate must name and hash-bind THIS goal claim.
    if getattr(cert, "result_claim_id", None) != goal.claim_id:
        return False
    goal_hash = getattr(goal, "canonical_hash", "") or ""
    if goal_hash and getattr(cert, "result_claim_hash", None) != goal_hash:
        return False
    if getattr(compiled, "goal_claim_id", goal.claim_id) != goal.claim_id:
        return False
    # Contract identity: guards a certificate minted for a different target.
    contract_hash = getattr(result.contract, "contract_hash", None)
    if callable(contract_hash):
        if getattr(cert, "problem_contract_hash", None) != contract_hash():
            return False
    # Cryptographic integrity: a stale/revoked/forged certificate fails closed.
    verify = getattr(cert, "verify", None)
    if callable(verify):
        try:
            if not verify(event_log=getattr(result.graph, "log", None)):
                return False
        except Exception:
            return False
    return True


def _valid_formal_certificate(result: "ResearchResult", goal: "Claim | None") -> bool:
    """A claim-bound formal verification backed by a real gate/certificate artifact.

    The goal's ``formal_verification`` axis alone is insufficient (a worker could
    set it): a kernel/independent-checker tier must be corroborated by a gate
    profile at T4/T5 with full formal correspondence (F2) and a bound formal
    correspondence certificate id.
    """
    if goal is None:
        return False
    profile = goal.evidence_profile
    if profile.formal_verification not in {
        FormalVerification.KERNEL_CHECKED,
        FormalVerification.INDEPENDENT_CHECKER,
    }:
        return False
    gates = result.gates
    if gates is None:
        return False
    if getattr(gates, "truth", "") not in {"T4", "T5"}:
        return False
    if getattr(gates, "formal_correspondence", "") != "F2":
        return False
    return bool(getattr(gates, "formal_correspondence_certificate_id", ""))


def classify_result(
    result: "ResearchResult", *, goal_claim_id: str | None = None
) -> ResultClassification:
    """Map a completed research result onto one honest public state."""
    contract = result.contract
    goal = _goal_claim(result, goal_claim_id)
    goal_status = goal.truth_status if goal is not None else TruthStatus.UNKNOWN
    profile: "EvidenceProfile | None" = goal.evidence_profile if goal is not None else None

    has_external = (
        profile is not None
        and profile.external_import == ExternalImport.INDEPENDENTLY_CORROBORATED
    )
    has_formal = profile is not None and profile.formal_verification in {
        FormalVerification.KERNEL_CHECKED,
        FormalVerification.INDEPENDENT_CHECKER,
    }
    has_exact = profile is not None and profile.exact_computation in {
        ExactComputation.SCOPED_EXACT,
        ExactComputation.CERTIFICATE_CHECKED,
    }
    has_numerical = profile is not None and profile.numerical == NumericalEvidence.REPRODUCIBLE
    has_informal = profile is not None and profile.informal_review in {
        InformalReview.SINGLE,
        InformalReview.DOUBLE_INDEPENDENT,
    }
    conditional = goal is not None and goal.scope == "conditional"

    interpretation_probe = _executed_probe_failure(result, _INTERPRETATION_PROBE_KINDS)
    refutation_probe = _executed_probe_failure(result, _REFUTATION_PROBE_KINDS)
    malformed = any(d.startswith("malformed:") for d in contract.unresolved_decisions)
    # A binding, signature-verified intent certificate certifies the READING
    # itself; it lifts parser-integrity probe failures only.  A still-blocked
    # lattice or a malformed statement is never lifted at classification.
    probe_lifted_by_certificate = (
        interpretation_probe is not None
        and not contract.lattice.release_blocked
        and not malformed
        and _certified_reading(result)
    )
    interpretation_blocked = (
        contract.lattice.release_blocked
        or malformed
        or (interpretation_probe is not None and not probe_lifted_by_certificate)
    )
    release_ok = _valid_release(result, goal)
    formal_ok = _valid_formal_certificate(result, goal)

    goal_id = goal.claim_id if goal is not None else (goal_claim_id or "goal")
    supported_subclaims = [
        cid
        for cid, claim in result.graph.claims.items()
        if cid != goal_id and claim.truth_status == TruthStatus.SUPPORTED
    ]
    # An incomplete compiler object is created even when the only admitted node
    # is the still-UNKNOWN goal.  Counting that bookkeeping artifact as
    # mathematical progress overstates an empty run.  Partial assembly requires
    # at least one admitted dependency that actually contributes to the proof.
    partial_assembly = bool(
        result.compiled_proof is not None
        and not result.compiled_proof.complete
        and getattr(result.compiled_proof, "used_claim_ids", ())
    )

    signals: dict[str, Any] = {
        "outcome": result.outcome,
        "goal_truth_status": str(goal_status),
        "valid_release": release_ok,
        "valid_formal_certificate": formal_ok,
        "lattice_release_blocked": contract.lattice.release_blocked,
        "malformed": malformed,
        "interpretation_probe_failed": None
        if interpretation_probe is None
        else interpretation_probe.name,
        "interpretation_probe_lifted_by_intent_certificate": probe_lifted_by_certificate,
        "refutation_probe_failed": None
        if refutation_probe is None
        else refutation_probe.name,
        "evidence_profile": profile.to_dict() if profile is not None else None,
        "conditional_scope": conditional,
        "supported_subclaims": supported_subclaims,
        "partial_assembly": partial_assembly,
    }

    # 1. INTERPRETATION INTEGRITY DOMINATES. If the reading is ambiguous,
    #    malformed, or parser-disputed, no evidence attached to that
    #    interpretation may be trusted — including formal or external-looking
    #    evidence. A blocked interpretation can never be a proved/validated state.
    if interpretation_blocked:
        reason = "independent parsers disagree on a single interpretation"
        if interpretation_probe is not None and not probe_lifted_by_certificate:
            reason = (
                f"integrity probe '{interpretation_probe.name}' failed: "
                f"{interpretation_probe.detail}"
            )
        elif malformed:
            reason = "statement is malformed / unparseable"
        return ResultClassification(
            ResultState.BLOCKED_BY_INTERPRETATION, reason, signals
        )

    # 2. Externally validated — the strongest, polarity-split state. Requires a
    #    valid, claim-bound release artifact AND independent external corroboration.
    #    A bare evidence-profile flag without a release is NOT externally validated.
    if release_ok and has_external and goal_status == TruthStatus.SUPPORTED:
        return ResultClassification(
            ResultState.EXTERNALLY_VALIDATED_SOLUTION,
            "goal claim SUPPORTED with a valid claim-bound release and "
            "independent external corroboration",
            signals,
        )
    if release_ok and has_external and goal_status == TruthStatus.REFUTED:
        return ResultClassification(
            ResultState.EXTERNALLY_VALIDATED_DISPROOF,
            "goal claim REFUTED with a valid claim-bound release and "
            "independent external corroboration",
            signals,
        )

    # 3. Formally verified candidate — requires a claim-bound formal certificate
    #    backed by a T4/T5 + F2 gate artifact, not just a profile flag.
    if goal_status in {TruthStatus.SUPPORTED, TruthStatus.REFUTED} and formal_ok:
        return ResultClassification(
            ResultState.FORMALLY_VERIFIED_CANDIDATE,
            "goal claim carries a claim-bound kernel-checked formal certificate "
            "(not yet externally validated)",
            signals,
        )

    # 4. A concrete refutation: the goal was refuted, or an executed probe found a
    #    counterexample to the statement as posed.
    if goal_status == TruthStatus.REFUTED or refutation_probe is not None:
        detail = "goal claim REFUTED"
        if refutation_probe is not None:
            detail = (
                f"counterexample probe '{refutation_probe.name}' failed: "
                f"{refutation_probe.detail}"
            )
        return ResultClassification(ResultState.CANDIDATE_DISPROOF, detail, signals)

    # 5. A supported goal: conditional, argued proof, or computational evidence.
    if goal_status == TruthStatus.SUPPORTED:
        if conditional:
            return ResultClassification(
                ResultState.CONDITIONAL_RESULT,
                "goal claim SUPPORTED only under stated (unproven) hypotheses",
                signals,
            )
        if has_informal:
            return ResultClassification(
                ResultState.CANDIDATE_PROOF,
                "goal claim SUPPORTED by an argued informal proof under review "
                "(local candidate, not externally validated)",
                signals,
            )
        if has_exact or has_numerical:
            return ResultClassification(
                ResultState.COMPUTATIONAL_EVIDENCE,
                "goal claim SUPPORTED by finite/scoped computation only "
                "(not a general proof)",
                signals,
            )
        if result.compiled_proof is not None and result.compiled_proof.complete:
            return ResultClassification(
                ResultState.CANDIDATE_PROOF,
                "goal claim SUPPORTED with an assembled candidate proof",
                signals,
            )
        return ResultClassification(
            ResultState.PARTIAL_PROGRESS,
            "goal claim marked SUPPORTED but without a concrete evidence artifact",
            signals,
        )

    # 6. No result on the goal: distinguish partial progress from no progress.
    if supported_subclaims or partial_assembly:
        return ResultClassification(
            ResultState.PARTIAL_PROGRESS,
            "supporting sub-results established but the goal claim remains open",
            signals,
        )
    return ResultClassification(
        ResultState.OPEN_NO_PROGRESS,
        "the interpretation was fixed and the problem attempted, but no "
        "supporting evidence was produced",
        signals,
    )
