"""Tests for the learning plane: memory stores, calibration, expert iteration."""

from egmra.learning import (
    CalibrationLedger,
    LongTermMemory,
    TrainingExample,
    VerifiedOnlyExpertIteration,
    brier_score,
    expected_calibration_error,
)


# ── memory ────────────────────────────────────────────────────────────────────

def test_verified_semantic_requires_replay_and_audit():
    mem = LongTermMemory()
    assert not mem.promote_verified_fact({"theorem_hash": "h"})  # missing replay/audit
    assert not mem.promote_verified_fact({
        "theorem_hash": "h", "kernel_or_certificate_replay": True, "dependency_audit": True})


def test_external_import_is_sourced_premise_not_verified_fact():
    mem = LongTermMemory()
    assert not mem.promote_external_import({"verbatim_extract": "x"})  # missing version/recheck
    assert mem.promote_external_import({
        "verbatim_extract": "thm", "source_version": "v1", "applicability_rechecked": True})
    # cross-problem policy differs: import is a sourced premise, not verified
    assert mem.external_import.cross_problem_usable() == "as_sourced_premise"
    assert mem.verified_semantic.cross_problem_usable() is True


def test_raw_scratch_never_promoted_cross_problem():
    mem = LongTermMemory()
    assert mem.raw_scratch.cross_problem_usable() is False


def test_toolchain_change_triggers_revalidation():
    mem = LongTermMemory()
    revalidate = mem.revalidate_on_toolchain_change()
    assert "mechanically_verified_semantic" in revalidate
    assert "audited_external_import" in revalidate


# ── calibration ─────────────────────────────────────────────────────────────────

def test_brier_and_ece():
    perfect = [(1.0, 1), (0.0, 0)]
    assert brier_score(perfect) == 0.0
    bad = [(0.0, 1), (1.0, 0)]
    assert brier_score(bad) == 1.0
    assert expected_calibration_error(perfect) == 0.0


def test_false_promotion_rate():
    ledger = CalibrationLedger()
    ledger.record_promotion(false_positive=False)
    ledger.record_promotion(false_positive=True)
    assert ledger.false_promotion_rate() == 0.5
    report = ledger.report()
    assert report["false_promotion_rate"] == 0.5


# ── expert iteration ─────────────────────────────────────────────────────────────

def test_expert_iteration_rejects_self_graded_and_unreplayed():
    ei = VerifiedOnlyExpertIteration(trained_lineage="fam1", frozen_eval_period="2026Q3")
    # self-graded (evaluator == generator) rejected
    assert not ei.admit(TrainingExample("e1", True, True, "fp", "fam1", "fam1"))
    # unreplayed rejected
    assert not ei.admit(TrainingExample("e2", True, False, "fp", "fam2", "fam1"))
    # authenticated + replayed + different evaluator accepted
    assert ei.admit(TrainingExample("e3", True, True, "fp", "fam2", "fam1"))
    assert ei.training_set_hashable() == ["e3"]
