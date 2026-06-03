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
