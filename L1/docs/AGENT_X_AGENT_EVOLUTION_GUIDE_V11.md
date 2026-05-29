# Agent_X Agent Evolution Guide

**Recommended repository path:** `docs/evolution/AGENT_EVOLUTION_GUIDE.md`  
**Version:** 11.0  
**Status:** Final stabilized document-first evolution framework for evolving Agent_X into user-requested agents; repository-adoption ready  
**Integration mode:** Advisory documentation only  
**Runtime status:** Not part of the L0 runtime path  
**Intended reader:** External coding/evolution agents, maintainers, future specialized Agent_X profiles, human reviewers  
**Primary method dependency:** `docs/methods/INVERSE_SCIENCE.md`  
**Authority dependencies:** `README.md`, `EVOLUTION_ACCEPTANCE.md`, `EXTENSION_ABI.md`, `SEED_ACCEPTANCE.md`, `SEED_INVARIANTS.yaml`, `CAPABILITY_MANIFEST.yaml`, `SEED_PACKAGE_MANIFEST.yaml`  
**Final quality target:** 10/10 document-only evolution doctrine  
**Recommended companion integration:** `README.md`, `EVOLUTION_ACCEPTANCE.md`, `SEED_ACCEPTANCE.md`, `EXTENSION_ABI.md`, and `SEED_PACKAGE_MANIFEST.yaml` should reference this guide as advisory evolution doctrine only when the guide is adopted into the repository.  
**Change-control status:** Final stabilized release. Future changes require a concrete defect, ambiguity, repository drift, repeated misuse, proven compression need, authority-file integration gap, new accepted architecture boundary, failed proof/check caused by this guide, or a user-approved change in Agent_X authority structure. Do not expand this guide for ordinary examples, speculative agent types, repeated score-chasing, or cosmetic rewording.

---

## 1. Purpose

This guide defines how to evolve Agent_X from a minimal governed universal seed kernel into any specialized agent the user wants.

The target may be:

- the main private problem-solving agent,
- a coding/evolution agent,
- a research agent,
- a planning agent,
- a tool-using assistant,
- an evaluator agent,
- an agent controller,
- a multi-agent orchestrator,
- a swarm coordinator,
- a specialist worker agent,
- or a future agent type not yet named.

The guide is intentionally document-first. It gives the external evolution agent a disciplined framework for deciding:

- what to change next,
- why that change is the smallest useful step,
- how to test the change,
- how to avoid bloating the seed,
- how to preserve the governed kernel,
- how to record evidence,
- and how to continue evolving safely after the current step.

This document does **not** create runtime behavior, tool authority, self-modification authority, orchestration authority, profile authority, or public API authority.

It is a framework for external agents and maintainers to use while evolving the repository.

---

## 1A. Document Use Rules

This guide is used when a human or external coding/evolution agent asks how to evolve Agent_X toward a desired agent capability.

Use this guide to decide the next repository change. Do not use this guide as permission to execute tools, mutate runtime behavior, bypass governance, or create an autonomous self-evolution loop.

The guide has four valid uses:

```text
1. choose the safest next evolution level,
2. prepare an evolution packet,
3. evaluate candidate repository changes,
4. decide whether to stop, continue, or reframe.
```

The guide has five invalid uses:

```text
1. treating advisory doctrine as runtime authority,
2. adding orchestration/swarm behavior to L0,
3. skipping lower evolution levels,
4. claiming a runtime capability from a document-only change,
5. weakening seed acceptance to satisfy an agent-specific target.
```

A future agent may quote or follow this guide, but every actual repository change must still satisfy the root authority files and proof commands.

Do not claim this guide is adopted, active, or complete in a repository unless the exact branch or commit contains the guide file, authority-file references, non-runtime manifest entry, absence of runtime imports, and proof results or explicitly listed unrun proof commands.

---

## 2. Source-of-Truth Hierarchy

When this guide conflicts with higher authority files, the higher authority wins.

Authority order:

```text
1. User instruction for the current evolution request
2. SEED_INVARIANTS.yaml
3. SEED_ACCEPTANCE.md
4. EXTENSION_ABI.md
5. EVOLUTION_ACCEPTANCE.md
6. CAPABILITY_MANIFEST.yaml
7. SEED_PACKAGE_MANIFEST.yaml
8. README.md
9. docs/methods/INVERSE_SCIENCE.md
10. this guide
11. examples, comments, speculative future notes
```

This guide may explain how to evolve Agent_X, but it cannot authorize a violation of seed invariants, governance, replay, checkpointing, manifest closure, tool mediation, or the stable public entrypoint.

If this guide is adopted into the repository, the repository authority files remain stronger than the guide. The guide is discoverable doctrine, not a new authority tier above seed invariants, acceptance rules, or extension boundaries.

If an external agent is uncertain whether a proposed change is allowed, it must choose the lower-risk interpretation:

```text
prefer doctrine over code
prefer test over runtime
prefer profile over core
prefer extension over L0 mutation
prefer explicit user approval over silent expansion
```


## 2A. Branch and Repository Verification Rule

Before evaluating whether Agent_X has already evolved, an external agent must verify the exact repository state it is inspecting.

Minimum verification packet:

```text
repository:
branch or commit:
files inspected:
authority files inspected:
proof commands available:
known stale-cache risk:
```

If the user supplies a commit hash, inspect that commit before judging the current state. If branch and commit disagree, report both rather than assuming the branch view is current.

Commit-specific evidence has priority over cached branch views for integration review. A branch view may be stale, delayed, or pointed at a different revision; a named commit is a fixed evidence target. When a user supplies a commit URL, the review must cite that commit or explicitly state that it could not be inspected.

Do not claim that a requested integration is missing until checking:

```text
README.md
EVOLUTION_ACCEPTANCE.md
EXTENSION_ABI.md
SEED_ACCEPTANCE.md
SEED_PACKAGE_MANIFEST.yaml
docs/methods/INVERSE_SCIENCE.md
this guide, if already added
```

This prevents stale repository views from producing false negative evaluations.

## 2B. User Request and Invariant Override Rule

A user may request any future agent target, including a main agent, orchestrator, swarm, coding agent, evaluator agent, or unknown future agent type. The request defines the desired direction, not automatic permission to violate the seed boundary.

Interpret broad user requests as target definitions first, not as implementation authority.

```text
User says: evolve Agent_X into an orchestrator.
Correct interpretation: define the orchestrator target and choose the lowest safe evolution boundary.
Incorrect interpretation: add an orchestration loop directly to L0.
```

A user request can authorize a higher-risk change only when all of the following are true:

```text
1. the requested target cannot be satisfied by doctrine, examples, tests, contracts, profiles, or extensions,
2. the user explicitly accepts the L0 impact,
3. the migration and rollback plan is documented,
4. proof commands and replay/checkpoint evidence are available,
5. the change does not introduce ungoverned tool use, hidden self-modification, or a second L0 public entrypoint.
```

If any condition is missing, use the lowest safe boundary and record the remaining gap.

---

## 3. Core Principle

Agent_X must evolve by controlled, evidence-producing changes.

The basic evolution loop is:

```text
desired future agent capability
-> define target output
-> identify current gap
-> generate candidate changes
-> rank candidates by evidence value, risk, cost, reversibility, and L0 impact
-> apply the smallest governed change
-> run proof commands
-> record evidence
-> update the evolution plan
-> stop, continue, or reframe
```

The seed kernel should become **easier to evolve** after each accepted change.

A change that makes one specialized agent more capable but makes the kernel harder to govern, replay, test, checkpoint, package, or specialize is not a good evolution step.

---

## 4. Relationship to Inverse Science

Use `docs/methods/INVERSE_SCIENCE.md` as the method for choosing the next evolution step.

