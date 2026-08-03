"""Durable immutable computational jobs and replay (spec §6.8).

Successful jobs are stored as atomic, content-addressed bundles containing the
validated specification, exact source, output, metadata, and captured stdout.
Service startup verifies and reloads those bundles so replay survives restart.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import tempfile
import time
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable

from egmra.compute.artifact import CertificateReport, ComputationalArtifact, ReplayReport
from egmra.compute.sandbox import ContainerSandbox, RestrictedPythonExecutor, SandboxResult
from egmra.compute.spec import ExperimentSpec
from egmra.provenance.hashing import canonical_json, content_id, sha256_hex

Checker = Callable[[ComputationalArtifact, Any], bool]
_ARTIFACT_DIR_RE = re.compile(r"^art_[0-9a-f]{16}$")
_CERTIFICATE_FILE_RE = re.compile(
    r"^cert_(art_[0-9a-f]{16})_([0-9a-f]{64})\.json$"
)
_BUNDLE_FORMAT = "egmra.compute.bundle.v1"
_CERTIFICATE_FORMAT = "egmra.compute.certificate.v1"
_MAX_CERTIFICATE_BYTES = 1_000_000
_BUNDLE_FILES = {
    "artifact.json": 1_000_000,
    "code.py": 256 * 1024,
    "job.json": 1_000_000,
    "output.json": 16 * 1024**2,
    "spec.json": 1_000_000,
    "stdout.log": 16 * 1024**2,
}


class PersistenceError(ValueError):
    """A stored computation bundle failed an integrity or path-safety check."""


@dataclass(frozen=True)
class TrustedCertificateChecker:
    """A checker admitted by trusted service configuration, not by a job caller.

    ``implementation_hash`` is the deployment-controlled digest of the checker
    implementation and its immutable dependencies.  It is deliberately
    explicit: production packaging can attest non-Python checkers as well as
    local callables.  The complete identity is persisted with every result and
    must match before the result is replayed after restart.
    """

    checker_id: str
    version: str
    implementation_hash: str
    check: Checker = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", self.checker_id):
            raise ValueError("checker_id must be a stable non-option identifier")
        if not isinstance(self.version, str) or not self.version.strip() \
                or len(self.version) > 128:
            raise ValueError("checker version must be a non-empty stable identifier")
        if not re.fullmatch(r"[0-9a-f]{64}", self.implementation_hash):
            raise ValueError("checker implementation_hash must be a lowercase SHA-256")
        if not callable(self.check):
            raise TypeError("trusted certificate checker must be callable")

    @property
    def attestation_hash(self) -> str:
        return content_id(
            {
                "checker_id": self.checker_id,
                "version": self.version,
                "implementation_hash": self.implementation_hash,
            }
        )


@dataclass
class _Job:
    job_id: str
    spec: ExperimentSpec
    code: str
    status: str
    artifact: ComputationalArtifact | None = None
    error: str = ""


@dataclass
class ComputeService:
    store_dir: Path | None = None
    sandbox: Any = field(default_factory=RestrictedPythonExecutor)
    certificate_checkers: Mapping[str, TrustedCertificateChecker] = field(
        default_factory=dict
    )
    jobs: dict[str, _Job] = field(default_factory=dict)
    artifacts: dict[str, ComputationalArtifact] = field(default_factory=dict)
    _code: dict[str, str] = field(default_factory=dict)
    _store_identity: tuple[int, int] | None = field(default=None, init=False, repr=False)
    _configuration_locked: bool = field(default=False, init=False, repr=False)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"sandbox", "certificate_checkers", "store_dir"} \
                and getattr(self, "_configuration_locked", False):
            raise AttributeError(f"compute service configuration {name!r} is immutable")
        object.__setattr__(self, name, value)

    def __post_init__(self) -> None:
        _require_trusted_executor(self.sandbox)
        checkers: dict[str, TrustedCertificateChecker] = {}
        for checker_id, checker in dict(self.certificate_checkers).items():
            if not isinstance(checker, TrustedCertificateChecker):
                raise TypeError(
                    "certificate_checkers values must be TrustedCertificateChecker records"
                )
            if checker_id != checker.checker_id:
                raise ValueError("certificate checker registry key/identity mismatch")
            checkers[checker_id] = checker
        self.certificate_checkers = MappingProxyType(checkers)
        if self.store_dir is None:
            self._configuration_locked = True
            return
        root = Path(self.store_dir).absolute()
        if root.exists() and root.is_symlink():
            raise PersistenceError("compute store integrity failure: root is a symlink")
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not root.is_dir():
            raise PersistenceError("compute store integrity failure: root is not a directory")
        self.store_dir = root
        info = root.lstat()
        self._store_identity = (info.st_dev, info.st_ino)
        self._assert_store_integrity()
        self._cleanup_staging(root)
        for child in sorted(root.iterdir(), key=lambda path: path.name):
            if not _ARTIFACT_DIR_RE.fullmatch(child.name):
                continue
            job, artifact = self._load_bundle(child)
            existing_job = self.jobs.get(job.job_id)
            existing_artifact = self.artifacts.get(artifact.artifact_id)
            if existing_job is not None or existing_artifact is not None:
                raise PersistenceError("compute store integrity failure: duplicate bundle identity")
            self.jobs[job.job_id] = job
            self.artifacts[artifact.artifact_id] = artifact
            self._code[job.job_id] = job.code
        for child in sorted(root.iterdir(), key=lambda path: path.name):
            if _CERTIFICATE_FILE_RE.fullmatch(child.name):
                self._load_certificate_record(child)
        self._configuration_locked = True

    # ── submit / poll / artifact ─────────────────────────────────────────────

    def submit_experiment(
        self,
        spec: ExperimentSpec,
        code: str,
        *,
        claimed_classification: str = "heuristic_numerical",
        certificate: Any = None,
    ) -> str:
        job_id = _job_id(spec, code)
        job = _Job(job_id=job_id, spec=spec, code=code, status="running")
        self.jobs[job_id] = job
        self._code[job_id] = code
        result = self.sandbox.run(spec, code)
        if not result.ok:
            job.status = "failed"
            job.error = result.stderr or ("timeout" if result.timed_out else "execution failed")
            return job_id
        if not result.environment_hash:
            job.status = "failed"
            job.error = "executor omitted its measured environment identity"
            return job_id
        try:
            artifact = self._freeze_artifact(
                spec, code, result, claimed_classification, certificate
            )
        except (TypeError, ValueError) as exc:
            job.status = "failed"
            job.error = f"invalid computation output: {exc}"
            return job_id
        if self.store_dir is not None:
            try:
                self._persist(job, artifact, result)
            except PersistenceError as exc:
                job.status = "failed"
                job.error = str(exc)
                raise
        # Publish only after durable storage succeeds.  A storage failure must
        # never leave an in-memory artifact that looks committed.
        job.artifact = artifact
        job.status = "done"
        self.artifacts[artifact.artifact_id] = artifact
        return job_id

    def _freeze_artifact(
        self,
        spec: ExperimentSpec,
        code: str,
        result: SandboxResult,
        claimed_classification: str,
        certificate: Any,
    ) -> ComputationalArtifact:
        output_hash = sha256_hex(canonical_json(result.output))
        code_hash = spec.code_hash(code)
        artifact_id = _artifact_id(
            spec.spec_hash(), code_hash, output_hash, result.environment_hash
        )
        return ComputationalArtifact(
            artifact_id=artifact_id,
            spec_hash=spec.spec_hash(),
            code_hash=code_hash,
            claimed_classification=claimed_classification,
            output=result.output,
            output_hash=output_hash,
            arithmetic_mode=spec.arithmetic_mode,
            # Coverage is part of the immutable submitted job.  Untrusted code
            # may echo it for diagnostics but cannot elevate its own evidence.
            coverage=spec.coverage,
            # A submitted object is not a checked certificate.  Only an
            # attested configured checker may set certificate state below.
            certificate_present=False,
            checker_passed=None,
            seed=spec.seed,
            environment_hash=result.environment_hash,
            stdout=result.stdout,
            created_at=_now(),
        )

    def poll(self, job_id: str) -> str:
        return self.jobs[job_id].status

    def artifact(self, job_id: str) -> ComputationalArtifact:
        job = self.jobs[job_id]
        if job.artifact is None:
            raise RuntimeError(f"job {job_id} has no artifact (status={job.status}): {job.error}")
        return job.artifact

    # ── replay ────────────────────────────────────────────────────────────────

    def replay(
        self,
        artifact_id: str,
        *,
        sandbox: Any = None,
        environment_label: str = "replay",
    ) -> ReplayReport:
        # Retained only for source compatibility.  A caller-provided string is
        # not evidence of an independent environment and is intentionally ignored.
        del environment_label
        artifact = self.artifacts[artifact_id]
        job = next(
            (
                candidate
                for candidate in self.jobs.values()
                if candidate.artifact and candidate.artifact.artifact_id == artifact_id
            ),
            None,
        )
        if job is None:
            raise RuntimeError("no persisted job for artifact")
        executor = sandbox or self.sandbox
        _require_trusted_executor(executor)
        result = executor.run(job.spec, job.code)
        if not result.ok or not result.environment_hash:
            return ReplayReport(
                artifact_id,
                False,
                False,
                artifact.output_hash,
                "",
                result.environment_hash,
                f"replay execution failed: {result.stderr}",
                artifact.environment_hash,
            )
        replay_hash = sha256_hex(canonical_json(result.output))
        matches = replay_hash == artifact.output_hash
        independent = result.environment_hash != artifact.environment_hash
        detail = "output hashes match" if matches else "output diverged on replay"
        if not independent:
            detail += "; replay used the same measured environment"
        return ReplayReport(
            artifact_id,
            True,
            matches,
            artifact.output_hash,
            replay_hash,
            result.environment_hash,
            detail,
            artifact.environment_hash,
        )

    # ── certificate ──────────────────────────────────────────────────────────

    def verify_certificate(
        self,
        artifact_id: str,
        *,
        checker_id: str,
        certificate: Any,
    ) -> CertificateReport:
        artifact = self.artifacts[artifact_id]
        job = self._job_for_artifact(artifact_id)
        if not job.spec.certificate_kind:
            return CertificateReport(
                artifact_id, checker_id, False, "experiment spec has no certificate kind"
            )
        if not job.spec.checker_id or checker_id != job.spec.checker_id:
            return CertificateReport(
                artifact_id, checker_id, False, "checker does not match immutable experiment spec"
            )
        checker = self.certificate_checkers.get(checker_id)
        if checker is None:
            return CertificateReport(
                artifact_id, checker_id, False, "checker is not in trusted service configuration"
            )
        if certificate is None:
            return CertificateReport(
                artifact_id, checker_id, False, "certificate payload is missing"
            )
        try:
            certificate_payload = canonical_json(certificate)
            if len(certificate_payload.encode("utf-8")) > _MAX_CERTIFICATE_BYTES:
                raise ValueError("certificate exceeds persistence limit")
            checked_certificate = _loads_json(certificate_payload)
        except (TypeError, ValueError) as exc:
            return CertificateReport(
                artifact_id, checker_id, False, f"invalid certificate payload: {exc}"
            )
        try:
            raw_artifact = replace(
                artifact, certificate_present=False, checker_passed=None
            )
            passed = bool(checker.check(raw_artifact, checked_certificate))
        except Exception as exc:  # a failing checker is a failed certificate
            passed = False
            detail = f"checker error: {exc}"
        else:
            detail = "certificate checked" if passed else "certificate rejected"
        record = {
            "format": _CERTIFICATE_FORMAT,
            "artifact_id": artifact_id,
            "checker_id": checker_id,
            "checker_attestation": checker.attestation_hash,
            "certificate_kind": job.spec.certificate_kind,
            "certificate_hash": sha256_hex(certificate_payload),
            "certificate": checked_certificate,
            "passed": passed,
        }
        if self.store_dir is not None:
            self._persist_certificate_record(record)
        if not passed:
            return CertificateReport(artifact_id, checker_id, False, detail)
        checked_artifact = replace(
            artifact, certificate_present=True, checker_passed=passed
        )
        self._replace_artifact(artifact_id, checked_artifact)
        return CertificateReport(
            artifact_id,
            checker_id,
            passed,
            detail,
        )

    # ── persistence ──────────────────────────────────────────────────────────

    def _persist(
        self, job: _Job, artifact: ComputationalArtifact, result: SandboxResult
    ) -> None:
        if self.store_dir is None:
            raise PersistenceError("compute persistence store is not configured")
        self._assert_store_integrity()
        root = Path(self.store_dir)
        target = root / artifact.artifact_id
        if target.exists():
            if target.is_symlink():
                raise PersistenceError("compute store integrity failure: artifact path is a symlink")
            loaded_job, loaded_artifact = self._load_bundle(target)
            if loaded_job.job_id != job.job_id or loaded_artifact.to_dict() != artifact.to_dict():
                raise PersistenceError("compute store integrity failure: content-address collision")
            return

        stage = Path(tempfile.mkdtemp(prefix=".tmp-", dir=root))
        marker = stage / ".egmra-staging"
        try:
            _write_new_file(marker, _BUNDLE_FORMAT)
            payloads = {
                "artifact.json": canonical_json(artifact.to_dict()),
                "code.py": job.code,
                "job.json": canonical_json({"job_id": job.job_id, "status": "done"}),
                "output.json": canonical_json(result.output),
                "spec.json": canonical_json(job.spec.to_dict()),
                "stdout.log": result.stdout,
            }
            for name, payload in payloads.items():
                if len(payload.encode("utf-8")) > _BUNDLE_FILES[name]:
                    raise PersistenceError(
                        f"compute store integrity failure: {name} exceeds bundle limit"
                    )
                _write_new_file(stage / name, payload)
            manifest = {
                "format": _BUNDLE_FORMAT,
                "artifact_id": artifact.artifact_id,
                "job_id": job.job_id,
                "files": {
                    name: sha256_hex(payload) for name, payload in sorted(payloads.items())
                },
            }
            _write_new_file(stage / "manifest.json", canonical_json(manifest))
            marker.unlink()
            _fsync_directory(stage)
            os.replace(stage, target)
            _fsync_directory(root)
        finally:
            if stage.exists() and not stage.is_symlink():
                shutil.rmtree(stage)

    def _load_bundle(self, directory: Path) -> tuple[_Job, ComputationalArtifact]:
        if directory.is_symlink() or not directory.is_dir():
            raise PersistenceError("compute store integrity failure: artifact path is not a real directory")
        manifest = _load_json_object(directory / "manifest.json", maximum=1_000_000)
        if set(manifest) != {"format", "artifact_id", "job_id", "files"} \
                or manifest.get("format") != _BUNDLE_FORMAT:
            raise PersistenceError("compute store integrity failure: malformed manifest")
        if manifest["artifact_id"] != directory.name:
            raise PersistenceError("compute store integrity failure: manifest/path identity mismatch")
        files = manifest.get("files")
        if not isinstance(files, dict) or set(files) != set(_BUNDLE_FILES):
            raise PersistenceError("compute store integrity failure: incomplete file manifest")

        payloads: dict[str, str] = {}
        for name, maximum in _BUNDLE_FILES.items():
            payload = _read_regular_text(directory / name, maximum=maximum)
            if not isinstance(files.get(name), str) or sha256_hex(payload) != files[name]:
                raise PersistenceError(f"compute store integrity failure: {name} hash mismatch")
            payloads[name] = payload

        spec_payload = _loads_json(payloads["spec.json"])
        artifact_payload = _loads_json(payloads["artifact.json"])
        job_payload = _loads_json(payloads["job.json"])
        output = _loads_json(payloads["output.json"])
        if not isinstance(spec_payload, dict) or not isinstance(artifact_payload, dict) \
                or not isinstance(job_payload, dict):
            raise PersistenceError("compute store integrity failure: bundle records must be objects")
        try:
            spec = ExperimentSpec.from_dict(spec_payload)
        except (TypeError, ValueError) as exc:
            raise PersistenceError(f"compute store integrity failure: invalid spec: {exc}") from exc
        code = payloads["code.py"]
        code_hash = spec.code_hash(code)
        output_hash = sha256_hex(canonical_json(output))
        environment_hash = artifact_payload.get("environment_hash")
        if not isinstance(environment_hash, str) \
                or not re.fullmatch(r"[0-9a-f]{64}", environment_hash):
            raise PersistenceError("compute store integrity failure: invalid environment hash")
        artifact_id = _artifact_id(
            spec.spec_hash(), code_hash, output_hash, environment_hash
        )
        job_id = _job_id(spec, code)
        if artifact_id != directory.name or manifest["artifact_id"] != artifact_id:
            raise PersistenceError("compute store integrity failure: artifact identity mismatch")
        if job_id != manifest["job_id"] or job_payload != {"job_id": job_id, "status": "done"}:
            raise PersistenceError("compute store integrity failure: job identity mismatch")

        try:
            artifact = ComputationalArtifact(
                artifact_id=artifact_payload["artifact_id"],
                spec_hash=artifact_payload["spec_hash"],
                code_hash=artifact_payload["code_hash"],
                claimed_classification=artifact_payload["claimed_classification"],
                output=output,
                output_hash=artifact_payload["output_hash"],
                arithmetic_mode=artifact_payload["arithmetic_mode"],
                coverage=artifact_payload["coverage"],
                certificate_present=artifact_payload["certificate_present"],
                checker_passed=artifact_payload["checker_passed"],
                seed=artifact_payload["seed"],
                environment_hash=artifact_payload["environment_hash"],
                stdout=payloads["stdout.log"],
                created_at=artifact_payload["created_at"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise PersistenceError(
                f"compute store integrity failure: invalid artifact metadata: {exc}"
            ) from exc
        if artifact.to_dict() != artifact_payload:
            raise PersistenceError("compute store integrity failure: artifact metadata mismatch")
        if artifact.artifact_id != artifact_id or artifact.spec_hash != spec.spec_hash() \
                or artifact.code_hash != code_hash or artifact.output_hash != output_hash:
            raise PersistenceError("compute store integrity failure: artifact hash mismatch")
        if artifact.certificate_present or artifact.checker_passed is not None:
            raise PersistenceError(
                "compute store integrity failure: base artifact contains forged checker state"
            )
        job = _Job(job_id=job_id, spec=spec, code=code, status="done", artifact=artifact)
        return job, artifact

    def _persist_certificate_record(self, record: Mapping[str, Any]) -> None:
        if self.store_dir is None:
            raise PersistenceError("compute persistence store is not configured")
        self._assert_store_integrity()
        payload = canonical_json(dict(record))
        if len(payload.encode("utf-8")) > _MAX_CERTIFICATE_BYTES:
            raise PersistenceError("compute store integrity failure: certificate record is too large")
        digest = sha256_hex(payload)
        path = Path(self.store_dir) / f"cert_{record['artifact_id']}_{digest}.json"
        if path.exists():
            if _read_regular_text(path, maximum=_MAX_CERTIFICATE_BYTES) != payload:
                raise PersistenceError(
                    "compute store integrity failure: certificate content-address collision"
                )
            return
        _write_new_file(path, payload)
        _fsync_directory(Path(self.store_dir))

    def _load_certificate_record(self, path: Path) -> None:
        match = _CERTIFICATE_FILE_RE.fullmatch(path.name)
        if match is None:
            raise PersistenceError("compute store integrity failure: malformed certificate path")
        payload = _read_regular_text(path, maximum=_MAX_CERTIFICATE_BYTES)
        if sha256_hex(payload) != match.group(2):
            raise PersistenceError(
                "compute store integrity failure: certificate record identity mismatch"
            )
        record = _loads_json(payload)
        required = {
            "format", "artifact_id", "checker_id", "checker_attestation",
            "certificate_kind", "certificate_hash", "certificate", "passed",
        }
        if not isinstance(record, dict) or set(record) != required \
                or record.get("format") != _CERTIFICATE_FORMAT:
            raise PersistenceError(
                "compute store integrity failure: malformed certificate record"
            )
        artifact_id = record.get("artifact_id")
        if artifact_id != match.group(1) or artifact_id not in self.artifacts:
            raise PersistenceError(
                "compute store integrity failure: certificate artifact mismatch"
            )
        checker_id = record.get("checker_id")
        if not isinstance(checker_id, str):
            raise PersistenceError(
                "compute store integrity failure: persisted certificate checker is unavailable"
            )
        checker = self.certificate_checkers.get(checker_id)
        if checker is None:
            raise PersistenceError(
                "compute store integrity failure: persisted certificate checker is unavailable"
            )
        job = self._job_for_artifact(artifact_id)
        if checker_id != job.spec.checker_id \
                or record.get("certificate_kind") != job.spec.certificate_kind \
                or record.get("checker_attestation") != checker.attestation_hash:
            raise PersistenceError(
                "compute store integrity failure: certificate checker attestation mismatch"
            )
        certificate = record.get("certificate")
        certificate_payload = canonical_json(certificate)
        if record.get("certificate_hash") != sha256_hex(certificate_payload) \
                or not isinstance(record.get("passed"), bool):
            raise PersistenceError(
                "compute store integrity failure: invalid certificate record fields"
            )
        try:
            raw_artifact = replace(
                self.artifacts[artifact_id], certificate_present=False, checker_passed=None
            )
            replayed_pass = bool(checker.check(raw_artifact, certificate))
        except Exception:
            replayed_pass = False
        if replayed_pass != record["passed"]:
            raise PersistenceError(
                "compute store integrity failure: certificate checker replay diverged"
            )
        if replayed_pass:
            checked_artifact = replace(
                self.artifacts[artifact_id], certificate_present=True, checker_passed=True
            )
            self._replace_artifact(artifact_id, checked_artifact)

    def _job_for_artifact(self, artifact_id: str) -> _Job:
        for job in self.jobs.values():
            if job.artifact is not None and job.artifact.artifact_id == artifact_id:
                return job
        raise RuntimeError("no persisted job for artifact")

    def _replace_artifact(
        self, artifact_id: str, artifact: ComputationalArtifact
    ) -> None:
        self.artifacts[artifact_id] = artifact
        for job in self.jobs.values():
            if job.artifact is not None and job.artifact.artifact_id == artifact_id:
                job.artifact = artifact

    @staticmethod
    def _cleanup_staging(root: Path) -> None:
        for child in root.iterdir():
            if not child.name.startswith(".tmp-"):
                continue
            if child.is_symlink() or not child.is_dir() or not (child / ".egmra-staging").is_file():
                raise PersistenceError("compute store integrity failure: unsafe staging entry")
            shutil.rmtree(child)

    def _assert_store_integrity(self) -> None:
        if self.store_dir is None or self._store_identity is None:
            return
        root = Path(self.store_dir)
        try:
            info = root.lstat()
        except OSError as exc:
            raise PersistenceError("compute store integrity failure: root disappeared") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) \
                or (info.st_dev, info.st_ino) != self._store_identity:
            raise PersistenceError("compute store integrity failure: root changed after startup")


def _job_id(spec: ExperimentSpec, code: str) -> str:
    return "job_" + content_id(
        {"spec": spec.spec_hash(), "code": spec.code_hash(code), "seed": spec.seed}
    )[:16]


def _require_trusted_executor(executor: Any) -> None:
    # Subclasses can override ``run`` and self-attest an arbitrary environment,
    # so the replay trust boundary admits only the two audited concrete types.
    if type(executor) not in {RestrictedPythonExecutor, ContainerSandbox}:
        raise ValueError("compute/replay requires a trusted executor implementation")


def _artifact_id(
    spec_hash: str, code_hash: str, output_hash: str, environment_hash: str
) -> str:
    return "art_" + content_id(
        {
            "spec": spec_hash,
            "code": code_hash,
            "out": output_hash,
            "environment": environment_hash,
        }
    )[:16]


def _write_new_file(path: Path, payload: str) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", closefd=False) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _read_regular_text(path: Path, *, maximum: int) -> str:
    if path.is_symlink():
        raise PersistenceError(f"compute store integrity failure: {path.name} is a symlink")
    try:
        info = path.stat()
    except OSError as exc:
        raise PersistenceError(f"compute store integrity failure: missing {path.name}") from exc
    if not stat.S_ISREG(info.st_mode) or info.st_size > maximum:
        raise PersistenceError(f"compute store integrity failure: invalid {path.name}")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PersistenceError(f"compute store integrity failure: unreadable {path.name}") from exc


def _loads_json(payload: str) -> Any:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise PersistenceError(
                    f"compute store integrity failure: duplicate JSON key {key!r}"
                )
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise PersistenceError(f"compute store integrity failure: non-finite JSON {value}")

    try:
        return json.loads(
            payload, object_pairs_hook=reject_duplicates, parse_constant=reject_constant
        )
    except json.JSONDecodeError as exc:
        raise PersistenceError("compute store integrity failure: malformed JSON") from exc


def _load_json_object(path: Path, *, maximum: int) -> dict[str, Any]:
    value = _loads_json(_read_regular_text(path, maximum=maximum))
    if not isinstance(value, dict):
        raise PersistenceError("compute store integrity failure: JSON record is not an object")
    return value


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
