"""ComputationalArtifact and its 6-way self-classification (spec §6.8).

Every artifact classifies itself as exactly one of six kinds, and the
classification is *checked, not trusted*: floating-point output can never claim
an exact kind without a validated interval/error argument, and a certificate kind
requires a checker to have run.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from egmra.provenance.hashing import content_id

# The six classifications (spec §6.8), ordered from weakest to strongest.
CLASSIFICATIONS = (
    "heuristic_numerical",              # 1
    "candidate_counterexample",         # 2 (awaiting exact validation)
    "exact_counterexample",             # 3
    "exhaustive_finite_subcase",        # 4
    "certificate_checked_lemma",        # 5
    "finite_reduction_proof",           # 6
)

_EXACT_KINDS = {
    "exact_counterexample", "exhaustive_finite_subcase",
    "certificate_checked_lemma", "finite_reduction_proof",
}

# Map an artifact classification to the truth-plane validator's vocabulary
# (egmra.truth.validators.validate_computation) so evidence is scored correctly.
VALIDATOR_CLASSIFICATION = {
    "heuristic_numerical": "heuristic",
    "candidate_counterexample": "candidate_counterexample",
    "exact_counterexample": "exact_counterexample",
    "exhaustive_finite_subcase": "exhaustive_finite",
    "certificate_checked_lemma": "certificate_checked",
    "finite_reduction_proof": "finite_reduction",
}


def validator_classification(effective_classification: str) -> str:
    """Translate a ComputationalArtifact classification to the validator token."""
    return VALIDATOR_CLASSIFICATION.get(effective_classification, "heuristic")


def _immutable_json(value: Any, *, path: str = "output") -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} contains a non-finite float")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} contains a non-string key")
            frozen[key] = _immutable_json(item, path=f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_immutable_json(item, path=f"{path}[{index}]") for index, item in enumerate(value))
    raise ValueError(f"{path} contains unsupported type {type(value).__name__}")


@dataclass(frozen=True)
class ComputationalArtifact:
    artifact_id: str
    spec_hash: str
    code_hash: str
    claimed_classification: str
    output: Any
    output_hash: str
    arithmetic_mode: str
    coverage: str = ""
    certificate_present: bool = False
    checker_passed: bool | None = None
    seed: int = 0
    environment_hash: str = ""
    stdout: str = ""
    created_at: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "output", _immutable_json(self.output))

    def effective_classification(self) -> str:
        """Downgrade a claimed exact classification when its evidence is missing."""
        claimed = self.claimed_classification
        if claimed not in CLASSIFICATIONS:
            return "heuristic_numerical"
        # Floating point can never establish an exact kind without an interval arg.
        if claimed in _EXACT_KINDS and self.arithmetic_mode == "float":
            return "candidate_counterexample" if "counterexample" in claimed else "heuristic_numerical"
        # A certificate-checked lemma requires a checker to have passed.
        if claimed == "certificate_checked_lemma" and not (self.certificate_present and self.checker_passed):
            return "candidate_counterexample" if False else "heuristic_numerical"
        # Exhaustive/finite-reduction proof claims must both describe coverage
        # and report successful completion.  A false or missing result is useful
        # diagnostic output, never proof of the asserted claim.
        if claimed in {"exhaustive_finite_subcase", "finite_reduction_proof"}:
            if not self.coverage or not isinstance(self.output, Mapping) \
                    or self.output.get("result") is not True:
                return "heuristic_numerical"
        return claimed

    def is_downgraded(self) -> bool:
        return self.effective_classification() != self.claimed_classification

    def refutes(self) -> bool:
        return self.effective_classification() == "exact_counterexample"

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "spec_hash": self.spec_hash,
            "code_hash": self.code_hash,
            "claimed_classification": self.claimed_classification,
            "effective_classification": self.effective_classification(),
            "downgraded": self.is_downgraded(),
            "output_hash": self.output_hash,
            "arithmetic_mode": self.arithmetic_mode,
            "coverage": self.coverage,
            "certificate_present": self.certificate_present,
            "checker_passed": self.checker_passed,
            "seed": self.seed,
            "environment_hash": self.environment_hash,
            "created_at": self.created_at,
        }

    def content_id(self) -> str:
        return content_id(self.to_dict())


@dataclass(frozen=True)
class ReplayReport:
    artifact_id: str
    replayed: bool
    output_hash_matches: bool
    original_hash: str
    replay_hash: str
    environment_hash: str
    detail: str = ""
    original_environment_hash: str = ""

    @property
    def independent_environment(self) -> bool:
        """Whether replay used a measured environment distinct from the original."""

        return bool(
            self.original_environment_hash
            and self.environment_hash
            and self.original_environment_hash != self.environment_hash
        )


@dataclass(frozen=True)
class CertificateReport:
    artifact_id: str
    checker_id: str
    passed: bool
    detail: str = ""
