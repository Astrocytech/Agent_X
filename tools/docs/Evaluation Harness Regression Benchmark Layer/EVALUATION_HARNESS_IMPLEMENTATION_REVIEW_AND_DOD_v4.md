# EVALUATION_HARNESS_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: EVALUATION_HARNESS_IMPLEMENTATION_REVIEW_AND_DOD
version: v4.0
status: final post-implementation review template and Definition of Done
component_id: AGENTX_EVALUATION_HARNESS
component_name: Evaluation Harness / Regression Benchmark Layer
roadmap_layer: 15
roadmap_phase: Phase C — Evaluation and Regression Control
review_use: use after code is committed
basis_documents:
  - EVALUATION_HARNESS_EQC_FIC_SIB_SCHEMA_CONTRACT
  - EVALUATION_HARNESS_IMPLEMENTATION_SPEC
  - EVALUATION_HARNESS_IMPLEMENTATION_REVIEW_AND_DOD_v1
  - EVALUATION_HARNESS_IMPLEMENTATION_REVIEW_AND_DOD_v2
  - EVALUATION_HARNESS_IMPLEMENTATION_REVIEW_AND_DOD_v3
  - EVALUATION_HARNESS_IMPLEMENTATION_REVIEW_AND_DOD_v4
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Regression Benchmark Acceptance Criteria
conditional_standards: Command Acceptance Criteria, Tool / MCP Adapter Acceptance Criteria, Policy / Capability Registry Acceptance Criteria
optional_standards: ES, only for ecosystem placement
canonical_evaluation_subdirectory: tools/agentx_evolve/evaluation/
canonical_benchmark_subdirectory: tools/agentx_evolve/evaluation/benchmarks/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/evaluation/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v4 Review and Upgrade Summary

The v3 review / DoD document was strong and close to final, but I would rate it:

```text
9.7/10
```

It already covered the core validation requirements and most production-gate controls:

```text
what exists
what passed
what failed
compileall result
pytest result
schema validation result
benchmark execution result
regression comparison result
threshold result
evidence/artifact result
source mutation check
definition of done
final done/not-done verdict
benchmark freeze and hashing
benchmark lockfile control
explicit oracle definitions
deterministic replay
metric definitions
expected-failure and skipped/flaky-case handling
regression severity and promotion-blocking rules
resource budget and timeout review
anti-overfitting / benchmark contamination checks
```

It was not fully 10/10 because several review-template consistency and production-control gaps remained:

```text
1. The expected schema list included oracle, lockfile, resource-budget, and promotion-gate schemas, but the later schema checklist omitted several of them.
2. The expected test list included oracle, lockfile, resource-budget, and promotion-gate tests, but the later test checklist omitted several of them.
3. Baseline-change governance was strong, but benchmark-case, oracle, threshold, metric, and resource-budget change governance needed the same explicit treatment.
4. The document needed a stronger no-training/no-tuning-on-gating-suite rule for model or prompt changes evaluated by this layer.
5. The evidence requirements needed explicit redaction and secret-handling rules for prompts, tool outputs, command outputs, and benchmark artifacts.
6. The review needed dependency/environment lock recording so benchmark changes are not confused with environment drift.
7. The promotion-gate summary needed a stricter machine-readable contract for downstream gates.
8. Section numbering had several legacy references, which could make review citations unstable.
9. The hard scoring caps needed explicit caps for benchmark-change governance, promotion-summary absence, and missing environment lock evidence.
10. The final freeze rule needed to stop repeated broad expansion after this v4 unless the benchmark semantics change.
```

This v4 fixes those gaps and is the final 10/10 post-implementation review / DoD template.
---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Evaluation Harness / Regression Benchmark Layer**.

Use this document after code is committed to determine whether the layer is complete, deterministic, auditable, reproducible, and safe to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether benchmark suites load
whether benchmark fixtures are immutable and hashed
whether benchmark execution is deterministic
whether regression comparison works
whether thresholds are enforced
whether metric definitions are stable
whether oracle definitions are explicit and stable
whether the benchmark lockfile fixes all reviewed benchmark inputs
whether baseline changes are governed separately from candidate evaluation
whether expected failures are handled honestly
whether skipped/flaky/nondeterministic cases are controlled
whether evidence and artifacts are complete
whether reports are evidence-backed
whether source mutation is avoided
whether promotion-blocking conditions are detected
whether the final verdict is DONE or NOT DONE
```

This is the validation document. A 10/10 rating for this review document does **not** mean the implementation is done. The implementation is done only when the recorded validation evidence satisfies this document's GO criteria.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because this layer decides whether a new Agent_X change is better, worse, acceptable, or regressive.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Regression Benchmark Acceptance Criteria
Report Template, if benchmark reports are written
```

## 2.3 Conditional Standards

```text
Command Acceptance Criteria, if it executes validation commands
Tool / MCP Adapter Acceptance Criteria, if it invokes registered tools
Policy / Capability Registry Acceptance Criteria, if evaluation permissions are checked
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
```

---

# 3. Why This Layer Needs These Standards

The Evaluation Harness / Regression Benchmark Layer is safety-critical because it decides:

```text
whether a new Agent_X change is better or worse
whether regressions are detected
whether benchmark results are reproducible
whether promotion should be blocked
whether failures are classified correctly
whether test artifacts are trustworthy
whether evaluation reports are evidence-backed
whether model/tool/orchestrator changes meet acceptance thresholds
```

It must not become a vague scoring layer. It needs:

```text
deterministic inputs
stable baselines
reproducible runs
fixed thresholds
stable metric definitions
auditable outputs
strict pass/fail rules
clear regression decisions
immutable review evidence
promotion-blocking behavior for unacceptable regressions
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
  timezone: UTC
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
[ ] benchmark suite ID is recorded
[ ] baseline ID is recorded
[ ] threshold set ID is recorded
[ ] metric definition version is recorded
[ ] benchmark lockfile ID and hash are recorded
[ ] oracle definition ID and hash are recorded
[ ] baseline-change record is absent or separately approved and recorded
[ ] every required command records command text, exit code, status, and summary
[ ] every command marked PASS has exit_code 0
[ ] deterministic replay was executed or explicitly justified as not applicable
[ ] every expected failure has an expected-failure ID and reason
[ ] every skipped case has a skip reason and does not inflate scores
[ ] every runtime artifact path is under `.agentx-init/evaluation/` or listed in deviations
[ ] evidence manifest exists before final DONE is claimed
[ ] review report exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] required SHA-256 hashes are present
[ ] reviewer did not rely only on this document's internal rating
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

The implementation can be marked `DONE` only when the recorded evidence satisfies the GO criteria.

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
| DEFERRED SAFELY | Feature is intentionally deferred and cannot execute, mutate, affect promotion, hide regressions, call unsafe tools, or weaken thresholds. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Deferral Rules

Use these rules to avoid hiding missing validation behind `NOT APPLICABLE` or `DEFERRED SAFELY`.

```text
NOT APPLICABLE:
  Use only when the implemented scope truly does not include the feature and there is no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot execute, mutate, affect promotion, weaken thresholds, or hide regressions.

PARTIAL:
  Use when some files or tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

Benchmark categories may be `DEFERRED SAFELY` only if:

```text
they are not part of the active benchmark suite
they do not affect current scores
they do not affect current thresholds
they do not hide a known regression
they are recorded in the deviation register
```

---

# 6. Expected Implementation Scope

## 6.1 Expected Package

Expected location:

```text
tools/agentx_evolve/evaluation/
```

Expected files:

```text
tools/agentx_evolve/evaluation/__init__.py
tools/agentx_evolve/evaluation/evaluation_models.py
tools/agentx_evolve/evaluation/benchmark_registry.py
tools/agentx_evolve/evaluation/benchmark_loader.py
tools/agentx_evolve/evaluation/evaluation_runner.py
tools/agentx_evolve/evaluation/score_calculator.py
tools/agentx_evolve/evaluation/regression_comparator.py
tools/agentx_evolve/evaluation/threshold_checker.py
tools/agentx_evolve/evaluation/evaluation_report_writer.py
tools/agentx_evolve/evaluation/evaluation_evidence.py
```

