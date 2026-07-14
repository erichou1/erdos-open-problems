#!/usr/bin/env python3
"""Apply external evidence to an existing proof run and optionally publish it."""

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from proof_pipeline import PipelineResult
from outcome_ledger import record_outcome
from erdos_searcher import write_json
from run_verified_pipeline import (
    _read_regular_file,
    _strict_json_object,
    inspect_evidence,
    load_evidence,
    publish_verified_result,
)
from verification import GateDecision, Review, candidate_contract, evaluate_gate
from research_state import make_statement_lock
from run_contract import (
    run_context_id,
    run_contract_id,
    validate_run_contract,
)

from egmra.m0 import PromotionGuard
from egmra.policy import PolicyEnforcer, PolicyError, default_policy_path, load_policy


TUPLE_FIELDS = {
    "checked_claim_ids", "open_gaps", "unchecked_imports", "material_errors"
}


def _enforce_promotion_policy(enforcer, *, formal: bool) -> str | None:
    """Enforce the signed feature policy at the promotion entry point (spec §16 P0.1).

    Returns ``None`` when promotion is allowed, or a human-readable reason string
    when the signed policy blocks it. With no explicit enforcer the default egmra
    policy is loaded (promotion disabled), so a caller must present a signed policy
    that enables promotion.
    """
    if enforcer is None:
        try:
            enforcer = PolicyEnforcer(load_policy(default_policy_path()))
        except PolicyError as exc:
            return f"feature policy is unavailable or unauthenticated: {exc}"
    elif type(enforcer) is not PolicyEnforcer:
        raise TypeError("promotion policy must be an authenticated PolicyEnforcer")
    allowed, reason = PromotionGuard(enforcer, entry_point="promote_verified_run.promote").check(
        formal=formal)
    return None if allowed else reason


def load_reviews(records: list[dict]) -> tuple[Review, ...]:
    reviews = []
    for record in records:
        normalized = dict(record)
        for field in TUPLE_FIELDS:
            normalized[field] = tuple(normalized.get(field, []))
        reviews.append(Review(**normalized))
    return tuple(reviews)


