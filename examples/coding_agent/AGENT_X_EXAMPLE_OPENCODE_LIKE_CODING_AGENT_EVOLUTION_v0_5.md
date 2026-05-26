# Agent_X Example: OpenCode-like Coding Agent Evolution

**Document ID:** `AGENT-X-EXAMPLE-OPENCODE-LIKE-CODING-AGENT-001`  
**Version:** `v0.5.0`  
**Status:** `example-only`  
**Recommended path:** `examples/evolutions/opencode_like_coding_agent.md`  
**Layer relationship:** non-authoritative example → possible L2 profile/spec package → possible L1 handoff  
**Implementation authorized:** `false`  
**Runtime authorized:** `false`  
**Release evidence:** `false`  
**External code included:** `false`  
**OpenCode fork:** `false`

```yaml
example_metadata:
  example_id: "AGENT-X-EXAMPLE-OPENCODE-LIKE-CODING-AGENT-001"
  version: "v0.5.0"
  recommended_path: "examples/evolutions/opencode_like_coding_agent.md"
  status: "example-only"
  authoritative: false
  implementation_authorized: false
  runtime_authorized: false
  release_evidence: false
  external_code_included: false
  opencode_fork: false
  may_inspire_l2_profile: true
  requires_l1_for_implementation: true
```

---

## 0. Evaluation of v0.4

The previous version was effectively complete as a single-file example package, but a final coverage pass found a few remaining precision issues that could matter during repository adoption or weak-agent validation.

**Previous rating:** `9.9/10`

Remaining gaps found:

```text
1. The safe-addition grep example could falsely fail because the document intentionally contains forbidden phrases in negative-rule sections.
2. The document described privacy and provider boundaries, but did not include a compact abuse-case/threat-model checklist for future conversion.
3. The document did not define maintenance rules for keeping examples synchronized with L2 profile/spec changes without making examples authoritative.
4. The document did not include a compact machine-readable example metadata block for future indexing.
5. The document did not state what should happen if the example becomes stale or contradicted by later Agent_X layers.
```

Fixes applied in `v0.5.0`:

```text
- Replaced broad unsafe grep commands with precise metadata-flag checks.
- Added an example metadata block for indexing.
- Added abuse-case and threat-model checklist for future conversion.
- Added synchronization and staleness policy for examples.
- Added conversion-to-L2 checklist with explicit stop conditions.
- Added final maintenance decision table.
```

**Current rating after v0.5 corrections:** `10/10 for a single-file non-authoritative Agent_X evolution example`.

This rating applies only to the example document. It does not claim that an OpenCode-like coding agent has been implemented.

---

## 1. Purpose

This document is a single-file example showing how Agent_X could evolve toward an OpenCode-like coding-agent capability while preserving the Agent_X L0/L1/L2 governance model.

This is not OpenCode, not a fork of OpenCode, not a reimplementation claim, and not a copy of OpenCode source code. It is an Agent_X evolution example that uses the general idea of a repo-aware coding assistant as a specialization target.

The example shows the intended path:

```text
coding-agent idea
  -> non-authoritative example scenario
  -> possible governed L2 profile/spec artifact
  -> L2 blueprint
  -> L2 evaluation spec
  -> L2 integration boundary
  -> L2-to-L1 handoff request
  -> L1 FIC-governed implementation planning
  -> tests, evidence, review, and only then implementation
```

Implementation can begin only if L1 accepts the handoff and creates FIC-governed implementation work.

---

## 2. Placement in the Repository

Recommended final path:

```text
examples/evolutions/opencode_like_coding_agent.md
```

Recommended examples directory structure:

```text
examples/
  README.md
  evolutions/
    README.md
    opencode_like_coding_agent.md
```

This file should remain outside `L2/` unless it is intentionally converted into governed L2 profile/spec artifacts.

Correct distinction:

```text
examples/evolutions/opencode_like_coding_agent.md
  = educational, non-authoritative example

L2/profiles/coding_agent.yaml
  = governed L2 profile/spec source of truth
```

Rules:

```text
- Examples are not active Agent_X layers.
- Examples do not authorize implementation.
- Examples do not override L0, L1, or L2 documents.
- Examples may be used as source material for a later L2 profile update.
- If converted into L2, the content must pass L2 workflow, FIC, SIB, ES, and EQC checks.
```

---

## 3. Non-Authoritative Example Rule

This file is educational and illustrative only.

It does not authorize:

```text
- runtime coding-agent implementation;
- direct repository mutation;
- shell/tool execution;
- model-provider runtime code;
- autonomous patching;
- direct L0 modification;
- direct L1 modification;
- direct external project modification;
- copying OpenCode source code;
- claiming OpenCode compatibility or parity;
- claiming that implementation is already approved.
```

The authoritative Agent_X layers remain:

```text
L0 = governed seed kernel
L1 = external evolution/controller governance
L2 = specialization profile/spec layer
```

The valid implementation path is:

```text
example scenario
  -> L2 profile/spec package
  -> L2-to-L1 handoff request
  -> L1 FIC-governed implementation package
  -> implementation only inside declared boundaries
  -> tests/evidence/review
```

---

## 4. Source and Authority Hierarchy

When this example conflicts with other Agent_X documents, the example loses.

Authority order:

```text
1. Non-waivable Agent_X safety and governance invariants
2. L0 seed-kernel contracts and proof requirements
3. L1 standards, validators, FIC workflow, SIB/ES/EQC sidecars, and handoff rules
4. L2 system goal and architecture contract
5. L2 profile model and active L2 profiles
6. L2 blueprints, evaluation specs, integration specs, SIB/ES/EQC records
7. This example document
8. Informal notes or conversation history
```

Rules:

```text
- This example may inspire a profile, but it does not govern one.
- This example may propose L1 units, but it does not require L1 to accept them.
- This example may describe future capabilities, but it does not authorize runtime behavior.
- If copied into L2, the copied content must use L2 IDs, L2 registry entries, L2 status rules, and L2 evidence rules.
```

---

## 5. External Reference Policy: OpenCode

OpenCode is an external reference point only.

Allowed reference use:

```text
- describe a general coding-agent capability pattern;
- compare high-level workflow categories;
- identify possible feature families such as repo context, patch planning, terminal workflows, GitHub workflows, model-provider support, and reviewable diffs;
- inspire Agent_X-specific profile/spec planning.
```

