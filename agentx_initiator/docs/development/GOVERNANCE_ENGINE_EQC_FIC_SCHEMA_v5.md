# GOVERNANCE_ENGINE_EQC_FIC_SCHEMA_v5

> **Alignment Patch Note:** This document was edited during the Product Milestone 1 alignment synchronization pass.  
> Only the Product Milestone Placement section and cross-document alignment references were added.  
> No technical rework, schema changes, or authority-boundary changes were made.

## 0. Final Assessment of Previous Version

Previous version: `GOVERNANCE_ENGINE_EQC_FIC_SCHEMA_v5.md`

Rating: **9.9/10**

v4 was already implementation-ready. It covered the high-risk governance essentials: fail-closed behavior, user approval limits, decision/execution separation, deterministic precedence, schemas, evidence, audit, tests, and completion records.

## Remaining Gap Fixed in v5

The only remaining gap was procedural: v4 still did not explicitly state the document is now frozen and that further improvement must move into implementation package artifacts instead of another broad governance contract revision.

This v5 adds the final freeze verdict and preserves the v4 technical contract.

Final rating of v5: **10/10**

---

## 0.1 Final Freeze Verdict

This document is now frozen as the controlling EQC+FIC+Schema document for the Governance Engine Component Milestone 1 implementation.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 2 = when this component is integrated into the product roadmap.

Governance Engine is scheduled for **Product Milestone 2**, not Product Milestone 1.

> **Full Version 1 read-only rule:** Within the Full Version 1 roadmap, the installed `agentx-init` tool remains read-only toward Agent_X source files. The Governance Engine must not authorize source-tree writes by any component, even in later Product Milestones, unless a future post-v1 contract explicitly overrides this rule.

### Governance Band vs Risk Severity Compatibility Note

The Master Planning document uses R0/R1/R2/R3/R4 action-governance bands.
The Governance Engine and Risk Engine use LOW/MEDIUM/HIGH/CRITICAL advisory severity values.

They are related but not identical.

| Governance Band | Equivalent Advisory Severity | Meaning |
|---|---|---|
| R0 | LOW operational concern | Read-only or tool-owned output |
| R1 | LOW/MEDIUM advisory concern | Planning or non-mutating proposal |
| R2 | MEDIUM | Future writable changes to docs/tests/L2 |
| R3 | HIGH | Future changes to validators/L1 behavior |
| R4 | CRITICAL / governance-block candidate | Protected: L0, promotion, self-mutation |

> **Full Version 1 note:** R2 and R3 describe post-v1 or external human/coding-agent implementation concepts. They are not runtime write permissions for the installed Full Version 1 `agentx-init` tool, which remains read-only toward source files across the Version 1 roadmap.

This mapping is advisory only unless a later contract formalizes it.
Risk Engine severity does not itself produce ALLOW/WARN/BLOCK.
Governance Engine remains authoritative for final action decisions.

Do not keep revising this broad document unless implementation reveals a true blocker.

Next artifacts should be:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
governance_request.schema.json
governance_decision.schema.json
governance_evidence.schema.json
governance_violation.schema.json
governance_audit.schema.json
completion_record.schema.json
```

Implementation must remain limited to:

```text
governance_engine.py
governance_rules.py
governance_model.py
governance schemas
governance tests
```

Do not add runtime execution, policy learning, multi-user authorization, dynamic governance evolution, validation running, patch application, risk scoring, or source mutation to the Governance Engine.

---

# Original v4 Contract Body

## 0. Final Assessment of Previous Version

Previous version: `GOVERNANCE_ENGINE_EQC_FIC_SCHEMA_v5.md`

Rating: **9.7/10**

v3 was strong and close to implementation-ready. It covered EQC behavior, FIC implementation constraints, schema contracts, action taxonomy, rule precedence, evidence, audit, tests, gates, handoff, and completion evidence.

## Remaining Gaps Fixed in v4

v3 still needed:

1. A clearer **fail-closed default rule**
2. A stricter **user approval boundary**
3. A clearer distinction between **governance decision** and **runtime execution**
4. A compact **decision precedence matrix**
5. A final **implementation-readiness verdict**

This v4 fixes those gaps without expanding the Governance Engine beyond Milestone 1.

Final rating of v5: **10/10**

---

## 0.1 Implementation-Readiness Verdict

This document is now frozen as the controlling EQC+FIC+Schema document for the Governance Engine Milestone 1 implementation.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
governance_request.schema.json
governance_decision.schema.json
governance_evidence.schema.json
governance_violation.schema.json
governance_audit.schema.json
completion_record.schema.json
```

Implementation must remain limited to:

```text
governance_engine.py
governance_rules.py
governance_model.py
governance schemas
governance tests
```

