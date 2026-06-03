# SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling contract, implementation-ready, v3 closure pass
component_id: AGENTX_SECURITY_SANDBOX_FILESYSTEM_BOUNDARY
component_name: Security Sandbox / Filesystem Boundary Layer
roadmap_layer: 1
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: None
risk_level: critical
implementation_mode: deterministic checker/gate only
target_language: Python
canonical_subdirectory: tools/agentx_evolve/security/
schema_subdirectory: tools/agentx_evolve/schemas/
test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/security/
review_document_rating: 10/10
final_rule: sandbox gates all path, file, command, network, and secret operations; fail-closed by default; all decisions schema-governed and evidence-backed
```

---

# 1. Purpose

This document defines the controlling contract for the **Security Sandbox / Filesystem Boundary Layer** in Agent_X.

The Security Sandbox is the first deterministic safety layer in the Agent_X self-evolution stack. It must answer **ALLOW**, **BLOCK**, **WARN**, **NEEDS_GOVERNANCE**, **NEEDS_ROLLBACK_SNAPSHOT**, or **NEEDS_SESSION** for every path, file, subprocess, network, and secret operation before any upper layer (orchestrator, tools, patch execution) may proceed.

Core rule:

```text
The Security Sandbox gates all unsafe operations.
It does not grant permission — it checks permission.
It fails closed when policy is missing, configuration is ambiguous, or authority cannot be verified.
```

The sandbox is a deterministic gate. It must not:

```text
execute subprocesses (only precheck)
apply patches (only precheck)
call models
make network requests
perform source-level orchestration
write to source files (only runtime writes under .agentx-init/ by default)
```

---

# 2. Scope

## 2.1 Required in This Layer

The Security Sandbox must define and implement deterministic checks for:

```text
path normalization and boundary checking
read file safety
write file safety (runtime and source)
exact edit safety
patch target precheck
subprocess command precheck
network request precheck
secret redaction
sandbox evidence writing (JSONL append + atomic latest)
Initiator compatibility adapter
schema-governed decision records
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
file writing outside runtime artifacts (source writes require governance)
patch application
shell execution
network fetching
model calls
orchestration
promotion
Git operations
MCP server
container sandbox
LLM calls
```

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because the sandbox is a safety-critical deterministic gate. Every operation must produce a schema-governed decision with evidence.

EQC applies to:

```text
path boundary decisions
file read decisions
file write decisions
edit decisions
patch precheck decisions
subprocess decisions
network decisions
secret redaction decisions
evidence writing
```

The sandbox must fail closed.

## 3.2 Required Supporting Standard: FIC

FIC is required because the implementation must be file-specific and auditable.

Expected files:

```text
tools/agentx_evolve/security/__init__.py
tools/agentx_evolve/security/security_models.py
tools/agentx_evolve/security/sandbox_policy.py
tools/agentx_evolve/security/path_boundary.py
tools/agentx_evolve/security/safe_file_ops.py
tools/agentx_evolve/security/safe_subprocess.py
tools/agentx_evolve/security/network_policy.py
tools/agentx_evolve/security/secret_redactor.py
tools/agentx_evolve/security/sandbox_evidence.py
tools/agentx_evolve/security/initiator_compat.py
```

Each file must have one clear responsibility, public API, safety invariants, tests, and evidence expectations.

## 3.3 Required Supporting Standard: SIB

SIB is required because the sandbox is an integration boundary that connects to:

```text
Initiator core services (path_registry, source_guard, schema_validation, artifact_io, audit_log)
Tool / MCP Adapter (security tools use sandbox for gating)
Governed Patch Execution (patch_precheck is called before patch application)
Self-Evolution Orchestrator (orchestrator calls sandbox through tool adapter)
```

This layer must not be bypassed by any upper layer. All path, file, subprocess, and network operations must go through the sandbox.

## 3.4 Required Schema Contract

Schema Contract is required because every sandbox decision must be structured and reproducible.

Required schemas:

```text
sandbox_policy.schema.json
sandbox_decision.schema.json
path_boundary_result.schema.json
safe_file_operation.schema.json
safe_subprocess_result.schema.json
network_policy_result.schema.json
secret_redaction_result.schema.json
sandbox_violation.schema.json
sandbox_audit.schema.json
```

## 3.5 Required Evidence / Audit Rules

Every sandbox decision may be written as evidence.

Evidence is required for:

```text
path boundary decision (when audit_enabled)
file operations (when audit_enabled)
subprocess decisions
network decisions
secret redaction events (metadata only)
policy decisions
violation events
```

---

# 4. Dependency Gates and Restricted Mode

## 4.1 Required Controlled Layers

The Security Sandbox has no required downstream layers. It is the foundation.

It integrates with:

```text
Initiator core services (optional, degraded mode allowed)
Tool / MCP Adapter (uses sandbox decisions)
```

## 4.2 Missing Dependency Behavior

If a dependency is missing, the sandbox must fall back to local deterministic behavior.

```text
Initiator path_registry unavailable -> use provided repo_root
Initiator source_guard unavailable -> check mutation_allowlist or fall back to BLOCK
Initiator schema_validation unavailable -> skip schema validation, fail closed on evidence write
Initiator artifact_io unavailable -> use local atomic write
Initiator audit_log unavailable -> write audit to local fallback file
```

## 4.3 Restricted Mode

Restricted mode is not applicable to this layer. The sandbox is always fully operational.

## 4.4 Authority Rule

The sandbox does not grant permission by itself. It checks:

```text
path is inside repository
path does not use symlink escape
path does not target L0 (for writes)
path does not target protected paths (for writes)
path is not in blocked_write_paths
source writes are explicitly allowed by policy
governance decision is present (for source writes)
implementation session is present (for source writes)
rollback snapshot is present (for source writes)
mutation allowlist approves the target (for source writes)
subprocess is allowed by policy and allowlist
network is allowed by policy and allowlist
```

If authorities disagree, the strictest result wins. Decision precedence:

```text
BLOCK
NEEDS_GOVERNANCE
NEEDS_SESSION
NEEDS_ROLLBACK_SNAPSHOT
WARN
ALLOW
```

---

# 5. Sandbox Decision Rules

## 5.1 Path Boundary Decisions

Every path must be normalized and checked against the repository root.

Rules:

```text
paths with control characters -> BLOCK
paths outside repository -> BLOCK
symlink escape -> BLOCK
L0 writes -> BLOCK
protected path writes -> BLOCK
blocked_write_paths writes -> BLOCK
source writes when source_write_allowed=False -> BLOCK
```

## 5.2 File Operation Decisions

File reads and writes have additional rules.

Read rules:

```text
path boundary must ALLOW
file must exist (otherwise FAILED, not BLOCK)
file must not be a directory
file size must not exceed max_file_size_bytes
read produces content and before_hash
```

Write rules:

```text
path boundary must ALLOW
runtime writes: allowed under .agentx-init/ (allowlisted paths enforced)
source writes: blocked unless source_write_allowed=True with governance, session, rollback, and compat
atomic write with fsync and temp file
clean up temp file on failure
```

## 5.3 Edit Rules

Exact edit rules:

```text
read old state first
old_text must appear exactly once (0 matches = BLOCK, >1 matches = BLOCK)
perform safe write with updated content
dry run does not modify file
```

## 5.4 Subprocess Decision Rules

Subprocess precheck rules:

```text
command must be list of strings
no control characters in tokens
shell_allowed=False -> BLOCK
working_directory must be inside repo (if provided)
empty command -> BLOCK
destructive patterns always BLOCK (rm -rf, sudo, su, curl|sh, bash -c, etc.)
bypass shell pipe patterns -> BLOCK
command must match allowlist entry (prefix match)
```

Destructive patterns that must always block:

```text
rm -rf /
rm -rf .
sudo ...
su ...
chmod -R 777
chown -R
curl | sh
wget | sh
bash -c
sh -c
python -c
powershell -Command
git push
git reset --hard
git clean -fdx
| sh, | bash, | zsh endings
commands starting with bash, sh, zsh
```

## 5.5 Network Decision Rules

Network precheck rules:

```text
network_allowed=False -> BLOCKED
target is None -> FAILED
v1: all targets blocked regardless (allowlist not yet implemented)
```

## 5.6 Secret Redaction Rules

Secret redaction rules:

```text
known secret names: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, GITHUB_TOKEN, GITLAB_TOKEN, AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, API_KEY, TOKEN, SECRET
generic long tokens: sk- prefix with 20+ chars, any 40+ char token
custom patterns from policy.redact_secret_patterns
empty input returns SUCCESS with 0 redactions
None policy uses default patterns only
replacement format: [REDACTED_API_KEY], [REDACTED_TOKEN], [REDACTED_SECRET]
```

---

# 6. Security Policy Contract

## 6.1 Policy Structure

The `SandboxPolicy` dataclass defines the sandbox configuration.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "sandbox_policy.schema.json",
  "policy_id": "string",
  "repo_root": "string",
  "runtime_state_root": ".agentx-init",
  "protected_paths": ["string"],
  "source_write_allowed": false,
  "runtime_write_allowed": true,
  "network_allowed": false,
  "shell_allowed": false,
  "allowlisted_commands": [],
  "allowlisted_write_paths": [],
  "blocked_write_paths": [],
  "max_file_size_bytes": 1048576,
  "resolve_symlinks": true,
  "require_governance_for_source_write": true,
  "require_session_for_source_write": true,
  "require_rollback_for_source_write": true,
  "redact_secret_patterns": [],
  "audit_enabled": false,
  "audit_log_path": "",
  "audit_level": "metadata",
  "warnings": [],
  "errors": []
}
```

