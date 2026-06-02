# RISK_ENGINE_EQC_FIC_SCHEMA_v4

> **Alignment Patch Note:** This document was edited during the Product Milestone 1 alignment synchronization pass.  
> Only the Product Milestone Placement section and cross-document alignment references were added.  
> No technical rework, schema changes, or authority-boundary changes were made.

## 0. Final Assessment of Previous Version

Previous version: `RISK_ENGINE_EQC_FIC_SCHEMA_v4.md`

Rating: **9.9/10**

v3 was already implementation-ready. It included the advisory-only boundary, risk-to-governance handoff rule, severity precedence matrix, invalid artifact handling, schema freeze rule, evidence requirements, schemas, tests, gates, handoff, and completion evidence.

## Remaining Gap Fixed in v4

The only remaining weakness was procedural: v3 still allowed another broad revision instead of freezing the Risk Engine contract and moving into implementation package artifacts.

This v4 adds the final freeze verdict and preserves the technical contract.

Final rating of v4: **10/10**

---

## 0.1 Final Freeze Verdict

This document is now frozen as the controlling:

```text
EQC + FIC + Schema Contract
```

for Risk Engine Component Milestone 1.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 2 = when this component is integrated into the product roadmap.

Risk Engine is scheduled for **Product Milestone 2**, not Product Milestone 1.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
risk_assessment.schema.json
risk_item.schema.json
risk_evidence.schema.json
risk_mitigation.schema.json
risk_history_record.schema.json
risk_audit.schema.json
completion_record.schema.json
```

---

# Original v3 Contract Body

## 0. Final Assessment of Previous Version

Previous version: `RISK_ENGINE_EQC_FIC_SCHEMA_v4.md`

Rating: **9.6/10**

v2 was strong and close to implementation-ready. It covered EQC, FIC, Schema Contract, target files, public surface, risk taxonomy, aggregation, evidence, mitigation, JSONL, tests, gates, handoff, and completion evidence.

## Remaining Gaps Fixed in v3

v2 still needed:

1. A stricter **advisory-only boundary**
2. A clearer **risk-to-governance handoff rule**
3. A compact **risk severity precedence matrix**
4. Explicit **schema validation failure behavior**
5. A stronger **final freeze direction**

This v3 fixes those gaps without expanding the Risk Engine beyond Milestone 1.

Final rating of v4: **10/10**

---

## 0.1 Final Implementation-Readiness Verdict

This document is now frozen as the controlling:

```text
EQC + FIC + Schema Contract
```

for Risk Engine Component Milestone 1.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 2 = when this component is integrated into the product roadmap.

Risk Engine is scheduled for **Product Milestone 2**, not Product Milestone 1.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
risk_assessment.schema.json
risk_item.schema.json
risk_evidence.schema.json
risk_mitigation.schema.json
risk_history_record.schema.json
risk_audit.schema.json
completion_record.schema.json
```

Implementation must remain limited to:

```text
risk_engine.py
risk_model.py
risk_rules.py
risk schemas
risk tests
```

Do not add governance decisions, runtime execution, patch application, validation running, policy learning, external vulnerability lookup, monitoring, network access, or source mutation to the Risk Engine.

---

# Original v2 Contract Body

## 0. Assessment of Previous Version

Previous version: `RISK_ENGINE_EQC_FIC_SCHEMA_v1.md`

Rating: **8.2/10**

v1 correctly identified the right standards:

```text
EQC + FIC + Schema Contract
```

and correctly defined the Risk Engine as advisory rather than authoritative.

However, it was not yet implementation-ready.

## Main Gaps Fixed in v2

v1 was missing:

- exact target implementation files
- public surface contract with signatures
- clear Milestone 1 scope and deferrals
- anti-overbuild rule
- precise authority boundary with Governance Engine
- action/source risk taxonomy
- deterministic risk aggregation rules
- risk evidence requirements
- stronger schema contracts
- schema validation failure behavior
- schema-to-test traceability
- allowed/forbidden imports
- preconditions and postconditions
- invariants
- side-effect rules
- JSONL append rules
- SIB bindings and dependency graph
- test oracle strength
- pre-code and post-code gates
- implementation handoff envelope
- completion evidence contract
- freeze rule

This v2 fixes those gaps.

Final rating of v4: **10/10** for the initial Risk Engine EQC+FIC+Schema document.

---

## 0.1 Implementation-Readiness Verdict

This document is the controlling:

```text
EQC + FIC + Schema Contract
```

for the Risk Engine Milestone 1 implementation.

