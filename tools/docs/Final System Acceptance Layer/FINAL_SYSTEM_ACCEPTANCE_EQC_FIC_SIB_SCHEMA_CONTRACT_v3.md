# FINAL_SYSTEM_ACCEPTANCE_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: FINAL_SYSTEM_ACCEPTANCE_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_FINAL_SYSTEM_ACCEPTANCE
component_name: Final System Acceptance Layer
roadmap_layer: 22
roadmap_phase: Phase Z — Final System Acceptance
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Release / Promotion Acceptance Criteria, MCP Protocol Acceptance Criteria if MCP runtime is validated
optional_standards: ES, Report Template
risk_level: critical
target_language: Python
canonical_subdirectory: tools/agentx_evolve/final_acceptance/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/final_acceptance/
contract_scope: final acceptance of the complete Agent_X system
final_verdict_field: ACCEPTED | NOT_ACCEPTED
previous_version_rating: 9.8/10
current_version_rating: 10/10
```

---

# 0. v3 Review and Upgrade Summary

## 0.1 v2 Rating

The v2 contract was strong and close to final, but I would rate it:

```text
9.8/10
```

It already covered:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
System Acceptance Gate Rules
Layer Completion Matrix
Cross-Layer Dependency Matrix
Regression / Validation Contract
Release Readiness Contract
Safety Freeze Contract
Final Evidence Contract
Final Verdict Contract
Agent_X integration notes
OpenCode borrowing notes
Definition of Done
No-Go conditions
fresh-clone validation
severity classification
deviation register
self-validation rule
implementation scoring rubric
```

## 0.2 Why v2 Was Not Fully 10/10

The v2 document was very strong, but several final-system acceptance edge cases needed tighter control:

```text
1. It did not explicitly define acceptance modes, such as DEVELOPMENT_ACCEPTANCE, RELEASE_CANDIDATE_ACCEPTANCE, and PRODUCTION_ACCEPTANCE.
2. It did not define exact canonical implementation files for this layer, leaving FIC responsibility too general for a coding handoff.
3. It did not require a contract-version compatibility check between lower-layer contracts, implementation specs, review reports, and completion records.
4. It did not define transitive dependency closure or dependency-cycle detection for the cross-layer dependency matrix.
5. It did not define stale-evidence rejection rules when a lower-layer evidence record belongs to a different commit or superseded contract.
6. It did not require deterministic path, timestamp, ordering, and hash normalization for reproducible final evidence.
7. It did not define a minimum threat model for final acceptance itself.
8. It did not define negative acceptance tests as first-class requirements, especially proving ACCEPTED cannot be produced with missing hashes, missing layers, broken dependencies, or unsafe deferrals.
9. It did not distinguish required, optional, inactive, externally unavailable, and future layers with enough precision.
10. It did not define provenance requirements for generated reports and machine-authored evidence.
11. It did not require explicit read-only behavior for the final acceptance runner beyond the general no-source-mutation rule.
12. It did not define a clear end-of-contract freeze rule for v3 that prevents further broad expansion unless actual acceptance semantics change.
```

## 0.3 v3 Improvements

This v3 adds:

```text
acceptance modes
canonical file/interface expectations
contract-version compatibility rules
transitive dependency closure and cycle checks
stale-evidence rejection rules
deterministic reproducibility rules
final-acceptance threat model
negative acceptance test requirements
layer applicability taxonomy
machine-authored evidence provenance rules
read-only runner constraints
stronger v3 freeze rule
```

This v3 is the final 10/10 controlling contract for the Final System Acceptance Layer.

---

# 1. Purpose

This document defines the controlling contract for the **Final System Acceptance Layer** of Agent_X.

The Final System Acceptance Layer determines whether the complete Agent_X system is validated, reproducible, safe, auditable, internally consistent, release-ready, recoverable, and ready to be marked as finally accepted at a specific commit.

This layer does not implement new agent behavior. It verifies that all required layers and subsystems have passed their own gates and that the whole system can operate as a governed self-evolving software system without bypassing:

```text
safety controls
policy controls
sandbox controls
patch governance
human review / approval controls
model-output boundaries
release / promotion gates
Git approval gates
evidence and audit requirements
backup and recovery requirements
runtime artifact boundaries
schema validation
regression validation
```

The layer must answer one final question:

```text
Can the complete Agent_X system be marked ACCEPTED at this exact reviewed commit?
```

The only valid final answers are:

```text
ACCEPTED
NOT_ACCEPTED
```

A partial, informal, assumed, or document-only acceptance is not allowed.

---

# 2. Scope

## 2.1 Required in This Layer

The Final System Acceptance Layer must define and enforce contracts for:

```text
system-wide acceptance gate
foundational layer inventory
roadmap layer completion matrix
cross-layer dependency matrix
required validation commands
schema validation status
regression validation status
evidence manifest verification
layer evidence-chain verification
release readiness verification
safety freeze verification
runtime artifact boundary verification
source mutation verification
deviation register
severity classification
final acceptance report
final evidence bundle
final verdict record
final accepted / not-accepted decision
```

It must verify that every required Agent_X layer is one of:

```text
implemented and validated
safely deferred with no active unsafe runtime path
not applicable with explicit justification
blocked and therefore prevents final acceptance
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
new model behavior
new tool execution behavior
new patch application behavior
new policy decisions
new sandbox decisions
new Git mutation logic
new promotion behavior
new monitoring behavior
new backup behavior
new MCP runtime behavior
new LLM or hosted-provider behavior
new self-evolution planning behavior
```

It validates those layers. It does not replace them.

## 2.3 Authority Boundary

Final System Acceptance may:

```text
read evidence
read source and runtime metadata
validate schemas
run allowlisted validation commands
compute hashes
write final acceptance artifacts
produce final verdict
```

Final System Acceptance must not:

```text
modify source files
apply patches
repair lower-layer evidence
approve its own missing prerequisites
rewrite failed layer evidence
override policy decisions
override sandbox decisions
override release gate decisions
override human approval requirements
open network connections by default
start MCP runtime by default
execute unallowlisted shell commands
mark NOT_CHECKED as PASS
mark unsafe deferrals as DEFERRED_SAFELY
```

---

# 3. Standards Applied

## 3.1 Primary Standard: EQC

EQC is primary because this layer decides whether Agent_X as a complete system is accepted.

The acceptance decision is safety-critical because it affects:

```text
whether self-evolution is considered operational
whether tool execution is trusted
whether patch execution is trusted
whether model execution is trusted
whether release/promotion gates are trusted
whether evidence is considered complete
whether unresolved blockers are enforced
whether the system may be considered ready for controlled use
```

