# 03_L1_WHOLE_SYSTEM_PSEUDOCODE.md

```yaml
document_id: "WHOLE-SYSTEM-PSEUDOCODE-001"
project: "Agent_X"
title: "Whole-System Pseudocode"
version: "1.5"
status: "ready-for-project-review"
document_type: "whole-system-pseudocode"
intended_location: "L1/docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md"
authority_level: "whole-system-flow"
last_updated: "2026-05-31"
governed_by:
  - "L1/docs/00_L1_SYSTEM_GOAL.md"
requires:
  - "L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md"
  - "future L1/docs/03_traceability_matrix.md"
  - "L1/fic/*.md"
supersedes:
  - "WHOLE-SYSTEM-PSEUDOCODE-001 v1.4"
change_classification: "final-readiness-and-boundary-tightening"
runtime_effect: "none"
```

---

# 1. Purpose

This document describes the intended whole-system workflow for Agent_X at the governance and process level.

It translates the root system goal into structured pseudocode that can later be split into bounded FIC unit documents.

This document is not direct coding instruction. Governed implementation must be decomposed into FIC unit documents before code is written or changed.

---

# 2. Governing Goal

Agent_X exists to support governed creation, modification, validation, and evolution of agent systems while preserving:

- governance
- traceability
- reproducibility
- validation
- reversibility
- user approval authority

All pseudocode in this document must remain consistent with `L1/docs/00_L1_SYSTEM_GOAL.md`.

---

# 3. Whole-System Inputs

```text
Input:
  project_request
  current_project_state
  governing_documents
  standards_documents
  existing_repository_state
  user_constraints
  available_tools
  validation_requirements
```

Where:

```text
project_request:
  user-provided intent, task, change request, review request, or evolution request

current_project_state:
  known Agent_X documents, code, tests, standards, prior decisions, and current status

governing_documents:
  system goal, architecture contract, pseudocode documents, shared interfaces, FIC units

standards_documents:
  adopted reference standards such as EQC, EQC-FIC, EQC-SIB, and project-specific standards

existing_repository_state:
  current files, public surfaces, tests, dependencies, callers, and implementation evidence

user_constraints:
  explicit constraints such as hardware limits, governance limits, allowed scope, and approval requirements

available_tools:
  permitted tools for inspection, editing, validation, testing, and artifact generation

validation_requirements:
  checks, tests, review gates, traceability requirements, and acceptance criteria
```

---

# 4. Whole-System Outputs

```text
Output:
  classified_request
  impact_assessment
  required_context_set
  consistency_status
  workflow_decision
  FIC_or_document_delta
  implementation_handoff_packet
  validation_plan
  completion_or_blocked_record
  review_packet
  updated_traceability_record
```

The system must not claim implementation success unless validation evidence or explicit waiver evidence exists.

---

# 5. Request Lifecycle Summary

Every governed request should move through this lifecycle:

```text
capture
  -> classify
  -> load governing context
  -> check consistency
  -> assess impact
  -> choose workflow
  -> prepare document/FIC/handoff
  -> implement only if authorized
  -> validate
  -> build completion record
  -> review
  -> update traceability
```

If a blocking condition appears at any point, the workflow returns a blocked record instead of guessing.

---

# 6. High-Level Flow

