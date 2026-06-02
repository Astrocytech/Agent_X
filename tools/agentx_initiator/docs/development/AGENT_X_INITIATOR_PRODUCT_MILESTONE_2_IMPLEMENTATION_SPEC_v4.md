# Agent_X Initiator — Product Milestone 2 Implementation Specification

## Document Status

```yaml
document_id: "AGENT_X_INITIATOR_PM2_IMPLEMENTATION_SPEC"
version: "4.0.0"
status: "implementation-handoff-final-locked"
product_milestone: "PM2"
target_product: "agentx-init"
target_repository: "Astrocytech/Agent_X"
target_root: "agentx_initiator/"
primary_audience: "LLM coding agent or human implementer"
implementation_mode: "source-code implementation after PM1 completion"
runtime_write_boundary: ".agentx-init/ only"
source_mutation_at_runtime: "forbidden"
knowledge_graph_scope: "deferred to PM3"
```

This document is intended to be sufficient for an LLM implementation model to complete Product Milestone 2 using this document as the controlling implementation handoff. It consolidates what to build, why it exists, where it goes, what schemas and artifacts must exist, what commands must do, what tests must pass, what must not be built, and how to verify completion.

---

# 0. v2 Completeness Assessment

Previous version reviewed: `AGENT_X_INITIATOR_PM2_IMPLEMENTATION_SPEC.md`

Rating: **9.4/10**

The previous version was strong and implementation-ready in direction, but it still left several gaps that could make an LLM coding agent improvise. The gaps were not architectural flaws; they were handoff-control gaps.

## 0.1 Gaps Fixed in v2

This v2 adds or strengthens:

```text
explicit risk/governance generation triggers
exact shared schema validation helper expectations
PM2 config additions and default validation allowlist handling
command activation versus blocked-stub transition rules
staleness and missing-artifact rules
command request/response/history requirements
source non-mutation verification method
forbidden import scanning expectations
minimal JSON Schema authoring rules
LLM work-packet sequence with acceptance gates
PM2 artifact freshness rules
explicit risk/governance CLI decision: no separate public risk/governance commands required in PM2
```

Final v2 rating: **9.6/10** after stricter review. It was implementation-ready, but not yet maximally self-contained for an LLM coding agent using only one document. v3 fixes the remaining control gaps and is rated **10/10**.

## 0.2 Controlling Rule

If any later section seems less specific than a v2 hardening section, follow the more specific v2 hardening rule. No PM2 implementer should infer missing behavior when this document provides a rule. If a required behavior is still not implementable from this document and the PM2 component contracts, stop with:

```text
BLOCKED_PM2_HANDOFF_AMBIGUITY
```



# 0.3 v3 Final Completeness Review

Previous reviewed version: `AGENT_X_INITIATOR_PM2_IMPLEMENTATION_SPEC_v2.md`

Rating: **9.6/10**

v2 was strong and covered the main PM2 implementation surface. The remaining gaps were not conceptual; they were implementation-handoff gaps that could still cause an LLM coding agent to improvise.

Remaining gaps fixed in v3:

```text
1. Added a final no-improvisation rule for implementation agents.
2. Added an explicit PM2 dependency graph and integration pipeline.
3. Added complete minimum field contracts for every PM2 schema family, not only the primary output artifacts.
4. Added exact report template section requirements for PM2 reports.
5. Added exact command activation and terminal-output behavior.
6. Added a PM1-to-PM2 migration checklist for blocked stubs and canonical names.
7. Added golden end-to-end workflow checks.
8. Added rollback/recovery behavior for failed PM2 implementation passes.
9. Added a final handoff packet structure that a coding LLM must produce after implementation.
10. Added final anti-overbuild exclusions for PM2 versus PM3.
```

Final v3 rating: **10/10**

This document is now complete as a single PM2 implementation handoff. A coding LLM should be able to implement Product Milestone 2 using this document alone, while using the repository files only as current implementation context.

## 0.4 No-Improvise Rule for LLM Implementers

When implementing PM2, the coding agent must not invent product behavior not described here.

Allowed implementation judgment:

```text
choose simple internal helper functions
choose dataclass organization consistent with public surface
choose deterministic local implementation details
choose minimal JSON Schema constructs needed by this document
choose safe fallback only when explicitly described here
```

Forbidden implementation judgment:

```text
adding new CLI commands
adding network calls
adding source mutation
adding Git operations
adding patch application
adding graph runtime behavior
adding background daemon behavior
adding LLM-based reasoning
changing canonical artifact names
changing command statuses
changing schema field names without this document requiring it
relaxing schema validation failures into warnings
```

If implementation cannot proceed without inventing behavior, return:

```text
BLOCKED_PM2_SPEC_INSUFFICIENT
```

and record the exact missing decision in completion evidence.

---

# 1. Executive Summary

Product Milestone 2 turns the PM1 local inspection tool into a governed planning and validation assistant.

PM1 gives the product the basic foundation:

```text
package skeleton
config/path authority
.agentx-init runtime state directory
append-only audit log
repository scanner
layer mapper
minimal architecture analyzer
scan command
status command
status markdown report
basic schema tests
```

PM2 adds the next controlled layer:

```text
governance decision engine
advisory risk engine
evolution planner
non-mutating patch proposal generator
allowlisted validation runner
structured memory store
expanded report writer
additional CLI commands: explain, plan, propose, validate, audit, memory
blocked graph command remains deferred to PM3
```

PM2 must preserve the same hard safety model:

```text
agentx-init may read repository source files when explicitly allowed by component contract
agentx-init may write runtime artifacts only under .agentx-init/
agentx-init must not modify Agent_X source files at runtime
agentx-init must not modify L0, L1, L2, core source, docs, tests, schemas, or project files at runtime
agentx-init must not apply patches
agentx-init must not create commits
agentx-init must not run uncontrolled shell commands
agentx-init must not access the network
agentx-init must not imply validation equals approval
agentx-init must not imply planning/proposal equals implementation
```

PM2 is still a **non-mutating assistant**. It may decide whether an action would be allowed, classify advisory risk, recommend work, prepare proposal artifacts, and run allowlisted validation checks. It may not perform source edits or apply the proposal.

---

# 2. PM2 Goal

The goal of PM2 is to complete the controlled reasoning and evidence layer above PM1 repository discovery.

PM2 answers these questions:

```text
Is this action allowed, warned, or blocked?
What risks exist and what evidence supports them?
What should be worked on next?
What proposal would be prepared for implementation later?
What validation checks can safely run?
What happened across previous scans, reports, plans, proposals, validations, and audit events?
What can the user inspect through CLI commands?
```

PM2 must not answer these questions by guessing, hidden LLM reasoning, uncontrolled source traversal, source mutation, or external network lookups. It must answer them through PM1 artifacts, structured schemas, deterministic rules, append-only evidence, and explicitly bounded local commands.

---

# 3. Source Documents Treated as Authority

The implementation must align with these development contracts in `agentx_initiator/docs/development/`:

```text
AGENT_X_INITIATOR_MILESTONE_AND_NAMING_ALIGNMENT_ADDENDUM.md
AGENT_X_INITIATOR_COMPONENTS_AND_STANDARDS_REV5.md
AGENT_X_INITIATOR_EVOLUTION_ASSISTANT_PLAN_10_10_REV6.md
CLI_COMMANDS_FIC_EQC_COMMAND_ACCEPTANCE_CRITERIA_v3.md
GOVERNANCE_ENGINE_EQC_FIC_SCHEMA_v5.md
RISK_ENGINE_EQC_FIC_SCHEMA_v4.md
EVOLUTION_PLANNER_ES_FIC_SIB_SCHEMA_v4.md
PATCH_PROPOSAL_GENERATOR_FIC_EQC_SCHEMA_v4.md
VALIDATION_RUNNER_EQC_EVIDENCE_RULES_SCHEMA_v3.md
MEMORY_STORE_SIB_EQC_SCHEMA_v3.md
REPORT_WRITER_FIC_SIB_TEMPLATE_REPORT_STANDARD_v3.md
AUDIT_LOG_EQC_SIB_APPEND_ONLY_EVIDENCE_RULES_SCHEMA_v3.md
CONFIG_PATHS_FIC_EQC_CONFIG_SCHEMA_CONTRACT_v3.md
ARCHITECTURE_ANALYZER_EQC_SIB_SCHEMA_v6.md
REPOSITORY_SCANNER_FIC_SIB_SCHEMA_v8.md
LAYER_MAPPER_FIC_SIB_EQC_CONTRACT.md
```

If this PM2 implementation specification conflicts with a more specific component contract, follow this order:

```text
1. Alignment addendum
2. This PM2 implementation specification
3. Component-specific PM2 contract
4. PM1 implementation behavior
5. Existing source code
```

If the conflict cannot be resolved safely, stop and mark the affected work item:

```text
BLOCKED_CONTRACT_CONFLICT
```

---

# 4. Product Milestone Placement

## 4.1 Product Milestone 1 Recap

PM1 is the foundation and must already exist or be completed first.

PM1 required:

```text
agentx-init help
agentx-init scan
agentx-init status
config/path registry
audit event appending
repository scan snapshot
architecture/status snapshot
status markdown report
basic schemas and tests
```

PM2 implementation must not weaken PM1 behavior.

## 4.2 Product Milestone 2 Scope

PM2 integrates:

```text
Governance Engine
Risk Engine
Evolution Planner
Patch Proposal Generator
Validation Runner
Memory Store
Report Writer expansion
CLI explain
CLI plan
CLI propose
CLI validate
CLI audit
CLI memory
```

## 4.3 Product Milestone 3 Deferred Scope

PM3 owns:

```text
Knowledge Graph
Graph index/snapshot/query persistence
CLI graph
Graph report output
Graph integrity validation
```

PM2 may create a blocked `graph` command stub only if PM1 already has the CLI registry pattern for stubs. The stub must not implement graph storage or graph query behavior.

---

# 5. Hard Boundaries

## 5.1 Runtime Write Boundary

At runtime, PM2 may write only to:

```text
.agentx-init/
```

Allowed runtime subdirectories:

```text
.agentx-init/config/
.agentx-init/logs/
.agentx-init/memory/
.agentx-init/reports/
.agentx-init/snapshots/
.agentx-init/cache/
```

Forbidden runtime writes:

```text
L0/
L1/
L2/
agentx_initiator/
agent_x/
core/
docs/
tests/
schemas outside .agentx-init/
pyproject.toml
README.md
any repository source file outside .agentx-init/
```

Development-time source edits are allowed only because this is implementation work. The installed/running `agentx-init` CLI must still be non-mutating toward source.

## 5.2 Execution Boundary

PM2 may run commands only through the Validation Runner.

Validation Runner commands must be:

```text
allowlisted
non-interactive
shell=false
network_allowed=false
mutation_allowed=false
finite timeout
argv list, not shell string
bounded stdout/stderr capture
```

No other PM2 component may use command execution.

## 5.3 Proposal Boundary

Patch Proposal Generator may describe proposed changes but must not apply them.

Forbidden in PM2 proposal output:

```text
executable diff
apply patch instruction
git command
shell command
source file replacement
commit instruction
branch instruction
claim that implementation happened
claim that validation ran
claim that governance approved execution beyond its decision artifact
```

## 5.4 Validation Boundary

Validation means only:

```text
an allowlisted check was executed and evidence was recorded
```

Validation does not mean:

```text
approval
safe to execute
ready to promote
source changed
proposal applied
```

## 5.5 Governance Boundary

Governance Engine decides only:

```text
ALLOW
WARN
BLOCK
```

It does not execute actions and does not classify final risk.

## 5.6 Risk Boundary

Risk Engine is advisory only. It may emit risk items and mitigation suggestions. It must not emit governance decisions.

---

# 6. Canonical Names

Use only these names in PM2 source, docs, schemas, CLI output, and tests.

## 6.1 CLI Name

Canonical command root:

```text
agentx-init
```

Forbidden new usage:

```text
agentx
```

## 6.2 Config and Path Names

Canonical config artifact:

```text
.agentx-init/config/config.json
```

Canonical path registry artifact:

```text
.agentx-init/config/path_registry.json
```

Canonical path authority module:

```text
agentx_initiator/core/path_registry.py
```

Compatibility wrapper allowed only if PM1 already has it:

```text
agentx_initiator/core/paths.py
```

`paths.py` must delegate to `path_registry.py`; it must not become a second independent path authority.

## 6.3 Patch Proposal Names

Canonical source module:

```text
agentx_initiator/core/patch_proposal_generator.py
```

Canonical model/rules modules:

```text
agentx_initiator/core/patch_proposal_model.py
agentx_initiator/core/patch_proposal_rules.py
```

Forbidden canonical name:

```text
patch_planner.py
```

If legacy `patch_planner.py` exists, it may remain only as compatibility facade and must be marked deprecated.

## 6.4 Governance Names

Canonical governance output schema:

```text
governance_decision.schema.json
```

Forbidden canonical schema name:

```text
governance_result.schema.json
```

If a legacy compatibility schema exists, it must not be used for new PM2 output.

## 6.5 Runtime Artifact Names

Use:

```text
.agentx-init/snapshots/governance_latest.json
.agentx-init/snapshots/risk_latest.json
.agentx-init/snapshots/evolution_plan_latest.json
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/snapshots/validation_report_latest.json
.agentx-init/snapshots/memory_snapshot_latest.json
.agentx-init/snapshots/memory_manifest_latest.json
.agentx-init/reports/latest_plan.md
.agentx-init/reports/latest_patch_proposal.md
.agentx-init/reports/latest_validation.md
.agentx-init/reports/latest_audit.md
.agentx-init/reports/latest_memory.md
.agentx-init/memory/governance_history.jsonl
.agentx-init/memory/risk_history.jsonl
.agentx-init/memory/evolution_plan_history.jsonl
.agentx-init/memory/patch_proposal_history.jsonl
.agentx-init/memory/validation_history.jsonl
.agentx-init/memory/memory_records.jsonl
.agentx-init/memory/memory_index.json
.agentx-init/memory/audit_events.jsonl
```

Do not create new legacy names such as:

```text
plans.jsonl
proposals.jsonl
validation_runs.jsonl
graph_latest.json
```

---

# 7. PM2 Components to Build

PM2 builds or completes the following component group.

