#!/usr/bin/env python3
"""Record exact proof-run outcomes in the evidence-bound learning ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from erdos_searcher import (
    AUTONOMOUS_LEARNING_STATUSES,
    append_ledger,
    canonical_json,
    evidence_transaction,
    normalized_budget_config,
    register_evidence_certificate,
    research_budget_id,
    write_json,
)
from run_contract import run_contract_id, run_context_id, validate_run_contract
from run_status import disposition_for_manifest, _read_bounded_regular


def record_outcome(
    triage_dir: Path,
    problem_number: int,
    manifest_path: Path,
) -> bool:
    """Append or supersede the durable outcome for exactly one manifest."""
    manifest_path = Path(manifest_path)
    disposition = disposition_for_manifest(manifest_path)
    if disposition.get("problem_number") != problem_number:
        raise ValueError("outcome disposition problem number mismatch")
    status = (
        disposition.get("outcome_class")
        or disposition.get("gate_status")
        or disposition.get("candidate_outcome")
        or "unknown"
    )
    manifest_bytes = _read_bounded_regular(manifest_path, max_bytes=4_000_000)
    manifest = json.loads(manifest_bytes)
    if manifest.get("problem_number") != problem_number:
        raise ValueError("outcome manifest problem number mismatch")
    contract = validate_run_contract(manifest.get("run_contract"))
    contract_id = run_contract_id(contract)
    execution_id = str(manifest.get("execution_id", ""))
    context_id = run_context_id(
        run_contract_id_value=contract_id, execution_id=execution_id,
    )
    if manifest.get("run_contract_id") != contract_id \
            or manifest.get("run_context_id") != context_id:
        raise ValueError("outcome manifest run identity mismatch")
    combined_budget = {**contract["budget"], **contract["execution_config"]}
    budget_config = normalized_budget_config(**combined_budget)
    identity = {
        "toolset": contract["toolset"],
        "dependencies": contract["dependencies"],
        "runtime": contract["runtime"],
    }
    candidate_path = manifest_path.parent / "candidate.md"
    candidate_sha256: str | None = None
    candidate_bytes: bytes | None = None
    try:
        candidate_bytes = _read_bounded_regular(
            candidate_path, max_bytes=16_000_000,
        )
        candidate_sha256 = hashlib.sha256(candidate_bytes).hexdigest()
    except OSError:
        pass
    recorded_candidate_sha = manifest.get("candidate_sha256")
    if recorded_candidate_sha is not None and recorded_candidate_sha != candidate_sha256:
        raise ValueError("outcome candidate artifact hash mismatch")
    record = {
        "problem_id": f"erdos-{problem_number}",
        "problem_number": problem_number,
        "execution_id": execution_id,
        "run_contract_id": contract_id,
        "run_context_id": context_id,
        "snapshot_id": contract["source_snapshot"]["id"],
        "source_snapshot_sha256": contract["source_snapshot"]["sha256"],
        "statement_sha256": contract["statement_sha256"],
        "pipeline_version": contract["pipeline_fingerprint"],
        "model_portfolio": contract["model_portfolio"],
        "toolset_version": hashlib.sha256(
            canonical_json(identity).encode("utf-8")
        ).hexdigest(),
        "budget": research_budget_id(**budget_config),
        "budget_config": budget_config,
        "status": status,
        "gate_status": disposition.get("gate_status", "unknown"),
        "candidate_outcome": disposition.get("candidate_outcome", "unknown"),
        "learning_eligible": False,
    }
    if candidate_sha256 is not None:
        record["candidate_sha256"] = candidate_sha256
    raw_gate_status = str(manifest.get("gate", {}).get("status", "unknown"))
    raw_candidate_outcome = str(manifest.get("candidate_outcome", "unknown"))
    failure_plane = (
        str(manifest["failure_plane"])
        if manifest.get("failure_plane") in {"statement", "mathematical"}
        else None
    )
    gate = {"status": raw_gate_status}
    safe_manifest_bytes: bytes | None = None
    common_support: dict[str, bytes] | None = None
    if candidate_bytes is not None and candidate_sha256 is not None:
        safe_manifest = {
            "schema_version": 1,
            "projection_type": "ledger-disposition-input-v1",
            "problem_number": problem_number,
            "execution_id": execution_id,
            "run_contract": contract,
            "run_contract_id": contract_id,
            "run_context_id": context_id,
            "statement_sha256": contract["statement_sha256"],
            "candidate_sha256": candidate_sha256,
            "gate_status": raw_gate_status,
            "manifest_candidate_outcome": raw_candidate_outcome,
            "failure_plane": failure_plane,
        }
        safe_manifest_bytes = (
            json.dumps(safe_manifest, indent=2, ensure_ascii=False, sort_keys=True)
            + "\n"
        ).encode("utf-8")
        common_support = {
            "manifest": safe_manifest_bytes,
            "candidate": candidate_bytes,
        }
    with evidence_transaction(triage_dir) as created_evidence_paths:
        if status.startswith("verified_"):
            if (
                candidate_sha256 is None
                or safe_manifest_bytes is None
                or common_support is None
            ):
                raise ValueError("verified outcome has no candidate artifact")
            snapshot_dir = (
                Path(triage_dir) / "ingestion" / contract["source_snapshot"]["id"]
            )
            source_manifest_path = snapshot_dir / "manifest.json"
            source_record_path = (
                snapshot_dir / "source_records" / f"problem_{problem_number}.json"
            )
            if not source_manifest_path.is_file() or not source_record_path.is_file():
                raise ValueError("verified outcome has no replayable canonical source evidence")
            manifest_sha256 = hashlib.sha256(safe_manifest_bytes).hexdigest()
            gate_id = register_evidence_certificate(
                triage_dir,
                kind="gate",
                run_contract_id_value=contract_id,
                run_context_id_value=context_id,
                statement_sha256=contract["statement_sha256"],
                candidate_sha256=candidate_sha256,
                evidence_payload={
                    "manifest_sha256": manifest_sha256,
                    "gate_status": disposition.get("gate_status", "unknown"),
                    "gate_object_sha256": hashlib.sha256(
                        canonical_json(gate).encode("utf-8")
                    ).hexdigest(),
                },
                issuer="proof_pipeline:deterministic_gate_v2",
                supporting_artifacts=common_support,
                _transaction_created_paths=created_evidence_paths,
            )
            intent_id = register_evidence_certificate(
                triage_dir,
                kind="intent",
                run_contract_id_value=contract_id,
                run_context_id_value=context_id,
                statement_sha256=contract["statement_sha256"],
                candidate_sha256=candidate_sha256,
                evidence_payload={
                    "source_snapshot_id": contract["source_snapshot"]["id"],
                    "source_snapshot_sha256": contract["source_snapshot"]["sha256"],
                    "statement_sha256": contract["statement_sha256"],
                    "run_contract_id": contract_id,
                },
                issuer="proof_pipeline:canonical_statement_lock_v2",
                supporting_artifacts={
                    **common_support,
                    "source_manifest": source_manifest_path.read_bytes(),
                    "source_record": source_record_path.read_bytes(),
                },
                _transaction_created_paths=created_evidence_paths,
            )
            record["evidence_certificate_ids"] = [gate_id, intent_id]
        elif (
            status in AUTONOMOUS_LEARNING_STATUSES
            and candidate_sha256 is not None
            and safe_manifest_bytes is not None
            and common_support is not None
        ):
            disposition_object = {
                "status": status,
                "gate_status": record["gate_status"],
                "candidate_outcome": record["candidate_outcome"],
            }
            disposition_id = register_evidence_certificate(
                triage_dir,
                kind="disposition",
                run_contract_id_value=contract_id,
                run_context_id_value=context_id,
                statement_sha256=contract["statement_sha256"],
                candidate_sha256=candidate_sha256,
                evidence_payload={
                    "manifest_sha256": hashlib.sha256(safe_manifest_bytes).hexdigest(),
                    **disposition_object,
                    "disposition_object_sha256": hashlib.sha256(
                        canonical_json(disposition_object).encode("utf-8")
                    ).hexdigest(),
                },
                issuer="proof_pipeline:deterministic_disposition_v1",
                supporting_artifacts=common_support,
                _transaction_created_paths=created_evidence_paths,
            )
            record["learning_eligible"] = True
            record["evidence_certificate_ids"] = [disposition_id]
        temporary = Path(triage_dir) / f".outcome_{execution_id}.json"
        write_json(temporary, record)
        try:
            return append_ledger(Path(triage_dir), "outcomes", temporary)
        finally:
            temporary.unlink(missing_ok=True)
