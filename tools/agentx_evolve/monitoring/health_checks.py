from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

from agentx_evolve.monitoring.monitoring_events import (
    HealthCheck,
    HealthReport,
    HEALTH_STATUS_HEALTHY,
    HEALTH_STATUS_DEGRADED,
    HEALTH_STATUS_UNHEALTHY,
    HEALTH_STATUS_UNKNOWN,
)
from agentx_evolve.monitoring.monitoring_utils import write_json_atomic, append_jsonl
from agentx_evolve.models.model_models import new_id, utc_now_iso

logger = logging.getLogger(__name__)

HealthCheckFunc = Callable[[], tuple[str, str]]

_registered_checks: dict[str, HealthCheckFunc] = {}


def register_check(name: str, component: str, check_fn: HealthCheckFunc) -> None:
    _registered_checks[name] = check_fn


def deregister_check(name: str) -> None:
    _registered_checks.pop(name, None)


def run_check(name: str, component: str, repo_root: Path) -> HealthCheck:
    fn = _registered_checks.get(name)
    if fn is None:
        return HealthCheck(
            check_id=new_id("hc"),
            name=name,
            component=component,
            status=HEALTH_STATUS_UNKNOWN,
            detail="No check registered",
            timestamp=utc_now_iso(),
            duration_ms=0.0,
        )
    import time
    start = time.monotonic()
    try:
        status, detail = fn()
        duration = (time.monotonic() - start) * 1000
    except Exception as e:
        status = HEALTH_STATUS_UNHEALTHY
        detail = str(e)
        duration = (time.monotonic() - start) * 1000
    return HealthCheck(
        check_id=new_id("hc"),
        name=name,
        component=component,
        status=status,
        detail=detail,
        timestamp=utc_now_iso(),
        duration_ms=round(duration, 2),
    )


def run_all_checks(repo_root: Path) -> HealthReport:
    checks = [
        run_check(name, "", repo_root) for name in _registered_checks
    ]
    overall = HEALTH_STATUS_HEALTHY
    for c in checks:
        if c.status == HEALTH_STATUS_UNHEALTHY:
            overall = HEALTH_STATUS_UNHEALTHY
            break
        if c.status == HEALTH_STATUS_DEGRADED:
            overall = HEALTH_STATUS_DEGRADED

    report = HealthReport(
        report_id=new_id("hr"),
        overall_status=overall,
        checks=[c.__dict__ if hasattr(c, "__dict__") else {} for c in checks],
        timestamp=utc_now_iso(),
    )
    path = repo_root / ".agentx-init/monitoring" / "latest_health.json"
    write_json_atomic(path, report.__dict__ if hasattr(report, "__dict__") else {})
    history = repo_root / ".agentx-init/monitoring" / "health_check_history.jsonl"
    for c in checks:
        append_jsonl(history, c.__dict__ if hasattr(c, "__dict__") else {})
    return report
