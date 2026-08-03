"""Persistent, validated state for long-horizon proof research."""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class StatementLock:
    original_statement: str
    sha256: str
    acceptance_criteria: tuple[str, ...]


@dataclass(frozen=True)
class Subgoal:
    id: str
    claim: str
    dependencies: tuple[str, ...]
    centrality: int
    falsifiable: bool


@dataclass
class ResearchState:
    statement_lock: dict
    subgoal_graph: dict
    attempts: list[dict] = field(default_factory=list)
    verified_lemmas: list[dict] = field(default_factory=list)
    failed_approaches: list[dict] = field(default_factory=list)

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")


def make_statement_lock(problem: str) -> StatementLock:
    normalized = problem.strip()
    return StatementLock(
        original_statement=normalized,
        sha256=hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        acceptance_criteria=(
            "Prove or disprove the exact original statement without changing quantifiers.",
            "Do not add hypotheses, restrict domains, weaken conclusions, or omit subproblems.",
            "Resolve every boundary case and every explicitly numbered task.",
            "Treat ambiguity as a blocking defect rather than choosing a convenient interpretation.",
        ),
    )


def statement_lock_text(lock: StatementLock) -> str:
    criteria = "\n".join(f"- {item}" for item in lock.acceptance_criteria)
    return (
        f"STATEMENT_SHA256: {lock.sha256}\n"
        f"ORIGINAL_STATEMENT (immutable):\n{lock.original_statement}\n"
        f"ACCEPTANCE_CRITERIA:\n{criteria}"
    )


def parse_subgoal_graph(data: dict) -> tuple[Subgoal, ...]:
    raw = data.get("subgoals")
    if not isinstance(raw, list) or not raw:
        raise ValueError("planner must return a non-empty subgoals list")
    nodes = []
    for item in raw:
        node = Subgoal(
            id=str(item["id"]),
            claim=str(item["claim"]).strip(),
            dependencies=tuple(str(dep) for dep in item.get("dependencies", [])),
            centrality=int(item.get("centrality", 1)),
            falsifiable=bool(item.get("falsifiable", False)),
        )
        if not node.id or not node.claim:
            raise ValueError("subgoal ids and claims must be non-empty")
        if not 1 <= node.centrality <= 5:
            raise ValueError(f"subgoal {node.id} centrality must be in 1..5")
        nodes.append(node)

    ids = [node.id for node in nodes]
    if len(ids) != len(set(ids)):
        raise ValueError("subgoal ids must be unique")
    known = set(ids)
    for node in nodes:
        missing = set(node.dependencies) - known
        if missing:
            raise ValueError(f"subgoal {node.id} has unknown dependencies: {sorted(missing)}")
        if node.id in node.dependencies:
            raise ValueError(f"subgoal {node.id} depends on itself")

    visiting: set[str] = set()
    visited: set[str] = set()
    deps = {node.id: node.dependencies for node in nodes}

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise ValueError("subgoal graph contains a cycle")
        if node_id in visited:
            return
        visiting.add(node_id)
        for dependency in deps[node_id]:
            visit(dependency)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in ids:
        visit(node_id)
    return tuple(nodes)


def graph_as_dict(data: dict, nodes: tuple[Subgoal, ...]) -> dict:
    node_ids = {node.id for node in nodes}
    if "GOAL" not in node_ids:
        raise ValueError("subgoal graph must contain a GOAL node")
    bottleneck_ids = [str(item) for item in data.get("bottleneck_ids", [])]
    unknown_bottlenecks = set(bottleneck_ids) - node_ids
    if unknown_bottlenecks:
        raise ValueError(
            f"planner named unknown bottlenecks: {sorted(unknown_bottlenecks)}"
        )
    return {
        "summary": str(data.get("summary", "")),
        "bottleneck_ids": bottleneck_ids,
        "subgoals": [asdict(node) for node in nodes],
    }
