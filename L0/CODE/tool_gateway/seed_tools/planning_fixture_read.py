from __future__ import annotations

import logging
import time

__all__ = ["PlanningFixtureReadTool"]

logger = logging.getLogger(__name__)

FIXTURES: dict[str, list[dict]] = {
    "urgent_today": [
        {"id": "t1", "title": "Submit report", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t2", "title": "Fix critical bug", "deadline": "2026-06-10", "urgency": "high", "effort": "medium", "dependencies": None, "completed": False},
        {"id": "t3", "title": "Plan sprint", "deadline": "2026-06-15", "urgency": "medium", "effort": "medium", "dependencies": None, "completed": False},
        {"id": "t4", "title": "Review PR", "deadline": "2026-06-12", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t5", "title": "Write docs", "deadline": "2026-06-20", "urgency": "low", "effort": "high", "dependencies": None, "completed": False},
    ],
    "several_low_priority": [
        {"id": "t1", "title": "Read articles", "deadline": "2026-07-01", "urgency": "low", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t2", "title": "Organise desk", "deadline": "2026-06-30", "urgency": "low", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t3", "title": "Update resume", "deadline": "2026-08-01", "urgency": "low", "effort": "medium", "dependencies": None, "completed": False},
        {"id": "t4", "title": "Clean inbox", "deadline": "2026-06-25", "urgency": "low", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t5", "title": "Back up files", "deadline": "2026-09-01", "urgency": "low", "effort": "high", "dependencies": None, "completed": False},
    ],
    "blocked_task": [
        {"id": "t1", "title": "Set up CI", "deadline": "2026-06-10", "urgency": "high", "effort": "medium", "dependencies": None, "completed": False},
        {"id": "t2", "title": "Write unit tests", "deadline": "2026-06-12", "urgency": "high", "effort": "high", "dependencies": ["t1"], "completed": False},
        {"id": "t3", "title": "Deploy app", "deadline": "2026-06-15", "urgency": "medium", "effort": "medium", "dependencies": ["t2"], "completed": False},
        {"id": "t4", "title": "Clean workspace", "deadline": "2026-06-20", "urgency": "low", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t5", "title": "Send report", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
    ],
    "missing_due_date": [
        {"id": "t1", "title": "Task A", "deadline": None, "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t2", "title": "Task B", "deadline": "2026-06-12", "urgency": "medium", "effort": "medium", "dependencies": None, "completed": False},
        {"id": "t3", "title": "Task C", "deadline": None, "urgency": "low", "effort": "high", "dependencies": None, "completed": False},
        {"id": "t4", "title": "Task D", "deadline": "2026-06-15", "urgency": "high", "effort": "high", "dependencies": None, "completed": False},
    ],
    "malformed_entry": [
        {"id": "t1", "title": "Valid task", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t2", "title": None, "deadline": "2026-06-12", "urgency": "medium", "effort": "medium", "dependencies": None, "completed": False},
        {"id": "t3", "title": "Bad urgency", "deadline": "2026-06-15", "urgency": "extreme", "effort": "medium", "dependencies": None, "completed": False},
        {"id": "t4", "title": "Bad effort", "deadline": "2026-06-18", "urgency": "low", "effort": "super", "dependencies": None, "completed": False},
        {"id": "t5", "title": "Valid task 2", "deadline": "2026-06-20", "urgency": "medium", "effort": "low", "dependencies": None, "completed": False},
    ],
    "empty_list": [],
    "all_completed": [
        {"id": "t1", "title": "Done A", "deadline": "2026-06-01", "urgency": "high", "effort": "low", "dependencies": None, "completed": True},
        {"id": "t2", "title": "Done B", "deadline": "2026-06-02", "urgency": "medium", "effort": "medium", "dependencies": None, "completed": True},
        {"id": "t3", "title": "Done C", "deadline": "2026-06-03", "urgency": "low", "effort": "high", "dependencies": None, "completed": True},
    ],
    "conflicting_urgency": [
        {"id": "t1", "title": "Task one", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t2", "title": "Task two", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t3", "title": "Task three", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
    ],
    "high_effort_low_urgency": [
        {"id": "t1", "title": "Refactor module", "deadline": "2026-07-01", "urgency": "low", "effort": "high", "dependencies": None, "completed": False},
        {"id": "t2", "title": "Write integration tests", "deadline": "2026-07-05", "urgency": "low", "effort": "high", "dependencies": None, "completed": False},
        {"id": "t3", "title": "Optimise queries", "deadline": "2026-07-10", "urgency": "low", "effort": "high", "dependencies": None, "completed": False},
        {"id": "t4", "title": "Clear cache", "deadline": "2026-06-15", "urgency": "medium", "effort": "low", "dependencies": None, "completed": False},
    ],
    "low_effort_high_urgency": [
        {"id": "t1", "title": "Fix typo", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t2", "title": "Approve invoice", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t3", "title": "Reply to email", "deadline": "2026-06-11", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t4", "title": "Update ticket", "deadline": "2026-06-12", "urgency": "medium", "effort": "low", "dependencies": None, "completed": False},
    ],
    "dependency_chain": [
        {"id": "t1", "title": "Design API", "deadline": "2026-06-08", "urgency": "high", "effort": "high", "dependencies": None, "completed": False},
        {"id": "t2", "title": "Implement API", "deadline": "2026-06-10", "urgency": "high", "effort": "high", "dependencies": ["t1"], "completed": False},
        {"id": "t3", "title": "Test API", "deadline": "2026-06-12", "urgency": "high", "effort": "medium", "dependencies": ["t2"], "completed": False},
        {"id": "t4", "title": "Document API", "deadline": "2026-06-15", "urgency": "medium", "effort": "low", "dependencies": ["t3"], "completed": False},
        {"id": "t5", "title": "Ship API", "deadline": "2026-06-20", "urgency": "medium", "effort": "low", "dependencies": ["t4"], "completed": False},
    ],
    "duplicate_ids": [
        {"id": "t1", "title": "First task", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t1", "title": "Second task (dup ID)", "deadline": "2026-06-12", "urgency": "medium", "effort": "medium", "dependencies": None, "completed": False},
        {"id": "t2", "title": "Unique task", "deadline": "2026-06-15", "urgency": "low", "effort": "high", "dependencies": None, "completed": False},
    ],
    "circular_dependency": [
        {"id": "t1", "title": "Task A", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": ["t2"], "completed": False},
        {"id": "t2", "title": "Task B", "deadline": "2026-06-11", "urgency": "high", "effort": "medium", "dependencies": ["t3"], "completed": False},
        {"id": "t3", "title": "Task C", "deadline": "2026-06-12", "urgency": "medium", "effort": "high", "dependencies": ["t1"], "completed": False},
        {"id": "t4", "title": "Task D", "deadline": "2026-06-13", "urgency": "low", "effort": "low", "dependencies": None, "completed": False},
    ],
    "invalid_due_date": [
        {"id": "t1", "title": "Valid task", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t2", "title": "Bad date", "deadline": "not-a-date", "urgency": "medium", "effort": "medium", "dependencies": None, "completed": False},
        {"id": "t3", "title": "Null date", "deadline": None, "urgency": "low", "effort": "high", "dependencies": None, "completed": False},
        {"id": "t4", "title": "Another valid", "deadline": "2026-06-12", "urgency": "high", "effort": "high", "dependencies": None, "completed": False},
    ],
    "nonexistent_dependency": [
        {"id": "t1", "title": "Real task", "deadline": "2026-06-10", "urgency": "high", "effort": "low", "dependencies": None, "completed": False},
        {"id": "t2", "title": "Depends on ghost", "deadline": "2026-06-12", "urgency": "medium", "effort": "medium", "dependencies": ["ghost_task"], "completed": False},
        {"id": "t3", "title": "Another real", "deadline": "2026-06-15", "urgency": "low", "effort": "high", "dependencies": ["missing_id"], "completed": False},
    ],
}


class PlanningFixtureReadTool:
    """Simulated daily-planning fixture tool — returns deterministic task-list data."""

    def __call__(self, scenario_id: str) -> dict:
        if not scenario_id or not isinstance(scenario_id, str):
            return {"success": False, "error": "scenario_id is required"}
        sid = scenario_id.strip().lower()
        if sid not in FIXTURES:
            return {"success": False, "error": f"unknown scenario: {scenario_id}"}

        logger.info("Simulating planning fixture fetch for %s", scenario_id)
        time.sleep(0.05)

        tasks = FIXTURES[sid]
        return {
            "success": True,
            "data": {
                "scenario_id": sid,
                "tasks": tasks,
                "task_count": len(tasks),
                "source": "fixture",
            },
        }
