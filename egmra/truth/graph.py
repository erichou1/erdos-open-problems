"""The epistemic claim graph: append-only events + materialized views (spec §6.6, §10).

This replaces the current mutable ``ResearchState`` JSON. The authoritative record
is the :class:`~egmra.truth.events.EventLog`; this class maintains the in-memory
materialized view (and can persist it to SQLite via :mod:`egmra.truth.views`).

Key invariant (§6.6): *a claim can guide search at a weak tier, but every
downstream use retains its tier; no model summary upgrades evidence.* Therefore
the evidence profile and truth status can only be changed through
:meth:`apply_validated_admission` / :meth:`apply_invalidation`, which are called
by the evidence router and revocation engine after type-specific validation —
never by an agent proposal.
"""

from __future__ import annotations

import copy
import time
from dataclasses import replace
from typing import Any, Iterable

from egmra.provenance.hashing import content_id, sha256_hex
from egmra.truth.entities import (
    Branch,
    Claim,
    Evidence,
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
    EvidenceKind,
)
from egmra.truth.events import Event, EventLog


class GraphError(RuntimeError):
    """Raised on an illegal graph operation (e.g. duplicate id, unknown ref)."""


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class EpistemicGraph:
    def __init__(self, log: EventLog):
        self.log = log
        self.problems: dict[str, Problem] = {}
        self.interpretations: dict[str, Interpretation] = {}
        self.claims: dict[str, Claim] = {}
        self.branches: dict[str, Branch] = {}
        self.evidence: dict[str, Evidence] = {}
        self.relations: dict[str, Relation] = {}
        self.intent_certificates: dict[str, IntentCertificate] = {}
        self.correspondence_certificates: dict[str, FormalCorrespondenceCertificate] = {}
        self.__truth_plane_token = object()
        if log.events:
            self._replay_events()

    def snapshot_claim(
        self, claim_id: str, *, env: dict[str, str] | None = None,
        issued_at: float | None = None,
    ):
        """Issue a signed release input from a fresh authoritative replay.

        The current materialized objects are deliberately ignored: callers can
        mutate Python dataclasses, but only replayed signed events may cross the
        truth/release boundary.
        """
        from egmra.truth.snapshots import TruthSnapshotError, issue_truth_snapshot

        if not self.log.verify_integrity():
            raise TruthSnapshotError("event log integrity failed")
        replayed = EpistemicGraph(self.log)
        claim = replayed.claims.get(claim_id)
        if claim is None:
            raise TruthSnapshotError(f"unknown claim {claim_id!r}")
        evidence_records = [
            replayed.evidence[evidence_id].to_dict()
            for evidence_id in sorted(claim.evidence_ids)
            if evidence_id in replayed.evidence and replayed.evidence[evidence_id].valid
        ]
        return issue_truth_snapshot(
            claim_id=claim.claim_id,
            canonical_hash=claim.canonical_hash,
            truth_status=str(claim.truth_status),
            evidence_profile=copy.deepcopy(claim.evidence_profile.to_dict()),
            status_version=claim.status_version,
            evidence_digest=content_id(evidence_records),
            event_log=self.log,
            env=env,
            issued_at=issued_at,
        )

    # ── problems / interpretations ──────────────────────────────────────────────

    def add_problem(self, problem: Problem, *, actor: dict[str, Any]) -> Problem:
        if problem.problem_id in self.problems:
            raise GraphError(f"duplicate problem {problem.problem_id}")
        if problem.status_version != 1:
            raise GraphError("new problem must start at version 1")
        self.log.append(
            action="PROBLEM_FROZEN",
            actor=actor,
            object_ids=[problem.problem_id],
            new_versions={problem.problem_id: problem.status_version},
            input_hashes=[problem.original_bytes_hash] if problem.original_bytes_hash else [],
            reason_code="SOURCE_FROZEN",
            payload={"problem": problem.to_dict()},
        )
        self.problems[problem.problem_id] = problem
        return problem

    def add_interpretation(self, interp: Interpretation, *, actor: dict[str, Any]) -> Interpretation:
        if interp.interpretation_id in self.interpretations:
            raise GraphError(f"duplicate interpretation {interp.interpretation_id}")
        if interp.parent_problem_id not in self.problems:
            raise GraphError(f"interpretation references unknown problem {interp.parent_problem_id}")
        if interp.status_version != 1:
            raise GraphError("new interpretation must start at version 1")
        self.log.append(
            action="INTERPRETATION_ADDED",
            actor=actor,
            object_ids=[interp.interpretation_id],
            new_versions={interp.interpretation_id: interp.status_version},
            reason_code=f"RELATION_{interp.relation_to_parent.upper()}",
            payload={"interpretation": interp.to_dict()},
        )
        self.interpretations[interp.interpretation_id] = interp
        self.problems[interp.parent_problem_id].interpretations.append(interp.interpretation_id)
        return interp

    # ── certificates ──────────────────────────────────────────────────────────────

    def issue_intent_certificate(self, cert: IntentCertificate, *, actor: dict[str, Any]) -> IntentCertificate:
        if cert.certificate_id in self.intent_certificates:
            raise GraphError(f"duplicate intent certificate {cert.certificate_id}")
        self.log.append(
            action="INTENT_CERTIFICATE_ISSUED",
            actor=actor,
            object_ids=[cert.certificate_id],
            new_versions={cert.certificate_id: int(cert.version)},
            reason_code=f"INTENT_{cert.verdict}",
            payload={"intent_certificate": cert.to_dict()},
        )
        self.intent_certificates[cert.certificate_id] = cert
        return cert

    def issue_correspondence_certificate(
        self, cert: FormalCorrespondenceCertificate, *, actor: dict[str, Any]
    ) -> FormalCorrespondenceCertificate:
        if cert.intent_certificate_id not in self.intent_certificates:
            raise GraphError("correspondence certificate references unknown intent certificate")
        if cert.certificate_id in self.correspondence_certificates:
            raise GraphError(f"duplicate correspondence certificate {cert.certificate_id}")
        self.log.append(
            action="FORMAL_CORRESPONDENCE_ISSUED",
            actor=actor,
            object_ids=[cert.certificate_id],
            new_versions={cert.certificate_id: int(cert.version)},
            reason_code=f"CORRESPONDENCE_{cert.verdict}",
            payload={"formal_correspondence_certificate": cert.to_dict()},
        )
        self.correspondence_certificates[cert.certificate_id] = cert
        return cert

    def bind_intent_certificate(
        self, claim_id: str, certificate_id: str, *, actor: dict[str, Any]
    ) -> Claim:
        """Bind an approved, exact-hash intent certificate to a claim.

        This is a versioned epistemic metadata transition.  It does not upgrade
        mathematical truth, and replay reconstructs the binding from the event.
        """
        claim = self._require_claim(claim_id)
        cert = self.intent_certificates.get(certificate_id)
        if cert is None or cert.verdict is not Verdict.APPROVED:
            raise GraphError("intent certificate is missing or not approved")
        if cert.informal_claim_hash != claim.canonical_hash:
            raise GraphError("intent certificate claim hash does not match the claim")
        current = claim.evidence_profile.intent_certificate_id
        if current == certificate_id:
            return claim
        if current is not None:
            raise GraphError("claim already has a different intent certificate")
        updated = copy.deepcopy(claim)
        updated.evidence_profile = replace(
            claim.evidence_profile, intent_certificate_id=certificate_id
        )
        updated.status_version = claim.status_version + 1
        self.log.append(
            action="CLAIM_INTENT_BOUND",
            actor=actor,
            object_ids=[claim_id, certificate_id],
            prior_versions={claim_id: claim.status_version},
            new_versions={claim_id: updated.status_version},
            input_hashes=[claim.canonical_hash],
            reason_code="APPROVED_INTENT_BOUND",
            payload={"claim": updated.to_dict()},
        )
        self.claims[claim_id] = updated
        return updated

    # ── claims ───────────────────────────────────────────────────────────────────

    def propose_claim(
        self,
        *,
        claim_id: str,
        interpretation_id: str,
        canonical_formula: str,
        informal_text: str = "",
        assumptions: Iterable[str] = (),
        dependencies: Iterable[str] = (),
        scope: str = "general",
        centrality: float = 0.0,
        semantic_risk: float = 0.0,
        actor: dict[str, Any],
    ) -> Claim:
        """Propose a claim. It always enters UNKNOWN with an empty profile."""
        if claim_id in self.claims:
            raise GraphError(f"duplicate claim {claim_id}")
        if interpretation_id not in self.interpretations:
            raise GraphError(f"claim {claim_id} references unknown interpretation {interpretation_id}")
        for dep in dependencies:
            if dep not in self.claims:
                raise GraphError(f"claim {claim_id} depends on unknown claim {dep}")
        claim = Claim(
            claim_id=claim_id,
            interpretation_id=interpretation_id,
            canonical_formula=canonical_formula,
            canonical_hash=sha256_hex(canonical_formula),
            informal_text=informal_text,
            assumptions=list(assumptions),
            dependencies=list(dependencies),
            scope=scope,
            centrality=centrality,
            semantic_risk=semantic_risk,
            truth_status=TruthStatus.UNKNOWN,
            evidence_profile=EvidenceProfile(),
            created_by=str(actor.get("id", "")),
            created_at=_now(),
            status_version=1,
        )
        self.log.append(
            action="CLAIM_PROPOSED",
            actor=actor,
            object_ids=[claim_id],
            new_versions={claim_id: 1},
            reason_code="PROPOSED_UNKNOWN",
            payload={"claim": claim.to_dict()},
        )
        self.claims[claim_id] = claim
        return claim

    def register_evidence(self, evidence: Evidence, *, actor: dict[str, Any]) -> Evidence:
        """Record raw evidence and link it to claims (does NOT change any tier)."""
        if evidence.evidence_id in self.evidence:
            raise GraphError(f"duplicate evidence {evidence.evidence_id}")
        if evidence.status_version != 1:
            raise GraphError("new evidence must start at version 1")
        for cid in evidence.claim_ids:
            if cid not in self.claims:
                raise GraphError(f"evidence references unknown claim {cid}")
        self.log.append(
            action="EVIDENCE_ATTACHED",
            actor=actor,
            object_ids=[evidence.evidence_id, *evidence.claim_ids],
            new_versions={evidence.evidence_id: evidence.status_version},
            output_hashes=list(evidence.artifact_hashes),
            reason_code=f"EVIDENCE_{str(evidence.kind).upper()}",
            payload={"evidence": evidence.to_dict()},
        )
        self.evidence[evidence.evidence_id] = evidence
        for cid in evidence.claim_ids:
            if evidence.evidence_id not in self.claims[cid].evidence_ids:
                self.claims[cid].evidence_ids.append(evidence.evidence_id)
        return evidence

    def apply_validated_admission(
        self,
        *,
        claim_id: str,
        new_profile: EvidenceProfile,
        truth_status: TruthStatus,
        validator_id: str,
        reason_code: str,
        actor: dict[str, Any],
        authority_token: object | None = None,
    ) -> Claim:
        """Change a claim's evidence tier/truth status. Only the router calls this."""
        self._require_truth_authority(authority_token)
        prior_claim = self._require_claim(claim_id)
        prior = prior_claim.status_version
        claim = copy.deepcopy(prior_claim)
        claim.evidence_profile = new_profile
        claim.truth_status = truth_status
        claim.status_version = prior + 1
        self.log.append(
            action="CLAIM_PROMOTED" if truth_status == TruthStatus.SUPPORTED else "CLAIM_CONFLICTED"
            if truth_status == TruthStatus.CONFLICTED
            else "ADJUDICATION_RECORDED",
            actor={**actor, "validator_id": validator_id},
            object_ids=[claim_id],
            prior_versions={claim_id: prior},
            new_versions={claim_id: claim.status_version},
            reason_code=reason_code,
            payload={"claim": claim.to_dict()},
        )
        self.claims[claim_id] = claim
        return claim

    def apply_invalidation(
        self,
        *,
        claim_id: str,
        new_profile: EvidenceProfile,
        truth_status: TruthStatus,
        reason_code: str,
        actor: dict[str, Any],
        lifecycle: Lifecycle | None = None,
        authority_token: object | None = None,
    ) -> Claim:
        """Downgrade/refute a claim during revocation. Only revocation calls this."""
        self._require_truth_authority(authority_token)
        prior_claim = self._require_claim(claim_id)
        prior = prior_claim.status_version
        claim = copy.deepcopy(prior_claim)
        claim.evidence_profile = new_profile
        claim.truth_status = truth_status
        if lifecycle is not None:
            claim.lifecycle_status = lifecycle
        claim.status_version = prior + 1
        action = (
            "CLAIM_REFUTED"
            if truth_status == TruthStatus.REFUTED
            else "CLAIM_CONFLICTED"
            if truth_status == TruthStatus.CONFLICTED
            else "CLAIM_REVOKED"
        )
        self.log.append(
            action=action,
            actor=actor,
            object_ids=[claim_id],
            prior_versions={claim_id: prior},
            new_versions={claim_id: claim.status_version},
            reason_code=reason_code,
            payload={"claim": claim.to_dict()},
        )
        self.claims[claim_id] = claim
        return claim

    def supersede_claim(self, *, old_claim_id: str, new_claim: Claim, actor: dict[str, Any]) -> Claim:
        """Create a superseding claim rather than rewriting the old one in place."""
        old = copy.deepcopy(self._require_claim(old_claim_id))
        new_claim = copy.deepcopy(new_claim)
        new_claim.supersedes = old_claim_id
        if new_claim.claim_id in self.claims:
            raise GraphError(f"duplicate claim {new_claim.claim_id}")
        old.lifecycle_status = Lifecycle.SUPERSEDED
        old.status_version += 1
        self.log.append(
            action="CLAIM_SUPERSEDED",
            actor=actor,
            object_ids=[old_claim_id, new_claim.claim_id],
            prior_versions={old_claim_id: old.status_version - 1},
            new_versions={old_claim_id: old.status_version, new_claim.claim_id: new_claim.status_version},
            reason_code="STATEMENT_REPLACED",
            payload={"old_claim": old.to_dict(), "new_claim": new_claim.to_dict()},
        )
        self.claims[old_claim_id] = old
        self.claims[new_claim.claim_id] = new_claim
        return new_claim

    # ── relations ────────────────────────────────────────────────────────────────

    def add_relation(self, relation: Relation, *, actor: dict[str, Any]) -> Relation:
        if relation.edge_id in self.relations:
            raise GraphError(f"duplicate relation {relation.edge_id}")
        if relation.status_version != 1:
            raise GraphError("new relation must start at version 1")
        self.log.append(
            action="RELATION_ADDED",
            actor=actor,
            object_ids=[relation.edge_id, relation.source_id, relation.target_id],
            new_versions={relation.edge_id: relation.status_version},
            reason_code=str(relation.relation_type),
            payload={"relation": relation.to_dict()},
        )
        self.relations[relation.edge_id] = relation
        return relation

    # ── branches ─────────────────────────────────────────────────────────────────

    def add_branch(self, branch: Branch, *, actor: dict[str, Any]) -> Branch:
        if branch.branch_id in self.branches:
            raise GraphError(f"duplicate branch {branch.branch_id}")
        if branch.status_version != 1:
            raise GraphError("new branch must start at version 1")
        self.log.append(
            action="BRANCH_OPENED", actor=actor, object_ids=[branch.branch_id],
            new_versions={branch.branch_id: branch.status_version},
            reason_code="BRANCH_PROPOSED",
            payload={"branch": branch.to_dict()},
        )
        self.branches[branch.branch_id] = branch
        return branch

    def set_branch_status(
        self, branch_id: str, status: str, *, reason: str, actor: dict[str, Any]
    ) -> Branch:
        current = self.branches.get(branch_id)
        if current is None:
            raise GraphError(f"unknown branch {branch_id}")
        branch = copy.deepcopy(current)
        prior = branch.status_version
        branch.status = status
        branch.status_version = prior + 1
        action = {
            "paused": "BRANCH_PAUSED",
            "active": "BRANCH_REOPENED",
            "killed": "BRANCH_KILLED",
            "closed": "BRANCH_CLOSED",
        }.get(status, "BRANCH_OPENED")
        if status == "paused":
            branch.pause_reason = reason
        self.log.append(
            action=action, actor=actor, object_ids=[branch_id], reason_code=reason,
            prior_versions={branch_id: prior}, new_versions={branch_id: branch.status_version},
            payload={"branch": branch.to_dict()},
        )
        self.branches[branch_id] = branch
        return branch

    # ── authoritative event replay ─────────────────────────────────────────────

    def _truth_authority_for_router(self) -> object:
        """Package-private capability used only by the evidence router.

        Strong evidence still requires an HMAC attestation.  This capability
        prevents accidental/public direct status mutation; process-level authority
        isolation remains a deployment boundary rather than a Python object claim.
        """

        return self.__truth_plane_token

    def _require_truth_authority(self, token: object | None) -> None:
        if token is not self.__truth_plane_token:
            raise GraphError("epistemic status may only be changed by the evidence router")

    def _replay_events(self) -> None:
        """Rebuild every semantic entity from signed event payloads.

        Event metadata alone is insufficient to be authoritative.  Every graph
        state transition therefore carries a canonical object snapshot, and
        replay validates optimistic versions before replacing a materialized view.
        """

        for event in self.log.events:
            payload = event.payload
            action = event.action
            if action == "PROBLEM_FROZEN":
                problem = _problem_from(payload, event)
                if problem.problem_id in self.problems:
                    raise GraphError(f"replay duplicate problem {problem.problem_id}")
                if event.new_versions.get(problem.problem_id) != problem.status_version:
                    raise GraphError("replay problem version mismatch")
                self.problems[problem.problem_id] = problem
            elif action == "INTERPRETATION_ADDED":
                interp = _interpretation_from(payload, event)
                if interp.parent_problem_id not in self.problems:
                    raise GraphError("replay interpretation references unknown problem")
                if event.new_versions.get(interp.interpretation_id) != interp.status_version:
                    raise GraphError("replay interpretation version mismatch")
                self.interpretations[interp.interpretation_id] = interp
                refs = self.problems[interp.parent_problem_id].interpretations
                if interp.interpretation_id not in refs:
                    refs.append(interp.interpretation_id)
            elif action == "INTENT_CERTIFICATE_ISSUED":
                intent_certificate = _intent_from(payload, event)
                if event.new_versions.get(intent_certificate.certificate_id) != int(
                    intent_certificate.version
                ):
                    raise GraphError("replay intent certificate version mismatch")
                self.intent_certificates[intent_certificate.certificate_id] = intent_certificate
            elif action == "FORMAL_CORRESPONDENCE_ISSUED":
                correspondence_certificate = _correspondence_from(payload, event)
                if correspondence_certificate.intent_certificate_id not in self.intent_certificates:
                    raise GraphError("replay correspondence references unknown intent certificate")
                if event.new_versions.get(correspondence_certificate.certificate_id) != int(
                    correspondence_certificate.version
                ):
                    raise GraphError("replay correspondence certificate version mismatch")
                self.correspondence_certificates[
                    correspondence_certificate.certificate_id
                ] = correspondence_certificate
            elif action == "CLAIM_PROPOSED":
                claim = _claim_from(payload, "claim", event)
                if claim.claim_id in self.claims:
                    raise GraphError(f"replay duplicate claim {claim.claim_id}")
                if claim.interpretation_id not in self.interpretations:
                    raise GraphError("replay claim references unknown interpretation")
                if any(dep not in self.claims for dep in claim.dependencies):
                    raise GraphError("replay claim references unknown dependency")
                if event.new_versions.get(claim.claim_id) != claim.status_version:
                    raise GraphError("replay proposed claim version mismatch")
                self.claims[claim.claim_id] = claim
            elif action == "EVIDENCE_ATTACHED":
                evidence = _evidence_from(payload, event)
                if evidence.evidence_id in self.evidence:
                    raise GraphError(f"replay duplicate evidence {evidence.evidence_id}")
                if any(cid not in self.claims for cid in evidence.claim_ids):
                    raise GraphError("replay evidence references unknown claim")
                if event.new_versions.get(evidence.evidence_id) != evidence.status_version:
                    raise GraphError("replay evidence version mismatch")
                self.evidence[evidence.evidence_id] = evidence
                for cid in evidence.claim_ids:
                    if evidence.evidence_id not in self.claims[cid].evidence_ids:
                        self.claims[cid].evidence_ids.append(evidence.evidence_id)
            elif action == "EVIDENCE_INVALIDATED":
                evidence = _evidence_from(payload, event)
                if evidence.evidence_id not in self.evidence:
                    raise GraphError("replay invalidates unknown evidence")
                prior_evidence = self.evidence[evidence.evidence_id]
                if event.prior_versions.get(evidence.evidence_id) != prior_evidence.status_version:
                    raise GraphError("replay prior evidence version mismatch")
                if event.new_versions.get(evidence.evidence_id) != evidence.status_version:
                    raise GraphError("replay new evidence version mismatch")
                self.evidence[evidence.evidence_id] = evidence
            elif action in {
                "CLAIM_PROMOTED", "CLAIM_REVOKED", "CLAIM_REFUTED",
                "CLAIM_CONFLICTED", "CLAIM_INTENT_BOUND", "ADJUDICATION_RECORDED",
            }:
                claim = _claim_from(payload, "claim", event)
                prior = self.claims.get(claim.claim_id)
                if prior is None:
                    raise GraphError("replay status event references unknown claim")
                if event.prior_versions.get(claim.claim_id) != prior.status_version:
                    raise GraphError("replay prior claim version mismatch")
                if event.new_versions.get(claim.claim_id) != claim.status_version:
                    raise GraphError("replay new claim version mismatch")
                if action == "CLAIM_INTENT_BOUND":
                    cert_id = claim.evidence_profile.intent_certificate_id
                    bound_intent_certificate = self.intent_certificates.get(cert_id or "")
                    if bound_intent_certificate is None \
                            or bound_intent_certificate.verdict is not Verdict.APPROVED \
                            or bound_intent_certificate.informal_claim_hash != claim.canonical_hash:
                        raise GraphError("replay intent binding is invalid")
                self.claims[claim.claim_id] = claim
            elif action == "CLAIM_SUPERSEDED":
                old = _claim_from(payload, "old_claim", event)
                new = _claim_from(payload, "new_claim", event)
                if old.claim_id not in self.claims or new.claim_id in self.claims:
                    raise GraphError("replay invalid supersession")
                if event.prior_versions.get(old.claim_id) != self.claims[old.claim_id].status_version:
                    raise GraphError("replay supersession prior version mismatch")
                if event.new_versions.get(old.claim_id) != old.status_version \
                        or event.new_versions.get(new.claim_id) != new.status_version:
                    raise GraphError("replay supersession new version mismatch")
                self.claims[old.claim_id] = old
                self.claims[new.claim_id] = new
            elif action == "RELATION_ADDED":
                relation = _relation_from(payload, event)
                if relation.edge_id in self.relations:
                    raise GraphError("replay duplicate relation")
                if event.new_versions.get(relation.edge_id) != relation.status_version:
                    raise GraphError("replay relation version mismatch")
                self.relations[relation.edge_id] = relation
            elif action in {
                "BRANCH_OPENED", "BRANCH_PAUSED", "BRANCH_REOPENED",
                "BRANCH_KILLED", "BRANCH_CLOSED",
            }:
                branch = _branch_from(payload, event)
                existing = self.branches.get(branch.branch_id)
                if existing is None:
                    if action != "BRANCH_OPENED" or event.new_versions.get(branch.branch_id) != 1:
                        raise GraphError("replay invalid branch creation")
                else:
                    if event.prior_versions.get(branch.branch_id) != existing.status_version:
                        raise GraphError("replay prior branch version mismatch")
                    if event.new_versions.get(branch.branch_id) != branch.status_version:
                        raise GraphError("replay new branch version mismatch")
                self.branches[branch.branch_id] = branch
            # Gate/checkpoint/rate-limit/human events have no graph entity view.

    # ── dependency traversal ───────────────────────────────────────────────────

    def _require_claim(self, claim_id: str) -> Claim:
        claim = self.claims.get(claim_id)
        if claim is None:
            raise GraphError(f"unknown claim {claim_id}")
        return claim

    def claims_supported_by(self, evidence_id: str) -> list[str]:
        return [c.claim_id for c in self.claims.values() if evidence_id in c.evidence_ids]

    def direct_dependents(self, claim_id: str) -> list[str]:
        """Claims that depend on (or are equivalent to) ``claim_id``."""
        out: list[str] = []
        for claim in self.claims.values():
            if claim_id in claim.dependencies or claim_id in claim.equivalent_to:
                out.append(claim.claim_id)
        # equivalence and mutual reduction edges are symmetric
        for rel in self.relations.values():
            if rel.lifecycle_status != Lifecycle.ACTIVE:
                continue
            if rel.target_id == claim_id and rel.relation_type.value in {"DEPENDS_ON", "IMPLIES"}:
                out.append(rel.source_id)
            if rel.relation_type.value == "EQUIVALENT_TO" and claim_id in (rel.source_id, rel.target_id):
                out.append(rel.target_id if rel.source_id == claim_id else rel.source_id)
        return [c for c in dict.fromkeys(out) if c in self.claims and c != claim_id]

    def dependency_edges(self) -> dict[str, set[str]]:
        """Adjacency of ``claim -> claims that depend on it`` (reverse dependency)."""
        edges: dict[str, set[str]] = {cid: set() for cid in self.claims}
        for cid in self.claims:
            for dependent in self.direct_dependents(cid):
                edges[cid].add(dependent)
        return edges

    def materialized_view(self) -> dict[str, Any]:
        """A disposable projection of the current state (spec §10.3)."""
        return {
            "event_count": len(self.log),
            "merkle_root": self.log.merkle_root(),
            "problems": {k: v.to_dict() for k, v in self.problems.items()},
            "interpretations": {k: v.to_dict() for k, v in self.interpretations.items()},
            "claims": {k: v.to_dict() for k, v in self.claims.items()},
            "branches": {k: v.to_dict() for k, v in self.branches.items()},
            "evidence": {k: v.to_dict() for k, v in self.evidence.items()},
            "relations": {k: v.to_dict() for k, v in self.relations.items()},
        }

    def view_hash(self) -> str:
        return content_id(self.materialized_view())


