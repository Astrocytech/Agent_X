from __future__ import annotations
from pathlib import Path
from agentx_evolve.security.security_models import SandboxPolicy, new_id


def default_sandbox_policy(repo_root: Path) -> SandboxPolicy:
    return SandboxPolicy(
        policy_id=new_id("policy"),
        repo_root=str(repo_root.resolve()),
        runtime_state_root=".agentx-init",
        protected_paths=["L0/", "agent_x/runtime/", "core/"],
        source_write_allowed=False,
        runtime_write_allowed=True,
        network_allowed=False,
        shell_allowed=False,
        allowlisted_commands=[],
        allowlisted_write_paths=[".agentx-init/"],
        blocked_write_paths=["L0/"],
        max_file_size_bytes=1048576,
        resolve_symlinks=True,
        require_governance_for_source_write=True,
        require_session_for_source_write=True,
        require_rollback_for_source_write=True,
        redact_secret_patterns=[],
        audit_enabled=False,
        audit_log_path="",
        audit_level="metadata",
        warnings=[],
        errors=[],
    )


def load_sandbox_policy_from_dict(
    data: dict, repo_root: Path | None = None
) -> SandboxPolicy:
    kwargs = {}
    field_names = {
        "schema_version", "schema_id", "policy_id", "repo_root",
        "runtime_state_root", "protected_paths", "source_write_allowed",
        "runtime_write_allowed", "network_allowed", "shell_allowed",
        "allowlisted_commands", "allowlisted_write_paths",
        "blocked_write_paths", "max_file_size_bytes", "resolve_symlinks",
        "require_governance_for_source_write", "require_session_for_source_write",
        "require_rollback_for_source_write", "redact_secret_patterns",
        "audit_enabled", "audit_log_path", "audit_level",
        "warnings", "errors",
    }
    for k, v in data.items():
        if k in field_names:
            kwargs[k] = v
    policy = SandboxPolicy(**kwargs)
    if repo_root is not None:
        policy.repo_root = str(repo_root.resolve())
    if not policy.policy_id:
        policy.policy_id = new_id("policy")
    return policy


def merge_sandbox_policy(base: SandboxPolicy, override: dict) -> SandboxPolicy:
    merged_protected = list(base.protected_paths)
    merged_blocked = list(base.blocked_write_paths)

    kwargs = {
        "schema_version": base.schema_version,
        "schema_id": base.schema_id,
        "policy_id": base.policy_id,
        "repo_root": base.repo_root,
        "runtime_state_root": base.runtime_state_root,
        "protected_paths": merged_protected,
        "source_write_allowed": base.source_write_allowed,
        "runtime_write_allowed": base.runtime_write_allowed,
        "network_allowed": base.network_allowed,
        "shell_allowed": base.shell_allowed,
        "allowlisted_commands": list(base.allowlisted_commands),
        "allowlisted_write_paths": list(base.allowlisted_write_paths),
        "blocked_write_paths": merged_blocked,
        "max_file_size_bytes": base.max_file_size_bytes,
        "resolve_symlinks": base.resolve_symlinks,
        "require_governance_for_source_write": base.require_governance_for_source_write,
        "require_session_for_source_write": base.require_session_for_source_write,
        "require_rollback_for_source_write": base.require_rollback_for_source_write,
        "redact_secret_patterns": list(base.redact_secret_patterns),
        "audit_enabled": base.audit_enabled,
        "audit_log_path": base.audit_log_path,
        "audit_level": base.audit_level,
        "warnings": list(base.warnings),
        "errors": list(base.errors),
    }

    for k, v in override.items():
        if k in ("protected_paths", "blocked_write_paths"):
            existing = set(kwargs.get(k, []))
            for item in v:
                if item not in existing:
                    kwargs.setdefault(k, []).append(item)
        elif k in kwargs:
            kwargs[k] = v

    return SandboxPolicy(**kwargs)


def is_runtime_path(path: Path, repo_root: Path, policy: SandboxPolicy) -> bool:
    try:
        resolved = path.resolve()
        runtime = (repo_root.resolve() / policy.runtime_state_root).resolve()
        resolved.relative_to(runtime)
        return True
    except (ValueError, OSError):
        return False


def is_protected_path(repo_relative_path: str, policy: SandboxPolicy) -> bool:
    path = repo_relative_path.rstrip("/")
    for protected in policy.protected_paths:
        p = protected.rstrip("/")
        if path == p or path.startswith(p + "/") or path == p:
            return True
    return False


def is_l0_path(repo_relative_path: str) -> bool:
    return repo_relative_path.startswith("L0/") or repo_relative_path == "L0"
