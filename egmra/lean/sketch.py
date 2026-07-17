"""Formal-native AND/OR proof sketches (effectiveness report R4, phase 1).

A *sketch* is a Lean source in which the community target theorem is proved
FROM named subgoal lemmas whose proofs are ``sorry``. If the sketch
development-compiles (warm service, sorries allowed), the decomposition
"these children suffice for the target" is MACHINE-CHECKED — Lean elaborated
the parent proof term — instead of being model prose. Each sorried child then
becomes an independent formalization obligation for the existing pipeline
(Aristotle dispatch → sealed kernel → lemma library), so children compound.

TRUST BOUNDARY (deliberate, load-bearing):

* Sketch artifacts are DEVELOPMENT-ONLY. A compiling sketch asserts nothing
  about truth: it contains ``sorry`` and can never reach the sealed checker,
  the truth graph, or a release gate. Only per-child sealed
  ``FormalCertificate``s (obtained through the unchanged pipeline) carry
  authority.
* Anti-circularity: a child whose statement is essentially the target is
  REJECTED (the decomposition would be vacuous). Token overlap is a cheap
  necessary filter; Lean-level equivalence can survive rewording, so
  rejected-child review stays in the report for the operator.

Scope: only problems with a community Lean target (``targets/<id>.lean``)
qualify — the target statement is the pinned obligation the sketch must
close.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from egmra.provenance.hashing import sha256_hex

_MAX_CHILDREN = 12
_CIRCULARITY_JACCARD = 0.9

# One sorried child declaration: `lemma name : TYPE := sorry` (multi-line
# types allowed; `by sorry` allowed; the tempered middle cannot cross into the
# next declaration). Sketches follow this CONTRACT format — the prompt demands
# it and the parser enforces it, keeping regex parsing honest instead of
# pretending to parse Lean. Children must state the FULL obligation in the
# type (∀-form), never in binders, so each statement is directly usable as a
# sealed-checker ``expected_type_source``.
_CHILD_RE = re.compile(
    r"^[ \t]*(?:private\s+)?(?:lemma|theorem)\s+([A-Za-z_][A-Za-z0-9_'.]*)"
    r"((?:(?!^[ \t]*(?:private\s+)?(?:lemma|theorem)\s)[\s\S])*?)"
    r":=\s*(?:by\s+)?sorry[ \t]*$",
    re.MULTILINE,
)
_DECL_RE = re.compile(
    r"^\s*(?:private\s+)?(?:lemma|theorem)\s+([A-Za-z_][A-Za-z0-9_'.]*)",
    re.MULTILINE,
)
_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
# Explicit formalization-friendly weakenings, recorded in the sketch itself
# (`-- DIVERGENCE: <what was weakened and why>`). The strongest public
# verification records keep exactly this fidelity note machine-readable so a
# kernel-checked weaker statement is never silently conflated with the
# informal target.
_DIVERGENCE_RE = re.compile(r"^[ \t]*--[ \t]*DIVERGENCE:[ \t]*(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class SketchChild:
    """One sorried subgoal lemma — a future formalization obligation."""

    name: str
    statement: str          # binders + type source, verbatim from the sketch

    def to_obligation(self) -> dict[str, str]:
        return {
            "declaration_name": self.name,
            "expected_type_source": self.statement,
            "source": "",              # to be produced by the prover pipeline
            "origin": "sketch_child",
        }


@dataclass(frozen=True)
class SketchReport:
    """Everything an operator (or later automation) needs about one sketch."""

    problem_id: str
    target_declaration: str
    source_hash: str
    children: tuple[SketchChild, ...] = ()
    rejected_children: tuple[str, ...] = ()     # circularity rejections
    problems: tuple[str, ...] = ()              # structural contract violations
    divergences: tuple[str, ...] = ()           # recorded formalization weakenings
    compiled: bool | None = None                # None = no dev service ran
    dev_sorries: int | None = None
    dev_messages: tuple[str, ...] = ()

    @property
    def viable(self) -> bool:
        """Structurally valid AND (if dev-compiled) accepted by Lean."""
        return not self.problems and (self.compiled is not False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "problem_id": self.problem_id,
            "target_declaration": self.target_declaration,
            "source_hash": self.source_hash,
            "children": [
                {"name": c.name, "statement": c.statement} for c in self.children
            ],
            "obligations": [c.to_obligation() for c in self.children],
            "rejected_children": list(self.rejected_children),
            "problems": list(self.problems),
            "divergences": list(self.divergences),
            "compiled": self.compiled,
            "dev_sorries": self.dev_sorries,
            "dev_messages": list(self.dev_messages),
            "viable": self.viable,
            "authority": (
                "development-only sketch; never a proof, never releasable — "
                "each child needs its own sealed FormalCertificate"
            ),
        }


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text)}


def _essentially_target(statement: str, target_statement: str) -> bool:
    a, b = _tokens(statement), _tokens(target_statement)
    if not a or not b:
        return False
    union = a | b
    return len(a & b) / len(union) >= _CIRCULARITY_JACCARD


def validate_sketch(source: str, *, problem_id: str, target_declaration: str,
                    target_statement: str = "") -> SketchReport:
    """Parse + structurally validate one sketch against the contract format.

    Contract: the sketch declares the target (NOT sorried) proved from ≤12
    sorried child lemmas, each ``lemma name ... : TYPE := sorry``. No truth
    judgement happens here — only shape and anti-circularity.
    """
    text = str(source)
    problems: list[str] = []
    children: list[SketchChild] = []
    rejected: list[str] = []

    declared = _DECL_RE.findall(text)
    sorried = {name: sig for name, sig in _CHILD_RE.findall(text)}

    if target_declaration not in declared:
        problems.append(f"target_declaration_missing:{target_declaration}")
    if target_declaration in sorried:
        problems.append(f"target_is_sorried:{target_declaration}")
    if not sorried:
        problems.append("no_sorried_children:sketch decomposes nothing")

    for name, signature in sorried.items():
        if name == target_declaration:
            continue
        raw = str(signature).strip()
        if not raw.startswith(":"):
            # Binder-form children (`lemma f (n : ℕ) : …`) are rejected by
            # contract: the obligation must be one bare type expression
            # (`lemma f : ∀ n : ℕ, …`) so it feeds the sealed checker's
            # `example : TYPE := @decl` obligation unchanged.
            problems.append(
                f"child_has_binders:{name} (state as `lemma {name} : ∀ …`)")
            continue
        statement = " ".join(raw[1:].split()).strip()
        if not statement:
            problems.append(f"child_missing_statement:{name}")
            continue
        if target_statement and _essentially_target(statement, target_statement):
            rejected.append(name)
            continue
        children.append(SketchChild(name=name, statement=statement))

    if len(children) > _MAX_CHILDREN:
        problems.append(
            f"too_many_children:{len(children)}>{_MAX_CHILDREN}")
        children = children[:_MAX_CHILDREN]
    if not children and not problems:
        problems.append("all_children_rejected_as_circular")

    return SketchReport(
        problem_id=problem_id,
        target_declaration=target_declaration,
        source_hash=sha256_hex(text),
        children=tuple(children),
        rejected_children=tuple(rejected),
        problems=tuple(problems),
        divergences=tuple(
            " ".join(note.split()) for note in _DIVERGENCE_RE.findall(text)[:12]),
    )


def compile_sketch(report: SketchReport, source: str,
                   dev_service: Any) -> SketchReport:
    """Development-compile the sketch; sorries are EXPECTED here.

    ``compiled=True`` means Lean elaborated the parent proof term from the
    sorried children — the AND-decomposition is machine-checked. Any error
    (including a dead dev service) fails OPEN to ``compiled=False`` /
    unavailability recorded in ``dev_messages``; never an exception out.
    """
    from dataclasses import replace

    try:
        result = dev_service.check(str(source))
    except Exception as exc:  # noqa: BLE001 - dev service isolation
        return replace(report, compiled=None, dev_messages=(
            f"dev_service_unavailable:{type(exc).__name__}:{exc}",))
    messages = tuple(result.messages)
    if result.ok and result.sorries != len(report.children):
        messages = messages + ((
            f"sorry_count_mismatch:expected {len(report.children)} "
            f"children, REPL reported {result.sorries}"),)
    return replace(
        report,
        compiled=bool(result.ok),
        dev_sorries=int(result.sorries),
        dev_messages=messages,
    )
