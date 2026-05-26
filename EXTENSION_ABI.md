# Extension ABI for the Governed Universal Seed Kernel

This repository is an L0 governed seed kernel.

L0 is not a finished agent. L0 is the stable kernel surface from which specialized agents, managers, controllers, and orchestrators may be evolved by an external coding/evolution process.

## Stable public entrypoint

External callers must enter the runtime through:

`core_kernel.public.kernel_service.KernelService.run_turn(request)`

No other L0 turn execution entrypoint is stable.

## Allowed extension method

Extensions may be added only by implementing or composing the existing ports:

- PlannerPort
- GovernancePort
- ToolGatewayPort
- MemoryPort
- EvaluationPort
- TracePort
- CheckpointPort
- ProfilePort
- PolicyPort
- RiskPolicyPort
- EvidenceWriterPort

Extensions must be injected through composition, not imported directly into L0 core runtime modules.

## Advisory method documents

Documentation under `docs/methods/` may describe optional reasoning methods for external agents.

These documents are not extension implementations. They do not create runtime behavior, tool authority, new ports, new profiles, or new public entrypoints.

An external agent may use `DOCUMENTS/INVERSE_SCIENCE.txt` to choose better candidate changes, but any actual capability must still attach through the allowed extension points and satisfy this ABI.

## Forbidden L0 mutations

An extension must not:

- add another public runtime entrypoint
- bypass GovernancePort
- bypass ToolGatewayPort
- execute shell commands directly from L0
- open arbitrary network connections from L0
- write arbitrary files from L0
- perform promotion during normal turn execution
- require GPU/model/network/secrets for seed boot
- mutate L0 public request/response contracts without versioning
- import extension modules into core_kernel runtime modules
- load external tools or register new tools through any mechanism
- add tool implementation files to CODE/tool_gateway/seed_tools/
- treat advisory method documents as runtime authority

## Required capability declaration

Every evolved capability must declare:

- capability id
- capability type
- attached port
- tool names, if any
- governance risk class
- replay/evidence requirements
- rollback/removal plan
- proof command

## Evolution acceptance rule

A changed seed is acceptable only if:

1. `make seed-boot` passes.
2. `make prove-seed` passes.
3. `make build-seed` passes.
4. `SEED_INVARIANTS.yaml` remains satisfied.
5. L0 public API compatibility is preserved.
6. All new capabilities are declared in `CAPABILITY_MANIFEST.yaml`.
7. All new L0 files are listed in `SEED_PACKAGE_MANIFEST.yaml`.
8. New capabilities are removable without breaking the seed.
