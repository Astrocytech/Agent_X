from __future__ import annotations

from pathlib import Path

from .policy_decision import (
    choose_strictest_decision as _choose_strictest_decision,
    evaluate_tool_request as _evaluate_tool_request,
    evaluate_model_request as _evaluate_model_request,
)
from .policy_defaults import (
    load_default_capability_policy,
    load_default_tool_policy,
    load_default_model_policy,
    load_default_role_permission_matrix,
)
from .policy_evidence import write_latest_policy_decision as _write_latest
from .policy_models import (
    CapabilityPolicy,
    ModelPolicy,
    PolicyDecision,
    RolePermissionMatrix,
    ToolPolicy,
)


class PolicyRegistry:
    def __init__(
        self,
        repo_root: Path,
        capability_policy: CapabilityPolicy | None = None,
        tool_policy: ToolPolicy | None = None,
        model_policy: ModelPolicy | None = None,
        role_matrix: RolePermissionMatrix | None = None,
    ):
        self.repo_root = repo_root
        self.capability_policy = capability_policy or load_default_capability_policy(repo_root)
        self.tool_policy = tool_policy or load_default_tool_policy(repo_root)
        self.model_policy = model_policy or load_default_model_policy(repo_root)
        self.role_matrix = role_matrix or load_default_role_permission_matrix(repo_root)

    def evaluate_tool_request(
        self,
        caller_role: str,
        tool_name: str,
        requested_effect: str,
        target: str | None = None,
    ) -> PolicyDecision:
        return _evaluate_tool_request(
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            capability_policy=self.capability_policy,
            tool_policy=self.tool_policy,
        )

    def evaluate_model_request(
        self,
        caller_role: str,
        model_profile_id: str,
        task_type: str,
    ) -> PolicyDecision:
        return _evaluate_model_request(
            caller_role=caller_role,
            model_profile_id=model_profile_id,
            task_type=task_type,
            model_policy=self.model_policy,
            capability_policy=self.capability_policy,
        )

    def write_decision(self, decision: PolicyDecision) -> dict:
        return _write_latest(decision, self.repo_root)

    def get_role_matrix(self) -> RolePermissionMatrix:
        return self.role_matrix

    def get_tool_policy(self) -> ToolPolicy:
        return self.tool_policy

    def get_model_policy(self) -> ModelPolicy:
        return self.model_policy

    def get_capability_policy(self) -> CapabilityPolicy:
        return self.capability_policy

    def set_capability_policy(self, policy: CapabilityPolicy) -> None:
        self.capability_policy = policy

    def set_tool_policy(self, policy: ToolPolicy) -> None:
        self.tool_policy = policy

    def set_model_policy(self, policy: ModelPolicy) -> None:
        self.model_policy = policy

    def set_role_matrix(self, matrix: RolePermissionMatrix) -> None:
        self.role_matrix = matrix

    def reload_defaults(self) -> None:
        self.capability_policy = load_default_capability_policy(self.repo_root)
        self.tool_policy = load_default_tool_policy(self.repo_root)
        self.model_policy = load_default_model_policy(self.repo_root)
        self.role_matrix = load_default_role_permission_matrix(self.repo_root)

    def choose_strictest_decision(self, decisions: list[PolicyDecision]) -> PolicyDecision:
        return _choose_strictest_decision(decisions)
