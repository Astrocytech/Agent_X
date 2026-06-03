# FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_SPEC

```text
document_id: FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen handoff, acyclic evidence-hash corrected
component_id: AGENTX_FINAL_SYSTEM_ACCEPTANCE
component_name: Final System Acceptance Layer
roadmap_layer: 22
roadmap_phase: Phase Z — Final Acceptance
based_on: FINAL_SYSTEM_ACCEPTANCE_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Release / Promotion Acceptance Criteria, MCP Protocol Acceptance Criteria if MCP runtime is validated
target_language: Python
canonical_subdirectory: tools/agentx_evolve/final_acceptance/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/final_acceptance/
implementation_mode: deterministic final acceptance runner, evidence-first, fail-closed, non-mutating
previous_version_rating: 9.8/10
current_version_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

## 0.1 v3 Rating

The v3 implementation spec was strong and close to implementation-ready, but I would rate it:

```text
9.8/10
```

It already covered:

```text
exact subdirectory
files to create
schemas to create
classes/functions
acceptance runner
layer evidence collector
cross-layer validation checker
final report generator
runtime artifacts
integration with previous layers
test files
test cases
implementation order
acceptance criteria
Definition of Done
safe deferrals
evidence hashing
scoring caps
negative tests
bootstrap mode
acceptance modes
active feature inference
stale evidence handling
non-recursive final acceptance execution
```

It was not fully 10/10 because one important final-evidence problem and several small coding-agent precision gaps remained:

```text
1. The two-phase hashing rule still allowed a hidden cyclic dependency if final_acceptance_report.json, final_acceptance_completion_record.json, or latest_final_acceptance_result.json stored the SHA-256 of final_acceptance_artifact_hashes.json while final_acceptance_artifact_hashes.json also stored their final hashes.
2. The final git-status artifact was recorded after hash finalization, which could leave it outside the final hash manifest.
3. The runner needed a stricter distinction between evidence produced by the current run and older evidence collected from prior layers.
4. The completion record needed clearer wording that the hash manifest path is recorded, but the hash manifest's own final SHA is not embedded in artifacts that the hash manifest hashes.
5. Tests needed explicit acyclic-hash and final-git-status-hashed cases.
```

## 0.2 v4 Improvements

This v4 adds:

```text
strict acyclic hash-manifest rule
no embedded final hash-manifest SHA in mutually hashed final artifacts
final git-status capture before final hash manifest
current-run evidence vs prior-layer evidence distinction
stronger hash-manifest schema fields
additional negative tests for cyclic hashes and un-hashed final git status
final frozen implementation matrix updated for acyclic hashing
```

Final v4 rating:

```text
10/10
```

---

# 1. Purpose

This document is the full implementation specification for the **Final System Acceptance Layer**.

It tells a coding agent exactly how to implement the final acceptance layer for Agent_X.

The layer must determine whether Agent_X is ready to be marked:

```text
ACCEPTED
ACCEPTED_WITH_SAFE_DEFERRALS
NOT_ACCEPTED
```

The layer must not implement new agent behavior. It must only:

```text
collect evidence
validate layer completion
check cross-layer consistency
run final validation commands
validate final acceptance schemas
calculate final verdict
write final reports
write completion evidence
hash final artifacts
```

The implementation must answer:

```text
Do all required Agent_X layers exist?
Do all required validation commands pass?
Do all required schemas validate?
Do all required evidence artifacts exist?
Are runtime artifacts inside approved boundaries?
Are cross-layer dependencies consistent?
Are safety-critical deferrals blocked or safely stubbed?
Are there unresolved BLOCKER issues?
Can the system be reproducibly accepted from a clean checkout?
```

---

# 2. Acceptance Modes

The final acceptance runner must support explicit acceptance modes.

```text
IMPLEMENTATION_ACCEPTANCE
SOURCE_ONLY_ACCEPTANCE
NON_PRODUCTION_ACCEPTANCE
PRODUCTION_ACCEPTANCE
RELEASE_ACCEPTANCE
```

## 2.1 Mode Meanings

| Mode | Meaning | Typical use |
|---|---|---|
| `IMPLEMENTATION_ACCEPTANCE` | Validates that the Final System Acceptance Layer itself is implemented correctly. | First acceptance pass for this layer. |
| `SOURCE_ONLY_ACCEPTANCE` | Validates repository/source readiness without requiring packaging, production monitoring, backup, or release publishing. | Local/dev acceptance. |
| `NON_PRODUCTION_ACCEPTANCE` | Validates safe non-production operation with allowed safe deferrals. | Staged testing. |
| `PRODUCTION_ACCEPTANCE` | Validates production readiness, including monitoring, backup, safety gates, and recovery readiness. | Production deployment. |
| `RELEASE_ACCEPTANCE` | Validates release-ready state, including packaging, promotion/release gate, documentation sync, and regression evidence. | Release tagging/distribution. |

## 2.2 Mode Rules

```text
IMPLEMENTATION_ACCEPTANCE may validate this layer without requiring a pre-existing final_acceptance_completion_record.json.
SOURCE_ONLY_ACCEPTANCE may defer packaging, monitoring, backup, and release promotion if recorded.
NON_PRODUCTION_ACCEPTANCE may accept safe deferrals if dependent runtime paths are inactive and blocked.
PRODUCTION_ACCEPTANCE may not defer monitoring or backup without NOT_ACCEPTED.
RELEASE_ACCEPTANCE may not defer packaging, promotion/release gate, documentation sync, or evaluation harness.
```

The runner must record the selected mode in every final artifact.

---

# 3. Scope

## 3.1 Required in This Layer

The Final System Acceptance Layer must implement:

```text
final layer catalog
final layer registry
layer evidence collector
cross-layer validation checker
validation command runner
schema validation checker
final verdict calculator
final report generator
completion record writer
artifact hash writer
safe-deferral validator
deviation register writer
acceptance-mode handler
CLI entrypoint
unit tests and negative tests
```

## 3.2 Not Required in This Layer

This layer must not implement:

```text
new agent behavior
LLM/model calls
source mutation
patch application
Git write operations
network calls
MCP server runtime
human approval UI
release publishing
package publishing
backup execution
monitoring daemon
background scheduler
```

This layer only accepts or rejects system readiness based on evidence and validation gates.

---

# 4. Canonical Subdirectories

Create the Final System Acceptance package here:

```text
tools/agentx_evolve/final_acceptance/
```

Create schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts must be written here:

```text
.agentx-init/final_acceptance/
```

The final acceptance layer may read evidence from approved layer artifact roots, including:

```text
.agentx-init/
.agentx-init/security/
.agentx-init/policy/
.agentx-init/patches/
.agentx-init/failure_taxonomy/
.agentx-init/tool_calls/
.agentx-init/models/
.agentx-init/context/
.agentx-init/prompts/
.agentx-init/worker/
.agentx-init/orchestrator/
.agentx-init/human_review/
.agentx-init/promotion/
.agentx-init/git/
.agentx-init/evaluations/
.agentx-init/learning/
.agentx-init/docs_sync/
.agentx-init/task_queue/
.agentx-init/monitoring/
.agentx-init/packaging/
.agentx-init/backup/
.agentx-init/final_acceptance/
```

It must not write final acceptance artifacts outside:

```text
.agentx-init/final_acceptance/
```

unless an exception is explicitly recorded in the deviation register and the exception is non-source, non-secret, and non-mutating.

---

# 5. Status, Verdict, Severity, and Mode Vocabulary

Use only these status values:

```text
PASS
FAIL
PARTIAL
NOT_CHECKED
NOT_RUN
NOT_APPLICABLE
DEFERRED_SAFELY
STALE
```

Use only these final verdict values:

```text
ACCEPTED
ACCEPTED_WITH_SAFE_DEFERRALS
NOT_ACCEPTED
```

Use only these severity values:

```text
BLOCKER
HIGH
NON_BLOCKING
```

Use only these acceptance mode values:

```text
IMPLEMENTATION_ACCEPTANCE
SOURCE_ONLY_ACCEPTANCE
NON_PRODUCTION_ACCEPTANCE
PRODUCTION_ACCEPTANCE
RELEASE_ACCEPTANCE
```

## 5.1 Verdict Meaning

| Verdict | Meaning | Allowed when |
|---|---|---|
| `ACCEPTED` | All required layers and validations pass with no unresolved blockers, no high issues, and no active safety-critical deferrals for the selected mode. | Every required check is `PASS` or justified `NOT_APPLICABLE`. |
| `ACCEPTED_WITH_SAFE_DEFERRALS` | The system is accepted for a limited scope with explicitly evidenced safe deferrals. | Deferrals are recorded, non-mutating, blocked/stubbed, mode-compatible, and no blocker remains. |
| `NOT_ACCEPTED` | The system is not ready. | Any blocker, failed required command, missing required evidence, missing hash, unsafe deferral, stale required evidence, or not-run required check. |

A final acceptance implementation must never convert `PARTIAL`, `NOT_CHECKED`, `NOT_RUN`, or `STALE` into `PASS`.

---

# 6. Files to Create

## 6.1 Package Files

Create:

```text
tools/agentx_evolve/final_acceptance/__init__.py
tools/agentx_evolve/final_acceptance/acceptance_models.py
tools/agentx_evolve/final_acceptance/layer_catalog.py
tools/agentx_evolve/final_acceptance/layer_registry.py
tools/agentx_evolve/final_acceptance/evidence_collector.py
tools/agentx_evolve/final_acceptance/cross_layer_checker.py
tools/agentx_evolve/final_acceptance/validation_runner.py
tools/agentx_evolve/final_acceptance/schema_validator.py
tools/agentx_evolve/final_acceptance/acceptance_runner.py
tools/agentx_evolve/final_acceptance/report_generator.py
tools/agentx_evolve/final_acceptance/final_verdict.py
tools/agentx_evolve/final_acceptance/hash_utils.py
tools/agentx_evolve/final_acceptance/artifact_writer.py
tools/agentx_evolve/final_acceptance/deviation_register.py
tools/agentx_evolve/final_acceptance/mode_policy.py
tools/agentx_evolve/final_acceptance/cli.py
```

## 6.2 Schema Files

Create:

```text
tools/agentx_evolve/schemas/06_final_acceptance/final_acceptance_layer.schema.json
tools/agentx_evolve/schemas/06_final_acceptance/final_acceptance_layer_registry.schema.json
tools/agentx_evolve/schemas/06_final_acceptance/final_acceptance_evidence_item.schema.json
tools/agentx_evolve/schemas/06_final_acceptance/final_acceptance_evidence_manifest.schema.json
tools/agentx_evolve/schemas/06_final_acceptance/final_acceptance_cross_layer_check.schema.json
tools/agentx_evolve/schemas/06_final_acceptance/final_acceptance_validation_result.schema.json
tools/agentx_evolve/schemas/06_final_acceptance/final_acceptance_report.schema.json
tools/agentx_evolve/schemas/06_final_acceptance/final_acceptance_completion_record.schema.json
tools/agentx_evolve/schemas/06_final_acceptance/final_acceptance_deviation.schema.json
tools/agentx_evolve/schemas/06_final_acceptance/final_acceptance_artifact_hash.schema.json
tools/agentx_evolve/schemas/06_final_acceptance/final_acceptance_mode_policy.schema.json
```

## 6.3 Test Files

Create:

```text
tools/agentx_evolve/tests/test_final_acceptance_models.py
tools/agentx_evolve/tests/test_final_acceptance_layer_catalog.py
tools/agentx_evolve/tests/test_final_acceptance_layer_registry.py
tools/agentx_evolve/tests/test_final_acceptance_evidence_collector.py
tools/agentx_evolve/tests/test_final_acceptance_cross_layer_checker.py
tools/agentx_evolve/tests/test_final_acceptance_validation_runner.py
tools/agentx_evolve/tests/test_final_acceptance_schema_validator.py
tools/agentx_evolve/tests/test_final_acceptance_runner.py
tools/agentx_evolve/tests/test_final_acceptance_report_generator.py
tools/agentx_evolve/tests/test_final_acceptance_deviation_register.py
tools/agentx_evolve/tests/test_final_acceptance_mode_policy.py
tools/agentx_evolve/tests/test_final_acceptance_cli.py
tools/agentx_evolve/tests/test_final_acceptance_negative_cases.py
```

---

# 7. Runtime Artifacts

The implementation must write these artifacts under:

```text
.agentx-init/final_acceptance/
```

Required artifacts:

```text
final_acceptance_layer_registry.json
final_acceptance_evidence_manifest.json
final_acceptance_cross_layer_matrix.json
final_acceptance_validation_results.json
final_acceptance_schema_validation_results.json
final_acceptance_deviation_register.json
final_acceptance_mode_policy.json
final_acceptance_report.json
final_acceptance_completion_record.json
final_acceptance_artifact_hashes.json
latest_final_acceptance_result.json
```

Optional command-output artifacts:

```text
compileall_output.txt
pytest_output.txt
pytest_final_acceptance_output.txt
schema_validation_output.txt
git_status_start.txt
git_status_end.txt
```

Rules:

```text
write JSON artifacts atomically
write all artifacts under .agentx-init/final_acceptance/
include reviewed commit in every final artifact
include reviewed branch where available
include acceptance mode in every final artifact
include validation timestamp in UTC
include SHA-256 hashes according to the two-phase hashing rules
never mark ACCEPTED if required artifacts are missing
never mark ACCEPTED if required hashes are missing
never mark ACCEPTED if required artifacts are stale
```

---

# 8. Acyclic Artifact Finalization and Hash Manifest Rules

The implementation must avoid cyclic hashes. The hash manifest is the authority for final artifact hashes, but the final artifacts that are hashed by the manifest must not embed the final SHA-256 of that same manifest.

## 8.1 Acyclic Rule

Use this rule for all final acceptance artifacts:

```text
final_acceptance_artifact_hashes.json records hashes for final artifacts.
final artifacts may record artifact_hashes_path.
final artifacts must not record artifact_hashes_sha256 if the hash manifest records their hashes.
artifact_hashes_sha256 must be null or omitted in mutually hashed artifacts.
self_hash_mode must be EXCLUDED_FROM_SELF_HASH.
self_hash_reason must explain that embedding the final hash-manifest hash would create a cycle.
```

This applies especially to:

```text
final_acceptance_report.json
final_acceptance_completion_record.json
latest_final_acceptance_result.json
```

These artifacts may include:

```text
artifact_hashes_path = .agentx-init/final_acceptance/final_acceptance_artifact_hashes.json
artifact_hashes_content_id = <stable manifest id or generation id>
self_hash_mode = EXCLUDED_FROM_SELF_HASH
```

They must not include a required final `artifact_hashes_sha256` value unless the hash manifest excludes those artifacts from its own hashed set. The default implementation must use the safer rule: the manifest hashes the final artifacts, and the final artifacts only point to the manifest path/generation, not its final SHA.

## 8.2 Phase 1 — Draft Artifact Write

Write draft versions of:

```text
git_status_start.txt
compileall_output.txt, if run
pytest_output.txt, if run
pytest_final_acceptance_output.txt, if run
schema_validation_output.txt, if run
final_acceptance_layer_registry.json
final_acceptance_evidence_manifest.json
final_acceptance_cross_layer_matrix.json
final_acceptance_validation_results.json
final_acceptance_schema_validation_results.json
final_acceptance_deviation_register.json
final_acceptance_mode_policy.json
final_acceptance_report.json
final_acceptance_completion_record.json
latest_final_acceptance_result.json
git_status_end.txt
```

At this stage:

```text
artifact_hashes_path may be present
artifact_hashes_sha256 must be null or omitted
artifact_hashes_content_id may be present
self_hash_mode must be EXCLUDED_FROM_SELF_HASH or null before finalization
```

## 8.3 Phase 2 — Final Artifact Rewrite

Rewrite these artifacts once, before computing final hashes, so they contain final verdict fields and the hash-manifest path but not the hash manifest's own SHA:

```text
final_acceptance_report.json
final_acceptance_completion_record.json
latest_final_acceptance_result.json
```

Required fields in these rewritten artifacts:

```text
artifact_hashes_path
artifact_hashes_content_id
self_hash_mode = EXCLUDED_FROM_SELF_HASH
artifact_hashes_sha256 = null or omitted
```

## 8.4 Phase 3 — Hash Manifest Write

Calculate SHA-256 hashes for all final artifacts and command output artifacts except `final_acceptance_artifact_hashes.json` itself. Then write:

```text
final_acceptance_artifact_hashes.json
```

The hash file must include:

```text
schema_version
schema_id
source_component
reviewed_commit
acceptance_mode
artifact_hashes_content_id
self_hash_mode = EXCLUDED_FROM_SELF_HASH
self_hash_reason
hashed_artifacts[]
unhashed_artifacts[]
warnings[]
errors[]
```

The hash file must list itself in `unhashed_artifacts` with reason:

```text
EXCLUDED_TO_AVOID_CYCLIC_HASH
```

## 8.5 Acceptance Rule

A final `ACCEPTED` or `ACCEPTED_WITH_SAFE_DEFERRALS` verdict is valid only if:

```text
all required final artifacts except the hash manifest itself are hashed
final_acceptance_artifact_hashes.json exists
hash file explicitly declares self_hash_mode = EXCLUDED_FROM_SELF_HASH
hash file lists itself as unhashed with reason EXCLUDED_TO_AVOID_CYCLIC_HASH
no required hashed artifact has null sha256
final report, completion record, and latest result do not embed a stale hash-manifest SHA
git_status_start.txt and git_status_end.txt are included if written and used by the report
```

---

# 9. Canonical Layer Catalog

Implement the canonical layer catalog in:

```text
tools/agentx_evolve/final_acceptance/layer_catalog.py
```

The catalog must include these layer IDs exactly.

| Layer ID | Layer Name | Required for full ACCEPTED? | Safe deferral allowed? | Expected evidence root |
|---|---|---:|---:|---|
| `L0_SEED_KERNEL` | L0 Seed Kernel | yes | no | `L0/` |
| `L1_STANDARDS_FRAMEWORK` | L1 Standards / Framework Contracts | yes | no | `L1/` |
| `L2_PROFILES_DOCS` | L2 Profiles / SIB / ES / EQC Docs | yes | no | `L2/` |
| `AGENTX_INITIATOR` | Agent_X Initiator | yes | no | `.agentx-init/` |
| `SECURITY_SANDBOX` | Security Sandbox / Filesystem Boundary | yes | no | `.agentx-init/security/` |
| `POLICY_CAPABILITY_REGISTRY` | Policy / Capability Registry | yes | no | `.agentx-init/policy/` |
| `GOVERNED_PATCH_EXECUTION` | Governed Patch Execution | yes if patching active | yes if patch apply remains blocked | `.agentx-init/patches/` |
| `FAILURE_TAXONOMY` | Failure Taxonomy / Recovery Playbook | yes | no | `.agentx-init/failure_taxonomy/` |
| `TOOL_MCP_ADAPTER` | Tool / MCP Adapter | yes | no | `.agentx-init/tool_calls/` |
| `MODEL_ADAPTER` | Model Adapter | yes if model execution active | yes if model execution disabled | `.agentx-init/models/` |
| `LOCAL_MODEL_RUNTIME_PROFILE` | Local Model Runtime Profile | yes if local runtime active | yes if local runtime disabled | `.agentx-init/models/` |
| `CONTEXT_BUILDER_TASK_PACKER` | Context Builder / Task Packer | yes if worker active | yes if worker disabled | `.agentx-init/context/` |
| `PROMPT_CONTRACT_VERSIONING` | Prompt Contract / Prompt Versioning | yes if prompt-driven work active | yes if worker disabled | `.agentx-init/prompts/` |
| `LLM_IMPLEMENTATION_WORKER` | LLM Implementation Worker | yes if autonomous implementation active | yes if disabled | `.agentx-init/worker/` |
| `SELF_EVOLUTION_ORCHESTRATOR` | Self-Evolution Orchestrator | yes if autonomous evolution active | yes if disabled | `.agentx-init/orchestrator/` |
| `HUMAN_REVIEW_APPROVAL` | Human Review / Approval Interface | yes if approval actions active | yes if approval-required actions blocked | `.agentx-init/human_review/` |
| `PROMOTION_RELEASE_GATE` | Promotion / Release Gate | yes for release verdict | yes for non-release acceptance | `.agentx-init/promotion/` |
| `GIT_INTEGRATION` | Git Integration | yes if Git mutation active | yes if Git write disabled | `.agentx-init/git/` |
| `EVALUATION_HARNESS` | Evaluation Harness / Regression Benchmark | yes | no | `.agentx-init/evaluations/` |
| `LONG_TERM_LEARNING` | Long-Term Learning / Outcome Review | no for v1 source-only acceptance | yes | `.agentx-init/learning/` |
| `DOCUMENTATION_SYNC` | Documentation Synchronization | yes for release acceptance | yes with doc drift warning | `.agentx-init/docs_sync/` |
| `TASK_QUEUE_SESSION_SCHEDULER` | Task Queue / Session Scheduler | no for v1 source-only acceptance | yes | `.agentx-init/task_queue/` |
| `MONITORING_OBSERVABILITY` | Monitoring / Observability | yes for production acceptance | yes for non-production/source-only acceptance | `.agentx-init/monitoring/` |
| `PACKAGING_DISTRIBUTION` | Packaging / Distribution | yes for release acceptance | yes for source-only acceptance | `.agentx-init/packaging/` |
| `BACKUP_DISASTER_RECOVERY` | Backup / Disaster Recovery | yes for production acceptance | yes for non-production/source-only acceptance | `.agentx-init/backup/` |
| `FINAL_SYSTEM_ACCEPTANCE` | Final System Acceptance | yes | no | `.agentx-init/final_acceptance/` |

The catalog must be deterministic. Layer IDs must be stable and unique.

---

# 10. Expected Evidence Path Map

The coding agent must implement explicit expected evidence paths. Do not rely only on directory existence.

Minimum path fields per layer:

```text
expected_package_path
expected_runtime_artifact_root
expected_completion_record_path
expected_review_report_path
expected_evidence_manifest_path
expected_latest_result_path
expected_artifact_hashes_path
expected_validation_output_path
```

Default expected evidence paths:

| Layer ID | Completion record | Review report | Evidence manifest / hashes |
|---|---|---|---|
| `AGENTX_INITIATOR` | `.agentx-init/completion_record.json` or documented initiator completion record | `.agentx-init/review_report.json` if present | `.agentx-init/validation_report.json` or equivalent |
| `SECURITY_SANDBOX` | `.agentx-init/security/security_sandbox_completion_record.json` | `.agentx-init/security/security_sandbox_review_report.json` | `.agentx-init/security/security_sandbox_evidence_manifest.json` |
| `POLICY_CAPABILITY_REGISTRY` | `.agentx-init/policy/policy_capability_registry_completion_record.json` | `.agentx-init/policy/policy_capability_registry_review_report.json` | `.agentx-init/policy/policy_capability_registry_evidence_manifest.json` |
| `GOVERNED_PATCH_EXECUTION` | `.agentx-init/patches/governed_patch_completion_record.json` | `.agentx-init/patches/governed_patch_review_report.json` | `.agentx-init/patches/governed_patch_evidence_manifest.json` |
| `FAILURE_TAXONOMY` | `.agentx-init/failure_taxonomy/failure_taxonomy_completion_record.json` | `.agentx-init/failure_taxonomy/failure_taxonomy_review_report.json` | `.agentx-init/failure_taxonomy/failure_taxonomy_evidence_manifest.json` |
| `TOOL_MCP_ADAPTER` | `.agentx-init/tool_calls/tool_mcp_adapter_completion_record.json` | `.agentx-init/tool_calls/tool_mcp_adapter_review_report.json` | `.agentx-init/tool_calls/tool_mcp_adapter_evidence_manifest.json` |
| `MODEL_ADAPTER` | `.agentx-init/models/model_adapter_completion_record.json` | `.agentx-init/models/model_adapter_review_report.json` | `.agentx-init/models/model_adapter_evidence_manifest.json` |
| `LOCAL_MODEL_RUNTIME_PROFILE` | `.agentx-init/models/local_model_runtime_profile_completion_record.json` | `.agentx-init/models/local_model_runtime_profile_review_report.json` | `.agentx-init/models/local_model_runtime_profile_evidence_manifest.json` |
| `CONTEXT_BUILDER_TASK_PACKER` | `.agentx-init/context/context_builder_completion_record.json` | `.agentx-init/context/context_builder_review_report.json` | `.agentx-init/context/context_builder_evidence_manifest.json` |
| `PROMPT_CONTRACT_VERSIONING` | `.agentx-init/prompts/prompt_contract_completion_record.json` | `.agentx-init/prompts/prompt_contract_review_report.json` | `.agentx-init/prompts/prompt_contract_evidence_manifest.json` |
| `LLM_IMPLEMENTATION_WORKER` | `.agentx-init/worker/llm_worker_completion_record.json` | `.agentx-init/worker/llm_worker_review_report.json` | `.agentx-init/worker/llm_worker_evidence_manifest.json` |
| `SELF_EVOLUTION_ORCHESTRATOR` | `.agentx-init/orchestrator/orchestrator_completion_record.json` | `.agentx-init/orchestrator/orchestrator_review_report.json` | `.agentx-init/orchestrator/orchestrator_evidence_manifest.json` |
| `HUMAN_REVIEW_APPROVAL` | `.agentx-init/human_review/human_review_completion_record.json` | `.agentx-init/human_review/human_review_report.json` | `.agentx-init/human_review/human_review_evidence_manifest.json` |
| `PROMOTION_RELEASE_GATE` | `.agentx-init/promotion/promotion_gate_completion_record.json` | `.agentx-init/promotion/promotion_gate_review_report.json` | `.agentx-init/promotion/promotion_gate_evidence_manifest.json` |
| `GIT_INTEGRATION` | `.agentx-init/git/git_integration_completion_record.json` | `.agentx-init/git/git_integration_review_report.json` | `.agentx-init/git/git_integration_evidence_manifest.json` |
| `EVALUATION_HARNESS` | `.agentx-init/evaluations/evaluation_harness_completion_record.json` | `.agentx-init/evaluations/evaluation_harness_review_report.json` | `.agentx-init/evaluations/evaluation_harness_evidence_manifest.json` |
| `DOCUMENTATION_SYNC` | `.agentx-init/docs_sync/docs_sync_completion_record.json` | `.agentx-init/docs_sync/docs_sync_review_report.json` | `.agentx-init/docs_sync/docs_sync_evidence_manifest.json` |
| `FINAL_SYSTEM_ACCEPTANCE` | `.agentx-init/final_acceptance/final_acceptance_completion_record.json` | `.agentx-init/final_acceptance/final_acceptance_report.json` | `.agentx-init/final_acceptance/final_acceptance_evidence_manifest.json` |

If a prior layer uses a different actual path, the Final System Acceptance Layer must support a documented alias table. Alias use must be recorded in the evidence item.

Rules:

```text
missing expected required path -> FAIL or DEFERRED_SAFELY only if layer deferral is allowed
alias path accepted only if documented in layer catalog or deviation register
file existence alone is not PASS
unreadable file is FAIL
schema-invalid required evidence is FAIL
stale required evidence is FAIL unless accepted as non-blocking for non-production/source-only mode
```

---

# 11. Active Feature Inference Rules

The cross-layer checker must infer whether optional/deferred layers are active.

A feature is active if any of the following is true:

```text
an enabled tool exposes the feature
a registry marks the feature enabled
a completion record says the feature is active
a runtime artifact shows successful execution of the feature
a config file enables the feature
a CLI command for the feature is exposed as production/release path
a dependent layer requires the feature
```

A feature is inactive only if evidence shows:

```text
the feature is disabled, blocked, stubbed, or not installed
no active dependent layer requires it
safe deferral is allowed for the selected acceptance mode
blocking behavior is tested or evidenced
```

The checker must not infer inactivity from missing files alone.

---

# 12. Dataclasses and Constants

Implement in:

```text
tools/agentx_evolve/final_acceptance/acceptance_models.py
```

## 12.1 Constants

```python
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_PARTIAL = "PARTIAL"
STATUS_NOT_CHECKED = "NOT_CHECKED"
STATUS_NOT_RUN = "NOT_RUN"
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"
STATUS_DEFERRED_SAFELY = "DEFERRED_SAFELY"
STATUS_STALE = "STALE"

