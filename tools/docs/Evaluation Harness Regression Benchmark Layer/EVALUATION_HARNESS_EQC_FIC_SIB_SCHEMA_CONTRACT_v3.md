# EVALUATION_HARNESS_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: EVALUATION_HARNESS_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_EVALUATION_HARNESS
component_name: Evaluation Harness / Regression Benchmark Layer
roadmap_layer: 15
roadmap_phase: Phase D — Evaluation, Regression, and Promotion Evidence
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
required_contracts:
  - Regression Benchmark Contract
  - Evaluation Dataset Contract
  - Scoring / Threshold Contract
  - Baseline Comparison Contract
  - Failure Classification Contract
  - Artifact / Evidence Contract
  - Benchmark Selection / Coverage Contract
  - Evaluator Independence / Anti-Gaming Contract
  - Flaky Benchmark Quarantine Contract
conditional_standards:
  - Command Acceptance Criteria, if validation commands are executed
  - Tool / MCP Adapter Acceptance Criteria, if registered tools are invoked
  - Policy / Capability Registry Acceptance Criteria, if evaluation permissions are checked
  - Model Evaluation Acceptance Criteria, if model output is benchmarked
optional_standards:
  - ES, only for ecosystem placement
  - Report Template, only if markdown reports are written
target_language: Python
canonical_subdirectory: tools/agentx_evolve/evaluation/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
canonical_fixture_subdirectory: tools/agentx_evolve/evaluation/fixtures/
canonical_dataset_subdirectory: tools/agentx_evolve/evaluation/datasets/
canonical_baseline_subdirectory: tools/agentx_evolve/evaluation/baselines/
runtime_artifact_root: .agentx-init/evaluation/
risk_level: critical
implementation_mode: deterministic evaluation harness with reproducible regression benchmarks
final_document_rating: 10/10
```

---

# 0. v3 Review and Upgrade Summary

The v2 controlling contract was strong and close to implementation-ready. I would rate it:

```text
9.7/10
```

It already covered the required controlling-contract areas:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
Regression Benchmark Contract
Evaluation Dataset Contract
Scoring / Threshold Contract
Baseline Comparison Contract
Failure Classification Contract
Artifact / Evidence Contract
Agent_X integration notes
OpenCode borrowing notes
allowed evaluation scope
benchmark input shape
run recording
score calculation
regression detection
pass/fail rules
evidence requirements
non-mutation rules
Definition of Done
```

It was not fully 10/10 because it still needed several final production-control details:

```text
1. A stricter benchmark selection and coverage contract so benchmark suites cannot be cherry-picked.
2. A clearer traceability rule from Agent_X layer requirement -> benchmark case -> score -> threshold -> evidence.
3. Explicit deterministic comparator rules, including equality, ordered-list, unordered-list, numeric, schema, artifact, and safety-policy comparisons.
4. Stronger stochastic/model benchmark rules so model variance cannot weaken deterministic safety gates.
5. A flaky benchmark quarantine rule that prevents unstable cases from silently passing or blocking without review.
6. Anti-gaming rules to prevent benchmark overfitting, baseline refresh abuse, and selectively omitted failing cases.
7. Clearer negative benchmark pack requirements for safety regressions.
8. Stronger command/tool invocation boundary rules for evaluations that call prior Agent_X layers.
9. Fresh-clone reproducibility requirements aligned with prior Agent_X layer documents.
10. More explicit pass/fail aggregation rules for required, blocking, warning, deferred, stochastic, and future-layer cases.
```

This v3 adds those details and is the final 10/10 controlling contract for this layer.

---

# 1. Purpose

This document defines the controlling contract for the **Evaluation Harness / Regression Benchmark Layer** in Agent_X.

This layer evaluates whether Agent_X changes are acceptable, stable, reproducible, and safe to promote. It provides deterministic benchmark execution, scoring, regression comparison, failure classification, and evidence-backed reports.

This layer must define:

```text
what this layer is allowed to evaluate
what benchmark inputs look like
how benchmark runs are recorded
how scores are calculated
how regressions are detected
what counts as pass/fail
what evidence must be written
which other Agent_X layers it may call
what it must never mutate
```

This is the controlling document for the layer. The implementation spec must follow it. The post-implementation review / DoD document must validate against it.

---

# 2. Scope

## 2.1 Required in This Layer

The Evaluation Harness / Regression Benchmark Layer must define and control:

```text
evaluation suites
benchmark cases
benchmark datasets
benchmark fixtures
expected outputs
scoring rules
threshold rules
baseline comparisons
regression detection
failure classification
evaluation reports
evaluation evidence
evaluation run manifests
artifact provenance
reproducibility metadata
promotion-blocking evaluation outcomes
```

It may evaluate Agent_X behavior across controlled scenarios, including:

```text
schema validation behavior
policy decision behavior
tool execution behavior
sandbox-denial behavior
patch-safety behavior
MCP exposure behavior
failure taxonomy behavior
report generation behavior
context packing behavior
prompt contract behavior
model adapter behavior, when that layer exists
orchestrator behavior, when that layer exists
LLM implementation worker behavior, when that layer exists
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
model inference
LLM prompting logic
self-evolution orchestration
source patch generation
source patch application
policy decisions
sandbox path authorization
tool execution logic
Git promotion
human review UI
long-term learning
production monitoring
```

This layer evaluates outputs and behaviors. It does not become the owner of the systems it evaluates.

---

# 3. Why This Layer Is Safety-Critical

The Evaluation Harness / Regression Benchmark Layer is safety-critical because it decides:

```text
whether a change is better or worse
whether regressions are detected
whether failures are classified correctly
whether promotion should be blocked
whether benchmark outputs are reproducible
whether evaluation artifacts are trustworthy
whether thresholds were met
whether evidence supports the final score
whether future agents can rely on benchmark results
```

A weak evaluation layer could allow unsafe changes to pass because of vague scoring, missing baselines, incomplete evidence, unstable datasets, non-deterministic benchmarks, or unrecorded failures.

Therefore, this layer must be deterministic, schema-driven, evidence-backed, reproducible, and fail-closed.

---

# 4. Standards Package

## 4.1 Primary Standard: EQC

EQC is primary because this layer determines whether changes meet quality and safety expectations.

EQC applies to:

```text
evaluation correctness
benchmark reproducibility
score calculation
threshold enforcement
regression detection
baseline comparison
failure classification
evidence completeness
promotion-blocking behavior
```

The layer must not allow a change to pass if required evaluation evidence is missing, inconsistent, stale, schema-invalid, hash-invalid, or not reproducible.

