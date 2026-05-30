# Agent_X L2 Lightweight EQC-ES / Ecosystem Specification

**Document ID:** `AGENT-X-L2-EQC-ES-001`  
**Version:** `v0.4.0`  
**Status:** `ready-for-use`  
**Layer:** `L2`  
**Applies to:** `Agent_X/L2`  
**Parent Standard:** Lightweight adaptation of EQC Ecosystem Specification for Agent_X L2  
**Related L2 Standards:**

```text
AGENT_X_L2_PSEUDOCODE_TO_FIC_WORKFLOW_v0_5
AGENT_X_L2_LIGHTWEIGHT_EQC_FIC_v0_4
AGENT_X_L2_LIGHTWEIGHT_EQC_SIB_BRIDGE_v0_4
```

**Source Standard Input Manifest:**

```yaml
source_standard_manifest:
  parent_standard:
    path: "ECOSYSTEM.md"
    standard_name: "EQC Ecosystem Specification"
    adaptation_mode: "lightweight-l2-profile-spec"
  sibling_l2_standards:
    - "AGENT_X_L2_PSEUDOCODE_TO_FIC_WORKFLOW_v0_5"
    - "AGENT_X_L2_LIGHTWEIGHT_EQC_FIC_v0_4"
    - "AGENT_X_L2_LIGHTWEIGHT_EQC_SIB_BRIDGE_v0_4"
  intended_stage: "L2 profile/spec governance only"
  implementation_authority: false
  release_evidence_default: false
```

**Primary purpose:** Define a lightweight registry and graph system for L2 documents, profiles, blueprints, integration specs, evaluation specs, generated profile catalogs, profile-readiness reports, and controlled L2-to-L1 handoff visibility.


**Previous Version Rating:** `9.8/10`

The previous version was strong enough for the current L2 profile/spec ecosystem stage, but it still had a few precision gaps that could confuse weaker agents or validators. The remaining issues were not about adding full production EQC-ES. They were about making the lightweight ES package more closed around profile-catalog derivation, bridge synchronization, schema fixtures, digest maturity, and final validation reporting.

**Fixes applied in v0.4.0:**

```text
- Added explicit profile-catalog source-of-truth partitioning.
- Added schema fixture and negative-fixture intent rules.
- Added bridge synchronization blocking rules for L2 ES and L2 SIB mismatch.
- Added digest maturity levels so bootstrap placeholders are not confused with release evidence.
- Added post-scaffold validation bundle requirements.
- Added exact weaker-agent final response contract.
- Added final no-false-claim and status decision rules.
- Updated examples and validator schemas to v0.4.0.
```

**v0.4 Upgrade Focus:** closes the remaining current-stage ecosystem gaps without expanding L2 into a runtime or full release-grade EQC-ES system.

---

## 0. Purpose

Agent_X L2 Lightweight EQC-ES is the document-ecosystem governance layer for the L2 profile/spec stage.

L2 is not a runtime layer yet. L2 defines specialization profiles, blueprints, evaluation specs, and integration proposals that L1 may later convert into governed implementation work.

This standard exists so that every L2 profile/spec artifact is:

```text
- discoverable;
- uniquely identified;
- versioned;
- path-stable;
- authority-aware;
- dependency-aware;
- traceable to the L2 system goal;
- safe to hand off to L1 only through declared bridge records.
```

It prevents:

```text
- orphan profiles;
- duplicate profile ownership;
- stale integration specs;
- profiles that silently authorize implementation;
- L2 runtime code appearing before approval;
- profile documents bypassing L1;
- generated catalogs becoming false authority;
- unregistered specialization specs being treated as active.
```

---

## 1. L2 ES Scope

This standard governs L2 control-plane artifacts only.

Governed artifact classes:

```text
L2/README.md
L2/docs/*.md
L2/profiles/*.yaml
L2/blueprints/*.md
L2/integration_specs/*.md
L2/evaluation_specs/*.md
L2/standards/*.md
L2/ecosystem/*.yaml
L2/ecosystem/*.md
L2/sib/*.yaml
L2/eqc/**/*.md
L2/eqc/**/*.yaml
L2/generated/*.yaml
L2/generated/*.md
L2/evidence/**
```

This standard does not govern implementation code because L2 must not contain runtime implementation in the current stage.

Forbidden current-stage implementation directories:

```text
L2/controller/
L2/runtime/
L2/agents/
L2/tools/
L2/model_router/
L2/memory/
L2/autonomy/
L2/executors/
```

If any of these directories exist, the L2 ES validator must classify them as one of:

```text
REGISTERED_PLACEHOLDER
EXPLICITLY_DEFERRED
BLOCKING_RUNTIME_SCOPE_DRIFT
```

Unregistered runtime-like directories are blocking.

---

## 2. Position in the L2 Standards Stack

L2 uses five lightweight standards:

```text
Pseudocode-to-FIC Workflow
  governs the process from L2 goal to profile package to L1 handoff candidate

Lightweight EQC-FIC
  governs L2 profile/spec artifacts that may later become implementation units

Lightweight EQC-SIB / Bridge
  binds L2 profiles/specs to L1 handoff and FIC targets

Lightweight EQC-ES
  governs the L2 document/profile ecosystem itself

Lightweight EQC
  governs algorithmic or procedural profile-selection logic only
```

This document is the L2 document-portfolio control layer.

It answers:

```text
Which L2 documents exist?
Which L2 profiles are active?
Which profile owns which specialization target?
Which blueprints, integration specs, and evaluation specs belong to each profile?
Which documents are stale, orphaned, duplicated, or unreachable?
Which profile packages are eligible to be reported to L1?
```

---

## 3. Non-Goals

L2 Lightweight EQC-ES must not become full EQC-ES too early.

This document does not require in the first L2 stage:

```text
- signed portfolio checkpoints;
- distributed portfolio federation;
- clean-room shadow traces;
- full cryptographic digest closure;
- runtime environment profiles;
- release-candidate implementation checkpoints;
- autonomous profile execution;
- L2 runtime import graphs;
- L2 tool execution governance;
- direct code-generation authority.
```

Those belong to later stages if L2 moves beyond profile/spec governance.

Current target:

```text
small, deterministic, inspectable L2 profile/spec registry and graph governance
```

---

## 4. L2 Portfolio Root

The L2 portfolio root is:

```text
L2/
```

All governed paths must be repository-relative POSIX-style paths.

Valid:

```text
L2/docs/00_L2_SYSTEM_GOAL.md
L2/profiles/symbolic_regression_controller.yaml
L2/blueprints/symbolic_regression_controller_blueprint.md
L2/generated/profile_catalog.yaml
```

Invalid:

```text
../L2/docs/00_L2_SYSTEM_GOAL.md
/home/user/Agent_X/L2/docs/00_L2_SYSTEM_GOAL.md
L2\\docs\\00_L2_SYSTEM_GOAL.md
./L2/docs/00_L2_SYSTEM_GOAL.md
```

Rules:

```text
- Paths must be relative to repository root.
- Paths must not escape the repository root.
- Paths must use `/`.
- Paths must not contain unresolved `.` or `..` components.
- Symlinks that resolve outside repository root are invalid.
- Active governed documents must exist and be non-empty unless explicitly marked as allowed sentinels.
```

