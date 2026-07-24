"""OEIS match ranking + held-out verification workflow (spec §8.3).

An OEIS match is a *conjecture generator and literature pointer*. It is never a
proof, and "sequence not found" is never evidence of novelty. The workflow
computes extra terms not sent in the query and tests candidate formulas against
those held-out terms before creating a claim node with ``NUMERICAL_EVIDENCE``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable

from egmra.oeis.transforms import TransformError, TransformStep, apply_path
from egmra.provenance.hashing import content_id


@dataclass(frozen=True)
class Match:
    a_number: str
    matched_transform: tuple[str, ...]
    prefix_overlap: int
    prefix_exact: bool
    name: str = ""
    offset: str = ""
    formulas: tuple[str, ...] = ()
    references: tuple[str, ...] = ()
    content_hash: str = ""


def prefix_overlap(query_terms: list[int], candidate_terms: list[int]) -> int:
    count = 0
    for a, b in zip(query_terms, candidate_terms):
        if a == b:
            count += 1
        else:
            break
    return count


def collision_risk(terms: list[int]) -> float:
    """Short/common prefixes have high collision risk (low distinctiveness)."""
    if len(terms) <= 2:
        return 1.0
    # small monotone runs like 1,2,3,... are common; longer & larger = rarer
    spread = len({t for t in terms})
    magnitude = max((abs(t) for t in terms), default=0)
    rarity = min(1.0, (len(terms) / 10.0) * (1 + math.log1p(magnitude)) / 5.0)
    return round(max(0.0, 1.0 - rarity * (spread / max(1, len(terms)))), 4)


def score_match(
    query_terms: list[int], match: Match, *, transform_len: int
) -> float:
    if match.prefix_overlap < 0 or match.prefix_overlap > len(query_terms):
        raise ValueError("prefix_overlap is outside the queried prefix")
    if match.prefix_exact and match.prefix_overlap != len(query_terms):
        raise ValueError("prefix_exact requires overlap with every queried term")
    if transform_len < 0:
        raise ValueError("transform length cannot be negative")
    exact = 1.0 if match.prefix_exact else 0.0
    overlap = match.prefix_overlap / max(1, len(query_terms))
    complexity_penalty = 0.05 * transform_len
    risk = collision_risk(query_terms[: match.prefix_overlap] or query_terms)
    return round(max(0.0, exact * 0.5 + overlap * 0.5 - complexity_penalty - 0.3 * risk), 4)


@dataclass
class HeldOutResult:
    formula: str
    checked_terms: int
    passed: bool


def held_out_verification(
    formula_fn: Callable[[int], int], held_out: list[tuple[int, int]], *, formula: str = ""
) -> HeldOutResult:
    """Test a candidate closed form against held-out (index, value) pairs."""
    if not held_out:
        return HeldOutResult(formula=formula, checked_terms=0, passed=False)
    ok = True
    checked = 0
    for index, value in held_out:
        checked += 1
        try:
            if formula_fn(index) != value:
                ok = False
                break
        except Exception:
            ok = False
            break
    return HeldOutResult(formula=formula, checked_terms=checked, passed=ok)


@dataclass
class OEISWorkflowResult:
    query_terms: list[int]
    transform_paths: list[list[TransformStep]]
    ranked_matches: list[tuple[Match, float]]
    held_out: list[HeldOutResult]
    conjecture_claim: dict

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_terms": self.query_terms,
            "transform_paths": [[s.label() for s in p] for p in self.transform_paths],
            "ranked_matches": [{"a_number": m.a_number, "score": s} for m, s in self.ranked_matches],
            "held_out": [h.__dict__ for h in self.held_out],
            "conjecture_claim": self.conjecture_claim,
        }


def enumerate_transform_paths(seq: list[int]) -> list[list[TransformStep]]:
    """Generate a deduplicated set of local transform paths for a sequence."""
    candidates = [
        [TransformStep("identity")],
        [TransformStep("first_difference")],
        [TransformStep("partial_sums")],
        [TransformStep("drop_prefix", {"count": 1})],
        [TransformStep("even_subsequence")],
        [TransformStep("odd_subsequence")],
    ]
    seen: set[str] = set()
    paths: list[list[TransformStep]] = []
    for path in candidates:
        try:
            transformed = apply_path(seq, path)
        except TransformError:
            continue
        key = content_id([int(x) if float(x).is_integer() else str(x) for x in transformed])
        if key in seen:
            continue
        seen.add(key)
        paths.append(path)
    return paths


def build_conjecture_claim(
    interpretation_id: str, query_terms: list[int], best: tuple[Match, float] | None,
    held_out: list[HeldOutResult],
) -> dict:
    """A NUMERICAL_EVIDENCE conjecture node descriptor (never a proof)."""
    supported_formula = next(
        (h.formula for h in held_out if h.passed and h.checked_terms > 0), ""
    )
    supported = bool(best is not None and supported_formula)
    return {
        "interpretation_id": interpretation_id,
        "kind": "oeis_conjecture",
        "evidence_kind": "numerical",
        "truth_tier": "T1_supported_conjecture" if supported else "T0_unknown",
        "query_terms": query_terms,
        "matched_a_number": best[0].a_number if best else None,
        "held_out_supported_formula": supported_formula,
        "note": "OEIS match is a conjecture/literature pointer; not a proof. "
                "'Not found' is not evidence of novelty.",
    }


def run_oeis_workflow(
    *,
    interpretation_id: str,
    query_terms: list[int],
    candidate_matches: list[Match],
    held_out: list[HeldOutResult] | None = None,
) -> OEISWorkflowResult:
    paths = enumerate_transform_paths(query_terms)
    ranked = sorted(
        ((m, score_match(query_terms, m, transform_len=len(m.matched_transform)))
         for m in candidate_matches),
        key=lambda ms: ms[1], reverse=True,
    )
    held = held_out or []
    best = ranked[0] if ranked else None
    claim = build_conjecture_claim(interpretation_id, query_terms, best, held)
    return OEISWorkflowResult(query_terms, paths, ranked, held, claim)
