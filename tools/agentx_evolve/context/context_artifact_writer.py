from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any

from agentx_evolve.context.context_models import (
    TaskPack, ContextPack,
    stable_hash, utc_now_iso,
    TP_READY,
)
from agentx_evolve.context.task_pack_validator import validate_task_pack


RUNTIME_ARTIFACT_ROOT = ".agentx-init/context_packs"


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, data: dict) -> None:
    _ensure_dir(path)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, default=str)
    tmp.replace(path)


def _append_jsonl(path: Path, data: dict) -> None:
    _ensure_dir(path)
    with open(path, "a") as f:
        f.write(json.dumps(data, default=str) + "\n")


def write_context_pack_artifacts(
    task_pack: TaskPack,
    repo_root: Path,
    skip_validation: bool = False,
) -> dict[str, Any]:
    artifact_root = repo_root / RUNTIME_ARTIFACT_ROOT
    artifact_root.mkdir(parents=True, exist_ok=True)

    validation = validate_task_pack(task_pack)
    validation_passed = validation["status"] == TP_READY or skip_validation

    cp = task_pack.context_pack
    cp_path = artifact_root / "latest_context_pack.json"
    tp_path = artifact_root / "latest_task_pack.json"

    cp_data = {
        "context_pack_id": cp.context_pack_id if cp else "",
        "created_at": cp.created_at if cp else "",
        "task_input_id": cp.task_input_id if cp else "",
        "max_context_tokens": cp.max_context_tokens if cp else 0,
        "reserved_output_tokens": cp.reserved_output_tokens if cp else 0,
        "available_input_tokens": cp.available_input_tokens if cp else 0,
        "total_estimated_tokens": cp.total_estimated_tokens if cp else 0,
        "included_count": len(cp.included_items) if cp else 0,
        "excluded_count": len(cp.excluded_items) if cp else 0,
        "summary_count": len(cp.summary_items) if cp else 0,
    } if cp else {}

    _atomic_write(cp_path, cp_data)
    if validation_passed:
        _atomic_write(tp_path, {
            "task_pack_id": task_pack.task_pack_id,
            "created_at": task_pack.created_at,
            "status": task_pack.status,
            "context_pack_id": cp.context_pack_id if cp else "",
            "allowed_tools": task_pack.allowed_tools,
            "blocked_tools": task_pack.blocked_tools,
            "errors": task_pack.errors,
        })

    _append_jsonl(artifact_root / "context_pack_history.jsonl", cp_data)
    _append_jsonl(artifact_root / "task_pack_history.jsonl", {
        "task_pack_id": task_pack.task_pack_id,
        "created_at": task_pack.created_at,
        "error_count": len(task_pack.errors),
    })

    cp_hash = stable_hash(cp_data) if cp_data else "NOT_EMITTED"

    evidence = {
        "schema_version": "1.0",
        "schema_id": "context_pack_evidence.schema.json",
        "component_id": "AGENTX_CONTEXT_BUILDER_TASK_PACKER",
        "validated_commit": "",
        "validated_at": utc_now_iso(),
        "context_pack_id": cp.context_pack_id if cp else "",
        "context_pack_hash": cp_hash,
        "evidence_files": [str(cp_path), str(tp_path)],
        "evidence_file_hashes": [
            {"path": str(cp_path), "sha256": stable_hash(str(cp_data))},
            {"path": str(tp_path), "sha256": stable_hash(str(task_pack.task_pack_id))},
        ],
    }
    _atomic_write(artifact_root / "context_pack_evidence.json", evidence)

    return {
        "artifact_root": str(artifact_root),
        "context_pack_path": str(cp_path),
        "task_pack_path": str(tp_path),
        "evidence_path": str(artifact_root / "context_pack_evidence.json"),
        "context_pack_hash": cp_hash,
    }


def append_context_pack_history(task_pack: TaskPack, repo_root: Path) -> dict[str, Any]:
    artifact_root = repo_root / RUNTIME_ARTIFACT_ROOT
    cp = task_pack.context_pack
    record = {
        "task_pack_id": task_pack.task_pack_id,
        "created_at": task_pack.created_at,
        "context_pack_id": cp.context_pack_id if cp else "",
        "model_profile_id": cp.model_profile_id if cp else None,
        "total_estimated_tokens": cp.total_estimated_tokens if cp else 0,
    }
    _append_jsonl(artifact_root / "context_pack_history.jsonl", record)
    return {"status": "appended"}


def write_latest_context_pack(task_pack: TaskPack, repo_root: Path) -> dict[str, Any]:
    artifact_root = repo_root / RUNTIME_ARTIFACT_ROOT
    cp = task_pack.context_pack
    data = {
        "task_pack_id": task_pack.task_pack_id,
        "context_pack_id": cp.context_pack_id if cp else "",
        "included_count": len(cp.included_items) if cp else 0,
        "excluded_count": len(cp.excluded_items) if cp else 0,
        "total_estimated_tokens": cp.total_estimated_tokens if cp else 0,
    } if cp else {}
    _atomic_write(artifact_root / "latest_context_pack.json", data)
    return {"context_pack_path": str(artifact_root / "latest_context_pack.json")}


def write_context_pack_evidence(evidence_record: dict, repo_root: Path) -> dict[str, Any]:
    artifact_root = repo_root / RUNTIME_ARTIFACT_ROOT
    path = artifact_root / "context_pack_evidence.json"
    _atomic_write(path, evidence_record)
    return {"evidence_path": str(path)}


def write_review_report(review_data: dict, repo_root: Path) -> dict[str, Any]:
    artifact_root = repo_root / RUNTIME_ARTIFACT_ROOT
    artifact_root.mkdir(parents=True, exist_ok=True)
    path = artifact_root / "context_builder_review_report.json"
    data = {
        "schema_version": "1.0",
        "schema_id": "context_builder_review_report.schema.json",
        "component_id": "AGENTX_CONTEXT_BUILDER_TASK_PACKER",
        **review_data,
    }
    _atomic_write(path, data)
    return {"review_report_path": str(path), "sha256": stable_hash(str(data))}


def write_completion_record(record_data: dict, repo_root: Path) -> dict[str, Any]:
    artifact_root = repo_root / RUNTIME_ARTIFACT_ROOT
    artifact_root.mkdir(parents=True, exist_ok=True)
    path = artifact_root / "context_builder_completion_record.json"
    data = {
        "schema_version": "1.0",
        "schema_id": "completion_record.schema.json",
        "component_id": "AGENTX_CONTEXT_BUILDER_TASK_PACKER",
        **record_data,
    }
    _atomic_write(path, data)
    return {"completion_record_path": str(path), "sha256": stable_hash(str(data))}
