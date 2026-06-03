# HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_SPEC

```text
document_id: HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen handoff
component_id: AGENTX_HUMAN_REVIEW_APPROVAL
component_name: Human Review / Approval Interface
roadmap_layer: 12
roadmap_phase: Phase C — Human Governance and Approval
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Report Template, MCP Protocol Acceptance Criteria
target_language: Python
canonical_subdirectory: tools/agentx_evolve/human_review/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/human_review/
implementation_mode: deterministic human approval ledger, review queue, and validation interface
previous_version_rating: 9.8/10
current_version_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v4 Review and Upgrade Summary

The v3 implementation spec was very strong and close to frozen, but I would rate it:

```text
9.8/10
```

It already covered the requested areas and added strong lifecycle, scope, replay, expiry, revocation, queue, evidence, review-report, and scoring controls.

It was not fully 10/10 because a few final production-control details were still under-specified:

```text
1. Reviewer authorization was not separated clearly from reviewer identity metadata.
2. Separation-of-duties rules were not explicit enough for requester/reviewer conflicts.
3. Approval invalidation on artifact drift, commit drift, policy drift, or patch-session drift was not strict enough.
4. Append-only history had hashing, but not a strict per-record integrity chain.
5. Clock and timestamp trust rules were not explicit enough for expiry-sensitive validation.
6. Approval validation did not require checking reviewer authority for the risk level/action type.
7. CLI exposure rules needed stronger non-interactive, non-implicit-input boundaries.
8. Simulated approvals for tests needed a clearer boundary from real approvals.
9. The public API did not expose reviewer authorization, integrity-chain verification, or approval invalidation functions.
10. The test pack needed explicit reviewer-authorization, separation-of-duties, drift-invalidation, and integrity-chain tests.
```

This v4 adds those controls and is the final 10/10 implementation spec.

---

# 1. Purpose

This document is the full implementation specification for the **Human Review / Approval Interface**.

The Human Review / Approval Interface provides a deterministic, local, auditable approval ledger for Agent_X. It records human review requests, approval decisions, rejection decisions, deferrals, clarification requests, expiry validation, revocation, and approval lookup/validation.

This layer must not become a bypass around Agent_X safety systems. A human approval may satisfy a human-approval requirement, but it must not override non-overridable safety blocks from:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Tool / MCP Adapter
Governed Patch Execution
Promotion / Release Gate
Failure Taxonomy / Recovery Playbook
```

The implementation must prove that approvals are:

```text
explicit
scoped
traceable
revocable
expiring when required
bound to a known reviewer identity record
bound to exact action/session/artifact/path/commit context
schema-valid
audit-backed
hash-backed for final evidence
not reusable outside their scope
not reusable across unrelated repo/session contexts
not able to override non-overridable safety blocks
```

This layer is not:

```text
interactive UI
email system
chat system
background daemon
human identity provider
cryptographic signing authority
LLM approval simulator
source mutation engine
patch application layer
promotion executor
```

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because this layer controls which high-risk actions can proceed after human review.