VERDICT_ACCEPTED = "ACCEPTED"
VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS = "ACCEPTED_WITH_SAFE_DEFERRALS"
VERDICT_NOT_ACCEPTED = "NOT_ACCEPTED"

SEVERITY_BLOCKER = "BLOCKER"
SEVERITY_HIGH = "HIGH"
SEVERITY_NON_BLOCKING = "NON_BLOCKING"

MODE_IMPLEMENTATION_ACCEPTANCE = "IMPLEMENTATION_ACCEPTANCE"
MODE_SOURCE_ONLY_ACCEPTANCE = "SOURCE_ONLY_ACCEPTANCE"
MODE_NON_PRODUCTION_ACCEPTANCE = "NON_PRODUCTION_ACCEPTANCE"
MODE_PRODUCTION_ACCEPTANCE = "PRODUCTION_ACCEPTANCE"
MODE_RELEASE_ACCEPTANCE = "RELEASE_ACCEPTANCE"
```

## 12.2 Required Dataclasses

Implement these dataclasses:

```text
FinalAcceptanceLayer
FinalAcceptanceLayerRegistry
FinalAcceptanceEvidenceItem
FinalAcceptanceEvidenceManifest
CrossLayerCheck
FinalAcceptanceValidationResult
FinalAcceptanceDeviation
FinalAcceptanceArtifactHash
FinalAcceptanceModePolicy
FinalAcceptanceReport
FinalAcceptanceCompletionRecord
```

Each dataclass must include:

```text
schema_version
schema_id
created_at where applicable
source_component
warnings
errors
```

## 12.3 Required Field Additions Beyond v2

`FinalAcceptanceLayer` must include:

```text
acceptance_modes_required: list[str]
deferral_modes_allowed: list[str]
expected_evidence_aliases: list[str]
stale_after_days: int | None
bootstrap_self_layer: bool
```

`FinalAcceptanceEvidenceItem` must include:

```text
reviewed_commit_in_artifact: str | None
artifact_timestamp: str | None
stale: bool
alias_used: str | None
```

`FinalAcceptanceReport` and `FinalAcceptanceCompletionRecord` must include:

```text
acceptance_mode: str
self_hash_mode: str
artifact_hashes_path: str
artifact_hashes_content_id: str
artifact_hashes_sha256: str | None  # null/omitted by default to avoid cyclic hashing
bootstrap_mode_used: bool
```

Default rule:

```text
artifact_hashes_sha256 must be null or omitted in artifacts that are themselves hashed by final_acceptance_artifact_hashes.json.
Use artifact_hashes_content_id to link artifacts to the hash manifest generation.
```

---

# 13. Public API

## 13.1 `mode_policy.py`

Implement:

```python
build_mode_policy(mode: str) -> dict
is_layer_required_for_mode(layer_id: str, mode: str) -> bool
is_deferral_allowed_for_mode(layer_id: str, mode: str) -> bool
validate_acceptance_mode(mode: str) -> list[str]
```

## 13.2 `layer_catalog.py`

Implement:

```python
build_canonical_layer_catalog() -> list[FinalAcceptanceLayer]
validate_layer_catalog(layers: list[FinalAcceptanceLayer]) -> list[str]
```

Rules:

```text
layer IDs must be unique
required layers must have expected evidence definitions
Final System Acceptance layer must be present
catalog order must be deterministic
acceptance mode requirements must be explicit
```

## 13.3 `layer_registry.py`

Implement:

```python
build_final_acceptance_layer_registry(
    repo_root: Path,
    reviewed_commit: str | None = None,
    reviewed_branch: str | None = None,
    acceptance_mode: str = "SOURCE_ONLY_ACCEPTANCE",
    bootstrap_self: bool = False,
) -> FinalAcceptanceLayerRegistry

