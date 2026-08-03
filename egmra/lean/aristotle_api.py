"""Aristotle API client (DECISIONS.md D-B: allowed, but never a trust root).

This is a real transport + artifact-intake client for the Aristotle formal-search
service. It is written against an injectable :class:`AristotleTransport` so the
submit/poll/download/quarantine control flow is fully exercised by a fake
transport in tests; the live :class:`HttpAristotleTransport` speaks HTTP via
``requests`` and reads the API key from the environment only.

The security-critical invariants (spec §9.6, task decision B):

* A vendor status of ``COMPLETE``/``solved`` is **never** a promotion. It only
  means "an artifact is available to re-check locally." Every returned artifact
  carries ``promotable=False`` until an *independent local* Lean replay passes.
* Returned Lean is executable metaprogram code, so the downloaded archive is
  extracted into a quarantine directory with a hardened extractor that rejects
  absolute paths, ``..`` traversal, symlinks/hardlinks/special files, oversized
  entries, and archive/zip bombs. Nothing is executed by this module.
* :meth:`AristotleApiClient.bind_local_replay` delegates trust to a caller-supplied
  local verifier (the pinned ``LeanService`` kernel path). A vendor result that
  the local verifier rejects is rejected, regardless of vendor status.
"""

from __future__ import annotations

import hashlib
import hmac
import io
import os
import re
import tarfile
import time
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Protocol
from urllib.parse import quote

from egmra.lean.aristotle_routing import AristotleRequest, AristotleRouting
from egmra.provenance.hashing import canonical_json, content_id, is_sha256, sha256_bytes, sha256_hex

# Vendor terminal statuses that indicate an artifact is available (NOT a proof).
VENDOR_COMPLETE_STATUSES = frozenset(
    {"complete", "completed", "solved", "succeeded", "success", "done"}
)
VENDOR_FAILURE_STATUSES = frozenset(
    {"failed", "error", "errored", "rejected", "cancelled", "canceled", "timeout"}
)

# Conservative archive-intake ceilings (defence in depth against archive bombs).
_DEFAULT_MAX_ENTRIES = 4000
_DEFAULT_MAX_ENTRY_BYTES = 16 * 1024 * 1024
_DEFAULT_MAX_TOTAL_BYTES = 128 * 1024 * 1024

# A strict, filesystem-safe job-id format: no slashes, no traversal, no leading dot.
_JOB_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")

# The local Lean checker key seals a replay attestation; it lives outside worker
# sandboxes and is the *only* thing that can turn a returned artifact into a
# trusted local verification (never a caller boolean/string/dict).
LEAN_REPLAY_KEY_ENV = "EGMRA_LEAN_CHECKER_KEY"


class AristotleClientError(RuntimeError):
    """Base class for Aristotle client failures."""


class AristotleTransportError(AristotleClientError):
    """The transport could not complete a submit/poll/download."""


class UnsafeArchiveError(AristotleClientError):
    """A returned archive attempted traversal, a symlink, or an oversized payload."""


class UnsafeJobIdError(AristotleClientError):
    """A job id is not a filesystem-safe token and could escape the quarantine."""


def validate_job_id(job_id: str) -> str:
    """Return ``job_id`` if it is a strict, filesystem-safe token, else raise."""
    if not isinstance(job_id, str) or not _JOB_ID_RE.match(job_id):
        raise UnsafeJobIdError(f"unsafe or malformed job id: {job_id!r}")
    return job_id