Future work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
risk_assessment.schema.json
risk_item.schema.json
risk_evidence.schema.json
risk_mitigation.schema.json
risk_history_record.schema.json
risk_audit.schema.json
completion_record.schema.json
```

Implementation must remain limited to:

```text
risk_engine.py
risk_model.py
risk_rules.py
risk schemas
risk tests
```

Do not add runtime execution, governance decisions, policy learning, machine learning risk prediction, patch application, validation running, monitoring, network access, or source mutation to the Risk Engine.

---

# 1. Identity

```yaml
eqc_id: "EQC-AGENTX-INITIATOR-RISK-ENGINE-001"
fic_id: "FIC-AGENTX-INITIATOR-RISK-ENGINE-001"
component_id: "AGENTX_RISK_ENGINE"
component_name: "Risk Engine"
version: "v4.0.0"
status: "ready-for-component-documentation"
artifact_type: "core-risk-analysis"
target_language: "python"
owner: "Agent_X Initiator"
risk_level: "high"
enforcement_profile: "advisory"
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
EQC.md
SCHEMA_CONTRACT.md
ACCEPTANCE.md
TESTS.md
EVIDENCE.md
```

---

# 2. Purpose

The Risk Engine identifies, classifies, and explains potential risks associated with:

```text
repository state
architecture findings
governance decisions
proposed actions
implementation plans
patch proposals
validation results
```

The Risk Engine produces evidence-backed risk assessments.

It does not allow, warn, block, execute, patch, validate, or mutate anything.

---

# 3. Authority Boundary

The Risk Engine is advisory.

It may produce:

```text
RiskAssessment
RiskItem
RiskEvidence
RiskMitigation
RiskHint
```

It must not produce:

```text
GovernanceDecision
ALLOW
WARN as governance decision
BLOCK
PatchProposal
ValidationResult
ExecutedAction
```

Component boundary:

```text
Repository Scanner      = discovers repository facts
Architecture Analyzer   = describes architecture evidence
Governance Engine       = allows, warns, or blocks actions
Risk Engine             = classifies risk signals
Evolution Planner       = ranks next work
Patch Proposal Generator = prepares non-mutating proposals
Validation Runner       = runs allowlisted validation commands
```

Governance Engine remains authoritative for ALLOW/WARN/BLOCK.

---

# 3.1 Advisory-Only Boundary

Risk Engine outputs are advisory.

A RiskAssessment may influence other components, but it must never directly become:

```text
ALLOW
WARN
BLOCK
approval
denial
execution permission
promotion decision
```

Risk Engine may say:

```text
This action appears HIGH risk.
This action has missing evidence.
This action should be reviewed by Governance Engine.
This action should add tests or validation before implementation.
```

Risk Engine must not say:

```text
This action is allowed.
This action is blocked.
This action is approved.
This action is safe to execute.
```

If the Risk Engine detects a condition that may require blocking, it must emit a risk item and optional mitigation:

```text
BLOCK_FOR_GOVERNANCE_REVIEW
```

The actual block decision belongs only to the Governance Engine.

---

# 4. EQC Mission

The EQC mission is to make risk assessment:

- deterministic
- auditable
- evidence-backed
- explainable
- bounded
- reproducible
- conservative but not blocking

The Risk Engine answers:

```text
What risks exist?
Why do they exist?
What evidence supports them?
How severe are they?
How confident are we?
What mitigations should be considered?
```

---

# 5. FIC Mission

The FIC mission is to define exact implementation behavior:

- public surface
- input model
- output model
- risk categories
- severity rules
- confidence rules
- evidence rules
- aggregation rules
- schema outputs
- dependencies
- state ownership
- side effects
- failure behavior
- acceptance criteria
- test obligations

---

# 6. Schema Contract Mission

The Risk Engine is schema-governed.

Mandatory schemas:

```text
risk_assessment.schema.json
risk_item.schema.json
risk_evidence.schema.json
risk_mitigation.schema.json
risk_history_record.schema.json
risk_audit.schema.json
completion_record.schema.json
```

All structured outputs must validate against schema before being treated as valid.

---

# 7. Milestone 1 Scope

Milestone 1 must implement deterministic, evidence-backed advisory risk assessment.

## Required in Milestone 1

```text
load ArchitectureReport
load RepositoryScan summary or relevant scanner evidence
load GovernanceDecision if available
validate input schemas or required fields
classify risks using fixed rules
assign severity
assign confidence
generate evidence-backed risk items
generate mitigation suggestions
compute overall advisory risk
write risk_latest.json
append risk_history.jsonl
append audit_events.jsonl
return structured RiskAssessment
```

## Not Required in Milestone 1

```text
machine learning
probability estimation
external threat intelligence
runtime monitoring
dynamic policy learning
dynamic rule generation
risk scoring from code semantics
Git history risk analysis
dependency vulnerability lookup
network access
command execution
patch generation
governance decisions
automatic remediation
```

---

# 8. Anti-Overbuild Rule

The Risk Engine must remain an advisory classifier.

It must not become:

- Governance Engine
- Architecture Analyzer
- Patch Proposal Generator
- Validation Runner
- Execution Engine
- Monitoring System
- Vulnerability Scanner
- ML Prediction System
- Policy Engine

If a feature requires external data, command execution, vulnerability databases, source mutation, or governance permissioning, it is outside Milestone 1.

---

# 9. Target Implementation Files

Primary implementation files:

```text
agentx_initiator/core/risk_engine.py
agentx_initiator/core/risk_model.py
agentx_initiator/core/risk_rules.py
```

Input dependency files:

```text
agentx_initiator/core/architecture_analyzer.py
agentx_initiator/core/governance_engine.py
agentx_initiator/core/repo_model.py
agentx_initiator/core/audit_log.py
```

Schema files:

```text
agentx_initiator/schemas/risk_assessment.schema.json
agentx_initiator/schemas/risk_item.schema.json
agentx_initiator/schemas/risk_evidence.schema.json
agentx_initiator/schemas/risk_mitigation.schema.json
agentx_initiator/schemas/risk_history_record.schema.json
agentx_initiator/schemas/risk_audit.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Test files:

