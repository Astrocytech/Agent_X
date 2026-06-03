from __future__ import annotations

from agentx_evolve.monitoring.monitoring_events import MonitoringEvent


_SCHEMA_CHECKS = {
    "event_id": (str,),
    "event_type": (str,),
    "session_id": (str,),
    "component": (str,),
    "message": (str,),
    "timestamp": (str,),
}


def validate_monitoring_schema(event: MonitoringEvent) -> list[str]:
    errors: list[str] = []
    for field_name, expected_types in _SCHEMA_CHECKS.items():
        val = getattr(event, field_name, None)
        if not isinstance(val, expected_types):
            errors.append(
                f"{field_name}: expected {expected_types}, got {type(val).__name__}"
            )
    return errors
