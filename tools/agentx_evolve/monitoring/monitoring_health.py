from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from agentx_evolve.models.model_models import new_id
from agentx_evolve.monitoring.monitoring_utils import write_json_atomic, ensure_dir
from agentx_evolve.monitoring.monitoring_events import (
    HealthCheck, HealthReport,
    HEALTH_STATUS_HEALTHY, HEALTH_STATUS_DEGRADED,
    HEALTH_STATUS_UNHEALTHY, HEALTH_STATUS_UNKNOWN,
)

HealthCheckFunc = Callable[[], tuple[str, str]]

_checks: dict[str, HealthCheckFunc] = {}


def register_health_check(name: str, component: str, fn: HealthCheckFunc) -> None:
    _checks[f"{component}:{name}"] = fn


def deregister_health_check(name: str, component: str) -> None:
    _checks.pop(f"{component}:{name}", None)


def run_health_check(name: str, component: str, fn: HealthCheckFunc) -> HealthCheck:
    start = time.time()
    try:
        status, detail = fn()
        duration = (time.time() - start) * 1000
    except Exception as e:
        status = HEALTH_STATUS_UNHEALTHY
        detail = str(e)
        duration = (time.time() - start) * 1000
    return HealthCheck(
        check_id=new_id("hlth"),
        name=name,
        component=component,
        status=status,
        detail=detail,
        duration_ms=round(duration, 2),
    )


def run_all_health_checks() -> HealthReport:
    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
    results: list[HealthCheck] = []
    for key, fn in _checks.items():
        component, name = key.split(":", 1)
        results.append(run_health_check(name, component, fn))
    overall = HEALTH_STATUS_HEALTHY
    for c in results:
        if c.status == HEALTH_STATUS_UNHEALTHY:
            overall = HEALTH_STATUS_UNHEALTHY
            break
        if c.status == HEALTH_STATUS_DEGRADED:
            overall = HEALTH_STATUS_DEGRADED
    return HealthReport(
        report_id=new_id("rprt"),
        overall_status=overall,
        checks=results,
        timestamp=now,
    )


def run_monitoring_health_checks(base_dir: Path | None = None) -> HealthReport:
    report = run_all_health_checks()
    if base_dir:
        dir_path = ensure_dir(base_dir)
        write_json_atomic(dir_path / "latest_health_report.json", report.to_dict())
    return report


def is_healthy() -> bool:
    for c in _checks.values():
        try:
            status, _ = c()
            if status != HEALTH_STATUS_HEALTHY:
                return False
        except Exception:
            return False
    return True
