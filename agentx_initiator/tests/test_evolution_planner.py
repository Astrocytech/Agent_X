import pytest
from agentx_initiator.core.evolution_planner import generate_plan


pytestmark = pytest.mark.skip(reason="PM2 evolution_planner not active in Product Milestone 1")


def test_generate_plan_returns_list():
    plan = generate_plan()
    assert isinstance(plan, list)
    assert len(plan) > 0


def test_each_item_has_required_keys():
    plan = generate_plan()
    for item in plan:
        assert "priority" in item
        assert "category" in item
        assert "action" in item