## 2.2 Required Supporting Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
```

## 2.3 Conditional Standards

```text
Command Acceptance Criteria, only if CLI commands are exposed
Report Template, if review reports are written as markdown or JSON reports
MCP Protocol Acceptance Criteria, only if human-review requests are exposed through MCP
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
```

---

# 3. Canonical Destination Summary

Create the Human Review package here:

```text
tools/agentx_evolve/human_review/
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
.agentx-init/human_review/
```

The intended package split is:

```text
tools/agentx_evolve/policy/          = Policy / Capability Registry
tools/agentx_evolve/tools/           = Tool / MCP Adapter
tools/agentx_evolve/patch/           = Governed Patch Execution
tools/agentx_evolve/promotion/       = Promotion / Release Gate, if present
tools/agentx_evolve/human_review/    = Human Review / Approval Interface
```

Package import must not:

```text
write files
load mutable queue state
create requests
create decisions
validate approvals as a side effect
start a server
open a port
wait for input
send email
call network
```

---

# 4. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic human approval interface that can:

```text
create a review request
validate review request schema
store requests in a review queue
record approval decisions
record rejection decisions
record deferral decisions
record clarification requests
record revocations
lookup approval decisions by ID
validate whether an approval applies to a requested action
validate approval scope
validate approval expiry
validate approval revocation status
validate reviewer identity metadata
reject forged, missing, stale, expired, revoked, malformed, replayed, cross-repo, or out-of-scope approval IDs
record human-review audit evidence
write evidence manifest
write review report
write completion record
integrate with Policy / Capability Registry
integrate with Tool / MCP Adapter
integrate with Governed Patch Execution
integrate with Promotion / Release Gate
fail closed when approval evidence is incomplete or unsafe
```

This layer must not implement:

```text
interactive UI
email sending
network notifications
chat server
LLM approval simulation
source mutation
patch application
promotion execution
Git write operations
MCP server runtime
background approval daemon
credential provider
identity provider
```

---

# 5. Exact Subdirectory

Canonical implementation subdirectory:

```text
tools/agentx_evolve/human_review/
```

Required package file:

```text
tools/agentx_evolve/human_review/__init__.py
```

All implementation files for this layer must live under that subdirectory unless a deviation is recorded in the completion evidence.

---

# 6. Files to Create

## 6.1 Human Review Package Files

```text
tools/agentx_evolve/human_review/__init__.py
tools/agentx_evolve/human_review/human_review_models.py
tools/agentx_evolve/human_review/review_queue.py
tools/agentx_evolve/human_review/approval_requests.py
tools/agentx_evolve/human_review/approval_decisions.py
tools/agentx_evolve/human_review/approval_lookup.py
tools/agentx_evolve/human_review/approval_expiry.py
tools/agentx_evolve/human_review/approval_revocation.py
tools/agentx_evolve/human_review/approval_scope.py
tools/agentx_evolve/human_review/reviewer_authorization.py
tools/agentx_evolve/human_review/approval_invalidation.py
tools/agentx_evolve/human_review/human_review_integrity.py
tools/agentx_evolve/human_review/human_review_logger.py
tools/agentx_evolve/human_review/human_review_evidence.py
tools/agentx_evolve/human_review/integration_policy.py
tools/agentx_evolve/human_review/integration_tools.py
tools/agentx_evolve/human_review/integration_patch.py
tools/agentx_evolve/human_review/integration_promotion.py
```

## 6.2 Optional CLI File

Create only if CLI commands are needed in this phase:

```text
tools/agentx_evolve/human_review/human_review_cli.py
```

CLI exposure is optional. If added, it must not create approvals from implicit input, environment variables, prompt text, or unauthenticated free text. It must require explicit request ID, reviewer identity metadata, decision type, reason, scope, and expiry/no-expiry justification.

## 6.3 Required Validation Utility

Create this validation utility unless schema validation is fully covered by pytest:

```text
tools/agentx_evolve/tests/validate_human_review_schemas.py
```

If this utility is not created, the review must identify the pytest file that validates all human-review schemas.

---

# 7. Schemas to Create

Create these schema files under:

```text
tools/agentx_evolve/schemas/
```

Required schemas:

```text
human_reviewer_identity.schema.json
human_approval_scope.schema.json
human_review_request.schema.json
human_review_decision.schema.json
human_approval_decision.schema.json
human_rejection_decision.schema.json
human_deferral_decision.schema.json
human_clarification_request.schema.json
human_approval_expiry.schema.json
human_approval_revocation.schema.json
human_review_queue.schema.json
human_review_audit.schema.json
human_review_authorization_policy.schema.json
separation_of_duties_rule.schema.json
human_review_integrity_record.schema.json
approval_invalidation_record.schema.json
human_review_validation_result.schema.json
human_review_evidence_manifest.schema.json
human_review_review_report.schema.json
human_review_completion_record.schema.json
```

## 7.1 General Schema Rules

Each schema must:

```text
require schema_version
require schema_id
require source_component where applicable
require created_at or timestamp where applicable
require warnings
require errors
reject missing required fields
reject unknown status values
reject unknown decision values
represent approval scope explicitly
represent approval expiry explicitly
represent no-expiry justification explicitly when no expiry is used
represent revocation explicitly
represent evidence references explicitly
represent artifact references explicitly
represent request hash and decision hash where applicable
```

## 7.2 Required Decision Values

```text
REQUESTED
APPROVED
REJECTED
DEFERRED
NEEDS_CLARIFICATION
REVOKED
EXPIRED
INVALID
```

## 7.3 Required Validation Status Values

```text
VALID
INVALID
EXPIRED
REVOKED
OUT_OF_SCOPE
MISSING
FORGED_OR_UNTRUSTED
STALE
REPLAYED
CROSS_REPO_OR_SESSION_MISMATCH
BLOCKED
```

## 7.4 Required Request Status Values

```text
PENDING
APPROVED
REJECTED
DEFERRED
NEEDS_CLARIFICATION
CLOSED
EXPIRED
REVOKED
INVALID
```

## 7.5 Schema Example Requirement

Every schema must have at least one valid example object in tests.

Required examples:

```text
valid_reviewer_identity
valid_action_scope
valid_tool_call_scope
valid_patch_session_scope
valid_promotion_scope
valid_review_request
valid_approval_decision
valid_rejection_decision
valid_deferral_decision
valid_clarification_request
valid_revocation_record
valid_review_queue
valid_validation_result_valid
valid_validation_result_expired
valid_validation_result_revoked
valid_validation_result_out_of_scope
valid_validation_result_replayed
valid_human_review_audit_event
valid_human_review_evidence_manifest
valid_human_review_review_report
valid_human_review_completion_record
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
invalid scope fails
invalid decision type fails
malformed evidence references fail when required
malformed hash fields fail when required
```

---

# 8. Approval Lifecycle State Machine

Human review requests and decisions must follow a deterministic lifecycle.

## 8.1 Request Lifecycle

Allowed request transitions:

```text
PENDING -> APPROVED
PENDING -> REJECTED
PENDING -> DEFERRED
PENDING -> NEEDS_CLARIFICATION
PENDING -> EXPIRED
PENDING -> INVALID
DEFERRED -> PENDING
NEEDS_CLARIFICATION -> PENDING
APPROVED -> REVOKED
APPROVED -> EXPIRED
REJECTED -> CLOSED
REVOKED -> CLOSED
EXPIRED -> CLOSED
INVALID -> CLOSED
```

Forbidden transitions:

```text
REJECTED -> APPROVED
REVOKED -> APPROVED
EXPIRED -> APPROVED
CLOSED -> APPROVED
INVALID -> APPROVED
APPROVED -> APPROVED with broader scope
APPROVED -> APPROVED with later expiry unless a new decision is created
```

## 8.2 Decision Lifecycle Rules

```text
An approval decision must reference an existing review request.
A rejection decision must reference an existing review request.
A deferral decision must reference an existing review request.
A clarification request must reference an existing review request.
A revocation must reference an existing approval decision.
A decision must not silently replace a previous decision.
A new approval after rejection requires a new review request.
A broadened approval requires a new review request.
A revoked approval must never validate as active.
An expired approval must never validate as active.
```

---

# 9. Classes and Functions

## 9.1 `human_review_models.py`

### Purpose

Define dataclasses, constants, helper functions, and serialization utilities.

### Required Constants

Decision constants:

```python
DECISION_REQUESTED = "REQUESTED"
DECISION_APPROVED = "APPROVED"
DECISION_REJECTED = "REJECTED"
DECISION_DEFERRED = "DEFERRED"
DECISION_NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
DECISION_REVOKED = "REVOKED"
DECISION_EXPIRED = "EXPIRED"
DECISION_INVALID = "INVALID"
```

Validation constants:

```python
VALIDATION_VALID = "VALID"
VALIDATION_INVALID = "INVALID"
VALIDATION_EXPIRED = "EXPIRED"
VALIDATION_REVOKED = "REVOKED"
VALIDATION_OUT_OF_SCOPE = "OUT_OF_SCOPE"
VALIDATION_MISSING = "MISSING"
VALIDATION_FORGED_OR_UNTRUSTED = "FORGED_OR_UNTRUSTED"
VALIDATION_STALE = "STALE"
VALIDATION_REPLAYED = "REPLAYED"
VALIDATION_CROSS_REPO_OR_SESSION_MISMATCH = "CROSS_REPO_OR_SESSION_MISMATCH"
VALIDATION_BLOCKED = "BLOCKED"
```

Approval scope constants:

```python
SCOPE_ACTION = "ACTION"
SCOPE_TOOL_CALL = "TOOL_CALL"
SCOPE_PATCH_SESSION = "PATCH_SESSION"
SCOPE_FILE_PATH = "FILE_PATH"
SCOPE_COMMIT = "COMMIT"
SCOPE_PROMOTION = "PROMOTION"
SCOPE_SESSION = "SESSION"
```

Reviewer auth constants:

```python
AUTH_LOCAL_CONFIG = "LOCAL_CONFIG"
AUTH_MANUAL_RECORD = "MANUAL_RECORD"
AUTH_SIGNED_RECORD = "SIGNED_RECORD"
AUTH_EXTERNAL_ASSERTION = "EXTERNAL_ASSERTION"
AUTH_UNKNOWN = "UNKNOWN"
```

### Required Dataclasses

#### `HumanReviewerIdentity`

```python
schema_version: str = "1.0"
schema_id: str = "human_reviewer_identity.schema.json"
reviewer_id: str
reviewer_label: str
reviewer_role: str
auth_method: str
auth_evidence_refs: list[str]
created_at: str
warnings: list[str]
errors: list[str]
```

#### `HumanApprovalScope`

```python
schema_version: str = "1.0"
schema_id: str = "human_approval_scope.schema.json"
scope_id: str
scope_type: str
action_id: str | None
tool_call_id: str | None
patch_session_id: str | None
promotion_request_id: str | None
policy_decision_id: str | None
file_paths: list[str]
commit_hashes: list[str]
artifact_hashes: list[str]
session_id: str | None
allowed_effects: list[str]
blocked_effects: list[str]
risk_level: str | None
repo_identity_hash: str | None
warnings: list[str]
errors: list[str]
```

#### `HumanReviewRequest`

```python
schema_version: str = "1.0"
schema_id: str = "human_review_request.schema.json"
request_id: str
created_at: str
source_component: str = "HumanReviewApproval"
requested_by: str
requested_action: str
requested_effect: str
risk_level: str
reason: str
scope: HumanApprovalScope
policy_decision_id: str | None
tool_call_id: str | None
patch_session_id: str | None
promotion_request_id: str | None
artifact_refs: list[str]
evidence_refs: list[str]
status: str
request_hash: str | None
warnings: list[str]
errors: list[str]
```

#### `HumanApprovalDecision`

```python
schema_version: str = "1.0"
schema_id: str = "human_approval_decision.schema.json"
decision_id: str
request_id: str
decided_at: str
source_component: str = "HumanReviewApproval"
reviewer: HumanReviewerIdentity
decision: str
reason: str
scope: HumanApprovalScope
expires_at: str | None
no_expiry_reason: str | None
artifact_refs: list[str]
evidence_refs: list[str]
request_hash: str | None
decision_hash: str | None
warnings: list[str]
errors: list[str]
```

#### `HumanRejectionDecision`

```python
schema_version: str = "1.0"
schema_id: str = "human_rejection_decision.schema.json"
decision_id: str
request_id: str
decided_at: str
source_component: str = "HumanReviewApproval"
reviewer: HumanReviewerIdentity
decision: str
reason: str
artifact_refs: list[str]
evidence_refs: list[str]
request_hash: str | None
decision_hash: str | None
warnings: list[str]
errors: list[str]
```

#### `HumanDeferralDecision`

```python
schema_version: str = "1.0"
schema_id: str = "human_deferral_decision.schema.json"
decision_id: str
request_id: str
decided_at: str
source_component: str = "HumanReviewApproval"
reviewer: HumanReviewerIdentity
decision: str
reason: str
deferred_until: str | None
artifact_refs: list[str]
evidence_refs: list[str]
request_hash: str | None
decision_hash: str | None
warnings: list[str]
errors: list[str]
```

#### `HumanClarificationRequest`

```python
schema_version: str = "1.0"
schema_id: str = "human_clarification_request.schema.json"
clarification_id: str
request_id: str
created_at: str
source_component: str = "HumanReviewApproval"
reviewer: HumanReviewerIdentity
clarification_question: str
artifact_refs: list[str]
evidence_refs: list[str]
request_hash: str | None
clarification_hash: str | None
warnings: list[str]
errors: list[str]
```

#### `HumanApprovalRevocation`

```python
schema_version: str = "1.0"
schema_id: str = "human_approval_revocation.schema.json"
revocation_id: str
approval_decision_id: str
request_id: str
revoked_at: str
source_component: str = "HumanReviewApproval"
revoked_by: HumanReviewerIdentity
reason: str
artifact_refs: list[str]
evidence_refs: list[str]
revocation_hash: str | None
warnings: list[str]
errors: list[str]
```

#### `HumanReviewValidationResult`

```python
schema_version: str = "1.0"
schema_id: str = "human_review_validation_result.schema.json"
validation_id: str
validated_at: str
source_component: str = "HumanReviewApproval"
approval_decision_id: str | None
request_id: str | None
requested_action: str
requested_effect: str
status: str
reason: str
matched_scope: bool
expired: bool
revoked: bool
allowed: bool
non_overridable_block_present: bool
replay_or_context_mismatch: bool
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `HumanReviewQueue`

