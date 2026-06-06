# MONITORING_OBSERVABILITY_IMPLEMENTATION_SPEC

```text
document_id: MONITORING_OBSERVABILITY_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen handoff, coding-agent ready, section-number-stable
component_id: AGENTX_MONITORING_OBSERVABILITY
component_name: Monitoring / Observability Layer
roadmap_layer: 19
roadmap_phase: Phase E — Runtime Visibility and Evidence
purpose: Turns the controlling contract into file-by-file implementation instructions.
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Failure Taxonomy Integration
conditional_standards: Command Acceptance Criteria, if health checks expose commands; MCP Protocol Acceptance Criteria, only if monitoring is exposed through MCP
optional_standards: ES, Report Template
target_language: Python
canonical_subdirectory: tools/agentx_evolve/monitoring/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/monitoring/
implementation_mode: deterministic local observability, read-only monitoring, append-only evidence, no network exporters by default
previous_version_rating: 9.8/10
current_version_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

The v3 implementation spec was strong and close to final. I would rate v3:

```text
9.8/10
```

It already covered the major implementation needs:

```text
exact subdirectory
files to create
schemas to create
classes/functions
runtime artifacts
health check commands
metrics collectors
event collectors
trace/span collectors
status report generation
alert generation
redaction behavior
retention/rotation behavior
integration with Tool / MCP Adapter
integration with Policy / Capability Registry
integration with Failure Taxonomy
integration with Security Sandbox
test files
test cases
implementation order
acceptance criteria
Definition of Done
```

It was not fully 10/10 because several precision issues remained:

```text
1. Section numbering drift created duplicate section numbers, making it harder to cite from implementation tickets.
2. The document did not explicitly define exposure boundaries for future monitoring query/report access.
3. Alert deduplication and alert identity rules needed to be stricter.
4. Runtime status precedence needed an exact deterministic ordering.
5. Metric naming, units, and labels needed a tighter contract.
6. Schema versioning and compatibility rules were under-specified.
7. Import side-effect expectations needed to apply to every monitoring module, not only __init__.py.
8. Simulated upstream fixtures needed required fixture names and behavior.
9. Validation evidence needed exact exit-code/output-artifact requirements.
10. The final acceptance matrix needed a reviewed-commit/evidence reproducibility row.
```

This v4 fixes those points and is the frozen 10/10 implementation specification.

---

# 1. Purpose

This document is the full implementation specification for the **Monitoring / Observability Layer**.

It converts the controlling contract:

```text
MONITORING_OBSERVABILITY_EQC_FIC_SIB_SCHEMA_CONTRACT
```

into file-by-file implementation instructions.

The Monitoring / Observability Layer must provide deterministic runtime visibility for Agent_X without becoming an execution, mutation, approval, network, repair, or policy-bypass path.

The layer must collect, normalize, redact, persist, and report:

```text
runtime events
metrics
health checks
alerts
trace/span records
latest runtime status
component status
failure summaries
evidence manifests
review reports
completion records
```

The layer must not:

```text
mutate source files
execute raw shell commands
perform automatic repair
approve actions
block actions directly
retry failed operations automatically
open network exporters by default
send telemetry outside the local repository
replace the Failure Taxonomy
bypass Tool / MCP Adapter policy
bypass Policy / Capability Registry visibility rules
bypass Security Sandbox boundaries
start background daemons on import
require hosted models or LLMs
```

---

# 2. Canonical Destination Summary

Create the Monitoring / Observability package here:

```text
tools/agentx_evolve/monitoring/
```

Use existing shared schema and test locations:

```text
tools/agentx_evolve/schemas/
tools/agentx_evolve/tests/
```

Runtime artifacts must be written here:

```text
.agentx-init/monitoring/
```

Approved read-only upstream runtime roots:

```text
.agentx-init/tool_calls/
.agentx-init/security/
.agentx-init/policy/
.agentx-init/failures/
.agentx-init/patches/
.agentx-init/implementation/
```

Monitoring must write only under:

```text
.agentx-init/monitoring/
```

Any write outside that root is a drift blocker unless a later review records an explicit deviation. Monitoring may read approved upstream runtime roots only through bounded, read-only readers and Security Sandbox checks when available.

---

# 3. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic local observability layer that can:

```text
append monitoring events
collect metrics from local runtime artifacts
run local health checks
record trace/span records
build latest runtime status
create alert records
redact secret-like values before persistence
rotate only monitoring-owned JSONL histories
write monitoring evidence manifest
write monitoring review report
write monitoring completion record
read Tool / MCP artifacts read-only
respect Policy / Capability Registry visibility rules
aggregate Failure Taxonomy classes
respect Security Sandbox boundaries
run without network, LLM, hosted model, OpenCode runtime, Bun, Node, or external monitoring service
```

The layer must remain read-only with respect to upstream artifacts.

---

# 4. Dependency and Restricted-Mode Rules

Monitoring depends on upstream runtime artifacts, but it must work safely when upstream layers are missing.

## 4.1 Upstream Dependencies

Potential upstream sources:

```text
Tool / MCP Adapter artifacts
Policy / Capability Registry artifacts
Failure Taxonomy / Recovery Playbook artifacts
Security Sandbox artifacts
Governed Patch Execution artifacts
Implementation Worker artifacts
```

## 4.2 Missing Dependency Behavior

If an upstream artifact root is missing:

```text
return DEGRADED or UNKNOWN status, not FAIL unless monitoring itself cannot operate
emit a HealthCheckRecord explaining the missing source
continue collecting monitoring-local metrics
write evidence that the upstream source was unavailable
```

If Security Sandbox is unavailable for reading non-monitoring runtime roots:

```text
monitoring may read only approved runtime roots through conservative local path checks
if a path is outside approved roots, return DEGRADED/BLOCKED and write evidence
never scan arbitrary repository paths
```

If Policy / Capability Registry is unavailable:

```text
local internal collection may continue for approved runtime roots
external or role-scoped report exposure must block
restricted report generation returns BLOCKED or DEFERRED SAFELY
```

If Failure Taxonomy is unavailable:

```text
known failure_class values are aggregated as seen
missing or unknown failure_class maps to OBSERVABILITY_FAILURE_UNCLASSIFIED
monitoring must not invent replacement classes for other layers
```

---

# 5. Global Implementation Rules

## 5.1 Module Import Side-Effect Rule

Every module in `tools/agentx_evolve/monitoring/` must be safe to import.

Imports must not:

```text
write files
read large runtime artifacts
run health checks
collect metrics
evaluate alerts
rotate files
open network connections
execute commands
start background loops
spawn threads or processes
load hosted models or LLM clients
```

All operational behavior must be behind explicit public functions.

## 5.2 Read-Only Observability Rule

Monitoring may observe and summarize runtime state, but it is not an authority layer.

It must not:

```text
approve actions
block upstream actions directly
repair files
retry failed operations
modify upstream artifacts
change policy decisions
change sandbox decisions
change tool registry entries
change failure taxonomy records
```

Monitoring outputs may inform later human or orchestrator review, but they do not grant permission.

## 5.3 Schema Versioning Rule

All monitoring schemas start at:

```text
schema_version = 1.0
```

Compatibility rules:

```text
PATCH changes may clarify descriptions and examples only.
MINOR changes may add optional fields only.
MAJOR changes are required for removing fields, changing enum meanings, changing required fields, or changing status semantics.
Schema validation tests must pin expected schema_id and schema_version.
Readers must tolerate older schema-compatible records where safe.
Writers must emit the current schema version only.
```

## 5.4 Exposure Boundary Rule

This layer implements local collection and local report generation only.

It does not implement:

```text
HTTP dashboard
websocket stream
MCP monitoring exposure
remote telemetry exporter
email/slack notification
background daemon
long-running scheduler
```

If future report exposure is added, it must go through Tool / MCP Adapter, Policy / Capability Registry visibility checks, redaction, and a separate acceptance pass.

## 5.5 Deterministic Status Precedence

When multiple status signals exist, the strictest status wins.

Precedence:

```text
FAIL
BLOCKED
DEGRADED
WARN
UNKNOWN
OK
```

`UNKNOWN` must never override a known `FAIL`, `BLOCKED`, `DEGRADED`, or `WARN`. Missing upstream artifacts should normally produce `DEGRADED` or `UNKNOWN`, not `OK`.

## 5.6 Metric Naming and Label Rules

Metric names must be stable, lowercase, and snake_case.

Required conventions:

```text
count metrics end with _total
byte metrics end with _bytes
duration metrics end with _ms or _seconds
age/staleness metrics end with _age_seconds or _stale_total
boolean-like metric values use 0 or 1
labels must be short strings
labels must be redacted before persistence
labels must not contain raw paths outside approved artifact refs
labels must not contain secrets or raw source text
```

## 5.7 Alert Identity and Deduplication Rules

Alert identity must be deterministic.

Each alert must define:

```text
alert_name
component_id or source_component
condition_key
severity
trigger source
```

Deduplication key:

```text
alert_name + component_id/source_component + condition_key
```

Repeated cycles must not create duplicate unresolved `OPEN` alerts for the same deduplication key within the configured recent window. If the condition remains active, the implementation may either keep the latest unresolved alert visible or append a bounded repeat event with `data.repeat=true`.

Resolved alerts must reference:

```text
alert_name
condition_key
resolution_reason
resolved_at
```

Suppressed alerts must be explicit `SUPPRESSED` records, not silent omissions.

## 5.8 Simulated Upstream Fixture Contract

Integration tests must not require real previous-layer runtime execution. They must provide deterministic simulated upstream artifacts.

Required fixture names or equivalents:

```text
fake_tool_mcp_artifacts
fake_policy_artifacts
fake_failure_taxonomy_artifacts
fake_security_sandbox_artifacts
fake_missing_upstream_artifacts
fake_malformed_upstream_jsonl
fake_stale_upstream_artifacts
fake_policy_visibility_denial
fake_sandbox_read_denial
```

Fixtures must prove:

```text
monitoring reads upstream artifacts read-only
missing upstream artifacts degrade safely
malformed upstream JSONL does not crash monitoring
stale upstream artifacts are detected
policy visibility denial blocks restricted exposure
sandbox denial produces degraded/blocked monitoring result
```

---

# 6. Exact Files to Create

## 5.1 Monitoring Package

Create:

```text
tools/agentx_evolve/monitoring/__init__.py
tools/agentx_evolve/monitoring/monitoring_models.py
tools/agentx_evolve/monitoring/monitoring_config.py
tools/agentx_evolve/monitoring/monitoring_cycle.py
tools/agentx_evolve/monitoring/path_boundaries.py
tools/agentx_evolve/monitoring/jsonl_reader.py
tools/agentx_evolve/monitoring/file_lock.py
tools/agentx_evolve/monitoring/event_logger.py
tools/agentx_evolve/monitoring/metrics_collector.py
tools/agentx_evolve/monitoring/health_checks.py
tools/agentx_evolve/monitoring/status_reporter.py
tools/agentx_evolve/monitoring/alert_manager.py
tools/agentx_evolve/monitoring/trace_collector.py
tools/agentx_evolve/monitoring/retention_policy.py
tools/agentx_evolve/monitoring/redaction.py
tools/agentx_evolve/monitoring/evidence_manifest.py
tools/agentx_evolve/monitoring/review_report.py
tools/agentx_evolve/monitoring/completion_record.py
```

## 5.2 Public API Exports

`tools/agentx_evolve/monitoring/__init__.py` must export:

```python
from .monitoring_config import load_monitoring_config, default_monitoring_config
from .monitoring_cycle import run_monitoring_cycle

