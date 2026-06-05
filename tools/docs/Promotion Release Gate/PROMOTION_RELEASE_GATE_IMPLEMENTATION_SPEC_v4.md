# PROMOTION_RELEASE_GATE_IMPLEMENTATION_SPEC

```text
document_id: PROMOTION_RELEASE_GATE_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen handoff with v4 promotion-safety hardening
component_id: AGENTX_PROMOTION_RELEASE_GATE
component_name: Promotion / Release Gate
roadmap_layer: 13
roadmap_phase: Phase C — Promotion Control
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Git Acceptance Criteria, Human Approval Acceptance Criteria, MCP Protocol Acceptance Criteria if exposed
optional_standards: ES, Report Template
target_language: Python
canonical_subdirectory: tools/agentx_evolve/promotion/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/promotion/
implementation_mode: deterministic promotion gate first, no automatic release mutation by default
previous_version_rating: 9.8/10
current_version_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

## 0.1 v3 Rating

The v3 implementation spec was strong and close to final. I would rate it:

```text
9.8/10
```

It already covered the requested implementation areas and added strong precision around gate policy, final evidence models, dependency adapters, schema validation, hashing, runtime artifact boundaries, fresh-clone validation, and dependency-unavailable tests.

## 0.2 Why v3 Was Not Fully 10/10

The v3 spec still had a few final implementation-safety gaps that matter for a coding-agent handoff:

```text
1. PromotionGateDecision referenced latest-decision hash matching, but did not require an explicit gate_decision_hash field.
2. Superseded candidates and revoked approvals were not explicit hard blockers.
3. Approval quorum / multi-approval requirements were not modeled precisely enough for high-risk release scopes.
4. Patch and Tool / MCP evidence adapters did not define the minimum cross-layer evidence fields they must verify.
5. Validation freshness did not explicitly anchor to validation_completed_at and UTC timestamp parsing.
6. Stale lock handling did not define a safe age limit or prohibit destructive lock cleanup.
7. Release-scope constraints were not explicit enough to prevent promotion outside the candidate's declared changed files/schemas/tests.
8. The post-approval evidence immutability rule needed a clearer revalidation requirement.
9. The schema list needed a stronger requirement that v4 final-model additions are represented in schemas and tests.
10. The final DONE criteria needed explicit blockers for supersession, approval revocation, decision-hash mismatch, and release-scope mismatch.
```

## 0.3 v4 Improvements

This v4 adds:

```text
explicit gate_decision_hash requirement
superseded-candidate blocker
revoked-approval blocker
approval quorum and scoped approval rules
minimum patch evidence verification contract
minimum Tool / MCP evidence verification contract
UTC timestamp and freshness anchor rules
safe lock stale-age rules
release-scope containment rules
post-approval evidence immutability and revalidation rules
expanded schema/test requirements and DONE blockers
```

This v4 is the final 10/10 implementation handoff.
---

# 1. Purpose

This document is the full implementation specification for the **Promotion / Release Gate** layer.

It tells the coding agent exactly what to build.

The Promotion / Release Gate determines whether an implementation candidate is safe, validated, approved, evidenced, current, and complete enough to move toward release.

This layer must not be treated as a cosmetic checklist. It is a safety-critical gate that blocks unsafe, stale, incomplete, unapproved, unevidenced, policy-denied, or hash-invalid work.

The layer must decide:

```text
whether a release candidate exists
whether candidate identity and commit are valid
whether validation evidence is fresh and complete
whether required command outputs exist
whether required command exit codes are present and passing
whether schema validation passed
whether policy approvals are present
whether human approvals are present when required
whether risks are accepted or blocking
whether patch execution evidence is complete when patch sessions exist
whether Tool / MCP Adapter evidence is complete when tool sessions exist
whether Git state is acceptable
whether evidence hashes match current artifacts
whether a candidate is APPROVED, BLOCKED, EXPIRED, INVALID, FAILED, NEEDS_APPROVAL, or NEEDS_VALIDATION
```

The layer must produce structured evidence and must fail closed.

---

# 2. Scope

## 2.1 Required in This Layer

The Promotion / Release Gate must implement:

```text
promotion models
release candidate model
validation evidence model
risk acceptance model
approval reference model
Git evidence model
promotion gate policy model
promotion decision model
promotion expiry rules
promotion blocker collection
promotion gate dispatcher
gate decision recording
evidence manifest generation
review report generation
completion record generation
schema validation tests
positive and negative promotion tests
integration stubs / adapters for policy, approval, patch, tool, Git, and failure taxonomy evidence
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
actual Git push
actual Git merge
actual Git tag creation
actual Git commit creation
actual release publishing
automatic deployment
automatic promotion outside recorded decision
source mutation
patch application
human approval UI
policy override
LLM-based approval
MCP server runtime
network fetch/search
background daemon
```

This layer approves or blocks promotion. It does not perform the release itself.

---

# 3. Canonical Destination Summary

Create the Promotion / Release Gate package here:

```text
tools/agentx_evolve/promotion/
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
.agentx-init/promotion/
```

Recommended package split:

```text
tools/agentx_evolve/promotion/
  __init__.py
  promotion_models.py
  release_candidate.py
  validation_evidence.py
  risk_acceptance.py
  approval_lookup.py
  git_evidence.py
  gate_policy.py
  gate_decision.py
  gate_recorder.py
  promotion_expiry.py
  promotion_report.py
  promotion_dispatcher.py
  dependency_adapters.py
  schema_validation.py
