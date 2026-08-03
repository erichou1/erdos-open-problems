"""L3 — proof-state search: portfolio, PUCT, diagnostics routing (spec §9.2 L3, §7.3).

Search operates on tactic segments and auxiliary-lemma proposals as well as single
tactics. Diagnostics route syntax / missing-premise / false-target / library-gap /
decomposition-failure to *different* repair policies. Transpositions are keyed by
the full GoalCapsule, never by pretty-printed text.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# The proof-state portfolio (spec §9.2 L3). Aristotle is an optional high-budget
# candidate worker, never the trusted checker.
PROOF_PORTFOLIO = (
    "direct_whole_proof_agent",
    "reprover_premise_bestfirst",
    "pantograph_multigoal_tree",
    "oprover_goedel_deepseek_repair",
    "aristotle_optional_candidate",
    "tactic_set_aesop_linarith_nlinarith_ring_omega",
    "sledgehammer_export_reconstruct",
    "formal_negation_counterexample",
)

# Diagnostic -> repair policy routing.
_DIAGNOSTIC_ROUTES = {
    "syntax_error": "resyntax_and_retry",
    "missing_premise": "retrieve_premises",
    "false_target": "revise_target_or_search_counterexample",
    "library_gap": "create_scoped_local_library",
    "decomposition_failure": "revise_blueprint_leaves",
    "type_mismatch": "elaborate_and_repair_types",
    "timeout": "increase_budget_or_decompose",
}


def route_diagnostic(diagnostic: str) -> str:
    return _DIAGNOSTIC_ROUTES.get(diagnostic, "escalate_to_governor")


def puct_score(
    *, q: float, prior: float, parent_visits: int, action_visits: int,
    delta_verified_debt: float, cost: float,
    c_puct: float = 1.4, beta: float = 0.5, gamma: float = 0.05,
) -> float:
    """PUCT(s,a) = Q + c·P·√N/(1+n) + β·Δdebt − γ·cost (spec §7.3)."""
    exploration = c_puct * prior * math.sqrt(max(0, parent_visits)) / (1 + action_visits)
    return round(q + exploration + beta * delta_verified_debt - gamma * cost, 6)


@dataclass
class TranspositionTable:
    """Exact-goal cache keyed by GoalCapsule.key() (spec §7.3, §9.3)."""

    _store: dict[str, dict] = field(default_factory=dict)

    def get(self, capsule_key: str) -> dict | None:
        return self._store.get(capsule_key)

    def put(self, capsule_key: str, result: dict) -> None:
        self._store[capsule_key] = dict(result)

    def __len__(self) -> int:
        return len(self._store)


@dataclass(frozen=True)
class ProofAction:
    worker: str
    tactic_or_lemma: str
    is_segment: bool = False

    def __post_init__(self) -> None:
        if self.worker not in PROOF_PORTFOLIO:
            raise ValueError(f"unknown proof worker {self.worker!r}")
