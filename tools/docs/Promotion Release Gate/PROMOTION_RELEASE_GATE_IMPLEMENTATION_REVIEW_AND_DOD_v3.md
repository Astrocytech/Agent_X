# PROMOTION_RELEASE_GATE_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: PROMOTION_RELEASE_GATE_IMPLEMENTATION_REVIEW_AND_DOD
version: v3.0
status: final post-implementation review template and Definition of Done
component_id: AGENTX_PROMOTION_RELEASE_GATE
component_name: Promotion / Release Gate
roadmap_layer: 13
roadmap_phase: Phase C — Promotion Control
review_use: use after code is committed
primary_standard: EQC
supporting_standards:
  - FIC
  - SIB
  - Schema Contract
  - Evidence Rules
  - Audit Rules
conditional_standards:
  - Command Acceptance Criteria, if validation or git commands are exposed
  - Git Acceptance Criteria, if promotion can create branches/tags/commits
  - Human Approval Acceptance Criteria, if human sign-off is required
  - MCP Protocol Acceptance Criteria, only if release-gate functions are exposed through MCP
optional_standards:
  - ES, only for ecosystem placement
  - Report Template, only if it writes markdown reports
canonical_subdirectory: tools/agentx_evolve/promotion/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/promotion/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v3 Review and Upgrade Summary

The v2 Promotion / Release Gate review / DoD document was very strong. I would rate it:

```text
9.8/10
```

It already covered:

```text
what exists
what passed
what failed
compileall result
pytest result
schema validation result
promotion gate coverage
release candidate coverage
validation evidence coverage
approval linkage coverage
risk acceptance coverage
policy integration coverage
patch integration coverage
git integration coverage
MCP exposure coverage
failure taxonomy coverage
blocked-promotion coverage
invalid-promotion coverage
negative-test coverage
audit/evidence coverage
source mutation check
evidence hashes
review report
completion record
definition of done
final done/not-done verdict
standards applied
canonical locations
review validity
traceability
evidence freshness
anti-replay controls
evidence immutability
implementation scoring
GO / NO-GO rules
```

It was not fully 10/10 because a few final promotion-control details were still under-specified:

```text
1. It did not explicitly separate inspect-only promotion review from release-write actions such as branch, tag, commit, merge, or push.
2. It did not require a release candidate provenance hash that binds source commit, changed files, validation evidence, approvals, risks, and patch evidence.
3. It did not require monotonic timestamp checks across candidate creation, validation, approval, review, and final decision.
4. It did not explicitly require re-validation when candidate-affecting inputs change after evidence is generated.
5. It did not define an authority-chain rule for resolving conflicts among Policy, Human Approval, Patch, Git, Failure Taxonomy, and Promotion Gate decisions.
6. It did not define a strict stale-approval/stale-risk rule when a candidate hash changes.
7. It did not require promotion decision immutability and supersession records.
8. It did not require review report command-output hashes for every recorded command.
9. It did not explicitly block release promotion if validation only covers a subset of changed files without a recorded scope justification.
10. It did not define a final freeze rule to prevent repeated broad expansion of the review template.
```

This v3 adds those controls and is the final 10/10 review / DoD template.
---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Promotion / Release Gate** layer.

Use this document after code is committed to determine whether the implementation is actually complete, safe, auditable, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether promotion gate coverage is complete
whether release candidate coverage is complete
whether validation evidence is sufficient and fresh
whether approvals are valid, scoped, and unexpired
whether policy integration works
whether patch integration works
whether git integration works
whether failure taxonomy integration works
whether blocked promotions fail closed
whether invalid promotions fail closed
whether audit/evidence is written
whether source mutation is controlled
whether evidence hashes exist
whether review report exists
whether completion record exists
whether the implementation is DONE or NOT DONE
```

A 10/10 rating for this document does not mean the implementation is done. The implementation is done only when the recorded validation evidence satisfies the GO criteria in this review.

---

# 2. Why This Layer Needs These Standards

Promotion / Release Gate is safety-critical because it decides:

```text
whether implementation work can be promoted
whether validation evidence is sufficient
whether tests are fresh enough
whether approvals are valid
whether risks are accepted or blocking
whether patch execution evidence is complete
whether source changes can move toward release
whether Git actions are allowed
whether incomplete or unsafe work is blocked
```

This layer must fail closed. It must never promote incomplete, unvalidated, stale, unapproved, incorrectly scoped, or unsafe implementation work.

---

# 3. Standards Applied

## 3.1 Primary Standard

```text
EQC
```

EQC is primary because this layer makes the final quality and safety decision before implementation work can move toward release.

## 3.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Command Acceptance Criteria, if validation or git commands are exposed
```

## 3.3 Conditional Standards

```text
Git Acceptance Criteria, if promotion can create branches/tags/commits
Human Approval Acceptance Criteria, if human sign-off is required
MCP Protocol Acceptance Criteria, only if release-gate functions are exposed through MCP
```

## 3.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if it writes markdown reports
```

---

# 4. Review Target

Fill this section after implementation.

```text
review_target_commit: <commit hash>
review_target_branch: <branch name>
review_date_utc: <timestamp>
reviewer: <name or tool>
repository: https://github.com/Astrocytech/Agent_X
working_tree_start_status: CLEAN | EXPECTED_RUNTIME_ARTIFACTS_ONLY | DIRTY
working_tree_end_status: CLEAN | EXPECTED_RUNTIME_ARTIFACTS_ONLY | DIRTY
review_environment:
  os: <name/version>
  python_version: <version>
  pytest_version: <version or NOT INSTALLED>
```

The review is invalid if the reviewed commit is not recorded.

## 4.1 Review Validity Rules

The review is valid only if all of the following are true:

```text
[ ] reviewed commit is recorded
[ ] validation was run against that exact commit
[ ] reviewed branch is recorded
[ ] initial working-tree state is recorded
[ ] final working-tree state is recorded
[ ] environment information is recorded
[ ] every required command records command text, exit code, status, and summary
[ ] every command marked PASS has exit_code 0
[ ] schema validation command or pytest equivalent is recorded
[ ] every expected-failure negative test records the expected failure condition
[ ] promotion review report artifact is created
[ ] evidence manifest exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] required evidence hashes are present
[ ] reviewer did not rely only on this document's internal rating
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

The implementation may not be marked `DONE` because this document says `review_document_rating: 10/10`.

---

# 5. Status Vocabulary

Use only these status values in review tables.

```text
PASS
PARTIAL
FAIL
NOT CHECKED
NOT RUN
NOT APPLICABLE
DEFERRED SAFELY
```

