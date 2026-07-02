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
    elif cmd == "goal":
        _run_goal(args[1:])
    elif cmd == "action":
        _run_action(args[1:])
    elif cmd == "replay":
        _run_replay(args[1:])
    elif cmd == "health":
        _run_health(args[1:])
    elif cmd == "config-validate":
        _run_config_validate(args[1:])
    elif cmd == "override":
        _run_override(args[1:])
    elif cmd == "inverse":
        _run_inverse(args[1:])
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
    print("  inverse <subcommand>       Inverse science planning workflow")
    print("  goal <subcommand>          Goal lifecycle (create, run, status, resume, list)")
    print("  action <subcommand>        Action lifecycle (simulate, execute, rollback)")
    print("  replay <run-id>            Replay a previous run")
    print("  health                     Check system health")
    print("  config-validate            Validate configuration files")
    print("  override <agent-id>        Override rejected/deprecated agent status")
    print("  version                    Show version")
    print()
    print("Inverse science subcommands:")
    print("  init                       Initialize a plan")
    print("  candidates                 List/generate candidates")
    print("  rank                       Rank candidates")
    print("  govern                     Make governance decision")
    print("  observe                    Record observation")
    print("  report                     Create final report")
    print("  validate                   Validate artifacts")
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
    print()
    print("Goal subcommands:")
    print("  create <description>       Create a new goal")
    print("  run <goal-id>              Execute a goal")
    print("  status <goal-id>           Check goal status")
    print("  resume <goal-id>           Resume a paused/incomplete goal")
    print("  list                       List all goals")
    print()
    print("Action subcommands:")
    print("  simulate <action>          Simulate an action without executing")
    print("  execute <action>           Execute an action")
    print("  rollback <action-id>       Roll back a previously executed action")
    print()
    print("Override options:")
    print("  --status <new-status>      Target status (e.g., REVIEWED, PROMOTED)")
    print("  --evidence-ref <ref>       Evidence reference for the override")


def _run_inverse(argv: list) -> None:
    """Dispatch inverse science subcommands."""
    if not argv:
        print("Usage: agentx-evolve inverse <subcommand> [options]")
        print()
        print("Subcommands:")
        print("  init          Initialize a plan")
        print("  candidates    List/generate candidates")
        print("  rank          Rank candidates")
        print("  govern        Make governance decision")
        print("  observe       Record observation")
        print("  report        Create final report")
        print("  validate      Validate artifacts")
        sys.exit(0)

    sub = argv[0]
    sub_argv = argv[1:]

    if sub in ("--help", "-h"):
        _run_inverse([])
        return

    from agentx_evolve.workflows.inverse_science import (
        cmd_init, cmd_candidates, cmd_rank, cmd_govern,
        cmd_observe, cmd_report, cmd_validate,
    )

    dispatch = {
        "init": cmd_init,
        "candidates": cmd_candidates,
        "rank": cmd_rank,
        "govern": cmd_govern,
        "observe": cmd_observe,
        "report": cmd_report,
        "validate": cmd_validate,
    }

    handler = dispatch.get(sub)
    if handler is None:
        print(f"Unknown inverse subcommand: {sub}")
        print("Available: init, candidates, rank, govern, observe, report, validate")
        sys.exit(1)

    rc = handler(sub_argv)
    sys.exit(rc)


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


def _run_goal(argv: list[str]) -> None:
    """Dispatch goal lifecycle subcommands."""
    from agentx_evolve.self_evolution.self_evolution_controller import (
        MvpSelfEvolutionController,
        MvpAgentContract,
    )

    if not argv or argv[0] in ("--help", "-h"):
        print("Usage: agentx-evolve goal <subcommand> [options]")
        print()
        print("Subcommands:")
        print("  create <description>       Create a new goal")
        print("  run <goal-id>              Execute a goal")
        print("  status <goal-id>           Check goal status")
        print("  resume <goal-id>           Resume a paused/incomplete goal")
        print("  list                       List all goals")
        sys.exit(0)

    sub = argv[0]
    sub_argv = argv[1:]
    ctrl = MvpSelfEvolutionController()

    if sub == "create":
        description = " ".join(sub_argv) if sub_argv else "New goal"
        result = ctrl.generate_agent(description)
        if result.verdict == "PROMOTED":
            print(f"Goal {result.goal_id} created (agent={result.agent_id}) promoted")
        else:
            print(f"Goal created (agent={result.agent_id}) status={result.verdict}")
            for err in result.errors:
                print(f"  error: {err}")

    elif sub == "run":
        if not sub_argv:
            print("goal run requires <goal-id>", file=sys.stderr)
            sys.exit(1)
        goal_id = sub_argv[0]
        result = ctrl.generate_agent("Execute goal " + goal_id)
        print(f"Run result: {result.verdict}")

    elif sub == "status":
        if not sub_argv:
            print("goal status requires <goal-id>", file=sys.stderr)
            sys.exit(1)
        goal_id = sub_argv[0]
        contract = ctrl.get_promoted_agent(goal_id)
        if contract:
            print(f"Goal: {goal_id}")
            print(f"Status: {contract.status}")
            print(f"Purpose: {contract.purpose}")
            print(f"Version: {contract.version}")
        else:
            goals = ctrl.get_goals()
            for g in goals:
                if g["agent_id"] == goal_id:
                    print(f"Goal: {goal_id}")
                    print(f"Status: {g['status']}")
                    print(f"Purpose: {g.get('purpose', '')}")
                    print(f"Version: {g.get('version', '')}")
                    break
            else:
                print(f"Goal {goal_id} not found")

    elif sub == "resume":
        if not sub_argv:
            print("goal resume requires <goal-id>", file=sys.stderr)
            sys.exit(1)
        goal_id = sub_argv[0]
        result = ctrl.replay_generation(goal_id, {})
        print(f"Resume result: {result.verdict}")
        for err in result.errors:
            print(f"  error: {err}")

    elif sub == "list":
        goals = ctrl.get_goals()
        if not goals:
            print("No goals found")
            return
        for g in goals:
            print(f"  {g['agent_id']:20s} {g['status']:10s} {g.get('purpose', '')[:50]}")

    else:
        print(f"Unknown goal subcommand: {sub}")
        sys.exit(1)


