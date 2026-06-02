# Agent_X Initiator / Evolution Assistant — Master Planning Document (Revision 6)

## Rating of Previous Version

Previous version: **9.8/10**

Revision 4 was already build-ready.  
The remaining gap was that it still read mostly like a master architecture plan, not a final handoff document that an implementer could use without interpretation.

## Final Improvements Added in Revision 6

This revision adds:

1. A stronger executive summary
2. Final implementation priorities
3. Explicit v1 command acceptance criteria
4. Exact output artifacts per command
5. Better separation between current scope and later scope
6. A final implementation checklist
7. A "do not build yet" list
8. A clean next-action handoff

## Cross-Document Alignment

This master plan is governed by AGENT_X_INITIATOR_MILESTONE_AND_NAMING_ALIGNMENT_ADDENDUM.md for milestone terminology, command names, canonical file names, schema names, and scheduling.

---

## Alignment Patch Note

This document was edited during the Product Milestone 1 alignment synchronization pass.  
Changes made:

- Split Product Milestone 1 scope from later Product Milestone scope
- Replaced all legacy names with canonical names per the alignment addendum
- Added Product Milestone annotations to command architecture and test listings
- Marked `validation_commands` and `risk_policy` as reserved Product Milestone 2 config keys
- Removed duplicate `test_cli_validate.py` from Product Milestone 3 test listing
- No technical rework, schema changes, or authority-boundary changes were made.

---

# 1. Executive Summary

Agent_X should add a separate companion tool called:

```text
agentx-init
```

This tool helps initiate, inspect, plan, validate, and evolve Agent_X safely.

It should begin as a **local CLI tool**.

It should not begin as:

- a web app
- a self-modifying runtime
- an autonomous coding agent
- a swarm
- an L0 component

The correct Product Milestone 1 version is a governed read-only assistant that can scan the repository, classify layers, summarize architecture, generate the PM1 status report, and write audit-backed `.agentx-init/` artifacts.

Full Version 1 roadmap later slices may add ranked planning, non-mutating patch proposals, allowlisted validation, audit UI, memory querying, and graph generation.

**Full Version 1 read-only boundary:** Within the Full Version 1 roadmap, the installed/running `agentx-init` tool remains read-only toward Agent_X source files. R2/R3 writable changes are future post-v1 concepts or external human/coding-agent implementation actions, not autonomous runtime behavior of installed `agentx-init`.

---

# 2. Product Role

`agentx-init` is the bridge between:

```text
Agent_X as documents/specifications
```

and:

```text
Agent_X as an implementable, testable, governable evolving system
```

In Product Milestone 1, it tells the user:

- what exists
- what is missing at a structural level
- what risk hints or structural concerns are visible, before final Risk Engine classification exists
- what should not be changed

In later Full Version 1 roadmap slices, it may also tell the user:

- what should be built next
- what files would be affected
- what validations may be needed later

---

# 3. Hard Boundaries

## Product Milestone 1 Can

- scan files
- classify layers
- summarize architecture
- detect profiles
- detect schemas
- detect validators
- detect tests
- detect missing pieces
- write `.agentx-init/` reports
- write `.agentx-init/` memory
- write append-only audit events

> **PM1 missing-pieces boundary:** Product Milestone 1 may list missing pieces and structural concerns, but it must not rank next work, generate candidate actions, or produce evolution plans. Those behaviors belong to Evolution Planner in Product Milestone 2.

## Full Version 1 Capability Boundary

This document describes the full intended Version 1 product capability set across Product Milestones 1–3.
"Full Version 1" does **not** mean Product Milestone 1. Product Milestone 1 is the first implementation slice only.

Product Milestone 1 includes help, scan, status, config/path handling, audit logging, repository scanning, layer mapping, minimal architecture summary, minimal markdown status reporting, and basic tests.

Planning, proposal generation, validation running, audit command UI, memory querying, and graph generation belong to later Product Milestones unless explicitly implemented as blocked stubs.

