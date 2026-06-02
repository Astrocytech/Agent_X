from datetime import datetime, timezone
from uuid import uuid4

from agentx_initiator.core.graph_model import (
    GraphNode, GraphEdge, GraphQuery,
    GraphSnapshot, GraphManifest, GraphIntegrityReport,
    GraphWriteResult, GraphIndex, compute_content_hash,
    NodeType, EdgeType, RecordStatus, GraphBuildStatus,
)
from agentx_initiator.core.graph_index import (
    build_graph_index, index_nodes_by_id, index_edges_by_id,
    find_outgoing_edges, find_incoming_edges, find_neighbors,
)
from agentx_initiator.core.knowledge_graph import KnowledgeGraph
import pytest


def _make_test_node(node_id="test-node-1", node_type="COMPONENT",
                     label="Test", source_ref="test"):
    return GraphNode(
        node_id=node_id,
        node_type=node_type,
        label=label,
        status=RecordStatus.ACTIVE.value,
        source_ref=source_ref,
        source_component="TestComponent",
    )


def _make_test_edge(edge_id="test-edge-1", source="test-node-1",
                     target="test-node-2", edge_type="REFERENCES",
                     evidence=None):
    return GraphEdge(
        edge_id=edge_id,
        source_node_id=source,
        target_node_id=target,
        edge_type=edge_type,
        status=RecordStatus.ACTIVE.value,
        source_ref="test",
        source_component="TestComponent",
        evidence_refs=evidence or ["ev1"],
    )


class TestGraphNodeModel:
    def test_minimal_valid_node(self):
        node = _make_test_node()
        d = node.to_dict()
        assert d["node_id"] == "test-node-1"
        assert d["node_type"] == "COMPONENT"
        assert d["schema_version"] == "1.0"
        assert d["schema_id"] == "graph_node.schema.json"
        assert d["owner_component"] == "AGENTX_KNOWLEDGE_GRAPH"
        assert d["artifact_type"] == "graph_node"
        assert d["content_hash"]

    def test_content_hash_is_deterministic(self):
        n1 = _make_test_node()
        n2 = _make_test_node()
        assert n1.content_hash == n2.content_hash

    def test_content_hash_excludes_self(self):
        d = _make_test_node().to_dict()
        ch = compute_content_hash(d)
        d2 = dict(d)
        d2["content_hash"] = "different"
        ch2 = compute_content_hash(d2)
        assert ch == ch2


class TestGraphEdgeModel:
    def test_minimal_valid_edge(self):
        edge = _make_test_edge()
        d = edge.to_dict()
        assert d["edge_id"] == "test-edge-1"
        assert d["edge_type"] == "REFERENCES"
        assert d["evidence_refs"] == ["ev1"]
        assert d["content_hash"]

    def test_edge_accepts_empty_evidence(self):
        edge = GraphEdge(
            edge_id="no-evidence-edge",
            source_node_id="src",
            target_node_id="tgt",
            edge_type="UNKNOWN",
            status=RecordStatus.ACTIVE.value,
            source_ref="test",
            source_component="Test",
            evidence_refs=[],
        )
        assert edge.evidence_refs == []


@pytest.fixture
def clean_graph(tmp_path, monkeypatch):
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir(parents=True, exist_ok=True)
    import agentx_initiator.core.knowledge_graph as kg_mod
    monkeypatch.setattr(kg_mod, "_graph_dir", lambda: graph_dir)
    return KnowledgeGraph()


@pytest.fixture
def kg(clean_graph):
    return clean_graph