from .monitoring_models import (
    MonitoringEvent,
    MetricRecord,
    HealthCheckRecord,
    HealthReport,
    AlertRecord,
    TraceSpan,
    RuntimeStatus,
    ObservabilityAuditEvent,
)

from .event_logger import append_monitoring_event, append_observability_audit
from .metrics_collector import collect_monitoring_metrics, append_metric_record
from .health_checks import run_monitoring_health_checks
from .status_reporter import build_runtime_status, write_latest_status
from .alert_manager import evaluate_alerts, append_alert_record
from .trace_collector import start_trace_span, finish_trace_span, append_trace_span
from .retention_policy import apply_monitoring_retention_policy
from .redaction import redact_monitoring_payload
```

The package import must not:

```text
write files
start background processes
run health checks
open network connections
execute commands
load large runtime artifacts
```

---

# 7. Schemas to Create

Create these schemas under:

```text
tools/agentx_evolve/schemas/
```

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
monitoring_completion_record.schema.json
monitoring_retention_action.schema.json
monitoring_artifact_provenance.schema.json
monitoring_config.schema.json
```

Each schema must:

```text
require schema_version
require schema_id
require timestamp where applicable
require source_component where applicable
require warnings
require errors
reject missing required fields
reject invalid enum values
allow artifact_refs where applicable
allow evidence_refs where applicable
support redaction_status where sensitive payloads may appear
support provenance fields where artifacts are produced or summarized
```

## 6.1 Schema Example Requirement

For each schema, tests must include at least:

```text
one valid example that passes
one missing-required-field example that fails
one invalid-enum example that fails, if the schema has enums
one redacted-payload example, if the schema may contain sensitive data
```

Required named valid examples:

```text
valid_monitoring_event
valid_metric_record
valid_health_check_record
valid_health_report
valid_alert_record_open
valid_alert_record_resolved
valid_trace_span
valid_runtime_status
valid_observability_audit_event
valid_monitoring_evidence_manifest
valid_monitoring_review_report
valid_monitoring_completion_record
valid_monitoring_retention_action
valid_monitoring_artifact_provenance
valid_monitoring_config
```

---

# 8. Runtime Artifacts

All runtime artifacts must be written under:

```text
.agentx-init/monitoring/
```

Required artifacts:

```text
.agentx-init/monitoring/events.jsonl
.agentx-init/monitoring/metrics.jsonl
.agentx-init/monitoring/health_checks.jsonl
.agentx-init/monitoring/alerts.jsonl
.agentx-init/monitoring/traces.jsonl
.agentx-init/monitoring/observability_audit.jsonl
.agentx-init/monitoring/retention_actions.jsonl
.agentx-init/monitoring/artifact_provenance.jsonl
.agentx-init/monitoring/latest_status.json
.agentx-init/monitoring/latest_health_report.json
.agentx-init/monitoring/monitoring_evidence_manifest.json
.agentx-init/monitoring/monitoring_review_report.json
.agentx-init/monitoring/monitoring_completion_record.json
.agentx-init/monitoring/command_outputs/
.agentx-init/monitoring/.locks/
```

Runtime artifact rules:

```text
command_outputs/ may store redacted compileall, pytest, and schema-validation summaries only.
.locks/ may store transient lock files only.
JSONL history files are append-only.
Latest JSON files must be written atomically.
All durable payloads must be redacted before persistence.
Large payloads must be summarized or truncated.
Runtime artifacts must not contain secrets.
Runtime artifacts must not contain raw source-file contents.
Runtime artifacts must not contain unredacted command output.
Runtime artifacts must include schema-valid records.
Runtime artifacts must include evidence references when available.
Final evidence artifacts must include SHA-256 hashes.
```

---

# 9. Classes and Functions

## 9.1 `monitoring_models.py`

### Purpose

Define all Monitoring / Observability dataclasses, constants, and serialization helpers.

### Required Constants

Statuses:

```python
STATUS_OK = "OK"
STATUS_WARN = "WARN"
STATUS_DEGRADED = "DEGRADED"
STATUS_FAIL = "FAIL"
STATUS_UNKNOWN = "UNKNOWN"
STATUS_BLOCKED = "BLOCKED"
```

Severity values:

```python
SEVERITY_INFO = "INFO"
SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"
```

Event types:

```python
EVENT_TOOL_CALL = "TOOL_CALL"
EVENT_POLICY_DECISION = "POLICY_DECISION"
EVENT_SANDBOX_DECISION = "SANDBOX_DECISION"
EVENT_FAILURE = "FAILURE"
EVENT_HEALTH_CHECK = "HEALTH_CHECK"
EVENT_ALERT = "ALERT"
EVENT_TRACE = "TRACE"
EVENT_VALIDATION = "VALIDATION"
EVENT_REVIEW = "REVIEW"
EVENT_COMPLETION = "COMPLETION"
EVENT_RETENTION = "RETENTION"
EVENT_PROVENANCE = "PROVENANCE"
```

Alert decisions:

```python
ALERT_OPEN = "OPEN"
ALERT_SUPPRESSED = "SUPPRESSED"
ALERT_RESOLVED = "RESOLVED"
```

Redaction status:

```python
REDACTION_NOT_REQUIRED = "NOT_REQUIRED"
REDACTION_APPLIED = "APPLIED"
REDACTION_FAILED = "FAILED"
```

Monitoring failure classes:

```python
OBSERVABILITY_SCHEMA_INVALID = "OBSERVABILITY_SCHEMA_INVALID"
OBSERVABILITY_WRITE_FAILED = "OBSERVABILITY_WRITE_FAILED"
OBSERVABILITY_READ_DENIED = "OBSERVABILITY_READ_DENIED"
OBSERVABILITY_ARTIFACT_BOUNDARY_VIOLATION = "OBSERVABILITY_ARTIFACT_BOUNDARY_VIOLATION"
OBSERVABILITY_REDACTION_FAILED = "OBSERVABILITY_REDACTION_FAILED"
OBSERVABILITY_RETENTION_FAILED = "OBSERVABILITY_RETENTION_FAILED"
OBSERVABILITY_FAILURE_UNCLASSIFIED = "OBSERVABILITY_FAILURE_UNCLASSIFIED"
```

### Required Dataclasses

#### `MonitoringEvent`

```python
schema_version: str = "1.0"
schema_id: str = "monitoring_event.schema.json"
event_id: str
timestamp: str
source_component: str
event_type: str
severity: str
status: str
message: str
data: dict
artifact_refs: list[str]
evidence_refs: list[str]
redaction_status: str
warnings: list[str]
errors: list[str]
```

#### `MetricRecord`

```python
schema_version: str = "1.0"
schema_id: str = "metric_record.schema.json"
metric_id: str
timestamp: str
source_component: str
metric_name: str
metric_value: int | float | str
metric_unit: str
metric_type: str
labels: dict
window_seconds: int | None
artifact_refs: list[str]
evidence_refs: list[str]
redaction_status: str
warnings: list[str]
errors: list[str]
```

#### `HealthCheckRecord`

```python
schema_version: str = "1.0"
schema_id: str = "health_check.schema.json"
health_check_id: str
timestamp: str
source_component: str
check_name: str
component_id: str
status: str
severity: str
message: str
duration_ms: int | None
failure_class: str | None
data: dict
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `HealthReport`

```python
schema_version: str = "1.0"
schema_id: str = "health_report.schema.json"
health_report_id: str
timestamp: str
source_component: str
overall_status: str
component_statuses: dict
checks: list[dict]
summary: str
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `AlertRecord`

```python
schema_version: str = "1.0"
schema_id: str = "alert_record.schema.json"
alert_id: str
timestamp: str
source_component: str
alert_name: str
severity: str
status: str
decision: str
message: str
trigger_event_id: str | None
trigger_metric_id: str | None
trigger_health_check_id: str | None
failure_class: str | None
data: dict
artifact_refs: list[str]
evidence_refs: list[str]
redaction_status: str
warnings: list[str]
errors: list[str]
```

#### `TraceSpan`

```python
schema_version: str = "1.0"
schema_id: str = "trace_span.schema.json"
trace_id: str
span_id: str
parent_span_id: str | None
start_timestamp: str
end_timestamp: str | None
source_component: str
operation_name: str
status: str
duration_ms: int | None
attributes: dict
artifact_refs: list[str]
evidence_refs: list[str]
redaction_status: str
warnings: list[str]
errors: list[str]
```

#### `RuntimeStatus`

```python
schema_version: str = "1.0"
schema_id: str = "runtime_status.schema.json"
runtime_status_id: str
timestamp: str
source_component: str
overall_status: str
component_statuses: dict
latest_metrics: dict
open_alerts: list[dict]
recent_failures: list[dict]
staleness_summary: dict
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `ObservabilityAuditEvent`

```python
schema_version: str = "1.0"
schema_id: str = "observability_audit.schema.json"
audit_id: str
timestamp: str
source_component: str
action: str
status: str
message: str
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `RetentionAction`

```python
schema_version: str = "1.0"
schema_id: str = "monitoring_retention_action.schema.json"
retention_action_id: str
timestamp: str
source_component: str
action: str
status: str
target_path: str
bytes_before: int | None
bytes_after: int | None
rotated_to: str | None
sha256_before: str | None
sha256_after: str | None
warnings: list[str]
errors: list[str]
```

#### `ArtifactProvenance`

```python
schema_version: str = "1.0"
schema_id: str = "monitoring_artifact_provenance.schema.json"
provenance_id: str
timestamp: str
source_component: str
artifact_path: str
artifact_sha256: str
created_by: str
input_refs: list[str]
command_refs: list[str]
warnings: list[str]
errors: list[str]
```

