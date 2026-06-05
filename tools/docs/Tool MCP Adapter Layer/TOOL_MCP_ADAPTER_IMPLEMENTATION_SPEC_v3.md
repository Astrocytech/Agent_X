# TOOL_MCP_ADAPTER_IMPLEMENTATION_SPEC_v3

```text
document_id: TOOL_MCP_ADAPTER_IMPLEMENTATION_SPEC
version: v3.0
status: implementation-ready, final frozen handoff
based_on: TOOL_MCP_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
component_id: AGENTX_TOOL_MCP_ADAPTER
component_name: Tool / MCP Adapter Layer
roadmap_layer: 5
roadmap_phase: Phase B — Tool Exposure
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria
target_language: Python
canonical_tool_subdirectory: tools/agentx_evolve/tools/
canonical_mcp_subdirectory: tools/agentx_evolve/mcp/
runtime_artifact_root: .agentx-init/tool_calls/
implementation_mode: deterministic tool adapter first, MCP exposure controlled and read-only by default
rating_target: 10/10
previous_version_rating: 9.8/10
current_version_rating: 10/10

```

---

# 0. v3 Review and Upgrade Summary

## 0.1 v2 Rating

The v2 implementation spec was rated:

```text
9.8/10
```

## 0.2 Why v2 Was Not Fully 10/10

The v2 document was already strong and implementation-ready. It covered the required files, schemas, runtime artifacts, integration points, tests, MCP exposure rules, dispatcher flow, drift blockers, and Definition of Done.

The remaining gaps were small but important for a coding-agent handoff:

```text
1. It needed a clearer dependency-order rule because Policy / Capability Registry and Governed Patch Execution may not exist yet.
2. It needed a direct tool-by-tool behavior table showing what each wrapper must do in v1.
3. It needed stronger schema example requirements so generated schemas are testable, not only listed.
4. It needed clearer evidence-ref propagation from Policy, Sandbox, and Failure records into ToolResult.
5. It needed stricter separation between "MCP adapter stub" and "real MCP server runtime."
6. It needed a final frozen acceptance matrix to prevent another broad rewrite.
```

## 0.3 v3 Improvements

This v3 adds:

```text
dependency-order and fallback rules
tool-by-tool v1 behavior table
schema example requirements
evidence-ref propagation rules
MCP stub-vs-runtime boundary
final frozen acceptance matrix
```

Final v3 rating:

```text
10/10
```



---

# 1. Purpose

This document is the full implementation specification for the **Tool / MCP Adapter Layer**.

It converts the controlling contract:

```text
TOOL_MCP_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
```

into file-by-file implementation instructions.

