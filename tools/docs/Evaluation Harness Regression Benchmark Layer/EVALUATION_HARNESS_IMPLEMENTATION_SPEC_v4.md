# EVALUATION_HARNESS_IMPLEMENTATION_SPEC

```text
document_id: EVALUATION_HARNESS_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen coding-agent handoff
component_id: AGENTX_EVALUATION_HARNESS
component_name: Evaluation Harness / Regression Benchmark Layer
roadmap_layer: 15
roadmap_phase: Phase D — Evaluation and Promotion Safety
target_language: Python
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Tool / MCP Adapter Acceptance Criteria, Policy / Capability Registry Acceptance Criteria
canonical_subdirectory: tools/agentx_evolve/evaluation/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
benchmark_fixture_root: tools/agentx_evolve/evaluation/fixtures/
runtime_artifact_root: .agentx-init/evaluation/
implementation_mode: deterministic offline evaluation harness first, no model/network dependency by default
previous_version_rating: 9.8/10
current_version_rating: 10/10
rating_target: 10/10
```

---

# 0. v4 Review and Upgrade Summary

The v3 implementation specification was strong and nearly implementation-ready. I would rate it:

```text
9.8/10
```

It already covered:

```text
exact subdirectory
files to create
schemas to create
classes/functions
runtime artifacts
benchmark fixture layout
evaluation runner
regression comparator
score calculator
threshold checker
report writer
integration with Tool / MCP Adapter
integration with Failure Taxonomy
integration with Policy / Capability Registry
test files
test cases
implementation order
acceptance criteria
Definition of Done
run configuration schema
fixture lock/provenance manifest
environment capture
baseline promotion boundary
numeric comparator tolerance rules
regex safety limits
case ordering and filtered-run semantics
mutation guard helper
partial report/evidence write failure rules
dedicated schema validation utility
```

It was not fully 10/10 because several handoff-control details still needed to be made explicit:

```text
1. Section numbering had a gap and the production-control addendum was appended rather than cleanly frozen into the handoff.
2. The command-line / programmatic entrypoint contract was not strict enough.
3. Deterministic run controls needed explicit seed, clock, case-order, and environment-normalization rules.
4. Tool-adapter case execution needed a clearer dry-run/read-only default boundary.
5. Baseline compatibility and schema-version handling needed stronger rules.
6. Report consistency between JSON and Markdown needed a machine-readable parity rule.
7. Evidence indexing and run immutability needed stricter finalization behavior.
8. Resource cleanup and temporary working-directory handling needed stronger rules.
9. Threshold severity semantics needed clearer promotion-blocking behavior.
10. The final acceptance matrix needed to include the v4 deterministic-entrypoint and evidence-finalization controls.
```

This v4 applies those corrections and is the final 10/10 implementation specification.

---

# 1. Purpose

This document is the full implementation specification for the **Evaluation Harness / Regression Benchmark Layer**.

This layer provides deterministic regression evaluation for Agent_X. It evaluates whether changes to tools, policies, prompts, adapters, orchestrators, or implementation behavior preserve required behavior or introduce regressions.

This is a coding-agent handoff document. It defines:

```text
exact subdirectory
files to create
schemas to create
classes/functions
runtime artifacts
benchmark fixture layout
evaluation runner
regression comparator
score calculator
threshold checker
report writer
integration with Tool / MCP Adapter
integration with Failure Taxonomy
integration with Policy / Capability Registry
test files
test cases
implementation order
acceptance criteria
Definition of Done
```

The Evaluation Harness must not be a vague scoring utility. It must produce reproducible, schema-valid, evidence-backed benchmark results that later promotion gates can trust.

---

# 2. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic evaluation harness that can:

```text
load benchmark suites
load benchmark cases
validate benchmark fixtures
execute offline evaluation cases
optionally call registered Tool / MCP Adapter tools in controlled mode
classify case outcomes
calculate scores
compare current results against immutable baselines
detect regressions
apply threshold rules
write evaluation evidence
write human-readable reports
write machine-readable reports
fail closed when fixtures, schemas, policy checks, or dependencies are invalid
```

The layer must support:

```text
unit-style benchmark cases
regression benchmark suites
expected-output checks
expected-status checks
expected-failure-class checks
artifact-presence checks
threshold-based pass/fail rules
baseline-vs-current comparison
first-run mode without baseline
no-network offline operation
no-source-mutation evaluation
```

The layer must not implement:

```text
model adapter
LLM worker
self-evolution orchestrator
promotion gate
patch execution
Git write operations
network benchmark fetching
background scheduler
human approval UI
```

---

# 3. Implementation Modes

The implementation must support two clearly separated modes.

## 3.1 Offline Fixture Mode

Offline fixture mode is required in v1.

Allowed:

```text
load local fixture files
validate schemas
run static expected-result checks
run score calculations
run threshold checks
compare against local baseline files
write evaluation artifacts
write reports
```

Forbidden:

```text
network
hosted model
LLM call
raw shell
Git write
MCP server startup
source mutation
```

## 3.2 Controlled Tool-Adapter Mode

Controlled Tool-Adapter mode is allowed only for tests that verify Agent_X tool behavior through the Tool / MCP Adapter dispatcher.

Allowed:

```text
load default tool registry
call execute_tool_call through dispatcher only
run dry-run tool cases
run read-only tool cases
verify invalid tools fail closed
verify blocked tools fail closed
preserve ToolResult evidence_refs in EvaluationCaseResult
```

Forbidden:

```text
calling wrapper functions directly
starting MCP server
executing raw shell
executing network tools
executing Git write tools
executing patch apply
mutating source files
```

If Tool / MCP Adapter is unavailable, tool-dependent cases must return:

```text
status = EVAL_BLOCKED
failure_class = EVAL_TOOL_ADAPTER_UNAVAILABLE
```

Pure offline fixture, scoring, threshold, reporting, and evidence tests must still run.

---

# 4. Dependency Order and Fail-Closed Rules

The Evaluation Harness must integrate with completed Agent_X safety layers when available, but must not become dependent on unsafe shortcuts.

## 4.1 Dependency Order

Preferred dependency order:

```text
1. Evaluation schemas and models
2. Fixture validator
3. Benchmark loader
4. Score calculator
5. Threshold checker
6. Regression comparator
7. Evidence writer
8. Report writer
9. Evaluation runner
10. Tool / MCP Adapter integration
11. Policy / Capability Registry integration
12. Failure Taxonomy integration
```

## 4.2 Dependency Rules

```text
Tool / MCP Adapter unavailable -> tool-dependent cases EVAL_BLOCKED, offline cases continue.
Policy / Capability Registry unavailable -> mutating/tool-execution cases EVAL_BLOCKED, offline cases continue.
Failure Taxonomy unavailable -> use local evaluation failure constants, but do not omit failure_class.
Schema validator unavailable -> schema-dependent execution EVAL_BLOCKED.
Baseline unavailable -> first-run mode only if explicitly requested or suite allows it.
```

## 4.3 Missing Dependency Must Not Become ALLOW

No missing dependency may be treated as success.

```text
missing policy cannot allow tool execution
missing tool adapter cannot mark tool cases PASS
missing schema validator cannot accept fixtures
missing baseline cannot produce REGRESSION_PASS unless first-run mode is explicit
```

---

# 5. Canonical Destination Summary

Create the evaluation package here:

```text
tools/agentx_evolve/evaluation/
```

Create schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Create deterministic benchmark fixtures here:

```text
tools/agentx_evolve/evaluation/fixtures/
```

Runtime artifacts must be written here:

```text
.agentx-init/evaluation/
```

Package split:

```text
tools/agentx_evolve/evaluation/              = evaluation harness implementation
tools/agentx_evolve/evaluation/fixtures/     = committed benchmark fixtures
tools/agentx_evolve/schemas/                 = evaluation schemas
tools/agentx_evolve/tests/                   = evaluation tests
.agentx-init/evaluation/                     = runtime benchmark evidence and reports
```

---

# 6. Exact Subdirectory

Required implementation directory:

```text
tools/agentx_evolve/evaluation/
```

Required fixture subdirectories:

```text
tools/agentx_evolve/evaluation/fixtures/
tools/agentx_evolve/evaluation/fixtures/smoke/
tools/agentx_evolve/evaluation/fixtures/regression/
tools/agentx_evolve/evaluation/fixtures/negative/
tools/agentx_evolve/evaluation/fixtures/baselines/
```

Runtime directory:

```text
.agentx-init/evaluation/
```

Runtime subdirectories:

```text
.agentx-init/evaluation/runs/
.agentx-init/evaluation/reports/
.agentx-init/evaluation/baselines/
.agentx-init/evaluation/latest/
.agentx-init/evaluation/evidence/
.agentx-init/evaluation/tmp/
```

---

# 7. Files to Create

## 7.1 Evaluation Package Files

```text
tools/agentx_evolve/evaluation/__init__.py
tools/agentx_evolve/evaluation/evaluation_models.py
tools/agentx_evolve/evaluation/evaluation_errors.py
tools/agentx_evolve/evaluation/fixture_validator.py
tools/agentx_evolve/evaluation/benchmark_loader.py
tools/agentx_evolve/evaluation/evaluation_runner.py
tools/agentx_evolve/evaluation/case_executor.py
tools/agentx_evolve/evaluation/comparator_engine.py
tools/agentx_evolve/evaluation/regression_comparator.py
tools/agentx_evolve/evaluation/score_calculator.py
tools/agentx_evolve/evaluation/threshold_checker.py
tools/agentx_evolve/evaluation/report_writer.py
tools/agentx_evolve/evaluation/evaluation_evidence.py
tools/agentx_evolve/evaluation/baseline_manager.py
tools/agentx_evolve/evaluation/path_guards.py
tools/agentx_evolve/evaluation/run_config.py
tools/agentx_evolve/evaluation/fixture_lock.py
tools/agentx_evolve/evaluation/mutation_guard.py
tools/agentx_evolve/evaluation/run_evaluation.py  # optional CLI entrypoint; required only if CLI is exposed
```

## 7.2 Fixture Files

