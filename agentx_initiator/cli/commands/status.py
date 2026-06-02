from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from agentx_initiator.core.path_registry import PathRegistry, get_path
from agentx_initiator.core.config import load_config
from agentx_initiator.core.repo_scanner import scan_repository
from agentx_initiator.core.architecture_analyzer import analyze_scan
from agentx_initiator.core.schema_validation import validate_instance
from agentx_initiator.core.report_writer import render_architecture_report
from agentx_initiator.core.audit_log import append_event
from agentx_initiator.cli.models import CLICommandResponse


def register(sub):
    p = sub.add_parser("status", help="Generate status report")
    p.add_argument("repo_root", nargs="?", default=".", help="Repository root path")
    p.set_defaults(func=run)


def run(args):
    repo_root_path = Path(args.repo_root).resolve()
    if not repo_root_path.exists():
        return _response("status", "FAILED", 1,
                         f"Repository root does not exist: {repo_root_path}",
                         errors=[{"failure_class": "PATH_NOT_FOUND"}])
    if not repo_root_path.is_dir():
        return _response("status", "FAILED", 1,
                         f"Repository root is not a directory: {repo_root_path}",
                         errors=[{"failure_class": "PATH_NOT_DIRECTORY"}])

    registry = PathRegistry(repo_root_path)
    registry.ensure_runtime_dirs()

    snapshot_path = get_path("repo_scan_latest")
    if not snapshot_path.exists():
        append_event({
            "event_type": "status",
            "category": "ARCHITECTURE",
            "status": "BLOCKED",
            "summary": "No scan found; status blocked",
            "component": "status_command",
        })
        resp = _response("status", "BLOCKED", 3,
                         "No repository scan found. Run agentx-init scan first.",
                         errors=[{"failure_class": "MISSING_SCAN"}])
        _print_response(resp)
        return resp

    try:
        scan_data = json.loads(snapshot_path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return _response("status", "FAILED", 5,
                         "Failed to read scan artifact",
                         errors=[{"failure_class": "FILE_READ_ERROR",
                                  "detail": str(e)}])

    scan_validation = validate_instance(scan_data, "repo_scan.schema.json")
    if not scan_validation.valid:
        return _response("status", "BLOCKED", 3,
                         "Invalid scan artifact",
                         errors=[{"failure_class": "INVALID_SCAN",
                                  "detail": scan_validation.errors}])

    from agentx_initiator.core.repo_model import RepositoryScanResult
    from agentx_initiator.core.repo_model import (
        RepositoryFileRecord, RepositoryDirectoryRecord, RepositoryFingerprint,
    )

    files = [
        RepositoryFileRecord(**f) if isinstance(f, dict) else f
        for f in scan_data.get("files", [])
    ]
    directories = [
        RepositoryDirectoryRecord(**d) if isinstance(d, dict) else d
        for d in scan_data.get("directories", [])
    ]
    fp_data = scan_data.get("repository_fingerprint")
    fingerprint = RepositoryFingerprint(**fp_data) if fp_data else None

    scan_result = RepositoryScanResult(
        scan_id=scan_data.get("scan_id", ""),
        timestamp=scan_data.get("timestamp", ""),
        repo_root=scan_data.get("repo_root", ""),
        scanner_version=scan_data.get("scanner_version", ""),
        status=scan_data.get("status", "PASS"),
        files=files,
        directories=directories,
        repository_fingerprint=fingerprint,
        warnings=scan_data.get("warnings", []),
        errors=scan_data.get("errors", []),
    )

    arch_result = analyze_scan(scan_result)

    arch_validation = validate_instance(arch_result.to_dict(), "architecture_report.schema.json")
    if not arch_validation.valid:
        return _response("status", "FAILED", 5,
                         "Architecture report failed schema validation",
                         errors=[{"failure_class": "INVALID_SCHEMA",
                                  "detail": arch_validation.errors}])

    arch_path = get_path("architecture_latest")
    arch_path.parent.mkdir(parents=True, exist_ok=True)
    arch_path.write_text(json.dumps(arch_result.to_dict(), indent=2, default=str))

    report_content = render_architecture_report(arch_result.to_dict())
    report_path = get_path("latest_status_report")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_content)

    arch_history_path = get_path("memory_dir") / "architecture_history.jsonl"
    try:
        with open(arch_history_path, "a") as f:
            f.write(json.dumps(arch_result.to_dict(), default=str) + "\n")
    except OSError:
        pass

    audit_result = append_event({
        "event_type": "status",
        "category": "ARCHITECTURE",
        "status": "PASS",
        "summary": f"Status report: {len(arch_result.layer_summary)} layers, "
                   f"{arch_result.total_files} files",
        "component": "status_command",
        "artifact_refs": [
            str(arch_path),
            str(report_path),
            str(get_path("audit_events_file")),
        ],
    })

    _append_command_history("status", {}, {
        "layer_count": len(arch_result.layer_summary),
        "total_files": arch_result.total_files,
        "protected_count": arch_result.protected_count,
    }, audit_result.event_id)

    resp = _response(
        "status",
        "SUCCESS" if arch_result.status == "PASS" else "PARTIAL",
        0 if arch_result.status == "PASS" else 4,
        f"Status report generated. {arch_result.total_files} files, "
        f"{arch_result.protected_count} protected.",
        data={
            "layer_summary": arch_result.layer_summary,
            "total_files": arch_result.total_files,
            "protected_count": arch_result.protected_count,
        },
        artifact_refs=[
            str(arch_path),
            str(report_path),
            str(get_path("audit_events_file")),
        ],
        warnings=arch_result.warnings,
        errors=[{"failure_class": "ARCHITECTURE_ERROR",
                 "detail": e} for e in arch_result.errors],
    )
    _print_response(resp)
    return resp


def _response(command: str, status: str, exit_code: int, message: str,
              data: dict | None = None,
              artifact_refs: list[str] | None = None,
              warnings: list[str] | None = None,
              errors: list[dict] | None = None) -> CLICommandResponse:
    return CLICommandResponse(
        response_id=str(uuid4()),
        request_id="cli-internal",
        timestamp=datetime.now(timezone.utc).isoformat(),
        command=command,
        status=status,
        exit_code=exit_code,
        message=message,
        data=data or {},
        artifact_refs=artifact_refs or [],
        warnings=warnings or [],
        errors=errors or [],
    )


def _print_response(resp: CLICommandResponse):
    import sys
    print(resp.message)
    if resp.warnings:
        for w in resp.warnings:
            print(f"  Warning: {w}")
    if resp.errors:
        for e in resp.errors:
            print(f"  Error: {e.get('failure_class', 'UNKNOWN')}")


def _append_command_history(command: str, request: dict, response_data: dict,
                             audit_event_id: str | None = None):
    try:
        history_path = get_path("command_history_file")
        history_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "schema_version": "1.0",
            "history_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request": {"command": command, **request},
            "response": response_data,
            "governance_ref": None,
            "audit_event_id": audit_event_id,
        }
        with open(history_path, "a") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass
