from __future__ import annotations

import json
from pathlib import Path
from agentx_evolve.prompts.prompt_models import (
    PromptRegistry,
    PromptVersion,
    PromptRuntimeBinding,
    PromptDiffRecord,
    PromptMigrationRecord,
    PromptAuditEvent,
    to_dict,
    redact_prompt_text,
    sha256_text,
    sha256_dict,
)


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _append_jsonl(filepath: Path, data: dict) -> None:
    with open(filepath, "a") as f:
        f.write(json.dumps(data, default=str) + "\n")


def _write_atomic_json(filepath: Path, data: dict) -> None:
    tmp = filepath.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, default=str)
    tmp.rename(filepath)


_REDACT_MAX = 2000


def _redacted_body(binding: PromptRuntimeBinding) -> str:
    return redact_prompt_text(binding.prompt_body_sha256 or "", _REDACT_MAX)


def append_prompt_audit_event(
    event: PromptAuditEvent, repo_root: Path
) -> dict:
    d = to_dict(event)
    artifact_dir = _ensure_dir(repo_root / ".agentx-init" / "prompts")
    _append_jsonl(artifact_dir / "prompt_registry_history.jsonl", d)
    return d


def append_prompt_registry_event(
    registry: PromptRegistry, repo_root: Path
) -> dict:
    d = to_dict(registry)
    artifact_dir = _ensure_dir(repo_root / ".agentx-init" / "prompts")
    _append_jsonl(artifact_dir / "prompt_registry_history.jsonl", d)
    return d


def append_prompt_version_event(
    version: PromptVersion, repo_root: Path
) -> dict:
    d = to_dict(version)
    artifact_dir = _ensure_dir(repo_root / ".agentx-init" / "prompts")
    _append_jsonl(artifact_dir / "prompt_version_history.jsonl", d)
    return d


def append_prompt_binding_event(
    binding: PromptRuntimeBinding, repo_root: Path
) -> dict:
    d = to_dict(binding)
    artifact_dir = _ensure_dir(repo_root / ".agentx-init" / "prompts")
    _append_jsonl(artifact_dir / "prompt_binding_history.jsonl", d)
    return d


def append_prompt_diff_event(
    diff_record: PromptDiffRecord, repo_root: Path
) -> dict:
    d = to_dict(diff_record)
    artifact_dir = _ensure_dir(repo_root / ".agentx-init" / "prompts")
    _append_jsonl(artifact_dir / "prompt_diff_history.jsonl", d)
    return d


def append_prompt_migration_event(
    migration: PromptMigrationRecord, repo_root: Path
) -> dict:
    d = to_dict(migration)
    artifact_dir = _ensure_dir(repo_root / ".agentx-init" / "prompts")
    _append_jsonl(artifact_dir / "prompt_migration_history.jsonl", d)
    return d


def append_prompt_safety_event(
    event: dict, repo_root: Path
) -> dict:
    artifact_dir = _ensure_dir(repo_root / ".agentx-init" / "prompts")
    _append_jsonl(artifact_dir / "prompt_safety_history.jsonl", event)
    return event


def write_latest_prompt_binding(
    binding: PromptRuntimeBinding, repo_root: Path
) -> dict:
    d = to_dict(binding)
    if d.get("warnings") is None:
        d["warnings"] = []
    if "prompt_body" in d:
        del d["prompt_body"]
    artifact_dir = _ensure_dir(repo_root / ".agentx-init" / "prompts")
    _write_atomic_json(artifact_dir / "latest_prompt_binding.json", d)
    return d


def write_prompt_evidence_manifest(
    evidence: dict, repo_root: Path
) -> dict:
    artifact_dir = _ensure_dir(repo_root / ".agentx-init" / "prompts")
    path = artifact_dir / "prompt_contract_versioning_evidence_manifest.json"
    _write_atomic_json(path, evidence)
    return evidence


def write_prompt_completion_record(
    record: dict, repo_root: Path
) -> dict:
    artifact_dir = _ensure_dir(repo_root / ".agentx-init" / "prompts")
    path = artifact_dir / "prompt_contract_versioning_completion_record.json"
    _write_atomic_json(path, record)
    return record
