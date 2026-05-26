# 05_L1_SHARED_TYPES_AND_INTERFACES.md

```yaml
document_id: "SHARED-TYPES-INTERFACES-001"
project: "Agent_X"
title: "Shared Types and Interfaces"
version: "1.4"
status: "ready-for-project-review"
document_type: "shared-types-and-interfaces"
intended_location: "L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md"
authority_level: "shared-contracts"
last_updated: "2026-05-31"
governed_by:
  - "L1/docs/00_L1_SYSTEM_GOAL.md"
  - "L1/docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md"
requires:
  - "future L1/docs/03_traceability_matrix.md"
  - "L1/fic/*.md"
supersedes:
  - "SHARED-TYPES-INTERFACES-001 v1.3"
change_classification: "final-schema-closure-and-fic-reuse-tightening"
runtime_effect: "none"
```

---

# 1. Purpose

This document defines shared terms, shared records, lifecycle statuses, and interface contracts used by Agent_X governance, pseudocode, FIC units, implementation handoffs, validation records, review packets, and traceability records.

Its purpose is to prevent every FIC unit from inventing its own version of the same concepts.

This document is not runtime code. It is a shared contract source for later FIC documents and implementation units.

---

# 2. Governing Documents

This document is governed by:

```text
L1/docs/00_L1_SYSTEM_GOAL.md
L1/docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md
```

No shared type or interface in this file may contradict those documents.

---

# 3. Shared Status Values

## 3.1 Lifecycle Status

```text
BLOCKED
NO_CHANGE
IMPLEMENTED
VALIDATED
ACCEPTED
REJECTED
DEFERRED
```

Definitions:

```text
BLOCKED:
  Work cannot proceed because required context, authority, validation, safety, dependency, or ownership information is missing or conflicting.

NO_CHANGE:
  Inspected artifacts already satisfy the governing contract, with evidence.

IMPLEMENTED:
  A change was made, but the change is not automatically validated or accepted.

VALIDATED:
  Required checks passed or accepted waivers exist, but review acceptance may still be pending.

ACCEPTED:
  Review confirms that evidence is sufficient for the governed scope.

REJECTED:
  Review or validation found unacceptable scope, behavior, evidence, risk, or governance problems.

DEFERRED:
  Work is intentionally postponed and excluded from the current acceptance scope.
```

Rules:

```text
IMPLEMENTED does not imply VALIDATED.
VALIDATED does not imply ACCEPTED.
NO_CHANGE requires inspection evidence.
BLOCKED is a valid outcome, not a failure of the workflow.
```

---

# 4. Shared Classification Values

## 4.1 Request Classification

```text
CODE_CHANGE_REQUEST
DOCUMENT_CHANGE_REQUEST
REVIEW_REQUEST
GOVERNANCE_EVOLUTION_REQUEST
FIC_WORKFLOW_REQUEST
NO_CHANGE_CHECK_REQUEST
VALIDATION_REQUEST
UNCLASSIFIED_REQUEST
```

## 4.2 Workflow Decision

```text
DOCUMENT_ONLY
FIC_REQUIRED
IMPLEMENTATION_ALLOWED
NO_CHANGE
BLOCKED_UNKNOWN_WORKFLOW
```

## 4.3 Change Classification

```text
METADATA
VALIDATION
STATE
FUNCTIONAL
```

Definitions:

```text
METADATA:
  Non-functional change such as wording, formatting, ownership metadata, or references.

VALIDATION:
  Change to tests, checks, traces, review records, or validation evidence.

STATE:
  Change to toolchain, dependency state, environment profile, lockfile, or execution assumptions.

FUNCTIONAL:
  Change to behavior, public surface, state ownership, error behavior, runtime effect, persistence, trace semantics, or governance meaning.
```

---

# 5. Shared Risk Levels

```text
LOW
MEDIUM
HIGH
CRITICAL
UNKNOWN
```

Definitions:

```text
LOW:
  Low-impact documentation, simple pure helper, or narrow non-stateful change.

MEDIUM:
  Core workflow logic, validation behavior, adapters, or non-trivial project structure.

HIGH:
  Public interfaces, persistence, governance gates, state mutation, deletion, migration, or broad refactor.

CRITICAL:
  Irreversible action, security-sensitive behavior, approval bypass risk, destructive operation, or major architecture change.

UNKNOWN:
  Risk cannot be determined from available context. Workflow must block until risk is classified.
```

---

# 6. Shared Review Levels

```text
none
standard
strict
critical
```

Definitions:

```text
none:
  Review is not required for the specific record, usually because the action is informational or blocked before change.

standard:
  Normal governed review for ordinary document, FIC, validation, or implementation work.

strict:
  Required for public interfaces, state mutation, dependency changes, migrations, broad refactors, persistence, or governance changes.

critical:
  Required for irreversible actions, approval-gate changes, destructive operations, security-sensitive behavior, or major architecture changes.
```

Rules:

```text
HIGH risk requires strict review unless explicitly waived.
CRITICAL risk requires critical review.
UNKNOWN risk blocks workflow selection.
```

---

# 7. Shared Error and Block Codes

```text
BLOCKED_MISSING_SYSTEM_GOAL
BLOCKED_MISSING_REQUIRED_CONTEXT
BLOCKED_FIC_REQUIRED
BLOCKED_MISSING_SHARED_INTERFACE
BLOCKED_EXISTING_CODE_UNAVAILABLE
BLOCKED_CONFLICTING_AUTHORITY
BLOCKED_DUPLICATED_STATE_OWNERSHIP
BLOCKED_DUPLICATED_PUBLIC_SURFACE
BLOCKED_UNDEFINED_VALIDATION
BLOCKED_UNSUPPORTED_RUNTIME_CLAIM
BLOCKED_UNCLASSIFIED_REQUEST
BLOCKED_UNKNOWN_RISK_LEVEL
BLOCKED_UNKNOWN_WORKFLOW
BLOCKED_REQUIRED_INSPECTION_FAILED
BLOCKED_SCOPE_EXPANSION_REQUIRED
BLOCKED_PUBLIC_SURFACE_CHANGE_REQUIRED
BLOCKED_DEPENDENCY_UNDEFINED
BLOCKED_UNSUPPORTED_RUNTIME_BEHAVIOR
BLOCKED_FIC_TARGET_FILE_MISSING
BLOCKED_FIC_PUBLIC_SURFACE_MISSING
BLOCKED_FIC_NON_GOALS_MISSING
BLOCKED_FIC_DEPENDENCY_RULES_MISSING
BLOCKED_FIC_STATE_OWNERSHIP_MISSING
BLOCKED_FIC_ERROR_BEHAVIOR_MISSING
BLOCKED_FIC_VALIDATION_MISSING
BLOCKED_FIC_CONFLICTS_WITH_SYSTEM_GOAL
BLOCKED_FIC_SCOPE_TOO_BROAD
BLOCKED_FIC_COMPLETION_EVIDENCE_MISSING
BLOCKED_FIC_REVIEW_GATE_MISSING
BLOCKED_FIC_TRACEABILITY_BINDINGS_MISSING
BLOCKED_FIC_STOP_CONDITIONS_MISSING
BLOCKED_UNKNOWN_INTERFACE_OWNER
BLOCKED_SHARED_TYPE_VERSION_MISMATCH
BLOCKED_REVIEW_GATE_MISSING
BLOCKED_ACCEPTANCE_RULE_MISSING
BLOCKED_UNDEFINED_TRACEABILITY_RELATION
BLOCKED_UNDEFINED_PUBLIC_SURFACE_SHAPE
BLOCKED_INVALID_STATUS_TRANSITION
BLOCKED_DUPLICATE_ARTIFACT_ID
```

Rules:

```text
Block codes must be stable.
A blocked record must use one or more block codes.
A block code must identify the missing, conflicting, or unsafe condition.
New block codes must be added here before FIC units depend on them.
```

---

# 8. Shared Record Types

## 8.1 RequestRecord

