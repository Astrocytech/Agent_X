# SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_IMPLEMENTATION_SPEC_v3

```text
document_id: SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_IMPLEMENTATION_SPEC
version: v3.0
status: implementation-ready, subdirectory-explicit, integration-final
based_on: SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_EQC_FIC_SIB_SCHEMA_CONTRACT_v3
component_id: AGENTX_SECURITY_SANDBOX_FILESYSTEM_BOUNDARY
component_name: Security Sandbox / Filesystem Boundary Layer
roadmap_layer: 1
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
target_language: Python
target_runtime: local-only first
target_package_preferred: tools/agentx_evolve
initiator_integration_target: tools/agentx_initiator
opencode_basis: read/edit/write/patch/shell tool separation, permission scanning, invalid-tool fail-closed behavior
rating_target: 10/10
```

---

# 0. v3 Review and Improvement Summary

## 0.1 v2 Rating

The v2 implementation spec was rated:

```text
9.7/10
```

## 0.2 Why v2 Was Not Fully 10/10

v2 correctly made the canonical subdirectory explicit:

```text
tools/agentx_evolve/security/
```

However, it still needed a few final implementation-control improvements:

```text
1. A single explicit destination summary at the top for coding agents.
2. A direct OpenCode-to-Agent_X implementation table inside the implementation spec, not only the contract.
3. Clearer rule that OpenCode is a design reference only and no TypeScript/Bun source should be copied.
4. More precise test/import setup for the new tools/agentx_evolve package.
5. A stronger final no-go list for implementation drift.
6. A final "ready to hand to coding LLM" checklist.
```

## 0.3 v3 Improvements

This v3 adds:

```text
canonical destination summary
OpenCode borrowing table
source-copy prohibition
test-time PYTHONPATH/import rules
implementation drift blockers
coding-LLM handoff checklist
```

Final v3 rating:

```text
10/10
```

---

# 1. Purpose

This document is the full implementation specification for the **Security Sandbox / Filesystem Boundary Layer**.

## 1.1 Canonical Destination Summary

The implementation must create the component here:

```text
tools/agentx_evolve/security/
```

The schemas must go here:

```text
tools/agentx_evolve/schemas/
```

The tests must go here:

```text
tools/agentx_evolve/tests/
```

The runtime artifacts must go here:

```text
.agentx-init/security/
```

The existing completed Initiator remains here and must not be moved:

```text
tools/agentx_initiator/
```

The integration bridge back to the Initiator must be:

```text
tools/agentx_evolve/security/initiator_compat.py
```

This is the canonical split:

```text
tools/agentx_initiator/         = completed Initiator
tools/agentx_evolve/security/   = new Security Sandbox / Filesystem Boundary layer
```

It converts the controlling contract:

```text
SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_EQC_FIC_SIB_SCHEMA_CONTRACT_v3
```

into exact implementation instructions for a coding LLM or developer.

The implementation must create a deterministic safety layer that future Agent_X self-evolution components will use before any file, path, command, network, or secret-sensitive operation.

This layer must borrow the useful OpenCode-style concepts:

```text
read
edit
write
patch / apply_patch
shell
tool registry
permission scanning
invalid-tool fail-closed behavior
```

but must implement them under Agent_X’s stricter rules:

```text
no source writes by default
no shell by default
no network by default
no L0 writes
no path traversal
no symlink escape
no protected path writes
all decisions schema-governed
all important decisions evidence-backed
integration with tools/agentx_initiator
```

---

# 2. Implementation Goal

At the end of this implementation, Agent_X must have a new deterministic package that can answer:

```text
ALLOW
BLOCK
WARN
NEEDS_GOVERNANCE
NEEDS_ROLLBACK_SNAPSHOT
```

for:

```text
path reads
runtime-state writes
source writes
exact edits
patch target prechecks
subprocess requests
network requests
secret redaction events
```

It must expose safe equivalents of OpenCode-style primitives:

```text
OpenCode read       -> safe_read_file
OpenCode edit       -> safe_exact_edit
OpenCode write      -> safe_write_file
OpenCode patch      -> safe_patch_precheck
OpenCode shell      -> check_subprocess_allowed
OpenCode invalid    -> fail-closed SandboxDecision
```

The component must not implement:

```text
full patch application
MCP server
LLM calls
Git write operations
network fetch
self-evolution orchestration
promotion
container sandbox
```


## 1.2 OpenCode Borrowing Table for Implementation

| OpenCode primitive/concept | Agent_X implementation in this spec | Borrowing limit |
|---|---|---|
| `read` | `safe_read_file` | Path-boundary checked, max-size checked, no unredacted durable logging. |
| `edit` | `safe_exact_edit` | Exact replacement only, ambiguity blocked, uses safe write. |
| `write` | `safe_write_file` | Runtime writes allowed under `.agentx-init/`; source writes blocked by default. |
| `patch` / `apply_patch` | `safe_patch_precheck` | Only target-path precheck in this layer; actual patch application belongs later. |
| `shell` | `check_subprocess_allowed` | Precheck only; default block; allowlist required. |
| invalid tool handling | `SandboxDecision(decision='BLOCK')` | Fail closed with evidence. |
| permission scanning | path/subprocess/network policy checks | Agent_X governance remains stronger than tool-level permission. |
| output truncation/redaction | `redact_secrets` and redacted result fields | No unredacted secret persistence. |