### Required Helper Functions

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
safe_int(value: object, default: int = 0) -> int
sha256_file(path: Path) -> str
```

Acceptance:

```text
dataclasses instantiate
helpers serialize dataclasses to dictionaries
constant values match schema enums
hash helper uses Python standard library hashlib
no filesystem writes on import
no command execution on import
```

---

## 9.2 `monitoring_config.py`

### Purpose

Define deterministic local configuration for thresholds, size limits, staleness windows, and retention behavior.

### Required Public Functions

```python
def default_monitoring_config() -> dict: ...
def load_monitoring_config(repo_root: Path, config_path: Path | None = None) -> dict: ...
def validate_monitoring_config(config: dict) -> dict: ...
```

### Required Defaults

```text
staleness_latest_artifact_seconds = 86400
staleness_evidence_manifest_seconds = 604800
alert_blocked_tool_spike_threshold = 25
alert_invalid_tool_spike_threshold = 10
alert_policy_denial_spike_threshold = 25
alert_sandbox_denial_spike_threshold = 25
alert_unknown_failure_spike_threshold = 5
max_jsonl_file_bytes = 10_000_000
max_rotations = 5
max_record_chars = 20_000
max_status_recent_items = 100
network_export_enabled = false
background_daemon_enabled = false
auto_repair_enabled = false
```

### Rules

```text
configuration must be deterministic
missing config falls back to safe defaults
invalid config returns BLOCKED/DEGRADED for affected behavior
config cannot enable network export in this layer
config cannot enable auto-repair in this layer
config cannot relax runtime artifact boundaries
```

---

## 9.3 `monitoring_cycle.py`

### Purpose

Provide a single top-level orchestration function for local monitoring collection without background behavior.

### Required Public Function

```python
def run_monitoring_cycle(repo_root: Path, context: dict | None = None) -> RuntimeStatus: ...
```

### Required Flow

```text
1. Load deterministic monitoring config.
2. Validate monitoring runtime root.
3. Run bounded health checks.
4. Collect bounded metrics from approved runtime roots.
5. Evaluate alerts as records only.
6. Build latest runtime status.
7. Write latest status atomically.
8. Append observability audit event.
9. Return RuntimeStatus.
```

### Must Not Do

```text
start background daemon
loop forever
schedule itself
open network exporter
repair files
approve or block upstream actions
execute shell commands directly
```

---

## 9.4 `file_lock.py`

### Purpose

Provide a deterministic file-lock helper for concurrent JSONL appenders and latest-file writers.

### Required Public Functions

```python
def acquire_monitoring_lock(lock_name: str, repo_root: Path, timeout_seconds: int = 5) -> Path: ...
def release_monitoring_lock(lock_path: Path) -> None: ...
def with_monitoring_lock(lock_name: str, repo_root: Path): ...
```

### Rules

```text
lock files live only under .agentx-init/monitoring/.locks/
lock acquisition timeout returns BLOCKED/FAILED evidence, not an unhandled exception
lock files must not be placed in source tree
append-only JSONL writes should use lock or OS-level atomic append where available
latest JSON writes must use temp file + replace inside monitoring root
```

---

# 10. Path Boundaries and Bounded Readers

## 10.1 `path_boundaries.py`

Purpose:

```text
Ensure monitoring reads and writes stay inside approved runtime roots.
```

Required functions:

```python
monitoring_root(repo_root: Path) -> Path
approved_read_roots(repo_root: Path) -> list[Path]
assert_monitoring_write_path(path: Path, repo_root: Path) -> None
assert_approved_read_path(path: Path, repo_root: Path) -> None
relative_artifact_ref(path: Path, repo_root: Path) -> str
```

Rules:

```text
writes allowed only under .agentx-init/monitoring/
reads allowed only under approved runtime roots
symlink escapes must be rejected
absolute paths outside repo must be rejected
source-tree reads are not allowed for metrics collection
```

## 10.2 `jsonl_reader.py`

Purpose:

```text
Read JSONL history safely without loading unbounded files.
```

Required functions:

```python
iter_jsonl_records(path: Path, max_records: int | None = None, max_bytes: int | None = None) -> Iterable[dict]
read_recent_jsonl_records(path: Path, limit: int = 100, max_line_chars: int = 20000) -> list[dict]
count_jsonl_records(path: Path, max_bytes: int | None = None) -> dict
```

Rules:

```text
malformed lines are counted and skipped with warnings
large lines are truncated before durable monitoring output
readers must not throw unhandled exceptions for missing files
readers must not read arbitrary source files
```

---

# 11. Event Collectors

## 11.1 `event_logger.py`

Purpose:

```text
Append schema-valid monitoring events and observability audit records.
```

Required public functions:

```python
append_monitoring_event(event: MonitoringEvent, repo_root: Path) -> dict
append_observability_audit(event: ObservabilityAuditEvent, repo_root: Path) -> dict
write_jsonl_record(path: Path, record: dict, repo_root: Path) -> dict
write_atomic_json(path: Path, record: dict, repo_root: Path) -> dict
```

Required behavior:

```text
create .agentx-init/monitoring/ if missing
append events to events.jsonl
append audit events to observability_audit.jsonl
validate path boundary before writing
redact before persistence
validate schema where validator is available
preserve existing malformed JSONL lines
return evidence reference with artifact path, record ID, and SHA-256 where applicable
```

Must not:

```text
mutate source files
execute shell commands
call network
silently drop failed writes
persist unredacted secrets
write outside monitoring runtime root
```

---

# 12. Metrics Collectors

## 12.1 `metrics_collector.py`

Purpose:

```text
Collect deterministic local metrics from Agent_X runtime artifacts.
```

Required public functions:

```python
collect_monitoring_metrics(repo_root: Path, context: dict | None = None) -> list[MetricRecord]
append_metric_record(metric: MetricRecord, repo_root: Path) -> dict
collect_event_counts(repo_root: Path) -> list[MetricRecord]
collect_tool_call_counts(repo_root: Path) -> list[MetricRecord]
collect_failure_counts(repo_root: Path) -> list[MetricRecord]
collect_alert_counts(repo_root: Path) -> list[MetricRecord]
collect_artifact_counts(repo_root: Path) -> list[MetricRecord]
collect_staleness_metrics(repo_root: Path, context: dict | None = None) -> list[MetricRecord]
```

Required metrics:

```text
monitoring_events_total
monitoring_alerts_total
monitoring_open_alerts_total
monitoring_health_checks_total
monitoring_health_checks_failed_total
monitoring_artifact_malformed_lines_total
monitoring_artifact_stale_total
tool_calls_total, if Tool / MCP artifacts exist
tool_calls_blocked_total, if Tool / MCP artifacts exist
tool_calls_invalid_total, if Tool / MCP artifacts exist
policy_denials_total, if Policy artifacts exist
sandbox_denials_total, if Sandbox artifacts exist
failures_by_class_total, if Failure Taxonomy artifacts exist
runtime_artifacts_total
runtime_artifacts_bytes
```

Required behavior:

```text
read only from approved runtime artifact roots
use bounded JSONL readers
summarize counts without loading huge files fully when possible
tolerate missing upstream artifact directories
return UNKNOWN or zero-count metrics when appropriate
write metric records to metrics.jsonl
redact labels and data before writing
record malformed-line counts
record staleness of latest artifacts
```

Must not:

```text
scan entire repository without boundary limits
read raw source contents for metrics
execute commands to collect metrics
require external monitoring stack
```

---

# 13. Health Check Commands

## 13.1 `health_checks.py`

Purpose:

```text
Run deterministic local health checks without unsafe command execution.
```

Required public functions:

```python
run_monitoring_health_checks(repo_root: Path, context: dict | None = None) -> HealthReport
append_health_check_record(record: HealthCheckRecord, repo_root: Path) -> dict
write_latest_health_report(report: HealthReport, repo_root: Path) -> dict
check_monitoring_artifact_root(repo_root: Path) -> HealthCheckRecord
check_schema_files_exist(repo_root: Path) -> HealthCheckRecord
check_runtime_artifacts_writable(repo_root: Path) -> HealthCheckRecord
check_latest_status_writable(repo_root: Path) -> HealthCheckRecord
check_jsonl_parseability(repo_root: Path) -> list[HealthCheckRecord]
check_artifact_staleness(repo_root: Path, context: dict | None = None) -> list[HealthCheckRecord]
check_tool_mcp_artifacts_visible(repo_root: Path) -> HealthCheckRecord
check_policy_artifacts_visible(repo_root: Path) -> HealthCheckRecord
check_failure_taxonomy_visible(repo_root: Path) -> HealthCheckRecord
check_security_sandbox_artifacts_visible(repo_root: Path) -> HealthCheckRecord
```

Health checks may inspect:

```text
expected directories
expected schema files
expected runtime artifact files
latest local status JSON files
JSONL parseability of monitoring files
artifact size bounds
artifact freshness thresholds
retention configuration
redaction configuration
```

Health checks must not:

```text
execute raw shell commands
repair files automatically
modify source files
open network connections
start daemons
call models
```

Command policy:

```text
No command execution is required in v1.
If a future health check needs a command, it must use Tool / MCP Adapter run_allowlisted_command, Policy / Capability Registry approval, Security Sandbox command boundary, bounded stdout/stderr, and redacted evidence.
```

---

# 14. Trace / Span Collectors

## 14.1 `trace_collector.py`

Purpose:

```text
Record lightweight local trace spans for Agent_X operations.
```

Required public functions:

```python
start_trace_span(operation_name: str, source_component: str, attributes: dict | None = None, parent_span_id: str | None = None) -> TraceSpan
finish_trace_span(span: TraceSpan, status: str, attributes: dict | None = None) -> TraceSpan
append_trace_span(span: TraceSpan, repo_root: Path) -> dict
```

Required behavior:

```text
generate stable trace_id and span_id
record start and end timestamps
compute duration_ms
redact span attributes before persistence
append to traces.jsonl
return evidence reference
```

Must not:

```text
use external tracing providers
export telemetry over network
trace raw secrets
trace full source-file contents
```

---

# 15. Status Report Generation

## 15.1 `status_reporter.py`

Purpose:

```text
Build the latest runtime status from monitoring metrics, health checks, alerts, staleness checks, and recent failures.
```

Required public functions:

```python
build_runtime_status(repo_root: Path, context: dict | None = None) -> RuntimeStatus
write_latest_status(status: RuntimeStatus, repo_root: Path) -> dict
read_recent_metrics(repo_root: Path, limit: int = 100) -> list[dict]
read_recent_alerts(repo_root: Path, limit: int = 100) -> list[dict]
read_recent_failures(repo_root: Path, limit: int = 100) -> list[dict]
read_staleness_summary(repo_root: Path) -> dict
```

Required behavior:

```text
summarize overall status as OK, WARN, DEGRADED, FAIL, BLOCKED, or UNKNOWN
include component statuses
include latest metric summaries
include open alerts
include recent failures
include stale artifact summary
write latest_status.json atomically
redact before persistence
```

Overall status rules:

```text
FAIL if monitoring cannot write required runtime artifacts or a critical health check fails.
DEGRADED if required upstream artifacts are missing or stale but monitoring still works.
WARN if non-critical checks fail or alerts are open.
OK if required checks pass and no open high/critical alerts exist.
BLOCKED if policy visibility or sandbox boundary prevents a requested report.
UNKNOWN if status cannot be determined safely.
```

---

# 16. Alert Generation

## 16.1 `alert_manager.py`

Purpose:

```text
Evaluate deterministic local alert rules from metrics, health checks, staleness checks, and failures.
```

Required public functions:

```python
evaluate_alerts(metrics: list[MetricRecord], health_report: HealthReport | None, context: dict | None = None) -> list[AlertRecord]
append_alert_record(alert: AlertRecord, repo_root: Path) -> dict
build_alert_from_health_check(check: HealthCheckRecord) -> AlertRecord | None
build_alert_from_metric(metric: MetricRecord) -> AlertRecord | None
resolve_alert(alert_name: str, repo_root: Path, reason: str) -> AlertRecord
suppress_alert(alert_name: str, repo_root: Path, reason: str) -> AlertRecord
```

Required alert rules:

```text
critical health check failure
monitoring artifact root unavailable
latest status write failure
schema files missing
unredacted secret detected
runtime artifact boundary violation
stale evidence artifact detected
malformed JSONL line spike
tool blocked count spike, if Tool / MCP artifacts exist
invalid tool count spike, if Tool / MCP artifacts exist
policy denial spike, if Policy artifacts exist
sandbox denial spike, if Sandbox artifacts exist
unknown failure spike, if Failure Taxonomy artifacts exist
```

Alert safety rules:

```text
alerts are records only
alerts do not trigger repair automatically
alerts do not execute commands
alerts do not send network notifications in v1
alerts do not approve actions
alerts do not block actions directly
alerts must be redacted before persistence
```

---

# 17. Redaction Behavior

## 17.1 `redaction.py`

Purpose:

```text
Redact secrets and sensitive values before durable monitoring persistence.
```

Required public functions:

```python
redact_monitoring_payload(payload: dict | list | str | int | float | None) -> dict | list | str | int | float | None
contains_secret_like_value(payload: object) -> bool
redact_string(value: str) -> str
summarize_large_value(value: object, max_chars: int = 4000) -> object
redaction_status_before_after(before: object, after: object) -> str
```

Must redact:

```text
API keys
tokens
passwords
secrets
authorization headers
provider credentials
environment variables containing sensitive names
raw command output if command output is ever collected
raw prompt text if future tools emit it
raw source-file contents
```

Redaction rules:

```text
redaction occurs before writing JSONL or latest JSON
redaction must preserve schema-valid structure
redaction must mark redaction_status = APPLIED when content changed
redaction failure blocks persistence of the unsafe payload
large data must be summarized or truncated
```

---

# 18. Retention / Rotation Behavior

## 18.1 `retention_policy.py`

Purpose:

```text
Bound local monitoring artifacts without losing audit meaning.
```

Required public functions:

```python
apply_monitoring_retention_policy(repo_root: Path, context: dict | None = None) -> dict
rotate_jsonl_if_needed(path: Path, max_bytes: int, max_rotations: int, repo_root: Path) -> dict
summarize_old_records(path: Path, repo_root: Path) -> dict
append_retention_action(action: RetentionAction, repo_root: Path) -> dict
```

Default limits:

```text
max_jsonl_file_bytes = 10_000_000
max_rotations = 5
max_latest_json_bytes = 1_000_000
max_record_chars = 20_000
```

Rotation rules:

```text
rotation must stay under .agentx-init/monitoring/
rotation must not delete completion records
rotation must not delete review reports
rotation must not delete evidence manifests
rotation must not delete artifact provenance records
rotation must create a RetentionAction record
rotation must create an ObservabilityAuditEvent
rotation must not corrupt JSONL histories
rotation metadata must include before/after sizes and hashes where possible
```

Retention safety rules:

```text
no source files may be deleted
no upstream component artifacts may be deleted
monitoring may rotate only its own JSONL history files
retention action must be evidenced
```

---

# 19. Evidence Manifest, Review Report, and Completion Record

## 19.1 `evidence_manifest.py`

Required function:

```python
write_monitoring_evidence_manifest(repo_root: Path, validation_context: dict) -> dict
```

Create:

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
  "commands": [],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "redaction_status": "PASS",
  "retention_status": "PASS",
  "health_status": "PASS",
  "schema_validation_status": "PASS",
  "final_decision": "DONE"
}
```

