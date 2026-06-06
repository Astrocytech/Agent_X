from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

GIT_OP_STATUS = "STATUS"
GIT_OP_DIFF = "DIFF"
GIT_OP_DIFF_NAME_ONLY = "DIFF_NAME_ONLY"
GIT_OP_DIFF_STAT = "DIFF_STAT"
GIT_OP_LOG = "LOG"
GIT_OP_SHOW = "SHOW"
GIT_OP_BRANCH = "BRANCH"
GIT_OP_STAGE = "STAGE"
GIT_OP_COMMIT = "COMMIT"
GIT_OP_TAG = "TAG"
ALL_GIT_OPS = [GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY, GIT_OP_DIFF_STAT,
               GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH, GIT_OP_STAGE, GIT_OP_COMMIT, GIT_OP_TAG]

GS_SUCCESS = "SUCCESS"
GS_FAILED = "FAILED"
GS_BLOCKED = "BLOCKED"
GS_PENDING = "PENDING"
GS_PARTIAL = "PARTIAL"
GS_INVALID = "INVALID"

GIT_EFFECT_READ = "READ"
GIT_EFFECT_STAGE = "STAGE"
GIT_EFFECT_COMMIT = "COMMIT"
GIT_EFFECT_BRANCH = "BRANCH"
GIT_EFFECT_REVERT = "REVERT"
GIT_EFFECT_PUSH = "PUSH"

GIT_LOCK_ACQUIRED = "ACQUIRED"
GIT_LOCK_RELEASED = "RELEASED"
GIT_LOCK_BLOCKED = "BLOCKED"
GIT_LOCK_TIMEOUT = "TIMEOUT"
GIT_LOCK_STALE_REJECTED = "STALE_REJECTED"

REF_KIND_BRANCH = "BRANCH"
REF_KIND_TAG = "TAG"
REF_KIND_REMOTE = "REMOTE"
REF_KIND_REFSPEC = "REFSPEC"
REF_KIND_COMMIT = "COMMIT"

PROTECTED_BRANCHES = ["main", "master", "develop", "release", "production", "staging", "stable"]


class GitOpType:
    READ = "read"
    WRITE = "write"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    if prefix:
        return f"{prefix}-{uuid4().hex}"
    return uuid4().hex


def to_dict(obj: object) -> dict:
    if isinstance(obj, Enum):
        return obj.value
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if isinstance(val, list):
                result[f] = [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in val]
            elif isinstance(val, dict):
                result[f] = {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in val.items()}
            elif isinstance(val, Enum):
                result[f] = val.value
            else:
                result[f] = val
        return result
    if isinstance(obj, dict):
        return {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in obj]
    return obj


@dataclass
class GitOperation:
    schema_version: str = "1.0"
    schema_id: str = "git_operation.schema.json"
    op_id: str = ""
    timestamp: str = ""
    operation: str = GIT_OP_STATUS
    target: str = ""
    repo_path: str = ""
    op_type: str = GitOpType.READ
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class GitResult:
    schema_version: str = "1.0"
    schema_id: str = "git_result.schema.json"
    result_id: str = ""
    timestamp: str = ""
    operation: str = GIT_OP_STATUS
    status: str = GS_SUCCESS
    message: str = ""
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    data: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class GitDiffEntry:
    path: str = ""
    change_type: str = ""
    additions: int = 0
    deletions: int = 0
    diff_content: str = ""


@dataclass
class GitDiffResult(GitResult):
    entries: list[GitDiffEntry] = field(default_factory=list)
    files_changed: int = 0


def sha256_text(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class GitPolicyRule:
    rule_id: str = ""
    operation: str = ""
    effect: str = "ALLOW"
    reason: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class GitPolicyResult:
    result_id: str = ""
    operation: str = ""
    allowed: bool = True
    message: str = ""
    matched_rules: list[GitPolicyRule] = field(default_factory=list)


@dataclass
class GitCommandResult:
    result_id: str = ""
    timestamp: str = ""
    operation_id: str = ""
    operation_name: str = ""
    status: str = GS_SUCCESS
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    argv_sha256: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class GitOperationResult:
    result_id: str = ""
    operation_id: str = ""
    timestamp: str = ""
    status: str = GS_SUCCESS
    message: str = ""
    authority_refs: dict[str, str] = field(default_factory=dict)
    command_result: Any = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class GitStatusDiffResult(GitResult):
    entries: list[GitDiffEntry] = field(default_factory=list)
    files_changed: int = 0


@dataclass
class GitMutationRequest:
    request_id: str = ""
    operation: str = ""
    repo_path: str = ""
    target: str = ""
    policy_decision_id: str = ""
    sandbox_decision_id: str = ""
    promotion_gate_id: str = ""
    human_approval_id: str = ""
    timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GitBranchRequest:
    request_id: str = ""
    repo_path: str = ""
    new_branch: str = ""
    base_branch: str = "HEAD"
    governance_decision_id: str = ""


@dataclass
class GitRefValidationResult:
    result_id: str = ""
    timestamp: str = ""
    raw_ref: str = ""
    normalized_ref: str = ""
    ref_kind: str = ""
    is_valid: bool = True
    is_protected: bool = False
    message: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class GitStageRequest:
    request_id: str = ""
    repo_path: str = ""
    paths: list[str] = field(default_factory=list)
    patch_evidence_id: str = ""


@dataclass
class GitCommitEvidence:
    commit_id: str = ""
    commit_hash: str = ""
    message: str = ""
    author: str = ""
    timestamp: str = ""
    stage_evidence_id: str = ""
    changes_summary: str = ""


@dataclass
class GitPushRequest:
    request_id: str = ""
    repo_path: str = ""
    remote: str = "origin"
    source_ref: str = "HEAD"
    target_ref: str = ""
    promotion_gate_id: str = ""


@dataclass
class GitRevertRequest:
    request_id: str = ""
    repo_path: str = ""
    target_commit: str = ""
    governance_decision_id: str = ""
    human_approval_id: str = ""


@dataclass
class GitLockRecord:
    lock_id: str = ""
    holder_id: str = ""
    operation_id: str = ""
    status: str = ""
    acquired_at: str = ""
    released_at: str = ""
    timeout_seconds: int = 30
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class GitAuditEvent:
    event_id: str = ""
    event_type: str = ""
    timestamp: str = ""
    actor: str = ""
    action: str = ""
    resource: str = ""
    outcome: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class GitEvidenceManifest:
    manifest_id: str = ""
    validated_commit: str = ""
    timestamp: str = ""
    operations: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)
    hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class GitReviewReport:
    report_id: str = ""
    commit_hash: str = ""
    reviewer: str = ""
    status: str = ""
    findings: list[str] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class GitCompletionRecord:
    record_id: str = ""
    timestamp: str = ""
    repo_root: str = ""
    status: str = "VALIDATED"
    summary: str = ""
    hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class GitCommandPolicy:
    schema_version: str = "1.0"
    schema_id: str = "git_command_policy.schema.json"
    policy_id: str = ""
    operation_name: str = ""
    command: str = "git"
    fixed_args: list[str] = field(default_factory=list)
    allowed_dynamic_args: list[str] = field(default_factory=list)
    allowed_roles: list[str] = field(default_factory=list)
    effect: str = "READ"
    requires_policy: bool = True
    requires_sandbox: bool = True
    mutates_repository: bool = False
    uses_remote: bool = False
    enabled: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
