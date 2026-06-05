# PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_REVIEW_AND_DOD
version: v3.0
status: final frozen post-implementation review template and Definition of Done
component_id: AGENTX_PROMPT_CONTRACT_VERSIONING
component_name: Prompt Contract / Prompt Versioning Layer
roadmap_layer: 9
roadmap_phase: Phase C — Prompt Governance and Runtime Binding
review_use: use after code is committed
basis_documents:
  - PROMPT_CONTRACT_VERSIONING_EQC_FIC_SIB_SCHEMA_CONTRACT
  - PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_SPEC
  - PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_REVIEW_AND_DOD_v2
  - PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_REVIEW_AND_DOD_v3
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria
optional_standards: ES, Report Template
canonical_prompt_subdirectory: tools/agentx_evolve/prompts/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/prompts/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v3 Review and Upgrade Summary

The v2 review / DoD document was strong and nearly complete. I would rate v2:

```text
9.7/10
```

It already covered the required post-implementation review areas:

```text
what exists
what passed
what failed
compileall result
pytest result
schema validation result
prompt registry coverage
prompt versioning coverage
prompt compatibility coverage
prompt safety-rule coverage
prompt provenance coverage
prompt diff/migration coverage
source mutation check
audit/evidence coverage
definition of done
final done/not-done verdict
standards applied
why this layer needs these standards
```

It was not fully 10/10 because several final review-control details were still under-specified:

```text
1. Section numbering used lettered insertions such as 8A and 25A, which is less stable for references than normal numeric sectioning.
2. The document did not define strict prompt canonicalization before hashing.
3. The document required hashes but did not define self-hash handling for evidence manifest, review report, and completion record.
4. The document did not require a prompt registry lock / active-version concurrency rule.
5. The document did not require idempotency checks for repeated runtime binding and repeated validation.
6. The document did not distinguish clearly enough between DEFERRED SAFELY, NOT APPLICABLE, and PARTIAL for Model Adapter, Context Builder, Worker, CLI, and MCP integrations.
7. The document did not require a scoped Prompt Contract pytest command when broader `tools/agentx_evolve/tests` contains future-layer tests.
8. The document did not require prompt fixture isolation to prevent tests from mutating real prompt source files.
9. The document did not define a strict runtime artifact boundary exception register.
10. The final sign-off did not require enough reviewer-independence and reproducibility detail.
```

This v3 applies those corrections and is the final 10/10 post-implementation review / Definition of Done template for the Prompt Contract / Prompt Versioning Layer.

---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Prompt Contract / Prompt Versioning Layer**.

Use this document after code is committed to decide whether the layer is complete, validated, safe, auditable, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether the prompt registry is complete
whether prompt versioning is deterministic
whether active prompt versions are explicit
whether compatibility checks work
whether prompt safety rules are enforced
whether prompt provenance is recorded
whether prompt diff/migration behavior is safe
whether prompt runtime binding is controlled
whether prompt canonicalization and hashing are stable
whether prompt injection and variable redaction controls work
whether source mutation checks pass
whether audit/evidence is complete
whether the final verdict is DONE or NOT DONE
```

A `10/10` rating for this review document does not mean the implementation is done. The implementation is done only after the validation commands and evidence checks in this document pass.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because this layer controls prompt identity, active prompt version selection, role permissions, model/task compatibility, prompt safety rules, runtime binding, output expectations, and provenance for model-facing behavior.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
```

## 2.3 Conditional Standards

```text
Command Acceptance Criteria, only if prompt validation exposes CLI commands
MCP Protocol Acceptance Criteria, only if prompts are exposed through MCP
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if it writes markdown reports
```

---

# 3. Why This Layer Needs These Standards

Prompt Contract / Prompt Versioning is safety-critical because it decides:

```text
which prompts exist
which prompt version is active
which roles can use which prompts
which model/task each prompt is valid for
which tools a prompt may request
which output format a prompt must produce
which safety rules are attached to a prompt
which prompt changes are compatible or breaking
which prompt version was used for a generated action
whether prompt drift occurred
whether prompt injection defenses are included
whether prompt provenance is auditable
```

This layer must prevent:

```text
prompt drift
untracked prompt mutation
implicit latest-version binding
unauthorized role-prompt binding
unsafe tool-request permissions
output-format mismatch
undocumented prompt migrations
untraceable model behavior
unredacted prompt variable leakage
prompt injection that attempts to bypass policy, sandbox, governance, provenance, or audit
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

---

# 5. Review Validity Rules

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
[ ] scoped Prompt Contract / Versioning pytest command is recorded if broader tests include unrelated future-layer tests
[ ] review report artifact is created
[ ] evidence manifest exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] required evidence hashes are present
[ ] prompt canonicalization algorithm is recorded or referenced
[ ] prompt registry snapshot hash is recorded
[ ] runtime binding hash is recorded when variables are rendered
[ ] reviewer did not rely only on the document's internal rating
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

The implementation may be marked `DONE` only when the recorded validation evidence satisfies the GO criteria.

---

# 6. Status Vocabulary

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
| NOT APPLICABLE | Requirement does not apply to the implemented scope and has no runtime entry point. | Yes, if justified |
| DEFERRED SAFELY | Feature is planned/stubbed but cannot execute, expose, mutate, bind prompts, call network, or bypass policy. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

---

# 7. Deferral and Applicability Rules

Use these rules to prevent missing work from being mislabeled as safe.

```text
NOT APPLICABLE:
  Use only when the feature is outside the implemented scope and has no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot bind prompts, expose prompts, mutate prompt state, call models, call tools, call network, or bypass policy/evidence.

PARTIAL:
  Use when some files/tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

Model Adapter, Context Builder, LLM Implementation Worker, CLI, and MCP integrations may be `DEFERRED SAFELY` only if the review proves:

```text
no runtime prompt binding bypasses the missing integration
no unversioned prompt text is accepted
no model call is made by this layer
no MCP server starts automatically
no network port opens
no CLI command mutates prompt source outside an approved migration
safe deferral is recorded in the deviation register
negative tests prove blocked behavior where applicable
```

---

# 8. Expected Implementation Scope

## 8.1 Required Prompt Package

Expected location:

```text
tools/agentx_evolve/prompts/
```

Expected files:

```text
tools/agentx_evolve/prompts/__init__.py
tools/agentx_evolve/prompts/prompt_models.py
tools/agentx_evolve/prompts/prompt_registry.py
tools/agentx_evolve/prompts/prompt_versioning.py
tools/agentx_evolve/prompts/prompt_compatibility.py
tools/agentx_evolve/prompts/prompt_safety.py
tools/agentx_evolve/prompts/prompt_provenance.py
tools/agentx_evolve/prompts/prompt_diff.py
tools/agentx_evolve/prompts/prompt_migration.py
tools/agentx_evolve/prompts/prompt_runtime_binding.py
tools/agentx_evolve/prompts/prompt_audit_logger.py
```

## 8.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
prompt_contract.schema.json
prompt_version.schema.json
prompt_registry.schema.json
prompt_input_contract.schema.json
prompt_output_contract.schema.json
prompt_safety_rule.schema.json
prompt_provenance.schema.json
prompt_diff.schema.json
prompt_migration.schema.json
prompt_runtime_binding.schema.json
prompt_permission_matrix.schema.json
prompt_audit.schema.json
prompt_evidence_manifest.schema.json
prompt_review_report.schema.json
prompt_completion_record.schema.json
```

## 8.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_prompt_registry.py
test_prompt_versioning.py
test_prompt_contract_schema.py
test_prompt_input_output_contracts.py
test_prompt_compatibility.py
test_prompt_safety_rules.py
test_prompt_provenance.py
test_prompt_diff_migration.py
test_prompt_runtime_binding.py
test_prompt_permission_matrix.py
test_prompt_audit_logger.py
test_prompt_negative_cases.py
test_prompt_schema_validation.py
test_prompt_canonicalization_hashing.py
test_prompt_idempotency_and_locking.py
```

## 8.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/prompts/
```

Expected artifacts:

```text
prompt_registry_snapshot.json
prompt_version_history.jsonl
prompt_binding_history.jsonl
prompt_safety_decision_history.jsonl
prompt_provenance_history.jsonl
prompt_diff_history.jsonl
prompt_migration_history.jsonl
prompt_lock_history.jsonl
latest_prompt_binding.json
latest_prompt_provenance.json
prompt_contract_versioning_evidence_manifest.json
prompt_contract_versioning_review_report.json
prompt_contract_versioning_completion_record.json
```

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
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_prompt_schemas.py
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

If `validate_prompt_schemas.py` is not implemented, equivalent schema coverage must be proven by:

```bash
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_prompt_schema_validation.py
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
```

---

# 10. Scoped Prompt Test Command

If unrelated future-layer tests exist under `tools/agentx_evolve/tests`, record a scoped Prompt Contract / Versioning test command.

```bash
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_prompt_registry.py \
  tools/agentx_evolve/tests/test_prompt_versioning.py \
  tools/agentx_evolve/tests/test_prompt_contract_schema.py \
  tools/agentx_evolve/tests/test_prompt_input_output_contracts.py \
  tools/agentx_evolve/tests/test_prompt_compatibility.py \
  tools/agentx_evolve/tests/test_prompt_safety_rules.py \
  tools/agentx_evolve/tests/test_prompt_provenance.py \
  tools/agentx_evolve/tests/test_prompt_diff_migration.py \
  tools/agentx_evolve/tests/test_prompt_runtime_binding.py \
  tools/agentx_evolve/tests/test_prompt_permission_matrix.py \
  tools/agentx_evolve/tests/test_prompt_audit_logger.py \
  tools/agentx_evolve/tests/test_prompt_negative_cases.py \
  tools/agentx_evolve/tests/test_prompt_schema_validation.py \
  tools/agentx_evolve/tests/test_prompt_canonicalization_hashing.py \
  tools/agentx_evolve/tests/test_prompt_idempotency_and_locking.py
```

Record command text, exit code, status, summary, and output artifact.

---

# 11. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Prompt package location | `tools/agentx_evolve/prompts/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt schemas | all required prompt schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation command | schema command or pytest equivalent exists and passes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt tests | required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt registry coverage | registry loads, validates, snapshots, rejects duplicates | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt versioning coverage | active version selection, immutability, history, rollback-safe metadata | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt canonicalization/hash coverage | canonical text hash, rendered hash, schema hash, safety hash | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt compatibility coverage | breaking vs compatible changes classified | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt safety-rule coverage | injection defenses, tool-request limits, output constraints enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt provenance coverage | prompt ID/version/hash/runtime binding recorded | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt diff/migration coverage | diffs and migrations are deterministic and evidenced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime binding coverage | role/model/task/tool binding rules enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Locking/concurrency coverage | active-version changes and registry writes are serialized or conflict-safe | PASS / PARTIAL / FAIL / NOT CHECKED |
| Idempotency coverage | repeated validation/binding gives stable results and no duplicate unsafe evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Audit/evidence coverage | JSONL histories, latest artifacts, evidence manifest, review report written | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence hashing | manifest, review report, completion record, registry snapshot, binding/provenance hashes present | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | tests do not mutate source unexpectedly | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy integration | role permissions checked before prompt use | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool/MCP integration | prompts cannot request unauthorized tools | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Model integration | prompts bind only to compatible model/task profiles | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Context Builder integration | input contracts match packed context | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Worker integration | worker can use only registered prompt contracts | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Runtime artifact boundary | evidence only under approved runtime root or exception listed | PASS / PARTIAL / FAIL / NOT CHECKED |
| OpenCode borrowing | prompt/versioning ideas mapped safely, no unsafe runtime copied | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 12. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Prompt registry loads | `prompt_registry.py` | `test_prompt_registry.py` | registry snapshot / pytest output | PASS / PARTIAL / FAIL / NOT CHECKED |
| Duplicate prompt IDs rejected | `prompt_registry.py` | `test_prompt_registry.py` | pytest output | PASS / PARTIAL / FAIL / NOT CHECKED |
| Active version explicit | `prompt_versioning.py` | `test_prompt_versioning.py` | version history / registry snapshot | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt canonical hash recorded | `prompt_versioning.py` | `test_prompt_canonicalization_hashing.py` | provenance history / registry snapshot | PASS / PARTIAL / FAIL / NOT CHECKED |
| Rendered prompt hash recorded | `prompt_runtime_binding.py` / `prompt_provenance.py` | `test_prompt_runtime_binding.py` | latest binding / provenance history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Compatibility classified | `prompt_compatibility.py` | `test_prompt_compatibility.py` | compatibility or migration evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Safety rules enforced | `prompt_safety.py` | `test_prompt_safety_rules.py` | safety decision history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime binding controlled | `prompt_runtime_binding.py` | `test_prompt_runtime_binding.py` | binding history / latest binding | PASS / PARTIAL / FAIL / NOT CHECKED |
| Provenance written | `prompt_provenance.py` | `test_prompt_provenance.py` | provenance history / latest provenance | PASS / PARTIAL / FAIL / NOT CHECKED |
| Diff deterministic | `prompt_diff.py` | `test_prompt_diff_migration.py` | diff history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Migration governed | `prompt_migration.py` | `test_prompt_diff_migration.py` | migration history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Registry locking | `prompt_registry.py` / `prompt_versioning.py` | `test_prompt_idempotency_and_locking.py` | lock history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Permission matrix enforced | `prompt_runtime_binding.py` / policy integration | `test_prompt_permission_matrix.py` | binding denial / policy evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Audit logging | `prompt_audit_logger.py` | `test_prompt_audit_logger.py` | JSONL histories / latest artifacts | PASS / PARTIAL / FAIL / NOT CHECKED |
| Negative cases fail closed | multiple | `test_prompt_negative_cases.py` | blocked / invalid evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence manifest | evidence writer or manual review artifact | `test_prompt_schema_validation.py` | evidence manifest JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |
| Review report | report writer or manual review artifact | `test_prompt_schema_validation.py` | review report JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record | completion writer or manual review artifact | `test_prompt_schema_validation.py` | completion record JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 13. What Exists Checklist

