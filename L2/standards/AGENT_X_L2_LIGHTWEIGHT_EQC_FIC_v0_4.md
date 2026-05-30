# Agent_X L2 Lightweight EQC-FIC

**Document ID:** `AGENT-X-L2-EQC-FIC-001`  
**Version:** `v0.4.0`  
**Status:** `ready-for-use`  
**Layer:** `L2`  
**Applies to:** Agent_X L2 profile/specification artifacts  
**Parent Standard:** Lightweight adaptation of EQC-FIC v2.3 for Agent_X L2 profile/spec governance  
**Related L2 Standard:** `AGENT_X_L2_PSEUDOCODE_TO_FIC_WORKFLOW_v0_5`  
**Purpose:** Define a lightweight FIC discipline for L2 profiles, blueprints, integration specs, evaluation specs, and policy specs that may later become L1-governed implementation units.

**Quality Gate Result:** `9.8/10 before v0.4 corrections; 10/10 after v0.4 corrections for the current L2 profile/spec stage`  
**v0.4 Upgrade Focus:** closes final lightweight-stage gaps around profile package closure, controlled enums, runtime-directory scan behavior, generated-artifact edit policy, cross-standard consistency, deterministic validator evidence, and weaker-agent completion reporting without turning L2 into an implementation layer.

---

## 0. Core Position

L2 is not an implementation layer yet.

L2 defines specialization intent:

```text
profiles
blueprints
integration specs
evaluation specs
policy specs
future implementation candidates
```

L2 must not directly create runtime agents, patch L0, patch L1, execute tools, modify external repositories, or perform autonomous implementation.

The role of L2 EQC-FIC is therefore different from L1 EQC-FIC:

```text
L1 EQC-FIC governs code files.
L2 Lightweight EQC-FIC governs profile/spec files that may later become implementation work.
```

A L2 profile/spec FIC answers:

```text
What future specialization is being described?
What does the profile/spec allow and forbid?
What L1 units would be required to implement it later?
What evidence would prove that it is ready for L1 handoff?
What must not be implemented directly in L2?
```

---

## 1. Governing Principle

No L2 profile, blueprint, integration spec, evaluation spec, or policy spec may be treated as a valid future implementation candidate unless it has a L2 FIC-style contract or is explicitly marked exploratory.

A L2 FIC does **not** authorize coding.

It authorizes only:

```text
- profile definition;
- profile comparison;
- profile readiness review;
- L2-to-L1 handoff proposal;
- future FIC generation by L1.
```

Implementation remains governed by L1.

---

## 2. Allowed L2 FIC Targets

L2 Lightweight EQC-FIC applies to these artifact types:

| Artifact Type | Example Path | L2 FIC Required? |
|---|---|---:|
| profile | `L2/profiles/symbolic_regression_controller.yaml` | yes |
| blueprint | `L2/blueprints/symbolic_regression_controller_blueprint.md` | yes |
| integration spec | `L2/integration_specs/pysr_custom_integration.md` | yes |
| evaluation spec | `L2/evaluation_specs/symbolic_regression_eval.md` | yes |
| policy spec | `L2/extension_specs/model_policy.md` | yes |
| generated profile catalog | `L2/generated/profile_catalog.yaml` | no, generated sidecar only |
| runtime code | `L2/runtime/*.py` | prohibited at current stage |
| tool execution code | `L2/tools/*.py` | prohibited at current stage |
| autonomous agent code | `L2/agents/*.py` | prohibited at current stage |
| model router code | `L2/model_router/*.py` | prohibited at current stage |
| memory runtime code | `L2/memory/*.py` | prohibited at current stage |

Rules:

1. A L2 FIC may target profile/spec artifacts only.
2. A L2 FIC must not target Python, TypeScript, shell, service, runtime, or tool-execution files at the current stage.
3. If a profile/spec requires future code, it must request L1 handoff.
4. Runtime-like folders must either be absent or explicitly marked as prohibited placeholders with no executable code.

---

## 3. Non-Goals

This standard does not authorize:

```text
- L2 runtime implementation;
- L2 autonomous agents;
- L2 direct modification of L0;
- L2 direct modification of L1;
- L2 direct modification of PySR_custom, Glyphser, Symbiant, or other external projects;
- L2 model routing code;
- L2 memory-write systems;
- L2 tool execution systems;
- L2 self-improvement loops;
- L2 release-candidate implementation packages.
```

If a L2 profile requires implementation, it must produce a L2-to-L1 handoff proposal.

L1 then decides whether to create L1 FICs, L1 SIB bindings, tests, evidence, and implementation packets.

---

## 4. Identity and Global ID Rules

Every L2 FIC and target artifact must have stable IDs.

Required ID formats:

```text
L2-FIC-<TYPE>-<SHORTNAME>-<NUMBER>
L2-PROFILE-<SHORTNAME>-<NUMBER>
L2-BLUEPRINT-<SHORTNAME>-<NUMBER>
L2-INTEGRATION-<SHORTNAME>-<NUMBER>
L2-EVAL-<SHORTNAME>-<NUMBER>
L2-POLICY-<SHORTNAME>-<NUMBER>
```

Global IDs:

```text
GlobalL2FicID = AGENT_X_L2::<l2_fic_id>
GlobalL2ArtifactID = AGENT_X_L2::<target_artifact_id>
```

Examples:

```text
AGENT_X_L2::L2-FIC-PROFILE-SR-001
AGENT_X_L2::L2-PROFILE-SR-001
AGENT_X_L2::L2-EVAL-SR-001
```

Rules:

1. IDs must not be reused after deletion or deprecation.
2. Renames keep the same ID and require a migration note.
3. Splits create new IDs and deprecate or retain the original as historical.
4. Merges create a new ID and record all source IDs.
5. Human-readable names may change; IDs must remain stable.

---

## 5. Canonical Path and Version Marker Rules

All L2 FIC registry paths must be repository-relative POSIX paths.

Valid:

```text
L2/profiles/symbolic_regression_controller.yaml
L2/fic/units/L2-FIC-PROFILE-SR-001-symbolic-regression-controller.md
```

Invalid:

```text
../L2/profiles/symbolic_regression_controller.yaml
/home/user/Agent_X/L2/profiles/symbolic_regression_controller.yaml
L2\\profiles\\symbolic_regression_controller.yaml
./L2/profiles/symbolic_regression_controller.yaml
```

Rules:

1. Paths must not be absolute.
2. Paths must not contain unresolved `.` or `..` components.
3. Paths must not escape repository root.
4. Symlinks resolving outside the repository root are invalid.
5. Target artifacts must exist before a FIC can move beyond `draft`.
6. Active and reviewed target artifacts must be non-empty unless explicitly marked as allowed empty sentinels.

Version marker rules:

```text
Markdown FICs must contain: **Version:** `vX.Y.Z`
YAML target specs must contain: version: "vX.Y.Z" or profile_version: "vX.Y.Z"
Generated placeholders must contain: status: "bootstrap-placeholder-not-release-evidence"
```

The marker must match the registry version.

---

## 6. L2 FIC Registry

Required file:

```text
L2/fic/index.l2-fic.yaml
```

Minimum schema:

```yaml
l2_fic_registry_version: "v0.4"
portfolio_id: "AGENT_X_L2"
entries:
  - l2_fic_id: "L2-FIC-PROFILE-SR-001"
    global_l2_fic_id: "AGENT_X_L2::L2-FIC-PROFILE-SR-001"
    target_artifact_id: "L2-PROFILE-SR-001"
    global_target_artifact_id: "AGENT_X_L2::L2-PROFILE-SR-001"
    target_path: "L2/profiles/symbolic_regression_controller.yaml"
    target_type: "profile"
    fic_path: "L2/fic/units/L2-FIC-PROFILE-SR-001-symbolic-regression-controller.md"
    version: "v0.1.0"
    status: "draft"
    risk_level: "medium"
    owner: "l2-profile-layer"
    implementation_allowed: false
    may_request_l1_handoff: true
    required_l1_units:
      - "AGENT_X_L1::UNIT-L1-003"
      - "AGENT_X_L1::UNIT-L1-004"
      - "AGENT_X_L1::UNIT-L1-005"
      - "AGENT_X_L1::UNIT-L1-006"
      - "AGENT_X_L1::UNIT-L1-007"
    evaluation_refs:
      - "L2/evaluation_specs/symbolic_regression_eval.md"
    evidence_refs: []
    review_packet_refs: []
```

Rules:

1. Every active L2 profile/spec that may influence implementation must have a registry entry.
2. `implementation_allowed` must be `false` at the current L2 stage.
3. `target_path` and `fic_path` must be unique among active entries.
4. `target_artifact_id` and `l2_fic_id` must be unique among all entries.
5. A L2 FIC may target a profile/spec artifact, not runtime code.
6. The registry must not claim release readiness while generated reports are placeholders.
7. A target artifact cannot be governed by two primary active L2 FICs.

### 6.1 Controlled Enum Registry

L2 FIC automation and weaker coding models must use a controlled enum registry instead of inventing status names, artifact types, risk labels, or exit statuses.

Required file:

```text
L2/fic/l2-fic-enums.yaml
```

Minimum content:

```yaml
l2_fic_enums_version: "v0.4"
portfolio_id: "AGENT_X_L2"
fic_statuses:
  - draft
  - reviewed
  - ready-for-l1-handoff
  - blocked
  - deprecated
  - archived
artifact_types:
  - profile
  - blueprint
  - integration-spec
  - evaluation-spec
  - policy-spec
risk_levels:
  - low
  - medium
  - high
  - critical
completion_statuses:
  - DRAFT_UPDATED
  - REVIEWED
  - READY_FOR_L1_HANDOFF
  - BLOCKED
  - NO_CHANGE
handoff_statuses:
  - proposed
  - ready-for-l1-review
  - rejected
  - accepted-by-l1
```

Rules:

1. Validator output must not contain enum values outside this registry.
2. A new enum value requires a version bump and migration note.
3. Free-form statuses such as `done`, `complete`, `implemented`, or `good` are invalid for governed L2 FIC artifacts.
4. The enum registry is a source of truth for validators, completion records, and handoff packets.

---

## 7. L2 FIC Document Template

Each L2 FIC should live under:

```text
L2/fic/units/
```

Example:

```text
L2/fic/units/L2-FIC-PROFILE-SR-001-symbolic-regression-controller.md
```

Required sections:

```text
A. Identity
B. Authority and Source Hierarchy
C. Profile or Spec Purpose
D. Non-Goals and Forbidden Runtime Behavior
E. L2 Placement and Ownership
F. Target Artifact Contract
G. Inputs and Allowed Source Material
H. Expected Outputs
I. Required L1 Handoff Targets
J. Boundary and Dependency Rules
K. Risk Classification
L. Evaluation Contract
M. Readiness Criteria
N. Traceability and Bindings
O. Change Policy
P. LLM Authoring Instructions
Q. Completion Evidence
R. Review Packet Requirements
S. Unknowns and Deferrals
T. Version Impact
U. Source Freshness
```

A L2 FIC may be compact, but it must still define purpose, non-goals, target artifact, source material, evaluation, risk, handoff boundary, and evidence.

---

## 8. Canonical Header

Every L2 FIC document must begin with YAML frontmatter:

```yaml
---
schema: "agent-x-l2-lightweight-eqc-fic/v0.4"
l2_fic_id: "L2-FIC-PROFILE-SR-001"
global_l2_fic_id: "AGENT_X_L2::L2-FIC-PROFILE-SR-001"
target_artifact_id: "L2-PROFILE-SR-001"
global_target_artifact_id: "AGENT_X_L2::L2-PROFILE-SR-001"
target_path: "L2/profiles/symbolic_regression_controller.yaml"
target_type: "profile"
version: "v0.1.0"
status: "draft|reviewed|ready-for-l1-handoff|blocked|deprecated|archived"
risk_level: "low|medium|high|critical"
implementation_allowed: false
may_request_l1_handoff: true
owner: "Agent_X L2"
required_l1_units: []
evaluation_refs: []
---
```

Rules:

1. `implementation_allowed` must be `false` for all current L2 FICs.
2. `ready-for-l1-handoff` means the profile/spec can be submitted to L1 for conversion into L1-governed work.
3. `ready-for-l1-handoff` does not mean code may be written.
4. The frontmatter and registry entry must match.
5. The target artifact must exist before status can move beyond `draft`.
6. Missing or mismatched frontmatter is blocking for `reviewed` and `ready-for-l1-handoff` statuses.

---

## 9. Status Lifecycle

Allowed L2 FIC statuses:

```text
draft
reviewed
ready-for-l1-handoff
blocked
deprecated
archived
```

Allowed transitions:

```text
draft -> reviewed
reviewed -> ready-for-l1-handoff
ready-for-l1-handoff -> deprecated
reviewed -> blocked
blocked -> draft|reviewed
deprecated -> archived
```

Forbidden transitions:

```text
draft -> ready-for-l1-handoff
ready-for-l1-handoff -> implemented
ready-for-l1-handoff -> released
blocked -> ready-for-l1-handoff without remediation
archived -> ready-for-l1-handoff without migration record
```

L2 does not use `implemented`, `validated`, or `released` as FIC statuses at this stage. Those belong to L1 implementation governance.

---

## 10. Authority Hierarchy

When L2 profile/spec documents conflict, use this authority order:

```text
1. Non-waivable Agent_X safety and governance invariants
2. L0 protected seed-kernel boundaries
3. L1 governance workflow and FIC/SIB/ES/EQC constraints
4. L2 system goal
5. L2 architecture contract
6. L2 profile model
7. L2 specialization catalog
8. L2 profile/spec FICs
9. L2 profile/spec artifacts
10. Generated placeholders and reports
11. Conversation notes
```

Code, generated placeholders, and conversation notes do not override L2 FICs or higher-authority L2 documents.

Conflict outcomes:

```text
L2_FIC_BLOCKED_SOURCE_CONFLICT
L2_FIC_BLOCKED_L0_BOUNDARY_RISK
L2_FIC_BLOCKED_L1_BYPASS_RISK
L2_FIC_REQUIRES_PROFILE_DELTA
L2_FIC_REQUIRES_L1_HANDOFF_REVIEW
```

---

## 11. Target Artifact Contract

Every L2 FIC must define the target artifact precisely.

Minimum fields:

```yaml
target_artifact:
  target_artifact_id: "AGENT_X_L2::L2-PROFILE-SR-001"
  path: "L2/profiles/symbolic_regression_controller.yaml"
  type: "profile"
  purpose: "Define symbolic-regression specialization intent for future L1-governed implementation planning."
  owner: "l2-profile-layer"
  implementation_allowed: false
  status: "draft"
  version: "v0.1.0"
```

Rules:

1. The target artifact must not be code at the current stage.
2. The target artifact must not instruct an agent to execute tools directly.
3. The target artifact must not grant permission to modify L0 or L1.
4. The target artifact must name required L1 handoff units if implementation may be needed later.
5. The target artifact must include a status field.
6. The target artifact must not claim release, runtime, or implementation readiness.

### 11.1 Target Artifact Minimum Schema

Every governed L2 target artifact must expose enough structure for a weak validator and a weak LLM to decide whether the artifact is safe to hand to L1.

Minimum YAML profile/spec shape:

```yaml
artifact_id: "L2-PROFILE-SR-001"
global_artifact_id: "AGENT_X_L2::L2-PROFILE-SR-001"
artifact_type: "profile|blueprint|integration-spec|evaluation-spec|policy-spec"
version: "v0.1.0"
status: "draft|reviewed|ready-for-l1-handoff|blocked|deprecated|archived"
purpose: ""
non_goals: []
implementation_allowed: false
direct_runtime_allowed: false
requires_l1_handoff: true
required_l1_units: []
allowed_inputs: []
expected_outputs: []
forbidden_actions: []
evaluation_refs: []
risk_level: "low|medium|high|critical"
external_references: []
traceability_refs: []
```

Rules:

1. `implementation_allowed` must be `false`.
2. `direct_runtime_allowed` must be `false`.
3. `artifact_type` must be one of the allowed L2 profile/spec types.
4. `required_l1_units` is required when `requires_l1_handoff` is `true`.
5. `forbidden_actions` must include L0 modification, L1 bypass, external repository edits, direct tool execution, and autonomous patching unless a higher-authority L2 document explicitly explains why the item is not applicable.
6. A target artifact that lacks this shape may remain exploratory, but it must not be marked `ready-for-l1-handoff`.

### 11.2 Normative Language and Claim Discipline

L2 FICs and target artifacts must use controlled claim language.

Allowed readiness claims:

```text
exploratory
draft
reviewed
ready-for-l1-handoff
blocked
deprecated
archived
```

Forbidden claims at the current stage:

```text
implemented
validated runtime
release ready
autonomous ready
production ready
L2 execution ready
external integration complete
```

If such a claim appears in a L2 profile/spec without L1-governed evidence, the L2 FIC must be downgraded to `blocked` or the claim must be removed.

### 11.3 Runtime Directory Scan Rule

The L2 FIC validator must explicitly scan for prohibited executable runtime directories before any profile/spec package can be marked `ready-for-l1-handoff`.

Prohibited executable directories at the current stage:

```text
L2/runtime/
L2/controller/
L2/agents/
L2/tools/
L2/model_router/
L2/memory/
L2/autonomy/
```

Rules:

1. These directories should be absent at the current stage.
2. If a directory exists only as documentation or a placeholder, it must contain a README stating that it is non-executable and not implementation authority.
3. Any `.py`, `.js`, `.ts`, `.sh`, executable script, notebook, or tool configuration inside these directories is blocking unless a later L2 implementation-governance standard explicitly authorizes it.
4. Runtime-directory scan results must appear in the validation output.
5. A skipped runtime-directory scan blocks `ready-for-l1-handoff` because it could hide unauthorized implementation.

---

## 12. Profile/Spec Non-Goals and Negative Space

Every L2 FIC must include negative space.

Required non-goal classes:

```yaml
non_goals:
  runtime_execution:
    - "does not execute tools"
    - "does not run models"
    - "does not patch files"
  governance_bypass:
    - "does not bypass L1 FIC workflow"
    - "does not bypass L0 proof gates"
  external_project_control:
    - "does not directly modify external repositories"
  autonomy:
    - "does not perform autonomous self-improvement"
```

