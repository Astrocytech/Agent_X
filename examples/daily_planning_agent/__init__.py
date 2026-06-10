from __future__ import annotations

from daily_planning_agent.runtime import DailyPlanningRuntime


def ask_planning(scenario_id: str) -> dict:
    return DailyPlanningRuntime().answer(scenario_id)
