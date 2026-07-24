"""Learning & memory stores (spec §6.11, §10.6).

Memory is separated into distinct stores that are *never conflated*: an audited
external theorem is a usable sourced import, not a locally-verified fact. Each
store has its own promotion rule and cross-problem policy from the §10.6 table.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from egmra.provenance.hashing import canonical_json, is_sha256

# The §10.6 memory table: (may_contain_false, cross_problem, promotion_rule).
MEMORY_TABLE = {
    "raw_scratch": (True, False, "never"),
    "problem_local_episodic": (True, "negative_or_search_hint_only", "expires_or_quarantined"),
    "mechanically_verified_semantic": (False, True, "kernel_or_certificate_replay_and_dependency_audit"),
    "audited_external_import": (True, "as_sourced_premise", "exact_source_audit_recheck_applicability"),
    "procedural_tactic": ("incomplete", "as_proposal_prior", "rechecked_on_each_exact_goal"),
    "negative_failure": ("falsified_scope_explicit", True, "counterexample_or_first_error_evidence"),
    "calibration_ledger": (False, True, "exact_pipeline_outcome_provenance"),
}


class MemoryError(RuntimeError):
    pass


@dataclass
class MemoryStore:
    name: str
    records: list[dict] = field(default_factory=list)
    admit_rule: Callable[[dict], bool] | None = None

    _PROTECTED = frozenset({
        "mechanically_verified_semantic", "audited_external_import",
        "negative_failure", "calibration_ledger",
    })

    def admit(self, record: dict) -> bool:
        if self.name in self._PROTECTED:
            return False
        return self._admit_validated(record)

    def _admit_validated(self, record: dict) -> bool:
        if not isinstance(record, dict):
            return False
        if self.admit_rule is not None and not self.admit_rule(record):
            return False
        try:
            import json
            frozen_copy = json.loads(canonical_json(record))
        except Exception:
            return False
        self.records.append(frozen_copy)
        return True

    def cross_problem_usable(self) -> object:
        return MEMORY_TABLE[self.name][1]


def _requires(keys: tuple[str, ...]) -> Callable[[dict], bool]:
    return lambda record: all(record.get(k) for k in keys)


@dataclass
class LongTermMemory:
    """The six persistent stores plus quarantined problem-local memory."""

    raw_scratch: MemoryStore = field(
        default_factory=lambda: MemoryStore("raw_scratch"))
    problem_local: MemoryStore = field(
        default_factory=lambda: MemoryStore("problem_local_episodic"))
    verified_semantic: MemoryStore = field(
        default_factory=lambda: MemoryStore(
            "mechanically_verified_semantic",
            admit_rule=_requires(("theorem_hash", "kernel_or_certificate_replay", "dependency_audit"))))
    external_import: MemoryStore = field(
        default_factory=lambda: MemoryStore(
            "audited_external_import",
            admit_rule=_requires(("verbatim_extract", "source_version", "applicability_rechecked"))))
    procedural: MemoryStore = field(
        default_factory=lambda: MemoryStore("procedural_tactic"))
    negative: MemoryStore = field(
        default_factory=lambda: MemoryStore(
            "negative_failure", admit_rule=_requires(("falsified_scope", "first_error_evidence"))))
    calibration: MemoryStore = field(
        default_factory=lambda: MemoryStore(
            "calibration_ledger",
            admit_rule=_requires(("authenticated", "pipeline_fingerprint", "outcome_provenance"))))

    def promote_verified_fact(
        self, record: dict, *, truth_snapshot=None, event_log=None, gates=None,
    ) -> bool:
        """Admit only a current truth snapshot bound to signed release gates.

        Caller booleans such as ``kernel_or_certificate_replay=True`` are never
        an authority.  The truth and gate services must authenticate the exact
        claim/event head before cross-problem semantic memory is updated.
        """
        if truth_snapshot is None or event_log is None or gates is None:
            return False
        try:
            claim_id = record.get("claim_id", "")
            theorem_hash = record.get("theorem_hash", "")
            if not truth_snapshot.verify(
                event_log=event_log, expected_claim_id=claim_id
            ):
                return False
            if truth_snapshot.truth_status != "SUPPORTED":
                return False
            if not is_sha256(theorem_hash) or theorem_hash != truth_snapshot.canonical_hash:
                return False
            if not gates.verify_attestation(event_log=event_log) \
                    or gates.evidence_hash != truth_snapshot.snapshot_digest:
                return False
            if gates.truth not in {"T2", "T3", "T4", "T5"} \
                    or gates.intent != "I2" or gates.reproducibility != "R2":
                return False
        except (AttributeError, TypeError, ValueError):
            return False
        authenticated = dict(record)
        authenticated["truth_snapshot_digest"] = truth_snapshot.snapshot_digest
        authenticated["gate_digest"] = gates.gate_digest
        authenticated["authenticated"] = True
        return self.verified_semantic._admit_validated(authenticated)

    def promote_external_import(self, record: dict) -> bool:
        """An audited import is a *sourced premise*, never a locally-verified fact."""
        return self.external_import._admit_validated(record)

    def record_negative(self, record: dict) -> bool:
        return self.negative._admit_validated(record)

    def stores(self) -> dict[str, MemoryStore]:
        return {
            "raw_scratch": self.raw_scratch,
            "problem_local_episodic": self.problem_local,
            "mechanically_verified_semantic": self.verified_semantic,
            "audited_external_import": self.external_import,
            "procedural_tactic": self.procedural,
            "negative_failure": self.negative,
            "calibration_ledger": self.calibration,
        }

    def revalidate_on_toolchain_change(self) -> list[str]:
        """A toolchain/source correction triggers revalidation, not blind reuse."""
        # Verified-semantic and external-import facts must be rechecked.
        return ["mechanically_verified_semantic", "audited_external_import"]
