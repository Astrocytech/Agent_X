import pytest
from agentx_evolve.monitoring.monitoring_cycle import (
    run_monitoring_cycle,
    MonitoringCycleResult,
)


class TestMonitoringCycle:
    def test_run_cycle(self, tmp_path):
        result = run_monitoring_cycle(repo_root=tmp_path)
        assert isinstance(result, MonitoringCycleResult)

    def test_cycle_with_session(self, tmp_path):
        result = run_monitoring_cycle(repo_root=tmp_path, session_id="test-session")
        assert isinstance(result, MonitoringCycleResult)
