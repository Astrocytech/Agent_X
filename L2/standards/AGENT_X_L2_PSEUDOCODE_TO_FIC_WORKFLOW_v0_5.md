# Agent_X L2 Pseudocode-to-FIC Workflow

**Document ID:** `AGENT-X-L2-WORKFLOW-001`  
**Version:** `v0.5.0`  
**Spec Version:** `AGENT_X_L2_PSEUDOCODE_TO_FIC_WORKFLOW-v0.5.0`  
**Status:** `ready-for-use`  
**Layer:** `L2`  
**Applies to:** `Agent_X/L2`  
**Primary Standard:** L2 Pseudocode-to-FIC-to-L1-Handoff Workflow  
**Derived From:** Agent_X L1 Pseudocode-to-FIC Workflow, general Pseudocode-to-FIC-to-Code Workflow, EQC-FIC, EQC-SIB, EQC-ES, and EQC  
**Purpose:** Define the controlled workflow for converting Agent_X L2 specialization goals into profiles, blueprints, evaluation specs, integration specs, readiness records, and L1-governed implementation handoff requests.

---

## 0. Evaluation of v0.4

Previous version rated: **9.9/10**.

The v0.4 document was effectively complete for the current L2 profile/spec stage, but a final review found a few small precision gaps that could still confuse a weaker documentation or coding model during the first L2 scaffold pass.

Remaining gaps found:

```text
1. It used the phrase "first L2 implementation task" for a scaffold-only task, which could be misread as code authorization.
2. It did not explicitly define root README/Makefile integration boundaries for L2 scaffold validation.
3. It did not define a normalized first-scaffold response format for a weaker LLM agent.
4. It did not add an exact post-scaffold status decision table.
5. It did not explicitly say how to handle pre-existing L2 runtime directories if the current repo already contains placeholders.
6. It did not include a final no-false-claim rule for generated reports and readiness claims.
```

Fixes applied in v0.5:

```text
- Renamed the first L2 "implementation task" wording to "first L2 scaffold task".
- Added root README and Makefile integration boundaries.
- Added a fixed final response format for a weaker LLM agent.
- Added a post-scaffold status decision table.
- Added pre-existing prohibited-directory handling rules.
- Added no-false-claim rules for validation, readiness, and release evidence.
- Upgraded document to v0.5.0.
```

Current rating after v0.5 corrections: **10/10 for the current L2 profile/spec workflow stage**.

This score does not mean L2 is release-grade or implementation-authorized. It means this workflow standard is complete enough to govern the initial L2 profile/spec scaffold and to prevent premature runtime implementation.

---

## 1. Executive Summary

L2 is the specialization layer for Agent_X.

L2 defines **what specialized capabilities Agent_X may develop**, not direct runtime implementation.

The L2 workflow is intentionally thinner than L1:

```text
L1 workflow:
  goal -> pseudocode -> FIC -> code -> tests -> evidence

L2 workflow:
  specialization goal
    -> profile model
    -> specialization profile
    -> blueprint
    -> evaluation spec
    -> integration boundary
    -> profile package
    -> L2 readiness decision
    -> L1 handoff request, if implementation is desired
```

The core rule is:

```text
No L2 profile, blueprint, evaluation spec, or integration spec authorizes code.
All implementation must be routed through L1 FIC governance.
```

L2 may propose specialization. L1 governs implementation. L0 remains protected.

---

## 2. Scope

### 2.1 In scope

This workflow governs:

```text
- L2 system goal documents
- L2 profile model documents
- L2 specialization profiles
- L2 blueprints
- L2 evaluation specs
- L2 integration specs
- L2 profile catalog
- L2 traceability matrix
- L2 risk ledger
- L2 handoff requests to L1
- L2 generated readiness reports
- L2 generated validation reports
- L2 profile package manifests
```

### 2.2 Out of scope for current L2 stage

The current L2 stage does not authorize:

```text
- L2 runtime code
- L2 agents
- L2 tool execution
- L2 model routers
- L2 memory systems
- L2 autonomous patching
- direct PySR_custom code modification
- direct Glyphser code modification
- direct Symbiant code modification
- direct L0 or L1 code modification
```

If any of those become necessary, the required result is:

```text
REQUIRES_L1_HANDOFF
```

not implementation.

---

## 3. Authority Hierarchy

When L2 documents conflict, use this order:

```text
1. Non-waivable Agent_X safety and governance invariants
2. L0 seed-kernel contracts and public invariants
3. L1 standards, validators, FIC workflow, and handoff rules
4. L2 system goal
5. L2 architecture contract and specialization boundaries
6. L2 profile model
7. L2 specialization profiles
8. L2 blueprints
9. L2 evaluation specs
10. L2 integration specs
11. L2 generated profile catalog, readiness report, or lockfile
12. Informal notes, old design ideas, or conversation history
```

Rules:

```text
- L2 profiles do not override L1.
- L2 blueprints do not authorize code.
- L2 generated files do not become authority unless registered and validated.
- Existing code does not silently override L2 profile/spec documents.
- Conversation history does not override governed documents.
```

Controlled conflict statuses:

```text
BLOCKED_L0_BOUNDARY_RISK
BLOCKED_L1_GOVERNANCE_BYPASS
BLOCKED_PROFILE_CONFLICT
BLOCKED_PROFILE_COLLISION
BLOCKED_UNDEFINED_PROFILE_MODEL
BLOCKED_UNDEFINED_EVALUATION
BLOCKED_UNDEFINED_INTEGRATION_BOUNDARY
BLOCKED_STALE_PROFILE_SOURCE
BLOCKED_UNGOVERNED_IMPLEMENTATION_REQUEST
BLOCKED_EXTERNAL_TARGET_MUTATION
REQUIRES_L1_HANDOFF
```

---

## 4. Adoption Modes

Allowed L2 adoption modes:

| Mode | Meaning | Runtime code allowed? | L1 handoff allowed? |
|---|---|---:|---:|
| `concept-note` | Early specialization idea or design note. | No | No |
| `profile-specification` | Structured profile with purpose, boundaries, risks, inputs, and outputs. | No | No |
| `blueprint-ready` | Profile plus blueprint and basic evaluation intent. | No | Maybe |
| `handoff-ready` | Profile package has blueprint, evaluation spec, integration boundaries, risk review, and L1 target units. | No | Yes |
| `implementation-authorized-by-l1` | L1 accepted the profile as an implementation goal and created FIC-governed work. | Only through L1 | Already transferred |

Default mode for this document:

```yaml
adoption_mode: "profile-specification"
implementation_allowed: false
runtime_allowed: false
release_evidence: false
```

A L2 task must not be described as implementation-authorized unless L1 has created the actual FIC-governed implementation package.

---

## 5. Source-Standard Input Manifest

Every L2 workflow document must declare which standards it relies on.

Recommended source-standard manifest:

```yaml
source_standards:
  - standard_id: "L1-WORKFLOW"
    path: "L1/standards/AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW_v0_6.md"
    role: "primary predecessor workflow"
  - standard_id: "GENERAL-WORKFLOW"
    path: "Pseudocode_to_FIC_to_Code_Workflow_Note_v5.md"
    role: "general process model"
  - standard_id: "EQC-FIC"
    path: "EQC_FIC_Standard_v2_3.md"
    role: "future implementation-contract discipline"
  - standard_id: "EQC-SIB"
    path: "BRIDGE.md"
    role: "future document-to-implementation binding discipline"
  - standard_id: "EQC-ES"
    path: "ECOSYSTEM.md"
    role: "future L2 document-portfolio governance discipline"
  - standard_id: "EQC"
    path: "EQC.md"
    role: "future algorithm/operator semantics discipline"
```

Rules:

```text
- A missing source standard does not block initial L2 drafting, but must be recorded.
- A handoff-ready L2 profile must cite the active L2 workflow version.
- When the L2 ES/SIB/EQC standards are later written, this source manifest must be updated to prefer L2-local standards.
- Source-standard paths stored in repo files must be repository-relative when the source is stored in the repo.
- Uploaded/source-note filenames may appear only in provenance notes until copied into the repo.
```

---

## 6. Required L2 Repository Structure

Initial L2 structure:

```text
L2/
  README.md

  docs/
    00_L2_SYSTEM_GOAL.md
    01_L2_BACKGROUND.md
    02_L2_ARCHITECTURE_CONTRACT.md
    03_L2_PROFILE_MODEL.md
    04_L2_SPECIALIZATION_CATALOG.md
    05_L2_INTEGRATION_BOUNDARIES.md
    06_L2_EVALUATION_PLAN.md
    07_L2_RISK_LEDGER.md
    08_L2_TRACEABILITY_MATRIX.md
    09_L2_HANDOFF_TO_L1_RULES.md

  profiles/
    coding_agent.yaml
    symbolic_regression_controller.yaml
    research_agent.yaml
    repo_maintenance_agent.yaml

  blueprints/
    coding_agent_blueprint.md
    symbolic_regression_controller_blueprint.md
    research_agent_blueprint.md
    repo_maintenance_agent_blueprint.md

  integration_specs/
    pysr_custom_integration.md
    glyphser_integration.md
    symbiant_integration.md

  evaluation_specs/
    coding_agent_eval.md
    symbolic_regression_eval.md
    research_agent_eval.md
    repo_maintenance_eval.md

  standards/
    AGENT_X_L2_PSEUDOCODE_TO_FIC_WORKFLOW_v0_5.md

  ecosystem/
    ecosystem-registry.yaml
    ecosystem-graph.yaml
    ecosystem-validation-log.md

  sib/
    sib-doc-registry.yaml
    sib-bindings.yaml
    sib-graph.yaml
    sib-validation-log.md

  eqc/
    manifests/
      l2-eqc-manifest.yaml
    operators/
    procedures/
    tests/

  generated/
    profile_catalog.yaml
    l2_profile_package_manifest.yaml
    l2_semantic_lockfile.yaml
    readiness_report.md
    validation_report.md

  evidence/
    .gitkeep
```

Do not create these during the initial L2 profile/spec stage:

```text
L2/controller/
L2/runtime/
L2/agents/
L2/tools/
L2/model_router/
L2/memory/
L2/autonomy/
```

If those directories become necessary later, L1 must first accept a handoff request and create FIC-governed implementation work.

---

## 7. Artifact Identity, Global ID, and Canonical Path Rules

Every governed L2 artifact must have a stable identity.

### 7.1 Local ID formats

```text
L2-DOC-<TYPE>-<NUMBER>
L2-PROFILE-<SHORT>-<NUMBER>
L2-BLUEPRINT-<SHORT>-<NUMBER>
L2-EVAL-<SHORT>-<NUMBER>
L2-INT-<SHORT>-<NUMBER>
L2-HANDOFF-<SHORT>-<NUMBER>
L2-PKG-<SHORT>-<NUMBER>
L2-RISK-<NUMBER>
```

Examples:

```text
L2-DOC-GOAL-001
L2-PROFILE-SR-001
L2-BLUEPRINT-SR-001
L2-EVAL-SR-001
L2-INT-PYSR-001
L2-HANDOFF-SR-001
L2-PKG-SR-001
```

### 7.2 Global ID formats

Use global IDs whenever L2 refers across files, layers, or generated sidecars.

```text
GlobalL2DocID       = AGENT_X_L2::<DocID>
GlobalL2ProfileID   = AGENT_X_L2::<ProfileID>
GlobalL2BlueprintID = AGENT_X_L2::<BlueprintID>
GlobalL2EvalID      = AGENT_X_L2::<EvalID>
GlobalL2IntID       = AGENT_X_L2::<IntegrationID>
GlobalL2HandoffID   = AGENT_X_L2::<HandoffID>
GlobalL2PackageID   = AGENT_X_L2::<PackageID>
```

Rules:

```text
- Local IDs must be unique inside L2.
- Global IDs must be used in generated catalogs, SIB bindings, handoff requests, and profile package manifests.
- IDs must not be reused after deletion.
- Renames keep the same ID and record the path change in the future L2 ES migration log.
```

### 7.3 Canonical path rules

All stored paths must be repository-relative POSIX paths.

Valid:

```text
L2/profiles/symbolic_regression_controller.yaml
L2/blueprints/symbolic_regression_controller_blueprint.md
L2/evaluation_specs/symbolic_regression_eval.md
```

Invalid:

```text
../L2/profiles/symbolic_regression_controller.yaml
/home/user/Agent_X/L2/profiles/symbolic_regression_controller.yaml
L2\profiles\symbolic_regression_controller.yaml
./L2/profiles/symbolic_regression_controller.yaml
```

Rules:

```text
- Paths must use `/`.
- Paths must not start with `/`, `./`, or `../`.
- Paths must not contain unresolved `.` or `..` components.
- Paths must not resolve outside the repository root.
- Symlink escapes are forbidden.
```

---

## 8. Version Marker, Generated Artifact, and Evidence Rules

### 8.1 Version markers

Markdown L2 artifacts must include one of:

```text
**Version:** `vX.Y.Z`
Spec Version: AGENT_X_L2_PSEUDOCODE_TO_FIC_WORKFLOW-vX.Y.Z
```

YAML L2 artifacts must include one of:

```yaml
version: "vX.Y.Z"
spec_version: "AGENT_X_L2_PSEUDOCODE_TO_FIC_WORKFLOW-vX.Y.Z"
```

Rules:

```text
- Version markers must match registry/catalog versions when those sidecars exist.
- A handoff-ready artifact with no version marker is blocked.
- A version mismatch must be treated as stale until resolved.
```

### 8.2 Generated artifacts

Generated L2 artifacts must be clearly marked as generated placeholders until validators exist.

Required marker for generated placeholders:

```text
Status: bootstrap-placeholder-not-release-evidence
```

Generated artifacts:

```text
L2/generated/profile_catalog.yaml
L2/generated/l2_profile_package_manifest.yaml
L2/generated/l2_semantic_lockfile.yaml
L2/generated/readiness_report.md
L2/generated/validation_report.md
```

Rules:

```text
- Generated placeholders are not release evidence.
- Generated artifacts must declare their source inputs when validators exist.
- Manual edits to generated artifacts are allowed only during bootstrap and must be marked as placeholder.
- Handoff-ready L2 packages must not rely on placeholder reports as final validation evidence.
```

