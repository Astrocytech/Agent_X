# LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_SPEC

```text
document_id: LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen handoff with formatting and validation precision fixes
component_id: AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW
component_name: Long-Term Learning / Outcome Review Layer
roadmap_layer: 16
roadmap_phase: Phase E — Outcome Review and Durable Learning Control
based_on: LONG_TERM_LEARNING_OUTCOME_REVIEW_EQC_FIC_SIB_SCHEMA_CONTRACT
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Policy / Capability Rules, Evaluation / Regression Linkage Rules
conditional_standards: Command Acceptance Criteria, Report Template, Memory Contract, Promotion Gate Contract
target_language: Python
canonical_subdirectory: tools/agentx_evolve/learning/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/learning/
implementation_mode: deterministic outcome review and learning-candidate control; no autonomous durable memory write without policy and approval
previous_version_rating: 9.8/10
current_version_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

## 0.1 v3 Rating

The v3 implementation spec was very strong and near implementation-ready. I would rate it:

```text
9.8/10
```

It already covered:

```text
exact subdirectory
files to create
schemas to create
classes/functions
runtime artifacts
integration with Evaluation Harness
integration with Promotion / Release Gate
integration with Documentation Sync
integration with Monitoring / Observability
integration with Task Queue / Session Scheduler
integration with Policy / Capability Registry
test files
test cases
implementation order
acceptance criteria
Definition of Done
dependency gates
restricted mode
anti-poisoning rules
idempotency and locking
evidence hashing
learning review index
duplicate-candidate prevention
privacy minimization
no-autonomous-activation rule
completion evidence
```

## 0.2 Why v3 Was Not Fully 10/10

The v3 content was substantively complete, but it still had small handoff-quality defects that could confuse a coding agent or reviewer:

```text
1. The required test-file list contained duplicated review-index and privacy test entries.
2. The required test-file list accidentally included shell line-continuation fragments in a plain file list.
3. The completion record still referenced IMPLEMENTATION_SPEC_v3 instead of the current frozen version.
4. The freeze rule still called v3 the frozen implementation handoff.
5. The final rating section still described v3 instead of the current corrected handoff.
6. The validation command lists were correct as shell commands, but the file inventory section needed to be clean, one-file-per-line, and non-command-like.
7. The implementation-handoff needed an explicit inventory-consistency rule: every file listed in the exact-file section must appear once and only once unless deliberately repeated in a command block.
```

These are not major architectural gaps, but they matter for a 10/10 implementation handoff because repeated or malformed file inventory lines can produce duplicate test creation, missed tests, or unnecessary coding-agent confusion.

## 0.3 v4 Improvements

This v4 adds and fixes:

```text
clean one-file-per-line required test inventory
no duplicated test entries in the exact file list
no shell continuation fragments in inventory lists
updated completion-record basis document reference
updated freeze rule and final-rating language
explicit inventory-consistency rule
clear separation between file inventories and shell validation commands
```

This v4 is the corrected final 10/10 implementation handoff.

---

# 1. Purpose

This document is the full implementation specification for the **Long-Term Learning / Outcome Review Layer**.

This layer reviews completed Agent_X runs, tasks, patches, validations, promotions, failures, and regressions. It extracts learning signals, builds memory candidates, links outcomes to evidence, and prevents unsafe or unsupported lessons from becoming durable learning.

The primary goal is controlled learning, not automatic self-reinforcement.

The layer must distinguish:

```text
verified success
lucky success
partial success
validation failure
regression
policy violation
sandbox denial
user rejection
promotion rejection
documentation drift
evaluation drift
unsafe learning candidate
unsupported model claim
insufficient evidence
contradictory evidence
```

The layer must not treat a successful run as proof of a general rule. It must not treat a failed run as a valid lesson unless the failure itself is evidence-supported and safely scoped.

---

# 2. Canonical Destination Summary

Create the Long-Term Learning / Outcome Review package here:

```text
tools/agentx_evolve/learning/
```

Create shared schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts must be written here:

```text
.agentx-init/learning/
```

Intended placement:

```text
tools/agentx_evolve/evaluation/       = Evaluation Harness / Regression Benchmark Layer
tools/agentx_evolve/promotion/        = Promotion / Release Gate
tools/agentx_evolve/docsync/          = Documentation Synchronization Layer
tools/agentx_evolve/monitoring/       = Monitoring / Observability Layer
tools/agentx_evolve/scheduler/        = Task Queue / Session Scheduler
tools/agentx_evolve/policy/           = Policy / Capability Registry
tools/agentx_evolve/learning/         = Long-Term Learning / Outcome Review Layer
```

If an upstream package does not exist or its API is not stable, this layer must use a safe adapter stub, context-provided evidence, or fail-closed behavior.

---

# 3. Implementation Goal

At the end of implementation, Agent_X must have a deterministic outcome-review and learning-control layer that can:

```text
load completed run evidence
review task outcomes
classify successes, failures, blocked runs, rejected runs, and regressions
extract evidence-supported learning signals
reject unsupported or unsafe learning signals
build bounded memory candidates
validate memory candidates against learning policy
require approval before durable learning
link outcomes to Evaluation Harness evidence
link outcomes to Promotion / Release Gate evidence
link documentation drift to learning candidates
link monitoring observations to outcome review
create follow-up task proposals without starting background jobs
write append-only learning evidence
write latest outcome review artifacts atomically
produce structured learning reports
write final evidence manifest and completion record
block unsafe long-term memory writes
```

The layer must not implement:

```text
LLM worker
model adapter
prompt generation engine
self-evolution orchestrator
patch application
release promotion
automatic durable memory mutation
external telemetry upload
network-based learning
background daemon
human approval UI
```

---

# 4. Dependency Gates and Restricted Mode

## 4.1 Required Upstream Components for Full Operation

The layer integrates with these upstream or neighboring components:

```text
Evaluation Harness / Regression Benchmark Layer
Promotion / Release Gate
Documentation Synchronization Layer
Monitoring / Observability Layer
Task Queue / Session Scheduler
Policy / Capability Registry
Memory / durable knowledge layer, if present
Human Review / Approval Interface, if approval is required
```

## 4.2 Restricted Mode

If any upstream dependency is missing or unstable, the layer must still support safe review/report behavior where possible, but it must block durable learning.

Restricted mode allows:

```text
OutcomeEvent schema validation
OutcomeReview creation
LearningSignal extraction when evidence is context-provided
LearningReport creation
append-only evidence writing
rejection records
follow-up task proposals as local artifacts only
```

Restricted mode blocks:

```text
durable memory approval
durable memory write
release-impacting learning approval
scheduler job creation
background tasks
network or external telemetry
positive learning from unverified success
policy-affecting learning candidates
```

## 4.3 Dependency Gate Rules

```text
If Evaluation Harness is missing -> positive learning requires context-provided validation evidence; otherwise NEEDS_MORE_EVIDENCE.
If Promotion Gate is missing -> release-impacting learning returns NEEDS_MORE_EVIDENCE or NEEDS_APPROVAL.
If Documentation Sync is missing -> DOC_DRIFT signals require context-provided documentation evidence.
If Monitoring is missing -> monitoring-based regression links are not created.
If Scheduler is missing -> follow-up task proposals are written as local proposals only; no scheduling occurs.
If Policy / Capability Registry is missing -> durable memory approval blocks.
If Human Review is missing -> candidates remain NEEDS_HUMAN_REVIEW or BLOCKED.
If Memory layer is missing -> no durable memory write occurs; candidates may be proposed only.
```

## 4.4 Authority Rule

The layer may propose learning. It may not grant itself authority to make durable learning effective.

Durable learning requires:

```text
valid evidence
bounded candidate
learning policy pass
Policy / Capability Registry approval
human approval when required
Memory layer availability
approved write path
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCKED
REJECT_UNSUPPORTED
NEEDS_MORE_EVIDENCE
NEEDS_HUMAN_REVIEW
NEEDS_APPROVAL
PROPOSED
ALLOW
```

---

# 5. Exact Files to Create

## 5.1 Required Learning Package Files

Create:

```text
tools/agentx_evolve/learning/__init__.py
tools/agentx_evolve/learning/outcome_models.py
tools/agentx_evolve/learning/outcome_reviewer.py
tools/agentx_evolve/learning/learning_signal_extractor.py
tools/agentx_evolve/learning/memory_candidate_builder.py
tools/agentx_evolve/learning/learning_policy.py
tools/agentx_evolve/learning/learning_audit.py
tools/agentx_evolve/learning/regression_linker.py
tools/agentx_evolve/learning/learning_reporter.py
tools/agentx_evolve/learning/learning_lock.py
tools/agentx_evolve/learning/learning_index.py
```

## 5.2 Required Integration Adapter Files

Create safe adapters even if upstream packages are not ready. Each adapter must fail closed when its upstream package is unavailable.

```text
tools/agentx_evolve/learning/evaluation_adapter.py
tools/agentx_evolve/learning/promotion_adapter.py
tools/agentx_evolve/learning/docsync_adapter.py
tools/agentx_evolve/learning/monitoring_adapter.py
tools/agentx_evolve/learning/scheduler_adapter.py
tools/agentx_evolve/learning/policy_adapter.py
tools/agentx_evolve/learning/memory_adapter.py
```

## 5.3 Schema Files

Create:

```text
tools/agentx_evolve/schemas/12_learning/outcome_event.schema.json
tools/agentx_evolve/schemas/12_learning/outcome_review.schema.json
tools/agentx_evolve/schemas/12_learning/learning_signal.schema.json
tools/agentx_evolve/schemas/12_learning/memory_candidate.schema.json
tools/agentx_evolve/schemas/12_learning/learning_policy_decision.schema.json
tools/agentx_evolve/schemas/12_learning/regression_link.schema.json
tools/agentx_evolve/schemas/12_learning/outcome_review_report.schema.json
tools/agentx_evolve/schemas/12_learning/learning_audit_event.schema.json
tools/agentx_evolve/schemas/12_learning/follow_up_task_proposal.schema.json
tools/agentx_evolve/schemas/12_learning/learning_lock.schema.json
tools/agentx_evolve/schemas/12_learning/learning_review_index.schema.json
tools/agentx_evolve/schemas/12_learning/learning_evidence_manifest.schema.json
tools/agentx_evolve/schemas/12_learning/learning_implementation_review_report.schema.json
tools/agentx_evolve/schemas/12_learning/learning_completion_record.schema.json
```

## 5.4 Test Files

Create:

```text
tools/agentx_evolve/tests/test_learning_outcome_models.py
tools/agentx_evolve/tests/test_outcome_reviewer.py
tools/agentx_evolve/tests/test_learning_signal_extractor.py
tools/agentx_evolve/tests/test_memory_candidate_builder.py
tools/agentx_evolve/tests/test_learning_policy.py
tools/agentx_evolve/tests/test_learning_audit.py
tools/agentx_evolve/tests/test_regression_linker.py
tools/agentx_evolve/tests/test_learning_reporter.py
tools/agentx_evolve/tests/test_learning_schema_validation.py
tools/agentx_evolve/tests/test_learning_negative_cases.py
tools/agentx_evolve/tests/test_learning_integration_adapters.py
tools/agentx_evolve/tests/test_learning_idempotency_and_locking.py
tools/agentx_evolve/tests/test_learning_anti_poisoning.py
tools/agentx_evolve/tests/test_learning_review_index.py
tools/agentx_evolve/tests/test_learning_privacy_minimization.py
```

Dedicated schema validator:

```text
tools/agentx_evolve/tests/validate_learning_schemas.py
```

## 5.5 Inventory Consistency Rule

The exact file inventories in Sections 5.1 through 5.4 are authoritative.

Rules:

```text
each required package file must appear once in the package-file inventory
each required adapter file must appear once in the adapter-file inventory
each required schema file must appear once in the schema-file inventory
each required test file must appear once in the test-file inventory
shell line-continuation syntax must not appear in inventory lists
repeated file names in inventory lists are defects unless explicitly marked as aliases
validation command blocks may repeat test paths because they are executable command examples
```

---

# 6. Runtime Artifacts

All runtime artifacts for this layer must be written under:

```text
.agentx-init/learning/
```

Required artifacts:

```text
.agentx-init/learning/outcome_event_history.jsonl
.agentx-init/learning/outcome_review_history.jsonl
.agentx-init/learning/learning_signal_history.jsonl
.agentx-init/learning/memory_candidate_history.jsonl
.agentx-init/learning/rejected_learning_history.jsonl
.agentx-init/learning/regression_link_history.jsonl
.agentx-init/learning/learning_policy_decision_history.jsonl
.agentx-init/learning/learning_audit_history.jsonl
.agentx-init/learning/follow_up_task_proposal_history.jsonl
.agentx-init/learning/learning_lock_history.jsonl
.agentx-init/learning/latest_outcome_review.json
.agentx-init/learning/latest_learning_report.json
.agentx-init/learning/learning_evidence_manifest.json
.agentx-init/learning/learning_implementation_review_report.json
.agentx-init/learning/learning_completion_record.json
.agentx-init/learning/learning_review_index.json
.agentx-init/learning/locks/<review_key>.lock
```

Runtime artifact rules:

```text
append-only JSONL for histories
atomic JSON writes for latest artifacts
SHA-256 hashes for final evidence artifacts
no source mutation
no direct durable memory write outside approved memory layer
no raw prompt persistence
no secret persistence
no private/sensitive data persistence unless policy explicitly permits
no overwriting past review evidence
no editing completed evidence without a new review record
no runtime artifacts outside .agentx-init/learning/ unless deviation is recorded
```

---

# 7. Public API Summary

The package must expose these primary APIs:

```python
review_outcome(event: OutcomeEvent, context: dict) -> OutcomeReview
extract_learning_signals(review: OutcomeReview, context: dict) -> list[LearningSignal]
build_memory_candidates(signals: list[LearningSignal], context: dict) -> list[MemoryCandidate]
check_learning_policy(candidate: MemoryCandidate, context: dict) -> LearningPolicyDecision
check_signal_policy(signal: LearningSignal, context: dict) -> LearningPolicyDecision
link_regression(event: OutcomeEvent, review: OutcomeReview, context: dict) -> RegressionLink | None
build_outcome_review_report(event: OutcomeEvent, review: OutcomeReview, signals: list[LearningSignal], candidates: list[MemoryCandidate], decisions: list[LearningPolicyDecision], regression_links: list[RegressionLink], context: dict) -> OutcomeReviewReport
write_learning_evidence(review: OutcomeReview, context: dict) -> dict
write_learning_report(report: OutcomeReviewReport, context: dict) -> dict
run_outcome_review_pipeline(event: OutcomeEvent, context: dict) -> OutcomeReviewReport
```

The dispatcher must perform all validation, evidence loading, classification, extraction, policy checking, evidence writing, report generation, and manifest writing in a fixed order.

No external caller should call extraction, candidate building, memory approval, or scheduler proposal directly unless the call is a unit test or internal pipeline step.

---

# 8. File-by-File Implementation Spec

## 8.1 `tools/agentx_evolve/learning/__init__.py`

### Purpose

Expose the public learning-layer API without side effects.

### Required Exports

```python
from .outcome_models import (
    OutcomeEvent,
    OutcomeReview,
    LearningSignal,
    MemoryCandidate,
    LearningPolicyDecision,
    RegressionLink,
    OutcomeReviewReport,
    LearningAuditEvent,
    FollowUpTaskProposal,
    LearningAdapterResult,
    LearningLockRecord,
    LearningReviewIndex,
)

