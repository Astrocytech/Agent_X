"""Unified Agent_X CLI — dispatches to agentx-init and agentx-evolve.

Item 20: Single coherent entry point for all Agent_X workflows.
"""

import os
import sys
from pathlib import Path


_TOOLS = Path(__file__).resolve().parent.parent


def _init_initiator_path() -> None:
    initiator = str(_TOOLS / "agentx_initiator")
    if initiator not in sys.path:
        sys.path.insert(0, initiator)


def _init_evolve_path() -> None:
    evolve = str(_TOOLS / "agentx_evolve")
    if evolve not in sys.path:
        sys.path.insert(0, evolve)


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        _print_help()
        sys.exit(0)

    cmd = args[0]

    # Init commands
    if cmd in ("scan", "status", "audit", "explain", "plan", "propose", "validate", "report", "graph"):
        _init_initiator_path()
        from agentx_initiator.cli.main import main as init_main
        sys.argv = ["agentx", *args]
        init_main()

    # Evolve commands
    elif cmd in ("review", "approve", "reject", "chat", "self-upgrade",
                  "init-agent", "evolve-agent", "inverse", "version"):
        _init_evolve_path()
        from agentx_evolve.__main__ import main as evolve_main
        sys.argv = ["agentx-evolve", *args]
        evolve_main()

    # Clean workspace / replay
    elif cmd == "clean-run":
        _init_evolve_path()
        from agentx_evolve.clean_workspace.clean_workspace_runner import run_clean
        import json
        result = run_clean()
        print(json.dumps(result, indent=2))

    # Generate final artifacts
    elif cmd == "generate-artifacts":
        from agentx_evolve.final_acceptance.generate_artifacts import main as gen_main
        gen_main()

    # Registry commands
    elif cmd == "registry":
        sub = args[1] if len(args) > 1 else ""
        if sub == "discover-schemas":
            _init_evolve_path()
            from agentx_evolve.registry.schema_registry import SchemaRegistry
            from pathlib import Path as P
            reg = SchemaRegistry()
            roots = [P("schemas"), P("tools/agentx_evolve/schemas"),
                     P("benchmarks/benchcore"), P("L2/ecosystem/ecosystem-schemas")]
            discovered = reg.discover(roots)
            print(f"Discovered {len(discovered)} schemas")
            Path(".agentx-init/registry/schema_registry.json").parent.mkdir(parents=True, exist_ok=True)
            reg.save(P(".agentx-init/registry/schema_registry.json"))
        elif sub == "register-requirements":
            _init_evolve_path()
            from agentx_evolve.registry.requirement_registry import RequirementRegistry, Requirement
            from pathlib import Path as P
            reg = RequirementRegistry()
            # Register known requirements from benchmark artifacts
            import json
            req_path = P("benchmarks/benchcore/requirements/requirements.json")
            if req_path.is_file():
                with open(req_path) as f:
                    for req_data in json.load(f):
                        reg.register(Requirement(
                            requirement_id=req_data.get("requirement_id", ""),
                            statement=req_data.get("statement", ""),
                            source_plans=[req_data.get("source_ids", [])] if isinstance(req_data.get("source_ids"), str) else req_data.get("source_ids", []),
                            requirement_class="mandatory",
                            status=req_data.get("status", "implemented"),
                        ))
            Path(".agentx-init/registry/requirement_registry.json").parent.mkdir(parents=True, exist_ok=True)
            reg.save(P(".agentx-init/registry/requirement_registry.json"))
            print(f"Registered {len(reg.all_requirements())} requirements")
        else:
            print("Registry subcommands: discover-schemas, register-requirements")
    else:
        print(f"Unknown command: {cmd}")
        print("Run 'agentx help' for available commands.")
        sys.exit(1)


def _print_help() -> None:
    print("Usage: agentx <command> [options]")
    print()
    print("Initiation commands (read-only analysis):")
    print("  scan                          Scan repository structure")
    print("  status                        Show Agent_X status")
    print("  audit                         Audit repository")
    print("  explain                       Explain session or structure")
    print("  plan                          Generate implementation plan")
    print("  propose                       Generate a proposal")
    print("  validate                      Validate artifacts")
    print("  report                        Generate report")
    print("  graph                         Visualize dependencies")
    print()
    print("Evolution commands (governed changes):")
    print("  review <session_id>           Review an implementation session")
    print("  approve <session_id>          Approve a session")
    print("  reject <session_id>           Reject a session")
    print("  chat [options]                Chat with an LLM provider")
    print("  init-agent [options]          Initialize a new agent")
    print("  evolve-agent [options]        Evolve an external agent")
    print("  self-upgrade [options]        Self-upgrade plan or apply")
    print("  inverse <subcommand>          Inverse science planning")
    print()
    print("Pipeline commands:")
    print("  clean-run                     Run in clean temp workspace")
    print("  generate-artifacts            Generate final acceptance artifacts")
    print("  registry discover-schemas     Discover and index all JSON schemas")
    print("  registry register-requirements Index requirements from benchmarks")
    print()
    print("Utility:")
    print("  version                       Show version")


if __name__ == "__main__":
    main()
