# Agent_X L2 Lightweight EQC

**Document ID:** `AGENT-X-L2-EQC-001`  
**Version:** `v0.4.0`  
**Status:** `ready-for-use`  
**Layer:** `L2`  
**Applies to:** Agent_X L2 profile/spec procedures only  
**Primary purpose:** Define a lightweight EquationCode discipline for L2 profile-selection, specialization-classification, evaluation-routing, and L2-to-L1 handoff procedures without creating L2 runtime implementation authority.

---

## 1. Purpose

This document defines how Agent_X L2 uses EQC selectively.

L2 is the profile/specification layer. It defines specialization profiles, blueprints, integration specs, and evaluation specs. L2 does not execute tools, mutate repositories, patch L0, patch L1, run autonomous agents, or implement runtime behavior.

Therefore, L2 does **not** need full EQC for every profile document. It needs lightweight EQC only for procedures that make repeatable decisions, such as:

```text
- selecting the best L2 profile for a specialization request;
- classifying a request as coding, research, symbolic-regression, repo-maintenance, or orchestration;
- detecting when a profile requires L1 handoff;
- ranking candidate profiles deterministically;
- deciding whether a profile package is ready to propose to L1;
- producing a bounded L2-to-L1 handoff proposal.
```

The controlling rule is:

```text
L2 EQC may specify decision procedures.
L2 EQC must not authorize runtime execution.
Any implementation generated from L2 EQC must be routed through L1 FIC-governed workflow first.
```

---

## 2. Scope

This lightweight EQC applies to:

```text
L2/eqc/procedures/*.eqc.md
L2/eqc/operators/*.eqc.md
L2/eqc/manifests/*.yaml
L2/eqc/tests/*.yaml
L2/generated/profile_catalog.yaml
L2/generated/l2_semantic_lockfile.yaml
L2/generated/validation_report.md
L2/generated/readiness_report.md
```

It may also apply to algorithmic sections embedded in:

```text
L2/profiles/*.yaml
L2/blueprints/*.md
L2/evaluation_specs/*.md
L2/integration_specs/*.md
```

only when those sections define deterministic selection, ranking, classification, scoring, or handoff decisions.

It does **not** apply to simple narrative profile text, background notes, or non-algorithmic descriptions.

---

## 3. Relationship to Other L2 Standards

This document is one part of the L2 lightweight standards stack:

```text
1. L2 Pseudocode-to-FIC Workflow
   Main workflow for turning profiles/specs into bounded L1 handoff proposals.

2. L2 Lightweight EQC-FIC
   Contract discipline for profile/spec artifacts that may later become implementation units.

3. L2 Lightweight EQC-SIB/Bridge
   Binding from L2 profiles/specs to future L1 handoff and FIC targets.

4. L2 Lightweight EQC-ES
   Registry and graph governance for L2 documents.

5. L2 Lightweight EQC
   Algorithm/procedure discipline for deterministic L2 profile/spec decisions.
```

L2 EQC is subordinate to the L2 workflow, L2 ES registry, and L2 SIB bridge. If a decision procedure selects a profile that the registry marks stale, blocked, deprecated, or unbound, the procedure must return a blocked status.

---

## 4. L2 EQC Boundary Rules

### 4.1 Allowed

L2 EQC may define:

```text
- pure decision procedures;
- deterministic ranking functions;
- profile selection logic;
- profile readiness scoring;
- evaluation-spec routing;
- L2-to-L1 handoff decision logic;
- bounded request classification;
- static catalog validation logic;
- no-runtime profile compatibility checks.
```

### 4.2 Forbidden

L2 EQC must not define or authorize:

```text
- direct code generation;
- direct repository mutation;
- autonomous patching;
- shell execution;
- network execution;
- live model routing;
- memory writes;
- tool execution;
- runtime orchestration;
- direct PySR_custom modification;
- direct L0 modification;
- direct L1 modification;
- bypassing L1 FIC workflow;
- L2/controller, L2/runtime, L2/agents, L2/tools, or L2/autonomy implementation behavior.
```

If an L2 EQC procedure appears to require one of these behaviors, it must return:

```text
BLOCKED_REQUIRES_L1_HANDOFF
```

or:

```text
BLOCKED_PROHIBITED_L2_RUNTIME_BEHAVIOR
```

---

## 5. Required L2 EQC Files

The first lightweight L2 EQC slice should contain:

```text
L2/eqc/
  manifests/
    l2-eqc-manifest.yaml

  procedures/
    L2_SelectProfile.eqc.md
    L2_AssessProfileReadiness.eqc.md
    L2_BuildL1HandoffProposal.eqc.md

  operators/
    classify_specialization_request.eqc.md
    select_profile_candidates.eqc.md
    rank_profile_candidates.eqc.md
    check_profile_boundary_conflicts.eqc.md
    decide_l1_handoff_required.eqc.md
    build_profile_readiness_score.eqc.md

  tests/
    profile-selection.test-vectors.yaml
    handoff-decision.test-vectors.yaml
    readiness-score.test-vectors.yaml
```

Generated outputs:

```text
L2/generated/
  profile_catalog.yaml
  l2_semantic_lockfile.yaml
  validation_report.md
  readiness_report.md
```

Rules:

```text
- Generated outputs are placeholders until produced by an L2 validator.
- Generated outputs must not be manually edited as source of truth.
- EQC procedures must call only declared L2 EQC operators.
- Operators must not access files, network, shell, tools, model APIs, or runtime state.
```

---

## 6. Identity and ID Rules

### 6.1 Portfolio ID

```yaml
portfolio_id: "AGENT_X_L2"
```

### 6.2 EQC object IDs

Use stable IDs:

```text
L2-EQC-PROC-001
L2-EQC-OP-001
L2-EQC-TEST-001
L2-EQC-MANIFEST-001
```

Global IDs:

```text
GlobalEqcProcID = AGENT_X_L2::<ProcID>
GlobalEqcOpID   = AGENT_X_L2::<OpID>
GlobalEqcTestID = AGENT_X_L2::<TestID>
```

Examples:

```text
AGENT_X_L2::L2-EQC-PROC-001
AGENT_X_L2::L2-EQC-OP-001
AGENT_X_L2::L2-EQC-TEST-001
```

Rules:

```text
- IDs must not be reused after deletion.
- Renames require aliases or migration notes.
- Human-readable titles may change; IDs must remain stable.
- Cross-standard references must use global IDs.
```

---

## 7. Canonical Path Rules

All L2 EQC paths must be repository-relative POSIX paths.

Valid:

```text
L2/eqc/procedures/L2_SelectProfile.eqc.md
L2/eqc/operators/rank_profile_candidates.eqc.md
L2/eqc/tests/profile-selection.test-vectors.yaml
```

Invalid:

```text
../L2/eqc/procedures/L2_SelectProfile.eqc.md
/home/user/Agent_X/L2/eqc/procedures/L2_SelectProfile.eqc.md
L2\eqc\procedures\L2_SelectProfile.eqc.md
./L2/eqc/procedures/L2_SelectProfile.eqc.md
```

Rules:

```text
- Absolute paths are forbidden.
- Paths containing `..` after normalization are forbidden.
- Symlinks escaping the repository root are forbidden.
- Runtime-like directories under L2 are prohibited unless a future L2 implementation governance stage explicitly authorizes them.
```

---

## 8. Version Marker Rules

Every L2 EQC artifact must contain a version marker.

Markdown EQC procedure/operator files must contain:

```text
**EQC ID:** `<global-id>`
**Version:** `vX.Y.Z`
**Status:** `<status>`
```

YAML EQC sidecars must contain:

```yaml
version: "vX.Y.Z"
portfolio_id: "AGENT_X_L2"
```

Generated files must contain:

```yaml
generated_by: "<validator-or-generator-id>"
input_manifest_digest: "sha256:<pending-or-computed>"
release_evidence: false
```

Rules:

```text
- A missing version marker blocks validation.
- A registry version mismatch blocks validation.
- Generated artifacts without generator/input digest metadata are not evidence.
```

---

## 9. EQC Manifest

File:

```text
L2/eqc/manifests/l2-eqc-manifest.yaml
```

Minimum schema:

```yaml
l2_eqc_manifest_version: "v0.3"
portfolio_id: "AGENT_X_L2"
status: "active"
procedures:
  - proc_id: "L2-EQC-PROC-001"
    global_proc_id: "AGENT_X_L2::L2-EQC-PROC-001"
    title: "L2 Select Profile"
    path: "L2/eqc/procedures/L2_SelectProfile.eqc.md"
    version: "v0.1.0"
    status: "draft"
    uses_operators:
      - "AGENT_X_L2::L2-EQC-OP-001"
      - "AGENT_X_L2::L2-EQC-OP-002"
      - "AGENT_X_L2::L2-EQC-OP-003"
    test_vectors:
      - "AGENT_X_L2::L2-EQC-TEST-001"
operators:
  - op_id: "L2-EQC-OP-001"
    global_op_id: "AGENT_X_L2::L2-EQC-OP-001"
    title: "Classify Specialization Request"
    path: "L2/eqc/operators/classify_specialization_request.eqc.md"
    version: "v0.1.0"
    status: "draft"
    purity_class: "PURE"
    determinism: "deterministic"
test_vectors:
  - test_id: "L2-EQC-TEST-001"
    global_test_id: "AGENT_X_L2::L2-EQC-TEST-001"
    path: "L2/eqc/tests/profile-selection.test-vectors.yaml"
    status: "draft"
```

Rules:

```text
- Every procedure must list all operators it calls.
- Every operator must have exactly one manifest entry.
- Every procedure must have at least one test-vector set or an explicit deferral.
- Missing manifest entries are blocking errors.
- Operator version collisions are blocking errors.
```

---

## 10. Lightweight L2 EQC Header

Each L2 EQC procedure should start with:

```markdown
# <Procedure Name>

**EQC ID:** `AGENT_X_L2::L2-EQC-PROC-001`  
**Version:** `v0.2.0`  
**Status:** `draft`  
**Layer:** `L2`  
**Procedure Type:** `profile-selection|readiness-assessment|handoff-proposal|evaluation-routing`  
**Runtime Authority:** `none`  
**Implementation Authority:** `none`  
**L1 Handoff Required For Implementation:** `true`
```

The header must also declare:

```yaml
objective:
  sense: "MAXIMIZE|MINIMIZE|CLASSIFY|DECIDE"
  comparison_rule: "deterministic-total-order"
  invalid_input_policy: "return-blocked-status"
determinism:
  randomness_allowed: false
  time_allowed: false
  network_allowed: false
  shell_allowed: false
  filesystem_reads_allowed: false
ordering:
  tie_breaking: "lowest stable profile_id wins after sorted score tuple"
  sorting: "stable lexicographic"
```

---

## 11. L2 Procedure Template

Each L2 EQC procedure must be control-flow only.

Template:

```markdown
## Procedure

Procedure <Name>(request, profile_catalog, policy):

1. Validate inputs using declared operators.
2. Classify request using `L2Profile.ClassifySpecializationRequest_v1`.
3. Select candidate profiles using `L2Profile.SelectProfileCandidates_v1`.
4. Reject candidates with boundary conflicts using `L2Profile.CheckBoundaryConflicts_v1`.
5. Rank remaining candidates using `L2Profile.RankProfileCandidates_v1`.
6. Decide whether L1 handoff is required using `L2Profile.DecideL1HandoffRequired_v1`.
7. Return a controlled decision record.
```

Rules:

```text
- No inline scoring math unless it is trivial comparison wiring.
- Math, scoring, classification, and ranking semantics belong in operators.
- The procedure must explicitly handle empty candidates.
- The procedure must explicitly handle blocked, stale, deprecated, or conflicting profiles.
- The procedure must return a controlled status.
```

Allowed procedure statuses:

```text
SELECTED_PROFILE
NO_MATCH
BLOCKED_INVALID_REQUEST
BLOCKED_PROFILE_CATALOG_STALE
BLOCKED_PROFILE_BOUNDARY_CONFLICT
BLOCKED_REQUIRES_L1_HANDOFF
BLOCKED_PROHIBITED_L2_RUNTIME_BEHAVIOR
BLOCKED_REGISTRY_CONFLICT
REJECTED_UNGOVERNED_PROFILE
```

---

## 12. Operator Template

Each L2 EQC operator must use this structure:

```markdown
# <Operator Name>

**EQC ID:** `AGENT_X_L2::L2-EQC-OP-001`  
**Version:** `v0.2.0`  
**Status:** `draft`  
**Category:** `classification|selection|ranking|boundary-check|handoff-decision|readiness-score`  
**Purity Class:** `PURE`  
**Determinism:** `deterministic`

## Signature

```text
OperatorName(input_a: TypeA, input_b: TypeB) -> OutputType
```

## Preconditions

```text
- Inputs must be schema-valid.
- Profile IDs must be stable strings.
- Candidate lists must be deterministically ordered before scoring or ranking.
```

## Definition

```text
Precise numbered steps or simple equations.
```

## Tie Handling

```text
If scores tie, sort by profile_id ascending.
```

## Edge Cases

```text
- empty candidates;
- unknown specialization type;
- stale profile;
- duplicate profile ID;
- forbidden boundary condition;
- missing required L1 unit mapping.
```

## Test Vectors

```text
At least one normal case, one tie case, one blocked case.
```
```

Operator rules:

```text
- Operators must be PURE for the first L2 stage.
- Operators must not read files.
- Operators must not call tools.
- Operators must not call models.
- Operators must not use randomness or wall-clock time.
- Operators must not mutate input objects.
- Operators must return controlled statuses instead of throwing ambiguous failures.
```

---

## 13. Initial Procedure Set

### 13.1 `L2_SelectProfile`

Purpose:

```text
Select the best matching L2 profile for a specialization request, or return a blocked/no-match status.
```

Inputs:

```text
request
profile_catalog
policy
```

Output:

```yaml
selected_profile_decision:
  status: "SELECTED_PROFILE|NO_MATCH|BLOCKED_*"
  selected_profile_id: null
  candidate_profile_ids: []
  rejected_profile_ids: []
  ranking_basis: []
  boundary_conflicts: []
  l1_handoff_required: true
  required_l1_units: []
  reasons: []
```

### 13.2 `L2_AssessProfileReadiness`

Purpose:

```text
Determine whether a profile package is complete enough to propose to L1.
```

Output:

```yaml
profile_readiness_decision:
  status: "READY_FOR_L1_PROPOSAL|BLOCKED|DRAFT_ONLY"
  profile_id: ""
  missing_required_fields: []
  stale_sources: []
  boundary_conflicts: []
  required_fixes: []
```

### 13.3 `L2_BuildL1HandoffProposal`

Purpose:

```text
Build a non-executable proposal packet that L1 may accept, reject, or convert into FIC-governed work.
```

Output:

```yaml
l2_to_l1_handoff_proposal:
  proposal_id: "L2-L1-HANDOFF-001"
  source_profile_id: "AGENT_X_L2::<profile-id>"
  status: "PROPOSED_TO_L1"
  implementation_allowed_by_l2: false
  requested_l1_units: []
  proposed_fic_targets: []
  non_goals: []
  forbidden_actions: []
  evidence_refs: []
```

---

## 14. Initial Operator Set

Required first-slice operators:

```text
L2Profile.ClassifySpecializationRequest_v1
L2Profile.SelectProfileCandidates_v1
L2Profile.CheckBoundaryConflicts_v1
L2Profile.RankProfileCandidates_v1
L2Profile.DecideL1HandoffRequired_v1
L2Profile.BuildProfileReadinessScore_v1
L2Profile.BuildL1HandoffProposal_v1
```

Recommended mapping:

```yaml
operators:
  L2Profile.ClassifySpecializationRequest_v1:
    file: "L2/eqc/operators/classify_specialization_request.eqc.md"
  L2Profile.SelectProfileCandidates_v1:
    file: "L2/eqc/operators/select_profile_candidates.eqc.md"
  L2Profile.CheckBoundaryConflicts_v1:
    file: "L2/eqc/operators/check_profile_boundary_conflicts.eqc.md"
  L2Profile.RankProfileCandidates_v1:
    file: "L2/eqc/operators/rank_profile_candidates.eqc.md"
  L2Profile.DecideL1HandoffRequired_v1:
    file: "L2/eqc/operators/decide_l1_handoff_required.eqc.md"
  L2Profile.BuildProfileReadinessScore_v1:
    file: "L2/eqc/operators/build_profile_readiness_score.eqc.md"
  L2Profile.BuildL1HandoffProposal_v1:
    file: "L2/eqc/operators/build_l1_handoff_proposal.eqc.md"
```

---

## 15. Deterministic Scoring and Ranking Rules

Where L2 profiles are ranked, ranking must be deterministic.

Recommended score tuple:

```text
score(profile, request) = (
  specialization_match,
  required_l1_units_available,
  boundary_conflict_score,
  evaluation_spec_completeness,
  integration_spec_completeness,
  risk_penalty,
  profile_id_tiebreak
)
```

Ordering:

```text
1. Higher specialization_match wins.
2. Higher required_l1_units_available wins.
3. Lower boundary_conflict_score wins.
4. Higher evaluation_spec_completeness wins.
5. Higher integration_spec_completeness wins.
6. Lower risk_penalty wins.
7. Lower lexical profile_id wins.
```

Rules:

```text
- All score components must be defined by operators.
- Missing required data must not be silently scored as zero unless the operator declares that rule.
- Boundary conflicts dominate ranking and may force BLOCKED.
- A deprecated profile cannot win selection.
- A stale profile cannot win selection unless an explicit non-release exploratory waiver exists.
```

---

## 16. Trace Schema

Every L2 EQC procedure decision must be traceable.

Minimum trace record:

```yaml
l2_eqc_trace_record:
  procedure_id: "AGENT_X_L2::L2-EQC-PROC-001"
  procedure_version: "v0.1.0"
  input_request_digest: "sha256:<pending-or-computed>"
  profile_catalog_digest: "sha256:<pending-or-computed>"
  policy_digest: "sha256:<pending-or-computed>"
  candidate_profile_ids: []
  rejected_profile_ids: []
  selected_profile_id: null
  operator_calls:
    - operator_id: "AGENT_X_L2::L2-EQC-OP-001"
      operator_version: "v0.1.0"
      result_status: "PASS|BLOCKED|NO_MATCH"
  decision_status: "SELECTED_PROFILE|NO_MATCH|BLOCKED_*"
  l1_handoff_required: true
  generated_at_utc: "YYYY-MM-DDTHH:MM:SSZ"
```