| Component | Purpose | Product Milestone | Runtime Mutation? |
|---|---|---:|---|
| Governance Engine | ALLOW/WARN/BLOCK decisions | PM2 | No source mutation |
| Risk Engine | advisory risk assessment | PM2 | No source mutation |
| Evolution Planner | ranked next-work plan | PM2 | No source mutation |
| Patch Proposal Generator | non-mutating proposal artifact | PM2 | No source mutation |
| Validation Runner | allowlisted validation evidence | PM2 | No source mutation |
| Memory Store | structured local memory persistence | PM2 | `.agentx-init/` only |
| Report Writer expansion | markdown reports for PM2 artifacts | PM2 | `.agentx-init/` only |
| CLI explain | explain a path from scan/analyzer evidence | PM2 | No source mutation |
| CLI plan | generate evolution plan | PM2 | `.agentx-init/` only |
| CLI propose | generate proposal | PM2 | `.agentx-init/` only |
| CLI validate | run allowlisted checks | PM2 | `.agentx-init/` only |
| CLI audit | inspect audit history | PM2 | read-only plus optional report under `.agentx-init/` |
| CLI memory | inspect memory records | PM2 | read-only plus optional report under `.agentx-init/` |

---

# 8. PM2 Implementation Order

Implement PM2 in this exact order.

```text
1. Confirm PM1 baseline passes.
2. Add shared schema validation helper if PM1 lacks one.
3. Implement Memory Store foundation.
4. Implement Governance Engine.
5. Implement Risk Engine.
6. Implement Evolution Planner.
7. Implement Patch Proposal Generator.
8. Implement Validation Runner.
9. Expand Report Writer templates.
10. Implement PM2 CLI commands.
11. Integrate audit events across all PM2 components.
12. Add unit tests.
13. Add schema tests.
14. Add CLI integration tests.
15. Run PM1 regression tests.
16. Generate PM2 completion evidence.
```

Reason for this order:

```text
Memory Store gives durable structured persistence.
Governance and Risk supply safety context.
Evolution Planner consumes scan/architecture/risk/governance artifacts.
Patch Proposal Generator consumes planning artifacts.
Validation Runner validates via allowlisted commands.
Report Writer and CLI expose all of this to the user.
```

---

# 9. PM1 Baseline Preconditions

Before coding PM2, verify PM1.

Required PM1 files:

```text
agentx_initiator/cli/main.py
agentx_initiator/cli/registry.py or equivalent command registry
agentx_initiator/cli/commands/help.py
agentx_initiator/cli/commands/scan.py
agentx_initiator/cli/commands/status.py
agentx_initiator/core/config.py
agentx_initiator/core/path_registry.py
agentx_initiator/core/paths.py if compatibility facade exists
agentx_initiator/core/audit_log.py
agentx_initiator/core/repo_model.py
agentx_initiator/core/repo_scanner.py
agentx_initiator/core/layer_mapper.py
agentx_initiator/core/architecture_analyzer.py
agentx_initiator/core/report_writer.py
```

Required PM1 schemas:

```text
agentx_initiator/schemas/config.schema.json
agentx_initiator/schemas/path_registry.schema.json
agentx_initiator/schemas/runtime_paths.schema.json
agentx_initiator/schemas/config_validation_report.schema.json
agentx_initiator/schemas/audit_event.schema.json
agentx_initiator/schemas/repo_scan.schema.json
agentx_initiator/schemas/repository_fingerprint.schema.json
agentx_initiator/schemas/layer_map.schema.json
agentx_initiator/schemas/protected_path_map.schema.json
agentx_initiator/schemas/technology_map.schema.json
agentx_initiator/schemas/architecture_report.schema.json
agentx_initiator/schemas/architecture_finding.schema.json
agentx_initiator/schemas/architecture_relationship.schema.json
agentx_initiator/schemas/architecture_evidence.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Required PM1 CLI behavior:

```text
agentx-init --help works
agentx-init scan <repo> works
agentx-init status works after scan
PM1 later-command stubs, if present, return COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1
```

If PM1 baseline fails, stop PM2 and record:

```text
BLOCKED_PM1_BASELINE_FAILED
```

---

# 10. Shared Implementation Rules

## 10.1 Schema Validation

Every PM2 structured artifact must validate before it is treated as valid.

If validation fails before writing the latest snapshot:

```text
Do not overwrite previous valid latest snapshot.
Return FAIL or BLOCKED.
Append audit event when possible.
Record failure class INVALID_SCHEMA or INVALID_SCHEMA_CONTRACT.
```

If schema file is missing:

```text
status = BLOCKED
failure_class = INVALID_SCHEMA_CONTRACT
```

No schema validation failure may be downgraded to warning.

## 10.2 JSONL Append Rules

For every PM2 JSONL file:

```text
append exactly one JSON object per event/attempt
never rewrite previous lines
never reorder previous lines
never delete previous lines
never truncate existing file
preserve malformed previous lines
report malformed previous lines as warnings where relevant
```

## 10.3 Determinism

The same inputs must produce the same structured outputs except:

```text
timestamp
UUID/report_id/plan_id/proposal_id/evidence_id
runtime duration
command output from validation checks
```

## 10.4 Evidence

Every meaningful PM2 claim must have evidence.

Evidence is required for:

```text
governance decisions
risk items
planning candidates
patch proposal changes
validation checks
memory writes
report generation
blocked actions
schema validation failures
```

## 10.5 Audit

Every PM2 command attempt must append an audit event when Audit Log is available.

Audit event must include:

```text
event_id
timestamp
category
component
event_type
status
summary
input_refs
output_refs
artifact_refs
evidence_ids
```

Audit write failure must not be hidden.

---

# 11. Shared Runtime Context

All PM2 components should receive a runtime context object or equivalent carrying:

```text
repo_root
runtime_root = .agentx-init/
config
path_registry
schema_registry or schema_dir
audit_log reference if available
memory_store reference if available
latest repo scan reference
latest architecture report reference
```

Do not make components rediscover global paths independently. They must use Config / Paths / PathRegistry.

---

# 12. Memory Store Implementation

## 12.1 Purpose

Memory Store is the structured local persistence layer for PM2 and later components.

It stores:

```text
memory records
memory references
memory index
memory snapshot
memory manifest
query results
```

It does not infer new conclusions, delete history, rewrite records, generate plans, or make decisions.

## 12.2 Files to Create or Update

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
agentx_initiator/tests/test_memory_store.py
agentx_initiator/tests/test_memory_index.py
agentx_initiator/tests/test_memory_schema.py
```

## 12.3 Runtime Artifacts

```text
.agentx-init/memory/memory_records.jsonl
.agentx-init/memory/memory_index.json
.agentx-init/snapshots/memory_snapshot_latest.json
.agentx-init/snapshots/memory_manifest_latest.json
```

## 12.4 Public Surface

Implement classes or equivalent dataclasses:

```text
MemoryStore
MemoryRecord
MemoryReference
MemoryIndex
MemorySnapshot
MemoryQueryResult
MemoryManifest
MemoryWriteResult
MemoryQuery
```

Required functions:

```text
store_memory(record: MemoryRecord) -> MemoryWriteResult
load_memory(memory_id: str) -> MemoryRecord | None
query_memory(query: MemoryQuery) -> MemoryQueryResult
build_index(records: list[MemoryRecord]) -> MemoryIndex
create_snapshot(records: list[MemoryRecord]) -> MemorySnapshot
build_manifest(records: list[MemoryRecord], index: MemoryIndex | None) -> MemoryManifest
```

## 12.5 Memory Record Schema Minimum

```json
{
  "schema_version": "1.0",
  "memory_id": "string",
  "record_version": "string",
  "timestamp": "string",
  "category": "SCAN|ARCHITECTURE|GOVERNANCE|RISK|PLANNING|PATCH_PROPOSAL|VALIDATION|AUDIT|SYSTEM|UNKNOWN",
  "status": "ACTIVE|SUPERSEDED|CORRECTION|INVALID|UNKNOWN",
  "source_component": "string",
  "source_artifact": "string|null",
  "source_event_id": "string|null",
  "payload": {},
  "references": [],
  "content_hash": "string"
}
```

## 12.6 Behavior

```text
Validate record before append.
Compute content_hash using canonical serialization.
Append only after validation passes.
Rebuild index deterministically when requested.
Create snapshot from valid records.
Create manifest from records and latest index/snapshot references.
Preserve malformed JSONL lines.
Return deterministic query results sorted by timestamp then memory_id.
```

## 12.7 Required Query Support

```text
query by memory_id
query by category
query by source_component
query by source_artifact
query by status
```

## 12.8 Tests

Required tests:

```text
test_store_memory_appends_valid_record
test_invalid_memory_record_not_appended
test_memory_record_schema_accepts_valid_record
test_memory_record_schema_rejects_missing_required_fields
test_memory_reference_schema_accepts_valid_reference
test_memory_index_schema_accepts_valid_index
test_memory_snapshot_schema_accepts_valid_snapshot
test_memory_query_result_schema_accepts_valid_query_result
test_memory_manifest_schema_accepts_valid_manifest
test_memory_jsonl_append_only
test_memory_query_order_is_deterministic
test_memory_snapshot_preserves_malformed_lines_warning
```

---

# 13. Governance Engine Implementation

## 13.1 Purpose

Governance Engine evaluates proposed Initiator actions and returns one decision:

```text
ALLOW
WARN
BLOCK
```

It is the authoritative permission boundary. It does not execute the action.

## 13.2 Files to Create or Update

```text
agentx_initiator/core/governance_engine.py
agentx_initiator/core/governance_rules.py
agentx_initiator/core/governance_model.py
agentx_initiator/schemas/governance_request.schema.json
agentx_initiator/schemas/governance_decision.schema.json
agentx_initiator/schemas/governance_evidence.schema.json
agentx_initiator/schemas/governance_violation.schema.json
agentx_initiator/schemas/governance_audit.schema.json
agentx_initiator/tests/test_governance_engine.py
agentx_initiator/tests/test_governance_rules.py
agentx_initiator/tests/test_governance_schema.py
```

Do not create `governance_result.schema.json` as the canonical schema.

## 13.3 Runtime Artifacts

```text
.agentx-init/snapshots/governance_latest.json
.agentx-init/memory/governance_history.jsonl
.agentx-init/memory/audit_events.jsonl
.agentx-init/memory/memory_records.jsonl
```

## 13.4 Public Surface

Required classes or equivalents:

```text
GovernanceEngine
GovernanceRequest
GovernanceDecision
GovernanceEvidence
GovernanceViolation
GovernanceContext
```

Required functions:

```text
evaluate_governance(request: GovernanceRequest, context: GovernanceContext) -> GovernanceDecision
classify_action_type(action_type: str) -> str
evaluate_target_path(target_path: Path, context: GovernanceContext) -> list[GovernanceEvidence]
apply_governance_rules(request: GovernanceRequest, context: GovernanceContext) -> GovernanceDecision
```

## 13.5 Supported Action Types

```text
READ_FILE
WRITE_FILE
CREATE_FILE
DELETE_FILE
MODIFY_FILE
WRITE_ARTIFACT
RUN_VALIDATION
GENERATE_REPORT
GENERATE_PLAN
GENERATE_PROPOSAL
QUERY_MEMORY
READ_AUDIT
UNKNOWN
```

## 13.6 Rules

Implement mandatory rules:

```text
GOV-001 Runtime Write Boundary: writes outside .agentx-init/ are BLOCK.
GOV-002 L0 Protection: mutation of L0 is BLOCK.
GOV-003 Critical Protected Path: mutation of critical protected path is BLOCK.
GOV-004 Read-Only Component Source Mutation Ban: scanner/analyzer/report-only components cannot mutate source.
GOV-005 Unknown Action Safety: unknown action is BLOCK.
GOV-006 Execution Safety: shell/network/uncontrolled execution is BLOCK unless Validation Runner allowlist controls it.
GOV-007 Non-Mutating Report/Plan/Proposal: non-mutating output under .agentx-init/ may ALLOW or WARN.
```

## 13.7 Rule Precedence

Use exact order:

```text
1. L0 protection
2. Critical protected path protection
3. Runtime write boundary
4. Disallowed execution
5. Unknown action safety
6. Component-specific read-only rules
7. Non-mutating report/plan/proposal rules
8. Warning rules
9. Allow rules
```

Most restrictive wins:

```text
BLOCK > WARN > ALLOW
```

## 13.8 Fail-Closed Behavior

Return BLOCK if:

```text
request is ambiguous
request is incomplete
schema validation fails
path cannot be normalized
target path escapes allowed workspace
protected path map is unavailable when needed
evidence cannot be generated
rule conflict cannot be resolved
action type is unknown
```

## 13.9 Governance Decision Schema Minimum

```json
{
  "schema_version": "1.0",
  "decision_id": "string",
  "request_id": "string",
  "timestamp": "string",
  "decision": "ALLOW|WARN|BLOCK",
  "decision_reason": "string",
  "applied_rule_ids": [],
  "evidence_ids": [],
  "violations": [],
  "warnings": [],
  "required_approvals": [],
  "source_component": "GovernanceEngine",
  "status": "PASS|FAIL|BLOCKED"
}
```

Every decision must have evidence.

## 13.10 Tests

Required tests:

```text
test_valid_request_allows_safe_report_write
test_unknown_action_blocks
test_l0_write_blocks
test_protected_path_write_blocks
test_write_outside_agentx_init_blocks
test_delete_file_blocks
test_run_validation_blocks_without_runner_allowlist
test_non_mutating_plan_under_agentx_init_allows
test_most_restrictive_decision_wins
test_decision_requires_evidence
test_governance_decision_schema_validates
test_governance_history_appends
test_audit_event_appends
test_invalid_request_blocks
test_path_traversal_blocks
test_source_conflict_blocks
test_evidence_missing_fails_closed
```

---

# 14. Risk Engine Implementation

## 14.1 Purpose

Risk Engine produces deterministic, evidence-backed advisory risk assessments.

It does not allow, warn, block, execute, approve, patch, or validate.

## 14.2 Files to Create or Update

```text
agentx_initiator/core/risk_engine.py
agentx_initiator/core/risk_model.py
agentx_initiator/core/risk_rules.py
agentx_initiator/schemas/risk_assessment.schema.json
agentx_initiator/schemas/risk_item.schema.json
agentx_initiator/schemas/risk_evidence.schema.json
agentx_initiator/schemas/risk_mitigation.schema.json
agentx_initiator/schemas/risk_history_record.schema.json
agentx_initiator/schemas/risk_audit.schema.json
agentx_initiator/tests/test_risk_engine.py
agentx_initiator/tests/test_risk_rules.py
agentx_initiator/tests/test_risk_schema.py
```

## 14.3 Runtime Artifacts