```yaml
RequestRecord:
  request_id: string
  request_text: string
  request_source: "user|system|document|validator|reviewer|automation"
  received_at: string
  classified_as: RequestClassification
  requested_artifacts: list[string]
  user_constraints: list[string]
  explicit_non_goals: list[string]
  raw_context_refs: list[string]
```

Rules:

```text
request_id must be stable inside the workflow.
request_text must preserve the original request or a faithful summary.
classified_as must use the shared request classification values.
```

---

## 8.2 GoverningContext

```yaml
GoverningContext:
  system_goal: DocumentRef
  architecture_contract: DocumentRef|null
  whole_system_pseudocode: DocumentRef
  shared_interfaces: DocumentRef|null
  traceability_matrix: DocumentRef|null
  relevant_fic_units: list[DocumentRef]
  relevant_standards: list[DocumentRef]
  repository_evidence: RepositoryEvidence|null
  validation_evidence: list[EvidenceRef]
  missing_context: list[MissingContextItem]
```

Rules:

```text
system_goal is mandatory.
whole_system_pseudocode is mandatory.
missing_context must be empty before implementation is allowed.
```

---

## 8.3 ImpactAssessment

```yaml
ImpactAssessment:
  affected_documents: list[DocumentRef]
  affected_fic_units: list[DocumentRef]
  affected_code_files: list[FileRef]
  affected_tests: list[FileRef]
  affected_interfaces: list[InterfaceRef]
  affected_standards: list[DocumentRef]
  risk_level: RiskLevel
  requires_user_approval: boolean
  requires_rollback_plan: boolean
  requires_validation: boolean
  allowed_scope: ScopeSet
  forbidden_scope: ScopeSet
  minimum_evidence: list[EvidenceRequirement]
  review_gate: ReviewGate
  unitization_target: UnitizationTarget
```

Rules:

```text
risk_level must not be UNKNOWN before implementation is allowed.
allowed_scope and forbidden_scope must be explicit before handoff.
minimum_evidence must be defined before implementation success can be claimed.
```

---

## 8.4 FICScope

```yaml
FICScope:
  primary_unit: UnitRef
  unitization_target: UnitizationTarget
  target_files: list[FileRef]
  allowed_files: list[FileRef]
  forbidden_files: list[FileRef]
  public_surface: PublicSurfaceContract
  inputs_outputs: InputOutputContract
  state_ownership: StateOwnershipContract
  dependencies: DependencyContract
  non_goals: list[string]
  stop_conditions: list[StopCondition]
  tests: TestContract
  validation_commands: list[ValidationCommand]
  completion_evidence: list[EvidenceRequirement]
  rollback_expectations: RollbackExpectations|null
  review_gate: ReviewGate
  traceability_bindings: list[TraceabilityBinding]
```

Rules:

```text
allowed_files and forbidden_files must be explicit.
public_surface must be exact enough to prevent hidden public behavior.
stop_conditions must include conditions where the coding agent must return BLOCKED.
traceability_bindings are mandatory.
```

---

## 8.5 HandoffPacket

```yaml
HandoffPacket:
  handoff_id: string
  primary_fic: DocumentRef
  allowed_files: list[FileRef]
  forbidden_files: list[FileRef]
  required_context: list[ContextRef]
  forbidden_actions: list[string]
  public_surface_contract: PublicSurfaceContract
  validation_commands: list[ValidationCommand]
  completion_record_schema: SchemaRef
  stop_conditions: list[StopCondition]
  traceability_bindings: list[TraceabilityBinding]
  required_output_statuses:
    - BLOCKED
    - NO_CHANGE
    - IMPLEMENTED
    - VALIDATED
```

Rules:

```text
A handoff packet must be bounded.
A handoff packet must not authorize broad repository rewrites.
A handoff packet must not permit invented dependencies or public surfaces.
```

---

## 8.6 CompletionRecord

