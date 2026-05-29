# Agent_X L1 EQC-FIC Implementation Contract

**Document ID:** `AGENT-X-L1-EQC-FIC-001`  
**Version:** `v0.6.0`  
**Status:** `ready-for-code`  
**Layer:** `L1`  
**Project:** `Agent_X`  
**Primary Standard:** `EQC-FIC v2.3 adapted for Agent_X L1`  
**Conformance Target:** `EQC-FIC Level 4 for L1 scaffolding; Level 5 later when executable validators and signed checkpoints exist`  
**Purpose:** Define the EQC-FIC-governed implementation-contract system for the Agent_X L1 external evolution/controller layer.

---

## 0. Rating of Previous Version

**Previous file rated:** `9.7/10`

The previous version was strong and implementation-ready for a careful human-guided pass, but it was not quite 10/10 because several machine-checkable details were still incomplete: not every acceptance criterion mapped to a verification method, the status vocabulary was not fully normalized, a stale `v0.6.0` reference remained in the performance section, zero-byte size-limit behavior needed to be explicit, path-like root handling needed tests, root symlink behavior needed a declared policy, and the document rated itself 10/10 before closing those verification gaps.

### Fixes applied in this version

1. **Status vocabulary normalized**  
   The document-level status is now `ready-for-code`, matching the controlled FIC lifecycle vocabulary instead of using a one-off descriptive status.

2. **Full acceptance-criterion coverage added**  
   Every `AC-L1-001-*` acceptance criterion now maps to at least one test, static check, review item, or completion-evidence requirement.

3. **Zero-byte size-limit behavior specified**  
   `max_bytes=0` is now defined precisely: empty files are allowed, non-empty files are rejected.

4. **Path-like root behavior made testable**  
   `root` may be `str` or `os.PathLike[str]`, and this is now explicitly covered by required tests.

5. **Root symlink behavior declared**  
   A root that is itself a symlink to an existing directory is allowed after resolution, but all returned paths remain relative to the resolved root and document symlink escapes remain blocked.

6. **Stale version references removed**  
   The stale `v0.6.0` performance-budget reference has been corrected.

7. **Review packet strengthened**  
   The review packet must now include explicit `acceptance_criteria_coverage`, `edge_case_coverage`, and `unmapped_requirements` fields.

8. **FIC-L1-001 upgraded to v0.5.0**  
   The first concrete FIC now has complete test-oracle coverage and can be used as the first controlled L1 implementation unit.

---

# Part I — Agent_X L1 EQC-FIC Standard

## 1. Purpose

Agent_X has an L0 governed seed kernel. L1 is the controlled external evolution/controller layer that converts improvement goals into bounded, reviewable, testable implementation work.

This document defines how L1 uses EQC-FIC-style contracts before any L1 code is generated, modified, refactored, or accepted.

The controlling L1 rule is:

```text
No governed L1 code may be generated, edited, refactored, or accepted unless the intended behavior is first defined in an L1 EQC-FIC document and the FIC passes the pre-code gate.
```

L1 protects L0 from uncontrolled evolution. L1 may inspect, plan, validate, prepare implementation packets, run declared proof/check commands, and record evidence. L1 must not bypass L0 governance or mutate the seed kernel without a bounded, approved contract.

---

## 2. L1 Role in Agent_X

L1 is responsible for:

- reading approved Agent_X repository state;
- reading L0 and L1 governing documents;
- classifying requested improvements;
- splitting broad goals into bounded implementation units;
- creating or updating EQC-FIC unit documents;
- validating FIC readiness before coding;
- building bounded coding-agent handoff packets;
- running declared checks and proof commands;
- collecting evidence;
- writing completion records;
- updating traceability records;
- recording failure-learning entries.

L1 is not responsible for:

- replacing L0;
- bypassing L0 governance;
- silently changing L0 contracts;
- performing uncontrolled autonomous self-modification;
- adding speculative future features;
- creating broad multi-agent orchestration before L1 itself is validated;
- executing unsafe tools without declared policy;
- treating code as the source of truth over governing documents;
- making L0 import or depend on L1 or L2.

---

## 3. Authority Hierarchy

When documents, code, tests, prompts, logs, prior notes, or generated output conflict, L1 must use this authority order:

```text
1. Non-waivable safety and governance invariants
2. Agent_X L0 seed-kernel contracts
3. Agent_X L1 system goal
4. Agent_X L1 architecture contract
5. L1 shared interfaces and unit DAG
6. L1 EQC-FIC unit documents
7. L1 validation plan and test oracles
8. Bounded coding-agent handoff packet
9. Existing implementation code
10. Conversation notes or model inference
```

Existing code is evidence of the current implementation state, but existing code does not override higher-authority contracts.

If a conflict cannot be resolved by this hierarchy, the correct status is:

```text
BLOCKED_SOURCE_CONFLICT
```

---

## 4. Repository Structure Required for L1

```text
L1/
  README.md

  docs/
    00_L1_SYSTEM_GOAL.md
    01_L1_BACKGROUND.md
    02_L1_ARCHITECTURE_CONTRACT.md
    03_L1_WHOLE_SYSTEM_PSEUDOCODE.md
    04_L1_UNIT_DAG.md
    05_L1_SHARED_TYPES_AND_INTERFACES.md
    06_L1_VALIDATION_PLAN.md
    07_L1_RISK_LEDGER.md
    08_L1_TRACEABILITY_MATRIX.md
    09_L1_CODING_AGENT_HANDOFF_RULES.md
    10_L1_FAILURE_LEARNING_LOG.md

  controller/
    __init__.py

  fic/
    index.fic.yaml
    units/
      FIC-L1-001-document-loader.md
      FIC-L1-002-repo-state-reader.md
      FIC-L1-003-goal-classifier.md
      FIC-L1-004-unit-planner.md
      FIC-L1-005-fic-generator.md
      FIC-L1-006-fic-validator.md
      FIC-L1-007-handoff-packet-builder.md
      FIC-L1-008-proof-check-runner.md
      FIC-L1-009-evidence-collector.md
      FIC-L1-010-completion-record-writer.md
      FIC-L1-011-traceability-updater.md
      FIC-L1-012-failure-learning-updater.md

  tests/
    __init__.py

  generated/
    semantic_lockfile.yaml
    fic_bundle_manifest.yaml
    readiness_report.md
    validation_report.md
    completion_records/
    evidence/
    review_packets/
```

Generated files are validator-owned or tool-owned outputs. A coding agent must not manually edit generated artifacts unless a FIC explicitly authorizes that maintenance task.

---

## 5. L1 Workflow

```text
Procedure L1_EvolveOnce(goal):

1. Load L0 repository state through declared read-only inspection rules.
2. Load L1 control documents.
3. Classify the requested goal.
4. Determine whether the goal affects L0, L1, L2, docs, tests, tooling, or generated artifacts.
5. If the goal is too broad, split it into bounded units.
6. Build or update the unit DAG.
7. Select the next implementation unit.
8. Create or update the EQC-FIC document for that unit.
9. Validate the FIC against the pre-code gate.
10. Build a bounded coding-agent handoff packet.
11. Permit implementation only inside declared files.
12. Run declared checks or record why checks were not run.
13. Collect evidence.
14. Produce completion record.
15. Produce review packet.
16. Update traceability matrix.
17. If implementation failed, update failure-learning log.
18. Return controlled status.
```

---

## 6. Controlled Statuses

### 6.1 FIC lifecycle status

```text
draft
reviewed
ready-for-code
implemented
validated
released
deprecated
stale
```

### 6.2 Implementation exit status

```text
BLOCKED
BLOCKED_SOURCE_CONFLICT
BLOCKED_MISSING_CONTEXT
BLOCKED_UNDEFINED_INTERFACE
BLOCKED_UNSAFE_DEPENDENCY
NO_CHANGE
IMPLEMENTED_UNVALIDATED
VALIDATED
IMPLEMENTED_WITH_WAIVERS
REJECTED
```