## 13.1 Prompt Package Files

```text
[ ] tools/agentx_evolve/prompts/__init__.py
[ ] tools/agentx_evolve/prompts/prompt_models.py
[ ] tools/agentx_evolve/prompts/prompt_registry.py
[ ] tools/agentx_evolve/prompts/prompt_versioning.py
[ ] tools/agentx_evolve/prompts/prompt_compatibility.py
[ ] tools/agentx_evolve/prompts/prompt_safety.py
[ ] tools/agentx_evolve/prompts/prompt_provenance.py
[ ] tools/agentx_evolve/prompts/prompt_diff.py
[ ] tools/agentx_evolve/prompts/prompt_migration.py
[ ] tools/agentx_evolve/prompts/prompt_runtime_binding.py
[ ] tools/agentx_evolve/prompts/prompt_audit_logger.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 13.2 Schema Files

```text
[ ] prompt_contract.schema.json
[ ] prompt_version.schema.json
[ ] prompt_registry.schema.json
[ ] prompt_input_contract.schema.json
[ ] prompt_output_contract.schema.json
[ ] prompt_safety_rule.schema.json
[ ] prompt_provenance.schema.json
[ ] prompt_diff.schema.json
[ ] prompt_migration.schema.json
[ ] prompt_runtime_binding.schema.json
[ ] prompt_permission_matrix.schema.json
[ ] prompt_audit.schema.json
[ ] prompt_evidence_manifest.schema.json
[ ] prompt_review_report.schema.json
[ ] prompt_completion_record.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 13.3 Test Files

```text
[ ] test_prompt_registry.py
[ ] test_prompt_versioning.py
[ ] test_prompt_contract_schema.py
[ ] test_prompt_input_output_contracts.py
[ ] test_prompt_compatibility.py
[ ] test_prompt_safety_rules.py
[ ] test_prompt_provenance.py
[ ] test_prompt_diff_migration.py
[ ] test_prompt_runtime_binding.py
[ ] test_prompt_permission_matrix.py
[ ] test_prompt_audit_logger.py
[ ] test_prompt_negative_cases.py
[ ] test_prompt_schema_validation.py
[ ] test_prompt_canonicalization_hashing.py
[ ] test_prompt_idempotency_and_locking.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 13.4 Runtime Artifact Files

```text
[ ] prompt_registry_snapshot.json
[ ] prompt_version_history.jsonl
[ ] prompt_binding_history.jsonl
[ ] prompt_safety_decision_history.jsonl
[ ] prompt_provenance_history.jsonl
[ ] prompt_diff_history.jsonl
[ ] prompt_migration_history.jsonl
[ ] prompt_lock_history.jsonl
[ ] latest_prompt_binding.json
[ ] latest_prompt_provenance.json
[ ] prompt_contract_versioning_evidence_manifest.json
[ ] prompt_contract_versioning_review_report.json
[ ] prompt_contract_versioning_completion_record.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 14. Compileall Result

Record the compile result.

```text
command: PYTHONPATH=tools python -m compileall tools/agentx_evolve
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any Prompt Contract / Versioning Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 15. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
scoped_prompt_command: <prompt-only pytest command if used>
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: <path>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required prompt registry, versioning, compatibility, safety, provenance, diff/migration, schema, evidence, canonicalization, idempotency, locking, or runtime binding test fails
exit code is missing
```

---

