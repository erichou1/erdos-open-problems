"""Verified lemma library: kernel-sealed results become reusable premises.

LeanDojo/ReProver's central finding is that premise selection is the key
bottleneck in formal proving; DeepSeek-Prover-V2's recipe is recursive subgoal
decomposition where solved subgoals compound. This module is the pipeline's
version of both: every candidate the pinned kernel PASSES is appended to a
durable library, and the library is offered back through the frozen retrieval
packet as literature whose provenance is our own kernel seal — so each sealed
lemma makes neighboring problems easier instead of being discarded with its
run.

Trust boundary: a library record never asserts problem-level truth. It enters
prompts/packets exactly like any retrieved literature (audited imports,
corroboration rules unchanged); its distinguishing feature is honest
provenance — ``proof_status="kernel_checked"`` with the certificate hashes
attached.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from egmra.learning.mechanisms import mechanism_tags
from egmra.provenance.hashing import sha256_hex
from egmra.retrieval.records import TheoremRecord

_SCHEMA_VERSION = 1
_MAX_SOURCE_CHARS = 20_000
_MAX_LIBRARY_BYTES = 50_000_000


def _entry_key(declaration_name: str, expected_type_source: str, source: str) -> str:
    return sha256_hex(
        f"{declaration_name}\n{expected_type_source}\n{source}")


def append_sealed_lemma(path: Path, *, problem_id: str, declaration_name: str,
                        expected_type_source: str, source: str,
                        certificate: dict[str, Any]) -> bool:
    """Append one kernel-PASSED lemma (idempotent by content key).

    Persistence is an ops aid: the caller treats a write failure as
    non-mathematical. Returns False when the entry already exists or inputs
    are degenerate.
    """
    if not declaration_name.strip() or not source.strip():
        return False
    path = Path(path)
    key = _entry_key(declaration_name, expected_type_source, source)
    for record in _iter_records(path):
        if record.get("key") == key:
            return False
    entry = {
        "schema_version": _SCHEMA_VERSION,
        "key": key,
        "problem_id": problem_id,
        "declaration_name": declaration_name,
        "expected_type_source": expected_type_source[:2000],
        # R10 (cheap half): coarse mechanism keywords recorded at seal time —
        # search metadata only, never part of the content key or certificate.
        "mechanism_tags": list(mechanism_tags(
            f"{declaration_name} {expected_type_source} {source[:1000]}")),
        "source": source[:_MAX_SOURCE_CHARS],
        "source_sha256": sha256_hex(source),
        "certificate": {
            name: certificate.get(name)
            for name in ("expected_type_hash", "candidate_type_hash",
                         "proof_term_hash", "transitive_axioms",
                         "checker_id", "checker_version",
                         "certificate_signature",
                         "certificate_key_fingerprint")
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)
    return True


def _iter_records(path: Path):
    try:
        if path.is_symlink() or not path.is_file():
            return
        if path.stat().st_size > _MAX_LIBRARY_BYTES:
            return
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict) \
                        and record.get("schema_version") == _SCHEMA_VERSION:
                    yield record
    except OSError:
        return


def load_lemma_records(path: Path | None) -> list[TheoremRecord]:
    """Render the library as retrieval records (fails open to [])."""
    if path is None:
        return []
    records: list[TheoremRecord] = []
    seen: set[str] = set()
    for entry in _iter_records(Path(path)):
        key = str(entry.get("key", ""))
        declaration = str(entry.get("declaration_name", "")).strip()
        typ = str(entry.get("expected_type_source", "")).strip()
        if not key or key in seen or not declaration:
            continue
        seen.add(key)
        statement = (
            f"Kernel-checked Lean lemma {declaration}"
            + (f" : {typ}" if typ else "")
        )
        records.append(TheoremRecord(
            theorem_id=f"sealed-lemma-{key[:16]}",
            canonical_statement=statement,
            conclusion=typ or statement,
            source_uri=f"egmra://lemma-library/{key}",
            source_version=str(entry.get("problem_id", "")),
            source_content_hash=str(entry.get("source_sha256", "")),
            verbatim_theorem_and_hypothesis_extract=str(
                entry.get("source", ""))[:2000],
            extraction_method="egmra_kernel_seal",
            proof_status="kernel_checked",
            independent_verification_status="kernel_checked",
        ))
    return records