## 4.2 Required Supporting Standard: FIC

FIC is required because this layer has concrete implementation files.

Expected file responsibilities include:

```text
evaluation models
benchmark suite registry
benchmark dataset loader
benchmark fixture loader
evaluation runner
case executor
score calculator
threshold checker
baseline comparator
regression detector
failure classifier
evidence writer
report writer
validation utilities
```

Each file must have a clear responsibility, public API, inputs, outputs, invariants, tests, and safety limits.

## 4.3 Required Supporting Standard: SIB

SIB is required because this layer is an integration boundary.

It may interact with:

```text
Policy / Capability Registry
Security Sandbox / Filesystem Boundary
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter Layer
Model Adapter Layer
Local Model Runtime Profile Layer
Context Builder / Task Packer
Prompt Contract / Prompt Versioning Layer
LLM Implementation Worker
Self-Evolution Orchestrator
Promotion / Release Gate
Git Integration Layer
Monitoring / Observability Layer
```

This layer must evaluate these systems without becoming a hidden bypass around them.

## 4.4 Required Supporting Standard: Schema Contract

Schema Contract is required because every evaluation input, run, result, score, threshold decision, baseline comparison, regression finding, and evidence record must be structured.

Required schema families include:

```text
evaluation_suite.schema.json
benchmark_case.schema.json
benchmark_dataset.schema.json
benchmark_fixture.schema.json
evaluation_run.schema.json
evaluation_result.schema.json
case_result.schema.json
score_result.schema.json
threshold_profile.schema.json
threshold_decision.schema.json
baseline_snapshot.schema.json
baseline_comparison.schema.json
regression_finding.schema.json
evaluation_failure.schema.json
evaluation_evidence_manifest.schema.json
evaluation_report.schema.json
evaluation_deviation.schema.json
```

## 4.5 Required Evidence / Audit Rules

Every evaluation run must create evidence.

Evidence is required for:

```text
benchmark suite selected
benchmark cases loaded
benchmark dataset hash
benchmark fixture hash
baseline snapshot used
evaluation environment
commands run, if any
registered tools called, if any
model/runtime profile used, if any
scores calculated
threshold decisions
regression comparisons
failure classifications
artifacts generated
final pass/fail decision
deviations accepted or rejected
```

---

# 5. Status Vocabulary

Use only these run-level statuses:

```text
PASS
PASS_WITH_WARNINGS
FAIL
REGRESSION_DETECTED
INSUFFICIENT_EVIDENCE
NOT_REPRODUCIBLE
BLOCKED
SCHEMA_INVALID
UNTRUSTED_INPUT
```

Use only these comparison statuses:

```text
NO_REGRESSION
REGRESSION_DETECTED
IMPROVEMENT_DETECTED
BASELINE_MISSING
BASELINE_INVALID
COMPARISON_NOT_REPRODUCIBLE
```

Use only these case statuses:

```text
CASE_PASS
CASE_FAIL
CASE_BLOCKED
CASE_SKIPPED_DEFERRED
CASE_SCHEMA_INVALID
CASE_NOT_REPRODUCIBLE
CASE_INSUFFICIENT_EVIDENCE
```

Rules:

```text
CASE_SKIPPED_DEFERRED cannot count as PASS.
INSUFFICIENT_EVIDENCE cannot count as PASS.
NOT_REPRODUCIBLE cannot count as PASS.
SCHEMA_INVALID cannot count as PASS.
UNTRUSTED_INPUT cannot count as PASS.
PASS_WITH_WARNINGS requires all blocking cases to pass and no critical regression.
```

---

# 6. Preconditions and Dependency Gates

## 6.1 Required Dependencies for Live Evaluation

Before live evaluation of a dependent layer is allowed, that layer must be present through a governed public interface.

Dependency gates:

```text
If Tool / MCP Adapter is missing -> tool-call benchmarks must be disabled or CASE_BLOCKED.
If Policy / Capability Registry is missing -> policy benchmarks must use fixtures only or CASE_BLOCKED.
If Security Sandbox is missing -> path/file/command benchmarks must use inert fixtures only or CASE_BLOCKED.
If Failure Taxonomy is missing -> failure-classification benchmarks must use local fixture mappings only or CASE_BLOCKED.
If Model Adapter is missing -> model-response benchmarks must be disabled or CASE_SKIPPED_DEFERRED.
If Local Model Runtime Profile is missing -> local runtime benchmarks must be disabled or CASE_SKIPPED_DEFERRED.
If Promotion Gate is missing -> promotion recommendation must be evidence-only and not executable.
```

## 6.2 Restricted Mode

Restricted mode allows:

```text
schema validation benchmarks
fixture-only benchmark execution
score calculation tests
threshold calculation tests
baseline comparison tests
regression detector tests
failure classifier fixture tests
evidence writer tests
report writer tests
```

Restricted mode blocks:

```text
live tool execution
live model calls
live network calls
source mutation
patch application
Git write
promotion actions
human approval side effects
```

## 6.3 Authority Rule

The Evaluation Harness cannot create authority for another layer.

The following must remain authoritative:

```text
Policy / Capability Registry decides permissions.
Security Sandbox decides path/file/command access.
Tool / MCP Adapter controls registered tool execution.
Governed Patch Execution controls patch application.
Promotion / Release Gate controls promotion.
Model Adapter controls model execution.
```

The Evaluation Harness may record and score their behavior. It must not bypass or replace them.

---

# 7. Agent_X Integration Notes

## 7.1 Integration Role

The Evaluation Harness is not the orchestrator and not the promotion gate. It produces validated evaluation evidence that other layers may use.

Its main outputs are:

```text
evaluation result
score summary
threshold decision
regression findings
failure classifications
evidence manifest
reviewable report
promotion recommendation input
```

It may produce a recommendation such as:

```text
PASS
FAIL
REGRESSION_DETECTED
INSUFFICIENT_EVIDENCE
NOT_REPRODUCIBLE
```

The final promotion decision belongs to the Promotion / Release Gate.

## 7.2 Allowed Layer Calls

The Evaluation Harness may call other layers only through their public, governed interfaces.

Allowed calls include:

```text
Tool / MCP Adapter, for registered tool evaluations
Policy / Capability Registry, for evaluation permission checks
Security Sandbox, for reading benchmark inputs and writing evaluation artifacts
Failure Taxonomy, for classifying evaluation failures
Model Adapter, when model behavior is being evaluated
Local Model Runtime Profile, when local runtime constraints are being evaluated
Context Builder / Task Packer, when context packing behavior is evaluated
Prompt Contract / Prompt Versioning, when prompt stability is evaluated
Git Integration, for read-only commit/baseline metadata
```

