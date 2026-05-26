import json
from agentx_initiator.core.evolution_planner import generate_plan
from agentx_initiator.core.paths import snapshot_file, report_file, ensure_state_dirs
from agentx_initiator.core.report_writer import render_report, write_report
from agentx_initiator.core.audit_log import append_event
from agentx_initiator.core.memory_store import append_record


def register(sub):
    p = sub.add_parser("plan", help="Generate evolution plan")
    p.set_defaults(func=run)


def run(args):
    ensure_state_dirs()
    items = generate_plan()

    snap = snapshot_file("architecture_latest.json")
    snap.write_text(json.dumps({"plan_items": items, "count": len(items)}, indent=2))

    context = {"plan_items": items, "count": len(items), "generated_at": __import__("datetime").datetime.now().isoformat()}
    report = render_report("evolution_plan.md.j2", context)
    path = write_report("evolution_plan_latest.json", report)

    print(f"Evolution plan written to {path}")
    print(f"Recommendations: {len(items)}")
    for item in items:
        print(f"  P{item['priority']:02d} [{item['category']}]: {item['action']}")
    for item in items:
        append_record("evolution_plan_history.jsonl", item)

    append_event({
        "event_type": "plan",
        "detail": f"Generated evolution plan with {len(items)} recommendations",
    })
