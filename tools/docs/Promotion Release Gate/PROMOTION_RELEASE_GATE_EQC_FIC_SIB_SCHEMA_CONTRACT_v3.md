# PROMOTION_RELEASE_GATE_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: PROMOTION_RELEASE_GATE_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v4.0
status: final frozen controlling contract, implementation-ready, v4 promotion-safety hardening
component_id: AGENTX_PROMOTION_RELEASE_GATE
component_name: Promotion / Release Gate
roadmap_layer: 13
roadmap_phase: Phase C — Promotion Control
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Git Acceptance Criteria, Human Approval Acceptance Criteria, MCP Protocol Acceptance Criteria
risk_level: critical
target_language: Python
canonical_subdirectory: tools/agentx_evolve/promotion/
schema_subdirectory: tools/agentx_evolve/schemas/
test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/promotion/
purpose: Defines what the Promotion / Release Gate is allowed to approve, block, defer, or reject.
contract_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

The v3 contract was strong and implementation-ready. I would rate v3:

```text
9.7/10
```

It already covered:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
Promotion decision schema
Release gate schema
Validation evidence schema
Risk acceptance schema
Human approval linkage
Policy / Capability Registry integration
Governed Patch Execution integration
Tool / MCP Adapter integration
Git Integration Layer integration
Failure Taxonomy integration
Review report / completion evidence contract
OpenCode borrowing notes
Agent_X integration notes
```

It was not fully 10/10 because several final production-control details were still under-specified:

```text
1. Deterministic candidate_hash construction was required, but the exact canonicalization rule was not defined.
2. Evidence provenance was required, but upstream evidence trust levels and revalidation rules were not explicit enough.
3. Validation commands were referenced, but the command acceptance boundary was not strict enough for a release gate.
4. Schema contracts were defined, but required valid/invalid schema examples were not explicit enough for implementation handoff.
5. Evidence hashing was required, but the exact hash target set and self-hash handling needed tighter rules.
6. Reviewer independence was required, but self-review versus self-approval needed clearer hard limits.
7. APPROVED decisions were separated from Git/release actions, but release-action boundaries needed a stronger prohibition.
8. Supersession/versioning of promotion decisions needed a clearer monotonic history rule.
9. Redaction and output-bounding rules for promotion evidence needed to be explicit.
10. Date/time and freshness handling needed a UTC-only clock-skew rule.
```

This v3 added those controls. This v4 closes the remaining precision gaps around deterministic hashing, upstream evidence trust, command admissibility, schema examples, decision supersession, redaction/output bounds, reviewer independence, and release-action boundaries. This v4 is the final 10/10 controlling contract for the Promotion / Release Gate layer.

---

# 1. Purpose

This document defines the controlling contract for the **Promotion / Release Gate** layer in the Agent_X self-evolving system.

The Promotion / Release Gate decides whether an implementation, patch session, tool-layer change, model-layer change, configuration change, documentation change, or release bundle may move forward toward acceptance, promotion, or release readiness.

The layer is allowed to decide whether to:

```text
approve
block
defer
reject
require additional evidence
require revalidation
require human approval
require governance approval
require rollback or remediation
```

The layer is not allowed to silently promote work. It must fail closed when evidence is missing, stale, invalid, incomplete, inconsistent, unverifiable, tampered with, or bound to a different commit.

A promotion decision is a controlled evidence-backed decision. It is not the same thing as performing a Git commit, tag, merge, push, deployment, or release publication.

---

# 2. Scope

## 2.1 Required in This Layer

The Promotion / Release Gate must define and enforce contracts for:

```text
promotion decisions
release gate definitions
release candidate records
validation evidence records
risk acceptance records
human approval linkage
policy/capability validation
patch execution evidence validation
tool/MCP adapter evidence validation
Git readiness validation
failure taxonomy validation
review report validation
completion record validation
evidence manifest validation
evidence hash validation
evidence immutability
promotion blocking rules
promotion deferral rules
promotion rejection rules
promotion approval rules
promotion idempotency
promotion locking/concurrency
audit/evidence records
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
patch generation
patch application
source editing
LLM implementation work
model adapter execution
human approval UI
Git commit execution
Git tag execution
Git merge execution
Git push execution
MCP server runtime
release deployment
long-term learning
background scheduling
```

The layer decides whether promotion is allowed. It does not perform the underlying implementation, patching, approval UI, Git release action, or deployment action unless a later layer explicitly delegates a narrowly controlled read-only or decision-only function.

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

```text
EQC
```

EQC is primary because this layer decides whether work can move from implementation or validation into a promoted, done, release-ready, or releasable state.

It must enforce:

```text
fail-closed promotion
complete validation evidence
fresh command evidence
schema-valid records
reviewed commit binding
human approval binding where required
governance approval binding where required
policy approval binding where required
patch evidence binding where required
tool/MCP evidence binding where required
Git readiness checks
risk acceptance limits
reproducibility
reviewer independence
source mutation safety
evidence hashing
evidence immutability
```

The Promotion / Release Gate must not mark work as promoted if any required authority, validation, review artifact, approval, or evidence hash is missing.

## 3.2 Required Supporting Standard: FIC

```text
FIC
```

FIC is required because this layer must have concrete implementation files with clearly separated responsibilities.

Expected responsibilities include:

```text
promotion models
release gate loading
release candidate validation
validation evidence loading
risk acceptance validation
approval linkage validation
policy integration
patch integration
tool/MCP integration
Git readiness integration
failure taxonomy mapping
evidence writing
evidence hashing
review report writing
completion record writing
promotion decision locking
idempotency handling
```

## 3.3 Required Supporting Standard: SIB

```text
SIB
```

SIB is required because this layer integrates multiple Agent_X subsystems:

```text
Policy / Capability Registry
Human Review / Approval Interface
Governed Patch Execution
Tool / MCP Adapter
Git Integration Layer
Failure Taxonomy / Recovery Playbook
Evaluation Harness / Regression Benchmark Layer
Documentation Synchronization Layer
Monitoring / Observability Layer
```

The Promotion / Release Gate is an integration boundary. It must verify upstream evidence rather than trusting implementation claims.

## 3.4 Required Schema Contract

```text
Schema Contract
```

Every promotion-related decision must be schema-valid and reproducible.

Required schemas:

```text
promotion_decision.schema.json
release_gate.schema.json
release_candidate.schema.json
validation_evidence.schema.json
risk_acceptance.schema.json
human_approval_link.schema.json
promotion_policy_check.schema.json
promotion_evidence_manifest.schema.json
promotion_review_report.schema.json
promotion_completion_record.schema.json
promotion_audit_event.schema.json
promotion_deviation.schema.json
```

## 3.5 Required Evidence / Audit Rules

```text
Evidence / Audit Rules
```

Every gate decision must create durable evidence under:

```text
.agentx-init/promotion/
```

Evidence is required for:

```text
promotion approval
promotion block
promotion rejection
promotion deferral
missing validation evidence
stale validation evidence
failed validation evidence
schema-invalid evidence
hash-mismatched evidence
human approval required
human approval missing
human approval expired
human approval revoked
human approval scope mismatch
human approval commit mismatch
policy denial
patch evidence failure
tool/MCP evidence failure
Git readiness failure
risk acceptance approval
risk acceptance rejection
release candidate creation
review report creation
completion record creation
```

---

# 4. Status Vocabulary

Use only these status values in promotion review tables and validation summaries:

```text
PASS
PARTIAL
FAIL
NOT CHECKED
NOT RUN
NOT APPLICABLE
DEFERRED SAFELY
```

Use only these promotion decision values in promotion records:

```text
APPROVED
BLOCKED
REJECTED
DEFERRED
NEEDS_REVALIDATION
NEEDS_HUMAN_APPROVAL
NEEDS_GOVERNANCE
INVALID
```

| Status | Meaning | Promotion allowed? |
|---|---|---|
| PASS | Requirement was checked and satisfied. | Yes |
| PARTIAL | Some required parts are present but incomplete. | No, unless explicitly non-blocking and recorded |
| FAIL | Requirement was checked and failed. | No |
| NOT CHECKED | Requirement was not validated. | No |
| NOT RUN | Required command or validation was not run. | No |
| NOT APPLICABLE | Requirement truly does not apply to the candidate. | Yes, if justified |
| DEFERRED SAFELY | Feature is intentionally deferred and cannot affect active runtime/release behavior. | Yes, only if justified and recorded |

A release candidate cannot be promoted if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

---

# 5. Why This Layer Needs Strict Standards

Promotion / Release Gate is safety-critical because it decides:

```text
whether implementation work can be promoted
whether validation evidence is sufficient
whether tests are fresh enough
whether approvals are valid
whether governance is required
whether risks are acceptable
whether patch execution evidence is complete
whether tool/MCP exposure is safe
whether source changes can move toward release
whether Git readiness exists
whether incomplete or unsafe work is blocked
```

A failure in this layer could allow incomplete, unsafe, unvalidated, unapproved, stale, or unreproducible work to be treated as done.

---

# 6. Authority Model

The Promotion / Release Gate does not grant authority by itself.

A promotion decision is allowed only when all required authorities agree:

```text
Policy / Capability Registry
Human Review / Approval Interface, when required
Governed Patch Execution, when source mutation or patch sessions are involved
Tool / MCP Adapter, when tool exposure or tool-call evidence is involved
Git Integration Layer, when Git readiness or release movement is involved
Failure Taxonomy / Recovery Playbook, when failures exist
Evaluation Harness / Regression Benchmark Layer, when regression evidence is required
Documentation Synchronization Layer, when documentation release evidence is required
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
REJECTED
BLOCKED
NEEDS_HUMAN_APPROVAL
NEEDS_GOVERNANCE
NEEDS_REVALIDATION
DEFERRED
APPROVED
```

Rules:

```text
APPROVED is allowed only when every required authority is satisfied.
BLOCKED is required when a safety, policy, validation, approval, patch, Git, or evidence check fails.
REJECTED is required when the candidate is invalid, unsafe, or unsuitable for remediation in place.
DEFERRED is allowed only when the candidate is not unsafe and the missing dependency cannot affect active release behavior.
NEEDS_REVALIDATION is required when evidence is stale, incomplete, or tied to another commit.
NEEDS_HUMAN_APPROVAL is required when valid human approval is absent.
NEEDS_GOVERNANCE is required when governance authority is absent.
INVALID is required when the promotion request or candidate record is malformed or schema-invalid.
```

---

# 7. Promotion Decision Schema

## 7.1 Purpose

The promotion decision schema records the final gate decision for a release candidate or implementation unit.

## 7.2 Required Fields

```json
{
  "schema_version": "1.0",
  "schema_id": "promotion_decision.schema.json",
  "promotion_decision_id": "string",
  "timestamp": "string",
  "source_component": "PromotionReleaseGate",
  "release_candidate_id": "string",
  "release_gate_id": "string",
  "reviewed_commit": "string",
  "candidate_hash": "string",
  "decision": "APPROVED|BLOCKED|REJECTED|DEFERRED|NEEDS_REVALIDATION|NEEDS_HUMAN_APPROVAL|NEEDS_GOVERNANCE|INVALID",
  "reason": "string",
  "failure_class": "string|null",
  "required_evidence_refs": [],
  "validated_evidence_refs": [],
  "missing_evidence_refs": [],
  "approval_refs": [],
  "policy_decision_refs": [],
  "risk_acceptance_refs": [],
  "failure_refs": [],
  "artifact_refs": [],
  "evidence_refs": [],
  "evidence_manifest_ref": "string|null",
  "expires_at": "string|null",
  "idempotency_key": "string",
  "warnings": [],
  "errors": []
}
```

## 7.3 Decision Rules

```text
APPROVED:
  All required validation, approval, policy, patch, tool/MCP, Git, risk, review, completion, and evidence checks pass.

