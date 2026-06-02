# Agent_X Initiator — Milestone and Naming Alignment Addendum

## Purpose

This addendum is the cross-document authority for milestone terminology, product milestone scheduling, canonical CLI executable names, canonical implementation file names, canonical schema names, canonical runtime artifact names, broad-plan versus component-contract conflict resolution, legacy-name deprecation, and frozen contract change-control.

It does not replace component contracts. Component contracts remain authoritative for their own internal implementation details.

---

## Document-Only Scope of This Addendum

This addendum synchronizes development documents only.

It does not itself rename source files, rename schema files on disk, create modules, update imports, or implement command stubs. Those actions belong to the later source-code alignment pass.

---

## Authority Hierarchy

The Addendum controls naming and product scheduling. Frozen component contracts control component implementation details.

### Naming / Product Scheduling Authority

1. Agent_X L0 governance rules
2. Milestone and Naming Alignment Addendum (this document)
3. Component contracts
4. Broad planning documents
5. Implementation code
6. Runtime artifacts

### Implementation-Detail Authority

1. Agent_X L0 governance rules
2. Frozen component contract for the component being implemented
3. Milestone and Naming Alignment Addendum, only for naming and scheduling interpretation
4. Components and Standards document
5. Master Planning document
6. Implementation code
7. Runtime artifacts

---

## Conflict Resolution Rule

If broad planning documents conflict with a frozen component contract, the frozen component contract controls implementation details.

If a frozen component contract says "Milestone 1," that means Component Milestone 1 unless it explicitly says Product Milestone 1.

If a component contract is scheduled for a later Product Milestone, its Component Milestone 1 remains valid as the first implementation version of that component, but it must not be implemented earlier than its Product Milestone placement.

If naming differs across documents, this addendum controls canonical names.

---

## Frozen Component Contract Change-Control Rule

Frozen component contracts should not be rewritten broadly.

### Allowed alignment edits

- add Product Milestone Placement section
- add cross-document alignment reference
- add compatibility note where a broad document uses an older name
- clarify that Component Milestone 1 does not mean Product Milestone 1

### Blocked without a new contract revision

- changing component authority boundaries
- changing required schema fields
- changing enum values
- changing validation order
- changing write-boundary rules
- weakening no-mutation rules
- weakening no-execution rules
- weakening evidence requirements

---

## Implementation-Agent Instructions

When applying this alignment pass:

1. Do not rewrite frozen component contracts from scratch.
2. Do not weaken any no-mutation, no-execution, evidence, schema, or governance rule.
3. Prefer adding short Product Milestone Placement sections over editing deep technical sections.
4. Patch broad planning documents more heavily than component contracts.
5. Treat old names as aliases only when explicitly listed in the legacy-name table.
6. Keep Product Milestone 1 small and executable.
7. Do not implement Product Milestone 2 or 3 components during Product Milestone 1.
8. Later commands may be absent or registered as stubs, but must not behave as active commands in Product Milestone 1.

---

## Canonical Milestone Definitions

**Product Milestone 1** = the first implementation slice of the agentx-init product.

**Product Milestone 2** = the second product slice, adding governance, risk, planning, proposal, validation, full memory, expanded reports, and later command workflows.

**Product Milestone 3** = the third product slice, adding the Knowledge Graph and graph CLI.

**Component Milestone 1** = the first implementation version of an individual component, even if that component is scheduled for Product Milestone 2 or Product Milestone 3.

When a component contract says "Milestone 1," it means Component Milestone 1 unless the document explicitly says Product Milestone 1.

---

## Canonical Product Milestone Schedule