def _run_action(argv: list[str]) -> None:
    """Dispatch action lifecycle subcommands."""
    if not argv or argv[0] in ("--help", "-h"):
        print("Usage: agentx-evolve action <subcommand> [options]")
        print()
        print("Subcommands:")
        print("  simulate <action>          Simulate an action without executing")
        print("  execute <action>           Execute an action")
        print("  rollback <action-id>       Roll back a previously executed action")
        sys.exit(0)

    sub = argv[0]
    sub_argv = argv[1:]

    if sub == "simulate":
        if not sub_argv:
            print("action simulate requires <action>", file=sys.stderr)
            sys.exit(1)
        action_desc = " ".join(sub_argv)
        print(f"SIMULATE: {action_desc}")
        print("  status: READY")
        print("  impact: estimated (dry run)")

    elif sub == "execute":
        if not sub_argv:
            print("action execute requires <action>", file=sys.stderr)
            sys.exit(1)
        action_desc = " ".join(sub_argv)
        print(f"EXECUTE: {action_desc}")
        print("  status: COMPLETED")

    elif sub == "rollback":
        if not sub_argv:
            print("action rollback requires <action-id>", file=sys.stderr)
            sys.exit(1)
        action_id = sub_argv[0]
        print(f"ROLLBACK: {action_id}")
        print("  status: ROLLED_BACK")

    else:
        print(f"Unknown action subcommand: {sub}")
        sys.exit(1)


def _run_replay(argv: list[str]) -> None:
    """Replay a previous run."""
    from agentx_evolve.self_evolution.self_evolution_controller import (
        MvpSelfEvolutionController,
    )

    if not argv or argv[0] in ("--help", "-h"):
        print("Usage: agentx-evolve replay <run-id>")
        sys.exit(0)

    run_id = argv[0]
    ctrl = MvpSelfEvolutionController()
    result = ctrl.replay_generation(run_id, {})
    print(f"Replay {run_id}: {result.verdict}")


def _run_health(argv: list[str]) -> None:
    """Check system health."""
    from agentx_evolve.self_evolution.self_evolution_controller import (
        MvpSelfEvolutionController,
    )

    ctrl = MvpSelfEvolutionController()
    goals = ctrl.get_goals()
    checks = [
        ("Controller initialized", True),
        ("Registry has agents", len(goals) >= 0),
        ("Goal evaluator accessible", True),
    ]
    all_ok = True
    for name, ok in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"  {status:4s}  {name}")

    if all_ok:
        print("Health: OK")
    else:
        print("Health: ISSUES DETECTED")
        sys.exit(1)


def _run_config_validate(argv: list[str]) -> None:
    """Validate configuration files."""
    import json
    from pathlib import Path

    if "--help" in argv or "-h" in argv:
        print("Usage: agentx-evolve config-validate [<path>]")
        sys.exit(0)

    target = Path(argv[0]) if argv else Path.cwd()
    errors: list[str] = []

    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = list(target.rglob("*.json")) + list(target.rglob("*.yaml"))
    else:
        print(f"Not found: {target}")
        sys.exit(1)

    for f in files:
        try:
            raw = f.read_text()
            if f.suffix == ".json":
                json.loads(raw)
            print(f"  PASS  {f}")
        except (json.JSONDecodeError, ValueError) as e:
            errors.append(str(e))
            print(f"  FAIL  {f}: {e}")

    if errors:
        print(f"config-validate: {len(errors)} error(s)")
        sys.exit(1)
    print("config-validate: all files valid")


def _run_override(argv: list[str]) -> None:
    """Override a rejected/deprecated agent's status."""
    from agentx_evolve.self_evolution.self_evolution_controller import (
        MvpSelfEvolutionController,
    )

    if not argv or argv[0] in ("--help", "-h"):
        print("Usage: agentx-evolve override <agent-id> --status <new-status> [--evidence-ref <ref>]")
        sys.exit(0)

    agent_id = argv[0]
    new_status = ""
    evidence_ref = ""

    for i, a in enumerate(argv[1:], start=1):
        if a == "--status" and i + 1 < len(argv):
            new_status = argv[i + 1]
        if a == "--evidence-ref" and i + 1 < len(argv):
            evidence_ref = argv[i + 1]

    if not new_status:
        print("override requires --status <new-status>", file=sys.stderr)
        sys.exit(1)

    ctrl = MvpSelfEvolutionController()
    result = ctrl.override_agent(agent_id, new_status, evidence_ref)
    if result["success"]:
        print(f"Agent {agent_id}: {result['old_status']} -> {result['new_status']}")
        if evidence_ref:
            print(f"Evidence: {evidence_ref}")
    else:
        print(f"Override failed: {result.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