The layer must fail closed.

## 3.2 Required Supporting Standard: FIC

FIC is required because this layer must have concrete implementation files with fixed responsibilities.

Expected implementation areas include:

```text
acceptance models
layer registry / layer matrix loader
cross-layer dependency checker
validation runner
schema validation checker
evidence manifest checker
evidence chain checker
release readiness checker
safety freeze checker
final verdict writer
final acceptance report generator
final evidence bundle generator
```

Every file must have:

```text
clear responsibility
public API
input contract
output contract
invariants
failure behavior
tests
runtime artifact limits
```

## 3.2.1 Canonical FIC File Expectations

The implementation spec may refine file names, but this contract requires the Final System Acceptance layer to include these responsibility areas as concrete files or explicitly equivalent modules:

```text
tools/agentx_evolve/final_acceptance/__init__.py
tools/agentx_evolve/final_acceptance/final_acceptance_models.py
tools/agentx_evolve/final_acceptance/layer_matrix.py
tools/agentx_evolve/final_acceptance/dependency_matrix.py
tools/agentx_evolve/final_acceptance/validation_runner.py
tools/agentx_evolve/final_acceptance/schema_validator.py
tools/agentx_evolve/final_acceptance/evidence_checker.py
tools/agentx_evolve/final_acceptance/release_readiness.py
tools/agentx_evolve/final_acceptance/safety_freeze.py
tools/agentx_evolve/final_acceptance/deviation_register.py
tools/agentx_evolve/final_acceptance/final_report.py
tools/agentx_evolve/final_acceptance/final_verdict.py
tools/agentx_evolve/final_acceptance/bundle_writer.py
tools/agentx_evolve/final_acceptance/run_final_acceptance.py
tools/agentx_evolve/final_acceptance/validate_final_acceptance_schemas.py
```

A different file layout is acceptable only if the implementation review maps each responsibility to a concrete file and records the deviation. Missing responsibility mapping blocks final acceptance.

## 3.3 Required Supporting Standard: SIB

SIB is required because this layer integrates all prior Agent_X layers.

It must verify boundaries between:

```text
L0 seed kernel
L1 standards and framework contracts
L2 profiles / SIB / ES / EQC documents
Agent_X Initiator
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter
Model Adapter
Local Model Runtime Profile
Context Builder / Task Packer
Prompt Contract / Prompt Versioning
LLM Implementation Worker
Self-Evolution Orchestrator
Human Review / Approval Interface
Promotion / Release Gate
Git Integration
Evaluation Harness / Regression Benchmark
Long-Term Learning / Outcome Review
Documentation Synchronization
Task Queue / Session Scheduler
Monitoring / Observability
Packaging / Distribution
Backup / Disaster Recovery
Final System Acceptance
```

This is a system boundary, not a local utility.

## 3.4 Required Supporting Standard: Schema Contract

Schema Contract is required because final acceptance must be machine-checkable.

The layer must define schemas for:

```text
final_acceptance_layer_record.schema.json
final_acceptance_layer_matrix.schema.json
final_acceptance_dependency_record.schema.json
final_acceptance_dependency_matrix.schema.json
final_acceptance_command_result.schema.json
final_acceptance_validation_result.schema.json
final_acceptance_evidence_manifest.schema.json
final_acceptance_release_readiness.schema.json
final_acceptance_safety_freeze.schema.json
final_acceptance_deviation_register.schema.json
final_acceptance_report.schema.json
final_acceptance_verdict.schema.json
final_acceptance_bundle.schema.json
```

## 3.5 Required Evidence / Audit Rules

Every acceptance decision must produce evidence.

Evidence is required for:

```text
acceptance run started
layer accepted
layer not accepted
layer deferred safely
layer not applicable
layer evidence missing
validation command pass
validation command fail
schema validation pass
schema validation fail
runtime artifact boundary pass
runtime artifact boundary fail
source mutation pass
source mutation fail
dependency check pass
dependency check fail
release readiness pass
release readiness fail
safety freeze pass
safety freeze fail
final ACCEPTED verdict
final NOT_ACCEPTED verdict
```

---

# 4. Final Acceptance Meaning

Final acceptance means:

```text
all required Agent_X layers exist or have accepted safe deferrals
all implemented layers passed their own acceptance gates
all required validation commands pass
all required schemas validate
all required evidence exists
all required evidence is hashable
all runtime artifacts are inside approved boundaries or deviations are recorded
all cross-layer dependencies are satisfied
all safety-critical deferrals are blocked or safely stubbed
no unresolved BLOCKER remains
release readiness is proven
backup and recovery readiness are proven when release-ready is claimed
final evidence is reproducible
final verdict is recorded at a specific commit
```

Final acceptance does not mean:

```text
the system is perfect forever
all future layers are feature-complete beyond their accepted scope
all optional integrations are enabled
all MCP runtime modes are enabled
all network/provider modes are enabled
all model providers are approved
all Git write operations are allowed
all patch operations can bypass review
all deferred features are usable
```

Final acceptance means the system is accepted **at a specific commit** under the recorded contract and evidence.

---

# 5. Status Vocabulary

Use only these status values in final acceptance artifacts:

```text
PASS
PARTIAL
FAIL
NOT_CHECKED
NOT_RUN
NOT_APPLICABLE
DEFERRED_SAFELY
BLOCKED
```

| Status | Meaning | Final ACCEPTED allowed? |
|---|---|---|
| PASS | Requirement was checked and satisfied. | Yes |
| PARTIAL | Some required parts exist, but coverage is incomplete. | No, unless explicitly non-blocking and outside active runtime path |
| FAIL | Requirement was checked and failed. | No |
| NOT_CHECKED | Requirement was not validated. | No |
| NOT_RUN | Required command was not run. | No |
| NOT_APPLICABLE | Requirement truly does not apply to accepted scope. | Yes, with justification |
| DEFERRED_SAFELY | Feature is deferred and cannot execute unsafe behavior. | Yes, only with evidence |
| BLOCKED | Requirement is blocked or unsafe. | No |

A final acceptance report cannot mark the system `ACCEPTED` if any required area remains `NOT_CHECKED` or any required command remains `NOT_RUN`.

---

# 6. Acceptance Modes

The final acceptance implementation must support explicit acceptance modes. A final report must record exactly one mode.

Allowed modes:

```text
DEVELOPMENT_ACCEPTANCE
RELEASE_CANDIDATE_ACCEPTANCE
PRODUCTION_ACCEPTANCE
```

## 6.1 DEVELOPMENT_ACCEPTANCE

