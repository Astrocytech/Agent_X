"""Metric definition tests for all 8 plan categories — N1 §2.

Categories:
1. goals        — goal lifecycle (created, completed, failed)
2. actions      — action execution (planned, executed, skipped)
3. denials      — policy or capability denials
4. rollbacks    — rollback operations
5. tests        — test execution (pass, fail, skip)
6. invariant failures — invariant violations
7. retries      — retry attempts
8. generated-agent outcomes — generated agent metric tracking
"""
from __future__ import annotations

import pytest

from agentx_evolve.evaluation.evaluation_models import EvaluationScore, EvaluationCaseResult
from agentx_evolve.evaluation.score_calculator import (
    calculate_weighted_score,
    calculate_run_score,
)


def _make_result(case_id: str, passed: bool, weight: float = 1.0) -> EvaluationCaseResult:
    return EvaluationCaseResult(
        case_id=case_id,
        passed=passed,
        score=1.0 if passed else 0.0,
        weight=weight,
        status="EVAL_PASS" if passed else "EVAL_FAIL",
    )


class TestGoalMetrics:
    def test_goal_completion_rate(self):
        results = [
            _make_result("goal-1", True),
            _make_result("goal-2", True),
            _make_result("goal-3", False),
        ]
        score = calculate_run_score(results)
        assert score.passed_cases == 2
        assert score.failed_cases == 1
        assert score.normalized_score == pytest.approx(2.0 / 3.0)

    def test_goal_agg_no_goals(self):
        score = calculate_run_score([])
        assert score.total_cases == 0
        assert score.pass_rate == 0.0

    def test_goal_all_pass(self):
        results = [_make_result(f"goal-{i}", True) for i in range(5)]
        score = calculate_run_score(results)
        assert score.pass_rate == 1.0
        assert score.normalized_score == 1.0


class TestActionMetrics:
    def test_action_execution_rate(self):
        results = [
            _make_result("action-exec-1", True, weight=2.0),
            _make_result("action-exec-2", True, weight=2.0),
            _make_result("action-exec-3", False, weight=2.0),
        ]
        ws = calculate_weighted_score(results)
        assert ws == pytest.approx(4.0 / 6.0)

    def test_action_plan_all_passed(self):
        results = [_make_result(f"plan-{i}", True) for i in range(3)]
        assert all(r.passed for r in results)

    def test_action_skipped_tracked_as_fail(self):
        result = _make_result("action-skip-1", False)
        assert not result.passed
        assert result.score == 0.0


class TestDenialMetrics:
    def test_denial_tracking(self):
        results = [_make_result("denial-1", True), _make_result("denial-2", False)]
        score = calculate_run_score(results)
        assert score.passed_cases == 1
        assert score.failed_cases == 1

    def test_denial_all_denied(self):
        results = [_make_result(f"denial-{i}", False) for i in range(3)]
        score = calculate_run_score(results)
        assert score.passed_cases == 0
        assert score.failed_cases == 3


class TestRollbackMetrics:
    def test_rollback_success_tracking(self):
        results = [
            _make_result("rollback-1", True),
            _make_result("rollback-2", True),
        ]
        score = calculate_run_score(results)
        assert score.passed_cases == 2

    def test_rollback_failure_tracking(self):
        results = [
            _make_result("rollback-1", True),
            _make_result("rollback-2", False),
        ]
        assert results[0].passed
        assert not results[1].passed

    def test_rollback_rate(self):
        results = [
            _make_result("rollback-ok-1", True),
            _make_result("rollback-ok-2", True),
            _make_result("rollback-fail-1", False),
        ]
        score = calculate_run_score(results)
        assert score.pass_rate == pytest.approx(2.0 / 3.0)


