from __future__ import annotations

from daily_planning_agent import ask_planning
from tool_gateway.seed_tools.planning_fixture_read import PlanningFixtureReadTool


_REQUIRED_FIELDS = {"top_priority", "ordered_tasks", "reason", "blocked_tasks", "safe_failure", "scenario_id"}


def _assert_valid_output(result: dict, *, safe_failure: bool | None = None) -> None:
    assert _REQUIRED_FIELDS.issubset(result.keys())
    assert isinstance(result.get("ordered_tasks"), list)
    assert isinstance(result.get("reason"), str)
    assert len(result.get("reason", "")) > 0
    if safe_failure is not None:
        assert result["safe_failure"] is safe_failure


# ── 1. Unknown scenario ──────────────────────────────────────────────────────

def test_ask_unknown_scenario_returns_safe_failure() -> None:
    result = ask_planning("nonexistent_scenario")
    assert result["safe_failure"] is True


# ── 2. Required fields present ───────────────────────────────────────────────

def test_output_contains_all_required_fields() -> None:
    _assert_valid_output(ask_planning("urgent_today"))


# ── 3. Malformed entry → safe_failure ────────────────────────────────────────

def test_safe_failure_is_true_for_malformed_entry() -> None:
    result = ask_planning("malformed_entry")
    assert result["safe_failure"] is True


# ── 4. Empty task list → safe_failure ────────────────────────────────────────

def test_safe_failure_is_true_for_empty_list() -> None:
    result = ask_planning("empty_list")
    assert result["safe_failure"] is True


# ── 5. Valid scenario produces structured output ─────────────────────────────

def test_safe_failure_is_false_for_valid_scenario() -> None:
    result = ask_planning("urgent_today")
    assert result["safe_failure"] is False


# ── 6. Tool gateway: known scenario ──────────────────────────────────────────

def test_tool_gateway_registered() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="urgent_today")
    assert result["success"]
    assert len(result["data"]["tasks"]) == 5


# ── 7. Tool gateway: unknown scenario ────────────────────────────────────────

def test_tool_gateway_unknown_scenario() -> None:
    tool = PlanningFixtureReadTool()
    result = tool(scenario_id="does_not_exist")
    assert not result["success"]


# ── 8. ordered_tasks is a list ───────────────────────────────────────────────

def test_output_ordered_tasks_is_list() -> None:
    _assert_valid_output(ask_planning("urgent_today"))


# ── 9. reason is non-empty string ────────────────────────────────────────────

def test_output_reason_is_non_empty_string() -> None:
    _assert_valid_output(ask_planning("urgent_today"))


# ── 10. Null / empty scenario ────────────────────────────────────────────────

def test_output_runtime_null_scenario() -> None:
    result = ask_planning("")
    assert result["safe_failure"] is True


# ── 11. Several low-priority tasks ───────────────────────────────────────────

def test_several_low_priority() -> None:
    _assert_valid_output(ask_planning("several_low_priority"), safe_failure=False)


# ── 12. Blocked task (dependency unmet) ──────────────────────────────────────

def test_blocked_task() -> None:
    _assert_valid_output(ask_planning("blocked_task"), safe_failure=False)


# ── 13. Missing due dates ────────────────────────────────────────────────────

def test_missing_due_date() -> None:
    _assert_valid_output(ask_planning("missing_due_date"), safe_failure=False)


# ── 14. All tasks completed ──────────────────────────────────────────────────

def test_all_completed() -> None:
    _assert_valid_output(ask_planning("all_completed"), safe_failure=False)


# ── 15. Circular dependency → safe_failure ───────────────────────────────────

def test_circular_dependency() -> None:
    result = ask_planning("circular_dependency")
    _assert_valid_output(result)
    assert len(result.get("blocked_tasks", [])) > 0