```python
schema_version: str = "1.0"
schema_id: str = "human_review_queue.schema.json"
queue_id: str
created_at: str
updated_at: str
source_component: str = "HumanReviewApproval"
pending_requests: list[HumanReviewRequest]
resolved_requests: list[str]
deferred_requests: list[str]
clarification_requests: list[str]
queue_version: int
queue_hash: str | None
warnings: list[str]
errors: list[str]
```

#### `HumanReviewAuditEvent`

```python
schema_version: str = "1.0"
schema_id: str = "human_review_audit.schema.json"
audit_id: str
timestamp: str
source_component: str = "HumanReviewApproval"
event_type: str
request_id: str | None
decision_id: str | None
validation_id: str | None
status: str
message: str
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `HumanReviewEvidenceManifest`

```python
schema_version: str = "1.0"
schema_id: str = "human_review_evidence_manifest.schema.json"
component_id: str
validated_commit: str | None
created_at: str
runtime_artifact_root: str
commands: list[dict]
evidence_files: list[dict]
evidence_file_hashes: list[dict]
deviation_register: list[dict]
warnings: list[str]
errors: list[str]
```

### Required Helper Functions

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
from_dict(model_type: type, data: dict) -> object
canonical_json(data: dict) -> str
canonical_hash_payload(data: dict) -> dict
sha256_dict(data: dict) -> str
sha256_file(path: Path) -> str
redact_sensitive_fields(data: dict) -> dict
```

Hashing rules:

```text
hash fields must be excluded from their own hash payload
volatile fields may be excluded only if the schema explicitly marks them volatile
canonical JSON must use sorted keys and stable separators
hash mismatches must fail closed during approval validation
```

Acceptance:

```text
dataclasses instantiate
dataclasses serialize to schema-compatible dictionaries
constants match schema enums
hash helpers are deterministic
redaction helper removes common secret-like fields
no filesystem writes on import
no approval auto-generation on import
```

---

# 10. Runtime Artifacts

Runtime artifact root:

```text
.agentx-init/human_review/
```

Required runtime artifacts:

```text
.agentx-init/human_review/review_queue.json
.agentx-init/human_review/review_request_history.jsonl
.agentx-init/human_review/approval_decision_history.jsonl
.agentx-init/human_review/rejection_decision_history.jsonl
.agentx-init/human_review/deferral_decision_history.jsonl
.agentx-init/human_review/clarification_request_history.jsonl
.agentx-init/human_review/revocation_history.jsonl
.agentx-init/human_review/approval_validation_history.jsonl
.agentx-init/human_review/human_review_audit.jsonl
.agentx-init/human_review/record_integrity_chain.jsonl
.agentx-init/human_review/approval_invalidation_history.jsonl
.agentx-init/human_review/human_review_authorization_policy.json
.agentx-init/human_review/latest_review_request.json
.agentx-init/human_review/latest_approval_decision.json
.agentx-init/human_review/latest_validation_result.json
.agentx-init/human_review/human_review_evidence_manifest.json
.agentx-init/human_review/human_review_review_report.json
.agentx-init/human_review/human_review_completion_record.json
```

Runtime rules:

```text
JSONL history files are append-only.
latest JSON files are written atomically.
review_queue.json is updated atomically.
all artifacts must include timestamps.
all decision artifacts must include reviewer identity metadata.
all approval decisions must include explicit scope.
all approval decisions must include expiry or explicit no-expiry reason.
revoked approvals must not validate as active.
expired approvals must not validate as active.
raw secrets must not be written to evidence.
final evidence artifacts must include SHA-256 hashes.
runtime artifacts must not be written outside .agentx-init/human_review/ unless a deviation is recorded.
```

---

# 11. Review Queue Model

## 11.1 Queue Purpose

The review queue records pending human review requests and resolved request references.

The queue is not an interactive UI. It is a deterministic local artifact that can be inspected by a future UI, CLI, orchestrator, or review tool.

## 11.2 Queue File

```text
.agentx-init/human_review/review_queue.json
```

Required queue fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "human_review_queue.schema.json",
  "queue_id": "string",
  "created_at": "string",
  "updated_at": "string",
  "source_component": "HumanReviewApproval",
  "pending_requests": [],
  "resolved_requests": [],
  "deferred_requests": [],
  "clarification_requests": [],
  "queue_version": 1,
  "queue_hash": "sha256-or-null",
  "warnings": [],
  "errors": []
}
```

## 11.3 Queue Rules

```text
a new request is appended to request history
pending request is added to review_queue.json
approval/rejection resolves the request
deferral or clarification keeps the request pending or records a deferred/clarification status
resolved request ID is recorded
queue updates must be atomic
queue corruption must fail closed
missing queue file may be recreated only if history is preserved
```

## 11.4 Queue Locking and Concurrency Rules

The implementation must prevent lost updates.

Required behavior:

```text
queue read-modify-write uses a lock file or atomic compare-and-replace
queue_version increments on every update
queue_hash is recalculated after every update
stale queue writes are rejected
partial queue writes do not replace the previous valid queue
concurrent decisions for the same pending request must not both resolve it
```

Acceptable implementation:

```text
standard-library lock file using os.open(..., O_CREAT | O_EXCL)
temporary file + atomic os.replace for writes
queue_version check before replace
```

Stale lock rule:

```text
lock acquisition timeout must return BLOCKED/STALE_LOCK rather than proceeding unsafely
stale lock recovery may occur only if the lock records owner, timestamp, and age exceeds a defined safe threshold
stale lock recovery must write audit evidence
```

---

# 12. Approval Request Creation

## 12.1 File

```text
tools/agentx_evolve/human_review/approval_requests.py
```

## 12.2 Required Public Functions

```python
create_review_request(
    requested_by: str,
    requested_action: str,
    requested_effect: str,
    risk_level: str,
    reason: str,
    scope: HumanApprovalScope,
    context: dict,
    repo_root: Path,
) -> HumanReviewRequest

validate_review_request(
    request: HumanReviewRequest,
) -> HumanReviewValidationResult

add_request_to_queue(
    request: HumanReviewRequest,
    repo_root: Path,
) -> dict
```

## 12.3 Required Behavior

```text
create schema-valid HumanReviewRequest
require explicit requested_action
require explicit requested_effect
require explicit reason
require explicit scope
attach policy/tool/patch/promotion references when provided
compute request_hash from canonical request fields
append request to review_request_history.jsonl
update review_queue.json atomically
write latest_review_request.json atomically
```

## 12.4 Request Idempotency Rules

Repeated request creation with the same action/effect/scope/context may either:

```text
return the existing pending request, or
create a new request with a distinct request_id
```

But it must not:

```text
silently overwrite an existing request
silently broaden an existing request
silently mark an existing request approved
create duplicate queue entries with the same request_id
```

## 12.5 Must Not Do

```text
do not auto-approve a request
do not infer broad scope from vague input
do not create unscoped approval requests
do not mutate source files
do not call network
do not create approvals from LLM-generated text alone
```

---

# 13. Approval Decision Recording

## 13.1 File

```text
tools/agentx_evolve/human_review/approval_decisions.py
```

## 13.2 Required Public Functions

```python
record_approval_decision(
    request_id: str,
    reviewer: HumanReviewerIdentity,
    reason: str,
    scope: HumanApprovalScope,
    expires_at: str | None,
    no_expiry_reason: str | None,
    context: dict,
    repo_root: Path,
) -> HumanApprovalDecision

record_rejection_decision(
    request_id: str,
    reviewer: HumanReviewerIdentity,
    reason: str,
    context: dict,
    repo_root: Path,
) -> HumanRejectionDecision

record_deferral_decision(
    request_id: str,
    reviewer: HumanReviewerIdentity,
    reason: str,
    deferred_until: str | None,
    context: dict,
    repo_root: Path,
) -> HumanDeferralDecision