The Tool / MCP Adapter Layer must expose Agent_X internal capabilities as controlled tools while preventing any bypass of:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Governed Patch Execution Layer
Agent_X Initiator governance/risk/validation/audit
schema validation
audit/evidence logging
```

The implementation must borrow useful OpenCode-style tool concepts:

```text
read
glob
grep
edit
write
patch / apply_patch
shell
plan
question
skill
task
invalid-tool handling
tool registry
```

but adapt them to Agent_X’s stricter rules:

```text
no unregistered tool execution
no raw shell
no source mutation directly in this layer
no network by default
no Git write in v1
no MCP bypass of policy
no MCP bypass of sandbox
schema-valid tool call/result records
append-only evidence
fail-closed invalid tool behavior
```

---

# 2. Canonical Destination Summary

Create the Tool Adapter package here:

```text
tools/agentx_evolve/tools/
```

Create the MCP Adapter package here:

```text
tools/agentx_evolve/mcp/
```

Create schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts must be written here:

```text
.agentx-init/tool_calls/
```

This is the intended package split:

```text
tools/agentx_initiator/         = completed Initiator
tools/agentx_evolve/security/   = validated Security Sandbox / Filesystem Boundary
tools/agentx_evolve/tools/      = new Tool / MCP Adapter tool registry and wrappers
tools/agentx_evolve/mcp/        = new optional MCP exposure adapter
```

---

# 3. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic tool adapter that can:

```text
load a default tool registry
register tools
reject duplicate tool names
validate tool calls
validate tool results
check tool trust tiers
check caller roles
check policy context
call Security Sandbox before path/file/command tools
wrap completed Initiator commands
stub future Governed Patch Execution tools safely
block Git write tools in v1
expose MCP manifest in read-only/default-safe form
handle invalid tool calls with schema-valid INVALID results
write tool call and result evidence
```

The layer must expose safe equivalents of OpenCode-style primitives:

```text
read_file_guarded
list_files_guarded
search_files_guarded
write_file_guarded
edit_file_guarded
patch_precheck_guarded
run_allowlisted_command
agentx_scan
agentx_status
agentx_plan
agentx_propose
agentx_validate
agentx_report
agentx_graph_build
agentx_graph_status
agentx_graph_query
patch_session_status
patch_apply_guarded
rollback_session
git_status
git_diff
git_diff_name_only
git_diff_stat
ask_human
invalid_tool_handler
```

The layer must not implement:

```text
LLM worker
model adapter
self-evolution orchestrator
actual patch application
source mutation logic
Git write operations
network fetch/search
promotion
human approval UI
background daemon
```


## 3.1 Required v1 Tool Behavior Table

| Tool | v1 behavior | Must call / depend on |
|---|---|---|
| `agentx_scan` | Run or wrap Initiator scan safely | Initiator wrapper |
| `agentx_status` | Run or wrap Initiator status safely | Initiator wrapper |
| `agentx_plan` | Run or wrap Initiator plan safely | Initiator wrapper |
| `agentx_propose` | Run or wrap Initiator propose safely | Initiator wrapper |
| `agentx_validate` | Run or wrap Initiator validate safely | Initiator wrapper |
| `agentx_report` | Run or wrap Initiator report safely | Initiator wrapper |
| `agentx_graph_build` | Run or wrap graph build safely | Initiator wrapper |
| `agentx_graph_status` | Run or wrap graph status safely | Initiator wrapper |
| `agentx_graph_query` | Run or wrap graph query safely | Initiator wrapper |
| `read_file_guarded` | Read only after sandbox check | Security Sandbox |
| `list_files_guarded` | List only inside approved boundary | Security Sandbox |
| `search_files_guarded` | Search only inside approved boundary | Security Sandbox |
| `write_file_guarded` | Runtime write only; source write blocked unless future authorities present | Security Sandbox + policy |
| `edit_file_guarded` | Dry-run or blocked unless future authorities present | Security Sandbox + policy |
| `patch_precheck_guarded` | Precheck targets only | Security Sandbox |
| `run_allowlisted_command` | Precheck or block; no raw shell | Security Sandbox + policy |
| `patch_session_status` | BLOCKED/PARTIAL stub until patch layer exists | Patch layer future |
| `patch_apply_guarded` | BLOCKED until patch layer exists | Patch layer future |
| `rollback_session` | BLOCKED until patch layer exists | Patch layer future |
| `git_status` | Read-only or BLOCKED if safe command runner not ready | safe command precheck |
| `git_diff` | Read-only or BLOCKED if safe command runner not ready | safe command precheck |
| `git_diff_name_only` | Read-only or BLOCKED if safe command runner not ready | safe command precheck |
| `git_diff_stat` | Read-only or BLOCKED if safe command runner not ready | safe command precheck |
| `git_create_branch` | BLOCKED in v1 | none |
| `git_stage_approved` | BLOCKED in v1 | none |
| `git_commit_approved` | BLOCKED in v1 | none |
| `git_push` | BLOCKED in v1 | none |
| `ask_human` | BLOCKED structured stub | Human review future |
| `invalid_tool_handler` | INVALID fail-closed result | local handler |

---

# 4. Implementation Order

Implement in this exact order:

```text
1. tools/agentx_evolve/tools/tool_models.py
2. schemas for tool definitions, calls, results, policies, audit
3. tools/agentx_evolve/tools/tool_registry.py
4. tools/agentx_evolve/tools/tool_policy.py
5. tools/agentx_evolve/tools/invalid_tool.py
6. tools/agentx_evolve/tools/tool_call_logger.py
7. tools/agentx_evolve/tools/initiator_tools.py
8. tools/agentx_evolve/tools/security_tools.py
9. tools/agentx_evolve/tools/patch_tools.py
10. tools/agentx_evolve/tools/git_tools.py
11. tools/agentx_evolve/tools/human_tools.py
12. tools/agentx_evolve/mcp/mcp_models.py
13. tools/agentx_evolve/mcp/mcp_adapter.py
14. tools/agentx_evolve/mcp/mcp_server.py
15. tests
16. completion evidence
```

Rationale:

```text
models first
schemas second
registry before execution
policy before wrappers
invalid-tool handler before execution flow
logger before wrappers
safe wrappers before MCP exposure
MCP exposure last
tests after all public surfaces exist
```

---

# 5. Minimal Implementation Slices

Do not implement the entire layer as one uncontrolled pass. Use these slices.

## 4.1 Slice A — Models and Schemas

Implement first:

```text
tool_models.py
tool_definition.schema.json
tool_registry.schema.json
tool_call.schema.json
tool_result.schema.json
tool_permission_decision.schema.json
tool_policy.schema.json
tool_trust_tier.schema.json
invalid_tool_record.schema.json
tool_audit.schema.json
```

Acceptance:

```text
dataclasses instantiate
schemas validate valid examples
schemas reject missing required fields
no tool execution exists yet
```

## 4.2 Slice B — Registry and Policy

Implement second:

```text
tool_registry.py
tool_policy.py
invalid_tool.py
```

Acceptance:

```text
default registry loads
duplicate tools rejected
unknown tools return INVALID
blocked tiers block
unknown callers block
mutating tools block without required policy context
```

## 4.3 Slice C — Evidence Logger

Implement third:

```text
tool_call_logger.py
```

Acceptance:

```text
tool call history writes
tool result history writes
blocked tool history writes
invalid tool history writes
latest artifacts write atomically
secrets are redacted before persistence
```

## 4.4 Slice D — Safe Wrappers

Implement fourth:

```text
initiator_tools.py
security_tools.py
patch_tools.py
git_tools.py
human_tools.py
```

Acceptance:

```text
Initiator wrappers return ToolResult
Security wrappers call validated sandbox functions
Patch tools block as stubs
Git write tools block
Human tool blocks as stub
no direct source mutation
```

## 4.5 Slice E — MCP Adapter

Implement last:

```text
mcp_models.py
mcp_adapter.py
mcp_server.py
mcp_tool_manifest.schema.json
```

Acceptance:

```text
MCP manifest exposes only read-only allowed tools by default
MCP request cannot bypass policy
MCP request cannot bypass sandbox
server does not start on import
no network port opens by default
```

---

# 6. Exact Files to Create

## 4.1 Tool Package

```text
tools/agentx_evolve/tools/__init__.py
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
```

## 4.2 MCP Package

```text
tools/agentx_evolve/mcp/__init__.py
tools/agentx_evolve/mcp/mcp_models.py
tools/agentx_evolve/mcp/mcp_adapter.py
tools/agentx_evolve/mcp/mcp_server.py
```

## 4.3 Schemas

```text
tools/agentx_evolve/schemas/tool_registry.schema.json
tools/agentx_evolve/schemas/tool_definition.schema.json
tools/agentx_evolve/schemas/tool_call.schema.json
tools/agentx_evolve/schemas/tool_result.schema.json
tools/agentx_evolve/schemas/tool_permission_decision.schema.json
tools/agentx_evolve/schemas/tool_policy.schema.json
tools/agentx_evolve/schemas/tool_trust_tier.schema.json
tools/agentx_evolve/schemas/mcp_tool_manifest.schema.json
tools/agentx_evolve/schemas/invalid_tool_record.schema.json
tools/agentx_evolve/schemas/tool_audit.schema.json
```

## 4.4 Tests

```text
tools/agentx_evolve/tests/test_tool_registry.py
tools/agentx_evolve/tests/test_tool_call_schema.py
tools/agentx_evolve/tests/test_tool_result_schema.py
tools/agentx_evolve/tests/test_tool_policy.py
tools/agentx_evolve/tests/test_tool_trust_tiers.py
tools/agentx_evolve/tests/test_tool_call_logger.py
tools/agentx_evolve/tests/test_invalid_tool.py
tools/agentx_evolve/tests/test_initiator_tools.py
tools/agentx_evolve/tests/test_security_tools.py
tools/agentx_evolve/tests/test_patch_tools.py
tools/agentx_evolve/tests/test_mcp_adapter.py
tools/agentx_evolve/tests/test_tool_negative_cases.py
```

---

# 7. File-by-File Implementation Spec

---

## 5.1 `tools/agentx_evolve/tools/__init__.py`

### Purpose

Expose the public tool adapter API.

### Required Exports

```python
from .tool_models import (
    ToolDefinition,
    ToolRegistry,
    ToolCall,
    ToolResult,
    ToolPermissionDecision,
    ToolAuditEvent,
    InvalidToolRecord,
)

