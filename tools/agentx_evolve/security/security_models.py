from __future__ import annotations
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

DECISION_ALLOW = "ALLOW"
DECISION_BLOCK = "BLOCK"
DECISION_WARN = "WARN"
DECISION_NEEDS_GOVERNANCE = "NEEDS_GOVERNANCE"
DECISION_NEEDS_ROLLBACK_SNAPSHOT = "NEEDS_ROLLBACK_SNAPSHOT"
DECISION_NEEDS_SESSION = "NEEDS_SESSION"

STATUS_SUCCESS = "SUCCESS"
STATUS_BLOCKED = "BLOCKED"
STATUS_FAILED = "FAILED"
STATUS_DRY_RUN = "DRY_RUN"
STATUS_PASS = "PASS"

OP_READ = "READ"
OP_WRITE = "WRITE"
OP_EDIT = "EDIT"
OP_PATCH_PRECHECK = "PATCH_PRECHECK"
OP_SUBPROCESS = "SUBPROCESS"
OP_NETWORK = "NETWORK"
OP_REDACT = "REDACT"


SV_PATH_ESCAPE = "PATH_ESCAPE"
SV_SUBPROCESS = "SUBPROCESS"
SV_REDACTION_FAIL = "REDACTION_FAIL"


@dataclass
class SecurityViolation:
    schema_version: str = "1.0"
    schema_id: str = "security_violation.schema.json"
    violation_id: str = ""
    violation_type: str = ""
    timestamp: str = ""
    source_component: str = "Security"
    target: str | None = None
    reason: str = ""
    severity: str = "medium"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    if prefix:
        return f"{prefix}-{uuid4().hex}"
    return uuid4().hex


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if isinstance(val, Path):
                result[f] = str(val)
            elif isinstance(val, list):
                result[f] = [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in val]
            else:
                result[f] = val
        return result
    if isinstance(obj, dict):
        return {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in obj]
    return obj


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def has_control_chars(s: str) -> bool:
    return bool(_CONTROL_CHARS_RE.search(s))


@dataclass
class SandboxPolicy:
    schema_version: str = "1.0"
    schema_id: str = "sandbox_policy.schema.json"
    policy_id: str = ""
    repo_root: str = ""
    runtime_state_root: str = ".agentx-init"
    protected_paths: list[str] = field(default_factory=list)
    source_write_allowed: bool = False
    runtime_write_allowed: bool = True
    network_allowed: bool = False
    shell_allowed: bool = False
    allowlisted_commands: list[list[str]] | list[str] = field(default_factory=list)
    allowlisted_write_paths: list[str] = field(default_factory=list)
    blocked_write_paths: list[str] = field(default_factory=list)
    max_file_size_bytes: int = 1048576
    resolve_symlinks: bool = True
    require_governance_for_source_write: bool = True
    require_session_for_source_write: bool = True
    require_rollback_for_source_write: bool = True
    redact_secret_patterns: list[str] = field(default_factory=list)
    audit_enabled: bool = False
    audit_log_path: str = ""
    audit_level: str = "metadata"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class SandboxDecision:
    schema_version: str = "1.0"
    schema_id: str = "sandbox_decision.schema.json"
    decision_id: str = ""
    timestamp: str = ""
    source_component: str = "SecuritySandbox"
    operation: str = ""
    target: str | None = None
    decision: str = DECISION_BLOCK
    reason: str = ""
    applied_rule_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class SandboxViolation:
    schema_version: str = "1.0"
    schema_id: str = "sandbox_violation.schema.json"
    violation_id: str = ""
    timestamp: str = ""
    source_component: str = "SecuritySandbox"
    operation: str = ""
    target: str | None = None
    violation_type: str = ""
    severity: str = ""
    reason: str = ""
    decision_id: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class PathBoundaryResult:
    schema_version: str = "1.0"
    schema_id: str = "path_boundary_result.schema.json"
    result_id: str = ""
    timestamp: str = ""
    source_component: str = "PathBoundary"
    input_path: str = ""
    resolved_path: str | None = None
    repo_relative_path: str | None = None
    inside_repo: bool = False
    is_symlink: bool = False
    symlink_escape: bool = False
    is_l0: bool = False
    is_protected: bool = False
    operation: str = ""
    status: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = to_dict(self)
        d.pop("resolved_path", None)
        return d


@dataclass
class SafeFileOperationResult:
    schema_version: str = "1.0"
    schema_id: str = "safe_file_operation.schema.json"
    operation_id: str = ""
    timestamp: str = ""
    source_component: str = "SafeFileOps"
    operation: str = ""
    target_path: str = ""
    status: str = ""
    before_hash: str | None = None
    after_hash: str | None = None
    bytes_read: int = 0
    bytes_written: int = 0
    decision_id: str = ""
    content: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = to_dict(self)
        return d


@dataclass
class SafeSubprocessResult:
    schema_version: str = "1.0"
    schema_id: str = "safe_subprocess_result.schema.json"
    result_id: str = ""
    timestamp: str = ""
    source_component: str = "SafeSubprocess"
    command: list[str] = field(default_factory=list)
    working_directory: str | None = None
    status: str = ""
    reason: str = ""
    timeout_seconds: int = 0
    stdout_redacted: str | None = None
    stderr_redacted: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = to_dict(self)
        d["command"] = list(self.command)
        return d


@dataclass
class NetworkPolicyResult:
    schema_version: str = "1.0"
    schema_id: str = "network_policy_result.schema.json"
    result_id: str = ""
    timestamp: str = ""
    source_component: str = "NetworkPolicy"
    target: str | None = None
    status: str = ""
    reason: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class SecretRedactionResult:
    schema_version: str = "1.0"
    schema_id: str = "secret_redaction_result.schema.json"
    result_id: str = ""
    timestamp: str = ""
    source_component: str = "SecretRedactor"
    status: str = ""
    redacted_text: str = ""
    redaction_count: int = 0
    redaction_types: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)
