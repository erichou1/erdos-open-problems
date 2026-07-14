"""Failure recovery table (spec §14.5) and compute-congestion pricing (§14.6).

Each failure has an automatic response and a precise *truth effect*. A rate limit
or timeout has no truth effect (censored); a false lemma triggers transactional
revocation; verification backlog is priced, never a truth downgrade.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryRule:
    failure: str
    automatic_response: str
    truth_effect: str


RECOVERY_TABLE: dict[str, RecoveryRule] = {
    r.failure: r for r in [
        RecoveryRule("rate_limit_quota",
                     "honor Retry-After, jittered backoff <=120s, pause lease, reroute if allowed",
                     "none; censored operational event"),
        RecoveryRule("timeout_process_crash",
                     "checkpoint, expire/transfer lease, resume compatible stage",
                     "none unless artifact incomplete"),
        RecoveryRule("malformed_model_output",
                     "schema repair/retry; preserve raw output; bounded attempts",
                     "no claim admitted"),
        RecoveryRule("source_unavailable_conflict",
                     "cache known version, mark provenance gap, alternate source/human task",
                     "novelty/import remains unresolved"),
        RecoveryRule("wrong_interpretation",
                     "create/reselect lattice node; revoke dependent correspondence",
                     "dependent claims downgraded"),
        RecoveryRule("false_lemma",
                     "attach counterexample, transactionally revoke closure, reopen alternatives",
                     "explicit graph update"),
        RecoveryRule("lean_statement_mismatch",
                     "reject certificate for intended target, repair target candidates",
                     "formal proof remains only for old encoded theorem"),
        RecoveryRule("formal_library_gap",
                     "create scoped local-library project and estimate cost",
                     "branch paused/redirected"),
        RecoveryRule("computation_mismatch",
                     "quarantine artifact, independent reimplementation, revoke dependents",
                     "relevant evidence removed"),
        RecoveryRule("evaluator_reward_hack",
                     "invalidate fitness run, strengthen multi-objective checker, replay population",
                     "no winner admitted"),
        RecoveryRule("model_provider_version_drift",
                     "new run contract, invalidate incompatible caches, re-benchmark",
                     "old verified artifacts remain versioned"),
        RecoveryRule("verification_backlog",
                     "congestion price, throttle generators, reserve verifier workers",
                     "no truth downgrade"),
        RecoveryRule("repeated_stagnation",
                     "retrieve targeted sources, counterfactual variants, new method family, escalate",
                     "branch paused, not falsely killed"),
    ]
}


def recovery_for(failure: str) -> RecoveryRule:
    if failure not in RECOVERY_TABLE:
        raise KeyError(f"unknown failure {failure!r}")
    return RECOVERY_TABLE[failure]


def truth_effect(failure: str) -> str:
    return recovery_for(failure).truth_effect
