"""Integrity, boundary, paraphrase/mutation, and counterexample probes (spec §6.1).

Probes are real and runnable. The paraphrase-invariance and mutation-covariance
probes exercise the parser: a faithful parser must produce the *same* IR under a
meaning-preserving paraphrase and a *different* IR under a meaning-changing local
mutation. The boundary/counterexample probes accept an optional executable
predicate so they genuinely enumerate small cases; without one they honestly
record that no executable predicate was available.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Iterable

from egmra.intake.statement_ir import GrammarParser, Parser, StatementIR
from egmra.provenance.hashing import content_id

# Meaning-preserving synonym substitutions (paraphrase should not change meaning).
_PARAPHRASE = [
    (r"\bfor all\b", "for every"),
    (r"\bthere exists\b", "there is"),
    (r"\bprove that\b", "show that"),
    (r"\bpositive integer\b", "natural number greater than zero"),
    (r"\bif and only if\b", "exactly when"),
]

# Meaning-changing local mutations (parser must be sensitive to these).
_MUTATIONS = [
    (r"\bfor all\b", "for some"),
    (r"\bfor every\b", "for some"),
    (r"\bthere exists\b", "for all"),
    (r"\bprove\b", "disprove"),
    (r"\bat least\b", "at most"),
    (r"\binfinitely many\b", "finitely many"),
]


@dataclass(frozen=True)
class Probe:
    name: str
    kind: str  # invariance|covariance|boundary|counterexample|dimensional
    passed: bool
    detail: str
    executed: bool = True
    artifacts: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def paraphrase(text: str) -> str:
    out = text
    for pattern, repl in _PARAPHRASE:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def mutate(text: str) -> tuple[str, bool]:
    """Return (mutated_text, changed). ``changed`` is False if no rule applied."""
    for pattern, repl in _MUTATIONS:
        if re.search(pattern, text, re.IGNORECASE):
            return re.sub(pattern, repl, text, count=1, flags=re.IGNORECASE), True
    return text, False


def paraphrase_invariance_probe(source_bytes: bytes, source_id: str, parser: Parser) -> Probe:
    original = parser.parse(source_bytes, source_id)
    para = paraphrase(source_bytes.decode("utf-8", errors="replace"))
    if para == source_bytes.decode("utf-8", errors="replace"):
        return Probe("paraphrase_invariance", "invariance", False,
                     "no meaning-preserving paraphrase rule was applicable", executed=False)
    para_ir = parser.parse(para.encode("utf-8"), source_id)
    invariant = original.semantic_hash() == para_ir.semantic_hash()
    return Probe(
        "paraphrase_invariance", "invariance", invariant,
        "IR is invariant under meaning-preserving paraphrase" if invariant
        else "IR changed under a paraphrase that should preserve meaning",
        True,
        {"original": original.semantic_hash(), "paraphrase": para_ir.semantic_hash()},
    )


def mutation_covariance_probe(source_bytes: bytes, source_id: str, parser: Parser) -> Probe:
    original = parser.parse(source_bytes, source_id)
    text = source_bytes.decode("utf-8", errors="replace")
    mutated, changed = mutate(text)
    if not changed:
        return Probe("mutation_covariance", "covariance", False,
                     "no meaning-changing mutation rule was applicable", executed=False)
    mut_ir = parser.parse(mutated.encode("utf-8"), source_id)
    covariant = original.semantic_hash() != mut_ir.semantic_hash()
    return Probe(
        "mutation_covariance", "covariance", covariant,
        "IR is sensitive to a meaning-changing mutation" if covariant
        else "IR ignored a meaning-changing local edit (insensitive parser)",
        True,
        {"original": original.semantic_hash(), "mutation": mut_ir.semantic_hash()},
    )


def dimensional_type_probe(ir: StatementIR) -> Probe:
    unspecified = [b.name for b in ir.binders if b.domain == "unspecified"]
    passed = not unspecified or bool(ir.parameter_regime)
    return Probe(
        "dimensional_type", "dimensional", passed,
        "all binders typed or a parameter regime is recorded" if passed
        else f"binders without a domain and no regime: {unspecified}",
        True,
        {"unspecified_binders": unspecified},
    )


def boundary_enumeration_probe(
    ir: StatementIR,
    *,
    predicate: Callable[[int], bool] | None = None,
    boundary_points: Iterable[int] = (0, 1, 2),
) -> Probe:
    """Check the predicate on boundary/degenerate points when one is executable."""
    if predicate is None:
        return Probe("boundary_enumeration", "boundary", False,
                     "no executable predicate supplied; boundary probe not run", False,
                     {"executable": False, "tested_points": []})
    points = list(boundary_points)
    if not points:
        return Probe("boundary_enumeration", "boundary", False,
                     "no in-domain boundary points were available", False,
                     {"executable": True, "tested_points": []})
    failures = [n for n in points if not _safe(predicate, n)]
    passed = not failures
    return Probe(
        "boundary_enumeration", "boundary", passed,
        "predicate holds on all boundary points" if passed
        else f"predicate fails at boundary points {failures}",
        True,
        {"executable": True, "boundary_failures": failures, "tested_points": points},
    )


def counterexample_probe(
    *,
    predicate: Callable[[int], bool] | None = None,
    search_space: Iterable[int] = range(0, 64),
) -> Probe:
    """Search the smallest domain for a counterexample when one is executable."""
    if predicate is None:
        return Probe("counterexample_search", "counterexample", False,
                     "no executable predicate supplied; counterexample search not run", False,
                     {"executable": False, "searched_points": []})
    points = list(search_space)
    if not points:
        return Probe("counterexample_search", "counterexample", False,
                     "no in-domain points were available", False,
                     {"executable": True, "searched_points": []})
    for n in points:
        if not _safe(predicate, n):
            return Probe(
                "counterexample_search", "counterexample", False,
                f"counterexample found at n={n}",
                True,
                {"executable": True, "counterexample": n, "searched_points": points},
            )
    return Probe("counterexample_search", "counterexample", True,
                 "no counterexample in the searched domain",
                 True, {"executable": True, "searched_points": points})


def run_integrity_probes(
    source_bytes: bytes,
    source_id: str,
    ir: StatementIR,
    *,
    parser: Parser | None = None,
    predicate: Callable[[int], bool] | None = None,
    boundary_points: Iterable[int] = (0, 1, 2),
    search_space: Iterable[int] = range(0, 64),
) -> list[Probe]:
    """Run the full §6.1 integrity-probe battery."""
    parser = parser or GrammarParser()
    boundary = tuple(n for n in boundary_points if _in_scope(ir, n))
    search = tuple(n for n in search_space if _in_scope(ir, n))
    return [
        paraphrase_invariance_probe(source_bytes, source_id, parser),
        mutation_covariance_probe(source_bytes, source_id, parser),
        dimensional_type_probe(ir),
        boundary_enumeration_probe(ir, predicate=predicate, boundary_points=boundary),
        counterexample_probe(predicate=predicate, search_space=search),
    ]


def probes_hash(probes: list[Probe]) -> str:
    return content_id([p.to_dict() for p in probes])


def _safe(predicate: Callable[[int], bool], n: int) -> bool:
    try:
        return bool(predicate(n))
    except Exception:
        # An exception at a boundary point is itself a boundary failure.
        return False


def _in_scope(ir: StatementIR, n: int) -> bool:
    if type(n) is not int:
        return False
    binders = ir.binders
    if binders:
        binder = binders[0]
        if binder.domain == "ℕ" and n < 0:
            return False
        if "positive" in binder.constraints and n <= 0:
            return False
        if "nonnegative" in binder.constraints and n < 0:
            return False
        if "negative" in binder.constraints and n >= 0:
            return False
    for constraint in ir.constraints:
        match = re.fullmatch(r"[A-Za-z]\s*(>=|≥|<=|≤|>|<|=)\s*(-?\d+)", constraint)
        if not match:
            continue
        op, raw = match.groups()
        bound = int(raw)
        if op in (">=", "≥") and not n >= bound:
            return False
        if op in ("<=", "≤") and not n <= bound:
            return False
        if op == ">" and not n > bound:
            return False
        if op == "<" and not n < bound:
            return False
        if op == "=" and not n == bound:
            return False
    return True