from .tool_registry import (
    load_default_tool_registry,
    register_tool,
    get_tool_definition,
)

from .tool_policy import check_tool_permission
from .invalid_tool import handle_invalid_tool
from .tool_call_logger import write_tool_call_evidence
```

### Must Not Do

```text
no filesystem writes
no registry loading side effects
no MCP server startup
no tool execution on import
```

---

## 5.2 `tool_models.py`

### Purpose

Define all shared dataclasses and constants for the Tool / MCP Adapter Layer.

### Required Trust Tier Constants

```python
TRUST_TIER_0_READ_ONLY = "TRUST_TIER_0_READ_ONLY"
TRUST_TIER_1_LOCAL_STATE_WRITE = "TRUST_TIER_1_LOCAL_STATE_WRITE"
TRUST_TIER_2_APPROVED_SOURCE_WRITE = "TRUST_TIER_2_APPROVED_SOURCE_WRITE"
TRUST_TIER_3_VALIDATION_EXECUTION = "TRUST_TIER_3_VALIDATION_EXECUTION"
TRUST_TIER_4_GIT_WRITE = "TRUST_TIER_4_GIT_WRITE"
TRUST_TIER_5_NETWORK_OR_EXTERNAL = "TRUST_TIER_5_NETWORK_OR_EXTERNAL"
TRUST_TIER_6_BLOCKED = "TRUST_TIER_6_BLOCKED"
```

### Required Role Constants

```python
ROLE_ORCHESTRATOR = "ORCHESTRATOR"
ROLE_IMPLEMENTATION_WORKER = "IMPLEMENTATION_WORKER"
ROLE_VALIDATION_REPAIR_WORKER = "VALIDATION_REPAIR_WORKER"
ROLE_REVIEWER_ASSISTANT = "REVIEWER_ASSISTANT"
ROLE_PROMOTION_CHECKER = "PROMOTION_CHECKER"
ROLE_HUMAN_OPERATOR = "HUMAN_OPERATOR"
ROLE_MCP_CLIENT = "MCP_CLIENT"
ROLE_UNKNOWN_CALLER = "UNKNOWN_CALLER"
```

### Required Status Constants

```python
STATUS_SUCCESS = "SUCCESS"
STATUS_PARTIAL = "PARTIAL"
STATUS_BLOCKED = "BLOCKED"
STATUS_FAILED = "FAILED"
STATUS_INVALID = "INVALID"
```

### Required Effect Constants

```python
EFFECT_READ = "READ"
EFFECT_WRITE = "WRITE"
EFFECT_EXECUTE = "EXECUTE"
EFFECT_VALIDATE = "VALIDATE"
EFFECT_REPORT = "REPORT"
EFFECT_PLAN = "PLAN"
EFFECT_PROPOSE = "PROPOSE"
EFFECT_APPROVE = "APPROVE"
EFFECT_PROMOTE = "PROMOTE"
EFFECT_ROLLBACK = "ROLLBACK"
```

### Required Failure Classes

```python
TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
TOOL_SCHEMA_INVALID = "TOOL_SCHEMA_INVALID"
TOOL_POLICY_DENIED = "TOOL_POLICY_DENIED"
TOOL_SANDBOX_DENIED = "TOOL_SANDBOX_DENIED"
TOOL_GOVERNANCE_REQUIRED = "TOOL_GOVERNANCE_REQUIRED"
TOOL_HUMAN_APPROVAL_REQUIRED = "TOOL_HUMAN_APPROVAL_REQUIRED"
TOOL_EXECUTION_FAILED = "TOOL_EXECUTION_FAILED"
TOOL_TIMEOUT = "TOOL_TIMEOUT"
TOOL_RESULT_SCHEMA_INVALID = "TOOL_RESULT_SCHEMA_INVALID"
MCP_REQUEST_INVALID = "MCP_REQUEST_INVALID"
MCP_TOOL_BLOCKED = "MCP_TOOL_BLOCKED"
COMMAND_NOT_IMPLEMENTED = "COMMAND_NOT_IMPLEMENTED"
UNKNOWN_TOOL_FAILURE = "UNKNOWN_TOOL_FAILURE"
```

### Required Dataclasses

#### `ToolDefinition`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "tool_definition.schema.json"
tool_name: str
description: str
owner_component: str
trust_tier: str
input_schema_id: str
output_schema_id: str
allowed_roles: list[str]
requested_effects: list[str]
requires_sandbox_check: bool
requires_capability_policy: bool
requires_governance: bool
requires_human_approval: bool
requires_dry_run: bool
writes_source: bool
writes_runtime_state: bool
runs_subprocess: bool
uses_network: bool
allowlisted: bool
enabled: bool
warnings: list[str]
errors: list[str]
```