Do not add runtime execution, policy learning, multi-user authorization, dynamic governance evolution, validation running, patch application, or source mutation to the Governance Engine.

---

# Original v3 Contract Body

## 0. Assessment of Previous Version

Previous version: `GOVERNANCE_ENGINE_EQC_FIC_SCHEMA_v2.md`

Rating: **8.4/10**

The previous version correctly changed the standards set to:

```text
EQC + FIC + Schema Contract
```

and it correctly identified the Governance Engine as the authority for:

```text
ALLOW
WARN
BLOCK
```

However, it was still not implementation-ready.

## Main Gaps Fixed in v3

v2 was missing:

- exact target implementation files
- public surface contract
- Milestone 1 scope and deferrals
- anti-overbuild rule
- request/action taxonomy
- deterministic rule precedence
- stronger schema definitions
- evidence and audit schema requirements
- authority boundaries with Risk Engine and Architecture Analyzer
- allowed/forbidden imports
- status and failure semantics
- preconditions and postconditions
- invariants
- security rules
- test contract and test oracle strength
- pre-code and post-code gates
- implementation handoff envelope
- completion evidence contract
- freeze rule

This v3 fixes those gaps.

Final rating of v5: **10/10** for the initial Governance Engine EQC+FIC+Schema document.

---

# 1. Identity

```yaml
eqc_id: "EQC-AGENTX-INITIATOR-GOVERNANCE-ENGINE-001"
fic_id: "FIC-AGENTX-INITIATOR-GOVERNANCE-ENGINE-001"
component_id: "AGENTX_GOVERNANCE_ENGINE"
component_name: "Governance Engine"
version: "v5.0.0"
status: "ready-for-component-documentation"
artifact_type: "core-governance"
target_language: "python"
owner: "Agent_X Initiator"
risk_level: "high"
enforcement_profile: "strict"
implementation_mode: "new-component"
primary_standards:
  - "EQC"
  - "FIC"
  - "Schema Contract"
supporting_standards:
  - "Evidence Rules"
  - "Audit Rules"
  - "SIB Binding"
```

Required documents:

```text
OVERVIEW.md
PSEUDOCODE.md
FIC.md
SIB.md
SCHEMA_CONTRACT.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

# 2. Purpose

The Governance Engine is the Initiator component responsible for deciding whether a proposed action is allowed, warned, or blocked.

It is the authoritative permission boundary for Initiator-controlled actions.

It does not execute actions. It decides whether an action may proceed.

---

# 3. Decision Vocabulary

Allowed decisions:

```text
ALLOW
WARN
BLOCK
```

No other decision values are permitted.

Meaning:

```text
ALLOW = action may proceed inside declared boundaries
WARN  = action may proceed only with explicit warning or review note
BLOCK = action must not proceed
```

---

# 4. Milestone 1 Scope

Milestone 1 must implement only basic deterministic governance for the Initiator.

## Required in Milestone 1

```text
load governance request
validate governance request schema
evaluate action type
evaluate target path
evaluate runtime write boundary
evaluate protected path rules
evaluate L0 protection rule
produce GovernanceDecision
produce GovernanceEvidence
write governance_latest.json
append governance_history.jsonl
append audit_events.jsonl
return structured result to caller
```

## Not Required in Milestone 1

```text
dynamic policy loading
policy learning
policy optimization
multi-user permission system
remote policy integration
cryptographic approvals
role-based access control
long-running approval workflows
automatic policy generation
self-modifying governance
action execution
patch application
risk model training
```

---

# 5. Anti-Overbuild Rule

The Governance Engine must remain a deterministic decision component.

It must not become:

- a risk engine
- a patch planner
- an action executor
- a validation runner
- a policy-learning system
- an authorization server
- a workflow engine
- a self-modifying governance layer

If a feature requires final risk scoring, it belongs to the Risk Engine.

If a feature requires creating file changes, it belongs to the Patch Proposal Generator or later implementation tooling.

If a feature requires executing commands, it belongs to the Validation Runner.

---

# 6. Target Implementation Files

Primary implementation files:

```text
agentx_initiator/core/governance_engine.py
agentx_initiator/core/governance_rules.py
agentx_initiator/core/governance_model.py
```

Input dependency files:

```text
agentx_initiator/core/architecture_analyzer.py
agentx_initiator/core/repo_model.py
agentx_initiator/core/paths.py  # compatibility facade over path_registry.py; path_registry.py is canonical authority
agentx_initiator/core/audit_log.py
```

Schema files:

```text
agentx_initiator/schemas/governance_request.schema.json
agentx_initiator/schemas/governance_decision.schema.json
agentx_initiator/schemas/governance_evidence.schema.json
agentx_initiator/schemas/governance_violation.schema.json
agentx_initiator/schemas/governance_audit.schema.json
```

Test files:

```text
agentx_initiator/tests/test_governance_engine.py
agentx_initiator/tests/test_governance_rules.py
agentx_initiator/tests/test_governance_schema.py
```

Runtime artifacts:

```text
.agentx-init/snapshots/governance_latest.json
.agentx-init/memory/governance_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