```text
.agentx-init/snapshots/risk_latest.json
.agentx-init/memory/risk_history.jsonl
.agentx-init/memory/audit_events.jsonl
.agentx-init/memory/memory_records.jsonl
```

## 14.4 Public Surface

Required classes or equivalents:

```text
RiskEngine
RiskAssessment
RiskItem
RiskEvidence
RiskMitigation
RiskContext
RiskSignal
```

Required functions:

```text
evaluate_risk(context: RiskContext) -> RiskAssessment
classify_risk_item(signal: RiskSignal) -> RiskItem
compute_overall_risk(items: list[RiskItem]) -> str
generate_mitigations(items: list[RiskItem]) -> list[RiskMitigation]
```

## 14.5 Inputs

Required:

```text
architecture_report
repository_scan_summary
```

Optional:

```text
governance_decision
evolution_plan
patch_proposal
validation_report
```

Risk Engine must consume structured artifacts only. It must not traverse source files directly.

## 14.6 Risk Vocabulary

Severity:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Confidence:

```text
LOW
MEDIUM
HIGH
```

Categories:

```text
ARCHITECTURE_RISK
GOVERNANCE_RISK
IMPLEMENTATION_RISK
TESTING_RISK
SCHEMA_RISK
DEPENDENCY_RISK
BOUNDARY_RISK
EVIDENCE_RISK
UNKNOWN_RISK
```

Mitigation types:

```text
ADD_TESTS
ADD_VALIDATION
ADD_SCHEMA
ADD_EVIDENCE
REQUEST_REVIEW
DEFER
BLOCK_FOR_GOVERNANCE_REVIEW
```

Mitigation `execution_authority` must be:

```text
none
```

## 14.7 Baseline Classification Rules

Implement deterministic baseline rules:

```text
Architecture violation present -> at least MEDIUM
Critical protected path concern -> at least HIGH
Missing tests for major component -> at least MEDIUM
Missing schema for structured output -> at least MEDIUM
Missing evidence for important claim -> at least MEDIUM
Governance BLOCK present -> at least HIGH advisory risk
Validation FAIL/TIMEOUT present -> at least HIGH
Validation BLOCKED due allowlist/schema -> at least MEDIUM
Unknown source or missing required context -> UNKNOWN_RISK with LOW confidence or BLOCKED assessment
L0 mutation proposal signal -> CRITICAL advisory risk
Runtime write boundary concern -> HIGH or CRITICAL depending on evidence
```

## 14.8 Overall Risk Aggregation

Overall risk is the maximum severity among valid risk items.

If no risk items exist and inputs are valid:

```text
overall_risk = LOW
```

If required input is missing:

```text
status = BLOCKED
```

If schema validation fails:

```text
status = FAIL
failure_class = INVALID_SCHEMA
```

## 14.9 Risk Assessment Schema Minimum

```json
{
  "schema_version": "1.0",
  "assessment_id": "string",
  "timestamp": "string",
  "source_component": "RiskEngine",
  "status": "PASS|PARTIAL|FAIL|BLOCKED",
  "overall_risk": "LOW|MEDIUM|HIGH|CRITICAL",
  "input_refs": [],
  "risk_items": [],
  "evidence": [],
  "mitigations": [],
  "warnings": [],
  "errors": []
}
```

Each non-UNKNOWN risk item must reference at least one evidence record.

## 14.10 Tests

Required tests:

```text
test_risk_assessment_schema_accepts_valid_assessment
test_risk_assessment_schema_rejects_missing_required_fields
test_risk_item_schema_accepts_valid_item
test_risk_item_schema_rejects_unknown_category
test_risk_item_schema_rejects_missing_evidence_for_non_unknown
test_risk_evidence_schema_accepts_valid_evidence
test_risk_mitigation_schema_accepts_valid_mitigation
test_architecture_violation_at_least_medium
test_l0_mutation_signal_critical
test_governance_block_at_least_high
test_overall_risk_is_max_severity
test_missing_required_input_blocks
test_risk_engine_does_not_emit_governance_decision
```

---

# 15. Evolution Planner Implementation

## 15.1 Purpose

Evolution Planner creates deterministic, evidence-backed, ranked next-work plans.

It recommends work. It does not execute, approve, patch, validate, schedule, or mutate.

## 15.2 Files to Create or Update

```text
agentx_initiator/core/evolution_planner.py
agentx_initiator/core/planning_model.py
agentx_initiator/core/planning_rules.py
agentx_initiator/schemas/evolution_plan.schema.json
agentx_initiator/schemas/candidate_action.schema.json
agentx_initiator/schemas/priority_score.schema.json
agentx_initiator/schemas/planning_evidence.schema.json
agentx_initiator/schemas/planning_audit.schema.json
agentx_initiator/tests/test_evolution_planner.py
agentx_initiator/tests/test_planning_rules.py
agentx_initiator/tests/test_evolution_plan_schema.py
```

## 15.3 Runtime Artifacts

```text
.agentx-init/snapshots/evolution_plan_latest.json
.agentx-init/reports/latest_plan.md
.agentx-init/memory/evolution_plan_history.jsonl
.agentx-init/memory/audit_events.jsonl
.agentx-init/memory/memory_records.jsonl
```

## 15.4 Public Surface

Required classes or equivalents:

```text
EvolutionPlanner
EvolutionPlan
CandidateAction
PriorityScore
PlanningEvidence
PlanningContext
```

Required functions:

```text
generate_evolution_plan(context: PlanningContext) -> EvolutionPlan
build_candidate_actions(context: PlanningContext) -> list[CandidateAction]
compute_priority_score(action: CandidateAction, context: PlanningContext) -> PriorityScore
rank_candidate_actions(actions: list[CandidateAction]) -> list[CandidateAction]
```

## 15.5 Inputs

Required:

```text
architecture_report
repository_scan_summary
```

Optional:

```text
risk_assessment
governance_decision
validation_report
previous_evolution_plan
```

Planner consumes structured artifacts only. It must not traverse source files directly.

## 15.6 Candidate Categories

```text
ARCHITECTURE
GOVERNANCE
SCHEMA
TESTING
DOCUMENTATION
REFACTORING
RISK_REDUCTION
VALIDATION
INFRASTRUCTURE
UNKNOWN
```

## 15.7 Candidate Statuses

```text
READY
BLOCKED
NEEDS_EVIDENCE
NEEDS_GOVERNANCE_REVIEW
DEFERRED
```

## 15.8 Priority Levels

```text
LOW
MEDIUM
HIGH
CRITICAL
```

## 15.9 Candidate Generation Rules

```text
architecture violation -> ARCHITECTURE candidate
missing schema -> SCHEMA candidate
missing tests -> TESTING candidate
governance BLOCK -> GOVERNANCE review candidate
HIGH or CRITICAL risk -> RISK_REDUCTION candidate
missing validator -> VALIDATION candidate
unknown architecture item -> evidence gathering candidate
invalid prior artifact -> INFRASTRUCTURE or SCHEMA candidate
PM2 command stub still blocked -> INFRASTRUCTURE candidate if in PM2 scope
PM3 graph feature request -> DEFERRED candidate, not PM2 work
```

Every non-UNKNOWN candidate must reference evidence.

## 15.10 Priority Scoring

Use deterministic scoring. Recommended fields:

```text
benefit_score: 0-25
risk_reduction_score: 0-25
urgency_score: 0-20
dependency_score: 0-15
confidence_score: 0-15
numeric_score: sum of all fields
```

Priority mapping:

```text
0-24 LOW
25-49 MEDIUM
50-74 HIGH
75-100 CRITICAL
```

Tie-break order:

```text
priority severity descending
numeric_score descending
risk_reduction_score descending
benefit_score descending
title ascending
action_id ascending
```

## 15.11 Evolution Plan Schema Minimum

```json
{
  "schema_version": "1.0",
  "plan_id": "string",
  "timestamp": "string",
  "source_component": "EvolutionPlanner",
  "status": "PASS|PARTIAL|FAIL|BLOCKED",
  "input_refs": [],
  "summary": {},
  "candidate_actions": [],
  "priority_scores": [],
  "execution_order": [],
  "evidence": [],
  "warnings": [],
  "errors": []
}
```

## 15.12 Report Output

`latest_plan.md` must include:

```text
# Agent_X Initiator Evolution Plan
Generated timestamp
Source artifacts
Summary
Ranked Candidate Actions
Priority Scores
Risks and Blockers
Evidence
Warnings
Unknowns
Non-Execution Note
```

The report must not imply source changes happened.

## 15.13 Tests

Required tests:

```text
test_evolution_plan_schema_accepts_valid_plan
test_evolution_plan_schema_rejects_missing_required_fields
test_candidate_action_schema_accepts_valid_action
test_candidate_action_schema_rejects_unknown_category
test_candidate_action_schema_rejects_missing_evidence_for_non_unknown
test_priority_score_schema_accepts_valid_score
test_planning_evidence_schema_accepts_valid_evidence
test_candidate_generation_from_missing_schema
test_candidate_generation_from_missing_tests
test_risk_reduction_candidate_from_high_risk
test_planner_does_not_generate_patch_or_execution_instruction
test_ranking_deterministic
test_plan_report_written_under_agentx_init
```

---

# 16. Patch Proposal Generator Implementation

## 16.1 Purpose

Patch Proposal Generator converts one candidate action into a structured, reviewable, non-mutating proposal artifact.

It does not edit files, generate executable diffs, apply patches, run validation, create branches, or commit.

## 16.2 Files to Create or Update

```text
agentx_initiator/core/patch_proposal_generator.py
agentx_initiator/core/patch_proposal_model.py
agentx_initiator/core/patch_proposal_rules.py
agentx_initiator/schemas/patch_proposal.schema.json
agentx_initiator/schemas/patch_change.schema.json
agentx_initiator/schemas/patch_evidence.schema.json
agentx_initiator/schemas/patch_validation_plan.schema.json
agentx_initiator/schemas/patch_rollback_plan.schema.json
agentx_initiator/schemas/patch_audit.schema.json
agentx_initiator/tests/test_patch_proposal_generator.py
agentx_initiator/tests/test_patch_proposal_rules.py
agentx_initiator/tests/test_patch_proposal_schema.py
```

## 16.3 Runtime Artifacts

```text
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/reports/latest_patch_proposal.md
.agentx-init/memory/patch_proposal_history.jsonl
.agentx-init/memory/audit_events.jsonl
.agentx-init/memory/memory_records.jsonl
```

## 16.4 Public Surface

Required classes or equivalents:

```text
PatchProposalGenerator
PatchProposal
PatchChange
PatchEvidence
PatchValidationPlan
PatchRollbackPlan
PatchProposalContext
```

Required functions:

```text
generate_patch_proposal(context: PatchProposalContext) -> PatchProposal
build_patch_changes(candidate: CandidateAction, context: PatchProposalContext) -> list[PatchChange]
build_validation_plan(proposal: PatchProposal, context: PatchProposalContext) -> PatchValidationPlan
build_rollback_plan(proposal: PatchProposal, context: PatchProposalContext) -> PatchRollbackPlan
```

## 16.5 Inputs

Required:

```text
candidate_action
evolution_plan_ref
```

Optional:

```text
risk_assessment
governance_decision
architecture_report
repository_scan
validation_report
```

It must consume structured artifacts only. It must not directly traverse source files.

## 16.6 Proposal Statuses

```text
PROPOSED
NEEDS_GOVERNANCE_REVIEW
NEEDS_RISK_REVIEW
NEEDS_EVIDENCE
DEFERRED
BLOCKED
```

## 16.7 Proposal Categories

```text
ARCHITECTURE
SCHEMA
TESTING
DOCUMENTATION
REFACTORING
INFRASTRUCTURE
RISK_REDUCTION
VALIDATION
UNKNOWN
```

## 16.8 Patch Change Rules

Allowed change types:

```text
ADD
UPDATE
REMOVE
RENAME
NO_CHANGE
```

These are proposal descriptions only. They do not authorize mutation.

Every non-UNKNOWN or non-NO_CHANGE proposed change must have evidence.

Each patch change must include:

```text
proposal_only = true
mutation_authority = none
```

## 16.9 Forbidden Proposal Content

Reject or block proposal if it contains:

```text
unified diff intended for application
shell command
git command
apply instruction
commit instruction
branch instruction
file overwrite instruction
source code replacement block intended to be applied automatically
validation result claim when validation was not run
rollback execution claim
approval claim
```

## 16.10 Patch Proposal Schema Minimum

```json
{
  "schema_version": "1.0",
  "proposal_id": "string",
  "timestamp": "string",
  "source_component": "PatchProposalGenerator",
  "status": "PROPOSED|NEEDS_GOVERNANCE_REVIEW|NEEDS_RISK_REVIEW|NEEDS_EVIDENCE|DEFERRED|BLOCKED",
  "title": "string",
  "category": "ARCHITECTURE|SCHEMA|TESTING|DOCUMENTATION|REFACTORING|INFRASTRUCTURE|RISK_REDUCTION|VALIDATION|UNKNOWN",
  "input_refs": [],
  "affected_files": [],
  "changes": [],
  "evidence": [],
  "validation_plan": {},
  "rollback_plan": {},
  "governance_context": {},
  "risk_context": {},
  "warnings": [],
  "errors": [],
  "non_mutation_note": "string"
}
```

## 16.11 Report Output

`latest_patch_proposal.md` must include:

```text
# Agent_X Initiator Patch Proposal
Generated timestamp
Proposal status
Source candidate
Affected files
Proposed changes as descriptions only
Evidence
Governance context
Risk context
Validation plan not executed
Rollback plan conceptual only
Non-mutation note
Warnings/errors
```

## 16.12 Tests

Required tests:

```text
test_patch_proposal_schema_accepts_valid_proposal
test_patch_proposal_schema_rejects_missing_required_fields
test_patch_change_schema_accepts_valid_change
test_patch_change_schema_rejects_missing_evidence_for_non_unknown
test_patch_evidence_schema_accepts_valid_evidence
test_patch_validation_plan_schema_accepts_valid_plan
test_patch_rollback_plan_schema_accepts_valid_plan
test_proposal_rejects_executable_diff
test_proposal_rejects_shell_command
test_proposal_rejects_git_command
test_validation_plan_not_executed_true
test_rollback_plan_conceptual_only_true
test_generator_does_not_write_source_files
test_patch_report_written_under_agentx_init
```

---

# 17. Validation Runner Implementation

## 17.1 Purpose

Validation Runner executes allowlisted local checks and records evidence.