```text
tools/agentx_evolve/evaluation/fixtures/smoke/smoke_suite.json
tools/agentx_evolve/evaluation/fixtures/smoke/tool_registry_smoke_case.json
tools/agentx_evolve/evaluation/fixtures/smoke/policy_denial_smoke_case.json
tools/agentx_evolve/evaluation/fixtures/regression/default_regression_suite.json
tools/agentx_evolve/evaluation/fixtures/regression/invalid_tool_regression_case.json
tools/agentx_evolve/evaluation/fixtures/regression/blocked_write_regression_case.json
tools/agentx_evolve/evaluation/fixtures/negative/malformed_case.json
tools/agentx_evolve/evaluation/fixtures/negative/missing_expected_result_case.json
tools/agentx_evolve/evaluation/fixtures/baselines/default_regression_baseline.json
```

## 7.3 Test Files

```text
tools/agentx_evolve/tests/test_evaluation_models.py
tools/agentx_evolve/tests/test_evaluation_errors.py
tools/agentx_evolve/tests/test_path_guards.py
tools/agentx_evolve/tests/test_benchmark_loader.py
tools/agentx_evolve/tests/test_fixture_validator.py
tools/agentx_evolve/tests/test_case_executor.py
tools/agentx_evolve/tests/test_comparator_engine.py
tools/agentx_evolve/tests/test_evaluation_runner.py
tools/agentx_evolve/tests/test_score_calculator.py
tools/agentx_evolve/tests/test_threshold_checker.py
tools/agentx_evolve/tests/test_regression_comparator.py
tools/agentx_evolve/tests/test_baseline_manager.py
tools/agentx_evolve/tests/test_report_writer.py
tools/agentx_evolve/tests/test_evaluation_evidence.py
tools/agentx_evolve/tests/test_evaluation_schema_validation.py
tools/agentx_evolve/tests/test_evaluation_negative_cases.py
tools/agentx_evolve/tests/test_evaluation_tool_adapter_integration.py
tools/agentx_evolve/tests/test_evaluation_run_config.py
tools/agentx_evolve/tests/test_evaluation_fixture_lock.py
tools/agentx_evolve/tests/test_evaluation_mutation_guard.py
tools/agentx_evolve/tests/test_evaluation_determinism.py
tools/agentx_evolve/tests/test_evaluation_report_parity.py
tools/agentx_evolve/tests/test_evaluation_evidence_finalization.py
tools/agentx_evolve/tests/test_evaluation_baseline_compatibility.py
```

---

# 8. Schemas to Create

Create these schema files:

```text
tools/agentx_evolve/schemas/evaluation_benchmark_suite.schema.json
tools/agentx_evolve/schemas/evaluation_benchmark_case.schema.json
tools/agentx_evolve/schemas/evaluation_case_input.schema.json
tools/agentx_evolve/schemas/evaluation_expected_result.schema.json
tools/agentx_evolve/schemas/evaluation_case_result.schema.json
tools/agentx_evolve/schemas/evaluation_run.schema.json
tools/agentx_evolve/schemas/evaluation_score.schema.json
tools/agentx_evolve/schemas/evaluation_threshold.schema.json
tools/agentx_evolve/schemas/evaluation_regression_comparison.schema.json
tools/agentx_evolve/schemas/evaluation_report.schema.json
tools/agentx_evolve/schemas/evaluation_evidence_manifest.schema.json
tools/agentx_evolve/schemas/evaluation_completion_record.schema.json
tools/agentx_evolve/schemas/evaluation_baseline.schema.json
tools/agentx_evolve/schemas/evaluation_comparator.schema.json
tools/agentx_evolve/schemas/evaluation_run_config.schema.json
tools/agentx_evolve/schemas/evaluation_fixture_lock.schema.json
tools/agentx_evolve/schemas/evaluation_evidence_index.schema.json
```

## 8.1 General Schema Rules

Each schema must:

```text
require schema_version
require schema_id
require source_component where applicable
require warnings
require errors
reject missing required fields
reject unknown status values
reject unknown case_type values
reject unknown result types
reject unknown threshold operators
reject unknown comparator types
support evidence_refs
support artifact_refs
support deterministic IDs
set additionalProperties deliberately, not accidentally
```

For safety-critical schemas, use:

```text
additionalProperties: false
```

Allowed flexible objects:

```text
input_payload
observed_result
expected_result.data
report metadata
```

Flexible fields must still be bounded and must not allow executable code.

## 8.2 Required Status Enums

```text
EVAL_PASS
EVAL_FAIL
EVAL_BLOCKED
EVAL_ERROR
EVAL_SKIPPED
REGRESSION_PASS
REGRESSION_FAIL
REGRESSION_BASELINE_MISSING
REGRESSION_NOT_APPLICABLE
THRESHOLD_PASS
THRESHOLD_FAIL
```

## 8.3 Required Case Types

```text
STATIC_EXPECTED_RESULT
TOOL_CALL_EXPECTED_RESULT
POLICY_DENIAL_EXPECTED_RESULT
REGRESSION_EXPECTED_FAILURE
ARTIFACT_EXPECTED_RESULT
REPORT_GENERATION_EXPECTED_RESULT
NEGATIVE_FIXTURE_VALIDATION
```

## 8.4 Required Comparator Enums

```text
EXACT_MATCH
CONTAINS
REGEX_MATCH
STATUS_MATCH
FAILURE_CLASS_MATCH
ARTIFACT_EXISTS
NUMERIC_EQUALS
NUMERIC_AT_LEAST
NUMERIC_AT_MOST
LIST_CONTAINS
DICT_HAS_KEY
CUSTOM_STATIC_CHECK
```

No dynamic Python execution is allowed for custom checks in v1.

## 8.5 Schema Example Requirement

For every schema, create at least one valid example and at least two invalid examples in tests.

Required valid examples:

```text
valid_benchmark_suite
valid_benchmark_case_static
valid_benchmark_case_tool_call
valid_case_input
valid_expected_result
valid_case_result_pass
valid_case_result_fail
valid_evaluation_run
valid_evaluation_score
valid_threshold
valid_regression_comparison
valid_evaluation_report
valid_evidence_manifest
valid_completion_record
valid_baseline
valid_comparator
```

Required invalid examples:

```text
missing required id
invalid enum value
invalid threshold number
path traversal case_ref
unknown comparator type
missing expected_result
invalid baseline schema
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
unsafe path field fails where applicable
```

---

# 9. Classes and Dataclasses

Implement these dataclasses in:

```text
tools/agentx_evolve/evaluation/evaluation_models.py
```

## 9.1 `BenchmarkSuite`

Fields:

```python
schema_version: str
schema_id: str
suite_id: str
suite_name: str
description: str
created_at: str
source_component: str
case_refs: list[str]
default_threshold_id: str | None
baseline_ref: str | None
first_run_allowed: bool
tags: list[str]
warnings: list[str]
errors: list[str]
```

## 9.2 `BenchmarkCase`

Fields:

```python
schema_version: str
schema_id: str
case_id: str
case_name: str
description: str
case_type: str
target_component: str
severity: str
weight: float
input_ref: str | None
input_payload: dict
expected_result: dict
threshold_id: str | None
timeout_seconds: int
tags: list[str]
warnings: list[str]
errors: list[str]
```

## 9.3 `EvaluationCaseInput`

Fields:

```python
schema_version: str
schema_id: str
input_id: str
source_component: str
input_type: str
payload: dict
artifact_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 9.4 `EvaluationExpectedResult`

Fields:

```python
schema_version: str
schema_id: str
expected_result_id: str
expected_status: str
expected_failure_class: str | None
comparators: list[dict]
required_artifacts: list[str]
minimum_score: float | None
warnings: list[str]
errors: list[str]
```

## 9.5 `EvaluationCaseResult`

Fields:

```python
schema_version: str
schema_id: str
case_result_id: str
case_id: str
run_id: str
timestamp: str
status: str
score: float
max_score: float
weight: float
weighted_score: float
passed: bool
message: str
observed_result: dict
expected_result: dict
comparison_details: list[dict]
failure_class: str | None
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 9.6 `EvaluationRun`

Fields:

```python
schema_version: str
schema_id: str
run_id: str
suite_id: str
timestamp: str
source_component: str
repo_commit: str | None
runner_version: str
execution_mode: str
case_results: list[EvaluationCaseResult]
score_summary: dict
threshold_summary: dict
regression_summary: dict | None
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 9.7 `EvaluationScore`

Fields:

```python
schema_version: str
schema_id: str
score_id: str
run_id: str
total_cases: int
passed_cases: int
failed_cases: int
blocked_cases: int
error_cases: int
skipped_cases: int
raw_score: float
normalized_score: float
weighted_score: float
pass_rate: float
failure_rate: float
blocked_rate: float
error_rate: float
warnings: list[str]
errors: list[str]
```

## 9.8 `EvaluationThreshold`

Fields:

```python
schema_version: str
schema_id: str
threshold_id: str
minimum_pass_rate: float
minimum_weighted_score: float
maximum_regression_count: int
maximum_error_count: int
maximum_blocked_count: int
allow_blocked_cases: bool
allow_error_cases: bool
required_case_ids: list[str]
allowed_score_delta: float
warnings: list[str]
errors: list[str]
```

## 9.9 `RegressionComparison`

Fields:

```python
schema_version: str
schema_id: str
comparison_id: str
current_run_id: str
baseline_run_id: str | None
timestamp: str
status: str
score_delta: float
weighted_score_delta: float
new_failures: list[str]
fixed_failures: list[str]
unchanged_failures: list[str]
new_blocked_cases: list[str]
new_error_cases: list[str]
regression_count: int
improvement_count: int
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 9.10 `EvaluationReport`

Fields:

```python
schema_version: str
schema_id: str
report_id: str
run_id: str
suite_id: str
timestamp: str
status: str
summary: str
score_summary: dict
threshold_summary: dict
regression_summary: dict | None
case_summaries: list[dict]
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 9.11 `EvaluationBaseline`

Fields:

```python
schema_version: str
schema_id: str
baseline_id: str
suite_id: str
baseline_run_id: str
baseline_commit: str | None
created_at: str
source_component: str
score_summary: dict
case_result_index: dict
artifact_refs: list[str]
evidence_refs: list[str]
sha256: str | None
warnings: list[str]
errors: list[str]
```

## 9.12 Helper Functions

```python
utc_now_iso() -> str
new_eval_id(prefix: str) -> str
stable_json_hash(payload: dict) -> str
to_dict(obj: object) -> dict
```

---

# 10. Required Functions

## 10.1 `path_guards.py`

Required public functions:

```python
resolve_inside_root(path: Path, root: Path) -> Path
ensure_inside_root(path: Path, root: Path) -> None
reject_path_traversal(path_text: str) -> None
safe_relative_ref(path: Path, root: Path) -> str
```

Rules:

```text
reject absolute paths in fixture refs
reject .. traversal
reject symlink escape when resolvable
reject writing outside .agentx-init/evaluation/
```

## 10.2 `benchmark_loader.py`

Required public functions:

```python
load_benchmark_suite(path: Path) -> BenchmarkSuite
load_benchmark_case(path: Path) -> BenchmarkCase
load_benchmark_cases(suite: BenchmarkSuite, fixture_root: Path) -> list[BenchmarkCase]
load_threshold(path: Path) -> EvaluationThreshold
resolve_case_refs(suite: BenchmarkSuite, fixture_root: Path) -> list[Path]
```

Rules:

```text
load only local fixture files
reject path traversal
reject missing case files
reject schema-invalid suites
reject schema-invalid cases
preserve fixture order for deterministic runs
```

## 10.3 `fixture_validator.py`

Required public functions:

```python
validate_benchmark_suite(suite: dict) -> tuple[bool, list[str]]
validate_benchmark_case(case: dict) -> tuple[bool, list[str]]
validate_expected_result(expected: dict) -> tuple[bool, list[str]]
validate_threshold(threshold: dict) -> tuple[bool, list[str]]
validate_baseline(baseline: dict) -> tuple[bool, list[str]]
validate_fixture_tree(fixture_root: Path) -> dict
```

Rules:

```text
schema-invalid fixtures fail before evaluation
malformed expected results fail before evaluation
unknown comparator types fail before evaluation
unsafe paths fail before evaluation
fixture validation writes evidence during full evaluation runs
```

## 10.4 `comparator_engine.py`

Required public functions:

```python
compare_observed_to_expected(observed: dict, expected: EvaluationExpectedResult) -> list[dict]
resolve_json_path(payload: dict, path: str) -> object
run_comparator(comparator: dict, observed: dict) -> dict
```

Comparator path rules:

```text
paths use dotted JSON path only, for example status or data.failure_class
paths must not execute code
paths must not access filesystem
missing path returns comparator failure, not exception
regex must use bounded input strings
CUSTOM_STATIC_CHECK may only use named built-in static checks
```

Allowed static checks:

```text
IS_SCHEMA_VALID_TOOL_RESULT
IS_SCHEMA_VALID_EVALUATION_RESULT
HAS_EVIDENCE_REFS
HAS_ARTIFACT_REFS
IS_REDACTED
```

Forbidden:

```text
eval
exec
importlib
runtime Python from fixtures
shell commands from fixtures
network calls from fixtures
```

## 10.5 `case_executor.py`

Required public functions:

```python
execute_benchmark_case(
    case: BenchmarkCase,
    repo_root: Path,
    policy_context: dict | None = None,
    dry_run: bool = False,
) -> EvaluationCaseResult

execute_static_case(case: BenchmarkCase, repo_root: Path) -> EvaluationCaseResult
execute_tool_call_case(case: BenchmarkCase, repo_root: Path, policy_context: dict | None) -> EvaluationCaseResult
execute_negative_fixture_case(case: BenchmarkCase, repo_root: Path) -> EvaluationCaseResult
```

Rules:

```text
static cases never call tool adapter
tool cases call Tool / MCP Adapter dispatcher only
negative fixture cases validate rejection behavior
every case result must be schema-valid
every failed case result must include failure_class
```

## 10.6 `evaluation_runner.py`

Required public functions:

```python
run_benchmark_suite(
    suite_path: Path,
    repo_root: Path,
    baseline_path: Path | None = None,
    policy_context: dict | None = None,
    dry_run: bool = False,
    first_run: bool = False,
) -> EvaluationRun

run_benchmark_case(
    case: BenchmarkCase,
    repo_root: Path,
    policy_context: dict | None = None,
    dry_run: bool = False,
) -> EvaluationCaseResult
```

Required behavior:

```text
load suite
validate suite
load cases
validate cases
execute each case deterministically
calculate per-case result
calculate run score
check thresholds
compare baseline if provided
write run artifact
write evidence
write report
return EvaluationRun
```

Must not:

```text
use network
call hosted model
mutate source files
execute raw shell
write artifacts outside .agentx-init/evaluation/
ignore invalid fixtures
continue silently after schema-invalid suite
```

## 10.7 `score_calculator.py`

Required public functions:

```python
calculate_case_score(case: BenchmarkCase, observed_result: dict) -> EvaluationCaseResult
calculate_run_score(case_results: list[EvaluationCaseResult]) -> EvaluationScore
normalize_score(raw_score: float, max_score: float) -> float
calculate_weighted_score(case_results: list[EvaluationCaseResult]) -> float
```

Rules:

```text
scores must be deterministic
no floating randomization
failed required case scores 0
blocked case handling must be explicit
skipped case handling must be explicit
score details must be recorded per case
negative weight rejected
NaN rejected
Infinity rejected
```

## 10.8 `threshold_checker.py`

Required public functions:

```python
check_thresholds(
    score: EvaluationScore,
    threshold: EvaluationThreshold,
    case_results: list[EvaluationCaseResult],
    regression_comparison: RegressionComparison | None = None,
) -> dict

check_required_cases(case_results: list[EvaluationCaseResult], required_case_ids: list[str]) -> dict
```

Rules:

```text
minimum pass rate must be enforced
minimum weighted score must be enforced
maximum regression count must be enforced
maximum error count must be enforced
maximum blocked count must be enforced
required case IDs must pass
error cases fail unless explicitly allowed
blocked cases fail unless explicitly allowed
```

## 10.9 `regression_comparator.py`

Required public functions:

```python
compare_against_baseline(
    current_run: EvaluationRun,
    baseline_run: EvaluationRun | None,
    first_run: bool = False,
) -> RegressionComparison

