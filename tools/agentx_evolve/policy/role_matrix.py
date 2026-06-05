from __future__ import annotations

from pathlib import Path
from typing import Any

from .policy_models import (
    ALL_ROLES,
    DECISION_ALLOW,
    DECISION_BLOCK,
    NON_OVERRIDABLE_BLOCKS,
    RolePermissionMatrix,
    new_id,
    utc_now_iso,
)


def build_default_role_permission_matrix(repo_root: Path) -> RolePermissionMatrix:
    """Build the default role permission matrix. Same as load_default_role_permission_matrix."""
    now = utc_now_iso()
    return RolePermissionMatrix(
        matrix_id=new_id("role-mat"),
        timestamp=now,
        roles=list(ALL_ROLES),
        matrix={role: {"default": DECISION_BLOCK} for role in ALL_ROLES},
        non_overridable_blocks=list(NON_OVERRIDABLE_BLOCKS),
    )


def role_exists(role: str, matrix: RolePermissionMatrix) -> bool:
    """Check if role exists in the matrix."""
    return role in matrix.roles or role in matrix.matrix


def get_role_permissions(role: str, matrix: RolePermissionMatrix) -> dict:
    """Get permissions dict for a role from the matrix."""
    return matrix.matrix.get(role, {})


def is_non_overridable_block(block_name: str, matrix: RolePermissionMatrix) -> bool:
    """Check if a block name is in the non_overridable_blocks list."""
    return block_name in matrix.non_overridable_blocks


# ── Backward compat wrappers ──────────────────────────────────────────────


def is_valid_role(role_name: str) -> bool:
    """Check if role name is a known role (backward compat)."""
    return role_name in ALL_ROLES


def check_role_permission(
    role_name: str,
    effect: str,
    matrix: RolePermissionMatrix | dict[str, Any] | None = None,
) -> bool:
    if not is_valid_role(role_name):
        return False
    if matrix is None:
        return False
    if isinstance(matrix, RolePermissionMatrix):
        role_rules = matrix.matrix.get(role_name, {})
    elif isinstance(matrix, dict):
        role_rules = matrix.get(role_name, {})
    else:
        return False
    default = role_rules.get("default", DECISION_BLOCK)
    if default == DECISION_BLOCK:
        allowed = role_rules.get("allowed_effects", [])
        return effect in allowed
    if default == DECISION_ALLOW:
        blocked = role_rules.get("blocked_effects", [])
        return effect not in blocked
    return False


def is_role_blocked(
    role_name: str,
    effect: str,
    matrix: RolePermissionMatrix | dict[str, Any] | None = None,
) -> bool:
    return not check_role_permission(role_name, effect, matrix)


def get_role_default_decision(
    role_name: str,
    matrix: RolePermissionMatrix | dict[str, Any] | None = None,
) -> str:
    if not is_valid_role(role_name):
        return DECISION_BLOCK
    if matrix is None:
        return DECISION_BLOCK
    if isinstance(matrix, RolePermissionMatrix):
        role_rules = matrix.matrix.get(role_name, {})
    elif isinstance(matrix, dict):
        role_rules = matrix.get(role_name, {})
    else:
        return DECISION_BLOCK
    return role_rules.get("default", DECISION_BLOCK)
