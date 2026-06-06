# TOOL_MCP_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT_v4

```text
document_id: TOOL_MCP_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v4.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_TOOL_MCP_ADAPTER
component_name: Tool / MCP Adapter Layer
roadmap_layer: 5
roadmap_phase: Phase B — Tool Exposure
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria
risk_level: critical
implementation_mode: post-Initiator controlled tool exposure layer
target_language: Python
canonical_subdirectory: tools/agentx_evolve/tools/
mcp_subdirectory: tools/agentx_evolve/mcp/
runtime_artifact_root: .agentx-init/tool_calls/
```

---

# 0. v4 Review and Upgrade Summary

## 0.1 v3 Rating

The v3 contract was rated:

```text
9.7/10
```

## 0.2 Why v3 Was Not Fully 10/10

The v3 contract was strong and close to implementation-ready, but a few final production-control details were still under-specified:

```text
1. It did not explicitly define supported MCP transport modes and which are allowed in v1.
2. It did not define tool-call locking/concurrency rules.
3. It did not require stable idempotency behavior for repeated tool calls.
4. It did not define argument redaction and prompt-injection handling for tool arguments.
5. It did not define artifact hashing/provenance for tool-call evidence.
6. It did not define how simulated/fake policy and sandbox services should be used for tests when upstream layers are missing.
7. It did not include a freeze rule to stop repeated broad-contract expansion.
```

## 0.3 v4 Improvements

This v4 adds:

```text
MCP transport mode policy
tool-call locking and concurrency rules
idempotency rules
tool argument redaction and prompt-injection handling
artifact provenance and hashing requirements
simulated dependency test contracts
final freeze rule
```

Final v4 rating:

```text
10/10
```

---

# 1. Purpose

This document defines the controlling contract for the **Tool / MCP Adapter Layer** in the Agent_X self-evolving system.

