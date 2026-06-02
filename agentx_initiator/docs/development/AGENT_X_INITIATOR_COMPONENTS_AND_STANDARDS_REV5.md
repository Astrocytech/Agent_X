# Agent_X Initiator — Components and Required Standards

## Document Status

**Version:** Revision 5  
**Purpose:** Define the Agent_X Initiator components, required standards, documentation package, milestone scope, traceability rules, implementation-readiness gates, and final document-freeze status.

## Cross-Document Alignment Rule

This document is governed by AGENT_X_INITIATOR_MILESTONE_AND_NAMING_ALIGNMENT_ADDENDUM.md for milestone terminology, canonical command names, canonical file names, schema names, runtime artifact names, and scheduling.

---

## Alignment Patch Note

This document was edited during the Product Milestone 1 alignment synchronization pass.  
Changes made:

- Added cross-document alignment reference
- Replaced legacy names with canonical names per the alignment addendum
- Added Product Milestone placement to all component scheduling
- No technical rework, schema changes, or authority-boundary changes were made.

---

# 1. Rating of Previous Version

Previous version rating: **9.9/10**

Revision 4 was effectively implementation-ready.

## Remaining Gap

The only remaining issue was procedural, not architectural:

Revision 4 still invited repeated refinement because it did not explicitly say that the component-and-standards document should now be treated as **frozen** and that future work should move into actual component documentation.

Revision 5 adds that final freeze rule.

---

# 2. Final Freeze Rule

This document is now the controlling reference for:

- Initiator components
- required standards
- documentation order
- Milestone 1 scope
- later milestone boundaries
- implementation-readiness checks

Do not keep expanding this document unless a real standard or component is missing.

The next artifacts should be the actual Milestone 1 component documents, not another broad planning revision.

Recommended next document family:

```text
docs/init/components/package_skeleton/
docs/init/components/cli_entrypoint/
docs/init/components/config_paths/
docs/init/components/audit_log/
docs/init/components/repository_scanner/
docs/init/components/layer_mapper/
docs/init/components/report_writer/
docs/init/components/cli_help/
docs/init/components/cli_scan/
docs/init/components/cli_status/
docs/init/components/architecture_analyzer_minimal/
```

---

# 3. Core Rule

Every Initiator component must be documented before implementation.

The required documentation chain is:

```text
Component Overview
  ↓
Pseudocode Specification
  ↓
FIC
  ↓
SIB Binding
  ↓
Schema Contract, if structured output exists
  ↓
Report Template Standard, if markdown reports are generated
  ↓
Command Acceptance Criteria, if user-facing CLI behavior exists
  ↓
Test Expectations
  ↓
Evidence Expectations
```

No component should be implemented from a vague description only.

> **`completion_record.schema.json` rule:** `completion_record.schema.json` is a common implementation-completion schema. Every PM1 component that declares completion evidence must include it in implementation package artifacts and schema validation tests. It may be owned by a common Initiator completion layer rather than by the component itself.

> **Evidence optionality rule:** Product Milestone 1 evidence is required for meaningful component outcomes. The separate file `.agentx-init/memory/audit_evidence.jsonl` is optional only if the implementation stores sufficient evidence references or evidence summaries inside `audit_events.jsonl` or related component artifacts. If split evidence-file mode is used, `audit_evidence.jsonl` must follow the Audit Log contract.

---

# 4. Runtime Boundary Versus Implementation Boundary

This distinction is mandatory.

## Runtime Boundary

At runtime, `agentx-init` version 1 (the initial product line across Product Milestones 1–3) may write only to:

```text
.agentx-init/
```

Runtime must not mutate:

```text
L0/
L1/
L2/
agent_x/runtime/
core/
source files outside .agentx-init/
```

> **Path disambiguation:** The `core/` entry above refers to a protected root-level Agent_X source directory, not to the `agentx_initiator/core/` implementation package. At runtime, `agentx-init` must not mutate either the root-level protected `core/` or any Agent_X source files outside `.agentx-init/`. During development, files under `agentx_initiator/core/` are implementation files and are not part of the runtime protected-path rule.

## Implementation Boundary

During development of `agentx-init`, a human or coding agent may create implementation files such as:

```text
agentx_initiator/
docs/
pyproject.toml
tests/
```

