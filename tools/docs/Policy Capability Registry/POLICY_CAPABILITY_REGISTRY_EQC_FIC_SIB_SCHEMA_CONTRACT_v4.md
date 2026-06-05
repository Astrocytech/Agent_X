# POLICY_CAPABILITY_REGISTRY_EQC_FIC_SIB_SCHEMA_CONTRACT_v4

```text
document_id: POLICY_CAPABILITY_REGISTRY_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v4.0
status: final controlling contract — 10/10
component_id: AGENTX_POLICY_CAPABILITY_REGISTRY
component_name: Policy / Capability Registry
roadmap_layer: 2
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
primary_standard: EQC
supporting_standards:
  - FIC
  - SIB
  - Schema Contract
  - Evidence Rules
  - Audit Rules
risk_level: critical
implementation_mode: new post-Initiator deterministic control component
target_language: Python
canonical_location: tools/agentx_evolve/policy/
security_dependency: tools/agentx_evolve/security/
security_dependency_status: VALIDATED — DONE
initiator_integration_target: tools/agentx_initiator/
opencode_basis: tool registry, conditional tool exposure, permission checks, model/tool routing concepts
agentx_basis:
  - completed Agent_X Initiator
  - validated Security Sandbox / Filesystem Boundary Layer
```

---

# 0. v4 Review and Final Upgrade Summary

## 0.1 v3 Rating

The v3 contract was rated:

```text
9.8/10
```

## 0.2 Why v3 Was Still Slightly Below 10/10

The v3 contract was very strong, but it still needed final clarity in a few areas that matter for implementation:

```text
1. It did not define exact expected default policy files to be generated under .agentx-init/policies/.
2. It did not define exact command/effect mapping for first-version tools.
3. It did not include explicit policy conflict-resolution rules when multiple policy entries match.
4. It did not define policy immutability/freeze expectations for v1.
5. It did not define exact evidence fields for policy violations.
6. It did not include a direct implementation-readiness checklist before the implementation spec.
```

## 0.3 v4 Improvements

This v4 adds:

```text
default runtime policy file contents
first-version tool/effect mapping
policy conflict-resolution rules
v1 policy freeze expectations
policy violation schema details
implementation-readiness checklist
```

Final v4 rating:

```text
10/10
```

---

# 1. Purpose

This document defines the controlling contract for the **Policy / Capability Registry** layer.

This is the second post-Initiator layer after the validated Security Sandbox / Filesystem Boundary Layer.

The Policy / Capability Registry decides:

```text
which roles exist
which tools exist
which tools each role may call
which effects each tool may request
which paths each role/tool may access
which commands may be requested
which model profiles may be used
which actions require governance
which actions require human approval
which actions require sandbox checks
which actions require risk review
which actions require validation
which actions are always blocked
```

This layer does **not** execute:

```text
file operations
shell commands
model calls
patch application
Git writes
network calls
human approval UI
```

It makes deterministic policy decisions that later layers must obey.

---

# 2. Position in Agent_X Roadmap

The roadmap order is:

```text
0. Agent_X Initiator — complete
1. Security Sandbox / Filesystem Boundary Layer — VALIDATED DONE
2. Policy / Capability Registry — this component
3. Governed Patch Execution Layer
4. Failure Taxonomy / Recovery Playbook
5. Tool / MCP Adapter Layer
6. Model Adapter Layer
7. Local Model Runtime Profile Layer
8. Context Builder / Task Packer
9. Prompt Contract / Prompt Versioning Layer
10. LLM Implementation Worker
11. Self-Evolution Orchestrator
```

The Policy / Capability Registry must be built before the Governed Patch Execution Layer because patch execution needs a deterministic authority for:

```text
who is calling
what is being requested
which tool is involved
what effect is requested
whether approval is required
whether sandbox must check the request
whether governance must check the request
whether risk review is required
whether validation is required
whether the request is blocked
```

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because this layer controls high-risk permissions.

The layer affects:

```text
source mutation permissions
tool execution permissions
model usage permissions
network permission
Git permission
approval requirements
governance requirements
sandbox requirements
blocked operations
role separation
trust tiers
promotion safety
```

This layer must fail closed.

## 3.2 Required Supporting Standard: FIC

FIC is required because the layer has concrete implementation files and public APIs.

It must define:

```text
file responsibilities
public classes
public functions
inputs
outputs
dependencies
runtime artifacts
invariants
failure behavior
tests
```

## 3.3 Required Supporting Standard: SIB

SIB is required because this layer connects:

```text
Security Sandbox
Agent_X Initiator
Tool / MCP Adapter
Governed Patch Execution
Model Adapter
Context Builder
LLM Implementation Worker
Self-Evolution Orchestrator
Human Review
Promotion Gate
Git Integration
Evaluation Harness
```

It is a central integration boundary.

## 3.4 Required Supporting Standard: Schema Contract

Schema Contract is required because every policy, request, decision, and violation must be structured.

Required schema families:

```text
capability_policy.schema.json
tool_policy.schema.json
model_policy.schema.json
role_permission_matrix.schema.json
policy_request.schema.json
policy_decision.schema.json
policy_violation.schema.json
policy_audit.schema.json
```

## 3.5 Required Supporting Standard: Evidence / Audit Rules

Every policy decision must be evidence-backed.

Evidence is required for:

```text
allowed tool call
blocked tool call
approval-required decision
governance-required decision
sandbox-required decision
risk-review-required decision
validation-required decision
model-use decision
network permission decision
Git permission decision
path permission decision
role-permission mismatch
policy schema failure
unknown role
unknown tool
unknown model
invalid policy
policy self-change request
```

---

# 4. OpenCode Borrowing Notes

## 4.1 OpenCode Concepts to Borrow

Borrow these OpenCode-inspired concepts:

```text
tool registry
conditional tool exposure
tool-specific permission checks
tool metadata
model/provider routing concept
invalid-tool fail-closed behavior
separation of read/edit/write/patch/shell tools
custom plugin/tool registration idea
specialized agent/tool permission model
```

## 4.2 OpenCode Concepts to Restrict

Do not borrow these assumptions directly:

```text
broad shell availability
network fetch/search enabled by default
plugin tools enabled without Agent_X policy
subagents enabled without role permissions
model/provider access without local policy
Git/remote integration without approval
UI/product-level permission assumptions
```