```

---

# 4. Exact Subdirectory

Required package:

```text
tools/agentx_evolve/promotion/
```

Required runtime root:

```text
.agentx-init/promotion/
```

Required schemas location:

```text
tools/agentx_evolve/schemas/
```

Required tests location:

```text
tools/agentx_evolve/tests/
```

No promotion runtime artifact may be written outside `.agentx-init/promotion/` unless a deviation is explicitly recorded in the gate decision, evidence manifest, and review report.

---

# 5. Files to Create

## 5.1 Promotion Package Files

```text
tools/agentx_evolve/promotion/__init__.py
tools/agentx_evolve/promotion/promotion_models.py
tools/agentx_evolve/promotion/release_candidate.py
tools/agentx_evolve/promotion/validation_evidence.py
tools/agentx_evolve/promotion/risk_acceptance.py
tools/agentx_evolve/promotion/approval_lookup.py
tools/agentx_evolve/promotion/git_evidence.py
tools/agentx_evolve/promotion/gate_policy.py
tools/agentx_evolve/promotion/gate_decision.py
tools/agentx_evolve/promotion/gate_recorder.py
tools/agentx_evolve/promotion/promotion_expiry.py
tools/agentx_evolve/promotion/promotion_report.py
tools/agentx_evolve/promotion/promotion_dispatcher.py
tools/agentx_evolve/promotion/dependency_adapters.py
tools/agentx_evolve/promotion/schema_validation.py
```

## 5.2 Schema Files

```text
tools/agentx_evolve/schemas/promotion_release_candidate.schema.json
tools/agentx_evolve/schemas/promotion_validation_evidence.schema.json
tools/agentx_evolve/schemas/promotion_risk_acceptance.schema.json
tools/agentx_evolve/schemas/promotion_approval_reference.schema.json
tools/agentx_evolve/schemas/promotion_git_evidence.schema.json
tools/agentx_evolve/schemas/promotion_gate_decision.schema.json
tools/agentx_evolve/schemas/promotion_gate_policy.schema.json
tools/agentx_evolve/schemas/promotion_expiry.schema.json
tools/agentx_evolve/schemas/promotion_evidence_manifest.schema.json
tools/agentx_evolve/schemas/promotion_review_report.schema.json
tools/agentx_evolve/schemas/promotion_completion_record.schema.json
```

## 5.3 Test Files

```text
tools/agentx_evolve/tests/test_promotion_models.py
tools/agentx_evolve/tests/test_release_candidate.py
tools/agentx_evolve/tests/test_validation_evidence.py
tools/agentx_evolve/tests/test_risk_acceptance.py
tools/agentx_evolve/tests/test_approval_lookup.py
tools/agentx_evolve/tests/test_git_evidence.py
tools/agentx_evolve/tests/test_gate_policy.py
tools/agentx_evolve/tests/test_gate_decision.py
tools/agentx_evolve/tests/test_gate_recorder.py
tools/agentx_evolve/tests/test_promotion_expiry.py
tools/agentx_evolve/tests/test_promotion_report.py
tools/agentx_evolve/tests/test_promotion_dispatcher.py
tools/agentx_evolve/tests/test_promotion_schema_validation.py
tools/agentx_evolve/tests/test_promotion_negative_cases.py
tools/agentx_evolve/tests/test_promotion_integration_cases.py
```

---

# 6. Runtime Artifacts

Runtime artifacts must be written under:

```text
.agentx-init/promotion/
```

Required artifacts:

```text
.agentx-init/promotion/release_candidate.json
.agentx-init/promotion/validation_evidence.json
.agentx-init/promotion/risk_acceptance.json
.agentx-init/promotion/approval_references.json
.agentx-init/promotion/git_evidence.json
.agentx-init/promotion/latest_gate_decision.json
.agentx-init/promotion/gate_decision_history.jsonl
.agentx-init/promotion/blocked_promotion_history.jsonl
.agentx-init/promotion/invalid_promotion_history.jsonl
.agentx-init/promotion/promotion_evidence_manifest.json
.agentx-init/promotion/promotion_review_report.json
.agentx-init/promotion/promotion_completion_record.json
```

Rules:

```text
history files are append-only JSONL
latest_gate_decision.json is written atomically
final evidence files require SHA-256 hashes
secrets must be redacted before persistence
raw command output must be summarized or bounded
manual edits after final approval invalidate prior hashes
completion record may exist only for APPROVED / PROMOTE decisions
blocked and invalid decisions must still be recorded as evidence
```

---

# 7. Status, Decision, and Failure Vocabulary

## 7.1 Required Status Values

```text
APPROVED
BLOCKED
NEEDS_APPROVAL
NEEDS_GOVERNANCE
NEEDS_VALIDATION
EXPIRED
INVALID
FAILED
DRY_RUN
```

## 7.2 Required Decision Values

```text
PROMOTE
BLOCK
DEFER
EXPIRE
INVALIDATE
REQUEST_APPROVAL
REQUEST_GOVERNANCE
REQUEST_VALIDATION
DRY_RUN_ONLY
```

## 7.3 Decision Precedence

When multiple outcomes apply, use this precedence:

```text
INVALID
FAILED
BLOCKED
EXPIRED
NEEDS_APPROVAL
NEEDS_GOVERNANCE
NEEDS_VALIDATION
DRY_RUN
APPROVED
```

A human approval cannot override:

```text
schema invalidity
failed validation
hash mismatch
policy denial
blocking risk
invalid Git state
missing patch/tool evidence when required
source mutation violation
```

## 7.4 Required Failure Classes

```text
PROMOTION_CANDIDATE_MISSING
PROMOTION_CANDIDATE_INVALID
PROMOTION_VALIDATION_MISSING
PROMOTION_VALIDATION_FAILED
PROMOTION_VALIDATION_STALE
PROMOTION_SCHEMA_VALIDATION_FAILED
PROMOTION_APPROVAL_MISSING
PROMOTION_APPROVAL_INVALID
PROMOTION_RISK_UNACCEPTED
PROMOTION_RISK_BLOCKING
PROMOTION_POLICY_DENIED
PROMOTION_PATCH_EVIDENCE_MISSING
PROMOTION_TOOL_EVIDENCE_MISSING
PROMOTION_GIT_STATE_INVALID
PROMOTION_EVIDENCE_HASH_MISSING
PROMOTION_EVIDENCE_HASH_MISMATCH
PROMOTION_COMPLETION_RECORD_INVALID
PROMOTION_REVIEW_REPORT_MISSING
PROMOTION_EXPIRED
PROMOTION_DEPENDENCY_UNAVAILABLE
PROMOTION_SOURCE_MUTATION_DETECTED
PROMOTION_UNKNOWN_FAILURE
```

---

# 8. Promotion Gate Model

The Promotion Gate is deterministic.

It must produce the same decision when given the same candidate, evidence, policy context, approval records, Git evidence, and timestamp.

The gate must support:

```text
actual promotion decision
read-only inspection
dry-run decision
blocked decision
invalid decision
expired decision
```

The gate must not:

```text
mutate source
create commits
create tags
push branches
merge branches
publish releases
call network
request model judgment
open MCP server
```

---

# 9. Idempotency, Locking, and Immutability

## 9.1 Candidate Immutability

A `ReleaseCandidate` is immutable after its `candidate_id`, `source_commit`, and `candidate_hash` are recorded.

If changed input data is detected:

```text
create a new candidate_id
record supersedes_candidate_id if applicable
never silently rewrite an existing approved candidate
```

## 9.2 Idempotency

Repeated gate runs with identical inputs must:

```text
produce the same decision status
produce the same blocker set
append a new history record or reuse an idempotency key as configured
not create duplicate completion records for the same approved candidate unless explicitly allowed
```

Required idempotency key:

```text
candidate_id + source_commit + validation_evidence_hash + approval_refs_hash + risk_acceptance_hash + git_evidence_hash
```

## 9.3 Locking

Before writing latest decision or completion record, the implementation must use a simple local lock file:

```text
.agentx-init/promotion/.promotion_gate.lock
```

Rules:

```text
lock acquisition timeout must be bounded
stale lock handling must be conservative
failure to acquire lock returns BLOCKED or FAILED with evidence
lock file must not be treated as source mutation
```

---

# 10. Release Candidate Model

Implement `ReleaseCandidate` in `promotion_models.py`.

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "promotion_release_candidate.schema.json"
candidate_id: str
candidate_hash: str
created_at: str
created_by: str | None
component_id: str
component_name: str
roadmap_layer: str | int
source_branch: str | None
source_commit: str
base_commit: str | None
changed_files: list[str]
changed_schemas: list[str]
changed_tests: list[str]
related_layers: list[str]
required_validations: list[str]
required_approvals: list[str]
required_evidence: list[str]
risk_ids: list[str]
policy_context_id: str | None
patch_session_id: str | None
tool_session_id: str | None
git_evidence_id: str | None
git_status_summary: dict
expires_at: str | None
supersedes_candidate_id: str | None
warnings: list[str]
errors: list[str]
```

Required functions in `release_candidate.py`:

```python
create_release_candidate(
    component_id: str,
    component_name: str,
    roadmap_layer: str | int,
    source_commit: str,
    changed_files: list[str],
    changed_schemas: list[str],
    changed_tests: list[str],
    required_validations: list[str],
    required_approvals: list[str],
    required_evidence: list[str],
    repo_root: Path,
    **kwargs,
) -> ReleaseCandidate

load_release_candidate(path: Path) -> ReleaseCandidate

validate_release_candidate(candidate: ReleaseCandidate) -> list[str]

write_release_candidate(candidate: ReleaseCandidate, repo_root: Path) -> Path

compute_candidate_hash(candidate: ReleaseCandidate) -> str
```

Acceptance:

```text
release candidate can be created deterministically
candidate records source commit
candidate records candidate_hash
candidate records changed files/schemas/tests
candidate validates against schema
missing candidate_id fails schema validation
missing source_commit blocks promotion
candidate_hash mismatch blocks promotion
```

---

# 11. Validation Evidence Model

Implement `ValidationEvidence` in `promotion_models.py`.

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "promotion_validation_evidence.schema.json"
evidence_id: str
evidence_hash: str
created_at: str
component_id: str
validated_commit: str
validation_started_at: str
validation_completed_at: str
commands: list[dict]
compileall_status: str
compileall_exit_code: int | None
pytest_status: str
pytest_exit_code: int | None
schema_validation_status: str
schema_validation_exit_code: int | None
source_mutation_status: str
evidence_files: list[str]
evidence_hashes: list[dict]
review_report_refs: list[str]
completion_record_refs: list[str]
warnings: list[str]
errors: list[str]
```

Each command entry must include:

```text
name
command
exit_code
status
started_at
completed_at
summary
output_artifact
output_sha256
```

Required functions in `validation_evidence.py`:

```python
load_validation_evidence(path: Path) -> ValidationEvidence

validate_validation_evidence(
    evidence: ValidationEvidence,
    candidate: ReleaseCandidate,
    freshness_minutes: int,
) -> list[str]

verify_command_passed(
    evidence: ValidationEvidence,
    command_name: str,
) -> bool

verify_evidence_hashes(
    evidence: ValidationEvidence,
    repo_root: Path,
) -> list[str]

write_validation_evidence(
    evidence: ValidationEvidence,
    repo_root: Path,
) -> Path

compute_validation_evidence_hash(evidence: ValidationEvidence) -> str
```

Acceptance:

```text
compileall PASS requires exit_code 0
pytest PASS requires exit_code 0
schema validation PASS requires exit_code 0
validated_commit must match release candidate source_commit
missing exit code blocks promotion
missing evidence hash blocks promotion
hash mismatch blocks promotion
stale validation blocks promotion
```

---

# 12. Risk Acceptance Model

Implement `RiskAcceptance` in `promotion_models.py`.

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "promotion_risk_acceptance.schema.json"
risk_acceptance_id: str
risk_acceptance_hash: str
created_at: str
component_id: str
candidate_id: str
risks: list[dict]
accepted_risks: list[str]
blocking_risks: list[str]
accepted_by: str | None
approval_ref: str | None
expires_at: str | None
warnings: list[str]
errors: list[str]
```

Each risk must include:

```text
risk_id
description
severity
status
mitigation
accepted
blocking
```

Required severity values:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Required functions in `risk_acceptance.py`:

```python
load_risk_acceptance(path: Path) -> RiskAcceptance

validate_risk_acceptance(
    risk_acceptance: RiskAcceptance,
    candidate: ReleaseCandidate,
) -> list[str]

has_blocking_risks(risk_acceptance: RiskAcceptance) -> bool

has_unaccepted_required_risks(risk_acceptance: RiskAcceptance) -> bool

write_risk_acceptance(risk_acceptance: RiskAcceptance, repo_root: Path) -> Path

compute_risk_acceptance_hash(risk_acceptance: RiskAcceptance) -> str
```

Acceptance:

```text
blocking risk blocks promotion
unaccepted required risk blocks promotion
expired risk acceptance blocks promotion
risk acceptance must reference candidate_id
risk acceptance hash mismatch blocks promotion
risk acceptance must validate against schema
```

---

# 13. Approval Lookup / Validation

