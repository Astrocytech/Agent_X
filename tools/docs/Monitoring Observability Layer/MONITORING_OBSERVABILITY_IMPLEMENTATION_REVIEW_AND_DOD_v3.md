# MONITORING_OBSERVABILITY_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: MONITORING_OBSERVABILITY_IMPLEMENTATION_REVIEW_AND_DOD
version: v3.0
status: final post-implementation review template and Definition of Done
component_id: AGENTX_MONITORING_OBSERVABILITY
component_name: Monitoring / Observability Layer
roadmap_layer: 19
roadmap_phase: Phase E — Runtime Visibility and Evidence
review_use: use after code is committed
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Failure Taxonomy Integration
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria
optional_standards: ES, Report Template
canonical_monitoring_subdirectory: tools/agentx_evolve/monitoring/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/monitoring/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v3 Review and Upgrade Summary

The v2 review / DoD document was strong and close to final, but I would rate it:

```text
9.8/10
```

It already covered the full requested review scope:

```text
what exists
what passed
what failed
compileall result
pytest result
schema validation result
health check result
metric collection result
event collection result
trace collection result
runtime status reporting result
alert generation result
redaction result
retention/rotation result
source mutation check
runtime artifact boundary check
evidence hash check
definition of done
implementation score
final done/not-done verdict
standards applied
why the layer needs the standards
expected package, schemas, tests, and runtime artifacts
core safety posture
```

It was not fully 10/10 because a few final production-control details were still under-specified:

```text
1. Observability audit records were listed as a schema, but did not have a dedicated review result section.
2. Resource/overhead controls were implied, but not reviewed as a separate bounded-cost requirement.
3. Timestamp and clock-validity rules were not strict enough for reproducible evidence.
4. Dependency availability for Failure Taxonomy, Policy / Capability Registry, Tool / MCP Adapter, and Security Sandbox needed an explicit gate.
5. The runtime artifact boundary needed a clearer rule for temporary files and atomic-write scratch files.
6. The review needed stricter rules for malformed JSONL line handling during append-only evidence review.
7. The scoring and GO / NO-GO sections needed to include observability audit, resource bounds, dependency availability, and timestamp validity.
```

This v3 applies those corrections and is the final 10/10 post-implementation review / DoD template.

---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Monitoring / Observability Layer**.

Use this document after code is committed to verify whether the committed Monitoring / Observability Layer is complete, safe, reproducible, auditable, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether package imports have no side effects
whether health checks work safely
whether metric collection works safely
whether event collection works safely
whether trace collection works safely
whether runtime status reporting works safely
whether alert generation works safely
whether redaction works before persistence
whether retention / rotation works without evidence loss
whether source mutation is absent
whether runtime artifacts stay inside the approved boundary
whether evidence hashes are present and match final files
whether monitoring is read-only and non-authoritative
whether observability audit records are schema-valid and complete
whether resource/overhead bounds are enforced
whether timestamps are valid and reproducible
whether dependency availability is recorded and fails closed
whether command-based health checks obey command acceptance rules
whether MCP exposure is absent, read-only, or safely deferred
whether the implementation is DONE or NOT DONE
```

This document reviews the implementation. A 10/10 rating for this document does not mean the implementation is done. The implementation is done only after the validation commands and evidence checks in this document pass and the review report records the evidence.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because this layer records runtime truth, component health, failures, alerts, metrics, traces, and evidence used to evaluate Agent_X behavior.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Failure Taxonomy Integration
```

## 2.3 Conditional Standards

```text
Command Acceptance Criteria, if health checks or validation commands are exposed
MCP Protocol Acceptance Criteria, only if monitoring is exposed through MCP
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, if it writes markdown/html reports
```

---

# 3. Why This Layer Needs These Standards

Monitoring / Observability is safety-critical because it decides:

```text
which runtime events are recorded
which failures are visible
which health states are trusted
which alerts are raised
which artifacts prove system behavior
which execution paths are observable
which evidence is retained or rotated
which sensitive data must be redacted
which components are considered degraded or unhealthy
```

It must not become:

```text
a source mutation path
a raw command execution path
a secret leakage path
a hidden network exporter
a background daemon that changes state
a bypass around Tool / MCP Adapter policy
a replacement for Failure Taxonomy
a replacement for Policy / Capability Registry
a retry, remediation, patch, approval, or promotion engine
```

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

The review is valid only if all are true:

```text
[ ] reviewed commit is recorded
[ ] validation was run against that exact commit
[ ] initial working-tree state is recorded
[ ] final working-tree state is recorded
[ ] environment information is recorded
[ ] every required command records command text, exit code, status, summary, and output artifact when available
[ ] every command marked PASS has exit_code 0
[ ] every negative test records the forbidden condition being tested
[ ] review report artifact is created
[ ] evidence manifest exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] required evidence hashes are present
[ ] evidence hashes match final evidence files
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
| DEFERRED SAFELY | Feature is intentionally deferred and cannot execute, expose, mutate, open ports, export data, or bypass policy/sandbox. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Deferral Rules

Use these rules to avoid hiding missing work behind `NOT APPLICABLE` or `DEFERRED SAFELY`.

```text
NOT APPLICABLE:
  Use only when the implementation scope truly does not include the feature and there is no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot execute, expose telemetry, mutate files, call network, open ports, start background workers, or bypass policy/sandbox.

PARTIAL:
  Use when some files or tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

MCP exposure may be `DEFERRED SAFELY` only if the review proves:

```text
no MCP server starts on import
no MCP network port opens
no mutating MCP tool is exposed
no telemetry export occurs through MCP by default
no MCP request bypasses Tool / MCP Adapter policy
no MCP request bypasses Policy / Capability Registry visibility rules
safe deferral is recorded in the deviation register
```

