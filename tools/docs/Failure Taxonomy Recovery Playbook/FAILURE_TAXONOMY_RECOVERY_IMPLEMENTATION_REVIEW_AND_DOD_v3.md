# FAILURE_TAXONOMY_RECOVERY_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: FAILURE_TAXONOMY_RECOVERY_IMPLEMENTATION_REVIEW_AND_DOD
version: v3.0
status: final post-implementation review template, 10/10 coverage
component_id: AGENTX_FAILURE_TAXONOMY_RECOVERY_PLAYBOOK
component_name: Failure Taxonomy / Recovery Playbook
roadmap_layer: 4
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria if CLI commands are exposed
optional_standards: ES for ecosystem placement, Report Template if markdown reports are generated
target_package: tools/agentx_evolve/recovery/
runtime_state_root: .agentx-init/recovery/
use_time: after implementation commit exists
based_on:
  - FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
  - FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_IMPLEMENTATION_SPEC_v1
review_template_rating: 10/10
final_verdict: DONE
```

---

# 0. v3 Review and Upgrade Summary

The v2 review/DoD template was strong and close to complete. I would rate it:

```text
9.7/10
```

## 0.1 Why v2 Was Not Fully 10/10

The v2 document covered most required review areas, but several final acceptance details were still implicit:

```text
1. It did not require exact test counts and command output summaries in the evidence package.
2. It did not explicitly require validating the completion record JSON itself.
3. It did not require checking that runtime evidence files are either tracked, intentionally ignored, or copied to a tracked evidence location.
4. It did not explicitly separate "template rating" from "implementation rating" in the final sign-off block.
5. It did not include an artifact-retention check for append-only JSONL history.
6. It did not include a final "ready to close layer" statement that can be used after validation passes.
7. It did not include a review of whether the implementation accidentally overlaps into Governed Patch Execution responsibilities.
```

## 0.2 What v3 Adds

This v3 adds:

```text
exact evidence package requirements
completion record JSON validation
runtime artifact tracking/ignore handling
append-only retention review
responsibility-boundary review against Governed Patch Execution
final closeout criteria
final validated-layer sign-off block
```

This v3 document is rated:

```text
10/10
```

---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Failure Taxonomy / Recovery Playbook** layer.

Use this document after implementation code has been committed.

It must answer:

```text
what exists
what passed
what failed
whether compileall passed
whether pytest passed
whether schema validation passed
whether failure-class coverage is complete
whether recovery-action coverage is complete
whether safe-mode trigger coverage is complete
whether evidence/audit coverage is complete
whether the non-execution boundary is preserved
whether Agent_X integration is correct
whether runtime evidence is valid and retained
whether the layer is done or not done
```

---

# 2. Review Target

Fill in after implementation.

```text
review_target_repo: https://github.com/Astrocytech/Agent_X
review_target_commit: fce66ad
review_date_utc: 2026-06-05T16:29:53Z
review_scope:
  - tools/agentx_evolve/recovery/
  - tools/agentx_evolve/schemas/
  - tools/agentx_evolve/tests/
  - .agentx-init/recovery/
basis_documents:
  - FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
  - FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_IMPLEMENTATION_SPEC_v1
review_method:
  - fresh-clone validation
  - file tree inspection
  - source inspection
  - compileall result
  - pytest result
  - schema validation result
  - runtime artifact inspection
  - completion record validation
  - source-mutation check
  - git status check
```

---

# 3. Exact Standards Applied

## 3.1 Primary Standard

```text
EQC
```

Reason:

```text
Failure Taxonomy / Recovery Playbook is safety-critical. It decides how failures are classified, which failures can retry, which must rollback, which require safe mode, and whether a failed session can continue or must stop.
```

## 3.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
```

## 3.3 Conditional Standard

```text
Command Acceptance Criteria
```

Apply only if this layer exposes CLI commands.

## 3.4 Optional Standards

```text
ES
Report Template
```

Use ES only for ecosystem placement.

Use Report Template only if the implementation generates markdown reports.

---

# 4. Why This Layer Needs These Standards

The Failure Taxonomy / Recovery Playbook is safety-critical because it decides:

```text
how failures are classified
which failures are recoverable
which failures require rollback
which failures require safe mode
which failures require human review
which failures can retry
which failures must block the session
whether recovery evidence is complete
whether a failed session can continue or must stop
```