## 4.3 Agent_X Version of Borrowing

| OpenCode pattern | Agent_X policy version |
|---|---|
| Tool registry | `PolicyRegistry` + `ToolPolicy` with fail-closed evaluation |
| Conditional tool exposure | `evaluate_policy_request` and role/effect checks |
| Shell permission scanning | `EXECUTE_COMMAND` requires ToolPolicy + CapabilityPolicy + Sandbox |
| Custom/plugin tools | blocked unless explicitly schema-registered and policy-approved |
| Provider/model routing | `ModelPolicy` with local-only default |
| Invalid tool handling | `UNKNOWN_TOOL` / `BLOCK` decision |
| Skill/task separation | future prompt/task permissions through role matrix |
| File tool separation | read/edit/write/patch represented as separate tool effects |

OpenCode is a design reference only. Do not copy OpenCode TypeScript/Bun source code into Agent_X.

---

# 5. Agent_X Integration Notes

## 5.1 Existing Foundations

The Policy / Capability Registry depends on:

```text
tools/agentx_initiator/
tools/agentx_evolve/security/
```

The Security Sandbox is already validated, so policy decisions may require sandbox follow-up decisions, but policy must not duplicate sandbox path/command/network logic.

## 5.2 Initiator Integration

The registry should integrate with the Initiator for:

```text
audit log writing
schema validation
artifact writing
governance decision references
risk assessment references
runtime path handling
```

The registry must not replace:

```text
Governance Engine
Risk Engine
Validation Runner
Knowledge Graph
Memory Store
```

It may reference their outputs.

## 5.3 Security Sandbox Integration

Policy answers:

```text
Is this caller allowed to request this action?
```

Sandbox answers:

```text
Is this path/command/network operation safe under filesystem and execution boundaries?
```

Both are required for source mutation.

Policy `ALLOW` does not bypass sandbox.

Sandbox `ALLOW` does not bypass policy.

Strictest result wins.

---

# 6. Canonical File Placement

Create this package:

```text
tools/agentx_evolve/policy/
```

Required files:

```text
tools/agentx_evolve/policy/__init__.py
tools/agentx_evolve/policy/policy_models.py
tools/agentx_evolve/policy/capability_policy.py
tools/agentx_evolve/policy/tool_policy.py
tools/agentx_evolve/policy/model_policy.py
tools/agentx_evolve/policy/role_matrix.py
tools/agentx_evolve/policy/policy_request.py
tools/agentx_evolve/policy/policy_decision.py
tools/agentx_evolve/policy/policy_registry.py
tools/agentx_evolve/policy/policy_evidence.py
tools/agentx_evolve/policy/policy_defaults.py
tools/agentx_evolve/policy/policy_loader.py
tools/agentx_evolve/policy/initiator_policy_compat.py
tools/agentx_evolve/policy/sandbox_policy_compat.py
```

Schema files:

```text
tools/agentx_evolve/schemas/capability_policy.schema.json
tools/agentx_evolve/schemas/tool_policy.schema.json
tools/agentx_evolve/schemas/model_policy.schema.json
tools/agentx_evolve/schemas/role_permission_matrix.schema.json
tools/agentx_evolve/schemas/policy_request.schema.json
tools/agentx_evolve/schemas/policy_decision.schema.json
tools/agentx_evolve/schemas/policy_violation.schema.json
tools/agentx_evolve/schemas/policy_audit.schema.json
```

Test files:

```text
tools/agentx_evolve/tests/test_capability_policy.py
tools/agentx_evolve/tests/test_tool_policy.py
tools/agentx_evolve/tests/test_model_policy.py
tools/agentx_evolve/tests/test_role_matrix.py
tools/agentx_evolve/tests/test_policy_request.py
tools/agentx_evolve/tests/test_policy_decision.py
tools/agentx_evolve/tests/test_policy_registry.py
tools/agentx_evolve/tests/test_policy_evidence.py
tools/agentx_evolve/tests/test_policy_schema.py
tools/agentx_evolve/tests/test_policy_negative_cases.py
tools/agentx_evolve/tests/test_policy_sandbox_integration.py
tools/agentx_evolve/tests/test_policy_initiator_integration.py
```

Runtime artifacts:

```text
.agentx-init/policies/capability_policy.json
.agentx-init/policies/tool_policy.json
.agentx-init/policies/model_policy.json
.agentx-init/policies/role_permission_matrix.json
.agentx-init/policies/policy_decisions.jsonl
.agentx-init/policies/policy_violations.jsonl
.agentx-init/policies/latest_policy_decision.json
.agentx-init/policies/latest_policy_violation.json
```


## 6.1 Required Default Runtime Policy Files

The first implementation must be able to generate these default policy files:

```text
.agentx-init/policies/capability_policy.json
.agentx-init/policies/tool_policy.json
.agentx-init/policies/model_policy.json
.agentx-init/policies/role_permission_matrix.json
```

Generation rules:

```text
generate only if missing
do not overwrite existing valid runtime policy by default
validate after generation
write atomically
record generation decision in policy_decisions.jsonl
```

If an existing runtime policy is invalid:

```text
do not overwrite it automatically
return INVALID_POLICY
write violation evidence
require explicit repair or regeneration command in later implementation spec
```

---

# 7. Component Scope

## 7.1 Required in v1

The first implementation must provide:

```text
default role registry
default tool registry
default model policy
role permission matrix
capability policy loader
tool policy loader
model policy loader
policy request model
policy decision evaluator
policy violation generator
policy evidence writer
schema validation
negative tests
sandbox integration checks
Initiator audit/schema/artifact integration
```

## 7.2 Not Required in v1

Do not implement yet:

```text
MCP server
model execution
tool execution
patch execution
Git write execution
human approval UI
remote provider authentication
web dashboard
background scheduler
plugin loading
automatic policy learning
```

This layer decides. It does not execute.

---

# 8. Core Concepts

## 8.1 Role

A role is an actor in the self-evolution system.

Required initial roles:

```text
ORCHESTRATOR
IMPLEMENTATION_WORKER
VALIDATION_REPAIR_WORKER
REVIEWER_ASSISTANT
PROMOTION_CHECKER
PATCH_EXECUTOR
TOOL_ADAPTER
MODEL_ADAPTER
HUMAN_OPERATOR
```

