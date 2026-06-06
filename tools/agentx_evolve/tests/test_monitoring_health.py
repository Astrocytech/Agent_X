from pathlib import Path

import pytest

from agentx_evolve.monitoring.monitoring_health import (
    register_health_check, deregister_health_check,
    run_health_check, run_all_health_checks,
    run_monitoring_health_checks, is_healthy,
)
from agentx_evolve.monitoring.monitoring_events import (
    HEALTH_STATUS_HEALTHY, HEALTH_STATUS_UNHEALTHY,
    HEALTH_STATUS_DEGRADED, HEALTH_STATUS_UNKNOWN,
)


def setup_function():
    deregister_health_check("test_check", "cmp")
    deregister_health_check("failing", "cmp")
    deregister_health_check("degraded", "cmp")


def teardown_function():
    deregister_health_check("test_check", "cmp")
    deregister_health_check("failing", "cmp")
    deregister_health_check("degraded", "cmp")


def test_register_and_run_health_check():
    def check():
        return HEALTH_STATUS_HEALTHY, "all good"
    register_health_check("test_check", "cmp", check)
    result = run_health_check("test_check", "cmp", check)
    assert result.name == "test_check"
    assert result.component == "cmp"
    assert result.status == HEALTH_STATUS_HEALTHY
    assert result.detail == "all good"
    assert result.duration_ms >= 0
    assert result.check_id.startswith("hlth")


def test_run_health_check_exception():
    def broken():
        raise RuntimeError("fail")
    result = run_health_check("broken", "cmp", broken)
    assert result.status == HEALTH_STATUS_UNHEALTHY
    assert "fail" in result.detail


def test_run_all_health_checks():
    def healthy():
        return HEALTH_STATUS_HEALTHY, "ok"
    register_health_check("test_check", "cmp", healthy)
    report = run_all_health_checks()
    assert report.overall_status == HEALTH_STATUS_HEALTHY
    assert len(report.checks) == 1
    assert report.report_id.startswith("rprt")


def test_run_all_health_checks_unhealthy():
    def healthy():
        return HEALTH_STATUS_HEALTHY, "ok"
    def failing():
        return HEALTH_STATUS_UNHEALTHY, "broken"
    register_health_check("test_check", "cmp", healthy)
    register_health_check("failing", "cmp", failing)
    report = run_all_health_checks()
    assert report.overall_status == HEALTH_STATUS_UNHEALTHY


def test_run_all_health_checks_degraded():
    def healthy():
        return HEALTH_STATUS_HEALTHY, "ok"
    def deg():
        return HEALTH_STATUS_DEGRADED, "slow"
    register_health_check("test_check", "cmp", healthy)
    register_health_check("degraded", "cmp", deg)
    report = run_all_health_checks()
    assert report.overall_status == HEALTH_STATUS_DEGRADED


def test_run_all_health_checks_empty():
    assert run_all_health_checks().overall_status == HEALTH_STATUS_HEALTHY


def test_run_monitoring_health_checks_with_dir(tmp_path):
    def healthy():
        return HEALTH_STATUS_HEALTHY, "ok"
    register_health_check("test_check", "cmp", healthy)
    report = run_monitoring_health_checks(base_dir=tmp_path)
    report_path = tmp_path / "latest_health_report.json"
    assert report_path.exists()
    import json
    data = json.loads(report_path.read_text())
    assert data["overall_status"] == HEALTH_STATUS_HEALTHY


def test_run_monitoring_health_checks_no_dir():
    def healthy():
        return HEALTH_STATUS_HEALTHY, "ok"
    register_health_check("test_check", "cmp", healthy)
    report = run_monitoring_health_checks()
    assert report.overall_status == HEALTH_STATUS_HEALTHY


def test_is_healthy_all_healthy():
    def healthy():
        return HEALTH_STATUS_HEALTHY, "ok"
    register_health_check("test_check", "cmp", healthy)
    assert is_healthy() is True


def test_is_healthy_one_unhealthy():
    def healthy():
        return HEALTH_STATUS_HEALTHY, "ok"
    def failing():
        return HEALTH_STATUS_UNHEALTHY, "broken"
    register_health_check("test_check", "cmp", healthy)
    register_health_check("failing", "cmp", failing)
    assert is_healthy() is False


def test_is_healthy_exception():
    def broken():
        raise RuntimeError("fail")
    register_health_check("failing", "cmp", broken)
    assert is_healthy() is False


def test_is_healthy_no_checks():
    assert is_healthy() is True


def test_deregister_health_check():
    def healthy():
        return HEALTH_STATUS_HEALTHY, "ok"
    register_health_check("test_check", "cmp", healthy)
    assert len(run_all_health_checks().checks) == 1
    deregister_health_check("test_check", "cmp")
    assert len(run_all_health_checks().checks) == 0


def test_deregister_nonexistent():
    deregister_health_check("nonexistent", "cmp")