Development acceptance may be used when the system is internally coherent but not being declared release-ready.

Rules:

```text
all safety-critical active layers must PASS
inactive future layers may be DEFERRED_SAFELY
release readiness may be NOT_APPLICABLE only if no release-ready claim is made
backup/disaster recovery may be DEFERRED_SAFELY only if packaging/release is inactive
no policy, sandbox, patch, tool, model, promotion, Git, or evidence bypass may exist
```

## 6.2 RELEASE_CANDIDATE_ACCEPTANCE

Release-candidate acceptance may be used when the system is ready for final release verification but not necessarily deployed.

Rules:

```text
all release-critical layers must PASS
promotion/release gate must PASS
packaging/distribution evidence must PASS
backup/disaster recovery evidence must PASS or have accepted non-production limitation
regression validation must PASS
final documentation synchronization must PASS
```

## 6.3 PRODUCTION_ACCEPTANCE

Production acceptance is the strictest mode.

Rules:

```text
all required layers must PASS unless explicitly out of production scope
no safety-critical layer may be PARTIAL
no release-critical dependency may be DEFERRED_SAFELY
backup/disaster recovery must PASS
monitoring/observability must PASS
promotion/release gate must PASS
rollback or recovery procedure must PASS
```

Mode-specific exceptions must be recorded in the deviation register. A final report that omits acceptance mode is invalid.

---

# 7. Review Validity Rules

A final acceptance run is valid only if all of the following are true:

```text
[ ] reviewed commit is recorded
[ ] reviewed branch is recorded
[ ] validation was run against the exact reviewed commit
[ ] initial working-tree state is recorded
[ ] final working-tree state is recorded
[ ] review environment is recorded
[ ] Python version is recorded
[ ] pytest version is recorded or explicitly unavailable
[ ] every required command records command text, working directory, exit code, status, and summary
[ ] every command marked PASS has exit_code 0
[ ] every expected-failure negative test records the expected failure condition
[ ] layer matrix is created and schema-validated
[ ] dependency matrix is created and schema-validated
[ ] evidence manifest exists before ACCEPTED is claimed
[ ] final report exists before ACCEPTED is claimed
[ ] final verdict record exists before ACCEPTED is claimed
[ ] final evidence bundle exists before ACCEPTED is claimed
[ ] required SHA-256 hashes are present
[ ] no acceptance result relies only on a document rating
```

The following are separate ratings:

```text
contract_document_rating: quality of this controlling contract
implementation_rating: validated quality of the Final System Acceptance implementation
system_acceptance_score: score for the complete Agent_X system at reviewed commit
```

The system may not be marked `ACCEPTED` because this document says `previous_version_rating: 9.8/10
current_version_rating: 10/10`. The system can be marked `ACCEPTED` only when the recorded validation evidence satisfies the GO criteria.

---

# 8. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or a clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <reviewed commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools
PYTHONPATH=tools python -m pytest
PYTHONPATH=tools python tools/agentx_evolve/final_acceptance/validate_final_acceptance_schemas.py
PYTHONPATH=tools python tools/agentx_evolve/final_acceptance/run_final_acceptance.py
git status --short
```

Required result:

```text
initial git status: CLEAN or EXPECTED_RUNTIME_ARTIFACTS_ONLY
python version: recorded
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
final acceptance runner: PASS, exit_code 0
final git status: CLEAN or EXPECTED_RUNTIME_ARTIFACTS_ONLY
```

No validation command may require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
external MCP server
background daemon
```

unless that dependency is explicitly part of a separately accepted runtime profile and recorded in the evidence package. The default final acceptance path must remain deterministic and local.

---

# 9. System Acceptance Gate Rules

## 8.1 Required Gate Inputs

The final acceptance gate must receive or discover:

```text
repository root
reviewed commit
reviewed branch
review timestamp
reviewer identity or tool name
operating system
Python version
pytest version
layer completion records
layer review reports
layer evidence manifests
schema validation results
compileall result
pytest result
final acceptance runner result
source mutation result
runtime artifact boundary result
release readiness result
safety freeze result
accepted deviation register
```

## 8.2 GO Criteria

The system may be marked `ACCEPTED` only if:

```text
reviewed commit is recorded
review environment is recorded
all required foundational layers have PASS, NOT_APPLICABLE, or DEFERRED_SAFELY status
all required roadmap layers have PASS, NOT_APPLICABLE, or DEFERRED_SAFELY status
all safety-critical layers are PASS or DEFERRED_SAFELY with blocking stubs
compileall passes with exit_code 0
pytest passes with exit_code 0
schema validation passes with exit_code 0
final acceptance runner passes with exit_code 0
regression validation passes or is explicitly not applicable
source mutation check passes
runtime artifact boundary check passes
evidence manifest exists
evidence hashes exist
final evidence bundle exists
release readiness check passes
safety freeze check passes
final acceptance report exists
final verdict record exists
no required command is NOT_RUN
no required area is NOT_CHECKED
no BLOCKER remains
all deviations are recorded and accepted
```

## 8.3 NO-GO Criteria

The system must be marked `NOT_ACCEPTED` if any are true:

```text
reviewed commit is missing
review environment is missing
compileall fails
pytest fails
schema validation fails
final acceptance runner fails
regression validation fails without accepted justification
required layer completion record is missing
required layer review report is missing
required layer evidence manifest is missing
cross-layer dependency is broken
policy layer can be bypassed
sandbox layer can be bypassed
patch execution can bypass governance
Tool / MCP Adapter exposes mutating MCP tools by default
model layer can perform ungoverned source mutation
orchestrator can bypass policy/sandbox/review gates
promotion gate can release without acceptance evidence
Git write operations can bypass approval
backup / disaster recovery evidence is missing for release-ready claim
runtime artifacts are written outside approved roots without accepted deviation
source files are mutated during acceptance validation
secrets are logged
final evidence hashes are missing
final acceptance report is missing
final verdict record is missing
final evidence bundle is missing
any BLOCKER remains
```

---

# 10. Foundational and Roadmap Layer Inventory

The Final System Acceptance Layer must separate foundational layers from roadmap layers.

## 9.1 Foundational Layers

Foundational layers are not all numbered in the same roadmap sequence, but they must still be included in final acceptance.

| Foundation ID | Layer | Required final status |
|---|---|---|
| F0 | L0 Seed Kernel | PASS |
| F1 | L1 Standards / Framework Contracts | PASS |
| F2 | L2 Profiles / SIB / ES / EQC Documents | PASS |
| F3 | Agent_X Initiator | PASS |

