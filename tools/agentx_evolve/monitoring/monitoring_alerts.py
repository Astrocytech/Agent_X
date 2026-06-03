from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from agentx_evolve.models.model_models import new_id
from agentx_evolve.monitoring.monitoring_utils import append_jsonl, ensure_dir
from agentx_evolve.monitoring.monitoring_events import (
    AlertRecord,
    ALERT_SEVERITY_CRITICAL, ALERT_SEVERITY_HIGH,
    ALERT_SEVERITY_MEDIUM, ALERT_SEVERITY_LOW,
)

AlertCondition = Callable[[], tuple[bool, str, str]]

ALERTS_DIR = Path(__file__).resolve().parent.parent / ".agentx-init" / "monitoring" / "alerts"


@dataclass
class AlertRule:
    name: str = ""
    condition: AlertCondition | None = None
    severity: str = ALERT_SEVERITY_MEDIUM
    component: str = ""
    enabled: bool = True


_rules: list[AlertRule] = []
_alerts: list[AlertRecord] = []


def register_alert_rule(name: str, condition: AlertCondition,
                        severity: str = ALERT_SEVERITY_MEDIUM,
                        component: str = "") -> AlertRule:
    rule = AlertRule(name=name, condition=condition, severity=severity,
                     component=component, enabled=True)
    _rules.append(rule)
    return rule


def evaluate_alerts(base_dir: Path | None = None) -> list[AlertRecord]:
    now = datetime.now(timezone.utc).isoformat()
    new_alerts: list[AlertRecord] = []
    for rule in _rules:
        if not rule.enabled or rule.condition is None:
            continue
        try:
            fired, message, severity = rule.condition()
            if not fired:
                continue
        except Exception as e:
            fired = True
            message = str(e)
            severity = ALERT_SEVERITY_HIGH

        alert = AlertRecord(
            alert_id=new_id("alrt"),
            rule_name=rule.name,
            severity=severity,
            message=message,
            component=rule.component,
            timestamp=now,
        )
        new_alerts.append(alert)
        _alerts.append(alert)

    if base_dir and new_alerts:
        dir_path = ensure_dir(base_dir)
        for alert in new_alerts:
            append_jsonl(dir_path / "alerts.jsonl", alert.to_dict())

    return new_alerts


def get_active_alerts() -> list[AlertRecord]:
    return [a for a in _alerts if not a.acknowledged]


def acknowledge_alert(alert_id: str) -> bool:
    for a in _alerts:
        if a.alert_id == alert_id:
            a.acknowledged = True
            return True
    return False


def clear_alerts() -> None:
    _alerts.clear()
