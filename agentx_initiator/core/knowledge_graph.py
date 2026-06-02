from __future__ import annotations
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from agentx_initiator.core.graph_model import (
    GraphNode, GraphEdge, GraphQuery, GraphQueryResult,
    GraphSnapshot, GraphManifest, GraphIntegrityReport,
    GraphWriteResult, GraphIndex, GraphArtifactDiscovery,
    GraphBuildStatus, RecordStatus, NodeType, EdgeType,
    compute_content_hash, OWNER_COMPONENT,
)
from agentx_initiator.core.graph_index import (
    build_graph_index as _build_graph_index,
    find_outgoing_edges, find_incoming_edges, find_neighbors,
)
from agentx_initiator.core.path_registry import get_path
from agentx_initiator.core.schema_validation import validate_instance


KNOWN_COMPONENTS = [
    ("ConfigPaths", "Config / Paths"),
    ("AuditLog", "Audit Log"),
    ("RepositoryScanner", "Repository Scanner"),
    ("LayerMapper", "Layer Mapper"),
    ("ArchitectureAnalyzer", "Architecture Analyzer"),
    ("GovernanceEngine", "Governance Engine"),
    ("RiskEngine", "Risk Engine"),
    ("EvolutionPlanner", "Evolution Planner"),
    ("PatchProposalGenerator", "Patch Proposal Generator"),
    ("ValidationRunner", "Validation Runner"),
    ("MemoryStore", "Memory Store"),
    ("ReportWriter", "Report Writer"),
    ("KnowledgeGraph", "Knowledge Graph"),
    ("CLICommands", "CLI Commands"),
]

GRAPH_SCHEMA_NAMES = [
    "graph_node.schema.json",
    "graph_edge.schema.json",
    "graph_snapshot.schema.json",
    "graph_query_result.schema.json",
    "graph_manifest.schema.json",
    "graph_integrity.schema.json",
]

PM1_ARTIFACTS = [
    ("repo_scan_latest", "snapshots/repo_scan_latest.json", True),
    ("architecture_latest", "snapshots/architecture_latest.json", True),
]

PM2_OPTIONAL_ARTIFACTS = [
    ("governance_latest", "snapshots/governance_latest.json"),
    ("risk_latest", "snapshots/risk_latest.json"),
    ("evolution_plan_latest", "snapshots/evolution_plan_latest.json"),
    ("patch_proposal_latest", "snapshots/patch_proposal_latest.json"),
    ("validation_report_latest", "snapshots/validation_report_latest.json"),
    ("memory_snapshot_latest", "snapshots/memory_snapshot_latest.json"),
    ("memory_manifest_latest", "snapshots/memory_manifest_latest.json"),
]


def _graph_dir() -> Path:
    return get_path("runtime_root") / "graph"


def _nodes_jsonl() -> Path:
    return _graph_dir() / "graph_nodes.jsonl"


def _edges_jsonl() -> Path:
    return _graph_dir() / "graph_edges.jsonl"


def _snapshot_json() -> Path:
    return _graph_dir() / "graph_snapshot_latest.json"


def _manifest_json() -> Path:
    return _graph_dir() / "graph_manifest_latest.json"


def _integrity_json() -> Path:
    return _graph_dir() / "graph_integrity_latest.json"


def _index_json() -> Path:
    return _graph_dir() / "graph_index.json"