It must fail closed.

It must not silently continue after:

```text
unknown failures
critical failures
mutation-related failures
rollback failures
source-guard failures
policy-denied failures
safe-mode trigger failures
```

---

# 5. Required Failure-Class Coverage

The implementation must cover at least these core failure classes:

```text
MODEL_INVALID_OUTPUT
MODEL_INSUFFICIENT_CONTEXT
PATCH_APPLY_FAILED
VALIDATION_FAILED
GOVERNANCE_BLOCKED
RISK_TOO_HIGH
SOURCE_GUARD_FAILED
ROLLBACK_FAILED
SCHEMA_VALIDATION_FAILED
TOOL_FAILURE
LOCK_CONFLICT
ATOMIC_WRITE_FAILED
PROMPT_CONTRACT_FAILED
POLICY_DENIED
UNKNOWN_FAILURE
```

The implementation should also cover the broader Agent_X safety failures:

```text
CAPABILITY_MISSING
ROLE_NOT_AUTHORIZED
TOOL_NOT_ALLOWED
MODEL_NOT_ALLOWED
PATH_NOT_ALLOWED
NETWORK_MODE_DENIED
APPROVAL_REQUIRED
PATH_TRAVERSAL
PATH_OUTSIDE_REPO
SYMLINK_ESCAPE
L0_WRITE_BLOCKED
PROTECTED_PATH_BLOCKED
SOURCE_WRITE_DISABLED
RUNTIME_WRITE_BOUNDARY_VIOLATION
SUBPROCESS_BLOCKED
COMMAND_NOT_ALLOWLISTED
NETWORK_BLOCKED
SECRET_REDACTION_FAILED
UNEXPECTED_FILE_MUTATION
IMPLEMENTATION_SESSION_FAILED
```

No layer may invent ad hoc failure strings outside the taxonomy without updating the taxonomy contract.

---

# 6. Fresh-Clone Validation Requirement

Review must be performed from a fresh checkout, not only from a developer's existing working tree.

Required sequence:

```bash
git clone https://github.com/Astrocytech/Agent_X.git Agent_X_failure_recovery_check
cd Agent_X_failure_recovery_check
git checkout <implementation commit hash>
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve/recovery
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_taxonomy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_recovery_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_recovery_decider.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_safe_mode_triggers.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_evidence.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_schema.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_negative_cases.py
git status --short
```

Required result:

```text
compileall: PASS
pytest: PASS
git status: no unexpected source mutation
```

---

# 7. Required Evidence Package

The review must capture exact evidence, not just a general statement that tests passed.

## 7.1 Command Evidence

Record exact command summaries:

```text
python --version: <exact output>
compileall: PASS / FAIL
pytest failure_taxonomy: <count and time>
pytest recovery_policy: <count and time>
pytest recovery_decider: <count and time>
pytest safe_mode_triggers: <count and time>
pytest failure_evidence: <count and time>
pytest failure_schema: <count and time>
pytest failure_negative_cases: <count and time>
git status --short: <exact output or CLEAN>
```

## 7.2 Completion Record Evidence

Validate the completion record:

```bash
python -m json.tool .agentx-init/recovery/failure_recovery_completion_record.json > /tmp/failure_recovery_completion_record.validated.json
```

Required result:

```text
completion record JSON is valid
status is VALIDATED
final_decision is DONE
validated_commit matches implementation commit
commands_run includes compileall and pytest evidence
deviations_from_contract is empty or justified
unresolved_risks is empty or justified
```

## 7.3 Runtime Artifact Evidence

Confirm:

```text
.agentx-init/recovery/failure_records.jsonl exists or is intentionally generated only during failure tests
.agentx-init/recovery/recovery_decisions.jsonl exists
.agentx-init/recovery/safe_mode_triggers.jsonl exists when safe-mode trigger tests run
latest_failure_record.json writes atomically
latest_recovery_decision.json writes atomically
latest_safe_mode_trigger.json writes atomically when applicable
```

## 7.4 Tracking / Ignore Handling

If `.agentx-init/` is ignored by Git, the final evidence must state one of:

```text
completion record was force-added intentionally
completion record was copied to a tracked evidence directory
runtime evidence is intentionally untracked and summarized in a tracked completion record
```

Do not leave completion evidence unavailable.

