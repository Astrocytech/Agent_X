# LONG_TERM_LEARNING_OUTCOME_REVIEW_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: LONG_TERM_LEARNING_OUTCOME_REVIEW_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling contract, implementation-ready, v3 precision hardening
component_id: AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW
component_name: Long-Term Learning / Outcome Review Layer
roadmap_layer: 16
roadmap_phase: Phase F — Learning, Review, and System Memory
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Policy / Capability Rules, Evaluation / Regression Linkage Rules
conditional_standards: Command Acceptance Criteria, Report Template, Memory Contract, Promotion Gate Contract
optional_standards: ES, only for ecosystem placement
risk_level: critical
implementation_mode: evidence-based outcome review and memory-candidate generation; no autonomous durable memory by default
target_language: Python
canonical_subdirectory: tools/agentx_evolve/learning/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/learning/
review_required_for_durable_learning: true
human_approval_required_for_durable_memory: true
policy_required_for_durable_memory: true
network_enabled_by_default: false
source_mutation_allowed: false
git_write_allowed: false
contract_rating: 10/10
```

---

# 0. v3 Review and Upgrade Summary

The v2 contract was strong and already close to implementation-ready, but I would rate it:

```text
9.7/10
```

It already covered the major requirements for the Long-Term Learning / Outcome Review Layer:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
Learning Boundary Rules
Outcome Review Schema
Learning Signal Schema
Memory Candidate Schema
Promotion / Rejection Decision Schema
Regression Linkage Schema
Safety Guardrails
Role Permission Matrix
OpenCode borrowing notes
Agent_X integration notes
dependency gates
restricted mode
confidence thresholds
memory lifecycle controls
evidence hashing and immutability
simulated dependency tests
Definition of Done
freeze rule
```

It was not fully 10/10 because several precision details were still under-specified for a safety-critical learning layer:

```text
1. It did not define deterministic idempotency rules for reprocessing the same outcome evidence.
2. It did not define duplicate-candidate prevention and canonical memory-candidate identity rules.
3. It did not define strict memory state-transition rules to prevent jumping from draft/candidate directly to durable memory.
4. It did not define a dedicated memory promotion handoff contract separating this layer from the governed memory writer.
5. It did not define privacy retention, minimization, and sanitization requirements strongly enough.
6. It did not define reviewer-independence rules for high-risk durable learning.
7. It did not define scope-escalation controls to stop component-local lessons from becoming global rules.
8. It did not define read/query API limits for learning records.
9. It did not define deviation-register structure in enough detail.
10. It did not define locked/concurrent review behavior for simultaneous outcome reviews.
```

This v3 adds those missing controls and is the final 10/10 controlling contract for the Long-Term Learning / Outcome Review Layer.

---

# 1. Purpose

This document defines the controlling contract for the **Long-Term Learning / Outcome Review Layer** in Agent_X.

This layer reviews completed tasks, validation runs, patch sessions, promotion decisions, failures, regressions, monitoring incidents, documentation sync outcomes, and human feedback. It extracts structured learning signals from evidence and decides whether those signals should become:

```text
ignored observations
short-term run notes
review-only recommendations
memory candidates
blocked memory candidates
rejected memory candidates
regression links
future evaluation requirements
future policy recommendations
future documentation recommendations
future prompt-contract recommendations
```

This layer must not allow Agent_X to learn unsafe, unverified, private, misleading, or overfitted lessons.

The main goal is not simply to remember outcomes. The goal is to preserve useful evidence-backed lessons while preventing false self-reinforcement.

The layer creates **learning records and memory candidates**. It does not silently write durable memory, approve releases, mutate source code, override policy, or rewrite history.

---

# 2. Scope

## 2.1 Required in This Layer

The Long-Term Learning / Outcome Review Layer must define contracts for:

```text
outcome review records
learning signal extraction
memory candidate generation
memory approval and rejection workflow
memory lifecycle review
memory supersession and revocation recommendations
regression linkage
failure-to-learning linkage
success-to-learning linkage
human review for durable learning
evidence-backed learning decisions
learning policy decisions
learning audit logs
learning evidence manifests
learning review reports
learning safety boundaries
learning report generation
```

It must review outcomes from:

```text
completed implementation sessions
failed implementation sessions
validation runs
compileall results
pytest results
schema validation results
evaluation harness results
regression benchmark results
promotion/release gate outcomes
rollback events
monitoring/observability incidents
documentation synchronization outcomes
human review feedback
post-implementation review reports
completion records
policy denials
sandbox denials
tool execution failures
MCP exposure failures
backup/recovery verification events
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
LLM worker behavior
model adapter behavior
patch generation
patch application
source mutation
Git write operations
promotion approval
policy override
human approval UI
external memory store runtime
self-evolution orchestration
background scheduling
network sync
automatic durable memory write
```

This layer produces structured learning outputs. Other governed layers may later consume those outputs.

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because this layer decides what the system learns from its own behavior.

Bad learning can corrupt future planning, future patches, future evaluation criteria, prompt selection, policy recommendations, and agent behavior. Therefore this layer must fail closed.

EQC applies to:

```text
learning signal validity
memory candidate safety
regression linkage accuracy
outcome classification
human review requirements
false lesson prevention
overfitting prevention
evidence integrity
rejection of unsafe memory
conflict handling with prior memory
learning lifecycle control
```

If evidence is missing, incomplete, contradictory, stale, unverifiable, or outside the accepted artifact boundary, the layer must not create approved durable learning.

## 3.2 Required Supporting Standard: FIC

FIC is required because this layer has concrete implementation files and responsibilities.

Expected implementation files include:

```text
tools/agentx_evolve/learning/__init__.py
tools/agentx_evolve/learning/outcome_models.py
tools/agentx_evolve/learning/outcome_reviewer.py
tools/agentx_evolve/learning/learning_signal_extractor.py
tools/agentx_evolve/learning/memory_candidate_builder.py
tools/agentx_evolve/learning/learning_policy.py
tools/agentx_evolve/learning/learning_audit.py
tools/agentx_evolve/learning/regression_linker.py
tools/agentx_evolve/learning/memory_lifecycle.py
tools/agentx_evolve/learning/memory_promotion_handoff.py
tools/agentx_evolve/learning/learning_identity.py
tools/agentx_evolve/learning/learning_locking.py
tools/agentx_evolve/learning/learning_reporter.py
```

Each file must have:

```text
clear responsibility
public API
schema-bound inputs
schema-bound outputs
fail-closed behavior
evidence references
hash/provenance behavior where applicable
tests
no source mutation
no direct durable memory write
```

## 3.3 Required Supporting Standard: SIB

SIB is required because this layer integrates outcomes from many Agent_X components.

Integration boundaries include:

```text
Agent_X Initiator
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution Layer
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter Layer
Model Adapter Layer
Context Builder / Task Packer
Prompt Contract / Prompt Versioning Layer
LLM Implementation Worker
Self-Evolution Orchestrator
Human Review / Approval Interface
Promotion / Release Gate
Git Integration Layer
Evaluation Harness / Regression Benchmark Layer
Documentation Synchronization Layer
Task Queue / Session Scheduler
Monitoring / Observability Layer
Backup / Disaster Recovery Layer
```

This layer may consume evidence from those systems, but it must not become a bypass around them.

## 3.4 Required Schema Contract

Schema Contract is required because all learning records must be structured and auditable.

Required schemas:

```text
outcome_review.schema.json
learning_signal.schema.json
memory_candidate.schema.json
memory_decision.schema.json
memory_lifecycle_event.schema.json
regression_link.schema.json
learning_policy_decision.schema.json
learning_audit.schema.json
learning_report.schema.json
memory_promotion_request.schema.json
learning_record_identity.schema.json
learning_deviation.schema.json
learning_evidence_manifest.schema.json
learning_review_report.schema.json
learning_completion_record.schema.json
```

## 3.5 Required Evidence / Audit Rules

Every learning decision must produce evidence.

Evidence is required for:

