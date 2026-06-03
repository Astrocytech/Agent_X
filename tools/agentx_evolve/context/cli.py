import argparse
import json
import sys
from pathlib import Path
from typing import Any

from agentx_evolve.context.task_pack_builder import build_task_pack
from agentx_evolve.context.task_pack_validator import validate_task_pack, validate_context_pack
from agentx_evolve.context.context_artifact_writer import write_context_pack_artifacts


def _find_repo_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return cwd


def _load_json(path_str: str) -> dict:
    path = Path(path_str)
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: failed to parse {path}: {e}", file=sys.stderr)
        sys.exit(1)


def _write_output(data: Any, path: str | None) -> None:
    if path:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        print(f"Output written to {out}")
    else:
        print(json.dumps(data, indent=2, default=str))


def _handle_build(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root) if args.repo_root else _find_repo_root()
    raw_task = _load_json(args.task)
    source_requests = _load_json(args.sources)

    builder_context = {}
    if args.model_profile:
        builder_context["model_profile"] = _load_json(args.model_profile)
    if args.runtime_profile:
        builder_context["runtime_profile"] = _load_json(args.runtime_profile)
    if args.tool_registry:
        builder_context["tool_registry"] = _load_json(args.tool_registry)
    if args.policy_context:
        builder_context["policy_context"] = _load_json(args.policy_context)
    if args.max_context_tokens:
        builder_context["max_context_tokens"] = args.max_context_tokens
    if args.reserved_output_tokens:
        builder_context["reserved_output_tokens"] = args.reserved_output_tokens

    task_pack = build_task_pack(
        raw_task=raw_task,
        source_requests=source_requests,
        builder_context=builder_context,
        repo_root=repo_root,
    )

    _write_output(task_pack.to_dict() if hasattr(task_pack, "to_dict") else task_pack, args.output)
    return 0 if not task_pack.errors else 1


def _handle_validate(args: argparse.Namespace) -> int:
    target = _load_json(args.file)

    if "task_pack_id" in target:
        from agentx_evolve.context.context_models import TaskPack

        tp_fields = {k: v for k, v in target.items() if k in TaskPack.__dataclass_fields__}
        task_pack = TaskPack(**tp_fields)
        result = validate_task_pack(task_pack)
    elif "context_pack_id" in target:
        from agentx_evolve.context.context_models import ContextPack

        cp_fields = {k: v for k, v in target.items() if k in ContextPack.__dataclass_fields__}
        context_pack = ContextPack(**cp_fields)
        result = validate_context_pack(context_pack)
    else:
        print("ERROR: input must contain 'task_pack_id' or 'context_pack_id'", file=sys.stderr)
        return 1

    _write_output(result, args.output)
    return 0 if result.get("status") in ("READY", "PASS") else 1


def _handle_pack(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root) if args.repo_root else _find_repo_root()

    if args.task_pack:
        task_pack_data = _load_json(args.task_pack)
        from agentx_evolve.context.context_models import TaskPack

        tp_fields = {k: v for k, v in task_pack_data.items() if k in TaskPack.__dataclass_fields__}
        if "context_pack" in tp_fields and isinstance(tp_fields["context_pack"], dict):
            from agentx_evolve.context.context_models import ContextPack

            cp_data = tp_fields["context_pack"]
            cp_fields = {k: v for k, v in cp_data.items() if k in ContextPack.__dataclass_fields__}
            tp_fields["context_pack"] = ContextPack(**cp_fields)
        task_pack = TaskPack(**tp_fields)
    else:
        raw_task = _load_json(args.task)
        source_requests = _load_json(args.sources)
        task_pack = build_task_pack(raw_task, source_requests, repo_root=repo_root)

    result = write_context_pack_artifacts(task_pack, repo_root, skip_validation=args.skip_validation)
    _write_output(result, args.output)
    return 0 if not task_pack.errors else 1


def _handle_inspect(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root) if args.repo_root else _find_repo_root()
    artifact_root = repo_root / ".agentx-init" / "context_packs"

    candidates = {
        "context-pack": artifact_root / "latest_context_pack.json",
        "task-pack": artifact_root / "latest_task_pack.json",
        "evidence": artifact_root / "context_pack_evidence.json",
        "history": artifact_root / "context_pack_history.jsonl",
    }

    target = args.target or "context-pack"
    path = candidates.get(target)
    if not path:
        print(f"ERROR: unknown target '{target}'. choose: {', '.join(candidates)}", file=sys.stderr)
        return 1

    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1

    if path.suffix == ".jsonl":
        for line in path.read_text().strip().split("\n"):
            if line.strip():
                print(json.dumps(json.loads(line), indent=2))
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        print(json.dumps(data, indent=2, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="context-builder",
        description="Agent X Context Builder Task Packer Layer",
    )
    parser.add_argument(
        "--repo-root",
        help="Repository root path (auto-detected if not provided)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build a task pack from source")
    build_parser.add_argument("--task", required=True, help="Path to raw task JSON file")
    build_parser.add_argument("--sources", required=True, help="Path to source requests JSON file")
    build_parser.add_argument("--model-profile", help="Path to model profile JSON")
    build_parser.add_argument("--runtime-profile", help="Path to runtime profile JSON")
    build_parser.add_argument("--tool-registry", help="Path to tool registry JSON")
    build_parser.add_argument("--policy-context", help="Path to policy context JSON")
    build_parser.add_argument("--max-context-tokens", type=int, help="Override max context tokens")
    build_parser.add_argument("--reserved-output-tokens", type=int, help="Override reserved output tokens")
    build_parser.add_argument("--output", help="Path to write output JSON")
    build_parser.set_defaults(func=_handle_build)

    validate_parser = subparsers.add_parser("validate", help="Validate a task pack or context pack")
    validate_parser.add_argument("--file", required=True, help="Path to task pack or context pack JSON")
    validate_parser.add_argument("--output", help="Path to write validation result JSON")
    validate_parser.set_defaults(func=_handle_validate)

    pack_parser = subparsers.add_parser("pack", help="Create a context pack artifact")
    pack_parser.add_argument("--task-pack", help="Path to existing task pack JSON")
    pack_parser.add_argument("--task", help="Path to raw task JSON (builds if --task-pack not given)")
    pack_parser.add_argument("--sources", help="Path to source requests JSON (builds if --task-pack not given)")
    pack_parser.add_argument("--skip-validation", action="store_true", help="Skip validation before writing")
    pack_parser.add_argument("--output", help="Path to write artifact metadata JSON")
    pack_parser.set_defaults(func=_handle_pack)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect context artifacts")
    inspect_parser.add_argument(
        "target", nargs="?", default="context-pack",
        choices=["context-pack", "task-pack", "evidence", "history"],
        help="Artifact to inspect (default: context-pack)",
    )
    inspect_parser.set_defaults(func=_handle_inspect)

    parsed = parser.parse_args(argv)
    return parsed.func(parsed)


if __name__ == "__main__":
    sys.exit(main())
