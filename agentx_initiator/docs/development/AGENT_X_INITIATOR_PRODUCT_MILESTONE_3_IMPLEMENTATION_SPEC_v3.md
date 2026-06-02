# Agent_X Initiator — Product Milestone 3 Implementation Specification

**Document type:** Complete implementation handoff for an LLM coding agent  
**Target product:** `agentx-init`  
**Product Milestone:** PM3  
**Primary goal:** Implement the local Knowledge Graph subsystem and activate the `agentx-init graph` command.  
**Runtime write boundary:** `.agentx-init/` only  
**Source mutation policy:** only normal implementation files may be changed during development; the running CLI must never modify Agent_X source files outside `.agentx-init/`.  
**Status:** ready for implementation handoff — Revision 3 final hardening for single-document LLM implementation

---

## 0. How to Use This Document

This document is written so an implementation LLM can complete Product Milestone 3 using this file alone.

The implementation agent must:

1. Treat this document as the local PM3 implementation contract.
2. Keep PM1 and PM2 behavior stable.
3. Implement only the PM3 scope defined here.
4. Avoid broad redesign of existing PM1/PM2 modules.
5. Add the Knowledge Graph as a local structured relationship layer.
6. Activate `agentx-init graph` as the only new PM3 command.
7. Keep all graph outputs schema-valid and evidence-backed.
8. Never use a graph database, vector database, embeddings, semantic inference, remote storage, network calls, or graph visualization in PM3.

If this document conflicts with a frozen component contract, prefer the frozen component contract unless the conflict is only about product milestone placement. Product Milestone 3 exists specifically to integrate the Knowledge Graph and graph CLI into the product roadmap.

---

## 1. PM3 Executive Summary

Product Milestone 3 adds a local, schema-governed Knowledge Graph to `agentx-init`.

The Knowledge Graph records structured relationships between artifacts already produced by PM1 and PM2, such as:

```text
repository scans
architecture reports
governance decisions
risk assessments
evolution plans
candidate actions
patch proposals
validation reports
memory records
audit events
schemas
tests
validators
reports
components
```

PM3 does not add autonomous reasoning. It does not add graph databases. It does not add semantic inference. It does not add visual graph UI. It creates a deterministic local JSON/JSONL graph that can be queried and regenerated from stored artifacts.

The main new user-facing command is:

```bash
agentx-init graph
```

This command builds or refreshes graph artifacts under:

```text
.agentx-init/graph/
```

---

## 2. Required Product Milestone 3 Scope

PM3 must implement:

```text
Knowledge Graph core models
Knowledge Graph storage
Knowledge Graph index builder
Knowledge Graph integrity checker
Knowledge Graph snapshot builder
Knowledge Graph manifest builder
Graph query support
Graph CLI command
Graph schemas
Graph tests
Graph audit events
Graph integration with existing PM1/PM2 artifacts
```

PM3 must not implement:

```text
graph database
Neo4j
NetworkX requirement
vector search
embeddings
semantic search
semantic inference
ontology generation
graph visualization
web UI
remote graph storage
network synchronization
source mutation
governance decisions
risk decisions
evolution planning
patch proposal generation
validation execution
```

---

## 3. Required Inputs From Prior Milestones

PM3 assumes PM1 and PM2 have already produced at least some of the following artifacts.

PM3 must tolerate missing optional artifacts. Missing optional artifacts must create warnings, not crashes.

### 3.1 Required Minimum Inputs

At minimum, PM3 should be able to run if these exist:

```text
.agentx-init/snapshots/repo_scan_latest.json
.agentx-init/snapshots/architecture_latest.json
.agentx-init/memory/audit_events.jsonl
```

If these do not exist, `agentx-init graph` may still create a partial graph from whatever valid artifacts exist, but must mark the result as `PARTIAL` or `BLOCKED` according to the rules in this document.

### 3.2 Optional PM2 Inputs

The graph should consume these when available:

```text
.agentx-init/snapshots/governance_latest.json
.agentx-init/snapshots/risk_latest.json
.agentx-init/snapshots/evolution_plan_latest.json
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/snapshots/validation_report_latest.json
.agentx-init/snapshots/memory_snapshot_latest.json
.agentx-init/snapshots/memory_manifest_latest.json
.agentx-init/memory/governance_history.jsonl
.agentx-init/memory/risk_history.jsonl
.agentx-init/memory/evolution_plan_history.jsonl
.agentx-init/memory/patch_proposal_history.jsonl
.agentx-init/memory/validation_history.jsonl
.agentx-init/memory/memory_records.jsonl
.agentx-init/reports/latest_status.md
.agentx-init/reports/latest_report.md
.agentx-init/reports/report_bundle.json
```

### 3.3 Schema Inputs

PM3 must add and validate these schema files:

```text
agentx_initiator/schemas/graph_node.schema.json
agentx_initiator/schemas/graph_edge.schema.json
agentx_initiator/schemas/graph_snapshot.schema.json
agentx_initiator/schemas/graph_query_result.schema.json
agentx_initiator/schemas/graph_manifest.schema.json
agentx_initiator/schemas/graph_integrity.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

If `completion_record.schema.json` already exists from PM1 or PM2, do not create a conflicting duplicate. Reuse the existing shared schema if compatible.

---

## 4. PM3 Target File Map

### 4.1 New Core Implementation Files

Create or complete:

```text
agentx_initiator/core/graph_model.py
agentx_initiator/core/graph_index.py
agentx_initiator/core/knowledge_graph.py
```

### 4.2 CLI Files

Create or activate:

```text
agentx_initiator/cli/commands/graph.py
```

Update only as needed:

```text
agentx_initiator/cli/main.py
agentx_initiator/cli/registry.py
agentx_initiator/cli/models.py
```

### 4.3 Schema Files

Create:

```text
agentx_initiator/schemas/graph_node.schema.json
agentx_initiator/schemas/graph_edge.schema.json
agentx_initiator/schemas/graph_snapshot.schema.json
agentx_initiator/schemas/graph_query_result.schema.json
agentx_initiator/schemas/graph_manifest.schema.json
agentx_initiator/schemas/graph_integrity.schema.json
```

Create only if missing:

```text
agentx_initiator/schemas/completion_record.schema.json
```

### 4.4 Tests

Create:

```text
agentx_initiator/tests/test_knowledge_graph.py
agentx_initiator/tests/test_graph_index.py
agentx_initiator/tests/test_graph_schema.py
agentx_initiator/tests/test_cli_graph.py
```

### 4.5 Runtime Artifacts

The running tool may write only under `.agentx-init/`.

PM3 graph artifacts:

```text
.agentx-init/graph/graph_nodes.jsonl
.agentx-init/graph/graph_edges.jsonl
.agentx-init/graph/graph_index.json
.agentx-init/graph/graph_snapshot_latest.json
.agentx-init/graph/graph_manifest_latest.json
.agentx-init/graph/graph_integrity_latest.json
.agentx-init/memory/audit_events.jsonl
.agentx-init/logs/command_history.jsonl
```

`graph_integrity_latest.json` is required in this PM3 implementation spec even if the older graph contract only mentioned integrity reports structurally. The file is the runtime persistence point for `GraphIntegrityReport`.

---

## 5. Authority and Boundary Rules

### 5.1 Knowledge Graph Authority

The Knowledge Graph may:

```text
store nodes
store edges
query nodes and edges
build deterministic graph indexes
build graph snapshots
build graph manifests
verify endpoint integrity
record provenance
record evidence references
append audit events
```

The Knowledge Graph must not:

```text
modify source artifacts
modify memory records
modify audit records
make governance decisions
classify risk
generate evolution plans
generate patch proposals
execute validation
infer unsupported relationships
create embeddings
perform semantic search
require a database server
```

### 5.2 Graph CLI Authority

`agentx-init graph` may:

```text
read PM1 and PM2 artifacts
build or refresh graph artifacts under .agentx-init/graph/
write command history
append audit event
print a human-readable summary
return JSON output if supported by existing CLI output-format rules
```

`agentx-init graph` must not:

```text
modify source files
modify L0/L1/L2
execute validation commands
run scans automatically unless explicitly already supported by an existing command contract
invoke governance/risk/planning/proposal logic as active processing
change PM1/PM2 artifacts in place
```

---

## 6. Required Public Surface

### 6.1 `graph_model.py`

Define these data models, preferably as dataclasses unless the project already standardizes on Pydantic:

```python
GraphNode
GraphEdge
GraphQuery
GraphQueryResult
GraphSnapshot
GraphManifest
GraphIntegrityReport
GraphWriteResult
GraphIndex
```

Minimum model requirements:

```text
models serialize to dict
models can be validated before write
models include schema_version
models avoid hidden runtime-only fields in serialized output
model field names match schema field names
```

### 6.2 `graph_index.py`

Provide deterministic index-building and lookup helpers:

```python
build_graph_index(nodes: list[GraphNode], edges: list[GraphEdge]) -> GraphIndex
index_nodes_by_id(nodes: list[GraphNode]) -> dict[str, GraphNode]
index_edges_by_id(edges: list[GraphEdge]) -> dict[str, GraphEdge]
find_outgoing_edges(node_id: str, edges: list[GraphEdge]) -> list[GraphEdge]
find_incoming_edges(node_id: str, edges: list[GraphEdge]) -> list[GraphEdge]
find_neighbors(node_id: str, nodes: list[GraphNode], edges: list[GraphEdge]) -> list[GraphNode]
```

### 6.3 `knowledge_graph.py`

Provide the main service:

```python
class KnowledgeGraph:
    def add_node(self, node: GraphNode) -> GraphWriteResult: ...
    def add_edge(self, edge: GraphEdge) -> GraphWriteResult: ...
    def load_nodes(self) -> list[GraphNode]: ...
    def load_edges(self) -> list[GraphEdge]: ...
    def query_graph(self, query: GraphQuery) -> GraphQueryResult: ...
    def build_index(self) -> GraphIndex: ...
    def build_snapshot(self) -> GraphSnapshot: ...
    def build_manifest(self) -> GraphManifest: ...
    def verify_integrity(self) -> GraphIntegrityReport: ...
    def ingest_known_artifacts(self) -> GraphSnapshot: ...
