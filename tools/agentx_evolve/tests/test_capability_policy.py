import pytest
from agentx_evolve.policy.capability_policy import (
    capability_requires_approval,
    capability_requires_governance,
    capability_requires_sandbox,
    find_capability,
    is_effect_allowed,
    is_effect_blocked,
)
from agentx_evolve.policy.policy_models import (
    CapabilityEntry,
    CapabilityPolicy,
    DECISION_ALLOW,
    DECISION_BLOCK,
    EFFECT_EXECUTE_COMMAND,
    EFFECT_READ,
    EFFECT_WRITE_SOURCE,
    ROLE_HUMAN_OPERATOR,
    ROLE_ORCHESTRATOR,
    new_id,
    utc_now_iso,
)


@pytest.fixture
def sample_policy():
    return CapabilityPolicy(
        policy_id=new_id("cp"),
        timestamp=utc_now_iso(),
        roles=[ROLE_ORCHESTRATOR, ROLE_HUMAN_OPERATOR],
        default_decision=DECISION_BLOCK,
        capabilities=[
            CapabilityEntry(
                capability_id="cap-1",
                role=ROLE_ORCHESTRATOR,
                tool_name="read_tool",
                allowed_effects=[EFFECT_READ],
                blocked_effects=[],
            ),
            CapabilityEntry(
                capability_id="cap-2",
                role=ROLE_HUMAN_OPERATOR,
                allowed_effects=[EFFECT_READ, EFFECT_EXECUTE_COMMAND],
                blocked_effects=[EFFECT_WRITE_SOURCE],
            ),
        ],
        blocked_effects=[EFFECT_WRITE_SOURCE],
        approval_required_effects=[EFFECT_EXECUTE_COMMAND],
        governance_required_effects=[EFFECT_WRITE_SOURCE],
        sandbox_required_effects=[EFFECT_EXECUTE_COMMAND],
    )


class TestFindCapability:
    def test_finds_by_role_and_tool(self, sample_policy):
        cap = find_capability(ROLE_ORCHESTRATOR, "read_tool", sample_policy)
        assert cap is not None
        assert cap.capability_id == "cap-1"

    def test_no_match(self, sample_policy):
        cap = find_capability("UNKNOWN_ROLE", "read_tool", sample_policy)
        assert cap is None

    def test_finds_human_operator(self, sample_policy):
        cap = find_capability(ROLE_HUMAN_OPERATOR, "", sample_policy)
        assert cap is not None
        assert cap.capability_id == "cap-2"


class TestIsEffectAllowed:
    def test_globally_blocked(self, sample_policy):
        cap = find_capability(ROLE_ORCHESTRATOR, "read_tool", sample_policy)
        assert is_effect_allowed(EFFECT_WRITE_SOURCE, cap, sample_policy) is False

    def test_allowed_for_role(self, sample_policy):
        cap = find_capability(ROLE_ORCHESTRATOR, "read_tool", sample_policy)
        assert is_effect_allowed(EFFECT_READ, cap, sample_policy) is True

    def test_blocked_for_role(self, sample_policy):
        cap = find_capability(ROLE_HUMAN_OPERATOR, "", sample_policy)
        assert is_effect_allowed(EFFECT_WRITE_SOURCE, cap, sample_policy) is False

    def test_unknown_role_uses_default(self, sample_policy):
        assert is_effect_allowed(EFFECT_READ, None, sample_policy) is False


class TestRequiresFunctions:
    def test_requires_approval(self, sample_policy):
        assert capability_requires_approval(EFFECT_EXECUTE_COMMAND, None, sample_policy) is True
        assert capability_requires_approval(EFFECT_READ, None, sample_policy) is False

    def test_requires_governance(self, sample_policy):
        assert capability_requires_governance(EFFECT_WRITE_SOURCE, None, sample_policy) is True

    def test_requires_sandbox(self, sample_policy):
        assert capability_requires_sandbox(EFFECT_EXECUTE_COMMAND, None, sample_policy) is True
