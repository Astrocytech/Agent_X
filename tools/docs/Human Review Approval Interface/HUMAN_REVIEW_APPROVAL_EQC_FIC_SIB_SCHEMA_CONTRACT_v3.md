# HUMAN_REVIEW_APPROVAL_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: HUMAN_REVIEW_APPROVAL_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_HUMAN_REVIEW_APPROVAL
component_name: Human Review / Approval Interface
roadmap_layer: 12
roadmap_phase: Phase C — Human Governance Boundary
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria, Report Template
optional_standards: ES
risk_level: critical
target_language: Python
canonical_subdirectory: tools/agentx_evolve/human_review/
runtime_artifact_root: .agentx-init/human_review/
contract_role: controlling contract for human review, approval, rejection, deferral, clarification, expiry, revocation, evidence, approval consumption, and non-overridable safety boundaries
previous_version_rating: 9.7/10
current_version_rating: 10/10
```

---

# 0. v3 Review and Upgrade Summary

## 0.1 v2 Rating

The v2 controlling contract was strong and close to final. I would rate it:

```text
9.7/10
```

It already covered the core 10/10 structure:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
Human Approval Authority Model
Human Review Request Schema
Human Approval Decision Schema
Human Rejection Decision Schema
Human Deferral / Clarification Schema
Approval Scope Schema
Approval Expiry / Revocation Schema
Human Reviewer Identity Schema
Review Queue Schema
Approval Evidence Schema
Role Permission Matrix
Approval Boundary Rules
Non-Overridable Safety Rules
OpenCode borrowing notes
Agent_X integration notes
approval state machine
approval locking and idempotency
reviewer independence
quorum rules
fingerprint binding
evidence hashing and immutability
Definition of Done
No-Go Conditions
```

It was not fully 10/10 because a few implementation-control details were still under-specified:

```text
1. Section numbering had formatting drift, making later references less stable.
2. The schema list did not include dedicated validation-result, quorum, supersession, transition, and reviewer-assignment records.
3. Approval validation returned a generic dict instead of a schema-valid approval validation result.
4. Canonicalization rules for paths, commands, commits, hashes, and action fingerprints were not explicit enough.
5. Time/clock rules were not explicit enough for expiry, revocation, and evidence ordering.
6. Queue assignment, reviewer reassignment, and reviewer unavailability were not defined.
7. Break-glass/emergency approval policy was not explicitly blocked by default.
8. Deviation register rules were not strict enough for accepted exceptions.
9. Privacy/minimization rules for human identity and review comments needed stronger bounds.
10. The final freeze rule needed explicit triggers for validation-result, canonicalization, and break-glass semantics.
```

## 0.2 v3 Improvements

This v3 adds:

```text
stable section numbering
additional schema contracts for validation result, quorum, supersession, state transition, reviewer assignment, and deviation register
schema-valid ApprovalValidationResult contract
canonicalization and fingerprint normalization rules
trusted time and ordering rules
queue assignment and reassignment rules
break-glass policy blocked by default
deviation register acceptance rules
privacy and minimization rules
expanded tests and No-Go Conditions
stronger final freeze rule
```

Final v3 rating:

```text
10/10
```

---

# 1. Purpose

This document defines the controlling contract for the **Human Review / Approval Interface** in Agent_X.

This layer provides a structured human governance boundary for high-risk actions. It records review requests, human decisions, approval scopes, rejection reasons, clarification requests, expiry rules, revocation events, reviewer identity, and evidence.

The layer exists to make human review explicit, auditable, bounded, and non-bypassable.

It must ensure that human approval can satisfy an approval requirement but cannot override non-overridable safety controls.

Core rule:

```text
Human approval may authorize a specific action within a specific scope.
Human approval must be revalidated immediately before use.
Human approval must be consumed atomically when single-use or max-use limited.
Human approval must not override policy denial, sandbox denial, schema failure, invalid tool calls, blocked trust tiers, source-boundary violations, missing evidence, invalid reviewer identity, or stale action fingerprints.
```

---

# 2. Scope

## 2.1 Required in This Layer

This layer must define and implement contracts for:

```text
human review request creation
human approval decisions
human rejection decisions
human deferral decisions
human clarification decisions
approval scope
approval expiry
approval revocation
reviewer identity
review queue state
approval evidence
review audit logs
approval lookup and validation
approval binding to tool calls, patch sessions, promotion gates, and policy decisions
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
LLM worker
model adapter
patch generation
patch execution
source mutation
Git write operations
promotion execution
MCP server runtime
email sending
chat notification service
background daemon
external identity provider integration by default
```

The Human Review / Approval Interface records and validates human decisions. It does not perform the risky action itself.

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because this layer controls whether high-risk Agent_X actions can proceed after human review.

It affects:

```text
source mutation approval
patch application approval
rollback approval
Git write approval
promotion approval
network/provider approval
model/provider approval
high-risk tool execution approval
manual override handling
review evidence integrity
```

The layer must fail closed.

## 3.2 Required Supporting Standard: FIC

FIC is required because the layer has concrete implementation files.

Expected files include:

```text
tools/agentx_evolve/human_review/__init__.py
tools/agentx_evolve/human_review/review_models.py
tools/agentx_evolve/human_review/review_queue.py
tools/agentx_evolve/human_review/review_policy.py
tools/agentx_evolve/human_review/review_evidence.py
tools/agentx_evolve/human_review/approval_validator.py
tools/agentx_evolve/human_review/revocation.py
tools/agentx_evolve/human_review/identity.py
tools/agentx_evolve/human_review/review_api.py
```

Each file must have a clear responsibility, stable public API, inputs, outputs, invariants, tests, and safety limits.

## 3.3 Required Supporting Standard: SIB

SIB is required because this layer connects multiple Agent_X subsystems:

```text
Policy / Capability Registry
Tool / MCP Adapter
Governed Patch Execution Layer
Promotion / Release Gate
Failure Taxonomy / Recovery Playbook
Security Sandbox / Filesystem Boundary
Git Integration Layer
LLM Implementation Worker
Self-Evolution Orchestrator
Agent_X Initiator
```

This layer is a governance boundary, not a local UI helper.

## 3.4 Required Supporting Standard: Schema Contract

Schema Contract is required because all human review actions must be structured and auditable.

Required schemas include:

```text
human_review_request.schema.json
human_approval_decision.schema.json
human_rejection_decision.schema.json
human_deferral_decision.schema.json
human_clarification_request.schema.json
approval_scope.schema.json
approval_expiry.schema.json
approval_revocation.schema.json
human_reviewer_identity.schema.json
review_queue_item.schema.json
approval_evidence.schema.json
human_review_audit.schema.json
approval_consumption_lock.schema.json
approval_usage.schema.json
human_review_evidence_manifest.schema.json
approval_validation_result.schema.json
approval_state_transition.schema.json
approval_quorum.schema.json
approval_supersession.schema.json
reviewer_assignment.schema.json
human_review_deviation.schema.json
```

## 3.5 Required Evidence / Audit Rules

Every review request and decision must create evidence.

Evidence is required for:

```text
review request created
review request queued
review request viewed
approval decision recorded
rejection decision recorded
deferral decision recorded
clarification requested
approval used by a tool call
approval used by patch execution
approval used by promotion gate
approval expired
approval revoked
approval lookup failed
approval scope mismatch
reviewer identity mismatch
non-overridable safety block encountered
invalid review record rejected
```

---

# 4. Human Approval Authority Model

Human approval is a bounded authority, not a universal override.

## 4.1 What Human Approval May Authorize

A valid human approval may authorize:

```text
a specific tool call
a specific patch session
a specific patch application
a specific rollback session
a specific Git write operation, if Git Integration allows it
a specific promotion decision, if Promotion Gate allows it
a specific network/provider action, if Policy allows it
a specific model/provider mode, if Model Adapter policy allows it
a specific high-risk validation action, if command policy allows it
```

## 4.2 What Human Approval May Not Authorize

Human approval must not authorize:

```text
unknown tool execution
schema-invalid tool calls
policy-forbidden actions marked non-overridable
sandbox-denied path access
source writes outside approved boundaries
raw shell execution
network access when network mode is disabled by policy
Git write when Git Integration blocks it
MCP mutating exposure by default
secret logging
OpenCode runtime dependency
Bun/Node dependency introduction
unregistered model/provider use
unsafe patch application
promotion without promotion gate validation
```

## 4.3 Strictest-Authority-Wins Rule

A reviewed action may proceed only when all required authorities agree:

```text
Tool Registry
Policy / Capability Registry
Security Sandbox, when paths/files/commands are involved
Governed Patch Execution, when patches are involved
Git Integration, when Git writes are involved
Promotion Gate, when release/promotion is involved
Human Review / Approval Interface, when human approval is required
Failure Taxonomy, for failure classification
```

Decision precedence:

```text
INVALID
BLOCKED
REVOKED
EXPIRED
REJECTED
NEEDS_CLARIFICATION
NEEDS_APPROVAL
APPROVED_WITH_LIMITS
APPROVED
```

If authorities disagree, the strictest result wins.

---

# 5. Review Status Vocabulary

Use only these status values:

```text
PENDING_REVIEW
NEEDS_CLARIFICATION
DEFERRED
APPROVED
APPROVED_WITH_LIMITS
REJECTED
EXPIRED
REVOKED
USED
INVALID
BLOCKED
FAILED
```

Status meanings:

| Status | Meaning |
|---|---|
| `PENDING_REVIEW` | Review request exists but no decision has been made. |
| `NEEDS_CLARIFICATION` | Reviewer requires more information before deciding. |
| `DEFERRED` | Reviewer intentionally postpones decision. |
| `APPROVED` | Reviewer approves the exact requested action and scope. |
| `APPROVED_WITH_LIMITS` | Reviewer approves only a reduced or modified scope. |
| `REJECTED` | Reviewer rejects the request. |
| `EXPIRED` | Approval or request expired before valid use. |
| `REVOKED` | Approval was withdrawn before use or future use. |
| `USED` | Approval was consumed or referenced by a downstream action. |
| `INVALID` | Review record is malformed or schema-invalid. |
| `BLOCKED` | Review cannot proceed because a non-overridable rule blocks it. |
| `FAILED` | Internal review operation failed. |

---

# 6. Review State Machine and Transition Rules

Human review status transitions must be deterministic. A review record must not move between statuses arbitrarily.

Allowed request transitions:

```text
PENDING_REVIEW -> NEEDS_CLARIFICATION
PENDING_REVIEW -> DEFERRED
PENDING_REVIEW -> APPROVED
PENDING_REVIEW -> APPROVED_WITH_LIMITS
PENDING_REVIEW -> REJECTED
PENDING_REVIEW -> EXPIRED
PENDING_REVIEW -> BLOCKED
PENDING_REVIEW -> INVALID
NEEDS_CLARIFICATION -> PENDING_REVIEW, only after clarification evidence is attached
NEEDS_CLARIFICATION -> REJECTED
NEEDS_CLARIFICATION -> EXPIRED
DEFERRED -> PENDING_REVIEW, only after deferred_until or explicit reopen
DEFERRED -> REJECTED
DEFERRED -> EXPIRED
APPROVED -> USED
APPROVED -> EXPIRED
APPROVED -> REVOKED
APPROVED_WITH_LIMITS -> USED
APPROVED_WITH_LIMITS -> EXPIRED
APPROVED_WITH_LIMITS -> REVOKED
```

Terminal statuses:

```text
REJECTED
EXPIRED
REVOKED
USED
INVALID
BLOCKED
FAILED, unless retry policy explicitly allows recovery
```

Forbidden transitions:

```text
REJECTED -> APPROVED
EXPIRED -> APPROVED
REVOKED -> APPROVED
USED -> APPROVED
INVALID -> APPROVED
BLOCKED -> APPROVED
APPROVED -> APPROVED with broader scope
APPROVED_WITH_LIMITS -> APPROVED with broader scope
```

Rules:

```text
A rejected request may be resubmitted only as a new review_request_id.
A blocked request may not be approved unless the blocking condition is removed and a new request is created.
A used single-use approval cannot return to active state.
A scope-reducing clarification may create a revised request, but it must preserve provenance to the original request.
Every transition must write evidence.
```

---

# 7. Approval Consumption, Locking, and Idempotency

Approval validation and approval consumption must be race-safe. A single-use approval must not be consumed twice by concurrent tool, patch, Git, or promotion operations.

Required behavior:

```text
approval validation is separate from approval consumption
approval consumption must be atomic for single-use and max-use approvals
approval usage count must be recorded
approval usage must bind to action_id and action fingerprint
repeated validation with same idempotency_key may return same result
repeated consumption with same idempotency_key must not double-count
repeated consumption with different idempotency_key must fail when max_uses is reached
failed consumption must not increment usage count unless policy explicitly records attempted-use evidence separately
```

Required lock record fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "approval_consumption_lock.schema.json",
  "lock_id": "string",
  "approval_id": "string",
  "action_id": "string",
  "idempotency_key": "string",
  "acquired_at": "string",
  "released_at": "string|null",
  "status": "ACQUIRED|RELEASED|FAILED|STALE",
  "warnings": [],
  "errors": []
}
```

Required idempotency fields for approval use:

```text
approval_id
action_id
action_fingerprint
idempotency_key
usage_index
max_uses
consumed_at
consumption_status
```

No implementation may rely on in-memory-only usage counters for approval enforcement. Persistent evidence must be sufficient to reconstruct whether an approval has already been used.

---

# 8. Reviewer Independence, Conflict-of-Interest, and Quorum Rules

Human approval authority depends on reviewer identity, authorization level, independence, and risk level.

## 8.1 Conflict-of-Interest Rules

The default rule is:

```text
The requester should not approve their own request for HIGH or CRITICAL actions.
The implementer should not be the sole approver of their own generated patch.
The promotion requester should not be the sole approver of promotion.
Machine roles cannot approve.
MCP clients cannot approve by default.
```

Allowed exception:

```text
A sole human operator may approve LOW or MEDIUM local-only actions if policy allows it and the action is fully scoped, evidenced, and non-mutating or safely governed.
```

## 8.2 Quorum Rules

Default quorum model:

| Risk level | Minimum approval requirement |
|---|---|
| `LOW` | One authorized reviewer or policy-defined auto-rejection/auto-deferral. |
| `MEDIUM` | One authorized reviewer. |
| `HIGH` | One authorized reviewer independent from requester, unless policy permits otherwise. |
| `CRITICAL` | Two independent approvals or one OWNER plus one SECURITY_REVIEWER / RELEASE_MANAGER where applicable. |

Critical approvals that may require quorum:

```text
source mutation affecting safety-critical files
patch application to protected layers
rollback of committed work
Git write operations
promotion / release decisions
external provider/network enablement
model/provider mode changes
policy exception requests
```

## 8.3 Quorum Evidence

When quorum applies, evidence must include:

```text
quorum_required = true
required_approval_count
actual_approval_count
reviewer_ids
reviewer_roles
independence_check_result
policy_decision_id
final_quorum_status
```

A quorum failure must return:

```text
status = BLOCKED
failure_class = HUMAN_APPROVAL_QUORUM_NOT_MET
```

# 9. Human Review Request Schema

Every human review request must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "human_review_request.schema.json",
  "review_request_id": "string",
  "created_at": "string",
  "source_component": "string",
  "requested_by_role": "string",
  "requested_by_id": "string|null",
  "request_type": "TOOL_CALL|PATCH_APPLY|ROLLBACK|GIT_WRITE|PROMOTION|NETWORK_USE|MODEL_USE|POLICY_EXCEPTION|OTHER",
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "request_expires_at": "string|null",
  "requester_identity": {},
  "title": "string",
  "summary": "string",
  "requested_action": {},
  "requested_scope": {},
  "required_authorities": [],
  "related_tool_call_id": "string|null",
  "related_patch_session_id": "string|null",
  "related_policy_decision_id": "string|null",
  "related_sandbox_decision_id": "string|null",
  "related_git_operation_id": "string|null",
  "related_promotion_id": "string|null",
  "action_fingerprint": {},
  "registry_fingerprint": "string|null",
  "policy_fingerprint": "string|null",
  "sandbox_fingerprint": "string|null",
  "patch_fingerprint": "string|null",
  "commit_fingerprint": "string|null",
  "schema_fingerprint": "string|null",
  "evidence_refs": [],
  "artifact_refs": [],
  "status": "PENDING_REVIEW",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
review_request_id is required.
request_type is required.
risk_level is required.
requested_action must be an object.
requested_scope must be an object.
evidence_refs must be preserved.
critical requests must include enough evidence for review.
requests with missing non-overridable authority evidence must be BLOCKED, not approved.
expired review requests must not be approved.
stale requests must be resubmitted if action fingerprints changed.
requester_identity must be present for HIGH and CRITICAL requests.
```

