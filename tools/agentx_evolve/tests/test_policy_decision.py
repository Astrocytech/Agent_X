import pytest
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
    DECISION_NEEDS_APPROVAL,
    DECISION_NEEDS_SANDBOX_CHECK,
    DECISION_UNKNOWN_MODEL,
    DECISION_UNKNOWN_ROLE,
    DECISION_UNKNOWN_TOOL,
    DECISION_WARN,
    EFFECT_EXECUTE_COMMAND,
    EFFECT_READ,
    ModelPolicy,
    ModelProfile,
    PolicyDecision,
    ROLE_HUMAN_OPERATOR,
    ROLE_ORCHESTRATOR,
    REASON_TOOL_BLOCKED,
    ToolEntry,
    ToolPolicy as SpecToolPolicy,
)


class TestChooseStrictestDecision:
    def test_block_is_strictest(self):
        decisions = [
            PolicyDecision(decision=DECISION_ALLOW),
            PolicyDecision(decision=DECISION_BLOCK),
            PolicyDecision(decision=DECISION_WARN),
        ]
        result = choose_strictest_decision(decisions)
        assert result.decision == DECISION_BLOCK

    def test_allow_is_weakest(self):
        decisions = [
            PolicyDecision(decision=DECISION_ALLOW),
            PolicyDecision(decision=DECISION_WARN),
        ]
        result = choose_strictest_decision(decisions)
        assert result.decision == DECISION_WARN

    def test_empty_list_returns_block(self):
        result = choose_strictest_decision([])
        assert result.decision == DECISION_BLOCK

    def test_same_priority(self):
        decisions = [
            PolicyDecision(decision=DECISION_ALLOW),
            PolicyDecision(decision=DECISION_ALLOW),
        ]
        result = choose_strictest_decision(decisions)
        assert result.decision == DECISION_ALLOW

    def test_invalid_policy_highest_priority(self):
        decisions = [
            PolicyDecision(decision=DECISION_ALLOW),
            PolicyDecision(decision=DECISION_INVALID_POLICY),
        ]
        result = choose_strictest_decision(decisions)
        assert result.decision == DECISION_INVALID_POLICY


class TestEvaluateToolRequest:
    def test_unknown_role(self):
        cap_policy = CapabilityPolicy(policy_id="cp-test")
        tool_policy = SpecToolPolicy(policy_id="tp-test")
        result = evaluate_tool_request(
            "NONEXISTENT", "read", EFFECT_READ,
            target=None,
            capability_policy=cap_policy,
            tool_policy=tool_policy,
        )
        assert result.decision == DECISION_UNKNOWN_ROLE
        assert "UNKNOWN" in result.reason

    def test_blocked_by_tool_policy(self):
        tool_policy = SpecToolPolicy(
            tools=[ToolEntry(tool_name="danger", blocked=True)],
        )
        cap_policy = CapabilityPolicy(policy_id="cp-test")
        result = evaluate_tool_request(
            ROLE_ORCHESTRATOR, "danger", EFFECT_READ,
            target=None,
            capability_policy=cap_policy,
            tool_policy=tool_policy,
        )
        assert result.decision == DECISION_BLOCK

    def test_allowed(self):
        cap_policy = CapabilityPolicy(
            policy_id="cp-1",
            default_decision=DECISION_ALLOW,
            roles=[ROLE_ORCHESTRATOR],
            capabilities=[
                CapabilityEntry(
                    capability_id="c1",
                    role=ROLE_ORCHESTRATOR,
                    tool_name="read",
                    allowed_effects=[EFFECT_READ],
                ),
            ],
        )
        tool_policy = SpecToolPolicy(
            tools=[ToolEntry(tool_name="read", allowlisted=True, blocked=False, requested_effects=[EFFECT_READ])],
        )
        result = evaluate_tool_request(
            ROLE_ORCHESTRATOR, "read", EFFECT_READ,
            target=None,
            capability_policy=cap_policy,
            tool_policy=tool_policy,
        )
        assert result.decision == DECISION_ALLOW

    def test_with_target(self):
        cap_policy = CapabilityPolicy(
            policy_id="cp-1",
            default_decision=DECISION_ALLOW,
            roles=[ROLE_ORCHESTRATOR],
            capabilities=[
                CapabilityEntry(
                    capability_id="c1",
                    role=ROLE_ORCHESTRATOR,
                    tool_name="read",
                    allowed_effects=[EFFECT_READ],
                ),
            ],
        )
        tool_policy = SpecToolPolicy(
            tools=[ToolEntry(tool_name="read", allowlisted=True, blocked=False, requested_effects=[EFFECT_READ])],
        )
        result = evaluate_tool_request(
            ROLE_ORCHESTRATOR, "read", EFFECT_READ,
            target="some/path.txt",
            capability_policy=cap_policy,
            tool_policy=tool_policy,
        )
        assert result.target == "some/path.txt"

    def test_requires_sandbox(self):
        cap_policy = CapabilityPolicy(
            policy_id="cp-1",
            default_decision=DECISION_ALLOW,
            roles=[ROLE_ORCHESTRATOR],
            capabilities=[
                CapabilityEntry(
                    capability_id="c1",
                    role=ROLE_ORCHESTRATOR,
                    tool_name="bash",
                    allowed_effects=[EFFECT_EXECUTE_COMMAND],
                ),
            ],
            sandbox_required_effects=[EFFECT_EXECUTE_COMMAND],
        )
        tool_policy = SpecToolPolicy(
            tools=[ToolEntry(tool_name="bash", allowlisted=True, blocked=False, requested_effects=[EFFECT_EXECUTE_COMMAND])],
        )
        result = evaluate_tool_request(
            ROLE_ORCHESTRATOR, "bash", EFFECT_EXECUTE_COMMAND,
            target=None,
            capability_policy=cap_policy,
            tool_policy=tool_policy,
        )
        assert result.decision == DECISION_NEEDS_SANDBOX_CHECK

    def test_requires_approval(self):
        cap_policy = CapabilityPolicy(
            policy_id="cp-1",
            default_decision=DECISION_ALLOW,
            roles=[ROLE_ORCHESTRATOR],
            capabilities=[
                CapabilityEntry(
                    capability_id="c1",
                    role=ROLE_ORCHESTRATOR,
                    tool_name="bash",
                    allowed_effects=[EFFECT_EXECUTE_COMMAND],
                ),
            ],
            approval_required_effects=[EFFECT_EXECUTE_COMMAND],
        )
        tool_policy = SpecToolPolicy(
            tools=[ToolEntry(tool_name="bash", allowlisted=True, blocked=False, requested_effects=[EFFECT_EXECUTE_COMMAND])],
        )
        result = evaluate_tool_request(
            ROLE_ORCHESTRATOR, "bash", EFFECT_EXECUTE_COMMAND,
            target=None,
            capability_policy=cap_policy,
            tool_policy=tool_policy,
        )
        assert result.decision == DECISION_NEEDS_APPROVAL

    def test_unknown_tool(self):
        cap_policy = CapabilityPolicy(policy_id="cp-1", default_decision=DECISION_ALLOW, roles=[ROLE_ORCHESTRATOR])
        tool_policy = SpecToolPolicy()
        result = evaluate_tool_request(
            ROLE_ORCHESTRATOR, "unknown_tool", EFFECT_READ,
            target=None,
            capability_policy=cap_policy,
            tool_policy=tool_policy,
        )
        assert result.decision in (DECISION_UNKNOWN_TOOL, DECISION_BLOCK)


