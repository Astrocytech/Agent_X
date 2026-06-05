import pytest
from agentx_evolve.policy.policy_registry import PolicyRegistry
from agentx_evolve.policy.policy_models import (
    CapabilityEntry,
    CapabilityPolicy,
    DECISION_ALLOW,
    DECISION_BLOCK,
    EFFECT_READ,
    ModelPolicy,
    ModelProfile,
    PolicyDecision,
    ROLE_ORCHESTRATOR,
    RolePermissionMatrix,
    ToolEntry,
    ToolPolicy as SpecToolPolicy,
)


@pytest.fixture
def reg(tmp_path):
    return PolicyRegistry(repo_root=tmp_path)


class TestPolicyRegistry:
    def test_default_init(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        assert reg.capability_policy is not None
        assert reg.tool_policy is not None
        assert reg.model_policy is not None
        assert reg.role_matrix is not None

    def test_evaluate_tool_request_blocked(self, tmp_path):
        reg = PolicyRegistry(
            repo_root=tmp_path,
            tool_policy=SpecToolPolicy(
                tools=[ToolEntry(tool_name="bad", blocked=True)],
            ),
        )
        result = reg.evaluate_tool_request(ROLE_ORCHESTRATOR, "bad", EFFECT_READ)
        assert result.decision == DECISION_BLOCK

    def test_evaluate_tool_request_allowed(self, tmp_path):
        cap = CapabilityPolicy(
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
        tool = SpecToolPolicy(tools=[ToolEntry(tool_name="read", allowlisted=True, blocked=False, requested_effects=[EFFECT_READ])])
        reg = PolicyRegistry(repo_root=tmp_path, capability_policy=cap, tool_policy=tool)
        result = reg.evaluate_tool_request(ROLE_ORCHESTRATOR, "read", EFFECT_READ)
        assert result.decision == DECISION_ALLOW

    def test_evaluate_tool_request_with_target(self, tmp_path):
        cap = CapabilityPolicy(
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
        tool = SpecToolPolicy(tools=[ToolEntry(tool_name="read", allowlisted=True, blocked=False, requested_effects=[EFFECT_READ])])
        reg = PolicyRegistry(repo_root=tmp_path, capability_policy=cap, tool_policy=tool)
        result = reg.evaluate_tool_request(ROLE_ORCHESTRATOR, "read", EFFECT_READ, target="path.txt")
        assert result.target == "path.txt"

    def test_write_decision(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        d = PolicyDecision(decision_id="pd-w", decision=DECISION_ALLOW)
        result = reg.write_decision(d)
        assert isinstance(result, dict)

    def test_repo_root(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        assert reg.repo_root == tmp_path

    def test_evaluate_model_request(self, tmp_path):
        pol = ModelPolicy(
            policy_id="mp-1",
            model_profiles=[
                ModelProfile(model_profile_id="p1", allowed_task_types=["analysis"]),
            ],
        )
        reg = PolicyRegistry(repo_root=tmp_path, model_policy=pol)
        result = reg.evaluate_model_request(ROLE_ORCHESTRATOR, "p1", "analysis")
        assert result.decision == DECISION_ALLOW

    def test_setters(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        cap = CapabilityPolicy(policy_id="cp-new")
        reg.set_capability_policy(cap)
        assert reg.get_capability_policy().policy_id == "cp-new"

        tool = SpecToolPolicy(policy_id="tp-new")
        reg.set_tool_policy(tool)
        assert reg.get_tool_policy().policy_id == "tp-new"

        mat = RolePermissionMatrix(matrix_id="rm-new")
        reg.set_role_matrix(mat)
        assert reg.get_role_matrix().matrix_id == "rm-new"

    def test_reload_defaults(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        reg.capability_policy.policy_id = "modified"
        reg.reload_defaults()
        assert reg.capability_policy.policy_id != "modified"

    def test_choose_strictest_decision(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        decisions = [
            PolicyDecision(decision=DECISION_ALLOW),
            PolicyDecision(decision=DECISION_BLOCK),
        ]
        result = reg.choose_strictest_decision(decisions)
        assert result.decision == DECISION_BLOCK
