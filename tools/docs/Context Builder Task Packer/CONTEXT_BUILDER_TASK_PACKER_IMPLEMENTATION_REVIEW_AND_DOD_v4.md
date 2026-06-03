# CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_REVIEW_AND_DOD
version: v4.0
status: final frozen post-implementation review template and Definition of Done
component_id: AGENTX_CONTEXT_BUILDER_TASK_PACKER
component_name: Context Builder / Task Packer
roadmap_layer: 8
roadmap_phase: Phase C — Context Preparation / Task Packing
review_use: use after code is committed
basis_documents:
  - CONTEXT_BUILDER_TASK_PACKER_EQC_FIC_SIB_SCHEMA_CONTRACT
  - CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_SPEC
  - CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_REVIEW_AND_DOD_v2
  - CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_REVIEW_AND_DOD_v3
  - CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_REVIEW_AND_DOD_v4
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Prompt Contract Acceptance Criteria, Model Runtime Compatibility Criteria
optional_standards: ES, Report Template
canonical_context_subdirectory: tools/agentx_evolve/context/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/context_packs/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v4 Review and Upgrade Summary

The v4 review / DoD document was strong and close to final. I would rate v3:

```text
9.8/10
```

It already covered the required final-validation areas and added strong production-review controls:

```text
what exists
what passed
what failed
compileall result
pytest result
schema validation result
context-source coverage
task-input coverage
source ranking and recency coverage
budgeting coverage
deduplication coverage
compression coverage
prompt-injection handling coverage
redaction coverage
model compatibility coverage
tool compatibility coverage
prompt contract compatibility
determinism / idempotency
pack hashing
audit/evidence coverage
source mutation check
Definition of Done
final done/not-done verdict
evidence manifest
review report artifact
negative tests
GO / NO-GO rules
```

It was not fully 10/10 because a few last production-control checks were still not explicit enough:

```text
1. Instruction hierarchy needed its own review coverage, separate from general prompt-injection handling.
2. Required task constraints needed a loss-prevention check proving that mandatory constraints were not dropped during ranking, budgeting, deduplication, or compression.
3. Excluded, truncated, compressed, and demoted sources needed explicit omission-reason evidence.
4. Source trust levels needed a clear conflict-resolution rule when source types disagree.
5. Golden fixture / snapshot regression evidence was not required, even though this layer must stay deterministic across future changes.
6. Context-pack canonicalization needed a stricter rule for stable ordering, stable hashing, and volatile-field exclusion.
7. Model-free validation needed a sharper rule: validation must not require live model inference, network summarization, hosted providers, or external embedding services.
8. The final checklist and sign-off needed explicit fields for instruction hierarchy, required-constraint preservation, omission reasons, golden fixtures, and canonical pack hash reproducibility.
```

This v4 applies those corrections and is the final 10/10 post-implementation review / DoD template.

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Context Builder / Task Packer** layer.

Use this document after code is committed to determine whether the layer is complete, validated, safe, auditable, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether context-source coverage is complete
whether task-input coverage is complete
whether required task constraints are preserved
whether instruction hierarchy is enforced
whether source ranking and priority selection work
whether excluded/omitted/truncated source reasons are evidenced
whether recency and staleness handling work
whether budgeting works
whether deduplication works
whether compression works safely
whether prompt-injection handling works
whether sensitive-data redaction works
whether model compatibility is enforced
whether tool compatibility is enforced
whether prompt/task-pack contract compatibility is enforced
whether deterministic/idempotent packing is proven
golden fixture regression is proven
canonical context pack and packed task hashes are recorded
whether golden fixture regression proves stable packing behavior
whether canonical pack hashing excludes volatile fields
whether pack hashes and provenance are complete
whether audit/evidence is written
whether source mutation checks pass
whether evidence hashes and review artifacts are complete
whether the layer is DONE or NOT DONE
```

A 10/10 rating for this document does not mean the implementation is done. The implementation is done only when the recorded validation evidence satisfies the GO criteria in this document.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because this layer decides what information reaches the model, which instructions are trusted, what gets excluded, what is compressed, and which task constraints are preserved.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
```

## 2.3 Conditional Standards

```text
Command Acceptance Criteria, only if this layer exposes CLI commands
Prompt Contract Acceptance Criteria, if this layer emits final prompt/task packs
Model Runtime Compatibility Criteria, because packed context must fit selected model limits
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if it writes markdown reports
```

---

# 3. Why This Layer Needs These Standards

Context Builder / Task Packer is safety-critical because it decides:

```text
which information reaches the model
which files or artifacts are included
which instructions are trusted
which context is ignored
which task constraints are preserved
which source gets priority
which source is considered stale or current
which content is summarized or compressed
which tokens are spent
which model can receive the task
which tool outputs are included
which injected or malicious text is filtered
which sensitive data is redacted
```

A failure in this layer can cause:

```text
loss of explicit task requirements
loss of safety constraints
unsafe prompt-injection promotion
wrong source priority
stale source overriding current source
missing implementation constraints
token-budget overflow
model-context overflow
sensitive-data leakage
wrong tool availability assumptions
unreviewable or unauditable model inputs
non-reproducible task packs
instruction hierarchy inversion
mandatory constraint loss during compression or budgeting
unexplained omission of required context
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
  jsonschema_version: <version or NOT INSTALLED>
```

The review is invalid if the reviewed commit is not recorded.

## 4.1 Review Validity Rules

The review is valid only if all of the following are true:

```text
[ ] reviewed commit is recorded
[ ] validation was run against that exact commit
[ ] initial working-tree state is recorded
[ ] final working-tree state is recorded
[ ] review environment is recorded
[ ] every required command records command text, exit code, status, and summary
[ ] every command marked PASS has exit_code 0
[ ] every expected-failure negative test records the expected failure condition
[ ] review report artifact is created
[ ] evidence manifest exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] required evidence hashes are present
[ ] final context pack hash is present if a pack is emitted
[ ] final packed task hash is present if a packed task is emitted
[ ] reviewer did not rely only on the document's internal rating
```

Document rating and implementation rating are separate:

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
| NOT APPLICABLE | Requirement does not apply to implemented scope and cannot affect runtime behavior. | Yes, if justified |
| DEFERRED SAFELY | Feature is intentionally deferred and cannot create unsafe packs, bypass model limits, bypass tool-policy compatibility, or emit unsafe prompt content. | Yes, only for accepted deferred areas |

A final `DONE` verdict is invalid if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Deferral Rules