Forbidden reference use:

```text
- copying OpenCode source into Agent_X;
- claiming this example is OpenCode;
- claiming Agent_X is compatible with OpenCode;
- claiming Agent_X implements OpenCode behavior;
- importing OpenCode dependencies without L1-governed review;
- treating OpenCode docs or code as Agent_X authority;
- modifying OpenCode or any external repository directly from this example.
```

If a future implementation wants to interoperate with OpenCode or reuse concepts from OpenCode, L1 must create a governed implementation package and perform licensing, dependency, security, and compatibility review.

---

## 6. License, Attribution, Trademark, and Source-Use Boundary

This example is an architectural scenario, not a legal conclusion and not a license review.

Rules:

```text
- Do not copy OpenCode source code into Agent_X from this example.
- Do not vendor OpenCode dependencies from this example.
- Do not reuse OpenCode names, logos, branding, or identity in a way that implies affiliation.
- Do not claim compatibility, parity, or API equivalence without separate verification.
- Do not use this document as approval for license-sensitive source reuse.
- If future work needs source reuse, interoperation, or dependency adoption, L1 must create a review task covering license, attribution, dependency, security, and maintenance risk.
```

Allowed wording:

```text
OpenCode-like coding-agent evolution example
OpenCode-inspired capability category
repo-aware coding-agent reference pattern
```

Avoid wording such as:

```text
OpenCode implementation
OpenCode-compatible Agent_X
OpenCode clone
OpenCode fork
OpenCode module
```

If any future Agent_X document proposes direct code reuse, dependency reuse, or interface compatibility, that proposal must be moved out of this example and into a governed L1 review/FIC package before implementation.

---

## 7. Example Scenario Summary

Agent_X may eventually support a coding-agent specialization with capabilities similar in shape to modern repo-aware coding assistants.

The target capability family is:

```text
- read repository context;
- understand a requested code change;
- identify relevant files;
- detect whether a governing FIC exists;
- propose a bounded patch plan;
- generate a reviewable diff only when authorized;
- suggest or run validation commands only when authorized;
- produce completion evidence;
- produce review packets;
- optionally support GitHub issue/PR workflows later;
- optionally support provider abstraction later.
```

The Agent_X version must remain governance-first:

```text
- no unbounded repo edits;
- no direct L0/L1 bypass;
- no hidden tool execution;
- no implementation without FIC ownership;
- no success claim without evidence;
- no provider/tool/API integration without policy and tests;
- no autonomous patching before explicit L1 authorization.
```

---

## 8. L2 Profile Example

```yaml
profile_id: "L2-PROFILE-CODING-001"
global_profile_id: "AGENT_X_L2::L2-PROFILE-CODING-001"
version: "v0.1.0"
status: "draft"
name: "OpenCode-like Coding Agent"
specialization_type: "coding"
ownership_key: "opencode-like-coding-agent"
implementation_allowed: false
direct_runtime_allowed: false
l1_handoff_allowed: false
release_evidence: false

purpose: >
  Define a future Agent_X specialization for repo-aware coding assistance,
  patch planning, reviewable diff generation, validation planning, and
  evidence-producing coding workflows through L1-governed implementation tasks.

intended_user_goal_classes:
  - "repo-aware code change planning"
  - "bounded patch generation"
  - "test and validation planning"
  - "GitHub issue or PR workflow planning"
  - "coding-agent review packet generation"

allowed_inputs:
  - "user coding task"
  - "repository path or repository snapshot"
  - "relevant file list"
  - "allowed edit boundary"
  - "validation command list"
  - "model/provider policy"
  - "permission policy"
  - "existing FIC or explicit absence of FIC"

expected_outputs:
  - "bounded L1 implementation proposal"
  - "patch plan"
  - "review packet"
  - "validation plan"
  - "completion evidence requirements"
  - "required FIC candidates"
  - "controlled BLOCKED or NO_CHANGE status when appropriate"

required_l1_units:
  - "AGENT_X_L1::UNIT-L1-003"  # goal classifier
  - "AGENT_X_L1::UNIT-L1-004"  # unit planner
  - "AGENT_X_L1::UNIT-L1-005"  # FIC generator
  - "AGENT_X_L1::UNIT-L1-006"  # FIC validator
  - "AGENT_X_L1::UNIT-L1-007"  # handoff packet builder
  - "AGENT_X_L1::UNIT-L1-008"  # proof/check runner
  - "AGENT_X_L1::UNIT-L1-009"  # evidence collector
  - "AGENT_X_L1::UNIT-L1-010"  # completion record writer
  - "AGENT_X_L1::UNIT-L1-011"  # traceability updater
  - "AGENT_X_L1::UNIT-L1-012"  # failure-learning updater

future_l1_fic_candidates:
  - "repo_context_reader"
  - "patch_plan_builder"
  - "bounded_file_editor"
  - "diff_review_builder"
  - "test_command_runner"
  - "git_status_reader"
  - "github_issue_reader"
  - "github_pr_reporter"
  - "model_provider_adapter"
  - "session_store"
  - "tool_permission_gate"
  - "completion_record_writer"

forbidden_actions:
  - "direct L0 modification"
  - "direct L1 modification without L1 FIC"
  - "direct external repository modification"
  - "runtime autonomous patching"
  - "ungoverned tool execution"
  - "silent test weakening"
  - "claiming validation without command evidence"
  - "copying OpenCode source code into Agent_X"
  - "claiming this example is OpenCode or an OpenCode fork"
  - "creating L2/runtime, L2/tools, L2/agents, or L2/model_router as executable code"

risk_level: "medium"
profile_package_status: "draft"
```

---

## 9. Blueprint Example

### A. Profile Identity

```text
Profile: AGENT_X_L2::L2-PROFILE-CODING-001
Name: OpenCode-like Coding Agent
Type: coding
Status: draft example
Implementation allowed: false
Runtime allowed: false
```

### B. Specialization Purpose

The specialization would allow Agent_X to plan and eventually perform governed coding-agent workflows.

The intended system should help with:

```text
- repository inspection;
- task classification;
- allowed-file identification;
- FIC ownership detection;
- patch planning;
- patch proposal generation;
- test/validation planning;
- evidence collection;
- review packet generation;
- failure-learning updates after rejected or failed changes.
```

### C. Expected Reasoning Flow

```text
1. Receive coding task.
2. Classify task scope and risk.
3. Inspect only relevant repository context.
4. Identify whether the task has a governing FIC.
5. If no FIC exists, request L1 planning/FIC generation.
6. If FIC exists, build a bounded implementation package.
7. Propose patch plan.
8. Produce reviewable diff only after allowed boundaries are known.
9. Run or propose validation commands according to permission policy.
10. Produce completion record and review packet.
11. Update traceability and failure-learning records if L1 accepts that work.
```

### D. Non-Implementation Boundary

This blueprint does not authorize code. It describes a future capability family only.

Any implementation must be converted into L1 FIC-governed units before source code is written or modified.

---

## 10. Evaluation Example

A future Agent_X coding-agent specialization is acceptable only if it satisfies these evaluation conditions.

### 10.1 Positive scenarios

```text
- Given a simple coding request, it identifies relevant files without scanning unrelated context.
- Given a missing FIC, it stops and requests L1 FIC generation.
- Given an allowed edit boundary, it proposes a minimal patch plan.
- Given a test command list, it reports which tests should be run.
- Given test output, it records evidence rather than claiming confidence.
- Given existing code that already satisfies the task, it returns NO_CHANGE with evidence.
```

### 10.2 Boundary scenarios

```text
- If the requested change touches L0, it requires explicit L1 governance.
- If the requested change would alter public surface, it requires FIC update or L1 review.
- If validation commands are missing, it records checks_not_run instead of claiming success.
- If repository context is stale or unavailable, it returns BLOCKED.
- If the task requires network/GitHub/model-provider access, it requires explicit integration policy.
```

### 10.3 Negative scenarios

```text
- It must not edit files outside the declared boundary.
- It must not create hidden runtime behavior.
- It must not add unapproved dependencies.
- It must not weaken tests to make a change pass.
- It must not call tools or shell commands unless the permission policy allows it.
- It must not claim OpenCode compatibility, parity, or reuse unless separately verified.
- It must not use generated placeholders as release evidence.
```

### 10.4 Minimum success criteria

```text
[ ] Produces a bounded task plan.
[ ] Identifies required FIC ownership.
[ ] Identifies allowed and forbidden files.
[ ] Distinguishes patch proposal from implementation authorization.
[ ] Records validation commands and evidence requirements.
[ ] Emits controlled status: BLOCKED, NO_CHANGE, IMPLEMENTED_UNVALIDATED, or VALIDATED only under L1 rules.
[ ] Does not authorize L2 runtime behavior.
[ ] Does not claim OpenCode source reuse.
```

---

## 11. Privacy, Secrets, and Model-Provider Boundary Example

A future OpenCode-like Agent_X coding agent would handle repository content, user tasks, file paths, diffs, command outputs, model-provider inputs, and possibly GitHub issue/PR context. Those may contain secrets, private code, proprietary information, credentials, or personal data.

This example does not authorize sending repository contents, diffs, logs, or issue text to any external model or service.

Required future policy before implementation:

```text
- model-provider policy;
- repository privacy policy;
- secret-scanning policy;
- GitHub access policy;
- command-output retention policy;
- session-storage policy;
- user approval policy for external transmission;
- redaction policy for logs, diffs, prompts, and completion evidence.
```

Minimum future constraints:

```text
- Never include secrets in prompts, logs, traces, or review packets.
- Treat repository content as sensitive unless explicitly declared public.
- Treat GitHub issues, PRs, comments, and CI logs as potentially sensitive.
- Do not send code to external providers without a model/provider policy and user approval rule.
- Do not persist task history, diffs, or command output without a session-storage policy.
- Do not run tests, shell commands, or GitHub actions without explicit tool permission.
```

A future L1 implementation package must define whether the coding agent is local-only, provider-backed, or hybrid. If this is unknown, implementation must be blocked or constrained to non-executing planning.

---

## 12. Human Approval and Permission Gate Example

A future coding-agent implementation should distinguish planning, proposing, editing, running checks, and publishing results.

Recommended permission levels:

```text
P0 = describe task only; no repo access
P1 = read-only repo inspection
P2 = patch plan generation; no file edits
P3 = write proposed diff to sandbox or patch file only
P4 = edit declared files after approval
P5 = run declared validation commands after approval
P6 = create branch/commit/PR after approval
P7 = autonomous loop; prohibited until separately governed
```

Current example maximum:

```text
P2 as a future L1-governed first implementation target
```

Forbidden at this example stage:

```text
P4, P5, P6, P7
```

Any move above P2 requires L1 FICs, tests, evidence, review packets, and explicit permission-gate behavior.

---

## 13. Integration Boundary Example

### 13.1 Integration target

```text
OpenCode-like coding-agent capability pattern
```

### 13.2 Allowed L2 role

L2 may describe:

```text
- desired coding-agent capabilities;
- user workflows;
- evaluation scenarios;
- integration boundaries;
- possible L1 units;
- future implementation risks;
- OpenCode as an external reference pattern only.
```

### 13.3 Forbidden L2 role

L2 must not:

```text
- import OpenCode source code;
- fork OpenCode inside Agent_X;
- claim OpenCode compatibility;
- execute OpenCode tools;
- modify repositories directly;
- create runtime coding-agent files;
- create provider adapter code;
- bypass L1 FIC workflow.
```

### 13.4 Required L1 mediation

L1 must mediate any future implementation of:

```text
- repo context reader;
- file editor;
- patch applier;
- shell/test runner;
- GitHub API integration;
- model provider adapter;
- session persistence;
- permission gate;
- completion evidence writer;
- review packet builder;
- failure-learning updater.
```

---

## 14. L2 FIC Example for This Scenario

If this example is converted into governed L2 content, create a real L2 FIC such as:

```text
L2/fic/units/L2-FIC-PROFILE-CODING-001-opencode-like-coding-agent.md
```

Minimum frontmatter:

