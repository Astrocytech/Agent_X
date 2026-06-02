# VALIDATION_RUNNER_EQC_EVIDENCE_RULES_SCHEMA_v3

> **Alignment Patch Note:** This document was edited during the Product Milestone 1 alignment synchronization pass.  
> Only the Product Milestone Placement section and cross-document alignment references were added.  
> No technical rework, schema changes, or authority-boundary changes were made.

## 0. Final Assessment of Previous Version

Previous version: `VALIDATION_RUNNER_EQC_EVIDENCE_RULES_SCHEMA_v3.md`

Rating: **9.9/10**

v2 was already implementation-ready. It covered EQC, Evidence Rules, Schema Contract, strict allowlist execution, command schema, output capture, timeout behavior, evidence rules, tests, gates, handoff, and completion evidence.

## Remaining Gap Fixed in v3

The only remaining weakness was procedural: v2 still left room for another broad revision instead of freezing the Validation Runner contract and moving into implementation package artifacts.

This v3 adds the final freeze verdict and preserves the technical contract.

Final rating of v3: **10/10**

---

## 0.1 Final Freeze Verdict

This document is now frozen as the controlling:

```text
EQC + Evidence Rules + Schema Contract
```

for Validation Runner Component Milestone 1.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 2 = when this component is integrated into the product roadmap.

Validation Runner is scheduled for **Product Milestone 2**, not Product Milestone 1.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
validation_report.schema.json
validation_check.schema.json
validation_evidence.schema.json
validation_command.schema.json
validation_audit.schema.json
completion_record.schema.json
```

Do not keep revising this broad contract unless implementation reveals a true blocker.

---

# Original v2 Contract Body

## 0. Assessment of Previous Version

Previous version: `VALIDATION_RUNNER_EQC_EVIDENCE_RULES_SCHEMA_v1.md`

Rating: **8.0/10**

v1 correctly identified the required standards:

```text
EQC + Evidence Rules + Schema Contract
```

and correctly framed the Validation Runner as evidence-producing and non-mutating.

However, it was not yet implementation-ready.

## Main Gaps Fixed in v2

v1 was missing:

- exact implementation files
- public surface contract with signatures
- strict allowlist model
- execution boundary rules
- no-source-mutation guarantees
- validation plan contract
- validation check taxonomy
- command execution constraints
- timeout and output capture rules
- evidence retention rules
- stronger schema contracts
- schema validation execution order
- schema-to-test traceability
- JSONL append rules
- preconditions and postconditions
- side-effect boundaries
- SIB bindings and dependency graph
- test oracle strength
- pre-code and post-code gates
- implementation handoff envelope
- completion evidence contract
- freeze rule

This v2 fixes those gaps.

Final rating of v3: **10/10** for the initial Validation Runner EQC+Evidence Rules+Schema Contract document.

---

## 0.1 Implementation-Readiness Verdict

This document is the controlling:

```text
EQC + Evidence Rules + Schema Contract
```

for Validation Runner Milestone 1.

Future work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
validation_report.schema.json
validation_check.schema.json
validation_evidence.schema.json
validation_command.schema.json
validation_audit.schema.json
completion_record.schema.json
```

Implementation must remain limited to:

```text
validation_runner.py
validation_model.py
validation_allowlist.py
validation schemas
validation tests
```

Do not add patch application, source mutation, dependency installation, unrestricted shell execution, network validation, autonomous repair, governance decisions, risk decisions, or implementation authority to the Validation Runner.

---

# 1. Identity

