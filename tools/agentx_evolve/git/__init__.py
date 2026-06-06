from agentx_evolve.git.git_models import (
    GitOperation, GitResult, GitDiffResult, GitDiffEntry,
    GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY, GIT_OP_DIFF_STAT,
    GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH, GIT_OP_STAGE, GIT_OP_COMMIT, GIT_OP_TAG,
    GS_SUCCESS, GS_FAILED, GS_BLOCKED, GS_PENDING, GS_PARTIAL, GS_INVALID,
    GitOpType, new_id, utc_now_iso, to_dict,
    GitCommandResult, GitOperationResult, GitStatusDiffResult,
    GitMutationRequest, GitBranchRequest, GitRefValidationResult,
    GitStageRequest, GitCommitEvidence, GitPushRequest, GitRevertRequest,
    GitLockRecord, GitAuditEvent, GitEvidenceManifest, GitReviewReport,
    GitCompletionRecord, GitCommandPolicy as GitCommandPolicySchema,
    GIT_EFFECT_READ, GIT_EFFECT_STAGE, GIT_EFFECT_COMMIT,
    GIT_EFFECT_BRANCH, GIT_EFFECT_REVERT, GIT_EFFECT_PUSH,
    GIT_LOCK_ACQUIRED, GIT_LOCK_RELEASED, GIT_LOCK_BLOCKED,
    GIT_LOCK_TIMEOUT, GIT_LOCK_STALE_REJECTED,
    REF_KIND_BRANCH, REF_KIND_TAG, REF_KIND_REMOTE, REF_KIND_REFSPEC, REF_KIND_COMMIT,
    PROTECTED_BRANCHES,
)
from agentx_evolve.git.git_operations import (
    run_git_operation, git_status as git_operations_status,
    git_diff as git_operations_diff,
    git_diff_name_only as git_operations_diff_name_only,
    git_diff_stat as git_operations_diff_stat,
    git_log, git_knows_repo,
)
from agentx_evolve.git.git_policy import GitPolicyEnforcer, GitPolicyRule, GitPolicyResult
from agentx_evolve.git.git_branch import git_branch
from agentx_evolve.git.git_command_policy import GitCommandPolicy
from agentx_evolve.git.git_command_runner import run_git_command, MAX_OUTPUT_BYTES, GIT_TIMEOUT
from agentx_evolve.git.git_commit import git_commit
from agentx_evolve.git.git_diff import (
    git_diff as git_diff_impl,
    git_diff_name_only as git_diff_impl_name_only,
    git_diff_stat as git_diff_impl_stat,
)
from agentx_evolve.git.git_environment import build_git_environment, build_isolated_home, cleanup_isolated_home
from agentx_evolve.git.git_evidence import (
    append_git_operation, append_git_result, append_git_blocked,
    append_git_mutation_request, append_git_commit_evidence,
    write_latest_artifact, write_latest_operation, write_latest_result,
    write_git_evidence_manifest, write_git_review_report, write_git_completion_record,
)
from agentx_evolve.git.git_locks import acquire_git_lock, release_git_lock, is_git_lock_stale
from agentx_evolve.git.git_mutation_gate import MutationGate
from agentx_evolve.git.git_push import git_push
from agentx_evolve.git.git_ref_validator import is_protected_branch, is_valid_branch_name, validate_ref
from agentx_evolve.git.git_revert import git_revert
from agentx_evolve.git.git_stage import git_stage
from agentx_evolve.git.git_status import git_status

__all__ = [
    "GitOperation", "GitResult", "GitDiffResult", "GitDiffEntry",
    "GIT_OP_STATUS", "GIT_OP_DIFF", "GIT_OP_DIFF_NAME_ONLY", "GIT_OP_DIFF_STAT",
    "GIT_OP_LOG", "GIT_OP_SHOW", "GIT_OP_BRANCH", "GIT_OP_STAGE", "GIT_OP_COMMIT", "GIT_OP_TAG",
    "GS_SUCCESS", "GS_FAILED", "GS_BLOCKED", "GS_PENDING", "GS_PARTIAL", "GS_INVALID",
    "GitOpType", "new_id", "utc_now_iso", "to_dict",
    "GitCommandResult", "GitOperationResult", "GitStatusDiffResult",
    "GitMutationRequest", "GitBranchRequest", "GitRefValidationResult",
    "GitStageRequest", "GitCommitEvidence", "GitPushRequest", "GitRevertRequest",
    "GitLockRecord", "GitAuditEvent", "GitEvidenceManifest", "GitReviewReport",
    "GitCompletionRecord", "GitCommandPolicySchema",
    "GIT_EFFECT_READ", "GIT_EFFECT_STAGE", "GIT_EFFECT_COMMIT",
    "GIT_EFFECT_BRANCH", "GIT_EFFECT_REVERT", "GIT_EFFECT_PUSH",
    "GIT_LOCK_ACQUIRED", "GIT_LOCK_RELEASED", "GIT_LOCK_BLOCKED",
    "GIT_LOCK_TIMEOUT", "GIT_LOCK_STALE_REJECTED",
    "REF_KIND_BRANCH", "REF_KIND_TAG", "REF_KIND_REMOTE", "REF_KIND_REFSPEC", "REF_KIND_COMMIT",
    "PROTECTED_BRANCHES",
    "run_git_operation", "git_operations_status", "git_operations_diff",
    "git_operations_diff_name_only", "git_operations_diff_stat",
    "git_log", "git_knows_repo",
    "GitPolicyEnforcer", "GitPolicyRule", "GitPolicyResult",
    "git_branch", "GitCommandPolicy", "run_git_command", "MAX_OUTPUT_BYTES", "GIT_TIMEOUT",
    "git_commit", "git_diff_impl", "git_diff_impl_name_only", "git_diff_impl_stat",
    "build_git_environment", "build_isolated_home", "cleanup_isolated_home",
    "append_git_operation", "append_git_result", "append_git_blocked",
    "append_git_mutation_request", "append_git_commit_evidence",
    "write_latest_artifact", "write_latest_operation", "write_latest_result",
    "write_git_evidence_manifest", "write_git_review_report", "write_git_completion_record",
    "acquire_git_lock", "release_git_lock", "is_git_lock_stale",
    "MutationGate", "git_push", "is_protected_branch", "is_valid_branch_name", "validate_ref",
    "git_revert", "git_stage", "git_status",
]
