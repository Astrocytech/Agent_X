# Evaluation Harness / Regression Benchmark Layer

- **Roadmap Layer:** 15  
- **Roadmap Phase:** Phase E — Evaluation and Benchmarking  
- **Canonical Subdirectory:** `tools/agentx_evolve/evaluation/`  
- **Runtime Artifact Root:** `.agentx-init/evaluation/`

---

## 1. Dataclasses

### GoldenTask

| Field            | Type         | Description                              |
|------------------|--------------|------------------------------------------|
| `task_id`        | `str`        | Unique identifier for the task           |
| `description`    | `str`        | Human-readable description               |
| `task_type`      | `str`        | One of `ALL_TASK_TYPES`                  |
| `expected_outcome` | `str`      | Expected result string                   |
| `allowed_files`  | `list[str]`  | Files the agent is allowed to touch      |
| `forbidden_files`| `list[str]`  | Files the agent must NOT touch           |
| `tags`           | `list[str]`  | Categorization tags                      |
| `warnings`       | `list[str]`  | Non-fatal issues                         |
| `errors`         | `list[str]`  | Fatal issues                             |

### EvalResult

| Field            | Type         | Description                              |
|------------------|--------------|------------------------------------------|
| `task_id`        | `str`        | Reference to the evaluated task          |
| `passed`         | `bool`       | Whether the task passed                  |
| `actual_outcome` | `str`        | Observed outcome string                  |
| `duration_ms`    | `float`      | Execution time in milliseconds           |
| `warnings`       | `list[str]`  | Non-fatal issues                         |
| `errors`         | `list[str]`  | Fatal issues                             |

### EvalSuiteResult

| Field            | Type             | Description                              |
|------------------|------------------|------------------------------------------|
| `suite_id`       | `str`            | Unique suite identifier                  |
| `total`          | `int`            | Total number of tasks                    |
| `passed`         | `int`            | Number of passed tasks                   |
| `failed`         | `int`            | Number of failed tasks                   |
| `results`        | `list[EvalResult]`| Individual task results                 |
| `timestamp`      | `str`            | ISO-8601 timestamp                       |
| `pass_rate`      | `float` (property) | `passed / total`                      |
| `warnings`       | `list[str]`      | Non-fatal issues                         |
| `errors`         | `list[str]`      | Fatal issues                             |

### EvaluationHarness

| Method                        | Returns              | Description                              |
|-------------------------------|----------------------|------------------------------------------|
| `register_task(task)`         | `None`               | Register a GoldenTask                    |
| `get_task(task_id)`           | `GoldenTask \| None` | Look up a task by ID                     |
| `list_tasks(tag=None)`        | `list[GoldenTask]`   | List tasks, optionally filtered by tag   |
| `run_suite(task_ids=None, evaluator=None)` | `EvalSuiteResult` | Run a suite of tasks                   |
| `list_suites()`               | `list[EvalSuiteResult]` | All recorded suites                  |
| `latest_suite()`              | `EvalSuiteResult \| None` | Most recently run suite            |
| `write_suite_result(suite)`   | `str`                | Persist suite result JSON to disk       |
| `append_suite_history(suite)` | `str`                | Append suite result to history file     |
| `result_hash(result)`         | `str`                | SHA-256 hex digest of an EvalResult     |
| `suite_hash(suite)`           | `str`                | SHA-256 hex digest of an EvalSuiteResult|
| `validate_against_schema(instance, schema)` | `list[str]` | Schema validation errors    |
| `acquire_lock()`              | `None`               | Acquire threading evaluation lock       |
| `release_lock()`              | `None`               | Release threading evaluation lock       |

### QualityScorecard

| Method                     | Returns            | Description                             |
|----------------------------|--------------------|-----------------------------------------|
| `set_score(metric, score)` | `None`             | Set a metric score (clamped 0–1)        |
| `get_score(metric)`        | `float`            | Get a metric score (default 0.0)        |
| `all_scores()`             | `dict[str, float]` | All metric scores                       |
| `average()`                | `float`            | Average of all scores (default 1.0)     |
| `write_scorecard(path)`    | `None`             | Persist scorecard to JSON               |
| `load_scorecard(path)`     | `QualityScorecard` | Load scorecard from JSON                |

---

## 2. Schemas

- `evaluation_result.schema.json` (draft-07)
- `evaluation_golden_task.schema.json` (draft-07)

---

## 3. Constants

| Symbol              | Value                 |
|---------------------|-----------------------|
| `ES_PASS`           | `"PASS"`              |
| `ES_FAIL`           | `"FAIL"`              |
| `ES_NOT_RUN`        | `"NOT_RUN"`           |
| `ALL_EVAL_STATUSES` | `[ES_PASS, ES_FAIL, ES_NOT_RUN]` |
| `ALL_TASK_TYPES`    | `["IMPLEMENT_PATCH", "FIX_VALIDATION", "WRITE_TEST", "EXPLAIN_FAILURE", "REVIEW_CODE", "GENERATE_PLAN", "SECURITY", "ORCHESTRATOR"]` |

---

## 4. Runtime Artifacts

All written to `.agentx-init/evaluation/`:
- `suite_{suite_id}.json` — individual suite result
- `suite_history.jsonl` — append-only history of all runs
- `scorecard.json` — quality scorecard snapshot