def _required(payload: dict[str, Any], key: str, event: Event) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise GraphError(f"event {event.sequence} {event.action} lacks {key!r} payload")
    return dict(value)


def _profile_from(doc: dict[str, Any]) -> EvidenceProfile:
    return EvidenceProfile(
        numerical=NumericalEvidence(doc.get("numerical", "NONE")),
        exact_computation=ExactComputation(doc.get("exact_computation", "NONE")),
        informal_review=InformalReview(doc.get("informal_review", "NONE")),
        formal_verification=FormalVerification(doc.get("formal_verification", "NONE")),
        external_import=ExternalImport(doc.get("external_import", "NONE")),
        intent_certificate_id=doc.get("intent_certificate_id"),
        formal_correspondence_certificate_id=doc.get("formal_correspondence_certificate_id"),
    )


def _problem_from(payload: dict[str, Any], event: Event) -> Problem:
    return Problem(**_required(payload, "problem", event))


def _interpretation_from(payload: dict[str, Any], event: Event) -> Interpretation:
    return Interpretation(**_required(payload, "interpretation", event))


def _claim_from(payload: dict[str, Any], key: str, event: Event) -> Claim:
    doc = _required(payload, key, event)
    doc["lifecycle_status"] = Lifecycle(doc.get("lifecycle_status", "ACTIVE"))
    doc["truth_status"] = TruthStatus(doc.get("truth_status", "UNKNOWN"))
    profile = doc.get("evidence_profile", {})
    if not isinstance(profile, dict):
        raise GraphError(f"event {event.sequence} claim has invalid evidence profile")
    doc["evidence_profile"] = _profile_from(profile)
    return Claim(**doc)