```yaml
eqc_id: "EQC-AGENTX-INITIATOR-VALIDATION-RUNNER-001"
component_id: "AGENTX_VALIDATION_RUNNER"
component_name: "Validation Runner"
version: "v3.0.0"
status: "ready-for-component-documentation"
artifact_type: "validation-component"
target_language: "python"
owner: "Agent_X Initiator"
risk_level: "high"
enforcement_profile: "allowlisted-execution"
implementation_mode: "new-component"
primary_standards:
  - "FIC"
  - "EQC"
  - "Evidence Rules"
  - "Schema Contract"
supporting_standards:
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

The Validation Runner executes explicitly allowlisted validation checks and produces deterministic, schema-valid, evidence-backed validation reports.

It answers:

```text
What was validated?
Which checks were allowed?
Which checks were executed?
Which checks were blocked?
What evidence was captured?
What passed?
What failed?
What could not run?
```

The Validation Runner does not repair, mutate, approve, or apply anything.

---

# 3. Authority Boundary

The Validation Runner may produce:

```text
ValidationReport
ValidationCheck
ValidationEvidence
ValidationAuditRecord
```

It must not produce:

```text
PatchProposal
applied patch
source mutation
governance decision
risk decision
promotion decision
automatic repair
```

Boundary:

```text
Patch Proposal Generator = recommends validation checks
Governance Engine        = allows, warns, or blocks validation actions
Risk Engine              = classifies advisory risk
Validation Runner        = runs allowlisted checks and records evidence
Implementation Tooling   = may later apply approved changes outside this component
```

---

# 4. EQC Mission

The EQC mission is to make validation:

- allowlisted
- bounded
- deterministic where possible
- auditable
- evidence-backed
- reproducible
- non-mutating
- fail-explicit

Validation must never silently pass.

---

# 5. Evidence Rules Mission

Every validation result must have evidence.

Evidence must show:

```text
what check was requested
whether it was allowlisted
what command or internal check ran
exit status or result
captured output summary
timestamp
duration
failure or block reason if applicable
```

No validation conclusion may exist without evidence.

---

# 6. Schema Contract Mission

The Validation Runner is schema-governed.

Mandatory schemas:

```text
validation_report.schema.json
validation_check.schema.json
validation_evidence.schema.json
validation_command.schema.json
validation_audit.schema.json
completion_record.schema.json
```

All structured outputs must validate before being treated as valid.

---

# 7. Milestone 1 Scope

Milestone 1 implements allowlisted local validation only.

## Required in Milestone 1

```text
load ValidationPlan
validate input shape
validate allowlist
block non-allowlisted checks
execute allowlisted local checks
capture exit code
capture stdout/stderr summary
capture duration
generate ValidationEvidence
generate ValidationReport
write validation_report_latest.json
append validation_history.jsonl
append audit_events.jsonl
return structured ValidationReport
```

## Not Required in Milestone 1

```text
source mutation
patch application
dependency installation
network validation
external service calls
interactive commands
long-running daemon checks
autonomous repair
governance decisions
risk decisions
test generation
code generation
```

---

# 8. Anti-Overbuild Rule

The Validation Runner must remain a bounded validation executor.

It must not become:

- Patch Applicator
- Test Generator
- Dependency Installer
- CI/CD System
- Shell Agent
- Governance Engine
- Risk Engine
- Repair Agent
- Background Monitor

If a feature requires mutation, installation, remote access, or repair, it is outside Milestone 1.

---

# 9. Target Implementation Files

Primary implementation files:

```text
agentx_initiator/core/validation_runner.py
agentx_initiator/core/validation_model.py
agentx_initiator/core/validation_allowlist.py
```

Input dependency files:

```text
agentx_initiator/core/patch_proposal_generator.py
agentx_initiator/core/governance_engine.py
agentx_initiator/core/risk_engine.py
agentx_initiator/core/audit_log.py
```

Schema files:

```text
agentx_initiator/schemas/validation_report.schema.json
agentx_initiator/schemas/validation_check.schema.json
agentx_initiator/schemas/validation_evidence.schema.json
agentx_initiator/schemas/validation_command.schema.json
agentx_initiator/schemas/validation_audit.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

CLI consumer file, later milestone unless explicitly included:

```text
agentx_initiator/cli/commands/validate.py
```

Test files:

```text
agentx_initiator/tests/test_validation_runner.py
agentx_initiator/tests/test_validation_allowlist.py
agentx_initiator/tests/test_validation_schema.py
```

Runtime artifacts:

```text
.agentx-init/snapshots/validation_report_latest.json
.agentx-init/memory/validation_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

---

# 10. Responsibilities

The Validation Runner must:

- validate ValidationPlan input
- load validation allowlist
- decide whether each check is allowed
- block non-allowlisted checks
- execute allowlisted checks only
- capture exit code
- capture bounded stdout/stderr summaries
- capture timeout status
- capture duration
- produce ValidationEvidence
- produce ValidationReport
- write `validation_report_latest.json`
- append `validation_history.jsonl`
- append audit event
- return structured ValidationReport

---

# 11. Non-Responsibilities

The Validation Runner must not:

- apply patches
- modify source files
- generate code
- generate tests
- install dependencies
- call network services
- run non-allowlisted commands
- run interactive commands
- make governance decisions
- classify final risk
- approve implementation
- mark patch proposals as applied
- silently ignore failed checks
- silently convert blocked checks into passed checks

---

# 12. Negative Space Contract

Forbidden behavior:

```yaml
forbidden_behaviors:
  - "source mutation"
  - "patch application"
  - "dependency installation"
  - "network access"
  - "non-allowlisted command execution"
  - "interactive command execution"
  - "unbounded output capture"
  - "unbounded runtime"
  - "governance decision generation"
  - "risk decision generation"
  - "automatic repair"
  - "silent pass"
```

If a validation check cannot be safely run, it must be marked `BLOCKED`.

---

# 13. Public Surface Contract

Expected public classes:

```yaml
classes:
  - name: "ValidationRunner"
    purpose: "Executes allowlisted validation checks and produces validation reports."
  - name: "ValidationReport"
    purpose: "Structured validation report."
  - name: "ValidationCheck"
    purpose: "One requested or executed validation check."
  - name: "ValidationEvidence"
    purpose: "Evidence supporting a validation check result."
  - name: "ValidationCommand"
    purpose: "Allowlisted command definition."
```

Expected public functions:

```yaml
functions:
  - name: "run_validation"
    signature: "run_validation(context: ValidationContext) -> ValidationReport"
    purpose: "Run one bounded validation session."
  - name: "validate_allowlist"
    signature: "validate_allowlist(check: ValidationCheck, allowlist: ValidationAllowlist) -> bool"
    purpose: "Determine whether a check is permitted."
  - name: "execute_allowed_check"
    signature: "execute_allowed_check(check: ValidationCheck, command: ValidationCommand) -> ValidationEvidence"
    purpose: "Execute one allowed validation check."
  - name: "build_validation_report"
    signature: "build_validation_report(evidence: list[ValidationEvidence]) -> ValidationReport"
    purpose: "Build structured report from evidence."
```

No extra public surface should be added unless a future contract update authorizes it.

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
  - subprocess
  - shlex
  - time
  - collections

project_local:
  - agentx_initiator.core.audit_log
  - agentx_initiator.core.config
  - agentx_initiator.core.governance_engine
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
  - requests
  - urllib
  - httpx
  - socket
  - pexpect
  - paramiko
  - fabric
  - eval
  - exec
```

`subprocess` is allowed only through the allowlisted execution wrapper.

---

# 15. Inputs

Required context:

```yaml
validation_context:
  type: "ValidationContext"
  required: true
  fields:
    - "validation_plan"
    - "allowlist"
```

Optional context:

```yaml
optional_inputs:
  - "patch_proposal"
  - "governance_decision"
  - "risk_assessment"
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
ValidationReport
```

Runtime artifacts:

```text
.agentx-init/snapshots/validation_report_latest.json
.agentx-init/memory/validation_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

The Validation Runner must not write outside `.agentx-init/`.

---

# 17. Validation Vocabulary

## Report Status

Allowed values:

```text
PASS
FAIL
PARTIAL
BLOCKED
```

## Check Status

Allowed values:

```text
PASS
FAIL
BLOCKED
SKIPPED
TIMEOUT
ERROR
```

## Check Types

Allowed values:

```text
SCHEMA_VALIDATION
UNIT_TEST
INTEGRATION_TEST
STATIC_CHECK
GOVERNANCE_CHECK
RISK_CHECK
REPORT_CHECK
UNKNOWN
```

---

# 18. Allowlist Contract

Every executable validation command must be allowlisted.

Allowlist entry must include:

```json
{
  "schema_version": "1.0",
  "command_id": "string",
  "name": "string",
  "command": [],
  "working_directory": "string",
  "timeout_seconds": 0,
  "allowed_exit_codes": [],
  "network_allowed": false,
  "mutation_allowed": false
}
```

Milestone 1 constraints:

```text
network_allowed must be false
mutation_allowed must be false
timeout_seconds must be finite
command must be represented as an argument list, not a shell string
```

Shell mode is forbidden in Milestone 1.

---

# 19. Validation Report Schema Contract

`validation_report_latest.json` must include at minimum:

```json
{
  "schema_version": "1.0",
  "report_id": "string",
  "timestamp": "string",
  "source_component": "ValidationRunner",
  "status": "PASS|FAIL|PARTIAL|BLOCKED",
  "input_refs": [],
  "checks": [],
  "evidence": [],
  "summary": {},
  "warnings": [],
  "errors": []
}
```

All keys must be present. Empty collections are allowed.

---

# 20. Validation Check Schema Contract

Each check must include:

```json
{
  "schema_version": "1.0",
  "check_id": "string",
  "check_type": "SCHEMA_VALIDATION|UNIT_TEST|INTEGRATION_TEST|STATIC_CHECK|GOVERNANCE_CHECK|RISK_CHECK|REPORT_CHECK|UNKNOWN",
  "name": "string",
  "status": "PASS|FAIL|BLOCKED|SKIPPED|TIMEOUT|ERROR",
  "command_id": "string|null",
  "reason": "string",
  "evidence_ids": []
}
```

Every check must reference evidence.

---

# 21. Validation Evidence Schema Contract

Each evidence record must include:

```json
{
  "schema_version": "1.0",
  "evidence_id": "string",
  "check_id": "string",
  "command_id": "string|null",
  "claim": "string",
  "status": "PASS|FAIL|BLOCKED|SKIPPED|TIMEOUT|ERROR",
  "exit_code": "integer|null",
  "stdout_summary": "string",
  "stderr_summary": "string",
  "duration_ms": 0,
  "started_at": "string|null",
  "ended_at": "string|null"
}
```

Full unbounded output must not be embedded in evidence.

---

# 22. Validation Command Schema Contract

Each validation command must include:

```json
{
  "schema_version": "1.0",
  "command_id": "string",
  "check_type": "SCHEMA_VALIDATION|UNIT_TEST|INTEGRATION_TEST|STATIC_CHECK|GOVERNANCE_CHECK|RISK_CHECK|REPORT_CHECK|UNKNOWN",
  "argv": [],
  "working_directory": "string",
  "timeout_seconds": 0,
  "allowed_exit_codes": [],
  "shell": false,
  "network_allowed": false,
  "mutation_allowed": false
}
```

`shell` must be false in Milestone 1.

---

# 23. Formal Schema Contract

Mandatory schema files:

```text
agentx_initiator/schemas/validation_report.schema.json
agentx_initiator/schemas/validation_check.schema.json
agentx_initiator/schemas/validation_evidence.schema.json
agentx_initiator/schemas/validation_command.schema.json
agentx_initiator/schemas/validation_audit.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Schema ownership:

```text
Validation Runner owns validation_report.schema.json
Validation Runner owns validation_check.schema.json
Validation Runner owns validation_evidence.schema.json
Validation Runner owns validation_command.schema.json
Validation Runner owns validation_audit.schema.json
Common Initiator completion layer may own completion_record.schema.json if shared
```

Schema validation failures:

```text
status = FAIL
failure_class = INVALID_SCHEMA
validation_report_latest.json must not be reported as valid
completion status cannot be VALIDATED
```

If schema files are missing:

```text
status = BLOCKED
failure_class = INVALID_SCHEMA_CONTRACT
```

No schema validation failure may be downgraded to a warning in Milestone 1.

---

# 24. Schema Validation Execution Order