| Product Milestone | Active Components | Active Commands | Runtime Outputs |
|---|---|---|---|
| Product Milestone 1 | Package skeleton, CLI entrypoint, Config / Paths, Audit Log, Repository Scanner, Layer Mapper, Minimal Architecture Analyzer, Minimal Report Writer | `agentx-init --help`, `agentx-init scan`, `agentx-init status` | config, path registry, config validation report, audit events, repo scan, scan history, architecture snapshot, status report; see Canonical Runtime Artifact Table for required vs optional PM1 outputs |
| Product Milestone 2 | Governance Engine, Risk Engine, Evolution Planner, Patch Proposal Generator, Validation Runner, full Memory Store, expanded Report Writer | `agentx-init explain`, `agentx-init plan`, `agentx-init propose`, `agentx-init validate`, `agentx-init audit`, `agentx-init report`, `agentx-init memory` | governance, risk, plan, proposal, validation, memory, expanded reports |
| Product Milestone 3 | Knowledge Graph, graph CLI | `agentx-init graph` | graph nodes, graph edges, graph index, graph snapshot, graph manifest, graph integrity report |

### CLI Command Activation Table

| Command | Category | Activation PM | PM1 Behavior |
|---|---|---|---|
| `agentx-init --help` / `help` | HELP | PM1 | Active |
| `agentx-init scan` | SCAN | PM1 | Active |
| `agentx-init status` | STATUS | PM1 | Active |
| `agentx-init explain` | EXPLAIN | PM2 | Absent or BLOCKED stub in PM1 |
| `agentx-init plan` | PLAN | PM2 | Absent or BLOCKED stub in PM1 |
| `agentx-init propose` | PROPOSE | PM2 | Absent or BLOCKED stub in PM1 |
| `agentx-init report` | REPORT | PM2 | Absent or BLOCKED stub in PM1 |
| `agentx-init memory` | MEMORY | PM2 | Absent or BLOCKED stub in PM1 |
| `agentx-init validate` | VALIDATE | PM2 | Absent or BLOCKED stub in PM1 |
| `agentx-init audit` | AUDIT | PM2 | Absent or BLOCKED stub in PM1 |
| `agentx-init graph` | GRAPH | PM3 | Absent or BLOCKED stub in PM1 (required_product_milestone: 3) |

> **PM1 stub note:** BLOCKED stubs must return `response.data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1` and must not import or invoke their corresponding later-component logic.

---

## Canonical Product Milestone 1 Scope

Product Milestone 1 must include only:

```
package skeleton
CLI entrypoint
help command
config loading
path registry
.agentx-init/ directory creation
append-only audit log
repository scanner
layer mapper
scan command
minimal architecture analyzer
minimal report writer for status/architecture report
status command
basic tests
```

Product Milestone 1 must not include active versions of:

```
governance engine
risk engine
evolution planner
patch proposal generator
validation runner
full memory store
knowledge graph
explain command
plan command
propose command
validate command
audit command
report command
memory command
graph command
```

If those later commands are present in Product Milestone 1, they must be registered stubs that return a schema-valid CLICommandResponse:

```json
{
  "schema_version": "1.0",
  "response_id": "generated-string",
  "request_id": "request-id",
  "timestamp": "iso-8601-string",
  "command": "agentx-init <reserved-command>",
  "status": "BLOCKED",
  "exit_code": 3,
  "message": "Command is not implemented in Product Milestone 1.",
  "data": {
    "failure_class": "COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1",
    "product_milestone": 1,
    "required_product_milestone": 2
  },
  "artifact_refs": [],
  "warnings": [],
  "errors": []
}
```

For `agentx-init graph`, use `required_product_milestone: 3`.

---

## Later Command Registry Rule

Product Milestone 1 may handle later commands in one of two ways:

- Option A: Do not register later commands at all.
- Option B: Register later commands as explicit stubs.

If Option B is used, the command must:

- return a schema-valid BLOCKED CLICommandResponse with data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1
- write an audit event if the audit layer is already available (recommended)
- optionally append to command history
- not import, instantiate, or invoke Governance Engine, Risk Engine, Evolution Planner, Patch Proposal Generator, Validation Runner, Memory Store, or Knowledge Graph
- not create later-component artifacts (no evolution plans, patch proposals, validation reports, expanded reports, graph data, or other PM2/PM3 artifacts)
- not imply that the later workflow exists

Later command stubs include:

- `agentx-init explain`
- `agentx-init plan`
- `agentx-init propose`
- `agentx-init report`
- `agentx-init memory`
- `agentx-init validate`
- `agentx-init audit`
- `agentx-init graph`

