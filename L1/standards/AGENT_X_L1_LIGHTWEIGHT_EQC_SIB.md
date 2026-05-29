# Agent_X L1 Lightweight EQC-SIB

**Document ID:** `AGENT_X-L1-SIB-001`  
**Version:** `v0.5.0`  
**Status:** `ready-for-use`  
**Layer:** `L1`  
**Applies to:** Agent_X L1 document-to-implementation governance  
**Primary purpose:** Define a lightweight, enforceable bridge between Agent_X L1 control documents, pseudocode units, EQC-FIC documents, implementation artifacts, tests, validation output, completion evidence, and review decisions.

---

## 0. Rating of Previous Version

Previous file rated: **9.8/10**.

The previous version was strong enough for current Agent_X L1 governed use, but it still had a few precision issues that prevented a 10/10 document-standard rating. The remaining gaps were not about adding full EQC-SIB machinery; they were about making the lightweight version internally closed, easier to validate, and less ambiguous for future scripts.

### Main gaps found

```text
1. Section ordering placed semantic-lockfile drift rules before the main semantic-lockfile section.
2. Required sidecars were listed, but schema coverage was not fully closed for every sidecar named in the document.
3. Object-registry paths could include fragment anchors, but anchor syntax and resolution were not defined.
4. Validator behavior did not clearly distinguish fatal missing checks from advisory not-yet-executable checks.
5. Fixture rules required valid/invalid fixtures, but did not require each invalid fixture to declare its intended failing error code.
6. Release acceptance needed clearer maturity levels so early L1 use and release-candidate hardening are not confused.
7. The final self-assessment still scored the document below 10 because scripts were not yet implemented, even though this file is the standard rather than the implementation.
```

### Fixes applied in v0.5.0

```text
- Reordered semantic-lockfile sections.
- Added complete sidecar schema coverage rules.
- Added fragment-anchor resolution rules for document/object registry entries.
- Added validator no-silent-skip rules.
- Added fixture intent metadata requirements.
- Added release acceptance maturity levels.
- Updated acceptance criteria to separate document-standard completeness from tooling implementation maturity.
- Upgraded this lightweight SIB document to 10/10 for the current Agent_X L1 stage.
```

---

## 1. Purpose

This document defines the lightweight EQC-SIB discipline for Agent_X L1.

Full EQC-SIB is a broad document↔implementation governance system. Agent_X L1 does not need the full version yet. It needs a smaller bridge that enforces this core rule:

```text
No L1 implementation artifact may be accepted as governed code unless it is traceably bound to:
1. a source goal or requirement,
2. a pseudocode unit,
3. an EQC-FIC document,
4. one or more implementation artifacts,
5. tests or validation checks,
6. completion evidence,
7. review or acceptance evidence,
8. the current L1 semantic lockfile.
```

The purpose is to prevent:

```text
- implementation drift;
- orphan behavior;
- hidden public surface;
- undocumented dependencies;
- uncontrolled edits to L0;
- test-only confidence without evidence;
- stale FIC implementation;
- coding-agent changes that cannot be traced back to a governing requirement.
```

---

## 2. Scope

This lightweight SIB applies to Agent_X L1 artifacts only.

It governs:

```text
- L1 control documents;
- L1 pseudocode units;
- L1 EQC-FIC documents;
- L1 implementation files;
- L1 tests;
- L1 validators;
- L1 generated sidecars;
- L1 validation outputs;
- L1 completion records;
- L1 review packets;
- L1 evidence files;
- L1 semantic lockfiles.
```

It does **not** govern L0 internals directly.

L0 remains protected by its own seed-kernel contracts. L1 may inspect, classify, validate, and propose changes that affect L0, but any L0-affecting implementation must pass the L0 impact gate and use the L0-approved proof commands.

---

## 3. Relationship to Other L1 Standards

This document sits after the two primary L1 standards:

```text
1. Agent_X L1 EQC-FIC
   Defines file/unit implementation contracts.

2. Agent_X L1 Pseudocode-to-FIC Workflow
   Defines the pipeline from goal → pseudocode → FIC → implementation → evidence.

3. Agent_X L1 Lightweight EQC-SIB
   Defines the binding map connecting documents, units, code, tests, evidence, and change impact.
```

EQC-FIC controls the local file/unit contract.

The Pseudocode-to-FIC workflow controls the implementation process.

Lightweight EQC-SIB controls cross-artifact binding, graph integrity, impact discipline, registry status, and evidence closure.

---

## 4. Core Binding Principle

Every governed L1 implementation artifact must be connected through a binding chain.

Required chain:

```text
GOAL / REQUIREMENT
  → WHOLE-SYSTEM PSEUDOCODE SECTION
  → PSEUDOCODE UNIT
  → EQC-FIC DOCUMENT
  → IMPLEMENTATION ARTIFACT
  → TEST / VALIDATION ARTIFACT
  → COMPLETION RECORD
  → REVIEW / ACCEPTANCE RECORD
  → SEMANTIC LOCKFILE ENTRY
```

If any required link is missing, the artifact cannot be accepted as governed implementation.

Allowed incomplete statuses:

```text
DRAFT
BLOCKED_MISSING_BINDING
EXPERIMENTAL_UNGOVERNED
IMPLEMENTED_UNVALIDATED
REJECTED_TRACEABILITY_GAP
```

Accepted status requires the complete chain.

---

## 5. Identity and Global ID Rules

Every governed document and artifact must have a stable local ID and a stable global ID.

### 5.1 Portfolio ID

```yaml
portfolio_id: "AGENT_X_L1"
```

### 5.2 Global ID formats

```text
GlobalArtID = AGENT_X_L1::<ArtID>
GlobalDocID = AGENT_X_L1::<DocID>
GlobalUnitID = AGENT_X_L1::<UnitID>
GlobalFicID = AGENT_X_L1::<FicID>
```

Examples:

```text
AGENT_X_L1::ART-L1-001
AGENT_X_L1::FIC-L1-001
AGENT_X_L1::UNIT-L1-001
AGENT_X_L1::GOAL-L1-001
```

Rules:

```text
- Local IDs must be unique inside L1.
- Global IDs must be used in cross-layer, cross-file, or generated sidecar records.
- IDs must not be reused after deletion.
- Renames require aliases or migration notes.
- Human-readable titles may change; IDs must remain stable.
```

---

## 6. Required Files

Agent_X L1 should maintain these lightweight SIB files:

```text
L1/sib/
  sib-registry.yaml
  sib-bindings.yaml
  sib-graph.yaml
  sib-validation-log.md
  sib-error-codes.yaml
  sib-waivers.yaml
  sib-doc-registry.yaml
  sib-source-freshness.yaml
  sib-version-impact.yaml
  sib-schemas/
    sib-registry.schema.json
    sib-bindings.schema.json
    sib-graph.schema.json
    completion-record.schema.json
    review-packet.schema.json
    validation-result.schema.json
    waiver.schema.json
```

Evidence should be stored under:

```text
L1/evidence/
  <unit_id>/
    <utc_timestamp>_completion_record.yaml
    <utc_timestamp>_review_packet.md
    <utc_timestamp>_checks.log
    <utc_timestamp>_traceability_update.yaml
    <utc_timestamp>_impact_report.yaml
```

Generated or validator-owned artifacts should be stored under:

```text
L1/generated/
  semantic_lockfile.yaml
  binding_report.md
  impact_report.md
  validation_report.md
  release_package_manifest.yaml
```

