import pytest
from agentx_evolve.policy.policy_decision import evaluate_tool_request
from agentx_evolve.policy.policy_models import (
    CapabilityEntry,
    CapabilityPolicy,
    DECISION_ALLOW,
    DECISION_BLOCK,
    DECISION_NEEDS_SANDBOX_CHECK,
    EFFECT_EXECUTE_COMMAND,
    EFFECT_READ,
    ROLE_ORCHESTRATOR,
    ToolEntry,
    ToolPolicy,
)


@pytest.fixture
def allow_tool_policy():
    return ToolPolicy(
        policy_id="tp-1",
        tools=[ToolEntry(
            tool_name="bash",
            blocked=False,
            requested_effects=[EFFECT_EXECUTE_COMMAND],
        )],
    )


def test_sandbox_required_for_execute_command(allow_tool_policy):
    cap_policy = CapabilityPolicy(
        policy_id="cp-1",
        default_decision=DECISION_ALLOW,
        roles=[ROLE_ORCHESTRATOR],
        sandbox_required_effects=[EFFECT_EXECUTE_COMMAND],
    )
    result = evaluate_tool_request(
        ROLE_ORCHESTRATOR, "bash", EFFECT_EXECUTE_COMMAND, None,
        cap_policy, allow_tool_policy,
    )
    assert result.decision == DECISION_NEEDS_SANDBOX_CHECK


def test_sandbox_not_required_for_read():
    cap_policy = CapabilityPolicy(
        policy_id="cp-1",
        default_decision=DECISION_ALLOW,
        roles=[ROLE_ORCHESTRATOR],
        sandbox_required_effects=[EFFECT_EXECUTE_COMMAND],
    )
    tool_policy = ToolPolicy(
        policy_id="tp-1",
        tools=[
            ToolEntry(
                tool_name="safe_read_file",
                blocked=False,
                requested_effects=[EFFECT_READ],
            ),
        ],
    )
    result = evaluate_tool_request(
        ROLE_ORCHESTRATOR, "safe_read_file", EFFECT_READ, None,
        cap_policy, tool_policy,
    )
    assert result.decision != DECISION_NEEDS_SANDBOX_CHECK


def test_sandbox_required_via_capability_entry(allow_tool_policy):
    cap_policy = CapabilityPolicy(
        policy_id="cp-1",
        default_decision=DECISION_ALLOW,
        roles=[ROLE_ORCHESTRATOR],
        capabilities=[
            CapabilityEntry(
                role=ROLE_ORCHESTRATOR,
                tool_name="bash",
                allowed_effects=[EFFECT_EXECUTE_COMMAND],
                requires_sandbox=True,
            ),
        ],
    )
    result = evaluate_tool_request(
        ROLE_ORCHESTRATOR, "bash", EFFECT_EXECUTE_COMMAND, None,
        cap_policy, allow_tool_policy,
    )
    assert result.decision == DECISION_NEEDS_SANDBOX_CHECK


def test_sandbox_not_required_when_not_in_effect_list():
    cap_policy = CapabilityPolicy(
        policy_id="cp-1",
        default_decision=DECISION_ALLOW,
        roles=[ROLE_ORCHESTRATOR],
        sandbox_required_effects=[EFFECT_EXECUTE_COMMAND],
    )
    tool_policy = ToolPolicy(
        policy_id="tp-1",
        tools=[
            ToolEntry(
                tool_name="safe_write_file",
                blocked=False,
                requested_effects=[EFFECT_READ],
            ),
        ],
    )
    result = evaluate_tool_request(
        ROLE_ORCHESTRATOR, "safe_write_file", EFFECT_READ, None,
        cap_policy, tool_policy,
    )
    assert result.decision != DECISION_NEEDS_SANDBOX_CHECK


def test_sandbox_and_block_interaction(allow_tool_policy):
    cap_policy = CapabilityPolicy(
        policy_id="cp-1",
        default_decision=DECISION_ALLOW,
        roles=[ROLE_ORCHESTRATOR],
        blocked_effects=[EFFECT_EXECUTE_COMMAND],
    )
    result = evaluate_tool_request(
        ROLE_ORCHESTRATOR, "bash", EFFECT_EXECUTE_COMMAND, None,
        cap_policy, allow_tool_policy,
    )
    assert result.decision == DECISION_BLOCK
