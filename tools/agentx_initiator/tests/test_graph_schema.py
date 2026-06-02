from datetime import datetime, timezone
from uuid import uuid4
from agentx_initiator.core.schema_validation import validate_instance


def _make_valid_node():
    return {
        "schema_version": "1.0",
        "schema_id": "graph_node.schema.json",
        "owner_component": "AGENTX_KNOWLEDGE_GRAPH",
        "artifact_type": "graph_node",
        "node_id": "graph-node::TEST::abc123",
        "node_type": "COMPONENT",
        "label": "Test Node",
        "status": "ACTIVE",
        "source_ref": "core/test.py",
        "source_component": "TestComponent",
        "properties": {},
        "content_hash": "abc123",
    }


def _make_valid_edge():
    return {
        "schema_version": "1.0",
        "schema_id": "graph_edge.schema.json",
        "owner_component": "AGENTX_KNOWLEDGE_GRAPH",
        "artifact_type": "graph_edge",
        "edge_id": "graph-edge::PRODUCES::def456",
        "source_node_id": "graph-node::COMPONENT::abc123",
        "target_node_id": "graph-node::ARTIFACT::def456",
        "edge_type": "PRODUCES",
        "status": "ACTIVE",
        "source_ref": "core/test.py",
        "source_component": "TestComponent",
        "evidence_refs": ["evidence-1"],
        "properties": {},
        "content_hash": "def456",
    }


def test_graph_node_schema_accepts_valid_node():
    result = validate_instance(_make_valid_node(), "graph_node.schema.json")
    assert result.valid, result.errors


def test_graph_node_schema_rejects_missing_required_fields():
    obj = _make_valid_node()
    del obj["node_id"]
    result = validate_instance(obj, "graph_node.schema.json")
    assert not result.valid


def test_graph_edge_schema_accepts_valid_edge():
    result = validate_instance(_make_valid_edge(), "graph_edge.schema.json")
    assert result.valid, result.errors


def test_graph_edge_schema_rejects_missing_endpoint():
    obj = _make_valid_edge()
    del obj["source_node_id"]
    result = validate_instance(obj, "graph_edge.schema.json")
    assert not result.valid


def test_graph_edge_schema_rejects_missing_evidence_for_non_unknown():
    obj = _make_valid_edge()
    del obj["evidence_refs"]
    result = validate_instance(obj, "graph_edge.schema.json")
    assert not result.valid


def test_graph_snapshot_schema_accepts_valid_snapshot():
    obj = {
        "schema_version": "1.0",
        "schema_id": "graph_snapshot.schema.json",
        "owner_component": "AGENTX_KNOWLEDGE_GRAPH",
        "artifact_type": "graph_snapshot",
        "snapshot_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "node_count": 0,
        "edge_count": 0,
        "nodes": [],
        "edges": [],
        "integrity_report": {},
        "warnings": [],
        "errors": [],
    }
    result = validate_instance(obj, "graph_snapshot.schema.json")
    assert result.valid, result.errors


def test_graph_query_result_schema_accepts_valid_result():
    obj = {
        "schema_version": "1.0",
        "schema_id": "graph_query_result.schema.json",
        "owner_component": "AGENTX_KNOWLEDGE_GRAPH",
        "artifact_type": "graph_query_result",
        "query_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": {"query_type": "all", "value": ""},
        "node_results": [],
        "edge_results": [],
        "result_count": 0,
        "warnings": [],
        "errors": [],
    }
    result = validate_instance(obj, "graph_query_result.schema.json")
    assert result.valid, result.errors


def test_graph_manifest_schema_accepts_valid_manifest():
    obj = {
        "schema_version": "1.0",
        "schema_id": "graph_manifest.schema.json",
        "owner_component": "AGENTX_KNOWLEDGE_GRAPH",
        "artifact_type": "graph_manifest",
        "manifest_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "node_count": 0,
        "edge_count": 0,
        "node_types": [],
        "edge_types": [],
        "latest_snapshot": "graph/graph_snapshot_latest.json",
        "schema_versions": {},
        "warnings": [],
        "errors": [],
    }
    result = validate_instance(obj, "graph_manifest.schema.json")
    assert result.valid, result.errors


def test_graph_integrity_schema_accepts_valid_report():
    obj = {
        "schema_version": "1.0",
        "schema_id": "graph_integrity.schema.json",
        "owner_component": "AGENTX_KNOWLEDGE_GRAPH",
        "artifact_type": "graph_integrity",
        "integrity_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "checked_node_count": 0,
        "checked_edge_count": 0,
        "missing_endpoint_edges": [],
        "invalid_schema_records": [],
        "warnings": [],
        "errors": [],
    }
    result = validate_instance(obj, "graph_integrity.schema.json")
    assert result.valid, result.errors