```text
Procedure Agent_X_Workflow(project_request):

  request_record ← CaptureRequest(project_request)

  classified_request ← ClassifyRequest(request_record)

  governing_context ← LoadGoverningContext(classified_request)

  consistency_status ← CheckContextConsistency(governing_context)

  IF consistency_status != CONSISTENT:
      blocked_record ← BuildBlockedRecord(consistency_status)
      UpdateTraceability(blocked_record)
      RETURN blocked_record

  impact_assessment ← AssessImpact(classified_request, governing_context)

  workflow_decision ← SelectWorkflow(classified_request, impact_assessment)

  IF workflow_decision == DOCUMENT_ONLY:
      document_delta ← PrepareDocumentDelta(classified_request, governing_context)
      validation_plan ← PrepareDocumentValidationPlan(document_delta)
      review_packet ← BuildReviewPacket(document_delta, validation_plan)
      UpdateTraceability(review_packet)
      RETURN review_packet

  IF workflow_decision == FIC_REQUIRED:
      fic_scope ← DeriveFICScope(classified_request, impact_assessment)
      fic_unit_plan ← CreateOrUpdateFICUnits(fic_scope, governing_context)
      fic_validation ← ValidateFICBundle(fic_unit_plan)

      IF fic_validation != FIC_BUNDLE_READY:
          blocked_record ← BuildBlockedRecord(fic_validation)
          UpdateTraceability(blocked_record)
          RETURN blocked_record

      handoff_packet ← BuildCodingAgentHandoff(fic_unit_plan)
      UpdateTraceability(handoff_packet)
      RETURN handoff_packet

  IF workflow_decision == IMPLEMENTATION_ALLOWED:
      handoff_packet ← BuildCodingAgentHandoff(classified_request)
      implementation_result ← ExecuteBoundedImplementation(handoff_packet)
      validation_result ← RunRequiredValidation(implementation_result)

      completion_record ← BuildCompletionRecord(
          implementation_result,
          validation_result
      )

      review_packet ← BuildReviewPacket(completion_record, validation_result)
      UpdateTraceability(review_packet)

      RETURN review_packet

  IF workflow_decision == NO_CHANGE:
      evidence ← CollectNoChangeEvidence(classified_request, governing_context)
      no_change_record ← BuildNoChangeRecord(evidence)
      UpdateTraceability(no_change_record)
      RETURN no_change_record

  blocked_record ← BuildBlockedRecord("UNKNOWN_WORKFLOW_DECISION")
  UpdateTraceability(blocked_record)
  RETURN blocked_record
```

---

# 7. Request Classification

```text
Procedure ClassifyRequest(request_record):

  IF request asks to add, modify, delete, or refactor code:
      return CODE_CHANGE_REQUEST

  IF request asks to add or modify governing documents:
      return DOCUMENT_CHANGE_REQUEST

  IF request asks to inspect, score, compare, or review artifacts:
      return REVIEW_REQUEST

  IF request asks to evolve Agent_X architecture or standards:
      return GOVERNANCE_EVOLUTION_REQUEST

  IF request asks to generate a FIC unit or implementation handoff:
      return FIC_WORKFLOW_REQUEST

  IF request asks whether something already satisfies requirements:
      return NO_CHANGE_CHECK_REQUEST

  IF request asks to run validation or summarize validation evidence:
      return VALIDATION_REQUEST

  return UNCLASSIFIED_REQUEST
```

If a request is unclassified and the missing classification affects behavior, the workflow must return `BLOCKED_UNCLASSIFIED_REQUEST` rather than guessing.

---

# 8. Context Loading

```text
Procedure LoadGoverningContext(classified_request):

  context ← {}

  context.system_goal ← Load("L1/docs/00_L1_SYSTEM_GOAL.md")

  context.architecture_contract ← LoadIfExists("L1/docs/architecture_contract.md")

  context.whole_system_pseudocode ← Load("L1/docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md")

  context.shared_interfaces ← LoadIfExists("L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md")

  context.traceability_matrix ← LoadIfExists("future L1/docs/03_traceability_matrix.md")

  context.relevant_fic_units ← FindRelevantFICUnits(classified_request)

  context.relevant_standards ← FindRelevantStandards(classified_request)

  context.repository_evidence ← InspectRelevantRepositoryState(classified_request)

  context.validation_evidence ← FindRelevantValidationEvidence(classified_request)

  context.missing_context ← IdentifyMissingRequiredContext(context, classified_request)

  RETURN context
```

Only relevant context should be loaded for bounded implementation work. Broad repository dumps must not replace selected context.

---

# 9. Consistency Checking