## 9.2 Roadmap Layers

The matrix must cover the current Agent_X roadmap sequence.

| Roadmap # | Layer | Required final status |
|---:|---|---|
| 1 | Security Sandbox / Filesystem Boundary | PASS |
| 2 | Policy / Capability Registry | PASS |
| 3 | Governed Patch Execution | PASS or DEFERRED_SAFELY for inactive mutation paths |
| 4 | Failure Taxonomy / Recovery Playbook | PASS |
| 5 | Tool / MCP Adapter | PASS |
| 6 | Model Adapter | PASS or DEFERRED_SAFELY if no hosted model path active |
| 7 | Local Model Runtime Profile | PASS or NOT_APPLICABLE if local runtime not enabled |
| 8 | Context Builder / Task Packer | PASS |
| 9 | Prompt Contract / Prompt Versioning | PASS |
| 10 | LLM Implementation Worker | PASS or DEFERRED_SAFELY if not active |
| 11 | Self-Evolution Orchestrator | PASS or DEFERRED_SAFELY if not active |
| 12 | Human Review / Approval Interface | PASS or DEFERRED_SAFELY with hard blocking stubs |
| 13 | Promotion / Release Gate | PASS |
| 14 | Git Integration | PASS or DEFERRED_SAFELY for write operations |
| 15 | Evaluation Harness / Regression Benchmark | PASS |
| 16 | Long-Term Learning / Outcome Review | PASS or DEFERRED_SAFELY if learning writes disabled |
| 17 | Documentation Synchronization | PASS |
| 18 | Task Queue / Session Scheduler | PASS or DEFERRED_SAFELY if background scheduling disabled |
| 19 | Monitoring / Observability | PASS |
| 20 | Packaging / Distribution | PASS |
| 21 | Backup / Disaster Recovery | PASS |
| 22 | Final System Acceptance | PASS |

## 9.3 Layer Applicability Taxonomy

Every layer must be classified with exactly one applicability value:

```text
REQUIRED_ACTIVE
REQUIRED_INACTIVE_SAFE_STUB
OPTIONAL_ACTIVE
OPTIONAL_INACTIVE
FUTURE_LAYER
NOT_APPLICABLE_TO_MODE
```

Rules:

```text
REQUIRED_ACTIVE must PASS.
REQUIRED_INACTIVE_SAFE_STUB may be DEFERRED_SAFELY only if execution is impossible or hard-blocked.
OPTIONAL_ACTIVE must PASS if it is part of the accepted runtime profile.
OPTIONAL_INACTIVE may be NOT_APPLICABLE only if no active runtime path depends on it.
FUTURE_LAYER may be DEFERRED_SAFELY only if no current layer can call it unsafely.
NOT_APPLICABLE_TO_MODE must cite the acceptance mode that makes it not applicable.
```

A layer cannot be omitted because it is inconvenient, incomplete, or currently failing.

## 9.4 Layer Matrix Rule

Final acceptance is blocked if:

```text
any required foundational layer is missing
any required roadmap layer is missing
any required layer has FAIL
any required layer has NOT_CHECKED
any required layer has NOT_RUN
any safety-critical layer is PARTIAL without accepted safe deferral
any layer claims DONE without evidence manifest
any layer claims DONE without reviewed commit
any layer claims DONE without validation command results
any layer evidence hash is missing
any layer evidence hash does not match
```

---

# 11. Layer Completion Matrix Contract

The Final System Acceptance Layer must maintain a machine-checkable layer matrix.

## 10.1 Required Layer Matrix Fields

Each layer record must include:

```text
schema_version
schema_id
layer_id
layer_name
layer_group
roadmap_number
component_id
required_for_final_acceptance
safety_critical
status
validated_commit
validated_at
completion_record_path
completion_record_sha256
review_report_path
review_report_sha256
evidence_manifest_path
evidence_manifest_sha256
schema_ids
validation_commands
runtime_artifact_root
open_blockers
high_issues
non_blocking_followups
accepted_deviations
safe_deferrals
final_decision
warnings
errors
```

## 10.2 Layer Matrix Aggregate Fields

The layer matrix must include:

```text
schema_version
schema_id
component_id
reviewed_commit
created_at
foundational_layers
roadmap_layers
missing_layers
failed_layers
deferred_layers
not_applicable_layers
hash_status
matrix_status
warnings
errors
```

---

# 12. Cross-Layer Dependency Matrix

The final acceptance layer must verify dependency correctness across the system.

## 11.1 Required Dependency Checks

| Dependent layer | Required dependency | Acceptance rule |
|---|---|---|
| Tool / MCP Adapter | Security Sandbox | File/path/command tools cannot bypass sandbox |
| Tool / MCP Adapter | Policy / Capability Registry | Every tool call must be policy-checked |
| Tool / MCP Adapter | Failure Taxonomy | Failed tool results must carry failure classes |
| Tool / MCP Adapter | Governed Patch Execution | Patch application must not be implemented directly in tools |
| Governed Patch Execution | Security Sandbox | Patch targets must be prechecked |
| Governed Patch Execution | Policy / Capability Registry | Source mutation requires policy approval |
| Governed Patch Execution | Human Review / Approval | High-risk mutation requires approval when configured |
| Model Adapter | Policy / Capability Registry | Provider/network modes must be governed |
| Local Model Runtime Profile | Model Adapter | Local runtime constraints must be enforced |
| Context Builder / Task Packer | Prompt Contract | Context must follow prompt/version limits |
| LLM Implementation Worker | Prompt Contract | Prompts must be versioned and bounded |
| LLM Implementation Worker | Tool / MCP Adapter | Worker cannot directly mutate source |
| Self-Evolution Orchestrator | Tool / MCP Adapter | Orchestrator must call tools through controlled adapter |
| Self-Evolution Orchestrator | Policy / Capability Registry | Orchestrator cannot override policy |
| Self-Evolution Orchestrator | Human Review / Approval | Review-required actions cannot bypass approval |
| Promotion / Release Gate | Evaluation Harness | Release requires regression evidence |
| Promotion / Release Gate | Git Integration | Git writes require release gate approval |
| Documentation Synchronization | Completion Evidence | Docs must match accepted layer state |
| Task Queue / Session Scheduler | Policy / Capability Registry | Scheduled work must not bypass policy |
| Monitoring / Observability | Evidence / Audit | Monitoring summaries must be evidence-backed |
| Packaging / Distribution | Promotion / Release Gate | Distribution requires release gate pass |
| Backup / Disaster Recovery | Packaging / Distribution | Release artifacts must be recoverable |
| Final System Acceptance | All layers | Final verdict requires system-wide evidence |