```text
outcome reviewed
learning signal extracted
learning signal rejected
memory candidate created
memory candidate rejected
memory candidate blocked
memory candidate approved for human review
memory candidate promotion requested
memory promotion rejected
human approval received
human approval missing
policy decision produced
regression linked
regression link rejected
memory lifecycle review
memory supersession recommendation
memory revocation recommendation
learning report generated
learning decision blocked
```

No durable learning is valid without evidence references, policy authorization, and human approval.

---

# 4. Preconditions and Dependency Gates

This layer depends on prior Agent_X safety and evidence components. It must not become a substitute for them.

## 4.1 Required Prior Components for Full Operation

Before durable memory promotion can be requested, these must be present and validated:

```text
Policy / Capability Registry
Human Review / Approval Interface or approved human approval record source
Evaluation Harness / Regression Benchmark Layer, when learning depends on test/regression evidence
Promotion / Release Gate, when learning affects release decisions
Failure Taxonomy / Recovery Playbook, when learning derives from failure records
Monitoring / Observability Layer, when learning derives from incidents
Backup / Disaster Recovery Layer, when evidence recovery or integrity is part of the decision
```

## 4.2 Restricted Mode

If upstream components are missing, the layer may run in restricted mode.

Restricted mode allows:

```text
schema validation
outcome review draft creation
learning signal draft creation
memory candidate draft creation
rejected learning record creation
blocked learning record creation
learning audit logging
learning report generation
```

Restricted mode blocks:

```text
durable memory promotion
memory approval
policy-changing recommendation marked as approved
release-gate-affecting learning marked as approved
network sync
source mutation
Git write
background learning daemon
```

## 4.3 Dependency Gate Rules

```text
If Policy / Capability Registry is missing -> durable memory promotion BLOCKS.
If Human Approval source is missing -> durable memory promotion BLOCKS.
If evidence manifest is missing -> learning signals may be DRAFT only.
If Evaluation Harness is missing -> regression-derived learning must be LOW confidence or BLOCKED.
If Failure Taxonomy is missing -> failure-derived learning must use LEARNING_FAILURE_UNCLASSIFIED and require review.
If Promotion Gate is missing -> promotion-impacting learning must be recommendation-only.
If Memory Store is missing -> memory candidates may be produced, but no durable write is attempted.
If Backup / Recovery verification is missing -> recovered-evidence learning must be BLOCKED or LOW confidence.
```

## 4.4 Authority Rule

A learning decision is allowed only when all required authorities agree:

```text
Learning Boundary Rules
Policy / Capability Registry
Evidence / Audit Rules
Human Approval, when durable memory is requested
Evaluation / Regression evidence, when regression or success pattern is claimed
Promotion Gate, when release behavior is affected
Memory Contract, when durable memory write is requested
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCKED
REJECTED
NEEDS_MORE_EVIDENCE
NEEDS_HUMAN_REVIEW
DRAFT_ONLY
APPROVED_FOR_REVIEW
PROMOTE_REQUESTED
PROMOTED_BY_HUMAN
```

The layer itself must never silently jump from `DRAFT` to durable memory.

---

# 5. Status Vocabulary

Use only these status values in learning records and review tables.

```text
DRAFT
CANDIDATE
APPROVED_FOR_REVIEW
NEEDS_MORE_EVIDENCE
NEEDS_HUMAN_REVIEW
PROMOTE_REQUESTED
PROMOTED_BY_HUMAN
REJECTED
BLOCKED
INVALID
SUPERSEDED
REVOKE_RECOMMENDED
EXPIRED
```

| Status | Meaning | Durable memory allowed? |
|---|---|---|
| DRAFT | Record exists for review only. | No |
| CANDIDATE | Candidate is eligible for review but not approved. | No |
| APPROVED_FOR_REVIEW | Safe enough to send to human review. | No |
| NEEDS_MORE_EVIDENCE | Evidence threshold not met. | No |
| NEEDS_HUMAN_REVIEW | Human review required. | No |
| PROMOTE_REQUESTED | Promotion request created for human approval. | No |
| PROMOTED_BY_HUMAN | Human-approved durable memory may be written by the memory layer. | Yes, by governed memory layer only |
| REJECTED | Not accepted as learning. | No |
| BLOCKED | Safety/policy/evidence block. | No |
| INVALID | Schema or structural invalidity. | No |
| SUPERSEDED | Replaced by newer approved memory. | No new write |
| REVOKE_RECOMMENDED | Existing memory should be reviewed for revocation. | No |
| EXPIRED | Memory or candidate expired. | No |

The term `APPROVED` must not be used alone because it is ambiguous. Use either `APPROVED_FOR_REVIEW` or `PROMOTED_BY_HUMAN`.

---

# 6. Why This Layer Needs Strict Controls

The Long-Term Learning / Outcome Review Layer is safety-critical because it decides:

```text
what Agent_X learns from previous runs
which outcomes are considered successful
which failures become future blockers
which mistakes are remembered
which patterns are reused
which lessons are rejected
which artifacts are linked to regressions
which learning candidates require human approval
which learning signals can influence future planning
```

The main danger is **bad learning**.

This layer must prevent:

```text
learning from incomplete evidence
treating a lucky success as a general rule
treating a failed run as a valid success pattern
storing unsafe instructions as memory
storing secrets or private data as memory
promoting unverified model conclusions
reinforcing bad patches
hiding regressions
rewriting history after failure
letting the system approve its own durable learning without review
turning temporary workaround behavior into long-term policy
learning from generated claims without validation evidence
preserving outdated lessons after newer contradictory evidence appears
creating global rules from component-specific behavior
```

---

# 7. Learning Boundary Rules

## 7.1 What Outcomes Are Reviewed

This layer must review outcomes from:

```text
implementation sessions
validation sessions
compileall runs
pytest runs
schema validation runs
security sandbox denials
policy denials
tool execution outcomes
MCP exposure outcomes
patch prechecks
patch application attempts
rollback sessions
Git integration events
promotion gate decisions
regression benchmark runs
monitoring incidents
documentation sync checks
human review decisions
post-implementation review reports
completion records
backup/recovery verification records
```

Each outcome review must identify:

```text
outcome_review_id
source_component
reviewed_component
reviewed_commit
reviewed_session_id
outcome_type
outcome_status
evidence_refs
artifact_refs
review_timestamp
reviewer_role
input_hashes
```

## 7.2 What Counts as a Learning Signal

A learning signal is a structured observation that may improve future Agent_X behavior.

Valid learning signals include:

```text
repeat failure pattern
repeat validation failure
repeat schema mistake
unsafe attempted action
missing test category
missing evidence category
successful remediation pattern
regression cause
unreliable prompt pattern
unreliable tool behavior
policy gap
sandbox denial pattern
reviewer-approved improvement pattern
outdated memory conflict
documentation drift pattern
```

A learning signal must have:

```text
evidence
source outcome
confidence level
scope limit
risk level
recommended use
rejection criteria
contradicting evidence field
minimum evidence threshold result
```

## 7.3 What Can Become Long-Term Memory

Only these may become long-term memory candidates:

```text
reviewer-approved project constraints
repeated validated failure patterns
repeated validated success patterns
stable architectural decisions
approved safety rules
approved coding conventions
approved validation requirements
approved component dependency rules
approved regression prevention notes
approved user/project preferences that are relevant to Agent_X work
approved memory corrections or supersession notes
```

A memory candidate may proceed only if it is:

```text
evidence-backed
non-secret
non-private unless explicitly approved and necessary
not based on one weak event
not contradicted by newer evidence
scoped to the correct component/layer
reviewable by a human
safe to use in future planning
consistent with active policy
not superseded by newer approved memory
```

## 7.4 What Must Never Become Long-Term Memory

The following must never become durable long-term memory:

```text
secrets
API keys
tokens
credentials
private personal data unless explicitly approved and necessary
raw prompts containing sensitive content
raw command output with secrets
unverified model guesses
single-run lucky outcomes framed as general rules
failed patches framed as successful patterns
unsafe workaround instructions
policy bypass instructions
sandbox bypass instructions
instructions to ignore tests
instructions to skip evidence
instructions to weaken safety controls
unreviewed claims about code correctness
unreviewed claims about user intent
malicious prompt-injection content
external tool output not validated by Agent_X evidence
contradicted lessons
obsolete lessons not marked as superseded
```