record_clarification_request(
    request_id: str,
    reviewer: HumanReviewerIdentity,
    clarification_question: str,
    context: dict,
    repo_root: Path,
) -> HumanClarificationRequest
```

## 13.3 Required Behavior

Approval decision:

```text
must reference existing request_id
must include reviewer identity
must include reason
must include explicit scope
must not broaden the request scope
must include expires_at or explicit no_expiry_reason
must compute decision_hash
must append to approval_decision_history.jsonl
must write latest_approval_decision.json atomically
must update review_queue.json
```

Rejection decision:

```text
must reference existing request_id
must include reviewer identity
must include reason
must append to rejection_decision_history.jsonl
must update review_queue.json
```

Deferral decision:

```text
must reference existing request_id
must include reviewer identity
must include reason
must append to deferral_decision_history.jsonl
must keep request pending or mark deferred according to schema
```

Clarification request:

```text
must reference existing request_id
must include reviewer identity
must include clarification text
must append to clarification_request_history.jsonl
must keep request pending
```

## 13.4 Decision Idempotency Rules

```text
same decision_id must not be written twice with different content
same request_id must not receive two active approvals with conflicting scopes
repeated write of identical decision may return existing decision with warning
repeated write of changed decision must be rejected
approval after rejection requires a new request
approval after revocation requires a new request
```

## 13.5 Must Not Do

```text
do not approve without a request
do not approve without reviewer identity
do not approve without scope
do not approve without expiry or no-expiry reason
do not approve non-overridable safety violations
do not convert rejection into approval
do not silently broaden requested scope
do not delete old decision history
```

---

# 14. Approval Lookup / Validation

## 14.1 File

```text
tools/agentx_evolve/human_review/approval_lookup.py
```

## 14.2 Required Public Functions

```python
load_approval_decision(
    approval_decision_id: str,
    repo_root: Path,
) -> HumanApprovalDecision | None

find_active_approval_for_action(
    requested_action: str,
    requested_effect: str,
    scope_context: dict,
    repo_root: Path,
) -> HumanApprovalDecision | None

validate_approval_for_action(
    approval_decision_id: str,
    requested_action: str,
    requested_effect: str,
    scope_context: dict,
    repo_root: Path,
) -> HumanReviewValidationResult

validate_approval_id(
    approval_decision_id: str | None,
    required_action: str,
    required_effect: str,
    scope_context: dict,
    repo_root: Path,
) -> HumanReviewValidationResult
```

## 14.3 Validation Rules

An approval is valid only if:

```text
approval decision exists
approval decision is APPROVED
approval references an existing request
approval request hash matches the original request when available
approval decision hash validates when available
approval has not expired
approval has not been revoked
requested action matches approval scope
requested effect is allowed by approval scope
file path / tool call / patch session / promotion request matches approval scope
approval evidence is schema-valid
approval belongs to the current repo/session context when context binding is required
no non-overridable safety block exists in context
```

Return invalid if:

```text
approval is missing
approval is expired
approval is revoked
approval is out of scope
approval decision is malformed
approval references missing request
approval hash does not match
approval attempts to override non-overridable safety block
approval was copied from another repo/session without matching scope evidence
approval was replayed from an incompatible context
```

---

# 15. Exact Scope Matching Semantics

Approval validation must use explicit matching rules.

## 15.1 Exact-Match Required

Exact match is required for:

```text
tool_call_id
patch_session_id
promotion_request_id
policy_decision_id
session_id
commit_hashes when approval is commit-scoped
artifact_hashes when approval is artifact-scoped
```

## 15.2 Subset Match Allowed

Subset match is allowed only when the approval scope is explicitly broader than the requested operation and still within the original request scope.

Examples:

```text
approval for files [A, B] may authorize file A if the original request also covered [A, B]
approval for allowed_effects [VALIDATE, REPORT] may authorize VALIDATE
approval for a patch session may authorize a prechecked artifact from the same patch_session_id
```

## 15.3 Never Implied

These implications are forbidden:

```text
promotion approval does not imply patch approval
patch approval does not imply promotion approval
session approval does not imply future sessions
commit approval does not imply later commits
file path approval does not imply sibling or parent directories
Tool / MCP approval does not imply MCP exposure policy override
human approval does not imply network enablement
human approval does not imply Git write enablement
```

---

# 16. Approval Expiry Handling

## 16.1 File

```text
tools/agentx_evolve/human_review/approval_expiry.py
```

## 16.2 Required Public Functions

```python
is_approval_expired(
    decision: HumanApprovalDecision,
    now_iso: str | None = None,
) -> bool

mark_expired_approvals(
    repo_root: Path,
    now_iso: str | None = None,
) -> list[HumanReviewValidationResult]
```

## 16.3 Rules

```text
expired approvals must not validate as active
missing expires_at is allowed only if decision records explicit no_expiry_reason
expiry comparison must use UTC ISO timestamps
expiry validation must be deterministic
expiry checks must not mutate source files
mark_expired_approvals may write validation evidence but must not rewrite original decisions
invalid timestamps must fail closed
```

---

# 17. Approval Revocation Handling

## 17.1 File

```text
tools/agentx_evolve/human_review/approval_revocation.py
```

## 17.2 Required Public Functions

```python
revoke_approval(
    approval_decision_id: str,
    revoked_by: HumanReviewerIdentity,
    reason: str,
    repo_root: Path,
) -> HumanApprovalRevocation

is_approval_revoked(
    decision: HumanApprovalDecision,
    repo_root: Path | None = None,
) -> bool
```

## 17.3 Rules

```text
revoked approvals must not validate as active
revocation must append to revocation_history.jsonl
revocation must include reviewer identity
revocation must include reason
revocation must preserve original decision evidence
revocation must not delete original approval record
revocation must not rewrite original approval record except through an explicit new revocation record
revocation history takes precedence over stale approval latest artifact
```

---

# 18. Approval Scope Handling

## 18.1 File

```text
tools/agentx_evolve/human_review/approval_scope.py
```

## 18.2 Required Public Functions

```python
scope_matches_action(
    scope: HumanApprovalScope,
    requested_action: str,
    requested_effect: str,
    scope_context: dict,
) -> bool

normalize_scope(
    scope: HumanApprovalScope,
) -> HumanApprovalScope

validate_scope(
    scope: HumanApprovalScope,
) -> HumanReviewValidationResult

assert_scope_not_broadened(
    requested_scope: HumanApprovalScope,
    approval_scope: HumanApprovalScope,
) -> HumanReviewValidationResult
```

## 18.3 Scope Rules

```text
approval scope must be explicit
approval scope must not default to all files
approval scope must not default to all sessions
approval scope must not default to all future actions
file path scopes must be normalized before comparison
file path scopes must remain within approved boundaries when boundary context is provided
promotion approval must not imply patch approval
patch approval must not imply promotion approval
tool-call approval must not imply arbitrary future tool calls
session approval must not imply future sessions
commit approval must not imply later commits
approval scope must not be broader than the request scope
```

---

# 19. Reviewer Authorization and Separation of Duties

## 19.1 File

```text
tools/agentx_evolve/human_review/reviewer_authorization.py
```

## 19.2 Required Public Functions

```python
load_reviewer_authorization_policy(repo_root: Path) -> dict
validate_reviewer_authorization(
    reviewer: HumanReviewerIdentity,
    requested_action: str,
    requested_effect: str,
    risk_level: str,
    scope: HumanApprovalScope,
    context: dict,
    repo_root: Path,
) -> HumanReviewValidationResult

validate_separation_of_duties(
    reviewer: HumanReviewerIdentity,
    request: HumanReviewRequest,
    context: dict,
) -> HumanReviewValidationResult
```

## 19.3 Reviewer Authorization Policy

Create or support this policy artifact:

```text
.agentx-init/human_review/human_review_authorization_policy.json
```

The policy must define:

```text
which reviewer roles may approve which action types
which reviewer roles may approve which risk levels
which reviewer roles may revoke approvals
which reviewer roles may close or defer requests
which requester/reviewer combinations are forbidden
whether dual approval is required for critical actions
whether signed identity evidence is required for critical actions
```

## 19.4 Required Rules

```text
identity metadata alone does not imply authorization
reviewer must be authorized for requested_action, requested_effect, risk_level, and scope
requester must not approve their own request unless policy explicitly allows it for low-risk local-only actions
implementation worker must not approve its own source mutation
model/LLM-generated approval text must never count as human approval
critical actions may require dual approval if policy says so
revocation must be allowed only for authorized reviewer roles or original approver when policy permits
missing authorization policy fails closed for high-risk or mutating approvals
```

## 19.5 Separation-of-Duties Tests

Required tests:

```text
test_reviewer_identity_does_not_imply_authorization
test_unauthorized_reviewer_cannot_approve_high_risk_action
test_requester_cannot_self_approve_source_mutation
test_implementation_worker_cannot_approve_own_patch
test_dual_approval_required_when_policy_requires_it
test_missing_authorization_policy_fails_closed_for_mutating_action
```

---

# 20. Approval Invalidation and Drift Handling

## 20.1 File

```text
tools/agentx_evolve/human_review/approval_invalidation.py
```

## 20.2 Required Public Functions

```python
check_approval_context_drift(
    decision: HumanApprovalDecision,
    current_context: dict,
    repo_root: Path,
) -> HumanReviewValidationResult