```yaml
CompletionRecord:
  completion_id: string
  status: LifecycleStatus
  request_id: string
  fic_id: string|null
  files_inspected: list[FileRef]
  files_changed: list[FileRef]
  public_surface_changes: list[PublicSurfaceChange]
  tests_added_or_updated: list[FileRef]
  validation_results: list[ValidationResult]
  deviations_from_fic: list[DeviationRecord]
  unresolved_risks: list[RiskRecord]
  rollback_notes: RollbackExpectations|null
  review_required: boolean
  traceability_bindings: list[TraceabilityBinding]
  acceptance_status: "NOT_ACCEPTED_UNTIL_REVIEWED|ACCEPTED|REJECTED|DEFERRED"
```

Rules:

```text
A completion record must not claim validation passed unless validation was run or explicitly waived.
files_inspected is required for NO_CHANGE and modify-existing work.
files_changed must be empty for NO_CHANGE.
deviations_from_fic must be empty or explicitly reviewed before acceptance.
```

---

## 8.7 ReviewPacket

```yaml
ReviewPacket:
  review_id: string
  summary: string
  governing_documents: list[DocumentRef]
  affected_artifacts: list[ArtifactRef]
  evidence: list[EvidenceRef]
  risks: list[RiskRecord]
  deviations: list[DeviationRecord]
  traceability_bindings: list[TraceabilityBinding]
  review_gate: ReviewGate
  acceptance_options:
    - ACCEPT
    - REJECT
    - REQUEST_REVISION
    - DEFER
    - MARK_BLOCKED
```

Rules:

```text
No meaningful governed change is accepted without a review packet.
Review must distinguish validated from accepted.
```

---

## 8.8 BlockedRecord

```yaml
BlockedRecord:
  blocked_id: string
  status: "BLOCKED"
  reason_codes: list[string]
  reason_summary: string
  required_missing_information: list[MissingContextItem]
  affected_artifacts: list[ArtifactRef]
  allowed_next_document_action: list[string]
  traceability_bindings: list[TraceabilityBinding]
```

Rules:

```text
A blocked record is a valid workflow output.
A blocked record must identify what prevents safe progress.
```

---

## 8.9 NoChangeRecord

```yaml
NoChangeRecord:
  no_change_id: string
  status: "NO_CHANGE"
  evidence: list[EvidenceRef]
  files_inspected: list[FileRef]
  governing_documents: list[DocumentRef]
  reason: string
  traceability_bindings: list[TraceabilityBinding]
```

Rules:

```text
NO_CHANGE requires inspection evidence.
NO_CHANGE must not be used when required files were not inspected.
```

---

# 9. Shared Reference Types

## 9.1 DocumentRef

```yaml
DocumentRef:
  doc_id: string
  path: string
  version: string|null
  status: string|null
  authority_level: string|null
```

## 9.2 FileRef

```yaml
FileRef:
  path: string
  file_type: "source|test|doc|config|schema|generated|unknown"
  exists: boolean|null
  inspected: boolean
```

## 9.3 ArtifactRef

```yaml
ArtifactRef:
  artifact_id: string
  artifact_type: "document|code|test|trace|standard|schema|review|completion|other"
  path: string|null
  version: string|null
```

## 9.4 EvidenceRef

```yaml
EvidenceRef:
  evidence_id: string
  evidence_type: "inspection|test_output|validation_output|trace|review|waiver|manual_record"
  path: string|null
  summary: string
  result: "pass|fail|not_run|waived|informational"
```

## 9.5 InterfaceRef

```yaml
InterfaceRef:
  interface_id: string
  name: string
  owner_doc: string
  owner_unit: string|null
  stability: "draft|stable|frozen|deprecated"
```

## 9.6 ContextRef

```yaml
ContextRef:
  context_id: string
  context_type: "document|file|excerpt|test|trace|schema|standard|repository_evidence"
  source: string
  required: boolean
  reason: string
```

## 9.7 SchemaRef

```yaml
SchemaRef:
  schema_id: string
  path: string|null
  version: string|null
  required: boolean
```

---

# 10. Shared Contract Types

## 10.1 PublicSurfaceContract

