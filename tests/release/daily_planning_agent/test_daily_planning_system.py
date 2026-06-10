from __future__ import annotations

from tool_gateway.seed_tools.planning_fixture_read import FIXTURES
from daily_planning_agent import ask_planning


def test_full_pipeline_urgent_today() -> None:
    result = ask_planning("urgent_today")
    assert isinstance(result["top_priority"], str)
    assert len(result["ordered_tasks"]) > 0
    assert isinstance(result["reason"], str) and len(result["reason"]) > 0
    assert isinstance(result["blocked_tasks"], list)


def test_full_pipeline_low_effort_high_urgency() -> None:
    result = ask_planning("low_effort_high_urgency")
    assert result["top_priority"] is not None
    assert len(result["ordered_tasks"]) > 0
    assert result["safe_failure"] is False


def test_full_pipeline_several_low_priority() -> None:
    result = ask_planning("several_low_priority")
    assert result["safe_failure"] is False
    assert len(result["ordered_tasks"]) == 5


def test_full_pipeline_blocked_task() -> None:
    result = ask_planning("blocked_task")
    assert len(result["blocked_tasks"]) > 0


def test_ordered_tasks_sorted_by_priority() -> None:
    result = ask_planning("urgent_today")
    ordered = result["ordered_tasks"]
    assert len(ordered) > 0
    assert result["top_priority"] == ordered[0]


def test_blocked_tasks_for_dependency_chain() -> None:
    result = ask_planning("dependency_chain")
    assert len(result["blocked_tasks"]) > 0


def test_safe_failure_for_circular_dependency() -> None:
    result = ask_planning("circular_dependency")
    assert result["safe_failure"] is True
    assert len(result["blocked_tasks"]) > 0


def test_safe_failure_for_duplicate_ids() -> None:
    result = ask_planning("duplicate_ids")
    assert result["safe_failure"] is True


def test_all_fields_present_in_output() -> None:
    result = ask_planning("urgent_today")
    assert "top_priority" in result
    assert "ordered_tasks" in result
    assert "reason" in result
    assert "blocked_tasks" in result
    assert "safe_failure" in result
    assert "scenario_id" in result


def test_safe_failure_false_for_valid_data() -> None:
    result = ask_planning("high_effort_low_urgency")
    assert result["safe_failure"] is False


def test_pipeline_all_valid_scenarios() -> None:
    valid = {"urgent_today", "several_low_priority", "blocked_task", "missing_due_date",
             "all_completed", "conflicting_urgency", "high_effort_low_urgency",
             "low_effort_high_urgency", "dependency_chain"}
    for scenario in valid:
        result = ask_planning(scenario)
        assert isinstance(result["ordered_tasks"], list)
        assert isinstance(result["reason"], str) and len(result["reason"]) > 0
