"""Release plane: five gates, certificate, proof compiler, promotion policy."""

from egmra.release.certificate import ReleaseCertificate, ReleaseSecurityError
from egmra.release.compiler import CompiledProof, CompilerError, assemble_from_admitted_graph
from egmra.release.gates import (
    FiveGateResult,
    GateSecurityError,
    formal_correspondence_gate,
    intent_gate,
    novelty_gate,
    reproducibility_gate,
    run_five_gates,
    significance_gate,
    truth_gate,
)
from egmra.release.policy import PromotionDecision, PromotionPolicy, PromotionSecurityError

__all__ = [
    "ReleaseCertificate", "ReleaseSecurityError",
    "CompiledProof", "CompilerError", "assemble_from_admitted_graph",
    "FiveGateResult", "GateSecurityError", "formal_correspondence_gate", "intent_gate", "novelty_gate",
    "reproducibility_gate", "run_five_gates", "significance_gate", "truth_gate",
    "PromotionDecision", "PromotionPolicy", "PromotionSecurityError",
]