```yaml
PublicSurfaceContract:
  functions: list[PublicFunction]
  classes: list[PublicClass]
  types: list[PublicType]
  constants: list[PublicConstant]
  cli_commands: list[PublicCommand]
  config_keys: list[PublicConfigKey]
  events: list[PublicEvent]
  exports: list[PublicExport]
```

Rule:

```text
No public surface may be created unless declared or explicitly authorized.
```

---

## 10.2 InputOutputContract

```yaml
InputOutputContract:
  inputs: list[InputSpec]
  outputs: list[OutputSpec]
  side_effects_allowed: boolean
  declared_side_effects: list[SideEffectSpec]
```

Rule:

```text
Hidden inputs and hidden side effects are prohibited.
```

---

## 10.3 StateOwnershipContract

```yaml
StateOwnershipContract:
  owns_state: boolean
  state_items: list[StateItem]
  external_state_used: list[StateItem]
  mutation_allowed: boolean
  concurrency_rule: string|null
  reset_rule: string|null
```

Rule:

```text
Mutable state must have exactly one owner unless an explicit synchronization rule exists.
```

---

## 10.4 DependencyContract

```yaml
DependencyContract:
  allowed_imports: list[string]
  forbidden_imports: list[string]
  required_existing_symbols: list[RequiredSymbol]
  external_dependencies: list[ExternalDependency]
  dynamic_imports_allowed: boolean
```

Rule:

```text
Dependencies must not be invented during implementation.
```

---

## 10.5 TestContract

```yaml
TestContract:
  required_test_files: list[FileRef]
  required_unit_tests: list[string]
  required_integration_tests: list[string]
  required_property_tests: list[string]
  required_negative_tests: list[string]
  required_security_tests: list[string]
  required_performance_tests: list[string]
  coverage_expectation: string|null
```

Rule:

```text
Tests must verify the contract, not merely the implementation shape.
```

---

# 11. Atomic Field Types

These field-level types are used inside higher-level records. They must be defined here so FIC units do not invent incompatible field shapes.

## 11.1 PublicFunction

```yaml
PublicFunction:
  name: string
  signature: string
  purpose: string
  inputs: list[InputSpec]
  returns: OutputSpec
  raises: list[string]
  stability: "draft|stable|frozen|deprecated"
```

## 11.2 PublicClass

```yaml
PublicClass:
  name: string
  purpose: string
  constructor_signature: string
  public_methods: list[PublicFunction]
  stability: "draft|stable|frozen|deprecated"
```

## 11.3 PublicType

```yaml
PublicType:
  name: string
  kind: "record|enum|alias|schema|protocol|other"
  fields: list[FieldSpec]
  stability: "draft|stable|frozen|deprecated"
```

## 11.4 PublicConstant

```yaml
PublicConstant:
  name: string
  type: string
  value_policy: "literal|computed|environment|generated|unknown"
  stability: "draft|stable|frozen|deprecated"
```

## 11.5 PublicCommand

```yaml
PublicCommand:
  name: string
  purpose: string
  arguments: list[InputSpec]
  outputs: list[OutputSpec]
  stability: "draft|stable|frozen|deprecated"
```

## 11.6 PublicConfigKey

```yaml
PublicConfigKey:
  key: string
  type: string
  default: string|null
  required: boolean
  stability: "draft|stable|frozen|deprecated"
```

## 11.7 PublicEvent

```yaml
PublicEvent:
  name: string
  payload_type: string
  producer: string
  consumers: list[string]
  stability: "draft|stable|frozen|deprecated"
```

## 11.8 PublicExport

```yaml
PublicExport:
  name: string
  export_type: "function|class|type|constant|schema|command|event|other"
  source_symbol: string
  stability: "draft|stable|frozen|deprecated"
```

## 11.9 SideEffectSpec

```yaml
SideEffectSpec:
  effect_id: string
  effect_type: "file_write|file_read|database|network|stdout|stderr|state_mutation|trace|event|other"
  allowed: boolean
  target: string|null
  conditions: string
```

## 11.10 InputSpec

