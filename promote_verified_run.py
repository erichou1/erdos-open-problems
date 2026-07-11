#!/usr/bin/env python3
"""Apply external evidence to an existing proof run and optionally publish it."""

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from proof_pipeline import PipelineResult
from run_verified_pipeline import load_evidence, publish_verified_result
from verification import Review, candidate_contract, evaluate_gate


TUPLE_FIELDS = {
    "checked_claim_ids", "open_gaps", "unchecked_imports", "material_errors"
}


def load_reviews(records: list[dict]) -> tuple[Review, ...]:
    reviews = []
    for record in records:
        normalized = dict(record)
        for field in TUPLE_FIELDS:
            normalized[field] = tuple(normalized.get(field, []))
        reviews.append(Review(**normalized))
    return tuple(reviews)


def promote(
    run_dir: Path,
    evidence_path: Path,
    *,
    publish: bool,
    category: str,
    base_dir: Path | None = None,
) -> PipelineResult:
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidate = (run_dir / "candidate.md").read_text(encoding="utf-8")
    evidence = load_evidence(evidence_path)
    candidate_sha = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
    decision = evaluate_gate(
        manifest["candidate_outcome"],
        load_reviews(manifest["reviews"]),
        expected_statement_sha256=manifest["statement_sha256"],
        candidate_contract=candidate_contract(candidate),
        verification_evidence=evidence,
        expected_candidate_sha256=candidate_sha,
    )
    manifest["gate"] = asdict(decision)
    manifest["verification_evidence"] = [asdict(item) for item in evidence]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
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
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--evidence-json", type=Path, required=True)
    parser.add_argument("--category", default="open")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    result = promote(
        args.run_dir.resolve(), args.evidence_json.resolve(),
        publish=args.publish, category=args.category,
    )
    print(f"gate: {result.gate.status}")
    for reason in result.gate.reasons:
        print(f"- {reason}")


if __name__ == "__main__":
    main()