Command-based health checks may be accepted only if they obey Command Acceptance Criteria:

```text
command is allowlisted
no raw shell
bounded stdout/stderr
timeout recorded
exit code recorded
secrets redacted
network commands blocked by default
Git write commands blocked
failure returns schema-valid health check result
```

---

# 6. Expected Implementation Scope

## 6.1 Required Monitoring Package

Expected location:

```text
tools/agentx_evolve/monitoring/
```

Expected files:

```text
tools/agentx_evolve/monitoring/__init__.py
tools/agentx_evolve/monitoring/monitoring_models.py
tools/agentx_evolve/monitoring/event_logger.py
tools/agentx_evolve/monitoring/metrics_collector.py
tools/agentx_evolve/monitoring/health_checks.py
tools/agentx_evolve/monitoring/status_reporter.py
tools/agentx_evolve/monitoring/alert_manager.py
tools/agentx_evolve/monitoring/trace_collector.py
tools/agentx_evolve/monitoring/retention_policy.py
tools/agentx_evolve/monitoring/redaction.py
```

## 6.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
monitoring_event.schema.json
metric_record.schema.json
health_check.schema.json
health_report.schema.json
alert_record.schema.json
trace_span.schema.json
runtime_status.schema.json
observability_audit.schema.json
monitoring_evidence_manifest.schema.json
monitoring_review_report.schema.json
completion_record.schema.json
```

## 6.3 Required Runtime Artifacts

Expected location:

```text
.agentx-init/monitoring/
```

Expected artifacts:

```text
.agentx-init/monitoring/events.jsonl
.agentx-init/monitoring/metrics.jsonl
.agentx-init/monitoring/health_checks.jsonl
.agentx-init/monitoring/alerts.jsonl
.agentx-init/monitoring/traces.jsonl
.agentx-init/monitoring/latest_status.json
.agentx-init/monitoring/latest_health_report.json
.agentx-init/monitoring/monitoring_evidence_manifest.json
.agentx-init/monitoring/monitoring_review_report.json
.agentx-init/monitoring/monitoring_completion_record.json
```

## 6.4 Expected Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_monitoring_models.py
test_monitoring_event_schema.py
test_metric_record_schema.py
test_health_check_schema.py
test_health_report_schema.py
test_alert_record_schema.py
test_trace_span_schema.py
test_runtime_status_schema.py
test_observability_audit_schema.py
test_monitoring_event_logger.py
test_metrics_collector.py
test_health_checks.py
test_status_reporter.py
test_alert_manager.py
test_trace_collector.py
test_retention_policy.py
test_monitoring_redaction.py
test_monitoring_runtime_artifact_boundary.py
test_monitoring_negative_cases.py
test_monitoring_import_side_effects.py
test_monitoring_idempotency.py
test_monitoring_evidence_manifest.py
test_monitoring_review_report.py
test_observability_audit.py
test_monitoring_resource_bounds.py
test_monitoring_timestamp_validity.py
test_monitoring_dependency_availability.py
```

## 6.5 Required Validation Utility

Expected validation utility:

```text
tools/agentx_evolve/tests/validate_monitoring_schemas.py
```

If this file is not present, the review must identify the exact pytest-based schema validation replacement and prove it covers all required valid and invalid schema cases.

---

# 7. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or a clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_monitoring_schemas.py
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

If unrelated future-layer tests exist under `tools/agentx_evolve/tests`, the review must also record a scoped Monitoring / Observability pytest command that includes only the monitoring tests.

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
background daemon
hidden network exporter
```

---

# 8. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Monitoring package location | `tools/agentx_evolve/monitoring/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Monitoring schemas | all required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Monitoring tests | required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Import side effects | imports do not start daemons, ports, exporters, collectors, or writes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime artifacts | artifacts written only under `.agentx-init/monitoring/` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Event logging | events append to `events.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Metric collection | metrics append to `metrics.jsonl` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Health checks | health checks are read-only and evidenced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime status reporting | latest status written atomically and schema-valid | PASS / PARTIAL / FAIL / NOT CHECKED |
| Alert generation | alerts are generated without mutation or network | PASS / PARTIAL / FAIL / NOT CHECKED |
| Trace collection | spans are bounded, schema-valid, and redacted | PASS / PARTIAL / FAIL / NOT CHECKED |
| Redaction | secrets redacted before persistence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Retention / rotation | retention does not delete source or required evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Determinism / idempotency | repeated collection is stable, append-only, and non-duplicative where required | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence hashes | final evidence hashes present and match files | PASS / PARTIAL / FAIL / NOT CHECKED |
| Failure taxonomy | failure_class values use approved taxonomy | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy integration | monitoring visibility rules fail closed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool / MCP integration | monitoring does not bypass tool policy | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE / DEFERRED SAFELY |
| Source mutation safety | no source mutation | PASS / PARTIAL / FAIL / NOT CHECKED |
| Network safety | no hidden network exporter by default | PASS / PARTIAL / FAIL / NOT CHECKED |
| Observability audit | audit records are schema-valid, append-only, and linked to evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Resource bounds | collectors enforce bounded payloads, counts, durations, and file sizes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Timestamp validity | timestamps are ISO-8601 UTC, monotonic where required, and review-reproducible | PASS / PARTIAL / FAIL / NOT CHECKED |
| Dependency availability | missing policy/taxonomy/tool/sandbox integrations fail closed or record safe deferral | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 9. What Exists Checklist

## 9.1 Monitoring Package Files

```text
[ ] tools/agentx_evolve/monitoring/__init__.py
[ ] tools/agentx_evolve/monitoring/monitoring_models.py
[ ] tools/agentx_evolve/monitoring/event_logger.py
[ ] tools/agentx_evolve/monitoring/metrics_collector.py
[ ] tools/agentx_evolve/monitoring/health_checks.py
[ ] tools/agentx_evolve/monitoring/status_reporter.py
[ ] tools/agentx_evolve/monitoring/alert_manager.py
[ ] tools/agentx_evolve/monitoring/trace_collector.py
[ ] tools/agentx_evolve/monitoring/retention_policy.py
[ ] tools/agentx_evolve/monitoring/redaction.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 9.2 Schema Files