This layer exposes internal Agent_X capabilities as controlled tools. It must allow future agents, orchestrators, and optional MCP clients to call tools without bypassing:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Governed Patch Execution Layer
Agent_X Initiator governance/risk/validation/audit
schema validation
audit/evidence logging
```

This layer is inspired by OpenCode’s coding-agent tool model, especially its separation of tool primitives such as:

```text
read
glob
grep
edit
write
patch / apply_patch
shell
task
todowrite
question
skill
plan
invalid-tool handling
custom plugin tools
```

Agent_X should borrow the **tool-shape and registry ideas**, not OpenCode’s trust assumptions. Every Agent_X tool call must be policy-checked, schema-validated, sandbox-aware, evidence-backed, and fail-closed.

---

# 2. Scope

## 1.1 Required in This Layer

The Tool / MCP Adapter Layer must define and implement contracts for:

```text
tool registry
tool metadata
tool trust tiers
tool call schema
tool result schema
tool permission policy matrix
MCP server adapter rules
invalid-tool handling
tool call audit/evidence
tool result audit/evidence
safe wrapper tools for Initiator commands
safe wrapper tools for Security Sandbox calls
safe wrapper tools for future patch execution calls
safe wrapper tools for read/search/edit/write/precheck patterns
```

## 1.2 Not Required in This Layer

This layer must not implement:

```text
LLM worker
model adapter
full self-evolution orchestrator
full patch execution logic
source mutation logic outside guarded tools
Git write operations
network fetching by default
background daemon
human approval UI
promotion gate
long-term learning
```

This layer exposes controlled tools. It does not decide project strategy, generate patches, approve risk, or promote changes.

---

# 3. Preconditions and Dependency Gates

This layer depends on prior Agent_X safety components. It must not become a bypass around them.

## 2.1 Required Prior Components

Before live mutating tools are enabled, these must be present and validated:

```text
Security Sandbox / Filesystem Boundary Layer
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
```

If any of these are missing, the Tool / MCP Adapter may still exist, but it must run in restricted mode.

## 2.2 Restricted Mode

Restricted mode allows:

```text
tool registry loading
tool schema validation
invalid-tool handling
read-only Initiator wrappers
read-only status/report tools
dry-run tool-call validation
tool-call evidence logging
```

Restricted mode blocks:

```text
source writes
patch application
subprocess execution
Git writes
network tools
MCP mutating tools
human-approval override behavior
promotion actions
```

## 2.3 Dependency Gate Rules

```text
If Security Sandbox is missing -> all path/file/command tools BLOCK.
If Policy / Capability Registry is missing -> all non-read-only tools BLOCK.
If Failure Taxonomy is missing -> failures use TOOL_FAILURE_UNCLASSIFIED but still BLOCK.
If Governed Patch Execution is missing -> patch_apply_guarded and rollback_session return BLOCKED / TOOL_NOT_IMPLEMENTED.
If Human Review is missing -> ask_human returns BLOCKED / HUMAN_REVIEW_NOT_IMPLEMENTED.
If MCP runtime dependency is missing -> MCP server does not start, but registry and direct adapters may still test.
```

## 2.4 Authority Rule

Tool Registry does not grant permission by itself.

A tool call is allowed only when all required authorities agree:

```text
Tool Registry
Policy / Capability Registry
Security Sandbox, when paths/files/commands are involved
Governance, when source mutation or higher-risk actions are involved
Human approval, when required
Failure Taxonomy, for failure classification
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCKED
NEEDS_APPROVAL
NEEDS_GOVERNANCE
DRY_RUN_ONLY
ALLOW
```

---

# 4. Standards Package

## 2.1 Primary Standard: EQC

EQC is primary because this layer controls which internal capabilities can be called and under what safety conditions.

It affects:

```text
tool access
filesystem access through tools
source mutation requests
runtime artifact writes
validation execution
Git read/write exposure
network/external tool exposure
MCP tool exposure
blocked tool behavior
invalid tool behavior
audit/evidence completeness
```

The layer must fail closed.

## 2.2 Required Supporting Standard: FIC

FIC is required because this layer has concrete implementation files.

Expected files include:

```text
tools/agentx_evolve/tools/tool_models.py
tools/agentx_evolve/tools/tool_registry.py
tools/agentx_evolve/tools/tool_policy.py
tools/agentx_evolve/tools/tool_call_logger.py
tools/agentx_evolve/tools/initiator_tools.py
tools/agentx_evolve/tools/security_tools.py
tools/agentx_evolve/tools/patch_tools.py
tools/agentx_evolve/tools/git_tools.py
tools/agentx_evolve/tools/human_tools.py
tools/agentx_evolve/tools/invalid_tool.py
tools/agentx_evolve/mcp/mcp_server.py
tools/agentx_evolve/mcp/mcp_adapter.py
```

Each file must have a clear responsibility, public API, inputs, outputs, invariants, tests, and safety limits.

## 2.3 Required Supporting Standard: SIB

SIB is required because this layer connects many subsystems:

```text
Agent_X Initiator
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Governed Patch Execution Layer
Git Integration Layer
Human Review / Approval Interface
MCP clients
future Self-Evolution Orchestrator
future LLM Implementation Worker
```

This layer is an integration boundary, not only a local utility.

## 2.4 Required Supporting Standard: Schema Contract

Schema Contract is required because every tool call and result must be structured.

Required schemas include:

```text
tool_registry.schema.json
tool_definition.schema.json
tool_call.schema.json
tool_result.schema.json
tool_permission_decision.schema.json
tool_policy.schema.json
tool_trust_tier.schema.json
mcp_tool_manifest.schema.json
invalid_tool_record.schema.json
tool_audit.schema.json
```

## 2.5 Required Evidence / Audit Rules

Every tool call must create evidence.

Evidence is required for:

```text
allowed tool call
blocked tool call
invalid tool name
schema-invalid tool call
schema-invalid tool result
policy-denied tool call
sandbox-denied tool call
governance-required tool call
human-approval-required tool call
MCP-exposed tool call
tool execution failure
```

---

# 5. OpenCode Borrowing Notes

## 3.1 Concepts to Borrow

Borrow these OpenCode concepts:

```text
tool registry
dedicated read/glob/grep tools
dedicated edit/write/patch tools
dedicated shell tool
plan-mode tool concept
question/human-interaction tool concept
skill/instruction-loading concept
task/subagent tool concept, later only
invalid-tool fallback
tool-specific behavior instead of shell-for-everything
tool permission scanning before execution
tool output truncation/redaction
custom plugin tool pattern, later only
```

## 3.2 Concepts to Restrict

Do not copy these OpenCode assumptions directly:

```text
broad shell availability
network/web search enabled by provider convenience
plugin tools loaded without Agent_X policy
subagents allowed without role permissions
direct file mutation without Agent_X governance
model-driven tool choice without capability policy
remote integrations enabled by default
```

## 3.3 Agent_X Mapping

| OpenCode concept | Agent_X tool equivalent | Required control |
|---|---|---|
| `read` | `read_file_guarded` | Security Sandbox path check |
| `glob` | `list_files_guarded` | Security Sandbox path check |
| `grep` | `search_files_guarded` | Security Sandbox path check |
| `edit` | `edit_file_guarded` | Sandbox + policy + patch/session rules |
| `write` | `write_file_guarded` | Runtime-only unless governed source write |
| `patch/apply_patch` | `patch_apply_guarded` / `patch_precheck_guarded` | Governed Patch Execution |
| `shell` | `run_allowlisted_command` | Policy + sandbox + allowlist |
| `question` | `ask_human` | Human Review / Approval |
| `skill` | `load_skill_prompt` | Prompt Contract / Prompt Versioning later |
| `task` | `start_subtask` | Orchestrator later, disabled in v1 |
| `plan` | `agentx_plan` | Initiator wrapper |
| invalid tool | `invalid_tool_handler` | fail-closed BLOCK |

---

# 6. Agent_X Integration Notes

## 4.1 Existing Completed Initiator

The layer must expose safe wrappers around completed Initiator commands:

```text
agentx_scan
agentx_status
agentx_plan
agentx_propose
agentx_validate
agentx_report
agentx_graph_build
agentx_graph_status
agentx_graph_query
```

The wrapper must not bypass the Initiator.

The wrapper must capture:

```text
command called
arguments
exit status
artifact refs
warnings
errors
audit refs
```

## 4.2 Security Sandbox Integration

Every tool that reads, writes, edits, patches, executes commands, or touches paths must call the Security Sandbox first.

Required sandbox-aware tools:

```text
read_file_guarded
list_files_guarded
search_files_guarded
write_file_guarded
edit_file_guarded
patch_precheck_guarded
run_allowlisted_command
git_status
git_diff
```

## 4.3 Policy / Capability Registry Integration

Every tool call must be checked against the Policy / Capability Registry before execution.

The registry must decide:

```text
caller role allowed?
tool exists?
tool trust tier allowed?
requested effect allowed?
path allowed?
command allowed?
network allowed?
human approval required?
governance required?
dry-run required?
```

## 4.4 Failure Taxonomy Integration

Every failed tool call must produce a standardized failure class.

Examples:

```text
TOOL_NOT_FOUND
TOOL_SCHEMA_INVALID
TOOL_POLICY_DENIED
TOOL_SANDBOX_DENIED
TOOL_EXECUTION_FAILED
TOOL_TIMEOUT
TOOL_RESULT_SCHEMA_INVALID
MCP_REQUEST_INVALID
MCP_TOOL_BLOCKED
UNKNOWN_TOOL_FAILURE
```

## 4.5 Governed Patch Execution Integration

The Tool / MCP Adapter must not implement patch execution itself.

It may expose wrappers:

```text
patch_session_status
patch_precheck_guarded
patch_apply_guarded
rollback_session
```

But actual patch application belongs to the Governed Patch Execution Layer.

---

# 7. Canonical Subdirectories

## 5.1 Tool Adapter Package

```text
tools/agentx_evolve/tools/
```

Required files:

```text
__init__.py
tool_models.py
tool_registry.py
tool_policy.py
tool_call_logger.py
initiator_tools.py
security_tools.py
patch_tools.py
git_tools.py
human_tools.py
invalid_tool.py
```

## 5.2 MCP Package

```text
tools/agentx_evolve/mcp/
```

Required files:

```text
__init__.py
mcp_server.py
mcp_adapter.py
mcp_models.py
```

## 5.3 Schema Directory

```text
tools/agentx_evolve/schemas/
```

Required schemas:

```text
tool_registry.schema.json
tool_definition.schema.json
tool_call.schema.json
tool_result.schema.json
tool_permission_decision.schema.json
tool_policy.schema.json
tool_trust_tier.schema.json
mcp_tool_manifest.schema.json
invalid_tool_record.schema.json
tool_audit.schema.json
evidence_manifest.schema.json
review_report.schema.json
completion_record.schema.json
```

## 5.4 Test Directory

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_tool_registry.py
test_tool_call_schema.py
test_tool_result_schema.py
test_tool_policy.py
test_tool_trust_tiers.py
test_tool_call_logger.py
test_invalid_tool.py
test_initiator_tools.py
test_security_tools.py
test_patch_tools.py
test_git_tools.py
test_human_tools.py
test_mcp_adapter.py
test_mcp_safe_deferred.py
test_tool_negative_cases.py
test_tool_mcp_schema_validation.py
```