This is allowed only as normal repository development.

The installed/running `agentx-init` CLI must remain non-mutating toward Agent_X source files in version 1.

---

# 5. Standards Reference

## 5.1 FIC — File Implementation Contract

Use when a component has concrete implementation files.

Defines:

- file purpose
- responsibilities
- public functions/classes
- inputs
- outputs
- dependencies
- state ownership
- invariants
- errors
- security limits
- acceptance criteria
- required tests

FIC answers:

```text
What exactly must this file do?
```

---

## 5.2 SIB — Structural Integration Binding

Use when a component connects files, layers, documents, schemas, reports, or evidence.

Defines:

- file-to-file relationships
- document-to-code relationships
- layer relationships
- schema/report bindings
- traceability paths
- integration boundaries

SIB answers:

```text
How does this component connect to the rest of Agent_X?
```

---

## 5.3 EQC — Engineering Quality Control

Use when a component affects correctness, governance, safety, validation, risk, evidence, or protected paths.

Defines:

- governance expectations
- quality gates
- evidence requirements
- validation expectations
- protection rules
- failure handling
- blocked behavior

EQC answers:

```text
How do we prove this is safe and correct?
```

---

## 5.4 ES — Ecosystem Specification

Use when a component describes system-level evolution, relationships, lifecycle position, or future growth.

Defines:

- ecosystem role
- lifecycle relationships
- cross-component meaning
- current scope versus later scope
- evolution path

ES answers:

```text
Where does this component fit in the larger Agent_X system?
```

---

## 5.5 Schema Contract

Use whenever a component reads or writes structured JSON or JSONL.

Defines:

- fields
- field types
- required fields
- allowed values
- validation rules
- serialization rules
- compatibility rules

Schema Contract answers:

```text
What exact structured artifact does this component produce or consume?
```

---

## 5.6 Evidence Rules

Use whenever a component claims that something happened, passed, failed, was blocked, or was validated.

Defines:

- audit event requirements
- proof artifacts
- append-only records
- validation summaries
- failure records
- timestamps
- traceability

Evidence Rules answer:

```text
What proof exists?
```

---

## 5.7 Report / Template Standard

Use whenever a component writes human-readable markdown reports.

Defines:

- report sections
- language style
- fact versus inference separation
- risk formatting
- artifact links
- consistency requirements

Report / Template Standard answers:

```text
How should humans read the result?
```

---

## 5.8 Command Acceptance Criteria

Use for every CLI command.

Defines:

- required inputs
- allowed options
- success output
- failure output
- write locations
- audit behavior
- done condition

Command Acceptance Criteria answers:

```text
When is this command done and correct?
```

---

# 6. Standard Requirement Levels

Each component may have three standard levels.

## Primary Standard

The main standard that governs the component.

## Required Supporting Standard

A standard that must also be applied because the component touches structure, governance, schemas, reports, commands, or evidence.

## Conditional Standard

A standard needed only if that component produces a specific artifact type.

Examples:

```text
If JSON/JSONL exists → Schema Contract required.
If markdown report exists → Report / Template Standard required.
If CLI command exists → Command Acceptance Criteria required.
If audit/proof exists → Evidence Rules required.
```

> **Note:** The Conditional column in the Component Standards Matrix may list standards as "if serialized" or "if output exists." Where a component contract or a later note makes that standard unconditional, the unconditional requirement governs. For example, Risk Engine's `SCHEMA_CONTRACT.md` is unconditionally required even though the matrix lists it as conditional.

---

# 7. Component Standards Matrix