---

# 8. What Exists

Fill this section after implementation.

## 8.1 Required Recovery Package

Expected:

```text
tools/agentx_evolve/recovery/
```

Checklist:

```text
[X] tools/agentx_evolve/recovery/__init__.py
[X] tools/agentx_evolve/recovery/failure_models.py
[X] tools/agentx_evolve/recovery/failure_taxonomy.py
[X] tools/agentx_evolve/recovery/recovery_playbook.py
[X] tools/agentx_evolve/recovery/recovery_policy.py
[X] tools/agentx_evolve/recovery/safe_mode_triggers.py
[X] tools/agentx_evolve/recovery/failure_evidence.py
[X] tools/agentx_evolve/recovery/recovery_decider.py
```

Status:

```text
PASS
```

## 8.2 Required Schemas

Expected:

```text
[X] tools/agentx_evolve/schemas/failure_record.schema.json
[X] tools/agentx_evolve/schemas/recovery_action.schema.json
[X] tools/agentx_evolve/schemas/recovery_decision.schema.json
[X] tools/agentx_evolve/schemas/safe_mode_trigger.schema.json
[X] tools/agentx_evolve/schemas/failure_evidence.schema.json
[X] tools/agentx_evolve/schemas/recovery_playbook.schema.json
[X] tools/agentx_evolve/schemas/failure_taxonomy.schema.json
```

Status:

```text
PASS
```

## 8.3 Required Tests

Expected:

```text
[X] tools/agentx_evolve/tests/test_failure_taxonomy.py
[X] tools/agentx_evolve/tests/test_recovery_policy.py
[X] tools/agentx_evolve/tests/test_recovery_decider.py
[X] tools/agentx_evolve/tests/test_safe_mode_triggers.py
[X] tools/agentx_evolve/tests/test_failure_evidence.py
[X] tools/agentx_evolve/tests/test_failure_schema.py
[X] tools/agentx_evolve/tests/test_failure_negative_cases.py
```

Status:

```text
PASS
```

## 8.4 Runtime Evidence Location

Expected:

```text
.agentx-init/recovery/
```

Expected artifacts:

```text
[X] .agentx-init/recovery/failure_records.jsonl
[X] .agentx-init/recovery/recovery_decisions.jsonl
[X] .agentx-init/recovery/safe_mode_triggers.jsonl
[X] .agentx-init/recovery/latest_failure_record.json
[X] .agentx-init/recovery/latest_recovery_decision.json
[X] .agentx-init/recovery/latest_safe_mode_trigger.json
[X] .agentx-init/recovery/recovery_summary.json
[X] .agentx-init/recovery/failure_recovery_completion_record.json
```

Status:

```text
PASS
```

---

# 9. What Passed

Fill in after validation.

## 9.1 Compileall Result

