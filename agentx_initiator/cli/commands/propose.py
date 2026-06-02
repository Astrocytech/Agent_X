# PM2 implementation — not active in Product Milestone 1 (registered as BLOCKED stub)
from agentx_initiator.core.patch_proposal_generator import generate_proposal
from agentx_initiator.core.paths import report_file, ensure_state_dirs
from agentx_initiator.core.report_writer import render_report, write_report
from agentx_initiator.core.audit_log import append_event
from agentx_initiator.core.memory_store import append_record


def register(sub):
    p = sub.add_parser("propose", help="Generate non-mutating patch proposal")
    p.add_argument("--task", required=True, help="Describe the task for the proposal")
    p.set_defaults(func=run)


def run(args):
    ensure_state_dirs()
    proposal = generate_proposal(args.task)

    if not proposal.allowed:
        print(f"BLOCKED: {proposal.reason}")
        print(f"Risk level {proposal.risk_level} exceeds allowed maximum.")
        append_event({
            "event_type": "propose_blocked",
            "detail": f"Proposal blocked: risk={proposal.risk_level}, task={args.task[:100]}",
        })
        return

    context = {
        "proposal": proposal.model_dump(),
        "task": args.task,
    }
    report = render_report("patch_proposal.md.j2", context)
    path = write_report("patch_proposal_latest.json", report)

    print(f"Proposal written to {path}")
    print(f"  ID:       {proposal.proposal_id}")
    print(f"  Risk:     {proposal.risk_level}")
    print(f"  Status:   {'ALLOWED' if proposal.allowed else 'BLOCKED'}")
    print(f"  Affected: {', '.join(proposal.affected_layers)}")
    print()
    print("This proposal is non-mutating and human-reviewable.")
    print("It does not modify any source files automatically.")

    append_record("patch_proposal_history.jsonl", proposal.model_dump())
    append_event({
        "event_type": "propose",
        "detail": f"Generated proposal {proposal.proposal_id}: {args.task[:100]}",
    })
