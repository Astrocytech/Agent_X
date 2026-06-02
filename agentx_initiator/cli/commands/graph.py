"""PM3: Build and query the Knowledge Graph."""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from agentx_initiator.core.knowledge_graph import KnowledgeGraph
from agentx_initiator.core.graph_model import (
    GraphQuery, GraphQueryResult, GraphBuildStatus, GraphNode, GraphEdge, GraphSnapshot,
)
from agentx_initiator.core.path_registry import get_path
from agentx_initiator.core.audit_log import append_event
from agentx_initiator.core.schema_validation import validate_instance
from agentx_initiator.cli.models import CLICommandResponse


def register(sub):
    p = sub.add_parser("graph", help="Build and query the Knowledge Graph")
    p.add_argument("mode", nargs="?", default="build",
                   choices=["build", "status", "query"],
                   help="Graph mode: build (default), status, or query")
    p.add_argument("--node-id", default="", help="Query by node ID")
    p.add_argument("--node-type", default="", help="Query by node type")
    p.add_argument("--edge-type", default="", help="Query by edge type")
    p.add_argument("--incoming", default="", help="Query incoming edges for a node")
    p.add_argument("--outgoing", default="", help="Query outgoing edges for a node")
    p.add_argument("--json", action="store_true", help="Output results as JSON")
    p.add_argument("--output-format", choices=["text", "json"], default="text",
                   help="Output format (text or json)")
    p.set_defaults(func=run)


def _build_graph() -> tuple[GraphSnapshot, list[str], list[str], str]:
    kg = KnowledgeGraph()
    snapshot = kg.ingest_known_artifacts()

    index = kg.build_index()
    manifest = kg.build_manifest()
    integrity = kg.verify_integrity()

    snap_path = get_path("runtime_root") / "graph" / "graph_snapshot_latest.json"
    snap_path.parent.mkdir(parents=True, exist_ok=True)
    snap_validation = validate_instance(snapshot.to_dict(), "graph_snapshot.schema.json")
    if snap_validation.valid:
        tmp = snap_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(snapshot.to_dict(), indent=2, default=str))
        tmp.rename(snap_path)
    else:
        return snapshot, [], [f"Snapshot validation failed: {snap_validation.errors}"], "FAIL"

    man_path = get_path("runtime_root") / "graph" / "graph_manifest_latest.json"
    man_validation = validate_instance(manifest.to_dict(), "graph_manifest.schema.json")
    if man_validation.valid:
        tmp = man_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(manifest.to_dict(), indent=2, default=str))
        tmp.rename(man_path)
    else:
        return snapshot, [], [f"Manifest validation failed: {man_validation.errors}"], "FAIL"

    int_path = get_path("runtime_root") / "graph" / "graph_integrity_latest.json"
    int_validation = validate_instance(integrity.to_dict(), "graph_integrity.schema.json")
    if int_validation.valid:
        tmp = int_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(integrity.to_dict(), indent=2, default=str))
        tmp.rename(int_path)
    else:
        return snapshot, [], [f"Integrity validation failed: {int_validation.errors}"], "FAIL"

    idx_path = get_path("runtime_root") / "graph" / "graph_index.json"
    tmp = idx_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(index.to_dict(), indent=2, default=str))
    tmp.rename(idx_path)

    status = GraphBuildStatus.PASS.value
    if snapshot.warnings or kg._warnings:
        status = GraphBuildStatus.PARTIAL.value

    return snapshot, list(kg._warnings), list(kg._errors), status


def _print_text_summary(
    snapshot: GraphSnapshot,
    warnings: list[str],
    errors: list[str],
    status: str,
):
    print(f"Knowledge Graph: {status}")
    print(f"Nodes: {snapshot.node_count}")
    print(f"Edges: {snapshot.edge_count}")
    print(f"Integrity: {snapshot.integrity_report.get('status', 'UNKNOWN')}")
    print(f"Snapshot: .agentx-init/graph/graph_snapshot_latest.json")
    print(f"Manifest: .agentx-init/graph/graph_manifest_latest.json")
    if warnings:
        for w in warnings:
            print(f"  Warning: {w}")
    if errors:
        for e in errors:
            print(f"  Error: {e}")