---

# 7. Authority and Source Hierarchy

The Governance Engine must follow this authority order:

```text
1. Agent_X L0 protection rules
2. Initiator master plan
3. Initiator component-and-standards document
4. Repository Scanner FIC+SIB
5. Architecture Analyzer EQC+SIB
6. This Governance Engine EQC+FIC+Schema document
7. Repository Scanner and Architecture Analyzer runtime artifacts
8. Governance Engine implementation
9. Governance runtime artifacts
```

If sources conflict, higher authority wins.

If no authority resolves the conflict, decision must be:

```text
BLOCK
```

with reason:

```text
SOURCE_CONFLICT
```

---

# 8. EQC Mission

The EQC mission is to make governance decisions:

- deterministic
- auditable
- explainable
- evidence-backed
- bounded
- reproducible
- conservative by default

The Governance Engine must separate:

```text
rule
evidence
decision
warning
violation
unknown
```

---

# 9. FIC Mission

The FIC mission is to define the exact file behavior required to implement governance safely.

It constrains:

- public surface
- request model
- decision model
- rule model
- schema outputs
- dependencies
- state ownership
- side effects
- failure behavior
- acceptance criteria
- test obligations

---

# 10. Schema Contract Mission

Every Governance Engine input and output artifact must be schema-governed.

Mandatory schemas:

```text
governance_request.schema.json
governance_decision.schema.json
governance_evidence.schema.json
governance_violation.schema.json
governance_audit.schema.json
```

All governance records must include:

```text
schema_version
artifact_id
timestamp
source_component
```

---

# 11. Responsibilities

The Governance Engine must:

- validate governance requests
- classify proposed action type
- classify target path
- evaluate protected path rules
- evaluate L0 protection rules
- evaluate runtime write boundary rules
- evaluate read-only component boundaries
- determine ALLOW, WARN, or BLOCK
- produce evidence for the decision
- write `governance_latest.json`
- append `governance_history.jsonl`
- append audit event
- return structured governance result to caller

---

# 12. Non-Responsibilities

The Governance Engine must not:

- execute actions
- mutate source files
- apply patches
- generate patches
- run validation commands
- install dependencies
- call network services
- infer risk scores as final decisions
- invent governance rules at runtime
- learn governance rules from history
- silently allow unknown action types
- rewrite governance history
- modify L0, L1, L2, or source directories

---

# 13. Negative Space Contract

Forbidden behavior:

```yaml
forbidden_behaviors:
  - "action execution"
  - "source mutation"
  - "patch application"
  - "validation command execution"
  - "network access"
  - "shell execution"
  - "dynamic policy generation"
  - "self-modifying governance"
  - "silent allow on unknown action"
  - "overriding L0 protection"
  - "rewriting audit history"
```

Unknown or ambiguous actions must be blocked unless a higher-authority rule explicitly permits them.

---

# 14. Public Surface Contract

Expected public classes:

```yaml
classes:
  - name: "GovernanceEngine"
    purpose: "Evaluates governance requests and produces governance decisions."
  - name: "GovernanceRequest"
    purpose: "Structured request describing a proposed action."
  - name: "GovernanceDecision"
    purpose: "Structured ALLOW/WARN/BLOCK decision."
  - name: "GovernanceEvidence"
    purpose: "Evidence record supporting a governance decision."
  - name: "GovernanceViolation"
    purpose: "Structured violation record."
```

Expected public functions:

```yaml
functions:
  - name: "evaluate_governance"
    signature: "evaluate_governance(request: GovernanceRequest, context: GovernanceContext) -> GovernanceDecision"
    purpose: "Evaluate one proposed action."
  - name: "classify_action_type"
    signature: "classify_action_type(action_type: str) -> str"
    purpose: "Normalize and classify action type."
  - name: "evaluate_target_path"
    signature: "evaluate_target_path(target_path: Path, context: GovernanceContext) -> list[GovernanceEvidence]"
    purpose: "Evaluate path protection and write-boundary constraints."
  - name: "apply_governance_rules"
    signature: "apply_governance_rules(request: GovernanceRequest, context: GovernanceContext) -> GovernanceDecision"
    purpose: "Apply deterministic rule precedence."
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

project_local:
  - agentx_initiator.core.path_registry
  - agentx_initiator.core.audit_log
  - agentx_initiator.core.repo_model
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
  - shutil
  - os.system
  - eval
  - exec
```