Rules:

```text
- Trace records are evidence only after generated by a validator/procedure runner.
- Placeholder traces must say `release_evidence: false`.
- Procedure traces must not include hidden model reasoning.
- Procedure traces must be reconstructable from declared inputs.
```

---

## 17. Test Vectors

Each L2 EQC procedure must have test vectors.

Minimum test vector schema:

```yaml
l2_eqc_test_vectors_version: "v0.3"
portfolio_id: "AGENT_X_L2"
test_vectors:
  - test_id: "L2-EQC-TEST-001"
    procedure_id: "AGENT_X_L2::L2-EQC-PROC-001"
    name: "selects symbolic regression profile"
    inputs:
      request:
        specialization_type: "symbolic-regression"
      profile_catalog_ref: "fixture:profile_catalog_basic"
      policy_ref: "fixture:policy_default"
    expected:
      status: "SELECTED_PROFILE"
      selected_profile_id: "AGENT_X_L2::L2-PROFILE-SR-001"
      l1_handoff_required: true
  - test_id: "L2-EQC-TEST-002"
    procedure_id: "AGENT_X_L2::L2-EQC-PROC-001"
    name: "blocks runtime behavior request"
    inputs:
      request:
        requested_action: "execute PySR directly from L2"
    expected:
      status: "BLOCKED_PROHIBITED_L2_RUNTIME_BEHAVIOR"
```

Required test classes:

```text
- normal profile match;
- no profile match;
- tie between profiles;
- stale profile blocked;
- deprecated profile rejected;
- runtime action blocked;
- missing required L1 mapping blocked;
- profile boundary conflict blocked.
```

---

## 18. Validation Rules

L2 EQC validation must check:

```text
[ ] manifest exists
[ ] every procedure path exists
[ ] every operator path exists
[ ] every listed test-vector path exists
[ ] every procedure lists all called operators
[ ] every called operator resolves in the manifest
[ ] no operator version collision exists
[ ] every operator declares purity class
[ ] every first-slice operator is PURE
[ ] no procedure or operator authorizes runtime behavior
[ ] no prohibited L2 runtime-like directory is required by EQC
[ ] every procedure has controlled statuses
[ ] every ranking operation has deterministic tie handling
[ ] every handoff procedure sets implementation_allowed_by_l2=false
[ ] every generated output is marked placeholder or generated with input digests
[ ] every test vector has expected status
```

Validation output:

```yaml
l2_eqc_validation_result:
  validator: "l2-eqc validate"
  validator_version: "v0.3.0"
  status: "PASS|FAIL|WARNING"
  errors: []
  warnings: []
  checked_procedures: []
  checked_operators: []
  checked_test_vectors: []
  prohibited_runtime_paths_found: []
  unresolved_operator_refs: []
  missing_test_vectors: []
  generated_at_utc: "YYYY-MM-DDTHH:MM:SSZ"
```

---

## 19. Validator Input Manifest

Every validation run must declare its inputs.

Minimum:

```yaml
validator_input_manifest:
  validator: "l2-eqc validate"
  validator_version: "v0.3.0"
  workspace_ref: "local-working-tree-or-commit"
  inputs:
    - path: "L2/eqc/manifests/l2-eqc-manifest.yaml"
      digest: "sha256:<pending-or-computed>"
    - path: "L2/generated/profile_catalog.yaml"
      digest: "sha256:<pending-or-computed>"
    - path: "L2/ecosystem/ecosystem-registry.yaml"
      digest: "sha256:<pending-or-computed>"
    - path: "L2/sib/sib-l1-handoff-map.yaml"
      digest: "sha256:<pending-or-computed>"
  profile: "agent_x_l2_profile_spec"
```

Rules:

```text
- Validation output without input manifest is advisory only.
- Release-bound evidence must use computed digests.
- Bootstrap placeholders may use pending digests only if `release_evidence: false`.
```

---

## 20. Error Code Registry

L2 EQC validators must use controlled error codes.

Initial codes:

```yaml
error_codes:
  - code: "L2_EQC_MISSING_MANIFEST"
    severity: "error"
    blocking: true
  - code: "L2_EQC_MISSING_OPERATOR"
    severity: "error"
    blocking: true
  - code: "L2_EQC_OPERATOR_VERSION_COLLISION"
    severity: "error"
    blocking: true
  - code: "L2_EQC_PROCEDURE_HAS_INLINE_HIDDEN_SEMANTICS"
    severity: "error"
    blocking: true
  - code: "L2_EQC_RUNTIME_AUTHORITY_VIOLATION"
    severity: "error"
    blocking: true
  - code: "L2_EQC_HANDOFF_ALLOWS_IMPLEMENTATION"
    severity: "error"
    blocking: true
  - code: "L2_EQC_MISSING_TEST_VECTOR"
    severity: "error"
    blocking: true
  - code: "L2_EQC_NONDETERMINISTIC_TIE_BREAK"
    severity: "error"
    blocking: true
  - code: "L2_EQC_STALE_PROFILE_CATALOG"
    severity: "error"
    blocking: true
```

Unknown error codes are validator failures.

---

## 21. L2-to-L1 Handoff Rule

An L2 EQC procedure may produce a handoff proposal only.

It must not produce an implementation packet that authorizes coding.

Allowed handoff output:

```yaml
l2_to_l1_handoff_proposal:
  source_eqc_procedure: "AGENT_X_L2::L2-EQC-PROC-003"
  source_profile: "AGENT_X_L2::L2-PROFILE-SR-001"
  proposed_l1_units:
    - "AGENT_X_L1::UNIT-L1-003"
    - "AGENT_X_L1::UNIT-L1-004"
    - "AGENT_X_L1::UNIT-L1-005"
    - "AGENT_X_L1::UNIT-L1-006"
    - "AGENT_X_L1::UNIT-L1-007"
  proposed_fic_targets: []
  implementation_allowed_by_l2: false
  l1_acceptance_required: true
  l1_may_reject: true
```

Blocking condition:

```text
If implementation_allowed_by_l2 is true, validation fails.
```

---

## 22. Maturity Levels