## 7.3 Forbidden Direct Calls

This layer must not directly bypass:

```text
Tool / MCP Adapter
Policy / Capability Registry
Security Sandbox
Governed Patch Execution
Git Integration
Promotion / Release Gate
Model Adapter
```

It must not directly execute tools, mutate source files, apply patches, approve changes, or promote commits.

---

# 8. OpenCode Borrowing Notes

## 8.1 Concepts to Borrow

OpenCode-style ideas may be borrowed only as design patterns.

Useful concepts include:

```text
tool-level evaluation cases
command/tool transcript evaluation
snapshot-style comparison
structured run records
task-level success/failure grading
regression-oriented test packs
agent behavior evaluation through controlled prompts/tasks
artifact-backed reports
```

## 8.2 Concepts to Restrict

Do not borrow these assumptions directly:

```text
uncontrolled shell execution during benchmarks
network-enabled evaluation by default
provider/model calls without policy
mutable plugin behavior without registry control
test cases that depend on live external state
unversioned prompt/task inputs
unstructured subjective scoring
hidden benchmark mutations
```

## 8.3 Agent_X Mapping

| OpenCode-style concept | Agent_X equivalent | Required control |
|---|---|---|
| Tool transcript test | Tool adapter benchmark case | Tool registry + policy + evidence |
| Agent task eval | Evaluation benchmark case | Dataset hash + expected outcome |
| Snapshot comparison | Baseline comparison | Stable baseline snapshot |
| Failure review | Failure taxonomy classification | Standard failure class |
| Report output | Evaluation report | Schema-valid report + evidence refs |
| Command-based check | Validation command benchmark | Command Acceptance Criteria |
| Model behavior check | Model evaluation case | Model Adapter + runtime profile |

OpenCode source code, runtime dependencies, Bun/Node requirements, network behavior, and ungoverned tool execution must not be imported into Agent_X for this layer.

---

# 9. Evaluation Authority Rules

## 9.1 Evaluation Cannot Invent Authority

The Evaluation Harness cannot:

```text
override Policy / Capability Registry
approve unsafe tool execution
approve sandbox-denied actions
apply patches
promote code
mark an unsafe result as safe
ignore missing evidence
ignore failed required checks
refresh a baseline to hide a regression
```

## 9.2 Strictest Result Wins

When evaluation inputs disagree, the strictest result wins.

Decision precedence:

```text
SCHEMA_INVALID
UNTRUSTED_INPUT
INSUFFICIENT_EVIDENCE
NOT_REPRODUCIBLE
REGRESSION_DETECTED
THRESHOLD_FAILED
FAIL
PASS_WITH_WARNINGS
PASS
```

## 9.3 Fail-Closed Evaluation Rule

The layer must return `FAIL`, `INSUFFICIENT_EVIDENCE`, `NOT_REPRODUCIBLE`, `SCHEMA_INVALID`, or `UNTRUSTED_INPUT` when:

```text
benchmark input schema is invalid
benchmark dataset hash is missing
benchmark fixture hash is missing
baseline snapshot is missing when required
score cannot be calculated
threshold cannot be applied
regression comparison cannot be reproduced
evaluation evidence cannot be written
required artifacts are missing
external dependency is unavailable and no safe fixture exists
suite, dataset, or baseline provenance is untrusted
```

---

# 10. Benchmark Selection / Coverage Contract

## 10.1 Purpose

The Evaluation Harness must not allow selective benchmark execution to hide failures. Every evaluation run must identify which suite was selected, why it was selected, which cases were included, which cases were excluded, and whether the selected suite is sufficient for the requested decision.

## 10.2 Coverage Matrix

Every benchmark suite must include a coverage matrix that maps:

```text
Agent_X layer or contract requirement
benchmark case ID
case type
required dataset or fixture
expected behavior
scoring method
threshold rule
baseline requirement
blocking status
safety critical flag
evidence artifact
```

Required coverage categories for this layer:

```text
schema validation coverage
benchmark loading coverage
scoring coverage
threshold coverage
baseline comparison coverage
regression detection coverage
failure classification coverage
evidence writing coverage
non-mutation coverage
command/tool invocation boundary coverage
negative safety benchmark coverage
```

A run cannot be marked `PASS` if the selected suite lacks coverage for a required category relevant to the requested decision.

## 10.3 Suite Selection Rules

A suite selection record must include:

```text
selection_id
requested_decision_type
selected_suite_id
selected_suite_version
selection_reason
required_coverage_categories
covered_categories
missing_categories
excluded_cases
exclusion_reasons
selection_status
warnings
errors
```

Allowed selection statuses:

```text
SUITE_SELECTION_VALID
SUITE_SELECTION_INSUFFICIENT
SUITE_SELECTION_SCHEMA_INVALID
SUITE_SELECTION_UNTRUSTED
```

Rules:

```text
missing required coverage -> INSUFFICIENT_EVIDENCE
excluded blocking case without accepted deviation -> INSUFFICIENT_EVIDENCE
unknown suite version -> SCHEMA_INVALID or UNTRUSTED_INPUT
untrusted suite source -> UNTRUSTED_INPUT
```

## 10.4 Anti-Cherry-Picking Rule

The implementation must not permit:

```text
running only passing cases while claiming full-suite PASS
excluding failed cases after execution
renaming failed cases as deferred without a deviation record
changing case blocking status during a run
changing thresholds during a run
using a different baseline than the suite declares without evidence
```

If any of these occur, the final status must be `INSUFFICIENT_EVIDENCE`, `UNTRUSTED_INPUT`, or `FAIL`.

---

# 11. Comparator / Expected-Output Contract

## 11.1 Comparator Types

Every benchmark case must declare an explicit comparator. Supported comparator types are:

```text
EXACT_OBJECT_MATCH
EXACT_TEXT_MATCH
ORDERED_LIST_MATCH
UNORDERED_LIST_MATCH
SCHEMA_MATCH
FIELD_SUBSET_MATCH
NUMERIC_WITH_TOLERANCE
ARTIFACT_EXISTS
ARTIFACT_HASH_MATCH
FAILURE_CLASS_MATCH
SAFETY_POLICY_MATCH
REGEX_MATCH_RESTRICTED
MODEL_RUBRIC_SCORE
```

Subjective comparison is not allowed unless the case is explicitly model/rubric-based and non-blocking by default.

## 11.2 Comparator Rule Fields

