# TOOL_MCP_ADAPTER_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: TOOL_MCP_ADAPTER_IMPLEMENTATION_REVIEW_AND_DOD
version: v5.0
status: final post-implementation review template and Definition of Done
component_id: AGENTX_TOOL_MCP_ADAPTER
component_name: Tool / MCP Adapter Layer
roadmap_layer: 5
roadmap_phase: Phase B — Tool Exposure
review_use: use after code is committed
basis_documents:
  - TOOL_MCP_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
  - TOOL_MCP_ADAPTER_IMPLEMENTATION_SPEC_v1
  - TOOL_MCP_ADAPTER_IMPLEMENTATION_REVIEW_AND_DOD_v4
  - TOOL_MCP_ADAPTER_IMPLEMENTATION_REVIEW_AND_DOD_v5
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria
optional_standards: ES, Report Template
canonical_tool_subdirectory: tools/agentx_evolve/tools/
canonical_mcp_subdirectory: tools/agentx_evolve/mcp/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/tool_calls/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v5 Review and Upgrade Summary

The v4 review / DoD document was strong, but I would rate it:

```text
9.7/10
```

It already had complete major coverage for structure, validation, registry, permissions, MCP exposure, CLI wrappers, blocked tools, invalid tools, audit evidence, review reports, completion records, scoring, and GO / NO-GO rules.

It was not fully 10/10 because it still had several precision gaps:

```text
1. Section numbering used 22A, which is less stable for references than normal numeric sectioning.
2. The NO-GO list duplicated `review report is missing`.
3. The evidence manifest example required exit codes for compileall and pytest, but not explicitly for schema validation.
4. Hashing was still optional when a hash helper was unavailable, even though Python standard-library hashing is enough.
5. The review report did not require hashes for the report itself and completion record.
6. The document did not define a strict evidence immutability rule after final verdict.
7. Deferred MCP handling needed a clearer distinction between `DEFERRED SAFELY`, `NOT APPLICABLE`, and missing implementation.
8. The runtime artifact boundary allowed justified exceptions but did not require those exceptions to be listed in a deviation register.
9. The scoring hard caps needed a stronger cap for missing reviewed commit and missing exit codes.
10. The final sign-off needed a more complete reviewer-independence and reproducibility block.
```

This v5 applies those corrections and is the final 10/10 review / DoD template.

---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Tool / MCP Adapter Layer**.

Use this document after code is committed to determine whether the Tool / MCP Adapter Layer is complete, validated, safe, auditable, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether the tool registry is complete
whether tool permission checks work
whether MCP exposure is safe or safely deferred
whether blocked tools fail closed
whether invalid tools fail closed
whether audit/evidence is written
whether Agent_X integration works
whether OpenCode-style concepts were borrowed safely
whether CLI command wrappers are safe, if exposed
whether negative tests prove forbidden behavior fails closed
whether evidence hashes and review artifacts are complete
whether the implementation is DONE or NOT DONE
```

This document reviews the implementation. A 10/10 rating for this document does not mean the implementation is done. The implementation is done only after the validation commands and evidence checks in this document pass and the review report records the evidence.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because this layer is safety-critical. It controls which tools exist, who can call them, what effects they may request, and whether calls can reach file, command, Git, network, patch, or MCP behavior.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Command Acceptance Criteria, if CLI commands are exposed
```

## 2.3 Conditional Standards

```text
MCP Protocol Acceptance Criteria, if MCP server/runtime is exposed in this phase
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if it writes markdown reports
```

---

# 3. Why This Layer Needs These Standards

The Tool / MCP Adapter Layer is safety-critical because it decides:

```text
which tools exist
which roles can call each tool
which tools are read-only
which tools can write runtime state
which tools can request source mutation
which tools can execute validation commands
which tools can access Git
which tools can use network or external providers
which calls require sandbox checks
which calls require capability policy checks
which calls require governance or human approval
how tool calls and results are logged
how invalid or blocked tool calls fail closed
how MCP-visible tools are filtered
how command wrappers avoid raw shell execution
how review evidence proves that the implementation did not bypass safety
```

It must cover Agent_X-safe equivalents of OpenCode-style tool primitives:

```text
read_file_guarded
list_files_guarded
search_files_guarded
write_file_guarded
edit_file_guarded
patch_apply_guarded
run_allowlisted_command
agentx_scan
agentx_status
agentx_plan
agentx_propose
agentx_validate
patch_session_status
rollback_session
git_status
git_diff
ask_human
invalid_tool_handler
```

OpenCode-style concepts may be borrowed as architectural patterns only. OpenCode source code, runtime dependency, Bun dependency, Node dependency, network behavior, and ungoverned tool exposure must not be imported into Agent_X for this layer.

---

# 4. Review Target

Fill this section after implementation.

```text
review_target_commit: <commit hash>
review_target_branch: <branch name>
review_date_utc: <timestamp>
reviewer: <name or tool>
repository: https://github.com/Astrocytech/Agent_X
working_tree_start_status: CLEAN | EXPECTED_RUNTIME_ARTIFACTS_ONLY | DIRTY
working_tree_end_status: CLEAN | EXPECTED_RUNTIME_ARTIFACTS_ONLY | DIRTY
review_environment:
  os: <name/version>
  python_version: <version>
  pytest_version: <version or NOT INSTALLED>
```

The review is invalid if the reviewed commit is not recorded.

## 4.1 Review Validity Rules

The review is valid only if all of the following are true:

```text
[ ] reviewed commit is recorded
[ ] validation was run against that exact commit
[ ] initial working-tree state is recorded
[ ] final working-tree state is recorded
[ ] environment information is recorded
[ ] every required command records command text, exit code, status, and summary
[ ] every command marked PASS has exit_code 0
[ ] every expected-failure negative test records the expected failure condition
[ ] review report artifact is created
[ ] evidence manifest exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] required evidence hashes are present
[ ] reviewer did not rely only on the document's internal rating
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

The implementation may not be marked `DONE` because this document says `review_document_rating: 10/10`. The implementation can be marked `DONE` only when the recorded validation evidence satisfies the GO criteria.

---

# 5. Status Vocabulary

Use only these status values in review tables.

```text
PASS
PARTIAL
FAIL
NOT CHECKED
NOT RUN
NOT APPLICABLE
DEFERRED SAFELY
```

| Status | Meaning | DONE allowed? |
|---|---|---|
| PASS | Requirement was checked and satisfied. | Yes |
| PARTIAL | Some required parts are present, but coverage is incomplete. | No, unless explicitly non-blocking and documented |
| FAIL | Requirement was checked and failed. | No |
| NOT CHECKED | Requirement was not validated. | No |
| NOT RUN | Required command or executable check was not run. | No |
| NOT APPLICABLE | Requirement does not apply to the implemented scope and cannot affect runtime behavior. | Yes, if justified |
| DEFERRED SAFELY | Feature is intentionally deferred and cannot execute, expose, mutate, open ports, or bypass policy/sandbox. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Deferral Rules

Use these rules to avoid hiding missing work behind `NOT APPLICABLE` or `DEFERRED SAFELY`.

```text
NOT APPLICABLE:
  Use only when the implementation scope truly does not include the feature and there is no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot execute, expose tools, mutate files, call network, or open ports.

PARTIAL:
  Use when some files or tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

MCP may be `DEFERRED SAFELY` only if the review proves:

```text
no MCP server starts on import
no MCP network port opens
no mutating MCP tool is exposed
no MCP request bypasses policy
no MCP request bypasses sandbox
no external MCP runtime is required for validation
safe deferral is recorded in the deviation register
```

---

# 6. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or a clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_tool_mcp_schemas.py
git status --short
```

Required result:

```text
initial git status: clean or expected known runtime artifacts only
python version: recorded
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation command: PASS, exit_code 0
final git status: clean or expected runtime artifacts only
```

If `validate_tool_mcp_schemas.py` is not implemented, the same schema coverage must be proven by a documented pytest file such as:

```text
tools/agentx_evolve/tests/test_tool_mcp_schema_validation.py
```

This is required because the Tool / MCP Adapter controls tool execution and must not mutate source files during tests.

---

# 7. Expected Implementation Scope

## 7.1 Required Tool Package

Expected location:

```text
tools/agentx_evolve/tools/
```

Expected files:

```text
tools/agentx_evolve/tools/__init__.py
tools/agentx_evolve/tools/tool_models.py
tools/agentx_evolve/tools/tool_registry.py
tools/agentx_evolve/tools/tool_policy.py
tools/agentx_evolve/tools/tool_call_logger.py
tools/agentx_evolve/tools/initiator_tools.py
tools/agentx_evolve/tools/security_tools.py
tools/agentx_evolve/tools/patch_tools.py
tools/agentx_evolve/tools/git_tools.py
tools/agentx_evolve/tools/human_tools.py
tools/agentx_evolve/tools/invalid_tool.py
```

## 7.2 Required MCP Package

Expected location:

```text
tools/agentx_evolve/mcp/
```

Expected files if MCP is implemented or stubbed:

```text
tools/agentx_evolve/mcp/__init__.py
tools/agentx_evolve/mcp/mcp_models.py
tools/agentx_evolve/mcp/mcp_adapter.py
tools/agentx_evolve/mcp/mcp_server.py
```

MCP may be implemented as a safe non-running adapter stub in this phase. If deferred, the implementation must prove that no MCP server starts, no MCP port opens, and no mutating MCP tool is exposed.

## 7.3 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
tool_registry.schema.json
tool_definition.schema.json
tool_call.schema.json
tool_result.schema.json
tool_permission_decision.schema.json
tool_policy.schema.json
tool_trust_tier.schema.json
mcp_tool_manifest.schema.json
invalid_tool_record.schema.json
tool_audit.schema.json
evidence_manifest.schema.json
review_report.schema.json
completion_record.schema.json
```