def _validated_run_candidate(run_dir: Path, manifest: dict) -> str:
    """Recompute all local immutable identities before trusting a manifest view."""
    run_dir = Path(run_dir)
    if run_dir.is_symlink() or not run_dir.is_dir():
        raise ValueError("run directory must be a regular non-symlink directory")
    problem_number = manifest.get("problem_number")
    if type(problem_number) is not int or problem_number <= 0:
        raise ValueError("manifest has no canonical problem number")
    if run_dir.parent.name != f"problem_{problem_number}":
        raise ValueError("manifest problem number does not match its run directory")
    execution_id = manifest.get("execution_id")
    if not isinstance(execution_id, str) or execution_id != run_dir.name:
        raise ValueError("manifest execution id does not match its run directory")

    problem_bytes = _read_regular_file(
        run_dir / "problem.txt", max_bytes=1_000_000, label="locked problem",
    )
    try:
        problem = problem_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("locked problem is not strict UTF-8") from exc
    recomputed_lock = make_statement_lock(problem)
    lock_bytes = _read_regular_file(
        run_dir / "statement_lock.json", max_bytes=1_000_000,
        label="statement lock",
    )
    try:
        lock_doc = json.loads(
            lock_bytes.decode("utf-8"), object_pairs_hook=_strict_json_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("statement lock is not strict JSON") from exc
    expected_lock = {
        "original_statement": recomputed_lock.original_statement,
        "sha256": recomputed_lock.sha256,
        "acceptance_criteria": list(recomputed_lock.acceptance_criteria),
    }
    if lock_doc != expected_lock \
            or manifest.get("statement_sha256") != recomputed_lock.sha256:
        raise ValueError("statement lock or manifest statement identity was mutated")

    embedded = validate_run_contract(manifest.get("run_contract"))
    contract_id = run_contract_id(embedded)
    if manifest.get("run_contract_id") != contract_id \
            or embedded.get("statement_sha256") != recomputed_lock.sha256:
        raise ValueError("run contract is absent or inconsistent")
    expected_context_id = run_context_id(
        run_contract_id_value=contract_id, execution_id=execution_id,
    )
    if manifest.get("run_context_id") != expected_context_id:
        raise ValueError("run context identity is inconsistent")
    if embedded.get("research_directive_sha256") \
            != manifest.get("research_directive_sha256"):
        raise ValueError("research directive is not bound to the run contract")

    candidate_bytes = _read_regular_file(
        run_dir / "candidate.md", max_bytes=16_000_000, label="candidate",
    )
    try:
        candidate = candidate_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("candidate is not strict UTF-8") from exc
    candidate_sha = hashlib.sha256(candidate_bytes).hexdigest()
    if manifest.get("candidate_sha256") != candidate_sha:
        raise ValueError("manifest candidate identity was mutated")
    return candidate


def promote(
    run_dir: Path,
    evidence_path: Path,
    *,
    publish: bool,
    category: str,
    base_dir: Path | None = None,
    triage_dir: Path | None = None,
    enforcer=None,
    attestation_env: dict[str, str] | None = None,
) -> PipelineResult:
    # M0 (spec §16 P0.1): enforce the signed feature policy at this promotion entry
    # point before reading any attacker-controlled run or evidence bytes.
    guard_reason = _enforce_promotion_policy(enforcer, formal=False)
    if guard_reason is not None:
        decision = GateDecision("promotion_disabled_by_policy", (guard_reason,))
        return PipelineResult(
            problem_number=0,
            candidate_outcome="unknown",
            gate=decision, artifact_dir=run_dir,
        )

    manifest_path = run_dir / "manifest.json"
    try:
        manifest = json.loads(
            _read_regular_file(
                manifest_path, max_bytes=4_000_000, label="run manifest",
            ).decode("utf-8"),
            object_pairs_hook=_strict_json_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("run manifest is not strict UTF-8 JSON") from exc

    candidate = _validated_run_candidate(run_dir, manifest)
    inspection = inspect_evidence(evidence_path, enforcer=enforcer)
    if "formal_proof" in inspection.kinds:
        guard_reason = _enforce_promotion_policy(enforcer, formal=True)
        if guard_reason is not None:
            decision = GateDecision("promotion_disabled_by_policy", (guard_reason,))
            manifest["gate"] = asdict(decision)
            write_json(manifest_path, manifest)
            return PipelineResult(
                problem_number=int(manifest["problem_number"]),
                candidate_outcome=str(manifest["candidate_outcome"]),
                gate=decision, artifact_dir=run_dir,
            )
    evidence = load_evidence(
        evidence_path, enforcer=enforcer, attestation_env=attestation_env,
        expected_document_sha256=inspection.document_sha256,
    )
    candidate_sha = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
    decision = evaluate_gate(
        manifest["candidate_outcome"],
        load_reviews(manifest["reviews"]),
        expected_statement_sha256=manifest["statement_sha256"],
        candidate_contract=candidate_contract(candidate),
        verification_evidence=evidence,
        expected_candidate_sha256=candidate_sha,
        attestation_env=attestation_env,
        expected_problem_number=manifest["problem_number"],
        expected_run_contract_id=manifest["run_contract_id"],
        expected_execution_id=manifest["execution_id"],
        expected_run_context_id=manifest["run_context_id"],
    )
    manifest["gate"] = asdict(decision)
    manifest["verification_evidence"] = [asdict(item) for item in evidence]
    manifest["candidate_sha256"] = candidate_sha
    write_json(manifest_path, manifest)
    result = PipelineResult(
        problem_number=int(manifest["problem_number"]),
        candidate_outcome=str(manifest["candidate_outcome"]),
        gate=decision,
        artifact_dir=run_dir,
    )
    if publish:
        publish_verified_result(
            result, category, base_dir or Path(__file__).parent
        )
    if triage_dir is not None:
        record_outcome(triage_dir, result.problem_number, manifest_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--evidence-json", type=Path, required=True)
    parser.add_argument("--category", default="open")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--triage", type=Path, default=Path("triage"))
    parser.add_argument("--policy", type=Path, default=None,
                        help="signed feature-policy JSON that must enable promotion")
    args = parser.parse_args()
    enforcer = None
    if args.policy is not None:
        enforcer = PolicyEnforcer(load_policy(args.policy))
    result = promote(
        args.run_dir.resolve(), args.evidence_json.resolve(),
        publish=args.publish, category=args.category,
        triage_dir=args.triage.resolve(), enforcer=enforcer,
    )
    print(f"gate: {result.gate.status}")
    for reason in result.gate.reasons:
        print(f"- {reason}")


if __name__ == "__main__":
    main()