| Component | Primary Standard | Required Supporting Standards | Conditional Standards | Milestone |
|---|---|---|---|---|
| Config and Paths | FIC | EQC | Config Schema Contract | 1 |
| Audit Log | EQC | FIC, SIB, Evidence Rules | Audit Schema Contract | 1 |
| Repository Scanner | FIC | SIB, Evidence Rules | Repo Scan Schema Contract | 1 |
| Layer Mapper | SIB | FIC, EQC | Shared Layer Map / Protected Path Schema Contract, if serialized | 1 |
| Report Writer | FIC | SIB | Report / Template Standard | 1 |
| CLI: scan | Command Acceptance Criteria | FIC, EQC, Evidence Rules | Repo Scan Schema Contract | 1 |
| CLI: status | Command Acceptance Criteria | FIC, EQC | Architecture Schema Contract, Report Standard | 1 |
| Architecture Analyzer (minimal) | SIB | FIC, EQC | Architecture Schema Contract | 1 (minimal) + 2 (full) |
| Governance Engine | EQC | FIC | Governance Schema Contract | 2 |
| Risk Engine | EQC | FIC | Risk Schema Contract, if serialized | 2 |
| Evolution Planner | ES | SIB, FIC | Evolution Plan Schema Contract, Report Standard | 2 |
| Patch Proposal Generator | FIC | EQC | Patch Proposal Schema Contract, Report Standard | 2 |
| Validation Runner | EQC | FIC, Evidence Rules | Validation Schema Contract, Report Standard | 2 |
| Memory Store | SIB | FIC, EQC, Evidence Rules | Memory Schema Contract | 2 |
| Knowledge Graph | SIB | FIC, ES | Graph Schema Contract | 3 |
| CLI: explain | Command Acceptance Criteria | FIC, EQC, Evidence Rules | None | 2 |
| CLI: plan | Command Acceptance Criteria | FIC, EQC | Evolution Plan Schema Contract, Report Standard | 2 |
| CLI: propose | Command Acceptance Criteria | FIC, EQC, Evidence Rules | Patch Proposal Schema Contract, Report Standard | 2 |
| CLI: validate | Command Acceptance Criteria | FIC, EQC, Evidence Rules | Validation Schema Contract, Report Standard | 2 |
| CLI: audit | Command Acceptance Criteria | FIC, EQC, Evidence Rules | Audit Schema Contract | 2 |
| CLI: graph | Command Acceptance Criteria | FIC, SIB, ES | Graph Schema Contract | 3 |

---

# 8. Product Milestone 1 Implementation Slice

Product Milestone 1 is limited to:

```text
package skeleton
config
paths / path registry
audit log core
repo scanner
layer mapper
minimal architecture analyzer
minimal report writer
scan command
status command
help command
basic tests
```

Later component contracts may define Component Milestone 1 for those components, but that does not make them active Product Milestone 1 scope.

| Work Item | Files | Required Docs | Required Proof |
|---|---|---|---|
| Package skeleton | `agentx_initiator/__init__.py`, `pyproject.toml` | OVERVIEW, ACCEPTANCE | `agentx-init --help` works |
| CLI entrypoint | `agentx_initiator/cli/main.py` | FIC, COMMAND_ACCEPTANCE, TESTS | help output test |
| help command | `agentx_initiator/cli/commands/help.py` | FIC, COMMAND_ACCEPTANCE | help output test |
| scan command | `agentx_initiator/cli/commands/scan.py` | FIC, COMMAND_ACCEPTANCE, EVIDENCE | scan writes snapshot + audit event |
| status command | `agentx_initiator/cli/commands/status.py` | FIC, COMMAND_ACCEPTANCE, REPORT_TEMPLATE_STANDARD | status writes markdown report |
| Config | `agentx_initiator/core/config.py`, `schemas/config.schema.json` | FIC, SCHEMA_CONTRACT, EQC | config validation test |
| Paths / Path Registry | `agentx_initiator/core/path_registry.py` | FIC, SIB, EQC | protected/write path tests |
| Audit Log | `agentx_initiator/core/audit_log.py`, `schemas/audit_event.schema.json` | FIC, SIB, SCHEMA_CONTRACT, EVIDENCE | append-only audit test |
| Repo Model | `agentx_initiator/core/repo_model.py` | FIC, SIB | model serialization test |
| Repo Scanner | `agentx_initiator/core/repo_scanner.py`, `schemas/repo_scan.schema.json` | FIC, SIB, SCHEMA_CONTRACT, EVIDENCE | scan freshness/hash tests |
| Layer Mapper | `agentx_initiator/core/layer_mapper.py` | FIC, SIB, EQC | L0 protected classification test |
| Report Writer | `agentx_initiator/core/report_writer.py`, `templates/status_report.md.j2` | FIC, REPORT_TEMPLATE_STANDARD | markdown report test |
| Minimal Architecture Analyzer | `agentx_initiator/core/architecture_analyzer.py`, `schemas/architecture_report.schema.json` | FIC, SIB, SCHEMA_CONTRACT | status summary test |

