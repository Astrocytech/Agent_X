# Agent_X Functional Runtime MVP — Implementation Source Plan

## Target

```text
FUNCTIONAL_RUNTIME_MVP
```

## Proof Target

```text
make prove-functional-runtime-mvp
```

## What Is Being Implemented

A minimal complete vertical slice of the Agent_X runtime loop:

```text
goal → plan → action → validation → simulation → gate decision → execution → observation → test/evaluation → review → promotion/rejection → evidence → replay
```

26 new components under `tools/agentx_evolve/`, each with:
- typed dataclass I/O
- one happy-path test
- one denial/failure test
- one integration point with the orchestrator

## What Is Explicitly Not Implemented

- full multi-agent swarm
- finance agent
- ZKP simulation
- tokenized settlement simulation
- large benchmark pack
- API server
- plugin marketplace
- advanced memory
- distributed scheduler
- advanced planner
- large generated-agent ecosystem
- live network integrations
- external model dependency
- L4 runtime package

## Required Scenario: safe_report_generation_goal (Positive)

Goal: Create a small approved report artifact from a fixed input string.

Expected result: `PASS` — no source mutation, all artifacts typed and persisted, replay reproduces same result.

## Required Scenario: unsafe_self_promotion_goal (Negative)

Goal: A generated agent attempts to approve and promote its own action.

Expected result: `DENIED_AND_RECORDED` — denial by governance, not crash.

## Required Replay Proof

Both scenarios must reproduce the same verdict and key artifact hashes from recorded deterministic runtime context.

## Forbidden Shortcuts

- hardcoded PASS without checks
- report-only acceptance
- skipped negative scenario
- skipped replay
- untyped action dicts with no schema
- raw LLM output as action
- execution before validation
- promotion without review
- review by same generated agent
- source mutation in safe report scenario
- silent artifact overwrite
- silent state overwrite
- missing event log
- missing evidence reference
- missing transaction result
- missing gate decision
- missing invariant result
- dependency on live model
- dependency on live network
- changing existing tests to pass
- weakening existing documents to match incomplete implementation

## MVP Done Checklist

### Runtime and storage
- [x] runtime context exists
- [x] fixed clock works
- [x] seeded randomness works
- [x] workspace is created
- [x] artifact store writes and hashes artifact
- [x] state store persists run/action records
- [x] event log persists lifecycle events

### Control
- [x] action lifecycle enforces valid transitions
- [x] contract registry resolves required contracts
- [x] capability graph allows/denies correctly
- [x] policy rule engine returns deterministic decisions
- [x] decision gate combines policy/capability/invariant/simulation results
- [x] invariant engine blocks unsafe states
- [x] security envelope is required by executor
- [x] transaction manager commits or aborts safely

### Execution
- [x] simulation predicts artifact write
- [x] report executor writes only approved artifact
- [x] observer confirms expected artifact
- [x] rollback controller can record rollback path
- [x] circuit breaker can stop unsafe loop

### Review and promotion
- [x] review packet/decision exists
- [x] promotion references review
- [x] promotion references evidence
- [x] unsafe self-promotion is denied

### Scenarios
- [x] safe_report_generation_goal passes
- [x] unsafe_self_promotion_goal is denied and recorded
- [x] replay reproduces both scenarios

### Compatibility and acceptance
- [x] existing Agent_X targets still pass
- [x] functional compatibility report exists
- [x] reuse map exists
- [x] functional acceptance matrix exists
- [x] make prove-functional-runtime-mvp passes

## Classification Rules

```text
FUNCTIONAL_RUNTIME_MVP only if:
  - safe_report_generation_goal passes
  - unsafe_self_promotion_goal is denied and recorded
  - replay reproduces both scenarios
  - make prove-functional-runtime-mvp passes
  - all MVP acceptance rows are PASS
  - compatibility report verdict is PASS
  - reuse map exists and is complete

Otherwise: FUNCTIONAL_SCAFFOLD or NOT_FUNCTIONAL
```
