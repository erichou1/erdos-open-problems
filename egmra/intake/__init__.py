"""Intake plane (Module A): Statement IR, interpretation lattice, probes, contract."""

from egmra.intake.contract import ProblemContract, build_problem_contract
from egmra.intake.interpretation import (
    InterpretationLattice,
    build_interpretation_lattice,
)
from egmra.intake.probes import Probe, mutate, paraphrase, run_integrity_probes
from egmra.intake.review import (
    IntentReviewError,
    interpretation_review_hash,
    sign_intent_certificate,
    verify_intent_certificate,
)
from egmra.intake.statement_ir import (
    Binder,
    ClauseParser,
    Definition,
    GrammarParser,
    ModelParser,
    Parser,
    Reconciliation,
    StatementIR,
    backtranslate,
    reconcile,
)

__all__ = [
    "ProblemContract", "build_problem_contract",
    "InterpretationLattice", "build_interpretation_lattice",
    "Probe", "mutate", "paraphrase", "run_integrity_probes",
    "IntentReviewError", "interpretation_review_hash",
    "sign_intent_certificate", "verify_intent_certificate",
    "Binder", "ClauseParser", "Definition", "GrammarParser", "ModelParser",
    "Parser", "Reconciliation", "StatementIR", "backtranslate", "reconcile",
]
