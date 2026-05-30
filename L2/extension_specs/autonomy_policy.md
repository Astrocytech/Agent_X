# L2 Autonomy Policy

**Status**: Bootstrap placeholder.

L2 does not authorize autonomous behavior. No L2 profile, blueprint, or spec
may enable autonomous patching, self-modification, or ungoverned tool execution.

## Rules

1. All L2 profiles must set `direct_runtime_allowed: false`.
2. All L2 profiles must set `implementation_allowed: false`.
3. No L2 artifact may claim autonomy authority.
4. Autonomous behavior requires L1 FIC-governed implementation.

## Current Status

No autonomy is implemented or authorized at L2.
