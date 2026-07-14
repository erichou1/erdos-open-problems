"""Service topology registry (spec §14.1).

Documents the ten deployment layers and a simple health/registration model. The
authoritative record is the event/artifact store; graph views and dashboards are
disposable projections.
"""

from __future__ import annotations

from dataclasses import dataclass, field

TOPOLOGY_LAYERS = {
    "event_transaction_store": "append-only events, optimistic object versions, transactional revocation",
    "artifact_store": "content-addressed storage for sources, code, proof trees, builds, logs, containers",
    "graph_views": "adjacency/materialized closure; dedicated graph engine only if profiling justifies",
    "retrieval": "hybrid lexical + vector + formula/type index; citation and theorem-dependency graphs",
    "scheduler": "durable priority queue with idempotency keys, leases, heartbeats, provider quotas",
    "compute_lab": "isolated OCI containers/VMs for Python/Sage/CAS/SAT/SMT/enumeration; network off",
    "lean_farm": "pinned multi-version build workers, live proof-state service, clean replay, independent checker",
    "model_gateway": "exact model/version registry, prompt hashes, cost/token telemetry, structured-output validation",
    "observability": "event-derived dashboard: evidence tiers, proof debt, active branches, costs, backlog",
    "release": "reproducible bundle builder, five-gate certificates, human review portal",
}


@dataclass
class ServiceTopology:
    registered: dict[str, str] = field(default_factory=dict)

    def register(self, layer: str, endpoint: str) -> None:
        if layer not in TOPOLOGY_LAYERS:
            raise KeyError(f"unknown topology layer {layer!r}")
        self.registered[layer] = endpoint

    def missing_layers(self) -> list[str]:
        return [layer for layer in TOPOLOGY_LAYERS if layer not in self.registered]

    def authoritative_layers(self) -> tuple[str, str]:
        # The event log and artifact store are authoritative; the rest are derived.
        return ("event_transaction_store", "artifact_store")