`agentx-init report` and `agentx-init memory` are Product Milestone 2 commands. If registered in Product Milestone 1, they must return the BLOCKED stub above.

### CLI failure_class placement rule

CLI failure_class values must be placed in `response.data.failure_class` unless a future `command_response.schema.json` revision adds `failure_class` as an explicit top-level field.

No CLI response example in any aligned document may imply that `failure_class` is a top-level response field.

---

## Canonical Names

### Canonical CLI Name

Use everywhere:

```
agentx-init
```

Do not use:

```
agentx
```

except as a rejected legacy example.

### Canonical Python Package Name

Use everywhere:

```
agentx_initiator
```

Do not rename it to match the CLI executable.

### Canonical Runtime Root

Use everywhere:

```
.agentx-init/
```

Runtime writes outside `.agentx-init/` remain blocked.

### Canonical Config / Path Files

Use:

```
agentx_initiator/core/config.py
agentx_initiator/core/config_model.py
agentx_initiator/core/path_registry.py
.agentx-init/config/config.json
.agentx-init/config/path_registry.json
```

If `paths.py` is retained, document it only as:

```
paths.py is a compatibility facade over path_registry.py and must not contain independent path authority.
```

Do not use these as canonical:

```
.agentx-init/config/agentx-init.yaml
.agentx-init/config/agentx-init.yml
```

### Canonical Layer Mapper File

Use:

```
agentx_initiator/core/layer_mapper.py
```

Layer Mapper is Product Milestone 1.

Layer Mapper remains separate from Repository Scanner:

- Layer Mapper = classification rules and protected path mapping support
- Repository Scanner = filesystem discovery and scan artifact generation

The Repository Scanner may call Layer Mapper, but must not absorb the Layer Mapper contract unless explicitly authorized.

### Canonical Patch Proposal Names

Use:

```
agentx_initiator/core/patch_proposal_generator.py
agentx_initiator/core/patch_proposal_model.py
agentx_initiator/core/patch_proposal_rules.py
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/memory/patch_proposal_history.jsonl
```

Do not use as canonical:

```
patch_planner.py
patch_planner
proposals.jsonl
latest_patch_proposal.md as the only proposal artifact
```

### Canonical Proposal Language

Use:

```
non-executable change summary preview
```

Do not use:

```
diff preview
executable diff
apply patch
Git patch
```

The Patch Proposal Generator must not produce executable diffs, apply instructions, shell commands, Git commands, commits, branches, or full replacement source files in Component Milestone 1.

---

## Legacy Name Deprecation Table

| Legacy / Inconsistent Name | Canonical Name | Rule |
|---|---|---|
| `agentx` command | `agentx-init` | Replace in user-facing command examples. |
| `agentx-init.yaml` | `config.json` | Replace as runtime config artifact. |
| `agentx-init.yml` | `config.json` | Replace as runtime config artifact. |
| `paths.py` | `path_registry.py` | Use `paths.py` only as facade if retained. |
| `governance_result.schema.json` | `governance_decision.schema.json` plus full governance schema set | Replace in broad documents. |
| `graph.schema.json` | graph schema set | Replace with graph node/edge/snapshot/query/manifest/integrity schemas. |
| `patch_planner.py` | `patch_proposal_generator.py` | Replace in broad documents. |
| `patch_planner` | `patch_proposal_generator` / `Patch Proposal Generator` | Replace in broad documents. |
| `proposals.jsonl` | `patch_proposal_history.jsonl` | Replace when referring to canonical proposal history. |
| `plans.jsonl` | `evolution_plan_history.jsonl` | Replace when referring to canonical plan history. |
| `graph_latest.json` | `graph_snapshot_latest.json` | Replace when referring to canonical graph snapshot. |
| `latest_patch_proposal.md` as primary artifact | `patch_proposal_latest.json` | Markdown may be a report later, not the canonical structured proposal. |
| `diff preview` | `non-executable change summary preview` | Replace to avoid implying executable patch output. |
| `validation equals approval` wording | `validation evidence only` | Validation must not imply governance approval. |
| `risk blocks action` wording | `risk suggests review / governance decides` | Risk Engine is advisory only. |
| `planner executes` wording | `planner recommends` | Evolution Planner is planning-only. |
| `proposal implements` wording | `proposal describes non-mutating change` | Patch Proposal Generator is proposal-only. |