### Required PM1 Runtime Artifacts

| Artifact | Source | Required |
|---|---|---|
| `.agentx-init/config/config.json` | Config / Paths | Required |
| `.agentx-init/config/path_registry.json` | Config / Paths | Required |
| `.agentx-init/snapshots/config_validation_report_latest.json` | Config / Paths | Required |
| `.agentx-init/memory/audit_events.jsonl` | Audit Log | Required |
| `.agentx-init/snapshots/repo_scan_latest.json` | Repository Scanner | Required |
| `.agentx-init/memory/scans.jsonl` | Repository Scanner | Required |
| `.agentx-init/snapshots/architecture_latest.json` | Architecture Analyzer | Required |
| `.agentx-init/reports/latest_status.md` | Report Writer | Required |
| `.agentx-init/memory/audit_evidence.jsonl` | Audit Log | Optional (only if separate evidence-file mode) |
| `.agentx-init/logs/command_history.jsonl` | CLI Commands | Optional (only if CLI history enabled) |

---

# 9. Component-by-Component Requirements

## 9.1 Config and Paths

Target files:

```text
agentx_initiator/core/config.py
agentx_initiator/core/config_model.py
agentx_initiator/core/path_registry.py
agentx_initiator/schemas/config.schema.json
agentx_initiator/schemas/path_registry.schema.json
agentx_initiator/schemas/runtime_paths.schema.json
agentx_initiator/schemas/config_validation_report.schema.json
agentx_initiator/schemas/completion_record.schema.json
.agentx-init/config/config.json
.agentx-init/config/path_registry.json
.agentx-init/snapshots/config_validation_report_latest.json
```

If paths.py is retained, it is a compatibility facade over path_registry.py only.

Purpose:

- load configuration
- detect repository root
- manage `.agentx-init/`
- enforce protected path handling
- define allowed write locations

Required standards:

- **Primary:** FIC
- **Required:** EQC
- **Conditional:** Config Schema Contract

Component Milestone 1 rule:

```text
Only .agentx-init/ may be writable at runtime.
```

| Config and Paths Work | Product Milestone 1 | Later Milestones |
|---|---|---|
| Load config | Required | Required |
| Detect repository root | Required | Required |
| Manage `.agentx-init/` directory | Required | Required |
| Enforce protected path detection | Required | Required |
| Define allowed write locations | Required | Required |
| Generate `config_validation_report_latest.json` | Required | Required |
| Manage sidecar env/config injection | Not required | Product Milestone 2 |
| Multi-repo or project-relative root | Not required | Product Milestone 3 |

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
SCHEMA_CONTRACT.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.2 Audit Log

Target files:

```text
agentx_initiator/core/audit_log.py
agentx_initiator/schemas/audit_event.schema.json
.agentx-init/memory/audit_events.jsonl
```

`audit_event.schema.json` is the minimum event schema. The full Audit Log contract controls the complete schema set: `audit_event`, `audit_evidence`, `audit_record`, `audit_trail`, `audit_integrity`, and `completion_record`.

Purpose:

- write append-only audit events
- record command actions
- record generated artifacts
- record success and failure

Required standards:

- **Primary:** EQC
- **Required:** SIB, Evidence Rules
- **Conditional:** Audit Schema Contract

Component Milestone 1 rule:

```text
Audit history must be append-only.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
SCHEMA_CONTRACT.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.3 Repository Scanner

Target files:

```text
agentx_initiator/core/repo_model.py
agentx_initiator/core/repo_scanner.py
agentx_initiator/core/layer_mapper.py
agentx_initiator/schemas/repo_scan.schema.json
agentx_initiator/schemas/repository_fingerprint.schema.json
agentx_initiator/schemas/protected_path_map.schema.json
agentx_initiator/schemas/technology_map.schema.json
agentx_initiator/schemas/completion_record.schema.json
.agentx-init/snapshots/repo_scan_latest.json
.agentx-init/memory/scans.jsonl
.agentx-init/memory/audit_events.jsonl
```

Purpose:

- scan repository files and directories
- classify likely layers
- detect profiles
- detect validators
- detect tests
- calculate file hashes
- ignore configured directories

Required standards:

- **Primary:** FIC
- **Required:** SIB, Evidence Rules
- **Conditional:** Repo Scan Schema Contract

Component Milestone 1 rule:

```text
Scanner reads source files but never modifies them.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
SCHEMA_CONTRACT.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.4 Layer Mapper