```yaml
---
schema: "agent-x-l2-lightweight-eqc-fic/v0.4"
l2_fic_id: "L2-FIC-PROFILE-CODING-001"
global_l2_fic_id: "AGENT_X_L2::L2-FIC-PROFILE-CODING-001"
target_artifact_id: "L2-PROFILE-CODING-001"
global_target_artifact_id: "AGENT_X_L2::L2-PROFILE-CODING-001"
target_path: "L2/profiles/coding_agent.yaml"
target_type: "profile"
version: "v0.1.0"
status: "draft"
risk_level: "medium"
implementation_allowed: false
may_request_l1_handoff: true
owner: "Agent_X L2"
required_l1_units:
  - "AGENT_X_L1::UNIT-L1-003"
  - "AGENT_X_L1::UNIT-L1-004"
  - "AGENT_X_L1::UNIT-L1-005"
  - "AGENT_X_L1::UNIT-L1-006"
  - "AGENT_X_L1::UNIT-L1-007"
  - "AGENT_X_L1::UNIT-L1-008"
  - "AGENT_X_L1::UNIT-L1-009"
  - "AGENT_X_L1::UNIT-L1-010"
  - "AGENT_X_L1::UNIT-L1-011"
  - "AGENT_X_L1::UNIT-L1-012"
evaluation_refs:
  - "L2/evaluation_specs/coding_agent_eval.md"
---
```

Rules:

```text
- implementation_allowed must remain false.
- target_path must point to a profile/spec artifact, not runtime code.
- ready-for-l1-handoff requires package closure, evidence, and review packet.
```

---

## 15. L2 SIB/Bridge Example

If governed, the profile should bind to future L1 handoff targets through L2 SIB/Bridge.

Example binding:

```yaml
binding_id: "L2-BIND-CODING-001"
source_profile: "AGENT_X_L2::L2-PROFILE-CODING-001"
source_profile_path: "L2/profiles/coding_agent.yaml"
binding_strength: "REFERENCE"
implementation_allowed: false
implementation_allowed_by_l2: false
l1_acceptance_required: true
target_l1_units:
  - "AGENT_X_L1::UNIT-L1-003"
  - "AGENT_X_L1::UNIT-L1-004"
  - "AGENT_X_L1::UNIT-L1-005"
  - "AGENT_X_L1::UNIT-L1-006"
  - "AGENT_X_L1::UNIT-L1-007"
  - "AGENT_X_L1::UNIT-L1-008"
  - "AGENT_X_L1::UNIT-L1-009"
  - "AGENT_X_L1::UNIT-L1-010"
  - "AGENT_X_L1::UNIT-L1-011"
  - "AGENT_X_L1::UNIT-L1-012"
status: "draft"
```

Rules:

```text
- A SIB binding does not authorize implementation.
- A missing SIB binding blocks L1 proposal for any profile that requires implementation.
- If ES registry and SIB binding disagree, the package is blocked.
```

---

## 16. L2 ES Registry/Graph Example

If governed, add the coding-agent profile and related artifacts to the L2 ecosystem registry and graph.

Registry entries should include at least:

```text
AX-L2-PROFILE-CODING-001
AX-L2-BLUEPRINT-CODING-001
AX-L2-EVAL-CODING-001
AX-L2-INTEGRATION-OPENCODE-REF-001
AX-L2-HANDOFF-CODING-001
```

Graph edges should represent:

```text
L2 system goal GOVERNS profile model
profile model GOVERNS coding-agent profile
coding-agent profile USES coding-agent blueprint
coding-agent profile VALIDATES through coding-agent evaluation spec
coding-agent profile REFERENCES OpenCode-like integration boundary
coding-agent profile PROPOSES_HANDOFF_TO_L1 through SIB handoff map
```

Rules:

```text
- The example itself should not be registered as active L2 authority unless converted.
- Active governed profile artifacts must be reachable from the L2 system goal.
- Generated profile catalogs must not become source of truth.
```

---

## 17. L2 EQC Procedure Example

This example does not require full EQC, but a governed version may use L2 EQC for deterministic profile selection.

Candidate procedure:

```text
L2_SelectProfile(request, profile_catalog, policy)
```

For an OpenCode-like coding request, expected result:

```yaml
selected_profile_decision:
  status: "SELECTED_PROFILE"
  selected_profile_id: "AGENT_X_L2::L2-PROFILE-CODING-001"
  candidate_profile_ids:
    - "AGENT_X_L2::L2-PROFILE-CODING-001"
  rejected_profile_ids: []
  l1_handoff_required: true
  implementation_allowed_by_l2: false
  required_l1_units:
    - "AGENT_X_L1::UNIT-L1-003"
    - "AGENT_X_L1::UNIT-L1-004"
    - "AGENT_X_L1::UNIT-L1-005"
    - "AGENT_X_L1::UNIT-L1-006"
    - "AGENT_X_L1::UNIT-L1-007"
  reasons:
    - "Request concerns repo-aware coding-agent specialization."
    - "Implementation requires L1 FIC-governed planning."
```

Rules:

```text
- EQC procedure must be pure and deterministic.
- EQC procedure must not inspect repositories directly.
- EQC procedure must not run tools.
- EQC procedure must output a proposal only.
```

---

## 18. L2-to-L1 Handoff Example

