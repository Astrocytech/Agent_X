from agentx_evolve.git.git_policy import GitPolicyEnforcer
from agentx_evolve.git.git_models import (
    GitOperation, GitPolicyRule,
    GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_STAGE, GIT_OP_COMMIT,
    GIT_OP_TAG, GIT_OP_LOG,
    GS_BLOCKED,
)


class TestGitPolicyEnforcer:
    def test_default_allow_reads(self):
        enforcer = GitPolicyEnforcer()
        op = GitOperation(operation=GIT_OP_STATUS)
        result = enforcer.enforce(op)
        assert result.allowed is True
        assert "allowed" in result.message

    def test_default_block_writes(self):
        enforcer = GitPolicyEnforcer()
        op = GitOperation(operation=GIT_OP_STAGE, target="test.txt")
        result = enforcer.enforce(op)
        assert result.allowed is False
        assert "not allowed" in result.message

    def test_allow_writes_enabled(self):
        enforcer = GitPolicyEnforcer(allow_writes=True)
        op = GitOperation(operation=GIT_OP_STAGE, target="test.txt")
        result = enforcer.enforce(op)
        assert result.allowed is True

    def test_forbidden_target(self):
        enforcer = GitPolicyEnforcer()
        op = GitOperation(operation=GIT_OP_LOG, target="push")
        result = enforcer.enforce(op)
        assert result.allowed is False
        assert "push" in result.message

    def test_forbidden_target_case_insensitive(self):
        enforcer = GitPolicyEnforcer()
        op = GitOperation(operation=GIT_OP_DIFF, target="PUSH")
        result = enforcer.enforce(op)
        assert result.allowed is False

    def test_rule_blocks_operation(self):
        enforcer = GitPolicyEnforcer(allow_writes=True)
        enforcer.add_rule(GitPolicyRule(
            rule_id="r1", operation=GIT_OP_STAGE, effect="BLOCK",
            reason="Stage not allowed",
        ))
        op = GitOperation(operation=GIT_OP_STAGE, target="x")
        result = enforcer.enforce(op)
        assert result.allowed is False
        assert len(result.matched_rules) == 1

    def test_multiple_rules_matched(self):
        enforcer = GitPolicyEnforcer(allow_writes=True)
        enforcer.add_rule(GitPolicyRule(rule_id="r1", operation=GIT_OP_COMMIT, effect="ALLOW"))
        enforcer.add_rule(GitPolicyRule(rule_id="r2", operation=GIT_OP_COMMIT, effect="BLOCK"))
        op = GitOperation(operation=GIT_OP_COMMIT, target="HEAD")
        result = enforcer.enforce(op)
        assert result.allowed is False
        assert len(result.matched_rules) == 2

    def test_add_rule_appends(self):
        enforcer = GitPolicyEnforcer()
        enforcer.add_rule(GitPolicyRule(rule_id="r1", operation=GIT_OP_TAG, effect="BLOCK"))
        enforcer.add_rule(GitPolicyRule(rule_id="r2", operation=GIT_OP_TAG, effect="BLOCK"))
        assert len(enforcer._rules[GIT_OP_TAG]) == 2

    def test_check_result_returns_none_when_allowed(self):
        enforcer = GitPolicyEnforcer()
        op = GitOperation(operation=GIT_OP_STATUS)
        assert enforcer.check_result(op) is None

    def test_check_result_returns_blocked_when_denied(self):
        enforcer = GitPolicyEnforcer()
        op = GitOperation(operation=GIT_OP_STAGE)
        result = enforcer.check_result(op)
        assert result is not None
        assert result.status == GS_BLOCKED
