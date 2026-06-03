from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from agentx_evolve.monitoring.monitoring_models import MetricPoint
from agentx_evolve.monitoring.monitoring_utils import write_json_atomic, append_jsonl
from agentx_evolve.models.model_models import new_id, utc_now_iso

logger = logging.getLogger(__name__)

METRICS_DIR = ".agentx-init/monitoring"

_registered_counters: dict[str, dict] = {}
_registered_gauges: dict[str, dict] = {}
_collected_points: list[MetricPoint] = []


def register_counter(name: str, unit: str = "", labels: dict | None = None) -> None:
    _registered_counters[name] = {"unit": unit, "labels": labels or {}, "value": 0.0}


def register_gauge(name: str, unit: str = "", labels: dict | None = None) -> None:
    _registered_gauges[name] = {"unit": unit, "labels": labels or {}, "value": 0.0}


def increment_counter(name: str, value: float = 1.0) -> None:
    if name in _registered_counters:
        _registered_counters[name]["value"] += value


def set_gauge(name: str, value: float) -> None:
    if name in _registered_gauges:
        _registered_gauges[name]["value"] = value


def record_point(
    name: str,
    value: float,
    unit: str = "",
    component: str = "",
    labels: dict | None = None,
) -> MetricPoint:
    point = MetricPoint(
        point_id=new_id("mp"),
        name=name,
        value=value,
        unit=unit,
        component=component,
        labels=labels or {},
        timestamp=utc_now_iso(),
    )
    _collected_points.append(point)
    return point


def collect_points(repo_root: Path) -> list[dict]:
    points: list[dict] = []
    for name, data in _registered_counters.items():
        points.append({
            "name": name,
            "value": data["value"],
            "unit": data["unit"],
            "labels": data["labels"],
            "timestamp": utc_now_iso(),
        })
    for name, data in _registered_gauges.items():
        points.append({
            "name": name,
            "value": data["value"],
            "unit": data["unit"],
            "labels": data["labels"],
            "timestamp": utc_now_iso(),
        })
    for p in _collected_points:
        points.append(p.to_dict() if hasattr(p, "to_dict") else p.__dict__)

    history = repo_root / METRICS_DIR / "metrics_history.jsonl"
    for pt in points:
        append_jsonl(history, pt)
    _collected_points.clear()
    return points


def reset_collectors() -> None:
    _registered_counters.clear()
    _registered_gauges.clear()
    _collected_points.clear()
