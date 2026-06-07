from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.policy.role_matrix import is_valid_role
from agentx_evolve.policy.policy_defaults import load_default_role_permission_matrix
from agentx_evolve.policy.policy_models import DECISION_ALLOW, DECISION_BLOCK

_READ_ACTIONS = {"read", "view", "list", "get", "validate"}
_WRITE_ACTIONS = {"write", "create", "update", "delete", "bind", "unbind"}
_EXECUTE_ACTIONS = {"execute", "diff", "migrate", "rollback"}


def check_prompt_permission(role: str, action: str, prompt_id: str) -> bool:
    if not is_valid_role(role):
        return False
    if action in _READ_ACTIONS:
        return True
    if action in (_WRITE_ACTIONS | _EXECUTE_ACTIONS):
        matrix = load_default_role_permission_matrix()
        if matrix:
            role_rules = matrix.matrix.get(role, {})
            default = role_rules.get("default", DECISION_BLOCK)
            if default == DECISION_ALLOW:
                return action not in role_rules.get("blocked_effects", [])
        return False
    return False


def get_role_permissions(role: str) -> list[str]:
    if not is_valid_role(role):
        return []
    matrix = load_default_role_permission_matrix()
    if not matrix:
        return list(_READ_ACTIONS)
    role_rules = matrix.matrix.get(role, {})
    default = role_rules.get("default", DECISION_BLOCK)
    if default == DECISION_ALLOW:
        allowed = list(_READ_ACTIONS | _WRITE_ACTIONS | _EXECUTE_ACTIONS)
        blocked = role_rules.get("blocked_effects", [])
        return [a for a in allowed if a not in blocked]
    allowed_effects = role_rules.get("allowed_effects", [])
    result = list(_READ_ACTIONS)
    for e in allowed_effects:
        if e in _WRITE_ACTIONS:
            result.append(e)
        elif e in _EXECUTE_ACTIONS:
            result.append(e)
    return result


def load_permission_matrix(path: str | None = None) -> dict[str, Any]:
    if path:
        p = Path(path)
        if p.exists():
            import json
            try:
                return json.loads(p.read_text())
            except (json.JSONDecodeError, OSError):
                pass
    matrix = load_default_role_permission_matrix()
    if matrix:
        permissions = {}
        for role in matrix.roles:
            role_rules = matrix.matrix.get(role, {})
            default = role_rules.get("default", DECISION_BLOCK)
            if default == DECISION_BLOCK:
                permissions[role] = list(_READ_ACTIONS)
            else:
                blocked = role_rules.get("blocked_effects", [])
                all_actions = list(_READ_ACTIONS | _WRITE_ACTIONS | _EXECUTE_ACTIONS)
                permissions[role] = [a for a in all_actions if a not in blocked]
        return {"roles": permissions, "default_permissions": list(_READ_ACTIONS)}
    return {"roles": {}, "default_permissions": list(_READ_ACTIONS)}
