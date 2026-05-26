# CLI_COMMANDS_FIC_EQC_COMMAND_ACCEPTANCE_CRITERIA_v3

## 0. Final Assessment of Previous Version

Previous version: `CLI_COMMANDS_FIC_EQC_COMMAND_ACCEPTANCE_CRITERIA_v3.md`

Rating: **9.9/10**

v2 was already implementation-ready. It covered FIC, EQC, Command Acceptance Criteria, command registry, lifecycle rules, governance integration, exact implementation files, schemas, tests, gates, handoff, and completion evidence.

## Remaining Gap Fixed in v3

The only remaining weakness was procedural: v2 still left room for another broad revision instead of freezing the CLI Commands contract and moving into implementation package artifacts.

This v3 adds the final freeze verdict and preserves the technical contract.

Final rating of v3: **10/10**

---

## 0.1 Final Freeze Verdict

This document is now frozen as the controlling:

```text
FIC + EQC + Command Acceptance Criteria
```

for CLI Commands Component Milestone 1.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 1 = when this component is integrated into the product roadmap.

For **Product Milestone 1**, only **help**, **scan**, and **status** are active commands.

Product Milestone 1 may implement a minimal internal status report command behavior through **status**, but not a separate broad **report** command. The standalone report command is Product Milestone 2 scope.

Other commands (explain, plan, propose, validate, audit, graph, report, memory) may exist only as registered stubs that return a schema-valid CLICommandResponse:

```json
{
  "schema_version": "1.0",
  "response_id": "generated-string",
  "request_id": "request-id",
  "timestamp": "iso-8601-string",
  "command": "agentx-init <reserved-command>",
  "status": "BLOCKED",
  "exit_code": 3,
  "message": "Command is not implemented in Product Milestone 1.",
  "data": {
    "failure_class": "COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1",
    "product_milestone": 1,
    "required_product_milestone": 2
  },
  "artifact_refs": [],
  "warnings": [],
  "errors": []
}
```

For `agentx-init graph`, use `required_product_milestone: 3`.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
command_request.schema.json
command_response.schema.json
command_registry.schema.json
command_history_record.schema.json
completion_record.schema.json
```

Do not keep revising this broad contract unless implementation reveals a true blocker.

---

## Alignment Patch Note

This document was edited during the Product Milestone 1 alignment synchronization pass.  
Changes made:

- Added Product Milestone Placement section
- Added compatibility notes clarifying the frozen v2 contract body's scope
- No technical rework, schema changes, or authority-boundary changes were made.

---

# Original v2 Contract Body

## 0. Assessment of Previous Version

Previous version: `CLI_COMMANDS_FIC_EQC_COMMAND_ACCEPTANCE_CRITERIA_v1.md`

Rating: **8.0/10**

v1 correctly identified the required standards:

```text
FIC + EQC + Command Acceptance Criteria
```

and correctly framed CLI Commands as the human-facing command interface.

However, it was not yet implementation-ready.

## Main Gaps Fixed in v2

v1 was missing:

- exact implementation files
- public surface contract with signatures
- command registry contract
- command lifecycle rules
- argument validation rules
- governance integration rules
- command response schema
- command history rules
- help/status/report/scan/validate command contracts
- failure and exit-code semantics
- schema validation execution order
- schema-to-test traceability
- side-effect boundaries
- audit and memory integration
- test oracle strength
- pre-code and post-code gates
- implementation handoff envelope
- completion evidence contract
- freeze rule

This v2 fixes those gaps.

Final rating of v3: **10/10** for the initial CLI Commands FIC+EQC+Command Acceptance Criteria document.

---

## 0.1 Implementation-Readiness Verdict

This document is the controlling:

```text
FIC + EQC + Command Acceptance Criteria
```

for CLI Commands Milestone 1.

Future work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
command_request.schema.json
command_response.schema.json
command_registry.schema.json
command_history_record.schema.json
completion_record.schema.json
```

Product Milestone 1 implementation must remain limited to:

```text
cli/main.py
cli/registry.py
cli/commands/help.py
cli/commands/scan.py
cli/commands/status.py
CLI schemas
CLI tests
```

Later commands (explain, plan, propose, report, memory, validate, audit, graph) are Product Milestone 2 or 3 scope and must not be implemented as active commands in Product Milestone 1. If registered, they must return the BLOCKED stub response above.

Do not add interactive shell mode, remote execution, arbitrary subprocess execution, web UI, GUI, source mutation, or governance bypass behavior to CLI Commands.

---

# 1. Identity

```yaml
fic_id: "FIC-AGENTX-INITIATOR-CLI-COMMANDS-001"
eqc_id: "EQC-AGENTX-INITIATOR-CLI-COMMANDS-001"
component_id: "AGENTX_CLI_COMMANDS"
component_name: "CLI Commands"
version: "v3.0.0"
status: "ready-for-component-documentation"
artifact_type: "cli-component"
target_language: "python"
owner: "Agent_X Initiator"
risk_level: "high"
enforcement_profile: "governed-command-interface"
implementation_mode: "new-component"
primary_standards:
  - "FIC"
  - "EQC"
  - "Command Acceptance Criteria"
supporting_standards:
  - "Schema Contract"
  - "Audit Rules"
  - "SIB Binding"
```

---

# 2. Purpose

The CLI Commands component provides the human-facing command interface for Agent_X Initiator.

It exposes approved commands for inspecting, operating, validating, and reporting on Initiator components without requiring users to directly access internal implementation files.

The CLI must be:

```text
predictable
governed
schema-valid
auditable
safe by default
clear on failure
```