load_baseline_run(path: Path) -> EvaluationRun
find_new_failures(current: EvaluationRun, baseline: EvaluationRun) -> list[str]
find_fixed_failures(current: EvaluationRun, baseline: EvaluationRun) -> list[str]
calculate_score_delta(current: EvaluationRun, baseline: EvaluationRun) -> dict
```

Rules:

```text
missing baseline is allowed only for explicit first-run mode
missing baseline must be recorded as warning
new failed required case is regression
score decrease below allowed delta is regression
case ID matching must be deterministic
baseline file must be schema-valid
```

## 10.10 `baseline_manager.py`

Required public functions:

```python
load_baseline(path: Path) -> EvaluationBaseline
write_candidate_baseline(run: EvaluationRun, repo_root: Path) -> Path
verify_baseline_hash(baseline: EvaluationBaseline, path: Path) -> bool
```

Rules:

```text
baseline updates must not occur automatically during normal evaluation
baseline artifacts are immutable once used for comparison
baseline hash must be recorded
baseline replacement requires explicit future promotion/review workflow
```

## 10.11 `report_writer.py`

Required public functions:

```python
write_evaluation_report(run: EvaluationRun, repo_root: Path) -> dict
write_evaluation_report_json(report: EvaluationReport, repo_root: Path) -> Path
write_evaluation_report_md(report: EvaluationReport, repo_root: Path) -> Path
write_latest_evaluation_run(run: EvaluationRun, repo_root: Path) -> Path
```

Required outputs:

```text
.agentx-init/evaluation/reports/<run_id>_evaluation_report.json
.agentx-init/evaluation/reports/<run_id>_evaluation_report.md
.agentx-init/evaluation/latest/latest_evaluation_run.json
.agentx-init/evaluation/latest/latest_evaluation_report.json
```

Report must include:

```text
run ID
suite ID
timestamp
commit, if available
execution mode
total cases
passed cases
failed cases
blocked cases
error cases
score
threshold result
regression result
case summaries
evidence refs
artifact refs
warnings
errors
final verdict
```

## 10.12 `evaluation_evidence.py`

Required public functions:

```python
write_evaluation_evidence_manifest(run: EvaluationRun, repo_root: Path) -> dict
append_evaluation_run_history(run: EvaluationRun, repo_root: Path) -> dict
append_evaluation_case_history(case_result: EvaluationCaseResult, repo_root: Path) -> dict
write_run_artifact(run: EvaluationRun, repo_root: Path) -> Path
write_completion_record(run: EvaluationRun, repo_root: Path) -> dict
hash_evidence_file(path: Path) -> str
```

Required outputs:

```text
.agentx-init/evaluation/evaluation_run_history.jsonl
.agentx-init/evaluation/evaluation_case_history.jsonl
.agentx-init/evaluation/evaluation_evidence_manifest.json
.agentx-init/evaluation/evaluation_completion_record.json
.agentx-init/evaluation/runs/<run_id>_run.json
```

Rules:

```text
append JSONL histories
write latest artifacts atomically
write SHA-256 hashes for final artifacts
record reviewed commit where available
redact secrets before durable logs
never log raw prompt/model outputs unless explicitly fixture-safe
```

## 10.13 `evaluation_errors.py`

Required constants:

```python
EVAL_FIXTURE_INVALID = "EVAL_FIXTURE_INVALID"
EVAL_SUITE_NOT_FOUND = "EVAL_SUITE_NOT_FOUND"
EVAL_CASE_NOT_FOUND = "EVAL_CASE_NOT_FOUND"
EVAL_CASE_FAILED = "EVAL_CASE_FAILED"
EVAL_THRESHOLD_FAILED = "EVAL_THRESHOLD_FAILED"
EVAL_REGRESSION_DETECTED = "EVAL_REGRESSION_DETECTED"
EVAL_BASELINE_MISSING = "EVAL_BASELINE_MISSING"
EVAL_BASELINE_INVALID = "EVAL_BASELINE_INVALID"
EVAL_POLICY_DENIED = "EVAL_POLICY_DENIED"
EVAL_TOOL_ADAPTER_UNAVAILABLE = "EVAL_TOOL_ADAPTER_UNAVAILABLE"
EVAL_TOOL_CALL_BLOCKED = "EVAL_TOOL_CALL_BLOCKED"
EVAL_REPORT_WRITE_FAILED = "EVAL_REPORT_WRITE_FAILED"
EVAL_EVIDENCE_WRITE_FAILED = "EVAL_EVIDENCE_WRITE_FAILED"
EVAL_SOURCE_MUTATION_DETECTED = "EVAL_SOURCE_MUTATION_DETECTED"
EVAL_UNKNOWN_FAILURE = "EVAL_UNKNOWN_FAILURE"
```

---


## 10.14 `run_config.py`

Required public functions:

```python
load_run_config(path: Path | None, repo_root: Path) -> dict
validate_run_config(config: dict) -> tuple[bool, list[str]]
merge_run_config_defaults(config: dict) -> dict
normalize_execution_mode(config: dict) -> str
```

Required run configuration fields:

```text
run_config_id
suite_path
execution_mode
baseline_path
first_run
case_filter
include_tags
exclude_tags
policy_context_ref
dry_run
timeout_seconds
max_case_count
write_reports
write_evidence
allow_tool_adapter_cases
allow_candidate_baseline_write
```

Rules:

```text
run config must be schema-valid before evaluation starts
case_filter and tag filters must be recorded in EvaluationRun
filtered runs are not valid for full-suite regression sign-off unless explicitly marked partial
first_run must be explicit; missing baseline must not silently become first-run
candidate baseline writing must be explicitly enabled
```

## 10.15 `fixture_lock.py`

Required public functions:

```python
build_fixture_lock(fixture_root: Path, suite_path: Path) -> dict
verify_fixture_lock(lock: dict, fixture_root: Path) -> tuple[bool, list[str]]
hash_fixture_file(path: Path) -> str
write_fixture_lock_candidate(lock: dict, repo_root: Path) -> Path
```

Required lock content:

```text
suite_id
suite_path
case_refs
case_hashes
baseline_ref
baseline_hash
threshold_refs
threshold_hashes
created_at
source_component
```

Rules:

```text
fixture hashes must be deterministic SHA-256 hashes
fixture lock candidate writes go under .agentx-init/evaluation/evidence/ unless future promotion accepts them
normal evaluation must not rewrite committed fixture locks or committed baselines
changed fixture hash must be recorded as fixture drift
fixture drift blocks full regression sign-off unless expected and recorded
```

## 10.16 `mutation_guard.py`

Required public functions:

```python
capture_source_state(repo_root: Path) -> dict
compare_source_state(before: dict, after: dict, allowed_runtime_root: Path) -> dict
assert_no_source_mutation(before: dict, after: dict, allowed_runtime_root: Path) -> None
```

Rules:

```text
prefer git status when repository metadata is available
fallback to hashing known source roots when git is unavailable
ignore approved runtime artifacts under .agentx-init/evaluation/
flag fixture rewrites, schema rewrites, source rewrites, and baseline rewrites
source mutation failure maps to EVAL_SOURCE_MUTATION_DETECTED
```

# 11. Runtime Artifacts

Runtime artifacts must be written under:

```text
.agentx-init/evaluation/
```

Required artifacts:

```text
.agentx-init/evaluation/evaluation_run_history.jsonl
.agentx-init/evaluation/evaluation_case_history.jsonl
.agentx-init/evaluation/evaluation_evidence_manifest.json
.agentx-init/evaluation/evaluation_completion_record.json
.agentx-init/evaluation/latest/latest_evaluation_run.json
.agentx-init/evaluation/latest/latest_evaluation_report.json
.agentx-init/evaluation/reports/<run_id>_evaluation_report.json
.agentx-init/evaluation/reports/<run_id>_evaluation_report.md
.agentx-init/evaluation/runs/<run_id>_run.json
```

Optional baseline artifacts:

```text
.agentx-init/evaluation/baselines/<suite_id>_candidate_baseline.json
```

Committed fixture baseline artifacts:

```text
tools/agentx_evolve/evaluation/fixtures/baselines/<suite_id>_baseline.json
```

Rules:

```text
runtime artifacts must not modify source files
history files are append-only JSONL
latest files are atomic JSON writes
reports are generated from schema-valid run data
SHA-256 hashes are required for final evidence files
runtime artifacts outside .agentx-init/evaluation/ require explicit deviation
```

---

# 12. Benchmark Fixture Layout

Benchmark fixtures are committed, deterministic, and local.

Required layout:

```text
tools/agentx_evolve/evaluation/fixtures/
  smoke/
    smoke_suite.json
    tool_registry_smoke_case.json
    policy_denial_smoke_case.json
  regression/
    default_regression_suite.json
    invalid_tool_regression_case.json
    blocked_write_regression_case.json
  negative/
    malformed_case.json
    missing_expected_result_case.json
  baselines/
    default_regression_baseline.json
