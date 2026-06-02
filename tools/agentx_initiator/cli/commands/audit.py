"""PM2: Read append-only audit event history."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from agentx_initiator.core.audit_log import read_events, append_event
from agentx_initiator.core.path_registry import get_path
from agentx_initiator.cli.models import CLICommandResponse


def register(sub):
    p = sub.add_parser("audit", help="Read append-only audit event history")
    p.add_argument("--limit", type=int, default=50, help="Max events to return")
    p.add_argument("--category", default="", help="Filter by category")
    p.set_defaults(func=run)


def run(args):
    try:
        events = read_events(limit=args.limit)
    except OSError as e:
        resp = _response("audit", "FAILED", 5, "Failed to read audit log",
                         errors=[{"failure_class": "FILE_READ_ERROR", "detail": str(e)}])
        _print_response(resp)
        return resp

    if args.category:
        events = [e for e in events if e.get("category", "").lower() == args.category.lower()]

    append_event({
        "event_type": "audit",
        "category": "SYSTEM",
        "status": "SUCCESS",
        "summary": f"Read {len(events)} audit events (limit={args.limit})",
        "component": "audit_command",
        "artifact_refs": [str(get_path("audit_events_file"))],
    })

    resp = _response("audit", "SUCCESS", 0,
                     f"Found {len(events)} audit event(s).",
                     data={"events": events, "count": len(events)},
                     artifact_refs=[str(get_path("audit_events_file"))])
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