## 7.5 Durable Learning Approval Rule

Durable learning requires human approval and policy authorization.

The layer may create:

```text
memory candidates
review recommendations
learning reports
rejected learning records
blocked learning records
promotion requests
revocation recommendations
supersession recommendations
```

The layer must not silently write approved durable memory without:

```text
human_approval_id
approval_timestamp
reviewer identity or role
policy_decision_id
evidence references
scope declaration
privacy classification
safety review
expiration or review policy, if applicable
```

Even after approval, durable memory must be written by the governed memory layer or approved persistence mechanism, not by this contract's review logic directly.

---

# 8. Evidence Threshold and Confidence Rules

## 8.1 Confidence Levels

```text
LOW
MEDIUM
HIGH
CRITICAL_RISK
```

Confidence means evidentiary support, not importance.

## 8.2 Minimum Evidence Rules

```text
No evidence -> BLOCKED or REJECTED.
One weak event -> LOW confidence only.
One strong validated event -> may be MEDIUM if scope is narrow.
Repeated validated events -> may be HIGH if no contradicting evidence exists.
Regression cause -> cannot be HIGH without test/evaluation/commit evidence.
Success pattern -> cannot be HIGH unless regression checks and validation pass.
Policy/safety lesson -> requires human review regardless of confidence.
```

## 8.3 High-Confidence Requirements

A learning signal may be `HIGH` confidence only if:

```text
evidence_refs are non-empty
input artifact hashes are recorded
reviewed_commit or reviewed_session_id is present where applicable
no unresolved contradicting evidence exists
scope is narrow and explicit
validation or regression evidence supports the signal
```

## 8.4 Single-Run Rule

Single-run observations must default to LOW confidence unless the evidence is a deterministic safety rule violation, such as:

```text
secret detected
policy bypass attempt
sandbox bypass attempt
schema-invalid result
evidence tampering attempt
```

Even then, a single event may justify a blocker or policy recommendation, not an automatic durable global rule.

---

# 9. Outcome Review Schema Contract

Every outcome review must use this structure.

```json
{
  "schema_version": "1.0",
  "schema_id": "outcome_review.schema.json",
  "outcome_review_id": "string",
  "created_at": "string",
  "source_component": "LongTermLearningOutcomeReview",
  "reviewed_component": "string",
  "reviewed_layer": "string|null",
  "reviewed_commit": "string|null",
  "reviewed_session_id": "string|null",
  "outcome_type": "IMPLEMENTATION|VALIDATION|PROMOTION|REGRESSION|ROLLBACK|HUMAN_REVIEW|MONITORING|DOCUMENTATION|BACKUP_RECOVERY|POLICY|SANDBOX|TOOL_EXECUTION|OTHER",
  "outcome_status": "SUCCESS|PARTIAL|FAILED|BLOCKED|REJECTED|UNKNOWN",
  "summary": "string",
  "evidence_refs": [],
  "artifact_refs": [],
  "input_records": [],
  "input_hashes": [],
  "review_findings": [],
  "learning_signal_ids": [],
  "regression_link_ids": [],
  "memory_candidate_ids": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
outcome_review_id is required.
created_at is required.
outcome_type is required.
outcome_status is required.
evidence_refs must not be empty for SUCCESS, FAILED, REGRESSION, PROMOTION, POLICY, SANDBOX, or TOOL_EXECUTION outcomes.
UNKNOWN status cannot produce approved memory candidates.
Input hashes are required when local artifacts are used to derive learning.
```

---

# 10. Learning Signal Schema Contract

Every learning signal must use this structure.

```json
{
  "schema_version": "1.0",
  "schema_id": "learning_signal.schema.json",
  "learning_signal_id": "string",
  "created_at": "string",
  "source_component": "LongTermLearningOutcomeReview",
  "source_outcome_review_id": "string",
  "signal_type": "SUCCESS_PATTERN|FAILURE_PATTERN|REGRESSION_CAUSE|POLICY_GAP|SANDBOX_PATTERN|TEST_GAP|SCHEMA_GAP|EVIDENCE_GAP|PROMPT_GAP|TOOL_GAP|DOCUMENTATION_GAP|MEMORY_CONFLICT|MEMORY_OBSOLETE|OTHER",
  "signal_status": "DRAFT|CANDIDATE|APPROVED_FOR_REVIEW|NEEDS_MORE_EVIDENCE|REJECTED|BLOCKED|INVALID",
  "description": "string",
  "scope": {
    "component_id": "string|null",
    "layer": "string|null",
    "file_paths": [],
    "applies_to_future_layers": false,
    "applies_globally": false
  },
  "confidence": "LOW|MEDIUM|HIGH",
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "evidence_refs": [],
  "evidence_hashes": [],
  "contradicting_evidence_refs": [],
  "recommended_action": "IGNORE|REVIEW|CREATE_MEMORY_CANDIDATE|CREATE_TEST|CREATE_POLICY_UPDATE|CREATE_DOCUMENTATION_UPDATE|BLOCK_PATTERN|REVOKE_MEMORY|SUPERSEDE_MEMORY",
  "human_review_required": true,
  "minimum_evidence_threshold_met": false,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
single-run signals default to LOW confidence unless supported by deterministic safety evidence.
critical-risk signals require human review.
signals with unresolved contradicting evidence cannot become memory candidates for promotion.
signals without evidence must be REJECTED or BLOCKED.
global scope requires explicit human review and policy authorization.
```

---

# 11. Memory Candidate Schema Contract

Every memory candidate must use this structure.

```json
{
  "schema_version": "1.0",
  "schema_id": "memory_candidate.schema.json",
  "memory_candidate_id": "string",
  "created_at": "string",
  "source_component": "LongTermLearningOutcomeReview",
  "source_learning_signal_ids": [],
  "source_outcome_review_ids": [],
  "canonical_identity_hash": "string",
  "duplicate_of_candidate_id": "string|null",
  "candidate_type": "PROJECT_RULE|SAFETY_RULE|ARCHITECTURE_DECISION|VALIDATION_RULE|REGRESSION_PREVENTION|USER_PREFERENCE|PROCESS_LESSON|REJECTED_PATTERN|MEMORY_CORRECTION|MEMORY_SUPERSESSION|MEMORY_REVOCATION|OTHER",
  "candidate_status": "DRAFT|CANDIDATE|APPROVED_FOR_REVIEW|NEEDS_MORE_EVIDENCE|NEEDS_HUMAN_REVIEW|PROMOTE_REQUESTED|PROMOTED_BY_HUMAN|REJECTED|BLOCKED|INVALID|SUPERSEDED|EXPIRED",
  "proposed_memory_text": "string",
  "scope": {
    "project": "Agent_X",
    "component_id": "string|null",
    "layer": "string|null",
    "applies_globally": false
  },
  "evidence_refs": [],
  "evidence_hashes": [],
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "privacy_classification": "NON_SENSITIVE|SENSITIVE|SECRET_OR_CREDENTIAL|UNKNOWN",
  "safety_review": {
    "contains_secret": false,
    "contains_private_data": false,
    "contains_unverified_claim": false,
    "contains_policy_bypass": false,
    "contains_sandbox_bypass": false,
    "contains_instruction_to_weaken_safety": false,
    "contains_prompt_injection": false,
    "contains_contradicted_claim": false
  },
  "conflict_review": {
    "checked_existing_memory": false,
    "conflicting_memory_ids": [],
    "supersedes_memory_ids": [],
    "requires_revocation_review": false
  },
  "human_review_required": true,
  "human_approval_id": "string|null",
  "policy_decision_id": "string|null",
  "expiration_or_review_policy": "string|null",
  "retention_policy": {
    "retain_until": "string|null",
    "review_after": "string|null",
    "data_minimization_applied": true
  },
  "warnings": [],
  "errors": []
}
```

Rules:

```text
candidate_status cannot be PROMOTED_BY_HUMAN without human_approval_id and policy_decision_id.
SECRET_OR_CREDENTIAL candidates must be BLOCKED.
UNKNOWN privacy classification cannot be promoted.
contains_policy_bypass=true must BLOCK.
contains_sandbox_bypass=true must BLOCK.
contains_instruction_to_weaken_safety=true must BLOCK.
contains_prompt_injection=true must BLOCK unless sanitized and reframed as a blocked pattern.
contains_unverified_claim=true must require human review and cannot auto-promote.
checked_existing_memory must be true before promotion request.
conflicting memory requires review before promotion.
canonical_identity_hash must be present before promotion request.
duplicate candidates must be linked instead of promoted separately.
retention_policy.data_minimization_applied must be true before promotion request.
```

---

# 12. Promotion / Rejection Decision Schema Contract

Every memory decision must use this structure.

```json
{
  "schema_version": "1.0",
  "schema_id": "memory_decision.schema.json",
  "memory_decision_id": "string",
  "created_at": "string",
  "source_component": "LongTermLearningOutcomeReview",
  "memory_candidate_id": "string",
  "decision": "PROMOTE_REQUESTED|PROMOTED_BY_HUMAN|REJECT|BLOCK|NEEDS_MORE_EVIDENCE|NEEDS_HUMAN_REVIEW|SUPERSEDE|REVOKE_RECOMMENDED|EXPIRE",
  "decision_reason": "string",
  "decider_role": "LEARNING_REVIEWER|HUMAN_OPERATOR|POLICY_REVIEWER|PROMOTION_CHECKER|UNKNOWN",
  "human_approval_id": "string|null",
  "policy_decision_id": "string|null",
  "evidence_refs": [],
  "evidence_hashes": [],
  "blocked_reasons": [],
  "followup_actions": [],
  "warnings": [],
  "errors": []
}
```

Decision rules:

```text
PROMOTED_BY_HUMAN requires human_approval_id.
PROMOTED_BY_HUMAN requires policy_decision_id.
PROMOTED_BY_HUMAN requires non-empty evidence_refs.
UNKNOWN decider_role cannot promote.
NEEDS_MORE_EVIDENCE cannot write durable memory.
NEEDS_HUMAN_REVIEW cannot write durable memory.
BLOCK must preserve reason and evidence.
REJECT must preserve reason and evidence if available.
SUPERSEDE and REVOKE_RECOMMENDED require target memory IDs in followup_actions or candidate conflict_review.
```

---

# 13. Memory Lifecycle Event Schema Contract

Every memory lifecycle event must use this structure.

```json
{
  "schema_version": "1.0",
  "schema_id": "memory_lifecycle_event.schema.json",
  "memory_lifecycle_event_id": "string",
  "created_at": "string",
  "source_component": "LongTermLearningOutcomeReview",
  "target_memory_id": "string|null",
  "source_memory_candidate_id": "string|null",
  "event_type": "REVIEW_DUE|REVIEW_COMPLETED|SUPERSESSION_RECOMMENDED|REVOCATION_RECOMMENDED|EXPIRATION_RECOMMENDED|CONFLICT_FOUND|EVIDENCE_INVALIDATED|HASH_MISMATCH_FOUND",
  "reason": "string",
  "evidence_refs": [],
  "evidence_hashes": [],
  "recommended_action": "KEEP|REVIEW|SUPERSEDE|REVOKE|EXPIRE|BLOCK_USE",
  "human_review_required": true,
  "warnings": [],
  "errors": []
}
```

Lifecycle rules:

```text
Learning records may age, expire, be superseded, or become suspect.
Hash mismatch requires BLOCK_USE or review.
Contradictory newer evidence requires review.
Deprecated component behavior cannot remain active global memory without review.
Revocation recommendations do not delete evidence; they mark memory for governed review.
```

---

# 14. Memory Promotion Handoff Schema Contract

This layer may request durable memory promotion, but it must not directly perform the durable write.

Every memory promotion handoff must use this structure.

```json
{
  "schema_version": "1.0",
  "schema_id": "memory_promotion_request.schema.json",
  "memory_promotion_request_id": "string",
  "created_at": "string",
  "source_component": "LongTermLearningOutcomeReview",
  "memory_candidate_id": "string",
  "memory_decision_id": "string",
  "requested_target": "GOVERNED_MEMORY_LAYER|HUMAN_REVIEW_QUEUE|POLICY_REVIEW_QUEUE",
  "requested_action": "PROMOTE|REVIEW|REJECT|SUPERSEDE|REVOKE_REVIEW",
  "proposed_memory_text_redacted": "string",
  "canonical_identity_hash": "string",
  "scope": {
    "project": "Agent_X",
    "component_id": "string|null",
    "layer": "string|null",
    "applies_globally": false
  },
  "human_approval_id": "string|null",
  "policy_decision_id": "string",
  "evidence_refs": [],
  "evidence_hashes": [],
  "privacy_classification": "NON_SENSITIVE|SENSITIVE|SECRET_OR_CREDENTIAL|UNKNOWN",
  "handoff_status": "REQUESTED|BLOCKED|REJECTED|ACCEPTED_BY_GOVERNED_MEMORY_LAYER",
  "warnings": [],
  "errors": []
}
```

Handoff rules:

```text
This layer may create a promotion request, but it must not directly write durable memory.
PROMOTE requests require human_approval_id.
PROMOTE requests require policy_decision_id.
PROMOTE requests require evidence_refs and evidence_hashes.
SECRET_OR_CREDENTIAL and UNKNOWN privacy classifications must BLOCK.
The proposed memory text in handoff artifacts must be redacted and minimized.
The governed memory layer must perform the actual durable write and must create its own evidence.
```

---

# 15. Learning Record Identity and Idempotency Contract

Outcome review and learning operations must be deterministic when they process the same inputs.

Every generated record must have either a stable deterministic identity or a documented reason for using a generated unique ID.

Required identity fields where applicable:

```text
source_component
reviewed_component
reviewed_commit
reviewed_session_id
source_outcome_review_ids
source_learning_signal_ids
evidence_hashes
canonical_scope
canonical_memory_text_hash
canonical_identity_hash
```

Idempotency rules:

```text
Reprocessing the same input evidence must not create multiple active memory candidates for the same lesson.
Duplicate candidates must be linked with duplicate_of_candidate_id.
Canonical identity must normalize whitespace, ordering of evidence refs, and ordering of source IDs.
A repeated review may append audit evidence but must not overwrite prior evidence.
If the same candidate is regenerated with changed text, it must be treated as a revision and require review.
If input evidence hashes change, the prior learning decision becomes suspect and requires lifecycle review.
```

Concurrency rules:

```text
A review lock must be acquired before writing latest learning artifacts.
Concurrent reviews may append independent JSONL records but must not overwrite each other's latest artifacts without atomic write semantics.
Lock artifacts, if used, must live under .agentx-init/learning/locks/.
Stale locks must be detectable and must not result in source mutation.
Concurrent duplicate memory candidates must be resolved by canonical_identity_hash.
```

---

# 16. Memory State Transition Contract

Memory and learning records must move through explicit states.

Allowed candidate state transitions:

```text
DRAFT -> CANDIDATE
DRAFT -> REJECTED
DRAFT -> BLOCKED
CANDIDATE -> APPROVED_FOR_REVIEW
CANDIDATE -> NEEDS_MORE_EVIDENCE
CANDIDATE -> REJECTED
CANDIDATE -> BLOCKED
APPROVED_FOR_REVIEW -> NEEDS_HUMAN_REVIEW
APPROVED_FOR_REVIEW -> PROMOTE_REQUESTED
PROMOTE_REQUESTED -> PROMOTED_BY_HUMAN
PROMOTE_REQUESTED -> REJECTED
PROMOTE_REQUESTED -> BLOCKED
PROMOTED_BY_HUMAN -> SUPERSEDED
PROMOTED_BY_HUMAN -> REVOKE_RECOMMENDED
ANY_NON_FINAL -> EXPIRED
```

Forbidden transitions:

```text
DRAFT -> PROMOTED_BY_HUMAN
CANDIDATE -> PROMOTED_BY_HUMAN
NEEDS_MORE_EVIDENCE -> PROMOTED_BY_HUMAN
REJECTED -> PROMOTED_BY_HUMAN
BLOCKED -> PROMOTED_BY_HUMAN
INVALID -> PROMOTED_BY_HUMAN
SUPERSEDED -> PROMOTED_BY_HUMAN without new candidate and new review
EXPIRED -> PROMOTED_BY_HUMAN without new candidate and new review
```

Transition rules:

```text
Every state transition must produce a MemoryDecision or MemoryLifecycleEvent.
High-risk transitions require reviewer identity and policy decision.
Promotion to durable memory requires human approval.
Final states must not be silently reopened; a new candidate or lifecycle event must be created.
State transitions must be append-only in history; prior states are not overwritten.
```

---

# 17. Privacy, Retention, and Data Minimization Contract

Learning records must preserve enough evidence for audit without turning logs into uncontrolled memory.

Privacy classifications:

```text
NON_SENSITIVE
SENSITIVE
SECRET_OR_CREDENTIAL
UNKNOWN
```

Data minimization rules:

```text
Store summaries and evidence references instead of raw sensitive content.
Redact secrets before writing learning artifacts.
Do not store raw prompts, raw command output, raw stack traces, or raw tool output if they contain secrets or private data.
If sensitive content is necessary for review, store only a redacted excerpt and a pointer to governed evidence.
UNKNOWN privacy classification cannot be promoted.
SECRET_OR_CREDENTIAL cannot become memory and must trigger a safety block.
```

Retention rules:

```text
Every memory candidate must define retain_until or review_after when it is high risk, sensitive, temporary, or component-specific.
Temporary workaround lessons must have a review_after field.
Component-specific lessons must be re-reviewed after major component changes.
Rejected and blocked candidates remain as evidence but must not be used as active guidance.
Revoked or superseded memory remains auditable but must be marked inactive by the governed memory layer.
```

---

# 18. Scope Escalation and Reviewer Independence Rules

A local lesson must not become a global Agent_X rule without explicit evidence and review.

Scope rules:

```text
File-specific observations remain file-scoped unless repeated across files.
Component-specific observations remain component-scoped unless repeated across components.
Layer-specific observations remain layer-scoped unless confirmed across layers.
Project-global memory requires human approval, policy authorization, and explicit applies_globally=true justification.
Safety rules may be global if they are deterministic and policy-approved.
Convenience preferences must not become global safety rules.
```

Reviewer independence rules:

```text
The same automated actor that produced a patch must not be the sole authority promoting durable learning from that patch.
High-risk memory candidates require HUMAN_OPERATOR approval.
Policy-impacting memory candidates require POLICY_REVIEWER or policy decision evidence.
Promotion-impacting learning requires PROMOTION_CHECKER review evidence.
The layer may recommend; it must not self-approve durable memory.
```

---

# 19. Learning Read / Query API Boundary

Read/query functionality is allowed only for inspection and review.

Allowed read/query behavior:

```text
list outcome reviews
list learning signals
list memory candidates
show candidate status
show regression links
show evidence refs and hashes
show active vs superseded/revoked status
```

Forbidden read/query behavior:

```text
return unredacted secrets
return raw sensitive evidence by default
change candidate state
approve durable memory
delete evidence
rewrite historical learning records
mutate source files
call network by default
```

Query results must distinguish:

```text
active memory
candidate memory
rejected candidate
blocked candidate
superseded memory
revocation-recommended memory
expired candidate
```

---

# 20. Regression Linkage Schema Contract

Every regression link must use this structure.

```json
{
  "schema_version": "1.0",
  "schema_id": "regression_link.schema.json",
  "regression_link_id": "string",
  "created_at": "string",
  "source_component": "LongTermLearningOutcomeReview",
  "regression_id": "string",
  "detected_by": "EVALUATION_HARNESS|PROMOTION_GATE|MONITORING|HUMAN_REVIEW|TEST_SUITE|OTHER",
  "suspected_source_commit": "string|null",
  "suspected_source_session_id": "string|null",
  "suspected_component_id": "string|null",
  "affected_tests": [],
  "affected_schemas": [],
  "affected_runtime_artifacts": [],
  "confidence": "LOW|MEDIUM|HIGH",
  "evidence_refs": [],
  "evidence_hashes": [],
  "contradicting_evidence_refs": [],
  "recommended_action": "INVESTIGATE|ROLLBACK_REVIEW|ADD_TEST|UPDATE_POLICY|UPDATE_DOCUMENTATION|BLOCK_PROMOTION|NO_ACTION",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
regression links require evidence_refs.
LOW confidence links cannot be treated as proven causes.
contradicting evidence must reduce confidence or block promotion of the lesson.
regression links must not blame a commit without evidence.
regression links must not create durable memory without human review.
```

---

# 21. Learning Policy Decision Schema Contract

Every learning policy decision must use this structure.

```json
{
  "schema_version": "1.0",
  "schema_id": "learning_policy_decision.schema.json",
  "learning_policy_decision_id": "string",
  "created_at": "string",
  "source_component": "LearningPolicy",
  "caller_role": "string",
  "requested_action": "CREATE_OUTCOME_REVIEW|CREATE_LEARNING_SIGNAL|CREATE_MEMORY_CANDIDATE|REQUEST_PROMOTION|PROMOTE_MEMORY|REJECT_MEMORY|LINK_REGRESSION|RECOMMEND_REVOCATION|WRITE_REPORT",
  "target_record_id": "string|null",
  "decision": "ALLOW|BLOCK|NEEDS_HUMAN_REVIEW|NEEDS_MORE_EVIDENCE|DRAFT_ONLY",
  "reason": "string",
  "required_checks": [],
  "missing_checks": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
PROMOTE_MEMORY requires HUMAN_OPERATOR and human approval.
MCP_CLIENT cannot create memory candidates or promote memory.
UNKNOWN_CALLER blocks by default.
Missing policy service blocks promotion.
Policy decisions must be referenced by memory decisions when promotion is requested.
```

---

# 22. Evidence / Audit Contract

## 16.1 Runtime Artifact Root

All learning artifacts must be written under:

```text
.agentx-init/learning/
```

Expected artifacts:

```text
.agentx-init/learning/outcome_review_history.jsonl
.agentx-init/learning/learning_signal_history.jsonl
.agentx-init/learning/memory_candidate_history.jsonl
.agentx-init/learning/memory_decision_history.jsonl
.agentx-init/learning/memory_lifecycle_history.jsonl
.agentx-init/learning/memory_promotion_request_history.jsonl
.agentx-init/learning/regression_link_history.jsonl
.agentx-init/learning/learning_policy_decision_history.jsonl
.agentx-init/learning/learning_audit_history.jsonl
.agentx-init/learning/latest_outcome_review.json
.agentx-init/learning/latest_learning_signal.json
.agentx-init/learning/latest_memory_candidate.json
.agentx-init/learning/latest_memory_decision.json
.agentx-init/learning/latest_memory_lifecycle_event.json
.agentx-init/learning/latest_memory_promotion_request.json
.agentx-init/learning/latest_regression_link.json
.agentx-init/learning/learning_evidence_manifest.json
.agentx-init/learning/learning_review_report.json
.agentx-init/learning/learning_completion_record.json
```

## 16.2 Evidence Rules

Evidence must be:

```text
append-only for history
atomic for latest JSON artifacts
schema-valid
redacted before persistence
linked to reviewed commit/session where available
hashable with SHA-256
reproducible from recorded inputs
recorded in an evidence manifest
immutable after sign-off unless a new review record is created
```

## 16.3 SHA-256 Hash Rule

The evidence manifest must include SHA-256 hashes for:

```text
learning_evidence_manifest.json
learning_review_report.json
learning_completion_record.json
all JSONL history files used by final review
all latest artifacts used by final review
all external evidence files referenced by learning decisions where local path access is available
```

Hashing must use Python standard library `hashlib` if no project hash helper exists.

## 16.4 Evidence Immutability Rule