## 1.3 Source-Copy Prohibition

OpenCode is a reference for architecture and tool shape only.

Do not copy OpenCode TypeScript/Bun source code into Agent_X.

Reasons:

```text
OpenCode is TypeScript/Bun.
Agent_X layer is Python.
OpenCode has different trust assumptions.
Agent_X requires governance, source guard, rollback, schemas, and audit evidence.
```

---

# 3. Required Build Shape and Exact `tools/` Subdirectory

## 2.1 Canonical Location

This component must reside under the post-Initiator tool package:

```text
tools/agentx_evolve/security/
```

This is the canonical subdirectory for the Security Sandbox / Filesystem Boundary Layer.

The reason is:

```text
tools/agentx_initiator/ = completed Initiator tool
tools/agentx_evolve/    = post-Initiator self-evolution tool stack
tools/agentx_evolve/security/ = first deterministic safety layer after Initiator
```

The implementation must not place the new safety layer directly inside unrelated repository locations.

## 2.2 Full Required Directory Tree

Create or update this exact tree:

```text
tools/
  agentx_evolve/
    __init__.py
    security/
      __init__.py
      security_models.py
      sandbox_policy.py
      path_boundary.py
      safe_file_ops.py
      safe_subprocess.py
      network_policy.py
      secret_redactor.py
      sandbox_evidence.py
      initiator_compat.py

    schemas/
      sandbox_policy.schema.json
      sandbox_decision.schema.json
      path_boundary_result.schema.json
      safe_file_operation.schema.json
      safe_subprocess_result.schema.json
      network_policy_result.schema.json
      secret_redaction_result.schema.json
      sandbox_violation.schema.json
      sandbox_audit.schema.json

    tests/
      test_path_boundary.py
      test_safe_file_ops.py
      test_safe_subprocess.py
      test_network_policy.py
      test_secret_redactor.py
      test_sandbox_schema.py
      test_sandbox_agentx_integration.py
      test_sandbox_negative_cases.py
```

## 2.3 Relationship to Existing Initiator

The new component must integrate with the existing completed Initiator at:

```text
tools/agentx_initiator/
```

Specifically, it should integrate with Initiator services through:

```text
tools/agentx_evolve/security/initiator_compat.py
```

The sandbox must not copy or fork Initiator logic. It must use the compatibility adapter to call or wrap the existing Initiator services where possible.

## 2.4 Allowed Alternative Placement

Only if the project owner explicitly rejects a new `agentx_evolve` package, the fallback location is:

```text
tools/agentx_initiator/security/
```

If this fallback is used, the implementation must record a deviation in the completion record:

```json
{
  "deviations_from_contract": [
    "Security sandbox placed under tools/agentx_initiator/security instead of tools/agentx_evolve/security"
  ]
}
```

The preferred and default placement remains:

```text
tools/agentx_evolve/security/
```

## 2.5 Import Rule

Filesystem path may be:

```text
tools/agentx_initiator/
tools/agentx_evolve/
```

but runtime imports should use installed package names, for example:

```python
from agentx_initiator.core import path_registry
from agentx_evolve.security.path_boundary import check_path_boundary
```

Do not use this as the default import form:

```python
from tools.agentx_initiator.core import path_registry
from tools.agentx_evolve.security.path_boundary import check_path_boundary
```

That may work only when the repository root is configured as a namespace package. It must not be the implementation contract.

## 2.6 Packaging Expectation

If `tools/agentx_evolve` does not yet have packaging metadata, add it later in the Packaging / Distribution phase. For this implementation slice, tests may import by adding `tools/` to `PYTHONPATH`, but the source code itself should be written as if `agentx_evolve` is a package.

Expected test-time import style:

```python
from agentx_evolve.security.sandbox_policy import default_sandbox_policy
```

---

# 4. Implementation Order

Implement in this exact order.

```text
1. security_models.py
2. schemas
3. sandbox_policy.py
4. path_boundary.py
5. network_policy.py
6. secret_redactor.py
7. safe_file_ops.py
8. safe_subprocess.py
9. initiator_compat.py
10. sandbox_evidence.py
11. tests
12. completion evidence
```

Rationale:

```text
models first
schemas second
pure policy/path decisions before mutation wrappers
network and redaction before logging
file ops only after path checks exist
subprocess only after policy rules exist
Initiator integration after local deterministic fallback exists
evidence after decision objects exist
```

---

# 5. File-by-File Implementation Spec

---

## 4.1 `tools/agentx_evolve/__init__.py`

### Purpose

Mark the package as the post-Initiator Agent_X self-evolution package.

### Required Content

```python
__version__ = "0.1.0"
```

### Must Not Do

```text
no imports with side effects
no filesystem writes
no network
no model loading
```

---

## 4.2 `tools/agentx_evolve/security/__init__.py`

### Purpose

Expose the public security/sandbox API.

### Required Exports

