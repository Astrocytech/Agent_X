from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentx_evolve.monitoring.monitoring_events import (
    MN_EVENT_INFO,
    MN_EVENT_HEALTH,
    MN_EVENT_METRIC,
    make_event,
)
from agentx_evolve.monitoring.monitoring_health import run_all_health_checks
from agentx_evolve.monitoring.monitoring_metrics import collect_monitoring_metrics
from agentx_evolve.monitoring.monitoring_utils import (
    write_json_atomic,
    append_jsonl,
    ensure_dir,
)
from agentx_evolve.monitoring.monitoring_status import build_runtime_status
from agentx_evolve.models.model_models import new_id, utc_now_iso

logger = logging.getLogger(__name__)

MC_SCHEMA_VERSION = "1.0"
CYCLE_DIR = ".agentx-init/monitoring"


@dataclass
class MonitoringCycleResult:
    schema_version: str = MC_SCHEMA_VERSION
    cycle_id: str = ""
    started_at: str = ""
    ended_at: str = ""
    duration_ms: float = 0.0
    events_written: int = 0
    checks_run: int = 0
    metrics_collected: int = 0
    status_updated: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = {}
        for f in self.__dataclass_fields__:
            val = getattr(self, f)
            result[f] = val
        return result


def run_monitoring_cycle(repo_root: Path, session_id: str = "") -> MonitoringCycleResult:
    start = time.monotonic()
    cycle_id = new_id("cycle")
    result = MonitoringCycleResult(
        cycle_id=cycle_id,
        started_at=utc_now_iso(),
    )

    ensure_dir(repo_root / CYCLE_DIR)

    event = make_event(
        event_type=MN_EVENT_INFO,
        session_id=session_id,
        component="MonitoringCycle",
        message=f"Monitoring cycle {cycle_id} started",
    )
    history = repo_root / CYCLE_DIR / "event_history.jsonl"
    append_jsonl(history, event.to_dict() if hasattr(event, "to_dict") else event.__dict__)
    result.events_written += 1

    try:
        checks = run_all_health_checks(repo_root)
        result.checks_run = len(checks.checks) if hasattr(checks, "checks") else 0
        result.status_updated = True
    except Exception as e:
        result.errors.append(f"Health checks failed: {e}")

    try:
        metrics = collect_monitoring_metrics(repo_root)
        result.metrics_collected = len(metrics)
    except Exception as e:
        result.errors.append(f"Metrics collection failed: {e}")

    try:
        status = build_runtime_status(repo_root)
        latest_status = repo_root / CYCLE_DIR / "latest_status.json"
        write_json_atomic(
            latest_status,
            status.to_dict() if hasattr(status, "to_dict") else status.__dict__,
        )
    except Exception as e:
        result.errors.append(f"Status update failed: {e}")

    result.ended_at = utc_now_iso()
    result.duration_ms = (time.monotonic() - start) * 1000

    latest = repo_root / CYCLE_DIR / "latest_result.json"
    write_json_atomic(latest, result.to_dict())
    return result
