"""Integrity-bound checkpoint and compatible resume decisions (spec §10.4).

This local M1 representation is deliberately *not* a durable checkpoint store.
It does, however, make the in-memory boundary fail closed: checkpoint state is
deeply immutable, content-addressed, and HMAC-authenticated; the recorded event
prefix is verified; and a cached stage is reusable only when the caller supplies
its current exact compatibility fingerprint.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import hashlib
import hmac
import math
import os
from types import MappingProxyType
from typing import Any

from egmra.provenance.hashing import content_id, is_sha256, merkle_root, sha256_hex
from egmra.truth.events import EventLog


_SCHEMA_VERSION = 1
_MIN_KEY_BYTES = 32
_GENESIS_EVENT_ID = sha256_hex("egmra-genesis")
_CACHE_RECORD_FIELDS = frozenset(
    {
        "artifact_hash",
        "compatibility_fingerprint",
        "replay_policy_hash",
        "durable_stage",
    }
)
_RATE_LIMIT_FIELDS = frozenset(
    {
        "blocked_until",
        "quota_remaining",
        "quota_limit",
        "quota_reset_at",
        "retry_after_seconds",
        "metadata_hash",
    }
)


class CheckpointError(ValueError):
    """Checkpoint state or resume input is malformed or incompatible."""


def _checkpoint_key(env: Mapping[str, str] | None = None) -> bytes:
    source = os.environ if env is None else env
    raw = source.get("EGMRA_CHECKPOINT_KEY", "")
    key = raw.encode("utf-8")
    if len(key) < _MIN_KEY_BYTES:
        raise CheckpointError(
            f"EGMRA_CHECKPOINT_KEY must contain at least {_MIN_KEY_BYTES} bytes"
        )
    return key


def _require_nonempty_string(value: object, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CheckpointError(f"{field_name} must be a non-empty string")
    return value


def _require_digest(value: object, *, field_name: str, allow_empty: bool = False) -> str:
    if allow_empty and value == "":
        return ""
    if not is_sha256(value):
        raise CheckpointError(f"{field_name} must be a lowercase SHA-256 digest")
    return value


def _finite_number(value: object, *, field_name: str, nonnegative: bool) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CheckpointError(f"{field_name} must be a finite number")
    if not math.isfinite(value):
        raise CheckpointError(f"{field_name} must be finite")
    if nonnegative and value < 0:
        raise CheckpointError(f"{field_name} must be non-negative")
    return value


def _freeze_json(value: Any, *, field_name: str) -> Any:
    """Validate and detach JSON-like state, returning immutable containers."""
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CheckpointError(f"{field_name} contains a non-finite float")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise CheckpointError(f"{field_name} contains an invalid object key")
            frozen[key] = _freeze_json(item, field_name=f"{field_name}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_json(item, field_name=f"{field_name}[{index}]")
            for index, item in enumerate(value)
        )
    raise CheckpointError(
        f"{field_name} contains unsupported type {type(value).__name__}"
    )


def _freeze_mapping(value: object, *, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CheckpointError(f"{field_name} must be a mapping")
    frozen = _freeze_json(value, field_name=field_name)
    if not isinstance(frozen, Mapping):
        raise CheckpointError(f"{field_name} did not freeze to a mapping")
    return frozen


def _validate_digest_tuple(value: object, *, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise CheckpointError(f"{field_name} must be an immutable tuple")
    for index, digest in enumerate(value):
        _require_digest(digest, field_name=f"{field_name}[{index}]")
    if len(set(value)) != len(value):
        raise CheckpointError(f"{field_name} cannot contain duplicates")
    return value


def _validate_leases(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise CheckpointError("active_leases must be an immutable tuple")
    for index, lease_id in enumerate(value):
        _require_nonempty_string(lease_id, field_name=f"active_leases[{index}]")
    if len(set(value)) != len(value):
        raise CheckpointError("active_leases cannot contain duplicates")
    return value


def _validate_in_flight_calls(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise CheckpointError("in_flight_calls must be an immutable tuple")
    for index, call_id in enumerate(value):
        _require_nonempty_string(call_id, field_name=f"in_flight_calls[{index}]")
    if len(set(value)) != len(value):
        raise CheckpointError("in_flight_calls cannot contain duplicates")
    return value


def _validate_budgets(value: object) -> Mapping[str, int | float]:
    mapping = _freeze_mapping(value, field_name="budgets")
    for name, amount in mapping.items():
        _finite_number(amount, field_name=f"budgets.{name}", nonnegative=True)
    return mapping


def _validate_seeds(value: object) -> Mapping[str, int]:
    mapping = _freeze_mapping(value, field_name="seeds")
    for name, seed in mapping.items():
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise CheckpointError(f"seeds.{name} must be a non-negative integer")
    return mapping


def _validate_stage_caches(value: object) -> Mapping[str, Mapping[str, Any]]:
    mapping = _freeze_mapping(value, field_name="stage_caches")
    for stage, record in mapping.items():
        _require_nonempty_string(stage, field_name="stage cache name")
        if not isinstance(record, Mapping):
            raise CheckpointError(f"stage_caches.{stage} must be a cache record")
        if set(record) != _CACHE_RECORD_FIELDS:
            raise CheckpointError(
                f"stage_caches.{stage} must contain exactly "
                f"{sorted(_CACHE_RECORD_FIELDS)!r}"
            )
        for digest_field in (
            "artifact_hash",
            "compatibility_fingerprint",
            "replay_policy_hash",
        ):
            _require_digest(
                record[digest_field],
                field_name=f"stage_caches.{stage}.{digest_field}",
            )
        durable_stage = record["durable_stage"]
        if (
            isinstance(durable_stage, bool)
            or not isinstance(durable_stage, int)
            or durable_stage < 0
        ):
            raise CheckpointError(
                f"stage_caches.{stage}.durable_stage must be a non-negative integer"
            )
    return mapping  # type: ignore[return-value]


def _validate_rate_limit_state(value: object) -> Mapping[str, Mapping[str, Any]]:
    mapping = _freeze_mapping(value, field_name="rate_limit_state")
    for provider, state in mapping.items():
        _require_nonempty_string(provider, field_name="rate-limit provider")
        if not isinstance(state, Mapping):
            raise CheckpointError(f"rate_limit_state.{provider} must be a state record")
        unknown = set(state) - _RATE_LIMIT_FIELDS
        if unknown:
            raise CheckpointError(
                f"rate_limit_state.{provider} has unknown fields {sorted(unknown)!r}"
            )
        for field_name, item in state.items():
            if field_name == "metadata_hash":
                _require_digest(
                    item, field_name=f"rate_limit_state.{provider}.metadata_hash"
                )
            elif item is not None:
                _finite_number(
                    item,
                    field_name=f"rate_limit_state.{provider}.{field_name}",
                    nonnegative=True,
                )
    return mapping  # type: ignore[return-value]


@dataclass(frozen=True)
class Checkpoint:
    run_id: str
    last_sequence: int
    last_event_id: str
    merkle_root: str
    problem_contract_hash: str
    interpretation_hashes: tuple[str, ...]
    graph_view_hash: str
    controller_posteriors: Mapping[str, Any]
    budgets: Mapping[str, int | float]
    seeds: Mapping[str, int]
    active_leases: tuple[str, ...]
    behavior_closure_fingerprint: str
    stage_caches: Mapping[str, Mapping[str, Any]]
    rate_limit_state: Mapping[str, Mapping[str, Any]]
    in_flight_calls: tuple[str, ...] = ()
    schema_version: int = _SCHEMA_VERSION
    _sealed_hash: str = field(default="", repr=False)
    _signature: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        _require_nonempty_string(self.run_id, field_name="run_id")
        if (
            isinstance(self.last_sequence, bool)
            or not isinstance(self.last_sequence, int)
            or self.last_sequence < -1
        ):
            raise CheckpointError("last_sequence must be an integer greater than or equal to -1")
        _require_digest(self.last_event_id, field_name="last_event_id")
        _require_digest(self.merkle_root, field_name="merkle_root")
        _require_digest(self.problem_contract_hash, field_name="problem_contract_hash")
        _validate_digest_tuple(
            self.interpretation_hashes, field_name="interpretation_hashes"
        )
        _require_digest(self.graph_view_hash, field_name="graph_view_hash")
        _require_digest(
            self.behavior_closure_fingerprint,
            field_name="behavior_closure_fingerprint",
        )
        if self.schema_version != _SCHEMA_VERSION or isinstance(self.schema_version, bool):
            raise CheckpointError(
                f"unsupported checkpoint schema version {self.schema_version!r}"
            )
        if self.last_sequence == -1 and self.last_event_id != _GENESIS_EVENT_ID:
            raise CheckpointError("an empty checkpoint must name the genesis event")

        object.__setattr__(
            self,
            "controller_posteriors",
            _freeze_mapping(self.controller_posteriors, field_name="controller_posteriors"),
        )
        object.__setattr__(self, "budgets", _validate_budgets(self.budgets))
        object.__setattr__(self, "seeds", _validate_seeds(self.seeds))
        object.__setattr__(self, "active_leases", _validate_leases(self.active_leases))
        object.__setattr__(
            self, "in_flight_calls", _validate_in_flight_calls(self.in_flight_calls)
        )
        object.__setattr__(self, "stage_caches", _validate_stage_caches(self.stage_caches))
        object.__setattr__(
            self,
            "rate_limit_state",
            _validate_rate_limit_state(self.rate_limit_state),
        )

        computed = self._compute_hash()
        if self._sealed_hash:
            _require_digest(self._sealed_hash, field_name="_sealed_hash")
            if self._sealed_hash != computed:
                raise CheckpointError("checkpoint content does not match its sealed hash")
        else:
            object.__setattr__(self, "_sealed_hash", computed)
        if self._signature:
            _require_digest(self._signature, field_name="_signature")

    def _content_record(self) -> dict[str, Any]:
        """All semantic state committed by the checkpoint's content identity."""
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "last_sequence": self.last_sequence,
            "last_event_id": self.last_event_id,
            "merkle_root": self.merkle_root,
            "problem_contract_hash": self.problem_contract_hash,
            "interpretation_hashes": self.interpretation_hashes,
            "graph_view_hash": self.graph_view_hash,
            "controller_posteriors": self.controller_posteriors,
            "budgets": self.budgets,
            "seeds": self.seeds,
            "active_leases": self.active_leases,
            "in_flight_calls": self.in_flight_calls,
            "behavior_closure_fingerprint": self.behavior_closure_fingerprint,
            "stage_caches": self.stage_caches,
            "rate_limit_state": self.rate_limit_state,
        }

    def _compute_hash(self) -> str:
        return content_id(self._content_record())

    def checkpoint_hash(self) -> str:
        """Return the content identity of the checkpoint's current semantic state."""
        return self._compute_hash()

    def _sign(self, *, env: Mapping[str, str] | None = None) -> None:
        signature = hmac.new(
            _checkpoint_key(env), self._sealed_hash.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        object.__setattr__(self, "_signature", signature)

    def verify_checkpoint_hash(self, *, env: Mapping[str, str] | None = None) -> bool:
        """Authenticate the content identity and detect post-signing corruption."""
        try:
            if not (
                is_sha256(self._sealed_hash)
                and self._sealed_hash == self._compute_hash()
                and is_sha256(self._signature)
            ):
                return False
            expected = hmac.new(
                _checkpoint_key(env),
                self._sealed_hash.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected, self._signature)
        except (CheckpointError, TypeError, ValueError):
            return False


@dataclass(frozen=True)
class ResumeReport:
    chain_verified: bool
    closure_compatible: bool
    invalidated_caches: tuple[str, ...]
    resumed_from_sequence: int
    censored_calls: tuple[str, ...]
    ok: bool


def take_checkpoint(
    *,
    log: EventLog,
    problem_contract_hash: str,
    interpretation_hashes: tuple[str, ...],
    graph_view_hash: str,
    controller_posteriors: Mapping[str, Any],
    budgets: Mapping[str, int | float],
    seeds: Mapping[str, int],
    active_leases: tuple[str, ...],
    behavior_closure_fingerprint: str,
    in_flight_calls: tuple[str, ...] = (),
    stage_caches: Mapping[str, Mapping[str, Any]] | None = None,
    rate_limit_state: Mapping[str, Mapping[str, Any]] | None = None,
    env: Mapping[str, str] | None = None,
) -> Checkpoint:
    """Capture one verified, internally consistent event-log prefix."""
    if not isinstance(log, EventLog):
        raise TypeError("log must be an EventLog")
    if not log.verify_integrity():
        raise CheckpointError("cannot checkpoint an event log with invalid integrity")
    events = log.events
    checkpoint = Checkpoint(
        run_id=log.run_id,
        last_sequence=len(events) - 1,
        last_event_id=events[-1].event_id if events else _GENESIS_EVENT_ID,
        merkle_root=merkle_root([event.event_id for event in events]),
        problem_contract_hash=problem_contract_hash,
        interpretation_hashes=interpretation_hashes,
        graph_view_hash=graph_view_hash,
        controller_posteriors=controller_posteriors,
        budgets=budgets,
        seeds=seeds,
        active_leases=active_leases,
        in_flight_calls=in_flight_calls,
        behavior_closure_fingerprint=behavior_closure_fingerprint,
        stage_caches=stage_caches or {},
        rate_limit_state=rate_limit_state or {},
    )
    checkpoint._sign(env=env)
    return checkpoint


def _validate_interrupted_calls(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise CheckpointError("interrupted_calls must be an immutable tuple")
    for index, call_id in enumerate(value):
        _require_nonempty_string(call_id, field_name=f"interrupted_calls[{index}]")
    if len(set(value)) != len(value):
        raise CheckpointError("interrupted_calls cannot contain duplicates")
    return value


def _validate_current_stage_fingerprints(
    value: object,
) -> Mapping[str, str]:
    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise CheckpointError("current_stage_fingerprints must be a mapping")
    result: dict[str, str] = {}
    for stage, fingerprint in value.items():
        _require_nonempty_string(stage, field_name="current stage name")
        result[stage] = _require_digest(
            fingerprint, field_name=f"current_stage_fingerprints.{stage}"
        )
    return MappingProxyType(result)


def _prefix_matches(checkpoint: Checkpoint, log: EventLog) -> bool:
    if checkpoint.run_id != log.run_id:
        return False
    events = log.events
    prefix_length = checkpoint.last_sequence + 1
    if prefix_length < 0 or prefix_length > len(events):
        return False
    prefix = events[:prefix_length]
    expected_last = prefix[-1].event_id if prefix else _GENESIS_EVENT_ID
    return (
        checkpoint.last_event_id == expected_last
        and checkpoint.merkle_root
        == merkle_root([event.event_id for event in prefix])
    )


def resume(
    checkpoint: Checkpoint,
    *,
    log: EventLog,
    current_closure_fingerprint: str,
    interrupted_calls: tuple[str, ...] = (),
    current_stage_fingerprints: Mapping[str, str] | None = None,
    verification_env: Mapping[str, str] | None = None,
) -> ResumeReport:
    """Validate a checkpoint and compute a fail-closed compatible reuse set.

    A valid appended event tail is permitted: the checkpoint commits to its exact
    prefix rather than requiring the current log head to equal the old head.
    Missing current per-stage identity is incompatible, even when the global
    closure happens to be unchanged.
    """
    if not isinstance(checkpoint, Checkpoint):
        raise TypeError("checkpoint must be a Checkpoint")
    if not isinstance(log, EventLog):
        raise TypeError("log must be an EventLog")
    _require_digest(
        current_closure_fingerprint, field_name="current_closure_fingerprint"
    )
    censored = _validate_interrupted_calls(interrupted_calls)
    current_stages = _validate_current_stage_fingerprints(current_stage_fingerprints)

    checkpoint_ok = checkpoint.verify_checkpoint_hash(env=verification_env)
    if checkpoint_ok:
        unrecorded = tuple(sorted(set(censored) - set(checkpoint.in_flight_calls)))
        if unrecorded:
            raise CheckpointError(
                f"cannot censor calls absent from checkpoint in-flight state: {unrecorded!r}"
            )
    elif censored:
        raise CheckpointError("cannot classify interrupted calls from a corrupt checkpoint")
    log_ok = log.verify_integrity()
    prefix_ok = checkpoint_ok and log_ok and _prefix_matches(checkpoint, log)
    closure_ok = (
        prefix_ok
        and checkpoint.behavior_closure_fingerprint == current_closure_fingerprint
    )

    if not prefix_ok:
        invalidated = tuple(sorted(checkpoint.stage_caches)) if checkpoint_ok else ()
    else:
        invalidated = tuple(
            sorted(
                stage
                for stage, cache_record in checkpoint.stage_caches.items()
                if current_stages.get(stage)
                != cache_record["compatibility_fingerprint"]
            )
        )

    return ResumeReport(
        chain_verified=prefix_ok,
        closure_compatible=closure_ok,
        invalidated_caches=invalidated,
        resumed_from_sequence=checkpoint.last_sequence if prefix_ok else -1,
        censored_calls=censored,
        ok=prefix_ok,
    )