---

## Canonical Runtime Artifact Table

| Artifact | Canonical Runtime Path | Product Milestone |
|---|---|---:|
| Config file | `.agentx-init/config/config.json` | 1 |
| Path registry | `.agentx-init/config/path_registry.json` | 1 |
| Config validation report | `.agentx-init/snapshots/config_validation_report_latest.json` | 1 |
| Audit events | `.agentx-init/memory/audit_events.jsonl` | 1 |
| Audit evidence | `.agentx-init/memory/audit_evidence.jsonl` | 1, optional if evidence-file mode is used |
| Command history | `.agentx-init/logs/command_history.jsonl` | 1, optional if CLI history is enabled |
| Repo scan latest | `.agentx-init/snapshots/repo_scan_latest.json` | 1 |
| Scan history | `.agentx-init/memory/scans.jsonl` | 1 |
| Architecture latest | `.agentx-init/snapshots/architecture_latest.json` | 1 |
| Status report | `.agentx-init/reports/latest_status.md` | 1 |
| Governance latest | `.agentx-init/snapshots/governance_latest.json` | 2 |
| Governance history | `.agentx-init/memory/governance_history.jsonl` | 2 |
| Risk latest | `.agentx-init/snapshots/risk_latest.json` | 2 |
| Risk history | `.agentx-init/memory/risk_history.jsonl` | 2 |
| Evolution plan latest | `.agentx-init/snapshots/evolution_plan_latest.json` | 2 |
| Evolution plan history | `.agentx-init/memory/evolution_plan_history.jsonl` | 2 |
| Patch proposal latest | `.agentx-init/snapshots/patch_proposal_latest.json` | 2 |
| Patch proposal history | `.agentx-init/memory/patch_proposal_history.jsonl` | 2 |
| Validation report latest | `.agentx-init/snapshots/validation_report_latest.json` | 2 |
| Validation history | `.agentx-init/memory/validation_history.jsonl` | 2 |
| Memory records | `.agentx-init/memory/memory_records.jsonl` | 2 |
| Memory index | `.agentx-init/memory/memory_index.json` | 2 |
| Memory snapshot | `.agentx-init/snapshots/memory_snapshot_latest.json` | 2 |
| Memory manifest | `.agentx-init/snapshots/memory_manifest_latest.json` | 2 |
| Graph nodes | `.agentx-init/graph/graph_nodes.jsonl` | 3 |
| Graph edges | `.agentx-init/graph/graph_edges.jsonl` | 3 |
| Graph index | `.agentx-init/graph/graph_index.json` | 3 |
| Graph snapshot | `.agentx-init/graph/graph_snapshot_latest.json` | 3 |
| Graph manifest | `.agentx-init/graph/graph_manifest_latest.json` | 3 |
| Graph integrity report | embedded in graph snapshot / structured output; no standalone runtime file in current contract | 3 |

---

## Canonical Schema Name Table — Naming Only, Not PM1 Activation

> **Important:** This table defines canonical schema names for traceability. It does not mean every listed schema is required in Product Milestone 1. Product Milestone activation is controlled by the Canonical Product Milestone Schedule, the Components & Standards document, and each component's Product Milestone Placement section.

