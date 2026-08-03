"""Service-interface contracts (spec §6.12).

Typed request/response protocols for the eight services. A trusted response never
upgrades truth by itself: an ATP/SMT/SAT ``proved``/``unsat`` without a checked
reconstruction remains solver testimony, and a correct certificate for a
mistranslated formula proves the wrong claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

SERVICES = (
    "literature", "theorem_db", "oeis", "computation", "lean", "atp_smt_sat",
    "claim_graph", "controller",
)


@dataclass(frozen=True)
class ServiceContract:
    service: str
    minimal_request: str
    minimal_trusted_response: str
    truth_upgrade: bool


SERVICE_CONTRACTS: dict[str, ServiceContract] = {
    c.service: c for c in [
        ServiceContract("literature", "statement, equivalents, objects, techniques, date cutoff",
                        "versioned SourcePacket[]", truth_upgrade=False),
        ServiceContract("theorem_db", "natural claim, formal signature, context/imports",
                        "candidate premises with exact declarations + dependency provenance",
                        truth_upgrade=False),
        ServiceContract("oeis", "exact terms, index/offset, construction, transforms/budget",
                        "ranked matches, fields, references, transform path + hashes",
                        truth_upgrade=False),
        ServiceContract("computation", "immutable experiment specification",
                        "replayable artifact + classification/checker report", truth_upgrade=True),
        ServiceContract("lean", "environment hash, declaration/goal/local context, action budget",
                        "proof term/state/diagnostics + clean replay report", truth_upgrade=True),
        ServiceContract("atp_smt_sat",
                        "source-claim hash, serialized fragment, premises, translator/encoding version",
                        "proof/model/certificate + checked reconstruction status", truth_upgrade=True),
        ServiceContract("claim_graph", "proposed node/edge/evidence event",
                        "admission/rejection with validator IDs + affected closure", truth_upgrade=True),
        ServiceContract("controller", "branch state/posterior/resources",
                        "lease, action budget, model/tool route + selection rationale",
                        truth_upgrade=False),
    ]
}


def service_contract(service: str) -> ServiceContract:
    if service not in SERVICE_CONTRACTS:
        raise KeyError(f"unknown service {service!r}")
    return SERVICE_CONTRACTS[service]


# Structural protocols the concrete services satisfy.
@runtime_checkable
class LiteratureService(Protocol):
    def build_packet(self, query: Any, **kwargs: Any) -> Any: ...


@runtime_checkable
class ComputationService(Protocol):
    def submit_experiment(self, spec: Any, code: str, **kwargs: Any) -> str: ...
    def replay(self, artifact_id: str, **kwargs: Any) -> Any: ...


@runtime_checkable
class FormalService(Protocol):
    def verify_declaration(self, **kwargs: Any) -> Any: ...


@runtime_checkable
class ClaimGraphService(Protocol):
    def admit(self, evidence: Any, **kwargs: Any) -> Any: ...