get_layer_by_id(registry: FinalAcceptanceLayerRegistry, layer_id: str) -> FinalAcceptanceLayer | None
list_required_layers(registry: FinalAcceptanceLayerRegistry) -> list[FinalAcceptanceLayer]
list_safely_deferred_layers(registry: FinalAcceptanceLayerRegistry) -> list[FinalAcceptanceLayer]
write_layer_registry(registry: FinalAcceptanceLayerRegistry, repo_root: Path) -> Path
```

## 13.4 `evidence_collector.py`

Implement:

```python
collect_layer_evidence(
    repo_root: Path,
    registry: FinalAcceptanceLayerRegistry,
    bootstrap_self: bool = False,
) -> FinalAcceptanceEvidenceManifest

collect_evidence_item(
    repo_root: Path,
    layer: FinalAcceptanceLayer,
    artifact_path: str,
    artifact_type: str,
    required: bool,
) -> FinalAcceptanceEvidenceItem

validate_evidence_item_schema_if_json(repo_root: Path, evidence_item: FinalAcceptanceEvidenceItem) -> FinalAcceptanceEvidenceItem
write_evidence_manifest(manifest: FinalAcceptanceEvidenceManifest, repo_root: Path) -> Path
```

Required behavior:

```text
check expected completion records
check expected review reports
check expected runtime roots
check schema files where applicable
calculate SHA-256 for existing evidence files
record missing required evidence
record unreadable evidence
record schema-invalid evidence
record stale evidence
never infer PASS from missing evidence
never create fake completion records for other layers
allow bootstrap exception only for FINAL_SYSTEM_ACCEPTANCE self completion during IMPLEMENTATION_ACCEPTANCE
```

## 13.5 `cross_layer_checker.py`

Implement:

```python
run_cross_layer_checks(
    repo_root: Path,
    registry: FinalAcceptanceLayerRegistry,
    evidence_manifest: FinalAcceptanceEvidenceManifest,
    acceptance_mode: str,
) -> list[CrossLayerCheck]