Target files:

```text
agentx_initiator/core/layer_mapper.py
```

> **Layer Mapper schema note:** Layer Mapper does not own a separate schema in Product Milestone 1. It may produce internal maps consumed by Repository Scanner and Architecture Analyzer. If serialized layer or protected-path maps are needed, they use the Repository Scanner / shared schemas: `layer_map.schema.json` and `protected_path_map.schema.json`.

> **`layer_mapper.py` ownership note:** `layer_mapper.py` is listed under Repository Scanner target files because Layer Mapper is accessed through the Repository Scanner component boundary in PM1. Its contract is defined in a separate document (`LAYER_MAPPER_FIC_SIB_EQC_CONTRACT.md`). The Repository Scanner component contract must be consistent with that separate document.

Purpose:

- map files to L0, L1, L2, or unknown
- detect protected paths
- support architecture and governance analysis

Required standards:

- **Primary:** SIB
- **Required:** FIC, EQC
- **Conditional:** None

**Dependency direction:** Layer Mapper must not import Repository Scanner. Repository Scanner may import Layer Mapper for layer classification during scan. This prevents circular dependency in PM1.

Component Milestone 1 rule:

```text
L0 must always be classified as protected.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.5 Architecture Analyzer

Target files:

```text
agentx_initiator/core/architecture_analyzer.py
agentx_initiator/schemas/architecture_report.schema.json
agentx_initiator/schemas/architecture_finding.schema.json
agentx_initiator/schemas/architecture_relationship.schema.json
agentx_initiator/schemas/architecture_evidence.schema.json
agentx_initiator/schemas/completion_record.schema.json
.agentx-init/snapshots/architecture_latest.json
.agentx-init/memory/audit_events.jsonl
```

Purpose:

- summarize repository architecture
- identify missing pieces
- separate facts, findings, warnings, violations, unknowns, and risk hints
- support the status command

Required standards:

- **Primary:** SIB
- **Required:** EQC
- **Conditional:** Architecture Schema Contract

Product Milestone 1 note:

```text
Only the minimal Architecture Analyzer needed for status is scheduled for Product Milestone 1.
Richer architecture analysis remains Product Milestone 2 scope.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
SCHEMA_CONTRACT.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.6 Governance Engine

Target files:

```text
agentx_initiator/core/governance_engine.py
agentx_initiator/schemas/governance_request.schema.json
agentx_initiator/schemas/governance_decision.schema.json
agentx_initiator/schemas/governance_evidence.schema.json
agentx_initiator/schemas/governance_violation.schema.json
agentx_initiator/schemas/governance_audit.schema.json
agentx_initiator/schemas/completion_record.schema.json
.agentx-init/snapshots/governance_latest.json
.agentx-init/memory/governance_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Purpose:

- decide whether an action is allowed, warned, or blocked
- enforce protected paths
- enforce Full Version 1 non-mutating behavior
- prevent R4 actions

Required standards:

- **Primary:** EQC
- **Required:** FIC
- **Conditional:** Governance Schema Contract

Component Milestone 1 rule:

```text
R4 actions must be blocked.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
SCHEMA_CONTRACT.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.7 Risk Engine

Target files:

```text
agentx_initiator/core/risk_engine.py
agentx_initiator/schemas/risk_assessment.schema.json
agentx_initiator/schemas/risk_item.schema.json
agentx_initiator/schemas/risk_evidence.schema.json
agentx_initiator/schemas/risk_mitigation.schema.json
agentx_initiator/schemas/risk_history_record.schema.json
agentx_initiator/schemas/risk_audit.schema.json
agentx_initiator/schemas/completion_record.schema.json
.agentx-init/snapshots/risk_latest.json
.agentx-init/memory/risk_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Purpose:

- classify action risk
- provide advisory risk context for Governance Engine review
- identify risk signals that may require governance review

Required standards:

- **Primary:** EQC
- **Required:** FIC
- **Conditional:** Risk Schema Contract

Component Milestone 1 rule:

```text
L0 writes, promotion, runtime self-mutation, and governance bypass are R4.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