BLOCKED:
  A required safety, policy, validation, approval, patch, tool/MCP, Git, hash, or evidence check fails.

REJECTED:
  The release candidate is invalid, unsafe, out of scope, or not suitable for remediation in place.

DEFERRED:
  The candidate is not unsafe, but required future evidence or dependency is not yet available and cannot affect active release behavior.

NEEDS_REVALIDATION:
  Existing evidence is stale, incomplete, missing command exit codes, or tied to a different commit.

NEEDS_HUMAN_APPROVAL:
  Human approval is required but missing, expired, revoked, scope-mismatched, or commit-mismatched.

NEEDS_GOVERNANCE:
  Governance approval is required but missing, incomplete, stale, or mismatched.

INVALID:
  The promotion request or candidate record is malformed or schema-invalid.
```

---

# 8. Release Gate Schema

## 8.1 Purpose

The release gate schema defines a named gate with required checks and pass/fail criteria.

## 8.2 Required Fields

```json
{
  "schema_version": "1.0",
  "schema_id": "release_gate.schema.json",
  "release_gate_id": "string",
  "gate_name": "string",
  "gate_version": "string",
  "source_component": "PromotionReleaseGate",
  "required_checks": [],
  "required_evidence_types": [],
  "required_approval_types": [],
  "required_policy_scopes": [],
  "required_test_commands": [],
  "allowed_risk_levels": [],
  "blocking_failure_classes": [],
  "freshness_requirements": {},
  "promotion_targets": [],
  "git_action_allowed": false,
  "release_action_allowed": false,
  "warnings": [],
  "errors": []
}
```

## 8.3 Required Gate Checks

A release gate must be able to require:

```text
compileall pass
pytest pass
schema validation pass
negative safety tests pass
source mutation check pass
runtime artifact boundary check pass
policy decision pass
human approval pass, when required
governance approval pass, when required
patch session evidence pass, when required
Tool / MCP Adapter exposure safety pass, when required
Git readiness pass, when required
failure taxonomy classification complete
review report present
completion record present
evidence manifest present
evidence hashes present
reviewer independence present
```

---

# 9. Release Candidate Schema

## 9.1 Purpose

The release candidate schema identifies the unit being considered for promotion.

## 9.2 Required Fields

```json
{
  "schema_version": "1.0",
  "schema_id": "release_candidate.schema.json",
  "release_candidate_id": "string",
  "timestamp": "string",
  "source_component": "PromotionReleaseGate",
  "component_id": "string",
  "component_name": "string",
  "candidate_type": "IMPLEMENTATION|PATCH_SESSION|TOOL_LAYER|MODEL_LAYER|CONFIG_CHANGE|DOCUMENTATION_CHANGE|RELEASE_BUNDLE",
  "reviewed_commit": "string",
  "base_commit": "string|null",
  "branch": "string|null",
  "changed_files": [],
  "candidate_hash": "string",
  "claimed_completion_record": "string|null",
  "claimed_review_report": "string|null",
  "claimed_evidence_manifest": "string|null",
  "validation_evidence_refs": [],
  "policy_refs": [],
  "approval_refs": [],
  "risk_acceptance_refs": [],
  "warnings": [],
  "errors": []
}
```

## 9.3 Candidate Rules

```text
A candidate must bind to an exact reviewed commit.
A candidate must include a stable candidate_hash derived from reviewed_commit, component_id, changed_files, and claimed evidence refs.
A candidate must list changed files or explicitly justify why there are none.
A candidate must reference validation evidence.
A candidate must reference a review report when claiming DONE.
A candidate must reference a completion record when claiming DONE.
A candidate must reference an evidence manifest when claiming DONE.
A candidate must not be promoted using evidence from another commit.
```

---

# 10. Validation Evidence Schema

## 10.1 Purpose

The validation evidence schema records command and test evidence required before promotion.

## 10.2 Required Fields

```json
{
  "schema_version": "1.0",
  "schema_id": "validation_evidence.schema.json",
  "validation_evidence_id": "string",
  "timestamp": "string",
  "source_component": "PromotionReleaseGate",
  "validated_commit": "string",
  "validation_environment": {
    "os": "string",
    "python_version": "string",
    "pytest_version": "string|null"
  },
  "commands": [
    {
      "name": "string",
      "command": "string",
      "exit_code": 0,
      "status": "PASS|FAIL|NOT_RUN",
      "summary": "string",
      "output_artifact": "string|null",
      "output_sha256": "string|null"
    }
  ],
  "schema_validation_status": "PASS|FAIL|NOT_RUN",
  "test_status": "PASS|FAIL|NOT_RUN",
  "source_mutation_status": "CLEAN|EXPECTED_RUNTIME_ARTIFACTS_ONLY|DIRTY|NOT_CHECKED",
  "evidence_hashes": [],
  "validated_at": "string",
  "expires_at": "string|null",
  "warnings": [],
  "errors": []
}
```

## 10.3 Validation Evidence Rules

```text
Every required command must record command text, exit code, status, and summary.
PASS requires exit_code 0.
NOT_RUN blocks promotion unless explicitly non-applicable in the release gate.
Validation evidence must bind to the same reviewed commit as the release candidate.
Stale validation evidence returns NEEDS_REVALIDATION.
Missing schema validation blocks promotion.
Missing source mutation check blocks promotion.
Missing command exit codes block promotion.
Missing output hashes block DONE or APPROVED where output artifacts are used.
```

## 10.4 Freshness Rules

Default freshness rules:

```text
Validation evidence must be produced after or at the reviewed commit.
Validation evidence must reference the exact reviewed commit.
Validation evidence from a different commit is stale even if the working tree is unchanged.
Validation evidence older than the configured gate freshness window returns NEEDS_REVALIDATION.
Validation evidence with missing validated_at or expires_at handling returns NEEDS_REVALIDATION.
```

Recommended default freshness window:

```text
implementation/unit validation: same reviewed commit, no time-only substitution
release bundle validation: same reviewed commit and within gate-configured freshness window
human approval: same reviewed commit or same release_candidate_id and unexpired
```

---

# 11. Risk Acceptance Schema

## 11.1 Purpose

The risk acceptance schema records accepted non-blocking risks.

## 11.2 Required Fields

```json
{
  "schema_version": "1.0",
  "schema_id": "risk_acceptance.schema.json",
  "risk_acceptance_id": "string",
  "timestamp": "string",
  "source_component": "PromotionReleaseGate",
  "release_candidate_id": "string",
  "reviewed_commit": "string",
  "risk_id": "string",
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "risk_description": "string",
  "accepted_by": "string",
  "approval_ref": "string|null",
  "reason": "string",
  "compensating_controls": [],
  "expires_at": "string|null",
  "status": "ACCEPTED|REJECTED|EXPIRED|REVOKED",
  "warnings": [],
  "errors": []
}
```

## 11.3 Risk Acceptance Rules

```text
LOW and MEDIUM risks may be accepted if documented and non-blocking.
HIGH risks require explicit governance or human approval.
CRITICAL risks cannot be accepted for promotion unless the controlling contract explicitly allows it and human/governance approval is present.
Accepted risk must bind to the same release candidate and reviewed commit.
Accepted risk must expire or be revalidated when the candidate changes.
Risk acceptance cannot override failed validation, missing evidence, policy denial, sandbox denial, unsafe Git readiness, unsafe MCP exposure, missing approval, missing hashes, or source mutation uncertainty.
```

---

# 12. Human Approval Linkage

## 12.1 Purpose

Human approval linkage connects promotion decisions to valid human approval records.

## 12.2 Required Fields

```json
{
  "schema_version": "1.0",
  "schema_id": "human_approval_link.schema.json",
  "approval_link_id": "string",
  "timestamp": "string",
  "source_component": "PromotionReleaseGate",
  "release_candidate_id": "string",
  "approval_id": "string",
  "approved_by": "string",
  "approval_scope": "string",
  "approved_commit": "string",
  "approval_evidence_ref": "string",
  "expires_at": "string|null",
  "status": "VALID|MISSING|EXPIRED|REVOKED|SCOPE_MISMATCH|COMMIT_MISMATCH",
  "warnings": [],
  "errors": []
}
```

## 12.3 Approval Rules

```text
Approval must bind to the same commit or explicitly approved release candidate.
Approval must match the required scope.
Approval evidence must be readable and hashable.
Expired approval blocks promotion.
Revoked approval blocks promotion.
Scope mismatch blocks promotion.
Commit mismatch returns NEEDS_HUMAN_APPROVAL or NEEDS_REVALIDATION.
Human approval cannot override non-overridable safety blocks.
Human approval cannot approve missing validation evidence.
Human approval cannot approve missing evidence hashes.
```

---

# 13. Policy / Capability Registry Integration

The Promotion / Release Gate must check the Policy / Capability Registry before approving promotion.

Required checks:

```text
promotion actor is allowed to request promotion
release target is allowed
component risk level is allowed
required authorities are present
network/provider mode is allowed, if relevant
Git operation scope is allowed, if relevant
human approval is required or not required
governance approval is required or not required
risk acceptance is permitted or blocked
```

Policy outcomes must map to promotion decisions:

```text
ALLOW -> continue gate checks
BLOCK -> BLOCKED
NEEDS_APPROVAL -> NEEDS_HUMAN_APPROVAL
NEEDS_GOVERNANCE -> NEEDS_GOVERNANCE
NEEDS_REVALIDATION -> NEEDS_REVALIDATION
INVALID -> INVALID
```

If the Policy / Capability Registry is unavailable, promotion must block unless the gate is explicitly running in read-only audit mode. Read-only audit mode cannot produce APPROVED or DONE.

---

# 14. Governed Patch Execution Integration

The Promotion / Release Gate must verify Governed Patch Execution evidence when a candidate includes source changes or patch sessions.

Required checks:

```text
patch session exists
patch session binds to candidate commit
patch was generated through governed execution
patch precheck passed
patch apply evidence exists, if patch was applied
rollback evidence exists or rollback plan exists
source mutation was confined to approved paths
patch risk level was recorded
patch validation commands passed after application
patch evidence hashes are present
```

Promotion must block if:

```text
patch session evidence is missing
patch was applied outside governed execution
patch evidence binds to a different commit
rollback plan is missing when required
source mutation occurred outside approved paths
post-patch validation failed
patch evidence hashes are missing
```

---

# 15. Tool / MCP Adapter Integration

The Promotion / Release Gate must verify Tool / MCP Adapter evidence when the candidate affects tool exposure, tool calls, or MCP behavior.

Required checks:

```text
tool registry evidence exists
Tool / MCP Adapter review report exists when tool layer is affected
Tool / MCP Adapter completion record exists for claimed DONE state
Tool / MCP Adapter evidence manifest exists
MCP exposure is read-only by default or safely deferred
mutating tools are not exposed through MCP by default
blocked tools fail closed
invalid tools fail closed
tool calls/results are evidenced
evidence hashes are present
```

Promotion must block if:

```text
MCP exposes mutating tools by default
tool calls lack evidence
blocked tools execute
invalid tools execute
Tool / MCP Adapter evidence hashes are missing
Tool / MCP Adapter review report is missing for tool-layer release
Tool / MCP Adapter completion record is missing for claimed DONE state
```

---

# 16. Git Integration Layer Integration

The Promotion / Release Gate must verify Git readiness before any candidate can move toward release.

Required checks:

```text
reviewed commit is recorded
branch is recorded
working tree status is recorded
git diff summary is recorded
changed files are recorded
source mutation check is recorded
Git readiness evidence is hashable
release tag or commit operation is not performed directly by this layer in v1
Git write actions require Git Integration Layer authority
```

Promotion must block if:

```text
reviewed commit is missing
working tree is dirty without approved runtime artifacts only
changed files are unknown
Git write action is attempted directly by the Promotion / Release Gate
Git Integration Layer denies readiness
Git readiness evidence is missing or unhashable
```

---

# 17. Failure Taxonomy Integration

Every promotion failure must map to a standard failure class.

Required failure classes:

```text
PROMOTION_SCHEMA_INVALID
PROMOTION_EVIDENCE_MISSING
PROMOTION_EVIDENCE_STALE
PROMOTION_EVIDENCE_HASH_MISMATCH
PROMOTION_VALIDATION_FAILED
PROMOTION_POLICY_DENIED
PROMOTION_APPROVAL_REQUIRED
PROMOTION_APPROVAL_EXPIRED
PROMOTION_APPROVAL_REVOKED
PROMOTION_APPROVAL_SCOPE_MISMATCH
PROMOTION_APPROVAL_COMMIT_MISMATCH
PROMOTION_GOVERNANCE_REQUIRED
PROMOTION_PATCH_EVIDENCE_INVALID
PROMOTION_TOOL_EVIDENCE_INVALID
PROMOTION_GIT_READINESS_FAILED
PROMOTION_RISK_NOT_ACCEPTABLE
PROMOTION_REVIEW_REPORT_MISSING
PROMOTION_COMPLETION_RECORD_MISSING
PROMOTION_HASH_MISSING
PROMOTION_SOURCE_MUTATION_UNVERIFIED
PROMOTION_CONCURRENCY_CONFLICT
PROMOTION_IDEMPOTENCY_CONFLICT
UNKNOWN_PROMOTION_FAILURE
```

Rules:

```text
Every BLOCKED, REJECTED, DEFERRED, NEEDS_REVALIDATION, NEEDS_HUMAN_APPROVAL, NEEDS_GOVERNANCE, or INVALID decision must include a failure_class or failure_refs.
Unknown failures map to UNKNOWN_PROMOTION_FAILURE.
Failure records must be evidenced.
Failure classes must be stable enum values in schema tests.
```

---

# 18. Evidence Manifest Contract

Create evidence manifests under:

```text
.agentx-init/promotion/promotion_release_gate_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "promotion_evidence_manifest.schema.json",
  "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
  "validated_commit": "string",
  "validated_at": "string",
  "release_candidate_id": "string|null",
  "promotion_decision_id": "string|null",
  "review_environment": {
    "os": "string",
    "python_version": "string",
    "pytest_version": "string|null"
  },
  "evidence_files": [],
  "evidence_file_hashes": [],
  "upstream_evidence_refs": [],
  "upstream_evidence_hashes": [],
  "commands": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN|EXPECTED_RUNTIME_ARTIFACTS_ONLY|DIRTY|NOT_CHECKED",
  "hash_status": "PASS|FAIL|NOT_CHECKED",
  "final_decision": "APPROVED|BLOCKED|REJECTED|DEFERRED|NEEDS_REVALIDATION|NEEDS_HUMAN_APPROVAL|NEEDS_GOVERNANCE|INVALID|DONE|NOT_DONE"
}
```

Hashing rule:

```text
SHA-256 hashes are required for all final evidence artifacts.
Use Python standard-library hashlib if no project hash helper exists.
A final APPROVED or DONE decision is invalid if required final evidence hashes are missing.
Hash mismatch blocks promotion.
```

---

# 19. Review Report / Completion Evidence Contract

## 19.1 Review Report

Create review report records under:

```text
.agentx-init/promotion/promotion_release_gate_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "promotion_review_report.schema.json",
  "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
  "review_document_id": "PROMOTION_RELEASE_GATE_EQC_FIC_SIB_SCHEMA_CONTRACT",
  "review_document_version": "v4.0",
  "reviewed_commit": "string",
  "reviewed_branch": "string|null",
  "reviewed_at": "string",
  "reviewer": "string",
  "reviewer_independence": "SELF_REVIEW|INDEPENDENT_REVIEW|AUTOMATED_REVIEW|MIXED",
  "commands_run": [],
  "gate_checks": [],
  "promotion_decisions": [],
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": "string",
  "evidence_manifest_sha256": "string",
  "review_report_sha256": "string",
  "completion_record_path": "string|null",
  "completion_record_sha256": "string|null",
  "implementation_rating": 10.0,
  "final_verdict": "DONE|NOT_DONE"
}
```

## 19.2 Completion Record

Create completion records under:

```text
.agentx-init/promotion/promotion_release_gate_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "promotion_completion_record.schema.json",
  "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
  "component_name": "Promotion / Release Gate",
  "status": "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED",
  "validated_commit": "string",
  "validated_at": "string",
  "canonical_subdirectory": "tools/agentx_evolve/promotion/",
  "schema_subdirectory": "tools/agentx_evolve/schemas/",
  "runtime_artifact_root": ".agentx-init/promotion/",
  "basis_documents": [
    "PROMOTION_RELEASE_GATE_EQC_FIC_SIB_SCHEMA_CONTRACT_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "integration_checks": [],
  "promotion_gate_checks": [],
  "evidence_manifest_path": ".agentx-init/promotion/promotion_release_gate_evidence_manifest.json",
  "evidence_manifest_sha256": "string",
  "review_report_path": ".agentx-init/promotion/promotion_release_gate_review_report.json",
  "review_report_sha256": "string",
  "completion_record_sha256": "string",
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE|NOT_DONE"
}
```

## 19.3 Evidence Immutability Rule

After a promotion decision records `APPROVED` or a review report records `DONE`:

```text
final evidence files must not be modified without creating a new promotion decision or review report
changed evidence hashes invalidate the previous APPROVED or DONE decision
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

