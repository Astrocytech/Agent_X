"""Acceptance dependency graph across phases (A, B, C).

Item 38 (32.1): Directed acyclic graph of acceptance criteria
linking source -> evidence -> evaluation -> report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AcceptanceNode:
    node_id: str
    phase: str  # A | B | C
    description: str
    depends_on: list[str] = field(default_factory=list)
    required_by: list[str] = field(default_factory=list)
    status: str = "pending"  # pending | passed | failed | blocked


ACCEPTANCE_GRAPH: dict[str, AcceptanceNode] = {}


def register(node: AcceptanceNode) -> None:
    ACCEPTANCE_GRAPH[node.node_id] = node


def depends(node_id: str) -> list[str]:
    n = ACCEPTANCE_GRAPH.get(node_id)
    return n.depends_on if n else []


def required_by(node_id: str) -> list[str]:
    n = ACCEPTANCE_GRAPH.get(node_id)
    return n.required_by if n else []


# --- Phase A: Source quality ---
register(AcceptanceNode("a1", "A", "All source documents have SHA-256 hashes",
                        required_by=["a2", "b1"]))
register(AcceptanceNode("a2", "A", "All benchmark artifacts are generated",
                        depends_on=["a1"], required_by=["b1"]))
register(AcceptanceNode("a3", "A", "Example agents have file origin classification",
                        required_by=["c1"]))

# --- Phase B: Governance evidence ---
register(AcceptanceNode("b1", "B", "Event log append-only with hash chain",
                        depends_on=["a2"], required_by=["b2", "b3"]))
register(AcceptanceNode("b2", "B", "Provenance records are cross-linked",
                        depends_on=["b1"], required_by=["b3", "c1"]))
register(AcceptanceNode("b3", "B", "Guard validators all pass (no-op, weak-test, secret, manual)",
                        depends_on=["b1", "b2"], required_by=["c1"]))
register(AcceptanceNode("b4", "B", "Clean workspace runner produces isolated results",
                        required_by=["c1"]))

# --- Phase C: Evaluation + Report ---
register(AcceptanceNode("c1", "C", "Evaluation harness runs without errors",
                        depends_on=["a3", "b2", "b3", "b4"],
                        required_by=["c2"]))
register(AcceptanceNode("c2", "C", "Final acceptance report is generated",
                        depends_on=["c1"]))


def topo_sort() -> list[str]:
    """Topological sort of acceptance graph (Kahn's algorithm)."""
    in_degree = {nid: len(n.depends_on) for nid, n in ACCEPTANCE_GRAPH.items()}
    queue = [nid for nid, deg in in_degree.items() if deg == 0]
    order = []
    while queue:
        nid = queue.pop(0)
        order.append(nid)
        for dep in ACCEPTANCE_GRAPH[nid].required_by:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)
    return order


def summary() -> list[dict]:
    return [{"node_id": n.node_id, "phase": n.phase, "description": n.description,
             "status": n.status, "depends_on": n.depends_on}
            for n in ACCEPTANCE_GRAPH.values()]
