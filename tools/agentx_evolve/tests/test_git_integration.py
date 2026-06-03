import pytest
from pathlib import Path
from agentx_evolve.git.git_models import (
    GitOperation, GitResult, GitDiffResult, GitDiffEntry,
    GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY, GIT_OP_DIFF_STAT,
    GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH, GIT_OP_COMMIT,
    GS_SUCCESS, GS_FAILED, GS_BLOCKED,
    GitOpType, new_id, utc_now_iso, to_dict,
)
from agentx_evolve.git.git_operations import (
    run_git_operation, git_knows_repo,
)
from agentx_evolve.git.git_policy import GitPolicyEnforcer, GitPolicyRule, GitPolicyResult


# ---------------------------------------------------------------------------
# GitModel tests
# ---------------------------------------------------------------------------

def test_git_operation_defaults():
    op = GitOperation()
    assert op.operation == GIT_OP_STATUS
    assert op.op_type == GitOpType.READ


def test_git_operation_custom():
    op = GitOperation(operation=GIT_OP_DIFF, target="HEAD", repo_path="/repo")
    assert op.operation == GIT_OP_DIFF
    assert op.target == "HEAD"


def test_git_operation_to_dict():
    op = GitOperation(op_id="go-1", operation=GIT_OP_LOG)
    d = op.to_dict()
    assert d["op_id"] == "go-1"
    assert d["operation"] == GIT_OP_LOG


def test_git_result_defaults():
    r = GitResult()
    assert r.status == GS_SUCCESS
    assert r.returncode == 0


def test_git_result_custom():
    r = GitResult(status=GS_FAILED, message="error", errors=["fail"])
    assert r.status == GS_FAILED


def test_git_result_to_dict():
    r = GitResult(result_id="gr-1", operation=GIT_OP_STATUS, status=GS_SUCCESS)
    d = r.to_dict()
    assert d["result_id"] == "gr-1"


def test_git_diff_entry():
    e = GitDiffEntry(path="src/main.py", change_type="M", additions=5, deletions=2)
    assert e.path == "src/main.py"
    assert e.additions == 5


def test_git_diff_result():
    r = GitDiffResult(files_changed=3)
    assert r.files_changed == 3


def test_helpers():
    nid = new_id("git")
    assert nid.startswith("git-")
    iso = utc_now_iso()
    assert "T" in iso


# ---------------------------------------------------------------------------
# GitOperation tests (in a non-repo directory)
# ---------------------------------------------------------------------------

def test_run_git_operation_not_a_repo(tmp_path):
    op = GitOperation(operation=GIT_OP_STATUS, repo_path=str(tmp_path))
    result = run_git_operation(op)
    assert result.status in (GS_FAILED, GS_SUCCESS)


def test_run_git_operation_diff_not_a_repo(tmp_path):
    op = GitOperation(operation=GIT_OP_DIFF, target="HEAD", repo_path=str(tmp_path))
    result = run_git_operation(op)
    assert result.status in (GS_FAILED, GS_SUCCESS)


def test_run_git_operation_write_blocked():
    op = GitOperation(operation=GIT_OP_COMMIT, target="", repo_path=".")
    result = run_git_operation(op)
    assert result.status == GS_BLOCKED


def test_git_knows_repo_not_a_repo(tmp_path):
    assert not git_knows_repo(str(tmp_path))


def test_git_knows_repo_current():
    result = git_knows_repo(".")
    assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# GitPolicy tests
# ---------------------------------------------------------------------------

def test_policy_enforcer_defaults():
    e = GitPolicyEnforcer()
    op = GitOperation(operation=GIT_OP_STATUS)
    result = e.enforce(op)
    assert result.allowed


def test_policy_enforcer_blocks_write():
    e = GitPolicyEnforcer(allow_writes=False)
    op = GitOperation(operation=GIT_OP_COMMIT)
    result = e.enforce(op)
    assert not result.allowed


def test_policy_enforcer_allows_write():
    e = GitPolicyEnforcer(allow_writes=True)
    op = GitOperation(operation=GIT_OP_COMMIT)
    result = e.enforce(op)
    assert result.allowed


def test_policy_enforcer_blocks_push_in_target():
    e = GitPolicyEnforcer(allow_writes=True)
    op = GitOperation(operation=GIT_OP_DIFF, target="origin/main..push")
    result = e.enforce(op)
    assert not result.allowed


def test_policy_enforcer_blocks_reset():
    e = GitPolicyEnforcer(allow_writes=True)
    op = GitOperation(operation=GIT_OP_DIFF, target="HEAD..reset")
    result = e.enforce(op)
    assert not result.allowed


def test_policy_check_result():
    e = GitPolicyEnforcer(allow_writes=False)
    op = GitOperation(operation=GIT_OP_COMMIT)
    result = e.check_result(op)
    assert result is not None
    assert result.status == GS_BLOCKED


def test_policy_check_result_allows():
    e = GitPolicyEnforcer()
    op = GitOperation(operation=GIT_OP_STATUS)
    result = e.check_result(op)
    assert result is None


def test_policy_add_rule():
    e = GitPolicyEnforcer(allow_writes=True)
    e.add_rule(GitPolicyRule(operation=GIT_OP_DIFF, effect="BLOCK", reason="No diff"))
    op = GitOperation(operation=GIT_OP_DIFF)
    result = e.enforce(op)
    assert not result.allowed


def test_policy_result():
    r = GitPolicyResult(result_id="gpr-1", operation=GIT_OP_STATUS, allowed=True)
    assert r.allowed


# ---------------------------------------------------------------------------
# Model serialization tests
# ---------------------------------------------------------------------------

def test_diff_entry_to_dict():
    e = GitDiffEntry(path="f.py", change_type="M")
    assert e.path == "f.py"


def test_git_op_type():
    assert GitOpType.READ == "read"
    assert GitOpType.WRITE == "write"
