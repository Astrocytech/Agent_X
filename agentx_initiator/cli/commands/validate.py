# PM2 implementation — not active in Product Milestone 1 (registered as BLOCKED stub)
from agentx_initiator.core.validation_runner import run_validation
from agentx_initiator.core.paths import report_file, ensure_state_dirs
from agentx_initiator.core.report_writer import render_report, write_report
from agentx_initiator.core.audit_log import append_event
from agentx_initiator.core.memory_store import append_record


def register(sub):
    p = sub.add_parser("validate", help="Run allowlisted validation commands")
    p.set_defaults(func=run)


def run(args):
    ensure_state_dirs()
    results = run_validation()

    context = {
        "validation_results": results,
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
    }
    report = render_report("validation_report.md.j2", context)
    path = write_report("validation_report_latest.json", report)

    print(f"Validation report written to {path}")
    print(f"Commands: {context['passed']} passed, {context['failed']} failed")
    for r in results:
        mark = "✓" if r["passed"] else "✗"
        print(f"  {mark} {r['command']} (exit={r['returncode']})")

    for r in results:
        append_record("validation_history.jsonl", r)
    append_event({
        "event_type": "validate",
        "detail": f"Ran {len(results)} validation commands: {context['passed']} passed",
    })
