import pytest
from agentx_evolve.policy.policy_defaults import (
    load_default_capability_policy,
    load_default_model_policy,
    load_default_role_permission_matrix,
    load_default_role_matrix,
    load_default_tool_policy,
)
from agentx_evolve.policy.policy_models import (
    DECISION_BLOCK,
    ROLE_HUMAN_OPERATOR,
    ROLE_ORCHESTRATOR,
    TRUST_TIER_0_READ_ONLY,
)


class TestLoadDefaultCapabilityPolicy:
    def test_returns_policy(self):
        policy = load_default_capability_policy()
        assert policy.policy_id != ""
        assert policy.default_decision == DECISION_BLOCK
        assert len(policy.roles) >= 2
        assert ROLE_ORCHESTRATOR in policy.roles

    def test_has_capabilities(self):
        policy = load_default_capability_policy()
        assert len(policy.capabilities) >= 1

    def test_has_blocked_effects(self):
        policy = load_default_capability_policy()
        assert hasattr(policy, 'blocked_effects')


class TestLoadDefaultToolPolicy:
    def test_returns_policy(self):
        policy = load_default_tool_policy()
        assert policy.policy_id != ""
        assert len(policy.tools) >= 5

    def test_read_tool_allowlisted(self):
        policy = load_default_tool_policy()
        tools = [t for t in policy.tools if t.tool_name == "safe_read_file"]
        assert len(tools) == 1
        assert tools[0].allowlisted is True
        assert tools[0].trust_tier == TRUST_TIER_0_READ_ONLY

    def test_patch_apply_blocked(self):
        policy = load_default_tool_policy()
        tools = [t for t in policy.tools if t.tool_name == "patch_apply"]
        assert len(tools) == 1
        assert tools[0].blocked is True
        assert tools[0].requires_governance is True
        assert tools[0].requires_sandbox is True


class TestLoadDefaultModelPolicy:
    def test_returns_policy(self):
        policy = load_default_model_policy()
        assert policy.policy_id != ""
        assert policy.default_model_mode == "local_only"

    def test_has_profiles(self):
        policy = load_default_model_policy()
        assert len(policy.model_profiles) >= 1

    def test_read_only_profile(self):
        policy = load_default_model_policy()
        profiles = [p for p in policy.model_profiles if p.model_profile_id == "small_local_coder"]
        assert len(profiles) == 1
        assert profiles[0].may_read_source_context is True
        assert profiles[0].may_write_files is False


class TestLoadDefaultRoleMatrix:
    def test_returns_matrix(self):
        matrix = load_default_role_matrix()
        assert matrix.matrix_id != ""
        assert len(matrix.roles) >= 2

    def test_non_overridable_blocks(self):
        matrix = load_default_role_matrix()
        assert len(matrix.non_overridable_blocks) >= 1

    def test_long_name_alias(self):
        matrix = load_default_role_permission_matrix()
        assert matrix.matrix_id != ""
        assert len(matrix.roles) >= 2

    def test_accepts_repo_root(self, tmp_path):
        matrix = load_default_role_permission_matrix(repo_root=tmp_path)
        assert matrix.matrix_id != ""


class TestLoadDefaultFunctionsAcceptRepoRoot:
    def test_capability_policy(self, tmp_path):
        p = load_default_capability_policy(repo_root=tmp_path)
        assert p.policy_id != ""

    def test_tool_policy(self, tmp_path):
        p = load_default_tool_policy(repo_root=tmp_path)
        assert p.policy_id != ""

    def test_model_policy(self, tmp_path):
        p = load_default_model_policy(repo_root=tmp_path)
        assert p.policy_id != ""
