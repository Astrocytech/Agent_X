# FIC-L1-014: Evolution Controller

**fic_id:** `FIC-L1-014`
**unit_id:** `UNIT-L1-014`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/evolution_controller.py`

## Description

Orchestrates the full L1 evolution workflow. Chains all sub-controllers (003–013) in order: classify → plan → generate → validate → build → run checks → collect evidence → write completion → update traceability → process failures → check boundaries.

## Public surface

```python
__all__ = [
    "EvolutionResult",
    "EvolutionController",
    "EvolutionControllerError",
    "run_evolution",
]
```

### Exports

- `EvolutionResult` — frozen dataclass with fields for each stage result and `success`
- `EvolutionControllerError` — base exception
- `EvolutionController` — class with `evolve(goal_text, changed_files)` method
- `run_evolution(goal_text, changed_files) -> EvolutionResult`

## Orchestration order

1. `GoalClassifier.classify(goal_text)`
2. `UnitPlanner.plan(goal_record)`
3. `FicGenerator.generate(unit_plan)`
4. `FicValidator.validate(templates)`
5. `HandoffPacketBuilder.build(templates, unit_plan)`
6. `ProofCheckRunner.run_all()`
7. `EvidenceCollector.collect(proof_result)`
8. `CompletionRecordWriter.write(unit_id, summary, evidence)`
9. `TraceabilityUpdater` (links completion + packets)
10. `FailureLearningUpdater.process(proof_result)`
11. `BoundaryChecker.check(changed_files)`

## Dependency contract

- **stdlib only** (dataclasses, typing)
- May import all L1 controllers (003–013)
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`
- **No** imports from `L0` or `L2`

## Rules

1. `success` is True only when all checks pass.
2. All sub-controllers execute even if earlier ones produce warnings.
3. `evolve` never raises — always returns an `EvolutionResult`.

## Test contract

Test file: `L1/tests/test_evolution_controller.py`

Required tests (8):
1. `test_evolve_returns_result`
2. `test_evolve_success_with_valid_input`
3. `test_evolve_contains_all_stages`
4. `test_result_is_frozen`
5. `test_evolution_controller_no_forbidden_imports`
6. `test_evolve_handles_empty_goal`
7. `test_evolve_reports_failure_on_l0_change`
8. `test_evolve_rejects_none_goal`