```yaml
InputSpec:
  name: string
  type: string
  source: "caller|config|environment|file|network|database|generated|llm-output|internal"
  required: boolean
  validation_rule: string
  trust_level: "trusted|untrusted|internal|external"
```

## 11.11 OutputSpec

```yaml
OutputSpec:
  name: string
  type: string
  destination: "return|file|database|stdout|event|trace|network|state"
  success_shape: string
  failure_shape: string
  ordering_rule: string|null
```

## 11.12 FieldSpec

```yaml
FieldSpec:
  name: string
  type: string
  required: boolean
  default: string|null
  validation_rule: string|null
```

## 11.13 StateItem

```yaml
StateItem:
  name: string
  type: string
  lifecycle: "created|read|updated|deleted|cached"
  mutation_allowed: boolean
  persistence: "memory|file|db|external|none"
  owner: string
```

## 11.14 RequiredSymbol

```yaml
RequiredSymbol:
  symbol: string
  source_file: string
  confirmation_required: boolean
```

## 11.15 ExternalDependency

```yaml
ExternalDependency:
  name: string
  version_policy: "pinned|range|stdlib|project-local"
  allowed: boolean
  reason: string
```

## 11.16 EvidenceRequirement

```yaml
EvidenceRequirement:
  requirement_id: string
  evidence_type: "inspection|unit_test|integration_test|property_test|validation_command|trace|review|waiver"
  required: boolean
  acceptance_rule: string
```

## 11.17 DeviationRecord

```yaml
DeviationRecord:
  deviation_id: string
  description: string
  affected_contract: string
  severity: "low|medium|high|critical"
  accepted: boolean
  acceptance_evidence: EvidenceRef|null
```

## 11.18 RiskRecord

```yaml
RiskRecord:
  risk_id: string
  description: string
  severity: "low|medium|high|critical"
  mitigation: string|null
  accepted: boolean
```

## 11.19 PublicSurfaceChange

```yaml
PublicSurfaceChange:
  change_id: string
  surface_type: "function|class|type|constant|command|config_key|event|export"
  symbol_or_name: string
  change_type: "added|removed|modified|deprecated|renamed"
  compatibility_impact: "none|patch|minor|major|unknown"
  review_required: boolean
```

## 11.20 RepositoryEvidence

```yaml
RepositoryEvidence:
  evidence_id: string
  inspected_files: list[FileRef]
  observed_public_surfaces: list[PublicSurfaceContract]
  observed_dependencies: list[string]
  observed_tests: list[FileRef]
  notes: string|null
```

## 11.21 StatusTransition

```yaml
StatusTransition:
  from_status: LifecycleStatus
  to_status: LifecycleStatus
  allowed: boolean
  required_evidence: list[EvidenceRequirement]
  required_review_gate: ReviewGate|null
```

## 11.22 WaiverRecord

```yaml
WaiverRecord:
  waiver_id: string
  waived_requirement: string
  reason: string
  approved_by: "user|maintainer|reviewer|not_assigned"
  expires: string|null
  risk_accepted: boolean
```

---

# 12. Shared Supporting Types

## 12.1 MissingContextItem

```yaml
MissingContextItem:
  item_id: string
  missing_type: "document|file|symbol|interface|test|validation|authority|dependency|risk|evidence"
  description: string
  blocking: boolean
```

## 12.2 ScopeSet

```yaml
ScopeSet:
  documents: list[DocumentRef]
  files: list[FileRef]
  units: list[UnitRef]
  allowed_actions: list[string]
  forbidden_actions: list[string]
```

## 12.3 UnitRef

```yaml
UnitRef:
  unit_id: string
  title: string
  fic_path: string|null
  status: string|null
  responsibility: string
```

## 12.4 UnitizationTarget

```yaml
UnitizationTarget:
  unit_id: string
  responsibility: string
  source_sections: list[string]
  must_split_if: list[string]
  must_not_include: list[string]
```

## 12.5 ReviewGate

```yaml
ReviewGate:
  required: boolean
  review_level: "none|standard|strict|critical"
  approver: "user|maintainer|reviewer|not_assigned"
  acceptance_rule: string
```