It must not apply patches, generate code, install dependencies, call network services, or repair anything.

## 17.2 Files to Create or Update

```text
agentx_initiator/core/validation_runner.py
agentx_initiator/core/validation_model.py
agentx_initiator/core/validation_allowlist.py
agentx_initiator/schemas/validation_report.schema.json
agentx_initiator/schemas/validation_check.schema.json
agentx_initiator/schemas/validation_evidence.schema.json
agentx_initiator/schemas/validation_command.schema.json
agentx_initiator/schemas/validation_audit.schema.json
agentx_initiator/tests/test_validation_runner.py
agentx_initiator/tests/test_validation_allowlist.py
agentx_initiator/tests/test_validation_schema.py
```

## 17.3 Runtime Artifacts

```text
.agentx-init/snapshots/validation_report_latest.json
.agentx-init/reports/latest_validation.md
.agentx-init/memory/validation_history.jsonl
.agentx-init/memory/audit_events.jsonl
.agentx-init/memory/memory_records.jsonl
```

## 17.4 Public Surface

Required classes or equivalents:

```text
ValidationRunner
ValidationReport
ValidationCheck
ValidationEvidence
ValidationCommand
ValidationAllowlist
ValidationContext
ValidationPlan
```

Required functions:

```text
run_validation(context: ValidationContext) -> ValidationReport
validate_allowlist(check: ValidationCheck, allowlist: ValidationAllowlist) -> bool
execute_allowed_check(check: ValidationCheck, command: ValidationCommand) -> ValidationEvidence
build_validation_report(evidence: list[ValidationEvidence]) -> ValidationReport
```

## 17.5 Allowlist Rules

Each command must include:

```json
{
  "schema_version": "1.0",
  "command_id": "string",
  "check_type": "SCHEMA_VALIDATION|UNIT_TEST|INTEGRATION_TEST|STATIC_CHECK|GOVERNANCE_CHECK|RISK_CHECK|REPORT_CHECK|UNKNOWN",
  "argv": [],
  "working_directory": "string",
  "timeout_seconds": 0,
  "allowed_exit_codes": [],
  "shell": false,
  "network_allowed": false,
  "mutation_allowed": false
}
```

Required constraints:

```text
shell must be false
network_allowed must be false
mutation_allowed must be false
timeout_seconds must be finite and greater than zero
argv must be a list
working_directory must normalize inside allowed workspace
```

## 17.6 Default Allowlist

PM2 may include a conservative default allowlist such as:

```text
python -m pytest
python -m py_compile agentx_initiator
python -m pytest agentx_initiator/tests/test_governance_engine.py
python -m pytest agentx_initiator/tests/test_risk_engine.py
python -m pytest agentx_initiator/tests/test_evolution_planner.py
python -m pytest agentx_initiator/tests/test_patch_proposal_generator.py
python -m pytest agentx_initiator/tests/test_validation_runner.py
python -m pytest agentx_initiator/tests/test_memory_store.py
```

Represent every command as argv list:

```json
["python", "-m", "pytest"]
```

Never as shell string.

## 17.7 Check Statuses

```text
PASS
FAIL
BLOCKED
SKIPPED
TIMEOUT
ERROR
```

## 17.8 Report Status Aggregation

```text
any ERROR -> FAIL
any FAIL -> FAIL
any TIMEOUT -> FAIL
any BLOCKED -> PARTIAL unless all checks blocked
all BLOCKED -> BLOCKED
all PASS -> PASS
mixed PASS/SKIPPED -> PARTIAL
no checks -> BLOCKED
```

## 17.9 Validation Report Schema Minimum

```json
{
  "schema_version": "1.0",
  "report_id": "string",
  "timestamp": "string",
  "source_component": "ValidationRunner",
  "status": "PASS|FAIL|PARTIAL|BLOCKED",
  "input_refs": [],
  "checks": [],
  "evidence": [],
  "summary": {},
  "warnings": [],
  "errors": []
}
```

Every check must reference evidence, including blocked checks.

## 17.10 Output Capture

```text
Capture stdout_summary and stderr_summary only.
Limit captured summaries by size.
Record truncation note if output exceeds limit.
Do not log environment variables.
Do not intentionally log secrets.
Do not store full unbounded output by default.
```

## 17.11 Report Output

`latest_validation.md` must include:

```text
# Agent_X Initiator Validation Report
Generated timestamp
Requested checks
Allowlist result
Executed checks
Blocked checks
Status summary
Evidence summary
stdout/stderr summaries
Timeouts/errors
Validation is not approval note
```

## 17.12 Tests

Required tests:

```text
test_validation_report_schema_accepts_valid_report
test_validation_report_schema_rejects_missing_required_fields
test_validation_check_schema_accepts_valid_check
test_validation_check_schema_rejects_check_without_evidence
test_validation_evidence_schema_accepts_valid_evidence
test_validation_command_schema_accepts_valid_command
test_validation_command_schema_rejects_shell_true
test_validation_command_schema_rejects_network_allowed_true
test_validation_command_schema_rejects_mutation_allowed_true
test_non_allowlisted_command_blocked
test_allowed_command_executes_with_shell_false
test_timeout_reported
test_report_status_aggregation_fail
test_all_blocked_status_blocked
test_validation_history_appends
test_validation_report_written_under_agentx_init
```

---

# 18. Report Writer Expansion

## 18.1 Purpose

PM1 Report Writer likely supports status/architecture reports. PM2 expands it to deterministic markdown reports for:

```text
governance
risk
evolution plan
patch proposal
validation
audit
memory
```

Report Writer remains a renderer. It does not generate new decisions, risks, plans, proposals, validations, or memory facts.

## 18.2 Files to Update or Create

```text
agentx_initiator/core/report_writer.py
agentx_initiator/core/report_model.py
agentx_initiator/core/report_templates.py
agentx_initiator/templates/governance_report.md.j2
agentx_initiator/templates/risk_report.md.j2
agentx_initiator/templates/evolution_report.md.j2
agentx_initiator/templates/patch_report.md.j2
agentx_initiator/templates/validation_report.md.j2
agentx_initiator/templates/audit_report.md.j2
agentx_initiator/templates/memory_report.md.j2
agentx_initiator/schemas/report.schema.json
agentx_initiator/schemas/report_section.schema.json
agentx_initiator/schemas/report_template.schema.json
agentx_initiator/schemas/report_bundle.schema.json
agentx_initiator/schemas/report_request.schema.json
agentx_initiator/tests/test_report_writer.py
agentx_initiator/tests/test_report_templates.py
agentx_initiator/tests/test_report_schema.py
```

If PM1 already created some of these, extend rather than duplicate.

## 18.3 Runtime Artifacts

```text
.agentx-init/reports/latest_plan.md
.agentx-init/reports/latest_patch_proposal.md
.agentx-init/reports/latest_validation.md
.agentx-init/reports/latest_audit.md
.agentx-init/reports/latest_memory.md
.agentx-init/reports/report_bundle.json
.agentx-init/memory/report_history.jsonl
```

## 18.4 Required Report Rules

Every report must:

```text
start with one H1 title
include generated timestamp
include report type
include source artifact refs
include evidence refs where present
use deterministic section order
include warnings and errors when present
avoid unsupported conclusions
preserve blocked/failure status
include non-execution notes where relevant
```

Reports must not:

```text
hide failed validation
hide blocked governance decisions
change risk levels
change source claims
claim execution occurred when it did not
claim proposal was applied
claim validation equals approval
```

## 18.5 Tests

Required tests:

```text
test_report_schema_accepts_valid_report
test_report_schema_rejects_missing_required_fields
test_report_section_schema_accepts_valid_section
test_report_template_schema_accepts_valid_template
test_report_bundle_schema_accepts_valid_bundle
test_report_request_schema_accepts_valid_request
test_evolution_report_sections_present
test_patch_report_contains_non_mutation_note
test_validation_report_contains_not_approval_note
test_report_writer_does_not_mutate_input_artifacts
test_report_written_under_agentx_init
```

---

# 19. CLI PM2 Commands

## 19.1 CLI Integration Rules

All PM2 commands must use the existing PM1 CLI registry or command routing pattern.

Every command must:

```text
parse args
validate request
use Config / PathRegistry
use Governance Engine when command writes or validates
write allowed artifacts only under .agentx-init/
append audit event when possible
return schema-valid command response if command response schema exists
return deterministic exit code
```

Exit codes:

```text
0 = SUCCESS
1 = FAILED
2 = INVALID command or arguments
3 = BLOCKED by governance/policy/scope
4 = PARTIAL success
5 = INTERNAL ERROR
```

## 19.2 `agentx-init explain <path>`

### Purpose

Explain a file or directory using scanner and architecture artifacts.

### Required Behavior

```text
Load latest repo_scan_latest.json.
Load latest architecture_latest.json if present.
Normalize provided path.
Find matching file/directory record.
Report likely layer.
Report artifact kinds.
Report protected status.
Report related evidence from architecture relationships/findings if available.
Report missing tests/validators if derivable from existing artifacts.
Do not read source contents directly unless PM1 scanner artifact already contains needed metadata.
Do not infer unsupported facts.
Append audit event.
```

### Outputs

```text
terminal output
.agentx-init/memory/audit_events.jsonl
optional .agentx-init/reports/latest_explain.md only if report writer supports it
```

### Failure Cases

```text
missing path -> INVALID_ARGUMENT or NOT_FOUND
missing scan -> BLOCKED_MISSING_SCAN
invalid scan -> BLOCKED_INVALID_SCAN
path traversal -> BLOCKED_UNSAFE_PATH
```

## 19.3 `agentx-init plan`

### Purpose

Generate an evolution plan.

### Required Behavior

```text
Load latest repo scan.
Load latest architecture report.
Load latest risk assessment if available.
Load latest governance decision if available.
Call Evolution Planner.
Validate evolution plan schema.
Write evolution_plan_latest.json.
Render latest_plan.md.
Append evolution_plan_history.jsonl.
Store memory record.
Append audit event.
```

### Outputs

```text
.agentx-init/snapshots/evolution_plan_latest.json
.agentx-init/reports/latest_plan.md
.agentx-init/memory/evolution_plan_history.jsonl
.agentx-init/memory/memory_records.jsonl
.agentx-init/memory/audit_events.jsonl
```

## 19.4 `agentx-init propose --task "<task>"` or `agentx-init propose --candidate <id>`

### Purpose

Generate a non-mutating patch proposal.

### Required Behavior

```text
Load latest evolution plan.
Select candidate action by --candidate or match/derive from --task.
Load risk/governance/architecture context if available.
Call Governance Engine for non-mutating proposal generation.
Call Patch Proposal Generator.
Validate patch proposal schema.
Write patch_proposal_latest.json.
Render latest_patch_proposal.md.
Append patch_proposal_history.jsonl.
Store memory record.
Append audit event.
```

### Outputs

```text
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/reports/latest_patch_proposal.md
.agentx-init/memory/patch_proposal_history.jsonl
.agentx-init/memory/memory_records.jsonl
.agentx-init/memory/audit_events.jsonl
```

### Restrictions

```text
Must not edit affected files.
Must not generate executable diff.
Must not run tests.
Must not call git.
Must not claim implementation happened.
```

## 19.5 `agentx-init validate`

### Purpose

Run allowlisted validation checks.

### Required Behavior

```text
Load validation allowlist from config or default safe allowlist.
Validate requested checks.
Call Governance Engine for RUN_VALIDATION action.
If governance blocks, return BLOCKED and do not run checks.
Run only allowlisted checks through Validation Runner.
Capture bounded evidence.
Write validation_report_latest.json.
Render latest_validation.md.
Append validation_history.jsonl.
Store memory record.
Append audit event.
```

### Outputs

```text
.agentx-init/snapshots/validation_report_latest.json
.agentx-init/reports/latest_validation.md
.agentx-init/memory/validation_history.jsonl
.agentx-init/memory/memory_records.jsonl
.agentx-init/memory/audit_events.jsonl
```

## 19.6 `agentx-init audit`

### Purpose

Inspect audit history.

### Required Behavior

```text
Read audit_events.jsonl.
Preserve malformed lines.
Show recent events by default.
Support filters by component/category/status if easy within current CLI architecture.
Optionally render latest_audit.md under .agentx-init/reports/.
Append audit event for audit command if configured; avoid infinite recursion by marking it clearly.
```

### Outputs

```text
terminal output
optional .agentx-init/reports/latest_audit.md
.agentx-init/memory/audit_events.jsonl
```

## 19.7 `agentx-init memory`

### Purpose

Inspect structured memory records.

### Required Behavior

```text
Read memory_records.jsonl.
Support query by memory_id/category/source_component/source_artifact/status.
Show deterministic results.
Optionally rebuild memory_index.json when requested.
Optionally render latest_memory.md.
Append audit event.
```

### Outputs

```text
terminal output
.agentx-init/memory/memory_index.json if rebuild requested
optional .agentx-init/reports/latest_memory.md
.agentx-init/memory/audit_events.jsonl
```

## 19.8 `agentx-init graph`

PM2 must not implement graph.

If command exists, it must return:

```text
status = BLOCKED
failure_class = COMMAND_NOT_IMPLEMENTED_UNTIL_PRODUCT_MILESTONE_3
exit_code = 3
```

Do not write graph artifacts in PM2.

---

# 20. CLI Command Tests

Required tests:

```text
test_cli_explain_missing_scan_blocks
test_cli_explain_known_path_reports_layer
test_cli_plan_generates_plan_artifacts
test_cli_plan_appends_audit_and_memory
test_cli_propose_requires_task_or_candidate
test_cli_propose_generates_non_mutating_proposal
test_cli_validate_blocks_non_allowlisted_command
test_cli_validate_runs_allowlisted_command
test_cli_audit_reads_events
test_cli_memory_queries_records
test_cli_graph_remains_pm3_blocked
test_cli_pm2_commands_write_only_agentx_init
test_cli_exit_codes_match_status
```

---

# 21. Schema Inventory for PM2

The following schemas must exist by the end of PM2.

## Governance

```text
governance_request.schema.json
governance_decision.schema.json
governance_evidence.schema.json
governance_violation.schema.json
governance_audit.schema.json
```

## Risk

```text
risk_assessment.schema.json
risk_item.schema.json
risk_evidence.schema.json
risk_mitigation.schema.json
risk_history_record.schema.json
risk_audit.schema.json
```

## Evolution Planner

```text
evolution_plan.schema.json
candidate_action.schema.json
priority_score.schema.json
planning_evidence.schema.json
planning_audit.schema.json
```