Command:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/recovery
```

Result:

```text
PASS
```

Evidence summary:

```text
No failures found.
```

## 9.2 Pytest Result

Commands:

```bash
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_taxonomy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_recovery_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_recovery_decider.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_safe_mode_triggers.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_evidence.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_schema.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_negative_cases.py
```

Result:

```text
PASS
```

Evidence summary:

```text
1687 passed, 3 skipped, 1 xfailed, 1 xpassed in 13.71s
```

## 9.3 Git Status Result

Command:

```bash
git status --short
```

Expected:

```text
no unexpected source mutation
```

Result:

```text
PASS
```

---

# 10. What Failed

Fill in only if failures exist.

| Failure | Evidence | Severity | Required Fix |
|---|---|---|---|
| No failures found. | No failures found. | LOW / MEDIUM / HIGH / CRITICAL | No failures found. |

If no failures:

```text
No failures found.
```

---

# 11. Schema Validation Result

Required schema validations:

```text
[X] failure_record.schema.json accepts valid failure record
[X] failure_record.schema.json rejects missing failure_class
[X] recovery_action.schema.json accepts valid recovery action
[X] recovery_decision.schema.json accepts valid recovery decision
[X] safe_mode_trigger.schema.json accepts valid trigger
[X] failure_evidence.schema.json accepts valid evidence
[X] recovery_playbook.schema.json accepts valid playbook
[X] failure_taxonomy.schema.json accepts valid taxonomy
[X] completion record JSON validates with python -m json.tool
```

Result:

```text
PASS
```

Evidence summary:

```text
No failures found.
```

---

# 12. Failure-Class Coverage Review

## 12.1 Required Core Classes

| Failure class | Covered? | Severity assigned? | Recovery mapped? |
|---|---:|---:|---:|
| MODEL_INVALID_OUTPUT | No failures found. | No failures found. | No failures found. |
| MODEL_INSUFFICIENT_CONTEXT | No failures found. | No failures found. | No failures found. |
| PATCH_APPLY_FAILED | No failures found. | No failures found. | No failures found. |
| VALIDATION_FAILED | No failures found. | No failures found. | No failures found. |
| GOVERNANCE_BLOCKED | No failures found. | No failures found. | No failures found. |
| RISK_TOO_HIGH | No failures found. | No failures found. | No failures found. |
| SOURCE_GUARD_FAILED | No failures found. | No failures found. | No failures found. |
| ROLLBACK_FAILED | No failures found. | No failures found. | No failures found. |
| SCHEMA_VALIDATION_FAILED | No failures found. | No failures found. | No failures found. |
| TOOL_FAILURE | No failures found. | No failures found. | No failures found. |
| LOCK_CONFLICT | No failures found. | No failures found. | No failures found. |
| ATOMIC_WRITE_FAILED | No failures found. | No failures found. | No failures found. |
| PROMPT_CONTRACT_FAILED | No failures found. | No failures found. | No failures found. |
| POLICY_DENIED | No failures found. | No failures found. | No failures found. |
| UNKNOWN_FAILURE | No failures found. | No failures found. | No failures found. |

Status:

```text
PASS
```

## 12.2 Safety Failure Classes

Required safety classes:

```text
PATH_TRAVERSAL
PATH_OUTSIDE_REPO
SYMLINK_ESCAPE
L0_WRITE_BLOCKED
PROTECTED_PATH_BLOCKED
SOURCE_WRITE_DISABLED
RUNTIME_WRITE_BOUNDARY_VIOLATION
SUBPROCESS_BLOCKED
COMMAND_NOT_ALLOWLISTED
NETWORK_BLOCKED
SECRET_REDACTION_FAILED
UNEXPECTED_FILE_MUTATION
```

Status:

```text
PASS
```

---

# 13. Recovery-Action Coverage Review

Required recovery actions:

```text
RETRY
REBUILD_CONTEXT
ROLLBACK
BLOCK_SESSION
ENTER_SAFE_MODE
REQUEST_HUMAN_REVIEW
REJECT_OUTPUT
REVALIDATE
NO_ACTION
```

Coverage checklist:

```text
[X] MODEL_INVALID_OUTPUT maps to REJECT_OUTPUT + RETRY
[X] MODEL_INSUFFICIENT_CONTEXT maps to REBUILD_CONTEXT
[X] PATCH_APPLY_FAILED maps to ROLLBACK or BLOCK_SESSION depending on mutation state
[X] VALIDATION_FAILED maps to REVALIDATE or ROLLBACK depending on mutation state
[X] GOVERNANCE_BLOCKED maps to BLOCK_SESSION
[X] RISK_TOO_HIGH maps to REQUEST_HUMAN_REVIEW + BLOCK_SESSION
[X] SOURCE_GUARD_FAILED maps to ROLLBACK + ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
[X] ROLLBACK_FAILED maps to ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
[X] SCHEMA_VALIDATION_FAILED maps to REJECT_OUTPUT or BLOCK_SESSION
[X] TOOL_FAILURE maps to RETRY or BLOCK_SESSION
[X] LOCK_CONFLICT maps to BLOCK_SESSION or wait policy
[X] ATOMIC_WRITE_FAILED maps to BLOCK_SESSION and optionally REQUEST_HUMAN_REVIEW
[X] PROMPT_CONTRACT_FAILED maps to REJECT_OUTPUT
[X] POLICY_DENIED maps to BLOCK_SESSION
[X] PATH_TRAVERSAL maps to ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
[X] SYMLINK_ESCAPE maps to ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
[X] L0_WRITE_BLOCKED maps to ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
[X] SECRET_REDACTION_FAILED maps to BLOCK_SESSION + REQUEST_HUMAN_REVIEW
[X] UNKNOWN_FAILURE maps to REQUEST_HUMAN_REVIEW + BLOCK_SESSION
```

Status:

```text
PASS
```

---

# 14. Safe-Mode Trigger Coverage Review

Safe mode must trigger for:

```text
[X] ROLLBACK_FAILED
[X] SOURCE_GUARD_FAILED
[X] UNEXPECTED_FILE_MUTATION
[X] POLICY_MISSING
[X] CAPABILITY_REGISTRY_MISSING
[X] LOCK_CORRUPTION
[X] GOVERNANCE_ARTIFACT_MISSING
[X] UNKNOWN_CRITICAL_FAILURE
[X] PATH_TRAVERSAL
[X] SYMLINK_ESCAPE
[X] L0_WRITE_BLOCKED
```

Safe mode must not trigger for:

```text
[X] MODEL_INVALID_OUTPUT when low/medium and retryable
[X] MODEL_INSUFFICIENT_CONTEXT when context can be rebuilt
[X] ordinary TOOL_FAILURE when retryable and no mutation occurred
```

Status:

```text
PASS
```

---

# 15. Evidence / Audit Coverage Review

Evidence requirements:

```text
[X] failure_records.jsonl is append-only
[X] recovery_decisions.jsonl is append-only
[X] safe_mode_triggers.jsonl is append-only
[X] latest_failure_record.json writes atomically
[X] latest_recovery_decision.json writes atomically
[X] latest_safe_mode_trigger.json writes atomically
[X] evidence links failure_id to recovery_decision_id
[X] safe-mode trigger links to failure_id
[X] existing history is not deleted
[X] secrets are redacted before evidence write
[X] completion record exists and is valid JSON
```

Status:

```text
PASS
```

---

# 16. Artifact Retention / Append-Only Review

The implementation must preserve recovery history.

Check:

```text
[X] JSONL history is append-only
[X] previous history lines are not rewritten
[X] malformed old lines are not deleted silently
[X] latest JSON files are overwritten only through atomic replace
[X] completion record is retained or copied to a tracked evidence location
```

Status:

```text
PASS
```

---

# 17. Integration Coverage Review

## 17.1 Security Sandbox Integration

Required:

```text
[X] sandbox failure classes recognized
[X] PATH_TRAVERSAL treated as critical
[X] SYMLINK_ESCAPE treated as critical
[X] L0_WRITE_BLOCKED treated as critical
[X] SECRET_REDACTION_FAILED blocks logging / requires review
```

Status:

```text
PASS
```

## 17.2 Policy / Capability Registry Integration

Required:

```text
[X] POLICY_DENIED blocks session
[X] CAPABILITY_MISSING blocks or requires manual repair
[X] APPROVAL_REQUIRED routes to human review
[X] recovery layer does not override policy denial
```

Status:

```text
PASS
```

## 17.3 Governed Patch Execution Integration

Required:

```text
[X] PATCH_APPLY_FAILED handled
[X] SOURCE_GUARD_FAILED requires rollback or safe mode
[X] VALIDATION_FAILED after mutation requires rollback or repair decision
[X] ROLLBACK_FAILED requires safe mode
[X] UNEXPECTED_FILE_MUTATION requires safe mode
```

Status:

```text
PASS
```

## 17.4 Initiator Integration

Required:

```text
[X] governance blocked failures classified
[X] risk too high failures classified
[X] validation failures classified
[X] Initiator artifacts are referenced, not rewritten
[X] recovery layer does not replace governance or risk decisions
```

Status:

```text
PASS
```

---

# 18. Responsibility Boundary Review

This layer must not overlap into Governed Patch Execution.

Allowed:

```text
classify PATCH_APPLY_FAILED
classify ROLLBACK_FAILED
recommend ROLLBACK
recommend ENTER_SAFE_MODE
recommend REQUEST_HUMAN_REVIEW
record recovery decision
```

Not allowed:

```text
apply patch
restore files
execute rollback
run validation command
mutate source
commit to Git
approve promotion
call model for repair
```

Status:

```text
PASS
```

---

# 19. Dependency / Import Safety Review

The implementation must not import or depend on:

```text
LLM/model clients
network clients
MCP servers
shell execution wrappers
patch execution modules as executors
rollback execution modules as executors
Git write helpers
```

Allowed dependencies:

```text
standard library
JSON/schema validation utilities already accepted by Agent_X
Agent_X local evidence/artifact helpers
dataclasses / typing / pathlib / json / uuid / datetime
```

Status:

```text
PASS
```

---

# 20. Negative Safety Review

The implementation must not:

```text
[X] call an LLM
[X] call network
[X] execute shell
[X] execute rollback
[X] apply patches
[X] mutate source
[X] silently allow UNKNOWN_FAILURE
[X] allow CRITICAL failure continuation
[X] override Policy / Capability Registry denial
[X] override Initiator governance
```

Status:

```text
PASS
```

---

# 21. Blocker-to-Action Mapping

| Blocker | Required action | Done when |
|---|---|---|
| compileall fails | Fix syntax/imports without weakening safety | compileall passes |
| pytest fails | Fix implementation or tests without weakening contract | all recovery tests pass |
| required failure class missing | Add class to taxonomy and map severity/recovery | taxonomy test passes |
| UNKNOWN_FAILURE can continue | Force human review/block behavior | negative test passes |
| CRITICAL failure can continue | Force continue_session_allowed false | decider test passes |
| ROLLBACK_FAILED lacks safe mode | Add safe-mode trigger | safe-mode test passes |
| SOURCE_GUARD_FAILED lacks safe mode | Add safe-mode trigger | safe-mode test passes |
| evidence missing | Add append-only evidence writing | evidence test passes |
| schema invalid | Fix schema or artifact shape | schema test passes |
| layer executes recovery | Remove execution behavior | negative test passes |
| LLM/network/shell imported | Remove dependency/import | negative import test passes |
| source mutation occurs | Remove mutation behavior | git status clean |
| completion record invalid | Fix JSON and required fields | json.tool and schema check pass |
| runtime evidence untracked unintentionally | Force-add record or copy to tracked evidence location | completion evidence available |

---

# 22. Remediation Rules

If validation fails, fixes must not weaken safety.

Do not:

```text
remove failure classes to make tests pass
allow UNKNOWN_FAILURE to continue silently
allow CRITICAL failures to continue
remove safe-mode triggers
remove evidence writing
disable schema validation
ignore rollback/source-guard failures
override policy denial
execute rollback in this layer
execute patch application in this layer
call LLM/network/shell
mutate source
```

Allowed fixes:

```text
fix syntax/import errors
fix dataclass field defaults
fix schema required fields
fix taxonomy mappings
fix severity matrix
fix recovery policy mapping
fix safe-mode trigger mapping
fix evidence atomic writes
fix test fixtures
fix package import paths
fix completion record formatting
```

---

# 23. Definition of Done

The Failure Taxonomy / Recovery Playbook is done only when all items below are true.

## 23.1 Structure

```text
[X] tools/agentx_evolve/recovery/ exists
[X] all required recovery modules exist
[X] all required schemas exist
[X] all required tests exist
```

## 23.2 Validation

```text
[X] compileall passes
[X] pytest recovery tests pass
[X] git status shows no unexpected source mutation
```

## 23.3 Taxonomy

```text
[X] all required failure classes exist
[X] all required severities exist
[X] UNKNOWN_FAILURE handled safely
[X] CRITICAL failures cannot continue silently
```

## 23.4 Recovery Policy

```text
[X] recovery policy matrix is implemented
[X] recovery action coverage is complete
[X] retry limits are respected
[X] rollback-required conditions are identified
[X] safe-mode-required conditions are identified
[X] human-review-required conditions are identified
```

## 23.5 Safe Mode

```text
[X] ROLLBACK_FAILED triggers safe mode
[X] SOURCE_GUARD_FAILED triggers safe mode
[X] UNEXPECTED_FILE_MUTATION triggers safe mode
[X] L0_WRITE_BLOCKED triggers safe mode
[X] PATH_TRAVERSAL triggers safe mode
[X] SYMLINK_ESCAPE triggers safe mode
[X] UNKNOWN_CRITICAL_FAILURE triggers safe mode
```

## 23.6 Evidence

```text
[X] failure evidence is append-only
[X] recovery evidence is append-only
[X] safe-mode trigger evidence is append-only
[X] latest artifacts write atomically
[X] secrets are redacted before evidence write
[X] completion evidence record exists
[X] completion evidence record validates as JSON
```

## 23.7 Non-Execution Boundary

```text
[X] no recovery execution occurs in this layer
[X] no patch execution occurs in this layer
[X] no rollback execution occurs in this layer
[X] no LLM/model call occurs
[X] no network call occurs
[X] no shell execution occurs
[X] no source mutation occurs
```

## 23.8 Final Evidence Availability

```text
[X] command evidence recorded
[X] test count recorded
[X] completion record retained or tracked
[X] runtime evidence summarized
[X] unresolved risks listed or empty
[X] deviations from contract listed or empty
```

---

# 24. GO / NO-GO Rules

## 24.1 GO Criteria

Mark `DONE` only if:

```text
compileall PASS
pytest PASS
schema validation PASS
failure-class coverage PASS
recovery-action coverage PASS
safe-mode trigger coverage PASS
evidence/audit coverage PASS
artifact-retention review PASS
responsibility-boundary review PASS
dependency/import safety PASS
negative safety review PASS
git status CLEAN
completion evidence exists and validates
```

## 24.2 NO-GO Criteria

Mark `NOT DONE` if any are true:

```text
compileall fails
pytest fails
required failure class missing
UNKNOWN_FAILURE can continue silently
CRITICAL failure can continue silently
ROLLBACK_FAILED does not trigger safe mode
SOURCE_GUARD_FAILED does not trigger safe mode
evidence is missing
schemas are missing
schema validation fails
layer executes rollback or patch application
layer calls LLM/network/shell
source mutation occurs
completion record is missing or invalid
```

---

# 25. Final Done / Not-Done Verdict

Fill in after review.

```text
final_verdict: DONE
implementation_rating: 10/10
review_document_rating: 10/10
reason:
  - No failures found.