```text
NOT APPLICABLE:
  Use only when the implementation scope truly does not include the feature and there is no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot create final packs, bypass model limits, bypass tool-policy compatibility, or emit unsafe prompt content.

PARTIAL:
  Use when some files/tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

---

# 6. Expected Implementation Scope

## 6.1 Expected Package Location

Expected canonical package:

```text
tools/agentx_evolve/context/
```

Expected files:

```text
tools/agentx_evolve/context/__init__.py
tools/agentx_evolve/context/context_models.py
tools/agentx_evolve/context/context_sources.py
tools/agentx_evolve/context/task_input.py
tools/agentx_evolve/context/source_ranking.py
tools/agentx_evolve/context/recency.py
tools/agentx_evolve/context/budgeting.py
tools/agentx_evolve/context/deduplication.py
tools/agentx_evolve/context/compression.py
tools/agentx_evolve/context/injection_filter.py
tools/agentx_evolve/context/redaction.py
tools/agentx_evolve/context/model_compatibility.py
tools/agentx_evolve/context/tool_compatibility.py
tools/agentx_evolve/context/task_packer.py
tools/agentx_evolve/context/instruction_hierarchy.py
tools/agentx_evolve/context/constraint_preservation.py
tools/agentx_evolve/context/pack_canonicalizer.py
tools/agentx_evolve/context/context_evidence.py
```

If `source_ranking.py` or `recency.py` is folded into another module, the review must record the actual implementation file in the traceability matrix.

## 6.2 Expected Schemas

Expected schema location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
context_source.schema.json
context_item.schema.json
task_input.schema.json
source_ranking_record.schema.json
recency_record.schema.json
context_budget.schema.json
context_pack.schema.json
packed_task.schema.json
compression_plan.schema.json
deduplication_record.schema.json
prompt_injection_record.schema.json
redaction_record.schema.json
model_context_compatibility.schema.json
tool_context_compatibility.schema.json
context_pack_audit.schema.json
context_omission_record.schema.json
constraint_preservation_record.schema.json
instruction_hierarchy_record.schema.json
golden_fixture_result.schema.json
context_pack_evidence_manifest.schema.json
context_pack_review_report.schema.json
completion_record.schema.json
```

## 6.3 Expected Tests

Expected test location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_context_models.py
test_context_source_schema.py
test_task_input_schema.py
test_source_ranking.py
test_context_recency.py
test_context_budgeting.py
test_context_deduplication.py
test_context_compression.py
test_prompt_injection_filter.py
test_context_redaction.py
test_model_compatibility.py
test_tool_compatibility.py
test_task_packer.py
test_context_evidence.py
test_context_negative_cases.py
test_context_pack_schema_validation.py
test_context_pack_determinism.py
test_instruction_hierarchy.py
test_constraint_preservation.py
test_context_omission_reasons.py
test_context_pack_golden_fixtures.py
```

## 6.4 Expected Runtime Artifacts

Expected runtime artifact root:

```text
.agentx-init/context_packs/
```

Expected artifacts:

```text
context_source_history.jsonl
context_pack_history.jsonl
context_budget_history.jsonl
context_ranking_history.jsonl
context_recency_history.jsonl
context_injection_history.jsonl
context_redaction_history.jsonl
context_omission_history.jsonl
constraint_preservation_history.jsonl
instruction_hierarchy_history.jsonl
golden_fixture_history.jsonl
latest_context_pack.json
latest_packed_task.json
context_builder_task_packer_evidence_manifest.json
context_builder_task_packer_review_report.json
context_builder_task_packer_completion_record.json
```

## 6.5 Expected Validation Utility

Preferred schema validation utility:

```text
tools/agentx_evolve/tests/validate_context_pack_schemas.py
```

If this file is absent, schema coverage must be proven by:

```text
tools/agentx_evolve/tests/test_context_pack_schema_validation.py
```

---

# 7. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Package location | `tools/agentx_evolve/context/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Models | context, source, task, pack, budget, ranking, recency, compatibility models exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schemas | all required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation | valid and invalid schema cases pass | PASS / PARTIAL / FAIL / NOT CHECKED |
| Context-source coverage | all supported source types handled safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source access integration | context loading uses approved access/tool/policy path | PASS / PARTIAL / FAIL / NOT CHECKED |
| Task-input coverage | task goals, constraints, files, tools, model target captured | PASS / PARTIAL / FAIL / NOT CHECKED |
| Required-constraint preservation | mandatory constraints survive ranking, budgeting, deduplication, and compression | PASS / PARTIAL / FAIL / NOT CHECKED |
| Instruction hierarchy | trusted instructions, task constraints, source data, and tool output are separated by authority | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source ranking coverage | priority, trust, relevance, requiredness, and conflicts handled | PASS / PARTIAL / FAIL / NOT CHECKED |
| Recency coverage | freshness/staleness recorded and used safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Omission / exclusion reasons | omitted, truncated, compressed, demoted, and excluded sources have reason codes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Budgeting coverage | token/context budget enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Deduplication coverage | duplicate and near-duplicate context reduced safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Compression coverage | compression preserves constraints and provenance | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt-injection handling | injected/untrusted instructions filtered or demoted | PASS / PARTIAL / FAIL / NOT CHECKED |
| Redaction coverage | sensitive content redacted before durable evidence/model pack | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model compatibility | pack fits selected model limits and mode | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool compatibility | included tool context matches available tools/policies | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt contract compatibility | final pack separates instructions/data and matches prompt contract | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Determinism / idempotency | same inputs produce stable pack/hash or justified variance | PASS / PARTIAL / FAIL / NOT CHECKED |
| Golden fixture regression | canonical fixtures prove stable packing and constraint preservation | PASS / PARTIAL / FAIL / NOT CHECKED |
| CLI command coverage | CLI commands pass acceptance criteria if exposed | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Audit/evidence | JSONL + latest artifacts + manifests written safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence hashing | final evidence, context pack, packed task SHA-256 hashes present | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime artifact boundary | artifacts only under approved runtime root or deviation listed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | no direct source mutation | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 8. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Context source representation | `context_sources.py` | `test_context_source_schema.py` | context source history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source access integration | `context_sources.py` | `test_context_source_schema.py` | source access evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Task input preservation | `task_input.py` | `test_task_input_schema.py` | packed task artifact | PASS / PARTIAL / FAIL / NOT CHECKED |
| Required-constraint preservation | `constraint_preservation.py` | `test_constraint_preservation.py` | constraint preservation history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Instruction hierarchy enforcement | `instruction_hierarchy.py` | `test_instruction_hierarchy.py` | instruction hierarchy history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source ranking | `source_ranking.py` or equivalent | `test_source_ranking.py` | ranking history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Recency / staleness | `recency.py` or equivalent | `test_context_recency.py` | recency history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Omission reason recording | `task_packer.py` or equivalent | `test_context_omission_reasons.py` | omission history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Budget enforcement | `budgeting.py` | `test_context_budgeting.py` | budget history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Deduplication | `deduplication.py` | `test_context_deduplication.py` | deduplication record / pack history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Compression safety | `compression.py` | `test_context_compression.py` | compression plan / pack history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Injection handling | `injection_filter.py` | `test_prompt_injection_filter.py` | injection history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Redaction | `redaction.py` | `test_context_redaction.py` | redaction history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model compatibility | `model_compatibility.py` | `test_model_compatibility.py` | compatibility record | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool compatibility | `tool_compatibility.py` | `test_tool_compatibility.py` | compatibility record | PASS / PARTIAL / FAIL / NOT CHECKED |
| Golden fixture regression | `task_packer.py` + fixtures | `test_context_pack_golden_fixtures.py` | golden fixture history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Pack building | `task_packer.py` | `test_task_packer.py` | latest packed task | PASS / PARTIAL / FAIL / NOT CHECKED |
| Determinism / idempotency | `task_packer.py` | `test_context_pack_determinism.py` | pack hashes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence writing | `context_evidence.py` | `test_context_evidence.py` | evidence manifest | PASS / PARTIAL / FAIL / NOT CHECKED |
| Negative safety cases | multiple files | `test_context_negative_cases.py` | review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Review report | report writer or manual creation | schema/manual validation | review report JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record | completion writer | schema validation test | completion record JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 9. What Exists Checklist

