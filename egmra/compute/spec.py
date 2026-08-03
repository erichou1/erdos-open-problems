"""Immutable, validated descriptions of computational jobs (spec §6.8)."""

from __future__ import annotations

import keyword
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from egmra.provenance.hashing import canonical_json, content_id, sha256_hex

ARITHMETIC_MODES = ("exact", "interval", "float")
SANDBOX_POLICIES = ("restricted-python-subprocess", "container")
_SCHEMA_KEYS = {
    "type", "required", "properties", "additionalProperties", "items", "enum", "const",
    "minimum", "maximum", "minLength", "maxLength", "minItems", "maxItems",
}
_SCHEMA_TYPES = {"object", "array", "string", "integer", "number", "boolean", "null"}


def _freeze_json(value: Any, *, path: str) -> Any:
    """Copy JSON data into immutable containers.

    ``frozen=True`` does not make nested dicts and lists immutable.  A job hash
    must not change because its caller later mutates a configuration object.
    """

    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} contains a non-finite float")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} contains a non-string key")
            frozen[key] = _freeze_json(item, path=f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item, path=f"{path}[{index}]") for index, item in enumerate(value))
    raise ValueError(f"{path} contains unsupported value type {type(value).__name__}")


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True)
class ExperimentSpec:
    purpose: str
    claim_ids: tuple[str, ...] = ()
    branch_ids: tuple[str, ...] = ()
    code_ref: str = ""              # repository/commit
    entry_point: str = "experiment"
    inputs: Mapping[str, Any] = field(default_factory=dict)
    domain: str = ""
    coverage: str = ""
    tool_versions: Mapping[str, Any] = field(default_factory=dict)
    arithmetic_mode: str = "exact"  # exact | interval | float
    precision: str = ""
    error_bounds: str = ""
    seed: int = 0
    cpu_seconds: int = 10
    memory_bytes: int = 512 * 1024 * 1024
    wall_seconds: float = 30.0
    max_processes: int = 1
    max_output_bytes: int = 1_000_000
    max_log_bytes: int = 1_000_000
    output_schema: Mapping[str, Any] = field(default_factory=dict)
    certificate_kind: str = ""      # e.g. sat_unsat_proof, interval_bound
    checker_id: str = ""
    network: str = "off"            # off | allowlist
    sandbox_policy: str = "restricted-python-subprocess"

    def __post_init__(self) -> None:
        if self.arithmetic_mode not in ARITHMETIC_MODES:
            raise ValueError(f"arithmetic_mode must be one of {ARITHMETIC_MODES}")
        if self.network not in ("off", "allowlist"):
            raise ValueError("network must be 'off' or 'allowlist'")
        if self.sandbox_policy not in SANDBOX_POLICIES:
            raise ValueError(f"sandbox_policy must be one of {SANDBOX_POLICIES}")
        if not self.entry_point.isidentifier() or keyword.iskeyword(self.entry_point) \
                or self.entry_point.startswith("_"):
            raise ValueError("entry_point must be a public Python identifier")
        _positive_int("cpu_seconds", self.cpu_seconds, maximum=3_600)
        _positive_int("memory_bytes", self.memory_bytes, maximum=16 * 1024**3)
        _positive_number("wall_seconds", self.wall_seconds, maximum=3_600.0)
        _positive_int("max_processes", self.max_processes, maximum=64)
        _positive_int("max_output_bytes", self.max_output_bytes, maximum=16 * 1024**2)
        _positive_int("max_log_bytes", self.max_log_bytes, maximum=16 * 1024**2)
        if isinstance(self.seed, bool) or not isinstance(self.seed, int) \
                or not 0 <= self.seed <= 2**32 - 1:
            raise ValueError("seed must be an integer in 0..4294967295")
        _validate_output_schema(self.output_schema)

        object.__setattr__(self, "claim_ids", tuple(self.claim_ids))
        object.__setattr__(self, "branch_ids", tuple(self.branch_ids))
        object.__setattr__(self, "inputs", _freeze_json(self.inputs, path="inputs"))
        object.__setattr__(self, "tool_versions", _freeze_json(self.tool_versions, path="tool_versions"))
        object.__setattr__(self, "output_schema", _freeze_json(self.output_schema, path="output_schema"))
        # Validate the complete canonical form at construction, not only when a
        # caller happens to request a hash.
        canonical_json(self.to_dict())

    def spec_hash(self) -> str:
        return content_id(self.to_dict())

    def code_hash(self, code: str) -> str:
        return sha256_hex(code)

    def to_dict(self) -> dict[str, Any]:
        out = {key: _thaw_json(value) for key, value in self.__dict__.items()}
        out["claim_ids"] = list(self.claim_ids)
        out["branch_ids"] = list(self.branch_ids)
        return out

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ExperimentSpec":
        values = dict(payload)
        values["claim_ids"] = tuple(values.get("claim_ids", ()))
        values["branch_ids"] = tuple(values.get("branch_ids", ()))
        return cls(**values)


