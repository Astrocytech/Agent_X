# Research Agent Blueprint

## Profile Reference

- **Profile**: `L2-PROFILE-RA-001`
- **Status**: draft
- **Risk**: low

## Purpose

The Research Agent explores problem spaces and produces documentation and
proposals for L1 consideration. It does not implement code.

## Specification

### Inputs

1. **Research question**: What to investigate.
2. **Codebase analysis request**: Specific areas to examine.
3. **Literature reference**: External references for context.

### Outputs

1. **Research findings**: Structured analysis results.
2. **Proposal documents**: Recommendations for L1 action.
3. **Feasibility assessment**: Whether a proposed approach is viable.

### Process

1. Accept research question.
2. Explore codebase and relevant context.
3. Produce findings and recommendations.
4. Flag any implementation opportunities for L1.

## L1 Handoff

Indirect — produces input for `goal_classifier` (UNIT-L1-001).

## Boundaries

- No code implementation.
- No governance artifact modification.
- No tool execution.