## 11.2 Dependency Record Fields

Each dependency record must include:

```text
schema_version
schema_id
dependency_id
dependent_layer
required_dependency
dependency_type
acceptance_rule
status
evidence_refs
failure_if_broken
warnings
errors
```

## 11.3 Dependency Failure Rule

Final acceptance is blocked if any dependency allows:

```text
policy bypass
sandbox bypass
direct source mutation outside governed path
unreviewed patch application
unapproved Git write
unvalidated model output used as source mutation
MCP mutating exposure by default
release without regression evidence
release without backup/recovery evidence
final verdict without evidence hashes
```

## 11.4 Transitive Dependency Closure and Cycle Rules

The dependency matrix must check direct and transitive dependencies.

Required behavior:

```text
build a dependency graph from all active and safely deferred layers
verify every required dependency target exists in the layer matrix
verify every transitive safety dependency is satisfied
reject unknown dependency targets
reject dependency cycles unless explicitly marked as review-only and non-runtime
record dependency graph hash in the evidence manifest
```

Final acceptance is blocked if:

```text
a required transitive dependency is missing
a dependency cycle can cause a safety gate to rely on itself
a layer marks itself PASS using evidence produced only by a downstream layer that depends on it
the final acceptance layer uses its own ACCEPTED verdict as prerequisite evidence for its own validation
```

---

# 13. Regression / Validation Contract

## 12.1 Required Validation Commands

The final acceptance process must record commands equivalent to:

```bash
PYTHONPATH=tools python -m compileall tools
PYTHONPATH=tools python -m pytest
PYTHONPATH=tools python tools/agentx_evolve/final_acceptance/validate_final_acceptance_schemas.py
PYTHONPATH=tools python tools/agentx_evolve/final_acceptance/run_final_acceptance.py
git status --short
```

If the repository uses scoped test commands, the final acceptance report must list every scoped command and why it is sufficient.

## 12.2 Command Evidence Requirements

Every command record must include:

```text
schema_version
schema_id
command_id
command_name
exact_command_text
working_directory
started_at
finished_at
exit_code
status
summary
stdout_artifact_path
stdout_sha256
stderr_artifact_path
stderr_sha256
expected_failure
expected_failure_condition
warnings
errors
```

`PASS` requires:

```text
exit_code = 0
```

unless the command is an explicitly expected-failure negative test with the expected failure condition recorded.

## 12.3 Regression Rule

Regression validation must prove:

```text
previously accepted safety tests still pass
negative tests still fail closed
known blocked operations remain blocked
known deferred features remain inert
runtime artifact boundaries remain enforced
schemas still reject invalid records
final acceptance cannot pass with missing evidence
final acceptance cannot pass with missing hashes
final acceptance cannot pass with broken dependencies
```

---

# 14. Schema Contract

## 13.1 Required Schemas

Create schemas for:

```text
final_acceptance_layer_record.schema.json
final_acceptance_layer_matrix.schema.json
final_acceptance_dependency_record.schema.json
final_acceptance_dependency_matrix.schema.json
final_acceptance_command_result.schema.json
final_acceptance_validation_result.schema.json
final_acceptance_evidence_manifest.schema.json
final_acceptance_release_readiness.schema.json
final_acceptance_safety_freeze.schema.json
final_acceptance_deviation_register.schema.json
final_acceptance_report.schema.json
final_acceptance_verdict.schema.json
final_acceptance_bundle.schema.json
```

## 13.2 Schema Rules

Each schema must:

```text
require schema_version
require schema_id
require component_id where applicable
require reviewed_commit where applicable
require status fields
require warnings
require errors
reject missing required fields
reject unknown final verdict values
reject unknown status values
reject PASS command records with non-zero exit code
represent ACCEPTED and NOT_ACCEPTED verdicts
represent DEFERRED_SAFELY and NOT_APPLICABLE statuses
represent blockers, deviations, and evidence hashes
represent command exit codes
represent source mutation status
represent runtime artifact boundary status
```

## 13.3 Schema Validation Requirement

Schema validation must prove:

```text
valid layer record passes
invalid layer record fails
valid layer matrix passes
layer matrix with missing required layer fails
valid dependency record passes
valid dependency matrix passes
dependency matrix with broken required dependency fails
valid command result passes
PASS command with non-zero exit code fails
valid validation result passes
valid evidence manifest passes
evidence manifest missing hashes fails
valid release readiness record passes
release readiness with blocker fails
valid safety freeze record passes
safety freeze with unapproved mutation path fails
valid deviation register passes
deviation register accepting a BLOCKER fails
valid final acceptance report passes
final report missing reviewed commit fails
valid final verdict ACCEPTED passes
ACCEPTED verdict with blockers fails
invalid verdict value fails
valid final evidence bundle passes
bundle missing hash-of-hashes fails
```

---

# 15. Evidence / Audit Rules

## 14.1 Runtime Artifact Root

All final acceptance runtime artifacts must be written under:

```text
.agentx-init/final_acceptance/
```

Allowed artifacts:

```text
final_acceptance_layer_matrix.json
final_acceptance_dependency_matrix.json
final_acceptance_validation_result.json
final_acceptance_evidence_manifest.json
final_acceptance_release_readiness.json
final_acceptance_safety_freeze.json
final_acceptance_deviation_register.json
final_acceptance_report.json
final_acceptance_verdict.json
final_acceptance_bundle.json
final_acceptance_command_history.jsonl
final_acceptance_event_history.jsonl
```

## 14.2 Evidence Hashing

Every final evidence file must have a SHA-256 hash.

Required hashed files:

```text
final_acceptance_layer_matrix.json
final_acceptance_dependency_matrix.json
final_acceptance_validation_result.json
final_acceptance_evidence_manifest.json
final_acceptance_release_readiness.json
final_acceptance_safety_freeze.json
final_acceptance_deviation_register.json
final_acceptance_report.json
final_acceptance_verdict.json
final_acceptance_bundle.json
stored command outputs, if any
referenced layer evidence manifests
referenced layer review reports
referenced layer completion records
```

Hashing rule:

```text
Use SHA-256.
Use Python standard library hashlib if no project hash helper exists.
A final ACCEPTED verdict is invalid if required evidence hashes are missing.
```

## 14.3 Evidence Chain Continuity

Final acceptance must prove evidence continuity from each accepted layer to final evidence.

For every accepted layer, the final evidence manifest must reference:

```text
layer completion record path
layer completion record SHA-256
layer review report path
layer review report SHA-256
layer evidence manifest path
layer evidence manifest SHA-256
validated commit
final decision
open blockers
accepted deviations
```