```

## 12.1 Benchmark Suite Shape

```json
{
  "schema_version": "1.0",
  "schema_id": "evaluation_benchmark_suite.schema.json",
  "suite_id": "smoke_suite",
  "suite_name": "Evaluation Harness Smoke Suite",
  "description": "Minimal deterministic smoke suite.",
  "created_at": "<UTC timestamp>",
  "source_component": "EvaluationHarness",
  "case_refs": [
    "tool_registry_smoke_case.json",
    "policy_denial_smoke_case.json"
  ],
  "default_threshold_id": "default_smoke_threshold",
  "baseline_ref": null,
  "first_run_allowed": true,
  "tags": ["smoke", "offline"],
  "warnings": [],
  "errors": []
}
```

## 12.2 Benchmark Case Shape

```json
{
  "schema_version": "1.0",
  "schema_id": "evaluation_benchmark_case.schema.json",
  "case_id": "invalid_tool_regression_case",
  "case_name": "Invalid tool returns INVALID",
  "description": "Unknown tool calls must fail closed.",
  "case_type": "TOOL_CALL_EXPECTED_RESULT",
  "target_component": "AGENTX_TOOL_MCP_ADAPTER",
  "severity": "critical",
  "weight": 3.0,
  "input_ref": null,
  "input_payload": {
    "tool_name": "unknown_tool",
    "caller_role": "ORCHESTRATOR",
    "requested_effect": "READ",
    "arguments": {}
  },
  "expected_result": {
    "expected_status": "INVALID",
    "expected_failure_class": "TOOL_NOT_FOUND",
    "comparators": [
      {
        "type": "STATUS_MATCH",
        "path": "status",
        "expected": "INVALID"
      }
    ],
    "required_artifacts": []
  },
  "threshold_id": null,
  "timeout_seconds": 30,
  "tags": ["regression", "tool", "fail-closed"],
  "warnings": [],
  "errors": []
}
```

## 12.3 Fixture Rules

```text
fixtures must be static local JSON
fixtures must not depend on current date except generated run timestamp
fixtures must not require network
fixtures must not require model inference
fixtures must not require GPU
fixtures must not mutate source
fixtures must not call Git write operations
fixtures must not contain executable Python
fixtures must not contain shell snippets intended for execution
negative fixtures must be used only in validation tests, not normal pass suites
```

---

# 13. Evaluation Runner

The evaluation runner is the main orchestrator for this layer.

Required flow:

```text
1. Receive suite path.
2. Validate suite path is inside approved fixture root or explicit local path.
3. Load benchmark suite.
4. Validate benchmark suite schema.
5. Resolve case refs deterministically.
6. Load benchmark cases.
7. Validate each benchmark case schema.
8. Validate baseline if provided.
9. Run each benchmark case.
10. Compare observed result against expected result.
11. Produce per-case EvaluationCaseResult.
12. Calculate run score.
13. Load or resolve threshold.
14. Check thresholds.
15. Compare current run against baseline.
16. Write run artifact.
17. Write report artifacts.
18. Write evidence manifest.
19. Write latest artifacts.
20. Return EvaluationRun.
```

Fail-closed behavior:

```text
invalid suite -> EVAL_BLOCKED / EVAL_FIXTURE_INVALID
invalid case -> EVAL_BLOCKED / EVAL_FIXTURE_INVALID
missing case file -> EVAL_BLOCKED / EVAL_CASE_NOT_FOUND
missing baseline outside explicit first-run mode -> EVAL_BLOCKED / EVAL_BASELINE_MISSING
invalid baseline -> EVAL_BLOCKED / EVAL_BASELINE_INVALID
threshold failure -> EVAL_FAIL / EVAL_THRESHOLD_FAILED
regression detected -> EVAL_FAIL / EVAL_REGRESSION_DETECTED
report write failure -> EVAL_ERROR / EVAL_REPORT_WRITE_FAILED
evidence write failure -> EVAL_ERROR / EVAL_EVIDENCE_WRITE_FAILED
source mutation detected -> EVAL_ERROR / EVAL_SOURCE_MUTATION_DETECTED
unknown failure -> EVAL_ERROR / EVAL_UNKNOWN_FAILURE
```

---

# 14. Case-Type Behavior Table

| Case Type | Purpose | Allowed execution | Required pass condition |
|---|---|---|---|
| `STATIC_EXPECTED_RESULT` | Compare static observed payload to expected result. | Local comparison only. | All comparators pass. |
| `TOOL_CALL_EXPECTED_RESULT` | Verify Tool / MCP Adapter behavior. | Dispatcher only. | ToolResult matches expected status/failure_class/comparators. |
| `POLICY_DENIAL_EXPECTED_RESULT` | Verify policy denial is enforced. | Dispatcher with restrictive policy. | BLOCKED result with policy-denial failure class. |
| `REGRESSION_EXPECTED_FAILURE` | Verify known regression is detected in comparator. | Local baseline comparison. | RegressionComparison records expected new failure. |
| `ARTIFACT_EXPECTED_RESULT` | Verify required artifact exists under allowed runtime root. | Local artifact check only. | Required artifact exists and is inside root. |
| `REPORT_GENERATION_EXPECTED_RESULT` | Verify report writer output. | Local report writer. | JSON and MD reports written under runtime root. |
| `NEGATIVE_FIXTURE_VALIDATION` | Verify malformed fixtures are rejected. | Validator only. | Fixture fails with expected failure class. |

---

# 15. Regression Comparator

The regression comparator compares current results against an immutable baseline.

Required comparison dimensions:

```text
case status changes
case score changes
new failed cases
fixed failed cases
unchanged failed cases
new blocked cases
new error cases
total score delta
weighted score delta
required case regressions
threshold regressions
```

Regression rules:

```text
PASS -> FAIL is regression
PASS -> BLOCKED is regression unless explicitly accepted
PASS -> ERROR is regression
FAIL -> PASS is improvement
BLOCKED -> PASS may be improvement if the case was expected to pass
missing required case is regression
score decrease below allowed delta is regression
new failure_class is regression unless expected
new blocked required case is regression
new error required case is regression
```

Missing baseline behavior:

```text
allowed only in explicit first-run mode
record warning
regression status becomes REGRESSION_BASELINE_MISSING or REGRESSION_NOT_APPLICABLE
threshold checks still run
final DONE for implementation tests may allow first-run smoke but not untracked regression baselines
```

---

# 16. Baseline Immutability and Provenance

Baselines are safety artifacts.

Rules:

```text
normal evaluation must not overwrite baselines
candidate baseline may be written only under .agentx-init/evaluation/baselines/
committed fixture baselines live under tools/agentx_evolve/evaluation/fixtures/baselines/
baseline file hash must be recorded in evidence manifest
baseline commit, run_id, suite_id, and timestamp must be recorded
baseline replacement requires future promotion/review workflow
```

A regression comparison is invalid if:

```text
baseline schema is invalid
baseline suite_id differs from current suite_id
baseline case IDs cannot be matched deterministically
baseline hash is missing where required
baseline was overwritten during the run
```

---

# 17. Score Calculator

The score calculator must be deterministic.

Required calculations:

```text
per-case score
raw run score
normalized run score
weighted run score
pass rate
failure rate
blocked rate
error rate
```

Default scoring:

```text
case pass = 1.0
case fail = 0.0
case blocked = 0.0 unless expected blocked
case error = 0.0
case skipped = excluded only if explicitly marked optional
```

Weighted scoring:

```text
critical case weight = 3.0
high case weight = 2.0
normal case weight = 1.0
optional case weight = 0.5
```

Rules:

```text
weights must be declared in fixtures or defaulted deterministically
missing weight defaults to normal
negative weights rejected
NaN rejected
Infinity rejected
score output must be JSON-serializable
```

---

# 18. Threshold Checker

Threshold checker decides if an evaluation run is acceptable.

Required default thresholds:

```text
minimum_pass_rate = 1.0 for smoke suite
minimum_weighted_score = 1.0 for smoke suite
maximum_regression_count = 0
maximum_error_count = 0
maximum_blocked_count = 0
allow_blocked_cases = false
allow_error_cases = false
required_case_ids must all pass
```

Required checks:

```text
pass rate >= minimum_pass_rate
weighted score >= minimum_weighted_score
regression_count <= maximum_regression_count
error_count <= maximum_error_count
blocked_count <= maximum_blocked_count
all required cases passed
blocked cases allowed only if threshold allows them
error cases allowed only if threshold allows them
```

Threshold failure must produce:

```text
status = EVAL_FAIL
failure_class = EVAL_THRESHOLD_FAILED
threshold_summary with exact failed checks
```

---

# 19. Report Writer

The report writer must produce both JSON and Markdown reports.

JSON report:

```text
schema-valid evaluation_report.schema.json
machine-readable
used by later promotion gates
```

Markdown report:

```text
human-readable
summarizes suite, cases, scores, thresholds, regressions, evidence
must not include secrets
must not include raw large outputs
```

Required report sections:

```text
Evaluation Summary
Suite Information
Run Information
Score Summary
Threshold Summary
Regression Summary
Case Results
Failures
Evidence Artifacts
Final Verdict
```

Final verdict values:

```text
PASS
FAIL
BLOCKED
ERROR
```

Report immutability rule:

```text
Once report hashes are recorded in the evidence manifest, the report files must not be modified.
If a report changes, a new run_id and new evidence manifest are required.
```

---

# 20. Evidence Manifest and Hashing

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
  "run_id": "<run_id>",
  "suite_id": "<suite_id>",
  "validated_commit": "<commit hash or null>",
  "validated_at": "<UTC timestamp>",
  "execution_mode": "OFFLINE_FIXTURE|CONTROLLED_TOOL_ADAPTER",
  "commands": [],
  "fixtures_used": [],
  "fixture_hashes": [],
  "baseline_used": null,
  "baseline_sha256": null,
  "runtime_artifacts": [],
  "runtime_artifact_hashes": [],
  "reports": [],
  "report_hashes": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "network_status": "NOT_USED",
  "tool_adapter_status": "PASS|BLOCKED|NOT_APPLICABLE",
  "policy_status": "PASS|BLOCKED|NOT_APPLICABLE",
  "failure_taxonomy_status": "PASS|LOCAL_FALLBACK",
  "final_decision": "PASS|FAIL|BLOCKED|ERROR"
}
```

Hashing rule:

```text
SHA-256 hashes are required for final reports, run artifacts, evidence manifest, and baseline if used.
Use Python standard library hashlib.
A final DONE verdict is invalid if required hashes are missing.
```

---

# 21. Integration with Tool / MCP Adapter

The Evaluation Harness may call Tool / MCP Adapter only through controlled interfaces.

Allowed integration:

```text
load default tool registry
execute dry-run tool calls
execute read-only or blocked-safety benchmark cases
validate ToolResult status and failure_class
verify invalid tools fail closed
verify blocked tools fail closed
```

Required behavior:

```text
all tool calls use Tool / MCP Adapter dispatcher
no wrapper is called directly except unit tests for the Tool Adapter layer itself
policy_context must be explicit
sandbox-required tool cases must not bypass sandbox
ToolResult evidence_refs must be preserved in EvaluationCaseResult
```

Forbidden behavior:

```text
no direct shell execution
no direct file mutation through evaluation cases
no MCP server startup
no network tool exposure
no Git write tool execution
no patch apply execution unless future benchmark explicitly runs in governed dry-run mode
```

If Tool / MCP Adapter is unavailable:

```text
Tool-dependent benchmark cases return EVAL_BLOCKED
pure fixture/schema/score tests still run
missing dependency is recorded in warnings/errors
```

---

# 22. Integration with Failure Taxonomy

The Evaluation Harness must map failures to standard failure classes.

Required mappings:

```text
invalid suite -> EVAL_FIXTURE_INVALID
invalid case -> EVAL_FIXTURE_INVALID
missing suite -> EVAL_SUITE_NOT_FOUND
missing case -> EVAL_CASE_NOT_FOUND
case mismatch -> EVAL_CASE_FAILED
threshold failure -> EVAL_THRESHOLD_FAILED
new regression -> EVAL_REGRESSION_DETECTED
missing baseline -> EVAL_BASELINE_MISSING
invalid baseline -> EVAL_BASELINE_INVALID
policy denial -> EVAL_POLICY_DENIED
tool adapter unavailable -> EVAL_TOOL_ADAPTER_UNAVAILABLE
tool call blocked -> EVAL_TOOL_CALL_BLOCKED
report write failure -> EVAL_REPORT_WRITE_FAILED
evidence write failure -> EVAL_EVIDENCE_WRITE_FAILED
source mutation detected -> EVAL_SOURCE_MUTATION_DETECTED
unknown exception -> EVAL_UNKNOWN_FAILURE
```

Rules:

```text
every failed EvaluationCaseResult must have failure_class
every failed EvaluationRun must have threshold or regression failure summary
unknown exceptions must be converted to schema-valid error results
no unhandled exception should escape normal runner calls except programming errors in tests
```

---

# 23. Integration with Policy / Capability Registry

Evaluation must respect policy.

Required behavior:

```text
evaluation runner receives policy_context
Tool / MCP Adapter benchmark calls pass policy_context through dispatcher
benchmark cases that require tool calls identify caller_role
policy-denied tool calls become expected BLOCKED results only if fixture expects them
policy unavailable blocks mutating or tool-execution cases
pure offline scoring/reporting may continue without policy
```

Policy rules:

```text
Evaluation Harness is read-only by default
Evaluation Harness may write runtime artifacts under .agentx-init/evaluation/
Evaluation Harness may not write source files
Evaluation Harness may not execute commands directly
Evaluation Harness may not call network
Evaluation Harness may not bypass sandbox/policy through test shortcuts
```

Recommended evaluation caller role:

```text
EVALUATION_RUNNER
```

If the Policy / Capability Registry does not yet define that role, use the nearest safe read-only role and record the deviation in evidence.

---

# 24. Resource Limits, Timeout, and Concurrency Rules

Required defaults:

```text
case timeout_seconds = 30
suite timeout_seconds = 300
max_case_count_per_suite = 100
max_report_size_chars = 200000
max_observed_result_chars = 50000
max_parallelism = 1 in v1
```

Rules:

```text
v1 runs cases sequentially for deterministic evidence ordering
no parallel execution unless a future contract adds lock/evidence ordering rules
case timeout produces EVAL_ERROR with EVAL_UNKNOWN_FAILURE or specific timeout class if added
large observed outputs are summarized before evidence/report writing
```

---

# 25. Source Mutation and Runtime Boundary Check

The implementation must prove it does not mutate source files.

Required checks:

```text
record git status before evaluation tests when available
record git status after evaluation tests when available
runtime writes must stay under .agentx-init/evaluation/
fixture files must not be rewritten during normal evaluation
baseline files under fixtures must not be rewritten during normal evaluation
```

