#!/usr/bin/env python3
"""Shared, atomic work queue for continuous multi-worker verified runs.

The searcher writes one problem card per open problem under
``triage/normalized/problem_cards``. This module turns those cards into a
priority-ordered queue and lets independent worker processes claim problems
atomically, so N browsers (one per ChatGPT profile) drain the whole ranked
corpus without ever attacking the same problem at once.
"""

from __future__ import annotations

import json
import hashlib
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from run_status import has_verified_result
from run_contract import canonical_json


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AllocationPlan:
    allocation_context_id: str
    ranking_content_sha256: str
    allocation_id: str
    records: tuple[dict, ...]

    @property
    def problem_numbers(self) -> list[int]:
        return [record["problem_number"] for record in self.records]


def load_allocation_plan(
    triage_dir: Path,
    *,
    expected_allocation_context_id: str,
    expected_ranking_content_sha256: str,
) -> AllocationPlan:
    """Read and validate one immutable, content-addressed allocation payload."""
    if not re.fullmatch(r"[0-9a-f]{64}", expected_allocation_context_id):
        raise ValueError("expected allocation context must be a SHA-256 digest")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_ranking_content_sha256):
        raise ValueError("expected ranking content must be a SHA-256 digest")
    path = (
        Path(triage_dir) / "rankings" / "contexts"
        / expected_allocation_context_id
        / f"{expected_ranking_content_sha256}.json"
    )
    try:
        ranking = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"allocation ranking is absent or unreadable: {path}") from error
    if not isinstance(ranking, dict) or ranking.get("schema_version") != 2:
        raise ValueError("allocation ranking schema is unsupported")
    if ranking.get("allocation_status") != "ready":
        raise ValueError("allocation ranking is not ready")
    immutable_content = {
        key: value for key, value in ranking.items()
        if key not in {
            "generated_at", "ranking_content_sha256", "allocation_id",
        }
    }
    calculated_ranking_hash = hashlib.sha256(
        json.dumps(
            immutable_content, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    if (
        ranking.get("ranking_content_sha256") != calculated_ranking_hash
        or calculated_ranking_hash != expected_ranking_content_sha256
    ):
        raise ValueError("allocation ranking content hash mismatch")
    context = ranking.get("allocation_context")
    if not isinstance(context, dict):
        raise ValueError("allocation context is absent")
    calculated_context_id = hashlib.sha256(
        canonical_json(context).encode("utf-8")
    ).hexdigest()
    recorded_context_id = ranking.get("allocation_context_id")
    if (
        not isinstance(recorded_context_id, str)
        or recorded_context_id != calculated_context_id
        or recorded_context_id != expected_allocation_context_id
    ):
        raise ValueError("allocation context mismatch")
    allocation_id = hashlib.sha256(canonical_json({
        "allocation_context_id": recorded_context_id,
        "ranking_content_sha256": calculated_ranking_hash,
    }).encode("utf-8")).hexdigest()
    if ranking.get("allocation_id") != allocation_id:
        raise ValueError("allocation identity mismatch")

    def validated_problem_number(record: dict, label: str) -> int:
        number = record.get("problem_number")
        if (
            not isinstance(number, int)
            or isinstance(number, bool)
            or number < 1
        ):
            raise ValueError(f"{label} has an invalid record")
        return number

    def records(value: object, label: str) -> list[dict]:
        if not isinstance(value, list):
            raise ValueError(f"{label} lane is absent or invalid")
        result: list[dict] = []
        for record in value:
            if not isinstance(record, dict):
                raise ValueError(f"{label} has an invalid record")
            validated_problem_number(record, label)
            if record.get("allocation_context_id") != recorded_context_id:
                raise ValueError(f"{label} record context mismatch")
            run_contract_id = record.get("run_contract_id")
            if (
                not isinstance(run_contract_id, str)
                or not re.fullmatch(r"[0-9a-f]{64}", run_contract_id)
            ):
                raise ValueError(f"{label} record has no exact run contract")
            result.append(record)
        return result

    exploitation = records(
        ranking.get("diversified_attack_queue"), "exploitation"
    )
    exploration = records(
        ranking.get("protected_exploration"), "protected exploration"
    )
    allocation = records(ranking.get("allocation_queue"), "allocation")

    def numbers(records: list[dict], label: str) -> list[int]:
        result = [validated_problem_number(record, label) for record in records]
        if len(result) != len(set(result)):
            raise ValueError(f"{label} contains duplicate problems")
        return result

    exploit_numbers = numbers(exploitation, "exploitation")
    explore_numbers = numbers(exploration, "protected exploration")
    if set(exploit_numbers) & set(explore_numbers):
        raise ValueError("protected exploration overlaps exploitation")
    allocation_numbers = numbers(allocation, "allocation")
    if set(allocation_numbers) != set(exploit_numbers) | set(explore_numbers):
        raise ValueError("allocation queue omits or adds lane members")
    for rank, record in enumerate(allocation, 1):
        allocation_rank = record.get("allocation_rank")
        if (
            not isinstance(allocation_rank, int)
            or isinstance(allocation_rank, bool)
            or allocation_rank != rank
        ):
            raise ValueError("allocation ranks are not contiguous")
        problem_number = record["problem_number"]
        expected_lane = (
            "exploitation" if problem_number in set(exploit_numbers)
            else "protected_exploration"
        )
        allocation_lane = record.get("allocation_lane")
        if not isinstance(allocation_lane, str) or allocation_lane != expected_lane:
            raise ValueError("allocation lane label mismatch")
    expected_interleave: list[tuple[int, str]] = []
    exploit_index = 0
    explore_index = 0
    while exploit_index < len(exploit_numbers) or explore_index < len(explore_numbers):
        for _ in range(4):
            if exploit_index >= len(exploit_numbers):
                break
            expected_interleave.append((exploit_numbers[exploit_index], "exploitation"))
            exploit_index += 1
        if explore_index < len(explore_numbers):
            expected_interleave.append((
                explore_numbers[explore_index], "protected_exploration"
            ))
            explore_index += 1
        if exploit_index >= len(exploit_numbers) and explore_index < len(explore_numbers):
            expected_interleave.extend(
                (number, "protected_exploration")
                for number in explore_numbers[explore_index:]
            )
            break
    actual_interleave = [
        (record["problem_number"], record["allocation_lane"])
        for record in allocation
    ]
    if actual_interleave != expected_interleave:
        raise ValueError("protected exploration cadence/order mismatch")
    return AllocationPlan(
        allocation_context_id=recorded_context_id,
        ranking_content_sha256=calculated_ranking_hash,
        allocation_id=allocation_id,
        records=tuple(allocation),
    )


def ranked_queue(
    triage_dir: Path, *, expected_allocation_context_id: str,
    expected_ranking_content_sha256: str,
) -> list[int]:
    return load_allocation_plan(
        triage_dir,
        expected_allocation_context_id=expected_allocation_context_id,
        expected_ranking_content_sha256=expected_ranking_content_sha256,
    ).problem_numbers


def allocation_record(plan: AllocationPlan, problem_number: int) -> dict:
    """Return one record from the already-validated in-memory immutable plan."""
    matches = [
        record for record in plan.records
        if record["problem_number"] == problem_number
    ]
    if len(matches) != 1:
        raise ValueError("problem has no unique allocation record")
    return matches[0]


def _claims_dir(artifacts: Path, allocation_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{64}", allocation_id):
        raise ValueError("allocation ID must be a SHA-256 digest")
    path = Path(artifacts) / ".claims" / allocation_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def claim(
    artifacts: Path, problem_number: int, worker: str, *,
    allocation_id: str, run_contract_id: str,
) -> bool:
    """Atomically claim one problem. Returns True only for the winning worker."""
    if not re.fullmatch(r"[0-9a-f]{64}", run_contract_id):
        raise ValueError("claim run contract must be a SHA-256 digest")
    claim_path = _claims_dir(artifacts, allocation_id) / f"problem_{problem_number}"
    try:
        fd = os.open(claim_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "worker": worker,
            "claimed_at": _now(),
            "allocation_id": allocation_id,
            "run_contract_id": run_contract_id,
        }) + "\n")
    return True


def claim_next(
    artifacts: Path, plan: AllocationPlan, worker: str,
) -> int | None:
    """Claim the highest-ranked problem that is neither verified nor taken."""
    for record in plan.records:
        number = record["problem_number"]
        expected_run_contract_id = record["run_contract_id"]
        if has_verified_result(
            artifacts, number,
            expected_run_contract_id=expected_run_contract_id,
        ):
            continue
        if claim(
            artifacts, number, worker,
            allocation_id=plan.allocation_id,
            run_contract_id=expected_run_contract_id,
        ):
            return number
    return None


def _has_manifest(
    artifacts: Path, problem_number: int, *, run_contract_id: str
) -> bool:
    problem_dir = Path(artifacts) / f"problem_{problem_number}"
    if not problem_dir.exists():
        return False
    for run in problem_dir.iterdir():
        manifest_path = run / "manifest.json"
        if not run.is_dir() or not manifest_path.exists():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if manifest.get("run_contract_id") == run_contract_id:
            return True
    return False


def _claim_identity(claim_file: Path) -> tuple[int, str] | None:
    try:
        number = int(claim_file.name.split("_", 1)[1])
        record = json.loads(claim_file.read_text(encoding="utf-8"))
        run_contract_id = str(record["run_contract_id"])
    except (IndexError, ValueError, KeyError, OSError, json.JSONDecodeError):
        return None
    if not re.fullmatch(r"[0-9a-f]{64}", run_contract_id):
        return None
    return number, run_contract_id


def release_incomplete_claims(artifacts: Path) -> int:
    """Drop claims for unverified problems that never produced a manifest.

    Call this once at campaign start (before launching workers) so a problem
    interrupted by a crash or restart is retried and resumed from its per-stage
    cache, while verified problems and completed runs keep their claims. Unsafe
    to call while workers are actively solving, since it could free an in-flight
    problem for a second worker.
    """
    claims_root = Path(artifacts) / ".claims"
    released = 0
    for claim_file in claims_root.glob("*/problem_*"):
        identity = _claim_identity(claim_file)
        if identity is None:
            continue
        number, run_contract_id = identity
        if has_verified_result(
            artifacts, number, expected_run_contract_id=run_contract_id,
        ):
            continue
        if _has_manifest(
            artifacts, number, run_contract_id=run_contract_id,
        ):
            continue
        try:
            claim_file.unlink()
            released += 1
        except OSError:
            pass
    return released


def release_unverified_claims(artifacts: Path) -> int:
    """Start a new campaign by releasing every claim without a verified result.

    This must be called only while no workers are active. It intentionally makes
    budget-exhausted/rejected problems eligible after a pipeline, model, toolset,
    budget, or campaign-policy change instead of treating failure as permanent.
    """
    claims_root = Path(artifacts) / ".claims"
    released = 0
    for claim_file in claims_root.glob("*/problem_*"):
        identity = _claim_identity(claim_file)
        if identity is None:
            continue
        number, run_contract_id = identity
        if has_verified_result(
            artifacts, number, expected_run_contract_id=run_contract_id,
        ):
            continue
        try:
            claim_file.unlink()
            released += 1
        except OSError:
            pass
    return released
