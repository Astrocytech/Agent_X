import pytest
from agentx_initiator.core.evolution_planner import generate_plan


pytestmark = pytest.mark.skip(reason="PM2 evolution_planner not active in Product Milestone 1")


def test_plan_logic():
    plan = generate_plan()
    assert len(plan) > 0
    assert any(item["category"] == "fic" for item in plan)