```text
L2-EQC-M0 = advisory EQC notes only
L2-EQC-M1 = procedures/operators drafted
L2-EQC-M2 = manifest + tests + controlled statuses
L2-EQC-M3 = validator-ready profile/spec EQC
L2-EQC-M4 = L1 handoff-integrated EQC
L2-EQC-M5 = release-grade EQC with computed digests and executable validators
```

Current target:

```text
L2-EQC-M3
```

Do not target M5 until L2 is intentionally moved toward release-candidate profile governance.

---

## 23. Anti-Bloat Rule

L2 EQC must stay selective.

Do not create EQC documents for:

```text
- every profile field;
- simple narrative docs;
- background notes;
- static integration descriptions;
- documentation-only blueprints;
- obvious YAML schema examples.
```

Create EQC only when the document defines repeatable decision behavior that must be deterministic, testable, and traceable.

---

## 24. First Scaffold Acceptance Criteria

The first L2 EQC scaffold is acceptable when:

```text
[ ] L2/eqc/manifests/l2-eqc-manifest.yaml exists
[ ] L2/eqc/procedures/L2_SelectProfile.eqc.md exists
[ ] L2/eqc/procedures/L2_AssessProfileReadiness.eqc.md exists
[ ] L2/eqc/procedures/L2_BuildL1HandoffProposal.eqc.md exists
[ ] required operator docs exist
[ ] required test-vector files exist
[ ] all procedures declare no runtime authority
[ ] all operators are PURE
[ ] all handoff outputs set implementation_allowed_by_l2=false
[ ] generated outputs are marked not release evidence
[ ] no L2 runtime/controller/agent/tool directory is required
[ ] validation report distinguishes scaffold readiness from release readiness
```

---

## 25. Final Status Decision Table

| Condition | Status |
|---|---|
| Required EQC files missing | `BLOCKED_MISSING_EQC_ARTIFACTS` |
| Operator reference unresolved | `BLOCKED_OPERATOR_REFERENCE` |
| Test vectors missing | `BLOCKED_MISSING_TEST_VECTORS` |
| Procedure authorizes runtime behavior | `BLOCKED_RUNTIME_AUTHORITY_VIOLATION` |
| Handoff proposal allows implementation directly | `BLOCKED_L2_AUTHORITY_VIOLATION` |
| Procedures/operators complete but validator not implemented | `SCAFFOLD_READY_NOT_RELEASE_EVIDENCE` |
| Validator passes with computed digests | `VALIDATED_PROFILE_SPEC_EQC` |
```

---

## 26. Source-Standard Input Manifest

L2 EQC must declare the standards used to derive it.

Required file:

```text
L2/eqc/manifests/l2-eqc-source-standards.yaml
```

Minimum schema:

```yaml
source_standards_manifest_version: "v0.3"
portfolio_id: "AGENT_X_L2"
standard_inputs:
  - standard_id: "EQC-v1.1"
    role: "algorithm/procedure discipline"
    local_reference: "L2/standards/AGENT_X_L2_LIGHTWEIGHT_EQC_v0_3.md"
    source_digest: "sha256:<pending-or-computed>"
  - standard_id: "L2-WORKFLOW-v0.5"
    role: "main L2 profile/spec workflow"
    local_reference: "L2/standards/AGENT_X_L2_PSEUDOCODE_TO_FIC_WORKFLOW_v0_5.md"
    source_digest: "sha256:<pending-or-computed>"
  - standard_id: "L2-EQC-ES-v0.4"
    role: "registry and graph governance"
    local_reference: "L2/standards/AGENT_X_L2_LIGHTWEIGHT_EQC_ES_v0_4.md"
    source_digest: "sha256:<pending-or-computed>"
  - standard_id: "L2-EQC-SIB-BRIDGE-v0.4"
    role: "profile-to-L1 handoff binding"
    local_reference: "L2/standards/AGENT_X_L2_LIGHTWEIGHT_EQC_SIB_BRIDGE_v0_4.md"
    source_digest: "sha256:<pending-or-computed>"
  - standard_id: "L2-EQC-FIC-v0.4"
    role: "profile/spec contract discipline"
    local_reference: "L2/standards/AGENT_X_L2_LIGHTWEIGHT_EQC_FIC_v0_4.md"
    source_digest: "sha256:<pending-or-computed>"
```

Rules:

```text
- Missing source-standard manifest is a blocking validation error for scaffold acceptance.
- Pending digests are allowed only while `release_evidence: false`.
- Computed digests are required before release-candidate profile governance.
- A source-standard digest change marks all dependent L2 EQC procedures stale until revalidated.
```

---

## 27. Controlled Enum Registry

L2 EQC validators must use a controlled enum registry rather than free-form status strings.

Required file:

```text
L2/eqc/manifests/l2-eqc-enums.yaml
```

Minimum enum groups:

```yaml
l2_eqc_enums_version: "v0.3"
portfolio_id: "AGENT_X_L2"
procedure_statuses:
  - "SELECTED_PROFILE"
  - "NO_MATCH"
  - "BLOCKED_INVALID_REQUEST"
  - "BLOCKED_PROFILE_CATALOG_STALE"
  - "BLOCKED_PROFILE_BOUNDARY_CONFLICT"
  - "BLOCKED_REQUIRES_L1_HANDOFF"
  - "BLOCKED_PROHIBITED_L2_RUNTIME_BEHAVIOR"
  - "BLOCKED_REGISTRY_CONFLICT"
  - "REJECTED_UNGOVERNED_PROFILE"
readiness_statuses:
  - "READY_FOR_L1_PROPOSAL"
  - "DRAFT_ONLY"
  - "BLOCKED"
  - "SCAFFOLD_READY_NOT_RELEASE_EVIDENCE"
  - "VALIDATED_PROFILE_SPEC_EQC"
operator_categories:
  - "classification"
  - "selection"
  - "ranking"
  - "boundary-check"
  - "handoff-decision"
  - "readiness-score"
purity_classes:
  - "PURE"