invalidate_approval_on_context_drift(
    approval_decision_id: str,
    drift_reason: str,
    current_context: dict,
    repo_root: Path,
) -> dict

append_approval_invalidation_record(
    approval_decision_id: str,
    reason: str,
    context: dict,
    repo_root: Path,
) -> dict
```

## 20.3 Drift Rules

An approval must become invalid or require revalidation when any bound context changes:

```text
repo_identity_hash changes
commit hash changes for commit-scoped approval
patch artifact hash changes for patch-scoped approval
promotion request hash changes for promotion-scoped approval
policy decision hash changes for policy-scoped approval
tool call hash changes for tool-call-scoped approval
review request hash changes or cannot be verified
approval decision hash changes or cannot be verified
queue integrity chain cannot be verified
reviewer authorization policy changed in a way that would no longer authorize the decision
```

Drift must return one of:

```text
STALE
REPLAYED
CROSS_REPO_OR_SESSION_MISMATCH
FORGED_OR_UNTRUSTED
INVALID
```

## 20.4 Invalidation Evidence

Create:

```text
.agentx-init/human_review/approval_invalidation_history.jsonl
```

Each invalidation record must include:

```text
approval_decision_id
request_id
drift_reason
old_context_hash where available
new_context_hash where available
timestamp
validation result ID
evidence_refs
warnings/errors
```

---

# 21. Append-Only Integrity Chain

## 21.1 File

```text
tools/agentx_evolve/human_review/human_review_integrity.py
```

## 21.2 Required Public Functions

```python
append_integrity_record(
    event_type: str,
    artifact_path: str,
    artifact_sha256: str,
    repo_root: Path,
) -> dict

verify_human_review_integrity_chain(repo_root: Path) -> HumanReviewValidationResult

compute_record_chain_hash(
    previous_hash: str | None,
    event_payload: dict,
) -> str
```

## 21.3 Integrity Artifact

Create:

```text
.agentx-init/human_review/record_integrity_chain.jsonl
```

Each record must include:

```text
sequence_number
timestamp
event_type
artifact_path
artifact_sha256
previous_record_hash
record_hash
source_component
warnings
errors
```

Rules:

```text
sequence_number must increase monotonically
previous_record_hash must match the prior record_hash
record_hash must exclude its own record_hash field
missing or broken chain fails validation
manual edits after final DONE invalidate previous DONE evidence
hash-chain verification must be part of final schema/evidence validation
```

---

# 22. Clock, Timestamp, and Expiry Trust Rules

Expiry-sensitive validation must use deterministic UTC timestamps.

Required rules:

```text
all timestamps use UTC ISO format
invalid timestamp format fails closed
expiry comparison must not use local timezone assumptions
clock_skew_warning is recorded if current time is earlier than evidence timestamps
approval cannot be created with expires_at earlier than decided_at
no-expiry approvals require no_expiry_reason and may be forbidden by authorization policy
tests must use injected now_iso rather than real wall-clock time where possible
```

---

# 23. CLI and Simulated-Approval Boundary

CLI is optional. If implemented, it must remain deterministic and non-interactive for tests.

Required CLI rules if `human_review_cli.py` exists:

```text
no approval from implicit environment variables
no approval from prompt text alone
no approval from LLM output alone
no hidden default reviewer
no default broad scope
no default no-expiry approval
requires explicit request_id, reviewer_id, decision type, reason, scope, and expiry/no-expiry justification
all CLI-created decisions must pass the same schema, authorization, scope, expiry, and evidence rules as API-created decisions
```

Simulated approvals are allowed only in tests when clearly marked:

```text
auth_method = MANUAL_RECORD or TEST_FIXTURE according to schema/policy
test fixture approvals must not be accepted in production validation context
production validation must reject TEST_FIXTURE approvals unless policy explicitly marks test mode
```

---

# 24. Human Review Logger

## 19.1 File

```text
tools/agentx_evolve/human_review/human_review_logger.py
```

## 19.2 Required Public Functions

```python
append_review_request(request: HumanReviewRequest, repo_root: Path) -> dict
append_approval_decision(decision: HumanApprovalDecision, repo_root: Path) -> dict
append_rejection_decision(decision: HumanRejectionDecision, repo_root: Path) -> dict
append_deferral_decision(decision: HumanDeferralDecision, repo_root: Path) -> dict
append_clarification_request(decision: HumanClarificationRequest, repo_root: Path) -> dict
append_revocation(revocation: HumanApprovalRevocation, repo_root: Path) -> dict
append_validation_result(result: HumanReviewValidationResult, repo_root: Path) -> dict
append_audit_event(event: HumanReviewAuditEvent, repo_root: Path) -> dict
write_latest_review_request(request: HumanReviewRequest, repo_root: Path) -> dict
write_latest_approval_decision(decision: HumanApprovalDecision, repo_root: Path) -> dict
write_latest_validation_result(result: HumanReviewValidationResult, repo_root: Path) -> dict
```

## 19.3 Rules

```text
create .agentx-init/human_review/ if missing
append JSONL only for histories
write latest JSON atomically
redact secrets before persistence
preserve malformed existing JSONL lines
never delete approval history
never rewrite approval history to hide prior decisions
never replace a valid latest artifact with a schema-invalid artifact
```

---

# 25. Human Review Evidence

## 20.1 File

```text
tools/agentx_evolve/human_review/human_review_evidence.py
```

## 20.2 Required Public Functions

```python
write_human_review_evidence_manifest(repo_root: Path, context: dict) -> dict
write_human_review_review_report(repo_root: Path, context: dict) -> dict
write_human_review_completion_record(repo_root: Path, context: dict) -> dict
collect_human_review_evidence_files(repo_root: Path) -> list[Path]
hash_human_review_evidence(repo_root: Path) -> list[dict]
```

## 20.3 Required Evidence Manifest

Create:

```text
.agentx-init/human_review/human_review_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "human_review_evidence_manifest.schema.json",
  "component_id": "AGENTX_HUMAN_REVIEW_APPROVAL",
  "validated_commit": "<commit hash or null>",
  "created_at": "<UTC timestamp>",
  "runtime_artifact_root": ".agentx-init/human_review/",
  "commands": [
    {
      "name": "compileall",
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve/human_review",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path or null>",
      "output_sha256": "<sha256 or null>"
    },
    {
      "name": "pytest",
      "command": "<pytest command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path or null>",
      "output_sha256": "<sha256 or null>"
    },
    {
      "name": "schema_validation",
      "command": "<schema validation command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path or null>",
      "output_sha256": "<sha256 or null>"
    }
  ],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "deviation_register": [],
  "warnings": [],
  "errors": []
}
```

Hashing rule:

```text
SHA-256 hashes are required for final evidence artifacts.
Use Python standard library hashlib if no project hash helper exists.
A DONE verdict is invalid if evidence hashes are missing.
```

## 20.4 Required Review Report

Create:

```text
.agentx-init/human_review/human_review_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "human_review_review_report.schema.json",
  "component_id": "AGENTX_HUMAN_REVIEW_APPROVAL",
  "review_document_id": "HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_SPEC",
  "review_document_version": "v4.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/human_review/human_review_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/human_review/human_review_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/human_review/human_review_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

---

# 26. Reviewer Identity and Non-Forgeability Rules

This layer does not authenticate humans by itself, but it must record enough identity evidence to prevent anonymous or forged local approvals from being treated as normal approvals.

Required behavior:

```text
reviewer_id is required
reviewer_label is required
reviewer_role is required
auth_method is required
auth_method UNKNOWN is allowed only for test fixtures or explicitly degraded records
reviewer identity must be included in every decision
approval validation may reject decisions with insufficient auth evidence when policy requires stronger assurance
decision_hash must be generated from canonical decision fields when possible
request_hash must bind approval to the original request when possible
copied decision IDs without matching evidence must return FORGED_OR_UNTRUSTED or INVALID
```

This layer must not claim cryptographic identity assurance unless an actual signing or identity mechanism exists.