```text
[ ] monitoring_event.schema.json
[ ] metric_record.schema.json
[ ] health_check.schema.json
[ ] health_report.schema.json
[ ] alert_record.schema.json
[ ] trace_span.schema.json
[ ] runtime_status.schema.json
[ ] observability_audit.schema.json
[ ] monitoring_evidence_manifest.schema.json
[ ] monitoring_review_report.schema.json
[ ] completion_record.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 9.3 Runtime Artifacts

```text
[ ] .agentx-init/monitoring/events.jsonl
[ ] .agentx-init/monitoring/metrics.jsonl
[ ] .agentx-init/monitoring/health_checks.jsonl
[ ] .agentx-init/monitoring/alerts.jsonl
[ ] .agentx-init/monitoring/traces.jsonl
[ ] .agentx-init/monitoring/latest_status.json
[ ] .agentx-init/monitoring/latest_health_report.json
[ ] .agentx-init/monitoring/monitoring_evidence_manifest.json
[ ] .agentx-init/monitoring/monitoring_review_report.json
[ ] .agentx-init/monitoring/monitoring_completion_record.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 10. Validation Commands

Record the exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`. Any non-zero exit code is `FAIL` unless the command is explicitly a negative test where non-zero is the expected result and the expected failure condition is recorded.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_monitoring_schemas.py
git status --short
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
background daemon
hidden network exporter
```

---

# 11. Compileall Result

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
any Monitoring / Observability Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 12. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
scoped_command: <optional scoped monitoring pytest command>
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
any required monitoring model, schema, event, metric, health, status, alert, trace, redaction, retention, evidence, import-side-effect, idempotency, or boundary test fails
exit code is missing
```

---

# 13. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_monitoring_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest <schema test files>
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
```

Required schema tests:

```text
monitoring_event schema accepts valid event
monitoring_event schema rejects missing event_type
monitoring_event schema rejects invalid severity
metric_record schema accepts valid metric
metric_record schema rejects invalid metric kind
health_check schema accepts valid health check
health_report schema accepts valid health report
alert_record schema accepts valid alert
trace_span schema accepts valid span
runtime_status schema accepts valid runtime status
observability_audit schema accepts valid audit event
monitoring_evidence_manifest schema accepts valid evidence manifest
monitoring_review_report schema accepts valid review report
completion_record schema accepts final completion record
invalid enum values fail
missing required fields fail
secret-like payload examples are redacted before schema-valid persistence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
schema-invalid telemetry is accepted
required schemas are missing
monitoring evidence manifest cannot be validated
review report cannot be validated
completion record cannot be validated
schema validation exit code is missing
```

---

# 14. Import Side-Effect Check

Required behavior:

```text
[ ] importing tools.agentx_evolve.monitoring has no filesystem write side effects
[ ] importing monitoring modules does not start a background daemon
[ ] importing monitoring modules does not open a network port
[ ] importing monitoring modules does not start exporters
[ ] importing monitoring modules does not start collectors
[ ] importing monitoring modules does not execute health checks
[ ] importing monitoring modules does not execute shell commands
[ ] importing monitoring modules does not mutate source or runtime state
```

Record result:

```text
import_side_effect_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
artifacts:
  - <test output or evidence path>
failures:
  - <none or list>
```

Blocking if:

```text
import starts daemon
import opens port
import writes files
import executes command
import mutates source or runtime state
```

---

# 15. Health Check Result

Required behavior:

```text
[ ] health checks are read-only
[ ] health checks do not mutate source
[ ] health checks do not start background daemon
[ ] health checks do not open network port
[ ] health checks do not execute raw shell
[ ] command-based health checks, if any, use allowlisted commands only
[ ] command-based health checks record timeout and exit code
[ ] health checks produce schema-valid HealthCheck records
[ ] health checks produce schema-valid HealthReport records
[ ] degraded components are represented explicitly
[ ] unavailable components are represented explicitly
[ ] failure_class values come from Failure Taxonomy
```

Record result:

```text
health_check_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
artifacts:
  - .agentx-init/monitoring/health_checks.jsonl
  - .agentx-init/monitoring/latest_health_report.json
failures:
  - <none or list>
```

Blocking if:

```text
health checks mutate source
health checks run raw shell
health checks hide failed components
health report is schema-invalid
health checks require network by default
command health checks lack allowlist or exit-code evidence
```

---

# 16. Metric Collection Result

Required behavior:

```text
[ ] metrics are schema-valid
[ ] metrics append to metrics.jsonl
[ ] metric names are stable
[ ] metric units are explicit
[ ] metric source_component is recorded
[ ] metric timestamps are recorded
[ ] metric output is bounded
[ ] sensitive values are not stored as metric labels
[ ] repeated collection is deterministic enough for comparison
[ ] metrics do not become authorization decisions
```

Record result:

```text
metric_collection_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
artifacts:
  - .agentx-init/monitoring/metrics.jsonl
failures:
  - <none or list>
```

Blocking if:

```text
metrics include secrets
metrics are schema-invalid
metrics are unbounded
metrics are used to grant permissions
metrics overwrite source or config
```

---

# 17. Event Collection Result

Required behavior:

```text
[ ] runtime events are schema-valid
[ ] events append to events.jsonl
[ ] event_type is required
[ ] source_component is required
[ ] severity is required
[ ] failure_class is used where applicable
[ ] event payload is redacted
[ ] event payload is bounded
[ ] event collection preserves append-only JSONL behavior
[ ] event collection does not alter runtime behavior except approved evidence writes
```

Record result:

```text
event_collection_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
artifacts:
  - .agentx-init/monitoring/events.jsonl
failures:
  - <none or list>
```

Blocking if:

```text
events are not written
events are schema-invalid
events contain unredacted secrets
event collection mutates source or execution state
```

---

# 18. Trace Collection Result

Required behavior:

```text
[ ] trace spans are schema-valid
[ ] traces append to traces.jsonl
[ ] trace_id is required
[ ] span_id is required
[ ] parent_span_id is nullable and schema-valid
[ ] start/end timestamps are recorded where applicable
[ ] span duration is bounded and non-negative where applicable
[ ] trace payloads are redacted
[ ] trace payloads are bounded
[ ] trace collection does not start a daemon or network exporter
[ ] trace collection does not alter execution behavior except approved evidence writes
```

Record result:

```text
trace_collection_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
artifacts:
  - .agentx-init/monitoring/traces.jsonl
failures:
  - <none or list>
```

Blocking if:

```text
traces are schema-invalid
traces contain unredacted secrets
trace collection starts exporter by default
trace collection mutates source or execution state
```

---

# 19. Runtime Status Reporting Result

Required behavior:

```text
[ ] runtime status is schema-valid
[ ] latest_status.json is written atomically
[ ] status includes component health summary
[ ] status includes degraded/unavailable components explicitly
[ ] status references evidence artifacts where available
[ ] status does not grant permissions or approvals
[ ] status does not trigger remediation
[ ] status output is redacted and bounded
```

Record result:

```text
runtime_status_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
artifacts:
  - .agentx-init/monitoring/latest_status.json
failures:
  - <none or list>
```

Blocking if:

```text
latest_status.json is schema-invalid
status reporting mutates source
status reporting grants permissions
status reporting triggers automated fixes
status output contains secrets
```

---

# 20. Alert Generation Result

Required behavior:

```text
[ ] alerts are generated from explicit rules
[ ] alerts are schema-valid
[ ] alerts append to alerts.jsonl
[ ] alert severity is explicit
[ ] alert source evidence is referenced
[ ] duplicate alert handling is deterministic
[ ] alerts do not send network messages by default
[ ] alerts do not trigger automated fixes
[ ] alerts do not approve, retry, patch, promote, or mutate
```

Record result:

```text
alert_generation_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
artifacts:
  - .agentx-init/monitoring/alerts.jsonl
failures:
  - <none or list>
```

Blocking if:

```text
alerts trigger mutation
auto-remediation is enabled
alerts send network messages by default
alerts are schema-invalid
alerts are generated without evidence
```

---

# 21. Redaction Result

Required behavior:

```text
[ ] API keys are redacted
[ ] tokens are redacted
[ ] credentials are redacted
[ ] environment secrets are redacted
[ ] command output is redacted before persistence
[ ] event payloads are redacted
[ ] metric labels are redacted or rejected if sensitive
[ ] trace/span payloads are redacted
[ ] alert payloads are redacted
[ ] health report payloads are redacted
[ ] runtime status payloads are redacted
[ ] redaction runs before durable writes
[ ] redaction does not remove required structural fields
```

Record result:

```text
redaction_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
redaction_tests:
  - <none or list>
failures:
  - <none or list>
```

Blocking if:

```text
secrets are logged
redaction runs only after durable writes
redaction breaks schema validation
sensitive values are stored in metric labels or alert keys
```

---

# 22. Retention / Rotation Result

Required behavior:

```text
[ ] retention policy is explicit
[ ] rotation policy is explicit
[ ] rotation affects only approved monitoring artifacts
[ ] rotation does not delete source files
[ ] rotation does not delete active completion evidence
[ ] rotation does not delete the final review report
[ ] rotation does not delete the final evidence manifest
[ ] rotation does not delete the final completion record
[ ] rotation preserves required review evidence or archives it with hashes
[ ] retained files remain schema-parseable or are clearly archived
[ ] retention actions are audited
[ ] retention can be disabled for review mode
```

Record result:

```text
retention_rotation_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
artifacts:
  - <retention audit artifacts>
failures:
  - <none or list>
```

Blocking if:

```text
retention deletes source files
retention deletes required review evidence
rotation writes outside approved runtime root
rotation corrupts latest status or health report
retention removes hashes needed to reproduce DONE verdict
```

---

# 23. Determinism / Idempotency Result

Required behavior:

```text
[ ] repeated status generation produces stable structure
[ ] repeated health checks do not multiply duplicate latest records
[ ] repeated alert generation handles duplicates deterministically
[ ] repeated metric/event/trace collection is append-only and schema-valid
[ ] repeated retention/rotation does not delete additional protected evidence
[ ] repeated review report creation records new timestamp/hash rather than modifying prior signed evidence silently
```

Record result:

```text
determinism_idempotency_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
failures:
  - <none or list>
```

Blocking if:

```text
repeat run corrupts JSONL
repeat run changes signed evidence without new review report
repeat alert generation triggers duplicate mutation/remediation
repeat retention deletes protected evidence
```

---

# 24. Observability Audit Result

Required behavior:

```text
[ ] observability audit records are schema-valid
[ ] audit records append to approved monitoring evidence artifacts
[ ] audit records include event type, source component, timestamp, status, and evidence refs
[ ] audit records link to affected event, metric, health, alert, trace, status, or retention action where applicable
[ ] audit records do not contain unredacted secrets
[ ] audit records do not replace Failure Taxonomy failure classes
[ ] audit records do not authorize, approve, patch, promote, retry, or mutate
[ ] audit records survive retention / rotation or are archived with hashes
```