```text
Procedure CheckContextConsistency(context):

  IF system_goal is missing:
      return BLOCKED_MISSING_SYSTEM_GOAL

  IF context.missing_context is not empty:
      return BLOCKED_MISSING_REQUIRED_CONTEXT

  IF request requires implementation AND no relevant FIC exists:
      return BLOCKED_FIC_REQUIRED

  IF required shared interface is missing:
      return BLOCKED_MISSING_SHARED_INTERFACE

  IF target file exists BUT existing code cannot be inspected:
      return BLOCKED_EXISTING_CODE_UNAVAILABLE

  IF governing documents conflict:
      return BLOCKED_CONFLICTING_AUTHORITY

  IF state ownership is duplicated:
      return BLOCKED_DUPLICATED_STATE_OWNERSHIP

  IF public surface ownership is duplicated:
      return BLOCKED_DUPLICATED_PUBLIC_SURFACE

  IF validation requirements are undefined for governed implementation:
      return BLOCKED_UNDEFINED_VALIDATION

  IF a document claims runtime behavior without implementation and validation evidence:
      return BLOCKED_UNSUPPORTED_RUNTIME_CLAIM

  return CONSISTENT
```

---

# 10. Impact Assessment

```text
Procedure AssessImpact(classified_request, context):

  impact ← NewImpactAssessment()

  impact.affected_documents ← FindAffectedDocuments(classified_request, context)

  impact.affected_fic_units ← FindAffectedFICUnits(classified_request, context)

  impact.affected_code_files ← FindAffectedCodeFiles(classified_request, context)

  impact.affected_tests ← FindAffectedTests(classified_request, context)

  impact.affected_interfaces ← FindAffectedSharedInterfaces(classified_request, context)

  impact.affected_standards ← FindAffectedStandards(classified_request, context)

  impact.risk_level ← EstimateRiskLevel(impact)

  impact.requires_user_approval ← DetermineApprovalRequirement(impact)

  impact.requires_rollback_plan ← DetermineRollbackRequirement(impact)

  impact.requires_validation ← DetermineValidationRequirement(impact)

  impact.allowed_scope ← DetermineAllowedScope(impact)

  impact.forbidden_scope ← DetermineForbiddenScope(impact)

  impact.minimum_evidence ← DetermineMinimumEvidence(impact)

  impact.review_gate ← DetermineReviewGate(impact)

  impact.unitization_target ← DetermineUnitizationTarget(impact)

  RETURN impact
```

Impact assessment must include enough information to prevent uncontrolled scope expansion.

---

# 11. Workflow Selection

```text
Procedure SelectWorkflow(classified_request, impact_assessment):

  IF impact_assessment.risk_level is unknown:
      return BLOCKED_UNKNOWN_RISK_LEVEL

  IF classified_request == REVIEW_REQUEST:
      return DOCUMENT_ONLY

  IF classified_request == DOCUMENT_CHANGE_REQUEST:
      return DOCUMENT_ONLY

  IF classified_request == GOVERNANCE_EVOLUTION_REQUEST:
      return DOCUMENT_ONLY

  IF classified_request == FIC_WORKFLOW_REQUEST:
      return FIC_REQUIRED

  IF classified_request == NO_CHANGE_CHECK_REQUEST:
      return NO_CHANGE

  IF classified_request == VALIDATION_REQUEST:
      return DOCUMENT_ONLY

  IF classified_request == CODE_CHANGE_REQUEST:
      IF no valid FIC governs the requested code change:
          return FIC_REQUIRED
      ELSE:
          return IMPLEMENTATION_ALLOWED

  return BLOCKED_UNKNOWN_WORKFLOW
```

Code change requests must not bypass FIC creation or FIC validation.

---

# 12. FIC Unit Derivation