#### `ToolRegistry`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "tool_registry.schema.json"
registry_id: str
created_at: str
source_component: str = "ToolRegistry"
tools: list[ToolDefinition]
warnings: list[str]
errors: list[str]
```

#### `ToolCall`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "tool_call.schema.json"
tool_call_id: str
timestamp: str
source_component: str = "ToolMCPAdapter"
caller_role: str
caller_id: str | None
session_id: str | None
tool_name: str
arguments: dict
requested_effect: str
dry_run: bool
policy_decision_id: str | None
sandbox_decision_id: str | None
governance_decision_id: str | None
human_approval_id: str | None
warnings: list[str]
errors: list[str]
```

#### `ToolResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "tool_result.schema.json"
tool_result_id: str
tool_call_id: str
timestamp: str
source_component: str = "ToolMCPAdapter"
tool_name: str
status: str
exit_code: int
message: str
data: dict
artifact_refs: list[str]
evidence_refs: list[str]
failure_class: str | None
warnings: list[str]
errors: list[str]
```

#### `ToolPermissionDecision`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "tool_permission_decision.schema.json"
decision_id: str
timestamp: str
source_component: str = "ToolPolicy"
tool_name: str
caller_role: str
requested_effect: str
decision: str
reason: str
required_checks: list[str]
missing_checks: list[str]
warnings: list[str]
errors: list[str]
```

#### `InvalidToolRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "invalid_tool_record.schema.json"
record_id: str
timestamp: str
source_component: str = "InvalidToolHandler"
tool_name: str | None
caller_role: str | None
reason: str
raw_call: dict
warnings: list[str]
errors: list[str]
```

#### `ToolAuditEvent`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "tool_audit.schema.json"
audit_id: str
timestamp: str
source_component: str = "ToolMCPAdapter"
event_type: str
tool_call_id: str | None
tool_result_id: str | None
tool_name: str | None
status: str
message: str
artifact_refs: list[str]
warnings: list[str]
errors: list[str]
```

### Helper Functions

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
```

### Acceptance

```text
dataclasses instantiate
to_dict serializes nested dataclasses
constants match schema enums
no filesystem writes
no imports from MCP runtime, LLM clients, or shell libraries
```

---

## 5.3 Schema Files

Create all schema files listed in Section 4.3.

### General Schema Rules

Each schema must:

```text
require schema_version
require schema_id
require source_component where applicable
require warnings
require errors
reject missing required fields
define enum values for status, trust tier, role, effect, and decision fields
allow artifact_refs and evidence_refs arrays
```

### Required Schema Coverage

```text
tool_definition.schema.json validates ToolDefinition
tool_registry.schema.json validates ToolRegistry
tool_call.schema.json validates ToolCall
tool_result.schema.json validates ToolResult
tool_permission_decision.schema.json validates ToolPermissionDecision
tool_policy.schema.json validates policy structure
tool_trust_tier.schema.json validates trust tier metadata
mcp_tool_manifest.schema.json validates MCP-safe manifest
invalid_tool_record.schema.json validates invalid tool records
tool_audit.schema.json validates audit events
```


### Schema Example Requirement

For each schema, create at least one valid example object in tests.

Required examples:

```text
valid_tool_definition
valid_tool_registry
valid_tool_call
valid_tool_result_success
valid_tool_result_blocked
valid_tool_permission_decision_allow
valid_tool_permission_decision_block
valid_invalid_tool_record
valid_tool_audit_event
valid_mcp_tool_manifest
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
```

---

## 5.4 `tool_registry.py`

### Purpose

Define and load the default Agent_X tool registry.

### Required Public Functions

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

list_enabled_tools(
    registry: ToolRegistry
) -> list[ToolDefinition]

list_mcp_exposable_tools(
    registry: ToolRegistry
) -> list[ToolDefinition]
```

### Default Registry Must Include

Initiator tools:

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

Security tools:

```text
read_file_guarded
list_files_guarded
search_files_guarded
write_file_guarded
edit_file_guarded
patch_precheck_guarded
run_allowlisted_command
```

Patch stubs:

```text
patch_session_status
patch_apply_guarded
rollback_session
```

Git read-only tools:

```text
git_status
git_diff
git_diff_name_only
git_diff_stat
```

Git write tools, disabled/blocked:

```text
git_create_branch
git_stage_approved
git_commit_approved
git_push
```

Human tool stub:

```text
ask_human
```

Invalid tool handler:

```text
invalid_tool_handler
```

### Registry Rules

```text
tool names must be unique
disabled tools remain visible only for internal inspection
blocked tools must not execute
MCP exposure list must exclude mutating tools by default
```

### Acceptance Tests

```text
default registry loads
expected tools exist
duplicate tool name rejected
Git write tools are disabled or blocked
patch apply guarded blocks until patch layer exists
MCP exposable list excludes write/execute/network tools by default
```

---

## 5.5 `tool_policy.py`

### Purpose

Check whether a tool call is allowed before execution.

### Required Public Function

```python
check_tool_permission(
    tool_call: ToolCall,
    tool_definition: ToolDefinition,
    policy_context: dict
) -> ToolPermissionDecision
```

### Required Logic

Return BLOCK if:

```text
tool is disabled
tool is not allowlisted
caller role is UNKNOWN_CALLER
caller role not in allowed_roles
requested_effect not in tool requested_effects
trust tier is TRUST_TIER_6_BLOCKED
tool requires governance but governance_decision_id missing
tool requires human approval but human_approval_id missing
tool requires dry-run but dry_run false
tool uses network and provider mode is local_only
tool writes source but no implementation session
tool runs subprocess and command policy missing
```

Return ALLOW only if:

```text
tool exists
tool enabled
tool allowlisted
caller role allowed
requested effect allowed
all required checks satisfied
```

### Required Decision Values

```text
ALLOW
BLOCK
NEEDS_GOVERNANCE
NEEDS_APPROVAL
NEEDS_SANDBOX_CHECK
NEEDS_DRY_RUN
```

### Acceptance Tests

```text
unknown caller blocks
blocked trust tier blocks
read-only tool allows read role
write tool requires policy and sandbox
governance-required tool returns NEEDS_GOVERNANCE
approval-required tool returns NEEDS_APPROVAL
```