## 6.2 Default Policy

The default sandbox policy must be safe by default:

```text
source_write_allowed: False
runtime_write_allowed: True
network_allowed: False
shell_allowed: False
protected_paths: ["L0/", "agent_x/runtime/", "core/"]
allowlisted_write_paths: [".agentx-init/"]
blocked_write_paths: ["L0/"]
max_file_size_bytes: 1048576 (1 MB)
resolve_symlinks: True
require_governance_for_source_write: True
require_session_for_source_write: True
require_rollback_for_source_write: True
```

## 6.3 Policy Loading

`load_sandbox_policy_from_dict` must accept a dict (from JSON or similar) and return a `SandboxPolicy`.

Rules:

```text
unknown fields in the source dict are ignored
repo_root can be overridden by the caller
missing policy_id is auto-generated
all fields have safe defaults
```

## 6.4 Policy Merging

`merge_sandbox_policy` must merge an override dict into a base policy.

Rules:

```text
list fields (protected_paths, blocked_write_paths) append unique entries
other fields are overwritten if present in override
the base policy is not mutated
```

---

# 7. Schema Contracts

## 7.1 General Schema Rules

Every schema must:

```text
require schema_version
require schema_id
define required field list
constrain enum values where applicable
reject additional properties
```

Every schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
```

## 7.2 Sandbox Policy Schema

Schema ID: `sandbox_policy.schema.json`

Purpose: defines the sandbox policy structure.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "sandbox_policy.schema.json",
  "policy_id": "string",
  "repo_root": "string",
  "runtime_state_root": "string",
  "protected_paths": ["string"],
  "source_write_allowed": false,
  "runtime_write_allowed": true,
  "network_allowed": false,
  "shell_allowed": false,
  "allowlisted_commands": [],
  "allowlisted_write_paths": [],
  "blocked_write_paths": [],
  "max_file_size_bytes": 1048576,
  "resolve_symlinks": true,
  "require_governance_for_source_write": true,
  "require_session_for_source_write": true,
  "require_rollback_for_source_write": true,
  "redact_secret_patterns": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
schema_version must be "1.0"
schema_id must be "sandbox_policy.schema.json"
all fields are required
no additional properties allowed
```

