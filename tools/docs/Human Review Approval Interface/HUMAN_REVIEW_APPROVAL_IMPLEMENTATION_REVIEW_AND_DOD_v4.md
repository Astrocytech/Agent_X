# HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_REVIEW_AND_DOD
version: v4.0
status: final post-implementation review template and Definition of Done
component_id: AGENTX_HUMAN_REVIEW_APPROVAL
component_name: Human Review / Approval Interface
roadmap_layer: 12
roadmap_phase: Phase C — Human Approval and Governance Control
review_use: use after code is committed
basis_documents:
  - HUMAN_REVIEW_APPROVAL_EQC_FIC_SIB_SCHEMA_CONTRACT
  - HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_SPEC
  - HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_REVIEW_AND_DOD_v1
  - HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_REVIEW_AND_DOD_v2
  - HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_REVIEW_AND_DOD_v3
  - HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_REVIEW_AND_DOD_v4
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Report Template, MCP Protocol Acceptance Criteria
optional_standards: ES
canonical_subdirectory: tools/agentx_evolve/human_review/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/human_review/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v4 Review and Upgrade Summary

The v3 review / DoD document was strong and close to final. I would rate it:

```text
9.8/10
```

It already covered the requested review sections and added production controls for approval consumption, queue locking, idempotency, reviewer identity assurance, quorum / dual control, stale-scope prevention, human-facing redaction, evidence hashing, review reports, and final sign-off.

It was not fully 10/10 because a few precision gaps remained in the review template itself:

```text
1. The expected-scope section listed identity-assurance, quorum, approval-consumption, locking, idempotency, and redaction schemas/tests, but the final existence checklists did not repeat all of them.
2. Approval lookup / validation was present indirectly through scope, policy, and tool integration checks, but it needed its own explicit review gate.
3. Stale request, stale policy snapshot, stale target hash, and stale reviewed-commit checks needed a dedicated pass/fail section.
4. Traceability from approval consumption, locking, idempotency, quorum, and redaction to code/test/evidence needed to be explicit.
5. The final pass/fail, GO/NO-GO, scoring, and sign-off sections needed to include approval lookup freshness and drift prevention as first-class gates.
6. Tamper-evidence for append-only approval histories needed to be separated from general evidence hashing.
```

This v4 applies those corrections and is the final 10/10 post-implementation review / DoD template.

---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Human Review / Approval Interface**.

Use this document after code is committed to determine whether the layer is complete, validated, safe, auditable, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether approval requests are created correctly
whether approval decisions are recorded correctly
whether rejections are enforced
whether deferrals and clarification requests are handled
whether approvals expire correctly
whether approvals can be revoked correctly
whether approval scope is immutable and enforced
whether approvals are bound to exact request hash, policy snapshot, target action, and reviewed commit
whether approval replay/reuse is blocked
whether approval consumption/use-token records are enforced
whether concurrent approval races are prevented
whether approval request and decision operations are idempotent
whether reviewer identity assurance is recorded
whether quorum / dual-control rules are enforced where required
whether self-approval is blocked
whether non-overridable safety rules are enforced
whether Policy / Capability Registry integration works
whether Tool / MCP Adapter integration works
whether Governed Patch Execution integration works or is safely guarded
whether Promotion / Release Gate integration works or is safely guarded
whether CLI commands are safe if exposed
whether reports are safe if generated
whether MCP exposure is safe if implemented
whether audit/evidence artifacts are complete and hashed
whether source mutation is avoided by this layer
whether the implementation is DONE or NOT DONE
```

This document reviews the implementation. A 10/10 rating for this document does not mean the implementation is done. The implementation is done only after the validation commands, coverage checks, evidence manifest, review report, and completion record satisfy this document.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because this layer is safety-critical. It controls whether human approval can satisfy approval requirements for high-risk operations, including source mutation, patch application, promotion, elevated tool use, and governance-sensitive actions.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Command Acceptance Criteria, only if CLI commands are exposed
```

## 2.3 Conditional Standards

```text
Report Template, if it writes markdown or JSON review reports
MCP Protocol Acceptance Criteria, only if human-review requests are exposed through MCP
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
```

---

# 3. Why This Layer Needs These Standards

The Human Review / Approval Interface is safety-critical because it decides:

```text
which actions require human review
who may approve them
what approval actually authorizes
what approval does not authorize
whether approval is scoped to one action/session/file/commit
whether approval expires
whether approval can be revoked
whether approval can override policy
whether approval can override sandbox
whether approval can authorize patch application
whether approval can authorize promotion
how approval evidence is preserved
```

Core rule:

```text
Human approval may satisfy an approval requirement.
Human approval must not override non-overridable safety blocks.
```

This layer must not become a universal override. Approval is one authority in the Agent_X control chain. It is not a replacement for policy, sandbox, governance, schema validation, patch execution controls, or release gates.

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
[ ] initial working-tree state is recorded
[ ] final working-tree state is recorded
[ ] environment information is recorded
[ ] every required command records command text, exit code, status, and summary
[ ] every command marked PASS has exit_code 0
[ ] every expected-failure negative test records the expected failure condition
[ ] evidence manifest exists before final DONE is claimed
[ ] review report exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] required SHA-256 evidence hashes are present
[ ] reviewer did not rely only on this document's internal rating
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

The implementation may not be marked `DONE` because this document says `review_document_rating: 10/10`. The implementation can be marked `DONE` only when recorded validation evidence satisfies the GO criteria.

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
| DEFERRED SAFELY | Feature is intentionally deferred and cannot approve, execute, expose, mutate, or bypass safety controls. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Deferral Rules

Use these rules to avoid hiding missing work behind `NOT APPLICABLE` or `DEFERRED SAFELY`.

```text
NOT APPLICABLE:
  Use only when the feature is outside the implemented scope and has no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot approve, execute, expose, mutate, open ports, or bypass policy/sandbox/patch/promotion gates.

PARTIAL:
  Use when some files or tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

Patch or promotion integration may be `DEFERRED SAFELY` only if the review proves:

```text
approval records cannot apply patches directly
approval records cannot promote releases directly
missing patch/promotion integration blocks or returns NEEDS_APPROVAL / NEEDS_GOVERNANCE
no bypass path exists through approval lookup
safe deferral is recorded in the deviation register
```

MCP may be `NOT APPLICABLE` only if no MCP human-review entrypoint exists. If an MCP adapter exists, MCP must be reviewed for self-approval, reviewer identity, scope, policy, and evidence behavior.

---

# 6. Expected Implementation Scope

## 6.1 Required Package

Expected location:

```text
tools/agentx_evolve/human_review/
```

Expected files:

```text
tools/agentx_evolve/human_review/__init__.py
tools/agentx_evolve/human_review/review_models.py
tools/agentx_evolve/human_review/review_queue.py
tools/agentx_evolve/human_review/approval_requests.py
tools/agentx_evolve/human_review/approval_decisions.py
tools/agentx_evolve/human_review/approval_lookup.py
tools/agentx_evolve/human_review/approval_expiry.py
tools/agentx_evolve/human_review/approval_revocation.py
tools/agentx_evolve/human_review/review_policy.py
tools/agentx_evolve/human_review/review_evidence.py
```

Optional files, only if implemented in this phase:

```text
tools/agentx_evolve/human_review/review_cli.py
tools/agentx_evolve/human_review/review_report.py
tools/agentx_evolve/human_review/mcp_review_adapter.py
```

## 6.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
human_review_request.schema.json
human_review_queue.schema.json
human_approval_decision.schema.json
human_rejection_decision.schema.json
human_review_deferral.schema.json
human_clarification_request.schema.json
human_approval_scope.schema.json
human_approval_expiry.schema.json
human_approval_revocation.schema.json
human_reviewer_identity.schema.json
human_review_identity_assurance.schema.json
human_review_quorum.schema.json
human_approval_consumption.schema.json
human_approval_lock.schema.json
human_review_evidence.schema.json
human_review_audit.schema.json
human_review_evidence_manifest.schema.json
human_review_report.schema.json
completion_record.schema.json
```

