"""Calibration ledger metrics (spec §12.3 calibration)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field


def _validate_predictions(predictions: list[tuple[float, int]]) -> None:
    for item in predictions:
        if not isinstance(item, tuple) or len(item) != 2:
            raise ValueError("prediction records must be (probability, outcome) tuples")
        probability, outcome = item
        if not isinstance(probability, (int, float)) or isinstance(probability, bool) \
                or not math.isfinite(float(probability)) or not 0 <= probability <= 1:
            raise ValueError("prediction probability must be finite and in [0, 1]")
        if type(outcome) is not int or outcome not in {0, 1}:
            raise ValueError("prediction outcome must be integer 0 or 1")


def brier_score(predictions: list[tuple[float, int]]) -> float:
    """Mean squared error of probabilistic predictions vs binary outcomes."""
    _validate_predictions(predictions)
    if not predictions:
        return 0.0
    return round(sum((p - y) ** 2 for p, y in predictions) / len(predictions), 6)


def log_score(predictions: list[tuple[float, int]]) -> float:
    _validate_predictions(predictions)
    if not predictions:
        return 0.0
    total = 0.0
    for p, y in predictions:
        p = min(1 - 1e-9, max(1e-9, p))
        total += -(y * math.log(p) + (1 - y) * math.log(1 - p))
    return round(total / len(predictions), 6)


def expected_calibration_error(predictions: list[tuple[float, int]], *, bins: int = 10) -> float:
    """ECE over equal-width probability bins."""
    _validate_predictions(predictions)
    if not isinstance(bins, int) or isinstance(bins, bool) or bins <= 0:
        raise ValueError("bins must be a positive integer")
    if not predictions:
        return 0.0
    buckets: list[list[tuple[float, int]]] = [[] for _ in range(bins)]
    for p, y in predictions:
        idx = min(bins - 1, int(p * bins))
        buckets[idx].append((p, y))
    n = len(predictions)
    ece = 0.0
    for bucket in buckets:
        if not bucket:
            continue
        conf = sum(p for p, _ in bucket) / len(bucket)
        acc = sum(y for _, y in bucket) / len(bucket)
        ece += (len(bucket) / n) * abs(conf - acc)
    return round(ece, 6)


def credible_interval_coverage(intervals: list[tuple[float, float, float]]) -> float:
    """Fraction of (low, high, actual) intervals that contain the actual value."""
    for interval in intervals:
        if not isinstance(interval, tuple) or len(interval) != 3:
            raise ValueError("intervals must be (low, high, actual) tuples")
        lo, hi, actual = interval
        if any(not isinstance(value, (int, float)) or isinstance(value, bool)
               or not math.isfinite(float(value)) for value in interval):
            raise ValueError("interval values must be finite numbers")
        if lo > hi:
            raise ValueError("credible interval lower bound exceeds upper bound")
    if not intervals:
        return 0.0
    covered = sum(1 for lo, hi, actual in intervals if lo <= actual <= hi)
    return round(covered / len(intervals), 6)


@dataclass
class CalibrationLedger:
    predictions: list[tuple[float, int]] = field(default_factory=list)
    false_promotions: int = 0
    total_promotions: int = 0

    def record_prediction(self, probability: float, outcome: int) -> None:
        _validate_predictions([(probability, outcome)])
        self.predictions.append((probability, outcome))

    def record_promotion(self, *, false_positive: bool) -> None:
        if not isinstance(false_positive, bool):
            raise ValueError("false_positive must be boolean")
        self.total_promotions += 1
        if false_positive:
            self.false_promotions += 1

    def false_promotion_rate(self) -> float:
        if self.total_promotions == 0:
            return 0.0
        return round(self.false_promotions / self.total_promotions, 6)

    def report(self) -> dict:
        return {
            "brier": brier_score(self.predictions),
            "log_score": log_score(self.predictions),
            "ece": expected_calibration_error(self.predictions),
            "false_promotion_rate": self.false_promotion_rate(),
            "n": len(self.predictions),
        }