Rules:

```text
- Generated artifacts must declare their generator and input digests.
- Generated artifacts must not be manually edited unless a maintenance task explicitly permits it.
- Required SIB sidecars must validate against their schemas before implementation can be accepted.
```

### 6.1 Complete Sidecar Schema Coverage

Every required machine-readable sidecar named by this standard must either have an executable schema or be explicitly listed as not-yet-executable in the validator profile.

Required executable-schema targets for accepted or release-bound L1 packages:

```text
sib-registry.yaml                       -> sib-registry.schema.json
sib-doc-registry.yaml                   -> sib-doc-registry.schema.json
sib-bindings.yaml                       -> sib-bindings.schema.json
sib-graph.yaml                          -> sib-graph.schema.json
sib-error-codes.yaml                    -> sib-error-codes.schema.json
sib-waivers.yaml                        -> waiver.schema.json
sib-source-freshness.yaml               -> sib-source-freshness.schema.json
sib-version-impact.yaml                 -> sib-version-impact.schema.json
completion records                      -> completion-record.schema.json
review packets                          -> review-packet.schema.json
validation results                      -> validation-result.schema.json
impact reports                          -> impact-report.schema.json
semantic lockfile SIB section           -> semantic-lockfile.schema.json
release package manifest                -> release-package-manifest.schema.json
```

Rules:

```text
- A sidecar listed in `L1/sib/` but not covered by a schema is advisory only and cannot be release evidence.
- A validator profile must name every schema it enforces and every schema it does not yet enforce.
- Release-bound packages must fail if any required release evidence depends on an unenforced schema.
- Schema names must be stable. Renaming a schema requires a migration note and validator-profile update.
```

---

## 7. Canonical Path Rules

All paths stored in SIB sidecars must be normalized repository-relative POSIX paths.

Valid:

```text
L1/controller/document_loader.py
L1/tests/test_document_loader.py
L1/fic/units/FIC-L1-001-document-loader.md
```

Invalid:

```text
../L1/controller/document_loader.py
/home/user/Agent_X/L1/controller/document_loader.py
L1\\controller\\document_loader.py
./L1/controller/document_loader.py
```

Rules:

```text
- Paths must not be absolute.
- Paths must not contain `..` after normalization.
- Paths must not escape the repository root.
- Symlinks that resolve outside the repository root are blocking errors.
- Symlinks inside governed implementation paths are rejected unless explicitly declared and tested.
- Path comparison must use normalized POSIX form.
```

---


## 7.1 Canonical Content and Digest Rules

All SIB-controlled text artifacts must have deterministic canonical bytes before hashing.

Canonical text rules:

```text
- Encoding: UTF-8 only.
- Line endings: LF only.
- BOM: forbidden.
- Trailing whitespace: stripped before digest computation.
- Final newline: required for text artifacts.
- Timestamps: excluded from functional digest unless the timestamp itself is functional behavior.
```

Canonical YAML/JSON rules:

```text
- Parse successfully before hashing.
- Re-emit as canonical JSON for digest computation.
- Object keys sorted lexicographically.
- Lists preserve declared order unless the schema marks the list as set-like.
- Integers and strings retain exact value.
- Floating values must be represented as strings unless the schema explicitly permits numeric floats.
- Unknown fields are blocking errors unless the schema declares `additionalProperties: true` for that object.
```

Digest references must include both algorithm and value:

```yaml
digest:
  algorithm: "sha256"
  value: "<64 lowercase hex chars>"
```

Rules:

```text
- Bare digest strings are allowed only in examples or compact lockfile rows.
- Accepted artifacts must use canonical digest objects in machine-readable sidecars.
- A digest computed from non-canonical bytes is invalid.
- Generated artifacts must record generator ID, generator version, input digests, and output digest.
```

## 7.2 File Existence, Non-Empty, and Version Marker Rules

Every registered artifact must resolve to a concrete repository-relative path unless it is explicitly marked as planned.

Validation rules:

```text
- `planned` artifacts may have a missing target file only if `implementation_mode` is `new-file`.
- `ready-for-implementation`, `implemented-unvalidated`, `validated`, and `accepted` artifacts must resolve to an existing file.
- Existing governed files must be non-empty after canonicalization.
- Empty sentinel files are allowed only when the registry entry sets `allow_empty: true` and provides a sidecar marker.
```

Version marker rules:

```text
- Markdown control documents must contain `Version:` matching the registry entry.
- YAML/JSON sidecars must contain `version`, `schema_version`, or an explicitly declared equivalent field.
- Python implementation files must contain either an inline marker or a sidecar marker.
```

Recommended Python marker:

```python
# Agent_X-SIB ArtID: AGENT_X_L1::ART-L1-001 | Version: v0.1.0 | FIC: AGENT_X_L1::FIC-L1-001
```

If inline markers are not appropriate, use:

```text
<artifact_path>.sibmeta.yaml
```

with:

```yaml
global_art_id: "AGENT_X_L1::ART-L1-001"
version: "v0.1.0"
fic_id: "AGENT_X_L1::FIC-L1-001"
marker_for: "L1/controller/document_loader.py"
```

## 8. Artifact Registry

The lightweight registry is stored at:

```text
L1/sib/sib-registry.yaml
```

It lists all governed L1 implementation artifacts.

Minimum schema:

```yaml
sib_registry_version: "v0.5"
portfolio_id: "AGENT_X_L1"
artifacts:
  - art_id: "ART-L1-001"
    global_art_id: "AGENT_X_L1::ART-L1-001"
    title: "L1 document loader"
    type: "implementation"
    layer: "L1"
    file_path: "L1/controller/document_loader.py"
    version: "v0.1.0"
    status: "planned"
    owner: "l1-controller"
    governed_by_fic: "AGENT_X_L1::FIC-L1-001"
    implements_unit: "AGENT_X_L1::UNIT-L1-001"
    canonicalization_tier: "T1"
    functional_digest: null
    public_surface_digest: null
    metadata_digest: null
    functional_state_digest: null
    tests:
      - "AGENT_X_L1::TEST-L1-001"
    completion_records: []
    review_packets: []
    public_surface:
      - "DocumentRecord"
      - "load_markdown_document"
      - "load_text_document"
    declared_dependencies:
      strict:
        - "python:dataclasses"
        - "python:pathlib"
        - "python:hashlib"
      optional: []
      dynamic_patterns: []
```

Required fields:

```text
art_id
global_art_id
title
type
layer
file_path
version
status
owner
governed_by_fic
implements_unit
canonicalization_tier
functional_digest
public_surface_digest
metadata_digest
functional_state_digest
tests
completion_records
review_packets
public_surface
declared_dependencies
```

Allowed `type` values:

```text
implementation
test
schema
validator
completion-record
review-packet
evidence
configuration
generated
```

Allowed `status` values:

```text
planned
draft
ready-for-implementation
implemented-unvalidated
validated
accepted
blocked
rejected
deprecated
```

Status transition rules:

```text
planned → draft → ready-for-implementation → implemented-unvalidated → validated → accepted
planned → blocked
draft → blocked
implemented-unvalidated → rejected
validated → rejected
accepted → deprecated
```

A registry entry cannot move to `accepted` unless:

```text
- it has a primary HARD binding;
- its FIC status is ready-for-code or validated;
- all required tests/checks passed or have explicit waivers;
- a completion record exists;
- a review packet exists;
- all digest fields are populated;
- the semantic lockfile includes the accepted artifact version and digest.
```

