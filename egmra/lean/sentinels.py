"""L1 sentinels + risk-weighted formal coverage F(c) (spec §9.2 L1, §9.5).

Formalize early: type/domain sanity, boundary/degenerate cases,
monotonicity/symmetry assumptions, finite cases, and the central lemma with the
highest calibrated combination of dependency centrality, semantic risk, and
false-branch cost. Do *not* formalize every prose claim (spec §4.3 item 5).
"""

from __future__ import annotations

from dataclasses import dataclass

SENTINEL_KINDS = ("type_domain", "boundary", "monotonicity_symmetry", "finite_case", "central_lemma")


@dataclass(frozen=True)
class FormalizationPriority:
    claim_id: str
    priority: float
    is_sentinel: bool
    rationale: str


def formalization_priority(
    *, claim_id: str, centrality: float, semantic_risk: float, dispute_probability: float,
    downstream_loss: float, reuse: float, formalization_cost: float,
    weights: tuple[float, ...] = (0.30, 0.25, 0.15, 0.20, 0.10),
) -> float:
    """F(c) = (w1·centrality + w2·risk + w3·dispute + w4·downstream + w5·reuse) / cost."""
    w1, w2, w3, w4, w5 = weights
    numerator = (w1 * centrality + w2 * semantic_risk + w3 * dispute_probability
                 + w4 * downstream_loss + w5 * reuse)
    return round(numerator / max(1e-6, formalization_cost), 4)


def select_sentinels(
    claims: list[dict], *, central_threshold: float = 0.6, risk_threshold: float = 0.5,
) -> list[FormalizationPriority]:
    """Choose which claims to formalize early. Low-risk glue can wait."""
    out: list[FormalizationPriority] = []
    # always-sentinel structural claims
    for claim in claims:
        kind = claim.get("sentinel_kind")
        centrality = float(claim.get("centrality", 0.0))
        risk = float(claim.get("semantic_risk", 0.0))
        priority = formalization_priority(
            claim_id=claim["claim_id"], centrality=centrality, semantic_risk=risk,
            dispute_probability=float(claim.get("dispute_probability", 0.0)),
            downstream_loss=float(claim.get("downstream_loss", centrality)),
            reuse=float(claim.get("reuse", 0.0)),
            formalization_cost=float(claim.get("formalization_cost", 1.0)),
        )
        is_sentinel = (
            kind in {"type_domain", "boundary", "monotonicity_symmetry", "finite_case"}
            or (centrality >= central_threshold and risk >= risk_threshold)
        )
        rationale = (
            f"structural sentinel ({kind})" if kind in SENTINEL_KINDS and kind != "central_lemma"
            else "high centrality×risk central lemma" if is_sentinel
            else "low-risk glue; formalization deferred"
        )
        out.append(FormalizationPriority(claim["claim_id"], priority, is_sentinel, rationale))
    out.sort(key=lambda p: p.priority, reverse=True)
    return out
