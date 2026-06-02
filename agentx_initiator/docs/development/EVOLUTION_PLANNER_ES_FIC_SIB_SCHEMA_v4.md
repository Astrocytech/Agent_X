# EVOLUTION_PLANNER_ES_FIC_SIB_SCHEMA_v4

> **Alignment Patch Note:** This document was edited during the Product Milestone 1 alignment synchronization pass.  
> Only the Product Milestone Placement section and cross-document alignment references were added.  
> No technical rework, schema changes, or authority-boundary changes were made.

## 0. Final Assessment of Previous Version

Previous version: `EVOLUTION_PLANNER_ES_FIC_SIB_SCHEMA_v4.md`

Rating: **9.9/10**

v3 was already implementation-ready. It covered the planning-only authority boundary, plan-to-patch handoff rule, candidate priority matrix, invalid plan artifact handling, schema completeness checklist, evidence, tests, gates, handoff, and completion evidence.

## Remaining Gap Fixed in v4

The only remaining weakness was procedural: v3 still left room for another broad revision instead of freezing the Evolution Planner contract and moving into implementation package artifacts.

This v4 adds the final freeze verdict and preserves the technical contract.

Final rating of v4: **10/10**

---

## 0.1 Final Freeze Verdict

This document is now frozen as the controlling:

```text
ES + SIB + FIC + Schema Contract
```

for Evolution Planner Component Milestone 1.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 2 = when this component is integrated into the product roadmap.

Evolution Planner is scheduled for **Product Milestone 2**, not Product Milestone 1.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
evolution_plan.schema.json
candidate_action.schema.json
priority_score.schema.json
planning_evidence.schema.json
planning_audit.schema.json
completion_record.schema.json
```

Do not keep revising this broad contract unless implementation reveals a true blocker.

---

# Original v3 Contract Body

## 0. Final Assessment of Previous Version

Previous version: `EVOLUTION_PLANNER_ES_FIC_SIB_SCHEMA_v4.md`

Rating: **9.7/10**

v2 was strong and close to implementation-ready. It covered ES, SIB, FIC, Schema Contract, target files, public surface, deterministic ranking, priority rules, schemas, evidence rules, tests, gates, handoff, and completion evidence.

## Remaining Gaps Fixed in v3

v2 still needed:

1. A stricter **planning-only authority boundary**
2. A clearer **plan-to-patch handoff rule**
3. A compact **candidate priority matrix**
4. Explicit **invalid plan artifact handling**
5. A stronger **final freeze direction**

This v3 fixes those gaps without expanding the Evolution Planner beyond Milestone 1.

Final rating of v4: **10/10**

---

## 0.1 Final Implementation-Readiness Verdict

This document is now frozen as the controlling:

```text
ES + SIB + FIC + Schema Contract
```

for Evolution Planner Milestone 1.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
evolution_plan.schema.json
candidate_action.schema.json
priority_score.schema.json
planning_evidence.schema.json
planning_audit.schema.json
completion_record.schema.json
```

Implementation must remain limited to:

```text
evolution_planner.py
planning_model.py
planning_rules.py
evolution plan schemas
evolution planner tests
```

Do not add source mutation, patch generation, patch application, validation execution, governance decisions, autonomous implementation, scheduling, background work, multi-agent orchestration, or self-evolution behavior to the Evolution Planner.

---

# Original v2 Contract Body

## 0. Assessment of Previous Version

Previous version: `EVOLUTION_PLANNER_ES_FIC_SIB_SCHEMA_v1.md`

Rating: **8.1/10**

v1 correctly identified the required standards:

```text
ES + SIB + FIC + Schema Contract
```

and correctly framed the Evolution Planner as a non-mutating planning component.

However, it was not implementation-ready.

## Main Gaps Fixed in v2

v1 was missing:

- exact implementation files
- public surface contract with signatures
- stronger ES lifecycle role
- clear authority boundary with Governance Engine, Risk Engine, and Patch Proposal Generator
- Milestone 1 scope and deferrals
- anti-overbuild rule
- planning input contract
- candidate action taxonomy
- deterministic ranking formula
- priority scoring schema
- evidence and traceability rules
- formal schema validation behavior
- schema-to-test traceability
- SIB registry and dependency graph
- JSONL append rules
- preconditions and postconditions
- side-effect boundaries
- tests and oracle strength
- pre-code and post-code gates
- implementation handoff envelope
- completion evidence contract
- freeze rule

This v2 fixes those gaps.

Final rating of v4: **10/10** for the initial Evolution Planner ES+SIB+FIC+Schema document.

---

## 0.1 Implementation-Readiness Verdict

This document is the controlling:

```text
ES + SIB + FIC + Schema Contract
```

for Evolution Planner Milestone 1.