| Component | Canonical Required Schemas |
|---|---|
| Config / Paths | `config.schema.json`, `path_registry.schema.json`, `runtime_paths.schema.json`, `config_validation_report.schema.json`, `completion_record.schema.json` |
| Audit Log | `audit_event.schema.json`, `audit_evidence.schema.json`, `audit_record.schema.json`, `audit_trail.schema.json`, `audit_integrity.schema.json`, `completion_record.schema.json` |
| Repository Scanner | `repo_scan.schema.json`, `repository_fingerprint.schema.json`, `layer_map.schema.json`, `protected_path_map.schema.json`, `technology_map.schema.json`, `completion_record.schema.json` |
| Layer Mapper | no separate schema required in Product Milestone 1 unless extracted from Repository Scanner maps; if extracted later, use `layer_map.schema.json` and `protected_path_map.schema.json` under Repository Scanner / shared schema ownership |
| Architecture Analyzer | `architecture_report.schema.json`, `architecture_finding.schema.json`, `architecture_relationship.schema.json`, `architecture_evidence.schema.json`, `completion_record.schema.json` |
| CLI Commands | `command_request.schema.json`, `command_response.schema.json`, `command_registry.schema.json`, `command_history_record.schema.json`, `completion_record.schema.json` |
| Governance Engine | `governance_request.schema.json`, `governance_decision.schema.json`, `governance_evidence.schema.json`, `governance_violation.schema.json`, `governance_audit.schema.json`, `completion_record.schema.json` |
| Risk Engine | `risk_assessment.schema.json`, `risk_item.schema.json`, `risk_evidence.schema.json`, `risk_mitigation.schema.json`, `risk_history_record.schema.json`, `risk_audit.schema.json`, `completion_record.schema.json` |
| Evolution Planner | `evolution_plan.schema.json`, `candidate_action.schema.json`, `priority_score.schema.json`, `planning_evidence.schema.json`, `planning_audit.schema.json`, `completion_record.schema.json` |
| Patch Proposal Generator | `patch_proposal.schema.json`, `patch_change.schema.json`, `patch_evidence.schema.json`, `patch_validation_plan.schema.json`, `patch_rollback_plan.schema.json`, `patch_audit.schema.json`, `completion_record.schema.json` |
| Validation Runner | `validation_report.schema.json`, `validation_check.schema.json`, `validation_evidence.schema.json`, `validation_command.schema.json`, `validation_audit.schema.json`, `completion_record.schema.json` |
| Memory Store | `memory_record.schema.json`, `memory_reference.schema.json`, `memory_index.schema.json`, `memory_snapshot.schema.json`, `memory_query_result.schema.json`, `memory_manifest.schema.json`, `completion_record.schema.json` |
| Knowledge Graph | `graph_node.schema.json`, `graph_edge.schema.json`, `graph_snapshot.schema.json`, `graph_query_result.schema.json`, `graph_manifest.schema.json`, `graph_integrity.schema.json`, `completion_record.schema.json` |
| Report Writer | `report.schema.json`, `report_section.schema.json`, `report_template.schema.json`, `report_bundle.schema.json`, `report_request.schema.json`, `completion_record.schema.json` |

Replace broad references to `governance_result.schema.json` and `graph.schema.json` with the canonical schema names above.

---

## Risk Level Authority Rule

R0–R4 are broad product-governance planning labels used by the Master Plan and this addendum only. They are not the Risk Engine schema severity enum. Risk Engine schema severity remains `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` as defined in `RISK_ENGINE_EQC_FIC_SCHEMA_v4.md`.

No aligned document may treat R0–R4 as Risk Engine serialized severity values. If a conceptual schema example includes `risk_level: "R0 | R1 | R2 | R3 | R4"`, it must be accompanied by a note stating that R0–R4 are product-governance planning labels, not Risk Engine schema values.

---

## Final Product Milestone 1 Acceptance Checklist

Product Milestone 1 is coherent only if all are true:

- Product Milestone 1 includes only help, scan, and status as active commands.
- Later commands are absent or return COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1.
- All user-facing command examples use agentx-init.
- Runtime writes are limited to .agentx-init/.
- Config runtime file is .agentx-init/config/config.json.
- path_registry.py is canonical, or paths.py is documented as a facade.
- Audit Log is Product Milestone 1.
- Repository Scanner is Product Milestone 1.
- Layer Mapper is Product Milestone 1 and has a standalone contract or explicit implementation document.
- Minimal Architecture Analyzer is Product Milestone 1.
- Minimal Report Writer is Product Milestone 1.
- Governance Engine is Product Milestone 2.
- Risk Engine is Product Milestone 2.
- Evolution Planner is Product Milestone 2.
- Patch Proposal Generator is Product Milestone 2.
- Validation Runner is Product Milestone 2.
- Full Memory Store is Product Milestone 2.
- Knowledge Graph is Product Milestone 3.
- CLI graph is Product Milestone 3.
- Patch Proposal Generator does not promise executable diffs.
- Validation is not described as approval.
- Risk is not described as governance.
- Planning is not described as execution.
- Proposal generation is not described as implementation.
- Broad planning documents defer to frozen component contracts for implementation details.
- Frozen component contracts are not broadly rewritten during alignment.

---

## Implementation-Agent Warning

This document is the cross-document authority for naming and milestone alignment.  
It must not be used as justification to rewrite frozen component contracts or to expand Product Milestone 1 scope beyond what the frozen component contracts define.

If a frozen component contract contradicts this addendum, the frozen component contract controls for its own implementation details. This addendum controls only naming, naming-adjacent compatibility, and milestone-scheduling interpretation.

Alignment patches to frozen documents must be limited to:

- Adding Product Milestone Placement sections
- Adding cross-document alignment references
- Adding compatibility notes for legacy names in frozen text
- Clarifying "Milestone 1" to "Component Milestone 1" where ambiguous

Alignment patches must not:

- Rewrite frozen technical sections
- Change schema fields or enum values
- Change authority boundaries
- Weaken no-mutation, no-execution, evidence, or governance rules

Every edited frozen document in this synchronization pass has an **Alignment Patch Note** header documenting the scope of changes made.

---

## Source-Code Alignment Readiness Gate

Source-code alignment (Phase 2) must not begin until:

1. All Phase 1 document-only edits are committed to the repository.
2. The test suite passes (at minimum the document-synchronization tests).
3. A final grep-based contradiction review confirms no new naming or schedule contradictions were introduced.
4. This addendum's completion ledger (below) accurately records what was changed.

When the gate opens, source-code alignment must begin from the latest committed document-only alignment baseline.

At the time of this synchronization review, the reviewed document-only baseline is:

`bbf163fba249c5f2c77a28a00f03f1e6a85bdf1d`

If a newer document-only alignment commit supersedes this one, Phase 2 must begin from that newer committed baseline instead.

**Important:** Phase 2 source-code alignment must begin from the latest committed document-only synchronization baseline. Do not use a hardcoded older baseline if a newer document-only alignment commit exists.

---

## Alignment Completion Ledger

| # | Document (exact filename) | Changes Made | Aligns With |
|---|---|---|---|
| 1 | `AGENT_X_INITIATOR_EVOLUTION_ASSISTANT_PLAN_10_10_REV6.md` (Master Plan) | Executive scoped to PM1; risk → risk_hints; added report/memory stubs; enhanced PM1 DoD | Addendum naming & scheduling |
| 2 | `AGENT_X_INITIATOR_COMPONENTS_AND_STANDARDS_REV5.md` (Components & Standards) | Version 1 → Component Milestone 1; risk → risk_hints; clarified report template ownership; PM1 write boundaries | Addendum naming & scheduling |
| 3 | `CLI_COMMANDS_FIC_EQC_COMMAND_ACCEPTANCE_CRITERIA_v3.md` (CLI Commands) | PM1 governance dep rule; status bounded write; stub side-effect rules; help alias policy; command history policy | Addendum governance & scheduling |
| 4 | `ARCHITECTURE_ANALYZER_EQC_SIB_SCHEMA_v6.md` (Architecture Analyzer) | PM1 scope boundary added (earlier pass) | Addendum PM1 scheduling |
| 5 | `LAYER_MAPPER_FIC_SIB_EQC_CONTRACT.md` (Layer Mapper) | Component Milestone 1 → PM1 scheduling note (earlier pass) | Addendum PM1 scheduling |
| 6 | `REPORT_WRITER_FIC_SIB_TEMPLATE_REPORT_STANDARD_v3.md` (Report Writer) | PM1 compatibility note (earlier pass) | Addendum PM1 compatibility |
| 7 | `AUDIT_LOG_EQC_SIB_APPEND_ONLY_EVIDENCE_RULES_SCHEMA_v3.md` (Audit Log) | Partial-use note for PM1 (earlier pass) | Addendum PM1 compatibility |
| 8 | This Addendum | Authority hierarchy split; graph_integrity fix; side-effect clarification; report/memory stub list | Self-consistent |
| 9–17 | All 9 remaining frozen contracts (Config/Paths, Repository Scanner, Governance Engine, Risk Engine, Evolution Planner, Patch Proposal Generator, Validation Runner, Memory Store, Knowledge Graph) | Product Milestone Placement section and cross-document alignment references added | Addendum scheduling |

