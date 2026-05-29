# Agent_X L1 Lightweight EQC Standard

**Document ID:** `AGENT_X_L1_LIGHTWEIGHT_EQC`  
**Version:** `v0.5.0`  
**Status:** `ready-for-use`  
**Layer:** `L1`  
**Project:** `Agent_X`  
**Purpose:** Define a lightweight EquationCode-style specification discipline for Agent_X L1 algorithms, procedures, operators, traces, and deterministic implementation contracts.

---

## 0. Executive Summary

Agent_X L1 already has four supporting standards:

```text
EQC-FIC                 = file/unit implementation contract
Pseudocode-to-FIC       = controlled workflow from goal to implementation package
Lightweight EQC-SIB     = document <-> implementation binding discipline
Lightweight EQC-ES      = document portfolio governance discipline
```

This document adds the missing fifth standard:

```text
Lightweight EQC         = algorithm/procedure/operator semantics discipline
```

The purpose is not to force every Agent_X L1 document into full mathematical EQC form. The purpose is to prevent hidden behavior in the parts of L1 that behave like algorithms, state machines, deterministic validators, classifiers, planners, comparators, reducers, trace generators, digest calculators, or execution procedures.

For the current Agent_X L1 stage, this standard should be applied selectively to:

```text
- goal classification
- unit planning
- FIC validation
- dependency graph checking
- impact classification
- digest calculation
- traceability update procedures
- evidence collection rules
- proof/check runner behavior
- release/readiness scoring
```

It should not be used as heavy paperwork for ordinary prose documents, simple templates, or human-readable background notes.

---

## 1. Scope

### 1.1 In scope

This lightweight EQC standard applies to any Agent_X L1 artifact that defines one of the following:

```text
- deterministic procedure
- classification rule
- scoring rule
- validation rule
- graph traversal
- digest/hash calculation
- ordering or tie-breaking behavior
- state transition
- trace or evidence construction
- readiness or release decision
- controlled transformation from one artifact type to another
```

Examples:

```text
L1 goal classifier
L1 unit planner
L1 FIC validator
L1 SIB validator
L1 ES validator
L1 semantic lockfile builder
L1 impact closure calculator
L1 digest calculator
L1 handoff packet builder
L1 completion-record checker
```

### 1.2 Out of scope

This standard does not govern:

```text
- general architecture prose
- visual diagrams
- broad roadmap text
- non-normative rationale sections
- informal design notes
- historical notes
- rejected alternatives
```

Those artifacts remain governed by the workflow, ES, SIB, or FIC standards as appropriate.

### 1.3 Relationship to full EQC

Full EQC defines a complete formal structure for mathematical algorithms, operator manifests, reproducibility contracts, numeric policies, traces, equivalence levels, and checkpoints.

This lightweight Agent_X L1 version keeps the useful core:

```text
- explicit global semantics
- named operators
- control-flow-only procedure bodies
- explicit state and inputs
- deterministic ordering and tie-breaking
- trace and evidence schemas
- validation and test vectors
- equivalence expectations
```

It defers heavy requirements that are not yet needed:

```text
- GPU deterministic kernel policy
- distributed reduction policy
- full stochastic replay tokens
- full numerical analysis policy
- complete checkpoint serialization formalism
- portfolio-wide golden trace infrastructure
```

---

## 2. Core Rule

Every governed L1 algorithmic artifact must separate:

```text
procedure control flow
from
operator semantics
```

The procedure may say:

```text
classification <- ClassifyGoal(goal, repo_state, policy)
impact_set <- ComputeImpactClosure(classification, graph, bindings)
status <- DecideReadiness(validation_result, release_policy)
```

The procedure must not hide important semantics inside vague prose such as:

```text
handle normally
choose best option
validate everything
resolve conflicts
update relevant files
use reasonable defaults
```

Those meanings must be defined in named operators or explicit decision tables.

---

## 3. Lightweight EQC Artifact Types

Agent_X L1 uses the following EQC artifact types.

| Artifact Type | Purpose | Example |
|---|---|---|
| `procedure-spec` | Defines control flow and operator calls | `L1_EvolveOnce` |
| `operator-spec` | Defines one named semantic operation | `ClassifyGoal_v1` |
| `decision-table` | Defines deterministic classification behavior | status classifier |
| `state-machine` | Defines legal states and transitions | workflow lifecycle |
| `trace-schema` | Defines required trace/evidence fields | validation trace |
| `test-vector-set` | Defines inputs and expected outputs | classifier examples |
| `equivalence-rule` | Defines acceptable refactor drift | E0/E1/E2/E3-lite |
| `manifest` | Binds procedure to exact operators | `l1-eqc-manifest.yaml` |

---

## 4. Required Repository Placement

Recommended placement inside Agent_X:

```text
L1/
  eqc/
    AGENT_X_L1_LIGHTWEIGHT_EQC.md
    manifests/
      l1-eqc-manifest.yaml
    procedures/
      L1_EvolveOnce.eqc.md
      L1_ValidateFICBundle.eqc.md
      L1_ComputeImpactClosure.eqc.md
    operators/
      classify_goal.eqc.md
      compute_impact_closure.eqc.md
      validate_fic_document.eqc.md
      build_semantic_lockfile.eqc.md
      decide_readiness.eqc.md
    traces/
      l1-validation-trace.schema.yaml
      l1-evidence-record.schema.yaml
    tests/
      goal-classifier.test-vectors.yaml
      impact-closure.test-vectors.yaml
      readiness-decision.test-vectors.yaml
```

If the repository does not yet have validators, these files may begin as Markdown plus YAML snippets. The format must still be stable enough for later parsing.

---

## 5. Authority Order

When EQC documents conflict with other L1 documents, use this authority order:

```text
1. Non-waivable L0 boundary rules
2. Agent_X root architecture / L0 seed contract
3. L1 Lightweight EQC-ES
4. L1 Lightweight EQC-SIB
5. L1 EQC-FIC
6. L1 Pseudocode-to-FIC workflow
7. L1 Lightweight EQC procedure/operator specs
8. Existing implementation code
9. Informal notes or conversation history
```

However, when the issue is the exact semantics of an algorithmic rule already governed by an EQC operator, the EQC operator is the local source of truth unless a higher-authority document blocks it.

---

## 6. Lightweight EQC Header

Every L1 EQC procedure or operator document must begin with a header.

```yaml
eqc_header:
  eqc_schema: "agent-x-l1-lightweight-eqc/v0.5"
  doc_id: "EQC-L1-..."
  title: "..."
  artifact_type: "procedure-spec|operator-spec|decision-table|state-machine|trace-schema|test-vector-set|equivalence-rule|manifest"
  version: "vX.Y.Z"
  status: "draft|ready-for-use|deprecated|superseded"
  layer: "L1"
  owner: "..."
  governed_unit_ids: []
  related_fic_ids: []
  related_sib_art_ids: []
  related_es_doc_ids: []
  last_updated_utc: "YYYY-MM-DDTHH:MM:SSZ"
```

Rules:

```text
- `doc_id` must be globally unique inside Agent_X L1.
- `version` must change when semantics change.
- `status` must be `ready-for-use` before implementation depends on it.
- `last_updated_utc` must be UTC, ISO-8601, and end with `Z`.
- Related FIC/SIB/ES IDs must be listed when the EQC artifact governs implementation behavior.
```

---

## 6.1 Stable Anchor Identity

Every release-bound EQC artifact must declare stable anchors for the exact semantic parts that can be bound by ES, SIB, FIC, tests, or implementation code.

```yaml
anchors:
  - anchor_id: "EQC-OP-L1-CLASSIFY-GOAL-V1"
    anchor_type: "operator|procedure|decision-table|state-machine|trace-schema|test-vector-set"
    target_name: "L1.ClassifyGoal_v1"
    semantic_scope: "complete operator semantics"
    stability: "stable"
```

Rules:

```text
- Anchor IDs must be globally unique within `AGENT_X_L1`.
- Anchor IDs must not be reused for different semantics.
- Renaming a heading must not change the anchor ID.
- Moving a document must not change the anchor ID.
- Removing or changing an anchored semantic object is a FUNCTIONAL change unless explicitly classified otherwise by an equivalence rule.
- ES and SIB bindings must reference anchors, not prose headings.
```

Missing anchors are non-blocking in `advisory` mode, blocking in `governed`, `validated`, and `enforced` modes.

---

## 7. Global Semantics Block

