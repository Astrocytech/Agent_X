import pytest
from agentx_evolve.evaluation.report_writer import (
    write_evaluation_report,
    write_evaluation_report_json,
    write_latest_evaluation_report,
)
from agentx_evolve.evaluation.evaluation_models import EvaluationRun


class TestReportWriter:
    def test_write_report(self, tmp_path):
        run = EvaluationRun(run_id="test")
        result = write_evaluation_report(run, tmp_path)
        assert isinstance(result, dict)

    def test_write_latest(self, tmp_path):
        run = EvaluationRun(run_id="test")
        result = write_latest_evaluation_report(run, tmp_path)
        assert result is not None