Blocking if:

```text
source file modified during evaluation
fixture baseline overwritten during evaluation
runtime artifact written outside .agentx-init/evaluation/ without deviation
Tool Adapter wrapper called directly to mutate files
Git write command executed
```

---

# 26. Test Cases

Required tests:

```text
test_evaluation_models_instantiate
test_evaluation_errors_constants_exist
test_path_guards_reject_path_traversal
test_benchmark_suite_schema_accepts_valid_suite
test_benchmark_suite_schema_rejects_missing_suite_id
test_benchmark_case_schema_accepts_valid_case
test_benchmark_case_schema_rejects_missing_expected_result
test_schema_examples_cover_all_required_schemas
test_benchmark_loader_loads_smoke_suite
test_benchmark_loader_preserves_case_order
test_benchmark_loader_rejects_path_traversal
test_fixture_validator_detects_malformed_case
test_fixture_validator_rejects_unknown_comparator
test_comparator_engine_exact_match
test_comparator_engine_missing_path_fails_without_exception
test_comparator_engine_rejects_dynamic_custom_check
test_case_executor_static_case_passes
test_case_executor_tool_case_uses_dispatcher
test_evaluation_runner_runs_smoke_suite
test_evaluation_runner_blocks_invalid_suite
test_score_calculator_counts_pass_fail_blocked_error
test_score_calculator_rejects_invalid_weight
test_score_calculator_rejects_nan_and_infinity
test_threshold_checker_passes_valid_smoke_score
test_threshold_checker_fails_below_minimum_pass_rate
test_threshold_checker_fails_required_case_failure
test_regression_comparator_detects_new_failure
test_regression_comparator_detects_fixed_failure
test_regression_comparator_handles_missing_baseline_first_run
test_baseline_manager_rejects_invalid_baseline
test_baseline_manager_does_not_overwrite_baseline
test_report_writer_writes_json_report
test_report_writer_writes_markdown_report
test_report_writer_redacts_secret_like_values
test_evaluation_evidence_writes_jsonl_history
test_evaluation_evidence_writes_manifest_hashes
test_tool_adapter_integration_invalid_tool_case
test_tool_adapter_integration_blocked_write_case
test_policy_denial_case_is_recorded
test_evaluation_runner_does_not_mutate_source
test_evaluation_runner_requires_no_network
test_evaluation_schema_validation_all_required_schemas
```

---

# 27. Negative Test Cases

Required negative tests:

```text
malformed benchmark suite is rejected
malformed benchmark case is rejected
missing expected_result is rejected
unknown comparator type is rejected
path traversal case_ref is rejected
baseline with invalid schema is rejected
baseline suite_id mismatch is rejected
threshold with NaN is rejected
threshold with Infinity is rejected
negative case weight is rejected
tool-dependent case blocks when Tool Adapter unavailable
mutating tool case blocks without policy approval
report writer refuses to write outside runtime artifact root
secret-like payload is redacted in report/evidence
unknown runner exception becomes EVAL_UNKNOWN_FAILURE
fixture attempts to define dynamic Python check is rejected
fixture baseline is not overwritten by normal evaluation
```

Any failure of these negative tests is a blocker.

---

# 28. Implementation Order

Implement in this exact order:

```text
1. Create tools/agentx_evolve/evaluation/ package.
2. Create fixtures directories.
3. Implement evaluation_errors.py.
4. Implement evaluation_models.py.
5. Create evaluation schemas.
6. Implement path_guards.py.
7. Implement fixture_validator.py.
8. Implement benchmark_loader.py.
9. Implement comparator_engine.py.
10. Implement case_executor.py.
11. Implement score_calculator.py.
12. Implement threshold_checker.py.
13. Implement baseline_manager.py.
14. Implement regression_comparator.py.
15. Implement evaluation_evidence.py.
16. Implement report_writer.py.
17. Implement evaluation_runner.py.
18. Create smoke fixtures.
19. Create regression fixtures.
20. Create negative fixtures.
21. Create baseline fixture.
22. Create schema validation tests.
23. Create path/loader/validator tests.
24. Create comparator/case executor tests.
25. Create scoring/threshold/regression tests.
26. Create report/evidence tests.
27. Create Tool / MCP Adapter integration tests.
28. Run compileall.
29. Run pytest.
30. Verify git status.
31. Write completion record.
```

Do not reorder unless required by real import dependencies.

---

# 29. Acceptance Criteria

The layer is acceptable only if:

```text
all target files exist
all required schemas exist
all required fixtures exist
all required tests exist
benchmark suites load deterministically
schema-invalid fixtures fail before execution
path traversal refs fail
smoke suite runs without network, GPU, hosted model, or MCP server
score calculation is deterministic
threshold checking is deterministic
regression comparison detects new failures
baseline immutability is enforced
report writer produces JSON and Markdown reports
evidence manifest is written
SHA-256 hashes are written
runtime artifacts stay under .agentx-init/evaluation/
Tool / MCP Adapter integration uses dispatcher only
Policy / Capability Registry is respected
Failure Taxonomy mappings are present
compileall passes
pytest passes
git status is clean or only expected runtime artifacts
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
Git write access
```

---

# 30. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/evaluation
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_evaluation_models.py \
  tools/agentx_evolve/tests/test_evaluation_errors.py \
  tools/agentx_evolve/tests/test_path_guards.py \
  tools/agentx_evolve/tests/test_benchmark_loader.py \
  tools/agentx_evolve/tests/test_fixture_validator.py \
  tools/agentx_evolve/tests/test_comparator_engine.py \
  tools/agentx_evolve/tests/test_case_executor.py \
  tools/agentx_evolve/tests/test_evaluation_runner.py \
  tools/agentx_evolve/tests/test_score_calculator.py \
  tools/agentx_evolve/tests/test_threshold_checker.py \
  tools/agentx_evolve/tests/test_regression_comparator.py \
  tools/agentx_evolve/tests/test_baseline_manager.py \
  tools/agentx_evolve/tests/test_report_writer.py \
  tools/agentx_evolve/tests/test_evaluation_evidence.py \
  tools/agentx_evolve/tests/test_evaluation_schema_validation.py \
  tools/agentx_evolve/tests/test_evaluation_negative_cases.py \
  tools/agentx_evolve/tests/test_evaluation_tool_adapter_integration.py
tools/agentx_evolve/tests/test_evaluation_run_config.py
tools/agentx_evolve/tests/test_evaluation_fixture_lock.py
tools/agentx_evolve/tests/test_evaluation_mutation_guard.py
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected runtime artifacts
```

Optional full suite command:

```bash
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
```

---

# 31. Completion Evidence

After implementation, write:

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
  "canonical_subdirectory": "tools/agentx_evolve/evaluation/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "benchmark_fixture_root": "tools/agentx_evolve/evaluation/fixtures/",
  "runtime_artifact_root": ".agentx-init/evaluation/",
  "basis_documents": [
    "EVALUATION_HARNESS_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "EVALUATION_HARNESS_IMPLEMENTATION_SPEC_v3"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "fixtures_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "benchmark_suites_verified": [],
  "thresholds_verified": [],
  "regression_comparisons_verified": [],
  "baselines_verified": [],
  "reports_verified": [],
  "policy_integration_verified": [],
  "tool_adapter_integration_verified": [],
  "failure_taxonomy_integration_verified": [],
  "evidence_artifacts": [],
  "evidence_hashes": [],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

---

# 32. Definition of Done

The Evaluation Harness / Regression Benchmark Layer is done when it can reliably evaluate Agent_X behavior and detect regressions using deterministic local fixtures.

It must prove:

```text
all target files exist
all schemas exist
all fixtures exist
all tests exist
benchmark suites load deterministically
benchmark cases validate against schema
invalid fixtures fail closed
path traversal refs fail closed
smoke suite runs successfully
regression comparator detects new failures
baseline immutability is enforced
score calculator produces deterministic scores
threshold checker blocks unacceptable results
report writer creates JSON and Markdown reports
evidence manifest is written
evidence hashes are written
completion record is written
Tool / MCP Adapter integration is controlled and dispatcher-based
Policy / Capability Registry is respected
Failure Taxonomy mappings are present
runtime artifacts stay under .agentx-init/evaluation/
no source mutation occurs
no network is required
no raw shell is executed
no Git write operation is used
compileall passes
pytest passes
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/evaluation
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_evaluation_models.py \
  tools/agentx_evolve/tests/test_evaluation_errors.py \
  tools/agentx_evolve/tests/test_path_guards.py \
  tools/agentx_evolve/tests/test_benchmark_loader.py \
  tools/agentx_evolve/tests/test_fixture_validator.py \
  tools/agentx_evolve/tests/test_comparator_engine.py \
  tools/agentx_evolve/tests/test_case_executor.py \
  tools/agentx_evolve/tests/test_evaluation_runner.py \
  tools/agentx_evolve/tests/test_score_calculator.py \
  tools/agentx_evolve/tests/test_threshold_checker.py \
  tools/agentx_evolve/tests/test_regression_comparator.py \
  tools/agentx_evolve/tests/test_baseline_manager.py \
  tools/agentx_evolve/tests/test_report_writer.py \
  tools/agentx_evolve/tests/test_evaluation_evidence.py \
  tools/agentx_evolve/tests/test_evaluation_schema_validation.py \
  tools/agentx_evolve/tests/test_evaluation_negative_cases.py \
  tools/agentx_evolve/tests/test_evaluation_tool_adapter_integration.py
