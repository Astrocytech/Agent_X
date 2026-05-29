# Symbolic Regression Controller Blueprint

## Profile Reference

- **Profile**: `L2-PROFILE-SR-001`
- **Status**: draft
- **Risk**: medium

## Purpose

The Symbolic Regression Controller defines how Agent_X plans, validates, and
packages symbolic-regression work. It does not execute SR experiments — that
is an L1 governed implementation task.

## Specification

### Inputs

1. **Problem statement**: Natural language or structured description of the
   symbolic-regression goal (e.g., "find equation for dataset X with error < 1%").
2. **Dataset description**: Schema, column semantics, known constraints.
3. **Candidate backend**: Reference to PySR or another SR engine.
4. **Resource budget**: Time, compute, iteration limits.

### Outputs

1. **Bounded L1 implementation proposal**: A structured packet that L1's
   `goal_classifier` and `unit_planner` can convert into FIC-governed tasks.
2. **Evaluation plan**: Success criteria, validation gates, acceptable error.
3. **Risk notes**: Identified failure modes and mitigations.

### Process

1. Accept problem statement and context.
2. Validate inputs against profile constraints.
3. Assess feasibility using known SR boundaries.
4. Produce implementation proposal for L1.
5. Attach evaluation criteria.
6. Flag known risks.

## L1 Handoff

When this profile is promoted to `active`, L1 must create FICs for:

- UNIT-L1-003 (fic_generator)
- UNIT-L1-004 (fic_validator)
- UNIT-L1-005 (implementation_orchestrator)
- UNIT-L1-006 (handoff_packet_builder)
- UNIT-L1-007 (test_and_evidence)

## Boundaries

- No direct PySR import or execution.
- No L0 modification.
- No autonomous experiment execution.
- All SR work requires an L1 FIC.
