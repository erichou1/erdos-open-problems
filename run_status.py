"""Normalize persisted proof-run states without conflating exit status and proof status."""

import json
from pathlib import Path


VERIFIED_GATES = frozenset({"verified_proved", "verified_disproved"})


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
    if gate_status in VERIFIED_GATES:
        outcome_class = "verified_novelty_pending"
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
        "is_verified": gate_status in VERIFIED_GATES,
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
    if not problem_dir.exists():
        return []
    return sorted(path for path in problem_dir.iterdir() if path.is_dir())


def _read_manifest(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def has_verified_result(
    artifact_root: Path,
    problem_number: int,
    *,
    expected_run_contract_id: str | None = None,
) -> bool:
    """Return true only for a matching persisted deterministic verification."""
    for run_dir in _run_directories(artifact_root, problem_number):
        manifest = _read_manifest(run_dir / "manifest.json")
        exact_context = (
            expected_run_contract_id is None
            or manifest and manifest.get("run_contract_id") == expected_run_contract_id
        )
        if (
            manifest
            and exact_context
            and str(manifest.get("gate", {}).get("status", "")) in VERIFIED_GATES
        ):
            return True
    return False


def disposition_for_manifest(manifest_path: Path) -> dict:
    """Classify exactly one manifest; never join identity across run dirs."""
    manifest_path = Path(manifest_path)
    run_dir = manifest_path.parent
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
    candidate_text = (
        candidate_path.read_text(encoding="utf-8", errors="ignore")
        if candidate_path.is_file() else None
    )
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