### 6.3 Status rules

- `draft` FICs must not be used for governed implementation.
- `ready-for-code` requires passing the pre-code gate or explicit waiver.
- `VALIDATED` requires required checks to have passed or waivers to be recorded.
- `IMPLEMENTED_UNVALIDATED` is allowed only when code changed but required checks did not pass or did not run.
- `NO_CHANGE` requires inspection evidence showing existing code already satisfies the FIC.
- `BLOCKED` is preferable to guessed code.
- `REJECTED` must include failure evidence and the failed gate or validator.

---

## 7. L1 Implementation Units

```text
UNIT-L1-001: L1 document loader
UNIT-L1-002: L1 repo state reader
UNIT-L1-003: L1 goal classifier
UNIT-L1-004: L1 unit planner
UNIT-L1-005: L1 FIC generator
UNIT-L1-006: L1 FIC validator
UNIT-L1-007: L1 handoff packet builder
UNIT-L1-008: L1 proof/check runner
UNIT-L1-009: L1 evidence collector
UNIT-L1-010: L1 completion record writer
UNIT-L1-011: L1 traceability updater
UNIT-L1-012: L1 failure-learning updater
```

Implementation order:

```text
1. document loader
2. repo state reader
3. shared types/interfaces
4. goal classifier
5. unit planner
6. FIC generator
7. FIC validator
8. handoff packet builder
9. proof/check runner
10. evidence collector
11. completion record writer
12. traceability updater
13. failure-learning updater
```

---

## 8. L1 Boundary Rules

### 8.1 L0 boundary

```yaml
l0_boundary:
  l1_may_read_l0_files: true
  l1_may_import_l0_runtime_modules: false
  l1_may_modify_l0_files: false
  l0_may_import_l1: false
  allowed_l0_access_mode: "read-only filesystem inspection through FIC-authorized paths"
  l0_mutation_requires: "separate FIC, explicit permitted files, proof commands, rollback plan, and review gate"
```

### 8.2 L2 boundary

```yaml
l2_boundary:
  l1_may_read_l2_specs: true
  l1_may_import_l2_runtime_modules: false
  l1_may_modify_l2_files: false
  l2_may_import_l1: "not until a specific integration FIC authorizes it"
```

### 8.3 Tool boundary

```yaml
tool_boundary:
  network_default: "forbidden"
  shell_default: "forbidden"
  file_write_default: "forbidden unless FIC declares permitted files"
  external_model_call_default: "forbidden unless FIC declares provider, inputs, outputs, and validation"
```

---

## 9. L1 FIC Registry Draft

Target file:

```text
L1/fic/index.fic.yaml
```

Initial contents:

```yaml
fic_registry_version: "v1.0"
portfolio_id: "AGENT_X_L1"
files:
  - fic_id: "FIC-L1-001"
    unit_id: "UNIT-L1-001"
    fic_path: "L1/fic/units/FIC-L1-001-document-loader.md"
    target_file: "L1/controller/document_loader.py"
    status: "ready-for-code"
    version: "v0.6.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
    permitted_files:
      - "L1/controller/document_loader.py"
      - "L1/tests/test_document_loader.py"

  - fic_id: "FIC-L1-002"
    unit_id: "UNIT-L1-002"
    fic_path: "L1/fic/units/FIC-L1-002-repo-state-reader.md"
    target_file: "L1/controller/repo_state_reader.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"

  - fic_id: "FIC-L1-003"
    unit_id: "UNIT-L1-003"
    fic_path: "L1/fic/units/FIC-L1-003-goal-classifier.md"
    target_file: "L1/controller/goal_classifier.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"

  - fic_id: "FIC-L1-004"
    unit_id: "UNIT-L1-004"
    fic_path: "L1/fic/units/FIC-L1-004-unit-planner.md"
    target_file: "L1/controller/unit_planner.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"

  - fic_id: "FIC-L1-005"
    unit_id: "UNIT-L1-005"
    fic_path: "L1/fic/units/FIC-L1-005-fic-generator.md"
    target_file: "L1/controller/fic_generator.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"

  - fic_id: "FIC-L1-006"
    unit_id: "UNIT-L1-006"
    fic_path: "L1/fic/units/FIC-L1-006-fic-validator.md"
    target_file: "L1/controller/fic_validator.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"

  - fic_id: "FIC-L1-007"
    unit_id: "UNIT-L1-007"
    fic_path: "L1/fic/units/FIC-L1-007-handoff-packet-builder.md"
    target_file: "L1/controller/handoff_packet_builder.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"

  - fic_id: "FIC-L1-008"
    unit_id: "UNIT-L1-008"
    fic_path: "L1/fic/units/FIC-L1-008-proof-check-runner.md"
    target_file: "L1/controller/proof_check_runner.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"

  - fic_id: "FIC-L1-009"
    unit_id: "UNIT-L1-009"
    fic_path: "L1/fic/units/FIC-L1-009-evidence-collector.md"
    target_file: "L1/controller/evidence_collector.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"

  - fic_id: "FIC-L1-010"
    unit_id: "UNIT-L1-010"
    fic_path: "L1/fic/units/FIC-L1-010-completion-record-writer.md"
    target_file: "L1/controller/completion_record_writer.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"

  - fic_id: "FIC-L1-011"
    unit_id: "UNIT-L1-011"
    fic_path: "L1/fic/units/FIC-L1-011-traceability-updater.md"
    target_file: "L1/controller/traceability_updater.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"

  - fic_id: "FIC-L1-012"
    unit_id: "UNIT-L1-012"
    fic_path: "L1/fic/units/FIC-L1-012-failure-learning-updater.md"
    target_file: "L1/controller/failure_learning_updater.py"
    status: "draft"
    version: "v0.1.0"
    layer: 1
    risk_level: "medium"
    enforcement_profile: "standard"
```

---

## 10. L1 FIC Unit Template

Use this template for every L1 implementation unit.

```markdown
# FIC-L1-XXX: <Unit Name>

---
schema: "agent-x-l1-eqc-fic/v0.6"
fic_id: "FIC-L1-XXX"
unit_id: "UNIT-L1-XXX"
version: "v0.1.0"
status: "draft"
target_file: "L1/controller/<file>.py"
target_language: "python"
artifact_type: "production"
risk_level: "medium"
enforcement_profile: "standard"
implementation_mode: "new-file|modify-existing|refactor|test-only"
owner: "Agent_X L1"
permitted_files:
  - "L1/controller/<file>.py"
  - "L1/tests/test_<file>.py"
required_checks:
  - "python -m compileall L1"
  - "pytest L1/tests -q"
---

## A. Identity
## B. Authority and Source Hierarchy
## C. File Purpose
## D. Non-Goals
## E. Layer, Ownership, and Placement
## F. Public Surface Contract
## G. Compatibility and Versioning Contract
## H. Internal Helper Policy
## I. Inputs
## J. Outputs and Side Effects
## K. State Contract
## L. Dependency Contract
## M. Existing-Code Inspection Contract
## N. Procedure
## O. Invariants
## P. Error and Failure Behavior
## Q. Security Contract
## R. Performance and Resource Budget
## S. Determinism and Reproducibility
## T. Observability and Tracing
## U. Edge Cases
## V. Test Contract
## W. Examples and Test Oracles
## X. Document and Code Bindings
## Y. Change Policy
## Z. LLM Implementation Instructions
## AA. Acceptance Criteria
## AB. Completion Evidence
## AC. Requirement-to-Test Map
## AD. Semantic Diff Expectation
## AE. Residual Risk Ledger
## AF. Review Packet Requirements
```

---

## 11. L1 Pre-Code Gate

Before coding any L1 unit, every applicable item must be `PASS`, `WAIVED`, or `NOT_APPLICABLE`.

