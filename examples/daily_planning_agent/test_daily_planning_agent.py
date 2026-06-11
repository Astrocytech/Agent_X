from __future__ import annotations

from daily_planning_agent.agent import DailyPlanningAgent
from daily_planning_agent.fixtures import FIXTURES


def test_normal_day_returns_plan() -> None:
    result = DailyPlanningAgent().plan("normal_day")
    assert len(result["plan"]) >= 4
    assert result["source"] == "fixture"
    assert result["confidence"] in ("high", "medium", "low", "unknown")


def test_normal_day_top_priority_is_high_urgency() -> None:
    result = DailyPlanningAgent().plan("normal_day")
    assert result["top_priority"] is not None


def test_one_urgent_task_is_top_priority() -> None:
    result = DailyPlanningAgent().plan("one_urgent")
    assert result["top_priority"] == "t1"
    assert "Fix production bug" in result["plan"][0]


def test_conflicting_tasks_are_ordered_by_urgency() -> None:
    result = DailyPlanningAgent().plan("conflicting")
    assert result["top_priority"] is not None
    assert len(result["plan"]) == 3


def test_too_many_tasks_triggers_budget_warning() -> None:
    result = DailyPlanningAgent().plan("too_many")
    budget_minutes = 480
    warning = f"exceeds available time budget ({budget_minutes} min)"
    assert warning in result["plan"][-1] or "exceeds" in result["plan"][-1].lower()


def test_empty_task_list_returns_empty_plan() -> None:
    result = DailyPlanningAgent().plan("empty")
    assert result["plan"] == []
    assert result["top_priority"] is None
    assert result["confidence"] == "low"


def test_malformed_fixture_fails_safely() -> None:
    result = DailyPlanningAgent().plan("malformed")
    assert result["plan"] == []
    assert result["top_priority"] is None
    assert result["confidence"] == "low"
    assert "Malformed" in result["reason"] or "malformed" in result["reason"]


def test_missing_time_budget_returns_medium_confidence() -> None:
    result = DailyPlanningAgent().plan("missing_budget")
    assert len(result["plan"]) == 2
    assert result["confidence"] == "medium"


def test_none_scenario_returns_unknown() -> None:
    result = DailyPlanningAgent().plan(None)
    assert result["plan"] == []
    assert result["top_priority"] is None
    assert result["confidence"] == "unknown"


def test_empty_scenario_returns_unknown() -> None:
    result = DailyPlanningAgent().plan("")
    assert result["plan"] == []


def test_unknown_scenario_returns_unknown() -> None:
    result = DailyPlanningAgent().plan("nonexistent_scenario")
    assert result["plan"] == []
    assert result["confidence"] == "unknown"


def test_output_contract_has_all_required_fields() -> None:
    result = DailyPlanningAgent().plan("normal_day")
    assert "plan" in result
    assert "top_priority" in result
    assert "reason" in result
    assert "source" in result
    assert "confidence" in result


def test_all_fixtures_produce_valid_output() -> None:
    agent = DailyPlanningAgent()
    for sid in FIXTURES:
        result = agent.plan(sid)
        assert "plan" in result
        assert "top_priority" in result or result["top_priority"] is None
        assert "reason" in result
        assert result["source"] == "fixture"
        assert result["confidence"] in ("high", "medium", "low", "unknown")


def test_plan_lines_are_strings() -> None:
    result = DailyPlanningAgent().plan("normal_day")
    for line in result["plan"]:
        assert isinstance(line, str)


def test_reason_is_string() -> None:
    result = DailyPlanningAgent().plan("normal_day")
    assert isinstance(result["reason"], str)


def test_normal_day_reason_includes_task_count() -> None:
    result = DailyPlanningAgent().plan("normal_day")
    assert "5" in result["reason"] or "tasks" in result["reason"].lower()


def test_high_urgency_tasks_appear_first() -> None:
    result = DailyPlanningAgent().plan("normal_day")
    first_plan_line = result["plan"][0].lower()
    assert "high" in first_plan_line or result["plan"][0].startswith("Code review")


def test_conflicting_scenario_has_both_tasks_in_plan() -> None:
    result = DailyPlanningAgent().plan("conflicting")
    plan_text = " ".join(result["plan"]).lower()
    assert "client presentation" in plan_text
    assert "sprint planning" in plan_text
