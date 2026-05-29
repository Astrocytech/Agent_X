# Evolution Acceptance Checklist

A change is acceptable only if it preserves the L0 seed and improves or safely extends capability.

## Required proof commands

- `make seed-boot`
- `make prove-seed`
- `make build-seed`

## Required review checks

### L0 preservation

- The only public runtime entrypoint remains `KernelService.run_turn`.
- No new L0 tool bypasses `ToolGatewayPort`.
- No action executes before `GovernancePort`.
- No L0 runtime module imports extension code.
- No model, GPU, network, secrets, Docker, or package manager is required for seed boot.

### Capability declaration

Every new capability must be declared in `CAPABILITY_MANIFEST.yaml`.

The declaration must include:

- id
- type
- attached port
- version
- risk class
- evidence requirement
- replay requirement
- checkpoint requirement
- rollback/removal support
- proof command

### Evidence and replay

Every evolved turn must remain:

- traceable
- checkpointable
- replayable
- evaluable
- governed
- removable

## Optional inverse-science method

External coding/evolution agents may use `DOCUMENTS/INVERSE_SCIENCE.txt` as advisory doctrine when choosing what change to propose next.

When using it, the agent should report:

- target
- current gap
- candidate input/change
- expected evidence
- hard-constraint check
- rollback path
- uncertainty
- stopping or continuation rule

This method is document-only. It must not be implemented as L0 runtime machinery unless a future accepted extension explicitly justifies that change through the governed extension boundary.

### Rejection rule

Reject the change if it:

- adds heavy agent behavior directly into L0
- adds self-evolution machinery to L0
- adds direct shell/network/filesystem access to L0
- creates another public entrypoint
- weakens governance
- weakens replay
- weakens checkpointing
- breaks seed package closure
- treats `DOCUMENTS/INVERSE_SCIENCE.txt` as mandatory L0 runtime behavior
