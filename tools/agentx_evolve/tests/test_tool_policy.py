import pytest
from agentx_evolve.policy.tool_policy import (
    find_tool,
    tool_allows_effect,
    tool_executes_command,
    tool_exists,
    tool_is_blocked,
    tool_requires_governance,
    tool_requires_human_approval,
    tool_requires_sandbox,
    tool_uses_network,
    tool_writes_source,
)
from agentx_evolve.policy.policy_models import (
    ToolEntry,
    ToolPolicy as SpecToolPolicy,
    TRUST_TIER_0_READ_ONLY,
    TRUST_TIER_3_VALIDATION_EXECUTION,
    TRUST_TIER_6_BLOCKED,
)


@pytest.fixture
def sample_policy():
    return SpecToolPolicy(
        policy_id="tp-1",
        tools=[
            ToolEntry(tool_name="read", trust_tier=TRUST_TIER_0_READ_ONLY, allowlisted=True, blocked=False),
            ToolEntry(
                tool_name="bash",
                trust_tier=TRUST_TIER_3_VALIDATION_EXECUTION,
                blocked=False,
                requires_sandbox=True,
                requires_human_approval=True,
                executes_command=True,
            ),
            ToolEntry(tool_name="danger", blocked=True),
        ],
    )


class TestFindTool:
    def test_found(self, sample_policy):
        entry = find_tool("read", sample_policy)
        assert entry is not None
        assert entry.tool_name == "read"

    def test_not_found(self, sample_policy):
        entry = find_tool("nonexistent", sample_policy)
        assert entry is None


class TestToolIsBlocked:
    def test_blocked(self, sample_policy):
        assert tool_is_blocked("danger", sample_policy) is True

    def test_not_blocked(self, sample_policy):
        assert tool_is_blocked("read", sample_policy) is False

    def test_not_found(self, sample_policy):
        assert tool_is_blocked("unknown", sample_policy) is True


class TestToolExists:
    def test_exists(self, sample_policy):
        assert tool_exists("read", sample_policy) is True

    def test_not_exists(self, sample_policy):
        assert tool_exists("nonexistent", sample_policy) is False


class TestRequiresFunctions:
    def test_requires_sandbox(self, sample_policy):
        assert tool_requires_sandbox("bash", sample_policy) is True
        assert tool_requires_sandbox("read", sample_policy) is False

    def test_requires_approval(self, sample_policy):
        assert tool_requires_human_approval("bash", sample_policy) is True
        assert tool_requires_human_approval("read", sample_policy) is False

    def test_requires_governance(self, sample_policy):
        assert tool_requires_governance("read", sample_policy) is False


class TestNewToolFunctions:
    def test_tool_allows_effect(self, sample_policy):
        assert tool_allows_effect("read", "read", sample_policy) is False

    def test_tool_uses_network(self, sample_policy):
        assert tool_uses_network("read", sample_policy) is False
        assert tool_uses_network("bash", sample_policy) is False

    def test_tool_executes_command(self, sample_policy):
        assert tool_executes_command("bash", sample_policy) is True
        assert tool_executes_command("read", sample_policy) is False

    def test_tool_writes_source(self, sample_policy):
        assert tool_writes_source("read", sample_policy) is False
