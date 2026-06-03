# MONITORING_OBSERVABILITY_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: MONITORING_OBSERVABILITY_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v4.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_MONITORING_OBSERVABILITY
component_name: Monitoring / Observability Layer
roadmap_layer: 19
roadmap_phase: Phase E — Runtime Visibility and Evidence
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria
optional_standards: ES, Report Template
risk_level: high
implementation_mode: read-only observability and append-only runtime evidence
target_language: Python
canonical_subdirectory: tools/agentx_evolve/monitoring/
schema_subdirectory: tools/agentx_evolve/schemas/
test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/monitoring/
previous_version_rating: 9.8/10
current_version_rating: 10/10
next_document: MONITORING_OBSERVABILITY_IMPLEMENTATION_SPEC
```

---

# 0. v4 Review and Upgrade Summary

## 0.1 v3 Rating

The v3 contract was strong and close to final, but I would rate it:

```text
9.8/10
```

It already covered the requested contract areas and the v3 production-control additions:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
Monitoring Event Schema
Metric Schema
Health Check Schema
Alert Schema
Trace / Span Schema
Runtime Status Schema
Telemetry Redaction Rules
Retention / Rotation Rules
Failure Taxonomy Integration
Policy / Capability Registry Integration
Tool / MCP Adapter Integration
Agent_X integration notes
OpenCode borrowing notes
event source allowlisting
telemetry ingestion trust
report/export safety
clock/duration consistency
missing-data-is-not-healthy behavior
metric sampling/drop/aggregation audit
alert deduplication and recurrence
import-time side-effect bans
review report and evidence manifest schemas
```

## 0.2 Why v3 Was Not Fully 10/10

The v3 document was implementation-ready, but a few final operational-hardening details were still under-specified:

```text
1. Monitoring self-observation and recursive telemetry storm prevention were not explicit enough.
2. Disk quota, backpressure, and write-failure behavior needed stricter fail-safe rules.
3. Component criticality and health-status derivation needed a clearer scoring/precedence model.
4. Schema versioning and compatibility rules were not defined for future telemetry evolution.
5. Data minimization rules needed to say that unused sensitive fields must be dropped, not only redacted.
6. Idempotency keys were discussed generally but not required in the main schemas where useful.
7. Monitoring-disabled or monitoring-degraded states needed explicit handling.
8. Negative tests needed coverage for recursion, quota/write failure, schema version mismatch, and monitoring self-failure.
```

## 0.3 v4 Improvements

This v4 adds:

```text
monitoring self-observation and recursion guard rules
quota, capacity, and backpressure rules
component criticality and health derivation rules
schema versioning and compatibility rules
data minimization and field dropping rules
explicit idempotency_key expectations for event-like records
monitoring-disabled and self-degraded handling
expanded negative tests and No-Go conditions
```

Final v4 rating:

```text
10/10
```

---

# 1. Purpose

This document defines the controlling contract for the **Monitoring / Observability Layer** in the Agent_X self-evolving system.

The purpose of this layer is to define:

```text
what the Monitoring / Observability Layer is allowed to observe
what it must never expose
what telemetry records look like
where runtime artifacts are written
how health, status, metrics, traces, and alerts work
how monitoring stays read-only and non-mutating
how monitoring evidence is retained, rotated, redacted, hashed, and validated
how monitoring supports review without becoming an authority
```

Monitoring exists to make Agent_X behavior visible, auditable, and reviewable. It must not become an execution, mutation, approval, patching, promotion, network-export, or policy-bypass path.

Monitoring may collect structured information about system behavior. It must not change system behavior.

---

# 2. Scope

## 2.1 Required in This Layer

The layer must define contracts for:

```text
monitoring events
metric records
health checks
health reports
runtime status records
alerts
trace spans
observability audit records
telemetry redaction
telemetry retention
telemetry rotation
evidence manifests
review reports
latest status artifacts
failure visibility
component status summaries
policy-controlled visibility
Tool / MCP Adapter observation
Failure Taxonomy integration
Agent_X runtime status summaries
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
source mutation
patch application
automatic repair
automatic rollback
promotion
Git write operations
network export by default
model execution
LLM worker behavior
MCP server runtime by default
background daemon that changes state
human approval UI
policy decisions
sandbox authorization
failure recovery logic
scheduled task execution
external telemetry exporter
```

Monitoring observes and reports. It does not approve, repair, mutate, promote, execute unsafe commands, or decide authority.

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because monitoring evidence may become the basis for deciding whether Agent_X is healthy, degraded, blocked, failed, or ready for a later review gate.

This layer affects:

```text
runtime visibility
failure visibility
health-state trust
alert generation
evidence completeness
review reproducibility
incident diagnosis
safe degradation reporting
status surfaces used by later orchestrators
```

The layer must fail closed when monitoring data is malformed, unsafe to persist, unredacted, outside the runtime artifact boundary, or unsupported by referenced evidence.

## 3.2 Required Supporting Standard: FIC

FIC is required because this layer has concrete files with narrow responsibilities.

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
tools/agentx_evolve/monitoring/report_builder.py
```

Each file must have:

```text
clear responsibility
public API
input contract
output contract
schema validation points
safety limits
evidence behavior
tests
```

## 3.3 Required Supporting Standard: SIB

SIB is required because monitoring connects many Agent_X subsystems.

The layer must integrate with:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter Layer
Governed Patch Execution Layer
Model Adapter Layer
LLM Implementation Worker
Self-Evolution Orchestrator
Promotion / Release Gate
Evaluation Harness / Regression Benchmark Layer
Git Integration Layer
Backup / Disaster Recovery Layer
```

This layer is an integration boundary and evidence consumer. It must not become an authority that bypasses those components.

## 3.4 Required Supporting Standard: Schema Contract

Schema Contract is required because all telemetry must be structured and machine-checkable.

Required schemas:

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

Each schema must have:

```text
at least one valid example in tests
at least two invalid examples in tests
required ID field validation
enum validation
artifact boundary validation where applicable
redaction marker validation where applicable
```

Required valid examples:

```text
valid_monitoring_event
valid_metric_record
valid_health_check
valid_health_report
valid_alert_record
valid_trace_span
valid_runtime_status
valid_observability_audit
valid_monitoring_evidence_manifest
valid_monitoring_review_report
valid_completion_record
```

Required invalid examples:

```text
missing required ID field
invalid enum value
unredacted secret payload where applicable
artifact path outside approved runtime root where applicable
missing redaction marker where applicable
missing evidence reference where required
```

## 3.5 Required Evidence / Audit Rules

Every persisted monitoring record must be:

```text
schema-valid
redacted
bounded in size
written inside approved runtime artifact root
linked to source_component
linked to component_id where applicable
linked to timestamp
linked to evidence_refs or artifact_refs where applicable
append-only if historical
atomic if latest-state artifact
```

Monitoring evidence is required for:

```text
health check execution
health check failure
metric collection
metric collection failure
alert generation
alert suppression
alert resolution
runtime status update
trace/span creation
event logging
retention/rotation action
redaction action
malformed telemetry rejection
artifact boundary violation
sampling/drop/aggregation decision
report generation
```

---

