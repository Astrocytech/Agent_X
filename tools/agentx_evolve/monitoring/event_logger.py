import warnings
from agentx_evolve.monitoring.monitoring_events import (
    MonitoringEvent, EventHash,
    MN_SCHEMA_VERSION, MN_SCHEMA_ID,
    MN_EVENT_AUDIT, MN_EVENT_ERROR, MN_EVENT_WARN, MN_EVENT_INFO,
    ALL_EVENT_TYPES,
    canonical_json, sha256_dict, utc_now_iso, make_event,
)
warnings.warn(
    "agentx_evolve.monitoring.event_logger is deprecated; "
    "use agentx_evolve.monitoring.monitoring_events instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "MonitoringEvent", "EventHash",
    "MN_SCHEMA_VERSION", "MN_SCHEMA_ID",
    "MN_EVENT_AUDIT", "MN_EVENT_ERROR", "MN_EVENT_WARN", "MN_EVENT_INFO",
    "ALL_EVENT_TYPES",
    "canonical_json", "sha256_dict", "utc_now_iso", "make_event",
]
