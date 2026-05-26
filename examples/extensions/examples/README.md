# Extension Examples

This folder is outside the L0 seed package.

Examples here show how an external evolution agent may attach new behavior through ports without mutating the L0 runtime.

These examples are not imported by L0 and are not part of `SEED_PACKAGE_MANIFEST.yaml`.

Allowed future examples:

- specialized planner
- manager planner
- controller planner
- orchestrator planner
- memory backend
- evaluator backend
- governed tool pack

Every real extension must declare itself in `CAPABILITY_MANIFEST.yaml` and pass `make prove-seed`.