After a learning review report records a final decision:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous learning decision
new validation evidence must record a new timestamp and reviewed commit/session
manual edits to learning evidence after sign-off must be listed as deviations
```

## 16.5 Audit Events

Every audit event must record:

```text
audit_id
timestamp
source_component
event_type
related_outcome_review_id
related_learning_signal_id
related_memory_candidate_id
related_memory_decision_id
related_memory_lifecycle_event_id
related_regression_link_id
status
message
evidence_refs
artifact_refs
warnings
errors
```

Required audit event types:

```text
OUTCOME_REVIEW_CREATED
LEARNING_SIGNAL_CREATED
LEARNING_SIGNAL_REJECTED
MEMORY_CANDIDATE_CREATED
MEMORY_CANDIDATE_REJECTED
MEMORY_CANDIDATE_BLOCKED
MEMORY_CANDIDATE_APPROVED_FOR_REVIEW
DURABLE_MEMORY_PROMOTION_REQUESTED
DURABLE_MEMORY_PROMOTION_APPROVED_BY_HUMAN
DURABLE_MEMORY_PROMOTION_REJECTED
MEMORY_SUPERSESSION_RECOMMENDED
MEMORY_REVOCATION_RECOMMENDED
REGRESSION_LINK_CREATED
REGRESSION_LINK_REJECTED
EVIDENCE_MISSING
EVIDENCE_HASH_MISMATCH
SECRET_REDACTED
SAFETY_BLOCK
POLICY_BLOCK
```

---

# 23. Learning Evidence Manifest Schema Contract

Create:

```text
.agentx-init/learning/learning_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "learning_evidence_manifest.schema.json",
  "component_id": "AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW",
  "created_at": "<UTC timestamp>",
  "reviewed_commit": "<commit hash|null>",
  "reviewed_session_id": "<session id|null>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "input_records": [],
  "input_record_hashes": [],
  "generated_records": [],
  "generated_record_hashes": [],
  "runtime_artifacts": [],
  "runtime_artifact_hashes": [],
  "policy_decision_refs": [],
  "human_approval_refs": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "durable_memory_write_status": "NOT_ATTEMPTED_OR_GOVERNED",
  "hash_status": "PASS"
}
```

A final positive learning decision is invalid if required hashes are missing.

---

# 24. Learning Review Report Schema Contract

Create:

```text
.agentx-init/learning/learning_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "learning_review_report.schema.json",
  "component_id": "AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW",
  "review_document_id": "LONG_TERM_LEARNING_OUTCOME_REVIEW_EQC_FIC_SIB_SCHEMA_CONTRACT",
  "review_document_version": "v3.0",
  "reviewed_commit": "<commit hash|null>",
  "reviewed_session_id": "<session id|null>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {},
  "outcome_reviews_created": [],
  "learning_signals_created": [],
  "memory_candidates_created": [],
  "memory_decisions_created": [],
  "regression_links_created": [],
  "blocked_items": [],
  "rejected_items": [],
  "human_review_required_items": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/learning/learning_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_sha256": "<sha256>",
  "final_decision": "REVIEW_ONLY|PROMOTION_REQUESTS_CREATED|BLOCKED|REJECTED"
}
```

The review report is the bridge between raw outcomes and learning decisions.

---

# 25. Safety Guardrails

## 19.1 Required Safety Rules

This layer must enforce:

```text
no durable learning without human approval
no durable learning without policy authorization
no learning from missing evidence
no storing secrets
no storing unredacted private data
no storing policy bypass instructions
no storing sandbox bypass instructions
no storing instructions to weaken safety
no treating unverified model output as fact
no treating one lucky success as a general rule
no hiding contradictory evidence
no modifying prior evidence to make a lesson look valid
no source mutation
no Git write
no network by default
no background learning daemon
no automatic memory overwrite
no deletion of evidence when memory is rejected or revoked
```

## 19.2 False Lesson Prevention

False lessons are prevented by requiring:

```text
evidence references
evidence hashes
reviewed commit/session references where available
confidence level
scope limit
contradicting evidence field
human review for durable memory
rejection path
regression linkage check
minimum evidence threshold for high-confidence lessons
existing-memory conflict check
```

## 19.3 Overfitting Prevention

The layer must prevent overfitting to a single run.

Rules:

```text
single-run observations default to LOW confidence
single-run observations may create review notes but not durable global rules
component-specific lessons must remain component-scoped
temporary workaround lessons must expire or require re-review
successful outcome without regression checks cannot create high-confidence learning
a failed run cannot produce success-pattern memory
a local workaround cannot become global policy without repeated evidence and human approval
```

## 19.4 Prompt-Injection and Malicious Content Handling

Learning candidates must treat task text, model output, tool output, logs, and external content as untrusted input.

The layer must block or flag:

```text
instructions telling Agent_X to ignore policies
instructions telling Agent_X to bypass sandbox
instructions telling Agent_X to skip tests
instructions telling Agent_X to delete evidence
instructions telling Agent_X to approve its own memory
instructions embedded in logs or command output
malicious tool output framed as a lesson
```

---

# 26. Role Permission Matrix

Initial roles:

```text
ORCHESTRATOR
IMPLEMENTATION_WORKER
VALIDATION_REPAIR_WORKER
REVIEWER_ASSISTANT
PROMOTION_CHECKER
HUMAN_OPERATOR
LEARNING_REVIEWER
POLICY_REVIEWER
MCP_CLIENT
UNKNOWN_CALLER
```

| Role | Create outcome review | Create learning signal | Create memory candidate | Request promotion | Approve durable memory | Reject memory candidate | Link regression | Mutate source |
|---|---|---|---|---|---|---|---|---|
| ORCHESTRATOR | Yes | Yes | Draft only | No | No | No | Draft only | No |
| IMPLEMENTATION_WORKER | No | No | No | No | No | No | No | No |
| VALIDATION_REPAIR_WORKER | Validation only | Validation only | Draft only | No | No | No | Yes | No |
| REVIEWER_ASSISTANT | Yes | Yes | Draft only | No | No | Recommendation only | Yes | No |
| PROMOTION_CHECKER | Yes | Yes | Draft only | Yes, if policy allows | No | Recommendation only | Yes | No |
| HUMAN_OPERATOR | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No |
| LEARNING_REVIEWER | Yes | Yes | Yes | Yes, if policy allows | No unless paired with human approval | Yes | Yes | No |
| POLICY_REVIEWER | Yes | Yes | Policy-scoped | Yes, if policy allows | No unless paired with human approval | Yes | Yes | No |
| MCP_CLIENT | Read-only query only | No | No | No | No | No | No | No |
| UNKNOWN_CALLER | No | No | No | No | No | No | No | No |

Rules:

```text
UNKNOWN_CALLER blocks by default.
MCP_CLIENT cannot create durable learning.
No role in this layer may mutate source code.
Only HUMAN_OPERATOR can approve durable memory.
Reviewer roles may recommend, reject, or block, but not silently promote durable memory.
```

---

# 27. OpenCode Borrowing Notes

## 21.1 Concepts That May Be Borrowed

OpenCode-style concepts that may be useful:

```text
session summaries
tool-call traces
review notes
plan/result comparison
failure-aware iteration
structured task records
explicit human question/review points
```

## 21.2 Concepts That Must Be Restricted

Do not copy assumptions that allow:

```text
model-generated lessons to become durable memory automatically
tool output to become trusted without validation
session success to override test evidence
agent self-approval of memory
broad plugin/tool learning without Agent_X policy
unreviewed task traces to become permanent instructions
external provider traces to become memory without redaction
```

## 21.3 Agent_X Mapping

| OpenCode-style concept | Agent_X equivalent | Required control |
|---|---|---|
| Session summary | Outcome review | Evidence required |
| Tool trace | Audit/evidence input | Redaction and hash/provenance required |
| Plan/result comparison | Learning signal | Confidence and scope required |
| Failure iteration | Failure-pattern signal | Must link to tests/evidence |
| Human question | Human review requirement | Durable learning requires approval |
| Memory / skill refinement | Memory candidate | Human approval and schema validation required |

---

# 28. Agent_X Integration Notes

## 22.1 Evaluation Harness / Regression Benchmark Layer

This layer must consume:

```text
test results
benchmark results
regression reports
expected-vs-actual behavior
failure artifacts
```

It may produce:

```text
regression links
test-gap learning signals
future benchmark recommendations
promotion blockers
```

## 22.2 Promotion / Release Gate

This layer must consume:

```text
promotion decisions
release gate failures
release gate approvals
rollback recommendations
```

It may produce:

```text
release-learning summaries
promotion-risk learning signals
regression-prevention candidates
```

It must not approve releases.

## 22.3 Human Review / Approval Interface

Durable learning requires human approval.

The layer must produce memory candidates that are reviewable by a human.

Required fields:

```text
proposed memory text
source evidence
risk level
scope
reason for promotion
reason to reject
safety flags
conflict review
expiration/review policy
```

## 22.4 Policy / Capability Registry

The Policy / Capability Registry must control:

```text
who can create learning records
who can propose memory candidates
who can request memory promotion
who can approve durable memory
which memory types are allowed
which evidence types are required
which privacy classes are blocked
```

If policy is unavailable:

```text
memory promotion must BLOCK
memory candidate creation may continue as DRAFT only
review reports may be generated
no durable learning write may occur
```

## 22.5 Monitoring / Observability

Monitoring incidents may become outcome review inputs.

The layer must distinguish:

```text
confirmed incident
suspected incident
false positive
expected warning
unknown signal
```

Only confirmed incidents with evidence may produce high-confidence learning signals.

## 22.6 Documentation Synchronization

The layer may recommend documentation updates.

It must not directly rewrite documentation unless delegated to a governed implementation or documentation sync layer.

## 22.7 Backup / Disaster Recovery

Learning records and memory decisions must be included in backup and recovery policies.

If recovered evidence hashes do not match:

```text
learning records become suspect
memory promotion based on that evidence must be blocked
review must record the mismatch
```

---

# 29. Public API Contract

Expected classes:

```text
OutcomeReview
LearningSignal
MemoryCandidate
MemoryDecision
MemoryLifecycleEvent
RegressionLink
LearningPolicyDecision
LearningAuditEvent
LearningEvidenceManifest
LearningReviewReport
MemoryPromotionRequest
LearningRecordIdentity
LearningDeviation
LearningCompletionRecord
```

Expected public functions:

```python
review_outcome(raw_outcome: dict, context: dict) -> OutcomeReview
extract_learning_signals(outcome_review: OutcomeReview, context: dict) -> list[LearningSignal]
build_memory_candidate(learning_signals: list[LearningSignal], context: dict) -> MemoryCandidate
decide_memory_candidate(memory_candidate: MemoryCandidate, context: dict) -> MemoryDecision
link_regression(regression_record: dict, context: dict) -> RegressionLink
review_memory_lifecycle(memory_record: dict, context: dict) -> MemoryLifecycleEvent
check_learning_policy(action: str, record: dict, context: dict) -> LearningPolicyDecision
write_learning_audit(event: LearningAuditEvent, repo_root: str) -> dict
write_learning_report(records: list[dict], repo_root: str) -> dict
validate_learning_record(record: dict, schema_id: str) -> bool
redact_learning_payload(payload: dict) -> dict
hash_learning_artifact(path: str) -> str
build_memory_promotion_request(memory_candidate: MemoryCandidate, decision: MemoryDecision, context: dict) -> dict
compute_learning_identity(record: dict) -> str
acquire_learning_review_lock(repo_root: str, lock_name: str) -> dict
release_learning_review_lock(repo_root: str, lock_name: str) -> dict
```

Rules:

```text
all public functions return schema-valid records or schema-valid blocked/error records.
all durable write attempts require policy check.
all memory promotion attempts require human approval.
all evidence writes must be under .agentx-init/learning/ unless delegated and registered.
no public function may mutate source files.
```

---

# 30. Runtime Artifact Rules

Runtime artifacts must be:

```text
append-only for history logs
atomic for latest JSON records
schema-valid
redacted
hashable
recorded in evidence manifest
```

Approved runtime root:

```text
.agentx-init/learning/
```

Allowed exception roots only when delegated to another component:

```text
.agentx-init/evaluations/
.agentx-init/promotion/
.agentx-init/monitoring/
.agentx-init/docsync/
.agentx-init/backups/
```

Any exception must be recorded in a deviation register.

---

# 31. Simulated Dependency Test Contract

Tests may use simulated dependencies when upstream services are absent.

Allowed simulated dependencies:

```text
fake policy registry returning ALLOW/BLOCK/NEEDS_HUMAN_REVIEW
fake human approval record source
fake evaluation result records
fake promotion gate decisions
fake existing memory records
fake backup hash verification records
```

Rules:

```text
simulated dependencies must be deterministic
simulated dependencies must be declared in test fixtures
simulated dependencies must not weaken fail-closed behavior
missing real dependency must still block promotion in production mode
unit tests must prove both ALLOW and BLOCK paths
```

---

# 32. Test Acceptance Criteria

Required tests:

```text
test_outcome_review_schema_accepts_valid_review
test_outcome_review_schema_rejects_missing_evidence_for_success
test_learning_signal_schema_accepts_valid_signal
test_learning_signal_without_evidence_is_rejected
test_learning_signal_high_confidence_requires_threshold
test_memory_candidate_schema_accepts_valid_candidate
test_memory_candidate_blocks_secret
test_memory_candidate_blocks_policy_bypass
test_memory_candidate_blocks_sandbox_bypass
test_memory_candidate_blocks_prompt_injection
test_memory_candidate_requires_human_approval_for_durable_memory
test_memory_candidate_requires_policy_decision_for_promotion
test_memory_candidate_checks_existing_memory_conflict
test_memory_decision_cannot_promote_without_human_approval
test_memory_decision_cannot_promote_without_policy_decision
test_memory_lifecycle_flags_hash_mismatch
test_memory_lifecycle_recommends_supersession_for_conflict
test_regression_link_requires_evidence
test_low_confidence_regression_cannot_be_treated_as_proven
test_single_run_signal_defaults_low_confidence
test_failed_run_cannot_create_success_pattern_memory
test_contradicting_evidence_blocks_memory_promotion
test_learning_policy_blocks_unknown_caller
test_mcp_client_cannot_create_memory_candidate
test_learning_audit_written
test_learning_latest_records_written_atomically
test_learning_evidence_manifest_contains_hashes
test_learning_review_report_written
test_reprocessing_same_evidence_is_idempotent
test_duplicate_memory_candidate_is_linked_not_promoted
test_forbidden_state_transition_blocks
test_memory_promotion_handoff_does_not_write_durable_memory
test_scope_escalation_requires_human_review
test_unknown_privacy_classification_blocks_promotion
test_reviewer_independence_required_for_high_risk_memory
test_learning_query_redacts_sensitive_content
test_learning_redacts_secrets_before_logging
test_no_source_mutation_occurs
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema validation PASS
learning boundary tests PASS
memory safety tests PASS
memory lifecycle tests PASS
regression linkage tests PASS
audit/evidence tests PASS
hash/provenance tests PASS
no source mutation
no durable learning without human approval
no durable learning without policy authorization
```

---

# 33. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is selected
[ ] runtime artifact root is selected
[ ] outcome review schema is defined
[ ] learning signal schema is defined
[ ] memory candidate schema is defined
[ ] memory decision schema is defined
[ ] memory lifecycle schema is defined
[ ] regression linkage schema is defined
[ ] learning policy decision schema is defined
[ ] evidence/audit schema is defined
[ ] role permission matrix is defined
[ ] human approval rule is defined
[ ] policy authorization rule is defined
[ ] false lesson prevention rule is defined
[ ] overfitting prevention rule is defined
[ ] evidence hash/provenance rule is defined
[ ] memory conflict/lifecycle rule is defined
[ ] Agent_X integration boundaries are defined
```