## 9.1 Package Files

```text
[ ] tools/agentx_evolve/context/__init__.py
[ ] tools/agentx_evolve/context/context_models.py
[ ] tools/agentx_evolve/context/context_sources.py
[ ] tools/agentx_evolve/context/task_input.py
[ ] tools/agentx_evolve/context/source_ranking.py or equivalent module recorded in traceability matrix
[ ] tools/agentx_evolve/context/recency.py or equivalent module recorded in traceability matrix
[ ] tools/agentx_evolve/context/budgeting.py
[ ] tools/agentx_evolve/context/deduplication.py
[ ] tools/agentx_evolve/context/compression.py
[ ] tools/agentx_evolve/context/injection_filter.py
[ ] tools/agentx_evolve/context/redaction.py
[ ] tools/agentx_evolve/context/model_compatibility.py
[ ] tools/agentx_evolve/context/tool_compatibility.py
[ ] tools/agentx_evolve/context/task_packer.py
[ ] tools/agentx_evolve/context/context_evidence.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 9.2 Schema Files

```text
[ ] context_source.schema.json
[ ] context_item.schema.json
[ ] task_input.schema.json
[ ] source_ranking_record.schema.json
[ ] recency_record.schema.json
[ ] context_budget.schema.json
[ ] context_pack.schema.json
[ ] packed_task.schema.json
[ ] compression_plan.schema.json
[ ] deduplication_record.schema.json
[ ] prompt_injection_record.schema.json
[ ] redaction_record.schema.json
[ ] model_context_compatibility.schema.json
[ ] tool_context_compatibility.schema.json
[ ] context_pack_audit.schema.json
[ ] context_pack_evidence_manifest.schema.json
[ ] context_pack_review_report.schema.json
[ ] completion_record.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 9.3 Test Files

```text
[ ] test_context_models.py
[ ] test_context_source_schema.py
[ ] test_task_input_schema.py
[ ] test_source_ranking.py
[ ] test_context_recency.py
[ ] test_context_budgeting.py
[ ] test_context_deduplication.py
[ ] test_context_compression.py
[ ] test_prompt_injection_filter.py
[ ] test_context_redaction.py
[ ] test_model_compatibility.py
[ ] test_tool_compatibility.py
[ ] test_task_packer.py
[ ] test_context_evidence.py
[ ] test_context_negative_cases.py
[ ] test_context_pack_schema_validation.py
[ ] test_context_pack_determinism.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 10. Validation Commands

Run from a fresh checkout or clean working tree.

Record exact command text, exit code, status, output artifact, and summary for every command. `PASS` requires exit code `0`. Any non-zero exit code is `FAIL` unless the command is explicitly a negative test where non-zero is expected and the expected failure condition is recorded.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_context_models.py \
  tools/agentx_evolve/tests/test_context_source_schema.py \
  tools/agentx_evolve/tests/test_task_input_schema.py \
  tools/agentx_evolve/tests/test_source_ranking.py \
  tools/agentx_evolve/tests/test_context_recency.py \
  tools/agentx_evolve/tests/test_context_budgeting.py \
  tools/agentx_evolve/tests/test_context_deduplication.py \
  tools/agentx_evolve/tests/test_context_compression.py \
  tools/agentx_evolve/tests/test_prompt_injection_filter.py \
  tools/agentx_evolve/tests/test_context_redaction.py \
  tools/agentx_evolve/tests/test_model_compatibility.py \
  tools/agentx_evolve/tests/test_tool_compatibility.py \
  tools/agentx_evolve/tests/test_task_packer.py \
  tools/agentx_evolve/tests/test_context_evidence.py \
  tools/agentx_evolve/tests/test_context_negative_cases.py \
  tools/agentx_evolve/tests/test_context_pack_schema_validation.py \
  tools/agentx_evolve/tests/test_context_pack_determinism.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_context_pack_schemas.py
git status --short
```

If `validate_context_pack_schemas.py` is not implemented, record the fallback command:

```bash
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_context_pack_schema_validation.py
```

Required result:

```text
initial git status: clean or expected runtime artifacts only
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
context-specific pytest: PASS, exit_code 0
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
external MCP server
actual model inference
```

---

# 11. Compileall Result

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
any Context Builder / Task Packer Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 12. Pytest Result

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
any required context-source, task-input, ranking, recency, budgeting, deduplication, compression, injection, redaction, model compatibility, tool compatibility, determinism, schema, evidence, or negative test fails
exit code is missing
```

---

# 13. Schema Validation Result

Record schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_context_pack_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_context_pack_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256 if output artifact is stored>
```

Required schema tests:

```text
context source schema accepts valid source
context source schema rejects missing source_id
context item schema accepts valid item
context item schema rejects unknown trust level
task input schema accepts valid task input
task input schema rejects missing task goal
task input schema rejects missing explicit constraints when declared required
source ranking record schema accepts valid ranking decision
recency record schema accepts valid freshness/staleness decision
context budget schema accepts valid budget
context budget schema rejects over-limit pack
context pack schema accepts valid pack
context pack schema requires provenance for included context
context pack schema requires pack_hash if final pack emitted
packed task schema accepts valid packed task
packed task schema separates instructions from source content
packed task schema requires packed_task_hash if final packed task emitted
compression plan schema accepts valid compression plan
deduplication record schema accepts valid deduplication record
prompt injection record schema accepts valid injection finding
redaction record schema accepts valid redaction record
model compatibility schema accepts valid compatibility result
tool compatibility schema accepts valid compatibility result
audit schema accepts valid context-pack audit event
evidence manifest schema accepts valid evidence manifest
review report schema accepts valid review report
completion record schema accepts final completion record
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
schema-invalid context items are accepted
task inputs can omit required task constraints
packed task schema cannot represent source provenance
packed task schema cannot separate trusted instructions from untrusted source content
context budget schema cannot represent token/context-window limits
ranking/recency records cannot be schema-validated
injection/redaction records cannot be schema-validated
evidence manifest cannot be schema-validated
review report cannot be schema-validated
completion record cannot be schema-validated
schema validation exit code is missing
```

---

# 14. Context-Source Coverage

Required context-source behavior:

```text
[ ] source files can be represented without raw uncontrolled reads
[ ] tool outputs can be represented with provenance
[ ] prior artifacts can be represented with provenance
[ ] user task input can be represented separately from retrieved context
[ ] trusted system/project instructions are separated from untrusted content
[ ] source trust level is recorded
[ ] source freshness or timestamp is recorded where available
[ ] source path or artifact ref is recorded where applicable
[ ] context item source type is recorded
[ ] source inclusion reason is recorded
[ ] source exclusion reason is recorded when excluded
[ ] source access evidence is attached when source came through a tool/sandbox/policy path
[ ] untrusted context cannot become trusted instruction
[ ] instruction hierarchy evidence written
[ ] tool output remains data unless policy promotes it
[ ] unavailable source returns schema-valid failure or exclusion record
[ ] approved access path/tool evidence is attached where applicable
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
untrusted context is promoted to trusted instruction
source provenance is missing
missing/unavailable sources crash packing
context sources are loaded by bypassing approved file/tool access rules
source trust level is missing
source inclusion/exclusion cannot be audited
```