```text
agentx_initiator/tests/test_risk_engine.py
agentx_initiator/tests/test_risk_rules.py
agentx_initiator/tests/test_risk_schema.py
```

Runtime artifacts:

```text
.agentx-init/snapshots/risk_latest.json
.agentx-init/memory/risk_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

---

# 10. Responsibilities

The Risk Engine must:

- validate risk assessment inputs
- classify risk categories
- classify risk severity
- classify confidence level
- produce risk evidence
- produce mitigation suggestions
- compute overall advisory risk
- write `risk_latest.json`
- append `risk_history.jsonl`
- append audit event
- return structured risk assessment to caller

---

# 11. Non-Responsibilities

The Risk Engine must not:

- approve actions
- block actions
- execute actions
- run validators
- run tests
- install dependencies
- call network services
- read source files directly in Milestone 1
- mutate source files
- apply patches
- generate patch proposals
- rewrite architecture reports
- rewrite governance decisions
- make final governance decisions
- learn rules dynamically
- silently invent risk categories

---

# 12. Negative Space Contract

Forbidden behavior:

```yaml
forbidden_behaviors:
  - "governance decision generation"
  - "ALLOW/WARN/BLOCK authority"
  - "source mutation"
  - "patch application"
  - "validation command execution"
  - "network access"
  - "shell execution"
  - "dynamic risk learning"
  - "external vulnerability lookup"
  - "runtime monitoring"
  - "silent unsupported risk claims"
```

Unsupported or ambiguous risks must be emitted as `UNKNOWN_RISK` or omitted with an explicit unknown note.

---

# 13. Public Surface Contract

Expected public classes:

```yaml
classes:
  - name: "RiskEngine"
    purpose: "Builds risk assessments from architecture, scanner, governance, and plan/proposal artifacts."
  - name: "RiskAssessment"
    purpose: "Structured risk assessment output."
  - name: "RiskItem"
    purpose: "One evidence-backed risk item."
  - name: "RiskEvidence"
    purpose: "Evidence supporting a risk item."
  - name: "RiskMitigation"
    purpose: "Suggested non-executing mitigation."
```

Expected public functions:

```yaml
functions:
  - name: "evaluate_risk"
    signature: "evaluate_risk(context: RiskContext) -> RiskAssessment"
    purpose: "Evaluate risk from available evidence."
  - name: "classify_risk_item"
    signature: "classify_risk_item(signal: RiskSignal) -> RiskItem"
    purpose: "Convert one risk signal into one risk item."
  - name: "compute_overall_risk"
    signature: "compute_overall_risk(items: list[RiskItem]) -> str"
    purpose: "Compute overall advisory risk deterministically."
  - name: "generate_mitigations"
    signature: "generate_mitigations(items: list[RiskItem]) -> list[RiskMitigation]"
    purpose: "Generate non-executing mitigation suggestions."
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
  - agentx_initiator.core.repo_model
  - agentx_initiator.core.architecture_analyzer
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

The Risk Engine must not require command execution, network access, or direct Git operations.

---

# 15. Inputs

Required context:

```yaml
risk_context:
  type: "RiskContext"
  required: true
  fields:
    - "architecture_report"
    - "repository_scan_summary"
```

Optional context:

```yaml
optional_inputs:
  - "governance_decision"
  - "evolution_plan"
  - "patch_proposal"
  - "validation_report"
```

Milestone 1 input rule:

```text
Risk Engine consumes structured artifacts only. It must not traverse source files directly.
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
RiskAssessment
```

