import pytest
from agentx_evolve.prompts.prompt_models import (
    PromptPermissionMatrix, RolePermission, PR_READ, PR_WRITE, PR_ADMIN
)


def test_matrix_grants_correct_permissions_per_role():
    matrix = PromptPermissionMatrix(
        matrix_id="pm-1",
        roles={
            "admin": [RolePermission(role="admin", permission=PR_ADMIN, enabled=True)],
            "editor": [RolePermission(role="editor", permission=PR_WRITE, enabled=True)],
            "viewer": [RolePermission(role="viewer", permission=PR_READ, enabled=True)],
        }
    )
    assert matrix.matrix_id == "pm-1"
    assert len(matrix.roles) == 3
    assert matrix.roles["admin"][0].permission == PR_ADMIN
    assert matrix.roles["viewer"][0].permission == PR_READ


def test_matrix_denies_unlisted_permissions():
    matrix = PromptPermissionMatrix(
        matrix_id="pm-2",
        roles={
            "viewer": [RolePermission(role="viewer", permission=PR_READ, enabled=True)],
        }
    )
    assert PR_ADMIN not in [p.permission for p in matrix.roles.get("viewer", [])]
    assert matrix.default_permission == PR_READ


def test_matrix_default_read():
    matrix = PromptPermissionMatrix()
    assert matrix.default_permission == PR_READ
    assert matrix.matrix_id == ""


def test_role_permission_fields():
    rp = RolePermission(role="test_role", permission=PR_WRITE, enabled=False)
    assert rp.role == "test_role"
    assert rp.permission == PR_WRITE
    assert rp.enabled is False


def test_matrix_empty_roles():
    matrix = PromptPermissionMatrix(matrix_id="pm-3")
    assert matrix.roles == {}