| Status | Meaning | DONE allowed? |
|---|---|---|
| PASS | Requirement was checked and satisfied. | Yes |
| PARTIAL | Some required parts are present, but coverage is incomplete. | No, unless explicitly non-blocking and documented |
| FAIL | Requirement was checked and failed. | No |
| NOT CHECKED | Requirement was not validated. | No |
| NOT RUN | Required command or executable check was not run. | No |
| NOT APPLICABLE | Requirement does not apply to the implemented scope and cannot affect runtime behavior. | Yes, if justified |
| DEFERRED SAFELY | Feature is intentionally deferred and cannot promote, mutate, approve, tag, commit, or bypass policy. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Deferral Rules

Use these rules to avoid hiding missing work behind `NOT APPLICABLE` or `DEFERRED SAFELY`.

```text
NOT APPLICABLE:
  Use only when the implementation scope truly does not include the feature and there is no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot promote, mutate, approve, create Git state, expose MCP behavior, or bypass policy.

PARTIAL:
  Use when some files or tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

---

# 6. Promotion Authority Boundary

The Promotion / Release Gate must distinguish between review decisions and release-write actions.

## 6.1 Inspect-Only Promotion Review

Inspect-only review may:

```text
read release candidate metadata
read validation evidence
read approval references
read policy decisions
read patch evidence
read Git/source state
write promotion runtime evidence under `.agentx-init/promotion/`
write BLOCKED / INVALID / ALLOW promotion decision records
write review report, evidence manifest, and completion record
```

Inspect-only review must not:

```text
create Git branches
create Git tags
create commits
merge branches
push to remote
modify source files
modify prior evidence files
approve itself
override policy
override failed validation
override unresolved hard blockers
```

## 6.2 Release-Write Actions

Release-write actions include:

```text
branch creation
tag creation
commit creation
merge
push
release artifact publication
promotion status mutation outside `.agentx-init/promotion/`
```

Release-write actions are allowed only if the implementation explicitly includes them and the review proves:

```text
Git Acceptance Criteria were applied
Human Approval Acceptance Criteria were applied where required
Policy / Capability Registry allowed the action
source state was clean or accepted by recorded deviation
release candidate provenance hash matched reviewed evidence
action was dry-run validated before execution where applicable
action wrote evidence
action had rollback or recovery notes where applicable
```

If release-write actions are not implemented, they must be:

```text
NOT APPLICABLE when no entrypoint exists
DEFERRED SAFELY when stubs exist but cannot execute
BLOCKED if callable but not authorized
```

## 6.3 Authority-Chain Conflict Rule

Promotion may return `ALLOW` only if all required authorities agree.

Required authority order:

```text
Schema validation
Release candidate provenance
Validation evidence
Policy / Capability Registry
Governed Patch Execution evidence, when source changes exist
Git/source-state check, when repository state matters
Human approval, when required
Risk acceptance, only for non-hard-blocker risks
Failure Taxonomy classification
Promotion Gate final decision
```

If authorities disagree, the strictest decision wins.

Decision precedence:

```text
INVALID
BLOCKED
NEEDS_APPROVAL
NEEDS_GOVERNANCE
DEFERRED
ALLOW
```

A human approval, risk acceptance, or promotion decision cannot override:

```text
failed validation
missing required evidence
stale validation evidence
wrong-commit validation evidence
policy denial
unresolved hard blocker
unsafe Git state
missing required patch evidence
schema-invalid candidate or decision
```

---

# 7. Provenance, Freshness, and Revalidation Rules

## 7.1 Release Candidate Provenance Hash

Every release candidate must have a provenance hash where possible.

The provenance hash should bind:

```text
candidate_id
source commit
branch
changed file list
changed file hashes or diff hash where available
basis documents
validation evidence references
approval references
risk acceptance references
policy decision references
patch evidence references
Git/source-state evidence
promotion gate version
```

Required behavior:

```text
candidate hash is recorded before final decision
candidate hash is recorded in promotion decision
candidate hash is recorded in review report
candidate hash is recorded in completion record
candidate hash changes invalidate prior approval/evidence unless explicitly scoped to survive the change
```

## 7.2 Monotonic Timestamp Rule

Promotion evidence must have a coherent time order.

Expected order:

```text
release candidate created
validation evidence generated
policy decision generated
patch evidence generated, if applicable
approval generated, if applicable
risk acceptance generated, if applicable
promotion review run
promotion decision written
completion record written
```

Blocking conditions:

```text
approval predates candidate outside allowed scope
risk acceptance predates candidate outside allowed scope
validation evidence predates candidate source commit
promotion decision predates required validation evidence
completion record predates review report
timestamps are missing from required evidence
timestamps are impossible or contradictory
```

## 7.3 Revalidation Triggers

Promotion must require new validation or a new promotion decision if any candidate-affecting input changes.

Candidate-affecting changes include:

```text
source commit changes
branch changes
changed file list changes
diff hash changes
schema files change
test files change
runtime promotion configuration changes
basis documents change
approval scope changes
risk acceptance scope changes
patch evidence changes
policy decision changes
promotion gate version changes
```

If any candidate-affecting input changes after validation evidence was generated:

```text
promotion must BLOCK
or require fresh validation evidence for the new candidate hash
or record a justified non-blocking deviation only when the changed input cannot affect runtime/release safety
```

## 7.4 Changed-File Coverage Rule

Validation evidence must cover the actual release candidate scope.

Blocking conditions:

```text
changed source files are not represented in validation evidence
changed schemas are not represented in schema validation evidence
changed tests are not represented in pytest evidence
changed promotion logic is not represented in promotion tests
validation command scope excludes changed files without justification
```

If scoped validation is used, the review must record:

```text
scoped command
reason full command was not used
changed files covered
changed files not covered
safety justification
reviewer decision
```

---

# 8. Expected Implementation Scope

## 6.1 Required Promotion Package

Expected location:

```text
tools/agentx_evolve/promotion/
```

Expected files:

```text
tools/agentx_evolve/promotion/__init__.py
tools/agentx_evolve/promotion/promotion_models.py
tools/agentx_evolve/promotion/promotion_gate.py
tools/agentx_evolve/promotion/release_candidate.py
tools/agentx_evolve/promotion/validation_evidence.py
tools/agentx_evolve/promotion/risk_acceptance.py
tools/agentx_evolve/promotion/approval_lookup.py
tools/agentx_evolve/promotion/promotion_policy.py
tools/agentx_evolve/promotion/promotion_audit.py
tools/agentx_evolve/promotion/promotion_report.py
```

## 6.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
promotion_gate.schema.json
release_candidate.schema.json
promotion_decision.schema.json
validation_evidence.schema.json
risk_acceptance.schema.json
approval_linkage.schema.json
promotion_policy.schema.json
promotion_audit.schema.json
promotion_review_report.schema.json
promotion_completion_record.schema.json
promotion_evidence_manifest.schema.json
```