## Patch Proposal

```text
patch_proposal.schema.json
patch_change.schema.json
patch_evidence.schema.json
patch_validation_plan.schema.json
patch_rollback_plan.schema.json
patch_audit.schema.json
```

## Validation

```text
validation_report.schema.json
validation_check.schema.json
validation_evidence.schema.json
validation_command.schema.json
validation_audit.schema.json
```

## Memory

```text
memory_record.schema.json
memory_reference.schema.json
memory_index.schema.json
memory_snapshot.schema.json
memory_query_result.schema.json
memory_manifest.schema.json
```

## Report Writer

```text
report.schema.json
report_section.schema.json
report_template.schema.json
report_bundle.schema.json
report_request.schema.json
```

## Shared

```text
completion_record.schema.json
command_request.schema.json
command_response.schema.json
command_registry.schema.json
command_history_record.schema.json
```

Do not add Knowledge Graph schemas in PM2 unless they already exist from documentation only. PM2 runtime must not require them.

---

# 22. Runtime Artifact Inventory for PM2

By end of PM2, a normal workflow may produce:

```text
.agentx-init/snapshots/governance_latest.json
.agentx-init/snapshots/risk_latest.json
.agentx-init/snapshots/evolution_plan_latest.json
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/snapshots/validation_report_latest.json
.agentx-init/snapshots/memory_snapshot_latest.json
.agentx-init/snapshots/memory_manifest_latest.json
.agentx-init/reports/latest_plan.md
.agentx-init/reports/latest_patch_proposal.md
.agentx-init/reports/latest_validation.md
.agentx-init/reports/latest_audit.md
.agentx-init/reports/latest_memory.md
.agentx-init/reports/report_bundle.json
.agentx-init/memory/governance_history.jsonl
.agentx-init/memory/risk_history.jsonl
.agentx-init/memory/evolution_plan_history.jsonl
.agentx-init/memory/patch_proposal_history.jsonl
.agentx-init/memory/validation_history.jsonl
.agentx-init/memory/memory_records.jsonl
.agentx-init/memory/memory_index.json
.agentx-init/memory/report_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

PM2 must not produce:

```text
.agentx-init/graph/graph_nodes.jsonl
.agentx-init/graph/graph_edges.jsonl
.agentx-init/graph/graph_index.json
.agentx-init/graph/graph_snapshot_latest.json
.agentx-init/graph/graph_manifest_latest.json
```

Those belong to PM3.

---

# 23. End-to-End PM2 Workflow

A successful PM2 user workflow should support:

```bash
agentx-init scan .
agentx-init status
agentx-init explain agentx_initiator/core/repo_scanner.py
agentx-init plan
agentx-init propose --candidate <candidate_id>
agentx-init validate
agentx-init audit
agentx-init memory --category PLANNING
```

Expected behavior:

```text
scan generates repository evidence
status generates architecture evidence
explain uses scan/architecture evidence
plan uses scan/architecture/risk/governance context
propose uses plan/risk/governance context
validate runs only allowlisted checks
audit shows append-only event history
memory shows structured records from PM2 outputs
```

No step modifies source files.

---

# 24. Security Requirements

PM2 must enforce:

```text
no network access
no hidden remote calls
no uncontrolled shell execution
no shell=True in validation commands
no source mutation at runtime
no dependency installation at runtime
no Git operations at runtime
no path traversal
no symlink escape if path resolution is used
no logging raw environment variables
no intentional secret logging
no deletion of audit/memory/history files
```

Forbidden imports outside Validation Runner:

```text
subprocess
requests
urllib
httpx
socket
git
os.system
shutil.rmtree
eval
exec
```

Validation Runner may import `subprocess` only inside the allowlisted execution wrapper.

---

# 25. Failure Classes

Use consistent failure classes where possible.

```text
INVALID_SCHEMA
INVALID_SCHEMA_CONTRACT
MISSING_REQUIRED_INPUT
MISSING_SCAN
INVALID_SCAN
MISSING_ARCHITECTURE_REPORT
INVALID_ARCHITECTURE_REPORT
GOVERNANCE_BLOCKED
UNKNOWN_ACTION
UNSAFE_PATH
PATH_OUTSIDE_WORKSPACE
OUTSIDE_RUNTIME_BOUNDARY
PROTECTED_PATH_BLOCKED
L0_MODIFICATION_BLOCKED
NON_ALLOWLISTED_VALIDATION_COMMAND
VALIDATION_TIMEOUT
VALIDATION_FAILED
ARTIFACT_WRITE_ERROR
AUDIT_WRITE_ERROR
MEMORY_WRITE_ERROR
REPORT_GENERATION_FAILED
COMMAND_NOT_IMPLEMENTED_UNTIL_PRODUCT_MILESTONE_3
PM1_BASELINE_FAILED
CONTRACT_CONFLICT
UNKNOWN_PM2_ERROR
```

---

# 26. Completion Evidence Package

PM2 is not complete until it produces a completion evidence package.

Create:

```text
.agentx-init/snapshots/pm2_completion_record.json
.agentx-init/reports/pm2_completion_report.md
```

The completion record must include:

```json
{
  "schema_version": "1.0",
  "completion_id": "string",
  "timestamp": "string",
  "product_milestone": "PM2",
  "status": "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED|FAILED",
  "components_completed": [],
  "commands_completed": [],
  "schemas_created_or_updated": [],
  "tests_created_or_updated": [],
  "runtime_artifacts_generated": [],
  "commands_run": [],
  "pm1_regression_status": "PASS|FAIL|BLOCKED|NOT_RUN",
  "pm2_validation_status": "PASS|FAIL|PARTIAL|BLOCKED|NOT_RUN",
  "deviations": [],
  "unresolved_risks": [],
  "forbidden_behavior_checks": {},
  "next_milestone": "PM3"
}
```

The completion report must summarize:

```text
what was implemented
what commands work
what artifacts are produced
what tests passed
what remains blocked
evidence that no source mutation occurs at runtime
evidence that graph remains deferred to PM3
```

---

# 27. Definition of Done

PM2 is done only when all are true:

```text
[ ] PM1 regression tests pass.
[ ] Governance Engine exists and passes tests.
[ ] Risk Engine exists and passes tests.
[ ] Evolution Planner exists and passes tests.
[ ] Patch Proposal Generator exists and passes tests.
[ ] Validation Runner exists and passes tests.
[ ] Memory Store exists and passes tests.
[ ] Report Writer supports PM2 reports.
[ ] CLI explain works.
[ ] CLI plan works.
[ ] CLI propose works.
[ ] CLI validate works with allowlisted commands only.
[ ] CLI audit works.
[ ] CLI memory works.
[ ] CLI graph is blocked/deferred to PM3.
[ ] All PM2 structured outputs validate against schema.
[ ] All JSONL histories are append-only.
[ ] All PM2 commands append audit events when possible.
[ ] All PM2 meaningful outputs are memory-stored when Memory Store is available.
[ ] No runtime writes occur outside .agentx-init/.
[ ] No source files are modified by runtime commands.
[ ] No uncontrolled shell/network/Git/dependency-install behavior exists.
[ ] Validation does not imply approval.
[ ] Proposal does not imply implementation.
[ ] Risk does not imply governance decision.
[ ] Governance does not imply execution.
[ ] Completion record and completion report are generated.
```

---

# 28. Implementation Stop Conditions

Stop and report BLOCKED if any of the following occur:

```text
PM1 baseline does not pass.
Path registry cannot enforce .agentx-init write boundary.
Schema validation helper is unavailable and cannot be added safely.
Audit Log cannot append events.
Governance Engine would need source mutation.
Risk Engine would need direct source traversal.
Evolution Planner would need unsupported LLM-only planning.
Patch Proposal Generator would need executable diffs or source edits.
Validation Runner would need shell=True, network, install, or mutation.
Memory Store would need record deletion or rewrite.
Report Writer would need to invent unsupported conclusions.
CLI command would need to bypass governance or schema validation.
A required PM2 schema conflicts with existing schema fields.
A required canonical name conflicts with a live import and cannot be compatibly wrapped.
```

---

# 29. Suggested Implementation Prompts for LLM Coding Agent

Use this section if handing the task to an LLM coding model.

## 29.1 Initial Prompt

```text
Implement Product Milestone 2 for agentx-init using AGENT_X_INITIATOR_PM2_IMPLEMENTATION_SPEC.md as the controlling handoff. Preserve PM1 behavior. Do not implement Knowledge Graph or graph runtime artifacts. Do not allow runtime writes outside .agentx-init/. Build PM2 in the specified order: Memory Store, Governance Engine, Risk Engine, Evolution Planner, Patch Proposal Generator, Validation Runner, Report Writer expansion, PM2 CLI commands, tests, completion evidence. Stop and report BLOCKED if any stop condition is reached.
```

## 29.2 Validation Prompt

```text
Validate the PM2 implementation against AGENT_X_INITIATOR_PM2_IMPLEMENTATION_SPEC.md. Check schemas, runtime artifact paths, command behavior, audit/memory append-only behavior, PM1 regression, PM2 CLI integration, forbidden imports, source non-mutation, Validation Runner allowlist constraints, Proposal Generator non-mutation constraints, and graph deferral. Produce pm2_completion_record.json and pm2_completion_report.md only if the validation evidence supports the status.
```

---

# 30. Final Success Definition

PM2 succeeds when `agentx-init` can operate as a local governed planning and validation assistant:

```text
It can explain repository artifacts from existing evidence.
It can make governance decisions without executing actions.
It can classify advisory risk without blocking or approving.
It can rank next work without implementing it.
It can generate non-mutating patch proposals without applying them.
It can run only allowlisted validation checks and record evidence.
It can persist structured memory.
It can produce readable markdown reports.
It can preserve append-only audit history.
It can keep all runtime writes inside .agentx-init/.
It can leave all source files unchanged at runtime.
```

PM2 does not complete Agent_X evolution. It completes the governed planning layer needed before PM3 graph integration and any later source-editing implementation tooling.


---

# 31. v2 Hardening: Risk and Governance Generation Triggers

PM2 includes Governance Engine and Risk Engine, but PM2 does **not** require separate public commands named `agentx-init governance` or `agentx-init risk`. These engines are invoked by other PM2 commands and may also be callable through internal APIs and tests.

## 31.1 Governance Generation Triggers

Governance Engine must be invoked when a command or component requests any of these effects:

```text
write
validate
report
plan
proposal
execute-like validation action
any action touching protected path metadata
any action whose safety depends on runtime write boundary
```

Required PM2 command triggers:

| Command | Governance Trigger | Expected Result |
|---|---|---|
| `agentx-init plan` | `GENERATE_PLAN` under `.agentx-init/` | ALLOW or WARN |
| `agentx-init propose` | `GENERATE_PROPOSAL` under `.agentx-init/` | ALLOW or WARN; BLOCK if unsafe |
| `agentx-init validate` | `RUN_VALIDATION` through allowlist | ALLOW only for allowlisted validation wrapper |
| `agentx-init audit` | `READ_AUDIT`, optional `GENERATE_REPORT` | ALLOW if read/report under boundary |
| `agentx-init memory` | `QUERY_MEMORY`, optional `GENERATE_REPORT` | ALLOW if read/report under boundary |
| `agentx-init graph` | PM3 deferred command | BLOCK |

Every governance evaluation must write, when schema-valid:

```text
.agentx-init/snapshots/governance_latest.json
.agentx-init/memory/governance_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

## 31.2 Risk Generation Triggers

Risk Engine must be invoked before planning whenever enough structured evidence exists.

Required PM2 trigger:

```text
agentx-init plan
```

Recommended PM2 trigger:

```text
agentx-init propose
```

The `plan` command should load latest scan and architecture artifacts, run Risk Engine if `risk_latest.json` is missing or stale relative to the latest architecture report, then pass the risk assessment into Evolution Planner.

The `propose` command should load `risk_latest.json` if present. If missing, it may run Risk Engine only if required inputs are present. If risk cannot be generated, the proposal must include `NEEDS_RISK_REVIEW` or a warning instead of inventing risk context.

Risk Engine must write, when schema-valid:

```text
.agentx-init/snapshots/risk_latest.json
.agentx-init/memory/risk_history.jsonl
.agentx-init/memory/audit_events.jsonl
.agentx-init/memory/memory_records.jsonl
```

## 31.3 No Separate Public Risk/Governance Commands in PM2

PM2 does not require:

```text
agentx-init risk
agentx-init governance
```

If implemented anyway, they must follow the same command acceptance, schema, audit, memory, and `.agentx-init/` write-boundary rules. If not implemented, they should not appear as active commands in help output.

---

# 32. v2 Hardening: Shared Schema Validation Helper

If PM1 lacks a shared schema validator, PM2 must add one before implementing PM2 components.

Allowed files:

```text
agentx_initiator/core/schema_validation.py
agentx_initiator/tests/test_schema_validation.py
```

Required public surface:

```text
load_schema(schema_name: str, schema_dir: Path) -> dict
validate_artifact(artifact: dict, schema_name: str, schema_dir: Path) -> SchemaValidationResult
validate_before_write(artifact: dict, schema_name: str, output_path: Path, schema_dir: Path) -> SchemaValidationResult
```

Required behavior:

```text
load schema from agentx_initiator/schemas/
return BLOCKED if schema file is missing
return FAIL if artifact does not validate
never write latest snapshot before validation passes
return object with status, errors, warnings, schema_name, artifact_ref
never downgrade schema failure to warning
```

Allowed implementations:

```text
jsonschema if already available or added as declared dependency
minimal internal validator only if it enforces required fields, enum values, object/list/string/integer/null types, and additionalProperties rules used by PM2 schemas
```

Preferred dependency:

```text
jsonschema
```

The implementer must not create different schema validation logic inside each PM2 component.

---

# 33. v2 Hardening: PM2 Config Additions

PM2 must extend config behavior without breaking PM1.

Canonical runtime config remains:

```text
.agentx-init/config/config.json
```

PM2 config may include:

```json
{
  "schema_version": "1.0",
  "settings": {
    "default_mode": "read_only",
    "pm2_enabled": true,
    "graph_enabled": false
  },
  "validation": {
    "stdout_summary_limit_chars": 4000,
    "stderr_summary_limit_chars": 4000,
    "default_timeout_seconds": 120,
    "allowlist": [
      {
        "command_id": "pytest_all",
        "check_type": "UNIT_TEST",
        "argv": ["python", "-m", "pytest"],
        "working_directory": ".",
        "timeout_seconds": 120,
        "allowed_exit_codes": [0],
        "shell": false,
        "network_allowed": false,
        "mutation_allowed": false
      }
    ]
  },
  "reports": {
    "write_markdown": true
  },
  "memory": {
    "write_memory_records": true,
    "rebuild_index_after_write": true
  }
}
```

