"""PM2: Run allowlisted validation commands."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from uuid import uuid4
from agentx_initiator.core.validation_runner import run_validation
from agentx_initiator.core.path_registry import get_path
from agentx_initiator.core.audit_log import append_event
from agentx_initiator.cli.models import CLICommandResponse


def register(sub):
    p = sub.add_parser("validate", help="Run allowlisted validation commands")
    p.set_defaults(func=run)


def run(args):
    try:
        results = run_validation()
    except Exception as e:
        resp = _response("validate", "FAILED", 5,
                         f"Validation runner error: {e}",
                         errors=[{"failure_class": "VALIDATION_ERROR", "detail": str(e)}])
        _print_response(resp)
        return resp

    passed = sum(1 for r in results if r.get("passed"))
    failed = sum(1 for r in results if not r.get("passed"))

    status = "PASS" if failed == 0 else "PARTIAL"

    report_obj = {
        "schema_version": "1.0",
        "schema_id": "validation_report.schema.json",
        "report_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_component": "ValidationRunner",
        "status": status,
        "allowlist_entries": [],
        "runs": results,
        "manifest": {},
        "warnings": [],
        "errors": [],
    }

    report_path = get_path("reports_dir") / "validation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report_obj, indent=2))

    append_event({
        "event_type": "validate",
        "category": "VALIDATION",
        "status": "SUCCESS" if failed == 0 else "PARTIAL",
        "summary": f"Validation: {passed} passed, {failed} failed",
        "component": "validate_command",
        "artifact_refs": [str(report_path)],
    })

    status = "SUCCESS" if failed == 0 else "PARTIAL"
    resp = _response("validate", status, 0 if failed == 0 else 4,
                     f"Validation complete: {passed} passed, {failed} failed.",
                     data={"results": results, "passed": passed, "failed": failed},
                     artifact_refs=[str(report_path)])
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