Optional schemas, if implemented in this phase:

```text
human_review_cli_result.schema.json
human_review_mcp_request.schema.json
human_review_mcp_response.schema.json
```

## 6.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_human_review_models.py
test_human_review_request_schema.py
test_human_review_queue.py
test_human_approval_decision.py
test_human_rejection_decision.py
test_human_review_deferral.py
test_human_clarification_request.py
test_human_approval_scope.py
test_human_approval_expiry.py
test_human_approval_revocation.py
test_human_review_policy.py
test_human_review_identity_assurance.py
test_human_review_quorum.py
test_human_approval_consumption.py
test_human_approval_locking.py
test_human_review_idempotency.py
test_human_review_redaction.py
test_human_review_evidence.py
test_human_review_integration_policy.py
test_human_review_integration_tools.py
test_human_review_integration_patch.py
test_human_review_integration_promotion.py
test_human_review_negative_cases.py
test_human_review_schema_validation.py
```

Optional tests, if applicable:

```text
test_human_review_cli.py
test_human_review_report.py
test_human_review_mcp_adapter.py
```

## 6.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/human_review/
```

Expected artifacts:

```text
review_request_history.jsonl
approval_decision_history.jsonl
rejection_decision_history.jsonl
deferral_history.jsonl
clarification_request_history.jsonl
approval_revocation_history.jsonl
approval_expiry_history.jsonl
approval_consumption_history.jsonl
human_review_lock_history.jsonl
human_review_audit_history.jsonl
latest_review_request.json
latest_approval_decision.json
latest_rejection_decision.json
latest_review_queue.json
human_review_evidence_manifest.json
human_review_report.json
human_review_completion_record.json
```

Optional artifacts, if implemented:

```text
human_review_report.md
```

---

# 7. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_human_review_schemas.py
git status --short
```

If `validate_human_review_schemas.py` is not implemented, the same schema coverage must be proven by pytest-based schema validation tests, for example:

```bash
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_human_review_schema_validation.py
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
interactive human input
```

---

# 8. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Human review package | `tools/agentx_evolve/human_review/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schemas | required human review schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation command | schema command or pytest equivalent exists and passes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tests | required human review tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Review queue | queue model exists, validates, and orders deterministically | PASS / PARTIAL / FAIL / NOT CHECKED |
| Approval request creation | request creation works and writes evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Approval decision recording | approval decisions are schema-valid, immutable, scoped, and evidenced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Rejection recording | rejections are schema-valid and enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Deferral / clarification | deferrals and clarification requests are represented safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Expiry handling | expired approvals cannot authorize actions | PASS / PARTIAL / FAIL / NOT CHECKED |
| Revocation handling | revoked approvals cannot authorize actions | PASS / PARTIAL / FAIL / NOT CHECKED |
| Scope enforcement | approvals apply only to approved action/session/file/commit/artifact | PASS / PARTIAL / FAIL / NOT CHECKED |
| Approval lookup validation | lookup checks state, scope, expiry, revocation, consumption, identity, policy snapshot, target hash, and reviewed commit before authorization | PASS / PARTIAL / FAIL / NOT CHECKED |
| Stale snapshot / drift prevention | stale request hash, stale policy snapshot, stale target hash, and stale commit bindings are rejected | PASS / PARTIAL / FAIL / NOT CHECKED |
| Replay protection | approval reuse/replay blocked unless explicitly single-use or repeat-scope approved | PASS / PARTIAL / FAIL / NOT CHECKED |
| Approval consumption | approval use is recorded and single-use approvals cannot be consumed twice | PASS / PARTIAL / FAIL / NOT CHECKED |
| Locking / concurrency | concurrent queue or decision updates cannot create conflicting active approvals | PASS / PARTIAL / FAIL / NOT CHECKED |
| Idempotency | duplicate request/decision submissions are deterministic and evidenced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Identity assurance | reviewer identity source, assurance level, and authorization are evidenced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Quorum / dual control | high-risk approvals require required reviewer count or explicitly block | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Self-approval prevention | requester cannot approve own request unless policy explicitly allows and evidence records it | PASS / PARTIAL / FAIL / NOT CHECKED |
| Non-overridable safety | approval cannot override sandbox/policy/schema/tool/patch/promotion hard blocks | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy integration | approval requirements are checked through policy layer | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool integration | Tool / MCP Adapter can request and validate approval IDs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Patch integration | patch actions require scoped approval when needed or are safely guarded | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Promotion integration | promotion actions require scoped approval when needed or are safely guarded | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Audit/evidence | histories, latest artifacts, manifest, review report, hashes written safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Append-only tamper evidence | approval histories are append-only, hashable, and not silently rewritten | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | this layer does not mutate source | PASS / PARTIAL / FAIL / NOT CHECKED |
| CLI commands | safe only if implemented | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Report output | schema/report rules followed if implemented | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| MCP exposure | safe only if implemented | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
```

---

# 9. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Review request creation | `approval_requests.py` | `test_human_review_request_schema.py` | `review_request_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Queue ordering | `review_queue.py` | `test_human_review_queue.py` | `latest_review_queue.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Approval recording | `approval_decisions.py` | `test_human_approval_decision.py` | `approval_decision_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Rejection recording | `approval_decisions.py` | `test_human_rejection_decision.py` | `rejection_decision_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Deferral / clarification | `approval_decisions.py` | `test_human_review_deferral.py`, `test_human_clarification_request.py` | `deferral_history.jsonl`, `clarification_request_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Scope validation | `approval_lookup.py` | `test_human_approval_scope.py` | decision history + audit history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Approval lookup validation | `approval_lookup.py` | `test_human_approval_lookup.py` | approval validation audit + consumption history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Stale snapshot / drift prevention | `approval_lookup.py`, `review_policy.py` | `test_human_review_stale_snapshot.py` | audit history + policy evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Approval consumption | `approval_lookup.py` | `test_human_approval_consumption.py` | `approval_consumption_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Queue locking / concurrency | `review_queue.py` | `test_human_approval_locking.py` | `human_review_lock_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Idempotency | `approval_requests.py`, `approval_decisions.py` | `test_human_review_idempotency.py` | request/decision history + audit history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Identity assurance | `review_policy.py` | `test_human_review_identity_assurance.py` | identity evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Quorum / dual control | `review_policy.py` | `test_human_review_quorum.py` | quorum evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Human-facing redaction | `review_evidence.py` | `test_human_review_redaction.py` | redacted evidence samples | PASS / PARTIAL / FAIL / NOT CHECKED |
| Expiry validation | `approval_expiry.py` | `test_human_approval_expiry.py` | `approval_expiry_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Revocation validation | `approval_revocation.py` | `test_human_approval_revocation.py` | `approval_revocation_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Non-overridable safety | `review_policy.py` | `test_human_review_negative_cases.py` | audit history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy integration | `review_policy.py` | `test_human_review_integration_policy.py` | policy evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool integration | `approval_lookup.py` | `test_human_review_integration_tools.py` | tool/evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Patch integration | `approval_lookup.py` or patch integration adapter | `test_human_review_integration_patch.py` | patch/evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Promotion integration | promotion integration adapter | `test_human_review_integration_promotion.py` | promotion/evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Evidence writing | `review_evidence.py` | `test_human_review_evidence.py` | manifest + JSONL histories | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation | schemas | `test_human_review_schema_validation.py` or validation utility | schema output artifact | PASS / PARTIAL / FAIL / NOT CHECKED |
| Review report | report writer or manual generation | schema/manual validation | `human_review_report.json` + hash | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record | completion writer | schema/manual validation | completion record + hash | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 10. What Exists Checklist