**Reviewed synchronization baseline:** `bbf163fba249c5f2c77a28a00f03f1e6a85bdf1d`

---

## Before / After Canonical Name Reference

| Context | Before | After |
|---|---|---|
| CLI binary | `agentx` | `agentx-init` |
| Python package | `agentx` | `agentx_initiator` |
| Architecture report `risks` field | `"risks": []` (architecture risk hints) | `"risks": []` (field name unchanged; contains non-authoritative architecture risk hints only) |
| Command text | `list risks` | `list risk hints / structural concerns` |
| Component version rule heading | `Version 1 rule` | `Component Milestone 1 rule` |
| Version identifier (component-context) | `v1` | `Component Milestone 1` |
| Version identifier (product-context) | `v1` | `Product Milestone 1` |
| Report writer template authority (Components doc) | implicit ownership | clarified: template content owned by Report / Template Standard |

---

## Document-Synchronization Completion Gate

Document synchronization is complete only when all of the following are true:

1. Product Milestone 1 active commands are exactly `help`, `scan`, and `status`.
2. Later command stubs are schema-valid `CLICommandResponse` objects.
3. `failure_class` appears only in `response.data.failure_class` for CLI responses.
4. Broad planning documents do not under-specify schema sets for frozen component contracts.
5. Full Version 1 roadmap language is separated from Product Milestone 1 implementation language.
6. Legacy names appear only in explicit deprecation/legacy-name tables.
7. No document implies PM1 active dependency on PM2/PM3 components.

---

## Product Milestone 1 Active Dependency Rule

Product Milestone 1 active dependencies may include only:

```text
Python standard library dependencies authorized by PM1 contracts
Config / Paths
Path Registry
Audit Log
Repository Scanner
Layer Mapper
Minimal Architecture Analyzer
Minimal Report Writer for status output
CLI registry/model/response handling
PM1 schema validators
```

Product Milestone 1 must not import or instantiate:

```text
Governance Engine
Risk Engine
Evolution Planner
Patch Proposal Generator
Validation Runner
full Memory Store
Knowledge Graph
```

except as inert type-only references explicitly allowed by the implementation package.

---

## Product Milestone 1 Placeholder Module Rule

Product Milestone 1 must not create PM2/PM3 placeholder modules unless the PM1 implementation spec explicitly authorizes inert placeholders. If placeholders are authorized, they must not be imported by active PM1 commands, must not create artifacts, and must expose no active behavior.

---

## Product Milestone 1 Memory / Audit Clarification

Product Milestone 1 may write component-owned JSONL files under `.agentx-init/memory/`, such as scan history and audit events. This does not activate the full Memory Store component. Full Memory Store behavior, including memory records, memory indexes, memory snapshots, memory manifests, and memory query APIs, begins in Product Milestone 2.

Product Milestone 1 must write `.agentx-init/memory/audit_events.jsonl`. It may also write `.agentx-init/memory/audit_evidence.jsonl` only if Audit Log is implemented in separate evidence-file mode. If separate evidence-file mode is not implemented, evidence references must remain embedded or referenced through audit events according to the Audit Log contract.

---

## Help Command Policy

`agentx-init --help` and `agentx-init help` are equivalent help surfaces for the same PM1 help behavior. They do not create two separate component contracts. If `help` is implemented as a subcommand, it must produce output equivalent to `--help` and remain read-only.