## 12.6 ValidationCommand

```yaml
ValidationCommand:
  command_id: string
  command: string
  required: boolean
  expected_result: "pass|fail_allowed|informational"
  evidence_required: boolean
```

## 12.7 ValidationResult

```yaml
ValidationResult:
  command_id: string
  command: string
  result: "pass|fail|not_run|waived"
  evidence: EvidenceRef|null
  notes: string|null
```

## 12.8 StopCondition

```yaml
StopCondition:
  condition_id: string
  condition: string
  required_status: "BLOCKED|NO_CHANGE|DEFERRED"
  required_record: string
```

## 12.9 TraceabilityBinding

```yaml
TraceabilityBinding:
  source_id: string
  source_type: "goal|requirement|pseudocode|fic|code|test|validation|review"
  target_id: string
  target_type: "goal|requirement|pseudocode|fic|code|test|validation|review"
  relation: "governs|implements|validates|reviews|supersedes|blocks|references"
```

## 12.10 RollbackExpectations

```yaml
RollbackExpectations:
  required: boolean
  rollback_scope: list[ArtifactRef]
  rollback_method: string
  irreversible_actions_allowed: boolean
  notes: string|null
```

---

# 13. Interface Ownership Rules

```text
1. Every shared interface must have one owning document.
2. Every public surface must have one owning FIC unit.
3. Shared interfaces must not be redefined inside individual FIC units.
4. FIC units may reference shared interfaces but must not silently change them.
5. A change to a shared interface is a functional change unless explicitly classified otherwise.
6. Duplicate interface ownership must block implementation.
7. Interface stability must be declared as draft, stable, frozen, or deprecated.
```

---

# 14. Versioning Rules

```text
1. Shared type changes must update this document version.
2. Adding a new optional field is normally a minor-compatible change.
3. Removing a field is a breaking change.
4. Changing status semantics is a functional governance change.
5. Changing lifecycle outcomes affects all dependent FIC units.
6. Lower-level documents must cite the shared type version they depend on.
7. A FIC unit using an older shared type version must declare whether it remains compatible.
```

---

# 15. Status Transition Rules

```text
BLOCKED may move to DEFERRED only with a recorded reason.
BLOCKED may move to IMPLEMENTED only after the blocking condition is resolved.
NO_CHANGE may move to ACCEPTED only after review or accepted evidence.
IMPLEMENTED may move to VALIDATED only with validation evidence or waiver.
VALIDATED may move to ACCEPTED only through review.
VALIDATED may move to REJECTED if review finds insufficient evidence or governance failure.
DEFERRED may move back into workflow only through a new request or document update.
REJECTED may move to IMPLEMENTED only through a revised request or corrected FIC/handoff.
```

---

# 16. Validator Readiness Rules

```text
1. Every referenced shared type must be defined in this document.
2. Every enum-like value must be listed in this document before use.
3. Every FIC unit must reference this document version when using these contracts.
4. A missing shared type definition is a blocking issue.
5. A type shape conflict between a FIC unit and this document is a blocking issue.
6. Validators may treat the YAML blocks in this file as schema-like contracts, but this document is not itself executable code.
```

---

# 17. Acceptance Criteria for This Document

This document is acceptable when:

- it defines the shared statuses used by Agent_X workflows
- it defines request classifications and workflow decisions
- it defines common records used by pseudocode, FIC units, handoffs, completion records, review packets, and traceability
- it prevents duplicated interface definitions across FIC units
- it distinguishes implementation, validation, and acceptance
- it defines ownership rules for shared interfaces
- it defines atomic field-level types used by shared records
- it defines public command, config key, event, export, and side-effect shapes
- it defines repository evidence and public-surface-change records
- it defines status-transition and waiver records
- it provides enough structure for `L1/fic/*.md` to reference instead of redefining shared contracts

---

# 18. Non-Authority Statement

This document defines shared contracts and vocabulary.

It does not authorize code changes by itself. Governed implementation still requires a FIC unit document, bounded handoff, validation evidence, and review.
