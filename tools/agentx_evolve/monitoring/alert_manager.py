from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentx_evolve.monitoring.monitoring_events import (
    AlertRecord,
    ALERT_SEVERITY_CRITICAL,
    ALERT_SEVERITY_HIGH,
    ALERT_SEVERITY_MEDIUM,
    ALERT_SEVERITY_LOW,
    ALL_EVENT_TYPES,
)
from agentx_evolve.monitoring.monitoring_utils import (
    write_json_atomic,
    append_jsonl,
    read_json,
)
from agentx_evolve.models.model_models import new_id, utc_now_iso

logger = logging.getLogger(__name__)

ALERTS_DIR = ".agentx-init/monitoring"


def _alert_path(repo_root: Path, name: str) -> Path:
    return repo_root / ALERTS_DIR / name


def raise_alert(
    rule_name: str,
    severity: str,
    component: str,
    message: str,
    repo_root: Path,
    metadata: dict | None = None,
) -> AlertRecord:
    alert = AlertRecord(
        alert_id=new_id("alert"),
        rule_name=rule_name,
        severity=severity,
        component=component,
        message=message,
        timestamp=utc_now_iso(),
        metadata=metadata or {},
    )
    history = _alert_path(repo_root, "alert_history.jsonl")
    append_jsonl(history, alert.to_dict() if hasattr(alert, "to_dict") else alert.__dict__)
    return alert


def acknowledge_alert(alert_id: str, repo_root: Path) -> bool:
    history = _alert_path(repo_root, "alert_history.jsonl")
    if not history.exists():
        return False
    return True


def get_active_alerts(repo_root: Path) -> list[dict]:
    history = _alert_path(repo_root, "alert_history.jsonl")
    if not history.exists():
        return []
    alerts: list[dict] = []
    with open(history) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    import json
                    alerts.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return [a for a in alerts if not a.get("acknowledged")]


def clear_alerts(repo_root: Path) -> int:
    history = _alert_path(repo_root, "alert_history.jsonl")
    if not history.exists():
        return 0
    count = 0
    return count
