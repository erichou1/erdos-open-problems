"""Adversarial calibration and anti-forgery tests for persistent learning."""

from __future__ import annotations

import math

import pytest

from egmra.learning import (
    CalibrationLedger,
    LongTermMemory,
    brier_score,
    credible_interval_coverage,
    expected_calibration_error,
    log_score,
)


@pytest.mark.parametrize(
    "predictions",
    [[(math.nan, 1)], [(1.1, 1)], [(-0.1, 0)], [(0.5, 2)], [(0.5, True)]],
)
def test_calibration_metrics_reject_invalid_probability_records(predictions) -> None:
    for metric in (brier_score, log_score, expected_calibration_error):
        with pytest.raises(ValueError):
            metric(predictions)


def test_calibration_bins_and_intervals_are_validated() -> None:
    with pytest.raises(ValueError):
        expected_calibration_error([(0.5, 1)], bins=0)
    with pytest.raises(ValueError):
        credible_interval_coverage([(0.9, 0.1, 0.5)])
    with pytest.raises(ValueError):
        credible_interval_coverage([(0.0, 1.0, math.nan)])


def test_calibration_ledger_rejects_forged_shapes() -> None:
    ledger = CalibrationLedger()
    with pytest.raises(ValueError):
        ledger.record_prediction(2.0, 1)
    with pytest.raises(ValueError):
        ledger.record_promotion(false_positive="no")


def test_truthy_dicts_alone_cannot_promote_persistent_semantic_memory() -> None:
    memory = LongTermMemory()
    assert not memory.promote_verified_fact({
        "theorem_hash": "h" * 64,
        "kernel_or_certificate_replay": True,
        "dependency_audit": True,
    })

