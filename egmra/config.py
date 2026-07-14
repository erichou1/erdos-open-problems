"""Layered configuration + secrets handling (spec §16 P0, security section).

Configuration is layered: built-in defaults -> optional JSON file -> environment
overrides. Secrets (API keys) are read from the environment ONLY; they never live
in the config file and are never serialized or logged.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Secret env vars that must never be persisted or logged.
SECRET_ENV_VARS = (
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "ARISTOTLE_API_KEY",
    "EGMRA_POLICY_KEY", "EGMRA_EVENT_KEY", "EGMRA_RELEASE_KEY",
    "EGMRA_EVIDENCE_KEY", "EGMRA_GATE_KEY", "EGMRA_PROMOTION_KEY",
    "EGMRA_LEAN_CHECKER_KEY", "EGMRA_AUTHORITY_KEY", "EGMRA_TRUTH_SNAPSHOT_KEY",
    "EGMRA_MODEL_ATTESTATION_KEY", "EGMRA_INTENT_REVIEW_KEY",
    "EGMRA_FORMAL_CORRESPONDENCE_KEY", "EGMRA_CHECKPOINT_KEY",
    "EGMRA_LEGACY_REVIEW_KEY", "EGMRA_LEGACY_EVIDENCE_KEY",
)


@dataclass
class EgmraConfig:
    events_dir: str = "egmra_runs"
    artifact_store_dir: str = "egmra_artifacts"
    oeis_cache_dir: str = "egmra_cache/oeis"
    oeis_offline: bool = True
    lean_lake_path: str = "lake"
    protected_exploration_fraction: float = 0.20
    max_backoff_seconds: float = 120.0
    policy_path: str = ""     # empty -> default_policy_path()

    @classmethod
    def load(cls, path: str | Path | None = None, *, env: dict[str, str] | None = None) -> "EgmraConfig":
        env = env if env is not None else dict(os.environ)
        config = cls()
        if path is not None:
            config_path = Path(path)
            if not config_path.exists():
                raise FileNotFoundError(config_path)
            if config_path.is_symlink() or not config_path.is_file():
                raise ValueError("configuration path must be a regular non-symlink file")
            if config_path.stat().st_size > 1_000_000:
                raise ValueError("configuration file is too large")
            doc = json.loads(
                config_path.read_text(encoding="utf-8"),
                object_pairs_hook=_strict_object,
            )
            if not isinstance(doc, dict):
                raise ValueError("configuration document must be a JSON object")
            _reject_secrets_in_file(doc)
            unknown = sorted(set(doc) - set(vars(config)))
            if unknown:
                raise ValueError(f"unknown configuration settings: {unknown}")
            for key, value in doc.items():
                setattr(config, key, value)
        # environment overrides (non-secret settings only)
        for key in list(vars(config)):
            env_key = f"EGMRA_{key.upper()}"
            if env_key in env and env_key not in SECRET_ENV_VARS:
                setattr(config, key, _coerce(getattr(config, key), env[env_key]))
        config._validate()
        return config

    def _validate(self) -> None:
        for name in (
            "events_dir", "artifact_store_dir", "oeis_cache_dir", "lean_lake_path",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip() or "\x00" in value:
                raise ValueError(f"{name} must be a non-empty path string")
        if type(self.oeis_offline) is not bool:
            raise ValueError("oeis_offline must be a boolean")
        if not isinstance(self.protected_exploration_fraction, (int, float)) \
                or isinstance(self.protected_exploration_fraction, bool) \
                or not math.isfinite(float(self.protected_exploration_fraction)) \
                or not 0.15 <= float(self.protected_exploration_fraction) <= 0.25:
            raise ValueError("protected_exploration_fraction must be within 0.15..0.25")
        if not isinstance(self.max_backoff_seconds, (int, float)) \
                or isinstance(self.max_backoff_seconds, bool) \
                or not math.isfinite(float(self.max_backoff_seconds)) \
                or not 0.0 < float(self.max_backoff_seconds) <= 120.0:
            raise ValueError("max_backoff_seconds must be finite and within (0, 120]")
        if not isinstance(self.policy_path, str) or "\x00" in self.policy_path:
            raise ValueError("policy_path must be a path string")

    def to_public_dict(self) -> dict[str, Any]:
        """Serializable config with no secrets (safe to log)."""
        return {k: v for k, v in asdict(self).items()}

    @staticmethod
    def secret(name: str, *, env: dict[str, str] | None = None) -> str:
        """Read a secret from the environment only; empty if unset."""
        if name not in SECRET_ENV_VARS:
            raise ValueError(f"{name!r} is not an allowlisted secret")
        env = env if env is not None else dict(os.environ)
        return env.get(name, "").strip()


def _reject_secrets_in_file(doc: dict) -> None:
    allowed = {name.casefold() for name in SECRET_ENV_VARS}
    present: list[str] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                child = f"{path}.{key}" if path else str(key)
                if isinstance(key, str) and key.casefold() in allowed:
                    present.append(child)
                walk(item, child)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")

    walk(doc, "")
    if present:
        raise ValueError(f"secrets must not appear in the config file: {present}; use env vars")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate configuration key: {key!r}")
        result[key] = value
    return result


def _coerce(current: Any, raw: str) -> Any:
    if isinstance(current, bool):
        normalized = raw.strip().lower()
        if normalized in ("1", "true", "yes", "on"):
            return True
        if normalized in ("0", "false", "no", "off"):
            return False
        raise ValueError(f"invalid boolean value {raw!r}")
    if isinstance(current, int):
        return int(raw)
    if isinstance(current, float):
        return float(raw)
    return raw