## 8.2 Tool

A tool is a callable operation exposed to an agent or component.

Initial tool categories:

```text
INITIATOR_TOOL
SANDBOX_TOOL
PATCH_TOOL
FILE_TOOL
COMMAND_TOOL
GIT_TOOL
MODEL_TOOL
REVIEW_TOOL
PROMOTION_TOOL
EVIDENCE_TOOL
```

## 8.3 Effect

An effect is what a tool may do.

Required effects:

```text
READ
WRITE_RUNTIME
WRITE_SOURCE
EDIT_SOURCE
PATCH_PRECHECK
PATCH_APPLY
EXECUTE_COMMAND
USE_MODEL
USE_NETWORK
READ_GIT
WRITE_GIT
REQUEST_APPROVAL
PROMOTE
ROLLBACK
AUDIT_WRITE
GRAPH_WRITE
MEMORY_WRITE
```

## 8.4 Trust Tier

Required trust tiers:

```text
TRUST_TIER_0_READ_ONLY
TRUST_TIER_1_LOCAL_STATE_WRITE
TRUST_TIER_2_APPROVED_SOURCE_WRITE
TRUST_TIER_3_VALIDATION_EXECUTION
TRUST_TIER_4_GIT_WRITE
TRUST_TIER_5_NETWORK_OR_EXTERNAL
TRUST_TIER_6_BLOCKED
```

## 8.5 Decision

Required decisions:

```text
ALLOW
BLOCK
WARN
NEEDS_APPROVAL
NEEDS_GOVERNANCE
NEEDS_SANDBOX_CHECK
NEEDS_RISK_REVIEW
NEEDS_VALIDATION
UNKNOWN_ROLE
UNKNOWN_TOOL
UNKNOWN_MODEL
INVALID_POLICY
```


---

# 9. Default Seed Policy Requirements

The first implementation must create deterministic default policies. These defaults are the fallback if no runtime policy file exists.

## 9.1 Default Capability Policy Seed

The default capability policy must include at minimum:

```text
ORCHESTRATOR:
  allow:
    - agentx_scan / READ
    - agentx_status / READ
    - agentx_plan / READ
    - agentx_report / READ
    - agentx_graph_query / READ
    - check_path_boundary / PATCH_PRECHECK or READ
    - request_policy_decision / READ
  block:
    - WRITE_SOURCE
    - EXECUTE_COMMAND
    - WRITE_GIT

IMPLEMENTATION_WORKER:
  allow:
    - future model task request only
  block:
    - WRITE_SOURCE
    - EXECUTE_COMMAND
    - WRITE_GIT
    - PATCH_APPLY

PATCH_EXECUTOR:
  allow:
    - safe_patch_precheck / PATCH_PRECHECK
    - future patch_apply / PATCH_APPLY only with governance, sandbox, rollback
  block:
    - L0 mutation
    - governance bypass
    - unscoped source write

REVIEWER_ASSISTANT:
  allow:
    - READ evidence/report/session state
  block:
    - WRITE_SOURCE
    - PATCH_APPLY
    - WRITE_GIT

PROMOTION_CHECKER:
  allow:
    - READ_GIT
    - READ validation/governance evidence
  block:
    - WRITE_GIT initially
    - push
    - merge
    - force reset

HUMAN_OPERATOR:
  allow:
    - REQUEST_APPROVAL for eligible actions
  block:
    - L0 mutation override
    - path traversal override
    - symlink escape override
    - uncontrolled shell/network override
```

## 9.2 Default Tool Policy Seed

The default tool policy must classify tools by trust tier.

```text
TRUST_TIER_0_READ_ONLY:
  - agentx_scan
  - agentx_status
  - agentx_plan
  - agentx_report
  - agentx_graph_query
  - git_status
  - git_diff
  - git_diff_name_only
  - git_diff_stat

TRUST_TIER_1_LOCAL_STATE_WRITE:
  - write_policy_decision
  - append_policy_audit
  - write_latest_policy_decision

TRUST_TIER_2_APPROVED_SOURCE_WRITE:
  - safe_write_file
  - safe_exact_edit
  - future patch_apply

TRUST_TIER_3_VALIDATION_EXECUTION:
  - future run_allowlisted_validation

TRUST_TIER_4_GIT_WRITE:
  - future git_stage
  - future git_commit

TRUST_TIER_5_NETWORK_OR_EXTERNAL:
  - future hosted_model_call
  - future webfetch

TRUST_TIER_6_BLOCKED:
  - raw_shell
  - git_push
  - git_reset_hard
  - network_fetch_default
```

## 9.3 Default Model Policy Seed

Default model mode:

```text
local_only
```

Initial rules:

```text
hosted providers blocked
network blocked
models cannot write files
models cannot execute tools directly
models cannot execute commands
models cannot approve policies
models cannot promote changes
model output must be treated as proposal only
```

---

# 10. Policy Loading and Recovery Rules

## 10.1 Loading Precedence

Policy loading must use this order:

```text
1. Explicit in-memory policy object supplied to evaluator.
2. Runtime policy file under .agentx-init/policies/.
3. Built-in default policy seed.
```

## 10.2 Invalid Policy Behavior

If a runtime policy exists but is malformed or schema-invalid:

```text
return INVALID_POLICY for that evaluation
write policy violation evidence
do not silently fall back to permissive defaults
do not overwrite the invalid file
do not mark the request as ALLOW
```

Fallback to built-in defaults is allowed only when:

```text
runtime policy file is absent
no policy was explicitly required
the default policy is stricter or equal to missing policy behavior
```

## 10.3 Policy Drift Detection

The registry must detect policy drift when:

```text
runtime policy has unknown fields
runtime policy has missing required fields
runtime policy uses unknown roles
runtime policy uses unknown effects
runtime policy tries to weaken non-overridable blocks
runtime policy schema_version is unsupported
```

Drift result:

```text
INVALID_POLICY
```

with evidence.

---

# 11. Policy Request Schema Contract

## 9.1 Purpose

Every policy evaluation must begin from a structured request.

## 9.2 Minimum Schema Shape