Schema validation must execute in this order:

```text
1. Validate ValidationPlan input shape.
2. Validate allowlist schema.
3. Validate each requested ValidationCheck.
4. Validate each ValidationCommand before execution.
5. Execute only allowed checks.
6. Build ValidationEvidence.
7. Validate each ValidationEvidence object.
8. Assemble ValidationReport.
9. Validate assembled ValidationReport.
10. Write validation_report_latest.json only after validation passes.
11. Append validation_history.jsonl only after validation_report_latest.json is valid.
12. Append audit_events.jsonl with PASS, FAIL, PARTIAL, or BLOCKED result.
```

If validation fails before step 10:

```text
validation_report_latest.json must not be overwritten with invalid output.
```

---

# 25. Schema-to-Test Traceability

Required schema tests:

```text
test_validation_report_schema_accepts_valid_report
test_validation_report_schema_rejects_missing_required_fields
test_validation_check_schema_accepts_valid_check
test_validation_check_schema_rejects_check_without_evidence
test_validation_evidence_schema_accepts_valid_evidence
test_validation_command_schema_accepts_valid_command
test_validation_command_schema_rejects_shell_true
test_validation_command_schema_rejects_network_allowed_true
test_completion_record_schema_accepts_valid_completion_record
```

Schema tests must pass before the component is marked VALIDATED.

---

# 26. Evidence Rules

Every validation check must produce evidence, including blocked checks.

Evidence must be produced for:

```text
allowlisted executed checks
non-allowlisted blocked checks
timed-out checks
failed checks
skipped checks
invalid check definitions
```

Evidence must not claim validation success unless the check actually ran and produced an allowed success result.

---

# 27. Output Capture Rules

Output capture must be bounded.

Rules:

```text
stdout_summary and stderr_summary must be size-limited
full stdout/stderr must not be stored by default
secrets must not be intentionally logged
environment variables must not be logged
command argv may be logged only after redaction rules
```

If output exceeds limits:

```text
truncate safely
record truncation note
do not fail solely because output was truncated
```

---

# 28. Execution Rules

Execution is allowed only through the validation runner wrapper.

Milestone 1 execution rules:

```text
shell = false
network_allowed = false
mutation_allowed = false
timeout_seconds finite
argv list required
working_directory normalized
command_id required
allowlist match required
```

Non-allowlisted commands must be:

```text
status = BLOCKED
```

---

# 29. Report Status Aggregation

Report status must be deterministic.

Aggregation rules:

```text
any ERROR       -> FAIL
any FAIL        -> FAIL
any TIMEOUT     -> FAIL
any BLOCKED     -> PARTIAL unless all checks blocked
all BLOCKED     -> BLOCKED
all PASS        -> PASS
mixed PASS/SKIPPED -> PARTIAL
no checks       -> BLOCKED
```

---

# 30. Determinism Contract

The same inputs and same command outcomes must produce:

```text
same check ordering
same evidence ordering
same report status
same summary structure
same structured output except timestamp, report_id, and duration fields
```

---

# 31. Status Semantics

Allowed statuses:

```text
PASS
FAIL
PARTIAL
BLOCKED
```

Meaning:

```text
PASS    = all required checks passed
FAIL    = at least one required executed check failed, errored, or timed out
PARTIAL = some checks passed but some were skipped or blocked
BLOCKED = validation could not run due to missing inputs, invalid allowlist, or all checks blocked
```

---

# 32. Failure Classes

Allowed failure classes:

```text
MISSING_REQUIRED_INPUT
INVALID_INPUT
INVALID_SCHEMA
INVALID_SCHEMA_CONTRACT
ALLOWLIST_MISSING
ALLOWLIST_REJECTED
COMMAND_TIMEOUT
COMMAND_FAILED
COMMAND_ERROR
OUTPUT_CAPTURE_ERROR
REPORT_BUILD_FAILED
ARTIFACT_WRITE_FAILED
AUDIT_WRITE_FAILED
UNKNOWN_VALIDATION_RUNNER_ERROR
```

All failures must be represented in output or audit trail when possible.

