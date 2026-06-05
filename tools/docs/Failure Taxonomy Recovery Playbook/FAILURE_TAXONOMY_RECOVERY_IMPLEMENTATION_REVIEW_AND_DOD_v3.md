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
final_verdict: TO_BE_FILLED_AFTER_REVIEW
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
review_target_commit: <commit hash>
review_date_utc: <timestamp>
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
[ ] tools/agentx_evolve/recovery/__init__.py
[ ] tools/agentx_evolve/recovery/failure_models.py
[ ] tools/agentx_evolve/recovery/failure_taxonomy.py
[ ] tools/agentx_evolve/recovery/recovery_playbook.py
[ ] tools/agentx_evolve/recovery/recovery_policy.py
[ ] tools/agentx_evolve/recovery/safe_mode_triggers.py
[ ] tools/agentx_evolve/recovery/failure_evidence.py
[ ] tools/agentx_evolve/recovery/recovery_decider.py
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

## 8.2 Required Schemas

Expected:

```text
[ ] tools/agentx_evolve/schemas/failure_record.schema.json
[ ] tools/agentx_evolve/schemas/recovery_action.schema.json
[ ] tools/agentx_evolve/schemas/recovery_decision.schema.json
[ ] tools/agentx_evolve/schemas/safe_mode_trigger.schema.json
[ ] tools/agentx_evolve/schemas/failure_evidence.schema.json
[ ] tools/agentx_evolve/schemas/recovery_playbook.schema.json
[ ] tools/agentx_evolve/schemas/failure_taxonomy.schema.json
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

## 8.3 Required Tests

Expected:

```text
[ ] tools/agentx_evolve/tests/test_failure_taxonomy.py
[ ] tools/agentx_evolve/tests/test_recovery_policy.py
[ ] tools/agentx_evolve/tests/test_recovery_decider.py
[ ] tools/agentx_evolve/tests/test_safe_mode_triggers.py
[ ] tools/agentx_evolve/tests/test_failure_evidence.py
[ ] tools/agentx_evolve/tests/test_failure_schema.py
[ ] tools/agentx_evolve/tests/test_failure_negative_cases.py
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

## 8.4 Runtime Evidence Location

Expected:

```text
.agentx-init/recovery/
```

Expected artifacts:

```text
[ ] .agentx-init/recovery/failure_records.jsonl
[ ] .agentx-init/recovery/recovery_decisions.jsonl
[ ] .agentx-init/recovery/safe_mode_triggers.jsonl
[ ] .agentx-init/recovery/latest_failure_record.json
[ ] .agentx-init/recovery/latest_recovery_decision.json
[ ] .agentx-init/recovery/latest_safe_mode_trigger.json
[ ] .agentx-init/recovery/recovery_summary.json
[ ] .agentx-init/recovery/failure_recovery_completion_record.json
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
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
TO_BE_FILLED: PASS / FAIL
```

Evidence summary:

```text
TO_BE_FILLED
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
TO_BE_FILLED: PASS / FAIL
```

Evidence summary:

```text
TO_BE_FILLED: exact pass count and runtime
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
TO_BE_FILLED: PASS / FAIL
```

---

# 10. What Failed

Fill in only if failures exist.

| Failure | Evidence | Severity | Required Fix |
|---|---|---|---|
| TO_BE_FILLED | TO_BE_FILLED | LOW / MEDIUM / HIGH / CRITICAL | TO_BE_FILLED |

If no failures:

```text
No failures found.
```

---

# 11. Schema Validation Result

Required schema validations:

```text
[ ] failure_record.schema.json accepts valid failure record
[ ] failure_record.schema.json rejects missing failure_class
[ ] recovery_action.schema.json accepts valid recovery action
[ ] recovery_decision.schema.json accepts valid recovery decision
[ ] safe_mode_trigger.schema.json accepts valid trigger
[ ] failure_evidence.schema.json accepts valid evidence
[ ] recovery_playbook.schema.json accepts valid playbook
[ ] failure_taxonomy.schema.json accepts valid taxonomy
[ ] completion record JSON validates with python -m json.tool
```

Result:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

Evidence summary:

```text
TO_BE_FILLED
```

---

# 12. Failure-Class Coverage Review

## 12.1 Required Core Classes

