"""M0 safety & provenance layer (spec §13.2, §16 P0).

Reusable safety functions that make the *existing* pipeline honest and replayable:

* ``PromotionGuard`` enforces the signed feature policy at a promotion entry point.
* ``evidence_precedence`` encodes the truth/intent/novelty/significance precedence:
  a clean kernel proof of the exact locked proposition cannot be overruled by a
  model referee, but intent/applicability/novelty/significance review can still
  block *release*, and a checked same-scope counterexample creates ``CONFLICTED``.
* ``quarantine_legacy_manifests`` quarantines identity-incomplete legacy manifests
  (including 601/661/724/782/849) instead of treating them as migrated evidence.
* ``PromotionTelemetry`` records the cost/call/rate-limit/cache/disposition data
  needed for an equal-cost baseline comparison.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from egmra.policy import PolicyEnforcer, PolicyViolation

# The identity-incomplete legacy manifests named in the spec (§4.1, §13.2, §16 P0.9).
LEGACY_QUARANTINE_PROBLEMS = (601, 661, 724, 782, 849)

# Fields that make a manifest's execution identity complete.
_REQUIRED_IDENTITY_FIELDS = (
    "run_contract", "execution_id", "run_contract_id", "run_context_id",
)


@dataclass
class PromotionGuard:
    """Enforce the signed feature policy at a promotion entry point."""

    enforcer: PolicyEnforcer
    entry_point: str = "promotion"

    def check(self, *, formal: bool) -> tuple[bool, str]:
        try:
            self.enforcer.require("promotion", entry_point=self.entry_point)
            if formal:
                self.enforcer.require("formal_promotion", entry_point=self.entry_point)
        except PolicyViolation as exc:
            return False, str(exc)
        return True, "promotion enabled by signed policy"


@dataclass(frozen=True)
class PrecedenceDecision:
    truth_status: str          # SUPPORTED | CONFLICTED | UNKNOWN
    release_blocked: bool
    reasons: tuple[str, ...]


def evidence_precedence(
    *,
    clean_kernel_proof: bool,
    model_referee_blocks_truth: bool,
    checked_same_scope_counterexample: bool,
    intent_blocks: bool = False,
    novelty_blocks: bool = False,
    significance_blocks: bool = False,
) -> PrecedenceDecision:
    """The explicit evidence-precedence policy (spec §13.2 item 7, §16 P0.8)."""
    reasons: list[str] = []

    # Incompatible hard evidence -> CONFLICTED, blocks every dependent promotion.
    if clean_kernel_proof and checked_same_scope_counterexample:
        return PrecedenceDecision("CONFLICTED", True,
                                  ("kernel proof and checked same-scope counterexample conflict; "
                                   "audit encoding/axioms/TCB",))
    if checked_same_scope_counterexample and not clean_kernel_proof:
        return PrecedenceDecision("UNKNOWN", True, ("checked counterexample refutes the claim",))

    truth = "UNKNOWN"
    if clean_kernel_proof:
        truth = "SUPPORTED"
        if model_referee_blocks_truth:
            # A model referee cannot overrule a clean kernel proof of the exact
            # locked proposition; it may only block on non-truth axes.
            reasons.append("model referee cannot overrule a clean kernel proof (truth stands)")

    # Non-truth gates can still block *release* even with a valid proof.
    release_blocked = intent_blocks or novelty_blocks or significance_blocks or truth != "SUPPORTED"
    if intent_blocks:
        reasons.append("intent/interpretation fidelity unresolved")
    if novelty_blocks:
        reasons.append("novelty unresolved")
    if significance_blocks:
        reasons.append("significance unresolved")
    return PrecedenceDecision(truth, release_blocked, tuple(reasons))


@dataclass(frozen=True)
class QuarantineRecord:
    manifest_path: str
    problem_number: int | None
    identity_complete: bool
    missing_fields: tuple[str, ...]
    quarantined: bool
    reason: str


def is_identity_incomplete(manifest: dict) -> tuple[bool, tuple[str, ...]]:
    """A manifest is identity-incomplete if any required identity field is null/absent."""
    missing = tuple(
        f for f in _REQUIRED_IDENTITY_FIELDS
        if manifest.get(f) in (None, "", {}, [])
    )
    return bool(missing), missing


def quarantine_manifest(manifest_path: Path | str) -> QuarantineRecord:
    path = Path(manifest_path)
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return QuarantineRecord(str(path), None, False, ("unreadable",), True, f"unreadable: {exc}")
    problem_number = manifest.get("problem_number")
    incomplete, missing = is_identity_incomplete(manifest)
    forced = problem_number in LEGACY_QUARANTINE_PROBLEMS
    quarantined = incomplete or forced
    reason = ("named legacy quarantine problem" if forced
              else f"missing identity fields: {list(missing)}" if incomplete
              else "identity complete")
    return QuarantineRecord(str(path), problem_number, not incomplete, missing, quarantined, reason)


def quarantine_legacy_manifests(manifest_paths: list[Path | str]) -> list[QuarantineRecord]:
    """Quarantine identity-incomplete legacy manifests rather than migrating them."""
    return [quarantine_manifest(p) for p in manifest_paths]


@dataclass
class PromotionTelemetry:
    """Cost/call/rate-limit/cache/disposition telemetry for baseline comparison."""

    tokens: int = 0
    calls: int = 0
    wall_seconds: float = 0.0
    rate_limit_pauses: int = 0
    deterministic_compute_seconds: float = 0.0
    reviewer_seconds: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    terminal_disposition: str = "unknown"
    interventions: int = 0

    def record(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"unknown telemetry field {key!r}")
            current = getattr(self, key)
            if isinstance(current, str):
                setattr(self, key, value)
            else:
                setattr(self, key, current + value)

    def report(self) -> dict:
        return dict(self.__dict__)