---

# 15. Task-Input Coverage

Required task-input behavior:

```text
[ ] task goal is captured
[ ] explicit user constraints are captured
[ ] required files/artifacts are captured
[ ] allowed tools are captured or referenced
[ ] disallowed tools/actions are captured
[ ] model target or model profile is captured where available
[ ] output format requirements are captured
[ ] safety constraints are preserved
[ ] task priority is recorded
[ ] task input validates against schema
[ ] unresolved ambiguity is recorded instead of guessed silently
[ ] constraints are marked as must-preserve where applicable
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
explicit user constraints are dropped
safety constraints are dropped
output format requirements are dropped
missing task goal still produces runnable packed task
unresolved ambiguity is silently converted into a false requirement
```

---

# 16. Source Ranking / Priority Coverage

Required source-ranking behavior:

```text
[ ] required task inputs outrank optional retrieved context
[ ] explicit user constraints outrank inferred context
[ ] trusted project/system instructions outrank untrusted file/tool content
[ ] source trust level is used in ranking
[ ] source relevance is used in ranking
[ ] source requiredness is used in ranking
[ ] conflict handling is deterministic
[ ] lower-trust source cannot override higher-trust source without evidence
[ ] excluded low-priority sources are recorded with exclusion reason
[ ] ranking decisions are evidenced
[ ] ranking record validates against schema
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
explicit user constraints lose priority to retrieved context
untrusted source outranks trusted instruction without evidence
ranking is non-deterministic without explanation
excluded required source lacks evidence
ranking cannot be audited
```

---

# 17. Recency / Staleness Coverage

Required recency behavior:

```text
[ ] source timestamp is recorded where available
[ ] artifact modified time or version is recorded where available
[ ] stale source is marked as stale when detectable
[ ] recency does not override trust by itself
[ ] newer low-trust source cannot silently replace older high-trust source
[ ] stale-but-required source remains included or is flagged for review
[ ] conflicting dates are recorded as conflicts
[ ] recency decision validates against schema
[ ] recency decisions are evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
stale source silently overrides current source
recency overrides trust without evidence
source date conflict is ignored
recency cannot be audited
```

---

# 18. Budgeting Coverage

Required budgeting behavior:

```text
[ ] context-window limit is represented
[ ] token budget is represented
[ ] reserved budget for system/project instructions is represented
[ ] reserved budget for task instructions is represented
[ ] reserved budget for answer/output is represented
[ ] per-source budget can be calculated or enforced
[ ] over-budget pack is rejected or compressed safely
[ ] selected model-specific limits are respected
[ ] local model runtime limits are respected when applicable
[ ] budgeting result is recorded in evidence
[ ] budget estimate method is recorded
[ ] budget overflow returns BLOCKED or NEEDS_REPACK, not silent truncation
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
packed task can exceed selected model context limit
required constraints are dropped to fit budget without evidence
over-budget context is silently truncated without provenance
budgeting cannot be audited
output budget is not reserved
```

---

# 19. Deduplication Coverage

Required deduplication behavior:

```text
[ ] exact duplicate context items are detected
[ ] near-duplicate context items are handled deterministically
[ ] higher-trust source wins when duplicates conflict
[ ] newer source wins only when trust levels allow it
[ ] deduplication preserves provenance of removed/merged items
[ ] deduplication does not remove unique constraints
[ ] conflicting duplicates are not merged silently
[ ] deduplication record is written or included in pack evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
unique task constraints are removed as duplicates
lower-trust source overrides higher-trust source without evidence
conflicting duplicates are merged silently
deduplication has no evidence record
```

---

# 20. Compression Coverage

Required compression behavior:

```text
[ ] compression is deterministic or auditable
[ ] compression preserves explicit task constraints
[ ] compression preserves safety constraints
[ ] compression preserves output format requirements
[ ] compression preserves source provenance
[ ] compression marks compressed items as compressed
[ ] compression records original source refs
[ ] compression does not convert untrusted text into trusted instruction
[ ] compression can be bypassed for must-include exact content
[ ] compression plan validates against schema
[ ] compression loss is recorded
[ ] compression failure returns NEEDS_REPACK or BLOCKED
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
compression drops explicit user constraints
compression drops safety constraints
compression drops output format requirements
compression removes source provenance
compression creates new unsupported claims
compression treats untrusted content as instruction
```

---

# 21. Prompt-Injection Handling Coverage

Required prompt-injection behavior:

```text
[ ] untrusted instructions inside files/tool outputs are detected or demoted
[ ] suspicious phrases are recorded in injection findings
[ ] injected instructions cannot override system/project/user task constraints
[ ] source trust level affects instruction handling
[ ] tool-output instructions are treated as data unless explicitly trusted
[ ] injection findings are included in evidence
[ ] packed task separates instructions from source content
[ ] injected requests to ignore policy/sandbox/tool/model limits are blocked or demoted
[ ] injected requests to alter output format are blocked unless trusted
[ ] injected requests to reveal secrets are blocked or redacted
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
untrusted source text can override task instructions
file content can instruct the packer to ignore safety rules
tool output can expand allowed tools without policy
injection findings are not evidenced
packed task does not separate trusted instructions from untrusted content
```

---

# 22. Redaction Coverage

Required redaction behavior:

```text
[ ] secret-like values are detected before durable evidence
[ ] API keys/tokens/provider credentials are redacted
[ ] environment values are redacted when present
[ ] raw command output is bounded and redacted before inclusion
[ ] raw file content is not durably logged unless explicitly allowed
[ ] redaction records preserve enough provenance for audit
[ ] redaction does not remove required task constraints unless recorded
[ ] redaction applies before evidence manifest/review report where applicable
[ ] redaction applies before model-ready pack output
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
secrets are written to context pack evidence
unredacted credentials reach packed model input
redaction removes important constraints without evidence
redaction is not test-covered
```

---

# 23. Model Compatibility Coverage

Required model compatibility behavior:

```text
[ ] selected model profile is considered
[ ] selected context-window mode is recorded
[ ] context-window limit is enforced
[ ] local/hosted mode constraints are respected
[ ] local runtime profile limits are respected when available
[ ] unsupported task type is blocked or marked incompatible
[ ] output budget is reserved
[ ] pack format matches target model/prompt contract where applicable
[ ] compatibility result is schema-valid
[ ] incompatibility returns BLOCKED or NEEDS_REPACK, not silent overflow
[ ] selected model's maximum input size is recorded
[ ] selected model's output mode requirements are recorded where available
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
pack exceeds selected model limit
model incompatibility is ignored
local-only policy is bypassed by hosted-model assumptions
unsupported output format is emitted without warning
output budget is not reserved
```

---

# 24. Tool Compatibility Coverage

Required tool compatibility behavior:

```text
[ ] available tools are read from Tool / MCP Adapter or policy context
[ ] unavailable tools are not listed as usable
[ ] blocked tools are not presented as allowed
[ ] required tools are checked before pack finalization
[ ] tool-call context includes tool names, constraints, and limits
[ ] tool compatibility result is schema-valid
[ ] mismatch returns BLOCKED, NEEDS_TOOL, or NEEDS_REPACK
[ ] tool permission state is recorded or referenced
[ ] MCP-only tools are not assumed available unless exposed and allowed
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
packed task tells model to use unavailable tools
blocked tools are presented as available
required tool absence is ignored
tool compatibility cannot be audited
```

