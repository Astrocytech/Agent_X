# Evaluation Harness / Regression Benchmark — EQC / FIC / SIB Schema Contract

## Contract ID
`EVC-SCHEMA-CONTRACT-v4`

## Schema Purpose
Provide formal JSON Schema contracts for evaluation results and golden task definitions.

## Schemas

### evaluation_golden_task.schema.json
- **$id:** `evaluation_golden_task.schema.json`
- **$schema:** `https://json-schema.org/draft-07/schema#`
- **Required:** `schema_version`, `schema_id`, `task_id`, `description`, `task_type`, `expected_outcome`, `tags`
- **Properties:** `allowed_files`, `forbidden_files`, `warnings`, `errors` (all `array` of `string`)
- **Additional properties:** `false`

### evaluation_result.schema.json
- **$id:** `evaluation_result.schema.json`
- **$schema:** `https://json-schema.org/draft-07/schema#`
- **Required:** `schema_version`, `schema_id`, `task_id`, `passed`, `actual_outcome`, `duration_ms`
- **Properties:** `warnings`, `errors` (both `array` of `string`)
- **Additional properties:** `false`

## EQC (Error Quality Check)
- All schema files must be valid draft-07 JSON Schema.
- Every required field must be present in valid instances.
- No unexpected properties allowed (`additionalProperties: false`).

## FIC (Field Integrity Check)
- `task_id` must be non-empty string.
- `passed` must be boolean.
- `duration_ms` must be number >= 0.
- `score` values must be in range `[0.0, 1.0]`.

## SIB (Schema Integrity Boundary)
- Schema files live in `tools/agentx_evolve/schemas/`.
- Runtime artifacts live in `.agentx-init/evaluation/`.
- No evaluation code writes outside these boundaries.
