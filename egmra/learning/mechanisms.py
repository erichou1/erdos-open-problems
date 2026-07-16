"""Mechanism tagging at write time (effectiveness report R10, the cheap half).

The full "mechanism library" (retrieve mechanisms by mathematical structure
and obstruction) is deferred until there is a corpus worth retrieving from.
What ships now is the part that must run EARLY to be useful later: every
dossier outcome and sealed lemma is tagged with coarse mechanism keywords at
write time, so the corpus accumulates structure from today. Tags are search
metadata only — they carry no authority and never touch truth.
"""

from __future__ import annotations

import re

_MAX_TAGS = 8

# Coarse, deliberately unclever taxonomy: each tag fires on surface keywords.
# The point is accumulation, not understanding — a retrieval layer can be
# built later ON TOP of these without rewriting history.
_TAXONOMY: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (tag, re.compile(pattern, re.IGNORECASE))
    for tag, pattern in (
        ("probabilistic", r"probabilist|random|expectation|variance|lovász local|chernoff|martingale"),
        ("density_increment", r"density|increment|szemerédi|regularity"),
        ("pigeonhole", r"pigeonhole|dirichlet box"),
        ("induction", r"induction|inductive|minimal counterexample|infinite descent"),
        ("coloring", r"color|colour|chromatic|ramsey"),
        ("extremal", r"extremal|turán|maximal|minimal size|threshold"),
        ("spectral", r"spectral|eigenvalue|adjacency matrix|expander"),
        ("polynomial_method", r"polynomial method|combinatorial nullstellensatz|slice rank"),
        ("fourier_analytic", r"fourier|exponential sum|character sum|circle method"),
        ("sieve", r"sieve|brun|selberg"),
        ("entropy_counting", r"entropy|counting argument|double counting"),
        ("greedy_constructive", r"greedy|explicit construction|constructive"),
        ("compactness", r"compactness|ultrafilter|de bruijn"),
        ("ergodic_dynamical", r"ergodic|dynamical|recurrence"),
        ("modular_arithmetic", r"modul|congruen|residue"),
        ("sat_finite", r"\bsat\b|cnf|exhaustive|finite check|case analysis"),
        ("formalization", r"\blean\b|mathlib|formaliz|kernel"),
    )
)


def mechanism_tags(text: str) -> tuple[str, ...]:
    """Coarse mechanism keywords present in ``text`` (bounded, deterministic)."""
    haystack = str(text or "")[:4000]
    if not haystack.strip():
        return ()
    return tuple(
        tag for tag, pattern in _TAXONOMY if pattern.search(haystack)
    )[:_MAX_TAGS]