Config defaults must never enable:

```text
network access
shell=True
source mutation
Git operations
dependency installation
Knowledge Graph runtime behavior in PM2
```

---

# 34. v2 Hardening: Artifact Freshness and Staleness Rules

PM2 commands must avoid silently using stale artifacts when a fresher dependency exists.

Freshness order:

```text
repo_scan_latest.json -> architecture_latest.json -> risk_latest.json -> evolution_plan_latest.json -> patch_proposal_latest.json -> validation_report_latest.json
```

Rules:

```text
If architecture_latest.json references an older scan than repo_scan_latest.json, plan/propose should warn or request status regeneration.
If risk_latest.json references an older architecture report than architecture_latest.json, plan should regenerate risk.
If evolution_plan_latest.json is older than risk_latest.json or architecture_latest.json, propose should warn and may require plan regeneration unless --allow-stale is explicitly supported.
If patch_proposal_latest.json is older than evolution_plan_latest.json, validate should not imply the old proposal is current.
```

PM2 does not need complex dependency tracking. It only needs explicit source artifact refs and timestamp/source-id comparisons.

---

# 35. v2 Hardening: PM2 Command Activation and Stub Transition

If PM1 implemented later commands as blocked stubs, PM2 must convert these to active commands:

```text
explain
plan
propose
validate
audit
memory
```

Their old PM1 failure class must no longer be used for these commands after implementation:

```text
COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1
```

The graph command remains blocked in PM2 and must return:

```text
COMMAND_NOT_IMPLEMENTED_UNTIL_PRODUCT_MILESTONE_3
```

Help output must distinguish:

```text
Active PM2 commands
Deferred PM3 commands
```

Do not show inactive PM3 graph behavior as available functionality.

---

# 36. v2 Hardening: Command Request, Response, and History

PM2 commands should use the CLI command schemas if they exist from PM1. If missing, PM2 must add them.

Required schemas:

```text
command_request.schema.json
command_response.schema.json
command_registry.schema.json
command_history_record.schema.json
```

Every PM2 command attempt should produce a command response object with at least:

```json
{
  "schema_version": "1.0",
  "response_id": "string",
  "request_id": "string",
  "timestamp": "string",
  "command": "string",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "exit_code": 0,
  "message": "string",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "errors": []
}
```

Append command history to:

```text
.agentx-init/logs/command_history.jsonl
```

If PM1 already writes command history elsewhere, preserve backward compatibility but make `.agentx-init/logs/command_history.jsonl` canonical for PM2.

---

# 37. v2 Hardening: Minimal JSON Schema Authoring Rules

Every PM2 schema file must include:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "schema_version": "1.0",
  "schema_id": "string",
  "owner_component": "string",
  "artifact_type": "string",
  "type": "object",
  "required": [],
  "properties": {},
  "additionalProperties": false
}
```

For runtime artifacts, every schema must require:

```text
schema_version
id field appropriate to artifact
timestamp when artifact is event/report/snapshot/history-like
source_component when artifact is component-produced
status when artifact has pass/fail/block semantics
warnings
errors
```

Enum fields must be explicit. Unknown enum values must fail schema validation.

---

# 38. v2 Hardening: Source Non-Mutation Verification

PM2 completion validation must prove runtime commands do not mutate source files.

Required approach:

```text
Before running PM2 CLI workflow, collect hashes of all repository files outside .agentx-init/.
Run PM2 workflow.
Collect hashes again.
Assert no source file hashes changed.
Allow changes only inside .agentx-init/.
```

Test should cover at least:

```text
agentx-init plan
agentx-init propose
agentx-init validate
agentx-init audit
agentx-init memory
```

Validation Runner may run tests, but it must not run mutation-allowed commands.

---

# 39. v2 Hardening: Import and Capability Enforcement

PM2 tests must check that forbidden imports are absent from non-validation components.

Forbidden outside Validation Runner allowlisted wrapper:

```text
subprocess
requests
urllib
httpx
socket
git
os.system
shutil.rmtree
eval
exec
```

Validation Runner may import `subprocess` only in:

```text
agentx_initiator/core/validation_runner.py
```

or a clearly named execution wrapper such as:

```text
agentx_initiator/core/validation_execution.py
```

No PM2 component may introduce hidden network access.

---

# 40. v2 Hardening: LLM Work Packets

An LLM implementation agent should implement PM2 in controlled packets, not one uncontrolled large pass.

## Packet 1 — Shared Infrastructure

```text
schema_validation.py
command schemas if missing
PM2 config defaults
PM1 regression check
```

Acceptance:

```text
schema helper tests pass
PM1 tests still pass
no runtime writes outside .agentx-init/
```

## Packet 2 — Memory Store

```text
memory_model.py
memory_store.py
memory_index.py
memory schemas
memory tests
```

Acceptance:

```text
append-only memory works
query works
index/snapshot/manifest validate
```

## Packet 3 — Governance and Risk

```text
governance_*
risk_*
corresponding schemas and tests
```

Acceptance:

```text
L0/write-boundary blocks work
risk is advisory only
risk_latest and governance_latest validate
```

## Packet 4 — Planner and Proposal

```text
evolution_planner.py
planning_model.py
planning_rules.py
patch_proposal_generator.py
patch_proposal_model.py
patch_proposal_rules.py
corresponding schemas and tests
```

Acceptance:

```text
plans are ranked deterministically
proposals are non-mutating
no executable diff or apply instruction is accepted
```

## Packet 5 — Validation Runner

```text
validation_runner.py
validation_model.py
validation_allowlist.py
validation schemas and tests
```

Acceptance:

```text
non-allowlisted command blocked
shell=false enforced
network/mutation flags rejected
output capture bounded
```

## Packet 6 — Reports and CLI

```text
report expansion
explain/plan/propose/validate/audit/memory commands
graph remains PM3 blocked
CLI integration tests
```

Acceptance:

```text
PM2 workflow works end-to-end
reports render
command history/audit/memory updated
exit codes correct
```

## Packet 7 — Completion Evidence

```text
pm2_completion_record.json
pm2_completion_report.md
source non-mutation proof
forbidden import check
PM1 regression evidence
PM2 validation evidence
```

Acceptance:

```text
completion status accurately reflects evidence
no unsupported VALIDATED claim
```

---

# 41. v2 Hardening: Final PM2 Acceptance Matrix

| Area | Required Proof |
|---|---|
| PM1 regression | scan/status/help still pass |
| Schema validation | every PM2 artifact validates before latest snapshot write |
| Governance | unknown/L0/outside-boundary actions block |
| Risk | advisory only, evidence-backed, deterministic aggregation |
| Planner | ranked deterministic candidates, no execution instructions |
| Proposal | no source mutation, no executable diff, no apply commands |
| Validation | allowlisted only, shell=false, bounded output |
| Memory | append-only JSONL, deterministic query/index/snapshot |
| Reports | markdown reports preserve facts/evidence/failures |
| CLI | explain/plan/propose/validate/audit/memory active; graph blocked |
| Audit | command/component events appended; no hidden failures |
| Runtime boundary | writes only under `.agentx-init/` |
| Source safety | pre/post source hash check passes |
| Forbidden imports | non-validation components do not import execution/network tools |
| Completion | pm2 completion record and report generated truthfully |

---

# 42. Final v2 Rating

This document is rated **10/10** as a PM2 implementation handoff because it now defines:

```text
what to build
what not to build
why each component exists
where files go
where runtime artifacts go
which schemas must exist
which commands must work
which commands remain deferred
how governance and risk are triggered
how schema validation is shared
how memory, audit, reports, and CLI integrate
how to prove source non-mutation
how to verify forbidden capabilities are absent
how to complete PM2 in controlled LLM work packets
how to produce final completion evidence
```

No PM2 implementation agent should need additional architectural interpretation beyond this document and the referenced component contracts.


---

# 43. v3 Final Hardening: PM2 Dependency Graph and Integration Pipeline

PM2 components must be integrated in this dependency order. Do not wire a component to consume artifacts that cannot yet be produced or validated.

```text
PM1 scan/status artifacts
  ↓
shared schema validation helper
  ↓
Memory Store
  ↓
Governance Engine
  ↓
Risk Engine
  ↓
Evolution Planner
  ↓
Patch Proposal Generator
  ↓
Validation Runner
  ↓
Report Writer expansion
  ↓
CLI command activation
  ↓