## 7.3 Sandbox Decision Schema

Schema ID: `sandbox_decision.schema.json`

Purpose: records every sandbox decision with decision outcome, rules applied, and evidence references.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "sandbox_decision.schema.json",
  "decision_id": "string",
  "timestamp": "string",
  "source_component": "SecuritySandbox",
  "operation": "READ|WRITE|EDIT|PATCH_PRECHECK|SUBPROCESS|NETWORK|REDACT",
  "target": "string|null",
  "decision": "ALLOW|BLOCK|WARN|NEEDS_GOVERNANCE|NEEDS_SESSION|NEEDS_ROLLBACK_SNAPSHOT",
  "reason": "string",
  "applied_rule_ids": ["string"],
  "evidence_ids": ["string"],
  "violations": ["string"],
  "warnings": ["string"],
  "errors": ["string"]
}
```

Rules:

```text
decision enum must include all six values
operation enum must include all seven operations
target may be null for network/subprocess operations
```

## 7.4 Path Boundary Result Schema

Schema ID: `path_boundary_result.schema.json`

Purpose: records the result of a path normalization and boundary check.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "path_boundary_result.schema.json",
  "result_id": "string",
  "timestamp": "string",
  "source_component": "PathBoundary",
  "input_path": "string",
  "resolved_path": "string|null",
  "repo_relative_path": "string|null",
  "inside_repo": true,
  "is_symlink": false,
  "symlink_escape": false,
  "is_l0": false,
  "is_protected": false,
  "operation": "string",
  "status": "SUCCESS|BLOCKED",
  "warnings": ["string"],
  "errors": ["string"]
}
```

