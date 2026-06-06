# LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_REVIEW_AND_DOD
version: v4.0
status: final frozen post-implementation review template and Definition of Done
component_id: AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW
component_name: Long-Term Learning / Outcome Review Layer
roadmap_layer: 16
roadmap_phase: Phase E — Learning, Review, and Outcome Feedback
review_use: use after code is committed
basis_documents:
  - LONG_TERM_LEARNING_OUTCOME_REVIEW_EQC_FIC_SIB_SCHEMA_CONTRACT
  - LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_SPEC
  - LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_REVIEW_AND_DOD_v1
  - LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_REVIEW_AND_DOD_v2
  - LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_REVIEW_AND_DOD_v3
  - LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_REVIEW_AND_DOD_v4
primary_standard: EQC
supporting_standards:
  - FIC
  - SIB
  - Schema Contract
  - Evidence / Audit Rules
  - Policy / Capability Rules
  - Evaluation / Regression Linkage Rules
conditional_standards:
  - Command Acceptance Criteria, if CLI commands are exposed
  - Report Template, if markdown reports are written
  - Memory Contract, if durable learning memory is written
  - Promotion Gate Contract, if learning affects release decisions
optional_standards:
  - ES, only for ecosystem placement
canonical_learning_subdirectory: tools/agentx_evolve/learning/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/learning/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v4 Review and Upgrade Summary

The v3 review / DoD document was strong and close to final, but I would rate it:

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
learning boundary validation
memory candidate validation
regression linkage validation
evidence/audit validation
source mutation check
runtime artifact check
definition of done
final done/not-done verdict
implementation rating
review report
completion record
reviewed commit requirement
environment requirement
exit-code requirement
evidence manifest requirement
review report requirement
completion record requirement
SHA-256 hash requirement
NOT CHECKED / NOT RUN blockers
learning signal confidence
anti-overfitting rules
contradiction / supersession / expiry handling
memory candidate lifecycle controls
replay/idempotency proof
causal attribution validation
flaky/non-deterministic outcome handling
memory retention, revocation, rollback, and quarantine controls
external-memory-provider deferral
no-training-data / no-model-fine-tuning boundary
```

It was not fully 10/10 because a few final review-control details were still under-specified:

```text
1. The header basis document list duplicated v3 and did not name v4 cleanly.
2. The schema checklist did not fully mirror the expanded required schema list from the scope section.
3. The test checklist did not fully mirror the replay, causal attribution, retention/revocation, and flaky-outcome tests used in the scoped command.
4. Command-output SHA-256 fields were required conceptually but not explicitly present in every command-result template and manifest command entry.
5. Input evidence provenance needed a separate validation section so learning cannot be based on untrusted, replaced, or poisoned evidence bundles.
6. Planning-influence boundaries needed a separate validation section so only approved, unexpired, non-revoked, non-quarantined learning can affect future planning.
7. Privacy/data-minimization checks needed stronger explicit review coverage for memory candidates and durable learning artifacts.
8. Reviewer independence and reproducibility needed a clearer sign-off requirement.
9. The GO / NO-GO, blocker, evidence package, and final checklist needed to include provenance, influence-boundary, privacy-minimization, and reviewer-independence checks.
```

This v4 applies those corrections and is the final frozen 10/10 post-implementation review / Definition of Done template for this layer.

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Long-Term Learning / Outcome Review Layer**.

Use this document after code is committed to determine whether the layer is complete, validated, safe, auditable, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether learning boundaries are enforced
whether memory candidates are safe and controlled
whether regression linkage works
whether evidence and audit records are complete
whether source mutation is prevented
whether runtime artifacts stay inside approved paths
whether review report and completion record exist
whether SHA-256 evidence hashes exist
whether learning signals are evidence-based and not overfit
whether contradictory or stale lessons are handled safely
whether durable memory writes are gated by policy and review
whether replay/idempotency produces the same conclusions from the same evidence
whether causal attribution is supported instead of guessed
whether revoked, quarantined, expired, or superseded lessons cannot influence future planning
whether input evidence provenance is verified before learning
whether poisoned or replaced evidence bundles are blocked
whether only approved learning can influence future planning
whether private/sensitive data is minimized or rejected before durable learning
whether the review is reproducible and reviewer-independent
whether the implementation is DONE or NOT DONE
```

This document reviews the implementation. A 10/10 rating for this review document does not mean the implementation is done. The implementation is done only after the validation commands, evidence checks, and safety checks in this document pass.

---

# 2. Why This Layer Needs These Standards

Long-Term Learning / Outcome Review is safety-critical because it decides:

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

The main danger is not ordinary code failure. The main danger is **bad learning**.

This layer must prevent:

```text
learning from incomplete evidence
treating a lucky success as a general rule
treating a failed run as a valid lesson
storing unsafe instructions as memory
storing secrets or private data as memory
promoting unverified model conclusions
reinforcing bad patches
hiding regressions
rewriting history after failure
letting the system approve its own long-term learning without review
```

---

# 3. Standards Applied

## 3.1 Primary Standard

```text
EQC
```

EQC is primary because this layer evaluates outcomes, extracts learning signals, proposes durable lessons, and may influence future planning, review, promotion, regression handling, or memory. It must fail closed when evidence is incomplete, contradictory, stale, low-confidence, unsafe, or unapproved.

## 3.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Policy / Capability Rules
Evaluation / Regression Linkage Rules
```

## 3.3 Conditional Standards

```text
Command Acceptance Criteria, if CLI commands are exposed
Report Template, if it writes markdown reports
Memory Contract, if it writes durable learning memory
Promotion Gate Contract, if learning affects release decisions
```

## 3.4 Optional Standards

```text
ES, only for ecosystem placement
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
[ ] all accepted deviations are listed in the deviation register
[ ] no required area remains NOT CHECKED
[ ] no required command remains NOT RUN
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

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
| DEFERRED SAFELY | Feature is intentionally deferred and cannot execute, mutate, write durable memory, affect promotion, or bypass policy/evidence. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

---

# 6. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or a clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_learning_schemas.py
git status --short
```

Required result:

```text
initial git status: clean or expected known runtime artifacts only
python version: recorded
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation command: PASS, exit_code 0
final git status: clean or expected runtime artifacts only
```

If `validate_learning_schemas.py` is not implemented, the same schema coverage must be proven by a documented pytest file such as:

```text
tools/agentx_evolve/tests/test_learning_schema_validation.py
test_learning_replay_idempotency.py
test_learning_causal_attribution.py
test_memory_retention_revocation.py
test_learning_flaky_outcomes.py
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
external MCP server
external memory provider
```

---

# 7. Expected Implementation Scope

## 7.1 Required Learning Package

Expected location:

```text
tools/agentx_evolve/learning/
```

Expected files:

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
tools/agentx_evolve/learning/learning_lifecycle.py
```

`learning_lifecycle.py` may be omitted only if lifecycle logic is implemented in `memory_candidate_builder.py` and `learning_policy.py`, with tests proving the lifecycle states.

