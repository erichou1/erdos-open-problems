"""Bridge a real local Lean kernel replay to a sealed attestation (task B1).

``AristotleApiClient.bind_local_replay`` only trusts a sealed
:class:`~egmra.lean.aristotle_api.LocalLeanReplayAttestation`. This module builds
that attestation from an *independent* local Lean kernel replay: it hashes the
quarantined source tree, drives the pinned :class:`AttestedKernelRunner` (which
runs the real ``lake``/kernel check in a hardened environment), verifies the
returned :class:`CheckerAttestation` is authentic and bound to the exact target
type, enforces the axiom whitelist, and only then seals an attestation bound to
that exact artifact.

The vendor never contributes trust; a failed, unauthenticated, mis-targeted, or
axiom-violating replay yields ``None`` (rejected), never a promotion.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from egmra.lean.aristotle_api import (
    LocalLeanReplayAttestation,
    hash_quarantine_tree,
    seal_local_lean_replay_attestation,
)
from egmra.lean.service import (
    DEFAULT_AXIOM_WHITELIST,
    CheckerAttestation,
    CheckerRequest,
    LeanEnvironment,
)


class KernelChecker(Protocol):
    """A pinned checker that runs a real kernel replay (e.g. AttestedKernelRunner)."""

    def run(self, request: CheckerRequest) -> CheckerAttestation: ...


@dataclass(frozen=True)
class LeanReplayTarget:
    """The locked target a returned Lean artifact must actually establish."""

    claim_id: str
    declaration_name: str
    normalized_target_hash: str
    expected_type_hash: str
    immutable_target_module_hash: str
    trust_policy_hash: str


@dataclass
class LeanReplayVerifier:
    """A ``bind_local_replay`` verifier backed by a real local Lean kernel replay.

    Usage::

        verifier = LeanReplayVerifier(checker=attested_kernel_runner,
                                      environment=lean_env, target=target)
        result = aristotle_client.bind_local_replay(
            artifact, verifier, expected_claim_id=target.claim_id)
        # result.promotable is True only if the kernel replay actually verified.
    """

    checker: KernelChecker
    environment: LeanEnvironment
    target: LeanReplayTarget
    axiom_whitelist: frozenset[str] = DEFAULT_AXIOM_WHITELIST
    env: dict[str, str] | None = None

    def __call__(self, quarantine_dir: Path) -> LocalLeanReplayAttestation | None:
        source_hash = hash_quarantine_tree(quarantine_dir)
        request = CheckerRequest(
            environment_id=self.environment.environment_id,
            source_hash=source_hash,
            declaration_name=self.target.declaration_name,
            expected_type_hash=self.target.expected_type_hash,
            immutable_target_module_hash=self.target.immutable_target_module_hash,
            trust_policy_hash=self.target.trust_policy_hash,
        )
        try:
            attestation = self.checker.run(request)
        except Exception:  # noqa: BLE001 - a failed replay is a rejection, never a pass
            return None
        # The checker attestation must be authentic AND bound to this exact request
        # (which is bound to this exact source tree and the locked target type).
        if not attestation.verify_for(request, env=self.env):
            return None
        # Defense in depth: the transitive axiom closure must stay within the whitelist.
        if set(attestation.transitive_axioms) - set(self.axiom_whitelist):
            return None
        return seal_local_lean_replay_attestation(
            LocalLeanReplayAttestation(
                claim_id=self.target.claim_id,
                normalized_target_hash=self.target.normalized_target_hash,
                source_hash=source_hash,
                environment_hash=self.environment.environment_id,
                lean_version=self.environment.lean_version,
                mathlib_commit=self.environment.mathlib_commit,
                artifact_hash=source_hash,
                checker_id=attestation.checker_id,
                replay_log_hash=attestation.checker_log_hash,
                issued_at=attestation.issued_at,
            ),
            env=self.env,
        )