---

## 5. Required L2 Ecosystem Files

The minimum L2 ES sidecars are:

```text
L2/ecosystem/ecosystem-registry.yaml
L2/ecosystem/ecosystem-graph.yaml
L2/ecosystem/ecosystem-validation-log.md
L2/ecosystem/ecosystem-error-codes.yaml
L2/ecosystem/ecosystem-waivers.yaml
L2/ecosystem/ecosystem-migration-log.md
L2/ecosystem/ecosystem-schemas/
  ecosystem-registry.schema.json
  ecosystem-graph.schema.json
  ecosystem-validation-output.schema.json
  ecosystem-impact-output.schema.json
```

Generated artifacts belong under:

```text
L2/generated/
```

Evidence belongs under:

```text
L2/evidence/
```

The first L2 scaffold may use minimal schemas, but schema files must be real JSON files, not only `.gitkeep` placeholders.

### 5.1 Sidecar Schema Closure

Every required machine-readable L2 ES sidecar must either have an executable schema or be explicitly listed as non-release placeholder in the validator profile.

Required schema coverage for current L2 profile/spec stage:

```text
L2/ecosystem/ecosystem-registry.yaml              -> ecosystem-registry.schema.json
L2/ecosystem/ecosystem-graph.yaml                 -> ecosystem-graph.schema.json
L2/ecosystem/ecosystem-error-codes.yaml           -> ecosystem-error-codes.schema.json
L2/ecosystem/ecosystem-waivers.yaml               -> ecosystem-waivers.schema.json
L2/ecosystem/ecosystem-enums.yaml                 -> ecosystem-enums.schema.json
L2/generated/l2_semantic_lockfile.yaml            -> l2-semantic-lockfile.schema.json
L2/generated/profile_catalog.yaml                 -> profile-catalog.schema.json
L2/generated/profile_package_manifest.yaml        -> profile-package-manifest.schema.json
L2/generated/validation_report.md or .yaml        -> ecosystem-validation-output.schema.json
L2/generated/impact_report.yaml, if present       -> ecosystem-impact-output.schema.json
L2/generated/readiness_report.md or .yaml         -> ecosystem-readiness-output.schema.json
```

Rules:

```text
- A sidecar used as validation evidence must have schema coverage.
- A sidecar without schema coverage may exist only as a bootstrap placeholder.
- Validator output must list enforced and unenforced schemas.
- A profile package proposed to L1 must not depend on an unenforced schema unless the dependency is explicitly marked advisory.
```

---

## 6. Document Types

Every governed L2 document or profile must declare one document type.

Allowed types:

| Type | Meaning |
|---|---|
| `system-goal` | Defines L2 purpose, scope, non-goals, and safety boundaries |
| `background` | Context and rationale |
| `architecture-contract` | L2/L1/L0 boundaries and authority rules |
| `profile-model` | Defines the standard profile schema |
| `specialization-catalog` | Lists available or planned specialization families |
| `integration-boundary` | Defines how L2 may reference L1, L0, or external projects |
| `evaluation-plan` | Defines profile evaluation and readiness checks |
| `risk-ledger` | Tracks L2 risks and accepted limitations |
| `traceability-matrix` | Maps L2 goal → profile → blueprint → evaluation → L1 handoff |
| `handoff-rules` | Defines L2-to-L1 reporting and handoff constraints |
| `profile` | YAML specialization profile |
| `blueprint` | Human-readable specialization design |
| `integration-spec` | External project or cross-layer integration specification |
| `evaluation-spec` | Tests, criteria, or evaluation design for a profile |
| `standard` | L2 lightweight standard document |
| `eqc-procedure` | L2 EQC procedure specification |
| `eqc-operator` | L2 EQC operator specification |
| `generated-catalog` | Generated profile catalog or index |
| `generated-report` | Generated validation/readiness/report artifact |
| `schema` | Machine-readable schema |
| `evidence` | Evidence, validation output, or review record |
| `other` | Allowed only with explicit justification |

`other` must not be used when a specific type applies.

---

## 7. Document and Profile IDs

Every governed L2 artifact must have a stable local ID and global ID.

### 7.1 Portfolio ID

```yaml
portfolio_id: "AGENT_X_L2"
```

### 7.2 Local ID formats

```text
AX-L2-DOC-<TYPE>-<NUMBER>
AX-L2-PROFILE-<NAME>-<NUMBER>
AX-L2-BLUEPRINT-<NAME>-<NUMBER>
AX-L2-INTEGRATION-<NAME>-<NUMBER>
AX-L2-EVAL-<NAME>-<NUMBER>
AX-L2-STANDARD-<NAME>-<NUMBER>
AX-L2-EQC-PROC-<NAME>-<NUMBER>
AX-L2-EQC-OP-<NAME>-<NUMBER>
```

Examples:

```text
AX-L2-DOC-GOAL-001
AX-L2-DOC-PROFILE-MODEL-001
AX-L2-PROFILE-SR-001
AX-L2-BLUEPRINT-SR-001
AX-L2-INTEGRATION-PYSR-001
AX-L2-EVAL-SR-001
```

### 7.3 Global ID formats

```text
GlobalDocID     = AGENT_X_L2::<DocID>
GlobalProfileID = AGENT_X_L2::<ProfileID>
GlobalSpecID    = AGENT_X_L2::<SpecID>
```

Rules:

```text
- IDs must not be reused after deletion.
- Renamed artifacts keep their ID and record path migration.
- Split artifacts receive new IDs and migration records.
- Merged artifacts receive a new ID and record all source IDs.
- Human-readable titles may change; IDs must remain stable.
```

---

## 8. Version Marker Rule

Every governed L2 artifact must contain a version marker matching the registry.

Markdown documents must contain one of:

```text
**Version:** `vX.Y.Z`
Version: vX.Y.Z
Spec Version: vX.Y.Z
```

YAML/JSON documents must contain one of:

```yaml
version: "vX.Y.Z"
spec_version: "vX.Y.Z"
profile_version: "vX.Y.Z"
blueprint_version: "vX.Y.Z"
evaluation_spec_version: "vX.Y.Z"
```

Generated reports must contain:

```text
Generated-From: <source-id>@<version>
Generated-By: <tool-or-process-id>
```

Rules:

```text
- Active artifacts must have matching version markers.
- Missing marker is blocking for active or locked artifacts.
- Mismatch between registry and artifact marker is blocking.
- Historical artifacts may keep old markers but must not be active.
```

---

## 9. Required Ecosystem Registry

The L2 ecosystem registry is:

```text
L2/ecosystem/ecosystem-registry.yaml
```

Minimum schema:

```yaml
ecosystem_registry_version: "L2-lightweight-v0.4"
portfolio_id: "AGENT_X_L2"
status: "active"
documents:
  - doc_id: "AX-L2-DOC-GOAL-001"
    global_doc_id: "AGENT_X_L2::AX-L2-DOC-GOAL-001"
    title: "L2 System Goal"
    type: "system-goal"
    path: "L2/docs/00_L2_SYSTEM_GOAL.md"
    version: "v0.1.0"
    status: "active"
    owner: "l2-control-plane"
    layer: 0
    authority_level: "constitutional"
    functional_digest: "sha256:<pending>"
    metadata_digest: "sha256:<pending>"
    depends_on: []
    governs: []
    recognized_by: []
    source_of_truth_owner: "AX-L2-DOC-GOAL-001"
    allow_empty: false
    generated_from: null
    last_validated_utc: null
```

Required fields:

```text
doc_id
global_doc_id
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
governs
recognized_by
source_of_truth_owner
allow_empty
generated_from
last_validated_utc
```

Rules:

```text
- Every active document must appear in the registry.
- Every active profile must appear in the registry.
- Every active blueprint, integration spec, and evaluation spec must appear in the registry.
- Two active entries must not share the same path.
- Two active entries must not share the same ID.
- Two active profiles must not claim final authority over the same specialization target unless one is explicitly subordinate.
- Generated artifacts must declare `generated_from`.
- Placeholder generated artifacts must not be treated as release evidence.
```

---

## 10. Document Status Values

Allowed statuses:

| Status | Meaning |
|---|---|
| `draft` | Incomplete; not authoritative |
| `reviewed` | Internally coherent but not active |
| `active` | Current authoritative L2 document/profile |
| `locked` | Frozen for L1 handoff package preparation |
| `generated` | Produced by tooling; not manually edited unless authorized |
| `placeholder` | Bootstrap placeholder; not evidence |
| `deprecated` | Superseded but retained for traceability |
| `archived` | Historical only |
| `blocked` | Known inconsistency or unresolved dependency |

Rules:

```text
- Only active or locked profiles may be proposed to L1.
- Draft profiles may be discussed but not handed off as authoritative.
- Placeholder artifacts must not be used as validation evidence.
- Deprecated artifacts may be referenced only for migration or history.
- Blocked artifacts block dependent packages unless explicitly waived.
```

### 10.1 Lifecycle Transition Rules

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
placeholder -> generated only after generator-owned regeneration
```

Forbidden transitions:

```text
draft -> locked
placeholder -> active
archived -> active without migration record
blocked -> locked
generated -> active source authority
```

Rules:

```text
- A transition into active requires registry, graph, path, version-marker, and authority validation.
- A transition into locked requires current graph hash and current lockfile entry.
- A transition into deprecated requires migration, replacement, or historical-retention note.
- A transition out of blocked requires remediation evidence.
- Status changes that alter authority are FUNCTIONAL changes.
```

---

## 11. Authority Levels

Allowed authority levels:

| Authority Level | Meaning |
|---|---|
| `constitutional` | L2 purpose, non-goals, and safety boundaries |
| `architecture` | L2/L1/L0 boundary and layer rules |
| `workflow` | L2 process and lifecycle rules |
| `profile-model` | Profile schema and profile validity rules |
| `profile` | One specialization profile |
| `blueprint` | Human-readable plan attached to a profile |
| `integration` | External or cross-layer integration description |
| `evaluation` | Profile-specific evaluation and readiness criteria |
| `bridge` | L2-to-L1 handoff and binding rule |
| `generated` | Tool-derived state or report |
| `historical` | Retained context only |

Conflict resolution order:

```text
constitutional
  > architecture
  > workflow
  > profile-model
  > profile
  > blueprint
  > integration
  > evaluation
  > bridge
  > generated
  > historical
```

L2 generated artifacts do not override L2 profiles. L2 profiles do not override L1 FICs. L2 never overrides L0.

---

## 12. L2 Layer Model

L2 document layers:

| Layer | Documents |
|---:|---|
| 0 | L2 system goal, constitutional boundaries |
| 1 | Architecture contract, workflow standard, profile model |
| 2 | Profiles, specialization catalog, blueprints |
| 3 | Integration specs, evaluation specs, handoff rules, SIB bridge |
| 4 | Generated catalogs, reports, lockfiles, evidence |

Dependency rule:

```text
A document may depend only on documents in the same or lower layer.
```

Metadata recognition may point upward, but metadata recognition does not create governing authority.

Invalid examples:

```text
L2 system goal depends on generated profile catalog.
L2 profile model depends on a specific profile.
L2 profile depends on unfinished runtime implementation.
L2 profile authorizes L1 code directly.
```

---

## 13. Required Ecosystem Graph

The L2 ecosystem graph is:

```text
L2/ecosystem/ecosystem-graph.yaml
```

Minimum schema:

```yaml
ecosystem_graph_version: "L2-lightweight-v0.4"
portfolio_id: "AGENT_X_L2"
root_doc_id: "AX-L2-DOC-GOAL-001"
nodes:
  - doc_id: "AX-L2-DOC-GOAL-001"
    path: "L2/docs/00_L2_SYSTEM_GOAL.md"
    type: "system-goal"
    layer: 0
edges:
  - src: "AX-L2-DOC-GOAL-001"
    type: "GOVERNS"
    dst: "AX-L2-DOC-PROFILE-MODEL-001"
    payload: {}
