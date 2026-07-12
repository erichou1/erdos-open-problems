"""Canonical, reusable identities for solver runs and stage caches.

A run contract intentionally excludes a unique execution or attempt ID.  It
describes only the inputs that make a persisted stage response safe to reuse.
Unique execution IDs belong in audit manifests, not in cache keys.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from typing import Any


RUN_CONTRACT_SCHEMA_VERSION = 2
STAGE_CACHE_SCHEMA_VERSION = 3
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_UNRECORDED = {"", "unknown", "unrecorded", "none", "n/a", "unspecified"}


class RunContractError(ValueError):
    """Raised when an identity is incomplete or cannot be canonicalized."""


def _normalize_json(value: Any, *, path: str = "$") -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise RunContractError(f"{path} contains a non-finite float")
        return value
    if isinstance(value, Mapping):
        normalized = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise RunContractError(f"{path} contains a non-string object key")
            normalized[key] = _normalize_json(item, path=f"{path}.{key}")
        return normalized
    if isinstance(value, (list, tuple)):
        return [
            _normalize_json(item, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
    raise RunContractError(
        f"{path} contains unsupported value type {type(value).__name__}"
    )


def canonical_json(value: Any) -> str:
    """Return deterministic UTF-8 JSON text suitable for hashing."""
    normalized = _normalize_json(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _recorded_string(value: Any, *, field: str) -> str:
    if not isinstance(value, str):
        raise RunContractError(f"{field} must be a string")
    normalized = value.strip()
    lowered = normalized.casefold()
    if lowered in _UNRECORDED or "unrecorded" in lowered:
        raise RunContractError(f"{field} must record an exact identity")
    return normalized


def _sha256(value: Any, *, field: str) -> str:
    normalized = _recorded_string(value, field=field).lower()
    if not _SHA256.fullmatch(normalized):
        raise RunContractError(f"{field} must be a lowercase SHA-256 digest")
    return normalized


def _nonempty_mapping(value: Any, *, field: str) -> dict[str, Any]:
    normalized = _normalize_json(value, path=f"$.{field}")
    if not isinstance(normalized, dict) or not normalized:
        raise RunContractError(f"{field} must be a non-empty JSON object")
    return normalized


def validate_run_contract(contract: Any) -> dict[str, Any]:
    """Validate and normalize a complete reusable run contract.

    Extra keys fail closed so volatile execution IDs cannot accidentally enter
    what is meant to be a reusable identity.
    """
    normalized = _normalize_json(contract)
    if not isinstance(normalized, dict):
        raise RunContractError("run contract must be a JSON object")
    required = {
        "run_contract_schema_version",
        "statement_sha256",
        "source_snapshot",
        "pipeline_fingerprint",
        "research_directive_sha256",
        "model_portfolio",
        "toolset",
        "budget",
        "execution_config",
        "dependencies",
        "runtime",
    }
    if set(normalized) != required:
        missing = sorted(required - set(normalized))
        extra = sorted(set(normalized) - required)
        raise RunContractError(
            f"run contract fields mismatch; missing={missing}, extra={extra}"
        )
    if normalized["run_contract_schema_version"] != RUN_CONTRACT_SCHEMA_VERSION:
        raise RunContractError("unsupported run contract schema version")

    source = normalized["source_snapshot"]
    if not isinstance(source, dict) or set(source) != {"id", "sha256"}:
        raise RunContractError("source_snapshot must contain exactly id and sha256")

    return {
        "run_contract_schema_version": RUN_CONTRACT_SCHEMA_VERSION,
        "statement_sha256": _sha256(
            normalized["statement_sha256"], field="statement_sha256"
        ),
        "source_snapshot": {
            "id": _recorded_string(source["id"], field="source_snapshot.id"),
            "sha256": _sha256(
                source["sha256"], field="source_snapshot.sha256"
            ),
        },
        "pipeline_fingerprint": _recorded_string(
            normalized["pipeline_fingerprint"], field="pipeline_fingerprint"
        ),
        "research_directive_sha256": _sha256(
            normalized["research_directive_sha256"],
            field="research_directive_sha256",
        ),
        "model_portfolio": _recorded_string(
            normalized["model_portfolio"], field="model_portfolio"
        ),
        "toolset": _nonempty_mapping(normalized["toolset"], field="toolset"),
        "budget": _nonempty_mapping(normalized["budget"], field="budget"),
        "execution_config": _nonempty_mapping(
            normalized["execution_config"], field="execution_config"
        ),
        "dependencies": _nonempty_mapping(
            normalized["dependencies"], field="dependencies"
        ),
        "runtime": _nonempty_mapping(normalized["runtime"], field="runtime"),
    }


def make_run_contract(
    *,
    statement_sha256: str,
    source_snapshot_id: str,
    source_snapshot_sha256: str,
    pipeline_fingerprint: str,
    research_directive_sha256: str,
    model_portfolio: str,
    toolset: Mapping[str, Any],
    budget: Mapping[str, Any],
    execution_config: Mapping[str, Any],
    dependencies: Mapping[str, Any],
    runtime: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a normalized reusable run contract from explicit identities."""
    return validate_run_contract({
        "run_contract_schema_version": RUN_CONTRACT_SCHEMA_VERSION,
        "statement_sha256": statement_sha256,
        "source_snapshot": {
            "id": source_snapshot_id,
            "sha256": source_snapshot_sha256,
        },
        "pipeline_fingerprint": pipeline_fingerprint,
        "research_directive_sha256": research_directive_sha256,
        "model_portfolio": model_portfolio,
        "toolset": toolset,
        "budget": budget,
        "execution_config": execution_config,
        "dependencies": dependencies,
        "runtime": runtime,
    })


def run_contract_id(contract: Mapping[str, Any]) -> str:
    """Return the SHA-256 identity of a validated reusable run contract."""
    validated = validate_run_contract(contract)
    return hashlib.sha256(canonical_json(validated).encode("utf-8")).hexdigest()


def run_context_id(*, run_contract_id_value: str, execution_id: str) -> str:
    """Return an execution-specific context ID for ledgers and audit joins.

    Unlike ``run_contract_id``, this identifier must never be used as a reusable
    cache key: it deliberately changes for every execution.
    """
    identity = {
        "execution_id": _recorded_string(execution_id, field="execution_id"),
        "run_contract_id": _sha256(
            run_contract_id_value, field="run_contract_id"
        ),
    }
    return hashlib.sha256(canonical_json(identity).encode("utf-8")).hexdigest()


def stage_cache_context_id(
    *,
    run_contract_id_value: str,
    stage: str,
    prompt_sha256: str,
    cache_schema_version: int = STAGE_CACHE_SCHEMA_VERSION,
) -> str:
    """Bind a stage cache key to schema, stage, prompt, and run contract."""
    contract_id = _sha256(run_contract_id_value, field="run_contract_id")
    prompt_id = _sha256(prompt_sha256, field="prompt_sha256")
    stage_name = _recorded_string(stage, field="stage")
    if cache_schema_version != STAGE_CACHE_SCHEMA_VERSION:
        raise RunContractError("unsupported stage cache schema version")
    identity = {
        "cache_schema_version": cache_schema_version,
        "prompt_sha256": prompt_id,
        "run_contract_id": contract_id,
        "stage": stage_name,
    }
    return hashlib.sha256(canonical_json(identity).encode("utf-8")).hexdigest()
