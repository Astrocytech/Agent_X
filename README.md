<div align="center">
  <img src="DOCUMENTS/images/text_logo.png" alt="Agent_X" />
</div>

# Agent_X

Agent_X uses visible `L<n>/` layers to keep the system understandable, governed, and expandable without mixing seed runtime code, evolution governance, specialization planning, and future implementation packages.

The layer number does **not** mean "better" or "more important." It means the layer has a different role and a different authority boundary.

```text
L0 = governed seed kernel
L1 = external evolution / controller governance
L2 = specialization profile/spec layer
L3 = selected specialization domain package, future only
L4 = implementation/runtime package, future only and L1-authorized
L5 = release/deployment/operations package, future only
```

## Core rule

```text
L0 runs independently.
L1 governs implementation planning.
L2 proposes specialization.
L3 expands one selected specialization.
L4 implements only after L1 authorization.
L5 releases or operates only after validated implementation exists.
```

No higher layer may bypass a lower-layer boundary.

```text
L0 must not import L1, L2, L3, L4, or L5.
L2 must not directly modify L0 or L1.
L3 must not directly implement code without L1 FIC governance.
L4 must not exist as runtime code unless L1 has accepted the implementation package.
L5 must not exist until there is something release-bound or operational.
```

---

## L0 — Governed Seed Kernel

`L0/` is the protected seed-kernel layer.

Its purpose is to provide the smallest independently runnable and proofable Agent_X core.

L0 should contain:

```text
- seed runtime code;
- seed contracts;
- seed invariants;
- seed tests;
- seed proof/validation commands;
- minimal documentation needed to run and verify the seed.
```

L0 should not contain:

```text
- L1 controller logic;
- L2 specialization profiles;
- future domain work;
- external project integration plans;
- autonomous patching logic;
- experimental runtime code from higher layers.
```

L0 is considered healthy when:

```text
make seed-boot
make prove-seed
make run
```

continue to pass independently.

---

## L1 — External Evolution / Controller Governance

`L1/` is the external controller and governed evolution layer.

Its purpose is to convert goals, profiles, and implementation requests into bounded, reviewable, FIC-governed work.

L1 should contain:

```text
- L1 standards;
- FIC documents;
- SIB/ES/EQC sidecars;
- validators;
- evidence records;
- controlled controller modules;
- tests for L1 controller units;
- generated validation/readiness artifacts;
- handoff packet rules for coding agents.
```

L1 may inspect L0, but L0 must not depend on L1.

L1 is responsible for:

```text
- deciding whether a goal is ready for implementation planning;
- splitting work into bounded units;
- generating or validating FICs;
- building coding-agent handoff packets;
- collecting completion evidence;
- preventing ungoverned changes;
- blocking unsafe, vague, stale, or over-broad implementation requests.
```

L1 should not become the product runtime itself. It is the governance/control plane for evolution.

L1 is considered healthy when:

```text
make prove-l1
```

passes, and `make prove-all` still passes with L0 included.

---

## L2 — Specialization Profile / Specification Layer

`L2/` is the specialization planning layer.

Its purpose is to describe what specialized capabilities Agent_X may later develop.

L2 should contain:

```text
- specialization profiles;
- blueprints;
- evaluation specs;
- integration specs;
- profile catalogs;
- L2 standards;
- L2 ES/SIB/EQC/FIC sidecars for profile/spec governance;
- readiness reports;
- handoff requests to L1.
```

Examples of L2 profiles:

```text
- coding agent profile;
- symbolic regression controller profile;
- research agent profile;
- repository maintenance agent profile.
```

L2 may propose future implementation work, but it must not authorize implementation directly.

L2 must not contain active runtime directories such as:

```text
L2/controller/
L2/runtime/
L2/agents/
L2/tools/
L2/model_router/
L2/memory/
L2/autonomy/
```

unless a later L1-authorized implementation governance stage explicitly permits them.

The normal L2 flow is:

```text
specialization idea
  -> profile
  -> blueprint
  -> evaluation spec
  -> integration boundary
  -> profile package
  -> L2 readiness decision
  -> L1 handoff request
```

L2 is considered healthy when:

```text
make prove-l2
```

passes and all generated reports correctly state that L2 is profile/spec governance only, with no release evidence and no direct implementation authority.

---

## L3 — Selected Specialization Domain Package

`L3/` should not exist by default.

Create L3 only when one L2 profile becomes large enough that it needs its own domain package.

L3 is not "more governance." L3 is where one selected specialization is expanded into concrete domain material before L1 decides whether to create implementation work.

Example:

```text
L2 profile:
  symbolic_regression_controller.yaml

Possible future L3 package:
  L3/symbolic_regression/
```

A future L3 package may contain:

```text
- domain scenarios;
- benchmark task descriptions;
- dataset descriptions;
- evaluation cases;
- experiment blueprints;
- backend constraints;
- risk notes;
- L1 handoff requests;
- domain-specific acceptance criteria.
```

L3 should not contain:

```text
- runtime implementation code;
- direct external repository patches;
- autonomous execution logic;
- direct L0 or L1 changes;
- production deployment assets.
```

Create L3 only when all are true:

```text
[ ] an L2 profile is selected as active or handoff-ready;
[ ] the profile needs deeper domain artifacts than L2 should hold;
[ ] L3 will remain specification/domain material only;
[ ] L1 remains the implementation authority;
[ ] the root README can explain why the L3 package exists.
```

---

## L4 — L1-Authorized Implementation / Runtime Package

`L4/` should not exist during the current stage.

L4 only makes sense after L1 accepts a concrete implementation package derived from L2 or L3.

L4 would contain implementation/runtime assets only when L1 has already produced or accepted:

```text
- FIC-governed implementation units;
- allowed target files;
- test obligations;
- validation commands;
- completion evidence requirements;
- rollback or review requirements.
```

L4 must not be created merely because a profile sounds useful.

Create L4 only when:

```text
[ ] L1 has accepted the relevant handoff;
[ ] L1 has generated or approved FICs;
[ ] permitted implementation files are declared;
[ ] tests and validators are required;
[ ] implementation authority is explicit and bounded.
```

Without those conditions, L4 is premature.

---

## L5 — Release / Deployment / Operations Package

`L5/` is future-only.

L5 should exist only when some L4 implementation becomes release-bound or operational.

L5 may eventually contain:

```text
- release candidate manifests;
- deployment notes;
- operational runbooks;
- rollback plans;
- monitoring and telemetry specifications;
- long-term maintenance policies;
- production evidence bundles.
```

L5 should not exist while the project is still at seed, controller, profile, or domain-planning stage.

Create L5 only when:

```text
[ ] a concrete implementation exists;
[ ] validation evidence exists;
[ ] release or deployment is being considered;
[ ] operational risk needs its own layer;
[ ] rollback and monitoring requirements are meaningful.
```

---

## Current recommended state

The current architecture should stop at:

```text
L0 + L1 + L2
```

Meaning:

```text
L0 governed seed kernel: complete
L1 controlled prototype/control plane: complete
L2 profile/spec scaffold: complete
```

Do not create `L3/`, `L4/`, or `L5/` until there is a concrete trigger.

Recommended next move:

```text
Pick one L2 profile.
Ask L1 to evaluate whether it should become a governed planning package.
Create L3 only if that selected profile needs deeper domain expansion.
```

Most likely first candidate:

```text
L2-PROFILE-SR-001 = Symbolic Regression Controller
```

---

## Framework Evolution Target

Agent_X can evolve not only toward agents, controllers, and orchestrators, but also toward framework-building targets.

This does not make L0 a framework engine. L0 remains a governed seed kernel. Framework evolution is handled by L1 evolution machinery and expressed through L2 specialization profiles.

The first framework target is `framework_seed`, which defines a minimal governed framework substrate that may later evolve into specialized frameworks.

```text
Agent_X L0
  stable governed seed kernel
        |
        v
Agent_X L1
  evolution, validation, evaluation, comparison, promotion, packaging, evidence
        |
        v
Agent_X L2
  specialization targets
    - agent
    - controller
    - orchestrator
    - framework_seed
        |
        v
Evolved framework candidate
        |
        v
Specialized framework families
```

---

## Layer decision table

| Question | Correct layer |
|---|---|
| Is this protected seed runtime or seed proof logic? | `L0` |
| Is this governance, FIC, validation, handoff, or evidence for implementation planning? | `L1` |
| Is this a specialization profile, blueprint, evaluation spec, or integration boundary? | `L2` |
| Is this detailed domain material for one selected specialization? | `L3`, later only |
| Is this actual implementation/runtime work accepted by L1? | `L4`, later only |
| Is this release, deployment, operation, or production maintenance? | `L5`, later only |

---

## Reserved future layers: L6+

Layers above L5 are intentionally reserved.

Agent_X does not predefine `L6`, `L7`, `L8`, `L9`, `L10`, or higher layers because doing so would create artificial structure before the system has a real need for it.

A new layer above L5 may be created only when all of the following are true:

1. The responsibility cannot cleanly fit into L0–L5.
2. The new layer has a stable purpose distinct from existing layers.
3. The new layer has clear boundaries, non-goals, and authority rules.
4. The new layer does not bypass L1 governance.
5. The new layer does not weaken L0 independence.
6. The new layer is introduced through a governed L1 review or FIC process.

Until such a need exists, `L6+` means:

```text
reserved for future expansion
not active
not implementation-authorized
not required for current Agent_X development
```

When uncertain, keep the artifact in the lower-risk layer:

```text
specification before implementation
handoff before code
validation before release
```

## Quick start

```
make install
make seed-boot
make prove-seed
make run
```

## Layer map

- [L0/README.md](L0/README.md) — L0 seed kernel documentation
- [L1/README.md](L1/README.md) — L1 evolution controller documentation
- [L2/README.md](L2/README.md) — L2 specialization documentation

## Commands

| Command | Purpose |
|---|---|
| `make install` | Install minimal seed dependencies |
| `make seed-boot` | Compile and boot the seed |
| `make prove-seed` | Run canonical L0 seed proof |
| `make run` | Run one default seed turn |
| `make build-seed` | Build seed package from manifest |
| `make prove-l1` | Run L1 structure tests |
| `make prove-l2` | Run L2 structure tests |
| `make prove-all` | Run all tests across layers |
| `make clean` | Remove generated runtime artifacts |

## License

Proprietary — see [LICENSE](LICENSE).