---

# 25. Prompt Contract Acceptance Coverage

This section applies if the layer emits final prompt/task packs.

Required behavior:

```text
[ ] packed task separates instruction blocks from source content blocks
[ ] trusted instructions are explicitly labeled
[ ] untrusted source content is explicitly labeled as data
[ ] instruction/data boundary is validated
[ ] instruction/data boundary hash is recorded where applicable
[ ] model-facing task goal is preserved
[ ] output format is preserved
[ ] allowed tools are listed only after tool compatibility check
[ ] disallowed tools/actions are preserved
[ ] context provenance is preserved or referenced
[ ] injection findings are not hidden from downstream components
[ ] redaction status is recorded
[ ] final prompt/task pack validates against packed_task.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
final prompt merges untrusted context with trusted instructions
final prompt omits explicit constraints
final prompt lists unavailable or blocked tools
final prompt lacks provenance references
final prompt lacks trust-boundary validation
```

---

# 26. Determinism / Idempotency Coverage

Required deterministic packing behavior:

```text
[ ] same inputs produce the same context pack ordering
[ ] same inputs produce the same context pack hash or justified timestamp-excluded hash
[ ] same inputs produce the same packed task hash or justified timestamp-excluded hash
[ ] ranking tie-breakers are deterministic
[ ] deduplication tie-breakers are deterministic
[ ] compression output is deterministic or compression variance is evidenced
[ ] volatile fields are excluded from stable hash or separately recorded
[ ] repeated run does not append duplicate final artifacts without run ID separation
[ ] idempotency result is evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
same input produces materially different packs without evidence
ranking order changes across identical runs without reason
pack hash cannot be reproduced
volatile fields invalidate reproducibility without stable-hash handling
```

---

# 27. CLI / Command Acceptance Coverage

This section applies only if this layer exposes CLI commands.

Required behavior:

```text
[ ] CLI commands are deterministic
[ ] CLI commands do not require network, model inference, or external providers for validation
[ ] CLI commands accept explicit input/output paths
[ ] CLI commands write only approved runtime artifacts
[ ] CLI commands return non-zero exit codes on validation failure
[ ] CLI commands record evidence when they build packs
[ ] CLI commands reject over-budget, injected, or incompatible packs
[ ] CLI commands do not mutate source files
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
CLI command silently emits unsafe pack
CLI command mutates source files
CLI command requires network/model inference for validation
CLI command returns success despite schema/budget/injection failure
```

---

# 28. Integration Coverage

## 28.1 Policy / Capability Registry Integration

```text
[ ] source access policy is checked or delegated through approved tools
[ ] tool availability policy is checked before including tools in pack
[ ] model/provider mode policy is checked before declaring model compatibility
[ ] policy denial returns BLOCKED or NEEDS_REPACK
[ ] policy decisions are referenced in evidence where available
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 28.2 Tool / MCP Adapter Integration

```text
[ ] tool context comes from registry or adapter output, not hard-coded assumptions
[ ] blocked tools are excluded or marked unavailable
[ ] MCP-only tools require explicit MCP exposure evidence
[ ] tool compatibility mismatch blocks final pack or records NEEDS_TOOL
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 28.3 Model Adapter / Local Runtime Profile Integration

```text
[ ] model profile source is recorded
[ ] local runtime constraints are represented when available
[ ] hosted-only assumptions are blocked under local-only policy
[ ] max input and output budgets match selected profile
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 28.4 Prompt Contract / Prompt Versioning Integration

```text
[ ] prompt/task-pack version is recorded
[ ] instruction/data boundaries match the prompt contract
[ ] packed task schema version is recorded
[ ] downstream prompt contract incompatibility blocks final pack or records NEEDS_REPACK
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

## 28.5 Instruction Hierarchy and Trust-Boundary Integration

Required behavior:

```text
[ ] system/project/developer/task constraints are represented as trusted instructions only when they originate from trusted sources
[ ] retrieved files, tool outputs, reports, logs, and user-provided source content are represented as data unless explicitly promoted by policy
[ ] untrusted source text cannot create, remove, or reorder trusted instructions
[ ] tool output cannot silently override task requirements
[ ] prompt-injection labels remain attached after deduplication and compression
[ ] final packed task records instruction/data/source/tool-output boundaries
[ ] instruction hierarchy record is written to evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
untrusted source content becomes a trusted instruction
retrieved context changes task requirements without evidence
compressed source removes the injection warning or trust label
final pack cannot prove which text is instruction and which text is data
```

## 28.6 Required-Constraint Preservation and Omission-Reason Integration

Required behavior:

```text
[ ] every explicit task requirement is assigned a stable requirement ID
[ ] mandatory constraints are marked non-droppable unless policy permits exclusion
[ ] budgeting may compress required constraints but must not delete them silently
[ ] deduplication may merge duplicates but must preserve the strongest requirement wording
[ ] compression records before/after constraint preservation evidence
[ ] every omitted, truncated, compressed, demoted, or excluded context item records a reason code
[ ] omitted required context blocks final pack or records NEEDS_REPACK
[ ] final packed task includes a requirement coverage map
```

Required omission reason codes:

```text
DUPLICATE
LOW_RELEVANCE
STALE_SUPERSEDED
LOW_TRUST
PROMPT_INJECTION_RISK
SENSITIVE_REDACTED
TOKEN_BUDGET_EXCEEDED
MODEL_INCOMPATIBLE
TOOL_UNAVAILABLE
POLICY_DENIED
SOURCE_UNAVAILABLE
CONFLICT_WITH_HIGHER_AUTHORITY
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
mandatory task constraint is dropped
required source is omitted without a reason
compression changes the meaning of a requirement
budgeting hides loss of required context
omitted required context does not block or request repack
```

---

# 29. Audit / Evidence Coverage

Required evidence behavior:

```text
[ ] context_source_history.jsonl is written
[ ] context_pack_history.jsonl is written
[ ] context_budget_history.jsonl is written
[ ] context_ranking_history.jsonl is written for ranking decisions
[ ] context_recency_history.jsonl is written for recency/staleness decisions
[ ] context_injection_history.jsonl is written for injection findings
[ ] context_redaction_history.jsonl is written for redaction findings
[ ] latest_context_pack.json is written atomically
[ ] latest_packed_task.json is written atomically
[ ] context_builder_task_packer_evidence_manifest.json is written
[ ] context_builder_task_packer_review_report.json is written
[ ] context_builder_task_packer_completion_record.json is written after validation
[ ] evidence includes reviewed commit
[ ] evidence includes command text, exit codes, statuses, and summaries
[ ] evidence includes schema validation summary
[ ] evidence includes hashes for final evidence artifacts
[ ] evidence includes context pack hash if final pack emitted
[ ] evidence includes packed task hash if final task emitted
[ ] secrets are redacted before logging
[ ] source provenance is recorded
[ ] source inclusion/exclusion decisions are recorded
[ ] budget decisions are recorded
[ ] ranking/recency decisions are recorded
[ ] injection/redaction decisions are recorded
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
context pack creation is not evidenced
budgeting decisions are not evidenced
ranking/recency decisions are not evidenced
injection/redaction findings are not evidenced
secrets are logged
reviewed commit is missing
required hashes are missing
```