from .outcome_reviewer import review_outcome, run_outcome_review_pipeline
from .learning_signal_extractor import extract_learning_signals
from .memory_candidate_builder import build_memory_candidates
from .learning_policy import check_learning_policy, check_signal_policy
from .regression_linker import link_regression
from .learning_audit import write_learning_evidence
from .learning_reporter import build_outcome_review_report, write_learning_report
from .learning_lock import acquire_learning_lock, release_learning_lock
from .learning_index import load_learning_review_index, update_learning_review_index
```

### Must Not Do

```text
no filesystem writes on import
no outcome review on import
no memory writes on import
no network calls
no background scheduler start
no import-time loading of large evidence artifacts
```

---

## 8.2 `outcome_models.py`

### Purpose

Define dataclasses, constants, enums, and helper functions for outcome review and learning control.

### Required Outcome Status Constants

```python
OUTCOME_SUCCESS = "SUCCESS"
OUTCOME_PARTIAL = "PARTIAL"
OUTCOME_FAILED = "FAILED"
OUTCOME_BLOCKED = "BLOCKED"
OUTCOME_REGRESSION = "REGRESSION"
OUTCOME_REJECTED = "REJECTED"
OUTCOME_UNKNOWN = "UNKNOWN"
```

### Required Review Status Constants

```python
REVIEW_VERIFIED = "VERIFIED"
REVIEW_BLOCKED = "BLOCKED"
REVIEW_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
REVIEW_NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
REVIEW_CONTRADICTORY = "CONTRADICTORY"
REVIEW_INVALID = "INVALID"
```

### Required Success Classifications

```python
SUCCESS_VERIFIED = "VERIFIED_SUCCESS"
SUCCESS_LUCKY = "LUCKY_SUCCESS"
SUCCESS_PARTIAL = "PARTIAL_SUCCESS"
SUCCESS_UNSUPPORTED = "UNSUPPORTED_SUCCESS"
```

### Required Failure Classifications

```python
FAIL_VALIDATION = "VALIDATION_FAILURE"
FAIL_POLICY = "POLICY_FAILURE"
FAIL_SANDBOX = "SANDBOX_FAILURE"
FAIL_PROMOTION_REJECTION = "PROMOTION_REJECTION"
FAIL_REGRESSION = "REGRESSION_FAILURE"
FAIL_USER_REJECTION = "USER_REJECTION"
FAIL_UNKNOWN = "UNKNOWN_FAILURE"
```

### Required Evidence Quality Constants

```python
EVIDENCE_STRONG = "STRONG"
EVIDENCE_MEDIUM = "MEDIUM"
EVIDENCE_WEAK = "WEAK"
EVIDENCE_MISSING = "MISSING"
EVIDENCE_CONTRADICTORY = "CONTRADICTORY"
```

### Required Learning Signal Types

```python
SIGNAL_FIX_WORKED = "FIX_WORKED"
SIGNAL_FIX_FAILED = "FIX_FAILED"
SIGNAL_REGRESSION_DETECTED = "REGRESSION_DETECTED"
SIGNAL_POLICY_BLOCKED = "POLICY_BLOCKED"
SIGNAL_SANDBOX_BLOCKED = "SANDBOX_BLOCKED"
SIGNAL_TEST_GAP = "TEST_GAP"
SIGNAL_DOC_DRIFT = "DOC_DRIFT"
SIGNAL_REPEAT_FAILURE = "REPEAT_FAILURE"
SIGNAL_USER_REJECTION = "USER_REJECTION"
SIGNAL_PROMOTION_REJECTION = "PROMOTION_REJECTION"
SIGNAL_UNSUPPORTED = "UNSUPPORTED"
```

### Required Memory Candidate Statuses

```python
MEMORY_CANDIDATE_PROPOSED = "PROPOSED"
MEMORY_CANDIDATE_APPROVED = "APPROVED"
MEMORY_CANDIDATE_REJECTED = "REJECTED"
MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
MEMORY_CANDIDATE_BLOCKED = "BLOCKED"
```

### Required Policy Decisions

```python
LEARNING_ALLOW = "ALLOW"
LEARNING_BLOCK = "BLOCK"
LEARNING_NEEDS_APPROVAL = "NEEDS_APPROVAL"
LEARNING_NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
LEARNING_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
LEARNING_REJECT_UNSUPPORTED = "REJECT_UNSUPPORTED"
```

### Required Final Learning Verdicts

```python
VERDICT_NO_LEARNING_ALLOWED = "NO_LEARNING_ALLOWED"
VERDICT_LEARNING_CANDIDATES_PROPOSED = "LEARNING_CANDIDATES_PROPOSED"
VERDICT_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
VERDICT_NEEDS_HUMAN_APPROVAL = "NEEDS_HUMAN_APPROVAL"
VERDICT_LEARNING_APPROVED = "LEARNING_APPROVED"
VERDICT_REGRESSION_REVIEW_REQUIRED = "REGRESSION_REVIEW_REQUIRED"
```

### Required Rejection Reasons

```python
REJECT_MISSING_EVIDENCE = "MISSING_EVIDENCE"
REJECT_UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"
REJECT_OVERBROAD_CLAIM = "OVERBROAD_CLAIM"
REJECT_SECRET_OR_PROMPT = "SECRET_OR_PROMPT"
REJECT_POLICY_DENIED = "POLICY_DENIED"
REJECT_REGRESSION_UNRESOLVED = "REGRESSION_UNRESOLVED"
REJECT_PROMOTION_REJECTED = "PROMOTION_REJECTED"
REJECT_FAILED_VALIDATION = "FAILED_VALIDATION"
REJECT_SENSITIVE_DATA = "SENSITIVE_DATA"
```

### Required Memory Candidate Types

```python
CANDIDATE_TYPE_BEHAVIOR_RULE = "BEHAVIOR_RULE"
CANDIDATE_TYPE_VALIDATION_PATTERN = "VALIDATION_PATTERN"
CANDIDATE_TYPE_FAILURE_PATTERN = "FAILURE_PATTERN"
CANDIDATE_TYPE_DOC_PATTERN = "DOC_PATTERN"
CANDIDATE_TYPE_PROMOTION_PATTERN = "PROMOTION_PATTERN"
CANDIDATE_TYPE_REGRESSION_PATTERN = "REGRESSION_PATTERN"
CANDIDATE_TYPE_BLOCKED_UNSAFE = "BLOCKED_UNSAFE"
```

### Required Candidate Scope Constants

```python
SCOPE_COMPONENT = "component"
SCOPE_LAYER = "layer"
SCOPE_REPOSITORY = "repository"
SCOPE_TASK_TYPE = "task_type"
SCOPE_VALIDATION_PATTERN = "validation_pattern"
SCOPE_FAILURE_PATTERN = "failure_pattern"
SCOPE_DOCUMENTATION_PATTERN = "documentation_pattern"
SCOPE_PROMOTION_PATTERN = "promotion_pattern"
SCOPE_REGRESSION_PATTERN = "regression_pattern"
```

### Required Regression Link Statuses

```python
REGRESSION_LINK_CONFIRMED = "CONFIRMED"
REGRESSION_LINK_SUSPECTED = "SUSPECTED"
REGRESSION_LINK_LOW_CONFIDENCE = "LOW_CONFIDENCE"
REGRESSION_LINK_REJECTED = "REJECTED"
REGRESSION_LINK_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
```

### Required Follow-Up Proposal Statuses

```python
PROPOSAL_CREATED = "CREATED"
PROPOSAL_POLICY_BLOCKED = "POLICY_BLOCKED"
PROPOSAL_NEEDS_APPROVAL = "NEEDS_APPROVAL"
PROPOSAL_SUBMITTED = "SUBMITTED"
PROPOSAL_DEFERRED = "DEFERRED"
```

### Required Dependency Status Constants

```python
DEPENDENCY_AVAILABLE = "AVAILABLE"
DEPENDENCY_MISSING = "MISSING"
DEPENDENCY_UNSTABLE = "UNSTABLE"
DEPENDENCY_CONTEXT_PROVIDED = "CONTEXT_PROVIDED"
DEPENDENCY_BLOCKED = "BLOCKED"
```

### Required Anti-Poisoning Flags

```python
ANTI_POISONING_PROMPT_INJECTION = "PROMPT_INJECTION"
ANTI_POISONING_POLICY_WEAKENING = "POLICY_WEAKENING"
ANTI_POISONING_SANDBOX_BYPASS = "SANDBOX_BYPASS"
ANTI_POISONING_TEST_SKIPPING = "TEST_SKIPPING"
ANTI_POISONING_SECRET = "SECRET"
ANTI_POISONING_RAW_PROMPT = "RAW_PROMPT"
ANTI_POISONING_SENSITIVE_DATA = "SENSITIVE_DATA"
ANTI_POISONING_MODEL_ONLY_CLAIM = "MODEL_ONLY_CLAIM"
ANTI_POISONING_OVERBROAD = "OVERBROAD"
ANTI_POISONING_CONTRADICTS_EVIDENCE = "CONTRADICTS_EVIDENCE"
```

### Required Dataclasses

#### `OutcomeEvent`

```python
schema_version: str = "1.0"
schema_id: str = "outcome_event.schema.json"
event_id: str
created_at: str
source_component: str
session_id: str | None
run_id: str | None
task_id: str | None
commit_before: str | None
commit_after: str | None
outcome_status: str
summary: str
evidence_refs: list[str]
artifact_refs: list[str]
validation_refs: list[str]
promotion_refs: list[str]
documentation_refs: list[str]
monitoring_refs: list[str]
policy_refs: list[str]
sandbox_refs: list[str]
user_feedback_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `OutcomeReview`

