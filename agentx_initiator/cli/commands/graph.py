"""PM3 stub — not active in Product Milestone 1."""
import json


def register(sub):
    p = sub.add_parser("graph", help="Build architecture knowledge graph (PM3 — BLOCKED in PM1)")
    p.set_defaults(func=run)


def run(args):
    resp = {
        "status": "BLOCKED",
        "exit_code": 3,
        "message": "Command is reserved for a later product milestone.",
        "errors": [{"failure_class": "COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1"}],
    }
    print(json.dumps(resp, indent=2))