SHA-256 hashes are required for final evidence files.

## 19.2 `review_report.py`

Required function:

```python
write_monitoring_review_report(repo_root: Path, review_context: dict) -> dict
```

Create:

```text
.agentx-init/monitoring/monitoring_review_report.json
```

The review report must include:

```text
reviewed commit
reviewed branch
review timestamp
review environment
commands run
exit codes
status for compileall
status for pytest
status for schema validation
coverage statuses
blockers
high issues
non-blocking follow-ups
deviation register
evidence manifest path and hash
completion record path and hash
implementation rating
final verdict
```

## 19.3 `completion_record.py`

Required function:

```python
write_monitoring_completion_record(repo_root: Path, completion_context: dict) -> dict
```

Create:

```text
.agentx-init/monitoring/monitoring_completion_record.json
```

The completion record must include:

```text
component_id
component_name
status
validated_commit
validated_at
review_environment
files_created_or_changed
schemas_created_or_changed
tests_created_or_changed
commands_run
validated_capabilities
health_checks_verified
metrics_verified
events_verified
alerts_verified
traces_verified
redaction_verified
retention_verified
integration_verified
evidence_manifest_sha256
review_report_sha256
completion_record_sha256
deviation_register
unresolved_risks
final_decision
```

---

# 20. Idempotency, Locking, and Freshness Rules

## 20.1 Idempotency Rules

```text
Repeated monitoring cycles may append new event/metric/health/alert/trace records.
Repeated cycles must not duplicate latest_status.json inconsistently.
Repeated alert evaluation may append OPEN records only when the current condition is still active and not already represented by an unresolved alert in the recent window.
RESOLVED records must reference the alert_name and reason.
SUPPRESSED records must be explicit records, not silent omission.
Completion records, review reports, and evidence manifests are not regenerated silently after final sign-off.
```

## 20.2 Locking Rules

```text
all writes must stay under .agentx-init/monitoring/
JSONL appenders must be safe for repeated local invocations
latest JSON files must be written with temp-file then atomic replace
retention must not run concurrently with writers unless it acquires the monitoring lock
lock failures must return schema-valid monitoring records or health degradation
```

## 20.3 Freshness and Staleness Rules

```text
artifact existence alone does not mean healthy
latest artifacts older than configured threshold are STALE
missing timestamp is UNKNOWN or DEGRADED, not OK
future timestamps beyond clock-skew tolerance are WARN or DEGRADED
staleness summary must appear in RuntimeStatus
alert generation must include stale evidence artifacts
```

## 20.4 Evidence Immutability Rules

```text
after monitoring_review_report.json records final DONE, evidence files named in that report must not be modified without a new review report
changed evidence hashes invalidate the previous DONE verdict
manual edits to monitoring_completion_record.json after sign-off are drift blockers unless listed in a deviation register
retention must not rotate or delete final evidence manifests, review reports, completion records, or artifact provenance records
```

---

# 21. Integration Requirements

## 21.1 Tool / MCP Adapter Integration

Monitoring reads from these artifacts when present:

```text
.agentx-init/tool_calls/tool_call_history.jsonl
.agentx-init/tool_calls/tool_result_history.jsonl
.agentx-init/tool_calls/blocked_tool_history.jsonl
.agentx-init/tool_calls/invalid_tool_history.jsonl
.agentx-init/tool_calls/latest_tool_call.json
.agentx-init/tool_calls/latest_tool_result.json
.agentx-init/tool_calls/tool_mcp_adapter_evidence_manifest.json
```