```

Also expose module-level functions only if this is already the project style:

```python
add_node(node: GraphNode) -> GraphWriteResult
add_edge(edge: GraphEdge) -> GraphWriteResult
query_graph(query: GraphQuery) -> GraphQueryResult
build_graph_index(nodes: list[GraphNode], edges: list[GraphEdge]) -> GraphIndex
build_snapshot(nodes: list[GraphNode], edges: list[GraphEdge]) -> GraphSnapshot
verify_graph_integrity(nodes: list[GraphNode], edges: list[GraphEdge]) -> GraphIntegrityReport
```

No extra public surface should be added unless needed for tests or existing CLI integration.

---

## 7. Graph Vocabulary

### 7.1 Node Types

Allowed node types:

```text
COMPONENT
ARTIFACT
MEMORY_RECORD
AUDIT_EVENT
RISK_ITEM
GOVERNANCE_DECISION
EVOLUTION_PLAN
CANDIDATE_ACTION
PATCH_PROPOSAL
VALIDATION_REPORT
REPOSITORY
SCHEMA
TEST
VALIDATOR
REPORT
COMMAND
UNKNOWN
```

`REPORT` and `COMMAND` are included in PM3 because the graph CLI and report artifacts are product-level entities. If an existing frozen schema omits them, use `ARTIFACT` for reports and `COMPONENT` or `UNKNOWN` for commands instead. Do not break existing schema tests.

### 7.2 Edge Types

Allowed edge types:

```text
DEPENDS_ON
PRODUCES
CONSUMES
SUPPORTS
VALIDATES
SUPERSEDES
CORRECTS
REFERENCES
AFFECTS
GENERATED_BY
DERIVED_FROM
BLOCKED_BY
MITIGATES
EVIDENCED_BY
IMPLEMENTS
USES_SCHEMA
HAS_TEST
HAS_VALIDATOR
UNKNOWN
```

If the implemented schema must match the narrower frozen graph contract exactly, keep only the frozen enum values and map added PM3 concepts to `REFERENCES`, `PRODUCES`, `CONSUMES`, `VALIDATES`, or `UNKNOWN`.

### 7.3 Record Status Values

Allowed status values:

```text
ACTIVE
SUPERSEDED
CORRECTION
INVALID
UNKNOWN
```

---

## 8. Required Schema Contracts

All graph schemas must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "string",
  "owner_component": "AGENTX_KNOWLEDGE_GRAPH",
  "artifact_type": "string"
}
```

The runtime artifact object itself must also include the required runtime fields below.

### 8.1 Graph Node Schema

Each graph node must include:

```json
{
  "schema_version": "1.0",
  "node_id": "string",
  "node_type": "COMPONENT|ARTIFACT|MEMORY_RECORD|AUDIT_EVENT|RISK_ITEM|GOVERNANCE_DECISION|EVOLUTION_PLAN|CANDIDATE_ACTION|PATCH_PROPOSAL|VALIDATION_REPORT|REPOSITORY|SCHEMA|TEST|VALIDATOR|UNKNOWN",
  "label": "string",
  "status": "ACTIVE|SUPERSEDED|CORRECTION|INVALID|UNKNOWN",
  "source_ref": "string",
  "source_component": "string",
  "properties": {},
  "content_hash": "string"
}
```

### 8.2 Graph Edge Schema

Each graph edge must include:

```json
{
  "schema_version": "1.0",
  "edge_id": "string",
  "source_node_id": "string",
  "target_node_id": "string",
  "edge_type": "DEPENDS_ON|PRODUCES|CONSUMES|SUPPORTS|VALIDATES|SUPERSEDES|CORRECTS|REFERENCES|AFFECTS|GENERATED_BY|DERIVED_FROM|BLOCKED_BY|MITIGATES|EVIDENCED_BY|UNKNOWN",
  "status": "ACTIVE|SUPERSEDED|CORRECTION|INVALID|UNKNOWN",
  "source_ref": "string",
  "source_component": "string",
  "evidence_refs": [],
  "properties": {},
  "content_hash": "string"
}
```

Every non-`UNKNOWN` edge must include at least one evidence reference.

### 8.3 Graph Snapshot Schema

`graph_snapshot_latest.json` must include:

```json
{
  "schema_version": "1.0",
  "snapshot_id": "string",
  "timestamp": "string",
  "node_count": 0,
  "edge_count": 0,
  "nodes": [],
  "edges": [],
  "integrity_report": {},
  "warnings": [],
  "errors": []
}
```

### 8.4 Graph Query Result Schema

Each query result must include:

```json
{
  "schema_version": "1.0",
  "query_id": "string",
  "timestamp": "string",
  "query": {},
  "node_results": [],
  "edge_results": [],
  "result_count": 0,
  "warnings": [],
  "errors": []
}
```

### 8.5 Graph Manifest Schema

`graph_manifest_latest.json` must include:

```json
{
  "schema_version": "1.0",
  "manifest_id": "string",
  "timestamp": "string",
  "node_count": 0,
  "edge_count": 0,
  "node_types": [],
  "edge_types": [],
  "latest_snapshot": "string|null",
  "schema_versions": {},
  "warnings": [],
  "errors": []
}
```

### 8.6 Graph Integrity Schema

`graph_integrity_latest.json` must include:

```json
{
  "schema_version": "1.0",
  "integrity_id": "string",
  "timestamp": "string",
  "status": "PASS|FAIL|PARTIAL|BLOCKED",
  "checked_node_count": 0,
  "checked_edge_count": 0,
  "missing_endpoint_edges": [],
  "invalid_schema_records": [],
  "warnings": [],
  "errors": []
}
```

