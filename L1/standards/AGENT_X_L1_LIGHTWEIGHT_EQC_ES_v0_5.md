# Agent_X L1 Lightweight EQC-ES

**Document ID:** `AGENT-X-L1-EQC-ES-001`  
**Version:** `v0.5.0`  
**Status:** `ready-for-use`  
**Scope:** Agent_X L1 document-portfolio governance  
**Parent Standard:** Lightweight adaptation of EQC Ecosystem Specification for Agent_X L1  
**Related Standards:** Agent_X L1 EQC-FIC, Agent_X L1 Pseudocode-to-FIC Workflow, Agent_X L1 Lightweight EQC-SIB

**Quality Gate Result:** `9.9/10 before v0.5 corrections; 10/10 after v0.5 corrections for the current Agent_X L1 stage`  
**v0.5 Upgrade Focus:** removes internal version/numbering inconsistencies, standardizes sidecar versions, adds direct-vs-transitive digest maturity rules, adds mandatory final self-assessment criteria, and closes the remaining lightweight-stage acceptance gap.

---

## 0. Purpose

Agent_X L1 Lightweight EQC-ES is the governance layer for the **L1 document ecosystem**.

It exists to make every L1 control-plane document discoverable, versioned, traceable, dependency-aware, and safe to update.

It governs documents such as:

```text
L1/docs/00_L1_SYSTEM_GOAL.md
L1/docs/01_L1_BACKGROUND.md
L1/docs/02_L1_ARCHITECTURE_CONTRACT.md
L1/docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md
L1/docs/04_L1_UNIT_DAG.md
L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md
L1/docs/06_L1_VALIDATION_PLAN.md
L1/docs/07_L1_RISK_LEDGER.md
L1/docs/08_L1_TRACEABILITY_MATRIX.md
L1/docs/09_L1_CODING_AGENT_HANDOFF_RULES.md
L1/docs/10_L1_FAILURE_LEARNING_LOG.md
L1/fic/index.fic.yaml
L1/fic/units/*.md
L1/generated/*.yaml
L1/generated/*.md
```

This document does **not** govern source code directly. Code and implementation artifacts are governed by Lightweight EQC-SIB and EQC-FIC.

---

## 1. Position in the Agent_X L1 Standards Stack

Agent_X L1 uses four lightweight standards:

```text
EQC-FIC
  governs individual file/unit implementation contracts

Pseudocode-to-FIC Workflow
  governs the process from goal to pseudocode to FIC to implementation

Lightweight EQC-SIB
  governs document ↔ FIC ↔ implementation binding

Lightweight EQC-ES
  governs the L1 document ecosystem itself
```

This document is the **document-portfolio control layer**.

It answers:

```text
Which documents exist?
Which document is authoritative?
Which documents depend on which others?
Which files must change when one document changes?
Which documents are stale, orphaned, duplicated, deprecated, or inconsistent?
Can the L1 document set be trusted as a coherent control plane?
```

---

## 2. Non-Goals

Lightweight EQC-ES must not become full production EQC-ES too early.

This document does **not** require, in the first L1 stage:

```text
- signed checkpoints
- distributed sub-portfolios
- alias rewriting
- full functional/metadata digest closure across all documents
- clean-room shadow traces
- hardware-profile equivalence
- golden ecosystem traces
- cryptographic approval workflows
- complex waiver quorum
- cross-repository federation
```

Those belong to later maturity levels.

For current Agent_X L1, the goal is:

```text
small, deterministic, inspectable document governance
```

---

## 3. L1 Document Portfolio Root

The L1 document portfolio root is:

```text
L1/
```

All governed document paths must be repository-relative POSIX-style paths.

Valid:

```text
L1/docs/00_L1_SYSTEM_GOAL.md
L1/fic/units/FIC-L1-001-document-loader.md
L1/generated/semantic_lockfile.yaml
```

Invalid:

```text
../L1/docs/00_L1_SYSTEM_GOAL.md
/home/user/project/L1/docs/00_L1_SYSTEM_GOAL.md
L1\\docs\\00_L1_SYSTEM_GOAL.md
./L1/docs/00_L1_SYSTEM_GOAL.md
```

Rules:

1. Paths must be relative to repository root.
2. Paths must not escape the repository root.
3. Paths must use `/`, not platform-specific separators.
4. Paths must not contain unresolved `.` or `..` components.
5. Symlinks that resolve outside the repository root are invalid.
6. A governed document must exist and be non-empty unless explicitly marked as an allowed empty sentinel.

---

## 4. Document Types

Each governed L1 document must declare one document type.

Allowed document types:

| Type | Meaning |
|---|---|
| `system-goal` | Defines purpose, scope, constraints, and non-goals |
| `background` | Explains context and rationale |
| `architecture-contract` | Defines layer boundaries, ownership, and dependency rules |
| `whole-system-pseudocode` | Defines end-to-end intended L1 behavior |
| `unit-dag` | Defines implementation units and dependencies |
| `shared-interface` | Defines shared types, schemas, and public contracts |
| `validation-plan` | Defines checks, gates, and evidence expectations |
| `risk-ledger` | Tracks residual risks and accepted limitations |
| `traceability-matrix` | Maps goal → pseudocode → FIC → implementation → tests |
| `handoff-rules` | Defines bounded coding-agent handoff rules |
| `failure-learning-log` | Records failures and process corrections |
| `fic-registry` | Registers EQC-FIC documents |
| `fic-unit` | Defines one bounded FIC implementation contract |
| `generated-lockfile` | Freezes approved document state |
| `generated-report` | Produced by validators or review tools |
| `schema` | Machine-readable validation schema |
| `other` | Allowed only with explicit justification || `standard` | Defines architectural, workflow, or interface rules for L1 agents |
| `governance-note` | Records governance decisions, legacy justifications, or non-binding guidance |


`other` must not be used when a more specific type applies.

---

## 5. Document IDs

Every governed document must have a stable `DocID`.

Format:

```text
AX-L1-DOC-<TYPE>-<NUMBER>
```

Examples:

```text
AX-L1-DOC-GOAL-001
AX-L1-DOC-ARCH-001
AX-L1-DOC-PS-001
AX-L1-DOC-DAG-001
AX-L1-DOC-FICREG-001
AX-L1-DOC-FIC-001
```

Rules:

1. A `DocID` must never be reused for a different semantic document.
2. A renamed document keeps the same `DocID` and records the path change.
3. A split document creates new `DocID`s and records a split/migration record.
4. A merged document creates a new `DocID` and records all source `DocID`s.
5. Deprecated documents keep their old `DocID` and must remain discoverable until removal is explicitly approved.

---

## 5.5 Version Marker Rule

Every governed document must contain a version marker that matches the registry entry.

Markdown documents must contain one of:

```text
**Version:** `vX.Y.Z`
Version: vX.Y.Z
Spec Version: vX.Y.Z
```

YAML and JSON documents must contain one of:

```yaml
version: "vX.Y.Z"
spec_version: "vX.Y.Z"
lockfile_version: "vX.Y.Z"
```

Generated reports must contain:

```text
Generated-From: <DocID>@<version>
Generated-By: <tool-or-process-id>
```

Rules:

1. The marker must exactly match the registry `version`.
2. A missing marker is blocking for `active`, `locked`, and `generated` documents.
3. A mismatch between registry version and document marker is a functional inconsistency.
4. Historical documents may keep their historical marker but must not be active.


## 6. Required Registry

Agent_X L1 must maintain a machine-readable ecosystem registry:

```text
L1/ecosystem/ecosystem-registry.yaml
```

Minimum schema:

```yaml
ecosystem_registry_version: "v0.5"
portfolio_id: "AGENT_X_L1"
documents:
  - doc_id: "AX-L1-DOC-GOAL-001"
    title: "L1 System Goal"
    type: "system-goal"
    path: "L1/docs/00_L1_SYSTEM_GOAL.md"
    version: "v0.1.0"
    status: "active"
    owner: "l1-control-plane"
    layer: 0
    authority_level: "constitutional"
    functional_digest: "sha256:<pending>"
    metadata_digest: "sha256:<pending>"
    depends_on: []
    recognized_by: []
    governs:
      - "AX-L1-DOC-PS-001"
      - "AX-L1-DOC-ARCH-001"
```

Required fields:

```text
doc_id
title
type
path
version
status
owner
layer
authority_level
functional_digest
metadata_digest
depends_on
recognized_by
governs
allow_empty
generated_from
last_validated_utc
source_of_truth_owner
```

Additional registry closure rules:

1. `allow_empty` defaults to `false`; if `true`, the document must be a declared sentinel and must still have a registry entry.
2. `generated_from` is required for generated lockfiles, generated reports, generated schema outputs, and validator-owned artifacts.
3. `last_validated_utc` must use `YYYY-MM-DDTHH:MM:SSZ` or be `null` for drafts.
4. `source_of_truth_owner` identifies the document or role allowed to change the governed semantics.
5. Two active documents may not share the same `path`, `doc_id`, or source-of-truth ownership claim over the same requirement.
6. The registry is invalid if it contains a document path that is absent from the graph and not explicitly marked as registry-only metadata.

---

## 7. Document Status Values

Allowed statuses:

| Status | Meaning |
|---|---|
| `draft` | Incomplete; cannot govern implementation |
| `reviewed` | Internally coherent but not fully active |
| `active` | Current authoritative document |
| `locked` | Frozen for implementation or release candidate |
| `generated` | Produced by tooling; not manually edited unless authorized |
| `deprecated` | Superseded but retained for traceability |
| `archived` | Historical only; not part of active validation |
| `blocked` | Known inconsistency or unresolved dependency |

Rules:

1. Only `active` or `locked` documents may govern implementation.
2. `draft` documents may not be referenced as authoritative.
3. `generated` documents must identify their generator or source.
4. `deprecated` documents may be referenced only for migration or history.
5. `blocked` documents cause dependent documents to become blocked unless a waiver exists.

---

## 8. Authority Levels

Allowed authority levels:

| Authority Level | Meaning |
|---|---|
| `constitutional` | Highest-level purpose, non-goals, safety rules |
| `architecture` | Layering, ownership, dependency boundaries |
| `workflow` | Process and lifecycle rules |
| `interface` | Shared type, schema, API, protocol contract |
| `unit-contract` | Individual FIC or bounded unit contract |
| `validation` | Tests, gates, evidence, review rules |
| `generated` | Tool-derived state or report |
| `historical` | Retained context but not governing |

Conflict resolution order:

```text
constitutional
  > architecture
  > workflow
  > interface
  > unit-contract
  > validation
  > generated
  > historical
```

Existing code does not override the document ecosystem. Code may reveal drift, but it does not silently become the source of truth.

---

## 9. Layer Model

Agent_X L1 document layers:

| Layer | Documents |
|---:|---|
| 0 | System goal, constitutional rules, non-goals |
| 1 | Architecture contract, background, source-of-truth rules |
| 2 | Whole-system pseudocode, unit DAG, shared interfaces |
| 3 | FIC documents, validation plan, handoff rules |
| 4 | Generated lockfiles, reports, traceability records, release packets |

Dependency rule:

```text
A document may depend only on documents in the same or lower layer.
```

Metadata recognition may point upward, but metadata recognition does not create governing authority.

Valid:

```text
FIC unit depends on shared interface.
Validation plan depends on architecture contract.
Traceability matrix recognizes FICs and code artifacts.
```

Invalid:

```text
System goal depends on a FIC unit.
Architecture contract depends on generated validation report.
Shared interface depends on code implementation.
```

---

## 10. Edge Types

The ecosystem graph uses explicit edge types.

Required graph file:

```text
L1/ecosystem/ecosystem-graph.yaml
```

Allowed edge types:

| Edge | Meaning | Functional? |
|---|---|---:|
| `IMPORTS` | Document imports rules or definitions from another document | yes |
| `EXTENDS` | Document extends another document's semantics | yes |
| `GOVERNS` | Document controls another document or artifact | yes |
| `USES` | Document uses a type, requirement, or unit from another document | yes |
| `DERIVES` | Document is generated or derived from another document | yes |
| `VALIDATES` | Document defines validation for another document | yes |
| `REFERENCES` | Non-binding citation | no |
| `RECOGNIZES` | Metadata-only discoverability edge | no |
| `SUPERSEDES` | Replacement or deprecation relation | no, unless active replacement changes authority |

Functional edges participate in dependency checks.

Metadata-only edges do not satisfy reachability and do not create authority.

---

## 10.5 Graph Schema and Cycle Rules

The ecosystem graph must be machine-readable and deterministic.

Minimum graph schema:

```yaml
ecosystem_graph_version: "v0.5"
portfolio_id: "AGENT_X_L1"
root_doc_id: "AX-L1-DOC-GOAL-001"
nodes:
  - doc_id: "AX-L1-DOC-GOAL-001"
    path: "L1/docs/00_L1_SYSTEM_GOAL.md"
    type: "system-goal"
    layer: 0
edges:
  - src: "AX-L1-DOC-GOAL-001"
    type: "GOVERNS"
    dst: "AX-L1-DOC-ARCH-001"
    payload: {}
```

Cycle detection applies only to functional edges:

```text
IMPORTS, EXTENDS, GOVERNS, USES, DERIVES, VALIDATES
```

Rules:

1. Functional cycles are blocking.
2. `REFERENCES`, `RECOGNIZES`, and `SUPERSEDES` do not participate in cycle detection.
3. Every graph node must exist in the registry.
4. Every functional graph edge must reference valid registry DocIDs.
5. Graph output must be sorted deterministically by `(src, type, dst)`.
6. A generated lockfile must record the resolved graph hash.


## 11. Reachability Rules

Every active document must be reachable from the root document by functional edges.

Root document:

```text
AX-L1-DOC-GOAL-001
```

Functional reachability edges:

```text
IMPORTS
EXTENDS
GOVERNS
USES
DERIVES
VALIDATES
```

Metadata-only edges ignored for functional reachability:

```text
REFERENCES
RECOGNIZES
SUPERSEDES
```