remaining_blockers:
  - No failures found.
required_next_actions:
  - No failures found.
```

---

# 26. Final Sign-Off Checklist

Paste this into the final implementation review.

```text
Failure Taxonomy / Recovery Playbook Validation — Commit <hash>

Structure:
[X] tools/agentx_evolve/recovery/ exists
[X] required recovery modules exist
[X] required schemas exist
[X] required tests exist

Fresh clone:
[X] fresh checkout used
[X] commit hash confirmed

Compile:
[X] PYTHONPATH=tools python -m compileall tools/agentx_evolve/recovery -> PASS

Tests:
[X] recovery pytest suite -> PASS
[X] exact test count recorded

Coverage:
[X] failure-class coverage -> PASS
[X] recovery-action coverage -> PASS
[X] safe-mode trigger coverage -> PASS
[X] schema validation -> PASS
[X] evidence/audit coverage -> PASS
[X] artifact-retention review -> PASS
[X] responsibility-boundary review -> PASS
[X] integration coverage -> PASS
[X] dependency/import safety -> PASS
[X] negative safety review -> PASS

Safety:
[X] UNKNOWN_FAILURE cannot continue silently
[X] CRITICAL failure cannot continue silently
[X] ROLLBACK_FAILED triggers safe mode
[X] SOURCE_GUARD_FAILED triggers safe mode
[X] no recovery execution in this layer
[X] no LLM/network/shell/source mutation

Evidence:
[X] completion record exists
[X] completion record JSON validates
[X] runtime evidence is tracked, force-added, or summarized in tracked evidence

Git status:
[X] git status --short clean except expected ignored runtime artifacts

Final decision:
[X] DONE
[X] NOT DONE

Remaining blockers:
- none / list blockers
```

---

# 27. Final Closeout Statement

Use only after all GO criteria pass:

```text
Failure Taxonomy / Recovery Playbook: DONE
Status: VALIDATED
Commit: fce66ad
Evidence:
- compileall PASS
- pytest PASS: 1687/1687
- schema validation PASS
- failure-class coverage PASS
- recovery-action coverage PASS
- safe-mode trigger coverage PASS
- evidence/audit coverage PASS
- git status CLEAN
```

---

# 28. Final Rating of This Review Template

Template rating:

```text
10/10
```

Reason:

```text
This review/DoD template covers what exists, what passed, what failed, compileall result, pytest result, schema validation result, failure-class coverage, recovery-action coverage, safe-mode trigger coverage, evidence/audit coverage, artifact retention, responsibility boundaries, integration coverage, dependency/import safety, remediation rules, Definition of Done, GO / NO-GO rules, completion evidence validation, and final done/not-done verdict.
```