write_cross_layer_matrix(checks: list[CrossLayerCheck], repo_root: Path) -> Path
```

Required check categories:

```text
safety dependencies
tool execution dependencies
model/runtime dependencies
orchestration dependencies
release dependencies
evidence dependencies
recovery dependencies
runtime artifact boundary dependencies
acceptance-mode dependencies
active-feature dependencies
```

## 13.6 `validation_runner.py`

Implement:

```python
run_validation_commands(
    repo_root: Path,
    include_full_pytest: bool = True,
    avoid_recursive_final_acceptance: bool = True,
) -> list[FinalAcceptanceValidationResult]

run_single_validation_command(
    repo_root: Path,
    command_name: str,
    command: list[str],
    output_artifact_name: str,
    timeout_seconds: int = 120,
) -> FinalAcceptanceValidationResult

write_validation_results(results: list[FinalAcceptanceValidationResult], repo_root: Path) -> Path
```

Required validation commands:

```bash
PYTHONPATH=tools python -m compileall tools
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_final_acceptance_*.py
```

No-recursion rule:

```text
The validation runner must not call a command that calls the final acceptance CLI recursively.
If a full pytest command would recursively invoke the CLI run command, the runner must use the scoped final acceptance pytest command and record the full pytest command as NOT_RUN with justification, or isolate recursion with a test flag.
```

Rules:

```text
record command text
record exit code
record PASS only when exit code is 0
record FAIL when exit code is non-zero
record NOT_RUN only when intentionally skipped and justified
write bounded output artifact
hash output artifact if written
use subprocess without shell=True
never require GPU, network, hosted model, LLM, Bun, Node, OpenCode runtime, or running MCP server
```

## 13.7 `schema_validator.py`

Implement:

```python
validate_final_acceptance_schemas(repo_root: Path) -> list[FinalAcceptanceValidationResult]
validate_json_file_against_schema(json_path: Path, schema_path: Path) -> FinalAcceptanceValidationResult
write_schema_validation_results(results: list[FinalAcceptanceValidationResult], repo_root: Path) -> Path
```

If `jsonschema` is already part of Agent_X, use it. If not, use deterministic structural validation in tests or add a local lightweight validator only if acceptable to the project dependency policy.

## 13.8 `hash_utils.py`

Implement:

```python
sha256_file(path: Path) -> str
sha256_text(text: str) -> str
hash_artifacts(paths: list[Path], exclude_self_hash_file: Path | None = None) -> list[FinalAcceptanceArtifactHash]
write_artifact_hashes(hashes: list[FinalAcceptanceArtifactHash], repo_root: Path, self_hash_mode: str = "EXCLUDED_FROM_SELF_HASH") -> Path
validate_acyclic_hash_manifest(repo_root: Path) -> list[str]
```

`validate_acyclic_hash_manifest` must fail if mutually hashed artifacts embed the final SHA of the hash manifest.

Use Python standard library only:

```python
hashlib
```

## 13.9 `artifact_writer.py`

Implement:

```python
runtime_root(repo_root: Path) -> Path
ensure_runtime_root(repo_root: Path) -> Path
atomic_write_json(path: Path, data: dict) -> None
write_json_artifact(repo_root: Path, artifact_name: str, data: dict) -> Path
is_within_runtime_root(repo_root: Path, path: Path) -> bool
reject_path_traversal(repo_root: Path, path: Path) -> None
```

Rules:

```text
all final acceptance artifacts must be under .agentx-init/final_acceptance/
JSON writes must be atomic
artifact path traversal must be rejected
source tree writes are forbidden except the implementation files themselves during coding
```

## 13.10 `deviation_register.py`

Implement:

```python
load_deviation_register(repo_root: Path) -> list[FinalAcceptanceDeviation]
validate_deviation_register(deviations: list[FinalAcceptanceDeviation]) -> list[str]
write_deviation_register(deviations: list[FinalAcceptanceDeviation], repo_root: Path) -> Path
```

Rules:

```text
BLOCKER cannot be accepted as a deviation
missing hash cannot be accepted as a deviation
missing command exit code cannot be accepted as a deviation
critical safety impact cannot be accepted for ACCEPTED
safe deferrals must be recorded
```

## 13.11 `final_verdict.py`

Implement:

```python
calculate_final_verdict(
    registry: FinalAcceptanceLayerRegistry,
    evidence_manifest: FinalAcceptanceEvidenceManifest,
    cross_layer_checks: list[CrossLayerCheck],
    validation_results: list[FinalAcceptanceValidationResult],
    schema_validation_results: list[FinalAcceptanceValidationResult],
    deviations: list[FinalAcceptanceDeviation],
    acceptance_mode: str,
    allow_safe_deferrals: bool = True,
    bootstrap_self: bool = False,
) -> tuple[str, float, list[str], list[str]]
```

Return:

```text
final_verdict
implementation_rating
blockers
high_issues
```

Verdict rules:

```text
Any BLOCKER -> NOT_ACCEPTED
Any required command NOT_RUN -> NOT_ACCEPTED
Any required command FAIL -> NOT_ACCEPTED
Any schema validation FAIL -> NOT_ACCEPTED
Missing required evidence -> NOT_ACCEPTED
Missing required hash -> NOT_ACCEPTED
Required stale evidence -> NOT_ACCEPTED
Required safety-critical layer missing without safe deferral -> NOT_ACCEPTED
Unsafe deferral -> NOT_ACCEPTED
Only safe deferrals and no blockers -> ACCEPTED_WITH_SAFE_DEFERRALS
No blockers, no high issues, no unsafe deferrals -> ACCEPTED
```

## 13.12 `report_generator.py`

Implement:

```python
build_final_acceptance_report(
    repo_root: Path,
    registry: FinalAcceptanceLayerRegistry,
    evidence_manifest: FinalAcceptanceEvidenceManifest,
    cross_layer_checks: list[CrossLayerCheck],
    validation_results: list[FinalAcceptanceValidationResult],
    schema_validation_results: list[FinalAcceptanceValidationResult],
    deviations: list[FinalAcceptanceDeviation],
    artifact_hashes: list[FinalAcceptanceArtifactHash],
    acceptance_mode: str,
    bootstrap_self: bool,
) -> FinalAcceptanceReport

