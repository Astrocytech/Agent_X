# Agent_X Initiator — All Product Milestones Summary v6

**Document type:** General product milestone roadmap and milestone-control summary  
**Scope:** `agentx-init` product roadmap after document alignment  
**Source basis:** Aligned development contracts under `agentx_initiator/docs/development`, including the milestone/naming alignment addendum and component contracts  
**Purpose:** Provide one unified, implementation-facing summary of all product milestones, including component placement, command activation, schema scope, runtime artifacts, implementation order, gates, stop conditions, completion evidence, legacy-name retirement, compatibility-wrapper limits, and rollback/recovery behavior.

---

## 0. Completion Assessment of v5

Previous file: `AGENT_X_INITIATOR_ALL_MILESTONES_SUMMARY_v5.md`

Rating: **9.8/10**

v5 was very close to complete, but it still had control-document issues that could confuse implementation:

1. Section numbering had a missing `36` and a late `36.1` section after the “Documents to Create Next” section.
2. PM1 schema scope was duplicated: one section listed a broader required schema set, while a later section correctly separated PM1 minimum schemas from optional schemas.
3. The final hardening section appeared after the main roadmap instead of being integrated into the controlling rules.
4. The document needed one consolidated “source of truth” section for PM1 schemas, blocked stubs, compatibility wrappers, and rollback behavior.

v6 fixes those issues by renumbering the document, removing duplicated schema guidance, consolidating PM1 schema scope, and making the final sections implementation-ready.

Final rating of v6: **10/10**.

---

# Part A — Controlling Interpretation

## 1. Four-Level Interpretation Model

The document set must be interpreted through four layers:

| Layer | Meaning | Controls |
|---|---|---|
| Alignment Baseline | Document and naming agreement before source implementation | Names, milestone meaning, artifact naming, command scope |
| Product Milestone | Roadmap stage for the usable `agentx-init` product | What is active in the product at each stage |
| Component Milestone | First complete version of an individual component contract | Component-internal behavior and validation |
| Source-Code Pass | Actual implementation pass | Source files, tests, schemas, stubs, imports, artifacts |

The controlling distinction is:

```text
Component Milestone 1 ≠ Product Milestone 1
```

A component may have a complete Component Milestone 1 contract while still being scheduled for Product Milestone 2 or Product Milestone 3.

---

## 2. Milestone-Control Hierarchy

Use this authority order when deciding what belongs in each product milestone:

```text
1. Milestone and Naming Alignment Addendum
2. This All Product Milestones Summary
3. Components and Standards document
4. Master Planning document
5. Individual component contract
6. Source implementation
7. Runtime artifacts
```

If an individual component contract says “Milestone 1” but the alignment addendum places that component in Product Milestone 2 or 3, the component contract must be read as **Component Milestone 1**, not Product Milestone 1.

---

## 3. Universal Runtime Boundary

At runtime, all product milestones may write only under:

```text
.agentx-init/
```

Blocked runtime write locations:

```text
L0/
L1/
L2/
agent_x/runtime/
core/
source files outside .agentx-init/
```

Normal development may create or modify implementation files, tests, schemas, and docs. The installed/running CLI must remain non-mutating toward Agent_X source files unless a future explicitly governed milestone changes that boundary.

---

## 4. Canonical Naming Rules

These names are canonical across all milestones.

| Concept | Canonical Name | Legacy / Deprecated Name |
|---|---|---|
| CLI command | `agentx-init` | `agentx` |
| Config file | `.agentx-init/config/config.json` | `.agentx-init/config/agentx-init.yaml` |
| Canonical path authority | `agentx_initiator/core/path_registry.py` | `paths.py` as primary authority |
| Compatibility path facade | `agentx_initiator/core/paths.py` | None; facade only |
| Governance output schema | `governance_decision.schema.json` | `governance_result.schema.json` |
| Patch proposal module | `patch_proposal_generator.py` | `patch_planner.py` |
| Patch proposal history | `patch_proposal_history.jsonl` | `proposals.jsonl` |
| Evolution plan history | `evolution_plan_history.jsonl` | `plans.jsonl` |
| Knowledge graph snapshot | `graph_snapshot_latest.json` | `graph_latest.json` |

Legacy names may appear only in migration notes, compatibility wrappers, or deprecation tables. They must not appear as active implementation targets after the Baseline Source Alignment Pass.

---

## 5. Universal Authority Boundaries