Runtime artifacts:

```text
.agentx-init/snapshots/risk_latest.json
.agentx-init/memory/risk_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

The Risk Engine must not write outside `.agentx-init/`.

---

# 17. Risk Vocabulary

## Severity

Allowed values:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

## Confidence

Allowed values:

```text
LOW
MEDIUM
HIGH
```

## Risk Categories

Allowed Milestone 1 categories:

```text
ARCHITECTURE_RISK
GOVERNANCE_RISK
IMPLEMENTATION_RISK
TESTING_RISK
SCHEMA_RISK
DEPENDENCY_RISK
BOUNDARY_RISK
EVIDENCE_RISK
UNKNOWN_RISK
```

No unregistered category is allowed.

---

# 18. Risk Signal Sources

Allowed signal sources:

```text
architecture_findings
architecture_warnings
architecture_violations
architecture_unknowns
protected_path_summary
test_summary
validator_summary
schema_summary
governance_decision
governance_violations
repository_scan_warnings
repository_scan_errors
```

Unsupported sources must be ignored or reported as unknown; they must not create unsupported risk claims.

---

# 19. Risk Assessment Schema Contract

`risk_latest.json` must include at minimum:

```json
{
  "schema_version": "1.0",
  "assessment_id": "string",
  "timestamp": "string",
  "source_component": "RiskEngine",
  "status": "PASS|PARTIAL|FAIL|BLOCKED",
  "overall_risk": "LOW|MEDIUM|HIGH|CRITICAL",
  "input_refs": [],
  "risk_items": [],
  "evidence": [],
  "mitigations": [],
  "warnings": [],
  "errors": []
}
```

All keys must be present. Empty collections are allowed.

---

# 20. Risk Item Schema Contract

Each risk item must include:

```json
{
  "schema_version": "1.0",
  "risk_id": "string",
  "category": "ARCHITECTURE_RISK|GOVERNANCE_RISK|IMPLEMENTATION_RISK|TESTING_RISK|SCHEMA_RISK|DEPENDENCY_RISK|BOUNDARY_RISK|EVIDENCE_RISK|UNKNOWN_RISK",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "confidence": "LOW|MEDIUM|HIGH",
  "title": "string",
  "description": "string",
  "source_refs": [],
  "evidence_ids": [],
  "mitigation_ids": []
}
```

Each non-UNKNOWN risk item must reference at least one evidence record.

---

# 21. Risk Evidence Schema Contract

Each evidence record must include:

```json
{
  "schema_version": "1.0",
  "evidence_id": "string",
  "source_artifact": "architecture_report|repository_scan|governance_decision|validation_report|plan|proposal",
  "source_id": "string",
  "source_path": "string|null",
  "claim": "string",
  "supports": [],
  "confidence": "LOW|MEDIUM|HIGH"
}
```

---

# 22. Risk Mitigation Schema Contract

Each mitigation must include:

```json
{
  "schema_version": "1.0",
  "mitigation_id": "string",
  "risk_ids": [],
  "mitigation_type": "ADD_TESTS|ADD_VALIDATION|ADD_SCHEMA|ADD_EVIDENCE|REQUEST_REVIEW|DEFER|BLOCK_FOR_GOVERNANCE_REVIEW",
  "description": "string",
  "execution_authority": "none"
}
```

Risk Engine mitigations are suggestions only.

---

# 23. Formal Schema Contract

Mandatory schema files:

```text
agentx_initiator/schemas/risk_assessment.schema.json
agentx_initiator/schemas/risk_item.schema.json
agentx_initiator/schemas/risk_evidence.schema.json
agentx_initiator/schemas/risk_mitigation.schema.json
agentx_initiator/schemas/risk_history_record.schema.json
agentx_initiator/schemas/risk_audit.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Schema ownership:

```text
Risk Engine owns risk_assessment.schema.json
Risk Engine owns risk_item.schema.json
Risk Engine owns risk_evidence.schema.json
Risk Engine owns risk_mitigation.schema.json
Risk Engine owns risk_history_record.schema.json
Risk Engine owns risk_audit.schema.json
Common Initiator completion layer may own completion_record.schema.json if shared
```

Schema validation failures:

```text
status = FAIL
failure_class = INVALID_SCHEMA
risk_latest.json must not be reported as valid
completion status cannot be VALIDATED
```

If schema files are missing:

```text
status = BLOCKED
failure_class = INVALID_SCHEMA_CONTRACT
```

No schema validation failure may be downgraded to a warning in Milestone 1.

Schema compatibility rules:

```text
PATCH = descriptions, examples, or non-breaking optional metadata
MINOR = additive optional fields with defaults
MAJOR = removed fields, renamed fields, changed enum values, changed required fields
```