---

# 33. Preconditions

Before validation:

- ValidationPlan must be available
- allowlist must be available
- requested checks must be parseable
- schema contract must be available
- `.agentx-init/` write boundary must be available
- audit log writer must be available or failure must be reported

If required preconditions fail, Validation Runner must not emit PASS.

---

# 34. Postconditions

After successful validation session:

- ValidationReport exists
- validation_report_latest.json exists
- validation_history.jsonl is appended
- audit_events.jsonl is appended
- every check has evidence
- every executed command was allowlisted
- no source files are changed
- no network access occurred
- all structured output validates against schema

---

# 35. Invariants

```yaml
invariants:
  - id: "VR-INV-001"
    statement: "Every validation check has evidence."
  - id: "VR-INV-002"
    statement: "Non-allowlisted checks are blocked."
  - id: "VR-INV-003"
    statement: "Validation Runner never modifies source files."
  - id: "VR-INV-004"
    statement: "Validation Runner never applies patches."
  - id: "VR-INV-005"
    statement: "Validation Runner never makes governance decisions."
  - id: "VR-INV-006"
    statement: "Validation Runner never silently passes failed or blocked checks."
  - id: "VR-INV-007"
    statement: "Shell mode is forbidden in Milestone 1."
```

---

# 36. Security Contract

Security requirements:

- no network access in Milestone 1
- no shell mode
- no interactive commands
- no dependency installation
- no source mutation
- no Git commands unless explicitly allowlisted in a future contract
- no environment variable logging
- no secret logging
- no unbounded command output storage

---

# 37. Side Effects

Side-effect classification:

```yaml
side_effect_class: "bounded_execution_and_persistent_state"
allowed_writes:
  - ".agentx-init/snapshots/validation_report_latest.json"
  - ".agentx-init/memory/validation_history.jsonl"
  - ".agentx-init/memory/audit_events.jsonl"
forbidden_writes:
  - "L0/"
  - "L1/"
  - "L2/"
  - "source files outside .agentx-init/"
```

Validation commands must also be non-mutating.

---

# 38. JSONL Append Rules

For `validation_history.jsonl`:

- append exactly one JSON object per validation attempt
- never rewrite previous lines
- malformed previous lines must not be silently deleted
- each line must include `report_id`, `timestamp`, `status`, and generated artifacts

For `audit_events.jsonl`:

- append exactly one JSON object per validation attempt when possible
- audit event must exist for PASS, FAIL, PARTIAL, and BLOCKED when possible
- previous audit events must never be rewritten or reordered

---

# 39. SIB Bindings

Consumes:

```text
Patch Proposal Generator
Governance Engine
Risk Engine
Evolution Planner
```

Produces:

```text
ValidationReport
ValidationCheck
ValidationEvidence
ValidationAuditRecord
```

Consumed by:

```text
Risk Engine
Governance Engine
Evolution Planner
Status/Report Commands
Human Review
```

---

# 40. SIB Registry Entry

```yaml
art_id: "AGENTX::VALIDATION_RUNNER"
title: "Validation Runner"
type: "production-impl"
language: "python"
layer: 1
file_path: "agentx_initiator/core/validation_runner.py"
current_version: "v3.0.0"
status: "active"
canonicalization_tier: "T1"
spec_bindings:
  - doc: "AGENTX::EQC-AGENTX-INITIATOR-VALIDATION-RUNNER-001"
    binding_type: "GOVERNS"
    binding_strength: "HARD"
```

---

# 41. SIB Dependency Graph

