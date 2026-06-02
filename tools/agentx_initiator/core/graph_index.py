from __future__ import annotations
from typing import Optional
from agentx_initiator.core.graph_model import GraphIndex, GraphNode, GraphEdge


def build_graph_index(
    nodes: list[GraphNode], edges: list[GraphEdge]
) -> GraphIndex:
    sorted_nodes = sorted(nodes, key=lambda n: n.node_id)
    sorted_edges = sorted(edges, key=lambda e: e.edge_id)

    nodes_by_id: dict[str, dict] = {}
    edges_by_id: dict[str, dict] = {}
    outgoing: dict[str, list[dict]] = {}
    incoming: dict[str, list[dict]] = {}

    for n in sorted_nodes:
        d = n.to_dict()
        nodes_by_id[n.node_id] = d
        outgoing.setdefault(n.node_id, [])
        incoming.setdefault(n.node_id, [])

    for e in sorted_edges:
        d = e.to_dict()
        edges_by_id[e.edge_id] = d
        outgoing.setdefault(e.source_node_id, []).append(d)
        incoming.setdefault(e.target_node_id, []).append(d)

    return GraphIndex(
        nodes_by_id=nodes_by_id,
        edges_by_id=edges_by_id,
        outgoing=outgoing,
        incoming=incoming,
    )


def index_nodes_by_id(
    nodes: list[GraphNode],
) -> dict[str, GraphNode]:
    return {n.node_id: n for n in nodes}


def index_edges_by_id(
    edges: list[GraphEdge],
) -> dict[str, GraphEdge]:
    return {e.edge_id: e for e in edges}


def find_outgoing_edges(
    node_id: str, edges: list[GraphEdge]
) -> list[GraphEdge]:
    return sorted(
        [e for e in edges if e.source_node_id == node_id],
        key=lambda e: e.edge_id,
    )


def find_incoming_edges(
    node_id: str, edges: list[GraphEdge]
) -> list[GraphEdge]:
    return sorted(
        [e for e in edges if e.target_node_id == node_id],
        key=lambda e: e.edge_id,
    )


def find_neighbors(
    node_id: str,
    nodes: list[GraphNode],
    edges: list[GraphEdge],
) -> list[GraphNode]:
    neighbor_ids: set[str] = set()
    for e in edges:
        if e.source_node_id == node_id:
            neighbor_ids.add(e.target_node_id)
        if e.target_node_id == node_id:
            neighbor_ids.add(e.source_node_id)
    node_map = {n.node_id: n for n in nodes}
    result = [node_map[nid] for nid in sorted(neighbor_ids) if nid in node_map]
    return result