A layer cannot contribute to final ACCEPTED status if its evidence chain is missing, unhashable, or inconsistent.

## 14.4 Contract-Version Compatibility and Stale Evidence Rules

Final acceptance must reject stale or incompatible evidence.

For every accepted layer, the final acceptance checker must compare:

```text
layer component_id
validated_commit
contract document id and version
implementation spec id and version
review / DoD document id and version
schema ids and schema versions
completion record timestamp
review report timestamp
evidence manifest timestamp
artifact hashes
```

Evidence is stale if:

```text
validated_commit does not match the reviewed commit and no accepted compatibility bridge exists
review report references an older contract that is superseded by a required current contract
completion record predates the latest source change for that layer without accepted justification
schema version in evidence does not match schema version required by the final matrix
hash in the final matrix does not match the referenced artifact
machine-generated report has no generator identity or version
```

A stale safety-critical layer record is a BLOCKER. A stale non-safety optional record may be accepted only as NOT_APPLICABLE or DEFERRED_SAFELY with a deviation entry.

## 14.5 Final Evidence Bundle

Create:

```text
.agentx-init/final_acceptance/final_acceptance_bundle.json
```

The bundle must include:

```text
schema_version
schema_id
component_id
reviewed_commit
created_at
included_artifacts
artifact_hashes
layer_evidence_hashes
command_output_hashes
hash_of_hashes
bundle_status
warnings
errors
```

The `hash_of_hashes` must be computed from the ordered list of final artifact SHA-256 values.

## 14.5.1 Deterministic Reproducibility Rules

Final acceptance evidence must be reproducible across fresh checkouts of the same commit.

The implementation must normalize:

```text
artifact path separators to POSIX-style relative paths
evidence file ordering by stable lexical order
layer matrix ordering by foundation id and roadmap number
dependency matrix ordering by dependency_id
hash input encoding as UTF-8
JSON serialization with sorted keys and stable separators where used for hashing
line endings for generated JSON/JSONL reports
```

The implementation must not include nondeterministic values in hash inputs unless the value is part of the recorded evidence object and the object hash is computed after final serialization.

Timestamps are allowed as evidence fields, but they must not be used to compare two separate runs as identical unless explicitly normalized.

## 14.6 Evidence Immutability

After a final `ACCEPTED` verdict:

```text
final evidence files must not be modified without a new final acceptance run
changed hashes invalidate the previous ACCEPTED verdict
manual edits must be recorded as deviations
new commits require new acceptance evidence
new validation evidence requires a new timestamp and reviewed commit
```

## 14.7 Audit Events

The layer must append audit events for:

```text
acceptance run started
layer matrix loaded
layer record missing
layer record accepted
layer record rejected
dependency matrix checked
dependency failure found
validation command started
validation command completed
schema validation completed
evidence manifest written
release readiness checked
safety freeze checked
deviation register written
final evidence bundle written
final verdict written
acceptance run completed
```

---

# 16. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded in the deviation register.

Create:

```text
.agentx-init/final_acceptance/final_acceptance_deviation_register.json
```

Required deviation fields:

```text
schema_version
schema_id
deviation_id
area
layer_id
description
reason
safety_impact
compensating_control
accepted_status
reviewer_decision
evidence_refs
warnings
errors
```

Allowed accepted statuses:

```text
NOT_APPLICABLE
DEFERRED_SAFELY
NON_BLOCKING_FOLLOWUP
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
HIGH items cannot be accepted for ACCEPTED unless the final report proves they are outside the active runtime path.
Runtime artifact writes outside approved roots require a deviation entry.
MCP runtime deferral requires a deviation entry if MCP runtime is part of claimed scope.
Missing evidence hashes cannot be accepted as a deviation for ACCEPTED.
Missing reviewed commit cannot be accepted as a deviation for ACCEPTED.
```

---

# 17. Release Readiness Contract

Final acceptance must verify release readiness.

Release readiness requires:

```text
all required validation commands pass
all release-critical layers pass
promotion/release gate passes
Git integration state is controlled
packaging/distribution evidence exists
backup/disaster recovery evidence exists
rollback or recovery path exists
release notes or accepted documentation state exists
no unresolved BLOCKER remains
```

Release readiness must fail if:

```text
promotion gate is missing
regression evidence is missing
Git state is dirty beyond expected runtime artifacts
release artifact is not reproducible
backup/recovery evidence is missing
known critical safety layer is deferred unsafely
final docs are out of sync with accepted layer state
```

---

# 18. Safety Freeze Contract

The Safety Freeze Contract prevents broad changes from being hidden inside final acceptance.

## 17.1 Frozen Safety Rules

The following must not change during final acceptance:

```text
policy checks remain required
sandbox checks remain required for file/path/command tools
patch application remains governed
Tool / MCP Adapter remains fail-closed
MCP mutating tools are not exposed by default
Git write operations require approval/release gate
network/provider modes are disabled unless explicitly approved
model outputs cannot directly mutate source
human approval requirements cannot be bypassed
release requires regression evidence
release requires final acceptance evidence
```

## 17.2 Safety Freeze Failure

Final acceptance must fail if it detects:

```text
policy check removed
sandbox check removed
raw shell enabled by default
network enabled by default
Git write enabled by default
MCP mutating exposure enabled by default
patch execution bypasses governed patch layer
orchestrator bypasses Tool / MCP Adapter
model worker writes source directly
promotion gate bypassed
acceptance evidence omitted
```

---

# 19. Final Evidence Contract

The final evidence package must include:

```text
reviewed commit
reviewed branch
review timestamp
review environment
layer completion matrix
cross-layer dependency matrix
compileall result
pytest result
schema validation result
final acceptance runner result
source mutation result
runtime artifact boundary result
release readiness result
safety freeze result
deviation register
evidence manifest
final evidence bundle
final acceptance report
final verdict record
SHA-256 hashes for all final evidence files
accepted deviations
remaining non-blocking follow-ups
remaining blockers, if NOT_ACCEPTED
```

A final evidence package is invalid if:

```text
reviewed commit is missing
command exit code is missing
layer matrix is missing
dependency matrix is missing
evidence manifest is missing
final evidence bundle is missing
hashes are missing
hash-of-hashes is missing
final report is missing
final verdict record is missing
```

---

# 20. Final Verdict Contract

## 19.1 Verdict Values

Only these verdicts are allowed:

```text
ACCEPTED
NOT_ACCEPTED
```

## 19.2 ACCEPTED Verdict Requirements