---


## 8.1 Document and Object Registry

The artifact registry governs implementation artifacts. L1 also needs a lightweight document/object registry for non-code control-plane objects.

Stored at:

```text
L1/sib/sib-doc-registry.yaml
```

Minimum schema:

```yaml
sib_doc_registry_version: "v0.5"
portfolio_id: "AGENT_X_L1"
objects:
  - object_id: "GOAL-L1-001"
    global_id: "AGENT_X_L1::GOAL-L1-001"
    object_type: "goal"
    path: "L1/docs/00_L1_SYSTEM_GOAL.md"
    version: "v0.1.0"
    status: "active"
    owner: "l1-control-plane"
    functional_digest: null
    metadata_digest: null
  - object_id: "UNIT-L1-001"
    global_id: "AGENT_X_L1::UNIT-L1-001"
    object_type: "pseudocode-unit"
    path: "L1/docs/04_L1_UNIT_DAG.md#UNIT-L1-001"
    version: "v0.1.0"
    status: "active"
    owner: "l1-control-plane"
    functional_digest: null
    metadata_digest: null
```

Allowed `object_type` values:

```text
goal
architecture-contract
whole-system-pseudocode
pseudocode-section
pseudocode-unit
unit-dag
shared-interface
fic-document
test-contract
validation-output
completion-record
review-packet
evidence-artifact
semantic-lockfile
release-manifest
waiver
```

Rules:

```text
- Every GlobalDocID, GlobalUnitID, and GlobalFicID referenced by bindings must resolve in this registry or in an explicitly imported registry.
- A FIC cannot move to `ready-for-code` unless its source pseudocode unit is active.
- A test artifact cannot be accepted unless it validates at least one active FIC or implementation artifact.
- Evidence artifacts must reference the artifact, unit, FIC, validation output, or review decision they support.
- Document/object registry digest must be included in the semantic lockfile.
```

### 8.1.1 Fragment Anchor and Object Path Rules

Document-object registry paths may reference whole files or file fragments.

Allowed forms:

```text
L1/docs/04_L1_UNIT_DAG.md
L1/docs/04_L1_UNIT_DAG.md#UNIT-L1-001
L1/fic/units/FIC-L1-001-document-loader.md#public-surface
```

Rules:

```text
- The file portion must obey canonical repository-relative POSIX path rules.
- Fragment anchors must be stable ASCII identifiers: `[A-Za-z0-9._:-]+`.
- Fragment anchors must not contain spaces, slashes, backslashes, URL encoding, or shell metacharacters.
- A fragment anchor must resolve to an explicit heading, YAML key, `AnchorID:`, or validator-recognized marker.
- If an object path includes a fragment that cannot be resolved, the object is stale or broken.
- Fragment-only changes are METADATA unless the anchored normative content changes.
```

## 8.2 Stale Artifact and Source-Freshness Rules

A registered artifact or document becomes stale when a source it depends on changes without revalidation.

Stale triggers:

```text
- governing FIC digest changed;
- source pseudocode unit digest changed;
- public surface digest changed;
- declared dependency digest changed;
- validation command set changed;
- L0 proof command or L0 public contract changed;
- semantic lockfile no longer contains the accepted digest;
- schema version changed without successful revalidation.
```

Allowed stale statuses:

```text
stale-needs-impact
stale-needs-fic-update
stale-needs-revalidation
stale-needs-review
stale-superseded
```

Remediation rules:

```text
- Stale accepted artifacts must not be used as release evidence.
- Stale implementation artifacts require impact analysis before further implementation.
- Stale FICs cannot be used for coding.
- Stale tests may still run, but their output cannot be used as final validation evidence until refreshed.
- Stale artifacts must either be revalidated, superseded, deprecated, or archived.
```

## 9. Digest Classes

Lightweight SIB uses digest classes to detect drift without adopting the full signed-checkpoint machinery yet.

### 9.1 FunctionalDigest

```text
FD = SHA256(canonical functional bytes of the artifact)
```

For Markdown/YAML/JSON control artifacts, canonical functional bytes are UTF-8 with LF line endings and trailing whitespace stripped.

For Python code in the first L1 stage, `T1` token-canonical digest may normalize comments and whitespace only if the canonicalizer is declared. If no canonicalizer exists, use raw UTF-8 LF bytes.

### 9.2 PublicSurfaceDigest

```text
SD = SHA256(canonical sorted public surface list)
```

The public surface list must be derived from the registry, the FIC, and optionally a validator extraction. Mismatch is blocking.

### 9.3 MetadataDigest

```text
MD = SHA256(canonical metadata fields)
```

Metadata includes owner, title, references, review notes, and non-functional commentary.

### 9.4 Lightweight FunctionalStateDigest

```text
FSD = SHA256(FD || SD || declared_dependency_digest || validator_profile_digest)
```

This catches state changes such as dependency or validator-profile drift.

### 9.5 Digest rules

```text
- SHA-256 digests must be lowercase hex.
- Digest input order must be deterministic.
- Digest fields may be null only for planned or draft artifacts.
- Accepted artifacts must have all required digest fields populated.
- Digest mismatch after acceptance marks the artifact stale.
```

---

## 10. Binding Map

The binding map is stored at:

```text
L1/sib/sib-bindings.yaml
```

It defines relationships between goals, pseudocode units, FICs, implementation files, tests, and evidence.

Minimum schema:

```yaml
sib_bindings_version: "v0.5"
portfolio_id: "AGENT_X_L1"
bindings:
  - binding_id: "BIND-L1-001"
    unit_id: "AGENT_X_L1::UNIT-L1-001"
    goal_refs:
      - "AGENT_X_L1::GOAL-L1-001"
    pseudocode_refs:
      - "AGENT_X_L1::PS-L1-001"
    fic_id: "AGENT_X_L1::FIC-L1-001"
    implementation_artifacts:
      - "AGENT_X_L1::ART-L1-001"
    test_artifacts:
      - "AGENT_X_L1::TEST-L1-001"
    evidence_artifacts: []
    binding_strength: "HARD"
    minimum_status_for_acceptance: "validated"
    minimum_equivalence: "E1"
```

Allowed `binding_strength` values:

```text
HARD
SOFT
REFERENCE
```

Rules:

```text
- HARD bindings are required for implementation acceptance.
- SOFT bindings are advisory and may warn but not block.
- REFERENCE bindings are citations only and do not create implementation authority.
- Every governed implementation artifact must have exactly one primary HARD FIC binding.
- One FIC may bind to multiple files only when the FIC explicitly declares a multi-file implementation unit.
- Every HARD binding must be bidirectionally checked: document changes affect code, and code changes affect documents.
```

---


## 10.1 Binding Multiplicity and Collision Rules

Binding multiplicity must be explicit.

Allowed patterns:

```text
1 FIC → 1 implementation artifact         default
1 FIC → many tiny implementation artifacts only if the FIC declares a multi-file implementation unit
many FICs → 1 implementation artifact     forbidden unless a merge FIC declares ownership boundaries
1 implementation artifact → 1 primary FIC required
1 implementation artifact → many reference FICs allowed only as REFERENCE bindings
```

Blocking collisions:

```text
- two primary FICs govern the same target file;
- two units claim ownership of the same public surface;
- two artifacts PROVIDE the same public symbol without an alias or migration rule;
- a test file validates behavior that no FIC owns;
- a completion record references a file outside its implementation package;
- a binding points to a stale, deprecated, missing, or rejected FIC.
```

