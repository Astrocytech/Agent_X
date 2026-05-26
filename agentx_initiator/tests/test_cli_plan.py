from agentx_initiator.core.evolution_planner import generate_plan


def test_plan_logic():
    plan = generate_plan()
    assert len(plan) > 0
    assert any(item["category"] == "fic" for item in plan)