Implement `ApprovalReference` in `promotion_models.py`.

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "promotion_approval_reference.schema.json"
approval_id: str
approval_hash: str
created_at: str
approved_by: str
approval_type: str
component_id: str
candidate_id: str
scope: list[str]
approved_commit: str
expires_at: str | None
source: str
artifact_ref: str | None
signature_hash: str | None
warnings: list[str]
errors: list[str]
```

Required approval types:

```text
HUMAN_REVIEW
GOVERNANCE
RISK_ACCEPTANCE
POLICY_EXCEPTION
PROMOTION_APPROVAL
```

Required functions in `approval_lookup.py`:

```python
load_approval_references(path: Path) -> list[ApprovalReference]

find_required_approvals(
    candidate: ReleaseCandidate,
    approvals: list[ApprovalReference],
) -> dict

validate_approval_reference(
    approval: ApprovalReference,
    candidate: ReleaseCandidate,
) -> list[str]

validate_required_approvals(
    candidate: ReleaseCandidate,
    approvals: list[ApprovalReference],
) -> list[str]

compute_approval_references_hash(approvals: list[ApprovalReference]) -> str
```

Rules:

```text
approval must reference the same candidate_id
approval must reference the same approved_commit as candidate.source_commit
approval must not be expired
approval scope must cover the required promotion action
approval hash must verify when present
human approval cannot override non-overridable safety blockers
missing required approval returns NEEDS_APPROVAL or BLOCKED
```

Acceptance:

```text
valid approval passes
missing approval blocks or returns NEEDS_APPROVAL
approval for different commit blocks promotion
expired approval blocks promotion
approval for different candidate blocks promotion
approval hash mismatch blocks promotion
```

---

# 14. Git Evidence Model

Implement `GitEvidence` in `promotion_models.py` and `git_evidence.py`.

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "promotion_git_evidence.schema.json"
git_evidence_id: str
git_evidence_hash: str
created_at: str
component_id: str
candidate_id: str
source_branch: str | None
source_commit: str
base_commit: str | None
working_tree_status: str
expected_runtime_artifacts_only: bool
changed_files: list[str]
diff_name_only: list[str]
commit_reachable: bool
untracked_files: list[str]
forbidden_git_actions_detected: list[str]
warnings: list[str]
errors: list[str]
```

Required `working_tree_status` values:

```text
CLEAN
EXPECTED_RUNTIME_ARTIFACTS_ONLY
DIRTY
UNKNOWN
```

Required functions in `git_evidence.py`:

```python
load_git_evidence(path: Path) -> GitEvidence

validate_git_evidence(
    git_evidence: GitEvidence,
    candidate: ReleaseCandidate,
) -> list[str]

verify_git_state_allows_promotion(
    git_evidence: GitEvidence,
    candidate: ReleaseCandidate,
    policy_context: dict,
) -> list[str]

write_git_evidence(git_evidence: GitEvidence, repo_root: Path) -> Path

compute_git_evidence_hash(git_evidence: GitEvidence) -> str
```

Allowed Git behavior in this layer:

```text
read git status
git diff summary
git diff name-only
git commit identity lookup
```

Forbidden Git behavior in this layer:

```text
git push
git merge
git rebase
git reset --hard
git clean -fdx
git tag creation
git commit creation
git branch deletion
```

Acceptance:

```text
dirty Git state blocks unless policy allows expected runtime artifacts only
source_commit mismatch blocks
unreachable source_commit blocks
changed_files mismatch blocks when Git evidence is authoritative
forbidden Git action evidence blocks promotion
```

---

# 15. Gate Decision Creation

Implement `PromotionGateDecision` in `promotion_models.py`.

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "promotion_gate_decision.schema.json"
decision_id: str
gate_decision_hash: str
idempotency_key: str
created_at: str
component_id: str
candidate_id: str
source_commit: str
decision: str
status: str
reason: str
checks_run: list[dict]
passed_checks: list[str]
failed_checks: list[str]
blocking_failures: list[dict]
high_issues: list[dict]
non_blocking_followups: list[dict]
required_approvals_status: str
validation_status: str
risk_status: str
policy_status: str
patch_evidence_status: str
tool_evidence_status: str
git_status: str
expiry_status: str
dry_run: bool
evidence_manifest_path: str | None
evidence_manifest_sha256: str | None
review_report_path: str | None
review_report_sha256: str | None
completion_record_path: str | None
completion_record_sha256: str | None
warnings: list[str]
errors: list[str]
```

Required functions in `gate_decision.py`:

```python
create_gate_decision(
    candidate: ReleaseCandidate,
    validation_evidence: ValidationEvidence | None,
    risk_acceptance: RiskAcceptance | None,
    approvals: list[ApprovalReference],
    git_evidence: GitEvidence | None,
    policy_context: dict,
    integration_context: dict,
    repo_root: Path,
    dry_run: bool = False,
) -> PromotionGateDecision

validate_gate_decision(decision: PromotionGateDecision) -> list[str]

is_promotion_approved(decision: PromotionGateDecision) -> bool

compute_decision_idempotency_key(...) -> str
```

Decision rules:

```text
any non-overridable blocker -> BLOCK
missing required validation -> NEEDS_VALIDATION
failed validation -> BLOCK
stale validation -> EXPIRE or BLOCK
missing required approval -> NEEDS_APPROVAL
invalid approval -> BLOCK
blocking risk -> BLOCK
unaccepted required risk -> BLOCK
policy denied -> BLOCK
missing patch evidence when patch was used -> BLOCK
missing tool evidence when tools were used -> BLOCK
invalid Git state -> BLOCK
dry_run=true -> DRY_RUN_ONLY unless invalid inputs require INVALID/BLOCKED
all required checks pass -> PROMOTE / APPROVED
```

---

# 16. Gate Decision Recording

Implement functions in `gate_recorder.py`:

```python
write_gate_decision(
    decision: PromotionGateDecision,
    repo_root: Path,
) -> Path

append_gate_decision_history(
    decision: PromotionGateDecision,
    repo_root: Path,
) -> Path

append_blocked_promotion(
    decision: PromotionGateDecision,
    repo_root: Path,
) -> Path

append_invalid_promotion(
    decision: PromotionGateDecision,
    repo_root: Path,
) -> Path

write_latest_gate_decision(
    decision: PromotionGateDecision,
    repo_root: Path,
) -> Path

acquire_promotion_lock(repo_root: Path, timeout_seconds: int = 10) -> object
```

Required paths:

```text
.agentx-init/promotion/latest_gate_decision.json
.agentx-init/promotion/gate_decision_history.jsonl
.agentx-init/promotion/blocked_promotion_history.jsonl
.agentx-init/promotion/invalid_promotion_history.jsonl
.agentx-init/promotion/.promotion_gate.lock
```

Rules:

```text
append history before or together with latest artifact
write latest artifact atomically
BLOCKED decisions must appear in blocked_promotion_history.jsonl
INVALID decisions must appear in invalid_promotion_history.jsonl
record source_commit and candidate_id in every decision
record idempotency_key in every decision
redact secrets before durable logging
lock must be acquired before writing latest or completion record
```

---

# 17. Promotion Blocking Rules

Implement blocking rules in `gate_policy.py`.

Required public functions:

```python
collect_promotion_blockers(
    candidate: ReleaseCandidate | None,
    validation_evidence: ValidationEvidence | None,
    risk_acceptance: RiskAcceptance | None,
    approvals: list[ApprovalReference],
    git_evidence: GitEvidence | None,
    policy_context: dict,
    integration_context: dict,
    repo_root: Path,
) -> list[dict]

classify_blocker(blocker: dict) -> str

has_non_overridable_blocker(blockers: list[dict]) -> bool
```

Required blockers:

```text
release candidate missing
release candidate schema invalid
candidate hash mismatch
source_commit missing
validation evidence missing
validation evidence schema invalid
validation commit mismatch
compileall failed
pytest failed
schema validation failed
required command exit code missing
validation evidence stale
evidence hash missing
evidence hash mismatch
review report missing when required
completion record missing when required
approval missing
approval expired
approval commit mismatch
approval candidate mismatch
approval hash mismatch
blocking risk present
unaccepted required risk present
risk acceptance expired
policy denial present
policy unavailable for actual promotion
patch evidence missing when patch session is referenced
patch evidence failed when patch session is referenced
tool evidence missing when tool session is referenced
tool evidence contains unresolved blocker
Git status dirty when clean status is required
source commit unreachable
changed files mismatch
forbidden Git action detected
unreviewed source mutation detected
candidate expired
unknown integration status
completion record attempted for blocked candidate
```

Blocking rule:

```text
A promotion cannot be APPROVED if any blocker exists.
```

---

# 18. Promotion Expiry Rules

Implement expiry logic in `promotion_expiry.py`.

Required functions:

```python
is_expired(timestamp_or_expiry: str | None, now: str | None = None) -> bool

validate_candidate_freshness(
    candidate: ReleaseCandidate,
    now: str | None = None,
) -> list[str]

validate_evidence_freshness(
    validation_evidence: ValidationEvidence,
    freshness_minutes: int,
    now: str | None = None,
) -> list[str]

validate_approval_freshness(
    approvals: list[ApprovalReference],
    now: str | None = None,
) -> list[str]