SCHEMA_CONTRACT.md is required because Risk Engine produces serialized Product Milestone 2 artifacts.

---

## 9.8 Evolution Planner

Target files:

```text
agentx_initiator/core/evolution_planner.py
agentx_initiator/schemas/evolution_plan.schema.json
.agentx-init/snapshots/evolution_plan_latest.json
.agentx-init/memory/evolution_plan_history.jsonl
.agentx-init/reports/latest_plan.md            # optional markdown report, not the canonical structured plan artifact
```

Purpose:

- rank next work
- identify benefits
- identify risks
- identify dependencies
- identify rollback strategies
- identify required tests

Required standards:

- **Primary:** ES
- **Required:** SIB, FIC
- **Conditional:** Evolution Plan Schema Contract, Report Standard

Component Milestone 1 rule:

```text
Plans may recommend work but may not perform implementation.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
SCHEMA_CONTRACT.md
REPORT_TEMPLATE_STANDARD.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.9 Patch Proposal Generator

Target files:

```text
agentx_initiator/core/patch_proposal_generator.py
agentx_initiator/schemas/patch_proposal.schema.json
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/memory/patch_proposal_history.jsonl
.agentx-init/reports/latest_patch_proposal.md  # optional markdown report, not the canonical proposal artifact
```

Purpose:

- create non-mutating patch proposals
- identify affected files
- include validation plan
- include rollback plan
- include governance decision reference
- optionally include non-executable change summary preview

Required standards:

- **Primary:** FIC
- **Required:** EQC
- **Conditional:** Patch Proposal Schema Contract, Report Standard

Component Milestone 1 rule:

```text
Patch proposals must not change source files.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
SCHEMA_CONTRACT.md
REPORT_TEMPLATE_STANDARD.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.10 Validation Runner

Target files:

```text
agentx_initiator/core/validation_runner.py
agentx_initiator/schemas/validation_report.schema.json
agentx_initiator/schemas/validation_check.schema.json
agentx_initiator/schemas/validation_evidence.schema.json
agentx_initiator/schemas/validation_command.schema.json
agentx_initiator/schemas/validation_audit.schema.json
agentx_initiator/schemas/completion_record.schema.json
.agentx-init/snapshots/validation_report_latest.json
.agentx-init/memory/validation_history.jsonl
.agentx-init/memory/audit_events.jsonl
.agentx-init/reports/latest_validation.md   # optional markdown report, not canonical structured validation artifact
```

Purpose:

- run only allowlisted validation commands
- capture exit codes
- summarize stdout and stderr
- write validation evidence

Required standards:

- **Primary:** EQC
- **Required:** Evidence Rules
- **Conditional:** Validation Schema Contract, Report Standard

Component Milestone 1 rule:

```text
Validation does not equal approval.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
SCHEMA_CONTRACT.md
REPORT_TEMPLATE_STANDARD.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.11 Memory Store

Target files:

```text
agentx_initiator/core/memory_store.py
agentx_initiator/core/memory_model.py
agentx_initiator/core/memory_index.py
agentx_initiator/schemas/memory_record.schema.json
agentx_initiator/schemas/memory_reference.schema.json
agentx_initiator/schemas/memory_index.schema.json
agentx_initiator/schemas/memory_snapshot.schema.json
agentx_initiator/schemas/memory_query_result.schema.json
agentx_initiator/schemas/memory_manifest.schema.json
agentx_initiator/schemas/completion_record.schema.json
.agentx-init/memory/memory_records.jsonl
.agentx-init/memory/memory_index.json
.agentx-init/snapshots/memory_snapshot_latest.json
.agentx-init/snapshots/memory_manifest_latest.json
```

Purpose:

- persist scan history
- persist evolution plans
- persist patch proposals
- persist validation history
- support repeatable inspection

Required standards:

- **Primary:** SIB
- **Required:** EQC, Evidence Rules
- **Conditional:** Memory Schema Contract

Product Milestone 1 note:

```text
Product Milestone 1 may write simple append-only JSONL history files such as scans.jsonl and audit_events.jsonl.
This does not mean the full Memory Store component is implemented.
The full Memory Store begins in Product Milestone 2.
```

Component Milestone 1 rule:

```text
Memory writes only under .agentx-init/memory/.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
SCHEMA_CONTRACT.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.12 Report Writer