## 7.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
outcome_review.schema.json
learning_signal.schema.json
memory_candidate.schema.json
learning_decision.schema.json
learning_policy.schema.json
regression_link.schema.json
learning_lifecycle.schema.json
outcome_evidence_manifest.schema.json
learning_review_report.schema.json
learning_completion_record.schema.json
learning_replay.schema.json
learning_causal_attribution.schema.json
memory_retention.schema.json
```

## 7.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_outcome_review_models.py
test_outcome_review_schema.py
test_learning_signal_extractor.py
test_memory_candidate_builder.py
test_learning_policy.py
test_learning_lifecycle.py
test_regression_linker.py
test_learning_audit.py
test_learning_reporter.py
test_learning_boundaries.py
test_learning_negative_cases.py
test_learning_schema_validation.py
```

## 7.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/learning/
```

Expected artifacts:

```text
outcome_review_history.jsonl
learning_signal_history.jsonl
memory_candidate_history.jsonl
learning_decision_history.jsonl
regression_link_history.jsonl
learning_violation_history.jsonl
learning_lifecycle_history.jsonl
contradiction_history.jsonl
learning_replay_history.jsonl
causal_attribution_history.jsonl
memory_retention_history.jsonl
memory_revocation_history.jsonl
learning_quarantine_history.jsonl
latest_outcome_review.json
latest_learning_signal.json
latest_memory_candidate.json
long_term_learning_evidence_manifest.json
long_term_learning_review_report.json
long_term_learning_completion_record.json
```

## 7.5 Required Validation Utility Files

Expected validation utility files:

```text
tools/agentx_evolve/tests/validate_learning_schemas.py
```

If this file is not present, the review must identify the exact pytest-based schema validation replacement and prove it covers all required valid and invalid schema cases.

---

# 8. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Learning package location | `tools/agentx_evolve/learning/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Learning schemas | all required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation command | schema command or pytest equivalent exists and passes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Learning tests | required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Outcome review | completed runs can be reviewed from evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Learning signal extraction | signals are evidence-based, bounded, typed, scoped, and confidence-scored | PASS / PARTIAL / FAIL / NOT CHECKED |
| Learning boundary validation | unsafe, unsupported, secret-like, prompt-injection, and self-approving lessons are blocked | PASS / PARTIAL / FAIL / NOT CHECKED |
| Memory candidate validation | durable memory candidates require evidence, policy, scope, risk, lifecycle state, and approval state | PASS / PARTIAL / FAIL / NOT CHECKED |
| Memory lifecycle | CANDIDATE / REVIEWED / APPROVED / REJECTED / APPLIED / EXPIRED / SUPERSEDED states enforced | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Regression linkage | outcomes can link to commits, evaluations, tests, and artifacts | PASS / PARTIAL / FAIL / NOT CHECKED |
| Contradiction handling | conflicting lessons are blocked, superseded, or escalated | PASS / PARTIAL / FAIL / NOT CHECKED |
| Replay / idempotency | same evidence produces same review, signals, decisions, and hashes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Input evidence provenance | reviewed evidence bundle has source, hash, timestamp, producer, and trust status | PASS / PARTIAL / FAIL / NOT CHECKED |
| Causal attribution | blamed cause is tied to commit/run/test/tool evidence, not guessed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Non-determinism handling | flaky/ambiguous outcomes are marked inconclusive, not learned as facts | PASS / PARTIAL / FAIL / NOT CHECKED |
| Retention / revocation | bad, expired, revoked, or quarantined lessons cannot influence planning | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Planning influence boundary | only approved, applied, unexpired, non-revoked learning can influence planning | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Privacy/data minimization | private, sensitive, secret-like, and excessive raw content is rejected or minimized | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy integration | learning decisions check policy before durable use | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evaluation integration | learning uses evaluation/regression evidence, not unsupported claims | PASS / PARTIAL / FAIL / NOT CHECKED |
| Promotion integration | learning cannot promote or release by itself | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Documentation sync integration | learning does not silently alter docs; proposed doc updates are evidenced | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Audit/evidence | JSONL + latest artifacts + manifest + report written safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence hashing | manifest, review report, completion record, and reviewed evidence hashes present | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime artifact boundary | evidence only under approved runtime root or exception listed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | no direct source mutation | PASS / PARTIAL / FAIL / NOT CHECKED |
| Durable memory safety | no durable memory write without accepted policy path | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |

---

# 9. Dependency and Integration Coverage

The layer must be reviewed as an integration boundary.

| Dependency | Required behavior | Status |
|---|---|---|
| Policy / Capability Registry | Durable learning, memory candidates, report emission, and promotion influence require policy checks. | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evaluation Harness / Regression Benchmark | Learning signals require evaluation/test/run evidence. | PASS / PARTIAL / FAIL / NOT CHECKED |
| Promotion / Release Gate | Learning may inform promotion but cannot approve promotion by itself. | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Documentation Synchronization | Learning may suggest docs, but must not silently rewrite docs. | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Monitoring / Observability | Operational outcomes can be referenced only when evidence is recorded. | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Task Queue / Session Scheduler | Review of scheduled runs must include run/session IDs. | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Memory Store / Long-Term Memory | Durable writes require lifecycle state and approval path. | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |

Blocking if:

```text
learning decisions bypass policy
evaluation evidence is optional for outcome claims
learning can approve promotion by itself
learning can silently edit documentation
learning can write durable memory directly without lifecycle and approval
```

---

# 10. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Outcome review created from evidence | `outcome_reviewer.py` | `test_learning_signal_extractor.py` | `outcome_review_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Learning signals are evidence-based | `learning_signal_extractor.py` | `test_learning_signal_extractor.py` | `learning_signal_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Unsafe lessons are blocked | `learning_policy.py` | `test_learning_boundaries.py` | `learning_violation_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Memory candidates are controlled | `memory_candidate_builder.py` | `test_memory_candidate_builder.py` | `memory_candidate_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Memory lifecycle is enforced | `learning_lifecycle.py` or equivalent | `test_learning_lifecycle.py` | `learning_lifecycle_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Regression links are recorded | `regression_linker.py` | `test_regression_linker.py` | `regression_link_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Contradictory lessons are handled | `learning_policy.py` | `test_learning_negative_cases.py` | `contradiction_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Learning decisions are policy checked | `learning_policy.py` | `test_learning_policy.py` | `learning_decision_history.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence is written safely | `learning_audit.py` | `test_learning_audit.py` | evidence manifest | PASS / PARTIAL / FAIL / NOT CHECKED |
| Reports are generated safely | `learning_reporter.py` | `test_learning_reporter.py` | review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation works | schemas | `test_learning_schema_validation.py` | schema validation output | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record exists | completion writer or manual creation | schema validation test | completion record JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 11. What Exists Checklist

## 11.1 Learning Package Files