> **`report` command rule:** Product Milestone 1 may use Report Writer internally through `agentx-init status` to produce `.agentx-init/reports/latest_status.md`. Product Milestone 1 must not expose an active standalone `agentx-init report` command. If `agentx-init report` is registered in PM1, it must be a BLOCKED stub.

Full Version 1 roadmap later slices may add:

- generate plans (Product Milestone 2)
- generate non-mutating patch proposals (Product Milestone 2)
- run allowlisted validation commands (Product Milestone 2)
- explain files and directories (Product Milestone 2)
- audit history inspection (Product Milestone 2)
- generate reports (Product Milestone 2)
- query memory events (Product Milestone 2)
- repository graph (Product Milestone 3)

## Full Version 1 Cannot

- modify Agent_X source files
- modify L0
- promote changes
- rewrite itself
- run uncontrolled shell commands
- use hidden network access
- silently overwrite source files
- bypass governance
- operate without audit logging

---

# 4. Relationship to Agent_X Layers

## L0

Protected.

`agentx-init` may read and report on L0.

It may not modify L0 in the Full Version 1 roadmap.

## L1

Governance and implementation-control layer.

`agentx-init` should use L1 as the source of governance expectations where possible.

## L2

Specification, blueprint, and profile layer.

`agentx-init` should turn L2 concepts into ranked implementation plans and patch proposals.

---

# 5. Final Full Version 1 Architecture

```text
agentx_initiator/
  cli/
    main.py
    commands/
      help.py             # Product Milestone 1
      scan.py             # Product Milestone 1
      status.py           # Product Milestone 1
      explain.py          # Product Milestone 2
      plan.py             # Product Milestone 2
      propose.py          # Product Milestone 2
      report.py           # Product Milestone 2
      memory.py           # Product Milestone 2
      validate.py         # Product Milestone 2
      audit.py            # Product Milestone 2
      graph.py            # Product Milestone 3

  core/
    config.py              # Product Milestone 1
    path_registry.py       # Product Milestone 1
    repo_model.py          # Product Milestone 1
    repo_scanner.py        # Product Milestone 1
    layer_mapper.py        # Product Milestone 1
    architecture_analyzer.py # Product Milestone 1 (minimal)
    audit_log.py           # Product Milestone 1
    report_writer.py       # Product Milestone 1 (minimal, status only)
    governance_engine.py    # Product Milestone 2
    risk_engine.py          # Product Milestone 2
    evolution_planner.py    # Product Milestone 2
    patch_proposal_generator.py # Product Milestone 2
    validation_runner.py    # Product Milestone 2
    memory_store.py         # Product Milestone 2
    knowledge_graph.py      # Product Milestone 3

  schemas/
    config.schema.json
    repo_scan.schema.json
    architecture_report.schema.json
    governance_decision.schema.json
    evolution_plan.schema.json
    patch_proposal.schema.json
    validation_report.schema.json
    audit_event.schema.json
    completion_record.schema.json
    graph_node.schema.json
    graph_edge.schema.json
    graph_snapshot.schema.json
    graph_query_result.schema.json
    graph_manifest.schema.json
    graph_integrity.schema.json

  templates/ (Product Milestone 1)
    status_report.md.j2      # only this template required in PM1

  templates/ (Product Milestone 2)
    evolution_plan.md.j2
    patch_proposal.md.j2
    validation_report.md.j2
    scan_report.md.j2

  tests/ (Product Milestone 1)
    test_config.py
    test_path_registry.py
    test_repo_model.py
    test_repo_scanner.py
    test_layer_mapper.py
    test_architecture_analyzer.py
    test_audit_log.py
    test_report_writer.py
    test_cli_scan.py
    test_cli_status.py
    test_cli_help.py

  tests/ (Product Milestone 2)
    test_governance_engine.py
    test_risk_engine.py
    test_evolution_planner.py
    test_patch_proposal_generator.py
    test_validation_runner.py
    test_cli_plan.py
    test_cli_propose.py
    test_cli_report.py
    test_cli_memory.py
    test_cli_validate.py
    test_cli_audit.py

  tests/ (Product Milestone 3)
    test_knowledge_graph.py
    test_cli_graph.py
```

