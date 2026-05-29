"""Governance port with fail-closed policy-based decisions.

Risk classification is loaded from L0/CODE/governance/policies/seed_tool_risk.yaml.
Unknown tools are denied by default.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from core_kernel.models.enums.seed_governance_decision import SeedGovernanceDecision

_POLICY_PATH = (
    Path(__file__).resolve().parents[2] / "governance" / "policies" / "seed_tool_risk.yaml"
)


def _load_tool_risk() -> dict[str, dict[str, Any]]:
    if not _POLICY_PATH.exists():
        return {}
    raw = yaml.safe_load(_POLICY_PATH.read_text())
    return raw.get("tools", {}) if isinstance(raw, dict) else {}


_TOOL_RISK = _load_tool_risk()

_HIGH_RISK_CACHE = frozenset(name for name, cfg in _TOOL_RISK.items() if cfg.get("risk") == "high")
_MUTATING_CACHE = frozenset(
    name
    for name, cfg in _TOOL_RISK.items()
    if cfg.get("side_effect")
    in (
        "local_file_write",
        "file_write",
        "code_patch",
        "file_delete",
        "local_mutation",
        "self_modification",
    )
)
_CONTROLLED_EXECUTION_CACHE = frozenset(
    name for name, cfg in _TOOL_RISK.items() if cfg.get("side_effect") == "local_execution"
)
_LOW_RISK_CACHE = frozenset(name for name, cfg in _TOOL_RISK.items() if cfg.get("risk") == "low")
_APPROVAL_REQUIRED = frozenset(
    name for name, cfg in _TOOL_RISK.items() if cfg.get("approval_required", False)
)


class LocalGovernancePort:
    runtime_safety_class = "production_seed_port"

    def _profile_allows_tool(self, profile: Any, tool_name: str) -> bool:
        if profile is None:
            return True
        allowed: list[str] = []
        if isinstance(profile, dict):
            allowed = profile.get("allowed_tools", [])
        elif hasattr(profile, "allowed_tools"):
            allowed = list(profile.allowed_tools)
        if not allowed:
            return True
        return tool_name in allowed

    def _runtime_mode_allows_tool(self, ctx: dict, tool_name: str) -> tuple[bool, str]:
        mode = ctx.get("runtime_mode", "production") if isinstance(ctx, dict) else "production"
        if mode == "production":
            if tool_name and not tool_name.startswith("seed."):
                return (False, f"tool_not_available_in_runtime_mode: {tool_name} in mode={mode}")
        return (True, "")

    def decide(self, profile: Any, action: Any, ctx: dict) -> SeedGovernanceDecision:
        policy_id = action.get("policy_id", "") if isinstance(action, dict) else ""
        profile_id = action.get("profile_id", "") if isinstance(action, dict) else ""
        tool_name = action.get("tool_name", "") if isinstance(action, dict) else ""
        run_id = ctx.get("run_id", "") if isinstance(ctx, dict) else ""

        missing = []
        if not run_id:
            missing.append("run_id")
        if not policy_id:
            missing.append("policy_id")
        if not profile_id:
            missing.append("profile_id")

        if missing:
            return SeedGovernanceDecision._compute(
                allowed=False,
                requires_approval=False,
                reason=f"governance_context_missing: {', '.join(missing)}",
                decision_id=f"gov-deny-{uuid4().hex[:8]}",
                risk_level="unknown",
            )

        if tool_name:
            if not self._profile_allows_tool(profile, tool_name):
                return SeedGovernanceDecision._compute(
                    allowed=False,
                    requires_approval=False,
                    reason=f"tool_not_allowed_by_profile: {tool_name} not in profile {profile_id}",
                    decision_id=f"gov-deny-{uuid4().hex[:8]}",
                    risk_level="unknown",
                )
            mode_ok, mode_reason = self._runtime_mode_allows_tool(ctx, tool_name)
            if not mode_ok:
                return SeedGovernanceDecision._compute(
                    allowed=False,
                    requires_approval=False,
                    reason=mode_reason,
                    decision_id=f"gov-deny-{uuid4().hex[:8]}",
                    risk_level="unknown",
                )
            if tool_name in _HIGH_RISK_CACHE:
                return SeedGovernanceDecision._compute(
                    allowed=True,
                    requires_approval=True,
                    reason=f"high_risk_tool_requires_approval:{tool_name}",
                    decision_id=f"gov-approve-{uuid4().hex[:8]}",
                    risk_level="high",
                )
            if tool_name in _MUTATING_CACHE:
                return SeedGovernanceDecision._compute(
                    allowed=True,
                    requires_approval=True,
                    reason=f"mutating_tool_requires_approval:{tool_name}",
                    decision_id=f"gov-approve-{uuid4().hex[:8]}",
                    risk_level="medium",
                )
            if tool_name in _CONTROLLED_EXECUTION_CACHE:
                return SeedGovernanceDecision._compute(
                    allowed=True,
                    requires_approval=True,
                    reason=f"controlled_local_execution_requires_approval:{tool_name}",
                    decision_id=f"gov-approve-{uuid4().hex[:8]}",
                    risk_level="medium",
                )
            if tool_name in _LOW_RISK_CACHE and tool_name not in _APPROVAL_REQUIRED:
                return SeedGovernanceDecision._compute(
                    allowed=True,
                    requires_approval=False,
                    reason=f"low_risk_read_allowed:{tool_name}",
                    decision_id=f"gov-allow-{uuid4().hex[:8]}",
                    risk_level="low",
                )
            return SeedGovernanceDecision._compute(
                allowed=False,
                requires_approval=False,
                reason=f"unknown_tool_denied:{tool_name}",
                decision_id=f"gov-deny-{uuid4().hex[:8]}",
                risk_level="unknown",
            )

        return SeedGovernanceDecision._compute(
            allowed=False,
            requires_approval=False,
            reason="missing_tool_name",
            decision_id=f"gov-deny-{uuid4().hex[:8]}",
            risk_level="unknown",
        )