---

# 10. Human Approval Decision Schema

Every approval decision must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "human_approval_decision.schema.json",
  "approval_id": "string",
  "review_request_id": "string",
  "decided_at": "string",
  "reviewer_identity": {},
  "decision": "APPROVED|APPROVED_WITH_LIMITS",
  "approval_scope": {},
  "expires_at": "string|null",
  "single_use": true,
  "max_uses": 1,
  "usage_count": 0,
  "approval_reason": "string",
  "quorum_required": false,
  "quorum_group_id": "string|null",
  "approver_independence_checked": true,
  "approved_action_fingerprint": {},
  "conditions": [],
  "non_overridable_rules_acknowledged": [],
  "evidence_refs": [],
  "artifact_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
approval_id is required.
review_request_id is required.
reviewer_identity is required.
approval_scope is required.
critical approvals must be single-use unless a stricter policy allows otherwise.
APPROVED_WITH_LIMITS must record the reduced scope.
approval does not imply policy override.
approval does not imply sandbox override.
approval does not imply promotion success.
approval does not authorize a changed patch, changed command, changed commit, changed path set, or changed policy context.
approval must be consumed atomically when single_use or max_uses applies.
critical approvals must satisfy quorum when policy requires it.
```

---

# 11. Human Rejection Decision Schema

Every rejection decision must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "human_rejection_decision.schema.json",
  "rejection_id": "string",
  "review_request_id": "string",
  "decided_at": "string",
  "reviewer_identity": {},
  "decision": "REJECTED",
  "rejection_reason": "string",
  "blocked_categories": [],
  "required_changes_before_resubmission": [],
  "evidence_refs": [],
  "artifact_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
rejection_id is required.
review_request_id is required.
rejection_reason is required.
rejected requests must not be executed.
resubmission must create a new review_request_id.
```

---

# 12. Human Deferral / Clarification Schema

## 9.1 Deferral Decision