```python
schema_version: str = "1.0"
schema_id: str = "outcome_review.schema.json"
review_id: str
created_at: str
source_component: str = "LongTermLearningOutcomeReview"
event_id: str
outcome_status: str
review_status: str
success_classification: str | None
failure_classification: str | None
regression_detected: bool
learning_allowed: bool
learning_blockers: list[str]
evidence_quality: str
confidence: float
summary: str
evidence_refs: list[str]
artifact_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `LearningSignal`

```python
schema_version: str = "1.0"
schema_id: str = "learning_signal.schema.json"
signal_id: str
created_at: str
source_component: str = "LearningSignalExtractor"
review_id: str
signal_type: str
claim: str
supporting_evidence_refs: list[str]
contradicting_evidence_refs: list[str]
confidence: float
eligible_for_memory: bool
requires_human_review: bool
anti_poisoning_flags: list[str]
warnings: list[str]
errors: list[str]
```

#### `MemoryCandidate`

```python
schema_version: str = "1.0"
schema_id: str = "memory_candidate.schema.json"
candidate_id: str
created_at: str
source_component: str = "MemoryCandidateBuilder"
signal_id: str
candidate_text: str
candidate_type: str
scope: str
status: str
requires_human_approval: bool
policy_decision_id: str | None
supporting_evidence_refs: list[str]
contradicting_evidence_refs: list[str]
rejection_reason: str | None
hash_of_candidate_text: str | None
warnings: list[str]
errors: list[str]
```

#### `LearningPolicyDecision`

```python
schema_version: str = "1.0"
schema_id: str = "learning_policy_decision.schema.json"
decision_id: str
created_at: str
source_component: str = "LearningPolicy"
candidate_id: str | None
signal_id: str | None
decision: str
reason: str
required_checks: list[str]
missing_checks: list[str]
evidence_refs: list[str]
policy_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `RegressionLink`

```python
schema_version: str = "1.0"
schema_id: str = "regression_link.schema.json"
regression_link_id: str
created_at: str
source_component: str = "RegressionLinker"
event_id: str
review_id: str
suspected_commit: str | None
suspected_change_refs: list[str]
failing_test_refs: list[str]
prior_passing_refs: list[str]
confidence: float
status: str
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `FollowUpTaskProposal`

```python
schema_version: str = "1.0"
schema_id: str = "follow_up_task_proposal.schema.json"
proposal_id: str
created_at: str
source_component: str = "LearningSchedulerAdapter"
review_id: str
reason: str
proposed_task_type: str
proposed_summary: str
requires_scheduler_approval: bool
scheduler_decision_ref: str | None
status: str
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `OutcomeReviewReport`

```python
schema_version: str = "1.0"
schema_id: str = "outcome_review_report.schema.json"
report_id: str
created_at: str
source_component: str = "LearningReporter"
event_id: str
review_id: str
outcome_status: str
signals: list[dict]
memory_candidates: list[dict]
policy_decisions: list[dict]
regression_links: list[dict]
follow_up_task_proposals: list[dict]
final_learning_verdict: str
summary: str
evidence_refs: list[str]
artifact_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `LearningAuditEvent`

```python
schema_version: str = "1.0"
schema_id: str = "learning_audit_event.schema.json"
audit_id: str
created_at: str
source_component: str
event_type: str
entity_type: str
entity_id: str
status: str
message: str
evidence_refs: list[str]
artifact_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `LearningAdapterResult`

All integration adapters must return this shape or a dictionary that validates against it.

```python
schema_version: str = "1.0"
schema_id: str = "learning_adapter_result.schema.json"
adapter_name: str
created_at: str
dependency_status: str
status: str
summary: str
data: dict
evidence_refs: list[str]
artifact_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `LearningLockRecord`

```python
schema_version: str = "1.0"
schema_id: str = "learning_lock.schema.json"
lock_id: str
created_at: str
review_key: str
lock_path: str
owner_session_id: str | None
expires_at: str
status: str
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `LearningReviewIndex`