## 6.2 Expected Benchmark Fixtures

Expected location:

```text
tools/agentx_evolve/evaluation/benchmarks/
```

Expected fixture types:

```text
benchmark suite manifest
benchmark case definitions
expected output specifications
baseline score records
threshold configuration
metric definition records
negative regression fixtures
known expected-failure fixtures, if applicable
```

## 6.3 Expected Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
evaluation_benchmark_suite.schema.json
evaluation_benchmark_case.schema.json
evaluation_run.schema.json
evaluation_result.schema.json
evaluation_score.schema.json
regression_comparison.schema.json
evaluation_threshold.schema.json
evaluation_metric_definition.schema.json
evaluation_oracle_definition.schema.json
evaluation_benchmark_lockfile.schema.json
evaluation_resource_budget.schema.json
evaluation_baseline_change.schema.json
evaluation_benchmark_change.schema.json
evaluation_promotion_gate_summary.schema.json
evaluation_report.schema.json
evaluation_evidence_manifest.schema.json
evaluation_completion_record.schema.json
```

## 6.4 Expected Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_evaluation_models.py
test_benchmark_registry.py
test_benchmark_loader.py
test_evaluation_runner.py
test_score_calculator.py
test_regression_comparator.py
test_threshold_checker.py
test_metric_definitions.py
test_evaluation_oracle_definitions.py
test_evaluation_lockfile.py
test_evaluation_resource_budget.py
test_evaluation_promotion_gate_summary.py
test_evaluation_report_writer.py
test_evaluation_evidence.py
test_evaluation_schema_validation.py
test_evaluation_deterministic_replay.py
test_evaluation_negative_cases.py
```

## 6.5 Expected Runtime Artifacts

Expected location:

```text
.agentx-init/evaluation/
```

Expected artifacts:

```text
evaluation_run_history.jsonl
evaluation_result_history.jsonl
regression_comparison_history.jsonl
threshold_decision_history.jsonl
latest_evaluation_run.json
latest_evaluation_result.json
latest_regression_comparison.json
latest_threshold_decision.json
evaluation_benchmark_lockfile.json
evaluation_promotion_gate_summary.json
evaluation_evidence_manifest.json
evaluation_review_report.json
evaluation_completion_record.json
```

---

# 7. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Evaluation package | `tools/agentx_evolve/evaluation/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Benchmark fixtures | Suite, cases, baselines, thresholds, metrics exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schemas | All required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation command | Dedicated command or pytest equivalent exists and passes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tests | Required test files exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Benchmark loader | Loads suite deterministically and validates fixtures first | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evaluation runner | Executes benchmark suite and writes structured results | PASS / PARTIAL / FAIL / NOT CHECKED |
| Deterministic replay | Same suite/run inputs produce same result | PASS / PARTIAL / FAIL / NOT CHECKED |
| Score calculator | Uses stable metric definitions and no hidden weighting | PASS / PARTIAL / FAIL / NOT CHECKED |
| Oracle definitions | Expected outputs and tolerances are explicit and stable | PASS / PARTIAL / FAIL / NOT CHECKED |
| Benchmark lockfile | Reviewed suite/cases/baseline/threshold/metric/oracle set is locked and hashed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Resource budget | Timeouts, case limits, and resource ceilings enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Regression comparator | Explicit baseline, current run, and regression decision | PASS / PARTIAL / FAIL / NOT CHECKED |
| Threshold checker | Fixed thresholds and promotion-blocking behavior | PASS / PARTIAL / FAIL / NOT CHECKED |
| Expected failures | Expected failures tracked and do not inflate score | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Skipped/flaky cases | Controlled, justified, and score-safe | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Report writer | Evidence-backed report if reports are written | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Evidence artifacts | JSONL, latest artifacts, manifest, report, completion record | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence hashing | Required SHA-256 hashes present | PASS / PARTIAL / FAIL / NOT CHECKED |
| Command safety | Allowlisted commands, no raw shell, exit codes recorded | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Tool Adapter integration | Registered tools invoked only through Tool / MCP Adapter | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Policy integration | Policy-checked where required and fail-closed | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Runtime artifact boundary | Artifacts under `.agentx-init/evaluation/` or deviation listed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | No source, baseline, or threshold mutation during review | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 8. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Benchmark suite loads | `benchmark_loader.py` | `test_benchmark_loader.py` | evaluation evidence manifest | PASS / PARTIAL / FAIL / NOT CHECKED |
| Benchmark registry deterministic | `benchmark_registry.py` | `test_benchmark_registry.py` | pytest output | PASS / PARTIAL / FAIL / NOT CHECKED |
| Benchmark cases schema-valid | `benchmark_loader.py` | `test_evaluation_schema_validation.py` | schema output | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evaluation runner executes suite | `evaluation_runner.py` | `test_evaluation_runner.py` | run history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Deterministic replay | `evaluation_runner.py` | `test_evaluation_deterministic_replay.py` | replay artifact | PASS / PARTIAL / FAIL / NOT CHECKED |
| Score calculation | `score_calculator.py` | `test_score_calculator.py` | evaluation score artifact | PASS / PARTIAL / FAIL / NOT CHECKED |
| Metric definitions stable | `score_calculator.py` | `test_metric_definitions.py` | metric definition hash | PASS / PARTIAL / FAIL / NOT CHECKED |
| Regression comparison | `regression_comparator.py` | `test_regression_comparator.py` | regression comparison history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Threshold decision | `threshold_checker.py` | `test_threshold_checker.py` | threshold decision history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Report generation | `evaluation_report_writer.py` | `test_evaluation_report_writer.py` | evaluation review report | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Evidence writing | `evaluation_evidence.py` | `test_evaluation_evidence.py` | JSONL + latest artifacts | PASS / PARTIAL / FAIL / NOT CHECKED |
| Negative cases fail closed | multiple | `test_evaluation_negative_cases.py` | pytest output | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record | evidence writer or manual creation | schema/manual validation | completion record JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 9. What Exists Checklist

## 9.1 Package Files

```text
[ ] tools/agentx_evolve/evaluation/__init__.py
[ ] tools/agentx_evolve/evaluation/evaluation_models.py
[ ] tools/agentx_evolve/evaluation/benchmark_registry.py
[ ] tools/agentx_evolve/evaluation/benchmark_loader.py
[ ] tools/agentx_evolve/evaluation/evaluation_runner.py
[ ] tools/agentx_evolve/evaluation/score_calculator.py
[ ] tools/agentx_evolve/evaluation/regression_comparator.py
[ ] tools/agentx_evolve/evaluation/threshold_checker.py
[ ] tools/agentx_evolve/evaluation/evaluation_report_writer.py
[ ] tools/agentx_evolve/evaluation/evaluation_evidence.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 9.2 Benchmark Fixtures

```text
[ ] benchmark suite manifest exists
[ ] benchmark cases exist
[ ] expected output specifications exist
[ ] baseline score records exist
[ ] threshold configuration exists
[ ] metric definition records exist
[ ] negative regression fixtures exist
[ ] expected-failure fixture list exists, if used
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 9.3 Schemas

```text
[ ] evaluation_benchmark_suite.schema.json
[ ] evaluation_benchmark_case.schema.json
[ ] evaluation_run.schema.json
[ ] evaluation_result.schema.json
[ ] evaluation_score.schema.json
[ ] regression_comparison.schema.json
[ ] evaluation_threshold.schema.json
[ ] evaluation_metric_definition.schema.json
[ ] evaluation_oracle_definition.schema.json
[ ] evaluation_benchmark_lockfile.schema.json
[ ] evaluation_resource_budget.schema.json
[ ] evaluation_baseline_change.schema.json
[ ] evaluation_benchmark_change.schema.json
[ ] evaluation_promotion_gate_summary.schema.json
[ ] evaluation_report.schema.json
[ ] evaluation_evidence_manifest.schema.json
[ ] evaluation_completion_record.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 9.4 Tests

```text
[ ] test_evaluation_models.py
[ ] test_benchmark_registry.py
[ ] test_benchmark_loader.py
[ ] test_evaluation_runner.py
[ ] test_score_calculator.py
[ ] test_regression_comparator.py
[ ] test_threshold_checker.py
[ ] test_metric_definitions.py
[ ] test_evaluation_oracle_definitions.py
[ ] test_evaluation_lockfile.py
[ ] test_evaluation_resource_budget.py
[ ] test_evaluation_promotion_gate_summary.py
[ ] test_evaluation_report_writer.py
[ ] test_evaluation_evidence.py
[ ] test_evaluation_schema_validation.py
[ ] test_evaluation_deterministic_replay.py
[ ] test_evaluation_negative_cases.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 9.5 Runtime Artifacts