write_final_acceptance_report(report: FinalAcceptanceReport, repo_root: Path) -> Path
```

Report must summarize:

```text
acceptance mode
bootstrap mode
layer status matrix
evidence completeness
schema validation results
validation command results
cross-layer dependency results
safe deferrals
deviations
blockers
high issues
non-blocking follow-ups
final verdict
implementation rating
artifact hashes
```

## 13.13 `acceptance_runner.py`

Implement:

```python
run_final_acceptance(
    repo_root: Path,
    acceptance_mode: str = "SOURCE_ONLY_ACCEPTANCE",
    include_optional: bool = False,
    include_full_pytest: bool = False,
    allow_safe_deferrals: bool = True,
    bootstrap_self: bool = False,
) -> FinalAcceptanceReport

write_completion_record(
    report: FinalAcceptanceReport,
    validation_results: list[FinalAcceptanceValidationResult],
    artifact_hashes: list[FinalAcceptanceArtifactHash],
    repo_root: Path,
) -> Path

write_latest_result(report: FinalAcceptanceReport, repo_root: Path) -> Path
```

## 13.14 `cli.py`

Implement CLI entrypoint:

```bash
PYTHONPATH=tools python -m agentx_evolve.final_acceptance.cli run
PYTHONPATH=tools python -m agentx_evolve.final_acceptance.cli report
PYTHONPATH=tools python -m agentx_evolve.final_acceptance.cli check
PYTHONPATH=tools python -m agentx_evolve.final_acceptance.cli validate-schemas
```

Support options:

```text
--mode IMPLEMENTATION_ACCEPTANCE|SOURCE_ONLY_ACCEPTANCE|NON_PRODUCTION_ACCEPTANCE|PRODUCTION_ACCEPTANCE|RELEASE_ACCEPTANCE
--include-full-pytest
--no-safe-deferrals
--bootstrap-self
--repo-root <path>
```

Minimum behavior:

```text
run: run full final acceptance and write artifacts
report: print path and summary of latest report
check: run lightweight structure/evidence check
validate-schemas: validate final acceptance schema examples and artifacts
```

CLI must not:

```text
mutate source files
run network calls
start MCP server
call model providers
perform Git write operations
use shell=True
```

---

# 14. Schema Requirements

Every schema must:

```text
require schema_version
require schema_id
require source_component where applicable
require warnings
require errors
reject missing required fields
reject invalid status values
reject invalid verdict values
reject invalid severity values
reject invalid acceptance mode values
reject invalid safety impact values
allow evidence_refs arrays where applicable
use additionalProperties: false unless a compatibility field is explicitly documented
```

Required valid examples in tests:

```text
valid_final_acceptance_layer
valid_final_acceptance_layer_registry
valid_final_acceptance_evidence_item
valid_final_acceptance_evidence_manifest
valid_final_acceptance_cross_layer_check
valid_final_acceptance_validation_result
valid_final_acceptance_report
valid_final_acceptance_completion_record
valid_final_acceptance_deviation
valid_final_acceptance_artifact_hash
valid_final_acceptance_mode_policy
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
unexpected property fails unless compatibility exception is documented
```

---

# 15. Acceptance Runner Flow

The main acceptance runner must execute this sequence:

```text
1. Resolve repository root.
2. Validate acceptance mode.
3. Record reviewed commit and branch if Git is available.
4. Record review environment.
5. Record initial git status.
6. Build final acceptance layer registry.
7. Write final_acceptance_layer_registry.json.
8. Collect layer evidence with bootstrap-self rules if applicable.
9. Write final_acceptance_evidence_manifest.json.
10. Run cross-layer validation checks.
11. Write final_acceptance_cross_layer_matrix.json.
12. Run validation commands without recursive final acceptance execution.
13. Write final_acceptance_validation_results.json.
14. Run final acceptance schema validation.
15. Write final_acceptance_schema_validation_results.json.
16. Load, validate, and write deviation register.
17. Write final_acceptance_mode_policy.json.
18. Calculate final verdict and implementation rating.
19. Build draft final acceptance report.
20. Write draft final_acceptance_report.json.
21. Write draft final_acceptance_completion_record.json.
22. Write draft latest_final_acceptance_result.json.
23. Record final git status and write git_status_end.txt before final hash manifest generation.
24. Rewrite final report, completion record, and latest result with final verdict, artifact_hashes_path, artifact_hashes_content_id, and self_hash_mode, but without embedding the final hash-manifest SHA.
25. Hash all final artifacts and command-output artifacts except final_acceptance_artifact_hashes.json itself.
26. Write final_acceptance_artifact_hashes.json with self_hash_mode = EXCLUDED_FROM_SELF_HASH and with itself listed as unhashed.
27. Validate that no mutually hashed final artifact embeds a stale or cyclic hash-manifest SHA.
28. Return final report.
```

Fail-closed rules:

```text
missing repo root -> NOT_ACCEPTED
invalid acceptance mode -> NOT_ACCEPTED
missing reviewed commit when Git is available -> NOT_ACCEPTED
compileall fail -> NOT_ACCEPTED
pytest fail -> NOT_ACCEPTED
schema validation fail -> NOT_ACCEPTED
missing required evidence -> NOT_ACCEPTED
missing evidence hash -> NOT_ACCEPTED
stale required evidence -> NOT_ACCEPTED
cross-layer safety blocker -> NOT_ACCEPTED
unsafe deferral -> NOT_ACCEPTED
recursive final acceptance command detected -> NOT_ACCEPTED unless isolated and documented
```

---

# 16. Cross-Layer Validation Rules

The checker must enforce dependency consistency.

Required checks:

| Check | Source Layer | Required Target Layer | Severity if failed |
|---|---|---|---|
| Sandbox before path/file/command tools | `TOOL_MCP_ADAPTER` | `SECURITY_SANDBOX` | BLOCKER |
| Policy before mutating tools | `TOOL_MCP_ADAPTER` | `POLICY_CAPABILITY_REGISTRY` | BLOCKER |
| Failure classes before final acceptance | all active layers | `FAILURE_TAXONOMY` | BLOCKER |
| Patch apply requires governed patch layer | `TOOL_MCP_ADAPTER` | `GOVERNED_PATCH_EXECUTION` | BLOCKER if patch apply active; NON_BLOCKING if blocked stub |
| Orchestrator requires tool adapter | `SELF_EVOLUTION_ORCHESTRATOR` | `TOOL_MCP_ADAPTER` | BLOCKER if orchestrator active |
| Worker requires model adapter | `LLM_IMPLEMENTATION_WORKER` | `MODEL_ADAPTER` | BLOCKER if worker active |
| Worker requires prompt contract | `LLM_IMPLEMENTATION_WORKER` | `PROMPT_CONTRACT_VERSIONING` | BLOCKER if worker active |
| Worker requires context builder | `LLM_IMPLEMENTATION_WORKER` | `CONTEXT_BUILDER_TASK_PACKER` | BLOCKER if worker active |
| Approval-required actions require human review | mutating/high-risk layers | `HUMAN_REVIEW_APPROVAL` | BLOCKER if approval actions active |
| Release verdict requires promotion gate | `FINAL_SYSTEM_ACCEPTANCE` | `PROMOTION_RELEASE_GATE` | BLOCKER for release acceptance |
| Git mutation requires Git integration | mutating Git behavior | `GIT_INTEGRATION` | BLOCKER if Git write active |
| Release readiness requires evaluation harness | `PROMOTION_RELEASE_GATE` | `EVALUATION_HARNESS` | BLOCKER |
| Production readiness requires monitoring | production verdict | `MONITORING_OBSERVABILITY` | BLOCKER for production acceptance |
| Production readiness requires backup | production verdict | `BACKUP_DISASTER_RECOVERY` | BLOCKER for production acceptance |
| Installable release requires packaging | release verdict | `PACKAGING_DISTRIBUTION` | BLOCKER for release acceptance |
| Final docs require documentation sync | release docs status | `DOCUMENTATION_SYNC` | HIGH for source-only, BLOCKER for release acceptance |
| Final acceptance bootstrap self exception | `FINAL_SYSTEM_ACCEPTANCE` | `FINAL_SYSTEM_ACCEPTANCE` | NON_BLOCKING only in implementation bootstrap mode |

Each check must include:

```text
check_id
source_layer
target_layer
requirement
status
severity
reason
evidence_refs
```

---

# 17. Safe Deferral Rules

A layer may be marked `DEFERRED_SAFELY` only if:

```text
safe_deferral_allowed is true in the canonical layer catalog
deferral is allowed for the selected acceptance mode
there is explicit deferral evidence
active unsafe runtime path is disabled or blocked
no source mutation can occur through the deferred feature
no network can occur through the deferred feature
no Git write can occur through the deferred feature
no MCP server starts because of the deferred feature
cross-layer checker confirms no active dependent layer requires it
```

Examples of acceptable safe deferrals:

```text
Model Adapter deferred if LLM Implementation Worker and Orchestrator are disabled.
Human Review deferred if all approval-required actions are blocked.
Git Integration write behavior deferred if Git write tools are blocked.
MCP runtime deferred if Tool / MCP Adapter exposes no running MCP server.
Packaging deferred for source-only non-release acceptance.
Monitoring and Backup deferred only for source-only or non-production acceptance.
```

Unsafe deferrals are BLOCKERS.

---

# 18. Deviation Register

Create:

```text
.agentx-init/final_acceptance/final_acceptance_deviation_register.json
```

Deviation entries must include:

```text
deviation_id
area
description
reason
safety_impact
compensating_control
accepted_status
reviewer_decision
warnings
errors
```

Allowed `safety_impact` values:

```text
none
low
medium
high
critical
```

Rules:

```text
critical safety impact cannot be accepted for ACCEPTED
high safety impact cannot be accepted unless feature is inactive and blocked
missing evidence hash cannot be accepted as a deviation
missing required command exit code cannot be accepted as a deviation
BLOCKER cannot be accepted as a deviation
runtime artifact path exception must be recorded as a deviation
safe deferral must be recorded as a deviation or safe-deferral entry
bootstrap self-acceptance exception must be recorded in implementation acceptance mode
```

---

# 19. Evidence Staleness Rules

Required evidence is stale if:

```text
its reviewed_commit does not match the final acceptance reviewed_commit and the layer is source-coupled
its timestamp is older than the configured stale_after_days
its hash no longer matches the artifact content
its completion record references a different implementation path than the current catalog
its final decision was NOT DONE, NOT_ACCEPTED, INCOMPLETE, or BLOCKED
```

Stale required evidence blocks `ACCEPTED` unless:

```text
the selected mode permits the layer to be safely deferred
the stale artifact is not safety-critical for the selected mode
the deviation register records the accepted stale artifact and compensating control
```

Missing timestamps must be treated as stale for safety-critical layers.

## 19.1 Current-Run Evidence vs Prior-Layer Evidence

The runner must distinguish evidence produced by the current final acceptance run from evidence collected from prior layers.

Current-run evidence includes:

```text
final_acceptance_* artifacts
command output artifacts produced during this run
git_status_start.txt
git_status_end.txt
```

Prior-layer evidence includes completion records, review reports, evidence manifests, validation outputs, and hash manifests produced by earlier layers.

Rules:

```text
current-run evidence must match the current final acceptance reviewed_commit and acceptance_mode
prior-layer evidence must match the reviewed_commit for source-coupled layers unless a documented safe-deferral/staleness exception applies
prior-layer evidence may be accepted by alias only when the alias is documented
current-run artifacts must not be reused silently from an older final acceptance run
latest_final_acceptance_result.json from a previous run is not evidence for the current run until rewritten in the current run
```

---

# 20. Evidence Immutability and Hashing

All final artifacts must be hashed with SHA-256.

Required hash targets:

```text
final_acceptance_layer_registry.json
final_acceptance_evidence_manifest.json
final_acceptance_cross_layer_matrix.json
final_acceptance_validation_results.json
final_acceptance_schema_validation_results.json
final_acceptance_deviation_register.json
final_acceptance_mode_policy.json
final_acceptance_report.json
final_acceptance_completion_record.json
latest_final_acceptance_result.json
all command output artifacts used by report
```

Rules:

```text
hashes must be written before final ACCEPTED verdict is claimed
changed evidence after final report invalidates previous ACCEPTED verdict
new evidence requires a new timestamp and new report
manual edits after sign-off must be recorded as deviations
missing hash blocks ACCEPTED
final_acceptance_artifact_hashes.json excludes its own hash and records self_hash_mode
```

---

# 21. Completion Record

Create:

```text
.agentx-init/final_acceptance/final_acceptance_completion_record.json
```

Required content:

```json
{
  "schema_version": "1.0",
  "schema_id": "final_acceptance_completion_record.schema.json",
  "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
  "component_name": "Final System Acceptance Layer",
  "status": "VALIDATED",
  "acceptance_mode": "SOURCE_ONLY_ACCEPTANCE",
  "final_verdict": "ACCEPTED",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "runtime_artifact_root": ".agentx-init/final_acceptance/",
  "commands_run": [],
  "artifacts_created": [],
  "artifact_hashes": [],
  "artifact_hashes_path": ".agentx-init/final_acceptance/final_acceptance_artifact_hashes.json",
  "artifact_hashes_content_id": "<stable manifest generation id>",
  "artifact_hashes_sha256": null,
  "self_hash_mode": "EXCLUDED_FROM_SELF_HASH",
  "bootstrap_mode_used": false,
  "accepted_safe_deferrals": [],
  "unresolved_blockers": [],
  "unresolved_high_issues": [],
  "implementation_rating": 10.0
}
```

If final verdict is not accepted, status must be:

```text
VALIDATED_NOT_ACCEPTED
```

If validation did not complete, status must be:

```text
INCOMPLETE
```

---

# 22. Implementation Scoring Rubric

Use this rubric only after validation is run.

| Category | Points | Full-credit requirement |
|---|---:|---|
| Structure and files | 1.0 | All package, schema, test, and artifact paths exist as required. |
| Layer catalog and registry | 1.0 | Canonical layer catalog complete, deterministic, unique, mode-aware, and written to artifact. |
| Evidence collection | 1.0 | Required evidence detected, missing/stale evidence blocked, hashes calculated. |
| Cross-layer checks | 1.0 | Safety, tool, model, orchestration, release, evidence, recovery, and active-feature dependencies checked. |
| Validation commands | 1.0 | Compileall, pytest, and scoped final acceptance tests run with exit codes and no recursion. |
| Schema validation | 1.0 | All final acceptance schemas validate valid and invalid cases. |
| Verdict calculation | 1.0 | ACCEPTED impossible with blockers, missing evidence, stale evidence, missing hashes, or failed commands. |
| Report and completion record | 1.0 | Report and completion record are schema-valid, complete, hashed, and mode-aware. |
| CLI and runtime safety | 1.0 | CLI works idempotently, no source mutation, no network/model/MCP/Git write behavior. |
| Tests and negative cases | 1.0 | Required positive, negative, bootstrap, hashing, and mode tests pass. |

Hard caps:

```text
missing reviewed commit caps score at 6.0
missing acceptance mode caps score at 7.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
missing required evidence caps score at 7.0
stale required evidence accepted as PASS caps score at 6.5
missing evidence hashes caps score at 8.0
cyclic/self hash unresolved caps score at 8.0
mutually hashed artifact embeds stale hash-manifest SHA caps score at 8.0
cross-layer blocker ignored caps score at 5.0
ACCEPTED with blocker caps score at 4.0
ACCEPTED with missing required evidence caps score at 4.0
ACCEPTED with stale required evidence caps score at 5.0
source mutation outside runtime artifacts caps score at 6.0
network/model/MCP server required caps score at 6.0
Git write performed caps score at 5.0
recursive final acceptance command loop caps score at 7.0
```

---

# 23. Test Cases

## 23.1 Model Tests

Required tests:

```text
test_final_acceptance_layer_instantiates
test_final_acceptance_registry_instantiates
test_evidence_item_instantiates
test_validation_result_instantiates
test_cross_layer_check_instantiates
test_deviation_instantiates
test_artifact_hash_instantiates
test_mode_policy_instantiates
test_report_instantiates
test_completion_record_instantiates
```

## 23.2 Layer Catalog / Registry Tests

Required tests:

```text
test_layer_catalog_contains_all_required_layers
test_layer_catalog_ids_are_unique
test_layer_catalog_marks_final_acceptance_layer
test_required_layers_have_evidence_expectations
test_safe_deferral_flags_are_explicit
test_acceptance_modes_are_explicit
test_layer_registry_writes_under_runtime_root
test_get_layer_by_id_returns_expected_layer
```

## 23.3 Evidence Collector Tests

Required tests:

```text
test_evidence_collector_detects_existing_artifact
test_evidence_collector_detects_missing_required_artifact
test_evidence_collector_hashes_existing_artifact
test_evidence_collector_records_unreadable_evidence
test_evidence_collector_records_stale_evidence
test_evidence_collector_does_not_mark_missing_evidence_pass
test_evidence_collector_does_not_create_fake_layer_evidence
test_evidence_collector_supports_documented_alias
test_evidence_manifest_written_under_runtime_root
test_bootstrap_self_mode_does_not_require_prior_final_completion_record
```

## 23.4 Cross-Layer Checker Tests

Required tests:

```text
test_cross_layer_checker_blocks_missing_policy_for_active_tools
test_cross_layer_checker_blocks_missing_sandbox_for_file_tools
test_cross_layer_checker_blocks_missing_failure_taxonomy
test_cross_layer_checker_blocks_missing_model_adapter_for_worker
test_cross_layer_checker_blocks_missing_prompt_contract_for_worker
test_cross_layer_checker_blocks_missing_context_builder_for_worker
test_cross_layer_checker_blocks_missing_evaluation_for_release
test_cross_layer_checker_allows_safe_deferral_when_stubbed_and_evidenced
test_cross_layer_checker_rejects_unsafe_deferral
test_cross_layer_checker_uses_active_feature_inference
test_cross_layer_checker_applies_acceptance_mode_rules
```

## 23.5 Validation Runner Tests

Required tests:

```text
test_validation_runner_records_command_text
test_validation_runner_records_exit_code
test_validation_runner_pass_requires_zero_exit_code
test_validation_runner_failure_records_output_artifact
test_validation_runner_uses_no_shell_true
test_validation_runner_writes_results_under_runtime_root
test_validation_runner_detects_or_avoids_recursive_final_acceptance
```

## 23.6 Schema Validator Tests

Required tests:

```text
test_final_acceptance_schemas_accept_valid_examples
test_final_acceptance_schemas_reject_missing_required_fields
test_final_acceptance_schemas_reject_invalid_status
test_final_acceptance_schemas_reject_invalid_verdict
test_final_acceptance_schemas_reject_invalid_severity
test_final_acceptance_schemas_reject_invalid_acceptance_mode
test_final_acceptance_schemas_reject_unexpected_properties
test_schema_validation_results_written_under_runtime_root
```

## 23.7 Acceptance Runner Tests

Required tests:

```text
test_acceptance_runner_writes_required_artifacts
test_acceptance_runner_not_accepted_when_compileall_fails
test_acceptance_runner_not_accepted_when_pytest_fails
test_acceptance_runner_not_accepted_when_schema_validation_fails
test_acceptance_runner_not_accepted_when_required_evidence_missing
test_acceptance_runner_not_accepted_when_required_evidence_stale
test_acceptance_runner_accepted_with_safe_deferrals_only_when_allowed
test_acceptance_runner_records_exit_codes
test_acceptance_runner_records_hashes
test_acceptance_runner_uses_acyclic_hash_manifest
test_acceptance_runner_hashes_final_git_status_artifacts
test_acceptance_runner_records_reviewed_commit_when_git_available
test_acceptance_runner_does_not_write_outside_runtime_root
test_acceptance_runner_is_idempotent_for_repeated_runs
```

## 23.8 Report Generator Tests

Required tests:

```text
test_report_contains_acceptance_mode
test_report_contains_layer_summary
test_report_contains_evidence_summary
test_report_contains_cross_layer_summary
test_report_contains_validation_summary
test_report_contains_schema_validation_summary
test_report_contains_artifact_hashes
test_report_contains_final_verdict
test_report_does_not_accept_with_blockers
test_report_records_self_hash_mode
```

## 23.9 CLI Tests

Required tests:

```text
test_cli_check_runs_without_network
test_cli_validate_schemas_runs_without_network
test_cli_report_handles_missing_report
test_cli_run_writes_final_acceptance_artifacts
test_cli_run_supports_acceptance_mode_option
test_cli_run_supports_bootstrap_self_option
test_cli_does_not_mutate_source_files
test_cli_does_not_start_mcp_server
test_cli_repeated_run_is_idempotent
```

## 23.10 Negative Tests

Required negative tests:

```text
test_missing_required_layer_completion_record_blocks_acceptance
test_missing_hash_blocks_acceptance
test_required_command_not_run_blocks_acceptance
test_required_command_exit_code_missing_blocks_acceptance
test_stale_required_evidence_blocks_acceptance
test_unsafe_deferral_blocks_acceptance
test_unapproved_runtime_artifact_path_blocks_acceptance
test_cross_layer_blocker_blocks_acceptance
test_report_cannot_claim_accepted_with_blocker
test_report_cannot_claim_accepted_with_missing_required_evidence
test_report_cannot_claim_accepted_with_missing_hash
test_report_cannot_claim_accepted_with_stale_required_evidence
test_deviation_cannot_accept_blocker
test_acceptance_runner_does_not_fabricate_other_layer_evidence
test_hash_file_does_not_require_impossible_self_hash
test_final_report_does_not_embed_stale_hash_manifest_sha
test_completion_record_does_not_embed_stale_hash_manifest_sha
```

---

# 24. Implementation Order

Use this exact order:

```text
1. Create tools/agentx_evolve/final_acceptance/ package.
2. Implement acceptance_models.py.
3. Implement artifact_writer.py.
4. Implement hash_utils.py with non-cyclic hash behavior.
5. Implement mode_policy.py.
6. Create JSON schemas.
7. Implement layer_catalog.py.
8. Implement layer_registry.py.
9. Implement evidence_collector.py.
10. Implement deviation_register.py.
11. Implement cross_layer_checker.py.
12. Implement validation_runner.py.
13. Implement schema_validator.py.
14. Implement final_verdict.py.
15. Implement report_generator.py.
16. Implement acceptance_runner.py with two-phase finalization.
17. Implement cli.py.
18. Create model and schema tests.
19. Create layer catalog and registry tests.
20. Create evidence collector tests.
21. Create cross-layer checker tests.
22. Create validation runner tests.
23. Create schema validator tests.
24. Create report generator tests.
25. Create acceptance runner tests.
26. Create CLI tests.
27. Create negative tests.
28. Run compileall.
29. Run pytest.
30. Run final acceptance CLI in IMPLEMENTATION_ACCEPTANCE with --bootstrap-self.
31. Verify git status.
32. Review generated final acceptance artifacts.
```

Do not implement CLI before the deterministic runner exists.
Do not calculate final verdict before evidence and cross-layer checks exist.
Do not write completion record before validation results are recorded.
Do not claim final hashes before two-phase finalization completes.

---

# 25. Acceptance Criteria

The implementation is acceptable only if:

```text
all package files exist
all schema files exist
all required tests exist
compileall passes
pytest passes
schema validation passes
layer catalog contains all expected layers
layer IDs are stable and unique
acceptance modes are implemented and tested
layer registry writes under runtime root
evidence collector detects missing, present, stale, unreadable, and schema-invalid evidence correctly
evidence collector does not fabricate other-layer evidence
bootstrap self mode is limited to Final System Acceptance implementation acceptance
cross-layer checker identifies safety blockers
active feature inference is implemented
validation runner records commands and exit codes
validation runner avoids recursive final acceptance loops
acceptance runner writes all required runtime artifacts
final report is schema-valid
completion record is schema-valid
acyclic artifact hash manifest is implemented
all final evidence artifacts have SHA-256 hashes except the explicitly self-excluded hash file
final report, completion record, and latest result do not embed stale hash-manifest SHA values
final git status output is captured before final hashing when used by the report
required command exit codes are recorded
missing required evidence blocks acceptance
stale required evidence blocks acceptance
unsafe deferrals block acceptance
safe deferrals are explicitly recorded
runtime artifacts are written only under .agentx-init/final_acceptance/
no source mutation occurs during tests except approved runtime artifacts
no network is required
no hosted model is required
no MCP server is started
no Git write operation is performed
```

---

# 26. Definition of Done

The Final System Acceptance Layer is done when it can reproducibly decide whether Agent_X is accepted as a complete system.

It must prove:

```text
final acceptance package exists
schemas exist and validate
required tests exist and pass
layer catalog covers all roadmap layers
layer registry is deterministic and mode-aware
evidence collector records required evidence and hashes
evidence collector detects stale required evidence
cross-layer checker validates safety-critical dependencies
active feature inference prevents unsafe optional-layer assumptions
validation runner records command text, exit codes, and output artifacts
validation runner avoids recursive final acceptance execution
schema validator validates final acceptance artifacts
acceptance runner executes deterministic validation flow
final report generator writes machine-readable report
completion record is written only after validation
artifact hashes use an acyclic hash-manifest process
final verdict is calculated fail-closed
ACCEPTED is impossible with unresolved BLOCKER
ACCEPTED is impossible with missing required evidence
ACCEPTED is impossible with stale required evidence
ACCEPTED is impossible with missing command exit codes
ACCEPTED is impossible with missing hashes
ACCEPTED is impossible with cyclic or stale embedded hash-manifest references
ACCEPTED_WITH_SAFE_DEFERRALS records all safe deferrals
NOT_ACCEPTED records blockers and high issues
no network, model provider, Bun, Node, OpenCode runtime, or MCP server is required
no source mutation occurs outside approved runtime artifacts
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_final_acceptance_*.py
PYTHONPATH=tools python -m agentx_evolve.final_acceptance.cli run --mode IMPLEMENTATION_ACCEPTANCE --bootstrap-self
git status --short
```

Expected result:

```text
compileall PASS
pytest PASS
scoped final acceptance pytest PASS
final acceptance CLI completes
git status CLEAN or only expected runtime artifacts under .agentx-init/final_acceptance/
```

---

# 27. No-Go Conditions

The layer is NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
required package file missing
required schema missing
required test missing
layer catalog omits required layers
layer registry has duplicate layer IDs
acceptance mode is missing or invalid
evidence collector marks missing required evidence as PASS
evidence collector marks stale required evidence as PASS
evidence collector fabricates other-layer evidence
cross-layer checker ignores safety-critical missing dependency
cross-layer checker assumes inactive feature from missing files alone
acceptance runner claims ACCEPTED with a BLOCKER
acceptance runner claims ACCEPTED with missing required evidence
acceptance runner claims ACCEPTED with stale required evidence
acceptance runner claims ACCEPTED with missing evidence hash
acceptance runner claims ACCEPTED with missing command exit code
artifact hash file uses unresolved cyclic self-hash requirement
final report or completion record embeds stale hash-manifest SHA while also being hashed by that manifest
runtime artifact is written outside approved root without deviation
network is required
hosted model is required
MCP server starts
Git write operation occurs
source mutation occurs outside approved runtime artifacts
recursive final acceptance command loop occurs
final report is missing
completion record is missing
```