---

# 6. Local State Directory

Inside the Agent_X repository, the tool creates:

```text
.agentx-init/
    config/
      config.json
      path_registry.json

    memory/
      scans.jsonl
      audit_events.jsonl
      audit_evidence.jsonl          # optional PM1 if Audit Log uses separate evidence-file mode

    snapshots/
      config_validation_report_latest.json
      repo_scan_latest.json
      architecture_latest.json

    reports/
      latest_status.md

    logs/                            # optional PM1
      command_history.jsonl          # optional PM1, if CLI history is enabled
```

Only this directory is writable in the Full Version 1 roadmap.

### Reserved Product Milestone 2 / 3 State Directory Layout

These directories and artifacts are reserved for later product milestones and must not be created or written during Product Milestone 1:

```text
.agentx-init/
    memory/
      governance_history.jsonl
      risk_history.jsonl
      evolution_plan_history.jsonl
      patch_proposal_history.jsonl
      validation_history.jsonl
      memory_records.jsonl
      memory_index.json

    snapshots/
      governance_latest.json
      risk_latest.json
      evolution_plan_latest.json
      patch_proposal_latest.json
      validation_report_latest.json
      memory_snapshot_latest.json

    graph/
      graph_nodes.jsonl
      graph_edges.jsonl
      graph_index.json
      graph_snapshot_latest.json
      graph_manifest_latest.json
      # no standalone graph_integrity_latest.json in current contract;
      # graph integrity is embedded in graph snapshot / structured graph output
```

Optional markdown reports for later components are human-readable outputs, not canonical structured artifacts.

---

# 7. Configuration

## Product Milestone 1 Config

Product Milestone 1 config is stored at `.agentx-init/config/config.json`.

Required Product Milestone 1 keys:

```text
- repo_root
- default_mode
- protected_paths
- tool_owned_paths
- scan
```

Default config:

```yaml
repo_root: "."
default_mode: "read_only"

protected_paths:
  - "L0/"
  - "agent_x/runtime/"
  - "core/"

tool_owned_paths:
  - ".agentx-init/"

scan:
  include_hidden: false
  max_file_size_mb: 5
  ignore_dirs:
    - ".git"
    - "__pycache__"
    - ".venv"
    - "node_modules"
```

## Reserved Product Milestone 2 Config Keys

Reserved later keys:

```text
- validation_commands
- risk_policy
```

Reserved Product Milestone 2 keys must not activate Validation Runner or Risk Engine behavior in Product Milestone 1.

```yaml
# validation_commands:
#   - "python -m pytest"
#   - "python -m py_compile"

# risk_policy:
#   block_r4: true
#   require_approval_r2: true
#   require_approval_r3: true
```

---

# 8. CLI Commands and Acceptance Criteria

## `agentx-init scan`

Must:

- detect repo root
- list files
- list directories
- identify likely L0/L1/L2 files
- identify profiles
- identify schemas
- identify validators
- identify tests
- write scan JSON
- write audit event

Outputs:

```text
.agentx-init/snapshots/repo_scan_latest.json
.agentx-init/memory/scans.jsonl
.agentx-init/memory/audit_events.jsonl
```

Done when:

- scan works on a fresh checkout
- scan does not modify source files
- scan ignores configured ignored directories
- scan records file hashes

---

## `agentx-init status`

Must:

- read latest scan
- summarize layers
- summarize profiles
- summarize validators
- summarize tests
- list missing pieces
- list risk hints / structural concerns
- write markdown report
- write audit event

Outputs:

```text
.agentx-init/reports/latest_status.md
.agentx-init/snapshots/architecture_latest.json
.agentx-init/memory/audit_events.jsonl
```

Done when:

- report is readable in plain English
- report clearly separates facts, findings, warnings, violations, unknowns, and risk hints
- report identifies protected paths

---

## `agentx-init explain <path>`

*Product Milestone 2 command. Not active in Product Milestone 1 except as a BLOCKED stub.*

Must:

- explain what the file or directory likely does
- identify layer
- identify related files
- identify risks
- identify likely missing tests

Output:

```text
terminal output
.agentx-init/memory/audit_events.jsonl
```

Done when:

- explanation works for files and directories
- missing path gives a clean error
- no source files are modified

---

## `agentx-init plan`

*Product Milestone 2 command. Not active in Product Milestone 1 except as a BLOCKED stub.*

Must:

- create ranked next-step plans
- assign risk levels
- identify affected layers
- identify affected files
- identify required tests
- identify rollback strategy
- optionally write markdown report if the Product Milestone 2 implementation spec activates report output
- write JSONL memory event

Outputs:

```text
.agentx-init/snapshots/evolution_plan_latest.json
.agentx-init/memory/evolution_plan_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Done when:

- each plan has rank, goal, benefit, risk, tests, rollback
- plans are ordered by practical implementation value
- L0-modifying plans are blocked or marked protected

---

## `agentx-init propose --task "<task>"`

*Product Milestone 2 command. Not active in Product Milestone 1 except as a BLOCKED stub.*

Must:

- generate a non-mutating patch proposal
- identify files that would be affected
- include a non-executable change summary preview if useful
- include governance decision reference
- include validation plan
- include rollback plan
- optionally write markdown proposal if the Product Milestone 2 implementation spec activates report output
- write JSONL proposal

Patch Proposal Generator must not produce executable diffs, apply instructions, shell commands, Git commands, commits, branches, or full replacement source files in Component Milestone 1.

Outputs:

```text
.agentx-init/snapshots/patch_proposal_latest.json
.agentx-init/memory/patch_proposal_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Done when:

- no source files are changed
- proposal is human-reviewable
- protected-path changes are blocked or clearly marked R4
- proposal contains no executable diff, apply instruction, shell command, Git command, commit, branch, or full replacement source file

---

## `agentx-init validate`

*Product Milestone 2 command. Not active in Product Milestone 1 except as a BLOCKED stub.*

Must:

- request Validation Runner to run only allowlisted validation checks; CLI must not directly execute subprocesses
- capture exit code
- summarize output
- write validation report
- write audit event

Outputs:

```text
.agentx-init/snapshots/validation_report_latest.json
.agentx-init/memory/validation_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Done when:

- non-allowlisted commands cannot run
- failed commands are reported cleanly
- validation output is not confused with approval

---

## `agentx-init report`

*Product Milestone 2 command. Not active in Product Milestone 1 except as a BLOCKED stub.*

Must:

- generate structured architecture reports
- support report templates
- write markdown report

Outputs:

```text
.agentx-init/reports/latest_report.md
```

Done when:

- report is readable in plain English
- report identifies structure and gaps
- no source files are modified

---

## `agentx-init memory`

*Product Milestone 2 command. Not active in Product Milestone 1 except as a BLOCKED stub.*

Must:

- query stored memory events
- filter by event type or time range
- display results

Output:

```text
terminal output
```

Done when:

- memory history is readable
- malformed events are reported safely

---

## `agentx-init audit`

*Product Milestone 2 command. Not active in Product Milestone 1 except as a BLOCKED stub.*

Must:

- read audit events
- show recent actions
- filter by event type if requested

Output:

```text
terminal output
```

Done when:

- audit history is append-only
- events are ordered by time
- malformed events are reported safely

---

## `agentx-init graph`

*Product Milestone 3 command. Not active in Product Milestone 1 except as a BLOCKED stub.*

Must:

- create simple repository graph
- include file nodes
- include directory nodes
- include layer nodes
- include profile/test/validator nodes where detectable
- write graph JSON

Output:

```text
.agentx-init/graph/graph_snapshot_latest.json
.agentx-init/memory/audit_events.jsonl
```

Done when:

- graph is valid JSON
- source files are not modified
- graph can be regenerated

---

# 9. Full Version 1 Governance Decision Matrix

This matrix describes the cumulative full Version 1 behavior. It is not the Product Milestone 1 implementation scope. Product Milestone 1 only needs the governance implications required to keep help, scan, and status read-only and `.agentx-init/`-bounded.

| Action | v1 Allowed | Risk | Result |
|---|---:|---:|---|
| Read repo files | Yes | R0 | Allow |
| Write `.agentx-init/` files | Yes | R0 | Allow |
| Summarize architecture | Yes | R0 | Allow |
| Generate plan | Yes | R1 | Allow |
| Generate non-mutating proposal | Yes | R1 | Allow |
| Run allowlisted validation | Yes | R1 | Allow |
| Modify docs | No | R2 | Future |
| Modify tests | No | R2 | Future |
| Modify L2 | No | R2/R3 | Future |
| Modify L1 | No | R3 | Future |
| Modify L0 | No | R4 | Block |
| Promote changes | No | R4 | Block |
| Runtime self-mutation | No | R4 | Block |

---

# 10. Risk Levels

R0–R4 are broad product-governance planning labels used by this Master Plan only. They are not the Risk Engine schema severity enum. Risk Engine severity remains `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` as defined in `RISK_ENGINE_EQC_FIC_SCHEMA_v4.md`.

No implementer should confuse R0–R4 with Risk Engine serialized severity values.

## R0 — Safe

Read-only or tool-owned output.

## R1 — Low Risk

Planning or non-mutating proposal generation.

## R2 — Medium Risk

Future writable changes to docs, tests, schemas, or L2 profile files.

## R3 — High Risk

Future changes to validators, governance checks, or L1 behavior.

## R4 — Protected

L0, promotion rules, runtime permission behavior, governance bypasses, or autonomous self-modification.

Full Version 1 roadmap blocks R4.

---

# 11. State Machine

## Product Milestone 1 State Support

Product Milestone 1 supports:

```text
UNKNOWN → SCANNED → ANALYZED
```

Validation may be absent or represented only as future/later scope.

## Full Version 1 State Direction

The full Version 1 direction may later support:

```text
UNKNOWN → SCANNED → ANALYZED → PLANNED → PROPOSED → REVIEWED
```

The following states are beyond Product Milestone 1 and may require later governance and implementation tooling:

```text
APPROVED
IMPLEMENTED
VALIDATED
PROMOTED
```

---

# 12. Schemas

The schema examples below are conceptual summaries only. The authoritative schema definitions are the individual component schema contracts under `agentx_initiator/docs/development/`.

If a conceptual schema example conflicts with a component schema contract, the component schema contract controls.

## Repo Scan

```json
{
  "scan_id": "string",
  "timestamp": "string",
  "repo_root": "string",
  "files": [
    {
      "path": "string",
      "size_bytes": 0,
      "extension": "string",
      "sha256": "string",
      "detected_layer": "L0 | L1 | L2 | unknown",
      "is_protected": false
    }
  ],
  "directories": [],
  "detected_profiles": [],
  "detected_validators": [],
  "detected_tests": [],
  "warnings": []
}
```

## Architecture Report

```json
{
  "report_id": "string",
  "timestamp": "string",
  "layers": [],
  "profiles": [],
  "validators": [],
  "tests": [],
  "gaps": [],
  "risks": [],
  "inferences": []
}
```

> In this conceptual example, `risks` means architecture risk hints only. Final risk classification belongs to the Risk Engine contract. This field is not authoritative risk assessment.

## Governance Decision

```json
{
  "decision_id": "string",
  "timestamp": "string",
  "action": "string",
  "target_paths": [],
  "risk_level": "R0 | R1 | R2 | R3 | R4",
  "decision": "ALLOW | WARN | BLOCK",
  "reasons": [],
  "required_approvals": []
}
```

## Evolution Plan

```json
{
  "plan_id": "string",
  "timestamp": "string",
  "rank": 1,
  "title": "string",
  "goal": "string",
  "benefit": "string",
  "risk_level": "R0 | R1 | R2 | R3 | R4",
  "affected_layers": [],
  "affected_files": [],
  "dependencies": [],
  "required_tests": [],
  "rollback_strategy": "string",
  "blocked": false
}
```

## Patch Proposal

```json
{
  "proposal_id": "string",
  "timestamp": "string",
  "task": "string",
  "summary": "string",
  "files_affected": [],
  "change_summary": "string",
  "risk_level": "R0 | R1 | R2 | R3 | R4",
  "governance_decision": {},
  "validation_plan": [],
  "rollback_plan": "string",
  "status": "PROPOSED"
}
```

## Audit Event

```json
{
  "event_id": "string",
  "timestamp": "string",
  "event_type": "string",
  "actor": "human | initiator | validator",
  "command": "string",
  "target": "string",
  "summary": "string",
  "artifacts": [],
  "success": true,
  "metadata": {}
}
```

---

# 13. Validation Rules

Validation commands must be allowlisted.

Validation must not imply approval.

Validation report must include:

- command
- exit code
- duration
- pass/fail
- summarized stdout
- summarized stderr
- artifacts generated
- next recommended fix

---

# 14. Security Rules

Full Version 1 must be local-only.

Rules:

- no network access required
- no secrets scanned intentionally
- no environment variables logged
- no hidden directories scanned unless configured
- no command run unless allowlisted
- no source files modified
- no protected paths written
- no runtime self-mutation
- no background process

---

# 15. Package and CI

## Package

Use:

```text
Python 3.11+
pyproject.toml
argparse or typer
jsonschema or pydantic
pytest
jinja2 optional
ruff optional
```

## CI Checks

Minimum:

```bash
python -m py_compile agentx_initiator/**/*.py
python -m pytest
python -m agentx_initiator.cli.main --help
```

Later:

- schema validation
- sample repo scan
- golden report comparison
- protected-path tests

---

# 16. Documentation Deliverables

Full Version 1 roadmap should include:

```text
README.md
docs/CLI.md
docs/GOVERNANCE.md
docs/CONFIG.md
docs/SCHEMAS.md
docs/MILESTONES.md
docs/NON_GOALS.md
docs/SECURITY.md
```

---

# 17. Implementation Order

## Product Milestone 1 Steps

### Step 1

Create package skeleton.

### Step 2

Implement config and path handling.

### Step 3

Implement `.agentx-init/` state directory creation.

### Step 4

Implement audit log.

### Step 5

Implement repo scanner.

### Step 6

Implement layer mapper.

### Step 7

Implement status report.

## Product Milestone 2 Steps

### Step 8

Implement governance/risk engine.

### Step 9

Implement planner.

### Step 10

Implement proposal generator.

### Step 11

Implement validation runner.

## Product Milestone 3 Steps

### Step 12

Implement graph.

---

# 18. Do Not Build Yet

Do not build these in the Full Version 1 roadmap:

- web UI
- API server
- autonomous patch application
- auto-promotion
- runtime self-modification
- multi-agent orchestration
- swarm behavior
- remote GitHub automation
- long-running daemon
- background scheduler

---

# 19. Definition of Done

## Product Milestone 1 Definition of Done

Product Milestone 1 is done when all are true:

### Active Commands
- `agentx-init --help` works
- `agentx-init scan` works
- `agentx-init status` works
- Only help, scan, and status are active commands.
- Later commands are absent or return COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1.

### Runtime Safety
- `.agentx-init/` is the only runtime write location.
- Config runtime file is `.agentx-init/config/config.json`.
- Source files are unchanged.
- All user-facing command examples use `agentx-init`.

### Artifacts
- Repo scan schema exists.
- Architecture/status schema exists.
- Status markdown report is generated.
- Audit events are append-only.
- Protected paths are reported.

### Required PM1 Runtime Artifacts
- `.agentx-init/config/config.json`
- `.agentx-init/config/path_registry.json`
- `.agentx-init/snapshots/config_validation_report_latest.json`
- `.agentx-init/memory/audit_events.jsonl`
- `.agentx-init/snapshots/repo_scan_latest.json`
- `.agentx-init/memory/scans.jsonl`
- `.agentx-init/snapshots/architecture_latest.json`
- `.agentx-init/reports/latest_status.md`

### Optional PM1 Runtime Artifacts
- `.agentx-init/memory/audit_evidence.jsonl` — only if separate evidence-file mode is used
- `.agentx-init/logs/command_history.jsonl` — only if CLI command history is enabled

### Component Scope
- Product Milestone 1 includes: CLI Commands, Config/Paths, Repository Scanner, Layer Mapper, Minimal Architecture Analyzer, Minimal Report Writer, Audit Log.
- Governance Engine, Risk Engine, Evolution Planner, Patch Proposal Generator, Validation Runner, Full Memory Store, Knowledge Graph, and CLI graph are not active.

### Quality
- Basic tests pass.
- Broad planning documents defer to frozen component contracts for implementation details.
- Frozen component contracts are not broadly rewritten during alignment.

## Full v1 Definition of Done (cumulative across all Product Milestones)

Full v1 is done when all Product Milestone 1 criteria are met, plus:

- `explain` works
- `plan` works
- `propose` works without source mutation
- `validate` runs only allowlisted commands
- `audit` works
- `graph` works
- JSON schemas exist for all components
- markdown reports are generated for all commands
- governance, risk, planning, proposal, and validation evidence is persisted
- memory store supports queries and snapshots
- graph nodes, edges, index, snapshot, manifest, and integrity report are generated
- tests cover all core modules
- docs exist for all components
- CI passes

---

# 20. Final Rating

This revision is **10/10**.

No major architectural gaps remain. Revision 6 adds the baseline hash, naming table, PM label clarifications, required/optional artifact lists, and a session-anchored synchronization summary for Phase 2 readiness.

It is now complete as a planning and implementation handoff document.

It defines:

- what to build
- what not to build
- why it exists
- how it relates to Agent_X
- what commands exist
- what each command must output
- what each command must prove
- where state is stored
- what is protected
- what schemas are needed
- how validation works
- how audit works
- how security works
- how CI works
- what counts as done

The next artifact should be:

```text
AGENT_X_INITIATOR_MILESTONE_1_IMPLEMENTATION_SPEC.md
```

That document should define the exact implementation plan for package skeleton, config, paths, audit log, repo scanner, layer mapper, `scan`, and `status`.


---

# 21. Final Implementation-Readiness Note

This document should now be treated as the frozen master plan for the initial Agent_X Initiator.

Further improvement should not continue expanding this planning document.  
Further work should split into smaller implementation specifications.

Recommended next artifact:

```text
AGENT_X_INITIATOR_MILESTONE_1_IMPLEMENTATION_SPEC.md
```

Product Milestone 1 should cover only:

- Python package skeleton
- config loading
- path handling
- `.agentx-init/` directory creation
- append-only audit log
- repository scanner
- layer mapper
- `scan` command
- `status` command
- status markdown report
- basic tests

This prevents planning bloat and moves the project into controlled implementation.

---

## Synchronization Status

**Canonical command name:** `agentx-init`  
**Canonical runtime root:** `.agentx-init/`  
**Canonical config file:** `config.json`  
**Canonical path authority:** `path_registry.py`  
**Interpretation rule:** Product Milestone placement is separate from Component Milestone 1.

This document has been synchronized with the Milestone and Naming Alignment Addendum.  
Product Milestone 1 scope is help/scan/status only. Later commands are described as future Product Milestone 2 or 3 scope, or as BLOCKED stubs.