## 7.5 Safe File Operation Schema

Schema ID: `safe_file_operation.schema.json`

Purpose: records the result of a safe file operation (read, write, edit).

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "safe_file_operation.schema.json",
  "operation_id": "string",
  "timestamp": "string",
  "source_component": "SafeFileOps",
  "operation": "READ|WRITE|EDIT",
  "target_path": "string",
  "status": "SUCCESS|BLOCKED|FAILED|DRY_RUN",
  "before_hash": "string|null",
  "after_hash": "string|null",
  "bytes_read": 0,
  "bytes_written": 0,
  "decision_id": "string",
  "content": "string|null",
  "warnings": ["string"],
  "errors": ["string"]
}
```

## 7.6 Safe Subprocess Result Schema

Schema ID: `safe_subprocess_result.schema.json`

Purpose: records the result of a subprocess precheck.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "safe_subprocess_result.schema.json",
  "result_id": "string",
  "timestamp": "string",
  "source_component": "SafeSubprocess",
  "command": ["string"],
  "working_directory": "string|null",
  "status": "ALLOW|BLOCK|FAILED",
  "reason": "string",
  "timeout_seconds": 60,
  "stdout_redacted": "string|null",
  "stderr_redacted": "string|null",
  "warnings": ["string"],
  "errors": ["string"]
}
```

## 7.7 Network Policy Result Schema

Schema ID: `network_policy_result.schema.json`

Purpose: records the result of a network request precheck.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "network_policy_result.schema.json",
  "result_id": "string",
  "timestamp": "string",
  "source_component": "NetworkPolicy",
  "target": "string|null",
  "status": "BLOCKED|FAILED",
  "reason": "string",
  "warnings": ["string"],
  "errors": ["string"]
}
```

## 7.8 Secret Redaction Result Schema

Schema ID: `secret_redaction_result.schema.json`

Purpose: records the result of a secret redaction operation.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "secret_redaction_result.schema.json",
  "result_id": "string",
  "timestamp": "string",
  "source_component": "SecretRedactor",
  "status": "SUCCESS",
  "redacted_text": "string",
  "redaction_count": 0,
  "redaction_types": ["string"],
  "warnings": ["string"],
  "errors": ["string"]
}
```

## 7.9 Sandbox Violation Schema

Schema ID: `sandbox_violation.schema.json`