---

# 30. Evidence Manifest

Create:

```text
.agentx-init/context_packs/context_builder_task_packer_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "context_pack_evidence_manifest.schema.json",
  "component_id": "AGENTX_CONTEXT_BUILDER_TASK_PACKER",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>"
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
  "context_pack_path": ".agentx-init/context_packs/latest_context_pack.json",
  "context_pack_sha256": "<sha256 or NOT_EMITTED>",
  "context_pack_canonical_sha256": "<sha256 or NOT_EMITTED>",
  "context_pack_canonical_sha256": "<sha256 or NOT_EMITTED>",
  "packed_task_path": ".agentx-init/context_packs/latest_packed_task.json",
  "packed_task_sha256": "<sha256 or NOT_EMITTED>",
  "packed_task_canonical_sha256": "<sha256 or NOT_EMITTED>",
  "requirement_coverage_map_sha256": "<sha256 or NOT_EMITTED>",
  "packed_task_canonical_sha256": "<sha256 or NOT_EMITTED>",
  "requirement_coverage_map_sha256": "<sha256 or NOT_EMITTED>",
  "stable_context_pack_hash": "<hash excluding volatile fields or NOT_EMITTED>",
  "stable_packed_task_hash": "<hash excluding volatile fields or NOT_EMITTED>",
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "source_ranking_status": "PASS",
  "recency_status": "PASS",
  "budgeting_status": "PASS",
  "prompt_injection_status": "PASS",
  "redaction_status": "PASS",
  "instruction_hierarchy_status": "PASS",
  "constraint_preservation_status": "PASS",
  "omission_reason_status": "PASS",
  "golden_fixture_status": "PASS",
  "model_compatibility_status": "PASS",
  "tool_compatibility_status": "PASS",
  "determinism_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

The manifest must include paths and hashes for all final evidence files, including:

```text
context_builder_task_packer_evidence_manifest.json
context_builder_task_packer_review_report.json
context_builder_task_packer_completion_record.json
command output artifacts, if stored as files
JSONL evidence histories used by the review
latest_context_pack.json, if used by the review
latest_packed_task.json, if used by the review
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Approved runtime artifact boundary:

```text
.agentx-init/context_packs/
```

Evidence artifacts for this layer must not be written outside that root unless the review records the exception in the deviation register.

---

# 31. Review Report Artifact

Create:

```text
.agentx-init/context_packs/context_builder_task_packer_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "context_pack_review_report.schema.json",
  "component_id": "AGENTX_CONTEXT_BUILDER_TASK_PACKER",
  "review_document_id": "CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v3.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>"
  },
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/context_packs/context_builder_task_packer_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/context_packs/context_builder_task_packer_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/context_packs/context_builder_task_packer_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "context_pack_sha256": "<sha256 or NOT_EMITTED>",
  "packed_task_sha256": "<sha256 or NOT_EMITTED>",
  "stable_context_pack_hash": "<stable hash or NOT_EMITTED>",
  "stable_packed_task_hash": "<stable hash or NOT_EMITTED>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, if it lacks command exit codes, or if it lacks required final hashes.

## 31.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

---

# 32. Source Mutation Check

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
only expected runtime artifacts under .agentx-init/context_packs/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by tests
unapproved files are created outside runtime artifact paths
context packing mutates source files
context packing rewrites user/project documents
evidence artifacts are written outside `.agentx-init/context_packs/` without deviation record
```

---

# 33. Negative Test Pack

The review must prove forbidden behavior fails closed.

Required negative cases:

```text
[ ] missing task goal -> INVALID or BLOCKED
[ ] missing explicit constraints when required -> INVALID or BLOCKED
[ ] over-budget pack -> BLOCKED or NEEDS_REPACK
[ ] untrusted injected instruction -> demoted or filtered
[ ] injected instruction tries to override system/project constraints -> blocked
[ ] injected instruction tries to enable blocked tool -> blocked/demoted
[ ] injected instruction asks to reveal secrets -> redacted/blocked
[ ] secret-like input -> redacted before evidence
[ ] unavailable tool requested -> BLOCKED or NEEDS_TOOL
[ ] blocked tool requested -> BLOCKED
[ ] incompatible model selected -> BLOCKED or NEEDS_REPACK
[ ] stale low-trust source conflicts with current high-trust source -> conflict recorded, no override
[ ] newer low-trust source conflicts with older high-trust source -> no silent override
[ ] duplicate context with conflict -> conflict recorded, no silent overwrite
[ ] compression would drop required constraint -> compression blocked
[ ] compression would remove provenance -> compression blocked
[ ] source unavailable -> exclusion/failure record, no crash
[ ] raw source content too large -> bounded/summarized with provenance
[ ] untrusted context attempts to become trusted instruction -> blocked/demoted
[ ] identical input run twice -> stable hash or justified variance
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked not applicable with justification.

---

# 34. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Schema | CLI | Prompt Contract | Model Compatibility | Tool Compatibility | Ranking | Recency | Evidence | Runtime Artifact Boundary | Other>
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
Runtime artifact writes outside `.agentx-init/context_packs/` require a deviation entry.
Missing evidence hashes cannot be accepted as a deviation for DONE.
Prompt/task-pack contract failures cannot be accepted as deviations for DONE if this layer emits final packs.
Model compatibility failures cannot be accepted as deviations for DONE.
Ranking/recency failures cannot be accepted as deviations for DONE if they affect final pack contents.
```

---

# 35. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
context-source coverage:
source access integration:
task-input coverage:
source ranking coverage:
recency/staleness coverage:
budgeting coverage:
deduplication coverage:
compression coverage:
prompt-injection handling:
redaction coverage:
model compatibility:
tool compatibility:
prompt contract compatibility:
determinism/idempotency:
CLI / command coverage:
audit/evidence:
evidence manifest:
review report:
evidence hashes:
negative tests:
source mutation check:
completion record:
```

---

# 36. What Failed

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

# 37. Issue Severity Classification

## 37.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
context pack exceeds selected model limit
explicit task constraints are dropped
safety constraints are dropped
output format requirements are dropped
untrusted context becomes trusted instruction
prompt injection can override task/system/project constraints
secrets are logged or packed into model input
blocked or unavailable tools are presented as usable
source provenance is missing
source ranking evidence is missing
recency/staleness evidence is missing
budget decision evidence is missing
injection/redaction evidence is missing
audit/evidence is missing
evidence hashes are missing
final pack hash is missing when final pack is emitted
review report is missing
completion record is missing
source mutation occurs directly in this layer
required area remains NOT CHECKED
required command remains NOT RUN
```

## 37.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
partial context-source coverage
partial source ranking coverage
partial recency/staleness coverage
partial model compatibility coverage
partial tool compatibility coverage
compression provenance incomplete
budget evidence incomplete
injection findings recorded inconsistently
redaction evidence incomplete
prompt contract compatibility incomplete
review environment not recorded
runtime artifact boundary exception lacks justification
determinism evidence incomplete
```

## 37.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled context source type
optional report writer absent
additional future-layer test exists but is not active
manual review note needed for unusual source type
```

---