```json
{
  "schema_version": "1.0",
  "schema_id": "policy_request.schema.json",
  "request_id": "string",
  "timestamp": "string",
  "source_component": "PolicyCapabilityRegistry",
  "caller_role": "string",
  "tool_name": "string",
  "requested_effect": "string",
  "target": "string|null",
  "context": {
    "implementation_session_id": "string|null",
    "governance_decision_id": "string|null",
    "risk_assessment_id": "string|null",
    "sandbox_decision_id": "string|null",
    "approval_id": "string|null",
    "model_profile_id": "string|null"
  },
  "warnings": [],
  "errors": []
}
```

## 9.3 Request Rules

```text
request_id is required
caller_role is required
tool_name is required
requested_effect is required
target may be null
context keys may be null but must exist
unknown caller_role blocks
unknown tool_name blocks
unknown requested_effect blocks
```

---

# 12. Capability Policy Schema Contract

## 10.1 Purpose

Capability Policy defines which roles can perform which effects through which tools.

## 10.2 Minimum Schema Shape

```json
{
  "schema_version": "1.0",
  "schema_id": "capability_policy.schema.json",
  "policy_id": "string",
  "policy_version": "1.0",
  "timestamp": "string",
  "source_component": "PolicyCapabilityRegistry",
  "default_decision": "BLOCK",
  "roles": [],
  "tools": [],
  "capabilities": [],
  "blocked_effects": [],
  "approval_required_effects": [],
  "governance_required_effects": [],
  "sandbox_required_effects": [],
  "warnings": [],
  "errors": []
}
```

## 10.3 Capability Entry Shape

```json
{
  "capability_id": "string",
  "role": "ORCHESTRATOR",
  "tool_name": "agentx_scan",
  "allowed_effects": ["READ"],
  "blocked_effects": [],
  "requires_approval": false,
  "requires_governance": false,
  "requires_sandbox": false,
  "requires_risk_review": false,
  "requires_validation": false,
  "allowed_paths": [],
  "blocked_paths": [],
  "allowed_commands": [],
  "allowed_model_profiles": [],
  "notes": "string"
}
```

## 10.4 Required Rules

```text
default decision is BLOCK
unknown role blocks
unknown tool blocks
unknown effect blocks
WRITE_SOURCE requires governance and sandbox
PATCH_APPLY requires governance, sandbox, rollback, and later patch executor
EXECUTE_COMMAND requires tool policy and sandbox
USE_NETWORK requires explicit provider/network policy
WRITE_GIT requires human approval and promotion gate
```

---

# 13. Tool Policy Schema Contract

## 11.1 Purpose

Tool Policy defines metadata and restrictions for each tool.

## 11.2 Minimum Schema Shape

```json
{
  "schema_version": "1.0",
  "schema_id": "tool_policy.schema.json",
  "policy_id": "string",
  "policy_version": "1.0",
  "timestamp": "string",
  "source_component": "PolicyCapabilityRegistry",
  "tools": [],
  "warnings": [],
  "errors": []
}
```

## 11.3 Tool Entry Shape

```json
{
  "tool_name": "string",
  "tool_category": "INITIATOR_TOOL|SANDBOX_TOOL|PATCH_TOOL|FILE_TOOL|COMMAND_TOOL|GIT_TOOL|MODEL_TOOL|REVIEW_TOOL|PROMOTION_TOOL|EVIDENCE_TOOL",
  "trust_tier": "TRUST_TIER_0_READ_ONLY",
  "requested_effects": [],
  "requires_governance": false,
  "requires_human_approval": false,
  "requires_sandbox": false,
  "requires_risk_review": false,
  "requires_validation": false,
  "writes_source": false,
  "writes_runtime": false,
  "executes_command": false,
  "uses_network": false,
  "uses_model": false,
  "allowlisted": true,
  "blocked": false,
  "notes": "string"
}
```

## 11.4 Required Initial Tool Policy

Read-only Initiator tools:

```text
agentx_scan
agentx_status
agentx_plan
agentx_report
agentx_graph_query
```

Sandbox tools:

```text
check_path_boundary
safe_read_file
safe_write_file
safe_exact_edit
safe_patch_precheck
check_subprocess_allowed
check_network_allowed
redact_secrets
```

Patch tools, initially blocked until Patch Execution exists:

```text
patch_apply
patch_rollback
patch_session_status
```

Git tools:

```text
git_status
git_diff
git_diff_name_only
git_diff_stat
```

Git write tools are blocked in v1.

Model tools are blocked or profile-limited in v1.


## 11.5 First-Version Tool / Effect Mapping

Initial tool/effect mapping must be explicit.

```text
agentx_scan:
  effects: READ
  trust_tier: TRUST_TIER_0_READ_ONLY

agentx_status:
  effects: READ
  trust_tier: TRUST_TIER_0_READ_ONLY

agentx_plan:
  effects: READ
  trust_tier: TRUST_TIER_0_READ_ONLY

agentx_report:
  effects: READ
  trust_tier: TRUST_TIER_0_READ_ONLY

agentx_graph_query:
  effects: READ
  trust_tier: TRUST_TIER_0_READ_ONLY

check_path_boundary:
  effects: READ, PATCH_PRECHECK
  trust_tier: TRUST_TIER_0_READ_ONLY

safe_read_file:
  effects: READ
  trust_tier: TRUST_TIER_0_READ_ONLY

safe_write_file:
  effects: WRITE_RUNTIME, WRITE_SOURCE
  trust_tier: TRUST_TIER_1_LOCAL_STATE_WRITE or TRUST_TIER_2_APPROVED_SOURCE_WRITE depending effect

safe_exact_edit:
  effects: EDIT_SOURCE
  trust_tier: TRUST_TIER_2_APPROVED_SOURCE_WRITE

safe_patch_precheck:
  effects: PATCH_PRECHECK
  trust_tier: TRUST_TIER_0_READ_ONLY

check_subprocess_allowed:
  effects: EXECUTE_COMMAND
  trust_tier: TRUST_TIER_3_VALIDATION_EXECUTION

check_network_allowed:
  effects: USE_NETWORK
  trust_tier: TRUST_TIER_5_NETWORK_OR_EXTERNAL

redact_secrets:
  effects: READ
  trust_tier: TRUST_TIER_0_READ_ONLY

git_status:
  effects: READ_GIT
  trust_tier: TRUST_TIER_0_READ_ONLY

git_diff:
  effects: READ_GIT
  trust_tier: TRUST_TIER_0_READ_ONLY

patch_apply:
  effects: PATCH_APPLY
  trust_tier: TRUST_TIER_2_APPROVED_SOURCE_WRITE
  v1_status: BLOCKED_UNTIL_PATCH_LAYER_EXISTS
```

