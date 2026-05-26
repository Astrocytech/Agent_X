from agentx_initiator.core.audit_log import read_events


def register(sub):
    p = sub.add_parser("audit", help="Read append-only audit history")
    p.add_argument("--limit", type=int, default=50, help="Number of events to show")
    p.set_defaults(func=run)


def run(args):
    events = read_events(limit=args.limit)
    if not events:
        print("No audit events found.")
        return
    print(f"Audit log ({len(events)} events):")
    print()
    for evt in events:
        ts = evt.get("timestamp", "?")
        etype = evt.get("event_type", "?")
        detail = evt.get("detail", "")
        print(f"  [{ts}] {etype}: {detail[:120]}")
