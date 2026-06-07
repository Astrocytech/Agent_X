from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentx_evolve.monitoring.monitoring_events import (
    MonitoringEvent,
    MN_EVENT_AUDIT,
    MN_EVENT_ERROR,
    MN_EVENT_WARN,
    MN_EVENT_INFO,
)
from agentx_evolve.monitoring.monitoring_utils import append_jsonl
from agentx_evolve.models.model_models import new_id, utc_now_iso

logger = logging.getLogger(__name__)

EVENT_LOG_DIR = ".agentx-init/monitoring"


def _event_path(repo_root: Path) -> Path:
    return repo_root / EVENT_LOG_DIR / "event_history.jsonl"


def log_event(
    event_type: str,
    component: str,
    message: str,
    repo_root: Path,
    session_id: str = "",
    metadata: dict | None = None,
) -> MonitoringEvent:
    event = MonitoringEvent(
        event_id=new_id("evt"),
        event_type=event_type,
        session_id=session_id,
        component=component,
        message=message,
        timestamp=utc_now_iso(),
        metadata=metadata or {},
    )
    path = _event_path(repo_root)
    append_jsonl(path, event.to_dict() if hasattr(event, "to_dict") else event.__dict__)
    return event


def log_info(component: str, message: str, repo_root: Path, **kwargs) -> MonitoringEvent:
    return log_event(MN_EVENT_INFO, component, message, repo_root, **kwargs)


def log_warn(component: str, message: str, repo_root: Path, **kwargs) -> MonitoringEvent:
    return log_event(MN_EVENT_WARN, component, message, repo_root, **kwargs)


def log_error(component: str, message: str, repo_root: Path, **kwargs) -> MonitoringEvent:
    return log_event(MN_EVENT_ERROR, component, message, repo_root, **kwargs)


def log_audit(component: str, message: str, repo_root: Path, **kwargs) -> MonitoringEvent:
    return log_event(MN_EVENT_AUDIT, component, message, repo_root, **kwargs)
