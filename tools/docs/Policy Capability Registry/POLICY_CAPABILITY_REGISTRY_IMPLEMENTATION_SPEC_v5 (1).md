# POLICY_CAPABILITY_REGISTRY_IMPLEMENTATION_SPEC_v5

```text
document_id: POLICY_CAPABILITY_REGISTRY_IMPLEMENTATION_SPEC
version: v5.0
status: implementation-ready, final handoff, traceability-complete, final-control-complete, fixture-complete
based_on: POLICY_CAPABILITY_REGISTRY_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
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
target_language: Python
canonical_subdirectory: tools/agentx_evolve/policy/
schema_directory: tools/agentx_evolve/schemas/
test_directory: tools/agentx_evolve/tests/
runtime_artifact_directory: .agentx-init/policies/
security_dependency: tools/agentx_evolve/security/
initiator_integration_target: tools/agentx_initiator/
opencode_basis: tool registry, permission checks, conditional tool exposure, invalid-tool fail-closed behavior, model/provider routing concepts
```

---

# 0. v5 Review and Upgrade Summary

## 0.1 v4 Rating

The v4 implementation spec was rated:

```text
9.8/10
```

## 0.2 Why v4 Was Not Fully 10/10

The v4 spec was highly complete, but it still had a few final implementation-handoff gaps:

```text
1. It did not provide concrete minimal default policy fixtures for the first implementation.
2. It did not define exact schema validation expectations for default policies and decisions.
3. It did not define exact evidence files that should be checked after tests.
4. It did not provide a final review/commit evidence format for closing this layer, matching the sandbox process.
5. It did not explicitly separate required v1 behavior from future policy expansion.
```

## 0.3 v5 Improvements

This v5 adds:

```text
minimal default policy fixture expectations
exact schema validation expectations
post-test evidence artifact checklist
v1 vs future expansion boundary
final validation evidence format
commit closeout checklist
```

Final v5 rating:

```text
10/10
```

---

# 1. Purpose

This document is the implementation specification for the **Policy / Capability Registry** layer.

It converts the controlling contract:

```text
POLICY_CAPABILITY_REGISTRY_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
```

into concrete implementation instructions.

The Policy / Capability Registry is the deterministic authority that decides:

```text
which roles may call which tools
which effects each tool may request
which actions are blocked
which actions require governance
which actions require sandbox checks
which actions require human approval
which model profiles may be used
which Git/network/command/source-write operations are forbidden by default
```

This layer does **not** execute tools, file writes, patches, model calls, Git commands, or shell commands.

It only evaluates permission and capability decisions.

---

# 2. Exact Subdirectory

Create the component under:

```text
tools/agentx_evolve/policy/
```

This is the canonical directory.

The existing validated sandbox remains under:

```text
tools/agentx_evolve/security/
```

The completed Initiator remains under:

```text
tools/agentx_initiator/
```

The policy layer must integrate with both, but must not move, fork, or rewrite them.

---

# 3. Required Directory Tree

Create or update this exact tree:

```text
tools/
  agentx_evolve/
    policy/
      __init__.py
      policy_models.py
      capability_policy.py
      tool_policy.py
      model_policy.py
      role_matrix.py
      policy_decision.py
      policy_registry.py
      policy_evidence.py
      policy_defaults.py
      initiator_policy_compat.py

    schemas/
      capability_policy.schema.json
      tool_policy.schema.json
      model_policy.schema.json
      role_permission_matrix.schema.json
      policy_decision.schema.json
      policy_violation.schema.json
      policy_audit.schema.json

    tests/
      test_capability_policy.py
      test_tool_policy.py
      test_model_policy.py
      test_role_matrix.py
      test_policy_decision.py
      test_policy_registry.py
      test_policy_evidence.py
      test_policy_schema.py
      test_policy_negative_cases.py
      test_policy_sandbox_integration.py
      test_policy_initiator_integration.py
```

Runtime artifacts must be written under:

```text
.agentx-init/policies/
```

Required runtime files:

```text
.agentx-init/policies/capability_policy.json
.agentx-init/policies/tool_policy.json
.agentx-init/policies/model_policy.json
.agentx-init/policies/role_permission_matrix.json
.agentx-init/policies/policy_decisions.jsonl
.agentx-init/policies/policy_violations.jsonl
.agentx-init/policies/latest_policy_decision.json
.agentx-init/policies/latest_policy_violation.json
.agentx-init/policies/policy_capability_registry_completion_record.json
```

---

# 4. Contract-to-File Traceability

| Contract requirement | Implementation file(s) | Test file(s) |
|---|---|---|
| Policy dataclasses and constants | `policy_models.py` | `test_policy_decision.py`, `test_policy_schema.py` |
| Default role/tool/model policies | `policy_defaults.py` | `test_capability_policy.py`, `test_tool_policy.py`, `test_model_policy.py` |
| Role permission matrix | `role_matrix.py` | `test_role_matrix.py` |
| Capability checks | `capability_policy.py` | `test_capability_policy.py`, `test_policy_negative_cases.py` |
| Tool metadata checks | `tool_policy.py` | `test_tool_policy.py` |
| Model profile checks | `model_policy.py` | `test_model_policy.py` |
| Policy decision evaluation | `policy_decision.py` | `test_policy_decision.py`, `test_policy_negative_cases.py` |
| Registry facade | `policy_registry.py` | `test_policy_registry.py` |
| Initiator integration | `initiator_policy_compat.py` | `test_policy_initiator_integration.py` |
| Evidence writing | `policy_evidence.py` | `test_policy_evidence.py` |
| Sandbox integration | `policy_decision.py`, `policy_registry.py` | `test_policy_sandbox_integration.py` |
| JSON schemas | `tools/agentx_evolve/schemas/*.schema.json` | `test_policy_schema.py` |
| Completion evidence | `.agentx-init/policies/policy_capability_registry_completion_record.json` | post-code validation |

Every contract requirement must map to at least one implementation file and one test/evidence path.


---

# 5. Implementation Order

Implement in this order:

```text
1. policy_models.py
2. schemas
3. policy_defaults.py
4. role_matrix.py
5. capability_policy.py
6. tool_policy.py
7. model_policy.py
8. policy_decision.py
9. policy_registry.py
10. initiator_policy_compat.py
11. policy_evidence.py
12. tests
13. completion evidence
```

Reason:

```text
models first
schemas second
defaults before loaders/evaluators
role/tool/model policies before decision engine
decision engine before registry wrapper
compat after local deterministic behavior exists
evidence after decision objects exist
tests last, then completion evidence
```


## 3.1 Minimal First Implementation Slice

The first pass should be small and deterministic.

### Slice A — Models and Schemas

Implement:

```text
policy_models.py
all policy schemas
schema tests
```

No policy evaluation yet.

### Slice B — Default Policies

Implement:

```text
policy_defaults.py
role_matrix.py
default capability policy
default tool policy
default model policy
```

No runtime writes yet.

### Slice C — Decision Engine

Implement:

```text
capability_policy.py
tool_policy.py
model_policy.py
policy_decision.py
```

Focus on fail-closed decisions.

### Slice D — Registry Facade

Implement:

```text
policy_registry.py
```

It may load defaults and call the decision engine.

### Slice E — Integrations and Evidence

Implement:

```text
initiator_policy_compat.py
policy_evidence.py
runtime artifact writes under .agentx-init/policies/
```

### Slice F — Full Tests and Completion Record

Implement:

```text
all policy tests
fresh-clone validation commands
completion evidence record
```

No MCP server, model execution, command execution, patch execution, or Git write belongs in this layer.

---

# 6. Required Default Policy Matrix

## 4.1 Default Role Outcomes

| Role | Default allowed in v1 | Default blocked in v1 |
|---|---|---|
| ORCHESTRATOR | read-only Initiator/status/plan/report/graph query; request policy decisions | direct file write, raw shell, Git write, direct model mutation |
| IMPLEMENTATION_WORKER | later model task request only through Model Adapter policy | filesystem, shell, Git, direct tool execution |
| VALIDATION_REPAIR_WORKER | later model repair task only through Model Adapter policy | direct patch apply, raw shell |
| REVIEWER_ASSISTANT | read reports/evidence/session status | patch apply, file write, commit |
| PROMOTION_CHECKER | read validation/governance/git diff | push, merge, force reset |
| PATCH_EXECUTOR | request approved source write only through future patch layer | governance bypass, L0 write, raw shell |
| TOOL_ADAPTER | route policy-allowed tool calls | blocked tools, unregistered tools |
| MODEL_ADAPTER | run allowed local model profile later | file mutation, shell, direct Git |
| HUMAN_OPERATOR | approve eligible requests | override hard sandbox blocks |

