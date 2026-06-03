from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun,
    EvaluationCaseResult,
    EvaluationScore,
    utc_now_iso,
    new_eval_id,
    to_dict,
)
from agentx_evolve.evaluation.report_writer import write_evaluation_report


def _make_failing_run() -> EvaluationRun:
    return EvaluationRun(
        run_id=new_eval_id("run"),
        suite_id="test_suite",
        case_results=[
            EvaluationCaseResult(
                case_id="case_001",
                status="EVAL_FAIL",
                passed=False,
                score=0.0,
                message="Failed threshold",
            )
        ],
        score_summary={"passed_cases": 0, "failed_cases": 1, "pass_rate": 0.0},
        threshold_summary={"all_passed": False, "failures": ["case_001 below threshold"]},
        timestamp=utc_now_iso(),
    )


class TestEvaluationPromotionGateSummary:
    def test_passing_run_allows_promotion(self, tmp_path: Path):
        run = _make_run()
        result = write_evaluation_report(run, repo_root=tmp_path)
        report = result["report"]
        passed = report["threshold_summary"].get("all_passed", False)
        assert passed is True

    def test_failing_run_blocks_promotion(self, tmp_path: Path):
        run = _make_failing_run()
        result = write_evaluation_report(run, repo_root=tmp_path)
        report = result["report"]
        passed = report["threshold_summary"].get("all_passed", True)
        assert passed is False

    def test_promotion_gate_summary_json(self, tmp_path: Path):
        run = _make_run()
        result = write_evaluation_report(run, repo_root=tmp_path)
        json_path = Path(result["json_path"])
        data = json.loads(json_path.read_text())
        assert "score_summary" in data
        assert "threshold_summary" in data


def _make_run() -> EvaluationRun:
    return EvaluationRun(
        run_id=new_eval_id("run"),
        suite_id="test_suite",
        case_results=[
            EvaluationCaseResult(
                case_id="case_001",
                status="EVAL_PASS",
                passed=True,
                score=1.0,
            )
        ],
        score_summary={"passed_cases": 1, "failed_cases": 0, "pass_rate": 1.0},
        threshold_summary={"all_passed": True},
        timestamp=utc_now_iso(),
    )