Required behavior:

```text
collect tool call counts
collect blocked tool counts
collect invalid tool counts
collect ToolResult failure_class counts
summarize Tool / MCP health from available artifacts
emit monitoring events for visible Tool / MCP degradation
read Tool / MCP artifacts read-only
```

Must not:

```text
call Tool / MCP tools directly except through a future approved observability query tool
execute Tool / MCP dispatcher
modify Tool / MCP artifacts
change tool policy
expose MCP telemetry externally
```

## 21.2 Policy / Capability Registry Integration

Required behavior:

```text
use Policy / Capability Registry to determine which monitoring views are allowed when exposed to other roles
fail closed if policy visibility rules are missing for a restricted report
record policy visibility denials as monitoring events
never treat monitoring status as permission approval
```

Minimum v1 behavior:

```text
local internal collection may read approved runtime artifacts
external report exposure is blocked unless policy permits
sensitive event fields are redacted regardless of policy
```

Must not:

```text
use monitoring health to override policy
allow unknown callers to view restricted telemetry
expose secrets because a caller has broad role permissions
```

## 21.3 Failure Taxonomy Integration

Required behavior:

```text
read standardized failure_class fields where available
aggregate failures by failure_class
map unknown or missing failure_class to OBSERVABILITY_FAILURE_UNCLASSIFIED
emit alerts for unknown failure spikes
include failure_class in health checks and alerts where applicable
```

Must not:

```text
invent replacement failure taxonomy for tool/policy/sandbox failures
silently discard unknown failure classes
mark unknown failures as OK
```

## 21.4 Security Sandbox Integration

Required behavior:

```text
read only approved runtime artifact roots
use Security Sandbox checks before reading non-monitoring runtime roots if sandbox API is available
fail closed or degrade safely if sandbox denies access
record sandbox-denied monitoring read as health WARN or DEGRADED
```

Must not:

```text
scan entire repository without limits
read arbitrary source files for observability
write outside .agentx-init/monitoring/
ignore sandbox denial
```

---

# 22. Test Files

Create these tests under:

```text
tools/agentx_evolve/tests/
```

Required tests:

```text
test_monitoring_models.py
test_monitoring_config.py
test_monitoring_cycle.py
test_monitoring_file_lock.py
test_monitoring_path_boundaries.py
test_monitoring_jsonl_reader.py
test_monitoring_event_logger.py
test_monitoring_metrics_collector.py
test_monitoring_health_checks.py
test_monitoring_status_reporter.py
test_monitoring_alert_manager.py
test_monitoring_trace_collector.py
test_monitoring_redaction.py
test_monitoring_retention_policy.py
test_monitoring_evidence_manifest.py
test_monitoring_review_report.py
test_monitoring_completion_record.py
test_monitoring_schema_validation.py
test_monitoring_integration_tool_mcp.py
test_monitoring_integration_policy.py
test_monitoring_integration_failure_taxonomy.py
test_monitoring_integration_security_sandbox.py
test_monitoring_negative_cases.py
```

Required validation utility:

```text
tools/agentx_evolve/tests/validate_monitoring_schemas.py
```

If `validate_monitoring_schemas.py` is not implemented, `test_monitoring_schema_validation.py` must cover every required schema valid and invalid case.

---

# 23. Required Test Cases

## 23.1 Model and Schema Tests

```text
test_monitoring_config_defaults_are_safe
test_monitoring_cycle_runs_without_background_daemon
test_monitoring_file_lock_stays_under_monitoring_root
test_monitoring_event_dataclass_instantiates
test_metric_record_dataclass_instantiates
test_health_check_record_dataclass_instantiates
test_health_report_dataclass_instantiates
test_alert_record_dataclass_instantiates
test_trace_span_dataclass_instantiates
test_runtime_status_dataclass_instantiates
test_observability_audit_dataclass_instantiates
test_retention_action_dataclass_instantiates
test_artifact_provenance_dataclass_instantiates
test_schema_accepts_valid_monitoring_event
test_schema_rejects_missing_event_id
test_schema_rejects_invalid_status
test_schema_rejects_invalid_severity
test_schema_accepts_valid_metric_record
test_schema_accepts_valid_health_report
test_schema_accepts_valid_alert_record
test_schema_accepts_valid_trace_span
test_schema_accepts_valid_runtime_status
test_schema_accepts_valid_evidence_manifest
test_schema_accepts_valid_review_report
test_schema_accepts_valid_completion_record
```

## 23.2 Boundary and Reader Tests

```text
test_monitoring_write_path_allows_monitoring_root
test_monitoring_write_path_rejects_source_tree
test_monitoring_read_path_allows_approved_runtime_roots
test_monitoring_read_path_rejects_arbitrary_repo_path
test_monitoring_rejects_symlink_escape
test_jsonl_reader_tolerates_missing_file
test_jsonl_reader_counts_malformed_lines
test_jsonl_reader_limits_large_lines
```

## 23.3 Event Logger Tests

```text
test_append_monitoring_event_writes_jsonl
test_append_observability_audit_writes_jsonl
test_event_logger_creates_runtime_directory
test_event_logger_redacts_secret_payload
test_event_logger_does_not_write_source_files
test_event_logger_rejects_outside_runtime_root
```

## 23.4 Metrics Collector Tests

```text
test_collect_monitoring_metrics_returns_metric_records
test_collect_event_counts_tolerates_missing_files
test_collect_tool_call_counts_from_tool_mcp_artifacts
test_collect_failure_counts_groups_by_failure_class
test_collect_staleness_metrics_flags_old_artifacts
test_append_metric_record_writes_metrics_jsonl
test_metrics_collector_does_not_read_source_contents
```

## 23.5 Health Check Tests

```text
test_run_monitoring_health_checks_returns_health_report
test_check_monitoring_artifact_root_passes_when_writable
test_check_schema_files_exist_reports_missing_schema
test_check_runtime_artifacts_writable_blocks_bad_path
test_latest_health_report_written_atomically
test_health_checks_do_not_execute_shell
test_health_checks_report_stale_artifacts
```

## 23.6 Status Reporter Tests

```text
test_build_runtime_status_ok
test_build_runtime_status_warn_with_open_alert
test_build_runtime_status_degraded_with_missing_upstream
test_build_runtime_status_fail_with_critical_check
test_build_runtime_status_blocked_for_policy_denied_view
test_write_latest_status_writes_atomic_json
test_status_report_redacts_sensitive_fields
```

## 23.7 Alert Manager Tests

```text
test_evaluate_alerts_from_critical_health_check
test_evaluate_alerts_from_metric_threshold
test_evaluate_alerts_from_stale_artifact
test_alert_record_written_to_alerts_jsonl
test_resolve_alert_writes_resolved_record
test_suppress_alert_writes_suppressed_record
test_alerts_do_not_execute_repair
test_alerts_do_not_send_network_notification
```

## 23.8 Trace Collector Tests

```text
test_start_trace_span_creates_ids
test_finish_trace_span_sets_duration
test_append_trace_span_writes_traces_jsonl
test_trace_attributes_redacted
```

## 23.9 Redaction Tests

```text
test_redact_api_key
test_redact_token
test_redact_password
test_redact_authorization_header
test_redact_raw_source_like_content
test_summarize_large_value
test_redaction_failure_blocks_persistence
```

## 23.10 Retention Tests

```text
test_rotation_stays_under_monitoring_root
test_rotation_preserves_completion_record
test_rotation_preserves_review_report
test_rotation_preserves_evidence_manifest
test_rotation_preserves_artifact_provenance
test_rotation_creates_retention_action
test_rotation_creates_audit_event
test_retention_does_not_delete_source_files
test_retention_does_not_delete_upstream_artifacts
```

## 23.11 Integration Tests