```text
Procedure DeriveFICScope(classified_request, impact_assessment):

  fic_scope ← {}

  fic_scope.primary_unit ← IdentifyPrimaryImplementationUnit(classified_request)

  fic_scope.unitization_target ← impact_assessment.unitization_target

  fic_scope.target_files ← IdentifyTargetFiles(impact_assessment)

  fic_scope.allowed_files ← DetermineAllowedFiles(impact_assessment)

  fic_scope.forbidden_files ← DetermineForbiddenFiles(impact_assessment)

  fic_scope.public_surface ← IdentifyOrDefinePublicSurface(classified_request)

  fic_scope.inputs_outputs ← IdentifyInputsAndOutputs(classified_request)

  fic_scope.state_ownership ← IdentifyStateOwnership(impact_assessment)

  fic_scope.dependencies ← IdentifyAllowedDependencies(impact_assessment)

  fic_scope.non_goals ← DeriveNonGoalsFromSystemGoalAndRequest()

  fic_scope.stop_conditions ← DefineStopConditions()

  fic_scope.tests ← DefineRequiredTests(impact_assessment)

  fic_scope.validation_commands ← DefineValidationCommands(impact_assessment)

  fic_scope.completion_evidence ← DefineCompletionEvidence()

  fic_scope.rollback_expectations ← DefineRollbackExpectations(impact_assessment)

  fic_scope.review_gate ← impact_assessment.review_gate

  fic_scope.traceability_bindings ← DefineTraceabilityBindings(impact_assessment)

  RETURN fic_scope
```

A FIC unit must define what the implementation may do, what it must not do, what evidence is required, and how the result will be traced.

---

# 13. FIC Bundle Validation

```text
Procedure ValidateFICBundle(fic_unit_plan):

  IF any FIC lacks target file:
      return BLOCKED_FIC_TARGET_FILE_MISSING

  IF any FIC lacks public surface:
      return BLOCKED_FIC_PUBLIC_SURFACE_MISSING

  IF any FIC lacks non-goals:
      return BLOCKED_FIC_NON_GOALS_MISSING

  IF any FIC lacks dependency rules:
      return BLOCKED_FIC_DEPENDENCY_RULES_MISSING

  IF any FIC lacks state ownership rule:
      return BLOCKED_FIC_STATE_OWNERSHIP_MISSING

  IF any FIC lacks error behavior:
      return BLOCKED_FIC_ERROR_BEHAVIOR_MISSING

  IF any FIC lacks validation requirements:
      return BLOCKED_FIC_VALIDATION_MISSING

  IF any FIC conflicts with system goal:
      return BLOCKED_FIC_CONFLICTS_WITH_SYSTEM_GOAL

  IF any FIC creates unsupported runtime claim:
      return BLOCKED_UNSUPPORTED_RUNTIME_CLAIM

  IF any FIC allows broad scope without explicit authorization:
      return BLOCKED_FIC_SCOPE_TOO_BROAD

  IF any FIC lacks completion evidence requirements:
      return BLOCKED_FIC_COMPLETION_EVIDENCE_MISSING

  IF any FIC lacks review gate:
      return BLOCKED_FIC_REVIEW_GATE_MISSING

  IF any FIC lacks traceability bindings:
      return BLOCKED_FIC_TRACEABILITY_BINDINGS_MISSING

  IF any FIC lacks stop conditions:
      return BLOCKED_FIC_STOP_CONDITIONS_MISSING

  return FIC_BUNDLE_READY
```

---

# 14. Coding-Agent Handoff

```text
Procedure BuildCodingAgentHandoff(fic_unit_plan):

  handoff ← {}

  handoff.primary_fic ← SelectPrimaryFIC(fic_unit_plan)

  handoff.allowed_files ← fic_unit_plan.allowed_files

  handoff.forbidden_files ← fic_unit_plan.forbidden_files

  handoff.required_context ← SelectRelevantContext(fic_unit_plan)

  handoff.forbidden_actions ← ExtractForbiddenActions(fic_unit_plan)

  handoff.public_surface_contract ← ExtractPublicSurface(fic_unit_plan)

  handoff.validation_commands ← ExtractValidationCommands(fic_unit_plan)

  handoff.completion_record_schema ← LoadCompletionRecordSchema()

  handoff.stop_conditions ← DefineStopConditions(fic_unit_plan)

  handoff.traceability_bindings ← fic_unit_plan.traceability_bindings

  handoff.required_output_statuses ← [
      BLOCKED,
      NO_CHANGE,
      IMPLEMENTED,
      VALIDATED
  ]

  RETURN handoff
```

The handoff must be bounded. The coding agent must not receive permission to infer missing architecture, invent APIs, or expand scope.

---

# 15. Bounded Implementation

