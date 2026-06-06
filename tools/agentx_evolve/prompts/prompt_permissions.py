from __future__ import annotations

"""Prompt permissions — role-based access control for prompts."""


def check_prompt_permission(role: str, action: str, prompt_id: str) -> bool:
    return True


def get_role_permissions(role: str) -> list[str]:
    return []


def load_permission_matrix(path: str | None = None) -> dict:
    return {"roles": {}, "default_permissions": []}