tools/agentx_evolve/tests/test_evaluation_run_config.py
tools/agentx_evolve/tests/test_evaluation_fixture_lock.py
tools/agentx_evolve/tests/test_evaluation_mutation_guard.py
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected runtime artifacts
```

---

# 33. Go / No-Go Rules

## 33.1 GO Criteria

The layer may be marked DONE only if:

```text
compileall passes
pytest passes
schemas validate
fixtures validate
smoke suite passes
negative tests pass
path traversal tests pass
comparator tests pass
score calculation tests pass
threshold tests pass
regression comparison tests pass
baseline immutability tests pass
report writer tests pass
evidence tests pass
Tool / MCP Adapter integration tests pass or are safely blocked with explicit unavailable dependency note
Policy integration is enforced for tool-dependent cases
Failure Taxonomy mappings exist
source mutation check passes
completion record exists
```

## 33.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema-invalid fixtures are accepted
path traversal fixture refs are accepted
benchmark runner mutates source files
benchmark runner uses network by default
raw shell is executed
Git write operation is executed
Tool / MCP Adapter is bypassed
policy checks are bypassed for tool-dependent cases
regressions are not detected
threshold failures are ignored
baselines are overwritten during normal evaluation
reports are missing
evidence is missing
hashes are missing
completion record is missing
```

---

# 34. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places evaluation files outside tools/agentx_evolve/evaluation/ without recorded deviation
writes runtime evidence outside .agentx-init/evaluation/ without recorded deviation
accepts invalid benchmark fixtures
executes arbitrary Python from fixtures
executes raw shell
uses network by default
requires hosted model or LLM for tests
starts MCP server
calls Tool / MCP Adapter wrappers directly instead of dispatcher
allows policy-denied tool benchmark to pass as allowed
fails to classify evaluation failures
logs secrets in reports or evidence
creates non-deterministic scores
ignores regression failures
marks threshold failure as PASS
overwrites baselines during normal evaluation
omits required evidence hashes
```

---

# 35. Final Frozen Acceptance Matrix

| Area | Required v2 behavior | DONE required? |
|---|---|---|
| Package layout | `tools/agentx_evolve/evaluation/` exists with required files | Yes |
| Schemas | All required schemas exist and validate valid/invalid examples | Yes |
| Fixtures | Smoke, regression, negative, and baseline fixtures exist | Yes |
| Loader | Loads fixtures deterministically and rejects traversal | Yes |
| Comparator | Uses safe static comparators only | Yes |
| Runner | Runs offline and controlled tool cases safely | Yes |
| Scoring | Deterministic score and weight handling | Yes |
| Thresholds | Blocks unacceptable results | Yes |
| Regression | Detects new failures and score regressions | Yes |
| Baselines | Immutable during normal evaluation | Yes |
| Reports | JSON and Markdown reports written under runtime root | Yes |
| Evidence | JSONL, manifest, hashes, completion record | Yes |
| Tool Adapter | Dispatcher-only integration | Yes for tool cases |
| Policy | Enforced for tool-dependent cases | Yes |
| Failure Taxonomy | Failure classes present for failed/blocked/error cases | Yes |
| Safety | No network, no raw shell, no source mutation, no Git write | Yes |

---

# 36. Final Coding-Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] The target repository is Agent_X.
[ ] The layer is Evaluation Harness / Regression Benchmark Layer.
[ ] The target package is tools/agentx_evolve/evaluation/.
[ ] Schemas go under tools/agentx_evolve/schemas/.
[ ] Tests go under tools/agentx_evolve/tests/.
[ ] Fixtures go under tools/agentx_evolve/evaluation/fixtures/.
[ ] Runtime artifacts go under .agentx-init/evaluation/.
[ ] Evaluation must be deterministic and offline by default.
[ ] No network, GPU, hosted model, LLM, Bun, Node, OpenCode runtime, or running MCP server is required.
[ ] Tool / MCP Adapter integration must use dispatcher only.
[ ] Policy / Capability Registry must be respected.
[ ] Failure Taxonomy mappings must be used.
[ ] Benchmark reports must be evidence-backed.
[ ] Regression failures must block DONE.
[ ] Threshold failures must block DONE.
[ ] Baselines must not be overwritten during normal evaluation.
[ ] Evidence hashes must be written.
```

---


# 37. v3 Production-Control Addendum

This section is mandatory. It closes the remaining handoff gaps from v2.

## 38.1 Run Configuration Contract

The implementation must create and validate:

```text
tools/agentx_evolve/schemas/evaluation_run_config.schema.json
```

Run configuration is required because a benchmark run must be reproducible from recorded inputs, not from hidden CLI flags or implicit defaults.

Required behavior:

```text
run config is validated before suite loading
all defaults are deterministic
execution_mode is recorded in EvaluationRun and Evidence Manifest
case/tag filters are recorded
first_run mode is explicit
candidate baseline writing is explicit
partial runs cannot be used as full regression pass evidence
```

## 38.2 Fixture Lock and Provenance Contract

The implementation must create and validate:

```text
tools/agentx_evolve/schemas/evaluation_fixture_lock.schema.json
```

The fixture lock records the exact benchmark inputs used for a run.

Required behavior:

```text
fixture files are hashed before execution
baseline file is hashed before comparison
threshold files are hashed before use
suite/case order is recorded
case_id collisions are rejected
fixture drift is recorded as warning or blocker depending on run mode
```

Full regression sign-off requires:

```text
fixture lock present
fixture hashes present
baseline hash present if baseline used
case order deterministic
no duplicate case_id
no unrecorded fixture drift
```

## 38.3 Environment Capture Contract

Every full evaluation run must record:

```text
OS name/version
Python version
pytest version when validation tests are run
repository commit when available
working tree start status when available
working tree end status when available
execution mode
policy mode
tool adapter mode
network status
```

If repository metadata is unavailable, record:

```text
repo_commit = null
repo_metadata_status = UNAVAILABLE
```

Do not invent commit hashes.

## 38.4 Comparator Precision Rules

Numeric comparators must define:

```text
operator
expected value
tolerance, default 0.0
allow_float_rounding, default false
```

Rules:

```text
NaN always invalid
Infinity always invalid
negative tolerance invalid
missing observed numeric path fails comparator
string numeric coercion is forbidden unless explicitly allowed by comparator config
```

Regex comparators must define:

```text
pattern
max_input_chars
flags from allowed list only
```

Rules:

```text
regex input must be truncated to max_input_chars before matching
catastrophic or invalid regex pattern returns comparator failure
regex flags are limited to IGNORECASE and MULTILINE in v1
fixtures cannot provide executable regex callbacks
```

## 38.5 Case Ordering and Filtering Rules

Required behavior:

```text
case_refs order from suite is preserved
resolved paths are normalized and recorded
case_id must be unique within suite
case filters must not reorder cases
include_tags/exclude_tags must be recorded in run config and report
filtered runs are marked PARTIAL unless full_suite=true
partial filtered runs cannot update or validate full-suite baseline
```

## 38.6 Baseline Promotion Boundary

This layer may write candidate baselines only.

Allowed:

```text
write candidate baseline under .agentx-init/evaluation/baselines/
hash candidate baseline
report candidate baseline path
```

Forbidden:

```text
overwrite committed fixture baseline during normal evaluation
promote candidate baseline to committed baseline
silently accept missing baseline as pass
use partial run as full baseline
```

Baseline promotion belongs to a future Promotion / Release Gate or human review workflow.

## 38.7 Partial Write Failure Rules

If evidence or report writing partially succeeds:

```text
record EVAL_EVIDENCE_WRITE_FAILED or EVAL_REPORT_WRITE_FAILED
mark final run ERROR unless only non-required Markdown report failed and JSON/evidence manifest succeeded
never mark PASS when required machine-readable evidence is missing
never mark PASS when hashes are missing
write a best-effort failure artifact only under .agentx-init/evaluation/
```

Required machine-readable artifacts for PASS:

```text
run JSON
JSON report
evidence manifest
completion record when implementation validation is finalized
hashes for all final evidence artifacts
```

## 38.8 Dedicated Schema Validation Utility

Create:

```text
tools/agentx_evolve/tests/validate_evaluation_schemas.py
```

or prove equivalent coverage in:

```text
tools/agentx_evolve/tests/test_evaluation_schema_validation.py
```

The validation utility or test must cover:

```text
all evaluation schemas
one valid example per schema
two invalid examples per schema
invalid enum rejection
unsafe path rejection where applicable
fixture lock validation
run config validation
completion record validation
```

## 38.9 Required v3 Additional Tests

Add these tests:

```text
test_run_config_requires_explicit_first_run_for_missing_baseline
test_run_config_records_case_filters
test_filtered_run_is_marked_partial
test_fixture_lock_hashes_suite_cases_thresholds_and_baseline
test_fixture_lock_rejects_case_id_collision
test_fixture_drift_blocks_full_regression_signoff
test_numeric_comparator_rejects_nan_infinity_and_negative_tolerance
test_numeric_comparator_applies_explicit_tolerance
test_regex_comparator_limits_input_and_rejects_invalid_flags
test_candidate_baseline_written_only_when_enabled
test_candidate_baseline_does_not_overwrite_committed_baseline
test_mutation_guard_detects_fixture_rewrite
test_partial_report_write_failure_marks_run_error_when_json_missing
test_schema_validation_utility_covers_run_config_and_fixture_lock
```

## 38.10 v3 Acceptance Delta

The v3 document is not considered satisfied unless these v3-specific additions are implemented:

```text
run_config.py implemented
fixture_lock.py implemented
mutation_guard.py implemented
evaluation_run_config.schema.json exists
evaluation_fixture_lock.schema.json exists
schema validation covers run config and fixture lock
case_id collisions rejected
filtered runs marked partial
fixture hashes recorded
baseline hashes recorded
numeric tolerance rules enforced
regex safety rules enforced
candidate baseline boundary enforced
partial write failure behavior tested
```

# 38. v3 Final Frozen Acceptance Matrix

| Area | Required v3 behavior | DONE required? |
|---|---|---|
| Run config | Explicit, schema-valid, recorded, deterministic defaults | Yes |
| Fixture lock | Suite/case/baseline/threshold hashes recorded | Yes |
| Environment | OS, Python, commit/status when available, execution mode recorded | Yes |
| Case ordering | Suite order preserved, duplicate case_id rejected | Yes |
| Filtering | Filtered runs marked partial and cannot validate full baseline | Yes |
| Comparator precision | Numeric tolerance and regex safety enforced | Yes |
| Baselines | Candidate write only; no committed overwrite | Yes |
| Mutation guard | Source/fixture/baseline rewrites detected | Yes |
| Partial write failures | Required missing machine evidence prevents PASS | Yes |
| Schema utility | All schemas including v3 schemas validated | Yes |