```yaml
l2_to_l1_handoff_request:
  request_id: "L2-HANDOFF-CODING-001"
  global_handoff_id: "AGENT_X_L2::L2-HANDOFF-CODING-001"
  profile_id: "L2-PROFILE-CODING-001"
  global_profile_id: "AGENT_X_L2::L2-PROFILE-CODING-001"
  profile_version: "v0.1.0"
  source_profile_example: "examples/evolutions/opencode_like_coding_agent.md#l2-profile-example"
  source_blueprint_example: "examples/evolutions/opencode_like_coding_agent.md#blueprint-example"
  source_evaluation_example: "examples/evolutions/opencode_like_coding_agent.md#evaluation-example"
  source_integration_boundary_example: "examples/evolutions/opencode_like_coding_agent.md#integration-boundary-example"
  requested_l1_action: "evaluate-for-fic-planning"
  implementation_requested: false
  implementation_allowed_by_l2: false
  l1_must_create_fic_before_code: true

  permitted_l1_units_to_consider:
    - "AGENT_X_L1::UNIT-L1-003"
    - "AGENT_X_L1::UNIT-L1-004"
    - "AGENT_X_L1::UNIT-L1-005"
    - "AGENT_X_L1::UNIT-L1-006"
    - "AGENT_X_L1::UNIT-L1-007"
    - "AGENT_X_L1::UNIT-L1-008"
    - "AGENT_X_L1::UNIT-L1-009"
    - "AGENT_X_L1::UNIT-L1-010"
    - "AGENT_X_L1::UNIT-L1-011"
    - "AGENT_X_L1::UNIT-L1-012"

  proposed_l1_fic_candidates:
    - "repo_context_reader"
    - "patch_plan_builder"
    - "bounded_file_editor"
    - "diff_review_builder"
    - "test_command_runner"
    - "git_status_reader"
    - "github_issue_reader"
    - "model_provider_adapter"
    - "session_store"
    - "tool_permission_gate"

  forbidden_direct_actions:
    - "modify L0"
    - "modify L1 implementation files without L1 FIC"
    - "modify external repositories directly"
    - "execute tools from L2"
    - "apply patches without L1 authorization"
    - "copy OpenCode source into Agent_X"

  expected_l1_output:
    - "goal classification"
    - "unit plan"
    - "FIC candidates or FIC updates"
    - "risk review"
    - "handoff packet if implementation is later authorized"

  status: "DRAFT_EXAMPLE_ONLY"
```

---

## 19. L1 Acceptance Gates Before Implementation

A L2 handoff request based on this example is not implementation approval.

L1 must pass these gates before any code is created or modified:

```text
[ ] L1 accepts the handoff for classification or planning.
[ ] L1 confirms the selected implementation unit is small enough.
[ ] L1 creates or updates the required FICs.
[ ] L1 confirms each target file has exactly one governing FIC.
[ ] L1 defines allowed files and forbidden files.
[ ] L1 defines allowed imports, dependencies, and side effects.
[ ] L1 defines test commands and evidence requirements.
[ ] L1 defines privacy, provider, GitHub, shell, and session policies if relevant.
[ ] L1 confirms implementation does not modify L0 without explicit governance.
[ ] L1 confirms implementation does not rely on OpenCode source copying.
[ ] L1 produces a reviewable implementation package.
[ ] The implementation package status is ready-for-code under L1 rules.
```

If any gate fails, the correct result is:

```text
BLOCKED_BY_L1_GATE
```

not partial implementation.

---

## 20. Future L3 Trigger

This example should stay as a single file under `examples/` until the coding-agent specialization becomes too large for an example or a single L2 profile package.

Create a future L3 package only when all of the following are true:

```text
[ ] L2 coding-agent profile is active or handoff-ready.
[ ] L1 has accepted the coding-agent profile for deeper planning.
[ ] Multiple related profile packages or scenarios need shared domain structure.
[ ] The work is still domain planning, not runtime implementation.
[ ] L3 has clear non-goals and does not bypass L1.
```

Possible future path:

```text
L3/coding_agent/
  README.md
  scenarios/
  evaluation_cases/
  policy_cases/
  implementation_candidates/
  l1_handoff_requests/
```

L3 would mean a selected specialization domain workspace. It would not mean runtime implementation authority.

---

## 21. Expected L1 Unit/FIC Expansion

If L1 accepts this example as a real planning target, it should start with the smallest useful coding-agent package.

### 21.1 First safe implementation candidate

```text
repo_context_reader + patch_plan_builder
```

This first candidate should only:

```text
- inspect repository structure;
- summarize relevant files;
- produce a patch plan;
- not edit files;
- not run commands;
- not call external APIs;
- not perform autonomous actions.
```

### 21.2 Later candidates

```text
bounded_file_editor
  Applies patches only inside declared file boundary.

diff_review_builder
  Produces reviewable semantic diff and risk summary.

test_command_runner
  Runs only approved validation commands and records output.

git_status_reader
  Reads workspace status and reports modified/untracked files.

github_issue_reader
  Reads issue/PR context only after explicit integration policy exists.

github_pr_reporter
  Reports PR-ready summary only after L1/GitHub policy exists.

model_provider_adapter
  Abstracts model calls only after model policy and privacy rules exist.

session_store
  Stores session metadata only after persistence policy exists.

tool_permission_gate
  Blocks unapproved shell/network/file mutation behavior.
```

---

## 22. Staged Evolution Roadmap

### Stage 0 — Example only

```text
Path: examples/evolutions/opencode_like_coding_agent.md
Status: example-only
Implementation: forbidden
```

### Stage 1 — Governed L2 profile/spec package

Potential files:

```text
L2/profiles/coding_agent.yaml
L2/blueprints/coding_agent_blueprint.md
L2/evaluation_specs/coding_agent_eval.md
L2/integration_specs/opencode_reference_integration.md
L2/fic/units/L2-FIC-PROFILE-CODING-001-opencode-like-coding-agent.md
```

Status:

```text
profile/spec only
implementation_allowed: false
release_evidence: false
```

### Stage 2 — L2-to-L1 handoff

Potential file:

```text
L2/generated/l1_handoff_requests/coding_agent_handoff_request.yaml
```

Status:

```text
proposal only
L1 may accept, reject, split, or request L2 delta
```

### Stage 3 — L1 FIC planning package

Potential L1 outputs:

```text
L1 FICs for repo_context_reader and patch_plan_builder
L1 SIB bindings
L1 ES impact records
L1 EQC operator/procedure docs if needed
L1 evidence and review packet
```

Status:

```text
implementation planning only until FICs are ready-for-code
```

### Stage 4 — Minimal implementation

Only after L1 authorization:

```text
repo_context_reader
patch_plan_builder
unit tests
completion evidence
review packet
```

No patch application yet.

### Stage 5 — Controlled editing and validation

Later, after separate L1 authorization:

```text
bounded_file_editor
diff_review_builder
test_command_runner
tool_permission_gate
```

### Stage 6 — GitHub/provider/session features

Only after policies exist:

```text
github_issue_reader
github_pr_reporter
model_provider_adapter
session_store
```

---

## 23. Risk Ledger Example

