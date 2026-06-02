"""PM2: Generate architecture report from latest scan."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
from agentx_initiator.core.path_registry import get_path
from agentx_initiator.core.architecture_analyzer import analyze_scan
from agentx_initiator.core.schema_validation import validate_instance
from agentx_initiator.core.report_writer import render_architecture_report
from agentx_initiator.core.audit_log import append_event
from agentx_initiator.cli.models import CLICommandResponse


def register(sub):
    p = sub.add_parser("report", help="Generate architecture report")
    p.set_defaults(func=run)


def run(args):
    snapshot_path = get_path("repo_scan_latest")
    if not snapshot_path.exists():
        resp = _response("report", "BLOCKED", 3,
                         "No repository scan found. Run agentx-init scan first.",
                         errors=[{"failure_class": "MISSING_SCAN"}])
        _print_response(resp)
        return resp

    try:
        scan_data = json.loads(snapshot_path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        resp = _response("report", "FAILED", 5, "Failed to read scan",
                         errors=[{"failure_class": "FILE_READ_ERROR", "detail": str(e)}])
        _print_response(resp)
        return resp

    from agentx_initiator.core.repo_model import RepositoryScanResult, RepositoryFileRecord, RepositoryDirectoryRecord, RepositoryFingerprint

    files = [RepositoryFileRecord(**f) if isinstance(f, dict) else f for f in scan_data.get("files", [])]
    directories = [RepositoryDirectoryRecord(**d) if isinstance(d, dict) else d for d in scan_data.get("directories", [])]
    fp_data = scan_data.get("repository_fingerprint")
    fingerprint = RepositoryFingerprint(**fp_data) if fp_data else None

    scan_result = RepositoryScanResult(
        scan_id=scan_data.get("scan_id", ""),
        timestamp=scan_data.get("timestamp", ""),
        repo_root=scan_data.get("repo_root", ""),
        scanner_version=scan_data.get("scanner_version", ""),
        status=scan_data.get("status", "PASS"),
        files=files, directories=directories,
        repository_fingerprint=fingerprint,
        warnings=scan_data.get("warnings", []),
        errors=scan_data.get("errors", []),
    )

    arch_result = analyze_scan(scan_result)

    arch_validation = validate_instance(arch_result.to_dict(), "architecture_report.schema.json")
    if not arch_validation.valid:
        resp = _response("report", "FAILED", 5,
                         "Architecture report failed schema validation",
                         errors=[{"failure_class": "INVALID_SCHEMA", "detail": arch_validation.errors}])
        _print_response(resp)
        return resp

    arch_path = get_path("architecture_latest")
    arch_path.parent.mkdir(parents=True, exist_ok=True)
    arch_path.write_text(json.dumps(arch_result.to_dict(), indent=2, default=str))

    report_content = render_architecture_report(arch_result.to_dict())
    report_path = get_path("reports_dir") / "architecture_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_content)

    append_event({
        "event_type": "report",
        "category": "ARCHITECTURE",
        "status": "SUCCESS",
        "summary": f"Architecture report: {len(arch_result.layer_summary)} layers, {arch_result.total_files} files",
        "component": "report_command",
        "artifact_refs": [str(arch_path), str(report_path)],
    })

    resp = _response("report", "SUCCESS", 0,
                     f"Architecture report generated: {arch_result.total_files} files, {arch_result.protected_count} protected.",
                     data={"layer_summary": arch_result.layer_summary, "total_files": arch_result.total_files},
                     artifact_refs=[str(arch_path), str(report_path)],
                     warnings=arch_result.warnings)
    _print_response(resp)
    return resp


def _response(command, status, exit_code, message, data=None, artifact_refs=None, warnings=None, errors=None):
    return CLICommandResponse(
        response_id=str(uuid4()),
        request_id="cli-internal",
        timestamp=datetime.now(timezone.utc).isoformat(),
        command=command, status=status, exit_code=exit_code, message=message,
        data=data or {}, artifact_refs=artifact_refs or [],
        warnings=warnings or [], errors=errors or [],
    )


def _print_response(resp):
    print(resp.message)
    if resp.warnings:
        for w in resp.warnings:
            print(f"  Warning: {w}")
    if resp.errors:
        for e in resp.errors:
            print(f"  Error: {e.get('failure_class', 'UNKNOWN')}")
