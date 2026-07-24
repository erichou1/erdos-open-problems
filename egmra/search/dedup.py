"""Duplicate-detection cascade (spec §7.5).

Exact duplicates merge their evidence/cost histories. Semantic near-duplicates
receive a penalty but remain separate when their assumptions, falsifiers, or proof
obligations differ.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from egmra.provenance.hashing import content_id
from egmra.search.mechanism import MechanismFingerprint

_TOKEN = re.compile(r"[a-zA-Z0-9]+")


def _shingles(text: str, k: int = 3) -> set[str]:
    tokens = _TOKEN.findall(text.lower())
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i:i + k]) for i in range(len(tokens) - k + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


@dataclass(frozen=True)
class DedupVerdict:
    stage: str                # exact | formula_cone | mechanism | plan | behavior | distinct
    is_duplicate: bool
    similarity: float
    action: str               # merge | penalize | keep


def exact_key(target_hash: str, assumptions: list[str], formal_context: str) -> str:
    return content_id({"target": target_hash, "assumptions": sorted(assumptions),
                       "context": formal_context})


def dedup_cascade(
    *,
    a_target_hash: str, b_target_hash: str,
    a_assumptions: list[str], b_assumptions: list[str],
    a_formal_context: str = "", b_formal_context: str = "",
    a_mechanism: MechanismFingerprint | None = None,
    b_mechanism: MechanismFingerprint | None = None,
    a_plan_text: str = "", b_plan_text: str = "",
    a_behavior: list[int] | None = None, b_behavior: list[int] | None = None,
    near_threshold: float = 0.8,
) -> DedupVerdict:
    """Run the 6-stage cascade; stop at the first decisive stage."""
    # 1. exact target/assumption/formal-context hash
    if exact_key(a_target_hash, a_assumptions, a_formal_context) == \
            exact_key(b_target_hash, b_assumptions, b_formal_context):
        return DedupVerdict("exact", True, 1.0, "merge")

    # 2. normalized formula + dependency-cone isomorphism (same target, diff assumptions)
    if a_target_hash == b_target_hash:
        assum_sim = jaccard(set(a_assumptions), set(b_assumptions))
        if assum_sim >= near_threshold:
            return DedupVerdict("formula_cone", True, assum_sim, "merge")
        return DedupVerdict("formula_cone", False, assum_sim, "keep")

    # 3. premise-set + mechanism fingerprint Jaccard/MinHash
    if a_mechanism is not None and b_mechanism is not None:
        if a_mechanism.method_family == b_mechanism.method_family:
            mech_sim = jaccard(set(a_mechanism.objects_invariants) | set(a_mechanism.external_theorems),
                               set(b_mechanism.objects_invariants) | set(b_mechanism.external_theorems))
            if mech_sim >= near_threshold:
                return DedupVerdict("mechanism", True, mech_sim, "penalize")

    # 4. proof-plan embedding similarity (shingle Jaccard as a local stand-in)
    if a_plan_text and b_plan_text:
        plan_sim = jaccard(_shingles(a_plan_text), _shingles(b_plan_text))
        if plan_sim >= near_threshold:
            return DedupVerdict("plan", True, plan_sim, "penalize")

    # 5. behavior vector over generated test cases/countermodels
    if a_behavior is not None and b_behavior is not None and a_behavior == b_behavior:
        return DedupVerdict("behavior", True, 1.0, "penalize")

    # 6. borderline -> keep separate (human/model comparison happens elsewhere)
    return DedupVerdict("distinct", False, 0.0, "keep")