In this guide:

| Inverse-science concept | Agent_X evolution meaning |
|---|---|
| Desired output | The agent capability the user wants |
| Input domain | Allowed repository changes |
| Candidate input | A proposed patch, profile, test, document, contract, adapter, evaluator, manifest change, or extension |
| Black box | The current Agent_X repository and its behavior under tests/proofs |
| Probe | A small controlled change plus proof run |
| Observed output | Test result, replay result, trace behavior, checkpoint behavior, governance behavior, complexity delta |
| Best-known input | Best current change or design path |
| Negative knowledge | Rejected patches, failed assumptions, unsafe patterns, bloat paths |
| Success tolerance | The minimum acceptable capability/evidence level |
| Stopping rule | Accept, continue, reframe, or reject further evolution |

The external evolution agent should treat every proposed repository change as a candidate input and every proof/check result as an observed output.

The method is useful because Agent_X evolution is usually an inverse problem:

```text
Wanted output: a safe agent capability
Unknown input: the smallest repository change that produces it without damaging L0
```

---

## 5. Non-Negotiable L0 Boundary

Agent_X’s L0 seed is the stable governed kernel. It must remain small, bootable, replayable, and profile-neutral.

Do not evolve L0 into a finished agent directly.

Do not turn L0 into:

- a model host,
- a swarm runtime,
- an autonomous coder,
- a self-improvement loop,
- a workflow engine,
- a direct shell executor,
- a direct network client,
- a direct filesystem actor,
- a multi-agent runtime,
- a profile-specific agent,
- or a hidden promotion system.

Future capabilities may be added outside L0 or behind governed extension/profile boundaries.

The L0 runtime path must remain governed:

```text
User/Input
-> KernelService.run_turn()
-> PlannerPort
-> GovernancePort
-> ToolGatewayPort
-> MemoryPort
-> EvaluationPort
-> TracePort
-> CheckpointPort
-> Output
```

No action may bypass governance.  
No tool may bypass `ToolGatewayPort`.  
No future agent type may create a second public runtime entrypoint for L0.  
No external evolution agent may interpret this guide as permission to add runtime machinery without passing the governed extension and acceptance process.

---

## 6. Evolution Levels

Every proposed change must be classified before implementation.

The level determines the required evidence and the acceptable risk.

### 6.1 Doctrine Level

A doctrine-level change adds or improves:

- documents,
- checklists,
- rubrics,
- prompts for external agents,
- acceptance criteria,
- examples,
- decision rules,
- future design guidance.

Doctrine-level changes are safest and should be preferred when they are enough.

Use doctrine when:

- the capability is not yet proven necessary at runtime,
- the risk of implementation is high,
- the concept can guide external agents without changing L0,
- the project needs clarity more than machinery.

### 6.2 Example Level

An example-level change demonstrates intended usage without changing required runtime behavior.

Use examples when:

- a future agent needs a pattern to copy,
- a concept is too abstract,
- implementation should remain optional,
- a full extension is not yet justified.

Examples must not become hidden authority. If examples conflict with seed invariants, the invariants win.

### 6.3 Test Level

A test-level change adds proof without changing behavior.

Use tests when:

- an invariant should be protected,
- a future agent might break a boundary,
- existing behavior needs replay evidence,
- a known failure mode should not recur.

Test-level changes are usually better than runtime changes because they improve evolvability without adding runtime complexity.

### 6.4 Contract Level

A contract-level change clarifies or extends typed boundaries.

Use contract changes only when:

- a future capability needs a stable interface,
- the contract preserves backward compatibility or has explicit versioning,
- replay/checkpoint/evaluation implications are clear,
- the change does not force one specialized agent type into L0.

### 6.5 Profile Level

A profile-level change specializes behavior without changing the neutral kernel.

Use profiles for:

- main agent behavior,
- coding agent behavior,
- research agent behavior,
- planning style,
- policy specialization,
- tool restrictions,
- evaluator selection,
- user-facing agent identity.

Profiles are the preferred first implementation point for most specialized agents.

### 6.6 Extension Level

An extension-level change adds capability through allowed ports or composition.

Use extensions for:

- tool integrations,
- external model use,
- orchestration adapters,
- memory backends,
- evaluator plugins,
- planner variants,
- non-core runtime experiments.

Extensions must remain removable and must not be imported into L0 core runtime modules except through allowed composition.

### 6.7 Capability Declaration Level

A capability declaration records an actual executable capability.

Use capability declarations only when actual behavior exists through a port, profile, extension, tool, evaluator, memory adapter, or runtime mechanism.

Do not declare documents as capabilities.

### 6.8 Runtime Level

A runtime-level change modifies L0 behavior.

This is the highest-risk category and should be avoided unless strictly necessary.

Runtime changes require strong evidence that doctrine, examples, tests, contracts, profiles, and extensions are insufficient.

Runtime changes must be:

- small,
- typed,
- governed,
- replayable,
- checkpointable,
- removable,
- manifest-declared,
- covered by proof commands,
- compatible with the stable public entrypoint,
- and explicitly justified against lower-level alternatives.

---

## 7. Capability Promotion Ladder

Do not jump directly from idea to runtime.

Use this ladder:

```text
idea
-> doctrine
-> example
-> test
-> contract
-> profile
-> extension
-> capability declaration
-> runtime integration only if unavoidable
```

Each rung requires evidence.

| Promotion | Allowed when | Evidence required |
|---|---|---|
| Idea -> Doctrine | concept is useful but unproven | clear problem, intended use, no runtime change |
| Doctrine -> Example | future agents need concrete usage guidance | realistic scenario, boundary, no runtime implication |
| Example -> Test | behavior should be protected | failure mode or invariant, expected pass/fail behavior |
| Test -> Contract | multiple components need stable boundary | repeated need, typed data shape, compatibility plan |
| Contract -> Profile | behavior is specialized, not L0-neutral | profile-specific policy/identity/planning need |
| Profile -> Extension | profile needs external capability | governed port attachment, capability declaration if executable, rollback plan |
| Extension -> Runtime | no viable lower-level boundary remains | strong evidence, governance proof, replay/checkpoint proof, minimal implementation |

A future agent must explain why it is not using a lower rung before proposing a higher one.

---

## 8. Universal Evolution Loop

Every evolution cycle must follow this loop.

### Step 1: Define the target agent or capability

The external evolution agent must state the desired output.

Examples:

```text
Target: Evolve Agent_X toward a private main agent that can solve user problems across sessions.
Target: Evolve Agent_X toward an orchestrator that can route tasks among specialist workers.
Target: Evolve Agent_X toward a coding agent that can propose governed patches.
Target: Evolve Agent_X toward a research agent that can manage hypotheses, evidence, and reports.
Target: Evolve Agent_X toward a swarm controller that coordinates multiple bounded agents.
```

The target must include:

- name,
- intended user benefit,
- expected behavior,
- forbidden behavior,
- minimum evidence of success,
- rollback/removal path,
- L0 boundary impact.

### Step 2: Define the current gap

The agent must describe what Agent_X cannot yet do.

Gap types:

- missing document,
- missing example,
- missing test,
- missing profile,
- missing contract,
- missing evaluator,
- missing memory schema,
- missing tool policy,
- missing extension boundary,
- missing replay fixture,
- ambiguous acceptance criterion,
- excess complexity,
- weak traceability,
- insufficient governance evidence.

### Step 3: Define hard constraints

Hard constraints block unsafe or architecture-breaking changes.

Minimum hard constraints:

- preserve `KernelService.run_turn()` as the stable public entrypoint,
- preserve governance-before-action,
- preserve `ToolGatewayPort` as the execution choke point,
- preserve traceability,
- preserve checkpointing,
- preserve replayability,
- preserve evaluation hooks,
- preserve profile-neutral L0,
- preserve manifest closure,
- preserve proof commands,
- avoid direct shell/network/filesystem access in L0,
- avoid runtime self-modification in production,
- avoid adding model/GPU/network/secrets/Docker requirements to seed boot,
- avoid adding heavy dependencies to L0,
- avoid adding orchestration or swarm behavior directly into L0.

### Step 4: Define soft preferences

Soft preferences guide tradeoffs.

Typical preferences:

- smaller change,
- simpler code,
- clearer contract,
- stronger test,
- less duplication,
- lower runtime surface,
- better replay evidence,
- better checkpoint evidence,
- more removable capability,
- clearer profile boundary,
- better documentation for future agents.

### Step 5: Generate candidate changes

Candidate changes should be small and comparable.

Examples:

```text
Candidate A: Add a main-agent profile document only.
Candidate B: Add a profile YAML for main-agent behavior.
Candidate C: Add tests proving profile isolation.
Candidate D: Add a new evaluator port contract.
Candidate E: Add an extension example for orchestrator routing.
Candidate F: Add runtime orchestration directly into L0.
```

Candidate F should normally be rejected unless there is strong evidence that all lower-level options are insufficient.

### Step 6: Rank candidates

Rank each candidate by:

- expected target improvement,
- expected information gain,
- hard-constraint safety,
- reversibility,
- implementation cost,
- runtime complexity,
- testability,
- replay/checkpoint impact,
- future evolvability,
- risk of bloat.

Preferred candidate:

```text
smallest change
+ highest evidence value
+ lowest L0 impact
+ easiest rollback
+ strongest proof path
```

### Step 7: Apply one primary change

Do not bundle unrelated changes.

One evolution cycle should usually contain:

- one main target,
- one primary change,
- one proof path,
- one rollback path.

Large changes must be decomposed.

### Step 8: Run evidence checks

Minimum commands after a repository change:

```bash
make seed-boot
make prove-seed
make build-seed
```

Recommended commands when relevant:

```bash
make clean
make run
```

A change is not accepted merely because it sounds architecturally correct. It needs evidence.

### Step 9: Record result

The external evolution agent must report:

```text
Target:
Current gap:
Candidate change:
Files changed:
Why this level was chosen:
Hard constraints checked:
Proof commands run:
Observed outputs:
Evidence strength:
Rollback path:
Remaining uncertainty:
Negative knowledge produced:
Next justified candidate:
Stop/continue decision:
```

### Step 10: Stop, continue, or reframe

Stop when:

- target is satisfied,
- evidence is strong enough,
- further change would add bloat,
- next candidates are too risky,
- the user’s requested level is reached.

Continue when:

- gap remains,
- next candidate is small,
- evidence supports further work,
- hard constraints remain safe.

Reframe when:

- target was vague,
- current path cannot satisfy target,
- evidence contradicts the hypothesis,
- the proposed agent type requires a different boundary.

### Step 11: State the capability claim precisely

Every evolution cycle must end with a bounded capability claim. The claim must match the evidence level and artifact level.

Allowed claim forms:

```text
Documentation added: the repository now contains advisory guidance for future agents.
Test added: the repository now protects a specific invariant or failure mode.
Profile added: a specialized behavior is now available through a profile boundary.
Extension added: an optional governed capability is now available through an extension boundary.
Runtime changed: universal L0 behavior changed and is proven by the required evidence packet.
```

Forbidden claim forms:

```text
claiming an agent exists because a doctrine document exists,
claiming orchestration exists because an orchestrator guide exists,
claiming a capability exists without executable behavior and capability declaration,
claiming 10/10 integration without checking the exact branch or commit,
claiming runtime support from advisory documents.
```


## 8A. Evolution Target Contract

Before choosing a candidate change, the external evolution agent must write a compact target contract.

The target contract prevents vague requests such as "make it an orchestrator" or "make it a better agent" from turning into oversized runtime patches.

Required fields:

```text
target agent family:
user-visible capability desired:
minimum useful next step:
lowest acceptable evolution level:
forbidden implementation shortcuts:
required evidence:
rollback/removal path:
expected future extension path:
```

The target contract must be used to reject changes that are larger than the current request requires.

Examples:

```text
If the user asks for an orchestrator, the first acceptable step may be an orchestrator doctrine, example, profile boundary, or extension boundary.
It is not automatically acceptable to add a live orchestration runtime to L0.

If the user asks for a coding agent, the first acceptable step may be a coding-agent profile or patch-evaluation doctrine.
It is not automatically acceptable to add autonomous repository mutation to production L0.
```

---

## 9. Candidate Scoring Rubric

Each proposed change should receive a candidate score before implementation.

Use a 0-2 score for each category.

| Category | 0 | 1 | 2 |
|---|---|---|---|
| Target alignment | weak or indirect | partially aligned | directly closes target gap |
| Evidence value | no proof path | limited proof path | strong proof path |
| L0 safety | changes/bloats L0 | touches boundary carefully | leaves L0 untouched or strengthens it |
| Governance safety | unclear | preserves current governance | strengthens governance proof |
| Reversibility | hard to undo | removable with effort | easy rollback |
| Complexity cost | large/unclear | moderate | small and simple |
| Future evolvability | narrows future paths | neutral | makes future evolution easier |
| Negative-knowledge value | little learning | some learning | clear learning even if failed |

Maximum score: 16.

Interpretation:

```text
14-16: strong candidate; usually proceed if proof path is clear
10-13: acceptable candidate; inspect risks and lower-level alternatives
6-9: weak candidate; reframe or reduce scope
0-5: reject unless explicitly requested and justified
```

Runtime candidates require at least 14/16 plus strong evidence that lower levels are insufficient.

---

## 10. Evolution Paths by Agent Type

This section describes how to evolve Agent_X toward different agent families without breaking L0.

---


### 10.0 Target Taxonomy and Boundary Decision

Before evolving toward an agent type, classify the target.

| Target type | Preferred first boundary | Runtime warning |
|---|---|---|
| Main private agent | profile + evaluator + memory policy | do not hardcode identity into L0 |
| Specialist worker | profile + examples + evaluator | do not make specialist behavior global |
| Research agent | profile + evidence/memory doctrine | do not embed research workflow in L0 |
| Coding/evolution agent | doctrine + tests + external tool process | do not add production self-modification |
| Tool-using agent | gateway adapter + governance policy | do not bypass ToolGatewayPort |
| Evaluator agent | evaluator contract/profile | do not let evaluation override governance silently |
| Orchestrator | external controller or extension | do not add orchestration loop to L0 |
| Swarm coordinator | bounded external/extension controller | do not add open-ended spawning to L0 |
| Unknown future agent | doctrine first | do not invent runtime before evidence |

Boundary decision rule:

```text
If the target can be represented as policy, use a profile.
If the target can be represented as a reusable optional behavior, use an extension.
If the target only needs explanation, use doctrine or examples.
If the target only needs protection, use tests.
If the target changes universal seed behavior, consider runtime only after proving every lower boundary insufficient.
```

### 10.0A Agent Architecture Blueprint Requirement

Before implementing any non-trivial target agent, the external evolution agent must produce a compact architecture blueprint.

Blueprint fields:

```text
target_agent_type:
user_value:
primary_boundary: doctrine | example | test | contract | profile | extension | capability declaration | runtime
required_ports:
forbidden_shortcuts:
state_or_memory_need:
tool_need:
evaluator_need:
trace_checkpoint_need:
rollback_or_removal_path:
minimum_acceptance_evidence:
```

The blueprint must prove that the proposed boundary is the lowest sufficient level. If the blueprint cannot explain why the target belongs in a profile, extension, external controller, or runtime, implementation is blocked until the boundary is clarified.