def resolve_quarantine_dir(quarantine_root: Path, job_id: str) -> Path:
    """Resolve a per-job quarantine dir with no symlink following (defect 4.8).

    The job id is a single safe token (no separators/traversal), so the only
    attacker-controlled path component is the ``root/job_id`` child. Every check
    uses ``lstat`` (``is_symlink``) and does **not** follow links: the root must
    be a real non-symlink directory, and the destination must not pre-exist as a
    symlink. The child is joined onto the resolved root without resolving it, so
    a pre-existing symlink can never redirect writes.
    """
    validate_job_id(job_id)
    root = Path(quarantine_root)
    # The configured root must exist (if present) as a real, non-symlink directory.
    if root.is_symlink():
        raise UnsafeJobIdError(f"quarantine root is a symlink: {root}")
    if root.exists() and not root.is_dir():
        raise UnsafeJobIdError(f"quarantine root is not a directory: {root}")
    child = root / job_id
    # lstat the destination WITHOUT following it — reject a pre-existing symlink,
    # hard-linked, or special-file destination.
    if child.is_symlink():
        raise UnsafeJobIdError(f"quarantine destination pre-exists as a symlink: {child}")
    if child.exists() and not child.is_dir():
        raise UnsafeJobIdError(f"quarantine destination is not a directory: {child}")
    resolved_root = root.resolve()
    # job_id has no separators/'..', so this stays directly under the resolved root.
    quarantine_dir = resolved_root / job_id
    if quarantine_dir.parent != resolved_root:
        raise UnsafeJobIdError(f"job id escapes quarantine root: {job_id!r}")
    return quarantine_dir


class AristotleTransport(Protocol):
    """The minimal transport the client drives (fake in tests, HTTP in prod)."""

    def submit(self, payload: dict[str, Any]) -> str:
        """Submit a locked target; return an opaque provider job id."""

    def poll(self, job_id: str) -> dict[str, Any]:
        """Return the provider's job record, including a ``status`` field."""

    def download(self, job_id: str) -> bytes:
        """Return the raw result archive bytes for a completed job."""


@dataclass(frozen=True)
class AristotleStatus:
    """A normalized poll result. ``promotable`` is always False here."""

    job_id: str
    raw_status: str
    vendor_reports_complete: bool
    failed: bool
    detail: dict[str, Any] = field(default_factory=dict)
    # A vendor status is never a promotion; local replay is the only trust root.
    promotable: bool = False


@dataclass(frozen=True)
class AristotleArtifact:
    """A quarantined, hardened extraction of a returned result archive."""

    job_id: str
    vendor_status: str
    vendor_reports_complete: bool
    quarantine_dir: Path
    extracted_files: tuple[Path, ...]
    total_bytes: int
    # Never promotable on arrival — a local replay must pass first.
    promotable: bool = False


@dataclass(frozen=True)
class LocalLeanReplayAttestation:
    """A sealed, claim-bound result of an independent local Lean replay.

    This is the ONLY object that can turn a quarantined vendor artifact into a
    trusted local verification. A caller boolean/string/dict/arbitrary object can
    never manufacture it: it must be sealed with an HMAC under the local checker
    key and bound to the exact claim, target, source, environment, and artifact.
    """

    claim_id: str
    normalized_target_hash: str
    source_hash: str
    environment_hash: str
    lean_version: str
    mathlib_commit: str
    artifact_hash: str
    checker_id: str
    replay_log_hash: str
    issued_at: str
    key_fingerprint: str = ""
    signature: str = ""

    def sealed_record(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "normalized_target_hash": self.normalized_target_hash,
            "source_hash": self.source_hash,
            "environment_hash": self.environment_hash,
            "lean_version": self.lean_version,
            "mathlib_commit": self.mathlib_commit,
            "artifact_hash": self.artifact_hash,
            "checker_id": self.checker_id,
            "replay_log_hash": self.replay_log_hash,
            "issued_at": self.issued_at,
        }


def _lean_replay_key(env: dict[str, str] | None) -> bytes:
    source = os.environ if env is None else env
    raw = source.get(LEAN_REPLAY_KEY_ENV, "")
    if len(raw.encode("utf-8")) < 32:
        raise AristotleClientError(
            f"{LEAN_REPLAY_KEY_ENV} must be configured with at least 32 bytes"
        )
    return raw.encode("utf-8")