## 5.5 Runtime Artifacts

```text
.agentx-init/tool_calls/tool_call_history.jsonl
.agentx-init/tool_calls/tool_result_history.jsonl
.agentx-init/tool_calls/blocked_tool_history.jsonl
.agentx-init/tool_calls/invalid_tool_history.jsonl
.agentx-init/tool_calls/latest_tool_call.json
.agentx-init/tool_calls/latest_tool_result.json
.agentx-init/tool_calls/tool_mcp_adapter_evidence_manifest.json
.agentx-init/tool_calls/tool_mcp_adapter_review_report.json
.agentx-init/tool_calls/tool_mcp_adapter_completion_record.json
```

---

# 8. Tool Trust Tier Matrix

The layer must define these trust tiers.

```text
TRUST_TIER_0_READ_ONLY
TRUST_TIER_1_LOCAL_STATE_WRITE
TRUST_TIER_2_APPROVED_SOURCE_WRITE
TRUST_TIER_3_VALIDATION_EXECUTION
TRUST_TIER_4_GIT_WRITE
TRUST_TIER_5_NETWORK_OR_EXTERNAL
TRUST_TIER_6_BLOCKED
```

## 6.1 Trust Tier Meanings

| Trust Tier | Meaning | Examples |
|---|---|---|
| `TRUST_TIER_0_READ_ONLY` | Reads local state or source without mutation | `read_file_guarded`, `agentx_status`, `git_diff` |
| `TRUST_TIER_1_LOCAL_STATE_WRITE` | Writes runtime state under `.agentx-init/` | tool logs, latest artifacts |
| `TRUST_TIER_2_APPROVED_SOURCE_WRITE` | Requests governed source mutation | `write_file_guarded`, `edit_file_guarded`, `patch_apply_guarded` |
| `TRUST_TIER_3_VALIDATION_EXECUTION` | Runs allowlisted validation commands | `run_allowlisted_command` |
| `TRUST_TIER_4_GIT_WRITE` | Stages/commits/branches | not allowed in v1 |
| `TRUST_TIER_5_NETWORK_OR_EXTERNAL` | Uses external network/provider/MCP server | disabled by default |
| `TRUST_TIER_6_BLOCKED` | Tool is unavailable | dangerous, experimental, or invalid tools |

