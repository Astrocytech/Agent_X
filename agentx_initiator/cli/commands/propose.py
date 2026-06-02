"""PM2: Generate non-mutating patch proposal."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
import json
from agentx_initiator.core.patch_proposal_generator import generate_patch_proposal
from agentx_initiator.core.path_registry import get_path
from agentx_initiator.core.audit_log import append_event
from agentx_initiator.cli.models import CLICommandResponse


def register(sub):
    p = sub.add_parser("propose", help="Generate non-mutating patch proposal")
    p.add_argument("--task", default="", required=True, help="Describe the task for the proposal")
    p.set_defaults(func=run)


def run(args):
    if not args.task:
        resp = _response("propose", "FAILED", 1,
                         "No task provided. Use --task to describe the work.",
                         errors=[{"failure_class": "MISSING_ARGUMENT"}])
        _print_response(resp)
        return resp

    spec = generate_patch_proposal(task=args.task)

    spec_path = get_path("proposals_dir") / f"proposal_{spec.spec_id[:8]}.json"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_dict = spec.to_dict() if hasattr(spec, "to_dict") else {"raw": str(spec)}
    spec_path.write_text(json.dumps(spec_dict, indent=2, default=str))

    append_event({
        "event_type": "propose",
        "category": "PATCH",
        "status": "SUCCESS",
        "summary": f"Patch proposal generated for: {args.task[:60]}",
        "component": "propose_command",
        "artifact_refs": [str(spec_path)],
    })

    actions = getattr(spec, "actions", [])
    resp = _response("propose", "SUCCESS", 0,
                     f"Patch proposal generated ({len(actions)} action(s)).",
                     data={"spec_id": spec.spec_id, "task": args.task, "action_count": len(actions)},
                     artifact_refs=[str(spec_path)])
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