Each comparator must define:

```text
comparator_id
comparator_type
expected_ref
actual_ref
normalization_rules
tolerance, if applicable
ignored_fields
required_fields
redaction_before_compare
case_sensitive, if text-based
ordering_required, if list-based
pass_condition
warnings
errors
```

## 11.3 Tolerance Rules

Tolerance is allowed only for comparator types that need it.

Rules:

```text
exact/schema/safety-policy comparisons cannot use tolerance to pass unsafe behavior
numeric tolerance must be declared before the run
model/rubric tolerance cannot override blocking deterministic failures
missing required fields cannot be tolerated
weaker policy/sandbox/tool safety cannot be accepted as equivalent
```

---

# 12. Evaluator Independence / Anti-Gaming Contract

## 12.1 Anti-Gaming Rules

The Evaluation Harness must resist benchmark gaming.

Forbidden behavior:

```text
modifying expected outputs during evaluation
refreshing baselines during evaluation
changing thresholds after seeing results
marking failed cases as skipped after execution
selecting easier suites for promotion claims
using local-only artifacts that are not recorded in evidence
allowing implementation code to detect and special-case benchmark IDs
allowing model prompts to include hidden answer keys unless the case is explicitly testing answer-key handling
```

## 12.2 Independence Requirements

Every evaluation run must record:

```text
current commit
suite version
case versions
dataset hashes
fixture hashes
baseline hash
threshold profile hash
scoring profile hash
runner version
```

The evaluator must use the committed suite/case/dataset/baseline definitions, not in-memory edits or unrecorded temporary definitions, for any final decision.

## 12.3 Golden Output Rules

Golden outputs may be used only if:

```text
they are versioned
they are hashed
they are tied to a case ID and case version
they are immutable during the run
they are not regenerated automatically to match current output
```

A mismatch against a golden output must be recorded as a case failure, regression finding, or accepted deviation.

---

# 13. Flaky Benchmark Quarantine Contract

## 13.1 Flaky Case Definition

A benchmark case is flaky when repeated runs under the same commit, suite, fixtures, datasets, and environment produce materially different pass/fail results without an intentional stochastic profile.

## 13.2 Quarantine Rule

Flaky cases must not silently pass or silently block. They must be classified as:

```text
CASE_NOT_REPRODUCIBLE
CASE_INSUFFICIENT_EVIDENCE
CASE_SKIPPED_DEFERRED, only if explicitly accepted as non-blocking
```

A flaky blocking case causes the run-level status to become `NOT_REPRODUCIBLE` or `INSUFFICIENT_EVIDENCE`.

## 13.3 Quarantine Record

A quarantine record must include:

```text
quarantine_id
case_id
case_version
first_observed_at
reproduction_attempts
observed_statuses
known_environment_factors
blocking
safety_critical
accepted_status
reviewer_decision
warnings
errors
```

Flaky safety-critical cases cannot be counted as passing evidence.

---

# 14. Regression Benchmark Contract



## 10.1 Benchmark Suite

A benchmark suite is a versioned collection of benchmark cases.

A suite must define:

```text
suite_id
suite_version
created_at
owner_component
purpose
scope
benchmark_cases
required_datasets
required_fixtures
required_baselines
scoring_profile
threshold_profile
expected_runtime_mode
isolation_mode
warnings
errors
```

## 10.2 Benchmark Case

Each benchmark case must define:

```text
case_id
case_version
case_type
purpose
input_refs
expected_behavior
expected_output_refs
scoring_method
thresholds
allowed_tools
blocked_tools
required_policy_context
required_sandbox_context
required_model_profile
expected_failure_class, if negative case
regression_sensitivity
blocking
stochastic
warnings
errors
```

## 10.3 Benchmark Case Types

Supported case types:

```text
SCHEMA_VALIDATION
POLICY_DECISION
SANDBOX_DECISION
TOOL_CALL
MCP_EXPOSURE
PATCH_SAFETY
FAILURE_CLASSIFICATION
REPORT_GENERATION
CONTEXT_PACKING
PROMPT_CONTRACT
MODEL_RESPONSE
ORCHESTRATOR_FLOW
END_TO_END_DRY_RUN
```

Case types that depend on future layers may exist as disabled or deferred cases, but must not silently pass.

## 10.4 Benchmark Determinism Rules

Benchmark cases must be deterministic unless explicitly marked as stochastic.

Default rules:

```text
no live network dependency
no clock-sensitive expected output unless time is injected
no random seed unless recorded
no unversioned external dataset
no hidden mutable fixture
no dependency on local user state
no dependency on GPU availability unless runtime profile says so
no dependency on provider model output unless model profile and tolerance rules are recorded
```

If a benchmark is stochastic, it must define:

```text
random_seed
sample_count
acceptable_variance
confidence_rule
stochastic_scoring_method
minimum_reproducible_summary
```

A stochastic benchmark cannot be a sole blocking promotion gate unless its tolerance and reproducibility rules are explicit.

---

# 15. Benchmark Isolation Contract

Every benchmark case must run in an isolated evaluation context.

Required isolation controls:

```text
case-specific run_id
case-specific working directory under .agentx-init/evaluation/runs/<run_id>/cases/<case_id>/
read-only access to canonical fixtures and datasets
runtime copies for generated outputs
environment metadata recorded
no access to user home state unless explicitly fixture-backed
no hidden dependency on current shell environment
```

Allowed writes:

```text
case runtime artifacts
case result JSON
case failure records
case stdout/stderr summaries, if command execution is allowed
case evidence references
```

Forbidden writes:

```text
source files
canonical datasets
canonical fixtures
accepted baselines
policy files
sandbox rules
tool registry files
model profiles
prompt contracts
Git state
```

---

# 16. Evaluation Dataset Contract

## 12.1 Dataset Requirements

Every benchmark dataset must be versioned and hashable.

A dataset must define:

```text
dataset_id
dataset_version
created_at
source_component
dataset_type
files
records
hash_algorithm
content_sha256
license_or_origin_note, if applicable
sensitive_data_flag
redaction_required
trusted_source_note
warnings
errors
```

## 12.2 Dataset Storage

Canonical dataset location:

```text
tools/agentx_evolve/evaluation/datasets/
```

Runtime copies or generated evaluation artifacts must be written under:

```text
.agentx-init/evaluation/
```

## 12.3 Dataset Safety Rules

Datasets must not contain:

```text
real secrets
private credentials
unredacted API keys
live personal data
unbounded prompt-injection payloads without explicit safety label
malicious files that execute during loading
binary executables used as benchmark inputs unless explicitly inert and justified
```