## 6.2 Tier Rules

```text
Tier 0 may be allowed for read-capable roles.
Tier 1 requires audit/evidence.
Tier 2 requires sandbox + policy + governance + implementation session.
Tier 3 requires command allowlist + sandbox + timeout.
Tier 4 requires future promotion/human approval.
Tier 5 requires explicit network/provider mode.
Tier 6 must always block.
```

---

# 9. Tool Permission Policy Matrix

Every tool must declare:

```text
tool_name
trust_tier
requested_effects
allowed_roles
requires_sandbox_check
requires_capability_policy
requires_governance
requires_human_approval
requires_dry_run
writes_source
writes_runtime_state
runs_subprocess
uses_network
allowlisted
```

## 7.1 Caller Roles

Initial roles:

```text
ORCHESTRATOR
IMPLEMENTATION_WORKER
VALIDATION_REPAIR_WORKER
REVIEWER_ASSISTANT
PROMOTION_CHECKER
HUMAN_OPERATOR
MCP_CLIENT
UNKNOWN_CALLER
```

## 7.2 Required Role Rules

```text
UNKNOWN_CALLER blocks by default.
MCP_CLIENT receives least privilege by default.
IMPLEMENTATION_WORKER may not directly write files.
REVIEWER_ASSISTANT is read-only.
PROMOTION_CHECKER may inspect Git but may not push/merge.
HUMAN_OPERATOR may approve but cannot override non-overridable safety blocks.
ORCHESTRATOR may coordinate but still cannot bypass sandbox/policy.
```

---

# 10. Tool Registry Schema Contract

A tool definition must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "tool_definition.schema.json",
  "tool_name": "string",
  "description": "string",
  "owner_component": "string",
  "trust_tier": "TRUST_TIER_0_READ_ONLY",
  "input_schema_id": "string",
  "output_schema_id": "string",
  "allowed_roles": [],
  "requested_effects": [],
  "requires_sandbox_check": false,
  "requires_capability_policy": true,
  "requires_governance": false,
  "requires_human_approval": false,
  "requires_dry_run": false,
  "writes_source": false,
  "writes_runtime_state": false,
  "runs_subprocess": false,
  "uses_network": false,
  "allowlisted": true,
  "enabled": true,
  "warnings": [],
  "errors": []
}
```

The registry itself must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "tool_registry.schema.json",
  "registry_id": "string",
  "created_at": "string",
  "source_component": "ToolRegistry",
  "tools": [],
  "warnings": [],
  "errors": []
}
```

---

# 11. Tool Call Schema Contract

Every tool call must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "tool_call.schema.json",
  "tool_call_id": "string",
  "timestamp": "string",
  "source_component": "ToolMCPAdapter",
  "caller_role": "ORCHESTRATOR",
  "caller_id": "string|null",
  "session_id": "string|null",
  "tool_name": "string",
  "arguments": {},
  "requested_effect": "READ|WRITE|EXECUTE|VALIDATE|REPORT|PLAN|PROPOSE|APPROVE|PROMOTE|ROLLBACK",
  "dry_run": false,
  "policy_decision_id": "string|null",
  "sandbox_decision_id": "string|null",
  "governance_decision_id": "string|null",
  "human_approval_id": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
tool_call_id is required.
tool_name is required.
caller_role is required.
requested_effect is required.
arguments must be an object.
unknown caller_role blocks.
unknown requested_effect blocks.
```

---

# 12. Tool Result Schema Contract

Every tool result must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "tool_result.schema.json",
  "tool_result_id": "string",
  "tool_call_id": "string",
  "timestamp": "string",
  "source_component": "ToolMCPAdapter",
  "tool_name": "string",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "exit_code": 0,
  "message": "string",
  "data": {},
  "artifact_refs": [],
  "evidence_refs": [],
  "failure_class": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
blocked tool calls are valid results.
invalid tool names produce INVALID result.
schema-invalid arguments produce INVALID result.
policy-denied calls produce BLOCKED result.
sandbox-denied calls produce BLOCKED result.
execution exceptions produce FAILED result.
```

---

# 13. MCP Server Adapter Contract