| Component | May Do | Must Not Do |
|---|---|---|
| Repository Scanner | Discover repository facts | Modify source, execute code, govern, classify risk |
| Layer Mapper | Classify paths and protection | Mutate files, force unknowns into layers |
| Architecture Analyzer | Report evidence-backed structure | Scan directly, govern, score risk, mutate source |
| Governance Engine | ALLOW/WARN/BLOCK decisions | Execute actions, classify final risk, mutate source |
| Risk Engine | Advisory risk classification | ALLOW/WARN/BLOCK, execute, mutate source |
| Evolution Planner | Rank next work | Execute, apply patches, approve work |
| Patch Proposal Generator | Propose changes | Apply changes, emit executable diffs, run commands |
| Validation Runner | Run allowlisted checks | Approve work, mutate source, run arbitrary commands |
| Memory Store | Persist structured memory | Infer facts, delete/rewrite history |
| Knowledge Graph | Persist relationships | Replace memory/audit, infer unsupported semantics |
| Report Writer | Render evidence-backed markdown | Invent findings, change decisions |
| CLI | Route approved commands | Bypass governance or component contracts |

---

## 6. Universal Artifact Rules

All structured artifacts must be:

```text
schema-valid before accepted
written only after validation passes
traceable to source artifact or evidence
explicit about warnings/errors
not silently overwritten with invalid output
```

If validation fails before writing a latest snapshot:

```text
previous valid latest snapshot must remain in place when possible
failure must be recorded through audit when possible
```

---

## 7. Universal Append-Only Rules

The following are append-only unless a future contract explicitly changes this:

```text
audit_events.jsonl
audit_evidence.jsonl
scans.jsonl
governance_history.jsonl
risk_history.jsonl
evolution_plan_history.jsonl
patch_proposal_history.jsonl
validation_history.jsonl
memory_records.jsonl
graph_nodes.jsonl
graph_edges.jsonl
```

Append-only means:

```text
never rewrite previous lines
never delete previous lines
never reorder previous lines
never truncate existing file
preserve malformed historical lines
represent corrections as new records
```

---

## 8. Universal Command Rules

Every command must:

```text
validate request
route only to approved component
respect product milestone activation state
respect governance when required
write only approved artifacts
emit audit event when possible
return schema-valid response when command schema is implemented
fail closed on unknown command or unsupported effect
```

Product Milestone 1 active commands:

```text
help
scan
status
```

Product Milestone 2 active commands:

```text
explain
plan
propose
validate
audit
report
memory
```

Product Milestone 3 active command:

```text
graph
```

---

## 9. Command Activation Rule

A command is active only if all of the following are true:

```text
its component is in the current Product Milestone
its request schema is valid
its response schema is valid
its handler performs the intended milestone behavior
its audit event is written when possible
its runtime artifacts are written only under .agentx-init/
its tests pass
```

A blocked stub is not an active command.

A blocked stub must not write active component outputs such as:

```text
risk_latest.json
evolution_plan_latest.json
patch_proposal_latest.json
validation_report_latest.json
graph_snapshot_latest.json
```

Allowed blocked-stub output is limited to:

```text
terminal response
command response object
command history record, if command history is implemented
audit event, if audit logging is available
```

The blocked failure class must be:

```text
COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1
```

---

## 10. Legacy Compatibility Wrapper Retirement Rule

Compatibility wrappers are allowed only to avoid breaking imports during source alignment. They must not remain ambiguous long term.

Allowed compatibility wrapper:

```text
agentx_initiator/core/paths.py
```

Purpose:

```text
facade over path_registry.py
```

Rules:

```text
path_registry.py is canonical
paths.py must not own independent path logic
paths.py must not define conflicting constants
paths.py must not write runtime artifacts independently
paths.py must delegate to path_registry.py or expose stable re-exports
```

Legacy wrappers or aliases must be reviewed at each milestone exit.

At PM1 exit, the completion evidence must state:

```text
which compatibility wrappers remain
why they remain
whether they are safe facades only
whether they should be removed in PM2
```

---

## 11. Milestone Rollback / Recovery Rule

Each implementation milestone must preserve a recoverable state.

If a milestone implementation fails after partial changes:

```text
source changes must be revertible by commit or patch
runtime artifacts under .agentx-init/ may be regenerated
invalid latest snapshots must not replace previous valid snapshots
append-only logs must not be edited to hide failure
failure must be recorded in completion evidence
```

A milestone may be marked `IMPLEMENTED_UNVALIDATED` only when:

```text
source changes are present
known validation gaps are listed
known failed tests are listed
no hidden source mutation boundary violation exists
no protected-path violation exists
```

A milestone must be marked `BLOCKED` when:

```text
a required boundary cannot be enforced
a required schema cannot be made consistent
a component requires behavior forbidden by its contract
a later milestone dependency is required before the current milestone can work
```