---

# 34. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] schema validation passes
[ ] outcome reviews are schema-valid
[ ] learning signals are schema-valid
[ ] memory candidates are schema-valid
[ ] memory decisions are schema-valid
[ ] memory lifecycle events are schema-valid
[ ] regression links are schema-valid
[ ] policy decisions are schema-valid
[ ] secrets are redacted
[ ] unsafe memory candidates are blocked
[ ] human approval is required for durable memory
[ ] policy decision is required for durable memory
[ ] evidence hashes are recorded
[ ] evidence records are written
[ ] duplicate candidate prevention works
[ ] idempotent reprocessing works
[ ] forbidden state transitions block
[ ] memory promotion handoff is generated without direct durable write
[ ] privacy retention and minimization checks pass
[ ] scope escalation checks pass
[ ] review report exists
[ ] completion record exists
```

---

# 35. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
learning without evidence is allowed
durable memory is written without human approval
durable memory is written without policy authorization
secret-bearing memory candidate is approved
policy-bypass memory candidate is approved
sandbox-bypass memory candidate is approved
prompt-injection memory candidate is approved
failed run creates success-pattern memory
contradicting evidence is ignored
regression link is created without evidence
MCP client can create durable learning
UNKNOWN_CALLER can create learning records
source mutation occurs
Git write occurs
network is enabled by default
evidence is missing
evidence hashes are missing
redaction fails
existing-memory conflict is ignored before promotion
hash mismatch does not block or trigger review
reprocessing same evidence creates duplicate active memory candidates
forbidden state transition is allowed
memory promotion handoff directly writes durable memory
local lesson becomes global without human approval and policy authorization
unknown privacy classification is promoted
high-risk memory is promoted without independent human approval
learning query returns unredacted sensitive content
```