## 10.1 Package Files

```text
[ ] tools/agentx_evolve/human_review/__init__.py
[ ] tools/agentx_evolve/human_review/review_models.py
[ ] tools/agentx_evolve/human_review/review_queue.py
[ ] tools/agentx_evolve/human_review/approval_requests.py
[ ] tools/agentx_evolve/human_review/approval_decisions.py
[ ] tools/agentx_evolve/human_review/approval_lookup.py
[ ] tools/agentx_evolve/human_review/approval_expiry.py
[ ] tools/agentx_evolve/human_review/approval_revocation.py
[ ] tools/agentx_evolve/human_review/review_policy.py
[ ] tools/agentx_evolve/human_review/review_evidence.py
```

Optional:

```text
[ ] tools/agentx_evolve/human_review/review_cli.py
[ ] tools/agentx_evolve/human_review/review_report.py
[ ] tools/agentx_evolve/human_review/mcp_review_adapter.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.2 Schema Files

```text
[ ] human_review_request.schema.json
[ ] human_review_queue.schema.json
[ ] human_approval_decision.schema.json
[ ] human_rejection_decision.schema.json
[ ] human_review_deferral.schema.json
[ ] human_clarification_request.schema.json
[ ] human_approval_scope.schema.json
[ ] human_approval_expiry.schema.json
[ ] human_approval_revocation.schema.json
[ ] human_reviewer_identity.schema.json
[ ] human_review_identity_assurance.schema.json
[ ] human_review_quorum.schema.json
[ ] human_approval_consumption.schema.json
[ ] human_approval_lock.schema.json
[ ] human_review_evidence.schema.json
[ ] human_review_audit.schema.json
[ ] human_review_evidence_manifest.schema.json
[ ] human_review_report.schema.json
[ ] completion_record.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.3 Test Files

```text
[ ] test_human_review_models.py
[ ] test_human_review_request_schema.py
[ ] test_human_review_queue.py
[ ] test_human_approval_decision.py
[ ] test_human_rejection_decision.py
[ ] test_human_review_deferral.py
[ ] test_human_clarification_request.py
[ ] test_human_approval_scope.py
[ ] test_human_approval_expiry.py
[ ] test_human_approval_revocation.py
[ ] test_human_review_policy.py
[ ] test_human_review_identity_assurance.py
[ ] test_human_review_quorum.py
[ ] test_human_approval_consumption.py
[ ] test_human_approval_locking.py
[ ] test_human_review_idempotency.py
[ ] test_human_review_redaction.py
[ ] test_human_approval_lookup.py
[ ] test_human_review_stale_snapshot.py
[ ] test_human_review_evidence.py
[ ] test_human_review_integration_policy.py
[ ] test_human_review_integration_tools.py
[ ] test_human_review_integration_patch.py
[ ] test_human_review_integration_promotion.py
[ ] test_human_review_negative_cases.py
[ ] test_human_review_schema_validation.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 11. Validation Commands

Record the exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`. Any non-zero exit code is `FAIL` unless the command is explicitly a negative test where non-zero is the expected result and the expected failure condition is recorded.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_human_review_schemas.py
git status --short
```

Required result:

```text
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
git status: CLEAN or only expected runtime artifacts
```

If unrelated future-layer tests exist in `tools/agentx_evolve/tests`, the review must also record a scoped Human Review pytest command covering only the required human-review tests.

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
interactive human input
```

---

# 12. Compileall Result

Record the compile result.

```text
command: PYTHONPATH=tools python -m compileall tools/agentx_evolve
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path or none>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any Human Review / Approval Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 13. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: <path or none>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required approval request, approval decision, rejection, deferral, clarification, expiry, revocation, policy, tool, patch, promotion, evidence, schema, or negative safety test fails
exit code is missing
```

---