Target files:

```text
Product Milestone 1 required:
agentx_initiator/core/report_writer.py
agentx_initiator/templates/status_report.md.j2
.agentx-init/reports/latest_status.md

Product Milestone 2 later templates:
agentx_initiator/templates/evolution_plan.md.j2
agentx_initiator/templates/patch_proposal.md.j2
agentx_initiator/templates/validation_report.md.j2
.agentx-init/reports/*.md (PM2 expanded reports)

Full Report Writer contract controls later report templates; Product Milestone 1 requires only status/architecture reporting.
```

Report template content is governed by the separate Report / Template Standard contract, not by this document. This section lists expected file locations only.

Purpose:

- generate consistent markdown reports
- separate facts from inferences
- present risks clearly
- present generated artifacts clearly

Required standards:

- **Primary:** FIC
- **Required:** SIB
- **Conditional:** Report / Template Standard

Component Milestone 1 rule:

```text
Reports must not imply approval or implementation completion.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
REPORT_TEMPLATE_STANDARD.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.13 Knowledge Graph

Target files:

```text
agentx_initiator/core/knowledge_graph.py
agentx_initiator/schemas/graph_node.schema.json
agentx_initiator/schemas/graph_edge.schema.json
agentx_initiator/schemas/graph_snapshot.schema.json
agentx_initiator/schemas/graph_query_result.schema.json
agentx_initiator/schemas/graph_manifest.schema.json
agentx_initiator/schemas/graph_integrity.schema.json
.agentx-init/graph/graph_snapshot_latest.json
```

Purpose:

- represent repository structure as nodes and edges
- connect files, directories, layers, profiles, tests, validators, and schemas

Required standards:

- **Primary:** SIB
- **Required:** ES
- **Conditional:** Graph Schema Contract

Product Milestone 3 note:

```text
Knowledge Graph is scheduled for Product Milestone 3, not Product Milestone 1.
Graph implementation should not begin until Product Milestone 1 and Product Milestone 2 components are stable.
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
SCHEMA_CONTRACT.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

## 9.14 CLI Commands

Target files:

```text
agentx_initiator/cli/main.py
agentx_initiator/cli/commands/help.py
agentx_initiator/cli/commands/scan.py
agentx_initiator/cli/commands/status.py
agentx_initiator/cli/commands/explain.py
agentx_initiator/cli/commands/plan.py
agentx_initiator/cli/commands/propose.py
agentx_initiator/cli/commands/report.py
agentx_initiator/cli/commands/memory.py
agentx_initiator/cli/commands/validate.py
agentx_initiator/cli/commands/audit.py
agentx_initiator/cli/commands/graph.py
```

Purpose:

- expose the Initiator as a local user-facing CLI
- execute bounded workflows
- write allowed artifacts
- record audit events

Required standards:

- **Primary:** Command Acceptance Criteria
- **Required:** FIC, EQC
- **Conditional:** Evidence Rules when command writes proof or reports

Component Milestone 1 rule:

```text
Commands must not write outside .agentx-init/.
```

Required documents per command:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
COMMAND_ACCEPTANCE.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

Add schema or report standard documents when the command writes schema-governed outputs or markdown reports.

---

# 10. Required Initial Documents Per Milestone 1 Component

For each Milestone 1 implementation file or component, create:

```text
docs/init/components/<component_name>/OVERVIEW.md
docs/init/components/<component_name>/PSEUDOCODE.md
docs/init/components/<component_name>/FIC.md
docs/init/components/<component_name>/SIB.md
docs/init/components/<component_name>/ACCEPTANCE.md
docs/init/components/<component_name>/TESTS.md
docs/init/components/<component_name>/EVIDENCE.md
```

For schema-producing components, also create:

```text
docs/init/components/<component_name>/SCHEMA_CONTRACT.md
```

For report-producing components, also create:

```text
docs/init/components/<component_name>/REPORT_TEMPLATE_STANDARD.md
```

For CLI command components, also create:

```text
docs/init/components/<command_name>/COMMAND_ACCEPTANCE.md
```

