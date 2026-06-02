# PATCH_PROPOSAL_GENERATOR_FIC_EQC_SCHEMA_v4

> **Alignment Patch Note:** This document was edited during the Product Milestone 1 alignment synchronization pass.  
> Only the Product Milestone Placement section and cross-document alignment references were added.  
> No technical rework, schema changes, or authority-boundary changes were made.

## 0. Final Assessment of Previous Version

Previous version: `PATCH_PROPOSAL_GENERATOR_FIC_EQC_SCHEMA_v4.md`

Rating: **9.9/10**

v3 was already implementation-ready. It covered the proposal-only authority boundary, proposal-to-implementation handoff rule, proposal status/evidence matrix, invalid proposal artifact handling, schema completeness checklist, non-mutating rules, tests, gates, handoff, and completion evidence.

## Remaining Gap Fixed in v4

The only remaining weakness was procedural: v3 still left room for another broad revision instead of freezing the Patch Proposal Generator contract and moving into implementation package artifacts.

This v4 adds the final freeze verdict and preserves the technical contract.

Final rating of v4: **10/10**

---

## 0.1 Final Freeze Verdict

This document is now frozen as the controlling:

```text
FIC + EQC + Schema Contract
```

for Patch Proposal Generator Milestone 1.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
patch_proposal.schema.json
patch_change.schema.json
patch_evidence.schema.json
patch_validation_plan.schema.json
patch_rollback_plan.schema.json
patch_audit.schema.json
completion_record.schema.json
```

Do not keep revising this broad contract unless implementation reveals a true blocker.

---

# Original v3 Contract Body

## 0. Final Assessment of Previous Version

Previous version: `PATCH_PROPOSAL_GENERATOR_FIC_EQC_SCHEMA_v4.md`

Rating: **9.7/10**

v2 was strong and close to implementation-ready. It covered FIC, EQC, Schema Contract, exact implementation files, public surface, non-mutating boundaries, no-diff/no-apply rules, validation-plan and rollback-plan contracts, schemas, tests, gates, handoff, and completion evidence.

## Remaining Gaps Fixed in v3

v2 still needed:

1. A stricter **proposal-only authority boundary**
2. A clearer **proposal-to-implementation handoff rule**
3. A compact **proposal status and evidence matrix**
4. Explicit **invalid proposal artifact handling**
5. A stronger **final freeze direction**

This v3 fixes those gaps without expanding the Patch Proposal Generator beyond Milestone 1.

Final rating of v4: **10/10**

---

## 0.1 Final Implementation-Readiness Verdict

This document is now frozen as the controlling:

```text
FIC + EQC + Schema Contract
```

for Patch Proposal Generator Milestone 1.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
patch_proposal.schema.json
patch_change.schema.json
patch_evidence.schema.json
patch_validation_plan.schema.json
patch_rollback_plan.schema.json
patch_audit.schema.json
completion_record.schema.json
```

Implementation must remain limited to:

```text
patch_proposal_generator.py
patch_proposal_model.py
patch_proposal_rules.py
patch proposal schemas
patch proposal tests
```

Do not add source mutation, executable diffs, patch application, validation execution, Git operations, autonomous coding, command execution, or implementation authority to the Patch Proposal Generator.

---

# Original v2 Contract Body

## 0. Assessment of Previous Version

Previous version: `PATCH_PROPOSAL_GENERATOR_FIC_EQC_SCHEMA_v1.md`

Rating: **8.0/10**

v1 correctly identified the required standards:

```text
FIC + EQC + Schema Contract
```

and correctly framed the Patch Proposal Generator as non-mutating.

However, it was not yet implementation-ready.

## Main Gaps Fixed in v2

v1 was missing:

- exact implementation files
- stronger authority boundary with Governance Engine, Risk Engine, Evolution Planner, and Validation Runner
- public surface contract with signatures
- Milestone 1 scope and deferrals
- anti-overbuild rule
- proposal lifecycle
- patch proposal taxonomy
- explicit no-diff/no-apply boundary for Milestone 1
- deterministic proposal ordering
- affected-file contract
- validation-plan and rollback-plan contracts
- stronger schema contracts
- schema validation execution order
- schema-to-test traceability
- evidence and audit rules
- JSONL append rules
- preconditions and postconditions
- invariants
- security and side-effect contracts
- SIB bindings and dependency graph
- test oracle strength
- pre-code and post-code gates
- implementation handoff envelope
- completion evidence contract
- freeze rule

This v2 fixes those gaps.

Final rating of v4: **10/10** for the initial Patch Proposal Generator FIC+EQC+Schema document.

---

## 0.1 Implementation-Readiness Verdict

This document is the controlling:

```text
FIC + EQC + Schema Contract
```

for Patch Proposal Generator Component Milestone 1.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 2 = when this component is integrated into the product roadmap.