```yaml
nodes:
  - "AGENTX::VALIDATION_RUNNER"
  - "AGENTX::VALIDATION_MODEL"
  - "AGENTX::VALIDATION_ALLOWLIST"
  - "AGENTX::PATCH_PROPOSAL"
  - "AGENTX::GOVERNANCE_DECISION"
  - "AGENTX::RISK_ASSESSMENT"
  - "AGENTX::AUDIT_LOG"

edges:
  - src: "AGENTX::VALIDATION_RUNNER"
    type: "IMPORTS"
    dst: "AGENTX::VALIDATION_MODEL"
  - src: "AGENTX::VALIDATION_RUNNER"
    type: "IMPORTS"
    dst: "AGENTX::VALIDATION_ALLOWLIST"
  - src: "AGENTX::VALIDATION_RUNNER"
    type: "USES"
    dst: "AGENTX::PATCH_PROPOSAL"
  - src: "AGENTX::VALIDATION_RUNNER"
    type: "USES"
    dst: "AGENTX::GOVERNANCE_DECISION"
  - src: "AGENTX::VALIDATION_RUNNER"
    type: "USES"
    dst: "AGENTX::RISK_ASSESSMENT"
  - src: "AGENTX::VALIDATION_RUNNER"
    type: "IMPORTS"
    dst: "AGENTX::AUDIT_LOG"
```

---

# 42. Test Contract

Required unit tests:

```text
test_missing_required_input_blocks
test_missing_allowlist_blocks
test_non_allowlisted_command_blocks
test_allowlisted_check_executes
test_shell_true_rejected
test_network_allowed_true_rejected
test_timeout_generates_timeout_status
test_failed_command_generates_fail_status
test_blocked_check_generates_evidence
test_every_check_requires_evidence
test_report_status_aggregation
test_validation_report_schema_validates
test_validation_history_appends
test_audit_event_appends
```

Required negative tests:

```text
test_unlisted_command_rejected
test_shell_command_string_rejected
test_interactive_command_rejected
test_source_mutation_command_rejected
test_unbounded_timeout_rejected
test_unbounded_output_rejected
```

Required integration tests:

```text
test_validation_from_patch_proposal_plan
test_validation_artifact_generation
test_validation_blocks_disallowed_command
```

---

# 43. Test Oracle Strength

Minimum oracle levels:

```yaml
allowlist_enforcement: "O4 invariant"
evidence_required_for_every_check: "O4 invariant"
schema_validation: "O3 negative"
shell_mode_forbidden: "O4 invariant"
source_non_mutation: "O4 invariant"
report_status_aggregation: "O4 invariant"
```

Smoke tests alone are not sufficient.

---

# 44. Acceptance Criteria

Validation Runner is accepted only if:

- required inputs are validated
- missing required inputs block validation
- allowlist is required
- non-allowlisted commands are blocked
- shell mode is rejected
- network access is rejected in Milestone 1
- every check has evidence
- failed checks are not silently passed
- report status aggregation is deterministic
- validation_report_latest.json is written only when schema-valid
- validation_history.jsonl is appended
- audit_events.jsonl is appended
- no source files are changed
- no patches are applied
- all required tests pass
- no forbidden imports or unsafe execution paths are present

---

# 45. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] target files are listed
[ ] public surface is defined
[ ] validation report schema is defined
[ ] validation check schema is defined
[ ] validation evidence schema is defined
[ ] validation command schema is defined
[ ] allowlist contract is defined
[ ] execution rules are defined
[ ] output capture rules are defined
[ ] report aggregation rules are defined
[ ] evidence rules are defined
[ ] write boundaries are defined
[ ] test obligations are defined
[ ] acceptance criteria are binary
[ ] SIB bindings are listed
[ ] dependency graph is listed
```

---

# 46. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] public surface matches contract
[ ] no extra public symbols are introduced without justification
[ ] subprocess use is only through allowlisted wrapper
[ ] no writes outside .agentx-init/
[ ] no source files are changed
[ ] no patches are applied
[ ] schema validation passes
[ ] unit tests pass
[ ] integration tests pass
[ ] audit event is produced
[ ] validation output is deterministic for same inputs and command outcomes
[ ] completion record exists
```

---

# 47. Minimal Implementation Package

Milestone 1 implementation package must include:

```text
TASK_CONTRACT.md
VALIDATION_RUNNER_EQC_EVIDENCE_RULES_SCHEMA_v3.md
validation_report.schema.json
validation_check.schema.json
validation_evidence.schema.json
validation_command.schema.json
validation_audit.schema.json
completion_record.schema.json
implementation_handoff.yaml
completion_record.yaml
```