## 7.4 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_tool_registry.py
test_tool_call_schema.py
test_tool_result_schema.py
test_tool_policy.py
test_tool_trust_tiers.py
test_tool_call_logger.py
test_invalid_tool.py
test_initiator_tools.py
test_security_tools.py
test_patch_tools.py
test_git_tools.py
test_human_tools.py
test_mcp_adapter.py
test_mcp_safe_deferred.py
test_tool_negative_cases.py
test_tool_mcp_schema_validation.py
```

## 7.5 Required Runtime Artifacts

Expected location:

```text
.agentx-init/tool_calls/
```

Expected artifacts:

```text
tool_call_history.jsonl
tool_result_history.jsonl
blocked_tool_history.jsonl
invalid_tool_history.jsonl
latest_tool_call.json
latest_tool_result.json
tool_mcp_adapter_evidence_manifest.json
tool_mcp_adapter_review_report.json
tool_mcp_adapter_completion_record.json
```

## 7.6 Required Validation Utility Files

Expected validation utility files:

```text
tools/agentx_evolve/tests/validate_tool_mcp_schemas.py
```

If this file is not present, the review must identify the exact pytest-based schema validation replacement and prove it covers all required valid and invalid schema cases.

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 8. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Tool package location | `tools/agentx_evolve/tools/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| MCP package location | `tools/agentx_evolve/mcp/` exists or is safely deferred | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Tool schemas | all required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation command | schema command or pytest equivalent exists and passes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool tests | required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Registry coverage | expected tools registered | PASS / PARTIAL / FAIL / NOT CHECKED |
| Permission coverage | role/effect/trust-tier rules enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| MCP coverage | read-only default, no auto server, no bypass | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Blocked tools | blocked tools return BLOCKED with evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Invalid tools | unknown/malformed tools return INVALID with evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Audit/evidence | JSONL + latest artifacts + evidence manifest + review report written safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence hashing | manifest, review report, and completion record hashes present | PASS / PARTIAL / FAIL / NOT CHECKED |
| Sandbox integration | path/file/command tools call sandbox | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy integration | all calls checked before execution | PASS / PARTIAL / FAIL / NOT CHECKED |
| Failure taxonomy | failure_class populated | PASS / PARTIAL / FAIL / NOT CHECKED |
| Patch integration | patch apply/rollback block until patch layer exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Initiator integration | wrappers exist and fail closed | PASS / PARTIAL / FAIL / NOT CHECKED |
| CLI command wrappers | no raw shell, allowlist enforced, output controlled | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Runtime artifact boundary | evidence only under approved runtime root or exception listed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | no direct source mutation | PASS / PARTIAL / FAIL / NOT CHECKED |
| OpenCode borrowing | concepts mapped safely, no OpenCode source copied | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 9. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Tool registry loads | `tool_registry.py` | `test_tool_registry.py` | evidence manifest | PASS / PARTIAL / FAIL / NOT CHECKED |
| Duplicate tools rejected | `tool_registry.py` | `test_tool_registry.py` | pytest output | PASS / PARTIAL / FAIL / NOT CHECKED |
| Permission check before execution | `tool_policy.py` | `test_tool_policy.py` | tool result history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Trust-tier enforcement | `tool_policy.py` | `test_tool_trust_tiers.py` | blocked tool history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Invalid tool handling | `invalid_tool.py` | `test_invalid_tool.py` | invalid tool history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Blocked tool handling | tool modules | `test_tool_negative_cases.py` | blocked tool history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Audit logging | `tool_call_logger.py` | `test_tool_call_logger.py` | JSONL histories | PASS / PARTIAL / FAIL / NOT CHECKED |
| MCP read-only exposure | `mcp_adapter.py` | `test_mcp_adapter.py` | MCP manifest | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| MCP safe deferral | `mcp_server.py` or absence proof | `test_mcp_safe_deferred.py` | deviation register + deferred MCP note | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Sandbox integration | `security_tools.py` | `test_security_tools.py` | tool result history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Patch stubs | `patch_tools.py` | `test_patch_tools.py` | blocked tool history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Git read-only tools | `git_tools.py` | `test_git_tools.py` | tool result history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Human review stub | `human_tools.py` | `test_human_tools.py` | tool result history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Review report | report writer or manual creation | schema/manual validation | review report JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record | completion writer | schema validation test | completion record JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 10. What Exists Checklist

## 10.1 Tool Package Files

```text
[ ] tools/agentx_evolve/tools/__init__.py
[ ] tools/agentx_evolve/tools/tool_models.py
[ ] tools/agentx_evolve/tools/tool_registry.py
[ ] tools/agentx_evolve/tools/tool_policy.py
[ ] tools/agentx_evolve/tools/tool_call_logger.py
[ ] tools/agentx_evolve/tools/initiator_tools.py
[ ] tools/agentx_evolve/tools/security_tools.py
[ ] tools/agentx_evolve/tools/patch_tools.py
[ ] tools/agentx_evolve/tools/git_tools.py
[ ] tools/agentx_evolve/tools/human_tools.py
[ ] tools/agentx_evolve/tools/invalid_tool.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.2 MCP Package Files

```text
[ ] tools/agentx_evolve/mcp/__init__.py
[ ] tools/agentx_evolve/mcp/mcp_models.py
[ ] tools/agentx_evolve/mcp/mcp_adapter.py
[ ] tools/agentx_evolve/mcp/mcp_server.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

## 10.3 Schema Files

```text
[ ] tool_registry.schema.json
[ ] tool_definition.schema.json
[ ] tool_call.schema.json
[ ] tool_result.schema.json
[ ] tool_permission_decision.schema.json
[ ] tool_policy.schema.json
[ ] tool_trust_tier.schema.json
[ ] mcp_tool_manifest.schema.json
[ ] invalid_tool_record.schema.json
[ ] tool_audit.schema.json
[ ] evidence_manifest.schema.json
[ ] review_report.schema.json
[ ] completion_record.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.4 Test Files

```text
[ ] test_tool_registry.py
[ ] test_tool_call_schema.py
[ ] test_tool_result_schema.py
[ ] test_tool_policy.py
[ ] test_tool_trust_tiers.py
[ ] test_tool_call_logger.py
[ ] test_invalid_tool.py
[ ] test_initiator_tools.py
[ ] test_security_tools.py
[ ] test_patch_tools.py
[ ] test_git_tools.py
[ ] test_human_tools.py
[ ] test_mcp_adapter.py
[ ] test_mcp_safe_deferred.py
[ ] test_tool_negative_cases.py
[ ] test_tool_mcp_schema_validation.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 11. Validation Commands

Run from a fresh checkout of the implementation commit.