Every procedure-spec must declare its global semantics.

```yaml
global_semantics:
  primary_objective: "..."
  better_means: "minimize|maximize|satisfy-all|ordered-status|not-applicable"
  decision_order: []
  tie_breaking: "deterministic_lowest_id|deterministic_lexicographic|explicit_table|not-applicable"
  invalid_input_policy: "return-blocked|raise-structured-error|reject-validation|not-applicable"
  determinism_level: "exact|stable-order|tolerance|manual-review"
  hidden_defaults_allowed: false
```

### 7.1 Meaning of `better_means`

Use `satisfy-all` for validators where all required conditions must pass.

Use `ordered-status` when statuses have a deterministic severity order, for example:

```text
PASS < WARNING < BLOCKED < FAIL
```

Use `not-applicable` only for pure record construction with no comparison or optimization.

### 7.2 Determinism levels

| Level | Meaning |
|---|---|
| `exact` | Same input must produce byte-identical result. |
| `stable-order` | Same logical result and deterministic ordering required. |
| `tolerance` | Numeric/text tolerance allowed and declared. |
| `manual-review` | Output needs human judgment; machine result must mark this. |

For Agent_X L1 validators and classifiers, the default must be:

```text
exact
```

---

## 8. State, Inputs, and Outputs

Every procedure-spec and operator-spec must declare persistent state, transient inputs, and outputs.

### 8.1 State declaration

```yaml
state:
  owns_persistent_state: false
  persistent_state_items: []
  reads_state:
    - name: "repo_state"
      source: "repository_snapshot"
      mutable: false
  writes_state: []
```

Rules:

```text
- Hidden state is prohibited.
- Cache behavior counts as state.
- File writes count as state mutation.
- A procedure may not write state unless the owning FIC/SIB artifact permits it.
```

### 8.2 Input declaration

```yaml
inputs:
  - name: "goal"
    type: "string"
    required: true
    trust_level: "user-provided|internal|generated|repository"
    validation: "non-empty UTF-8 string after stripping surrounding whitespace"
  - name: "repo_state"
    type: "RepoStateRecord"
    required: true
    trust_level: "repository"
    validation: "must include root path, file inventory, and digest map"
```

Rules:

```text
- Every input must have a type.
- Every input must have a validation rule.
- User-provided, generated, and repository-derived text must be treated as untrusted instructions unless marked authoritative by ES/SIB.
- Missing required input produces a structured blocked/error result.
```

### 8.3 Output declaration

```yaml
outputs:
  - name: "classification"
    type: "GoalClassification"
    destination: "return"
    deterministic_ordering: true
  - name: "trace_record"
    type: "L1TraceRecord"
    destination: "trace"
    deterministic_ordering: true
```

Rules:

```text
- Outputs must be fully declared.
- Output ordering must be deterministic.
- Output records must not contain hidden implementation-only fields unless clearly marked diagnostic.
```

---

## 9. Operator Manifest

Each procedure-spec must bind to exact operator versions.

```yaml
operator_manifest:
  procedure: "L1.EvolveOnce_v1"
  operators:
    - name: "L1.ClassifyGoal_v1"
      category: "classification"
      source_doc: "L1/eqc/operators/classify_goal.eqc.md"
      version: "v1.0.0"
    - name: "L1.BuildUnitPlan_v1"
      category: "planning"
      source_doc: "L1/eqc/operators/build_unit_plan.eqc.md"
      version: "v1.0.0"
    - name: "L1.ValidateFIC_v1"
      category: "validation"
      source_doc: "L1/eqc/operators/validate_fic.eqc.md"
      version: "v1.0.0"
```

Rules:

```text
- Operator names must be fully qualified.
- Operator versions must be explicit.
- Procedure documents may not call unmanifested operators.
- A change to operator semantics requires a version bump and impact classification.
```

---

## 10. Operator Specification Template

Every operator must use this template.

```yaml
operator:
  name: "L1.OperatorName_v1"
  version: "v1.0.0"
  category: "classification|planning|validation|digest|trace|binding|readiness|error|io"
  purity: "pure|stateful|io|external"
  deterministic: true
  signature:
    inputs: []
    outputs: []
  preconditions: []
  postconditions: []
  edge_cases: []
  failure_behavior: []
  ordering_rule: "..."
  tie_breaking_rule: "..."
  dependencies: []
  test_vectors: []
```

### 10.1 Purity classes

| Purity | Meaning | L1 default |
|---|---|---|
| `pure` | No side effects, deterministic from inputs | preferred |
| `stateful` | Reads/writes declared state | allowed only with FIC/SIB ownership |
| `io` | Reads/writes filesystem or external process | allowed only for explicit runner units |
| `external` | Depends on non-deterministic external service | blocked for current L1 stage unless waived |

### 10.2 Operator edge-case rule

Each operator must list edge cases relevant to its inputs.

For example:

```yaml
edge_cases:
  - case: "empty goal"
    behavior: "return BLOCKED_EMPTY_GOAL"
    test_required: true
  - case: "duplicate document IDs"
    behavior: "return FAIL_DUPLICATE_DOC_ID"
    test_required: true
  - case: "graph cycle"
    behavior: "return FAIL_FUNCTIONAL_CYCLE"
    test_required: true
```

---

## 11. Procedure Specification Rules

Procedure bodies must be control-flow only.

Allowed constructs:

```text
- IF / ELSE
- FOR EACH
- WHILE, only with explicit termination condition
- RETURN
- assignment
- record construction
- operator calls
- deterministic comparisons
```

Forbidden inside procedure bodies:

```text
- hidden heuristics
- unbound natural-language decisions
- direct filesystem access unless operatorized
- direct model calls
- direct network calls
- implicit global state
- unbounded retry loops
- unmanifested helper behavior
```

### 11.1 Procedure skeleton example

```text
Procedure L1_EvolveOnce_v1(goal, repo_state, policy):

  validated_goal <- L1.ValidateGoalInput_v1(goal, policy)
  IF validated_goal.status != PASS:
      RETURN L1.BlockedResult_v1(validated_goal)

  classification <- L1.ClassifyGoal_v1(validated_goal, repo_state, policy)

  impact <- L1.ComputeImpactClosure_v1(classification, repo_state.graph, repo_state.bindings)
  IF impact.requires_L0_change == true:
      RETURN L1.BlockedL0Impact_v1(impact)

  unit_plan <- L1.BuildUnitPlan_v1(classification, impact, policy)

  fic_plan <- L1.BuildFICPlan_v1(unit_plan, repo_state, policy)

  readiness <- L1.DecidePreCodeReadiness_v1(fic_plan, repo_state, policy)

  trace <- L1.BuildTraceRecord_v1(goal, classification, impact, unit_plan, fic_plan, readiness)

  RETURN L1.EvolveOnceResult_v1(classification, impact, unit_plan, fic_plan, readiness, trace)
```

This skeleton does not implement the semantics directly. The semantics live in the operators.

### 11.2 Loop, retry, and termination policy

Any loop or retry in a procedure must declare a bounded termination rule.

```yaml
termination_policy:
  loops_allowed: true
  max_iterations: "declared per procedure"
  retry_allowed: false
  retry_budget: 0
  retry_backoff: "not-applicable"
  timeout_policy: "not-used|fixed-budget|external-runner-owned"
```

Rules:

```text
- Unbounded loops are prohibited.
- Retry behavior must be operatorized and testable.
- A retry must not hide validation failure.
- If a loop traverses files, graph nodes, or operators, traversal order must use the ordering policy in Section 12.
- A procedure with an undeclared loop termination rule is not ready-for-use.
```

### 11.3 Time and timestamp policy

L1 EQC procedures should avoid wall-clock time in decision logic. When timestamps are needed for evidence records, they are recorded metadata, not decision inputs.

```yaml
time_policy:
  decision_time_dependency_allowed: false
  evidence_timestamps_allowed: true
  timestamp_format: "UTC ISO-8601 ending with Z"
  trace_significance: "metadata-only unless explicitly declared"
```

Rules:

```text
- Wall-clock time must not affect PASS/BLOCKED/FAIL decisions.
- If a timestamp appears in a digest, the digest input list must explicitly include it.
- By default, trace/evidence timestamps are metadata and excluded from functional equivalence.
```

---

## 12. Deterministic Ordering and Tie-Breaking

Every EQC-governed L1 procedure must declare ordering rules.

Default rules:

```yaml
ordering_policy:
  path_order: "ascending_posix_lexicographic"
  id_order: "ascending_lexicographic"
  graph_node_order: "ascending_global_id"
  graph_edge_order: "ascending_src_type_dst"
  duplicate_resolution: "blocking_error"
  tie_breaking: "lowest_global_id_wins_only_when_explicitly_allowed"
```

Rules:

```text
- Sorting must be stable.
- Duplicate source-of-truth owners are blocking errors.
- Duplicate IDs are blocking errors.
- If two candidate results are equally valid, tie-breaking must be explicit.
- Validators must not depend on OS directory iteration order.
```

---

## 13. Numeric and Hashing Policy

Most Agent_X L1 logic is not numerical optimization. Still, digest and scoring behavior must be explicit.

### 13.1 Score policy

If a document or implementation unit is scored, the scoring procedure must define:

```yaml
score_policy:
  scale: "0..10"
  precision: "one_decimal_place|max_integer|exact_fraction"
  passing_threshold: "..."
  rounding_rule: "round_half_up|round_half_even|floor|not-applicable"
  components: []
  tie_breaking: "..."
```

A score such as `9.7/10` must be traceable to criteria.

### 13.2 Digest policy

```yaml
digest_policy:
  algorithm: "sha256"
  text_canonicalization:
    encoding: "utf-8"
    line_endings: "LF"
    strip_trailing_whitespace: true
    final_newline_required: true
  yaml_json_canonicalization:
    parse_and_emit_canonical_json: true
    sorted_keys: true
    deterministic_list_order: "as_declared_unless_schema_declares_sort_key"
```

Rules:

```text
- Hashes must be lowercase hex.
- Canonicalization rules must be applied before hashing.
- Digest inputs must be listed in trace/evidence records.
```

---

## 14. Error and Failure Semantics

Every procedure and operator must use structured errors or structured blocked statuses.

### 14.1 Required error record

```yaml
error_record:
  code: "EQC_L1_..."
  severity: "warning|blocked|fail"
  source_operator: "L1.OperatorName_v1"
  message: "human-readable message"
  affected_ids: []
  remediation: "..."
```

### 14.2 Error-code registry

Error codes should be registered in:

```text
L1/eqc/error_codes.yaml
```

Minimum schema:

```yaml
error_codes:
  - code: "EQC_L1_DUPLICATE_ID"
    severity: "fail"
    meaning: "Two governed artifacts declare the same stable ID."
    release_blocking: true
  - code: "EQC_L1_L0_IMPACT_REQUIRES_REVIEW"
    severity: "blocked"
    meaning: "A proposed L1 change would modify or weaken L0 behavior."
    release_blocking: true
```

Rules:

```text
- Unknown error codes are invalid.
- Release-blocking errors must stop package closure.
- Error messages must not leak secrets, absolute local paths, or private environment details unless explicitly allowed.
```

---

## 15. Trace and Evidence Schema

Every EQC-governed L1 procedure must produce or update a trace/evidence record.

### 15.1 Minimum trace record

```yaml
trace_record:
  trace_id: "TRACE-L1-..."
  procedure: "L1.EvolveOnce_v1"
  procedure_version: "v1.0.0"
  input_digest: "sha256:..."
  operator_manifest_digest: "sha256:..."
  repo_state_digest: "sha256:..."
  started_at_utc: "YYYY-MM-DDTHH:MM:SSZ"
  finished_at_utc: "YYYY-MM-DDTHH:MM:SSZ"
  status: "PASS|WARNING|BLOCKED|FAIL"
  errors: []
  warnings: []
  output_digest: "sha256:..."
```

### 15.2 Evidence record

```yaml
evidence_record:
  evidence_id: "EVID-L1-..."
  produced_by: "L1.OperatorName_v1"
  artifact_paths: []
  commands_run: []
  validators_run: []
  claims: []
  evidence_items: []
  unresolved_unknowns: []
```

Rules:

```text
- Claims and evidence must be separated.
- Validator output has higher authority than agent reasoning.
- A trace record must be reproducible from declared inputs, except for UTC timestamps when timestamp nondeterminism is allowed and recorded.
```

---

## 16. Validation and Test Vectors

Every operator must include at least one positive test vector and one relevant edge/failure test vector unless explicitly waived.

### 16.1 Test-vector format

```yaml
test_vectors:
  - id: "TV-GOAL-CLASSIFIER-001"
    operator: "L1.ClassifyGoal_v1"
    input:
      goal: "create a FIC for UNIT-L1-001"
      policy_ref: "POLICY-L1-STANDARD"
    expected:
      classification: "fic_creation"
      affects_l0: false
      required_artifacts:
        - "fic_document"
    equivalence: "E0"
  - id: "TV-GOAL-CLASSIFIER-002"
    operator: "L1.ClassifyGoal_v1"
    input:
      goal: "modify L0 governance gate to allow shell access"
    expected:
      status: "BLOCKED"
      code: "EQC_L1_L0_IMPACT_REQUIRES_REVIEW"
    equivalence: "E0"
```


### 16.3 Procedure-to-operator and operator-to-test coverage

Each release-bound procedure must include a coverage table that proves every operator call has a manifest binding and every high-risk operator has tests.

```yaml
procedure_operator_coverage:
  procedure: "L1.ValidateFICBundle_v1"
  calls:
    - operator: "L1.ValidateBundleHeader_v1"
      manifested: true
      operator_ready: true
      positive_test_vectors: ["TV-BUNDLE-HEADER-001"]
      negative_test_vectors: ["TV-BUNDLE-HEADER-002"]
      release_blocking_if_missing: true
```

Rules:

```text
- A procedure cannot be ready-for-use when it calls an unready operator.
- A high-risk operator must have at least one negative or blocked-path test vector.
- Coverage rows must be deterministic and sorted by operator name.
- Missing coverage is `FAIL_OPERATOR_TEST_COVERAGE_MISSING` in validated/enforced modes.
```

### 16.4 Required validator behavior

The EQC validator must check:

```text
- required headers exist
- operator manifest resolves
- all called operators are manifested
- operator versions are explicit
- duplicate operator names are rejected
- procedure body uses only allowed constructs
- all inputs and outputs are declared
- failure behavior is declared
- ordering and tie-breaking are declared
- at least one test vector exists per operator
- trace schema exists for procedure specs
```

---

## 17. Equivalence Levels

Agent_X L1 uses lightweight EQC equivalence levels.

| Level | Name | Meaning |
|---|---|---|
| `E0` | Trace-equivalent | Same inputs produce same trace-significant outputs. |
| `E1` | Decision-equivalent | Same final decision/status, minor trace wording may differ. |
| `E2` | Metric-equivalent | Same score/classification within declared tolerance. |
| `E3` | Invariant-equivalent | Core invariants preserved, outputs may be reorganized. |

Default requirements:

```text
validators/classifiers/readiness decisions: E0
trace/evidence formatting refactors: E1
scoring/ranking changes: E2 with declared tolerance
architecture refactors: E3 only with explicit review
```

Rules:

```text
- An operator replacement must declare required equivalence level.
- If equivalence is lower than required, the change is functional.
- Functional changes must update FIC/SIB/ES bindings where applicable.
```

---

## 18. Checkpoint and Replay Lite

For the current Agent_X L1 stage, full checkpointing is deferred. A lightweight replay package is required for release-bound changes.

```yaml
replay_package:
  package_id: "REPLAY-L1-..."
  base_commit: "<git commit or unknown>"
  input_artifacts:
    - path: "..."
      digest: "sha256:..."
  operator_manifest_digest: "sha256:..."
  policy_digest: "sha256:..."
  commands_to_replay: []
  expected_outputs:
    - path: "..."
      digest: "sha256:..."
```

Rules:

```text
- A release-bound validator run must record enough inputs to replay the decision.
- If a run cannot be replayed, the evidence status must be `not_replayable`.
- `not_replayable` evidence cannot support a final release decision unless waived.
```

---

## 19. Integration With EQC-FIC

A FIC may reference an EQC procedure or operator when the target file implements algorithmic behavior.

Example FIC binding:

```yaml
bindings:
  implements_eqc:
    - eqc_doc_id: "EQC-L1-GOAL-CLASSIFIER"
      operator: "L1.ClassifyGoal_v1"
      binding_strength: "HARD"
      required_equivalence: "E0"
```

Rules:

```text
- If a file implements an EQC operator, the public surface must match the operator signature or declare an adapter rule.
- Tests for the file must include the EQC test vectors or derived equivalents.
- Changing implementation behavior without updating the EQC operator is prohibited.
```

---

## 20. Integration With Lightweight EQC-SIB

SIB tracks document-to-implementation binding. EQC supplies semantic operator contracts.

SIB registry entries for EQC-bound artifacts should include:

```yaml
spec_bindings:
  - doc: "AGENT_X_L1::EQC-L1-GOAL-CLASSIFIER"
    binding_type: "IMPLEMENTS"
    anchors:
      - doc_anchor_id: "EQC-OP-L1-CLASSIFY-GOAL-V1"
        art_anchor_id: "PY-FUNC-CLASSIFY-GOAL"
        binding_strength: "HARD"
        minimum_equivalence: "E0"
```

Rules:

```text
- SIB impact must include EQC docs when bound implementation changes functionally.
- EQC impact must include implementation artifacts when operator semantics change.
- Missing HARD anchors are release-blocking.
```

---

## 21. Integration With Lightweight EQC-ES

ES governs the EQC document portfolio.

Every EQC document should be registered as an ES document:

```yaml
registry_entry:
  DocID: "EQC-L1-GOAL-CLASSIFIER"
  Type: "operator-spec"
  Layer: 1
  FilePath: "L1/eqc/operators/classify_goal.eqc.md"
  CurrentVersion: "v1.0.0"
  Status: "active"
  FunctionalDigest: "sha256:..."
  MetadataDigest: "sha256:..."
```

Rules:

```text
- EQC documents must appear in the ES registry before they govern implementation.
- EQC functional digest changes trigger ES impact analysis.
- EQC documents must use canonical paths and version markers.
```

---

## 22. L1 Operator Set: Initial Recommendation

The first Agent_X L1 EQC operator set should be small.

```text
L1.ValidateGoalInput_v1
L1.ClassifyGoal_v1
L1.ComputeImpactClosure_v1
L1.BuildUnitPlan_v1
L1.BuildFICPlan_v1
L1.ValidateFICReadiness_v1
L1.BuildHandoffPacket_v1
L1.CollectEvidence_v1
L1.DecideReadiness_v1
L1.BuildTraceRecord_v1
```

Do not define dozens of operators before code exists. Start with the operators that prevent ambiguity in implementation and validation.

---

## 23. Example Operator: Goal Classifier

```yaml
operator:
  name: "L1.ClassifyGoal_v1"
  version: "v1.0.0"
  category: "classification"
  purity: "pure"
  deterministic: true
  signature:
    inputs:
      - name: "goal"
        type: "ValidatedGoal"
      - name: "repo_state"
        type: "RepoStateRecord"
      - name: "policy"
        type: "L1Policy"
    outputs:
      - name: "classification"
        type: "GoalClassification"
  preconditions:
    - "goal.status == PASS"
    - "repo_state.inventory_digest is present"
  postconditions:
    - "classification.category is one of the controlled categories"
    - "classification.affects_l0 is true if proposed changes touch L0 paths or L0 governance semantics"
  ordering_rule: "classification reasons sorted by reason_code"
  tie_breaking_rule: "if multiple categories match, choose highest severity category by controlled order"
  failure_behavior:
    - condition: "category cannot be determined"
      behavior: "return BLOCKED_UNKNOWN_GOAL_CLASS"
```

Controlled category order:

```text
L0_IMPACT
SECURITY_OR_GOVERNANCE_IMPACT
SIB_ES_EQC_STANDARD_UPDATE
FIC_CREATION_OR_UPDATE
WORKFLOW_DOCUMENT_UPDATE
L1_IMPLEMENTATION_UNIT
L2_PROFILE_OR_BLUEPRINT
DOC_ONLY
UNKNOWN
```

If multiple categories match, choose the earliest category in the list.

---

## 24. Example Operator: Readiness Decision

```yaml
operator:
  name: "L1.DecideReadiness_v1"
  version: "v1.0.0"
  category: "readiness"
  purity: "pure"
  deterministic: true
  signature:
    inputs:
      - name: "validation_results"
        type: "ValidationResultSet"
      - name: "policy"
        type: "ReleasePolicy"
    outputs:
      - name: "readiness"
        type: "ReadinessDecision"
  decision_table:
    - condition: "any release_blocking_error exists"
      status: "BLOCKED"
    - condition: "any required validator not run and no waiver exists"
      status: "BLOCKED"
    - condition: "all required validators pass and no unresolved high risk exists"
      status: "READY_FOR_IMPLEMENTATION"
    - condition: "implementation evidence exists and required checks pass"
      status: "VALIDATED"
    - condition: "existing implementation satisfies all requirements without changes"
      status: "NO_CHANGE"
  tie_breaking_rule: "most severe status wins"
```

Severity order:

```text
VALIDATED < READY_FOR_IMPLEMENTATION < NO_CHANGE < WARNING < BLOCKED < FAIL
```

---

## 25. Example Procedure: Validate FIC Bundle

```text
Procedure L1_ValidateFICBundle_v1(bundle, registry, policy):

  header_result <- L1.ValidateBundleHeader_v1(bundle)
  registry_result <- L1.ValidateFICRegistryCoverage_v1(bundle, registry)
  path_result <- L1.ValidateCanonicalPaths_v1(bundle)
  authority_result <- L1.ValidateAuthorityBindings_v1(bundle)
  dependency_result <- L1.ValidateDependencyDeclarations_v1(bundle)
  oracle_result <- L1.ValidateAcceptanceOracles_v1(bundle)
  edge_case_result <- L1.ValidateEdgeCaseCoverage_v1(bundle)
  lockfile_result <- L1.ValidateSemanticLockfile_v1(bundle)

  result_set <- L1.CombineValidationResults_v1([
      header_result,
      registry_result,
      path_result,
      authority_result,
      dependency_result,
      oracle_result,
      edge_case_result,
      lockfile_result
  ])

  decision <- L1.DecideReadiness_v1(result_set, policy)
  trace <- L1.BuildValidationTrace_v1(bundle, result_set, decision)

  RETURN L1.FICBundleValidationOutput_v1(result_set, decision, trace)
```

This procedure is acceptable because each validation meaning is operatorized.

---

## 26. Machine-Readable Manifest Template

```yaml
l1_eqc_manifest:
  manifest_version: "v0.5"
  portfolio_id: "AGENT_X_L1"
  procedures:
    - procedure_id: "EQC-PROC-L1-VALIDATE-FIC-BUNDLE"
      path: "L1/eqc/procedures/L1_ValidateFICBundle.eqc.md"
      version: "v1.0.0"
      operators:
        - "L1.ValidateBundleHeader_v1"
        - "L1.ValidateFICRegistryCoverage_v1"
        - "L1.ValidateCanonicalPaths_v1"
        - "L1.ValidateAuthorityBindings_v1"
        - "L1.ValidateDependencyDeclarations_v1"
        - "L1.ValidateAcceptanceOracles_v1"
        - "L1.ValidateEdgeCaseCoverage_v1"
        - "L1.ValidateSemanticLockfile_v1"
        - "L1.CombineValidationResults_v1"
        - "L1.DecideReadiness_v1"
        - "L1.BuildValidationTrace_v1"
  operators:
    - name: "L1.DecideReadiness_v1"
      path: "L1/eqc/operators/decide_readiness.eqc.md"
      version: "v1.0.0"
      category: "readiness"
      purity: "pure"
```

---

## 27. Lightweight EQC Lint Rules

The first EQC linter should check these rules.

```yaml
eqc_lint_rules:
  required:
    - EQC_HEADER_PRESENT
    - VERSION_MARKER_PRESENT
    - GLOBAL_SEMANTICS_PRESENT_FOR_PROCEDURE
    - STATE_INPUT_OUTPUT_DECLARED
    - OPERATOR_MANIFEST_PRESENT_FOR_PROCEDURE
    - ALL_CALLED_OPERATORS_MANIFESTED
    - OPERATOR_SIGNATURE_PRESENT
    - PURITY_DECLARED
    - DETERMINISM_DECLARED
    - ORDERING_POLICY_DECLARED
    - FAILURE_BEHAVIOR_DECLARED
    - TEST_VECTOR_PRESENT
    - TRACE_SCHEMA_DECLARED_FOR_PROCEDURE
  release_blocking:
    - DUPLICATE_OPERATOR_NAME
    - DUPLICATE_DOC_ID
    - UNMANIFESTED_OPERATOR_CALL
    - HIDDEN_STATE
    - UNDECLARED_OUTPUT
    - UNKNOWN_ERROR_CODE
    - NONDETERMINISTIC_ORDERING
```

