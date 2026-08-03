"""Theorem-library / premise retrieval (spec §8.5).

Formal retrieval accepts informal and typed queries and returns
:class:`PremiseCandidate` objects. A proof worker may use a candidate only after
elaboration (``compiled_in_context``); the source auditor separately checks an
informal paper theorem was not silently strengthened during formal linkage.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from egmra.retrieval.records import PremiseCandidate

# Split declaration names on dots/underscores/camelCase so "Nat.add_comm" matches
# an informal "add comm nat" query.
_TOKEN = re.compile(r"[A-Za-z0-9]+")


def _subtokens(text: str) -> set[str]:
    parts: list[str] = []
    for tok in _TOKEN.findall(text):
        parts.append(tok)
        parts.extend(re.findall(r"[A-Z]?[a-z]+|[0-9]+|[A-Z]+(?![a-z])", tok))
    return {p.lower() for p in parts if p}


@dataclass
class PremiseRetrievalRequest:
    natural_claim: str = ""
    lean_goal: str = ""
    local_context: tuple[str, ...] = ()
    imports: tuple[str, ...] = ()
    mathlib_commit: str = ""
    max_premises: int = 10
    modes: tuple[str, ...] = ("dense", "lexical", "type-shape")

    def query_text(self) -> str:
        return " ".join([self.natural_claim, self.lean_goal, *self.local_context])


@dataclass
class PremiseLibrary:
    """A local index of formal declarations for premise retrieval."""

    declarations: list[PremiseCandidate] = field(default_factory=list)

    def _score(self, query: str, cand: PremiseCandidate) -> float:
        q = _subtokens(query)
        d = _subtokens(cand.declaration_name + " " + cand.declaration_type)
        if not q or not d:
            return 0.0
        overlap = len(q & d)
        return round(overlap / math.sqrt(len(q) * len(d)), 4)

    def retrieve_premises(self, request: PremiseRetrievalRequest) -> list[PremiseCandidate]:
        query = request.query_text()
        scored: list[tuple[PremiseCandidate, float]] = []
        for cand in self.declarations:
            score = self._score(query, cand)
            if score > 0.0:
                scored.append((
                    PremiseCandidate(
                        declaration_name=cand.declaration_name,
                        declaration_type=cand.declaration_type,
                        imports=cand.imports,
                        source_file=cand.source_file,
                        source_commit=cand.source_commit or request.mathlib_commit,
                        dependencies=cand.dependencies,
                        retrieval_scores={**cand.retrieval_scores, "lexical": score},
                        compiled_in_context=cand.compiled_in_context,
                    ),
                    score,
                ))
        scored.sort(key=lambda cs: cs[1], reverse=True)
        return [c for c, _ in scored[: request.max_premises]]


def usable_premises(candidates: list[PremiseCandidate]) -> list[PremiseCandidate]:
    """Filter to premises that actually elaborated in the current context."""
    return [c for c in candidates if c.usable_after_elaboration()]
