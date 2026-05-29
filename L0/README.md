# L0: Governed Universal Seed Kernel

A minimal governed kernel that bootstraps from a single profile, planner, governance, and tool gateway — with no model, GPU, network, environment secrets, or Docker required.

**Default production mode prohibits:**
- live self-modification
- direct shell access
- direct network access
- direct filesystem write outside approved runtime artifacts
- promotion from normal turn execution

## Architecture

```
User Input → KernelService.run_turn()
  → PlannerPort (decides planned tool)
  → GovernancePort (allows/denies/requires-approval)
  → ToolGatewayPort (single execution choke point)
  → MemoryPort → EvaluationPort → TracePort → CheckpointPort
  → Output
```

Governance is checked after the planner selects a tool and before the gateway executes it.

## Contents

| Path | Purpose |
|---|---|
| `CODE/` | L0 kernel runtime (core_kernel, governance, profiles, tool_gateway, kernel_composition) |
| `tests/seed_l0/` | Canonical L0 proof suite |
| `scripts/` | Build and proof scripts |
| `manifests/` | Seed invariants, capability manifest, package manifest |
| `docs/` | Acceptance criteria, public contract policy, extension ABI |

## Non-goals

L0's purpose is to be a minimal, governed **kernel** that supports evolution. Future capability (agent, controller, model integration, external tool, network, shell, code evolution) must be added outside L0 or behind a separately governed extension boundary.

## Proof Suite

```
make install
make seed-boot
make prove-seed
make run
```

The canonical proof suite verifies boot, governed turn execution, governance denial, governance-before-gateway ordering, evidence persistence, checkpoint replay, manifest closure, and phase order alignment.
