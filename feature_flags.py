"""Runtime access to release-state feature flags."""

import json
from pathlib import Path


DEFAULT_FLAGS = Path(__file__).resolve().parent / "config" / "pipeline_features.json"


def load_feature_flags(path: Path = DEFAULT_FLAGS) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("feature flag document must be a JSON object")
    return value


def feature_enabled(name: str, path: Path = DEFAULT_FLAGS) -> bool:
    flags = load_feature_flags(path)
    if name not in flags:
        raise KeyError(f"unknown feature flag: {name}")
    return flags[name] is True


def require_feature(name: str, *, override: bool = False,
                    path: Path = DEFAULT_FLAGS) -> None:
    if override or feature_enabled(name, path):
        return
    raise RuntimeError(
        f"feature '{name}' is disabled in {path}; pass the explicit experimental "
        "override only after reviewing its migration gate and rollback"
    )