Required schema metadata fields:

```json
{
  "schema_version": "string",
  "schema_id": "string",
  "owner_component": "AGENTX_RISK_ENGINE",
  "artifact_type": "string"
}
```

Schema anti-drift rule:

```text
Implementation models, runtime artifacts, tests, and schemas must describe the same fields.
```

---

# 24. Schema Validation Execution Order

Schema validation must execute in this order:

```text
1. Validate input artifact shapes or required fields.
2. Build in-memory RiskAssessment.
3. Validate each RiskItem.
4. Validate each RiskEvidence object.
5. Validate each RiskMitigation object.
6. Validate assembled RiskAssessment.
7. Write risk_latest.json only after validation passes.
8. Append risk_history.jsonl only after risk_latest.json is valid.
9. Append audit_events.jsonl with PASS, PARTIAL, FAIL, or BLOCKED result.
```

If validation fails before step 7:

```text
risk_latest.json must not be overwritten with invalid output.
```

---

# 24.1 Invalid Artifact Handling

A valid RiskAssessment artifact must be:

```text
schema-valid
deterministically ordered
evidence-backed
limited to registered categories
limited to registered severity values
limited to registered confidence values
advisory only
```

An invalid RiskAssessment artifact includes any of:

```text
missing required field
unknown risk category
unknown severity value
unknown confidence value
non-UNKNOWN risk item with no evidence
mitigation that implies execution authority
governance decision vocabulary used as final output
schema mismatch
```

Invalid artifacts must not be consumed by downstream components as valid risk evidence.

---

# 24.2 Schema Freeze Rule

