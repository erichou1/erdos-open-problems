"""Search-algorithm routing per abstraction level (spec §6.7, §7.1).

Different algorithms match different topologies, connected through the claim graph:
Thompson/UCB across programs, a diversity-preserving MAP-Elites archive for
top-level mechanisms, AO*/best-first on the AND/OR claim graph, PUCT for exact Lean
states, evolutionary islands only for executable candidates, and debate/critique
only to *propose* defects/experiments — never as a truth oracle.
"""

from __future__ import annotations

import math

SEARCH_LEVEL_ALGORITHMS = {
    "problem_acquisition": "contextual_thompson_ucb",
    "research_programs": "contextual_thompson_ucb",
    "mechanism_archive": "map_elites_best_first",
    "andor_blueprint": "ao_star_best_first",
    "lean_proof_state": "puct_mcts_beam",
    "executable_candidates": "evolutionary_islands",
    "defect_discovery": "debate_propose_only",
}


def route_search_level(level: str) -> str:
    if level not in SEARCH_LEVEL_ALGORITHMS:
        raise KeyError(f"unknown search level {level!r}")
    return SEARCH_LEVEL_ALGORITHMS[level]


def ucb1(mean_reward: float, total_pulls: int, arm_pulls: int, *, c: float = 1.4) -> float:
    """UCB1 arm score. Unpulled arms get +inf so they are tried first."""
    if arm_pulls == 0:
        return float("inf")
    return mean_reward + c * math.sqrt(math.log(max(1, total_pulls)) / arm_pulls)


def ao_star_next_leaf(open_leaves: list[dict]) -> str | None:
    """Pick the next AND/OR leaf: highest centrality per unit expected cost."""
    if not open_leaves:
        return None
    def key(leaf: dict) -> float:
        return leaf.get("centrality", 0.0) / max(1e-6, leaf.get("cost", 1.0))
    return max(open_leaves, key=key)["node_id"]


def evolution_allowed(*, has_executable_fitness: bool, has_independent_checker: bool) -> bool:
    """Evolutionary promotion is restricted to hard-evaluator executable domains
    (spec §2.4, §6.7). General proof-strategy evolution is forbidden."""
    return has_executable_fitness and has_independent_checker


def debate_output_role() -> str:
    """Debate/critique may only propose defects/experiments/branch revisions."""
    return "propose_defects_experiments_or_branch_revisions_never_truth"