# 16. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_prompt_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_prompt_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
```

Required schema tests:

```text
prompt contract schema accepts valid contract
prompt contract schema rejects missing prompt_id
prompt version schema accepts valid version
prompt version schema rejects missing semantic version
prompt registry schema accepts valid registry
prompt registry schema rejects duplicate active prompt bindings
prompt input contract schema accepts valid input contract
prompt output contract schema accepts valid output contract
prompt safety rule schema accepts valid safety rule
prompt provenance schema accepts valid provenance record
prompt diff schema accepts valid diff record
prompt migration schema accepts valid migration record
prompt runtime binding schema accepts valid binding
prompt permission matrix schema accepts valid role mapping
prompt audit schema accepts valid audit event
prompt evidence manifest schema accepts valid evidence manifest
prompt review report schema accepts valid review report
prompt completion record schema accepts valid completion record
invalid enum values are rejected
missing required fields are rejected
```

Blocking if:

```text
schema-invalid prompts are accepted
schema-invalid prompt versions are accepted
registry cannot represent active/inactive versions
provenance cannot represent prompt ID, version, hash, runtime binding, and caller role
migration records cannot distinguish compatible and breaking changes
evidence manifest cannot be schema-validated
review report cannot be schema-validated
completion record cannot be schema-validated
schema validation exit code is missing
```

---

# 17. Prompt Registry Coverage

Required behavior:

```text
[ ] default prompt registry loads
[ ] prompt IDs are unique
[ ] prompt version IDs are unique
[ ] duplicate prompt IDs are rejected
[ ] duplicate active version bindings are rejected
[ ] registry snapshot is deterministic
[ ] registry records active version per prompt
[ ] inactive/deprecated versions remain inspectable
[ ] disabled prompts do not execute or bind at runtime
[ ] role permissions are attached to prompt definitions
[ ] model/task compatibility metadata is attached
[ ] tool-request permissions are attached
[ ] input and output contracts are attached
[ ] safety rules are attached
[ ] provenance rules are attached
[ ] registry snapshot hash is recorded
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
duplicate prompt IDs silently override previous prompts
multiple active versions exist without explicit selection rule
unknown prompt IDs are accepted
prompt registry loads with invalid schema
registry snapshot hash is missing
```

---

# 18. Prompt Versioning Coverage

Required behavior:

```text
[ ] every prompt has prompt_id
[ ] every prompt version has version_id
[ ] semantic version or controlled version scheme is enforced
[ ] active version is explicit
[ ] previous versions are preserved
[ ] version history is append-only
[ ] canonical prompt hash is recorded
[ ] prompt content changes produce new version or controlled migration
[ ] active version changes are evidenced
[ ] rollback metadata is recorded without automatic unsafe rollback
[ ] version aliases do not bypass exact version tracking
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
prompt text can change without version change
active version changes without evidence
prompt hash is missing
version history is overwritten instead of appended
```

---

# 19. Prompt Canonicalization, Hashing, and Active-Version Rules

Required behavior:

```text
[ ] canonicalization algorithm is defined and tested
[ ] canonical prompt text hash is recorded
[ ] rendered prompt hash is recorded when variables are bound
[ ] input variable schema hash is recorded
[ ] output contract hash is recorded
[ ] safety-rule set hash is recorded
[ ] prompt registry snapshot hash is recorded
[ ] active version change creates append-only evidence
[ ] aliases such as latest/current resolve to an exact version before runtime binding
[ ] alias resolution is recorded in provenance
[ ] prompt content cannot be edited in place after publication
[ ] deprecated prompt versions remain inspectable
```

Minimum canonicalization rule:

```text
The implementation must define one deterministic canonical representation before hashing.
It must specify how line endings, trailing spaces, key ordering, variable placeholders, and metadata fields are normalized.
The same logical prompt must produce the same canonical hash across repeated validation runs.
```

Blocking if:

```text
active prompt version is implicit
latest/current alias is used without resolving to an exact version
prompt content is edited in place
canonicalization is undefined
rendered prompt hash is missing when runtime variables are bound
safety-rule set changes without hash/evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 20. Prompt Compatibility Coverage

Required behavior:

```text
[ ] compatible prompt changes are classified
[ ] breaking prompt changes are classified
[ ] input contract changes are checked
[ ] output contract changes are checked
[ ] allowed tool-request changes are checked
[ ] safety-rule changes are checked
[ ] model/task compatibility changes are checked
[ ] role permission changes are checked
[ ] breaking changes require migration record or explicit approval
[ ] compatibility result is evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
breaking changes are accepted as compatible
output contract changes are ignored
safety-rule removals are treated as non-breaking
role permission expansion is accepted without evidence
```

---

# 21. Prompt Safety-Rule Coverage

Required behavior:

```text
[ ] prompt injection defense rules exist
[ ] tool-request boundaries exist
[ ] prompt may not request tools outside role permission
[ ] prompt may not request network if model/task policy forbids it
[ ] prompt may not request source mutation unless governance rules allow it
[ ] prompt output format rules are enforced
[ ] safety-critical prompts require explicit safety rules
[ ] missing safety rule blocks runtime binding for safety-critical prompts
[ ] unsafe prompt content patterns are detected or flagged
[ ] safety decisions are evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
prompt can request unauthorized tools
prompt can bypass role/tool policy
prompt injection defense is absent for tool-using prompts
safety-rule removal is not detected
missing safety rules default to ALLOW
```

---

# 22. Prompt Injection and Variable Redaction Review

Required behavior:

```text
[ ] user-controlled fields are identified before rendering
[ ] tool instructions are separated from user-provided content where supported
[ ] prompt variables are schema-validated before rendering
[ ] secret-like variables are redacted in evidence
[ ] prompt-injection markers in unsafe fields are blocked or flagged
[ ] prompts cannot instruct tools to ignore policy/sandbox/governance layers
[ ] prompts cannot instruct output consumers to ignore schema contracts
[ ] system/developer/role prompt boundaries are preserved where the runtime supports them
[ ] safety-rule evaluation runs before runtime binding
[ ] prompt safety decisions are evidenced
```

Blocking if:

```text
user-controlled content can override prompt safety rules
secret-like values are persisted unredacted
prompt asks to bypass policy, sandbox, governance, provenance, or audit and is allowed
prompt variables render without schema validation
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 23. Prompt Provenance Coverage

Required behavior:

```text
[ ] every runtime prompt binding records prompt_id
[ ] every runtime prompt binding records version_id
[ ] every runtime prompt binding records canonical_prompt_hash
[ ] every runtime prompt binding records rendered_prompt_hash when variables are bound
[ ] every runtime prompt binding records caller role
[ ] every runtime prompt binding records model/task profile
[ ] every runtime prompt binding records allowed tools
[ ] every runtime prompt binding records input contract
[ ] every runtime prompt binding records output contract
[ ] provenance records include timestamp and session ID where available
[ ] generated actions can be traced back to prompt version
[ ] provenance is append-only
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
runtime prompt use lacks prompt version
runtime prompt use lacks prompt hash
runtime variables are rendered without rendered_prompt_hash
prompt-generated actions cannot be traced to prompt version
provenance is overwritten or missing
```

---

# 24. Prompt Diff / Migration Coverage

Required behavior:

```text
[ ] prompt diffs are deterministic
[ ] prompt diff records old and new prompt versions
[ ] prompt diff records content hash changes
[ ] prompt diff records input/output contract changes
[ ] prompt diff records safety-rule changes
[ ] prompt diff records tool-permission changes
[ ] migration records classify compatible vs breaking changes
[ ] migration records list required downstream updates
[ ] migration records are evidenced
[ ] unsafe automatic migrations are blocked
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
prompt migration can change output format without evidence
prompt migration can remove safety rules without detection
prompt diff omits tool permission changes
breaking migrations are applied silently
```

---

# 25. Runtime Binding Coverage

Required behavior:

```text
[ ] prompt binding checks role permission
[ ] prompt binding checks model/task compatibility
[ ] prompt binding checks allowed tools
[ ] prompt binding checks input contract compatibility
[ ] prompt binding checks output contract compatibility
[ ] prompt binding checks safety rules
[ ] prompt binding records provenance
[ ] unknown prompt ID returns BLOCKED or INVALID
[ ] disabled prompt returns BLOCKED
[ ] deprecated prompt requires explicit compatibility approval
[ ] runtime binding cannot use unversioned prompt text
[ ] runtime binding records exact version after alias resolution
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
unversioned prompt can bind at runtime
role-incompatible prompt can bind
model/task-incompatible prompt can bind
prompt can bind without provenance
alias binding skips exact version resolution
```

---

# 26. Locking, Concurrency, and Idempotency Coverage

Required behavior:

```text
[ ] active-version updates are serialized or conflict-detected
[ ] registry snapshot writes are atomic
[ ] latest_prompt_binding.json writes are atomic
[ ] latest_prompt_provenance.json writes are atomic
[ ] repeated validation produces stable registry snapshot hash
[ ] repeated runtime binding with same inputs produces same canonical hashes
[ ] duplicate evidence is either append-only with unique IDs or explicitly idempotent
[ ] failed partial writes cannot leave corrupt latest artifacts
[ ] lock/conflict decisions are evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
parallel active-version changes can silently overwrite each other
registry snapshot can be partially written
latest artifacts can be corrupted by partial writes
repeated validation produces unstable hashes without explanation
```

---

# 27. Audit / Evidence Coverage

Required evidence behavior:

```text
[ ] prompt_registry_snapshot.json is written
[ ] prompt_version_history.jsonl is written
[ ] prompt_binding_history.jsonl is written
[ ] prompt_safety_decision_history.jsonl is written
[ ] prompt_provenance_history.jsonl is written
[ ] prompt_diff_history.jsonl is written
[ ] prompt_migration_history.jsonl is written
[ ] prompt_lock_history.jsonl is written when locking/conflicts occur
[ ] latest_prompt_binding.json is written atomically
[ ] latest_prompt_provenance.json is written atomically
[ ] prompt_contract_versioning_evidence_manifest.json is written
[ ] prompt_contract_versioning_review_report.json is written
[ ] completion record is written after validation
[ ] evidence includes reviewed commit
[ ] evidence includes timestamps
[ ] evidence includes command text, exit codes, statuses, and summaries
[ ] evidence includes schema validation summary
[ ] evidence includes hashes for final evidence artifacts
[ ] secrets and sensitive prompt variables are redacted before logging
[ ] raw prompt content is not durably logged where policy forbids it
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
prompt registry/version/binding/provenance evidence is missing
prompt safety decisions are not evidenced
secrets are logged
required hashes are missing
evidence lacks reviewed commit reference
```

---

# 28. Evidence Manifest

Create:

```text
.agentx-init/prompts/prompt_contract_versioning_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_evidence_manifest.schema.json",
  "component_id": "AGENTX_PROMPT_CONTRACT_VERSIONING",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>"
  },
  "commands": [],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "hash_algorithm": "sha256",
  "hash_canonicalization": "<canonicalization rule or implementation reference>",
  "self_hash_policy": "hash file with self-hash field omitted or set to null",
  "registry_snapshot_sha256": "<sha256>",
  "latest_prompt_binding_sha256": "<sha256 or NOT_USED>",
  "latest_prompt_provenance_sha256": "<sha256 or NOT_USED>",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "prompt_registry_status": "PASS",
  "prompt_versioning_status": "PASS",
  "prompt_safety_status": "PASS",
  "prompt_provenance_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
For files containing their own hash, compute the hash with the self-hash field omitted or set to null, and record that policy.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Approved runtime artifact boundary:

```text
.agentx-init/prompts/
```

Evidence artifacts for this layer must not be written outside that root unless the review records the exception in the deviation register.

The manifest must include paths and hashes for all final evidence files, including:

```text
prompt_contract_versioning_evidence_manifest.json
prompt_contract_versioning_review_report.json
prompt_contract_versioning_completion_record.json
prompt_registry_snapshot.json
latest_prompt_binding.json, if used by the review
latest_prompt_provenance.json, if used by the review
JSONL evidence histories used by the review
command output artifacts, if stored as files
```

---

# 29. Review Report Artifact

Create:

```text
.agentx-init/prompts/prompt_contract_versioning_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_review_report.schema.json",
  "component_id": "AGENTX_PROMPT_CONTRACT_VERSIONING",
  "review_document_id": "PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v3.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {},
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/prompts/prompt_contract_versioning_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/prompts/prompt_contract_versioning_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/prompts/prompt_contract_versioning_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is the bridge between this template and the implementation. A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, or if it lacks command exit codes.

---

# 30. Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
prompt source changes after sign-off require a new prompt version or migration record
```

---

# 31. Integration Coverage

## 31.1 Policy / Capability Registry Integration

```text
[ ] prompt use checks role permission before binding
[ ] prompt tool requests are checked against policy
[ ] policy-denied prompt use returns BLOCKED
[ ] missing policy fails closed for non-read-only or tool-using prompts
[ ] policy decisions are evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

## 31.2 Tool / MCP Adapter Integration

```text
[ ] prompts declare allowed tools
[ ] prompts cannot request unregistered tools
[ ] prompts cannot request blocked tools
[ ] MCP-exposed prompts are read-only or explicitly governed
[ ] tool-request violations return BLOCKED with evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

