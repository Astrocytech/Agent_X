from pathlib import Path

import pytest

from agentx_evolve.monitoring.monitoring_status import (
    _component_statuses,
    register_component, set_component_status,
    update_session_count, build_runtime_status, get_component_status,
)
from agentx_evolve.monitoring.monitoring_events import (
    STATUS_RUNNING, STATUS_STOPPED, STATUS_DEGRADED, STATUS_STARTING,
)


def setup_function():
    _component_statuses.clear()


def teardown_function():
    _component_statuses.clear()


def test_register_component():
    rs = register_component("cmp_a", version="1.0")
    assert rs.component == "cmp_a"
    assert rs.status == STATUS_STARTING
    assert rs.version == "1.0"
    assert rs.active_sessions == 0


def test_register_component_idempotent():
    rs1 = register_component("cmp_a")
    rs2 = register_component("cmp_a")
    assert rs1 is rs2


def test_register_component_different_names():
    rs1 = register_component("cmp_a")
    rs2 = register_component("cmp_b")
    assert rs1 is not rs2


def test_set_component_status():
    register_component("cmp_a")
    rs = set_component_status("cmp_a", STATUS_RUNNING)
    assert rs is not None
    assert rs.status == STATUS_RUNNING
    assert rs.last_event_timestamp != ""


def test_set_component_status_nonexistent():
    rs = set_component_status("nonexistent", STATUS_RUNNING)
    assert rs is None


def test_set_component_status_stopped():
    register_component("cmp_a")
    set_component_status("cmp_a", STATUS_STOPPED)
    assert get_component_status("cmp_a").status == STATUS_STOPPED


def test_update_session_count():
    register_component("cmp_a")
    rs = update_session_count("cmp_a", delta=1)
    assert rs.active_sessions == 1
    update_session_count("cmp_a", delta=2)
    assert get_component_status("cmp_a").active_sessions == 3


def test_update_session_count_negative():
    register_component("cmp_a")
    update_session_count("cmp_a", delta=5)
    update_session_count("cmp_a", delta=-2)
    assert get_component_status("cmp_a").active_sessions == 3


def test_update_session_count_clamp_to_zero():
    register_component("cmp_a")
    update_session_count("cmp_a", delta=-5)
    assert get_component_status("cmp_a").active_sessions == 0


def test_update_session_count_nonexistent():
    rs = update_session_count("nonexistent", delta=1)
    assert rs is None


def test_build_runtime_status():
    register_component("cmp_a", version="1.0")
    set_component_status("cmp_a", STATUS_RUNNING)
    result = build_runtime_status()
    assert result["overall_status"] == STATUS_RUNNING
    assert "cmp_a" in result["components"]
    assert result["components"]["cmp_a"]["version"] == "1.0"


def test_build_runtime_status_stopped():
    register_component("cmp_a")
    register_component("cmp_b")
    set_component_status("cmp_a", STATUS_RUNNING)
    set_component_status("cmp_b", STATUS_STOPPED)
    result = build_runtime_status()
    assert result["overall_status"] == STATUS_STOPPED


def test_build_runtime_status_degraded():
    register_component("cmp_a")
    set_component_status("cmp_a", STATUS_DEGRADED)
    result = build_runtime_status()
    assert result["overall_status"] == STATUS_DEGRADED


def test_build_runtime_status_with_dir(tmp_path):
    register_component("cmp_a")
    set_component_status("cmp_a", STATUS_RUNNING)
    result = build_runtime_status(base_dir=tmp_path)
    status_path = tmp_path / "runtime_status.json"
    assert status_path.exists()
    import json
    data = json.loads(status_path.read_text())
    assert data["overall_status"] == STATUS_RUNNING


def test_build_runtime_status_empty():
    result = build_runtime_status()
    assert result["components"] == {}


def test_get_component_status():
    register_component("cmp_a")
    rs = get_component_status("cmp_a")
    assert rs is not None
    assert rs.component == "cmp_a"


def test_get_component_status_nonexistent():
    rs = get_component_status("nonexistent")
    assert rs is None
