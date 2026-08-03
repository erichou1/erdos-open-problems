"""Pessimistic aggregation + conflict flow (spec §11.4).

Do not average reviewer scores. A single valid central defect blocks promotion.
Conflicting reviews trigger issue normalization, targeted evidence, a fresh
adjudicator blind to reviewer identities/status, formal/executable resolution
where possible, and ``unknown`` if the conflict remains. Consensus among
correlated models raises search priority, never truth tier.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReviewVerdict:
    reviewer_id: str
    lineage: str
    verdict: str          # pass | fail | unknown
    central_defect: bool = False

    def __post_init__(self) -> None:
        if not self.reviewer_id or not self.lineage:
            raise ValueError("reviewer id and lineage are required")
        if self.verdict not in {"pass", "fail", "unknown"}:
            raise ValueError(f"invalid review verdict {self.verdict!r}")
        if self.central_defect and self.verdict != "fail":
            raise ValueError("only a failing review may report a central defect")


@dataclass(frozen=True)
class AggregationResult:
    decision: str          # promote_ok | blocked | conflict_unknown
    reason: str
    priority_boost: float = 0.0
    needs_fresh_adjudicator: bool = False


def aggregate(verdicts: list[ReviewVerdict]) -> AggregationResult:
    """Pessimistic aggregation (never an average)."""
    if not verdicts:
        return AggregationResult("blocked", "no reviews")
    reviewer_ids = [verdict.reviewer_id for verdict in verdicts]
    if len(reviewer_ids) != len(set(reviewer_ids)):
        raise ValueError("duplicate reviewer identities are not independent reviews")

    # A single valid central defect blocks promotion.
    if any(v.verdict == "fail" and v.central_defect for v in verdicts):
        return AggregationResult("blocked", "valid central defect found")

    fails = [v for v in verdicts if v.verdict == "fail"]
    passes = [v for v in verdicts if v.verdict == "pass"]
    unknowns = [v for v in verdicts if v.verdict == "unknown"]

    if unknowns:
        return AggregationResult(
            "conflict_unknown", "one or more review obligations remain unknown",
            needs_fresh_adjudicator=bool(fails or passes),
        )

    # Conflicting reviews -> fresh adjudicator, not an average.
    if fails and passes:
        return AggregationResult(
            "conflict_unknown", "conflicting reviews; escalate to fresh adjudicator",
            needs_fresh_adjudicator=True,
        )
    if fails:
        return AggregationResult("blocked", "review(s) failed")

    # All pass: correlated consensus only raises priority, not truth tier.
    distinct_lineages = {v.lineage for v in passes}
    if len(passes) > 1 and len(distinct_lineages) < 2:
        return AggregationResult(
            "search_priority_only",
            "correlated all-pass reviews may guide search but cannot authorize promotion",
            priority_boost=0.1,
        )
    priority_boost = 0.1 * len(distinct_lineages)
    return AggregationResult("promote_ok", "all reviews pass (truth tier unchanged by consensus)",
                             priority_boost=priority_boost)


@dataclass
class ConflictResolution:
    """The §11.4 conflict-resolution flow with an identity-blind adjudicator."""

    normalized_issue: str
    targeted_evidence: list[str] = field(default_factory=list)
    formal_or_executable_resolution: str = ""
    adjudicator_blind_to_identities: bool = True

    def resolve(self) -> str:
        if self.formal_or_executable_resolution:
            return self.formal_or_executable_resolution
        return "unknown"          # conflict remains -> unknown, never averaged