Forbidden behavior must also be listed in the target artifact when the target artifact is a YAML profile.

A L2 profile/spec that lacks non-goals is not ready for L1 handoff.

---

## 13. Inputs and Source Material

A L2 FIC must define which source materials may inform the profile/spec.

Example:

```yaml
allowed_source_material:
  authoritative:
    - "L2/docs/00_L2_SYSTEM_GOAL.md"
    - "L2/docs/03_L2_PROFILE_MODEL.md"
    - "L1/docs/09_L1_CODING_AGENT_HANDOFF_RULES.md"
  supporting:
    - "external project README, if cited and freshness-checked"
  forbidden:
    - "unlabeled generated outputs"
    - "conversation-only assumptions"
    - "stale implementation notes"
```

Rules:

1. External project references must be labeled as external and freshness-sensitive.
2. External references do not become implementation authority.
3. Generated placeholders cannot define normative behavior.
4. Conversation notes must be converted into L2 documents before becoming authority.
5. A FIC must distinguish authoritative, supporting, optional, historical, and forbidden context.

---

## 14. Expected Outputs

A L2 profile/spec FIC must state what the target artifact may output or define.

Allowed output classes:

```text
- profile definition
- blueprint definition
- integration intent
- evaluation criteria
- risk notes
- L1 handoff proposal
- required L1 unit list
- future FIC candidate list
```

Forbidden output classes:

```text
- code patch
- runtime action
- direct tool call
- direct external repository change
- L0 modification
- L1 modification without L1 FIC
- release claim
```

---

## 15. Required L1 Handoff Targets

A L2 FIC that may later lead to implementation must list the L1 units needed for conversion.

Example:

```yaml
required_l1_handoff:
  required: true
  target_l1_units:
    - "AGENT_X_L1::UNIT-L1-003"  # goal classifier
    - "AGENT_X_L1::UNIT-L1-004"  # unit planner
    - "AGENT_X_L1::UNIT-L1-005"  # FIC generator
    - "AGENT_X_L1::UNIT-L1-006"  # FIC validator
    - "AGENT_X_L1::UNIT-L1-007"  # handoff packet builder
  required_packet:
    - "profile artifact"
    - "profile FIC"
    - "evaluation spec"
    - "risk ledger entry"
    - "traceability matrix entry"
```

Rules:

1. Missing L1 handoff targets block `ready-for-l1-handoff` status.
2. L2 may request L1 handoff, but L1 decides whether implementation proceeds.
3. L1 may reject, split, defer, or rewrite the implementation package.
4. A L2 FIC must not name L1 implementation files as permitted edit targets.
5. The handoff packet must preserve `implementation_allowed: false` for L2.

### 15.1 L2-to-L1 Handoff Packet Schema

A L2 FIC marked `ready-for-l1-handoff` must define or reference a handoff packet.

Recommended path:

```text
L2/generated/handoff_packets/<l2_fic_id>_handoff_to_l1.yaml
```

Minimum schema:

```yaml
l2_to_l1_handoff_packet:
  packet_id: "L2-HANDOFF-SR-001"
  source_l2_fic_id: "L2-FIC-PROFILE-SR-001"
  source_target_artifact_id: "AGENT_X_L2::L2-PROFILE-SR-001"
  source_target_path: "L2/profiles/symbolic_regression_controller.yaml"
  handoff_status: "proposed|ready-for-l1-review|rejected|accepted-by-l1"
  implementation_allowed_by_l2: false
  requested_l1_units:
    - "AGENT_X_L1::UNIT-L1-003"
    - "AGENT_X_L1::UNIT-L1-004"
    - "AGENT_X_L1::UNIT-L1-005"
    - "AGENT_X_L1::UNIT-L1-006"
    - "AGENT_X_L1::UNIT-L1-007"
  proposed_l1_fic_candidates: []
  required_l1_decisions:
    - "accept|reject|split|defer|request-profile-delta"
  allowed_l1_outputs:
    - "L1 FIC draft"
    - "L1 implementation package"
    - "L1 rejection or deferral"
  forbidden_l2_outputs:
    - "code patch"
    - "tool execution"
    - "external repository edit"
  evidence_refs: []
  risk_refs: []
```

Rules:

1. The packet proposes work to L1; it does not authorize implementation.
2. The packet must not list permitted code-edit files.
3. L1 must convert any accepted work into L1 FIC/SIB/ES/EQC-governed artifacts before implementation.
4. If L1 rejects the handoff, the L2 profile/spec must remain reviewed, draft, blocked, or deferred.

### 15.2 Profile Package Closure Rule

A L2 FIC package is closed for L1 handoff only when all required artifacts are present, internally consistent, and explicitly non-executable.

Minimum package manifest:

```yaml
l2_profile_package_manifest:
  manifest_version: "v0.4"
  portfolio_id: "AGENT_X_L2"
  package_id: "L2-PKG-SR-001"
  source_l2_fic_id: "L2-FIC-PROFILE-SR-001"
  target_artifact_id: "AGENT_X_L2::L2-PROFILE-SR-001"
  required_artifacts:
    profile: "L2/profiles/symbolic_regression_controller.yaml"
    fic: "L2/fic/units/L2-FIC-PROFILE-SR-001-symbolic-regression-controller.md"
    evaluation_spec: "L2/evaluation_specs/symbolic_regression_eval.md"
    risk_record: "L2/docs/07_L2_RISK_LEDGER.md"
    traceability_record: "L2/docs/08_L2_TRACEABILITY_MATRIX.md"
    handoff_packet: "L2/generated/handoff_packets/L2-FIC-PROFILE-SR-001_handoff_to_l1.yaml"
    completion_record: "L2/evidence/L2-FIC-PROFILE-SR-001/<timestamp>_completion_record.yaml"
    review_packet: "L2/evidence/L2-FIC-PROFILE-SR-001/<timestamp>_review_packet.md"
  implementation_allowed: false
  release_evidence: false
  runtime_scan_status: "PASS|FAIL|SKIPPED"
  validator_output: "L2/generated/validation_report.md"
```

