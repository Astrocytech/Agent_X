from agentx_evolve.git.git_models import (
    GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY, GIT_OP_DIFF_STAT,
    GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH, GIT_OP_STAGE, GIT_OP_COMMIT, GIT_OP_TAG,
    ALL_GIT_OPS,
    GS_SUCCESS, GS_FAILED, GS_BLOCKED, GS_PENDING, GS_PARTIAL, GS_INVALID,
    GIT_EFFECT_READ, GIT_EFFECT_STAGE, GIT_EFFECT_COMMIT,
    GIT_EFFECT_BRANCH, GIT_EFFECT_REVERT, GIT_EFFECT_PUSH,
    GIT_LOCK_ACQUIRED, GIT_LOCK_RELEASED, GIT_LOCK_BLOCKED,
    GIT_LOCK_TIMEOUT, GIT_LOCK_STALE_REJECTED,
    REF_KIND_BRANCH, REF_KIND_TAG, REF_KIND_REMOTE, REF_KIND_REFSPEC, REF_KIND_COMMIT,
    PROTECTED_BRANCHES,
    GitOpType, utc_now_iso, new_id, to_dict, sha256_text, sha256_file,
    GitOperation, GitResult, GitDiffEntry, GitDiffResult,
    GitPolicyRule, GitPolicyResult, GitCommandResult, GitOperationResult,
    GitStatusDiffResult, GitMutationRequest, GitBranchRequest,
    GitRefValidationResult, GitStageRequest, GitCommitEvidence,
    GitPushRequest, GitRevertRequest, GitLockRecord, GitAuditEvent,
    GitEvidenceManifest, GitReviewReport, GitCompletionRecord, GitCommandPolicy,
)


class TestConstants:
    def test_git_ops(self):
        assert GIT_OP_STATUS == "STATUS"
        assert GIT_OP_DIFF == "DIFF"
        assert len(ALL_GIT_OPS) == 10

    def test_statuses(self):
        assert GS_SUCCESS == "SUCCESS"
        assert GS_FAILED == "FAILED"
        assert GS_BLOCKED == "BLOCKED"

    def test_locks(self):
        assert GIT_LOCK_ACQUIRED == "ACQUIRED"
        assert GIT_LOCK_STALE_REJECTED == "STALE_REJECTED"

    def test_protected_branches(self):
        assert "main" in PROTECTED_BRANCHES
        assert "master" in PROTECTED_BRANCHES


class TestHelpers:
    def test_utc_now_iso(self):
        val = utc_now_iso()
        assert "T" in val

    def test_new_id(self):
        val = new_id("git")
        assert val.startswith("git-")

    def test_sha256_text(self):
        h = sha256_text("test")
        assert len(h) == 64

    def test_to_dict_dataclass(self):
        op = GitOperation(op_id="op-1")
        d = to_dict(op)
        assert d["op_id"] == "op-1"


class TestGitOperation:
    def test_defaults(self):
        op = GitOperation()
        assert op.operation == GIT_OP_STATUS
        assert op.op_type == GitOpType.READ

    def test_with_values(self):
        op = GitOperation(
            op_id="go-1", operation=GIT_OP_DIFF,
            target="HEAD", op_type=GitOpType.WRITE,
        )
        assert op.operation == GIT_OP_DIFF

    def test_to_dict(self):
        d = GitOperation(op_id="o1").to_dict()
        assert d["op_id"] == "o1"


class TestGitResult:
    def test_defaults(self):
        r = GitResult()
        assert r.status == GS_SUCCESS
        assert r.returncode == 0

    def test_with_values(self):
        r = GitResult(
            result_id="gr-1", operation=GIT_OP_STATUS,
            status=GS_FAILED, returncode=1, stdout="out",
        )
        assert r.returncode == 1


class TestGitDiffEntry:
    def test_defaults(self):
        e = GitDiffEntry()
        assert e.path == ""
        assert e.additions == 0


class TestGitDiffResult:
    def test_inherits(self):
        r = GitDiffResult(result_id="gdr-1")
        assert r.files_changed == 0
        assert r.entries == []


class TestGitPolicyRule:
    def test_defaults(self):
        r = GitPolicyRule()
        assert r.effect == "ALLOW"


class TestGitPolicyResult:
    def test_defaults(self):
        r = GitPolicyResult()
        assert r.allowed is True


class TestGitCommandResult:
    def test_defaults(self):
        r = GitCommandResult()
        assert r.exit_code == 0


class TestGitMutationRequest:
    def test_defaults(self):
        r = GitMutationRequest()
        assert r.operation == ""


class TestGitBranchRequest:
    def test_defaults(self):
        r = GitBranchRequest()
        assert r.new_branch == ""
        assert r.base_branch == "HEAD"


class TestGitRefValidationResult:
    def test_defaults(self):
        r = GitRefValidationResult()
        assert r.is_valid is True
        assert r.is_protected is False


class TestGitStageRequest:
    def test_defaults(self):
        r = GitStageRequest()
        assert r.paths == []


class TestGitCommitEvidence:
    def test_defaults(self):
        r = GitCommitEvidence()
        assert r.commit_hash == ""


class TestGitPushRequest:
    def test_defaults(self):
        r = GitPushRequest()
        assert r.remote == "origin"


class TestGitRevertRequest:
    def test_defaults(self):
        r = GitRevertRequest()
        assert r.target_commit == ""


class TestGitLockRecord:
    def test_defaults(self):
        r = GitLockRecord()
        assert r.timeout_seconds == 30


class TestGitAuditEvent:
    def test_defaults(self):
        r = GitAuditEvent()
        assert r.event_type == ""


class TestGitEvidenceManifest:
    def test_defaults(self):
        r = GitEvidenceManifest()
        assert r.operations == []


class TestGitReviewReport:
    def test_defaults(self):
        r = GitReviewReport()
        assert r.status == ""


class TestGitCompletionRecord:
    def test_defaults(self):
        r = GitCompletionRecord()
        assert r.status == "VALIDATED"


class TestGitCommandPolicy:
    def test_defaults(self):
        p = GitCommandPolicy()
        assert p.command == "git"
        assert p.effect == "READ"
        assert p.enabled is True