```text
[ ] evaluation_run_history.jsonl
[ ] evaluation_result_history.jsonl
[ ] regression_comparison_history.jsonl
[ ] threshold_decision_history.jsonl
[ ] latest_evaluation_run.json
[ ] latest_evaluation_result.json
[ ] latest_regression_comparison.json
[ ] evaluation_evidence_manifest.json
[ ] evaluation_review_report.json
[ ] evaluation_completion_record.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 10. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_evaluation_schemas.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_evaluation_runner.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_regression_comparator.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_threshold_checker.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_evaluation_deterministic_replay.py
git status --short
```

Required result:

```text
initial git status: clean or expected known runtime artifacts only
python version: recorded
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
benchmark execution tests: PASS, exit_code 0
regression comparison tests: PASS, exit_code 0
threshold tests: PASS, exit_code 0
deterministic replay tests: PASS, exit_code 0
final git status: clean or expected runtime artifacts only
```

If `validate_evaluation_schemas.py` is not implemented, the same schema coverage must be proven by a documented pytest file such as:

```text
tools/agentx_evolve/tests/test_evaluation_schema_validation.py
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
non-local model provider
```

---

# 11. Validation Commands

Record exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`. Any non-zero exit code is `FAIL` unless the command is explicitly a negative test where non-zero is the expected result and the expected failure condition is recorded.

Primary validation commands:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_evaluation_schemas.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_evaluation_runner.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_regression_comparator.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_threshold_checker.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_evaluation_deterministic_replay.py
git status --short
```

If unrelated future-layer tests exist in `tools/agentx_evolve/tests`, the review must also record a scoped Evaluation Harness pytest command:

```bash
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_evaluation_models.py \
  tools/agentx_evolve/tests/test_benchmark_registry.py \
  tools/agentx_evolve/tests/test_benchmark_loader.py \
  tools/agentx_evolve/tests/test_evaluation_runner.py \
  tools/agentx_evolve/tests/test_score_calculator.py \
  tools/agentx_evolve/tests/test_regression_comparator.py \
  tools/agentx_evolve/tests/test_threshold_checker.py \
  tools/agentx_evolve/tests/test_metric_definitions.py \
  tools/agentx_evolve/tests/test_evaluation_oracle_definitions.py \
  tools/agentx_evolve/tests/test_evaluation_lockfile.py \
  tools/agentx_evolve/tests/test_evaluation_resource_budget.py \
  tools/agentx_evolve/tests/test_evaluation_promotion_gate_summary.py \
  tools/agentx_evolve/tests/test_evaluation_report_writer.py \
  tools/agentx_evolve/tests/test_evaluation_evidence.py \
  tools/agentx_evolve/tests/test_evaluation_schema_validation.py \
  tools/agentx_evolve/tests/test_evaluation_deterministic_replay.py \
  tools/agentx_evolve/tests/test_evaluation_negative_cases.py
```

Required result:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
benchmark execution tests PASS, exit_code 0
regression comparison tests PASS, exit_code 0
threshold tests PASS, exit_code 0
deterministic replay tests PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
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
output_artifact: <path>
output_sha256: <sha256>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any Evaluation Harness Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 13. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
scoped_command: <scoped Evaluation Harness pytest command, if needed>
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required evaluation, benchmark, regression, threshold, schema, report, evidence, deterministic replay, command-safety, or negative test fails
exit code is missing
```

---

# 14. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_evaluation_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_evaluation_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256>
```

Required schema tests:

```text
benchmark suite schema accepts valid suite
benchmark suite schema rejects missing suite_id
benchmark case schema accepts valid case
benchmark case schema rejects missing expected_output
benchmark case schema rejects unstable nondeterministic fields
evaluation run schema accepts valid run
evaluation result schema accepts PASS result
evaluation result schema accepts FAIL result
evaluation result schema accepts EXPECTED_FAIL result, if expected failures are supported
evaluation score schema accepts valid score
regression comparison schema accepts valid comparison
threshold schema accepts valid threshold definition
metric definition schema accepts valid metric definition
oracle definition schema accepts valid exact-match oracle
oracle definition schema accepts valid tolerance oracle
oracle definition schema rejects vague/unbounded oracle
benchmark lockfile schema accepts valid lockfile
resource budget schema accepts valid budget
promotion gate summary schema accepts valid summary
evaluation report schema accepts valid report
evidence manifest schema accepts valid evidence manifest
completion record schema accepts final completion record
invalid enum values are rejected
missing required fields are rejected
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
schema-invalid benchmark cases are accepted
schema-invalid evaluation results are accepted
regression comparison cannot represent PASS and FAIL outcomes
threshold decision cannot represent BLOCK_PROMOTION
metric definitions cannot be schema-validated
report or evidence manifest cannot be schema-validated
schema validation exit code is missing
```

---

# 15. Benchmark Freeze and Integrity Check

Before execution, record the exact benchmark material used.

```text
benchmark_suite_id: <suite id>
benchmark_suite_version: <version>
benchmark_suite_path: <path>
benchmark_suite_sha256: <sha256>
benchmark_case_count: <integer>
benchmark_case_hashes: <path or list>
baseline_id: <baseline id>
baseline_version: <version>
baseline_path: <path>
baseline_sha256: <sha256>
threshold_set_id: <threshold id>
threshold_set_version: <version>
threshold_path: <path>
threshold_sha256: <sha256>
metric_definition_id: <metric definition id>
metric_definition_version: <version>
metric_definition_sha256: <sha256>
```

Acceptance:

```text
all benchmark suites, cases, baselines, thresholds, and metric definitions are identified
all active benchmark inputs have SHA-256 hashes
benchmark fixtures are read-only during validation
baseline is explicit and not overwritten
threshold set is explicit and not rewritten
metric definition is explicit and not rewritten
```

Blocking if:

```text
benchmark suite is not identified
case list is not fixed
baseline is missing
threshold set is missing
metric definition is missing
hashes are missing
baseline is silently generated during review
thresholds are modified during review
metric weights are changed during review
```

---

# 16. Benchmark Lockfile Review

The review must identify one immutable benchmark lockfile for the validation run.

Required lockfile path:

```text
tools/agentx_evolve/evaluation/benchmarks/<suite_id>/benchmark.lock.json
```