Prompt-injection or adversarial cases are allowed only as inert text fixtures with clear labels and no execution path.

## 12.4 Dataset Mutation Rules

The Evaluation Harness must not mutate canonical datasets during runs.

Allowed:

```text
read canonical dataset
copy dataset into runtime artifact area
write run outputs under .agentx-init/evaluation/
write derived hashes and summaries
```

Forbidden:

```text
modify canonical dataset files during evaluation
overwrite baseline datasets silently
normalize expected outputs in place
repair failing cases automatically
```

---

# 17. Fixture Contract

Benchmark fixtures are controlled static inputs used by benchmark cases.

A fixture must define:

```text
fixture_id
fixture_version
fixture_type
source_component
file_refs
content_sha256
intended_case_ids
sensitive_data_flag
adversarial_flag
execution_allowed
warnings
errors
```

Rules:

```text
fixtures are read-only
fixtures must be hash-checked before use
adversarial fixtures must be inert
fixtures must not execute during loading
fixture mutation invalidates the run
missing fixture hash causes INSUFFICIENT_EVIDENCE
```

---

# 18. Scoring / Threshold Contract

## 14.1 Score Types

Supported score types:

```text
BOOLEAN_PASS_FAIL
EXACT_MATCH
SCHEMA_VALIDITY
FIELD_MATCH
NUMERIC_SCORE
WEIGHTED_SCORE
REGRESSION_DELTA
FAILURE_CLASS_MATCH
ARTIFACT_PRESENCE
EVIDENCE_COMPLETENESS
SAFETY_INVARIANT
REPRODUCIBILITY_CHECK
```

## 14.2 Score Result

Each score result must include:

```text
score_id
case_id
run_id
score_type
raw_score
normalized_score
max_score
weight
passed
threshold_applied
scoring_method
blocking
safety_critical
warnings
errors
```

## 14.3 Threshold Profile

A threshold profile must define:

```text
threshold_profile_id
scope
minimum_total_score
minimum_required_cases_passed
maximum_regression_delta
maximum_critical_failures
required_case_ids
blocking_case_ids
warning_case_ids
safety_invariant_case_ids
warnings
errors
```

## 14.4 Threshold Decision

A threshold decision must include:

```text
threshold_decision_id
run_id
threshold_profile_id
total_score
required_cases_passed
blocking_cases_passed
safety_invariants_passed
regression_delta
critical_failures
status
reason
warnings
errors
```

Allowed threshold statuses:

```text
PASS
PASS_WITH_WARNINGS
FAIL
REGRESSION_DETECTED
INSUFFICIENT_EVIDENCE
NOT_REPRODUCIBLE
```

## 14.5 Scoring Rules

The layer must apply these rules:

```text
blocking case failure causes FAIL
safety invariant failure causes FAIL or REGRESSION_DETECTED
missing required score causes INSUFFICIENT_EVIDENCE
schema-invalid output scores zero for that case
critical safety regression causes REGRESSION_DETECTED
unreproducible case cannot be counted as PASS
manual override is not allowed in this layer
aggregate score cannot override a blocking failure
high aggregate score cannot hide critical safety failure
```

---

# 19. Baseline Comparison Contract

## 15.1 Baseline Snapshot

A baseline snapshot represents the accepted reference behavior for a benchmark suite.

It must include:

```text
baseline_id
baseline_version
created_at
source_commit
suite_id
suite_version
dataset_hashes
fixture_hashes
score_summary
case_results
artifact_refs
evidence_refs
hash_algorithm
baseline_sha256
approval_ref, if baseline is accepted
warnings
errors
```

## 15.2 Baseline Comparison

A baseline comparison must include:

```text
comparison_id
run_id
baseline_id
suite_id
current_commit
baseline_commit
score_delta
case_deltas
new_failures
resolved_failures
changed_failure_classes
artifact_differences
regression_findings
status
warnings
errors
```

Allowed comparison statuses:

```text
NO_REGRESSION
REGRESSION_DETECTED
IMPROVEMENT_DETECTED
BASELINE_MISSING
BASELINE_INVALID
COMPARISON_NOT_REPRODUCIBLE
```

## 15.3 Regression Detection Rules

A regression is detected when:

```text
a previously passing blocking case fails
normalized total score drops below allowed delta
critical failure count increases
safety failure appears in current run
failure class becomes more severe
required artifact is missing
schema-valid output becomes schema-invalid
MCP/tool/policy/sandbox behavior becomes less restrictive than baseline
reproducibility metadata becomes incomplete
required evidence hash disappears
```

## 15.4 Baseline Mutation Rules

The Evaluation Harness must not update baselines automatically.

Allowed:

```text
read baseline
compare current run to baseline
write comparison artifact
recommend baseline update as separate review item
```

Forbidden:

```text
overwrite baseline after a passing run
accept a new baseline without review
hide regression by refreshing baseline
mutate baseline files during evaluation
```

---

# 20. Failure Classification Contract

## 16.1 Evaluation Failure Classes

The layer must classify failures using standard classes.

Required evaluation failure classes:

```text
EVAL_SCHEMA_INVALID
EVAL_DATASET_INVALID
EVAL_FIXTURE_INVALID
EVAL_BASELINE_MISSING
EVAL_BASELINE_INVALID
EVAL_SCORE_CALCULATION_FAILED
EVAL_THRESHOLD_FAILED
EVAL_REGRESSION_DETECTED
EVAL_REQUIRED_ARTIFACT_MISSING
EVAL_EVIDENCE_WRITE_FAILED
EVAL_COMMAND_FAILED
EVAL_TOOL_CALL_FAILED
EVAL_POLICY_DENIED
EVAL_SANDBOX_DENIED
EVAL_MODEL_RUNTIME_UNAVAILABLE
EVAL_NOT_REPRODUCIBLE
EVAL_UNSUPPORTED_CASE_TYPE
EVAL_UNTRUSTED_INPUT
EVAL_MUTATION_DETECTED
EVAL_INTERNAL_ERROR
```

## 16.2 Failure Severity

Allowed severity levels:

```text
INFO
WARNING
NON_BLOCKING
HIGH
BLOCKER
CRITICAL
```

## 16.3 Failure Record

Every failure record must include:

```text
failure_id
run_id
case_id, if applicable
failure_class
severity
message
source_component
artifact_refs
evidence_refs
recovery_hint
blocking
warnings
errors
```

## 16.4 Failure Rules

Failures must be recorded when:

```text
a benchmark case fails
a required input is missing
a schema is invalid
a score cannot be calculated
a threshold fails
a regression is detected
evidence cannot be written
a tool call returns BLOCKED, FAILED, or INVALID
a command exits non-zero unexpectedly
canonical dataset mutation is detected
baseline mutation is detected
source mutation is detected
```

---

# 21. Artifact / Evidence Contract

## 17.1 Runtime Artifact Root

All runtime artifacts for this layer must be written under:

```text
.agentx-init/evaluation/
```

Recommended run-specific layout:

```text
.agentx-init/evaluation/runs/<run_id>/evaluation_run.json
.agentx-init/evaluation/runs/<run_id>/evaluation_result.json
.agentx-init/evaluation/runs/<run_id>/score_summary.json
.agentx-init/evaluation/runs/<run_id>/threshold_decision.json
.agentx-init/evaluation/runs/<run_id>/baseline_comparison.json
.agentx-init/evaluation/runs/<run_id>/regression_findings.json
.agentx-init/evaluation/runs/<run_id>/evaluation_failures.jsonl
.agentx-init/evaluation/runs/<run_id>/evaluation_evidence_manifest.json
.agentx-init/evaluation/runs/<run_id>/evaluation_report.md
.agentx-init/evaluation/latest_evaluation_run.json
.agentx-init/evaluation/latest_evaluation_result.json
```

## 17.2 Evidence Manifest

Every run must create:

```text
.agentx-init/evaluation/runs/<run_id>/evaluation_evidence_manifest.json
```

Required fields:

```text
schema_version
schema_id
component_id
run_id
suite_id
suite_version
validated_commit
validated_at
review_environment
benchmark_inputs
dataset_hashes
fixture_hashes
baseline_refs
commands_run
tools_called
model_profiles_used
artifacts_generated
artifact_hashes
score_summary_ref
threshold_decision_ref
baseline_comparison_ref
failure_refs
deviation_refs
final_status
warnings
errors
```

## 17.3 Hashing Rules

All final evidence artifacts must have SHA-256 hashes.

Required hashes:

```text
benchmark suite file hash
benchmark case file hashes
dataset file hashes
fixture file hashes
baseline snapshot hash
evaluation run artifact hash
evaluation result hash
score summary hash
threshold decision hash
baseline comparison hash
regression findings hash
failure log hash
evidence manifest hash
report hash, if report exists
latest artifact hashes, if used by review
```

Use Python standard-library `hashlib` if no project hash helper exists.

## 17.4 Evidence Manifest Self-Hash Rule

Because a file cannot contain its final hash without changing that hash, the manifest must use one of these valid approaches:

```text
Approach A: evidence manifest contains hashes of all other artifacts, and a sidecar .sha256 file stores the manifest hash.
Approach B: evidence manifest contains a hash field explicitly set to null during hashing, with canonical hashing rules documented.
```

The implementation spec must choose one approach and test it.

## 17.5 Evidence Immutability Rule

After final evaluation status is written:

```text
evidence artifacts must not be modified in place
a changed hash invalidates the prior evaluation result
new evidence requires a new run_id
baseline updates require separate review
manual edits must be recorded as deviations
```

---

# 22. Deviation Register

Any accepted exception must be recorded.

Deviation record fields:

```text
deviation_id
run_id
area
requirement
description
reason
safety_impact
compensating_control
accepted_status
reviewer_decision
warnings
errors
```

Rules:

```text
BLOCKER deviations cannot be accepted for PASS.
CRITICAL safety deviations cannot be accepted for PASS.
Missing evidence hashes cannot be accepted for PASS.
Baseline mutation cannot be accepted for PASS.
Source mutation cannot be accepted for PASS.
Network use without explicit runtime profile cannot be accepted for PASS.
```

---

# 23. Evaluation Run Recording Contract

## 19.1 Evaluation Run

An evaluation run must include:

```text
run_id
schema_version
schema_id
created_at
source_component
suite_id
suite_version
benchmark_case_ids
dataset_refs
fixture_refs
baseline_refs
current_commit
runtime_mode
policy_context_ref
sandbox_context_ref
model_profile_refs
commands_run
tools_called
isolation_mode
warnings
errors
```

## 19.2 Evaluation Result

An evaluation result must include:

```text
result_id
run_id
created_at
source_component
case_results
score_summary
threshold_decision
baseline_comparison
regression_findings
failures
artifact_refs
evidence_refs
final_status
warnings
errors
```

Allowed final statuses:

```text
PASS
PASS_WITH_WARNINGS
FAIL
REGRESSION_DETECTED
INSUFFICIENT_EVIDENCE
NOT_REPRODUCIBLE
BLOCKED
SCHEMA_INVALID
UNTRUSTED_INPUT
```

## 19.3 Command Recording

If this layer executes commands, each command record must include:

```text
command_id
command
working_directory
exit_code
status
started_at
ended_at
stdout_summary
stderr_summary
output_artifact
output_sha256
warnings
errors
```

Command output must be bounded and redacted.

Commands must not run through raw shell. They must use an allowlisted command runner or Tool / MCP Adapter-controlled command path.

## 19.4 Tool Call Recording

If this layer invokes registered tools, each tool-call record must include:

```text
tool_call_id
tool_name
caller_role
requested_effect
status
result_ref
evidence_refs
policy_decision_ref
sandbox_decision_ref, if applicable
warnings
errors
```

Tool calls must go through Tool / MCP Adapter unless the benchmark is a fixture-only unit test.

---

# 24. What This Layer Is Allowed to Evaluate

This layer may evaluate:

```text
schema validity
benchmark fixture stability
tool registry behavior
tool permission behavior
MCP exposure behavior
sandbox restriction behavior
policy decision behavior
failure taxonomy mapping
patch safety behavior
context packing behavior
prompt contract behavior
model adapter behavior
local model runtime behavior
orchestrator dry-run behavior
report generation behavior
regression against baseline
```

This layer may not evaluate by guessing user intent, manually overriding safety rules, or changing the thing being evaluated during the run.

---

# 25. What This Layer Must Never Mutate

The Evaluation Harness must never mutate:

```text
source code under evaluation
canonical benchmark datasets
canonical benchmark fixtures
accepted baselines
policy registry definitions
security sandbox rules
tool registry definitions
model profiles
prompt contracts
Git branches/tags/commits
promotion records
human approval records
```

Allowed writes are limited to runtime evaluation artifacts under:

```text
.agentx-init/evaluation/
```

and only when those writes are evidence/report outputs from the current evaluation run.

---