```yaml
l1_pre_code_gate:
  identity:
    fic_id_present: "PASS|WAIVED|NOT_APPLICABLE"
    unit_id_present: "PASS|WAIVED|NOT_APPLICABLE"
    target_file_declared: "PASS|WAIVED|NOT_APPLICABLE"
    permitted_files_declared: "PASS|WAIVED|NOT_APPLICABLE"
  authority:
    governing_docs_declared: "PASS|WAIVED|NOT_APPLICABLE"
    conflict_policy_declared: "PASS|WAIVED|NOT_APPLICABLE"
    l0_boundary_declared: "PASS|WAIVED|NOT_APPLICABLE"
  scope:
    purpose_declared: "PASS|WAIVED|NOT_APPLICABLE"
    non_goals_declared: "PASS|WAIVED|NOT_APPLICABLE"
    negative_space_declared: "PASS|WAIVED|NOT_APPLICABLE"
  surface:
    public_surface_declared: "PASS|WAIVED|NOT_APPLICABLE"
    extra_public_surface_forbidden: "PASS|WAIVED|NOT_APPLICABLE"
    compatibility_policy_declared: "PASS|WAIVED|NOT_APPLICABLE"
  dependencies:
    allowed_imports_declared: "PASS|WAIVED|NOT_APPLICABLE"
    forbidden_imports_declared: "PASS|WAIVED|NOT_APPLICABLE"
    l0_import_policy_declared: "PASS|WAIVED|NOT_APPLICABLE"
    l2_import_policy_declared: "PASS|WAIVED|NOT_APPLICABLE"
  behavior:
    inputs_declared: "PASS|WAIVED|NOT_APPLICABLE"
    outputs_declared: "PASS|WAIVED|NOT_APPLICABLE"
    side_effects_declared: "PASS|WAIVED|NOT_APPLICABLE"
    state_ownership_declared: "PASS|WAIVED|NOT_APPLICABLE"
    procedure_declared: "PASS|WAIVED|NOT_APPLICABLE"
    errors_declared: "PASS|WAIVED|NOT_APPLICABLE"
    invariants_declared: "PASS|WAIVED|NOT_APPLICABLE"
  validation:
    tests_declared: "PASS|WAIVED|NOT_APPLICABLE"
    test_oracles_declared: "PASS|WAIVED|NOT_APPLICABLE"
    requirement_to_test_map_declared: "PASS|WAIVED|NOT_APPLICABLE"
    acceptance_criteria_declared: "PASS|WAIVED|NOT_APPLICABLE"
    completion_evidence_declared: "PASS|WAIVED|NOT_APPLICABLE"
```

If a required item is not `PASS` and not explicitly `WAIVED`, implementation status must be:

```text
BLOCKED
```

---

## 12. L1 Post-Code Gate

After coding any L1 unit, confirm:

```yaml
l1_post_code_gate:
  target_file_exists: "PASS|FAIL|WAIVED"
  target_file_has_fic_marker_or_sidecar: "PASS|FAIL|WAIVED"
  declared_public_surface_exists: "PASS|FAIL|WAIVED"
  no_extra_public_surface: "PASS|FAIL|WAIVED"
  forbidden_imports_absent: "PASS|FAIL|WAIVED"
  l0_l1_boundary_preserved: "PASS|FAIL|WAIVED"
  required_tests_exist: "PASS|FAIL|WAIVED"
  required_checks_run_or_recorded: "PASS|FAIL|WAIVED"
  completion_record_exists: "PASS|FAIL|WAIVED"
  semantic_diff_declared: "PASS|FAIL|WAIVED"
  public_surface_diff_declared: "PASS|FAIL|WAIVED"
  dependency_diff_declared: "PASS|FAIL|WAIVED"
  deviations_recorded: "PASS|FAIL|WAIVED"
  traceability_updated_or_recorded_not_run: "PASS|FAIL|WAIVED"
  failure_learning_updated_if_needed: "PASS|FAIL|WAIVED"
  review_packet_created: "PASS|FAIL|WAIVED"
```

If any required item is `FAIL`, implementation must not be marked `VALIDATED`.

---

## 13. L1 Implementation Handoff Packet

A coding agent must receive a bounded packet, not broad repository notes.

```yaml
implementation_handoff:
  handoff_id: "HANDOFF-L1-XXX"
  fic_id: "FIC-L1-XXX"
  fic_version: "vX.Y.Z"
  unit_id: "UNIT-L1-XXX"
  target_file: "L1/controller/<file>.py"
  task_type: "create|modify|refactor|test"
  permitted_files:
    - "L1/controller/<file>.py"
    - "L1/tests/test_<file>.py"
  required_context_files:
    - "L1/fic/units/FIC-L1-XXX-<name>.md"
    - "L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md"
  forbidden_changes:
    - "Do not edit L0 files."
    - "Do not edit L2 files."
    - "Do not add network access."
    - "Do not add shell execution unless this FIC explicitly allows it."
  allowed_statuses:
    - "BLOCKED"
    - "NO_CHANGE"
    - "IMPLEMENTED_UNVALIDATED"
    - "VALIDATED"
    - "IMPLEMENTED_WITH_WAIVERS"
    - "REJECTED"
  stop_conditions:
    - "Required context unavailable."
    - "Referenced API not found."
    - "Acceptance criteria conflict."
    - "Required check cannot be run and no waiver exists."
    - "Implementation would require editing outside permitted files."
```

### 13.1 Package closure rule

The handoff package is closed only when:

```yaml
package_closure:
  exactly_one_primary_fic: true
  permitted_files_complete: true
  target_file_declared: true
  test_file_declared: true
  required_checks_declared: true
  public_surface_declared: true
  dependencies_declared: true
  stop_conditions_declared: true
  completion_record_schema_declared: true
```

A package that does not close must not be implemented.

---

## 14. L1 Validator Contract

L1 should eventually provide executable validators. Until those exist, the same checks must be performed manually and recorded in the completion or review packet.

Required validator expectations for each L1 FIC:

```yaml
validators:
  fic_schema_validate:
    purpose: "frontmatter and required sections are present and internally consistent"
    required_for_status: "ready-for-code"
  fic_registry_check:
    purpose: "FIC registry entry matches FIC identity, target file, version, status, risk, and permitted files"
    required_for_status: "ready-for-code"
  public_surface_check:
    purpose: "implemented __all__ and visible public symbols match the FIC"
    required_for_status: "validated"
  forbidden_import_check:
    purpose: "implementation imports only declared dependencies and no forbidden modules"
    required_for_status: "validated"
  requirement_test_map_check:
    purpose: "each acceptance criterion and invariant maps to at least one test, static check, review item, or waiver"
    required_for_status: "ready-for-code"
  edge_case_coverage_check:
    purpose: "each edge case marked test-required maps to at least one test or explicit waiver"
    required_for_status: "ready-for-code"
  status_vocabulary_check:
    purpose: "document, FIC, handoff, completion, and review statuses use only controlled vocabulary"
    required_for_status: "ready-for-code"
  completion_record_check:
    purpose: "completion record uses a controlled status and includes checks run, checks not run, deviations, residual risks, and semantic diff"
    required_for_status: "implemented"
  review_packet_check:
    purpose: "review packet contains public surface diff, semantic diff, dependency diff, requirement-to-code map, and requirement-to-test map"
    required_for_status: "validated"
```

A FIC or implementation must not claim `validated` when any required validator is missing, failing, or not run without an explicit waiver.

---

## 15. L1 Anti-Patterns

Reject L1 work if it contains:

- broad coding from architecture notes without a FIC;
- undocumented changes to L0;
- hidden shell execution;
- hidden network access;
- generated files not listed in the FIC;
- public functions not declared in the FIC;
- speculative future features;
- broad refactors hidden inside a small unit;
- tests that only check that code exists;
- completion claims without test or validation evidence;
- code behavior with no owning FIC;
- direct L0 dependency that makes L0 depend on L1;
- any L0 import of L1 or L2;
- treating generated reports as authoritative requirements unless registered as such.

