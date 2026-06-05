"""Append-only evidence recording for the Governed Patch Execution Layer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentx_evolve.patch_execution.patch_models import (
    ImplementationSession,
    PatchApplication,
    PatchResult,
    SourceChangeGuardResult,
    ImplementationValidationGateResult,
    RollbackRecord,
    to_dict,
    utc_now_iso,
)
from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat

SCHEMA_VERSION = "1.0"

EVIDENCE_DIR = ".agentx-init/implementation"
MEMORY_DIR = ".agentx-init/memory"

IMPLEMENTATION_HISTORY_FILE = "implementation_history.jsonl"
IMPLEMENTATION_EVIDENCE_FILE = "implementation_evidence.jsonl"
PATCH_APPLICATIONS_FILE = "patch_applications.jsonl"
SOURCE_CHANGE_GUARD_FILE = "source_change_guard_results.jsonl"
VALIDATION_GATE_FILE = "validation_gate_results.jsonl"
ROLLBACK_HISTORY_FILE = "rollback_history.jsonl"
AUDIT_EVENTS_FILE = "audit_events.jsonl"


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _atomic_write_json(data: dict, path: Path) -> dict:
    _ensure_dir(path)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)
    return {"status": "written", "path": str(path), "timestamp": utc_now_iso()}


def _append_jsonl(data: dict, path: Path) -> dict:
    _ensure_dir(path)
    with open(path, "a") as f:
        f.write(json.dumps(data) + "\n")
    return {"status": "written", "path": str(path), "timestamp": data.get("timestamp", utc_now_iso())}


def _evidence_entry(event: str, data: dict) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now_iso(),
        "event": event,
        "data": data,
    }


def _append_evidence(
    event_name: str,
    obj: object,
    specific_rel: str,
    repo_root: Path,
    compat: InitiatorPatchCompat | None = None,
) -> dict:
    data = to_dict(obj)
    entry = _evidence_entry(event_name, data)
    specific_path = repo_root / EVIDENCE_DIR / specific_rel
    evidence_path = repo_root / EVIDENCE_DIR / IMPLEMENTATION_EVIDENCE_FILE
    result = _append_jsonl(entry, specific_path)
    _append_jsonl(entry, evidence_path)
    return result


def append_implementation_history(
    session: ImplementationSession,
    repo_root: Path,
    compat: InitiatorPatchCompat | None = None,
) -> dict:
    return _append_evidence(
        "implementation_history",
        session,
        IMPLEMENTATION_HISTORY_FILE,
        repo_root,
        compat,
    )


def append_patch_application(
    application: PatchApplication | PatchResult,
    repo_root: Path,
    compat: InitiatorPatchCompat | None = None,
) -> dict:
    return _append_evidence(
        "patch_application",
        application,
        PATCH_APPLICATIONS_FILE,
        repo_root,
        compat,
    )


def append_source_change_guard_result(
    result: SourceChangeGuardResult,
    repo_root: Path,
    compat: InitiatorPatchCompat | None = None,
) -> dict:
    return _append_evidence(
        "source_change_guard_result",
        result,
        SOURCE_CHANGE_GUARD_FILE,
        repo_root,
        compat,
    )


def append_validation_gate_result(
    result: ImplementationValidationGateResult,
    repo_root: Path,
    compat: InitiatorPatchCompat | None = None,
) -> dict:
    return _append_evidence(
        "validation_gate_result",
        result,
        VALIDATION_GATE_FILE,
        repo_root,
        compat,
    )


def append_rollback_record(
    record: RollbackRecord,
    repo_root: Path,
    compat: InitiatorPatchCompat | None = None,
) -> dict:
    return _append_evidence(
        "rollback_record",
        record,
        ROLLBACK_HISTORY_FILE,
        repo_root,
        compat,
    )


def write_latest_artifact(
    name: str,
    artifact: dict,
    repo_root: Path,
    compat: InitiatorPatchCompat | None = None,
) -> dict:
    path = repo_root / EVIDENCE_DIR / f"latest_{name}.json"
    timestamp = utc_now_iso()
    data = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": timestamp,
        "event": f"latest_{name}",
        "data": artifact,
    }
    if compat:
        compat_result = compat.write_json_atomic(path, data)
        if not compat_result.get("success"):
            _atomic_write_json(data, path)
    else:
        _atomic_write_json(data, path)
    evidence_path = repo_root / EVIDENCE_DIR / IMPLEMENTATION_EVIDENCE_FILE
    _append_jsonl(data, evidence_path)
    return {"status": "written", "path": str(path), "timestamp": timestamp}


def build_patch_execution_audit_event(
    session: ImplementationSession,
    event_type: str,
    decision: str,
    artifacts: list[str],
) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now_iso(),
        "event": "patch_execution_audit_event",
        "data": {
            "session_id": session.session_id,
            "event_type": event_type,
            "decision": decision,
            "artifacts": artifacts,
        },
    }