## 6.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_promotion_gate.py
test_release_candidate.py
test_promotion_decision_schema.py
test_validation_evidence.py
test_risk_acceptance.py
test_approval_linkage.py
test_promotion_policy_integration.py
test_promotion_patch_integration.py
test_promotion_git_integration.py
test_promotion_failure_taxonomy.py
test_blocked_promotion.py
test_invalid_promotion.py
test_promotion_audit_evidence.py
test_promotion_negative_cases.py
test_promotion_schema_validation.py
```

## 6.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/promotion/
```

Expected artifacts:

```text
promotion_decision_history.jsonl
release_candidate_history.jsonl
blocked_promotion_history.jsonl
invalid_promotion_history.jsonl
latest_promotion_decision.json
latest_release_candidate.json
promotion_evidence_manifest.json
promotion_review_report.json
promotion_completion_record.json
```

## 6.5 Required Validation Utility

Expected validation utility:

```text
tools/agentx_evolve/tests/validate_promotion_schemas.py
```

If this utility is not present, the review must identify the exact pytest-based schema validation replacement and prove it covers all required valid and invalid schema cases.

---

# 9. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or a clean working tree.

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

If `validate_promotion_schemas.py` is not implemented, the same schema coverage must be proven by a documented pytest file such as:

```text
tools/agentx_evolve/tests/test_promotion_schema_validation.py
```

Required result:

```text
initial git status: clean or expected known runtime artifacts only
python version: recorded
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
final git status: clean or expected runtime artifacts only
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
running MCP server
manual human input
```

The primary pytest command may run the full `tools/agentx_evolve/tests` suite. If unrelated future-layer tests exist in that directory, the review must also record a scoped Promotion / Release Gate pytest command that includes only promotion-related tests.

---

# 10. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Promotion package location | `tools/agentx_evolve/promotion/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schemas | all required promotion schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tests | required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Promotion gate model | gate model validates required fields and states | PASS / PARTIAL / FAIL / NOT CHECKED |
| Release candidate model | candidate identity, source commit, evidence refs, and status are captured | PASS / PARTIAL / FAIL / NOT CHECKED |
| Promotion decision model | ALLOW / BLOCK / EXPIRE / DEFER / INVALID outcomes are schema-valid | PASS / PARTIAL / FAIL / NOT CHECKED |
| Validation evidence | compileall, pytest, schema, review, and integration evidence are checked | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence freshness | validation evidence is tied to commit and freshness window | PASS / PARTIAL / FAIL / NOT CHECKED |
| Anti-replay controls | approvals/evidence cannot be reused outside scope | PASS / PARTIAL / FAIL / NOT CHECKED |
| Risk acceptance | risk records validate and cannot override hard blockers | PASS / PARTIAL / FAIL / NOT CHECKED |
| Approval linkage | human approval references are verified and freshness checked | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Policy integration | promotion checks Policy / Capability Registry | PASS / PARTIAL / FAIL / NOT CHECKED |
| Patch integration | promotion checks Governed Patch Execution evidence | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Git integration | promotion checks source commit and blocks unsafe Git actions | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Failure taxonomy | blocked/invalid/failure outcomes use standard failure classes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Blocked promotion | unsafe or incomplete work blocks with evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Invalid promotion | malformed candidate/request returns INVALID with evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Audit/evidence | JSONL + latest artifacts + manifest + report + completion record exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence hashing | SHA-256 hashes exist for final evidence artifacts | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime artifact boundary | artifacts written only under `.agentx-init/promotion/` or deviation listed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | review proves no unapproved source mutation | PASS / PARTIAL / FAIL / NOT CHECKED |
| MCP exposure | N/A unless release-gate functions exposed through MCP | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE / DEFERRED SAFELY |

---

# 11. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Promotion gate loads | `promotion_gate.py` | `test_promotion_gate.py` | review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Release candidate validates | `release_candidate.py` | `test_release_candidate.py` | candidate history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Promotion decision validates | `promotion_models.py` | `test_promotion_decision_schema.py` | decision history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Validation evidence checked | `validation_evidence.py` | `test_validation_evidence.py` | evidence manifest | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence freshness enforced | `validation_evidence.py` | `test_validation_evidence.py` | review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Risk acceptance enforced | `risk_acceptance.py` | `test_risk_acceptance.py` | risk records | PASS / PARTIAL / FAIL / NOT CHECKED |
| Approval linkage checked | `approval_lookup.py` | `test_approval_linkage.py` | approval refs | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Policy integration checked | `promotion_policy.py` | `test_promotion_policy_integration.py` | policy decision refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Patch evidence checked | promotion integration code | `test_promotion_patch_integration.py` | patch evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Git/source state checked | promotion integration code | `test_promotion_git_integration.py` | git evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Failure taxonomy mapped | `promotion_models.py` or failure adapter | `test_promotion_failure_taxonomy.py` | blocked/invalid histories | PASS / PARTIAL / FAIL / NOT CHECKED |
| Blocked promotion fails closed | `promotion_gate.py` | `test_blocked_promotion.py` | blocked history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Invalid promotion fails closed | `promotion_gate.py` | `test_invalid_promotion.py` | invalid history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Audit evidence written | `promotion_audit.py` | `test_promotion_audit_evidence.py` | JSONL + latest artifacts | PASS / PARTIAL / FAIL / NOT CHECKED |
| Review report written | `promotion_report.py` | schema/manual validation | review report JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record written | `promotion_report.py` | schema/manual validation | completion record JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 12. What Exists Checklist

## 10.1 Promotion Package Files

```text
[ ] tools/agentx_evolve/promotion/__init__.py
[ ] tools/agentx_evolve/promotion/promotion_models.py
[ ] tools/agentx_evolve/promotion/promotion_gate.py
[ ] tools/agentx_evolve/promotion/release_candidate.py
[ ] tools/agentx_evolve/promotion/validation_evidence.py
[ ] tools/agentx_evolve/promotion/risk_acceptance.py
[ ] tools/agentx_evolve/promotion/approval_lookup.py
[ ] tools/agentx_evolve/promotion/promotion_policy.py
[ ] tools/agentx_evolve/promotion/promotion_audit.py
[ ] tools/agentx_evolve/promotion/promotion_report.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.2 Schema Files

```text
[ ] promotion_gate.schema.json
[ ] release_candidate.schema.json
[ ] promotion_decision.schema.json
[ ] validation_evidence.schema.json
[ ] risk_acceptance.schema.json
[ ] approval_linkage.schema.json
[ ] promotion_policy.schema.json
[ ] promotion_audit.schema.json
[ ] promotion_review_report.schema.json
[ ] promotion_completion_record.schema.json
[ ] promotion_evidence_manifest.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.3 Test Files