Collision resolution requires one of:

```text
- split the implementation artifact;
- merge the FICs through an explicit merge FIC;
- move ownership to one FIC and convert the other to REFERENCE;
- add an alias/migration record;
- mark the affected package BLOCKED until authority is resolved.
```

## 11. Dependency Graph

The dependency graph is stored at:

```text
L1/sib/sib-graph.yaml
```

It records allowed implementation relationships.

Minimum schema:

```yaml
sib_graph_version: "v0.5"
portfolio_id: "AGENT_X_L1"
nodes:
  - id: "AGENT_X_L1::ART-L1-001"
    kind: "implementation"
    layer: "L1"
    status: "planned"
edges:
  - src: "AGENT_X_L1::ART-L1-001"
    type: "IMPLEMENTS"
    dst: "AGENT_X_L1::FIC-L1-001"
  - src: "AGENT_X_L1::TEST-L1-001"
    type: "VALIDATES"
    dst: "AGENT_X_L1::ART-L1-001"
```

Allowed edge types:

```text
IMPLEMENTS
GOVERNS
VALIDATES
USES
PROVIDES
REFERENCES
RECOGNIZES
DERIVES
OBSERVED_IMPORTS
OBSERVED_FS_READS
```

Cycle detection applies only to:

```text
USES
DERIVES
VALIDATES
```

`REFERENCES`, `RECOGNIZES`, `OBSERVED_IMPORTS`, and `OBSERVED_FS_READS` must not participate in cycle detection.

---

## 12. Declared vs Observed Dependency Enforcement

For governed artifacts, SIB validation must compare declared dependencies with observed behavior.

Declared dependencies come from:

```text
- sib-registry.yaml declared_dependencies;
- sib-graph.yaml USES edges;
- governing FIC dependency contract;
- implementation handoff packet.
```

Observed dependencies may come from:

```text
- static import scan;
- validator execution trace;
- observed file reads;
- test runner instrumentation;
- manually recorded inspection evidence in early stage.
```

Rule:

```text
observed_deps ⊆ strict ∪ optional ∪ dynamic_pattern_matches
```

Blocking conditions:

```text
- observed import is not declared;
- observed file read escapes permitted paths;
- observed dependency violates layer rules;
- dynamic pattern is too broad to review;
- dependency appears only in code and not in FIC/registry.
```

Early L1 may use static scanning and manual inspection, but the result must still be recorded in the validation output.

---

## 13. Layer Rules

Agent_X uses visible root layers:

```text
L0 = governed seed kernel
L1 = external evolution/controller layer
L2 = specialization profiles and blueprints
```

Allowed dependency direction:

```text
L1 may read L0 public contracts and proof outputs.
L1 may call L0 only through declared public entrypoints or proof commands.
L1 may read L2 profiles when planning specialization.
L2 may reference L1 outputs, but L1 must not depend on unfinished L2 execution behavior.
```

Forbidden dependency direction:

```text
L0 must not import L1.
L0 must not import L2.
L0 must not depend on L1 FICs, SIB files, or generated artifacts.
L1 implementation must not patch L0 directly without an L0 impact classification and proof plan.
```

Any graph edge that violates these rules is blocking.

---

## 14. Public Surface Binding

Every implementation artifact must declare its public surface in the registry and in its governing FIC.

Public surface includes:

```text
- functions;
- classes;
- dataclasses;
- constants intended for import;
- CLI commands;
- schemas;
- configuration keys;
- file formats;
- generated output fields.
```

Rules:

```text
- Public surface must match the governing FIC.
- Extra public surface is rejected unless the FIC is updated first.
- Removed or changed public surface is a functional change.
- Imported helper names must not leak into public surface.
- Python modules with stable imports must declare `__all__`.
- Surface diff must be included in review packets.
```

---

## 15. Deterministic Change Classification

Every change to a governed L1 artifact must be classified.

Allowed classifications:

```text
METADATA
VALIDATION
STATE
FUNCTIONAL
```

Severity order:

```text
METADATA < VALIDATION < STATE < FUNCTIONAL
```

Classification is the highest severity triggered.

### 15.1 Functional triggers

```text
TRG_FD_CHANGED_UNEXPLAINED
TRG_PUBLIC_SURFACE_CHANGED
TRG_OPERATOR_OR_FUNCTION_SIGNATURE_CHANGED
TRG_TRACE_DRIFT_EXCEEDS_TOLERANCE
TRG_OBSERVED_DEPS_VIOLATION
TRG_L0_IMPACT
TRG_SECURITY_RULE_CHANGED
TRG_ERROR_BEHAVIOR_CHANGED
TRG_STATE_OWNERSHIP_CHANGED
TRG_ACCEPTANCE_CRITERIA_CHANGED
```

### 15.2 State triggers

```text
TRG_DEPENDENCY_LOCK_CHANGED
TRG_VALIDATOR_PROFILE_CHANGED
TRG_CANONICALIZER_CHANGED
TRG_FSD_CHANGED_WITH_NO_BEHAVIOR_DRIFT
TRG_GENERATED_DIGEST_CHANGED
```

### 15.3 Validation triggers

```text
TRG_TEST_ONLY_CHANGED
TRG_TRACE_ONLY_CHANGED
TRG_VALIDATION_REPORT_CHANGED
TRG_REVIEW_PACKET_CHANGED
```

### 15.4 Metadata triggers

```text
TRG_COMMENT_ONLY_CHANGED
TRG_TITLE_OWNER_OR_NOTE_CHANGED
TRG_REFERENCE_ONLY_CHANGED
```

Functional changes require:

```text
1. FIC update or FIC delta before implementation.
2. Binding map update if affected artifacts change.
3. Registry version impact classification.
4. Tests or validator updates.
5. Completion evidence.
6. Review packet.
7. Semantic lockfile update.
```

---


## 15.5 Version Impact Classification

Every accepted change must declare version impact.

Allowed version impacts:

```text
NONE
PATCH
MINOR
MAJOR
```

Default mapping:

```text
METADATA   → PATCH or NONE
VALIDATION → PATCH
STATE      → PATCH or MINOR
FUNCTIONAL → MINOR or MAJOR
```

MAJOR is required when:

```text
- public surface is removed;
- public signature changes incompatibly;
- serialized output format changes incompatibly;
- L0 interaction semantics change;
- validation/proof behavior is weakened;
- migration is required;
- a previously accepted behavior is removed.
```

MINOR is sufficient when:

```text
- public surface is added without breaking existing callers;
- behavior is extended without changing existing accepted behavior;
- new validation evidence is required but old behavior remains valid.
```

PATCH is sufficient when:

```text
- documentation, metadata, evidence, or validation reporting changes without accepted behavior drift;
- dependency or tool profile metadata changes and revalidation shows no behavior drift.
```

A missing version-impact classification blocks acceptance.

## 16. Impact Rules

When an artifact changes, L1 must compute the affected set.

Impact traversal follows these edges:

```text
IMPLEMENTS
GOVERNS
VALIDATES
USES
DERIVES
```

Impact traversal does not follow:

```text
REFERENCES
RECOGNIZES
OBSERVED_IMPORTS
OBSERVED_FS_READS
```

Bindings traversal must be bidirectional:

```text
Implementation change → affected FICs, pseudocode units, tests, completion records, review packets.
Document/FIC change → affected implementation artifacts, tests, completion records, review packets.
```