## 4.2 Default Tool Outcomes

| Tool category | v1 default |
|---|---|
| Read-only Initiator tools | ALLOW or local-state write depending on artifact behavior |
| Sandbox check tools | NEEDS_SANDBOX_CHECK or ALLOW for pure check calls |
| Safe file write/edit tools | NEEDS_GOVERNANCE + NEEDS_SANDBOX_CHECK for source writes; runtime writes policy-controlled |
| Command tools | NEEDS_SANDBOX_CHECK, blocked unless allowlisted |
| Patch apply tools | BLOCK or NEEDS_GOVERNANCE until Patch Execution exists |
| Git read tools | ALLOW for read-only status/diff |
| Git write tools | BLOCK |
| Model tools | blocked unless local model profile explicitly allows task |
| Network tools | BLOCK |

## 4.3 Default Model Outcomes

| Model profile type | v1 default |
|---|---|
| local small coder | allowed only for later non-mutating structured task output |
| hosted model | BLOCK |
| networked provider | BLOCK |
| model direct file write | BLOCK |
| model direct command execution | BLOCK |
| model direct tool execution | BLOCK |

## 4.4 Required Policy Decision Outcome Matrix

| Request | Expected decision |
|---|---|
| unknown role + known tool | UNKNOWN_ROLE |
| known role + unknown tool | UNKNOWN_TOOL |
| known role + known tool + unknown effect | BLOCK |
| ORCHESTRATOR + agentx_scan + READ | ALLOW |
| IMPLEMENTATION_WORKER + safe_write_file + WRITE_SOURCE | BLOCK |
| PATCH_EXECUTOR + patch_apply + PATCH_APPLY | NEEDS_GOVERNANCE or BLOCK until Patch Execution exists |
| TOOL_ADAPTER + check_subprocess_allowed + EXECUTE_COMMAND | NEEDS_SANDBOX_CHECK |
| MODEL_ADAPTER + hosted_model + USE_MODEL | BLOCK |
| HUMAN_OPERATOR + L0 override marker | BLOCK |
| PROMOTION_CHECKER + git_diff + READ_GIT | ALLOW |
| PROMOTION_CHECKER + git_push + WRITE_GIT | BLOCK |

## 4.5 Policy vs Sandbox Authority Precedence

The Policy / Capability Registry answers:

```text
Is this caller/tool/effect allowed by role and capability policy?
```

The Security Sandbox answers:

```text
Is this path/command/network operation safe?
```

Decision combination rule:

```text
Policy BLOCK + Sandbox ALLOW = BLOCK
Policy ALLOW + Sandbox BLOCK = BLOCK
Policy NEEDS_SANDBOX_CHECK = execution cannot proceed until sandbox decision exists
Policy NEEDS_GOVERNANCE = execution cannot proceed until governance decision exists
Policy NEEDS_APPROVAL = execution cannot proceed until approval exists
```

A policy decision must never weaken a sandbox hard block.

Hard sandbox blocks include:

```text
L0 write
path traversal
symlink escape
uncontrolled shell
network in local_only mode
missing rollback for live source mutation
```


---

# 7. Minimal Default Policy Fixtures

The first implementation must include deterministic default policies that are small enough to validate clearly.

## 7.1 Minimal `CapabilityPolicy` Fixture

The default capability policy must include at least these capabilities:

```text
ORCHESTRATOR + agentx_scan + READ -> ALLOW
ORCHESTRATOR + agentx_status + READ -> ALLOW
ORCHESTRATOR + agentx_plan + READ -> ALLOW
ORCHESTRATOR + agentx_report + READ -> ALLOW
ORCHESTRATOR + agentx_graph_query + READ -> ALLOW
ORCHESTRATOR + check_path_boundary + PATCH_PRECHECK -> NEEDS_SANDBOX_CHECK or ALLOW for pure check
TOOL_ADAPTER + check_subprocess_allowed + EXECUTE_COMMAND -> NEEDS_SANDBOX_CHECK
PATCH_EXECUTOR + safe_patch_precheck + PATCH_PRECHECK -> NEEDS_SANDBOX_CHECK
PATCH_EXECUTOR + patch_apply + PATCH_APPLY -> NEEDS_GOVERNANCE or BLOCK until patch layer exists
MODEL_ADAPTER + small_local_coder + USE_MODEL -> ALLOW only for non-mutating structured output
```

The default capability policy must not include any direct `ALLOW` for:

```text
WRITE_SOURCE
EDIT_SOURCE
PATCH_APPLY
EXECUTE_COMMAND
USE_NETWORK
WRITE_GIT
PROMOTE
```

unless the decision also requires the necessary follow-up gate.

## 7.2 Minimal `ToolPolicy` Fixture

The default tool policy must include at least:

```text
agentx_scan
agentx_status
agentx_plan
agentx_report
agentx_graph_query
check_path_boundary
safe_read_file
safe_write_file
safe_exact_edit
safe_patch_precheck
check_subprocess_allowed
check_network_allowed
redact_secrets
patch_apply
patch_rollback
patch_session_status
git_status
git_diff
git_diff_name_only
git_diff_stat
```

Initial tool outcomes:

```text
read-only tools: allow READ
sandbox-check tools: allow check/precheck behavior
source-writing tools: require governance and sandbox; no direct ALLOW
command tools: require sandbox; no direct execution here
patch_apply: blocked or governance-gated until patch layer exists
git_status/git_diff: read-only allowed
Git write tools: blocked
network tools: blocked by default
```

## 7.3 Minimal `ModelPolicy` Fixture

The default model policy must include one local profile:

```text
model_profile_id: small_local_coder
provider_type: LOCAL
may_read_source_context: true
may_write_files: false
may_execute_tools: false
may_execute_commands: false
may_use_network: false
requires_redaction: true
requires_json_output: true
```

The default model policy must block:

```text
hosted models
networked providers
model direct file writes
model direct command execution
model direct tool execution
```

## 7.4 Minimal `RolePermissionMatrix` Fixture

The default role matrix must include all required roles and non-overridable blocks.

Required non-overridable blocks:

```text
L0_MUTATION_BLOCK
PATH_TRAVERSAL_BLOCK
SYMLINK_ESCAPE_BLOCK
MISSING_ROLLBACK_FOR_SOURCE_MUTATION
SCHEMA_INVALID_PROMOTION_EVIDENCE
UNCONTROLLED_SHELL_EXECUTION
NETWORK_IN_LOCAL_ONLY_MODE
```

## 7.5 Fixture Acceptance Rule

The implementation is not complete unless these default fixtures can be:

```text
created deterministically
serialized to dict
validated against schemas
used by PolicyRegistry
tested without network, LLM, shell, Git write, or patch execution
```


---

# 8. File-by-File Implementation Spec

---

## 4.1 `tools/agentx_evolve/policy/__init__.py`

### Purpose

Expose the public Policy / Capability Registry API.

### Required Exports

```python
from .policy_models import (
    CapabilityPolicy,
    ToolPolicy,
    ModelPolicy,
    RolePermissionMatrix,
    PolicyDecision,
    PolicyViolation,
    PolicyAudit,
)

from .policy_defaults import (
    load_default_capability_policy,
    load_default_tool_policy,
    load_default_model_policy,
    load_default_role_permission_matrix,
)

from .policy_registry import PolicyRegistry
from .policy_decision import evaluate_tool_request, evaluate_model_request, check_role_permission
from .policy_evidence import write_policy_decision, write_policy_violation
```

### Must Not Do

```text
no filesystem writes on import
no policy loading on import
no model calls
no network
no shell
```

---

## 4.2 `policy_models.py`

### Purpose

Define the shared dataclasses and constants.

### Required Decision Constants

