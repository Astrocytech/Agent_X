# PySR Custom Integration Specification

## Profile

- **Profile**: L2-PROFILE-SR-001 (Symbolic Regression Controller)

## Boundary

L2 may define SR experiment plans. L1 implements the PySR_custom wrapper.

## Integration Points

| Point | L2 Specifies | L1 Implements |
|-------|--------------|---------------|
| Experiment plan format | YAML with dataset, target, constraints | Parsing and validation |
| Equation output format | Structured equation with error metrics | Execution and capture |
| Validation protocol | Holdout test, error threshold | Computation and reporting |

## Constraints

1. L2 must not import `pysr` or any SR backend.
2. L2 must not invoke SR experiments directly.
3. All integration code requires an L1 FIC.
4. Integration tests belong in L1.