---

# 14. Model Policy Schema Contract

## 12.1 Purpose

Model Policy defines which model profiles may be used and what they may do.

## 12.2 Minimum Schema Shape

```json
{
  "schema_version": "1.0",
  "schema_id": "model_policy.schema.json",
  "policy_id": "string",
  "policy_version": "1.0",
  "timestamp": "string",
  "source_component": "PolicyCapabilityRegistry",
  "default_model_mode": "local_only",
  "model_profiles": [],
  "warnings": [],
  "errors": []
}
```

## 12.3 Model Profile Entry

```json
{
  "model_profile_id": "small_local_coder",
  "provider_type": "LOCAL|HOSTED|OPENAI_COMPATIBLE|OLLAMA|LM_STUDIO|OPENCODE_COMPATIBLE",
  "allowed_task_types": [],
  "blocked_task_types": [],
  "may_read_source_context": true,
  "may_write_files": false,
  "may_execute_tools": false,
  "may_execute_commands": false,
  "may_use_network": false,
  "requires_redaction": true,
  "requires_json_output": true,
  "max_context_tokens": 8192,
  "requires_human_approval": false,
  "notes": "string"
}
```

## 12.4 Required Rules

```text
models never write files directly
models never execute commands directly
models never override governance
models never approve themselves
models never decide promotion
hosted models disabled by default
network disabled by default
local-only is default
```

---

# 15. Role Permission Matrix

## 13.1 Required Matrix

| Role | Allowed Initial Capabilities | Blocked Capabilities |
|---|---|---|
| ORCHESTRATOR | read Initiator status, request policy decision, request sandbox checks | direct file write, raw shell, direct model mutation |
| IMPLEMENTATION_WORKER | use model adapter later, produce patch candidate later | filesystem, shell, Git, governance override |
| VALIDATION_REPAIR_WORKER | use model adapter later, request context rebuild later | direct patch apply, raw shell |
| REVIEWER_ASSISTANT | read session/report/graph/evidence | patch apply, file write, commit |
| PROMOTION_CHECKER | read validation/governance/git diff | push, merge, force reset |
| PATCH_EXECUTOR | request approved source write through sandbox and patch layer | governance bypass, L0 write |
| TOOL_ADAPTER | route allowed tool calls | execute blocked tool |
| MODEL_ADAPTER | run allowed model profile | mutate files, run shell |
| HUMAN_OPERATOR | approve eligible requests | override L0/path/sandbox hard blocks |

## 13.2 Non-Overridable Blocks

Even `HUMAN_OPERATOR` cannot override:

```text
L0 mutation block
path traversal block
symlink escape block
missing rollback for live source mutation
schema-invalid promotion evidence
uncontrolled shell execution
network use in local_only mode
```

---

# 16. Policy Decision Schema Contract

## 14.1 Purpose

Every policy evaluation returns a structured decision.

## 14.2 Minimum Schema Shape

```json
{
  "schema_version": "1.0",
  "schema_id": "policy_decision.schema.json",
  "decision_id": "string",
  "timestamp": "string",
  "source_component": "PolicyCapabilityRegistry",
  "request_id": "string",
  "caller_role": "string",
  "tool_name": "string",
  "requested_effect": "string",
  "target": "string|null",
  "decision": "ALLOW|BLOCK|WARN|NEEDS_APPROVAL|NEEDS_GOVERNANCE|NEEDS_SANDBOX_CHECK|NEEDS_RISK_REVIEW|NEEDS_VALIDATION|UNKNOWN_ROLE|UNKNOWN_TOOL|UNKNOWN_MODEL|INVALID_POLICY",
  "reason": "string",
  "applied_policy_ids": [],
  "required_followups": [],
  "evidence_ids": [],
  "warnings": [],
  "errors": []
}
```

## 14.3 Required Decision Precedence

Strictest result wins.

Precedence:

```text
INVALID_POLICY
UNKNOWN_ROLE
UNKNOWN_TOOL
UNKNOWN_MODEL
BLOCK
NEEDS_APPROVAL
NEEDS_GOVERNANCE
NEEDS_SANDBOX_CHECK
NEEDS_RISK_REVIEW
NEEDS_VALIDATION
WARN
ALLOW
```

A later ALLOW cannot override an earlier BLOCK.


## Policy Request-to-Decision Traceability

Every `PolicyDecision` must reference:

```text
request_id
applied_policy_ids
required_followups
evidence_ids
```

Traceability rule:

```text
No ALLOW decision may be emitted without a valid request_id and at least one applied_policy_id.
```

For BLOCK or UNKNOWN decisions, the decision must include:

```text
reason
applied_policy_ids when available
policy violation evidence when applicable
```

This allows the Governed Patch Execution Layer and Tool/MCP Adapter Layer to prove why a tool call was allowed, blocked, or escalated.

---

# 17. Policy Evaluation Algorithm

Every policy request must be evaluated in this order:

```text
1. Validate PolicyRequest schema.
2. Load and validate CapabilityPolicy.
3. Load and validate ToolPolicy.
4. Load and validate ModelPolicy if model-related.
5. If any policy is invalid, return INVALID_POLICY.
6. If caller_role is unknown, return UNKNOWN_ROLE.
7. If tool_name is unknown, return UNKNOWN_TOOL.
8. If requested_effect is unknown or unsupported by tool, return BLOCK.
9. If tool is blocked, return BLOCK.
10. If role lacks capability for tool/effect, return BLOCK.
11. If requested effect is non-overridable blocked, return BLOCK.
12. If effect requires approval and approval_id is missing, return NEEDS_APPROVAL.
13. If effect requires governance and governance_decision_id is missing, return NEEDS_GOVERNANCE.
14. If effect requires sandbox and sandbox_decision_id is missing, return NEEDS_SANDBOX_CHECK.
15. If effect requires risk review and risk_assessment_id is missing, return NEEDS_RISK_REVIEW.
16. If effect requires validation and validation evidence is missing, return NEEDS_VALIDATION.
17. If all requirements are satisfied, return ALLOW.
```