## 31.3 Model Adapter Integration

```text
[ ] prompts declare compatible model profiles
[ ] prompts declare compatible task types
[ ] hosted/local model mode is respected
[ ] model-incompatible prompt binding blocks
[ ] output contract is compatible with model/runtime requirements
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

## 31.4 Context Builder / Task Packer Integration

```text
[ ] prompt input contract matches packed context fields
[ ] missing required context fields block binding
[ ] extra context fields are handled deterministically
[ ] context provenance is linked to prompt provenance
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

## 31.5 LLM Implementation Worker Integration

```text
[ ] worker must use registered prompt contracts only
[ ] worker must record prompt version used
[ ] worker must obey output contract
[ ] worker cannot modify prompt text at runtime without versioning
[ ] worker-generated actions can be traced to prompt provenance
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

---

# 32. Conditional CLI Command Acceptance Criteria

This section applies only if prompt validation exposes CLI commands.

Required behavior if CLI commands exist:

```text
[ ] prompt validation CLI accepts explicit prompt contract paths
[ ] prompt validation CLI records command text, exit code, status, and summary
[ ] CLI does not mutate prompt source unless running an explicitly governed migration command
[ ] CLI rejects unknown command options that would bypass schema/safety validation
[ ] CLI writes evidence only under approved runtime artifact roots or records a deviation
[ ] CLI returns non-zero exit code for invalid prompt contracts
[ ] CLI does not require GPU, network, hosted model, LLM, Bun, Node, or OpenCode runtime
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
CLI mutates prompt source without migration evidence
CLI accepts invalid prompt contracts with exit_code 0
CLI bypasses schema or safety validation
CLI requires network/model runtime for static validation
```

---

# 33. Conditional MCP Protocol Acceptance Criteria

This section applies only if prompts are exposed through MCP.

Required behavior if prompts are exposed through MCP:

```text
[ ] MCP prompt manifest exposes only governed prompt contracts
[ ] MCP prompt request resolves to exact prompt_id and version_id
[ ] MCP prompt request cannot select unversioned prompt text
[ ] MCP prompt request cannot bypass role permission
[ ] MCP prompt request cannot request unauthorized tools
[ ] MCP prompt request records provenance
[ ] MCP prompt exposure is read-only unless explicitly governed
[ ] MCP runtime does not start automatically as part of prompt validation tests
[ ] MCP prompt exposure deferral is recorded if not implemented
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

Blocking if:

```text
MCP can expose unversioned prompt text
MCP can bypass prompt role permissions
MCP can bind prompt without provenance
MCP prompt exposure starts server or opens network port by default
```

---

# 34. Negative Test Pack

The review must prove forbidden behavior fails closed.

Required negative cases:

```text
[ ] unknown prompt ID -> INVALID or BLOCKED
[ ] disabled prompt -> BLOCKED
[ ] duplicate prompt ID -> registry invalid
[ ] duplicate active prompt version -> registry invalid
[ ] unversioned prompt binding -> BLOCKED
[ ] latest/current alias without exact resolution -> BLOCKED
[ ] prompt text changed without version change -> BLOCKED
[ ] missing prompt hash -> BLOCKED
[ ] missing rendered hash when variables are bound -> BLOCKED
[ ] role-incompatible prompt use -> BLOCKED
[ ] model/task-incompatible prompt use -> BLOCKED
[ ] prompt requests unauthorized tool -> BLOCKED
[ ] prompt requests source mutation without governance -> BLOCKED
[ ] prompt removes safety rule without migration -> BLOCKED
[ ] breaking output contract change without migration -> BLOCKED
[ ] prompt injection pattern in unsafe field -> BLOCKED or flagged with safety evidence
[ ] provenance missing for runtime binding -> BLOCKED
[ ] secret-like prompt variable -> redacted in evidence
[ ] parallel active-version update conflict -> BLOCKED or conflict evidence
[ ] registry snapshot partial write simulation -> no corrupt final artifact
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked as non-applicable with justification.

---

# 35. Test Fixture Isolation Requirement

Prompt tests must not mutate real prompt source files unless the test is explicitly a governed migration test running in a temporary fixture.

Required behavior:

```text
[ ] tests use temp prompt registries or fixture copies
[ ] tests do not edit production prompt files in place
[ ] migration tests write only to temporary paths or approved runtime artifacts
[ ] source mutation check is run before and after tests
[ ] prompt fixture hashes are deterministic
```

Blocking if:

```text
tests mutate real prompt source files
tests leave unapproved generated files outside .agentx-init/prompts/
test fixtures hide prompt drift by rewriting source files
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 36. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Schema | Runtime Binding | Evidence | MCP | CLI | Model Integration | Context Integration | Worker Integration | Runtime Artifact Boundary | Other>
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
Runtime artifact writes outside `.agentx-init/prompts/` require a deviation entry.
MCP prompt exposure deferral requires a deviation entry if MCP prompt exposure is part of the claimed scope.
Model/Context/Worker integration deferral requires a deviation entry if any runtime entry point exists.
Missing evidence hashes cannot be accepted as a deviation for DONE.
```

---

# 37. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
prompt registry:
prompt versioning:
prompt canonicalization / hashing:
prompt compatibility:
prompt safety rules:
prompt provenance:
prompt diff/migration:
runtime binding:
locking / concurrency:
idempotency:
audit/evidence:
evidence manifest:
review report:
evidence hashes:
integration:
CLI acceptance, if applicable:
MCP acceptance, if applicable:
negative tests:
test fixture isolation:
source mutation check:
completion record:
```

---

# 38. What Failed

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

# 39. Issue Severity Classification