```python
from .security_models import (
    SandboxPolicy,
    SandboxDecision,
    SandboxViolation,
    PathBoundaryResult,
    SafeFileOperationResult,
    SafeSubprocessResult,
    NetworkPolicyResult,
    SecretRedactionResult,
)

from .path_boundary import normalize_repo_path, check_path_boundary
from .safe_file_ops import safe_read_file, safe_write_file, safe_exact_edit, safe_patch_precheck
from .safe_subprocess import check_subprocess_allowed
from .network_policy import check_network_allowed
from .secret_redactor import redact_secrets
```

### Must Not Do

```text
no execution
no policy loading from disk
no runtime artifact writes
```

---

## 4.3 `security_models.py`

### Purpose

Define all shared data structures.

### Required Implementation Style

Use Python dataclasses first. Do not require Pydantic unless project already standardizes on it.

### Required Enums as String Constants

```python
DECISION_ALLOW = "ALLOW"
DECISION_BLOCK = "BLOCK"
DECISION_WARN = "WARN"
DECISION_NEEDS_GOVERNANCE = "NEEDS_GOVERNANCE"
DECISION_NEEDS_ROLLBACK_SNAPSHOT = "NEEDS_ROLLBACK_SNAPSHOT"

STATUS_SUCCESS = "SUCCESS"
STATUS_BLOCKED = "BLOCKED"
STATUS_FAILED = "FAILED"
STATUS_DRY_RUN = "DRY_RUN"
STATUS_PASS = "PASS"

OP_READ = "READ"
OP_WRITE = "WRITE"
OP_EDIT = "EDIT"
OP_PATCH_PRECHECK = "PATCH_PRECHECK"
OP_SUBPROCESS = "SUBPROCESS"
OP_NETWORK = "NETWORK"
OP_REDACT = "REDACT"
```

### Required Dataclasses

#### `SandboxPolicy`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "sandbox_policy.schema.json"
policy_id: str
repo_root: str
runtime_state_root: str = ".agentx-init"
protected_paths: list[str]
source_write_allowed: bool = False
runtime_write_allowed: bool = True
network_allowed: bool = False
shell_allowed: bool = False
allowlisted_commands: list[list[str]] | list[str]
allowlisted_write_paths: list[str]
blocked_write_paths: list[str]
max_file_size_bytes: int = 1048576
resolve_symlinks: bool = True
require_governance_for_source_write: bool = True
require_session_for_source_write: bool = True
require_rollback_for_source_write: bool = True
redact_secret_patterns: list[str]
warnings: list[str]
errors: list[str]
```

#### `SandboxDecision`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "sandbox_decision.schema.json"
decision_id: str
timestamp: str
source_component: str = "SecuritySandbox"
operation: str
target: str | None
decision: str
reason: str
applied_rule_ids: list[str]
evidence_ids: list[str]
violations: list[str]
warnings: list[str]
errors: list[str]
```

#### `SandboxViolation`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "sandbox_violation.schema.json"
violation_id: str
timestamp: str
source_component: str = "SecuritySandbox"
operation: str
target: str | None
violation_type: str
severity: str
reason: str
decision_id: str | None
warnings: list[str]
errors: list[str]
```

#### `PathBoundaryResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "path_boundary_result.schema.json"
result_id: str
timestamp: str
source_component: str = "PathBoundary"
input_path: str
resolved_path: str | None
repo_relative_path: str | None
inside_repo: bool
is_symlink: bool
symlink_escape: bool
is_l0: bool
is_protected: bool
operation: str
status: str
warnings: list[str]
errors: list[str]
```

#### `SafeFileOperationResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "safe_file_operation.schema.json"
operation_id: str
timestamp: str
source_component: str = "SafeFileOps"
operation: str
target_path: str
status: str
before_hash: str | None
after_hash: str | None
bytes_read: int
bytes_written: int
decision_id: str
content: str | None
warnings: list[str]
errors: list[str]
```

Note:

```text
content may be present for safe_read_file return value, but must not be written to durable audit logs unless explicitly redacted.
```

#### `SafeSubprocessResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "safe_subprocess_result.schema.json"
result_id: str
timestamp: str
source_component: str = "SafeSubprocess"
command: list[str]
working_directory: str | None
status: str
reason: str
timeout_seconds: int
stdout_redacted: str | None
stderr_redacted: str | None
warnings: list[str]
errors: list[str]
```

#### `NetworkPolicyResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "network_policy_result.schema.json"
result_id: str
timestamp: str
source_component: str = "NetworkPolicy"
target: str | None
status: str
reason: str
warnings: list[str]
errors: list[str]
```

#### `SecretRedactionResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "secret_redaction_result.schema.json"
result_id: str
timestamp: str
source_component: str = "SecretRedactor"
status: str
redacted_text: str
redaction_count: int
redaction_types: list[str]
warnings: list[str]
errors: list[str]
```

### Required Helper Functions

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
sha256_text(text: str) -> str
sha256_file(path: Path) -> str
```

### Acceptance

```text
dataclasses instantiate
to_dict serializes them
IDs are unique enough for local evidence
timestamps are ISO-like UTC strings
no filesystem writes
no imports from LLM/network packages
```

---

## 4.4 `sandbox_policy.py`

