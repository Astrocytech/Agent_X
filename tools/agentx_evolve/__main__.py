import json
import os
import sys
import select
from pathlib import Path


_self_dir = Path(__file__).resolve().parent
_tools_dir = _self_dir.parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))


def _read_input(prompt: str = "chat> ") -> str:
    """Read input with bracketed paste support."""
    PASTE_START = "\x1b[200~"
    PASTE_END = "\x1b[201~"

    sys.stderr.write(prompt)
    sys.stderr.flush()

    lines: list[str] = []
    while True:
        try:
            raw = sys.stdin.readline()
        except KeyboardInterrupt:
            raise
        if not raw:
            raise EOFError
        line = raw.rstrip("\r\n")

        if PASTE_START in line:
            line = line.replace(PASTE_START, "")
        is_paste_end = PASTE_END in line
        if is_paste_end:
            line = line.replace(PASTE_END, "")

        if not line and not lines:
            continue

        lines.append(line)

        if is_paste_end:
            break

        ready, _, _ = select.select([sys.stdin], [], [], 0.08)
        if not ready:
            break

    return "\n".join(lines)


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
    elif cmd == "help" or cmd == "--help" or cmd == "-h":
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
    print("  --provider <name>          Provider (api, opencode, mock)")
    print("  --model <model-id>         Model identifier (default: qwen2.5-coder:7b)")
    print("  --run-root <path>          Run artifacts root")
    print("  --timeout <seconds>        Provider timeout")
    print("  --session-id <id>          Resume an existing session (provider-specific)")
    print("  --api-base-url <url>       API provider base URL (default: http://127.0.0.1:11434/v1)")
    print("  --api-key <key>            API provider key")
    print()
    print("Self-upgrade / Evolve-agent options:")
    print("  --concept-file <path>      Concept/architecture change file")
    print("  --mode <plan|apply>        Workflow mode")
    print("  --dry-run                  Validate without applying")
    print()
    print("Init-agent options:")
    print("  --name <agent-name>        Agent name")
    print("  --dest <path>              Destination directory")


def _chat_help() -> None:
    print("Usage: agentx-evolve chat [options]")
    print()
    print("Start an interactive chat session, or send a one-shot message.")
    print()
    print("Interactive mode:")
    print("  (no arguments)              Start interactive REPL")
    print("  /exit                       Exit the REPL")
    print("  Ctrl+C or Ctrl+D            Exit the REPL")
    print()
    print("One-shot mode:")
    print("  --once <message>            Single message, print response and exit")
    print("  (pipe stdin)                Read message from stdin")
    print()
    print("Options:")
    print("  --help, -h                  Show this help")
    print("  --mock                      Use deterministic mock provider")
    print("  --json                      JSON stdout output")
    print("  --provider <name>           Provider (api, opencode, mock)")
    print("  --model <model-id>          Model identifier (default: qwen2.5-coder:7b)")
    print("  --run-root <path>           Run artifacts root")
    print("  --timeout <seconds>         Provider timeout")
    print("  --session-id <id>           Resume an existing session (provider-specific)")
    print("  --api-base-url <url>        API provider base URL (default: http://127.0.0.1:11434/v1)")
    print("  --api-key <key>             API provider key")
    print("  --gui                       Force browser UI (default when DISPLAY is set)")
    print("  --no-gui                    Force terminal REPL")


def _should_use_gui(argv: list[str]) -> bool:
    if "--no-gui" in argv:
        return False
    if "--gui" in argv:
        return True
    return bool(os.environ.get("DISPLAY"))


def _run_chat(argv: list[str]) -> None:
    from agentx_evolve.runtime.config import ConfigResolver
    from agentx_evolve.runtime.results import (
        EXIT_ARTIFACT_FAIL, EXIT_BLOCKED, EXIT_FAIL, EXIT_INVALID_CLI,
    )
    from agentx_evolve.workflows.chat import ChatWorkflow

    if "--help" in argv or "-h" in argv:
        _chat_help()
        sys.exit(0)

    use_gui = _should_use_gui(argv)
    stripped = [a for a in argv if a not in ("--gui", "--no-gui")]

    resolver = ConfigResolver()
    config = resolver.resolve(stripped)

    if config.once_message:
        pass
    elif sys.stdin.isatty():
        from agentx_evolve.providers.provider_router import ProviderRouter
        router = ProviderRouter(config)
        provider = router.get_provider()
        sid = getattr(provider, "session_id", None)

        if use_gui:
            from agentx_evolve.runtime.chat_window import run_chat_window
            sys.exit(run_chat_window(provider, sid or "", config.model, config))
        else:
            import readline
            from agentx_evolve.runtime.chat_ui import ChatUI
            ui = ChatUI(session_id=sid or "", model=config.model, mode=config.mode)
            while True:
                try:
                    line = _read_input("chat> ")
                    stripped = line.strip()
                    if stripped == "/exit":
                        sys.exit(0)
                    if stripped.startswith("/mode"):
                        parts = stripped.split()
                        if len(parts) == 1:
                            mode_label = {"plan": "Planning", "apply": "Build"}.get(ui.mode, ui.mode)
                            print(f"Current mode: {mode_label}")
                        elif len(parts) == 2:
                            try:
                                ui.set_mode(parts[1])
                                config.mode = parts[1]
                                mode_label = {"plan": "Planning", "apply": "Build"}.get(parts[1], parts[1])
                                print(f"Switched to {mode_label} mode")
                            except ValueError as e:
                                print(e)
                        continue
                    if not stripped:
                        continue
                    ui.add_event({"type": "text", "text": stripped, "author": "user"})
                    gen = provider.complete_streaming([{"role": "user", "content": stripped}])
                    try:
                        while True:
                            event = next(gen)
                            ui.add_event(event)
                    except StopIteration:
                        pass
                except KeyboardInterrupt:
                    print(file=sys.stderr)
                    break
                except EOFError:
                    break
            sys.exit(0)
    else:
        config.once_message = sys.stdin.read().strip()
        if not config.once_message:
            print("chat: empty input", file=sys.stderr)
            sys.exit(EXIT_BLOCKED)

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


def _init_agent_help() -> None:
    print("Usage: agentx-evolve init-agent [options]")
    print()
    print("Initialize a new agent from a template.")
    print()
    print("Options:")
    print("  --help, -h                  Show this help")
    print("  --name <agent-name>         Agent name")
    print("  --dest <path>               Destination directory")


def _run_init_agent(argv: list[str]) -> None:
    from agentx_evolve.runtime.config import ConfigResolver
    from agentx_evolve.runtime.results import EXIT_BLOCKED, EXIT_FAIL, EXIT_INVALID_CLI
    from agentx_evolve.workflows.init_agent import InitAgentWorkflow

    if "--help" in argv or "-h" in argv:
        _init_agent_help()
        sys.exit(0)

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