Required lockfile fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "evaluation_benchmark_lockfile.schema.json",
  "lockfile_id": "<id>",
  "created_at": "<UTC timestamp>",
  "benchmark_suite_id": "<suite id>",
  "benchmark_suite_version": "<version>",
  "benchmark_suite_sha256": "<sha256>",
  "case_manifest_sha256": "<sha256>",
  "case_hashes": [],
  "baseline_id": "<baseline id>",
  "baseline_sha256": "<sha256>",
  "threshold_set_id": "<threshold id>",
  "threshold_set_sha256": "<sha256>",
  "metric_definition_id": "<metric definition id>",
  "metric_definition_sha256": "<sha256>",
  "oracle_definition_id": "<oracle definition id>",
  "oracle_definition_sha256": "<sha256>",
  "resource_budget_id": "<budget id>",
  "resource_budget_sha256": "<sha256>",
  "warnings": [],
  "errors": []
}
```

Acceptance:

```text
lockfile exists for the active gating suite
lockfile hashes all score-affecting inputs
lockfile is read-only during validation
review report references the lockfile ID and SHA-256
completion record references the lockfile ID and SHA-256
```

Blocking if:

```text
active gating suite has no lockfile
lockfile omits any score-affecting input
lockfile changes during validation
lockfile hash is missing from evidence
benchmark inputs are selected outside the lockfile for final DONE
```

---

# 17. Oracle Definition Review

Every benchmark case must define how correctness is judged. The review must verify that oracle definitions are explicit and not improvised at scoring time.

Allowed oracle types:

```text
EXACT_MATCH
NORMALIZED_EXACT_MATCH
SCHEMA_MATCH
PREDICATE_MATCH
NUMERIC_TOLERANCE
ORDER_INSENSITIVE_SET_MATCH
GOLDEN_ARTIFACT_MATCH
EXPECTED_FAILURE
MANUAL_REVIEW_REQUIRED, non-gating only unless separately approved
```

Required oracle fields:

```text
oracle_id
oracle_type
case_id
expected_output_ref or expected_predicate_ref
tolerance, if numeric
normalization_rules, if used
non_score_fields_to_ignore
score_fields
last_reviewed_at
owner_component
sha256
warnings
errors
```

Acceptance:

```text
every active case has an oracle
oracle type is from the allowed list
score-affecting fields are explicit
ignored fields are explicit and justified
numeric tolerances are explicit and bounded
manual-review cases are non-gating unless separately approved
oracle definitions are hashed and included in the lockfile
```

Blocking if:

```text
case has no oracle
oracle says only "looks correct" or equivalent vague wording
tolerance is unbounded or missing
ignored fields could hide a real regression
manual-review oracle is used as a final automated PASS without approval
oracle definition changes during validation
```

---

# 18. Baseline Change Governance

Baseline updates are not part of ordinary candidate validation. A candidate change must be evaluated against the already-approved baseline.

Rules:

```text
baseline used for candidate validation must be approved before the reviewed commit
baseline update requires a separate baseline-change record
baseline update and candidate validation must not be collapsed into one undocumented action
new baseline must include reason, old baseline hash, new baseline hash, benchmark suite ID, metric definition ID, threshold set ID, and reviewer approval
baseline changes caused by intentional behavior changes must still show old-vs-new impact
```

Required baseline-change record, if baseline changed:

```json
{
  "schema_version": "1.0",
  "schema_id": "evaluation_baseline_change.schema.json",
  "baseline_change_id": "<id>",
  "changed_at": "<UTC timestamp>",
  "changed_by": "<reviewer/tool>",
  "reason": "<reason>",
  "old_baseline_id": "<id>",
  "old_baseline_sha256": "<sha256>",
  "new_baseline_id": "<id>",
  "new_baseline_sha256": "<sha256>",
  "impact_summary": {},
  "approval_ref": "<approval id>",
  "warnings": [],
  "errors": []
}
```

Blocking if:

```text
baseline is regenerated to make candidate pass
baseline changes without a baseline-change record
baseline change lacks old/new hashes
baseline change lacks approval reference
review compares candidate only against a newly generated baseline with no old-baseline impact
```

---

# 19. Benchmark Input Change Governance

Benchmark input changes must be governed separately from ordinary candidate validation. This applies to benchmark cases, oracle definitions, threshold sets, metric definitions, resource budgets, and lockfiles.

Rules:

```text
benchmark cases must not be added, removed, or rewritten during the same review that evaluates a candidate change unless a benchmark-change record exists
oracle definitions must not be loosened to make a candidate pass
thresholds must not be lowered to make a candidate pass
metric definitions or weights must not be changed to improve the candidate score
resource budgets must not be widened to hide timeouts or hangs
lockfiles must be regenerated only as part of an approved benchmark-change action, not silently during validation
all benchmark input changes require old/new hashes and rationale
```

Required benchmark-change record, if any benchmark input changed:

```json
{
  "schema_version": "1.0",
  "schema_id": "evaluation_benchmark_change.schema.json",
  "benchmark_change_id": "<id>",
  "changed_at": "<UTC timestamp>",
  "changed_by": "<reviewer/tool>",
  "change_type": "CASE|ORACLE|THRESHOLD|METRIC|RESOURCE_BUDGET|LOCKFILE|SUITE_MANIFEST",
  "reason": "<reason>",
  "old_artifact_ref": "<path or id>",
  "old_artifact_sha256": "<sha256>",
  "new_artifact_ref": "<path or id>",
  "new_artifact_sha256": "<sha256>",
  "impact_summary": {},
  "approval_ref": "<approval id>",
  "warnings": [],
  "errors": []
}
```

Blocking if:

```text
benchmark cases are removed to avoid failures
oracles are loosened to pass a candidate
thresholds are lowered during validation
metric weights are changed during validation
resource budgets are widened during validation without benchmark-change approval
lockfile is regenerated without a benchmark-change record
benchmark-change record lacks old/new hashes
benchmark-change record lacks approval reference
```

---

# 20. Partial-Suite and Diagnostic-Run Rules

A partial benchmark run may be useful for debugging, but it cannot support a final DONE verdict unless the active gating suite is explicitly defined as partial in the lockfile.

Status categories:

```text
GATING_FULL_SUITE
GATING_APPROVED_SUBSET
DIAGNOSTIC_SUBSET
SMOKE_ONLY
```

Rules:

```text
GATING_FULL_SUITE may support DONE if all other criteria pass.
GATING_APPROVED_SUBSET may support DONE only if the lockfile defines it as the active gate and the omitted cases are listed with rationale.
DIAGNOSTIC_SUBSET cannot support DONE.
SMOKE_ONLY cannot support DONE.
```

Blocking if:

```text
final DONE is based on a diagnostic subset
case failures are avoided by running only a subset
case count differs from lockfile without a deviation record
omitted cases lack rationale
```

---

# 21. Resource Budget and Timeout Review

The Evaluation Harness must not pass because it hangs, silently skips slow cases, or consumes unbounded resources.

Required budget fields:

```text
resource_budget_id
max_total_runtime_seconds
max_case_runtime_seconds
max_memory_mb, if measurable
max_artifact_size_mb
max_report_size_mb
timeout_status_behavior
retry_policy
network_allowed=false by default
warnings
errors
```

Acceptance:

```text
resource budget exists and is hashed
timeouts are enforced
timeout is recorded as FAIL, BLOCK_PROMOTION, or configured expected failure; never silent PASS
retry policy is explicit
resource-budget violations are evidenced
```

Blocking if:

```text
no resource budget exists
benchmark can hang indefinitely
timeouts are hidden as skipped passes
resource-budget failure is ignored
network is needed by default
```

---

# 22. Environment and Dependency Lock Review

The review must distinguish true implementation regressions from environment drift.

Required environment evidence:

```text
python version
pytest version
jsonschema version
operating system
active dependency lockfile hash, if the repository has one
relevant environment variables, redacted
network mode
local-only / hosted-provider mode
```

Acceptance:

```text
environment is recorded in the evidence manifest and review report
dependency lockfile hash is recorded when a lockfile exists
environment variables are redacted before evidence writing
benchmark results do not depend on network or hosted providers by default
environment drift is listed as a deviation if it affects scores
```

Blocking if:

```text
environment is not recorded
dependency lockfile exists but its hash is missing
environment drift changes benchmark outcomes without a deviation record
secrets or provider credentials are logged
network/provider availability changes benchmark results by default
```

---

# 23. Benchmark Contamination and Anti-Overfitting Review

The review must ensure that benchmark results are trustworthy and not produced by tuning specifically against the active benchmark in a way that hides general regressions.

Required checks:

```text
[ ] candidate code does not special-case benchmark case IDs
[ ] prompts, models, or rules were not tuned on the active gating suite without benchmark-change disclosure
[ ] benchmark expected outputs are not read by runtime code under evaluation
[ ] benchmark fixture paths are not used as implementation inputs except by the harness
[ ] hidden/holdout cases, if present, are not exposed to implementation code
[ ] generated reports distinguish public benchmark results from holdout results
[ ] benchmark case removal is recorded as baseline/benchmark governance, not silent deletion
```

Blocking if:

```text
implementation detects benchmark IDs to pass tests
candidate prompts/models/rules are tuned against the active gating suite and presented as general regression improvement without disclosure
runtime code reads expected outputs directly
failing cases are removed without benchmark-change record
holdout cases leak into implementation logic
```

---

# 24. Benchmark Execution Result

Record benchmark execution result.

```text
benchmark_suite_id: <suite id>
baseline_id: <baseline id>
metric_definition_id: <metric definition id>
command: <benchmark command or pytest test>
exit_code: <integer>
status: PASS | FAIL | NOT RUN
cases_total: <integer>
cases_passed: <integer>
cases_failed: <integer>
cases_expected_failed: <integer>
cases_skipped: <integer>
cases_flaky: <integer>
cases_nondeterministic: <integer>
deterministic_replay_status: PASS | FAIL | NOT CHECKED
random_seed: <seed or NOT USED>
output_artifact: <path>
output_sha256: <sha256>
```

Acceptance:

```text
benchmark suite loads
benchmark cases validate before execution
benchmark execution is deterministic
benchmark results are written as structured artifacts
failures are classified
expected failures are separated from true passes
skipped cases do not inflate scores
flaky/nondeterministic cases are not counted as clean passes
```

Blocking if:

```text
benchmark suite cannot load
benchmark cases execute without schema validation
results differ across deterministic replay
failed cases lack failure classification
expected failures are counted as normal passes
skipped cases inflate scores
flaky cases are hidden
benchmark output is unstructured
benchmark execution requires network, hosted model, or external service by default
```

---

# 25. Deterministic Replay Protocol

The review must prove reproducibility.

Required deterministic replay controls:

```text
[ ] benchmark case order is stable
[ ] random seed is fixed or randomness is not used
[ ] timestamps are excluded from score-affecting comparisons or normalized
[ ] temporary paths are excluded from score-affecting comparisons or normalized
[ ] environment-specific values are excluded from score-affecting comparisons or normalized
[ ] case results are stable across at least two runs
[ ] baseline is unchanged between runs
[ ] thresholds are unchanged between runs
[ ] metric definitions are unchanged between runs
```

Record:

```text
replay_run_1_id: <id>
replay_run_2_id: <id>
replay_command: <command>
exit_code: <integer>
status: PASS | FAIL | NOT RUN
score_run_1: <value>
score_run_2: <value>
case_diff_count: <integer>
allowed_normalized_diff_count: <integer>
output_artifact: <path>
output_sha256: <sha256>
```

Blocking if:

```text
same inputs produce different score-affecting outputs
benchmark ordering is nondeterministic
randomness is unseeded
transient fields affect scores
baseline or thresholds change between replay runs
```

---

# 26. Metric and Scoring Result

Record score calculation result.

```text
metric_definition_id: <id>
metric_definition_version: <version>
metric_definition_sha256: <sha256>
score_command: <command or pytest test>
exit_code: <integer>
status: PASS | FAIL | NOT RUN
overall_score: <value>
case_weighting_method: <equal | explicit-weighted | other>
weights_hash: <sha256 or NOT USED>
passed_case_count: <integer>
failed_case_count: <integer>
expected_failure_count: <integer>
skipped_case_count: <integer>
score_artifact: <path>
score_artifact_sha256: <sha256>
```

Acceptance:

```text
metric definitions are explicit
scoring is deterministic
weights are explicit and hashed if used
failed cases are included in score calculation
expected failures are handled separately
skipped cases are handled separately
score output is structured
```

Blocking if:

```text
metric formula is missing
metric formula changes during review
failed cases are omitted from denominator without documented rule
expected failures inflate score
skipped cases inflate score
weights are hidden or modified to pass
score cannot be reproduced from artifacts
```

---

# 27. Regression Comparison Result

Record regression comparison result.

```text
comparison_id: <id>
current_run_id: <id>
baseline_run_id: <id>
metric_definition_id: <id>
command: <comparison command or pytest test>
exit_code: <integer>
status: PASS | FAIL | NOT RUN
regressions_detected: <integer>
critical_regressions_detected: <integer>
high_regressions_detected: <integer>
medium_regressions_detected: <integer>
low_regressions_detected: <integer>
improvements_detected: <integer>
unchanged_cases: <integer>
regression_decision: PASS | FAIL | BLOCK_PROMOTION
output_artifact: <path>
output_sha256: <sha256>
```

Acceptance:

```text
baseline is explicit
current run is explicit
comparison is deterministic
regression thresholds are applied
promotion-blocking regressions are detected
comparison artifact is written
improvements are distinguished from regressions
unchanged cases are counted
```

Blocking if:

```text
comparison runs without explicit baseline
baseline is silently overwritten
regressions are ignored
comparison cannot distinguish improvement from regression
regression severity is missing for failing cases
regression decision is not evidence-backed
```

---

# 28. Regression Severity Rules

Classify regressions with these levels.

```text
CRITICAL:
  safety, policy, sandbox, source-mutation, tool-execution, promotion-gate, or evidence regression