```

Allowed edge types:

| Edge | Meaning | Functional? |
|---|---|---:|
| `IMPORTS` | Imports rules or definitions from another artifact | yes |
| `EXTENDS` | Extends another document's semantics | yes |
| `GOVERNS` | Controls another document/profile/spec | yes |
| `USES` | Uses a type, profile, evaluation, or rule | yes |
| `DERIVES` | Generated or derived from another artifact | yes |
| `VALIDATES` | Defines validation for another artifact | yes |
| `PROPOSES_HANDOFF_TO_L1` | L2 profile may be reported to L1 | yes |
| `REFERENCES` | Non-binding citation | no |
| `RECOGNIZES` | Metadata-only discoverability edge | no |
| `SUPERSEDES` | Replacement or deprecation relation | no, unless active authority changes |

Functional edges participate in reachability and cycle checks.

---

## 14. Reachability Rules

Every active L2 document must be reachable from:

```text
AX-L2-DOC-GOAL-001
```

Functional reachability edges:

```text
IMPORTS
EXTENDS
GOVERNS
USES
DERIVES
VALIDATES
PROPOSES_HANDOFF_TO_L1
```

Metadata-only edges ignored for functional reachability:

```text
REFERENCES
RECOGNIZES
SUPERSEDES
```

Blocking conditions:

```text
- Active document is not reachable from root.
- Active profile is reachable only through metadata edges.
- Active profile depends on a deprecated or blocked document.
- Active profile has no authority path to the system goal.
```

---

## 15. Cycle Rules

Cycle detection applies only to functional edges:

```text
IMPORTS, EXTENDS, GOVERNS, USES, DERIVES, VALIDATES, PROPOSES_HANDOFF_TO_L1
```

Rules:

```text
- Functional cycles are blocking.
- REFERENCES, RECOGNIZES, and SUPERSEDES do not participate in cycle detection.
- Every graph node must exist in the registry.
- Every functional graph edge must reference valid registered IDs.
- Graph output must be sorted deterministically by `(src, type, dst)`.
```

### 15.1 Registry/Graph Consistency Rules

The registry and graph must agree.

Blocking inconsistencies:

```text
- registry entry missing from graph nodes while active or locked;
- graph node missing from registry;
- graph node path/type/layer disagrees with registry;
- graph edge references an unknown ID;
- registry `depends_on` does not match functional incoming graph edges when both are declared;
- generated lockfile references a document not present in the current registry and graph;
- active profile has graph reachability but no registry authority level.
```

Resolution requires updating the registry, graph, or document status before the profile package can be proposed to L1.

---

## 16. Profile Ownership and Collision Rules

A profile owns a specialization target when it claims authority to define how that specialization should be described or evaluated.

Collision keys:

```text
specialization_type
external_project_ref
profile_id
blueprint_id
integration_spec_id
evaluation_spec_id
l1_handoff_target
```

Blocking collisions:

```text
- two active profiles claim final authority over the same specialization target;
- two active profiles claim incompatible L1 handoff targets for the same specialization;
- one blueprint is attached to multiple profiles without explicit shared ownership;
- one evaluation spec defines conflicting acceptance criteria for the same profile;
- integration specs disagree about whether external code modification is allowed;
- profile says implementation is allowed while SIB bridge says implementation is forbidden.
```

Resolution options:

```text
- choose one owner and mark the other subordinate;
- split the specialization target;
- merge profiles with a migration note;
- convert one relation to REFERENCE only;
- block the profile package until resolved.
```

---

## 17. Canonical Content and Digest Rules

For digest and comparison purposes, text documents must be canonicalized as:

```text
- UTF-8 encoding;
- LF line endings;
- no byte-order mark;
- trailing whitespace stripped;
- final newline required;
- no unresolved conflict markers.
```

YAML/JSON documents additionally require:

```text
- parse successfully;
- no duplicate keys;
- deterministic key ordering when serialized by validators;
- explicit strings for version numbers;
- UTC timestamps when timestamps are used.
```

Digest format:

```text
sha256:<64 lowercase hex characters>
```

`sha256:<pending>` is allowed only before executable validators exist or for bootstrap placeholders explicitly marked not release evidence.

---

## 18. Digest Classes

### 18.1 Functional Digest

Functional digest changes when governing meaning changes.

Examples:

```text
- profile purpose changed;
- specialization type changed;
- forbidden action changed;
- required L1 units changed;
- evaluation criteria changed;
- integration permission changed;
- handoff eligibility changed;
- status changes into or out of active/locked;
- dependency or authority relation changes.
```

### 18.2 Metadata Digest

Metadata digest changes for non-governing changes.

Examples:

```text
- owner note changed;
- non-binding reference changed;
- formatting changed without semantic effect;
- explanatory wording changed without obligation change.
```

If a change affects obligations, readiness, authority, dependency, or L1 handoff behavior, it is functional.

---

## 19. Resolved L2 Ecosystem Graph Hash

The ecosystem graph must produce a deterministic resolved graph hash.

Canonical graph representation:

```json
{
  "portfolio_id": "AGENT_X_L2",
  "nodes": [
    {"doc_id": "AX-L2-DOC-GOAL-001", "type": "system-goal", "layer": 0, "status": "active"}
  ],
  "edges": [
    {"src": "AX-L2-DOC-GOAL-001", "type": "GOVERNS", "dst": "AX-L2-DOC-PROFILE-MODEL-001", "payload": {}}
  ]
}
```

Rules:

```text
- Nodes sorted by doc_id.
- Edges sorted by `(src, type, dst)`.
- Payload keys sorted recursively.
- Absent payload normalized to `{}`.
- Metadata-only edges may have a separate metadata graph hash.
- Functional and metadata graph hashes must not be mixed.
```

Digest field:

```text
resolved_l2_ecosystem_graph_hash: "sha256:<hash-or-pending>"
```

---

## 20. Change Classification

Allowed classifications:

```text
METADATA
VALIDATION
STATE
FUNCTIONAL
STRUCTURAL
```

Severity order:

```text
METADATA < VALIDATION < STATE < FUNCTIONAL < STRUCTURAL
```

Functional triggers:

```text
TRG_PROFILE_PURPOSE_CHANGED
TRG_SPECIALIZATION_TYPE_CHANGED
TRG_FORBIDDEN_ACTION_CHANGED
TRG_L1_HANDOFF_TARGET_CHANGED
TRG_EVALUATION_CRITERIA_CHANGED
TRG_INTEGRATION_PERMISSION_CHANGED
TRG_PROFILE_STATUS_AUTHORITY_CHANGED
TRG_PROFILE_OWNERSHIP_COLLISION
```

Structural triggers:

```text
TRG_DOC_ID_CHANGED
TRG_PATH_MIGRATION
TRG_GRAPH_EDGE_CHANGED
TRG_REGISTRY_SCHEMA_CHANGED
TRG_ROOT_DOC_CHANGED
TRG_LAYER_RULE_CHANGED
```

Validation triggers:

```text
TRG_EVALUATION_SPEC_CHANGED
TRG_VALIDATION_REPORT_CHANGED
TRG_SCHEMA_ONLY_CHANGED
```

Metadata triggers:

```text
TRG_COMMENT_ONLY_CHANGED
TRG_OWNER_NOTE_CHANGED
TRG_REFERENCE_ONLY_CHANGED
```

---

## 21. Impact Rules

When an L2 artifact changes, compute affected artifacts through functional graph edges.

Impact traversal follows:

```text
IMPORTS
EXTENDS
GOVERNS
USES
DERIVES
VALIDATES
PROPOSES_HANDOFF_TO_L1
```

Impact traversal does not follow:

```text
REFERENCES
RECOGNIZES
SUPERSEDES
```

Required action categories:

```text
NO_ACTION
REVIEW_ONLY
UPDATE_REFERENCE
UPDATE_DEPENDENT_DOC
UPDATE_PROFILE
UPDATE_BLUEPRINT
UPDATE_EVALUATION_SPEC
UPDATE_INTEGRATION_SPEC
UPDATE_GRAPH
UPDATE_REGISTRY
UPDATE_SIB_BRIDGE
REVALIDATE
REGENERATE_PROFILE_CATALOG
REGENERATE_LOCKFILE
BLOCK_L1_HANDOFF
BLOCK_L2_PROFILE_PACKAGE
```

Example:

```yaml
impact_result:
  change: "AX-L2-PROFILE-SR-001@v0.4.0"
  classification: "FUNCTIONAL"
  affected_documents:
    - doc_id: "AX-L2-BLUEPRINT-SR-001"
      required_action: "UPDATE_BLUEPRINT"
      blocking: true
    - doc_id: "AX-L2-EVAL-SR-001"
      required_action: "UPDATE_EVALUATION_SPEC"
      blocking: true
  global_actions:
    - "UPDATE_SIB_BRIDGE"
    - "REGENERATE_PROFILE_CATALOG"
    - "REVALIDATE"