Purpose: records a sandbox violation event.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "sandbox_violation.schema.json",
  "violation_id": "string",
  "timestamp": "string",
  "source_component": "SecuritySandbox",
  "operation": "string",
  "target": "string|null",
  "violation_type": "string",
  "severity": "string",
  "reason": "string",
  "decision_id": "string|null",
  "warnings": ["string"],
  "errors": ["string"]
}
```

## 7.10 Sandbox Audit Schema

Schema ID: `sandbox_audit.schema.json`

Purpose: records an audit event for sandbox decisions.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "sandbox_audit.schema.json",
  "audit_id": "string",
  "timestamp": "string",
  "source_component": "SecuritySandbox",
  "event_type": "string",
  "operation": "string",
  "target": "string|null",
  "decision": "string",
  "reason": "string",
  "artifacts": ["string"],
  "success": true,
  "operation_allowed": true,
  "enforcement_success": true,
  "warnings": ["string"],
  "errors": ["string"]
}
```

---

# 8. Evidence / Audit Contract

## 8.1 Evidence Writing

Every sandbox decision may be written as evidence.

Evidence methods:

```text
append_sandbox_decision: appends to .agentx-init/security/sandbox_decisions.jsonl
write_latest_sandbox_decision: atomically writes .agentx-init/security/latest_sandbox_decision.json
append_sandbox_violation: appends to .agentx-init/security/sandbox_violations.jsonl
```

Evidence rules:

```text
JSONL appends use fcntl locking for concurrency safety
latest writes use atomic temp-file + replace pattern
schema validation is performed when InitiatorCompat is available
schema-invalid artifacts are rejected with SCHEMA_VALIDATION_FAILED
audit events are delegated to Initiator audit_log when available
audit falls back to local .agentx-init/memory/audit_events.jsonl
```

## 8.2 Audit Event Schema

Every `SandboxDecision` can produce an audit event via `build_sandbox_audit_event`.