HIGH:
  benchmark pass/fail regression, major score drop, schema validation regression, deterministic replay regression

MEDIUM:
  non-safety behavior regression, partial score drop, report metadata regression

LOW:
  wording-only report drift, non-critical metadata drift, optional ecosystem placement regression
```

Promotion-blocking rules:

```text
any CRITICAL regression -> BLOCK_PROMOTION
any HIGH regression above threshold tolerance -> BLOCK_PROMOTION
any deterministic replay regression -> BLOCK_PROMOTION
any schema/evidence regression -> BLOCK_PROMOTION
any threshold failure -> BLOCK_PROMOTION
```

---

# 29. Threshold Result

Record threshold result.

```text
threshold_set_id: <id>
threshold_set_version: <version>
threshold_set_sha256: <sha256>
command: <threshold command or pytest test>
exit_code: <integer>
status: PASS | FAIL | NOT RUN
minimum_score_required: <value>
current_score: <value>
regression_tolerance: <value>
critical_regression_tolerance: 0
threshold_decision: PASS | FAIL | BLOCK_PROMOTION
output_artifact: <path>
output_sha256: <sha256>
```

Acceptance:

```text
thresholds are explicit
thresholds are fixed for the reviewed run
thresholds are not silently changed to pass
threshold failures block DONE or promotion where required
threshold decision is evidenced
critical regression tolerance is zero unless explicitly changed by major contract revision
```

Blocking if:

```text
thresholds are missing
thresholds are changed during review without deviation record
threshold failure is reported as pass
promotion-blocking threshold failure is ignored
critical regression tolerance is nonzero without major contract revision
```

---

# 30. Evidence / Artifact Result

Required evidence behavior:

```text
[ ] evaluation_run_history.jsonl is written
[ ] evaluation_result_history.jsonl is written
[ ] regression_comparison_history.jsonl is written
[ ] threshold_decision_history.jsonl is written
[ ] latest_evaluation_run.json is written atomically
[ ] latest_evaluation_result.json is written atomically
[ ] latest_regression_comparison.json is written atomically
[ ] evaluation_evidence_manifest.json is written
[ ] evaluation_review_report.json is written
[ ] evaluation_completion_record.json is written after validation
[ ] evidence includes reviewed commit
[ ] evidence includes benchmark suite ID
[ ] evidence includes benchmark suite hash
[ ] evidence includes baseline ID
[ ] evidence includes baseline hash
[ ] evidence includes threshold set ID
[ ] evidence includes threshold set hash
[ ] evidence includes metric definition ID and hash
[ ] evidence includes command text, exit codes, statuses, and summaries
[ ] evidence includes hashes for final artifacts
[ ] benchmark report is evidence-backed if written
[ ] prompt text, command output, tool output, environment variables, and provider credentials are redacted or bounded before durable evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
evaluation runs are not logged
benchmark results are not logged
regression comparisons are not logged
threshold decisions are not logged
evidence lacks reviewed commit
evidence lacks baseline reference
evidence lacks threshold reference
evidence lacks metric definition reference
evidence hashes are missing
report exists but is not backed by evidence
secrets, provider credentials, or unbounded raw outputs are persisted
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
only expected runtime artifacts under .agentx-init/evaluation/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by evaluation runs
baseline fixtures are overwritten during validation
threshold configuration is modified during validation
metric definitions are modified during validation
unapproved files are created outside runtime artifact paths
benchmark reports are written outside approved artifact roots without deviation
```

---

# 32. Integration Coverage

## 24.1 Tool / MCP Adapter Integration

Applies if the evaluation harness invokes registered tools.

```text
[ ] evaluation invokes tools only through Tool / MCP Adapter
[ ] evaluation does not call unsafe wrappers directly
[ ] tool calls are policy-checked
[ ] tool results are schema-validated
[ ] tool evidence refs are preserved in evaluation results
[ ] blocked/invalid tool results are counted honestly in evaluation outcomes
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
evaluation bypasses Tool / MCP Adapter for registered tools
unsafe direct tool calls are used
tool evidence is dropped
blocked/invalid tool results are hidden from scoring
```

## 24.2 Policy / Capability Registry Integration

Applies if evaluation permissions are checked.

```text
[ ] evaluation run checks policy before invoking tools or commands
[ ] policy-denied evaluation returns BLOCKED
[ ] missing policy fails closed for non-read-only execution
[ ] policy decision IDs are included in evidence where available
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
policy-denied evaluation executes anyway
missing policy defaults to ALLOW for non-read-only execution
policy evidence is discarded when available
```

## 24.3 Command Acceptance Integration

Applies if the evaluation harness executes commands.

```text
[ ] commands are allowlisted
[ ] raw shell is not used
[ ] command output is bounded
[ ] command exit codes are recorded
[ ] network commands are blocked by default
[ ] Git write commands are blocked by default
[ ] command output is redacted before durable evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
raw shell executes
unknown command executes
network command executes by default
Git write command executes during evaluation
command exit code is missing
unredacted command output is persisted
```

---

# 33. Negative Test Pack

The review must prove forbidden behavior fails closed.

Required negative cases:

```text
[ ] invalid benchmark suite -> FAIL before execution
[ ] invalid benchmark case -> FAIL before execution
[ ] missing baseline -> FAIL or BLOCK_PROMOTION
[ ] missing threshold -> FAIL or BLOCK_PROMOTION
[ ] missing metric definition -> FAIL or BLOCK_PROMOTION
[ ] nondeterministic replay -> FAIL
[ ] regression above tolerance -> BLOCK_PROMOTION
[ ] critical regression -> BLOCK_PROMOTION
[ ] threshold failure -> BLOCK_PROMOTION
[ ] report without evidence -> FAIL
[ ] attempt to overwrite baseline during evaluation -> BLOCKED
[ ] attempt to rewrite threshold during evaluation -> BLOCKED
[ ] attempt to rewrite metric definition during evaluation -> BLOCKED
[ ] attempt to mutate source during evaluation -> BLOCKED
[ ] command not allowlisted -> BLOCKED
[ ] raw shell command -> BLOCKED
[ ] network required by default -> BLOCKED
[ ] tool invocation without Tool Adapter, when required -> BLOCKED
[ ] policy-denied evaluation -> BLOCKED
[ ] skipped case inflates score -> FAIL
[ ] expected failure counted as normal pass -> FAIL
[ ] flaky case hidden as clean pass -> FAIL
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked not applicable with justification.