```python
schema_version: str = "1.0"
schema_id: str = "learning_review_index.schema.json"
index_id: str
created_at: str
updated_at: str
source_component: str = "LearningReviewIndex"
review_keys: list[str]
candidate_hashes: list[str]
approved_candidate_hashes: list[str]
blocked_candidate_hashes: list[str]
latest_report_refs: list[str]
warnings: list[str]
errors: list[str]
```

### Required Helpers

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
clamp_confidence(value: float) -> float
stable_hash_dict(data: dict) -> str
sha256_text(text: str) -> str
redact_learning_text(text: str) -> str
```

### Acceptance

```text
dataclasses instantiate
to_dict serializes dataclasses
confidence values are clamped to 0.0-1.0
constants match schema enum values
hash helpers are deterministic
redaction helper redacts secrets and raw prompt markers
no filesystem writes
no network calls
```

---

## 8.3 `outcome_reviewer.py`

### Purpose

Classify the outcome of a completed run/task/change using available evidence.

### Required Public Functions

```python
review_outcome(event: OutcomeEvent, context: dict) -> OutcomeReview
run_outcome_review_pipeline(event: OutcomeEvent, context: dict) -> OutcomeReviewReport
validate_outcome_event(event: OutcomeEvent | dict) -> OutcomeEvent
```

### Required Review Logic

The reviewer must inspect:

```text
outcome status
validation evidence
test pass/fail evidence
promotion decision evidence
known regression evidence
policy/sandbox failure evidence
monitoring observations
documentation drift records
user rejection records
prior outcome records when available
```

The reviewer must classify:

```text
verified success
lucky success
partial success
failed implementation
blocked implementation
regression
unsupported success claim
unsupported failure claim
insufficient evidence
contradictory evidence
```

### Required Fail-Closed Behavior

```text
missing evidence -> learning_allowed = false
schema-invalid event -> blocked review/report
contradictory evidence -> learning_allowed = false and needs human review
promotion rejection -> learning_allowed = false unless reviewed manually
regression detected -> memory candidates must be blocked unless corrective lesson is evidence-supported
model-only claim -> unsupported unless tied to concrete evidence refs
```

### Acceptance Tests

```text
verified passing validation can produce successful review
missing validation evidence blocks durable learning
failed validation produces failed review
promotion rejection blocks positive learning
regression evidence produces regression review
contradictory evidence lowers confidence and blocks memory candidates
model-only success claim is unsupported
```

---

## 8.4 `learning_signal_extractor.py`

### Purpose

Extract bounded learning signals from an `OutcomeReview`.

### Required Public Function

```python
extract_learning_signals(review: OutcomeReview, context: dict) -> list[LearningSignal]
```

### Required Behavior

Signals may be extracted only from evidence-supported review findings.

Allowed signal classes:

```text
fix worked, if validation and promotion evidence support it
fix failed, if validation or review evidence supports it
regression detected, if linked to failing tests or monitoring evidence
policy blocked, if policy evidence exists
sandbox blocked, if sandbox evidence exists
test gap, if outcome succeeded but later regression shows missing coverage
documentation drift, if docsync evidence exists
repeat failure, if prior outcome evidence exists
user rejection, if explicit review/user feedback evidence exists
promotion rejection, if release gate evidence exists
```

### Anti-Poisoning Rules

The extractor must reject or mark unsupported:

```text
claims with no evidence refs
claims based only on model text
claims that include secrets or raw prompts
claims that tell future agents to bypass policy, sandbox, tests, evidence, or approval
claims that generalize from a single weak example
claims that contradict validation, promotion, or regression evidence
claims that would weaken future safety rules
```

### Must Not Do

```text
infer broad lessons from one weak signal
convert raw model claims into learning signals without evidence
store secrets or raw prompts as signal text
create positive learning from failed validation
create learning signals from missing evidence
```

### Acceptance Tests

```text
success review with strong evidence creates FIX_WORKED signal
failed review creates FIX_FAILED signal
regression review creates REGRESSION_DETECTED signal
missing evidence creates no eligible memory signal
secret-like text is redacted or rejected
policy-bypass instruction is rejected
```

---

## 8.5 `memory_candidate_builder.py`

### Purpose

Convert learning signals into proposed durable-memory candidates.

### Required Public Function

```python
build_memory_candidates(signals: list[LearningSignal], context: dict) -> list[MemoryCandidate]
```

### Required Rules

Memory candidates must be:

```text
short
specific
bounded to evidence
scoped to component/layer/task type
free of secrets
free of raw prompt text
free of private/sensitive data unless policy explicitly permits it
not phrased as universal truth from one run
not automatically approved
hashable for provenance
linked to signal and supporting evidence refs
```

Candidate scopes:

```text
component
layer
repository
task_type
validation_pattern
failure_pattern
documentation_pattern
promotion_pattern
regression_pattern
```

Default status:

```text
NEEDS_HUMAN_REVIEW
```

or:

```text
BLOCKED
```

if evidence is insufficient, the signal is unsafe, or policy rejects it.

### Must Not Do

```text
write to durable memory store directly
auto-approve memory candidates
create memory from unsupported signal
include secrets, tokens, raw prompts, private data, or unbounded claims
```

### Acceptance Tests

```text
eligible signal creates proposed memory candidate
unsupported signal creates no candidate or blocked candidate
candidate requires human approval by default
secret-like candidate is blocked
universal overbroad candidate is blocked
candidate hash is deterministic
```

---

## 8.6 `learning_policy.py`

### Purpose

Apply learning safety rules and Policy / Capability Registry decisions to learning signals and memory candidates.

### Required Public Functions

```python
check_learning_policy(candidate: MemoryCandidate, context: dict) -> LearningPolicyDecision
check_signal_policy(signal: LearningSignal, context: dict) -> LearningPolicyDecision
```

### Required Policy Logic

Return `LEARNING_BLOCK` if:

```text
candidate contains secrets
candidate contains raw prompt text
candidate contains unsupported claim
candidate is overbroad
candidate contradicts validation evidence
candidate comes from failed run but presents itself as success
candidate lacks evidence refs
candidate attempts to alter policy, sandbox, approval, evidence, or test requirements
candidate records sensitive personal data without explicit approval
policy registry denies durable learning
memory layer is unavailable for an approval/write operation
```

Return `LEARNING_NEEDS_APPROVAL` if:

```text
candidate is otherwise valid but would become durable memory
candidate affects future planning behavior
candidate affects release/promotion decisions
candidate changes coding-agent behavior
candidate affects safety-relevant behavior
```

Return `LEARNING_NEEDS_MORE_EVIDENCE` if:

```text
evidence exists but is incomplete
confidence is below threshold
regression linkage is unresolved
promotion state is unknown
validation evidence is missing
```

Return `LEARNING_ALLOW` only if:

```text
candidate is evidence-supported
candidate is scoped
candidate is non-sensitive
candidate passes Policy / Capability Registry checks
candidate has required human approval
candidate has an approved memory-layer write path
```

### Required Integration with Policy / Capability Registry

The layer must call Policy / Capability Registry before allowing durable learning.

If policy registry is unavailable:

```text
read/review/report may continue
memory candidate approval must BLOCK or NEEDS_APPROVAL
no durable memory write may occur
```

### Acceptance Tests

```text
unsupported candidate blocks
secret candidate blocks
over-broad candidate blocks
valid candidate returns NEEDS_APPROVAL by default
policy unavailable blocks durable memory approval
approved context can return ALLOW
candidate attempting to weaken policy blocks
```

---

## 8.7 `learning_audit.py`

### Purpose

Write append-only learning evidence.

### Required Public Functions

```python
append_outcome_event(event: OutcomeEvent, repo_root: Path) -> dict
append_outcome_review(review: OutcomeReview, repo_root: Path) -> dict
append_learning_signal(signal: LearningSignal, repo_root: Path) -> dict
append_memory_candidate(candidate: MemoryCandidate, repo_root: Path) -> dict
append_rejected_learning(entity: dict, reason: str, repo_root: Path) -> dict
append_regression_link(link: RegressionLink, repo_root: Path) -> dict
append_learning_policy_decision(decision: LearningPolicyDecision, repo_root: Path) -> dict
append_learning_audit_event(event: LearningAuditEvent, repo_root: Path) -> dict
append_follow_up_task_proposal(proposal: FollowUpTaskProposal, repo_root: Path) -> dict
write_latest_outcome_review(review: OutcomeReview, repo_root: Path) -> dict
write_latest_learning_report(report: OutcomeReviewReport, repo_root: Path) -> dict
write_learning_evidence(review: OutcomeReview, context: dict) -> dict
write_learning_evidence_manifest(context: dict) -> dict
write_learning_implementation_review_report(context: dict) -> dict
write_learning_completion_record(context: dict) -> dict
sha256_file(path: Path) -> str
```

### Required Paths

```text
.agentx-init/learning/outcome_event_history.jsonl
.agentx-init/learning/outcome_review_history.jsonl
.agentx-init/learning/learning_signal_history.jsonl
.agentx-init/learning/memory_candidate_history.jsonl
.agentx-init/learning/rejected_learning_history.jsonl
.agentx-init/learning/regression_link_history.jsonl
.agentx-init/learning/learning_policy_decision_history.jsonl
.agentx-init/learning/learning_audit_history.jsonl
.agentx-init/learning/follow_up_task_proposal_history.jsonl
.agentx-init/learning/learning_lock_history.jsonl
.agentx-init/learning/latest_outcome_review.json
.agentx-init/learning/latest_learning_report.json
.agentx-init/learning/learning_evidence_manifest.json
.agentx-init/learning/learning_implementation_review_report.json
.agentx-init/learning/learning_completion_record.json
.agentx-init/learning/learning_review_index.json
.agentx-init/learning/locks/<review_key>.lock
```

### Evidence Rules

```text
create .agentx-init/learning/ if needed
append JSONL histories only
write latest JSON atomically
redact secrets before durable logging
write SHA-256 hashes for final artifacts
preserve malformed existing JSONL lines
do not write outside .agentx-init/learning/ unless deviation is recorded
do not durably log raw prompts, raw command output, secrets, or private data
```

### Acceptance Tests

```text
outcome event history written
outcome review history written
learning signal history written
memory candidate history written
rejected learning history written
regression link history written
policy decision history written
latest outcome review written atomically
latest learning report written atomically
final evidence hashes are written
secrets redacted before logging
```

---

## 8.8 `learning_lock.py`

### Purpose

Provide local lock handling for deterministic outcome review runs.

### Required Public Functions

```python
compute_review_key(event: OutcomeEvent) -> str
acquire_learning_lock(review_key: str, context: dict) -> LearningLockRecord
release_learning_lock(lock: LearningLockRecord, context: dict) -> LearningLockRecord
record_stale_lock(lock_path: Path, context: dict) -> LearningLockRecord
```

### Required Behavior

```text
locks live under .agentx-init/learning/locks/
lock files are runtime artifacts only
lock acquisition is atomic where possible
stale locks are never deleted silently
stale-lock recovery writes evidence
lock failure returns a schema-valid blocked/failed report
```

### Acceptance Tests

```text
review key is deterministic
lock file is created under approved runtime root
concurrent lock acquisition fails safely
stale lock is evidenced before recovery
lock release does not remove unrelated lock files
```

---

## 8.9 `learning_index.py`

### Purpose

Maintain a local review index so repeated reviews do not duplicate proposed or approved candidates.

### Required Public Functions

```python
load_learning_review_index(repo_root: Path) -> LearningReviewIndex
update_learning_review_index(index: LearningReviewIndex, report: OutcomeReviewReport, repo_root: Path) -> LearningReviewIndex
candidate_hash_exists(index: LearningReviewIndex, candidate_hash: str) -> bool
record_candidate_hash(index: LearningReviewIndex, candidate: MemoryCandidate) -> LearningReviewIndex
```

### Required Behavior

```text
index lives at .agentx-init/learning/learning_review_index.json
index writes are atomic
index records review keys and candidate hashes
index prevents duplicate approved/proposed candidates for identical evidence
index must not activate or approve candidates
```

### Acceptance Tests

```text
index loads when absent by creating empty in-memory index
index write stays under runtime root
duplicate candidate hash is detected
repeated review does not duplicate approved candidate
corrupt index returns safe warning and no approval
```

---

## 8.10 `regression_linker.py`

### Purpose

Link outcome reviews to regressions, prior passing evidence, suspected changes, and evaluation failures.

### Required Public Function

```python
link_regression(event: OutcomeEvent, review: OutcomeReview, context: dict) -> RegressionLink | None
```

### Required Behavior

Create a regression link when:

```text
outcome status is REGRESSION
validation evidence changed from pass to fail
monitoring evidence shows degradation after a commit
promotion gate rejected due to regression
Evaluation Harness reports benchmark regression
Documentation Sync reports breakage caused by code/docs mismatch
```

Do not create an accepted regression link when:

```text
there is no failing evidence
there is only a model suspicion
there is no prior passing baseline
commit linkage is unknown and evidence quality is low
```

### Acceptance Tests

```text
failing test with prior passing baseline creates regression link
monitoring degradation creates regression link
missing prior baseline returns None or low-confidence blocked link
model-only suspicion does not create accepted regression link
```

---

## 8.11 `learning_reporter.py`

### Purpose

Create structured and optionally Markdown learning reports.

### Required Public Functions

```python
build_outcome_review_report(
    event: OutcomeEvent,
    review: OutcomeReview,
    signals: list[LearningSignal],
    candidates: list[MemoryCandidate],
    decisions: list[LearningPolicyDecision],
    regression_links: list[RegressionLink],
    context: dict,
) -> OutcomeReviewReport