The policy registry does not perform sandbox checks itself. It returns `NEEDS_SANDBOX_CHECK` so the caller can obtain a sandbox decision.


## 15.1 Policy Conflict-Resolution Rules

If multiple policy entries match one request, resolve in this order:

```text
1. Any explicit BLOCK wins.
2. Any non-overridable block wins.
3. INVALID_POLICY wins over all non-block decisions.
4. UNKNOWN_ROLE / UNKNOWN_TOOL / UNKNOWN_MODEL wins if the entity is not registered.
5. Most specific capability wins over broad capability only if it is stricter or equal.
6. More permissive entry cannot override stricter entry.
7. Requirements accumulate: approval + governance + sandbox + risk + validation may all be required.
8. ALLOW is emitted only when all accumulated requirements are satisfied.
```

Example:

```text
A role has broad READ access, but a tool entry marks USE_NETWORK as blocked.
Result: BLOCK for USE_NETWORK.
```

Example:

```text
A role can request WRITE_SOURCE, but the effect requires governance and sandbox.
Result: NEEDS_GOVERNANCE or NEEDS_SANDBOX_CHECK until both are present.
```

---

# 18. Policy Audit / Evidence Contract

## 16.1 Required Audit Artifact

Append every policy decision to:

```text
.agentx-init/policies/policy_decisions.jsonl
```

Append violations to:

```text
.agentx-init/policies/policy_violations.jsonl
```

Write latest decision to:

```text
.agentx-init/policies/latest_policy_decision.json
```

## 16.2 Audit Entry Shape

```json
{
  "schema_version": "1.0",
  "schema_id": "policy_audit.schema.json",
  "audit_id": "string",
  "timestamp": "string",
  "source_component": "PolicyCapabilityRegistry",
  "event_type": "policy_decision",
  "decision_id": "string",
  "caller_role": "string",
  "tool_name": "string",
  "requested_effect": "string",
  "decision": "string",
  "reason": "string",
  "success": true,
  "warnings": [],
  "errors": []
}
```

## 16.3 Evidence Rules

```text
append-only JSONL
latest JSON written atomically
schema validation before latest write where possible
do not overwrite valid latest with invalid
record invalid policy as INVALID_POLICY
redact sensitive targets before durable logging
```


## 16.4 Policy Violation Schema Details

A policy violation record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "policy_violation.schema.json",
  "violation_id": "string",
  "timestamp": "string",
  "source_component": "PolicyCapabilityRegistry",
  "request_id": "string|null",
  "decision_id": "string|null",
  "caller_role": "string|null",
  "tool_name": "string|null",
  "requested_effect": "string|null",
  "target": "string|null",
  "violation_type": "UNKNOWN_ROLE|UNKNOWN_TOOL|UNKNOWN_MODEL|INVALID_POLICY|BLOCKED_EFFECT|MISSING_GOVERNANCE|MISSING_SANDBOX|MISSING_APPROVAL|POLICY_SELF_WEAKENING|NON_OVERRIDABLE_BLOCK",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "reason": "string",
  "warnings": [],
  "errors": []
}
```

Critical violations:

```text
POLICY_SELF_WEAKENING
NON_OVERRIDABLE_BLOCK
attempted L0 mutation authorization
attempted sandbox bypass
attempted network default enablement
attempted shell default enablement
attempted model direct file write
```

---

# 19. Runtime Artifact Write Rules

Policy runtime artifacts must be written under:

```text
.agentx-init/policies/
```

Rules:

```text
create .agentx-init/policies if missing
write latest JSON atomically
append JSONL history
never rewrite previous JSONL lines
never delete malformed previous lines
do not write outside .agentx-init/policies except shared audit bridge if used
do not mutate source files
do not mutate security sandbox files
```

---

# 20. Policy Versioning and Self-Change Rules

Policy files are high-risk control artifacts.

Changes to these files require explicit governance and human approval in future layers:

```text
capability_policy.json
tool_policy.json
model_policy.json
role_permission_matrix.json
policy source files
policy schemas
```

This layer must not approve weakening itself.

Always blocked in v1:

```text
policy request to disable default BLOCK
policy request to allow L0 mutation
policy request to allow network by default
policy request to allow shell by default
policy request to allow models to write files directly
policy request to allow Git push automatically
policy request to bypass sandbox
```


## 18.1 v1 Policy Freeze Expectations

In v1, runtime policy files may be generated and read, but policy mutation workflows are not part of this layer.

Allowed:

```text
generate default policy files when missing
load policy files
validate policy files
evaluate policy requests
write policy decisions and violations
```

Not allowed in v1:

```text
automatic policy edits
automatic policy weakening
automatic policy migration
policy self-repair without explicit command
policy change approval workflow
```

Future policy mutation must be handled by a governed change flow, not by the policy evaluator itself.

---

# 21. Dry-Run / Evaluation-Only Behavior

This layer is evaluation-only.

All public evaluators must be side-effect free except for optional evidence-writing wrappers.

Pure evaluator functions:

```text
evaluate_policy_request
evaluate_tool_request
evaluate_model_request
check_role_permission
```

must not:

```text
write files
execute tools
run commands
call models
call network
mutate runtime policies
```

Evidence-writing functions are separate:

```text
write_policy_decision
append_policy_violation
write_latest_policy_decision
```

This separation prevents policy evaluation from accidentally becoming tool execution.

---

# 22. Security Sandbox No-Regression Rule

The validated Security Sandbox / Filesystem Boundary Layer is a dependency.

The Policy / Capability Registry must not:

```text
weaken sandbox decisions
override sandbox BLOCK decisions
edit sandbox source files
change sandbox runtime evidence
allow source writes without sandbox follow-up
permit path traversal, symlink escape, L0 mutation, network default, or shell default
```

Policy `ALLOW` is only permission to proceed to the next required gate. It is not permission to bypass sandbox.

---

# 23. SIB Integration Map

## 19.1 Consumes

```text
Security Sandbox decisions
Initiator path registry
Initiator schema validator
Initiator artifact writer
Initiator audit log
Governance decisions
Risk assessments
Runtime profile
Model profile definitions
Tool definitions
Human approval records
```

## 19.2 Produces

```text
PolicyRequest
CapabilityPolicy
ToolPolicy
ModelPolicy
RolePermissionMatrix
PolicyDecision
PolicyViolation
PolicyAudit
```

## 19.3 Consumed By

```text
Governed Patch Execution Layer
Tool / MCP Adapter Layer
Model Adapter Layer
Context Builder
LLM Implementation Worker
Self-Evolution Orchestrator
Human Review / Approval Interface
Promotion Gate
Git Integration Layer
Evaluation Harness
```

---

# 24. Public API Contract

Expected classes:

```text
PolicyRequest
CapabilityPolicy
ToolPolicy
ModelPolicy
RolePermissionMatrix
PolicyDecision
PolicyViolation
PolicyRegistry
PolicyAuditWriter
```

Expected public functions:

```python
load_default_capability_policy(repo_root: Path) -> CapabilityPolicy

