"""Verification-congestion pricing (spec §14.6, §7.10).

Without deduplication and value calibration, orchestration spends more while
proving less. When the verification backlog grows relative to capacity, the price
of opening new proof branches rises and generators are throttled — but this is a
scheduling signal, never a truth downgrade.
"""

from __future__ import annotations

from dataclasses import dataclass


def congestion_price(backlog: int, capacity: int, *, base: float = 1.0) -> float:
    """Price grows super-linearly as backlog approaches/exceeds capacity."""
    if capacity <= 0:
        return float("inf")
    ratio = backlog / capacity
    return round(base * (1.0 + ratio ** 2), 4)


@dataclass
class CongestionController:
    capacity: int
    throttle_ratio: float = 1.0     # throttle generators when backlog >= capacity

    def should_throttle_generation(self, backlog: int) -> bool:
        return backlog >= self.capacity * self.throttle_ratio

    def branch_open_cost(self, backlog: int, base_cost: float) -> float:
        return round(base_cost * congestion_price(backlog, self.capacity), 4)

    def affects_truth(self) -> bool:
        return False    # congestion pricing is scheduling only, never truth