---

## 9. Deterministic Identity and Hashing Rules

### 9.1 Node IDs

Node IDs must be deterministic when built from existing artifacts.

Recommended format:

```text
graph-node::<node_type>::<stable-source-ref-hash>
```

Examples:

```text
graph-node::ARTIFACT::sha256(repo_scan_latest.json)
graph-node::COMPONENT::knowledge_graph
graph-node::SCHEMA::graph_node.schema.json
```

If IDs from source artifacts already exist, preserve them inside `properties.source_id`, but graph node IDs must still be unique in graph storage.

### 9.2 Edge IDs

Edge IDs must be deterministic.

Recommended format:

```text
graph-edge::<edge_type>::<source_node_id_hash>::<target_node_id_hash>::<evidence_hash>
```

### 9.3 Content Hash

`content_hash` must be computed from canonical serialized content excluding `content_hash` itself.

Rules:

```text
use SHA-256
use lowercase hex
sort JSON keys
use stable separators
exclude timestamps from content hash if timestamp is generated by graph layer
include source_ref, type, status, label, and properties
```

### 9.4 Deterministic Ordering

Always sort:

```text
nodes by node_id ascending
edges by edge_id ascending
node_types alphabetically
edge_types alphabetically
warnings alphabetically when possible
errors alphabetically when possible
```

Timestamps may differ by run. Graph structural content must remain stable for the same source artifacts.

---

## 10. Graph Storage Rules

### 10.1 Append-Only JSONL

These files are append-only:

```text
.agentx-init/graph/graph_nodes.jsonl
.agentx-init/graph/graph_edges.jsonl
```

Rules:

```text
one JSON object per line
append exactly one line per accepted node or edge
never rewrite previous lines
never reorder previous lines
never delete previous lines
never truncate existing file
malformed previous lines must be preserved
```

If a previous line is malformed:

```text
record warning
skip malformed line for active index construction
preserve the malformed line
append a correction/error event only if useful
never edit the malformed line
```

### 10.2 Regenerable Files

These files may be regenerated after validation passes:

```text
.agentx-init/graph/graph_index.json
.agentx-init/graph/graph_snapshot_latest.json
.agentx-init/graph/graph_manifest_latest.json
.agentx-init/graph/graph_integrity_latest.json
```

Rules:

```text
write to a temporary file first
validate generated object
replace latest file only after validation passes
if validation fails, preserve previous latest file
```

---

## 11. Ingestion Rules

PM3 must ingest existing artifacts as graph records.

The graph builder must be conservative. It must only create edges that can be supported by structured evidence.

### 11.1 Core Component Nodes

Always create component nodes for PM3-known components:

```text
Config / Paths
Audit Log
Repository Scanner
Layer Mapper
Architecture Analyzer
Governance Engine
Risk Engine
Evolution Planner
Patch Proposal Generator
Validation Runner
Memory Store
Report Writer
Knowledge Graph
CLI Commands
```

If a component has no runtime artifact yet, its node may still exist as a `COMPONENT` node with source_ref pointing to the component contract or known implementation file.

### 11.2 Artifact Nodes

Create artifact nodes for every existing known artifact under `.agentx-init/` relevant to PM1/PM2/PM3.

Examples:

```text
repo_scan_latest.json
architecture_latest.json
governance_latest.json
risk_latest.json
evolution_plan_latest.json
patch_proposal_latest.json
validation_report_latest.json
memory_snapshot_latest.json
audit_events.jsonl
graph_nodes.jsonl
graph_edges.jsonl
graph_snapshot_latest.json
```

### 11.3 Schema Nodes

Create schema nodes for graph schemas and, if available, core PM1/PM2 schemas:

```text
repo_scan.schema.json
architecture_report.schema.json
governance_decision.schema.json
risk_assessment.schema.json
evolution_plan.schema.json
patch_proposal.schema.json
validation_report.schema.json
memory_record.schema.json
graph_node.schema.json
graph_edge.schema.json
graph_snapshot.schema.json
graph_query_result.schema.json
graph_manifest.schema.json
graph_integrity.schema.json
```

### 11.4 Audit Event Nodes

When reading `audit_events.jsonl`, create one node per valid audit event.

Node type:

```text
AUDIT_EVENT
```

Node label:

```text
<event_type> — <status>
```

Source ref:

```text
.agentx-init/memory/audit_events.jsonl:<line_number>
```

Malformed audit lines must not crash graph generation.

### 11.5 Memory Record Nodes

When `memory_records.jsonl` exists, create one node per valid memory record.

Node type:

```text
MEMORY_RECORD
```

If full Memory Store is not present or the file is missing, emit a warning only.

### 11.6 Relationship Edges

Create these relationship types when evidence exists:

```text
Repository Scanner PRODUCES repo_scan_latest.json
Architecture Analyzer CONSUMES repo_scan_latest.json
Architecture Analyzer PRODUCES architecture_latest.json
Governance Engine CONSUMES architecture_latest.json
Governance Engine PRODUCES governance_latest.json
Risk Engine CONSUMES architecture_latest.json
Risk Engine PRODUCES risk_latest.json
Evolution Planner CONSUMES architecture_latest.json
Evolution Planner CONSUMES risk_latest.json
Evolution Planner CONSUMES governance_latest.json
Evolution Planner PRODUCES evolution_plan_latest.json
Patch Proposal Generator CONSUMES evolution_plan_latest.json
Patch Proposal Generator PRODUCES patch_proposal_latest.json
Validation Runner CONSUMES patch_proposal_latest.json
Validation Runner PRODUCES validation_report_latest.json
Report Writer CONSUMES structured artifacts
Report Writer PRODUCES markdown reports
Knowledge Graph CONSUMES PM1/PM2 artifacts
Knowledge Graph PRODUCES graph_snapshot_latest.json
Knowledge Graph PRODUCES graph_manifest_latest.json
schema file VALIDATES matching artifact type
runtime artifact GENERATED_BY source component
```

Every edge must reference at least one evidence source, such as an existing artifact path, schema path, audit event id, memory record id, or known component contract path.

---

## 12. Endpoint Integrity Rules

Every graph edge must reference existing node IDs.

Rules:

```text
source_node_id must exist
target_node_id must exist
edge must not be appended if either endpoint is missing
endpoint validation runs before append
integrity report lists missing endpoint edges
```

If an edge endpoint is missing:

```text
status = REJECTED
failure_class = MISSING_ENDPOINT_NODE
```

Rejected edges may be represented in warnings or integrity report, but must not be appended as valid edges.

---

## 13. Query Support

PM3 must support at least these query types:

```text
all
node_id
node_type
edge_type
outgoing
incoming
neighbors
source_component
artifact_path
```

### 13.1 CLI Query Options

`agentx-init graph` should support these options if the existing CLI pattern allows it:

```bash
agentx-init graph
agentx-init graph --build
agentx-init graph --query all
agentx-init graph --query node-type --value COMPONENT
agentx-init graph --query edge-type --value PRODUCES
agentx-init graph --query node-id --value <node_id>
agentx-init graph --query outgoing --value <node_id>
agentx-init graph --query incoming --value <node_id>
agentx-init graph --query neighbors --value <node_id>
agentx-init graph --format text
agentx-init graph --format json
```

If the current CLI framework is simpler, implement only:

```bash
agentx-init graph
agentx-init graph --json
```

and keep the deeper query options for tests/API.

### 13.2 Query Result Rules

Every query result must:

```text
be schema-valid
include query object
include node_results
include edge_results
include result_count
sort results deterministically
include warnings/errors when applicable
```

---

## 14. `agentx-init graph` Command Behavior

### 14.1 Purpose

The `graph` command builds and summarizes the Knowledge Graph.