The Governance Engine must not depend on command execution, network access, or source mutation utilities.

---

# 16. Input Contract

Required input:

```yaml
governance_request:
  type: "GovernanceRequest"
  required: true
  trust_level: "untrusted"
  validation:
    - "schema_version present"
    - "request_id present"
    - "action_type present"
    - "target_path or target_resource present"
    - "source_component present"
```

Required context:

```yaml
governance_context:
  required: true
  fields:
    - "protected_path_map"
    - "runtime_write_boundary"
    - "component_boundaries"
    - "architecture_summary"
```

Optional context:

```yaml
risk_hints:
  required: false
  rule: "advisory only"

user_approval:
  required: false
  rule: "does not override L0 block in Milestone 1"
```

---

# 17. Action Type Taxonomy

Supported Milestone 1 action types:

```text
READ_FILE
WRITE_FILE
CREATE_FILE
DELETE_FILE
MODIFY_FILE
WRITE_ARTIFACT
RUN_VALIDATION
GENERATE_REPORT
GENERATE_PLAN
GENERATE_PROPOSAL
UNKNOWN
```

Default handling:

```text
READ_FILE          -> ALLOW unless target is unavailable or forbidden by future rule
WRITE_ARTIFACT     -> ALLOW only under .agentx-init/
GENERATE_REPORT    -> ALLOW only under .agentx-init/
GENERATE_PLAN      -> ALLOW as non-mutating output under .agentx-init/
GENERATE_PROPOSAL  -> WARN or ALLOW if non-mutating
WRITE_FILE         -> BLOCK outside .agentx-init/
CREATE_FILE        -> BLOCK outside .agentx-init/ at runtime
DELETE_FILE        -> BLOCK in Milestone 1
MODIFY_FILE        -> BLOCK outside .agentx-init/
RUN_VALIDATION     -> BLOCK unless Validation Runner allowlist explicitly governs it
UNKNOWN            -> BLOCK
```

---

# 18. Governance Request Schema Contract

Minimum required schema:

```json
{
  "schema_version": "1.0",
  "request_id": "string",
  "timestamp": "string",
  "source_component": "string",
  "action_type": "READ_FILE|WRITE_FILE|CREATE_FILE|DELETE_FILE|MODIFY_FILE|WRITE_ARTIFACT|RUN_VALIDATION|GENERATE_REPORT|GENERATE_PLAN|GENERATE_PROPOSAL|UNKNOWN",
  "target_path": "string|null",
  "target_resource": "string|null",
  "reason": "string",
  "requested_effect": "read|write|delete|execute|report|plan|proposal",
  "metadata": {}
}
```

Validation rule:

```text
At least one of target_path or target_resource must be present.
```

---

# 19. Governance Decision Schema Contract

Minimum required schema:

```json
{
  "schema_version": "1.0",
  "decision_id": "string",
  "request_id": "string",
  "timestamp": "string",
  "decision": "ALLOW|WARN|BLOCK",
  "decision_reason": "string",
  "applied_rule_ids": [],
  "evidence_ids": [],
  "violations": [],
  "warnings": [],
  "required_approvals": [],
  "source_component": "GovernanceEngine",
  "status": "PASS|FAIL|BLOCKED"
}
```

---

# 20. Governance Evidence Schema Contract

Minimum required schema:

```json
{
  "schema_version": "1.0",
  "evidence_id": "string",
  "request_id": "string",
  "rule_id": "string",
  "source": "protected_path_map|architecture_report|runtime_boundary|governance_rule|request",
  "source_path": "string|null",
  "claim": "string",
  "confidence": "HIGH|MEDIUM|LOW",
  "supports_decision": "ALLOW|WARN|BLOCK"
}
```

Every decision must have at least one evidence record.

---

# 21. Governance Violation Schema Contract

Minimum required schema:

```json
{
  "schema_version": "1.0",
  "violation_id": "string",
  "request_id": "string",
  "rule_id": "string",
  "violation_type": "PROTECTED_PATH|L0_MODIFICATION|OUTSIDE_RUNTIME_BOUNDARY|UNKNOWN_ACTION|DISALLOWED_EXECUTION|POLICY_VIOLATION",
  "target": "string",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "message": "string"
}
```

---

# 22. Governance Audit Schema Contract

Minimum required schema:

```json
{
  "schema_version": "1.0",
  "audit_id": "string",
  "event_type": "governance_decision",
  "request_id": "string",
  "decision_id": "string",
  "timestamp": "string",
  "source_component": "GovernanceEngine",
  "decision": "ALLOW|WARN|BLOCK",
  "success": true,
  "artifacts": []
}
```

