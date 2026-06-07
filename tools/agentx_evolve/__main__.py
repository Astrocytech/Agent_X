import sys


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("Usage: agentx-evolve <command> [options]")
        print()
        print("Commands:")
        print("  review <session_id>   Review an implementation session")
        print("  approve <session_id>  Approve a session")
        print("  reject <session_id>   Reject a session")
        print("  explain <session_id>  Show session details")
        print("  version               Show version")
        sys.exit(0)

    cmd = args[0]
    if cmd == "version":
        from agentx_evolve import __version__
        print(f"agentx-evolve {__version__}")
    elif cmd == "review":
        if len(args) < 2:
            print("Usage: agentx-evolve review <session_id>")
            sys.exit(1)
        _run_review(args[1])
    elif cmd == "approve":
        if len(args) < 2:
            print("Usage: agentx-evolve approve <session_id>")
            sys.exit(1)
        _run_approve(args[1])
    elif cmd == "reject":
        if len(args) < 2:
            print("Usage: agentx-evolve reject <session_id>")
            sys.exit(1)
        _run_reject(args[1])
    elif cmd == "explain":
        if len(args) < 2:
            print("Usage: agentx-evolve explain <session_id>")
            sys.exit(1)
        _run_explain(args[1])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


from agentx_evolve.review.review_interface import HumanReviewInterface, ReviewReport


def _run_review(session_id: str) -> None:
    hri = HumanReviewInterface()
    report = ReviewReport(session_id=session_id, task="review")
    result = hri.review(session_id, report)
    print(f"Session: {result.session_id}")
    print(f"Task: {result.task}")
    print(f"Files changed: {', '.join(result.files_changed) or 'none'}")
    print(f"Rollback available: {result.rollback_available}")


def _run_approve(session_id: str) -> None:
    hri = HumanReviewInterface()
    record = hri.approve(session_id, reviewer="cli", reason="CLI approval")
    print(f"Session {session_id} approved (id={record.approval_id})")


def _run_reject(session_id: str) -> None:
    hri = HumanReviewInterface()
    record = hri.reject(session_id, reviewer="cli", reason="CLI rejection")
    print(f"Session {session_id} rejected (id={record.approval_id})")


def _run_explain(session_id: str) -> None:
    hri = HumanReviewInterface()
    report = ReviewReport(session_id=session_id)
    result = hri.review(session_id, report)
    print(f"Session: {result.session_id}")
    print(f"Proposal: {result.proposal}")
    print(f"Governance: {result.governance_decision}")
    print(f"Risk: {result.risk_assessment}")


if __name__ == "__main__":
    main()
