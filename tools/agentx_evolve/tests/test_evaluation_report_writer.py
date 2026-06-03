import pytest
from agentx_evolve.evaluation.report_writer import (
    write_evaluation_report,
    write_evaluation_report_json,
)
from agentx_evolve.evaluation.evaluation_models import EvaluationRun, EvaluationReport


class TestEvaluationReportWriter:
    def test_write_report_returns_dict(self, tmp_path):
        run = EvaluationRun(run_id="test-run")
        result = write_evaluation_report(run, tmp_path)
        assert isinstance(result, dict)

    def test_write_report_json(self, tmp_path):
        report = EvaluationReport(report_id="test", run_id="test-run")
        path = write_evaluation_report_json(report, tmp_path)
        assert path is not None
