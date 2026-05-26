# Governance Rules

## Layer Protection

| Layer | Status | Notes |
| --- | --- | --- |
| L0 | Protected | Read-only; agentx-init cannot modify L0 |
| L1 | Governance layer | agentx-init reads but does not override L1 governance |
| L2 | Specification layer | May be read for profile/spec context |

## Hard Rules

1. L0 is protected. agentx-init may read L0 but must not modify it.
2. L1 remains the governance and implementation-control layer.
3. L2 remains the specification, blueprint, and profile layer.
4. agentx-init may convert L2 concepts into plans and proposals only.
5. Validation does not equal approval.
6. Patch proposals must be non-mutating.
7. Only allowlisted validation commands may run.
8. No source files may be silently overwritten.
9. No network access is required.
10. No background process.
11. No runtime self-mutation.
12. No promotion behavior.

## Risk Matrix

| Level | Description |
| --- | --- |
| R0 | Read-only or tool-owned output |
| R1 | Planning, proposals, allowlisted validation |
| R2 | Future docs/tests/schema/profile modifications |
| R3 | Future governance or L1 behavior changes |
| R4 | L0, promotion, permission behavior, self-modification, governance bypass |

Version 1 blocks R4.