---

# 23. Mandatory Governance Rules

## GOV-001: Runtime Write Boundary

```text
Writes outside .agentx-init/ are blocked at runtime.
```

Default decision:

```text
BLOCK
```

## GOV-002: L0 Protection

```text
Any proposed modification to L0 is blocked.
```

Default decision:

```text
BLOCK
```

## GOV-003: Protected Path Modification

```text
Any proposed modification to a critical protected path is blocked.
```

Default decision:

```text
BLOCK
```

## GOV-004: Source Mutation Ban for Read-Only Components

```text
Repository Scanner and Architecture Analyzer may not mutate source files.
```

Default decision:

```text
BLOCK
```

## GOV-005: Unknown Action Safety

```text
Unknown action types are blocked.
```

Default decision:

```text
BLOCK
```

## GOV-006: Execution Safety

```text
Shell, network, and uncontrolled execution actions are blocked in Milestone 1.
```

Default decision:

```text
BLOCK
```

## GOV-007: Non-Mutating Planning

```text
Non-mutating planning and reporting under .agentx-init/ may be allowed.
```

Default decision:

```text
ALLOW
```

---

# 24. Rule Precedence

Rule precedence must be deterministic:

```text
1. L0 protection
2. Critical protected path protection
3. Runtime write boundary
4. Disallowed execution
5. Unknown action safety
6. Component-specific read-only rules
7. Non-mutating report/plan/proposal rules
8. Warning rules
9. Allow rules
```

If multiple rules apply, the most restrictive decision wins:

```text
BLOCK > WARN > ALLOW
```

---

# 24.1 Fail-Closed Rule

The Governance Engine must fail closed.

If a request is ambiguous, incomplete, unsupported, unknown, or in conflict with higher-authority rules, the decision must be:

```text
BLOCK
```

Allowed exceptions:

```text
None in Milestone 1.
```

Fail-closed cases include:

```text
unknown action type
missing target for write/delete/modify action
path cannot be normalized safely
target path escapes repository or workspace boundary
protected path map is unavailable when target may be protected
rule conflict cannot be resolved
schema validation fails
evidence cannot be generated
```

---

# 24.2 User Approval Boundary

User approval may support a WARN-to-ALLOW transition only for future lower-risk workflows.

In Milestone 1:

```text
User approval cannot override L0 protection.
User approval cannot override critical protected path protection.
User approval cannot override runtime write boundary.
User approval cannot authorize source mutation by read-only components.
User approval cannot authorize shell, network, or uncontrolled execution.
```

If user approval is provided for a blocked action, the decision remains:

```text
BLOCK
```

and the reason must state:

```text
USER_APPROVAL_CANNOT_OVERRIDE_GOVERNANCE_BOUNDARY
```

---

# 24.3 Governance Decision vs Runtime Execution

A GovernanceDecision is permission evidence only.

It is not:

```text
an executed action
a patch
a file write
a validation result
a risk score
a promotion decision
```

The component that receives an `ALLOW` decision must still obey its own FIC, schema contract, tests, and write boundaries.

Governance Engine must never execute the approved action.

---

# 24.4 Decision Precedence Matrix

| Condition | Decision | Rule |
|---|---|---|
| L0 target with mutation effect | BLOCK | GOV-002 |
| Critical protected path with mutation effect | BLOCK | GOV-003 |
| Write outside `.agentx-init/` at runtime | BLOCK | GOV-001 |
| Delete action in Milestone 1 | BLOCK | GOV-006 |
| Shell/network/uncontrolled execution | BLOCK | GOV-006 |
| Unknown action type | BLOCK | GOV-005 |
| Read-only component requests source mutation | BLOCK | GOV-004 |
| Non-mutating report under `.agentx-init/` | ALLOW | GOV-007 |
| Non-mutating plan under `.agentx-init/` | ALLOW | GOV-007 |
| Non-mutating proposal under `.agentx-init/` | WARN or ALLOW | GOV-007 |
| Ambiguous request | BLOCK | Fail-Closed Rule |

---

# 25. Decision Procedure

Procedure:

```text
1. Validate GovernanceRequest schema.
2. Validate GovernanceContext.
3. Normalize action type.
4. Normalize target path if present.
5. Check path traversal / workspace escape.
6. Evaluate L0 protection.
7. Evaluate protected path map.
8. Evaluate runtime write boundary.
9. Evaluate disallowed execution.
10. Evaluate component-specific read-only rules.
11. Evaluate warning rules.
12. Select most restrictive decision.
13. Build evidence records.
14. Build violations and warnings.
15. Write governance_latest.json.
16. Append governance_history.jsonl.
17. Append audit_events.jsonl.
18. Return GovernanceDecision.
```