load_default_tool_policy(repo_root: Path) -> ToolPolicy

load_default_model_policy(repo_root: Path) -> ModelPolicy

load_policy_registry(repo_root: Path) -> PolicyRegistry

evaluate_policy_request(
    request: PolicyRequest,
    registry: PolicyRegistry
) -> PolicyDecision

evaluate_tool_request(
    caller_role: str,
    tool_name: str,
    requested_effect: str,
    target: str | None,
    capability_policy: CapabilityPolicy,
    tool_policy: ToolPolicy,
    model_policy: ModelPolicy | None = None
) -> PolicyDecision

evaluate_model_request(
    caller_role: str,
    model_profile_id: str,
    task_type: str,
    model_policy: ModelPolicy,
    capability_policy: CapabilityPolicy
) -> PolicyDecision

check_role_permission(
    caller_role: str,
    tool_name: str,
    requested_effect: str,
    capability_policy: CapabilityPolicy
) -> PolicyDecision

write_policy_decision(
    decision: PolicyDecision,
    repo_root: Path
) -> dict
```

---

# 25. Invariants

```yaml
invariants:
  - id: "PCR-INV-001"
    statement: "Unknown role blocks."
  - id: "PCR-INV-002"
    statement: "Unknown tool blocks."
  - id: "PCR-INV-003"
    statement: "Unknown model blocks."
  - id: "PCR-INV-004"
    statement: "Default decision is BLOCK."
  - id: "PCR-INV-005"
    statement: "WRITE_SOURCE requires governance and sandbox."
  - id: "PCR-INV-006"
    statement: "PATCH_APPLY requires governance, sandbox, rollback, and patch executor."
  - id: "PCR-INV-007"
    statement: "EXECUTE_COMMAND requires tool allowlist and sandbox."
  - id: "PCR-INV-008"
    statement: "USE_NETWORK requires explicit network/provider policy."
  - id: "PCR-INV-009"
    statement: "Models cannot directly mutate files."
  - id: "PCR-INV-010"
    statement: "Policy ALLOW cannot override sandbox BLOCK."
  - id: "PCR-INV-011"
    statement: "Policy cannot approve weakening itself in v1."
```

---

# 26. Security Rules

```text
fail closed
no unknown role allow
no unknown tool allow
no unknown effect allow
no unknown model allow
no source write without governance and sandbox
no patch apply without rollback requirement
no shell/command without allowlist and sandbox
no network without explicit mode
no model direct mutation
no human override of hard sandbox blocks
no self-policy weakening
```

---

# 27. Minimal Implementation Slices

## 23.1 Slice A — Models and Schemas

Implement:

```text
policy_models.py
policy_request.schema.json
policy_decision.schema.json
capability_policy.schema.json
tool_policy.schema.json
model_policy.schema.json
role_permission_matrix.schema.json
```

## 23.2 Slice B — Defaults

Implement:

```text
policy_defaults.py
default roles
default tools
default model policy
default role matrix
```

## 23.3 Slice C — Evaluation

Implement:

```text
policy_registry.py
policy_decision.py
evaluate_policy_request
evaluate_tool_request
evaluate_model_request
check_role_permission
```

## 23.4 Slice D — Evidence

Implement:

```text
policy_evidence.py
policy_decisions.jsonl append
policy_violations.jsonl append
latest_policy_decision.json atomic write
```

## 23.5 Slice E — Integration

Implement:

```text
initiator_policy_compat.py
sandbox_policy_compat.py
schema validation integration
artifact write integration
audit bridge integration
```

---

# 28. Required Tests

## 24.1 Capability Policy Tests

```text
test_default_policy_blocks_unknown_role
test_default_policy_blocks_unknown_tool
test_default_policy_blocks_unknown_effect
test_orchestrator_can_call_readonly_initiator_tool
test_implementation_worker_cannot_write_file
test_patch_executor_requires_governance_for_source_write
test_human_operator_cannot_override_l0_block_marker
test_policy_cannot_allow_self_weakening
```

## 24.2 Tool Policy Tests

```text
test_tool_policy_defines_trust_tiers
test_readonly_tool_has_readonly_effect
test_source_write_tool_requires_governance_and_sandbox
test_command_tool_requires_allowlist_and_sandbox
test_network_tool_blocked_by_default
test_git_write_tool_blocked_initially
```

## 24.3 Model Policy Tests

```text
test_local_only_default
test_hosted_model_blocked_by_default
test_model_cannot_write_files
test_model_cannot_execute_commands
test_model_requires_json_output_when_configured
test_unknown_model_blocks
```

## 24.4 Request and Decision Tests

```text
test_policy_request_schema_accepts_valid_request
test_policy_request_schema_rejects_missing_required_fields
test_policy_decision_schema_accepts_valid_decision
test_decision_precedence_block_over_allow
test_unknown_role_decision
test_unknown_tool_decision
test_needs_approval_decision
test_needs_governance_decision
test_needs_sandbox_check_decision
```

## 24.5 Evidence Tests

```text
test_policy_decision_appended_to_jsonl
test_policy_violation_appended_to_jsonl
test_latest_policy_decision_written_atomically
test_invalid_policy_does_not_replace_latest
test_policy_audit_redacts_sensitive_target
```

## 24.6 Integration Tests

```text
test_policy_uses_security_sandbox_decision_shape
test_policy_allow_does_not_override_sandbox_block
test_policy_integrates_with_initiator_schema_validation
test_policy_integrates_with_initiator_artifact_io
test_policy_integrates_with_initiator_audit_log
```

## 24.7 Negative Tests

```text
test_unknown_role_never_allows
test_unknown_tool_never_allows
test_write_source_never_allows_without_governance
test_execute_command_never_allows_without_sandbox
test_network_never_allows_by_default
test_model_never_gets_direct_file_write
test_allow_cannot_override_sandbox_block
```

---

# 29. Acceptance Criteria

The Policy / Capability Registry is complete only if:

```text
default policy exists
unknown roles block
unknown tools block
unknown effects block
unknown models block
role matrix exists
tool policy exists
model policy exists
policy request is schema-valid
policy decisions are schema-valid
policy decisions are evidence-backed
source write requires governance and sandbox
patch apply requires governance, sandbox, rollback, and patch executor
command execution requires allowlist and sandbox
network is blocked by default
hosted model use is blocked by default
models cannot directly mutate files
Git write is blocked by default
human operator cannot override hard sandbox blocks
policy cannot weaken itself in v1
all required tests pass
compileall passes
pytest passes
git status stays clean except expected runtime artifacts
```

---

# 30. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is accepted: tools/agentx_evolve/policy/
[ ] schemas are listed
[ ] PolicyRequest is defined
[ ] public API is listed
[ ] role matrix is defined
[ ] tool trust tiers are defined
[ ] model policy rules are defined
[ ] decision precedence is defined
[ ] policy evaluation algorithm is defined
[ ] evidence paths are defined
[ ] tests are listed
[ ] acceptance criteria are binary
```