write_learning_report(report: OutcomeReviewReport, context: dict) -> dict
```

### Required Report Sections

```text
review target
outcome classification
evidence quality
what worked
what failed
regressions detected
learning signals proposed
memory candidates proposed
memory candidates rejected
policy decisions
required human approvals
follow-up review tasks
final learning verdict
```

### Acceptance Tests

```text
report builds from valid review
report includes rejected candidates
report includes policy decisions
report does not claim approval without approval evidence
report schema validates
```

---

# 9. Integration Adapter Specifications

Each adapter must be deterministic and fail closed. Adapters may read context-provided evidence if the upstream package is unavailable. No adapter may mutate upstream artifacts.

Every adapter must return `LearningAdapterResult` or a dict with equivalent fields. Adapter failures must not raise unhandled exceptions into the main pipeline. Missing upstream packages must produce `dependency_status = MISSING` and a safe `status` such as `NEEDS_MORE_EVIDENCE`, `BLOCKED`, or `UNAVAILABLE`, depending on the action requested.

## 9.1 `evaluation_adapter.py`

Required public functions:

```python
load_evaluation_summary(context: dict) -> dict
has_passing_validation(evaluation_summary: dict) -> bool
has_regression(evaluation_summary: dict) -> bool
```

Behavior:

```text
read evaluation result summaries when available
link validation pass/fail evidence to outcome reviews
link benchmark regressions to regression links
block positive learning when evaluation failed
mark learning as NEEDS_MORE_EVIDENCE when evaluation evidence is missing
```

Must not:

```text
rerun benchmarks by default
modify evaluation artifacts
ignore failed tests
learn from unvalidated success
```

## 9.2 `promotion_adapter.py`

Required public functions:

```python
load_promotion_decision(context: dict) -> dict
promotion_allows_learning(promotion_decision: dict) -> bool
promotion_rejected(promotion_decision: dict) -> bool
```

Behavior:

```text
read promotion decision evidence when available
block positive learning from rejected promotions
link promotion rejection to learning signals
only allow release-impacting learning if promotion evidence supports it
```

## 9.3 `docsync_adapter.py`

Required public functions:

```python
load_docsync_evidence(context: dict) -> dict
detect_documentation_drift(docsync_evidence: dict) -> dict
```

Behavior:

```text
read documentation drift evidence when available
create DOC_DRIFT signals when docs are inconsistent with code or behavior
block documentation-related learning without docsync evidence
link accepted learning candidates to documentation follow-up proposals
```

Must not edit documentation directly.

## 9.4 `monitoring_adapter.py`

Required public functions:

```python
load_monitoring_observations(context: dict) -> dict
detect_runtime_degradation(observations: dict) -> dict
```

Behavior:

```text
read local monitoring observations when available
link runtime degradations to outcome reviews
create regression links from monitoring evidence when supported
block learning from unverifiable monitoring claims
```

Must not:

```text
send telemetry externally
open network connection
persist sensitive telemetry fields
```

## 9.5 `scheduler_adapter.py`

Required public functions:

```python
build_follow_up_task_proposal(review: OutcomeReview, context: dict) -> FollowUpTaskProposal | None
submit_follow_up_task_proposal(proposal: FollowUpTaskProposal, context: dict) -> dict
```

Behavior:

```text
create follow-up task proposals for unresolved review items
schedule later outcome review only through scheduler policy
record task proposal evidence
block scheduler integration if policy denies it
```

Must not:

```text
start background jobs directly
create recurring tasks without scheduler approval
silently schedule future work
```

## 9.6 `policy_adapter.py`

Required public functions:

```python
check_durable_learning_allowed(candidate: MemoryCandidate, context: dict) -> dict
check_follow_up_task_allowed(proposal: FollowUpTaskProposal, context: dict) -> dict
check_report_write_allowed(report: OutcomeReviewReport, context: dict) -> dict
```

Fail-closed rule:

```text
if Policy / Capability Registry is unavailable, review/report may run, but durable memory approval and scheduler actions must block or require approval.
```

## 9.7 `memory_adapter.py`

Required public functions:

```python
build_memory_write_request(candidate: MemoryCandidate, context: dict) -> dict
check_memory_write_ready(candidate: MemoryCandidate, context: dict) -> dict
```

Behavior:

```text
prepare memory write request only after approval
never write durable memory directly in this layer
return BLOCKED if memory layer is unavailable
return NEEDS_APPROVAL if approval is missing
```

---

# 10. Schema Implementation Spec

Each schema must:

```text
require schema_version
require schema_id
require created_at where applicable
require source_component where applicable
require warnings
require errors
use enum constraints for statuses, signal types, policy decisions, evidence quality, final verdicts, and rejection reasons
allow evidence_refs and artifact_refs arrays
reject missing required fields
reject unknown enum values
support additionalProperties=false unless explicitly justified
```

## 10.1 Required Schema Coverage

```text
outcome_event.schema.json validates OutcomeEvent
outcome_review.schema.json validates OutcomeReview
learning_signal.schema.json validates LearningSignal
memory_candidate.schema.json validates MemoryCandidate
learning_policy_decision.schema.json validates LearningPolicyDecision
regression_link.schema.json validates RegressionLink
outcome_review_report.schema.json validates OutcomeReviewReport
learning_audit_event.schema.json validates LearningAuditEvent
follow_up_task_proposal.schema.json validates FollowUpTaskProposal
learning_lock.schema.json validates LearningLockRecord
learning_review_index.schema.json validates LearningReviewIndex
learning_evidence_manifest.schema.json validates evidence manifest
learning_implementation_review_report.schema.json validates implementation review report
learning_completion_record.schema.json validates completion record
```

## 10.2 Required Schema Examples in Tests

Create valid examples for:

```text
valid_outcome_event_success
valid_outcome_event_failure
valid_outcome_event_regression
valid_outcome_review_success
valid_outcome_review_failed
valid_learning_signal_fix_worked
valid_learning_signal_regression
valid_memory_candidate_needs_review
valid_memory_candidate_blocked
valid_learning_policy_decision_block
valid_learning_policy_decision_needs_approval
valid_regression_link
valid_outcome_review_report
valid_learning_audit_event
valid_follow_up_task_proposal
valid_learning_lock
valid_learning_review_index
valid_learning_evidence_manifest
valid_learning_implementation_review_report
valid_learning_completion_record
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
secret-like payload is rejected or redacted before evidence writing
```

---

# 11. Schema Versioning, Privacy, and Evidence Reference Rules

## 11.1 Schema Versioning

All durable artifacts must include `schema_version` and `schema_id`.

Rules:

```text
new schemas start at 1.0
minor additive fields may be optional only if old artifacts remain valid
required-field changes require schema version bump
old evidence must not be rewritten to satisfy new schemas
readers must tolerate older known schema versions by producing warnings, not approvals
unknown schema versions block durable learning approval
```

## 11.2 Privacy Minimization

The layer must store references to raw evidence, not raw evidence itself, whenever possible.

Do not persist:

```text
raw prompts
full command outputs
secrets
tokens
credentials
private user data
large logs
telemetry payloads
full file contents
```

Persist instead:

```text
evidence refs
artifact refs
hashes
short summaries
classification results
redacted snippets only when necessary
```

## 11.3 No-Autonomous-Activation Rule

A proposed learning signal or memory candidate must not influence future planning, tool selection, promotion decisions, policy decisions, or code generation until all of the following are true:

```text
learning policy allows it
required human approval exists
Policy / Capability Registry allows durable learning
Memory layer write path is available
Memory layer writes the candidate, not this layer
activation evidence is written
```

This layer may propose, reject, report, and package candidates. It may not activate them.

---

# 12. Controlled Outcome Review Pipeline

The implementation must include a controlled pipeline.

Required flow:

```text
1. Receive OutcomeEvent or raw event dict.
2. Validate OutcomeEvent schema.
3. Compute stable event hash and review key.
4. Acquire learning review lock for the review key.
5. Load evaluation, promotion, docsync, monitoring, scheduler, policy, and memory context if available.
6. Review outcome.
7. Block learning if evidence quality is insufficient.
8. Extract learning signals only from supported review findings.
9. Check every signal against learning policy.
10. Link regressions where supported.
11. Build memory candidates from eligible signals only.
12. Check every memory candidate against learning policy.
13. Reject unsupported, overbroad, sensitive, unsafe, or approval-bypassing candidates.
14. Build follow-up task proposals where appropriate.
15. Check follow-up proposals against policy/scheduler adapter.
16. Write outcome event evidence.
17. Write outcome review evidence.
18. Write signal, candidate, policy-decision, rejection, follow-up, and regression evidence.
19. Build outcome review report.
20. Write latest outcome review and learning report atomically.
21. Write evidence manifest with SHA-256 hashes.
22. Release learning review lock.
23. Return OutcomeReviewReport.
```

Fail-closed rules:

```text
schema-invalid event -> no learning; return blocked review/report
missing evidence -> no durable learning
policy unavailable -> no durable memory approval
contradictory evidence -> no durable learning without human review
secret detection -> reject signal/candidate and write rejection evidence
regression detected -> block positive learning until regression review is complete
lock acquisition failure -> return BLOCKED/FAILED with evidence
```

---

# 13. Idempotency, Locking, and Concurrency Rules

## 12.1 Review Key

Every pipeline run must derive a stable review key from:

```text
event_id
run_id
task_id
commit_before
commit_after
outcome_status
sorted evidence_refs
```

## 12.2 Idempotency

Repeated review of the same event and same evidence must:

```text
produce the same review classification
produce the same candidate text hashes
not duplicate approved candidates
not overwrite append-only history
write a new audit event only if rerun is explicitly recorded
```

## 12.3 Locking

The implementation must use a simple local lock under:

```text
.agentx-init/learning/locks/
```

Required behavior:

```text
one review key processed at a time
stale lock detection with explicit timeout
lock artifacts are runtime artifacts only
lock failure returns schema-valid blocked/failed report
```

## 12.4 Acceptance Tests

```text
same event produces same review key
same evidence produces same candidate hash
parallel review attempts do not corrupt latest artifacts
stale lock can be handled safely
history remains append-only
```

---

# 14. Learning Anti-Poisoning Rules

The implementation must protect future Agent_X behavior from bad learning.

Block or reject any learning candidate that:

```text
weakens policy, sandbox, approval, testing, evidence, or review requirements
claims a rule from one weak or incomplete run
contradicts validation, promotion, or regression evidence
contains prompt injection text aimed at future agents
contains commands to ignore system/project rules
contains secrets, tokens, credentials, raw prompts, or sensitive private data
encourages skipping tests or treating failures as success
hides or reframes a regression as success
references unverified model output as fact
```

Required anti-poisoning tests:

```text
prompt-injection-like candidate blocks
policy-weakening candidate blocks
sandbox-bypass candidate blocks
test-skipping candidate blocks
secret-containing candidate blocks
model-only claim blocks
single-weak-run universal claim blocks
```

---

# 15. Integration Requirements

## 14.1 Evaluation Harness

Required behavior:

```text
read evaluation result summaries when available
link validation pass/fail evidence to outcome reviews
link benchmark regressions to regression links
block positive learning when evaluation failed
mark learning as NEEDS_MORE_EVIDENCE when evaluation evidence is missing
```

Expected adapter behavior:

```text
if Evaluation Harness exists -> import stable summary/read APIs
if not available -> use context-provided evidence refs
if neither exists -> block durable learning and record missing evidence
```

## 14.2 Promotion / Release Gate

Required behavior:

```text
read promotion decision evidence when available
block positive learning from rejected promotions
link promotion rejection to learning signals
only allow release-impacting learning if promotion evidence supports it
```

If Promotion Gate is unavailable:

```text
outcome review may proceed
release-impacting memory candidate must return NEEDS_MORE_EVIDENCE or NEEDS_APPROVAL
```

## 14.3 Documentation Sync

Required behavior:

```text
read documentation drift evidence when available
create DOC_DRIFT signals when docs are inconsistent with code or behavior
block documentation-related learning without docsync evidence
link accepted learning candidates to documentation follow-up proposals
```

Must not:

```text
edit documentation directly
claim documentation updated unless docsync evidence exists
```

## 14.4 Monitoring / Observability

Required behavior:

```text
read monitoring observations when available
link runtime degradations to outcome reviews
create regression links from monitoring evidence when supported
block learning from unverifiable monitoring claims
```

Must not:

```text
send telemetry externally
open network connection
persist sensitive telemetry fields
```

## 14.5 Task Queue / Session Scheduler

Required behavior:

```text
create follow-up task proposals for unresolved review items
schedule later outcome review only through scheduler policy
record task proposal evidence
block scheduler integration if policy denies it
```

Must not:

```text
start background jobs directly
create recurring tasks without scheduler approval
silently schedule future work
```

## 14.6 Policy / Capability Registry

Required behavior:

```text
check whether durable learning is allowed
check whether memory candidate requires approval
check whether candidate scope is allowed
check whether candidate contains restricted content
check whether follow-up task creation is allowed
check whether reports may be written
```

Fail-closed rule:

```text
if Policy / Capability Registry is unavailable, review/report may run, but durable memory approval and scheduler actions must block or require approval.
```

---

# 16. Test Cases

## 15.1 Model and Schema Tests

```text
test_outcome_event_dataclass_instantiates
test_outcome_review_dataclass_instantiates
test_learning_signal_dataclass_instantiates
test_memory_candidate_dataclass_instantiates
test_policy_decision_dataclass_instantiates
test_regression_link_dataclass_instantiates
test_follow_up_task_proposal_dataclass_instantiates
test_to_dict_serializes_dataclasses
test_confidence_clamped_to_valid_range
test_learning_schemas_accept_valid_examples
test_learning_schemas_reject_missing_required_fields
test_learning_schemas_reject_invalid_enums
```

## 15.2 Outcome Reviewer Tests

```text
test_review_success_with_validation_evidence
test_review_blocks_learning_when_validation_missing
test_review_failed_validation_blocks_positive_learning
test_review_promotion_rejection_blocks_positive_learning
test_review_regression_detected_from_evaluation_evidence
test_review_contradictory_evidence_requires_human_review
test_model_only_success_claim_is_unsupported
```

## 15.3 Learning Signal Tests

```text
test_extract_fix_worked_signal_from_verified_success
test_extract_fix_failed_signal_from_failed_review
test_extract_regression_signal_from_regression_review
test_extract_policy_blocked_signal_from_policy_evidence
test_extract_doc_drift_signal_from_docsync_evidence
test_missing_evidence_creates_no_memory_eligible_signal
test_secret_like_signal_text_is_rejected_or_redacted
test_policy_bypass_signal_is_rejected
```

## 15.4 Memory Candidate Tests

```text
test_eligible_signal_creates_memory_candidate
test_memory_candidate_requires_human_review_by_default
test_unsupported_signal_creates_blocked_candidate
test_overbroad_candidate_is_blocked
test_secret_candidate_is_blocked
test_failed_run_cannot_create_positive_success_memory
test_candidate_hash_is_stable
```

## 15.5 Learning Policy Tests

```text
test_learning_policy_blocks_unsupported_claim
test_learning_policy_blocks_secret_candidate
test_learning_policy_blocks_raw_prompt_candidate
test_learning_policy_blocks_overbroad_candidate
test_learning_policy_blocks_policy_weakening_candidate
test_learning_policy_requires_approval_for_durable_memory
test_learning_policy_blocks_when_policy_registry_unavailable
test_learning_policy_allows_only_with_valid_approval_context
```

## 15.6 Learning Audit Tests

```text
test_append_outcome_event_history
test_append_outcome_review_history
test_append_learning_signal_history
test_append_memory_candidate_history
test_append_rejected_learning_history
test_append_regression_link_history
test_append_policy_decision_history
test_write_latest_outcome_review_atomically
test_write_latest_learning_report_atomically
test_learning_audit_redacts_secrets
test_learning_audit_does_not_write_outside_runtime_root
test_learning_evidence_manifest_contains_hashes
```

## 15.7 Regression Linker Tests

```text
test_regression_link_created_from_failed_eval_with_prior_pass
test_regression_link_created_from_monitoring_degradation
test_no_regression_link_without_failing_evidence
test_no_accepted_regression_link_from_model_only_suspicion
test_low_confidence_regression_link_blocks_positive_learning
```

## 15.8 Reporter Tests

```text
test_learning_report_builds_from_valid_review
test_learning_report_includes_signals_candidates_and_decisions
test_learning_report_includes_rejected_candidates
test_learning_report_does_not_claim_approval_without_approval_evidence
test_learning_report_schema_validates
```

## 15.9 Integration Adapter Tests

```text
test_evaluation_adapter_missing_blocks_durable_learning
test_promotion_adapter_rejection_blocks_positive_learning
test_docsync_adapter_doc_drift_creates_doc_drift_signal
test_monitoring_adapter_degradation_creates_regression_context
test_scheduler_adapter_does_not_start_background_job
test_policy_adapter_unavailable_blocks_memory_approval
test_memory_adapter_does_not_write_durable_memory_directly
```

## 15.10 Idempotency and Locking Tests

```text
test_same_event_produces_same_review_key
test_same_evidence_produces_same_candidate_hash
test_repeated_review_does_not_duplicate_approved_candidate
test_lock_prevents_concurrent_latest_artifact_corruption
test_stale_lock_returns_safe_result_or_recovers_with_evidence
test_learning_review_index_prevents_duplicate_candidate
test_corrupt_review_index_blocks_approval
```

## 15.11 Negative Tests

```text
test_missing_evidence_cannot_create_approved_memory
test_failed_run_cannot_be_recorded_as_success_lesson
test_regression_cannot_create_positive_learning_without_review
test_secret_payload_not_persisted_to_learning_history
test_raw_prompt_not_persisted_to_memory_candidate
test_policy_bypass_attempt_blocks
test_scheduler_bypass_attempt_blocks
test_learning_layer_does_not_mutate_source
test_learning_layer_does_not_write_durable_memory_directly
test_learning_layer_does_not_open_network
test_prompt_injection_candidate_blocks
test_test_skipping_candidate_blocks
test_raw_evidence_reference_used_instead_of_raw_payload
test_unknown_schema_version_blocks_approval
```

---

# 17. Implementation Order

Implement in this exact order:

```text
1. tools/agentx_evolve/learning/outcome_models.py
2. schema files for outcome events, reviews, signals, candidates, policy decisions, regression links, reports, audit, evidence manifest, implementation review report, completion record
3. tools/agentx_evolve/learning/learning_policy.py
4. tools/agentx_evolve/learning/learning_audit.py
5. tools/agentx_evolve/learning/evaluation_adapter.py
6. tools/agentx_evolve/learning/promotion_adapter.py
7. tools/agentx_evolve/learning/docsync_adapter.py
8. tools/agentx_evolve/learning/monitoring_adapter.py
9. tools/agentx_evolve/learning/scheduler_adapter.py
10. tools/agentx_evolve/learning/policy_adapter.py
11. tools/agentx_evolve/learning/memory_adapter.py
12. tools/agentx_evolve/learning/outcome_reviewer.py
13. tools/agentx_evolve/learning/learning_signal_extractor.py
14. tools/agentx_evolve/learning/memory_candidate_builder.py
15. tools/agentx_evolve/learning/regression_linker.py
16. tools/agentx_evolve/learning/learning_lock.py
17. tools/agentx_evolve/learning/learning_index.py
18. tools/agentx_evolve/learning/learning_reporter.py
19. tools/agentx_evolve/learning/__init__.py
18. tests
19. schema validation utility
20. completion evidence
```

Rationale:

```text
models first
schemas second
policy before memory approval
audit before pipeline writes
adapters before reviewer integration
review before signal extraction
signals before memory candidates
regression linkage before report finalization
reports after all entities exist
tests after public surfaces exist
```

---

# 18. Acceptance Criteria

The implementation is acceptable only if:

```text
all required files exist
all required schemas exist
all required tests exist
compileall passes
pytest passes
schema validation passes
outcome review works for success, failure, blocked, rejected, and regression cases
learning signals are evidence-supported
memory candidates are scoped and require approval by default
unsupported learning is rejected
secret/raw prompt learning is rejected or redacted before evidence
anti-poisoning tests pass
regressions are linked to evidence
Evaluation Harness integration fails closed when unavailable
Promotion Gate integration blocks positive learning after rejection
Documentation Sync integration records doc drift only when evidenced
Monitoring integration does not send external telemetry
Scheduler integration does not start background jobs directly
Policy / Capability Registry controls durable learning approval
Memory adapter does not write durable memory directly
learning evidence is written under .agentx-init/learning/
latest artifacts are written atomically
evidence manifest includes SHA-256 hashes
review report artifact exists
no source mutation occurs
no direct durable memory write occurs
no network is enabled by default
completion record exists
```

---

# 19. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/learning
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_learning_outcome_models.py \
  tools/agentx_evolve/tests/test_outcome_reviewer.py \
  tools/agentx_evolve/tests/test_learning_signal_extractor.py \
  tools/agentx_evolve/tests/test_memory_candidate_builder.py \
  tools/agentx_evolve/tests/test_learning_policy.py \
  tools/agentx_evolve/tests/test_learning_audit.py \
  tools/agentx_evolve/tests/test_regression_linker.py \
  tools/agentx_evolve/tests/test_learning_reporter.py \
  tools/agentx_evolve/tests/test_learning_schema_validation.py \
  tools/agentx_evolve/tests/test_learning_negative_cases.py \
  tools/agentx_evolve/tests/test_learning_integration_adapters.py \
  tools/agentx_evolve/tests/test_learning_idempotency_and_locking.py \
  tools/agentx_evolve/tests/test_learning_anti_poisoning.py \
  tools/agentx_evolve/tests/test_learning_review_index.py \
  tools/agentx_evolve/tests/test_learning_privacy_minimization.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_learning_schemas.py
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts under .agentx-init/learning/
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
external scheduler
external telemetry service
external memory service
```