# 26. Schema Contract Summary

The implementation spec must define exact JSON schemas for:

```text
evaluation_suite.schema.json
benchmark_case.schema.json
benchmark_dataset.schema.json
benchmark_fixture.schema.json
evaluation_run.schema.json
evaluation_result.schema.json
case_result.schema.json
score_result.schema.json
threshold_profile.schema.json
threshold_decision.schema.json
baseline_snapshot.schema.json
baseline_comparison.schema.json
regression_finding.schema.json
evaluation_failure.schema.json
evaluation_evidence_manifest.schema.json
evaluation_report.schema.json
evaluation_deviation.schema.json
```

Each schema must:

```text
require schema_version
require schema_id
require source_component where applicable
require warnings
require errors
define enum values for statuses and failure classes
reject missing required fields
reject invalid enum values
support artifact_refs and evidence_refs where applicable
support hash/provenance fields where applicable
```

---

# 27. Public API Contract

Expected public classes or dataclasses:

```text
EvaluationSuite
BenchmarkCase
BenchmarkDataset
BenchmarkFixture
EvaluationRun
EvaluationResult
CaseResult
ScoreResult
ThresholdProfile
ThresholdDecision
BaselineSnapshot
BaselineComparison
RegressionFinding
EvaluationFailure
EvaluationEvidenceManifest
EvaluationDeviation
```

Expected public functions:

```python
load_evaluation_suite(suite_path: Path) -> EvaluationSuite
load_benchmark_dataset(dataset_path: Path) -> BenchmarkDataset
load_benchmark_fixture(fixture_path: Path) -> BenchmarkFixture
validate_evaluation_suite(suite: EvaluationSuite) -> list[EvaluationFailure]
validate_benchmark_case(case: BenchmarkCase) -> list[EvaluationFailure]
validate_dataset(dataset: BenchmarkDataset) -> list[EvaluationFailure]
validate_fixture(fixture: BenchmarkFixture) -> list[EvaluationFailure]
run_evaluation_suite(suite: EvaluationSuite, context: dict) -> EvaluationResult
run_benchmark_case(case: BenchmarkCase, context: dict) -> CaseResult
calculate_scores(case_results: list[CaseResult], threshold_profile: ThresholdProfile) -> list[ScoreResult]
apply_thresholds(scores: list[ScoreResult], threshold_profile: ThresholdProfile) -> ThresholdDecision
load_baseline_snapshot(baseline_path: Path) -> BaselineSnapshot
compare_to_baseline(result: EvaluationResult, baseline: BaselineSnapshot) -> BaselineComparison
detect_regressions(comparison: BaselineComparison, threshold_profile: ThresholdProfile) -> list[RegressionFinding]
classify_evaluation_failure(raw_failure: dict) -> EvaluationFailure
write_evaluation_evidence(result: EvaluationResult, repo_root: Path) -> EvaluationEvidenceManifest
write_evaluation_report(result: EvaluationResult, repo_root: Path) -> Path
```

---

# 28. Evaluation Pipeline

Every evaluation run must follow this sequence:

```text
1. Receive suite request.
2. Resolve evaluation suite.
3. Validate suite schema.
4. Resolve benchmark cases.
5. Validate benchmark case schemas.
6. Resolve datasets.
7. Validate dataset hashes.
8. Resolve fixtures.
9. Validate fixture hashes.
10. Resolve baseline snapshot, if required.
11. Validate baseline hash.
12. Create isolated EvaluationRun record.
13. Run benchmark cases in deterministic order.
14. Record each case result.
15. Classify failures.
16. Calculate scores.
17. Apply thresholds.
18. Compare to baseline.
19. Detect regressions.
20. Write evaluation result.
21. Write evidence manifest.
22. Write report, if enabled.
23. Write latest evaluation artifacts atomically.
24. Return final status.
```

No step may be silently skipped if it is required by the suite.

---

# 29. Regression Safety Rules

Regression detection must fail closed.

A run must not be marked `PASS` when:

```text
baseline is required but missing
baseline is schema-invalid
baseline hash does not match
current run is not reproducible
blocking case failed
critical failure increased
safety behavior became less restrictive
score dropped beyond threshold
required artifact is missing
required evidence hash is missing
```

A run may be marked `PASS_WITH_WARNINGS` only when:

```text
all blocking cases pass
no critical regression exists
all required evidence exists
warnings are non-blocking and recorded
```

---

# 30. Reproducibility Rules

Each evaluation run must record:

```text
current commit
suite version
case versions
dataset hashes
fixture hashes
baseline hash
Python version
OS information
runtime mode
random seed, if applicable
commands run with exit codes
registered tools called, if applicable
model/runtime profile, if applicable
artifact hashes
```

A run is not reproducible if any required reproducibility field is missing.

---

# 31. Security Rules

This layer must enforce:

```text
no source mutation
no baseline mutation
no canonical dataset mutation
no canonical fixture mutation
no raw shell execution
no network by default
no Git write
no promotion decision
no policy bypass
no sandbox bypass
no tool execution bypass
no unredacted secret logging
no hidden benchmark input mutation
no subjective unrecorded scoring
no automatic baseline refresh
```

---

# 32. Test Acceptance Criteria

Required tests must prove:

```text
evaluation suite schema accepts valid suite
evaluation suite schema rejects missing suite_id
benchmark case schema accepts valid case
benchmark case schema rejects invalid case_type
dataset schema requires hash
fixture schema requires hash
baseline comparison detects missing baseline
score calculator applies exact-match score
threshold checker fails blocking case failure
threshold checker fails safety invariant failure
regression detector catches score drop
regression detector catches new critical failure
regression detector catches less restrictive safety behavior
failure classifier maps known failures
evidence writer creates manifest
artifact hashes are written
manifest self-hash rule works
latest artifacts are written atomically
canonical datasets are not mutated
canonical fixtures are not mutated
baselines are not mutated
source files are not mutated
network benchmark is blocked by default
command execution is blocked unless allowlisted
tool benchmarks go through Tool / MCP Adapter or fixture-only mode
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema tests PASS
benchmark fixture tests PASS
scoring tests PASS
threshold tests PASS
baseline comparison tests PASS
regression detection tests PASS
evidence tests PASS
source mutation check PASS
```

---

# 33. Runtime Artifact Rules

Runtime artifacts must be under:

```text
.agentx-init/evaluation/
```

Rules:

```text
append JSONL for failure history
write latest JSON atomically
redact secrets before persistence
write SHA-256 hashes for final artifacts
preserve prior run artifacts
use unique run_id for each new evaluation
never overwrite baseline or canonical dataset files
never overwrite canonical fixtures
```