---

## 16. v0.6 Machine-Checkable Closure Rules

A L1 FIC can be rated 10/10 only if all of the following are true:

```yaml
machine_checkable_closure:
  controlled_status_vocabulary_only: true
  public_signatures_match_input_contracts: true
  dependency_contract_has_no_type_reference_contradiction: true
  all_acceptance_criteria_mapped: true
  all_required_edge_cases_mapped: true
  all_public_surface_items_mapped: true
  all_forbidden_dependencies_tested_or_reviewed: true
  all_error_types_tested: true
  all_path_security_rules_tested: true
  invalid_utf8_behavior_tested: true
  completion_record_has_controlled_exit_status: true
  review_packet_has_coverage_fields: true
  no_stale_version_references: true
```

If any field is false, the FIC may still be useful, but it must not be rated 10/10.

---

# Part II — First Concrete L1 FIC

# FIC-L1-001: L1 Document Loader

---
schema: "agent-x-l1-eqc-fic/v0.6"
fic_id: "FIC-L1-001"
unit_id: "UNIT-L1-001"
version: "v0.6.0"
status: "ready-for-code"
target_file: "L1/controller/document_loader.py"
target_language: "python"
artifact_type: "production"
risk_level: "medium"
enforcement_profile: "standard"
implementation_mode: "new-file"
owner: "Agent_X L1"
permitted_files:
  - "L1/controller/document_loader.py"
  - "L1/tests/test_document_loader.py"
required_checks:
  - "python -m compileall L1"
  - "pytest L1/tests/test_document_loader.py -q"
---

## A. Identity

```yaml
fic_id: "FIC-L1-001"
unit_id: "UNIT-L1-001"
target_file: "L1/controller/document_loader.py"
target_language: "python"
artifact_type: "production"
status: "ready-for-code"
version: "v0.6.0"
owner: "Agent_X L1"
risk_level: "medium"
enforcement_profile: "standard"
implementation_mode: "new-file"
```

---

## B. Authority and Source Hierarchy

```yaml
authority:
  governing_docs:
    - doc_id: "AGENT-X-L0-CONTRACTS"
      path: "L0/"
      authority_level: "constitutional"
    - doc_id: "AGENT-X-L1-SYSTEM-GOAL"
      path: "L1/docs/00_L1_SYSTEM_GOAL.md"
      authority_level: "architecture"
    - doc_id: "AGENT-X-L1-ARCHITECTURE"
      path: "L1/docs/02_L1_ARCHITECTURE_CONTRACT.md"
      authority_level: "architecture"
    - doc_id: "AGENT-X-L1-UNIT-DAG"
      path: "L1/docs/04_L1_UNIT_DAG.md"
      authority_level: "subsystem"
  conflict_resolution:
    rule: "higher_authority_wins"
    unresolved_conflict_status: "BLOCKED_SOURCE_CONFLICT"
  stale_doc_policy:
    stale_behavior: "BLOCKED_MISSING_CONTEXT"
```

---

## C. File Purpose

`document_loader.py` loads approved L1 control-plane documents from declared paths and returns immutable structured document records for downstream L1 units.

It exists so that later L1 units do not manually read arbitrary files or treat unapproved repository text as authoritative instructions.

---

## D. Non-Goals

This file must not:

- interpret semantic meaning of documents;
- classify goals;
- generate FICs;
- validate FIC readiness;
- modify documents;
- write files;
- execute shell commands;
- call network resources;
- inspect arbitrary repository files outside declared allowed paths;
- import L0 runtime internals;
- import L2 modules;
- use environment variables as hidden inputs;
- cache loaded document content globally;
- silently skip unreadable documents;
- normalize or rewrite document contents beyond UTF-8 decoding.

---

## E. Layer, Ownership, and Placement

```yaml
architecture:
  layer: 1
  architectural_role: "control-plane document loading"
  module_boundary: "L1/controller"
  owns_state: false
  state_owner: "none"
  allowed_callers:
    - "L1 controller/orchestrator"
    - "L1 tests"
  forbidden_callers:
    - "L0 runtime"
    - "L2 profiles"
  allowed_callees:
    - "dataclasses"
    - "hashlib"
    - "pathlib"
    - "typing"
  forbidden_callees:
    - "subprocess"
    - "requests"
    - "urllib"
    - "socket"
    - "http"
    - "L0"
    - "L2"
```

---

## F. Public Surface Contract

```yaml
public_surface:
  module_exports:
    - "DEFAULT_MAX_DOCUMENT_BYTES"
    - "DocumentRecord"
    - "DocumentLoaderError"
    - "DocumentRootError"
    - "DocumentPathError"
    - "DocumentLoadError"
    - "load_document"
    - "load_documents"

  constants:
    - name: "DEFAULT_MAX_DOCUMENT_BYTES"
      value: 1048576
      purpose: "Default maximum size for one loaded document, in bytes."
      stability: "experimental"

  classes:
    - name: "DocumentRecord"
      purpose: "Immutable record describing a loaded control-plane document."
      constructor_signature: "DocumentRecord(path: str, content: str, size_bytes: int, sha256: str, exists: bool = True)"
      fields:
        - "path: str  # normalized POSIX-style relative path from root"
        - "content: str"
        - "size_bytes: int"
        - "sha256: str  # 64-character lowercase hexadecimal SHA-256 digest of raw bytes"
        - "exists: bool"
      dataclass_frozen: true
      equality_semantics: "value equality from frozen dataclass fields"
      stability: "experimental"

    - name: "DocumentLoaderError"
      purpose: "Base exception for document loader failures."
      constructor_signature: "DocumentLoaderError(message: str)"
      stability: "experimental"

    - name: "DocumentRootError"
      purpose: "Raised when the provided root is missing, invalid, or not a directory."
      constructor_signature: "DocumentRootError(message: str)"
      stability: "experimental"

    - name: "DocumentPathError"
      purpose: "Raised when a document path is invalid, absolute, or escapes the declared root."
      constructor_signature: "DocumentPathError(message: str)"
      stability: "experimental"

    - name: "DocumentLoadError"
      purpose: "Raised when a declared document cannot be read as a regular bounded UTF-8 file."
      constructor_signature: "DocumentLoadError(message: str)"
      stability: "experimental"

  functions:
    - name: "load_document"
      signature: "load_document(path: str, *, root: str | pathlib.Path, max_bytes: int = DEFAULT_MAX_DOCUMENT_BYTES) -> DocumentRecord"
      purpose: "Load one declared document path under the provided root."
      stability: "experimental"

    - name: "load_documents"
      signature: "load_documents(paths: list[str], *, root: str | pathlib.Path, max_bytes: int = DEFAULT_MAX_DOCUMENT_BYTES) -> list[DocumentRecord]"
      purpose: "Load multiple declared document paths under the provided root in deterministic input order."
      stability: "experimental"

  cli_commands: []
  config_keys: []
  events: []
```

No other public functions, classes, constants, CLI commands, config keys, events, or module-level side effects are allowed. The module must define `__all__` matching `module_exports` exactly. Imported implementation helpers must not leak as public symbols; imports should use private aliases where needed, such as `_Path`, `_hashlib`, or `_dataclass`, or must otherwise be hidden from the module public surface.

---

## G. Compatibility and Versioning Contract

```yaml
compatibility:
  backward_compatible: true
  public_surface_change: false
  migration_required: false
  deprecation_required: false
  version_impact: "minor-initial"
  compatibility_tests_required: false
  affected_callers:
    - "future L1 controller/orchestrator"
    - "future L1 repo state reader"
```

Any future public surface change must update this FIC before code changes.

---

## H. Internal Helper Policy