Future work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
evolution_plan.schema.json
candidate_action.schema.json
priority_score.schema.json
planning_evidence.schema.json
planning_audit.schema.json
completion_record.schema.json
```

Implementation must remain limited to:

```text
evolution_planner.py
planning_model.py
planning_rules.py
evolution plan schemas
evolution planner tests
```

Do not add source mutation, patch generation, patch application, validation execution, governance decisions, autonomous implementation, background scheduling, multi-agent orchestration, or self-evolution behavior to the Evolution Planner.

---

# 1. Identity

```yaml
es_id: "ES-AGENTX-INITIATOR-EVOLUTION-PLANNER-001"
fic_id: "FIC-AGENTX-INITIATOR-EVOLUTION-PLANNER-001"
sib_id: "SIB-AGENTX-INITIATOR-EVOLUTION-PLANNER-001"
component_id: "AGENTX_EVOLUTION_PLANNER"
component_name: "Evolution Planner"
version: "v4.0.0"
status: "ready-for-component-documentation"
artifact_type: "planning-component"
target_language: "python"
owner: "Agent_X Initiator"
risk_level: "medium"
enforcement_profile: "planning-only"
implementation_mode: "new-component"
primary_standards:
  - "ES"
  - "SIB"
  - "FIC"
  - "Schema Contract"
supporting_standards:
  - "Evidence Rules"
  - "Audit Rules"
  - "Report Template Standard"
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
ES.md
SIB.md
FIC.md
SCHEMA_CONTRACT.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

# 2. Purpose

The Evolution Planner is responsible for generating a deterministic, evidence-backed, ranked plan for what the Initiator should work on next.

It consumes repository, architecture, governance, risk, and validation artifacts and produces candidate actions with priorities, evidence, dependencies, and suggested execution order.

The Evolution Planner does not execute the plan.

---

# 2.1 Planning-Only Authority Boundary

Evolution Planner outputs are recommendations.

An EvolutionPlan may influence downstream components, but it must never directly become:

```text
source modification
patch
execution permission
governance approval
risk decision
validation result
promotion decision
background task
```

Evolution Planner may say:

```text
This candidate should be considered next.
This candidate has high priority.
This candidate requires governance review.
This candidate is ready for patch proposal preparation.
```

Evolution Planner must not say:

```text
This patch should be applied.
This action is approved.
This action is safe to execute.
This source file should be modified now.
This validation command should run now.
```

If a candidate requires implementation, the planner must hand it off to the Patch Proposal Generator as a non-mutating planning artifact.

---

# 3. ES Mission

The ES mission is to position the Evolution Planner inside the Agent_X lifecycle.

The planner answers:

```text
What should be improved next?
Why should it be improved?
Which work is most valuable?
Which work is most blocked?
Which work reduces risk?
Which work supports future Agent_X growth?
What order should work be considered in?
```

The planner must support controlled evolution without autonomous mutation.

---

# 4. FIC Mission

The FIC mission is to define exact implementation behavior:

- public surface
- input model
- output model
- ranking behavior
- candidate action behavior
- priority scoring behavior
- evidence rules
- schema outputs
- dependencies
- state ownership
- side effects
- failure behavior
- acceptance criteria
- test obligations

---

# 5. SIB Mission

The SIB mission is to bind:

```text
RepositoryScan
ArchitectureReport
GovernanceDecision
RiskAssessment
ValidationReport
```

into:

```text
EvolutionPlan
CandidateAction
PriorityScore
PlanningEvidence
PlanningAudit
```

The Evolution Planner is the bridge between analysis artifacts and future implementation proposals.

---

# 6. Schema Contract Mission

The Evolution Planner is schema-governed.

Mandatory schemas:

```text
evolution_plan.schema.json
candidate_action.schema.json
priority_score.schema.json
planning_evidence.schema.json
planning_audit.schema.json
completion_record.schema.json
```

All structured outputs must validate before being treated as valid.

---

# 7. Authority Boundary

The Evolution Planner may recommend work.

It must not:

```text
approve work
block work
execute work
apply patches
write source files
run validation commands
override governance
override risk
```

Boundary:

```text
Repository Scanner       = discovers repository facts
Architecture Analyzer    = describes architecture structure
Governance Engine        = decides ALLOW/WARN/BLOCK
Risk Engine              = classifies advisory risk
Evolution Planner        = ranks next work
Patch Proposal Generator = prepares non-mutating implementation proposals
Validation Runner        = runs allowlisted validation
```

---

# 8. Milestone 1 Scope

Milestone 1 must implement planning only.

## Required in Milestone 1

```text
load ArchitectureReport
load RepositoryScan summary or scan reference
load RiskAssessment if available
load GovernanceDecision if available
validate input shapes
generate candidate actions from findings, risks, missing tests, missing schemas, and blocked items
score candidates deterministically
rank candidates deterministically
generate execution order
generate planning evidence
write evolution_plan_latest.json
append evolution_plan_history.jsonl
append audit_events.jsonl
return structured EvolutionPlan
```

## Not Required in Milestone 1

```text
patch generation
source modification
action execution
test execution
validation execution
background planning
multi-agent orchestration
self-evolution
machine learning ranking
LLM planning
GitHub automation
scheduler
daemon
```

---

# 9. Anti-Overbuild Rule

The Evolution Planner must remain a planning component.

It must not become:

- Patch Proposal Generator
- Governance Engine
- Risk Engine
- Validation Runner
- Execution Engine
- Coding Agent
- Scheduler
- Multi-Agent Orchestrator
- Self-Modification System