It answers:

```text
What artifacts exist?
What produced them?
What consumes them?
What schemas validate them?
What evidence connects them?
What records depend on what?
What graph integrity issues exist?
```

### 14.2 Required Command Lifecycle

The command must execute this lifecycle:

```text
1. Parse graph command arguments.
2. Load config and path registry.
3. Ensure .agentx-init/graph/ exists.
4. Load existing graph nodes and edges if present.
5. Load PM1/PM2 runtime artifacts if present.
6. Build component, artifact, schema, audit, memory, and report nodes.
7. Build evidence-backed edges.
8. Validate nodes.
9. Validate edges and endpoints.
10. Append new valid nodes and edges, avoiding duplicate active records where possible.
11. Build graph index.
12. Build graph integrity report.
13. Build graph snapshot.
14. Build graph manifest.
15. Validate all generated graph outputs.
16. Write graph latest artifacts only after validation passes.
17. Append command history when available.
18. Append audit event.
19. Print summary.
20. Return exit code.
```

### 14.3 Command Output Summary

Text output should include:

```text
Graph build status
Node count
Edge count
Node types
Edge types
Snapshot path
Manifest path
Integrity status
Warnings count
Errors count
```

Example:

```text
Knowledge Graph: PASS
Nodes: 42
Edges: 67
Integrity: PASS
Snapshot: .agentx-init/graph/graph_snapshot_latest.json
Manifest: .agentx-init/graph/graph_manifest_latest.json
```

### 14.4 Exit Codes

Use existing CLI exit-code semantics if already implemented. Otherwise use:

```text
0 = SUCCESS / PASS
1 = FAILED
2 = INVALID command or arguments
3 = BLOCKED
4 = PARTIAL
5 = INTERNAL ERROR
```

`PARTIAL` is acceptable when optional PM2 artifacts are missing but graph generation completes from available evidence.

---

## 15. Validation Execution Order

Graph validation must execute in this order:

```text
1. Validate graph schema files exist.
2. Validate each GraphNode before append.
3. Validate each GraphEdge before append.
4. Verify edge endpoints exist.
5. Compute content hashes after canonical serialization.
6. Append valid graph nodes.
7. Append valid graph edges.
8. Build GraphIndex.
9. Validate GraphIndex if schema exists; otherwise validate by internal invariant checks.
10. Build GraphIntegrityReport.
11. Validate GraphIntegrityReport.
12. Build GraphSnapshot.
13. Validate GraphSnapshot.
14. Build GraphManifest.
15. Validate GraphManifest.
16. Write latest graph artifacts only after validation passes.
17. Append audit event.
```

If validation fails before writing latest artifacts:

```text
preserve previous latest graph files
return FAIL or BLOCKED
record error in audit event when possible
```

---

## 16. Failure Semantics

### 16.1 Graph Build Status

Allowed graph build statuses:

```text
PASS
PARTIAL
FAIL
BLOCKED
```

Meaning:

```text
PASS = graph built, validated, and persisted with no blocking errors
PARTIAL = graph built from available artifacts, but optional artifacts were missing or malformed
FAIL = graph build attempted but generated invalid output or write failed
BLOCKED = required graph schema/path/config boundary missing or unsafe
```

### 16.2 Common Failure Classes

Use these failure classes:

```text
MISSING_GRAPH_SCHEMA
INVALID_GRAPH_SCHEMA
MISSING_AGENTX_INIT
UNSAFE_GRAPH_PATH
INVALID_GRAPH_NODE
INVALID_GRAPH_EDGE
MISSING_ENDPOINT_NODE
GRAPH_INDEX_FAILED
GRAPH_SNAPSHOT_FAILED
GRAPH_MANIFEST_FAILED
GRAPH_INTEGRITY_FAILED
ARTIFACT_READ_ERROR
ARTIFACT_WRITE_ERROR
AUDIT_WRITE_ERROR
COMMAND_HISTORY_WRITE_ERROR
UNKNOWN_GRAPH_ERROR
```

### 16.3 Missing Source Artifacts

Missing optional source artifacts are warnings, not failures.

Examples:

```text
risk_latest.json missing -> warning
patch_proposal_latest.json missing -> warning
validation_report_latest.json missing -> warning
memory_snapshot_latest.json missing -> warning
```

Missing graph schema files are blocking failures.

---

## 17. Security and Safety Rules

PM3 must obey:

```text
no network access
no shell command execution
no dependency installation
no Git operations
no source mutation
no remote graph storage
no database server
no unsafe deserialization
no environment variable logging
no secret logging
no path traversal
no symlink escape outside repository/workspace boundary
```

Allowed imports:

```text
pathlib
json
datetime
dataclasses
typing
enum
uuid
hashlib
collections
```

Conditionally allowed:

```text
jsonschema, if already used or available
pydantic, if already used as project model standard
```

Forbidden imports:

```text
subprocess
requests
urllib
httpx
socket
git
networkx
neo4j
sqlite3 for graph storage
os.system
eval
exec
```

Do not add NetworkX just for graph operations. PM3 graph traversal must be simple local list/dict traversal.

---

## 18. Implementation Steps

### Step 1 — Inspect Existing PM1/PM2 Code

Check existing structure:

```bash
find agentx_initiator -maxdepth 4 -type f | sort
```

Look for:

```text
existing CLI registry pattern
existing schema validation helper
existing audit log writer
existing config/path registry
existing command response model
existing test style
```

Do not redesign working PM1/PM2 files.

### Step 2 — Add Graph Schemas

Create all required graph schemas.

Acceptance:

```text
schemas exist
schemas include required fields
valid fixtures pass
invalid fixtures fail
schema tests pass
```

### Step 3 — Add Graph Models

Create `graph_model.py` with dataclasses or project-standard models.

Acceptance:

```text
models serialize to dict
model field names match schemas
content hash helper works
minimal valid model validates
```

### Step 4 — Add Graph Index

Create `graph_index.py`.

Acceptance:

```text
index by node_id works
index by edge_id works
incoming/outgoing queries work
neighbors query works
ordering is deterministic
```

### Step 5 — Add KnowledgeGraph Core

Create `knowledge_graph.py`.

Acceptance:

```text
loads existing nodes/edges
preserves malformed JSONL lines
appends valid nodes/edges
rejects invalid nodes/edges
rejects edges with missing endpoints
builds snapshot
builds manifest
builds integrity report
writes only under .agentx-init/graph/
```

### Step 6 — Add Artifact Ingestion

Implement conservative ingestion from PM1/PM2 artifacts.

Acceptance:

```text
component nodes are created
artifact nodes are created for existing artifacts
schema nodes are created
basic producer/consumer edges are created
audit event nodes are created when audit_events.jsonl exists
missing optional artifacts produce warnings
unsupported relationships are not invented
```

### Step 7 — Add CLI Graph Command

Create or activate `agentx_initiator/cli/commands/graph.py`.

Acceptance:

```text
agentx-init graph runs
command builds graph artifacts
command prints summary
command returns correct exit code
command writes audit event
command does not invoke PM2/PM3 unrelated behavior beyond Knowledge Graph
```

### Step 8 — Add Tests

Create graph unit, schema, integration, and CLI tests.

Acceptance:

```text
all graph tests pass
existing PM1/PM2 tests still pass
no forbidden imports
no source writes outside allowed files during runtime tests
```

### Step 9 — Generate Completion Evidence

Create or update completion evidence under `.agentx-init/` or the project’s accepted completion-evidence location.

Required evidence fields:

```text
milestone_id
status
files_created_or_changed
schemas_created_or_changed
tests_created_or_changed
commands_run
artifacts_generated
deviations_from_spec
unresolved_risks
```

---

## 19. Required Tests

### 19.1 Schema Tests

Create tests:

```text
test_graph_node_schema_accepts_valid_node
test_graph_node_schema_rejects_missing_required_fields
test_graph_edge_schema_accepts_valid_edge
test_graph_edge_schema_rejects_missing_endpoint
test_graph_edge_schema_rejects_missing_evidence_for_non_unknown
test_graph_snapshot_schema_accepts_valid_snapshot
test_graph_query_result_schema_accepts_valid_result
test_graph_manifest_schema_accepts_valid_manifest
test_graph_integrity_schema_accepts_valid_report
test_completion_record_schema_accepts_valid_completion_record
```

### 19.2 Core Graph Tests

Create tests:

```text
test_add_node_appends_valid_node
test_add_node_rejects_invalid_node
test_add_edge_appends_valid_edge
test_add_edge_rejects_missing_source_endpoint
test_add_edge_rejects_missing_target_endpoint
test_non_unknown_edge_requires_evidence
test_malformed_existing_node_line_is_preserved
test_malformed_existing_edge_line_is_preserved
test_graph_index_is_deterministic
test_query_by_node_id
test_query_by_node_type
test_query_by_edge_type
test_query_outgoing_edges
test_query_incoming_edges
test_query_neighbors
test_snapshot_contains_nodes_edges_and_integrity
test_manifest_summarizes_node_and_edge_types
test_integrity_report_detects_missing_endpoint_edges
```

### 19.3 Ingestion Tests

Create tests:

```text
test_ingest_repo_scan_creates_artifact_node
test_ingest_architecture_report_creates_artifact_node
test_ingest_audit_events_creates_audit_event_nodes
test_missing_optional_pm2_artifact_is_warning_not_failure
test_known_component_nodes_are_created
test_schema_nodes_are_created
test_produces_edges_have_evidence_refs
test_consumes_edges_have_evidence_refs
```

### 19.4 CLI Tests

Create tests:

```text
test_cli_graph_builds_graph_artifacts
test_cli_graph_prints_summary
test_cli_graph_returns_zero_on_pass
test_cli_graph_returns_partial_when_optional_artifacts_missing
test_cli_graph_writes_audit_event
test_cli_graph_writes_only_agentx_init
test_cli_graph_does_not_mutate_source_files
test_cli_graph_json_output_if_supported
```

### 19.5 Regression Tests

Run existing PM1/PM2 tests.

At minimum:

```bash
python -m pytest
python -m py_compile agentx_initiator/**/*.py
python -m agentx_initiator.cli.main --help
python -m agentx_initiator.cli.main scan .
python -m agentx_initiator.cli.main status
python -m agentx_initiator.cli.main graph
```

If the CLI entrypoint differs, use the existing project command pattern.

---

## 20. Acceptance Criteria

PM3 is accepted only if all criteria below are met.

### 20.1 Functional Acceptance

```text
KnowledgeGraph can store nodes
KnowledgeGraph can store edges
KnowledgeGraph rejects edges with missing endpoints
KnowledgeGraph builds graph_index.json
KnowledgeGraph builds graph_snapshot_latest.json
KnowledgeGraph builds graph_manifest_latest.json
KnowledgeGraph builds graph_integrity_latest.json
KnowledgeGraph supports required query types
agentx-init graph runs successfully after PM1/PM2 artifacts exist
agentx-init graph handles missing optional PM2 artifacts as warnings
```

### 20.2 Schema Acceptance

```text
all graph schemas exist
all graph schemas have required metadata
valid graph artifacts validate
invalid graph artifacts fail validation
graph_node.schema.json accepts valid node
graph_edge.schema.json accepts valid edge
graph_snapshot.schema.json accepts valid snapshot
graph_query_result.schema.json accepts valid query result
graph_manifest.schema.json accepts valid manifest
graph_integrity.schema.json accepts valid integrity report
```

### 20.3 Safety Acceptance

```text
no graph runtime writes outside .agentx-init/
no source files are modified by running agentx-init graph
no network access
no shell execution
no graph database
no vector database
no semantic inference
no unsupported relationships emitted as facts
malformed JSONL history is preserved
append-only node/edge files are not rewritten
```

### 20.4 Integration Acceptance

```text
existing PM1 commands still work
existing PM2 commands still work
PM3 command history is recorded when command history exists
audit event is appended for graph command
graph artifacts can be regenerated deterministically
graph manifest points to latest snapshot
graph snapshot includes integrity report
graph query output is schema-valid
```

### 20.5 Test Acceptance

```text
all new graph tests pass
all existing tests pass
no forbidden imports appear in graph modules
py_compile passes
pytest passes
```

---

## 21. Stop Conditions

Stop implementation and return `BLOCKED` if any of these occur:

```text
PM1/PM2 runtime path registry cannot safely resolve .agentx-init/graph/
schema validation helper is missing and cannot be implemented locally without broad redesign
graph schemas conflict with existing schema standard
CLI registry cannot add graph command without breaking existing commands
Audit Log cannot append graph event and project requires audit event for all commands
Graph implementation would require source mutation at runtime
Graph implementation would require network, database server, or external graph library
Existing PM1/PM2 tests break because of graph integration
```

When blocked, produce a completion record with:

```text
status = BLOCKED
reason
files_changed
unresolved_risks
recommended_next_fix
```

---

## 22. Completion Evidence Package

At the end of PM3, produce a completion record.

Recommended path:

```text
.agentx-init/snapshots/pm3_completion_record.json
```

If the project has another completion-evidence convention, use that instead.

Minimum content:

```json
{
  "schema_version": "1.0",
  "completion_id": "string",
  "timestamp": "string",
  "milestone": "Product Milestone 3",
  "status": "VALIDATED|IMPLEMENTED_UNVALIDATED|NO_CHANGE|BLOCKED",
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "commands_run": [],
  "artifacts_generated": [],
  "acceptance_criteria_results": [],
  "deviations_from_spec": [],
  "unresolved_risks": [],
  "next_recommended_action": "string"
}
```

---

## 23. Final PM3 Definition of Done

Product Milestone 3 is done when:

```text
agentx-init graph
```

can:

```text
load existing PM1/PM2 artifacts
build local graph nodes
build local graph edges
enforce endpoint integrity
preserve evidence references
write graph_nodes.jsonl
write graph_edges.jsonl
write graph_index.json
write graph_snapshot_latest.json
write graph_manifest_latest.json
write graph_integrity_latest.json
append audit event
produce schema-valid graph query results
print a clear graph summary
pass graph schema tests
pass graph core tests
pass graph CLI tests
leave source files unchanged
avoid network, shell, database, and semantic inference behavior
```

PM3 is not done if:

```text
graph command only prints a placeholder
graph edges can reference missing nodes
graph schemas are missing
snapshot/manifest/integrity files are not generated
graph output is not schema-validated
graph writes outside .agentx-init/
graph behavior mutates source files
graph requires external graph database or network access
```

---

## 24. Implementation-Agent Final Instructions

When implementing this milestone:

1. Start with schemas.
2. Then implement models.
3. Then implement append-only storage.
4. Then implement index/snapshot/manifest/integrity.
5. Then implement artifact ingestion.
6. Then activate CLI graph.
7. Then write tests.
8. Then run the full test suite.
9. Then generate completion evidence.

Do not skip schema tests. Do not implement graph visualization. Do not use NetworkX or Neo4j. Do not infer relationships from prose. Do not mutate source files at runtime. Do not weaken PM1 or PM2 behavior.



---

## 25. PM3 Revision 2 Hardening Addendum

This section is part of the implementation contract. It closes the remaining gaps from the first PM3 implementation document and must be followed as if it appeared in the earlier sections.

### 25.1 Completeness Verdict for Previous PM3 Spec

The previous PM3 document is rated **9.4/10**.

It was strong and implementation-oriented, but not yet complete enough for a coding LLM to use with no other context because it left several points under-specified:

```text
artifact-to-node mapping was not fully explicit
artifact-to-edge mapping was not fully explicit
CLI argument behavior was not fully locked down
query output persistence rules were not fully defined
duplicate node and duplicate edge handling needed stricter rules
minimum JSON schema structure needed more implementation detail
missing-artifact status aggregation needed clearer rules
completion evidence validation needed stronger rules
rollback and recovery rules after failed graph builds needed stronger rules
PM3-to-PM1/PM2 non-regression obligations needed a stricter checklist
```

Revision 2 fixes those gaps. The updated rating is **10/10**.

---

## 26. Exact Artifact-to-Node Mapping Contract

The implementation agent must use this mapping when ingesting available PM1 and PM2 artifacts. Do not invent additional node types unless the schema and tests are updated in the same implementation pass.

| Input artifact | Node type | Node label | Required source_component | Required properties |
|---|---|---|---|---|
| `.agentx-init/snapshots/repo_scan_latest.json` | `ARTIFACT` | `repo_scan_latest.json` | `RepositoryScanner` | `path`, `artifact_type`, `status`, `scan_id` if present |
| repository root from repo scan | `REPOSITORY` | repository name or `repository` | `RepositoryScanner` | `repo_root`, `repository_hash` if present |
| file records from repo scan | `ARTIFACT` | relative file path | `RepositoryScanner` | `relative_path`, `sha256`, `detected_layer`, `is_protected` |
| directory records from repo scan | `ARTIFACT` | relative directory path | `RepositoryScanner` | `relative_path`, `detected_layer`, `is_protected` |
| test file records | `TEST` | relative test path | `RepositoryScanner` | `relative_path`, `detection_rule` |
| validator records | `VALIDATOR` | relative validator path | `RepositoryScanner` | `relative_path`, `detection_rule` |
| schema records or schema files | `SCHEMA` | schema filename | `RepositoryScanner` or `KnowledgeGraph` | `schema_path`, `owner_component` if known |
| `.agentx-init/snapshots/architecture_latest.json` | `ARTIFACT` | `architecture_latest.json` | `ArchitectureAnalyzer` | `analysis_id`, `source_scan_id`, `status` if present |
| architecture findings | `ARTIFACT` | finding title or finding id | `ArchitectureAnalyzer` | `finding_id`, `category`, `confidence` |
| `.agentx-init/snapshots/governance_latest.json` | `GOVERNANCE_DECISION` | governance decision id | `GovernanceEngine` | `decision`, `request_id`, `status` |
| `.agentx-init/snapshots/risk_latest.json` | `ARTIFACT` | `risk_latest.json` | `RiskEngine` | `assessment_id`, `overall_risk`, `status` |
| risk items | `RISK_ITEM` | risk title or risk id | `RiskEngine` | `risk_id`, `category`, `severity`, `confidence` |
| `.agentx-init/snapshots/evolution_plan_latest.json` | `EVOLUTION_PLAN` | evolution plan id | `EvolutionPlanner` | `plan_id`, `status` |
| candidate actions | `CANDIDATE_ACTION` | action title or action id | `EvolutionPlanner` | `action_id`, `priority`, `status`, `category` |
| `.agentx-init/snapshots/patch_proposal_latest.json` | `PATCH_PROPOSAL` | patch proposal id | `PatchProposalGenerator` | `proposal_id`, `status`, `category` |
| `.agentx-init/snapshots/validation_report_latest.json` | `VALIDATION_REPORT` | validation report id | `ValidationRunner` | `report_id`, `status` |
| memory records from `memory_records.jsonl` | `MEMORY_RECORD` | memory id | `MemoryStore` | `memory_id`, `category`, `status` |
| audit events from `audit_events.jsonl` | `AUDIT_EVENT` | event type or event id | `AuditLog` | `event_id`, `event_type`, `component`, `status` |
| markdown reports | `ARTIFACT` | report filename | `ReportWriter` | `path`, `artifact_type=markdown_report` |
| CLI command definitions | `COMMAND` if schema supports it, otherwise `COMPONENT` | command name | `CLICommands` | `command`, `category`, `requested_effect` |

If the schema does not support `REPORT` or `COMMAND` node types, map report files to `ARTIFACT` and command entries to `COMPONENT` or `UNKNOWN`, exactly as allowed earlier in this document.

---

## 27. Exact Edge Construction Matrix

Edges must be evidence-backed and deterministic. For each edge, `source_ref`, `source_component`, and `evidence_refs` must point to the artifact or record that justifies the relationship.

| Source node | Edge type | Target node | Evidence source |
|---|---|---|---|
| Repository node | `PRODUCES` or `CONTAINS` if supported, otherwise `REFERENCES` | file artifact nodes | repo scan file list |
| Repository node | `PRODUCES` or `REFERENCES` | directory artifact nodes | repo scan directory list |
| Repository Scanner component node | `PRODUCES` | repo scan artifact node | repo scan artifact metadata |
| repo scan artifact node | `EVIDENCED_BY` | audit event node for scan | audit event artifact refs |
| Architecture Analyzer component node | `CONSUMES` | repo scan artifact node | architecture report `source_scan_id` |
| Architecture Analyzer component node | `PRODUCES` | architecture report artifact node | architecture_latest metadata |
| architecture report artifact node | `SUPPORTS` | architecture finding nodes | finding evidence ids |
| Governance Engine component node | `CONSUMES` | architecture report or protected path artifact | governance evidence source |
| Governance Engine component node | `PRODUCES` | governance decision node | governance_latest metadata |
| Risk Engine component node | `CONSUMES` | architecture/governance/validation artifact nodes | risk input refs |
| Risk Engine component node | `PRODUCES` | risk assessment artifact node | risk_latest metadata |
| risk assessment artifact node | `AFFECTS` or `REFERENCES` | risk item nodes | risk item evidence ids |
| Evolution Planner component node | `CONSUMES` | architecture/risk/governance/validation artifacts | evolution plan input refs |
| Evolution Planner component node | `PRODUCES` | evolution plan node | evolution_plan_latest metadata |
| evolution plan node | `PRODUCES` or `REFERENCES` | candidate action nodes | candidate action ids |
| Patch Proposal Generator component node | `CONSUMES` | candidate action or evolution plan node | patch proposal input refs |
| Patch Proposal Generator component node | `PRODUCES` | patch proposal node | patch_proposal_latest metadata |
| Validation Runner component node | `PRODUCES` | validation report node | validation_report_latest metadata |
| Validation report node | `VALIDATES` | artifact nodes named in validation input refs | validation input refs |
| Memory Store component node | `PRODUCES` | memory record nodes | memory_records.jsonl |
| Audit Log component node | `PRODUCES` | audit event nodes | audit_events.jsonl |
| Report Writer component node | `PRODUCES` | report artifact nodes | report bundle or report path |
| schema nodes | `VALIDATES` or `USES_SCHEMA` if supported | artifacts governed by that schema | schema filename and artifact type mapping |

If an edge type such as `CONTAINS` or `USES_SCHEMA` is not in the implemented frozen schema enum, use `REFERENCES`, `PRODUCES`, `CONSUMES`, `VALIDATES`, `EVIDENCED_BY`, or `UNKNOWN`. Do not expand enums without updating schemas and tests.

---

## 28. Duplicate Handling Rules

Graph ingestion must be idempotent enough for repeated `agentx-init graph` runs.

### 28.1 Node Duplicate Rule

A node is considered the same logical node when these fields match:

```text
node_type
source_ref
source_component
content_hash
```

If the same logical node already exists as `ACTIVE`, do not append another identical active node.

If the same `source_ref` has changed content hash, append a new node with a new node id and leave the old node unchanged. If the old node is to be superseded, append a `SUPERSEDES` edge if evidence exists. Do not rewrite the old JSONL line.

### 28.2 Edge Duplicate Rule

An edge is considered the same logical edge when these fields match:

```text
source_node_id
target_node_id
edge_type
source_ref
content_hash
```

If the same logical edge already exists as `ACTIVE`, do not append a duplicate active edge.

### 28.3 Malformed Historical Lines

Malformed historical lines in `graph_nodes.jsonl` or `graph_edges.jsonl` must be preserved. They may be reported in `graph_integrity_latest.json`, but must not be deleted, rewritten, or moved.

---

## 29. CLI Argument Contract for `agentx-init graph`

The graph command must work with no arguments:

```bash
agentx-init graph
```

Default behavior:

```text
build or refresh graph from available PM1/PM2 artifacts
write graph artifacts
print text summary
return PASS, PARTIAL, FAIL, or BLOCKED through exit code
```

Optional arguments may be implemented only if they fit the existing CLI style:

```text
--json                 print schema-valid graph command response or summary JSON
--query-node NODE_ID   return graph query result for one node id
--node-type TYPE       query nodes by node type
--edge-type TYPE       query edges by edge type
--incoming NODE_ID     query incoming edges for one node
--outgoing NODE_ID     query outgoing edges for one node
--neighbors NODE_ID    query neighboring nodes
--no-ingest            build reports from existing graph JSONL only, if useful for tests
```

If optional arguments are not implemented in PM3, they must not be advertised in help output.

Invalid graph arguments must return:

```text
status = INVALID
failure_class = INVALID_COMMAND_REQUEST
exit_code = 2
```

The graph command must not call `scan`, `status`, `plan`, `propose`, or `validate` internally. It may read their already-existing artifacts only.

---

## 30. Query Result Persistence and Output Rules

Graph query results must be schema-valid when returned.

Minimum behavior:

```text
query results are returned to terminal or command response
query results do not have to be persisted by default
```

Optional persistence path, if implemented:

```text
.agentx-init/graph/graph_query_result_latest.json
```

If query result persistence is implemented, it must validate against:

```text
agentx_initiator/schemas/graph_query_result.schema.json
```

Query ordering must be deterministic:

```text
nodes sorted by node_id ascending
edges sorted by edge_id ascending
```

---

## 31. Status Aggregation Rules

Graph command status must be computed deterministically.

```text
schema path unsafe or missing required graph schema -> BLOCKED
required graph directory cannot be created safely -> BLOCKED
all available artifacts malformed or unreadable -> BLOCKED or FAIL
node/edge schema validation failure before write -> FAIL
edge endpoint integrity failure in generated edges -> FAIL
write failure for required graph latest artifact -> FAIL
audit write failure -> FAIL unless existing project treats audit failure as warning
only optional PM2 artifacts missing -> PARTIAL
some optional artifact malformed but graph built from valid artifacts -> PARTIAL
valid graph built from minimum PM1 artifacts -> PASS or PARTIAL depending on missing optional warnings
valid graph built from PM1+PM2 artifacts without errors -> PASS
```

If a previous valid graph snapshot exists and the new graph build fails before latest artifact write, preserve the previous latest graph artifacts.

---

## 32. Minimum JSON Schema Implementation Requirements

The implementation agent must create real JSON Schema files, not prose placeholders.

Each graph schema must include at minimum:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [],
  "properties": {},
  "additionalProperties": false
}
```

Each schema must define:

```text
required fields listed in this document
enum values for node_type, edge_type, status, and graph statuses
array item types for nodes, edges, evidence_refs, warnings, errors
object type for properties and query fields
string pattern or minimum length for ids where practical
content_hash as string
```

If the existing project uses a different JSON Schema draft, follow the existing project standard, but preserve field requirements.

---

## 33. Allowed Imports and Dependency Limits

Allowed imports for PM3 graph modules:

```text
pathlib
json
datetime
dataclasses
typing
enum
uuid
hashlib
collections
```

Allowed local imports:

```text
agentx_initiator.core.config
agentx_initiator.core.path_registry
agentx_initiator.core.audit_log
agentx_initiator.cli.models if needed
```

Conditionally allowed if already used by the project:

```text
jsonschema
pydantic
```

Forbidden imports:

```text
subprocess
requests
urllib
httpx
socket
git
networkx
neo4j
numpy
pandas
sklearn
faiss
eval
exec
```

Do not add a graph database or external graph algorithm dependency.

---

## 34. Recovery and Rollback Rules

PM3 implementation must be recoverable.

During development, if the graph build fails:

```text
do not delete previous graph JSONL history
do not overwrite previous latest snapshot with invalid output
do not rewrite PM1/PM2 artifacts
do not weaken existing tests to pass PM3
record failure in completion evidence
```

If a file rename or import update breaks PM1/PM2 behavior, revert that change or return `BLOCKED` with exact failure details.

PM3 should add graph behavior, not destabilize the foundation.

---

## 35. PM3 Non-Regression Checklist

Before PM3 is marked done, verify:

```text
agentx-init --help still works
agentx-init scan still works
agentx-init status still works
PM2 commands still either work or retain their documented blocked/implemented status
existing schema tests still pass
existing audit append behavior still passes
existing command history behavior still passes if present
runtime writes remain under .agentx-init/
source files are not modified by runtime commands
```

PM3 completion is invalid if graph implementation requires weakening PM1 or PM2 acceptance criteria.

---

## 36. Final Single-Document Implementation Rule

An LLM implementation agent must be able to complete PM3 from this document alone by following this order:

```text
1. Read this full document.
2. Inspect the repository only to discover existing implementation style.
3. Implement graph schemas.
4. Implement graph models.
5. Implement graph storage and idempotent append behavior.
6. Implement graph index/query/snapshot/manifest/integrity.
7. Implement conservative PM1/PM2 artifact ingestion using the mapping tables above.
8. Implement or activate the graph CLI command.
9. Add schema, unit, integration, ingestion, CLI, and regression tests.
10. Run full validation.
11. Produce completion evidence.
```

No additional architecture interpretation is required. If a required decision is not covered by this document, choose the most conservative option that preserves PM1/PM2 behavior, schema validity, append-only history, and `.agentx-init/` write boundaries.

---

## 37. Revision 3 Final Completeness Hardening

This section closes the remaining implementation-hand-off gaps. If any item here conflicts with an earlier section, this section is the more specific PM3 rule.

### 37.1 PM3 Starting-State Checklist

Before writing code, the implementation agent must inspect the repository and classify the starting state as one of:

```text
READY_FOR_PM3
PARTIAL_PM2_AVAILABLE
PM1_ONLY_AVAILABLE
BLOCKED_BASELINE_BROKEN
```

Use this interpretation:

```text
READY_FOR_PM3 = PM1 and PM2 artifacts/modules exist enough for graph integration.
PARTIAL_PM2_AVAILABLE = some PM2 artifacts exist, but graph can still build a partial graph.
PM1_ONLY_AVAILABLE = scan/status/audit artifacts exist, but governance/risk/planning/proposal/validation/memory may be absent.
BLOCKED_BASELINE_BROKEN = the CLI cannot import, PM1 scan/status is broken, or .agentx-init write boundary cannot be enforced.
```

If the starting state is `BLOCKED_BASELINE_BROKEN`, do not implement graph behavior yet. Produce a completion record with status `BLOCKED` and list the missing prerequisite.

### 37.2 PM3 Must Not Repair PM1 or PM2 Broadly

PM3 may make narrow compatibility edits required to register and run `agentx-init graph`.

PM3 must not redesign or rewrite:

```text
Config / Paths
Audit Log
Repository Scanner
Architecture Analyzer
Governance Engine
Risk Engine
Evolution Planner
Patch Proposal Generator
Validation Runner
Memory Store
Report Writer
```

If one of those components is malformed, PM3 must consume whatever schema-valid artifacts are available and record warnings for the rest.

### 37.3 Blocked Stub Replacement Rule

If `agentx-init graph` exists as a PM1/PM2 blocked stub, PM3 must replace the stub with the real graph command.

The implementation must remove or bypass only the graph-specific blocked reason:

```text
COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1
```

Other later or unrelated command stubs must remain unchanged.

### 37.4 Required CLI Exit Codes

`agentx-init graph` must return deterministic exit codes:

```text
0 = PASS, graph built or queried successfully
1 = FAIL, implementation/runtime error after execution started
2 = INVALID, invalid arguments or invalid query request
3 = BLOCKED, required baseline cannot be used safely
4 = PARTIAL, graph built with missing optional artifacts or malformed skipped records
5 = INTERNAL_ERROR, unexpected exception caught and reported
```

The command response status, terminal message, audit event, and completion evidence must agree with the exit code.

### 37.5 Required CLI Modes

The graph command must support these minimum modes:

```bash
agentx-init graph
agentx-init graph build
agentx-init graph status
agentx-init graph query --node-id <id>
agentx-init graph query --node-type <type>
agentx-init graph query --edge-type <type>
agentx-init graph query --outgoing <node_id>
agentx-init graph query --incoming <node_id>
```

Allowed optional flags:

```bash
--output-format text|json
--rebuild-index
--strict
```

Default behavior:

```text
agentx-init graph = build graph from available artifacts, write latest graph artifacts, print short status.
```

`--strict` means missing recommended PM2 artifacts may upgrade the result from `PARTIAL` to `BLOCKED`, but missing optional artifacts must never be treated as success without warning.

### 37.6 Artifact Discovery Manifest

PM3 must create a deterministic artifact discovery list before graph construction.

The discovery list must include, for each candidate artifact:

```json
{
  "artifact_path": "string",
  "artifact_type": "string",
  "required_for_pm3_minimum": false,
  "exists": false,
  "valid_json": false,
  "schema_valid_if_checked": false,
  "consumed": false,
  "warning": "string|null"
}
```

This discovery list may be embedded inside `graph_manifest_latest.json` under `artifact_discovery` or written as:

```text
.agentx-init/graph/graph_artifact_discovery_latest.json
```

If written separately, it must still remain under `.agentx-init/graph/`.

### 37.7 Minimum Graph Build From PM1 Only

Even if PM2 is absent, PM3 must build a useful graph from PM1 artifacts when possible.

Minimum PM1-only graph nodes:

```text
REPOSITORY node from repo_scan_latest.json
ARTIFACT node for repo_scan_latest.json
ARTIFACT node for architecture_latest.json if present
AUDIT_EVENT nodes from audit_events.jsonl valid lines
SCHEMA nodes for graph schema files
COMPONENT nodes for Repository Scanner, Architecture Analyzer, Audit Log, Config / Paths, Layer Mapper, CLI graph
```

Minimum PM1-only graph edges:

```text
Repository Scanner PRODUCES repo_scan_latest.json
Architecture Analyzer PRODUCES architecture_latest.json when present
Audit Log PRODUCES audit_events.jsonl
repo_scan_latest.json EVIDENCED_BY audit event when matching evidence exists
architecture_latest.json DERIVED_FROM repo_scan_latest.json when source_scan_id or source ref exists
CLI graph PRODUCES graph_snapshot_latest.json
```

A PM1-only graph should normally be `PARTIAL`, not `FAIL`, unless required baseline artifacts are invalid or missing.

### 37.8 Schema Validation Practical Rule

Every graph schema must include at minimum:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [],
  "properties": {}
}
```

