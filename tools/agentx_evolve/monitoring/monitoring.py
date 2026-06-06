"""
[DEPRECATED] Legacy monitoring module.

All functionality has been moved to separate submodules:
  - monitoring_events.py   - Event models and constants
  - monitoring_audit.py    - Audit log and session inspection
  - monitoring_utils.py    - Shared utilities
  - monitoring_metrics.py  - Metrics collection
  - monitoring_health.py   - Health checks
  - monitoring_alerts.py   - Alert evaluation
  - monitoring_traces.py   - Trace spans
  - monitoring_status.py   - Runtime status
  - monitoring_retention.py - Data retention
  - monitoring_config.py   - Configuration

This module re-exports the original API for backward compatibility.
"""
import warnings
warnings.warn(
    "monitoring/monitoring.py is deprecated; import from monitoring.* submodules instead",
    DeprecationWarning, stacklevel=2,
)

from agentx_evolve.monitoring.monitoring_events import (
    MonitoringEvent as AuditEvent,
    EventHash as AuditEventHash,
    MN_SCHEMA_VERSION, MN_SCHEMA_ID,
    MN_EVENT_AUDIT, MN_EVENT_ERROR, MN_EVENT_WARN, MN_EVENT_INFO,
    ALL_EVENT_TYPES,
    canonical_json, sha256_dict,
)

from agentx_evolve.monitoring.monitoring_audit import AuditLog, SessionInspector

from agentx_evolve.monitoring.monitoring_utils import write_json_atomic, append_jsonl