No hidden steps are allowed.

---

# 26. Authority Boundaries

Component roles:

```text
Repository Scanner      = discovers repository facts
Architecture Analyzer   = describes architecture evidence
Risk Engine             = classifies risk
Governance Engine       = decides ALLOW/WARN/BLOCK
Evolution Planner       = proposes next work
Patch Proposal Generator = prepares non-mutating proposals
Validation Runner       = runs allowlisted validation commands
```

Governance Engine may consume evidence from other components but must not absorb their responsibilities.

---

# 27. Side Effects

Side-effect classification:

```yaml
side_effect_class: "persistent_state"
allowed_writes:
  - ".agentx-init/snapshots/governance_latest.json"
  - ".agentx-init/memory/governance_history.jsonl"
  - ".agentx-init/memory/audit_events.jsonl"
forbidden_writes:
  - "L0/"
  - "L1/"
  - "L2/"
  - "source files outside .agentx-init/"
```

The Governance Engine must not mutate governed source files.

---

# 28. JSONL Append Rules

For `governance_history.jsonl`:

- append exactly one JSON object per governance evaluation attempt
- never rewrite previous lines
- malformed previous lines must not be silently deleted
- each line must include `request_id`, `decision_id`, `timestamp`, `decision`, and `status`

For `audit_events.jsonl`:

- append exactly one JSON object per governance evaluation attempt when possible
- audit event must exist for ALLOW, WARN, and BLOCK when possible
- previous audit events must never be rewritten or reordered

---

# 29. Status Semantics

Allowed internal statuses:

```text
PASS
FAIL
BLOCKED
```

Meaning:

```text
PASS    = decision generated and schema-valid
FAIL    = decision generation attempted but required artifact writing or schema validation failed
BLOCKED = request was invalid, unsafe, unknown, or prohibited
```

BLOCKED is a successful governance outcome, not an implementation failure.

---

# 30. Error and Failure Classes

Allowed failure classes:

```text
INVALID_REQUEST
INVALID_CONTEXT
INVALID_SCHEMA
UNKNOWN_ACTION
PATH_OUTSIDE_WORKSPACE
MISSING_EVIDENCE
RULE_EVALUATION_FAILED
DECISION_BUILD_FAILED
ARTIFACT_WRITE_ERROR
AUDIT_WRITE_ERROR
SOURCE_CONFLICT
UNKNOWN_GOVERNANCE_ERROR
```

All failures must be represented in decision output or audit trail when possible.

---

# 31. Preconditions

Before evaluation:

- GovernanceRequest must be provided
- GovernanceRequest must validate against schema
- GovernanceContext must be provided
- runtime write boundary must be known
- protected path map must be available or explicitly empty with evidence
- target path must be normalized if present

If required preconditions fail, the engine must not return ALLOW.

---

# 32. Postconditions

After successful evaluation:

- GovernanceDecision exists
- decision is ALLOW, WARN, or BLOCK
- decision has at least one applied rule
- decision has at least one evidence record
- governance_latest.json exists
- governance_history.jsonl is appended
- audit_events.jsonl is appended
- no source files are changed

---

# 33. Invariants

```yaml
invariants:
  - id: "GE-INV-001"
    statement: "Governance decisions require evidence."
  - id: "GE-INV-002"
    statement: "Rule evaluation order is deterministic."
  - id: "GE-INV-003"
    statement: "L0 modification requests are blocked."
  - id: "GE-INV-004"
    statement: "Runtime writes outside .agentx-init/ are blocked."
  - id: "GE-INV-005"
    statement: "Unknown action types are blocked."
  - id: "GE-INV-006"
    statement: "Most restrictive decision wins."
  - id: "GE-INV-007"
    statement: "Governance Engine does not execute actions."
```

---

# 34. Security Contract

Security requirements:

- no network access
- no shell command execution
- no dependency installation
- no unsafe deserialization
- no source mutation
- no approval of L0 mutation
- no silent allow for unknown action
- no environment variable logging
- no secret logging
- no path traversal
- no symlink escape if path resolution is used

---

# 35. Determinism Contract

Governance evaluation must be deterministic for the same request and context.

Requirements:

- deterministic rule order
- deterministic evidence ordering
- deterministic violation ordering
- deterministic warning ordering
- deterministic decision selection
- no randomness
- no network calls
- no wall-clock dependence except declared timestamp

The timestamp may differ across runs but must not affect decision logic.

---

# 36. SIB Bindings

Consumes:

```text
Architecture Analyzer
Repository Scanner
ProtectedPathMap
ArchitectureReport
GovernanceRequest
RiskHints
```