```text
Procedure ExecuteBoundedImplementation(handoff_packet):

  Inspect required existing files.

  IF required file or symbol cannot be inspected:
      return BLOCKED_REQUIRED_INSPECTION_FAILED

  IF existing code already satisfies FIC:
      return NO_CHANGE_WITH_EVIDENCE

  IF implementation requires editing files outside allowed scope:
      return BLOCKED_SCOPE_EXPANSION_REQUIRED

  IF implementation requires changing public surface not authorized by FIC:
      return BLOCKED_PUBLIC_SURFACE_CHANGE_REQUIRED

  IF implementation requires missing dependency:
      return BLOCKED_DEPENDENCY_UNDEFINED

  IF implementation requires unsupported runtime behavior:
      return BLOCKED_UNSUPPORTED_RUNTIME_BEHAVIOR

  Apply smallest satisfying change.

  Create or update required tests.

  Produce implementation summary.

  RETURN IMPLEMENTED
```

---

# 16. Validation

```text
Procedure RunRequiredValidation(implementation_result):

  IF implementation_result is BLOCKED:
      return VALIDATION_NOT_RUN_BLOCKED

  IF implementation_result is NO_CHANGE:
      return VALIDATION_OPTIONAL_OR_EVIDENCE_ONLY

  validation_results ← []

  FOR each required validation command:
      result ← RunValidationCommand(command)
      validation_results.append(result)

  IF any required validation fails:
      return VALIDATION_FAILED(validation_results)

  return VALIDATION_PASSED(validation_results)
```

Validation results must be recorded. A claim that validation passed must be backed by actual validation evidence.

---

# 17. Completion Record

```text
Procedure BuildCompletionRecord(implementation_result, validation_result):

  record.status ← DetermineCompletionStatus(implementation_result, validation_result)

  record.files_inspected ← ListInspectedFiles()

  record.files_changed ← ListChangedFiles()

  record.public_surface_changes ← ListPublicSurfaceChanges()

  record.tests_added_or_updated ← ListTestsChanged()

  record.validation_results ← validation_result

  record.deviations_from_fic ← ListDeviations()

  record.unresolved_risks ← ListUnresolvedRisks()

  record.rollback_notes ← BuildRollbackNotesIfRequired()

  record.review_required ← DetermineReviewRequirement()

  record.traceability_bindings ← ListTraceabilityBindings()

  record.acceptance_status ← NOT_ACCEPTED_UNTIL_REVIEWED

  RETURN record
```

Completion status must distinguish:

```text
BLOCKED
NO_CHANGE
IMPLEMENTED
VALIDATED
REJECTED
DEFERRED
```

---

# 18. Status Semantics

```text
BLOCKED:
  Work cannot proceed because required context, authority, validation, safety, or dependency information is missing or conflicting.

NO_CHANGE:
  Inspected artifacts already satisfy the governing contract, and evidence is recorded.

IMPLEMENTED:
  A change was made, but the change is not accepted and may not be validated yet.

VALIDATED:
  Required checks passed or accepted waivers exist, but review acceptance may still be pending.

ACCEPTED:
  Review confirms that the validated evidence is sufficient for the governed scope.

REJECTED:
  Review or validation found unacceptable scope, behavior, evidence, risk, or governance problems.

DEFERRED:
  Work is intentionally postponed and excluded from the current acceptance scope.
```

Implementation, validation, and acceptance are separate states.

---

# 19. Review and Acceptance

```text
Procedure BuildReviewPacket(completion_record, validation_result):

  review_packet ← {}

  review_packet.summary ← SummarizeChangeOrDecision()

  review_packet.governing_documents ← ListGoverningDocuments()

  review_packet.affected_artifacts ← ListAffectedArtifacts()

  review_packet.evidence ← CollectEvidence(completion_record, validation_result)

  review_packet.risks ← CollectRisks()

  review_packet.deviations ← CollectDeviations()

  review_packet.traceability_bindings ← completion_record.traceability_bindings

  review_packet.review_gate ← DetermineReviewGateFromImpactOrFIC()

  review_packet.acceptance_options ← [
      ACCEPT,
      REJECT,
      REQUEST_REVISION,
      DEFER,
      MARK_BLOCKED
  ]

  RETURN review_packet
```

