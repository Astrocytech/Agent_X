"""PM2: Explain a file, directory, or layer using latest scan."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
from agentx_initiator.core.path_registry import get_path
from agentx_initiator.core.audit_log import append_event
from agentx_initiator.cli.models import CLICommandResponse


def register(sub):
    p = sub.add_parser("explain", help="Explain a file, directory, or layer")
    p.add_argument("path", nargs="?", default=".", help="Path to explain")
    p.set_defaults(func=run)


def run(args):
    snapshot_path = get_path("repo_scan_latest")
    if not snapshot_path.exists():
        resp = _response("explain", "BLOCKED", 3,
                         "No repository scan found. Run agentx-init scan first.",
                         errors=[{"failure_class": "MISSING_SCAN"}])
        _print_response(resp)
        return resp

    try:
        scan_data = json.loads(snapshot_path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        resp = _response("explain", "FAILED", 5, "Failed to read scan",
                         errors=[{"failure_class": "FILE_READ_ERROR", "detail": str(e)}])
        _print_response(resp)
        return resp

    target = str(Path(args.path).resolve())
    files = scan_data.get("files", [])
    directories = scan_data.get("directories", [])

    matched_files = [f for f in files if target in f.get("path", "")]
    matched_dirs = [d for d in directories if target in d.get("path", "")]
    layers = scan_data.get("layer_summary", {})

    info = {
        "target": target,
        "matched_files": len(matched_files),
        "matched_directories": len(matched_dirs),
        "file_details": matched_files[:20],
        "directory_details": matched_dirs[:10],
        "layers": layers,
    }

    append_event({
        "event_type": "explain",
        "category": "ANALYSIS",
        "status": "SUCCESS",
        "summary": f"Explained {target}: {len(matched_files)} files",
        "component": "explain_command",
        "artifact_refs": [str(snapshot_path)],
    })

    resp = _response("explain", "SUCCESS", 0,
                     f"Found {len(matched_files)} file(s), {len(matched_dirs)} directory(ies) for {target}",
                     data=info, artifact_refs=[str(snapshot_path)])
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