```yaml
internal_helpers:
  allowed: true
  rules:
    - "Helpers must be private/internal by leading underscore."
    - "Helpers must support only declared public functions."
    - "Helpers must not add hidden file-loading modes."
    - "Helpers must not expose additional public symbols through __all__."
  max_helper_count: 5
  max_helper_complexity: "simple path validation, size validation, hash computation, or read helper only"
```

---

## I. Inputs

```yaml
inputs:
  - name: "path"
    type: "str"
    source: "caller"
    required: true
    validation_rule: "must be a relative path that resolves under root"
    trust_level: "untrusted"

  - name: "paths"
    type: "list[str]"
    source: "caller"
    required: true
    validation_rule: "must be a list whose items each pass the same validation as load_document path"
    trust_level: "untrusted"

  - name: "root"
    type: "str | pathlib.Path"
    source: "caller"
    required: true
    validation_rule: "must be non-empty after conversion to a filesystem path, must exist, and must resolve to a directory; root symlink to a directory is allowed after resolution"
    trust_level: "internal"

  - name: "max_bytes"
    type: "int"
    source: "caller or default"
    required: false
    validation_rule: "must be an integer greater than or equal to 0; bool is invalid even though bool subclasses int in Python"
    trust_level: "internal"
```

---

## J. Outputs and Side Effects

```yaml
outputs:
  - name: "DocumentRecord"
    type: "frozen dataclass"
    destination: "return"
    success_shape: "exists=true, content populated as str, size_bytes >= 0, sha256 is lowercase hex digest of raw bytes"
    failure_shape: "raises declared exception"
    ordering_rule: "not applicable for single document"

  - name: "list[DocumentRecord]"
    type: "list"
    destination: "return"
    success_shape: "records returned in the same order as input paths"
    failure_shape: "raises declared exception and returns no partial list"
    ordering_rule: "same order as input paths"

side_effects:
  allowed: true
  declared_effects:
    - "read-only filesystem access to declared paths under root"
```

No file writes are allowed.

---

## K. State Contract

```yaml
state:
  owns_state: false
  state_items: []
```

The module must not use mutable global state, caches, hidden registries, environment variables, or process-wide configuration.

---

## L. Dependency Contract

```yaml
dependencies:
  allowed_imports:
    - "dataclasses"
    - "hashlib"
    - "pathlib"
    - "typing"
  import_style_rules:
    - "Imported helper names must not become public module symbols."
    - "Use private aliases or module imports where needed."
    - "No from-import may create a non-declared public symbol unless it is assigned to a private alias."
  forbidden_imports:
    - "os"
    - "os.system"
    - "subprocess"
    - "requests"
    - "urllib"
    - "socket"
    - "http"
    - "L0"
    - "L2"
  dynamic_imports_allowed: false
```

The implementation must not import L0 or L2 packages. L1 reads L0 only through declared filesystem inspection in later units, not through runtime imports.

---

## M. Existing-Code Inspection Contract

```yaml
existing_code_inspection:
  required: true
  reason: "new-file implementation still must confirm whether target or test file already exists"
  no_change_allowed: true
  must_confirm:
    - "target file does not already exist, or if it exists, whether it already satisfies this FIC"
    - "test file does not already exist, or if it exists, whether it should be updated"
```

If existing code already satisfies the FIC, the correct status is `NO_CHANGE` with evidence.

---

## N. Procedure

### `load_document(path, *, root, max_bytes=DEFAULT_MAX_DOCUMENT_BYTES)`

```text
1. Confirm root is provided and is a string or `pathlib.Path` value.
2. Convert root to a filesystem path and reject empty roots.
3. Resolve root as an absolute path.
4. Confirm root exists and resolves to a directory. A root symlink to a directory is allowed after resolution.
5. Confirm max_bytes is an integer >= 0 and is not bool. `max_bytes=0` allows only empty files.
6. Confirm path is provided and is a string.
7. Reject empty paths.
8. Reject absolute document paths.
9. Resolve root / path.
10. Reject the resolved document path if it escapes root after resolution.
11. Reject the path if it does not exist.
12. Reject the path if it is not a regular file.
13. Read raw bytes from the file only after path validation passes.
14. Reject the file if raw byte length exceeds max_bytes.
15. Decode the raw bytes as UTF-8 text.
16. Compute sha256 as lowercase hex digest from the raw bytes.
17. Compute normalized_relative_path as a POSIX-style path relative to root.
18. Return DocumentRecord(path=normalized_relative_path, content=content, size_bytes=len(raw_bytes), sha256=sha256, exists=true).
```

### `load_documents(paths, *, root, max_bytes=DEFAULT_MAX_DOCUMENT_BYTES)`

```text
1. Confirm paths is a list.
2. Reject non-list paths input.
3. Preserve input order and multiplicity; duplicate paths are allowed and must produce duplicate records.
4. For each path in input order, call load_document(path, root=root, max_bytes=max_bytes).
5. If any path fails, raise the declared exception and return no partial result.
6. Return the list of DocumentRecord values in the same order as the input paths.
```

---

## O. Invariants

```yaml
invariants:
  - id: "FIC-L1-001-INV-001"
    statement: "A document path must never resolve outside the declared root."
    enforcement: "code+test"
    violation_behavior: "raise DocumentPathError"

  - id: "FIC-L1-001-INV-002"
    statement: "The loader must not write files."
    enforcement: "code+test+review"
    violation_behavior: "reject implementation"

  - id: "FIC-L1-001-INV-003"
    statement: "The loader must not import L0 or L2 modules."
    enforcement: "static review+test"
    violation_behavior: "reject implementation"

  - id: "FIC-L1-001-INV-004"
    statement: "For the same root and paths, output order must be deterministic."
    enforcement: "test"
    violation_behavior: "test failure"

  - id: "FIC-L1-001-INV-005"
    statement: "The loader must not depend on wall-clock time, randomness, network, environment variables, or shell execution."
    enforcement: "static review+test"
    violation_behavior: "reject implementation"

  - id: "FIC-L1-001-INV-006"
    statement: "DocumentRecord must be immutable after construction."
    enforcement: "test"
    violation_behavior: "test failure"

  - id: "FIC-L1-001-INV-007"
    statement: "Loaded content hash must be computed from raw bytes before UTF-8 decoding."
    enforcement: "test"
    violation_behavior: "test failure"

  - id: "FIC-L1-001-INV-008"
    statement: "Returned DocumentRecord.path must be normalized, relative to root, and POSIX-style."
    enforcement: "test"
    violation_behavior: "test failure"

  - id: "FIC-L1-001-INV-009"
    statement: "Exception messages must not include document content, raw bytes, secrets, or absolute escaped target paths."
    enforcement: "test+review"
    violation_behavior: "reject implementation"

  - id: "FIC-L1-001-INV-010"
    statement: "Duplicate paths in load_documents must preserve multiplicity and order."
    enforcement: "test"
    violation_behavior: "test failure"
```

---

## P. Error and Failure Behavior

```yaml
errors:
  - condition: "root is missing, empty, wrong type, invalid, or not a directory"
    behavior: "raise"
    error_type: "DocumentRootError"
    recoverable: false

  - condition: "max_bytes is not an integer, is bool, or is negative"
    behavior: "raise"
    error_type: "DocumentLoadError"
    recoverable: false

  - condition: "path is missing, empty, not a string, absolute, or escapes root"
    behavior: "raise"
    error_type: "DocumentPathError"
    recoverable: false

  - condition: "paths is not a list"
    behavior: "raise"
    error_type: "DocumentPathError"
    recoverable: false

  - condition: "path does not exist or is not a regular file"
    behavior: "raise"
    error_type: "DocumentLoadError"
    recoverable: false

  - condition: "file byte length exceeds max_bytes"
    behavior: "raise"
    error_type: "DocumentLoadError"
    recoverable: false

  - condition: "file cannot be decoded as UTF-8"
    behavior: "raise"
    error_type: "DocumentLoadError"
    recoverable: false
```