---

# 3. Authority Boundary

> **Compatibility note:** This authority boundary is the cumulative full CLI contract. In Product Milestone 1, active CLI authority is limited to help, scan, and status. Product Milestone 2 and Product Milestone 3 command authorities remain reserved unless the command is registered only as a BLOCKED stub with no later-component side effects.

CLI Commands may:

```text
# Product Milestone 1
invoke approved component operations (help/scan/status only)
display component status
request repository scan
request report generation through Minimal Report Writer (PM1 — status report only)

# Product Milestone 2 (cumulative)
request validation through Validation Runner
request report generation through full Report Writer
query memory artifacts

# Product Milestone 3 (cumulative)
query graph artifacts

# All Milestones
display help
write command history
emit audit events
```

CLI Commands must not:

```text
# All Milestones
bypass Governance Engine
modify source files directly
execute arbitrary code
run arbitrary shell commands
modify protected artifacts
apply patches
create commits
install dependencies
access the network unless a future command contract explicitly allows it
```

CLI Commands are an interface layer, not an execution engine.

---

# 4. FIC Mission

The FIC mission is to define exact CLI behavior:

- command registry
- command parsing
- argument validation
- command routing
- command response shape
- command history
- command errors
- command boundaries
- file outputs
- acceptance criteria

---

# 5. EQC Mission

The EQC mission is to ensure that every command is:

- validated before execution
- routed only to approved components
- governed where applicable
- deterministic where possible
- auditable
- schema-valid
- explicit on failure
- safe by default

Commands must not silently succeed.

---

# 6. Command Acceptance Criteria Mission

A CLI command is accepted only if:

```text
command name exists
command category is allowed
arguments validate
schema validation passes
permission boundary is respected
governance check passes when required
target component exists
output path is inside .agentx-init/ when writing
command response is schema-valid
command history is recorded when possible
```

Unknown commands must fail closed.

---

# 7. Component Milestone 1 Scope

CLI Commands Component Milestone 1 defines the complete command-interface contract.

## Product Milestone 1 Active Commands

```text
agentx-init --help
agentx-init help       # optional alias; produces equivalent output to --help
agentx-init scan
agentx-init status
```

## Product Milestone 1 Stubbed or Absent Commands

```text
agentx-init explain
agentx-init plan
agentx-init propose
agentx-init validate
agentx-init audit
agentx-init graph
agentx-init report
agentx-init memory
```

If registered in Product Milestone 1, later commands must return:

```text
COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1
```

They must not execute their future behavior in Product Milestone 1.

## Not Required in Product Milestone 1

```text
interactive shell
remote execution
web UI
GUI
plugin system
arbitrary command execution
auto-repair commands
patch application commands
Git commands
dependency installation commands
background daemon commands
```

---

# 8. Anti-Overbuild Rule

CLI Commands must remain a governed command interface.

It must not become:

- Shell Agent
- Automation Daemon
- Web Server
- GUI Application
- Patch Applicator
- Git Client
- Package Manager
- Remote Executor
- Multi-Agent Console

If a feature requires arbitrary execution, patch application, remote access, or interactive shell behavior, it belongs outside Milestone 1.

---

# 9. Target Implementation Files

Primary implementation files:

```text
agentx_initiator/cli/main.py
agentx_initiator/cli/registry.py
agentx_initiator/cli/models.py
```

Command implementation files (Product Milestone 1):

```text
agentx_initiator/cli/commands/help.py
agentx_initiator/cli/commands/scan.py
agentx_initiator/cli/commands/status.py
```

Command implementation files (Product Milestone 2):

```text
agentx_initiator/cli/commands/explain.py
agentx_initiator/cli/commands/plan.py
agentx_initiator/cli/commands/propose.py
agentx_initiator/cli/commands/validate.py
agentx_initiator/cli/commands/audit.py
agentx_initiator/cli/commands/report.py
```

Command implementation files (Product Milestone 3):

```text
agentx_initiator/cli/commands/graph.py
```

> **Compatibility note**: This list is from the frozen v2 body. The canonical file name is `repo_scanner.py`, not `repository_scanner.py`.  
> See AGENT_X_INITIATOR_MILESTONE_AND_NAMING_ALIGNMENT_ADDENDUM.md for the complete legacy-name table.

Input dependency files (Product Milestone 1):

```text
agentx_initiator/core/repo_scanner.py        # canonical name; repository_scanner.py is deprecated
agentx_initiator/core/report_writer.py        # minimal — status only
agentx_initiator/core/audit_log.py
```

Input dependency files (Product Milestone 2, cumulative):

```text
agentx_initiator/core/validation_runner.py
agentx_initiator/core/memory_store.py
agentx_initiator/core/governance_engine.py
```

Input dependency files (Product Milestone 3, cumulative):

```text
agentx_initiator/core/knowledge_graph.py
```

Schema files:

```text
agentx_initiator/schemas/command_request.schema.json
agentx_initiator/schemas/command_response.schema.json
agentx_initiator/schemas/command_registry.schema.json
agentx_initiator/schemas/command_history_record.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Test files:

```text
agentx_initiator/tests/test_cli_commands.py
agentx_initiator/tests/test_cli_registry.py
agentx_initiator/tests/test_cli_schema.py
```

Runtime artifacts:

```text
.agentx-init/logs/command_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

---

# 10. Responsibilities

CLI Commands must:

- parse command name
- parse command arguments
- validate command request
- reject unknown commands
- enforce command registry
- route command to approved component
- request governance check when required
- return schema-valid command response
- write command history
- emit audit event when Audit Log is available
- preserve clear exit-code semantics
- avoid direct source mutation