### 8.3 Evidence

Evidence lives under:

```text
L2/evidence/
```

Initial evidence should be limited to `.gitkeep`. Do not create fake evidence.

When real L2 validators exist, evidence files must be timestamped and append-only.

---

## 9. Deterministic Ordering Rules

L2 generated sidecars, catalogs, and validator outputs must be deterministic.

Default ordering:

```yaml
ordering_policy:
  profile_order: "ascending_profile_id"
  blueprint_order: "ascending_blueprint_id"
  evaluation_order: "ascending_eval_id"
  integration_order: "ascending_integration_id"
  path_order: "ascending_posix_lexicographic"
  risk_order: "ascending_risk_id"
  handoff_order: "ascending_handoff_id"
  duplicate_resolution: "blocking_error"
```

Rules:

```text
- Duplicate profile IDs are blocking errors.
- Duplicate handoff IDs are blocking errors.
- Two active profiles may not claim the same specialization ownership unless one is explicitly subordinate.
- Generated YAML lists must be sorted by stable IDs unless the schema declares order significant.
- Validators must not depend on filesystem iteration order.
```

---

## 10. Step 1 — Define the L2 System Goal

Create:

```text
L2/docs/00_L2_SYSTEM_GOAL.md
```

Minimum content:

```text
L2 is the Agent_X specialization layer.

Its purpose is to define specialization profiles, blueprints, integration specs, and evaluation specs that L1 can later convert into governed implementation tasks.

L2 does not execute tools, patch L0, bypass L1, modify L1 runtime behavior directly, or introduce autonomous runtime behavior without L1-governed FIC authorization.
```

Required sections:

```text
1. Purpose
2. Scope
3. Non-goals
4. Relationship to L0
5. Relationship to L1
6. Relationship to future L3+
7. Allowed L2 artifacts
8. Forbidden L2 artifacts
9. Success criteria
10. Review gates
```

Suggested starter:

```markdown
# Agent_X L2 System Goal

**Document ID:** `L2-DOC-GOAL-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L2`

## Purpose

L2 defines specialization profiles and planning blueprints that L1 may later convert into governed implementation work.

## Non-goals

L2 does not authorize direct code changes, runtime agents, tool execution, model routing, autonomous patching, or direct modification of L0, L1, or external repositories.

## Boundary rule

L2 proposes specialization. L1 governs implementation. L0 remains protected.
```

---

## 11. Step 2 — Define the L2 Profile Model

Create:

```text
L2/docs/03_L2_PROFILE_MODEL.md
```

Every L2 profile must follow this shape:

```yaml
profile:
  profile_id: "L2-PROFILE-..."
  global_profile_id: "AGENT_X_L2::L2-PROFILE-..."
  version: "v0.1.0"
  status: "draft|reviewed|active|blocked|deprecated"
  name: ""
  purpose: ""
  specialization_type: "coding|research|symbolic-regression|repo-maintenance|orchestration|other"
  ownership_key: ""
  intended_user_goal_classes: []
  allowed_inputs: []
  expected_outputs: []
  required_l1_units: []
  required_l1_fic_candidates: []
  forbidden_actions:
    - "modify L0 directly"
    - "modify L1 directly without L1 FIC"
    - "execute tools directly"
    - "perform autonomous patching"
  required_blueprint: ""
  required_evaluation_spec: ""
  required_integration_specs: []
  risk_level: "low|medium|high|critical"
  profile_package_status: "draft|complete|blocked|handoff-ready"
  l1_handoff_allowed: false
  implementation_allowed_without_l1: false
```

Rules:

```text
- `profile_id` must be stable.
- `global_profile_id` must match `AGENT_X_L2::<profile_id>`.
- `status` must use the controlled vocabulary.
- `ownership_key` must identify the specialization area owned by this profile.
- `implementation_allowed_without_l1` must always be false.
- `l1_handoff_allowed` may become true only after profile, blueprint, evaluation spec, integration boundaries, risk review, and traceability exist.
- A profile with no evaluation spec is not handoff-ready.
- A profile with no integration boundary is not handoff-ready when external systems are involved.
```

---

## 12. Step 3 — Create Initial L2 Profiles

Initial profiles:

```text
L2/profiles/coding_agent.yaml
L2/profiles/symbolic_regression_controller.yaml
L2/profiles/research_agent.yaml
L2/profiles/repo_maintenance_agent.yaml
```

### 12.1 Symbolic Regression Controller Profile

This should be the first priority profile.

Minimum profile:

```yaml
profile_id: "L2-PROFILE-SR-001"
global_profile_id: "AGENT_X_L2::L2-PROFILE-SR-001"
version: "v0.1.0"
status: "draft"
name: "Symbolic Regression Controller"
specialization_type: "symbolic-regression"
ownership_key: "symbolic-regression-controller"
purpose: "Define a future Agent_X specialization for planning, validating, and packaging symbolic-regression workflows through L1-governed implementation tasks."
intended_user_goal_classes:
  - "symbolic regression experiment planning"
  - "PySR_custom task planning"
  - "equation search workflow design"
  - "result validation and comparison planning"
allowed_inputs:
  - "problem statement"
  - "dataset description"
  - "candidate symbolic-regression backend"
  - "resource budget"
  - "evaluation preference"
expected_outputs:
  - "bounded L1 implementation proposal"
  - "symbolic-regression evaluation plan"
  - "risk notes"
  - "required FIC candidates"
required_l1_units:
  - "UNIT-L1-003"
  - "UNIT-L1-004"
  - "UNIT-L1-005"
  - "UNIT-L1-006"
  - "UNIT-L1-007"
required_l1_fic_candidates:
  - "FIC-L1-003"
  - "FIC-L1-004"
  - "FIC-L1-005"
  - "FIC-L1-006"
  - "FIC-L1-007"
forbidden_actions:
  - "direct PySR_custom modification"
  - "direct L0 modification"
  - "direct L1 modification without FIC"
  - "runtime autonomous patching"
  - "ungoverned tool execution"
risk_level: "medium"
profile_package_status: "draft"
l1_handoff_allowed: false
implementation_allowed_without_l1: false
```

---

## 13. Step 4 — Create Blueprints

Each profile must have a blueprint before it can become handoff-ready.

Blueprint path pattern:

```text
L2/blueprints/<profile_name>_blueprint.md
```

Required sections:

```text
A. Profile Identity
B. Specialization Purpose
C. User Goal Classes
D. Expected Reasoning Flow
E. Inputs and Outputs
F. Required L1 Units
G. Forbidden Actions
H. Integration Boundaries
I. Evaluation Criteria
J. Failure Modes
K. Risks and Non-Goals
L. L1 Handoff Conditions
M. Non-Implementation Statement
```

Blueprints must not include implementation code.

Blueprints may include pseudocode, but the pseudocode must describe specialization decision flow, not runtime implementation.

---

## 14. Step 5 — Create Evaluation Specs

Each active or handoff-ready profile must have an evaluation spec.

Evaluation spec path pattern:

```text
L2/evaluation_specs/<profile_name>_eval.md
```

Required sections:

```text
A. Evaluation Purpose
B. Profile Behaviors Evaluated
C. Success Criteria
D. Failure Criteria
E. Positive Scenarios
F. Boundary Scenarios
G. Negative Scenarios
H. Required Evidence
I. L1 Handoff Readiness Criteria
J. Residual Risks
```

Example for symbolic regression:

```text
The profile is acceptable if it can turn a symbolic-regression user goal into:
1. a bounded L1 implementation proposal;
2. a clear evaluation plan;
3. explicit backend constraints;
4. explicit resource constraints;
5. no direct code-modification instruction;
6. no L0 or L1 bypass.
```

Rules:

```text
- Evaluation criteria must be observable.
- A profile with vague evaluation criteria remains draft.
- Evaluation specs must test boundary and negative scenarios, not only normal cases.
```

---

## 15. Step 6 — Create Integration Specs

Integration specs define boundaries with external projects or internal systems.

Initial integration specs:

```text
L2/integration_specs/pysr_custom_integration.md
L2/integration_specs/glyphser_integration.md
L2/integration_specs/symbiant_integration.md
```

Required sections:

```text
A. Integration Target
B. Purpose
C. Allowed L2 Role
D. Forbidden L2 Role
E. Required L1 Mediation
F. Data/Input Boundary
G. Output Boundary
H. Validation Boundary
I. Risk Notes
J. Handoff Conditions
K. Direct-Modification Ban
```

Important rule:

```text
An L2 integration spec does not authorize direct code changes in the integration target.
It only defines what L1 may later convert into governed implementation work.
```

---

## 16. External Project Reference Policy

L2 may reference external or adjacent projects only as planning targets.

Examples:

```text
PySR_custom
Glyphser
Symbiant
Agent_X itself
```

Rules:

```text
- L2 integration specs may describe goals, risks, assumptions, evaluation criteria, and handoff conditions.
- L2 integration specs must not contain patch instructions for external repositories.
- L2 integration specs must not claim that an external repo has been modified or validated.
- If an external repo must be edited, L2 must produce a handoff request and L1 must create the governed implementation package.
- External project assumptions must be marked as stale unless verified by a current source and recorded in the integration spec.
```

Blocking condition:

```text
Any L2 file that directly instructs a coding agent to patch an external repo must be marked BLOCKED_EXTERNAL_TARGET_MUTATION.
```

---

## 17. Step 7 — Build L2 Profile Catalog

Generated artifact:

```text
L2/generated/profile_catalog.yaml
```

Minimum structure:

```yaml
profile_catalog_version: "v0.5.0"
portfolio_id: "AGENT_X_L2"
status: "bootstrap-placeholder-not-release-evidence"
profiles:
  - profile_id: "L2-PROFILE-SR-001"
    global_profile_id: "AGENT_X_L2::L2-PROFILE-SR-001"
    path: "L2/profiles/symbolic_regression_controller.yaml"
    version: "v0.1.0"
    blueprint: "L2/blueprints/symbolic_regression_controller_blueprint.md"
    evaluation_spec: "L2/evaluation_specs/symbolic_regression_eval.md"
    integration_specs:
      - "L2/integration_specs/pysr_custom_integration.md"
    status: "draft"
    l1_handoff_allowed: false
    implementation_allowed_without_l1: false
```

Rules:

```text
- Generated profile catalog must not be manually treated as final authority.
- A profile not listed in the catalog is not ready for L1 handoff.
- A catalog entry with missing blueprint/evaluation/integration references is not handoff-ready.
- The catalog must preserve deterministic path order.
```

---

## 18. Step 8 — L2 Readiness Classification

Allowed L2 readiness statuses:

```text
DRAFT_PROFILE
PROFILE_COMPLETE
BLUEPRINT_COMPLETE
EVALUATION_DEFINED
INTEGRATION_BOUNDARY_DEFINED
READY_FOR_L1_HANDOFF
BLOCKED
DEPRECATED
```

Readiness matrix:

| Requirement | Draft | Profile Complete | Handoff Ready |
|---|---:|---:|---:|
| Profile exists | yes | yes | yes |
| Profile validates against profile model | no | yes | yes |
| Blueprint exists | no | optional | yes |
| Evaluation spec exists | no | optional | yes |
| Integration boundary exists when needed | no | optional | yes |
| Required L1 units listed | optional | yes | yes |
| Forbidden actions declared | yes | yes | yes |
| Risk level declared | yes | yes | yes |
| Traceability matrix updated | no | yes | yes |
| L1 handoff request exists | no | no | yes |
| Direct implementation requested | no | no | no |

A profile is `READY_FOR_L1_HANDOFF` only when:

```text
[ ] profile exists and validates against profile model
[ ] profile has stable profile_id
[ ] blueprint exists
[ ] evaluation spec exists
[ ] integration spec exists if external project is involved
[ ] forbidden actions are declared
[ ] required L1 units are listed
[ ] L0/L1 boundary risks are classified
[ ] risk level is declared
[ ] traceability matrix maps profile -> blueprint -> eval -> integration -> L1 handoff target
[ ] no implementation is requested directly from L2
```

---

## 19. Profile Collision and Ownership Rules

Each profile must declare an `ownership_key`.

Examples:

```text
symbolic-regression-controller
coding-agent-specialization
research-agent-specialization
repo-maintenance-specialization
```

Blocking collisions:

```text
- two active profiles use the same ownership_key without a parent/subprofile relationship;
- two profiles claim final authority over the same L1 handoff target;
- two profiles define contradictory forbidden actions for the same specialization target;
- a profile claims an integration target that another active profile owns without a relationship edge;
- a profile says implementation is forbidden while its blueprint says implementation is directly allowed.
```

Allowed resolution:

```text
- make one profile subordinate;
- merge profiles;
- rename ownership key;
- mark one profile deprecated;
- block both until the L2 ES/SIB graph resolves authority.
```

Unresolved collision status:

```text
BLOCKED_PROFILE_COLLISION
```

---

## 20. Step 9 — L2 to L1 Handoff Request

When implementation is desired, L2 must produce a handoff request for L1.

Recommended file:

```text
L2/generated/l1_handoff_requests/<profile_id>_handoff_request.yaml
```

Minimum structure:

```yaml
l2_to_l1_handoff_request:
  request_id: "L2-HANDOFF-SR-001"
  global_handoff_id: "AGENT_X_L2::L2-HANDOFF-SR-001"
  profile_id: "L2-PROFILE-SR-001"
  global_profile_id: "AGENT_X_L2::L2-PROFILE-SR-001"
  profile_version: "v0.1.0"
  source_profile: "L2/profiles/symbolic_regression_controller.yaml"
  source_blueprint: "L2/blueprints/symbolic_regression_controller_blueprint.md"
  source_evaluation_spec: "L2/evaluation_specs/symbolic_regression_eval.md"
  source_integration_specs:
    - "L2/integration_specs/pysr_custom_integration.md"
  requested_l1_action: "classify_and_plan"
  required_l1_units:
    - "UNIT-L1-003"
    - "UNIT-L1-004"
    - "UNIT-L1-005"
    - "UNIT-L1-006"
    - "UNIT-L1-007"
  implementation_allowed_by_l2: false
  l1_must_create_fic_before_code: true
  forbidden_direct_actions:
    - "modify L0"
    - "modify L1 implementation files without FIC"
    - "modify external project repos directly"
  expected_l1_output:
    - "goal classification"
    - "unit plan"
    - "FIC candidates or FIC updates"
    - "handoff packet if implementation is later authorized"
```

