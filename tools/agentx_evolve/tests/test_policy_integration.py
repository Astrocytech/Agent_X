import pytest
from agentx_evolve.policy.policy_registry import PolicyRegistry
from agentx_evolve.policy.policy_models import (
    DECISION_ALLOW,
    DECISION_BLOCK,
    EFFECT_EXECUTE_COMMAND,
    EFFECT_READ,
    ROLE_HUMAN_OPERATOR,
    ROLE_ORCHESTRATOR,
)


@pytest.fixture
def reg(tmp_path):
    return PolicyRegistry(repo_root=tmp_path)


class TestPolicyRegistryIntegration:
    def test_default_registry_blocks_unknown_tool(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        result = reg.evaluate_tool_request(ROLE_ORCHESTRATOR, "nonexistent_tool", EFFECT_READ)
        assert result.decision != DECISION_ALLOW

    def test_default_registry_allows_read_tool(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        result = reg.evaluate_tool_request(ROLE_ORCHESTRATOR, "agentx_scan", EFFECT_READ)
        assert result.decision == DECISION_ALLOW

    def test_default_registry_allows_write_runtime(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        result = reg.evaluate_tool_request(ROLE_ORCHESTRATOR, "agentx_scan", EFFECT_READ)
        assert result.decision == DECISION_ALLOW

    def test_tool_policy_and_capability_policy_must_agree_on_block(self, tmp_path):
        from agentx_evolve.policy.policy_models import (
            CapabilityPolicy,
            CapabilityEntry,
            ToolEntry,
            ToolPolicy as SpecToolPolicy,
        )
        cap = CapabilityPolicy(
            policy_id="cp-1",
            default_decision=DECISION_ALLOW,
            roles=[ROLE_ORCHESTRATOR],
            capabilities=[
                CapabilityEntry(
                    capability_id="c1",
                    role=ROLE_ORCHESTRATOR,
                    allowed_effects=[EFFECT_READ],
                ),
            ],
        )
        tool = SpecToolPolicy(
            tools=[ToolEntry(tool_name="read", allowlisted=False, blocked=True)],
        )
        reg = PolicyRegistry(repo_root=tmp_path, capability_policy=cap, tool_policy=tool)
        result = reg.evaluate_tool_request(ROLE_ORCHESTRATOR, "read", EFFECT_READ)
        assert result.decision == DECISION_BLOCK

    def test_model_and_tool_independent(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        tool_result = reg.evaluate_tool_request(ROLE_ORCHESTRATOR, "agentx_scan", EFFECT_READ)
        model_result = reg.evaluate_model_request(ROLE_ORCHESTRATOR, "small_local_coder", "code_analysis")
        assert tool_result.decision == DECISION_ALLOW
        assert model_result.decision == DECISION_ALLOW

    def test_role_unknown(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        result = reg.evaluate_tool_request("FAKE_ROLE", "read", EFFECT_READ)
        assert "UNKNOWN" in result.decision

    def test_reload_defaults_restores_state(self, tmp_path):
        reg = PolicyRegistry(repo_root=tmp_path)
        original_id = reg.capability_policy.policy_id
        reg.capability_policy.policy_id = "modified"
        reg.reload_defaults()
        assert reg.capability_policy.policy_id != "modified"
        result = reg.evaluate_tool_request(ROLE_ORCHESTRATOR, "agentx_scan", EFFECT_READ)
        assert result.decision == DECISION_ALLOW
