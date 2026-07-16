"""Closed, auditable policies used by the Erdős problem selector."""

from __future__ import annotations

from typing import Literal


PrizeStatus = Literal["unpaid", "paid", "unknown"]
PRIZE_POLICY_VERSION = "strict-unpaid-first-v1"


def classify_prize(value: object) -> PrizeStatus:
    """Classify raw first-party prize metadata without currency conversion."""
    if not isinstance(value, str) or not value.strip():
        return "unknown"
    normalized = value.strip()
    if normalized.casefold() == "no":
        return "unpaid"
    if any(character.isdigit() for character in normalized):
        return "paid"
    return "unknown"


def selection_priority_tier(prize_status: str) -> int:
    """Return the strict solve-allocation tier, rejecting incomplete metadata."""
    if prize_status == "unpaid":
        return 0
    if prize_status == "paid":
        return 1
    raise ValueError("unknown prize metadata cannot enter allocation")
