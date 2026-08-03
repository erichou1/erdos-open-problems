"""Corpus & status hygiene (spec §8.1).

"Open" is a *dated status claim* with a source and review date, never a fact baked
into a filename. The system distinguishes the date a status changed from the date
a problem was mathematically solved, refreshes status (or uses a recent signed
snapshot), and turns a conflict into ``status_uncertain`` plus a literature task —
never an automatic proof campaign.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from egmra.provenance.hashing import content_id

STATUS_VALUES = ("open", "known", "false", "misquoted", "ambiguous", "status_uncertain")


@dataclass(frozen=True)
class CorpusSnapshot:
    """A pinned upstream snapshot (spec §8.1: pin a commit, not a drifting page)."""

    repository: str
    commit: str
    snapshot_date: str
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class StatusClaim:
    """A single dated status assertion from one source."""

    problem_id: str
    status: str
    source: str
    review_date: str
    status_change_date: str = ""     # when the status last changed
    solution_date: str = ""          # distinct: when it was mathematically solved
    source_independence: str = "unknown"

    def __post_init__(self) -> None:
        if self.status not in STATUS_VALUES:
            raise ValueError(f"unknown status {self.status!r}; expected one of {STATUS_VALUES}")

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class StatusResolution:
    problem_id: str
    resolved_status: str
    claims: list[StatusClaim] = field(default_factory=list)
    conflict: bool = False
    literature_task: dict | None = None

    @property
    def blocks_proof_campaign(self) -> bool:
        # A conflict or an uncertain status must not auto-launch a proof campaign.
        return self.conflict or self.resolved_status == "status_uncertain"

    def to_dict(self) -> dict[str, Any]:
        return {
            "problem_id": self.problem_id,
            "resolved_status": self.resolved_status,
            "claims": [c.to_dict() for c in self.claims],
            "conflict": self.conflict,
            "literature_task": self.literature_task,
            "blocks_proof_campaign": self.blocks_proof_campaign,
            "resolution_hash": content_id({
                "problem_id": self.problem_id,
                "resolved_status": self.resolved_status,
                "claims": sorted(c.to_dict().items().__str__() for c in self.claims),
            }),
        }


def reconcile_status(problem_id: str, claims: list[StatusClaim]) -> StatusResolution:
    """Reconcile multiple dated status claims into a single resolution.

    Distinct statuses across sources produce ``status_uncertain`` and a literature
    task, never a silent choice of the most convenient reading.
    """
    if not claims:
        return StatusResolution(
            problem_id=problem_id, resolved_status="status_uncertain",
            claims=[], conflict=False,
            literature_task={"reason": "no status source", "action": "search_status"},
        )
    distinct = {c.status for c in claims}
    if len(distinct) == 1:
        return StatusResolution(
            problem_id=problem_id, resolved_status=next(iter(distinct)), claims=list(claims)
        )
    return StatusResolution(
        problem_id=problem_id, resolved_status="status_uncertain", claims=list(claims),
        conflict=True,
        literature_task={
            "reason": f"conflicting status claims: {sorted(distinct)}",
            "action": "resolve_status_conflict",
            "sources": [c.source for c in claims],
        },
    )