```python
DECISION_ALLOW = "ALLOW"
DECISION_BLOCK = "BLOCK"
DECISION_WARN = "WARN"
DECISION_NEEDS_APPROVAL = "NEEDS_APPROVAL"
DECISION_NEEDS_GOVERNANCE = "NEEDS_GOVERNANCE"
DECISION_NEEDS_SANDBOX_CHECK = "NEEDS_SANDBOX_CHECK"
DECISION_NEEDS_RISK_REVIEW = "NEEDS_RISK_REVIEW"
DECISION_NEEDS_VALIDATION = "NEEDS_VALIDATION"
DECISION_UNKNOWN_ROLE = "UNKNOWN_ROLE"
DECISION_UNKNOWN_TOOL = "UNKNOWN_TOOL"
DECISION_UNKNOWN_MODEL = "UNKNOWN_MODEL"
DECISION_INVALID_POLICY = "INVALID_POLICY"
```

### Required Roles

```python
ROLE_ORCHESTRATOR = "ORCHESTRATOR"
ROLE_IMPLEMENTATION_WORKER = "IMPLEMENTATION_WORKER"
ROLE_VALIDATION_REPAIR_WORKER = "VALIDATION_REPAIR_WORKER"
ROLE_REVIEWER_ASSISTANT = "REVIEWER_ASSISTANT"
ROLE_PROMOTION_CHECKER = "PROMOTION_CHECKER"
ROLE_PATCH_EXECUTOR = "PATCH_EXECUTOR"
ROLE_TOOL_ADAPTER = "TOOL_ADAPTER"
ROLE_MODEL_ADAPTER = "MODEL_ADAPTER"
ROLE_HUMAN_OPERATOR = "HUMAN_OPERATOR"
```

### Required Effects

```python
EFFECT_READ = "READ"
EFFECT_WRITE_RUNTIME = "WRITE_RUNTIME"
EFFECT_WRITE_SOURCE = "WRITE_SOURCE"
EFFECT_EDIT_SOURCE = "EDIT_SOURCE"
EFFECT_PATCH_PRECHECK = "PATCH_PRECHECK"
EFFECT_PATCH_APPLY = "PATCH_APPLY"
EFFECT_EXECUTE_COMMAND = "EXECUTE_COMMAND"
EFFECT_USE_MODEL = "USE_MODEL"
EFFECT_USE_NETWORK = "USE_NETWORK"
EFFECT_READ_GIT = "READ_GIT"
EFFECT_WRITE_GIT = "WRITE_GIT"
EFFECT_REQUEST_APPROVAL = "REQUEST_APPROVAL"
EFFECT_PROMOTE = "PROMOTE"
EFFECT_ROLLBACK = "ROLLBACK"
EFFECT_AUDIT_WRITE = "AUDIT_WRITE"
EFFECT_GRAPH_WRITE = "GRAPH_WRITE"
EFFECT_MEMORY_WRITE = "MEMORY_WRITE"
```

### Required Trust Tiers

```python
TRUST_TIER_0_READ_ONLY = "TRUST_TIER_0_READ_ONLY"
TRUST_TIER_1_LOCAL_STATE_WRITE = "TRUST_TIER_1_LOCAL_STATE_WRITE"
TRUST_TIER_2_APPROVED_SOURCE_WRITE = "TRUST_TIER_2_APPROVED_SOURCE_WRITE"
TRUST_TIER_3_VALIDATION_EXECUTION = "TRUST_TIER_3_VALIDATION_EXECUTION"
TRUST_TIER_4_GIT_WRITE = "TRUST_TIER_4_GIT_WRITE"
TRUST_TIER_5_NETWORK_OR_EXTERNAL = "TRUST_TIER_5_NETWORK_OR_EXTERNAL"
TRUST_TIER_6_BLOCKED = "TRUST_TIER_6_BLOCKED"
```

### Required Dataclasses

#### `CapabilityEntry`

```python
@dataclass
class CapabilityEntry:
    capability_id: str
    role: str
    tool_name: str
    allowed_effects: list[str]
    blocked_effects: list[str]
    requires_approval: bool
    requires_governance: bool
    requires_sandbox: bool
    requires_risk_review: bool
    allowed_paths: list[str]
    blocked_paths: list[str]
    allowed_commands: list[str]
    allowed_model_profiles: list[str]
    notes: str = ""
```

#### `CapabilityPolicy`

```python
@dataclass
class CapabilityPolicy:
    schema_version: str
    schema_id: str
    policy_id: str
    timestamp: str
    source_component: str
    default_decision: str
    roles: list[str]
    tools: list[str]
    capabilities: list[CapabilityEntry]
    blocked_effects: list[str]
    approval_required_effects: list[str]
    governance_required_effects: list[str]
    sandbox_required_effects: list[str]
    warnings: list[str]
    errors: list[str]
```

#### `ToolEntry`

```python
@dataclass
class ToolEntry:
    tool_name: str
    tool_category: str
    trust_tier: str
    requested_effects: list[str]
    requires_governance: bool
    requires_human_approval: bool
    requires_sandbox: bool
    requires_risk_review: bool
    writes_source: bool
    writes_runtime: bool
    executes_command: bool
    uses_network: bool
    uses_model: bool
    allowlisted: bool
    blocked: bool
    notes: str = ""
```

#### `ToolPolicy`

```python
@dataclass
class ToolPolicy:
    schema_version: str
    schema_id: str
    policy_id: str
    timestamp: str
    source_component: str
    tools: list[ToolEntry]
    warnings: list[str]
    errors: list[str]
```

#### `ModelProfile`

```python
@dataclass
class ModelProfile:
    model_profile_id: str
    provider_type: str
    allowed_task_types: list[str]
    blocked_task_types: list[str]
    may_read_source_context: bool
    may_write_files: bool
    may_execute_tools: bool
    may_execute_commands: bool
    may_use_network: bool
    requires_redaction: bool
    requires_json_output: bool
    max_context_tokens: int
    requires_human_approval: bool
    notes: str = ""
```

#### `ModelPolicy`

```python
@dataclass
class ModelPolicy:
    schema_version: str
    schema_id: str
    policy_id: str
    timestamp: str
    source_component: str
    default_model_mode: str
    model_profiles: list[ModelProfile]
    warnings: list[str]
    errors: list[str]
```

#### `RolePermissionMatrix`

```python
@dataclass
class RolePermissionMatrix:
    schema_version: str
    schema_id: str
    matrix_id: str
    timestamp: str
    source_component: str
    roles: list[str]
    matrix: dict[str, dict]
    non_overridable_blocks: list[str]
    warnings: list[str]
    errors: list[str]
```

#### `PolicyDecision`

```python
@dataclass
class PolicyDecision:
    schema_version: str
    schema_id: str
    decision_id: str
    timestamp: str
    source_component: str
    caller_role: str
    tool_name: str
    requested_effect: str
    target: str | None
    decision: str
    reason: str
    applied_policy_ids: list[str]
    required_followups: list[str]
    evidence_ids: list[str]
    warnings: list[str]
    errors: list[str]
```

#### `PolicyViolation`

```python
@dataclass
class PolicyViolation:
    schema_version: str
    schema_id: str
    violation_id: str
    timestamp: str
    source_component: str
    caller_role: str
    tool_name: str
    requested_effect: str
    target: str | None
    violation_type: str
    severity: str
    reason: str
    decision_id: str | None
    warnings: list[str]
    errors: list[str]
```

#### `PolicyAudit`

```python
@dataclass
class PolicyAudit:
    schema_version: str
    schema_id: str
    audit_id: str
    timestamp: str
    source_component: str
    event_type: str
    decision_id: str
    caller_role: str
    tool_name: str
    requested_effect: str
    decision: str
    reason: str
    success: bool
    warnings: list[str]
    errors: list[str]
```

### Required Helper Functions

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
```

### Acceptance

```text
dataclasses instantiate
to_dict works recursively
constants are complete
no filesystem writes
no network
no shell
no model calls
```

---

## 4.3 `policy_defaults.py`

### Purpose

Provide deterministic default policies.

### Required Public Functions

```python
load_default_capability_policy(repo_root: Path) -> CapabilityPolicy
load_default_tool_policy(repo_root: Path) -> ToolPolicy
load_default_model_policy(repo_root: Path) -> ModelPolicy
load_default_role_permission_matrix(repo_root: Path) -> RolePermissionMatrix
```

### Default Policy Rules

```text
default decision = BLOCK
unknown role = BLOCK
unknown tool = BLOCK
unknown effect = BLOCK
unknown model = BLOCK
network = blocked
hosted model = blocked
Git write = blocked
source write = requires governance + sandbox + later patch executor
command execution = requires tool policy + sandbox
models cannot mutate files
models cannot execute commands
human cannot override L0/path/sandbox hard blocks
```

### Required Initial Tools

Read-only/local Initiator tools:

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

Future patch tools initially blocked or guarded:

```text
patch_apply
patch_rollback
patch_session_status
```

Git read-only tools:

```text
git_status
git_diff
git_diff_name_only
git_diff_stat
```

Git write tools must be blocked.

### Acceptance

```text
default objects are valid dataclass instances
default policy has BLOCK default
expected roles exist
expected tools exist
Git write blocked
network blocked
hosted model blocked
```

---

## 4.4 `role_matrix.py`

### Purpose

Represent role-level permissions and hard non-overridable blocks.

### Required Public Functions

```python
build_default_role_permission_matrix(repo_root: Path) -> RolePermissionMatrix