# 39. v4 Deterministic Handoff Addendum

This section is mandatory. It closes the remaining handoff-control gaps from v3.

## 39.1 Public Entrypoint Contract

The implementation must expose one stable programmatic entrypoint and one optional CLI-safe entrypoint.

Required programmatic entrypoint:

```python
def run_evaluation_from_config(
    config_path: Path,
    repo_root: Path,
) -> EvaluationRun:
    ...
```

Optional CLI entrypoint, if CLI support is added in this layer:

```bash
PYTHONPATH=tools python -m agentx_evolve.evaluation.run_evaluation --config <path>
```

Rules:

```text
all CLI arguments must be parsed into evaluation_run_config.schema.json
no hidden CLI-only behavior is allowed
no CLI flag may bypass schema validation
no CLI flag may enable network, source mutation, Git write, or baseline promotion
CLI output must reference the run_id, JSON report path, evidence manifest path, and final status
CLI exit_code 0 requires THRESHOLD_PASS or an explicitly accepted first-run status
CLI exit_code non-zero is required for schema failure, threshold failure, regression failure, evidence write failure, or source mutation detection
```

Acceptance tests:

```text
test_cli_config_path_required_if_cli_enabled
test_cli_cannot_enable_network_or_source_mutation
test_cli_exit_code_nonzero_on_threshold_fail
test_programmatic_entrypoint_returns_evaluation_run
```

## 39.2 Determinism Contract

Every full evaluation run must be deterministic for the same repo state, fixture lock, run config, and baseline.

Required deterministic controls:

```text
case order comes only from suite case_refs
case_id collisions are rejected before execution
random seed is recorded even if randomness is not used
clock values are limited to run metadata, not scoring logic
score calculation does not depend on wall-clock time
JSON output uses stable key ordering where hashes are calculated
filesystem traversal order is sorted before hashing
filtered runs preserve original suite order
```

Default values:

```text
random_seed: 0
parallel_execution: false
clock_for_scoring: forbidden
case_order: suite_order
hash_json_sort_keys: true
```

Forbidden:

```text
randomized case ordering
time-dependent scoring
filesystem iteration without sorting
implicit baseline selection by latest modified time
implicit fixture selection by glob order without sorting
```

Acceptance tests:

```text
test_same_config_fixture_and_baseline_produce_same_hashes
test_filesystem_hash_order_is_sorted
test_random_seed_recorded_and_stable
test_score_does_not_depend_on_timestamp
```

## 39.3 Tool-Adapter Execution Boundary

Tool-adapter cases must remain constrained by evaluation policy.

Default tool-case behavior:

```text
dry_run = true unless case explicitly requests read-only execution
read-only execution must still pass Tool / MCP Adapter policy checks
mutating tools must return EVAL_BLOCKED unless a future evaluation contract explicitly permits them
patch_apply_guarded must not execute
git write tools must not execute
network tools must not execute
MCP server must not start
```

Tool adapter results must be preserved as evidence, but evaluation reports must not durably store raw sensitive payloads.

Required mapping:

```text
ToolResult.status SUCCESS -> case comparator decides pass/fail
ToolResult.status BLOCKED -> EVAL_BLOCKED unless expected_result requires blocked behavior
ToolResult.status INVALID -> EVAL_PASS only for invalid-tool negative cases that expect INVALID
ToolResult.status FAILED -> EVAL_FAIL or EVAL_ERROR based on failure_class
missing ToolResult.evidence_refs -> warning or fail if evidence is required by case severity
```

Acceptance tests:

```text
test_tool_case_defaults_to_dry_run
test_tool_case_cannot_execute_mutating_tool
test_invalid_tool_negative_case_can_pass_when_invalid_expected
test_missing_tool_evidence_blocks_required_case
```

## 39.4 Baseline Compatibility and Schema-Version Rules

Baselines are immutable comparison inputs. They must also be schema-compatible with the current evaluator.

Rules:

```text
baseline schema_version must be validated before comparison
baseline suite_id must match current suite_id
baseline case IDs must be compared against current case IDs before scoring
missing baseline case for required current case is a regression unless first_run is explicit
extra baseline case is recorded as removed_case, not ignored silently
major baseline schema mismatch blocks comparison
minor additive schema fields may be ignored only if explicitly allowed by schema compatibility rules
no automatic migration of committed baselines in this layer
```

Required failure classes:

```text
EVAL_BASELINE_SCHEMA_INVALID
EVAL_BASELINE_SUITE_MISMATCH
EVAL_BASELINE_CASE_MISMATCH
EVAL_BASELINE_VERSION_UNSUPPORTED
```

Acceptance tests:

```text
test_baseline_suite_id_mismatch_blocks_comparison
test_baseline_major_schema_mismatch_blocks_comparison
test_missing_required_current_case_is_regression
test_extra_baseline_case_recorded_as_removed_case
```

## 39.5 Report Consistency Rule

The JSON report is authoritative. The Markdown report is a human-readable rendering of the JSON report.

Rules:

```text
JSON report must be written before Markdown report
Markdown report must be generated from the same in-memory EvaluationReport object
Markdown report must not contain a different final status than JSON
Markdown report must not omit blockers from JSON
Markdown report may summarize case details, but must preserve case counts, failed case IDs, blocked case IDs, threshold status, regression status, evidence manifest path, and run_id
if JSON report succeeds and Markdown report fails, run may be PARTIAL only if machine evidence is complete
if JSON report fails, run cannot PASS
```

Acceptance tests:

```text
test_markdown_report_status_matches_json_report
test_markdown_report_preserves_failed_and_blocked_case_ids
test_json_report_failure_prevents_pass
test_markdown_failure_with_complete_json_marks_partial_or_warning_only
```

## 39.6 Evidence Index and Finalization Rule

Each run must have a run-local evidence index. After finalization, evidence must be treated as immutable.

Required artifact:

```text
.agentx-init/evaluation/evidence/<run_id>_evidence_index.json
```

Required fields:

```text
run_id
suite_id
run_config_hash
fixture_lock_hash
baseline_hash
case_result_hashes
report_json_hash
report_markdown_hash or null
evidence_manifest_hash
completion_record_hash or null
created_at
finalized_at
finalized
```

Rules:

```text
finalized evidence must not be modified in place
changed hash after finalization invalidates the prior run status
new validation requires a new run_id
latest artifacts may point to a finalized run, but must not replace finalized evidence files
latest artifacts are not the source of truth; run-specific artifacts are
```

Acceptance tests:

```text
test_evidence_index_contains_hashes_for_final_artifacts
test_finalized_evidence_hash_change_invalidates_status
test_latest_artifacts_do_not_replace_run_specific_artifacts
```

## 39.7 Temporary Directory and Cleanup Rules

Evaluation may use temporary directories only for runtime execution scratch space.

Rules:

```text
temporary directories must be created under .agentx-init/evaluation/tmp/ or system temp with recorded path
temporary paths must never become baseline paths
temporary files must not be included in final score unless explicitly recorded as artifacts
cleanup failures are warnings unless they affect evidence integrity
source tree must not be used as scratch space
```

Acceptance tests:

```text
test_temp_artifacts_written_under_runtime_boundary
test_source_tree_not_used_as_scratch_space
test_cleanup_failure_records_warning_without_hiding_evidence_failure
```

## 39.8 Threshold Severity and Promotion-Blocking Semantics

Threshold results must distinguish ordinary failures from promotion-blocking failures.

Required severity values:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Rules:

```text
CRITICAL case failure always blocks THRESHOLD_PASS
required_case_ids must pass unless explicitly waived in run config
new CRITICAL regression always blocks full regression pass
blocked required case blocks pass unless expected_result explicitly expects BLOCKED
error case blocks pass unless threshold allows errors and case is non-required
waivers must be recorded, schema-valid, and evidence-backed
```

Acceptance tests:

```text
test_critical_case_failure_blocks_threshold_pass
test_required_case_failure_blocks_threshold_pass
test_expected_blocked_case_can_pass_when_explicitly_expected
test_waiver_must_be_recorded_to_ignore_noncritical_case
```

## 39.9 v4 Acceptance Delta

The v4 document is not considered satisfied unless these v4-specific additions are implemented:

```text
public programmatic entrypoint implemented
CLI behavior defined or explicitly not implemented
deterministic seed/order/hash behavior enforced
tool-adapter cases default to dry-run/read-only safe behavior
baseline schema compatibility checked
JSON/Markdown report parity tested
run-local evidence index written
finalized evidence immutability enforced
temporary directory boundary enforced
threshold severity semantics implemented
v4 tests added
```

---

# 40. v4 Final Frozen Acceptance Matrix

| Area | Required v4 behavior | DONE required? |
|---|---|---|
| Entrypoint | Stable programmatic entrypoint; CLI safe if implemented | Yes |
| Determinism | Seed/order/hash/clock controls recorded and enforced | Yes |
| Tool-adapter boundary | Dry-run/read-only default; mutating tool cases blocked | Yes |
| Baseline compatibility | Suite/schema/case compatibility checked before comparison | Yes |
| Report parity | Markdown does not contradict JSON report | Yes |
| Evidence finalization | Run-local evidence index and immutable finalized artifacts | Yes |
| Temporary files | Scratch space stays outside source tree and inside approved runtime boundary where possible | Yes |
| Threshold severity | Critical/required cases block pass unless explicitly expected or waived | Yes |
| v4 tests | All v4-specific tests implemented | Yes |

---

# 41. Final Rating

This v4 implementation specification is rated:

```text
10/10
```

Reason:

```text
It preserves the strong v3 coverage and fixes the remaining coding-agent handoff risks: stable entrypoint behavior, deterministic run controls, stricter tool-adapter execution boundaries, baseline compatibility rules, JSON/Markdown report parity, run-local evidence indexing, evidence finalization immutability, temporary directory boundaries, threshold severity semantics, and a final v4 acceptance matrix that prevents DONE from being claimed without those controls.
```