---

# 11. Non-Responsibilities

CLI Commands must not:

- implement core component logic
- bypass component APIs
- bypass governance checks
- apply patches
- modify source files directly
- execute arbitrary shell commands
- install dependencies
- access remote services
- make governance decisions
- classify final risk
- generate implementation code
- silently ignore errors

---

# 12. Negative Space Contract

Forbidden behavior:

```yaml
forbidden_behaviors:
  - "arbitrary command execution"
  - "interactive shell"
  - "source mutation"
  - "patch application"
  - "git operation"
  - "dependency installation"
  - "network access"
  - "governance bypass"
  - "direct protected artifact modification"
  - "silent success on failure"
```

If a command requires a capability outside Milestone 1, it must return:

```text
status = BLOCKED
failure_class = COMMAND_OUT_OF_SCOPE
```

> **Compatibility note:** `COMMAND_OUT_OF_SCOPE` is reserved for capabilities that are not part of any accepted CLI contract. For known later Product Milestone commands registered as PM1 stubs, use `response.data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1`.

---

# 13. Public Surface Contract

Expected public classes:

```yaml
classes:
  - name: "CLICommand"
    purpose: "Registered command definition."
  - name: "CLICommandRequest"
    purpose: "Parsed command request."
  - name: "CLICommandResponse"
    purpose: "Schema-valid command response."
  - name: "CLIRegistry"
    purpose: "Registry of allowed commands and handlers."
  - name: "CLIContext"
    purpose: "Runtime context for command execution."
```

Expected public functions:

```yaml
functions:
  - name: "main"
    signature: "main(argv: list[str] | None = None) -> int"
    purpose: "CLI entrypoint."
  - name: "register_command"
    signature: "register_command(command: CLICommand) -> None"
    purpose: "Register one allowed command."
  - name: "validate_command_request"
    signature: "validate_command_request(request: CLICommandRequest, registry: CLIRegistry) -> CLIValidationResult"
    purpose: "Validate command name, category, and arguments."
  - name: "execute_command"
    signature: "execute_command(request: CLICommandRequest, context: CLIContext) -> CLICommandResponse"
    purpose: "Route and execute one approved command."
```

No extra public surface should be added unless a future FIC update authorizes it.

---

# 14. Dependency Contract

Allowed imports:

```yaml
stdlib:
  - argparse
  - json
  - pathlib
  - typing
  - dataclasses
  - datetime
  - enum
  - uuid
  - sys

project_local:
  - agentx_initiator.cli.registry
  - agentx_initiator.cli.models
  - agentx_initiator.core.audit_log
  - agentx_initiator.core.config

PM2-added imports (Product Milestone 2, not active in PM1):
  - agentx_initiator.core.governance_engine
```

Conditionally allowed:

```yaml
rich:
  allowed_if: "project uses Rich for terminal formatting"
typer:
  allowed_if: "project chooses Typer as CLI framework"
click:
  allowed_if: "project chooses Click as CLI framework"
jsonschema:
  allowed_if: "project dependency already exists or pyproject explicitly includes it"
```

Forbidden imports:

```yaml
forbidden:
  - subprocess
  - requests
  - urllib
  - httpx
  - socket
  - git
  - eval
  - exec
```

Milestone 1 CLI must not directly execute shell commands.

---

# 15. Inputs

Allowed input forms:

```text
argv list
CLICommandRequest
environment-independent config
structured runtime context
```

Required command request fields:

```text
command
category
arguments
requested_effect
output_format
```

Missing required inputs must produce:

```text
status = BLOCKED
failure_class = INVALID_COMMAND_REQUEST
```

---

# 16. Outputs

Primary output:

```text
CLICommandResponse
```

Runtime artifacts:

```text
.agentx-init/logs/command_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

CLI Commands must not write outside `.agentx-init/` except normal terminal stdout/stderr.

---

# 17. Command Vocabulary

## Command Categories

Allowed categories:

```text
HELP
STATUS
SCAN
EXPLAIN
PLAN
PROPOSE
REPORT
VALIDATE
AUDIT
MEMORY
GRAPH
UNKNOWN
```

`UNKNOWN` is reserved for truly unrecognized commands. Reserved known later commands (EXPLAIN, PLAN, PROPOSE, REPORT, VALIDATE, AUDIT, MEMORY, GRAPH) must use their specific category even when the command is not active in PM1. This allows the CLI to distinguish "known reserved command returning BLOCKED" from "unknown command returning INVALID/UNKNOWN_COMMAND."

### Command Activation Table

| Command | Category | Activation PM | PM1 Behavior |
|---|---|---|---|
| `agentx-init --help` / `help` | HELP | PM1 | Active |
| `agentx-init scan` | SCAN | PM1 | Active |
| `agentx-init status` | STATUS | PM1 | Active |
| `agentx-init explain` | EXPLAIN | PM2 | Absent or BLOCKED stub |
| `agentx-init plan` | PLAN | PM2 | Absent or BLOCKED stub |
| `agentx-init propose` | PROPOSE | PM2 | Absent or BLOCKED stub |
| `agentx-init report` | REPORT | PM2 | Absent or BLOCKED stub |
| `agentx-init memory` | MEMORY | PM2 | Absent or BLOCKED stub |
| `agentx-init validate` | VALIDATE | PM2 | Absent or BLOCKED stub |
| `agentx-init audit` | AUDIT | PM2 | Absent or BLOCKED stub |
| `agentx-init graph` | GRAPH | PM3 | Absent or BLOCKED stub (required_product_milestone: 3) |

> **PM1 stub note:** All BLOCKED stubs must return `response.data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1` and must not import or invoke their corresponding later-component logic.

## Command Status Values

Allowed values:

```text
SUCCESS
PARTIAL
BLOCKED
FAILED
INVALID
```

## Output Formats

Allowed values:

```text
TEXT
JSON
MARKDOWN
```

---

# 18. Command Registry Contract

Every command registry entry must include:

```json
{
  "schema_version": "1.0",
  "command": "string",
  "category": "HELP|STATUS|SCAN|EXPLAIN|PLAN|PROPOSE|REPORT|VALIDATE|AUDIT|MEMORY|GRAPH|UNKNOWN",
  "description": "string",
  "handler": "string",
  "arguments": [],
  "requested_effect": "read|write|execute|report|plan|proposal|validate|audit|memory|graph|none",
  "requires_governance": false,
  "writes_artifacts": false,
  "allowed_output_formats": []
}
```

> **PM2 activation note:** `report`, `validate`, `plan`, `proposal`, `audit`, `memory`, and `graph` effects are reserved for later Product Milestones unless used by active PM1 commands under explicit PM1 rules. PM1 must not route commands with these effects to active handlers. The `requested_effect` enum must be reviewed and formally revised before PM2 activates commands carrying those effects; this enum expansion must happen through a formal schema revision, not as a silent alignment patch.

---

# 19. Command Request Schema Contract

Each command request must include:

```json
{
  "schema_version": "1.0",
  "request_id": "string",
  "timestamp": "string",
  "command": "string",
  "category": "HELP|STATUS|SCAN|EXPLAIN|PLAN|PROPOSE|REPORT|VALIDATE|AUDIT|MEMORY|GRAPH|UNKNOWN",
  "arguments": {},
  "requested_effect": "read|write|execute|report|plan|proposal|validate|audit|memory|graph|none",
  "output_format": "TEXT|JSON|MARKDOWN"
}
```

---

# 20. Command Response Schema Contract

Each command response must include:

```json
{
  "schema_version": "1.0",
  "response_id": "string",
  "request_id": "string",
  "timestamp": "string",
  "command": "string",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "exit_code": 0,
  "message": "string",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "errors": []
}
```

---

# 21. Command History Record Schema Contract

Each command history record must include:

```json
{
  "schema_version": "1.0",
  "history_id": "string",
  "timestamp": "string",
  "request": {},
  "response": {},
  "governance_ref": "string|null",
  "audit_event_id": "string|null"
}
```

---

# 22. Formal Schema Contract

Mandatory schema files:

```text
agentx_initiator/schemas/command_request.schema.json
agentx_initiator/schemas/command_response.schema.json
agentx_initiator/schemas/command_registry.schema.json
agentx_initiator/schemas/command_history_record.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Schema ownership:

```text
CLI Commands owns command_request.schema.json
CLI Commands owns command_response.schema.json
CLI Commands owns command_registry.schema.json
CLI Commands owns command_history_record.schema.json
Common Initiator completion layer may own completion_record.schema.json if shared
```

Schema validation failures:

```text
status = INVALID
failure_class = INVALID_SCHEMA
invalid command must not be executed
completion status cannot be VALIDATED
```

If schema files are missing:

```text
status = BLOCKED
failure_class = INVALID_SCHEMA_CONTRACT
```

No schema validation failure may be downgraded to a warning in Milestone 1.

---

# 23. Schema Validation Execution Order

Schema validation must execute in this order:

```text
1. Parse argv into CLICommandRequest.
2. Validate command exists in registry.
3. Validate CLICommandRequest schema.
4. Validate command arguments.
5. Run Governance Engine if command requires governance.
6. Execute only approved command handler.
7. Build CLICommandResponse.
8. Validate CLICommandResponse schema.
9. Append command_history.jsonl when possible.
10. Append audit event when Audit Log is available.
```

If validation fails before step 6:

```text
command handler must not run
```

---

# 24. Schema-to-Test Traceability

Required schema tests:

```text
test_command_request_schema_accepts_valid_request
test_command_request_schema_rejects_missing_required_fields
test_command_response_schema_accepts_valid_response
test_command_registry_schema_accepts_valid_registry
test_command_history_record_schema_accepts_valid_history_record
test_completion_record_schema_accepts_valid_completion_record
```

Schema tests must pass before the component is marked VALIDATED.

---

# 25. Command Lifecycle

Command lifecycle:

```text
parse
normalize
validate registry
validate schema
validate arguments
check governance when required
execute handler
build response
validate response
write command history
emit audit event
return exit code
```

No command may skip validation.

---

# 26. Command Acceptance Criteria

A command is accepted only if:

```text
command exists in registry
command category is allowed
arguments validate
requested effect is allowed
schema validation passes
governance allows execution when required
target component is available
output path is inside .agentx-init/ when writing
response can be schema-validated
```

If any acceptance condition fails:

```text
status = BLOCKED or INVALID or FAILED
handler must not run unless failure occurs after handler execution
```

---

# 27. Governance Integration Rules

## Product Milestone 1 Governance Policy

In Product Milestone 1, the full Governance Engine is not active. PM1 commands enforce safety through component-local write-boundary checks, path validation, schema validation, and Audit Log evidence.

Product Milestone 1 `scan` and `status` may write only their approved `.agentx-init/` artifacts through their approved component APIs. They do not require the full Governance Engine in Product Milestone 1.