```json
{
  "schema_version": "1.0",
  "schema_id": "human_deferral_decision.schema.json",
  "deferral_id": "string",
  "review_request_id": "string",
  "decided_at": "string",
  "reviewer_identity": {},
  "decision": "DEFERRED",
  "deferred_until": "string|null",
  "deferral_reason": "string",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

## 9.2 Clarification Request

```json
{
  "schema_version": "1.0",
  "schema_id": "human_clarification_request.schema.json",
  "clarification_id": "string",
  "review_request_id": "string",
  "created_at": "string",
  "reviewer_identity": {},
  "decision": "NEEDS_CLARIFICATION",
  "questions": [],
  "required_evidence": [],
  "response_due_at": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
deferred requests must not execute.
clarification requests must not execute.
clarification responses must attach evidence.
clarification does not extend approval unless expiry policy allows it.
```

---

# 13. Approval Scope Schema

Every approval must be scoped.

```json
{
  "schema_version": "1.0",
  "schema_id": "approval_scope.schema.json",
  "scope_id": "string",
  "scope_type": "TOOL_CALL|PATCH_SESSION|FILE_SET|COMMAND|GIT_OPERATION|PROMOTION|MODEL_PROVIDER|NETWORK_PROVIDER|SESSION|COMMIT|OTHER",
  "allowed_tool_names": [],
  "allowed_effects": [],
  "allowed_paths": [],
  "allowed_commands": [],
  "allowed_patch_session_ids": [],
  "allowed_git_operations": [],
  "allowed_model_profiles": [],
  "allowed_network_targets": [],
  "allowed_commit_hashes": [],
  "allowed_session_ids": [],
  "denied_paths": [],
  "denied_commands": [],
  "max_risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "single_use": true,
  "max_uses": 1,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
scope_id is required.
scope_type is required.
approvals must not be global by default.
approvals must not apply to unknown tools.
approvals must not apply to future unrelated sessions unless explicitly allowed by policy.
path scope must not exceed sandbox-allowed boundaries.
command scope must not exceed command allowlist.
```

---

# 14. Approval Expiry / Revocation Schema

## 11.1 Expiry Schema

```json
{
  "schema_version": "1.0",
  "schema_id": "approval_expiry.schema.json",
  "approval_id": "string",
  "expires_at": "string|null",
  "expired_at": "string|null",
  "expiry_reason": "TIME_LIMIT|SESSION_END|COMMIT_CHANGED|SCOPE_CHANGED|POLICY_CHANGED|MANUAL_EXPIRY|OTHER",
  "status": "ACTIVE|EXPIRED",
  "warnings": [],
  "errors": []
}
```

## 11.2 Revocation Schema

```json
{
  "schema_version": "1.0",
  "schema_id": "approval_revocation.schema.json",
  "revocation_id": "string",
  "approval_id": "string",
  "revoked_at": "string",
  "revoked_by": {},
  "revocation_reason": "string",
  "effective_immediately": true,
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
expired approval must not authorize action.
revoked approval must not authorize action.
commit change may expire patch-related approval.
scope change must expire or invalidate approval.
policy change may invalidate approval.
revocation must be evidenced.
```

---

# 15. Human Reviewer Identity Schema

Every decision must identify the reviewer.

```json
{
  "schema_version": "1.0",
  "schema_id": "human_reviewer_identity.schema.json",
  "reviewer_id": "string",
  "reviewer_role": "HUMAN_OPERATOR|MAINTAINER|OWNER|RELEASE_MANAGER|SECURITY_REVIEWER|OTHER",
  "display_name": "string|null",
  "identity_source": "LOCAL_CONFIG|SIGNED_RECORD|GIT_IDENTITY|EXTERNAL_IDP|MANUAL_ENTRY",
  "authenticated": false,
  "authentication_method": "NONE|LOCAL|SIGNED|EXTERNAL|OTHER",
  "authorization_level": "REVIEW_ONLY|APPROVE_LOW|APPROVE_MEDIUM|APPROVE_HIGH|APPROVE_CRITICAL",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
reviewer_id is required.
reviewer_role is required.
authorization_level must be checked against request risk level.
unauthenticated reviewer identity cannot approve critical actions.
reviewer identity must be included in approval, rejection, deferral, and revocation records.
```

---

# 16. Review Queue Schema

The review queue must be deterministic and auditable.

```json
{
  "schema_version": "1.0",
  "schema_id": "review_queue_item.schema.json",
  "queue_item_id": "string",
  "review_request_id": "string",
  "created_at": "string",
  "updated_at": "string",
  "priority": "LOW|NORMAL|HIGH|URGENT",
  "status": "PENDING_REVIEW|NEEDS_CLARIFICATION|DEFERRED|APPROVED|APPROVED_WITH_LIMITS|REJECTED|EXPIRED|REVOKED|INVALID|BLOCKED",
  "assigned_reviewer_id": "string|null",
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "request_type": "string",
  "evidence_refs": [],
  "artifact_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
queue order must be deterministic.
queue updates must be evidenced.
queue item status must match latest decision state.
queue item deletion is not allowed for audit history.
closed items remain queryable.
```

---

# 17. Approval Evidence Schema

Every human review event must produce evidence.

```json
{
  "schema_version": "1.0",
  "schema_id": "approval_evidence.schema.json",
  "evidence_id": "string",
  "created_at": "string",
  "source_component": "HumanReviewApproval",
  "event_type": "REQUEST_CREATED|QUEUE_UPDATED|APPROVED|APPROVED_WITH_LIMITS|REJECTED|DEFERRED|CLARIFICATION_REQUESTED|EXPIRED|REVOKED|USED|INVALID|BLOCKED|FAILED",
  "review_request_id": "string|null",
  "approval_id": "string|null",
  "decision_id": "string|null",
  "reviewer_id": "string|null",
  "related_action_id": "string|null",
  "status": "string",
  "message": "string",
  "artifact_refs": [],
  "evidence_refs": [],
  "sha256_refs": [],
  "warnings": [],
  "errors": []
}
```

Required evidence artifacts:

```text
.agentx-init/human_review/review_request_history.jsonl
.agentx-init/human_review/approval_decision_history.jsonl
.agentx-init/human_review/rejection_decision_history.jsonl
.agentx-init/human_review/deferral_decision_history.jsonl
.agentx-init/human_review/clarification_history.jsonl
.agentx-init/human_review/revocation_history.jsonl
.agentx-init/human_review/review_queue_history.jsonl
.agentx-init/human_review/approval_usage_history.jsonl
.agentx-init/human_review/latest_review_request.json
.agentx-init/human_review/latest_decision.json
.agentx-init/human_review/latest_queue_snapshot.json
```

Rules:

```text
JSONL histories are append-only.
latest artifacts are written atomically.
SHA-256 hashes are required for final review evidence.
secret-like fields must be redacted before durable logging.
raw patch content should be summarized unless the owning patch layer already approved evidence storage.
```

---

# 18. Evidence Hashing, Provenance, and Immutability

Human review evidence must be tamper-evident.

## 15.1 Required Hashing

All final evidence artifacts used for implementation validation must have SHA-256 hashes.

Required hashed artifacts include:

```text
review_request_history.jsonl
approval_decision_history.jsonl
rejection_decision_history.jsonl
deferral_decision_history.jsonl
clarification_history.jsonl
revocation_history.jsonl
review_queue_history.jsonl
approval_usage_history.jsonl
latest_review_request.json
latest_decision.json
latest_queue_snapshot.json
human_review_evidence_manifest.json
human_review_evidence_manifest.json
approval_consumption_lock_history.jsonl
human_review_completion_record.json
```

Hashing rule:

```text
Use SHA-256.
Use Python standard library hashlib if no project helper exists.
A final DONE verdict is invalid if final evidence hashes are missing.
```

## 15.2 Evidence Provenance

Every evidence event should record:

```text
created_at
source_component
event_type
review_request_id, if applicable
approval_id, if applicable
reviewer_id, if applicable
related action identifier
related policy decision ID
related sandbox decision ID
related patch session ID
related commit hash
related registry hash
input artifact refs
output artifact refs
sha256 refs
```

## 15.3 Evidence Immutability

After a decision is recorded:

```text
append-only histories must not be rewritten
latest artifacts may be updated only by writing a new event
manual edits to evidence invalidate the affected approval unless recorded as a deviation and revalidated
changed evidence hashes invalidate prior completion claims
approval evidence must remain queryable after rejection, expiry, revocation, or use
```

## 15.4 Evidence Manifest

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
  "created_at": "string",
  "validated_commit": "string|null",
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "deviation_register": [],
  "redaction_status": "PASS|FAIL|NOT_CHECKED",
  "hash_status": "PASS|FAIL|NOT_CHECKED",
  "final_decision": "DONE|NOT_DONE|IMPLEMENTED_UNVALIDATED|BLOCKED"
}
```

# 19. Role Permission Matrix

Initial roles:

```text
ORCHESTRATOR
IMPLEMENTATION_WORKER
VALIDATION_REPAIR_WORKER
REVIEWER_ASSISTANT
PROMOTION_CHECKER
HUMAN_OPERATOR
MAINTAINER
OWNER
SECURITY_REVIEWER
RELEASE_MANAGER
MCP_CLIENT
UNKNOWN_CALLER
```

| Role | May request review | May view queue | May approve | May reject | May revoke | Notes |
|---|---|---|---|---|---|
| `ORCHESTRATOR` | Yes | Yes | No | No | No | May coordinate, not approve. |
| `IMPLEMENTATION_WORKER` | Yes | Limited | No | No | No | May request approval for generated changes. |
| `VALIDATION_REPAIR_WORKER` | Yes | Limited | No | No | No | May request approval for repair actions. |
| `REVIEWER_ASSISTANT` | Yes | Yes | No | No | No | May summarize evidence only. |
| `PROMOTION_CHECKER` | Yes | Yes | No | No | No | May require release approval. |
| `HUMAN_OPERATOR` | Yes | Yes | Conditional | Yes | Conditional | Must match authorization level. |
| `MAINTAINER` | Yes | Yes | Conditional | Yes | Conditional | Project-specific authority. |
| `OWNER` | Yes | Yes | Conditional | Yes | Yes | Cannot override non-overridable safety. |
| `SECURITY_REVIEWER` | Yes | Yes | Security-scoped | Yes | Security-scoped | May reject unsafe requests. |
| `RELEASE_MANAGER` | Yes | Yes | Promotion-scoped | Yes | Promotion-scoped | Release/promotion scope only. |
| `MCP_CLIENT` | Limited | No by default | No | No | No | Must not approve through MCP by default. |
| `UNKNOWN_CALLER` | No | No | No | No | No | Always blocked. |

Rules:

```text
machine roles cannot approve.
MCP clients cannot approve by default.
reviewer authorization level must match risk level.
approval authority is scoped, not global.
human approval cannot override non-overridable safety rules.
```

---

# 20. Approval Boundary Rules

Approval must be bounded by:

```text
request_id
approval_id
reviewer_id
request_type
risk_level
scope_id
session_id
patch_session_id, when applicable
tool_call_id, when applicable
commit hash, when applicable
path set, when applicable
command set, when applicable
model/provider profile, when applicable
network target, when applicable
expiry time
single-use or max-use count
```

Boundary rules:

```text
approval for one request must not authorize another request.
approval for one patch session must not authorize another patch session.
approval for one file path must not authorize unrelated paths.
approval for one command must not authorize arbitrary commands.
approval for one commit must expire if commit changes, unless policy explicitly allows continuation.
approval with reduced scope must block out-of-scope execution.
approval must be revalidated immediately before use.
```

---

# 21. Request Expiry, Supersession, and Resubmission Rules

Review request expiry is separate from approval expiry. A request may expire before any decision is made.

Request expiry triggers:

```text
request_expires_at reached
action fingerprint changed
patch hash changed
commit hash changed
policy version changed
sandbox boundary decision changed
registry version changed
schema version changed
requester explicitly cancels request
reviewer marks request superseded
```

Supersession rules:

```text
A superseded request must not be approved.
A corrected request must receive a new review_request_id.
A resubmitted request must reference supersedes_review_request_id.
Evidence from the prior request may be referenced but must not be silently rewritten.
Rejection does not prevent resubmission, but resubmission requires new evidence and new review.
```

Required supersession schema fields where applicable:

```text
supersedes_review_request_id
superseded_by_review_request_id
supersession_reason
superseded_at
```

---

# 22. Approval Binding Fingerprint Rules

Every approval must bind to the exact action being approved.

Required fingerprints where applicable:

```text
action_fingerprint
tool_call_fingerprint
registry_hash
policy_decision_hash
sandbox_decision_hash
patch_hash
patch_session_hash
commit_hash
command_hash
path_set_hash
model_profile_hash
network_target_hash
promotion_candidate_hash
schema_version_hash
evidence_manifest_hash
```

Binding rules:

```text
If a fingerprint changes, the approval must be treated as stale.
Stale approval must return BLOCKED, not APPROVED.
Patch approval must bind to patch hash and patch session ID.
Promotion approval must bind to commit hash and promotion candidate ID.
Command approval must bind to exact allowlisted command shape, not free-form shell text.
Path approval must bind to canonical normalized path set.
Model/provider approval must bind to model profile and provider mode.
Network approval must bind to exact target class or endpoint scope allowed by policy.
```

# 23. Non-Overridable Safety Rules

The following cannot be overridden by human approval:

```text
schema-invalid request
unknown caller
unknown tool
unregistered tool
blocked trust tier
policy non-overridable denial
sandbox path denial
source boundary violation
raw shell execution
command injection risk
network disabled by policy
Git write disabled by Git Integration
MCP mutating exposure by default
secret logging
missing required evidence
expired approval
revoked approval
approval scope mismatch
unauthorized reviewer identity
patch integrity failure
promotion gate validation failure
OpenCode source-code copying
Bun/Node/OpenCode runtime dependency introduction without major architecture approval
```

If a non-overridable rule is encountered, the result must be:

```text
status = BLOCKED
failure_class = HUMAN_APPROVAL_CANNOT_OVERRIDE_SAFETY
```

---


# 24. Canonicalization, Time, and Fingerprint Rules

Approval decisions must bind to canonicalized action data. The same logical action must produce the same fingerprint, and materially changed action data must produce a different fingerprint.

## 24.1 Canonicalization Rules

Required canonicalization behavior:

```text
paths must be normalized relative to the approved repository root
path traversal segments must be resolved before hashing
symlinks must be handled according to Security Sandbox rules
command arguments must be tokenized, not shell-string normalized
command fingerprints must preserve argument order
Git operation fingerprints must include operation type and target commit/branch where applicable
patch fingerprints must include patch session ID and patch content hash
promotion fingerprints must include promotion candidate ID and commit hash
model/provider fingerprints must include provider mode, model profile ID, and policy version
network fingerprints must include target class and policy-approved endpoint scope
schema fingerprints must include schema IDs and versions used for validation
```

Forbidden canonicalization behavior:

```text
no fingerprint based only on free-form summary text
no approval binding to non-normalized paths
no approval binding to raw shell strings
no approval binding to mutable labels such as "latest" without resolved commit/hash
no approval binding that ignores policy, sandbox, patch, or promotion evidence when those authorities apply
```

## 24.2 Trusted Time Rules

All review timestamps must use UTC ISO-8601 format.

Required ordering rules:

```text
created_at must be before decided_at
approval decided_at must be before consumed_at
revoked_at must be before any revocation enforcement event
expired_at must be recorded before or at failed approval validation
queue updated_at must never move backward for the same queue item
manual clock override is not allowed in production mode
```

Test mode may use a deterministic injected clock, but production code must not use test-only clock shortcuts.

## 24.3 Approval Validation Result Schema

Approval validation must return a schema-valid record, not an unstructured dictionary.

```json
{
  "schema_version": "1.0",
  "schema_id": "approval_validation_result.schema.json",
  "validation_id": "string",
  "validated_at": "string",
  "approval_id": "string|null",
  "review_request_id": "string|null",
  "action_id": "string",
  "action_fingerprint": {},
  "decision": "ALLOW|BLOCK|EXPIRED|REVOKED|SCOPE_MISMATCH|QUORUM_NOT_MET|REVIEWER_UNAUTHORIZED|STALE|INVALID",
  "status": "PASS|FAIL",
  "failure_class": "string|null",
  "checks_performed": [],
  "failed_checks": [],
  "policy_decision_id": "string|null",
  "sandbox_decision_id": "string|null",
  "patch_session_id": "string|null",
  "promotion_candidate_id": "string|null",
  "evidence_refs": [],
  "artifact_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
ALLOW is valid only if all required checks pass.
Any missing required authority record must return BLOCK or INVALID.
Any stale fingerprint must return STALE or BLOCK.
Any expired or revoked approval must return EXPIRED or REVOKED.
Validation results must be evidenced before downstream action execution.
```

# 25. Reviewer Assignment, Queue Ownership, and Availability Rules

The review queue must distinguish queue state from reviewer assignment.

## 25.1 Reviewer Assignment Schema

```json
{
  "schema_version": "1.0",
  "schema_id": "reviewer_assignment.schema.json",
  "assignment_id": "string",
  "review_request_id": "string",
  "assigned_at": "string",
  "assigned_by": "string|null",
  "assigned_reviewer_id": "string",
  "assignment_reason": "string",
  "status": "ASSIGNED|REASSIGNED|UNASSIGNED|DECLINED|STALE",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
assignment does not imply approval authority
assignment does not bypass conflict-of-interest checks
reassignment must preserve prior assignment evidence
unavailable reviewer status must not silently approve, reject, or expire a request
queue item may remain unassigned, but execution must remain blocked until approval exists
```

## 25.2 State Transition Evidence Schema

Every status transition must be evidenced.

```json
{
  "schema_version": "1.0",
  "schema_id": "approval_state_transition.schema.json",
  "transition_id": "string",
  "review_request_id": "string",
  "approval_id": "string|null",
  "transitioned_at": "string",
  "from_status": "string",
  "to_status": "string",
  "transition_reason": "string",
  "actor_id": "string|null",
  "valid_transition": true,
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Forbidden transition attempts must be recorded as blocked evidence.

# 26. Quorum, Supersession, and Deviation Schemas

## 26.1 Approval Quorum Schema

```json
{
  "schema_version": "1.0",
  "schema_id": "approval_quorum.schema.json",
  "quorum_id": "string",
  "review_request_id": "string",
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "quorum_required": true,
  "required_approval_count": 1,
  "actual_approval_count": 0,
  "required_reviewer_roles": [],
  "actual_reviewer_roles": [],
  "reviewer_ids": [],
  "independence_check_result": "PASS|FAIL|NOT_REQUIRED",
  "quorum_status": "MET|NOT_MET|BLOCKED",
  "policy_decision_id": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
critical quorum cannot be inferred from count alone; reviewer role and independence must be checked
quorum failure blocks approval validation
quorum evidence must be linked to approval validation result
```

## 26.2 Supersession Schema

```json
{
  "schema_version": "1.0",
  "schema_id": "approval_supersession.schema.json",
  "supersession_id": "string",
  "superseded_review_request_id": "string",
  "superseded_by_review_request_id": "string|null",
  "superseded_at": "string",
  "supersession_reason": "ACTION_CHANGED|PATCH_CHANGED|COMMIT_CHANGED|POLICY_CHANGED|SCHEMA_CHANGED|REQUESTER_CANCELLED|REVIEWER_MARKED_SUPERSEDED|OTHER",
  "source_component": "HumanReviewApproval",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
superseded requests cannot be approved
superseded approvals cannot authorize action
supersession must preserve old evidence and create new evidence
corrected requests must receive new review_request_id
```

## 26.3 Deviation Register Schema

```json
{
  "schema_version": "1.0",
  "schema_id": "human_review_deviation.schema.json",
  "deviation_id": "string",
  "created_at": "string",
  "area": "IDENTITY|QUORUM|EVIDENCE|SCOPE|EXPIRY|REVOCATION|QUEUE|CLI|MCP|OTHER",
  "description": "string",
  "reason": "string",
  "safety_impact": "NONE|LOW|MEDIUM|HIGH|CRITICAL",
  "compensating_control": "string",
  "accepted_status": "NON_BLOCKING|DEFERRED_SAFELY|REJECTED",
  "reviewer_decision": "ACCEPTED|REJECTED",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
BLOCKER issues cannot be accepted as deviations
missing evidence hashes cannot be accepted for DONE
non-overridable safety bypass cannot be accepted as a deviation
MCP approval by default cannot be accepted as a deviation
machine-role approval cannot be accepted as a deviation
```

# 27. Break-Glass and Emergency Approval Policy

Break-glass approval is blocked by default in this layer.

Rules:

```text
no emergency approval path exists in v1
no role may bypass schema, policy, sandbox, evidence, expiry, revocation, scope, or quorum by claiming emergency authority
any future break-glass mode requires a major contract revision
future break-glass must require stronger identity, quorum, evidence, expiry, and post-action review controls
```

Required result for attempted break-glass in v1:

```text
status = BLOCKED
failure_class = HUMAN_APPROVAL_BREAK_GLASS_NOT_IMPLEMENTED
```

# 28. Privacy, Minimization, and Review Comment Rules

Human review evidence must preserve auditability without over-collecting human data.

Rules:

```text
reviewer identity must record the minimum fields needed for authorization and audit
free-form review comments must not contain secrets, credentials, private keys, or raw prompt dumps
review comments should be summarized or redacted before durable evidence when they include sensitive operational details
reviewer display_name may be null if reviewer_id and authority are sufficient
external identity provider tokens must never be logged
identity_source may be recorded, but authentication secrets must not be stored
```

Redaction applies before writing any JSONL or latest artifact.

# 29. Public API Contract

Expected classes:

```text
HumanReviewRequest
HumanApprovalDecision
HumanRejectionDecision
HumanDeferralDecision
HumanClarificationRequest
ApprovalScope
ApprovalExpiry
ApprovalRevocation
HumanReviewerIdentity
ReviewQueueItem
ApprovalEvidence
HumanReviewAuditEvent
```

Expected public functions:

```python
create_review_request(arguments: dict, context: dict) -> HumanReviewRequest
enqueue_review_request(request: HumanReviewRequest, repo_root: Path) -> ReviewQueueItem
record_approval_decision(request_id: str, decision: dict, repo_root: Path) -> HumanApprovalDecision
record_rejection_decision(request_id: str, decision: dict, repo_root: Path) -> HumanRejectionDecision
record_deferral_decision(request_id: str, decision: dict, repo_root: Path) -> HumanDeferralDecision
record_clarification_request(request_id: str, clarification: dict, repo_root: Path) -> HumanClarificationRequest
validate_approval_for_action(approval_id: str, action_context: dict, repo_root: Path) -> ApprovalValidationResult
expire_approval(approval_id: str, reason: str, repo_root: Path) -> dict
revoke_approval(approval_id: str, revocation: dict, repo_root: Path) -> dict
write_human_review_evidence(event: dict, repo_root: Path) -> dict
load_review_queue(repo_root: Path) -> list[ReviewQueueItem]
```

Import rules:

```text
No function may execute patch application directly.
No function may execute Git write directly.
No function may call network by default.
No function may send email or external notification by default.
No function may block waiting for interactive input.
```

---

# 30. Approval Validation Pipeline

Every approval use must follow this sequence:

```text
1. Receive downstream action requiring approval.
2. Load approval decision by approval_id.
3. Validate approval schema.
4. Validate reviewer identity and authorization level.
5. Validate approval status is active.
6. Validate approval is not expired.
7. Validate approval is not revoked.
8. Validate single-use or max-use count.
9. Validate action type matches approval scope.
10. Validate tool/session/patch/path/command/model/network scope.
11. Re-check Policy / Capability Registry.
12. Re-check Security Sandbox if paths/files/commands are involved.
13. Re-check owning layer state, such as patch or promotion gate.
14. Apply strictest-authority-wins rule.
15. Record approval usage evidence.
16. Return ALLOW only if all checks pass.
```

No downstream action may rely only on the presence of an `approval_id`.

---

# 31. OpenCode Borrowing Notes

## 20.1 Concepts to Borrow

Borrow these OpenCode-style ideas only as bounded patterns:

```text
question/human-interaction tool concept
plan approval checkpoint concept
tool-specific permission boundary
human-in-the-loop decision point
structured tool result pattern
approval before risky action pattern
```

## 20.2 Concepts to Restrict

Do not copy or import these assumptions:

```text
model-driven human approval without policy binding
free-form approval text as authorization
approval that bypasses tool registry
approval that bypasses sandbox
approval that bypasses command allowlist
approval that automatically executes after response
human prompt as hidden side channel
broad shell or plugin behavior
OpenCode runtime dependency
Bun/Node dependency
```

## 20.3 Agent_X Mapping

| OpenCode-style concept | Agent_X equivalent | Required control |
|---|---|---|
| `question` | `create_review_request` / `ask_human` | structured review request, no blocking UI by default |
| plan confirmation | approval request for plan or patch session | scoped approval and expiry |
| risky tool confirmation | approval decision | policy + sandbox still required |
| tool output explanation | review evidence summary | redacted, hashed, auditable evidence |
| plugin approval | future extension approval | disabled unless policy authorizes |

---

# 32. Agent_X Integration Notes

## 21.1 Policy / Capability Registry Integration

The Policy / Capability Registry decides when human approval is required.

Required behavior:

```text
policy decision may return NEEDS_APPROVAL.
human approval may satisfy NEEDS_APPROVAL only for the exact scope.
policy non-overridable BLOCK cannot be overridden.
approval evidence must reference the policy decision ID where available.
```

## 21.2 Tool / MCP Adapter Integration

Tool / MCP Adapter may create review requests through the `ask_human` tool or equivalent human-review API.

Required behavior:

```text
ToolResult may include approval_required metadata.
ToolResult may reference review_request_id.
Tool execution must pause/block until approval exists.
MCP clients cannot approve through MCP by default.
MCP mutating tools remain hidden or blocked by default.
```

## 21.3 Governed Patch Execution Integration

Patch application may require human approval.

Required behavior:

```text
approval must bind to patch_session_id.
approval must bind to patch hash or patch evidence.
approval expires if patch content changes.
approval does not execute patch by itself.
patch layer must revalidate approval immediately before application.
```

## 21.4 Promotion / Release Gate Integration

Promotion may require human approval.

Required behavior:

```text
approval must bind to promotion candidate.
approval must bind to commit hash.
approval expires if commit hash changes.
approval does not bypass validation failures.
approval does not promote by itself.
```

## 21.5 Security Sandbox Integration

Human approval cannot expand filesystem authority beyond sandbox rules.

Required behavior:

```text
sandbox-denied path remains denied.
source boundary violations remain blocked.
path scope in approval must be no broader than sandbox-allowed scope.
```

## 21.6 Failure Taxonomy Integration

Human review failures must map to standard failure classes.

Required failure classes:

```text
HUMAN_REVIEW_REQUIRED
HUMAN_APPROVAL_MISSING
HUMAN_APPROVAL_REJECTED
HUMAN_APPROVAL_EXPIRED
HUMAN_APPROVAL_REVOKED
HUMAN_APPROVAL_SCOPE_MISMATCH
HUMAN_REVIEWER_UNAUTHORIZED
HUMAN_APPROVAL_CANNOT_OVERRIDE_SAFETY
HUMAN_REVIEW_SCHEMA_INVALID
HUMAN_REVIEW_EVIDENCE_MISSING
UNKNOWN_HUMAN_REVIEW_FAILURE
```

---

# 33. Runtime Artifact Rules

All human-review state must be under:

```text
.agentx-init/human_review/
```

Required artifacts:

```text
review_request_history.jsonl
approval_decision_history.jsonl
rejection_decision_history.jsonl
deferral_decision_history.jsonl
clarification_history.jsonl
revocation_history.jsonl
review_queue_history.jsonl
approval_usage_history.jsonl
latest_review_request.json
latest_decision.json
latest_queue_snapshot.json
human_review_evidence_manifest.json
approval_consumption_lock_history.jsonl
human_review_completion_record.json
approval_validation_result_history.jsonl
approval_state_transition_history.jsonl
approval_quorum_history.jsonl
approval_supersession_history.jsonl
reviewer_assignment_history.jsonl
human_review_deviation_register.jsonl
```

Rules:

```text
JSONL histories are append-only.
latest artifacts are atomic writes.
review queue state must be reconstructable from history.
approval usage must be recorded.
expired and revoked approvals must remain auditable.
source files must not be modified by this layer.
```

---

# 34. Security Rules

This layer must enforce:

```text
no approval without schema-valid request
no approval without reviewer identity
no approval without approval scope
no approval without evidence
no global approval by default
no approval reuse beyond max_uses
no expired approval use
no revoked approval use
no machine-role approval
no MCP approval by default
no safety override for non-overridable blocks
no direct patch execution
no direct Git write
no direct promotion
no external notification by default
no raw shell
no network by default
no unredacted secret logging
```

---

# 35. Simulated Dependency and Test Double Contract

Tests may use simulated upstream components only when the simulation is explicitly fail-closed and records the simulated decision.

Allowed test doubles:

```text
fake Policy / Capability Registry returning ALLOW, BLOCK, NEEDS_APPROVAL, or non-overridable BLOCK
fake Security Sandbox returning ALLOW or DENY with path decision ID
fake Governed Patch Execution state returning patch hash and patch session status
fake Promotion Gate returning candidate hash and validation status
fake identity provider returning authenticated or unauthenticated reviewer identity
```

Rules:

```text
A fake dependency must never default to ALLOW.
Missing fake dependency must produce BLOCKED for safety-relevant checks.
Test doubles must expose decision IDs for evidence propagation.
Tests must include both positive and negative dependency outcomes.
Production code must not rely on test-only approval bypasses.
```

---

# 36. CLI and MCP Exposure Boundary

Human review operations may later be exposed through CLI or MCP, but the base layer must not depend on either.

## 25.1 CLI Boundary

If CLI commands are exposed, they must:

```text
create structured review requests
record structured decisions only from authorized human identities
validate schema before writing evidence
write append-only evidence
not execute the approved action
not open raw shell
not send network notifications by default
not approve CRITICAL actions without required quorum
```

## 25.2 MCP Boundary

If MCP exposure is added, default behavior must be:

```text
MCP may create review requests only if policy allows.
MCP may not approve by default.
MCP may not revoke by default.
MCP may not execute approved actions.
MCP may not bypass reviewer identity.
MCP may not bypass quorum.
MCP may not broaden approval scope.
```

MCP approval support, if ever added, requires a separate major revision and MCP Protocol Acceptance Criteria.

# 37. Test Acceptance Criteria

Required tests:

```text
test_create_review_request_validates_schema
test_review_request_rejects_missing_request_type
test_approval_decision_validates_schema
test_rejection_decision_validates_schema
test_deferral_decision_validates_schema
test_clarification_request_validates_schema
test_approval_scope_required
test_global_approval_rejected_by_default
test_expired_approval_blocks
test_revoked_approval_blocks
test_single_use_approval_cannot_be_reused
test_scope_mismatch_blocks
test_unauthorized_reviewer_blocks
test_machine_role_cannot_approve
test_mcp_client_cannot_approve_by_default
test_policy_non_overridable_block_cannot_be_approved
test_sandbox_denial_cannot_be_approved
test_patch_approval_expires_when_patch_hash_changes
test_promotion_approval_expires_when_commit_changes
test_review_queue_append_only
test_approval_evidence_written
test_approval_usage_evidence_written
test_secrets_redacted_before_human_review_logging
test_status_transition_rejects_invalid_transition
test_single_use_approval_consumption_is_atomic
test_idempotent_consumption_does_not_double_count
test_conflicted_reviewer_cannot_approve_high_risk_own_request
test_critical_request_requires_quorum_when_policy_requires_it
test_stale_patch_hash_invalidates_approval
test_stale_commit_hash_invalidates_promotion_approval
test_policy_version_change_invalidates_policy_bound_approval
test_evidence_hashes_are_recorded
test_manual_evidence_change_invalidates_completion_claim
test_superseded_request_cannot_be_approved
test_approval_validation_returns_schema_valid_result
test_path_canonicalization_blocks_path_escape
test_command_fingerprint_uses_tokenized_arguments
test_reviewer_assignment_does_not_grant_approval
test_break_glass_blocks_by_default
test_deviation_cannot_accept_non_overridable_bypass
test_utc_timestamps_are_ordered
test_review_comments_are_redacted
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema tests PASS
negative safety tests PASS
approval evidence written
review queue evidence written
approval validation pipeline enforced
no source mutation
invalid or unsafe approval fails closed
```

---

# 38. Implementation Slices

Build this layer in small slices.

## 25.1 Slice A — Models and Schemas

Implement:

```text
review_models.py
human_review_request.schema.json
human_approval_decision.schema.json
human_rejection_decision.schema.json
human_deferral_decision.schema.json
human_clarification_request.schema.json
approval_scope.schema.json
approval_expiry.schema.json
approval_revocation.schema.json
human_reviewer_identity.schema.json
review_queue_item.schema.json
approval_evidence.schema.json
human_review_audit.schema.json
approval_consumption_lock.schema.json
approval_usage.schema.json
human_review_evidence_manifest.schema.json
approval_validation_result.schema.json
approval_state_transition.schema.json
approval_quorum.schema.json
approval_supersession.schema.json
reviewer_assignment.schema.json
human_review_deviation.schema.json
```

Acceptance:

```text
schemas validate valid examples
schemas reject missing required fields
schema enums match model constants
dataclasses instantiate and serialize
```

## 25.2 Slice B — Review Queue

Implement:

```text
review_queue.py
```

Acceptance:

```text
request enqueues deterministically
queue history written
latest queue snapshot written atomically
closed items remain queryable
```

## 25.3 Slice C — Evidence Logger

Implement:

```text
review_evidence.py
```

Acceptance:

```text
review request evidence written
approval evidence written
rejection evidence written
deferral evidence written
clarification evidence written
revocation evidence written
approval usage evidence written
secrets redacted
```

## 25.4 Slice D — Approval Policy and Validation

Implement:

```text
review_policy.py
approval_validator.py
revocation.py
identity.py
```

Acceptance:

```text
reviewer authorization checked
approval scope checked
expiry checked
revocation checked
single-use and max-use checked
non-overridable safety blocks enforced
```

## 25.5 Slice E — Public API

Implement:

```text
review_api.py
```

Acceptance:

```text
review requests created through API
approval decisions recorded through API
rejection/deferral/clarification recorded through API
approval validation exposed through API
no direct risky execution occurs
```

---

# 39. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is selected
[ ] runtime artifact root is selected
[ ] review request schema is defined
[ ] approval decision schema is defined
[ ] rejection decision schema is defined
[ ] deferral and clarification schemas are defined
[ ] approval scope schema is defined
[ ] expiry and revocation schemas are defined
[ ] reviewer identity schema is defined
[ ] review queue schema is defined
[ ] approval evidence schema is defined
[ ] role permission matrix is defined
[ ] approval boundary rules are defined
[ ] non-overridable safety rules are defined
[ ] OpenCode borrowing is bounded
[ ] Agent_X integration points are defined
```

---

# 40. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] schema validation passes
[ ] review requests validate
[ ] approval decisions validate
[ ] rejection decisions validate
[ ] deferral and clarification records validate
[ ] expired approvals block
[ ] revoked approvals block
[ ] scope mismatch blocks
[ ] unauthorized reviewers block
[ ] non-overridable safety blocks remain blocked
[ ] evidence records are written
[ ] source mutation does not occur
[ ] completion record exists
approval validation result is schema-valid
action fingerprints are canonicalized before validation
reviewer assignment does not grant authority
break-glass attempts block by default
deviation register cannot accept non-overridable bypasses
```

---

# 41. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_HUMAN_REVIEW_APPROVAL"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  review_request_coverage: []
  approval_decision_coverage: []
  rejection_decision_coverage: []
  deferral_clarification_coverage: []
  expiry_revocation_coverage: []
  role_permission_coverage: []
  non_overridable_safety_coverage: []
  policy_integration_verified: []
  tool_adapter_integration_verified: []
  patch_integration_verified: []
  promotion_integration_verified: []
  opencode_patterns_borrowed: []
  opencode_patterns_rejected_or_restricted: []
  deviations_from_contract: []
  unresolved_risks: []
```

---

# 42. Residual Risks

```yaml
residual_risks:
  - id: "HRA-RISK-001"
    description: "Human approval could be treated as a universal override."
    severity: "critical"
    mitigation: "Non-overridable safety rules and strictest-authority-wins rule."
  - id: "HRA-RISK-002"
    description: "Approval scope could be too broad."
    severity: "high"
    mitigation: "Approval scope schema requires bounded tool/path/session/commit/action scope."
  - id: "HRA-RISK-003"
    description: "Expired or revoked approval could be reused."
    severity: "high"
    mitigation: "Approval validation pipeline checks expiry, revocation, and max-use before every use."
  - id: "HRA-RISK-004"
    description: "Machine role or MCP client could approve actions."
    severity: "critical"
    mitigation: "Role permission matrix blocks machine approval and MCP approval by default."
  - id: "HRA-RISK-005"
    description: "Approval evidence could be incomplete or mutable."
    severity: "high"
    mitigation: "Append-only JSONL evidence, atomic latest files, hashes, and completion evidence."
```

---

# 43. Definition of Done

This layer is done when it can act as Agent_X's controlled human review and approval boundary.

It must prove:

```text
review requests are schema-valid
approval decisions are schema-valid
rejection decisions are schema-valid
deferral and clarification decisions are schema-valid
approval scopes are enforced
expiry is enforced
revocation is enforced
reviewer identity is checked
reviewer authorization is checked
machine roles cannot approve
MCP clients cannot approve by default
non-overridable safety blocks cannot be overridden
approval usage is evidenced
approval consumption is atomic
idempotent approval consumption does not double-count
reviewer conflict-of-interest rules are enforced
critical quorum rules are enforced where policy requires them
changed action fingerprints invalidate approval
review queue is auditable
all histories are append-only
latest artifacts are written atomically
secrets are redacted
evidence hashes are recorded
evidence immutability is preserved
no direct patch execution occurs
no direct Git write occurs
no direct promotion occurs
no source mutation occurs
completion record exists
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_human_review_schemas.py
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

# 44. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
review request schema is missing
approval decision schema is missing
approval scope schema is missing
reviewer identity schema is missing
approval without scope is accepted
machine role approval is accepted
MCP approval is accepted by default
expired approval authorizes action
revoked approval authorizes action
approval scope mismatch authorizes action
single-use approval can be reused
approval consumption is not persistent or race-safe
conflicted reviewer can approve HIGH or CRITICAL own request without policy exception
critical quorum requirement is bypassed
stale action fingerprint authorizes action
superseded request can be approved
policy non-overridable block is overridden
sandbox denial is overridden
approval executes patch directly
approval executes Git write directly
approval performs promotion directly
review evidence is missing
approval usage evidence is missing
evidence hashes are missing for final DONE
manual evidence mutation does not invalidate approval or completion claim
secrets are logged
source mutation occurs directly in this layer
approval validation returns an unstructured result
path canonicalization can broaden scope
command fingerprint is based on raw shell text instead of tokenized arguments
reviewer assignment grants approval authority
break-glass approval is allowed in v1
non-overridable bypass is accepted as a deviation
review comments or identity evidence log secrets
```

---

# 45. Final Freeze Rule

This v3 document is the frozen controlling contract for the Human Review / Approval Interface.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional schema fields or test examples
MAJOR: changed approval authority model, changed role permission rules, changed non-overridable safety rules, changed approval scope semantics, changed quorum rules, changed identity/authentication model, changed evidence immutability semantics, changed approval consumption semantics, new external identity dependency, changed validation-result schema, changed canonicalization semantics, changed break-glass policy, changed deviation acceptance semantics
```

Blocked without major revision:

```text
allowing approval to override sandbox denial
allowing approval to override policy non-overridable block
allowing machine-role approval
allowing MCP approval by default
allowing global approval by default
allowing expired approval use
allowing revoked approval use
allowing single-use approval reuse
removing approval consumption locking
removing quorum for policy-required critical approvals
removing approval evidence
removing approval scope
removing reviewer identity
allowing direct patch execution
allowing direct Git write
allowing direct promotion
allowing break-glass approval in v1
allowing reviewer assignment to imply approval
allowing unstructured approval validation results
allowing non-overridable bypasses as deviations
```

The next document should be:

```text
HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_SPEC.md
```

---

# 46. Final Rating

This v3 controlling contract is rated:

```text
10/10
```

Reason:

```text
It defines the Human Review / Approval Interface with EQC, FIC, SIB, schema contracts, evidence/audit rules, human authority model, review request and decision schemas, rejection/deferral/clarification handling, approval scope, expiry, revocation, reviewer identity, review queue, role permissions, approval boundaries, non-overridable safety rules, approval state transitions, race-safe approval consumption, idempotency, reviewer independence, quorum rules, request supersession, canonical action fingerprint binding, schema-valid approval validation results, queue assignment boundaries, break-glass blocking, deviation-register controls, privacy/minimization rules, evidence hashing, evidence immutability, OpenCode borrowing limits, Agent_X integration points, acceptance tests, and Definition of Done.
```
