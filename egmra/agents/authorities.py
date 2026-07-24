"""Seven durable authorities (spec §6.5, §4.3 item 1).

Twenty-two standing roles are architecture theater unless dispatch is conditional.
EGMRA consolidates them into seven durable authorities with distinct objectives,
information boundaries, required outputs, and forbidden actions. Specialist workers
are instantiated only when a branch requires their distinct tool/prior/information.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import hmac
import math
import os
import secrets
import time
from typing import Callable

from egmra.provenance.hashing import canonical_json


class AuthorityError(PermissionError):
    """An authority credential or attempted action is invalid."""


@dataclass(frozen=True)
class Authority:
    name: str
    objective: str
    information_boundary: str
    required_output: str
    forbidden: tuple[str, ...]


AUTHORITIES: dict[str, Authority] = {
    "research_governor": Authority(
        "research_governor",
        "maximize verified progress under budget",
        "sees branch posteriors/costs/leases; cannot change truth status",
        "branch decisions, budgets, rationale, stop/reopen triggers",
        ("change_claim_evidence", "interpret_timeout_as_math_failure",
         "publish_theorem", "use_self_reported_confidence_as_truth"),
    ),
    "intake_retrieval": Authority(
        "intake_retrieval",
        "establish target/status/source packet",
        "full sources; cannot write a candidate proof into truth",
        "contracts, theorem records, uncertainty and novelty reports",
        ("admit_candidate_proof_as_truth",),
    ),
    "program_worker": Authority(
        "program_worker",
        "pursue one declared mechanism with specific tools/priors",
        "sees only the relevant graph slice",
        "branch capsule updates, claim proposals, falsifiers, next experiments",
        ("import_uncited_theorems", "silently_strengthen_assumptions", "label_evidence"),
    ),
    "computational_falsifier": Authority(
        "computational_falsifier",
        "seek counterexamples and exact finite evidence",
        "initially withheld from the candidate proof",
        "immutable jobs, witnesses/certificates, coverage statements",
        ("assume_target_true",),
    ),
    "formalization_authority": Authority(
        "formalization_authority",
        "create/audit Lean targets and close exact goals",
        "sees locked target + goal states; cannot decide novelty",
        "formal declarations, proof states, build/axiom reports",
        ("decide_novelty", "treat_vendor_status_as_correspondence"),
    ),
    "adversarial_referee": Authority(
        "adversarial_referee",
        "find a valid defect or complete a documented checklist/replay",
        "no generator scratchpad; fresh context + different family for high value",
        "defect graph, independent recalculation, verification profile",
        ("earn_reward_for_agreement", "repair_proof_in_same_pass",
         "report_to_research_governor"),
    ),
    "release_auditor": Authority(
        "release_auditor",
        "decide the five release gates from evidence",
        "sees certificates; cannot generate repair text in the same pass",
        "signed intent/truth/novelty/significance/replay certificates",
        ("substitute_one_positive_verdict_for_another", "generate_repair_same_pass"),
    ),
}


def authority(name: str) -> Authority:
    if name not in AUTHORITIES:
        raise KeyError(f"unknown authority {name!r}; expected one of {sorted(AUTHORITIES)}")
    return AUTHORITIES[name]


def is_forbidden(name: str, action: str) -> bool:
    return action in authority(name).forbidden


# This allowlist, rather than prompt text, is the enforceable action boundary.
AUTHORITY_PERMISSIONS: dict[str, frozenset[str]] = {
    "research_governor": frozenset({
        "read_control_state", "open_branch", "pause_branch", "reopen_branch",
        "merge_branch", "allocate_budget", "dispatch_worker",
    }),
    "intake_retrieval": frozenset({
        "read_source", "write_contract", "write_source_packet", "read_branch_slice",
        "write_proposal", "read_own_proposals",
    }),
    "program_worker": frozenset({
        "read_branch_slice", "write_proposal", "read_own_proposals", "invoke_scoped_tool",
    }),
    "computational_falsifier": frozenset({
        "read_branch_slice", "write_proposal", "read_own_proposals", "invoke_compute",
    }),
    "formalization_authority": frozenset({
        "read_branch_slice", "write_proposal", "read_own_proposals", "invoke_lean",
    }),
    "adversarial_referee": frozenset({
        "read_locked_candidate", "read_branch_slice", "write_proposal",
        "read_own_proposals", "issue_referee_report",
    }),
    "release_auditor": frozenset({
        "read_certificates", "issue_gate_verdict", "issue_release",
    }),
}


@dataclass(frozen=True)
class AuthorityToken:
    authority_name: str
    subject: str
    lineage: str
    permissions: tuple[str, ...]
    resources: tuple[str, ...]
    issued_at: float
    expires_at: float
    nonce: str
    key_id: str
    signature: str = ""

    def signing_record(self) -> dict:
        return {
            "authority_name": self.authority_name,
            "subject": self.subject,
            "lineage": self.lineage,
            "permissions": list(self.permissions),
            "resources": list(self.resources),
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "nonce": self.nonce,
            "key_id": self.key_id,
        }


class AuthorityTokenIssuer:
    """Issue and verify short-lived, resource-scoped authority capabilities.

    Model workers receive tokens, never the HMAC key.  Keeping the signer in the
    same Python process is suitable only for local M1; a scaled deployment must
    isolate this service and its key from worker containers.
    """

    def __init__(
        self,
        *,
        env: dict[str, str] | None = None,
        now_fn: Callable[[], float] = time.time,
    ):
        source = os.environ if env is None else env
        key = source.get("EGMRA_AUTHORITY_KEY", "")
        if len(key.encode("utf-8")) < 32:
            raise AuthorityError("EGMRA_AUTHORITY_KEY must contain at least 32 bytes")
        self._key = key.encode("utf-8")
        self.key_id = hashlib.sha256(self._key).hexdigest()[:16]
        self.now_fn = now_fn

    def _now(self) -> float:
        now = float(self.now_fn())
        if not math.isfinite(now):
            raise AuthorityError("authority clock returned a non-finite timestamp")
        return now

    def _signature(self, token: AuthorityToken) -> str:
        return hmac.new(
            self._key,
            canonical_json(token.signing_record()).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def issue(
        self, *, authority_name: str, subject: str, resources: tuple[str, ...],
        permissions: tuple[str, ...] | None = None, lineage: str = "", ttl_seconds: float = 300,
    ) -> AuthorityToken:
        authority(authority_name)
        if not isinstance(subject, str) or not subject.strip():
            raise AuthorityError("token subject must be a non-empty string")
        if not resources or any(not isinstance(item, str) or not item for item in resources):
            raise AuthorityError("authority token requires non-empty resource scopes")
        if not math.isfinite(float(ttl_seconds)) or not 0 < ttl_seconds <= 3600:
            raise AuthorityError("authority token TTL must be in (0, 3600] seconds")
        requested = set(permissions or AUTHORITY_PERMISSIONS[authority_name])
        disallowed = requested - AUTHORITY_PERMISSIONS[authority_name]
        if disallowed:
            raise AuthorityError(
                f"permissions not allowed for {authority_name}: {sorted(disallowed)}"
            )
        now = self._now()
        unsigned = AuthorityToken(
            authority_name=authority_name,
            subject=subject,
            lineage=lineage,
            permissions=tuple(sorted(requested)),
            resources=tuple(sorted(set(resources))),
            issued_at=now,
            expires_at=now + float(ttl_seconds),
            nonce=secrets.token_hex(16),
            key_id=self.key_id,
        )
        return replace(unsigned, signature=self._signature(unsigned))

    def verify(
        self, token: AuthorityToken, *, action: str, resource: str | None = None,
    ) -> AuthorityToken:
        if not isinstance(token, AuthorityToken):
            raise AuthorityError("missing or malformed authority token")
        if token.key_id != self.key_id or not hmac.compare_digest(
            token.signature, self._signature(replace(token, signature=""))
        ):
            raise AuthorityError("authority token signature is invalid")
        now = self._now()
        if token.issued_at > now + 5:
            raise AuthorityError("authority token was issued in the future")
        if now >= token.expires_at:
            raise AuthorityError("authority token has expired")
        allowed = AUTHORITY_PERMISSIONS.get(token.authority_name, frozenset())
        if action not in token.permissions or action not in allowed:
            raise AuthorityError(
                f"action {action!r} is not allowed for {token.authority_name}"
            )
        if resource is not None and resource not in token.resources and "*" not in token.resources:
            raise AuthorityError(f"token is not scoped to resource {resource!r}")
        return token

    def require_independent(
        self, token: AuthorityToken, *, generator_subjects: set[str],
        generator_lineages: set[str],
    ) -> None:
        """Reject self-approval and same-lineage review credentials."""
        action = (
            "issue_referee_report" if token.authority_name == "adversarial_referee"
            else "issue_gate_verdict"
        )
        self.verify(token, action=action)
        if token.subject in generator_subjects:
            raise AuthorityError("self-approval is forbidden")
        if token.lineage and token.lineage in generator_lineages:
            raise AuthorityError("same-lineage review is not independent")