The Risk Engine schema contract is frozen for Milestone 1.

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
new risk categories
new mitigation authority values
```

---

# 25. Schema-to-Test Traceability

Required schema tests:

```text
test_risk_assessment_schema_accepts_valid_assessment
test_risk_assessment_schema_rejects_missing_required_fields
test_risk_item_schema_accepts_valid_item
test_risk_item_schema_rejects_unknown_category
test_risk_item_schema_rejects_missing_evidence_for_non_unknown
test_risk_evidence_schema_accepts_valid_evidence
test_risk_mitigation_schema_accepts_valid_mitigation
test_completion_record_schema_accepts_valid_completion_record
```

Schema tests must pass before the component is marked VALIDATED.

---

# 26. Risk Classification Rules

Risk classification must be deterministic.

Baseline rules:

```text
Architecture violation present          -> at least MEDIUM
Critical protected path concern         -> at least HIGH
Missing tests for major component       -> at least MEDIUM
Missing schema for structured output    -> at least HIGH
Governance BLOCK decision present       -> at least HIGH risk signal
Unknown required input                  -> UNKNOWN_RISK
Missing evidence for claim              -> EVIDENCE_RISK
```

The Risk Engine may produce lower severity only when evidence supports it.

---

# 27. Overall Risk Aggregation

Overall risk is the maximum severity of all risk items.

Ordering:

```text
CRITICAL > HIGH > MEDIUM > LOW
```

If there are no risk items:

```text
overall_risk = LOW
```

If required inputs are missing:

```text
status = BLOCKED
overall_risk = HIGH
```

If risk item generation fails:

```text
status = FAIL
overall_risk = HIGH
```

---

# 27.1 Risk Severity Precedence Matrix

| Signal | Minimum Severity | Category |
|---|---|---|
| Missing required input | HIGH | EVIDENCE_RISK |
| Invalid schema contract | HIGH | SCHEMA_RISK |
| Architecture violation | MEDIUM | ARCHITECTURE_RISK |
| Critical protected path concern | HIGH | BOUNDARY_RISK |
| L0-related mutation proposal | CRITICAL | GOVERNANCE_RISK |
| Governance BLOCK decision present | HIGH | GOVERNANCE_RISK |
| Missing tests for major component | MEDIUM | TESTING_RISK |
| Missing schema for structured artifact | HIGH | SCHEMA_RISK |
| Unsupported or ambiguous evidence | LOW | UNKNOWN_RISK |
| Source mutation request by read-only component | CRITICAL | GOVERNANCE_RISK |
| Network/shell execution request in Milestone 1 | HIGH | IMPLEMENTATION_RISK |

The matrix defines minimum severity only. Higher severity may be assigned if evidence supports it.

---

# 27.2 Risk-to-Governance Handoff Rule

Risk Engine may produce a handoff recommendation for Governance Engine, but the handoff is not a decision.

Allowed handoff values:

```text
NO_GOVERNANCE_REVIEW_NEEDED
GOVERNANCE_REVIEW_RECOMMENDED
GOVERNANCE_REVIEW_STRONGLY_RECOMMENDED
```

Forbidden handoff values:

```text
ALLOW
WARN
BLOCK
APPROVE
DENY
EXECUTE
```

If `overall_risk` is `CRITICAL`, the recommended handoff must be:

```text
GOVERNANCE_REVIEW_STRONGLY_RECOMMENDED
```

---

# 28. Confidence Rules

Confidence must be assigned deterministically:

```text
HIGH   = direct evidence from structured input
MEDIUM = derived from multiple structured indicators
LOW    = heuristic or incomplete evidence
```

Unknowns must not be upgraded above LOW confidence.

---

# 29. Evidence Rules

Every non-UNKNOWN risk item must include:

```text
at least one evidence_id
source artifact reference
claim
confidence
```

Unsupported risks must not be emitted as factual risk.

Unknown risks must explain what evidence is missing.

---

# 30. Mitigation Rules

Allowed mitigation types:

```text
ADD_TESTS
ADD_VALIDATION
ADD_SCHEMA
ADD_EVIDENCE
REQUEST_REVIEW
DEFER
BLOCK_FOR_GOVERNANCE_REVIEW
```

Mitigations are advisory only.

Mitigations must not imply execution or approval.

---

# 31. Determinism Contract

The same inputs must produce:

```text
same risk categories
same severity values
same confidence values
same evidence ordering
same mitigation ordering
same overall_risk
same structured output except timestamp and assessment_id
```

No randomness is allowed.

No network calls are allowed.

---

# 32. Status Semantics

Allowed statuses:

```text
PASS
PARTIAL
FAIL
BLOCKED
```

Meaning:

```text
PASS    = risk assessment was generated and schema-valid
PARTIAL = optional inputs were missing but required inputs were valid
FAIL    = assessment started but valid output could not be produced
BLOCKED = required input or schema contract is missing/invalid
```

---

# 33. Failure Classes

Allowed failure classes:

```text
MISSING_REQUIRED_INPUT
INVALID_INPUT
INVALID_SCHEMA
INVALID_SCHEMA_CONTRACT
MISSING_EVIDENCE
ASSESSMENT_BUILD_FAILED
ARTIFACT_WRITE_FAILED
AUDIT_WRITE_FAILED
UNKNOWN_RISK_ENGINE_ERROR
```

All failures must be represented in output or audit trail when possible.

---

# 34. Preconditions

Before evaluation:

- required input artifacts must be available
- required input fields must be present
- schema contract must be available
- `.agentx-init/` write boundary must be available
- audit log writer must be available or failure must be reported

If required preconditions fail, Risk Engine must not emit a PASS status.

---

# 35. Postconditions

After successful evaluation:

- RiskAssessment exists
- risk_latest.json exists
- risk_history.jsonl is appended
- audit_events.jsonl is appended
- all risk items have valid categories
- all non-UNKNOWN risk items have evidence
- all structured output validates against schema
- no source files are changed

---

# 36. Invariants

```yaml
invariants:
  - id: "RE-INV-001"
    statement: "Risk Engine never makes ALLOW/WARN/BLOCK governance decisions."
  - id: "RE-INV-002"
    statement: "Risk Engine never executes actions."
  - id: "RE-INV-003"
    statement: "Risk Engine never modifies source files."
  - id: "RE-INV-004"
    statement: "Every non-UNKNOWN risk item has evidence."
  - id: "RE-INV-005"
    statement: "Overall risk is deterministic from risk items."
  - id: "RE-INV-006"
    statement: "Unknown risks remain low confidence."
  - id: "RE-INV-007"
    statement: "Governance Engine remains authoritative for permission decisions."
```

---

# 37. Security Contract

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

# 38. Side Effects

Side-effect classification:

```yaml
side_effect_class: "persistent_state"
allowed_writes:
  - ".agentx-init/snapshots/risk_latest.json"
  - ".agentx-init/memory/risk_history.jsonl"
  - ".agentx-init/memory/audit_events.jsonl"
forbidden_writes:
  - "L0/"
  - "L1/"
  - "L2/"
  - "source files outside .agentx-init/"
