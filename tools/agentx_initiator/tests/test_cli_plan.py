import pytest
from agentx_initiator.core.evolution_planner import generate_plan, generate_evolution_plan


def test_plan_logic():
    plan = generate_plan()
    assert len(plan) > 0
    assert any(item["category"] == "fic" for item in plan)


def test_evolution_plan_api():
    plan = generate_evolution_plan()
    assert hasattr(plan, "plan_id")
    assert hasattr(plan, "steps")