| Failure class | Covered? | Severity assigned? | Recovery mapped? |
|---|---:|---:|---:|
| MODEL_INVALID_OUTPUT | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| MODEL_INSUFFICIENT_CONTEXT | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| PATCH_APPLY_FAILED | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| VALIDATION_FAILED | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| GOVERNANCE_BLOCKED | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| RISK_TOO_HIGH | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| SOURCE_GUARD_FAILED | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| ROLLBACK_FAILED | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| SCHEMA_VALIDATION_FAILED | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| TOOL_FAILURE | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| LOCK_CONFLICT | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| ATOMIC_WRITE_FAILED | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| PROMPT_CONTRACT_FAILED | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| POLICY_DENIED | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |
| UNKNOWN_FAILURE | TO_BE_FILLED | TO_BE_FILLED | TO_BE_FILLED |

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
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
TO_BE_FILLED: PASS / PARTIAL / FAIL
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
[ ] MODEL_INVALID_OUTPUT maps to REJECT_OUTPUT + RETRY
[ ] MODEL_INSUFFICIENT_CONTEXT maps to REBUILD_CONTEXT
[ ] PATCH_APPLY_FAILED maps to ROLLBACK or BLOCK_SESSION depending on mutation state
[ ] VALIDATION_FAILED maps to REVALIDATE or ROLLBACK depending on mutation state
[ ] GOVERNANCE_BLOCKED maps to BLOCK_SESSION
[ ] RISK_TOO_HIGH maps to REQUEST_HUMAN_REVIEW + BLOCK_SESSION
[ ] SOURCE_GUARD_FAILED maps to ROLLBACK + ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
[ ] ROLLBACK_FAILED maps to ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
[ ] SCHEMA_VALIDATION_FAILED maps to REJECT_OUTPUT or BLOCK_SESSION
[ ] TOOL_FAILURE maps to RETRY or BLOCK_SESSION
[ ] LOCK_CONFLICT maps to BLOCK_SESSION or wait policy
[ ] ATOMIC_WRITE_FAILED maps to BLOCK_SESSION and optionally REQUEST_HUMAN_REVIEW
[ ] PROMPT_CONTRACT_FAILED maps to REJECT_OUTPUT
[ ] POLICY_DENIED maps to BLOCK_SESSION
[ ] PATH_TRAVERSAL maps to ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
[ ] SYMLINK_ESCAPE maps to ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
[ ] L0_WRITE_BLOCKED maps to ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
[ ] SECRET_REDACTION_FAILED maps to BLOCK_SESSION + REQUEST_HUMAN_REVIEW
[ ] UNKNOWN_FAILURE maps to REQUEST_HUMAN_REVIEW + BLOCK_SESSION
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

---

# 14. Safe-Mode Trigger Coverage Review

Safe mode must trigger for:

```text
[ ] ROLLBACK_FAILED
[ ] SOURCE_GUARD_FAILED
[ ] UNEXPECTED_FILE_MUTATION
[ ] POLICY_MISSING
[ ] CAPABILITY_REGISTRY_MISSING
[ ] LOCK_CORRUPTION
[ ] GOVERNANCE_ARTIFACT_MISSING
[ ] UNKNOWN_CRITICAL_FAILURE
[ ] PATH_TRAVERSAL
[ ] SYMLINK_ESCAPE
[ ] L0_WRITE_BLOCKED
```

Safe mode must not trigger for:

```text
[ ] MODEL_INVALID_OUTPUT when low/medium and retryable
[ ] MODEL_INSUFFICIENT_CONTEXT when context can be rebuilt
[ ] ordinary TOOL_FAILURE when retryable and no mutation occurred
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

---

# 15. Evidence / Audit Coverage Review

Evidence requirements:

```text
[ ] failure_records.jsonl is append-only
[ ] recovery_decisions.jsonl is append-only
[ ] safe_mode_triggers.jsonl is append-only
[ ] latest_failure_record.json writes atomically
[ ] latest_recovery_decision.json writes atomically
[ ] latest_safe_mode_trigger.json writes atomically
[ ] evidence links failure_id to recovery_decision_id
[ ] safe-mode trigger links to failure_id
[ ] existing history is not deleted
[ ] secrets are redacted before evidence write
[ ] completion record exists and is valid JSON
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

---

# 16. Artifact Retention / Append-Only Review

The implementation must preserve recovery history.

Check:

```text
[ ] JSONL history is append-only
[ ] previous history lines are not rewritten
[ ] malformed old lines are not deleted silently
[ ] latest JSON files are overwritten only through atomic replace
[ ] completion record is retained or copied to a tracked evidence location
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

---

# 17. Integration Coverage Review

## 17.1 Security Sandbox Integration

Required:

```text
[ ] sandbox failure classes recognized
[ ] PATH_TRAVERSAL treated as critical
[ ] SYMLINK_ESCAPE treated as critical
[ ] L0_WRITE_BLOCKED treated as critical
[ ] SECRET_REDACTION_FAILED blocks logging / requires review
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

## 17.2 Policy / Capability Registry Integration

Required:

```text
[ ] POLICY_DENIED blocks session
[ ] CAPABILITY_MISSING blocks or requires manual repair
[ ] APPROVAL_REQUIRED routes to human review
[ ] recovery layer does not override policy denial
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

## 17.3 Governed Patch Execution Integration

Required:

```text
[ ] PATCH_APPLY_FAILED handled
[ ] SOURCE_GUARD_FAILED requires rollback or safe mode
[ ] VALIDATION_FAILED after mutation requires rollback or repair decision
[ ] ROLLBACK_FAILED requires safe mode
[ ] UNEXPECTED_FILE_MUTATION requires safe mode
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

## 17.4 Initiator Integration

Required:

```text
[ ] governance blocked failures classified
[ ] risk too high failures classified
[ ] validation failures classified
[ ] Initiator artifacts are referenced, not rewritten
[ ] recovery layer does not replace governance or risk decisions
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
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
TO_BE_FILLED: PASS / PARTIAL / FAIL
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
TO_BE_FILLED: PASS / PARTIAL / FAIL
```

