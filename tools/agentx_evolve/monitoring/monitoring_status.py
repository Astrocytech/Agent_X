from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentx_evolve.models.model_models import new_id
from agentx_evolve.monitoring.monitoring_utils import write_json_atomic, ensure_dir
from agentx_evolve.monitoring.monitoring_events import (
    RuntimeStatus,
    STATUS_RUNNING, STATUS_DEGRADED, STATUS_STOPPED, STATUS_STARTING,
)

STATUS_DIR = Path(__file__).resolve().parent.parent / ".agentx-init" / "monitoring" / "status"


_component_statuses: dict[str, RuntimeStatus] = {}


def register_component(component: str, version: str = "") -> RuntimeStatus:
    if component not in _component_statuses:
        _component_statuses[component] = RuntimeStatus(
            component=component,
            status=STATUS_STARTING,
            version=version,
        )
    return _component_statuses[component]


def set_component_status(component: str, status: str) -> RuntimeStatus | None:
    rs = _component_statuses.get(component)
    if rs is None:
        return None
    rs.status = status
    rs.last_event_timestamp = (
        __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat()
    )
    return rs


def update_session_count(component: str, delta: int = 1) -> RuntimeStatus | None:
    rs = _component_statuses.get(component)
    if rs is None:
        return None
    rs.active_sessions = max(0, rs.active_sessions + delta)
    return rs


def build_runtime_status(base_dir: Path | None = None) -> dict[str, Any]:
    statuses = {k: v.to_dict() for k, v in _component_statuses.items()}
    overall = STATUS_RUNNING
    for rs in _component_statuses.values():
        if rs.status == STATUS_STOPPED:
            overall = STATUS_STOPPED
            break
        if rs.status == STATUS_DEGRADED:
            overall = STATUS_DEGRADED
    result = {
        "overall_status": overall,
        "components": statuses,
    }
    if base_dir:
        dir_path = ensure_dir(base_dir)
        write_json_atomic(dir_path / "runtime_status.json", result)
    return result


def get_component_status(component: str) -> RuntimeStatus | None:
    return _component_statuses.get(component)