Record the exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`. Any non-zero exit code is `FAIL` unless the command is explicitly a negative test where non-zero is the expected result and the expected failure condition is recorded.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_tool_mcp_schemas.py
git status --short
```

Required result:

```text
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
git status: CLEAN or only expected runtime artifacts
```

The primary pytest command may run the whole `tools/agentx_evolve/tests` suite. If unrelated future-layer tests exist in that directory, the review must also record a scoped Tool / MCP Adapter pytest command such as:

```bash
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_tool_registry.py \
  tools/agentx_evolve/tests/test_tool_call_schema.py \
  tools/agentx_evolve/tests/test_tool_result_schema.py \
  tools/agentx_evolve/tests/test_tool_policy.py \
  tools/agentx_evolve/tests/test_tool_trust_tiers.py \
  tools/agentx_evolve/tests/test_tool_call_logger.py \
  tools/agentx_evolve/tests/test_invalid_tool.py \
  tools/agentx_evolve/tests/test_initiator_tools.py \
  tools/agentx_evolve/tests/test_security_tools.py \
  tools/agentx_evolve/tests/test_patch_tools.py \
  tools/agentx_evolve/tests/test_git_tools.py \
  tools/agentx_evolve/tests/test_human_tools.py \
  tools/agentx_evolve/tests/test_mcp_adapter.py \
  tools/agentx_evolve/tests/test_mcp_safe_deferred.py \
  tools/agentx_evolve/tests/test_tool_negative_cases.py \
  tools/agentx_evolve/tests/test_tool_mcp_schema_validation.py
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
```

---

# 12. Compileall Result

Record the compile result.

```text
command: PYTHONPATH=tools python -m compileall tools/agentx_evolve
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any Tool / MCP Adapter Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 13. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: <path>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required tool registry, permission, MCP, blocked-tool, invalid-tool, schema, evidence, command-wrapper, or integration test fails
exit code is missing
```

---

# 14. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_tool_mcp_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_tool_mcp_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
```

Required schema tests:

```text
tool registry schema accepts valid registry
tool definition schema accepts valid definition
tool call schema accepts valid call
tool call schema rejects missing tool_name
tool call schema rejects unknown effect values
tool result schema accepts SUCCESS result
tool result schema accepts BLOCKED result
tool result schema accepts INVALID result
tool permission decision schema accepts valid decision
tool policy schema accepts valid policy
trust-tier schema accepts valid trust tiers
MCP manifest schema accepts valid read-only manifest
MCP manifest schema rejects default mutating exposure
invalid tool record schema accepts valid invalid-tool record
tool audit schema accepts valid event
evidence manifest schema accepts valid evidence manifest
review report schema accepts valid review report
completion record schema accepts final completion record
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
schema-invalid calls are accepted
schema-invalid results are accepted
tool result schema cannot represent BLOCKED or INVALID outcomes
MCP manifest schema cannot represent blocked/hidden tools
evidence manifest cannot be schema-validated
review report cannot be schema-validated
completion record cannot be schema-validated
schema validation exit code is missing
```

---

# 15. Tool Registry Coverage

Required registry coverage:

```text
[ ] default registry loads
[ ] registry is deterministic
[ ] duplicate tool names are rejected
[ ] tool names are stable and canonical
[ ] expected Initiator wrapper tools are registered
[ ] expected Security Sandbox wrapper tools are registered
[ ] patch tools are registered as stubs or implemented safely
[ ] Git read-only tools are registered
[ ] Git write tools are disabled or blocked
[ ] ask_human is registered as safe stub if not implemented
[ ] invalid_tool_handler is registered or available as fallback
[ ] every registered tool has schema metadata
[ ] every registered tool has effect metadata
[ ] every registered tool has trust-tier metadata
[ ] every registered tool has audit behavior metadata
```

Required Agent_X-safe OpenCode-style primitives covered:

```text
[ ] read_file_guarded
[ ] list_files_guarded
[ ] search_files_guarded
[ ] write_file_guarded
[ ] edit_file_guarded
[ ] patch_apply_guarded or patch_precheck_guarded
[ ] run_allowlisted_command
[ ] invalid_tool_handler
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 16. Tool Permission Coverage

Required permission behavior:

```text
[ ] UNKNOWN_CALLER blocks by default
[ ] MCP_CLIENT has least privilege by default
[ ] IMPLEMENTATION_WORKER cannot directly write files
[ ] REVIEWER_ASSISTANT is read-only
[ ] PROMOTION_CHECKER can inspect Git but cannot push/merge
[ ] HUMAN_OPERATOR cannot override non-overridable safety blocks
[ ] ORCHESTRATOR cannot bypass sandbox/policy
[ ] blocked trust tier always blocks
[ ] source-write tools require sandbox and policy
[ ] governance-required tools return NEEDS_GOVERNANCE when governance ID missing
[ ] approval-required tools return NEEDS_APPROVAL when approval ID missing
[ ] missing caller role fails closed
[ ] missing tool effect fails closed
[ ] missing trust tier fails closed
[ ] unknown effect fails closed
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
unknown caller can execute a tool
mutating tool executes without policy check
source-write tool bypasses sandbox
blocked trust tier can execute
missing permission metadata defaults open
```

---

# 17. MCP Exposure Coverage

Required MCP behavior if MCP files/runtime are implemented:

```text
[ ] MCP manifest builds without starting server
[ ] MCP server does not start on import
[ ] MCP opens no network port by default
[ ] MCP exposes read-only tools only by default
[ ] MCP does not expose write_file_guarded by default
[ ] MCP does not expose edit_file_guarded by default
[ ] MCP does not expose patch_apply_guarded by default
[ ] MCP does not expose run_allowlisted_command by default
[ ] MCP does not expose Git write tools by default
[ ] MCP requests cannot bypass policy
[ ] MCP requests cannot bypass sandbox
[ ] invalid MCP request returns schema-valid INVALID or BLOCKED result
[ ] MCP-visible tool list is generated from registry allowlist, not hard-coded unsafe exposure
[ ] MCP manifest records hidden/blocked mutating tools as hidden or unavailable
```

If MCP is intentionally deferred, the review must confirm:

```text
[ ] MCP files are absent or safe stubs by design
[ ] no MCP server starts
[ ] no MCP network port opens
[ ] no mutating MCP exposure exists
[ ] no MCP command starts automatically
[ ] no external MCP dependency is required for tests
[ ] deferred MCP status is recorded in deviations or unresolved future work
[ ] safe deferral is proven by test_mcp_safe_deferred.py or equivalent
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

Blocking if MCP is implemented and:

```text
mutating tools are exposed by default
MCP bypasses policy
MCP bypasses sandbox
server starts automatically
network port opens by default
MCP tests require external runtime
```

---

# 18. CLI / Command Wrapper Coverage

This section applies if the layer exposes CLI-accessible tools or command wrappers.

Required behavior:

```text
[ ] command wrapper uses allowlist
[ ] command wrapper does not use raw shell by default
[ ] command wrapper rejects shell metacharacter injection
[ ] command wrapper rejects unknown commands
[ ] command wrapper rejects network commands by default
[ ] command wrapper rejects Git write commands by default
[ ] command wrapper captures bounded stdout/stderr
[ ] command wrapper redacts secrets before evidence writing
[ ] command wrapper records command, decision, and result
[ ] command wrapper returns schema-valid BLOCKED for denied commands
[ ] command wrapper returns schema-valid INVALID for malformed command calls
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
raw shell executes
unknown command executes
network command executes by default
Git write command executes in v1
command output is logged without redaction or bounds
```

---

# 19. Blocked-Tool Coverage

Required blocked-tool behavior:

```text
[ ] disabled tools return BLOCKED
[ ] trust tier 6 tools return BLOCKED
[ ] Git write tools return BLOCKED in v1
[ ] patch apply returns BLOCKED until Governed Patch Execution exists
[ ] rollback returns BLOCKED until Governed Patch Execution exists
[ ] network tools return BLOCKED by default
[ ] subprocess tools return BLOCKED unless allowlisted and policy-approved
[ ] blocked tools write evidence
[ ] blocked tools include failure_class
[ ] blocked tools include denial reason
[ ] blocked tools do not mutate source or runtime state except allowed evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
blocked tools throw unhandled exceptions
blocked tools silently do nothing without evidence
blocked tools execute anyway
blocked tools mutate source
```

---

# 20. Invalid-Tool Coverage

Required invalid-tool behavior:

```text
[ ] unknown tool name returns INVALID
[ ] malformed tool call returns INVALID
[ ] invalid tool result validates against tool_result.schema.json
[ ] invalid tool record writes to invalid_tool_history.jsonl
[ ] invalid tool does not execute fallback shell
[ ] invalid tool does not guess intended command
[ ] invalid tool does not call model/network
[ ] invalid tool includes failure_class TOOL_NOT_FOUND or TOOL_SCHEMA_INVALID
[ ] invalid tool includes original tool_name only if safe to log
[ ] invalid tool result redacts suspicious payload fields
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
unknown tools execute
unknown tools raise unhandled exceptions
invalid tools lack evidence
invalid tool handler guesses and executes a substitute command
```

---

# 21. Audit / Evidence Coverage

Required evidence behavior:

```text
[ ] tool_call_history.jsonl is written
[ ] tool_result_history.jsonl is written
[ ] blocked_tool_history.jsonl is written for blocked tools
[ ] invalid_tool_history.jsonl is written for invalid tools
[ ] latest_tool_call.json is written atomically
[ ] latest_tool_result.json is written atomically
[ ] tool_mcp_adapter_evidence_manifest.json is written
[ ] tool_mcp_adapter_review_report.json is written
[ ] completion record is written after validation
[ ] evidence includes timestamps
[ ] evidence includes reviewed commit
[ ] evidence includes command text, exit codes, statuses, and summaries
[ ] evidence includes schema validation summary
[ ] evidence includes hashes for final evidence artifacts
[ ] secrets are redacted before logging
[ ] raw file content is not durably logged by read tools
[ ] unredacted command output is not durably logged
[ ] schema-invalid result does not replace valid latest result
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
tool calls are not logged
tool results are not logged
blocked/invalid calls are not evidenced
secrets are logged
latest artifacts are written unsafely
evidence has no reviewed commit reference
required hashes are missing
```

---

# 22. Evidence Manifest

Create:

```text
.agentx-init/tool_calls/tool_mcp_adapter_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "evidence_manifest.schema.json",
  "component_id": "AGENTX_TOOL_MCP_ADAPTER",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "commands": [
    {
      "name": "compileall",
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>"
    },
    {
      "name": "pytest",
      "command": "PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>"
    },
    {
      "name": "schema_validation",
      "command": "<schema validation command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>"
    }
  ],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "mcp_status": "PASS_OR_DEFERRED_SAFELY",
  "blocked_invalid_status": "PASS",
  "redaction_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

The manifest must include paths and hashes for all final evidence files, including:

```text
tool_mcp_adapter_evidence_manifest.json
tool_mcp_adapter_review_report.json
tool_mcp_adapter_completion_record.json
command output artifacts, if stored as files
JSONL evidence histories used by the review
latest_tool_call.json, if used by the review
latest_tool_result.json, if used by the review
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Approved runtime artifact boundary:

```text
.agentx-init/tool_calls/
```

Evidence artifacts for this layer must not be written outside that root unless the review records the exception in the deviation register. Unapproved evidence writes outside the runtime root are a source-mutation or artifact-boundary failure.

---

# 23. Review Report Artifact

Create:

```text
.agentx-init/tool_calls/tool_mcp_adapter_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "review_report.schema.json",
  "component_id": "AGENTX_TOOL_MCP_ADAPTER",
  "review_document_id": "TOOL_MCP_ADAPTER_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v5.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [
    {
      "name": "compileall",
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    }
  ],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/tool_calls/tool_mcp_adapter_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/tool_calls/tool_mcp_adapter_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/tool_calls/tool_mcp_adapter_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is the bridge between this template and the implementation. A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, or if it lacks command exit codes.

## 23.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

---

# 24. Integration Coverage

## 24.1 Security Sandbox Integration

```text
[ ] read_file_guarded calls Security Sandbox
[ ] list_files_guarded calls Security Sandbox
[ ] search_files_guarded calls Security Sandbox
[ ] write_file_guarded calls Security Sandbox
[ ] edit_file_guarded calls Security Sandbox
[ ] patch_precheck_guarded calls Security Sandbox
[ ] run_allowlisted_command calls Security Sandbox
[ ] sandbox-denied tools return TOOL_SANDBOX_DENIED
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 24.2 Policy / Capability Registry Integration

```text
[ ] every tool call checks policy before execution
[ ] missing policy fails closed or restrictive local fallback is used
[ ] policy-denied tools return TOOL_POLICY_DENIED
[ ] mutating tools block when policy is unavailable
[ ] policy decisions are evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 24.3 Failure Taxonomy Integration

```text
[ ] failed results have failure_class
[ ] blocked results have failure_class where applicable
[ ] invalid results have TOOL_NOT_FOUND or TOOL_SCHEMA_INVALID
[ ] sandbox denials map to TOOL_SANDBOX_DENIED
[ ] policy denials map to TOOL_POLICY_DENIED
[ ] command denials map to TOOL_COMMAND_DENIED
[ ] MCP denials map to TOOL_MCP_EXPOSURE_DENIED
[ ] unknown failures map to UNKNOWN_TOOL_FAILURE
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 24.4 Governed Patch Execution Integration

```text
[ ] patch tools are stubs if patch layer is not implemented
[ ] patch_apply_guarded blocks until patch layer exists
[ ] rollback_session blocks until patch layer exists
[ ] patch_precheck_guarded may call sandbox
[ ] patch session status is read-only if implemented
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 24.5 Initiator Integration

```text
[ ] agentx_scan wrapper exists
[ ] agentx_status wrapper exists
[ ] agentx_plan wrapper exists
[ ] agentx_propose wrapper exists
[ ] agentx_validate wrapper exists
[ ] Initiator wrappers do not modify Initiator source
[ ] wrapper failures return schema-valid ToolResult
[ ] wrapper calls are logged
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 25. Negative Test Pack

The review must prove that forbidden actions fail closed.

Required negative cases:

```text
[ ] unknown tool name -> INVALID
[ ] malformed tool call -> INVALID
[ ] missing caller role -> BLOCKED or INVALID
[ ] unknown caller role -> BLOCKED
[ ] blocked trust tier -> BLOCKED
[ ] write tool without policy approval -> BLOCKED
[ ] write tool without sandbox approval -> BLOCKED
[ ] patch apply before patch layer -> BLOCKED
[ ] rollback before patch layer -> BLOCKED
[ ] Git push/merge command -> BLOCKED
[ ] raw shell command -> BLOCKED
[ ] network command -> BLOCKED
[ ] MCP mutating tool default exposure -> BLOCKED or hidden
[ ] MCP server import -> no server start
[ ] secret-like payload -> redacted in evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked as non-applicable with justification.

---

# 26. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <MCP | CLI | Evidence | Schema | Runtime Artifact Boundary | Other>
    description: <what differs from the contract>
    reason: <why accepted>
    safety_impact: <none | low | medium | high>
    compensating_control: <test/evidence/control>
    accepted_status: NOT APPLICABLE | DEFERRED SAFELY | NON-BLOCKING FOLLOW-UP
    reviewer_decision: ACCEPTED | REJECTED
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
HIGH items cannot be accepted for DONE unless the review explicitly proves they are not part of the active runtime path.
Runtime artifact writes outside `.agentx-init/tool_calls/` require a deviation entry.
MCP deferral requires a deviation entry.
Missing evidence hashes cannot be accepted as a deviation for DONE.
```

---

# 27. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
tool registry:
tool permission:
MCP exposure:
CLI / command wrappers:
blocked tools:
invalid tools:
audit/evidence:
evidence manifest:
review report:
evidence hashes:
integration:
negative tests:
source mutation check:
completion record:
```

---

# 28. What Failed

Fill after validation.

```text
failures:
  - <none or list>
blocking_failures:
  - <none or list>
high_priority_failures:
  - <none or list>
non_blocking_failures:
  - <none or list>
rejected_deviations:
  - <none or list>
```

---

# 29. Issue Severity Classification

Use these severity levels.

