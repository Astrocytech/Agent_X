from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    DependencyStatus,
    LLMWorkerContextPackage,
    LLMWorkerPromptPackage,
    LLMWorkerModelRequest,
    LLMWorkerModelResponse,
    ParsedModelOutput,
    ImplementationPlan,
    PatchProposal,
    ValidationHandoff,
    LLMWorkerResult,
    LLMWorkerAuditEvent,
    utc_now_iso,
    new_id,
    sha256_dict,
    redact_secret_like,
    to_dict,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    RUNTIME_ARTIFACT_ROOT,
)


def _ensure_dir(repo_root: Path) -> Path:
    artifact_dir = repo_root / RUNTIME_ARTIFACT_ROOT
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir


def _append_jsonl(filename: str, record: dict, repo_root: Path) -> dict:
    artifact_dir = _ensure_dir(repo_root)
    filepath = artifact_dir / filename
    line = json.dumps(record, sort_keys=True, separators=(",", ":"))
    with open(filepath, "a") as f:
        f.write(line + "\n")
    return {
        "path": str(filepath),
        "sha256": sha256_dict(record),
    }


def _write_json(filename: str, record: dict, repo_root: Path) -> dict:
    artifact_dir = _ensure_dir(repo_root)
    filepath = artifact_dir / filename
    content = json.dumps(record, sort_keys=True, separators=(",", ":"))
    tmp_path = filepath.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    tmp_path.rename(filepath)
    return {
        "path": str(filepath),
        "sha256": sha256_dict(record),
    }


def _safe_record(obj: Any) -> dict:
    data = to_dict(obj) if hasattr(obj, "to_dict") else dict(obj)
    result: dict = {}
    for k, v in data.items():
        if isinstance(v, str):
            result[k] = redact_secret_like(v)
        elif isinstance(v, list):
            result[k] = [
                redact_secret_like(item) if isinstance(item, str) else item
                for item in v
            ]
        else:
            result[k] = v
    return result


def append_worker_task(task: LLMWorkerTask, repo_root: Path) -> dict:
    return _append_jsonl("worker_task_history.jsonl", _safe_record(task), repo_root)


def append_dependency_status(status: DependencyStatus, repo_root: Path) -> dict:
    return _append_jsonl(
        "dependency_status_history.jsonl", _safe_record(status), repo_root
    )


def append_context_package(
    context_package: LLMWorkerContextPackage, repo_root: Path
) -> dict:
    return _append_jsonl(
        "context_package_history.jsonl", _safe_record(context_package), repo_root
    )


def append_prompt_package(
    prompt_package: LLMWorkerPromptPackage, repo_root: Path
) -> dict:
    return _append_jsonl(
        "prompt_package_history.jsonl", _safe_record(prompt_package), repo_root
    )


def append_model_request(
    model_request: LLMWorkerModelRequest, repo_root: Path
) -> dict:
    return _append_jsonl(
        "model_request_history.jsonl", _safe_record(model_request), repo_root
    )


def append_model_response(
    model_response: LLMWorkerModelResponse, repo_root: Path
) -> dict:
    return _append_jsonl(
        "model_response_history.jsonl", _safe_record(model_response), repo_root
    )


def append_parsed_model_output(
    parsed_output: ParsedModelOutput, repo_root: Path
) -> dict:
    return _append_jsonl(
        "model_output_history.jsonl", _safe_record(parsed_output), repo_root
    )


def append_implementation_plan(plan: ImplementationPlan, repo_root: Path) -> dict:
    return _append_jsonl(
        "implementation_plan_history.jsonl", _safe_record(plan), repo_root
    )


def append_patch_proposal(
    patch_proposal: PatchProposal, repo_root: Path
) -> dict:
    return _append_jsonl(
        "patch_proposal_history.jsonl", _safe_record(patch_proposal), repo_root
    )


def append_validation_handoff(
    handoff: ValidationHandoff, repo_root: Path
) -> dict:
    return _append_jsonl(
        "validation_handoff_history.jsonl", _safe_record(handoff), repo_root
    )


def append_worker_result(result: LLMWorkerResult, repo_root: Path) -> dict:
    return _append_jsonl(
        "worker_result_history.jsonl", _safe_record(result), repo_root
    )


def append_worker_audit(event: LLMWorkerAuditEvent, repo_root: Path) -> dict:
    return _append_jsonl(
        "worker_audit_history.jsonl", _safe_record(event), repo_root
    )


def write_latest_worker_result(result: LLMWorkerResult, repo_root: Path) -> dict:
    return _write_json(
        "latest_worker_result.json", _safe_record(result), repo_root
    )


def write_evidence_manifest(manifest: dict, repo_root: Path) -> dict:
    return _write_json(
        "llm_worker_evidence_manifest.json", manifest, repo_root
    )


def write_review_report(report: dict, repo_root: Path) -> dict:
    return _write_json("llm_worker_review_report.json", report, repo_root)


def write_completion_record(record: dict, repo_root: Path) -> dict:
    return _write_json("llm_worker_completion_record.json", record, repo_root)
