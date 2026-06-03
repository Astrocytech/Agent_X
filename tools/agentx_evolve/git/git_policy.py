from __future__ import annotations
from dataclasses import dataclass, field
from agentx_evolve.git.git_models import (
    GitOperation, GitResult, GitPolicyRule, GitPolicyResult,
    GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY, GIT_OP_DIFF_STAT,
    GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH,
    GIT_OP_STAGE, GIT_OP_COMMIT, GIT_OP_TAG,
    GS_SUCCESS, GS_BLOCKED,
    GitOpType, new_id, utc_now_iso,
)


_READ_ONLY_OPS = {
    GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY,
    GIT_OP_DIFF_STAT, GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH,
}

_WRITE_OPS = {GIT_OP_STAGE, GIT_OP_COMMIT, GIT_OP_TAG}


class GitPolicyEnforcer:
    def __init__(self, allow_writes: bool = False):
        self._allow_writes = allow_writes
        self._rules: dict[str, list[GitPolicyRule]] = {}

    def add_rule(self, rule: GitPolicyRule) -> None:
        self._rules.setdefault(rule.operation, []).append(rule)

    def enforce(self, op: GitOperation) -> GitPolicyResult:
        matched = []
        for forbidden in ["push", "fetch", "pull", "merge", "rebase", "reset", "clean"]:
            if forbidden in op.target.lower():
                return GitPolicyResult(
                    result_id=new_id("gpr"),
                    operation=op.operation,
                    allowed=False,
                    message=f"Operation involving '{forbidden}' is forbidden",
                )
        if op.operation in _WRITE_OPS and not self._allow_writes:
            return GitPolicyResult(
                result_id=new_id("gpr"),
                operation=op.operation,
                allowed=False,
                message=f"Write git operation '{op.operation}' is not allowed",
            )
        for rule in self._rules.get(op.operation, []):
            matched.append(rule)
            if rule.effect == "BLOCK":
                return GitPolicyResult(
                    result_id=new_id("gpr"),
                    operation=op.operation,
                    allowed=False,
                    message=rule.reason or f"Blocked by rule: {rule.rule_id}",
                    matched_rules=matched,
                )
        return GitPolicyResult(
            result_id=new_id("gpr"),
            operation=op.operation,
            allowed=True,
            message=f"Operation '{op.operation}' allowed",
            matched_rules=matched,
        )

    def check_result(self, op: GitOperation) -> GitResult | None:
        policy = self.enforce(op)
        if not policy.allowed:
            return GitResult(
                result_id=new_id("gr"), timestamp=utc_now_iso(),
                operation=op.operation, status=GS_BLOCKED,
                message=policy.message,
                errors=[policy.message],
            )
        return None