def _positive_int(name: str, value: Any, *, maximum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0 or value > maximum:
        raise ValueError(f"{name} must be an integer in 1..{maximum}")


def _positive_number(name: str, value: Any, *, maximum: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(float(value)) or value <= 0 or value > maximum:
        raise ValueError(f"{name} must be finite and in (0, {maximum}]")


def _validate_output_schema(schema: Any, *, path: str = "output_schema", depth: int = 0) -> None:
    if depth > 64:
        raise ValueError("output_schema exceeds maximum nesting depth")
    if not isinstance(schema, Mapping):
        raise ValueError(f"{path} must be an object")
    unknown = set(schema) - _SCHEMA_KEYS
    if unknown:
        raise ValueError(f"{path} has unsupported keywords {sorted(unknown)!r}")
    schema_type = schema.get("type")
    if schema_type is not None and schema_type not in _SCHEMA_TYPES:
        raise ValueError(f"{path}.type is unsupported")
    required = schema.get("required")
    if required is not None:
        if not isinstance(required, (list, tuple)) \
                or any(not isinstance(item, str) for item in required) \
                or len(set(required)) != len(required):
            raise ValueError(f"{path}.required must be an array of unique strings")
    properties = schema.get("properties")
    if properties is not None:
        if not isinstance(properties, Mapping):
            raise ValueError(f"{path}.properties must be an object")
        for name, child in properties.items():
            if not isinstance(name, str):
                raise ValueError(f"{path}.properties has a non-string key")
            _validate_output_schema(child, path=f"{path}.properties.{name}", depth=depth + 1)
    if "additionalProperties" in schema and not isinstance(schema["additionalProperties"], bool):
        raise ValueError(f"{path}.additionalProperties must be boolean")
    if "items" in schema:
        _validate_output_schema(schema["items"], path=f"{path}.items", depth=depth + 1)
    if "enum" in schema and not isinstance(schema["enum"], (list, tuple)):
        raise ValueError(f"{path}.enum must be an array")
    for name in ("minLength", "maxLength", "minItems", "maxItems"):
        if name in schema:
            value = schema[name]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{path}.{name} must be a nonnegative integer")
    for low, high in (("minLength", "maxLength"), ("minItems", "maxItems")):
        if low in schema and high in schema and schema[low] > schema[high]:
            raise ValueError(f"{path}.{low} cannot exceed {high}")
    for name in ("minimum", "maximum"):
        if name in schema:
            value = schema[name]
            if isinstance(value, bool) or not isinstance(value, (int, float)) \
                    or not math.isfinite(float(value)):
                raise ValueError(f"{path}.{name} must be a finite number")
    if "minimum" in schema and "maximum" in schema \
            and schema["minimum"] > schema["maximum"]:
        raise ValueError(f"{path}.minimum cannot exceed maximum")