`ACCEPTED` is valid only if:

```text
all GO criteria pass
no NO-GO condition exists
no BLOCKER remains
all required evidence exists
all required hashes exist
all required commands passed
all required layers are accepted or safely deferred
release readiness passes
safety freeze passes
final evidence bundle exists
final report exists
final verdict record exists
```

## 19.3 NOT_ACCEPTED Verdict Requirements

`NOT_ACCEPTED` must include:

```text
summary reason
blocking failures
failed layers
failed dependencies
failed commands
missing evidence
unsafe deferrals
source mutation failures
release readiness failures
safety freeze failures
required remediation areas
```

## 19.4 Verdict Record Fields

The final verdict record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "final_acceptance_verdict.schema.json",
  "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch>",
  "validated_at": "<UTC timestamp>",
  "final_verdict": "ACCEPTED",
  "acceptance_score": 10.0,
  "go_criteria_status": "PASS",
  "no_go_criteria_status": "PASS",
  "layer_matrix_status": "PASS",
  "dependency_matrix_status": "PASS",
  "validation_status": "PASS",
  "schema_validation_status": "PASS",
  "release_readiness_status": "PASS",
  "safety_freeze_status": "PASS",
  "evidence_manifest_path": ".agentx-init/final_acceptance/final_acceptance_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "final_report_path": ".agentx-init/final_acceptance/final_acceptance_report.json",
  "final_report_sha256": "<sha256>",
  "final_bundle_path": ".agentx-init/final_acceptance/final_acceptance_bundle.json",
  "final_bundle_sha256": "<sha256>",
  "hash_of_hashes": "<sha256>",
  "blockers": [],
  "accepted_deviations": [],
  "non_blocking_followups": [],
  "warnings": [],
  "errors": []
}
```

---

# 21. Self-Validation Rule

The Final System Acceptance Layer must validate itself.

It must prove:

```text
its own files exist
its own schemas exist
its own tests exist
its own schema validation passes
its own final acceptance runner passes
its own evidence artifacts are under .agentx-init/final_acceptance/
it cannot return ACCEPTED when required evidence is missing
it cannot return ACCEPTED when a BLOCKER exists
it cannot return ACCEPTED when its own validation fails
```

Self-validation must be represented in the layer matrix as:

```text
roadmap_number: 22
layer_name: Final System Acceptance
status: PASS
```

A final acceptance implementation cannot claim system ACCEPTED while its own implementation is unvalidated.

---

# 22. Agent_X Integration Notes

## 21.1 Integration Role

The Final System Acceptance Layer is the last validator in Agent_X.

It must integrate with:

```text
layer completion records
layer evidence manifests
layer review reports
schema validation utilities
validation command outputs
release gate outputs
monitoring summaries
backup/recovery evidence
packaging/distribution evidence
documentation synchronization evidence
```

## 21.2 Relationship to Prior Layers

Prior layer verdicts are necessary but not sufficient.

Final acceptance must check:

```text
individual layer DONE records
system-wide consistency
cross-layer dependencies
evidence continuity
runtime artifact boundaries
release readiness
safety freeze
```

A layer can be individually `DONE` while the system remains `NOT_ACCEPTED` due to a broken dependency or missing final evidence.

---

# 23. OpenCode Borrowing Notes

OpenCode is relevant only as a design reference for tool-driven coding-agent workflows.

Concepts that may be referenced:

```text
tool registry shape
validation-before-action pattern
structured tool outputs
tool auditability
separation of read/write/shell/tool primitives
```

Concepts that must not be imported into final acceptance:

```text
raw shell convenience
unbounded tool execution
network-enabled default behavior
plugin trust by default
model-driven approval without governance
release without explicit acceptance evidence
```

Final System Acceptance is stricter than OpenCode-style workflow completion. It is not merely a task-complete signal. It is a system-wide evidence-backed acceptance verdict.

---

# 24. Issue Severity Classification

## 23.1 BLOCKER

The system cannot be marked ACCEPTED if any BLOCKER exists.

```text
reviewed commit is missing
review environment is missing
required command exit code is missing
compileall fails
pytest fails
schema validation fails
final acceptance runner fails
layer matrix is missing
dependency matrix is missing
required layer evidence is missing
required evidence hash is missing
hash-of-hashes is missing
policy bypass exists
sandbox bypass exists
patch governance bypass exists
MCP exposes mutating tools by default
model worker can mutate source directly
orchestrator can bypass Tool / MCP Adapter
promotion gate can release without evidence
Git write can bypass approval
source mutation occurs during acceptance validation
secrets are logged
final report is missing
final verdict record is missing
final evidence bundle is missing
```

## 23.2 HIGH

High issues must be fixed before final acceptance unless they are explicitly proven outside the active runtime path.

```text
incomplete evidence references
incomplete documentation synchronization evidence
partial monitoring evidence
partial backup evidence for non-release use
safe deferral missing explanatory note
runtime artifact boundary exception lacks justification
review environment incomplete
some optional layer status unclear
```

## 23.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra inactive schema fields
additional optional reports not generated
inactive optional MCP runtime not installed
inactive hosted provider profile not configured
```

---

# 25. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Final acceptance files, schemas, tests, and runtime roots exist. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass. |
| Layer matrix | 1.0 | Foundational and roadmap layers are represented with evidence. |
| Dependency matrix | 1.0 | Required cross-layer dependencies are checked and pass. |
| Evidence chain and hashing | 1.0 | Evidence manifest, layer evidence refs, final bundle, hashes, and hash-of-hashes exist. |
| Release readiness | 1.0 | Promotion, packaging, docs, backup, recovery, and regression evidence are checked. |
| Safety freeze | 1.0 | Safety controls remain frozen and bypasses are blocked. |
| Self-validation and final verdict | 1.0 | Final Acceptance validates itself and writes valid ACCEPTED/NOT_ACCEPTED verdict. |

Scoring rule:

```text
10.0 = fully ACCEPTED
9.0-9.9 = strong but NOT_ACCEPTED if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not final-acceptance-complete
below 7.0 = not acceptable for final system acceptance
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
missing layer matrix caps score at 7.0
missing dependency matrix caps score at 7.0
missing evidence hashes caps score at 8.0
missing hash-of-hashes caps score at 8.0
missing final report caps score at 8.0
missing final verdict record caps score at 8.0
missing final evidence bundle caps score at 8.0
any NOT_CHECKED required area caps score at 8.0
any NOT_RUN required command caps score at 8.0
any BLOCKER caps score at 8.0 or lower depending on severity
policy/sandbox/patch/release bypass caps score at 4.0
source mutation during acceptance caps score at 7.0
secrets logged caps score at 4.0
```