## 29.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
unknown tool executes
blocked tool executes
MCP exposes mutating tools by default
MCP starts server automatically
MCP opens network port by default
source mutation occurs directly in this layer
Git write tool is enabled in v1
network tool is enabled by default
raw shell executes without allowlist
command injection is possible
secrets are logged
tool calls/results lack evidence
evidence lacks reviewed commit
evidence hashes are missing
review report is missing
completion record is missing
required area remains NOT CHECKED
```

## 29.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
incomplete evidence references
partial Initiator wrapper coverage
partial Failure Taxonomy mapping
MCP deferred without explicit deviation entry
some expected tool wrappers missing but not yet used
runtime artifact boundary exception lacks justification
review environment not recorded
```

## 29.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled tool definitions
MCP server intentionally stubbed with safe-deferral proof
human review tool intentionally stubbed
patch tools intentionally stubbed until patch layer exists
additional future-layer tests exist outside scoped Tool / MCP Adapter suite
```

---

# 30. Source Mutation Check

Required command:

```bash
git status --short
```

Expected:

```text
clean working tree
```

or:

```text
only expected runtime artifacts under .agentx-init/tool_calls/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by tests
Initiator source is modified
unapproved files are created outside runtime artifact paths
runtime artifacts are written outside approved runtime roots
evidence artifacts are written outside `.agentx-init/tool_calls/` without recorded deviation
```

---

# 31. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Tool, schema, test, runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, and completion record. |
| Registry coverage | 1.0 | Expected tools registered, duplicates rejected, metadata complete. |
| Permission / trust-tier coverage | 1.0 | Role, effect, trust-tier, policy, governance, approval checks fail closed. |
| MCP exposure safety | 1.0 | Read-only by default or safely deferred, no server/port/mutating exposure. |
| Blocked / invalid behavior | 1.0 | BLOCKED and INVALID outcomes are schema-valid, evidenced, and non-mutating. |
| Audit / evidence | 1.0 | JSONL histories, latest artifacts, evidence manifest, review report, hashes, redaction, completion record. |
| Integration and source-mutation safety | 1.0 | Sandbox, policy, failure taxonomy, patch, Initiator, CLI safety, clean git status. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for controlled tool execution
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
MCP unsafe exposure caps score at 4.0
unknown or blocked tool executes caps score at 4.0
raw shell executes caps score at 4.0
secrets logged caps score at 4.0
source mutation by tests caps score at 7.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
```

---

# 32. GO / NO-GO Rules