Record result:

```text
observability_audit_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
artifacts:
  - <observability audit artifacts>
failures:
  - <none or list>
```

Blocking if:

```text
audit records are schema-invalid
audit records contain secrets
audit trail is missing for retention / rotation actions
audit records are used as permission or approval decisions
audit evidence needed for DONE is deleted or unhashed
```

---

# 25. Resource Bound / Collector Cost Check

Required behavior:

```text
[ ] collectors define maximum payload size
[ ] collectors define maximum record count per run where applicable
[ ] collectors define maximum scan depth or file count where applicable
[ ] health checks define timeout_seconds when command-backed or potentially slow
[ ] trace collection limits span payload size and count
[ ] alert generation limits duplicate alerts and alert payload size
[ ] runtime status generation limits output size
[ ] retention / rotation limits affected files to approved monitoring artifacts
[ ] bounded failures return schema-valid FAILED or BLOCKED records
[ ] resource-limit decisions are evidenced
```

Record result:

```text
resource_bound_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
limits_verified:
  - <none or list>
failures:
  - <none or list>
```

Blocking if:

```text
collector can scan unbounded source tree
collector writes unbounded payloads
health check can hang without timeout
trace or metric collection can produce unbounded evidence
resource-bound failure is silent or unevidenced
```

---

# 26. Timestamp / Clock Validity Check

Required behavior:

```text
[ ] timestamps are ISO-8601 UTC or otherwise explicitly normalized
[ ] validation timestamp is recorded in evidence manifest, review report, and completion record
[ ] event, metric, health, alert, trace, and status timestamps are present
[ ] trace start/end timestamps are ordered where both are present
[ ] durations are non-negative where applicable
[ ] repeated review evidence records new timestamp rather than silently rewriting signed evidence
[ ] missing or malformed timestamp fails schema validation or is recorded as BLOCKED/FAILED
```

Record result:

```text
timestamp_validity_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
failures:
  - <none or list>
```

Blocking if:

```text
required timestamps are missing
timestamps are schema-invalid
trace durations are negative
review report timestamp does not match validation evidence window
evidence is silently rewritten without a new timestamp and hash
```

---

# 27. Dependency Availability Gate

The review must record whether required integration dependencies are present, safely deferred, or unavailable. Missing dependencies must not cause monitoring to expose sensitive telemetry, invent failure classifications, execute tools directly, or bypass sandbox boundaries.

Required dependency checks:

```text
[ ] Failure Taxonomy available or approved fallback failure class is used with warning
[ ] Policy / Capability Registry available for sensitive telemetry visibility or visibility fails closed
[ ] Tool / MCP Adapter available if monitoring records tool outcomes or MCP exposure is safely N/A/deferred
[ ] Security Sandbox available if monitoring health checks inspect paths or command health checks are used
[ ] missing dependency produces schema-valid degraded health/status evidence
[ ] missing dependency does not become ALLOW, PASS, or exposed telemetry by default
```

Record result:

```text
dependency_availability_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
dependencies:
  - name: <dependency>
    status: AVAILABLE | UNAVAILABLE_FAIL_CLOSED | DEFERRED SAFELY | NOT APPLICABLE
    evidence: <path or note>
failures:
  - <none or list>
```

Blocking if:

```text
missing Policy / Capability Registry exposes sensitive telemetry
missing Failure Taxonomy causes incompatible failure classes to be treated as final
missing Tool / MCP Adapter causes monitoring to execute tools directly
missing Security Sandbox causes path/command health checks to bypass safety
missing dependency is silently treated as PASS
```

---

# 28. JSONL Integrity Check

Required behavior:

```text
[ ] JSONL artifacts are append-only during collection
[ ] malformed pre-existing JSONL lines are preserved and reported, not silently deleted
[ ] new records are schema-valid
[ ] latest JSON artifacts are written atomically
[ ] temporary files for atomic writes remain inside `.agentx-init/monitoring/` or are recorded as deviations
[ ] review evidence identifies which JSONL files were parsed and hashed
```

Record result:

```text
jsonl_integrity_status: PASS | PARTIAL | FAIL | NOT CHECKED
summary: <summary>
failures:
  - <none or list>
```

Blocking if:

```text
collector truncates JSONL history unexpectedly
malformed existing lines are silently removed
new records are schema-invalid
atomic-write temporary files are created outside approved runtime boundary without deviation
```
---

# 29. Runtime Artifact Boundary Check

Approved runtime artifact root:

```text
.agentx-init/monitoring/
```

Required behavior:

```text
[ ] monitoring artifacts are written only under .agentx-init/monitoring/
[ ] evidence manifest is under .agentx-init/monitoring/
[ ] review report is under .agentx-init/monitoring/
[ ] completion record is under .agentx-init/monitoring/
[ ] runtime writes outside this root are listed in deviation register
[ ] source tree is not used for runtime artifacts
[ ] monitoring does not overwrite another layer's artifacts without authority
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
monitoring writes runtime evidence into source directories
monitoring writes hidden files outside approved root
monitoring overwrites another layer's artifacts without authority
unapproved artifact path is not recorded as a deviation
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
only expected runtime artifacts under .agentx-init/monitoring/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by monitoring tests
monitoring writes source files
monitoring modifies configuration without approval
retention / rotation touches source files
unapproved files are created outside runtime artifact paths
```

---

# 31. Evidence Hash Check

Create:

```text
.agentx-init/monitoring/monitoring_evidence_manifest.json
```

The manifest must include paths and SHA-256 hashes for final evidence files, including:

```text
monitoring_evidence_manifest.json
monitoring_review_report.json
monitoring_completion_record.json
events.jsonl, if used by review
metrics.jsonl, if used by review
health_checks.jsonl, if used by review
alerts.jsonl, if used by review
traces.jsonl, if used by review
latest_status.json
latest_health_report.json
command output artifacts, if stored as files
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
evidence manifest is missing
evidence hashes are missing
hashes do not match final files
review report is not hashed
completion record is not hashed
```

---

# 32. Monitoring Evidence Manifest

Required file:

```text
.agentx-init/monitoring/monitoring_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "monitoring_evidence_manifest.schema.json",
  "component_id": "AGENTX_MONITORING_OBSERVABILITY",
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
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "pytest",
      "command": "PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "schema_validation",
      "command": "<schema validation command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    }
  ],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "runtime_artifact_boundary_status": "PASS",
  "import_side_effect_status": "PASS",
  "redaction_status": "PASS",
  "retention_rotation_status": "PASS",
  "determinism_idempotency_status": "PASS",
  "health_status": "PASS",
  "metric_collection_status": "PASS",
  "event_collection_status": "PASS",
  "trace_collection_status": "PASS",
  "runtime_status_reporting_status": "PASS",
  "jsonl_integrity_status": "PASS",
  "alert_generation_status": "PASS",
  "observability_audit_status": "PASS",
  "resource_bound_status": "PASS",
  "timestamp_validity_status": "PASS",
  "dependency_availability_status": "PASS",
  "jsonl_integrity_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

The manifest must include paths and hashes for all final evidence files, including itself, the review report, and the completion record.

---

# 33. Monitoring Review Report

Required file:

```text
.agentx-init/monitoring/monitoring_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "monitoring_review_report.schema.json",
  "component_id": "AGENTX_MONITORING_OBSERVABILITY",
  "review_document_id": "MONITORING_OBSERVABILITY_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v3.0",
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
  "commands_run": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/monitoring/monitoring_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/monitoring/monitoring_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/monitoring/monitoring_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, or if it lacks command exit codes.

---

# 34. Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
retention / rotation must not remove evidence required to reproduce the DONE verdict
```

---

# 35. Integration Coverage

## 30.1 Failure Taxonomy Integration

```text
[ ] monitoring failures use approved failure_class values
[ ] degraded health states use standard failure classes where applicable
[ ] alert records reference failure classes where applicable
[ ] unknown failures map to approved unknown failure class
[ ] monitoring does not invent incompatible failure categories
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 30.2 Policy / Capability Registry Integration

```text
[ ] monitoring visibility rules use policy where needed
[ ] sensitive telemetry visibility fails closed
[ ] policy unavailable does not expose sensitive telemetry
[ ] monitoring does not grant permissions
[ ] monitoring does not approve actions
[ ] monitoring does not relax policy decisions based on observed state
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 30.3 Tool / MCP Adapter Integration

```text
[ ] monitoring may record tool-call outcomes
[ ] monitoring does not execute tools directly except through approved Tool Adapter paths
[ ] monitoring does not bypass Tool / MCP Adapter policy
[ ] monitoring exposed through MCP is read-only, not applicable, or safely deferred
[ ] MCP exposure does not include mutation, retry, patch, promote, approval, or command execution
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

## 30.4 Security Sandbox Integration

```text
[ ] monitoring does not use sandbox bypasses for filesystem reads
[ ] retention / rotation respects approved runtime boundaries
[ ] health checks that inspect paths use approved safe path access
[ ] command-based health checks, if any, use command acceptance rules
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 36. Negative Test Pack

The review must prove forbidden behavior fails closed.

Required negative cases:

```text
[ ] monitoring cannot write source files
[ ] monitoring cannot mutate configuration
[ ] monitoring cannot execute raw shell
[ ] monitoring cannot open network exporter by default
[ ] monitoring cannot start background daemon on import
[ ] monitoring cannot start collectors on import
[ ] alert generation cannot trigger automated fix
[ ] alert generation cannot apply patch
[ ] alert generation cannot approve promotion
[ ] retention cannot delete source files
[ ] retention cannot delete active review evidence
[ ] unredacted secret-like payload is not persisted
[ ] schema-invalid metric is rejected
[ ] schema-invalid event is rejected
[ ] schema-invalid alert is rejected
[ ] schema-invalid trace span is rejected
[ ] schema-invalid runtime status is rejected
[ ] sensitive telemetry visibility fails closed when policy is missing
[ ] MCP exposure, if present, cannot expose mutation or telemetry export by default
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked as non-applicable with justification.

---

# 37. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Runtime Artifact Boundary | MCP | Command Health Check | Retention | Schema | Report Template | Other>
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
Runtime artifact writes outside `.agentx-init/monitoring/` require a deviation entry.
MCP exposure requires either PASS, NOT APPLICABLE, or DEFERRED SAFELY with proof.
Command-based health checks require command-acceptance evidence.
Missing evidence hashes cannot be accepted as a deviation for DONE.
```

---

# 38. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
import side effects:
health checks:
metric collection:
event collection:
trace collection:
runtime status reporting:
alert generation:
redaction:
retention / rotation:
determinism / idempotency:
observability audit:
resource bounds:
timestamp validity:
dependency availability:
jsonl integrity:
runtime artifact boundary:
evidence manifest:
review report:
evidence hashes:
failure taxonomy integration:
policy integration:
tool / mcp integration:
negative tests:
source mutation check:
completion record:
```

---

# 39. What Failed

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

# 40. Issue Severity Classification