Rules:

```text
- L2 handoff request is an input to L1, not permission to code.
- L1 may reject or block the handoff request.
- If L1 accepts it, L1 owns the implementation package.
```

---

## 21. L2-to-L1 Handoff Acceptance Boundary

A L2 handoff request becomes accepted only when L1 records one of these statuses:

```text
L1_ACCEPTED_FOR_CLASSIFICATION
L1_ACCEPTED_FOR_UNIT_PLANNING
L1_ACCEPTED_FOR_FIC_DRAFTING
L1_BLOCKED_NEEDS_L2_DELTA
L1_REJECTED_OUT_OF_SCOPE
```

Rules:

```text
- L2 must not mark itself implementation-authorized merely because a handoff file exists.
- L1 acceptance for classification is not acceptance for coding.
- L1 acceptance for FIC drafting is not acceptance for coding.
- Coding begins only after L1 creates a FIC-governed implementation package and declares it ready for implementation.
- If L1 rejects or blocks the request, L2 must update the profile package or risk ledger before retrying.
```

---

## 22. Profile Package Manifest and Closure Rule

Generated package manifest:

```text
L2/generated/l2_profile_package_manifest.yaml
```

A L2 profile package is closed for L1 handoff only when it includes:

```yaml
l2_profile_package_manifest_version: "v0.5.0"
portfolio_id: "AGENT_X_L2"
status: "bootstrap-placeholder-not-release-evidence"
packages:
  - package_id: "L2-PKG-SR-001"
    global_package_id: "AGENT_X_L2::L2-PKG-SR-001"
    profile_id: "L2-PROFILE-SR-001"
    global_profile_id: "AGENT_X_L2::L2-PROFILE-SR-001"
    required_artifacts:
      profile: "L2/profiles/symbolic_regression_controller.yaml"
      blueprint: "L2/blueprints/symbolic_regression_controller_blueprint.md"
      evaluation_spec: "L2/evaluation_specs/symbolic_regression_eval.md"
      integration_specs:
        - "L2/integration_specs/pysr_custom_integration.md"
      traceability_matrix: "L2/docs/08_L2_TRACEABILITY_MATRIX.md"
      risk_ledger: "L2/docs/07_L2_RISK_LEDGER.md"
    required_l1_units:
      - "UNIT-L1-003"
      - "UNIT-L1-004"
      - "UNIT-L1-005"
      - "UNIT-L1-006"
      - "UNIT-L1-007"
    package_status: "draft|closed-for-l1-handoff|blocked"
    implementation_authorized: false
```

Closure checklist:

```text
[ ] all required artifact paths exist
[ ] all required artifact paths are canonical
[ ] profile has stable ID and version
[ ] blueprint matches profile ID
[ ] evaluation spec names observable pass/fail criteria
[ ] integration specs define direct-modification ban
[ ] risk ledger contains profile risks
[ ] traceability matrix links profile package to required L1 units
[ ] generated catalog either matches package or is explicitly placeholder
[ ] no file claims direct implementation authority
```

If closure fails, the profile package status is `blocked` or `draft`, not `handoff-ready`.

---

## 23. L2 Workflow State Machine

Allowed states:

```text
DRAFT_SPECIALIZATION_GOAL
PROFILE_DRAFT
PROFILE_REVIEWED
BLUEPRINT_DRAFT
BLUEPRINT_REVIEWED
EVALUATION_DRAFT
EVALUATION_REVIEWED
INTEGRATION_BOUNDARY_REVIEWED
PROFILE_PACKAGE_CLOSED
READY_FOR_L1_HANDOFF
L1_HANDOFF_REQUESTED
L1_ACCEPTED_FOR_PLANNING
L1_REJECTED_OR_BLOCKED
DEPRECATED
```

Forbidden transitions:

```text
PROFILE_DRAFT -> IMPLEMENTATION
BLUEPRINT_REVIEWED -> IMPLEMENTATION
READY_FOR_L1_HANDOFF -> CODE_CHANGE
L1_HANDOFF_REQUESTED -> L0_CHANGE
L1_ACCEPTED_FOR_PLANNING -> L2_RUNTIME_CODE
```

L2 never transitions directly to implementation. It transitions to L1 handoff.

---

## 24. Traceability Requirements

Create:

```text
L2/docs/08_L2_TRACEABILITY_MATRIX.md
```

Minimum table:

| Profile ID | Blueprint | Evaluation Spec | Integration Spec | Required L1 Units | Status |
|---|---|---|---|---|---|
| `L2-PROFILE-SR-001` | `symbolic_regression_controller_blueprint.md` | `symbolic_regression_eval.md` | `pysr_custom_integration.md` | `UNIT-L1-003..007` | `draft` |

Rules:

```text
- Every active profile must appear in the traceability matrix.
- Every handoff-ready profile must map to required L1 units.
- Every implementation request must cite this matrix.
- No L2 profile may claim implementation readiness without traceability.
```

---

## 25. Risk Ledger

Create:

```text
L2/docs/07_L2_RISK_LEDGER.md
```

Minimum risk format:

```yaml
risk:
  risk_id: "L2-RISK-001"
  profile_id: "L2-PROFILE-SR-001"
  description: "Profile could be misread as permission to modify PySR_custom directly."
  severity: "low|medium|high|critical"
  mitigation: "All implementation must go through L1 FIC handoff."
  status: "open|mitigated|accepted|blocked"
```

Common L2 risks:

```text
- L2 profile treated as implementation authorization
- external repo modification without L1 FIC
- model/tool policy unspecified
- evaluation criteria too vague
- profile conflicts with L1 governance
- profile implies runtime autonomy before governance exists
```

---

## 26. Stale Source and Version-Impact Rules

A L2 artifact becomes stale when any of the following changes:

```text
- L2 profile model changes
- L2 system goal changes
- L1 handoff rules change
- required L1 unit IDs change
- L1 FIC IDs referenced by the profile change
- integration target assumptions change
- evaluation criteria change
- risk level changes
```

Version impact:

| Change | Impact |
|---|---|
| typo or formatting only | PATCH |
| clarification with no new obligation | PATCH |
| new profile field added | MINOR |
| new required handoff field added | MINOR |
| profile purpose changed | MINOR or MAJOR |
| forbidden action weakened | MAJOR |
| implementation ban weakened | MAJOR |
| required L1 mediation removed | MAJOR |

Rules:

```text
- A stale profile cannot be handoff-ready.
- A MAJOR change requires risk review and traceability update.
- Weakening the L1 mediation rule is prohibited unless a higher-authority review explicitly approves it.
```

---

## 27. Controlled Error-Code Registry

Create or reserve:

```text
L2/generated/l2_error_codes.yaml
```

Initial codes:

```yaml
error_codes:
  BLOCKED_L0_BOUNDARY_RISK: "L2 artifact may affect L0 without authorized L1 mediation."
  BLOCKED_L1_GOVERNANCE_BYPASS: "L2 artifact attempts to bypass L1 FIC workflow."
  BLOCKED_PROFILE_CONFLICT: "Two L2 artifacts conflict over profile purpose or authority."
  BLOCKED_PROFILE_COLLISION: "Two L2 profiles claim the same specialization ownership or handoff target."
  BLOCKED_UNDEFINED_PROFILE_MODEL: "Profile does not conform to the L2 profile model."
  BLOCKED_UNDEFINED_EVALUATION: "Profile lacks observable evaluation criteria."
  BLOCKED_UNDEFINED_INTEGRATION_BOUNDARY: "External integration boundary is missing or vague."
  BLOCKED_STALE_PROFILE_SOURCE: "Profile depends on stale L1, integration, or profile-model source."
  BLOCKED_UNGOVERNED_IMPLEMENTATION_REQUEST: "L2 artifact requests code directly instead of L1 handoff."
  BLOCKED_EXTERNAL_TARGET_MUTATION: "L2 artifact directly instructs mutation of an external target."
  REQUIRES_L1_HANDOFF: "L2 profile requires L1 classification and FIC-governed planning before implementation."
```

Validators must not invent unregistered blocking codes without updating the registry.

---

## 28. L2 Validator Expectations

Early L2 may use manual validation, but validator outputs must be structured.

Expected validators:

```text
l2_profile_schema_validate
l2_profile_catalog_check
l2_profile_package_check
l2_traceability_check
l2_handoff_readiness_check
l2_boundary_check
l2_risk_check
```

### 28.1 Validator input manifest

Every validation run must declare inputs.

```yaml
validator_input_manifest:
  validator: "l2-profile-validate"
  validator_version: "v0.5.0"
  workspace_ref: "local-working-tree|<commit>"
  inputs:
    - path: "L2/docs/03_L2_PROFILE_MODEL.md"
      digest: "sha256:<pending-or-computed>"
    - path: "L2/profiles/symbolic_regression_controller.yaml"
      digest: "sha256:<pending-or-computed>"
    - path: "L2/blueprints/symbolic_regression_controller_blueprint.md"
      digest: "sha256:<pending-or-computed>"
    - path: "L2/evaluation_specs/symbolic_regression_eval.md"
      digest: "sha256:<pending-or-computed>"
    - path: "L2/integration_specs/pysr_custom_integration.md"
      digest: "sha256:<pending-or-computed>"
```

Rules:

```text
- Validation output without an input manifest is not handoff evidence.
- Pending digests are allowed during bootstrap only.
- Handoff-ready packages should use computed digests once validators exist.
```

### 28.2 Minimum validation output

```yaml
l2_validation_result:
  validator: "l2-profile-validate"
  version: "v0.5.0"
  status: "PASS|WARNING|BLOCKED|FAIL|TOOL_ERROR"
  checked_profiles: []
  checked_blueprints: []
  checked_evaluation_specs: []
  checked_integration_specs: []
  checked_profile_packages: []
  errors: []
  warnings: []
  skipped_checks: []
  handoff_ready_profiles: []
  blocked_profiles: []
```

No-silent-skip rule:

```text
- A validator must not silently skip a required check.
- If a check cannot run, it must appear in `skipped_checks` with reason and release/handoff impact.
- TOOL_ERROR must not be treated as PASS.
```

Controlled statuses:

```text
PASS
WARNING
BLOCKED
FAIL
TOOL_ERROR
```

### 28.3 Canonical output rules

When validators emit JSON or YAML for automation:

```text
- keys must be sorted lexicographically where supported;
- lists must sort by stable ID unless order is semantic;
- errors sort by `(code, profile_id, path)`;
- warnings sort by `(code, profile_id, path)`;
- skipped checks sort by `(check_id, path)`;
- unknown error codes are invalid output.
```

---

## 29. Relationship to L2 ES, SIB, EQC, and FIC

### 29.1 L2 ES

L2 ES should govern the L2 document/profile portfolio:

```text
profiles, blueprints, evaluation specs, integration specs, risk ledgers, traceability matrices, generated catalogs
```

This workflow should be registered in L2 ES once the L2 ES document exists.

### 29.2 L2 SIB

L2 SIB should bind:

```text
L2 profile -> blueprint -> evaluation spec -> integration spec -> L1 handoff target
```

L2 SIB should not bind directly to implementation code at the initial stage.

### 29.3 L2 EQC

L2 EQC should be used only for deterministic specialization decision logic, such as:

```text
ClassifySpecializationRequest
SelectProfile
DecideL1HandoffRequired
RankProfileCandidates
```

### 29.4 L2 FIC

L2 FIC should not create L2 runtime code at this stage.

Use L2 FIC only if a L2 document-generation or validation tool later becomes implementation work, and route that through L1 first.

---

## 30. Upgrade Triggers for Future L2 Implementation Governance

L2 must remain profile/spec only until one of these conditions is explicitly accepted by L1:

```text
- L1 creates a FIC for an L2 validator implementation.
- L1 creates a FIC for an L2 catalog generator.
- L1 creates a FIC for an L2 profile selector.
- L1 creates a FIC for an L2 evaluation runner.
- L1 creates a FIC for an integration planning adapter.
```

Even then, implementation belongs to L1 governance.

The future L2 implementation mode requires:

```text
[ ] L2 ES standard exists
[ ] L2 SIB standard exists
[ ] L2 EQC standard exists for profile selection logic
[ ] L2 FIC profile exists for implementation-bound tools
[ ] L1 accepts the implementation package
[ ] permitted files are declared
[ ] tests and evidence are required
```

Until those are true, do not create L2 runtime directories.

---

## 31. L2 Anti-Patterns

Reject L2 work if it contains:

```text
- runtime code without L1 authorization
- tool execution policy hidden inside profile prose
- direct instruction to modify L0
- direct instruction to modify L1 implementation files
- broad autonomous-agent behavior without boundaries
- profile with no evaluation criteria
- blueprint with no forbidden actions
- integration spec that authorizes direct external-repo edits
- generated catalog treated as final evidence
- handoff request with no required L1 units
- profile that bypasses FIC
- L2 runtime folder created before L1 authorizes implementation
- profile collision hidden by similar but different names
```

---

## 32. Minimum L2 Readiness Checklist

L2 is ready as a profile/spec layer when:

```text
[ ] L2/docs/00_L2_SYSTEM_GOAL.md exists
[ ] L2/docs/03_L2_PROFILE_MODEL.md exists
[ ] at least one profile exists under L2/profiles/
[ ] symbolic_regression_controller.yaml exists
[ ] every profile has a blueprint or is explicitly draft
[ ] every handoff-ready profile has an evaluation spec
[ ] every external integration has an integration spec
[ ] L2 traceability matrix exists
[ ] L2 risk ledger exists
[ ] generated profile catalog exists and is marked placeholder unless validator-produced
[ ] generated profile package manifest exists and is marked placeholder unless validator-produced
[ ] no runtime code exists under L2
[ ] no L2 file claims permission to bypass L1
[ ] profile package closure rule passes for any handoff-ready profile
[ ] all skipped checks are explicit
```

---

## 33. Quality Rubric

Score L2 workflow/profile packages from 0 to 10.