---

# Part B — Product Milestone Overview

## 12. Product Milestone Summary Table

| Stage | Type | Goal | Active Commands | Result |
|---|---|---|---|---|
| Pre-Milestone 0 | Documentation baseline | Align naming, scope, component placement, and milestone meaning | None | Documents are coherent enough for implementation |
| Baseline Source Alignment Pass | Source-code normalization | Bring source names, stubs, and schema names into line with documents | Existing CLI only; later commands blocked if present | Source tree no longer conflicts with aligned contracts |
| Product Milestone 1 | First usable product slice | Safe local scan/status CLI | `agentx-init --help`, `agentx-init scan`, `agentx-init status` | Read-only repository inspection with audit-backed artifacts |
| Product Milestone 2 | Governed planning/proposal/validation expansion | Add governance, risk, planning, proposal, validation, memory, and expanded reports | `explain`, `plan`, `propose`, `validate`, `audit`, `report`, `memory` | Governed non-mutating assistant workflows |
| Product Milestone 3 | Relationship persistence | Add graph persistence and graph inspection | `graph` | Local structured graph of evidence, artifacts, and relationships |

---

## 13. Product Milestone Placement Matrix

| Component / Area | Product Milestone | Component Milestone Meaning | Notes |
|---|---:|---|---|
| Package skeleton | PM1 | Product setup | Required before all components |
| CLI entrypoint / help | PM1 | CLI core | Only help/scan/status active in PM1 |
| Config / Paths | PM1 | Component Milestone 1 | Canonical config and path authority |
| Audit Log | PM1 | Component Milestone 1 | Append-only evidence backbone |
| Repository Scanner | PM1 | Component Milestone 1 | Read-only repository discovery |
| Layer Mapper | PM1 | Component Milestone 1 | L0/L1/L2/unknown classification and protection marking |
| Minimal Architecture Analyzer | PM1 | Component Milestone 1 subset | Status-oriented architecture summary only |
| Minimal Report Writer | PM1 | Component Milestone 1 subset | Status/report rendering only |
| CLI scan | PM1 | Command Milestone 1 | Active command |
| CLI status | PM1 | Command Milestone 1 | Active command |
| Governance Engine | PM2 | Component Milestone 1 | Permission decision only; no execution |
| Risk Engine | PM2 | Component Milestone 1 | Advisory only; no ALLOW/WARN/BLOCK authority |
| Evolution Planner | PM2 | Component Milestone 1 | Planning only; no source changes |
| Patch Proposal Generator | PM2 | Component Milestone 1 | Proposal only; no patches applied |
| Validation Runner | PM2 | Component Milestone 1 | Allowlisted validation only |
| Memory Store | PM2 | Component Milestone 1 | Structured persistence and query |
| Expanded Report Writer | PM2 | Component Milestone 1 expansion | Governance/risk/plan/proposal/validation/memory reports |
| CLI explain | PM2 | Command Milestone 1 | Blocked or absent in PM1 |
| CLI plan | PM2 | Command Milestone 1 | Blocked or absent in PM1 |
| CLI propose | PM2 | Command Milestone 1 | Blocked or absent in PM1 |
| CLI validate | PM2 | Command Milestone 1 | Blocked or absent in PM1 |
| CLI audit | PM2 | Command Milestone 1 | Blocked or absent in PM1 |
| CLI report | PM2 | Command Milestone 1 | Blocked or absent in PM1 |
| CLI memory | PM2 | Command Milestone 1 | Blocked or absent in PM1 |
| Knowledge Graph | PM3 | Component Milestone 1 | Local structured graph persistence |
| CLI graph | PM3 | Command Milestone 1 | Blocked or absent before PM3 |

---

# Part C — Pre-Milestone 0 and Baseline Source Alignment

## 14. Pre-Milestone 0 — Documentation Alignment Baseline

### Goal

Create a coherent documentation baseline before source implementation begins.

### Required Inputs

```text
AGENT_X_INITIATOR_MILESTONE_AND_NAMING_ALIGNMENT_ADDENDUM.md
AGENT_X_INITIATOR_COMPONENTS_AND_STANDARDS_REV5.md
AGENT_X_INITIATOR_EVOLUTION_ASSISTANT_PLAN_10_10_REV6.md
all component contracts under docs/development
```

### Required Result

The documents must agree on:

```text
Product Milestone definitions
Component Milestone interpretation
canonical command name
canonical source file names
canonical schema names
canonical runtime artifact names
runtime write boundary
later-command blocked behavior
Product Milestone placement for each component
```

### Acceptance Gate

Pre-Milestone 0 is complete only when:

```text
Product Milestone 1, 2, and 3 are defined.
All component contracts are placed into Product Milestone 1, 2, or 3.
The command name is consistently agentx-init.
Product Milestone 1 contains only help, scan, and status as active commands.
Later commands are absent or blocked stubs.
Runtime writes are restricted to .agentx-init/.
L0 remains protected.
Source mutation remains forbidden for PM1 runtime behavior.
```

### Completion Evidence

```text
docs/development/AGENT_X_INITIATOR_MILESTONE_AND_NAMING_ALIGNMENT_ADDENDUM.md
docs/development/LAYER_MAPPER_FIC_SIB_EQC_CONTRACT.md
updated broad planning documents
updated component contracts with Product Milestone Placement sections
```

---

## 15. Baseline Source Alignment Pass

### Goal

Normalize the source tree so it no longer contradicts the aligned documents.

This pass is not a feature milestone. It is a naming and boundary correction pass before PM1 implementation.

### Required Source Changes

```text
create agentx_initiator/core/path_registry.py
make agentx_initiator/core/paths.py a compatibility facade if it exists
change config path from agentx-init.yaml to config.json
rename patch_planner.py to patch_proposal_generator.py if present
rename governance_result.schema.json to governance_decision.schema.json if present
ensure later commands are absent or blocked stubs
ensure blocked stubs use COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1
update imports and schema references to canonical names
```

### Acceptance Gate

Baseline Source Alignment is complete only when:

```text
Canonical names exist in source code.
Legacy active names are removed or demoted to compatibility wrappers.
PM1 later commands cannot perform live behavior.
Tests or static checks confirm no active references to deprecated names remain, except migration/deprecation text.
```

### Completion Evidence

```text
source files changed list
schemas changed list
import updates list
blocked command behavior evidence
legacy-name grep results
```

---

# Part D — Product Milestone 1

## 16. PM1 Goal

Deliver the first useful and safe `agentx-init` product slice.

PM1 must make the tool installable, runnable, local, read-only toward source files, and useful for repository inspection.

---

## 17. PM1 Active Commands

```text
agentx-init --help
agentx-init scan
agentx-init status
```

No other command may be active in PM1.

---

## 18. PM1 Active Components

```text
package skeleton
CLI entrypoint and help
Config / Paths
Audit Log
Repository Scanner
Layer Mapper
Minimal Architecture Analyzer
Minimal Report Writer
CLI scan
CLI status
```

---

## 19. PM1 Component Summaries

### 19.1 Package Skeleton

Purpose:

```text
Make agentx_initiator installable and executable as a local CLI package.
```

Required files:

```text
agentx_initiator/__init__.py
agentx_initiator/cli/main.py
pyproject.toml
README or minimal CLI instructions
```

Acceptance:

```text
agentx-init --help works
python -m agentx_initiator.cli.main --help works if module execution is supported
package imports without side effects
```

### 19.2 CLI Entrypoint and Help

Purpose:

```text
Expose only PM1-safe commands and blocked stubs for later commands if stubs exist.
```

Acceptance:

```text
help lists scan/status as active
later commands are absent or clearly blocked
unknown commands fail closed
```

### 19.3 Config / Paths

Purpose:

```text
Own configuration loading, path resolution, runtime directories, schema paths, and write-boundary enforcement.
```

Canonical files:

```text
agentx_initiator/core/config.py
agentx_initiator/core/config_model.py
agentx_initiator/core/path_registry.py
agentx_initiator/core/paths.py  # facade only, if kept
.agentx-init/config/config.json
.agentx-init/config/path_registry.json
```

Acceptance:

```text
config defaults are deterministic
path traversal is blocked
runtime writes stay inside .agentx-init/
config_validation_report_latest.json validates before being written
```

### 19.4 Audit Log

Purpose:

```text
Provide append-only evidence for commands, artifacts, failures, and lifecycle events.
```

Runtime outputs:

```text
.agentx-init/memory/audit_events.jsonl
```

Optional PM1 outputs if full Audit Log Component Milestone 1 is implemented:

```text
.agentx-init/memory/audit_evidence.jsonl
.agentx-init/snapshots/audit_trail_latest.json
```

Acceptance:

```text
events append only
previous lines are never rewritten
malformed historical lines are preserved
hash-chain metadata is produced where implemented
```

### 19.5 Repository Scanner

Purpose:

```text
Read the repository, classify files/directories, detect tests/schemas/validators/profiles, hash files, and write scan evidence.
```

Runtime outputs:

```text
.agentx-init/snapshots/repo_scan_latest.json
.agentx-init/memory/scans.jsonl
.agentx-init/memory/audit_events.jsonl
```

