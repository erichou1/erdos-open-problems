"""Fail-closed source contracts for legacy browser candidate collectors.

These helpers do not verify mathematical output.  They only ensure that a
legacy ChatGPT/DeepSeek collection session is bound to one validated canonical
source snapshot and cannot be silently reused after that source identity
changes.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from erdos_ingest import find_latest_canonical_snapshot, load_canonical_corpus


MAX_COOLDOWN_SECONDS = 120.0
COLLECTION_CONTRACT_VERSION = "legacy-candidate-collector-v2"
UNVERIFIED_STATUS = "UNVERIFIED_CANDIDATE"
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(value: Mapping[str, object]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def clamp_cooldown(value: float) -> float:
    """Return a finite, nonnegative cooldown no greater than 120 seconds."""
    seconds = float(value)
    if not math.isfinite(seconds):
        raise ValueError("cooldown must be finite")
    return min(MAX_COOLDOWN_SECONDS, max(0.0, seconds))


@dataclass
class AdaptiveCooldown:
    """Exponential provider-throttle penalty that never exceeds two minutes."""

    initial_seconds: float
    streak: int = 0

    def __post_init__(self) -> None:
        self.initial_seconds = clamp_cooldown(self.initial_seconds)

    def record_rate_limit(self) -> float:
        self.streak += 1
        base = max(1.0, self.initial_seconds)
        return min(
            MAX_COOLDOWN_SECONDS,
            base * (2 ** max(0, self.streak - 1)),
        )

    def record_success(self) -> None:
        self.streak = 0


@dataclass(frozen=True)
class CandidateSource:
    problem_number: int
    statement: str
    source_url: str
    source_snapshot_id: str
    source_snapshot_sha256: str
    statement_sha256: str

    def __post_init__(self) -> None:
        if self.problem_number <= 0:
            raise ValueError("problem_number must be positive")
        if not self.statement.strip():
            raise ValueError("canonical statement is empty")
        expected_url = (
            f"https://www.erdosproblems.com/latex/{self.problem_number}"
        )
        if self.source_url != expected_url:
            raise ValueError("canonical source URL does not match problem number")
        if not self.source_snapshot_id:
            raise ValueError("canonical source snapshot ID is absent")
        if not _SHA256_RE.fullmatch(self.source_snapshot_sha256):
            raise ValueError("canonical source snapshot hash is malformed")
        if not _SHA256_RE.fullmatch(self.statement_sha256):
            raise ValueError("canonical statement hash is malformed")
        if _sha256(self.statement.encode("utf-8")) != self.statement_sha256:
            raise ValueError("canonical statement hash does not match statement")


def load_canonical_candidate_sources(
    triage_dir: Path,
) -> dict[int, CandidateSource]:
    """Load the entire latest canonical corpus and bind it to its manifest.

    ``load_canonical_corpus`` performs the expensive complete-snapshot audit.
    Hashing the manifest before and after that audit closes the ordinary
    replacement race and gives every prompt a stable snapshot identity.
    """
    snapshot = find_latest_canonical_snapshot(Path(triage_dir))
    manifest_path = snapshot / "manifest.json"
    manifest_before = manifest_path.read_bytes()
    canonical = load_canonical_corpus(snapshot)
    manifest_after = manifest_path.read_bytes()
    if manifest_after != manifest_before:
        raise RuntimeError("canonical snapshot changed while it was being loaded")
    snapshot_sha256 = _sha256(manifest_before)

    sources: dict[int, CandidateSource] = {}
    for number, record in canonical.items():
        provenance = record["provenance"]
        section_hashes = provenance["section_sha256"]
        source = CandidateSource(
            problem_number=int(number),
            statement=record["statement"],
            source_url=record["source_url"],
            source_snapshot_id=provenance["snapshot_id"],
            source_snapshot_sha256=snapshot_sha256,
            statement_sha256=section_hashes["statement"],
        )
        if source.source_snapshot_id != snapshot.name:
            raise RuntimeError(
                f"problem {number} source snapshot identity is inconsistent"
            )
        sources[source.problem_number] = source
    return sources


def build_collection_contract(
    source: CandidateSource,
    *,
    provider: str,
    category: str,
    prompt_template: str,
) -> dict[str, object]:
    """Create the deterministic run identity for one legacy collection chat."""
    identity: dict[str, object] = {
        "contract_version": COLLECTION_CONTRACT_VERSION,
        "collection_status": UNVERIFIED_STATUS,
        "provider": str(provider),
        "category": str(category),
        "problem": source.problem_number,
        "source_snapshot_id": source.source_snapshot_id,
        "source_snapshot_sha256": source.source_snapshot_sha256,
        "statement_sha256": source.statement_sha256,
        "prompt_template_sha256": _sha256(prompt_template.encode("utf-8")),
    }
    identity["candidate_collection_contract_id"] = _sha256(
        _canonical_json(identity)
    )
    return identity


def build_bound_prompt(
    prompt_template: str,
    *,
    source: CandidateSource,
    contract: Mapping[str, object],
) -> str:
    """Prepend an immutable source/run contract to the canonical statement."""
    expected = build_collection_contract(
        source,
        provider=str(contract.get("provider", "")),
        category=str(contract.get("category", "")),
        prompt_template=prompt_template,
    )
    if dict(contract) != expected:
        raise ValueError("collection contract does not match canonical source")
    preamble = "\n".join(
        (
            "IMMUTABLE SOURCE CONTRACT",
            f"collection_status: {UNVERIFIED_STATUS}",
            f"candidate_collection_contract_id: {contract['candidate_collection_contract_id']}",
            f"source_snapshot_id: {source.source_snapshot_id}",
            f"source_snapshot_sha256: {source.source_snapshot_sha256}",
            f"statement_sha256: {source.statement_sha256}",
            f"prompt_template_sha256: {contract['prompt_template_sha256']}",
            f"canonical_source_url: {source.source_url}",
            "This session collects an unverified candidate only. It cannot "
            "promote, verify, or mark the problem solved.",
        )
    )
    body = prompt_template.format(
        problem=source.statement,
        problem_number=source.problem_number,
        problem_url=source.source_url,
    )
    return f"{preamble}\n\n{body}"


def chat_metadata(
    contract: Mapping[str, object], url: str
) -> dict[str, object]:
    """Return a source-bound, explicitly unverified legacy map entry."""
    return {"url": url, **dict(contract)}


def reusable_chat_entry(
    entry: object,
    contract: Mapping[str, object],
    *,
    valid_url: Callable[[str], bool],
) -> bool:
    """Reuse only URLs produced under this exact source/run identity."""
    if not isinstance(entry, dict):
        return False
    url = entry.get("url")
    if not isinstance(url, str) or not valid_url(url):
        return False
    return all(entry.get(key) == value for key, value in contract.items())
