# Coding Agent Blueprint

## Profile Reference

- **Profile**: `L2-PROFILE-CA-001`
- **Status**: draft
- **Risk**: medium

## Purpose

The Coding Agent generates, reviews, and validates code changes within L1 FIC
boundaries. It is the primary mechanism for turning L2 specs into implemented code.

## Specification

### Inputs

1. **Implementation request**: What code needs to be written or changed.
2. **FIC reference**: The governing FIC that defines behavior and acceptance criteria.
3. **Codebase context**: Relevant existing code, types, and interfaces.
4. **Test results**: Current test state for regression detection.

### Outputs

1. **Governed code changes**: Modified files with evidence of FIC compliance.
2. **Validation evidence**: Test results, type checks, lint results.
3. **Handoff packets**: Ready for review and merge.

### Process

1. Accept implementation request and FIC reference.
2. Understand codebase context and constraints.
3. Implement changes within FIC boundaries.
4. Run validation suite.
5. Package evidence.
6. Produce handoff packet.

## L1 Handoff

When promoted to `active`, requires FICs for:

- UNIT-L1-003 through UNIT-L1-007

## Boundaries

- No L0 modification without L0 FIC.
- No bypass of L1 validation.
- No autonomous deployment.
