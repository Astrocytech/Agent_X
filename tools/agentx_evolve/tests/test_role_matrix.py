import pytest
from agentx_evolve.policy.role_matrix import (
    check_role_permission,
    get_role_default_decision,
    get_role_permissions,
    is_non_overridable_block,
    is_valid_role,
    role_exists,
)
from agentx_evolve.policy.policy_models import (
    DECISION_ALLOW,
    DECISION_BLOCK,
    EFFECT_READ,
    EFFECT_EXECUTE_COMMAND,
    ROLE_HUMAN_OPERATOR,
    ROLE_ORCHESTRATOR,
    RolePermissionMatrix,
)


@pytest.fixture
def sample_matrix():
    return RolePermissionMatrix(
        roles=[ROLE_ORCHESTRATOR, ROLE_HUMAN_OPERATOR],
        matrix={
            ROLE_ORCHESTRATOR: {"default": DECISION_ALLOW, "blocked_effects": []},
            ROLE_HUMAN_OPERATOR: {"default": DECISION_BLOCK, "allowed_effects": [EFFECT_READ]},
        },
        non_overridable_blocks=["L0_MUTATION_BLOCK"],
    )


class TestRoleExists:
    def test_valid_role(self, sample_matrix):
        assert role_exists(ROLE_ORCHESTRATOR, sample_matrix) is True

    def test_invalid_role(self, sample_matrix):
        assert role_exists("NONEXISTENT", sample_matrix) is False


class TestIsValidRole:
    def test_valid(self):
        assert is_valid_role(ROLE_HUMAN_OPERATOR) is True

    def test_invalid(self):
        assert is_valid_role("FAKE") is False


class TestCheckRolePermission:
    def test_unknown_role_returns_false(self):
        assert check_role_permission("FAKE", EFFECT_READ) is False

    def test_none_matrix_returns_false(self):
        assert check_role_permission(ROLE_ORCHESTRATOR, EFFECT_READ, None) is False

    def test_allowed_in_dict_matrix(self):
        matrix = {
            ROLE_ORCHESTRATOR: {"default": DECISION_ALLOW, "blocked_effects": [EFFECT_EXECUTE_COMMAND]}
        }
        assert check_role_permission(ROLE_ORCHESTRATOR, EFFECT_READ, matrix) is True

    def test_blocked_in_dict_matrix(self):
        matrix = {
            ROLE_ORCHESTRATOR: {"default": DECISION_BLOCK, "allowed_effects": [EFFECT_READ]}
        }
        assert check_role_permission(ROLE_ORCHESTRATOR, EFFECT_EXECUTE_COMMAND, matrix) is False

    def test_allowed_in_role_matrix_obj(self):
        mat = RolePermissionMatrix(
            roles=[ROLE_ORCHESTRATOR],
            matrix={ROLE_ORCHESTRATOR: {"default": DECISION_ALLOW, "blocked_effects": []}},
        )
        assert check_role_permission(ROLE_ORCHESTRATOR, EFFECT_READ, mat) is True


class TestIsRoleBlocked:
    def test_blocked(self):
        from agentx_evolve.policy.role_matrix import is_role_blocked
        matrix = {ROLE_ORCHESTRATOR: {"default": DECISION_BLOCK, "allowed_effects": []}}
        assert is_role_blocked(ROLE_ORCHESTRATOR, EFFECT_READ, matrix) is True


class TestIsNonOverridableBlock:
    def test_known_block(self, sample_matrix):
        assert is_non_overridable_block("L0_MUTATION_BLOCK", sample_matrix) is True

    def test_unknown_block(self, sample_matrix):
        assert is_non_overridable_block("SOME_OTHER", sample_matrix) is False


class TestGetRoleDefaultDecision:
    def test_unknown_role(self):
        assert get_role_default_decision("FAKE") == DECISION_BLOCK

    def test_from_dict(self):
        matrix = {ROLE_ORCHESTRATOR: {"default": DECISION_ALLOW}}
        assert get_role_default_decision(ROLE_ORCHESTRATOR, matrix) == DECISION_ALLOW


class TestGetRolePermissions:
    def test_known_role(self, sample_matrix):
        perms = get_role_permissions(ROLE_ORCHESTRATOR, sample_matrix)
        assert perms is not None
        assert perms.get("default") == DECISION_ALLOW

    def test_unknown_role(self, sample_matrix):
        result = get_role_permissions("UNKNOWN", sample_matrix)
        assert result == {}