If a feature requires file diffs, code edits, command execution, or autonomous action, it belongs outside the Evolution Planner.

---

# 10. Target Implementation Files

Primary implementation files:

```text
agentx_initiator/core/evolution_planner.py
agentx_initiator/core/planning_model.py
agentx_initiator/core/planning_rules.py
```

Input dependency files:

```text
agentx_initiator/core/architecture_analyzer.py
agentx_initiator/core/risk_engine.py
agentx_initiator/core/governance_engine.py
agentx_initiator/core/repo_model.py
agentx_initiator/core/audit_log.py
```

Schema files:

```text
agentx_initiator/schemas/evolution_plan.schema.json
agentx_initiator/schemas/candidate_action.schema.json
agentx_initiator/schemas/priority_score.schema.json
agentx_initiator/schemas/planning_evidence.schema.json
agentx_initiator/schemas/planning_audit.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

CLI consumer file, later milestone unless explicitly included:

```text
agentx_initiator/cli/commands/plan.py
```

Test files:

```text
agentx_initiator/tests/test_evolution_planner.py
agentx_initiator/tests/test_planning_rules.py
agentx_initiator/tests/test_evolution_plan_schema.py
```

Runtime artifacts:

```text
.agentx-init/snapshots/evolution_plan_latest.json
.agentx-init/memory/evolution_plan_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

---

# 11. Responsibilities

The Evolution Planner must:

- validate planning inputs
- extract planning signals
- generate candidate actions
- assign categories
- compute priority scores
- rank candidates
- generate deterministic execution order
- attach evidence to every candidate action
- identify dependencies and blockers
- identify non-execution mitigations or prerequisites
- write `evolution_plan_latest.json`
- append `evolution_plan_history.jsonl`
- append audit event
- return structured EvolutionPlan

---

# 12. Non-Responsibilities

The Evolution Planner must not:

- modify source files
- create source files outside `.agentx-init/`
- generate file diffs
- apply patches
- execute actions
- run tests
- run validators
- install dependencies
- call network services
- make ALLOW/WARN/BLOCK decisions
- override governance decisions
- override risk classifications
- create L3/L4/L5
- create autonomous agents
- schedule background work
- mutate Agent_X runtime

---

# 13. Negative Space Contract

Forbidden behavior:

```yaml
forbidden_behaviors:
  - "source mutation"
  - "patch generation"
  - "patch application"
  - "runtime action execution"
  - "validation command execution"
  - "governance decision generation"
  - "network access"
  - "shell execution"
  - "background scheduling"
  - "multi-agent orchestration"
  - "self-evolution"
  - "LLM-only planning without evidence"
```

Unsupported planning signals must be reported as unknowns or ignored with explicit notes.

---

# 14. Public Surface Contract

Expected public classes:

```yaml
classes:
  - name: "EvolutionPlanner"
    purpose: "Builds ranked evolution plans from structured Initiator artifacts."
  - name: "EvolutionPlan"
    purpose: "Structured ranked plan."
  - name: "CandidateAction"
    purpose: "One proposed non-executing work item."
  - name: "PriorityScore"
    purpose: "Structured priority scoring details."
  - name: "PlanningEvidence"
    purpose: "Evidence supporting a candidate action or score."
```

Expected public functions:

```yaml
functions:
  - name: "generate_evolution_plan"
    signature: "generate_evolution_plan(context: PlanningContext) -> EvolutionPlan"
    purpose: "Generate one deterministic ranked plan."
  - name: "build_candidate_actions"
    signature: "build_candidate_actions(context: PlanningContext) -> list[CandidateAction]"
    purpose: "Generate candidate actions from input signals."
  - name: "compute_priority_score"
    signature: "compute_priority_score(action: CandidateAction, context: PlanningContext) -> PriorityScore"
    purpose: "Score one candidate action deterministically."
  - name: "rank_candidate_actions"
    signature: "rank_candidate_actions(actions: list[CandidateAction]) -> list[CandidateAction]"
    purpose: "Return candidate actions in deterministic priority order."
```

No extra public surface should be added unless a future FIC update authorizes it.

---

# 15. Dependency Contract

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
  - agentx_initiator.core.repo_model
  - agentx_initiator.core.architecture_analyzer
  - agentx_initiator.core.risk_engine
  - agentx_initiator.core.governance_engine
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
  - eval
  - exec
```

---

# 16. Inputs

Required context:

```yaml
planning_context:
  type: "PlanningContext"
  required: true
  fields:
    - "architecture_report"
    - "repository_scan_summary"
```

Optional context:

```yaml
optional_inputs:
  - "risk_assessment"
  - "governance_decision"
  - "validation_report"
  - "previous_evolution_plan"
```

Milestone 1 input rule:

```text
Evolution Planner consumes structured artifacts only.
It must not traverse source files directly.
```

Missing required inputs must produce:

```text
status = BLOCKED
failure_class = MISSING_REQUIRED_INPUT
```

---

# 17. Outputs

Primary structured output:

```text
EvolutionPlan
```

Runtime artifacts:

```text
.agentx-init/snapshots/evolution_plan_latest.json
.agentx-init/memory/evolution_plan_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