# 4. Why This Layer Is Safety-Critical

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
which summaries may influence later review or promotion gates
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
a replacement for Security Sandbox
a promotion authority
```

---

# 5. Core Safety Posture

The Monitoring / Observability Layer must be:

```text
read-only by default
append-only for historical evidence
schema-validated
redacted before persistence
bounded in output size
non-networked by default
non-mutating outside .agentx-init/monitoring/
non-authoritative for permissions
non-authoritative for source changes
non-authoritative for promotion
integrated with Failure Taxonomy for failure class names
integrated with Policy / Capability Registry for monitoring visibility rules
```

The layer may collect and report state. It must not:

```text
fix
mutate
approve
retry
patch
promote
execute unsafe commands
export telemetry to the network by default
start background daemons by import side effect
```

---

# 6. Observation and Authority Boundaries

Monitoring is an observer and evidence producer. It is not an authority.

## 6.1 Monitoring May Produce

```text
events
metrics
health checks
health reports
alerts as local records
trace spans
runtime status summaries
review evidence manifests
local reports
```

## 6.2 Monitoring Must Not Produce

```text
permission decisions
policy approvals
sandbox approvals
governance approvals
human approvals
patch applications
rollback actions
Git writes
network exports
model calls
source modifications
```

## 6.3 Authority Rule

Monitoring data can support review, but it must not be treated as proof by itself unless referenced evidence exists.

A status, alert, metric, or health report is trusted only when it includes:

```text
schema-valid record
timestamp
source_component
component_id where applicable
evidence_refs or artifact_refs where applicable
redaction_applied marker
provenance metadata for generated artifacts
```

If required evidence is missing, monitoring must report:

```text
UNKNOWN
DEGRADED
BLOCKED
FAILED
```

It must not report `HEALTHY`.

---

# 7. Telemetry Source and Ingestion Trust Rules

Monitoring must accept telemetry only from known or explicitly identified sources.

## 7.1 Allowed Source Classes

```text
AGENTX_INTERNAL_COMPONENT
AGENTX_RUNTIME_ARTIFACT
AGENTX_TEST_FIXTURE
AGENTX_VALIDATION_COMMAND
AGENTX_REVIEW_REPORT
SIMULATED_DEPENDENCY
UNKNOWN_SOURCE
```

## 7.2 Source Rules

```text
AGENTX_INTERNAL_COMPONENT may produce normal telemetry if schema-valid.
AGENTX_RUNTIME_ARTIFACT may be summarized but not copied raw if sensitive.
AGENTX_TEST_FIXTURE may be used only in tests and must be marked as simulated.
AGENTX_VALIDATION_COMMAND output must be bounded and redacted.
AGENTX_REVIEW_REPORT may be referenced and hashed.
SIMULATED_DEPENDENCY must be denied-by-default and clearly marked.
UNKNOWN_SOURCE must be rejected or recorded only as a redacted SCHEMA_REJECTION / UNKNOWN_SOURCE event.
```

## 7.3 Ingestion Rules

```text
telemetry source must be recorded
source_component must be present or derived safely
source trust class must be present for external or simulated records
unknown sources must not update latest_status as HEALTHY
untrusted telemetry must not create critical system health claims
raw external telemetry must not be persisted without redaction and schema validation
```

---

# 8. Visibility Classes

Monitoring records must support visibility classification.

Allowed visibility classes:

```text
PUBLIC_SUMMARY
INTERNAL_SUMMARY
INTERNAL_DETAILED
RESTRICTED_SECURITY
RESTRICTED_SECRET_REDACTED
```

Rules:

```text
PUBLIC_SUMMARY may contain only non-sensitive summary state.
INTERNAL_SUMMARY may include component status and counts.
INTERNAL_DETAILED may include artifact refs and failure classes.
RESTRICTED_SECURITY may include security-relevant failure summaries but not raw secrets.
RESTRICTED_SECRET_REDACTED must prove redaction occurred before persistence.
```

External exposure of anything beyond `INTERNAL_SUMMARY` must be policy-checked.

---

# 9. Canonical Subdirectories

## 9.1 Monitoring Package

```text
tools/agentx_evolve/monitoring/
```

Expected files:

```text
__init__.py
monitoring_models.py
event_logger.py
metrics_collector.py
health_checks.py
status_reporter.py
alert_manager.py
trace_collector.py
retention_policy.py
redaction.py
report_builder.py
```

## 9.2 Schema Directory

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

## 9.3 Test Directory

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
test_event_logger.py
test_metrics_collector.py
test_health_checks.py
test_status_reporter.py
test_alert_manager.py
test_trace_collector.py
test_retention_policy.py
test_monitoring_redaction.py
test_monitoring_report_builder.py
test_monitoring_negative_cases.py
```

## 9.4 Runtime Artifact Root

```text
.agentx-init/monitoring/
```

Expected runtime artifacts:

```text
.agentx-init/monitoring/events.jsonl
.agentx-init/monitoring/metrics.jsonl
.agentx-init/monitoring/health_checks.jsonl
.agentx-init/monitoring/alerts.jsonl
.agentx-init/monitoring/traces.jsonl
.agentx-init/monitoring/observability_audit.jsonl
.agentx-init/monitoring/latest_status.json
.agentx-init/monitoring/latest_health_report.json
.agentx-init/monitoring/monitoring_evidence_manifest.json
.agentx-init/monitoring/monitoring_review_report.json
.agentx-init/monitoring/monitoring_completion_record.json
```

---

# 10. Monitoring Event Schema Contract

A monitoring event records a discrete observable event.

Required structure:

```json
{
  "schema_version": "1.0",
  "schema_id": "monitoring_event.schema.json",
  "event_id": "string",
  "timestamp": "string",
  "source_component": "string",
  "source_trust_class": "AGENTX_INTERNAL_COMPONENT|AGENTX_RUNTIME_ARTIFACT|AGENTX_TEST_FIXTURE|AGENTX_VALIDATION_COMMAND|AGENTX_REVIEW_REPORT|SIMULATED_DEPENDENCY|UNKNOWN_SOURCE",
  "event_type": "string",
  "idempotency_key": "string|null",
  "severity": "INFO|WARNING|ERROR|CRITICAL",
  "visibility": "PUBLIC_SUMMARY|INTERNAL_SUMMARY|INTERNAL_DETAILED|RESTRICTED_SECURITY|RESTRICTED_SECRET_REDACTED",
  "component_id": "string",
  "component_status": "UNKNOWN|HEALTHY|DEGRADED|BLOCKED|FAILED",
  "message": "string",
  "data": {},
  "artifact_refs": [],
  "evidence_refs": [],
  "failure_class": "string|null",
  "redaction_applied": true,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
event_id is required
timestamp is required
source_component is required
source_trust_class is required
event_type is required
severity must be enum-bound
visibility must be enum-bound
failure_class must use Failure Taxonomy when present
raw secrets must not be persisted
large data must be summarized or truncated
```

Event type naming must follow:

```text
COMPONENT_EVENT
HEALTH_EVENT
METRIC_EVENT
ALERT_EVENT
TRACE_EVENT
RETENTION_EVENT
REDACTION_EVENT
SCHEMA_REJECTION
BOUNDARY_REJECTION
UNKNOWN_SOURCE_REJECTION
```

---