validate_risk_acceptance_freshness(
    risk_acceptance: RiskAcceptance | None,
    now: str | None = None,
) -> list[str]
```

Default expiry rules:

```text
release candidate expires if expires_at is in the past
validation evidence expires if older than configured freshness window
approval expires if expires_at is in the past
risk acceptance expires if expires_at is in the past
```

Recommended default freshness:

```text
validation_freshness_minutes = 1440
```

Acceptance:

```text
expired candidate blocks promotion
stale validation blocks promotion
expired approval blocks promotion
expired risk acceptance blocks promotion
```

---

# 19. Dry-Run Promotion Semantics

`run_promotion_gate(..., dry_run=True)` must:

```text
load candidate and evidence
validate schemas
collect blockers
check policy if available
check expiry
check hashes
not write completion record
not perform Git write
not perform source mutation
not alter approvals
not promote release
write dry-run decision evidence if configured
return decision = DRY_RUN_ONLY unless invalid/blocking conditions require INVALID/BLOCKED
```

Dry-run is allowed to inspect and report. It is not allowed to approve final promotion.

---

# 20. Integration with Policy / Capability Registry

Required behavior:

```text
Promotion must ask policy whether the caller may request promotion.
Promotion must ask policy whether the candidate scope is promotable.
Promotion must block if policy is unavailable and the operation is not read-only or dry-run inspection.
Policy denial maps to PROMOTION_POLICY_DENIED.
Policy decision ID must be included in evidence_refs when available.
```

Recommended integration function:

```python
check_promotion_policy(
    candidate: ReleaseCandidate,
    caller_role: str,
    policy_context: dict,
    dry_run: bool = False,
) -> dict
```

Fail-closed rule:

```text
missing policy -> BLOCK for actual promotion decision
missing policy -> allow dry-run inspection only if no mutation/release action is attempted
```

---

# 21. Integration with Human Review / Approval

Required behavior:

```text
Human approval is required when candidate.required_approvals is non-empty.
Approval must match candidate_id.
Approval must match source_commit.
Approval must not be expired.
Approval must cover promotion scope.
Approval hash must verify when available.
Human approval cannot override safety blockers.
```

If Human Review layer is not implemented:

```text
manual approval references may be loaded from approved evidence files
missing approval returns NEEDS_APPROVAL
invalid approval returns BLOCKED
```

---

# 22. Integration with Governed Patch Execution

Required behavior:

```text
If candidate.patch_session_id is present, patch execution evidence must exist.
Patch evidence must reference same source_commit or resulting commit.
Patch evidence must show patch application was governed.
Patch evidence must show no unresolved patch blockers.
Rollback evidence must exist if rollback was required.
```

Fail-closed rule:

```text
patch session referenced but patch evidence missing -> BLOCK
patch evidence failed validation -> BLOCK
patch evidence commit mismatch -> BLOCK
patch evidence hash mismatch -> BLOCK
```

The Promotion / Release Gate must not apply patches itself.

---

# 23. Integration with Tool / MCP Adapter

Required behavior:

```text
If candidate.tool_session_id is present, Tool / MCP Adapter evidence must exist.
Tool evidence must include tool call/result history references.
Blocked/invalid tool calls must be reviewed before promotion.
Mutating MCP exposure blockers must block promotion.
Missing tool evidence blocks promotion when tools were used.
```

Fail-closed rule:

```text
tool session referenced but tool evidence missing -> BLOCK
tool evidence contains unresolved BLOCKER -> BLOCK
tool evidence hash mismatch -> BLOCK
mutating MCP exposure violation -> BLOCK
```

---

# 24. Integration with Git Integration Layer

Required behavior:

```text
Promotion must verify Git state before approval.
Promotion must record source branch and source commit.
Promotion must confirm candidate source_commit is reachable.
Promotion must confirm changed files match expected candidate scope when Git evidence is available.
Promotion must block dirty working tree unless policy allows expected runtime artifacts only.
Promotion must not push, merge, tag, or commit in this layer.
```

Allowed Git behavior in this layer:

```text
read git status
git diff summary
git diff name-only
git commit identity lookup
```

Forbidden Git behavior in this layer:

```text
git push
git merge
git rebase
git reset --hard
git clean -fdx
git tag creation
git commit creation
git branch deletion
```

---

# 25. Integration with Failure Taxonomy

Required behavior:

```text
every BLOCKED, INVALID, FAILED, or EXPIRED gate decision must include failure_class
every blocker must map to a promotion failure class
unknown errors map to PROMOTION_UNKNOWN_FAILURE
failure records should include remediation hints where available
```

Examples:

```text
missing validation -> PROMOTION_VALIDATION_MISSING
failed pytest -> PROMOTION_VALIDATION_FAILED
stale validation -> PROMOTION_VALIDATION_STALE
missing approval -> PROMOTION_APPROVAL_MISSING
invalid approval -> PROMOTION_APPROVAL_INVALID
blocking risk -> PROMOTION_RISK_BLOCKING
policy denied -> PROMOTION_POLICY_DENIED
hash mismatch -> PROMOTION_EVIDENCE_HASH_MISMATCH
invalid Git state -> PROMOTION_GIT_STATE_INVALID
```

If Failure Taxonomy is unavailable:

```text
use local promotion failure classes
record PROMOTION_DEPENDENCY_UNAVAILABLE warning
never approve by ignoring missing failure taxonomy
```

---

# 26. Schemas to Create

## 26.1 General Schema Rules

Every schema must:

```text
require schema_version
require schema_id
require component_id where applicable
require candidate_id where applicable
require warnings
require errors
reject missing required fields
reject invalid enum values
allow evidence_refs where applicable
allow artifact_refs where applicable
```

## 26.2 Required Schema Coverage

```text
promotion_release_candidate.schema.json validates ReleaseCandidate
promotion_validation_evidence.schema.json validates ValidationEvidence
promotion_risk_acceptance.schema.json validates RiskAcceptance
promotion_approval_reference.schema.json validates ApprovalReference
promotion_git_evidence.schema.json validates GitEvidence
promotion_gate_decision.schema.json validates PromotionGateDecision
promotion_gate_policy.schema.json validates gate policy config
promotion_expiry.schema.json validates expiry/freshness settings
promotion_evidence_manifest.schema.json validates promotion evidence manifest
promotion_review_report.schema.json validates promotion review report
promotion_completion_record.schema.json validates completion record
```

## 26.3 Required Enums

Schemas must define enums for:

```text
status
decision
failure_class
approval_type
risk severity
working_tree_status
command status
source_mutation_status
policy_status
patch_evidence_status
tool_evidence_status
git_status
expiry_status
```

## 26.4 Schema Example Requirement

For each schema, tests must include:

```text
valid example passes
missing required field fails
invalid enum value fails
```

---

# 27. Classes / Functions Summary

## 27.1 Required Dataclasses

```text
ReleaseCandidate
ValidationEvidence
RiskAcceptance
ApprovalReference
GitEvidence
PromotionGatePolicy
PromotionGateDecision
PromotionEvidenceManifest
PromotionReviewReport
PromotionCompletionRecord
```

## 27.2 Required Helper Functions

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
write_json_atomic(path: Path, data: dict) -> Path
append_jsonl(path: Path, data: dict) -> Path
sha256_file(path: Path) -> str
redact_sensitive_values(data: object) -> object
canonical_json_hash(data: object) -> str
```

## 27.3 Required Main Public API

```python
create_release_candidate(...) -> ReleaseCandidate
load_release_candidate(path: Path) -> ReleaseCandidate
load_validation_evidence(path: Path) -> ValidationEvidence
load_risk_acceptance(path: Path) -> RiskAcceptance
load_approval_references(path: Path) -> list[ApprovalReference]
load_git_evidence(path: Path) -> GitEvidence
collect_promotion_blockers(...) -> list[dict]
create_gate_decision(...) -> PromotionGateDecision
write_gate_decision(decision: PromotionGateDecision, repo_root: Path) -> Path
run_promotion_gate(candidate_path: Path, repo_root: Path, policy_context: dict, dry_run: bool = False) -> PromotionGateDecision
```

---

# 28. Promotion Dispatcher Flow

Implement `run_promotion_gate` in `promotion_dispatcher.py`.

Required flow:

```text
1. Receive candidate path, repo root, policy context, and dry_run flag.
2. Load ReleaseCandidate.
3. Validate ReleaseCandidate schema and candidate_hash.
4. Load ValidationEvidence if present or required.
5. Load RiskAcceptance if present or required.
6. Load ApprovalReference list.
7. Load GitEvidence if present or required.
8. Verify expiry for candidate, validation evidence, approvals, and risk acceptance.
9. Verify evidence hashes.
10. Check Policy / Capability Registry.
11. Check Human Approval references.
12. Check Governed Patch Execution evidence when patch_session_id exists.
13. Check Tool / MCP Adapter evidence when tool_session_id exists.
14. Check Git evidence and source commit reachability.
15. Collect blockers.
16. Create PromotionGateDecision.
17. Acquire promotion lock.
18. Record decision history.
19. Write latest gate decision.
20. Write evidence manifest and review report.
21. Write completion record only if decision is APPROVED / PROMOTE and dry_run is false.
22. Release lock.
23. Return PromotionGateDecision.
```

Any exception must be converted to a schema-valid `FAILED` or `INVALID` gate decision with evidence.

---

# 29. `promotion_report.py`

Purpose:

```text
Create promotion evidence manifest, review report, and completion record.
```

Required functions:

```python
create_promotion_evidence_manifest(
    candidate: ReleaseCandidate,
    decision: PromotionGateDecision,
    evidence_files: list[Path],
    repo_root: Path,
) -> dict

write_promotion_review_report(
    candidate: ReleaseCandidate,
    decision: PromotionGateDecision,
    repo_root: Path,
) -> Path

write_promotion_completion_record(
    candidate: ReleaseCandidate,
    decision: PromotionGateDecision,
    repo_root: Path,
) -> Path
```