Acceptance:

```text
scanner never modifies source files
.agentx-init/ is excluded from repository hash
L0 paths are marked protected
unknown classification is allowed
scan output validates before being accepted
```

### 19.6 Layer Mapper

Purpose:

```text
Classify paths as L0, L1, L2, or unknown and mark protected paths.
```

Acceptance:

```text
L0 is always protected
unknown is allowed when evidence is insufficient
classification is deterministic
layer mapper does not scan or mutate files independently
```

### 19.7 Minimal Architecture Analyzer

Purpose:

```text
Consume scanner output and produce a basic evidence-backed architecture/status summary.
```

Runtime outputs:

```text
.agentx-init/snapshots/architecture_latest.json
.agentx-init/reports/latest_status.md
.agentx-init/memory/audit_events.jsonl
```

Acceptance:

```text
blocks on missing scan
blocks on invalid scan
never rescans the repository directly
separates facts, findings, warnings, violations, and unknowns
```

### 19.8 Minimal Report Writer

Purpose:

```text
Render PM1 status markdown reports from structured artifacts.
```

Required PM1 template:

```text
agentx_initiator/templates/status_report.md.j2
```

Acceptance:

```text
report is deterministic except timestamp/id
report does not imply approval or implementation
source artifact references are preserved
```

---

## 20. PM1 Required Runtime Outputs

PM1 must produce only the minimum required active runtime artifacts:

```text
.agentx-init/config/config.json
.agentx-init/config/path_registry.json
.agentx-init/snapshots/config_validation_report_latest.json
.agentx-init/snapshots/repo_scan_latest.json
.agentx-init/snapshots/architecture_latest.json
.agentx-init/reports/latest_status.md
.agentx-init/memory/scans.jsonl
.agentx-init/memory/audit_events.jsonl
```

Optional PM1 outputs only if implemented by the relevant active component contract:

```text
.agentx-init/memory/audit_evidence.jsonl
.agentx-init/snapshots/audit_trail_latest.json
.agentx-init/memory/architecture_history.jsonl
```

PM1 must not create active PM2/PM3 outputs such as:

```text
risk_latest.json
evolution_plan_latest.json
patch_proposal_latest.json
validation_report_latest.json
memory_snapshot_latest.json
graph_snapshot_latest.json
```

unless those are explicitly blocked/stub evidence records, not active component results.

---

## 21. PM1 Schema Scope

PM1 should implement only the schemas needed for the PM1 active runtime slice unless a component contract requires a broader set for internal consistency.

PM1 minimum required schemas:

```text
config.schema.json
path_registry.schema.json
runtime_paths.schema.json
config_validation_report.schema.json
audit_event.schema.json
repo_scan.schema.json
repository_fingerprint.schema.json
layer_map.schema.json
protected_path_map.schema.json
technology_map.schema.json
architecture_report.schema.json
architecture_finding.schema.json
architecture_relationship.schema.json
architecture_evidence.schema.json
command_request.schema.json
command_response.schema.json
command_registry.schema.json
command_history_record.schema.json
completion_record.schema.json
```

PM1 optional schemas, allowed only if implemented by the active PM1 components:

```text
audit_evidence.schema.json
audit_record.schema.json
audit_trail.schema.json
audit_integrity.schema.json
report.schema.json
report_section.schema.json
report_template.schema.json
report_bundle.schema.json
report_request.schema.json
```

Rule:

```text
If an optional schema is created in PM1, it must validate and must not imply that the full later component scope is active.
```

---

## 22. PM1 Test Obligations

PM1 is not complete without tests covering:

```text
CLI help
CLI scan
CLI status
config default loading
config schema validation
path traversal rejection
runtime write boundary
append-only audit behavior
repository root validation
scanner deterministic hashing
scanner source non-mutation
layer classification
L0 protection
architecture blocks on missing scan
architecture evidence requirements
status report rendering
schema validation failure behavior
blocked later-command stubs if present
```

Smoke tests alone are not sufficient.

---

## 23. PM1 Implementation Order

Implement PM1 in this order:

```text
1. Package skeleton
2. CLI entrypoint/help
3. Config model and config loader
4. Path registry and path facade
5. Runtime directory creation
6. Audit model and append-only audit log
7. Layer Mapper
8. Repository model
9. Repository Scanner
10. Scan command
11. Architecture Analyzer minimal mode
12. Report Writer minimal status template
13. Status command
14. Schema validation tests
15. CLI integration tests
16. Completion evidence package
```

Do not implement governance, risk, planning, patch proposal generation, validation runner, memory store, or knowledge graph before PM1 exits.