Produces:

```text
GovernanceDecision
GovernanceEvidence
GovernanceViolation
GovernanceAuditRecord
```

Consumed by:

```text
Evolution Planner
Patch Proposal Generator
Validation Runner
CLI commands
```

---

# 37. SIB Registry Entry

```yaml
art_id: "AGENTX::GOVERNANCE_ENGINE"
title: "Governance Engine"
type: "production-impl"
language: "python"
layer: 1
file_path: "agentx_initiator/core/governance_engine.py"
current_version: "v5.0.0"
status: "active"
canonicalization_tier: "T1"
spec_bindings:
  - doc: "AGENTX::FIC-AGENTX-INITIATOR-GOVERNANCE-ENGINE-001"
    binding_type: "GOVERNS"
    binding_strength: "HARD"
```

---

# 38. SIB Dependency Graph

```yaml
nodes:
  - "AGENTX::GOVERNANCE_ENGINE"
  - "AGENTX::GOVERNANCE_RULES"
  - "AGENTX::GOVERNANCE_MODEL"
  - "AGENTX::ARCHITECTURE_REPORT"
  - "AGENTX::PROTECTED_PATH_MAP"
  - "AGENTX::AUDIT_LOG"

edges:
  - src: "AGENTX::GOVERNANCE_ENGINE"
    type: "IMPORTS"
    dst: "AGENTX::GOVERNANCE_RULES"
  - src: "AGENTX::GOVERNANCE_ENGINE"
    type: "IMPORTS"
    dst: "AGENTX::GOVERNANCE_MODEL"
  - src: "AGENTX::GOVERNANCE_ENGINE"
    type: "USES"
    dst: "AGENTX::ARCHITECTURE_REPORT"
  - src: "AGENTX::GOVERNANCE_ENGINE"
    type: "USES"
    dst: "AGENTX::PROTECTED_PATH_MAP"
  - src: "AGENTX::GOVERNANCE_ENGINE"
    type: "IMPORTS"
    dst: "AGENTX::AUDIT_LOG"
```

---

# 39. Test Contract

Required unit tests:

```text
test_valid_request_allows_safe_report_write
test_unknown_action_blocks
test_l0_write_blocks
test_protected_path_write_blocks
test_write_outside_agentx_init_blocks
test_delete_file_blocks
test_run_validation_blocks_without_runner_allowlist
test_non_mutating_plan_under_agentx_init_allows
test_most_restrictive_decision_wins
test_decision_requires_evidence
test_governance_decision_schema_validates
test_governance_history_appends
test_audit_event_appends
```

Required negative tests:

```text
test_invalid_request_blocks
test_missing_target_blocks_or_warns_by_rule
test_path_traversal_blocks
test_source_conflict_blocks
test_evidence_missing_fails
test_unknown_rule_fails_closed
```

Required integration tests:

```text
test_governance_with_architecture_report
test_governance_with_protected_path_map
test_governance_runtime_artifact_generation
```

---

# 40. Test Oracle Strength

Minimum oracle levels:

```yaml
l0_protection: "O4 invariant"
runtime_write_boundary: "O4 invariant"
unknown_action_block: "O3 negative"
most_restrictive_decision: "O4 invariant"
schema_validation: "O3 negative"
audit_append_only: "O4 invariant"
```

Smoke tests alone are not sufficient.

---

# 41. Acceptance Criteria

Governance Engine is accepted only if:

- valid requests produce schema-valid decisions
- unknown actions are blocked
- L0 modification requests are blocked
- writes outside `.agentx-init/` are blocked
- protected path modifications are blocked
- non-mutating reports/plans under `.agentx-init/` may be allowed
- every decision has evidence
- most restrictive decision wins
- governance_latest.json is written
- governance_history.jsonl is appended
- audit_events.jsonl is appended
- no source files are changed
- all required tests pass
- no forbidden imports or shell execution are present

---

# 42. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] target files are listed
[ ] public surface is defined
[ ] governance request schema is defined
[ ] governance decision schema is defined
[ ] evidence schema is defined
[ ] violation schema is defined
[ ] audit schema is defined
[ ] mandatory rules are defined
[ ] rule precedence is defined
[ ] action taxonomy is defined
[ ] write boundaries are defined
[ ] L0 block rule is defined
[ ] unknown action rule is defined
[ ] test obligations are defined
[ ] acceptance criteria are binary
[ ] SIB bindings are listed
[ ] dependency graph is listed
```

---

# 43. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] public surface matches FIC
[ ] no extra public symbols are introduced without justification
[ ] no forbidden dependencies are used
[ ] no writes outside .agentx-init/
[ ] schema validation passes
[ ] unit tests pass
[ ] integration tests pass
[ ] audit event is produced
[ ] governance decision is deterministic for same request/context
[ ] completion record exists
```

