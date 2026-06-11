"""Integration tests for inverse-science governance routing."""
import os, sys, json, pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "agentx_evolve"))

from workflow.inverse_science_cli import cmd_plan, cmd_candidates, cmd_rank, cmd_decide, cmd_observe

def test_candidate_routed_to_governance():
    result = cmd_decide({"decision": "allow", "candidate_id": "C1"})
    assert result["governance_routed"] is True
    assert result["patch_executed"] is False

def test_allow_does_not_execute_patch():
    result = cmd_decide({"decision": "allow"})
    assert result["patch_executed"] is False

def test_allow_with_limits_propagates():
    result = cmd_decide({"decision": "allow_with_limits"})
    assert result["patch_executed"] is False

def test_reject_creates_no_patch_request():
    result = cmd_decide({"decision": "reject"})
    assert result["patch_executed"] is False

def test_require_reframe_creates_no_patch():
    result = cmd_decide({"decision": "require_reframe"})
    assert result["patch_executed"] is False

def test_observation_writes_evidence():
    result = cmd_observe({"evidence_class": "SIMULATION"})
    assert result["status"] == "ok"
    assert "observation_id" in result

def test_plan_creation():
    result = cmd_plan({"capability": "umbrella_weather_improvement", "constraints": ["fixture-only"]})
    assert result["status"] == "ok"
    assert "plan" in result
    assert result["plan"]["target_capability"] == "umbrella_weather_improvement"