The required fields listed earlier in this document must be present in each schema’s `required` list. Enum fields must use the exact enum values defined in this document.

If the project already uses a different JSON Schema draft consistently, preserve project consistency, but do not weaken required fields, enums, or validation failure behavior.

### 37.9 Deterministic Ordering Contract

All graph artifacts must use deterministic ordering:

```text
nodes sorted by node_id ascending
edges sorted by edge_id ascending
query node results sorted by node_id ascending
query edge results sorted by edge_id ascending
manifest artifact lists sorted by artifact_path ascending
warnings sorted by stable warning code then artifact path
errors sorted by stable error code then artifact path
```

Timestamps and generated UUIDs may differ across runs, but content-derived IDs and sorted output order must remain stable for the same inputs.

### 37.10 Malformed JSONL Handling

For JSONL inputs such as audit, memory, validation history, proposal history, and planning history:

```text
valid lines must be consumed
malformed lines must be preserved
malformed lines must produce warnings
malformed lines must not crash the whole graph build unless --strict is used
line numbers must be reported in warnings
```

Malformed input lines must not be rewritten or deleted.

### 37.11 Required Test Fixtures

PM3 tests must include these fixtures:

```text
fixture_pm1_minimal_repo_state
fixture_pm2_full_artifact_state
fixture_missing_optional_pm2_artifacts
fixture_malformed_jsonl_lines
fixture_duplicate_artifacts
fixture_missing_edge_endpoint
fixture_invalid_graph_schema_record
```

Each fixture must be local and must not require network access.

### 37.12 Required Non-Regression Tests

The PM3 implementation is incomplete unless these existing behaviors still pass:

```text
agentx-init --help
agentx-init scan <fixture_repo>
agentx-init status
existing PM1 schema tests
existing PM1 audit append-only tests
existing PM2 governance/risk/planning/proposal/validation/memory tests if present
```

If PM2 tests are not present in the repository, PM3 must not invent PM2 behavior just to satisfy graph tests.

### 37.13 Graph Completion Record

At the end of PM3, write or produce a completion record containing:

```yaml
completion_record:
  product_milestone: "PM3"
  component: "Knowledge Graph and graph CLI"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|PARTIAL|BLOCKED|FAILED"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  graph_artifacts_generated: []
  source_artifacts_consumed: []
  warnings: []
  errors: []
  deviations_from_pm3_spec: []
  non_regression_result: "PASS|FAIL|NOT_RUN"
```

Preferred output path:

```text
.agentx-init/snapshots/pm3_completion_record_latest.json
```

If the shared completion record system already has a canonical path, use that instead and record the chosen path in the terminal output.

### 37.14 Documentation Update Requirement

PM3 must update project documentation only as needed to expose the graph command and graph artifacts.

Allowed documentation updates:

```text
README command list
CLI documentation
schema inventory documentation
milestone status documentation
```

Forbidden documentation updates:

```text
rewriting frozen component contracts
rewriting milestone definitions
silently changing PM1 or PM2 scope
claiming graph visualization or semantic reasoning exists
```

### 37.15 Final PM3 Acceptance Gate

PM3 is accepted only when all are true:

```text
[ ] graph core files exist
[ ] graph CLI command exists and is registered
[ ] graph schemas exist and validate valid samples
[ ] invalid graph node sample fails schema validation
[ ] invalid graph edge sample fails schema validation
[ ] missing endpoint edge is rejected
[ ] graph can build from PM1-only artifacts with PARTIAL or PASS status
[ ] graph can build from full PM2 artifacts with PASS or PARTIAL status
[ ] graph index is deterministic
[ ] graph snapshot is deterministic except timestamp/id fields
[ ] graph manifest lists consumed and missing artifacts
[ ] graph query by node_id works
[ ] graph query by node_type works
[ ] graph query by edge_type works
[ ] graph query incoming/outgoing works
[ ] malformed JSONL input is warned about, not rewritten
[ ] duplicate nodes/edges are handled deterministically
[ ] audit event is appended for graph build/query
[ ] no writes occur outside .agentx-init/
[ ] no source files are changed by runtime graph command
[ ] no forbidden imports are introduced
[ ] no NetworkX/Neo4j/vector/embedding dependency is required
[ ] PM1 and PM2 non-regression checks pass or are explicitly recorded as not available
[ ] completion record exists
```

### 37.16 Final Rating After Revision 3

With this hardening section included, this PM3 document is complete as a single-document implementation handoff.

Final target rating:

```text
10/10
```