Impact output must include:

```yaml
impact_report:
  change_id: "CHANGE-L1-001"
  changed_artifact: "AGENT_X_L1::ART-L1-001"
  classification: "FUNCTIONAL"
  classification_triggers:
    - "TRG_PUBLIC_SURFACE_CHANGED"
  affected_units:
    - "AGENT_X_L1::UNIT-L1-001"
  affected_fics:
    - "AGENT_X_L1::FIC-L1-001"
  affected_implementation_artifacts:
    - "AGENT_X_L1::ART-L1-001"
  affected_tests:
    - "AGENT_X_L1::TEST-L1-001"
  affected_l0_contracts: []
  required_actions:
    - "update_fic"
    - "run_tests"
    - "update_completion_record"
    - "update_review_packet"
    - "regenerate_semantic_lockfile"
  blocking: true
```

If `affected_l0_contracts` is non-empty, the change must go through the L0 impact gate.

---

## 17. L0 Impact Gate

A change has L0 impact if it does any of the following:

```text
- modifies files under L0/;
- changes commands that validate L0;
- changes how L1 reads L0 contracts;
- changes how L1 interprets L0 proof results;
- changes any public entrypoint used to run or validate L0;
- changes an integration path between L1 and L0;
- weakens an L0-related validator, proof, or blocking condition.
```

L0-impacting changes require:

```text
1. Explicit affected_l0_contracts entry.
2. FUNCTIONAL classification.
3. Updated FIC or FIC delta.
4. Proof command list.
5. Rollback plan.
6. Completion record with proof results.
7. Review packet with L0 impact section.
8. Semantic lockfile update.
```

Minimum proof commands:

```text
make seed-boot
make prove-seed
make run
```

If the actual repository uses different commands, the current L0 README or Makefile is authoritative.

A missing or failed L0 proof blocks acceptance.

---

## 18. Completion Record Binding

Every implemented unit must produce a completion record.

Recommended path:

```text
L1/evidence/<unit_id>/<utc_timestamp>_completion_record.yaml
```

Minimum schema:

```yaml
completion_record:
  completion_id: "COMP-L1-001"
  unit_id: "AGENT_X_L1::UNIT-L1-001"
  fic_id: "AGENT_X_L1::FIC-L1-001"
  implementation_artifacts:
    - "AGENT_X_L1::ART-L1-001"
  status: "VALIDATED"
  change_classification: "FUNCTIONAL"
  classification_triggers:
    - "TRG_PUBLIC_SURFACE_CHANGED"
  files_inspected: []
  files_changed: []
  public_surface_created_or_preserved: []
  tests_created_or_updated: []
  checks_run:
    - command: "pytest L1/tests/test_document_loader.py -q"
      result: "pass"
      evidence_path: "L1/evidence/UNIT-L1-001/2026-05-29T000000Z_checks.log"
  checks_not_run: []
  deviations_from_fic: []
  unresolved_unknowns: []
  residual_risks: []
  rollback_plan: []
  digest_updates:
    functional_digest: "<sha256>"
    public_surface_digest: "<sha256>"
    functional_state_digest: "<sha256>"
```

Allowed completion statuses:

```text
BLOCKED
NO_CHANGE
IMPLEMENTED_UNVALIDATED
VALIDATED
IMPLEMENTED_WITH_WAIVERS
REJECTED
```

The registry must reference accepted completion records.

A completion record cannot claim `VALIDATED` unless all required checks either passed or have explicit valid waivers.

---

## 19. Review Packet Binding

Accepted implementation requires a review packet.

Recommended path:

```text
L1/evidence/<unit_id>/<utc_timestamp>_review_packet.md
```

Minimum contents:

```yaml
review_packet:
  review_id: "REV-L1-001"
  unit_id: "AGENT_X_L1::UNIT-L1-001"
  fic_id: "AGENT_X_L1::FIC-L1-001"
  implementation_artifacts:
    - "AGENT_X_L1::ART-L1-001"
  test_artifacts:
    - "AGENT_X_L1::TEST-L1-001"
  decision: "accepted"
  requirement_to_code_map: []
  requirement_to_test_map: []
  public_surface_diff: []
  dependency_diff: []
  declared_vs_observed_dependency_report: []
  semantic_diff:
    behavior_added: []
    behavior_removed: []
    behavior_changed: []
    behavior_preserved: []
  l0_impact_review:
    has_l0_impact: false
    proof_commands: []
    proof_results: []
  residual_risks: []
  validators_run: []
  validators_not_run: []
  waivers: []
```

Allowed review decisions:

```text
accepted
rejected_needs_fix
rejected_scope_drift
rejected_test_insufficient
rejected_traceability_gap
rejected_l0_impact_unproven
blocked_requires_fic_delta
```

A review packet must not accept an implementation with undocumented behavior, missing completion evidence, or unresolved blocking unknowns.

---

## 20. Unknowns and Waivers

Unknowns must be explicit.

Minimum unknown record:

```yaml
unknown:
  id: "UNK-L1-001"
  artifact: "AGENT_X_L1::ART-L1-001"
  field: "public_surface"
  severity: "blocking"
  reason: "FIC does not declare the required exported function."
  resolution: "blocked_until_fic_update"
```

Allowed severities:

```text
blocking
non_blocking
waived
```

Waivers must be explicit, scoped, and temporary.

Minimum waiver record:

```yaml
waiver:
  waiver_id: "WVR-L1-001"
  scope:
    unit_id: "AGENT_X_L1::UNIT-L1-001"
    fic_id: "AGENT_X_L1::FIC-L1-001"
    artifact: "AGENT_X_L1::ART-L1-001"
  waived_requirement: "property_test_required"
  reason: "Unit is deterministic file loading with exhaustive edge-case tests."
  risk_accepted: "low"
  expires: "2026-08-29T00:00:00Z"
  approval: "documented"
```

Waivers cannot be used to hide:

```text
- missing L0 proof;
- security ambiguity;
- public-surface ambiguity;
- undocumented behavior;
- missing primary FIC binding;
- failed required tests;
- repository path escape;
- observed dependency violation.
```

---


## 20.1 Evidence Retention and Immutability

Evidence files are append-only by default.

Rules:

```text
- Evidence that supported an accepted artifact must not be overwritten.
- Replacement evidence must receive a new timestamped path and a new digest.
- The review packet must state which evidence version it accepted.
- Completion records must reference exact evidence paths and digests.
- Check logs must not be summarized as pass/fail only; the exact command and result must be retained.
- If evidence is redacted, the redaction must be declared and the unredacted source must either be retained privately or the evidence must be classified as partial.
```

Minimum evidence reference:

```yaml
evidence_ref:
  path: "L1/evidence/UNIT-L1-001/2026-05-29T153000Z_checks.log"
  digest:
    algorithm: "sha256"
    value: "<64 lowercase hex chars>"
  produced_by: "pytest"
  command: "pytest L1/tests/test_document_loader.py -q"
  result: "pass"
```

An accepted review packet must contain enough evidence references to reconstruct why the change was accepted without reading the conversation history.

## 20.2 Waiver Closure and Non-Waivable Conditions

Waivers may relax process requirements only when the risk is explicit and temporary.

Waiver scope must include:

```text
- affected unit;
- affected FIC;
- affected artifact or document;
- waived requirement;
- reason;
- expiration;
- approval source;
- replacement evidence or risk acceptance.
```

Non-waivable conditions:

```text
- missing primary HARD FIC binding;
- missing registry entry for accepted implementation;
- repository path escape;
- missing or failed L0 proof for L0-impacting change;
- undocumented public surface change;
- observed dependency violation;
- expired waiver;
- blocking unknown marked unresolved;
- generated artifact accepted without input digest record;
- review packet absent for accepted implementation.
```

## 21. Timestamp Rules

Rules:

```text
- All timestamps must be UTC ISO-8601 strings ending in Z.
- Timestamp format should be YYYY-MM-DDTHHMMSSZ for filenames.
- Timestamp format should be YYYY-MM-DDTHH:MM:SSZ inside YAML/JSON content.
- Wall-clock time must not affect validation pass/fail except as recorded metadata.
```

---

## 22. Validator Commands

The lightweight SIB validator should eventually provide these commands:

```text
l1-sib validate
l1-sib impact --change <GLOBAL_ART_ID_OR_DOC_ID>
l1-sib check-bindings
l1-sib check-graph
l1-sib check-public-surface
l1-sib check-completion-records
l1-sib check-observed-deps
```

Early implementation may use scripts instead of a full CLI.

Minimum validator exit codes:

```text
0 = PASS
1 = VALIDATION_FAIL
2 = TOOL_ERROR
```

Minimum validation output:

```yaml
validation_result:
  validator: "l1-sib validate"
  version: "v0.5.0"
  status: "PASS"
  errors: []
  warnings: []
  checked_artifacts: []
  checked_bindings: []
  checked_graph_edges: []
  classification_triggers: []
  observed_deps_delta: []
  broken_bindings: []
  stale_artifacts: []
  waivers_used: []
  generated_at: "2026-05-29T00:00:00Z"
```

Validator output must be deterministic:

```text
- errors sorted by code, artifact, field;
- warnings sorted by code, artifact, field;
- artifacts sorted by GlobalArtID;
- bindings sorted by binding_id;
- graph edges sorted by src, type, dst;
- no random ordering;
- no pass/fail dependence on uncontrolled time, network, locale, or filesystem order.
```

---


## 22.1 Validator Input Manifest

Every validation run must declare its input set.

Minimum input manifest:

```yaml
validator_input_manifest:
  validator: "l1-sib validate"
  validator_version: "v0.5.0"
  workspace_ref: "local-working-tree"
  inputs:
    - path: "L1/sib/sib-registry.yaml"
      digest: "<sha256>"
    - path: "L1/sib/sib-bindings.yaml"
      digest: "<sha256>"
    - path: "L1/sib/sib-graph.yaml"
      digest: "<sha256>"
    - path: "L1/generated/semantic_lockfile.yaml"
      digest: "<sha256>"
  profile: "agent_x_l1_local"
```

Rules:

```text
- Validation output must name the input manifest or embed it.
- Validation output without input digests is not release evidence.
- Validator profile changes trigger STATE classification.
```

## 22.2 Deterministic JSON Output and Error-Code Closure

Machine-readable validator output must be canonical JSON when used by automation.

Rules:

```text
- JSON keys sorted lexicographically.
- No insignificant whitespace in canonical output files.
- Error and warning codes must come from `L1/sib/sib-error-codes.yaml`.
- Unknown error codes are validator failures.
- Lists sorted by stable keys unless order is semantically meaningful and declared in schema.
- Validator output must not depend on uncontrolled filesystem ordering.
```

Minimum error-code entry:

```yaml
error_codes:
  - code: "SIB_MISSING_PRIMARY_BINDING"
    severity: "error"
    message: "Artifact has no primary HARD FIC binding."
    blocking: true
```

## 23. Schema Closure Rule

The lightweight SIB package is schema-closed when every required sidecar has a schema and validates against it.

Required schemas:

```text
sib-registry.schema.json
sib-bindings.schema.json
sib-graph.schema.json
completion-record.schema.json
review-packet.schema.json
validation-result.schema.json
waiver.schema.json
```

Blocking conditions:

```text
- schema missing;
- sidecar missing;
- sidecar fails schema validation;
- sidecar contains unknown enum values;
- sidecar references an undefined GlobalArtID, GlobalDocID, GlobalUnitID, or GlobalFicID;
- schema and document examples disagree.
```

Manual review is allowed before validators exist, but the manual result must record which schema checks were not executable yet.

---



## 23.1 Schema Example Fixture Rule

Every schema-controlled sidecar must have at least one valid example fixture and one invalid example fixture before the schema is treated as executable.

Minimum fixture layout:

```text
L1/sib/sib-schemas/examples/
  sib-registry.valid.yaml
  sib-registry.invalid.yaml
  sib-bindings.valid.yaml
  sib-bindings.invalid.yaml
  sib-graph.valid.yaml
  sib-graph.invalid.yaml
  completion-record.valid.yaml
  completion-record.invalid.yaml
  review-packet.valid.yaml
  review-packet.invalid.yaml
```

Rules:

```text
- Valid fixtures must pass schema validation.
- Invalid fixtures must fail for the intended error code.
- Fixture validation must be deterministic.
- Schema examples embedded in this document must not contradict fixture files.
- If a schema changes, fixtures must be updated in the same change package.
```

Each invalid fixture must include fixture intent metadata, either inline or in a sibling metadata file:

```yaml
fixture_intent:
  fixture: "sib-registry.invalid.yaml"
  expected_result: "fail"
  expected_error_code: "SIB_MISSING_PRIMARY_BINDING"
  expected_field: "artifacts[0].governed_by_fic"
```

A schema without tested fixtures may be used for manual review, but it cannot be used as release-blocking automation evidence.

## 23.2 Minimum Executable Validator Profile

The lightweight SIB validator is considered minimally executable when it performs the following checks in one deterministic command:

```text
l1-sib validate --profile agent_x_l1_minimal
```

Required checks:

```text
1. Load and schema-validate sib-registry.yaml.
2. Load and schema-validate sib-doc-registry.yaml.
3. Load and schema-validate sib-bindings.yaml.
4. Load and schema-validate sib-graph.yaml.
5. Verify every referenced GlobalArtID, GlobalDocID, GlobalUnitID, and GlobalFicID resolves.
6. Verify every accepted artifact has one primary HARD FIC binding.
7. Verify every accepted artifact has a completion record and review packet.
8. Verify accepted artifact digests are populated and match canonical bytes where files exist.
9. Verify public surface listed in registry matches the governing FIC surface entry.
10. Verify declared dependencies are present and no observed dependency violation is recorded.
11. Verify L0-impacting changes have an L0 impact report and proof results.
12. Verify semantic_lockfile.yaml contains every accepted artifact and current SIB sidecar digests.
13. Verify no blocking unknown or expired waiver is referenced by an accepted artifact.
14. Emit canonical JSON output with known error codes only.
```

The validator may be simple, but it must not silently skip these checks when used as acceptance evidence. If a check is not implemented yet, the validator must emit a warning or error that names the missing check.

### 23.2.1 Validator No-Silent-Skip Rule

A validator profile must classify each required check as one of:

```text
implemented_blocking
implemented_warning
not_implemented_blocking
not_implemented_advisory
not_applicable
```

Rules:

```text
- Release-bound validation may not contain `not_implemented_advisory` for any check used as acceptance evidence.
- Accepted artifacts may not rely on a check marked `not_implemented_advisory`.
- If a check is required by this document and not implemented, the validator output must name the check ID and reason.
- A validator must not report overall `PASS` when any release-blocking check is `not_implemented_blocking`.
- Manual review may temporarily satisfy a missing check only when the review packet names the missing automated check and records the manual evidence.
```