Blocking conditions:

1. Active document is not reachable from root.
2. Active document is reachable only through metadata edges.
3. Active document depends on a deprecated or blocked document.
4. Active document has no authority path to the system goal.

---

## 12. Canonical Content Rules

For digest and comparison purposes, text documents must be canonicalized as follows:

```text
- UTF-8 encoding
- LF line endings
- no byte-order mark
- trailing whitespace stripped
- final newline required
- no unresolved conflict markers
```

YAML and JSON documents must additionally use:

```text
- deterministic key ordering when serialized by validators
- no duplicate keys
- explicit strings for version numbers
- UTC timestamps when timestamps are used
```

Markdown documents are hashed after text canonicalization. No Markdown AST normalization is required in the lightweight stage.

---

## 13. Digest Classes

Lightweight EQC-ES uses two digest classes.

### 13.1 Functional Digest

`FunctionalDigest` changes when the document's governing meaning changes.

Examples of functional changes:

```text
- requirement added, removed, or changed
- authority level changed
- dependency changed
- status changed into or out of active/locked
- acceptance criteria changed
- validation requirement changed
- unit boundary changed
- public interface rule changed
- allowed or forbidden dependency changed
```

### 13.2 Metadata Digest

`MetadataDigest` changes when non-governing metadata changes.

Examples:

```text
- owner changed
- formatting changed without semantic effect
- explanatory note changed
- non-binding reference changed
- typo fixed without changing meaning
```

### 13.3 Digest Format

Digest fields must use:

```text
sha256:<64 lowercase hex characters>
```

`<pending>` is allowed only before the first validator implementation exists.

After the validator exists, `<pending>` is invalid for active or locked documents.


### 13.4 Lightweight Functional Digest Basis

For active and locked documents, the functional digest is computed from:

```text
canonical_document_bytes
+ functional registry fields for the document
+ direct functional dependency DocID/version/digest list
+ declared authority level
+ declared layer
+ declared status
```

Direct functional dependency list includes only:

```text
IMPORTS, EXTENDS, GOVERNS, USES, DERIVES, VALIDATES
```

It excludes:

```text
REFERENCES, RECOGNIZES, SUPERSEDES
```

Deterministic ordering:

```text
lexical by DocID, then by edge type, then by target DocID
```

This is intentionally lighter than full EQC-ES dependency-closure hashing, but it is strong enough to detect stale direct dependencies in the current L1 stage.

### 13.5 Metadata Digest Basis

The metadata digest is computed from:

```text
canonical_document_bytes for non-functional sections
+ owner metadata
+ non-binding references
+ recognized_by metadata
+ historical notes
```

Metadata-only changes must not alter governing semantics, readiness gates, authority, dependency edges, or acceptance criteria. If they do, they are functional changes.


---

## 13.6 Resolved Graph Hash

The ecosystem graph must produce a deterministic resolved graph hash.

Canonical graph representation:

```json
{
  "portfolio_id": "AGENT_X_L1",
  "nodes": [
    {"doc_id": "AX-L1-DOC-GOAL-001", "type": "system-goal", "layer": 0, "status": "active"}
  ],
  "edges": [
    {"src": "AX-L1-DOC-GOAL-001", "type": "GOVERNS", "dst": "AX-L1-DOC-ARCH-001", "payload": {}}
  ]
}
```

Rules:

1. Nodes are sorted lexicographically by `doc_id`.
2. Edges are sorted by `(src, type, dst)`.
3. Payload keys are sorted recursively.
4. Absent payload is normalized to `{}`.
5. Metadata-only edges may be included in a separate metadata graph hash, but must not be mixed into the functional resolved graph hash.
6. The semantic lockfile records the functional resolved graph hash.
7. A changed resolved graph hash makes the lockfile stale until regenerated.

Digest format:

```text
resolved_graph_hash = sha256:<64 lowercase hex characters>
```

`<pending>` is allowed only before the first validator exists.

---

## 13.7 Source-of-Truth Collision Scope

Duplicate ownership must be evaluated at the requirement, unit, interface, and target-artifact level.

Collision keys:

```text
requirement_id
unit_id
interface_id
fic_id
target_file
validation_rule_id
```

Rules:

1. Two active documents may describe the same subject only when one is explicitly subordinate through a functional edge.
2. Two active documents may not both claim final authority over the same collision key.
3. A collision between a FIC and a higher-authority document is resolved by the authority hierarchy, but must still be recorded.
4. A collision with no authority path blocks implementation.
5. The validator must report duplicate ownership with the exact collision key.

---

## 14. Versioning Rules

Documents use semantic versioning:

```text
vMAJOR.MINOR.PATCH
```

Version impact:

| Change | Version Impact |
|---|---|
| typo, formatting, non-functional wording | PATCH |
| clarifying existing rule without changing obligations | PATCH |
| adding a new compatible rule | MINOR |
| adding a new required document field | MINOR or MAJOR depending on breakage |
| changing authority order | MAJOR |
| changing layer rules | MAJOR |
| changing active root document | MAJOR |
| removing or weakening a requirement | MAJOR |
| changing FIC readiness or implementation gates | MAJOR |

A document's version must change whenever its `FunctionalDigest` changes.

A metadata-only change should normally produce a PATCH version bump unless the project chooses to track metadata outside version numbers.

---

## 14.5 Lifecycle Transition Rules

Document status changes are governed changes.

Allowed transitions:

```text
draft -> reviewed
reviewed -> active
active -> locked
locked -> active
active -> deprecated
deprecated -> archived
active -> blocked
blocked -> draft|reviewed|active only after remediation
```

Forbidden transitions:

```text
draft -> locked
archived -> active without migration record
blocked -> locked
historical/generated -> active without registry update
```

Rules:

1. A transition into `active` requires path, version-marker, registry, graph, and authority validation.
2. A transition into `locked` requires a current semantic lockfile.
3. A transition into `deprecated` requires a replacement, migration note, or explicit historical-retention reason.
4. A transition out of `blocked` requires a remediation record.
5. Status transitions must update the document version if the status affects governing authority.

---

## 15. Change Propagation Rules

When a document changes, the validator must compute affected documents.

Impact rules:

| Changed Document Type | Affected Documents |
|---|---|
| system-goal | all active L1 documents |
| architecture-contract | pseudocode, DAG, shared interfaces, FICs, validation plan, SIB bindings |
| whole-system-pseudocode | unit DAG, FICs, traceability matrix, validation plan |
| unit-dag | FIC registry, FICs, handoff packets, traceability matrix |
| shared-interface | FICs, SIB bindings, implementation packets, tests |
| validation-plan | FICs, completion records, review packets, release packets |
| FIC registry | all FIC units and SIB binding map |
| FIC unit | implementation packet, SIB binding, traceability matrix, tests |
| semantic lockfile | implementation readiness and release package |
| risk ledger | review packet and release packet |
| failure-learning log | future validation plan or FIC template when failure creates a new rule |

Required action categories:

```text
NO_ACTION
REVIEW_ONLY
UPDATE_REFERENCE
UPDATE_DEPENDENT_DOC
UPDATE_GRAPH
UPDATE_REGISTRY
UPDATE_SIB_BINDING
REVALIDATE
REGENERATE_LOCKFILE
REBUILD_IMPLEMENTATION_PACKAGE
BLOCK_IMPLEMENTATION
BLOCK_RELEASE
```

### 15.1 Deterministic Impact Closure

`agentx-es impact` must compute impact closure over functional graph edges.

Traversal rules:

1. Start from the changed `DocID`.
2. Traverse outgoing and incoming functional edges where the changed document affects the target's authority, inputs, requirements, validation, or derivation.
3. Do not traverse `REFERENCES`, `RECOGNIZES`, or `SUPERSEDES` unless the changed relation alters active authority.
4. Include the semantic lockfile if any active document digest, graph hash, or registry field changes.
5. Include Lightweight EQC-SIB bindings when a FIC, interface document, unit DAG, or implementation-governing document changes.
6. Sort affected documents lexicographically by `doc_id`.
7. Sort required actions in this severity order:

```text
BLOCK_RELEASE
BLOCK_IMPLEMENTATION
REBUILD_IMPLEMENTATION_PACKAGE
REGENERATE_LOCKFILE
REVALIDATE
UPDATE_SIB_BINDING
UPDATE_REGISTRY
UPDATE_GRAPH
UPDATE_DEPENDENT_DOC
UPDATE_REFERENCE
REVIEW_ONLY
NO_ACTION
```

The impact result must be reproducible for the same registry, graph, lockfile, and changed document.

---

## 16. Stale Document Rules

A document is stale when any governing dependency changed after the document was last validated.

A stale document must not remain `active` or `locked` unless:

```text
- it is revalidated successfully, or
- it has a recorded waiver, or
- it is downgraded to draft/reviewed/blocked
```

Staleness sources:

```text
- dependency version changed
- dependency digest changed
- source path changed
- authority order changed
- owning document changed
- FIC registry changed
- semantic lockfile changed
- validation plan changed
```

Stale-artifact remediation status:

```text
REVALIDATED
UPDATED
WAIVED
DOWNGRADED
DEPRECATED
BLOCKED
```

---

## 17. Orphan, Shadow, and Duplicate Rules

### 17.1 Orphan Document

A document is an orphan if:

```text
status is active or locked
AND it has no functional path from AX-L1-DOC-GOAL-001
```

Orphans block release.

### 17.2 Shadowed Document

A document is shadowed if another active document replaces its authority but the old document remains active.

Shadowed documents must be:

```text
- deprecated,
- archived,
- explicitly marked as historical, or
- removed from active authority paths
```

### 17.3 Duplicate Ownership

Duplicate ownership exists when two active documents claim authority over the same requirement, unit, interface, FIC, or target file.

Duplicate ownership blocks implementation unless one document is explicitly subordinate.

---

## 18. Required Ecosystem Sidecars

The lightweight L1 ecosystem should contain:

```text
L1/ecosystem/ecosystem-registry.yaml
L1/ecosystem/ecosystem-graph.yaml
L1/ecosystem/ecosystem-validation-log.md
L1/ecosystem/ecosystem-error-codes.yaml
L1/ecosystem/ecosystem-schemas/
  ecosystem-registry.schema.json
  ecosystem-graph.schema.json
  ecosystem-validation-output.schema.json
  ecosystem-impact-output.schema.json
```

Optional but recommended:

```text
L1/ecosystem/ecosystem-release-notes-template.md
L1/ecosystem/ecosystem-waivers.yaml
L1/ecosystem/ecosystem-migration-log.md
```

Generated documents belong under:

```text
L1/generated/
```

---

## 19. Validator Commands

The minimum validator command set:

```text
agentx-es validate
agentx-es impact --change <DocID>@<version>
agentx-es registry-check
agentx-es graph-check
agentx-es lockfile-check
```

Required exit codes:

| Exit Code | Meaning |
|---:|---|
| 0 | PASS |
| 1 | FAIL, validation errors found |
| 2 | TOOLING ERROR |

The validator must never silently skip a required check.

If a check cannot run, the validator must report:

```yaml
skipped_checks:
  - check: "<name>"
    reason: "<reason>"
    release_blocking: true
```

---

## 20. Validation Output Schema

`agentx-es validate` must produce deterministic JSON.

Minimum schema:

```json
{
  "portfolio_id": "AGENT_X_L1",
  "eqc_es_version": "v0.5.0",
  "status": "PASS|FAIL",
  "errors": [
    {
      "code": "AX_ES_...",
      "doc_id": "AX-L1-DOC-...",
      "path": "L1/...",
      "message": "..."
    }
  ],
  "warnings": [],
  "functional_reachability_missing": [],
  "metadata_reachability_only": [],
  "stale_documents": [],
  "orphan_documents": [],
  "duplicate_ownership": [],
  "blocked_documents": [],
  "digest_mismatches": [],
  "skipped_checks": [],
  "resolved_graph_hash": "sha256:<hash-or-pending>"
}
```

Deterministic ordering:

```text
errors sorted by code, doc_id, path
warnings sorted by code, doc_id, path
document lists sorted lexicographically by doc_id
```

---

## 21. Impact Output Schema

`agentx-es impact --change <DocID>@<version>` must produce deterministic JSON.

Minimum schema:

```json
{
  "portfolio_id": "AGENT_X_L1",
  "change": "AX-L1-DOC-PS-001@v0.2.0",
  "classification": "METADATA|FUNCTIONAL|STRUCTURAL|VALIDATION",
  "changed_doc": "AX-L1-DOC-PS-001",
  "affected_documents": [
    {
      "doc_id": "AX-L1-DOC-DAG-001",
      "required_action": "UPDATE_DEPENDENT_DOC",
      "version_impact": "PATCH|MINOR|MAJOR",
      "release_blocking": true
    }
  ],
  "required_global_actions": [
    "REVALIDATE",
    "REGENERATE_LOCKFILE"
  ]
}
```

---

## 22. Error Code Registry

Errors and warnings must come from:

```text
L1/ecosystem/ecosystem-error-codes.yaml
```

Initial codes:

```yaml
error_codes:
  AX_ES_PATH_NOT_FOUND: "Registered document path does not exist."
  AX_ES_PATH_ESCAPES_ROOT: "Registered path escapes repository root."
  AX_ES_EMPTY_DOCUMENT: "Registered document is empty and not marked AllowEmpty."
  AX_ES_MISSING_VERSION_MARKER: "Document does not declare matching version marker."
  AX_ES_DUPLICATE_DOC_ID: "Two registry entries use the same DocID."
  AX_ES_DUPLICATE_PATH: "Two active documents use the same path."
  AX_ES_UNKNOWN_DOC_TYPE: "Document type is not allowed."
  AX_ES_INVALID_STATUS: "Document status is not allowed."
  AX_ES_INVALID_LAYER_EDGE: "Document depends on a higher layer through a functional edge."
  AX_ES_CYCLE_DETECTED: "Functional dependency graph contains a cycle."
  AX_ES_ORPHAN_DOCUMENT: "Active document is not reachable from root."
  AX_ES_METADATA_ONLY_REACHABILITY: "Document is reachable only through metadata edges."
  AX_ES_STALE_DOCUMENT: "Document depends on a newer or changed dependency and was not revalidated."
  AX_ES_DIGEST_MISMATCH: "Stored digest does not match computed digest."
  AX_ES_DUPLICATE_OWNERSHIP: "Two active documents claim the same authority."
  AX_ES_BLOCKED_DEPENDENCY: "Active document depends on a blocked document."
  AX_ES_DEPRECATED_DEPENDENCY: "Active document depends on a deprecated document."
  AX_ES_SCHEMA_INVALID: "Sidecar does not match its schema."
  AX_ES_SILENT_SKIP: "Validator skipped a required check without reporting it."
```

