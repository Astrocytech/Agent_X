# L2 Lightweight FIC Standard

## Purpose

EQC-FIC at L2 is used only when an L2 profile becomes an L1 implementation task.
For L2 itself, FIC is lightweight — profiles serve as pre-FIC specifications.

## When to Use

- When an L2 profile is promoted from `draft` to `active`.
- When an L2 handoff packet triggers L1 FIC creation.
- When integration boundaries require governance.

## L2 FIC Equivalents

| L1 FIC Element | L2 Equivalent |
|----------------|---------------|
| Behavior contract | Profile YAML definition |
| Acceptance criteria | Evaluation spec criteria |
| Test requirements | Evaluation spec methods |
| Evidence requirements | Blueprint output specification |

## Rule

No governed code file should be written until its behavior is defined in an
implementation contract (L1 FIC) and passes a pre-code gate. L2 profiles are
pre-FIC specifications — they describe what should be built, not how.