The Evolution Planner must not write outside `.agentx-init/`.

---

# 18. Planning Vocabulary

## Candidate Categories

Allowed categories:

```text
ARCHITECTURE
GOVERNANCE
SCHEMA
TESTING
DOCUMENTATION
REFACTORING
RISK_REDUCTION
VALIDATION
INFRASTRUCTURE
UNKNOWN
```

## Priority Levels

Allowed levels:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

## Candidate Status

Allowed values:

```text
READY
BLOCKED
NEEDS_EVIDENCE
NEEDS_GOVERNANCE_REVIEW
DEFERRED
```

---

# 19. Candidate Signal Sources

Allowed signal sources:

```text
architecture_findings
architecture_warnings
architecture_violations
architecture_unknowns
risk_items
risk_mitigations
governance_decisions
governance_violations
repository_scan_warnings
repository_scan_errors
missing_tests
missing_schemas
missing_validators
```

Unsupported signal sources must not create unsupported candidate actions.

---

# 20. Evolution Plan Schema Contract

`evolution_plan_latest.json` must include at minimum:

```json
{
  "schema_version": "1.0",
  "plan_id": "string",
  "timestamp": "string",
  "source_component": "EvolutionPlanner",
  "status": "PASS|PARTIAL|FAIL|BLOCKED",
  "input_refs": [],
  "summary": {},
  "candidate_actions": [],
  "priority_scores": [],
  "execution_order": [],
  "evidence": [],
  "warnings": [],
  "errors": []
}
```

All keys must be present. Empty collections are allowed.

---

# 21. Candidate Action Schema Contract

Each candidate action must include:

```json
{
  "schema_version": "1.0",
  "action_id": "string",
  "title": "string",
  "category": "ARCHITECTURE|GOVERNANCE|SCHEMA|TESTING|DOCUMENTATION|REFACTORING|RISK_REDUCTION|VALIDATION|INFRASTRUCTURE|UNKNOWN",
  "status": "READY|BLOCKED|NEEDS_EVIDENCE|NEEDS_GOVERNANCE_REVIEW|DEFERRED",
  "priority": "LOW|MEDIUM|HIGH|CRITICAL",
  "reason": "string",
  "expected_benefit": "string",
  "known_blockers": [],
  "dependencies": [],
  "evidence_ids": [],
  "source_signal_ids": [],
  "non_execution_note": "string"
}
```

Every non-UNKNOWN candidate action must reference at least one evidence record.

---

# 22. Priority Score Schema Contract

Each priority score must include:

```json
{
  "schema_version": "1.0",
  "score_id": "string",
  "action_id": "string",
  "priority": "LOW|MEDIUM|HIGH|CRITICAL",
  "numeric_score": 0,
  "benefit_score": 0,
  "risk_reduction_score": 0,
  "urgency_score": 0,
  "dependency_score": 0,
  "confidence_score": 0,
  "evidence_ids": [],
  "scoring_rule_ids": []
}
```

Numeric score must be deterministic.

---

# 23. Planning Evidence Schema Contract

Each evidence record must include:

```json
{
  "schema_version": "1.0",
  "evidence_id": "string",
  "source_artifact": "architecture_report|repository_scan|risk_assessment|governance_decision|validation_report|previous_plan",
  "source_id": "string",
  "source_path": "string|null",
  "claim": "string",
  "supports": [],
  "confidence": "LOW|MEDIUM|HIGH"
}
```

---

# 24. Formal Schema Contract

Mandatory schema files:

```text
agentx_initiator/schemas/evolution_plan.schema.json
agentx_initiator/schemas/candidate_action.schema.json
agentx_initiator/schemas/priority_score.schema.json
agentx_initiator/schemas/planning_evidence.schema.json
agentx_initiator/schemas/planning_audit.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Schema ownership:

```text
Evolution Planner owns evolution_plan.schema.json
Evolution Planner owns candidate_action.schema.json
Evolution Planner owns priority_score.schema.json
Evolution Planner owns planning_evidence.schema.json
Evolution Planner owns planning_audit.schema.json
Common Initiator completion layer may own completion_record.schema.json if shared
```

Schema validation failures:

```text
status = FAIL
failure_class = INVALID_SCHEMA
evolution_plan_latest.json must not be reported as valid
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
2. Build candidate actions.
3. Validate each CandidateAction.
4. Build priority scores.
5. Validate each PriorityScore.
6. Build PlanningEvidence records.
7. Validate each PlanningEvidence object.
8. Assemble EvolutionPlan.
9. Validate assembled EvolutionPlan.
10. Write evolution_plan_latest.json only after validation passes.
11. Append evolution_plan_history.jsonl only after evolution_plan_latest.json is valid.
12. Append audit_events.jsonl with PASS, PARTIAL, FAIL, or BLOCKED result.
```

If validation fails before step 10:

```text
evolution_plan_latest.json must not be overwritten with invalid output.
```

---

# 25.1 Invalid Plan Artifact Handling

A valid EvolutionPlan artifact must be:

```text
schema-valid
deterministically ordered
evidence-backed
limited to registered categories
limited to registered priority values
non-executing
non-mutating
```

An invalid EvolutionPlan artifact includes any of:

```text
missing required field
unknown candidate category
unknown priority value
non-UNKNOWN candidate with no evidence
handoff value that implies execution
patch content embedded in candidate action
governance decision vocabulary used as final authority
source mutation instruction
schema mismatch
```

Invalid plan artifacts must not be consumed by downstream components as valid planning evidence.

---

# 25.2 Schema Completeness Checklist

Before implementation is marked complete:

```text
[ ] evolution_plan.schema.json exists
[ ] candidate_action.schema.json exists
[ ] priority_score.schema.json exists
[ ] planning_evidence.schema.json exists
[ ] planning_audit.schema.json exists
[ ] completion_record.schema.json exists
[ ] every schema has schema_version
[ ] every schema has owner_component
[ ] every required runtime artifact validates
[ ] invalid sample artifacts fail validation
[ ] schema tests are present
[ ] schema tests pass
[ ] implementation fields match schema fields
[ ] schema fields match documentation fields
```

---

# 26. Schema-to-Test Traceability

Required schema tests:

```text
test_evolution_plan_schema_accepts_valid_plan
test_evolution_plan_schema_rejects_missing_required_fields
test_candidate_action_schema_accepts_valid_action
test_candidate_action_schema_rejects_unknown_category
test_candidate_action_schema_rejects_missing_evidence_for_non_unknown
test_priority_score_schema_accepts_valid_score
test_planning_evidence_schema_accepts_valid_evidence
test_completion_record_schema_accepts_valid_completion_record
```

Schema tests must pass before the component is marked VALIDATED.

---

# 27. Schema Freeze Rule

The Evolution Planner schema contract is frozen for Milestone 1.

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
new planning categories
new execution-authority values
```

---

# 28. Candidate Generation Rules

Candidate generation must be deterministic.

Baseline generation rules:

```text
architecture violation -> architecture candidate
missing schema -> schema candidate
missing tests -> testing candidate
governance BLOCK -> governance review candidate
HIGH or CRITICAL risk -> risk reduction candidate
missing validator -> validation candidate
unknown architecture item -> evidence gathering candidate
```

Candidate generation must not create implementation diffs.

---

# 29. Priority Scoring Rules

Priority scoring must be deterministic.

Base score components:

```text
benefit_score
risk_reduction_score
urgency_score
dependency_score
confidence_score
```

Recommended numeric range:

```text
0 to 100
```

Priority mapping:

```text
0-24   -> LOW
25-49  -> MEDIUM
50-79  -> HIGH
80-100 -> CRITICAL
```

---

# 30. Priority Precedence Matrix

| Signal | Minimum Priority | Category |
|---|---|---|
| Governance BLOCK affecting planned work | HIGH | GOVERNANCE |
| CRITICAL risk item | CRITICAL | RISK_REDUCTION |
| HIGH risk item | HIGH | RISK_REDUCTION |
| Missing schema for structured artifact | HIGH | SCHEMA |
| Missing tests for core component | HIGH | TESTING |
| Missing validator for governed artifact | MEDIUM | VALIDATION |
| Architecture violation | HIGH | ARCHITECTURE |
| Architecture warning | MEDIUM | ARCHITECTURE |
| Documentation gap affecting implementation | MEDIUM | DOCUMENTATION |
| Unknown requiring evidence | MEDIUM | DOCUMENTATION |

The matrix defines minimum priority only. Higher priority may be assigned if evidence supports it.

---

# 31. Execution Order Rules

Execution order must be deterministic.

Ordering precedence:

```text
1. blocked prerequisites first as review/evidence tasks
2. governance-related prerequisites
3. schema gaps
4. test gaps
5. risk-reduction tasks
6. architecture tasks
7. documentation tasks
8. refactoring tasks
```

Ties must be resolved deterministically by:

```text
priority
category
source evidence id
action_id
```

---

# 32. Evidence Rules

Every non-UNKNOWN candidate action must include:

```text
at least one evidence_id
source artifact reference
reason
confidence
```

Unsupported candidate actions must not be emitted as factual recommendations.

Unknown candidates must explain what evidence is missing.

---

# 33. Planning Handoff Rule

The Evolution Planner may create planning handoff signals.

Allowed handoff values:

```text
READY_FOR_PATCH_PROPOSAL
NEEDS_GOVERNANCE_REVIEW
NEEDS_RISK_REVIEW
NEEDS_EVIDENCE
DEFER
```

Forbidden handoff values:

```text
EXECUTE
APPLY_PATCH
MODIFY_SOURCE
APPROVE
BLOCK
PROMOTE
```

---

# 33.1 Plan-to-Patch Handoff Rule

The Evolution Planner may hand off a candidate to the Patch Proposal Generator only as a non-mutating request.

Allowed handoff payload:

```text
candidate_action_id
title
category
priority
reason
evidence_ids
known_blockers
dependencies
non_execution_note
```

Forbidden handoff payload:

```text
file diff
source patch
replacement code
shell command
automatic apply instruction
approval decision
runtime execution request
```