# 38. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Package, schema, test, and runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, completion record, ranking/recency records, and pack hashes. |
| Context-source, source ranking, recency, and task-input coverage | 1.0 | Sources, trust levels, provenance, source priority, freshness, task goals, constraints, and output requirements preserved. |
| Budgeting and model compatibility | 1.0 | Selected model limits, context budget, output budget, local/hosted constraints enforced. |
| Deduplication and compression | 1.0 | Duplicates/conflicts handled safely; compression preserves constraints and provenance. |
| Injection handling and redaction | 1.0 | Untrusted instructions demoted/filtered; secrets redacted before evidence and model input. |
| Tool/prompt compatibility and determinism | 1.0 | Tool availability, prompt contract compatibility, stable pack ordering, and reproducible hashes proven. |
| Audit/evidence and source-mutation safety | 1.0 | JSONL/latest artifacts, manifest, report, hashes, completion record, clean git status. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for model-ready task packing
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
pack exceeds selected model limit caps score at 5.0
explicit task constraints dropped caps score at 5.0
untrusted context promoted to trusted instruction caps score at 4.0
secrets logged or packed into model input caps score at 4.0
blocked/unavailable tools presented as usable caps score at 5.0
source ranking failure caps score at 7.0
recency/staleness conflict ignored caps score at 7.0
non-reproducible pack without evidence caps score at 8.0
source mutation by tests caps score at 7.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
missing final pack hash when pack emitted caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
```

---

# 39. GO / NO-GO Rules

## 39.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
context-source tests pass
source access integration tests pass
task-input tests pass
source ranking tests pass
recency/staleness tests pass
budgeting tests pass
deduplication tests pass
compression tests pass
prompt-injection tests pass
redaction tests pass
model compatibility tests pass
tool compatibility tests pass
prompt contract compatibility passes or is not applicable
determinism/idempotency tests pass
CLI / command wrapper tests pass or are not applicable
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

## 39.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
packed context exceeds selected model budget
required task constraints are dropped
safety constraints are dropped
output format requirements are dropped
source ranking is not evidenced
stale or lower-trust source silently overrides trusted/current source
prompt injection is not handled
untrusted context is promoted to trusted instruction
sensitive data is not redacted
unavailable tools are presented as available
blocked tools are presented as available
model incompatibility is ignored
tool incompatibility is ignored
source provenance is missing
audit/evidence is missing
evidence manifest is missing
evidence hashes are missing
final pack hash is missing when pack emitted
review report is missing
completion record is missing
source mutation occurs
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 40. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix context source provenance fields
fix source access integration
fix source ranking rules
fix recency/staleness rules
fix task-input preservation
fix budget calculations
fix model compatibility checks
fix tool compatibility checks
fix deduplication conflict handling
fix compression preservation rules
fix prompt-injection detection/demotion
fix redaction rules
fix deterministic tie-breakers
fix stable pack hashing
fix evidence writing
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix tests to reflect the contract
fix runtime artifact boundary checks
```

Forbidden fixes:

```text
do not remove model compatibility checks to pass tests
do not remove tool compatibility checks to pass tests
do not remove source ranking/recency checks to pass tests
do not silently truncate context to pass budget tests
do not drop explicit user constraints to fit budget
do not merge trusted and untrusted instruction blocks
do not mark injected content as trusted
do not skip redaction to preserve output content
do not make pack output non-deterministic without evidence
do not omit hashes for final DONE
do not skip evidence writing
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
do not require network, hosted model, or LLM inference for validation
```

---

# 41. Definition of Done

The Context Builder / Task Packer layer is done when it can safely construct model-ready task packs without losing requirements, exceeding model limits, promoting untrusted instructions, presenting unavailable tools as usable, or leaking sensitive data.

It must prove:

```text
all target files exist
all required schemas exist
all required tests exist
context sources are represented with provenance
source access is controlled or delegated through approved tool/policy paths
source ranking is deterministic and evidenced
recency/staleness is recorded and evidenced
task inputs preserve goals, constraints, required artifacts, and output requirements
budgeting enforces model context limits
output budget is reserved
deduplication preserves unique constraints and provenance
compression preserves task constraints, safety constraints, output requirements, and provenance
prompt-injection handling prevents untrusted instruction override
redaction prevents sensitive data leakage
model compatibility is checked before pack finalization
tool compatibility is checked before pack finalization
prompt/task-pack contract compatibility is checked when final packs are emitted
determinism/idempotency is proven or deviations are evidenced
audit/evidence records are written
latest context pack is written atomically
latest packed task is written atomically
context pack and packed task hashes are written when emitted
evidence manifest is written
review report is written
evidence hashes are written
negative tests prove forbidden behavior fails closed
no source mutation occurs directly in this layer
completion record exists
final verdict is recorded
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_context_pack_schemas.py
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

# 42. Required Evidence Package

The completion evidence package must include:

```text
compileall output
pytest output
schema validation result
context-source test result
source access integration test result
task-input test result
source ranking test result
recency/staleness test result
budgeting test result
deduplication test result
compression test result
prompt-injection test result
redaction test result
model compatibility test result
tool compatibility test result
prompt contract compatibility test result or N/A note
determinism/idempotency test result
CLI / command test result or N/A note
negative-test result
audit/evidence test result
evidence manifest
review report
git status output
completion record
SHA-256 hashes for final evidence artifacts
SHA-256 hash for latest context pack if emitted
SHA-256 hash for latest packed task if emitted
```

The evidence package must show:

```text
reviewed commit
validation timestamp
review environment
command exit codes
no source mutation
no network required for validation
no model inference required for validation
context provenance preserved
source ranking evidenced
recency/staleness evidenced
task constraints preserved
budget limits enforced
prompt injection demoted or filtered
secrets redacted
blocked/unavailable tools not presented as usable
stable hashes for final pack artifacts
hashes for final evidence artifacts
```

---

# 43. Completion Evidence Record

After validation, create:

```text
.agentx-init/context_packs/context_builder_task_packer_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_CONTEXT_BUILDER_TASK_PACKER",
  "component_name": "Context Builder / Task Packer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>"
  },
  "canonical_context_subdirectory": "tools/agentx_evolve/context/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/context_packs/",
  "basis_documents": [
    "CONTEXT_BUILDER_TASK_PACKER_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_SPEC",
    "CONTEXT_BUILDER_TASK_PACKER_IMPLEMENTATION_REVIEW_AND_DOD_v3"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "context_sources_verified": [],
  "source_access_integration_verified": [],
  "task_inputs_verified": [],
  "source_ranking_verified": [],
  "recency_staleness_verified": [],
  "budgeting_verified": [],
  "deduplication_verified": [],
  "compression_verified": [],
  "prompt_injection_handling_verified": [],
  "redaction_verified": [],
  "instruction_hierarchy_verified": [],
  "constraint_preservation_verified": [],
  "omission_reasons_verified": [],
  "golden_fixtures_verified": [],
  "model_compatibility_verified": [],
  "tool_compatibility_verified": [],
  "prompt_contract_compatibility_verified": [],
  "determinism_idempotency_verified": [],
  "cli_command_compatibility_verified": [],
  "negative_tests_verified": [],
  "context_pack_sha256": "<sha256 or NOT_EMITTED>",
  "packed_task_sha256": "<sha256 or NOT_EMITTED>",
  "stable_context_pack_hash": "<hash or NOT_EMITTED>",
  "stable_packed_task_hash": "<hash or NOT_EMITTED>",
  "evidence_manifest_path": ".agentx-init/context_packs/context_builder_task_packer_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/context_packs/context_builder_task_packer_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
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
evidence manifest is missing
evidence hashes are missing
final pack hash is missing when final pack is emitted
review report is missing
completion record is missing
```

---

# 45. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/context/ exists
[ ] schemas exist
[ ] tests exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Context Sources:
[ ] sources have provenance
[ ] sources have trust levels
[ ] source access is controlled or delegated through approved tool/policy path
[ ] unavailable sources fail safely
[ ] untrusted context cannot become trusted instruction

Task Input:
[ ] task goal preserved
[ ] explicit constraints preserved
[ ] output requirements preserved
[ ] safety requirements preserved
[ ] unresolved ambiguity is recorded, not guessed silently
[ ] required-constraint coverage map exists
[ ] mandatory constraints are not dropped by budget, deduplication, or compression

Ranking / Recency:
[ ] source ranking is deterministic
[ ] source priority respects trust, requiredness, and relevance
[ ] recency/staleness is recorded
[ ] stale source cannot silently override trusted/current source
[ ] ranking and recency evidence written
[ ] omitted, truncated, compressed, demoted, and excluded sources have reason codes

Budgeting:
[ ] model context window enforced
[ ] token budget enforced
[ ] output budget reserved
[ ] over-budget pack blocks or repacks safely

Deduplication / Compression:
[ ] duplicates handled deterministically
[ ] conflicts recorded
[ ] compression preserves constraints
[ ] compression preserves provenance
[ ] compression preserves output requirements

Prompt Injection / Redaction:
[ ] injection attempts demoted or filtered
[ ] untrusted instructions cannot override trusted instructions
[ ] secrets redacted before evidence
[ ] secrets redacted before model-ready pack
[ ] redaction records written

Compatibility:
[ ] selected model compatibility checked
[ ] local runtime limits checked where applicable
[ ] tool availability checked
[ ] blocked/unavailable tools not presented as usable
[ ] prompt/task-pack contract compatibility checked or N/A

Determinism / Hashing:
[ ] repeated identical input produces stable ordering
[ ] stable context pack hash recorded
[ ] stable packed task hash recorded
[ ] canonical context pack hash recorded
[ ] canonical packed task hash recorded
[ ] golden fixture regression passed
[ ] volatile fields handled separately

Evidence:
[ ] context source history written
[ ] context pack history written
[ ] budget history written
[ ] ranking history written
[ ] recency history written
[ ] injection history written
[ ] redaction history written
[ ] omission history written
[ ] constraint preservation history written
[ ] instruction hierarchy history written
[ ] golden fixture history written
[ ] latest context pack written atomically
[ ] latest packed task written atomically
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written

Safety:
[ ] no source mutation directly in this layer
[ ] no network required by validation
[ ] no LLM/model inference required by validation
[ ] no secrets logged

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
Context Builder / Task Packer Validation — Commit <hash>

Reviewer / Environment:
- reviewer: <name or tool>
- reviewed commit: <hash>
- reviewed branch: <branch>
- reviewed at UTC: <timestamp>
- OS: <name/version>
- Python: <version>
- pytest: <version or NOT INSTALLED>
- jsonschema: <version or NOT INSTALLED>

Status:
- initial git status: CLEAN/EXPECTED_RUNTIME_ARTIFACTS_ONLY/DIRTY
- compileall: PASS/FAIL, exit_code=<code>
- pytest: PASS/FAIL, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- context-source coverage: PASS/FAIL
- source access integration: PASS/FAIL
- task-input coverage: PASS/FAIL
- required-constraint preservation: PASS/FAIL
- instruction hierarchy coverage: PASS/FAIL
- omission-reason coverage: PASS/FAIL
- source ranking coverage: PASS/FAIL
- recency/staleness coverage: PASS/FAIL
- budgeting coverage: PASS/FAIL
- deduplication coverage: PASS/FAIL
- compression coverage: PASS/FAIL
- prompt-injection handling: PASS/FAIL
- redaction coverage: PASS/FAIL
- model compatibility coverage: PASS/FAIL
- tool compatibility coverage: PASS/FAIL
- prompt contract compatibility: PASS/FAIL/N/A
- determinism/idempotency: PASS/FAIL
- golden fixture regression: PASS/FAIL
- CLI / command coverage: PASS/FAIL/N/A
- audit/evidence coverage: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- context pack hash: PRESENT/MISSING/NOT_EMITTED
- packed task hash: PRESENT/MISSING/NOT_EMITTED
- review report: PRESENT/MISSING
- negative-test coverage: PASS/FAIL
- source mutation check: PASS/FAIL
- completion record: PRESENT/MISSING

Reproducibility:
- exact commands recorded: YES/NO
- exit codes recorded: YES/NO
- output artifacts recorded: YES/NO
- final hashes recorded: YES/NO
- stable pack hash recorded: YES/NO/NOT_EMITTED
- canonical pack hash recorded: YES/NO/NOT_EMITTED
- stable packed task hash recorded: YES/NO/NOT_EMITTED
- canonical packed task hash recorded: YES/NO/NOT_EMITTED
- requirement coverage map recorded: YES/NO/NOT_EMITTED
- deviations recorded: YES/NO/N/A

Final decision:
DONE / NOT DONE

Implementation rating:
<0-10>

Evidence paths:
- evidence manifest: <path>, sha256=<hash>
- review report: <path>, sha256=<hash>
- completion record: <path>, sha256=<hash>
- context pack: <path or NOT_EMITTED>, sha256=<hash or NOT_EMITTED>, canonical_sha256=<hash or NOT_EMITTED>
- packed task: <path or NOT_EMITTED>, sha256=<hash or NOT_EMITTED>, canonical_sha256=<hash or NOT_EMITTED>
- requirement coverage map: <path or NOT_EMITTED>, sha256=<hash or NOT_EMITTED>

Remaining blockers:
- none / list blockers

Accepted non-blocking follow-ups:
- none / list follow-ups
```

---

# 47. v4 Final Freeze Addendum

This v4 review / DoD document is frozen as the final validation template for the Context Builder / Task Packer layer.

Allowed future changes:

```text
PATCH: typo fixes, wording clarifications, example formatting
MINOR: optional implementation notes that do not change required safety behavior
MAJOR: changed source-trust model, changed instruction hierarchy, changed required evidence, changed context-pack compatibility rules, or changed DONE criteria
```

Blocked without major revision:

```text
allowing untrusted context to become trusted instruction
allowing required constraints to be dropped silently
removing omission-reason evidence
removing canonical pack hashes
removing golden fixture regression
removing prompt-injection filtering
removing model-runtime compatibility checks
removing source-access policy/tool-mediated checks
removing audit/evidence requirements
allowing validation to require network, hosted providers, or live model inference
```

---

# 48. Final Rating

This v4 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the v3 validation coverage and adds the final production controls needed for a frozen 10/10 DoD: explicit instruction hierarchy review, required-constraint preservation, omission-reason evidence, source-trust conflict handling, canonical stable pack hashes, golden fixture regression, model-free validation boundaries, stronger evidence artifacts, stricter GO/NO-GO criteria, and final sign-off fields that prevent DONE from being claimed without reproducible pack evidence and reviewed implementation proof.
```