## 32.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
tool registry tests pass
tool permission tests pass
blocked tool tests pass
invalid tool tests pass
audit/evidence tests pass
evidence manifest exists
evidence hashes exist
review report exists
MCP exposure tests pass or MCP is deferred safely with no runtime exposure
CLI / command wrapper tests pass or are not applicable
negative tests pass
source mutation check passes
completion record exists
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 32.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
unknown tool executes
blocked tool executes
mutating tool bypasses policy
mutating tool bypasses sandbox
MCP exposes mutating tools by default
MCP starts server or opens network port by default
Git write tool is enabled in v1
network tool is enabled by default
raw shell executes without allowlist
secrets are logged
tool calls/results lack evidence
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 33. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix registry entries
fix permission checks
fix MCP filtering
fix blocked-tool result formatting
fix invalid-tool result formatting
fix evidence writing
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix secret redaction
fix tests to reflect the contract
fix command allowlist enforcement
fix missing failure_class mapping
fix runtime artifact boundary checks
```

Forbidden fixes:

```text
do not remove policy checks to pass tests
do not remove sandbox checks to pass tests
do not enable source writes by default
do not expose mutating MCP tools by default
do not enable Git writes in v1
do not enable network by default
do not execute raw shell to satisfy command wrappers
do not skip evidence writing
do not omit hashes for final DONE
do not log secrets
do not copy OpenCode source code
do not add Bun/Node/OpenCode runtime dependency
do not mark NOT CHECKED as PASS
do not mark unsafe MCP deferral as DEFERRED SAFELY
do not accept a BLOCKER as a deviation
```

---

# 34. Definition of Done

The Tool / MCP Adapter Layer is done when it can act as the controlled tool interface for Agent_X.

It must prove:

```text
all target files exist or explicit safe deferral is documented
all schemas exist
all tests exist
registered tools are discoverable
unknown tools fail closed
blocked tools fail closed
tool calls validate against schema
tool results validate against schema
tool trust tiers enforce access
tool permission checks run before execution
sandbox checks run before path/file/command operations
MCP exposure is read-only by default or safely deferred with no runtime exposure
CLI command wrappers are allowlisted and fail closed
tool call evidence is written
tool result evidence is written
blocked tool evidence is written
invalid tool evidence is written
evidence manifest is written
review report is written
evidence hashes are written
review environment is recorded
no source mutation occurs directly in this layer
no network is enabled by default
no Git write is enabled by default
no raw shell is executed without allowlist
completion record exists
final verdict is recorded
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_tool_mcp_schemas.py
git status --short
```

Expected:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

---

# 35. Required Evidence Package

The completion evidence package must include:

```text
compileall output
pytest output
schema validation result
tool registry test result
tool permission test result
MCP exposure test result or safe-deferred note
CLI / command wrapper test result or N/A note
blocked-tool test result
invalid-tool test result
negative-test result
audit/evidence test result
evidence manifest
review report
git status output
completion record
SHA-256 hashes for final evidence artifacts
```

The evidence package must show:

```text
reviewed commit
validation timestamp
review environment
command exit codes
no source mutation
no network by default
no Git write in v1
no mutating MCP exposure by default
no raw shell
blocked and invalid tools fail closed
secrets redacted
hashes for final evidence artifacts
```

---

# 36. Completion Evidence Record

After validation, create:

```text
.agentx-init/tool_calls/tool_mcp_adapter_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_TOOL_MCP_ADAPTER",
  "component_name": "Tool / MCP Adapter Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "canonical_tool_subdirectory": "tools/agentx_evolve/tools/",
  "canonical_mcp_subdirectory": "tools/agentx_evolve/mcp/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/tool_calls/",
  "basis_documents": [
    "TOOL_MCP_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT_v1",
    "TOOL_MCP_ADAPTER_IMPLEMENTATION_SPEC_v1",
    "TOOL_MCP_ADAPTER_IMPLEMENTATION_REVIEW_AND_DOD_v5"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "tool_registry_entries_verified": [],
  "mcp_exposure_verified": [],
  "cli_command_wrappers_verified": [],
  "policy_integration_verified": [],
  "sandbox_integration_verified": [],
  "failure_taxonomy_integration_verified": [],
  "governed_patch_integration_verified": [],
  "opencode_patterns_borrowed": [],
  "opencode_patterns_rejected_or_restricted": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/tool_calls/tool_mcp_adapter_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/tool_calls/tool_mcp_adapter_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 37. Final Done / Not-Done Verdict

Fill after validation.

```text
final_verdict: DONE | NOT DONE
implementation_rating: <0-10>
review_document_rating: 10/10
reason:
  - <summary>
remaining_blockers:
  - <none or list>
remaining_high_issues:
  - <none or list>
accepted_non_blocking_followups:
  - <none or list>
accepted_deviations:
  - <none or list>
```

A final verdict of `DONE` is invalid if:

```text
implementation_rating is below 10.0
reviewed commit is missing
review environment is missing
any required command was not run
any required command exit code is missing
any required area is NOT CHECKED
any required command is NOT RUN
any BLOCKER remains
evidence hashes are missing
review report is missing
completion record is missing
```

---

# 38. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/tools/ exists
[ ] tools/agentx_evolve/mcp/ exists or MCP intentionally deferred safely
[ ] schemas exist
[ ] tests exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Registry:
[ ] default registry loads
[ ] expected tools registered
[ ] duplicate tools rejected
[ ] tool metadata complete

Permissions:
[ ] unknown caller blocked
[ ] blocked trust tier blocked
[ ] mutating tools require policy
[ ] source tools require sandbox
[ ] missing metadata fails closed

MCP:
[ ] MCP read-only by default or safely deferred
[ ] MCP mutating tools blocked or hidden by default
[ ] MCP does not start server automatically
[ ] MCP opens no network port by default

CLI / Commands:
[ ] command wrappers use allowlist or are N/A
[ ] raw shell blocked
[ ] network commands blocked by default
[ ] Git write commands blocked in v1

Blocked / Invalid:
[ ] unknown tool returns INVALID
[ ] blocked tool returns BLOCKED
[ ] blocked/invalid calls write evidence
[ ] blocked/invalid outcomes are schema-valid

Evidence:
[ ] tool call history written
[ ] tool result history written
[ ] blocked tool history written
[ ] invalid tool history written
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written
[ ] secrets redacted

Safety:
[ ] no source mutation directly in this layer
[ ] no network by default
[ ] no Git write in v1
[ ] no raw shell
[ ] no OpenCode runtime dependency

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 39. Final Sign-Off Template

Use this after implementation validation.

```text
Tool / MCP Adapter Validation — Commit <hash>

Reviewer / Environment:
- reviewer: <name or tool>
- reviewed commit: <hash>
- reviewed branch: <branch>
- reviewed at UTC: <timestamp>
- OS: <name/version>
- Python: <version>
- pytest: <version or NOT INSTALLED>

Status:
- initial git status: CLEAN/EXPECTED_RUNTIME_ARTIFACTS_ONLY/DIRTY
- compileall: PASS/FAIL, exit_code=<code>
- pytest: PASS/FAIL, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- tool registry coverage: PASS/FAIL
- tool permission coverage: PASS/FAIL
- MCP exposure coverage: PASS/FAIL/DEFERRED SAFELY
- CLI / command wrapper coverage: PASS/FAIL/N/A
- blocked-tool coverage: PASS/FAIL
- invalid-tool coverage: PASS/FAIL
- negative-test coverage: PASS/FAIL
- audit/evidence coverage: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- review report: PRESENT/MISSING
- source mutation check: PASS/FAIL
- completion record: PRESENT/MISSING

Reproducibility:
- exact commands recorded: YES/NO
- exit codes recorded: YES/NO
- output artifacts recorded: YES/NO
- final hashes recorded: YES/NO
- deviations recorded: YES/NO/N/A

Final decision:
DONE / NOT DONE

Implementation rating:
<0-10>

Evidence paths:
- evidence manifest: <path>, sha256=<hash>
- review report: <path>, sha256=<hash>
- completion record: <path>, sha256=<hash>

Remaining blockers:
- none / list blockers

Accepted non-blocking follow-ups:
- none / list follow-ups
```

---

# 40. Final Rating

This v5 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the strong v4 coverage and fixes the remaining precision gaps: normal section numbering, duplicate NO-GO cleanup, explicit exit-code recording for all required commands, strict SHA-256 evidence hashing, evidence immutability, deviation-register requirements, clearer MCP safe-deferral rules, stronger hard score caps, and a final reproducibility sign-off that prevents DONE from being claimed without reviewed commit, command evidence, hashes, review report, and completion record.
```