| Score | Meaning |
|---:|---|
| 0–3 | Too vague; profile cannot guide L1. |
| 4–6 | Some structure, but L1 would need to guess. |
| 7 | Usable for early planning. |
| 8 | Strong enough for profile governance. |
| 9 | Strong enough for L1 handoff preparation. |
| 10 | Machine-checkable profile package with traceability, evaluation, risk, validator output, source freshness, and boundary closure. |

Current target:

```text
8/10 for initial profiles
9/10 before L1 handoff
10/10 only when L2 ES/SIB/EQC/FIC documents and validators exist
```

---


## 34. Minimum First L2 Scaffold Slice

The first L2 scaffold task should create only the profile/spec control plane. It is not an implementation task and must not create runtime code.

Required first slice:

```text
L2/README.md
L2/docs/00_L2_SYSTEM_GOAL.md
L2/docs/01_L2_BACKGROUND.md
L2/docs/02_L2_ARCHITECTURE_CONTRACT.md
L2/docs/03_L2_PROFILE_MODEL.md
L2/docs/04_L2_SPECIALIZATION_CATALOG.md
L2/docs/05_L2_INTEGRATION_BOUNDARIES.md
L2/docs/06_L2_EVALUATION_PLAN.md
L2/docs/07_L2_RISK_LEDGER.md
L2/docs/08_L2_TRACEABILITY_MATRIX.md
L2/docs/09_L2_HANDOFF_TO_L1_RULES.md
L2/profiles/coding_agent.yaml
L2/profiles/symbolic_regression_controller.yaml
L2/profiles/research_agent.yaml
L2/profiles/repo_maintenance_agent.yaml
L2/blueprints/coding_agent_blueprint.md
L2/blueprints/symbolic_regression_controller_blueprint.md
L2/blueprints/research_agent_blueprint.md
L2/blueprints/repo_maintenance_agent_blueprint.md
L2/evaluation_specs/coding_agent_eval.md
L2/evaluation_specs/symbolic_regression_eval.md
L2/evaluation_specs/research_agent_eval.md
L2/evaluation_specs/repo_maintenance_eval.md
L2/integration_specs/pysr_custom_integration.md
L2/integration_specs/glyphser_integration.md
L2/integration_specs/symbiant_integration.md
L2/generated/profile_catalog.yaml
L2/generated/l2_profile_package_manifest.yaml
L2/generated/l2_semantic_lockfile.yaml
L2/generated/readiness_report.md
L2/generated/validation_report.md
L2/evidence/.gitkeep
```

Rules:

```text
- This slice must not create L2 runtime code.
- This slice must not add L2 tool execution.
- This slice must not create model-routing, memory, autonomy, or patching directories.
- This slice must not modify L0 or L1 except for optional README references to the existence of L2.
- Generated files must be marked bootstrap-placeholder-not-release-evidence unless produced by a validator.
```

The first slice is successful when it creates a complete L2 profile/spec scaffold and no prohibited runtime surface.

---

## 35. Prohibited Runtime Directory Validation

A L2 scaffold validator must fail or block if any of the following directories exist before L1 has authorized implementation:

```text
L2/controller/
L2/runtime/
L2/agents/
L2/tools/
L2/model_router/
L2/memory/
L2/autonomy/
L2/executors/
L2/patchers/
```

Allowed exception:

```text
A directory may exist only if it contains a README.md explicitly stating that it is a non-executable placeholder and has no source code, no tests, no runtime entrypoint, and no tool execution policy.
```

Blocking statuses:

```text
BLOCKED_PREMATURE_L2_RUNTIME
BLOCKED_L2_TOOL_EXECUTION_SURFACE
BLOCKED_L2_AUTONOMY_SURFACE
BLOCKED_L2_BYPASSES_L1
```

---

## 36. Profile Lifecycle Transitions

Profile lifecycle is separate from workflow adoption mode.

Allowed profile statuses:

```text
draft
reviewed
active
handoff-ready
transferred-to-l1
deprecated
blocked
```

Allowed transitions:

```text
draft -> reviewed
reviewed -> active
active -> handoff-ready
handoff-ready -> transferred-to-l1
active -> deprecated
handoff-ready -> blocked
blocked -> draft|reviewed only after remediation
```

Forbidden transitions:

```text
draft -> handoff-ready
reviewed -> transferred-to-l1
active -> transferred-to-l1 without handoff-ready
blocked -> handoff-ready
transferred-to-l1 -> active without a new version and migration note
```

Rules:

```text
- `active` means the profile is valid as a profile/spec document.
- `handoff-ready` means the profile package closes and may be sent to L1.
- `transferred-to-l1` means L1 received the request; it does not mean implementation is accepted.
- A transferred profile must keep a reference to the L1 handoff request ID.
```

---

## 37. Controlled Enum Registry

L2 validators and documents must use controlled values.

### 37.1 Profile types

```text
coding
research
symbolic-regression
repo-maintenance
orchestration
integration-planning
evaluation-planning
other-with-justification
```

### 37.2 Artifact types

```text
system-goal
background
architecture-contract
profile-model
profile
blueprint
evaluation-spec
integration-spec
risk-ledger
traceability-matrix
handoff-rules
handoff-request
generated-catalog
generated-report
generated-lockfile
evidence
```

### 37.3 Risk levels

```text
low
medium
high
critical
```

### 37.4 Handoff decisions

```text
NO_HANDOFF_NEEDED
READY_FOR_L1_HANDOFF
BLOCKED_PROFILE_INCOMPLETE
BLOCKED_EVALUATION_INCOMPLETE
BLOCKED_INTEGRATION_BOUNDARY_INCOMPLETE
BLOCKED_RISK_REVIEW_REQUIRED
REQUIRES_PROFILE_DELTA
REJECTED_BYPASSES_L1
```

Rules:

```text
- Unknown enum values are invalid in generated or validator-owned files.
- Human prose may explain an enum, but machine-readable fields must use the controlled value exactly.
- If a new enum is needed, update this workflow or the future L2 ES standard first.
```

---

## 38. Post-Scaffold Evidence Bundle

After the first L2 scaffold is created, evidence must be stored under:

```text
L2/evidence/bootstrap/
```

Minimum evidence files:

```text
<timestamp>_l2_scaffold_inventory.yaml
<timestamp>_l2_forbidden_runtime_check.yaml
<timestamp>_l2_profile_package_check.yaml
<timestamp>_l2_readiness_summary.md
```

Minimum scaffold inventory:

```yaml
l2_scaffold_inventory:
  workflow_version: "v0.5.0"
  commit: "<commit-or-local-working-tree>"
  created_paths: []
  required_paths_missing: []
  prohibited_paths_present: []
  generated_placeholders:
    - path: "L2/generated/profile_catalog.yaml"
      release_evidence: false
  status: "PASS|WARNING|BLOCKED|FAIL"
```

Rules:

```text
- Evidence must not claim release readiness.
- Evidence must distinguish placeholder generation from validator-produced reports.
- A scaffold with prohibited runtime directories is not valid unless each directory is documented as a non-executable placeholder.
```

---

## 39. L2-to-L1 Reporting Packet

When L2 is ready to ask L1 for implementation planning, it must produce a reporting packet, not an implementation packet.

Recommended path:

```text
L2/generated/l2_to_l1_handoff_request.yaml
```

Minimum schema:

```yaml
l2_to_l1_handoff_request:
  request_id: "L2-HANDOFF-SR-001"
  source_profile_id: "AGENT_X_L2::L2-PROFILE-SR-001"
  source_profile_package: "L2/generated/l2_profile_package_manifest.yaml"
  requested_l1_action: "evaluate-for-fic-planning"
  implementation_requested: false
  permitted_l1_units_to_consider:
    - "AGENT_X_L1::UNIT-L1-003"
    - "AGENT_X_L1::UNIT-L1-004"
    - "AGENT_X_L1::UNIT-L1-005"
    - "AGENT_X_L1::UNIT-L1-006"
    - "AGENT_X_L1::UNIT-L1-007"
  forbidden_direct_actions:
    - "modify L0"
    - "modify L1 implementation files without L1 FIC"
    - "modify external project repositories"
    - "execute tools from L2"
  evidence_refs: []
  status: "READY_FOR_L1_HANDOFF|BLOCKED|DRAFT"
```

Rules:

```text
- This packet requests L1 planning only.
- This packet must not list permitted code files.
- This packet must not authorize edits.
- L1 must decide whether to create FIC-governed implementation work.
```

---

## 40. Anti-Bloat and Deferral Rule

L2 must stay thinner than L1 until there is a concrete implementation need.

Do not add the following to this workflow standard yet:

```text
- full release-candidate machinery
- signed checkpoints
- executable L2 runtime contracts
- tool sandbox policies beyond boundary notes
- L2 memory governance
- L2 model-router governance
- L2 multi-agent orchestration governance
- full SIB/ES/EQC duplication from L1
```

Those belong in later L2 standards only after L1 accepts a handoff and creates FIC-governed implementation work.

Deferral record template:

```yaml
l2_deferral:
  deferred_item: "L2 runtime governance"
  reason: "No L1-authorized implementation exists yet."
  revisit_trigger: "L1 creates a FIC for L2 runtime or validator implementation."
  risk: "low"
```

---

## 41. Updated Quality Target

For the current stage, this workflow is complete when it can safely guide a weaker documentation/coding agent to create L2 profile/spec artifacts without creating runtime code or bypassing L1.

Current quality target:

```text
10/10 for L2 profile/spec workflow standard
Not release-grade
Not implementation-authorizing
Not a substitute for L2 ES, SIB, EQC, or FIC standards
```

---

## 42. Root Integration Boundary

The L2 scaffold may update root-level integration references only in a narrow way.

Allowed root-level updates:

```text
README.md may mention that L2 exists as a profile/spec layer.
Makefile may add prove-l2 if it runs only scaffold/profile validation and does not execute L2 runtime code.
```

Recommended Makefile target:

```makefile
prove-l2:
	python L2/validators/bootstrap_validate_l2_scaffold.py
```

Rules:

```text
- `prove-l2` must not run L2 tools, agents, model routers, memory systems, or autonomous patchers.
- `prove-all` may call `prove-l2` only if `prove-l2` is scaffold/profile validation only.
- README must not claim L2 runtime capability exists.
- README must not claim L2 can modify L0, L1, or external repositories.
- If no L2 validator exists yet, README must say L2 is scaffold/profile-spec only.
```

---

## 43. Pre-Existing Prohibited Directory Handling

If the repository already contains a prohibited L2 runtime-like directory, the scaffold validator must classify it instead of deleting or accepting it silently.

Decision table:

| Condition | Status | Required Action |
|---|---|---|
| Directory absent | `PASS` | None |
| Directory exists and contains only README.md stating non-executable placeholder | `WARNING` | Keep as placeholder; list in evidence |
| Directory exists and contains source code | `BLOCKED_PREMATURE_L2_RUNTIME` | Stop; route through L1 if implementation is desired |
| Directory exists and contains tests for runtime behavior | `BLOCKED_PREMATURE_L2_RUNTIME` | Stop; route through L1 |
| Directory exists and contains tool/model/memory/autonomy policy as executable instruction | `BLOCKED_L2_BYPASSES_L1` | Stop; rewrite as non-authorizing spec or route through L1 |

Rules:

```text
- A weaker agent must not delete pre-existing directories unless a FIC-governed cleanup task authorizes deletion.
- Placeholder directories must contain no executable source files.
- Placeholder READMEs must state that they do not authorize implementation.
```

---

## 44. Final Weaker-Agent Response Format

A L2 scaffold agent must end with a structured response so review does not require reconstructing the whole conversation.

Required final response:

```yaml
l2_scaffold_completion:
  status: "PASS|WARNING|BLOCKED|FAIL"
  workflow_version: "v0.5.0"
  files_created: []
  files_modified: []
  prohibited_paths_present: []
  prohibited_paths_status: "none|placeholder-only|blocked"
  generated_placeholders: []
  evidence_files: []
  commands_run:
    - command: ""
      result: "pass|fail|not-run"
  checks_not_run:
    - check: ""
      reason: ""
  l1_handoff_requests_created: []
  implementation_authorized: false
  release_evidence: false
  unresolved_risks: []
```

Rules:

```text
- `implementation_authorized` must remain false for the initial L2 scaffold.
- `release_evidence` must remain false until real validators produce release-grade evidence.
- Missing commands must be reported under `checks_not_run`; they must not be omitted.
```

---

## 45. Post-Scaffold Status Decision Table

Use this table after the first L2 scaffold pass.

| Result | Meaning | Next Action |
|---|---|---|
| `PASS` | Required scaffold exists; no prohibited runtime surface. | Proceed to lightweight L2 ES/SIB/EQC/FIC standards. |
| `WARNING` | Scaffold exists, but some outputs are placeholders or non-executable placeholder dirs exist. | Record evidence; continue only with profile/spec work. |
| `BLOCKED` | Runtime/code/tool/autonomy surface appears without L1 authorization, or required profile artifacts are missing. | Fix scaffold or route implementation request through L1. |
| `FAIL` | Files contradict boundary rules, version markers, or profile model. | Correct documents before further L2 work. |

No status in this table authorizes direct L2 code implementation.

---

## 46. No-False-Claim Rule

L2 documents, generated reports, README sections, and evidence files must not overclaim maturity.

Forbidden claims during the initial L2 stage:

```text
- "L2 runtime is implemented"
- "L2 agents can execute"
- "L2 can modify PySR_custom/Glyphser/Symbiant"
- "L2 release validation passed"
- "L2 implementation is authorized"
- "Generated placeholders are validation evidence"
```

Allowed claims:

```text
- "L2 profile/spec scaffold exists"
- "L2 generated placeholders exist but are not release evidence"
- "L2 may request L1 planning through a handoff request"
- "L2 implementation requires L1 FIC governance"
```

Any false maturity claim must be corrected before the scaffold is marked `PASS`.

---

## 47. Final Rule

L2 is allowed to specialize Agent_X only by producing governed profile/spec artifacts.

L2 must not implement directly.

Correct escalation path:

```text
L2 profile/spec -> L2 handoff request -> L1 FIC workflow -> implementation
```

Incorrect escalation path:

```text
L2 profile/spec -> direct code
```