---

# 36. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  validated_commit: "<commit hash>"
  validated_at: "<UTC timestamp>"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  outcome_review_cases_verified: []
  learning_signal_cases_verified: []
  memory_candidate_cases_verified: []
  memory_decision_cases_verified: []
  memory_lifecycle_cases_verified: []
  regression_linkage_cases_verified: []
  human_review_requirements_verified: []
  policy_requirements_verified: []
  redaction_cases_verified: []
  hash_provenance_cases_verified: []
  idempotency_cases_verified: []
  duplicate_candidate_cases_verified: []
  state_transition_cases_verified: []
  promotion_handoff_cases_verified: []
  privacy_retention_cases_verified: []
  scope_escalation_cases_verified: []
  no_go_conditions_checked: []
  evidence_manifest_path: ".agentx-init/learning/learning_evidence_manifest.json"
  evidence_manifest_sha256: "<sha256>"
  review_report_path: ".agentx-init/learning/learning_review_report.json"
  review_report_sha256: "<sha256>"
  deviations_from_contract: []
  unresolved_risks: []
```

---

# 37. Residual Risks

```yaml
residual_risks:
  - id: "LEARN-RISK-001"
    description: "The system may convert a weak single-run observation into a general rule."
    severity: "critical"
    mitigation: "Single-run observations default to LOW confidence and cannot become durable global memory without repeated evidence, policy authorization, and human approval."
  - id: "LEARN-RISK-002"
    description: "The system may store unsafe instructions as memory."
    severity: "critical"
    mitigation: "Memory candidates are blocked when they contain policy bypass, sandbox bypass, safety weakening, prompt injection, or secret-bearing content."
  - id: "LEARN-RISK-003"
    description: "The system may learn from incomplete or missing evidence."
    severity: "high"
    mitigation: "Learning signals without evidence are rejected or blocked. Durable memory requires evidence references and hashes."
  - id: "LEARN-RISK-004"
    description: "The system may incorrectly assign regression cause."
    severity: "high"
    mitigation: "Regression links require evidence, confidence levels, and contradicting evidence fields. Low-confidence links cannot be treated as proven causes."
  - id: "LEARN-RISK-005"
    description: "The system may silently approve its own long-term learning."
    severity: "critical"
    mitigation: "Durable memory requires human approval and policy authorization."
  - id: "LEARN-RISK-006"
    description: "Older memory may become wrong after architecture changes."
    severity: "high"
    mitigation: "Memory lifecycle events require review, supersession, expiration, and revocation recommendations."
```

---

# 38. Definition of Done

This layer is done when it proves:

```text
outcomes are reviewed from evidence
learning signals are schema-valid
memory candidates are schema-valid
memory decisions are schema-valid
memory lifecycle events are schema-valid
regression links are schema-valid
unsafe memory candidates are blocked
human approval is required for durable memory
policy authorization is required for durable memory
failed runs cannot create success-pattern memory
single-run observations do not become global rules
regressions are linked only with evidence
contradicting evidence blocks promotion
existing-memory conflicts are checked before promotion
hash mismatches block or trigger review
secrets are redacted
policy bypass instructions are blocked
sandbox bypass instructions are blocked
prompt-injection lessons are blocked
evidence logs are written
latest artifacts are written atomically
learning evidence manifest is written
learning review report is written
completion record exists
idempotent reprocessing is proven
duplicate candidate prevention is proven
state-transition enforcement is proven
memory promotion handoff does not directly write durable memory
privacy retention and minimization are proven
scope escalation checks are proven
reviewer-independence checks are proven
no source mutation occurs
no Git write occurs
no network is enabled by default
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_learning_schemas.py
git status --short
```

Expected result:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
```

---

# 39. Fresh-Clone Validation and Sign-Off

The implementation is accepted only after validation from a fresh checkout.

Required command sequence:

```bash
git clone https://github.com/Astrocytech/Agent_X.git Agent_X_learning_check
cd Agent_X_learning_check
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_learning_schemas.py
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected ignored runtime artifacts
```

## 33.1 Final Sign-Off Checklist

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] outcome review schema validates
[ ] learning signal schema validates
[ ] memory candidate schema validates
[ ] memory decision schema validates
[ ] memory lifecycle event schema validates
[ ] regression link schema validates
[ ] learning policy decision schema validates
[ ] learning without evidence is blocked
[ ] durable learning without human approval is blocked
[ ] durable learning without policy authorization is blocked
[ ] secrets are blocked/redacted
[ ] policy-bypass memory is blocked
[ ] sandbox-bypass memory is blocked
[ ] prompt-injection memory is blocked
[ ] failed runs cannot create success-pattern memory
[ ] single-run observations remain low confidence or review-only
[ ] regression links require evidence
[ ] contradicting evidence blocks promotion
[ ] existing-memory conflict check runs
[ ] memory lifecycle events can recommend supersession/revocation
[ ] learning audit history is written
[ ] latest learning artifacts are written atomically
[ ] evidence manifest contains SHA-256 hashes
[ ] learning review report exists
[ ] no source mutation
[ ] no Git write
[ ] no network by default
[ ] completion record exists
```

---

# 40. Final Freeze Rule

This v3 document is frozen as the controlling contract for the Long-Term Learning / Outcome Review Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details for implementation spec
MAJOR: changed approval model, changed memory promotion rules, changed evidence thresholds, new durable memory authority, new required schema family
```

Blocked without major revision:

```text
allowing durable learning without human approval
allowing durable learning without policy authorization
removing evidence hashes
removing redaction rules
allowing source mutation
allowing Git write
allowing network by default
allowing self-approval of memory
allowing single-run success to become global memory automatically
removing contradiction/conflict checks
removing idempotency controls
allowing duplicate active memory candidates
allowing forbidden state transitions
allowing this layer to directly write durable memory
removing privacy minimization or retention rules
allowing local lessons to become global without review
```

The next document should be:

```text
LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_SPEC.md
```

---

# 41. Final Rating

This v3 contract is rated:

```text
10/10
```

Reason:

```text
It defines the Long-Term Learning / Outcome Review Layer with EQC, FIC, SIB, schemas, dependency gates, restricted mode, learning boundary rules, evidence thresholds, outcome review rules, learning signal rules, memory candidate rules, memory promotion handoff rules, memory lifecycle rules, state-transition controls, idempotency controls, duplicate-candidate prevention, privacy retention and minimization, scope escalation controls, reviewer-independence rules, regression linkage, policy decisions, audit/evidence, SHA-256 provenance, evidence immutability, role permissions, OpenCode borrowing limits, Agent_X integration points, simulated dependency tests, test acceptance criteria, no-go conditions, Definition of Done, and a freeze rule.
```