# 11. Metric Schema Contract

A metric record stores a numeric or categorical measurement.

Required structure:

```json
{
  "schema_version": "1.0",
  "schema_id": "metric_record.schema.json",
  "metric_id": "string",
  "timestamp": "string",
  "source_component": "string",
  "metric_name": "string",
  "idempotency_key": "string|null",
  "metric_type": "COUNTER|GAUGE|TIMER|SUMMARY|STATE",
  "value": 0,
  "unit": "string|null",
  "labels": {},
  "component_id": "string|null",
  "session_id": "string|null",
  "artifact_refs": [],
  "evidence_refs": [],
  "redaction_applied": true,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
metric_name is required
metric_type is enum-bound
labels must be redacted
values must be JSON-serializable
metrics must not contain raw file contents
metrics must not contain unredacted command output
```

Metric cardinality rules:

```text
metric_name must come from an allowlist or documented component namespace
labels must be low-cardinality
labels must not include raw paths unless normalized and policy-allowed
labels must not include user-provided text, prompts, command output, tokens, or secrets
component_id, status, failure_class, tool_name, and layer_id are allowed labels when redacted
session_id may be included only as a bounded reference, not as a high-cardinality aggregate label by default
unknown or unbounded labels must be dropped, summarized, or blocked before persistence
```

Sampling, dropping, and aggregation rules:

```text
sampling must be deterministic or explicitly configured
sampled records must include sampling_applied=true where applicable
dropped metrics must write an observability audit event with reason
aggregation must preserve counts, time window, source_component, and redaction status
high-cardinality values must never be used as labels by default
metrics dropped for safety must not be silently ignored
```

Allowed metric examples:

```text
tool_calls_total
blocked_tool_calls_total
invalid_tool_calls_total
schema_validation_failures_total
health_check_duration_ms
latest_status_age_seconds
evidence_files_written_total
redaction_events_total
alerts_generated_total
runtime_artifact_bytes
monitoring_records_dropped_total
```

---

# 12. Health Check Schema Contract

A health check record stores the result of one check.

Required structure:

```json
{
  "schema_version": "1.0",
  "schema_id": "health_check.schema.json",
  "health_check_id": "string",
  "timestamp": "string",
  "source_component": "MonitoringHealthChecks",
  "check_name": "string",
  "idempotency_key": "string|null",
  "component_id": "string",
  "status": "PASS|WARN|FAIL|SKIP|BLOCKED",
  "severity": "INFO|WARNING|ERROR|CRITICAL",
  "message": "string",
  "duration_ms": 0,
  "failure_class": "string|null",
  "artifact_refs": [],
  "evidence_refs": [],
  "redaction_applied": true,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
health checks must be read-only by default
health checks must not mutate source
health checks must not run raw shell
health checks must not require network by default
health checks must return BLOCKED if required safe command authority is missing
missing upstream evidence must not produce PASS
```

---

# 13. Health Report Schema Contract

A health report summarizes the current health of one or more Agent_X components.

Required structure:

```json
{
  "schema_version": "1.0",
  "schema_id": "health_report.schema.json",
  "health_report_id": "string",
  "timestamp": "string",
  "generated_at": "string",
  "source_component": "MonitoringHealthReporter",
  "overall_status": "UNKNOWN|HEALTHY|DEGRADED|BLOCKED|FAILED",
  "components": [],
  "checks": [],
  "alerts": [],
  "artifact_refs": [],
  "evidence_refs": [],
  "redaction_applied": true,
  "warnings": [],
  "errors": []
}
```

Status precedence:

```text
FAILED
BLOCKED
DEGRADED
UNKNOWN
HEALTHY
```

Rules:

```text
if components disagree, the strictest status wins
if required evidence is missing, status must be UNKNOWN or DEGRADED, not HEALTHY
if a critical component is stale, overall status must not be HEALTHY
if schema validation fails, the report must not replace latest_health_report.json
```

---

# 14. Alert Schema Contract

An alert record stores a condition that requires attention.

Required structure:

```json
{
  "schema_version": "1.0",
  "schema_id": "alert_record.schema.json",
  "alert_id": "string",
  "alert_key": "string",
  "idempotency_key": "string|null",
  "timestamp": "string",
  "source_component": "MonitoringAlertManager",
  "alert_type": "THRESHOLD|HEALTH|FAILURE|SECURITY|EVIDENCE|SCHEMA|RETENTION|UNKNOWN",
  "severity": "INFO|WARNING|ERROR|CRITICAL",
  "component_id": "string|null",
  "title": "string",
  "message": "string",
  "condition": {},
  "status": "OPEN|ACKNOWLEDGED|SUPPRESSED|RESOLVED",
  "suppression_reason": "string|null",
  "dedupe_key": "string|null",
  "failure_class": "string|null",
  "artifact_refs": [],
  "evidence_refs": [],
  "redaction_applied": true,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
alerts are records, not actions
alerts must not send email by default
alerts must not call network by default
alerts must not mutate source
alert suppression must be evidenced
critical alert generation must not expose secrets
```

Alert lifecycle rules:

```text
OPEN alerts are newly generated and require review.
ACKNOWLEDGED alerts record that a reviewer or authorized system has seen the alert.
SUPPRESSED alerts must include suppression_reason and evidence_refs.
RESOLVED alerts must reference the evidence that proves the condition no longer applies.
Alerts must not auto-resolve without evidence.
Alert status transitions must be appended as new records, not silent in-place edits.
Alert suppression must not delete the original alert.
```

Allowed transitions:

```text
OPEN -> ACKNOWLEDGED
OPEN -> SUPPRESSED
OPEN -> RESOLVED
ACKNOWLEDGED -> RESOLVED
ACKNOWLEDGED -> SUPPRESSED
SUPPRESSED -> OPEN, if condition reappears
```

Forbidden transitions:

```text
RESOLVED -> OPEN without a new alert record
SUPPRESSED -> RESOLVED without evidence
any transition that removes the original alert evidence
```

Deduplication and recurrence rules:

```text
dedupe_key may group repeated alerts for the same condition
recurring alerts must append recurrence records, not overwrite history
alert_count may be aggregated only if raw sensitive details are not required
critical security alerts must not be suppressed solely by dedupe
```

---

# 15. Trace / Span Schema Contract

Trace spans record relationships between operations.

Required structure:

```json
{
  "schema_version": "1.0",
  "schema_id": "trace_span.schema.json",
  "trace_id": "string",
  "span_id": "string",
  "parent_span_id": "string|null",
  "timestamp_start": "string",
  "timestamp_end": "string|null",
  "source_component": "string",
  "operation_name": "string",
  "idempotency_key": "string|null",
  "status": "STARTED|SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "duration_ms": 0,
  "component_id": "string|null",
  "tool_call_id": "string|null",
  "tool_result_id": "string|null",
  "policy_decision_id": "string|null",
  "sandbox_decision_id": "string|null",
  "failure_record_id": "string|null",
  "session_id": "string|null",
  "attributes": {},
  "artifact_refs": [],
  "evidence_refs": [],
  "redaction_applied": true,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
trace attributes must be redacted
trace data must not include raw prompts, raw secrets, or raw file contents
trace spans must be append-only
trace span creation must not change operation behavior
```