If `AUTH_SIGNED_RECORD` is used, the schema must include signature evidence references, and validation must fail closed when the signature evidence is missing or malformed.

---

# 27. Replay and Cross-Context Prevention

Approval validation must prevent replay outside the scope where the approval was granted.

Required checks when context values are available:

```text
repo_identity_hash matches
session_id matches when session-scoped
tool_call_id matches when tool-call-scoped
patch_session_id matches when patch-scoped
promotion_request_id matches when promotion-scoped
commit_hash matches when commit-scoped
artifact_hashes match when artifact-scoped
request_hash matches the original request record
decision_hash matches the approval decision record
```

If required context binding is missing:

```text
return BLOCKED or FORGED_OR_UNTRUSTED
write validation evidence
never silently accept the approval
```

---

# 28. Non-Overridable Safety Blocks

Human approval must not override non-overridable safety blocks.

Non-overridable blocks include:

```text
sandbox-denied path
source write outside allowed boundary
blocked L0 or protected kernel mutation
raw shell command
network disabled by policy
Git write disabled by current phase
MCP mutating tool exposure disabled by policy
failed required tests for promotion
missing evidence for promotion
unresolved BLOCKER in review report
schema-invalid patch/session/promotion record
malformed approval request
approval scope mismatch
expired approval
revoked approval
```

Human approval may satisfy:

```text
explicit human approval requirement
high-risk action acknowledgement
promotion sign-off when all technical gates already pass
patch session approval when sandbox/policy/patch prechecks already pass
manual acceptance of non-blocking deviation
```

Human approval must not convert a technical `FAIL` into `PASS`.

---

# 29. Integration with Policy / Capability Registry

## 24.1 File

```text
tools/agentx_evolve/human_review/integration_policy.py
```

## 24.2 Required Public Functions

```python
create_review_request_from_policy_decision(
    policy_decision: dict,
    context: dict,
    repo_root: Path,
) -> HumanReviewRequest

validate_approval_for_policy_decision(
    policy_decision: dict,
    approval_decision_id: str,
    repo_root: Path,
) -> HumanReviewValidationResult
```

## 24.3 Required Behavior

```text
policy decision NEEDS_APPROVAL may create review request
policy decision BLOCK must not be converted to approval unless the policy marks it overridable
approval validation must check requested effect and scope
approval validation must return invalid for expired/revoked/out-of-scope approval
human approval may satisfy approval requirement
human approval must not override BLOCK caused by non-overridable policy rule
policy decision ID must be included in evidence_refs when available
```

If Policy / Capability Registry is missing:

```text
creation from policy decision returns BLOCKED/MISSING dependency result or safe stub
validation for policy decision fails closed
no approval may be treated as policy-authorized by default
```

---

# 30. Integration with Tool / MCP Adapter

## 25.1 File

```text
tools/agentx_evolve/human_review/integration_tools.py
```

## 25.2 Required Public Functions

```python
create_review_request_from_tool_call(
    tool_call: dict,
    tool_definition: dict,
    policy_decision: dict | None,
    repo_root: Path,
) -> HumanReviewRequest

validate_approval_for_tool_call(
    tool_call: dict,
    approval_decision_id: str,
    repo_root: Path,
) -> HumanReviewValidationResult
```

## 25.3 Required Behavior

```text
tool calls requiring human approval can create review requests
approval must match tool_call_id or exact scope
approval must match requested effect
approval must validate against policy/sandbox context when provided
MCP_CLIENT cannot use human approval to bypass MCP exposure policy
approval cannot authorize raw shell, network default, Git write, or unsafe MCP exposure
validation result must be schema-valid
validation evidence must be written
```

If Tool / MCP Adapter is missing:

```text
integration functions return safe missing-dependency results
no approval is treated as tool-authorized by default
```

---

# 31. Integration with Governed Patch Execution

## 26.1 File

```text
tools/agentx_evolve/human_review/integration_patch.py
```

## 26.2 Required Public Functions

```python
create_review_request_from_patch_session(
    patch_session: dict,
    risk_summary: dict,
    repo_root: Path,
) -> HumanReviewRequest

validate_approval_for_patch_session(
    patch_session: dict,
    approval_decision_id: str,
    repo_root: Path,
) -> HumanReviewValidationResult
```

## 26.3 Required Behavior

```text
patch session approval must be scoped to patch_session_id
patch approval must include affected file paths or approved patch artifact refs
approval must not authorize unrelated patch sessions
approval must not authorize promotion automatically
approval must not override sandbox-denied paths
approval must not override failed patch prechecks
approval must not override patch contract blockers
revoked or expired patch approvals must block patch application
```

If Governed Patch Execution is missing:

```text
patch integration may be implemented as a safe stub
patch approval validation returns BLOCKED or MISSING dependency
no patch application is authorized by this layer
```

---

# 32. Integration with Promotion / Release Gate

## 27.1 File

```text
tools/agentx_evolve/human_review/integration_promotion.py
```

## 27.2 Required Public Functions

```python
create_review_request_from_promotion_request(
    promotion_request: dict,
    validation_summary: dict,
    repo_root: Path,
) -> HumanReviewRequest

validate_approval_for_promotion(
    promotion_request: dict,
    approval_decision_id: str,
    repo_root: Path,
) -> HumanReviewValidationResult
```

## 27.3 Required Behavior

```text
promotion approval must be scoped to promotion_request_id or exact commit hash
promotion approval must not imply patch approval
promotion approval must not override failed tests
promotion approval must not override missing evidence
promotion approval must not override unresolved BLOCKER
revoked or expired promotion approvals must block promotion
```

If Promotion / Release Gate does not exist yet:

```text
this integration may be implemented as a safe stub that returns BLOCKED or MISSING_DEPENDENCY validation results
```

---

# 33. Public API Contract

The package must expose these stable public functions from `__init__.py` or documented module-level imports:

```python
create_review_request
record_approval_decision
record_rejection_decision
record_deferral_decision
record_clarification_request
validate_approval_id
validate_approval_for_action
revoke_approval
find_active_approval_for_action
validate_reviewer_authorization
validate_separation_of_duties
invalidate_approval_on_context_drift
verify_human_review_integrity_chain
write_human_review_completion_record
```

The package must expose these stable dataclasses:

```text
HumanReviewerIdentity
HumanApprovalScope
HumanReviewRequest
HumanApprovalDecision
HumanRejectionDecision
HumanDeferralDecision
HumanClarificationRequest
HumanApprovalRevocation
HumanReviewValidationResult
HumanReviewQueue
HumanReviewAuditEvent
HumanReviewEvidenceManifest
```

---

# 34. Test Files

Create these test files under:

```text
tools/agentx_evolve/tests/
```

Required tests:

```text
test_human_review_models.py
test_human_review_request_schema.py
test_human_review_decision_schema.py
test_human_review_queue.py
test_approval_request_creation.py
test_approval_decision_recording.py
test_approval_lookup_validation.py
test_approval_expiry.py
test_approval_revocation.py
test_approval_scope.py
test_human_review_logger.py
test_human_review_evidence.py
test_human_review_policy_integration.py
test_human_review_tool_integration.py
test_human_review_patch_integration.py
test_human_review_promotion_integration.py
test_human_review_negative_cases.py
test_human_review_schema_validation.py
test_reviewer_authorization.py
test_separation_of_duties.py
test_approval_invalidation.py
test_human_review_integrity_chain.py
```

Optional CLI test, only if CLI is exposed:

```text
test_human_review_cli.py
```

---

# 35. Test Cases

## 30.1 Required Positive Tests

```text
test_models_instantiate
test_review_request_schema_accepts_valid_request
test_approval_decision_schema_accepts_valid_approval
test_rejection_decision_schema_accepts_valid_rejection
test_deferral_decision_schema_accepts_valid_deferral
test_clarification_request_schema_accepts_valid_clarification
test_review_queue_created
test_create_review_request_writes_history
test_create_review_request_updates_queue
test_record_approval_decision_writes_history
test_record_rejection_decision_writes_history
test_record_deferral_decision_writes_history
test_record_clarification_request_writes_history
test_lookup_existing_approval_decision
test_validate_active_approval_for_matching_action
test_policy_needs_approval_creates_review_request
test_tool_call_needs_approval_creates_review_request
test_patch_session_review_request_scopes_to_patch_session
test_promotion_review_request_scopes_to_promotion_request
test_evidence_manifest_written
test_review_report_written
test_completion_record_schema_validates
```

## 30.2 Required Negative Tests