def seal_local_lean_replay_attestation(
    attestation: LocalLeanReplayAttestation, *, env: dict[str, str] | None = None
) -> LocalLeanReplayAttestation:
    """Seal an attestation with an HMAC under the local checker key."""
    key = _lean_replay_key(env)
    payload = canonical_json(attestation.sealed_record()).encode("utf-8")
    signature = hmac.new(key, payload, hashlib.sha256).hexdigest()
    fingerprint = hashlib.sha256(key).hexdigest()[:16]
    return LocalLeanReplayAttestation(
        **attestation.sealed_record(), key_fingerprint=fingerprint, signature=signature
    )


def verify_local_lean_replay_attestation(
    attestation: LocalLeanReplayAttestation, *, env: dict[str, str] | None = None
) -> bool:
    """True only if the attestation carries a valid seal under the checker key."""
    if not isinstance(attestation, LocalLeanReplayAttestation):
        return False
    if not attestation.signature or not is_sha256(attestation.artifact_hash):
        return False
    try:
        key = _lean_replay_key(env)
    except AristotleClientError:
        return False
    payload = canonical_json(attestation.sealed_record()).encode("utf-8")
    expected = hmac.new(key, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, attestation.signature)


@dataclass(frozen=True)
class LocalReplayResult:
    """The outcome of binding a quarantined artifact to an independent checker."""

    job_id: str
    verified: bool
    attestation: LocalLeanReplayAttestation | None = None
    detail: str = ""

    @property
    def promotable(self) -> bool:
        # Promotion requires a *sealed, artifact-bound* local attestation; the
        # vendor never contributes trust.
        return bool(self.verified and self.attestation is not None)


def _reject_unsafe_member_name(name: str) -> str:
    normalized = name.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or normalized.startswith("/"):
        raise UnsafeArchiveError(f"absolute path in archive member: {name!r}")
    parts = [p for p in pure.parts if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise UnsafeArchiveError(f"parent-directory traversal in archive member: {name!r}")
    return "/".join(parts)


def _target_within(dest: Path, relative: str) -> Path:
    target = (dest / relative).resolve()
    if target != dest and dest not in target.parents:
        raise UnsafeArchiveError(f"archive member escapes quarantine: {relative!r}")
    return target


def hash_quarantine_tree(root: Path) -> str:
    """Content hash over every regular file under ``root`` (symlinks excluded).

    Deterministic and reproducible from the directory alone, so an independent
    local verifier can bind its attestation to the exact quarantined artifact.
    """
    root = Path(root).resolve()
    entries: list[list[str]] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink()):
        rel = path.resolve().relative_to(root)
        entries.append([str(rel), sha256_bytes(path.read_bytes())])
    return content_id({"tree": entries})


