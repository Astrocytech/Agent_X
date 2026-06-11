from __future__ import annotations

from typing import Any

from daily_planning_agent.fixtures import FIXTURES

URGENCY_ORDER = {"high": 0, "medium": 1, "low": 2}
VALID_URGENCIES = {"high", "medium", "low"}


class DailyPlanningAgent:
    def plan(self, scenario_id: str) -> dict[str, Any]:
        if not scenario_id or not isinstance(scenario_id, str):
            return {
                "plan": [],
                "top_priority": None,
                "reason": "No scenario ID provided",
                "source": "fixture",
                "confidence": "unknown",
            }

        sid = scenario_id.strip().lower()
        data = FIXTURES.get(sid)

        if data is None:
            return {
                "plan": [],
                "top_priority": None,
                "reason": f"Unknown scenario: {scenario_id}",
                "source": "fixture",
                "confidence": "unknown",
            }

        tasks = data.get("tasks", [])
        time_budget = data.get("time_budget_min")

        if not tasks:
            return {
                "plan": [],
                "top_priority": None,
                "reason": "No tasks scheduled for today",
                "source": "fixture",
                "confidence": "low",
            }

        for task in tasks:
            title = task.get("title")
            urgency = task.get("urgency")
            if not title or not isinstance(title, str):
                return {
                    "plan": [],
                    "top_priority": None,
                    "reason": "Malformed task data: missing or invalid title",
                    "source": "fixture",
                    "confidence": "low",
                }
            if urgency not in VALID_URGENCIES:
                return {
                    "plan": [],
                    "top_priority": None,
                    "reason": f"Malformed task data: invalid urgency '{urgency}'",
                    "source": "fixture",
                    "confidence": "low",
                }

        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                URGENCY_ORDER.get(t.get("urgency", "low"), 99),
                t.get("deadline", "9999-99-99") or "9999-99-99",
            ),
        )

        total_duration = sum(t.get("duration_min", 0) or 0 for t in sorted_tasks)

        plan_lines = []
        for t in sorted_tasks:
            plan_lines.append(
                f"{t['title']} ({t.get('urgency', 'unknown')}) - due {t.get('deadline', 'no deadline')}"
            )

        if time_budget is not None and total_duration > time_budget:
            plan_lines.append(
                f"NOTE: Total task time ({total_duration} min) exceeds available time budget ({time_budget} min)"
            )

        top = sorted_tasks[0]
        top_priority = top["id"]
        top_title = top["title"]

        if time_budget is None:
            reason = (
                f"Prioritised {len(sorted_tasks)} tasks by urgency and deadline"
            )
            confidence = "medium"
        elif total_duration > time_budget:
            reason = (
                f"Prioritised {len(sorted_tasks)} tasks; {total_duration} min exceeds "
                f"{time_budget} min budget — consider rescheduling"
            )
            confidence = "medium"
        else:
            reason = (
                f"Prioritised {len(sorted_tasks)} tasks by urgency and deadline; "
                f"fits within {time_budget} min budget"
            )
            confidence = "high"

        return {
            "plan": plan_lines,
            "top_priority": top_priority,
            "reason": reason,
            "source": "fixture",
            "confidence": confidence,
        }