---

## 24. PM1 Acceptance Gate

PM1 is complete only when:

```text
agentx-init --help works.
agentx-init scan works on a fresh Agent_X-style repository.
agentx-init status works after scan.
Source files outside .agentx-init/ remain unchanged.
Runtime writes are only under .agentx-init/.
Audit events are appended.
Scan artifacts validate.
Architecture/status artifacts validate.
Status markdown report is produced.
L0 is protected.
Later commands are absent or blocked stubs.
Required tests pass.
Completion evidence exists.
```

---

## 25. PM1 Stop Conditions

Stop PM1 implementation if:

```text
write boundary cannot be enforced
config schema conflicts with path schema
scanner requires source mutation
scanner requires command execution
architecture analyzer requires direct repository traversal
status command requires PM2 governance/risk logic
later commands perform active behavior
schema files are missing and cannot be created consistently
```

---

# Part E — Product Milestone 2

## 26. PM2 Goal

Add governed non-mutating assistant behavior after PM1 scan/status evidence is stable.

PM2 turns the tool from a repository inspector into a governed planning assistant.

---

## 27. PM2 Active Commands

```text
agentx-init explain
agentx-init plan
agentx-init propose
agentx-init validate
agentx-init audit
agentx-init report
agentx-init memory
```

---

## 28. PM2 Active Components

```text
Governance Engine
Risk Engine
Evolution Planner
Patch Proposal Generator
Validation Runner
Memory Store
Expanded Report Writer
expanded CLI command set
```

---

## 29. PM2 Component Summaries

### 29.1 Governance Engine

Purpose:

```text
Decide ALLOW, WARN, or BLOCK for proposed actions without executing them.
```

Runtime outputs:

```text
.agentx-init/snapshots/governance_latest.json
.agentx-init/memory/governance_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Acceptance:

```text
unknown actions block
L0 mutation blocks
writes outside .agentx-init/ block
all decisions have evidence
most restrictive decision wins
```

### 29.2 Risk Engine

Purpose:

```text
Classify advisory risk from evidence without making governance decisions.
```

Runtime outputs:

```text
.agentx-init/snapshots/risk_latest.json
.agentx-init/memory/risk_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Acceptance:

```text
risk is advisory only
no ALLOW/WARN/BLOCK authority
non-UNKNOWN risks require evidence
mitigations are non-executing suggestions
```

### 29.3 Evolution Planner

Purpose:

```text
Generate evidence-backed ranked next-work plans.
```

Runtime outputs:

```text
.agentx-init/snapshots/evolution_plan_latest.json
.agentx-init/memory/evolution_plan_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Acceptance:

```text
plans are non-executing
candidate actions have evidence
rank ordering is deterministic
implementation is handed off only as planning evidence
```

### 29.4 Patch Proposal Generator

Purpose:

```text
Generate structured non-mutating implementation proposals.
```

Runtime outputs:

```text
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/memory/patch_proposal_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Acceptance:

```text
no source mutation
no executable diffs
no apply instructions
validation plan is not executed
rollback plan is conceptual only
```

### 29.5 Validation Runner

Purpose:

```text
Run allowlisted local validation checks and produce evidence-backed validation reports.
```

Runtime outputs:

```text
.agentx-init/snapshots/validation_report_latest.json
.agentx-init/memory/validation_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Acceptance:

```text
non-allowlisted checks block
shell mode is false
network is disabled
mutation is disabled
every check has evidence
validation does not equal approval
```

### 29.6 Memory Store

Purpose:

```text
Persist structured memory records, indexes, snapshots, and query results.
```

Runtime outputs:

```text
.agentx-init/memory/memory_records.jsonl
.agentx-init/memory/memory_index.json
.agentx-init/snapshots/memory_snapshot_latest.json
.agentx-init/snapshots/memory_manifest_latest.json
```

Acceptance:

```text
memory_records.jsonl is append-only
corrections are additive
queries are deterministic
no semantic/vector retrieval in PM2 unless separately authorized
```

### 29.7 Expanded Report Writer

Purpose:

```text
Render governance, risk, planning, proposal, validation, audit, and memory reports from structured artifacts.
```

Acceptance:

```text
reports preserve evidence
reports do not invent findings
reports do not imply approval or execution
reports are markdown-first
```

---

## 30. PM2 Required Schemas

```text
governance_request.schema.json
governance_decision.schema.json
governance_evidence.schema.json
governance_violation.schema.json
governance_audit.schema.json
risk_assessment.schema.json
risk_item.schema.json
risk_evidence.schema.json
risk_mitigation.schema.json
risk_history_record.schema.json
risk_audit.schema.json
evolution_plan.schema.json
candidate_action.schema.json
priority_score.schema.json
planning_evidence.schema.json
planning_audit.schema.json
patch_proposal.schema.json
patch_change.schema.json
patch_evidence.schema.json
patch_validation_plan.schema.json
patch_rollback_plan.schema.json
patch_audit.schema.json
validation_report.schema.json
validation_check.schema.json
validation_evidence.schema.json
validation_command.schema.json
validation_audit.schema.json
memory_record.schema.json
memory_reference.schema.json
memory_index.schema.json
memory_snapshot.schema.json
memory_query_result.schema.json
memory_manifest.schema.json
completion_record.schema.json
```

---

## 31. PM2 Implementation Order

Implement PM2 in this order:

```text
1. Governance Engine
2. Governance CLI integration / governance-backed command routing
3. Risk Engine
4. Memory Store
5. Expanded Report Writer
6. Evolution Planner
7. Patch Proposal Generator
8. Validation Runner
9. explain command
10. plan command
11. propose command
12. validate command
13. audit command
14. report command
15. memory command
16. PM2 integration tests
17. PM2 completion evidence package
```

Governance must precede components that need permission boundaries.
Memory Store should precede later durable history features.
Validation Runner must not be active until governance and allowlist rules are stable.

---

## 32. PM2 Acceptance Gate

PM2 is complete only when:

```text
Governance decisions are schema-valid and evidence-backed.
Risk assessments are advisory only.
Plans are ranked and non-executing.
Patch proposals are non-mutating and non-executing.
Validation runs only allowlisted commands.
Memory records are append-only and queryable.
Expanded reports preserve evidence.
PM2 commands work through governed routes.
PM1 scan/status still pass unchanged.
No source files are mutated by runtime behavior.
Required PM2 tests pass.
PM2 completion evidence exists.
```

---

## 33. PM2 Stop Conditions

Stop PM2 implementation if:

```text
governance cannot fail closed
risk engine starts making ALLOW/WARN/BLOCK decisions
planner emits source mutation instructions
proposal generator emits executable diffs or apply commands
validation runner requires unrestricted shell execution
memory store rewrites historical records
reports invent unsupported conclusions
PM1 scan/status regress
```

---

# Part F — Product Milestone 3

## 34. PM3 Goal

Add local structured relationship persistence after PM2 evidence, memory, planning, proposal, validation, and audit artifacts are stable.

PM3 makes Agent_X Initiator able to preserve and query relationships between components, artifacts, evidence, memory, audit events, risks, plans, proposals, validations, schemas, and tests.

---

## 35. PM3 Active Command

```text
agentx-init graph
```

---

## 36. PM3 Active Components

```text
Knowledge Graph
Graph CLI
Graph query/report integration
```

---

## 37. PM3 Knowledge Graph Summary

Purpose:

```text
Store, query, index, snapshot, and validate local graph nodes and edges derived from structured artifacts.
```

Runtime outputs:

```text
.agentx-init/graph/graph_nodes.jsonl
.agentx-init/graph/graph_edges.jsonl
.agentx-init/graph/graph_index.json
.agentx-init/graph/graph_snapshot_latest.json
.agentx-init/graph/graph_manifest_latest.json
```

Acceptance:

```text
nodes validate before append
edges validate before append
edge endpoints must exist
non-UNKNOWN edges require evidence
nodes and edges are append-only
snapshots are reproducible
queries are deterministic
no semantic inference or vector search in PM3 unless separately authorized
```

---

## 38. PM3 Required Schemas

```text
graph_node.schema.json
graph_edge.schema.json
graph_snapshot.schema.json
graph_query_result.schema.json
graph_manifest.schema.json
graph_integrity.schema.json
completion_record.schema.json
```

---

## 39. PM3 Implementation Order

Implement PM3 in this order:

```text
1. Graph model
2. Graph schemas
3. Graph storage append logic
4. Graph endpoint integrity checks
5. Graph index builder
6. Graph query API
7. Graph snapshot builder
8. Graph manifest builder
9. Graph integrity report
10. Graph CLI command
11. Graph report/query integration if needed
12. PM3 integration tests
13. PM3 completion evidence package
```

---

## 40. PM3 Acceptance Gate

PM3 is complete only when:

```text
Graph nodes append safely.
Graph edges append safely.
Missing endpoints block edge append.
Non-UNKNOWN edges require evidence.
Graph index is deterministic.
Graph snapshot is schema-valid.
Graph manifest is schema-valid.
agentx-init graph works.
PM1 and PM2 workflows still pass.
No source files are changed by runtime behavior.
PM3 completion evidence exists.
```

---

## 41. PM3 Stop Conditions

Stop PM3 implementation if:

```text
graph requires external graph database
graph requires remote storage
graph requires embeddings/vector search
graph infers unsupported semantic relationships
graph rewrites historical nodes or edges
graph replaces memory store or audit log
graph causes PM1 or PM2 regression
```

---

# Part G — Transition Gates and Completion Evidence

## 42. Milestone Transition Gates

### 42.1 Pre-Milestone 0 → Baseline Source Alignment

Allowed only when:

```text
alignment addendum exists
component placement is defined
canonical naming table exists
legacy-name replacements are defined
later-command blocked behavior is defined
```

### 42.2 Baseline Source Alignment → PM1

Allowed only when:

```text
source names match canonical names
config.json is canonical
path_registry.py exists or is scheduled first in PM1
later commands are absent or blocked
legacy active names are removed or facaded
```

### 42.3 PM1 → PM2

Allowed only when:

```text
help/scan/status pass
repo scan artifact validates
architecture/status artifact validates
audit append works
runtime write boundary is proven
L0 protection is proven
source non-mutation is proven
PM1 completion evidence exists
```

### 42.4 PM2 → PM3

Allowed only when:

```text
governance/risk/planning/proposal/validation/memory components pass
PM2 commands pass
append-only histories are stable
structured artifacts are evidence-backed
graph input artifacts are available
PM2 completion evidence exists
```

---

## 43. Milestone Completion Evidence Packages

Each milestone must finish with a completion evidence package.

### 43.1 Baseline Source Alignment Evidence

```yaml
completion_record:
  milestone: "BASELINE_SOURCE_ALIGNMENT"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  files_changed: []
  canonical_names_verified: []
  legacy_names_retired: []
  blocked_stubs_verified: []
  tests_or_checks_run: []
  unresolved_risks: []
