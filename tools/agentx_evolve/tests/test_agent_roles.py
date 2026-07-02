from __future__ import annotations

from agentx_evolve.agents.base_agent import MvpBaseAgent
from agentx_evolve.agents.agent_roles import (
    MvpAgentRole,
    MvpRoleRegistry,
    ROLE_PLANNER,
    ROLE_EXECUTOR,
    ROLE_VALIDATOR,
    ROLE_REVIEWER,
    ROLE_PROMOTION,
    ROLE_OBSERVER,
    ROLE_ADVERSARY,
)


class TestMvpBaseAgent:
    def test_base_agent_creation(self) -> None:
        agent = MvpBaseAgent("agent-1", ROLE_EXECUTOR, ["write_code", "run_tests"])
        assert agent.agent_id == "agent-1"
        assert agent.role == ROLE_EXECUTOR
        assert agent.capabilities == ["write_code", "run_tests"]

    def test_base_agent_can_perform(self) -> None:
        agent = MvpBaseAgent("agent-2", ROLE_PLANNER, ["generate_plan", "assign_tasks"])
        assert agent.can_perform("generate_plan") is True
        assert agent.can_perform("write_code") is False

    def test_base_agent_repr(self) -> None:
        agent = MvpBaseAgent("agent-3", ROLE_VALIDATOR, ["run_tests"])
        expected = "MvpBaseAgent(agent_id='agent-3', role='validator', capabilities=['run_tests'])"
        assert repr(agent) == expected


class TestMvpRoleRegistry:
    def test_role_registry_get_role(self) -> None:
        registry = MvpRoleRegistry()
        role = registry.get_role(ROLE_PLANNER)
        assert role is not None
        assert role.role_id == ROLE_PLANNER
        assert "generate_plan" in role.allowed_actions
        assert "execute_plan" in role.forbidden_actions

    def test_role_registry_get_role_unknown(self) -> None:
        registry = MvpRoleRegistry()
        assert registry.get_role("unknown_role") is None

    def test_role_allowed_action(self) -> None:
        registry = MvpRoleRegistry()
        assert registry.is_action_allowed(ROLE_EXECUTOR, "write_code") is True
        assert registry.is_action_allowed(ROLE_EXECUTOR, "generate_plan") is False

    def test_role_forbidden_action(self) -> None:
        registry = MvpRoleRegistry()
        assert registry.is_action_forbidden(ROLE_PLANNER, "execute_plan") is True
        assert registry.is_action_forbidden(ROLE_PLANNER, "generate_plan") is False

    def test_role_action_unknown_role(self) -> None:
        registry = MvpRoleRegistry()
        assert registry.is_action_allowed("ghost", "anything") is False
        assert registry.is_action_forbidden("ghost", "anything") is False

    def test_separation_of_duties_passes(self) -> None:
        registry = MvpRoleRegistry()
        assert registry.validate_separation(ROLE_EXECUTOR, ROLE_REVIEWER) is True

    def test_separation_of_duties_fails_same_role(self) -> None:
        registry = MvpRoleRegistry()
        assert registry.validate_separation(ROLE_EXECUTOR, ROLE_EXECUTOR) is False

    def test_separation_of_duties_all_combinations(self) -> None:
        registry = MvpRoleRegistry()
        roles = [ROLE_PLANNER, ROLE_EXECUTOR, ROLE_VALIDATOR, ROLE_REVIEWER, ROLE_PROMOTION]
        for r1 in roles:
            for r2 in roles:
                if r1 != r2:
                    assert registry.validate_separation(r1, r2) is True

    def test_all_roles_have_descriptions(self) -> None:
        registry = MvpRoleRegistry()
        all_roles = [ROLE_PLANNER, ROLE_EXECUTOR, ROLE_VALIDATOR, ROLE_REVIEWER, ROLE_PROMOTION, ROLE_OBSERVER, ROLE_ADVERSARY]
        for role_id in all_roles:
            role = registry.get_role(role_id)
            assert role is not None
            assert len(role.description) > 0

    def test_all_roles_have_allowed_actions(self) -> None:
        registry = MvpRoleRegistry()
        all_roles = [ROLE_PLANNER, ROLE_EXECUTOR, ROLE_VALIDATOR, ROLE_REVIEWER, ROLE_PROMOTION, ROLE_OBSERVER, ROLE_ADVERSARY]
        for role_id in all_roles:
            role = registry.get_role(role_id)
            assert role is not None
            assert len(role.allowed_actions) > 0

    def test_all_roles_have_forbidden_actions(self) -> None:
        registry = MvpRoleRegistry()
        all_roles = [ROLE_PLANNER, ROLE_EXECUTOR, ROLE_VALIDATOR, ROLE_REVIEWER, ROLE_PROMOTION, ROLE_OBSERVER, ROLE_ADVERSARY]
        for role_id in all_roles:
            role = registry.get_role(role_id)
            assert role is not None
            assert len(role.forbidden_actions) > 0

    def test_default_separation_rules_enforced(self) -> None:
        registry = MvpRoleRegistry()
        planner = registry.get_role(ROLE_PLANNER)
        executor = registry.get_role(ROLE_EXECUTOR)
        validator = registry.get_role(ROLE_VALIDATOR)
        reviewer = registry.get_role(ROLE_REVIEWER)
        promotion = registry.get_role(ROLE_PROMOTION)

        assert planner is not None
        assert executor is not None
        assert validator is not None
        assert reviewer is not None
        assert promotion is not None

        # Planner cannot execute
        assert "execute_plan" in planner.forbidden_actions

        # Executor cannot validate its own action
        assert "validate_own_action" in executor.forbidden_actions

        # Validator cannot promote
        assert "promote_artifact" in validator.forbidden_actions

        # Reviewer cannot alter evidence
        assert "alter_evidence" in reviewer.forbidden_actions

        # Promotion agent cannot generate source
        assert "generate_source" in promotion.forbidden_actions