```text
[ ] tools/agentx_evolve/learning/__init__.py
[ ] tools/agentx_evolve/learning/outcome_models.py
[ ] tools/agentx_evolve/learning/outcome_reviewer.py
[ ] tools/agentx_evolve/learning/learning_signal_extractor.py
[ ] tools/agentx_evolve/learning/memory_candidate_builder.py
[ ] tools/agentx_evolve/learning/learning_policy.py
[ ] tools/agentx_evolve/learning/learning_audit.py
[ ] tools/agentx_evolve/learning/regression_linker.py
[ ] tools/agentx_evolve/learning/learning_reporter.py
[ ] tools/agentx_evolve/learning/learning_lifecycle.py or equivalent lifecycle implementation
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 11.2 Schema Files

```text
[ ] outcome_review.schema.json
[ ] learning_signal.schema.json
[ ] memory_candidate.schema.json
[ ] learning_decision.schema.json
[ ] learning_policy.schema.json
[ ] regression_link.schema.json
[ ] learning_lifecycle.schema.json
[ ] outcome_evidence_manifest.schema.json
[ ] learning_review_report.schema.json
[ ] learning_completion_record.schema.json
[ ] learning_replay.schema.json
[ ] learning_causal_attribution.schema.json
[ ] memory_retention.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 11.3 Test Files

```text
[ ] test_outcome_review_models.py
[ ] test_outcome_review_schema.py
[ ] test_learning_signal_extractor.py
[ ] test_memory_candidate_builder.py
[ ] test_learning_policy.py
[ ] test_learning_lifecycle.py
[ ] test_regression_linker.py
[ ] test_learning_audit.py
[ ] test_learning_reporter.py
[ ] test_learning_boundaries.py
[ ] test_learning_negative_cases.py
[ ] test_learning_schema_validation.py
[ ] test_learning_replay_idempotency.py
[ ] test_learning_causal_attribution.py
[ ] test_memory_retention_revocation.py
[ ] test_learning_flaky_outcomes.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 12. Validation Commands

Run from a fresh checkout of the implementation commit.

Record the exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`. Any non-zero exit code is `FAIL` unless the command is explicitly a negative test where non-zero is the expected result and the expected failure condition is recorded.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_learning_schemas.py
git status --short
```

Required result:

```text
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
git status: CLEAN or only expected runtime artifacts
```

The primary pytest command may run the whole `tools/agentx_evolve/tests` suite. If unrelated future-layer tests exist in that directory, the review must also record a scoped Long-Term Learning pytest command.

The scoped Long-Term Learning pytest command, when required, should be recorded as:

```bash
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_outcome_review_models.py \
  tools/agentx_evolve/tests/test_outcome_review_schema.py \
  tools/agentx_evolve/tests/test_learning_signal_extractor.py \
  tools/agentx_evolve/tests/test_memory_candidate_builder.py \
  tools/agentx_evolve/tests/test_learning_policy.py \
  tools/agentx_evolve/tests/test_learning_lifecycle.py \
  tools/agentx_evolve/tests/test_regression_linker.py \
  tools/agentx_evolve/tests/test_learning_audit.py \
  tools/agentx_evolve/tests/test_learning_reporter.py \
  tools/agentx_evolve/tests/test_learning_boundaries.py \
  tools/agentx_evolve/tests/test_learning_negative_cases.py \
  tools/agentx_evolve/tests/test_learning_schema_validation.py \
  tools/agentx_evolve/tests/test_learning_replay_idempotency.py \
  tools/agentx_evolve/tests/test_learning_causal_attribution.py \
  tools/agentx_evolve/tests/test_memory_retention_revocation.py \
  tools/agentx_evolve/tests/test_learning_flaky_outcomes.py
```

The review must record whether the full suite, the scoped suite, or both were used. If the full suite fails because of unrelated future-layer tests, the scoped suite may establish this layer's status only if the unrelated failures are listed as deviations and no Long-Term Learning required test is skipped.

No validation command may require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
external MCP server
external memory provider
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
output_sha256: <sha256 or NOT STORED>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any Long-Term Learning / Outcome Review Python file fails compile
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
output_sha256: <sha256 or NOT STORED>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required outcome review, learning boundary, memory candidate, lifecycle, regression linkage, schema, evidence, or negative safety test fails
exit code is missing
```

---