Trace correlation rules:

```text
Tool / MCP Adapter calls should propagate tool_call_id and tool_result_id where available.
Policy decisions should propagate policy_decision_id where available.
Sandbox checks should propagate sandbox_decision_id where available.
Patch sessions should propagate patch_session_id where available.
Failure records should propagate failure_record_id where available.
Health reports should reference the trace_id or evidence_refs used to build them.
```

Trace spans must not invent missing upstream IDs. If a correlation ID is unavailable, the span must record a warning instead of fabricating one.

---

# 16. Runtime Status Schema Contract

Runtime status records the current summarized state of Agent_X.

Required structure:

```json
{
  "schema_version": "1.0",
  "schema_id": "runtime_status.schema.json",
  "runtime_status_id": "string",
  "timestamp": "string",
  "generated_at": "string",
  "source_component": "MonitoringStatusReporter",
  "overall_status": "UNKNOWN|HEALTHY|DEGRADED|BLOCKED|FAILED",
  "component_statuses": [],
  "active_sessions": [],
  "recent_failures": [],
  "recent_alerts": [],
  "last_health_report_ref": "string|null",
  "status_age_seconds": 0,
  "artifact_refs": [],
  "evidence_refs": [],
  "redaction_applied": true,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
latest_status.json must be written atomically
latest_status.json must not contain secrets
latest_status.json must summarize, not duplicate large raw evidence
latest_status.json must not become an approval record
```

Freshness and stale-data rules:

```text
latest_status.json must include generated_at and status_age_seconds where possible.
latest_health_report.json must include generated_at and source evidence refs.
A stale status must be marked DEGRADED or UNKNOWN, not HEALTHY.
A missing required upstream status must not be summarized as HEALTHY.
If clock data is unavailable or inconsistent, monitoring must record UNKNOWN with warning.
```

Default staleness thresholds:

```text
latest_status_stale_after_seconds: 3600
latest_health_report_stale_after_seconds: 3600
critical_component_status_stale_after_seconds: 900
```

---

# 17. Observability Audit Schema Contract

Observability audit records describe monitoring-layer actions.

Required structure:

```json
{
  "schema_version": "1.0",
  "schema_id": "observability_audit.schema.json",
  "audit_id": "string",
  "timestamp": "string",
  "source_component": "MonitoringObservability",
  "action": "EVENT_WRITE|METRIC_WRITE|HEALTH_CHECK|ALERT_WRITE|TRACE_WRITE|STATUS_WRITE|REPORT_WRITE|RETENTION_ROTATION|REDACTION|SCHEMA_REJECTION|BOUNDARY_REJECTION|UNKNOWN_SOURCE_REJECTION|SAMPLE_DROP|AGGREGATION",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "message": "string",
  "artifact_refs": [],
  "evidence_refs": [],
  "redaction_applied": true,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
audit records must be append-only
audit records must not include unredacted payloads
schema rejection must be evidenced
artifact boundary rejection must be evidenced
sampling/drop/aggregation must be evidenced
```

---

# 18. Evidence Manifest Schema Contract

The monitoring evidence manifest records final evidence artifacts for validation and review.

Required structure:

```json
{
  "schema_version": "1.0",
  "schema_id": "monitoring_evidence_manifest.schema.json",
  "component_id": "AGENTX_MONITORING_OBSERVABILITY",
  "created_at": "string",
  "validated_commit": "string|null",
  "runtime_artifact_root": ".agentx-init/monitoring/",
  "evidence_files": [],
  "evidence_file_hashes": [],
  "record_counts": {},
  "schema_validation_status": "PASS|PARTIAL|FAIL|NOT_RUN",
  "redaction_status": "PASS|PARTIAL|FAIL|NOT_RUN",
  "artifact_boundary_status": "PASS|PARTIAL|FAIL|NOT_RUN",
  "deviation_register": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
evidence manifest must include SHA-256 hashes for final evidence artifacts
evidence manifest must include record counts where applicable
evidence manifest must not include raw secret values
evidence manifest must not mark validation PASS without command evidence or test evidence
```

---

# 19. Review Report Schema Contract

The monitoring review report records post-implementation validation findings.

Required structure:

```json
{
  "schema_version": "1.0",
  "schema_id": "monitoring_review_report.schema.json",
  "component_id": "AGENTX_MONITORING_OBSERVABILITY",
  "review_document_id": "MONITORING_OBSERVABILITY_IMPLEMENTATION_REVIEW_AND_DOD",
  "reviewed_commit": "string",
  "reviewed_at": "string",
  "review_environment": {},
  "commands_run": [],
  "coverage_statuses": {},
  "evidence_manifest_path": "string",
  "evidence_manifest_sha256": "string",
  "implementation_rating": 0,
  "final_verdict": "DONE|NOT_DONE",
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
reviewed_commit is required for final DONE
command exit codes are required for final DONE
evidence manifest path and hash are required for final DONE
coverage_statuses must include schemas, redaction, retention, artifact boundary, source mutation, and no-network checks
```

---

# 20. Telemetry Redaction Rules

Before writing telemetry, the layer must redact:

```text
API keys
tokens
passwords
private keys
session cookies
provider credentials
environment secrets
raw command output containing secrets
raw file contents containing secrets
raw prompt text if prompt redaction rules apply
personal data not required for debugging
```

Redaction applies to:

```text
event data
metric labels
health check messages
alert messages
trace attributes
runtime status summaries
observability audit records
review reports
error messages
warnings
```

Replacement format:

```text
[REDACTED]
```

Rules:

```text
redaction must occur before persistence
redaction failures must block persistence of unsafe payloads
redaction must preserve enough structure for debugging
redaction must not remove schema-required fields
redaction_applied must be true on persisted telemetry records
```

---

# 21. Retention / Rotation Rules

Monitoring evidence may grow over time. The layer must define retention and rotation rules.

Default retention policy:

```text
append-only active logs under .agentx-init/monitoring/
rotation allowed only within .agentx-init/monitoring/
no deletion of final review evidence without explicit backup/retention policy
no truncation of active evidence without recording rotation audit
```

Required rotation behavior:

```text
rotation action writes observability audit record
rotated file path stays inside runtime artifact root
rotation preserves JSONL line boundaries
rotation does not corrupt latest_status.json
rotation does not remove completion evidence
```

Retention metadata must include:

```text
retention_policy_id
max_file_bytes
max_retained_files
rotation_timestamp
source_file
rotated_file
sha256_before
sha256_after
warnings
errors
```

Forbidden retention behavior:

```text
silent deletion
source file deletion outside monitoring root
log compaction that removes critical failure evidence
rotation that writes outside .agentx-init/monitoring/
rotation that changes source code
```

---

# 22. Failure Taxonomy Integration

Monitoring must use the Failure Taxonomy for failure classes.

Allowed behavior:

```text
reuse known failure_class values from upstream components
record UNKNOWN_MONITORING_FAILURE only when no specific class exists
preserve upstream failure_class in events, alerts, and status summaries
```

Monitoring-specific failure classes may include:

```text
MONITORING_SCHEMA_INVALID
MONITORING_ARTIFACT_BOUNDARY_DENIED
MONITORING_REDACTION_FAILED
MONITORING_RETENTION_FAILED
MONITORING_HEALTH_CHECK_FAILED
MONITORING_STATUS_WRITE_FAILED
MONITORING_ALERT_GENERATION_FAILED
MONITORING_UNKNOWN_SOURCE_DENIED
UNKNOWN_MONITORING_FAILURE
```

Rules:

```text
monitoring must not invent conflicting failure classes for upstream failures
monitoring must not overwrite upstream failure_class values without evidence
monitoring must include failure_class for failed, blocked, or invalid monitoring records
```

---

# 23. Policy / Capability Registry Integration

Monitoring visibility may be policy-controlled.

Policy may decide:

```text
which roles can read monitoring artifacts
which roles can run health checks
which roles can generate review reports
which components may be observed
which sensitive fields must be hidden
which metric groups are visible
which alert details are visible
```

Rules:

```text
monitoring must not grant permissions
monitoring must not bypass Policy / Capability Registry
monitoring must fail closed if policy is required and unavailable
monitoring write of runtime evidence is allowed only inside approved monitoring root
read access to monitoring artifacts must respect policy when exposed through tools or reports
```

If Policy / Capability Registry is unavailable:

```text
internal append-only monitoring may continue for local runtime evidence
external exposure of monitoring artifacts must block
sensitive details must be redacted by default
```

---

# 24. Tool / MCP Adapter Integration

Monitoring may observe Tool / MCP Adapter behavior.

Allowed observations:

```text
tool call count
tool result count
blocked tool count
invalid tool count
MCP request count
MCP blocked request count
tool latency summaries
tool failure classes
evidence artifact refs
```

Forbidden behavior:

```text
monitoring must not execute tools directly to collect metrics
monitoring must not bypass tool permission checks
monitoring must not expose mutating tools through MCP
monitoring must not start MCP server
monitoring must not change Tool Registry
monitoring must not alter tool results
```

If monitoring is exposed as tools later, those tools must be:

```text
read-only
schema-validated
policy-checked
sandbox-aware if reading files
MCP-hidden or read-only by default
```

---

# 25. Security Sandbox Integration

Monitoring must respect filesystem boundaries.

Rules:

```text
monitoring writes only to .agentx-init/monitoring/
monitoring reads external artifacts only through approved read paths or sandbox-aware tools
monitoring must not scan arbitrary filesystem paths by default
monitoring must not read source files to collect metrics unless explicitly authorized
monitoring must not write outside runtime artifact root
```

Boundary violations must return or record:

```text
status = BLOCKED
failure_class = MONITORING_ARTIFACT_BOUNDARY_DENIED
```

---

# 26. Agent_X Integration Notes

The layer must be able to summarize the health of these Agent_X areas:

```text
Initiator
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter
Model Adapter
Local Model Runtime Profiles
Context Builder / Task Packer
Prompt Contract / Prompt Versioning
LLM Implementation Worker
Self-Evolution Orchestrator
Human Review / Approval Interface
Promotion / Release Gate
Git Integration
Evaluation Harness / Regression Benchmark
Long-Term Learning / Outcome Review
Documentation Synchronization
Task Queue / Session Scheduler
Packaging / Distribution
Backup / Disaster Recovery
Final System Acceptance
```

Minimum v1 integration:

```text
record monitoring events
record metric records
record health check records
write latest_status.json
write latest_health_report.json
generate alerts as local records only
redact telemetry before writing
rotate monitoring logs safely
build local evidence manifest
```

---

# 27. OpenCode Borrowing Notes

## 27.1 Concepts to Borrow

Borrow these OpenCode-style concepts only as architectural patterns:

```text
structured tool/event logs
clear separation between tool calls and results
bounded output summaries
status surfaces
error visibility
human-readable reports
plugin/tool observability concepts
operation tracing concepts
```

## 27.2 Concepts to Restrict

Do not copy these assumptions:

```text
telemetry exported over network by default
provider-integrated analytics by default
broad shell access for diagnostics
plugin-driven monitoring without Agent_X policy
unbounded logging of raw outputs
monitoring that mutates runtime behavior
monitoring that silently reads arbitrary files
```

## 27.3 Agent_X Mapping

| OpenCode-style concept | Agent_X monitoring equivalent | Required control |
|---|---|---|
| Tool call log | `monitoring_event` / metric counters | Redacted, schema-valid, local runtime only |
| Tool result log | event + metric + trace span | Redacted, bounded output |
| Status display | `latest_status.json` | Atomic write, no approval authority |
| Error visibility | alert records | Local records only, no network send |
| Trace/debug flow | `trace_span` | No raw prompts/secrets/file contents |
| Plugin telemetry | future monitoring tool | Policy-checked, read-only |
| Runtime diagnostics | health checks | No raw shell, no mutation |

---

# 28. Public API Contract

Expected classes:

```text
MonitoringEvent
MetricRecord
HealthCheckRecord
HealthReport
AlertRecord
TraceSpan
RuntimeStatus
ObservabilityAuditEvent
MonitoringEvidenceManifest
MonitoringReviewReport
```

Expected public functions:

```python
record_monitoring_event(event: MonitoringEvent, repo_root: Path) -> dict
record_metric(metric: MetricRecord, repo_root: Path) -> dict
record_health_check(check: HealthCheckRecord, repo_root: Path) -> dict
record_alert(alert: AlertRecord, repo_root: Path) -> dict
record_trace_span(span: TraceSpan, repo_root: Path) -> dict
write_latest_status(status: RuntimeStatus, repo_root: Path) -> dict
write_latest_health_report(report: HealthReport, repo_root: Path) -> dict
redact_telemetry_payload(payload: dict) -> dict
apply_monitoring_retention(repo_root: Path, policy: dict) -> dict
build_monitoring_evidence_manifest(repo_root: Path) -> dict
build_monitoring_review_report(repo_root: Path, validation_context: dict) -> dict
```

Public functions must not:

```text
mutate source
execute raw shell
open network connections
start background daemons
change policy
change tool registry
apply patches
commit or push Git changes
```

---

# 29. Monitoring Write Pipeline

Every persisted monitoring record must follow this sequence:

```text
1. Receive monitoring object or raw dict.
2. Normalize into schema-shaped object.
3. Attach timestamp if missing.
4. Attach source_component if missing.
5. Attach source_trust_class when applicable.
6. Redact sensitive fields.
7. Validate against schema.
8. Enforce runtime artifact boundary.
9. Append JSONL record or atomically write latest artifact.
10. Write observability audit record.
11. Return evidence reference.
```

Rules:

```text
schema-invalid telemetry must not be persisted as normal telemetry
unsafe unredacted telemetry must not be persisted
artifact-boundary violation must block
exceptions must become schema-valid observability audit failures
```

---

# 30. Runtime Artifact Rules

Approved runtime artifact root:

```text
.agentx-init/monitoring/
```

Allowed writes:

```text
append JSONL records
atomic latest JSON writes
rotation files inside monitoring root
evidence manifest
review report
completion record
```

Forbidden writes:

```text
source files
config files outside monitoring root
Git metadata
Tool Registry files
Policy Registry files
Security Sandbox files
MCP server files
network destinations
```