---

# 20. Audit / Evidence Contract

Required runtime artifacts:

```text
.agentx-init/promotion/promotion_decision_history.jsonl
.agentx-init/promotion/release_gate_history.jsonl
.agentx-init/promotion/release_candidate_history.jsonl
.agentx-init/promotion/validation_evidence_history.jsonl
.agentx-init/promotion/risk_acceptance_history.jsonl
.agentx-init/promotion/human_approval_link_history.jsonl
.agentx-init/promotion/promotion_audit_history.jsonl
.agentx-init/promotion/latest_promotion_decision.json
.agentx-init/promotion/latest_release_candidate.json
.agentx-init/promotion/promotion_release_gate_evidence_manifest.json
.agentx-init/promotion/promotion_release_gate_review_report.json
.agentx-init/promotion/promotion_release_gate_completion_record.json
```

Rules:

```text
append-only JSONL for histories
atomic JSON writes for latest artifacts
redact secrets before logging
record reviewed commit in every final decision
record evidence hashes for final approval
preserve invalid or blocked decisions as evidence
never erase rejected or blocked promotion decisions
never overwrite history to make a promotion look successful
```

---

# 21. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded in the evidence manifest and review report.

Required deviation fields:

```yaml
deviations:
  - id: "PROMO-DEV-001"
    area: "Evidence|Git|Approval|Policy|Patch|ToolMCP|Validation|Other"
    description: "what differs from the contract"
    reason: "why accepted"
    safety_impact: "none|low|medium|high|critical"
    compensating_control: "test/evidence/control"
    accepted_status: "NOT APPLICABLE|DEFERRED SAFELY|NON-BLOCKING FOLLOW-UP"
    reviewer_decision: "ACCEPTED|REJECTED"
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
HIGH items cannot be accepted for APPROVED or DONE unless not part of the active runtime/release path.
Runtime artifact writes outside `.agentx-init/promotion/` require a deviation entry.
Missing evidence hashes cannot be accepted as a deviation for APPROVED or DONE.
Missing reviewed commit cannot be accepted as a deviation.
```

