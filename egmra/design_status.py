"""Machine-readable design-status table (spec §5.3, §1).

Each design choice carries an evidence status: ``established`` (mature mechanism /
independently checkable), ``demonstrated`` (author-reported / artifact-backed),
``plausible`` (engineering hypothesis), or ``original`` (a new proposal that must
be tested). This encodes the spec's own epistemic honesty as queryable data.
"""

from __future__ import annotations

from dataclasses import dataclass

STATUS_VALUES = ("established", "demonstrated", "plausible", "original")


@dataclass(frozen=True)
class DesignChoice:
    choice: str
    support: str
    status: str

    def __post_init__(self) -> None:
        if self.status not in STATUS_VALUES:
            raise ValueError(f"unknown design status {self.status!r}")


DESIGN_STATUS: dict[str, DesignChoice] = {
    d.choice: d for d in [
        DesignChoice("kernel_certificate_validation", "Lean/Isabelle/Rocq/Metamath/AlphaProof", "established"),
        DesignChoice("generator_critic_repair_loop", "Aletheia, QED, compiler-feedback agents", "demonstrated"),
        DesignChoice("formal_blueprint_dynamic_leaves", "LEAP, Goedel-Architect, LeanMarathon", "demonstrated"),
        DesignChoice("dependency_graph_revocation", "Danus; build-system practice", "demonstrated"),
        DesignChoice("theorem_retrieval_before_search", "LeanSearch v2, ReProver, QED, Rethlas", "demonstrated"),
        DesignChoice("evolution_under_hard_fitness", "FunSearch, AlphaEvolve", "demonstrated"),
        DesignChoice("cold_pass_then_mandatory_retrieval", "anchoring control + retrieval evidence", "original"),
        DesignChoice("interpretation_lattice", "Aletheia/autoformalization failures", "original"),
        DesignChoice("risk_weighted_lean_sentinels", "formalization-cost + semantic-risk evidence", "original"),
        DesignChoice("epistemic_compiler_per_claim", "claim graph + typed obligations", "original"),
        DesignChoice("posterior_branch_allocation", "bandits, VOI, dependency search", "plausible"),
        DesignChoice("separate_novelty_firewall", "repeated rediscovery in Erdos efforts", "original"),
    ]
}


def design_status(choice: str) -> DesignChoice:
    if choice not in DESIGN_STATUS:
        raise KeyError(f"unknown design choice {choice!r}")
    return DESIGN_STATUS[choice]


def originals() -> list[str]:
    """Design choices that are original proposals and MUST be tested (ablations)."""
    return sorted(c for c, d in DESIGN_STATUS.items() if d.status == "original")