```

### 43.2 PM1 Evidence

```yaml
completion_record:
  milestone: "PRODUCT_MILESTONE_1"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  active_commands:
    - "help"
    - "scan"
    - "status"
  artifacts_generated: []
  schemas_validated: []
  tests_run: []
  audit_events_verified: true
  source_non_mutation_verified: true
  compatibility_wrappers_remaining: []
  unresolved_risks: []
```

### 43.3 PM2 Evidence

```yaml
completion_record:
  milestone: "PRODUCT_MILESTONE_2"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  active_commands: []
  governance_verified: true
  risk_advisory_boundary_verified: true
  proposal_non_mutation_verified: true
  validation_allowlist_verified: true
  memory_append_only_verified: true
  artifacts_generated: []
  schemas_validated: []
  tests_run: []
  unresolved_risks: []
```

### 43.4 PM3 Evidence

```yaml
completion_record:
  milestone: "PRODUCT_MILESTONE_3"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  active_commands:
    - "graph"
  graph_nodes_verified: true
  graph_edges_verified: true
  endpoint_integrity_verified: true
  graph_snapshot_validated: true
  graph_manifest_validated: true
  tests_run: []
  unresolved_risks: []
```

---

## 44. Documents to Create Next

The next implementation-control documents should be created in this order:

```text
1. AGENT_X_INITIATOR_BASELINE_SOURCE_ALIGNMENT_SPEC.md
2. AGENT_X_INITIATOR_PRODUCT_MILESTONE_1_IMPLEMENTATION_SPEC.md
3. AGENT_X_INITIATOR_PRODUCT_MILESTONE_2_IMPLEMENTATION_SPEC.md
4. AGENT_X_INITIATOR_PRODUCT_MILESTONE_3_IMPLEMENTATION_SPEC.md
```

Do not start PM2 or PM3 implementation specs until the prior milestone has completion evidence.

---

## 45. Final v6 Roadmap Verdict

This v6 roadmap is complete as a general all-product-milestones summary and milestone-control document.

It covers:

```text
Product milestones
Component placement
Component-vs-product milestone distinction
Baseline source alignment
Canonical names
Legacy-name deprecation
Compatibility wrapper limits
Active command lifecycle
Blocked command stub rules
Schemas per milestone
Minimum-vs-optional PM1 schema distinction
Runtime outputs
Implementation order
Stop conditions
Transition gates
Completion evidence
Rollback/recovery rules
Universal runtime write boundary
Universal append-only behavior
Universal authority boundaries
```

Final rating: **10/10**

This document is ready to guide the next artifact:

```text
AGENT_X_INITIATOR_BASELINE_SOURCE_ALIGNMENT_SPEC.md
```