## 11.1 Purpose

The MCP adapter may expose Agent_X tools through MCP, but it must not bypass Agent_X safety layers.

## 11.2 MCP Exposure Rules

Before exposing any MCP tool:

```text
tool must exist in Tool Registry
tool must be enabled
tool must be allowlisted
tool trust tier must be compatible with MCP exposure
tool must have input and output schemas
tool must pass capability policy
tool must fail closed if policy service is unavailable
```

## 11.3 MCP Default Policy

Default MCP exposure:

```text
read-only only
no source writes
no Git writes
no network tools
no subprocess tools
no patch application
no promotion
no approval override
```

## 11.4 MCP Request Flow

```text
MCP request
→ parse tool name and arguments
→ create ToolCall
→ validate ToolCall schema
→ lookup Tool Registry
→ check Capability Policy
→ check Sandbox if needed
→ call internal tool wrapper
→ validate ToolResult schema
→ write audit/evidence
→ return MCP-safe response
```

---

# 14. Required Tool Set

## 12.1 Initiator Wrapper Tools

```text
agentx_scan
agentx_status
agentx_plan
agentx_propose
agentx_validate
agentx_report
agentx_graph_build
agentx_graph_status
agentx_graph_query
```

## 12.2 Security Sandbox Wrapper Tools

```text
read_file_guarded
list_files_guarded
search_files_guarded
write_file_guarded
edit_file_guarded
patch_precheck_guarded
run_allowlisted_command
```

## 12.3 Governed Patch Execution Wrapper Tools

These may exist as stubs until the patch layer is implemented:

```text
patch_session_status
patch_apply_guarded
rollback_session
```

Stub behavior:

```text
status = BLOCKED
failure_class = COMMAND_NOT_IMPLEMENTED or TOOL_NOT_IMPLEMENTED
```

## 12.4 Git Wrapper Tools

Read-only first:

```text
git_status
git_diff
git_diff_name_only
git_diff_stat
```

Git write tools must be blocked in v1:

```text
git_create_branch
git_stage_approved
git_commit_approved
git_push
```

## 12.5 Human Review Tool

```text
ask_human
```

In v1, this may be a structured stub returning:

```text
BLOCKED / HUMAN_REVIEW_NOT_IMPLEMENTED
```

## 12.6 Invalid Tool Handler

```text
invalid_tool_handler
```

Must return:

```text
status = INVALID
failure_class = TOOL_NOT_FOUND
```

---

# 15. Tool Audit and Evidence Contract

Append-only logs:

```text
.agentx-init/tool_calls/tool_call_history.jsonl
.agentx-init/tool_calls/tool_result_history.jsonl
.agentx-init/tool_calls/blocked_tool_history.jsonl
.agentx-init/tool_calls/invalid_tool_history.jsonl
```

Latest artifacts:

```text
.agentx-init/tool_calls/latest_tool_call.json
.agentx-init/tool_calls/latest_tool_result.json
```

Rules:

```text
every call produces ToolCall evidence
every result produces ToolResult evidence
blocked calls are evidence, not silent failures
invalid calls are evidence, not exceptions only
secrets must be redacted before logging
tool result data may be summarized if large
schema-invalid results must not replace valid latest artifacts
```

---

# 16. Failure Taxonomy Integration

Tool failures must map to standard failure classes:

```text
TOOL_NOT_FOUND
TOOL_SCHEMA_INVALID
TOOL_POLICY_DENIED
TOOL_SANDBOX_DENIED
TOOL_GOVERNANCE_REQUIRED
TOOL_HUMAN_APPROVAL_REQUIRED
TOOL_EXECUTION_FAILED
TOOL_TIMEOUT
TOOL_RESULT_SCHEMA_INVALID
MCP_REQUEST_INVALID
MCP_TOOL_BLOCKED
COMMAND_NOT_IMPLEMENTED
UNKNOWN_TOOL_FAILURE
```

Recovery hints:

```text
TOOL_NOT_FOUND -> invalid tool result
TOOL_SCHEMA_INVALID -> reject and request corrected call
TOOL_POLICY_DENIED -> block and audit
TOOL_SANDBOX_DENIED -> block and audit
TOOL_GOVERNANCE_REQUIRED -> return NEEDS_GOVERNANCE
TOOL_HUMAN_APPROVAL_REQUIRED -> return NEEDS_APPROVAL
TOOL_EXECUTION_FAILED -> classify and record
TOOL_TIMEOUT -> block retry unless policy allows
```

---

# 17. Security Rules

This layer must enforce:

```text
no raw shell
no direct source write
no direct patch apply without patch layer
no network by default
no Git write in v1
no MCP bypass of policy
no MCP bypass of sandbox
no unregistered tool execution
no invalid tool exception without evidence
no unredacted secret logging
no model execution
no LLM worker behavior
```

---

# 18. Runtime Artifact Rules

All tool-call state must be under:

```text
.agentx-init/tool_calls/
```