Closure checklist:

```text
[ ] every required artifact exists
[ ] every required artifact uses canonical repository-relative paths
[ ] registry and FIC frontmatter match
[ ] target artifact shape validates or is manually checked against schema
[ ] implementation_allowed is false everywhere
[ ] direct_runtime_allowed is false everywhere
[ ] required L1 units exist as references or are marked unknown/blocking
[ ] evaluation spec exists
[ ] risk entry exists
[ ] handoff packet exists
[ ] completion and review evidence exist
[ ] runtime-directory scan passed
[ ] generated placeholders are not used as release evidence
```

Failure to close the package prevents `ready-for-l1-handoff`.

---

## 16. Evaluation Contract

Every L2 FIC must define how the profile/spec will be evaluated.

Minimum fields:

```yaml
evaluation_contract:
  evaluation_spec_path: "L2/evaluation_specs/symbolic_regression_eval.md"
  success_criteria:
    - "profile has clear purpose and non-goals"
    - "profile maps to required L1 units"
    - "forbidden runtime actions are explicit"
    - "integration references are external and non-authoritative"
  failure_conditions:
    - "profile implies direct implementation"
    - "profile bypasses L1"
    - "profile modifies L0 or external repos directly"
    - "profile lacks testable handoff criteria"
```

A profile/spec cannot be marked `ready-for-l1-handoff` without an evaluation contract.

---

## 17. Risk Classification

Allowed risk levels:

```text
low
medium
high
critical
```

Default risk mapping:

| L2 Artifact | Default Risk |
|---|---:|
| profile with no external integration | low |
| profile with future implementation path | medium |
| profile involving external repo modification | high |
| profile involving autonomy, tool execution, memory writes, or L0 change | critical/prohibited at current stage |

Rules:

1. Current L2 stage should avoid high and critical implementation claims.
2. High-risk profiles may exist as design documents but cannot request implementation until L1 accepts a separate governed package.
3. Critical profiles must be marked blocked unless explicitly constrained to design-only analysis.
4. A risk-level downgrade requires a review note explaining why the risk no longer applies.

---

## 18. Source Freshness and External Reference Policy

L2 profiles may reference external projects such as PySR_custom, Glyphser, or Symbiant only as external design references.

External references must be freshness-scoped:

```yaml
external_reference:
  project: "PySR_custom"
  relation: "future symbolic-regression backend candidate"
  authority: "external-informational"
  implementation_allowed: false
  requires_l1_handoff: true
  freshness_checked_utc: null
  reference_status: "unverified|fresh|stale"
```

Rules:

1. External project references must include name, purpose, and freshness date when used as current design input.
2. External project references do not authorize edits.
3. Integration specs must say whether the reference is informational, proposed, or implementation-bound.
4. Implementation-bound references require L1 handoff.
5. L2 must not store secrets, tokens, credentials, or private access assumptions.
6. If freshness is unknown, the reference may support brainstorming but must not define implementation constraints.

---

## 19. L2 FIC Readiness Checklist

A L2 FIC is ready for L1 handoff only when:

```text
[ ] identity is complete
[ ] registry entry exists and matches the FIC
[ ] target artifact exists
[ ] target artifact is profile/spec, not runtime code
[ ] target artifact has matching version marker
[ ] status is reviewed or ready-for-l1-handoff
[ ] implementation_allowed is false
[ ] purpose is narrow
[ ] non-goals are explicit
[ ] forbidden runtime behavior is listed
[ ] allowed source material is declared
[ ] expected outputs are declared
[ ] L1 handoff targets are declared
[ ] evaluation contract exists
[ ] risk level is assigned
[ ] traceability entry exists or is planned
[ ] generated reports are not treated as release evidence
[ ] no L0/L1 bypass is implied
[ ] no external repository modification is authorized
[ ] completion evidence path is declared
[ ] review packet path is declared
```

If any required item fails, status must remain `draft`, `reviewed`, or `blocked`.

---

## 20. L2 FIC Validation Output

A future lightweight validator may produce canonical JSON:

```json
{
  "portfolio_id": "AGENT_X_L2",
  "validator": "l2-fic validate",
  "l2_fic_version": "v0.4.0",
  "status": "PASS|FAIL",
  "errors": [],
  "warnings": [],
  "checked_fics": [],
  "ready_for_l1_handoff": [],
  "blocked_fics": [],
  "implementation_allowed_violations": [],
  "prohibited_runtime_path_violations": [],
  "missing_l1_handoff_targets": [],
  "skipped_checks": []
}
```

Rules:

1. Validator output must be deterministic.
2. Unknown error codes are invalid.
3. A skipped check must be reported with a reason and release/handoff blocking flag.
4. A validator must not silently pass a missing target artifact.
5. Lists must be sorted lexicographically by stable ID.

### 20.1 Validator Input Manifest

Every L2 FIC validation run must declare the exact input set.

Minimum manifest:

```yaml
validator_input_manifest:
  validator: "l2-fic validate"
  validator_version: "v0.4.0"
  workspace_ref: "local-working-tree-or-commit"
  inputs:
    - path: "L2/fic/index.l2-fic.yaml"
      digest: "sha256:<hash-or-pending>"
    - path: "L2/fic/units/L2-FIC-PROFILE-SR-001-symbolic-regression-controller.md"
      digest: "sha256:<hash-or-pending>"
    - path: "L2/profiles/symbolic_regression_controller.yaml"
      digest: "sha256:<hash-or-pending>"
    - path: "L2/docs/03_L2_PROFILE_MODEL.md"
      digest: "sha256:<hash-or-pending>"
  profile: "agent_x_l2_profile_spec_stage"
```

Rules:

1. Validation output without input paths is not acceptable handoff evidence.
2. Validation output without input digests may be accepted only as bootstrap evidence, not release evidence.
3. A validator profile change is a `STATE` change and requires revalidation.
4. The validator must fail closed when a required input is missing.

### 20.2 Validator Profile and No-Silent-Skip Rule

Required checks for `ready-for-l1-handoff`:

```text
registry_exists
registry_frontmatter_match
target_artifact_exists
target_artifact_shape_valid
implementation_allowed_false
runtime_paths_absent_or_non_executable
required_l1_units_declared
evaluation_contract_present
risk_level_present
non_goals_present
external_references_scoped
false_release_claim_absent
completion_record_present
review_packet_present
```

If a check cannot run, validation must report it as skipped and mark whether it blocks handoff. A required check skipped without reporting is itself a blocking validator failure.

### 20.3 Generated-Artifact Edit Policy

Generated L2 FIC artifacts are not manual sources of truth.

Generated locations:

```text
L2/generated/profile_catalog.yaml
L2/generated/l2_semantic_lockfile.yaml
L2/generated/readiness_report.md
L2/generated/validation_report.md
L2/generated/handoff_packets/*.yaml
```

Rules:

1. Generated artifacts must declare their generator, input files, and input digests when used as evidence.
2. Manual edits to generated artifacts invalidate them unless a maintenance task explicitly permits the edit.
3. Generated placeholders may support scaffold existence only; they must not support handoff readiness or release claims.
4. The authoritative source for profile/spec meaning remains the L2 FIC, target profile/spec, L2 docs, and L2 registry, not generated reports.
5. Validators must distinguish `bootstrap-placeholder-not-release-evidence` from validator-produced evidence.

---

## 21. Error Code Registry

Required file:

```text
L2/fic/l2-fic-error-codes.yaml
```

Initial codes:

```yaml
error_codes:
  L2_FIC_MISSING_TARGET: "Target artifact path is missing or does not exist."
  L2_FIC_TARGET_IS_RUNTIME_CODE: "Target artifact is runtime code, which is prohibited at current L2 stage."
  L2_FIC_IMPLEMENTATION_ALLOWED_TRUE: "L2 FIC incorrectly authorizes implementation."
  L2_FIC_MISSING_NON_GOALS: "L2 FIC lacks required non-goals."
  L2_FIC_MISSING_L1_HANDOFF: "L2 FIC lacks required L1 handoff targets."
  L2_FIC_EXTERNAL_AUTHORITY_LEAK: "External project notes are treated as implementation authority."
  L2_FIC_L0_BYPASS: "L2 FIC implies direct L0 modification or proof bypass."
  L2_FIC_L1_BYPASS: "L2 FIC implies implementation outside L1 governance."
  L2_FIC_NO_EVALUATION_CONTRACT: "L2 FIC lacks evaluation criteria."
  L2_FIC_FALSE_RELEASE_CLAIM: "L2 FIC makes release or implementation readiness claims not supported by evidence."
  L2_FIC_REGISTRY_MISMATCH: "FIC frontmatter does not match the L2 FIC registry."
  L2_FIC_VERSION_MARKER_MISSING: "FIC or target artifact lacks a matching version marker."
  L2_FIC_DUPLICATE_TARGET: "More than one active L2 FIC claims the same target artifact."
  L2_FIC_SKIPPED_REQUIRED_CHECK: "Validator skipped a required check without blocking or reporting it correctly."
  L2_FIC_TARGET_SCHEMA_INVALID: "Target profile/spec does not satisfy the minimum target artifact schema."
  L2_FIC_HANDOFF_PACKET_MISSING: "Ready-for-l1-handoff FIC lacks a handoff packet or equivalent handoff record."
  L2_FIC_PROHIBITED_CLAIM: "L2 artifact contains a runtime, implementation, or release claim not supported at the current stage."
  L2_FIC_EVIDENCE_MUTATED: "Evidence supporting a reviewed or handoff-ready state was overwritten instead of appended."
  L2_FIC_ENUM_UNKNOWN: "A status, type, risk level, decision, or exit status is not in the controlled enum registry."
  L2_FIC_RUNTIME_SCAN_SKIPPED: "Runtime-directory scan was skipped for a handoff-ready package."
  L2_FIC_PACKAGE_NOT_CLOSED: "The L2 profile package lacks required closure artifacts or consistency checks."
  L2_FIC_GENERATED_ARTIFACT_MANUAL_EDIT: "A generated artifact appears manually edited without authorization."
  L2_FIC_CROSS_STANDARD_MISMATCH: "L2 FIC, workflow, ES, SIB, or EQC sidecars disagree on identity, status, or handoff boundary."
```

Unknown error codes are invalid validator output.

---

## 22. Traceability Requirements

Each L2 FIC must trace to:

```text
L2 system goal
L2 profile model
L2 target artifact
L2 evaluation spec
L2 risk ledger
L2-to-L1 handoff packet, if applicable
```

Recommended traceability row:

```yaml
traceability:
  l2_fic_id: "L2-FIC-PROFILE-SR-001"
  target_artifact_id: "AGENT_X_L2::L2-PROFILE-SR-001"
  target_path: "L2/profiles/symbolic_regression_controller.yaml"
  governing_docs:
    - "AX-L2-DOC-GOAL-001"
    - "AX-L2-DOC-PROFILE-MODEL-001"
  evaluation_refs:
    - "L2/evaluation_specs/symbolic_regression_eval.md"
  l1_handoff_refs: []
  status: "draft"
```

---

## 23. Change Policy and Version Impact

A L2 FIC must be updated before changing the functional meaning of its target profile/spec.

Functional changes include:

```text
- changing profile purpose;
- changing allowed or forbidden actions;
- changing required L1 handoff units;
- changing integration scope;
- changing evaluation criteria;
- changing risk level;
- changing implementation_allowed;
- changing external project assumptions;
- changing profile outputs.
```

Version impact:

| Change | Impact |
|---|---|
| typo or formatting | PATCH |
| clarifying existing non-goal | PATCH |
| adding a compatible evaluation criterion | MINOR |
| adding a new required L1 handoff unit | MINOR |
| changing specialization type | MAJOR |
| allowing previously forbidden runtime behavior | MAJOR and blocked |
| changing `implementation_allowed` to true | MAJOR and prohibited at current stage |

A missing version-impact classification blocks `ready-for-l1-handoff`.

---

## 24. LLM Authoring Instructions

A weaker LLM editing L2 profiles/specs must follow these rules:

```text
1. Edit only L2 profile/spec documents named in the task.
2. Do not create runtime code.
3. Do not create tool execution code.
4. Do not set implementation_allowed to true.
5. Do not claim release readiness.
6. Do not modify L0 or L1.
7. Do not invent external project APIs.
8. If a profile requires implementation, create a L2-to-L1 handoff proposal instead.
9. If required L1 units are unclear, mark BLOCKED_MISSING_L1_HANDOFF.
10. Preserve the target artifact path and ID unless a migration note is added.
11. Do not manually edit generated placeholders unless a maintenance task explicitly authorizes it.
12. Do not treat generated placeholders as evidence.
```

Allowed final statuses:

```text
DRAFT_UPDATED
REVIEWED
READY_FOR_L1_HANDOFF
BLOCKED
NO_CHANGE
```

---

## 25. Completion Evidence

Any L2 FIC edit must produce a completion record.

Recommended path:

```text
L2/evidence/<l2_fic_id>/<utc_timestamp>_completion_record.yaml
```

Template:

```yaml
completion_record:
  l2_fic_id: "L2-FIC-PROFILE-SR-001"
  target_artifact_id: "AGENT_X_L2::L2-PROFILE-SR-001"
  status: "READY_FOR_L1_HANDOFF|DRAFT_UPDATED|BLOCKED|NO_CHANGE"
  files_inspected: []
  files_changed: []
  profile_or_spec_changes:
    purpose_changed: false
    non_goals_changed: false
    handoff_targets_changed: false
    evaluation_changed: false
    risk_changed: false
  version_impact: "NONE|PATCH|MINOR|MAJOR"
  implementation_allowed: false
  l1_handoff_required: true
  checks_run: []
  checks_not_run: []
  unresolved_unknowns: []
  residual_risks: []
```

Evidence must not claim implementation validation.

---

## 26. Review Packet Requirements

A L2 FIC ready for L1 handoff must have a review packet.

Recommended path:

```text
L2/evidence/<l2_fic_id>/<utc_timestamp>_review_packet.md
```

Minimum contents:

```yaml
review_packet:
  l2_fic_id: "L2-FIC-PROFILE-SR-001"
  target_artifact_id: "AGENT_X_L2::L2-PROFILE-SR-001"
  decision: "ready_for_l1_handoff|blocked|rejected"
  profile_purpose_review: []
  non_goal_review: []
  forbidden_runtime_behavior_review: []
  l1_handoff_target_review: []
  evaluation_contract_review: []
  risk_review: []
  source_freshness_review: []
  false_claim_check:
    release_claim_present: false
    implementation_claim_present: false
  residual_risks: []
```

### 26.1 Evidence Immutability

L2 FIC evidence is append-only.

Rules:

1. Completion records and review packets that supported a status transition must not be overwritten.
2. Replacement evidence must use a new timestamped path.
3. A review packet must name the exact completion record it reviewed.
4. Evidence may cite validator output only if the validator input manifest is present.
5. Generated placeholders must not be cited as proof of readiness except for scaffold existence.

### 26.2 Status Downgrade Rule

A L2 FIC or target artifact must be downgraded to `blocked` or `draft` when any of the following appears after review:

```text
- implementation_allowed becomes true;
- a runtime-like target is added;
- L1 handoff units become stale or invalid;
- an external reference becomes stale while still used as current design input;
- evaluation criteria are removed or weakened;
- evidence is overwritten or missing;
- a false implementation/release claim is introduced.
```

Downgrade must be recorded in the completion record or validation log.

---

## 27. Unknowns, Deferrals, and Waivers

Unknowns must be explicit.

```yaml
unknown:
  id: "L2-FIC-UNK-001"
  field: "required_l1_units"
  severity: "blocking|non_blocking"
  reason: "Profile references a future L1 unit that does not exist."
  resolution: "blocked_until_l1_mapping_exists"
```

Deferrals are allowed only for profile/spec completeness, not for bypassing runtime prohibitions.

```yaml
deferral:
  id: "L2-FIC-DEF-001"
  deferred_item: "optional evaluation scenario"
  reason: "not needed for first handoff"
  blocks_l1_handoff: false
```

Non-waivable at current stage:

```text
- implementation_allowed set to true;
- L2 runtime code target;
- direct L0 modification permission;
- direct L1 modification permission;
- direct external repository edit permission;
- release-ready claim without release evidence;
- missing target artifact for ready-for-l1-handoff status.
```

---

## 28. Anti-Patterns

Reject or block a L2 FIC if it contains:

```text
- runtime implementation instructions;
- direct L0 modification instructions;
- direct L1 modification instructions;
- direct external repository modification instructions;
- tool execution permission;
- hidden autonomy permission;
- model routing behavior without L1 governance;
- memory-write behavior without L1 governance;
- vague profile purpose;
- no non-goals;
- no evaluation contract;
- no L1 handoff path for implementation-bound profiles;
- release-ready claims without release evidence;
- generated placeholders treated as authoritative evidence.
```

---

## 29. Minimum First L2 FIC Set

The first L2 scaffold should include these L2 FICs:

```text
L2/fic/index.l2-fic.yaml
L2/fic/l2-fic-error-codes.yaml
L2/fic/units/L2-FIC-PROFILE-CODING-001-coding-agent.md
L2/fic/units/L2-FIC-PROFILE-SR-001-symbolic-regression-controller.md
L2/fic/units/L2-FIC-PROFILE-RESEARCH-001-research-agent.md
L2/fic/units/L2-FIC-PROFILE-REPO-001-repo-maintenance-agent.md
```

Only profile/spec FICs should be created at this stage.

No L2 code FICs should be created yet.

### 29.1 Minimum Schema Closure

The first L2 FIC scaffold should include minimal schemas, even if they are not yet release-grade.

Recommended files:

```text
L2/fic/l2-fic.schema.json
L2/fic/l2-fic-registry.schema.json
L2/fic/l2-target-artifact.schema.json
L2/fic/l2-handoff-packet.schema.json
L2/fic/l2-completion-record.schema.json
L2/fic/l2-review-packet.schema.json
L2/fic/l2-validation-output.schema.json
```

Rules:

1. A missing schema is acceptable for early scaffold only if the validator profile marks it `not-yet-executable`.
2. A missing schema must not be hidden by a PASS result.
3. A handoff-ready FIC should have at least manual checklist validation against these schema shapes.
4. These schemas must stay focused on profile/spec artifacts, not code artifacts.