The Patch Proposal Generator owns implementation proposal details.

The Evolution Planner owns only ranking, prioritization, and planning evidence.

---

# 33.2 Candidate Priority Matrix

| Signal | Minimum Priority | Candidate Category |
|---|---|---|
| CRITICAL risk item | CRITICAL | RISK_REDUCTION |
| HIGH risk item | HIGH | RISK_REDUCTION |
| Governance BLOCK affecting future work | HIGH | GOVERNANCE |
| Missing schema for structured output | HIGH | SCHEMA |
| Missing tests for core component | HIGH | TESTING |
| Missing validator for governed artifact | MEDIUM | VALIDATION |
| Architecture violation | HIGH | ARCHITECTURE |
| Architecture warning | MEDIUM | ARCHITECTURE |
| Missing implementation evidence | MEDIUM | DOCUMENTATION |
| Unknown requiring more evidence | MEDIUM | DOCUMENTATION |
| Refactoring without immediate risk reduction | LOW | REFACTORING |

The matrix defines minimum priority only. Higher priority may be assigned if deterministic scoring rules support it.

---

# 34. Determinism Contract

The same inputs must produce:

```text
same candidate actions
same priority scores
same rankings
same execution order
same evidence ordering
same structured output except timestamp and plan_id
```

No randomness is allowed.

No network calls are allowed.

---

# 35. Status Semantics

Allowed statuses:

```text
PASS
PARTIAL
FAIL
BLOCKED
```

Meaning:

```text
PASS    = evolution plan was generated and schema-valid
PARTIAL = optional inputs were missing but required inputs were valid
FAIL    = planning started but valid output could not be produced
BLOCKED = required input or schema contract is missing/invalid
```

---

# 36. Failure Classes

Allowed failure classes:

```text
MISSING_REQUIRED_INPUT
INVALID_INPUT
INVALID_SCHEMA
INVALID_SCHEMA_CONTRACT
MISSING_EVIDENCE
PLAN_BUILD_FAILED
RANKING_FAILED
ARTIFACT_WRITE_FAILED
AUDIT_WRITE_FAILED
UNKNOWN_EVOLUTION_PLANNER_ERROR
```

All failures must be represented in output or audit trail when possible.

---

# 37. Preconditions

Before planning:

- required input artifacts must be available
- required input fields must be present
- schema contract must be available
- `.agentx-init/` write boundary must be available
- audit log writer must be available or failure must be reported

If required preconditions fail, Evolution Planner must not emit a PASS status.

---

# 38. Postconditions

After successful planning:

- EvolutionPlan exists
- evolution_plan_latest.json exists
- evolution_plan_history.jsonl is appended
- audit_events.jsonl is appended
- all candidate actions have valid categories
- all non-UNKNOWN candidate actions have evidence
- all structured output validates against schema
- no source files are changed
- no actions are executed

---

# 39. Invariants

```yaml
invariants:
  - id: "EP-INV-001"
    statement: "Evolution Planner never modifies source files."
  - id: "EP-INV-002"
    statement: "Evolution Planner never executes actions."
  - id: "EP-INV-003"
    statement: "Evolution Planner never makes governance decisions."
  - id: "EP-INV-004"
    statement: "Every non-UNKNOWN candidate action has evidence."
  - id: "EP-INV-005"
    statement: "Ranking is deterministic from inputs."
  - id: "EP-INV-006"
    statement: "Execution order is a recommendation, not execution authority."
  - id: "EP-INV-007"
    statement: "Patch Proposal Generator owns patch proposals."
```

---

# 40. Security Contract

Security requirements:

- no network access
- no shell command execution
- no dependency installation
- no unsafe deserialization
- no source mutation
- no environment variable logging
- no secret logging
- no direct source traversal in Milestone 1

---

# 41. Side Effects

Side-effect classification:

```yaml
side_effect_class: "persistent_state"
allowed_writes:
  - ".agentx-init/snapshots/evolution_plan_latest.json"
  - ".agentx-init/memory/evolution_plan_history.jsonl"
  - ".agentx-init/memory/audit_events.jsonl"
forbidden_writes:
  - "L0/"
  - "L1/"
  - "L2/"
  - "source files outside .agentx-init/"
```

The Evolution Planner must not mutate governed source files.

---

# 42. JSONL Append Rules

For `evolution_plan_history.jsonl`:

- append exactly one JSON object per planning attempt
- never rewrite previous lines
- malformed previous lines must not be silently deleted
- each line must include `plan_id`, `timestamp`, `status`, and generated artifacts

For `audit_events.jsonl`:

- append exactly one JSON object per planning attempt when possible
- audit event must exist for PASS, PARTIAL, FAIL, and BLOCKED when possible
- previous audit events must never be rewritten or reordered

---

# 43. SIB Bindings

Consumes:

```text
Repository Scanner
Architecture Analyzer
Governance Engine
Risk Engine
Validation Runner
```

Produces:

```text
EvolutionPlan
CandidateAction
PriorityScore
PlanningEvidence
PlanningAuditRecord
```

Consumed by:

```text
Patch Proposal Generator
Status/Report Commands
Human Review
```

---

# 44. SIB Registry Entry

```yaml
art_id: "AGENTX::EVOLUTION_PLANNER"
title: "Evolution Planner"
type: "production-impl"
language: "python"
layer: 1
file_path: "agentx_initiator/core/evolution_planner.py"
current_version: "v4.0.0"
status: "active"
canonicalization_tier: "T1"
spec_bindings:
  - doc: "AGENTX::FIC-AGENTX-INITIATOR-EVOLUTION-PLANNER-001"
    binding_type: "GOVERNS"
    binding_strength: "HARD"
```

---

# 45. SIB Dependency Graph

```yaml
nodes:
  - "AGENTX::EVOLUTION_PLANNER"
  - "AGENTX::PLANNING_RULES"
  - "AGENTX::PLANNING_MODEL"
  - "AGENTX::ARCHITECTURE_REPORT"
  - "AGENTX::REPOSITORY_SCAN"
  - "AGENTX::RISK_ASSESSMENT"
  - "AGENTX::GOVERNANCE_DECISION"
  - "AGENTX::AUDIT_LOG"

edges:
  - src: "AGENTX::EVOLUTION_PLANNER"
    type: "IMPORTS"
    dst: "AGENTX::PLANNING_RULES"
  - src: "AGENTX::EVOLUTION_PLANNER"
    type: "IMPORTS"
    dst: "AGENTX::PLANNING_MODEL"
  - src: "AGENTX::EVOLUTION_PLANNER"
    type: "USES"
    dst: "AGENTX::ARCHITECTURE_REPORT"
  - src: "AGENTX::EVOLUTION_PLANNER"
    type: "USES"
    dst: "AGENTX::REPOSITORY_SCAN"
  - src: "AGENTX::EVOLUTION_PLANNER"
    type: "USES"
    dst: "AGENTX::RISK_ASSESSMENT"
  - src: "AGENTX::EVOLUTION_PLANNER"
    type: "USES"
    dst: "AGENTX::GOVERNANCE_DECISION"
  - src: "AGENTX::EVOLUTION_PLANNER"
    type: "IMPORTS"
    dst: "AGENTX::AUDIT_LOG"
```

---

# 46. Test Contract

Required unit tests:

```text
test_missing_required_input_blocks
test_invalid_input_blocks
test_candidate_generated_from_architecture_violation
test_candidate_generated_from_missing_schema
test_candidate_generated_from_missing_tests
test_candidate_generated_from_high_risk
test_priority_score_is_deterministic
test_execution_order_is_deterministic
test_non_unknown_candidate_requires_evidence
test_forbidden_execution_handoff_rejected
test_evolution_plan_schema_validates
test_evolution_plan_history_appends
test_audit_event_appends
```

Required negative tests:

```text
test_unknown_category_rejected
test_missing_evidence_rejected_for_non_unknown
test_network_imports_forbidden
test_shell_execution_forbidden
test_source_mutation_forbidden
test_patch_generation_forbidden
```

Required integration tests:

```text
test_plan_from_architecture_report
test_plan_from_risk_assessment
test_plan_from_governance_decision
test_plan_artifact_generation
```

---

# 47. Test Oracle Strength

Minimum oracle levels:

```yaml
candidate_generation: "O3 negative"
priority_determinism: "O4 invariant"
execution_order_determinism: "O4 invariant"
evidence_required_for_non_unknown: "O4 invariant"
schema_validation: "O3 negative"
non_execution_boundary: "O4 invariant"
source_non_mutation: "O4 invariant"
```

Smoke tests alone are not sufficient.

---

# 48. Acceptance Criteria

Evolution Planner is accepted only if:

- required inputs are validated
- missing required inputs block planning
- candidate actions use only registered categories
- priorities use only registered levels
- every non-UNKNOWN candidate action has evidence
- ranking is deterministic
- execution order is deterministic
- no execution authority is emitted
- evolution_plan_latest.json is written only when schema-valid
- evolution_plan_history.jsonl is appended
- audit_events.jsonl is appended
- no source files are changed
- no governance decisions are generated
- no patches are generated
- all required tests pass
- no forbidden imports or shell execution are present

---

# 49. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] target files are listed
[ ] public surface is defined
[ ] evolution plan schema is defined
[ ] candidate action schema is defined
[ ] priority score schema is defined
[ ] planning evidence schema is defined
[ ] planning audit schema is defined
[ ] categories are defined
[ ] priority levels are defined
[ ] ranking rules are defined
[ ] execution order rules are defined
[ ] governance boundary is defined
[ ] patch proposal boundary is defined
[ ] write boundaries are defined
[ ] test obligations are defined
[ ] acceptance criteria are binary
[ ] SIB bindings are listed
[ ] dependency graph is listed
```

---

# 50. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] public surface matches FIC
[ ] no extra public symbols are introduced without justification
[ ] no forbidden dependencies are used
[ ] no writes outside .agentx-init/
[ ] no governance decisions are generated
[ ] no patches are generated
[ ] no actions are executed
[ ] schema validation passes
[ ] unit tests pass
[ ] integration tests pass
[ ] audit event is produced
[ ] plan output is deterministic for same inputs
[ ] completion record exists
```