### 10.0B Agent-Family Boundary Matrix

Use this matrix to avoid placing specialized behavior in the wrong layer.

| Agent family | First safe artifact | Second safe artifact | Highest likely artifact | Runtime default |
|---|---|---|---|---|
| Main private agent | doctrine | profile | governed extension | no |
| Coding/evolution agent | doctrine | tests + external process | optional review extension | no |
| Research agent | doctrine | profile + evaluator | governed tool extension | no |
| Planner/strategy agent | profile | evaluator | planner extension | no |
| Tool-using agent | tool policy | gateway adapter | governed extension | no |
| Evaluator agent | evaluator doctrine | evaluator contract | evaluator extension | no |
| Orchestrator | doctrine + contract | external controller | bounded extension | no |
| Swarm coordinator | doctrine + simulation | worker contracts | bounded external controller | no |
| Specialist worker | profile | task evaluator | optional tool extension | no |

Runtime becomes acceptable only when the target modifies universal turn execution for all future agents and no lower boundary can satisfy the requirement.

---


### 10.0C Minimum Architecture Blueprint Fields

For any non-trivial target agent, the evolution agent must define a blueprint before implementing behavior.

Minimum blueprint fields:

```text
agent family:
primary user goal:
runtime boundary:
profile boundary:
allowed tools or tool classes:
forbidden tools or actions:
memory requirements:
evaluation requirements:
trace/checkpoint requirements:
rollback strategy:
first safe evolution level:
later possible evolution level:
```

The blueprint is not a capability claim. It is a control document used to choose the next smallest evidence-producing change.

A blueprint may justify a future profile, extension, or runtime change, but it cannot itself create that behavior.

### 10.0D Agent Capability Boundary Statement

Before implementing any non-trivial target agent, the external evolution agent must write a capability boundary statement.

Minimum fields:

```text
target_agent_type:
user_requested_capability:
what_L0_must_keep_doing:
what_L0_must_not_absorb:
profile_responsibilities:
extension_responsibilities:
tool_gateway_responsibilities:
memory_responsibilities:
evaluator_responsibilities:
trace_checkpoint_responsibilities:
new_capability_claim_allowed:
new_capability_claim_forbidden:
rollback_boundary:
```

This prevents the phrase "evolve into any agent" from being misread as permission to place every agent behavior inside L0.

A target agent may be strong, autonomous-looking, or multi-agent in its final behavior, but the seed boundary remains governed and minimal unless a specific accepted patch proves that a higher-risk boundary is necessary.

### 10.1 Main Private Problem-Solving Agent

Goal:

```text
A persistent, governed, user-aligned agent that helps solve real-world problems over multiple turns.
```

Recommended evolution order:

1. Doctrine: define main-agent responsibilities and non-goals.
2. Profile: add main-agent profile.
3. Memory: add profile-level memory policy or extension boundary.
4. Evaluation: add progress, usefulness, and uncertainty evaluators.
5. Tools: add governed tool policies only through gateway/extension.
6. Tests: prove governance, replay, and checkpoint behavior under main-agent profile.
7. Runtime: avoid unless profile/extension is insufficient.

Main-agent hard constraints:

- no unapproved irreversible actions,
- no direct tool execution,
- no hidden self-modification,
- no uncontrolled memory mutation,
- no bypass of governance,
- no overclaiming of certainty.

Acceptance criteria:

```text
[ ] main-agent behavior is profile-based or extension-based.
[ ] L0 remains profile-neutral.
[ ] memory writes are traceable.
[ ] evaluation records uncertainty and progress.
[ ] tool use remains governed.
[ ] replay/checkpoint tests pass.
```

---

### 10.2 Coding / Evolution Agent

Goal:

```text
An external or extension-level agent that proposes safe, governed, evidence-producing repository changes.
```

Recommended evolution order:

1. Doctrine: use this guide and inverse science.
2. Test: protect L0 boundaries.
3. Contract: define patch proposal format.
4. Evaluator: score patch evidence and risk.
5. Extension: add optional patch-review or code-inspection adapter.
6. Tool policy: allow repository operations only through governed gateway.
7. Runtime: never place self-evolution machinery inside L0 production path.

Coding-agent output format:

```text
Target:
Gap:
Candidate patch:
Files touched:
Risk class:
Evidence command:
Expected output:
Rollback:
Why this is not runtime bloat:
```

Acceptance criteria:

```text
[ ] patches are small and reversible.
[ ] no direct shell/network/filesystem access is added to L0.
[ ] proof commands pass.
[ ] capability changes are declared only when executable behavior exists.
[ ] failed patches become negative knowledge.
```

---

### 10.3 Research Agent

Goal:

```text
An agent that manages hypotheses, evidence, literature, uncertainty, experiments, and reports.
```

Recommended evolution order:

1. Doctrine: research workflow document or profile instructions.
2. Profile: research-agent profile.
3. Memory: hypothesis/evidence/report memory types through allowed boundary.
4. Evaluation: evidence quality and uncertainty evaluators.
5. Tools: governed search/file/report tools.
6. Tests: replay research turn with evidence and uncertainty.
7. Runtime: avoid embedding research workflow in L0.

Acceptance criteria:

```text
[ ] hypotheses are distinguishable from facts.
[ ] evidence is cited or traceable.
[ ] uncertainty is preserved.
[ ] reports separate observation, inference, and recommendation.
[ ] tool use remains governed.
```

---

### 10.4 Planner / Strategy Agent

Goal:

```text
An agent that decomposes goals into governed strategies and next actions.
```

Recommended evolution order:

1. Doctrine: define planning model.
2. Profile: planning-agent profile.
3. Evaluator: plan quality, constraint preservation, actionability.
4. Memory: plans, blockers, resources, assumptions.
5. Extension: optional planner variant through `PlannerPort`.
6. Runtime: avoid adding planning-specific logic directly to L0.

Acceptance criteria:

```text
[ ] plans include target, constraints, candidate actions, risks, and evidence.
[ ] only one primary next action is selected unless explicitly multi-action.
[ ] governance checks occur before action.
[ ] plan revisions are traceable.
```

---

### 10.5 Tool-Using Agent

Goal:

```text
An agent that uses external tools safely through the governed gateway.
```

Recommended evolution order:

1. Doctrine: tool-use policy.
2. Contract: tool request/response schemas.
3. Governance: risk classes and approval rules.
4. Gateway: tool adapter through allowed boundary.
5. Evaluation: tool result verification and failure handling.
6. Tests: allowed/denied tool-use cases.
7. Runtime: keep direct tool implementation outside L0 core.

Acceptance criteria:

```text
[ ] no tool bypasses ToolGatewayPort.
[ ] every tool call is governed.
[ ] tool results are traceable.
[ ] failure and denial are handled.
[ ] rollback/removal is possible.
```

---

### 10.6 Evaluator Agent

Goal:

```text
An agent or component that scores outputs, plans, patches, profiles, and tool results against explicit criteria.
```

Recommended evolution order:

1. Doctrine: define evaluation dimensions and failure modes.
2. Test: add examples of accepted and rejected evaluations.
3. Contract: define evaluator input/output schema if repeated use appears.
4. Profile: attach evaluation preferences to agent types.
5. Extension: add evaluator plugin only when doctrine/test/profile are insufficient.
6. Runtime: avoid embedding evaluator-specific policy into L0 unless it is universal.

Acceptance criteria:

```text
[ ] evaluator criteria are explicit.
[ ] evaluator output separates score, evidence, uncertainty, and recommendation.
[ ] evaluation does not silently override governance.
[ ] failed evaluation is traceable.
[ ] evaluator can be removed or replaced.
```

---

### 10.7 Orchestrator Agent

Goal:

```text
An agent/controller that routes work among specialized agents or components.
```

Important boundary:

An orchestrator is not L0. It must be an extension or higher-level runtime built around the governed seed, not inside the seed core.

Recommended evolution order:

1. Doctrine: define orchestration responsibilities and forbidden behaviors.
2. Contract: define task routing request/response structures.
3. Profile: orchestrator profile or external controller spec.
4. Evaluator: routing quality, delegation correctness, conflict handling.
5. Trace: record why each route/delegation was chosen.
6. Checkpoint: record orchestration state.
7. Extension: implement orchestrator through allowed ports/composition.
8. Runtime: do not add orchestrator loop to L0.

Orchestrator hard constraints:

- no hidden delegation,
- no ungoverned tool use by workers,
- no worker bypassing gateway,
- no uncontrolled recursive spawning,
- no unlimited fanout,
- no promotion/self-modification during normal turn execution,
- no unmanaged shared memory writes.

Acceptance criteria:

```text
[ ] orchestration is outside L0 or behind governed extension boundary.
[ ] each delegated action has a trace.
[ ] each worker/tool action remains governed.
[ ] fanout and recursion are bounded.
[ ] failure handling is explicit.
[ ] replay can reconstruct routing decisions.
```

---

### 10.8 Swarm / Multi-Agent Coordinator

Goal:

```text
A bounded multi-agent system where multiple workers collaborate under a controller.
```

Swarm evolution is high-risk and must be staged.

Recommended evolution order:

1. Doctrine only: define swarm safety and coordination rules.
2. Simulation: create non-runtime examples or tests.
3. Contracts: define worker message schemas.
4. Evaluators: consensus quality, conflict detection, redundancy, cost.
5. Controller extension: bounded fanout and bounded recursion.
6. Memory policy: prevent uncontrolled shared-state corruption.
7. Tool policy: workers cannot execute tools except through governed gateway.
8. Runtime: never embed open-ended swarm spawning in L0.

Swarm hard constraints:

- bounded agent count,
- bounded recursion depth,
- bounded tool budget,
- bounded memory writes,
- explicit controller responsibility,
- worker role isolation,
- no ungoverned inter-agent action,
- no hidden self-replication,
- no unbounded parallelism,
- no direct shell/network/filesystem execution from workers.

Acceptance criteria:

```text
[ ] swarm behavior is extension-level or external.
[ ] controller owns routing and termination.
[ ] workers have explicit roles and limits.
[ ] all tool use remains mediated.
[ ] all shared memory writes are governed or policy-checked.
[ ] replay can reconstruct the swarm decision path.
[ ] stop conditions are explicit.
```

---

### 10.9 Specialist Worker Agent

Goal:

```text
A narrow agent optimized for one task type.
```

Examples:

- summarizer,
- code reviewer,
- test generator,
- evaluator,
- research assistant,
- file organizer,
- prompt engineer,
- data analyzer.

Recommended evolution order:

1. Profile first.
2. Add task-specific examples.
3. Add evaluator for task quality.
4. Add governed tool policy if needed.
5. Add memory rules if needed.
6. Add extension only if profile is insufficient.

Acceptance criteria:

```text
[ ] task scope is narrow.
[ ] forbidden actions are explicit.
[ ] profile can be removed without breaking L0.
[ ] tool permissions are minimal.
[ ] evaluator can score output quality.
```

---

## 11. Risk Classes

Every proposed change must be assigned a risk class.

### Risk 0: Documentation only

Examples:

- add or clarify guide,
- add checklist,
- add prompt contract,
- add non-runtime example.

Evidence required:

- file placement is correct,
- manifest entry if required,
- no runtime imports,
- no capability declaration.

### Risk 1: Tests or examples

Examples:

- add a seed-boundary test,
- add replay fixture,
- add extension example.

Evidence required:

- proof commands pass,
- test is not brittle,
- no runtime behavior changes unless intended.

### Risk 2: Contract/profile/evaluator surface

Examples:

- add profile,
- add typed contract,
- add evaluator hook.

Evidence required:

- backward compatibility,
- profile isolation,
- replay/checkpoint implications clear,
- manifest updated.

### Risk 3: Extension/tool behavior

Examples:

- tool adapter,
- planner extension,
- memory backend,
- orchestrator extension.

Evidence required:

- governance path proven,
- ToolGatewayPort preserved,
- denial path tested,
- rollback possible,
- capability declared if executable.

### Risk 4: L0 runtime mutation

Examples:

- change core turn flow,
- alter public entrypoint behavior,
- modify governance execution order,
- change checkpoint/replay semantics.

Evidence required:

- strong proof,
- explicit justification that lower levels are insufficient,
- no weaker invariant,
- no new ungoverned capability,
- user approval if requested by project policy.

Risk 4 should be rare.

---

## 11A. Phase Gates for Higher-Risk Evolution

Use phase gates whenever the target involves orchestration, swarms, tools, memory backends, coding agents, or runtime changes.

```text
Gate 0: target and non-goals are explicit.
Gate 1: lower-level alternative has been considered.
Gate 2: hard constraints are listed.
Gate 3: rollback path exists.
Gate 4: evidence command is available.
Gate 5: failure mode is known.
Gate 6: manifest/capability impact is known.
Gate 7: user approval is obtained when required by project policy.
```

A candidate cannot move to implementation if any gate is unknown.

For Risk 3 and Risk 4 changes, unknown must be treated as blocked, not as permission to proceed.


---

## 12. Negative Knowledge Rules

Failed evolution attempts are useful.

Record negative knowledge when:

- a patch fails proof,
- a design adds bloat,
- a capability violates L0 boundary,
- a profile tries to become runtime,
- a tool bypasses governance,
- a test is too broad or brittle,
- a dependency is too heavy,
- replay/checkpoint behavior becomes weaker,
- a candidate change solves the wrong problem.

Negative knowledge record:

```text
Rejected candidate:
Target:
Why it seemed promising:
Failure evidence:
Violated constraint:
What was learned:
Do not retry unless:
Safer alternative:
```

Negative knowledge prevents repeated bad patches and helps the agent evolve more efficiently.

---

## 13. Evidence Strength

Classify evidence before accepting a change.

### Weak evidence

- plausible explanation only,
- no test,
- no trace,
- no comparison,
- no replay/checkpoint proof.

Weak evidence may justify a document change but not runtime change.

### Moderate evidence

- inspection plus local consistency,
- test added or updated,
- proof command passes,
- rollback path exists.

Moderate evidence may justify doctrine, examples, tests, contracts, and some profile changes.

### Strong evidence

- proof commands pass,
- replay/checkpoint behavior verified,
- before/after behavior is compared,
- governance behavior is tested,
- capability is declared if applicable,
- removal/rollback is possible.

Strong evidence is required for runtime, tool, governance, and orchestration changes.

### Exceptional evidence

- all strong evidence requirements pass,
- multiple relevant failure modes are tested,
- negative path is tested,
- manifest/package proof passes,
- complexity increase is justified and bounded,
- future removability is demonstrated.

Exceptional evidence is required for major orchestration, multi-agent, or L0-adjacent changes.

---

## 13A. Evidence Ledger

Every accepted evolution step should leave an evidence ledger entry, even if the change is documentation-only.

Minimum ledger fields:

```text
change_id:
target_agent_or_capability:
evolution_level:
risk_class:
files_changed:
proof_commands_run:
proof_result:
governance_boundary_impact:
manifest_impact:
capability_manifest_impact:
rollback_path:
remaining_uncertainty:
next_candidate:
```

Evidence ledger rules:

```text
A document-only change may have inspection evidence.
A test change must have passing test/proof evidence.
A profile change must have profile isolation evidence.
An extension/tool change must have governance and denial-path evidence.
A runtime change must have strong or exceptional evidence.
```

