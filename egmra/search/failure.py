"""Failure compression + kill/pause discipline (spec §7.6).

A failed branch produces a *structured certificate*. "The model could not finish"
is not a mathematical failure certificate — resource exhaustion is censored. A
branch is killed only by a valid counterexample, logical impossibility, a
dominated identical state, or a policy constraint. Otherwise it is paused.
"""

from __future__ import annotations

from dataclasses import dataclass

from egmra.provenance.hashing import content_id

# Only these reasons may KILL a branch (spec §7.6).
KILL_REASONS = frozenset({"valid_counterexample", "logical_impossibility",
                          "dominated_identical_state", "policy_constraint"})
# Everything else -> pause (censored operational data).
CENSORED_REASONS = frozenset({"resource_exhaustion", "timeout", "rate_limit",
                              "model_incomplete", "budget_exhausted"})


@dataclass(frozen=True)
class FailureCertificate:
    branch_id: str
    mechanism_fingerprint: str
    exact_failed_obligation: str
    first_invalid_claim: str
    evidence: str
    counterexample: str
    attempted_actions: tuple[str, ...]
    compute_spent: dict
    what_was_learned: str
    scope_of_failure: str
    reopen_condition: str
    related_branches: tuple[str, ...] = ()

    def certificate_hash(self) -> str:
        return content_id({
            "branch": self.branch_id, "obligation": self.exact_failed_obligation,
            "first_invalid": self.first_invalid_claim, "scope": self.scope_of_failure,
        })


def disposition(reason: str) -> str:
    """Return 'kill', 'pause', or raise for an unknown reason."""
    if reason in KILL_REASONS:
        return "kill"
    if reason in CENSORED_REASONS:
        return "pause"
    raise ValueError(f"unknown failure reason {reason!r}")


def is_censored(reason: str) -> bool:
    return reason in CENSORED_REASONS


def make_failure_certificate(
    *, branch_id: str, mechanism_fingerprint: str, reason: str,
    exact_failed_obligation: str = "", first_invalid_claim: str = "",
    evidence: str = "", counterexample: str = "", attempted_actions: tuple[str, ...] = (),
    compute_spent: dict | None = None, what_was_learned: str = "", scope_of_failure: str = "",
    reopen_condition: str = "", related_branches: tuple[str, ...] = (),
) -> FailureCertificate:
    if reason in CENSORED_REASONS and not reopen_condition:
        reopen_condition = "resources available again"
    return FailureCertificate(
        branch_id=branch_id,
        mechanism_fingerprint=mechanism_fingerprint,
        exact_failed_obligation=exact_failed_obligation,
        first_invalid_claim=first_invalid_claim,
        evidence=evidence,
        counterexample=counterexample,
        attempted_actions=attempted_actions,
        compute_spent=dict(compute_spent or {}),
        what_was_learned=what_was_learned or (
            "resource exhaustion (censored); not a mathematical failure"
            if reason in CENSORED_REASONS else ""),
        scope_of_failure=scope_of_failure,
        reopen_condition=reopen_condition,
        related_branches=related_branches,
    )
