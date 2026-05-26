import sys
import json
import argparse
from datetime import datetime, timezone
from uuid import uuid4
from agentx_initiator.core.path_registry import ensure_state_dirs
from agentx_initiator.cli.commands import scan, status


def stub_cmd(args):
    pm_required = getattr(args, "required_pm", 2)
    resp = {
        "schema_version": "1.0",
        "response_id": str(uuid4()),
        "request_id": "cli-internal",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": f"agentx-init {args.command}",
        "status": "BLOCKED",
        "exit_code": 3,
        "message": "Command is not implemented in Product Milestone 1.",
        "data": {
            "failure_class": "COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1",
            "product_milestone": 1,
            "required_product_milestone": pm_required,
        },
        "artifact_refs": [],
        "warnings": [],
        "errors": [],
    }
    print(json.dumps(resp, indent=2))


def register_stub(sub, name, help_text, required_pm=2):
    p = sub.add_parser(name, help=help_text)
    p.set_defaults(func=stub_cmd, required_pm=required_pm)


def main():
    ensure_state_dirs()
    parser = argparse.ArgumentParser(
        prog="agentx-init",
        description="Agent_X Initiator / Evolution Assistant — inspect, plan, and safely evolve Agent_X",
    )
    parser.add_argument("--version", action="version", version="agentx-init 1.0.0")

    sub = parser.add_subparsers(dest="command")

    scan.register(sub)
    status.register(sub)
    register_stub(sub, "explain", "Explain a file, directory, or layer (PM2)")
    register_stub(sub, "plan", "Generate ranked evolution plans (PM2)")
    register_stub(sub, "propose", "Generate non-mutating patch proposal (PM2)")
    register_stub(sub, "validate", "Run allowlisted validation commands (PM2)")
    register_stub(sub, "audit", "Read audit event history (PM2)")
    register_stub(sub, "report", "Generate architecture report (PM2)")
    register_stub(sub, "memory", "Query memory store (PM2)")
    register_stub(sub, "graph", "Generate repository knowledge graph (PM3)", required_pm=3)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
