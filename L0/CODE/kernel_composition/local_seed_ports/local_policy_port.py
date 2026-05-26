"""LocalPolicyPort — L0 seed policy port that extracts policy decisions from profiles."""

from __future__ import annotations

from typing import Any

from core_kernel.models.kernel_atoms import PolicyDecision


def _get_profile_attr(profile: Any, key: str, default: Any = None) -> Any:
    if isinstance(profile, dict):
        return profile.get(key, default)
    return getattr(profile, key, default)


class LocalPolicyPort:
    runtime_safety_class = "production_seed_port"

    def __init__(self):
        self._risk_policy = self._load_risk_policy()

    def _load_risk_policy(self):
        import yaml
        from pathlib import Path

        path = (
            Path(__file__).resolve().parents[3]
            / "CODE"
            / "governance"
            / "policies"
            / "seed_tool_risk.yaml"
        )
        return yaml.safe_load(path.read_text()) if path.exists() else {}

    def compute(self, profile, task) -> PolicyDecision:
        allowed = _get_profile_attr(profile, "allowed_tools", []) or []
        forbidden = _get_profile_attr(profile, "forbidden_tools", []) or []
        max_risk = _get_profile_attr(profile, "max_risk_level", "high") or "high"
        profile_id = _get_profile_attr(profile, "id", "unknown")

        if not allowed and not forbidden:
            allowed = list(self._risk_policy.get("tools", {}).keys())

        import hashlib

        policy_id = (
            f"policy-{profile_id}-{hashlib.md5(str(sorted(allowed)).encode()).hexdigest()[:8]}"
        )

        approval_required = {}
        for tool_name, tool_info in self._risk_policy.get("tools", {}).items():
            if tool_info.get("risk_level") in ("high", "critical"):
                approval_required[tool_name] = True

        return PolicyDecision(
            target_id=policy_id,
            allowed=True,
            requires_human_approval=False,
            risk_level=max_risk,
            metadata={
                "allowed_tool_classes": allowed,
                "forbidden_tool_classes": forbidden,
                "max_risk_level": max_risk,
                "approval_required": approval_required,
            },
        )