---

# 34. Fresh-Clone Reproducibility Gate

Final acceptance requires validation from a clean checkout or clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_evaluation_schemas.py
git status --short
```

Required result:

```text
initial git status: clean or expected runtime artifacts only
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
final git status: clean or expected runtime artifacts only
```

A final `PASS` or `DONE` claim is invalid if the reviewed commit, command text, command exit codes, Python version, and final git status are not recorded in evidence.

---

# 35. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is selected
[ ] runtime artifact root is selected
[ ] evaluation suite schema is defined
[ ] benchmark case schema is defined
[ ] benchmark dataset schema is defined
[ ] benchmark fixture schema is defined
[ ] evaluation run/result schemas are defined
[ ] scoring rules are defined
[ ] threshold rules are defined
[ ] baseline comparison rules are defined
[ ] regression detection rules are defined
[ ] failure classes are defined
[ ] evidence manifest contract is defined
[ ] manifest self-hash rule is selected
[ ] non-mutation rules are defined
[ ] dependency gates are defined
[ ] Agent_X integration boundaries are defined
[ ] OpenCode borrowing is bounded
```

---

# 36. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] evaluation suite validates
[ ] benchmark datasets validate
[ ] benchmark fixtures validate
[ ] scoring works
[ ] threshold checks work
[ ] baseline comparison works
[ ] regression detection works
[ ] evidence records are written
[ ] artifact hashes are written
[ ] evidence self-hash rule passes
[ ] source mutation check passes
[ ] canonical dataset mutation check passes
[ ] canonical fixture mutation check passes
[ ] baseline mutation check passes
```

---

# 37. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_EVALUATION_HARNESS"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  validated_commit: "<commit hash>"
  validated_at: "<UTC timestamp>"
  review_environment: {}
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  benchmark_suites_validated: []
  benchmark_cases_validated: []
  datasets_validated: []
  fixtures_validated: []
  baselines_compared: []
  scores_calculated: []
  thresholds_applied: []
  regressions_detected: []
  evidence_artifacts_created: []
  artifact_hashes: []
  deviations_from_contract: []
  unresolved_risks: []
  final_decision: "DONE|NOT_DONE"
```

---

# 38. Residual Risks

```yaml
residual_risks:
  - id: "EVAL-RISK-001"
    description: "Benchmarks may become too broad or vague to detect real regressions."
    severity: "high"
    mitigation: "Use versioned benchmark cases with explicit expected behavior, scoring method, thresholds, and blocking status."
  - id: "EVAL-RISK-002"
    description: "Baseline updates could hide regressions."
    severity: "critical"
    mitigation: "Evaluation Harness must not update baselines automatically; baseline changes require separate review."
  - id: "EVAL-RISK-003"
    description: "Non-deterministic tests could produce unstable pass/fail outcomes."
    severity: "high"
    mitigation: "Require dataset hashes, fixture hashes, random seeds, environment metadata, and reproducibility fields."
  - id: "EVAL-RISK-004"
    description: "Evaluation may accidentally mutate source, datasets, fixtures, or baselines."
    severity: "critical"
    mitigation: "Runtime writes are restricted to .agentx-init/evaluation/ and mutation checks are required."
  - id: "EVAL-RISK-005"
    description: "Scoring may hide critical safety failures behind high aggregate scores."
    severity: "critical"
    mitigation: "Blocking cases, safety invariants, and critical failures override aggregate score."
  - id: "EVAL-RISK-006"
    description: "Model-based benchmarks may be unstable across local hardware or model versions."
    severity: "medium"
    mitigation: "Model cases require runtime profile, seed/tolerance rules, and cannot be sole blocking gates unless reproducible."
```

---

# 39. Definition of Done

This layer is done when it can act as Agent_X's deterministic benchmark and regression evaluation boundary.

It must prove:

```text
evaluation suites are schema-valid
benchmark cases are schema-valid
datasets are versioned and hashed
fixtures are versioned and hashed
baselines are versioned and hashed
evaluation runs are recorded
scores are calculated deterministically
thresholds are applied correctly
safety invariants override aggregate score
regressions are detected against baseline
failures are classified consistently
evidence manifests are written
artifact hashes are written
manifest self-hash rule is implemented
reports are generated if enabled
canonical datasets are not mutated
canonical fixtures are not mutated
baselines are not mutated
source files are not mutated
no network is enabled by default
no raw shell is executed
no Git write is performed
no promotion decision is made directly by this layer
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_evaluation_schemas.py
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
```

---

# 40. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
benchmark dataset hash is missing
benchmark fixture hash is missing
baseline hash is missing when baseline is required
blocking case failure is ignored
safety invariant failure is ignored
score calculation is unstructured
threshold failure is ignored
regression detection is skipped
baseline is updated automatically
canonical dataset is mutated
canonical fixture is mutated
source file is mutated
network is enabled by default
raw shell is executed
Git write occurs
promotion decision is made directly by this layer
evidence manifest is missing
artifact hashes are missing
manifest self-hash rule is missing
unredacted secrets are logged
```

---

# 41. Final Freeze Rule

This v3 document is frozen as the controlling contract for the Evaluation Harness / Regression Benchmark Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional implementation-spec details
MAJOR: changed status vocabulary, changed scoring semantics, changed baseline mutation policy, changed default network/tool/model execution behavior, new required benchmark family
```

Blocked without major revision:

```text
allowing automatic baseline refresh
allowing aggregate score to override blocking safety failures
removing evidence hashing
removing non-mutation checks
allowing raw shell execution
allowing network by default
allowing Git write
allowing source mutation
allowing canonical dataset or fixture mutation
allowing promotion decision directly in this layer
```

The next document should be:

```text
EVALUATION_HARNESS_IMPLEMENTATION_SPEC.md
```

---

# 42. Final Rating

This v3 controlling contract is rated:

```text
10/10
```

Reason:

```text
It defines the Evaluation Harness / Regression Benchmark Layer with EQC, FIC, SIB, schema contracts, benchmark contracts, dataset and fixture contracts, benchmark selection and coverage rules, comparator rules, scoring and threshold rules, baseline comparison rules, flaky benchmark quarantine, anti-gaming controls, failure classification, artifact/evidence requirements, dependency gates, isolation rules, Agent_X integration boundaries, OpenCode borrowing limits, non-mutation rules, fresh-clone reproducibility rules, no-go conditions, freeze rules, acceptance criteria, and Definition of Done.
```