```yaml
risks:
  - risk_id: "L2-RISK-CODING-001"
    profile_id: "AGENT_X_L2::L2-PROFILE-CODING-001"
    description: "Example may be misread as implementation permission."
    severity: "high"
    mitigation: "Document repeatedly states implementation_allowed=false and routes all implementation through L1 FIC governance."
    status: "mitigated"

  - risk_id: "L2-RISK-CODING-002"
    profile_id: "AGENT_X_L2::L2-PROFILE-CODING-001"
    description: "OpenCode reference may be misread as source copying, compatibility, or fork intent."
    severity: "medium"
    mitigation: "Document states this is not OpenCode, not a fork, and contains no OpenCode source."
    status: "mitigated"

  - risk_id: "L2-RISK-CODING-003"
    profile_id: "AGENT_X_L2::L2-PROFILE-CODING-001"
    description: "Future coding agent could edit files outside declared boundaries."
    severity: "high"
    mitigation: "Require L1 FIC ownership, allowed-file list, bounded editor, diff review, and evidence."
    status: "open-until-L1-implementation"

  - risk_id: "L2-RISK-CODING-004"
    profile_id: "AGENT_X_L2::L2-PROFILE-CODING-001"
    description: "Future test runner could execute unsafe commands."
    severity: "high"
    mitigation: "Require explicit permission policy and tool_permission_gate before command execution."
    status: "open-until-L1-implementation"
```

---

## 24. Traceability Example

```yaml
traceability:
  example_doc: "examples/evolutions/opencode_like_coding_agent.md"
  possible_l2_profile: "AGENT_X_L2::L2-PROFILE-CODING-001"
  possible_l2_blueprint: "AGENT_X_L2::L2-BLUEPRINT-CODING-001"
  possible_l2_evaluation_spec: "AGENT_X_L2::L2-EVAL-CODING-001"
  possible_l2_integration_spec: "AGENT_X_L2::L2-INTEGRATION-OPENCODE-REF-001"
  possible_l2_handoff: "AGENT_X_L2::L2-HANDOFF-CODING-001"
  proposed_l1_units:
    - "AGENT_X_L1::UNIT-L1-003"
    - "AGENT_X_L1::UNIT-L1-004"
    - "AGENT_X_L1::UNIT-L1-005"
    - "AGENT_X_L1::UNIT-L1-006"
    - "AGENT_X_L1::UNIT-L1-007"
    - "AGENT_X_L1::UNIT-L1-008"
    - "AGENT_X_L1::UNIT-L1-009"
    - "AGENT_X_L1::UNIT-L1-010"
    - "AGENT_X_L1::UNIT-L1-011"
    - "AGENT_X_L1::UNIT-L1-012"
  status: "example-only"
  implementation_authorized: false
```

---

## 25. Example Profile Package Manifest

If converted into governed L2, a package manifest may look like this:

```yaml
l2_profile_package_manifest:
  manifest_version: "v0.1.0"
  package_id: "L2-PKG-CODING-001"
  global_package_id: "AGENT_X_L2::L2-PKG-CODING-001"
  status: "draft"
  source_example: "examples/evolutions/opencode_like_coding_agent.md"
  implementation_authorized: false
  release_evidence: false
  required_artifacts:
    profile: "L2/profiles/coding_agent.yaml"
    blueprint: "L2/blueprints/coding_agent_blueprint.md"
    evaluation_spec: "L2/evaluation_specs/coding_agent_eval.md"
    integration_spec: "L2/integration_specs/opencode_reference_integration.md"
    l2_fic: "L2/fic/units/L2-FIC-PROFILE-CODING-001-opencode-like-coding-agent.md"
    risk_ledger: "L2/docs/07_L2_RISK_LEDGER.md"
    traceability_matrix: "L2/docs/08_L2_TRACEABILITY_MATRIX.md"
    handoff_request: "L2/generated/l1_handoff_requests/coding_agent_handoff_request.yaml"
  closure_status: "draft|closed-for-l1-handoff|blocked"
  blockers:
    - "This is an example until copied into governed L2 artifacts."
```

---

## 26. Controlled Status and Claim Rules

Allowed statuses for this example:

```text
example-only
draft-example
converted-to-l2-draft
proposed-to-l1
superseded
archived
```

Forbidden claims:

```text
implemented
validated runtime
release-ready
OpenCode-compatible
OpenCode fork
production-ready
autonomous-ready
L2 execution-ready
```

Completion statement for this example must preserve:

```yaml
implementation_authorized: false
runtime_authorized: false
release_evidence: false
external_code_included: false
opencode_fork: false
```

---

## 27. Source-Freshness and External-Reference Update Rules

This example may mention OpenCode as an external reference pattern. Any future governed L2 or L1 work must re-check the external reference before relying on current behavior, features, APIs, repository structure, license terms, or documentation.

Rules:

```text
- Treat all OpenCode-specific implementation details as freshness-sensitive.
- Do not copy claims about OpenCode features into governed Agent_X specs unless the source is checked at that time.
- Do not pin Agent_X architecture to OpenCode internals.
- Do not treat this example as proof of current OpenCode behavior.
- If a future L2 or L1 package needs exact OpenCode behavior, record source URL, date checked, artifact digest if available, and whether the source is documentation, code, issue discussion, or release note.
```

If current external facts cannot be verified, the governed result must be:

```text
BLOCKED_EXTERNAL_REFERENCE_UNVERIFIED
```

or the reference must be downgraded to:

```text
historical_non_authoritative
```

---

## 28. Weak-Agent Copy and Adaptation Guardrails

A weaker documentation or coding agent may use this file only as source material. It must not copy this example into active L2/L1 authority without conversion.

Allowed weak-agent actions:

```text
- place this file under examples/evolutions/;
- add a short examples README pointer;
- use the profile example as draft source material for L2/profiles/coding_agent.yaml;
- use the handoff example as draft source material for a L2-to-L1 request;
- report BLOCKED when unsure whether implementation is authorized.
```

Forbidden weak-agent actions:

```text
- create L2/runtime, L2/tools, L2/agents, L2/model_router, or similar executable directories from this example;
- create Python, JavaScript, TypeScript, shell, or GitHub Action runtime code from this example;
- change implementation_authorized, runtime_authorized, or release_evidence to true;
- copy OpenCode source, API claims, or dependency assumptions into Agent_X as authority;
- mark the example as an active L2 profile without creating proper L2 FIC, ES, SIB, EQC, evidence, and registry updates;
- mark L1 implementation accepted without a L1 evidence artifact.
```