```

### 21.1 Deterministic Impact Output Schema

`l2-es impact` must emit deterministic JSON or YAML.

Minimum fields:

```yaml
impact_result:
  portfolio_id: "AGENT_X_L2"
  l2_eqc_es_version: "v0.4.0"
  change: "AX-L2-PROFILE-SR-001@v0.4.0"
  changed_doc_id: "AX-L2-PROFILE-SR-001"
  classification: "METADATA|VALIDATION|STATE|FUNCTIONAL|STRUCTURAL"
  triggers: []
  affected_documents: []
  affected_profiles: []
  affected_l1_handoff_records: []
  required_global_actions: []
  blocking: true
```

Ordering rules:

```text
- affected documents sorted by ID;
- required actions sorted by severity;
- triggers sorted lexicographically;
- no free-form classification outside the controlled enum registry.
```

---

## 22. Stale Artifact Rules

An L2 artifact is stale when a governing dependency changed after the artifact was last validated.

Staleness sources:

```text
- system goal changed;
- architecture contract changed;
- profile model changed;
- profile changed;
- blueprint changed;
- integration spec changed;
- evaluation spec changed;
- L1 handoff target changed;
- SIB bridge binding changed;
- generated profile catalog changed;
- semantic lockfile changed.
```

Stale active artifacts must be:

```text
REVALIDATED
UPDATED
WAIVED
DOWNGRADED
DEPRECATED
BLOCKED
```

A stale profile must not be handed off to L1.

---

## 23. L2-to-L1 Boundary Rule

L2 may propose profile packages to L1, but L2 must not authorize implementation.

Allowed:

```text
L2 profile -> L2 blueprint -> L2 evaluation spec -> L2 SIB bridge -> L1 handoff candidate
```

Forbidden:

```text
L2 profile -> code implementation
L2 profile -> direct L0 modification
L2 profile -> direct external project patch
L2 generated catalog -> implementation permission
```

L1 is the acceptance authority for implementation. L2 ES may report that a profile package is ready to propose to L1, but it must not claim that implementation is approved.

### 23.1 Profile Package Closure Before L1 Proposal

A selected L2 profile package is closed for L1 proposal only when it includes:

```yaml
l2_profile_package:
  package_id: "AX-L2-PKG-SR-001"
  selected_profile_id: "AX-L2-PROFILE-SR-001"
  profile_path: "L2/profiles/symbolic_regression_controller.yaml"
  blueprint_path: "L2/blueprints/symbolic_regression_controller_blueprint.md"
  evaluation_spec_path: "L2/evaluation_specs/symbolic_regression_eval.md"
  integration_specs: []
  l1_handoff_map: "L2/sib/sib-l1-handoff-map.yaml"
  required_l1_units: []
  forbidden_actions_confirmed: true
  implementation_authority: false
  readiness_status: "ready-to-propose-to-L1|blocked|draft"
```

Blocking closure failures:

```text
- selected profile is not active or locked;
- profile has no blueprint;
- profile has no evaluation spec;
- profile has no SIB bridge binding;
- package claims implementation authority;
- required L1 units are missing or unknown;
- package depends on stale L1 references;
- generated catalog disagrees with source profile.
```

---

## 24. L2 Generated Artifact Policy

Generated artifacts include:

```text
L2/generated/profile_catalog.yaml
L2/generated/profile_package_manifest.yaml
L2/generated/l2_semantic_lockfile.yaml
L2/generated/readiness_report.md
L2/generated/validation_report.md
```

Rules:

```text
- Generated artifacts must identify generator and inputs.
- Bootstrap placeholders must state `bootstrap-placeholder-not-release-evidence`.
- Manual edits to generated artifacts are forbidden unless a maintenance task explicitly permits them.
- Generated artifacts do not override source profiles or docs.
- Placeholder generated artifacts cannot be used as release evidence or L1 handoff acceptance evidence.
```

---

## 25. L2 Semantic Lockfile

The lightweight L2 semantic lockfile is:

```text
L2/generated/l2_semantic_lockfile.yaml
```

Minimum structure:

```yaml
lockfile_version: "L2-lightweight-v0.4"
portfolio_id: "AGENT_X_L2"
status: "bootstrap-placeholder-not-release-evidence"
created_at_utc: null
root_doc_id: "AX-L2-DOC-GOAL-001"
documents:
  - doc_id: "AX-L2-DOC-GOAL-001"
    path: "L2/docs/00_L2_SYSTEM_GOAL.md"
    version: "v0.1.0"
    functional_digest: "sha256:<pending>"
    metadata_digest: "sha256:<pending>"
profiles:
  - profile_id: "AX-L2-PROFILE-SR-001"
    path: "L2/profiles/symbolic_regression_controller.yaml"
    version: "v0.1.0"
    status: "draft"