---

## 30. Readiness Decision Table

| Condition | L2 FIC Status |
|---|---|
| Target profile/spec missing | `blocked` |
| Target exists but purpose incomplete | `draft` |
| Purpose, non-goals, risk, and evaluation exist | `reviewed` |
| L1 handoff targets and packet requirements exist | `ready-for-l1-handoff` |
| Runtime code is targeted | `blocked` |
| Implementation allowed is true | `blocked` |
| External repo edit is authorized directly | `blocked` |
| Registry/frontmatter mismatch exists | `blocked` |
| Version marker missing for reviewed target | `blocked` |

---

## 31. Cross-Standard Consistency Checks

This L2 FIC standard must remain consistent with the L2 workflow, future L2 ES, future L2 SIB, and future L2 EQC documents.

Required consistency checks:

```text
[ ] L2 FIC status vocabulary matches the L2 workflow status vocabulary
[ ] L2 FIC registry IDs match L2 ES document/object IDs or have explicit mappings
[ ] L2 target artifact IDs match L2 SIB document/object registry entries when SIB exists
[ ] L2 handoff packet names the same required L1 units as the profile/spec artifact
[ ] L2 EQC procedures, if present, do not authorize implementation or tool execution
[ ] generated lockfile/report status does not contradict FIC status
[ ] no standard claims release readiness while release_evidence is false
```

A mismatch is blocking for `ready-for-l1-handoff` unless explicitly recorded as a temporary bootstrap inconsistency.

---

## 32. Weaker-Agent Completion Response Format

A weaker LLM editing a L2 FIC or target profile/spec must finish with a controlled completion response.

Required final response shape:

```yaml
l2_fic_agent_result:
  status: "DRAFT_UPDATED|REVIEWED|READY_FOR_L1_HANDOFF|BLOCKED|NO_CHANGE"
  l2_fic_id: "L2-FIC-..."
  target_artifact_id: "AGENT_X_L2::..."
  files_inspected: []
  files_changed: []
  implementation_allowed_confirmed_false: true
  runtime_scan_result: "PASS|FAIL|NOT_RUN"
  l1_handoff_required: true
  l1_handoff_packet_created_or_updated: false
  checks_run: []
  checks_not_run: []
  unresolved_unknowns: []
  residual_risks: []
  evidence_paths: []
```

Rules:

1. The agent must not use prose-only completion for governed edits.
2. The agent must not claim `READY_FOR_L1_HANDOFF` unless package closure passes.
3. The agent must report `BLOCKED` when it cannot confirm `implementation_allowed: false`.
4. The agent must report `NO_CHANGE` only with inspected-file evidence.

---

## 33. Current-Stage Acceptance Criteria

This L2 Lightweight EQC-FIC standard is acceptable for the current L2 profile/spec stage when:

```text
[ ] it governs profile/spec artifacts only
[ ] it does not authorize L2 runtime implementation
[ ] it defines L2 FIC identity and registry rules
[ ] it defines canonical path and version marker rules
[ ] it defines readiness for L1 handoff
[ ] it requires non-goals and forbidden runtime behavior
[ ] it requires evaluation contracts
[ ] it requires risk classification
[ ] it defines completion and review evidence
[ ] it defines unknown/deferral handling
[ ] it defines minimum target artifact and handoff packet schemas
[ ] it defines evidence immutability and downgrade rules
[ ] it blocks false implementation/release claims
[ ] it defines package closure for L1 handoff
[ ] it defines controlled enum and runtime-directory scan rules
[ ] it defines generated-artifact edit policy
[ ] it defines weaker-agent completion response format
[ ] it remains lighter than L1 EQC-FIC
```

---

## 34. Deferred Full-FIC Capabilities

The following are deferred until L2 moves beyond profile/spec governance:

```text
- code-level public surface checking;
- runtime dependency scanning;
- executable post-code gates;
- L2 runtime SIB bindings;
- L2 golden traces;
- L2 model/tool execution validators;
- release-candidate paired checkpoints;
- autonomous-agent implementation FICs.
```

These must not be added prematurely.

---

## 35. Maturity Levels

L2 FIC maturity levels:

| Level | Name | Meaning | Implementation allowed? |
|---:|---|---|---:|
| 0 | notes | Informal profile/spec notes only | no |
| 1 | registered | L2 FIC registry entry exists | no |
| 2 | reviewed | Target artifact, FIC, risk, non-goals, and evaluation contract exist | no |
| 3 | handoff-ready | Handoff packet, completion record, and review packet exist | no, L1 decision required |
| 4 | L1-accepted | L1 accepts the handoff and creates L1-governed work | only under L1 |
| 5 | release-bound | L1-generated implementation package enters release-candidate governance | only under L1 release rules |

Current target for L2 is Level 3.

---

## 36. Current-Stage Self-Assessment Gate

Before this standard is treated as final for the L2 profile/spec stage, confirm:

```text
[ ] it blocks L2 implementation permission
[ ] it governs only profile/spec artifacts
[ ] it defines a registry and canonical header
[ ] it defines minimum target artifact schema
[ ] it defines L2-to-L1 handoff packet shape
[ ] it requires non-goals and forbidden behavior
[ ] it requires evaluation and risk review
[ ] it requires completion and review evidence
[ ] it defines validator input/output expectations
[ ] it defines error codes
[ ] it includes evidence immutability and downgrade rules
[ ] it defines package closure and controlled enum behavior
[ ] it defines runtime-directory scan and generated-artifact edit rules
[ ] it defers full code-level FIC machinery until L1 accepts implementation work
```

If all items pass, the standard is complete for the current L2 profile/spec stage.

---

## 37. Final Rule

L2 FICs are future-implementation contracts, not implementation permission.

Correct:

```text
L2 profile/spec -> L2 FIC -> reviewed L2 handoff proposal -> L1 FIC-governed implementation decision
```

Incorrect:

```text
L2 profile/spec -> direct code implementation
```

At the current stage, L2 must stay thin, explicit, profile-driven, and subordinate to L1 implementation governance.
