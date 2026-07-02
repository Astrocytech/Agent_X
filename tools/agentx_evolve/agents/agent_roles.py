from __future__ import annotations

from dataclasses import dataclass, field

ROLE_PLANNER = "planner"
ROLE_EXECUTOR = "executor"
ROLE_VALIDATOR = "validator"
ROLE_REVIEWER = "reviewer"
ROLE_PROMOTION = "promotion"
ROLE_OBSERVER = "observer"
ROLE_ADVERSARY = "adversary"


@dataclass
class MvpAgentRole:
    role_id: str
    allowed_actions: list[str]
    forbidden_actions: list[str]
    description: str = ""


class MvpRoleRegistry:
    def __init__(self) -> None:
        self._roles: dict[str, MvpAgentRole] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        self._roles[ROLE_PLANNER] = MvpAgentRole(
            role_id=ROLE_PLANNER,
            allowed_actions=["generate_plan", "assign_tasks", "estimate_effort"],
            forbidden_actions=["execute_plan", "write_code", "modify_source"],
            description="Responsible for decomposing tasks and producing execution plans. Cannot execute or write code.",
        )
        self._roles[ROLE_EXECUTOR] = MvpAgentRole(
            role_id=ROLE_EXECUTOR,
            allowed_actions=["write_code", "run_tests", "modify_source"],
            forbidden_actions=["validate_own_action", "promote_artifact"],
            description="Implements the plan by writing code and running tests. Cannot validate or promote its own work.",
        )
        self._roles[ROLE_VALIDATOR] = MvpAgentRole(
            role_id=ROLE_VALIDATOR,
            allowed_actions=["run_tests", "inspect_output", "verify_contract"],
            forbidden_actions=["promote_artifact", "generate_plan"],
            description="Validates that outputs meet acceptance criteria. Cannot promote artifacts or generate plans.",
        )
        self._roles[ROLE_REVIEWER] = MvpAgentRole(
            role_id=ROLE_REVIEWER,
            allowed_actions=["audit_evidence", "approve_promotion", "flag_issues"],
            forbidden_actions=["alter_evidence", "modify_source", "write_code"],
            description="Reviews evidence and approvals. Cannot alter evidence or modify source code.",
        )
        self._roles[ROLE_PROMOTION] = MvpAgentRole(
            role_id=ROLE_PROMOTION,
            allowed_actions=["promote_artifact", "tag_release", "update_changelog"],
            forbidden_actions=["generate_source", "write_code", "modify_source"],
            description="Promotes validated artifacts to release. Cannot generate or modify source code.",
        )
        self._roles[ROLE_OBSERVER] = MvpAgentRole(
            role_id=ROLE_OBSERVER,
            allowed_actions=["read_logs", "monitor_progress", "generate_reports"],
            forbidden_actions=["modify_state", "execute_actions", "approve_promotion"],
            description="Passively monitors agent activities and generates reports. Cannot modify state or execute actions.",
        )
        self._roles[ROLE_ADVERSARY] = MvpAgentRole(
            role_id=ROLE_ADVERSARY,
            allowed_actions=["propose_counterexample", "challenge_plan", "stress_test_output"],
            forbidden_actions=["promote_artifact", "approve_promotion", "modify_source"],
            description="Challenges plans and outputs to uncover weaknesses. Cannot promote or approve artifacts.",
        )

    def get_role(self, role_id: str) -> MvpAgentRole | None:
        return self._roles.get(role_id)

    def is_action_allowed(self, role_id: str, action: str) -> bool:
        role = self.get_role(role_id)
        if role is None:
            return False
        return action in role.allowed_actions

    def is_action_forbidden(self, role_id: str, action: str) -> bool:
        role = self.get_role(role_id)
        if role is None:
            return False
        return action in role.forbidden_actions

    def validate_separation(self, executor_role: str, reviewer_role: str) -> bool:
        return executor_role != reviewer_role
