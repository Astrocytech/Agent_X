from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from enum import Enum
import hashlib
import json


SCHEMA_VERSION = "1.0"
OWNER_COMPONENT = "AGENTX_KNOWLEDGE_GRAPH"


class NodeType(str, Enum):
    COMPONENT = "COMPONENT"
    ARTIFACT = "ARTIFACT"
    MEMORY_RECORD = "MEMORY_RECORD"
    AUDIT_EVENT = "AUDIT_EVENT"
    RISK_ITEM = "RISK_ITEM"
    GOVERNANCE_DECISION = "GOVERNANCE_DECISION"
    EVOLUTION_PLAN = "EVOLUTION_PLAN"
    CANDIDATE_ACTION = "CANDIDATE_ACTION"
    PATCH_PROPOSAL = "PATCH_PROPOSAL"
    VALIDATION_REPORT = "VALIDATION_REPORT"
    REPOSITORY = "REPOSITORY"
    SCHEMA = "SCHEMA"
    TEST = "TEST"
    VALIDATOR = "VALIDATOR"
    REPORT = "REPORT"
    COMMAND = "COMMAND"
    UNKNOWN = "UNKNOWN"


class EdgeType(str, Enum):
    DEPENDS_ON = "DEPENDS_ON"
    PRODUCES = "PRODUCES"
    CONSUMES = "CONSUMES"
    SUPPORTS = "SUPPORTS"
    VALIDATES = "VALIDATES"
    SUPERSEDES = "SUPERSEDES"
    CORRECTS = "CORRECTS"
    REFERENCES = "REFERENCES"
    AFFECTS = "AFFECTS"
    GENERATED_BY = "GENERATED_BY"
    DERIVED_FROM = "DERIVED_FROM"
    BLOCKED_BY = "BLOCKED_BY"
    MITIGATES = "MITIGATES"
    EVIDENCED_BY = "EVIDENCED_BY"
    IMPLEMENTS = "IMPLEMENTS"
    USES_SCHEMA = "USES_SCHEMA"
    HAS_TEST = "HAS_TEST"
    HAS_VALIDATOR = "HAS_VALIDATOR"
    UNKNOWN = "UNKNOWN"


class RecordStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    CORRECTION = "CORRECTION"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


class GraphBuildStatus(str, Enum):
    PASS = "PASS"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


def compute_content_hash(obj: dict, exclude_keys: set[str] | None = None) -> str:
    exclude = set(exclude_keys or [])
    exclude.add("content_hash")
    canonical = {k: v for k, v in obj.items() if k not in exclude}
    serialized = json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _to_dict(obj: Any) -> dict:
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return asdict(obj)


@dataclass
class GraphNode:
    node_id: str
    node_type: str
    label: str
    status: str = RecordStatus.ACTIVE.value
    source_ref: str = ""
    source_component: str = ""
    properties: dict = field(default_factory=dict)
    content_hash: str = ""
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "graph_node.schema.json"
    owner_component: str = OWNER_COMPONENT
    artifact_type: str = "graph_node"

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = compute_content_hash(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "schema_id": self.schema_id,
            "owner_component": self.owner_component,
            "artifact_type": self.artifact_type,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "status": self.status,
            "source_ref": self.source_ref,
            "source_component": self.source_component,
            "properties": self.properties,
            "content_hash": self.content_hash,
        }


@dataclass
class GraphEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: str
    status: str = RecordStatus.ACTIVE.value
    source_ref: str = ""
    source_component: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    properties: dict = field(default_factory=dict)
    content_hash: str = ""
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "graph_edge.schema.json"
    owner_component: str = OWNER_COMPONENT
    artifact_type: str = "graph_edge"

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = compute_content_hash(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "schema_id": self.schema_id,
            "owner_component": self.owner_component,
            "artifact_type": self.artifact_type,
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "edge_type": self.edge_type,
            "status": self.status,
            "source_ref": self.source_ref,
            "source_component": self.source_component,
            "evidence_refs": self.evidence_refs,
            "properties": self.properties,
            "content_hash": self.content_hash,
        }


@dataclass
class GraphQuery:
    query_type: str = "all"
    value: str = ""
    filters: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "query_type": self.query_type,
            "value": self.value,
            "filters": self.filters,
        }