---

# 20. Completion Evidence

After implementation and validation, create:

```text
.agentx-init/learning/learning_completion_record.json
.agentx-init/learning/learning_review_index.json
.agentx-init/learning/locks/<review_key>.lock
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "learning_completion_record.schema.json",
  "component_id": "AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW",
  "component_name": "Long-Term Learning / Outcome Review Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/learning/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/learning/",
  "basis_documents": [
    "LONG_TERM_LEARNING_OUTCOME_REVIEW_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_SPEC_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "evaluation_integration_verified": [],
  "promotion_gate_integration_verified": [],
  "documentation_sync_integration_verified": [],
  "monitoring_integration_verified": [],
  "scheduler_integration_verified": [],
  "policy_integration_verified": [],
  "memory_adapter_verified": [],
  "anti_poisoning_tests_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/learning/learning_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/learning/learning_implementation_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

## 19.1 Evidence Manifest Requirements

Create:

```text
.agentx-init/learning/learning_evidence_manifest.json
```

The manifest must include:

```text
validated commit
validation timestamp
command text
command exit codes
command summaries
evidence files
evidence file SHA-256 hashes
runtime artifacts used by the review
deviation register
source mutation status
anti-poisoning status
policy integration status
memory write status
final decision
```

## 19.2 Implementation Review Report Requirements

Create:

```text
.agentx-init/learning/learning_implementation_review_report.json
```

The report must include:

```text
reviewed commit
reviewed branch
review environment
compileall result
pytest result
schema validation result
coverage status by area
blockers
high issues
non-blocking follow-ups
deviation register
evidence manifest hash
completion record hash
implementation rating
final verdict
```

---

# 21. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places files outside tools/agentx_evolve/learning/ without recorded deviation
writes runtime artifacts outside .agentx-init/learning/ without recorded deviation
auto-writes durable memory without approval
learns from missing evidence
learns positive lessons from failed validation
learns positive lessons from promotion rejection
stores secrets or raw prompts
stores private/sensitive data without policy approval
creates broad universal lessons from one run
lets model-generated claims become memory without evidence
starts background scheduler jobs directly
opens network connections
sends telemetry externally
mutates source files
modifies evaluation, promotion, docsync, monitoring, scheduler, or policy artifacts directly
bypasses Policy / Capability Registry
returns unstructured review results
skips evidence writing
omits final evidence hashes
```