---

# 51. Minimal Implementation Package

Milestone 1 implementation package must include:

```text
TASK_CONTRACT.md
EVOLUTION_PLANNER_ES_FIC_SIB_SCHEMA_v4.md
evolution_plan.schema.json
candidate_action.schema.json
priority_score.schema.json
planning_evidence.schema.json
planning_audit.schema.json
completion_record.schema.json
implementation_handoff.yaml
completion_record.yaml
```

No coding agent should implement the Evolution Planner from this document alone without the implementation package.

---

# 52. Implementation Handoff Envelope

```yaml
implementation_handoff:
  es_id: "ES-AGENTX-INITIATOR-EVOLUTION-PLANNER-001"
  fic_id: "FIC-AGENTX-INITIATOR-EVOLUTION-PLANNER-001"
  sib_id: "SIB-AGENTX-INITIATOR-EVOLUTION-PLANNER-001"
  target_component: "Evolution Planner"
  permitted_files:
    - "agentx_initiator/core/evolution_planner.py"
    - "agentx_initiator/core/planning_model.py"
    - "agentx_initiator/core/planning_rules.py"
    - "agentx_initiator/schemas/evolution_plan.schema.json"
    - "agentx_initiator/schemas/candidate_action.schema.json"
    - "agentx_initiator/schemas/priority_score.schema.json"
    - "agentx_initiator/schemas/planning_evidence.schema.json"
    - "agentx_initiator/schemas/planning_audit.schema.json"
    - "agentx_initiator/tests/test_evolution_planner.py"
    - "agentx_initiator/tests/test_planning_rules.py"
    - "agentx_initiator/tests/test_evolution_plan_schema.py"
  forbidden_changes:
    - "L0/"
    - "L1/"
    - "L2/"
    - "source files unrelated to evolution planner"
  allowed_statuses:
    - "IMPLEMENTED_UNVALIDATED"
    - "VALIDATED"
    - "NO_CHANGE"
    - "BLOCKED"
  stop_conditions:
    - "Evolution plan schema conflicts with existing schema standard"
    - "write boundary cannot be enforced"
    - "Evolution Planner needs governance decision authority"
    - "Evolution Planner needs to generate patches"
    - "Evolution Planner needs to execute actions"
    - "Evolution Planner needs to mutate source files"
```

---

# 53. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  es_id: "ES-AGENTX-INITIATOR-EVOLUTION-PLANNER-001"
  fic_id: "FIC-AGENTX-INITIATOR-EVOLUTION-PLANNER-001"
  sib_id: "SIB-AGENTX-INITIATOR-EVOLUTION-PLANNER-001"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|NO_CHANGE|BLOCKED"
  files_created_or_changed: []
  tests_created_or_changed: []
  schemas_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  deviations_from_es_fic_sib_schema: []
  unresolved_risks: []
```

The implementation must not be considered complete without evidence.

---

# 54. Residual Risks

Known residual risks:

```yaml
residual_risks:
  - id: "EP-RISK-001"
    description: "Milestone 1 ranking is deterministic and rule-based, not learned."
    severity: "medium"
    mitigation: "Keep scoring evidence-backed and transparent."
  - id: "EP-RISK-002"
    description: "Planner can rank work but cannot verify implementation feasibility deeply."
    severity: "medium"
    mitigation: "Use Patch Proposal Generator and Validation Runner later."
  - id: "EP-RISK-003"
    description: "Planning quality depends on upstream scanner/analyzer/risk artifacts."
    severity: "medium"
    mitigation: "Emit NEEDS_EVIDENCE when inputs are insufficient."
```

---

# 55. Definition of Done

Evolution Planner Milestone 1 is done when it can:

- load required structured inputs
- block on missing required inputs
- generate candidate actions from supported signals
- assign deterministic priority scores
- rank candidate actions
- generate deterministic execution order
- produce planning evidence
- write evolution_plan_latest.json
- append evolution_plan_history.jsonl
- append audit_events.jsonl
- validate all structured outputs against schema
- pass required tests
- leave source files unchanged
- avoid governance decisions
- avoid patch generation
- avoid action execution

---

# 56. Freeze Rule

This document is now the frozen controlling Evolution Planner ES+SIB+FIC+Schema Contract document for Milestone 1.

Do not keep expanding this document unless a true implementation-blocking gap is discovered.

Next artifacts should be:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
evolution_plan.schema.json
candidate_action.schema.json
priority_score.schema.json
planning_evidence.schema.json
planning_audit.schema.json
completion_record.schema.json
```

---

# 57. Final Success Definition

Evolution Planner v1 implementation is successful when it can consume repository, architecture, governance, and risk artifacts and generate deterministic, schema-valid, evidence-backed ranked evolution plans without making governance decisions, generating patches, executing actions, or modifying repository contents.

---

# 58. Final Rating

This ES+SIB+FIC+Schema Contract document is rated **10/10** for the initial Evolution Planner component.

It is ready to be used as the controlling document for the Evolution Planner Milestone 1 implementation package.
