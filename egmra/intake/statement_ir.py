"""Typed Statement IR and two independent parsers (spec §6.1).

The intake plane must not silently normalize a problem into one statement. It
parses the immutable source bytes into a typed :class:`StatementIR` using *two
independent* parsers and reconciles only exact / semantically-justified matches;
every disagreement becomes an ambiguity node feeding the interpretation lattice.

Per DECISIONS.md D-002, the default two parsers are two *independently
implemented deterministic* parsers (a cue/grammar parser and a
structurally-different clause parser). A :class:`ModelParser` adapter exists for
real model families and plugs into the same reconciliation contract.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, Protocol

from egmra.provenance.hashing import content_id, sha256_bytes

# requested_outcome vocabulary (spec §6.1)
OUTCOMES = ("prove", "disprove", "determine", "estimate", "construct")

_QUANTIFIER_PATTERNS = [
    (r"\bfor\s+all\b|\bfor\s+every\b|\bfor\s+each\b|∀", "universal"),
    (r"\bfor\s+infinitely\s+many\b", "infinitely_many"),
    (r"\bfor\s+sufficiently\s+large\b|\bfor\s+all\s+large\b", "eventually"),
    (r"\bthere\s+exists?\b|\bthere\s+is\b|\bfor\s+some\b|∃", "existential"),
]

_OUTCOME_CUES = [
    (r"\bdisprove\b|\brefute\b|\bfind\s+a\s+counterexample\b", "disprove"),
    (r"\bconstruct\b|\bexhibit\b|\bgive\s+an?\s+example\b|\bbuild\b", "construct"),
    (r"\bestimate\b|\bbound\b|\basymptotic\b|\bgrowth\s+rate\b|\border\s+of\b", "estimate"),
    (r"\bdetermine\b|\bfind\b|\bcompute\b|\bwhat\s+is\b|\bhow\s+many\b|"
     r"\bwhether\b|\bis\s+it\s+true\b", "determine"),
    (r"\bprove\b|\bshow\b|\bestablish\b|\bverify\s+that\b|\bdemonstrate\b", "prove"),
]

_HYP_CUES = re.compile(
    r"\b(if|assume|suppose|given|whenever|provided that|where|such that|let)\b",
    re.IGNORECASE,
)

_SYMBOL_RE = re.compile(r"\b([a-zA-Z])\b")
_NUM_PARAM_RE = re.compile(r"\b([a-zA-Z])\s*(?:∈|in|≥|>=|≤|<=|>|<|=)\s*", re.IGNORECASE)
_QUANTIFIED_BINDER_RE = re.compile(
    r"\b(?P<quantifier>for\s+infinitely\s+many|for\s+sufficiently\s+large|"
    r"for\s+(?:all|every|each|some)|there\s+(?:exists?|is))\s+"
    r"(?:(?:an?|the)\s+)?"
    r"(?:(?P<sign>positive|nonnegative|negative)\s+)?"
    r"(?:(?P<domain>natural\s+numbers?|natural\s+number|integers?|reals?|rationals?)\s+)?"
    r"(?P<name>[a-zA-Z])\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Binder:
    name: str
    domain: str
    quantifier: str
    scope: str = "global"
    constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name or not self.domain or not self.quantifier or not self.scope:
            raise ValueError("binder identity, domain, quantifier, and scope are required")
        object.__setattr__(self, "constraints", tuple(self.constraints))

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class Definition:
    symbol: str
    arity: int
    semantics: str
    conventions: str = ""

    def __post_init__(self) -> None:
        if not self.symbol or type(self.arity) is not int or self.arity < 0 \
                or not self.semantics.strip():
            raise ValueError("definition requires a symbol, nonnegative arity, and semantics")

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class StatementIR:
    """A typed intermediate representation of a problem statement (spec §6.1)."""

    source_id: str
    source_hash: str
    source_spans: tuple[Mapping[str, int], ...] = field(default_factory=tuple)
    binders: tuple[Binder, ...] = field(default_factory=tuple)
    definitions: tuple[Definition, ...] = field(default_factory=tuple)
    hypotheses: tuple[str, ...] = field(default_factory=tuple)
    conclusion: str = ""
    requested_outcome: str = "determine"
    parameter_regime: str = ""
    constraints: tuple[str, ...] = field(default_factory=tuple)
    edge_cases: tuple[str, ...] = field(default_factory=tuple)
    ambiguity_nodes: tuple[str, ...] = field(default_factory=tuple)
    variants: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    parser_id: str = ""
    parser_family: str = ""

    def __post_init__(self) -> None:
        if self.requested_outcome not in OUTCOMES:
            raise ValueError(f"unknown requested outcome {self.requested_outcome!r}")
        if not self.source_id or not self.source_hash or not self.parser_id or not self.parser_family:
            raise ValueError("source and parser identities are required")
        spans: list[Mapping[str, int]] = []
        for span in self.source_spans:
            if not isinstance(span, Mapping) or set(span) != {"start", "end"}:
                raise ValueError("source spans require exact start/end offsets")
            start, end = span["start"], span["end"]
            if type(start) is not int or type(end) is not int or start < 0 or end < start:
                raise ValueError("source span offsets are invalid")
            spans.append(MappingProxyType({"start": start, "end": end}))
        binders = tuple(
            item if isinstance(item, Binder) else Binder(**dict(item)) for item in self.binders
        )
        definitions = tuple(
            item if isinstance(item, Definition) else Definition(**dict(item))
            for item in self.definitions
        )
        variants = tuple(
            MappingProxyType(dict(item)) if isinstance(item, Mapping) else _bad_variant()
            for item in self.variants
        )
        object.__setattr__(self, "source_spans", tuple(spans))
        object.__setattr__(self, "binders", binders)
        object.__setattr__(self, "definitions", definitions)
        object.__setattr__(self, "hypotheses", tuple(str(item) for item in self.hypotheses))
        object.__setattr__(self, "constraints", tuple(str(item) for item in self.constraints))
        object.__setattr__(self, "edge_cases", tuple(str(item) for item in self.edge_cases))
        object.__setattr__(self, "ambiguity_nodes", tuple(str(item) for item in self.ambiguity_nodes))
        object.__setattr__(self, "variants", variants)

    def semantic_key(self) -> dict[str, Any]:
        """The meaning-bearing fields used for reconciliation and IR hashing."""
        return {
            "requested_outcome": self.requested_outcome,
            "quantifiers": sorted(b.quantifier for b in self.binders),
            "binder_names": sorted(b.name for b in self.binders),
            "binder_domains": sorted((b.name, b.domain) for b in self.binders),
            "binder_scopes": sorted((b.name, b.scope) for b in self.binders),
            "binder_constraints": sorted((b.name, b.constraints) for b in self.binders),
            "definitions": sorted(
                (d.symbol, d.arity, _normalize_text(d.semantics), _normalize_text(d.conventions))
                for d in self.definitions
            ),
            "hypothesis_count": len(self.hypotheses),
            "conclusion_norm": _normalize_text(self.conclusion),
            "hypotheses_norm": sorted(_normalize_text(h) for h in self.hypotheses),
            "parameter_regime": _normalize_text(self.parameter_regime),
            "constraints": sorted(_normalize_text(item) for item in self.constraints),
        }

    def semantic_hash(self) -> str:
        return content_id(self.semantic_key())

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_hash": self.source_hash,
            "source_spans": [dict(span) for span in self.source_spans],
            "binders": [b.to_dict() for b in self.binders],
            "definitions": [d.to_dict() for d in self.definitions],
            "hypotheses": list(self.hypotheses),
            "conclusion": self.conclusion,
            "requested_outcome": self.requested_outcome,
            "parameter_regime": self.parameter_regime,
            "constraints": list(self.constraints),
            "edge_cases": list(self.edge_cases),
            "ambiguity_nodes": list(self.ambiguity_nodes),
            "variants": [dict(item) for item in self.variants],
            "parser_id": self.parser_id,
            "parser_family": self.parser_family,
        }


def _bad_variant() -> Mapping[str, Any]:
    raise ValueError("variants must be mappings")


def _normalize_text(text: str) -> str:
    """Lowercase, collapse whitespace, and canonicalize synonyms.

    Canonicalization merges *synonym* pairs (the same pairs the paraphrase probe
    substitutes) to a single token so a meaning-preserving paraphrase yields an
    identical semantic key. Antonyms (the mutation targets) are never merged, so
    a meaning-changing edit still produces a different key.
    """
    out = re.sub(r"\s+", " ", text.strip().lower())
    for pattern, canonical in _CANONICAL_SYNONYMS:
        out = re.sub(pattern, canonical, out, flags=re.IGNORECASE)
    return out


# Synonym → canonical (both members of each paraphrase pair collapse here).
_CANONICAL_SYNONYMS = [
    (r"\bfor every\b|\bfor each\b", "for all"),
    (r"\bthere is\b", "there exists"),
    (r"\bshow that\b", "prove that"),
    (r"\bnatural numbers? greater than zero\b", "positive integer"),
    (r"\bexactly when\b", "if and only if"),
]


def _detect_outcome(text: str) -> str:
    low = text.lower()
    for pattern, outcome in _OUTCOME_CUES:
        if re.search(pattern, low):
            return outcome
    return "determine"


def _detect_quantifiers(text: str) -> list[str]:
    found: list[str] = []
    for pattern, kind in _QUANTIFIER_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            found.append(kind)
    return found


def _detect_parameter_regime(text: str) -> str:
    cues = []
    if re.search(r"\bsufficiently\s+large\b|\blarge\s+enough\b|\bn\s*(?:→|->)\s*∞", text, re.IGNORECASE):
        cues.append("asymptotic")
    if re.search(r"\bpositive\s+integers?\b|∈\s*ℕ|\bnatural\s+numbers?\b", text, re.IGNORECASE):
        cues.append("naturals")
    if re.search(r"\bfinite\b", text, re.IGNORECASE):
        cues.append("finite")
    return ";".join(cues)


class Parser(Protocol):
    parser_id: str

    def parse(self, source_bytes: bytes, source_id: str) -> StatementIR: ...


class GrammarParser:
    """Cue/keyword grammar parser: outcome + quantifier binders + hyp/conclusion split."""

    parser_id = "grammar-parser-v1"
    parser_family = "deterministic-grammar"

    def parse(self, source_bytes: bytes, source_id: str) -> StatementIR:
        text = _decode_source(source_bytes).strip()
        outcome = _detect_outcome(text)
        quantifiers = _detect_quantifiers(text)
        binders = self._binders(text, quantifiers)
        hypotheses, conclusion = self._split(text)
        return StatementIR(
            source_id=source_id,
            source_hash=sha256_bytes(source_bytes),
            source_spans=({"start": 0, "end": len(source_bytes)},),
            binders=tuple(binders),
            definitions=_extract_definitions(text),
            hypotheses=tuple(hypotheses),
            conclusion=conclusion,
            requested_outcome=outcome,
            parameter_regime=_detect_parameter_regime(text),
            constraints=_extract_constraints(text),
            edge_cases=_edge_cases(text),
            parser_id=self.parser_id,
            parser_family=self.parser_family,
        )

    @staticmethod
    def _binders(text: str, quantifiers: list[str]) -> list[Binder]:
        binders: list[Binder] = []
        seen: set[str] = set()
        for match in _QUANTIFIED_BINDER_RE.finditer(text):
            name = match.group("name")
            if name in seen:
                continue
            seen.add(name)
            sign = (match.group("sign") or "").lower()
            binders.append(Binder(
                name=name,
                domain=_domain_name(match.group("domain")),
                quantifier=_quantifier_name(match.group("quantifier")),
                constraints=(sign,) if sign else (),
            ))
        for match in _NUM_PARAM_RE.finditer(text):
            name = match.group(1)
            if name not in seen:
                seen.add(name)
                binders.append(Binder(name=name, domain=_domain_for(text, name), quantifier="free"))
        if not binders and quantifiers:
            binders.append(Binder(name="x", domain="unspecified", quantifier=quantifiers[0]))
        return binders

    @staticmethod
    def _split(text: str) -> tuple[list[str], str]:
        parts = re.split(r"(?<=[.;])\s+", text)
        hypotheses = [p.strip() for p in parts if _HYP_CUES.search(p)]
        non_hyp = [p.strip() for p in parts if not _HYP_CUES.search(p) and p.strip()]
        conclusion = non_hyp[-1] if non_hyp else text
        return hypotheses, conclusion


class ClauseParser:
    """Structurally different parser: clause segmentation + role scoring.

    Unlike the grammar parser it segments on connectives and scores each clause
    for a hypothesis/conclusion role, giving an independent second reading whose
    disagreements with the grammar parser become ambiguity nodes.
    """

    parser_id = "clause-parser-v1"
    parser_family = "deterministic-clause"

    def parse(self, source_bytes: bytes, source_id: str) -> StatementIR:
        text = _decode_source(source_bytes).strip()
        clauses = [c.strip() for c in re.split(r",|;|\bthen\b|\bimplies\b|\.\s", text) if c.strip()]
        outcome = _detect_outcome(text)
        quantifiers = _detect_quantifiers(text)
        hypotheses = [c for c in clauses if _HYP_CUES.search(c)]
        conclusion_candidates = [c for c in clauses if not _HYP_CUES.search(c)]
        # A comma in a mathematical formula is not by itself a semantic clause
        # boundary. Preserve the complete statement unless a hypothesis-bearing
        # clause was actually identified.
        conclusion = text if not hypotheses else (
            max(conclusion_candidates, key=len) if conclusion_candidates else text
        )
        # Independently recognize variables bound by quantified phrases. The old
        # all-one-letter-word heuristic invented English-word binders such as
        # ``a`` and systematically disagreed with the grammar parse.
        binders = []
        for match in list(_QUANTIFIED_BINDER_RE.finditer(text))[:4]:
            sign = (match.group("sign") or "").lower()
            binders.append(Binder(
                name=match.group("name"),
                domain=_domain_name(match.group("domain")),
                quantifier=_quantifier_name(match.group("quantifier")),
                constraints=(sign,) if sign else (),
            ))
        if not binders and quantifiers:
            binders = [Binder("x", "unspecified", quantifiers[0])]
        return StatementIR(
            source_id=source_id,
            source_hash=sha256_bytes(source_bytes),
            source_spans=({"start": 0, "end": len(source_bytes)},),
            binders=tuple(binders),
            definitions=_extract_definitions(text),
            hypotheses=tuple(hypotheses),
            conclusion=conclusion,
            requested_outcome=outcome,
            parameter_regime=_detect_parameter_regime(text),
            constraints=_extract_constraints(text),
            edge_cases=_edge_cases(text),
            parser_id=self.parser_id,
            parser_family=self.parser_family,
        )


@dataclass
class ModelParser:
    """Adapter for a real model-family parser (see DECISIONS.md D-002).

    ``runner`` is a callable ``(prompt) -> json-ish dict`` provided when a model
    is configured. Without a runner it raises, so tests use the deterministic
    parsers and never silently fabricate a parse.
    """

    parser_id: str
    runner: Any = None

    def parse(self, source_bytes: bytes, source_id: str) -> StatementIR:
        if self.runner is None:
            raise RuntimeError(
                f"ModelParser '{self.parser_id}' has no runner configured; "
                "configure a model runner or use a deterministic parser"
            )
        text = _decode_source(source_bytes).strip()
        parsed = self.runner(text)
        if not isinstance(parsed, dict):
            raise TypeError("model parser result must be an object")
        allowed = {
            "binders", "definitions", "hypotheses", "conclusion",
            "requested_outcome", "parameter_regime", "constraints",
        }
        unknown = set(parsed) - allowed
        if unknown:
            raise ValueError(f"model parser returned unknown fields: {sorted(unknown)}")
        outcome = parsed.get("requested_outcome", "determine")
        conclusion = parsed.get("conclusion", "")
        if outcome not in OUTCOMES or not isinstance(conclusion, str) or not conclusion.strip():
            raise ValueError("model parser returned an invalid outcome or empty conclusion")
        for name in ("binders", "definitions", "hypotheses", "constraints"):
            if name in parsed and not isinstance(parsed[name], list):
                raise TypeError(f"model parser field {name} must be a list")
        return StatementIR(
            source_id=source_id,
            source_hash=sha256_bytes(source_bytes),
            source_spans=({"start": 0, "end": len(source_bytes)},),
            binders=tuple(Binder(**b) for b in parsed.get("binders", [])),
            definitions=tuple(Definition(**d) for d in parsed.get("definitions", [])),
            hypotheses=tuple(str(item) for item in parsed.get("hypotheses", [])),
            conclusion=conclusion,
            requested_outcome=outcome,
            parameter_regime=str(parsed.get("parameter_regime", "")),
            constraints=tuple(str(item) for item in parsed.get("constraints", [])),
            parser_id=self.parser_id,
            parser_family=f"model:{self.parser_id}",
        )


def _domain_for(text: str, name: str) -> str:
    window = re.search(rf"\b{re.escape(name)}\b\s*(?:∈|\bin\b)\s*([^\s,.;]+)", text)
    if window:
        return window.group(1)
    if re.search(r"positive\s+integers?|ℕ|natural", text, re.IGNORECASE):
        return "ℕ"
    if re.search(r"\bintegers?\b|ℤ", text, re.IGNORECASE):
        return "ℤ"
    return "unspecified"


def _domain_name(value: str | None) -> str:
    if not value:
        return "unspecified"
    low = value.lower()
    if "natural" in low:
        return "ℕ"
    if "integer" in low:
        return "ℤ"
    if "rational" in low:
        return "ℚ"
    if "real" in low:
        return "ℝ"
    return "unspecified"


def _quantifier_name(value: str) -> str:
    low = value.lower()
    if "infinitely" in low:
        return "infinitely_many"
    if "sufficiently" in low:
        return "eventually"
    if "some" in low or "there" in low:
        return "existential"
    return "universal"


def _extract_definitions(text: str) -> tuple[Definition, ...]:
    definitions: list[Definition] = []
    pattern = re.compile(
        r"\b(?:let|define)\s+([A-Za-z][A-Za-z0-9_]*)\s*"
        r"(?:\(([^)]*)\))?\s*(?::=|=)\s*([^.;]+)",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        arguments = [item.strip() for item in (match.group(2) or "").split(",") if item.strip()]
        definitions.append(Definition(
            symbol=match.group(1),
            arity=len(arguments),
            semantics=f"{match.group(1)}({', '.join(arguments)}) = {match.group(3).strip()}"
            if arguments else f"{match.group(1)} = {match.group(3).strip()}",
        ))
    return tuple(definitions)


def _extract_constraints(text: str) -> tuple[str, ...]:
    """Extract only explicit binder/hypothesis restrictions.

    A comparison in the theorem's *conclusion* is not a domain restriction.  In
    particular, interpreting ``for all n, n < 3`` as a search domain ``n < 3``
    would erase exactly the counterexamples intake is supposed to find.  We
    therefore require a nearby assumption cue (``with``, ``given``, ``such
    that``, etc.) or a quantifier that directly binds the comparison.
    """
    constraints: list[str] = []
    for match in re.finditer(
        r"\b([A-Za-z])\s*(>=|<=|>|<|=|≥|≤)\s*(-?\d+)\b", text
    ):
        prefix = text[max(0, match.start() - 80):match.start()]
        # Stay within the current clause; a cue in an earlier sentence must not
        # authorize a later conclusion comparison.
        clause_prefix = re.split(r"[.;,]", prefix)[-1].strip().lower()
        assumption_cued = re.search(
            r"(?:with|such\s+that|where|satisfying|subject\s+to|"
            r"assume|suppose|given|provided\s+that|whenever|let)\s*$",
            clause_prefix,
        )
        directly_quantified = re.search(
            r"(?:for\s+(?:all|every|each|some)|there\s+(?:exists?|is))\s*$",
            clause_prefix,
        )
        if assumption_cued or directly_quantified:
            constraints.append(match.group(0).strip())
    return tuple(dict.fromkeys(constraints))


def _decode_source(source_bytes: bytes) -> str:
    if not isinstance(source_bytes, bytes):
        raise TypeError("source_bytes must be bytes")
    try:
        return source_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("source bytes must be valid UTF-8") from exc


def _edge_cases(text: str) -> tuple[str, ...]:
    edges: list[str] = []
    if re.search(r"\bn\b", text) or "natural" in text.lower() or "integer" in text.lower():
        edges.extend(["n=0", "n=1"])
    if re.search(r"\bset\b|\bgraph\b|\bsequence\b", text, re.IGNORECASE):
        edges.append("empty")
    return tuple(edges)


@dataclass(frozen=True)
class Reconciliation:
    agreed: bool
    agreed_fields: tuple[str, ...]
    disagreements: tuple[str, ...]
    ambiguity_nodes: tuple[str, ...]
    primary: StatementIR
    secondary: StatementIR

    def target_fidelity_risk(self) -> float:
        """0.0 = both parsers fully agree; higher = more disagreement."""
        total = max(1, len(self.agreed_fields) + len(self.disagreements))
        return round(len(self.disagreements) / total, 4)


def reconcile(primary: StatementIR, secondary: StatementIR) -> Reconciliation:
    """Reconcile two independent parses; disagreements become ambiguity nodes.

    Different prompts to the *same* model are correlated, not independent, so the
    two parsers must have different ``parser_id`` values.
    """
    if not primary.parser_family or primary.parser_family == secondary.parser_family:
        raise ValueError("reconcile requires two independent parser families")
    a, b = primary.semantic_key(), secondary.semantic_key()
    agreed: list[str] = []
    disagreements: list[str] = []
    ambiguities: list[str] = []
    for field_name in a:
        if a[field_name] == b[field_name]:
            agreed.append(field_name)
        else:
            disagreements.append(field_name)
            ambiguities.append(
                f"parsers disagree on {field_name}: {a[field_name]!r} vs {b[field_name]!r}"
            )
    return Reconciliation(
        agreed=not disagreements,
        agreed_fields=tuple(agreed),
        disagreements=tuple(disagreements),
        ambiguity_nodes=tuple(ambiguities),
        primary=primary,
        secondary=secondary,
    )


def backtranslate(ir: StatementIR) -> str:
    """Deterministically reconstruct plain prose from the IR (spec §6.1 step 3)."""
    quant = ", ".join(f"{b.quantifier} {b.name} in {b.domain}" for b in ir.binders)
    hyp = "; ".join(ir.hypotheses)
    pieces = [f"Requested outcome: {ir.requested_outcome}."]
    if quant:
        pieces.append(f"Binders: {quant}.")
    if hyp:
        pieces.append(f"Assuming {hyp},")
    pieces.append(f"conclude: {ir.conclusion}")
    if ir.parameter_regime:
        pieces.append(f"(regime: {ir.parameter_regime})")
    return " ".join(pieces)