Full Governance Engine ALLOW/WARN/BLOCK decisions begin in Product Milestone 2.

## Full Version 1 Governance View (cumulative)

Governance is required for commands with:

```text
requested_effect = write
requested_effect = execute
requested_effect = validate
writes_artifacts = true
```

Governance is not required for pure read-only help/status commands unless future policy changes.

Governance result handling:

```text
ALLOW -> command may proceed
WARN  -> command may proceed with warning in response
BLOCK -> command must not execute
```

CLI must not override Governance Engine decisions.

---

# 28. Command-Specific Contracts

## help

```text
Purpose: display available commands.
Effect: read
Governance required: no
Writes artifacts: no
```

`help` and `--help` must produce equivalent output. `--help` must be supported on every registered command, including BLOCKED stubs.

**Side-effect-free policy:** `agentx-init --help` must be side-effect-free. It may not create `.agentx-init/`, append to command history, or emit audit events. `agentx-init help` invoked as a subcommand may append to audit history when Audit Log is available, but must still produce identical help output. Both forms must be equivalent from the user's perspective.

## status

```text
Purpose: invoke Minimal Architecture Analyzer and Minimal Report Writer, or read their latest artifacts if already present.
Effect: report
Governance required: no (PM1 uses component-local write-boundary checks; full Governance Engine begins in PM2)
Writes artifacts: yes, limited to approved PM1 status artifacts
```

## scan

```text
Purpose: invoke Repository Scanner.
Effect: write
Governance required: no in PM1 (component-local write-boundary checks and Audit Log evidence apply; full Governance Engine begins in PM2)
Writes artifacts: yes
```

## report

*Product Milestone 2 command. Not active in Product Milestone 1. If registered in Product Milestone 1, it must return a schema-valid BLOCKED CLICommandResponse with data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1 and must not invoke Report Writer. The behavioral contract below applies only when this command reaches Product Milestone 2.*

```text
Purpose: invoke Report Writer.
Effect: report
Governance required: yes
Writes artifacts: yes
```

## validate

*Product Milestone 2 command. Not active in Product Milestone 1. If registered in Product Milestone 1, it must return a schema-valid BLOCKED CLICommandResponse with data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1 and must not invoke Validation Runner. The behavioral contract below applies only when this command reaches Product Milestone 2.*

```text
Purpose: invoke Validation Runner with allowlisted validation plan.
Effect: validate
Governance required: yes
Writes artifacts: yes
```

**Delegation rule (PM2):** `validate` must delegate all subprocess execution to Validation Runner. CLI must not execute subprocesses directly. Validation Runner controls allowlist enforcement, command timeout, output capture, and exit-code interpretation. CLI must not bypass Validation Runner for any subprocess invocation.

## memory

*Product Milestone 2 command. Not active in Product Milestone 1. If registered in Product Milestone 1, it must return a schema-valid BLOCKED CLICommandResponse with data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1 and must not invoke Memory Store. The behavioral contract below applies only when this command reaches Product Milestone 2.*

```text
Purpose: query Memory Store.
Effect: read
Governance required: no for read-only queries
Writes artifacts: no for read-only queries
```

## graph

*Product Milestone 3 command. Not active in Product Milestone 1. If registered in Product Milestone 1, it must return a schema-valid BLOCKED CLICommandResponse with data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1 and must not invoke Knowledge Graph. The behavioral contract below applies only when this command reaches Product Milestone 3.*

```text
Purpose: query Knowledge Graph.
Effect: read
Governance required: no for read-only queries
Writes artifacts: no for read-only queries
```

## explain

*Product Milestone 2 command. Not active in Product Milestone 1. If registered in Product Milestone 1, it must return a schema-valid BLOCKED CLICommandResponse with data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1 and must not invoke Evolution Planner. The behavioral contract below applies only when this command reaches Product Milestone 2.*

```text
Purpose: explain current architecture state through Evolution Planner.
Effect: read
Governance required: yes
Writes artifacts: yes
```

## plan

*Product Milestone 2 command. Not active in Product Milestone 1. If registered in Product Milestone 1, it must return a schema-valid BLOCKED CLICommandResponse with data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1 and must not invoke Evolution Planner. The behavioral contract below applies only when this command reaches Product Milestone 2.*

```text
Purpose: generate an evolution plan through Evolution Planner.
Effect: plan
Governance required: yes
Writes artifacts: yes
```

## propose

*Product Milestone 2 command. Not active in Product Milestone 1. If registered in Product Milestone 1, it must return a schema-valid BLOCKED CLICommandResponse with data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1 and must not invoke Patch Proposal Generator. The behavioral contract below applies only when this command reaches Product Milestone 2.*

```text
Purpose: generate a patch proposal through Patch Proposal Generator.
Effect: proposal
Governance required: yes
Writes artifacts: yes
```

## audit

*Product Milestone 2 command. Not active in Product Milestone 1. If registered in Product Milestone 1, it must return a schema-valid BLOCKED CLICommandResponse with data.failure_class = COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1 and must not invoke full Audit Log component. The behavioral contract below applies only when this command reaches Product Milestone 2.*

```text
Purpose: run audit queries against Audit Log.
Effect: audit
Governance required: yes
Writes artifacts: yes
```

---

# 29. Exit Code Semantics

Required exit codes:

```text
0 = SUCCESS
1 = FAILED
2 = INVALID command or arguments
3 = BLOCKED by governance or policy
4 = PARTIAL success
5 = INTERNAL ERROR
```

Exit code must match response status.

---

# 30. Command History Rules