## 35.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
monitoring writes source files
monitoring mutates configuration
monitoring starts background daemon on import
monitoring starts collectors on import
monitoring opens network exporter by default
raw shell executes
health checks mutate state
alerts trigger automated fixes
alerts apply patches
alerts approve or promote changes
runtime status grants permission or approval
retention deletes source files
retention deletes required review evidence
collector behavior is unbounded
required timestamps are invalid
missing dependency is silently treated as PASS
JSONL history is silently truncated or corrupted
secrets are logged
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
required area remains NOT CHECKED
```

## 35.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
partial Failure Taxonomy mapping
partial Policy / Capability Registry visibility control
incomplete retention audit trail
incomplete trace/span redaction
runtime artifact boundary exception lacks justification
review environment not recorded
some expected monitoring files missing but not active runtime blockers
MCP deferral without explicit deviation entry
command-based health check without full command evidence
```

## 35.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled monitoring collector
MCP exposure intentionally deferred with safe-deferral proof
markdown/html report not implemented when JSON review report exists
additional future-layer metrics not implemented
```

---

# 41. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Monitoring package, schemas, tests, and runtime paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, and completion record. |
| Health / status reporting | 1.0 | Health checks and latest status are read-only, schema-valid, and evidenced. |
| Event / metric / trace collection | 1.0 | Events, metrics, and traces are bounded, schema-valid, append-only, and evidenced. |
| Alert generation | 1.0 | Alerts are rule-based, schema-valid, evidenced, deterministic, and non-mutating. |
| Redaction / retention / rotation | 1.0 | Secrets redacted before persistence; retention/rotation safe and audited. |
| Evidence / hashes / reports | 1.0 | Evidence manifest, review report, completion record, and SHA-256 hashes exist and match. |
| Integration and source-mutation safety | 1.0 | Import side effects, Failure Taxonomy, policy visibility, tool/MCP boundaries, dependency availability, observability audit, resource bounds, timestamp validity, JSONL integrity, runtime artifact boundary, idempotency, and clean git status pass. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for trusted monitoring evidence
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
import side effect starts daemon/exporter caps score at 4.0
source mutation caps score at 6.0
raw shell execution caps score at 4.0
network exporter enabled by default caps score at 4.0
secret leakage caps score at 4.0
alert-triggered mutation caps score at 4.0
retention deletes required evidence caps score at 5.0
missing evidence hashes caps score at 8.0
missing observability audit coverage caps score at 8.5
unbounded collector behavior caps score at 7.0
missing dependency availability proof caps score at 8.0
invalid timestamps in final evidence caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
```

---

# 42. GO / NO-GO Rules

## 37.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
import side-effect tests pass
health check tests pass
metric collection tests pass
event collection tests pass
trace collection tests pass
runtime status reporting tests pass
alert generation tests pass
redaction tests pass
retention / rotation tests pass
determinism / idempotency tests pass
observability audit tests pass
resource bound tests pass
timestamp validity tests pass
dependency availability checks pass
JSONL integrity checks pass
runtime artifact boundary check passes
evidence manifest exists
evidence hashes exist and match final files
review report exists
completion record exists
Failure Taxonomy integration passes
Policy / Capability Registry visibility rules pass or fail closed
Tool / MCP integration is safe, not applicable, or safely deferred
command-based health checks pass command acceptance rules or are not applicable
negative tests pass
source mutation check passes
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 37.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
monitoring writes source files
monitoring mutates configuration
monitoring starts background daemon on import
monitoring starts collectors on import
monitoring opens network exporter by default
raw shell executes
health checks mutate state
alerts trigger automated fixes
alerts apply patches
alerts approve or promote changes
runtime status grants permission or approval
retention deletes source files
retention deletes required review evidence
collector behavior is unbounded
required timestamps are invalid
missing dependency is silently treated as PASS
JSONL history is silently truncated or corrupted
secrets are logged
evidence manifest is missing
evidence hashes are missing or mismatched
review report is missing
completion record is missing
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 43. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix event formatting
fix metric formatting
fix alert formatting
fix trace/span formatting
fix runtime status structure
fix health report structure
fix import side-effect behavior
fix deterministic duplicate alert handling
fix redaction rules
fix retention boundary checks
fix evidence writing
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix tests to reflect the contract
fix Failure Taxonomy mapping
fix Policy / Capability visibility checks
fix runtime artifact boundary checks
```

Forbidden fixes:

```text
do not remove redaction to pass tests
do not skip schema validation
do not write monitoring artifacts into source directories
do not enable network export by default
do not start daemon on import
do not start collectors on import
do not execute raw shell for health checks
do not let alerts mutate, patch, retry, approve, or promote
do not let runtime status grant permissions or approval
do not delete evidence to satisfy retention tests
do not log secrets
do not omit hashes for final DONE
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
```

---

# 44. Definition of Done

The Monitoring / Observability Layer is done when it can act as the trusted runtime visibility and evidence layer for Agent_X.

It must prove:

```text
all target files exist
all schemas exist
all tests exist
monitoring package imports have no side effects
monitoring events are schema-valid
metric records are schema-valid
health checks are schema-valid and read-only
health reports are schema-valid and evidenced
alerts are schema-valid and non-mutating
traces/spans are schema-valid and bounded
runtime status is schema-valid and written atomically
redaction runs before persistence
retention / rotation is bounded and audited
collector and alert behavior is deterministic/idempotent enough for evidence review
observability audit records are schema-valid and linked to evidence
resource bounds are enforced for collectors and status/report output
timestamps are valid, normalized, and reproducible
dependency availability is recorded and fails closed when unavailable
JSONL integrity is preserved
all monitoring artifacts stay under .agentx-init/monitoring/ unless deviation is recorded
evidence manifest is written
review report is written
evidence hashes are written and match final files
review environment is recorded
Failure Taxonomy integration works
Policy / Capability Registry visibility rules fail closed
Tool / MCP Adapter boundary is not bypassed
command-based health checks obey Command Acceptance Criteria or are not applicable
MCP exposure is read-only, not applicable, or safely deferred
no source mutation occurs directly in this layer
no network exporter is enabled by default
no raw shell is executed
no background daemon starts on import
no collector starts on import
completion record exists
final verdict is recorded
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_monitoring_schemas.py
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