---

# 28. Final Frozen Acceptance Matrix

| Area | Required result for 10/10 |
|---|---|
| Subdirectory | `tools/agentx_evolve/final_acceptance/` exists with all required files. |
| Schemas | All final acceptance schemas exist and validate positive/negative examples. |
| Tests | All required tests and negative tests exist and pass. |
| Runtime artifacts | All final artifacts written under `.agentx-init/final_acceptance/`. |
| Acceptance modes | Implementation, source-only, non-production, production, and release modes are explicit. |
| Layer catalog | All roadmap layers represented with stable IDs and mode-aware requirements. |
| Evidence collector | Missing/stale required evidence blocks acceptance. |
| Cross-layer checker | Safety-critical dependency failures become BLOCKERS. |
| Active feature inference | Optional layers are required when their feature is active. |
| Validation runner | Commands, exit codes, summaries, and output artifacts recorded without recursion. |
| Schema validator | Final acceptance artifacts are schema-validated. |
| Final verdict | `ACCEPTED` impossible with blockers, missing evidence, stale evidence, missing hashes, failed commands, or unsafe deferrals. |
| Report generator | Final report contains mode, layer, evidence, validation, cross-layer, deviation, hash, and verdict summaries. |
| Completion record | Written after validation and includes reviewed commit, environment, commands, hashes, mode, and verdict. |
| Hashing | Acyclic SHA-256 hash manifest is implemented; final artifacts do not embed stale hash-manifest SHA values. |
| Bootstrap | Self-validation bootstrap exists only for implementation acceptance. |
| Safety | No network, model provider, MCP server, Git write, or source mutation. |