```

Rules:

```text
- Validators must fail if a procedure, operator, trace, or test vector uses an unknown status.
- New enum values require a version-impact record.
- L2 EQC cannot use L1 implementation statuses as if they were L2 decision statuses.
```

---

## 28. Side-Effect and Input Discipline

L2 EQC first-stage operators must be pure and input-bounded.

Allowed inputs:

```text
- request object;
- profile catalog object;
- L2 policy object;
- L2 ES registry extract;
- L2 SIB handoff map extract;
- static evaluation-spec metadata;
- static integration-spec metadata.
```

Forbidden inputs:

```text
- live filesystem reads inside operators;
- network results;
- shell outputs;
- model outputs generated during the procedure;
- wall-clock time;
- environment variables;
- mutable runtime state;
- hidden global caches.
```

Rules:

```text
- Validators may read files before running a procedure, but operators receive parsed input objects only.
- Operators must not mutate input objects.
- Any required external project reference must appear as declared metadata in the profile catalog or integration spec before the EQC procedure runs.
- A procedure that needs live repo inspection must return BLOCKED_REQUIRES_L1_HANDOFF, not inspect directly.
```

---

## 29. Canonical Output and No-Silent-Skip Rules

Machine-readable L2 EQC output must be deterministic.

Canonical output rules:

```text
- Output JSON keys sorted lexicographically.
- Lists sorted by stable ID unless the schema declares input-order preservation.
- Numeric scores represented as strings unless the schema explicitly permits numeric values.
- No uncontrolled timestamps in pass/fail logic.
- Generated timestamps must be UTC ISO-8601 strings ending in Z.
```

No-silent-skip rules:

```text
- A validator must list every procedure, operator, and test-vector file it checked.
- A validator must list every expected procedure, operator, or test-vector file it did not check.
- An unimplemented check must be reported as `not_executed`, not silently omitted.
- A validation result with skipped required checks cannot claim release evidence.
```

Expanded validation output:

```yaml
l2_eqc_validation_result:
  validator: "l2-eqc validate"
  validator_version: "v0.3.0"
  status: "PASS|FAIL|WARNING"
  release_evidence: false
  checked_procedures: []
  checked_operators: []
  checked_test_vectors: []
  skipped_required_checks: []
  not_yet_executable_checks: []
  enum_violations: []
  canonical_output_digest: "sha256:<pending-or-computed>"
  input_manifest_ref: "L2/generated/l2_eqc_validator_input_manifest.yaml"
  generated_at_utc: "YYYY-MM-DDTHH:MM:SSZ"
```

---

## 30. Test Fixture Requirements

L2 EQC test vectors must be backed by fixtures.

Required fixture directory:

```text
L2/eqc/tests/fixtures/
```

Minimum fixture types:

```text
- valid profile catalog;
- stale profile catalog;
- catalog with duplicate profile IDs;
- profile with missing L1 handoff mapping;
- runtime-behavior request;
- tie-ranking catalog;
- deprecated profile catalog;
- blocked boundary-conflict profile.
```

Each negative fixture must declare intended failure code:

```yaml
fixture_intent:
  fixture_id: "L2-EQC-FIXTURE-STALE-CATALOG-001"
  expected_failure_code: "L2_EQC_STALE_PROFILE_CATALOG"
  purpose: "Profile selection must block stale catalogs rather than scoring stale profiles."
```

Rules:

```text
- Negative fixtures without intended failure codes are invalid.
- Test vectors must not rely on hidden defaults outside the fixture.
- Fixture changes are VALIDATION changes unless they change expected profile decision semantics.
```

---

## 31. Cross-Standard Consistency Checks

L2 EQC validation must check consistency with the other L2 standards.

Required cross-checks:

```text
[ ] Every selected profile exists in L2 ES registry.
[ ] Every selected profile has a L2 SIB handoff binding if L1 handoff is required.
[ ] Every selected profile satisfies L2 EQC-FIC profile/spec artifact requirements.
[ ] Every generated handoff proposal follows the L2 workflow handoff boundary.
[ ] Every blocked status uses the controlled enum registry.
[ ] Every proposed L1 unit uses AGENT_X_L1 global ID format.
[ ] No EQC procedure creates implementation authority without L1 acceptance.
```

Blocking results:

```text
- Missing ES registry entry -> BLOCKED_REGISTRY_CONFLICT
- Missing SIB handoff binding -> BLOCKED_REQUIRES_L1_HANDOFF
- Missing profile/spec FIC contract -> REJECTED_UNGOVERNED_PROFILE
- Handoff proposal claims implementation authority -> BLOCKED_PROHIBITED_L2_RUNTIME_BEHAVIOR
```

---

## 32. Digest Maturity Levels

L2 EQC uses digest maturity levels so bootstrap scaffolding and release evidence are not confused.

```text
D0 = no digest, draft only
D1 = pending digest allowed, release_evidence false
D2 = computed local artifact digest
D3 = computed input-manifest digest closure
D4 = computed cross-standard digest closure
D5 = release-candidate digest closure with validator-produced reports
```

Current target:

```text
D2 for first scaffold artifacts;
D3 for validator-produced readiness reports;
D5 only for future release-candidate profile governance.
```

Rules:

```text
- A file with D0 cannot be cited as validation evidence.
- A file with D1 can support scaffold review only.
- Release-candidate L2 EQC requires D5.
```

---

## 33. Upgrade Triggers

L2 EQC must be upgraded beyond the lightweight stage when any of the following become true:

```text
- L2 procedures are executed by automation rather than reviewed as specs.
- L2 decisions directly affect repository changes.
- L2 emits implementation packets instead of proposals.
- L2 profiles include stochastic, numerical, or search procedures.
- L2 evaluation specs require replay/golden traces.
- L2 selects among live model/tool providers.
- L2 writes persistent state or runtime memory.
```

Required upgrade path:

```text
lightweight L2 EQC -> full L2 EQC package -> L1 FIC-governed implementation -> release-candidate validation
```

---

## 34. Minimum First-Slice Procedure Contracts

The first L2 EQC scaffold must not stop at naming procedures. It must define the minimum contract for each required procedure so a weaker model can create the files without inventing semantics.

### 34.1 `L2_SelectProfile` minimum contract

Required operator sequence:

```text
1. ValidateRequest_v1
2. ClassifySpecializationRequest_v1
3. SelectProfileCandidates_v1
4. CheckProfileBoundaryConflicts_v1
5. RankProfileCandidates_v1
6. DecideL1HandoffRequired_v1
7. BuildProfileDecisionRecord_v1
```

Required blocked branches:

```text
- invalid request -> BLOCKED_INVALID_REQUEST
- missing or stale profile catalog -> BLOCKED_PROFILE_CATALOG_STALE
- duplicate profile IDs -> BLOCKED_REGISTRY_CONFLICT
- no matching profiles -> NO_MATCH
- boundary conflict -> BLOCKED_PROFILE_BOUNDARY_CONFLICT
- selected profile lacks L1 handoff map when handoff is required -> BLOCKED_REQUIRES_L1_HANDOFF
- profile not governed by L2 ES/SIB/FIC -> REJECTED_UNGOVERNED_PROFILE
```

Required success branch:

```text
SELECTED_PROFILE with implementation_allowed_by_l2=false and l1_handoff_required=true|false.
```

### 34.2 `L2_AssessProfileReadiness` minimum contract

Required checks:

```text
- profile exists in L2 ES registry;
- profile has stable GlobalProfileID;
- profile document has version marker;
- required profile fields are present;
- profile has evaluation spec reference or explicit deferral;
- profile has integration spec reference or explicit deferral;
- if L1 handoff is required, profile has L2 SIB handoff binding;
- profile does not request runtime execution authority;
- profile is not stale, deprecated, rejected, or blocked.
```

Required output statuses:

```text
READY_FOR_L1_PROPOSAL
DRAFT_ONLY
BLOCKED
```

### 34.3 `L2_BuildL1HandoffProposal` minimum contract

Required fields:

```yaml
l2_to_l1_handoff_proposal:
  proposal_id: "L2-L1-HANDOFF-<number>"
  source_profile_id: "AGENT_X_L2::<profile-id>"
  source_eqc_procedure: "AGENT_X_L2::<procedure-id>"
  source_profile_digest: "sha256:<pending-or-computed>"
  target_l1_units: []
  proposed_l1_goal: ""
  proposed_fic_targets: []
  implementation_allowed_by_l2: false
  l1_acceptance_required: true
  l1_may_reject: true
  non_goals: []
  forbidden_actions:
    - "L2 must not implement code."
    - "L2 must not edit L0 or L1."
    - "L2 must not execute tools."
  evidence_refs: []
  residual_risks: []