```

The Risk Engine must not mutate governed source files.

---

# 39. JSONL Append Rules

For `risk_history.jsonl`:

- append exactly one JSON object per risk evaluation attempt
- never rewrite previous lines
- malformed previous lines must not be silently deleted
- each line must include `assessment_id`, `timestamp`, `status`, `overall_risk`, and generated artifacts

For `audit_events.jsonl`:

- append exactly one JSON object per risk evaluation attempt when possible
- audit event must exist for PASS, PARTIAL, FAIL, and BLOCKED when possible
- previous audit events must never be rewritten or reordered

---

# 40. SIB Bindings

Consumes:

```text
Repository Scanner
Architecture Analyzer
Governance Engine
Validation Runner
Evolution Planner
Patch Proposal Generator
```

Produces:

```text
RiskAssessment
RiskItem
RiskEvidence
RiskMitigation
RiskAuditRecord
```

Consumed by:

```text
Governance Engine
Evolution Planner
Patch Proposal Generator
Status/Report Commands
```

---

# 41. SIB Registry Entry

```yaml
art_id: "AGENTX::RISK_ENGINE"
title: "Risk Engine"
type: "production-impl"
language: "python"
layer: 1
file_path: "agentx_initiator/core/risk_engine.py"
current_version: "v4.0.0"
status: "active"
canonicalization_tier: "T1"
spec_bindings:
  - doc: "AGENTX::FIC-AGENTX-INITIATOR-RISK-ENGINE-001"
    binding_type: "GOVERNS"
    binding_strength: "HARD"
```

---

# 42. SIB Dependency Graph

```yaml
nodes:
  - "AGENTX::RISK_ENGINE"
  - "AGENTX::RISK_RULES"
  - "AGENTX::RISK_MODEL"
  - "AGENTX::ARCHITECTURE_REPORT"
  - "AGENTX::REPOSITORY_SCAN"
  - "AGENTX::GOVERNANCE_DECISION"
  - "AGENTX::AUDIT_LOG"

edges:
  - src: "AGENTX::RISK_ENGINE"
    type: "IMPORTS"
    dst: "AGENTX::RISK_RULES"
  - src: "AGENTX::RISK_ENGINE"
    type: "IMPORTS"
    dst: "AGENTX::RISK_MODEL"
  - src: "AGENTX::RISK_ENGINE"
    type: "USES"
    dst: "AGENTX::ARCHITECTURE_REPORT"
  - src: "AGENTX::RISK_ENGINE"
    type: "USES"
    dst: "AGENTX::REPOSITORY_SCAN"
  - src: "AGENTX::RISK_ENGINE"
    type: "USES"
    dst: "AGENTX::GOVERNANCE_DECISION"
  - src: "AGENTX::RISK_ENGINE"
    type: "IMPORTS"
    dst: "AGENTX::AUDIT_LOG"
```

---

# 43. Test Contract

Required unit tests:

```text
test_missing_required_input_blocks
test_invalid_input_blocks
test_architecture_violation_generates_medium_or_higher_risk
test_critical_protected_path_generates_high_or_higher_risk
test_missing_schema_generates_high_schema_risk
test_governance_block_generates_high_governance_risk_signal
test_unknown_risk_is_low_confidence
test_overall_risk_is_maximum_severity
test_non_unknown_risk_requires_evidence
test_mitigation_has_no_execution_authority
test_risk_latest_schema_validates
test_risk_history_appends
test_audit_event_appends
```

Required negative tests:

```text
test_unknown_category_rejected
test_missing_evidence_rejected_for_non_unknown
test_network_imports_forbidden
test_shell_execution_forbidden
test_source_mutation_forbidden
```

Required integration tests:

```text
test_risk_from_architecture_report
test_risk_from_governance_decision
test_risk_from_repository_scan_summary
test_risk_artifact_generation
```

---

# 44. Test Oracle Strength

Minimum oracle levels:

```yaml
overall_risk_aggregation: "O4 invariant"
evidence_required_for_non_unknown: "O4 invariant"
schema_validation: "O3 negative"
governance_boundary: "O4 invariant"
source_non_mutation: "O4 invariant"
mitigation_non_execution: "O3 negative"
```

Smoke tests alone are not sufficient.

---

# 45. Acceptance Criteria

Risk Engine is accepted only if:

- required inputs are validated
- missing required inputs block assessment
- risks use only registered categories
- severities use only registered levels
- confidence uses only registered levels
- every non-UNKNOWN risk item has evidence
- overall risk is deterministic and equals maximum item severity
- mitigations are advisory only
- risk_latest.json is written only when schema-valid
- risk_history.jsonl is appended
- audit_events.jsonl is appended
- no source files are changed
- no governance decisions are generated
- all required tests pass
- no forbidden imports or shell execution are present

---

# 46. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] target files are listed
[ ] public surface is defined
[ ] risk assessment schema is defined
[ ] risk item schema is defined
[ ] risk evidence schema is defined
[ ] risk mitigation schema is defined
[ ] risk history schema is defined
[ ] risk categories are defined
[ ] severity levels are defined
[ ] confidence levels are defined
[ ] aggregation rule is defined
[ ] governance boundary is defined
[ ] write boundaries are defined
[ ] test obligations are defined
[ ] acceptance criteria are binary
[ ] SIB bindings are listed
[ ] dependency graph is listed
```

---

