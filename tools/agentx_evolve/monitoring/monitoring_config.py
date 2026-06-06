from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MonitoringConfig:
    enabled: bool = True
    monitoring_root: str = ".agentx-init/monitoring"
    retention_days: int = 30
    max_events: int = 10000
    max_metrics: int = 100000
    health_check_interval_seconds: int = 300
    alert_evaluation_interval_seconds: int = 60
    trace_enabled: bool = True
    metric_collection_enabled: bool = True
    redact_secrets: bool = True
    redacted_keys: tuple[str, ...] = (
        "secret", "password", "token", "api_key", "private_key",
    )
    component: str = "monitoring"


DEFAULT_CONFIG = MonitoringConfig()


def redact_sensitive_keys(data: dict, keys: set[str] | None = None) -> dict:
    if keys is None:
        keys = {"secret", "password", "token", "api_key", "private_key"}
    result: dict = {}
    for k, v in data.items():
        if k.lower() in keys:
            result[k] = "***REDACTED***"
        elif isinstance(v, dict):
            result[k] = redact_sensitive_keys(v, keys)
        elif isinstance(v, list):
            result[k] = [
                redact_sensitive_keys(item, keys) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            result[k] = v
    return result


def load_monitoring_config(config_path: Path | None = None) -> MonitoringConfig:
    if config_path is None:
        return DEFAULT_CONFIG
    if not config_path.exists():
        return DEFAULT_CONFIG
    import json
    data = json.loads(config_path.read_text())
    return MonitoringConfig(**{k: v for k, v in data.items() if k in MonitoringConfig.__dataclass_fields__})