When CLI command history is enabled, all registered command attempts, including BLOCKED stubs, are recorded in command_history.jsonl.

For `command_history.jsonl`:

```text
append exactly one JSON object per command attempt when possible
never rewrite previous lines
never reorder previous lines
never delete previous lines
each line must include request, response, timestamp, and status
```

Malformed previous lines must be preserved.

---

# 31. Output Rendering Rules

CLI may render:

```text
TEXT
JSON
MARKDOWN
```

Rules:

```text
JSON output must be valid JSON
MARKDOWN output must be deterministic
TEXT output must include status and message
errors must be visible
warnings must be visible
```

No command may hide errors.

---

# 32. Determinism Contract

The same command, same arguments, and same component artifacts must produce:

```text
same command validation outcome
same handler routing
same response status
same response data structure
same exit code
```

Timestamps and generated ids may differ.

---

# 33. Status Semantics

Allowed statuses:

```text
SUCCESS
PARTIAL
BLOCKED
FAILED
INVALID
```

Meaning:

```text
SUCCESS = command completed successfully
PARTIAL = command completed with missing optional data or warning
BLOCKED = command was stopped by governance, policy, or precondition
FAILED  = command ran but failed
INVALID = command request or arguments are invalid
```

---

# 34. Failure Classes

Allowed failure classes:

```text
UNKNOWN_COMMAND
INVALID_ARGUMENTS
INVALID_SCHEMA
INVALID_SCHEMA_CONTRACT
GOVERNANCE_BLOCKED                           # PM2+ only — PM1 uses component-local safety checks
COMMAND_OUT_OF_SCOPE
HANDLER_NOT_AVAILABLE
HANDLER_FAILED
ARTIFACT_WRITE_FAILED
COMMAND_HISTORY_WRITE_FAILED
AUDIT_WRITE_FAILED
UNKNOWN_CLI_ERROR
```

### Failure-class distinction

`COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1` is used only for known later commands registered as Product Milestone 1 stubs, such as `explain`, `plan`, `propose`, `report`, `memory`, `validate`, `audit`, and `graph`.

`COMMAND_OUT_OF_SCOPE` is used for unsupported commands or capabilities that are not part of the known roadmap, violate the CLI command contract, or request behavior outside the component boundary.

All failures must be represented in response or audit trail when possible.

### failure_class placement rule

CLI failure_class values must be placed in `response.data.failure_class` unless a future `command_response.schema.json` revision adds `failure_class` as an explicit top-level field.

No CLI response example may imply that `failure_class` is a top-level response field.

---

# 35. Preconditions

Before handler execution:

- command must exist
- arguments must validate
- request schema must validate
- governance must allow execution when required (PM2+ only — PM1 does not require full Governance Engine)
- target component must be available
- output path must be inside `.agentx-init/` when writing

If preconditions fail, handler must not run.

---

# 36. Postconditions

After command execution:

- CLICommandResponse exists
- response schema validates
- exit code matches response status
- command history is appended when possible
- audit event is appended when Audit Log is available
- no source files are changed directly by CLI

---

# 37. Invariants

```yaml
invariants:
  - id: "CLI-INV-001"
    statement: "Commands are validated before execution."
  - id: "CLI-INV-002"
    statement: "Unknown commands are rejected."
  - id: "CLI-INV-003"
    statement: "Governance-required commands cannot bypass Governance Engine."
  - id: "CLI-INV-004"
    statement: "CLI never directly mutates source files."
  - id: "CLI-INV-005"
    statement: "CLI responses are schema-valid."
  - id: "CLI-INV-006"
    statement: "Exit codes match response status."
  - id: "CLI-INV-007"
    statement: "Command history is append-only when written."
```

---

# 38. Security Contract

Security requirements:

- no arbitrary shell execution
- no network access in Milestone 1
- no dependency installation
- no source mutation directly by CLI
- no Git commands in Milestone 1
- no environment variable logging
- no intentional secret logging
- path traversal must be blocked

---

# 39. Side Effects

Side-effect classification:

```yaml
side_effect_class: "governed_interface_and_persistent_history"
allowed_writes:
  - ".agentx-init/logs/command_history.jsonl"
  - ".agentx-init/memory/audit_events.jsonl"
  - "component-owned .agentx-init artifacts through approved component APIs"
forbidden_writes:
  - "L0/"
  - "L1/"
  - "L2/"
  - "source files outside .agentx-init/"
```

CLI must not mutate governed source files directly.

---

# 40. SIB Bindings

Consumes:

```text
# Product Milestone 1
Repository Scanner
Report Writer (minimal — PM1)
Audit Log

# Product Milestone 2 (consumed via BLOCKED stubs only in PM1)
Governance Engine
Validation Runner
Memory Store

# Product Milestone 3 (consumed via BLOCKED stubs only in PM1)
Knowledge Graph
```

Produces:

```text
CLICommandRequest
CLICommandResponse
CLICommandHistoryRecord
```

Consumed by:

```text
Human User
Audit Log
Memory Store (PM2+)
Report Writer
```

---

# 41. SIB Registry Entry

```yaml
art_id: "AGENTX::CLI_COMMANDS"
title: "CLI Commands"
type: "production-impl"
language: "python"
layer: 1
file_path: "agentx_initiator/cli/main.py"
current_version: "v3.0.0"
status: "active"
canonicalization_tier: "T1"
spec_bindings:
  - doc: "AGENTX::FIC-AGENTX-INITIATOR-CLI-COMMANDS-001"
    binding_type: "GOVERNS"
    binding_strength: "HARD"
```

---

### Product Milestone 1 Active CLI Bindings