---

# 11. Traceability Chain

Each component must support the following traceability chain:

```text
Standard
  ↓
Component document
  ↓
FIC / SIB / schema contract
  ↓
Implementation file
  ↓
Test file
  ↓
Runtime artifact
  ↓
Audit event
  ↓
Evidence record
```

Example for Repository Scanner:

```text
FIC + SIB + Repo Scan Schema Contract
  ↓
docs/init/components/repository_scanner/
  ↓
agentx_initiator/core/repo_scanner.py
  ↓
agentx_initiator/tests/test_repo_scanner.py
  ↓
.agentx-init/snapshots/repo_scan_latest.json
  ↓
.agentx-init/memory/audit_events.jsonl
  ↓
scan evidence
```

---

# 12. Product Milestone 1 Write Boundaries

Allowed runtime write location:

```text
.agentx-init/
```

Allowed generated runtime artifacts (Product Milestone 1 only):

```text
.agentx-init/config/config.json
.agentx-init/config/path_registry.json
.agentx-init/snapshots/config_validation_report_latest.json
.agentx-init/snapshots/repo_scan_latest.json
.agentx-init/snapshots/architecture_latest.json
.agentx-init/reports/latest_status.md
.agentx-init/memory/audit_events.jsonl
.agentx-init/memory/scans.jsonl
.agentx-init/logs/command_history.jsonl          # optional — only if CLI history is enabled
```

Product Milestone 1 must not create Product Milestone 2 or Product Milestone 3 artifacts except BLOCKED command-history and audit records for registered later-command stubs.

Blocked runtime write locations:

```text
L0/
L1/
L2/
agent_x/runtime/
core/
source files outside .agentx-init/
```

Runtime rule:

```text
the installed/running agentx-init product line, across Product Milestones 1–3 is a read-only assistant toward Agent_X source files.
```

---

# 13. Component Readiness Checklist

A component is ready for implementation only when:

- component purpose is defined
- target files are listed
- primary standard is assigned
- supporting standards are assigned
- conditional standards are resolved
- runtime outputs are listed
- write boundaries are clear
- FIC exists
- SIB exists
- schema contract exists if structured output exists
- report standard exists if markdown output exists
- command acceptance exists if CLI behavior exists
- tests are listed
- evidence expectations are listed
- protected-path behavior is specified
- failure behavior is specified
- acceptance criteria are testable

---

# 14. Do Not Overbuild Rule

For later components, write only enough documentation to define their place in the system.

Do not fully specify or implement these until Milestone 1 is stable:

```text
governance_engine.py
risk_engine.py
evolution_planner.py
patch_proposal_generator.py
validation_runner.py
memory_store.py
knowledge_graph.py
explain.py
plan.py
propose.py
validate.py
audit.py
graph.py
```

The first implementation push should remain limited to:

```text
package skeleton
config
paths
audit log
repo scanner
layer mapper
scan command
status command
status report
basic tests
```

---

# 15. Final Coverage Verdict

Revision 5 gives complete standard coverage and adds the final freeze rule.

## Covered

- all major Initiator components
- all relevant standards
- primary, supporting, and conditional standard roles
- concrete target files
- output artifacts
- schema ownership
- report ownership
- command acceptance requirements
- milestone boundaries
- implementation handoff table
- runtime versus implementation boundary
- traceability chain
- readiness checklist
- do-not-overbuild rule
- read-only version 1 boundary
- audit and evidence requirements
- final freeze rule

## Final Rating

**10/10**

This document is now frozen as the controlling component-and-standards reference.

---

## Synchronization Status

**Canonical command name:** `agentx-init`  
**Canonical runtime root:** `.agentx-init/`  
**Canonical config file:** `config.json`  
**Canonical path authority:** `path_registry.py`  
**Interpretation rule:** Product Milestone placement is separate from Component Milestone 1.

This document has been synchronized with the Milestone and Naming Alignment Addendum.  
"Version 1 rule" sections have been updated to "Component Milestone 1 rule." Report Writer template ownership is clarified as governed by the separate Report / Template Standard contract. Product Milestone 1 Write Boundaries are explicitly documented.

The next step should not be another broad revision of this document. The next step should be writing the Milestone 1 component documents.
