from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from agentx_initiator.core.path_registry import PathRegistry, get_path
from agentx_initiator.core.config_model import ConfigRecord
from agentx_initiator.core.config import load_config
from agentx_initiator.core.repo_scanner import scan_repository, SCANNER_VERSION
from agentx_initiator.core.schema_validation import validate_instance
from agentx_initiator.core.audit_log import append_event
from agentx_initiator.cli.models import CLICommandResponse


def register(sub):
    p = sub.add_parser("scan", help="Scan repository structure and layers")
    p.add_argument("repo_root", nargs="?", default=".", help="Repository root path")
    p.set_defaults(func=run)


def run(args):
    repo_root_path = Path(args.repo_root).resolve()
    if not repo_root_path.exists():
        resp = _response("scan", "FAILED", 1,
                         f"Repository root does not exist: {repo_root_path}",
                         errors=[{"failure_class": "PATH_NOT_FOUND"}])
        _print_response(resp)
        return resp
    if not repo_root_path.is_dir():
        resp = _response("scan", "FAILED", 1,
                         f"Repository root is not a directory: {repo_root_path}",
                         errors=[{"failure_class": "PATH_NOT_DIRECTORY"}])
        _print_response(resp)
        return resp

    registry = PathRegistry(repo_root_path)
    registry.ensure_runtime_dirs()

    config = load_config()
    if hasattr(config, "model_dump"):
        config_dict = config.model_dump()
    elif hasattr(config, "to_dict"):
        config_dict = config.to_dict()
    elif isinstance(config, dict):
        config_dict = config
    else:
        config_dict = {"agentx_init": {}}
    scan_cfg = config_dict.get("agentx_init", config_dict)
    ignore_dirs = set(scan_cfg.get("scan", {}).get("ignore_dirs", [
        ".git", "__pycache__", ".venv", "node_modules", ".agentx-init"
    ]))
    max_size_mb = scan_cfg.get("scan", {}).get("max_file_size_mb", 5)
    include_hidden = scan_cfg.get("scan", {}).get("include_hidden", False)

    scan_result = scan_repository(
        root=repo_root_path,
        ignore_dirs=ignore_dirs,
        max_file_size=max_size_mb * 1024 * 1024,
        include_hidden=include_hidden,
    )

    validation = validate_instance(scan_result.to_dict(), "repo_scan.schema.json")
    if not validation.valid:
        append_event({
            "event_type": "scan",
            "category": "SCAN",
            "status": "FAILED",
            "summary": "Scan artifact failed schema validation",
            "component": "scan_command",
            "artifact_refs": [],
        })
        resp = _response("scan", "FAILED", 5,
                         "Scan artifact failed validation",
                         errors=[{"failure_class": "INVALID_SCHEMA",
                                  "detail": validation.errors}])
        _print_response(resp)
        return resp

    snapshot_path = get_path("repo_scan_latest")
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps(scan_result.to_dict(), indent=2, default=str)
    )

    scans_path = get_path("scans_history")
    scans_path.parent.mkdir(parents=True, exist_ok=True)
    with open(scans_path, "a") as f:
        f.write(json.dumps(scan_result.to_dict(), default=str) + "\n")

    audit_result = append_event({
        "event_type": "scan",
        "category": "SCAN",
        "status": "PASS" if scan_result.status == "PASS" else "PARTIAL",
        "summary": f"Scanned {scan_result.total_files} files, "
                   f"{len(scan_result.directories)} directories",
        "component": "scan_command",
        "artifact_refs": [
            str(snapshot_path),
            str(scans_path),
            str(get_path("audit_events_file")),
        ],
    })

    _append_command_history("scan", {}, {
        "status": scan_result.status,
        "total_files": scan_result.total_files,
    }, audit_result.event_id)

    resp = _response(
        "scan",
        "SUCCESS" if scan_result.status == "PASS" else "PARTIAL",
        0 if scan_result.status == "PASS" else 4,
        f"Repository scan completed. {scan_result.total_files} files, "
        f"{len(scan_result.directories)} directories.",
        data={
            "scan_id": scan_result.scan_id,
            "total_files": scan_result.total_files,
            "status": scan_result.status,
        },
        artifact_refs=[
            str(snapshot_path),
            str(scans_path),
            str(get_path("audit_events_file")),
        ],
        warnings=scan_result.warnings,
        errors=[{"failure_class": "SCAN_ERROR", "detail": e} for e in scan_result.errors],
    )
    _print_response(resp)
    return resp


def _print_response(resp: CLICommandResponse):
    print(resp.message)
    if resp.warnings:
        for w in resp.warnings:
            print(f"  Warning: {w}")
    if resp.errors:
        for e in resp.errors:
            failure = e.get("failure_class", "UNKNOWN")
            detail = e.get("detail", "")
            print(f"  Error: {failure}" + (f" — {detail}" if detail else ""))


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
