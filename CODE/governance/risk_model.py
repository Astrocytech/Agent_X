"""GovernanceRisk — Structured risk assessment for candidate moves.

Provides a richer risk model than simple allow/deny/approval, tracking:
- irreversibility
- protected file impact
- seed boundary impact
- public API impact
- dependency impact
- rollback availability
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GovernanceRisk:
    risk_id: str
    action_type: str
    target_files: list[str]
    protected_files_touched: list[str]
    irreversible: bool
    external_side_effects: bool
    seed_boundary_impact: str
    public_api_impact: str
    dependency_impact: bool
    rollback_available: bool
    requires_user_approval: bool
    reason: str


_PROTECTED_PATHS: set[str] = {
    "SEED_PACKAGE_MANIFEST.yaml",
    "CAPABILITY_MANIFEST.yaml",
    "CODE/core_kernel/contracts",
    "CODE/core_kernel/public",
    "CODE/core_kernel/runtime/seed_runtime.py",
    "CODE/tool_gateway/seed_tool_registry.py",
}

_IRREVERSIBLE_ACTIONS: set[str] = {
    "delete_file",
    "overwrite_authority",
    "modify_contract",
    "change_policy",
    "modify_runtime",
    "delete_directory",
}

_DEPENDENCY_IMPACT_ACTIONS: set[str] = {
    "modify_pyproject_toml",
    "modify_requirements_txt",
    "modify_lock_file",
    "add_dependency",
    "remove_dependency",
}


def assess_risk(
    action_type: str,
    target_files: list[str] | None = None,
    tool_name: str = "",
    arguments: dict[str, Any] | None = None,
) -> GovernanceRisk:
    import uuid

    target_files = target_files or []
    arguments = arguments or {}

    protected_touched = [f for f in target_files if _is_protected(f)]
    irreversible = action_type in _IRREVERSIBLE_ACTIONS
    dependency_impact = action_type in _DEPENDENCY_IMPACT_ACTIONS
    seed_boundary = _assess_seed_boundary_impact(target_files)
    public_api = _assess_public_api_impact(target_files)

    return GovernanceRisk(
        risk_id=uuid.uuid4().hex[:12],
        action_type=action_type,
        target_files=target_files,
        protected_files_touched=protected_touched,
        irreversible=irreversible,
        external_side_effects=not irreversible,
        seed_boundary_impact=seed_boundary,
        public_api_impact=public_api,
        dependency_impact=dependency_impact,
        rollback_available=not irreversible,
        requires_user_approval=bool(protected_touched) or irreversible or dependency_impact,
        reason=_build_reason(action_type, protected_touched, irreversible, dependency_impact),
    )


def _is_protected(path: str) -> bool:
    for p in _PROTECTED_PATHS:
        if path == p or path.startswith(p):
            return True
    return False


def _assess_seed_boundary_impact(target_files: list[str]) -> str:
    for f in target_files:
        if "SEED_BOUNDARY" in f or "seed_boundary" in f or "seed_runtime" in f:
            return "high"
        if "SEED_POLICY" in f or "authority" in f.lower():
            return "high"
        if f.startswith("CODE/core_kernel/contracts"):
            return "medium"
    return "low"


def _assess_public_api_impact(target_files: list[str]) -> str:
    for f in target_files:
        if "PUBLIC_API" in f or "kernel_service" in f or "kernel_contracts" in f:
            return "high"
    return "low"


def _build_reason(
    action_type: str,
    protected_touched: list[str],
    irreversible: bool,
    dependency_impact: bool,
) -> str:
    parts: list[str] = []
    if protected_touched:
        parts.append(f"touches protected files: {', '.join(protected_touched)}")
    if irreversible:
        parts.append("irreversible action")
    if dependency_impact:
        parts.append("modifies dependencies")
    if not parts:
        parts.append("standard action")
    return "; ".join(parts)