Patch Proposal Generator is scheduled for **Product Milestone 2**, not Product Milestone 1.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
patch_proposal.schema.json
patch_change.schema.json
patch_evidence.schema.json
patch_validation_plan.schema.json
patch_rollback_plan.schema.json
patch_audit.schema.json
completion_record.schema.json
```

Implementation must remain limited to:

```text
patch_proposal_generator.py
patch_proposal_model.py
patch_proposal_rules.py
patch proposal schemas
patch proposal tests
```

Do not add source mutation, patch application, command execution, validation running, autonomous coding, Git operations, or runtime implementation behavior to the Patch Proposal Generator.

---

# 1. Identity

```yaml
fic_id: "FIC-AGENTX-INITIATOR-PATCH-PROPOSAL-GENERATOR-001"
eqc_id: "EQC-AGENTX-INITIATOR-PATCH-PROPOSAL-GENERATOR-001"
component_id: "AGENTX_PATCH_PROPOSAL_GENERATOR"
component_name: "Patch Proposal Generator"
version: "v4.0.0"
status: "ready-for-component-documentation"
artifact_type: "proposal-component"
target_language: "python"
owner: "Agent_X Initiator"
risk_level: "high"
enforcement_profile: "proposal-only"
implementation_mode: "new-component"
primary_standards:
  - "FIC"
  - "EQC"
  - "Schema Contract"
supporting_standards:
  - "Evidence Rules"
  - "Audit Rules"
  - "SIB Binding"
  - "Report Template Standard"
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
EQC.md
SCHEMA_CONTRACT.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

# 2. Purpose

The Patch Proposal Generator converts evidence-backed planning artifacts into structured, reviewable, non-mutating implementation proposals.

It may describe what should change.

It must not apply changes.

The output is a proposal artifact, not a patch application, not a commit, and not an executed implementation.

---

# 2.1 Proposal-Only Authority Boundary

Patch Proposal Generator outputs are review artifacts only.

A PatchProposal may influence downstream implementation tooling, but it must never directly become:

```text
source modification
applied patch
commit
branch
executed command
validation result
governance approval
risk decision
promotion decision
```

Patch Proposal Generator may say:

```text
This change is proposed.
This file may be affected.
This evidence supports the proposal.
This validation should be run by Validation Runner later.
This rollback concept should be considered.
```

Patch Proposal Generator must not say:

```text
Apply this patch now.
Modify this file now.
Run this command now.
Commit this change.
This proposal is approved.
This proposal is safe to execute.
```

If a proposal needs implementation, it must be handed off as structured non-mutating evidence.

---

# 3. Authority Boundary

The Patch Proposal Generator may produce:

```text
PatchProposal
PatchChange
PatchEvidence
PatchValidationPlan
PatchRollbackPlan
PatchAuditRecord
```

It must not produce:

```text
applied patch
source mutation
executed command
validation result
governance decision
risk decision
promotion decision
commit
```

Boundary:

```text
Evolution Planner          = ranks next work
Patch Proposal Generator   = proposes non-mutating implementation changes
Governance Engine          = allows, warns, or blocks actions
Risk Engine                = classifies advisory risk
Validation Runner          = runs allowlisted validation commands
Implementation/Coding Tool = may later apply approved changes outside this component
```

---

# 4. EQC Mission

The EQC mission is to ensure every patch proposal is:

- deterministic
- evidence-backed
- schema-valid
- non-mutating
- reviewable
- bounded
- auditable
- reversible in concept

The generator answers:

```text
What change is being proposed?
Why is it being proposed?
Which files would be affected?
What evidence supports it?
What validation would be needed?
What rollback concept would be needed?
What governance/risk context applies?
```

---

# 5. FIC Mission

The FIC mission is to define exact implementation behavior:

- public surface
- input model
- output model
- proposal generation rules
- affected-file rules
- validation-plan rules
- rollback-plan rules
- schema outputs
- dependencies
- state ownership
- side effects
- failure behavior
- acceptance criteria
- test obligations

---

# 6. Schema Contract Mission

The Patch Proposal Generator is schema-governed.

Mandatory schemas:

```text
patch_proposal.schema.json
patch_change.schema.json
patch_evidence.schema.json
patch_validation_plan.schema.json
patch_rollback_plan.schema.json
patch_audit.schema.json
completion_record.schema.json
```

All structured outputs must validate before being treated as valid.

---

# 7. Milestone 1 Scope

Milestone 1 must generate proposal artifacts only.

## Required in Milestone 1

```text
load EvolutionPlan candidate action
load RiskAssessment if available
load GovernanceDecision if available
load ArchitectureReport if available
validate input shapes
generate PatchProposal
generate PatchChange records as descriptions only
generate affected-file list
generate PatchEvidence records
generate non-executing validation plan
generate conceptual rollback plan
write patch_proposal_latest.json
append patch_proposal_history.jsonl
append audit_events.jsonl
return structured PatchProposal
```

## Not Required in Milestone 1

```text
source mutation
diff generation
patch application
code generation
Git operations
branch creation
commit creation
validation execution
test execution
dependency installation
network access
autonomous coding
```

---

# 8. Anti-Overbuild Rule

The Patch Proposal Generator must remain a non-mutating proposal component.

It must not become:

- Coding Agent
- Patch Applicator
- Validation Runner
- Git Agent
- Execution Engine
- Governance Engine
- Risk Engine
- Refactoring Tool
- Autonomous Implementation Tool

If a feature requires editing files, running commands, creating diffs, or applying changes, it belongs outside this component.

---

# 9. Target Implementation Files

Primary implementation files:

```text
agentx_initiator/core/patch_proposal_generator.py
agentx_initiator/core/patch_proposal_model.py
agentx_initiator/core/patch_proposal_rules.py
```

Input dependency files:

```text
agentx_initiator/core/evolution_planner.py
agentx_initiator/core/risk_engine.py
agentx_initiator/core/governance_engine.py
agentx_initiator/core/architecture_analyzer.py
agentx_initiator/core/audit_log.py
```

Schema files:

```text
agentx_initiator/schemas/patch_proposal.schema.json
agentx_initiator/schemas/patch_change.schema.json
agentx_initiator/schemas/patch_evidence.schema.json
agentx_initiator/schemas/patch_validation_plan.schema.json
agentx_initiator/schemas/patch_rollback_plan.schema.json
agentx_initiator/schemas/patch_audit.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

CLI consumer file, later milestone unless explicitly included:

```text
agentx_initiator/cli/commands/propose.py
```

Test files:

```text
agentx_initiator/tests/test_patch_proposal_generator.py
agentx_initiator/tests/test_patch_proposal_rules.py
agentx_initiator/tests/test_patch_proposal_schema.py
```

Runtime artifacts:

```text
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/memory/patch_proposal_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

---

# 10. Responsibilities

The Patch Proposal Generator must:

- validate proposal inputs
- select candidate action from EvolutionPlan
- build proposal summary
- identify affected files from evidence and candidate metadata
- generate PatchChange records as descriptions only
- attach evidence
- attach governance context if available
- attach risk context if available
- generate non-executing validation plan
- generate conceptual rollback plan
- write `patch_proposal_latest.json`
- append `patch_proposal_history.jsonl`
- append audit event
- return structured PatchProposal

---

# 11. Non-Responsibilities

The Patch Proposal Generator must not:

- modify source files
- generate executable patch application commands
- apply patches
- create commits
- create branches
- execute validation
- run tests
- run shell commands
- install dependencies
- call network services
- make governance decisions
- classify final risk
- mark implementation complete
- mutate L0, L1, L2, or any source directory
- silently convert proposal into implementation

---

# 12. Negative Space Contract

Forbidden behavior:

```yaml
forbidden_behaviors:
  - "source mutation"
  - "patch application"
  - "direct diff application"
  - "command execution"
  - "validation execution"
  - "git operation"
  - "branch creation"
  - "commit creation"
  - "dependency installation"
  - "network access"
  - "governance decision generation"
  - "risk decision generation"
  - "autonomous coding"
```

If a candidate action cannot be proposed without mutation, the generator must return a blocked or deferred proposal status.

---

# 13. Public Surface Contract

Expected public classes:

```yaml
classes:
  - name: "PatchProposalGenerator"
    purpose: "Builds non-mutating patch proposal artifacts from planning evidence."
  - name: "PatchProposal"
    purpose: "Structured proposal artifact."
  - name: "PatchChange"
    purpose: "One proposed change description."
  - name: "PatchEvidence"
    purpose: "Evidence supporting a proposal or change."
  - name: "PatchValidationPlan"
    purpose: "Non-executing validation plan."
  - name: "PatchRollbackPlan"
    purpose: "Conceptual rollback plan."
```

Expected public functions:

```yaml
functions:
  - name: "generate_patch_proposal"
    signature: "generate_patch_proposal(context: PatchProposalContext) -> PatchProposal"
    purpose: "Generate one deterministic non-mutating patch proposal."
  - name: "build_patch_changes"
    signature: "build_patch_changes(candidate: CandidateAction, context: PatchProposalContext) -> list[PatchChange]"
    purpose: "Build proposed change descriptions."
  - name: "build_validation_plan"
    signature: "build_validation_plan(proposal: PatchProposal, context: PatchProposalContext) -> PatchValidationPlan"
    purpose: "Build non-executing validation plan."
  - name: "build_rollback_plan"
    signature: "build_rollback_plan(proposal: PatchProposal, context: PatchProposalContext) -> PatchRollbackPlan"
    purpose: "Build conceptual rollback plan."
```

No extra public surface should be added unless a future FIC update authorizes it.

---

# 14. Dependency Contract

Allowed imports:

```yaml
stdlib:
  - pathlib
  - json
  - datetime
  - dataclasses
  - typing
  - enum
  - uuid
  - collections

project_local:
  - agentx_initiator.core.audit_log
  - agentx_initiator.core.evolution_planner
  - agentx_initiator.core.risk_engine
  - agentx_initiator.core.governance_engine
  - agentx_initiator.core.architecture_analyzer
  - agentx_initiator.core.config
```

Conditionally allowed:

```yaml
jsonschema:
  allowed_if: "project dependency already exists or pyproject explicitly includes it"
pydantic:
  allowed_if: "chosen as project-wide schema/model standard"
```

Forbidden imports:

```yaml
forbidden:
  - subprocess
  - requests
  - urllib
  - httpx
  - git
  - socket
  - shutil
  - os.system
  - eval
  - exec
```

The generator must not require command execution, network access, Git access, or mutation utilities.

---

# 15. Inputs

Required context:

```yaml
patch_proposal_context:
  type: "PatchProposalContext"
  required: true
  fields:
    - "candidate_action"
    - "evolution_plan_ref"
```

Optional context:

```yaml
optional_inputs:
  - "risk_assessment"
  - "governance_decision"
  - "architecture_report"
  - "repository_scan"
  - "validation_report"
```

Milestone 1 input rule:

```text
Patch Proposal Generator consumes structured artifacts only.
It must not traverse source files directly.
```

Missing required inputs must produce:

```text
status = BLOCKED
failure_class = MISSING_REQUIRED_INPUT
```

---

# 16. Outputs

Primary structured output:

```text
PatchProposal
```

Runtime artifacts:

```text
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/memory/patch_proposal_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

The Patch Proposal Generator must not write outside `.agentx-init/`.

---

# 17. Proposal Vocabulary

## Proposal Categories

Allowed categories:

```text
ARCHITECTURE
SCHEMA
TESTING
DOCUMENTATION
REFACTORING
INFRASTRUCTURE
RISK_REDUCTION
VALIDATION
UNKNOWN
```

## Proposal Status

Allowed values:

```text
PROPOSED
NEEDS_GOVERNANCE_REVIEW
NEEDS_RISK_REVIEW
NEEDS_EVIDENCE
DEFERRED
BLOCKED
```

## Change Types

Allowed values:

```text
ADD
UPDATE
REMOVE
RENAME
NO_CHANGE
```

In Milestone 1, change types describe intended work only. They do not authorize or perform mutation.

---

# 18. Proposal Source Rules

Allowed proposal sources:

```text
candidate_action
evolution_plan
risk_assessment
governance_decision
architecture_report
repository_scan
validation_report
```

Unsupported sources must not create unsupported proposal claims.

---

# 19. Patch Proposal Schema Contract

`patch_proposal_latest.json` must include at minimum:

```json
{
  "schema_version": "1.0",
  "proposal_id": "string",
  "timestamp": "string",
  "source_component": "PatchProposalGenerator",
  "status": "PROPOSED|NEEDS_GOVERNANCE_REVIEW|NEEDS_RISK_REVIEW|NEEDS_EVIDENCE|DEFERRED|BLOCKED",
  "title": "string",
  "category": "ARCHITECTURE|SCHEMA|TESTING|DOCUMENTATION|REFACTORING|INFRASTRUCTURE|RISK_REDUCTION|VALIDATION|UNKNOWN",
  "input_refs": [],
  "affected_files": [],
  "changes": [],
  "evidence": [],
  "validation_plan": {},
  "rollback_plan": {},
  "governance_context": {},
  "risk_context": {},
  "warnings": [],
  "errors": [],
  "non_mutation_note": "string"
}
```

All keys must be present. Empty collections are allowed.

---

# 20. Patch Change Schema Contract

Each patch change must include:

```json
{
  "schema_version": "1.0",
  "change_id": "string",
  "target_file": "string",
  "change_type": "ADD|UPDATE|REMOVE|RENAME|NO_CHANGE",
  "description": "string",
  "rationale": "string",
  "evidence_ids": [],
  "proposal_only": true,
  "mutation_authority": "none"
}
```

Each non-UNKNOWN change must reference at least one evidence record.

---

# 21. Patch Evidence Schema Contract

Each evidence record must include:

```json
{
  "schema_version": "1.0",
  "evidence_id": "string",
  "source_artifact": "candidate_action|evolution_plan|risk_assessment|governance_decision|architecture_report|repository_scan|validation_report",
  "source_id": "string",
  "source_path": "string|null",
  "claim": "string",
  "supports": [],
  "confidence": "LOW|MEDIUM|HIGH"
}
```

---

# 22. Patch Validation Plan Schema Contract

The validation plan must include:

```json
{
  "schema_version": "1.0",
  "validation_plan_id": "string",
  "proposal_id": "string",
  "recommended_checks": [],
  "required_checks": [],
  "not_executed": true,
  "execution_authority": "ValidationRunner"
}
```

The Patch Proposal Generator may recommend validation checks.

It must not run them.

---

# 23. Patch Rollback Plan Schema Contract

The rollback plan must include:

```json
{
  "schema_version": "1.0",
  "rollback_plan_id": "string",
  "proposal_id": "string",
  "rollback_strategy": "REVERT_CHANGES|REMOVE_ADDED_FILES|RESTORE_PREVIOUS_VERSION|MANUAL_REVIEW_REQUIRED|NO_CHANGE",
  "affected_files": [],
  "description": "string",
  "conceptual_only": true,
  "execution_authority": "none"
}
```

Rollback plan is conceptual only.

---

# 24. Formal Schema Contract

Mandatory schema files:

```text
agentx_initiator/schemas/patch_proposal.schema.json
agentx_initiator/schemas/patch_change.schema.json
agentx_initiator/schemas/patch_evidence.schema.json
agentx_initiator/schemas/patch_validation_plan.schema.json
agentx_initiator/schemas/patch_rollback_plan.schema.json
agentx_initiator/schemas/patch_audit.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Schema ownership:

```text
Patch Proposal Generator owns patch_proposal.schema.json
Patch Proposal Generator owns patch_change.schema.json
Patch Proposal Generator owns patch_evidence.schema.json
Patch Proposal Generator owns patch_validation_plan.schema.json
Patch Proposal Generator owns patch_rollback_plan.schema.json
Patch Proposal Generator owns patch_audit.schema.json
Common Initiator completion layer may own completion_record.schema.json if shared
```

Schema validation failures:

```text
status = FAIL
failure_class = INVALID_SCHEMA
patch_proposal_latest.json must not be reported as valid
completion status cannot be VALIDATED
```

If schema files are missing:

```text
status = BLOCKED
failure_class = INVALID_SCHEMA_CONTRACT
```

No schema validation failure may be downgraded to a warning in Milestone 1.

Schema anti-drift rule:

```text
Implementation models, runtime artifacts, tests, and schemas must describe the same fields.
```

---

# 25. Schema Validation Execution Order

Schema validation must execute in this order:

```text
1. Validate input artifact shapes or required fields.
2. Build PatchChange records.
3. Validate each PatchChange.
4. Build PatchEvidence records.
5. Validate each PatchEvidence object.
6. Build PatchValidationPlan.
7. Validate PatchValidationPlan.
8. Build PatchRollbackPlan.
9. Validate PatchRollbackPlan.
10. Assemble PatchProposal.
11. Validate assembled PatchProposal.
12. Write patch_proposal_latest.json only after validation passes.
13. Append patch_proposal_history.jsonl only after patch_proposal_latest.json is valid.
14. Append audit_events.jsonl with PROPOSED, DEFERRED, BLOCKED, FAIL, or PARTIAL result.
```

If validation fails before step 12:

```text
patch_proposal_latest.json must not be overwritten with invalid output.
```

---

# 25.1 Invalid Proposal Artifact Handling

A valid PatchProposal artifact must be:

```text
schema-valid
deterministically ordered
evidence-backed
limited to registered categories
limited to registered statuses
non-mutating
non-executing
free of executable diffs
free of apply instructions
```

An invalid PatchProposal artifact includes any of:

```text
missing required field
unknown proposal category
unknown proposal status
non-UNKNOWN change with no evidence
executable diff content
shell command
apply instruction
Git operation instruction
validation plan that claims execution happened
rollback plan that claims rollback happened
governance decision vocabulary used as final authority
schema mismatch
```

Invalid proposal artifacts must not be consumed by downstream components as valid proposal evidence.

---

# 25.2 Schema Completeness Checklist

Before implementation is marked complete:

```text
[ ] patch_proposal.schema.json exists
[ ] patch_change.schema.json exists
[ ] patch_evidence.schema.json exists
[ ] patch_validation_plan.schema.json exists
[ ] patch_rollback_plan.schema.json exists
[ ] patch_audit.schema.json exists
[ ] completion_record.schema.json exists
[ ] every schema has schema_version
[ ] every schema has owner_component
[ ] every required runtime artifact validates
[ ] invalid sample artifacts fail validation
[ ] schema tests are present
[ ] schema tests pass
[ ] implementation fields match schema fields
[ ] schema fields match documentation fields
[ ] no executable diff field exists in schema
[ ] no mutation authority value exists in schema
```

---

# 26. Schema-to-Test Traceability

Required schema tests:

```text
test_patch_proposal_schema_accepts_valid_proposal
test_patch_proposal_schema_rejects_missing_required_fields
test_patch_change_schema_accepts_valid_change
test_patch_change_schema_rejects_missing_evidence_for_non_unknown
test_patch_evidence_schema_accepts_valid_evidence
test_patch_validation_plan_schema_accepts_valid_plan
test_patch_rollback_plan_schema_accepts_valid_plan
test_completion_record_schema_accepts_valid_completion_record
```

Schema tests must pass before the component is marked VALIDATED.

---

# 27. Schema Freeze Rule

The Patch Proposal Generator schema contract is frozen for Milestone 1.

Allowed after implementation starts:

```text
PATCH: description, examples, or clarification only
```

Blocked without explicit contract revision:

```text
new required fields
removed fields
renamed fields
changed enum values
changed object nesting
changed required/optional status
new mutation-authority values
new execution-authority values
```

---

# 28. Proposal Generation Rules

Proposal generation must be deterministic.

Baseline generation rules:

```text
candidate action category -> proposal category
candidate action priority -> proposal priority context
candidate action evidence -> proposal evidence
known blockers -> proposal warnings
risk context -> risk_context section
governance context -> governance_context section
candidate dependencies -> affected prerequisites
```

Proposal generation must not create implementation diffs in Milestone 1.

---

# 29. Affected File Rules

Affected files may be listed only when supported by evidence.

Allowed sources for affected files:

```text
candidate_action.dependencies
candidate_action.source_signal_ids
architecture_report affected paths
repository_scan paths
governance_decision target_path
risk_item source refs
```

If affected files are unknown:

```text
affected_files = []
status = NEEDS_EVIDENCE
```

The generator must not invent target files.

---

# 30. No-Diff / No-Apply Rule

Milestone 1 proposals must not contain executable diffs.

Forbidden fields or content:

```text
unified diff
git patch
apply command
shell command
automatic edit instruction
full replacement source file
commit message as execution instruction
```

Allowed content:

```text
description of intended change
affected file path
rationale
evidence
validation plan
rollback concept
```

---

# 31. Validation Plan Rules

Validation plans are recommendations only.

Allowed recommendations:

```text
run unit tests
run schema validation
run integration tests
run governance checks
run risk reassessment
manual review
```

Forbidden:

```text
execute validation now
run command now
assume validation passed
mark proposal validated
```

---

# 32. Rollback Plan Rules

Rollback plans are conceptual only.

Allowed rollback concepts:

```text
revert proposed change
remove proposed added file
restore previous version
manual review required
no change required
```

Forbidden:

```text
execute rollback
write rollback script
modify repository
delete files
run git reset
```

---

# 32.1 Proposal-to-Implementation Handoff Rule

The Patch Proposal Generator may hand off a proposal to later implementation tooling only as a non-mutating artifact.

Allowed handoff payload:

```text
proposal_id
title
category
affected_files
changes as descriptions
evidence_ids
validation_plan
rollback_plan
governance_context
risk_context
non_mutation_note
```

Forbidden handoff payload:

```text
executable diff
git patch
shell command
apply instruction
source replacement block
auto-commit instruction
automatic branch creation request
runtime execution request
```

Later implementation tooling owns any actual source modification.

The Patch Proposal Generator owns only proposal structure, evidence, validation recommendations, and rollback concepts.