---

# 26. Residual Risks

```yaml
residual_risks:
  - id: "FSA-RISK-001"
    description: "A layer may claim DONE without complete evidence."
    severity: "critical"
    mitigation: "Final acceptance requires completion records, review reports, evidence manifests, and hashes."

  - id: "FSA-RISK-002"
    description: "Cross-layer dependency gaps may allow safety bypasses."
    severity: "critical"
    mitigation: "Dependency matrix must prove policy, sandbox, patch, tool, model, orchestrator, and release boundaries."

  - id: "FSA-RISK-003"
    description: "Deferred features may be mislabeled as safe."
    severity: "high"
    mitigation: "DEFERRED_SAFELY requires evidence that the feature cannot execute unsafe behavior."

  - id: "FSA-RISK-004"
    description: "Final evidence may be edited after acceptance."
    severity: "high"
    mitigation: "Evidence immutability and SHA-256 hash rules invalidate modified evidence."

  - id: "FSA-RISK-005"
    description: "Release readiness may be claimed without backup or rollback evidence."
    severity: "high"
    mitigation: "Release readiness contract requires packaging, backup, recovery, and regression evidence."

  - id: "FSA-RISK-006"
    description: "The final acceptance layer may accidentally bless its own incomplete implementation."
    severity: "critical"
    mitigation: "Self-validation is required and represented as Roadmap Layer 22 in the layer matrix."
```

---

# 28. Pre-Code Gate

Implementation must not begin unless this contract defines:

```text
[ ] EQC, FIC, SIB standards
[ ] schema contract
[ ] evidence / audit rules
[ ] system acceptance gate rules
[ ] foundational layer inventory
[ ] roadmap layer completion matrix
[ ] cross-layer dependency matrix
[ ] regression / validation contract
[ ] release readiness contract
[ ] safety freeze contract
[ ] final evidence contract
[ ] deviation register
[ ] severity classification
[ ] self-validation rule
[ ] final verdict contract
[ ] Agent_X integration notes
[ ] OpenCode borrowing boundaries, if relevant
```

---

# 29. Post-Code Gate

After implementation, acceptance requires:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] schema validation passes
[ ] final acceptance runner passes
[ ] layer matrix validates
[ ] dependency matrix validates
[ ] release readiness validates
[ ] safety freeze validates
[ ] deviation register validates
[ ] evidence manifest exists
[ ] final evidence bundle exists
[ ] final report exists
[ ] final verdict record exists
[ ] evidence hashes exist
[ ] hash-of-hashes exists
[ ] source mutation check passes
[ ] runtime artifact boundary check passes
[ ] Final System Acceptance self-validation passes
```

---

# 30. Definition of Done

The Final System Acceptance Layer is done when it can produce a reproducible, evidence-backed final verdict for the complete Agent_X system.

It must prove:

```text
all required foundational layers are represented
all required roadmap layers are represented
all required layer statuses are validated
all required dependencies are checked
all required validation commands are recorded
all required schemas are validated
all required evidence exists
all required evidence is hashed
final evidence bundle is written
hash-of-hashes is written
release readiness is checked
safety freeze is checked
runtime artifact boundaries are checked
source mutation is checked
deviation register is written
final acceptance report is written
final verdict record is written
Final System Acceptance validates itself
ACCEPTED cannot be produced when blockers exist
NOT_ACCEPTED clearly identifies blockers and remediation areas
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools
PYTHONPATH=tools python -m pytest
PYTHONPATH=tools python tools/agentx_evolve/final_acceptance/validate_final_acceptance_schemas.py
PYTHONPATH=tools python tools/agentx_evolve/final_acceptance/run_final_acceptance.py
git status --short
```

Expected:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
final acceptance runner PASS, exit_code 0
git status CLEAN or expected runtime artifacts only
```

---

# 31. No-Go Conditions

The layer must remain NOT DONE, and the system must remain NOT_ACCEPTED, if any are true:

```text
final acceptance can return ACCEPTED without reviewed commit
final acceptance can return ACCEPTED without command evidence
final acceptance can return ACCEPTED without layer matrix
final acceptance can return ACCEPTED without dependency matrix
final acceptance can return ACCEPTED without evidence hashes
final acceptance can return ACCEPTED without hash-of-hashes
final acceptance can return ACCEPTED with unresolved BLOCKER
final acceptance can return ACCEPTED with failed compileall
final acceptance can return ACCEPTED with failed pytest
final acceptance can return ACCEPTED with failed schema validation
final acceptance can return ACCEPTED with failed final acceptance runner
final acceptance can return ACCEPTED with source mutation
final acceptance can return ACCEPTED with unsafe deferral
final acceptance can return ACCEPTED with release readiness failure
final acceptance can return ACCEPTED with safety freeze failure
final acceptance can return ACCEPTED without self-validation
final acceptance writes artifacts outside approved root without deviation
final acceptance modifies source files
final acceptance overrides lower-layer safety decisions
```

---

# 32. Final Freeze Rule

This v3 document is frozen as the controlling contract for the Final System Acceptance Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details in implementation spec
MAJOR: changed acceptance gates, changed final verdict semantics, changed required layer matrix, changed safety freeze rules, changed evidence requirements
```

Blocked without major revision:

```text
allowing ACCEPTED without evidence hashes
allowing ACCEPTED without hash-of-hashes
allowing ACCEPTED with unresolved BLOCKER
allowing ACCEPTED without reviewed commit
allowing ACCEPTED without validation command results
allowing acceptance to override policy/sandbox/release decisions
allowing source mutation during final acceptance
removing release readiness gate
removing safety freeze gate
removing layer matrix requirement
removing dependency matrix requirement
removing self-validation requirement
```

The next document should be:

```text
FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_SPEC.md
```

---

# 33. Final Rating

This v3 contract is rated:

```text
10/10
```

Reason:

```text
It defines the Final System Acceptance Layer with EQC, FIC, SIB, schema contracts, evidence rules, system acceptance gates, acceptance modes, foundational and roadmap layer matrices, layer applicability taxonomy, cross-layer dependency checks, transitive dependency closure, regression validation, release readiness, safety freeze, final evidence, final evidence bundle hashing, stale-evidence rejection, contract-version compatibility, deterministic reproducibility rules, machine-authored evidence provenance, deviation handling, severity classification, negative acceptance tests, threat model, self-validation, final verdict rules, Agent_X integration boundaries, OpenCode borrowing limits, no-go conditions, and Definition of Done.
```