Required audit fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "sandbox_audit.schema.json",
  "audit_id": "string",
  "timestamp": "string",
  "source_component": "SecuritySandbox",
  "event_type": "sandbox_decision",
  "operation": "string",
  "target": "string|null",
  "decision": "string",
  "reason": "string",
  "artifacts": [".agentx-init/security/sandbox_decisions.jsonl"],
  "success": true,
  "operation_allowed": true,
  "enforcement_success": true,
  "warnings": [],
  "errors": []
}
```

---

# 9. InitiatorCompat Contract

## 9.1 Purpose

`InitiatorCompat` is the integration bridge between the new Security Sandbox layer and the existing completed Initiator at `tools/agentx_initiator/`.

It must:

```text
import Initiator modules gracefully (degrade on ImportError)
provide repo_root from path_registry or fallback
provide runtime_state_root
provide protected_paths
check source guard via source_guard or mutation_allowlist
validate schemas via initiator schema_validation or fail closed
write artifacts atomically via initiator artifact_io or local fallback
append audit events via initiator audit_log or local fallback
track integration failures
support degraded mode flag
```

## 9.2 Degraded Mode

When Initiator modules are unavailable:

```text
repo_root must be provided by the caller
schema validation is unavailable -> decisions still proceed (validation is best-effort for evidence)
fallback local atomic write is used
fallback local audit log is written
degraded flag is set to True
integration_failures list records all import errors
```

## 9.3 Source Guard Check

Source guard must be checked before source writes are allowed.

Order:

```text
1. If mutation_allowlist is provided and non-empty, check against allowlist
2. If mutation_allowlist is not provided or empty, try initiator source_guard
3. If source_guard unavailable, return non-enforcing status -> BLOCK
```

---

# 10. Evidence Rules

## 10.1 Evidence File Locations

Runtime evidence is written under:

```text
.agentx-init/security/
```

Expected evidence files:

```text
.agentx-init/security/sandbox_decisions.jsonl
.agentx-init/security/sandbox_violations.jsonl
.agentx-init/security/latest_sandbox_decision.json
```

## 10.2 Evidence Writing Rules

```text
JSONL files are append-only
latest files are written atomically (temp file + fsync + replace)
concurrent appends use fcntl flock
schema-invalid artifacts are NOT written when InitiatorCompat is available
evidence must not contain unredacted secrets
```

---

# 11. Dependency Degraded Behavior

## 11.1 When Policy / Policy File Is Unavailable

```text
default_sandbox_policy() returns a safe-default policy
load_sandbox_policy_from_dict() still works with any dict
merge_sandbox_policy() requires a base policy
no sandbox operation requires a persisted policy file
```

## 11.2 When Git / Repository Root Is Unavailable

```text
repo_root is required for path boundary checks
if no repo_root is provided and path_registry is unavailable, InitiatorCompat raises RuntimeError
safe file operations require repo_root
subprocess checks require repo_root for working_directory validation
degraded mode: caller must provide repo_root explicitly
```

## 11.3 When Initiator Modules Are Unavailable

```text
imports fail silently, recorded in integration_failures
degraded mode: compat continues with local fallbacks
schema validation: fails closed (returns valid=False)
source guard: returns non-enforcing (causes BLOCK for source writes)
atomic write: falls back to local temp-file + replace
audit: falls back to local .agentx-init/memory/audit_events.jsonl
repo_root: must be provided explicitly
```

## 11.4 When mutation_allowlist Is Available

```text
allowlist is checked before initiator source_guard
allowlist with empty mutations falls through to source_guard
unapproved mutations cause BLOCK
approved mutations allow the write (if other gates pass)
```

---

# 12. OpenCode Borrowing Notes

## 12.1 Concepts to Borrow

```text
path normalization and boundary checking
read-before-write for edits
exact string replacement (single match only)
permission scanning
invalid-tool fail-closed behavior
atomic file writes with temp files
```

## 12.2 Concepts to Restrict

```text
no default shell execution
no default network access
no source writes without governance
no patch application without governed patch execution
no L0 writes ever
no symlink escape
no raw file mutation without sandbox check
```

## 12.3 Agent_X Mapping

| OpenCode concept | Agent_X equivalent | Required control |
|---|---|---|
| read file | `safe_read_file` | Path boundary + max size + audit |
| edit file | `safe_exact_edit` | Single match + safe write |
| write file | `safe_write_file` | Runtime/source gates + atomic fsync |
| patch/apply_patch | `safe_patch_precheck` | Target precheck only |
| shell | `check_subprocess_allowed` | Policy + allowlist + destructive pattern block |
| invalid tool | `SandboxDecision(decision=BLOCK)` | Fail closed with evidence |
| permission scan | `check_path_boundary` | Inside-repo + symlink + protected path check |

---

# 13. Agent_X Integration Notes

## 13.1 Tool / MCP Adapter Integration

The sandbox is called by security tools before any file, command, or network operation.

Integration points:

```text
read_file_guarded -> safe_read_file
write_file_guarded -> safe_write_file
edit_file_guarded -> safe_exact_edit
patch_precheck_guarded -> safe_patch_precheck
run_allowlisted_command -> check_subprocess_allowed
```

## 13.2 Policy / Capability Registry Integration

The sandbox uses `SandboxPolicy` for its configuration. The policy may be loaded from a registry or created by defaults.

## 13.3 Governed Patch Execution Integration

`safe_patch_precheck` provides the path-level precheck for patch targets. The actual patch application is handled by the Governed Patch Execution Layer.

## 13.4 Self-Evolution Orchestrator Integration

The orchestrator routes path, file, and command operations through the Tool / MCP Adapter, which calls sandbox checks. The orchestrator must not call sandbox functions directly for mutation.

---

# 14. No-Go Conditions

The implementation must be rejected if:

```text
any path operation defaults to ALLOW without checking repository boundary
symlink escape is not detected
L0 writes are not blocked by default
source writes are allowed without governance, session, rollback, and source guard
subprocess execution is allowed by default
network access is allowed by default
secret values are logged without redaction
destructive subprocess patterns (rm -rf, sudo, curl|sh) are not blocked
schemas accept unknown additional properties
schema-invalid decisions are written to evidence
atomic writes use unsafe patterns (no fsync, no temp file)
concurrent evidence appends can corrupt the JSONL file
Initiator import failures cause exceptions instead of degraded fallback
```
