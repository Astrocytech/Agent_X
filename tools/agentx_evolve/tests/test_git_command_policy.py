import pytest
from agentx_evolve.git.git_command_policy import GitCommandPolicy
from agentx_evolve.git.git_models import (
    GitOperation, GS_SUCCESS, GS_BLOCKED,
    GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY, GIT_OP_DIFF_STAT,
    GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH,
    GIT_OP_STAGE, GIT_OP_COMMIT, GIT_OP_TAG,
)


class TestGitCommandPolicyDefaults:
    def setup_method(self):
        self.policy = GitCommandPolicy()

    def test_read_ops_allowed_by_default(self):
        for op_name in [GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY,
                        GIT_OP_DIFF_STAT, GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH]:
            op = GitOperation(operation=op_name)
            result = self.policy.enforce(op)
            assert result.allowed, f"{op_name} should be allowed"

    def test_write_ops_blocked_by_default(self):
        for op_name in [GIT_OP_STAGE, GIT_OP_COMMIT, GIT_OP_TAG]:
            op = GitOperation(operation=op_name)
            result = self.policy.enforce(op)
            assert not result.allowed, f"{op_name} should be blocked"

    def test_permanently_blocked_ops(self):
        for blocked in GitCommandPolicy.PERMANENTLY_BLOCKED:
            op = GitOperation(operation=blocked.upper())
            result = self.policy.enforce(op)
            assert not result.allowed, f"{blocked} should be permanently blocked"

    def test_unknown_operation_blocked(self):
        op = GitOperation(operation="UNKNOWN_OP")
        result = self.policy.enforce(op)
        assert not result.allowed

    def test_target_with_forbidden_word_blocked(self):
        op = GitOperation(operation=GIT_OP_STATUS, target="origin/main..push")
        result = self.policy.enforce(op)
        assert not result.allowed

    def test_target_with_merge_blocked(self):
        op = GitOperation(operation=GIT_OP_DIFF, target="merge-branch")
        result = self.policy.enforce(op)
        assert not result.allowed


class TestGitCommandPolicyEntries:
    def setup_method(self):
        self.policy = GitCommandPolicy()

    def test_get_template_known_op(self):
        op = GitOperation(operation=GIT_OP_STATUS)
        tmpl = self.policy.get_template(op)
        assert tmpl is not None
        assert "git" in tmpl
        assert "--short" in tmpl

    def test_get_template_with_target(self):
        op = GitOperation(operation=GIT_OP_DIFF, target="HEAD~1")
        tmpl = self.policy.get_template(op)
        assert tmpl is not None
        assert "HEAD~1" in tmpl

    def test_get_template_unknown_op(self):
        op = GitOperation(operation="UNKNOWN")
        assert self.policy.get_template(op) is None

    def test_add_entry_new_op(self):
        self.policy.add_entry("custom_op", ["custom", "--flag"], effect="READ")
        op = GitOperation(operation="custom_op")
        result = self.policy.enforce(op)
        assert result.allowed

    def test_class_constants_present(self):
        assert GIT_OP_STATUS in GitCommandPolicy.READ_ONLY_OPS
        assert GIT_OP_STAGE in GitCommandPolicy.WRITE_OPS
        assert "push" in GitCommandPolicy.PERMANENTLY_BLOCKED


class TestGitPolicyResult:
    def setup_method(self):
        self.policy = GitCommandPolicy()

    def test_allowed_result_has_positive_message(self):
        op = GitOperation(operation=GIT_OP_STATUS)
        result = self.policy.enforce(op)
        assert "allowed" in result.message.lower()

    def test_blocked_result_has_reason(self):
        op = GitOperation(operation=GIT_OP_COMMIT)
        result = self.policy.enforce(op)
        assert not result.allowed
        assert len(result.message) > 0

    def test_result_has_operation_field(self):
        op = GitOperation(operation=GIT_OP_STATUS)
        result = self.policy.enforce(op)
        assert result.operation == GIT_OP_STATUS

    def test_result_id_starts_with_gpr(self):
        op = GitOperation(operation=GIT_OP_STATUS)
        result = self.policy.enforce(op)
        assert result.result_id.startswith("gpr-")