@dataclass
class GraphQueryResult:
    query_id: str
    query: dict
    node_results: list[dict] = field(default_factory=list)
    edge_results: list[dict] = field(default_factory=list)
    result_count: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "graph_query_result.schema.json"
    owner_component: str = OWNER_COMPONENT
    artifact_type: str = "graph_query_result"
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "schema_id": self.schema_id,
            "owner_component": self.owner_component,
            "artifact_type": self.artifact_type,
            "query_id": self.query_id,
            "timestamp": self.timestamp,
            "query": self.query,
            "node_results": self.node_results,
            "edge_results": self.edge_results,
            "result_count": self.result_count,
            "warnings": self.warnings,
            "errors": self.errors,
        }


@dataclass
class GraphSnapshot:
    snapshot_id: str
    timestamp: str
    nodes: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    integrity_report: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "graph_snapshot.schema.json"
    owner_component: str = OWNER_COMPONENT
    artifact_type: str = "graph_snapshot"

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "schema_id": self.schema_id,
            "owner_component": self.owner_component,
            "artifact_type": self.artifact_type,
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "nodes": self.nodes,
            "edges": self.edges,
            "integrity_report": self.integrity_report,
            "warnings": self.warnings,
            "errors": self.errors,
        }


@dataclass
class GraphManifest:
    manifest_id: str
    timestamp: str
    nodes: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    latest_snapshot: str = ""
    schema_versions: dict = field(default_factory=dict)
    artifact_discovery: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "graph_manifest.schema.json"
    owner_component: str = OWNER_COMPONENT
    artifact_type: str = "graph_manifest"

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def node_types(self) -> list[str]:
        types: set[str] = set()
        for n in self.nodes:
            if isinstance(n, dict):
                t = n.get("node_type", n.get("type", ""))
                if t:
                    types.add(t)
        return sorted(types)

    @property
    def edge_types(self) -> list[str]:
        types: set[str] = set()
        for e in self.edges:
            if isinstance(e, dict):
                t = e.get("edge_type", e.get("type", ""))
                if t:
                    types.add(t)
        return sorted(types)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "schema_id": self.schema_id,
            "owner_component": self.owner_component,
            "artifact_type": self.artifact_type,
            "manifest_id": self.manifest_id,
            "timestamp": self.timestamp,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "node_types": self.node_types,
            "edge_types": self.edge_types,
            "latest_snapshot": self.latest_snapshot,
            "schema_versions": self.schema_versions,
            "artifact_discovery": self.artifact_discovery,
            "warnings": self.warnings,
            "errors": self.errors,
        }


@dataclass
class GraphIntegrityReport:
    integrity_id: str
    timestamp: str
    status: str = GraphBuildStatus.PASS.value
    checked_node_count: int = 0
    checked_edge_count: int = 0
    missing_endpoint_edges: list[dict] = field(default_factory=list)
    invalid_schema_records: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "graph_integrity.schema.json"
    owner_component: str = OWNER_COMPONENT
    artifact_type: str = "graph_integrity"

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "schema_id": self.schema_id,
            "owner_component": self.owner_component,
            "artifact_type": self.artifact_type,
            "integrity_id": self.integrity_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "checked_node_count": self.checked_node_count,
            "checked_edge_count": self.checked_edge_count,
            "missing_endpoint_edges": self.missing_endpoint_edges,
            "invalid_schema_records": self.invalid_schema_records,
            "warnings": self.warnings,
            "errors": self.errors,
        }


@dataclass
class GraphWriteResult:
    status: str = "ACCEPTED"
    record_id: str = ""
    content_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "record_id": self.record_id,
            "content_hash": self.content_hash,
            "warnings": self.warnings,
            "errors": self.errors,
        }


@dataclass
class GraphIndex:
    nodes_by_id: dict[str, dict] = field(default_factory=dict)
    edges_by_id: dict[str, dict] = field(default_factory=dict)
    outgoing: dict[str, list[dict]] = field(default_factory=dict)
    incoming: dict[str, list[dict]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "node_count": len(self.nodes_by_id),
            "edge_count": len(self.edges_by_id),
        }


@dataclass
class GraphArtifactDiscovery:
    artifact_path: str = ""
    artifact_type: str = ""
    required_for_pm3_minimum: bool = False
    exists: bool = False
    valid_json: bool = False
    schema_valid_if_checked: bool = False
    consumed: bool = False
    warning: str | None = None

    def to_dict(self) -> dict:
        return {
            "artifact_path": self.artifact_path,
            "artifact_type": self.artifact_type,
            "required_for_pm3_minimum": self.required_for_pm3_minimum,
            "exists": self.exists,
            "valid_json": self.valid_json,
            "schema_valid_if_checked": self.schema_valid_if_checked,
            "consumed": self.consumed,
            "warning": self.warning,
        }