role_exists(role: str, matrix: RolePermissionMatrix) -> bool

get_role_permissions(role: str, matrix: RolePermissionMatrix) -> dict

is_non_overridable_block(block_name: str, matrix: RolePermissionMatrix) -> bool
```

### Required Role Matrix

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

### Non-Overridable Blocks

```text
L0_MUTATION_BLOCK
PATH_TRAVERSAL_BLOCK
SYMLINK_ESCAPE_BLOCK
MISSING_ROLLBACK_FOR_SOURCE_MUTATION
SCHEMA_INVALID_PROMOTION_EVIDENCE
UNCONTROLLED_SHELL_EXECUTION
NETWORK_IN_LOCAL_ONLY_MODE
```

### Acceptance

```text
all roles exist
unknown role false
human operator cannot override non-overridable blocks
matrix schema-valid
```

---

## 4.5 `capability_policy.py`

### Purpose

Load and evaluate role/tool/effect capabilities.

### Required Public Functions

```python
find_capability(
    role: str,
    tool_name: str,
    capability_policy: CapabilityPolicy
) -> CapabilityEntry | None

is_effect_allowed(
    effect: str,
    capability: CapabilityEntry,
    capability_policy: CapabilityPolicy
) -> bool

is_effect_blocked(
    effect: str,
    capability: CapabilityEntry | None,
    capability_policy: CapabilityPolicy
) -> bool

capability_requires_approval(effect: str, capability: CapabilityEntry, capability_policy: CapabilityPolicy) -> bool

capability_requires_governance(effect: str, capability: CapabilityEntry, capability_policy: CapabilityPolicy) -> bool

capability_requires_sandbox(effect: str, capability: CapabilityEntry, capability_policy: CapabilityPolicy) -> bool
```

### Rules

```text
unknown role blocks
unknown tool blocks
unknown effect blocks
default decision blocks
blocked_effects wins over allowed_effects
global blocked effects win over entry allowed effects
WRITE_SOURCE requires governance and sandbox
PATCH_APPLY requires governance, sandbox, rollback
EXECUTE_COMMAND requires sandbox
USE_NETWORK requires explicit policy
```

### Acceptance

```text
unknown role blocks
unknown tool blocks
unknown effect blocks
WRITE_SOURCE returns requires governance/sandbox
PATCH_APPLY returns requires governance/sandbox/rollback
```

---

## 4.6 `tool_policy.py`

### Purpose

Load and evaluate tool metadata.

### Required Public Functions

```python
find_tool(tool_name: str, tool_policy: ToolPolicy) -> ToolEntry | None

tool_exists(tool_name: str, tool_policy: ToolPolicy) -> bool

tool_is_blocked(tool_name: str, tool_policy: ToolPolicy) -> bool

tool_allows_effect(tool_name: str, effect: str, tool_policy: ToolPolicy) -> bool

tool_requires_governance(tool_name: str, tool_policy: ToolPolicy) -> bool

tool_requires_sandbox(tool_name: str, tool_policy: ToolPolicy) -> bool

tool_requires_human_approval(tool_name: str, tool_policy: ToolPolicy) -> bool

tool_uses_network(tool_name: str, tool_policy: ToolPolicy) -> bool

tool_executes_command(tool_name: str, tool_policy: ToolPolicy) -> bool

tool_writes_source(tool_name: str, tool_policy: ToolPolicy) -> bool
```

### Rules

```text
blocked tool always blocks
unknown tool blocks
tool requested effect must be listed in requested_effects
TRUST_TIER_6_BLOCKED always blocks
WRITE_GIT blocked in v1
USE_NETWORK blocked in v1 unless explicit future policy says otherwise
```

### Acceptance

```text
read-only tools allow READ
source-write tools require governance/sandbox
command tools require sandbox
network tools blocked by default
Git write tools blocked initially
```

---

## 4.7 `model_policy.py`

### Purpose

Load and evaluate model profile permissions.

### Required Public Functions

```python
find_model_profile(model_profile_id: str, model_policy: ModelPolicy) -> ModelProfile | None

model_profile_exists(model_profile_id: str, model_policy: ModelPolicy) -> bool

model_task_allowed(model_profile_id: str, task_type: str, model_policy: ModelPolicy) -> bool

model_may_read_source(model_profile_id: str, model_policy: ModelPolicy) -> bool

model_may_write_files(model_profile_id: str, model_policy: ModelPolicy) -> bool

model_may_execute_tools(model_profile_id: str, model_policy: ModelPolicy) -> bool

model_may_execute_commands(model_profile_id: str, model_policy: ModelPolicy) -> bool

model_may_use_network(model_profile_id: str, model_policy: ModelPolicy) -> bool
```

### Rules

```text
unknown model blocks
local_only default
hosted models blocked by default
models cannot write files
models cannot execute commands
models cannot directly execute tools
models require redaction
models require JSON output where configured
```

### Acceptance

```text
unknown model blocks
hosted model blocked by default
model cannot write files
model cannot execute commands
local model profile exists
```

---

## 4.8 `policy_decision.py`

### Purpose

Return policy decisions for tool/model/role requests.

### Required Public Functions

```python
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

choose_strictest_decision(decisions: list[PolicyDecision]) -> PolicyDecision
```

### Decision Precedence

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

### Evaluation Logic for Tool Request

Order:

```text
1. Validate policy objects.
2. Unknown role -> UNKNOWN_ROLE.
3. Unknown tool -> UNKNOWN_TOOL.
4. Blocked tool -> BLOCK.
5. Unknown effect -> BLOCK.
6. Tool does not allow effect -> BLOCK.
7. Capability missing -> BLOCK.
8. Capability blocks effect -> BLOCK.
9. If human approval required -> NEEDS_APPROVAL.
10. If governance required -> NEEDS_GOVERNANCE.
11. If sandbox required -> NEEDS_SANDBOX_CHECK.
12. If risk review required -> NEEDS_RISK_REVIEW.
13. Else ALLOW.
```

### Evaluation Logic for Model Request

Order:

```text
1. Validate model policy.
2. Unknown role -> UNKNOWN_ROLE.
3. Unknown model -> UNKNOWN_MODEL.
4. Hosted/network model while local_only -> BLOCK.
5. Task type blocked -> BLOCK.
6. Model writes files -> BLOCK.
7. Model executes commands -> BLOCK.
8. Model executes tools directly -> BLOCK.
9. If human approval required -> NEEDS_APPROVAL.
10. Else ALLOW.
```

### Required Reasons

Each decision must include a stable reason string, for example:

```text
UNKNOWN_ROLE
UNKNOWN_TOOL
TOOL_BLOCKED
EFFECT_NOT_ALLOWED
CAPABILITY_MISSING
REQUIRES_GOVERNANCE
REQUIRES_SANDBOX
REQUIRES_APPROVAL
MODEL_CANNOT_WRITE_FILES
HOSTED_MODEL_BLOCKED_BY_DEFAULT
ALLOW_BY_CAPABILITY
```

### Acceptance

```text
decision is schema-aligned
strictest decision wins
reasons are stable
warnings/errors populated
```

---

## 4.9 `policy_registry.py`

### Purpose

Provide the high-level facade for loading policies and evaluating requests.

### Required Class

```python
class PolicyRegistry:
    def __init__(
        self,
        repo_root: Path,
        capability_policy: CapabilityPolicy | None = None,
        tool_policy: ToolPolicy | None = None,
        model_policy: ModelPolicy | None = None,
        role_matrix: RolePermissionMatrix | None = None,
    ): ...

    def evaluate_tool_request(
        self,
        caller_role: str,
        tool_name: str,
        requested_effect: str,
        target: str | None = None
    ) -> PolicyDecision: ...

    def evaluate_model_request(
        self,
        caller_role: str,
        model_profile_id: str,
        task_type: str
    ) -> PolicyDecision: ...

    def write_decision(self, decision: PolicyDecision) -> dict: ...

    def get_role_matrix(self) -> RolePermissionMatrix: ...

    def get_tool_policy(self) -> ToolPolicy: ...

    def get_model_policy(self) -> ModelPolicy: ...

    def get_capability_policy(self) -> CapabilityPolicy: ...