# 15. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_learning_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_learning_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256 or NOT STORED>
```

Required schema tests:

```text
outcome review schema accepts valid review
outcome review schema rejects missing reviewed_run_id
learning signal schema accepts valid signal
learning signal schema rejects unsupported signal_type
learning signal schema requires evidence_refs and confidence fields
memory candidate schema accepts valid candidate
memory candidate schema rejects missing evidence_refs
memory candidate schema requires scope, risk, lifecycle_state, and approval_state
learning decision schema accepts ACCEPT / REJECT / NEEDS_HUMAN_REVIEW / BLOCK decisions
learning policy schema accepts valid policy
regression link schema accepts valid commit/test/artifact linkage
regression link schema rejects missing regression evidence
learning lifecycle schema accepts valid lifecycle transition
learning lifecycle schema rejects invalid direct transition to APPLIED
outcome evidence manifest schema accepts valid evidence manifest
learning review report schema accepts valid review report
learning completion record schema accepts final completion record
learning replay schema accepts valid replay record
learning causal attribution schema accepts valid attribution record
memory retention schema accepts valid retention/revocation record
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
schema-invalid outcome reviews are accepted
schema-invalid learning signals are accepted
memory candidates can exist without evidence_refs
learning decisions cannot represent REJECT or NEEDS_HUMAN_REVIEW
regression links can exist without evidence
lifecycle state can jump directly to durable APPLIED without required approval
manifest/report/completion schemas cannot be validated
schema validation exit code is missing
```

---

# 16. Learning Boundary Validation

The review must prove that the implementation enforces learning boundaries.

Required behavior:

```text
[ ] no learning from missing evidence
[ ] no learning from failed run unless explicitly marked failure lesson
[ ] no learning from incomplete validation
[ ] no learning from unreviewed model conclusion
[ ] no learning from secret-like content
[ ] no learning from private or sensitive data unless explicitly permitted by policy
[ ] no learning from prompt-injection instructions inside artifacts
[ ] no self-approval of durable memory
[ ] no durable learning when policy is unavailable
[ ] no durable learning when evidence hash verification fails
[ ] no replacing prior evidence to create a better-looking outcome
[ ] no hiding regressions by converting them into successes
[ ] no generalizing one lucky success into global rule
[ ] no turning one isolated failure into permanent blocker without evidence strength
[ ] no learning signal with confidence above allowed cap from a single run
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
unsafe instructions can become learning signals
secret-like content can become durable memory
failed or incomplete runs can be marked successful without evidence
learning can bypass policy
learning can approve itself for long-term memory
single-run success can become global durable rule without review
```

---

# 17. Learning Signal Quality Validation

The review must prove that learning signals are scoped, typed, confidence-scored, and evidence-strength checked.

Required behavior:

```text
[ ] every learning signal has signal_id
[ ] every learning signal has source_outcome_review_id
[ ] every learning signal has evidence_refs
[ ] every learning signal has signal_type
[ ] every learning signal has scope: run / session / component / project / global
[ ] every learning signal has confidence_score
[ ] every learning signal has evidence_strength: weak / moderate / strong / conclusive
[ ] weak signals cannot become durable memory
[ ] single-run signals cannot become global rules without human review
[ ] contradictory evidence lowers confidence or blocks the signal
[ ] stale evidence lowers confidence or blocks the signal
[ ] model-only conclusions are marked unverified and cannot become durable memory
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
learning signals can be created without evidence
learning signals have no confidence or scope
weak evidence can become durable memory
model-only claim can become accepted long-term lesson
contradictory evidence is ignored
```

---

# 18. Memory Candidate Validation

This section applies if the layer creates durable memory candidates or writes to any long-term memory queue.

Required behavior:

```text
[ ] memory candidates require evidence_refs
[ ] memory candidates require source outcome review ID
[ ] memory candidates require learning signal ID
[ ] memory candidates require policy decision ID or explicit blocked status
[ ] memory candidates classify scope: local project / component / global / prohibited
[ ] memory candidates classify risk: low / medium / high / prohibited
[ ] memory candidates classify lifecycle_state
[ ] memory candidates classify approval_state
[ ] high-risk candidates require human review
[ ] global candidates require human review
[ ] candidates containing secrets are rejected
[ ] candidates containing private data are rejected unless policy permits
[ ] candidates based on one lucky success are rejected or marked low-confidence
[ ] candidates based on regression are marked as cautionary or blocker, not success pattern
[ ] rejected candidates are evidenced
[ ] expired or superseded candidates cannot be applied
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
memory candidates can be created without evidence
unsafe content can become a candidate
candidate approval can bypass policy
candidate can be written directly to durable memory without review when review is required
expired or superseded candidate can be applied
```

---

# 19. Memory Lifecycle Validation

If durable memory is implemented or memory candidates are emitted, the review must prove lifecycle controls.

Allowed lifecycle states:

```text
CANDIDATE
REVIEWED
APPROVED
REJECTED
APPLIED
EXPIRED
SUPERSEDED
BLOCKED
```

Required behavior:

```text
[ ] CANDIDATE is the default state
[ ] CANDIDATE cannot become APPLIED directly
[ ] APPROVED requires policy approval or human review where required
[ ] REJECTED candidates cannot be applied
[ ] EXPIRED candidates cannot be applied
[ ] SUPERSEDED candidates cannot be applied unless revived by explicit review
[ ] APPLIED candidates record applied_at, applied_by, and applied_to_scope
[ ] lifecycle transitions are append-only and evidenced
[ ] lifecycle transitions include reason and decision ID
[ ] lifecycle state is included in latest_memory_candidate.json when applicable
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
candidate can become durable memory without lifecycle transition evidence
rejected/expired/superseded candidate can be applied
APPLIED state lacks approval evidence
lifecycle history can be overwritten silently
```

---

# 20. Regression Linkage Validation

The review must prove that regressions, failures, and outcome changes are linked to concrete evidence.

Required behavior:

```text
[ ] regression links include reviewed commit or run ID
[ ] regression links include failing test/evaluation/artifact refs
[ ] regression links include before/after status where available
[ ] regression links include failure_class where available
[ ] learning signals from regressions are marked cautionary or corrective
[ ] regression-linked lessons cannot be promoted as success patterns
[ ] missing regression evidence blocks regression conclusion
[ ] stale regression evidence is rejected or marked stale
[ ] regression linkage does not rewrite prior history
[ ] regression link includes affected component/layer when known
[ ] regression link includes confidence and evidence strength
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
regressions can be asserted without evidence
regression lessons are stored as success patterns
prior failed results can be overwritten without audit
regression links omit commit/run/test evidence
```

---

# 21. Contradiction, Supersession, and Expiry Validation

Long-term learning must not accumulate stale or contradictory lessons without control.

Required behavior:

```text
[ ] new learning is checked against existing accepted candidates where available
[ ] contradictory lessons are marked CONFLICTING, BLOCKED, or NEEDS_HUMAN_REVIEW
[ ] superseded lessons remain auditable and are not deleted silently
[ ] expired lessons cannot influence planning unless renewed
[ ] higher-evidence lessons may supersede lower-evidence lessons with audit
[ ] global lessons require stronger evidence than project-local lessons
[ ] contradiction records are written to contradiction_history.jsonl
[ ] latest accepted lesson cannot be replaced without a lifecycle record
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
contradictory lessons can both be active without warning
stale lessons continue to influence future planning without expiry/supersession
superseded lessons are deleted without evidence
low-confidence lesson overrides high-confidence lesson without review
```

---

# 22. Replay / Idempotency Validation

The review must prove that outcome review is deterministic for the same validated evidence input.

Required behavior:

```text
[ ] same reviewed commit + same evidence bundle produces same outcome review decision
[ ] same evidence bundle produces same learning signal IDs or stable content hashes
[ ] same evidence bundle does not create duplicate active memory candidates
[ ] repeated review appends replay evidence without rewriting prior history
[ ] replay output records input evidence manifest hash
[ ] replay output records reviewed commit and review configuration hash
[ ] replay drift is detected and marked BLOCKED or NEEDS_REVIEW
[ ] repeated failed/incomplete evidence remains rejected
[ ] repeated contradiction produces stable contradiction status
[ ] idempotency holds without network, model calls, external memory provider, or hidden state
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
same evidence produces different learning decisions without explanation
replay creates duplicate active lessons
replay overwrites prior evidence
replay relies on model/network/external memory provider
review result changes because of hidden state not captured in evidence manifest
```

---

# 23. Causal Attribution and Flaky Outcome Validation

The review must prove that the layer does not invent causes for outcomes.

Required behavior:

```text
[ ] causal attribution links to commit/run/test/tool/artifact evidence
[ ] attribution distinguishes direct cause, contributing cause, suspected cause, and unknown cause
[ ] unknown cause remains UNKNOWN_CAUSE, not guessed
[ ] flaky or non-deterministic tests are marked INCONCLUSIVE or NEEDS_REVIEW
[ ] inconclusive outcomes cannot become durable learning
[ ] regression cause is not assigned to a commit without before/after or failure evidence
[ ] tool failure, policy denial, sandbox denial, model error, and test failure remain distinct
[ ] causal attribution history is append-only
[ ] causal confidence is lower when evidence is partial, stale, or contradictory
[ ] causal claims can be superseded when stronger evidence appears
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
causes can be asserted without evidence
flaky tests can become durable lessons
unknown cause is converted into a confident learning rule
wrong layer/tool/commit can be blamed without traceability
causal history can be rewritten silently
```

---

# 24. Memory Retention, Revocation, Rollback, and Quarantine Validation

This section applies if memory candidates, durable learning memory, or future-planning learning inputs are implemented.

Required behavior:

```text
[ ] memory candidates define retention class: transient / session / project / durable / prohibited
[ ] durable candidates define expiry or review interval
[ ] revoked lessons cannot influence planning
[ ] quarantined lessons cannot influence planning
[ ] bad learning can be marked REVOKED or QUARANTINED with evidence
[ ] memory revocation is append-only and evidenced
[ ] memory rollback records prior applied lesson ID and replacement decision
[ ] retained lessons can be listed with source evidence, approval state, and expiry state
[ ] expired lessons require renewal before use
[ ] external memory provider writes are blocked unless explicitly authorized and tested offline
[ ] no training-data export, model fine-tuning, or embedding-store persistence occurs in this layer unless a separate approved contract exists
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
revoked/quarantined lesson can still influence planning
durable lesson has no retention/expiry/review rule
bad learning cannot be revoked or rolled back
external memory provider is written during validation
training-data export or model fine-tuning occurs in this layer
```

---

# 25. Input Evidence Provenance and Poisoning Validation

The review must prove that the layer learns only from trusted, immutable, and hash-verified evidence bundles.

Required behavior:

```text
[ ] every reviewed evidence bundle records producer component
[ ] every reviewed evidence bundle records reviewed commit or run ID
[ ] every reviewed evidence bundle records created_at timestamp
[ ] every reviewed evidence bundle records SHA-256 hash
[ ] every reviewed evidence bundle records trust status: trusted / untrusted / stale / replaced / poisoned / unknown
[ ] untrusted evidence cannot produce durable learning
[ ] replaced evidence cannot silently replace prior evidence
[ ] poisoned or prompt-injection-like evidence is quarantined
[ ] missing producer component blocks durable learning
[ ] missing evidence hash blocks durable learning
[ ] stale evidence lowers confidence or blocks durable learning
[ ] model-generated summaries are treated as derived evidence, not primary evidence
[ ] primary evidence links remain available in evidence_refs
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
learning can proceed from untrusted evidence
learning can proceed from evidence with missing hashes
poisoned evidence can become a learning signal
replaced evidence can overwrite prior evidence without audit
model summary is treated as primary evidence without source refs
```

---

# 26. Planning Influence Boundary Validation

The review must prove that long-term learning cannot affect future planning unless it has passed the required lifecycle, policy, expiry, and safety gates.

Required behavior:

```text
[ ] only APPROVED or APPLIED learning can be exported to planning context
[ ] CANDIDATE learning cannot influence planning
[ ] REJECTED learning cannot influence planning
[ ] EXPIRED learning cannot influence planning
[ ] SUPERSEDED learning cannot influence planning unless explicitly renewed
[ ] REVOKED learning cannot influence planning
[ ] QUARANTINED learning cannot influence planning
[ ] low-confidence learning cannot influence global planning
[ ] project-local lessons cannot be applied globally without review
[ ] planning export records source memory candidate IDs
[ ] planning export records active lifecycle state
[ ] planning export records expiry state
[ ] planning export records policy decision ID
[ ] planning export is reproducible from approved learning records
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
candidate, rejected, expired, revoked, or quarantined learning can influence planning
project-local learning is applied globally without review
planning export lacks source evidence refs
planning export bypasses policy
```

---

# 27. Privacy and Data-Minimization Validation

The review must prove that durable learning records do not preserve secrets, private data, unnecessary raw content, or oversized evidence copies.

Required behavior:

```text
[ ] memory candidates classify data sensitivity
[ ] secret-like content is rejected and redacted
[ ] private/sensitive content is rejected unless policy explicitly permits it
[ ] raw transcripts, raw prompts, raw tool outputs, and raw file contents are not stored as durable lessons
[ ] durable learning stores minimal lesson text plus evidence refs, not full evidence dumps
[ ] evidence summaries are bounded by max character limits
[ ] redaction occurs before JSONL and latest artifact writes
[ ] redaction failures block durable learning
[ ] data-minimization decision is recorded in learning_decision_history.jsonl
[ ] prohibited data categories cannot be exported to external memory providers
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
secrets are persisted in learning artifacts
private/sensitive data becomes durable learning without explicit policy approval
raw prompts or raw transcripts are stored as lessons
redaction failure still allows durable memory
```

---

# 28. Reviewer Independence and Reproducibility Validation

The review must prove that final DONE is based on reproducible evidence, not the implementation's self-claim.

Required behavior:

```text
[ ] reviewer records exact reviewed commit
[ ] reviewer records exact commands and exit codes
[ ] reviewer records environment
[ ] reviewer records evidence hashes
[ ] reviewer records whether evidence was generated by implementation or independently checked
[ ] implementation self-report is not accepted without command evidence
[ ] final review can be reproduced from evidence manifest and command outputs
[ ] any manual evidence edits are listed as deviations
[ ] reviewer independence status is recorded in review report
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
DONE relies only on implementation-generated self-report
review lacks independent command evidence
review cannot be reproduced from recorded artifacts
manual edits to evidence are not disclosed
```

---

# 29. Evidence / Audit Validation

Required evidence behavior:

```text
[ ] outcome_review_history.jsonl is written
[ ] learning_signal_history.jsonl is written
[ ] memory_candidate_history.jsonl is written when candidates are created
[ ] learning_decision_history.jsonl is written
[ ] regression_link_history.jsonl is written when regressions are linked
[ ] learning_violation_history.jsonl is written for blocked unsafe learning
[ ] learning_lifecycle_history.jsonl is written when lifecycle transitions occur
[ ] contradiction_history.jsonl is written when contradictions are detected
[ ] latest_outcome_review.json is written atomically
[ ] latest_learning_signal.json is written atomically when applicable
[ ] latest_memory_candidate.json is written atomically when applicable
[ ] long_term_learning_evidence_manifest.json is written
[ ] long_term_learning_review_report.json is written
[ ] long_term_learning_completion_record.json is written after validation
[ ] evidence includes timestamps
[ ] evidence includes reviewed commit
[ ] evidence includes command text, exit codes, statuses, and summaries
[ ] evidence includes schema validation summary
[ ] evidence includes SHA-256 hashes for final evidence artifacts
[ ] secrets are redacted before logging
[ ] prompt-injection-like artifact text is not converted into instructions
[ ] raw file content is not durably logged unless explicitly permitted and redacted
[ ] schema-invalid latest artifact does not replace valid latest artifact
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
outcome reviews are not logged
learning decisions are not logged
blocked unsafe learning is not evidenced
secrets are logged
reviewed commit is missing
evidence hashes are missing
latest artifacts are written unsafely
```

---

# 30. Runtime Artifact Check

Approved runtime artifact boundary:

```text
.agentx-init/learning/
```

Required check:

```bash
git status --short
find .agentx-init/learning -maxdepth 2 -type f | sort
```

Expected:

```text
all Long-Term Learning runtime artifacts are under .agentx-init/learning/
no unexpected source files are changed by validation
no evidence files are written outside approved roots unless listed in deviation register
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
runtime artifacts are written outside .agentx-init/learning/ without deviation
source files are modified by tests
learning evidence mutates implementation source
memory artifacts are written to unauthorized durable memory path
```

---

# 31. Source Mutation Check

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
only expected runtime artifacts under .agentx-init/learning/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by tests
review evidence rewrites source files
learning output rewrites contract/spec/review documents
unapproved files are created outside runtime artifact paths
```