def _load_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    valid: list[dict] = []
    warnings: list[str] = []
    if not path.exists():
        return valid, warnings
    for i, line in enumerate(path.read_text().splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
            valid.append(obj)
        except json.JSONDecodeError:
            warnings.append(f"Malformed JSONL line {i} in {path.name}: preserved")
    return valid, warnings


def _read_artifact_json(path: Path) -> tuple[Optional[dict], Optional[str]]:
    if not path.exists():
        return None, None
    try:
        data = json.loads(path.read_text())
        return data, None
    except (json.JSONDecodeError, OSError) as e:
        return None, str(e)


def _read_artifact_lines(path: Path) -> tuple[list[dict], list[str]]:
    if not path.exists():
        return [], []
    return _load_jsonl(path)


def _make_node_id(node_type: str, stable_ref: str) -> str:
    ref_hash = hashlib.sha256(stable_ref.encode("utf-8")).hexdigest()[:16]
    return f"graph-node::{node_type}::{ref_hash}"


def _make_edge_id(
    edge_type: str, source_id: str, target_id: str, evidence_ref: str = "",
) -> str:
    raw = f"{source_id}::{target_id}::{edge_type}::{evidence_ref}"
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"graph-edge::{edge_type}::{h}"


def _is_duplicate_node(
    node: GraphNode, existing_nodes: list[dict],
) -> bool:
    for en in existing_nodes:
        if (en.get("node_type") == node.node_type
                and en.get("source_ref") == node.source_ref
                and en.get("source_component") == node.source_component
                and en.get("content_hash") == node.content_hash
                and en.get("status") == RecordStatus.ACTIVE.value):
            return True
    return False


def _is_duplicate_edge(
    edge: GraphEdge, existing_edges: list[dict],
) -> bool:
    for ee in existing_edges:
        if (ee.get("edge_type") == edge.edge_type
                and ee.get("source_node_id") == edge.source_node_id
                and ee.get("target_node_id") == edge.target_node_id
                and ee.get("source_ref") == edge.source_ref
                and ee.get("content_hash") == edge.content_hash
                and ee.get("status") == RecordStatus.ACTIVE.value):
            return True
    return False


class KnowledgeGraph:
    def __init__(self):
        self._graph_dir = _graph_dir()
        self._graph_dir.mkdir(parents=True, exist_ok=True)
        self._loaded_nodes: list[dict] = []
        self._loaded_edges: list[dict] = []
        self._warnings: list[str] = []
        self._errors: list[str] = []

    def load_nodes(self) -> list[GraphNode]:
        raw, warns = _load_jsonl(_nodes_jsonl())
        self._loaded_nodes = raw
        self._warnings.extend(warns)
        result: list[GraphNode] = []
        for d in raw:
            try:
                result.append(GraphNode(**d))
            except (TypeError, ValueError):
                continue
        return result

    def load_edges(self) -> list[GraphEdge]:
        raw, warns = _load_jsonl(_edges_jsonl())
        self._loaded_edges = raw
        self._warnings.extend(warns)
        result: list[GraphEdge] = []
        for d in raw:
            try:
                result.append(GraphEdge(**d))
            except (TypeError, ValueError):
                continue
        return result

    def add_node(self, node: GraphNode) -> GraphWriteResult:
        valid = validate_instance(node.to_dict(), "graph_node.schema.json")
        if not valid.valid:
            return GraphWriteResult(
                status="REJECTED", record_id=node.node_id,
                errors=[f"Schema validation failed: {valid.errors}"],
            )
        existing = [n.to_dict() for n in self.load_nodes()]
        if _is_duplicate_node(node, existing):
            return GraphWriteResult(
                status="DUPLICATE_SKIPPED", record_id=node.node_id,
                warnings=["Duplicate active node, not appended"],
            )
        path = _nodes_jsonl()
        with open(path, "a") as f:
            f.write(json.dumps(node.to_dict(), default=str) + "\n")
        return GraphWriteResult(
            status="ACCEPTED", record_id=node.node_id,
            content_hash=node.content_hash,
        )

    def add_edge(self, edge: GraphEdge) -> GraphWriteResult:
        valid = validate_instance(edge.to_dict(), "graph_edge.schema.json")
        if not valid.valid:
            return GraphWriteResult(
                status="REJECTED", record_id=edge.edge_id,
                errors=[f"Schema validation failed: {valid.errors}"],
            )
        existing_nodes = [n.to_dict() for n in self.load_nodes()]
        existing_edges = [e.to_dict() for e in self.load_edges()]
        node_ids = {n.get("node_id") for n in existing_nodes}
        if edge.source_node_id not in node_ids:
            return GraphWriteResult(
                status="REJECTED", record_id=edge.edge_id,
                errors=[f"Missing source endpoint: {edge.source_node_id}"],
            )
        if edge.target_node_id not in node_ids:
            return GraphWriteResult(
                status="REJECTED", record_id=edge.edge_id,
                errors=[f"Missing target endpoint: {edge.target_node_id}"],
            )
        if _is_duplicate_edge(edge, existing_edges):
            return GraphWriteResult(
                status="DUPLICATE_SKIPPED", record_id=edge.edge_id,
                warnings=["Duplicate active edge, not appended"],
            )
        path = _edges_jsonl()
        with open(path, "a") as f:
            f.write(json.dumps(edge.to_dict(), default=str) + "\n")
        return GraphWriteResult(
            status="ACCEPTED", record_id=edge.edge_id,
            content_hash=edge.content_hash,
        )

    def query_graph(self, query: GraphQuery) -> GraphQueryResult:
        qid = str(uuid4())
        nodes = self.load_nodes()
        edges = self.load_edges()
        node_dicts = [n.to_dict() for n in nodes]
        edge_dicts = [e.to_dict() for e in edges]

        if query.query_type == "all":
            return GraphQueryResult(
                query_id=qid, query=query.to_dict(),
                node_results=sorted(node_dicts, key=lambda x: x["node_id"]),
                edge_results=sorted(edge_dicts, key=lambda x: x["edge_id"]),
                result_count=len(node_dicts) + len(edge_dicts),
            ).to_dict()

        if query.query_type == "node_id":
            results = [n.to_dict() for n in nodes if n.node_id == query.value]
            return GraphQueryResult(
                query_id=qid, query=query.to_dict(),
                node_results=sorted(results, key=lambda x: x["node_id"]),
                result_count=len(results),
            ).to_dict()

        if query.query_type == "node_type":
            results = [n.to_dict() for n in nodes if n.node_type == query.value]
            return GraphQueryResult(
                query_id=qid, query=query.to_dict(),
                node_results=sorted(results, key=lambda x: x["node_id"]),
                result_count=len(results),
            ).to_dict()

        if query.query_type == "edge_type":
            results = [e.to_dict() for e in edges if e.edge_type == query.value]
            return GraphQueryResult(
                query_id=qid, query=query.to_dict(),
                edge_results=sorted(results, key=lambda x: x["edge_id"]),
                result_count=len(results),
            ).to_dict()

        if query.query_type == "outgoing":
            results = find_outgoing_edges(query.value, edges)
            return GraphQueryResult(
                query_id=qid, query=query.to_dict(),
                edge_results=[e.to_dict() for e in results],
                result_count=len(results),
            ).to_dict()

        if query.query_type == "incoming":
            results = find_incoming_edges(query.value, edges)
            return GraphQueryResult(
                query_id=qid, query=query.to_dict(),
                edge_results=[e.to_dict() for e in results],
                result_count=len(results),
            ).to_dict()

        if query.query_type == "neighbors":
            results = find_neighbors(query.value, nodes, edges)
            return GraphQueryResult(
                query_id=qid, query=query.to_dict(),
                node_results=[n.to_dict() for n in results],
                result_count=len(results),
            ).to_dict()

        if query.query_type == "source_component":
            results = [n.to_dict() for n in nodes if n.source_component == query.value]
            return GraphQueryResult(
                query_id=qid, query=query.to_dict(),
                node_results=sorted(results, key=lambda x: x["node_id"]),
                result_count=len(results),
            ).to_dict()

        if query.query_type == "artifact_path":
            results = [n.to_dict() for n in nodes if query.value in n.source_ref]
            return GraphQueryResult(
                query_id=qid, query=query.to_dict(),
                node_results=sorted(results, key=lambda x: x["node_id"]),
                result_count=len(results),
            ).to_dict()

        return GraphQueryResult(
            query_id=qid, query=query.to_dict(),
            errors=[f"Unknown query type: {query.query_type}"],
        ).to_dict()

    def build_index(self) -> GraphIndex:
        nodes = self.load_nodes()
        edges = self.load_edges()
        return _build_graph_index(nodes, edges)

    def build_snapshot(
        self, nodes: Optional[list[GraphNode]] = None,
             edges: Optional[list[GraphEdge]] = None,
    ) -> GraphSnapshot:
        if nodes is None:
            nodes = self.load_nodes()
        if edges is None:
            edges = self.load_edges()
        integrity = self.verify_integrity(nodes=nodes, edges=edges)
        snap = GraphSnapshot(
            snapshot_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            nodes=sorted([n.to_dict() for n in nodes], key=lambda x: x["node_id"]),
            edges=sorted([e.to_dict() for e in edges], key=lambda x: x["edge_id"]),
            integrity_report=integrity.to_dict(),
            warnings=list(self._warnings),
            errors=list(self._errors),
        )
        return snap

    def build_manifest(self) -> GraphManifest:
        nodes = self.load_nodes()
        edges = self.load_edges()
        snapshot_path = str(_snapshot_json().relative_to(get_path("runtime_root")))
        schema_versions: dict[str, str] = {}
        for sn in GRAPH_SCHEMA_NAMES:
            try:
                schema = json.loads(
                    (Path(__file__).resolve().parent.parent / "schemas" / sn).read_text()
                )
                sv = schema.get("properties", {}).get("schema_version", {}).get("const", "1.0")
                schema_versions[sn] = sv
            except Exception:
                schema_versions[sn] = "unknown"
        return GraphManifest(
            manifest_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            nodes=[n.to_dict() for n in nodes],
            edges=[e.to_dict() for e in edges],
            latest_snapshot=snapshot_path,
            schema_versions=schema_versions,
            warnings=list(self._warnings),
            errors=list(self._errors),
        )

    def verify_integrity(
        self, nodes: Optional[list[GraphNode]] = None,
             edges: Optional[list[GraphEdge]] = None,
    ) -> GraphIntegrityReport:
        if nodes is None:
            nodes = self.load_nodes()
        if edges is None:
            edges = self.load_edges()
        node_ids = {n.node_id for n in nodes}
        missing_endpoints: list[dict] = []
        for e in edges:
            if e.source_node_id not in node_ids:
                missing_endpoints.append({
                    "edge_id": e.edge_id,
                    "missing_endpoint": e.source_node_id,
                    "endpoint_type": "source",
                })
            if e.target_node_id not in node_ids:
                missing_endpoints.append({
                    "edge_id": e.edge_id,
                    "missing_endpoint": e.target_node_id,
                    "endpoint_type": "target",
                })
        status = GraphBuildStatus.PASS.value
        if missing_endpoints:
            status = GraphBuildStatus.FAIL.value
        return GraphIntegrityReport(
            integrity_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            checked_node_count=len(nodes),
            checked_edge_count=len(edges),
            missing_endpoint_edges=missing_endpoints,
            warnings=list(self._warnings),
            errors=list(self._errors),
        )

    def _make_component_node(self, cid: str, label: str) -> GraphNode:
        return GraphNode(
            node_id=_make_node_id(NodeType.COMPONENT.value, cid),
            node_type=NodeType.COMPONENT.value,
            label=label,
            status=RecordStatus.ACTIVE.value,
            source_ref=f"core/{cid.lower()}.py",
            source_component="KnowledgeGraph",
            properties={"component_id": cid},
        )

    def _make_artifact_node(
        self, artifact_path: str, source_component: str,
        extra_props: dict | None = None,
    ) -> GraphNode:
        ref = str(get_path("runtime_root") / artifact_path)
        props = {"path": artifact_path, "artifact_type": Path(artifact_path).suffix}
        if extra_props:
            props.update(extra_props)
        return GraphNode(
            node_id=_make_node_id(NodeType.ARTIFACT.value, ref),
            node_type=NodeType.ARTIFACT.value,
            label=Path(artifact_path).name,
            status=RecordStatus.ACTIVE.value,
            source_ref=ref,
            source_component=source_component,
            properties=props,
        )

    def _make_schema_node(self, schema_name: str) -> GraphNode:
        ref = f"schemas/{schema_name}"
        return GraphNode(
            node_id=_make_node_id(NodeType.SCHEMA.value, ref),
            node_type=NodeType.SCHEMA.value,
            label=schema_name,
            status=RecordStatus.ACTIVE.value,
            source_ref=ref,
            source_component="KnowledgeGraph",
            properties={"schema_path": ref, "owner_component": OWNER_COMPONENT},
        )

    def discover_artifacts(self) -> list[GraphArtifactDiscovery]:
        runtime_root = get_path("runtime_root")
        discoveries: list[GraphArtifactDiscovery] = []

        for name, rel_path, required in PM1_ARTIFACTS:
            full = runtime_root / rel_path
            exists = full.exists()
            data, err = _read_artifact_json(full)
            discovery = GraphArtifactDiscovery(
                artifact_path=rel_path,
                artifact_type="snapshot",
                required_for_pm3_minimum=required,
                exists=exists,
                valid_json=data is not None,
                consumed=False,
                warning=err,
            )
            discoveries.append(discovery)

        for name, rel_path in PM2_OPTIONAL_ARTIFACTS:
            full = runtime_root / rel_path
            exists = full.exists()
            data, err = _read_artifact_json(full)
            discovery = GraphArtifactDiscovery(
                artifact_path=rel_path,
                artifact_type="snapshot",
                required_for_pm3_minimum=False,
                exists=exists,
                valid_json=data is not None,
                consumed=False,
                warning=err or ("Missing optional PM2 artifact" if not exists else None),
            )
            discoveries.append(discovery)

        audit_path = runtime_root / "memory" / "audit_events.jsonl"
        audit_exists = audit_path.exists()
        discoveries.append(GraphArtifactDiscovery(
            artifact_path="memory/audit_events.jsonl",
            artifact_type="jsonl",
            required_for_pm3_minimum=True,
            exists=audit_exists,
            valid_json=audit_exists,
            consumed=False,
        ))

        memory_path = runtime_root / "memory" / "memory_records.jsonl"
        memory_exists = memory_path.exists()
        discoveries.append(GraphArtifactDiscovery(
            artifact_path="memory/memory_records.jsonl",
            artifact_type="jsonl",
            required_for_pm3_minimum=False,
            exists=memory_exists,
            valid_json=memory_exists,
            consumed=False,
            warning=None if memory_exists else "Missing optional memory_records.jsonl",
        ))

        return discoveries

    def ingest_known_artifacts(self) -> GraphSnapshot:
        runtime_root = get_path("runtime_root")
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        all_warnings: list[str] = []
        all_errors: list[str] = []

        discoveries = self.discover_artifacts()

        for cid, label in KNOWN_COMPONENTS:
            nodes.append(self._make_component_node(cid, label))

        for discovery in discoveries:
            if not discovery.exists:
                if discovery.warning:
                    all_warnings.append(discovery.warning)
                continue
            if discovery.artifact_type == "snapshot":
                source_comp = discovery.artifact_path.split("/")[-1].replace("_latest.json", "")
                art_node = self._make_artifact_node(discovery.artifact_path, source_comp)
                nodes.append(art_node)
                discovery.consumed = True
            elif discovery.artifact_type == "jsonl":
                full = runtime_root / discovery.artifact_path
                lines, warns = _load_jsonl(full)
                all_warnings.extend(warns)
                if discovery.artifact_path == "memory/audit_events.jsonl":
                    for i, line in enumerate(lines):
                        event_type = line.get("event_type", "unknown")
                        event_id = line.get("event_id", f"audit-line-{i}")
                        aud_node = GraphNode(
                            node_id=_make_node_id(NodeType.AUDIT_EVENT.value, event_id),
                            node_type=NodeType.AUDIT_EVENT.value,
                            label=f"{event_type} - {line.get('status', 'UNKNOWN')}",
                            status=RecordStatus.ACTIVE.value,
                            source_ref=f"{discovery.artifact_path}:{i + 1}",
                            source_component="AuditLog",
                            properties={
                                "event_id": event_id,
                                "event_type": event_type,
                                "component": line.get("component", ""),
                                "status": line.get("status", ""),
                            },
                        )
                        nodes.append(aud_node)
                    discovery.consumed = True
                elif discovery.artifact_path == "memory/memory_records.jsonl":
                    for i, line in enumerate(lines):
                        mem_id = line.get("record_id", f"memory-line-{i}")
                        mem_node = GraphNode(
                            node_id=_make_node_id(NodeType.MEMORY_RECORD.value, mem_id),
                            node_type=NodeType.MEMORY_RECORD.value,
                            label=mem_id,
                            status=RecordStatus.ACTIVE.value,
                            source_ref=f"{discovery.artifact_path}:{i + 1}",
                            source_component="MemoryStore",
                            properties={
                                "memory_id": mem_id,
                                "category": line.get("record_type", ""),
                                "status": line.get("status", ""),
                            },
                        )
                        nodes.append(mem_node)
                    discovery.consumed = True

        for sn in GRAPH_SCHEMA_NAMES:
            nodes.append(self._make_schema_node(sn))

        for discovery in discoveries:
            if not discovery.consumed or not discovery.exists:
                continue
            art_path = discovery.artifact_path
            if not art_path.endswith(".json"):
                continue
            art_name = Path(art_path).name
            source_comp = discovery.artifact_path.split("/")[-1].replace("_latest.json", "Component")

            edge_id = _make_edge_id(EdgeType.PRODUCES.value, "RepositoryScanner", art_path)
            edge = GraphEdge(
                edge_id=edge_id,
                source_node_id=_make_node_id(NodeType.COMPONENT.value, "RepositoryScanner"),
                target_node_id=_make_node_id(NodeType.ARTIFACT.value, str(runtime_root / art_path)),
                edge_type=EdgeType.PRODUCES.value,
                status=RecordStatus.ACTIVE.value,
                source_ref=art_path,
                source_component="KnowledgeGraph",
                evidence_refs=[art_path],
            )
            edges.append(edge)

        kg_node_id = _make_node_id(NodeType.COMPONENT.value, "KnowledgeGraph")
        snap_art_path = "graph/graph_snapshot_latest.json"
        snap_full = runtime_root / snap_art_path
        snap_art_node = GraphNode(
            node_id=_make_node_id(NodeType.ARTIFACT.value, str(snap_full)),
            node_type=NodeType.ARTIFACT.value,
            label="graph_snapshot_latest.json",
            status=RecordStatus.ACTIVE.value,
            source_ref=str(snap_full),
            source_component="KnowledgeGraph",
            properties={"path": snap_art_path, "artifact_type": ".json"},
        )
        nodes.append(snap_art_node)
        snap_edge = GraphEdge(
            edge_id=_make_edge_id(EdgeType.PRODUCES.value, kg_node_id, snap_art_path),
            source_node_id=kg_node_id,
            target_node_id=snap_art_node.node_id,
            edge_type=EdgeType.PRODUCES.value,
            status=RecordStatus.ACTIVE.value,
            source_ref=snap_art_path,
            source_component="KnowledgeGraph",
            evidence_refs=[snap_art_path],
        )
        edges.append(snap_edge)

        for n in nodes:
            result = self.add_node(n)
            if result.status == "REJECTED":
                all_errors.extend(result.errors)

        for e in edges:
            result = self.add_edge(e)
            if result.status == "REJECTED":
                all_errors.extend(result.errors)

        self._warnings = all_warnings
        self._errors = all_errors
        return self.build_snapshot()


def add_node(node: GraphNode) -> GraphWriteResult:
    kg = KnowledgeGraph()
    kg.load_nodes()
    kg.load_edges()
    return kg.add_node(node)


def add_edge(edge: GraphEdge) -> GraphWriteResult:
    kg = KnowledgeGraph()
    kg.load_nodes()
    kg.load_edges()
    return kg.add_edge(edge)


def query_graph(query: GraphQuery) -> GraphQueryResult:
    kg = KnowledgeGraph()
    return kg.query_graph(query)


def build_graph_index(
    nodes: list[GraphNode], edges: list[GraphEdge],
) -> GraphIndex:
    return _build_graph_index(nodes, edges)


def build_snapshot(
    nodes: list[GraphNode], edges: list[GraphEdge],
) -> GraphSnapshot:
    return KnowledgeGraph().build_snapshot(nodes=nodes, edges=edges)


def verify_graph_integrity(
    nodes: list[GraphNode], edges: list[GraphEdge],
) -> GraphIntegrityReport:
    kg = KnowledgeGraph()
    return kg.verify_integrity(nodes=nodes, edges=edges)