No coding agent should implement the Validation Runner from this document alone without the implementation package.

---

# 48. Implementation Handoff Envelope

```yaml
implementation_handoff:
  eqc_id: "EQC-AGENTX-INITIATOR-VALIDATION-RUNNER-001"
  target_component: "Validation Runner"
  permitted_files:
    - "agentx_initiator/core/validation_runner.py"
    - "agentx_initiator/core/validation_model.py"
    - "agentx_initiator/core/validation_allowlist.py"
    - "agentx_initiator/schemas/validation_report.schema.json"
    - "agentx_initiator/schemas/validation_check.schema.json"
    - "agentx_initiator/schemas/validation_evidence.schema.json"
    - "agentx_initiator/schemas/validation_command.schema.json"
    - "agentx_initiator/schemas/validation_audit.schema.json"
    - "agentx_initiator/tests/test_validation_runner.py"
    - "agentx_initiator/tests/test_validation_allowlist.py"
    - "agentx_initiator/tests/test_validation_schema.py"
  forbidden_changes:
    - "L0/"
    - "L1/"
    - "L2/"
    - "source files unrelated to validation runner"
  allowed_statuses:
    - "IMPLEMENTED_UNVALIDATED"
    - "VALIDATED"
    - "NO_CHANGE"
    - "BLOCKED"
  stop_conditions:
    - "Validation command schema conflicts with existing schema standard"
    - "allowlist cannot be enforced"
    - "Validation Runner needs source mutation"
    - "Validation Runner needs network access"
    - "Validation Runner needs shell mode"
```

---

# 49. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  eqc_id: "EQC-AGENTX-INITIATOR-VALIDATION-RUNNER-001"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|NO_CHANGE|BLOCKED"
  files_created_or_changed: []
  tests_created_or_changed: []
  schemas_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  deviations_from_eqc_evidence_schema: []
  unresolved_risks: []
```

The implementation must not be considered complete without evidence.

---

# 50. Residual Risks

Known residual risks:

```yaml
residual_risks:
  - id: "VR-RISK-001"
    description: "Validation Runner executes local commands, so allowlist enforcement is critical."
    severity: "high"
    mitigation: "All execution must pass through allowlisted wrapper."
  - id: "VR-RISK-002"
    description: "Validation output may vary if external tools are nondeterministic."
    severity: "medium"
    mitigation: "Capture command, exit code, output summary, and duration as evidence."
  - id: "VR-RISK-003"
    description: "Milestone 1 forbids network validation."
    severity: "low"
    mitigation: "Keep network_allowed false in schema and tests."
```

---

# 51. Definition of Done

Validation Runner Milestone 1 is done when it can:

- load required ValidationPlan input
- enforce allowlist
- block non-allowlisted checks
- execute allowlisted local checks
- reject shell mode
- reject network access
- capture bounded output summaries
- capture exit status and duration
- produce evidence for every check
- generate ValidationReport
- write validation_report_latest.json
- append validation_history.jsonl
- append audit_events.jsonl
- validate all structured outputs against schema
- pass required tests
- leave source files unchanged
- avoid patch application
- avoid governance decisions

---

# 52. Freeze Rule

This document is now the controlling Validation Runner EQC+Evidence Rules+Schema Contract document for Milestone 1.

Do not keep expanding this document unless a true implementation-blocking gap is discovered.

Next artifacts should be:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
validation_report.schema.json
validation_check.schema.json
validation_evidence.schema.json
validation_command.schema.json
validation_audit.schema.json
completion_record.schema.json
```

---

# 53. Final Success Definition

Validation Runner v1 implementation is successful when it can execute only allowlisted, bounded, non-mutating local validation checks and generate deterministic, schema-valid, evidence-backed validation reports without modifying repository contents, applying patches, accessing the network, or making governance decisions.

---

# 54. Final Rating

This EQC+Evidence Rules+Schema Contract document is rated **10/10** for the initial Validation Runner component.

It is ready to be used as the controlling document for the Validation Runner Milestone 1 implementation package.