---

# 29. Coding Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] Target repository is Agent_X.
[ ] Final acceptance package will be created under tools/agentx_evolve/final_acceptance/.
[ ] Runtime artifacts will be written under .agentx-init/final_acceptance/.
[ ] This layer will not implement new agent behavior.
[ ] This layer will not mutate source files.
[ ] This layer will not call model providers.
[ ] This layer will not require network.
[ ] This layer will not start MCP server.
[ ] This layer will not perform Git writes.
[ ] Acceptance mode will be explicit.
[ ] Bootstrap self mode is only for implementation acceptance.
[ ] Missing required evidence blocks acceptance.
[ ] Stale required evidence blocks acceptance.
[ ] Missing hashes block acceptance.
[ ] Missing command exit codes block acceptance.
[ ] BLOCKER issues block acceptance.
[ ] Safe deferrals must be explicit, evidenced, and mode-compatible.
[ ] ACCEPTED_WITH_SAFE_DEFERRALS is not the same as full ACCEPTED.
[ ] The runner must not fabricate evidence for other layers.
[ ] The artifact hash file must avoid impossible cyclic self-hashing, and mutually hashed artifacts must not embed the hash manifest SHA.
[ ] The validation runner must avoid recursive final acceptance command loops.
```

---

# 30. Final Rating

This v4 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, files to create, schemas to create, classes/functions, acceptance runner, layer evidence collector, cross-layer validation checker, final report generator, runtime artifacts, integration with all previous layers, test files, test cases, implementation order, acceptance criteria, scoring rules, no-go conditions, evidence immutability, safe deferral rules, acceptance modes, bootstrap/self-validation handling, acyclic hash-manifest handling, active feature inference, stale evidence handling, CLI idempotency, and Definition of Done for the Final System Acceptance Layer.
```
