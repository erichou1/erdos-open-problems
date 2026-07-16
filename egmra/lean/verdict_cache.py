"""Sealed kernel-verdict cache + lemma sealing, as a LeanService wrapper.

Every kernel check pays a fresh Mathlib load (minutes). The verdict of the
pinned kernel is DETERMINISTIC in (environment, source, obligation, bindings),
so an identical re-check — a resample retry, a repair round that regenerated
the same source, a cross-campaign duplicate — can replay the stored
certificate instead of re-paying the kernel.

Soundness: the stored artifact is the ORIGINAL signed
:class:`~egmra.lean.service.FormalCertificate`; on load it is reconstructed
and its own HMAC signature re-verified, and the cache key binds the full
obligation (environment id, source hash, declaration, expected-type hash,
module hash, claim bindings). Any mismatch or tamper falls open to a LIVE
kernel check — a cache can therefore never mint a verdict, only skip
recomputing one it can prove was already sealed.

The wrapper also seals PASSING lemmas into the verified lemma library
(:mod:`egmra.retrieval.lemma_library`) so they compound across problems.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from egmra.lean.service import FormalCertificate
from egmra.provenance.hashing import canonical_json, sha256_hex
from egmra.retrieval.lemma_library import append_sealed_lemma

_SCHEMA_VERSION = 1
_MAX_ENTRY_BYTES = 2_000_000
_TUPLE_FIELDS = ("transitive_axioms", "placeholder_findings", "unsafe_findings",
                 "artifact_hashes")


class SealedLeanService:
    """Wrap a LeanService with a verdict cache and lemma-library sealing."""

    def __init__(self, service: Any, *, cache_dir: Path | None = None,
                 lemma_library: Path | None = None, problem_id: str = "") -> None:
        self._service = service
        self.cache_dir = Path(cache_dir) if cache_dir is not None else None
        self.lemma_library = Path(lemma_library) if lemma_library is not None else None
        self.problem_id = problem_id
        self.hits = 0
        self.misses = 0

    def __getattr__(self, name: str) -> Any:
        return getattr(object.__getattribute__(self, "_service"), name)

    def create_environment(self, **kwargs: Any) -> Any:
        return self._service.create_environment(**kwargs)

    # ── cache mechanics ──────────────────────────────────────────────────────
    def _key(self, *, environment: Any, source: str, declaration_name: str,
             expected_type_hash: str, immutable_target_module_hash: str,
             expected_type_source: str, claim_bindings: dict | None) -> str:
        return sha256_hex(canonical_json({
            "environment_id": str(getattr(environment, "environment_id", "")),
            "source_sha256": sha256_hex(source),
            "declaration_name": declaration_name,
            "expected_type_hash": expected_type_hash,
            "immutable_target_module_hash": immutable_target_module_hash,
            "expected_type_source": expected_type_source,
            "claim_bindings": dict(claim_bindings or {}),
        }))

    def _entry_path(self, key: str) -> Path:
        assert self.cache_dir is not None
        return self.cache_dir / f"verdict.{key}.json"

    def _load(self, key: str) -> FormalCertificate | None:
        if self.cache_dir is None:
            return None
        path = self._entry_path(key)
        try:
            if path.is_symlink() or not path.is_file():
                return None
            if path.stat().st_size > _MAX_ENTRY_BYTES:
                return None
            record = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(record, dict) \
                    or record.get("schema_version") != _SCHEMA_VERSION \
                    or record.get("key") != key:
                return None
            payload = record.get("certificate")
            if not isinstance(payload, dict):
                return None
            fields = dict(payload)
            # to_dict() adds DERIVED keys that are not constructor fields.
            fields.pop("certificate_digest", None)
            fields.pop("passed", None)
            for name in _TUPLE_FIELDS:
                if isinstance(fields.get(name), list):
                    fields[name] = tuple(fields[name])
            if isinstance(fields.get("claim_bindings"), list):
                fields["claim_bindings"] = tuple(
                    tuple(item) for item in fields["claim_bindings"])
            certificate = FormalCertificate(**fields)
            # The certificate's OWN signature is the integrity check: a
            # tampered entry fails closed to a live kernel re-check.
            if not certificate.verify():
                return None
            return certificate
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return None

    def _store(self, key: str, certificate: FormalCertificate,
               context: dict | None = None) -> None:
        if self.cache_dir is None:
            return
        try:
            payload = json.dumps({
                "schema_version": _SCHEMA_VERSION,
                "key": key,
                # Operations context only — the certificate's own signature is
                # the sole integrity/trust check on load; these fields never
                # participate in verification.
                "context": dict(context or {}),
                "certificate": certificate.to_dict(),
            }, ensure_ascii=False)
            if len(payload.encode("utf-8")) > _MAX_ENTRY_BYTES:
                return
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(dir=self.cache_dir, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(payload)
                os.chmod(tmp_name, 0o600)
                os.replace(tmp_name, self._entry_path(key))
            except BaseException:
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass
                raise
        except OSError:
            return          # persistence is an ops aid, never a verdict

    # ── the wrapped verification ─────────────────────────────────────────────
    def verify_declaration(self, *, environment: Any, source: str,
                           declaration_name: str, expected_type_hash: str,
                           immutable_target_module_hash: str,
                           expected_type_source: str = "",
                           claim_bindings: dict | None = None,
                           **kwargs: Any) -> FormalCertificate:
        key = self._key(
            environment=environment, source=source,
            declaration_name=declaration_name,
            expected_type_hash=expected_type_hash,
            immutable_target_module_hash=immutable_target_module_hash,
            expected_type_source=expected_type_source,
            claim_bindings=claim_bindings)
        cached = self._load(key)
        if cached is not None:
            self.hits += 1
            return cached
        self.misses += 1
        certificate = self._service.verify_declaration(
            environment=environment, source=source,
            declaration_name=declaration_name,
            expected_type_hash=expected_type_hash,
            immutable_target_module_hash=immutable_target_module_hash,
            expected_type_source=expected_type_source,
            claim_bindings=claim_bindings, **kwargs)
        # Only PASSING certificates are cached: FormalCertificate.verify()
        # deliberately conflates integrity with qualification, so a stored
        # rejection could never re-validate on load — rejected sources simply
        # re-check live (they are usually mutated by repair anyway).
        if getattr(certificate, "passed", False):
            self._store(key, certificate, context={
                "declaration_name": declaration_name,
                "expected_type_source": expected_type_source[:2000],
                "problem_id": self.problem_id,
            })
        if getattr(certificate, "passed", False) and self.lemma_library is not None:
            try:
                append_sealed_lemma(
                    self.lemma_library, problem_id=self.problem_id,
                    declaration_name=declaration_name,
                    expected_type_source=expected_type_source,
                    source=source, certificate=certificate.to_dict())
            except OSError:
                pass    # library persistence is an ops aid, never a verdict
        return certificate
