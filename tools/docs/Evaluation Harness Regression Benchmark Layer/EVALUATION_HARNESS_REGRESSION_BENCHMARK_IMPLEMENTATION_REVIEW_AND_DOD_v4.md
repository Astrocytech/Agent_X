# Evaluation Harness / Regression Benchmark — Review & DoD

## What Exists

| Artifact | Status |
|---|---|
| `evaluation_harness.py` — GoldenTask, EvalResult, EvalSuiteResult, EvaluationHarness, QualityScorecard | Implemented & enhanced |
| `golden_tasks/core_tasks.py` — 5 core golden tasks | Stable |
| `regression_benchmarks/core_benchmarks.py` — 5 regression benchmarks | Stable |
| `schemas/evaluation_result.schema.json` | Created |
| `schemas/evaluation_golden_task.schema.json` | Created |
| `test_evaluation_harness.py` | Created |
| `test_evaluation_schema_validation.py` | Created |
| 3 doc files in docs/ | Created |

## Verification Gates

### compileall
```bash
python3 -m compileall tools/agentx_evolve/evaluation/
python3 -m compileall tools/agentx_evolve/tests/test_evaluation_harness.py
python3 -m compileall tools/agentx_evolve/tests/test_evaluation_schema_validation.py
```

### pytest
```bash
python3 -m pytest tools/agentx_evolve/tests/test_evaluation_harness.py -v
python3 -m pytest tools/agentx_evolve/tests/test_evaluation_schema_validation.py -v
```

### Schema validation
- `jsonschema.Draft7Validator.check_schema()` on both schema files
- Instance validation with valid/invalid fixtures

## Coverage Matrix

| Feature | Unit Test | Schema Test |
|---|---|---|
| GoldenTask creation | test_register_task_adds_task | evaluation_golden_task.schema.json |
| EvalResult creation | test_run_suite_with_all_tasks_returns_results | evaluation_result.schema.json |
| EvalSuiteResult pass_rate | test_eval_suite_result_pass_rate | — |
| QualityScorecard set/get | test_quality_scorecard_set_and_get | — |
| write_suite_result | test_write_suite_result_creates_file | — |
| append_suite_history | test_append_suite_history_appends | — |
| list_tasks by tag | test_list_tasks_by_tag | — |
| latest_suite | test_latest_suite_returns_last | — |
| Schema structure | — | test_schema_is_valid_draft07 |
| Schema rejects bad data | — | test_invalid_result_missing_required |

## Traceability Matrix

| Requirement | Implementation | Test |
|---|---|---|
| Register golden tasks | `EvaluationHarness.register_task` | `test_register_task_adds_task` |
| Run evaluation suite | `EvaluationHarness.run_suite` | `test_run_suite_with_all_tasks_returns_results` |
| Compute pass rate | `EvalSuiteResult.pass_rate` | `test_eval_suite_result_pass_rate` |
| Scorecard metrics | `QualityScorecard.set_score/get_score` | `test_quality_scorecard_set_and_get` |
| Persist suite results | `EvaluationHarness.write_suite_result` | `test_write_suite_result_creates_file` |
| Append suite history | `EvaluationHarness.append_suite_history` | `test_append_suite_history_appends` |
| Filter by tag | `EvaluationHarness.list_tasks` | `test_list_tasks_by_tag` |
| Latest suite access | `EvaluationHarness.latest_suite` | `test_latest_suite_returns_last` |

## GO/NO-GO Rules

- **GO:** All unit tests pass, all schema tests pass, compileall clean, all 3 doc files reviewed.
- **NO-GO:** Any test failure, compile error, or missing doc file.