Product Milestone 1 active CLI bindings are limited to:

```
Config / Paths
Audit Log
Repository Scanner
Layer Mapper (indirectly through Repository Scanner)
Minimal Architecture Analyzer
Minimal Report Writer
```

Governance Engine, Risk Engine, Evolution Planner, Patch Proposal Generator, Validation Runner, Memory Store, Knowledge Graph, `report` command, `memory` command, `validate` command, `audit` command, `plan` command, `propose` command, `explain` command, and `graph` command are cumulative CLI contract bindings only. They are not active PM1 dependencies unless represented as BLOCKED stubs with no later-component side effects.

### PM1 Later-Command Stub Restrictions

Product Milestone 1 later-command stubs must not import, instantiate, or invoke Governance Engine, Risk Engine, Evolution Planner, Patch Proposal Generator, Validation Runner, Memory Store, or Knowledge Graph. They may only build and return a schema-valid BLOCKED CLICommandResponse, append command history if enabled, and append an audit event if Audit Log is available.

---

## Product Milestone 1 Test Scope Override

For Product Milestone 1, only the following CLI tests are required:

```text
test_help_flag_success
test_help_alias_success_if_registered
test_scan_command_success
test_status_command_success
test_unknown_command_rejected
test_invalid_arguments_rejected
test_later_commands_absent_or_blocked
test_blocked_stub_returns_command_not_implemented_in_pm1
test_command_request_schema_validates
test_command_response_schema_validates
test_exit_code_matches_status
test_command_history_appends_if_enabled
test_audit_event_appends_when_audit_available
test_cli_does_not_directly_mutate_source_files
test_no_full_governance_engine_required_in_pm1
```

The tests listed below in the frozen component body remain valid for the full CLI component contract or later Product Milestones, but they are not Product Milestone 1 acceptance blockers unless explicitly listed above.

Product Milestone 1 uses component-local write-boundary checks instead of the full Governance Engine.
Full Governance Engine integration tests become active in Product Milestone 2.

---

# 42. Test Contract

Required unit tests:

```text
test_help_command_success
test_status_command_success
test_unknown_command_rejected
test_invalid_arguments_rejected
test_command_request_schema_validates
test_command_response_schema_validates
test_exit_code_matches_status
test_command_history_appends
test_governance_required_for_scan
test_governance_required_for_report
test_governance_required_for_validate
test_governance_block_prevents_handler_execution
test_cli_does_not_directly_mutate_source_files
```

Required negative tests:

```text
test_arbitrary_command_rejected
test_path_traversal_output_rejected
test_source_write_command_rejected
test_shell_execution_rejected
test_network_command_rejected
test_missing_handler_fails
```

> **Compatibility note**: The canonical file name is `repo_scanner.py`, not `repository_scanner.py`.  
> Test names follow the legacy naming in this frozen v2 body.

Required integration tests (PM2+):

```text
test_scan_command_invokes_repository_scanner
test_report_command_invokes_report_writer    # PM2 — not a PM1 blocker
test_validate_command_invokes_validation_runner  # PM2 — not a PM1 blocker
test_memory_command_queries_memory_store     # PM2 — not a PM1 blocker
test_graph_command_queries_knowledge_graph   # PM3 — not a PM1 blocker
```

---

# 43. Test Oracle Strength

Minimum oracle levels:

```yaml
unknown_command_rejection: "O4 invariant"
governance_enforcement: "O4 invariant"        # PM2+ — PM1 does not require full Governance Engine
exit_code_semantics: "O4 invariant"
schema_validation: "O3 negative"
history_append: "O3 negative"
source_non_mutation: "O4 invariant"
```

Smoke tests alone are not sufficient.

---

# 44. Acceptance Criteria

CLI Commands are accepted only if:

- command registry is defined
- valid commands execute through approved handlers
- unknown commands are rejected
- invalid arguments are rejected
- governance-required commands call Governance Engine (PM2+ only — PM1 uses component-local write-boundary checks)
- governance BLOCK prevents handler execution (PM2+ only — PM1 uses component-local checks)
- responses are schema-valid
- exit codes match response statuses
- command history is appended when possible
- audit event is appended when Audit Log is available
- no arbitrary shell execution exists
- no direct source mutation exists
- all required tests pass

---

# 45. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] target files are listed
[ ] public surface is defined
[ ] command registry contract is defined
[ ] command request schema is defined
[ ] command response schema is defined
[ ] command history schema is defined
[ ] command categories are defined
[ ] command statuses are defined
[ ] exit code semantics are defined
[ ] governance integration rules are defined
[ ] command-specific contracts are defined
[ ] write boundaries are defined
[ ] test obligations are defined
[ ] acceptance criteria are binary
```

---

# 46. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] public surface matches FIC
[ ] no extra public symbols are introduced without justification
[ ] no forbidden dependencies are used
[ ] command registry validates
[ ] request schema validates
[ ] response schema validates
[ ] governance-required commands call Governance Engine (PM2+ only — PM1 uses component-local write-boundary checks)
[ ] governance block prevents execution (PM2+ only — PM1 uses component-local checks)
[ ] exit codes match statuses
[ ] command history appends
[ ] unit tests pass
[ ] integration tests pass
[ ] completion record exists
```

---

# 47. Minimal Implementation Package

Milestone 1 implementation package must include:

```text
TASK_CONTRACT.md
CLI_COMMANDS_FIC_EQC_COMMAND_ACCEPTANCE_CRITERIA_v3.md
command_request.schema.json
command_response.schema.json
command_registry.schema.json
command_history_record.schema.json
completion_record.schema.json
implementation_handoff.yaml
completion_record.yaml
```

