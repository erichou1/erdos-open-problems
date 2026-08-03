"""Learning plane (Module K): memory stores, calibration, expert iteration."""

from egmra.learning.calibration import (
    CalibrationLedger,
    brier_score,
    credible_interval_coverage,
    expected_calibration_error,
    log_score,
)
from egmra.learning.expert_iteration import (
    TrainingExample,
    VerifiedOnlyExpertIteration,
)
from egmra.learning.memory import MEMORY_TABLE, LongTermMemory, MemoryStore

__all__ = [
    "CalibrationLedger", "brier_score", "credible_interval_coverage",
    "expected_calibration_error", "log_score",
    "TrainingExample", "VerifiedOnlyExpertIteration",
    "MEMORY_TABLE", "LongTermMemory", "MemoryStore",
]
