import json
import os
from pathlib import Path

from .doc_models import (
    DocumentScanReport,
    DocumentSyncPlan,
    DocumentSyncResult,
    DocumentDriftRecord,
    DocumentLinkRecord,
    DocumentStalenessRecord,
    DocumentationSyncEvidenceManifest,
    DocumentationSyncCommandResult,
    DocumentationSyncCompletionRecord,
    CENTRAL_STATUS_NOT_RUN,
    sha256_file,
    new_id,
    to_dict,
)

RUNTIME_ROOT = ".agentx-init/docs_sync"


def _ensure_dir(repo_root: Path) -> Path:
    path = repo_root / RUNTIME_ROOT
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json_atomic(path: Path, payload: dict) -> dict:
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    tmp.replace(path)
    return {"path": str(path), "status": "written"}


def sha256_evidence_file(path: Path) -> str:
    if path.exists():
        return sha256_file(path)
    return ""


def write_scan_report(repo_root: Path, scan_report: DocumentScanReport) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "documentation_scan_result.json"
    data = _serialize(to_dict(scan_report))
    return write_json_atomic(path, data)


def write_drift_report(
    repo_root: Path, drift_records: list[DocumentDriftRecord]
) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "documentation_drift_report.json"
    data = [_serialize(to_dict(r)) for r in drift_records]
    return write_json_atomic(path, {"drift_records": data, "count": len(data)})


def write_link_report(
    repo_root: Path, link_records: list[DocumentLinkRecord]
) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "broken_link_report.json"
    data = [_serialize(to_dict(r)) for r in link_records]
    return write_json_atomic(path, {"link_records": data, "count": len(data)})


def write_staleness_report(
    repo_root: Path, staleness_records: list[DocumentStalenessRecord]
) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "document_staleness_report.json"
    data = [_serialize(to_dict(r)) for r in staleness_records]
    return write_json_atomic(path, {"staleness_records": data, "count": len(data)})


def write_sync_plan(repo_root: Path, plan: DocumentSyncPlan) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "documentation_sync_plan.json"
    data = _serialize(to_dict(plan))
    return write_json_atomic(path, data)


def write_sync_result(repo_root: Path, result: DocumentSyncResult) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "documentation_sync_result.json"
    data = _serialize(to_dict(result))
    return write_json_atomic(path, data)


def write_evidence_manifest(
    repo_root: Path, manifest: DocumentationSyncEvidenceManifest
) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "documentation_evidence_manifest.json"
    data = _serialize(to_dict(manifest))
    return write_json_atomic(path, data)


def write_command_result(
    repo_root: Path, command_result: DocumentationSyncCommandResult
) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / f"command_result_{command_result.command_id}.json"
    data = _serialize(to_dict(command_result))
    return write_json_atomic(path, data)


def write_completion_record(
    repo_root: Path, completion_record: DocumentationSyncCompletionRecord
) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "documentation_completion_record.json"
    data = _serialize(to_dict(completion_record))
    return write_json_atomic(path, data)


def write_registry_report(repo_root: Path, registry: dict) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "documentation_registry.json"
    return write_json_atomic(path, registry)


def write_manual_protection_report(repo_root: Path, protection_result: dict) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "manual_doc_protection_report.json"
    return write_json_atomic(path, protection_result)


def write_generated_sync_report(repo_root: Path, generated_sync_result: dict) -> dict:
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "generated_doc_sync_report.json"
    return write_json_atomic(path, generated_sync_result)


def append_change_history_line(repo_root: Path, record: dict) -> dict:
    import json
    out_dir = _ensure_dir(repo_root)
    path = out_dir / "documentation_change_history.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")
    return {"path": str(path), "status": "appended"}


def _serialize(data):
    if isinstance(data, dict):
        return {k: _serialize(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_serialize(v) for v in data]
    if hasattr(data, "__dict__"):
        return {k: _serialize(v) for k, v in data.__dict__.items() if not k.startswith("_")}
    return data
