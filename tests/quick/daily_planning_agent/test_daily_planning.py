from __future__ import annotations

from tool_gateway.seed_tools.planning_fixture_read import FIXTURES, PlanningFixtureReadTool
from daily_planning_agent.planner import DailyPlanningPlannerPort


def test_tool_returns_data_for_urgent_today() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="urgent_today")
    assert result["success"]
    assert len(result["data"]["tasks"]) == 5


def test_tool_returns_data_for_several_low_priority() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="several_low_priority")
    assert result["success"]
    assert len(result["data"]["tasks"]) == 5


def test_tool_returns_data_for_blocked_task() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="blocked_task")
    assert result["success"]
    assert result["data"]["task_count"] == 5


def test_tool_returns_data_for_missing_due_date() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="missing_due_date")
    assert result["success"]
    assert result["data"]["task_count"] == 4


def test_tool_returns_data_for_malformed_entry() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="malformed_entry")
    assert result["success"]
    assert result["data"]["task_count"] == 5


def test_tool_returns_data_for_empty_list() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="empty_list")
    assert result["success"]
    assert result["data"]["task_count"] == 0


def test_tool_returns_data_for_all_completed() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="all_completed")
    assert result["success"]
    assert result["data"]["task_count"] == 3


def test_tool_returns_data_for_conflicting_urgency() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="conflicting_urgency")
    assert result["success"]
    assert result["data"]["task_count"] == 3


def test_tool_returns_data_for_high_effort_low_urgency() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="high_effort_low_urgency")
    assert result["success"]
    assert result["data"]["task_count"] == 4


def test_tool_returns_data_for_low_effort_high_urgency() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="low_effort_high_urgency")
    assert result["success"]
    assert result["data"]["task_count"] == 4


def test_tool_returns_data_for_dependency_chain() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="dependency_chain")
    assert result["success"]
    assert result["data"]["task_count"] == 5


def test_tool_returns_data_for_duplicate_ids() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="duplicate_ids")
    assert result["success"]
    assert result["data"]["task_count"] == 3


def test_tool_returns_data_for_circular_dependency() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="circular_dependency")
    assert result["success"]
    assert result["data"]["task_count"] == 4


def test_tool_returns_data_for_invalid_due_date() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="invalid_due_date")
    assert result["success"]
    assert result["data"]["task_count"] == 4


def test_tool_returns_data_for_nonexistent_dependency() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="nonexistent_dependency")
    assert result["success"]
    assert result["data"]["task_count"] == 3


def test_tool_unknown_scenario_returns_failure() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="does_not_exist")
    assert not result["success"]


def test_tool_null_scenario_returns_failure() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id=None)
    assert not result["success"]


def test_tool_empty_scenario_returns_failure() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="")
    assert not result["success"]


def test_all_fixture_scenarios_covered() -> None:
    tool = PlanningFixtureReadTool()
    for scenario_id in FIXTURES:
        result = tool(scenario_id=scenario_id)
        assert result["success"], f"Scenario {scenario_id} failed"
        assert "data" in result


def test_scenario_source_in_data() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="urgent_today")
    assert result["success"]
    assert result["data"]["source"] == "fixture"


def test_parse_llm_json_extracts_plain_json() -> None:
    raw = '{"top_priority": "t1", "ordered_tasks": ["t1", "t2"], "reason": "Urgent first", "blocked_tasks": [], "safe_failure": false}'
    result = DailyPlanningPlannerPort._parse_llm_json(raw)
    assert result is not None
    assert result["top_priority"] == "t1"
    assert result["ordered_tasks"] == ["t1", "t2"]


def test_parse_llm_json_extracts_from_markdown() -> None:
    raw = '```json\n{"top_priority": null, "ordered_tasks": [], "reason": "Empty list", "blocked_tasks": [], "safe_failure": true}\n```'
    result = DailyPlanningPlannerPort._parse_llm_json(raw)
    assert result is not None
    assert result["safe_failure"] is True


def test_parse_llm_json_extracts_with_surrounding_text() -> None:
    raw = 'Here is the plan:\n{"top_priority": "t3", "ordered_tasks": ["t3", "t1"], "reason": "T3 is most urgent", "blocked_tasks": [], "safe_failure": false}\nDone.'
    result = DailyPlanningPlannerPort._parse_llm_json(raw)
    assert result is not None
    assert result["top_priority"] == "t3"


def test_parse_llm_json_returns_none_for_invalid() -> None:
    assert DailyPlanningPlannerPort._parse_llm_json("not json") is None
    assert DailyPlanningPlannerPort._parse_llm_json("") is None
    assert DailyPlanningPlannerPort._parse_llm_json("{}") is not None