---

# 34. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
benchmark freeze / integrity:
benchmark execution:
deterministic replay:
metric / scoring:
regression comparison:
threshold checks:
evidence/artifacts:
report generation:
Tool / MCP Adapter integration:
Policy / Capability Registry integration:
command safety:
negative tests:
source mutation check:
completion record:
```

---

# 35. What Failed

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

# 36. Issue Severity Classification

## 36.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
benchmark suite cannot load
benchmark input hashes are missing
benchmark execution is nondeterministic
baseline is missing
baseline is overwritten during review
thresholds are missing
thresholds are changed to pass validation
metric definitions are missing
metric definitions are changed during review
regression comparison fails
regression above tolerance is not detected
critical regression does not block promotion
threshold failure does not block promotion
expected failures are counted as normal passes
skipped cases inflate scores
flaky cases are hidden
source mutation occurs during evaluation
raw shell executes
network is required by default
Tool / MCP Adapter is bypassed when required
policy-denied evaluation executes anyway
evidence is missing
evidence hashes are missing
review report is missing
completion record is missing
required area remains NOT CHECKED
required command remains NOT RUN
```

## 36.2 HIGH

High issues must be fixed before this layer is used by a promotion gate.

```text
incomplete evidence references
partial regression fixture coverage
partial negative test coverage
report generated but missing some non-critical metadata
benchmark suite lacks enough representative cases
runtime artifact boundary exception lacks justification
review environment not recorded
expected-failure rationale incomplete
skipped-case rationale incomplete
```

## 36.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled benchmark fixtures
optional report format missing
optional ecosystem placement notes absent
future benchmark category deferred safely
additional non-gating metrics planned for later
```

---

# 37. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Benchmark | Regression | Threshold | Metric | Evidence | Report | Command | Tool Adapter | Policy | Runtime Artifact Boundary | Other>
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
Runtime artifact writes outside `.agentx-init/evaluation/` require a deviation entry.
Missing evidence hashes cannot be accepted as a deviation for DONE.
Missing benchmark hashes cannot be accepted as a deviation for DONE.
Missing baseline cannot be accepted as a deviation for DONE.
Missing thresholds cannot be accepted as a deviation for DONE.
Missing metric definitions cannot be accepted as a deviation for DONE.
```

---

# 38. Evidence Manifest

Create:

```text
.agentx-init/evaluation/evaluation_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "evaluation_evidence_manifest.schema.json",
  "component_id": "AGENTX_EVALUATION_HARNESS",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>",
    "timezone": "UTC"
  },
  "benchmark_suite_id": "<suite id>",
  "benchmark_suite_version": "<version>",
  "benchmark_suite_sha256": "<sha256>",
  "baseline_id": "<baseline id>",
  "baseline_version": "<version>",
  "baseline_sha256": "<sha256>",
  "threshold_set_id": "<threshold id>",
  "threshold_set_version": "<version>",
  "threshold_set_sha256": "<sha256>",
  "metric_definition_id": "<metric definition id>",
  "metric_definition_version": "<version>",
  "metric_definition_sha256": "<sha256>",
  "benchmark_lockfile_id": "<lockfile id>",
  "benchmark_lockfile_sha256": "<sha256>",
  "oracle_definition_id": "<oracle definition id>",
  "oracle_definition_sha256": "<sha256>",
  "resource_budget_id": "<budget id>",
  "resource_budget_sha256": "<sha256>",
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
    },
    {
      "name": "benchmark_execution",
      "command": "<benchmark execution command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "deterministic_replay",
      "command": "<deterministic replay command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "regression_comparison",
      "command": "<regression comparison command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "threshold_check",
      "command": "<threshold check command>",
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
  "benchmark_integrity_status": "PASS",
  "deterministic_replay_status": "PASS",
  "regression_status": "PASS",
  "threshold_status": "PASS",
  "metric_status": "PASS",
  "report_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

The manifest must include paths and hashes for all final evidence files, including:

```text
evaluation_evidence_manifest.json
evaluation_review_report.json
evaluation_completion_record.json
command output artifacts, if stored as files
JSONL evidence histories used by the review
latest_evaluation_run.json, if used by the review
latest_evaluation_result.json, if used by the review
latest_regression_comparison.json, if used by the review
benchmark suite manifest
active benchmark case files
baseline record
threshold record
metric definition record
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Approved runtime artifact boundary:

```text
.agentx-init/evaluation/
```

Evidence artifacts for this layer must not be written outside that root unless the review records the exception in the deviation register.

---

# 39. Review Report Artifact

Create:

```text
.agentx-init/evaluation/evaluation_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "evaluation_report.schema.json",
  "component_id": "AGENTX_EVALUATION_HARNESS",
  "review_document_id": "EVALUATION_HARNESS_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v4.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>",
    "timezone": "UTC"
  },
  "benchmark_suite_id": "<suite id>",
  "benchmark_suite_sha256": "<sha256>",
  "baseline_id": "<baseline id>",
  "baseline_sha256": "<sha256>",
  "threshold_set_id": "<threshold id>",
  "threshold_set_sha256": "<sha256>",
  "metric_definition_id": "<metric definition id>",
  "metric_definition_sha256": "<sha256>",
  "benchmark_lockfile_id": "<lockfile id>",
  "benchmark_lockfile_sha256": "<sha256>",
  "oracle_definition_id": "<oracle definition id>",
  "oracle_definition_sha256": "<sha256>",
  "resource_budget_id": "<budget id>",
  "resource_budget_sha256": "<sha256>",
  "promotion_gate_summary_path": ".agentx-init/evaluation/evaluation_promotion_gate_summary.json",
  "promotion_gate_summary_sha256": "<sha256>",
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [],
  "coverage_statuses": {},
  "benchmark_summary": {},
  "deterministic_replay_summary": {},
  "metric_summary": {},
  "regression_summary": {},
  "threshold_summary": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/evaluation/evaluation_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/evaluation/evaluation_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/evaluation/evaluation_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is invalid if it does not identify:

```text
reviewed commit
review environment
benchmark suite
baseline
threshold set
metric definition
commands and exit codes
evidence manifest
final verdict
```

## 39.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
baseline changes require a new benchmark review
threshold changes require a new benchmark review
metric definition changes require a new benchmark review
benchmark fixture changes require a new benchmark review
```

---

# 40. Promotion Gate Summary Contract

Create a machine-readable downstream gate summary whenever this layer is used to inform promotion.

Required path:

```text
.agentx-init/evaluation/evaluation_promotion_gate_summary.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "evaluation_promotion_gate_summary.schema.json",
  "component_id": "AGENTX_EVALUATION_HARNESS",
  "validated_commit": "<commit hash>",
  "benchmark_suite_id": "<suite id>",
  "benchmark_lockfile_sha256": "<sha256>",
  "baseline_id": "<baseline id>",
  "threshold_set_id": "<threshold id>",
  "metric_definition_id": "<metric id>",
  "overall_score": "<value>",
  "threshold_decision": "PASS|FAIL|BLOCK_PROMOTION",
  "regression_decision": "PASS|FAIL|BLOCK_PROMOTION",
  "critical_regressions_detected": 0,
  "promotion_recommendation": "ALLOW|WARN|BLOCK",
  "evidence_manifest_path": ".agentx-init/evaluation/evaluation_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
BLOCK_PROMOTION maps to promotion_recommendation = BLOCK
critical regression count greater than zero maps to BLOCK
missing evidence manifest maps to BLOCK
missing benchmark lockfile hash maps to BLOCK
WARN is allowed only for non-blocking follow-ups
ALLOW is allowed only when all GO criteria pass
```

Blocking if:

```text
promotion gate summary is missing when promotion depends on evaluation
promotion recommendation conflicts with threshold or regression decision
BLOCK_PROMOTION is mapped to WARN or ALLOW
summary lacks evidence manifest reference or hash
```

---

# 41. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Evaluation package, schemas, tests, benchmark fixtures, runtime artifact paths exist. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including report, evidence manifest, and completion record. |
| Benchmark integrity and execution | 1.0 | Suites/cases/baselines/thresholds/metrics are fixed, hashed, loaded, and executed. |
| Deterministic replay | 1.0 | Same inputs produce same score-affecting outputs. |
| Metric and scoring correctness | 1.0 | Stable formulas, explicit weights, no hidden denominator changes. |
| Regression and threshold enforcement | 1.0 | Regressions and threshold failures are detected and block promotion where required. |
| Evidence and reports | 1.0 | JSONL histories, latest artifacts, manifest, review report, hashes, redaction, completion record. |
| Integration and source-mutation safety | 1.0 | Tool Adapter, policy, command safety where applicable; clean git status; no source/baseline/threshold mutation. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not promotion-gate complete
below 7.0 = not acceptable for regression control
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
missing benchmark suite caps score at 6.0
missing baseline caps score at 6.0
missing threshold set caps score at 6.0
missing metric definition caps score at 6.5
missing benchmark lockfile caps score at 6.5
missing oracle definition caps score at 6.5
incomplete gating suite caps score at 7.0
missing resource budget caps score at 8.0
missing environment/dependency lock evidence caps score at 8.0
missing baseline-change approval caps score at 7.0
missing benchmark-change approval caps score at 7.0
missing promotion gate summary, when promotion depends on evaluation, caps score at 8.0
nondeterministic replay caps score at 6.5
regression comparison failure caps score at 7.0
threshold enforcement failure caps score at 7.0
critical regression not blocking promotion caps score at 5.0
baseline overwrite caps score at 5.0
threshold rewrite to pass caps score at 5.0
metric rewrite to pass caps score at 5.0
source mutation by evaluation caps score at 7.0
raw shell execution caps score at 5.0
network required by default caps score at 5.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
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
benchmark suite loads
benchmark suite is hashed
benchmark cases are hashed
baseline is explicit and hashed
threshold set is explicit and hashed
metric definition is explicit and hashed
benchmark lockfile is explicit and hashed
oracle definitions are explicit and hashed
resource budget is explicit and hashed
environment/dependency lock evidence is recorded or not applicable
active gating suite is complete or approved subset is lockfile-defined
benchmark execution passes or expected failures are correctly classified
benchmark replay is deterministic
score calculation is reproducible
regression comparison passes
threshold checks pass
promotion-blocking regressions are detected
critical regressions block promotion
threshold failures block promotion
negative tests pass
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

## 42.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
benchmark suite cannot load
benchmark inputs are not hashed
benchmark execution is nondeterministic
baseline is missing
baseline is overwritten during validation
thresholds are missing
threshold checks fail without correct blocking decision
metric definitions are missing
metric definitions change during review
benchmark lockfile is missing or changes during review
oracle definitions are missing or vague
active gating suite is incomplete without approved-subset lockfile
resource budget is missing or unenforced
environment/dependency lock evidence is missing where applicable
benchmark input changes lack benchmark-change approval
score calculation is not reproducible
regression comparison fails
critical regression does not block promotion
threshold failure does not block promotion
source mutation occurs during evaluation
raw shell executes
network is required by default
Tool / MCP Adapter is bypassed when required
policy-denied evaluation executes anyway
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

