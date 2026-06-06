from pathlib import Path
from agentx_evolve.git.git_models import (
    GitOperation, GitPolicyResult, GitPolicyRule,
    GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY, GIT_OP_DIFF_STAT,
    GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH,
    GIT_OP_STAGE, GIT_OP_COMMIT, GIT_OP_TAG,
    GS_SUCCESS, GS_BLOCKED,
    GitOpType, new_id, utc_now_iso, to_dict,
)


class GitCommandPolicy:
    READ_ONLY_OPS = {GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY,
                     GIT_OP_DIFF_STAT, GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH}
    WRITE_OPS = {GIT_OP_STAGE, GIT_OP_COMMIT, GIT_OP_TAG}
    PERMANENTLY_BLOCKED = ["push", "fetch", "pull", "merge", "rebase",
                           "reset", "clean", "cherry-pick", "revert"]

    def __init__(self):
        self._entries: dict[str, dict] = {}
        self._init_defaults()

    def _init_defaults(self):
        self.add_entry(GIT_OP_STATUS, ["status", "--short"], effect="READ")
        self.add_entry(GIT_OP_DIFF, ["diff", "--no-ext-diff", "--no-textconv"], effect="READ")
        self.add_entry(GIT_OP_DIFF_NAME_ONLY, ["diff", "--no-ext-diff", "--name-only"], effect="READ")
        self.add_entry(GIT_OP_DIFF_STAT, ["diff", "--no-ext-diff", "--stat"], effect="READ")
        self.add_entry(GIT_OP_LOG, ["log", "--oneline", "-20"], effect="READ")
        self.add_entry(GIT_OP_SHOW, ["show"], effect="READ")
        self.add_entry(GIT_OP_BRANCH, ["branch", "--list"], effect="READ")
        self.add_entry("rev_parse_show_toplevel", ["rev-parse", "--show-toplevel"], effect="READ")
        self.add_entry("rev_parse_head", ["rev-parse", "HEAD"], effect="READ")
        self.add_entry("rev_parse_abbrev_ref", ["rev-parse", "--abbrev-ref", "HEAD"], effect="READ")
        self.add_entry("ls_files", ["ls-files"], effect="READ")

    def add_entry(self, op_name: str, fixed_args: list[str], effect: str = "READ"):
        self._entries[op_name] = {
            "fixed_args": fixed_args,
            "effect": effect,
            "mutates": effect != "READ",
        }

    def get_template(self, op: GitOperation) -> list[str] | None:
        entry = self._entries.get(op.operation)
        if entry is None:
            return None
        if op.target:
            return ["git"] + entry["fixed_args"] + [op.target]
        return ["git"] + entry["fixed_args"]

    def enforce(self, op: GitOperation) -> GitPolicyResult:
        op_lower = op.operation.lower()
        target_lower = op.target.lower()
        for blocked in self.PERMANENTLY_BLOCKED:
            if blocked in op_lower or blocked in target_lower:
                return GitPolicyResult(
                    result_id=new_id("gpr"),
                    operation=op.operation,
                    allowed=False,
                    message=f"Operation involving '{blocked}' is permanently blocked",
                )
        if op.operation in self.WRITE_OPS:
            return GitPolicyResult(
                result_id=new_id("gpr"),
                operation=op.operation,
                allowed=False,
                message=f"Write git operation '{op.operation}' is not allowed",
            )
        entry = self._entries.get(op.operation)
        if entry is None:
            return GitPolicyResult(
                result_id=new_id("gpr"),
                operation=op.operation,
                allowed=False,
                message=f"No policy entry for operation '{op.operation}'",
            )
        for forbidden in ["push", "fetch", "pull", "merge", "rebase", "reset", "clean"]:
            if forbidden in op.target.lower():
                return GitPolicyResult(
                    result_id=new_id("gpr"),
                    operation=op.operation,
                    allowed=False,
                    message=f"Operation target involves forbidden '{forbidden}'",
                )
        return GitPolicyResult(
            result_id=new_id("gpr"),
            operation=op.operation,
            allowed=True,
            message=f"Operation '{op.operation}' allowed by policy",
        )