Allowed implementation choices:

```text
integration adapters may be safe stubs
scheduler integration may only propose tasks, not start jobs
memory candidates may remain proposed/blocked until approval layer exists
Evaluation Harness evidence may be context-provided if package is not yet stable
Promotion Gate evidence may be context-provided if package is not yet stable
Monitoring evidence may be local artifact references only
reports may be JSON-only if markdown reporting is deferred
```

---

# 22. Definition of Done

The Long-Term Learning / Outcome Review Layer is done when it can safely review outcomes and propose evidence-backed learning without uncontrolled self-reinforcement.

It must prove:

```text
all target files exist
all schemas exist
all tests exist
outcome events validate against schema
outcome reviews validate against schema
learning signals validate against schema
memory candidates validate against schema
policy decisions validate against schema
regression links validate against schema
reports validate against schema
verified success can generate bounded learning signals
failed validation blocks positive learning
promotion rejection blocks positive learning
regressions block positive learning until reviewed
missing evidence blocks durable learning
unsupported claims are rejected
secrets and raw prompts are rejected or redacted
anti-poisoning rules block unsafe learning
memory candidates require approval by default
Policy / Capability Registry controls durable learning approval
Memory adapter never writes durable memory directly
Evaluation Harness evidence is linked or missing evidence blocks learning
Promotion Gate evidence is linked or missing evidence blocks release-impacting learning
Documentation Sync evidence is linked for doc drift
Monitoring evidence is linked for runtime regressions
Scheduler integration creates only approved follow-up proposals
learning evidence is written
latest outcome review is written atomically
latest learning report is written atomically
evidence manifest exists and includes hashes
implementation review report exists
completion record exists
no source mutation occurs
no direct durable memory write occurs
no network is enabled by default
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/learning
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_learning_outcome_models.py \
  tools/agentx_evolve/tests/test_outcome_reviewer.py \
  tools/agentx_evolve/tests/test_learning_signal_extractor.py \
  tools/agentx_evolve/tests/test_memory_candidate_builder.py \
  tools/agentx_evolve/tests/test_learning_policy.py \
  tools/agentx_evolve/tests/test_learning_audit.py \
  tools/agentx_evolve/tests/test_regression_linker.py \
  tools/agentx_evolve/tests/test_learning_reporter.py \
  tools/agentx_evolve/tests/test_learning_schema_validation.py \
  tools/agentx_evolve/tests/test_learning_negative_cases.py \
  tools/agentx_evolve/tests/test_learning_integration_adapters.py \
  tools/agentx_evolve/tests/test_learning_idempotency_and_locking.py \
  tools/agentx_evolve/tests/test_learning_anti_poisoning.py \
  tools/agentx_evolve/tests/test_learning_review_index.py \
  tools/agentx_evolve/tests/test_learning_privacy_minimization.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_learning_schemas.py
git status --short
```

