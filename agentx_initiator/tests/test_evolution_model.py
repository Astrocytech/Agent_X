import pytest
from agentx_initiator.core.evolution_model import EvolutionPlan, EvolutionStep, EvolutionDependency, EvolutionManifest, EvolutionAudit


def test_evolution_step_defaults():
    step = EvolutionStep()
    assert step.priority == "P2"
    assert step.category == "UNKNOWN"


def test_evolution_step_to_dict():
    step = EvolutionStep(step_id="s1", priority="P0", category="GOVERNANCE", action="fix", detail="fix it")
    d = step.to_dict()
    assert d["step_id"] == "s1"
    assert d["priority"] == "P0"


def test_evolution_plan_defaults():
    plan = EvolutionPlan()
    assert plan.status == "DRAFT"
    assert plan.steps == []


def test_evolution_manifest_to_dict():
    m = EvolutionManifest(manifest_id="m1", plan_id="p1", step_count=3, completed_count=1, total_dependencies=0, created_at="now", updated_at="now")
    d = m.to_dict()
    assert d["step_count"] == 3


def test_evolution_dependency_defaults():
    dep = EvolutionDependency()
    assert dep.dependency_type == "blocks"


def test_evolution_audit_defaults():
    a = EvolutionAudit()
    assert a.source_component == "EvolutionPlanner"
    assert a.status == "INITIATED"