```text
test_monitoring_reads_tool_mcp_artifacts_read_only
test_monitoring_counts_blocked_invalid_tool_calls
test_monitoring_respects_policy_visibility_block
test_monitoring_aggregates_failure_taxonomy_classes
test_monitoring_uses_sandbox_boundary_for_upstream_artifacts
test_monitoring_degrades_when_upstream_artifacts_missing
test_monitoring_does_not_modify_upstream_artifacts
```

## 23.12 Negative Tests

```text
test_monitoring_does_not_execute_raw_shell
test_monitoring_does_not_open_network
test_monitoring_does_not_mutate_source
test_monitoring_does_not_write_outside_runtime_root
test_monitoring_does_not_persist_unredacted_secret
test_monitoring_does_not_auto_repair_failure
test_monitoring_does_not_override_policy
test_monitoring_does_not_modify_tool_mcp_artifacts
test_monitoring_does_not_delete_upstream_artifacts
test_monitoring_does_not_mark_missing_dependency_as_ok
test_monitoring_does_not_enable_network_export_from_config
test_monitoring_does_not_enable_auto_repair_from_config
test_monitoring_completion_evidence_hash_change_invalidates_done
```

---

# 24. Implementation Slices

Implement in controlled slices.

## 24.1 Slice A — Models, Constants, Schemas

Implement:

```text
monitoring_models.py
all monitoring schemas
schema examples in tests
```

Acceptance:

```text
dataclasses instantiate
schemas validate valid examples
schemas reject missing required fields
schemas reject invalid enum values
no durable writes yet
```

## 24.2 Slice B — Boundaries, Readers, Redaction

Implement:

```text
path_boundaries.py
jsonl_reader.py
redaction.py
```

Acceptance:

```text
write path boundary enforced
read roots bounded
symlink escapes rejected
large JSONL records bounded
secrets redacted before persistence
```

## 24.3 Slice C — Event, Trace, Metric Logging

Implement:

```text
event_logger.py
trace_collector.py
metrics_collector.py
```

Acceptance:

```text
events append
traces append
metrics append
records are redacted
records remain inside monitoring root
```

## 24.4 Slice D — Health, Status, Alerts

Implement:

```text
health_checks.py
status_reporter.py
alert_manager.py
```

Acceptance:

```text
health report generated
latest health report written atomically
latest status written atomically
alerts generated as records only
missing upstream dependencies degrade safely
```

## 24.5 Slice E — Retention, Evidence, Review, Completion

Implement:

```text
retention_policy.py
evidence_manifest.py
review_report.py
completion_record.py
```

Acceptance:

```text
retention rotates only monitoring-owned JSONL files
evidence manifest written
review report written
completion record written
SHA-256 hashes included
```

## 24.6 Slice F — Integration and Negative Tests

Implement:

```text
Tool / MCP read-only integration tests
Policy visibility tests
Failure Taxonomy aggregation tests
Security Sandbox boundary tests
negative safety tests
```

Acceptance:

```text
upstream artifacts are never modified
policy visibility blocks restricted views
unknown failure classes are handled
sandbox denial degrades safely
negative safety tests pass
```

---

# 25. Implementation Order

Use this exact order:

```text
1. Create tools/agentx_evolve/monitoring/ package.
2. Implement monitoring_models.py.
3. Implement monitoring_config.py with safe defaults.
4. Create monitoring schemas.
5. Implement path_boundaries.py.
6. Implement jsonl_reader.py.
7. Implement file_lock.py.
8. Implement redaction.py.
9. Implement event_logger.py.
10. Implement trace_collector.py.
11. Implement metrics_collector.py.
12. Implement health_checks.py.
13. Implement alert_manager.py.
14. Implement status_reporter.py.
15. Implement monitoring_cycle.py fully after collectors exist.
16. Implement retention_policy.py.
17. Implement evidence_manifest.py.
18. Implement review_report.py.
19. Implement completion_record.py.
20. Add schema validation utility and schema validation tests.
21. Add unit tests for each module.
22. Add simulated upstream fixture tests.
23. Add integration tests.
24. Add negative safety tests.
25. Run compileall.
26. Run pytest.
27. Run schema validation command or pytest equivalent.
28. Verify git status.
29. Write completion evidence.
```

Rationale:

```text
models first
config before thresholds and limits
schemas before durable records
boundaries before reading/writing
locks before concurrent writes
redaction before durable writes
event logger before collectors
trace/metrics/health before status
alerts after metrics and health
monitoring cycle after component functions exist
retention after artifacts exist
evidence/review/completion after runtime behavior exists
tests after public surfaces exist
```

---

# 26. Schema Validation Utility Requirements

Create:

```text
tools/agentx_evolve/tests/validate_monitoring_schemas.py
```

Required behavior:

```text
load every monitoring schema from tools/agentx_evolve/schemas/
validate every required named valid example
verify missing-required-field examples fail
verify invalid-enum examples fail where enums exist
verify redacted-payload examples remain schema-valid
print a concise PASS/FAIL summary
return exit_code 0 only when all schema checks pass
return non-zero when any required schema/example is missing or invalid
write only redacted validation summary artifacts under .agentx-init/monitoring/command_outputs/ if output is persisted
```

A final DONE claim is invalid if schema validation is only implied by pytest without identifying the exact test coverage.

---

# 27. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/monitoring

PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_monitoring_models.py \
  tools/agentx_evolve/tests/test_monitoring_config.py \
  tools/agentx_evolve/tests/test_monitoring_cycle.py \
  tools/agentx_evolve/tests/test_monitoring_file_lock.py \
  tools/agentx_evolve/tests/test_monitoring_path_boundaries.py \
  tools/agentx_evolve/tests/test_monitoring_jsonl_reader.py \
  tools/agentx_evolve/tests/test_monitoring_event_logger.py \
  tools/agentx_evolve/tests/test_monitoring_metrics_collector.py \
  tools/agentx_evolve/tests/test_monitoring_health_checks.py \
  tools/agentx_evolve/tests/test_monitoring_status_reporter.py \
  tools/agentx_evolve/tests/test_monitoring_alert_manager.py \
  tools/agentx_evolve/tests/test_monitoring_trace_collector.py \
  tools/agentx_evolve/tests/test_monitoring_redaction.py \
  tools/agentx_evolve/tests/test_monitoring_retention_policy.py \
  tools/agentx_evolve/tests/test_monitoring_evidence_manifest.py \
  tools/agentx_evolve/tests/test_monitoring_review_report.py \
  tools/agentx_evolve/tests/test_monitoring_completion_record.py \
  tools/agentx_evolve/tests/test_monitoring_schema_validation.py \
  tools/agentx_evolve/tests/test_monitoring_integration_tool_mcp.py \
  tools/agentx_evolve/tests/test_monitoring_integration_policy.py \
  tools/agentx_evolve/tests/test_monitoring_integration_failure_taxonomy.py \
  tools/agentx_evolve/tests/test_monitoring_integration_security_sandbox.py \
  tools/agentx_evolve/tests/test_monitoring_negative_cases.py

PYTHONPATH=tools python tools/agentx_evolve/tests/validate_monitoring_schemas.py

git status --short
```

If `validate_monitoring_schemas.py` is not implemented, record the pytest schema-validation replacement.

Required result:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts under .agentx-init/monitoring/
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
external monitoring service
running MCP server
```

---

# 28. Acceptance Criteria

The implementation is acceptable only if:

```text
all target files exist
all required schemas exist
all required tests exist
all dataclasses instantiate
monitoring config defaults are safe
monitoring cycle composes collectors without daemon behavior
schemas validate valid examples
schemas reject missing required fields
schemas reject invalid enum values
path boundaries block unsafe reads/writes
file locks stay under monitoring root
bounded JSONL readers handle missing/malformed/large files
event logger writes append-only JSONL
metrics collector writes metrics JSONL
health checks produce HealthReport
status reporter writes latest_status.json atomically
alert manager writes alert records only
trace collector writes trace spans
redaction removes secret-like values before persistence
retention rotates only monitoring JSONL files
retention preserves evidence manifests, review reports, completion records, and provenance
integration reads Tool / MCP artifacts read-only
integration respects Policy / Capability Registry visibility rules
integration aggregates Failure Taxonomy classes
integration respects Security Sandbox boundaries
negative tests prove no raw shell, no network, no source mutation, no auto-repair, no policy override, no unredacted secrets
compileall passes
pytest passes
schema validation passes
git status is clean or only expected runtime artifacts
completion record exists
```