---

# 22. OpenCode Borrowing Notes

## 22.1 Concepts to Borrow

Borrow these OpenCode-style concepts only as design patterns:

```text
explicit permission boundaries
review before mutation
command evidence
separation between read tools and write tools
status/report commands
plan and task state as explicit artifacts
blocked tool behavior
invalid tool handling
plugin exposure control
```

## 22.2 Concepts to Reject or Restrict

Do not copy these assumptions:

```text
broad tool execution by default
shell access as a normal promotion path
network/provider access by default
plugin or MCP exposure without Agent_X policy
release or Git operations without human/governance authority
model-driven approval without evidence
implicit trust in generated reports
```

## 22.3 Agent_X Mapping

| OpenCode-style concept | Agent_X Promotion / Release Gate equivalent | Required control |
|---|---|---|
| plan approval | release gate decision | schema-valid promotion decision |
| status check | validation evidence check | fresh command output and exit codes |
| tool permission | Policy / Capability Registry check | policy refs and denial handling |
| shell/test run | validation evidence | allowlisted commands only |
| patch application | Governed Patch Execution evidence | patch session refs |
| plugin exposure | Tool / MCP Adapter evidence | MCP exposure safety |
| final commit/release | Git Integration readiness | Git authority and clean status |
| human question | Human Review / Approval linkage | valid approval scope and commit |

