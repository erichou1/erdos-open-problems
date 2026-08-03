"""Statistical policy guards (spec §12.6)."""

from __future__ import annotations

from dataclasses import dataclass


class StatisticalPolicyError(RuntimeError):
    pass


def compare_pass_at_k(a_k: int, b_k: int) -> None:
    """Never compare pass@1 with pass@32/1024 or unmatched budgets (spec §12.6)."""
    if a_k != b_k:
        raise StatisticalPolicyError(
            f"cannot compare pass@{a_k} with pass@{b_k}; match budgets or report a curve")


@dataclass(frozen=True)
class ReportedResult:
    numerator: int
    denominator: int
    interval_low: float
    interval_high: float
    censored: int
    paired: bool

    def __post_init__(self) -> None:
        if self.denominator <= 0:
            raise StatisticalPolicyError("must report an exact nonzero denominator")
        if not (0 <= self.numerator <= self.denominator):
            raise StatisticalPolicyError("numerator must lie between zero and denominator")
        if not (0 <= self.censored <= self.denominator):
            raise StatisticalPolicyError("censored count must lie between zero and denominator")
        if not (0.0 <= self.interval_low <= self.interval_high <= 1.0):
            raise StatisticalPolicyError("interval must satisfy 0 <= low <= high <= 1")
        if not (self.interval_low <= self.numerator / self.denominator <= self.interval_high):
            raise StatisticalPolicyError("reported interval must contain the point estimate")
        if type(self.paired) is not bool:
            raise StatisticalPolicyError("paired must be a boolean")

    def rate(self) -> float:
        return round(self.numerator / self.denominator, 6)


def dev_eval_separated(dev_packet_hash: str, eval_packet_hash: str) -> bool:
    """Development and sealed evaluation source packets must be separate."""
    return dev_packet_hash != eval_packet_hash


def treat_recent_preprint_as_hypothesis(independently_reproduced: bool) -> str:
    """Very recent preprint claims are hypotheses until independent rerun/replay."""
    return "established" if independently_reproduced else "hypothesis"


def requires_two_blind_experts(high_value: bool) -> int:
    """High-value informal claims need at least two blind referees."""
    return 2 if high_value else 1