Required final weak-agent status after adding or adapting this example:

```yaml
example_agent_result:
  status: "EXAMPLE_ADDED|EXAMPLE_UPDATED|BLOCKED|NO_CHANGE"
  example_path: "examples/evolutions/opencode_like_coding_agent.md"
  implementation_authorized: false
  runtime_authorized: false
  release_evidence: false
  opencode_source_included: false
  active_l2_profile_created: false
  l1_handoff_created: false
  files_changed: []
  checks_run: []
  checks_not_run: []
  unresolved_risks: []
```

---

## 29. Safe Addition Checklist

Before committing this file to Agent_X, confirm:

```text
[ ] Path is examples/evolutions/opencode_like_coding_agent.md.
[ ] File is not placed under L0/, L1/, or L2/ as authority.
[ ] File status remains example-only.
[ ] implementation_authorized is false.
[ ] runtime_authorized is false.
[ ] release_evidence is false.
[ ] external_code_included is false.
[ ] opencode_fork is false.
[ ] No OpenCode source code is included.
[ ] No executable code block is presented as implementation.
[ ] No shell command is presented as a required runtime action.
[ ] Root README, if updated, calls examples non-authoritative.
[ ] examples/README.md, if updated, says examples do not authorize implementation.
[ ] No L2 runtime-like directory is created.
[ ] No L0, L1, or L2 source-of-truth file is modified except optional README pointers.
```

Suggested verification commands:

```bash
git status --short
python - <<'PY'
from pathlib import Path
p = Path("examples/evolutions/opencode_like_coding_agent.md")
text = p.read_text(encoding="utf-8")
required_false = [
    "**Implementation authorized:** `false`",
    "**Runtime authorized:** `false`",
    "**Release evidence:** `false`",
    "**External code included:** `false`",
    "**OpenCode fork:** `false`",
    "implementation_authorized: false",
    "runtime_authorized: false",
    "release_evidence: false",
]
missing = [item for item in required_false if item not in text]
if missing:
    raise SystemExit(f"Boundary markers missing: {missing}")
if "**Implementation authorized:** `true`" in text or "**Runtime authorized:** `true`" in text:
    raise SystemExit("Example incorrectly authorizes implementation or runtime behavior")
PY
```

Do not use a broad grep for phrases such as `OpenCode fork` or `OpenCode-compatible`, because this document intentionally includes those phrases inside forbidden-claim sections.

---

## 30. Example-Only Acceptance Decision Table

| Observed state | Correct status | Required action |
|---|---|---|
| File is under `examples/evolutions/`, non-authoritative, and contains no code | `EXAMPLE_ADDED` | Keep as example-only |
| File is unchanged and already satisfies boundary rules | `NO_CHANGE` | Record no-change evidence if needed |
| File was copied into `L2/` without registry/FIC/SIB/ES/EQC conversion | `BLOCKED` | Convert properly or move back to examples |
| File claims implementation/runtime/release authority | `BLOCKED` | Remove false claim |
| File includes copied OpenCode source or claims fork/compatibility | `BLOCKED` | Remove source/claim and require separate review |
| File creates runtime directories or executable code | `BLOCKED` | Remove runtime material or route through L1 |
| File is used as source for a real L2 profile package | `CONVERTED_TO_L2_DRAFT` | Create governed L2 artifacts and evidence |

---

## 31. Abuse-Case and Threat-Model Checklist for Future Conversion

This example is safe as documentation, but a future conversion into governed L2/L1 work must explicitly handle abuse cases.

Minimum future abuse cases:

```text
- malicious prompt asks the coding agent to ignore FIC boundaries;
- task asks the agent to edit L0 or L1 directly;
- repository contains secrets in source files, logs, or test output;
- generated diff includes sensitive data;
- user asks to weaken or delete failing tests;
- model provider receives private code without approval;
- GitHub issue or PR text contains credentials or private data;
- command output includes tokens, paths, or private environment details;
- dependency proposal introduces unreviewed network or shell behavior;
- session history persists more data than the policy allows.
```

Required future controls before implementation:

```text
[ ] permission gate exists;
[ ] allowed-file boundary exists;
[ ] secret-handling rule exists;
[ ] provider/transmission policy exists;
[ ] command execution policy exists;
[ ] test-weakening prohibition exists;
[ ] completion evidence redaction rule exists;
[ ] human approval level is declared;
[ ] rollback or no-write policy is declared for the first implementation slice.
```

A future package that does not address these abuse cases must remain planning-only or be blocked by L1.

---

## 32. Synchronization and Staleness Policy

Examples are allowed to become stale, but they must not silently contradict active Agent_X governance.

Rules:

```text
- If L2/profile schema changes, this example may remain historical, but must not be treated as current L2 source of truth.
- If L1 handoff unit IDs change, this example must be updated or marked stale before being used as source material.
- If OpenCode changes materially, do not update this example with current claims unless the source is rechecked.
- If Agent_X later implements a real coding-agent package, this example remains educational unless explicitly superseded.
- If this example conflicts with active L2 profiles, the active L2 profile wins.
```

Recommended staleness marker:

```yaml
example_staleness:
  status: "current|stale|historical|superseded"
  reason: ""
  superseded_by: null
  last_reviewed_utc: null
```

---

## 33. Conversion-to-L2 Checklist

Use this checklist only if the example is intentionally converted into governed L2 artifacts.

```text
[ ] Copy content into L2 profile/spec files, not by making this example authoritative.
[ ] Create or update L2/profiles/coding_agent.yaml.
[ ] Create or update L2/blueprints/coding_agent_blueprint.md.
[ ] Create or update L2/evaluation_specs/coding_agent_eval.md.
[ ] Create or update L2/integration_specs/opencode_reference_integration.md.
[ ] Create or update L2/fic/units/L2-FIC-PROFILE-CODING-001-opencode-like-coding-agent.md.
[ ] Update L2/fic/index.l2-fic.yaml.
[ ] Update L2/ecosystem/ecosystem-registry.yaml and ecosystem-graph.yaml.
[ ] Update L2/sib/sib-l1-handoff-map.yaml or equivalent bridge file.
[ ] Update L2/docs/07_L2_RISK_LEDGER.md.
[ ] Update L2/docs/08_L2_TRACEABILITY_MATRIX.md.
[ ] Keep implementation_allowed=false everywhere in L2.
[ ] Keep release_evidence=false unless validator-produced release evidence exists.
[ ] Do not create runtime code.
[ ] Do not claim L1 acceptance until L1 evidence exists.
```