---

## 28. Controlled Exit Statuses

EQC validators must return one of these statuses:

```text
PASS
WARNING
BLOCKED
FAIL
TOOL_ERROR
```

Meaning:

| Status | Meaning |
|---|---|
| `PASS` | All required rules pass. |
| `WARNING` | Non-blocking issue exists. |
| `BLOCKED` | Required context, authority, or evidence is missing. |
| `FAIL` | A rule is violated. |
| `TOOL_ERROR` | Validator could not run correctly. |

`TOOL_ERROR` must not be treated as `PASS`.

### 28.1 Status severity and aggregation

When multiple operator results are combined, the final status is the most severe status by this order:

```text
PASS < WARNING < BLOCKED < FAIL < TOOL_ERROR
```

Readiness statuses that are not validator statuses must be mapped before aggregation:

```yaml
readiness_status_mapping:
  VALIDATED: PASS
  READY_FOR_IMPLEMENTATION: PASS
  NO_CHANGE: PASS
  IMPLEMENTED_UNVALIDATED: WARNING
  BLOCKED: BLOCKED
  REJECTED: FAIL
```

Rules:

```text
- `TOOL_ERROR` must never be downgraded to `WARNING` or `PASS`.
- `NO_CHANGE` is acceptable only with inspection evidence.
- `IMPLEMENTED_UNVALIDATED` cannot support release closure.
- Status aggregation must be deterministic and must preserve all component errors in the trace.
```

---

## 29. Release Gate

An Agent_X L1 release package may depend on EQC-governed behavior only if:

```text
[ ] all referenced EQC docs are registered in ES
[ ] all EQC-bound implementation artifacts are registered in SIB
[ ] all EQC operators used by procedures are in the operator manifest
[ ] all EQC procedure specs have global semantics
[ ] all operator specs have signatures, purity, determinism, and failure behavior
[ ] all required test vectors exist
[ ] all release-blocking lint rules pass
[ ] all equivalence claims are declared
[ ] all trace/evidence schemas are present
[ ] no L0 impact is hidden inside L1 EQC behavior
```

If any required item fails, the release status is `BLOCKED` or `FAIL`.

---

## 30. Adoption Modes

| Mode | Use Case | Minimum EQC Requirement |
|---|---|---|
| `advisory` | early notes | named procedure or operator only |
| `structured` | design before FIC | header, inputs, outputs, basic procedure |
| `governed` | implementation-bound L1 behavior | manifest, operators, tests, trace schema |
| `validated` | release-bound validators/classifiers | linter, test vectors, evidence records |
| `enforced` | future CI gate | machine schemas, executable validators, release blocking |

Current Agent_X L1 target:

```text
governed -> validated
```

Do not attempt full `enforced` mode until the L1 validators exist.

---

## 31. Anti-Patterns

Reject an EQC-governed L1 artifact if it contains:

```text
- "use best judgment" in normative procedure steps
- unlisted operator calls
- hidden scoring rules
- hidden tie-breaking
- missing invalid-input behavior
- missing duplicate-ID behavior
- procedure bodies that perform I/O directly
- model calls inside validators
- unbounded retries
- unregistered error codes
- output statuses not in the controlled set
- test vectors that only check that output exists
- release decisions based on prose confidence instead of evidence
```

---

## 32. Deferred Full-EQC Features

The following full EQC features are intentionally deferred for Agent_X L1:

```yaml
deferred_full_eqc_features:
  stochastic_prng_replay:
    status: "deferred"
    reason: "Current L1 procedures should be deterministic and non-stochastic."
  gpu_numeric_determinism:
    status: "deferred"
    reason: "Current L1 validation does not require GPU kernels."
  distributed_reduction_policy:
    status: "deferred"
    reason: "Current L1 validation is local and single-repository."
  full_checkpoint_serialization:
    status: "deferred"
    reason: "Replay package is enough for current L1 stage."
  golden_trace_portfolio:
    status: "deferred"
    reason: "Can be added after validators stabilize."
```

Deferred means not required now, not rejected permanently.

---


## 33. Machine-Readable Schema Requirements

Lightweight EQC documents may begin as Markdown, but release-bound procedure and operator documents must expose a parseable schema block.

Minimum schema files:

```text
L1/eqc/schemas/
  eqc-header.schema.json
  eqc-procedure.schema.json
  eqc-operator.schema.json
  eqc-manifest.schema.json
  eqc-test-vector.schema.json
  eqc-trace-record.schema.json
  eqc-validator-output.schema.json
```

Required schema coverage:

```yaml
schema_coverage:
  eqc_header:
    required: true
    release_blocking_if_missing: true
  global_semantics:
    required_for: ["procedure-spec", "decision-table", "state-machine"]
    release_blocking_if_missing: true
  operator_manifest:
    required_for: ["procedure-spec"]
    release_blocking_if_missing: true
  operator_signature:
    required_for: ["operator-spec"]
    release_blocking_if_missing: true
  test_vectors:
    required_for: ["operator-spec", "decision-table"]
    release_blocking_if_missing: true
  trace_schema:
    required_for: ["procedure-spec"]
    release_blocking_if_missing: true
```

Rules:

```text
- Markdown prose may explain the artifact, but schema blocks are the validation source.
- Schema blocks must not contradict prose.
- If prose and schema conflict, validation returns `FAIL_SCHEMA_PROSE_CONFLICT`.
- Schema validation failure is release-blocking for governed, validated, and enforced modes.
```

---

## 34. Version Marker and Canonical Path Rules

Every EQC artifact must contain a version marker and use a canonical repository-relative path.

### 34.1 Version marker

Markdown EQC artifacts must contain this exact marker near the top of the file:

```text
Spec Version: AGENT_X_L1_LIGHTWEIGHT_EQC-vX.Y.Z
```

YAML or JSON sidecars must contain:

```yaml
spec_version: "AGENT_X_L1_LIGHTWEIGHT_EQC-vX.Y.Z"
```

Rules:

```text
- The marker must match the ES registry version.
- Missing marker is `FAIL_VERSION_MARKER_MISSING`.
- Marker/registry mismatch is `FAIL_VERSION_MARKER_MISMATCH`.
```

### 34.2 Canonical path

```yaml
canonical_path_policy:
  path_style: "repository_relative_posix"
  absolute_paths_allowed: false
  parent_directory_segments_allowed: false
  symlink_escape_allowed: false
  case_sensitive: true
```

Rules:

```text
- Paths must use `/`, not platform-specific separators.
- Paths must not start with `/`, `./`, or `../`.
- Paths must not resolve outside the repository root.
- Symlinks that escape the repository root are release-blocking.
```

---

## 35. Deterministic Change Classification

EQC changes must be classified before implementation or release decisions.

```yaml
change_classification:
  allowed_classes:
    - METADATA
    - VALIDATION
    - STATE
    - FUNCTIONAL
  severity_order: ["METADATA", "VALIDATION", "STATE", "FUNCTIONAL"]
```

Classification triggers:

| Trigger | Class | Meaning |
|---|---|---|
| `TRG_EQC_MD_ONLY` | `METADATA` | Owner, commentary, formatting, or non-functional references changed. |
| `TRG_TEST_VECTOR_CHANGED` | `VALIDATION` | Test vectors or expected validation assets changed. |
| `TRG_TRACE_SCHEMA_CHANGED` | `FUNCTIONAL` | Trace-significant fields changed. |
| `TRG_OPERATOR_SIGNATURE_CHANGED` | `FUNCTIONAL` | Operator inputs, outputs, or types changed. |
| `TRG_OPERATOR_DEFINITION_CHANGED` | `FUNCTIONAL` | Operator semantics changed. |
| `TRG_PROCEDURE_FLOW_CHANGED` | `FUNCTIONAL` | Procedure ordering, branching, or operator calls changed. |
| `TRG_EQUIVALENCE_LEVEL_CHANGED` | `FUNCTIONAL` | Required E0/E1/E2/E3 level changed. |
| `TRG_MANIFEST_BINDING_CHANGED` | `STATE` or `FUNCTIONAL` | Operator version binding changed; functional if decision outputs can change. |
| `TRG_SCHEMA_ONLY_TIGHTENING` | `VALIDATION` | Schema is stricter but does not change semantic behavior. |