## 23.3 Observed Dependency Maturity Levels

Observed dependency enforcement may mature over time, but the current level must be declared in the validator profile.

```text
ODL-0 manual-inspection-only
ODL-1 static-import-scan
ODL-2 static-import-scan-plus-file-read-review
ODL-3 instrumented-test-run
ODL-4 clean-room-instrumented-run
```

Rules:

```text
- ODL-0 is acceptable only for early draft or exploratory artifacts.
- ODL-1 is the minimum for accepted pure Python implementation artifacts.
- ODL-2 is the minimum for artifacts that read repository files.
- ODL-3 is required before claiming automated dependency enforcement.
- ODL-4 is deferred until full EQC-SIB or release-candidate hardening.
```

The review packet must state the observed dependency maturity level used for acceptance.

## 23.4 Source Authority and Conflict Resolution

When artifacts disagree, SIB validation must resolve authority deterministically.

Authority order:

```text
1. Non-waivable L0 safety and proof requirements
2. L1 system goal and architecture contract
3. L1 pseudocode-to-FIC workflow
4. L1 EQC-FIC document for the target unit
5. L1 lightweight SIB registry and binding records
6. Existing code inspected directly
7. Existing tests
8. Completion records and review packets
9. Conversation notes or informal task text
```

Conflict outcomes:

| Conflict | Required result |
|---|---|
| FIC permits behavior that L0 gate forbids | `BLOCKED_L0_AUTHORITY_CONFLICT` |
| Code exposes public surface not in FIC | `BLOCKED_PUBLIC_SURFACE_DRIFT` |
| Test asserts behavior not owned by any FIC | `BLOCKED_UNOWNED_TEST_ORACLE` |
| Registry target path disagrees with FIC target path | `BLOCKED_REGISTRY_FIC_PATH_CONFLICT` |
| Completion record claims checks that evidence does not support | `BLOCKED_EVIDENCE_CONFLICT` |
| Review packet accepts stale artifact | `BLOCKED_STALE_ACCEPTANCE` |
| Binding map references missing object | `BLOCKED_BROKEN_BINDING` |

The validator must not choose the more convenient source. It must apply the authority order or block the package.

## 23.5 Release-Blocking Matrix

A release-bound L1 package is blocked when any required condition below is true.

| Area | Blocking condition | Error code |
|---|---|---|
| Registry | accepted artifact missing registry entry | `SIB_MISSING_REGISTRY_ENTRY` |
| Binding | missing primary HARD FIC binding | `SIB_MISSING_PRIMARY_BINDING` |
| FIC | FIC not `ready-for-code`, `validated`, or accepted equivalent | `SIB_FIC_NOT_READY` |
| Path | path escapes repository root | `SIB_PATH_ESCAPE` |
| Digest | accepted digest missing or mismatched | `SIB_DIGEST_MISMATCH` |
| Surface | public surface mismatch | `SIB_PUBLIC_SURFACE_MISMATCH` |
| Dependency | observed dependency violation | `SIB_OBSERVED_DEP_UNDECLARED` |
| L0 | missing or failed required L0 proof | `SIB_L0_PROOF_MISSING_OR_FAILED` |
| Evidence | completion or review evidence missing | `SIB_EVIDENCE_MISSING` |
| Waiver | waiver expired or non-waivable condition waived | `SIB_INVALID_WAIVER` |
| Lockfile | semantic lockfile stale or missing artifact | `SIB_LOCKFILE_STALE` |
| Schema | required sidecar schema validation failed | `SIB_SCHEMA_FAIL` |

A release package with any error-code row above cannot be accepted as governed L1 implementation.

## 24. Semantic Lockfile Integration

The SIB bridge must be reflected in the L1 semantic lockfile.

Minimum lockfile SIB section:

```yaml
sib_lock:
  sib_registry_digest: "<sha256>"
  sib_bindings_digest: "<sha256>"
  sib_graph_digest: "<sha256>"
  fic_index_digest: "<sha256>"
  accepted_artifacts:
    - global_art_id: "AGENT_X_L1::ART-L1-001"
      version: "v0.1.0"
      functional_digest: "<sha256>"
      public_surface_digest: "<sha256>"
      functional_state_digest: "<sha256>"
```

Rules:

```text
- Accepted artifacts must appear in the lockfile.
- Lockfile digest mismatch marks the package stale.
- Functional changes require lockfile regeneration.
- A generated lockfile must include the validator version or script identity used to produce it.
```

---

## 24.1 Semantic Lockfile Drift Rules

The semantic lockfile becomes stale when any of the following digests change without lockfile regeneration:

```text
- sib-registry.yaml digest;
- sib-doc-registry.yaml digest;
- sib-bindings.yaml digest;
- sib-graph.yaml digest;
- fic index digest;
- accepted artifact FD, SD, MD, or FSD;
- accepted completion record digest;
- accepted review packet digest;
- waiver file digest when a waiver is referenced;
- schema digest for any sidecar used in validation.
```

Rules:

```text
- A stale semantic lockfile blocks release acceptance.
- A stale semantic lockfile may be used for impact comparison, but not as final evidence.
- Lockfile regeneration must record generator identity, generator version, input manifest digest, and UTC timestamp.
- Regenerated lockfiles must not silently drop accepted artifacts; removals require migration or deprecation records.
```



## 25. Release Package Contents

A release-bound L1 implementation package must include:

```text
- current FIC documents for included units;
- sib-registry.yaml;
- sib-bindings.yaml;
- sib-graph.yaml;
- semantic_lockfile.yaml;
- validation_report.md or validation_result.yaml;
- impact_report.yaml for functional changes;
- completion records;
- review packets;
- waiver file if any waiver was used;
- release package manifest.
```

The release package manifest must list every included artifact and digest.

### 25.0.1 Release Acceptance Maturity Levels

A package must declare its acceptance maturity level.

```text
SAM-0 exploratory: documents may be incomplete; no governed acceptance claim.
SAM-1 governed-local: registry, binding, FIC, completion, review, and lockfile chain exists; some validators may be manual.
SAM-2 validator-backed: schemas, validator output, fixture checks, digests, and dependency checks are executable.
SAM-3 release-candidate: validator-backed plus no advisory gaps, no stale artifacts, no unresolved waivers, and L0 impact proofs where relevant.
SAM-4 full-SIB-ready: release-candidate plus clean-room dependency tracing, signed checkpoints, and cryptographic waiver/signature controls.
```

Current Agent_X L1 target:

```text
SAM-1 for early implementation units.
SAM-2 before accepting repeated L1 implementation workflow as stable.
SAM-3 before using L1 to propose or apply L0-impacting changes.
SAM-4 deferred.
```

Rules:

```text
- A package must not claim a higher maturity level than its evidence supports.
- SAM-3 packages may not contain validator checks marked `not_implemented_advisory` if those checks affect acceptance.
- L0-impacting packages require at least SAM-3 unless explicitly marked experimental and blocked from acceptance.
```

---


## 25.1 Migration, Move, Split, Merge, and Delete Rules

Structural changes to governed artifacts must be explicit.

Actions requiring migration records:

```text
- moving a file;
- renaming a public symbol;
- splitting one artifact into several artifacts;
- merging several artifacts into one artifact;
- deleting a governed artifact;
- replacing a FIC with a new FIC;
- changing ownership of public surface or state.
```