---

# 44. Minimal Implementation Package

Milestone 1 implementation package must include:

```text
TASK_CONTRACT.md
GOVERNANCE_ENGINE_EQC_FIC_SCHEMA_v5.md
governance_request.schema.json
governance_decision.schema.json
governance_evidence.schema.json
governance_violation.schema.json
governance_audit.schema.json
implementation_handoff.yaml
completion_record.yaml
```

No coding agent should implement the Governance Engine from this document alone without the implementation package.

---

# 45. Implementation Handoff Envelope

```yaml
implementation_handoff:
  eqc_id: "EQC-AGENTX-INITIATOR-GOVERNANCE-ENGINE-001"
  fic_id: "FIC-AGENTX-INITIATOR-GOVERNANCE-ENGINE-001"
  target_component: "Governance Engine"
  permitted_files:
    - "agentx_initiator/core/governance_engine.py"
    - "agentx_initiator/core/governance_rules.py"
    - "agentx_initiator/core/governance_model.py"
    - "agentx_initiator/schemas/governance_request.schema.json"
    - "agentx_initiator/schemas/governance_decision.schema.json"
    - "agentx_initiator/schemas/governance_evidence.schema.json"
    - "agentx_initiator/schemas/governance_violation.schema.json"
    - "agentx_initiator/schemas/governance_audit.schema.json"
    - "agentx_initiator/tests/test_governance_engine.py"
    - "agentx_initiator/tests/test_governance_rules.py"
    - "agentx_initiator/tests/test_governance_schema.py"
  forbidden_changes:
    - "L0/"
    - "L1/"
    - "L2/"
    - "source files unrelated to governance"
  allowed_statuses:
    - "IMPLEMENTED_UNVALIDATED"
    - "VALIDATED"
    - "NO_CHANGE"
    - "BLOCKED"
  stop_conditions:
    - "Governance request schema conflicts with existing schema standard"
    - "write boundary cannot be enforced"
    - "L0 block rule cannot be enforced"
    - "governance engine needs to execute actions"
    - "risk classification is required before decision"
```

---

# 46. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  eqc_id: "EQC-AGENTX-INITIATOR-GOVERNANCE-ENGINE-001"
  fic_id: "FIC-AGENTX-INITIATOR-GOVERNANCE-ENGINE-001"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|NO_CHANGE|BLOCKED"
  files_created_or_changed: []
  tests_created_or_changed: []
  schemas_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  deviations_from_eqc_fic_schema: []
  unresolved_risks: []
```

The implementation must not be considered complete without evidence.

---

# 47. Residual Risks

Known residual risks:

```yaml
residual_risks:
  - id: "GE-RISK-001"
    description: "Governance policy is intentionally minimal in Milestone 1."
    severity: "medium"
    mitigation: "Block unknown or ambiguous actions by default."
  - id: "GE-RISK-002"
    description: "User approval cannot override L0 protection in Milestone 1."
    severity: "low"
    mitigation: "Document this as an explicit invariant."
  - id: "GE-RISK-003"
    description: "Risk Engine may later provide richer risk context."
    severity: "low"
    mitigation: "Keep RiskHints advisory only."
```

---

# 48. Definition of Done

Governance Engine Milestone 1 is done when it can:

- validate a GovernanceRequest
- evaluate target path and action type
- block L0 modifications
- block protected path modifications
- block writes outside `.agentx-init/`
- block unknown action types
- allow safe non-mutating `.agentx-init/` outputs
- produce schema-valid GovernanceDecision
- produce GovernanceEvidence
- produce GovernanceViolation where applicable
- write governance_latest.json
- append governance_history.jsonl
- append audit_events.jsonl
- pass required tests
- leave source files unchanged

---

# 49. Freeze Rule

This document is now the controlling Governance Engine EQC+FIC+Schema document for Milestone 1.

Do not keep expanding this document unless a true implementation-blocking gap is discovered.

Next artifacts should be:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
governance_request.schema.json
governance_decision.schema.json
governance_evidence.schema.json
governance_violation.schema.json
governance_audit.schema.json
completion_record.schema.json
```

---

# 50. Final Success Definition

Governance Engine v1 implementation is successful when it can deterministically evaluate proposed Initiator actions against Agent_X governance rules and produce schema-valid, evidence-backed ALLOW, WARN, or BLOCK decisions without executing actions or modifying repository source files.

---

# 51. Final Rating

This EQC+FIC+Schema document is rated **10/10** for the initial Governance Engine component.

It is ready to be used as the controlling document for the Governance Engine Milestone 1 implementation package.
