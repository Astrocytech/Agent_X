from agentx_initiator.core.graph_model import GraphNode, GraphEdge
from agentx_initiator.core.graph_index import (
    build_graph_index,
    index_nodes_by_id,
    index_edges_by_id,
    find_outgoing_edges,
    find_incoming_edges,
    find_neighbors,
)


def _make_node(node_id, node_type="COMPONENT", label="test"):
    return GraphNode(
        node_id=node_id,
        node_type=node_type,
        label=label,
        status="ACTIVE",
        source_ref="test",
        source_component="Test",
        properties={},
    )


def _make_edge(edge_id, source, target, edge_type="REFERENCES"):
    return GraphEdge(
        edge_id=edge_id,
        source_node_id=source,
        target_node_id=target,
        edge_type=edge_type,
        status="ACTIVE",
        source_ref="test",
        source_component="Test",
        evidence_refs=["ev1"],
        properties={},
    )


def test_index_by_node_id():
    nodes = [_make_node("n1"), _make_node("n2")]
    idx = index_nodes_by_id(nodes)
    assert "n1" in idx
    assert "n2" in idx
    assert idx["n1"].node_id == "n1"


def test_index_by_edge_id():
    edges = [_make_edge("e1", "n1", "n2"), _make_edge("e2", "n2", "n3")]
    idx = index_edges_by_id(edges)
    assert "e1" in idx
    assert "e2" in idx


def test_find_outgoing_edges():
    edges = [
        _make_edge("e1", "n1", "n2"),
        _make_edge("e2", "n1", "n3"),
        _make_edge("e3", "n2", "n3"),
    ]
    outgoing = find_outgoing_edges("n1", edges)
    assert len(outgoing) == 2
    assert all(e.source_node_id == "n1" for e in outgoing)


def test_find_incoming_edges():
    edges = [
        _make_edge("e1", "n1", "n3"),
        _make_edge("e2", "n2", "n3"),
        _make_edge("e3", "n3", "n4"),
    ]
    incoming = find_incoming_edges("n3", edges)
    assert len(incoming) == 2
    assert all(e.target_node_id == "n3" for e in incoming)


def test_find_neighbors():
    nodes = [
        _make_node("n1"), _make_node("n2"),
        _make_node("n3"), _make_node("n4"),
    ]
    edges = [
        _make_edge("e1", "n1", "n2"),
        _make_edge("e2", "n1", "n3"),
    ]
    neighbors = find_neighbors("n1", nodes, edges)
    nids = {n.node_id for n in neighbors}
    assert nids == {"n2", "n3"}


def test_build_graph_index_is_deterministic():
    nodes = [
        _make_node("n2"), _make_node("n1"), _make_node("n0"),
    ]
    edges = [
        _make_edge("e2", "n1", "n2"),
        _make_edge("e0", "n0", "n1"),
        _make_edge("e1", "n0", "n2"),
    ]
    idx1 = build_graph_index(nodes, edges)
    idx2 = build_graph_index(nodes[::-1], edges[::-1])
    assert list(idx1.nodes_by_id.keys()) == ["n0", "n1", "n2"]
    assert list(idx2.nodes_by_id.keys()) == ["n0", "n1", "n2"]
    assert list(idx1.edges_by_id.keys()) == ["e0", "e1", "e2"]
    assert list(idx2.edges_by_id.keys()) == ["e0", "e1", "e2"]