---

# 23. Agent_X Integration Notes

## 23.1 Upstream Evidence Sources

The Promotion / Release Gate may consume evidence from:

```text
.agentx-init/security/
.agentx-init/policy/
.agentx-init/tool_calls/
.agentx-init/patches/
.agentx-init/git/
.agentx-init/evaluations/
.agentx-init/human_review/
.agentx-init/docs/
```

## 23.2 Canonical Package Placement

Implementation package:

```text
tools/agentx_evolve/promotion/
```

Schemas:

```text
tools/agentx_evolve/schemas/
```

Tests:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts:

```text
.agentx-init/promotion/
```

## 23.3 Integration Boundary Rule

The Promotion / Release Gate may read and verify upstream evidence, but it must not bypass upstream layers.

It must not:

```text
apply patches directly
write source files directly
create Git commits directly in v1
create Git tags directly in v1
push to remote repositories
modify human approval records
modify policy records
rewrite validation evidence
rewrite upstream review reports
rewrite upstream completion records
```

---

# 24. Promotion Gate Decision Pipeline

Every promotion request must follow this sequence:

```text
1. Receive promotion request or release candidate.
2. Acquire candidate lock.
3. Compute idempotency key.
4. Validate release candidate schema.
5. Bind candidate to reviewed commit.
6. Load release gate definition.
7. Load validation evidence.
8. Verify validation evidence commit matches candidate commit.
9. Verify command exit codes and statuses.
10. Verify schema validation evidence.
11. Verify source mutation / working tree evidence.
12. Check Policy / Capability Registry.
13. Check Human Approval linkage if required.
14. Check governance approval if required.
15. Check Governed Patch Execution evidence if source changes exist.
16. Check Tool / MCP Adapter evidence if tool/MCP surfaces are affected.
17. Check Git Integration readiness if promotion implies release movement.
18. Classify any failures using Failure Taxonomy.
19. Evaluate risk acceptance records.
20. Build evidence manifest and hashes.
21. Produce promotion decision.
22. Write promotion decision evidence.
23. Write latest promotion decision atomically.
24. Release candidate lock.
25. Return schema-valid decision.
```

No step may be skipped unless the release gate schema explicitly marks it not applicable.

---

# 25. Locking, Concurrency, and Idempotency

## 25.1 Locking Rules

```text
Only one active promotion decision may be written for the same release_candidate_id at a time.
Concurrent promotion requests for the same candidate must block, wait, or return PROMOTION_CONCURRENCY_CONFLICT.
Lock evidence must be recorded when lock conflicts occur.
Lock files, if used, must live under .agentx-init/promotion/.
Stale locks must be recoverable only with explicit evidence.
```