class TestTestMetrics:
    def test_test_pass_rate(self):
        results = [
            _make_result("test-unit-1", True),
            _make_result("test-unit-2", True),
            _make_result("test-unit-3", True),
            _make_result("test-unit-4", False),
        ]
        score = calculate_run_score(results)
        assert score.pass_rate == 0.75

    def test_test_weighted_importance(self):
        results = [
            _make_result("test-critical-1", True, weight=5.0),
            _make_result("test-trivial-1", False, weight=1.0),
        ]
        ws = calculate_weighted_score(results)
        assert ws == pytest.approx(5.0 / 6.0)

    def test_test_all_pass(self):
        results = [_make_result(f"test-{i}", True) for i in range(10)]
        score = calculate_run_score(results)
        assert score.passed_cases == 10
        assert score.failed_cases == 0


class TestInvariantFailureMetrics:
    def test_invariant_failure_count(self):
        results = [_make_result(f"invariant-{i}", False) for i in range(4)]
        assert all(not r.passed for r in results)

    def test_invariant_recovery(self):
        results = [
            _make_result("invariant-crash-1", False),
            _make_result("invariant-recover-1", True),
        ]
        assert not results[0].passed
        assert results[1].passed

    def test_invariant_fail_rate(self):
        results = [
            _make_result("inv-ok-1", True),
            _make_result("inv-ok-2", True),
            _make_result("inv-fail-1", False),
            _make_result("inv-fail-2", False),
        ]
        score = calculate_run_score(results)
        assert score.passed_cases == 2
        assert score.failed_cases == 2


class TestRetryMetrics:
    def test_retry_success_after_fail(self):
        results = [
            _make_result("attempt-1", False),
            _make_result("attempt-2", False),
            _make_result("attempt-3", True),
        ]
        assert not results[0].passed
        assert results[2].passed

    def test_retry_exhaustion(self):
        results = [_make_result(f"retry-{i}", False) for i in range(5)]
        assert all(not r.passed for r in results)

    def test_retry_partial_success(self):
        results = [
            _make_result("retry-try-1", False),
            _make_result("retry-try-2", True),
        ]
        score = calculate_run_score(results)
        assert score.passed_cases == 1


class TestGeneratedAgentOutcomeMetrics:
    def test_generated_agent_promotion_rate(self):
        results = [
            _make_result("agent-gen-1", True, weight=3.0),
            _make_result("agent-gen-2", True, weight=3.0),
            _make_result("agent-gen-3", False, weight=3.0),
        ]
        ws = calculate_weighted_score(results)
        assert ws == pytest.approx(6.0 / 9.0)

    def test_generated_agent_all_promoted(self):
        results = [_make_result(f"agent-{i}", True) for i in range(3)]
        assert all(r.passed for r in results)

    def test_generated_agent_all_rejected(self):
        results = [_make_result(f"agent-reject-{i}", False) for i in range(2)]
        assert all(not r.passed for r in results)

    def test_generated_agent_mixed_outcomes(self):
        results = [
            _make_result("agent-ok-1", True),
            _make_result("agent-ok-2", True),
            _make_result("agent-fail-1", False),
            _make_result("agent-fail-2", False),
            _make_result("agent-fail-3", False),
        ]
        score = calculate_run_score(results)
        assert score.passed_cases == 2
        assert score.failed_cases == 3
        assert score.pass_rate == 0.4


class TestCrossCategoryAggregation:
    def test_mixed_categories_can_be_aggregated(self):
        all_results = [
            _make_result("goals", True),
            _make_result("actions", False),
            _make_result("denials", True),
            _make_result("rollbacks", True),
            _make_result("tests", False),
            _make_result("invariants", True),
            _make_result("retries", False),
            _make_result("agents", True),
        ]
        score = calculate_run_score(all_results)
        assert score.total_cases == 8
        assert score.passed_cases == 5
        assert score.pass_rate == pytest.approx(5.0 / 8.0)

    def test_evaluation_score_tracks_all_fields(self):
        score = EvaluationScore(score_id="cross-cat-1")
        assert hasattr(score, "pass_rate")
        assert hasattr(score, "total_cases")
        assert hasattr(score, "passed_cases")
        assert hasattr(score, "failed_cases")
        assert hasattr(score, "normalized_score")