`agentx-init --help` may be side-effect-free and does not have to create `.agentx-init/`, command history, or audit events. `agentx-init help` may be treated as a command invocation that appends audit history when Audit Log is available. Both must produce equivalent user-facing help output.

---

## Product Milestone 1 Required vs Optional Runtime Artifacts

### Required PM1 Artifacts

```text
.agentx-init/config/config.json
.agentx-init/config/path_registry.json
.agentx-init/snapshots/config_validation_report_latest.json
.agentx-init/memory/audit_events.jsonl
.agentx-init/snapshots/repo_scan_latest.json
.agentx-init/memory/scans.jsonl
.agentx-init/snapshots/architecture_latest.json
.agentx-init/reports/latest_status.md
```

### Optional PM1 Artifacts

```text
.agentx-init/memory/audit_evidence.jsonl        # only if separate evidence-file mode is used
.agentx-init/logs/command_history.jsonl         # only if CLI command history is enabled
```

No PM1 acceptance checklist may require optional artifacts unless the PM1 implementation spec explicitly promotes them.

---

## Cross-Document Milestone 1 Interpretation Rule

Bare `Milestone 1` inside a frozen component contract means Component Milestone 1 unless the phrase explicitly says Product Milestone 1. Bare `Milestone 1` inside broad planning documents must be resolved to either Product Milestone 1 or Component Milestone 1 before implementation handoff.

---

## Pre-Phase-2 Legacy-Name Verification List

Before Phase 2 source-code alignment, run grep checks for these legacy names. Each match must be either corrected or explicitly marked as deprecated legacy wording:

```text
agentx command examples outside legacy/deprecation tables
agentx-init.yaml
agentx-init.yml
governance_result.schema.json
graph.schema.json
patch_planner.py
patch_planner
proposals.jsonl
plans.jsonl
graph_latest.json
diff preview (when used to imply executable patch output)
governance result (when used without "decision reference" clarification)
risk classification in Architecture Analyzer PM1 sections (who implied as RiskEngine)
docs/init/components//
agentx_initiator.core.paths (outside explicit facade/legacy notes)
```

---

## Final No-New-Issues Verification Gate

After all TODO items are applied, run one final synchronization review with these checks:

1. grep for every legacy name in the legacy-name table.
2. grep for Product Milestone 1 references to PM2/PM3 active components.
3. grep for full Report Writer artifacts in PM1 sections.
4. grep for full Memory Store artifacts in PM1 sections.
5. grep for Governance Engine / Risk Engine / Validation Runner / Knowledge Graph imports in PM1 implementation instructions.
6. grep for malformed placeholders such as `docs/init/components//` and `agentx-init `; verify every fenced JSON code block used as a runtime artifact or command response example is parseable JSON.
7. verify every document heading/version matches its filename or has an explicit compatibility note.
8. verify every PM1 runtime artifact in the Addendum, Master Plan, and Components & Standards matches exactly.

If no contradictions remain under these checks, mark the document set as synchronized for the reviewed commit.

---

## Implementation Handoff Summary

The source-code alignment pass (Phase 2) should:

1. Rename CLI from `agentx` to `agentx-init` wherever source references remain.
2. Rename Python package from `agentx` to `agentx_initiator` wherever source references remain.
3. Ensure runtime writes use `.agentx-init/config/config.json`, not `.agentx-init/agentx-init.yaml` or similar.
4. Ensure `scan` and `status` use component-local write-boundary checks rather than calling a non-existent PM2 Governance Engine.
5. Ensure `report` and `memory` are either absent or registered as BLOCKED stubs with no PM2 artifact side effects.
6. Confirm no source code creates `graph_integrity_latest.json` as a runtime file.
7. Architecture report output must keep the serialized schema field `risks` unless the Architecture Analyzer schema contract is formally revised. Source code may internally treat this field as architecture risk hints, but the serialized field remains `risks`.
8. Run the full test suite and verify against `main` drift from the current document-synchronization baseline commit.