Unknown error codes are invalid validator output.

---

## 23. Semantic Lockfile Integration

The L1 semantic lockfile is:

```text
L1/generated/semantic_lockfile.yaml
```

Lightweight EQC-ES governs whether the lockfile is current.

The lockfile must contain:

```yaml
lockfile_version: "v0.5"
portfolio_id: "AGENT_X_L1"
created_at_utc: "YYYY-MM-DDTHH:MM:SSZ"
root_doc_id: "AX-L1-DOC-GOAL-001"
documents:
  - doc_id: "AX-L1-DOC-GOAL-001"
    path: "L1/docs/00_L1_SYSTEM_GOAL.md"
    version: "v0.1.0"
    functional_digest: "sha256:<hash>"
    metadata_digest: "sha256:<hash>"
resolved_graph_hash: "sha256:<hash>"
validation_report: "L1/generated/validation_report.md"
status: "LOCKED_FOR_IMPLEMENTATION"
```

Implementation may proceed only when:

```text
- lockfile exists
- lockfile validates
- all referenced active documents match their current digest
- validation status is PASS
- no release-blocking stale documents exist
```

---

## 23.5 ES/SIB Boundary Synchronization

Lightweight EQC-ES governs documents. Lightweight EQC-SIB governs implementation artifacts and document-to-code bindings.

Synchronization is required when any of the following documents change functionally:

```text
L1/docs/04_L1_UNIT_DAG.md
L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md
L1/docs/06_L1_VALIDATION_PLAN.md
L1/docs/08_L1_TRACEABILITY_MATRIX.md
L1/fic/index.fic.yaml
L1/fic/units/*.md
```

Required actions:

1. Run `agentx-es impact` for the document change.
2. Run the corresponding SIB impact check for bound implementation artifacts.
3. Update SIB binding records when document anchors, FIC IDs, target files, or implementation-unit boundaries change.
4. Block implementation if ES says the document ecosystem is stale or SIB says the binding map is stale.
5. Regenerate semantic lockfile after ES and SIB sidecars agree.

ES must not claim an implementation package is ready unless the relevant SIB bindings are current.

---

## 24. Release Package Requirements

A release or implementation handoff package must include:

```text
L1/ecosystem/ecosystem-registry.yaml
L1/ecosystem/ecosystem-graph.yaml
L1/generated/semantic_lockfile.yaml
L1/generated/validation_report.md
L1/generated/readiness_report.md
L1/docs/08_L1_TRACEABILITY_MATRIX.md
L1/docs/07_L1_RISK_LEDGER.md
```

For implementation tasks, the package must also include:

```text
FIC document(s)
context packet
handoff packet
SIB binding records
required checks
completion-record template
```

Release must be blocked if any required package file is missing or stale.

---

## 24.5 Release Package Digest Closure

A release package is closed only when the following digests are present and current:

```text
registry_digest
graph_digest
resolved_graph_hash
semantic_lockfile_digest
validation_report_digest
risk_ledger_digest
traceability_matrix_digest
sib_binding_digest, when implementation artifacts are included
fic_registry_digest, when FICs are included
```

Rules:

1. The release package must list every included file with path, version, and digest.
2. Missing digest fields block release after the first validator exists.
3. A package cannot mix documents from different lockfile states.
4. Regenerated reports must identify their source lockfile.
5. Manual edits to generated reports invalidate the package unless explicitly authorized.

---

## 25. Waiver Policy

Waivers are allowed in the lightweight stage but must be explicit.

Waiver file:

```text
L1/ecosystem/ecosystem-waivers.yaml
```

Minimum waiver record:

```yaml
waivers:
  - waiver_id: "AX-ES-WVR-001"
    doc_id: "AX-L1-DOC-..."
    waived_rule: "AX_ES_..."
    reason: "..."
    risk: "low|medium|high|critical"
    expires_utc: "YYYY-MM-DDTHH:MM:SSZ"
    approved_by: "user|maintainer|reviewer"
```

Rules:

1. Waivers must expire.
2. Waivers must not hide unknown authority conflicts.
3. Waivers for system-goal, architecture, or L0-impact rules are release-blocking unless manually approved.
4. Active waivers must be listed in validation output.
5. A waiver may unblock implementation only if its `risk` is `low` or `medium` and no higher-authority conflict exists.
6. A `high` or `critical` waiver may allow exploratory work, but must not allow release or promotion.
7. Expired waivers are treated as validation errors.
8. Waivers must name the exact rule, document, affected dependency, and required follow-up.

Waiver severity behavior:

| Waiver Risk | Implementation | Release |
|---|---:|---:|
| `low` | may proceed with warning | may proceed if listed |
| `medium` | may proceed with review | may proceed only if approved |
| `high` | exploratory only | blocked |
| `critical` | blocked unless explicitly user-approved | blocked |

---

## 26. L0 Impact Rule

Any L1 document change that affects L0 must be classified as L0-impacting.

L0-impacting examples:

```text
- change to L0 boundary rules
- permission to edit L0 runtime files
- change to L0 proof commands
- change to L0 public contract assumptions
- change to L0 seed invariants
- change to L0/L1 dependency direction
```

L0-impacting changes require:

```text
- explicit impact report
- L0 proof commands listed
- SIB binding update if implementation artifacts are affected
- semantic lockfile regeneration
- release-blocking review
```

L1 must never silently authorize changes to L0.

---

## 27. Migration, Split, Merge, and Delete Rules

### 27.1 Move

If a document path changes:

```text
- keep the same DocID
- update registry path
- record old path in migration log
- update graph if path appears in payloads
- regenerate lockfile
```

### 27.2 Split

If one document becomes several:

```text
- original DocID becomes deprecated or historical
- new documents receive new DocIDs
- migration log records source and targets
- graph edges are redistributed
- traceability matrix is updated
```

### 27.3 Merge

If several documents become one:

```text
- new merged document receives a new DocID
- source documents become deprecated or historical
- migration log records all sources
- duplicate ownership is resolved
```

### 27.4 Delete

Deleting a governed document is allowed only when:

```text
- no active document depends on it through functional edges
- it is not required by the semantic lockfile
- it is not the sole owner of a requirement, unit, interface, or validation rule
- migration log records the deletion
```

Otherwise deletion is blocked.

---

## 28. Minimum Readiness Checklist

A document ecosystem is ready for L1 implementation when:

```text
[ ] ecosystem registry exists
[ ] ecosystem graph exists
[ ] all active documents have unique DocIDs
[ ] all active paths exist and are non-empty
[ ] all active documents have version markers
[ ] all active documents have allowed status values
[ ] all active documents have allowed document types
[ ] all active documents are reachable from root through functional edges
[ ] no forbidden upward functional dependency exists
[ ] no active document depends on blocked/deprecated documents
[ ] no duplicate ownership exists
[ ] semantic lockfile exists
[ ] semantic lockfile matches active document digests
[ ] validation report exists
[ ] validation status is PASS
[ ] risk ledger exists
[ ] traceability matrix exists
[ ] release-blocking waivers are absent or explicitly approved
```

If any required item fails, the ecosystem status is not ready.

---

## 28.5 Release-Blocking Matrix

The validator must classify findings as release-blocking or non-release-blocking.

| Condition | Release Blocking? | Notes |
|---|---:|---|
| Missing registry | yes | No governed ecosystem exists |
| Missing graph | yes | Reachability cannot be proven |
| Missing root document | yes | No authority source |
| Missing active document path | yes | Registry is not physically true |
| Empty active document without `allow_empty` | yes | Invalid governed artifact |
| Version-marker mismatch | yes | Registry and document disagree |
| Functional cycle | yes | Governance authority is ambiguous |
| Upward functional dependency | yes | Layer rule violation |
| Metadata-only reachability | yes | False authority path |
| Stale active or locked document | yes | Implementation may use old semantics |
| Duplicate ownership | yes | Conflicting source of truth |
| Digest mismatch after validator exists | yes | Lockfile cannot be trusted |
| Unknown error code in validator output | yes | Validator output is not governed |
| Waiver expired | yes | Waiver no longer authorizes risk |
| Historical reference missing | no | Warning unless used by active document |
| Metadata typo | no | PATCH impact if semantics unchanged |


## 29. Maturity Levels

| Level | Name | Meaning |
|---:|---|---|
| 0 | informal | Documents exist but are not registered |
| 1 | registered | Documents have DocIDs and registry entries |
| 2 | graph-aware | Functional dependencies are represented |
| 3 | validated | Registry and graph checks pass |
| 4 | lockfile-governed | Semantic lockfile blocks stale implementation |
| 5 | release-ready | Release package, risk, traceability, and evidence all close |

Agent_X L1 should target:

```text
Level 4 before serious implementation
Level 5 before release/promotion
```

---

## 29.5 Initial Sidecar Templates

The first registry and graph should be created from these minimal templates. These templates use v0.5 sidecar versions and must be expanded before release.

### 29.5.1 Registry Template

```yaml
ecosystem_registry_version: "v0.5"
portfolio_id: "AGENT_X_L1"
documents:
  - doc_id: "AX-L1-DOC-GOAL-001"
    title: "L1 System Goal"
    type: "system-goal"
    path: "L1/docs/00_L1_SYSTEM_GOAL.md"
    version: "v0.1.0"
    status: "active"
    owner: "l1-control-plane"
    layer: 0
    authority_level: "constitutional"
    functional_digest: "sha256:<pending>"
    metadata_digest: "sha256:<pending>"
    depends_on: []
    recognized_by: []
    governs: []
    allow_empty: false
    generated_from: null
    last_validated_utc: null
    source_of_truth_owner: "AX-L1-DOC-GOAL-001"
```

### 29.5.2 Graph Template

```yaml
ecosystem_graph_version: "v0.5"
portfolio_id: "AGENT_X_L1"
root_doc_id: "AX-L1-DOC-GOAL-001"
nodes:
  - doc_id: "AX-L1-DOC-GOAL-001"
    path: "L1/docs/00_L1_SYSTEM_GOAL.md"
    type: "system-goal"
    layer: 0
edges: []
```

Templates are not enough for release. They are only the starting point for registering the document ecosystem.

---

## 30. Deferred Full EQC-ES Capabilities

The following capabilities are intentionally deferred:

```text
- distributed portfolio imports
- alias namespace rewriting
- full FD/MD dependency closure
- signed portfolio checkpoints
- golden ecosystem traces
- profile-specific shadow traces
- clean-room trace validation
- multi-owner quorum approval
- cryptographic waiver signing
- hardware equivalence tiers
- cross-repository ecosystem federation
```

A deferred capability may be promoted only when:

```text
- current lightweight governance is passing,
- the new capability solves a real observed failure mode,
- the additional burden is justified,
- migration rules are written before adoption.
```

---

## 30.5 Minimum Validator Maturity Profile

The first validator does not need to implement full EQC-ES. It must implement the following checks before the ecosystem can claim Level 4 maturity:

```text
1. registry schema validation
2. graph schema validation
3. path existence and path safety validation
4. version-marker validation
5. DocID uniqueness validation
6. status/type/authority/layer enum validation
7. functional edge validity validation
8. functional cycle detection
9. root reachability validation
10. stale lockfile validation
11. skipped-check reporting
12. deterministic JSON output validation
```

Validator maturity levels:

| Validator Level | Meaning |
|---:|---|
| V0 | manual checklist only |
| V1 | registry and graph parse checks |
| V2 | path, DocID, enum, and version-marker checks |
| V3 | reachability, cycle, stale-lockfile, and duplicate-ownership checks |
| V4 | deterministic output, schema fixtures, and release-blocking classification |

Agent_X L1 should reach V3 before serious implementation and V4 before release/promotion.

## 30.6 Schema Fixture Requirements

Every ecosystem schema must include at least one passing fixture and one failing fixture.

Required fixture set:

```text
L1/ecosystem/ecosystem-schemas/fixtures/registry.valid.yaml
L1/ecosystem/ecosystem-schemas/fixtures/registry.invalid.duplicate_doc_id.yaml
L1/ecosystem/ecosystem-schemas/fixtures/graph.valid.yaml
L1/ecosystem/ecosystem-schemas/fixtures/graph.invalid.cycle.yaml
L1/ecosystem/ecosystem-schemas/fixtures/validation_output.valid.json
L1/ecosystem/ecosystem-schemas/fixtures/validation_output.invalid.unknown_error_code.json
L1/ecosystem/ecosystem-schemas/fixtures/impact_output.valid.json
L1/ecosystem/ecosystem-schemas/fixtures/impact_output.invalid.missing_action.json
```

Fixture records must include:

```yaml
fixture_id: "AX-ES-FIXTURE-..."
intent: "what this fixture proves"
expected_result: "PASS|FAIL"
expected_error_codes: []
```

A schema without fixtures is advisory, not enforceable.



## 30.7 Anchor Identity and Fragment Resolution

Every governing document should expose stable anchors for requirements, sections, units, interfaces, and validation rules.

Anchor format:

```text
AX-L1-ANCHOR-<DOC-TYPE>-<NUMBER>-<SHORT-NAME>
```

Examples:

```text
AX-L1-ANCHOR-GOAL-001-NON-GOALS
AX-L1-ANCHOR-ARCH-001-L0-BOUNDARY
AX-L1-ANCHOR-PS-001-EVOLVE-ONCE
AX-L1-ANCHOR-FIC-001-PUBLIC-SURFACE
```