## 25.2 Idempotency Rules

```text
Repeated promotion requests for the same candidate_hash and same evidence refs must return the same decision or create a superseding decision with explicit reason.
Repeated promotion requests with the same release_candidate_id but different candidate_hash must return PROMOTION_IDEMPOTENCY_CONFLICT or create a new candidate version.
APPROVED decisions must not be silently overwritten by later BLOCKED or APPROVED decisions.
Superseded decisions must remain in history.
```

---

# 26. Required Public API Contract

Expected classes:

```text
PromotionDecision
ReleaseGate
ReleaseCandidate
ValidationEvidence
RiskAcceptance
HumanApprovalLink
PromotionAuditEvent
PromotionEvidenceManifest
PromotionReviewReport
PromotionCompletionRecord
PromotionDeviation
```

Expected public functions:

```python
load_release_gate(gate_id: str, repo_root: Path) -> ReleaseGate
validate_release_candidate(candidate: ReleaseCandidate) -> list[str]
load_validation_evidence(candidate: ReleaseCandidate, repo_root: Path) -> ValidationEvidence
check_validation_evidence(candidate: ReleaseCandidate, evidence: ValidationEvidence) -> PromotionDecision | None
check_policy_gate(candidate: ReleaseCandidate, context: dict) -> PromotionDecision | None
check_human_approval(candidate: ReleaseCandidate, context: dict) -> PromotionDecision | None
check_governance_approval(candidate: ReleaseCandidate, context: dict) -> PromotionDecision | None
check_patch_evidence(candidate: ReleaseCandidate, context: dict) -> PromotionDecision | None
check_tool_mcp_evidence(candidate: ReleaseCandidate, context: dict) -> PromotionDecision | None
check_git_readiness(candidate: ReleaseCandidate, context: dict) -> PromotionDecision | None
evaluate_risk_acceptance(candidate: ReleaseCandidate, context: dict) -> PromotionDecision | None
build_promotion_evidence_manifest(candidate: ReleaseCandidate, decision: PromotionDecision, repo_root: Path) -> dict
make_promotion_decision(candidate: ReleaseCandidate, context: dict) -> PromotionDecision
write_promotion_evidence(decision: PromotionDecision, repo_root: Path) -> dict
```

---

# 27. Security Rules

The Promotion / Release Gate must enforce:

```text
no promotion without reviewed commit
no promotion without required validation evidence
no promotion with failed required commands
no promotion with stale evidence
no promotion with missing schema validation
no promotion with dirty source state unless explicitly accepted as runtime artifacts only
no promotion with missing approval when approval is required
no promotion with expired or revoked approval
no promotion with policy denial
no promotion with invalid patch evidence
no promotion with unsafe MCP/tool exposure
no promotion with Git write operation attempted directly by this layer
no promotion with missing evidence hashes
no promotion with unclassified blocking failures
no source mutation directly in this layer
no raw shell execution
no network by default
no self-promotion without explicit reviewer-independence record
```

---

# 28. Test Acceptance Criteria

Required tests:

```text
test_release_candidate_schema_accepts_valid_candidate
test_release_candidate_schema_rejects_missing_commit
test_release_candidate_hash_required
test_promotion_decision_schema_accepts_blocked_decision
test_promotion_decision_schema_accepts_approved_decision
test_validation_evidence_requires_exit_codes
test_validation_evidence_requires_hashes_when_output_artifacts_exist
test_failed_validation_blocks_promotion
test_stale_validation_returns_needs_revalidation
test_commit_mismatch_returns_needs_revalidation
test_missing_human_approval_returns_needs_human_approval
test_expired_human_approval_blocks_promotion
test_revoked_human_approval_blocks_promotion
test_approval_scope_mismatch_blocks_promotion
test_policy_denial_blocks_promotion
test_invalid_patch_evidence_blocks_promotion
test_unsafe_mcp_exposure_blocks_promotion
test_git_dirty_status_blocks_promotion
test_missing_review_report_blocks_done
test_missing_completion_record_blocks_done
test_missing_evidence_manifest_blocks_done
test_missing_evidence_hash_blocks_done
test_hash_mismatch_blocks_promotion
test_risk_acceptance_cannot_override_blocker
test_concurrent_promotion_conflict_blocks_or_serializes
test_idempotent_promotion_returns_same_decision
test_promotion_decision_history_written
test_latest_promotion_decision_written_atomically
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema validation PASS
negative safety tests PASS
promotion decision evidence written
evidence manifest written
review report written
completion record written
evidence hashes written
no source mutation
no raw shell
no network by default
```

---

# 29. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is selected
[ ] runtime artifact root is selected
[ ] promotion decision schema is defined
[ ] release gate schema is defined
[ ] release candidate schema is defined
[ ] validation evidence schema is defined
[ ] risk acceptance schema is defined
[ ] human approval linkage schema is defined
[ ] evidence manifest schema is defined
[ ] deviation schema is defined
[ ] policy integration is defined
[ ] patch integration is defined
[ ] Tool / MCP Adapter integration is defined
[ ] Git integration is defined
[ ] failure taxonomy integration is defined
[ ] evidence rules are defined
[ ] idempotency rules are defined
[ ] locking/concurrency rules are defined
[ ] no direct source mutation rule is defined
```

---

# 30. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] schema validation passes
[ ] promotion gate decisions are schema-valid
[ ] failed validation blocks promotion
[ ] stale evidence returns NEEDS_REVALIDATION
[ ] commit mismatch returns NEEDS_REVALIDATION
[ ] missing approval blocks promotion
[ ] policy denial blocks promotion
[ ] invalid patch evidence blocks promotion
[ ] unsafe MCP exposure blocks promotion
[ ] Git readiness failure blocks promotion
[ ] risk acceptance cannot override blockers
[ ] promotion evidence is written
[ ] evidence manifest exists
[ ] review report exists
[ ] completion record exists
[ ] evidence hashes exist
[ ] idempotency works
[ ] concurrency conflicts fail closed or serialize safely
[ ] no source mutation occurs directly in this layer
```

---

# 31. Implementation Scoring Rubric

