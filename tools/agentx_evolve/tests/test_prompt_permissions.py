import pytest
from agentx_evolve.prompts.prompt_permissions import check_prompt_permission, get_role_permissions, load_permission_matrix


class TestCheckPromptPermission:
    def test_read_action_allowed(self):
        assert check_prompt_permission("ORCHESTRATOR", "read", "prompt-1") is True

    def test_empty_role_not_allowed(self):
        assert check_prompt_permission("", "write", "prompt-1") is False


class TestGetRolePermissions:
    def test_empty_role(self):
        perms = get_role_permissions("")
        assert perms == []

    def test_invalid_role(self):
        perms = get_role_permissions("nonexistent_role")
        assert perms == []


class TestLoadPermissionMatrix:
    def test_default_matrix(self):
        matrix = load_permission_matrix()
        assert "roles" in matrix
        assert "default_permissions" in matrix