def _evidence_from(payload: dict[str, Any], event: Event) -> Evidence:
    doc = _required(payload, "evidence", event)
    doc["kind"] = EvidenceKind(doc["kind"])
    return Evidence(**doc)


def _relation_from(payload: dict[str, Any], event: Event) -> Relation:
    doc = _required(payload, "relation", event)
    doc["relation_type"] = RelationType(doc["relation_type"])
    doc["lifecycle_status"] = Lifecycle(doc.get("lifecycle_status", "ACTIVE"))
    profile = doc.get("evidence_profile", {})
    if not isinstance(profile, dict):
        raise GraphError(f"event {event.sequence} relation has invalid evidence profile")
    doc["evidence_profile"] = _profile_from(profile)
    return Relation(**doc)


def _branch_from(payload: dict[str, Any], event: Event) -> Branch:
    return Branch(**_required(payload, "branch", event))


def _intent_from(payload: dict[str, Any], event: Event) -> IntentCertificate:
    doc = _required(payload, "intent_certificate", event)
    doc["verdict"] = Verdict(doc.get("verdict", "UNRESOLVED"))
    return IntentCertificate(**doc)


def _correspondence_from(payload: dict[str, Any], event: Event) -> FormalCorrespondenceCertificate:
    doc = _required(payload, "formal_correspondence_certificate", event)
    doc["verdict"] = Verdict(doc.get("verdict", "UNRESOLVED"))
    return FormalCorrespondenceCertificate(**doc)