Minimum migration record:

```yaml
migration_record:
  migration_id: "MIG-L1-001"
  action: "move|split|merge|delete|rename|replace"
  old_ids: []
  new_ids: []
  affected_bindings: []
  affected_public_surface: []
  compatibility_impact: "none|patch|minor|major"
  required_tests: []
  rollback_plan: []
  status: "planned|applied|validated|rejected"
```

Rules:

```text
- IDs must not be silently reused after delete or replacement.
- Deleted artifacts must be proven unreferenced or explicitly deprecated first.
- Moved artifacts must preserve aliases or migration notes until all bindings are updated.
- Split/merge changes require updated registry, graph, binding map, FICs, tests, and semantic lockfile.
- Any migration touching L0 paths triggers the L0 impact gate.
```



## 25.2 Deferred Full-SIB Capability Register

The lightweight SIB intentionally defers some full EQC-SIB capabilities. Deferral is allowed only when it is explicit.

```yaml
deferred_capabilities:
  - capability_id: "DEF-SIB-001"
    name: "signed paired checkpoint"
    reason: "not required for early L1 governed implementation"
    current_control: "semantic lockfile plus evidence digests"
    promotion_trigger: "release candidate or multi-contributor governance"
  - capability_id: "DEF-SIB-002"
    name: "clean-room observed dependency tracing"
    reason: "manual/static observed dependency checks are sufficient for first L1 files"
    current_control: "ODL-1 or ODL-2 validator profile"
    promotion_trigger: "artifact reads external files, runs subprocesses, or touches L0"
  - capability_id: "DEF-SIB-003"
    name: "cryptographic waiver signatures"
    reason: "single-user local development stage"
    current_control: "explicit waiver file with expiration and evidence"
    promotion_trigger: "shared repo governance or release-bound automation"
```

Rules:

```text
- Deferred capabilities must not be described as implemented.
- A deferred capability must have a current control or the affected package is blocked.
- Promotion triggers must be reviewed at release-candidate time.
- A package may not rely on a deferred capability as evidence.
```


## 26. Blocking Conditions

Validation must fail if any of these are true:

```text
- implementation artifact has no registry entry;
- implementation artifact has no primary FIC binding;
- FIC binding points to a missing FIC;
- implementation file path escapes repository root;
- implementation depends on undeclared artifact;
- observed dependency is undeclared;
- dependency graph has a forbidden cycle;
- L0-impacting change lacks L0 impact gate;
- public surface differs from FIC without FIC delta;
- accepted artifact has no completion record;
- accepted artifact has no review packet;
- completion record claims tests passed without evidence path;
- waiver is expired;
- unknown is blocking and unresolved;
- generated artifact was manually edited without authorization;
- accepted artifact is missing from semantic lockfile;
- required sidecar fails schema validation.
```

---

## 27. Lightweight SIB Acceptance Criteria

This standard is accepted for current Agent_X L1 use when:

```text
[ ] L1/sib/sib-registry.yaml exists.
[ ] L1/sib/sib-bindings.yaml exists.
[ ] L1/sib/sib-graph.yaml exists.
[ ] L1/sib/sib-doc-registry.yaml exists.
[ ] L1/sib/sib-error-codes.yaml exists.
[ ] Required schemas exist for all required sidecars or the validator profile explicitly marks the sidecar advisory-only.
[ ] Schema fixtures exist for sidecars used as executable validation evidence, and invalid fixtures declare intended error codes.
[ ] The minimum executable validator profile is declared and uses the no-silent-skip classification.
[ ] Every planned L1 implementation unit has a registry entry.
[ ] Every implementation artifact binds to one primary FIC.
[ ] Every FIC binds to one pseudocode unit.
[ ] Every accepted artifact has completion evidence.
[ ] Every accepted artifact has a review packet.
[ ] Every accepted artifact appears in the semantic lockfile.
[ ] Declared dependencies and observed dependencies are checked.
[ ] L0-impacting changes are separately classified.
[ ] Validator outputs are deterministic.
[ ] Source authority conflicts are either absent or blocked with declared error codes.
[ ] Semantic lockfile integration and drift rules pass in correct section order.
[ ] Deferred full-SIB capabilities have current controls and promotion triggers.
[ ] Canonical digest rules are applied consistently.
[ ] Evidence files referenced by accepted artifacts include paths and digests.
[ ] No accepted artifact has unresolved blocking unknowns.
```

---

## 28. First Agent_X L1 Binding Example

This example binds the first planned L1 unit: document loading.

```yaml
unit:
  unit_id: "AGENT_X_L1::UNIT-L1-001"
  title: "L1 document loader"
  purpose: "Load approved L1 Markdown/text control documents into immutable records for downstream L1 planning and validation."

fic:
  fic_id: "AGENT_X_L1::FIC-L1-001"
  path: "L1/fic/units/FIC-L1-001-document-loader.md"
  status: "ready-for-code"

implementation:
  art_id: "AGENT_X_L1::ART-L1-001"
  path: "L1/controller/document_loader.py"
  status: "planned"
  public_surface:
    - "DocumentRecord"
    - "load_markdown_document"
    - "load_text_document"

tests:
  - test_id: "AGENT_X_L1::TEST-L1-001"
    path: "L1/tests/test_document_loader.py"
    validates:
      - "AGENT_X_L1::ART-L1-001"

binding:
  binding_id: "BIND-L1-001"
  binding_strength: "HARD"
  chain:
    - "AGENT_X_L1::GOAL-L1-001"
    - "AGENT_X_L1::PS-L1-001"
    - "AGENT_X_L1::UNIT-L1-001"
    - "AGENT_X_L1::FIC-L1-001"
    - "AGENT_X_L1::ART-L1-001"
    - "AGENT_X_L1::TEST-L1-001"
```

---


## 29. Self-Assessment for v0.5.0

Current score: **10/10** for the current Agent_X L1 stage.

This is a 10/10 lightweight SIB standard because it now defines the complete governance bridge needed for L1 without prematurely importing full EQC-SIB machinery.

What is complete at the document-standard level:

```text
- identity and global ID rules;
- required sidecars and schema coverage;
- canonical path, content, and digest rules;
- artifact and document/object registries;
- binding map and collision rules;
- dependency graph rules;
- declared-vs-observed dependency discipline;
- L0/L1/L2 layer boundaries;
- public surface binding;
- deterministic change classification;
- version-impact rules;
- impact closure rules;
- L0 impact gate;
- completion and review evidence binding;
- unknown and waiver discipline;
- evidence immutability;
- validator commands, inputs, outputs, and no-silent-skip rules;
- schema closure and fixture rules;
- semantic lockfile integration and drift rules;
- release package contents and maturity levels;
- migration, move, split, merge, and delete rules;
- deferred full-SIB capability register.
```

Remaining work is implementation work, not a defect in this standard:

```text
- write the actual sidecar files;
- write JSON schemas;
- write fixtures;
- implement validator scripts;
- generate the first semantic lockfile;
- produce real evidence from the first L1 implementation unit.
```

Full clean-room replay, signed paired checkpoints, and cryptographic waiver signatures remain intentionally deferred and are tracked in the deferred-capability register.

## 30. Final Rule

L1 may evolve the project only through traceable, bounded, reviewable implementation units.

If L1 cannot prove the chain from goal to pseudocode to FIC to code to tests to evidence to review to semantic lockfile, the change is not accepted as governed Agent_X implementation.