```text
[ ] test_promotion_gate.py
[ ] test_release_candidate.py
[ ] test_promotion_decision_schema.py
[ ] test_validation_evidence.py
[ ] test_risk_acceptance.py
[ ] test_approval_linkage.py
[ ] test_promotion_policy_integration.py
[ ] test_promotion_patch_integration.py
[ ] test_promotion_git_integration.py
[ ] test_promotion_failure_taxonomy.py
[ ] test_blocked_promotion.py
[ ] test_invalid_promotion.py
[ ] test_promotion_audit_evidence.py
[ ] test_promotion_negative_cases.py
[ ] test_promotion_schema_validation.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.4 Runtime Artifacts

```text
[ ] promotion_decision_history.jsonl
[ ] release_candidate_history.jsonl
[ ] blocked_promotion_history.jsonl
[ ] invalid_promotion_history.jsonl
[ ] latest_promotion_decision.json
[ ] latest_release_candidate.json
[ ] promotion_evidence_manifest.json
[ ] promotion_review_report.json
[ ] promotion_completion_record.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 13. Compileall Result

Record the compile result.

```text
command: PYTHONPATH=tools python -m compileall tools/agentx_evolve
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256 if output artifact is stored>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any Promotion / Release Gate Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 14. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256 if output artifact is stored>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required promotion gate, release candidate, approval, policy, patch, git, blocked-promotion, invalid-promotion, schema, evidence, or integration test fails
exit code is missing
```

---

# 15. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_promotion_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_promotion_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256 if output artifact is stored>
```

Required schema checks:

```text
promotion gate schema accepts valid gate
promotion gate schema rejects missing gate_id
release candidate schema accepts valid candidate
release candidate schema rejects missing source commit
promotion decision schema accepts ALLOW
promotion decision schema accepts BLOCK
promotion decision schema accepts INVALID
promotion decision schema rejects unknown decision
validation evidence schema accepts compileall/pytest/schema evidence
validation evidence schema rejects missing command exit code
validation evidence schema rejects missing validated commit
risk acceptance schema accepts valid accepted risk
risk acceptance schema rejects accepted hard blocker
approval linkage schema accepts valid approval reference
approval linkage schema rejects expired approval
approval linkage schema rejects wrong candidate scope
promotion audit schema accepts valid audit event
promotion evidence manifest schema accepts valid manifest
promotion review report schema accepts valid report
promotion completion record schema accepts valid completion record
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
schema-invalid promotion request is accepted
schema-invalid release candidate is accepted
promotion decision schema cannot represent BLOCK or INVALID outcomes
validation evidence can omit command exit codes
validation evidence can omit validated commit
risk acceptance can override hard blockers
expired approval validates as usable
wrong-scope approval validates as usable
review report cannot be schema-validated
completion record cannot be schema-validated
schema validation exit code is missing
```

---

# 16. Promotion Gate Coverage

Required behavior:

```text
[ ] default promotion gate loads
[ ] gate has deterministic gate_id and version
[ ] gate declares required validation evidence
[ ] gate declares required approval evidence
[ ] gate declares required policy checks
[ ] gate declares required patch evidence checks
[ ] gate declares required Git/source-state checks
[ ] gate blocks stale validation evidence
[ ] gate blocks missing evidence
[ ] gate blocks failed evidence
[ ] gate blocks unrelated evidence
[ ] gate blocks unresolved hard blockers
[ ] gate blocks wrong-scope approval
[ ] gate records decision reason
[ ] gate records evidence references
[ ] gate records source commit
[ ] gate records candidate_id
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
promotion gate can allow without required evidence
promotion gate can allow with unresolved hard blockers
promotion gate can allow with stale tests
promotion gate can allow with wrong-scope approval
promotion gate decision lacks evidence refs
```

---

# 17. Release Candidate Coverage

Required behavior:

```text
[ ] release candidate records candidate_id
[ ] release candidate records source commit
[ ] release candidate records source tree hash or diff hash where available
[ ] release candidate records branch
[ ] release candidate records implementation component
[ ] release candidate records basis documents
[ ] release candidate records files changed
[ ] release candidate records schemas changed
[ ] release candidate records tests changed
[ ] release candidate records validation evidence refs
[ ] release candidate records approval refs
[ ] release candidate records risk records
[ ] release candidate records promotion status
[ ] release candidate is immutable after promotion decision
[ ] changed candidate requires new candidate_id or new decision
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
release candidate has no source commit
release candidate has no validation evidence
release candidate can be promoted without status
release candidate can be modified after promotion without new decision
```

---

# 18. Validation Evidence Coverage

Required behavior:

```text
[ ] compileall evidence is present
[ ] pytest evidence is present
[ ] schema validation evidence is present
[ ] command text is recorded
[ ] command exit code is recorded
[ ] command status is recorded
[ ] command summary is recorded
[ ] validated commit is recorded
[ ] evidence timestamp is recorded
[ ] evidence applies to the same source commit as the release candidate
[ ] evidence freshness window is checked
[ ] stale validation evidence blocks promotion
[ ] failed validation evidence blocks promotion
[ ] missing validation evidence blocks promotion
[ ] evidence hashes are recorded
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
promotion allows missing compileall evidence
promotion allows missing pytest evidence
promotion allows missing schema evidence
promotion allows failed validation evidence
promotion allows evidence from a different commit
promotion allows stale validation evidence
command exit codes are missing
```

Recommended default freshness rule:

```text
Validation evidence is fresh only if it was generated for the exact release candidate commit during the current review session.
```

If a different freshness window is used, it must be recorded in the promotion gate configuration and review report.

---

# 19. Approval Linkage Coverage

Required behavior:

```text
[ ] human approval reference can be looked up
[ ] approval has approval_id
[ ] approval has approver role
[ ] approval has approved scope
[ ] approval has timestamp
[ ] approval has expiry
[ ] approval is linked to candidate_id or implementation session
[ ] approval cannot be reused for different candidate unless scope permits
[ ] expired approval blocks promotion
[ ] wrong-scope approval blocks promotion
[ ] missing required approval returns BLOCKED or NEEDS_APPROVAL
[ ] human approval cannot override hard safety blockers
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
promotion can proceed with missing required approval
expired approval is accepted
approval for one candidate is reused for another without scope
human approval overrides hard safety blocker
```

---

# 20. Risk Acceptance Coverage

Required behavior:

```text
[ ] risk record has risk_id
[ ] risk record has severity
[ ] risk record has owner/approver where required
[ ] risk record has accepted scope
[ ] risk record has expiry where required
[ ] risk record is linked to candidate_id or implementation session
[ ] accepted risk cannot override hard blockers
[ ] accepted risk cannot override failed validation
[ ] accepted risk cannot override policy denial
[ ] accepted risk cannot override sandbox/patch/Git safety blocks
[ ] expired risk acceptance is rejected
[ ] wrong-scope risk acceptance is rejected
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
risk acceptance allows failed tests to promote
risk acceptance allows unresolved hard blocker to promote
risk acceptance allows policy-denied promotion
expired or wrong-scope risk acceptance is accepted
```

---

# 21. Policy Integration Coverage

Required behavior:

```text
[ ] promotion asks Policy / Capability Registry before ALLOW
[ ] missing policy service fails closed or restrictive fallback blocks promotion
[ ] policy-denied promotion returns BLOCKED
[ ] policy decision ID is recorded in evidence
[ ] promotion cannot bypass role permissions
[ ] promotion cannot override non-overridable blocks
[ ] policy result maps to standard failure class
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
missing policy results in ALLOW
policy-denied promotion proceeds
policy evidence is missing
promotion bypasses role permissions
```

---

# 22. Patch Integration Coverage

Required behavior:

```text
[ ] promotion checks Governed Patch Execution evidence when source changes are involved
[ ] patch session ID is recorded
[ ] patch application evidence is recorded
[ ] rollback availability is recorded where required
[ ] patch validation result is recorded
[ ] patch layer unresolved blockers block promotion
[ ] missing patch evidence blocks promotion when source mutation occurred
[ ] patch evidence cannot be reused across unrelated candidates
[ ] patch evidence applies to same source commit or candidate scope
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
source changes promote without patch evidence
failed patch validation promotes
patch blockers are ignored
patch evidence is missing or unrelated
```

---

# 23. Git Integration Coverage

This section applies if promotion can inspect or perform Git actions.

Required behavior:

```text
[ ] source commit is recorded
[ ] branch is recorded
[ ] working tree status is recorded
[ ] promotion checks clean or expected-runtime-only status
[ ] promotion blocks dirty source tree unless explicitly allowed by contract
[ ] promotion records diff or diff summary evidence
[ ] Git write actions are disabled unless this phase explicitly allows them
[ ] tag/branch/commit actions require Git Acceptance Criteria if implemented
[ ] Git failure maps to standard failure class
[ ] promotion cannot create tag/branch/commit without explicit reviewed approval
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
promotion can proceed without source commit
promotion can proceed from dirty tree without accepted deviation
Git write occurs without approval and acceptance criteria
Git evidence is missing
```

---

# 24. MCP Exposure Coverage

This section applies only if release-gate functions are exposed through MCP.

Required behavior if MCP exposure exists:

```text
[ ] MCP exposure is disabled by default or read-only/status-only
[ ] MCP cannot approve promotion by default
[ ] MCP cannot override policy
[ ] MCP cannot override approval checks
[ ] MCP cannot perform Git write action
[ ] MCP cannot mark DONE directly
[ ] MCP request creates schema-valid promotion request
[ ] invalid MCP request returns INVALID or BLOCKED
[ ] MCP exposure has tests
```

If MCP is intentionally absent:

```text
[ ] no MCP release-gate entrypoint exists
[ ] no MCP server starts
[ ] no network port opens
[ ] no MCP promotion approval path exists
[ ] status is recorded as NOT APPLICABLE
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