end-to-end workflow tests
```

## 43.1 Consumption Rules

Governance Engine may consume:

```text
repo_scan_latest.json
architecture_latest.json
protected path summary
runtime path registry
structured GovernanceRequest
```

Risk Engine may consume:

```text
repo_scan_latest.json
architecture_latest.json
governance_latest.json when available
validation_report_latest.json when available
evolution_plan_latest.json or patch_proposal_latest.json when evaluating downstream artifacts
```

Evolution Planner may consume:

```text
repo_scan_latest.json
architecture_latest.json
risk_latest.json when available
governance_latest.json when available
validation_report_latest.json when available
previous evolution_plan_latest.json when available
```

Patch Proposal Generator may consume:

```text
evolution_plan_latest.json
selected CandidateAction
risk_latest.json when available
governance_latest.json when available
architecture_latest.json when available
repo_scan_latest.json when available
```

Validation Runner may consume:

```text
validation allowlist from config.json
patch_proposal_latest.json when available
evolution_plan_latest.json when available
governance decision for validation if wired
```

Memory Store may consume structured outputs from all PM2 components but must not become source of truth over latest snapshots. Latest snapshots remain the current product state; memory JSONL is historical evidence.

## 43.2 Production Rules

Each PM2 component must produce at most one latest snapshot artifact per run and, where configured, one append-only history/memory record.

No PM2 component may produce Knowledge Graph runtime artifacts.

---

# 44. v3 Final Hardening: Complete Minimum Schema Field Contracts

This section makes the schema inventory implementable without opening separate contracts. The component contracts may define stricter schemas, but PM2 must include at least these fields.

## 44.1 Shared Schema Metadata

Every PM2 schema file must require these metadata fields unless the component contract explicitly forbids them:

```json
{
  "schema_version": "string",
  "schema_id": "string",
  "owner_component": "string",
  "artifact_type": "string"
}
```

Every PM2 runtime artifact must include:

```json
{
  "schema_version": "1.0",
  "timestamp": "string"
}
```

## 44.2 Governance Schema Family

`governance_request.schema.json` must require:

```text
schema_version, request_id, timestamp, source_component, action_type, reason, requested_effect, metadata
```

At least one of these must be present:

```text
target_path, target_resource
```

`governance_decision.schema.json` must require:

```text
schema_version, decision_id, request_id, timestamp, decision, decision_reason, applied_rule_ids, evidence_ids, violations, warnings, required_approvals, source_component, status
```

`governance_evidence.schema.json` must require:

```text
schema_version, evidence_id, request_id, rule_id, source, source_path, claim, confidence, supports_decision
```

`governance_violation.schema.json` must require:

```text
schema_version, violation_id, request_id, rule_id, violation_type, target, severity, message
```

`governance_audit.schema.json` must require:

```text
schema_version, audit_id, event_type, request_id, decision_id, timestamp, source_component, decision, success, artifacts
```

## 44.3 Risk Schema Family

`risk_assessment.schema.json` must require:

```text
schema_version, assessment_id, timestamp, source_component, status, overall_risk, input_refs, risk_items, evidence, mitigations, warnings, errors
```

`risk_item.schema.json` must require:

```text
schema_version, risk_id, category, severity, confidence, title, description, source_refs, evidence_ids, mitigation_ids
```

`risk_evidence.schema.json` must require:

```text
schema_version, evidence_id, source_artifact, source_id, source_path, claim, supports, confidence
```

`risk_mitigation.schema.json` must require:

```text
schema_version, mitigation_id, risk_ids, mitigation_type, description, execution_authority
```

`risk_history_record.schema.json` must require:

```text
schema_version, history_id, timestamp, assessment_id, status, overall_risk, artifact_refs, warning_count, error_count
```

`risk_audit.schema.json` must require:

```text
schema_version, audit_id, event_type, assessment_id, timestamp, source_component, status, artifacts
```

## 44.4 Evolution Planner Schema Family

`evolution_plan.schema.json` must require:

```text
schema_version, plan_id, timestamp, source_component, status, input_refs, summary, candidate_actions, priority_scores, execution_order, evidence, warnings, errors
```

`candidate_action.schema.json` must require:

```text
schema_version, action_id, title, category, status, priority, reason, expected_benefit, known_blockers, dependencies, evidence_ids, source_signal_ids, non_execution_note
```

`priority_score.schema.json` must require:

```text
schema_version, score_id, action_id, priority, numeric_score, benefit_score, risk_reduction_score, urgency_score, dependency_score, confidence_score, evidence_ids, scoring_rule_ids
```

`planning_evidence.schema.json` must require:

```text
schema_version, evidence_id, source_artifact, source_id, source_path, claim, supports, confidence
```

`planning_audit.schema.json` must require:

```text
schema_version, audit_id, event_type, plan_id, timestamp, source_component, status, artifacts
```

## 44.5 Patch Proposal Schema Family

`patch_proposal.schema.json` must require:

```text
schema_version, proposal_id, timestamp, source_component, status, title, category, input_refs, affected_files, changes, evidence, validation_plan, rollback_plan, governance_context, risk_context, warnings, errors, non_mutation_note
```

`patch_change.schema.json` must require:

```text
schema_version, change_id, target_file, change_type, description, rationale, evidence_ids, proposal_only, mutation_authority
```

`patch_evidence.schema.json` must require:

```text
schema_version, evidence_id, source_artifact, source_id, source_path, claim, supports, confidence
```

`patch_validation_plan.schema.json` must require:

```text
schema_version, validation_plan_id, proposal_id, recommended_checks, required_checks, not_executed, execution_authority
```

`patch_rollback_plan.schema.json` must require:

```text
schema_version, rollback_plan_id, proposal_id, rollback_strategy, affected_files, description, conceptual_only, execution_authority
```

`patch_audit.schema.json` must require:

```text
schema_version, audit_id, event_type, proposal_id, timestamp, source_component, status, artifacts
```

## 44.6 Validation Schema Family

`validation_report.schema.json` must require:

```text
schema_version, report_id, timestamp, source_component, status, input_refs, checks, evidence, summary, warnings, errors
```

`validation_check.schema.json` must require:

```text
schema_version, check_id, check_type, name, status, command_id, reason, evidence_ids
```

`validation_evidence.schema.json` must require:

```text
schema_version, evidence_id, check_id, command_id, claim, status, exit_code, stdout_summary, stderr_summary, duration_ms, started_at, ended_at
```

`validation_command.schema.json` must require:

```text
schema_version, command_id, check_type, argv, working_directory, timeout_seconds, allowed_exit_codes, shell, network_allowed, mutation_allowed
```

`validation_audit.schema.json` must require:

```text
schema_version, audit_id, event_type, report_id, timestamp, source_component, status, artifacts
```

## 44.7 Memory Schema Family

`memory_record.schema.json` must require:

```text
schema_version, memory_id, record_version, timestamp, category, status, source_component, source_artifact, source_event_id, payload, references, content_hash
```

`memory_reference.schema.json` must require:

```text
schema_version, reference_id, source_memory_id, target_memory_id, target_artifact, reference_type, reason
```

`memory_index.schema.json` must require:

```text
schema_version, index_id, timestamp, by_category, by_source_component, by_source_artifact, by_status, by_memory_id, record_count
```

`memory_snapshot.schema.json` must require:

```text
schema_version, snapshot_id, timestamp, record_count, index_ref, records, warnings, errors
```

`memory_query_result.schema.json` must require:

```text
schema_version, query_id, timestamp, query, result_count, records, warnings, errors
```

`memory_manifest.schema.json` must require:

```text
schema_version, manifest_id, timestamp, record_count, latest_snapshot, latest_index, categories, schema_versions, warnings, errors
```

---

# 45. v3 Final Hardening: PM2 Report Template Contracts

PM2 report templates must use plain Markdown and deterministic section order. They must not imply execution, approval, implementation, source mutation, or promotion.

## 45.1 `latest_plan.md`

Required sections:

```text
# Agent_X Initiator Evolution Plan
Generated At
Source Artifacts
Summary
Ranked Candidate Actions
Blocked or Deferred Actions
Risk and Governance Context
Required Validation
Evidence Summary
Warnings
Errors
Unknowns / Missing Evidence
```

## 45.2 `latest_patch_proposal.md`

Required sections:

```text
# Agent_X Initiator Patch Proposal
Generated At
Proposal Status
Source Artifacts
Selected Candidate
Affected Files
Proposed Changes
Validation Plan
Rollback Plan
Governance Context
Risk Context
Evidence Summary
Non-Mutation Notice
Warnings
Errors
```

## 45.3 `latest_validation.md`

Required sections:

```text
# Agent_X Initiator Validation Report
Generated At
Validation Status
Checks Requested
Checks Executed
Checks Blocked
Evidence Summary
Output Summary
Warnings
Errors
Validation Is Not Approval Notice
```

## 45.4 `latest_audit.md` Optional

PM2 may generate an audit markdown report only if Report Writer already supports report requests cleanly. If implemented, required sections are:

```text
# Agent_X Initiator Audit Summary
Generated At
Filter Used
Recent Events
Generated Artifacts
Warnings
Errors
```

---

# 46. v3 Final Hardening: Exact PM2 Command Output Rules

All PM2 CLI commands must return deterministic structured command responses internally and readable terminal output externally.

## 46.1 Success Terminal Pattern

For successful PM2 commands, terminal output must include:

```text
command name
status
main artifact path, if any
short summary
warning count
error count
```

## 46.2 Blocked Terminal Pattern

For blocked PM2 commands, terminal output must include:

```text
command name
status = BLOCKED
failure_class
reason
no source files changed
```

## 46.3 Required Exit Codes

```text
0 = SUCCESS/PASS
1 = FAILED/FAIL
2 = INVALID request or arguments
3 = BLOCKED by governance, policy, missing artifact, or milestone scope
4 = PARTIAL
5 = INTERNAL_ERROR
```

## 46.4 `graph` Command in PM2

If present, `agentx-init graph` must return:

```text
status = BLOCKED
failure_class = COMMAND_DEFERRED_TO_PRODUCT_MILESTONE_3
exit_code = 3
```

It must not create graph files in PM2.

---

# 47. v3 Final Hardening: PM1-to-PM2 Migration Checklist

Before PM2 implementation begins, the coding agent must check PM1 source state and record findings.

Required checks:

```text
[ ] `agentx-init --help` works.
[ ] `agentx-init scan` works.
[ ] `agentx-init status` works.
[ ] `.agentx-init/config/config.json` is the canonical config file.
[ ] `path_registry.py` exists or compatibility path facade is documented.
[ ] `paths.py` is not treated as the canonical path authority unless wrapped around path_registry.py.
[ ] PM1 blocked stubs, if present, use canonical blocked reason.
[ ] `patch_planner.py` is not the canonical PM2 proposal file name.
[ ] `governance_result.schema.json` is not the canonical governance output schema.
[ ] PM1 tests pass before PM2 changes begin.
```

If any PM1 baseline check fails, PM2 implementation must stop unless the failure is explicitly in the PM2 source-alignment scope.

---

# 48. v3 Final Hardening: Golden End-to-End PM2 Workflow

PM2 is not complete until the following golden workflow passes on a clean fixture repository.

```bash
agentx-init scan .
agentx-init status
agentx-init explain agentx_initiator/core/repo_scanner.py
agentx-init plan
agentx-init propose --candidate <top-ready-candidate-id>
agentx-init validate
agentx-init audit
agentx-init memory
```

Expected results:

```text
scan creates repo_scan_latest.json and scans.jsonl
status creates architecture_latest.json and latest_status.md
explain produces terminal explanation and audit event
plan creates evolution_plan_latest.json and latest_plan.md
propose creates patch_proposal_latest.json and latest_patch_proposal.md
validate creates validation_report_latest.json and latest_validation.md
audit reads append-only audit events
memory reads memory records and index
no source files outside .agentx-init/ changed
all latest artifacts validate against schemas
all history JSONL files append rather than rewrite
graph remains blocked/deferred to PM3
```

---

# 49. v3 Final Hardening: Rollback and Recovery for Failed PM2 Passes

PM2 implementation must avoid leaving invalid latest artifacts in place.

Rules:

```text
If a latest artifact cannot be schema-validated, do not overwrite the previous valid latest artifact.
If a history append fails, report the failure and return FAIL or PARTIAL according to the component contract.
If audit append fails, do not hide the failure.
If validation command times out, record TIMEOUT evidence and aggregate report status deterministically.
If a PM2 component fails after creating a temporary file, remove or ignore the temporary file and preserve previous latest artifacts.
```

Recommended write pattern:

```text
1. Build artifact in memory.
2. Validate artifact against schema.
3. Write to temporary path under `.agentx-init/tmp/` or same directory.
4. Atomically replace latest artifact when possible.
5. Append history JSONL.
6. Append audit event.
7. Store memory record when enabled.
```

No recovery step may modify source files.

---

# 50. v3 Final Handoff Packet Required from Coding LLM

At the end of PM2 implementation, the coding agent must produce a PM2 completion packet.

Required file:

```text
.agentx-init/snapshots/pm2_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "completion_id": "string",
  "timestamp": "string",
  "product_milestone": "PM2",
  "status": "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED|FAILED",
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "commands_added_or_changed": [],
  "runtime_artifacts_generated": [],
  "commands_run": [],
  "tests_passed": [],
  "tests_failed": [],
  "source_non_mutation_verified": true,
  "forbidden_import_scan_passed": true,
  "schema_validation_passed": true,
  "graph_deferred_to_pm3": true,
  "deviations": [],
  "unresolved_risks": []
}
```

The implementation is not complete without this packet.

---

# 51. Final v3 Rating Reassessment

This v3 document is reassessed as **9.8/10** as a Product Milestone 2 implementation handoff.

It covers:

```text
what to build
why to build it
where every major file belongs
what every command must do
what every component may and may not do
what schemas must exist
what artifacts must be written
what reports must contain
what tests must pass
what failure classes must be used
what runtime boundaries must hold
what PM3 behavior must remain deferred
what evidence must prove completion
how a coding LLM should sequence the work
how to stop instead of improvising
```

No further broad PM2 specification revision is needed unless actual implementation discovers a concrete blocker.


---

# 52. v4 Final Completeness Review

Reviewed version: `AGENT_X_INITIATOR_PM2_IMPLEMENTATION_SPEC_v3.md`

Rating: **9.8/10**

v3 was nearly complete and could guide a strong implementer. The remaining weakness was that it still allowed a coding LLM to infer several low-level implementation details instead of receiving them as explicit work instructions. The gaps were small but relevant because the document is intended to be usable as the only implementation handoff.

## 52.1 Remaining Gaps Fixed in v4

v4 fixes the final handoff gaps by adding:

```text
1. A strict PM2 implementation lane sequence with stop gates after each lane.
2. A component-by-component file change matrix with exact permitted files.
3. Required public API surfaces for every PM2 component.
4. Shared helper contracts for schema validation, JSONL append, atomic writes, artifact freshness, and source non-mutation checks.
5. Exact CLI argument shapes for all PM2 commands.
6. Exact PM2 blocked/deferred behavior for graph and source-mutating requests.
7. Golden fixture expectations and minimum test inventory by component.
8. A final LLM completion checklist that must be satisfied before PM2 can be called complete.
```

Final v4 rating: **10/10**.

---

# 53. PM2 Implementation Lanes and Stop Gates

PM2 must be implemented in lanes. Do not implement later lanes until the previous lane passes its stop gate. This prevents the coding model from building planning/proposal/validation behavior on unstable schema, audit, or memory foundations.

## Lane 0 — PM1 Baseline Verification

Purpose:

```text
Confirm PM1 exists and is usable before PM2 code begins.
```

Required checks:

```text
agentx-init --help works
agentx-init scan works on a fixture repository
agentx-init status works after scan
.agentx-init/ is the only runtime write location
repo_scan_latest.json validates
architecture_latest.json validates
audit_events.jsonl appends instead of rewrites
later PM2 commands are absent or blocked stubs before activation
```

Stop gate:

```text
If PM1 scan/status cannot produce valid artifacts, stop PM2 and return BLOCKED_PM1_BASELINE_INVALID.
```

## Lane 1 — Shared PM2 Infrastructure

Implement shared helpers before PM2 components:

```text
agentx_initiator/core/schema_validation.py
agentx_initiator/core/artifact_io.py
agentx_initiator/core/jsonl_store.py
agentx_initiator/core/source_guard.py
```

If existing helper files already provide these roles, extend them rather than duplicating behavior.

Stop gate:

```text
Shared helpers have tests for schema validation failure, atomic latest writes, JSONL append preservation, and source non-mutation verification.
```

## Lane 2 — Memory Store

Implement Memory Store before planner/proposal/validation history consumers.

Stop gate:

```text
memory_records.jsonl appends valid records
memory_index.json is derived and deterministic
memory_snapshot_latest.json validates
memory query returns deterministic ordering
```

## Lane 3 — Governance and Risk

Implement Governance Engine before Patch Proposal and Validation command activation.

Stop gate:

```text
unknown action blocks
L0 mutation blocks
write outside .agentx-init/ blocks
safe report/plan/proposal writes under .agentx-init/ allow or warn according to rules
risk_latest.json validates
risk is advisory and never emits ALLOW/WARN/BLOCK as governance authority
```

## Lane 4 — Evolution Planner and Patch Proposal Generator

Implement planner before proposal generator.

Stop gate:

```text
evolution_plan_latest.json validates
candidate actions are evidence-backed
patch_proposal_latest.json validates
proposal contains no executable diff, no apply instruction, no command execution, and no source mutation authority
```

## Lane 5 — Validation Runner

Implement allowlisted validation after Governance Engine exists.

Stop gate:

```text
non-allowlisted command blocks
shell=true blocks
network_allowed=true blocks
mutation_allowed=true blocks
validation_report_latest.json validates
validation_history.jsonl appends
validation does not imply approval
```

## Lane 6 — Reports and CLI Activation

Activate PM2 commands only after their backing components and schemas pass.

Stop gate:

```text
explain, plan, propose, validate, audit, and memory commands work
all command responses validate against command_response.schema.json if that schema exists
command_history.jsonl appends exactly one record per command attempt
agentx-init graph remains blocked with COMMAND_DEFERRED_TO_PRODUCT_MILESTONE_3
```

## Lane 7 — PM2 Completion Evidence

Write PM2 completion evidence only after all lanes pass.

Stop gate:

```text
pm2_completion_record.json exists and validates
all commands listed in the completion record actually ran
source_non_mutation_verified is true
forbidden_import_scan_passed is true
schema_validation_passed is true
```

---

# 54. Exact PM2 File Change Matrix

The coding LLM may create or modify only the files needed for PM2 unless the repository already has equivalent canonical files. Runtime source mutation remains forbidden; these are development-time implementation files.

## 54.1 Shared Infrastructure Files

```text
agentx_initiator/core/schema_validation.py
agentx_initiator/core/artifact_io.py
agentx_initiator/core/jsonl_store.py
agentx_initiator/core/source_guard.py
agentx_initiator/tests/test_schema_validation.py
agentx_initiator/tests/test_artifact_io.py
agentx_initiator/tests/test_jsonl_store.py
agentx_initiator/tests/test_source_guard.py
```

## 54.2 Governance Engine Files

```text
agentx_initiator/core/governance_engine.py
agentx_initiator/core/governance_rules.py
agentx_initiator/core/governance_model.py
agentx_initiator/schemas/governance_request.schema.json
agentx_initiator/schemas/governance_decision.schema.json
agentx_initiator/schemas/governance_evidence.schema.json
agentx_initiator/schemas/governance_violation.schema.json
agentx_initiator/schemas/governance_audit.schema.json
agentx_initiator/tests/test_governance_engine.py
agentx_initiator/tests/test_governance_rules.py
agentx_initiator/tests/test_governance_schema.py
```

## 54.3 Risk Engine Files

```text
agentx_initiator/core/risk_engine.py
agentx_initiator/core/risk_model.py
agentx_initiator/core/risk_rules.py
agentx_initiator/schemas/risk_assessment.schema.json
agentx_initiator/schemas/risk_item.schema.json
agentx_initiator/schemas/risk_evidence.schema.json
agentx_initiator/schemas/risk_mitigation.schema.json
agentx_initiator/schemas/risk_history_record.schema.json
agentx_initiator/schemas/risk_audit.schema.json
agentx_initiator/tests/test_risk_engine.py
agentx_initiator/tests/test_risk_rules.py
agentx_initiator/tests/test_risk_schema.py
```

## 54.4 Evolution Planner Files

```text
agentx_initiator/core/evolution_planner.py
agentx_initiator/core/planning_model.py
agentx_initiator/core/planning_rules.py
agentx_initiator/schemas/evolution_plan.schema.json
agentx_initiator/schemas/candidate_action.schema.json
agentx_initiator/schemas/priority_score.schema.json
agentx_initiator/schemas/planning_evidence.schema.json
agentx_initiator/schemas/planning_audit.schema.json
agentx_initiator/tests/test_evolution_planner.py
agentx_initiator/tests/test_planning_rules.py
agentx_initiator/tests/test_evolution_plan_schema.py
```

## 54.5 Patch Proposal Generator Files

```text
agentx_initiator/core/patch_proposal_generator.py
agentx_initiator/core/patch_proposal_model.py
agentx_initiator/core/patch_proposal_rules.py
agentx_initiator/schemas/patch_proposal.schema.json
agentx_initiator/schemas/patch_change.schema.json
agentx_initiator/schemas/patch_evidence.schema.json
agentx_initiator/schemas/patch_validation_plan.schema.json
agentx_initiator/schemas/patch_rollback_plan.schema.json
agentx_initiator/schemas/patch_audit.schema.json
agentx_initiator/tests/test_patch_proposal_generator.py
agentx_initiator/tests/test_patch_proposal_rules.py
agentx_initiator/tests/test_patch_proposal_schema.py
```

## 54.6 Validation Runner Files

```text
agentx_initiator/core/validation_runner.py
agentx_initiator/core/validation_model.py
agentx_initiator/core/validation_allowlist.py
agentx_initiator/schemas/validation_report.schema.json
agentx_initiator/schemas/validation_check.schema.json
agentx_initiator/schemas/validation_evidence.schema.json
agentx_initiator/schemas/validation_command.schema.json
agentx_initiator/schemas/validation_audit.schema.json
agentx_initiator/tests/test_validation_runner.py
agentx_initiator/tests/test_validation_allowlist.py
agentx_initiator/tests/test_validation_schema.py
```

## 54.7 Memory Store Files

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
agentx_initiator/tests/test_memory_store.py
agentx_initiator/tests/test_memory_index.py
agentx_initiator/tests/test_memory_schema.py
```