```

### Rules

```text
defaults loaded when explicit policies not provided
no execution of tools
no model calls
no network
no shell
write_decision delegates to policy_evidence
```

### Acceptance

```text
PolicyRegistry can evaluate known read-only tool request
PolicyRegistry blocks unknown tool
PolicyRegistry blocks source write without governance/sandbox followups
```

---

## 4.10 `initiator_policy_compat.py`

### Purpose

Integrate with the completed Initiator without tight coupling.

### Required Class

```python
class InitiatorPolicyCompat:
    def __init__(self, repo_root: Path | None = None): ...

    def get_repo_root(self) -> Path: ...

    def get_policy_runtime_root(self) -> Path: ...

    def validate_schema(self, artifact: dict, schema_id: str) -> dict: ...

    def write_json_atomic(self, path: Path, artifact: dict) -> dict: ...

    def append_audit_event(self, event: dict) -> dict: ...
```

### Import Strategy

Try package imports:

```python
from agentx_initiator.core import schema_validation
from agentx_initiator.core import artifact_io
from agentx_initiator.core import audit_log
from agentx_initiator.core import path_registry
```

If unavailable:

```text
record INITIATOR_POLICY_INTEGRATION_FAILED
fall back only to deterministic local JSON write/append where safe
do not pretend schema validation passed
do not pretend audit integration succeeded
```

### Acceptance

```text
imports succeed when Initiator installed
fallback records integration failure
runtime root resolves to .agentx-init/policies
does not modify Initiator source
```

---

## 4.11 `policy_evidence.py`

### Purpose

Write policy decisions, violations, latest artifacts, and audit events.

### Required Public Functions

```python
append_policy_decision(
    decision: PolicyDecision,
    repo_root: Path,
    compat: InitiatorPolicyCompat | None = None
) -> dict

append_policy_violation(
    violation: PolicyViolation,
    repo_root: Path,
    compat: InitiatorPolicyCompat | None = None
) -> dict

write_latest_policy_decision(
    decision: PolicyDecision,
    repo_root: Path,
    compat: InitiatorPolicyCompat | None = None
) -> dict

build_policy_audit_event(
    decision: PolicyDecision
) -> PolicyAudit