```text
test_missing_request_id_rejected
test_approval_without_request_blocks
test_approval_without_reviewer_identity_rejected
test_approval_without_scope_rejected
test_approval_without_reason_rejected
test_approval_without_expiry_or_no_expiry_reason_rejected
test_expired_approval_invalid
test_revoked_approval_invalid
test_out_of_scope_approval_invalid
test_approval_for_wrong_tool_call_invalid
test_approval_for_wrong_patch_session_invalid
test_patch_approval_does_not_authorize_promotion
test_promotion_approval_does_not_authorize_patch
test_approval_cannot_override_sandbox_denial
test_approval_cannot_override_policy_block
test_approval_cannot_override_failed_tests_for_promotion
test_forged_approval_id_invalid
test_replayed_approval_invalid
test_cross_repo_approval_invalid_when_context_bound
test_stale_queue_update_rejected
test_concurrent_queue_update_does_not_lose_request
test_rejected_request_cannot_be_approved_without_new_request
test_scope_broadening_rejected
test_malformed_queue_fails_closed
test_secret_like_value_redacted_in_evidence
test_unauthorized_reviewer_cannot_approve
test_requester_cannot_self_approve_mutating_action
test_artifact_drift_invalidates_approval
test_integrity_chain_break_fails_validation
test_test_fixture_approval_rejected_in_production_context
```

## 30.3 Schema Tests

Every schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
invalid scope fails
invalid timestamp where applicable fails or is rejected by validation layer
invalid decision/reference relationship fails where applicable
hash mismatch fails where applicable
```

---

# 36. Implementation Order

Implement in this exact order:

```text
1. tools/agentx_evolve/human_review/__init__.py
2. human_review_models.py
3. human review schemas
4. human_review_logger.py
5. human_review_evidence.py
6. review_queue.py
7. approval_scope.py
8. reviewer_authorization.py
9. approval_invalidation.py
10. human_review_integrity.py
11. approval_requests.py
12. approval_decisions.py
13. approval_expiry.py
14. approval_revocation.py
15. approval_lookup.py
16. integration_policy.py
17. integration_tools.py
18. integration_patch.py
19. integration_promotion.py
20. tests
21. completion evidence
```

Rationale:

```text
models first
schemas second
logger/evidence before queue mutations
queue before request creation
scope before approval validation
reviewer authorization before approval decisions
drift and integrity controls before lookup/validation is considered complete
decisions before lookup
expiry/revocation before final validation
integrations after core approval behavior exists
tests after public surfaces exist
```

---

# 37. Acceptance Criteria

## 32.1 Structural Acceptance

```text
[ ] tools/agentx_evolve/human_review/ exists
[ ] required package files exist
[ ] required schemas exist
[ ] required tests exist
[ ] runtime artifact root is .agentx-init/human_review/
```

## 32.2 Functional Acceptance

```text
[ ] review requests can be created
[ ] review requests are schema-valid
[ ] review queue is updated atomically
[ ] approval decisions can be recorded
[ ] rejection decisions can be recorded
[ ] deferral decisions can be recorded
[ ] clarification requests can be recorded
[ ] revocations can be recorded
[ ] approval decisions can be looked up
[ ] approval validation checks scope
[ ] approval validation checks expiry
[ ] approval validation checks revocation
[ ] approval validation checks identity/evidence trust when required
[ ] approval validation rejects missing/malformed/forged/stale/replayed decisions
[ ] reviewer authorization is checked
[ ] separation-of-duties rules are enforced
[ ] approval invalidates on bound artifact/context drift
[ ] integrity chain verifies final evidence
```

## 32.3 Integration Acceptance

```text
[ ] Policy / Capability Registry integration creates and validates approval requirements
[ ] Tool / MCP Adapter integration validates human approval IDs for tool calls
[ ] Governed Patch Execution integration validates patch-session-scoped approvals or blocks safely if patch layer unavailable
[ ] Promotion / Release Gate integration validates promotion-scoped approvals or blocks safely if promotion layer unavailable
```

## 32.4 Safety Acceptance

```text
[ ] approval cannot override sandbox denial
[ ] approval cannot override non-overridable policy block
[ ] approval cannot override failed promotion validation
[ ] approval cannot authorize unrelated files/actions/sessions
[ ] expired approval blocks
[ ] revoked approval blocks
[ ] approval without scope is invalid
[ ] approval without reviewer identity is invalid
[ ] approval without expiry or no-expiry reason is invalid
[ ] evidence is written for request/decision/validation
[ ] evidence hashes are written for final evidence artifacts
[ ] secrets are redacted before evidence
[ ] no source mutation occurs
```

---

# 38. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/human_review
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_human_review_models.py \
  tools/agentx_evolve/tests/test_human_review_request_schema.py \
  tools/agentx_evolve/tests/test_human_review_decision_schema.py \
  tools/agentx_evolve/tests/test_human_review_queue.py \
  tools/agentx_evolve/tests/test_approval_request_creation.py \
  tools/agentx_evolve/tests/test_approval_decision_recording.py \
  tools/agentx_evolve/tests/test_approval_lookup_validation.py \
  tools/agentx_evolve/tests/test_approval_expiry.py \
  tools/agentx_evolve/tests/test_approval_revocation.py \
  tools/agentx_evolve/tests/test_approval_scope.py \
  tools/agentx_evolve/tests/test_human_review_logger.py \
  tools/agentx_evolve/tests/test_human_review_evidence.py \
  tools/agentx_evolve/tests/test_human_review_policy_integration.py \
  tools/agentx_evolve/tests/test_human_review_tool_integration.py \
  tools/agentx_evolve/tests/test_human_review_patch_integration.py \
  tools/agentx_evolve/tests/test_human_review_promotion_integration.py \
  tools/agentx_evolve/tests/test_human_review_negative_cases.py \
  tools/agentx_evolve/tests/test_human_review_schema_validation.py
test_reviewer_authorization.py
test_separation_of_duties.py
test_approval_invalidation.py
test_human_review_integrity_chain.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_human_review_schemas.py
git status --short
```

If `validate_human_review_schemas.py` is not implemented, the pytest schema validation test must cover the same cases and the review must record that substitution.

Required result:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

No validation command may require:

```text
GPU
network
hosted model
LLM
MCP server
human interactive input
browser UI
email service
```

---

# 39. Completion Evidence

After implementation, write:

```text
.agentx-init/human_review/human_review_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "human_review_completion_record.schema.json",
  "component_id": "AGENTX_HUMAN_REVIEW_APPROVAL",
  "component_name": "Human Review / Approval Interface",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "canonical_subdirectory": "tools/agentx_evolve/human_review/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/human_review/",
  "basis_documents": [
    "HUMAN_REVIEW_APPROVAL_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_SPEC_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "policy_integration_verified": [],
  "tool_adapter_integration_verified": [],
  "patch_integration_verified": [],
  "promotion_integration_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/human_review/human_review_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/human_review/human_review_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 40. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places files outside tools/agentx_evolve/human_review/ without recorded deviation
writes runtime artifacts outside .agentx-init/human_review/ without recorded deviation
creates approval decisions without reviewer identity
creates approval decisions without explicit scope
creates approval decisions without expiry or no-expiry reason
allows expired approvals to validate
allows revoked approvals to validate
allows out-of-scope approvals to validate
allows forged approval IDs to validate
allows replayed or cross-context approvals to validate when context binding is required
allows stale queue updates to overwrite newer state
allows human approval to override sandbox denial
allows human approval to override non-overridable policy block
allows patch approval to authorize promotion
allows promotion approval to authorize patch application
requires network, browser UI, email, or interactive human input for tests
mutates source files directly
logs unredacted secrets
returns unstructured validation results
raises unhandled exceptions for malformed approvals
```

---

