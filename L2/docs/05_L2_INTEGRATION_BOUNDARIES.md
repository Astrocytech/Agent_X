# L2 Integration Boundaries

## Integration Model

L2 defines integration boundaries at the specification level. Actual integration
code is implemented by L1 governed units.

## External Systems

### PySR Custom (symbolic_regression_backend)

| Aspect | Specification |
|--------|---------------|
| L2 role | Define SR experiment plans, validation criteria, packaging specs |
| L1 role | Implement PySR_custom wrapper, execute experiments, produce evidence |
| Boundary | L2 must not import or call PySR_custom directly |
| Handoff trigger | L2 evaluation spec → L1 FIC → L1 implementation |

### Glyphser (UI/frontend)

| Aspect | Specification |
|--------|---------------|
| L2 role | Define interaction patterns, display requirements, user workflows |
| L1 role | Implement Glyphser integration as governed unit |
| Boundary | L2 must not produce UI code or frontend bundles |
| Handoff trigger | L2 blueprint → L1 FIC → L1 implementation |

### Symbiant (self-improvement/autonomy)

| Aspect | Specification |
|--------|---------------|
| L2 role | Define self-improvement boundaries, safety constraints, evaluation criteria |
| L1 role | Implement Symbiant integration under strict FIC governance |
| Boundary | L2 must not enable autonomous self-modification |
| Handoff trigger | L2 evaluation spec + risk assessment → L1 FIC → L1 implementation |

## Cross-Cutting Boundary Rules

1. All external integrations require an L1 FIC before any code is written.
2. L2 may propose integration architecture. L1 implements.
3. No external system may modify L0 or L1 governance artifacts.
4. All integration code must pass L1 validation before merge.