write_policy_decision(
    decision: PolicyDecision,
    repo_root: Path
) -> dict
```

### Runtime Paths

```text
.agentx-init/policies/policy_decisions.jsonl
.agentx-init/policies/policy_violations.jsonl
.agentx-init/policies/latest_policy_decision.json
.agentx-init/policies/latest_policy_violation.json
.agentx-init/memory/audit_events.jsonl
```

### Rules

```text
create .agentx-init/policies if needed
append JSONL only
write latest JSON atomically
do not overwrite valid latest with invalid
redact sensitive targets
do not write secrets
```

### Acceptance

```text
decision appended
violation appended
latest decision atomic write
audit event built
malformed existing JSONL preserved
```

---

# 9. Schema Implementation Spec

Use the same JSON Schema draft convention already used by `tools/agentx_evolve/schemas/`.

Create:

```text
capability_policy.schema.json
tool_policy.schema.json
model_policy.schema.json
role_permission_matrix.schema.json
policy_decision.schema.json
policy_violation.schema.json
policy_audit.schema.json
```

Each schema must require:

```text
schema_version
schema_id
timestamp
source_component
warnings
errors
```

## 5.1 `capability_policy.schema.json`

Required fields:

```text
schema_version
schema_id
policy_id
timestamp
source_component
default_decision
roles
tools
capabilities
blocked_effects
approval_required_effects
governance_required_effects
sandbox_required_effects
warnings
errors
```

## 5.2 `tool_policy.schema.json`

Required fields:

```text
schema_version
schema_id
policy_id
timestamp
source_component
tools
warnings
errors
```

Tool entries require:

```text
tool_name
tool_category
trust_tier
requested_effects
requires_governance
requires_human_approval
requires_sandbox
requires_risk_review
writes_source
writes_runtime
executes_command
uses_network
uses_model
allowlisted
blocked
notes
```

## 5.3 `model_policy.schema.json`

Required fields:

```text
schema_version
schema_id
policy_id
timestamp
source_component
default_model_mode
model_profiles
warnings
errors
```

Model profile entries require:

```text
model_profile_id
provider_type
allowed_task_types
blocked_task_types
may_read_source_context
may_write_files
may_execute_tools
may_execute_commands
may_use_network
requires_redaction
requires_json_output
max_context_tokens
requires_human_approval
notes
```

## 5.4 `role_permission_matrix.schema.json`

Required fields:

```text
schema_version
schema_id
matrix_id
timestamp
source_component
roles
matrix
non_overridable_blocks
warnings
errors
```

## 5.5 `policy_decision.schema.json`

Required fields:

```text
schema_version
schema_id
decision_id
timestamp
source_component
caller_role
tool_name
requested_effect
target
decision
reason
applied_policy_ids
required_followups
evidence_ids
warnings
errors
```

Allowed decisions:

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

## 5.6 `policy_violation.schema.json`

Required fields:

```text
schema_version
schema_id
violation_id
timestamp
source_component
caller_role
tool_name
requested_effect
target
violation_type
severity
reason
decision_id
warnings
errors
```

## 5.7 `policy_audit.schema.json`

Required fields:

```text
schema_version
schema_id
audit_id
timestamp
source_component
event_type
decision_id
caller_role
tool_name
requested_effect
decision
reason
success
warnings
errors
```

---

# 10. v1 Boundary vs Future Expansion

## 9.1 Required v1 Behavior

The first implementation must support:

```text
deterministic default policies
role/tool/effect/model lookup
policy decision evaluation
policy evidence writing
schema validation for policy artifacts
sandbox follow-up requirements
Initiator compatibility bridge
negative tests
fresh-clone validation
```

## 9.2 Explicitly Future Behavior

Do not implement in v1:

```text
dynamic policy learning
policy auto-rewriting
MCP tool exposure
actual command execution
actual model execution
actual patch application
Git write operations
human approval UI
remote provider auth
plugin loading
network allowlist execution
```

Future layers may consume policy decisions, but this layer only creates and evaluates policy.

## 9.3 Schema Validation Expectations

The following must validate against schemas:

```text
default CapabilityPolicy
default ToolPolicy
default ModelPolicy
default RolePermissionMatrix
ALLOW PolicyDecision
BLOCK PolicyDecision
UNKNOWN_ROLE PolicyDecision
UNKNOWN_TOOL PolicyDecision
UNKNOWN_MODEL PolicyDecision
NEEDS_GOVERNANCE PolicyDecision
NEEDS_SANDBOX_CHECK PolicyDecision
PolicyViolation
PolicyAudit
```

The following must be rejected by schemas:

```text
policy decision missing decision_id
policy decision missing caller_role
policy decision with invalid decision enum
tool policy missing trust_tier
model policy missing may_write_files
capability policy missing default_decision
role matrix missing non_overridable_blocks
```


---

# 11. Integration With Security Sandbox

The Policy / Capability Registry must integrate with the validated sandbox by policy reference, not by reimplementing sandbox logic.

Use sandbox concepts:

```text
NEEDS_SANDBOX_CHECK
requires_sandbox
EXECUTE_COMMAND requires sandbox
WRITE_SOURCE requires sandbox
PATCH_APPLY requires sandbox
USE_NETWORK requires sandbox/network policy
```

Do not duplicate:

```text
path traversal checks
symlink checks
L0 path checks
safe file operation logic
safe subprocess logic
secret redaction logic
network boundary logic
```

The sandbox remains the authority for physical filesystem/command/network safety.

The policy layer remains the authority for caller/tool/effect permission.

Strictest result wins:

```text
Policy ALLOW + Sandbox BLOCK = BLOCK
Policy BLOCK + Sandbox ALLOW = BLOCK
Policy NEEDS_SANDBOX_CHECK = caller must obtain sandbox decision before execution
```

---

# 12. Integration With Initiator

The Policy / Capability Registry should use `InitiatorPolicyCompat` to integrate with:

```text
schema_validation
artifact_io
audit_log
path_registry
```

It may reference future governance/risk artifacts, but must not replace:

```text
governance_engine
risk_engine
validation_runner
knowledge_graph
memory_store
```

Required behavior:

```text
if schema validation available, use it
if artifact_io available, use it for atomic writes
if audit_log available, append audit events
if integration unavailable, record failure and use deterministic fallback where safe
do not fake integration success
```

---

# 13. OpenCode-Inspired Implementation Notes

Borrow:

```text
tool registry concept
conditional tool exposure
tool metadata
permission checks before tool use
fail-closed invalid-tool behavior
model/provider routing concept
```

Do not borrow:

```text
OpenCode source code
Bun/TypeScript dependency
broad shell availability
network fetch/search defaults
plugin execution defaults
subagent execution assumptions
UI/product permission model
```

OpenCode mapping:

```text
tool registry -> PolicyRegistry + ToolPolicy
invalid tool -> UNKNOWN_TOOL / BLOCK
shell permission scan -> EXECUTE_COMMAND requires policy + sandbox
custom plugin -> blocked unless registered
provider routing -> ModelPolicy
```

---

# 14. Stable Reason Codes and Failure Classes

## 12.1 Required Reason Codes

Policy decisions must use stable reason strings so tests, evidence, and downstream layers can rely on consistent meanings.

Required reason codes:

```text
ALLOW_BY_CAPABILITY
DEFAULT_BLOCK
UNKNOWN_ROLE
UNKNOWN_TOOL
UNKNOWN_EFFECT
UNKNOWN_MODEL
INVALID_POLICY
TOOL_BLOCKED
TOOL_EFFECT_NOT_ALLOWED
CAPABILITY_MISSING
CAPABILITY_EFFECT_BLOCKED
REQUIRES_APPROVAL
REQUIRES_GOVERNANCE
REQUIRES_SANDBOX
REQUIRES_RISK_REVIEW
REQUIRES_VALIDATION
NETWORK_BLOCKED_BY_DEFAULT
HOSTED_MODEL_BLOCKED_BY_DEFAULT
MODEL_CANNOT_WRITE_FILES
MODEL_CANNOT_EXECUTE_COMMANDS
MODEL_CANNOT_EXECUTE_TOOLS
GIT_WRITE_BLOCKED_BY_DEFAULT
HUMAN_CANNOT_OVERRIDE_HARD_BLOCK
SANDBOX_BLOCK_IS_AUTHORITATIVE
```

## 12.2 Required Failure Classes

Policy violations should use these failure classes where applicable:

```text
UNKNOWN_ROLE_VIOLATION
UNKNOWN_TOOL_VIOLATION
UNKNOWN_MODEL_VIOLATION
UNKNOWN_EFFECT_VIOLATION
POLICY_SCHEMA_INVALID
POLICY_RUNTIME_WRITE_FAILED
EVIDENCE_WRITE_FAILED
TOOL_BLOCKED_BY_POLICY
EFFECT_BLOCKED_BY_POLICY
MISSING_GOVERNANCE
MISSING_SANDBOX_CHECK
MISSING_APPROVAL
MODEL_PERMISSION_DENIED
NETWORK_PERMISSION_DENIED
GIT_WRITE_DENIED
HARD_BLOCK_OVERRIDE_ATTEMPT
INITIATOR_POLICY_INTEGRATION_FAILED
```

## 12.3 High-Risk Request Expected Outcomes

| Request | Expected decision | Required reason |
|---|---|---|
| Unknown role requests READ | `UNKNOWN_ROLE` | `UNKNOWN_ROLE` |
| Known role requests unknown tool | `UNKNOWN_TOOL` | `UNKNOWN_TOOL` |
| Known role/tool requests unknown effect | `BLOCK` | `UNKNOWN_EFFECT` |
| `ORCHESTRATOR` requests `agentx_scan` with `READ` | `ALLOW` | `ALLOW_BY_CAPABILITY` |
| `IMPLEMENTATION_WORKER` requests `safe_write_file` with `WRITE_SOURCE` | `BLOCK` or `NEEDS_GOVERNANCE`; never direct `ALLOW` | `REQUIRES_GOVERNANCE` or `CAPABILITY_EFFECT_BLOCKED` |
| `PATCH_EXECUTOR` requests `patch_apply` before patch layer exists | `BLOCK` or `NEEDS_GOVERNANCE`; never direct `ALLOW` | `REQUIRES_GOVERNANCE` |
| `TOOL_ADAPTER` requests `check_subprocess_allowed` with `EXECUTE_COMMAND` | `NEEDS_SANDBOX_CHECK` or `BLOCK`; must not bypass sandbox | `REQUIRES_SANDBOX` |
| Hosted model request in `local_only` mode | `BLOCK` | `HOSTED_MODEL_BLOCKED_BY_DEFAULT` |
| Model direct file write | `BLOCK` | `MODEL_CANNOT_WRITE_FILES` |
| Git write request | `BLOCK` | `GIT_WRITE_BLOCKED_BY_DEFAULT` |
| Human override of L0 block | `BLOCK` | `HUMAN_CANNOT_OVERRIDE_HARD_BLOCK` |

---

# 15. Dependency, Import, and Determinism Contract

## 13.1 Allowed Dependencies

Use the standard library first.

Allowed standard library imports:

```text
pathlib
json
dataclasses
typing
datetime
uuid
enum
hashlib
tempfile
os
re
```

Allowed Agent_X imports:

```text
agentx_evolve.security
agentx_initiator.core.schema_validation
agentx_initiator.core.artifact_io
agentx_initiator.core.audit_log
agentx_initiator.core.path_registry
```

Conditionally allowed:

```text
jsonschema
```

only if it is already used in the project or accepted by the current Agent_X dependency policy.

Forbidden in this layer:

```text
requests
httpx
urllib network execution
subprocess execution
LLM/model clients
MCP server/client runtime
Git write helpers
OpenCode runtime
Bun
Node
```

## 13.2 Import Style

Repository-relative files live under:

```text
tools/agentx_evolve/policy/
```

Runtime imports should use package names:

```python
from agentx_evolve.policy.policy_registry import PolicyRegistry
from agentx_evolve.policy.policy_decision import evaluate_tool_request
from agentx_initiator.core import schema_validation
```

Do not use this as the default implementation import style:

```python
from tools.agentx_evolve.policy.policy_registry import PolicyRegistry
```

Tests may use:

```bash
PYTHONPATH=tools
```

## 13.3 Determinism and No-Side-Effect Contract

For the same input policies and request, the same policy decision must be returned.

Required behavior:

```text
deterministic rule order
deterministic precedence order
stable reason codes
no random decisions
no filesystem writes during pure evaluation
no shell calls
no network calls
no model calls
no Git calls
```

Pure functions:

```text
evaluate_tool_request
evaluate_model_request
check_role_permission
choose_strictest_decision
find_capability
find_tool
find_model_profile
```

Side-effect functions:

```text
write_policy_decision
append_policy_decision
append_policy_violation
write_latest_policy_decision
```

## 13.4 JSONL Evidence Recovery Rules

Evidence writing must preserve existing history.

Rules:

```text
append one JSON object per line
preserve malformed existing JSONL lines
record malformed JSONL line as warning/evidence instead of deleting it
never rewrite existing JSONL history
write latest JSON atomically
fail closed if latest policy artifact cannot be written
do not overwrite a valid latest artifact with an invalid artifact
```


---

# 16. Test Implementation Plan

## 9.1 Fixtures

Create fixtures:

```python
@pytest.fixture
def temp_repo(tmp_path): ...

@pytest.fixture
def default_capability_policy(temp_repo): ...

@pytest.fixture
def default_tool_policy(temp_repo): ...

@pytest.fixture
def default_model_policy(temp_repo): ...

@pytest.fixture
def default_role_matrix(temp_repo): ...

@pytest.fixture
def policy_registry(temp_repo): ...
```

`temp_repo` should include:

```text
repo/
  .agentx-init/
    policies/
    memory/
  tools/
    agentx_evolve/
      security/