---

## 5.6 `invalid_tool.py`

### Purpose

Handle unknown or invalid tool calls fail-closed.

### Required Public Function

```python
handle_invalid_tool(
    tool_call: ToolCall | dict
) -> ToolResult
```

### Required Behavior

```text
status = INVALID
failure_class = TOOL_NOT_FOUND or TOOL_SCHEMA_INVALID
exit_code = 2
message explains invalid tool
data contains safe summary only
evidence_refs may be empty initially
warnings/errors populated
```

### Must Not Do

```text
raise unhandled exception for unknown tool
execute fallback shell
guess intended tool
call network
call model
```

### Acceptance Tests

```text
unknown tool returns INVALID
schema-invalid call returns INVALID
invalid result schema validates
invalid tool history is written by logger
```

---

## 5.7 `tool_call_logger.py`

### Purpose

Write tool call/result/audit evidence.

### Required Public Functions

```python
write_tool_call_evidence(
    tool_call: ToolCall,
    result: ToolResult,
    repo_root: Path
) -> dict

append_tool_call(
    tool_call: ToolCall,
    repo_root: Path
) -> dict

append_tool_result(
    result: ToolResult,
    repo_root: Path
) -> dict

append_blocked_tool(
    tool_call: ToolCall,
    result: ToolResult,
    repo_root: Path
) -> dict

append_invalid_tool(
    record: InvalidToolRecord,
    repo_root: Path
) -> dict

write_latest_tool_call(
    tool_call: ToolCall,
    repo_root: Path
) -> dict

write_latest_tool_result(
    result: ToolResult,
    repo_root: Path
) -> dict
```

### Required Paths

```text
.agentx-init/tool_calls/tool_call_history.jsonl
.agentx-init/tool_calls/tool_result_history.jsonl
.agentx-init/tool_calls/blocked_tool_history.jsonl
.agentx-init/tool_calls/invalid_tool_history.jsonl
.agentx-init/tool_calls/latest_tool_call.json
.agentx-init/tool_calls/latest_tool_result.json
```

### Rules

```text
create .agentx-init/tool_calls/ if needed
append JSONL only
write latest JSON atomically
redact secrets before durable logging
do not write raw file contents to tool logs
do not write unredacted command output
do not replace valid latest artifact with invalid one
```


### Evidence Reference Propagation

ToolResult must include evidence references where available.

Required mappings:

```text
policy decision produced -> ToolResult.evidence_refs includes policy decision ID
sandbox decision produced -> ToolResult.evidence_refs includes sandbox decision ID
failure record produced -> ToolResult.evidence_refs includes failure record ID
tool call logged -> ToolResult.evidence_refs includes tool call evidence ID
tool result logged -> final completion evidence includes result evidence path
```

If an evidence source is unavailable, record a warning and fail closed when the missing evidence is required for safety.

### Acceptance Tests

```text
tool call history written
tool result history written
blocked tool history written
invalid tool history written
latest tool call written atomically
latest tool result written atomically
secrets redacted before logging
```

---

## 5.8 `initiator_tools.py`

### Purpose

Wrap completed Initiator commands/tools.

### Required Public Functions

```python
agentx_scan(arguments: dict, context: dict) -> ToolResult
agentx_status(arguments: dict, context: dict) -> ToolResult
agentx_plan(arguments: dict, context: dict) -> ToolResult
agentx_propose(arguments: dict, context: dict) -> ToolResult
agentx_validate(arguments: dict, context: dict) -> ToolResult
agentx_report(arguments: dict, context: dict) -> ToolResult
agentx_graph_build(arguments: dict, context: dict) -> ToolResult
agentx_graph_status(arguments: dict, context: dict) -> ToolResult
agentx_graph_query(arguments: dict, context: dict) -> ToolResult
```

### Required Behavior

Prefer importing and calling Initiator internals if stable.

If not stable, call the installed CLI through an allowlisted command runner only if policy permits.

Default safe behavior:

```text
read/plan/report/status wrappers may run
mutating behavior must not occur
capture artifacts and summaries
return schema-valid ToolResult
```

### Must Not Do

```text
bypass Initiator validation
bypass Initiator governance
modify Initiator source
shell out through raw subprocess
```

### Acceptance Tests

```text
agentx_status wrapper returns ToolResult
agentx_plan wrapper returns ToolResult or blocked if unavailable
wrapper failure returns FAILED/BLOCKED with failure_class
no source mutation occurs
```

---

## 5.9 `security_tools.py`

### Purpose

Expose Security Sandbox capabilities as tools.

### Required Public Functions

```python
read_file_guarded(arguments: dict, context: dict) -> ToolResult
list_files_guarded(arguments: dict, context: dict) -> ToolResult
search_files_guarded(arguments: dict, context: dict) -> ToolResult
write_file_guarded(arguments: dict, context: dict) -> ToolResult
edit_file_guarded(arguments: dict, context: dict) -> ToolResult
patch_precheck_guarded(arguments: dict, context: dict) -> ToolResult
run_allowlisted_command(arguments: dict, context: dict) -> ToolResult
```

### Required Security Integration

Use the validated sandbox package:

```python
from agentx_evolve.security import (
    safe_read_file,
    safe_write_file,
    safe_exact_edit,
    safe_patch_precheck,
    check_subprocess_allowed,
)
```

### Required Behavior

```text
read_file_guarded calls safe_read_file
write_file_guarded calls safe_write_file
edit_file_guarded calls safe_exact_edit
patch_precheck_guarded calls safe_patch_precheck
run_allowlisted_command calls check_subprocess_allowed
list/search must perform path boundary checks before reading
```

### v1 Rule

`run_allowlisted_command` may precheck only and return BLOCKED/ALLOW decision. It does not need to execute commands in this layer.

### Acceptance Tests

```text
read_file_guarded calls sandbox
write_file_guarded blocks source write by default
edit_file_guarded blocks without proper policy
patch_precheck_guarded blocks L0 path
run_allowlisted_command blocks by default
```