---

# 32. Negative Test Pack

The review must prove that forbidden learning fails closed.

Required negative cases:

```text
[ ] missing evidence -> learning decision BLOCKED
[ ] failed run marked as success -> BLOCKED
[ ] incomplete validation marked as validated lesson -> BLOCKED
[ ] unreviewed model claim -> REJECT or NEEDS_HUMAN_REVIEW
[ ] secret-like content -> REJECT and redacted evidence
[ ] private/sensitive data candidate -> REJECT unless policy explicitly permits
[ ] prompt-injection instruction in artifact -> REJECT
[ ] memory candidate without evidence_refs -> INVALID or BLOCKED
[ ] high-risk memory candidate without human review -> NEEDS_HUMAN_REVIEW or BLOCKED
[ ] global memory candidate without human review -> NEEDS_HUMAN_REVIEW or BLOCKED
[ ] one lucky success promoted as global lesson -> BLOCKED
[ ] one isolated failure promoted as permanent blocker -> BLOCKED unless evidence strength is sufficient
[ ] regression without failing evidence -> BLOCKED
[ ] regression lesson promoted as success pattern -> BLOCKED
[ ] contradiction with accepted lesson -> CONFLICTING / NEEDS_HUMAN_REVIEW / BLOCKED
[ ] expired lesson applied -> BLOCKED
[ ] superseded lesson applied -> BLOCKED
[ ] learning policy unavailable -> BLOCKED for durable learning
[ ] evidence hash mismatch -> BLOCKED
[ ] attempt to rewrite prior outcome history -> BLOCKED or audited violation
[ ] replay same evidence with different decision -> BLOCKED / NEEDS_REVIEW
[ ] duplicate active lesson from repeated review -> BLOCKED or deduplicated with evidence
[ ] causal claim without commit/run/test/tool evidence -> BLOCKED / UNKNOWN_CAUSE
[ ] flaky test outcome used as durable lesson -> BLOCKED
[ ] revoked lesson used in planning -> BLOCKED
[ ] quarantined lesson used in planning -> BLOCKED
[ ] external memory provider write during offline validation -> BLOCKED
[ ] training-data export or model fine-tuning attempt -> BLOCKED
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked not applicable with justification.

---

# 33. Evidence Manifest

Create:

```text
.agentx-init/learning/long_term_learning_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "outcome_evidence_manifest.schema.json",
  "component_id": "AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW",
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
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "pytest",
      "command": "PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "schema_validation",
      "command": "<schema validation command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    }
  ],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "learning_boundary_status": "PASS",
  "learning_signal_quality_status": "PASS",
  "memory_candidate_status": "PASS_OR_NOT_APPLICABLE",
  "memory_lifecycle_status": "PASS_OR_NOT_APPLICABLE",
  "regression_linkage_status": "PASS",
  "contradiction_handling_status": "PASS_OR_NOT_APPLICABLE",
  "replay_idempotency_status": "PASS",
  "causal_attribution_status": "PASS",
  "flaky_outcome_status": "PASS",
  "memory_retention_revocation_status": "PASS_OR_NOT_APPLICABLE",
  "input_evidence_provenance_status": "PASS",
  "planning_influence_boundary_status": "PASS_OR_NOT_APPLICABLE",
  "privacy_data_minimization_status": "PASS",
  "reviewer_independence_status": "PASS",
  "external_memory_provider_status": "NOT_APPLICABLE_OR_DEFERRED_SAFELY",
  "training_data_export_status": "BLOCKED_OR_NOT_APPLICABLE",
  "redaction_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