Never report a change as complete if the evidence ledger is empty, vague, or unable to identify which file/change produced the observed result.


---

## 14. Change Granularity Rules

Prefer one change per evolution cycle.

### 14.0 Versioning and Migration Rule

Any evolution that changes a contract, profile, memory schema, evaluator output, trace shape, checkpoint shape, extension interface, or capability declaration must state whether the change is backward compatible.

Required migration fields for non-document changes:

```text
schema_or_contract_changed:
backward_compatible:
old_behavior_preserved:
migration_needed:
rollback_safe:
replay_impact:
checkpoint_impact:
manifest_impact:
```

A change that breaks replay, checkpoint loading, or existing profile behavior is blocked unless the user explicitly requested a breaking evolution and the migration plan is documented.


Allowed small changes:

- one document,
- one example,
- one test file,
- one profile,
- one contract clarification,
- one extension adapter,
- one evaluator hook,
- one manifest update.

Avoid mixed patches such as:

```text
document + runtime + tool + profile + tests + dependency
```

unless the user explicitly requested a full integrated feature and the change is still bounded.

Large agent evolution should be decomposed into staged cycles.

If a patch must touch multiple files, those files must serve one primary change.

---

## 15. Runtime-Bloat Rejection Rules

Reject or reframe a proposed change if it:

- adds runtime machinery before doctrine/profile use proves need,
- hardcodes one agent type into L0,
- adds orchestration behavior to L0,
- adds swarm behavior to L0,
- adds self-evolution behavior to L0,
- adds a second public entrypoint,
- bypasses governance,
- bypasses `ToolGatewayPort`,
- adds direct shell/network/filesystem access,
- requires model/GPU/network/secrets for seed boot,
- makes replay/checkpointing harder,
- adds dependency weight disproportionate to benefit,
- cannot be removed without breaking the seed,
- makes a profile mandatory for all future agents,
- turns advisory documentation into runtime authority.

---

## 15A. No Premature Generalization Rule

Do not generalize from one requested agent type into a broad framework unless the evidence requires it.

Examples:

```text
If the user requests a research agent, do not also add orchestrator and swarm machinery.
If the user requests an orchestrator guide, do not add worker execution runtime.
If the user requests a main-agent profile, do not add tool adapters unless the profile cannot be evaluated without them.
```

A broader abstraction is allowed only when it reduces future risk, clarifies a repeated boundary, or prevents duplicated incompatible implementations.

---

## 16. User-Requested Agent Evolution Protocol

When the user asks to evolve Agent_X into a specific agent type, use this protocol.

### 16.1 Parse the requested target

Example user request:

```text
Evolve Agent_X into an orchestrator that can coordinate specialist agents.
```

Extract:

```text
target_agent_type: orchestrator
desired_capability: coordinate specialist agents
likely_level: doctrine -> contract -> profile/extension
forbidden_direct_path: putting orchestration loop inside L0
```

### 16.2 Classify the safest first change

Usually:

```text
doctrine first
test second
profile third
extension fourth
runtime last
```

### 16.3 Produce the next evolution packet

The external agent must output:

```text
Evolution target:
Capability class:
Proposed level:
Candidate change:
Why not lower level:
Hard constraints:
Expected evidence:
Files to change:
Proof commands:
Rollback path:
Stop/continue rule:
```

### 16.4 Apply only the selected change

Do not use the user’s broad target as permission to implement everything at once.

### 16.5 Re-score after evidence

After proof commands, update:

```text
target_distance:
evidence_strength:
remaining_gap:
next candidate:
risk:
stop/continue:
```

---

## 17. File Placement Guide

Recommended placements:

| Artifact type | Recommended location |
|---|---|
| Method doctrine | `docs/methods/` |
| Evolution guide | `docs/evolution/` |
| Acceptance criteria | root acceptance docs or `docs/evolution/` |
| Profile docs | `docs/profiles/` or profile metadata |
| Built-in profiles | `CODE/profiles/` only when actual profile behavior is intended |
| Extension examples | `examples/extensions/` |
| Runtime contracts | `CODE/core_kernel/contracts/` only when truly needed |
| Tests | `tests/seed_l0/` or extension-specific tests |
| Capability declarations | `CAPABILITY_MANIFEST.yaml` |
| Manifest entries | `SEED_PACKAGE_MANIFEST.yaml` |

Do not place method doctrine inside runtime code directories.

### 17A. Authority-File Touch Matrix

When an evolution step adds a new advisory document, profile, extension, capability, or runtime behavior, the external agent must decide which authority files need updates.

| Change type | README | EVOLUTION_ACCEPTANCE | EXTENSION_ABI | SEED_ACCEPTANCE | SEED_PACKAGE_MANIFEST | CAPABILITY_MANIFEST |
|---|---|---|---|---|---|---|
| Advisory method/evolution document | usually yes | optional/usually yes | only if boundary semantics change | optional/usually yes | yes if packaged | no |
| Example only | optional | no | no | no | yes if packaged | no |
| Test/invariant proof | optional | optional | no | yes if acceptance changes | yes if packaged | no |
| Profile | yes if user-facing | optional | no | yes if acceptance changes | yes | only if executable capability exists |
| Extension | yes if supported | yes | yes | yes | yes | yes if executable capability exists |
| Tool/gateway behavior | yes | yes | yes | yes | yes | yes |
| L0 runtime mutation | yes | yes | yes | yes | yes | yes if capability changes |

A document-only evolution guide should normally update README and manifest placement, but it must not update `CAPABILITY_MANIFEST.yaml` as if the document were executable behavior.

---

## 17B. No Capability Inference From Advisory Documents

A guide can influence how an external agent thinks, but it cannot create executable behavior.

The following claims are invalid after a document-only adoption patch:

```text
Agent_X now has an evolution agent.
Agent_X now has an orchestrator.
Agent_X now has swarm capability.
Agent_X can now self-evolve in production.
Agent_X now exposes a new runtime mode.
```

The valid claim is narrower:

```text
Agent_X now includes advisory evolution doctrine that external agents and maintainers can use when proposing future changes.
```

Executable capability exists only after executable behavior is added through an accepted profile, extension, tool, evaluator, memory adapter, contract, or runtime change, with appropriate proof and manifest/capability updates.

---

## 18. Manifest and Capability Rules

### 18.1 Manifest

Every added file that belongs to the seed package or authority surface should be listed in `SEED_PACKAGE_MANIFEST.yaml` under the correct non-runtime or runtime section.

For this guide, recommended manifest section:

```yaml
seed_l0_evolution_docs:
  - docs/evolution/AGENT_EVOLUTION_GUIDE.md
```

Do not list this guide under runtime, public API, gateway, governance, tools, profiles, or contracts.

### 18.2 Capability Manifest

Do not add a capability declaration for this document.

A document is not a runtime capability.

Add a capability only when actual behavior is implemented through a port, profile, extension, tool, evaluator, memory adapter, or other executable mechanism.

---

## 19. Proof and Review Commands

Minimum proof after adding this guide as a document:

```bash
make seed-boot
make prove-seed
make build-seed
```

Recommended:

```bash
make clean
make seed-boot
make prove-seed
make build-seed
make run
```

A document-only change should not alter runtime outputs except packaging/manifest behavior if the document is included in the seed package.

---


## 19A. Proof Result Interpretation

Proof commands must be interpreted conservatively.

```text
pass:
    The checked boundary is preserved for the tested path.
    A pass does not prove global optimality or unlimited future safety.

fail:
    The change is not accepted.
    Record the failure as negative knowledge and either revert, repair, or lower the evolution level.

inconclusive:
    The change is not accepted as complete.
    Add a narrower test, reduce scope, or report the remaining uncertainty.
```