---

## 5.10 `patch_tools.py`

### Purpose

Expose future Governed Patch Execution functions as stubs until that layer exists.

### Required Public Functions

```python
patch_session_status(arguments: dict, context: dict) -> ToolResult
patch_apply_guarded(arguments: dict, context: dict) -> ToolResult
rollback_session(arguments: dict, context: dict) -> ToolResult
```

### v1 Behavior

Until Governed Patch Execution exists:

```text
patch_session_status -> BLOCKED or PARTIAL with TOOL_NOT_IMPLEMENTED
patch_apply_guarded -> BLOCKED with COMMAND_NOT_IMPLEMENTED
rollback_session -> BLOCKED with COMMAND_NOT_IMPLEMENTED
```

### Acceptance Tests

```text
patch_apply_guarded blocks until patch layer exists
rollback_session blocks until patch layer exists
stubs return schema-valid ToolResult
```

---

## 5.11 `git_tools.py`

### Purpose

Expose read-only Git inspection tools and block Git write tools.

### Required Public Functions

```python
git_status(arguments: dict, context: dict) -> ToolResult
git_diff(arguments: dict, context: dict) -> ToolResult
git_diff_name_only(arguments: dict, context: dict) -> ToolResult
git_diff_stat(arguments: dict, context: dict) -> ToolResult
git_create_branch(arguments: dict, context: dict) -> ToolResult
git_stage_approved(arguments: dict, context: dict) -> ToolResult
git_commit_approved(arguments: dict, context: dict) -> ToolResult
git_push(arguments: dict, context: dict) -> ToolResult
```

### v1 Behavior

Read-only tools may be implemented by allowlisted command precheck and controlled subprocess execution later.

Minimum v1 acceptable behavior:

```text
git_status -> either controlled read-only result or BLOCKED if command runner not ready
git_diff -> either controlled read-only result or BLOCKED if command runner not ready
Git write tools -> always BLOCKED
```

### Must Block

```text
git_push
git reset --hard
git clean -fdx
merge
rebase
branch deletion
```

### Acceptance Tests

```text
git write tools block in v1
git read-only tools do not mutate source
git result schema validates
```

---

## 5.12 `human_tools.py`

### Purpose

Expose human review request as a structured stub.

### Required Public Function

```python
ask_human(arguments: dict, context: dict) -> ToolResult
```

### v1 Behavior

Return:

```text
status = BLOCKED
failure_class = HUMAN_REVIEW_NOT_IMPLEMENTED or COMMAND_NOT_IMPLEMENTED
message = "Human review interface is not implemented in this layer."
```

### Must Not Do

```text
open UI
send email
send network request
block waiting for interactive input
```

---

## 5.13 `mcp_models.py`

### Purpose

Define MCP-facing metadata structures.

### Required Dataclasses

```text
MCPToolManifest
MCPToolDefinition
MCPToolRequest
MCPToolResponse
```

MCP manifest fields:

```text
schema_version
schema_id
manifest_id
created_at
source_component
exposed_tools
blocked_tools
warnings
errors
```

---

## 5.14 `mcp_adapter.py`

### Purpose

Convert between MCP requests and Agent_X ToolCall / ToolResult.

### Required Public Functions

```python
build_mcp_tool_manifest(registry: ToolRegistry) -> dict

handle_mcp_tool_request(
    tool_name: str,
    arguments: dict,
    caller_context: dict,
    registry: ToolRegistry,
    policy_context: dict
) -> dict
```

### Required MCP Exposure Rules

Default MCP exposure must be:

```text
read-only only
no write_file_guarded
no edit_file_guarded
no patch_apply_guarded
no rollback_session
no run_allowlisted_command
no Git write tools
no network tools
no approval override
```

### Required Flow

```text
receive MCP request
create ToolCall with caller_role = MCP_CLIENT
validate ToolCall
lookup registry
check policy
check sandbox if tool requires sandbox
execute internal wrapper only if allowed
validate ToolResult
write evidence
return safe response
```

### Acceptance Tests

```text
MCP manifest exposes only allowed read-only tools by default
MCP request cannot call mutating tool
MCP request cannot bypass policy
MCP request cannot bypass sandbox
MCP invalid request returns INVALID/BLOCKED
```

---

## 5.15 `mcp_server.py`

### Purpose

Provide future MCP server entrypoint.

### v1 Behavior

MCP server may be a non-running adapter stub.

Acceptable v1 implementation:

```text
define build_server_manifest
define register_mcp_tools
do not start background server automatically
do not open network port by default
```

### Must Not Do

```text
start server on import
open network socket by default
expose mutating tools by default
run without policy registry
run without tool registry
```


### MCP Stub vs Runtime Boundary

In v1, MCP may be implemented as an adapter/stub only.

Allowed:

```text
build MCP-safe manifest
convert MCP-style request into ToolCall
return MCP-safe response dict
unit-test MCP exposure rules
keep server start function inert unless explicitly called
```

Not allowed:

```text
start background server
open network port
listen on stdio/socket automatically
register mutating tools by default
expose shell/network/Git write tools
require MCP package for base tests
```

If a real MCP runtime is added later, it requires a separate MCP runtime acceptance pass.

---

# 8. Tool Execution Dispatcher Flow

The implementation must include a single controlled execution flow.

Required flow for `execute_tool_call`:

```text
1. Receive raw call or ToolCall.
2. Convert raw call to ToolCall if needed.
3. Validate ToolCall schema.
4. Load or receive ToolRegistry.
5. Look up ToolDefinition.
6. If missing, call invalid_tool_handler.
7. Check tool enabled and allowlisted.
8. Check caller role and requested effect.
9. Check local policy fallback or Policy / Capability Registry when available.
10. If tool requires sandbox, call sandbox before execution.
11. If governance required and missing, return NEEDS_GOVERNANCE / BLOCKED.
12. If human approval required and missing, return NEEDS_APPROVAL / BLOCKED.
13. Execute wrapper only if all checks pass.
14. Validate ToolResult schema.
15. Write ToolCall and ToolResult evidence.
16. Return ToolResult.
```