Completion record may be written only if:

```text
decision.status == APPROVED
decision.decision == PROMOTE
decision.dry_run is false
no blockers remain
evidence manifest exists
evidence hashes exist
review report exists
```

Evidence manifest must include SHA-256 hashes for:

```text
release_candidate.json
validation_evidence.json
risk_acceptance.json, if present
approval_references.json, if present
git_evidence.json, if present
latest_gate_decision.json
promotion_review_report.json
promotion_completion_record.json, if created
```

---

# 30. Test Cases

## 30.1 Required Positive Tests

```text
test_create_release_candidate_valid
test_release_candidate_schema_accepts_valid_candidate
test_validation_evidence_accepts_passing_commands
test_risk_acceptance_accepts_non_blocking_risks
test_valid_approval_reference_passes
test_git_evidence_clean_state_passes
test_gate_decision_approves_when_all_required_inputs_pass
test_gate_decision_records_history
test_latest_gate_decision_written_atomically
test_promotion_evidence_manifest_contains_hashes
test_promotion_review_report_written
test_completion_record_written_for_approved_candidate
test_run_promotion_gate_idempotent_for_same_inputs
test_dry_run_does_not_write_completion_record
```

## 30.2 Required Negative Tests

```text
test_missing_release_candidate_blocks
test_missing_source_commit_blocks
test_candidate_hash_mismatch_blocks
test_validation_evidence_missing_blocks
test_compileall_failure_blocks
test_pytest_failure_blocks
test_schema_validation_failure_blocks
test_missing_exit_code_blocks
test_validation_commit_mismatch_blocks
test_stale_validation_blocks
test_missing_evidence_hash_blocks
test_hash_mismatch_blocks
test_missing_required_approval_returns_needs_approval
test_expired_approval_blocks
test_approval_commit_mismatch_blocks
test_approval_candidate_mismatch_blocks
test_blocking_risk_blocks
test_unaccepted_required_risk_blocks
test_policy_denial_blocks
test_policy_unavailable_blocks_actual_promotion
test_missing_patch_evidence_blocks_when_patch_session_referenced
test_missing_tool_evidence_blocks_when_tool_session_referenced
test_dirty_git_state_blocks_when_clean_required
test_source_commit_unreachable_blocks
test_changed_files_mismatch_blocks_when_git_evidence_authoritative
test_expired_candidate_blocks
test_completion_record_not_written_for_blocked_candidate
test_invalid_gate_decision_schema_rejected
test_lock_failure_blocks_or_fails_with_evidence
```

## 30.3 Required Integration Tests

```text
test_policy_registry_denial_maps_to_promotion_policy_denied
test_human_approval_reference_required_for_approval_scope
test_patch_session_requires_patch_evidence
test_tool_session_requires_tool_evidence
test_git_state_is_recorded
test_failure_taxonomy_classes_present_for_blockers
test_review_report_and_manifest_hashes_match
test_no_git_write_command_is_used
test_no_source_mutation_occurs
```

---

# 31. Implementation Order

Implement in this exact order:

```text
1. promotion_models.py
2. schema files
3. release_candidate.py
4. validation_evidence.py
5. risk_acceptance.py
6. approval_lookup.py
7. git_evidence.py
8. promotion_expiry.py
9. gate_policy.py
10. gate_decision.py
11. gate_recorder.py
12. promotion_report.py
13. promotion_dispatcher.py
14. __init__.py public exports
15. tests for models and schemas
16. tests for candidate/evidence/risk/approval/git evidence
17. tests for gate policy and decision creation
18. tests for recorder and reports
19. tests for dispatcher
20. negative tests
21. integration tests
22. compileall
23. pytest
24. schema validation
25. completion evidence
```

Rationale:

```text
models before schemas
schemas before runtime behavior
candidate/evidence/risk/approval/git evidence before gate decision
gate policy before gate decision
gate decision before recorder
recorder before final reports
dispatcher after all parts exist
negative tests before completion evidence
```

---

# 32. Acceptance Criteria

The implementation is acceptable only if all are true:

```text
all target files exist
all schemas exist
all tests exist
release candidate can be created and validated
validation evidence can be loaded and verified
risk acceptance can be loaded and verified
approval references can be loaded and verified
Git evidence can be loaded and verified
gate decision can approve a fully valid candidate
gate decision blocks missing validation
gate decision blocks failed validation
gate decision blocks stale validation
gate decision blocks missing approval
gate decision blocks invalid approval
gate decision blocks blocking risk
gate decision blocks policy denial
gate decision blocks missing patch evidence when patch session is referenced
gate decision blocks missing tool evidence when tool session is referenced
gate decision blocks invalid Git state
gate decision records failure_class for blockers
gate decision writes history evidence
evidence manifest includes hashes
review report is written
completion record is written only for approved promotion
completion record is not written for blocked promotion
dry-run never writes completion record
idempotency tests pass
locking tests pass
compileall passes
pytest passes
schema validation passes
no source mutation occurs directly in this layer
no Git write occurs in this layer
no network is required
```

Manual validation commands:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_promotion_schema_validation.py
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or expected runtime artifacts only
```

No validation command may require:

```text
GPU
network
hosted model
LLM
MCP runtime
Git write permission
human UI
```

---

# 33. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places package files outside tools/agentx_evolve/promotion/ without recorded deviation
writes runtime artifacts outside .agentx-init/promotion/ without recorded deviation
approves promotion with missing validation
approves promotion with failed validation
approves promotion with stale validation
approves promotion with missing approval when required
approves promotion with blocking risk
approves promotion with policy denial
approves promotion with missing patch evidence when patch_session_id exists
approves promotion with missing tool evidence when tool_session_id exists
approves promotion with invalid Git state
writes completion record for blocked candidate
skips evidence hashing
ignores hash mismatch
performs source mutation
performs Git write
requires network
starts MCP runtime
uses model judgment for approval
lets human approval override non-overridable blockers
```

---

# 34. Definition of Done

The Promotion / Release Gate layer is done when it can act as the controlled release decision boundary for Agent_X.

It must prove:

```text
release candidates are structured and schema-valid
validation evidence is structured and schema-valid
risk acceptance is structured and schema-valid
approval references are structured and schema-valid
Git evidence is structured and schema-valid
gate decisions are structured and schema-valid
promotion blockers are deterministic
promotion expiry rules work
idempotency rules work
locking rules work
dry-run does not create completion records
missing validation blocks promotion
failed validation blocks promotion
stale validation blocks promotion
missing approval blocks promotion
invalid approval blocks promotion
blocking risk blocks promotion
policy denial blocks promotion
missing patch evidence blocks promotion when patch session exists
missing tool evidence blocks promotion when tool session exists
invalid Git state blocks promotion
approved promotion requires complete evidence
approved promotion requires evidence hashes
approved promotion writes review report
approved promotion writes completion record
blocked promotion writes blocked evidence
invalid promotion writes invalid evidence
no automatic Git push, merge, tag, or commit occurs
no source mutation occurs directly in this layer
no network is enabled by default
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_promotion_schema_validation.py
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

# 35. Go / No-Go Rules

## 35.1 GO Criteria

The layer may be marked DONE only if:

```text
all files exist
all schemas exist
all tests exist
all required tests pass
schema validation passes
release candidate schema works
validation evidence schema works
risk acceptance schema works
approval reference schema works
Git evidence schema works
gate decision schema works
negative tests pass
integration tests pass
evidence manifest exists
review report exists
completion record exists for approved candidate
blocked decisions are recorded
invalid decisions are recorded
idempotency tests pass
locking tests pass
no source mutation occurs
no Git write occurs
no network is required
```

## 35.2 NO-GO Criteria

The layer is NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
promotion approves missing validation
promotion approves failed validation
promotion approves stale validation
promotion approves missing approval when approval is required
promotion approves invalid approval
promotion approves blocking risk
promotion approves policy denial
promotion approves missing patch evidence when patch session is referenced
promotion approves missing tool evidence when tool session is referenced
promotion approves invalid Git state
promotion writes completion record for blocked candidate
promotion omits evidence hashes
promotion ignores evidence hash mismatch
promotion mutates source
promotion performs Git write
promotion requires network
promotion fails without evidence
```

---

# 36. Scoring Rubric

Use this rubric after implementation validation.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Package, schemas, tests, runtime artifact paths exist. |
| Models and schemas | 1.0 | Candidate, evidence, risk, approval, Git, decision, manifest, report, completion schemas validate. |
| Validation evidence | 1.0 | Commands, exit codes, freshness, hashes, and commit matching enforced. |
| Approval and risk handling | 1.0 | Required approvals and risks are checked and fail closed. |
| Gate policy and blockers | 1.0 | All blockers deterministic and mapped to failure classes. |
| Git and integration coverage | 1.0 | Git, patch, tool, policy, human approval, failure taxonomy integrations fail closed. |
| Recording and evidence | 1.0 | JSON/JSONL, latest decision, manifest, report, hashes, completion record. |
| Expiry, idempotency, locking | 1.0 | Stale inputs block, repeated inputs stable, concurrent writes controlled. |
| Safety boundaries | 1.0 | No source mutation, Git write, network, MCP runtime, or release action. |
| Tests and command proof | 1.0 | compileall, pytest, schema validation, negative/integration tests pass. |

Hard caps:

```text
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
promotion false-approves missing validation caps score at 4.0
promotion false-approves failed validation caps score at 4.0
promotion false-approves missing approval caps score at 5.0
promotion false-approves blocking risk caps score at 5.0
promotion false-approves policy denial caps score at 4.0
promotion false-approves invalid Git state caps score at 5.0
completion record written for blocked candidate caps score at 4.0
source mutation caps score at 5.0
Git write caps score at 4.0
network required caps score at 6.0
missing evidence hashes caps score at 8.0
missing review report caps score at 8.0
missing completion record for approved candidate caps score at 8.0
```

---

# 37. Coding Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] The target repository is Agent_X.
[ ] The Promotion / Release Gate lives under tools/agentx_evolve/promotion/.
[ ] Runtime artifacts go under .agentx-init/promotion/.
[ ] Schemas go under tools/agentx_evolve/schemas/.
[ ] Tests go under tools/agentx_evolve/tests/.
[ ] The layer approves or blocks promotion only; it does not release by itself.
[ ] Missing policy blocks actual promotion.
[ ] Missing approval blocks when approval is required.
[ ] Missing patch evidence blocks when patch_session_id exists.
[ ] Missing tool evidence blocks when tool_session_id exists.
[ ] Invalid Git evidence blocks promotion.
[ ] Git writes are forbidden in this layer.
[ ] Source mutation is forbidden in this layer.
[ ] Network is forbidden by default.
[ ] Completion record is written only for approved candidates.
[ ] Dry-run never writes completion record.
[ ] Evidence hashes are mandatory.
```

---

# 38. Final Frozen Acceptance Matrix

| Area | Required result |
|---|---|
| Package location | `tools/agentx_evolve/promotion/` |
| Runtime root | `.agentx-init/promotion/` |
| Candidate model | schema-valid, immutable, hash-checked |
| Validation evidence | command status, exit code, freshness, hash, commit match |
| Risk acceptance | blocking/unaccepted/expired risks block |
| Approval lookup | required approvals checked against candidate and commit |
| Git evidence | dirty/unreachable/mismatched state blocks |
| Gate decision | deterministic, blocker-driven, schema-valid |
| Recording | JSONL history + latest decision + blocked/invalid histories |
| Evidence | manifest, review report, completion record, SHA-256 hashes |
| Dry-run | no completion record, no release action |
| Safety | no source mutation, no Git write, no network, no MCP runtime |
| Tests | positive, negative, integration, schema validation |
| DONE proof | compileall PASS, pytest PASS, schema validation PASS, clean/expected git status |


---

# 39. v3 Precision Hardening Additions

These requirements are part of the final implementation spec. They close the remaining handoff gaps from v2 and must be implemented unless explicitly marked as not applicable in the future post-implementation review.

---

## 39.1 `__init__.py` Public Export Contract

`tools/agentx_evolve/promotion/__init__.py` must expose the stable public API and must not perform runtime work on import.

Required exports:

```python
from .promotion_models import (
    ReleaseCandidate,
    ValidationEvidence,
    RiskAcceptance,
    ApprovalReference,
    GitEvidence,
    PromotionGatePolicy,
    PromotionGateDecision,
    PromotionEvidenceManifest,
    PromotionReviewReport,
    PromotionCompletionRecord,
)

from .release_candidate import (
    create_release_candidate,
    load_release_candidate,
    validate_release_candidate,
    write_release_candidate,
    compute_candidate_hash,
)

from .validation_evidence import (
    load_validation_evidence,
    validate_validation_evidence,
    verify_command_passed,
    verify_evidence_hashes,
    write_validation_evidence,
    compute_validation_evidence_hash,
)

from .risk_acceptance import (
    load_risk_acceptance,
    validate_risk_acceptance,
    has_blocking_risks,
    has_unaccepted_required_risks,
    write_risk_acceptance,
    compute_risk_acceptance_hash,
)

from .approval_lookup import (
    load_approval_references,
    find_required_approvals,
    validate_approval_reference,
    validate_required_approvals,
    compute_approval_references_hash,
)

from .git_evidence import (
    load_git_evidence,
    validate_git_evidence,
    verify_git_state_allows_promotion,
    write_git_evidence,
    compute_git_evidence_hash,
)

from .gate_policy import collect_promotion_blockers
from .gate_decision import create_gate_decision, is_promotion_approved
from .gate_recorder import write_gate_decision
from .promotion_dispatcher import run_promotion_gate
```

Must not do:

```text
no filesystem writes on import
no Git command on import
no policy lookup on import
no network call on import
no promotion decision on import
no MCP runtime startup
```

---

## 39.2 PromotionGatePolicy Model

Implement `PromotionGatePolicy` in `promotion_models.py`.

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "promotion_gate_policy.schema.json"
policy_id: str
policy_hash: str
created_at: str
component_id: str = "AGENTX_PROMOTION_RELEASE_GATE"
source_component: str = "PromotionReleaseGate"
require_clean_git_state: bool = True
allow_expected_runtime_artifacts_only: bool = True
validation_freshness_minutes: int = 1440
require_compileall_pass: bool = True
require_pytest_pass: bool = True
require_schema_validation_pass: bool = True
require_command_exit_codes: bool = True
require_evidence_hashes: bool = True
require_review_report: bool = True
require_completion_record_for_approved: bool = True
require_policy_decision: bool = True
require_human_approval_when_listed: bool = True
require_patch_evidence_when_patch_session_exists: bool = True
require_tool_evidence_when_tool_session_exists: bool = True
allow_dry_run_without_policy: bool = True
allow_network: bool = False
allow_git_write: bool = False
allow_source_mutation: bool = False
allow_release_action: bool = False
allowed_runtime_roots: list[str]
non_overridable_blockers: list[str]
warnings: list[str]
errors: list[str]
```

Default policy values must be restrictive.

Acceptance:

```text
missing gate policy -> use restrictive default policy
gate policy schema validates
invalid gate policy enum/value fails validation
policy hash mismatch blocks actual promotion
policy cannot enable Git write, source mutation, network, or release action in this layer
```

---

## 39.3 PromotionEvidenceManifest Model

Implement `PromotionEvidenceManifest` in `promotion_models.py`.

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "promotion_evidence_manifest.schema.json"
manifest_id: str
manifest_hash: str
created_at: str
component_id: str
candidate_id: str
source_commit: str
decision_id: str
gate_decision_hash: str
idempotency_key: str
reviewed_commit: str | None
runtime_artifact_root: str
evidence_files: list[dict]
evidence_file_hashes: list[dict]
command_outputs: list[dict]
policy_decision_refs: list[str]
approval_refs: list[str]
patch_evidence_refs: list[str]
tool_evidence_refs: list[str]
git_evidence_refs: list[str]
failure_record_refs: list[str]
deviation_register: list[dict]
source_mutation_status: str
hash_status: str
final_decision: str
warnings: list[str]
errors: list[str]
```

Every `evidence_files` entry must include:

```text
path
sha256
artifact_type
required
created_at_or_verified_at
```

Acceptance:

```text
manifest references candidate_id, source_commit, and decision_id
manifest includes SHA-256 hashes for all final evidence artifacts
manifest includes deviation register even when empty
manifest hash excludes its own manifest_hash field
hash mismatch blocks promotion
missing required manifest entry blocks promotion
```

---

## 39.4 PromotionReviewReport Model

Implement `PromotionReviewReport` in `promotion_models.py`.

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "promotion_review_report.schema.json"
review_report_id: str
review_report_hash: str
created_at: str
component_id: str
candidate_id: str
source_commit: str
decision_id: str
reviewed_branch: str | None
reviewed_commit: str
review_environment: dict
commands_run: list[dict]
coverage_statuses: dict
blockers: list[dict]
high_issues: list[dict]
non_blocking_followups: list[dict]
deviation_register: list[dict]
evidence_manifest_path: str
evidence_manifest_sha256: str
completion_record_path: str | None
completion_record_sha256: str | None
implementation_rating: float | None
final_verdict: str
warnings: list[str]
errors: list[str]
```

Acceptance:

```text
review report records exact reviewed commit
review report records command text, exit codes, and summaries
review report records environment metadata
review report hash excludes its own review_report_hash field
missing review report blocks approval when policy requires it
changed review report hash invalidates prior approval
```

---

## 39.5 PromotionCompletionRecord Model

Implement `PromotionCompletionRecord` in `promotion_models.py`.

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "promotion_completion_record.schema.json"
completion_record_id: str
completion_record_hash: str
created_at: str
component_id: str
component_name: str
candidate_id: str
source_commit: str
decision_id: str
decision_status: str
decision: str
approved_at: str
approved_by: str | None
basis_documents: list[str]
validated_commands: list[dict]
validated_evidence: list[dict]
release_scope: list[str]
policy_decision_refs: list[str]
approval_refs: list[str]
risk_acceptance_refs: list[str]
git_evidence_refs: list[str]
patch_evidence_refs: list[str]
tool_evidence_refs: list[str]
evidence_manifest_path: str
evidence_manifest_sha256: str
review_report_path: str
review_report_sha256: str
deviation_register: list[dict]
unresolved_risks: list[dict]
final_decision: str = "DONE"
warnings: list[str]
errors: list[str]
```

Completion record write gate:

```text
write only if decision.status == APPROVED
write only if decision.decision == PROMOTE
write only if dry_run is false
write only if blockers list is empty
write only if evidence manifest exists and hash verifies
write only if review report exists and hash verifies
write only if candidate_hash verifies
write only if latest_gate_decision hash matches the approved decision
write only if policy allows completion record creation
```

Acceptance:

```text
completion record schema validates
completion record hash excludes completion_record_hash
completion record is never written for BLOCKED, INVALID, FAILED, EXPIRED, NEEDS_APPROVAL, NEEDS_GOVERNANCE, NEEDS_VALIDATION, or DRY_RUN decisions
completion record hash mismatch invalidates DONE evidence
```

---

## 39.6 Dependency Adapter Contracts

Create:

```text
tools/agentx_evolve/promotion/dependency_adapters.py
```

This file isolates optional upstream dependencies so the gate fails closed when a dependency is unavailable, unstable, or missing evidence.

Required functions:

```python
check_policy_dependency(
    candidate: ReleaseCandidate,
    caller_role: str,
    policy_context: dict,
    dry_run: bool,
) -> dict