If a monitoring artifact must reference evidence outside monitoring root, it must store only a reference path or ID, not duplicate raw sensitive content.

---

# 31. Idempotency, Concurrency, and Locking Rules

Monitoring writes must be deterministic and safe under repeated calls.

## 31.1 Idempotency Rules

```text
Repeated latest_status writes may replace latest_status.json atomically.
Repeated JSONL event writes must create new records unless an explicit idempotency_key is provided.
Records with the same idempotency_key must not be duplicated without a warning.
Retrying a failed write must not corrupt existing JSONL.
Retention rotation must be safe to retry.
```

## 31.2 Concurrency Rules

```text
append-only JSONL writes must preserve full-line records
latest JSON writes must use temp-file then atomic rename
rotation must not run concurrently with writes without a lock or safe guard
partial temp files must not be treated as final evidence
```

Acceptable locking approaches:

```text
platform-safe file lock if available
atomic rename with per-file temp names
single-process lock object for unit tests
conservative BLOCKED result if safe write cannot be guaranteed
```

## 31.3 Corruption Handling

```text
malformed existing JSONL lines must be preserved
new writes must append after malformed lines instead of rewriting history
latest JSON corruption must produce BLOCKED or FAILED status and an audit event
monitoring must not silently repair evidence without recording the repair as a new audit event
```

---

# 32. Artifact Provenance and Hashing Rules

Final monitoring evidence must be hashable and reproducible.

Required provenance fields for final evidence artifacts:

```text
artifact_path
artifact_type
created_at
source_component
schema_id
component_id
sha256
record_count, where applicable
byte_size
validated_commit, where available
```

Hashing rules:

```text
SHA-256 is required for evidence manifest, review report, and completion record.
SHA-256 is required for rotated files.
SHA-256 is required for command-output artifacts if health checks store output artifacts.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required hashes are missing.
```

Monitoring must never hash secrets in a way that later exposes the secret value in logs. If an artifact contains redacted content, hash the redacted persisted artifact.

---

# 33. Clock, Timestamp, and Duration Rules

Monitoring timestamps must be consistent enough for review.

Rules:

```text
all timestamps must be ISO-8601 UTC where possible
records must preserve upstream timestamps when provided and valid
duration_ms must be non-negative
if timestamp_end precedes timestamp_start, record FAILED or INVALID with warning
clock inconsistency must not produce HEALTHY summary
status_age_seconds must not be negative
fake clock may be used in tests only and must be marked as simulated
```

If clock data is unavailable:

```text
record UNKNOWN or DEGRADED status
include warning
avoid deriving misleading latency or freshness metrics
```

---

# 34. MCP Exposure Policy

Monitoring is not required to expose MCP tools in v1.

If monitoring is exposed through MCP later:

```text
MCP exposure must be read-only
MCP exposure must not include alert mutation
MCP exposure must not include retention mutation unless policy-approved
MCP exposure must not expose raw telemetry with secrets
MCP exposure must not start server automatically
MCP exposure must not bypass Tool / MCP Adapter
```

Required default:

```text
no MCP runtime dependency
no MCP server auto-start
no network port
no mutating monitoring tools exposed
```

---

# 35. Command Acceptance Criteria

This section applies only if health checks or diagnostics use commands.

Allowed command behavior:

```text
commands must be allowlisted
commands must be read-only
commands must run through Tool / MCP Adapter or Security Sandbox command gate
stdout/stderr must be bounded
output must be redacted before persistence
exit code must be recorded
```

Forbidden command behavior:

```text
raw shell
network commands by default
Git write commands
source mutation commands
package install commands
daemon start commands
unbounded output capture
```

If safe command execution is unavailable:

```text
command-based health checks return BLOCKED
non-command health checks may continue
```

---

# 36. Report and Export Rules

Monitoring may generate local reports only.

Allowed local report formats:

```text
JSON
Markdown
HTML, if static and local only
```

Rules:

```text
reports must be generated under .agentx-init/monitoring/ or another approved runtime report root with deviation recorded
reports must be redacted before writing
reports must not include raw secrets, raw prompts, raw file contents, or unbounded command output
reports must include generated_at, source_component, evidence_refs, and redaction_applied
reports must not open a browser, send email, call network, or start a server
reports must not replace evidence logs
```

If a report is intended for external sharing:

```text
visibility must be PUBLIC_SUMMARY or policy-approved INTERNAL_SUMMARY
restricted details must be removed or redacted
artifact hashes may be included, but raw sensitive evidence must not be embedded
```

---

# 37. Import-Time and Startup Side-Effect Rules

Monitoring modules must be safe to import.

On import, monitoring modules must not:

```text
write files
start background threads
start daemons
open sockets
run health checks
scan filesystem
read secrets
load external providers
execute commands
```

Allowed on import:

```text
define dataclasses
load constants
define pure helper functions
expose public API
```

---

# 38. Simulated Dependency Test Contracts

Tests may use simulated upstream components when real upstream layers are unavailable. Simulations must be restrictive and explicit.

Allowed simulated dependencies:

```text
fake Policy / Capability Registry that denies by default
fake Security Sandbox that denies boundary violations
fake Failure Taxonomy that returns known failure classes
fake Tool / MCP Adapter event source with read-only records
fake clock for deterministic timestamps
fake artifact root under tmp_path
```

Rules:

```text
fakes must not allow behavior that real components would block
fakes must not write outside tmp_path or .agentx-init/monitoring/
fakes must not use network
fakes must not run raw shell
fakes must make denial behavior testable
```

A test pass using simulated dependencies does not prove live integration unless the review document later records real integration evidence.

---

# 39. Monitoring Self-Observation and Recursion Guard

Monitoring may observe its own failures, but it must not create recursive telemetry storms.

Allowed self-observation:

```text
monitoring write failure event
monitoring redaction failure event
monitoring retention failure event
monitoring schema rejection event
monitoring quota/backpressure event
monitoring self-health check record
```

Rules:

```text
self-observation records must use source_component = MonitoringObservability or a specific monitoring module
self-observation must include component_id = AGENTX_MONITORING_OBSERVABILITY
self-observation must be bounded and redacted
self-observation must not recursively trigger unlimited alert/event creation
recursion_depth must be tracked where recursive handling is possible
recursion_depth greater than 1 must produce one bounded FAILED or BLOCKED audit record and stop
monitoring failure must not be summarized as HEALTHY
monitoring-disabled state must be UNKNOWN or DEGRADED unless explicitly planned and evidenced
```

No-Go behavior:

```text
monitoring failure causes infinite event writes
monitoring redaction failure persists unsafe payload
monitoring-disabled state is summarized as HEALTHY
monitoring self-failure is silently ignored
```

---

# 40. Capacity, Quota, and Backpressure Rules

Monitoring must not grow without bounds or corrupt evidence when storage is constrained.

Required capacity controls:

```text
max_record_bytes
max_jsonl_file_bytes
max_latest_artifact_bytes
max_report_bytes
max_records_per_batch
max_rotation_files
```

Backpressure behavior:

```text
if a record exceeds max_record_bytes, summarize or block before persistence
if active log exceeds max_jsonl_file_bytes, rotate inside monitoring root or return BLOCKED
if rotation cannot run safely, write one bounded observability audit failure if possible
if disk write fails, return FAILED/BLOCKED and do not claim HEALTHY
if latest artifact cannot be written atomically, preserve previous latest artifact and record failure where possible
if evidence cannot be written, later review status must be DEGRADED, BLOCKED, or FAILED, not HEALTHY
```

Forbidden behavior:

```text
unbounded telemetry writes
unbounded report generation
unbounded in-memory buffering
silent metric/event dropping
silent latest artifact overwrite failure
source mutation to recover storage
network export to bypass local storage limits
```

---

# 41. Component Criticality and Health Derivation Rules

Health summaries must be derived from component criticality and evidence, not optimistic defaults.

Required component criticality levels:

```text
CRITICAL
HIGH
MEDIUM
LOW
OPTIONAL
UNKNOWN
```

Default critical components for Agent_X runtime health:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter
Monitoring / Observability
```

Status derivation rules:

```text
CRITICAL component FAILED -> overall FAILED
CRITICAL component BLOCKED -> overall BLOCKED unless failure is explicitly non-runtime
CRITICAL component UNKNOWN or stale -> overall DEGRADED or UNKNOWN
HIGH component FAILED -> overall DEGRADED unless it blocks active runtime path
OPTIONAL component UNKNOWN must not block overall status if explicitly optional and evidenced
missing critical component evidence must never produce HEALTHY
conflicting statuses use the strictest status unless policy-defined aggregation says otherwise
```

A health report must record:

```text
component_id
criticality
source evidence refs
last_seen_at
staleness_seconds
status_reason
failure_class, if failed/blocked/invalid
```

---

# 42. Schema Versioning and Compatibility Rules

Monitoring records must remain reviewable as schemas evolve.

Rules:

```text
every persisted record must include schema_version and schema_id
schema_version 1.0 is the initial accepted version
unknown major schema versions must be rejected or recorded as SCHEMA_REJECTION
unknown minor-compatible fields may be preserved only if redacted and bounded
schema migration must never rewrite historical JSONL in place
new schema versions require tests for old valid records and new valid records
completion evidence must record the schema versions used during validation
```

Compatibility statuses:

```text
COMPATIBLE
MINOR_FORWARD_COMPATIBLE
MAJOR_UNSUPPORTED
SCHEMA_UNKNOWN
SCHEMA_INVALID
```

No-Go behavior:

```text
historical records are silently rewritten
unknown major schema is treated as valid HEALTHY telemetry
schema version mismatch is ignored in final review evidence
```

---

# 43. Data Minimization and Sensitive Field Dropping Rules

Redaction is required, but it is not always sufficient. Monitoring must avoid collecting unnecessary sensitive details.

Data minimization rules:

```text
collect counts, statuses, IDs, hashes, and evidence refs before raw details
store references to artifacts rather than copying artifact contents
drop raw prompts, raw command output, raw file content, environment dumps, stack-local secrets, and provider payloads unless explicitly required and safely redacted
prefer failure_class and status_reason over raw exception blobs
prefer normalized path category over full path when full path is not needed
keep labels low-cardinality and non-sensitive
```

If a field is not needed for review, debugging, or reproducibility:

```text
drop it before persistence
record data_minimized=true where applicable
record dropped_fields_count where applicable
write an audit event for safety-based dropping when it affects review detail
```

Forbidden behavior:

```text
persisting complete environment variables
persisting raw provider responses
persisting raw prompts by default
persisting full command output when summary is enough
using redaction as an excuse to collect unnecessary sensitive data
```

---

# 44. Test Acceptance Criteria

Required tests:

```text
test_monitoring_event_schema_accepts_valid_event
test_monitoring_event_schema_rejects_missing_event_id
test_monitoring_event_schema_rejects_unknown_source_for_healthy_status
test_metric_record_schema_accepts_valid_metric
test_metric_record_schema_rejects_invalid_metric_type
test_health_check_schema_accepts_valid_check
test_alert_schema_accepts_valid_alert
test_trace_span_schema_accepts_valid_span
test_runtime_status_schema_accepts_valid_status
test_event_logger_writes_jsonl
test_latest_status_written_atomically
test_latest_health_report_written_atomically
test_redaction_removes_secret_values
test_unredacted_secret_payload_blocks_or_redacts
test_retention_rotation_stays_inside_monitoring_root
test_artifact_boundary_violation_blocks
test_monitoring_does_not_mutate_source
test_monitoring_does_not_require_network
test_health_check_command_blocks_without_safe_runner
test_metric_high_cardinality_labels_block_or_drop
test_metric_drop_writes_audit_event
test_alert_lifecycle_transition_is_evidenced
test_alert_deduplication_appends_recurrence
test_trace_correlation_preserves_upstream_ids
test_latest_status_marks_stale_data_degraded_or_unknown
test_missing_upstream_evidence_never_reports_healthy
test_jsonl_append_preserves_malformed_existing_lines
test_atomic_latest_write_does_not_leave_partial_final_artifact
test_evidence_manifest_records_sha256_hashes
test_report_builder_redacts_restricted_details
test_import_has_no_side_effects
test_simulated_policy_denies_by_default
test_monitoring_self_failure_is_bounded
test_recursion_guard_stops_recursive_event_storm
test_quota_exceeded_blocks_or_rotates_safely
test_disk_write_failure_does_not_report_healthy
test_unknown_major_schema_version_rejected
test_component_criticality_derives_overall_status
test_data_minimization_drops_unneeded_sensitive_fields
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema tests PASS
redaction tests PASS
retention/rotation tests PASS
artifact boundary tests PASS
source mutation tests PASS
no network required
no raw shell required
monitoring evidence written
```

---

# 45. Implementation Slices

Build this layer in small slices.

## 45.1 Slice A — Models and Schemas

Implement:

```text
monitoring_models.py
monitoring_event.schema.json
metric_record.schema.json
health_check.schema.json
health_report.schema.json
alert_record.schema.json
trace_span.schema.json
runtime_status.schema.json
observability_audit.schema.json
```

Acceptance:

```text
dataclasses instantiate
schemas validate valid examples
schemas reject missing required fields
schemas reject invalid enums
```

## 45.2 Slice B — Redaction and Event Logging

Implement:

```text
redaction.py
event_logger.py
```

Acceptance:

```text
secrets redacted
JSONL event writes work
latest artifacts use atomic writes
unsafe telemetry does not persist unredacted
```

## 45.3 Slice C — Metrics, Health, Status, Alerts

Implement:

```text
metrics_collector.py
health_checks.py
status_reporter.py
alert_manager.py
```

Acceptance:

```text
metrics written
health checks recorded
latest status written
latest health report written
alerts recorded locally only
missing evidence does not produce healthy status
```

## 45.4 Slice D — Tracing and Retention

Implement:

```text
trace_collector.py
retention_policy.py
```

Acceptance:

```text
trace spans written
rotation stays inside monitoring root
rotation action is audited
critical evidence is not silently deleted
```

## 45.5 Slice E — Evidence Manifest, Reports, and Completion Contract

Implement:

```text
monitoring_evidence_manifest.schema.json
monitoring_review_report.schema.json
completion_record.schema.json
report_builder.py
```

Acceptance:

```text
evidence manifest validates
review report validates
completion record validates
local reports are redacted
SHA-256 hashes recorded where required by review document
```

---

# 46. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical monitoring subdirectory is selected
[ ] runtime artifact root is selected
[ ] monitoring event schema is defined
[ ] metric schema is defined
[ ] health check schema is defined
[ ] alert schema is defined
[ ] trace/span schema is defined
[ ] runtime status schema is defined
[ ] redaction rules are defined
[ ] retention/rotation rules are defined
[ ] Failure Taxonomy integration is defined
[ ] Policy / Capability Registry integration is defined
[ ] Tool / MCP Adapter integration is defined
[ ] OpenCode borrowing boundaries are defined
[ ] report/export rules are defined
[ ] no network-by-default rule is accepted
[ ] no source-mutation rule is accepted
```