def _query_graph(args) -> GraphQueryResult:
    kg = KnowledgeGraph()
    if args.node_id:
        return kg.query_graph(GraphQuery(query_type="node_id", value=args.node_id))
    if args.node_type:
        return kg.query_graph(GraphQuery(query_type="node_type", value=args.node_type))
    if args.edge_type:
        return kg.query_graph(GraphQuery(query_type="edge_type", value=args.edge_type))
    if args.incoming:
        return kg.query_graph(GraphQuery(query_type="incoming", value=args.incoming))
    if args.outgoing:
        return kg.query_graph(GraphQuery(query_type="outgoing", value=args.outgoing))
    return kg.query_graph(GraphQuery(query_type="all"))


def run(args):
    if args.mode == "query":
        result = _query_graph(args)
        result_dict = result.to_dict() if hasattr(result, "to_dict") else result
        if args.json or args.output_format == "json":
            print(json.dumps(result_dict, indent=2, default=str))
        else:
            print(f"Query results: {result_dict.get('result_count', 0)}")
            nodes = result_dict.get("node_results", [])
            edges = result_dict.get("edge_results", [])
            for n in nodes[:20]:
                print(f"  Node: {n.get('node_id', '?')} ({n.get('node_type', '?')}) - {n.get('label', '?')}")
            for e in edges[:20]:
                print(f"  Edge: {e.get('edge_id', '?')} {e.get('source_node_id', '?')} -> {e.get('target_node_id', '?')} [{e.get('edge_type', '?')}]")
            if len(nodes) > 20 or len(edges) > 20:
                print(f"  ... and more (total {result_dict.get('result_count', 0)})")
        append_event({
            "event_type": "graph_query",
            "category": "GRAPH",
            "status": "SUCCESS",
            "summary": f"Graph query returned {result_dict.get('result_count', 0)} results",
            "component": "graph_command",
        })
        return

    if args.mode == "status":
        kg = KnowledgeGraph()
        manifest = kg.build_manifest()
        man_dict = manifest.to_dict()
        if args.json or args.output_format == "json":
            print(json.dumps(man_dict, indent=2, default=str))
        else:
            print(f"Graph Status")
            print(f"  Nodes: {man_dict.get('node_count', 0)}")
            print(f"  Edges: {man_dict.get('edge_count', 0)}")
            print(f"  Node types: {', '.join(man_dict.get('node_types', []))}")
            print(f"  Edge types: {', '.join(man_dict.get('edge_types', []))}")
            print(f"  Latest snapshot: {man_dict.get('latest_snapshot', 'N/A')}")
        append_event({
            "event_type": "graph_status",
            "category": "GRAPH",
            "status": "SUCCESS",
            "summary": f"Graph status: {man_dict.get('node_count', 0)} nodes, {man_dict.get('edge_count', 0)} edges",
            "component": "graph_command",
        })
        return

    snapshot, warnings, errors, status = _build_graph()

    if args.json or args.output_format == "json":
        result = {
            "status": status,
            "node_count": snapshot.node_count,
            "edge_count": snapshot.edge_count,
            "integrity_status": snapshot.integrity_report.get("status", "UNKNOWN"),
            "warnings": warnings,
            "errors": errors,
        }
        print(json.dumps(result, indent=2, default=str))
    else:
        _print_text_summary(snapshot, warnings, errors, status)

    append_event({
        "event_type": "graph_build",
        "category": "GRAPH",
        "status": status,
        "summary": f"Graph built: {snapshot.node_count} nodes, {snapshot.edge_count} edges, integrity {snapshot.integrity_report.get('status', 'UNKNOWN')}",
        "component": "graph_command",
        "artifact_refs": [
            str(get_path("runtime_root") / "graph" / "graph_snapshot_latest.json"),
            str(get_path("runtime_root") / "graph" / "graph_manifest_latest.json"),
            str(get_path("runtime_root") / "graph" / "graph_integrity_latest.json"),
        ],
    })

    if status == GraphBuildStatus.FAIL.value:
        sys.exit(1)
    elif status == GraphBuildStatus.BLOCKED.value:
        sys.exit(3)
    elif status == GraphBuildStatus.PARTIAL.value:
        sys.exit(4)
    else:
        sys.exit(0)
