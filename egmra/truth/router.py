"""Evidence router: dispatch by kind, then set the claim's tier (spec §10.2)."""

from __future__ import annotations

from egmra.truth.entities import (
    Evidence,
    EvidenceKind,
    TruthStatus,
    Verdict,
)
from egmra.truth.graph import EpistemicGraph
from egmra.truth.validators import merge_assessments, validate_evidence
from egmra.lean.service import verify_formal_certificate


class EvidenceRouter:
    """Routes evidence to type-specific validators and updates claim tiers.

    The router is the *only* component (besides revocation) allowed to change a
    claim's evidence profile / truth status. Agent proposals never can.
    """

    def __init__(
        self, graph: EpistemicGraph, *, validator_id: str = "evidence-router-v1",
        evidence_env: dict[str, str] | None = None,
        formal_env: dict[str, str] | None = None,
    ):
        self.graph = graph
        self.validator_id = validator_id
        self.evidence_env = evidence_env
        self.formal_env = formal_env
        self._authority_token = graph._truth_authority_for_router()

    def admit(self, evidence: Evidence, *, actor: dict) -> list[str]:
        """Register evidence and revalidate every claim it touches.

        Returns the list of claim ids whose truth status changed.
        """
        self.graph.register_evidence(evidence, actor=actor)
        changed: list[str] = []
        for claim_id in evidence.claim_ids:
            if self.revalidate(claim_id, actor=actor):
                changed.append(claim_id)
        return changed

    def revalidate(self, claim_id: str, *, actor: dict) -> bool:
        """Recompute a claim's profile/truth from its currently-valid evidence.

        Idempotent and safe to call during both admission and revocation.
        Returns True if the truth status changed.
        """
        claim = self.graph.claims[claim_id]
        valid_evidence = [
            self.graph.evidence[eid]
            for eid in claim.evidence_ids
            if eid in self.graph.evidence and self.graph.evidence[eid].valid
        ]
        assessments = []
        for ev in valid_evidence:
            correspondence_valid = self._formal_correspondence_valid(ev)
            formal_valid, independent = self._formal_certificate_status(
                ev, correspondence_valid=correspondence_valid
            )
            assessments.append(validate_evidence(
                ev,
                env=self.evidence_env,
                expected_claim_hashes={
                    cid: self.graph.claims[cid].canonical_hash for cid in ev.claim_ids
                    if cid in self.graph.claims
                },
                formal_correspondence_valid=correspondence_valid,
                formal_certificate_valid=formal_valid,
                formal_certificate_independent=independent,
            ))

        # Carry through the strongest correspondence certificate on lean evidence.
        corr_cert = None
        for ev in valid_evidence:
            if ev.formal_correspondence_certificate_id:
                corr_cert = ev.formal_correspondence_certificate_id
        intent_cert = claim.evidence_profile.intent_certificate_id

        merged = merge_assessments(
            assessments,
            scope=claim.scope,
            intent_certificate_id=intent_cert,
            formal_correspondence_certificate_id=corr_cert,
        )

        new_status = self._decide_status(claim_id, merged)
        prior_status = claim.truth_status
        if new_status == prior_status and merged.profile.to_dict() == claim.evidence_profile.to_dict():
            return False

        reason = self._reason_code(new_status, merged)
        if new_status in (TruthStatus.REFUTED, TruthStatus.CONFLICTED):
            self.graph.apply_invalidation(
                claim_id=claim_id, new_profile=merged.profile, truth_status=new_status,
                reason_code=reason, actor={**actor, "validator_id": self.validator_id},
                authority_token=self._authority_token,
            )
        else:
            self.graph.apply_validated_admission(
                claim_id=claim_id, new_profile=merged.profile, truth_status=new_status,
                validator_id=self.validator_id, reason_code=reason, actor=actor,
                authority_token=self._authority_token,
            )
        return new_status != prior_status

    def _decide_status(self, claim_id: str, merged) -> TruthStatus:
        supported_own = bool(merged.supporting_dimensions)
        if merged.refuted:
            # A checked counterexample alongside surviving *hard* support (a kernel
            # proof or exact computation) of the same scope is a genuine conflict.
            # An informal review contradicted by a checked counterexample was
            # simply wrong, so the claim is cleanly REFUTED.
            return (TruthStatus.CONFLICTED if merged.strong_supporting_dimensions
                    else TruthStatus.REFUTED)
        if not supported_own:
            return TruthStatus.UNKNOWN
        # Self-contained kernel proofs do not depend on premise tiers.
        if "formal_verification" in merged.supporting_dimensions:
            return TruthStatus.SUPPORTED
        # Otherwise the claim's support presumes its dependencies hold.
        if self._all_dependencies_supported(claim_id):
            return TruthStatus.SUPPORTED
        return TruthStatus.UNKNOWN

    def _all_dependencies_supported(self, claim_id: str) -> bool:
        claim = self.graph.claims[claim_id]
        for dep in claim.dependencies:
            dep_claim = self.graph.claims.get(dep)
            if dep_claim is None or dep_claim.truth_status != TruthStatus.SUPPORTED:
                return False
        return True

    def _formal_correspondence_valid(self, evidence: Evidence) -> bool | None:
        if evidence.kind not in {EvidenceKind.LEAN_PROOF, EvidenceKind.ATP_PROOF}:
            return None
        if len(evidence.claim_ids) != 1:
            return False
        claim = self.graph.claims.get(evidence.claim_ids[0])
        cert = self.graph.correspondence_certificates.get(
            evidence.formal_correspondence_certificate_id or ""
        )
        if claim is None or cert is None or cert.verdict is not Verdict.APPROVED:
            return False
        intent = self.graph.intent_certificates.get(cert.intent_certificate_id)
        if intent is None or intent.verdict is not Verdict.APPROVED:
            return False
        # Lazy import avoids a package-initialization cycle: Lean's
        # correspondence module uses truth entity types, while truth imports the
        # router during package initialization.
        from egmra.lean.correspondence import verify_formal_correspondence_certificate
        from egmra.intake.review import verify_intent_certificate

        return bool(
            verify_formal_correspondence_certificate(cert, env=self.formal_env)
            and verify_intent_certificate(intent, env=self.formal_env)
            and
            evidence.intent_certificate_id == intent.certificate_id
            and cert.informal_claim_hash == claim.canonical_hash
            and intent.informal_claim_hash == claim.canonical_hash
        )

    def _formal_certificate_status(
        self, evidence: Evidence, *, correspondence_valid: bool | None,
    ) -> tuple[bool | None, bool]:
        """Authenticate a formal envelope against graph- and evidence-derived bindings."""
        if evidence.kind not in {EvidenceKind.LEAN_PROOF, EvidenceKind.ATP_PROOF}:
            return None, False
        if correspondence_valid is not True or len(evidence.claim_ids) != 1:
            return False, False
        claim = self.graph.claims.get(evidence.claim_ids[0])
        correspondence = self.graph.correspondence_certificates.get(
            evidence.formal_correspondence_certificate_id or ""
        )
        envelope = evidence.generator_identity.get("formal_certificate")
        source_hash = evidence.generator_identity.get("source_hash")
        if (
            claim is None
            or correspondence is None
            or not isinstance(envelope, dict)
            or not isinstance(source_hash, str)
        ):
            return False, False
        certificate_digest = envelope.get("certificate_digest")
        if not isinstance(certificate_digest, str) or (
            certificate_digest not in evidence.artifact_hashes
        ):
            return False, False
        required_artifacts = tuple(
            digest for digest in evidence.artifact_hashes
            if digest != certificate_digest
        )
        valid = verify_formal_certificate(
            envelope,
            env=self.formal_env,
            expected_source_hash=source_hash,
            expected_environment_id=evidence.environment_hash,
            expected_type_hash=correspondence.elaborated_type_hash,
            expected_claim_bindings={claim.claim_id: claim.canonical_hash},
            required_artifact_hashes=required_artifacts,
            expected_declaration_name=correspondence.lean_declaration_name,
        )
        return valid, bool(valid and envelope.get("independent_checker_id"))

    @staticmethod
    def _reason_code(status: TruthStatus, merged) -> str:
        if status == TruthStatus.REFUTED:
            return "REFUTED_BY_COUNTEREXAMPLE"
        if status == TruthStatus.CONFLICTED:
            return "CONFLICTING_STRONG_EVIDENCE"
        if status == TruthStatus.SUPPORTED:
            dims = "+".join(merged.supporting_dimensions)
            return f"SUPPORTED_BY_{dims.upper()}"
        return "INSUFFICIENT_OR_DEPENDENCY_DEBT"