The manifest must include paths and hashes for all final evidence files, including:

```text
long_term_learning_evidence_manifest.json
long_term_learning_review_report.json
long_term_learning_completion_record.json
command output artifacts, if stored as files
JSONL evidence histories used by the review
latest outcome / signal / candidate artifacts used by the review
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

---

# 34. Review Report Artifact

Create:

```text
.agentx-init/learning/long_term_learning_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "learning_review_report.schema.json",
  "component_id": "AGENTX_LONG_TERM_LEARNING_OUTCOME_REVIEW",
  "review_document_id": "LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_REVIEW_AND_DOD",
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
  "evidence_manifest_path": ".agentx-init/learning/long_term_learning_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/learning/long_term_learning_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/learning/long_term_learning_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is the bridge between this template and the implementation. A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, or if it lacks command exit codes.

## 30.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

---

# 35. Completion Record

After validation, create:

```text
.agentx-init/learning/long_term_learning_completion_record.json
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
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "canonical_learning_subdirectory": "tools/agentx_evolve/learning/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/learning/",
  "basis_documents": [
    "LONG_TERM_LEARNING_OUTCOME_REVIEW_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_SPEC",
    "LONG_TERM_LEARNING_OUTCOME_REVIEW_IMPLEMENTATION_REVIEW_AND_DOD_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "outcome_review_cases_verified": [],
  "learning_signal_quality_cases_verified": [],
  "learning_boundary_cases_verified": [],
  "memory_candidate_cases_verified": [],
  "memory_lifecycle_cases_verified": [],
  "regression_linkage_cases_verified": [],
  "contradiction_handling_cases_verified": [],
  "replay_idempotency_cases_verified": [],
  "causal_attribution_cases_verified": [],
  "flaky_outcome_cases_verified": [],
  "memory_retention_revocation_cases_verified": [],
  "input_evidence_provenance_cases_verified": [],
  "planning_influence_boundary_cases_verified": [],
  "privacy_data_minimization_cases_verified": [],
  "reviewer_independence_cases_verified": [],
  "external_memory_provider_cases_verified": [],
  "policy_integration_verified": [],
  "evaluation_integration_verified": [],
  "promotion_gate_integration_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/learning/long_term_learning_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/learning/long_term_learning_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 36. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
learning boundary validation:
learning signal quality validation:
memory candidate validation:
memory lifecycle validation:
regression linkage validation:
contradiction handling validation:
replay/idempotency validation:
causal attribution validation:
flaky outcome validation:
memory retention/revocation validation:
input evidence provenance validation:
planning influence boundary validation:
privacy/data-minimization validation:
reviewer independence validation:
evidence/audit validation:
evidence manifest:
review report:
evidence hashes:
negative tests:
runtime artifact check:
source mutation check:
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

## 34.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
review environment is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
learning boundary validation fails
learning signal quality validation fails
memory candidate validation fails where applicable
memory lifecycle validation fails where applicable
regression linkage validation fails
contradiction handling fails where applicable
replay/idempotency validation fails
causal attribution validation fails
flaky outcome validation fails
memory retention/revocation validation fails where applicable
input evidence provenance validation fails
planning influence boundary validation fails where applicable
privacy/data-minimization validation fails
reviewer independence validation fails
evidence/audit validation fails
source mutation occurs
runtime artifact boundary is violated
learning from incomplete evidence is allowed
unsafe instruction becomes learning signal
secret-like content becomes durable memory
failed run is treated as success without evidence
regression is hidden or rewritten
learning approves itself for durable memory
policy unavailable results in durable learning ALLOW
single lucky run becomes global rule without review
weak evidence becomes durable memory
contradictory lessons remain active without warning
expired or superseded lesson can be applied
replay produces different decisions from same evidence without explanation
causal attribution is guessed without evidence
flaky outcome becomes durable learning
revoked or quarantined lesson can influence planning
external memory provider is written without explicit approval
learning proceeds from untrusted, replaced, poisoned, or hash-missing evidence
candidate/rejected/expired/revoked/quarantined learning influences planning
private/sensitive data is persisted without explicit policy approval
DONE relies only on implementation self-report without independent command evidence
training-data export or model fine-tuning occurs in this layer
evidence hashes are missing
review report is missing
completion record is missing
required area remains NOT CHECKED
required command remains NOT RUN
```

