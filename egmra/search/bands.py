"""Progressive compute bands 0-5 (spec §7.8).

Compute scales because evidence warrants expansion, not because a fixed tab count
must stay busy. A 10-20% reserve is kept for surprise branches, independent
verification, and recovery. All defaults are engineering defaults, not
evidence-backed optima (they are the subject of Section 12 ablations).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ComputeBand:
    level: int
    purpose: str
    typical_actions: tuple[str, ...]
    expansion_condition: str


BANDS = (
    ComputeBand(0, "integrity", ("dual_parse", "status_check", "tiny_cases"),
                "target/status coherent"),
    ComputeBand(1, "cheap_probes", ("cold_scratch", "local_enumeration", "retrieval_sketch"),
                "nontrivial route or falsifier found"),
    ComputeBand(2, "portfolio", ("4_to_8_mechanism_distinct_programs", "solver_packet"),
                "at least one branch has positive posterior value"),
    ComputeBand(3, "lemma_research", ("dynamic_leaves", "serious_computation", "lean_sentinels"),
                "verified debt decreases or information gain remains high"),
    ComputeBand(4, "deep_campaign", ("days_long_branches", "specialist_models", "full_formalization"),
                "central path credible and verification capacity available"),
    ComputeBand(5, "release", ("independent_replay", "novelty_expert_review", "hardening"),
                "all required gates can plausibly close"),
)

RESERVE_FRACTION_RANGE = (0.10, 0.20)


def band(level: int) -> ComputeBand:
    if not 0 <= level < len(BANDS):
        raise ValueError(f"compute band {level} out of range 0..{len(BANDS)-1}")
    return BANDS[level]


def can_expand(current_level: int, condition_met: bool) -> bool:
    """Advance to the next band only when the current band's condition is met."""
    return condition_met and current_level < len(BANDS) - 1


def reserve_amount(total_budget: float, fraction: float = 0.15) -> float:
    lo, hi = RESERVE_FRACTION_RANGE
    fraction = min(hi, max(lo, fraction))
    return round(total_budget * fraction, 6)