Blocking if:

```text
MCP can approve promotion by default
MCP bypasses policy or approval checks
MCP performs Git write action
MCP marks implementation DONE without review evidence
```

---

# 25. Failure Taxonomy Coverage

Required behavior:

```text
[ ] blocked promotion has failure_class
[ ] invalid promotion has failure_class
[ ] missing validation evidence maps to PROMOTION_VALIDATION_EVIDENCE_MISSING
[ ] failed validation evidence maps to PROMOTION_VALIDATION_EVIDENCE_FAILED
[ ] stale validation evidence maps to PROMOTION_VALIDATION_EVIDENCE_STALE
[ ] wrong-commit validation evidence maps to PROMOTION_VALIDATION_EVIDENCE_SCOPE_MISMATCH
[ ] missing approval maps to PROMOTION_APPROVAL_MISSING
[ ] expired approval maps to PROMOTION_APPROVAL_EXPIRED
[ ] wrong-scope approval maps to PROMOTION_APPROVAL_SCOPE_MISMATCH
[ ] risk acceptance violation maps to PROMOTION_RISK_ACCEPTANCE_INVALID
[ ] policy denial maps to PROMOTION_POLICY_DENIED
[ ] patch evidence issue maps to PROMOTION_PATCH_EVIDENCE_INVALID
[ ] Git/source-state issue maps to PROMOTION_GIT_STATE_INVALID
[ ] unknown failure maps to UNKNOWN_PROMOTION_FAILURE
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
blocked/invalid promotion lacks failure_class
policy, patch, git, approval, or evidence failures use unstructured errors only
unknown failures are swallowed
```

---

# 26. Blocked-Promotion Coverage

Required blocked-promotion behavior:

```text
[ ] missing compileall evidence blocks promotion
[ ] failed compileall evidence blocks promotion
[ ] missing pytest evidence blocks promotion
[ ] failed pytest evidence blocks promotion
[ ] missing schema validation evidence blocks promotion
[ ] failed schema validation evidence blocks promotion
[ ] stale validation evidence blocks promotion
[ ] wrong-commit validation evidence blocks promotion
[ ] missing approval blocks promotion when approval is required
[ ] expired approval blocks promotion
[ ] wrong-scope approval blocks promotion
[ ] unresolved hard blocker blocks promotion
[ ] invalid risk acceptance blocks promotion
[ ] failed patch evidence blocks promotion
[ ] unsafe Git state blocks promotion
[ ] blocked promotion writes evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
blocked promotion silently succeeds
blocked promotion has no evidence
blocked promotion mutates source or Git state
blocked promotion returns ALLOW
```

---

# 27. Invalid-Promotion Coverage

Required invalid-promotion behavior:

```text
[ ] malformed release candidate returns INVALID
[ ] missing candidate_id returns INVALID
[ ] missing source commit returns INVALID
[ ] missing required decision fields returns INVALID
[ ] unknown promotion action returns INVALID
[ ] invalid promotion writes evidence
[ ] invalid promotion does not guess intended candidate
[ ] invalid promotion does not mutate source or Git state
[ ] invalid promotion does not call network or model
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
invalid promotion raises unhandled exception
invalid promotion proceeds
invalid promotion lacks evidence
invalid promotion guesses and promotes a substitute candidate
```

---

# 28. Negative Test Pack

The review must prove that forbidden promotion scenarios fail closed.

Required negative cases:

```text
[ ] missing release candidate -> INVALID
[ ] missing candidate_id -> INVALID
[ ] missing source commit -> INVALID
[ ] missing compileall evidence -> BLOCKED
[ ] failed compileall evidence -> BLOCKED
[ ] missing pytest evidence -> BLOCKED
[ ] failed pytest evidence -> BLOCKED
[ ] missing schema validation evidence -> BLOCKED
[ ] failed schema validation evidence -> BLOCKED
[ ] stale validation evidence -> BLOCKED
[ ] validation evidence from different commit -> BLOCKED
[ ] missing required approval -> BLOCKED or NEEDS_APPROVAL
[ ] expired approval -> BLOCKED
[ ] wrong-scope approval -> BLOCKED
[ ] accepted risk attempts to override hard blocker -> BLOCKED
[ ] policy-denied promotion -> BLOCKED
[ ] missing patch evidence for source changes -> BLOCKED
[ ] failed patch evidence -> BLOCKED
[ ] dirty Git tree without accepted deviation -> BLOCKED
[ ] Git write action without acceptance criteria -> BLOCKED
[ ] MCP promotion approval by default -> BLOCKED or NOT APPLICABLE
[ ] secret-like payload -> redacted in evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked not applicable with justification.

---

# 29. Audit / Evidence Coverage

Required evidence behavior:

```text
[ ] promotion_decision_history.jsonl is written
[ ] release_candidate_history.jsonl is written
[ ] blocked_promotion_history.jsonl is written
[ ] invalid_promotion_history.jsonl is written
[ ] latest_promotion_decision.json is written atomically
[ ] latest_release_candidate.json is written atomically
[ ] promotion_evidence_manifest.json is written
[ ] promotion_review_report.json is written
[ ] promotion_completion_record.json is written after validation
[ ] evidence includes timestamps
[ ] evidence includes reviewed commit
[ ] evidence includes command text, exit codes, statuses, and summaries
[ ] evidence includes validation freshness information
[ ] evidence includes approval references
[ ] evidence includes risk acceptance references
[ ] evidence includes policy decision references
[ ] evidence includes patch evidence references
[ ] evidence includes Git/source-state references
[ ] evidence includes SHA-256 hashes
[ ] secrets are redacted before logging
[ ] schema-invalid result does not replace valid latest result
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
promotion decisions are not logged
blocked/invalid promotions are not evidenced
reviewed commit is missing
required hashes are missing
secrets are logged
latest artifacts are written unsafely
```

---

# 30. Source Mutation Check

Required command:

```bash
git status --short
```

Expected:

```text
clean working tree
```

or:

```text
only expected runtime artifacts under .agentx-init/promotion/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by promotion review tests
unapproved files are created outside runtime artifact paths
runtime artifacts are written outside approved runtime roots
promotion gate creates branches/tags/commits without explicit Git Acceptance Criteria
```

---

# 31. Evidence Hashes

SHA-256 hashes are required for final evidence artifacts.

Required hashed artifacts:

```text
promotion_evidence_manifest.json
promotion_review_report.json
promotion_completion_record.json
promotion_decision_history.jsonl, if used by review
release_candidate_history.jsonl, if used by review
blocked_promotion_history.jsonl, if used by review
invalid_promotion_history.jsonl, if used by review
latest_promotion_decision.json, if used by review
latest_release_candidate.json, if used by review
command output artifacts, if stored as files
```

Hashing rule:

```text
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 32. Evidence Manifest

Create:

```text
.agentx-init/promotion/promotion_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "promotion_evidence_manifest.schema.json",
  "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "commands": [
    {
      "name": "compileall",
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>"
    },
    {
      "name": "pytest",
      "command": "PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>"
    },
    {
      "name": "schema_validation",
      "command": "<schema validation command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>"
    }
  ],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [],
  "release_candidate_provenance_hash": "<sha256>",
  "changed_file_scope_status": "PASS",
  "monotonic_timestamp_status": "PASS",
  "revalidation_trigger_status": "PASS",
  "validation_freshness_policy": {
    "mode": "same_commit_current_review",
    "max_age_seconds": null
  },
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "promotion_gate_status": "PASS",
  "release_candidate_status": "PASS",
  "approval_linkage_status": "PASS_OR_NOT_APPLICABLE",
  "risk_acceptance_status": "PASS_OR_NOT_APPLICABLE",
  "policy_integration_status": "PASS",
  "patch_integration_status": "PASS_OR_NOT_APPLICABLE",
  "git_integration_status": "PASS_OR_NOT_APPLICABLE",
  "mcp_exposure_status": "NOT_APPLICABLE",
  "blocked_invalid_status": "PASS",
  "redaction_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

The manifest must include paths and hashes for all final evidence files.

Approved runtime artifact boundary:

```text
.agentx-init/promotion/
```

Evidence artifacts for this layer must not be written outside that root unless the review records the exception in the deviation register.

---

# 33. Review Report Artifact

Create:

```text
.agentx-init/promotion/promotion_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "promotion_review_report.schema.json",
  "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
  "review_document_id": "PROMOTION_RELEASE_GATE_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v3.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
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
  "command_output_hashes": [],
  "coverage_statuses": {},
  "release_candidate_provenance_hash": "<sha256>",
  "changed_file_scope_status": "PASS",
  "monotonic_timestamp_status": "PASS",
  "revalidation_trigger_status": "PASS",
  "validation_freshness_policy": {
    "mode": "same_commit_current_review",
    "max_age_seconds": null
  },
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/promotion/promotion_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/promotion/promotion_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/promotion/promotion_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

A final `DONE` verdict is invalid if this report is missing, does not identify the exact reviewed commit, or lacks command exit codes.

## 31.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

---

# 34. Completion Record

Create after validation:

```text
.agentx-init/promotion/promotion_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "promotion_completion_record.schema.json",
  "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
  "component_name": "Promotion / Release Gate",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "canonical_subdirectory": "tools/agentx_evolve/promotion/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/promotion/",
  "release_candidate_provenance_hash": "<sha256>",
  "promotion_decision_id": "<decision id>",
  "supersedes_promotion_decision_id": "<decision id or null>",
  "basis_documents": [
    "PROMOTION_RELEASE_GATE_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "PROMOTION_RELEASE_GATE_IMPLEMENTATION_SPEC",
    "PROMOTION_RELEASE_GATE_IMPLEMENTATION_REVIEW_AND_DOD_v3"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "promotion_gate_entries_verified": [],
  "release_candidates_verified": [],
  "validation_evidence_verified": [],
  "approval_linkage_verified": [],
  "risk_acceptance_verified": [],
  "policy_integration_verified": [],
  "patch_integration_verified": [],
  "git_integration_verified": [],
  "mcp_exposure_verified": [],
  "failure_taxonomy_integration_verified": [],
  "blocked_promotions_verified": [],
  "invalid_promotions_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/promotion/promotion_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/promotion/promotion_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

---

# 35. Promotion Decision Immutability and Supersession

Promotion decisions are immutable once written.

Required behavior:

```text
[ ] promotion decision has decision_id
[ ] promotion decision has candidate_id
[ ] promotion decision has release_candidate_provenance_hash
[ ] promotion decision has reviewed commit
[ ] promotion decision has timestamp
[ ] promotion decision has decision status
[ ] promotion decision has evidence refs
[ ] promotion decision has reviewer/tool identity
[ ] promotion decision cannot be edited in place after final verdict
[ ] changed candidate requires a new decision
[ ] replaced decision records supersedes_promotion_decision_id
[ ] superseded decision remains in history
```

Blocking if:

```text
promotion decision can be modified in place
changed candidate reuses prior ALLOW decision without supersession
superseded decision is deleted
final decision lacks candidate provenance hash
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

