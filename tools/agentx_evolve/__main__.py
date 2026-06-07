import sys
from pathlib import Path


_self_dir = Path(__file__).resolve().parent
_tools_dir = _self_dir.parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))


def main() -> None:
    args = sys.argv[1:]
    if not args:
        _print_help()
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
    elif cmd == "chat":
        _run_chat(args[1:])
    elif cmd == "self-upgrade":
        _run_self_upgrade(args[1:])
    elif cmd == "init-agent":
        _run_init_agent(args[1:])
    elif cmd == "evolve-agent":
        _run_evolve_agent(args[1:])
    elif cmd == "help" or cmd == "--help":
        _print_help()
        sys.exit(0)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


def _print_help() -> None:
    print("Usage: agentx-evolve <command> [options]")
    print()
    print("Commands:")
    print("  review <session_id>        Review an implementation session")
    print("  approve <session_id>       Approve a session")
    print("  reject <session_id>        Reject a session")
    print("  explain <session_id>       Show session details")
    print("  chat [options]             Chat with an LLM provider")
    print("  self-upgrade [options]     Self-upgrade plan or apply")
    print("  init-agent [options]       Initialize a new agent")
    print("  evolve-agent [options]     Evolve an external agent")
    print("  version                    Show version")
    print()
    print("Chat options:")
    print("  --once <message>           One-shot chat message")
    print("  --mock                     Use deterministic mock provider")
    print("  --json                     JSON stdout output")
    print("  --provider <name>          Provider (mock, opencode)")
    print("  --model <model-id>         Model identifier")
    print("  --run-root <path>          Run artifacts root")
    print("  --timeout <seconds>        Provider timeout")
    print()
    print("Self-upgrade / Evolve-agent options:")
    print("  --concept-file <path>      Concept/architecture change file")
    print("  --mode <plan|apply>        Workflow mode")
    print("  --dry-run                  Validate without applying")
    print()
    print("Init-agent options:")
    print("  --name <agent-name>        Agent name")
    print("  --dest <path>              Destination directory")