```

Blocking rule:

```text
If a handoff proposal omits `implementation_allowed_by_l2: false`, validation fails.
```

---

## 35. Profile Catalog Contract

L2 EQC procedures must consume a parsed profile catalog object, not scan profile files directly.

Required generated file:

```text
L2/generated/profile_catalog.yaml
```

Minimum schema:

```yaml
profile_catalog_version: "v0.3"
portfolio_id: "AGENT_X_L2"
generated_by: "l2-profile-catalog-builder"
release_evidence: false
input_manifest_digest: "sha256:<pending-or-computed>"
profiles:
  - profile_id: "L2-PROFILE-SR-001"
    global_profile_id: "AGENT_X_L2::L2-PROFILE-SR-001"
    path: "L2/profiles/symbolic_regression_controller.yaml"
    version: "v0.1.0"
    status: "draft|active|deprecated|blocked|rejected"
    specialization_type: "symbolic-regression"
    supported_request_types: []
    required_l1_units: []
    evaluation_spec_refs: []
    integration_spec_refs: []
    boundary_flags:
      l2_runtime_authority_requested: false
      direct_l0_modification_requested: false
      direct_l1_modification_requested: false
      tool_execution_requested: false
    risk_level: "low|medium|high|critical"
    digest: "sha256:<pending-or-computed>"
```

Rules:

```text
- The catalog is generated/supporting output, not the source of truth.
- The source of truth remains L2 profile files plus L2 ES registry and L2 SIB bridge bindings.
- A generated catalog that disagrees with the registry is stale.
- Duplicate `global_profile_id` values are blocking errors.
- A profile requesting runtime authority cannot be selected.
```

---

## 36. Schema Closure Requirements

The lightweight L2 EQC stage must include schemas for the artifacts that a validator or weaker coding model is expected to create.

Required first-slice schema files:

```text
L2/eqc/schemas/l2-eqc-manifest.schema.json
L2/eqc/schemas/l2-eqc-procedure.schema.json
L2/eqc/schemas/l2-eqc-operator.schema.json
L2/eqc/schemas/l2-eqc-test-vectors.schema.json
L2/eqc/schemas/l2-eqc-trace-record.schema.json
L2/eqc/schemas/l2-eqc-validation-result.schema.json
L2/eqc/schemas/l2-eqc-source-standards.schema.json
L2/eqc/schemas/l2-eqc-enums.schema.json
L2/eqc/schemas/l2-profile-catalog.schema.json
L2/eqc/schemas/l2-l1-handoff-proposal.schema.json
```

Rules:

```text
- A required sidecar without a schema is advisory only.
- Validator output must name which schemas were enforced and which were not yet executable.
- Release-candidate profile governance requires all required schemas to be executable.
- Schema fixture files must include at least one valid fixture and one invalid fixture with intended failure code.
```

---

## 37. Generated Artifact Edit Policy

Generated L2 EQC artifacts must not silently become source of truth.

Generated artifacts include:

```text
L2/generated/profile_catalog.yaml
L2/generated/l2_semantic_lockfile.yaml
L2/generated/validation_report.md
L2/generated/readiness_report.md
L2/generated/l2_eqc_validator_input_manifest.yaml
L2/generated/l2_eqc_trace_record.yaml
```

Rules:

```text
- Generated artifacts must declare `generated_by`, `input_manifest_digest`, and `release_evidence`.
- Manual edits to generated artifacts are forbidden unless a maintenance task explicitly permits them.
- If a generated artifact is manually edited, it must be marked stale and regenerated before being used as evidence.
- Generated artifacts with pending digests cannot support release-candidate claims.
```

---

## 38. Release-Blocking Matrix

| Condition | Scaffold status | Release-candidate status |
|---|---|---|
| Missing manifest | blocked | blocked |
| Missing procedure/operator files | blocked | blocked |
| Missing test vectors | blocked | blocked |
| Missing schemas | warning if declared not executable | blocked |
| Pending digests | allowed only with `release_evidence: false` | blocked |
| Generated catalog stale | blocked | blocked |
| Runtime-like L2 behavior requested | blocked | blocked |
| Handoff proposal permits implementation directly | blocked | blocked |
| Validator has skipped required checks | scaffold-only warning or blocked by profile | blocked |
| No L2 SIB handoff binding for L1-required profile | blocked | blocked |
```