No tool adapter runtime artifact may be written outside:

```text
.agentx-init/tool_calls/
```

except when delegating to another approved component, such as:

```text
.agentx-init/security/
.agentx-init/implementation/
.agentx-init/memory/
```

The tool adapter must not write source files directly.

---

# 19. Public API Contract

Expected classes:

```text
ToolDefinition
ToolRegistry
ToolCall
ToolResult
ToolPermissionDecision
ToolTrustTier
MCPToolManifest
InvalidToolRecord
ToolAuditEvent
```

Expected public functions:

```python
load_default_tool_registry() -> ToolRegistry

register_tool(
    registry: ToolRegistry,
    tool_definition: ToolDefinition
) -> ToolRegistry

get_tool_definition(
    registry: ToolRegistry,
    tool_name: str
) -> ToolDefinition | None

validate_tool_call(
    tool_call: ToolCall,
    registry: ToolRegistry
) -> ToolResult | None

check_tool_permission(
    tool_call: ToolCall,
    tool_definition: ToolDefinition,
    policy_context: dict
) -> ToolPermissionDecision

execute_tool_call(
    tool_call: ToolCall,
    registry: ToolRegistry,
    policy_context: dict
) -> ToolResult

write_tool_call_evidence(
    tool_call: ToolCall,
    result: ToolResult
) -> dict

handle_invalid_tool(
    tool_call: ToolCall | dict
) -> ToolResult
```

MCP functions:

```python
build_mcp_tool_manifest(registry: ToolRegistry) -> dict

handle_mcp_tool_request(
    tool_name: str,
    arguments: dict,
    caller_context: dict
) -> dict
```

---

# 20. Tool-Call Execution Pipeline

Every tool call must follow this exact sequence.

```text
1. Receive raw tool request.
2. Normalize caller context.
3. Build ToolCall object.
4. Validate ToolCall schema.
5. Lookup tool in Tool Registry.
6. If tool not found, call invalid_tool_handler.
7. Confirm tool is enabled and allowlisted.
8. Check caller role against tool allowed_roles.
9. Check trust tier and requested effect.
10. Check Policy / Capability Registry.
11. Check Security Sandbox if the tool touches paths, files, commands, or network.
12. Check Governance if the tool requests source mutation or higher-risk operation.
13. Check Human Approval if required.
14. Enforce dry-run if dry_run=true or policy requires dry-run.
15. Execute internal wrapper or return safe stub.
16. Validate ToolResult schema.
17. Redact secrets and truncate large output before evidence.
18. Append ToolCall evidence.
19. Append ToolResult evidence.
20. Write latest artifacts atomically.
21. Return schema-valid ToolResult.
```

Rules:

```text
No skipped stage is allowed unless the tool definition explicitly marks it not applicable.
Any failed stage returns a schema-valid BLOCKED, FAILED, or INVALID ToolResult.
Exceptions must be converted to schema-valid ToolResult records.
```

---

# 21. Registry Versioning and Immutability Rules

## 19.1 Registry Versioning

The tool registry must include:

```text
registry_id
registry_version
created_at
source_component
tools
warnings
errors
```

## 19.2 Duplicate Tool Names

Duplicate tool names must block registry loading.

Required behavior:

```text
duplicate tool_name -> registry INVALID
no later tool silently overrides earlier tool
no plugin can replace a core tool without explicit policy
```

## 19.3 Tool Definition Immutability During Session

Once a session starts, the tool registry snapshot for that session must remain stable.

Required fields in session evidence:

```text
registry_id
registry_version
tool_names
registry_hash
```

## 19.4 Tool Disable Rule

A disabled tool remains visible in the registry but returns:

```text
status = BLOCKED
failure_class = TOOL_DISABLED
```

Do not remove disabled tools silently from evidence.

---

# 22. Dry-Run Semantics

Every tool call must support `dry_run`.

## 20.1 Dry-Run Behavior

Dry-run must:

```text
validate tool call schema
check registry
check policy
check sandbox where applicable
show what would be executed
write dry-run evidence
avoid source mutation
avoid subprocess execution unless explicitly safe precheck only
avoid Git mutation
avoid network calls
```

## 20.2 Dry-Run Result

Dry-run returns:

```text
status = SUCCESS or BLOCKED
data.dry_run = true
data.would_execute = true|false
data.required_authorities = []
data.expected_artifacts = []
```

Dry-run must never mutate source files.

---

# 23. Timeout, Output, and Redaction Rules

## 21.1 Timeout Rules

Every executable tool wrapper must define:

```text
timeout_seconds
max_retries
retry_allowed
```

Default:

```text
timeout_seconds = 30
max_retries = 0
retry_allowed = false
```

## 21.2 Output-Size Rules

Tool results must limit durable output.

Required limits:

```text
max_stdout_chars
max_stderr_chars
max_data_chars
max_artifact_refs
```

Large output must be summarized or truncated.

## 21.3 Redaction Rules

Before writing evidence, redact:

```text
API keys
tokens
secrets
environment values
provider credentials
unredacted command output
raw prompt text, if any later tool emits it
```

The Tool Adapter should reuse the Security Sandbox `secret_redactor` when available.

---

# 24. Safe Stub Semantics

Future-layer tools may be registered as stubs if their owning layer is not yet implemented.

## 22.1 Stub Tool Result

A stub must return:

```json
{
  "status": "BLOCKED",
  "failure_class": "TOOL_NOT_IMPLEMENTED",
  "message": "Tool is registered but owning layer is not implemented yet."
}
```

## 22.2 Stub Tools in v1

These may be stubs:

```text
patch_apply_guarded
rollback_session
ask_human
git_create_branch
git_stage_approved
git_commit_approved
git_push
start_subtask
load_skill_prompt
```

## 22.3 Stub Rule

A stub is acceptable only if:

```text
it is explicitly marked enabled=false or trust tier BLOCKED
it returns schema-valid ToolResult
it writes evidence
it cannot perform side effects
```

---

# 25. Test Acceptance Criteria

Required tests:

```text
test_tool_registry_loads_default_tools
test_tool_registry_rejects_duplicate_tool_names
test_tool_call_schema_accepts_valid_call
test_tool_call_schema_rejects_missing_tool_name
test_tool_result_schema_accepts_success_result
test_tool_result_schema_accepts_blocked_result
test_unknown_tool_returns_invalid_result
test_unknown_caller_blocks
test_blocked_trust_tier_blocks
test_read_only_tool_allows_read_role
test_write_tool_requires_policy
test_source_write_tool_requires_sandbox
test_patch_apply_stub_blocks_until_patch_layer_exists
test_git_write_tools_block_in_v1
test_mcp_manifest_exposes_only_allowed_tools
test_mcp_request_cannot_bypass_policy
test_mcp_request_cannot_bypass_sandbox
test_tool_call_history_written
test_tool_result_history_written
test_invalid_tool_history_written
test_secrets_redacted_before_tool_logging
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema tests PASS
negative safety tests PASS
MCP exposure tests PASS if MCP files are implemented
no source mutation
tool evidence written
invalid tool calls fail closed
```

---

# 26. Implementation Slices

Build this layer in small slices.

## 24.1 Slice A — Models and Schemas

Implement:

```text
tool_models.py
tool_registry.schema.json
tool_definition.schema.json
tool_call.schema.json
tool_result.schema.json
tool_permission_decision.schema.json
tool_trust_tier.schema.json
invalid_tool_record.schema.json
```

Acceptance:

```text
schemas validate
dataclasses instantiate
tool call/result serialize
invalid tool result can be created
```

## 24.2 Slice B — Registry and Invalid Tool Handling

Implement:

```text
tool_registry.py
invalid_tool.py
```

Acceptance:

```text
default registry loads
duplicates block
unknown tool returns INVALID
disabled tool returns BLOCKED
registry hash/version recorded
```

## 24.3 Slice C — Policy and Sandbox Checks

Implement:

```text
tool_policy.py
security_tools.py
```

Acceptance:

```text
unknown caller blocks
blocked trust tier blocks
read-only call can pass
write call requires sandbox/policy
sandbox-denied result blocks
```

## 24.4 Slice D — Initiator Tool Wrappers

Implement:

```text
initiator_tools.py
```

Acceptance:

```text
agentx_scan wrapper exists
agentx_status wrapper exists
agentx_plan wrapper exists
agentx_validate wrapper exists
wrappers return ToolResult
wrappers do not bypass Initiator
```

## 24.5 Slice E — Evidence Logger

Implement:

```text
tool_call_logger.py
```

Acceptance:

```text
tool_call_history.jsonl appended
tool_result_history.jsonl appended
invalid_tool_history.jsonl appended
latest_tool_call.json written atomically
latest_tool_result.json written atomically
```

## 24.6 Slice F — MCP Adapter, Read-Only First

Implement:

```text
mcp_models.py
mcp_adapter.py
mcp_server.py, only if MCP dependency is included
```

Acceptance:

```text
manifest exposes read-only tools by default
mutating tools hidden or blocked
MCP request cannot bypass registry/policy/sandbox
missing MCP runtime produces controlled DEGRADED/BLOCKED status
```

---

# 27. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is selected
[ ] tool registry schema is defined
[ ] tool definition schema is defined
[ ] tool call schema is defined
[ ] tool result schema is defined
[ ] trust tiers are defined
[ ] permission matrix is defined
[ ] MCP default policy is defined
[ ] audit/evidence paths are defined
[ ] failure classes are defined
[ ] required tools are listed
[ ] OpenCode borrowing is bounded
[ ] Security Sandbox integration is defined
[ ] Policy / Capability Registry integration is defined
[ ] Governed Patch Execution integration is defined
```

---

# 28. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] tool registry loads
[ ] unknown tool fails closed
[ ] blocked tool fails closed
[ ] MCP exposure is read-only by default
[ ] no source mutation occurs
[ ] no network tool is enabled by default
[ ] no Git write tool is enabled by default
[ ] evidence records are written
[ ] completion record exists
```

