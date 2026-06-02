import pytest
from agentx_initiator.core.evolution_planner import generate_plan, generate_evolution_plan
from agentx_initiator.core.evolution_model import EvolutionPlan


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


def test_generate_evolution_plan_returns_plan():
    plan = generate_evolution_plan()
    assert isinstance(plan, EvolutionPlan)
    assert plan.status == "DRAFT"
    assert len(plan.steps) > 0


def test_generate_evolution_plan_blocked():
    plan = generate_evolution_plan(governance_decision={"decision": "BLOCK"})
    statuses = [s.get("status") for s in plan.steps]
    assert "BLOCKED" in statuses