No coding agent should implement CLI Commands from this document alone without the implementation package.

---

# 48. Implementation Handoff Envelope

```yaml
implementation_handoff:
  fic_id: "FIC-AGENTX-INITIATOR-CLI-COMMANDS-001"
  eqc_id: "EQC-AGENTX-INITIATOR-CLI-COMMANDS-001"
  target_component: "CLI Commands"
  permitted_files:
    # Product Milestone 1
    - "agentx_initiator/cli/main.py"
    - "agentx_initiator/cli/registry.py"
    - "agentx_initiator/cli/models.py"
    - "agentx_initiator/cli/commands/help.py"
    - "agentx_initiator/cli/commands/scan.py"
    - "agentx_initiator/cli/commands/status.py"
    # Product Milestone 2
    - "agentx_initiator/cli/commands/explain.py"
    - "agentx_initiator/cli/commands/plan.py"
    - "agentx_initiator/cli/commands/propose.py"
    - "agentx_initiator/cli/commands/validate.py"
    - "agentx_initiator/cli/commands/audit.py"
    - "agentx_initiator/cli/commands/report.py"
    - "agentx_initiator/cli/commands/memory.py"
    # Product Milestone 3
    - "agentx_initiator/cli/commands/graph.py"
    - "agentx_initiator/schemas/command_request.schema.json"
    - "agentx_initiator/schemas/command_response.schema.json"
    - "agentx_initiator/schemas/command_registry.schema.json"
    - "agentx_initiator/schemas/command_history_record.schema.json"
    - "agentx_initiator/tests/test_cli_commands.py"
    - "agentx_initiator/tests/test_cli_registry.py"
    - "agentx_initiator/tests/test_cli_schema.py"
  forbidden_changes:
    - "L0/"
    - "L1/"
    - "L2/"
    - "source files unrelated to CLI commands"
  allowed_statuses:
    - "IMPLEMENTED_UNVALIDATED"
    - "VALIDATED"
    - "NO_CHANGE"
    - "BLOCKED"
  stop_conditions:
    - "command schema validation cannot be enforced"
    - "governance enforcement cannot be wired"
    - "CLI requires arbitrary shell execution"
    - "CLI requires source mutation"
    - "CLI requires remote execution"
```

---

# 49. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  fic_id: "FIC-AGENTX-INITIATOR-CLI-COMMANDS-001"
  eqc_id: "EQC-AGENTX-INITIATOR-CLI-COMMANDS-001"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|NO_CHANGE|BLOCKED"
  files_created_or_changed: []
  tests_created_or_changed: []
  schemas_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  deviations_from_fic_eqc_command_acceptance: []
  unresolved_risks: []
```

The implementation must not be considered complete without evidence.

---

# 50. Residual Risks

Known residual risks:

```yaml
residual_risks:
  - id: "CLI-RISK-001"
    description: "CLI can become a bypass layer if governance integration is weak."
    severity: "high"
    mitigation: "Require governance for write/execute/validate/report commands."
  - id: "CLI-RISK-002"
    description: "CLI errors can confuse users if exit codes and statuses diverge."
    severity: "medium"
    mitigation: "Test exit-code/status mapping."
  - id: "CLI-RISK-003"
    description: "CLI can expand too quickly into a shell-like agent."
    severity: "medium"
    mitigation: "Keep Milestone 1 command registry fixed and non-interactive."
```

---

# 51. Definition of Done

### Product Milestone 1 DoD

CLI Commands Product Milestone 1 is done when it can:

- register approved commands (help, scan, status)
- reject unknown commands
- validate command requests
- validate command arguments
- use component-local write-boundary checks in place of full Governance Engine
- reject unsafe output paths
- route valid commands to approved handlers
- produce schema-valid responses
- return correct exit codes
- append command history when enabled
- emit audit events when available
- pass required tests
- avoid arbitrary shell execution
- avoid direct source mutation

### Component Milestone 1 / Product Milestone 2+ DoD

- governance-required commands call Governance Engine
- governance BLOCK prevents execution

---

# 52. Freeze Rule

This document is now the controlling CLI Commands FIC+EQC+Command Acceptance Criteria document for Milestone 1.

Do not keep expanding this document unless a true implementation-blocking gap is discovered.

Next artifacts should be:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
command_request.schema.json
command_response.schema.json
command_registry.schema.json
command_history_record.schema.json
completion_record.schema.json
```

---

# 53. Final Success Definition

CLI Commands v1 implementation is successful when it provides a deterministic, schema-valid, governance-controlled command interface for approved Initiator operations while preserving traceability, enforcing command acceptance criteria, and preventing unauthorized execution or direct source mutation.

---

# 54. Final Rating

This FIC+EQC+Command Acceptance Criteria document is rated **10/10** for the initial CLI Commands component.

It is ready to be used as the controlling document for the CLI Commands Milestone 1 implementation package.

---

## Synchronization Status

**Canonical command name:** `agentx-init`  
**Canonical runtime root:** `.agentx-init/`  
**Canonical config file:** `config.json`  
**Canonical path authority:** `path_registry.py`  
**Interpretation rule:** Product Milestone placement is separate from Component Milestone 1.

This document has been synchronized with the Milestone and Naming Alignment Addendum.  
Product Milestone 1 active commands are help/scan/status. Product Milestone 1 uses component-local write-boundary checks in place of the full Governance Engine. Later commands are described as PM2 or PM3 scope, or as BLOCKED stubs.
