"""Normalize persisted proof-run states without conflating exit status and proof status."""

import json
import os
import stat
from pathlib import Path


# Historical manifests stored a mutable gate-status label without an
# authenticated release certificate.  Keep the labels so they can be
# quarantined explicitly, but never treat them as proof of verification.
UNAUTHENTICATED_VERIFIED_GATES = frozenset(
    {"verified_proved", "verified_disproved"}
)


def classify_disposition_inputs(
    *,
    problem_number: int,
    gate_status: str,
    manifest_candidate_outcome: str,
    failure_plane: str | None,
    candidate_text: str | None,
) -> dict:
    """Classify the closed raw inputs used by both runs and ledger replay."""
    candidate_outcome = manifest_candidate_outcome
    if candidate_outcome == "candidate_unclassified" and candidate_text is not None:
        from verification import candidate_status

        recovered = candidate_status(candidate_text)
        if recovered != "candidate_unclassified":
            candidate_outcome = recovered
    if gate_status in UNAUTHENTICATED_VERIFIED_GATES:
        # A caller can edit manifest.json directly.  Until this legacy reader is
        # wired to the EGMRA ReleaseCertificate verifier, a success-looking
        # label is an operationally untrusted input, not a learning or release
        # outcome.
        outcome_class = "operational_failure"
    elif gate_status == "awaiting_external_evidence":
        outcome_class = "awaiting_external_evidence"
    elif candidate_outcome == "resource_exhausted":
        outcome_class = "no_progress_within_budget"
    elif gate_status == "candidate_rejected" and failure_plane == "statement":
        outcome_class = "wrong_interpretation"
    elif gate_status == "candidate_rejected" and failure_plane == "mathematical":
        outcome_class = "fundamentally_flawed_candidate"
    else:
        outcome_class = "operational_failure"
    return {
        "problem_number": problem_number,
        "outcome_class": outcome_class,
        "gate_status": gate_status,
        "candidate_outcome": candidate_outcome,
        "is_verified": False,
        "is_labeled_outcome": outcome_class not in {
            "unattempted", "censored_attempt", "operational_failure",
            "awaiting_external_evidence",
        },
        "is_negative_training_example": outcome_class in {
            "no_progress_within_budget", "fundamentally_flawed_candidate",
            "wrong_interpretation", "statement_defect", "formalization_mismatch",
        },
    }


def _run_directories(artifact_root: Path, problem_number: int) -> list[Path]:
    problem_dir = Path(artifact_root) / f"problem_{problem_number}"
    if problem_dir.is_symlink() or not problem_dir.is_dir():
        return []
    return sorted(
        path for path in problem_dir.iterdir()
        if not path.is_symlink() and path.is_dir()
    )


def _read_bounded_regular(path: Path, *, max_bytes: int) -> bytes:
    flags = (
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise OSError("path is not a regular file")
        if metadata.st_size > max_bytes:
            raise OSError("file exceeds bounded status-reader limit")
        chunks: list[bytes] = []
        remaining = max_bytes + 1
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > max_bytes:
            raise OSError("file exceeds bounded status-reader limit")
        return payload
    finally:
        os.close(descriptor)


def _read_manifest(path: Path) -> dict | None:
    try:
        value = json.loads(
            _read_bounded_regular(path, max_bytes=4_000_000).decode("utf-8")
        )
    except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def has_verified_result(
    artifact_root: Path,
    problem_number: int,
    *,
    expected_run_contract_id: str | None = None,
) -> bool:
    """Return whether an authoritative release exists for this legacy store.

    Legacy proof-run directories contain no independently authenticated EGMRA
    release certificate, only caller-writable manifest labels.  They therefore
    cannot establish a verified result.  Parameters are retained for API
    compatibility while callers migrate to the release-certificate store.
    """
    del artifact_root, problem_number, expected_run_contract_id
    return False


def disposition_for_manifest(manifest_path: Path) -> dict:
    """Classify exactly one manifest; never join identity across run dirs."""
    manifest_path = Path(manifest_path)
    run_dir = manifest_path.parent
    if run_dir.is_symlink() or not run_dir.is_dir():
        manifest = None
    else:
        manifest = _read_manifest(manifest_path)
    if manifest is None:
        return {
            "run_dir": str(run_dir),
            "outcome_class": "operational_failure",
            "gate_status": "malformed_manifest",
            "candidate_outcome": "unknown",
            "is_verified": False,
            "is_labeled_outcome": False,
            "is_negative_training_example": False,
        }
    problem_number = int(manifest.get("problem_number", 0))
    candidate_path = run_dir / "candidate.md"
    try:
        candidate_text = _read_bounded_regular(
            candidate_path, max_bytes=16_000_000,
        ).decode("utf-8", errors="ignore")
    except OSError:
        candidate_text = None
    result = classify_disposition_inputs(
        problem_number=problem_number,
        gate_status=str(manifest.get("gate", {}).get("status", "unknown")),
        manifest_candidate_outcome=str(
            manifest.get("candidate_outcome", "unknown")
        ),
        failure_plane=(
            str(manifest["failure_plane"])
            if manifest.get("failure_plane") in {"statement", "mathematical"}
            else None
        ),
        candidate_text=candidate_text,
    )
    return {**result, "run_dir": str(run_dir)}


def problem_disposition(artifact_root: Path, problem_number: int) -> dict:
    """Classify the latest durable run using outcome classes suitable for learning."""
    run_dirs = _run_directories(artifact_root, problem_number)
    if not run_dirs:
        return {
            "problem_number": problem_number,
            "outcome_class": "unattempted",
            "is_verified": False,
            "is_labeled_outcome": False,
            "is_negative_training_example": False,
        }

    readable = []
    for run_dir in run_dirs:
        manifest_path = run_dir / "manifest.json"
        if manifest_path.exists():
            readable.append((run_dir, _read_manifest(manifest_path)))
    if not readable:
        return {
            "problem_number": problem_number,
            "run_dir": str(run_dirs[-1]),
            "outcome_class": "censored_attempt",
            "is_verified": False,
            "is_labeled_outcome": False,
            "is_negative_training_example": False,
        }

    run_dir, _ = readable[-1]
    return disposition_for_manifest(run_dir / "manifest.json")
