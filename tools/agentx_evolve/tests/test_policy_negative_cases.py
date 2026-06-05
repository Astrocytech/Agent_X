import pytest
from agentx_evolve.policy.capability_policy import (
    capability_requires_approval,
    capability_requires_governance,
    capability_requires_sandbox,
    find_capability,
    is_effect_allowed,
    is_effect_blocked,
)
from agentx_evolve.policy.model_policy import (
    find_model_profile,
    model_may_read_source,
    model_may_write_files,
    model_task_allowed,
)
from agentx_evolve.policy.policy_decision import (
    check_role_permission as check_role_permission_dec,
    choose_strictest_decision,
    evaluate_model_request,
    evaluate_tool_request,
)
from agentx_evolve.policy.policy_models import (
    CapabilityEntry,
    CapabilityPolicy,
    DECISION_ALLOW,
    DECISION_BLOCK,
    DECISION_INVALID_POLICY,
    DECISION_UNKNOWN_MODEL,
    DECISION_UNKNOWN_ROLE,
    DECISION_UNKNOWN_TOOL,
    EFFECT_READ,
    EFFECT_WRITE_SOURCE,
    ModelPolicy,
    ModelProfile,
    PolicyDecision,
    ROLE_ORCHESTRATOR,
    ToolEntry,
    ToolPolicy,
)


def test_evaluate_tool_request_none_policies():
    result = evaluate_tool_request(
        ROLE_ORCHESTRATOR, "read", EFFECT_READ, None, None, None
    )
    assert result.decision == DECISION_INVALID_POLICY


def test_evaluate_model_request_none_policy():
    result = evaluate_model_request(
        ROLE_ORCHESTRATOR, "p1", "code_analysis", None, None
    )
    assert result.decision == DECISION_INVALID_POLICY


def test_find_capability_no_match():
    cap_policy = CapabilityPolicy(
        policy_id="cp-1",
        roles=[ROLE_ORCHESTRATOR],
    )
    result = find_capability(ROLE_ORCHESTRATOR, "nonexistent_tool", cap_policy)
    assert result is None


def test_is_effect_allowed_no_capability():
    cap_policy = CapabilityPolicy(policy_id="cp-1", roles=[ROLE_ORCHESTRATOR])
    result = is_effect_allowed(EFFECT_READ, None, cap_policy)
    assert result is False


def test_is_effect_blocked_no_capability():
    cap_policy = CapabilityPolicy(policy_id="cp-1", roles=[ROLE_ORCHESTRATOR])
    result = is_effect_blocked(EFFECT_READ, None, cap_policy)
    assert result is True


def test_capability_requires_approval_no_capability():
    cap_policy = CapabilityPolicy(policy_id="cp-1", roles=[ROLE_ORCHESTRATOR])
    result = capability_requires_approval(EFFECT_READ, None, cap_policy)
    assert result is False


def test_capability_requires_governance_no_capability():
    cap_policy = CapabilityPolicy(policy_id="cp-1", roles=[ROLE_ORCHESTRATOR])
    result = capability_requires_governance(EFFECT_READ, None, cap_policy)
    assert result is False


def test_capability_requires_sandbox_no_capability():
    cap_policy = CapabilityPolicy(policy_id="cp-1", roles=[ROLE_ORCHESTRATOR])
    result = capability_requires_sandbox(EFFECT_READ, None, cap_policy)
    assert result is False


def test_find_model_profile_none():
    model_policy = ModelPolicy(policy_id="mp-1")
    result = find_model_profile("nonexistent", model_policy)
    assert result is None


def test_model_task_allowed_empty_policy():
    model_policy = ModelPolicy(policy_id="mp-1")
    result = model_task_allowed("p1", "code_analysis", model_policy)
    assert result is False


def test_model_may_read_source_empty_policy():
    model_policy = ModelPolicy(policy_id="mp-1")
    result = model_may_read_source("p1", model_policy)
    assert result is False


def test_model_may_write_files_empty_policy():
    model_policy = ModelPolicy(policy_id="mp-1")
    result = model_may_write_files("p1", model_policy)
    assert result is False


def test_choose_strictest_decision_with_none():
    decisions = [PolicyDecision(decision=DECISION_ALLOW), None]
    result = choose_strictest_decision(decisions)
    assert result.decision == DECISION_ALLOW


def test_tool_policy_with_empty_tools():
    tool_policy = ToolPolicy(policy_id="tp-1")
    cap_policy = CapabilityPolicy(
        policy_id="cp-1",
        default_decision=DECISION_ALLOW,
        roles=[ROLE_ORCHESTRATOR],
    )
    result = evaluate_tool_request(
        ROLE_ORCHESTRATOR, "unknown_tool", EFFECT_READ, None,
        cap_policy, tool_policy,
    )
    assert result.decision in (DECISION_UNKNOWN_TOOL, DECISION_BLOCK)


def test_model_policy_with_no_profiles():
    model_policy = ModelPolicy(policy_id="mp-1")
    cap_policy = CapabilityPolicy(
        policy_id="cp-1",
        default_decision=DECISION_ALLOW,
        roles=[ROLE_ORCHESTRATOR],
    )
    result = evaluate_model_request(
        ROLE_ORCHESTRATOR, "p1", "code_analysis",
        model_policy, cap_policy,
    )
    assert result.decision == DECISION_UNKNOWN_MODEL


def test_find_capability_wrong_role():
    cap_policy = CapabilityPolicy(
        policy_id="cp-1",
        roles=[ROLE_ORCHESTRATOR],
        capabilities=[
            CapabilityEntry(
                role=ROLE_ORCHESTRATOR,
                tool_name="safe_read_file",
                allowed_effects=[EFFECT_READ],
            ),
        ],
    )
    result = find_capability("HUMAN_OPERATOR", "safe_read_file", cap_policy)
    assert result is None


def test_is_effect_allowed_unknown_role_no_capability():
    cap_policy = CapabilityPolicy(policy_id="cp-1", roles=[])
    result = is_effect_allowed(EFFECT_READ, None, cap_policy)
    assert result is False
