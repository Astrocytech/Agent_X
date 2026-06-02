import pytest
from agentx_initiator.core.evolution_rules import build_default_steps


def test_build_default_steps_empty():
    steps = build_default_steps(None, None, None)
    assert len(steps) > 0


def test_build_default_steps_blocked_on_gov_fail():
    steps = build_default_steps(None, None, {"decision": "BLOCK"})
    statuses = [s.get("status") for s in steps]
    assert "BLOCKED" in statuses


def test_build_default_steps_validation_fail():
    steps = build_default_steps(None, {"status": "FAIL", "failures": [{"id": "f1"}]}, None)
    categories = [s.get("category") for s in steps]
    assert "VALIDATION" in categories


def test_build_default_steps_arch_gap():
    steps = build_default_steps({"missing_components": ["tests"]}, None, None)
    categories = [s.get("category") for s in steps]
    assert "STRUCTURE" in categories