If implementation fails validation, fixes must not weaken evaluation integrity.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix benchmark fixture metadata
fix deterministic ordering
fix stable random seed behavior
fix transient-field normalization
fix baseline reference handling
fix regression comparator logic
fix threshold checker logic
fix metric definition schema
fix score calculator denominator handling
fix expected-failure accounting
fix skipped/flaky-case accounting
fix failure classification
fix report generation
fix evidence writing
fix evidence manifest generation
fix evidence hashing
fix test fixtures to reflect the contract
```

Forbidden fixes:

```text
do not lower thresholds to pass validation
do not overwrite baselines during review
do not rewrite metric definitions to pass validation
do not modify oracle definitions to pass validation
do not widen resource budgets to hide failures
do not delete failing benchmark cases to pass tests
do not mark regressions as improvements
do not ignore failed cases in score calculation
do not count expected failures as normal passes
do not count skipped cases as normal passes
do not hide flaky cases
do not remove schema checks to pass tests
do not skip deterministic replay
do not skip evidence writing
do not omit hashes for final DONE
do not allow raw shell execution
do not enable network by default
do not bypass Tool / MCP Adapter when required
do not bypass Policy / Capability Registry when required
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
```

---

# 44. Definition of Done

The Evaluation Harness / Regression Benchmark Layer is done when it can act as Agent_X's controlled evaluation and regression gate.

It must prove:

```text
all target files exist
all schemas exist
all tests exist
benchmark suites are structured and schema-valid
benchmark cases are deterministic
benchmark inputs are hashed
benchmark lockfile hashes all score-affecting inputs
oracle definitions are explicit and hashed
resource budgets and timeouts are enforced
environment/dependency lock evidence is recorded where applicable
active gating suite is complete or approved subset is lockfile-defined
benchmark execution writes structured results
scores are calculated reproducibly
metric definitions are explicit and hashed
baselines are explicit and not overwritten during review
thresholds are explicit and enforced
regressions are detected
critical regressions block promotion
threshold failures block promotion
expected failures are not counted as normal passes
skipped and flaky cases do not inflate scores
failure classifications are recorded
reports are evidence-backed
promotion gate summary is written when promotion depends on evaluation
runtime artifacts are written under .agentx-init/evaluation/
evidence manifest is written
review report is written
evidence hashes are written
review environment is recorded
no source mutation occurs during evaluation
no baseline mutation occurs during evaluation
no threshold mutation occurs during evaluation
no metric mutation occurs during evaluation
no network is required by default
no raw shell is executed
completion record exists
final verdict is recorded
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_evaluation_schemas.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_evaluation_deterministic_replay.py
git status --short
```

Expected:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
deterministic replay PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

---

# 45. Completion Evidence Record

After validation, create:

```text
.agentx-init/evaluation/evaluation_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "evaluation_completion_record.schema.json",
  "component_id": "AGENTX_EVALUATION_HARNESS",
  "component_name": "Evaluation Harness / Regression Benchmark Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>",
    "timezone": "UTC"
  },
  "canonical_evaluation_subdirectory": "tools/agentx_evolve/evaluation/",
  "canonical_benchmark_subdirectory": "tools/agentx_evolve/evaluation/benchmarks/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/evaluation/",
  "basis_documents": [
    "EVALUATION_HARNESS_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "EVALUATION_HARNESS_IMPLEMENTATION_SPEC",
    "EVALUATION_HARNESS_IMPLEMENTATION_REVIEW_AND_DOD_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "benchmark_suites_verified": [],
  "benchmark_cases_verified": [],
  "baselines_verified": [],
  "thresholds_verified": [],
  "metric_definitions_verified": [],
  "oracle_definitions_verified": [],
  "benchmark_lockfiles_verified": [],
  "resource_budgets_verified": [],
  "regression_checks_verified": [],
  "deterministic_replay_verified": [],
  "reports_verified": [],
  "promotion_gate_summary_verified": [],
  "evidence_manifest_path": ".agentx-init/evaluation/evaluation_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/evaluation/evaluation_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 46. Final Done / Not-Done Verdict

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
benchmark suite is missing or unhashed
benchmark baseline is missing or unhashed
threshold set is missing or unhashed
metric definition is missing or unhashed
benchmark lockfile is missing or unhashed
oracle definition is missing or unhashed
resource budget is missing or unhashed
active gating suite is incomplete without approved-subset lockfile
regression comparison is missing
deterministic replay is missing
```

---

# 47. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/evaluation/ exists
[ ] schemas exist
[ ] tests exist
[ ] benchmark fixtures exist
[ ] baseline records exist
[ ] threshold definitions exist
[ ] metric definitions exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] benchmark execution PASS
[ ] deterministic replay PASS
[ ] regression comparison PASS
[ ] threshold checks PASS
[ ] git status clean or expected runtime artifacts only

Benchmark Integrity:
[ ] benchmark suite is identified
[ ] benchmark suite is hashed
[ ] benchmark cases are schema-valid
[ ] benchmark cases are hashed
[ ] expected outputs are explicit
[ ] baseline is explicit
[ ] baseline is hashed
[ ] baseline is not overwritten
[ ] threshold set is explicit
[ ] threshold set is hashed
[ ] threshold set is not rewritten
[ ] metric definition is explicit
[ ] metric definition is hashed
[ ] metric definition is not rewritten
[ ] benchmark lockfile exists
[ ] benchmark lockfile is hashed
[ ] oracle definitions exist for every active case
[ ] oracle definitions are hashed
[ ] resource budget exists and is enforced
[ ] environment/dependency lock evidence recorded where applicable
[ ] benchmark-change records exist for any benchmark input change

Benchmark Execution:
[ ] cases are deterministic
[ ] failures are classified
[ ] expected failures are separated from normal passes
[ ] skipped cases do not inflate scores
[ ] flaky cases are not hidden as clean passes

Regression:
[ ] comparison is deterministic
[ ] regressions are detected
[ ] improvements are distinguished from regressions
[ ] critical regressions block promotion
[ ] unchanged cases are counted

Thresholds:
[ ] thresholds are fixed for the reviewed run
[ ] threshold failures block promotion
[ ] regression tolerance is enforced
[ ] critical regression tolerance is zero unless major revision allows otherwise

Evidence:
[ ] evaluation run history written
[ ] evaluation result history written
[ ] regression comparison history written
[ ] threshold decision history written
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] promotion gate summary written when required
[ ] SHA-256 hashes written

Safety:
[ ] no source mutation during evaluation
[ ] no baseline overwrite during validation
[ ] no threshold rewrite during validation
[ ] no metric rewrite during validation
[ ] no raw shell
[ ] no network by default
[ ] Tool / MCP Adapter not bypassed when required
[ ] Policy / Capability Registry not bypassed when required

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 48. Final Sign-Off Template

Use this after implementation validation.

```text
Evaluation Harness Validation — Commit <hash>

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
- benchmark integrity: PASS/FAIL
- benchmark execution: PASS/FAIL, exit_code=<code>
- deterministic replay: PASS/FAIL, exit_code=<code>
- metric / scoring: PASS/FAIL, exit_code=<code>
- regression comparison: PASS/FAIL, exit_code=<code>
- threshold checks: PASS/FAIL, exit_code=<code>
- evidence/artifact coverage: PASS/FAIL
- report coverage: PASS/FAIL/N/A
- Tool / MCP Adapter integration: PASS/FAIL/N/A
- Policy / Capability Registry integration: PASS/FAIL/N/A
- command safety: PASS/FAIL/N/A
- negative-test coverage: PASS/FAIL
- source mutation check: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- review report: PRESENT/MISSING
- completion record: PRESENT/MISSING

Benchmark Summary:
- benchmark suite: <id>, sha256=<hash>
- baseline: <id>, sha256=<hash>
- threshold set: <id>, sha256=<hash>
- metric definition: <id>, sha256=<hash>
- benchmark lockfile: <id>, sha256=<hash>
- oracle definition: <id>, sha256=<hash>
- resource budget: <id>, sha256=<hash>
- cases total: <count>
- cases passed: <count>
- cases failed: <count>
- expected failures: <count>
- skipped cases: <count>
- flaky cases: <count>
- regressions detected: <count>
- critical regressions detected: <count>
- threshold decision: PASS/FAIL/BLOCK_PROMOTION

Reproducibility:
- exact commands recorded: YES/NO
- exit codes recorded: YES/NO
- output artifacts recorded: YES/NO
- final hashes recorded: YES/NO
- deterministic replay checked: YES/NO
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

# 49. Final Freeze Rule

This v4 document is frozen as the post-implementation review / Definition of Done template for the Evaluation Harness / Regression Benchmark Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes, section-reference fixes
MINOR: additive optional checks that do not change DONE semantics
MAJOR: changed scoring semantics, changed threshold policy, changed benchmark-lockfile rules, changed oracle rules, changed promotion-blocking behavior, or new required benchmark category
```

Blocked without major revision:

```text
lowering thresholds by default
allowing missing baselines
allowing missing oracle definitions
allowing missing benchmark lockfile
allowing incomplete gating suites without lockfile approval
allowing nondeterministic replay to pass
allowing expected failures or skipped cases to inflate score
allowing benchmark input changes without governance
removing evidence hashing
removing promotion-blocking behavior for critical regressions
```

---

# 50. Final Rating

This v4 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the full v3 validation coverage and fixes the remaining review-template and production-gate gaps: complete schema/test checklist alignment, benchmark-input change governance, no-training/no-tuning disclosure for active gating suites, redaction and bounded-output requirements, environment/dependency lock evidence, machine-readable promotion gate summary, stricter hard score caps, stable sectioning, and a final freeze rule. It now defines a reproducible, auditable, anti-gaming validation process for the Evaluation Harness / Regression Benchmark Layer.
```
