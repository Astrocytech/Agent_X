# Glyphser Integration Specification

## Profile

- **Profile**: TBD (UI/orchestration)

## Boundary

L2 defines interaction patterns and display requirements. L1 implements the
Glyphser integration as a governed unit.

## Integration Points

| Point | L2 Specifies | L1 Implements |
|-------|--------------|---------------|
| Display format | Structured output schema | Rendering |
| User interaction | Command/response patterns | Event handling |
| Data presentation | Visualization requirements | Chart/table generation |

## Constraints

1. L2 must not produce UI code or frontend bundles.
2. All Glyphser integration requires an L1 FIC.