No meaningful governed change is accepted until review determines that the evidence is sufficient.

---

# 20. Traceability Update

```text
Procedure UpdateTraceability(record):

  Link request to governing document.

  Link governing document to FIC unit.

  Link FIC unit to implementation files.

  Link implementation files to tests.

  Link tests to validation evidence.

  Link validation evidence to review outcome.

  Store unresolved risks or deviations.

  RETURN UPDATED_TRACEABILITY_RECORD
```

No governed behavior should remain without an owning document and validation path.

---

# 21. Failure Handling

```text
Procedure BuildBlockedRecord(reason):

  record.status ← BLOCKED
  record.reason ← reason
  record.required_missing_information ← IdentifyMissingInformation(reason)
  record.affected_artifacts ← IdentifyAffectedArtifacts(reason)
  record.allowed_next_document_action ← DetermineRequiredDocumentAction(reason)

  RETURN record
```

Blocked outcomes are valid results. They prevent uncontrolled guessing and uncontrolled implementation.

---

# 22. No-Change Handling

```text
Procedure BuildNoChangeRecord(evidence):

  record.status ← NO_CHANGE
  record.evidence ← evidence
  record.files_inspected ← ListInspectedFiles()
  record.governing_documents ← ListGoverningDocuments()
  record.reason ← "Existing artifacts already satisfy the governing contract."

  RETURN record
```

No-change claims require inspection evidence.

---

# 23. Whole-System Invariants

Agent_X must preserve these invariants:

```text
INV-001: Governed code changes require an owning FIC or explicit waiver.
INV-002: Generated code does not override higher-authority documents.
INV-003: Missing required context produces BLOCKED, not guessed implementation.
INV-004: Public surface changes require classification and review.
INV-005: State ownership must be explicit.
INV-006: Validation evidence must be recorded before claiming validation success.
INV-007: Runtime behavior must not be claimed unless implemented and validated.
INV-008: Standards are references until adopted through project-specific usage rules.
INV-009: Broad pseudocode is not direct coding instruction.
INV-010: Human approval authority is preserved for meaningful acceptance decisions.
INV-011: Completion claims distinguish implementation, validation, and acceptance.
INV-012: Exploratory work is not promoted into governed status without review.
INV-013: A validated change is not automatically an accepted change.
INV-014: A FIC handoff must define allowed files, forbidden files, stop conditions, and required evidence.
INV-015: FIC units and completion records must include traceability bindings.
INV-016: FIC unitization must preserve bounded responsibility and must not collapse unrelated workflow stages into one unit.
```

---

# 24. Unitization Targets

This whole-system pseudocode should be split into FIC units such as:

```text
UNIT-001 request intake and classification
UNIT-002 governing context loader
UNIT-003 consistency checker
UNIT-004 impact assessment engine
UNIT-005 workflow selector
UNIT-006 FIC scope derivation
UNIT-007 FIC bundle validator
UNIT-008 coding-agent handoff builder
UNIT-009 bounded implementation runner
UNIT-010 validation runner
UNIT-011 completion record builder
UNIT-012 review packet builder
UNIT-013 traceability updater
UNIT-014 blocked/no-change outcome handler
```

Each unit must receive its own FIC document before governed implementation.

---

# 25. Acceptance Criteria for This Document

This document is acceptable when:

- it translates the system goal into whole-system pseudocode
- it avoids direct implementation details
- it defines major workflow stages
- it defines blocked/no-change/implemented/validated/rejected/deferred outcomes
- it preserves FIC-before-code governance
- it defines enough units to support later FIC decomposition
- it avoids unsupported runtime claims
- it can be used as a source document for `L1/fic/*.md`
- it makes no-change and blocked outcomes first-class
- it distinguishes implementation, validation, review, and acceptance
- it defines what evidence is required before implementation success is claimed
- it defines review-gate handling before acceptance
- it requires traceability bindings for FIC handoffs and completion records
- it preserves bounded unit responsibility for later FIC decomposition

---

# 26. Non-Authority Statement

This document does not authorize code changes by itself.

Any governed implementation must be derived from this document into one or more FIC unit documents and validated through the FIC workflow before coding.