```

## 9.2 Capability Policy Tests

```text
test_default_policy_blocks_unknown_role
test_default_policy_blocks_unknown_tool
test_default_policy_blocks_unknown_effect
test_orchestrator_can_call_readonly_initiator_tool
test_implementation_worker_cannot_write_file
test_patch_executor_requires_governance_for_source_write
test_human_operator_cannot_override_l0_block_marker
```

## 9.3 Tool Policy Tests

```text
test_tool_policy_defines_trust_tiers
test_readonly_tool_has_readonly_effect
test_source_write_tool_requires_governance_and_sandbox
test_command_tool_requires_allowlist_and_sandbox
test_network_tool_blocked_by_default
test_git_write_tool_blocked_initially
```

## 9.4 Model Policy Tests

```text
test_local_only_default
test_hosted_model_blocked_by_default
test_model_cannot_write_files
test_model_cannot_execute_commands
test_model_requires_json_output_when_configured
test_unknown_model_blocks
```

## 9.5 Role Matrix Tests

```text
test_all_required_roles_exist
test_unknown_role_false
test_human_operator_cannot_override_non_overridable_blocks
test_patch_executor_has_no_governance_bypass
```

## 9.6 Decision Tests

```text
test_policy_decision_schema_accepts_valid_decision
test_decision_precedence_block_over_allow
test_unknown_role_decision
test_unknown_tool_decision
test_unknown_model_decision
test_needs_approval_decision
test_needs_governance_decision
test_needs_sandbox_check_decision
```

## 9.7 Registry Tests

```text
test_registry_loads_defaults
test_registry_allows_orchestrator_readonly_scan
test_registry_blocks_unknown_tool
test_registry_blocks_model_direct_file_write
test_registry_blocks_git_write
```

## 9.8 Evidence Tests

```text
test_policy_decision_appended_to_jsonl
test_policy_violation_appended_to_jsonl
test_latest_policy_decision_written_atomically
test_invalid_policy_does_not_replace_latest
test_policy_audit_redacts_sensitive_target
```

## 9.9 Schema Tests

```text
test_capability_policy_schema_accepts_valid_policy
test_tool_policy_schema_accepts_valid_policy
test_model_policy_schema_accepts_valid_policy
test_role_permission_matrix_schema_accepts_valid_matrix
test_policy_decision_schema_accepts_valid_decision
test_policy_violation_schema_accepts_valid_violation
test_policy_audit_schema_accepts_valid_audit
test_policy_decision_schema_rejects_missing_required_fields
```

## 9.10 Negative Tests

```text
test_unknown_role_never_allows
test_unknown_tool_never_allows
test_unknown_model_never_allows
test_write_source_never_allows_without_governance
test_execute_command_never_allows_without_sandbox
test_network_never_allows_by_default
test_model_never_gets_direct_file_write
test_allow_cannot_override_sandbox_block
```

## 9.11 Sandbox Integration Tests

```text
test_policy_decision_needs_sandbox_for_source_write
test_policy_decision_needs_sandbox_for_command_execution
test_policy_decision_needs_sandbox_for_network_use
test_policy_does_not_reimplement_path_boundary
```

## 9.12 Initiator Integration Tests

```text
test_policy_compat_imports_schema_validation
test_policy_compat_imports_artifact_io
test_policy_compat_imports_audit_log
test_policy_compat_records_integration_failure
test_policy_compat_does_not_modify_initiator_source
```

---

# 17. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/policy
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_capability_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_tool_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_model_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_role_matrix.py
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

Required result:

```text
compileall PASS
pytest PASS
git status clean except expected runtime artifacts
```

No command may require:

```text
GPU
LLM
network
hosted model
Bun
Node
OpenCode runtime
```

---

# 18. Runtime Artifact Rules

All policy runtime artifacts go under:

```text
.agentx-init/policies/
```

Rules:

```text
create directory if missing
append JSONL only for decision/violation history
write latest JSON atomically
do not overwrite valid latest artifact with invalid artifact
do not write secrets
do not write outside .agentx-init/policies except approved audit event under .agentx-init/memory/audit_events.jsonl
preserve malformed existing JSONL lines
record malformed JSONL line as warning/evidence instead of deleting it
fail closed if latest policy artifact cannot be written
```

---

# 19. Coding Constraints

The coding LLM must not:

```text
implement MCP server
execute tools
execute commands
call models
apply patches
write source files as part of policy evaluation
enable network
enable Git write
modify Security Sandbox internals
modify Initiator internals unnecessarily
copy OpenCode source code
add Bun/Node/OpenCode runtime dependency
```

Allowed implementation:

```text
dataclasses
standard library
jsonschema only if already used by project
pytest
schema JSON files
deterministic local file writes for policy evidence
```

---

# 20. Implementation Drift Blockers

Reject the implementation if it does any of the following:

```text
places files outside tools/agentx_evolve/policy/ without recorded deviation
executes tools instead of only deciding policy
executes shell commands
calls models
applies patches
runs Git write operations
enables network by default
allows hosted models by default
allows source writes without governance and sandbox
lets human operator override L0/path/sandbox hard blocks
modifies tools/agentx_evolve/security/ internals unnecessarily
modifies tools/agentx_initiator/ internals unnecessarily
copies OpenCode source code
adds Bun, Node, or OpenCode runtime dependencies
writes policy artifacts outside .agentx-init/policies/
```

Allowed fixes during implementation:

```text
add dataclasses
add schemas
add deterministic default policies
add policy decision evaluator
add evidence writer
add tests
add Initiator compatibility adapter
add Security Sandbox integration checks
```

---

# 21. Fresh-Clone Validation Gate

Final validation must be run from a clean checkout.

Required commands:

```bash
git clone <repo-url> Agent_X_policy_check
cd Agent_X_policy_check
git checkout <policy-registry-commit>

PYTHONPATH=tools python -m compileall tools/agentx_evolve/policy
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_capability_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_tool_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_model_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_role_matrix.py
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

Required result:

```text
compileall PASS
all policy tests PASS
full relevant test suite PASS
git status clean except expected runtime artifacts
```


---

# 22. Acceptance Criteria

The implementation is complete only if:

```text
all target files exist
all target schemas exist
all target tests exist
public API matches this spec
default policy blocks unknown role/tool/effect/model
role matrix exists
tool policy exists
model policy exists
policy decisions schema-valid
policy evidence written
source write requires governance and sandbox
command execution requires sandbox
network blocked by default
hosted model blocked by default
Git write blocked by default
models cannot directly mutate files
human operator cannot override non-overridable blocks
sandbox integration tests pass
Initiator integration tests pass or fail closed as designed
compileall passes
pytest passes
git status clean except expected runtime artifacts
```

---

# 23. Definition of Done

