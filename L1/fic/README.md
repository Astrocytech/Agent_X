# L1 FIC Units

This directory is for bounded implementation-unit FIC contracts.

Root governance documents belong in:

```text
L1/docs/
```

Unit-specific FIC contracts belong in:

```text
L1/fic/
```

FIC units must derive from and cite:

- `L1/docs/00_L1_SYSTEM_GOAL.md`
- `L1/docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md`
- `L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md`

A FIC unit should define:

- unit ID
- source pseudocode section
- target file or files
- allowed files
- forbidden files
- public surface
- input/output contract
- state ownership
- dependency rules
- stop conditions
- validation commands
- completion evidence
- review gate
- traceability bindings

A FIC unit does not authorize broad repository rewrites unless it explicitly defines the allowed scope, review gate, validation requirements, and rollback expectations.

A FIC unit must return `BLOCKED` rather than guessing if required context, authority, interface, dependency, validation, or ownership information is missing.