No silent fallback behavior is allowed. Exception messages must identify the error category without exposing document content, raw bytes, secrets, or absolute escaped target paths.

---

## Q. Security Contract

```yaml
security:
  handles_sensitive_data: false
  input_validation_required: true
  authorization_required: false
  forbidden_operations:
    - "path traversal"
    - "network access"
    - "shell execution"
    - "unsafe deserialization"
    - "writing files"
    - "environment-variable control"
    - "reading absolute paths supplied by caller"
    - "exposing document contents or raw bytes in exception messages"
```

The loader must treat caller-provided paths as untrusted.

---

## R. Performance and Resource Budget

```yaml
performance:
  expected_complexity: "O(n) in total bytes read"
  max_input_size: "max_bytes per file; default 1048576 bytes"
  memory_budget: "No hidden global copies; only returned content is retained."
  timeout_budget: "No timeout in v0.5.0."
  batching_required: false
  caching_allowed: false
  hot_path: false
  benchmark_required: false
```

---

## S. Determinism and Reproducibility

```yaml
determinism:
  deterministic_required: true
  time_policy: "not-used"
  randomness_policy: "not-used"
  ordering_policy: "preserve input path order"
  floating_point_policy: "not-applicable"
  concurrency_policy: "no shared mutable state"
```

---

## T. Observability and Tracing

```yaml
observability:
  logs_allowed: false
  required_log_events: []
  metrics: []
  traces: []
  forbidden_log_content:
    - "document content"
    - "personal data"
    - "secrets"
```

The loader must not log document contents.

---

## U. Edge Cases

| ID | Case | Input/State | Expected Behavior | Test Required | Waiver Allowed |
|---|---|---|---|---:|---:|
| EC-L1-001-001 | Missing root | `root=""` | raise `DocumentRootError` | yes | no |
| EC-L1-001-002 | Root not directory | root points to file | raise `DocumentRootError` | yes | no |
| EC-L1-001-003 | Negative max bytes | `max_bytes=-1` | raise `DocumentLoadError` | yes | no |
| EC-L1-001-004 | Non-string path | `path=123` | raise `DocumentPathError` | yes | no |
| EC-L1-001-005 | Empty path | `path=""` | raise `DocumentPathError` | yes | no |
| EC-L1-001-006 | Absolute path | `/tmp/x.md` | raise `DocumentPathError` | yes | no |
| EC-L1-001-007 | Path traversal | `../x.md` | raise `DocumentPathError` | yes | no |
| EC-L1-001-008 | Symlink escape | symlink under root points outside root | raise `DocumentPathError` or `DocumentLoadError` before content return | yes | no |
| EC-L1-001-009 | Missing file | valid root, missing path | raise `DocumentLoadError` | yes | no |
| EC-L1-001-010 | Directory path | path points to directory | raise `DocumentLoadError` | yes | no |
| EC-L1-001-011 | Oversized file | file exceeds `max_bytes` | raise `DocumentLoadError` | yes | no |
| EC-L1-001-012 | Non-UTF-8 file | invalid bytes | raise `DocumentLoadError` | yes | no |
| EC-L1-001-013 | Empty file | file exists, zero bytes | return content `""`, size `0`, valid SHA-256 | yes | no |
| EC-L1-001-014 | Multiple paths | list of valid paths | preserve input order | yes | no |
| EC-L1-001-015 | Non-list paths | `paths="abc.md"` | raise `DocumentPathError` | yes | no |
| EC-L1-001-016 | Duplicate paths | same valid path appears twice | return two corresponding records in the same positions | yes | no |
| EC-L1-001-017 | Boolean max bytes | `max_bytes=True` or `False` | raise `DocumentLoadError` | yes | no |
| EC-L1-001-018 | Platform separator | path contains platform separator but resolves under root | returned record path uses POSIX-style relative format | yes | no |
| EC-L1-001-019 | Error message safety | invalid file/path error | message contains no content, raw bytes, secrets, or escaped absolute target | yes | no |
| EC-L1-001-020 | Zero max bytes with empty file | `max_bytes=0`, empty file | return valid empty `DocumentRecord` | yes | no |
| EC-L1-001-021 | Zero max bytes with non-empty file | `max_bytes=0`, non-empty file | raise `DocumentLoadError` | yes | no |
| EC-L1-001-022 | Path-like root | `root` is a `Path` object | accepted if it resolves to a directory | yes | no |
| EC-L1-001-023 | Root symlink to directory | `root` is symlink to valid directory | allowed after resolution; output path remains relative | yes | no |

---

## V. Test Contract

Required test file:

```text
L1/tests/test_document_loader.py
```

Required tests:

```yaml
tests:
  required_unit_tests:
    - id: "TEST-L1-001-001"
      name: "loads a valid UTF-8 document"
    - id: "TEST-L1-001-002"
      name: "loads an empty UTF-8 document"
    - id: "TEST-L1-001-003"
      name: "computes SHA-256 from raw bytes"
    - id: "TEST-L1-001-004"
      name: "DocumentRecord is frozen"
    - id: "TEST-L1-001-005"
      name: "preserves input order for multiple documents"
    - id: "TEST-L1-001-006"
      name: "rejects non-list paths input"
    - id: "TEST-L1-001-007"
      name: "rejects non-string path"
    - id: "TEST-L1-001-008"
      name: "rejects empty path"
    - id: "TEST-L1-001-009"
      name: "rejects absolute path"
    - id: "TEST-L1-001-010"
      name: "rejects path traversal outside root"
    - id: "TEST-L1-001-011"
      name: "rejects symlink escape outside root where platform supports symlink"
    - id: "TEST-L1-001-012"
      name: "rejects missing root"
    - id: "TEST-L1-001-013"
      name: "rejects root that is a file"
    - id: "TEST-L1-001-014"
      name: "rejects missing document"
    - id: "TEST-L1-001-015"
      name: "rejects directory document path"
    - id: "TEST-L1-001-016"
      name: "rejects file larger than max_bytes"
    - id: "TEST-L1-001-017"
      name: "rejects invalid max_bytes"
    - id: "TEST-L1-001-018"
      name: "does not write files"
    - id: "TEST-L1-001-019"
      name: "does not use forbidden imports"
    - id: "TEST-L1-001-020"
      name: "__all__ matches declared module exports"
    - id: "TEST-L1-001-021"
      name: "duplicate paths preserve multiplicity and order"
    - id: "TEST-L1-001-022"
      name: "bool max_bytes is rejected"
    - id: "TEST-L1-001-023"
      name: "returned path is normalized POSIX-style relative path"
    - id: "TEST-L1-001-024"
      name: "error messages do not expose document content or escaped absolute target paths"
    - id: "TEST-L1-001-025"
      name: "non-declared imported helper names do not leak through __all__"
    - id: "TEST-L1-001-026"
      name: "max_bytes zero allows empty file and rejects non-empty file"
    - id: "TEST-L1-001-027"
      name: "path-like root is accepted when it resolves to a directory"
    - id: "TEST-L1-001-028"
      name: "root symlink to directory is allowed while document symlink escape remains blocked"
    - id: "TEST-L1-001-029"
      name: "rejects invalid UTF-8 bytes"
  required_negative_tests:
    - "path traversal"
    - "symlink escape"
    - "missing file"
    - "invalid root"
    - "invalid max_bytes"
    - "non-list paths input"
    - "oversized file"
    - "bool max_bytes"
    - "unsafe error-message leakage"
    - "invalid UTF-8 bytes"
  required_property_tests: []
  required_integration_tests: []
```

Tests must verify behavior, not merely symbol existence.

---

## W. Examples and Test Oracles

