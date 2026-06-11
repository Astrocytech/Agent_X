"""Inverse-science CLI workflow commands."""
import json, sys, os
from datetime import datetime, timezone

COMMANDS = ["plan", "candidates", "rank", "decide", "observe", "report"]

def cmd_plan(args):
    """Create an inverse-science plan."""
    return {"status": "ok", "plan": {"target_capability": args.get("capability", "unknown"),
                                      "constraints": args.get("constraints", []),
                                      "created_at_utc": datetime.now(timezone.utc).isoformat()}}

def cmd_candidates(args):
    """List candidate actions for a plan."""
    return {"status": "ok", "candidates": [{"id": "C1", "action": "improve_boundary_weather",
                                             "priority": "high", "risk": "low"}]}

def cmd_rank(args):
    """Rank candidates by priority."""
    candidates = args.get("candidates", [])
    ranked = sorted(candidates, key=lambda c: {"high": 0, "medium": 1, "low": 2}.get(c.get("priority", "low"), 3))
    return {"status": "ok", "ranked": ranked}

def cmd_decide(args):
    """Route candidate through governance."""
    decision = args.get("decision", "allow")
    if decision not in ("allow", "allow_with_limits", "reject", "require_reframe"):
        return {"status": "error", "message": f"Invalid decision: {decision}"}
    return {"status": "ok", "decision": decision, "governance_routed": True, "patch_executed": False}

def cmd_observe(args):
    """Record observation and evidence."""
    return {"status": "ok", "observation_id": f"OBS-{datetime.now(timezone.utc).timestamp():.0f}",
            "evidence_class": args.get("evidence_class", "unknown")}

def cmd_report(args):
    """Generate inverse-science report."""
    return {"status": "ok", "report": {"findings": args.get("findings", []),
                                        "negative_knowledge": args.get("negative_knowledge", []),
                                        "best_known_solution": args.get("best_known_solution", None)}}

def main():
    if len(sys.argv) < 2:
        print("Usage: agentx-evolve inverse-science <command> [args]")
        print(f"Commands: {', '.join(COMMANDS)}")
        sys.exit(1)
    cmd = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    dispatch = {"plan": cmd_plan, "candidates": cmd_candidates, "rank": cmd_rank,
                "decide": cmd_decide, "observe": cmd_observe, "report": cmd_report}
    if cmd not in dispatch:
        print(f"Unknown command: {cmd}"); sys.exit(1)
    result = dispatch[cmd](args)
    print(json.dumps(result, indent=2))
    if result.get("status") != "ok":
        sys.exit(1)

if __name__ == "__main__":
    main()
