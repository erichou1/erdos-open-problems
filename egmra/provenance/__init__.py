"""Provenance primitives: canonical hashing, stage identity, provenance rules."""

from egmra.provenance.hashing import (
    ProvenanceError,
    canonical_json,
    content_id,
    sha256_bytes,
    sha256_hex,
    is_sha256,
    merkle_root,
)
from egmra.provenance.rules import (
    ProvenanceCheck,
    check_provenance,
    hidden_reasoning_is_provenance,
    is_auditable,
    required_fields,
)

__all__ = [
    "ProvenanceError",
    "canonical_json",
    "content_id",
    "sha256_bytes",
    "sha256_hex",
    "is_sha256",
    "merkle_root",
    "ProvenanceCheck",
    "check_provenance",
    "hidden_reasoning_is_provenance",
    "is_auditable",
    "required_fields",
]
