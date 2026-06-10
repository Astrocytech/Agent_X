from __future__ import annotations

from daily_planning_agent import ask_planning
from tool_gateway.seed_tools.planning_fixture_read import PlanningFixtureReadTool


def test_ask_unknown_scenario_returns_safe_failure() -> None:
    result = ask_planning("nonexistent_scenario")
    assert result["safe_failure"] is True


def test_output_contains_all_required_fields() -> None:
    result = ask_planning("urgent_today")
    required = {"top_priority", "ordered_tasks", "reason", "blocked_tasks", "safe_failure", "scenario_id"}
    assert required.issubset(result.keys())


def test_safe_failure_is_true_for_malformed_entry() -> None:
    result = ask_planning("malformed_entry")
    assert result["safe_failure"] is True


def test_safe_failure_is_true_for_empty_list() -> None:
    result = ask_planning("empty_list")
    assert result["safe_failure"] is True


def test_safe_failure_is_false_for_valid_scenario() -> None:
    result = ask_planning("urgent_today")
    assert result["safe_failure"] is False


def test_tool_gateway_registered() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="urgent_today")
    assert result["success"]
    assert len(result["data"]["tasks"]) == 5


def test_tool_gateway_unknown_scenario() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="does_not_exist")
    assert not result["success"]


def test_output_ordered_tasks_is_list() -> None:
    result = ask_planning("urgent_today")
    assert isinstance(result["ordered_tasks"], list)


def test_output_reason_is_non_empty_string() -> None:
    result = ask_planning("urgent_today")
    assert isinstance(result["reason"], str)
    assert len(result["reason"]) > 0


def test_output_runtime_null_scenario() -> None:
    result = ask_planning("")
    assert result["safe_failure"] is True