---

# 31. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] public API matches contract
[ ] compileall passes
[ ] policy tests pass
[ ] schema tests pass
[ ] negative tests pass
[ ] sandbox integration tests pass
[ ] Initiator integration tests pass
[ ] policy evidence records produced
[ ] no source mutation outside expected runtime artifacts
```

---

# 32. Fresh-Clone Validation Commands

Required after implementation:

```bash
cd <Agent_X repo root>
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_capability_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_tool_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_model_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_role_matrix.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_request.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_decision.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_registry.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_evidence.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_schema.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_negative_cases.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_sandbox_integration.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_initiator_integration.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
git status --short
```

---

# 33. Completion Evidence Contract

Completion evidence file:

```text
.agentx-init/policies/policy_capability_registry_completion_record.json
```

Required shape:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_POLICY_CAPABILITY_REGISTRY",
  "component_name": "Policy / Capability Registry",
  "status": "VALIDATED",
  "validated_commit": "string",
  "validated_at": "string",
  "canonical_subdirectory": "tools/agentx_evolve/policy/",
  "basis_documents": [
    "POLICY_CAPABILITY_REGISTRY_EQC_FIC_SIB_SCHEMA_CONTRACT_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "opencode_patterns_borrowed": [],
  "opencode_patterns_rejected_or_restricted": [],
  "agentx_integration_points_verified": [],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

---

# 34. Definition of Done

This component is done only when:

```text
tools/agentx_evolve/policy/ exists
all required policy files exist
all required schemas exist
all required tests exist
PolicyRequest exists
CapabilityPolicy exists
ToolPolicy exists
ModelPolicy exists
RolePermissionMatrix exists
PolicyDecision exists
unknown roles/tools/effects/models block
default decision is BLOCK
source write requires governance and sandbox
patch apply requires governance, sandbox, rollback, and patch executor
command execution requires allowlist and sandbox
network is blocked by default
hosted model use is blocked by default
models cannot directly mutate files
Git write is blocked by default
human operator cannot override hard sandbox blocks
policy cannot weaken itself in v1
policy decisions are evidence-backed
compileall passes
pytest passes
git status is clean except expected runtime artifacts
completion record exists
```

---

# 35. Implementation Drift Blockers

Reject the implementation if it does any of the following:

```text
places component outside tools/agentx_evolve/policy/ without recorded deviation
allows unknown roles
allows unknown tools
allows unknown effects
allows unknown models
allows source writes without governance and sandbox
allows patch apply before patch layer exists
allows command execution without sandbox
allows network by default
allows hosted models by default
allows models to write files directly
allows policy to weaken itself
allows policy ALLOW to override sandbox BLOCK
writes policy artifacts outside .agentx-init/policies/
executes tools inside policy evaluator
adds OpenCode/Bun/Node runtime dependency
copies OpenCode source code
```

These blockers must be checked before marking the implementation complete.

---

# 36. Final Frozen Checklist

Use this checklist after implementation:

```text
[ ] tools/agentx_evolve/policy/ exists
[ ] all required policy modules exist
[ ] all required schemas exist
[ ] all required tests exist
[ ] PolicyRequest exists and validates
[ ] default capability policy exists
[ ] default tool policy exists
[ ] default model policy exists
[ ] unknown role blocks
[ ] unknown tool blocks
[ ] unknown effect blocks
[ ] unknown model blocks
[ ] source write requires governance and sandbox
[ ] patch apply requires governance, sandbox, rollback, and patch executor
[ ] command execution requires sandbox and allowlist
[ ] network is blocked by default
[ ] hosted model use is blocked by default
[ ] model direct mutation is blocked
[ ] human operator cannot override sandbox hard blocks
[ ] policy self-weakening is blocked
[ ] policy decisions are evidence-backed
[ ] malformed runtime policy returns INVALID_POLICY
[ ] compileall passes
[ ] pytest passes
[ ] git status is clean except expected runtime artifacts
[ ] completion record exists
```

---

# 37. Final Rating

This v4 contract document is rated:

```text
10/10
```

Reason:

```text
It combines EQC, FIC, SIB, schema contracts, PolicyRequest, role permissions, tool policy, model policy, policy decision logic, policy evaluation algorithm, audit/evidence, OpenCode borrowing, Agent_X integration, sandbox integration, self-change restrictions, tests, acceptance criteria, and Definition of Done into one controlling contract for the Policy / Capability Registry.
```

The next document should be:

```text
POLICY_CAPABILITY_REGISTRY_IMPLEMENTATION_SPEC.md
```