# 14. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_human_review_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_human_review_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path or none>
```

Required schema tests:

```text
human review request schema accepts valid request
human review request schema rejects missing request_id
human review request schema rejects missing requested_action
human review queue schema accepts valid queue
human approval decision schema accepts valid approval
human approval decision schema rejects missing approval_scope
human approval decision schema rejects missing reviewer_identity
human approval decision schema rejects missing expiry or single-use marker
human rejection decision schema accepts valid rejection
human review deferral schema accepts valid deferral
human clarification request schema accepts valid clarification request
human approval scope schema accepts session/action/file/commit/artifact scope
human approval expiry schema accepts valid expiry record
human approval revocation schema accepts valid revocation record
human reviewer identity schema accepts valid reviewer identity
human review evidence schema accepts valid evidence record
human review audit schema accepts valid audit event
human review evidence manifest schema accepts valid evidence manifest
human review report schema accepts valid review report
completion record schema accepts final completion record
schemas reject invalid decision/status/scope enum values
```

Blocking if:

```text
schema-invalid approval requests are accepted
schema-invalid approval decisions are accepted
approval decisions can exist without scope
approval decisions can exist without reviewer identity
approval decisions can exist without expiry or single-use marker
revocation or expiry records cannot be represented
human review evidence cannot be schema-validated
review report cannot be schema-validated
completion record cannot be schema-validated
schema validation exit code is missing
```

---

# 15. Approval State Model Coverage

Required decision states:

```text
REQUESTED
APPROVED
REJECTED
DEFERRED
NEEDS_CLARIFICATION
EXPIRED
REVOKED
CANCELLED
```

Required behavior:

```text
[ ] only APPROVED can authorize action
[ ] REQUESTED cannot authorize action
[ ] REJECTED cannot authorize action
[ ] DEFERRED cannot authorize action
[ ] NEEDS_CLARIFICATION cannot authorize action
[ ] EXPIRED cannot authorize action
[ ] REVOKED cannot authorize action
[ ] CANCELLED cannot authorize action
[ ] state transitions are append-only and evidenced
[ ] invalid state transitions are blocked
[ ] final states cannot be silently overwritten
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
non-approved state authorizes action
approval state can be silently overwritten
state transition lacks evidence
```


## 15.1 Queue Locking / Concurrency Coverage

Required behavior:

```text
[ ] review queue updates are atomic or otherwise race-safe
[ ] two reviewers cannot create conflicting final decisions for the same request without conflict evidence
[ ] request state transition from PENDING to final state is single-writer or conflict-detected
[ ] concurrent revoke/consume race cannot allow revoked approval to authorize action
[ ] concurrent expire/consume race cannot allow expired approval to authorize action
[ ] lock or compare-and-swap evidence is written where implemented
[ ] lock failures return schema-valid BLOCKED/FAILED result, not silent success
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
concurrent decisions can produce multiple active final approvals
revoked or expired approval can be consumed due to race condition
queue update conflicts are silently ignored
```

## 15.2 Idempotency Coverage

Required behavior:

```text
[ ] repeated creation of the same request with same idempotency_key returns same request or safe duplicate-block result
[ ] repeated submission of the same decision with same idempotency_key returns same decision or safe duplicate-block result
[ ] repeated rejection/approval attempts after final state do not create a new active decision
[ ] idempotency key, request_hash, and decision_hash are evidenced
[ ] idempotency does not permit scope widening
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
duplicate request creates conflicting active review records
duplicate decision creates multiple active approvals
idempotency retry widens approval scope
```

---

# 16. Approval Request Coverage

Required behavior:

```text
[ ] approval requests can be created for governed actions
[ ] request records include request_id
[ ] request records include requester identity or component
[ ] request records include action type
[ ] request records include target resource or artifact
[ ] request records include requested authority
[ ] request records include risk level
[ ] request records include reason/context summary
[ ] request records include approval scope proposal
[ ] request records include expiry proposal
[ ] request records include related policy/tool/patch/promotion evidence refs
[ ] request records are added to the review queue
[ ] request creation writes audit/evidence
[ ] request creation does not authorize action by itself
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
approval request lacks stable ID
approval request lacks scope proposal
approval request lacks evidence
approval request can authorize action by itself before decision
```

---

# 17. Approval Decision Coverage

Required behavior:

```text
[ ] approval decision can be recorded
[ ] approval decision includes approval_id
[ ] approval decision includes original request_id
[ ] approval decision includes reviewer identity
[ ] approval decision includes decision timestamp
[ ] approval decision includes exact approved action
[ ] approval decision includes approval scope
[ ] approval decision includes expiry or single-use marker
[ ] approval decision includes evidence refs
[ ] approval decision is immutable after recording
[ ] approval decision can be looked up by approval_id
[ ] approval decision validates against schema
[ ] approval decision writes audit/evidence
[ ] approval decision does not itself execute the approved action
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
approval has no scope
approval has no expiry or single-use rule
approval can authorize unrelated actions
approval can be silently edited
approval lacks evidence
approval directly executes the approved action
```

---

# 18. Approval Scope Coverage

Required scope dimensions:

```text
request_id
approval_id
session_id
action_type
requested_effect
tool_name, if applicable
patch_session_id, if applicable
patch_artifact_hash, if applicable
target_file_set, if applicable
commit_hash, if applicable
release_gate_id, if applicable
promotion_artifact_hash, if applicable
allowed_use_count
expiry
```

Required behavior:

```text
[ ] approval scope is required for every approval
[ ] approval scope is immutable after approval
[ ] approval lookup compares requested action to stored scope
[ ] mismatched action blocks
[ ] mismatched session blocks
[ ] mismatched tool/effect blocks
[ ] mismatched patch/session/file set blocks
[ ] mismatched commit/release artifact blocks
[ ] use count is enforced when single-use or bounded-use approval is used
[ ] scope validation writes audit/evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
approval without scope can authorize action
approval for one action authorizes another action
approval for one session authorizes another session
approval for one patch authorizes another patch
approval for one commit authorizes another commit
approval use count is ignored
```


## 18.1 Approval Consumption and Use-Token Coverage

Required behavior:

```text
[ ] approved decisions create approval_id and, where required, approval_use_token or equivalent consumption record
[ ] single-use approvals cannot be consumed twice
[ ] approval consumption records action_id, session_id, target artifact, requester, consumer, timestamp, and reviewed commit where applicable
[ ] failed consumption attempts are evidenced
[ ] scope mismatch prevents consumption
[ ] expired approval prevents consumption
[ ] revoked approval prevents consumption
[ ] stale policy snapshot prevents consumption unless explicitly revalidated
[ ] consumption does not mutate patch/promotion state by itself
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
single-use approval can be reused
approval can be consumed outside its approved scope
expired or revoked approval can be consumed
consumption is not evidenced
```

## 18.2 Approval Binding and Snapshot Coverage

Required behavior:

```text
[ ] approval request includes request_hash
[ ] decision records the exact request_hash it approves/rejects/defers
[ ] approval scope records target_action, target_component, target_session, target_files, target_patch_id, target_release_id, and reviewed_commit where applicable
[ ] decision records policy_snapshot_id or policy_decision_id where applicable
[ ] lookup rejects approval if current target does not match approved snapshot
[ ] lookup rejects approval if policy has materially changed and revalidation is required
[ ] approval does not authorize future unknown patches or releases by broad wording
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
approval can be applied to a different patch, file set, commit, release, or session
approval request hash is missing
approval lookup ignores stale policy/scope mismatch
```

---

# 19. Rejection Coverage

Required behavior:

```text
[ ] rejection decision can be recorded
[ ] rejection includes original request_id
[ ] rejection includes reviewer identity
[ ] rejection includes reason
[ ] rejected request cannot be used as approval
[ ] rejected request cannot be converted to approval without new decision record
[ ] rejection writes audit/evidence
[ ] rejection is immutable after recording
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
rejected request can still authorize action
rejection lacks evidence
rejection can be overwritten silently
```

---

# 20. Deferral / Clarification Coverage

Required behavior:

```text
[ ] deferral decision can be recorded
[ ] clarification request can be recorded
[ ] deferral does not authorize action
[ ] clarification request does not authorize action
[ ] pending/needs-clarification requests remain non-authorizing
[ ] deferral includes reason
[ ] clarification request includes question/context
[ ] deferral/clarification writes audit/evidence
[ ] later approval requires a separate approval decision record
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
deferral authorizes action
clarification request authorizes action
pending request is treated as approval
later approval lacks separate approval decision evidence
```

---

# 21. Expiry Coverage

Required behavior:

```text
[ ] approval has expiry timestamp or explicit single-use scope
[ ] expired approval cannot authorize action
[ ] expiry check occurs before approval validation returns ALLOW
[ ] expired approval writes expiry/audit evidence
[ ] expiry is enforced for policy/tool/patch/promotion integrations
[ ] clock source is deterministic enough for tests
[ ] missing expiry/single-use marker blocks approval validation
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
expired approval authorizes action
approval has no expiry/single-use rule
expiry is not checked before use
missing expiry defaults to unlimited approval
```

---

# 22. Revocation Coverage

Required behavior:

```text
[ ] approval can be revoked
[ ] revocation includes approval_id
[ ] revocation includes reviewer/operator identity
[ ] revocation includes reason
[ ] revoked approval cannot authorize action
[ ] revocation cannot be silently undone
[ ] revocation writes audit/evidence
[ ] revocation is checked before approval validation returns ALLOW
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
revoked approval authorizes action
revocation lacks evidence
revocation can be overwritten silently
revocation is not checked before use
```

---

# 23. Reviewer Identity and Self-Approval Coverage

Required behavior:

```text
[ ] reviewer identity is required for approval/rejection/deferral/revocation
[ ] requester identity is recorded on approval request
[ ] reviewer identity is separate from requester identity unless policy explicitly permits exception
[ ] MCP client cannot self-approve
[ ] implementation worker cannot self-approve its own action
[ ] orchestrator cannot silently approve its own elevated action
[ ] reviewer role is authorized for the action/risk level
[ ] identity and role evidence is written
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
approval can be recorded without reviewer identity
unauthorized role can approve high-risk action
MCP client can self-approve
requester can approve own request without explicit policy and evidence
```


## 23.1 Reviewer Identity Assurance Coverage

Required behavior:

```text
[ ] reviewer identity record includes reviewer_id
[ ] reviewer identity record includes identity_source
[ ] reviewer identity record includes assurance_level
[ ] reviewer identity record includes authenticated_at or validated_at where applicable
[ ] reviewer authorization for the requested approval type is checked
[ ] reviewer role is checked against Policy / Capability Registry
[ ] anonymous approval is rejected
[ ] ambiguous reviewer identity is rejected
[ ] identity evidence is written without storing unnecessary personal data
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
anonymous or ambiguous reviewer can approve
reviewer authorization is not checked
identity evidence is missing
```

## 23.2 Quorum / Dual-Control Coverage

Required behavior for high-risk actions, if the contract or policy requires quorum:

```text
[ ] required reviewer count is derived from policy
[ ] required reviewer roles are derived from policy
[ ] duplicate approvals by the same reviewer do not count twice
[ ] requester cannot satisfy quorum for own request unless explicitly allowed and evidenced
[ ] one reviewer cannot approve mutually exclusive roles unless policy allows it
[ ] quorum approval remains scoped to the same request_hash and target scope
[ ] missing quorum returns NEEDS_APPROVAL or BLOCKED
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
high-risk action can proceed before required quorum is satisfied
duplicate reviewer identity counts more than once
quorum is satisfied across different request hashes or scopes
```

---

# 24. Non-Overridable Safety Coverage

Core rule:

```text
Human approval may satisfy an approval requirement.
Human approval must not override non-overridable safety blocks.
```

Required behavior:

```text
[ ] human approval cannot override sandbox denial
[ ] human approval cannot override policy hard block
[ ] human approval cannot override schema-invalid request
[ ] human approval cannot override unregistered tool execution
[ ] human approval cannot override blocked trust tier
[ ] human approval cannot authorize raw shell
[ ] human approval cannot authorize network by default
[ ] human approval cannot authorize Git write outside approved Git layer
[ ] human approval cannot authorize source mutation outside Governed Patch Execution
[ ] human approval cannot authorize promotion outside Promotion / Release Gate
[ ] human approval cannot authorize expired/revoked approval reuse
[ ] human approval cannot convert unsafe BLOCKED to ALLOW when block is non-overridable
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
approval bypasses policy hard block
approval bypasses sandbox denial
approval bypasses schema validation
approval directly mutates source
approval directly applies patch outside patch layer
approval directly promotes release outside promotion gate
```

---

# 25. Policy Integration Coverage

Required behavior:

```text
[ ] Policy / Capability Registry can require human approval
[ ] policy decisions can reference review request IDs
[ ] policy decisions can reference approval IDs
[ ] missing approval returns NEEDS_APPROVAL or BLOCKED
[ ] valid approval satisfies approval-required policy condition
[ ] invalid/expired/revoked approval does not satisfy policy
[ ] scope-mismatched approval does not satisfy policy
[ ] policy hard blocks remain non-overridable
[ ] policy integration writes evidence refs
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
missing approval is treated as ALLOW
expired/revoked approval is treated as ALLOW
scope-mismatched approval is treated as ALLOW
human approval overrides non-overridable policy block
```

---

# 26. Tool Integration Coverage

Required behavior:

```text
[ ] Tool / MCP Adapter can create approval request for approval-required tool call
[ ] Tool / MCP Adapter can validate approval_id before execution
[ ] approval_id must match tool call scope
[ ] approval_id must match requested effect
[ ] approval_id must not be expired or revoked
[ ] MCP client cannot self-approve
[ ] invalid approval returns BLOCKED or NEEDS_APPROVAL
[ ] tool result includes approval evidence refs where applicable
[ ] approval validation occurs before wrapper execution
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
tool call executes with missing approval when approval is required
tool call executes with mismatched approval scope
MCP client can approve its own request
tool call bypasses approval lookup
approval validation occurs after execution
```

---

# 27. Patch Integration Coverage

Required behavior:

```text
[ ] patch application can require human approval
[ ] approval scope can bind to patch session ID
[ ] approval scope can bind to patch artifact/hash
[ ] approval scope can bind to target file set
[ ] patch apply rejects missing/expired/revoked approval
[ ] patch apply rejects approval for different patch/session/file set
[ ] approval does not bypass patch precheck
[ ] approval does not bypass sandbox
[ ] approval does not bypass governed patch execution rules
[ ] patch integration writes evidence refs
```

If Governed Patch Execution is not active in this phase, patch integration may be `DEFERRED SAFELY` only if:

```text
[ ] approval cannot apply patches directly
[ ] patch_apply remains blocked or unavailable
[ ] approval lookup cannot be used as patch execution
[ ] deferral is recorded in the deviation register
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