def _run_chat(argv: list[str]) -> None:
    from agentx_evolve.runtime.config import ConfigResolver
    from agentx_evolve.runtime.results import (
        EXIT_BLOCKED, EXIT_INVALID_CLI, EXIT_FAIL, EXIT_ARTIFACT_FAIL,
    )
    from agentx_evolve.workflows.chat import ChatWorkflow

    resolver = ConfigResolver()
    config = resolver.resolve(argv)

    if config.once_message:
        pass
    elif not argv:
        if sys.stdin.isatty():
            sys.stderr.write("chat> ")
            sys.stderr.flush()
        config.once_message = sys.stdin.read().strip()
        if not config.once_message:
            print("chat: empty input", file=sys.stderr)
            sys.exit(EXIT_BLOCKED)
    else:
        remaining = " ".join(argv)
        config.once_message = remaining

    workflow = ChatWorkflow(config)
    try:
        result = workflow.run()
    except ValueError as e:
        print(f"chat invalid flag: {e}", file=sys.stderr)
        sys.exit(EXIT_INVALID_CLI)
    except FileNotFoundError as e:
        print(f"chat BLOCKED: {e}", file=sys.stderr)
        sys.exit(EXIT_BLOCKED)
    except OSError as e:
        print(f"chat artifact error: {e}", file=sys.stderr)
        sys.exit(EXIT_ARTIFACT_FAIL)
    except Exception as e:
        print(f"chat failed: {e}", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    if config.json:
        import json
        json.dump(result.to_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(result.message)

    sys.exit(result.exit_code)


def _run_review(session_id: str) -> None:
    from agentx_evolve.review.review_interface import HumanReviewInterface, ReviewReport
    hri = HumanReviewInterface()
    report = ReviewReport(session_id=session_id, task="review")
    result = hri.review(session_id, report)
    print(f"Session: {result.session_id}")
    print(f"Task: {result.task}")
    print(f"Files changed: {', '.join(result.files_changed) or 'none'}")
    print(f"Rollback available: {result.rollback_available}")


def _run_approve(session_id: str) -> None:
    from agentx_evolve.review.review_interface import HumanReviewInterface
    hri = HumanReviewInterface()
    record = hri.approve(session_id, reviewer="cli", reason="CLI approval")
    print(f"Session {session_id} approved (id={record.approval_id})")


def _run_reject(session_id: str) -> None:
    from agentx_evolve.review.review_interface import HumanReviewInterface
    hri = HumanReviewInterface()
    record = hri.reject(session_id, reviewer="cli", reason="CLI rejection")
    print(f"Session {session_id} rejected (id={record.approval_id})")


def _run_explain(session_id: str) -> None:
    from agentx_evolve.review.review_interface import HumanReviewInterface, ReviewReport
    hri = HumanReviewInterface()
    report = ReviewReport(session_id=session_id)
    result = hri.review(session_id, report)
    print(f"Session: {result.session_id}")
    print(f"Proposal: {result.proposal}")
    print(f"Governance: {result.governance_decision}")
    print(f"Risk: {result.risk_assessment}")


def _run_self_upgrade(argv: list[str]) -> None:
    from agentx_evolve.runtime.config import ConfigResolver
    from agentx_evolve.runtime.results import EXIT_BLOCKED, EXIT_FAIL, EXIT_INVALID_CLI
    from agentx_evolve.workflows.self_upgrade import SelfUpgradeWorkflow

    resolver = ConfigResolver()
    try:
        config = resolver.resolve(argv)
    except ValueError as e:
        print(f"self-upgrade: {e}", file=sys.stderr)
        sys.exit(EXIT_INVALID_CLI)
    config.command = "self-upgrade"

    if not config.concept_file:
        for i, a in enumerate(argv):
            if a == "--concept-file" and i + 1 < len(argv):
                config.concept_file = argv[i + 1]

    workflow = SelfUpgradeWorkflow(config)
    try:
        result = workflow.run()
    except Exception as e:
        print(f"self-upgrade failed: {e}", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    if config.json:
        import json
        json.dump(result.to_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(result.message)

    sys.exit(result.exit_code)


def _run_init_agent(argv: list[str]) -> None:
    from agentx_evolve.runtime.config import ConfigResolver
    from agentx_evolve.runtime.results import EXIT_BLOCKED, EXIT_FAIL, EXIT_INVALID_CLI
    from agentx_evolve.workflows.init_agent import InitAgentWorkflow

    resolver = ConfigResolver()
    try:
        config = resolver.resolve(argv)
    except ValueError as e:
        print(f"init-agent: {e}", file=sys.stderr)
        sys.exit(EXIT_INVALID_CLI)
    config.command = "init-agent"

    for i, a in enumerate(argv):
        if a == "--name" and i + 1 < len(argv):
            config.agent_name = argv[i + 1]
        if a == "--dest" and i + 1 < len(argv):
            config.dest = argv[i + 1]

    if not config.agent_name:
        print("init-agent requires --name", file=sys.stderr)
        sys.exit(EXIT_BLOCKED)

    workflow = InitAgentWorkflow(config)
    try:
        result = workflow.run()
    except Exception as e:
        print(f"init-agent failed: {e}", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    if config.json:
        import json
        json.dump(result.to_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(result.message)

    sys.exit(result.exit_code)


def _run_evolve_agent(argv: list[str]) -> None:
    from agentx_evolve.runtime.config import ConfigResolver
    from agentx_evolve.runtime.results import EXIT_BLOCKED, EXIT_FAIL, EXIT_INVALID_CLI
    from agentx_evolve.workflows.evolve_agent import EvolveAgentWorkflow

    resolver = ConfigResolver()
    try:
        config = resolver.resolve(argv)
    except ValueError as e:
        print(f"evolve-agent: {e}", file=sys.stderr)
        sys.exit(EXIT_INVALID_CLI)
    config.command = "evolve-agent"

    for i, a in enumerate(argv):
        if a == "--agent-dir" and i + 1 < len(argv):
            config.agent_dir = argv[i + 1]
        if a == "--concept-file" and i + 1 < len(argv):
            config.concept_file = argv[i + 1]

    if not config.agent_dir:
        print("evolve-agent requires --agent-dir", file=sys.stderr)
        sys.exit(EXIT_BLOCKED)

    workflow = EvolveAgentWorkflow(config)
    try:
        result = workflow.run()
    except Exception as e:
        print(f"evolve-agent failed: {e}", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    if config.json:
        import json
        json.dump(result.to_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(result.message)

    sys.exit(result.exit_code)


if __name__ == "__main__":
    main()