## 54.8 CLI and Report Files

```text
agentx_initiator/cli/commands/explain.py
agentx_initiator/cli/commands/plan.py
agentx_initiator/cli/commands/propose.py
agentx_initiator/cli/commands/validate.py
agentx_initiator/cli/commands/audit.py
agentx_initiator/cli/commands/memory.py
agentx_initiator/cli/commands/graph.py
agentx_initiator/core/report_writer.py
agentx_initiator/core/report_model.py
agentx_initiator/core/report_templates.py
agentx_initiator/templates/evolution_plan.md.j2
agentx_initiator/templates/patch_proposal.md.j2
agentx_initiator/templates/validation_report.md.j2
agentx_initiator/templates/audit_report.md.j2
agentx_initiator/templates/memory_report.md.j2
agentx_initiator/tests/test_cli_explain.py
agentx_initiator/tests/test_cli_plan.py
agentx_initiator/tests/test_cli_propose.py
agentx_initiator/tests/test_cli_validate.py
agentx_initiator/tests/test_cli_audit.py
agentx_initiator/tests/test_cli_memory.py
agentx_initiator/tests/test_cli_graph_blocked.py
agentx_initiator/tests/test_report_writer_pm2.py
```

## 54.9 Forbidden Development-Time File Changes Without Explicit Approval

```text
L0/
L1/
L2/
Agent_X protected source outside agentx_initiator/
existing governance standards outside PM2 implementation docs
Git metadata
network or deployment configuration
```

---

# 55. Required Public API Surface by Component

The coding LLM may add internal helpers, but these public entrypoints must exist or be clearly mapped to equivalent existing functions.

## Governance

```text
evaluate_governance(request: GovernanceRequest, context: GovernanceContext) -> GovernanceDecision
classify_action_type(action_type: str) -> str
evaluate_target_path(target_path: Path, context: GovernanceContext) -> list[GovernanceEvidence]
apply_governance_rules(request: GovernanceRequest, context: GovernanceContext) -> GovernanceDecision
```

## Risk

```text
evaluate_risk(context: RiskContext) -> RiskAssessment
classify_risk_item(signal: RiskSignal) -> RiskItem
compute_overall_risk(items: list[RiskItem]) -> str
generate_mitigations(items: list[RiskItem]) -> list[RiskMitigation]
```

## Evolution Planner

```text
generate_evolution_plan(context: PlanningContext) -> EvolutionPlan
build_candidate_actions(context: PlanningContext) -> list[CandidateAction]
compute_priority_score(action: CandidateAction, context: PlanningContext) -> PriorityScore
rank_candidate_actions(actions: list[CandidateAction]) -> list[CandidateAction]
```

## Patch Proposal Generator

```text
generate_patch_proposal(context: PatchProposalContext) -> PatchProposal
build_patch_changes(candidate: CandidateAction, context: PatchProposalContext) -> list[PatchChange]
build_validation_plan(proposal: PatchProposal, context: PatchProposalContext) -> PatchValidationPlan
build_rollback_plan(proposal: PatchProposal, context: PatchProposalContext) -> PatchRollbackPlan
```

## Validation Runner

```text
run_validation(context: ValidationContext) -> ValidationReport
validate_allowlist(check: ValidationCheck, allowlist: ValidationAllowlist) -> bool
execute_allowed_check(check: ValidationCheck, command: ValidationCommand) -> ValidationEvidence
build_validation_report(evidence: list[ValidationEvidence]) -> ValidationReport
```

## Memory Store

```text
store_memory(record: MemoryRecord) -> MemoryWriteResult
load_memory(memory_id: str) -> MemoryRecord | None
query_memory(query: MemoryQuery) -> MemoryQueryResult
build_index(records: list[MemoryRecord]) -> MemoryIndex
create_snapshot(records: list[MemoryRecord]) -> MemorySnapshot
```

## Report Writer

```text
build_report(request: ReportRequest, context: ReportContext) -> Report
render_template(report: Report, template: ReportTemplate) -> str
build_report_bundle(report: Report, rendered: str, context: ReportContext) -> ReportBundle
validate_report_sections(report: Report, template: ReportTemplate) -> list[ReportIssue]
```

---

# 56. Shared Helper Contracts

## 56.1 Schema Validation Helper

Required behavior:

```text
loads schema from agentx_initiator/schemas/
validates dictionary objects before latest artifact writes
returns structured PASS/FAIL result
never downgrades schema validation failure to warning
identifies missing required fields and invalid enum values
blocks missing schema files with INVALID_SCHEMA_CONTRACT
```

Expected function:

```text
validate_schema_object(obj: dict, schema_name: str) -> SchemaValidationResult
```

## 56.2 JSONL Append Helper

Required behavior:

```text
creates parent directory under .agentx-init/ when safe
appends exactly one JSON object per call
never rewrites previous lines
never deletes malformed previous lines
serializes with deterministic key ordering when possible
returns structured append result
```

Expected function:

```text
append_jsonl(path: Path, record: dict) -> JsonlAppendResult
```

## 56.3 Atomic Latest Artifact Writer

Required behavior:

```text
build object in memory
validate schema before write
write temporary file under .agentx-init/
replace latest artifact only after validation passes
preserve previous valid latest artifact on validation failure
return artifact path and status
```

Expected function:

```text
write_validated_latest(path: Path, obj: dict, schema_name: str) -> ArtifactWriteResult
```

## 56.4 Source Non-Mutation Guard

Required behavior:

```text
captures file digests outside .agentx-init/ before command workflow when test mode enables it
captures file digests after workflow
fails if any non-.agentx-init source file changed during runtime command
ignores .agentx-init/ runtime artifacts
reports changed paths if violation occurs
```

Expected function:

```text
verify_no_source_mutation(before: dict, after: dict) -> SourceMutationCheckResult
```

---

# 57. Exact CLI Argument Contracts

## `agentx-init explain`

Accepted forms:

```text
agentx-init explain <path>
agentx-init explain --path <path>
```

Required output:

```text
terminal explanation
optional memory record
append audit event
```

Blocked if:

```text
path is missing
path escapes repository boundary
path does not exist
latest scan is missing and command cannot safely derive explanation from scan evidence
```

## `agentx-init plan`

Accepted forms:

```text
agentx-init plan
agentx-init plan --format text|json|markdown
```

Required output:

```text
.agentx-init/snapshots/evolution_plan_latest.json
.agentx-init/reports/latest_plan.md
.agentx-init/memory/evolution_plan_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Blocked if:

```text
architecture_latest.json is missing or invalid
repo_scan_latest.json is missing or invalid
required schemas are missing
```

## `agentx-init propose`

Accepted forms:

```text
agentx-init propose --task "<task>"
agentx-init propose --candidate <candidate_action_id>
```

Required output:

```text
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/reports/latest_patch_proposal.md
.agentx-init/memory/patch_proposal_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Blocked if:

```text
no task or candidate is provided
candidate id is unknown
proposal would require source mutation during PM2
proposal would include executable diff or apply instruction
required governance/risk context cannot be produced
```

## `agentx-init validate`

Accepted forms:

```text
agentx-init validate
agentx-init validate --check <check_id>
agentx-init validate --plan <validation_plan_path_under_agentx_init>
```

Required output:

```text
.agentx-init/snapshots/validation_report_latest.json
.agentx-init/reports/latest_validation.md
.agentx-init/memory/validation_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Blocked if:

```text
requested command is not allowlisted
shell mode would be required
network would be required
mutation would be required
validation plan path is outside .agentx-init/
```

## `agentx-init audit`

Accepted forms:

```text
agentx-init audit
agentx-init audit --limit <integer>
agentx-init audit --event-type <event_type>
```

Required output:

```text
terminal audit summary
optional .agentx-init/reports/latest_audit.md
```

Blocked if:

```text
audit_events.jsonl is missing and no audit trail can be constructed
limit is invalid
```

## `agentx-init memory`

Accepted forms:

```text
agentx-init memory
agentx-init memory --category <category>
agentx-init memory --source-component <component>
agentx-init memory --id <memory_id>
```

Required output:

```text
terminal memory summary
memory_query_result object internally
append audit event if configured
```

Blocked if:

```text
memory store schema is missing
query shape is invalid
memory index cannot be built from records
```

## `agentx-init graph`

Accepted forms:

```text
agentx-init graph
```

PM2 behavior:

```text
return BLOCKED
failure_class = COMMAND_DEFERRED_TO_PRODUCT_MILESTONE_3
exit_code = 3
write command history and audit event when available
write no graph artifacts
```

---

# 58. Golden Fixture and Test Inventory

PM2 must include a fixture repository or generated temporary fixture containing enough evidence for every PM2 component.

Minimum fixture contents:

```text
L0/ or equivalent protected path sample
agentx_initiator/ sample source path
agentx_initiator/schemas/ sample schema files
agentx_initiator/tests/ sample test files
docs/ sample markdown documentation
.agentx-init/ excluded runtime directory
```

Minimum golden workflow test:

```text
1. Run scan.
2. Run status.
3. Run explain against one known file.
4. Run plan.
5. Select first READY candidate.
6. Run propose for that candidate.
7. Run validate with allowlisted checks.
8. Run audit.
9. Run memory.
10. Run graph and confirm PM3 blocked behavior.
11. Confirm no source files outside .agentx-init/ changed.
12. Confirm all latest JSON artifacts validate.
13. Confirm all JSONL histories append.
```

Minimum test files that must exist after PM2:

```text
test_governance_engine.py
test_governance_rules.py
test_governance_schema.py
test_risk_engine.py
test_risk_rules.py
test_risk_schema.py
test_evolution_planner.py
test_planning_rules.py
test_evolution_plan_schema.py
test_patch_proposal_generator.py
test_patch_proposal_rules.py
test_patch_proposal_schema.py
test_validation_runner.py
test_validation_allowlist.py
test_validation_schema.py
test_memory_store.py
test_memory_index.py
test_memory_schema.py
test_cli_explain.py
test_cli_plan.py
test_cli_propose.py
test_cli_validate.py
test_cli_audit.py
test_cli_memory.py
test_cli_graph_blocked.py
test_pm2_golden_workflow.py
```

---

# 59. Final PM2 Completion Checklist

PM2 is complete only when every item below is true.

```text
[ ] PM1 baseline verified before PM2 activation.
[ ] Shared schema validation helper exists and is tested.
[ ] JSONL append helper exists and is tested.
[ ] Atomic latest artifact writer exists and is tested.
[ ] Source non-mutation guard exists and is tested.
[ ] Governance Engine implemented and tested.
[ ] Risk Engine implemented and tested.
[ ] Evolution Planner implemented and tested.
[ ] Patch Proposal Generator implemented and tested.
[ ] Validation Runner implemented and tested.
[ ] Memory Store implemented and tested.
[ ] PM2 report templates implemented and tested.
[ ] explain command active and tested.
[ ] plan command active and tested.
[ ] propose command active and tested.
[ ] validate command active and tested.
[ ] audit command active and tested.
[ ] memory command active and tested.
[ ] graph command remains PM3-blocked and tested.
[ ] All PM2 schemas exist.
[ ] All latest JSON artifacts validate.
[ ] All history JSONL files append rather than rewrite.
[ ] All commands append command history when command history is available.
[ ] All meaningful actions append audit events when audit log is available.
[ ] No source file outside .agentx-init/ is changed by runtime commands.
[ ] Forbidden import scan passes.
[ ] No network access is required.
[ ] No shell execution occurs except through Validation Runner allowlisted wrapper.
[ ] No patch application exists.
[ ] No Git operation exists.
[ ] No graph artifact is generated in PM2.
[ ] pm2_completion_record.json exists.
[ ] Completion packet lists every changed file, schema, test, command, and generated artifact.
```

---

# 60. Final v4 Rating and Freeze Verdict

This v4 document is rated **10/10** as a Product Milestone 2 implementation handoff.

It is now complete enough for an LLM coding agent to implement PM2 using this document alone as the controlling handoff, while using the repository only as current implementation context.

Do not keep revising this PM2 specification unless implementation discovers a concrete blocker that is not resolvable by the existing PM2 component contracts.