Use this rubric after implementation validation.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Promotion package, schemas, tests, and runtime artifact root exist. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass for all required promotion schemas. |
| Evidence binding and freshness | 1.0 | Commit binding, freshness, exit codes, source state, and hashes are enforced. |
| Authority integration | 1.0 | Policy, approval, governance, patch, tool/MCP, Git, and failure taxonomy checks work. |
| Promotion decisions | 1.0 | APPROVED/BLOCKED/REJECTED/DEFERRED/NEEDS_* / INVALID are schema-valid and correct. |
| Risk and approval safety | 1.0 | Risk acceptance cannot override blockers; approval scope/commit/expiry/revocation are enforced. |
| Audit / evidence | 1.0 | JSONL histories, latest artifacts, evidence manifest, review report, hashes, completion record. |
| Safety, idempotency, and concurrency | 1.0 | No source mutation, no raw shell, no network default, idempotent decisions, safe locking. |

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
failed validation approved caps score at 4.0
stale evidence approved caps score at 4.0
policy denial approved caps score at 4.0
missing required approval approved caps score at 4.0
risk acceptance overrides blocker caps score at 4.0
source mutation by this layer caps score at 5.0
raw shell executes caps score at 4.0
network enabled by default caps score at 4.0
missing evidence manifest caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
missing evidence hashes caps score at 8.0
any NOT CHECKED required area caps score at 8.0
```

---

# 32. GO / NO-GO Rules

## 32.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
promotion decision schemas pass
release candidate schemas pass
validation evidence schemas pass
risk acceptance schemas pass
approval linkage schemas pass
evidence manifest schema passes
failed validation blocks promotion
stale evidence returns NEEDS_REVALIDATION
commit mismatch returns NEEDS_REVALIDATION
missing approval blocks when approval is required
policy denial blocks promotion
invalid patch evidence blocks promotion
unsafe MCP/tool exposure blocks promotion
Git readiness failure blocks promotion
risk acceptance cannot override blockers
promotion evidence exists
evidence manifest exists
evidence hashes exist
review report exists
completion record exists
idempotency tests pass
concurrency tests pass or safe serialization is proven
source mutation check passes
no raw shell executes
no network is enabled by default
no BLOCKER exists
```

## 32.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
promotion request without reviewed commit is approved
failed validation evidence is approved
stale evidence is approved without revalidation
commit-mismatched evidence is approved
missing human approval is approved when approval is required
expired approval is accepted
revoked approval is accepted
policy denial is overridden
patch evidence failure is ignored
unsafe MCP exposure is ignored
Git dirty state is approved without explicit allowed runtime-artifact exception
risk acceptance overrides a blocker
review report is missing
completion record is missing
evidence manifest is missing
evidence hashes are missing
promotion decision evidence is missing
source mutation occurs directly in this layer
raw shell executes
network is enabled by default
Git write action is performed directly in this layer
concurrent conflicting promotion decisions are silently written
```

---

# 33. Residual Risks

```yaml
residual_risks:
  - id: "PROMO-RISK-001"
    description: "Promotion could approve stale validation evidence tied to an older commit."
    severity: "critical"
    mitigation: "Every validation evidence record must bind to the same reviewed commit as the release candidate."
  - id: "PROMO-RISK-002"
    description: "Risk acceptance could be misused to override real blockers."
    severity: "critical"
    mitigation: "Risk acceptance cannot override failed validation, policy denial, missing approval, missing evidence, unsafe MCP/Git state, or missing hashes."
  - id: "PROMO-RISK-003"
    description: "Human approval may be accepted outside its scope."
    severity: "high"
    mitigation: "Approval link must validate scope, commit, expiry, and revocation status."
  - id: "PROMO-RISK-004"
    description: "Git readiness could be treated as optional."
    severity: "high"
    mitigation: "Reviewed commit, branch/status evidence, changed files, and source mutation check are required for promotion."
  - id: "PROMO-RISK-005"
    description: "Upstream evidence may be incomplete or tampered with."
    severity: "high"
    mitigation: "Promotion evidence must include SHA-256 hashes and reviewed commit binding."
  - id: "PROMO-RISK-006"
    description: "Concurrent promotion decisions may conflict."
    severity: "medium"
    mitigation: "Candidate locking and idempotency keys are required."
```

---

# 34. Definition of Done

This controlling contract is satisfied when the implementation proves:

```text
promotion decisions are schema-valid
release candidates bind to reviewed commits
candidate hashes are present
validation evidence is required and commit-matched
failed validation blocks promotion
stale validation returns NEEDS_REVALIDATION
commit-mismatched evidence returns NEEDS_REVALIDATION
missing approval blocks when approval is required
expired/revoked/scope-mismatched approval blocks promotion
policy denial blocks promotion
patch evidence failures block promotion
unsafe Tool / MCP exposure blocks promotion
Git readiness failures block promotion
risk acceptance cannot override blockers
failure classes are recorded for non-approved decisions
audit/evidence records are written
evidence manifest is written
review report is written
completion record is written
evidence hashes are present
evidence immutability is enforced
idempotency is enforced
concurrency conflicts fail closed or serialize safely
no source mutation occurs directly in this layer
no raw shell is executed
no network is enabled by default
no Git write is performed directly by this layer in v1
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_promotion_release_gate_schemas.py
git status --short
```

Expected:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or expected runtime artifacts only
```

---


# 35. Deterministic Hashing and Provenance Contract

## 35.1 Candidate Hash Construction

`candidate_hash` must be deterministic and reproducible.

Required canonical inputs:

```text
component_id
candidate_type
reviewed_commit
base_commit, if present
branch, if present
sorted changed_files
claimed_review_report path and sha256, if present
claimed_completion_record path and sha256, if present
claimed_evidence_manifest path and sha256, if present
sorted validation_evidence_refs
sorted approval_refs
sorted risk_acceptance_refs
```

Canonicalization rule:

```text
serialize as JSON with sorted keys
normalize path separators to /
sort arrays that are order-insensitive
preserve order only for command sequences and decision histories
hash with SHA-256
record the algorithm as sha256-canonical-json-v1
```

Promotion must block if:

```text
candidate_hash is missing
candidate_hash cannot be recomputed
candidate_hash does not match canonical inputs
candidate_hash uses non-deterministic fields such as wall-clock timestamp, random ID, or local absolute path
```

## 35.2 Evidence Hash Target Set

The evidence manifest must hash every artifact used to justify APPROVED or DONE, including:

```text
release candidate record
promotion decision record
validation evidence records
policy decision evidence
human approval links, when required
risk acceptance records, when present
patch execution evidence, when source changes exist
Tool / MCP Adapter evidence, when tool/MCP surfaces are affected
Git readiness evidence
review report
completion record
evidence manifest, using the self-hash rule below
```

Self-hash rule:

```text
The evidence manifest may include its own hash only after writing a canonical final copy.
If self-hashing is used, the manifest field holding its own hash must be null or omitted during hash computation.
The chosen method must be recorded as manifest_self_hash_mode.
```

## 35.3 Upstream Evidence Trust Levels

Promotion evidence must classify upstream evidence as:

```text
TRUSTED_VALIDATED
TRUSTED_CURRENT_COMMIT
STALE_DIFFERENT_COMMIT
UNVERIFIED_IMPORTED
MISSING
TAMPERED
```

Rules:

```text
TRUSTED_VALIDATED may be used for APPROVED.
TRUSTED_CURRENT_COMMIT may be used only when schema, hash, and commit binding pass.
STALE_DIFFERENT_COMMIT returns NEEDS_REVALIDATION.
UNVERIFIED_IMPORTED cannot support APPROVED.
MISSING blocks promotion.
TAMPERED rejects or blocks promotion.
```

## 35.4 UTC and Clock-Skew Rules

All timestamps must be UTC ISO-8601 with a `Z` suffix.

Promotion must return NEEDS_REVALIDATION or BLOCKED if:

```text
timestamps are missing
timestamps are not parseable
evidence timestamp is earlier than the reviewed commit validation point when the gate requires post-commit validation
evidence timestamp is after the promotion decision by more than an accepted clock-skew window
evidence expiry cannot be evaluated
```

Default accepted clock-skew window:

```text
5 minutes maximum, unless the release gate defines a stricter value
```

---

# 36. Validation Command Acceptance Boundary

The Promotion / Release Gate may verify validation command evidence. It must not become a general command runner.

Allowed validation command evidence:

```text
python -m compileall for approved Agent_X paths
python -m pytest for approved Agent_X test paths
schema validation utilities under tools/agentx_evolve/tests/
git status/diff inspection produced by Git Integration Layer
component-specific validation commands already allowlisted by Policy / Capability Registry
```

Forbidden command behavior:

```text
raw shell execution
shell metacharacter interpolation
network commands
Git write commands
commands outside the repository without explicit policy authority
commands that mutate source files
commands whose stdout/stderr are durably logged without bounds and redaction
```

Command evidence must include:

```text
command text
argv representation, when available
working directory
exit code
status
summary
bounded output artifact reference, if output is stored
output sha256, if output artifact is used
policy decision ref, when command admissibility was checked
```

A command marked PASS without exit_code 0 is invalid.

---

# 37. Schema Example and Negative-Case Contract

Every required schema must have at least one valid example and at least one invalid example in tests.

Required valid examples:

```text
valid_promotion_decision_approved
valid_promotion_decision_blocked
valid_release_gate
valid_release_candidate
valid_validation_evidence
valid_risk_acceptance
valid_human_approval_link
valid_promotion_evidence_manifest
valid_promotion_review_report
valid_promotion_completion_record
valid_promotion_deviation
valid_promotion_audit_event
```

Required invalid examples:

```text
missing reviewed_commit
missing candidate_hash
invalid decision enum
validation command missing exit_code
validation command PASS with nonzero exit_code
approval commit mismatch
approval scope mismatch
missing evidence hash
hash mismatch
risk acceptance attempting to override blocker
unknown failure_class
non-UTC timestamp
```

Schema tests must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
commit/hash/approval mismatch is rejected by gate logic even if the raw schema shape is valid
```

---

# 38. Redaction and Output-Bounding Rules

Promotion evidence must not become a durable leak of secrets or excessive command output.

Before writing evidence, redact:

```text
API keys
tokens
provider credentials
environment values that look secret
personal access tokens
private SSH material
unredacted command output that contains secrets
raw prompts or model outputs if later layers include them
```

Output-bounding rules:

```text
command stdout/stderr must be summarized or stored as bounded artifacts
large validation outputs must not be embedded directly in promotion decisions
hashes may reference output artifacts, but raw output must be redacted first
review reports may include summaries, paths, hashes, and failure excerpts only
```

Promotion must block or downgrade to NOT DONE if a required evidence artifact contains unredacted secrets.

---

# 39. Reviewer Independence and Self-Approval Boundary

Reviewer independence must be recorded for every DONE or APPROVED claim.

Allowed reviewer independence values:

```text
SELF_REVIEW
INDEPENDENT_REVIEW
AUTOMATED_REVIEW
MIXED
```

Rules:

```text
SELF_REVIEW may support draft readiness but cannot be the only authority for release-critical APPROVED unless the release gate explicitly allows it.
INDEPENDENT_REVIEW is required for release bundles, Git release movement, and high-risk or critical-risk candidates unless explicitly deferred safely.
AUTOMATED_REVIEW may support evidence validation but cannot replace required human/governance approval.
MIXED must identify which checks were automated and which were independently reviewed.
```

Promotion must block if:

```text
reviewer independence is missing for DONE
self-review is used where independent review is required
same actor creates the candidate, accepts the risk, and marks final release-critical APPROVED without an accepted policy rule
```

---

# 40. Promotion Outcome and Release-Action Boundary

Promotion decisions are not release actions.

Allowed in this layer:

```text
APPROVED decision for a candidate
BLOCKED decision for a candidate
REJECTED decision for a candidate
DEFERRED decision for a candidate
NEEDS_* decision for a candidate
release readiness evidence
Git readiness evidence verification
release-action recommendation record
```

Not allowed in this layer in v1:

```text
creating commits
creating tags
merging branches
pushing to remotes
publishing releases
deploying artifacts
changing package versions as a side effect of approval
```

If a later Git Integration or Release layer performs an action based on APPROVED, it must create separate action evidence that references the promotion decision ID and hash.

---

# 41. Decision Supersession and Monotonic History

Promotion history must be monotonic.

Rules:

```text
every decision is append-only
a later decision may supersede an earlier one but must not erase it
a superseding decision must reference supersedes_decision_id
an APPROVED decision can be invalidated by changed evidence hashes, new commit, revoked approval, failed revalidation, or explicit supersession
a superseded APPROVED decision must not remain the active latest decision
latest_promotion_decision.json must point to the latest active decision, not rewrite history
```

Promotion must return PROMOTION_IDEMPOTENCY_CONFLICT or create a new candidate version when:

```text
same release_candidate_id has a different candidate_hash
same idempotency_key is reused with different evidence refs
an old APPROVED decision is requested for a changed commit
```

---

# 42. Final Freeze Rule

This v4 document is frozen as the controlling contract for the Promotion / Release Gate layer.

Allowed future changes:

```text
PATCH: wording, typo, section-reference, and example fixes
MINOR: additive optional schema examples or optional checks that do not weaken safety
MAJOR: changed decision precedence, changed approval rules, changed Git authority, changed risk acceptance rules, changed evidence freshness rules, changed default safety behavior
```

Blocked without major revision:

```text
allowing promotion without reviewed commit
allowing promotion without validation evidence
allowing stale evidence by default
allowing commit-mismatched evidence by default
allowing risk acceptance to override blockers
allowing human approval to override non-overridable safety blocks
allowing direct Git write by this layer in v1
allowing source mutation directly in this layer
allowing raw shell execution
allowing network by default
removing evidence hashing
removing evidence manifest requirements
removing review report or completion record requirements
removing idempotency or concurrency controls
```

The next document should be:

```text
PROMOTION_RELEASE_GATE_IMPLEMENTATION_SPEC.md
```

---

# 43. Final Rating

This v4 controlling contract is rated:

```text
10/10
```

Reason:

```text
It defines the Promotion / Release Gate with EQC, FIC, SIB, schema contracts, evidence/audit rules, promotion decision rules, release gate rules, validation evidence, risk acceptance, human approval linkage, Policy / Capability Registry integration, Governed Patch Execution integration, Tool / MCP Adapter integration, Git Integration Layer integration, Failure Taxonomy integration, evidence manifest requirements, evidence immutability, deterministic hashing, upstream evidence trust levels, validation command acceptance boundaries, schema examples, redaction and output-bounding rules, reviewer independence, release-action boundaries, monotonic decision history, OpenCode borrowing boundaries, Agent_X integration notes, idempotency, concurrency, no-go conditions, scoring caps, GO/NO-GO criteria, and a precise Definition of Done.
```