---

# 32.2 Proposal Status and Evidence Matrix

| Proposal Status | Required Evidence | Meaning |
|---|---|---|
| PROPOSED | Candidate action evidence and affected-file evidence if known | Proposal is reviewable but not executable |
| NEEDS_GOVERNANCE_REVIEW | Governance context or protected-path concern | Governance Engine should review before implementation |
| NEEDS_RISK_REVIEW | Risk item or missing risk context | Risk Engine should review before implementation |
| NEEDS_EVIDENCE | Missing affected files or weak source evidence | More evidence is required before proposal can mature |
| DEFERRED | Planning or dependency reason | Proposal should not be pursued now |
| BLOCKED | Required input or schema boundary failure | Proposal cannot be safely generated |

No status authorizes implementation.

---

# 33. Determinism Contract

The same inputs must produce:

```text
same proposal structure
same proposal status
same affected file ordering
same change ordering
same evidence ordering
same validation plan ordering
same rollback plan ordering
same structured output except timestamp and proposal_id
```

No randomness is allowed.

No network calls are allowed.

---

# 34. Status Semantics

Allowed statuses:

```text
PROPOSED
NEEDS_GOVERNANCE_REVIEW
NEEDS_RISK_REVIEW
NEEDS_EVIDENCE
DEFERRED
BLOCKED
FAIL
PARTIAL
```

Meaning:

```text
PROPOSED                 = proposal generated and schema-valid
NEEDS_GOVERNANCE_REVIEW  = proposal requires governance review before implementation
NEEDS_RISK_REVIEW        = proposal requires risk review before implementation
NEEDS_EVIDENCE           = insufficient evidence to identify affected files or changes
DEFERRED                 = proposal should not be pursued now
BLOCKED                  = proposal cannot be safely generated
FAIL                     = proposal generation attempted but valid output could not be produced
PARTIAL                  = optional context missing but proposal is still schema-valid
```

---

# 35. Failure Classes

Allowed failure classes:

```text
MISSING_REQUIRED_INPUT
INVALID_INPUT
INVALID_SCHEMA
INVALID_SCHEMA_CONTRACT
MISSING_EVIDENCE
PROPOSAL_BUILD_FAILED
AFFECTED_FILES_UNKNOWN
VALIDATION_PLAN_BUILD_FAILED
ROLLBACK_PLAN_BUILD_FAILED
ARTIFACT_WRITE_FAILED
AUDIT_WRITE_FAILED
UNKNOWN_PATCH_PROPOSAL_ERROR
```

All failures must be represented in output or audit trail when possible.

---

# 36. Preconditions

Before proposal generation:

- required input artifacts must be available
- required input fields must be present
- schema contract must be available
- `.agentx-init/` write boundary must be available
- audit log writer must be available or failure must be reported

If required preconditions fail, the generator must not emit `PROPOSED`.

---

# 37. Postconditions

After successful proposal generation:

- PatchProposal exists
- patch_proposal_latest.json exists
- patch_proposal_history.jsonl is appended
- audit_events.jsonl is appended
- all changes have valid change types
- all non-UNKNOWN changes have evidence
- all structured output validates against schema
- no source files are changed
- no actions are executed
- no diffs are generated or applied

---

# 38. Invariants

```yaml
invariants:
  - id: "PPG-INV-001"
    statement: "Patch Proposal Generator never modifies source files."
  - id: "PPG-INV-002"
    statement: "Patch Proposal Generator never applies patches."
  - id: "PPG-INV-003"
    statement: "Patch Proposal Generator never executes validation."
  - id: "PPG-INV-004"
    statement: "Every non-UNKNOWN change has evidence."
  - id: "PPG-INV-005"
    statement: "Validation plans are recommendations only."
  - id: "PPG-INV-006"
    statement: "Rollback plans are conceptual only."
  - id: "PPG-INV-007"
    statement: "No executable diffs are emitted in Milestone 1."
```

---

# 39. Security Contract

Security requirements:

- no network access
- no shell command execution
- no dependency installation
- no Git commands
- no unsafe deserialization
- no source mutation
- no environment variable logging
- no secret logging
- no direct source traversal in Milestone 1

---

# 40. Side Effects

Side-effect classification:

```yaml
side_effect_class: "persistent_state"
allowed_writes:
  - ".agentx-init/snapshots/patch_proposal_latest.json"
  - ".agentx-init/memory/patch_proposal_history.jsonl"
  - ".agentx-init/memory/audit_events.jsonl"
forbidden_writes:
  - "L0/"
  - "L1/"
  - "L2/"
  - "source files outside .agentx-init/"
```

The Patch Proposal Generator must not mutate governed source files.

---

# 41. JSONL Append Rules

For `patch_proposal_history.jsonl`:

- append exactly one JSON object per proposal generation attempt
- never rewrite previous lines
- malformed previous lines must not be silently deleted
- each line must include `proposal_id`, `timestamp`, `status`, and generated artifacts

For `audit_events.jsonl`:

- append exactly one JSON object per proposal generation attempt when possible
- audit event must exist for PROPOSED, PARTIAL, FAIL, and BLOCKED when possible
- previous audit events must never be rewritten or reordered

---

# 42. SIB Bindings

Consumes:

```text
Evolution Planner
Risk Engine
Governance Engine
Architecture Analyzer
Repository Scanner
Validation Runner
```

Produces:

```text
PatchProposal
PatchChange
PatchEvidence
PatchValidationPlan
PatchRollbackPlan
PatchAuditRecord
```

Consumed by:

```text
Human Review
Validation Runner
Implementation Tooling
Status/Report Commands
```

---

# 43. SIB Registry Entry

```yaml
art_id: "AGENTX::PATCH_PROPOSAL_GENERATOR"
title: "Patch Proposal Generator"
type: "production-impl"
language: "python"
layer: 1
file_path: "agentx_initiator/core/patch_proposal_generator.py"
current_version: "v4.0.0"
status: "active"
canonicalization_tier: "T1"
spec_bindings:
  - doc: "AGENTX::FIC-AGENTX-INITIATOR-PATCH-PROPOSAL-GENERATOR-001"
    binding_type: "GOVERNS"
    binding_strength: "HARD"
```

---

# 44. SIB Dependency Graph

```yaml
nodes:
  - "AGENTX::PATCH_PROPOSAL_GENERATOR"
  - "AGENTX::PATCH_PROPOSAL_MODEL"
  - "AGENTX::PATCH_PROPOSAL_RULES"
  - "AGENTX::EVOLUTION_PLAN"
  - "AGENTX::RISK_ASSESSMENT"
  - "AGENTX::GOVERNANCE_DECISION"
  - "AGENTX::ARCHITECTURE_REPORT"
  - "AGENTX::AUDIT_LOG"

edges:
  - src: "AGENTX::PATCH_PROPOSAL_GENERATOR"
    type: "IMPORTS"
    dst: "AGENTX::PATCH_PROPOSAL_RULES"
  - src: "AGENTX::PATCH_PROPOSAL_GENERATOR"
    type: "IMPORTS"
    dst: "AGENTX::PATCH_PROPOSAL_MODEL"
  - src: "AGENTX::PATCH_PROPOSAL_GENERATOR"
    type: "USES"
    dst: "AGENTX::EVOLUTION_PLAN"
  - src: "AGENTX::PATCH_PROPOSAL_GENERATOR"
    type: "USES"
    dst: "AGENTX::RISK_ASSESSMENT"
  - src: "AGENTX::PATCH_PROPOSAL_GENERATOR"
    type: "USES"
    dst: "AGENTX::GOVERNANCE_DECISION"
  - src: "AGENTX::PATCH_PROPOSAL_GENERATOR"
    type: "USES"
    dst: "AGENTX::ARCHITECTURE_REPORT"
  - src: "AGENTX::PATCH_PROPOSAL_GENERATOR"
    type: "IMPORTS"
    dst: "AGENTX::AUDIT_LOG"
```

---

# 45. Test Contract

Required unit tests:

```text
test_missing_required_input_blocks
test_invalid_input_blocks
test_proposal_generated_from_candidate_action
test_affected_files_require_evidence
test_unknown_affected_files_needs_evidence
test_patch_change_requires_evidence
test_validation_plan_is_non_executing
test_rollback_plan_is_conceptual
test_no_diff_emitted
test_no_apply_instruction_emitted
test_patch_proposal_schema_validates
test_patch_proposal_history_appends
test_audit_event_appends
```

Required negative tests:

```text
test_unknown_category_rejected
test_missing_evidence_rejected_for_non_unknown_change
test_network_imports_forbidden
test_shell_execution_forbidden
test_git_imports_forbidden
test_source_mutation_forbidden
test_executable_diff_rejected
```

Required integration tests:

```text
test_patch_proposal_from_evolution_plan
test_patch_proposal_with_risk_context
test_patch_proposal_with_governance_context
test_patch_proposal_artifact_generation
```

---

# 46. Test Oracle Strength

Minimum oracle levels:

```yaml
non_mutation_boundary: "O4 invariant"
no_diff_output: "O4 invariant"
evidence_required_for_changes: "O4 invariant"
schema_validation: "O3 negative"
validation_plan_non_execution: "O4 invariant"
rollback_plan_conceptual_only: "O3 negative"
source_non_mutation: "O4 invariant"
```

Smoke tests alone are not sufficient.

---

# 47. Acceptance Criteria

Patch Proposal Generator is accepted only if:

- required inputs are validated
- missing required inputs block proposal generation
- patch proposal uses only registered categories and statuses
- affected files are evidence-backed or marked unknown
- every non-UNKNOWN change has evidence
- no executable diff is emitted
- no apply instruction is emitted
- validation plan is non-executing
- rollback plan is conceptual only
- patch_proposal_latest.json is written only when schema-valid
- patch_proposal_history.jsonl is appended
- audit_events.jsonl is appended
- no source files are changed
- no commands are executed
- no governance decisions are generated
- all required tests pass
- no forbidden imports or shell execution are present

---

# 48. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] target files are listed
[ ] public surface is defined
[ ] patch proposal schema is defined
[ ] patch change schema is defined
[ ] patch evidence schema is defined
[ ] validation plan schema is defined
[ ] rollback plan schema is defined
[ ] proposal categories are defined
[ ] proposal statuses are defined
[ ] no-diff rule is defined
[ ] no-apply rule is defined
[ ] validation plan boundary is defined
[ ] rollback plan boundary is defined
[ ] write boundaries are defined
[ ] test obligations are defined
[ ] acceptance criteria are binary
[ ] SIB bindings are listed
[ ] dependency graph is listed
```

---

# 49. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] public surface matches FIC
[ ] no extra public symbols are introduced without justification
[ ] no forbidden dependencies are used
[ ] no writes outside .agentx-init/
[ ] no executable diffs are emitted
[ ] no actions are executed
[ ] no source files are changed
[ ] schema validation passes
[ ] unit tests pass
[ ] integration tests pass
[ ] audit event is produced
[ ] proposal output is deterministic for same inputs
[ ] completion record exists
```

