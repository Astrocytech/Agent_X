import argparse
import json
import sys
from pathlib import Path

from .doc_controller import (
    run_documentation_sync,
    run_scan_only,
    run_validate_only,
    run_plan_only,
    run_apply_generated,
)
from .doc_models import utc_now_iso
from .validate_docs_sync_schemas import validate_all_docs_sync_schemas


def _find_repo_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return cwd


def _handle_sync(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root) if args.repo_root else _find_repo_root()
    result = run_documentation_sync(
        repo_root=repo_root,
        mode=args.mode,
        policy_context=args.policy_context or None,
        reviewed_commit=args.commit,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("status") not in ("BLOCKED", "FAILED") else 1


def _handle_scan(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root) if args.repo_root else _find_repo_root()
    result = run_scan_only(repo_root=repo_root)
    print(json.dumps(result, indent=2, default=str))
    return 0


def _handle_validate(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root) if args.repo_root else _find_repo_root()
    exit_code = validate_all_docs_sync_schemas(repo_root)
    result = run_validate_only(repo_root=repo_root)
    print(json.dumps(result, indent=2, default=str))
    return exit_code if exit_code else 0


def _handle_plan(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root) if args.repo_root else _find_repo_root()
    result = run_plan_only(
        repo_root=repo_root,
        policy_context=args.policy_context or None,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("status") not in ("BLOCKED", "FAILED") else 1


def _handle_apply(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root) if args.repo_root else _find_repo_root()
    result = run_apply_generated(
        repo_root=repo_root,
        policy_context=args.policy_context or None,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("status") not in ("BLOCKED", "FAILED") else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="docs-sync",
        description="Documentation Synchronization Layer CLI",
    )
    parser.add_argument(
        "--repo-root",
        help="Repository root path (auto-detected if not provided)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync", help="Run full documentation sync")
    sync_parser.add_argument(
        "--mode", default="SCAN_PLAN",
        help="Sync mode (default: SCAN_PLAN)",
    )
    sync_parser.add_argument("--commit", help="Reviewed commit SHA")
    sync_parser.add_argument(
        "--policy-context", type=json.loads, default="{}",
        help="JSON policy context string",
    )
    sync_parser.set_defaults(func=_handle_sync)

    scan_parser = subparsers.add_parser("scan", help="Scan documentation only")
    scan_parser.set_defaults(func=_handle_scan)

    validate_parser = subparsers.add_parser("validate", help="Validate schemas and documentation")
    validate_parser.set_defaults(func=_handle_validate)

    plan_parser = subparsers.add_parser("plan", help="Generate sync plan only")
    plan_parser.add_argument(
        "--policy-context", type=json.loads, default="{}",
        help="JSON policy context string",
    )
    plan_parser.set_defaults(func=_handle_plan)

    apply_parser = subparsers.add_parser("apply", help="Apply generated updates")
    apply_parser.add_argument(
        "--policy-context", type=json.loads, default="{}",
        help="JSON policy context string",
    )
    apply_parser.set_defaults(func=_handle_apply)

    parsed = parser.parse_args(argv)
    return parsed.func(parsed)


if __name__ == "__main__":
    sys.exit(main())