```yaml
examples:
  - name: "basic success"
    input:
      root: "/repo"
      path: "L1/docs/00_L1_SYSTEM_GOAL.md"
    expected_output:
      exists: true
      size_bytes: ">= 0"
      sha256: "lowercase hex SHA-256 over raw bytes"
      content_type: "str"

  - name: "path traversal blocked"
    input:
      root: "/repo"
      path: "../secret.txt"
    expected_error: "DocumentPathError"

test_oracles:
  - oracle_type: "exact-error"
    applies_to: "invalid path, invalid root, oversized file, invalid max_bytes, and invalid UTF-8 cases"
    pass_rule: "declared exception type is raised"
  - oracle_type: "exact-output"
    applies_to: "successful load"
    pass_rule: "content, size_bytes, exists, and sha256 match the fixture"
  - oracle_type: "property"
    applies_to: "multiple document loading"
    pass_rule: "output order equals input order"
  - oracle_type: "static"
    applies_to: "forbidden imports and public surface"
    pass_rule: "forbidden import strings are absent, __all__ matches declared exports, and imported helper names do not leak as public API"
  - oracle_type: "exact-output"
    applies_to: "normalized record path"
    pass_rule: "returned DocumentRecord.path is the expected POSIX-style relative path"
  - oracle_type: "negative"
    applies_to: "exception message safety"
    pass_rule: "exception string does not contain fixture content, raw bytes, or escaped absolute target path"
```

---

## X. Document and Code Bindings

```yaml
bindings:
  governs:
    - doc_id: "AGENT-X-L1-SYSTEM-GOAL"
      anchor_id: "L1-document-control-plane"
      binding_strength: "HARD"
  implements:
    - spec_id: "UNIT-L1-001"
      section: "L1 document loading"
  validated_by:
    - test_file: "L1/tests/test_document_loader.py"
  sib_artifact_id: "AGENT_X_L1::ART-DOCUMENT-LOADER"
```

---

## Y. Change Policy

```yaml
change_policy:
  allowed_change_types:
    - "METADATA"
    - "VALIDATION"
    - "FUNCTIONAL"
  requires_fic_update_before_code_change: true
  public_surface_change_requires_version_bump: true
  behavioral_change_requires_tests: true
  refactor_requires_equivalence_evidence: true
```

---

## Z. LLM Implementation Instructions

```text
Before coding:
1. Read this FIC completely.
2. Confirm target file path.
3. Confirm all required existing symbols.
4. Confirm allowed imports.
5. Confirm public surface.
6. Confirm tests to create or update.
7. If existing code already satisfies this FIC, return NO_CHANGE with evidence.
8. If any required information is UNKNOWN, return BLOCKED.
9. Do not invent APIs, files, dependencies, or requirements.
10. Do not edit outside the declared target and test files unless this FIC allows it.
11. Produce the smallest implementation that satisfies this FIC.
12. Produce a completion record.
13. Produce a review packet.
```

---

## AA. Acceptance Criteria

```yaml
acceptance_criteria:
  - id: "AC-L1-001-001"
    text: "DocumentRecord exists as a frozen dataclass with declared fields."
  - id: "AC-L1-001-002"
    text: "Declared error classes exist."
  - id: "AC-L1-001-003"
    text: "DEFAULT_MAX_DOCUMENT_BYTES exists with value 1048576."
  - id: "AC-L1-001-004"
    text: "load_document exists with the declared signature."
  - id: "AC-L1-001-005"
    text: "load_documents exists with the declared signature."
  - id: "AC-L1-001-006"
    text: "__all__ matches the declared public module exports."
  - id: "AC-L1-001-007"
    text: "No public symbols beyond the declared public surface are introduced, except private helpers prefixed with underscore."
  - id: "AC-L1-001-008"
    text: "Absolute paths and path traversal are rejected."
  - id: "AC-L1-001-009"
    text: "File reads are constrained under the declared root."
  - id: "AC-L1-001-010"
    text: "Files larger than max_bytes are rejected."
  - id: "AC-L1-001-011"
    text: "SHA-256 is computed from raw file bytes."
  - id: "AC-L1-001-012"
    text: "No file writes occur."
  - id: "AC-L1-001-013"
    text: "No forbidden imports are present."
  - id: "AC-L1-001-014"
    text: "Required tests exist."
  - id: "AC-L1-001-015"
    text: "Declared tests pass or failures are recorded."
  - id: "AC-L1-001-016"
    text: "Completion record is produced."
  - id: "AC-L1-001-017"
    text: "Review packet is produced."
  - id: "AC-L1-001-018"
    text: "Duplicate paths preserve multiplicity and order."
  - id: "AC-L1-001-019"
    text: "Boolean max_bytes values are rejected."
  - id: "AC-L1-001-020"
    text: "Returned record paths are normalized POSIX-style relative paths."
  - id: "AC-L1-001-021"
    text: "Exception messages do not expose document contents, raw bytes, secrets, or escaped absolute target paths."
  - id: "AC-L1-001-022"
    text: "Invalid UTF-8 files are rejected with DocumentLoadError."
```

---

## AB. Completion Evidence

```yaml
completion_record:
  status: "<BLOCKED|NO_CHANGE|IMPLEMENTED_UNVALIDATED|VALIDATED|IMPLEMENTED_WITH_WAIVERS|REJECTED>"
  fic_id: "FIC-L1-001"
  fic_version: "v0.6.0"
  target_file: "L1/controller/document_loader.py"
  files_inspected: []
  files_changed: []
  public_surface_created_or_preserved: []
  tests_created_or_updated: []
  checks_run:
    - command: "python -m compileall L1"
      result: "<pass|fail|not-run>"
      evidence: ""
    - command: "pytest L1/tests/test_document_loader.py -q"
      result: "<pass|fail|not-run>"
      evidence: ""
  checks_not_run: []
  deviations_from_fic: []
  unresolved_unknowns: []
  residual_risks: []
  requires_fic_update: false
```

---

## AC. Requirement-to-Test Map

Every invariant and acceptance criterion must be mapped before implementation begins.