### Purpose

Create and normalize `SandboxPolicy`.

### Required Public Functions

```python
default_sandbox_policy(repo_root: Path) -> SandboxPolicy

load_sandbox_policy_from_dict(data: dict, repo_root: Path | None = None) -> SandboxPolicy

merge_sandbox_policy(base: SandboxPolicy, override: dict) -> SandboxPolicy

is_runtime_path(path: Path, repo_root: Path, policy: SandboxPolicy) -> bool

is_protected_path(repo_relative_path: str, policy: SandboxPolicy) -> bool

is_l0_path(repo_relative_path: str) -> bool
```

### Default Policy

```text
source_write_allowed = false
runtime_write_allowed = true
network_allowed = false
shell_allowed = false
allowlisted_write_paths = [".agentx-init/"]
blocked_write_paths = ["L0/"]
protected_paths = ["L0/", "agent_x/runtime/", "core/"]
require_governance_for_source_write = true
require_session_for_source_write = true
require_rollback_for_source_write = true
max_file_size_bytes = 1048576
resolve_symlinks = true
```

### Rules

```text
Do not read config from disk in this module.
Do not write artifacts in this module.
Policy creation must be deterministic.
```

### Tests

```text
default policy blocks source writes
default policy allows runtime writes under .agentx-init
L0 path detection works
protected path detection works
policy merge does not silently remove protected paths
```

---

## 4.5 `path_boundary.py`

### Purpose

Normalize paths and determine whether a requested path is inside allowed boundaries.

### Required Public Functions

```python
normalize_repo_path(path: str | Path, repo_root: Path) -> PathBoundaryResult

check_path_boundary(
    path: str | Path,
    repo_root: Path,
    operation: str,
    policy: SandboxPolicy
) -> SandboxDecision

path_to_repo_relative(resolved_path: Path, repo_root: Path) -> str | None

is_inside_repo(resolved_path: Path, repo_root: Path) -> bool

detect_symlink_escape(path: Path, resolved_path: Path, repo_root: Path) -> bool
```

### Required Logic

1. Convert input to `Path`.
2. If relative, join with `repo_root`.
3. Resolve with strict behavior appropriate to operation:
   - For reads, missing file should fail cleanly.
   - For writes, parent must resolve and target may not exist yet.
4. Confirm resolved path is under `repo_root`.
5. Convert to repo-relative path.
6. Check:
   - traversal escape
   - symlink escape
   - L0
   - protected path
   - runtime path
   - source write disabled
7. Return schema-aligned result and decision.

### Path Handling Details

For existing targets:

```python
resolved = path.resolve()
```

For non-existing write target:

```text
resolve parent directory
join final filename
ensure resolved parent is inside repo
ensure final normalized target remains inside repo
```

### Blocking Priority

```text
PATH_OUTSIDE_REPO
SYMLINK_ESCAPE
L0_WRITE_BLOCKED
PROTECTED_PATH_BLOCKED
SOURCE_WRITE_DISABLED
RUNTIME_WRITE_BOUNDARY_VIOLATION
```

### Tests

```text
relative inside repo allowed for read
absolute inside repo allowed for read
../ traversal outside repo blocked
absolute outside repo blocked
symlink escape blocked
L0 write blocked
protected path write blocked
runtime write under .agentx-init allowed
runtime write outside .agentx-init blocked
```

---

## 4.6 `network_policy.py`

### Purpose

Decide whether a network operation is allowed.

### Required Public Function

```python
check_network_allowed(target: str | None, policy: SandboxPolicy) -> NetworkPolicyResult
```

### v1 Behavior

```text
network_allowed false -> BLOCK
network_allowed true but target missing -> BLOCK
network_allowed true + target provided -> ALLOW only if future allowlist says yes
```

Since v1 does not implement endpoint allowlists, default should still block unless explicitly configured and documented.

### Tests

```text
network blocked by default
network target blocked when not allowlisted
network result schema-valid
```

---

## 4.7 `secret_redactor.py`

### Purpose

Redact secrets before text can be logged or stored.

### Required Public Function

```python
redact_secrets(text: str, policy: SandboxPolicy) -> SecretRedactionResult
```

### Required Patterns

Implement at minimum:

```text
configured regex patterns from policy.redact_secret_patterns
environment-style secret names:
  OPENAI_API_KEY
  ANTHROPIC_API_KEY
  GOOGLE_API_KEY
  GITHUB_TOKEN
  GITLAB_TOKEN
  AWS_SECRET_ACCESS_KEY
  AWS_ACCESS_KEY_ID
  API_KEY
  TOKEN
  SECRET
API-key-like long token heuristic
```

### Redaction Replacement

Use:

```text
[REDACTED_SECRET]
```

or more specific forms:

```text
[REDACTED_API_KEY]
[REDACTED_TOKEN]
[REDACTED_SECRET]
```

### Rules

```text
Do not log unredacted text.
Do not mutate input.
Return redacted_text.
Return redaction_count.
Return redaction_types.
```

### Tests

```text
API-key-like value redacted
known env secret assignment redacted
no secret written to audit fixture
redaction count recorded
```

---

## 4.8 `safe_file_ops.py`

