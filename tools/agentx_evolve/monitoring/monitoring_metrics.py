from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentx_evolve.models.model_models import new_id
from agentx_evolve.monitoring.monitoring_utils import append_jsonl, ensure_dir
from agentx_evolve.monitoring.monitoring_events import MetricRecord


METRICS_DIR = Path(__file__).resolve().parent.parent / ".agentx-init" / "monitoring" / "metrics"


@dataclass
class Counter:
    name: str = ""
    value: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)

    def inc(self, delta: float = 1.0) -> None:
        self.value += delta


@dataclass
class Gauge:
    name: str = ""
    value: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)

    def set(self, val: float) -> None:
        self.value = val


_counters: dict[str, Counter] = {}
_gauges: dict[str, Gauge] = {}


def register_counter(name: str, labels: dict[str, str] | None = None) -> Counter:
    key = f"counter:{name}"
    if key not in _counters:
        _counters[key] = Counter(name=name, labels=labels or {})
    return _counters[key]


def register_gauge(name: str, labels: dict[str, str] | None = None) -> Gauge:
    key = f"gauge:{name}"
    if key not in _gauges:
        _gauges[key] = Gauge(name=name, labels=labels or {})
    return _gauges[key]


def collect_metrics(component: str = "") -> list[MetricRecord]:
    records: list[MetricRecord] = []
    now = datetime.now(timezone.utc).isoformat()
    for key, c in _counters.items():
        records.append(MetricRecord(
            metric_id=new_id("mtr"),
            name=c.name,
            value=c.value,
            unit="count",
            labels=c.labels,
            timestamp=now,
            component=component,
        ))
    for key, g in _gauges.items():
        records.append(MetricRecord(
            metric_id=new_id("mtr"),
            name=g.name,
            value=g.value,
            unit="gauge",
            labels=g.labels,
            timestamp=now,
            component=component,
        ))
    return records


def write_metrics(metrics: list[MetricRecord], base_dir: Path | None = None) -> Path:
    dir_path = ensure_dir(base_dir or METRICS_DIR)
    metrics_path = dir_path / "metrics.jsonl"
    for m in metrics:
        append_jsonl(metrics_path, m.to_dict())
    return metrics_path


def collect_monitoring_metrics(component: str = "") -> list[MetricRecord]:
    return collect_metrics(component)


def reset_metrics() -> None:
    _counters.clear()
    _gauges.clear()