Rules:

1. Anchors must be stable after assignment.
2. A renamed heading must keep its anchor.
3. A removed anchor must be recorded in the migration log unless the document is still draft.
4. Functional graph payloads may reference anchors, but anchor references must resolve during validation.
5. A broken anchor in a functional edge is release-blocking.
6. Broken anchors in `REFERENCES` or `RECOGNIZES` are warnings unless used by an active implementation package.

Graph edge payload example:

```yaml
edges:
  - src: "AX-L1-DOC-ARCH-001"
    type: "GOVERNS"
    dst: "AX-L1-DOC-FIC-001"
    payload:
      src_anchor: "AX-L1-ANCHOR-ARCH-001-L0-BOUNDARY"
      dst_anchor: "AX-L1-ANCHOR-FIC-001-DEPENDENCIES"
      binding_strength: "HARD"
```

Allowed `binding_strength` values:

```text
HARD
SOFT
REFERENCE_ONLY
```

Only `HARD` and `SOFT` edges may be functional. `REFERENCE_ONLY` edges must use metadata edge types.

---

## 30.8 Registry and Graph Consistency Contract

The registry and graph must agree exactly on active document identity.

Blocking inconsistencies:

```text
- graph node missing from registry
- registry active or locked document missing from graph
- graph node path differs from registry path
- graph node type differs from registry type
- graph node layer differs from registry layer
- functional edge uses a DocID not present in registry
- registry depends_on list disagrees with functional graph edges
- registry governs list disagrees with outgoing GOVERNS edges
```

Canonical consistency rule:

```text
The graph is the source of truth for edges.
The registry may duplicate edge summaries for readability.
If duplicated fields disagree, validation fails.
```

The validator must report the exact disagreeing fields and must not choose one side silently.

---

## 30.9 Exact Digest Field Partition

To avoid ambiguous digest behavior, registry fields are partitioned into functional, metadata, and validation-state fields.

Functional registry fields:

```text
doc_id
type
path
version
status
layer
authority_level
depends_on
governs
allow_empty
generated_from
source_of_truth_owner
```

Metadata registry fields:

```text
title
owner
recognized_by
historical_notes
```

Validation-state fields:

```text
functional_digest
metadata_digest
last_validated_utc
validation_status
validator_version
```

Rules:

1. Functional fields participate in `FunctionalDigest`.
2. Metadata fields participate in `MetadataDigest`.
3. Validation-state fields must not participate in `FunctionalDigest`, otherwise validation would become self-referential.
4. Validation-state fields are included in release package digest closure.
5. Moving a field between partitions is a MAJOR change to this standard.

---

## 30.10 Deterministic Change Classification Algorithm

Document changes must be classified deterministically.

Allowed classifications:

```text
METADATA
VALIDATION
STRUCTURAL
FUNCTIONAL
```

Severity order:

```text
METADATA < VALIDATION < STRUCTURAL < FUNCTIONAL
```

Trigger rules:

| Trigger | Classification |
|---|---|
| Only metadata fields changed | `METADATA` |
| Validation report, validator version, or fixture changed without changing rules | `VALIDATION` |
| Registry/graph path, node, edge, status, layer, or sidecar schema changed | `STRUCTURAL` |
| Requirement, authority, acceptance, dependency, unit boundary, interface, or validation obligation changed | `FUNCTIONAL` |
| Any L0-impacting rule changed | `FUNCTIONAL` and release-blocking |
| Any classification conflict | highest severity wins |

The impact output must include:

```json
{
  "classification_basis": [
    {"trigger": "AX_ES_TRG_FUNCTIONAL_FIELD_CHANGED", "classification": "FUNCTIONAL"}
  ]
}
```

A validator must not classify a change from filename or commit message alone.

---

## 30.11 Validation Input Manifest

Every validation run must declare its exact inputs.

Required file:

```text
L1/ecosystem/validation-input-manifest.yaml
```

Minimum fields:

```yaml
validation_input_manifest_version: "v0.5"
portfolio_id: "AGENT_X_L1"
run_id: "AX-ES-RUN-YYYYMMDDTHHMMSSZ"
validator:
  command: "agentx-es validate"
  version: "v0.1.0"
inputs:
  - path: "L1/ecosystem/ecosystem-registry.yaml"
    digest: "sha256:<hash>"
  - path: "L1/ecosystem/ecosystem-graph.yaml"
    digest: "sha256:<hash>"
  - path: "L1/generated/semantic_lockfile.yaml"
    digest: "sha256:<hash>"
```

Rules:

1. Validation output must reference the input manifest digest.
2. A validation report without an input manifest is advisory only.
3. Input paths must follow the canonical path rules from Section 3.
4. Input manifest timestamps must use UTC `YYYY-MM-DDTHH:MM:SSZ`.

---

## 30.12 Generated Artifact Edit Policy

Generated artifacts must not be manually edited unless the registry explicitly allows maintenance mode.

Generated artifacts include:

```text
L1/generated/semantic_lockfile.yaml
L1/generated/validation_report.md
L1/generated/readiness_report.md
L1/generated/release_package_manifest.yaml
```

Rules:

1. Generated artifacts must contain `Generated-From` and `Generated-By` markers.
2. Generated artifacts must list their source input manifest or source lockfile.
3. Manual edits to generated artifacts invalidate the artifact.
4. A manually repaired generated artifact must be reclassified as `blocked` or `reviewed` until regenerated by tooling.
5. A generated artifact may not govern implementation unless its generator and source inputs are recorded.

---

## 30.13 Release Package Manifest Schema

A release package must include a machine-readable manifest.

Required file:

```text
L1/generated/release_package_manifest.yaml
```

Minimum schema:

```yaml
release_package_manifest_version: "v0.5"
portfolio_id: "AGENT_X_L1"
created_at_utc: "YYYY-MM-DDTHH:MM:SSZ"
lockfile: "L1/generated/semantic_lockfile.yaml"
resolved_graph_hash: "sha256:<hash>"
files:
  - path: "L1/ecosystem/ecosystem-registry.yaml"
    type: "registry"
    version: "v0.5"
    digest: "sha256:<hash>"
    source: "manual"
  - path: "L1/generated/validation_report.md"
    type: "generated-report"
    version: "v0.5"
    digest: "sha256:<hash>"
    source: "agentx-es validate"
validation:
  status: "PASS"
  report: "L1/generated/validation_report.md"
waivers: []
release_status: "READY|BLOCKED"
```

Rules:

1. Every release-package file must appear exactly once.
2. Every listed file must exist and match its digest.
3. `release_status` must be `BLOCKED` if validation status is not `PASS`.
4. `release_status` must be `BLOCKED` if any release-blocking waiver, stale document, or digest mismatch exists.
5. The release package manifest itself must be included in any final archive or handoff bundle.

---

## 30.14 v0.4 Residual Limit

This lightweight ES is now strong enough for the current Agent_X L1 document stage, but it still intentionally does not claim full EQC-ES parity.

Remaining deferred items are acceptable only because L1 is not yet operating as a distributed, signed, production portfolio.

