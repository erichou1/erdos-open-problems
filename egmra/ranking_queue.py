"""Compact, integrity-checked projection of the current solver allocation."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
from pathlib import Path


QUEUE_PROJECTION_SCHEMA_VERSION = 1
QUEUE_PROJECTION_POLICY_VERSION = "queue-projection-v1"
QUEUE_FILENAME = "current_queue.json"
MAX_QUEUE_BYTES = 8_000_000

ROW_FIELDS = (
    "problem_id",
    "problem_number",
    "allocation_rank",
    "allocation_lane",
    "prize",
    "prize_status",
    "selection_priority_tier",
    "literature_coverage_status",
    "base_acquisition_score",
    "literature_adjustment",
    "selection_score",
    "reason_selected",
)

_TOP_LEVEL_FIELDS = {
    "schema_version",
    "projection_policy_version",
    "allocation_status",
    "allocation_context_id",
    "ranking_content_sha256",
    "source_snapshot_id",
    "source_snapshot_sha256",
    "prize_policy_version",
    "literature_policy_version",
    "literature_model_version",
    "literature_coverage",
    "corpus_integrity",
    "attempt_exclusions",
    "allocation_queue",
    "projection_content_sha256",
}
_DIGEST_RE = re.compile(r"[0-9a-f]{64}")
_PROBLEM_ID_RE = re.compile(r"erdos-([1-9][0-9]*)")


class QueueProjectionError(RuntimeError):
    """The compact queue is absent, malformed, or inconsistent."""


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


def projection_content_sha256(document: dict) -> str:
    immutable = {
        key: value
        for key, value in document.items()
        if key != "projection_content_sha256"
    }
    return hashlib.sha256(_canonical_json(immutable).encode("utf-8")).hexdigest()


def _require_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or _DIGEST_RE.fullmatch(value) is None:
        raise QueueProjectionError(f"{label} must be a SHA-256 digest")
    return value


def _require_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise QueueProjectionError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise QueueProjectionError(f"{label} must be finite")
    return number


def validate_queue_projection(document: object) -> dict:
    if not isinstance(document, dict):
        raise QueueProjectionError("queue projection must be a JSON object")
    if set(document) != _TOP_LEVEL_FIELDS:
        raise QueueProjectionError("queue projection fields are unsupported")
    if document.get("schema_version") != QUEUE_PROJECTION_SCHEMA_VERSION:
        raise QueueProjectionError("queue projection schema is unsupported")
    if document.get("projection_policy_version") != QUEUE_PROJECTION_POLICY_VERSION:
        raise QueueProjectionError("queue projection policy is unsupported")
    if document.get("allocation_status") != "ready":
        raise QueueProjectionError("queue projection is not ready")
    if not isinstance(document.get("source_snapshot_id"), str) \
            or not document["source_snapshot_id"].strip():
        raise QueueProjectionError("source snapshot id is absent")
    for key in (
        "allocation_context_id",
        "ranking_content_sha256",
        "source_snapshot_sha256",
    ):
        _require_digest(document.get(key), key)
    for key in (
        "prize_policy_version",
        "literature_policy_version",
        "literature_model_version",
    ):
        if not isinstance(document.get(key), str) or not document[key].strip():
            raise QueueProjectionError(f"{key} is absent")
    if not isinstance(document.get("literature_coverage"), dict):
        raise QueueProjectionError("literature coverage must be an object")
    integrity = document.get("corpus_integrity")
    if not isinstance(integrity, dict) or integrity.get("status") != "complete":
        raise QueueProjectionError("queue projection corpus integrity is incomplete")
    exclusions = document.get("attempt_exclusions")
    if not isinstance(exclusions, list) or any(
        isinstance(value, bool) or not isinstance(value, int) or value < 1
        for value in exclusions
    ) or len(set(exclusions)) != len(exclusions):
        raise QueueProjectionError("attempt exclusions are malformed")

    rows = document.get("allocation_queue")
    if not isinstance(rows, list) or not rows:
        raise QueueProjectionError("allocation queue must be a non-empty list")
    seen_numbers: set[int] = set()
    paid_seen = False
    for expected_rank, row in enumerate(rows, start=1):
        if not isinstance(row, dict) or set(row) != set(ROW_FIELDS):
            raise QueueProjectionError("allocation row fields are unsupported")
        number = row.get("problem_number")
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            raise QueueProjectionError("problem number must be a positive integer")
        if number in seen_numbers:
            raise QueueProjectionError("allocation queue contains a duplicate problem")
        seen_numbers.add(number)
        match = _PROBLEM_ID_RE.fullmatch(str(row.get("problem_id", "")))
        if match is None or int(match.group(1)) != number:
            raise QueueProjectionError("problem id and number disagree")
        if row.get("allocation_rank") != expected_rank:
            raise QueueProjectionError("allocation ranks must be contiguous")
        if not isinstance(row.get("allocation_lane"), str) \
                or not row["allocation_lane"].strip():
            raise QueueProjectionError("allocation lane is absent")
        status = row.get("prize_status")
        if status not in {"unpaid", "paid"}:
            raise QueueProjectionError("allocation row prize status is unsupported")
        if status == "paid":
            paid_seen = True
        elif paid_seen:
            raise QueueProjectionError("every unpaid problem must precede paid problems")
        expected_tier = 0 if status == "unpaid" else 1
        if row.get("selection_priority_tier") != expected_tier:
            raise QueueProjectionError("selection priority tier disagrees with prize status")
        if isinstance(row.get("prize"), (dict, list, bool)) \
                or row.get("prize") is None:
            raise QueueProjectionError("prize metadata is malformed")
        if not isinstance(row.get("literature_coverage_status"), str) \
                or not row["literature_coverage_status"].strip():
            raise QueueProjectionError("literature coverage status is absent")
        for key in (
            "base_acquisition_score", "literature_adjustment", "selection_score"
        ):
            _require_number(row.get(key), key)
        if not isinstance(row.get("reason_selected"), str) \
                or not row["reason_selected"].strip():
            raise QueueProjectionError("selection reason is absent")

    expected_hash = projection_content_sha256(document)
    if document.get("projection_content_sha256") != expected_hash:
        raise QueueProjectionError("queue projection content hash mismatch")
    return copy.deepcopy(document)


def build_queue_projection(ranking: dict) -> dict:
    if not isinstance(ranking, dict):
        raise QueueProjectionError("complete ranking must be an object")
    try:
        projected_rows = [
            {field: copy.deepcopy(row[field]) for field in ROW_FIELDS}
            for row in ranking["allocation_queue"]
        ]
        projection = {
            "schema_version": QUEUE_PROJECTION_SCHEMA_VERSION,
            "projection_policy_version": QUEUE_PROJECTION_POLICY_VERSION,
            "allocation_status": ranking["allocation_status"],
            "allocation_context_id": ranking["allocation_context_id"],
            "ranking_content_sha256": ranking["ranking_content_sha256"],
            "source_snapshot_id": ranking["source_snapshot_id"],
            "source_snapshot_sha256": ranking["source_snapshot_sha256"],
            "prize_policy_version": ranking["prize_policy_version"],
            "literature_policy_version": ranking["literature_policy_version"],
            "literature_model_version": ranking["literature_model_version"],
            "literature_coverage": copy.deepcopy(ranking["literature_coverage"]),
            "corpus_integrity": copy.deepcopy(ranking["corpus_integrity"]),
            "attempt_exclusions": copy.deepcopy(ranking["attempt_exclusions"]),
            "allocation_queue": projected_rows,
        }
    except (KeyError, TypeError) as error:
        raise QueueProjectionError(
            f"complete ranking cannot be projected: missing {error}"
        ) from error
    projection["projection_content_sha256"] = projection_content_sha256(projection)
    return validate_queue_projection(projection)


def load_queue_projection(path: Path) -> dict:
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise QueueProjectionError(f"queue projection is not a regular file: {path}")
    if path.stat().st_size > MAX_QUEUE_BYTES:
        raise QueueProjectionError(f"queue projection is implausibly large: {path}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise QueueProjectionError(f"queue projection is unreadable: {path}") from error
    return validate_queue_projection(document)


def write_queue_projection(path: Path, ranking: dict) -> dict:
    path = Path(path)
    projection = build_queue_projection(ranking)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    serialized = json.dumps(projection, indent=2, sort_keys=True) + "\n"
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    return projection
