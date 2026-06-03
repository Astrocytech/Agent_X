import pytest
from agentx_evolve.monitoring.completion_record import (
    write_monitoring_completion_record,
    load_monitoring_completion_record,
)


class TestMonitoringCompletionRecord:
    def test_write_and_load(self, tmp_path):
        write_monitoring_completion_record(
            repo_root=tmp_path,
            status="COMPLETED",
        )
        result = load_monitoring_completion_record(tmp_path)
        assert result is not None

    def test_load_empty_returns_none(self, tmp_path):
        result = load_monitoring_completion_record(tmp_path)
        assert result is None