# 36. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
promotion gate coverage:
release candidate coverage:
validation evidence coverage:
release candidate provenance coverage:
changed-file scope coverage:
monotonic timestamp coverage:
revalidation trigger coverage:
approval linkage coverage:
risk acceptance coverage:
policy integration coverage:
patch integration coverage:
git integration coverage:
mcp exposure coverage:
failure taxonomy coverage:
blocked-promotion coverage:
invalid-promotion coverage:
negative-test coverage:
promotion decision immutability coverage:
audit/evidence coverage:
source mutation check:
evidence hashes:
review report:
completion record:
```

---

# 37. What Failed

Fill after validation.

```text
failures:
  - <none or list>
blocking_failures:
  - <none or list>
high_priority_failures:
  - <none or list>
non_blocking_failures:
  - <none or list>
rejected_deviations:
  - <none or list>
```

---

# 38. Issue Severity Classification

## 35.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
promotion allows without required evidence
promotion allows stale validation evidence
promotion allows failed validation evidence
promotion allows evidence from different commit
promotion allows unresolved hard blocker
promotion allows missing required approval
promotion accepts expired approval
promotion accepts wrong-scope approval
risk acceptance overrides hard blocker
risk acceptance overrides failed validation
promotion bypasses Policy / Capability Registry
promotion ignores required patch evidence
promotion proceeds without source commit
promotion creates Git branch/tag/commit without Git Acceptance Criteria
MCP can approve promotion by default
blocked promotion returns ALLOW
promotion decision is modified in place after final verdict
invalid promotion proceeds
source mutation occurs directly in this layer
secrets are logged
promotion decisions lack evidence
evidence hashes are missing
review report is missing
completion record is missing
required area remains NOT CHECKED
```

## 35.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
partial approval linkage coverage
partial risk acceptance coverage
partial Failure Taxonomy mapping
partial Git evidence
partial patch evidence
runtime artifact boundary exception lacks justification
review environment not recorded
deferred integration lacks deviation entry
```

## 35.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled future promotion action
Git write actions intentionally absent
MCP exposure intentionally not applicable
human approval intentionally stubbed with safe NEEDS_APPROVAL behavior
additional future-layer tests exist outside scoped promotion suite
```

---

# 39. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Approval | Risk | Policy | Patch | Git | Evidence | Schema | Runtime Artifact Boundary | MCP | Other>
    description: <what differs from the contract>
    reason: <why accepted>
    safety_impact: <none | low | medium | high>
    compensating_control: <test/evidence/control>
    accepted_status: NOT APPLICABLE | DEFERRED SAFELY | NON-BLOCKING FOLLOW-UP
    reviewer_decision: ACCEPTED | REJECTED
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
HIGH items cannot be accepted for DONE unless proven outside active runtime path.
Runtime artifact writes outside `.agentx-init/promotion/` require a deviation entry.
Missing evidence hashes cannot be accepted as a deviation for DONE.
MCP exposure deferral requires a deviation entry if any MCP file or entrypoint exists.
Git write absence can be NOT APPLICABLE only if no Git write entrypoint exists.
```

---

# 40. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Promotion package, schemas, tests, and runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including manifest, report, and completion record. |
| Promotion gate and release candidate | 1.0 | Gate and candidate models enforce source commit, evidence, status, immutability, and decision states. |
| Validation evidence and freshness | 1.0 | Compileall, pytest, schema, freshness, same-commit, and anti-replay checks pass. |
| Approval and risk acceptance | 1.0 | Approvals are scoped/unexpired; risk acceptance cannot override hard blockers. |
| Policy, patch, Git, MCP integration | 1.0 | Required integrations fail closed and cannot bypass authorities. |
| Blocked/invalid/negative behavior | 1.0 | Unsafe, malformed, stale, missing, wrong-scope, and denied promotions fail closed with evidence. |
| Audit/evidence and source safety | 1.0 | Histories, latest artifacts, manifest, report, hashes, redaction, clean source state, completion record. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for promotion control
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
promotion allows failed/stale/missing evidence caps score at 4.0
promotion allows unresolved hard blocker caps score at 4.0
promotion accepts expired or wrong-scope approval caps score at 5.0
risk acceptance overrides hard blocker caps score at 4.0
policy bypass caps score at 4.0
Git write without acceptance criteria caps score at 4.0
MCP promotion approval by default caps score at 4.0
source mutation by tests caps score at 7.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
```

---

# 41. GO / NO-GO Rules

## 38.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
promotion gate tests pass
release candidate tests pass
validation evidence tests pass
validation freshness tests pass
release candidate provenance tests pass
changed-file scope tests pass
monotonic timestamp tests pass
revalidation trigger tests pass
approval linkage tests pass or are not applicable
risk acceptance tests pass or are not applicable
policy integration tests pass
patch integration tests pass or are not applicable
git integration tests pass or are not applicable
mcp exposure tests pass or are not applicable
failure taxonomy tests pass
blocked-promotion tests pass
invalid-promotion tests pass
negative tests pass
promotion decision immutability tests pass
audit/evidence tests pass
evidence manifest exists
evidence hashes exist
review report exists
source mutation check passes
completion record exists
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 38.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
promotion allows missing evidence
promotion allows failed validation evidence
promotion allows stale validation evidence
promotion allows evidence from different commit
promotion allows candidate-affecting changes without revalidation
promotion allows uncovered changed files without justification
promotion allows contradictory or impossible evidence timestamps
promotion allows unresolved hard blockers
promotion accepts missing, expired, or wrong-scope required approval
risk acceptance overrides hard blocker
promotion bypasses policy
promotion ignores required patch evidence
promotion proceeds without source commit
promotion performs unapproved Git write action
MCP can approve promotion by default
blocked promotion returns ALLOW
promotion decision is modified in place after final verdict
invalid promotion proceeds
source mutation occurs directly in this layer
secrets are logged
promotion decisions lack evidence
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 42. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix gate decision logic
fix validation freshness checks
fix same-commit evidence checks
fix approval lookup checks
fix approval scope checks
fix risk acceptance checks
fix policy integration
fix patch evidence validation
fix Git state validation
fix MCP exposure blocking
fix failure_class mapping
fix blocked-promotion result formatting
fix invalid-promotion result formatting
fix evidence writing
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix secret redaction
fix tests to reflect the contract
fix runtime artifact boundary checks
```

Forbidden fixes:

```text
do not remove policy checks to pass tests
do not remove validation evidence checks to pass tests
do not accept stale tests as fresh
do not accept wrong-commit evidence
do not allow approval to override hard blockers
do not allow risk acceptance to override hard blockers
do not ignore patch evidence for source changes
do not allow Git write actions without acceptance criteria
do not allow MCP to approve promotion by default
do not mark NOT CHECKED as PASS
do not skip evidence writing
do not omit hashes for final DONE
do not log secrets
do not accept a BLOCKER as a deviation
```

---

# 43. Definition of Done

The Promotion / Release Gate is done when it can act as the final controlled gate before implementation work moves toward release.

It must prove:

```text
all target files exist
all schemas exist
all tests exist
promotion gate model validates
release candidate model validates
promotion decision model validates
validation evidence is checked
validation freshness is checked
validation evidence applies to the same source commit
risk acceptance cannot override hard blockers
approval linkage works or is safely not applicable
policy integration blocks denied promotion
patch integration checks required patch evidence
git integration checks source commit and source state
MCP exposure is absent, read-only/status-only, or safely blocked
failure taxonomy maps blocked/invalid/failure outcomes
blocked promotions fail closed
invalid promotions fail closed
negative tests prove unsafe promotions fail closed
promotion decisions are evidenced
release candidates are evidenced
latest artifacts are written atomically
evidence manifest is written
review report is written
evidence hashes are written
completion record is written
no source mutation occurs directly in this layer
no Git write occurs unless explicitly allowed and validated
no promotion proceeds with missing, failed, stale, wrong-commit, or invalid evidence
no promotion proceeds with unresolved hard blockers
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_promotion_schemas.py
git status --short
```

Expected:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

---

# 44. Final Done / Not-Done Verdict

Fill after validation.

```text
final_verdict: DONE | NOT DONE
implementation_rating: <0-10>
review_document_rating: 10/10
reason:
  - <summary>
