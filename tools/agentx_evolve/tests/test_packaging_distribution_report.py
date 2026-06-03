import pytest
from agentx_evolve.packaging.distribution_report import DistributionReport


class TestDistributionReport:
    def test_defaults(self):
        r = DistributionReport()
        assert r.report_id == ""
        assert r.layers == {}

    def test_add_result(self):
        r = DistributionReport()
        r.add_result("context", "PASS")
        assert r.layers["context"] == "PASS"

    def test_summary_all_pass(self):
        r = DistributionReport(report_id="r-001")
        r.add_result("context", "PASS")
        r.add_result("git", "OK")
        s = r.summary()
        assert s["total_layers"] == 2
        assert s["passed"] == 2
        assert s["failed"] == 0

    def test_summary_mixed(self):
        r = DistributionReport()
        r.add_result("context", "PASS")
        r.add_result("git", "FAIL")
        s = r.summary()
        assert s["passed"] == 1
        assert s["failed"] == 1

    def test_summary_empty(self):
        r = DistributionReport()
        s = r.summary()
        assert s["total_layers"] == 0