The Policy / Capability Registry is done when the following command set passes from a fresh checkout:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/policy
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
git status --short
```

And test evidence confirms:

```text
unknown roles block
unknown tools block
unknown effects block
unknown models block
default decision is BLOCK
OpenCode-style tool registry concept is represented safely
source write requires governance and sandbox
patch apply requires governance, sandbox, rollback, and patch executor
command execution requires sandbox and allowlist
network is blocked by default
hosted models are blocked by default
models cannot write files
models cannot execute commands
Git write is blocked by default
human operator cannot override hard sandbox blocks
policy decisions are written as evidence
latest policy decision is written atomically
Agent_X Initiator integration works or fails closed
Security Sandbox integration is respected
```

Completion evidence must be written to:

```text
.agentx-init/policies/policy_capability_registry_completion_record.json
```

---

# 24. Completion Evidence Record

Write this after validation:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_POLICY_CAPABILITY_REGISTRY",
  "component_name": "Policy / Capability Registry",
  "status": "VALIDATED",
  "validated_commit": "<commit>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/policy/",
  "basis_documents": [
    "POLICY_CAPABILITY_REGISTRY_EQC_FIC_SIB_SCHEMA_CONTRACT_v1",
    "POLICY_CAPABILITY_REGISTRY_IMPLEMENTATION_SPEC_v1"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "opencode_patterns_borrowed": [
    "tool registry mapped to PolicyRegistry and ToolPolicy",
    "conditional tool exposure mapped to evaluate_tool_request",
    "invalid-tool behavior mapped to UNKNOWN_TOOL / BLOCK",
    "model/provider routing concept mapped to ModelPolicy"
  ],
  "opencode_patterns_rejected_or_restricted": [
    "no OpenCode source copied",
    "no Bun dependency added",
    "no Node dependency added",
    "no broad shell availability",
    "no network fetch/search by default",
    "no plugin execution by default"
  ],
  "agentx_integration_points_verified": [
    "Security Sandbox integration",
    "Initiator schema validation integration",
    "Initiator artifact writing integration",
    "Initiator audit log integration"
  ],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

---

# 25. Final Implementation Sequence

Use this exact order:

```text
1. Create tools/agentx_evolve/policy/ package.
2. Create policy_models.py.
3. Create schemas.
4. Create policy_defaults.py.
5. Create role_matrix.py.
6. Create capability_policy.py.
7. Create tool_policy.py.
8. Create model_policy.py.
9. Create policy_decision.py.
10. Create policy_registry.py.
11. Create initiator_policy_compat.py.
12. Create policy_evidence.py.
13. Create tests.
14. Run compileall.
15. Run pytest.
16. Fix failures without weakening safety.
17. Generate completion record.
18. Report final evidence.
```

---

# 26. GO / NO-GO Criteria

## 20.1 GO Criteria

The Policy / Capability Registry may be marked DONE only if:

```text
all files exist under tools/agentx_evolve/policy/
all schemas exist
all tests exist
compileall passes
pytest passes
unknown role blocks
unknown tool blocks
unknown model blocks
unknown effect blocks
default decision is BLOCK
source write requires governance and sandbox
command execution requires sandbox
network blocked by default
hosted model blocked by default
Git write blocked by default
human operator cannot override hard sandbox blocks
policy decisions are evidence-backed
latest decision is written atomically
Security Sandbox integration tests pass
Initiator integration tests pass or fail closed as designed
git status clean except expected runtime artifacts
completion record written
```

## 20.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
compileall fails
any required policy test fails
unknown role/tool/model can ALLOW
source write can proceed without governance and sandbox
shell/command execution can proceed without sandbox
network enabled by default
hosted model enabled by default
Git write enabled by default
human operator can override L0/path/sandbox hard block
policy decisions are not schema-valid
policy evidence is not written
runtime artifacts written outside .agentx-init/policies/
Security Sandbox or Initiator source is unnecessarily modified
OpenCode/Bun/Node runtime dependency is added
```

---

# 27. Coding LLM Handoff Checklist

Before giving this spec to a coding LLM, confirm:

```text
[ ] Target component is Policy / Capability Registry.
[ ] Canonical subdirectory is tools/agentx_evolve/policy/.
[ ] Security Sandbox is already validated and must not be reimplemented.
[ ] Agent_X Initiator is already completed and must not be forked.
[ ] OpenCode is a design reference only.
[ ] No OpenCode source code should be copied.
[ ] This layer decides policy only; it does not execute tools.
[ ] Runtime artifacts go under .agentx-init/policies/.
[ ] Default decision is BLOCK.
[ ] Unknown role/tool/effect/model blocks.
[ ] Network, hosted models, Git write, command execution, and source write are blocked or gated by default.
```


---

# 28. Patch-Execution Dependency Gate

Governed Patch Execution must not be implemented or used for live mutation until this layer is validated.

Required gate:

```text
Policy / Capability Registry: VALIDATED
Security Sandbox / Filesystem Boundary: VALIDATED
unknown role/tool/model/effect blocks
source write requires governance and sandbox
patch apply requires governance, sandbox, rollback, and patch executor
policy decisions are evidence-backed
```

If this layer is not validated, the next layer may only be planned or documented. It must not perform live source mutation.

---

# 29. Final Fresh-Handoff Checklist

Before coding begins, confirm:

```text
[ ] Policy layer location is tools/agentx_evolve/policy/.
[ ] Runtime artifacts go under .agentx-init/policies/.
[ ] Security Sandbox is already validated and is not reimplemented here.
[ ] Initiator is completed and is not forked here.
[ ] This layer decides only; it does not execute.
[ ] Default decision is BLOCK.
[ ] Unknown role/tool/effect/model blocks.
[ ] Source write requires governance and sandbox.
[ ] Network is blocked by default.
[ ] Hosted models are blocked by default.
[ ] Git write is blocked by default.
[ ] Human cannot override hard sandbox blocks.
[ ] OpenCode is used only as a conceptual reference.
[ ] No Bun/Node/OpenCode runtime dependency is added.
```


---

# 30. Final Validation Scoreboard

The implementation is accepted only if this scoreboard is fully green.

| Area | Required result |
|---|---|
| File placement | All files under `tools/agentx_evolve/policy/` |
| Schemas | All required policy schemas exist and validate fixtures |
| Imports | Package imports work with `PYTHONPATH=tools` |
| Compile | `compileall tools/agentx_evolve/policy` passes |
| Tests | All policy tests pass |
| Unknown role/tool/effect/model | All block or return unknown decisions |
| Default decision | `BLOCK` |
| Source write | Requires governance and sandbox |
| Command execution | Requires sandbox and allowlist |
| Network | Blocked by default |
| Hosted models | Blocked by default |
| Git write | Blocked by default |
| Human override | Cannot override hard sandbox blocks |
| Evidence | Decisions/violations append JSONL and latest writes atomically |
| Recovery | Malformed JSONL preserved |
| Integration | Sandbox and Initiator integration pass or fail closed |
| Side effects | Pure evaluation functions do not write files or execute anything |
| OpenCode borrowing | Conceptual only; no source copied; no Bun/Node dependency |
| Git status | Clean except expected runtime artifacts |
| Completion record | Written under `.agentx-init/policies/` |

If any row fails, the layer is not done.


---

# 31. Final Closeout Evidence Format

After implementation passes validation, create:

```text
.agentx-init/policies/policy_capability_registry_completion_record.json
```

Use this evidence format:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_POLICY_CAPABILITY_REGISTRY",
  "component_name": "Policy / Capability Registry",
  "status": "VALIDATED",
  "validated_commit": "<commit>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/policy/",
  "basis_documents": [
    "POLICY_CAPABILITY_REGISTRY_EQC_FIC_SIB_SCHEMA_CONTRACT_v1",
    "POLICY_CAPABILITY_REGISTRY_IMPLEMENTATION_SPEC_v5"
  ],
  "commands_run": [
    {
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve/policy",
      "status": "PASS",
      "evidence_summary": "<compileall summary>"
    },
    {
      "command": "PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests",
      "status": "PASS",
      "evidence_summary": "<pytest summary>"
    },
    {
      "command": "git status --short",
      "status": "PASS",
      "evidence_summary": "No unexpected source mutation after validation."
    }
  ],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [
    "unknown roles block",
    "unknown tools block",
    "unknown effects block",
    "unknown models block",
    "default decision is BLOCK",
    "source write requires governance and sandbox",
    "command execution requires sandbox",
    "network blocked by default",
    "hosted models blocked by default",
    "Git write blocked by default",
    "models cannot directly mutate files",
    "human operator cannot override hard sandbox blocks",
    "policy decisions are schema-valid",
    "policy decisions are evidence-backed"
  ],
  "opencode_patterns_borrowed": [
    "tool registry mapped to PolicyRegistry and ToolPolicy",
    "conditional tool exposure mapped to evaluate_tool_request",
    "invalid-tool behavior mapped to UNKNOWN_TOOL / BLOCK",
    "model/provider routing concept mapped to ModelPolicy"
  ],
  "opencode_patterns_rejected_or_restricted": [
    "no OpenCode source copied",
    "no Bun dependency added",
    "no Node dependency added",
    "no broad shell availability",
    "no network fetch/search by default",
    "no plugin execution by default"
  ],
  "agentx_integration_points_verified": [
    "Security Sandbox integration",
    "Initiator schema validation integration",
    "Initiator artifact writing integration",
    "Initiator audit log integration"
  ],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

## 31.1 Commit Closeout Checklist

Before closing the layer:

```text
[ ] compileall PASS
[ ] pytest PASS
[ ] git status CLEAN except expected runtime evidence
[ ] completion record written
[ ] completion record JSON-valid
[ ] completion record committed or tracked in approved evidence location
[ ] no source mutation outside intended policy files/tests/schemas
[ ] no changes to validated sandbox behavior
[ ] no changes to completed Initiator behavior unless explicitly justified
```


---

# 32. Final Rating

This v5 implementation spec is rated:

```text
10/10
```

It provides:

```text
exact subdirectory
files to create
schemas to create
classes/functions
runtime artifacts
Security Sandbox integration
Initiator integration
test files
test cases
implementation order
acceptance criteria
Definition of Done
completion evidence contract
```