remaining_blockers:
  - <none or list>
remaining_high_issues:
  - <none or list>
accepted_non_blocking_followups:
  - <none or list>
accepted_deviations:
  - <none or list>
```

A final verdict of `DONE` is invalid if:

```text
implementation_rating is below 10.0
reviewed commit is missing
review environment is missing
any required command was not run
any required command exit code is missing
any required area is NOT CHECKED
any required command is NOT RUN
any BLOCKER remains
evidence hashes are missing
review report is missing
completion record is missing
```

---

# 45. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/promotion/ exists
[ ] schemas exist
[ ] tests exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Promotion Gate:
[ ] promotion gate loads
[ ] promotion decision model validates
[ ] missing evidence blocks
[ ] failed evidence blocks
[ ] stale evidence blocks
[ ] wrong-commit evidence blocks
[ ] hard blockers block

Release Candidate:
[ ] candidate_id recorded
[ ] source commit recorded
[ ] branch recorded
[ ] validation evidence refs recorded
[ ] approval refs recorded where required
[ ] candidate immutability enforced after decision

Approvals / Risk:
[ ] required approval looked up
[ ] expired approval blocks
[ ] wrong-scope approval blocks
[ ] approval cannot override hard blockers
[ ] risk acceptance cannot override hard blockers
[ ] risk acceptance cannot override failed validation

Integration:
[ ] policy integration checked
[ ] patch evidence checked where source changes exist
[ ] Git/source-state checked where applicable
[ ] MCP exposure N/A or safely blocked
[ ] failure classes populated

Blocked / Invalid:
[ ] blocked promotion returns BLOCKED
[ ] invalid promotion returns INVALID
[ ] negative tests pass
[ ] blocked/invalid promotions write evidence

Evidence:
[ ] decision history written
[ ] candidate history written
[ ] blocked promotion history written
[ ] invalid promotion history written
[ ] latest artifacts written atomically
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written
[ ] secrets redacted

Safety:
[ ] no direct source mutation in this layer
[ ] no unapproved Git write
[ ] no promotion with missing/failed/stale/wrong-commit evidence
[ ] no promotion with unresolved hard blockers

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 46. Final Sign-Off Template

Use this after implementation validation.

```text
Promotion / Release Gate Validation — Commit <hash>

Reviewer / Environment:
- reviewer: <name or tool>
- reviewed commit: <hash>
- reviewed branch: <branch>
- reviewed at UTC: <timestamp>
- OS: <name/version>
- Python: <version>
- pytest: <version or NOT INSTALLED>

Status:
- initial git status: CLEAN/EXPECTED_RUNTIME_ARTIFACTS_ONLY/DIRTY
- compileall: PASS/FAIL, exit_code=<code>
- pytest: PASS/FAIL, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- promotion gate coverage: PASS/FAIL
- release candidate coverage: PASS/FAIL
- validation evidence coverage: PASS/FAIL
- approval linkage coverage: PASS/FAIL/N/A
- risk acceptance coverage: PASS/FAIL/N/A
- policy integration coverage: PASS/FAIL
- patch integration coverage: PASS/FAIL/N/A
- git integration coverage: PASS/FAIL/N/A
- MCP exposure coverage: PASS/FAIL/N/A
- failure taxonomy coverage: PASS/FAIL
- blocked-promotion coverage: PASS/FAIL
- invalid-promotion coverage: PASS/FAIL
- negative-test coverage: PASS/FAIL
- audit/evidence coverage: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- review report: PRESENT/MISSING
- source mutation check: PASS/FAIL
- completion record: PRESENT/MISSING

Reproducibility:
- exact commands recorded: YES/NO
- exit codes recorded: YES/NO
- output artifacts recorded: YES/NO
- final hashes recorded: YES/NO
- deviations recorded: YES/NO/N/A

Final decision:
DONE / NOT DONE

Implementation rating:
<0-10>

Evidence paths:
- evidence manifest: <path>, sha256=<hash>
- review report: <path>, sha256=<hash>
- completion record: <path>, sha256=<hash>

Remaining blockers:
- none / list blockers

Accepted non-blocking follow-ups:
- none / list follow-ups
```

---

---

# 47. Final Freeze Rule

This v3 document is frozen as the Promotion / Release Gate post-implementation review / DoD template.

Allowed future changes:

```text
PATCH: typo fixes, wording corrections, clearer examples
MINOR: additive optional checks that do not weaken existing safety requirements
MAJOR: changed promotion authority, changed Git release-write policy, changed approval semantics, changed risk acceptance semantics, changed evidence freshness semantics, or new required release action category
```

Blocked without major revision:

```text
allowing promotion with failed validation
allowing promotion with stale validation evidence
allowing promotion with wrong-commit evidence
allowing risk acceptance to override hard blockers
allowing human approval to override non-overridable safety blocks
allowing Git write actions without acceptance criteria
allowing MCP promotion approval by default
removing policy checks
removing evidence hashes
removing review report or completion record requirements
removing source-state checks
```

# 48. Final Rating

This v3 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the full v2 scope and adds the remaining promotion-control details: release-action boundaries, candidate provenance hashing, monotonic timestamp checks, re-validation triggers, authority-chain conflict resolution, stale approval/risk handling after candidate changes, decision supersession records, command-output hashes, changed-file scope controls, and a final freeze rule.
```