### Purpose

Implement safe file operations inspired by OpenCode’s `read`, `edit`, `write`, and `patch/apply_patch` separation.

### Required Public Functions

```python
check_read_allowed(
    path: str | Path,
    repo_root: Path,
    policy: SandboxPolicy
) -> SandboxDecision

check_write_allowed(
    path: str | Path,
    repo_root: Path,
    policy: SandboxPolicy,
    implementation_session_id: str | None = None,
    governance_decision_id: str | None = None
) -> SandboxDecision

safe_read_file(
    path: str | Path,
    repo_root: Path,
    policy: SandboxPolicy
) -> SafeFileOperationResult

safe_write_file(
    path: str | Path,
    content: str,
    repo_root: Path,
    policy: SandboxPolicy,
    dry_run: bool = False,
    implementation_session_id: str | None = None,
    governance_decision_id: str | None = None
) -> SafeFileOperationResult

safe_exact_edit(
    path: str | Path,
    old_text: str,
    new_text: str,
    repo_root: Path,
    policy: SandboxPolicy,
    dry_run: bool = False,
    implementation_session_id: str | None = None,
    governance_decision_id: str | None = None
) -> SafeFileOperationResult

safe_patch_precheck(
    target_paths: list[str | Path],
    repo_root: Path,
    policy: SandboxPolicy,
    implementation_session_id: str | None = None,
    governance_decision_id: str | None = None
) -> SandboxDecision
```

### `safe_read_file` Behavior

```text
check read boundary
block missing file cleanly
block directories
block files larger than max_file_size_bytes
read UTF-8 text by default
return content in result
do not write content to audit
```

### `safe_write_file` Behavior

```text
check write boundary
for runtime write: allow only under .agentx-init
for source write: require policy source_write_allowed and governance/session IDs
support dry-run without writing
write atomically if live
return before_hash if file exists
return after_hash for new content
return bytes_written
```

### Atomic Write Required

For live write:

```text
write temp file in same directory
flush
replace target atomically
```

### `safe_exact_edit` Behavior

```text
safe_read_file
count old_text occurrences
if 0 -> BLOCKED / OLD_TEXT_NOT_FOUND
if >1 -> BLOCKED / MULTIPLE_MATCHES
replace once in memory
call safe_write_file
support dry-run
```

### `safe_patch_precheck` Behavior

```text
iterate all target paths
run write boundary checks
if any BLOCK -> BLOCK
if any NEEDS_GOVERNANCE -> NEEDS_GOVERNANCE
if any NEEDS_ROLLBACK_SNAPSHOT -> NEEDS_ROLLBACK_SNAPSHOT
else ALLOW
```

### Tests

```text
safe read works
safe read missing fails cleanly
large file blocks
runtime write under .agentx-init works
source write blocks by default
source write requires governance and session
exact edit succeeds with one match
exact edit blocks no match
exact edit blocks multiple matches
dry-run changes nothing
patch precheck blocks forbidden target
```

---

## 4.9 `safe_subprocess.py`

### Purpose

Implement safe subprocess precheck inspired by OpenCode’s `shell` permission-scanning concept, but stricter.

### Required Public Function

```python
check_subprocess_allowed(
    command: list[str],
    policy: SandboxPolicy,
    working_directory: Path | None = None
) -> SafeSubprocessResult
```

### v1 Behavior

This function is a precheck. It should not actually run commands unless explicitly required later.

Default:

```text
BLOCK
```

### Allow Conditions

Allow only if:

```text
policy.shell_allowed = true
command is non-empty list
command executable matches allowlist
arguments do not match destructive patterns
working directory is allowed
network is not implied unless network_allowed
timeout policy exists
```

### Always Block If Command Contains

```text
rm -rf /
rm -rf .
sudo
su
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
```

### Tests

```text
blocks by default
blocks rm -rf
blocks curl pipe shell
blocks unallowlisted command
allows explicitly allowlisted validation command when shell_allowed true
redacts stdout/stderr sample text if provided later
```

---

## 4.10 `initiator_compat.py`

### Purpose

Safely integrate with the completed `tools/agentx_initiator` package without tightly coupling to unstable internals.

### Required Class

```python
class InitiatorCompat:
    def __init__(self, repo_root: Path | None = None): ...

    def get_repo_root(self) -> Path: ...

    def get_runtime_state_root(self) -> Path: ...

    def get_protected_paths(self) -> list[str]: ...

    def check_source_guard(self, target_paths: list[str]) -> dict: ...

    def validate_schema(self, artifact: dict, schema_id: str) -> dict: ...

    def write_json_atomic(self, path: Path, artifact: dict) -> dict: ...

    def append_audit_event(self, event: dict) -> dict: ...
```

### Import Strategy

Try imports in package form:

```python
from agentx_initiator.core import path_registry
from agentx_initiator.core import source_guard
from agentx_initiator.core import schema_validation
from agentx_initiator.core import artifact_io
from agentx_initiator.core import audit_log
```

If unavailable:

```text
record INITIATOR_INTEGRATION_FAILED
fall back only for deterministic local behavior
do not pretend integration succeeded
```

### Fallback Rules

Allowed fallback:

```text
repo_root from provided argument or cwd
runtime_state_root = repo_root / ".agentx-init"
protected_paths from default policy
local JSON atomic write
local append JSONL
```

Not allowed fallback:

```text
pretending source_guard approved source writes
pretending governance exists
pretending schema validation passed
```

### Tests

```text
imports initiator modules when installed
falls back cleanly when unavailable
records integration failure
does not modify initiator source
uses .agentx-init runtime state
```

---

## 4.11 `sandbox_evidence.py`

### Purpose

Write sandbox decisions and violations to append-only evidence files.

### Required Public Functions

```python
append_sandbox_decision(
    decision: SandboxDecision,
    repo_root: Path,
    compat: InitiatorCompat | None = None
) -> dict

append_sandbox_violation(
    violation: SandboxViolation,
    repo_root: Path,
    compat: InitiatorCompat | None = None
) -> dict

write_latest_sandbox_decision(
    decision: SandboxDecision,
    repo_root: Path,
    compat: InitiatorCompat | None = None
) -> dict

build_sandbox_audit_event(
    decision: SandboxDecision
) -> dict
```

### Required Paths

```text
.agentx-init/security/sandbox_decisions.jsonl
.agentx-init/security/sandbox_violations.jsonl
.agentx-init/security/latest_sandbox_decision.json
.agentx-init/security/latest_path_boundary_result.json
.agentx-init/security/latest_safe_subprocess_result.json
.agentx-init/security/latest_secret_redaction_result.json
.agentx-init/memory/audit_events.jsonl
```

### Rules

```text
create .agentx-init/security if needed
append JSONL only
write latest JSON atomically
redact before writing
do not write raw file content
do not write unredacted command output
do not rewrite previous JSONL lines
```

### Tests

```text
decision appended
violation appended
latest decision written atomically
audit event built
malformed existing JSONL line is preserved
```

---

# 6. Schema Implementation Spec

Create each schema as JSON Schema Draft 2020-12 or Draft 7, depending on current Agent_X convention. If the Initiator already uses a specific draft, match it.

Each schema must require:

```text
schema_version
schema_id
timestamp or artifact-specific timestamp
source_component
status/decision where applicable
warnings
errors
```

## 5.1 `sandbox_policy.schema.json`

Required fields:

```text
schema_version
schema_id
policy_id
repo_root
runtime_state_root
protected_paths
source_write_allowed
runtime_write_allowed
network_allowed
shell_allowed
allowlisted_commands
allowlisted_write_paths
blocked_write_paths
max_file_size_bytes
resolve_symlinks
require_governance_for_source_write
require_session_for_source_write
require_rollback_for_source_write
redact_secret_patterns
warnings
errors
```

## 5.2 `sandbox_decision.schema.json`

Required fields:

```text
schema_version
schema_id
decision_id
timestamp
source_component
operation
target
decision
reason
applied_rule_ids
evidence_ids
violations
warnings
errors
```

Allowed operations:

```text
READ
WRITE
EDIT
PATCH_PRECHECK
SUBPROCESS
NETWORK
REDACT
```

Allowed decisions:

```text
ALLOW
BLOCK
WARN
NEEDS_GOVERNANCE
NEEDS_ROLLBACK_SNAPSHOT
```

## 5.3 `path_boundary_result.schema.json`

Required fields:

```text
schema_version
schema_id
result_id
timestamp
source_component
input_path
resolved_path
repo_relative_path
inside_repo
is_symlink
symlink_escape
is_l0
is_protected
operation
status
warnings
errors
```

## 5.4 `safe_file_operation.schema.json`

Required fields:

```text
schema_version
schema_id
operation_id
timestamp
source_component
operation
target_path
status
before_hash
after_hash
bytes_read
bytes_written
decision_id
warnings
errors
```

Do not require `content`, because read content should not be durable evidence by default.

## 5.5 `safe_subprocess_result.schema.json`

Required fields:

```text
schema_version
schema_id
result_id
timestamp
source_component
command
working_directory
status
reason
timeout_seconds
stdout_redacted
stderr_redacted
warnings
errors
```

## 5.6 `network_policy_result.schema.json`

Required fields:

```text
schema_version
schema_id
result_id
timestamp
source_component
target
status
reason
warnings
errors
```

## 5.7 `secret_redaction_result.schema.json`

Required fields:

```text
schema_version
schema_id
result_id
timestamp
source_component
status
redacted_text
redaction_count
redaction_types
warnings
errors
```

## 5.8 `sandbox_violation.schema.json`

Required fields:

```text
schema_version
schema_id
violation_id
timestamp
source_component
operation
target
violation_type
severity
reason
decision_id
warnings
errors
```

## 5.9 `sandbox_audit.schema.json`

Required fields:

```text
schema_version
schema_id
audit_id
timestamp
source_component
event_type
operation
target
decision
reason
artifacts
success
warnings
errors
```

---

# 7. Authority Precedence Implementation

Implement a shared rule order.

Required order:

```text
1. L0_BLOCK
2. PATH_ESCAPE_BLOCK
3. SYMLINK_ESCAPE_BLOCK
4. PROTECTED_PATH_BLOCK
5. CAPABILITY_POLICY_BLOCK
6. GOVERNANCE_BLOCK
7. SOURCE_GUARD_BLOCK
8. ROLLBACK_REQUIRED
9. SANDBOX_POLICY_BLOCK
10. ALLOW
```

In this component, implement directly:

```text
L0_BLOCK
PATH_ESCAPE_BLOCK
SYMLINK_ESCAPE_BLOCK
PROTECTED_PATH_BLOCK
SOURCE_GUARD_BLOCK if source_guard available
ROLLBACK_REQUIRED if policy requires but session context lacks rollback signal
SANDBOX_POLICY_BLOCK
ALLOW
```

Capability and Governance checks may be represented by required IDs in v1. Full verification belongs to later layers.

Required rule:

```text
A later ALLOW can never override an earlier BLOCK.
```

---

# 8. Runtime Artifact Rules

All sandbox runtime writes go under:

```text
.agentx-init/security/
```

Required behavior:

```text
create directory if missing
write JSON latest files atomically
append JSONL history
never write outside .agentx-init/security except shared audit event under .agentx-init/memory/audit_events.jsonl
```

Do not write:

```text
source files
L0
protected paths
model logs
network logs
Git state
```

---

# 9. OpenCode Borrowing Checklist

Before implementation is accepted, verify the following conceptual borrowings are present.

```text
[ ] read concept implemented as safe_read_file
[ ] edit concept implemented as safe_exact_edit
[ ] write concept implemented as safe_write_file
[ ] patch concept implemented as safe_patch_precheck
[ ] shell concept implemented as check_subprocess_allowed
[ ] invalid-tool concept implemented as fail-closed SandboxDecision
[ ] tool-specific behavior avoids raw shell for file operations
[ ] permission scanning exists before subprocess allow
[ ] output redaction exists before logging
```

Also verify rejected OpenCode assumptions:

```text
[ ] shell is not broadly available
[ ] network fetch/search not available by default
[ ] plugin tool execution not implemented here
[ ] subagent execution not implemented here
[ ] no OpenCode TypeScript code copied
```

---

# 10. Initiator Integration Checklist

```text
[ ] imports use package path agentx_initiator, not tools.agentx_initiator
[ ] initiator_compat.py exists
[ ] path_registry integration attempted
[ ] source_guard integration attempted
[ ] validation_allowlist integration attempted where subprocess rules need it
[ ] schema_validation integration attempted
[ ] artifact_io integration attempted
[ ] audit_log integration attempted
[ ] integration failure is recorded, not hidden
[ ] sandbox does not modify Initiator source
```

---

# 11. Test Implementation Plan

## 10.1 Test Setup Utilities

Create reusable pytest fixtures:

```python
@pytest.fixture
def temp_repo(tmp_path): ...

@pytest.fixture
def default_policy(temp_repo): ...

@pytest.fixture
def repo_with_l0(temp_repo): ...

@pytest.fixture
def repo_with_symlink_escape(temp_repo): ...

@pytest.fixture
def runtime_state_dir(temp_repo): ...
```

Fixtures must create:

```text
repo_root/
  L0/
    protected.py
  src/
    allowed.txt
  core/
    protected_core.py
  .agentx-init/
    memory/
```

## 10.2 Path Boundary Test Cases

Implement:

```text
test_relative_path_inside_repo_allows_read
test_absolute_path_inside_repo_allows_read
test_path_traversal_blocks
test_absolute_path_outside_repo_blocks
test_symlink_escape_blocks
test_l0_write_blocks
test_protected_path_write_blocks
test_runtime_write_under_agentx_init_allows
test_runtime_write_outside_agentx_init_blocks
```

## 10.3 Safe File Operation Test Cases

Implement:

```text
test_safe_read_existing_file
test_safe_read_missing_file_fails_cleanly
test_safe_read_large_file_blocks
test_safe_write_blocks_when_source_write_disabled
test_safe_write_allows_runtime_artifact
test_safe_write_requires_governance_for_source_write
test_safe_write_requires_session_for_source_write
test_safe_exact_edit_single_match_succeeds
test_safe_exact_edit_no_match_blocks
test_safe_exact_edit_multiple_matches_blocks
test_safe_exact_edit_dry_run_changes_nothing
test_patch_precheck_blocks_forbidden_target
```

## 10.4 Safe Subprocess Test Cases

Implement:

```text
test_subprocess_blocks_by_default
test_rm_rf_blocks
test_curl_pipe_shell_blocks
test_unallowlisted_command_blocks
test_allowlisted_validation_command_allows_when_policy_enabled
test_stdout_stderr_redacted
```

## 10.5 Network Test Cases

Implement:

```text
test_network_blocks_by_default
test_network_requires_explicit_policy
test_network_target_not_allowlisted_blocks
```

## 10.6 Secret Redaction Test Cases

Implement:

```text
test_api_key_like_value_redacted
test_env_secret_name_redacted
test_no_secret_written_to_audit
test_redaction_count_recorded
```

## 10.7 Initiator Integration Test Cases

Implement:

```text
test_imports_initiator_path_registry
test_imports_initiator_source_guard
test_imports_initiator_validation_allowlist
test_imports_initiator_schema_validation
test_imports_initiator_artifact_io
test_imports_initiator_audit_log
test_sandbox_uses_agentx_init_runtime_state
test_sandbox_does_not_modify_initiator_source
```

If a module name has changed in the real repo, the test must either:

```text
update the compatibility adapter to the real module
```

or:

```text
record INITIATOR_INTEGRATION_FAILED and fail only if the module is required for the current operation
```

## 10.8 Schema Test Cases

Implement:

```text
test_sandbox_policy_schema_accepts_valid_policy
test_sandbox_decision_schema_accepts_valid_decision
test_sandbox_decision_schema_rejects_missing_required_fields
test_path_boundary_result_schema_accepts_valid_result
test_safe_file_operation_schema_accepts_valid_result
test_safe_subprocess_result_schema_accepts_valid_result
test_secret_redaction_schema_accepts_valid_result
```

## 10.9 Negative Safety Test Cases

Implement:

```text
test_attempted_l0_write_never_allows
test_attempted_path_escape_never_allows
test_attempted_symlink_escape_never_allows
test_attempted_raw_shell_never_allows
test_attempted_network_never_allows_by_default
test_opencode_style_patch_cannot_bypass_agentx_governance
test_plugin_like_tool_cannot_bypass_capability_policy
```

---

# 12. Manual Validation Commands

From repository root:

```bash
python -m compileall tools/agentx_evolve
python -m pytest tools/agentx_evolve/tests
```

If package installation is configured:

```bash
pip install -e tools/agentx_initiator
python -m pytest tools/agentx_evolve/tests
```

No command may require GPU, network, hosted provider, or LLM.

---

# 13. Completion Evidence

After implementation, write:

```text
.agentx-init/security/security_sandbox_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_SECURITY_SANDBOX_FILESYSTEM_BOUNDARY",
  "status": "VALIDATED",
  "canonical_subdirectory": "tools/agentx_evolve/security/",
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "commands_run": [],
  "artifacts_generated": [],
  "initiator_integration_points_verified": [],
  "opencode_patterns_borrowed": [],
  "opencode_patterns_rejected_or_restricted": [],
  "deviations_from_contract": [],
  "unresolved_risks": []
}
```

---

# 14. Coding Constraints for LLM Implementer

The coding LLM must follow these constraints:

```text
do not implement model adapter
do not implement MCP
do not implement patch applier
do not implement Git write
do not implement network fetch
do not implement background daemon
do not modify L0
do not modify completed Initiator internals unless unavoidable and explicitly justified
do not use shell helpers except safe_subprocess precheck
do not add hosted dependencies
do not add non-standard dependencies unless already present or justified
```

Preferred implementation:

```text
standard library first
jsonschema only if already used or acceptable
dataclasses over Pydantic unless project standard says otherwise
pytest tests
schema files as plain JSON
```

---

# 15. Definition of Done

This implementation is done only when:

```text
all target files exist
all schemas exist
all tests exist
all tests pass
source writes are blocked by default
runtime writes under .agentx-init/security work
L0 writes are blocked
protected path writes are blocked
path traversal is blocked
symlink escape is blocked
subprocess is blocked by default
network is blocked by default
secret redaction works
OpenCode-style read/edit/write/patch/shell concepts are represented safely
Agent_X Initiator integration is verified or failure is explicitly recorded
evidence records are written
completion record exists
```

---

# 16. Final Implementation Sequence for Coding Agent

Use this exact sequence:

```text
1. Create tools/agentx_evolve package skeleton.
2. Create security_models.py.
3. Create schemas.
4. Create sandbox_policy.py.
5. Create path_boundary.py.
6. Create network_policy.py.
7. Create secret_redactor.py.
8. Create safe_file_ops.py.
9. Create safe_subprocess.py.
10. Create initiator_compat.py.
11. Create sandbox_evidence.py.
12. Create tests.
13. Run compileall.
14. Run pytest.
15. Fix failures without weakening safety.
16. Generate completion record.
17. Report final evidence.
```

Do not reorder unless a real dependency requires it.

---

# 17. Coding LLM Handoff Checklist

Before handing this spec to a coding LLM, confirm:

```text
[ ] The target repository is Agent_X.
[ ] The completed Initiator is under tools/agentx_initiator/.
[ ] The new component must be placed under tools/agentx_evolve/security/.
[ ] OpenCode is used only as a design reference.
[ ] No OpenCode source code is copied.
[ ] The implementation language is Python.
[ ] Runtime artifacts go under .agentx-init/security/.
[ ] Source writes are blocked by default.
[ ] Shell is blocked by default.
[ ] Network is blocked by default.
[ ] L0 writes are always blocked.
[ ] Tests must run without GPU, network, hosted model, Bun, or Node.
```

This checklist is mandatory for the first implementation pass.

---

# 18. Final Rating

This v2 implementation spec is rated:

```text
10/10
```

It is complete enough for a coding LLM to implement the Security Sandbox / Filesystem Boundary Layer using only this document plus the repository contents.

It preserves the intended borrowing from OpenCode while integrating into Agent_X’s existing Initiator and stricter safety architecture.