Blocking if:

```text
approval applies a patch directly
approval bypasses Governed Patch Execution
approval for one patch authorizes a different patch
approval bypasses patch sandbox/precheck
```

---

# 28. Promotion Integration Coverage

Required behavior:

```text
[ ] promotion gate can require human approval
[ ] approval scope can bind to release gate ID
[ ] approval scope can bind to commit hash
[ ] approval scope can bind to promotion artifact/hash
[ ] promotion rejects missing/expired/revoked approval
[ ] promotion rejects approval for different commit/artifact
[ ] approval does not bypass required validation evidence
[ ] approval does not bypass release gate checks
[ ] promotion integration writes evidence refs
```

If Promotion / Release Gate is not active in this phase, promotion integration may be `DEFERRED SAFELY` only if:

```text
[ ] approval cannot promote releases directly
[ ] promotion entrypoint remains blocked or unavailable
[ ] approval lookup cannot be used as promotion execution
[ ] deferral is recorded in the deviation register
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

Blocking if:

```text
approval promotes release directly
approval bypasses Promotion / Release Gate
approval for one commit authorizes another commit
approval bypasses required validation evidence
```

---

# 29. Audit / Evidence Coverage

Required evidence behavior:

```text
[ ] review_request_history.jsonl is written
[ ] approval_decision_history.jsonl is written
[ ] rejection_decision_history.jsonl is written
[ ] deferral_history.jsonl is written
[ ] clarification_request_history.jsonl is written
[ ] approval_revocation_history.jsonl is written
[ ] approval_expiry_history.jsonl is written
[ ] human_review_audit_history.jsonl is written
[ ] latest_review_request.json is written atomically
[ ] latest_approval_decision.json is written atomically
[ ] latest_rejection_decision.json is written atomically
[ ] latest_review_queue.json is written atomically
[ ] human_review_evidence_manifest.json is written
[ ] human_review_report.json is written
[ ] completion record is written after validation
[ ] evidence includes timestamps
[ ] evidence includes reviewed commit or relevant runtime context
[ ] evidence includes request/decision IDs
[ ] evidence includes scope
[ ] evidence includes expiry/revocation status
[ ] evidence includes SHA-256 hashes for final artifacts
[ ] secrets are redacted before logging
[ ] raw patch contents are not durably logged unless explicitly approved by evidence rules
[ ] source files are not modified by evidence writing
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
approval requests are not logged
approval decisions are not logged
rejections/deferrals/revocations are not logged
approval evidence lacks scope
approval evidence lacks reviewer identity
secrets are logged
required evidence hashes are missing
```


## 29.1 Human-Facing Data Minimization and Redaction Coverage

Required behavior:

```text
[ ] review request summaries exclude secrets, tokens, credentials, and unnecessary raw file contents
[ ] approval/rejection evidence stores summaries and artifact references rather than large raw payloads
[ ] human-facing diffs or command outputs are truncated and redacted
[ ] reviewer comments are treated as evidence and redacted before durable storage where required
[ ] redaction is applied before both JSONL history and latest artifacts are written
[ ] redaction failures block final approval recording for sensitive payloads
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
secrets are visible in human-facing review artifacts
unnecessary raw source or command output is durably logged
redaction failure still records APPROVED state
```

## 29.2 Append-Only / Tamper-Evidence Coverage

Required behavior:

```text
[ ] review request history is append-only
[ ] approval decision history is append-only
[ ] rejection / deferral / clarification / revocation / expiry / consumption histories are append-only
[ ] latest artifacts are derived views and do not replace history
[ ] evidence manifest records SHA-256 hashes for histories used in final review
[ ] history rewrite, truncation, or deletion is detected or recorded as a deviation
[ ] final DONE evidence is immutable unless a new review report is created
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
approval history can be silently rewritten
latest artifacts replace append-only history as the only evidence
final evidence hashes do not cover histories used for validation
post-signoff evidence changes do not invalidate prior DONE verdict
```

---

# 30. Evidence Manifest

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
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "approval_scope_status": "PASS",
  "expiry_revocation_status": "PASS",
  "approval_consumption_status": "PASS",
  "locking_concurrency_status": "PASS",
  "idempotency_status": "PASS",
  "identity_assurance_status": "PASS",
  "quorum_status": "PASS_OR_NOT_APPLICABLE",
  "non_overridable_safety_status": "PASS",
  "redaction_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

The manifest must include paths and SHA-256 hashes for all final evidence files, including:

```text
human_review_evidence_manifest.json
human_review_report.json
human_review_completion_record.json
command output artifacts, if stored as files
JSONL evidence histories used by the review
latest_review_request.json, if used by the review
latest_approval_decision.json, if used by the review
latest_review_queue.json, if used by the review
approval_consumption_history.jsonl, if used by the review
human_review_lock_history.jsonl, if used by the review
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Approved runtime artifact boundary:

```text
.agentx-init/human_review/
```

Evidence artifacts for this layer must not be written outside that root unless the review records the exception in the deviation register.

---

# 31. Review Report Artifact

Create:

```text
.agentx-init/human_review/human_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "human_review_report.schema.json",
  "component_id": "AGENTX_HUMAN_REVIEW_APPROVAL",
  "review_document_id": "HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v4.0",
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
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/human_review/human_review_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/human_review/human_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/human_review/human_review_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is the bridge between this template and the implementation. A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, or if it lacks command exit codes.

## 31.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

---

# 32. CLI Command Coverage

This section applies only if CLI commands are exposed.

Required behavior:

```text
[ ] CLI command names are explicit and allowlisted
[ ] CLI does not approve by default
[ ] CLI requires reviewer identity
[ ] CLI requires request_id
[ ] CLI requires explicit decision
[ ] CLI requires approval scope for approvals
[ ] CLI requires expiry or single-use marker for approvals
[ ] CLI writes evidence
[ ] CLI rejects malformed requests
[ ] CLI rejects expired/revoked approval reuse
[ ] CLI blocks self-approval unless explicitly authorized by policy and evidenced
[ ] CLI does not require network/LLM/interactivity for validation tests
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
CLI can approve without reviewer identity
CLI can approve without scope
CLI can approve without expiry/single-use marker
CLI silently mutates source
CLI bypasses schema validation
```

---

# 33. Report Template Coverage

This section applies only if markdown or JSON review reports are generated.

Required behavior:

```text
[ ] report identifies reviewed commit or runtime context
[ ] report lists approval requests
[ ] report lists decisions
[ ] report lists rejected/deferred/clarification items
[ ] report lists expired/revoked approvals
[ ] report lists unresolved approvals
[ ] report lists evidence refs
[ ] report lists hashes where applicable
[ ] report does not expose secrets
[ ] report does not become the approval authority itself
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
report output is treated as approval
report omits evidence refs
report leaks secrets
```

---

# 34. MCP Exposure Coverage

This section applies only if human-review requests are exposed through MCP.

Required behavior:

```text
[ ] MCP can create review request only if policy permits
[ ] MCP cannot self-approve
[ ] MCP cannot revoke approval unless authorized
[ ] MCP cannot bypass reviewer identity requirements
[ ] MCP cannot bypass scope requirements
[ ] MCP cannot approve mutating actions by default
[ ] MCP approval operations are disabled by default unless explicitly enabled
[ ] MCP request/response schemas validate
[ ] MCP exposure writes audit/evidence
[ ] MCP exposure does not open a network port by default unless explicitly part of a later MCP runtime acceptance pass
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
MCP client can self-approve
MCP approval bypasses policy
MCP approval bypasses reviewer identity
MCP approval bypasses scope
MCP approval operations are enabled by default without explicit policy
```

---

# 35. Source Mutation Check

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
only expected runtime artifacts under .agentx-init/human_review/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by tests
approval evidence writes outside approved runtime paths without recorded deviation
approval request/decision handling mutates source
patch or promotion is executed directly by this layer
```

---

# 36. Negative Test Pack

The review must prove that forbidden actions fail closed.

Required negative cases:

```text
[ ] missing request_id -> INVALID
[ ] missing reviewer identity -> INVALID or BLOCKED
[ ] approval without scope -> INVALID
[ ] approval without expiry/single-use rule -> INVALID or BLOCKED
[ ] pending request used as approval -> BLOCKED
[ ] rejected request used as approval -> BLOCKED
[ ] deferred request used as approval -> BLOCKED
[ ] clarification request used as approval -> BLOCKED
[ ] expired approval used -> BLOCKED
[ ] revoked approval used -> BLOCKED
[ ] approval for one action used for another action -> BLOCKED
[ ] approval for one session used for another session -> BLOCKED
[ ] approval for one commit used for another commit -> BLOCKED
[ ] approval for one patch hash used for another patch hash -> BLOCKED
[ ] approval over use-count limit -> BLOCKED
[ ] approval attempts to override sandbox denial -> BLOCKED
[ ] approval attempts to override policy hard block -> BLOCKED
[ ] approval attempts to bypass patch layer -> BLOCKED
[ ] approval attempts to bypass promotion gate -> BLOCKED
[ ] requester self-approval -> BLOCKED unless policy explicitly permits and evidence records it
[ ] MCP client self-approval -> BLOCKED, if MCP applies
[ ] secret-like payload -> redacted in evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked as non-applicable with justification.

---

# 37. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <CLI | MCP | Evidence | Report | Schema | Runtime Artifact Boundary | Patch | Promotion | Other>
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
HIGH items cannot be accepted for DONE unless the review proves they are not part of the active runtime path.
Runtime artifact writes outside `.agentx-init/human_review/` require a deviation entry.
Patch integration deferral requires a deviation entry.
Promotion integration deferral requires a deviation entry.
MCP exposure requires explicit coverage or a NOT APPLICABLE note.
CLI exposure requires explicit coverage or a NOT APPLICABLE note.
Report output requires explicit coverage or a NOT APPLICABLE note.
Missing evidence hashes cannot be accepted as a deviation for DONE.
```

---

