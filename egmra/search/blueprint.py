"""AND/OR lemma blueprint with dynamic leaves (spec §4.2, §6.7, §7).

Replaces the current single-JSON synthesis DAG. Attempt the target directly; if
that fails, express *alternative sufficient lemma sets* (OR of ANDs). Leaves are
dynamic, carry proof debt, and support dependency-local repair.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from egmra.provenance.hashing import content_id


class BlueprintError(RuntimeError):
    pass


@dataclass
class Node:
    node_id: str
    claim: str
    node_type: str            # "AND" | "OR" | "LEAF" | "GOAL"
    children: list[str] = field(default_factory=list)
    centrality: float = 0.0
    semantic_risk: float = 0.0
    closed: bool = False

    def __post_init__(self) -> None:
        if self.node_type not in {"AND", "OR", "LEAF", "GOAL"}:
            raise BlueprintError(f"bad node type {self.node_type!r}")


@dataclass
class AndOrBlueprint:
    goal_id: str
    nodes: dict[str, Node] = field(default_factory=dict)
    direct_attempted: bool = False

    def add_node(self, node: Node) -> Node:
        if node.node_id in self.nodes:
            raise BlueprintError(f"duplicate node {node.node_id}")
        for child in node.children:
            if child not in self.nodes:
                raise BlueprintError(f"node {node.node_id} references unknown child {child}")
        self.nodes[node.node_id] = node
        return node

    def add_sufficient_lemma_set(self, lemma_ids: list[str], *, or_parent: str) -> str:
        """Add one AND-set of sufficient lemmas as a child of an OR node."""
        parent = self.nodes[or_parent]
        if parent.node_type != "OR":
            raise BlueprintError("sufficient lemma sets attach only to OR nodes")
        and_id = f"and_{content_id({'p': or_parent, 'lemmas': sorted(lemma_ids)})[:12]}"
        self.add_node(Node(and_id, claim="AND of lemmas", node_type="AND", children=list(lemma_ids)))
        parent.children.append(and_id)
        return and_id

    def is_closed(self, node_id: str | None = None) -> bool:
        """Recursively evaluate AND/OR closure from the goal."""
        def evaluate(current_id: str, visiting: set[str]) -> bool:
            if current_id not in self.nodes:
                raise BlueprintError(f"unknown blueprint node {current_id!r}")
            if current_id in visiting:
                raise BlueprintError(f"cycle detected at blueprint node {current_id!r}")
            node = self.nodes[current_id]
            if node.node_type == "LEAF":
                return node.closed
            if not node.children:
                return node.closed
            visiting.add(current_id)
            try:
                if node.node_type == "OR":
                    return any(evaluate(child, visiting) for child in node.children)
                return all(evaluate(child, visiting) for child in node.children)
            finally:
                visiting.remove(current_id)

        return evaluate(node_id or self.goal_id, set())

    def open_leaves(self) -> list[str]:
        return [n.node_id for n in self.nodes.values() if n.node_type == "LEAF" and not n.closed]

    def failed_dependency_cone(self, failed_leaf: str) -> list[str]:
        """Ancestors that depend on a failed leaf (for dependency-local repair)."""
        cone: set[str] = set()
        changed = True
        target = {failed_leaf}
        while changed:
            changed = False
            for node in self.nodes.values():
                if node.node_id in cone:
                    continue
                if set(node.children) & target:
                    cone.add(node.node_id)
                    target = target | {node.node_id}
                    changed = True
        return sorted(cone)

    def blueprint_hash(self) -> str:
        return content_id({nid: {"type": n.node_type, "children": n.children, "closed": n.closed}
                           for nid, n in self.nodes.items()})
