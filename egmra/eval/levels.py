"""Seven difficulty levels + A/B/C tracks (spec §12.1)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DifficultyLevel:
    level: int
    evaluation_set: str
    primary_capability: str
    ground_truth: str


LEVELS = {
    1: DifficultyLevel(1, "elementary algebra/number theory/logic; false/ambiguous variants",
                       "parsing, edge cases, basic formal proof", "exact answer and kernel proof"),
    2: DifficultyLevel(2, "miniF2F, verified ProofNet#, pinned IMO-LeanProofBench Basic",
                       "olympiad reasoning, autoformalization, premise retrieval",
                       "versioned formal statements/proofs"),
    3: DifficultyLevel(3, "pinned PutnamBench and IMO-LeanProofBench Advanced",
                       "longer proof plans and formal search",
                       "kernel replay plus human statement audit"),
    4: DifficultyLevel(4, "fresh problems requiring cited literature",
                       "theorem retrieval and hypothesis application",
                       "hidden source packet and expert grading"),
    5: DifficultyLevel(5, "construction/enumeration/finite-reduction tasks",
                       "computation plus proof/certificate",
                       "independent executable verifier and proof"),
    6: DifficultyLevel(6, "previously solved Erdos problems hidden behind a historical cutoff",
                       "full research workflow, status and novelty",
                       "dated source snapshot and held-out solution"),
    7: DifficultyLevel(7, "currently unsolved Erdos problems",
                       "genuine research progress",
                       "no answer key; blind experts, formal artifacts, later literature"),
}

# Levels 2-3 report three separate tracks (spec §12.1).
TRACKS = {
    "A": "proof search with an audited Lean statement supplied",
    "B": "NL-to-Lean autoformalization with independent semantic grading before proof search",
    "C": "end-to-end work from the raw source",
}


def level(n: int) -> DifficultyLevel:
    if n not in LEVELS:
        raise KeyError(f"unknown level {n}; expected 1..7")
    return LEVELS[n]


def requires_tracks(n: int) -> bool:
    return n in (2, 3)


def scores_accuracy(n: int) -> bool:
    # Level 7 never scores "accuracy" (spec §12.2).
    return n != 7
