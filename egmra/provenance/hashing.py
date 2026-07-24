"""Deterministic content-addressing utilities.

Everything the truth plane records is content-addressed. Canonical JSON gives a
single deterministic byte serialization so identical logical values always hash
identically regardless of key order or float formatting differences.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from typing import Any, TypeGuard

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ProvenanceError(ValueError):
    """Raised when a value cannot be canonicalized or an identity is malformed."""


def _normalize(value: Any, *, path: str = "$") -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ProvenanceError(f"{path} contains a non-finite float")
        return value
    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ProvenanceError(f"{path} has a non-string object key")
            out[key] = _normalize(item, path=f"{path}.{key}")
        return out
    if isinstance(value, (list, tuple)):
        return [_normalize(item, path=f"{path}[{i}]") for i, item in enumerate(value)]
    # dataclasses / sets are normalized via their canonical dict form by callers.
    raise ProvenanceError(
        f"{path} has unsupported type {type(value).__name__}; convert to a "
        "JSON-compatible structure before hashing"
    )


def canonical_json(value: Any) -> str:
    """Return deterministic UTF-8 JSON text suitable for hashing."""
    return json.dumps(
        _normalize(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_bytes(data: bytes) -> str:
    """Return the lowercase hex SHA-256 of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_hex(text: str) -> str:
    """Return the lowercase hex SHA-256 of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_id(value: Any) -> str:
    """Return the SHA-256 identity of a JSON-compatible value."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def is_sha256(value: object) -> TypeGuard[str]:
    """True if ``value`` is a lowercase 64-hex SHA-256 digest string."""
    return isinstance(value, str) and bool(_SHA256_RE.fullmatch(value))


def merkle_root(hashes: list[str]) -> str:
    """Return a deterministic Merkle root over an ordered list of hex hashes.

    An empty list hashes the empty string so the root is always defined. The
    tree is order-sensitive: the event log's Merkle root therefore commits to the
    exact sequence of events, not just the set.
    """
    if not hashes:
        return sha256_hex("")
    layer = list(hashes)
    for h in layer:
        if not is_sha256(h):
            raise ProvenanceError(f"merkle_root requires SHA-256 leaves, got {h!r}")
    while len(layer) > 1:
        nxt: list[str] = []
        for i in range(0, len(layer), 2):
            left = layer[i]
            right = layer[i + 1] if i + 1 < len(layer) else left
            nxt.append(sha256_hex(left + right))
        layer = nxt
    return layer[0]
