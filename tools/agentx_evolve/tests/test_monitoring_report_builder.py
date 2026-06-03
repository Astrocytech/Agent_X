import pytest
from agentx_evolve.monitoring.report_builder import MonitoringReport, ReportBuilder


class TestMonitoringReport:
    def test_default_values(self):
        r = MonitoringReport()
        assert r.report_id == ""
        assert r.metrics == {}
        assert r.events == []


class TestReportBuilder:
    def test_build_empty(self):
        builder = ReportBuilder(report_id="r-001")
        report = builder.build()
        assert report.report_id == "r-001"
        assert report.metrics == {}

    def test_add_metric(self):
        builder = ReportBuilder()
        builder.add_metric("cpu", 0.85)
        report = builder.build()
        assert report.metrics["cpu"] == 0.85

    def test_add_event(self):
        builder = ReportBuilder()
        builder.add_event({"type": "test", "value": 1})
        report = builder.build()
        assert len(report.events) == 1

    def test_fluent_interface(self):
        builder = ReportBuilder()
        builder.add_metric("a", 1.0).add_metric("b", 2.0)
        report = builder.build()
        assert report.metrics == {"a": 1.0, "b": 2.0}