# 41. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and files | 1.0 | Package, schemas, tests, and runtime root exist as specified. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Human review test suite passes with exit code 0. |
| Schema validation | 1.0 | All valid and invalid schema cases pass. |
| Request/queue behavior | 1.0 | Requests are scoped, queued atomically, locked, hashed, and evidenced. |
| Decision behavior | 1.0 | Approval/rejection/deferral/clarification/revocation are distinct and evidenced. |
| Validation behavior | 1.0 | Expiry, revocation, scope, replay, forgery, and context mismatch fail closed. |
| Integration behavior | 1.0 | Policy, Tool/MCP, Patch, and Promotion integrations work or safely stub unavailable dependencies. |
| Evidence/reporting | 1.0 | JSONL histories, manifest, review report, completion record, hashes, and redaction are complete. |
| Safety | 1.0 | No source mutation, no network/UI/email dependency, no non-overridable block bypass. |

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
approval without identity accepted caps score at 4.0
unauthorized reviewer approval accepted caps score at 4.0
self-approval of restricted action accepted caps score at 4.0
approval without scope accepted caps score at 4.0
expired/revoked approval validates caps score at 4.0
drifted approval validates caps score at 4.0
broken integrity chain accepted caps score at 4.0
non-overridable safety block bypass caps score at 4.0
missing evidence manifest caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
missing evidence hashes caps score at 8.0
any required area NOT CHECKED caps score at 8.0
```

---

# 42. Go / No-Go Acceptance Rules

## 37.1 GO Criteria

The layer may be marked DONE only if all are true:

```text
all target files exist
all required schemas exist
all required tests exist
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
review request creation works
approval decision recording works
rejection/deferral/clarification recording works
revocation recording works
approval lookup works
approval validation checks scope
approval validation checks expiry
approval validation checks revocation
approval validation rejects forged/stale/replayed/malformed approvals
Policy / Capability Registry integration works or safely stubs unavailable dependency
Tool / MCP Adapter integration works or safely stubs unavailable dependency
Governed Patch Execution integration works or safely stubs unavailable dependency
Promotion / Release Gate integration works or safely stubs unavailable dependency
non-overridable safety blocks remain non-overridable
runtime evidence is written
evidence manifest exists
review report exists
evidence hashes exist
secrets are redacted
no source mutation occurs directly in this layer
completion record exists
```

## 37.2 NO-GO Criteria

The layer is NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
approval without scope is accepted
approval without reviewer identity is accepted
approval without expiry or no-expiry reason is accepted
expired approval validates as active
revoked approval validates as active
out-of-scope approval validates as active
forged approval validates as active
replayed or cross-context approval validates when context binding is required
approval overrides sandbox denial
approval overrides non-overridable policy block
patch approval authorizes promotion
promotion approval authorizes patch application
runtime evidence is missing
evidence hashes are missing
review report is missing
secrets are logged
source mutation occurs directly in this layer
network/browser/email/interactive input is required for tests
completion record is missing
```

---

# 43. Definition of Done

The Human Review / Approval Interface is done when it can act as the controlled approval ledger for Agent_X.

It must prove:

```text
review requests are schema-valid
review queue is deterministic and atomically updated
approval decisions are schema-valid
rejection decisions are schema-valid
deferral decisions are schema-valid
clarification requests are schema-valid
revocations are schema-valid
approval scope is explicit
approval lookup is deterministic
approval validation checks exact action/effect/scope
approval validation checks request/decision evidence where available
approval expiry is enforced
approval revocation is enforced
approval replay/context mismatch is rejected when context binding is required
approval cannot override non-overridable safety blocks
reviewer identity alone does not imply reviewer authorization
requester cannot self-approve restricted actions
artifact/commit/policy drift invalidates bound approvals
append-only integrity chain verifies
Policy / Capability Registry can consume approval validation results
Tool / MCP Adapter can validate approval IDs
Governed Patch Execution can validate patch-scoped approvals or block safely if unavailable
Promotion / Release Gate can validate promotion-scoped approvals or block safely if unavailable
all review/decision/validation events write evidence
evidence manifest is written
review report is written
evidence hashes are written
no source mutation occurs directly in this layer
no network/browser/email dependency is required
completion record exists
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/human_review
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_human_review_models.py \
  tools/agentx_evolve/tests/test_human_review_request_schema.py \
  tools/agentx_evolve/tests/test_human_review_decision_schema.py \
  tools/agentx_evolve/tests/test_human_review_queue.py \
  tools/agentx_evolve/tests/test_approval_request_creation.py \
  tools/agentx_evolve/tests/test_approval_decision_recording.py \
  tools/agentx_evolve/tests/test_approval_lookup_validation.py \
  tools/agentx_evolve/tests/test_approval_expiry.py \
  tools/agentx_evolve/tests/test_approval_revocation.py \
  tools/agentx_evolve/tests/test_approval_scope.py \
  tools/agentx_evolve/tests/test_human_review_logger.py \
  tools/agentx_evolve/tests/test_human_review_evidence.py \
  tools/agentx_evolve/tests/test_human_review_policy_integration.py \
  tools/agentx_evolve/tests/test_human_review_tool_integration.py \
  tools/agentx_evolve/tests/test_human_review_patch_integration.py \
  tools/agentx_evolve/tests/test_human_review_promotion_integration.py \
  tools/agentx_evolve/tests/test_human_review_negative_cases.py \
  tools/agentx_evolve/tests/test_human_review_schema_validation.py
test_reviewer_authorization.py
test_separation_of_duties.py
test_approval_invalidation.py
test_human_review_integrity_chain.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_human_review_schemas.py
git status --short
```

Expected proof:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

---

# 44. Final Implementation Sequence for Coding Agent

Use this sequence:

```text
1. Create tools/agentx_evolve/human_review/ package.
2. Implement human_review_models.py.
3. Create human review schemas.
4. Implement human_review_logger.py.
5. Implement human_review_evidence.py.
6. Implement review_queue.py.
7. Implement approval_scope.py.
8. Implement approval_requests.py.
9. Implement approval_decisions.py.
10. Implement approval_expiry.py.
11. Implement approval_revocation.py.
12. Implement approval_lookup.py.
13. Implement Policy integration.
14. Implement Tool / MCP Adapter integration.
15. Implement Governed Patch Execution integration.
16. Implement Promotion / Release Gate integration.
17. Create tests.
18. Run compileall.
19. Run pytest.
20. Run schema validation.
21. Verify git status.
22. Write evidence manifest.
23. Write review report.
24. Write completion record.
```

Do not reorder unless required by real import dependencies.

---

# 45. Final Frozen Acceptance Matrix

| Area | Required result |
|---|---|
| Package path | `tools/agentx_evolve/human_review/` exists |
| Runtime root | `.agentx-init/human_review/` only, unless deviation recorded |
| Schemas | all human review schemas exist and validate examples |
| Queue | atomic update, queue version/hash, corruption fails closed |
| Requests | explicit action/effect/reason/scope, no auto-approval |
| Approvals | reviewer identity, reason, scope, expiry/no-expiry, request reference |
| Rejections | request reference, reviewer identity, reason, evidence |
| Deferrals | request remains pending or deferred with evidence |
| Clarifications | request remains pending with clarification evidence |
| Revocations | original approval preserved, revoked approval invalid |
| Expiry | expired approvals do not validate |
| Scope | exact/subset semantics defined, no patch/promotion cross-authorization |
| Identity | reviewer metadata required; forged/stale/replayed approvals fail closed |
| Policy integration | approval satisfies NEEDS_APPROVAL only, not non-overridable BLOCK |
| Tool integration | approval ID validates exact tool/effect/scope only |
| Patch integration | patch approval scoped to patch session/artifacts only |
| Promotion integration | promotion approval scoped to promotion request/commit only |
| Evidence | JSONL histories, latest artifacts, manifest, review report, hashes, completion record |
| Safety | no source mutation, no network/email/browser/human input required for tests |
| Validation | compileall PASS, pytest PASS, schema validation PASS, git status clean or expected runtime artifacts |

---

# 46. Final Freeze Rule

This v4 document is frozen as the implementation specification for the Human Review / Approval Interface.

Allowed future changes:

```text
PATCH: typo fixes, wording cleanup, examples that do not alter behavior
MINOR: additive optional tests, optional CLI notes, extra schema examples
MAJOR: changed approval authority, changed non-overridable block rules, changed runtime artifact root, changed approval scope semantics, changed decision lifecycle, changed DONE criteria
```

Blocked without major revision:

```text
allowing approval without explicit scope
allowing approval without reviewer identity
allowing approval without expiry or no-expiry reason
allowing approval to override sandbox denial
allowing approval to override non-overridable policy block
allowing patch approval to authorize promotion
allowing promotion approval to authorize patch application
removing evidence logging
removing evidence hashes
removing review report or completion record
requiring network/UI/email/human interactive input for validation tests
```

---

# 47. Final Rating

This v4 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, files, schemas, dataclasses, functions, runtime artifacts, review queue behavior, approval request creation, distinct approval/rejection/deferral/clarification/revocation records, approval lookup and validation, exact scope semantics, expiry, revocation, reviewer identity, reviewer authorization, separation of duties, replay prevention, drift invalidation, append-only integrity chain, evidence hashing, review report, completion record, integration boundaries, fallback behavior, CLI/simulated-approval boundaries, test files, test cases, implementation order, acceptance criteria, scoring rules, GO/NO-GO rules, and Definition of Done for the Human Review / Approval Interface.
```