# 45. Required Evidence Package

The completion evidence package must include:

```text
compileall output
pytest output
schema validation result
import side-effect test result
health check test result
metric collection test result
event collection test result
trace collection test result
runtime status reporting test result
alert generation test result
redaction test result
retention / rotation test result
determinism / idempotency test result
observability audit test result
resource bound test result
timestamp validity test result
dependency availability result
JSONL integrity result
runtime artifact boundary result
source mutation check result
evidence manifest
review report
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
no network exporter by default
no background daemon on import
no collector start on import
no raw shell
no alert-triggered mutation
no retention deletion of required evidence
secrets redacted
hashes for final evidence artifacts
```

---

# 46. Completion Evidence Record

After validation, create:

```text
.agentx-init/monitoring/monitoring_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_MONITORING_OBSERVABILITY",
  "component_name": "Monitoring / Observability Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "canonical_monitoring_subdirectory": "tools/agentx_evolve/monitoring/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/monitoring/",
  "basis_documents": [
    "MONITORING_OBSERVABILITY_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "MONITORING_OBSERVABILITY_IMPLEMENTATION_SPEC",
    "MONITORING_OBSERVABILITY_IMPLEMENTATION_REVIEW_AND_DOD_v3"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "import_side_effects_verified": [],
  "health_checks_verified": [],
  "metrics_verified": [],
  "events_verified": [],
  "alerts_verified": [],
  "traces_verified": [],
  "runtime_status_verified": [],
  "redaction_verified": [],
  "retention_rotation_verified": [],
  "determinism_idempotency_verified": [],
  "observability_audit_verified": [],
  "resource_bounds_verified": [],
  "timestamp_validity_verified": [],
  "dependency_availability_verified": [],
  "jsonl_integrity_verified": [],
  "runtime_artifact_boundary_verified": [],
  "failure_taxonomy_integration_verified": [],
  "policy_integration_verified": [],
  "tool_mcp_boundary_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/monitoring/monitoring_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/monitoring/monitoring_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 47. Final Done / Not-Done Verdict

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
evidence hashes are missing or mismatched
review report is missing
completion record is missing
```

---

# 48. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/monitoring/ exists
[ ] schemas exist
[ ] tests exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Import Safety:
[ ] no daemon starts on import
[ ] no collector starts on import
[ ] no network exporter starts on import
[ ] no files written on import
[ ] no commands executed on import

Telemetry:
[ ] monitoring events written
[ ] metrics written
[ ] health checks written
[ ] alerts written
[ ] traces written
[ ] latest status written atomically
[ ] latest health report written atomically

Safety:
[ ] read-only by default
[ ] append-only for evidence
[ ] redacted before persistence
[ ] bounded output size
[ ] non-networked by default
[ ] non-mutating outside .agentx-init/monitoring/
[ ] no raw shell
[ ] no background daemon on import
[ ] alerts do not mutate/fix/patch/approve/promote
[ ] runtime status does not grant permissions or approval
[ ] retention does not delete source or required review evidence

Integration:
[ ] Failure Taxonomy integration passes
[ ] Policy / Capability visibility fails closed
[ ] Tool / MCP boundary is not bypassed
[ ] MCP exposure is N/A, read-only, or safely deferred
[ ] command health checks satisfy Command Acceptance Criteria or are N/A

Evidence:
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written and matching
[ ] evidence immutable after sign-off
[ ] JSONL history integrity preserved
[ ] observability audit records written and hashed
[ ] resource bounds verified
[ ] timestamps valid and normalized
[ ] dependency availability recorded and fail-closed

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 49. Final Sign-Off Template

Use this after implementation validation.

```text
Monitoring / Observability Validation — Commit <hash>

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
- import side effects: PASS/FAIL
- health check coverage: PASS/FAIL
- metric collection coverage: PASS/FAIL
- event collection coverage: PASS/FAIL
- trace collection coverage: PASS/FAIL
- runtime status reporting: PASS/FAIL
- alert generation coverage: PASS/FAIL
- redaction coverage: PASS/FAIL
- retention / rotation coverage: PASS/FAIL
- determinism / idempotency: PASS/FAIL
- observability audit: PASS/FAIL
- resource bounds: PASS/FAIL
- timestamp validity: PASS/FAIL
- dependency availability: PASS/FAIL
- JSONL integrity: PASS/FAIL
- runtime artifact boundary: PASS/FAIL
- Failure Taxonomy integration: PASS/FAIL
- Policy / Capability integration: PASS/FAIL
- Tool / MCP boundary: PASS/FAIL/N/A/DEFERRED SAFELY
- command health checks: PASS/FAIL/N/A
- negative-test coverage: PASS/FAIL
- source mutation check: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING/MISMATCHED
- review report: PRESENT/MISSING
- completion record: PRESENT/MISSING

Reproducibility:
- exact commands recorded: YES/NO
- exit codes recorded: YES/NO
- output artifacts recorded: YES/NO
- final hashes recorded: YES/NO
- deviations recorded: YES/NO/N/A
- evidence immutability respected: YES/NO

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

# 50. Final Rating

This v3 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the strong v2 coverage and fixes the remaining production-control gaps: dedicated observability audit review, resource-bound and collector-cost verification, timestamp/clock validity, dependency availability gates, JSONL integrity rules, atomic-write temporary file boundaries, stronger GO / NO-GO scoring coverage, and final reproducibility sign-off.
```