## 39.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
unknown prompt binds at runtime
disabled prompt binds at runtime
unversioned prompt binds at runtime
latest/current alias binds without exact version resolution
prompt text changes without version change
active prompt version changes without evidence
prompt canonicalization is undefined
prompt hash is missing
rendered prompt hash is missing when variables are bound
role-incompatible prompt binds
model/task-incompatible prompt binds
prompt requests unauthorized tool
prompt bypasses safety rules
prompt provenance is missing
breaking migration is applied silently
parallel active-version changes silently overwrite each other
source mutation occurs directly in this layer
secrets are logged
evidence lacks reviewed commit
evidence hashes are missing
review report is missing
completion record is missing
required area remains NOT CHECKED
```

## 39.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
incomplete evidence references
partial prompt provenance coverage
partial prompt diff coverage
partial context/model integration mapping
MCP prompt exposure deferred without explicit deviation entry
runtime artifact boundary exception lacks justification
review environment not recorded
lock/conflict evidence incomplete
idempotency behavior incomplete
```

## 39.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled prompt definitions
MCP prompt exposure intentionally deferred with safe-deferral proof
model adapter integration intentionally deferred until Model Adapter exists
context builder integration intentionally deferred until Context Builder exists
LLM worker integration intentionally deferred until LLM Implementation Worker exists
additional future-layer tests exist outside scoped Prompt Contract / Versioning suite
```

---

# 40. Source Mutation Check

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
only expected runtime artifacts under .agentx-init/prompts/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by tests
prompt source files are modified without version/migration evidence
unapproved files are created outside runtime artifact paths
evidence artifacts are written outside `.agentx-init/prompts/` without recorded deviation
```

---

# 41. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Prompt package, schemas, tests, runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, and completion record. |
| Prompt registry coverage | 1.0 | Registry loads, rejects duplicates, snapshots deterministically, records active versions. |
| Prompt versioning, canonicalization, and compatibility | 1.0 | Prompt hashes, exact active versions, canonicalization, and breaking-change handling are enforced. |
| Prompt safety and runtime binding | 1.0 | Safety rules, role permissions, model/task compatibility, and tool-request boundaries are enforced. |
| Prompt provenance and diff/migration | 1.0 | Runtime prompt use is traceable; diffs/migrations are deterministic and evidenced. |
| Audit / evidence | 1.0 | JSONL histories, latest artifacts, evidence manifest, review report, hashes, redaction, completion record. |
| Integration, idempotency, locking, and source-mutation safety | 1.0 | Cross-layer boundaries are safe; idempotency/locking tested; git status clean. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for governed prompt execution
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
unknown or disabled prompt binds caps score at 4.0
unversioned prompt binds caps score at 4.0
implicit latest/current binding caps score at 4.0
prompt text changes without version change caps score at 4.0
missing canonicalization caps score at 7.0
prompt requests unauthorized tool caps score at 4.0
provenance missing caps score at 6.0
secrets logged caps score at 4.0
source mutation by tests caps score at 7.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
```

---

# 42. GO / NO-GO Rules

## 42.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
prompt registry tests pass
prompt versioning tests pass
prompt canonicalization/hash tests pass
prompt compatibility tests pass
prompt safety-rule tests pass
prompt provenance tests pass
prompt diff/migration tests pass
runtime binding tests pass
locking/idempotency tests pass
audit/evidence tests pass
evidence manifest exists
evidence hashes exist
review report exists
negative tests pass
test fixture isolation passes
source mutation check passes
completion record exists
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 42.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
unknown prompt binds at runtime
disabled prompt binds at runtime
unversioned prompt binds at runtime
latest/current alias binds without exact version resolution
prompt text changes without version change
active version changes without evidence
prompt canonicalization is undefined
prompt hash is missing
rendered prompt hash is missing when variables are bound
role-incompatible prompt binds
model/task-incompatible prompt binds
prompt requests unauthorized tool
prompt bypasses safety rules
prompt provenance is missing
breaking migration is applied silently
parallel active-version changes silently overwrite each other
secrets are logged
source mutation occurs directly in this layer
prompt evidence is missing
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 43. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix prompt registry entries
fix prompt version metadata
fix active-version resolution
fix canonicalization / hashing
fix compatibility classification
fix safety-rule checks
fix runtime binding checks
fix provenance writing
fix diff/migration evidence
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix secret redaction
fix command acceptance criteria
fix MCP prompt filtering
fix tests to reflect the contract
```

Forbidden fixes:

```text
do not remove prompt versioning to pass tests
do not remove prompt hashes to pass tests
do not allow implicit latest/current binding
do not remove safety-rule checks
do not allow unauthorized tool requests
do not skip provenance writing
do not skip evidence writing
do not omit hashes for final DONE
do not log secrets
do not let tests mutate real prompt source files
do not require LLM/model runtime for static prompt validation
do not require network for static prompt validation
do not copy OpenCode source code
do not add Bun/Node/OpenCode runtime dependency
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
```

---

# 44. Definition of Done

The Prompt Contract / Prompt Versioning Layer is done when it can act as the governed prompt identity, versioning, safety, and provenance layer for Agent_X.

It must prove:

```text
all target files exist or explicit safe deferral is documented
all schemas exist
all tests exist
prompt registry loads
prompt IDs are unique
duplicate prompt IDs are rejected
active prompt versions are explicit
latest/current aliases resolve to exact versions before runtime binding
prompt content changes require new version or governed migration
canonical prompt hashes are recorded
rendered prompt hashes are recorded when variables are bound
input contracts are checked
output contracts are checked
safety rules are enforced
role permissions are enforced
model/task compatibility is enforced
allowed tool boundaries are enforced
runtime prompt binding records provenance
prompt diff/migration records are deterministic and evidenced
registry writes and active-version changes are conflict-safe or locked
repeated validation and binding are idempotent
prompt registry/version/binding/provenance evidence is written
evidence manifest is written
review report is written
evidence hashes are written
review environment is recorded
no source mutation occurs directly in this layer
secrets are redacted
completion record exists
final verdict is recorded
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_prompt_schemas.py
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

# 45. Required Evidence Package

The completion evidence package must include:

```text
compileall output
pytest output
schema validation result
prompt registry test result
prompt versioning test result
prompt canonicalization/hash test result
prompt compatibility test result
prompt safety-rule test result
prompt provenance test result
prompt diff/migration test result
runtime binding test result
locking/idempotency test result
negative-test result
test fixture isolation result
audit/evidence test result
evidence manifest
review report
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
no source mutation
no unversioned prompt binding
no implicit latest/current runtime binding
no prompt drift
no unauthorized tool request
no missing provenance
secrets redacted
hashes for final evidence artifacts
```

---

# 46. Completion Evidence Record

After validation, create:

```text
.agentx-init/prompts/prompt_contract_versioning_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_completion_record.schema.json",
  "component_id": "AGENTX_PROMPT_CONTRACT_VERSIONING",
  "component_name": "Prompt Contract / Prompt Versioning Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {},
  "canonical_prompt_subdirectory": "tools/agentx_evolve/prompts/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/prompts/",
  "basis_documents": [
    "PROMPT_CONTRACT_VERSIONING_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_SPEC",
    "PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_REVIEW_AND_DOD_v3"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "prompt_registry_entries_verified": [],
  "prompt_versions_verified": [],
  "prompt_hashes_verified": [],
  "prompt_compatibility_verified": [],
  "prompt_safety_rules_verified": [],
  "prompt_provenance_verified": [],
  "prompt_diff_migration_verified": [],
  "runtime_bindings_verified": [],
  "locking_idempotency_verified": [],
  "policy_integration_verified": [],
  "tool_mcp_integration_verified": [],
  "model_integration_verified": [],
  "context_builder_integration_verified": [],
  "worker_integration_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/prompts/prompt_contract_versioning_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/prompts/prompt_contract_versioning_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
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
evidence hashes are missing
review report is missing
completion record is missing
```

---

# 48. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/prompts/ exists
[ ] schemas exist
[ ] tests exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Prompt Registry:
[ ] default prompt registry loads
[ ] prompt IDs unique
[ ] duplicate prompts rejected
[ ] active versions explicit
[ ] inactive/deprecated versions inspectable
[ ] registry snapshot hash recorded

Prompt Versioning / Hashing:
[ ] version IDs unique
[ ] canonicalization defined
[ ] canonical prompt hashes recorded
[ ] rendered prompt hashes recorded when variables are bound
[ ] prompt text changes require new version or migration
[ ] version history append-only

Compatibility:
[ ] compatible changes classified
[ ] breaking changes classified
[ ] input/output contract changes checked
[ ] safety-rule changes checked
[ ] tool-permission changes checked

Safety:
[ ] injection defenses present where required
[ ] role permissions enforced
[ ] model/task compatibility enforced
[ ] unauthorized tool requests blocked
[ ] missing safety rules block safety-critical prompt binding
[ ] prompt variables schema-validated before rendering
[ ] secret-like variables redacted

Provenance:
[ ] runtime binding records prompt_id
[ ] runtime binding records version_id
[ ] runtime binding records prompt_hash
[ ] runtime binding records rendered_prompt_hash where applicable
[ ] runtime binding records caller role
[ ] runtime binding records model/task profile
[ ] generated actions trace to prompt version

Diff / Migration:
[ ] prompt diffs deterministic
[ ] migrations evidenced
[ ] breaking migrations require approval or explicit migration record
[ ] unsafe automatic migrations blocked

Locking / Idempotency:
[ ] active-version changes are conflict-safe
[ ] registry/latest writes are atomic
[ ] repeated validation produces stable hashes
[ ] repeated binding produces stable provenance for same inputs

Evidence:
[ ] prompt registry snapshot written
[ ] prompt version history written
[ ] prompt binding history written
[ ] prompt provenance history written
[ ] prompt safety decision history written
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written
[ ] self-hash policy recorded
[ ] secrets redacted

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
Prompt Contract / Versioning Validation — Commit <hash>

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
- scoped prompt pytest: PASS/FAIL/N/A, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- prompt registry coverage: PASS/FAIL
- prompt versioning coverage: PASS/FAIL
- prompt canonicalization/hash coverage: PASS/FAIL
- prompt compatibility coverage: PASS/FAIL
- prompt safety-rule coverage: PASS/FAIL
- prompt provenance coverage: PASS/FAIL
- prompt diff/migration coverage: PASS/FAIL
- runtime binding coverage: PASS/FAIL
- locking/idempotency coverage: PASS/FAIL
- CLI acceptance: PASS/FAIL/N/A
- MCP acceptance: PASS/FAIL/N/A/DEFERRED SAFELY
- negative-test coverage: PASS/FAIL
- fixture isolation: PASS/FAIL
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
- self-hash policy recorded: YES/NO
- prompt canonicalization rule recorded: YES/NO
- deviations recorded: YES/NO/N/A

Final decision:
DONE / NOT DONE

Implementation rating:
<0-10>

Evidence paths:
- evidence manifest: <path>, sha256=<hash>
- review report: <path>, sha256=<hash>
- completion record: <path>, sha256=<hash>
- registry snapshot: <path>, sha256=<hash>

Remaining blockers:
- none / list blockers

Accepted non-blocking follow-ups:
- none / list follow-ups
```

---

# 50. Final Freeze Rule

This v3 document is frozen as the post-implementation review / DoD template for the Prompt Contract / Prompt Versioning Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details that do not change safety semantics
MAJOR: changed prompt versioning policy, changed active-version rules, changed prompt safety behavior, new required schema category, new required runtime exposure path, new required integration gate
```

Blocked without major revision:

```text
allowing unversioned prompt binding
allowing latest/current aliases without exact version resolution
removing prompt canonicalization or hash requirements
removing prompt provenance requirements
removing safety-rule enforcement
allowing prompt text mutation without versioning or migration
allowing unauthorized tool requests
removing evidence logging
omitting reviewed commit from evidence
omitting SHA-256 evidence hashes for DONE
marking NOT CHECKED areas as PASS
accepting BLOCKER items as deviations
```

This freeze rule prevents repeated broad expansion after the document is accepted.

---

# 51. Final Rating

This v3 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the strong v2 coverage and fixes the remaining precision gaps: normal numeric sectioning, stricter review-validity rules, scoped prompt pytest command, prompt canonicalization and self-hash policy, registry locking/concurrency rules, idempotency checks, fixture isolation, clearer deferral semantics for model/context/worker/CLI/MCP integrations, strict runtime artifact boundary handling, stronger GO/NO-GO rules, and a reproducible final sign-off template.
```