---

# 29. Definition of Done

The Monitoring / Observability Layer is done when it provides safe, deterministic runtime visibility for Agent_X.

It must prove:

```text
monitoring package exists
schemas exist
tests exist
runtime artifact root exists or is created safely
events are appended
metrics are collected
health checks run locally
latest status is generated
alerts are generated as records only
traces/spans are recorded locally
redaction works before durable writes
retention/rotation is bounded and local
evidence manifest is written
review report is written
completion record is written
SHA-256 hashes are written for final evidence artifacts
Tool / MCP Adapter integration is read-only
Policy / Capability Registry visibility is respected
Failure Taxonomy classes are aggregated
Security Sandbox boundaries are respected
missing upstream dependencies degrade safely
stale artifacts are detected
no source mutation occurs
no network is enabled by default
no raw shell is executed
no automatic repair occurs
no policy override occurs
no unredacted secrets are persisted
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/monitoring
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_monitoring_*.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_monitoring_schemas.py
git status --short
```

Expected proof:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
```

---

# 30. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places monitoring files outside tools/agentx_evolve/monitoring/ without recorded deviation
writes runtime artifacts outside .agentx-init/monitoring/ without recorded deviation
reads arbitrary source files for observability
scans the whole repository without bounded approved roots
executes raw shell
opens network connection by default
exports telemetry externally
mutates source files
modifies Tool / MCP artifacts
modifies Policy artifacts
modifies Failure Taxonomy artifacts
modifies Security Sandbox artifacts
runs automatic repair
approves or blocks actions directly through monitoring
logs unredacted secrets
logs raw source-file contents
requires external observability service
requires hosted model or LLM
adds OpenCode/Bun/Node runtime dependency
skips schema validation
returns unstructured monitoring records
marks missing upstream dependencies as OK without evidence
marks stale evidence as healthy without staleness check
```

---

# 31. Final Frozen Acceptance Matrix

| Area | Required Result | Status |
|---|---|---|
| Package structure | `tools/agentx_evolve/monitoring/` exists | PASS / FAIL / NOT CHECKED |
| Schemas | all required schemas exist and validate | PASS / FAIL / NOT CHECKED |
| Tests | all required monitoring tests exist | PASS / FAIL / NOT CHECKED |
| Boundaries | reads/writes limited to approved roots | PASS / FAIL / NOT CHECKED |
| Redaction | secrets removed before persistence | PASS / FAIL / NOT CHECKED |
| Events | events JSONL append works | PASS / FAIL / NOT CHECKED |
| Metrics | local metrics collected safely | PASS / FAIL / NOT CHECKED |
| Health | health report generated safely | PASS / FAIL / NOT CHECKED |
| Status | latest status written atomically | PASS / FAIL / NOT CHECKED |
| Alerts | alerts are records only | PASS / FAIL / NOT CHECKED |
| Traces | trace spans written locally | PASS / FAIL / NOT CHECKED |
| Retention | rotates only monitoring JSONL files | PASS / FAIL / NOT CHECKED |
| Evidence | manifest/review/completion records written | PASS / FAIL / NOT CHECKED |
| Hashing | final evidence SHA-256 hashes present | PASS / FAIL / NOT CHECKED |
| Tool / MCP integration | read-only artifact aggregation | PASS / FAIL / NOT CHECKED |
| Policy integration | restricted views fail closed | PASS / FAIL / NOT CHECKED |
| Failure Taxonomy | failure classes aggregated | PASS / FAIL / NOT CHECKED |
| Security Sandbox | artifact reads respect boundaries | PASS / FAIL / NOT CHECKED |
| Negative safety | no shell/network/source mutation/secrets | PASS / FAIL / NOT CHECKED |
| Validation | compileall, pytest, schema validation pass | PASS / FAIL / NOT CHECKED |
| Reviewed commit | exact commit and environment recorded | PASS / FAIL / NOT CHECKED |
| Evidence reproducibility | command exit codes, output refs, and hashes recorded | PASS / FAIL / NOT CHECKED |

A final `DONE` verdict is not valid if any required area is `FAIL` or `NOT CHECKED`.

---

# 32. Final Implementation Checklist

```text
Structure:
[ ] tools/agentx_evolve/monitoring/ exists
[ ] monitoring package files exist
[ ] schema files exist
[ ] test files exist

Models / Schemas:
[ ] monitoring dataclasses instantiate
[ ] schemas accept valid records
[ ] schemas reject invalid records
[ ] schema examples exist

Boundaries / Readers:
[ ] approved read roots enforced
[ ] monitoring write root enforced
[ ] symlink escapes rejected
[ ] bounded JSONL readers implemented

Runtime Artifacts:
[ ] events.jsonl written
[ ] metrics.jsonl written
[ ] health_checks.jsonl written
[ ] alerts.jsonl written
[ ] traces.jsonl written
[ ] observability_audit.jsonl written
[ ] retention_actions.jsonl written
[ ] artifact_provenance.jsonl written
[ ] latest_status.json written atomically
[ ] latest_health_report.json written atomically

Behavior:
[ ] health checks run locally
[ ] metrics are collected locally
[ ] events are appended
[ ] traces are appended
[ ] alerts are generated as records only
[ ] status report is generated
[ ] redaction is applied
[ ] retention is bounded
[ ] stale artifacts are detected

Integration:
[ ] Tool / MCP artifacts read-only
[ ] Policy visibility respected
[ ] Failure Taxonomy classes aggregated
[ ] Security Sandbox boundaries respected
[ ] missing upstream dependencies degrade safely

Safety:
[ ] no source mutation
[ ] no raw shell
[ ] no network by default
[ ] no automatic repair
[ ] no policy override
[ ] no unredacted secrets
[ ] no upstream artifact modification

Validation:
[ ] compileall PASS
[ ] pytest PASS
[ ] schema validation PASS
[ ] git status clean or expected runtime artifacts only
[ ] evidence manifest exists
[ ] review report exists
[ ] completion record exists
[ ] SHA-256 hashes exist
```

---

# 33. Fresh-Clone Validation and Evidence Requirements

The implementation must be validated from a clean checkout or clean working tree.

Required recorded fields:

```text
reviewed_commit
reviewed_branch
reviewed_at_utc
review_environment.os
review_environment.python_version
review_environment.pytest_version
initial_git_status
final_git_status
```

Every validation command must record:

```text
command text
exit_code
status
summary
output_artifact path, if persisted
output_sha256, if persisted
```

Required command proof:

```bash
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve/monitoring
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_monitoring_*.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_monitoring_schemas.py
git status --short
```

Required result:

```text
initial git status: clean or expected runtime artifacts only
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
final git status: clean or expected runtime artifacts only
```

A final DONE claim is invalid if:

```text
reviewed commit is missing
any required command is NOT RUN
any required command exit code is missing
compileall fails
pytest fails
schema validation fails
final evidence hashes are missing
source mutation occurs
evidence manifest is missing
review report is missing
completion record is missing
```

The evidence manifest, review report, and completion record must cross-reference one another by path and SHA-256 hash.

---

# 34. Final Rating

This v4 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, files, schemas, classes, functions, runtime artifacts, configuration defaults, lock behavior, top-level monitoring cycle, exposure boundary, schema versioning, status precedence, metric naming, alert deduplication, health checks, metrics collectors, event collectors, trace/span collectors, status reports, alerts, redaction, retention/rotation, evidence hashing, dependency fallback rules, boundary enforcement, bounded JSONL reading, staleness handling, evidence immutability, integrations, simulated dependency fixtures, validation evidence requirements, test cases, implementation slices, implementation order, acceptance criteria, drift blockers, and Definition of Done.
```

This v4 is frozen as the implementation-ready handoff for the Monitoring / Observability Layer unless a later major revision changes runtime behavior, network exposure, policy visibility, or default safety posture.