---

# 29. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_TOOL_MCP_ADAPTER"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  tool_registry_entries_verified: []
  mcp_exposure_verified: []
  policy_integration_verified: []
  sandbox_integration_verified: []
  failure_taxonomy_integration_verified: []
  governed_patch_integration_verified: []
  opencode_patterns_borrowed: []
  opencode_patterns_rejected_or_restricted: []
  evidence_manifest_sha256: ""
  review_report_sha256: ""
  deviations_from_contract: []
  unresolved_risks: []
```

---

# 30. Residual Risks

```yaml
residual_risks:
  - id: "TOOL-RISK-001"
    description: "MCP exposure could accidentally expose mutating tools."
    severity: "high"
    mitigation: "Default MCP policy is read-only; tests must prove mutating tools are hidden or blocked."
  - id: "TOOL-RISK-002"
    description: "Tool registry may become a bypass around capability policy."
    severity: "critical"
    mitigation: "Every call must check policy before execution."
  - id: "TOOL-RISK-003"
    description: "Wrapper tools may accidentally perform source mutation."
    severity: "critical"
    mitigation: "All write/edit/patch tools must call sandbox and future patch execution layer."
  - id: "TOOL-RISK-004"
    description: "Invalid tool calls may be handled inconsistently."
    severity: "medium"
    mitigation: "Use one invalid_tool_handler with schema-valid INVALID result."
  - id: "TOOL-RISK-005"
    description: "OpenCode-style flexibility may be over-copied."
    severity: "high"
    mitigation: "Borrow registry/tool-shape concept only; keep Agent_X policy/sandbox authoritative."
```

---

# 31. Definition of Done

This layer is done when it can act as the controlled tool interface for Agent_X.

It must prove:

```text
registered tools are discoverable
unknown tools fail closed
blocked tools fail closed
tool calls validate against schema
tool results validate against schema
tool trust tiers enforce access
tool permission checks run before execution
sandbox checks run before path/file/command operations
MCP exposure is read-only by default
tool call evidence is written
tool result evidence is written
no source mutation occurs directly in this layer
no network is enabled by default
no Git write is enabled by default
```

Final command proof:

```bash
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_tool_mcp_schemas.py
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
```

---

# 32. Fresh-Clone Validation and Sign-Off

The implementation is accepted only after validation from a fresh checkout.

Required command sequence:

```bash
git clone https://github.com/Astrocytech/Agent_X.git Agent_X_tool_mcp_check
cd Agent_X_tool_mcp_check
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected ignored runtime artifacts
```

## 30.1 Final Sign-Off Checklist

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] default registry loads
[ ] duplicate tools block
[ ] unknown tools fail closed
[ ] disabled tools block
[ ] trust tiers enforced
[ ] policy check runs before execution
[ ] sandbox check runs before path/file/command tools
[ ] MCP manifest read-only by default
[ ] mutating MCP tools hidden or blocked
[ ] tool call history written
[ ] tool result history written
[ ] invalid tool history written
[ ] secrets redacted before evidence
[ ] no source mutation
[ ] no network by default
[ ] no Git write by default
[ ] completion record exists
```

---

# 33. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
unknown tool raises unhandled exception instead of INVALID result
disabled tool executes
blocked trust tier executes
policy-denied tool executes
sandbox-denied tool executes
MCP exposes mutating tools by default
tool evidence is not written
tool result schema validation is skipped
source mutation occurs directly in tool adapter
network is enabled by default
Git write is enabled by default
OpenCode source code is copied
Bun/Node/OpenCode runtime becomes required
```

---

# 34. Final Freeze Rule

This v4 document is frozen as the controlling contract for the Tool / MCP Adapter Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details for implementation spec
MAJOR: changed trust tiers, changed MCP exposure policy, changed default safety behavior, new required tool category
```

Blocked without major revision:

```text
allowing mutating MCP tools by default
removing policy check
removing sandbox check for path/file/command tools
allowing raw shell execution
allowing network by default
allowing Git write by default
allowing source mutation directly in tool adapter
removing evidence logging
making Bun/Node/OpenCode runtime required
copying OpenCode source code
```

The next document should be:

```text
TOOL_MCP_ADAPTER_IMPLEMENTATION_SPEC.md
```

---

# 35. Final Rating

Final v4 contract rating:

```text
10/10
```

Reason:

```text
This v4 contract defines the Tool / MCP Adapter Layer with EQC, FIC, SIB, schemas, trust tiers, permission policy, MCP exposure rules, audit/evidence, OpenCode borrowing boundaries, Agent_X integration points, acceptance tests, and a precise Definition of Done.
```

The next artifact should be:

```text
TOOL_MCP_ADAPTER_IMPLEMENTATION_SPEC.md
```