A future agent must not convert partial evidence into a broad capability claim.


## 20. Branch, Patch, and Commit Discipline

External evolution agents should prefer small patch cycles.

### 20.0 Commit Acceptance Rule

A patch is not accepted because the change was written. It is accepted only when the exact branch or commit has been inspected and the evidence packet points to that exact state.

Minimum acceptance record:

```text
branch_or_commit_checked:
files_changed:
files_inspected_after_change:
proof_commands_run:
proof_result:
known_unrun_checks:
acceptance_status:
```

If the user gives a commit hash, use that commit as the inspected state. If the current branch view disagrees with the commit, treat the branch view as possibly stale and report the exact discrepancy.


Recommended branch naming:

```text
docs/agent-evolution-guide
profile/main-agent-v1
test/profile-isolation
extension/orchestrator-boundary
```

Recommended commit message style:

```text
Add advisory agent evolution guide
Add main-agent profile doctrine
Add profile isolation proof
Add orchestrator extension boundary example
```

A commit should not claim runtime capability when it only adds documentation.

A commit that changes L0 must say which invariant, contract, or proof required the change.

---

## 21. External Evolution Agent Prompt Contract

When another agent is asked to evolve Agent_X, include this instruction:

```text
Read docs/methods/INVERSE_SCIENCE.md and docs/evolution/AGENT_EVOLUTION_GUIDE.md as advisory doctrine.

Use inverse science to choose the next smallest evidence-producing repository change.

Do not implement runtime machinery unless doctrine, examples, tests, contracts, profiles, and extension boundaries are insufficient.

Preserve the L0 seed invariants:
- stable public entrypoint through KernelService.run_turn
- governance before gateway execution
- ToolGatewayPort as the single execution choke point
- trace, checkpoint, memory, and evaluation evidence
- no model/GPU/network/secrets/Docker requirement for seed boot
- no direct shell/network/filesystem access in L0
- no production self-modification or runtime promotion
- no new L0 public entrypoint

For every proposed change, report:
- target
- current gap
- candidate input/change
- expected evidence
- hard-constraint check
- rollback path
- uncertainty
- stopping or continuation rule
```

---

## 22. Evolution Packet Template

Use this exact template for every evolution step.

```text
# Evolution Packet

## Target
What future agent/capability is being evolved?

## Desired Output
What observable output should the repository produce after this step?

## Current Gap
What is missing, weak, ambiguous, overcomplicated, or unsafe?

## Inverse-Science Framing
- black box:
- candidate input:
- expected output:
- expected information gain:
- expected risk:
- success tolerance:
- stopping rule:

## Candidate Scoring
- target alignment:
- evidence value:
- L0 safety:
- governance safety:
- reversibility:
- complexity cost:
- future evolvability:
- negative-knowledge value:
- total score:

## Proposed Change
What one primary change will be made?

## Change Level
Choose one:
- doctrine
- example
- test
- contract
- profile
- extension
- capability declaration
- runtime

## Risk Class
Choose one:
- Risk 0: documentation only
- Risk 1: tests or examples
- Risk 2: contract/profile/evaluator surface
- Risk 3: extension/tool behavior
- Risk 4: L0 runtime mutation

## Why This Level
Why is this the lowest sufficient level?

## Files to Change
List exact files.

## Hard Constraints Checked
- L0 entrypoint preserved:
- governance before action preserved:
- ToolGatewayPort preserved:
- replay/checkpoint preserved:
- manifest closure preserved:
- no direct shell/network/filesystem:
- no heavy dependency:
- no runtime bloat:

## Evidence Plan
What commands/tests/checks prove the change?

## Rollback Plan
How can this change be removed?

## Expected Negative Knowledge
What would failure teach?

## Acceptance Criteria
What must be true for acceptance?

## Stop/Continue Decision
When should the agent stop, continue, or reframe?
```

---

## 22A. Guide Adoption Patch Rule

When this guide is added to the repository, the adoption patch must remain documentation-only.

Required adoption files:

```text
docs/evolution/AGENT_EVOLUTION_GUIDE.md
README.md
EVOLUTION_ACCEPTANCE.md
SEED_ACCEPTANCE.md
EXTENSION_ABI.md
SEED_PACKAGE_MANIFEST.yaml
```

Required adoption semantics:

```text
README.md must make the guide discoverable as advisory evolution doctrine.
EVOLUTION_ACCEPTANCE.md must tell external agents how to use the guide without treating it as runtime authority.
SEED_ACCEPTANCE.md must protect the documentation-only boundary.
EXTENSION_ABI.md must clarify that advisory evolution documents are not extension implementations.
SEED_PACKAGE_MANIFEST.yaml must list the guide under a non-runtime documentation section.
```

Forbidden adoption changes:

```text
CODE/** runtime imports
new profile forced to use this guide
new tool or capability declaration
new dependency
new public entrypoint
new orchestration loop
new self-evolution loop
CAPABILITY_MANIFEST.yaml entry for this guide as if it were executable behavior
```

The adoption patch succeeds only if it makes the guide discoverable while preserving its advisory status and adding no runtime authority.

---

## 22B. Minimum Repository Adoption Text

When this guide is adopted into Agent_X, the authority files should not merely mention it by filename. They should preserve the correct advisory boundary.

Minimum adoption semantics:

```text
README.md:
    The guide is discoverable as advisory evolution doctrine for external agents.

EVOLUTION_ACCEPTANCE.md:
    External agents may use the guide to choose evidence-producing changes, but it is not runtime authority.

SEED_ACCEPTANCE.md:
    The guide is documentation only, not imported by runtime code, and adds no L0 capability.

EXTENSION_ABI.md:
    Advisory evolution documents are not extension implementations and do not create ports, tools, profiles, or public entrypoints.

SEED_PACKAGE_MANIFEST.yaml:
    The guide is listed under a non-runtime documentation section if included in the seed package.

CAPABILITY_MANIFEST.yaml:
    Unchanged for document-only guide adoption.
```

If an adoption patch weakens any of these meanings, the guide is not correctly integrated even if the file exists.

## 23. Guide-Specific Acceptance Criteria

This guide is correctly integrated when:

```text
[ ] docs/evolution/AGENT_EVOLUTION_GUIDE.md exists.
[ ] README.md references it as advisory evolution guidance.
[ ] EVOLUTION_ACCEPTANCE.md references it as advisory evolution doctrine for external agents without making it runtime authority.
[ ] SEED_ACCEPTANCE.md confirms the guide is advisory documentation only and not imported by runtime code.
[ ] EXTENSION_ABI.md confirms advisory evolution documents do not create extension/runtime authority.
[ ] SEED_PACKAGE_MANIFEST.yaml lists it under a non-runtime documentation section.
[ ] CAPABILITY_MANIFEST.yaml is unchanged.
[ ] No runtime file imports this guide.
[ ] No profile is forced to use this guide.
[ ] No new tool, runtime phase, public entrypoint, dependency, or executable capability is added.
[ ] make clean passes.
[ ] make seed-boot passes.
[ ] make prove-seed passes.
[ ] make build-seed passes.
[ ] make run passes.
```

---

## 24. 10/10 Quality Rubric for This Guide

This guide rates 10/10 only if it satisfies all of the following:

```text
[ ] It clearly explains how inverse science guides repository evolution.
[ ] It can guide evolution into main agents, specialist agents, orchestrators, and swarms.
[ ] It protects L0 from becoming a finished agent or orchestrator runtime.
[ ] It gives exact evolution levels from doctrine to runtime.
[ ] It gives a promotion ladder with evidence requirements.
[ ] It defines candidate scoring.
[ ] It defines risk classes.
[ ] It defines negative knowledge handling.
[ ] It gives file placement rules.
[ ] It gives manifest and capability rules.
[ ] It gives proof commands.
[ ] It gives an external-agent prompt contract.
[ ] It gives an evolution packet template.
[ ] It defines guide-specific repository integration criteria.
[ ] It defines branch/commit verification to avoid stale repository judgments.
[ ] It defines phase gates for higher-risk evolution.
[ ] It defines an evidence ledger.
[ ] It defines maintenance triggers and stabilization rules.
[ ] It defines an agent architecture blueprint requirement.
[ ] It defines a compact evolution target contract before candidate selection.
[ ] It requires a capability boundary statement for non-trivial target agents.
[ ] It defines minimum architecture blueprint fields for non-trivial target agents.
[ ] It defines conservative proof-result interpretation.
[ ] It defines versioning and migration discipline for non-document changes.
[ ] It defines exact branch/commit acceptance evidence.
[ ] It defines how user requests interact with L0 invariants.
[ ] It prevents false capability claims from document-only changes.
[ ] It defines authority-file update expectations by change type.
[ ] It forbids premature generalization beyond the requested agent target.
[ ] It forbids runtime bloat and direct bypasses.
[ ] It remains document-only and does not create runtime authority.
[ ] It defines a documentation-only adoption patch rule.
[ ] It defines repository adoption evidence before claiming integration completion.
[ ] It defines minimum authority-file adoption semantics.
[ ] It prevents capability claims from advisory evolution documents.
[ ] It passes the final consistency rule before adoption.
[ ] It defines when future guide revisions must stop.
[ ] It gives commit-specific evidence priority over cached branch views.
[ ] It defines that after 10/10 adoption, the guide should be used rather than repeatedly rewritten unless a concrete trigger exists.
```

---

## 24A. Final Consistency Rule

This guide should be internally consistent before adoption.

Minimum final consistency checks:

```text
[ ] Metadata lists all required companion authority files.
[ ] Adoption patch rule and final checklist name the same required files.
[ ] The guide never claims runtime authority from documentation alone.
[ ] The guide never asks for CAPABILITY_MANIFEST.yaml changes for document-only adoption.
[ ] The guide never treats examples, prompts, or doctrine as executable capabilities.
[ ] Proof commands are interpreted conservatively and tied to an exact branch or commit.
```

If a future edit breaks one of these checks, repair consistency rather than adding new doctrine.

---

## 24B. Maintenance and Stabilization Rule

This guide should not grow indefinitely.

Future edits are valid only if they address at least one concrete trigger:

```text
1. a real repository change creates a new authority-file conflict,
2. an external agent repeatedly misuses the guide,
3. a section becomes stale because Agent_X's accepted architecture changes,
4. an ambiguity causes an unsafe or bloated candidate proposal,
5. the guide can be compressed without losing decision value,
6. the user explicitly requests a new agent-evolution family not covered here.
```

Future edits are invalid if they merely add more examples, repeat existing rules, make the document more ornate, or expand runtime ambitions without evidence.

Above the 10/10 quality threshold, prefer stabilization over expansion.


---

## 24C. Repository Adoption Evidence Packet

Before claiming this guide is integrated into Agent_X, the external agent must identify the exact repository state and the exact adoption evidence.

Required evidence packet:

```text
branch_or_commit_checked:
guide_path_checked:
README_reference_checked:
EVOLUTION_ACCEPTANCE_reference_checked:
SEED_ACCEPTANCE_boundary_checked:
EXTENSION_ABI_boundary_checked:
SEED_PACKAGE_MANIFEST_entry_checked:
CAPABILITY_MANIFEST_unchanged_checked:
CODE_runtime_import_absence_checked:
profile_not_forced_checked:
proof_commands_run:
proof_result:
known_unrun_checks:
final_score:
```

A guide-integration score of 10/10 is not valid unless this packet is complete and points to the exact branch or commit inspected.

---

## 24D. Final 10/10 Integration Checklist

This guide is complete for repository integration when all of the following are true:

```text
[ ] The guide is placed at docs/evolution/AGENT_EVOLUTION_GUIDE.md.
[ ] README.md references it as advisory evolution guidance.
[ ] EVOLUTION_ACCEPTANCE.md references it as advisory evolution doctrine for external evolution agents without making it runtime authority.
[ ] SEED_ACCEPTANCE.md protects the guide as advisory documentation only.
[ ] EXTENSION_ABI.md confirms advisory evolution documents are not extension implementations.
[ ] SEED_PACKAGE_MANIFEST.yaml lists it under a non-runtime documentation section if manifest closure requires it.
[ ] CAPABILITY_MANIFEST.yaml does not declare this guide as a runtime capability.
[ ] No CODE/ runtime file imports the guide.
[ ] No profile is forced to use the guide.
[ ] No new tool, runtime phase, public entrypoint, dependency, or L0 obligation is introduced.
[ ] The guide points to docs/methods/INVERSE_SCIENCE.md as advisory method dependency.
[ ] The guide preserves lower-level-first evolution discipline.
[ ] The guide covers main agent, specialist workers, research/planning/tool agents, evaluator agents, orchestrators, and swarms.
[ ] The guide requires an architecture blueprint before non-trivial agent implementation.
[ ] The guide requires a capability boundary statement before non-trivial agent implementation.
[ ] The guide requires an evolution target contract before implementation.
[ ] The guide defines conservative proof-result interpretation.
[ ] The guide protects replay/checkpoint compatibility through migration rules.
[ ] The guide's authority-file touch matrix and minimum adoption semantics are used when adding this guide to the repository.
[ ] The guide does not claim executable capability from document-only integration.
[ ] Proof commands pass after the repository integration patch.
[ ] The repository adoption patch did not add runtime code, tools, profiles, dependencies, or capabilities.
[ ] A repository adoption evidence packet identifies the exact branch or commit inspected.
[ ] Commit-specific evidence is preferred over stale or cached branch views.
[ ] The final consistency rule, final stabilization stop rule, and final release use rule pass before claiming 10/10 adoption.
```

If these are satisfied, do not continue editing this guide unless a concrete maintenance trigger appears.


---

## 24E. Final Stabilization Stop Rule

After this guide reaches the 10/10 quality rubric, future evaluation cycles should not create a new version unless at least one concrete maintenance trigger is present.

A valid future revision must name the exact defect, ambiguity, stale repository fact, failed proof, repeated misuse, or accepted architecture change that justifies editing.

Invalid reasons for another revision:

```text
raising the score after it is already 10/10
adding more examples without a misuse case
adding another agent family already covered by the taxonomy
turning advisory doctrine into runtime authority
expanding L0 to make the guide look more complete
```

If no concrete trigger exists, the correct output is to keep the guide stable and use it for repository evolution.

## 24F. Final Release Use Rule

This guide is complete once the final 10/10 integration checklist passes against a named branch or commit. After that point, the guide should be used to evolve Agent_X, not repeatedly rewritten.

A future reviewer may score the guide, but a new file version is justified only when the reviewer can name one of the maintenance triggers in Section 24B or a failed item from Section 24D.

If no such trigger exists, the correct evaluation result is:

```text
score: 10/10
action: no guide edit required
next step: use the guide for the next repository evolution target
```

---

## 25. Final Rule

Agent_X should be able to evolve into many kinds of agents, but the seed must not become all of those agents at once.

The correct evolution philosophy is:

```text
Keep L0 small.
Add doctrine before machinery.
Add examples before abstractions.
Add tests before runtime.
Add profiles before core behavior.
Add extensions before kernel mutation.
Use inverse science to choose the next smallest evidence-producing step.
Preserve governance, replay, checkpointing, traceability, manifest closure, and removability.
```

A successful evolution step makes the next evolution step safer, clearer, and easier to prove.