---

# 20. Negative Safety Review

The implementation must not:

```text
[ ] call an LLM
[ ] call network
[ ] execute shell
[ ] execute rollback
[ ] apply patches
[ ] mutate source
[ ] silently allow UNKNOWN_FAILURE
[ ] allow CRITICAL failure continuation
[ ] override Policy / Capability Registry denial
[ ] override Initiator governance
```

Status:

```text
TO_BE_FILLED: PASS / PARTIAL / FAIL
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
[ ] tools/agentx_evolve/recovery/ exists
[ ] all required recovery modules exist
[ ] all required schemas exist
[ ] all required tests exist
```

## 23.2 Validation

```text
[ ] compileall passes
[ ] pytest recovery tests pass
[ ] git status shows no unexpected source mutation
```

## 23.3 Taxonomy

```text
[ ] all required failure classes exist
[ ] all required severities exist
[ ] UNKNOWN_FAILURE handled safely
[ ] CRITICAL failures cannot continue silently
```

## 23.4 Recovery Policy

```text
[ ] recovery policy matrix is implemented
[ ] recovery action coverage is complete
[ ] retry limits are respected
[ ] rollback-required conditions are identified
[ ] safe-mode-required conditions are identified
[ ] human-review-required conditions are identified
```

## 23.5 Safe Mode

```text
[ ] ROLLBACK_FAILED triggers safe mode
[ ] SOURCE_GUARD_FAILED triggers safe mode
[ ] UNEXPECTED_FILE_MUTATION triggers safe mode
[ ] L0_WRITE_BLOCKED triggers safe mode
[ ] PATH_TRAVERSAL triggers safe mode
[ ] SYMLINK_ESCAPE triggers safe mode
[ ] UNKNOWN_CRITICAL_FAILURE triggers safe mode
```

## 23.6 Evidence

```text
[ ] failure evidence is append-only
[ ] recovery evidence is append-only
[ ] safe-mode trigger evidence is append-only
[ ] latest artifacts write atomically
[ ] secrets are redacted before evidence write
[ ] completion evidence record exists
[ ] completion evidence record validates as JSON
```

## 23.7 Non-Execution Boundary

```text
[ ] no recovery execution occurs in this layer
[ ] no patch execution occurs in this layer
[ ] no rollback execution occurs in this layer
[ ] no LLM/model call occurs
[ ] no network call occurs
[ ] no shell execution occurs
[ ] no source mutation occurs
```

## 23.8 Final Evidence Availability

```text
[ ] command evidence recorded
[ ] test count recorded
[ ] completion record retained or tracked
[ ] runtime evidence summarized
[ ] unresolved risks listed or empty
[ ] deviations from contract listed or empty
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
final_verdict: DONE / NOT DONE
implementation_rating: <score>/10
review_document_rating: 10/10
reason:
  - TO_BE_FILLED
remaining_blockers:
  - TO_BE_FILLED
required_next_actions:
  - TO_BE_FILLED
```

---

# 26. Final Sign-Off Checklist

Paste this into the final implementation review.

```text
Failure Taxonomy / Recovery Playbook Validation — Commit <hash>

Structure:
[ ] tools/agentx_evolve/recovery/ exists
[ ] required recovery modules exist
[ ] required schemas exist
[ ] required tests exist

Fresh clone:
[ ] fresh checkout used
[ ] commit hash confirmed

Compile:
[ ] PYTHONPATH=tools python -m compileall tools/agentx_evolve/recovery -> PASS

Tests:
[ ] recovery pytest suite -> PASS
[ ] exact test count recorded

Coverage:
[ ] failure-class coverage -> PASS
[ ] recovery-action coverage -> PASS
[ ] safe-mode trigger coverage -> PASS
[ ] schema validation -> PASS
[ ] evidence/audit coverage -> PASS
[ ] artifact-retention review -> PASS
[ ] responsibility-boundary review -> PASS
[ ] integration coverage -> PASS
[ ] dependency/import safety -> PASS
[ ] negative safety review -> PASS

Safety:
[ ] UNKNOWN_FAILURE cannot continue silently
[ ] CRITICAL failure cannot continue silently
[ ] ROLLBACK_FAILED triggers safe mode
[ ] SOURCE_GUARD_FAILED triggers safe mode
[ ] no recovery execution in this layer
[ ] no LLM/network/shell/source mutation

Evidence:
[ ] completion record exists
[ ] completion record JSON validates
[ ] runtime evidence is tracked, force-added, or summarized in tracked evidence

Git status:
[ ] git status --short clean except expected ignored runtime artifacts

Final decision:
[ ] DONE
[ ] NOT DONE

Remaining blockers:
- none / list blockers
```

---

# 27. Final Closeout Statement

Use only after all GO criteria pass:

```text
Failure Taxonomy / Recovery Playbook: DONE
Status: VALIDATED
Commit: <commit hash>
Evidence:
- compileall PASS
- pytest PASS: <count>/<count>
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