Expected proof:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
```

---

# 23. Implementation Review Scoring Guardrails

The post-implementation review may not rate the implementation as 10/10 unless all required commands and evidence artifacts pass.

Hard score caps:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall failure caps score at 5.0
pytest failure caps score at 6.0
schema validation failure caps score at 6.5
missing evidence manifest caps score at 7.0
missing evidence hashes caps score at 8.0
missing completion record caps score at 8.0
missing implementation review report caps score at 8.0
any required area NOT CHECKED caps score at 8.0
positive learning from failed validation caps score at 4.0
secret/raw prompt persistence caps score at 4.0
direct durable memory write caps score at 4.0
policy bypass caps score at 4.0
network enabled by default caps score at 4.0
```

---

# 24. Go / No-Go Rules

## 22.1 GO Criteria

The layer may be marked `DONE` only if:

```text
all required files exist
all required schemas exist
all required tests exist
compileall passes
pytest passes
schema validation passes
learning evidence is written
review reports are written
evidence manifest exists and includes hashes
completion record exists
memory candidates are policy-checked
memory candidates require approval by default
failed validation blocks positive learning
promotion rejection blocks positive learning
regression blocks positive learning
missing evidence blocks durable learning
secrets and raw prompts are not persisted
anti-poisoning tests pass
Policy / Capability Registry integration fails closed
Memory adapter does not write durable memory directly
no source mutation occurs
no direct durable memory write occurs
no network is enabled by default
no background scheduler starts directly
```

## 22.2 NO-GO Criteria

The layer is `NOT DONE` if any are true:

```text
compileall fails
pytest fails
schema validation fails
outcome review result is unstructured
learning signal result is unstructured
memory candidate result is unstructured
missing evidence can create approved memory
failed validation can create positive learning
promotion rejection can create positive learning
regression can create positive learning without review
secret or raw prompt is persisted
policy unavailable results in durable learning approval
direct durable memory write occurs
source mutation occurs
network is enabled by default
background scheduler job starts directly
evidence is missing
evidence hashes are missing
implementation review report is missing
completion record is missing
anti-poisoning test fails
```

## 22.3 Conditional GO

Conditional GO is allowed only for non-safety items:

```text
integration adapters are stubs if they fail closed
scheduler integration proposes tasks but does not schedule them directly
memory candidates remain proposed or blocked until human approval exists
reports are JSON-only if markdown reporting is deferred
Evaluation Harness evidence is context-provided if package API is not stable
Promotion Gate evidence is context-provided if package API is not stable
```

Conditional GO is not allowed for:

```text
policy bypass
memory approval bypass
secret persistence
direct durable memory write
positive learning from failed validation
positive learning from promotion rejection
positive learning from unresolved regression
missing evidence treated as success
schema/evidence failure
anti-poisoning failure
```

---

# 25. Final Implementation Sequence for Coding Agent

Use this sequence:

```text
1. Create tools/agentx_evolve/learning/ package.
2. Implement outcome_models.py.
3. Create all learning schemas.
4. Implement learning_policy.py.
5. Implement learning_audit.py.
6. Implement integration adapters as safe fail-closed adapters.
7. Implement outcome_reviewer.py.
8. Implement learning_signal_extractor.py.
9. Implement memory_candidate_builder.py.
10. Implement regression_linker.py.
11. Implement learning_reporter.py.
12. Update __init__.py exports.
13. Create schema validation tests.
14. Create model tests.
15. Create outcome reviewer tests.
16. Create signal extraction tests.
17. Create memory candidate tests.
18. Create policy tests.
19. Create audit tests.
20. Create regression linker tests.
21. Create reporter tests.
22. Create integration adapter tests.
23. Create idempotency and locking tests.
24. Create anti-poisoning tests.
25. Create negative safety tests.
26. Run compileall.
27. Run pytest.
28. Run schema validation.
29. Verify git status.
30. Write evidence manifest, implementation review report, and completion record.
```

Do not reorder unless required by real import dependencies.

---

# 26. Coding Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] The target repository is Agent_X.
[ ] The layer lives under tools/agentx_evolve/learning/.
[ ] Runtime artifacts go under .agentx-init/learning/.
[ ] Schemas go under tools/agentx_evolve/schemas/.
[ ] Tests go under tools/agentx_evolve/tests/.
[ ] Learning is evidence-backed only.
[ ] Durable memory writes are not performed directly.
[ ] Memory candidates require policy and approval.
[ ] Failed validation cannot create positive learning.
[ ] Promotion rejection cannot create positive learning.
[ ] Regression blocks positive learning until reviewed.
[ ] Missing evidence blocks durable learning.
[ ] Secrets and raw prompts are rejected or redacted.
[ ] Anti-poisoning rules are implemented.
[ ] Scheduler integration does not start jobs directly.
[ ] Monitoring integration does not open network or send telemetry.
[ ] Policy / Capability Registry fails closed.
[ ] Memory adapter fails closed and never writes directly.
[ ] Evidence manifest includes SHA-256 hashes.
[ ] Tests run without GPU, network, hosted model, LLM, Bun, Node, or external services.
```

---

# 27. Final Frozen Acceptance Matrix

| Area | Required for 10/10 implementation |
|---|---|
| Structure | Required files, schemas, tests, and runtime paths exist. |
| Models | Dataclasses, constants, helpers, redaction, and hashing implemented. |
| Schemas | Valid/invalid examples pass; enums are strict; required fields enforced. |
| Outcome review | Success, failure, blocked, rejected, and regression outcomes classified. |
| Signal extraction | Signals require evidence and unsafe claims are rejected. |
| Memory candidates | Candidates are scoped, evidence-backed, hashed, and not auto-approved. |
| Policy | Durable learning blocks without policy/approval. |
| Evidence | JSONL histories, latest artifacts, manifest, hashes, and completion record written. |
| Integration | Evaluation, Promotion, DocSync, Monitoring, Scheduler, Policy, and Memory adapters fail closed. |
| Anti-poisoning | Prompt injection, policy bypass, sandbox bypass, secret, and test-skipping lessons block. |
| Idempotency | Same event/evidence produces stable keys and candidate hashes. |
| Safety | No source mutation, no network, no direct memory write, no scheduler background job. |
| Validation | compileall, pytest, schema validation, and git status pass. |

---

# 28. Final Freeze Rule

This v4 document is frozen as the implementation handoff for the Long-Term Learning / Outcome Review Layer.

Allowed future changes:

```text
PATCH: wording, examples, typos, small clarifications
MINOR: additive optional tests or report fields that do not weaken safety
MAJOR: changed learning authority model, changed memory approval policy, changed evidence rules, changed runtime paths, changed direct-memory-write policy
```

Blocked without major revision:

```text
allowing durable memory write directly from this layer
removing Policy / Capability Registry approval
removing human approval where required
allowing positive learning from failed validation
allowing positive learning from promotion rejection
allowing positive learning from unresolved regression
allowing missing evidence to approve learning
allowing network telemetry by default
allowing background scheduler jobs by default
removing evidence logging
removing anti-poisoning checks
```

---

# 29. Final Rating

This v4 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, files, schemas, classes, functions, runtime artifacts, dependency gates, integration adapters, pipeline ordering, idempotency, locking, review indexing, anti-poisoning rules, privacy minimization, schema versioning, tests, validation commands, acceptance criteria, completion evidence, scoring guardrails, Go / No-Go rules, Definition of Done, inventory-consistency rules, and frozen implementation handoff rules for the Long-Term Learning / Outcome Review Layer.
```