class TestKnowledgeGraphCore:
    def test_add_node_appends_valid_node(self, kg):
        node = _make_test_node()
        result = kg.add_node(node)
        assert result.status == "ACCEPTED"

    def test_add_node_rejects_invalid_node(self, kg):
        node = _make_test_node()
        node.node_type = "INVALID_TYPE"
        result = kg.add_node(node)
        assert result.status == "REJECTED"

    def test_add_edge_appends_valid_edge(self, kg):
        n1 = _make_test_node("node-a")
        n2 = _make_test_node("node-b")
        kg.add_node(n1)
        kg.add_node(n2)
        edge = _make_test_edge("edge-1", "node-a", "node-b")
        result = kg.add_edge(edge)
        assert result.status == "ACCEPTED"

    def test_add_edge_rejects_missing_source_endpoint(self, kg):
        n2 = _make_test_node("node-b")
        kg.add_node(n2)
        edge = _make_test_edge("edge-1", "nonexistent", "node-b")
        result = kg.add_edge(edge)
        assert result.status == "REJECTED"

    def test_add_edge_rejects_missing_target_endpoint(self, kg):
        n1 = _make_test_node("node-a")
        kg.add_node(n1)
        edge = _make_test_edge("edge-1", "node-a", "nonexistent")
        result = kg.add_edge(edge)
        assert result.status == "REJECTED"

    def test_duplicate_node_is_skipped(self, kg):
        n1 = _make_test_node("dup-node")
        r1 = kg.add_node(n1)
        assert r1.status == "ACCEPTED"
        r2 = kg.add_node(n1)
        assert r2.status == "DUPLICATE_SKIPPED"

    def test_duplicate_edge_is_skipped(self, kg):
        n1 = _make_test_node("node-x")
        n2 = _make_test_node("node-y")
        kg.add_node(n1)
        kg.add_node(n2)
        e1 = _make_test_edge("dup-edge", "node-x", "node-y")
        r1 = kg.add_edge(e1)
        assert r1.status == "ACCEPTED"
        r2 = kg.add_edge(e1)
        assert r2.status == "DUPLICATE_SKIPPED"

    def test_query_by_node_id(self, kg):
        n1 = _make_test_node("query-id-1")
        kg.add_node(n1)
        q = GraphQuery(query_type="node_id", value="query-id-1")
        result = kg.query_graph(q)
        assert len(result.get("node_results", [])) == 1

    def test_query_by_node_type(self, kg):
        n1 = _make_test_node("type-test-1", node_type="COMPONENT")
        n2 = _make_test_node("type-test-2", node_type="ARTIFACT")
        kg.add_node(n1)
        kg.add_node(n2)
        q = GraphQuery(query_type="node_type", value="COMPONENT")
        result = kg.query_graph(q)
        results = result.get("node_results", [])
        assert len(results) == 1
        assert results[0]["node_id"] == "type-test-1"

    def test_query_outgoing_edges(self, kg):
        n1 = _make_test_node("out-source")
        n2 = _make_test_node("out-target")
        kg.add_node(n1)
        kg.add_node(n2)
        e1 = _make_test_edge("out-e1", "out-source", "out-target")
        kg.add_edge(e1)
        q = GraphQuery(query_type="outgoing", value="out-source")
        result = kg.query_graph(q)
        assert len(result.get("edge_results", [])) == 1

    def test_query_incoming_edges(self, kg):
        n1 = _make_test_node("in-source")
        n2 = _make_test_node("in-target")
        kg.add_node(n1)
        kg.add_node(n2)
        e1 = _make_test_edge("in-e1", "in-source", "in-target")
        kg.add_edge(e1)
        q = GraphQuery(query_type="incoming", value="in-target")
        result = kg.query_graph(q)
        assert len(result.get("edge_results", [])) == 1

    def test_query_neighbors(self, kg):
        n1 = _make_test_node("neighbor-a")
        n2 = _make_test_node("neighbor-b")
        kg.add_node(n1)
        kg.add_node(n2)
        e1 = _make_test_edge("n-e1", "neighbor-a", "neighbor-b")
        kg.add_edge(e1)
        q = GraphQuery(query_type="neighbors", value="neighbor-a")
        result = kg.query_graph(q)
        assert len(result.get("node_results", [])) == 1

    def test_snapshot_contains_nodes_edges_and_integrity(self, kg):
        n1 = _make_test_node("snap-a")
        n2 = _make_test_node("snap-b")
        kg.add_node(n1)
        kg.add_node(n2)
        e1 = _make_test_edge("snap-e1", "snap-a", "snap-b")
        kg.add_edge(e1)
        snap = kg.build_snapshot()
        assert snap.node_count >= 2
        assert snap.edge_count >= 1
        assert "status" in snap.integrity_report

    def test_integrity_check_with_missing_endpoints(self, kg):
        n1 = _make_test_node("int-x")
        n2 = _make_test_node("int-y")
        kg.add_node(n1)
        kg.add_node(n2)
        bad_edge = GraphEdge(
            edge_id="bad-e1",
            source_node_id="int-x",
            target_node_id="ghost-node",
            edge_type="REFERENCES",
            status=RecordStatus.ACTIVE.value,
            source_ref="test",
            source_component="Test",
            evidence_refs=["ev1"],
        )
        nodes = kg.load_nodes()
        edges = kg.load_edges()
        report = kg.verify_integrity(nodes=nodes, edges=edges + [bad_edge])
        assert report.status == "FAIL"

    def test_integrity_report_detects_missing_endpoint_edges(self, kg):
        n1 = _make_test_node("int-a")
        n2 = _make_test_node("int-b")
        kg.add_node(n1)
        kg.add_node(n2)
        e1 = _make_test_edge("int-e1", "int-a", "int-b")
        kg.add_edge(e1)

        bad_edge = GraphEdge(
            edge_id="int-e2",
            source_node_id="int-a",
            target_node_id="missing-node",
            edge_type="REFERENCES",
            status=RecordStatus.ACTIVE.value,
            source_ref="test",
            source_component="Test",
            evidence_refs=["ev1"],
        )
        nodes = kg.load_nodes()
        edges = kg.load_edges()
        report = kg.verify_integrity(nodes=nodes + [n1, n2], edges=edges + [bad_edge])
        assert report.status == "FAIL"