---

# 47. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] monitoring events validate
[ ] metrics validate
[ ] health checks validate
[ ] alerts validate
[ ] trace spans validate
[ ] runtime status validates
[ ] redaction works
[ ] retention/rotation works
[ ] artifact boundary is enforced
[ ] latest_status.json is atomic
[ ] latest_health_report.json is atomic
[ ] missing data is never summarized as HEALTHY
[ ] local reports are redacted
[ ] imports have no side effects
[ ] no source mutation occurs
[ ] no network is required
[ ] no raw shell is executed
[ ] monitoring evidence is written
[ ] monitoring self-failure is bounded and evidenced
capacity/quota/backpressure behavior is defined and tested
component criticality is recorded and used for status derivation
schema version compatibility is enforced
data minimization drops unneeded sensitive fields
completion record exists
```

---

# 48. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_MONITORING_OBSERVABILITY"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  monitoring_events_verified: []
  metric_records_verified: []
  health_checks_verified: []
  alerts_verified: []
  trace_spans_verified: []
  runtime_status_verified: []
  redaction_verified: []
  retention_rotation_verified: []
  report_generation_verified: []
  failure_taxonomy_integration_verified: []
  policy_integration_verified: []
  tool_mcp_adapter_integration_verified: []
  opencode_patterns_borrowed: []
  opencode_patterns_rejected_or_restricted: []
  deviations_from_contract: []
  unresolved_risks: []
```

---

# 49. Residual Risks

```yaml
residual_risks:
  - id: "MONITORING-RISK-001"
    description: "Monitoring may accidentally persist secrets."
    severity: "critical"
    mitigation: "Redaction occurs before persistence; redaction tests must prove secrets are removed."
  - id: "MONITORING-RISK-002"
    description: "Monitoring may become an unintended source mutation path."
    severity: "critical"
    mitigation: "All writes are restricted to .agentx-init/monitoring/ and source mutation tests must pass."
  - id: "MONITORING-RISK-003"
    description: "Health checks may become raw command execution."
    severity: "high"
    mitigation: "Command checks must use allowlisted safe command gates or return BLOCKED."
  - id: "MONITORING-RISK-004"
    description: "Telemetry may grow without bounds."
    severity: "medium"
    mitigation: "Retention and rotation rules must be implemented and audited."
  - id: "MONITORING-RISK-005"
    description: "Monitoring may expose internal runtime details through future MCP tools."
    severity: "high"
    mitigation: "No MCP exposure in v1; future exposure must be read-only, policy-checked, and redacted."
  - id: "MONITORING-RISK-006"
    description: "Missing upstream evidence may be misrepresented as healthy state."
    severity: "high"
    mitigation: "Missing evidence must produce UNKNOWN, DEGRADED, BLOCKED, or FAILED, never HEALTHY."
```

---

# 50. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
monitoring writes outside .agentx-init/monitoring/
monitoring mutates source
monitoring requires network by default
monitoring executes raw shell
monitoring exposes secrets
monitoring records unbounded raw output
monitoring silently deletes evidence
retention/rotation corrupts JSONL evidence
latest_status.json is not written atomically
alerts send network/email by default
health checks mutate system state
Policy / Capability Registry is bypassed for exposed monitoring reads
Tool / MCP Adapter is bypassed for exposed monitoring tools
Failure Taxonomy integration is skipped for failed monitoring records
missing upstream evidence is summarized as HEALTHY
UNKNOWN_SOURCE telemetry updates latest status as HEALTHY
local reports contain restricted raw details
imports create files, start threads, open sockets, or run checks
monitoring self-failure causes recursive telemetry storm
quota/write failure is silently ignored
unknown major schema version is treated as valid healthy telemetry
critical component missing evidence is summarized as HEALTHY
unnecessary sensitive fields are persisted instead of dropped
```

---

# 51. Definition of Done

The Monitoring / Observability Layer is done when it can provide safe, structured, local, redacted, and reproducible visibility into Agent_X runtime behavior.

It must prove:

```text
registered monitoring models exist
schemas validate monitoring events
schemas validate metric records
schemas validate health checks
schemas validate alerts
schemas validate trace spans
schemas validate runtime status records
telemetry is redacted before persistence
monitoring events are written as JSONL
metrics are written as JSONL
health checks are written as JSONL
alerts are written as JSONL
trace spans are written as JSONL
latest_status.json is written atomically
latest_health_report.json is written atomically
retention/rotation stays inside monitoring root
artifact boundary is enforced
source trust class is enforced
unknown sources fail closed or are rejected
missing evidence never reports HEALTHY
Failure Taxonomy integration exists
Policy / Capability Registry integration is respected
Tool / MCP Adapter integration is read-only and non-bypassing
local reports are redacted and non-networked
imports have no side effects
no source mutation occurs
no network is enabled by default
no raw shell is executed
monitoring self-failure is bounded and evidenced
capacity/quota/backpressure behavior is defined and tested
component criticality is recorded and used for status derivation
schema version compatibility is enforced
data minimization drops unneeded sensitive fields
completion record exists
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected runtime artifacts
```

---

# 52. Final Freeze Rule

This v4 document is frozen as the controlling contract for the Monitoring / Observability Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details for implementation spec
MAJOR: changed telemetry exposure policy, changed runtime artifact boundary, changed network policy, changed source-mutation policy, changed authority model, new required telemetry category
```

Blocked without major revision:

```text
allowing monitoring to mutate source
allowing network telemetry export by default
allowing raw shell diagnostics
removing redaction before persistence
removing schema validation
removing runtime artifact boundary
allowing alerts to send external messages by default
allowing MCP monitoring exposure without Tool / MCP Adapter policy
silently deleting critical evidence
allowing missing evidence to report HEALTHY
allowing import-time daemon or file-write side effects
removing recursion guard for monitoring self-failures
removing quota/backpressure controls
removing schema version compatibility checks
allowing unnecessary sensitive data collection by default
```

The next document should be:

```text
MONITORING_OBSERVABILITY_IMPLEMENTATION_SPEC.md
```

---

# 53. Final Rating

This v4 contract is rated:

```text
10/10
```

Reason:

```text
It preserves the v3 coverage and fixes the remaining operational-hardening gaps: monitoring self-observation and recursion guards, quota/capacity/backpressure behavior, component criticality and health derivation, schema version compatibility, data minimization and sensitive-field dropping, expanded negative tests, stronger No-Go conditions, and a final freeze rule suitable for the implementation spec handoff.
```
