from __future__ import annotations
import sys
import json
from datetime import datetime, timezone
from uuid import uuid4
import argparse
from agentx_initiator.cli.registry import register, CommandEntry
from agentx_initiator.cli.commands import scan, status, help as help_cmd
from agentx_initiator.cli.commands import audit, explain, plan, propose, validate, report, graph
from agentx_initiator.cli.models import CLICommandResponse
from agentx_initiator.core.audit_log import append_event


PM3_COMMANDS: list[tuple[str, str]] = []
RESERVED_COMMANDS = [
    ("memory", "Query memory store (PM3+)"),
]


def _register_all():
    register(CommandEntry(
        name="help", category="HELP", description="Show available commands",
        writes_artifacts=False,
    ))
    register(CommandEntry(
        name="scan", category="SCAN",
        description="Scan repository structure and layers",
        writes_artifacts=True,
    ))
    register(CommandEntry(
        name="status", category="STATUS",
        description="Generate status report from scan",
        writes_artifacts=True,
    ))
    register(CommandEntry(
        name="audit", category="AUDIT",
        description="Read append-only audit event history",
        writes_artifacts=False,
    ))
    register(CommandEntry(
        name="explain", category="ANALYSIS",
        description="Explain a file, directory, or layer",
        writes_artifacts=False,
    ))
    register(CommandEntry(
        name="plan", category="EVOLUTION",
        description="Generate ranked evolution plan",
        writes_artifacts=True,
    ))
    register(CommandEntry(
        name="propose", category="PATCH",
        description="Generate non-mutating patch proposal",
        writes_artifacts=True,
    ))
    register(CommandEntry(
        name="validate", category="VALIDATION",
        description="Run allowlisted validation commands",
        writes_artifacts=True,
    ))
    register(CommandEntry(
        name="report", category="ARCHITECTURE",
        description="Generate architecture report",
        writes_artifacts=True,
    ))
    register(CommandEntry(
        name="graph", category="GRAPH",
        description="Build and query the Knowledge Graph",
        writes_artifacts=True,
    ))
    for name, desc in PM3_COMMANDS:
        register(CommandEntry(
            name=name, category="RESERVED", description=desc,
            writes_artifacts=False,
        ))
    for name, desc in RESERVED_COMMANDS:
        register(CommandEntry(
            name=name, category="RESERVED", description=desc,
            writes_artifacts=False,
        ))


def _reserved_stub(command_name: str, args=None) -> CLICommandResponse:
    resp = CLICommandResponse(
        response_id=str(uuid4()),
        request_id="cli-internal",
        timestamp=datetime.now(timezone.utc).isoformat(),
        command=command_name,
        status="BLOCKED",
        exit_code=3,
        message="Command is reserved for a later product milestone.",
        errors=[{"failure_class": "COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1"}],
    )
    append_event({
        "event_type": command_name,
        "category": "SYSTEM",
        "status": "BLOCKED",
        "summary": f"Reserved command '{command_name}' blocked in PM1",
        "component": "cli_main",
    })
    print(json.dumps(resp.to_dict(), indent=2))
    return resp


def main():
    _register_all()
    parser = argparse.ArgumentParser(
        prog="agentx-init",
        description="Agent_X Initiator — read-only CLI companion",
    )
    parser.add_argument("--version", action="version", version="agentx-init 1.0.0")

    sub = parser.add_subparsers(dest="command")

    scan.register(sub)
    status.register(sub)
    help_cmd.register(sub)
    audit.register(sub)
    explain.register(sub)
    plan.register(sub)
    propose.register(sub)
    validate.register(sub)
    report.register(sub)
    graph.register(sub)

    for name, desc in PM3_COMMANDS + RESERVED_COMMANDS:
        p = sub.add_parser(name, help=desc)
        p.set_defaults(func=lambda a, n=name: _reserved_stub(n, a))

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(2)

    if args.command == "help":
        args.func(args)
        sys.exit(0)
    elif args.command in ("scan", "status", "audit", "explain", "plan", "propose", "validate", "report", "graph"):
        resp = args.func(args)
        if resp is not None:
            sys.exit(resp.exit_code if hasattr(resp, 'exit_code') else 0)
    else:
        args.func(args)
        sys.exit(3)


if __name__ == "__main__":
    main()