class TestEvaluateModelRequest:
    def test_unknown_role(self):
        result = evaluate_model_request(
            "NONEXISTENT", "p1", "code_analysis",
            model_policy=ModelPolicy(policy_id="mp-test"),
            capability_policy=CapabilityPolicy(policy_id="cp-test"),
        )
        assert result.decision == DECISION_UNKNOWN_ROLE

    def test_unknown_profile(self):
        model_policy = ModelPolicy(policy_id="mp-1")
        result = evaluate_model_request(
            ROLE_ORCHESTRATOR, "p1", "code_analysis",
            model_policy=model_policy,
            capability_policy=CapabilityPolicy(policy_id="cp-test"),
        )
        assert result.decision == DECISION_UNKNOWN_MODEL

    def test_allowed(self):
        model_policy = ModelPolicy(
            policy_id="mp-1",
            model_profiles=[
                ModelProfile(
                    model_profile_id="p1",
                    allowed_task_types=["code_analysis"],
                ),
            ],
        )
        result = evaluate_model_request(
            ROLE_ORCHESTRATOR, "p1", "code_analysis",
            model_policy=model_policy,
            capability_policy=CapabilityPolicy(policy_id="cp-test"),
        )
        assert result.decision == DECISION_ALLOW

    def test_blocked_task(self):
        model_policy = ModelPolicy(
            policy_id="mp-1",
            model_profiles=[
                ModelProfile(
                    model_profile_id="p1",
                    allowed_task_types=["code_review"],
                    blocked_task_types=["code_generation"],
                ),
            ],
        )
        result = evaluate_model_request(
            ROLE_ORCHESTRATOR, "p1", "code_generation",
            model_policy=model_policy,
            capability_policy=CapabilityPolicy(policy_id="cp-test"),
        )
        assert result.decision == DECISION_BLOCK

    def test_requires_approval(self):
        model_policy = ModelPolicy(
            policy_id="mp-1",
            model_profiles=[
                ModelProfile(
                    model_profile_id="p1",
                    allowed_task_types=["code_analysis"],
                    requires_human_approval=True,
                ),
            ],
        )
        result = evaluate_model_request(
            ROLE_ORCHESTRATOR, "p1", "code_analysis",
            model_policy=model_policy,
            capability_policy=CapabilityPolicy(policy_id="cp-test"),
        )
        assert result.decision == DECISION_NEEDS_APPROVAL


class TestCheckRolePermissionDec:
    def test_allowed(self):
        cap_policy = CapabilityPolicy(
            policy_id="cp-1",
            default_decision=DECISION_ALLOW,
            roles=[ROLE_ORCHESTRATOR],
            capabilities=[
                CapabilityEntry(
                    capability_id="c1",
                    role=ROLE_ORCHESTRATOR,
                    tool_name="read",
                    allowed_effects=[EFFECT_READ],
                ),
            ],
        )
        result = check_role_permission_dec(ROLE_ORCHESTRATOR, "read", EFFECT_READ, cap_policy)
        assert result.decision == DECISION_ALLOW

    def test_unknown_role(self):
        result = check_role_permission_dec("FAKE", "read", EFFECT_READ, CapabilityPolicy(policy_id="cp-1"))
        assert "UNKNOWN" in result.decision