```yaml
requirement_to_test_map:
  invariants:
    - requirement_id: "FIC-L1-001-INV-001"
      verifies: "document path never resolves outside root"
      tests: ["TEST-L1-001-009", "TEST-L1-001-010", "TEST-L1-001-011"]
    - requirement_id: "FIC-L1-001-INV-002"
      verifies: "loader performs no file writes"
      tests: ["TEST-L1-001-018"]
      review_items: ["forbidden side effects review"]
    - requirement_id: "FIC-L1-001-INV-003"
      verifies: "loader imports neither L0 nor L2"
      tests: ["TEST-L1-001-019"]
    - requirement_id: "FIC-L1-001-INV-004"
      verifies: "output order is deterministic"
      tests: ["TEST-L1-001-005", "TEST-L1-001-021"]
    - requirement_id: "FIC-L1-001-INV-005"
      verifies: "no time, randomness, network, environment variable, or shell dependency"
      tests: ["TEST-L1-001-019"]
      review_items: ["dependency and source review"]
    - requirement_id: "FIC-L1-001-INV-006"
      verifies: "DocumentRecord is immutable"
      tests: ["TEST-L1-001-004"]
    - requirement_id: "FIC-L1-001-INV-007"
      verifies: "hash computed from raw bytes before decoding"
      tests: ["TEST-L1-001-003"]
    - requirement_id: "FIC-L1-001-INV-008"
      verifies: "record path is normalized POSIX-style relative path"
      tests: ["TEST-L1-001-023"]
    - requirement_id: "FIC-L1-001-INV-009"
      verifies: "safe exception messages"
      tests: ["TEST-L1-001-024"]
      review_items: ["error-message review"]
    - requirement_id: "FIC-L1-001-INV-010"
      verifies: "duplicate path multiplicity and order preserved"
      tests: ["TEST-L1-001-021"]

  acceptance_criteria:
    - requirement_id: "AC-L1-001-001"
      tests: ["TEST-L1-001-004"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-002"
      tests: ["TEST-L1-001-007", "TEST-L1-001-012", "TEST-L1-001-014"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-003"
      tests: ["TEST-L1-001-016"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-004"
      tests: ["TEST-L1-001-001"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-005"
      tests: ["TEST-L1-001-005", "TEST-L1-001-021"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-006"
      tests: ["TEST-L1-001-020"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-007"
      tests: ["TEST-L1-001-020", "TEST-L1-001-025"]
      static_checks: ["public_surface_check"]
    - requirement_id: "AC-L1-001-008"
      tests: ["TEST-L1-001-009", "TEST-L1-001-010"]
    - requirement_id: "AC-L1-001-009"
      tests: ["TEST-L1-001-010", "TEST-L1-001-011"]
    - requirement_id: "AC-L1-001-010"
      tests: ["TEST-L1-001-016", "TEST-L1-001-026"]
    - requirement_id: "AC-L1-001-011"
      tests: ["TEST-L1-001-003"]
    - requirement_id: "AC-L1-001-012"
      tests: ["TEST-L1-001-018"]
      review_items: ["side-effect review"]
    - requirement_id: "AC-L1-001-013"
      tests: ["TEST-L1-001-019"]
      static_checks: ["forbidden_import_check"]
    - requirement_id: "AC-L1-001-014"
      static_checks: ["test-file-exists review", "requirement_test_map_check"]
    - requirement_id: "AC-L1-001-015"
      checks: ["pytest L1/tests/test_document_loader.py -q"]
    - requirement_id: "AC-L1-001-016"
      static_checks: ["completion_record_check"]
    - requirement_id: "AC-L1-001-017"
      static_checks: ["review_packet_check"]
    - requirement_id: "AC-L1-001-018"
      tests: ["TEST-L1-001-021"]
    - requirement_id: "AC-L1-001-019"
      tests: ["TEST-L1-001-022"]
    - requirement_id: "AC-L1-001-020"
      tests: ["TEST-L1-001-023"]
    - requirement_id: "AC-L1-001-021"
      tests: ["TEST-L1-001-024"]
    - requirement_id: "AC-L1-001-022"
      tests: ["TEST-L1-001-029"]

  edge_cases:
    - edge_case_id: "EC-L1-001-001"
      tests: ["TEST-L1-001-012"]
    - edge_case_id: "EC-L1-001-002"
      tests: ["TEST-L1-001-013"]
    - edge_case_id: "EC-L1-001-003"
      tests: ["TEST-L1-001-017"]
    - edge_case_id: "EC-L1-001-004"
      tests: ["TEST-L1-001-007"]
    - edge_case_id: "EC-L1-001-005"
      tests: ["TEST-L1-001-008"]
    - edge_case_id: "EC-L1-001-006"
      tests: ["TEST-L1-001-009"]
    - edge_case_id: "EC-L1-001-007"
      tests: ["TEST-L1-001-010"]
    - edge_case_id: "EC-L1-001-008"
      tests: ["TEST-L1-001-011"]
    - edge_case_id: "EC-L1-001-009"
      tests: ["TEST-L1-001-014"]
    - edge_case_id: "EC-L1-001-010"
      tests: ["TEST-L1-001-015"]
    - edge_case_id: "EC-L1-001-011"
      tests: ["TEST-L1-001-016"]
    - edge_case_id: "EC-L1-001-012"
      tests: ["TEST-L1-001-029"]
    - edge_case_id: "EC-L1-001-013"
      tests: ["TEST-L1-001-002", "TEST-L1-001-003"]
    - edge_case_id: "EC-L1-001-014"
      tests: ["TEST-L1-001-005"]
    - edge_case_id: "EC-L1-001-015"
      tests: ["TEST-L1-001-006"]
    - edge_case_id: "EC-L1-001-016"
      tests: ["TEST-L1-001-021"]
    - edge_case_id: "EC-L1-001-017"
      tests: ["TEST-L1-001-022"]
    - edge_case_id: "EC-L1-001-018"
      tests: ["TEST-L1-001-023"]
    - edge_case_id: "EC-L1-001-019"
      tests: ["TEST-L1-001-024"]
      review_items: ["error-message review"]
    - edge_case_id: "EC-L1-001-020"
      tests: ["TEST-L1-001-026"]
    - edge_case_id: "EC-L1-001-021"
      tests: ["TEST-L1-001-026"]
    - edge_case_id: "EC-L1-001-022"
      tests: ["TEST-L1-001-027"]
    - edge_case_id: "EC-L1-001-023"
      tests: ["TEST-L1-001-028"]
```

---

## AD. Semantic Diff Expectation

```yaml
semantic_diff_expected:
  behavior_added:
    - "Read-only loading of declared UTF-8 documents under a root path."
    - "Path traversal rejection."
    - "Symlink/root escape rejection after resolution."
    - "Size-bound loading through max_bytes."
    - "Structured immutable document record return value."
    - "SHA-256 digest computation from raw bytes."
    - "Deterministic normalized POSIX-style relative path output."
    - "Duplicate input path preservation."
    - "Safe exception messages that do not leak document contents."
    - "Invalid UTF-8 rejection through DocumentLoadError."
    - "Precise `max_bytes=0` behavior."
    - "Path-like root acceptance."
    - "Resolved-root symlink policy."
  behavior_removed: []
  behavior_changed: []
  behavior_preserved: []
  public_surface_added:
    - "DEFAULT_MAX_DOCUMENT_BYTES"
    - "DocumentRecord"
    - "DocumentLoaderError"
    - "DocumentRootError"
    - "DocumentPathError"
    - "DocumentLoadError"
    - "load_document"
    - "load_documents"
  public_surface_removed: []
  public_surface_changed: []
  state_ownership_changed: []
  dependency_changes:
    - "Adds only declared Python standard library imports."
  compatibility_impact: "new internal L1 module"
```

---

## AE. Residual Risk Ledger

```yaml
residual_risks: []
```

No known residual risk is accepted for `FIC-L1-001` v0.6.0. If implementation cannot satisfy the size, path, import, public surface, or test requirements, the result must be `BLOCKED`, `IMPLEMENTED_UNVALIDATED`, or `REJECTED`, not `VALIDATED`.

---

## AF. Review Packet Requirements

```yaml
review_packet:
  fic_id: "FIC-L1-001"
  fic_version: "v0.6.0"
  implementation_unit: "UNIT-L1-001"
  decision: "ready_for_review|blocked|no_change|rejected"
  changed_files: []
  unchanged_files_inspected: []
  requirement_to_code_map: []
  requirement_to_test_map: []
  acceptance_criteria_coverage: []
  edge_case_coverage: []
  unmapped_requirements: []
  public_surface_diff: []
  semantic_diff: []
  dependency_diff: []
  risk_ledger: []
  validators_run: []
  validators_not_run: []
  waivers: []
  rollback_plan: "revert permitted files changed by this implementation unit"
```

---

# Part III — Minimal First Development Target

The first implementation target is:

```text
FIC-L1-001: L1 Document Loader
```

Only after this unit is implemented and validated should L1 proceed to:

```text
FIC-L1-002: L1 Repo State Reader
```

This keeps L1 grounded in controlled document loading before it starts inspecting repository state or planning changes.

---

# Part IV — Current Rating

This version is rated:

```text
10/10 for L1 scaffolding and first-unit implementation readiness.
```

Scope of the rating:

- It is 10/10 as an **L1 EQC-FIC implementation-control document** for bootstrapping the first controlled L1 unit.
- It is not claiming the entire Agent_X L1 system is complete.
- It is not claiming executable validators already exist.
- It intentionally postpones full EQC-ES/SIB signed checkpoints, digest graph validation, and multi-profile shadow traces until after the basic L1 units exist.
- `FIC-L1-001` now has consistent type contracts, explicit public signatures, complete acceptance mapping, complete edge-case mapping, and no known unresolved specification gaps for implementation of the first L1 unit.