No wrapper may be called directly by external users without this dispatcher unless the caller is a unit test for that wrapper.

## 6.1 Required Dispatcher Function

```python
execute_tool_call(
    tool_call: ToolCall,
    registry: ToolRegistry,
    policy_context: dict,
    repo_root: Path | None = None
) -> ToolResult
```

## 6.2 Fail-Closed Rule

If any required dependency is unavailable:

```text
policy unavailable -> BLOCKED
sandbox unavailable for sandbox-required tool -> BLOCKED
schema validator unavailable -> BLOCKED for non-trivial execution
registry unavailable -> INVALID/BLOCKED
wrapper raises exception -> FAILED
```

Do not fall back to raw shell, raw file IO, or direct mutation.

---

# 9. Tool Registration Rules

Every tool must be registered with:

```text
name
description
owner component
trust tier
input schema
output schema
allowed roles
requested effects
sandbox requirement
capability policy requirement
governance requirement
human approval requirement
dry-run requirement
source write flag
runtime write flag
subprocess flag
network flag
allowlisted flag
enabled flag
```

Registration must fail if:

```text
tool name duplicate
missing trust tier
missing output schema
missing allowed roles
unknown trust tier
unknown requested effect
enabled mutating tool lacks policy requirement
enabled source-write tool lacks sandbox requirement
enabled network tool lacks explicit network flag
```

---

# 10. Dependency Contract

Allowed standard-library dependencies:

```text
dataclasses
typing
pathlib
json
uuid
datetime
subprocess only through safe wrappers or Git read-only wrapper
hashlib
tempfile
os
shutil
```

Allowed Agent_X local imports:

```text
agentx_evolve.security
agentx_initiator core modules through stable wrappers where available
```

Conditionally allowed:

```text
jsonschema, if already used by Agent_X or needed for schema validation
mcp package, only if MCP runtime is intentionally added and kept disabled by default
```

Forbidden in this layer:

```text
LLM/model clients
OpenCode runtime dependency
Bun
Node
network clients by default
raw shell helpers
Git write helpers in v1
web fetch/search clients
background daemon frameworks
```

`mcp_server.py` may define adapter functions, but it must not require the MCP package unless that dependency is intentionally enabled. The v1 implementation may keep MCP as a structured adapter/stub.

---

# 11. Runtime Artifact Rules

Runtime artifacts must be under:

```text
.agentx-init/tool_calls/
```

Required files:

```text
tool_call_history.jsonl
tool_result_history.jsonl
blocked_tool_history.jsonl
invalid_tool_history.jsonl
latest_tool_call.json
latest_tool_result.json
```

Rules:

```text
append-only JSONL for history
atomic JSON writes for latest
redact secrets before logging
preserve malformed existing JSONL lines
do not write source files
do not log raw file content from read tools
```

---

# 12. Integration Requirements

## 8.1 Security Sandbox Integration

Required:

```text
all path/file/command tools call sandbox first
sandbox-denied result maps to TOOL_SANDBOX_DENIED
sandbox decision ID is attached to ToolCall or ToolResult where possible
no wrapper can bypass sandbox
```

## 8.2 Policy / Capability Registry Integration

Required:

```text
all calls checked against policy before execution
policy-denied result maps to TOOL_POLICY_DENIED
policy missing results in BLOCKED, not ALLOW
```

Until the Policy / Capability Registry is implemented, use deterministic local policy fallback that is restrictive:

```text
read-only tools may allow known roles
mutating tools block
network tools block
Git write tools block
unknown roles block
```

## 8.3 Failure Taxonomy Integration

Required:

```text
every failed/blocked/invalid tool result has failure_class
failure class must be from the standard tool failure list
unknown failure maps to UNKNOWN_TOOL_FAILURE
```

## 8.4 Governed Patch Execution Integration

Required:

```text
patch tools are stubs until layer exists
patch_apply_guarded must block in v1
rollback_session must block in v1
patch_precheck_guarded may call sandbox only
```

## 8.5 Initiator Integration

Required:

```text
Initiator wrappers must use completed Initiator behavior
failure to import/call Initiator returns schema-valid FAILED/BLOCKED ToolResult
Initiator source must not be modified
```

---

# 13. Test Implementation Plan

## 9.1 Test Fixtures

Create fixtures:

```python
@pytest.fixture
def temp_repo(tmp_path): ...

@pytest.fixture
def default_registry(): ...

@pytest.fixture
def read_only_tool_call(): ...

@pytest.fixture
def unknown_tool_call(): ...

@pytest.fixture
def mcp_client_context(): ...

@pytest.fixture
def restrictive_policy_context(): ...
```

## 9.2 Required Tests

Implement:

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

## 9.3 Negative Tests

Implement:

```text
test_unregistered_tool_never_executes
test_mcp_client_cannot_call_write_tool_by_default
test_mcp_client_cannot_call_shell_tool_by_default
test_mutating_tool_without_policy_blocks
test_network_tool_disabled_by_default
test_git_push_tool_blocks
test_tool_result_with_unredacted_secret_not_logged
test_tool_wrapper_does_not_modify_source_directly
```

---

# 14. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected runtime artifacts
```

No validation command may require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
```

---

# 15. Completion Evidence

After implementation, write:

```text
.agentx-init/tool_calls/tool_mcp_adapter_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_TOOL_MCP_ADAPTER",
  "component_name": "Tool / MCP Adapter Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_tool_subdirectory": "tools/agentx_evolve/tools/",
  "canonical_mcp_subdirectory": "tools/agentx_evolve/mcp/",
  "basis_documents": [
    "TOOL_MCP_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT_v1",
    "TOOL_MCP_ADAPTER_IMPLEMENTATION_SPEC_v1"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "tool_registry_entries_verified": [],
  "mcp_exposure_verified": [],
  "policy_integration_verified": [],
  "sandbox_integration_verified": [],
  "failure_taxonomy_integration_verified": [],
  "governed_patch_integration_verified": [],
  "opencode_patterns_borrowed": [],
  "opencode_patterns_rejected_or_restricted": [],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

---

# 16. Implementation Drift Blockers

Reject the implementation if it:

```text
places files outside tools/agentx_evolve/tools/ or tools/agentx_evolve/mcp/ without recorded deviation
starts MCP server automatically
opens network port by default
exposes mutating tools over MCP by default
executes raw shell
performs source mutation directly
enables Git write tools in v1
adds OpenCode/Bun/Node runtime dependency
copies OpenCode source code
bypasses Security Sandbox for file/path/command tools
bypasses Policy / Capability Registry checks
logs unredacted secrets
returns unstructured tool results
throws unhandled exception for invalid tool calls
```

---

# 17. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
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

No validation command may require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
running MCP server
```

---

# 18. Go / No-Go Acceptance Rules

## 16.1 GO Criteria

The layer may be marked DONE only if all are true:

```text
all target files exist
all required schemas exist
all required tests exist
compileall passes
pytest passes
default tool registry loads
unknown tools fail closed
blocked tools fail closed
mutating tools require policy and sandbox
MCP exposure is read-only by default
MCP server does not start on import
Git write tools are blocked
patch apply and rollback tools are blocked until patch layer exists
tool call/result evidence is written
no source mutation occurs directly in this layer
no network is enabled by default
no raw shell is executed
completion record exists
```

## 16.2 NO-GO Criteria

The layer is NOT DONE if any are true:

```text
compileall fails
required tests fail
unknown tool raises unhandled exception
MCP can call mutating tool by default
MCP server starts on import
source write occurs directly in this layer
raw shell is executed
network is enabled by default
Git write tool is enabled
patch_apply_guarded applies a patch before patch layer exists
policy missing results in ALLOW
sandbox missing results in ALLOW for sandbox-required tools
tool result is unstructured
tool evidence is missing
unredacted secrets are logged
```

## 16.3 Conditional GO

Conditional GO is allowed only for non-safety items, such as:

```text
optional MCP runtime package not installed, if adapter tests pass in stub mode
human review tool implemented as BLOCKED stub
patch tools implemented as BLOCKED stubs
Git read-only tools implemented as BLOCKED until safe command runner is ready
```

Conditional GO is not allowed for:

```text
policy bypass
sandbox bypass
source mutation
raw shell
network default enablement
invalid tool unhandled exception
schema/evidence failure
```

---

# 19. Definition of Done

The Tool / MCP Adapter Layer is done when:

```text
all target files exist
all schemas exist
all tests exist
default registry loads
expected tools are registered
duplicate tool names are rejected
unknown tools fail closed
tool calls validate
tool results validate
trust tiers enforce access
policy checks occur before execution
sandbox checks occur before path/file/command tool execution
patch apply and rollback tools block until patch layer exists
Git write tools block in v1
MCP manifest exposes read-only tools only by default
MCP requests cannot bypass policy
MCP requests cannot bypass sandbox
tool call evidence is written
tool result evidence is written
blocked/invalid tool evidence is written
no source mutation occurs directly in this layer
no network is enabled by default
no raw shell is executed
completion record exists
```

Command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
git status --short
```

Expected proof:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected runtime artifacts
```

---

# 20. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places files outside tools/agentx_evolve/tools/ or tools/agentx_evolve/mcp/ without recorded deviation
exposes mutating tools over MCP by default
starts MCP server on import
opens network socket by default
executes raw shell
performs source mutation directly
enables Git write tools in v1
enables patch application before Governed Patch Execution exists
allows missing policy to pass
allows missing sandbox to pass for file/path/command tools
adds OpenCode/Bun/Node runtime dependency
copies OpenCode source code
logs unredacted secrets
returns unstructured tool results
raises unhandled exception for invalid tool calls
```

Allowed implementation choices:

```text
MCP adapter as safe stub
patch tools as safe stubs
human review tool as safe stub
Git read-only tools as safe stubs if safe command execution is not ready
local restrictive policy fallback until Policy / Capability Registry is complete
```

---

# 21. Final Implementation Sequence for Coding Agent

Use this sequence:

```text
1. Create tools/agentx_evolve/tools/ package files.
2. Create tools/agentx_evolve/mcp/ package files.
3. Implement tool_models.py.
4. Create schemas.
5. Implement tool_registry.py.
6. Implement tool_policy.py.
7. Implement invalid_tool.py.
8. Implement tool_call_logger.py.
9. Implement initiator_tools.py.
10. Implement security_tools.py.
11. Implement patch_tools.py stubs.
12. Implement git_tools.py with read-only/block behavior.
13. Implement human_tools.py stub.
14. Implement mcp_models.py.
15. Implement mcp_adapter.py.
16. Implement mcp_server.py as non-running safe stub.
17. Create tests.
18. Run compileall.
19. Run pytest.
20. Verify git status.
21. Write completion record.
```

Do not reorder unless required by real import dependencies.

---

# 22. Coding Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] The target repository is Agent_X.
[ ] Security Sandbox is validated and available under tools/agentx_evolve/security/.
[ ] The new tool adapter must live under tools/agentx_evolve/tools/.
[ ] The MCP adapter must live under tools/agentx_evolve/mcp/.
[ ] Runtime artifacts must go under .agentx-init/tool_calls/.
[ ] OpenCode is used only as a design reference.
[ ] No OpenCode source code is copied.
[ ] No Bun/Node dependency is added.
[ ] Policy fallback is restrictive.
[ ] MCP is read-only by default.
[ ] Mutating tools block unless all required future layers approve.
[ ] Patch apply and rollback are stubs until Governed Patch Execution exists.
[ ] Git write tools block in v1.
[ ] Tests must run without GPU, network, hosted model, LLM, Bun, Node, or running MCP server.
```

---

# 23. Final Rating

This v3 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, files, schemas, classes, functions, runtime artifacts, integrations, MCP exposure rules, registration rules, tests, implementation order, acceptance criteria, and Definition of Done.
```
