"""§9.6 — Aristotle and external-prover routing + sandbox policy.

External services receive the locked formal target, exact toolchain, a bounded
leaf, and source packets — after a licensing check. Returned Lean is executable
metaprogram code: it enters quarantine and is built only in a disposable
unprivileged sandbox (no network/credentials, read-only mounts, bounded resources),
then source-scanned, axiom/import-audited, correspondence-reviewed, checked against
the isolated target type, and independently checked before admission. Provider
identity may diversify search; it does not diversify the trusted verifier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from egmra.provenance.hashing import content_id


@dataclass(frozen=True)
class AristotleRequest:
    locked_target_hash: str
    toolchain_hash: str
    bounded_leaf: str
    source_packet_hash: str
    licensing_ok: bool

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class ProviderAttestation:
    request_id: str
    model_id: str
    build_id: str
    timestamp: str
    client_version: str
    server_attested_revision: bool

    @property
    def reproducible(self) -> bool:
        # If the provider does not attest an immutable server revision, generation
        # is non-reproducible (spec §9.6); the client version does not pin the model.
        return self.server_attested_revision


QUARANTINE_SANDBOX_POLICY = {
    "network": "off",
    "credentials": "none",
    "mounts": "read-only source/dependencies",
    "limits": "bounded cpu/ram/time/processes",
    "outputs": "captured",
    "host_execution": "forbidden",
}

RETURNED_LEAN_PIPELINE = (
    "build_in_disposable_sandbox",
    "source_scan",
    "axiom_import_audit",
    "correspondence_review",
    "check_against_isolated_target_type",
    "independent_check",
)


class AristotleRouting:
    """Route to Aristotle as a candidate worker; never as a trust root."""

    def prepare_request(self, request: AristotleRequest) -> AristotleRequest:
        if not request.licensing_ok:
            raise PermissionError(
                "licensing/confidentiality/data-residency not cleared; cannot send source packet"
            )
        return request

    @staticmethod
    def generation_reproducible(attestation: ProviderAttestation) -> bool:
        return attestation.reproducible

    @staticmethod
    def sandbox_policy() -> dict:
        return dict(QUARANTINE_SANDBOX_POLICY)

    @staticmethod
    def admission_pipeline() -> tuple[str, ...]:
        return RETURNED_LEAN_PIPELINE

    @staticmethod
    def routing_hash(request: AristotleRequest, attestation: ProviderAttestation) -> str:
        return content_id({
            "request": request.to_dict(),
            "attestation": attestation.__dict__,
            "reproducible": attestation.reproducible,
        })
