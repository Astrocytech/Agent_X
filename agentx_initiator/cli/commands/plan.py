"""PM2: Generate ranked evolution plans."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from agentx_initiator.core.evolution_planner import generate_evolution_plan
from agentx_initiator.core.path_registry import get_path
from agentx_initiator.core.audit_log import append_event
from agentx_initiator.core.report_writer import render_report
from agentx_initiator.cli.models import CLICommandResponse


def register(sub):
    p = sub.add_parser("plan", help="Generate ranked evolution plan")
    p.add_argument("--task", default="", help="Task description for planning")
    p.set_defaults(func=run)


def run(args):
    plan = generate_evolution_plan()

    plan_path = get_path("plans_dir") / f"plan_{plan.plan_id[:8]}.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(plan.to_dict() if hasattr(plan, "to_dict") else str(plan))

    report_content = render_report("evolution_plan.md.j2", plan.to_dict() if hasattr(plan, "to_dict") else {})
    report_path = get_path("latest_status_report").parent / f"evolution_plan_{plan.plan_id[:8]}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_content)

    append_event({
        "event_type": "plan",
        "category": "EVOLUTION",
        "status": "SUCCESS",
        "summary": f"Generated evolution plan with {len(getattr(plan, 'steps', []))} steps",
        "component": "plan_command",
        "artifact_refs": [str(plan_path), str(report_path)],
    })

    resp = _response("plan", "SUCCESS", 0,
                     f"Evolution plan generated ({len(getattr(plan, 'steps', []))} steps).",
                     data={"plan_id": plan.plan_id, "step_count": len(getattr(plan, 'steps', []))},
                     artifact_refs=[str(plan_path), str(report_path)])
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