---

# 50. Minimal Implementation Package

Milestone 1 implementation package must include:

```text
TASK_CONTRACT.md
PATCH_PROPOSAL_GENERATOR_FIC_EQC_SCHEMA_v4.md
patch_proposal.schema.json
patch_change.schema.json
patch_evidence.schema.json
patch_validation_plan.schema.json
patch_rollback_plan.schema.json
patch_audit.schema.json
completion_record.schema.json
implementation_handoff.yaml
completion_record.yaml
```

No coding agent should implement the Patch Proposal Generator from this document alone without the implementation package.

---

# 51. Implementation Handoff Envelope

```yaml
implementation_handoff:
  fic_id: "FIC-AGENTX-INITIATOR-PATCH-PROPOSAL-GENERATOR-001"
  eqc_id: "EQC-AGENTX-INITIATOR-PATCH-PROPOSAL-GENERATOR-001"
  target_component: "Patch Proposal Generator"
  permitted_files:
    - "agentx_initiator/core/patch_proposal_generator.py"
    - "agentx_initiator/core/patch_proposal_model.py"
    - "agentx_initiator/core/patch_proposal_rules.py"
    - "agentx_initiator/schemas/patch_proposal.schema.json"
    - "agentx_initiator/schemas/patch_change.schema.json"
    - "agentx_initiator/schemas/patch_evidence.schema.json"
    - "agentx_initiator/schemas/patch_validation_plan.schema.json"
    - "agentx_initiator/schemas/patch_rollback_plan.schema.json"
    - "agentx_initiator/schemas/patch_audit.schema.json"
    - "agentx_initiator/tests/test_patch_proposal_generator.py"
    - "agentx_initiator/tests/test_patch_proposal_rules.py"
    - "agentx_initiator/tests/test_patch_proposal_schema.py"
  forbidden_changes:
    - "L0/"
    - "L1/"
    - "L2/"
    - "source files unrelated to patch proposal generator"
  allowed_statuses:
    - "IMPLEMENTED_UNVALIDATED"
    - "VALIDATED"
    - "NO_CHANGE"
    - "BLOCKED"
  stop_conditions:
    - "Patch proposal schema conflicts with existing schema standard"
    - "write boundary cannot be enforced"
    - "Patch Proposal Generator needs to apply patches"
    - "Patch Proposal Generator needs to execute validation"
    - "Patch Proposal Generator needs to mutate source files"
```

---

# 52. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  fic_id: "FIC-AGENTX-INITIATOR-PATCH-PROPOSAL-GENERATOR-001"
  eqc_id: "EQC-AGENTX-INITIATOR-PATCH-PROPOSAL-GENERATOR-001"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|NO_CHANGE|BLOCKED"
  files_created_or_changed: []
  tests_created_or_changed: []
  schemas_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  deviations_from_fic_eqc_schema: []
  unresolved_risks: []
```

The implementation must not be considered complete without evidence.

---

# 53. Residual Risks

Known residual risks:

```yaml
residual_risks:
  - id: "PPG-RISK-001"
    description: "Milestone 1 proposals are descriptive and do not include executable diffs."
    severity: "medium"
    mitigation: "Patch application belongs to later approved implementation tooling."
  - id: "PPG-RISK-002"
    description: "Affected-file identification depends on upstream planning and architecture evidence."
    severity: "medium"
    mitigation: "Use NEEDS_EVIDENCE instead of inventing targets."
  - id: "PPG-RISK-003"
    description: "Validation plans are not executed by this component."
    severity: "low"
    mitigation: "Validation Runner owns execution later."
```

---

# 54. Definition of Done

Patch Proposal Generator Milestone 1 is done when it can:

- load required structured inputs
- block on missing required inputs
- generate a non-mutating patch proposal
- identify affected files only when evidence-backed
- generate PatchChange records as descriptions only
- attach proposal evidence
- create a non-executing validation plan
- create a conceptual rollback plan
- write patch_proposal_latest.json
- append patch_proposal_history.jsonl
- append audit_events.jsonl
- validate all structured outputs against schema
- pass required tests
- leave source files unchanged
- avoid executable diffs
- avoid patch application
- avoid command execution

---

# 55. Freeze Rule

This document is now the frozen controlling Patch Proposal Generator FIC+EQC+Schema Contract document for Milestone 1.

Do not keep expanding this document unless a true implementation-blocking gap is discovered.

Next artifacts should be:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
patch_proposal.schema.json
patch_change.schema.json
patch_evidence.schema.json
patch_validation_plan.schema.json
patch_rollback_plan.schema.json
patch_audit.schema.json
completion_record.schema.json
```

---

# 56. Final Success Definition

Patch Proposal Generator v1 implementation is successful when it can consume planning artifacts and generate deterministic, schema-valid, evidence-backed, non-mutating patch proposals with validation and rollback plans, without generating executable diffs, applying patches, executing actions, or modifying repository contents.

---

# 57. Final Rating

This FIC+EQC+Schema Contract document is rated **10/10** for the initial Patch Proposal Generator component.

It is ready to be used as the controlling document for the Patch Proposal Generator Milestone 1 implementation package.