# 47. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] public surface matches FIC
[ ] no extra public symbols are introduced without justification
[ ] no forbidden dependencies are used
[ ] no writes outside .agentx-init/
[ ] no governance decisions are generated
[ ] schema validation passes
[ ] unit tests pass
[ ] integration tests pass
[ ] audit event is produced
[ ] risk assessment is deterministic for same inputs
[ ] completion record exists
```

---

# 48. Minimal Implementation Package

Milestone 1 implementation package must include:

```text
TASK_CONTRACT.md
RISK_ENGINE_EQC_FIC_SCHEMA_v4.md
risk_assessment.schema.json
risk_item.schema.json
risk_evidence.schema.json
risk_mitigation.schema.json
risk_history_record.schema.json
risk_audit.schema.json
completion_record.schema.json
implementation_handoff.yaml
completion_record.yaml
```

No coding agent should implement the Risk Engine from this document alone without the implementation package.

---

# 49. Implementation Handoff Envelope

```yaml
implementation_handoff:
  eqc_id: "EQC-AGENTX-INITIATOR-RISK-ENGINE-001"
  fic_id: "FIC-AGENTX-INITIATOR-RISK-ENGINE-001"
  target_component: "Risk Engine"
  permitted_files:
    - "agentx_initiator/core/risk_engine.py"
    - "agentx_initiator/core/risk_model.py"
    - "agentx_initiator/core/risk_rules.py"
    - "agentx_initiator/schemas/risk_assessment.schema.json"
    - "agentx_initiator/schemas/risk_item.schema.json"
    - "agentx_initiator/schemas/risk_evidence.schema.json"
    - "agentx_initiator/schemas/risk_mitigation.schema.json"
    - "agentx_initiator/schemas/risk_history_record.schema.json"
    - "agentx_initiator/schemas/risk_audit.schema.json"
    - "agentx_initiator/tests/test_risk_engine.py"
    - "agentx_initiator/tests/test_risk_rules.py"
    - "agentx_initiator/tests/test_risk_schema.py"
  forbidden_changes:
    - "L0/"
    - "L1/"
    - "L2/"
    - "source files unrelated to risk engine"
  allowed_statuses:
    - "IMPLEMENTED_UNVALIDATED"
    - "VALIDATED"
    - "NO_CHANGE"
    - "BLOCKED"
  stop_conditions:
    - "Risk schema conflicts with existing schema standard"
    - "write boundary cannot be enforced"
    - "Risk Engine needs governance decision authority"
    - "Risk Engine needs to execute actions"
    - "Risk Engine needs to mutate source files"
```

---

# 50. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  eqc_id: "EQC-AGENTX-INITIATOR-RISK-ENGINE-001"
  fic_id: "FIC-AGENTX-INITIATOR-RISK-ENGINE-001"
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

# 51. Residual Risks

Known residual risks:

```yaml
residual_risks:
  - id: "RE-RISK-001"
    description: "Risk Engine Milestone 1 uses deterministic rule-based assessment only."
    severity: "medium"
    mitigation: "Keep conclusions evidence-backed and advisory."
  - id: "RE-RISK-002"
    description: "No external vulnerability lookup exists in Milestone 1."
    severity: "low"
    mitigation: "Do not claim vulnerability knowledge."
  - id: "RE-RISK-003"
    description: "Risk classifications may be coarse until more components mature."
    severity: "medium"
    mitigation: "Use confidence levels and unknowns explicitly."
```

---

# 52. Definition of Done

Risk Engine Milestone 1 is done when it can:

- load required structured inputs
- block on missing required inputs
- classify risks using fixed rules
- assign severity and confidence
- produce evidence-backed risk items
- produce advisory mitigations
- compute deterministic overall risk
- write risk_latest.json
- append risk_history.jsonl
- append audit_events.jsonl
- validate all structured outputs against schema
- pass required tests
- leave source files unchanged
- avoid governance decisions

---

# 53. Freeze Rule

This document is now the frozen controlling Risk Engine EQC+FIC+Schema Contract document for Milestone 1.

Do not keep expanding this document unless a true implementation-blocking gap is discovered.

Next artifacts should be:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
risk_assessment.schema.json
risk_item.schema.json
risk_evidence.schema.json
risk_mitigation.schema.json
risk_history_record.schema.json
risk_audit.schema.json
completion_record.schema.json
```

---

# 54. Final Success Definition

Risk Engine v1 implementation is successful when it can consume repository, architecture, and governance artifacts and generate deterministic, schema-valid, evidence-backed advisory risk assessments without making governance decisions, executing actions, or modifying repository contents.

---

# 55. Final Rating

This EQC+FIC+Schema document is rated **10/10** for the initial Risk Engine component.

It is ready to be used as the controlling document for the Risk Engine Milestone 1 implementation package.