def scan_quarantine_tree(
    root: Path,
    *,
    max_entries: int = _DEFAULT_MAX_ENTRIES,
    max_entry_bytes: int = _DEFAULT_MAX_ENTRY_BYTES,
    max_total_bytes: int = _DEFAULT_MAX_TOTAL_BYTES,
) -> tuple[tuple[Path, ...], int]:
    """Validate a directory tree written by an external tool (e.g. the SDK download).

    Rejects symlinks, entries that escape ``root`` after resolving, and any tree
    exceeding the entry-count / per-file / total-size ceilings. Returns the
    regular files and their total size.
    """
    root = Path(root).resolve()
    files: list[Path] = []
    total = 0
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise UnsafeArchiveError(f"symlink in downloaded tree: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise UnsafeArchiveError(f"non-regular file in downloaded tree: {path}")
        resolved = path.resolve()
        if root not in resolved.parents:
            raise UnsafeArchiveError(f"downloaded file escapes quarantine: {path}")
        size = path.stat().st_size
        if size > max_entry_bytes:
            raise UnsafeArchiveError(f"downloaded file too large: {path}")
        total += size
        if total > max_total_bytes:
            raise UnsafeArchiveError("downloaded tree exceeds total-size budget")
        files.append(resolved)
        if len(files) > max_entries:
            raise UnsafeArchiveError(f"downloaded tree has too many entries (>{max_entries})")
    return tuple(files), total


def safe_extract_archive(
    archive_bytes: bytes,
    dest: Path,
    *,
    max_entries: int = _DEFAULT_MAX_ENTRIES,
    max_entry_bytes: int = _DEFAULT_MAX_ENTRY_BYTES,
    max_total_bytes: int = _DEFAULT_MAX_TOTAL_BYTES,
) -> tuple[tuple[Path, ...], int]:
    """Safely extract a zip or tar(.gz) archive into ``dest``.

    Rejects absolute paths, ``..`` traversal, symlinks/hardlinks/special files,
    oversized entries, and archive bombs. Returns ``(files, total_bytes)``.
    """
    dest.mkdir(parents=True, exist_ok=True)
    dest = dest.resolve()
    buffer = io.BytesIO(archive_bytes)
    if zipfile.is_zipfile(buffer):
        return _extract_zip(buffer, dest, max_entries, max_entry_bytes, max_total_bytes)
    buffer.seek(0)
    try:
        tar = tarfile.open(fileobj=buffer, mode="r:*")
    except tarfile.TarError as exc:
        raise UnsafeArchiveError(f"unrecognized or corrupt archive: {exc}") from exc
    with tar:
        return _extract_tar(tar, dest, max_entries, max_entry_bytes, max_total_bytes)


def _extract_zip(buffer, dest, max_entries, max_entry_bytes, max_total_bytes):
    files: list[Path] = []
    total = 0
    with zipfile.ZipFile(buffer) as zf:
        infos = zf.infolist()
        if len(infos) > max_entries:
            raise UnsafeArchiveError(f"archive has too many entries ({len(infos)})")
        for info in infos:
            relative = _reject_unsafe_member_name(info.filename)
            if not relative:
                continue
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise UnsafeArchiveError(f"symlink in archive: {info.filename!r}")
            target = _target_within(dest, relative)
            if info.is_dir() or info.filename.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
                continue
            if info.file_size > max_entry_bytes:
                raise UnsafeArchiveError(f"archive entry too large: {info.filename!r}")
            total += info.file_size
            if total > max_total_bytes:
                raise UnsafeArchiveError("archive exceeds total-size budget")
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src:
                data = src.read(max_entry_bytes + 1)
            if len(data) > max_entry_bytes:
                raise UnsafeArchiveError(f"archive entry exceeded size on read: {info.filename!r}")
            target.write_bytes(data)
            files.append(target)
    return tuple(files), total


def _extract_tar(tar, dest, max_entries, max_entry_bytes, max_total_bytes):
    files: list[Path] = []
    total = 0
    members = tar.getmembers()
    if len(members) > max_entries:
        raise UnsafeArchiveError(f"archive has too many entries ({len(members)})")
    for member in members:
        relative = _reject_unsafe_member_name(member.name)
        if not relative:
            continue
        if member.issym() or member.islnk():
            raise UnsafeArchiveError(f"link in archive: {member.name!r}")
        if member.ischr() or member.isblk() or member.isfifo() or member.isdev():
            raise UnsafeArchiveError(f"special file in archive: {member.name!r}")
        target = _target_within(dest, relative)
        if member.isdir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if not member.isfile():
            raise UnsafeArchiveError(f"unsupported archive member type: {member.name!r}")
        if member.size > max_entry_bytes:
            raise UnsafeArchiveError(f"archive entry too large: {member.name!r}")
        total += member.size
        if total > max_total_bytes:
            raise UnsafeArchiveError("archive exceeds total-size budget")
        target.parent.mkdir(parents=True, exist_ok=True)
        extracted = tar.extractfile(member)
        data = b"" if extracted is None else extracted.read(max_entry_bytes + 1)
        if len(data) > max_entry_bytes:
            raise UnsafeArchiveError(f"archive entry exceeded size on read: {member.name!r}")
        target.write_bytes(data)
        files.append(target)
    return tuple(files), total


@dataclass
class AristotleApiClient:
    """Route to Aristotle as a candidate worker; verify locally before any trust."""

    transport: AristotleTransport
    quarantine_root: Path
    routing: AristotleRouting = field(default_factory=AristotleRouting)
    max_entries: int = _DEFAULT_MAX_ENTRIES
    max_entry_bytes: int = _DEFAULT_MAX_ENTRY_BYTES
    max_total_bytes: int = _DEFAULT_MAX_TOTAL_BYTES

    def submit(self, request: AristotleRequest) -> str:
        # Licensing/confidentiality gate before any source packet leaves the host.
        prepared = self.routing.prepare_request(request)
        try:
            job_id = self.transport.submit(prepared.to_dict())
        except Exception as exc:  # transport-specific errors normalized here
            raise AristotleTransportError(f"submit failed: {exc}") from exc
        # A provider-returned job id is used as a filesystem path later; it must be
        # a strict safe token or the download quarantine could be escaped.
        return validate_job_id(job_id if isinstance(job_id, str) else "")

    def poll(self, job_id: str) -> AristotleStatus:
        validate_job_id(job_id)
        try:
            record = self.transport.poll(job_id)
        except Exception as exc:
            raise AristotleTransportError(f"poll failed: {exc}") from exc
        if not isinstance(record, dict):
            raise AristotleTransportError("transport returned a non-object poll record")
        raw = str(record.get("status", "")).strip().lower()
        return AristotleStatus(
            job_id=job_id,
            raw_status=raw,
            vendor_reports_complete=raw in VENDOR_COMPLETE_STATUSES,
            failed=raw in VENDOR_FAILURE_STATUSES,
            detail={k: v for k, v in record.items() if k != "status"},
        )

    def _resolve_quarantine_dir(self, job_id: str) -> Path:
        """Resolve a per-job quarantine dir with no symlink following (defect 4.8)."""
        return resolve_quarantine_dir(self.quarantine_root, job_id)

    def download(self, job_id: str, *, vendor_status: str = "") -> AristotleArtifact:
        quarantine_dir = self._resolve_quarantine_dir(job_id)
        try:
            archive_bytes = self.transport.download(job_id)
        except Exception as exc:
            raise AristotleTransportError(f"download failed: {exc}") from exc
        if not isinstance(archive_bytes, (bytes, bytearray)):
            raise AristotleTransportError("transport returned non-bytes archive")
        files, total = safe_extract_archive(
            bytes(archive_bytes), quarantine_dir,
            max_entries=self.max_entries, max_entry_bytes=self.max_entry_bytes,
            max_total_bytes=self.max_total_bytes,
        )
        raw = vendor_status.strip().lower()
        return AristotleArtifact(
            job_id=job_id,
            vendor_status=raw,
            vendor_reports_complete=raw in VENDOR_COMPLETE_STATUSES,
            quarantine_dir=quarantine_dir,
            extracted_files=files,
            total_bytes=total,
            promotable=False,  # never on arrival
        )

    @staticmethod
    def artifact_hash(artifact: AristotleArtifact) -> str:
        """Content hash over the quarantined tree, binding an attestation to it."""
        return hash_quarantine_tree(artifact.quarantine_dir)

    def bind_local_replay(
        self,
        artifact: AristotleArtifact,
        verifier: Callable[[Path], "LocalLeanReplayAttestation | None"],
        *,
        expected_claim_id: str | None = None,
        env: dict[str, str] | None = None,
    ) -> LocalReplayResult:
        """Bind a quarantined artifact to an independent, sealed local Lean replay.

        The vendor never contributes trust. The verifier MUST return a sealed
        :class:`LocalLeanReplayAttestation` bound to this exact quarantined
        artifact; a boolean, string, dict, or any other truthy object is rejected.
        A verifier error is a rejection, never a promotion.
        """
        return verify_local_replay(
            artifact, verifier, expected_claim_id=expected_claim_id, env=env,
        )


def verify_local_replay(
    artifact: AristotleArtifact,
    verifier: Callable[[Path], "LocalLeanReplayAttestation | None"],
    *,
    expected_claim_id: str | None = None,
    env: dict[str, str] | None = None,
) -> LocalReplayResult:
    """Trusted-replay gate shared by every Aristotle client (REST or official SDK).

    Promotion requires a sealed, artifact-bound :class:`LocalLeanReplayAttestation`
    from the local verifier; the vendor status never contributes trust.
    """
    # Re-scan the tree immediately before replay: a symlink/escape/bomb that
    # appeared after download (or was missed) is a rejection, never a pass.
    try:
        scan_quarantine_tree(artifact.quarantine_dir)
    except UnsafeArchiveError as exc:
        return LocalReplayResult(
            job_id=artifact.job_id, verified=False,
            detail=f"pre-replay quarantine scan rejected the tree: {exc}",
        )
    computed = hash_quarantine_tree(artifact.quarantine_dir)
    try:
        outcome = verifier(artifact.quarantine_dir)
    except Exception as exc:  # a failing local check is a rejection, never a pass
        return LocalReplayResult(
            job_id=artifact.job_id, verified=False,
            detail=f"local verifier raised: {type(exc).__name__}: {exc}",
        )
    if not isinstance(outcome, LocalLeanReplayAttestation):
        return LocalReplayResult(
            job_id=artifact.job_id, verified=False,
            detail="verifier did not return a sealed LocalLeanReplayAttestation",
        )
    if not verify_local_lean_replay_attestation(outcome, env=env):
        return LocalReplayResult(
            job_id=artifact.job_id, verified=False,
            detail="local replay attestation seal is invalid",
        )
    if outcome.artifact_hash != computed:
        return LocalReplayResult(
            job_id=artifact.job_id, verified=False,
            detail="attestation is not bound to this quarantined artifact",
        )
    if expected_claim_id is not None and outcome.claim_id != expected_claim_id:
        return LocalReplayResult(
            job_id=artifact.job_id, verified=False,
            detail="attestation claim id does not match the expected claim",
        )
    return LocalReplayResult(
        job_id=artifact.job_id, verified=True, attestation=outcome,
        detail="sealed, artifact-bound local Lean replay verified",
    )


class HttpAristotleTransport:  # pragma: no cover - requires network + credentials
    """Live HTTP transport. Reads the API key from the environment only.

    Requires the ``requests`` extra and ``ARISTOTLE_API_KEY`` in the environment.
    No network access occurs at import time.
    """

    def __init__(self, base_url: str, *, env: dict[str, str] | None = None,
                 timeout_s: float = 60.0) -> None:
        from egmra.config import EgmraConfig

        if not base_url.lower().startswith("https://"):
            raise AristotleClientError("Aristotle base_url must be https://")
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self._api_key = EgmraConfig.secret("ARISTOTLE_API_KEY", env=env)
        if not self._api_key:
            raise AristotleClientError(
                "ARISTOTLE_API_KEY is not configured; set it in the environment"
            )

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}",
                "Accept": "application/json"}

    def submit(self, payload: dict[str, Any]) -> str:
        import requests

        resp = requests.post(f"{self.base_url}/jobs", json=payload,
                             headers=self._headers(), timeout=self.timeout_s,
                             allow_redirects=False)
        resp.raise_for_status()
        return str(resp.json()["job_id"])

    def poll(self, job_id: str) -> dict[str, Any]:
        import requests

        quoted = quote(validate_job_id(job_id), safe="")
        resp = requests.get(f"{self.base_url}/jobs/{quoted}",
                            headers=self._headers(), timeout=self.timeout_s,
                            allow_redirects=False)
        resp.raise_for_status()
        return dict(resp.json())

    def download(self, job_id: str) -> bytes:
        import requests

        quoted = quote(validate_job_id(job_id), safe="")
        resp = requests.get(f"{self.base_url}/jobs/{quoted}/artifact",
                            headers=self._headers(), timeout=self.timeout_s,
                            allow_redirects=False)
        resp.raise_for_status()
        return resp.content