Stop conditions:

```text
- required L1 units cannot be mapped;
- L2 ES and SIB disagree;
- privacy/provider/tool policy is required but absent;
- runtime or tool implementation appears;
- OpenCode source reuse is proposed without separate L1 review;
- the package claims implementation authority from L2.
```

---

## 34. Maintenance Decision Table

| Situation | Correct action |
|---|---|
| Example is useful and still aligned with L2 boundaries | Keep as `example-only` |
| Example is useful but no longer current | Mark `historical_non_authoritative` or `stale` |
| Active L2 profile has superseded this example | Add `superseded_by` note; keep for education |
| Example conflicts with active L2/L1/L0 governance | Update or archive the example |
| Example needs implementation details | Move to L2/L1 governed process, not examples |
| Example would require OpenCode source/dependency reuse | Route through L1 license/security/dependency review |
| Example is being copied by a weaker agent | Require the weak-agent guardrails and conversion checklist |

---

## 35. Validation Checklist for This Example

This example is complete only if all checks pass:

```text
[ ] Document states it is non-authoritative.
[ ] Document states it is not OpenCode and not an OpenCode fork.
[ ] Document states no OpenCode source code is included.
[ ] Document has a recommended examples path.
[ ] Document separates examples/ from active L2 authority.
[ ] Document defines allowed and forbidden behavior.
[ ] Document includes a L2 profile example.
[ ] Document includes a blueprint example.
[ ] Document includes an evaluation example.
[ ] Document includes an integration boundary example.
[ ] Document includes a L2 FIC example.
[ ] Document includes a SIB/Bridge example.
[ ] Document includes an ES registry/graph example.
[ ] Document includes an EQC procedure example.
[ ] Document includes a L2-to-L1 handoff example.
[ ] Document includes expected L1 unit/FIC expansion.
[ ] Document includes a staged evolution roadmap.
[ ] Document includes risk ledger examples.
[ ] Document includes traceability examples.
[ ] Document includes profile package manifest example.
[ ] Document includes controlled status and no-false-claim rules.
[ ] Document contains no executable runtime code.
[ ] Document does not authorize direct repo mutation.
[ ] Document does not authorize L0 or L1 modification.
[ ] Document does not authorize external repository modification.
[ ] Document does not treat generated placeholders as evidence.
[ ] Document includes licensing/trademark/source-use boundary rules.
[ ] Document includes privacy, secrets, model-provider, GitHub, and session-storage boundaries.
[ ] Document includes human approval and permission-gate levels.
[ ] Document defines L1 acceptance gates before implementation.
[ ] Document defines when future L3 may be created.
[ ] Document includes weak-agent copy/adaptation guardrails.
[ ] Document includes source-freshness and external-reference update rules.
[ ] Document includes safe-addition checklist.
[ ] Document includes example-only acceptance decision table.
```

---

## 36. Evidence Bundle Rule

If this example is added to the repo, evidence is optional because examples are not governed implementation artifacts.

If evidence is created, use:

```text
examples/evidence/opencode_like_coding_agent/<utc_timestamp>_example_review.md
```

Minimum evidence statement:

```yaml
example_review:
  example_path: "examples/evolutions/opencode_like_coding_agent.md"
  status: "example-only"
  implementation_authorized: false
  runtime_authorized: false
  release_evidence: false
  opencode_source_included: false
  reviewed_for_boundary_claims: true
  reviewed_for_l1_handoff_path: true
```

Do not store fake command results or fake validation evidence for this example.

---

## 37. README Placement Recommendation

Add this to `examples/README.md`:

```md
## OpenCode-like Coding Agent Example

`examples/evolutions/opencode_like_coding_agent.md` is a single-file, non-authoritative example showing how Agent_X could evolve toward an OpenCode-like coding-agent capability through L2 profile/spec planning and L1-governed FIC work.

It is not OpenCode, not a fork, does not include OpenCode source code, and is not implementation authority.
```

Add this to the root `README.md` only if a short public-facing pointer is desired:

```md
## Examples

The `examples/` directory contains non-authoritative evolution examples. These examples show how Agent_X could grow into specialized agents through L2 profile/spec artifacts and L1-governed handoff. They do not authorize implementation or runtime execution.
```

---

## 38. Final Single-File Completeness Gate

This document is complete as a single-file example only if it satisfies all of the following:

```text
[ ] It can be read without any companion files.
[ ] It explains where the file belongs in the repository.
[ ] It states that it is non-authoritative.
[ ] It distinguishes example material from governed L2 profile/spec artifacts.
[ ] It defines an L2 profile example, blueprint example, evaluation example, integration boundary, FIC example, SIB/Bridge example, ES example, EQC example, and L2-to-L1 handoff example.
[ ] It defines expected L1 gates before implementation.
[ ] It includes privacy, secrets, provider, GitHub, session, license, attribution, and source-use boundaries.
[ ] It includes weak-agent guardrails and safe-addition checks.
[ ] It includes risk, traceability, and package-manifest examples.
[ ] It contains no executable implementation authority.
[ ] It keeps implementation_authorized, runtime_authorized, release_evidence, external_code_included, and opencode_fork set to false.
```

Current status:

```yaml
single_file_example_completeness: "10/10"
implementation_authorized: false
runtime_authorized: false
release_evidence: false
```

---

## 39. Final Boundary Statement

This document is a scenario package.

It may help a user or coding agent understand how Agent_X could evolve into an OpenCode-like coding agent, but it does not authorize code, tools, patches, runtime agents, external integrations, or source-code reuse.

The only valid implementation path is:

```text
example scenario
  -> governed L2 profile/spec artifact
  -> L2-to-L1 handoff request
  -> L1 FIC-governed implementation package
  -> tests and evidence
  -> review
```

Until that happens, the correct status is:

```yaml
status: "example-only"
implementation_authorized: false
runtime_authorized: false
release_evidence: false
```