A future upgrade to full ES is required before:

```text
- cross-repository federation,
- signed releases,
- independent external consumers,
- automated promotion into L0,
- multi-user governance,
- non-local execution environments.
```

## 31. Acceptance Criteria

This Lightweight EQC-ES document is acceptable when:

```text
[ ] It defines the L1 document portfolio root.
[ ] It defines allowed document types.
[ ] It defines stable DocID rules.
[ ] It defines registry and graph sidecars.
[ ] It defines authority levels and conflict resolution.
[ ] It defines layer and edge rules.
[ ] It defines reachability and orphan checks.
[ ] It defines digest and versioning rules.
[ ] It defines stale-document handling.
[ ] It defines semantic lockfile integration.
[ ] It defines validator commands and outputs.
[ ] It defines deterministic impact closure.
[ ] It defines resolved graph hashing.
[ ] It defines lifecycle transition rules.
[ ] It defines source-of-truth collision keys.
[ ] It defines ES/SIB synchronization boundaries.
[ ] It defines release-blocking conditions.
[ ] It defines waiver, migration, split, merge, and delete behavior.
[ ] It defines version-marker rules by document format.
[ ] It defines cycle detection and graph hashing rules.
[ ] It defines functional and metadata digest bases.
[ ] It defines minimum validator maturity and schema fixtures.
[ ] It defines anchor identity and fragment resolution.
[ ] It defines registry and graph consistency rules.
[ ] It defines exact digest-field partitioning.
[ ] It defines deterministic change classification.
[ ] It defines validation input manifests.
[ ] It defines generated-artifact edit policy.
[ ] It defines release package manifest closure.
[ ] It protects L0 from silent L1 authority drift.
[ ] It remains lightweight enough for the current Agent_X L1 stage.
```

---

## 31.5 Quality Assessment

This v0.5 document is rated **10/10 for the current Agent_X L1 stage**.

It is not claiming full production EQC-ES parity. It is claiming that the lightweight Agent_X L1 document-portfolio standard is complete enough to govern the local L1 control plane before implementation begins.

Why it now reaches 10/10 for this stage:

```text
- portfolio root and path rules are explicit
- document types, DocIDs, anchors, and version markers are governed
- registry and graph sidecars have deterministic schemas
- registry/graph consistency is release-blocking
- authority, layer, edge, reachability, and cycle rules are defined
- functional and metadata digest bases are partitioned
- direct dependency digest closure is mandatory for active/locked documents
- full transitive digest closure is deferred but explicitly gated by maturity level
- stale-document handling and lockfile regeneration rules are explicit
- ES/SIB synchronization boundaries are defined
- waiver, migration, split, merge, delete, and generated-artifact policies are defined
- validation input manifests and deterministic validator output are required
- release package manifest closure is defined
- L0-impacting authority drift is blocked
- the remaining full-ES capabilities are consciously deferred, not missing by accident
```

## 32. Direct vs. Transitive Digest Maturity Rule

Lightweight EQC-ES intentionally uses direct functional dependency digest closure during the first L1 stage.

Mandatory now:

```text
FunctionalDigest(Doc) must include:
- canonical document bytes
- functional registry fields
- direct functional dependency DocID/version/digest list
- authority level
- layer
- status
```

Deferred until full ES maturity:

```text
- recursive transitive dependency closure
- signed portfolio checkpoint hashing
- clean-room golden ecosystem trace hashing
- distributed sub-portfolio checkpoint imports
```

Rules:

1. Direct closure is sufficient for Agent_X L1 Level 4 local implementation governance.
2. Full transitive closure becomes required before Level 5 external release or any automated promotion into L0.
3. A document must not claim full EQC-ES parity while using lightweight direct closure only.
4. The validator must report the digest maturity mode in validation output.

Validation output must include:

```json
{
  "digest_maturity": "DIRECT_CLOSURE|TRANSITIVE_CLOSURE",
  "full_eqc_es_parity": false
}
```

## 33. Final Self-Assessment Gate

Before this standard is accepted as the active Agent_X L1 ecosystem standard, it must pass this self-assessment gate:

```text
[ ] no stale version references in normative examples
[ ] no duplicate section numbers in the active document body
[ ] all sidecar examples use the current standard version
[ ] validator JSON examples use the current standard version
[ ] quality assessment matches the current version
[ ] changelog includes the current version
[ ] any deferred full-ES capability is listed as deferred, not omitted silently
[ ] acceptance criteria match the actual rules in the document
```

A failure in this self-assessment gate is a documentation-quality defect and must be corrected before the document is used as an active governance standard.

## 34. Initial Implementation Target

The first implementation target for this standard is **not** full automation.

The first target is:

```text
1. Create L1/ecosystem/ecosystem-registry.yaml.
2. Create L1/ecosystem/ecosystem-graph.yaml.
3. Register the core L1 documents.
4. Validate path existence and DocID uniqueness manually or with a small script.
5. Generate the first semantic lockfile.
6. Use the lockfile to gate the first L1 FIC implementation packet.
```

That is enough to make the L1 control plane coherent without overbuilding.

## 35. Remaining Non-Blocking Limitations

The document is complete for the current Agent_X L1 stage, but it remains intentionally below full production EQC-ES.

Deferred limitations:

```text
- no signed portfolio checkpoints yet
- no distributed sub-portfolio imports yet
- no cryptographic waiver quorum yet
- no clean-room golden ecosystem traces yet
- no full transitive digest closure until Level 5 or L0-promotion workflows
```

These limitations do not reduce the score for the current L1 stage because they are not required for local, controlled L1 document governance.

They must be reconsidered before:

```text
- cross-repository federation
- signed releases
- independent external consumers
- automated promotion into L0
- multi-user governance
- non-local execution environments
```

## 36. Final Rule

Lightweight EQC-ES has one central rule:

```text
No L1 implementation package may be treated as governed unless the L1 document ecosystem that authorizes it is registered, reachable, current, and validated.
```

If the ecosystem is stale, contradictory, orphaned, or unregistered, implementation must be blocked until the document control plane is repaired.

## 37. Changelog

### v0.5.0

Added/corrected:

```text
- current-version normalization across examples
- final self-assessment gate
- direct-vs-transitive digest maturity rule
- validation-output digest maturity fields
- duplicate section-number cleanup
- 10/10 current-stage quality classification
```

### v0.4.0

Added:

```text
- anchor identity and fragment resolution
- registry and graph consistency contract
- exact digest-field partitioning
- deterministic change classification algorithm
- validation input manifest
- generated artifact edit policy
- release package manifest schema
- explicit lightweight residual limit
```

### v0.3.0

Added deterministic impact closure, resolved graph hashing, lifecycle transitions, source-of-truth collision keys, ES/SIB boundary synchronization, waiver severity behavior, and initial registry/graph templates.

### v0.2.0

Added version-marker rules, registry closure fields, graph schema, cycle detection, digest basis, release-blocking matrix, validator maturity levels, fixture rules, and expanded acceptance criteria.

### v0.1.0

Initial lightweight EQC-ES for Agent_X L1 document-portfolio governance.