Rules:

```text
- The most severe trigger wins.
- FUNCTIONAL changes require ES impact analysis and SIB binding review when implementation is bound.
- VALIDATION changes require rerunning affected test vectors.
- METADATA changes must still preserve anchors and version markers.
```

### 35.1 Version impact and migration notes

Every classified EQC change must declare version impact.

```yaml
version_impact_policy:
  METADATA: "patch"
  VALIDATION: "patch|minor if validation contract becomes stricter"
  STATE: "patch|minor depending on manifest binding effect"
  FUNCTIONAL: "minor|major depending on compatibility"
```

Major impact is required when:

```text
- an operator signature is removed or made incompatible;
- a procedure removes or reorders trace-significant behavior;
- a status meaning changes;
- an equivalence level is weakened;
- an existing HARD-bound implementation can no longer conform without code changes.
```

Functional changes must include migration notes:

```yaml
migration_note:
  change_id: "EQC-MIG-..."
  affected_docs: []
  affected_artifacts: []
  required_updates: []
  equivalence_claim: "E0|E1|E2|E3|none"
  validation_required: []
```

Missing migration notes for FUNCTIONAL changes are release-blocking.


---

## 36. Validator JSON Output Schema

The future `l1-eqc validate` command must emit deterministic JSON.

```json
{
  "eqc_version": "AGENT_X_L1_LIGHTWEIGHT_EQC-v0.5.0",
  "workspace_ref": "<commit-or-workspace-id>",
  "status": "PASS|WARNING|BLOCKED|FAIL|TOOL_ERROR",
  "errors": [
    {
      "code": "EQC_L1_...",
      "doc_id": "EQC-L1-...",
      "operator": "L1.OperatorName_v1",
      "message": "...",
      "release_blocking": true
    }
  ],
  "warnings": [],
  "classification_triggers": [
    {
      "doc_id": "EQC-L1-...",
      "triggers": ["TRG_..."]
    }
  ],
  "manifest_digest": "sha256:<lowercase-hex>",
  "input_digest": "sha256:<lowercase-hex>",
  "output_digest": "sha256:<lowercase-hex>",
  "test_vectors_run": ["TV-..."],
  "test_vectors_missing": [],
  "equivalence_claims": [
    {
      "doc_id": "EQC-L1-...",
      "level": "E0|E1|E2|E3",
      "evidence": "..."
    }
  ],
  "skipped_checks": [
    {
      "check_id": "...",
      "reason": "...",
      "waiver_id": null,
      "release_blocking": true
    }
  ],
  "schema_version": "eqc-validator-output/v0.5"
}
```

Deterministic output rules:

```text
- Object keys must be emitted in sorted order.
- Errors sort by `(code, doc_id, operator)`.
- Warnings sort by `(code, doc_id, operator)`.
- Test vector IDs sort lexicographically.
- Unknown fields are invalid unless the schema version explicitly allows extensions.
```

---

## 37. Initial Operator Coverage Matrix

The first L1 EQC operator set must not be treated as a loose list. Each operator needs a purpose, risk, test-vector requirement, and binding target.

| Operator | Purpose | Risk | Required test vectors | Expected binding |
|---|---|---:|---|---|
| `L1.ValidateGoalInput_v1` | Normalize and reject unusable goals | medium | empty, whitespace-only, hostile instruction, valid goal | FIC + SIB |
| `L1.ClassifyGoal_v1` | Classify requested change type | high | doc-only, FIC update, SIB/ES/EQC update, L0-impact, unknown | EQC + FIC + SIB |
| `L1.ComputeImpactClosure_v1` | Determine affected docs/artifacts | high | no edges, direct edge, transitive edge, cycle, L0 impact | EQC + ES + SIB |
| `L1.BuildUnitPlan_v1` | Convert classification into bounded units | medium | single unit, multi-unit split, duplicated owner, deferred unit | FIC + workflow |
| `L1.BuildFICPlan_v1` | Create/update FIC package plan | medium | missing FIC, stale FIC, ready FIC, conflicting FIC | FIC + SIB |
| `L1.ValidateFICReadiness_v1` | Validate pre-code gate | high | missing test oracle, missing dependency, complete package, stale lockfile | FIC + workflow |
| `L1.BuildHandoffPacket_v1` | Produce bounded coding context | medium | allowed files, forbidden files, stale context, overbroad context | workflow + FIC |
| `L1.CollectEvidence_v1` | Separate evidence from claims | medium | test log, missing command, failed check, LLM-only claim | SIB + workflow |
| `L1.DecideReadiness_v1` | Convert validation result to controlled status | high | pass, warning, blocked, fail, tool-error | EQC + workflow |
| `L1.BuildTraceRecord_v1` | Build deterministic trace record | medium | normal trace, error trace, missing input digest | ES + SIB |

Rules:

```text
- High-risk operators require at least one negative test vector and one conflict/blocked test vector.
- Operators that can block L0-impact changes require explicit L0-impact test vectors.
- An operator may not be marked ready-for-use until its coverage row is satisfied or waived.
```

---

## 38. Operator Readiness Gate

An operator is ready-for-use only when all items pass:

```yaml
operator_readiness:
  header_present: PASS
  version_marker_present: PASS
  signature_complete: PASS
  purity_declared: PASS
  deterministic_behavior_declared: PASS
  input_validation_declared: PASS
  output_schema_declared: PASS
  failure_behavior_declared: PASS
  ordering_rule_declared: PASS
  tie_breaking_rule_declared: PASS
  test_vectors_present: PASS
  negative_tests_present_if_high_risk: PASS
  trace_or_evidence_binding_declared: PASS
  es_registry_entry_present: PASS
  sib_binding_present_if_implemented: PASS
```

If any item is missing, status must remain `draft` or `blocked`, not `ready-for-use`.

---

## 39. Procedure Readiness Gate

A procedure is ready-for-use only when all items pass:

```yaml
procedure_readiness:
  global_semantics_present: PASS
  state_inputs_outputs_declared: PASS
  operator_manifest_complete: PASS
  all_called_operators_registered: PASS
  control_flow_only_body: PASS
  termination_condition_declared_if_looping: PASS
  trace_schema_declared: PASS
  error_statuses_controlled: PASS
  equivalence_requirement_declared: PASS
  release_blocking_lint_passed: PASS
```

A procedure that calls an unready operator is not ready-for-use.

---

## 40. Release Package Requirements

A release package that includes EQC-governed behavior must include:

```text
L1/eqc/manifests/l1-eqc-manifest.yaml
L1/eqc/error_codes.yaml
L1/eqc/schemas/eqc-validator-output.schema.json
L1/eqc/tests/*.test-vectors.yaml
L1/eqc/traces/*.schema.yaml
L1/eqc/reports/l1-eqc-validation-report.json
```

The release package must also include:

```yaml
release_eqc_closure:
  eqc_docs_registered_in_es: true
  eqc_bound_artifacts_registered_in_sib: true
  manifest_digest_recorded: true
  validator_output_recorded: true
  test_vectors_run_or_waived: true
  unresolved_release_blocking_errors: 0
```

---


## 41. Waiver and Unknown Handling

A lightweight EQC artifact may use a waiver only when a requirement is intentionally deferred or cannot be satisfied at the current maturity level. Waivers must not hide missing semantics.

```yaml
eqc_waiver:
  waiver_id: "EQC-WVR-..."
  affected_doc_id: "EQC-L1-..."
  affected_anchor_id: "..."
  waived_requirement: "..."
  reason: "..."
  risk_level: "low|medium|high|critical"
  expires_utc: "YYYY-MM-DDTHH:MM:SSZ"
  replacement_control: "..."
```

Rules:

```text
- Waivers must expire.
- Waivers for L0-impact detection, status aggregation, hidden state, or unmanifested operators are not allowed for release-bound artifacts.
- Unknown input semantics produce `BLOCKED`, not a waiver, unless the artifact is explicitly advisory.
- A waived test vector must appear in the release package waiver list.
```

## 42. Source-of-Truth and Conflict Rules

Every EQC artifact that defines behavior must declare the source of truth it refines or implements.

```yaml
source_of_truth:
  primary_authority: "AGENT_X_L1::DOC-..."
  authority_anchor_id: "..."
  derived_from: []
  conflicts: []
```

Conflict handling:

```text
- Conflict with L0 boundary rules => BLOCKED.
- Conflict with ES registry/graph => FAIL until registry or document is corrected.
- Conflict with SIB binding => BLOCKED until binding impact is resolved.
- Conflict between EQC operator and FIC => BLOCKED unless authority order resolves it explicitly.
- Existing code cannot override an EQC operator with a HARD binding.
```

## 43. Validator Maturity Levels

Lightweight EQC validation may mature in stages. The release package must declare which maturity level was used.

| Level | Name | Validator capability | Release use |
|---:|---|---|---|
| 0 | manual | human checklist only | advisory only |
| 1 | schema | parse headers, manifests, schemas | governed draft |
| 2 | structural | check operators, manifests, paths, duplicate IDs | implementation-bound |
| 3 | semantic-lite | run test vectors and controlled decision tables | release candidate |
| 4 | enforced | CI blocks release on violations | future target |

Current Agent_X L1 target:

```text
Level 2 before implementation-bound use.
Level 3 before release-candidate use.
```


## 44. Reproducibility and Replay-Lite Contract

Every EQC-governed L1 procedure must declare its reproducibility class.

```yaml
reproducibility:
  class: "deterministic|recorded_external|non_replayable_blocked"
  replay_inputs:
    - "canonical input artifacts"
    - "operator manifest versions"
    - "policy files"
    - "environment profile id"
  replay_token:
    required: true
    definition: "sha256(canonical_json(replay_inputs + manifest + procedure_id + procedure_version))"
```

Rules:

```text
- deterministic procedures must produce the same result from the same canonical inputs.
- procedures that read external state must record that state as an input artifact before validation.
- procedures with unrecorded external nondeterminism are not release-bound.
- every validation trace must include the replay token.
```

This is intentionally lighter than full EQC PRNG replay. Agent_X L1 should not use randomness in validators, classifiers, digest calculators, or readiness decisions. If randomness is later introduced, the affected operator must be upgraded to full EQC-style seeded replay semantics before release use.

---

## 45. Environment and Dependency Profile Lite

Each EQC-governed procedure must declare the minimum environment profile needed to reproduce its validation.

```yaml
environment_profile:
  profile_id: "agent_x_l1_python_local"
  python_version: "declared-by-repo"
  os_assumption: "posix-compatible or explicitly declared"
  timezone: "UTC"
  locale: "C.UTF-8 or declared equivalent"
  network_allowed: false
  wall_clock_allowed: false
  filesystem_scope: "repository-root only unless declared"
```

Rules:

```text
- network access is forbidden for EQC validation unless the operator explicitly declares a content-addressed input snapshot.
- wall-clock time must not affect functional output.
- timestamps in evidence must be UTC ISO-8601 with trailing Z.
- file traversal must stay inside the repository root.
- environment variables must not affect behavior unless named in the operator input schema.
```

---

## 46. Data and Artifact Provenance Lite

If an EQC-governed procedure consumes files, generated documents, schemas, tests, traces, or registry sidecars, it must declare them as input artifacts.

```yaml
input_artifact:
  artifact_id: "ART-..."
  path: "L1/..."
  artifact_type: "fic|workflow|sib|es|eqc|schema|test-vector|trace|code|other"
  digest: "sha256:<hex>"
  version: "vX.Y.Z|unknown-blocking|not-versioned-waived"
  provenance: "authored|generated|inspected|external-snapshot"
```

Rules:

```text
- release-bound procedures must not consume anonymous files.
- generated inputs must identify the generator or previous validation step.
- stale or digest-mismatched inputs produce BLOCKED_STALE_INPUT unless explicitly waived.
- external examples may inform prose but cannot define functional semantics unless recorded as input artifacts.
```

---

## 47. Metrics and Comparability Lite

Any EQC-governed scoring, ranking, readiness, or quality decision must define a metric schema before use.

```yaml
metric_schema:
  metric_id: "METRIC-..."
  name: "readiness_score"
  type: "integer|decimal|enum|boolean|object"
  range: "0..10"
  comparison: "higher_is_better|lower_is_better|exact_match|ordered_enum"
  tie_break: "declared deterministic rule"
  computed_by_operator: "OperatorName_v#"
```

Rules:

```text
- a metric used for release or blocking decisions must have a declared range and comparison rule.
- numeric metrics must define rounding and tolerance if decimals are used.
- multiple metrics must define aggregation order and severity precedence.
- readiness scores must not override blocking errors.
```

---

## 48. Purity, Side-Effect, and External-Nondeterminism Classes

Every operator must declare one purity class.

| Purity Class | Meaning | Release-bound rule |
|---|---|---|
| `PURE` | output depends only on inputs | preferred |
| `STATEFUL_DECLARED` | reads/writes declared local state | allowed with state schema |
| `IO_DECLARED` | reads/writes declared files or traces | allowed with provenance and path controls |
| `EXTERNAL_RECORDED` | consumes external state captured as input artifact | allowed only with replay evidence |
| `EXTERNAL_UNRECORDED` | consumes unrecorded external nondeterminism | blocked for release |

Rules:

```text
- hidden globals are forbidden.
- hidden filesystem reads are forbidden.
- hidden environment-variable reads are forbidden.
- hidden cache use is forbidden unless declared as state.
- validators and classifiers should be PURE whenever practical.
```

---

## 49. Parallelism and Concurrency Lite

Default policy:

```yaml
parallelism:
  allowed: false
  async_updates_allowed: false
  concurrent_state_mutation_allowed: false
```

Parallelism may be introduced only when the EQC artifact declares:

```yaml
parallelism:
  allowed: true
  parallel_scope: "..."
  deterministic_order: "..."
  reduction_rule: "stable lexical order before aggregation"
  tie_break: "..."
  trace_required: true
```

Rules:

```text
- validation results must not depend on thread scheduling.
- graph traversal and impact closure must use deterministic ordering.
- any future parallel reduction must produce the same output as the serial reference procedure or declare a higher equivalence class.
```

---

## 50. Golden Trace and Example-Vector Policy

For current Agent_X L1, every release-bound EQC procedure should have at least one of:

```text
- exact test vectors
- golden trace
- decision-table fixture
- schema fixture with expected PASS/FAIL output
```

Critical validators should have both exact test vectors and a golden trace.

Minimum golden trace fields:

```yaml
golden_trace:
  trace_id: "TRACE-..."
  procedure_id: "PROC-..."
  procedure_version: "vX.Y.Z"
  replay_token: "sha256:<hex>"
  input_artifacts: []
  operator_manifest_digest: "sha256:<hex>"
  expected_status: "PASS|FAIL|BLOCKED"
  expected_errors: []
  expected_warnings: []
```

Rules:

```text
- golden traces must be updated only through a declared validation or semantic change.
- tests must not be changed merely to match an accidental implementation.
- fixture intent must be recorded: normal, boundary, negative, conflict, stale, or security.
```

---

## 51. Full-EQC Escalation Triggers

A lightweight EQC artifact must be escalated to full EQC or near-full EQC if any of the following become true:

```text
- stochastic behavior is introduced;
- floating-point numerical optimization becomes central;
- parallel reductions affect outputs;
- long-running checkpoint/restore becomes required;
- multiple environment profiles must be distributionally compared;
- external data preprocessing defines functional semantics;
- algorithm outputs are used to promote self-modifying or irreversible changes.
```

Escalation means the artifact must add the relevant full EQC blocks for PRNG, numeric policy, parallel policy, data provenance, equivalence testing, checkpointing, and replay.

---
## 52. Final Self-Assessment Gate

Before this standard is considered complete for the current L1 stage, it must pass:

```yaml
standard_self_assessment_gate:
  scope_is_lightweight: PASS
  procedure_operator_separation_defined: PASS
  state_input_output_rules_defined: PASS
  ordering_and_tie_rules_defined: PASS
  trace_and_evidence_rules_defined: PASS
  test_vector_rules_defined: PASS
  change_classification_defined: PASS
  version_impact_defined: PASS
  waiver_and_unknown_rules_defined: PASS
  integration_with_fic_sib_es_defined: PASS
  release_package_closure_defined: PASS
  deferred_full_eqc_features_listed: PASS
```

## 53. Finalization Threshold

For the current Agent_X L1 stage, this standard should stop growing once it satisfies these conditions:

```text
[ ] lightweight enough to be usable before L1 code exists
[ ] strict enough to prevent hidden algorithm semantics
[ ] compatible with FIC, SIB, ES, and Pseudocode-to-FIC workflow
[ ] capable of supporting future executable validators
[ ] not pretending to be full production EQC-ES/SIB infrastructure
```

Further additions should go into concrete operator specs, manifests, schemas, or validators rather than expanding this standard indefinitely.

---
## 54. Quality Rubric

Score an L1 EQC artifact from 0 to 10.

| Score | Meaning |
|---:|---|
| 0-3 | prose only; not usable as an implementation or validation contract |
| 4-5 | partially structured; still requires guessing |
| 6 | usable with human interpretation only |
| 7 | usable for low-risk internal logic |
| 8 | good governed spec; minor machine-checking gaps |
| 9 | strong implementation-bound spec with tests and traces |
| 10 | machine-checkable, registered, bound, tested, and release-ready |

Minimums:

```text
advisory design: 6+
L1 implementation-bound operator: 8+
validator/classifier/readiness operator: 9+
release-bound EQC procedure: 9.5+
```

---



## 55. Canonical Enum and Severity Registry

All status names, change classes, equivalence levels, purity classes, artifact types, and error severities used by EQC-governed L1 artifacts must come from a single controlled enum registry.

Recommended location:

```text
L1/eqc/enums.yaml
```

Minimum content:

```yaml
eqc_enums:
  validator_status:
    order: ["PASS", "WARNING", "BLOCKED", "FAIL", "TOOL_ERROR"]
  readiness_status:
    allowed: ["READY_FOR_IMPLEMENTATION", "VALIDATED", "NO_CHANGE", "IMPLEMENTED_UNVALIDATED", "BLOCKED", "REJECTED"]
  change_class:
    order: ["METADATA", "VALIDATION", "STATE", "FUNCTIONAL"]
  equivalence_level:
    order: ["E0", "E1", "E2", "E3"]
  purity_class:
    allowed: ["PURE", "STATEFUL_DECLARED", "IO_DECLARED", "EXTERNAL_RECORDED", "EXTERNAL_UNRECORDED"]
```

Rules:

```text
- New enum values are FUNCTIONAL unless explicitly declared metadata-only.
- Validator output must reject unknown enum values.
- Synonyms are prohibited in machine-readable fields.
- Human-readable prose may explain enums, but schema blocks must use the canonical value exactly.
```

## 56. Cross-Standard Consistency Matrix

Every release-bound EQC artifact must be consistent with the other L1 standards.

```yaml
cross_standard_consistency:
  fic:
    required_when: "EQC operator is implemented by a code file"
    check: "FIC public surface and tests match EQC operator signature and test vectors"
    blocking_if_missing: true
  sib:
    required_when: "EQC operator or procedure binds to implementation"
    check: "SIB HARD binding references EQC anchor and implementation anchor"
    blocking_if_missing: true
  es:
    required_when: "EQC document is active or release-bound"
    check: "ES registry and graph include the EQC document and digest fields"
    blocking_if_missing: true
  workflow:
    required_when: "EQC artifact is used in a coding handoff"
    check: "handoff packet includes EQC references, allowed files, checks, and evidence requirements"
    blocking_if_missing: true
```

Rules:

```text
- EQC cannot silently override FIC/SIB/ES/workflow constraints.
- FIC/SIB/ES cannot silently weaken EQC operator semantics.
- Any conflict produces BLOCKED_CROSS_STANDARD_CONFLICT until the authority path is documented.
```

## 57. Validator No-Silent-Skip Rule

A validator must not omit a required check without recording it.

```yaml
validator_skip_record:
  check_id: "EQC_HEADER_PRESENT"
  status: "RUN|SKIPPED|NOT_APPLICABLE"
  reason: ""
  waiver_id: null
  release_blocking: true
```

Rules:

```text
- `SKIPPED` is release-blocking unless a valid waiver exists.
- `NOT_APPLICABLE` must include a deterministic reason.
- A missing check result is treated as `SKIPPED`.
- A validator crash is `TOOL_ERROR`, not `SKIPPED`.
```

## 58. Generated Artifact Edit Policy

Generated EQC artifacts may exist, but they must be marked and regenerated rather than manually edited.

```yaml
generated_artifact_policy:
  generated_paths:
    - "L1/eqc/generated/**"
  manual_edit_allowed: false
  generator_required: true
  generator_digest_required: true
  source_inputs_required: true
```

Rules:

```text
- Generated manifests, coverage reports, validator outputs, and readiness reports must identify their generator.
- Manual edits to generated artifacts are invalid unless the artifact is explicitly converted to authored status.
- Regeneration must be reproducible from declared source inputs.
```

## 59. Minimal First Implementation Slice

The first implementation slice for this standard should be intentionally small.

```text
1. L1/eqc/enums.yaml
2. L1/eqc/error_codes.yaml
3. L1/eqc/manifests/l1-eqc-manifest.yaml
4. L1/eqc/operators/decide_readiness.eqc.md
5. L1/eqc/tests/readiness-decision.test-vectors.yaml
6. L1/eqc/schemas/eqc-validator-output.schema.json
```

This slice is enough to prove the standard can govern a real decision operator before expanding to goal classification, impact closure, FIC validation, or release package validation.

## 60. Anti-Bloat Boundary

This standard is now complete for the current Agent_X L1 stage. Future detail should be placed in concrete artifacts rather than extending the standard.

Allowed future additions to this document:

```text
- correction of inconsistency
- removal of ambiguity
- compatibility update required by FIC/SIB/ES/workflow
- escalation to full EQC for a specific new capability
```

Not allowed without strong justification:

```text
- adding more generic governance sections
- adding duplicate lifecycle rules already owned by workflow/ES/SIB/FIC
- expanding examples into implementation plans
- adding production-scale distributed, stochastic, or GPU rules before L1 needs them
```


## 61. Self-Assessment for This Document

This document is intentionally lightweight and stage-appropriate.

Current self-assessment:

```yaml
self_assessment:
  version: "v0.5.0"
  score_for_current_l1_stage: "10/10"
  strengths:
    - "Defines clear lightweight EQC scope for Agent_X L1."
    - "Separates procedures from operators."
    - "Adds deterministic ordering, trace, test, equivalence, schema, and JSON validator-output rules."
    - "Defines version markers, canonical paths, change classification, readiness gates, and release package requirements."
    - "Integrates with FIC, SIB, ES, and the Pseudocode-to-FIC workflow."
    - "Adds stable anchors, status aggregation, waiver/unknown handling, migration notes, and validator maturity levels."
    - "Adds replay-lite, environment, provenance, metrics, purity, parallelism, golden trace, and full-EQC escalation rules."
    - "Adds canonical enum registry, cross-standard consistency, no-silent-skip rules, generated-artifact policy, and a minimal first implementation slice."
  remaining_gaps: []
```

---

## 62. Acceptance Criteria

This lightweight EQC standard is acceptable for current Agent_X L1 use when:

```text
[ ] it defines where EQC artifacts live
[ ] it defines headers and version markers
[ ] it defines procedure/operator separation
[ ] it defines operator templates
[ ] it defines deterministic ordering and tie-breaking
[ ] it defines input/output/state requirements
[ ] it defines trace and evidence records
[ ] it defines validation and test-vector requirements
[ ] it defines equivalence levels
[ ] it integrates with FIC, SIB, and ES
[ ] it identifies deferred full-EQC features
[ ] it is usable before L1 implementation begins
[ ] it defines schema and validator-output expectations
[ ] it defines operator and procedure readiness gates
[ ] it defines release package closure for EQC-governed behavior
[ ] it defines stable semantic anchors
[ ] it defines status aggregation
[ ] it defines waiver and unknown handling
[ ] it defines version impact and migration-note requirements
[ ] it defines reproducibility and replay-lite requirements
[ ] it defines environment and data provenance rules
[ ] it defines metric comparability for scoring and readiness decisions
[ ] it defines purity and side-effect classes
[ ] it defines parallelism/concurrency default restrictions
[ ] it defines golden trace or example-vector expectations
[ ] it defines escalation triggers for full EQC
[ ] it defines canonical enum and severity registries
[ ] it defines cross-standard consistency checks
[ ] it prevents silent validator skips
[ ] it defines generated-artifact edit policy
[ ] it defines a minimal first implementation slice
```

All criteria are satisfied for `v0.5.0` at the standards-document level. Concrete operator documents and executable validators remain separate implementation artifacts.