resolved_l2_ecosystem_graph_hash: "sha256:<pending>"
validation_report: "L2/generated/validation_report.md"
release_evidence: false
```

Profile package handoff to L1 is allowed only when:

```text
- lockfile exists;
- registry validates;
- graph validates;
- selected profile is active or locked;
- selected profile is not stale;
- SIB bridge binding exists;
- readiness report says ready-to-propose-to-L1;
- release_evidence remains false unless a later release process explicitly changes it.
```

---

## 25.1 L2 ES / L2 SIB / L1 Synchronization

L2 ES governs document/profile reachability. L2 SIB/Bridge governs the L2-to-L1 handoff map. L1 remains the implementation authority.

Synchronization is required when any of these change functionally:

```text
L2/profiles/*.yaml
L2/blueprints/*.md
L2/evaluation_specs/*.md
L2/integration_specs/*.md
L2/sib/sib-l1-handoff-map.yaml
L2/generated/profile_catalog.yaml
```

Required actions:

```text
1. Run or record `l2-es impact` for the changed artifact.
2. Update L2 SIB bridge records if L1 units, handoff targets, profile IDs, anchors, or package eligibility changed.
3. Regenerate profile catalog if active profiles changed.
4. Regenerate lockfile if active/locked profile package inputs changed.
5. Block L1 proposal if ES and SIB disagree.
6. Record L1 response only after L1 produces explicit evidence.
```

L2 ES must not claim that L1 accepted a profile unless a L1 handoff response or L1 evidence artifact is referenced by path and digest.

---

## 26. Validator Commands

Minimum future validator command set:

```text
l2-es validate
l2-es impact --change <DocID>@<version>
l2-es registry-check
l2-es graph-check
l2-es profile-readiness-check
l2-es lockfile-check
```

Early scaffold may use a script instead of full CLI, but output must still be deterministic.

Exit codes:

| Exit Code | Meaning |
|---:|---|
| 0 | PASS |
| 1 | FAIL, validation errors found |
| 2 | TOOLING ERROR |

No required check may be silently skipped.

If a check cannot run, output must include:

```yaml
skipped_checks:
  - check: "<name>"
    reason: "<reason>"
    blocking: true
```

### 26.1 Validator Input Manifest

Every validation run must declare its input set.

Minimum manifest:

```yaml
validator_input_manifest:
  validator: "l2-es validate"
  validator_version: "v0.4.0"
  workspace_ref: "local-working-tree-or-commit"
  profile: "agent_x_l2_profile_spec"
  inputs:
    - path: "L2/ecosystem/ecosystem-registry.yaml"
      digest: "sha256:<hash-or-pending>"
    - path: "L2/ecosystem/ecosystem-graph.yaml"
      digest: "sha256:<hash-or-pending>"
    - path: "L2/generated/l2_semantic_lockfile.yaml"
      digest: "sha256:<hash-or-pending>"
    - path: "L2/sib/sib-l1-handoff-map.yaml"
      digest: "sha256:<hash-or-pending>"
```

Validation output without an input manifest is not evidence for L1 proposal readiness.

---

## 27. Validation Output Schema

`l2-es validate` must produce deterministic JSON or YAML.

Minimum schema:

```yaml
validation_result:
  portfolio_id: "AGENT_X_L2"
  l2_eqc_es_version: "v0.4.0"
  status: "PASS|FAIL"
  checked_registry: "L2/ecosystem/ecosystem-registry.yaml"
  checked_graph: "L2/ecosystem/ecosystem-graph.yaml"
  errors: []
  warnings: []
  skipped_checks: []
  unreachable_documents: []
  metadata_only_reachability: []
  stale_documents: []
  orphan_profiles: []
  duplicate_profile_ownership: []
  blocked_documents: []
  digest_mismatches: []
  prohibited_runtime_directories: []
  profile_package_closure: []
  l1_handoff_disagreements: []
  schema_coverage: []
  waivers_used: []
  input_manifest: {}
  resolved_l2_ecosystem_graph_hash: "sha256:<hash-or-pending>"
```

Deterministic ordering:

```text
errors sorted by code, doc_id, path
warnings sorted by code, doc_id, path
document lists sorted lexicographically by doc_id
```

---

## 28. Error Code Registry

Error and warning codes are stored in:

```text
L2/ecosystem/ecosystem-error-codes.yaml
```

Initial codes:

```yaml
error_codes:
  AX_L2_ES_PATH_NOT_FOUND: "Registered artifact path does not exist."
  AX_L2_ES_PATH_ESCAPES_ROOT: "Registered path escapes repository root."
  AX_L2_ES_EMPTY_ARTIFACT: "Registered artifact is empty and not marked allow_empty."
  AX_L2_ES_MISSING_VERSION_MARKER: "Artifact does not declare matching version marker."
  AX_L2_ES_DUPLICATE_DOC_ID: "Two registry entries use the same document ID."
  AX_L2_ES_DUPLICATE_PATH: "Two active artifacts use the same path."
  AX_L2_ES_UNKNOWN_DOC_TYPE: "Document type is not allowed."
  AX_L2_ES_INVALID_STATUS: "Status is not allowed."
  AX_L2_ES_INVALID_LAYER_EDGE: "Functional edge violates layer rules."
  AX_L2_ES_CYCLE_DETECTED: "Functional dependency graph contains a cycle."
  AX_L2_ES_ORPHAN_PROFILE: "Active profile is not reachable from root."
  AX_L2_ES_METADATA_ONLY_REACHABILITY: "Artifact is reachable only through metadata edges."
  AX_L2_ES_STALE_PROFILE: "Profile depends on newer or changed source and was not revalidated."
  AX_L2_ES_DUPLICATE_PROFILE_OWNERSHIP: "Two active profiles claim same specialization authority."
  AX_L2_ES_PROHIBITED_RUNTIME_DIR: "L2 contains unregistered runtime-like directory."
  AX_L2_ES_FALSE_IMPLEMENTATION_AUTHORITY: "L2 artifact claims implementation authority instead of L1 proposal authority."
  AX_L2_ES_SCHEMA_INVALID: "Sidecar does not match schema."
  AX_L2_ES_SILENT_SKIP: "Validator skipped a required check without reporting it."
  AX_L2_ES_REGISTRY_GRAPH_MISMATCH: "Registry and graph disagree about an active artifact."
  AX_L2_ES_PROFILE_PACKAGE_NOT_CLOSED: "Selected profile package is incomplete or inconsistent."
  AX_L2_ES_L1_HANDOFF_STALE: "Profile package references stale or missing L1 handoff target."
  AX_L2_ES_SCHEMA_MISSING: "Required sidecar schema is missing or unenforced."
  AX_L2_ES_LOCKFILE_STALE: "L2 semantic lockfile does not match active registry, graph, or profile package."
```

Unknown error codes are invalid validator output.

---

## 29. Waiver Policy

Waiver file:

```text
L2/ecosystem/ecosystem-waivers.yaml
```

Minimum waiver record:

```yaml
waivers:
  - waiver_id: "AX-L2-ES-WVR-001"
    doc_id: "AX-L2-..."
    waived_rule: "AX_L2_ES_..."
    reason: "..."
    risk: "low|medium|high|critical"
    expires_utc: "YYYY-MM-DDTHH:MM:SSZ"
    approved_by: "user|maintainer|reviewer"
```

Non-waivable conditions:

```text
- profile claims direct implementation authority;
- profile authorizes direct L0 modification;
- active profile has no registry entry;
- active profile has no graph reachability from root;
- duplicate profile ownership is unresolved;
- prohibited runtime directory contains real implementation;
- L1 handoff is claimed accepted without L1 evidence;
- expired waiver.
```

---

## 30. Migration Rules

### 30.1 Move

If a path changes:

```text
- keep the same ID;
- update registry path;
- record old path in migration log;
- update graph payloads if needed;
- regenerate lockfile/catalog.
```

### 30.2 Split

If one profile/spec becomes several:

```text
- original ID becomes deprecated or historical;
- new artifacts receive new IDs;
- migration log records source and targets;
- graph edges are redistributed;
- traceability matrix is updated.
```

### 30.3 Merge

If several artifacts become one:

```text
- merged artifact receives new ID;
- source artifacts become deprecated or historical;
- duplicate ownership is resolved;
- migration log records all sources.
```

### 30.4 Delete

Deleting a governed artifact is allowed only when:

```text
- no active artifact depends on it through functional edges;
- it is not the sole owner of a profile, evaluation, or integration target;
- it is not required by the lockfile;
- migration log records deletion.
```

Otherwise deletion is blocked.

---

## 31. Minimum First L2 ES Slice

For the first L2 scaffold, create at minimum:

```text
L2/ecosystem/ecosystem-registry.yaml
L2/ecosystem/ecosystem-graph.yaml
L2/ecosystem/ecosystem-validation-log.md
L2/ecosystem/ecosystem-error-codes.yaml
L2/ecosystem/ecosystem-waivers.yaml
L2/ecosystem/ecosystem-migration-log.md
L2/ecosystem/ecosystem-enums.yaml
L2/ecosystem/ecosystem-schemas/ecosystem-registry.schema.json
L2/ecosystem/ecosystem-schemas/ecosystem-graph.schema.json
L2/ecosystem/ecosystem-schemas/ecosystem-validation-output.schema.json
L2/ecosystem/ecosystem-schemas/ecosystem-impact-output.schema.json
L2/ecosystem/ecosystem-schemas/ecosystem-error-codes.schema.json
L2/ecosystem/ecosystem-schemas/ecosystem-enums.schema.json
L2/ecosystem/ecosystem-schemas/profile-catalog.schema.json
L2/ecosystem/ecosystem-schemas/profile-package-manifest.schema.json
L2/ecosystem/ecosystem-schemas/l2-semantic-lockfile.schema.json
```

The registry should include at least:

```text
L2/docs/00_L2_SYSTEM_GOAL.md
L2/docs/03_L2_PROFILE_MODEL.md
L2/profiles/symbolic_regression_controller.yaml
L2/blueprints/symbolic_regression_controller_blueprint.md
L2/evaluation_specs/symbolic_regression_eval.md
L2/sib/sib-l1-handoff-map.yaml
L2/generated/profile_catalog.yaml
L2/generated/profile_package_manifest.yaml
L2/generated/l2_semantic_lockfile.yaml
```

---

## 32. Readiness Checklist

L2 ES is ready for profile/spec use when:

```text
[ ] ecosystem registry exists
[ ] ecosystem graph exists
[ ] all active artifacts have unique IDs
[ ] all active paths exist and are non-empty
[ ] all active artifacts have version markers
[ ] all active artifacts have allowed status values
[ ] all active artifacts have allowed document types
[ ] all active artifacts are reachable from root through functional edges
[ ] no forbidden upward functional dependency exists
[ ] no active artifact depends on blocked/deprecated artifacts
[ ] no duplicate profile ownership exists
[ ] no duplicate source-of-truth collision keys exist
[ ] every graph edge endpoint resolves
[ ] no unregistered runtime-like directories exist
[ ] profile catalog exists and is marked generated/placeholder or regenerated by validator
[ ] profile package manifest exists before any L1 proposal
[ ] controlled enum sidecar exists
[ ] L2 semantic lockfile exists
[ ] validation report exists
[ ] SIB bridge exists for any profile proposed to L1
[ ] no false implementation-authority claim exists
```

If any required item fails, L2 profile packages may remain draft but must not be proposed to L1.

---

## 32.1 Release-Blocking / Handoff-Blocking Matrix

| Condition | Blocks L1 Proposal? | Notes |
|---|---:|---|
| Missing ecosystem registry | yes | No governed L2 ecosystem exists |
| Missing ecosystem graph | yes | Reachability cannot be proven |
| Missing root L2 goal | yes | No authority source |
| Active profile path missing | yes | Registry is physically false |
| Version-marker mismatch | yes | Registry and artifact disagree |
| Functional graph cycle | yes | Authority/dependency ambiguity |
| Profile reachable only by metadata edge | yes | False authority path |
| Duplicate profile ownership | yes | Conflicting source of truth |
| Duplicate source-of-truth collision key | yes | Ownership ambiguity |
| Graph edge endpoint missing | yes | Graph does not close |
| Stale generated profile catalog | yes | Derived output may mislead L1 |
| Missing profile package manifest | yes | Package is not closed |
| Prohibited runtime directory with real implementation | yes | L2 exceeded profile/spec stage |
| Missing SIB handoff map for selected profile | yes | L1 proposal cannot be bound |
| Stale L1 handoff target | yes | Proposal may target wrong L1 unit/FIC |
| Generated placeholder used as evidence | yes | False evidence claim |
| Missing optional migration log | no | Warning unless migration is active |
| Metadata typo | no | PATCH impact if semantics unchanged |

---

## 33. Maturity Levels

| Level | Name | Meaning |
|---:|---|---|
| 0 | informal | L2 documents exist but are not registered |
| 1 | registered | L2 docs/profiles have IDs and registry entries |
| 2 | graph-aware | Functional dependencies are represented |
| 3 | validated-scaffold | Registry and graph checks pass |
| 4 | handoff-ready | Selected profile package can be proposed to L1 |
| 5 | release-ready | Not current-stage; requires full validators, digests, and release evidence |

Current Agent_X L2 should target:

```text
Level 3 for first scaffold
Level 4 for selected profile packages
```

Do not target Level 5 until L2 is intentionally upgraded beyond profile/spec governance.

---

## 34. No-False-Claim Rules

L2 ES must not claim:

```text
- L2 implementation exists;
- L2 runtime is operational;
- L2 can modify L0;
- L2 can modify L1;
- L2 profile was accepted by L1 unless L1 evidence exists;
- generated placeholders are release evidence;
- draft profiles are active;
- metadata reachability is functional authority.
```

Allowed claims:

```text
- L2 profile/spec scaffold exists;
- L2 ecosystem registry exists;
- L2 profile package is ready for review;
- L2 profile package is ready to propose to L1;
- L2 release evidence is false by design.
```

---


## 34.1 Profile Catalog Source-of-Truth Partitioning

`L2/generated/profile_catalog.yaml` is a derived index, not a source authority.

Authoritative sources for catalog content:

```text
profile identity             -> L2/profiles/*.yaml
profile lifecycle status     -> L2/ecosystem/ecosystem-registry.yaml
blueprint binding            -> L2/ecosystem/ecosystem-graph.yaml and L2/sib/sib-bindings.yaml
evaluation binding           -> L2/ecosystem/ecosystem-graph.yaml and L2/sib/sib-bindings.yaml
L1 handoff target            -> L2/sib/sib-l1-handoff-map.yaml
readiness decision           -> L2/generated/readiness_report.md or .yaml, generated by validator
```

Rules:

```text
- A generated catalog must not introduce a profile absent from the registry.
- A generated catalog must not upgrade profile status.
- A generated catalog must not add L1 handoff authority.
- If catalog and source profile disagree, the source profile and registry win.
- If catalog and SIB handoff map disagree, L1 proposal is blocked until both are reconciled.
- Manual edits to the catalog are invalid unless an explicit maintenance task records the reason and affected inputs.
```

Minimum catalog row:

```yaml
profile_catalog_entry:
  profile_id: "AX-L2-PROFILE-SR-001"
  profile_path: "L2/profiles/symbolic_regression_controller.yaml"
  registry_status: "active|locked|draft|blocked|deprecated"
  blueprint_refs: []
  evaluation_refs: []
  integration_refs: []
  l1_handoff_refs: []
  generated_from_inputs: []
  source_digest_status: "pending|computed|stale"
  l1_proposal_eligible: false
```

## 34.2 Digest Maturity Levels

L2 ES must distinguish scaffold digest placeholders from validator-produced digests.

Allowed digest maturity values:

```text
D0_PENDING_PLACEHOLDER       digest is pending and not evidence
D1_COMPUTED_LOCAL            digest computed locally without full validator closure
D2_VALIDATOR_COMPUTED        digest computed by declared validator with input manifest
D3_LOCKED_HANDOFF_PACKAGE    digest participates in a profile package proposed to L1
D4_RELEASE_EVIDENCE          not current-stage; reserved for future release-grade L2
```

Rules:

```text
- First L2 scaffold may use D0 or D1.
- A profile package proposed to L1 should use D2 or D3 for all required inputs.
- D0 artifacts must not be used as readiness evidence.
- D4 must not be claimed in the current L2 profile/spec stage.
- Validation output must report the minimum digest maturity across all checked required artifacts.
```

Validation output field:

```yaml
digest_maturity:
  minimum_required_for_l1_proposal: "D2_VALIDATOR_COMPUTED"
  minimum_observed: "D0_PENDING_PLACEHOLDER|D1_COMPUTED_LOCAL|D2_VALIDATOR_COMPUTED|D3_LOCKED_HANDOFF_PACKAGE"
  blocking: true
```

## 34.3 Schema Fixture Requirements

Every executable schema used by L2 ES validation must have at least one valid fixture and at least one invalid fixture when the schema is used for profile-package or L1-proposal evidence.

Fixture paths:

```text
L2/ecosystem/ecosystem-schemas/fixtures/valid/<schema-name>/*.yaml
L2/ecosystem/ecosystem-schemas/fixtures/invalid/<schema-name>/*.yaml
```

Each invalid fixture must declare its intended failing error code:

```yaml
fixture_intent:
  schema: "ecosystem-registry.schema.json"
  expected_error_code: "AX_L2_ES_DUPLICATE_DOC_ID"
  reason: "Two active registry entries use the same doc_id."
```

Rules:

```text
- Missing fixtures are warnings for early scaffold.
- Missing fixtures are blocking for a selected profile package proposed to L1.
- Invalid fixtures that pass validation indicate schema weakness and must block readiness claims.
- Fixture results must be included in validation output when schemas are claimed executable.
```

## 34.4 Bridge Synchronization Blocking Rule

L2 ES and L2 SIB/Bridge must agree before any profile package is proposed to L1.

Blocking disagreements:

```text
- ES says profile is active/locked but SIB has no binding.
- SIB has a profile binding for a profile absent from ES registry.
- ES graph includes PROPOSES_HANDOFF_TO_L1 but SIB handoff map marks implementation_allowed false without proposal eligibility.
- SIB handoff target references an L1 unit/FIC not recorded in ES profile package manifest.
- ES generated catalog says eligible but SIB bridge says stale, blocked, or unresolved.
```

Resolution:

```text
1. Update the ES registry or graph.
2. Update the SIB handoff map or bindings.
3. Regenerate profile catalog and readiness report.
4. Re-run validation or record a blocking skipped check.
5. Do not propose the package to L1 until disagreement is cleared.
```

## 34.5 Post-Scaffold Validation Bundle

After creating or updating the first L2 ES scaffold, produce a validation bundle under:

```text
L2/evidence/bootstrap/<utc_timestamp>_l2_es_validation_bundle.yaml
```

Minimum fields:

```yaml
l2_es_validation_bundle:
  portfolio_id: "AGENT_X_L2"
  l2_eqc_es_version: "v0.4.0"
  mode: "L2 profile/spec scaffold"
  workspace_ref: "<commit-or-local-working-tree>"
  commands_run: []
  files_checked: []
  schema_results: []
  registry_graph_consistency: "pass|fail|not-run"
  profile_package_closure: "pass|fail|not-run"
  l2_sib_bridge_sync: "pass|fail|not-run"
  prohibited_runtime_directory_scan: "pass|fail|not-run"
  digest_maturity_minimum_observed: "D0_PENDING_PLACEHOLDER|D1_COMPUTED_LOCAL|D2_VALIDATOR_COMPUTED|D3_LOCKED_HANDOFF_PACKAGE"
  l1_proposal_allowed: false
  release_evidence: false
```

Rules:

```text
- The bundle may report not-run checks, but each not-run check must include a reason.
- The bundle must not claim release evidence in the current stage.
- The bundle must not claim L1 acceptance.
```

## 34.6 Weaker-Agent Final Response Contract

A weaker implementation or scaffolding agent working from this standard must end with exactly one controlled status:

```text
BLOCKED
SCAFFOLD_CREATED_UNVALIDATED
SCAFFOLD_VALIDATED
READY_TO_PROPOSE_PROFILE_TO_L1
REJECTED_SCOPE_DRIFT
```

Required final response fields:

```yaml
final_response:
  status: "BLOCKED|SCAFFOLD_CREATED_UNVALIDATED|SCAFFOLD_VALIDATED|READY_TO_PROPOSE_PROFILE_TO_L1|REJECTED_SCOPE_DRIFT"
  files_created: []
  files_modified: []
  files_inspected: []
  checks_run: []
  checks_not_run: []
  l1_proposal_allowed: false
  release_evidence: false
  unresolved_blockers: []
```

No other final status is allowed for current-stage L2 ES tasks.

## 34.7 Final Status Decision Table

| Observed State | Required Status |
|---|---|
| Required L2 ES files missing | `BLOCKED` |
| Files created but checks not run | `SCAFFOLD_CREATED_UNVALIDATED` |
| Registry, graph, schemas, and runtime-directory scan pass for scaffold | `SCAFFOLD_VALIDATED` |
| Selected active/locked profile package closes and ES/SIB agree | `READY_TO_PROPOSE_PROFILE_TO_L1` |
| L2 runtime code appears without explicit upgrade | `REJECTED_SCOPE_DRIFT` |
| Generated placeholder used as evidence | `BLOCKED` |
| L2 claims direct implementation authority | `REJECTED_SCOPE_DRIFT` |
```


## 35. Final Self-Assessment Gate

This document may be rated complete for the current L2 profile/spec stage only if:

```text
[ ] it defines L2 registry requirements
[ ] it defines L2 graph requirements
[ ] it defines document/profile IDs
[ ] it defines path and version-marker rules
[ ] it defines reachability and cycle rules
[ ] it defines profile ownership/collision rules
[ ] it defines generated artifact policy
[ ] it defines L2-to-L1 boundary rules
[ ] it defines validation output expectations
[ ] it defines error-code rules
[ ] it defines minimum first scaffold slice
[ ] it defines registry/graph consistency rules
[ ] it defines graph endpoint closure rules
[ ] it defines source-of-truth collision keys
[ ] it defines generated catalog consistency rules
[ ] it defines profile-package closure before L1 proposal
[ ] it defines validator input manifest requirements
[ ] it defines schema closure requirements
[ ] it defines controlled enum registry requirements
[ ] it defines a handoff-blocking matrix
[ ] it defines profile-catalog source-of-truth partitioning
[ ] it defines digest maturity levels
[ ] it defines schema fixture requirements
[ ] it defines ES/SIB bridge synchronization blocking rules
[ ] it defines post-scaffold validation bundle requirements
[ ] it defines weaker-agent final response discipline
[ ] it blocks false implementation authority
[ ] it avoids full production EQC-ES burden
```

Current self-assessment:

```text
Document-standard completeness for current L2 profile/spec stage: 10/10
Tooling implementation maturity: early scaffold
Release-readiness: not applicable yet
```

This rating applies to the standard document only. It does not claim that executable L2 validators or release-grade evidence already exist.

---

## 36. Anti-Bloat Boundary

Stop expanding this L2 ES document unless one of these occurs:

```text
- L2 gains real runtime implementation;
- L2 profiles become release-bound artifacts;
- L2 starts producing executable handoff packages automatically;
- L2 validators need stricter schema requirements;
- L2 needs signed checkpoint/release evidence;
- L2 begins managing multiple external project integrations at once.
```

Until then, keep L2 ES lightweight.
