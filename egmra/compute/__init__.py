"""Compute plane (Module H): sandboxed immutable experiments + replay + certificates."""

from egmra.compute.artifact import (
    CLASSIFICATIONS,
    CertificateReport,
    ComputationalArtifact,
    ReplayReport,
)
from egmra.compute.backends import (
    CASBackend,
    ExactArithmetic,
    SATBackend,
    SMTBackend,
    SolverResult,
    check_sat_model,
    reconstruct_unsat,
)
from egmra.compute.sandbox import (
    ContainerSandbox,
    RestrictedPythonExecutor,
    SandboxResult,
    SubprocessSandbox,
)
from egmra.compute.service import (
    ComputeService,
    PersistenceError,
    TrustedCertificateChecker,
)
from egmra.compute.spec import ARITHMETIC_MODES, SANDBOX_POLICIES, ExperimentSpec

__all__ = [
    "CLASSIFICATIONS", "CertificateReport", "ComputationalArtifact", "ReplayReport",
    "CASBackend", "ExactArithmetic", "SATBackend", "SMTBackend", "SolverResult",
    "check_sat_model", "reconstruct_unsat",
    "ContainerSandbox", "RestrictedPythonExecutor", "SandboxResult", "SubprocessSandbox",
    "ComputeService", "PersistenceError", "TrustedCertificateChecker",
    "ARITHMETIC_MODES", "SANDBOX_POLICIES", "ExperimentSpec",
]