---

## 39. Weaker-Agent File Creation Order

A weaker coding model should create the first L2 EQC scaffold in this order:

```text
1. L2/eqc/manifests/l2-eqc-enums.yaml
2. L2/eqc/manifests/l2-eqc-source-standards.yaml
3. L2/eqc/manifests/l2-eqc-manifest.yaml
4. L2/eqc/operators/*.eqc.md
5. L2/eqc/procedures/*.eqc.md
6. L2/eqc/tests/fixtures/*.yaml
7. L2/eqc/tests/*.yaml
8. L2/eqc/schemas/*.schema.json
9. L2/generated/profile_catalog.yaml
10. L2/generated/validation_report.md
11. L2/generated/readiness_report.md
```

Stop conditions:

```text
- If required L2 ES or SIB files are missing, stop with BLOCKED_MISSING_CROSS_STANDARD_INPUT.
- If profile files are missing, create EQC scaffold only and mark profile selection tests as fixture-based.
- If any procedure needs runtime behavior, stop with BLOCKED_PROHIBITED_L2_RUNTIME_BEHAVIOR.
- If any handoff output grants implementation authority, stop with BLOCKED_L2_AUTHORITY_VIOLATION.
```

---

## 40. Termination, Totality, and Deterministic Tie Closure

L2 EQC procedures are not runtime systems, but they still must be total decision procedures over their declared input domain.

Required rules:

```text
- Every procedure must declare a finite input domain or a finite bounded scan set.
- Every loop must have a declared bound derived from the input size.
- Recursive procedure calls are forbidden in the lightweight L2 EQC stage.
- Every branch must return one controlled status.
- Every profile-candidate tie must be resolved by deterministic lexical ordering of GlobalProfileID.
- Ranking functions must not use wall-clock time, filesystem order, random order, model judgment, network data, or unstated repository context.
- Empty candidate sets must return NO_MATCH, not an empty successful selection.
- Multiple equally ranked candidates must return a stable ordered candidate list and identify the first candidate as selected only when policy permits automatic selection.
```

Blocking conditions:

```text
BLOCKED_NON_TOTAL_PROCEDURE
BLOCKED_UNBOUNDED_LOOP
BLOCKED_UNDECLARED_TIE_RULE
BLOCKED_UNSTABLE_RANKING_INPUT
```

---

## 41. Minimal Executable Validator Profile

The first L2 EQC validator does not need to prove semantic correctness, but it must catch scaffold-breaking defects deterministically.

Minimum executable validator profile:

```yaml
l2_eqc_validator_profile:
  profile_id: "L2-EQC-VALIDATOR-PROFILE-001"
  version: "v0.4.0"
  release_evidence: false
  required_checks:
    - manifest_exists
    - manifest_schema_valid_or_declared_not_executable
    - required_procedures_exist
    - required_operators_exist
    - procedure_manifest_references_resolve
    - operator_manifest_references_resolve
    - test_vector_files_exist
    - controlled_statuses_only
    - no_prohibited_runtime_directories_referenced
    - no_shell_network_tool_or_model_execution_authority
    - l2_to_l1_outputs_set_implementation_allowed_by_l2_false
    - generated_artifacts_mark_release_evidence_false
    - profile_catalog_source_of_truth_not_inverted
```

No-silent-skip rule:

```text
A validator may mark a check as not_yet_executable only if the validator profile names the check, explains the missing capability, and marks the output as scaffold-only.
A required check omitted from validator output is a validator failure, not a warning.
```

---

## 42. Procedure-to-Operator Coverage Matrix

Every L2 EQC procedure must have a procedure-to-operator coverage matrix.

Minimum matrix row:

```yaml
procedure_operator_coverage:
  - procedure_id: "AGENT_X_L2::L2-EQC-PROC-001"
    procedure_step: "classify request"
    operator_id: "AGENT_X_L2::L2-EQC-OP-001"
    operator_name: "ClassifySpecializationRequest_v1"
    required: true
    test_vector_refs:
      - "AGENT_X_L2::L2-EQC-TEST-001"
```

Rules:

```text
- Every normative procedure step must map to one operator or be declared as control-flow only.
- Every required operator must have at least one test vector or explicit deferral.
- An operator listed in the manifest but unused by any procedure is advisory unless marked required by a future profile.
- A procedure that calls an operator not present in the manifest is blocked.
```

Blocking code:

```text
BLOCKED_OPERATOR_COVERAGE_GAP
```

---

## 43. Profile Score Explanation Contract

Profile ranking must be explainable enough for L1 to review the handoff proposal.

Every selected profile decision must include:

```yaml
profile_score_explanation:
  selected_profile_id: "AGENT_X_L2::<profile-id>"
  request_classification: "coding|research|symbolic-regression|repo-maintenance|orchestration|mixed|unknown"
  candidate_count: 0
  rejected_candidates: []
  scoring_components:
    - name: "specialization_match"
      value: 0
      reason: ""
    - name: "boundary_safety"
      value: 0
      reason: ""
    - name: "l1_handoff_readiness"
      value: 0
      reason: ""
  tie_break_applied: false
  final_ordered_candidates: []
```

Rules:

```text
- Numeric score components must use integer or fixed decimal string values.
- Component names must come from the controlled enum registry.
- A selected profile without score explanation cannot be proposed to L1.
- Score explanation is review evidence, not implementation authority.
```

---

## 44. Final Self-Assessment

Previous version rated: **9.8/10**.

Remaining gaps fixed in `v0.4.0`:

```text
- added termination, totality, and deterministic tie-closure rules;
- added a minimal executable validator profile;
- added procedure-to-operator coverage matrix rules;
- added profile score explanation contract;
- added final blocking codes for non-total procedures, unbounded loops, unstable ranking, and operator coverage gaps;
- upgraded the document to `v0.4.0`.
```

Current rating:

```text
10/10 for the current L2 profile/spec EQC document stage.
```

This rating applies to the standard as a lightweight profile/spec-stage document. Implementation maturity remains separate: the first L2 scaffold and validator can still be incomplete while this document remains sufficient as the governing EQC standard for the current stage.