## 34.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
incomplete evidence references
partial memory candidate coverage
partial memory lifecycle coverage
partial regression linkage coverage
partial contradiction handling coverage
partial policy integration
partial evaluation linkage
report generated without full traceability
runtime artifact boundary exception lacks justification
review environment not recorded fully
```

## 34.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra rejected learning-signal types
markdown report generation intentionally deferred
memory write integration intentionally stubbed with safe proof
promotion-gate integration intentionally N/A because learning does not affect promotion
additional future-layer tests exist outside scoped Long-Term Learning suite
```

---

# 39. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Memory | Evidence | Regression | Policy | Evaluation | Report | Runtime Artifact Boundary | Other>
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
HIGH items cannot be accepted for DONE unless the review explicitly proves they are not part of the active runtime path.
Runtime artifact writes outside `.agentx-init/learning/` require a deviation entry.
Durable memory deferral requires a deviation entry if memory candidate APIs exist.
Missing evidence hashes cannot be accepted as a deviation for DONE.
```

---

# 40. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Learning package, schemas, tests, runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including manifest, review report, and completion record. |
| Learning boundary and signal quality | 1.0 | Unsafe, unsupported, secret-like, prompt-injection, low-confidence, and self-approval cases fail closed. |
| Memory candidate and lifecycle safety | 1.0 | Candidates require evidence, policy, scope/risk classification, lifecycle state, and approval state where applicable. |
| Regression, provenance, contradiction, replay, and causality | 1.0 | Regressions link to evidence; input provenance, contradictions, stale lessons, replay drift, flaky outcomes, and causal attribution are handled safely. |
| Evidence / audit | 1.0 | JSONL histories, latest artifacts, manifest, report, hashes, redaction, completion record. |
| Policy / evaluation / promotion / influence integration | 1.0 | Learning decisions use policy and evaluation/regression evidence, cannot approve promotion by themselves, and only approved learning can influence planning. |
| Runtime/source safety | 1.0 | Clean git status, approved runtime artifact boundary, no source mutation, no unauthorized durable memory write. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for long-term learning or outcome review
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing review environment caps score at 7.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
learning boundary FAIL caps score at 4.0
learning signal quality FAIL caps score at 5.0
secret-like content stored as memory caps score at 4.0
self-approved durable learning caps score at 4.0
regression hidden or rewritten caps score at 4.0
contradictory active lessons without warning caps score at 5.0
expired/superseded lesson applied caps score at 5.0
learning from untrusted or hash-missing evidence caps score at 5.0
planning influence boundary FAIL caps score at 5.0
privacy/data-minimization FAIL caps score at 5.0
reviewer independence FAIL caps score at 7.0
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

## 37.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
learning boundary validation passes
learning signal quality validation passes
memory candidate validation passes or is not applicable with justification
memory lifecycle validation passes or is not applicable with justification
regression linkage validation passes
contradiction handling passes or is not applicable with justification
replay/idempotency validation passes
causal attribution validation passes
flaky outcome validation passes
memory retention/revocation validation passes or is not applicable with justification
input evidence provenance validation passes
planning influence boundary validation passes or is not applicable with justification
privacy/data-minimization validation passes
reviewer independence validation passes
evidence/audit validation passes
evidence manifest exists
evidence hashes exist
review report exists
runtime artifact check passes
source mutation check passes
completion record exists
negative tests pass
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 37.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
learning boundary validation fails
learning signal quality validation fails
memory candidate validation fails where applicable
memory lifecycle validation fails where applicable
regression linkage validation fails
contradiction handling fails where applicable
replay/idempotency validation fails
causal attribution validation fails
flaky outcome validation fails
memory retention/revocation validation fails where applicable
input evidence provenance validation fails
planning influence boundary validation fails where applicable
privacy/data-minimization validation fails
reviewer independence validation fails
evidence/audit validation fails
source mutation check fails
runtime artifact check fails
learning from incomplete evidence is allowed
failed run can become success lesson without evidence
unsafe instruction can become learning signal
secret-like content can become durable memory
learning can approve itself for durable memory
policy unavailable results in durable learning ALLOW
regressions can be hidden or rewritten
single lucky success can become global learning without review
weak evidence can become durable memory
contradictory lessons can both remain active without warning
expired or superseded lesson can be applied
replay creates different decisions from the same evidence without explanation
causal cause is guessed without evidence
flaky outcome becomes durable learning
revoked or quarantined lesson can influence planning
external memory provider is written without explicit approval
learning proceeds from untrusted, replaced, poisoned, or hash-missing evidence
candidate/rejected/expired/revoked/quarantined learning influences planning
private/sensitive data is persisted without explicit policy approval
DONE relies only on implementation self-report without independent command evidence
training-data export or model fine-tuning occurs in this layer
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
fix learning signal validation
fix confidence and evidence-strength calculation
fix memory candidate evidence requirements
fix lifecycle transition checks
fix regression linkage fields
fix contradiction detection
fix policy checks
fix evaluation linkage
fix blocked-learning result formatting
fix evidence writing
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix secret redaction
fix tests to reflect the contract
fix input evidence provenance checks
fix planning influence boundary checks
fix privacy/data-minimization checks
fix reviewer-independence recording
fix runtime artifact boundary checks
```

Forbidden fixes:

```text
do not remove policy checks to pass tests
do not allow durable learning without evidence
do not allow memory candidates without evidence_refs
do not bypass human review where required
do not store secret-like content
do not treat failed or incomplete runs as successful lessons
do not promote weak evidence to durable memory
do not hide regressions
do not ignore contradictions
do not revive expired/superseded lessons without review
do not rewrite prior outcome history without audit
do not skip evidence writing
do not omit hashes for final DONE
do not learn from untrusted or hash-missing evidence
do not allow candidate/rejected/expired/revoked/quarantined learning to influence planning
do not persist private/sensitive raw content without explicit policy approval
do not accept implementation self-report as final proof without independent command evidence
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
```

---

# 43. Definition of Done

The Long-Term Learning / Outcome Review Layer is done when it can safely review outcomes, extract bounded learning signals, produce controlled memory candidates, link regressions, handle contradictions, and preserve auditable evidence without unsafe self-reinforcement.

It must prove:

```text
all target files exist or explicit safe deferral is documented
all schemas exist
all tests exist
outcome reviews are created only from evidence
learning signals are evidence-based
learning signals have scope, confidence, and evidence strength
unsafe learning signals are rejected
weak evidence cannot become durable memory
single lucky success cannot become global durable rule without review
memory candidates require evidence and policy controls
memory candidates have lifecycle state and approval state
high-risk memory candidates require review
secret-like content is redacted and rejected from memory
prompt-injection-like instructions are not converted into system learning
regressions link to concrete commits/runs/tests/artifacts
regression lessons cannot be stored as success patterns
contradictory lessons are blocked, escalated, or superseded with evidence
expired or superseded lessons cannot be applied
replay/idempotency proves same evidence gives stable decisions
causal attribution is evidence-linked or marked unknown
input evidence provenance is verified and hash-checked
poisoned, replaced, stale, or untrusted evidence cannot become durable learning
flaky outcomes cannot become durable learning
revoked and quarantined lessons cannot influence future planning
only approved, applied, unexpired, non-revoked, non-quarantined lessons can influence planning
private/sensitive content is minimized, rejected, or explicitly policy-approved
external memory provider writes are blocked unless separately authorized
training-data export and model fine-tuning do not occur in this layer
learning decisions are audited
evidence manifest is written
review report is written
evidence hashes are written
review environment is recorded
no source mutation occurs directly in this layer
runtime artifacts stay under approved root
no unauthorized durable memory write occurs
completion record exists
final verdict is recorded
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_learning_schemas.py
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
learning boundary validation result
learning signal quality validation result
memory candidate validation result or N/A justification
memory lifecycle validation result or N/A justification
regression linkage validation result
contradiction handling validation result or N/A justification
evidence/audit validation result
negative-test result
runtime artifact check result
git status output
evidence manifest
review report
completion record
SHA-256 hashes for final evidence artifacts
```

The evidence package must show:

```text
reviewed commit
validation timestamp
review environment
command exit codes
no source mutation
approved runtime artifact boundary
no unauthorized durable memory write
no unsafe learning from incomplete evidence
no secret-like content stored as memory
no self-approved durable learning
no weak evidence promoted into durable learning
no single lucky success promoted into global rule without review
no active contradictory lessons without escalation
input evidence provenance verified
only approved active learning can influence planning
private/sensitive raw content is not stored as durable learning
review evidence independently reproducible
regressions are not hidden or rewritten
hashes for final evidence artifacts
```

---

# 45. Final Done / Not-Done Verdict

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

# 46. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/learning/ exists
[ ] schemas exist
[ ] tests exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Learning Boundaries:
[ ] incomplete evidence blocks learning
[ ] failed run cannot become success lesson without evidence
[ ] unsafe instruction rejected
[ ] secret-like content rejected/redacted
[ ] prompt-injection-like content rejected
[ ] learning cannot approve itself
[ ] one lucky success cannot become global rule without review

Learning Signal Quality:
[ ] signals require evidence_refs
[ ] signals require scope
[ ] signals require confidence_score
[ ] signals require evidence_strength
[ ] weak signals cannot become durable memory
[ ] model-only conclusions cannot become durable lessons

Memory Candidates:
[ ] candidates require evidence_refs
[ ] candidates require outcome review ID
[ ] candidates require learning signal ID
[ ] candidates require policy decision or blocked state
[ ] candidates require lifecycle state
[ ] candidates require approval state
[ ] high-risk candidates require human review
[ ] rejected/expired/superseded candidates cannot be applied

Regression / Contradiction:
[ ] regressions link to commit/run/test/artifact evidence
[ ] regression lessons are cautionary/corrective, not success patterns
[ ] missing regression evidence blocks conclusion
[ ] prior outcome history is not rewritten silently
[ ] contradictory lessons are blocked, superseded, or escalated
[ ] replay/idempotency checked
[ ] causal attribution evidence-linked
[ ] flaky outcomes blocked from durable learning
[ ] revoked/quarantined lessons blocked from planning
[ ] input evidence provenance verified
[ ] poisoned/replaced/hash-missing evidence blocked
[ ] only approved active learning can influence planning
[ ] private/sensitive data minimized or rejected
[ ] reviewer independence recorded

Evidence:
[ ] outcome review history written
[ ] learning signal history written
[ ] memory candidate history written or N/A
[ ] learning decision history written
[ ] regression link history written
[ ] learning violation history written
[ ] lifecycle history written or N/A
[ ] contradiction history written or N/A
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written
[ ] secrets redacted

Safety:
[ ] no source mutation directly in this layer
[ ] runtime artifacts under .agentx-init/learning/
[ ] no unauthorized durable memory write
[ ] no policy bypass
[ ] no evaluation/regression evidence bypass
[ ] no promotion approval by learning layer alone
[ ] no external memory provider write without authorization
[ ] no training-data export or model fine-tuning

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 47. Final Sign-Off Template

Use this after implementation validation.

```text
Long-Term Learning / Outcome Review Validation — Commit <hash>

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
- learning boundary validation: PASS/FAIL
- learning signal quality validation: PASS/FAIL
- memory candidate validation: PASS/FAIL/N/A
- memory lifecycle validation: PASS/FAIL/N/A
- regression linkage validation: PASS/FAIL
- contradiction handling validation: PASS/FAIL/N/A
- replay/idempotency validation: PASS/FAIL
- causal attribution validation: PASS/FAIL
- flaky outcome validation: PASS/FAIL
- memory retention/revocation validation: PASS/FAIL/N/A
- input evidence provenance validation: PASS/FAIL
- planning influence boundary validation: PASS/FAIL/N/A
- privacy/data-minimization validation: PASS/FAIL
- reviewer independence validation: PASS/FAIL
- evidence/audit validation: PASS/FAIL
- negative-test coverage: PASS/FAIL
- runtime artifact check: PASS/FAIL
- source mutation check: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- review report: PRESENT/MISSING
- completion record: PRESENT/MISSING

Reproducibility:
- exact commands recorded: YES/NO
- exit codes recorded: YES/NO
- output artifacts recorded: YES/NO
- final hashes recorded: YES/NO
- deviations recorded: YES/NO/N/A
- independent command evidence recorded: YES/NO
- implementation self-report cross-checked: YES/NO

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

# 48. Final Freeze Rule

This v4 review / DoD document is frozen as the post-implementation review template for the Long-Term Learning / Outcome Review Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes, additional non-blocking examples
MINOR: additive optional checks that do not change DONE criteria
MAJOR: changed memory lifecycle, changed approval policy, changed evidence requirements, changed durable-learning behavior, changed default safety posture
```

Blocked without major revision:

```text
allowing durable learning without evidence
removing policy checks
removing evaluation/regression evidence requirements
allowing self-approval of memory
allowing revoked/quarantined lessons to influence planning
allowing candidate/rejected/expired learning to influence planning
allowing learning from untrusted or hash-missing evidence
allowing raw private/sensitive content to become durable learning without policy approval
allowing external memory provider writes by default
allowing training-data export or model fine-tuning in this layer
removing SHA-256 evidence hashes
removing replay/idempotency requirements
removing causal attribution requirements
removing source-mutation checks
```

---

# 49. Final Rating

This v4 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the strong v3 coverage and fixes the final precision gaps: clean v4 basis metadata, complete schema/test checklist alignment, explicit command-output SHA-256 fields, input evidence provenance and poisoning validation, planning influence boundary validation, privacy/data-minimization validation, reviewer-independence validation, and updated GO / NO-GO, blocker, evidence-package, checklist, and sign-off requirements. A DONE verdict now requires reviewed commit, environment, exit codes, schema validation, evidence manifest, review report, completion record, SHA-256 hashes, stable replay, evidence-linked causality, trusted evidence provenance, safe planning influence boundaries, privacy-minimized durable learning, independently reproducible review evidence, and no active bad-learning path.
```