# 38. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
approval state model:
approval request coverage:
approval decision coverage:
approval scope coverage:
approval lookup / validation coverage:
stale snapshot / drift coverage:
rejection coverage:
deferral / clarification coverage:
expiry coverage:
revocation coverage:
reviewer identity / self-approval coverage:
identity assurance coverage:
quorum / dual-control coverage:
approval consumption coverage:
queue locking / concurrency coverage:
idempotency coverage:
redaction coverage:
append-only / tamper-evidence coverage:
non-overridable safety coverage:
policy integration:
tool integration:
patch integration:
promotion integration:
audit/evidence:
evidence manifest:
review report:
evidence hashes:
CLI coverage, if applicable:
report coverage, if applicable:
MCP coverage, if applicable:
negative tests:
source mutation check:
completion record:
```

---

# 39. What Failed

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

# 40. Issue Severity Classification

## 40.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
review environment is missing
required command exit code is missing
compileall fails
pytest fails
schema validation fails
approval request lacks stable ID
approval decision lacks scope
approval decision lacks reviewer identity
approval decision lacks expiry or single-use rule
approval state can be silently overwritten
pending request authorizes action
rejected request authorizes action
deferred or clarification request authorizes action
expired approval authorizes action
revoked approval authorizes action
approval for one scope authorizes another scope
approval replay/use-count violation authorizes action
approval lookup defaults to ALLOW on validation error
stale request hash authorizes action
stale policy snapshot authorizes action without revalidation
stale target hash or reviewed commit authorizes action
unauthorized self-approval succeeds
approval overrides sandbox denial
approval overrides policy hard block
approval bypasses schema validation
approval directly applies patch outside Governed Patch Execution
approval directly promotes release outside Promotion / Release Gate
MCP client can self-approve, if MCP applies
CLI can approve without reviewer identity, if CLI applies
approval/rejection/revocation evidence is missing
secrets are logged
evidence hashes are missing
review report is missing
completion record is missing
source mutation occurs directly in this layer
required area remains NOT CHECKED
required command remains NOT RUN
```

## 40.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
incomplete evidence references
partial integration with Policy / Capability Registry
partial integration with Tool / MCP Adapter
partial patch integration coverage
partial promotion integration coverage
review queue exists but lacks deterministic ordering
approval expiry behavior is incomplete but non-active in runtime path
self-approval exception exists but lacks policy evidence
CLI/MCP/report deferral lacks explicit NOT APPLICABLE note
review environment not recorded
runtime artifact boundary exception lacks justification
```

## 40.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled fields reserved for later UI
markdown report intentionally not implemented
MCP exposure intentionally not implemented
CLI commands intentionally not implemented
human approval UI intentionally deferred if data model and API are complete
```

---

# 41. GO / NO-GO Rules

## 41.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
approval state model tests pass
approval request tests pass
approval decision tests pass
approval scope tests pass
approval lookup / validation tests pass
stale snapshot / drift tests pass
rejection tests pass
deferral / clarification tests pass
expiry tests pass
revocation tests pass
reviewer identity / self-approval tests pass
identity assurance tests pass
quorum / dual-control tests pass or are not applicable by policy
approval consumption tests pass
queue locking / concurrency tests pass
idempotency tests pass
redaction tests pass
append-only / tamper-evidence tests pass
non-overridable safety tests pass
policy integration tests pass
tool integration tests pass
patch integration tests pass or patch integration is safely deferred with no active bypass
promotion integration tests pass or promotion integration is safely deferred with no active bypass
audit/evidence tests pass
evidence manifest exists
evidence hashes exist
review report exists
negative tests pass
source mutation check passes
completion record exists
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 41.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
approval request is unstructured
approval decision is unstructured
approval lacks scope
approval lacks reviewer identity
approval lacks expiry/single-use rule
expired approval authorizes action
revoked approval authorizes action
approval scope mismatch authorizes action
approval replay/use-count violation authorizes action
approval lookup defaults to ALLOW on validation error
stale request hash authorizes action
stale policy snapshot authorizes action without revalidation
stale target hash or reviewed commit authorizes action
unauthorized self-approval succeeds
human approval overrides sandbox denial
human approval overrides policy hard block
human approval bypasses patch layer
human approval bypasses promotion gate
approval evidence is missing
rejection/revocation evidence is missing
secrets are logged
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
source mutation occurs directly in this layer
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
fix schema enum values
fix dataclass defaults
fix approval state transitions
fix approval scope checks
fix expiry checks
fix revocation checks
fix use-count/replay checks
fix self-approval checks
fix rejection/deferral handling
fix evidence writing
fix evidence hashing
fix secret redaction
fix policy integration
fix tool integration
fix patch integration guardrails
fix promotion integration guardrails
fix tests to match the contract
```

Forbidden fixes:

```text
do not remove approval scope to pass tests
do not remove expiry checks to pass tests
do not remove revocation checks to pass tests
do not remove reviewer identity checks to pass tests
do not remove self-approval checks to pass tests
do not allow pending/rejected/deferred requests to authorize actions
do not let human approval override sandbox hard denials
do not let human approval override policy hard blocks
do not directly apply patches in this layer
do not directly promote releases in this layer
do not skip evidence writing
do not omit hashes for final DONE
do not log secrets
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
```

---

# 43. Definition of Done

The Human Review / Approval Interface is done when it can safely record, validate, and enforce human review decisions without bypassing Agent_X safety controls.

It must prove:

```text
all target files exist or explicit safe deferral is documented
all required schemas exist
all required tests exist
approval states are enforced
approval requests are schema-valid and evidenced
approval decisions are schema-valid and evidenced
approval scope is immutable and enforced
approval lookup validates state, scope, expiry, revocation, consumption, identity, policy snapshot, target hash, and reviewed commit before authorization
stale request/policy/target drift is blocked or revalidated
approval replay/use-count rules are enforced
rejection decisions are schema-valid and enforced
deferrals and clarification requests do not authorize action
approval expiry is enforced
approval revocation is enforced
reviewer identity is recorded
unauthorized self-approval is blocked
non-overridable safety rules are enforced
Policy / Capability Registry integration works
Tool / MCP Adapter integration works
Governed Patch Execution integration works or is safely guarded
Promotion / Release Gate integration works or is safely guarded
audit/evidence artifacts are written
evidence manifest is written
review report is written
evidence hashes are written
secrets are redacted
source mutation does not occur directly in this layer
completion record exists
final verdict is recorded
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
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

---

# 44. Required Evidence Package

The completion evidence package must include:

```text
compileall output
pytest output
schema validation result
approval state model test result
approval request test result
approval decision test result
approval scope test result
rejection test result
deferral / clarification test result
expiry test result
revocation test result
reviewer identity / self-approval test result
identity assurance test result
quorum / dual-control test result or N/A justification
approval consumption test result
locking/concurrency test result
idempotency test result
non-overridable safety test result
policy integration test result
tool integration test result
patch integration test result or safe-guard note
promotion integration test result or safe-guard note
audit/evidence test result
evidence manifest
review report
negative-test result
git status output
completion record
SHA-256 hashes for final evidence artifacts
```

The evidence package must show:

```text
reviewed commit
validation timestamp
review environment
command exit codes
approval requests evidenced
approval decisions evidenced
approval scope evidenced
rejections/revocations evidenced
expired/revoked/scope-mismatched approvals blocked
replay/use-count violations blocked
unauthorized self-approval blocked
non-overridable safety blocks remain non-overridable
no source mutation
secrets redacted
hashes for final evidence artifacts
```

---

# 45. Completion Evidence Record

After validation, create:

```text
.agentx-init/human_review/human_review_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
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
    "HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_SPEC",
    "HUMAN_REVIEW_APPROVAL_IMPLEMENTATION_REVIEW_AND_DOD_v2"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "approval_state_model_verified": [],
  "approval_request_coverage_verified": [],
  "approval_decision_coverage_verified": [],
  "approval_scope_coverage_verified": [],
  "approval_lookup_validation_verified": [],
  "stale_snapshot_drift_verified": [],
  "approval_consumption_verified": [],
  "queue_locking_concurrency_verified": [],
  "idempotency_verified": [],
  "identity_assurance_verified": [],
  "quorum_dual_control_verified": [],
  "redaction_verified": [],
  "append_only_tamper_evidence_verified": [],
  "rejection_coverage_verified": [],
  "deferral_clarification_coverage_verified": [],
  "expiry_coverage_verified": [],
  "revocation_coverage_verified": [],
  "reviewer_identity_self_approval_verified": [],
  "non_overridable_safety_verified": [],
  "policy_integration_verified": [],
  "tool_integration_verified": [],
  "patch_integration_verified": [],
  "promotion_integration_verified": [],
  "audit_evidence_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/human_review/human_review_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/human_review/human_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 46. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Human review package, schemas, tests, and runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, and completion record. |
| Request / decision / state model | 1.0 | Requests, approvals, rejections, deferrals, clarification, and state transitions are schema-valid and evidenced. |
| Scope / lookup / expiry / revocation | 1.0 | Scope, approval lookup, stale snapshot / drift, expiry, revocation, replay, and use-count checks are enforced. |
| Non-overridable safety | 1.0 | Approval cannot override sandbox, policy hard blocks, schema validation, patch controls, or promotion gates. |
| Integration coverage | 1.0 | Policy, Tool / MCP Adapter, Patch, and Promotion integration are verified or safely deferred. |
| Audit / evidence | 1.0 | JSONL histories, latest artifacts, evidence manifest, review report, hashes, redaction, append-only tamper evidence, completion record. |
| Source-mutation and optional-surface safety | 1.0 | No source mutation; CLI/report/MCP safe or N/A; negative tests pass. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for human approval enforcement
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing review environment caps score at 7.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
approval without scope caps score at 5.0
approval without reviewer identity caps score at 5.0
approval without expiry/single-use marker caps score at 6.0
expired or revoked approval authorizes action caps score at 4.0
approval scope mismatch authorizes action caps score at 4.0
approval lookup defaults to ALLOW on validation error caps score at 4.0
stale request/policy/target drift authorizes action caps score at 4.0
unauthorized self-approval succeeds caps score at 4.0
approval overrides sandbox/policy hard block caps score at 4.0
approval bypasses patch/promotion gate caps score at 4.0
secrets logged caps score at 4.0
source mutation by this layer caps score at 7.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
```

---

# 47. Final Done / Not-Done Verdict

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
approval evidence is missing
approval lookup / validation evidence is missing
stale snapshot / drift evidence is missing
evidence hashes are missing
review report is missing
completion record is missing
```

---

# 48. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/human_review/ exists
[ ] schemas exist
[ ] tests exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Approval State:
[ ] only APPROVED authorizes action
[ ] pending/rejected/deferred/clarification/expired/revoked/cancelled states do not authorize action
[ ] state transitions are append-only and evidenced

Approval Requests:
[ ] requests are schema-valid
[ ] requests include scope proposal
[ ] requests include evidence refs
[ ] requests do not authorize action before decision

Decisions:
[ ] approvals are schema-valid
[ ] approvals include reviewer identity
[ ] approvals include scope
[ ] approvals include expiry/single-use rule
[ ] approvals write evidence
[ ] approvals do not execute actions directly

Scope / Lookup / Replay:
[ ] approval lookup validates state, scope, expiry, revocation, consumption, identity, policy snapshot, target hash, and reviewed commit
[ ] stale request/policy/target drift blocked or revalidated
[ ] action/session/tool/effect scope enforced
[ ] patch/session/file/hash scope enforced if applicable
[ ] commit/release/artifact scope enforced if applicable
[ ] use-count/replay rules enforced

Rejection / Deferral / Clarification:
[ ] rejections do not authorize action
[ ] deferrals do not authorize action
[ ] clarification requests do not authorize action
[ ] all write evidence

Expiry / Revocation:
[ ] expired approvals block
[ ] revoked approvals block
[ ] scope mismatches block

Reviewer Identity / Control:
[ ] reviewer identity required
[ ] reviewer identity assurance recorded
[ ] quorum / dual-control rules enforced where required
[ ] queue locking / concurrency safe
[ ] idempotency enforced
[ ] reviewer role authorized
[ ] unauthorized self-approval blocked
[ ] MCP self-approval blocked if MCP applies

Non-overridable Safety:
[ ] approval cannot override sandbox denial
[ ] approval cannot override policy hard block
[ ] approval cannot bypass schema validation
[ ] approval cannot bypass patch layer
[ ] approval cannot bypass promotion gate

Integration:
[ ] Policy integration verified
[ ] Tool / MCP Adapter integration verified
[ ] Patch integration verified or safely guarded
[ ] Promotion integration verified or safely guarded

Evidence:
[ ] request history written
[ ] approval history written
[ ] rejection history written
[ ] deferral / clarification history written
[ ] expiry / revocation history written
[ ] audit history written
[ ] latest artifacts written atomically
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written
[ ] secrets redacted
[ ] append-only histories protected by hashes

Safety:
[ ] no source mutation directly in this layer
[ ] no raw shell
[ ] no network by default
[ ] no direct patch application
[ ] no direct promotion

Optional Surfaces:
[ ] CLI safe or N/A
[ ] report output safe or N/A
[ ] MCP exposure safe or N/A

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 49. Final Sign-Off Template

Use this after implementation validation.

```text
Human Review / Approval Validation — Commit <hash>

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
- approval state model coverage: PASS/FAIL
- approval request coverage: PASS/FAIL
- approval decision coverage: PASS/FAIL
- approval scope coverage: PASS/FAIL
- approval lookup / validation coverage: PASS/FAIL
- stale snapshot / drift coverage: PASS/FAIL
- rejection coverage: PASS/FAIL
- deferral / clarification coverage: PASS/FAIL
- expiry coverage: PASS/FAIL
- revocation coverage: PASS/FAIL
- reviewer identity / self-approval coverage: PASS/FAIL
- identity assurance coverage: PASS/FAIL
- quorum / dual-control coverage: PASS/FAIL/N/A
- approval consumption coverage: PASS/FAIL
- queue locking / concurrency coverage: PASS/FAIL
- idempotency coverage: PASS/FAIL
- redaction coverage: PASS/FAIL
- append-only / tamper-evidence coverage: PASS/FAIL
- non-overridable safety coverage: PASS/FAIL
- policy integration coverage: PASS/FAIL
- tool integration coverage: PASS/FAIL
- patch integration coverage: PASS/FAIL/DEFERRED SAFELY
- promotion integration coverage: PASS/FAIL/DEFERRED SAFELY
- audit/evidence coverage: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- review report: PRESENT/MISSING
- CLI coverage: PASS/FAIL/N/A
- report coverage: PASS/FAIL/N/A
- MCP coverage: PASS/FAIL/N/A
- negative-test coverage: PASS/FAIL
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

# 50. Final Rating

This v4 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the strong v3 review structure and closes the remaining precision gaps: the existence checklists now match the full expected scope, approval lookup / validation is a first-class review gate, stale request/policy/target drift is explicitly tested, consumption/locking/idempotency/quorum/redaction traceability is complete, tamper-evident append-only history is reviewed separately, and final DONE cannot be claimed without reproducible evidence for freshness, scope, identity, non-overridable safety, and immutable evidence.
```