check_human_approval_dependency(
    candidate: ReleaseCandidate,
    approvals: list[ApprovalReference],
) -> dict

check_patch_evidence_dependency(
    candidate: ReleaseCandidate,
    repo_root: Path,
) -> dict

check_tool_evidence_dependency(
    candidate: ReleaseCandidate,
    repo_root: Path,
) -> dict

check_git_dependency(
    candidate: ReleaseCandidate,
    git_evidence: GitEvidence | None,
    repo_root: Path,
) -> dict

classify_failure_dependency(
    blocker: dict,
) -> dict
```

Required return shape:

```json
{
  "status": "PASS|BLOCKED|FAILED|NOT_AVAILABLE|NOT_APPLICABLE",
  "failure_class": "string|null",
  "reason": "string",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Fail-closed rules:

```text
Policy dependency unavailable -> BLOCK actual promotion
Human approval dependency unavailable -> NEEDS_APPROVAL if approval is required
Patch evidence dependency unavailable -> BLOCK if patch_session_id exists
Tool evidence dependency unavailable -> BLOCK if tool_session_id exists
Git dependency unavailable -> BLOCK actual promotion unless policy explicitly allows documented GitEvidence-only mode
Failure Taxonomy dependency unavailable -> use local promotion failure classes and record warning; do not approve by ignoring classification
```

---

## 39.7 Schema Validation Utility

Create:

```text
tools/agentx_evolve/promotion/schema_validation.py
tools/agentx_evolve/tests/validate_promotion_schemas.py
```

Required behavior:

```text
validate every promotion schema against at least one valid object
reject at least one missing-required-field object per schema
reject at least one invalid-enum object per schema
validate final evidence manifest example
validate review report example
validate completion record example
exit code 0 only when all schema checks pass
non-zero exit code if any schema is missing, malformed, or accepts invalid data
```

Required command:

```bash
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_promotion_schemas.py
```

This command must require no network, no Git write, no MCP runtime, no LLM, and no human UI.

---

## 39.8 Canonical Hashing Rules

Use deterministic canonical JSON hashing for object hashes.

Rules:

```text
sort keys
use compact separators
normalize paths to POSIX-style strings
exclude self-hash fields from their own hash
exclude volatile warning text only if explicitly marked non-hashable
include candidate_id and source_commit in all promotion evidence hashes where applicable
include idempotency_key in decision/report/completion hashes
```

Self-hash fields to exclude:

```text
candidate_hash
validation_evidence.evidence_hash
risk_acceptance.risk_acceptance_hash
approval_reference.approval_hash, when computing that approval itself
git_evidence.git_evidence_hash
gate_policy.policy_hash
gate_decision.decision hash field, if later added
manifest.manifest_hash
review_report.review_report_hash
completion_record.completion_record_hash
```

File hashing:

```text
SHA-256 is mandatory for evidence files
use Python standard library hashlib
missing hash is a blocker
hash mismatch is a blocker
manual evidence modification after approval invalidates previous approval
```

---

## 39.9 Runtime Artifact Boundary and Deviation Register

Approved runtime root:

```text
.agentx-init/promotion/
```

Allowed cross-layer read-only evidence roots:

```text
.agentx-init/security/
.agentx-init/policy/
.agentx-init/patches/
.agentx-init/tool_calls/
.agentx-init/git/
.agentx-init/human_review/
```

The Promotion / Release Gate may read cross-layer evidence, but must not write into those roots unless the owning layer explicitly defines that write as part of its contract.

Any runtime artifact outside `.agentx-init/promotion/` must be recorded in the deviation register with:

```text
id
area
path
reason
safety_impact
owning_layer
compensating_control
accepted_status
```

Unrecorded runtime artifact writes outside `.agentx-init/promotion/` block DONE.

---

## 39.10 Fresh-Clone Validation Contract

The implementation must be validated from a fresh checkout or clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_promotion_schemas.py
git status --short
```

Required recorded metadata:

```text
reviewed commit
reviewed branch
review timestamp UTC
OS
Python version
pytest version
initial git status
final git status
command text
command exit code
command summary
output artifact path, if stored
output artifact sha256, if stored
```

A validation command marked PASS must have exit code 0. Missing exit code blocks DONE.

---

## 39.11 Expanded Dependency-Unavailable Tests

Add these tests to `test_promotion_integration_cases.py` or `test_promotion_negative_cases.py`:

```text
test_policy_dependency_unavailable_blocks_actual_promotion
test_policy_dependency_unavailable_allows_dry_run_only_when_no_release_action
test_human_review_dependency_missing_returns_needs_approval_when_required
test_patch_dependency_missing_blocks_when_patch_session_id_present
test_tool_dependency_missing_blocks_when_tool_session_id_present
test_git_dependency_missing_blocks_actual_promotion
test_failure_taxonomy_dependency_missing_uses_local_failure_class_without_approval_bypass
test_cross_layer_evidence_hash_mismatch_blocks
test_unrecorded_runtime_artifact_boundary_exception_blocks_done
test_completion_record_requires_latest_decision_hash_match
```

---

## 39.12 Final Freeze Rule

This v3 implementation spec is frozen for coding-agent handoff.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes, added non-required examples
MINOR: additive optional helper functions that do not weaken safety
MAJOR: changed promotion decision vocabulary, changed blocker precedence, changed approval rules, changed Git/release behavior, changed evidence requirements
```

Blocked without major revision:

```text
allowing promotion with failed validation
allowing promotion with missing validation
allowing promotion with stale validation
allowing promotion with missing required approval
allowing promotion with blocking risk
allowing promotion with policy denial
allowing promotion with invalid Git evidence
allowing Git write in this layer
allowing source mutation in this layer
allowing network by default
allowing completion record for blocked candidate
removing evidence hashes
removing review report
removing completion record for approved candidate
```
---

# 40. v4 Final Promotion-Safety Hardening

These requirements are part of the final implementation spec. They close the remaining handoff gaps from v3 and must be implemented unless explicitly marked as not applicable in the future post-implementation review.

---

## 40.1 Gate Decision Hash Requirement

`PromotionGateDecision` must include an explicit hash field:

```python
gate_decision_hash: str
```

Hashing rules:

```text
compute gate_decision_hash from canonical JSON
exclude gate_decision_hash from its own hash
include candidate_id
include source_commit
include idempotency_key
include decision
include status
include blocking_failures
include required approval status
include validation status
include risk status
include policy status
include patch/tool/git/expiry statuses
include evidence manifest and review report references when present
```

Blocking rules:

```text
missing gate_decision_hash blocks completion record creation
gate_decision_hash mismatch blocks promotion approval finalization
latest_gate_decision hash must match the decision used to write the completion record
manual modification of latest_gate_decision.json after approval invalidates prior completion evidence
```

Required tests:

```text
test_gate_decision_hash_excludes_self_hash_field
test_gate_decision_hash_changes_when_blockers_change
test_completion_record_requires_latest_decision_hash_match
test_modified_latest_decision_invalidates_completion_record
```

---

## 40.2 Superseded Candidate Rules

A candidate may be superseded by a newer candidate. Supersession must be explicit and evidence-backed.

Add optional fields to `ReleaseCandidate` if not already present:

```python
superseded_by_candidate_id: str | None
superseded_at: str | None
supersession_reason: str | None
```

Rules:

```text
a candidate with superseded_by_candidate_id is not promotable
a candidate that has been superseded must return BLOCKED, not APPROVED
supersession cannot be ignored by human approval
supersession must be recorded in blockers and gate decision evidence
```

Failure class:

```text
PROMOTION_CANDIDATE_SUPERSEDED
```

Required tests:

```text
test_superseded_candidate_blocks_promotion
test_human_approval_cannot_override_superseded_candidate
test_superseded_candidate_failure_class_recorded
```

---

## 40.3 Approval Revocation and Quorum Rules

`ApprovalReference` must support revocation and quorum-sensitive release scopes.

Add fields to `ApprovalReference`:

```python
revoked: bool = False
revoked_at: str | None
revoked_by: str | None
revocation_reason: str | None
```

Add fields to `PromotionGatePolicy`:

```python
required_approval_quorum: int = 1
require_distinct_approvers: bool = True
high_risk_approval_quorum: int = 2
critical_risk_approval_quorum: int = 2
```

Rules:

```text
revoked approval is invalid
revoked approval blocks if it was required for the candidate
expired approval is invalid
approval from wrong candidate blocks
approval from wrong commit blocks
approval scope must cover the candidate release scope
quorum must be satisfied when policy requires multiple approvals
if require_distinct_approvers is true, duplicate approver IDs do not satisfy quorum
human approval cannot override hash mismatch, failed validation, policy denial, supersession, or invalid Git evidence
```

Failure classes:

```text
PROMOTION_APPROVAL_REVOKED
PROMOTION_APPROVAL_QUORUM_MISSING
PROMOTION_APPROVAL_SCOPE_INSUFFICIENT
```

Required tests:

```text
test_revoked_approval_blocks_promotion
test_required_approval_quorum_missing_blocks
test_duplicate_approver_does_not_satisfy_distinct_quorum
test_approval_scope_must_cover_release_scope
```

---

## 40.4 Release-Scope Containment Rules

Promotion approval must be limited to the declared candidate scope.

`ReleaseCandidate` must declare a release scope either directly or through the changed files/schemas/tests lists.

Add field:

```python
release_scope: list[str]
```

Rules:

```text
release_scope must be non-empty for actual promotion
changed_files, changed_schemas, and changed_tests must be contained within release_scope or explicitly justified
Git diff evidence must not include files outside release_scope unless policy permits and records a deviation
completion record release_scope must match candidate release_scope
approval scope must cover release_scope
```

Failure class:

```text
PROMOTION_RELEASE_SCOPE_MISMATCH
```

Required tests:

```text
test_release_scope_required_for_actual_promotion
test_git_diff_outside_release_scope_blocks
test_completion_record_release_scope_matches_candidate
test_approval_scope_must_cover_release_scope
```

---

## 40.5 Minimum Patch Evidence Verification Contract

When `candidate.patch_session_id` is present, the patch evidence adapter must verify a minimum evidence shape rather than only checking that a file exists.

Minimum required patch evidence fields:

```text
patch_session_id
component_id
source_commit or pre_patch_commit
result_commit or post_patch_commit, if patch changed source
status
final_decision
patch_files_changed
validation_refs
rollback_required
rollback_status, if rollback_required=true
evidence_hash or evidence_file_sha256
unresolved_blockers
```

Rules:

```text
missing patch evidence blocks when patch_session_id exists
patch evidence status must be PASS, VALIDATED, or DONE according to owning-layer vocabulary
patch evidence commit must match candidate source_commit or documented resulting commit
unresolved patch blockers block promotion
rollback_required without successful rollback evidence blocks promotion
patch evidence hash mismatch blocks promotion
```

Failure classes:

```text
PROMOTION_PATCH_EVIDENCE_INVALID
PROMOTION_PATCH_ROLLBACK_EVIDENCE_MISSING
PROMOTION_PATCH_COMMIT_MISMATCH
```

Required tests:

```text
test_patch_evidence_missing_blocks_when_patch_session_id_present
test_patch_evidence_unresolved_blocker_blocks
test_patch_evidence_commit_mismatch_blocks
test_patch_rollback_required_without_evidence_blocks
```

---

## 40.6 Minimum Tool / MCP Evidence Verification Contract

When `candidate.tool_session_id` is present, the Tool / MCP Adapter evidence adapter must verify a minimum evidence shape rather than only checking that a file exists.

Minimum required Tool / MCP evidence fields:

```text
tool_session_id
component_id
validated_commit or reviewed_commit
tool_call_history_ref
tool_result_history_ref
blocked_tool_history_ref, if blocked calls occurred
invalid_tool_history_ref, if invalid calls occurred
mcp_exposure_status
policy_integration_status
sandbox_integration_status
final_decision or validation_status
evidence_hash or evidence_file_sha256
unresolved_blockers
```

Rules:

```text
missing tool evidence blocks when tool_session_id exists
tool evidence with unresolved BLOCKER blocks promotion
mutating MCP exposure violation blocks promotion
policy or sandbox bypass in tool evidence blocks promotion
tool evidence hash mismatch blocks promotion
blocked/invalid tool calls are allowed only if reviewed and non-blocking
```

Failure classes:

```text
PROMOTION_TOOL_EVIDENCE_INVALID
PROMOTION_TOOL_UNRESOLVED_BLOCKER
PROMOTION_TOOL_MCP_EXPOSURE_UNSAFE
```

Required tests:

```text
test_tool_evidence_missing_blocks_when_tool_session_id_present
test_tool_evidence_unresolved_blocker_blocks
test_mutating_mcp_exposure_violation_blocks_promotion
test_tool_evidence_hash_mismatch_blocks
```

---

## 40.7 UTC Timestamp and Freshness Rules

All timestamps must be UTC ISO-8601 strings.

Rules:

```text
use timezone-aware UTC timestamps
freshness is measured from validation_completed_at, not created_at
validation_completed_at must be greater than or equal to validation_started_at
future timestamps beyond allowed clock skew are invalid
default allowed clock skew is 5 minutes
invalid timestamp parse blocks actual promotion
```

Add field to `PromotionGatePolicy`:

```python
allowed_clock_skew_minutes: int = 5
```

Failure classes:

```text
PROMOTION_TIMESTAMP_INVALID
PROMOTION_VALIDATION_TIME_INVALID
```

Required tests:

```text
test_validation_freshness_uses_completed_at
test_future_timestamp_beyond_clock_skew_blocks
test_validation_completed_before_started_blocks
test_invalid_timestamp_format_blocks_actual_promotion
```

---

## 40.8 Safe Lock Handling Rules

The promotion lock prevents concurrent writes to final decision and completion artifacts.

Add fields to `PromotionGatePolicy`:

```python
lock_timeout_seconds: int = 10
stale_lock_age_seconds: int = 900
allow_stale_lock_recovery: bool = False
```

Rules:

```text
failure to acquire lock returns FAILED or BLOCKED with evidence
stale lock must not be deleted by default
stale lock recovery requires explicit policy flag
stale lock recovery must move the old lock to a quarantine artifact under .agentx-init/promotion/
stale lock recovery must be recorded in deviation_register
lock handling must never use rm -rf or broad cleanup
```

Failure class:

```text
PROMOTION_LOCK_UNAVAILABLE
```

Required tests:

```text
test_lock_failure_blocks_or_fails_with_evidence
test_stale_lock_not_deleted_by_default
test_stale_lock_recovery_requires_policy_flag
test_lock_cleanup_never_removes_runtime_root
```

---

## 40.9 Post-Approval Evidence Immutability and Revalidation

After an approval or completion record is written, final evidence becomes immutable for that decision.

Rules:

```text
changed evidence hash invalidates the previous approval
changed latest_gate_decision invalidates the previous completion record
changed release_candidate invalidates the previous approval
changed validation_evidence invalidates the previous approval
changed approval_references invalidates the previous approval
changed git_evidence invalidates the previous approval
manual edits after approval require a new gate decision
new gate decision must record a new timestamp and hash set
completion record must not be silently rewritten
```

Required function:

```python
revalidate_promotion_evidence(
    completion_record: PromotionCompletionRecord,
    repo_root: Path,
) -> list[str]
```

Required tests:

```text
test_changed_candidate_hash_invalidates_approval
test_changed_validation_evidence_hash_invalidates_approval
test_changed_approval_hash_invalidates_approval
test_changed_git_evidence_hash_invalidates_approval
test_completion_record_not_silently_rewritten
```

---

## 40.10 v4 Schema and Test Expansion

The schema and test set must include the v4 additions.

Schemas must represent and validate:

```text
gate_decision_hash
superseded_by_candidate_id
superseded_at
supersession_reason
release_scope
approval revoked fields
approval quorum policy fields
clock skew policy field
lock policy fields
patch evidence dependency result shape
tool evidence dependency result shape
```

Additional tests required:

```text
test_promotion_schemas_accept_v4_fields
test_promotion_schemas_reject_missing_gate_decision_hash
test_promotion_schemas_reject_invalid_revoked_field_type
test_promotion_schemas_reject_invalid_release_scope
test_promotion_schemas_reject_invalid_quorum_values
test_promotion_schemas_reject_invalid_lock_policy_values
```

---

## 40.11 v4 Additional Drift Blockers

Reject or revise the implementation if it:

```text
approves a superseded candidate
approves with revoked required approval
approves without required approval quorum
approves a release scope not covered by approvals
approves Git diff outside release scope without recorded deviation
approves with missing or mismatched gate_decision_hash
approves with latest_gate_decision hash mismatch
approves with patch evidence that has unresolved blockers
approves with tool evidence that has unresolved blockers
approves after evidence changed without creating a new gate decision
deletes stale lock destructively
silently rewrites a completion record
```

---

## 40.12 v4 Final DONE Additions

The layer may be marked DONE only if the v4 additions are proven:

```text
gate_decision_hash exists and verifies
latest_gate_decision hash matches approved decision
superseded candidates block
revoked approvals block
approval quorum works
release scope containment works
patch evidence minimum shape is verified
tool evidence minimum shape is verified
UTC/freshness rules work
lock stale-handling is conservative
post-approval evidence revalidation works
v4 schema additions validate
v4 negative tests pass
```

---

# 41. Final Rating

This v4 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, files, schemas, classes, functions, runtime artifacts, promotion gate model, release candidate model, validation evidence model, risk acceptance model, approval lookup and validation, Git evidence model, gate policy model, evidence manifest model, review report model, completion record model, dependency adapter contracts, schema validation utility, gate decision creation and recording, blocking and expiry rules, dry-run semantics, idempotency and locking, integrations, test cases, fresh-clone validation, implementation order, acceptance criteria, Definition of Done, Go/No-Go rules, scoring caps, and final frozen handoff criteria, plus explicit decision hashing, supersession handling, approval revocation/quorum, release-scope containment, minimum cross-layer evidence verification, UTC freshness rules, conservative lock handling, and post-approval evidence revalidation.
```
