import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .acceptance_models import (
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
    ALL_MODES, VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS,
)
from .mode_policy import validate_acceptance_mode
from .acceptance_runner import run_final_acceptance
from .schema_validator import validate_final_acceptance_schemas, write_schema_validation_results


def _find_repo_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return cwd


def _handle_run(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root) if args.repo_root else _find_repo_root()

    mode_errors = validate_acceptance_mode(args.mode)
    if mode_errors:
        for err in mode_errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    result = run_final_acceptance(
        repo_root=repo_root,
        acceptance_mode=args.mode,
        reviewed_commit=args.commit,
        reviewed_branch=args.branch,
        bootstrap_self=args.bootstrap_self,
        skip_validation_commands=args.skip_validation,
        skip_schema_validation=args.skip_schema_validation,
        skip_cross_layer_checks=args.skip_cross_layer,
        include_full_pytest=not args.no_full_pytest,
        avoid_recursive_final_acceptance=not args.no_avoid_recursive,
        no_safe_deferrals=args.no_safe_deferrals,
    )

    verdict = result.get("final_verdict", "NOT_ACCEPTED")
    rating = result.get("implementation_rating", 0.0)
    blockers = result.get("blockers", [])
    high = result.get("high_issues", [])
    non_blocking = result.get("non_blocking_followups", [])
    errors = result.get("errors", [])

    print(f"Verdict: {verdict}")
    print(f"Rating:  {rating:.4f}")
    if blockers:
        print(f"Blockers ({len(blockers)}):")
        for b in blockers:
            print(f"  ! {b}")
    if high:
        print(f"High Issues ({len(high)}):")
        for h in high:
            print(f"  - {h}")
    if non_blocking:
        print(f"Non-blocking ({len(non_blocking)}):")
        for n in non_blocking:
            print(f"  * {n}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  ERR: {e}")

    if args.output_json:
        output = Path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        print(f"Results saved to {output}")

    if verdict in (VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS):
        return 0
    return 1


def _handle_report(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root) if args.repo_root else _find_repo_root()
    report_paths = [
        repo_root / ".agentx-init" / "final_acceptance" / "final_acceptance_report.json",
        repo_root / ".agentx-init" / "final_acceptance" / "latest_final_acceptance_result.json",
    ]
    found = False
    for p in report_paths:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                print(json.dumps(data, indent=2, default=str))
                found = True
                break
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error reading {p}: {e}", file=sys.stderr)
    if not found:
        print("No report found. Run 'agentx-evolve final-acceptance run' first.", file=sys.stderr)
        return 1
    return 0


def _handle_check(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root) if args.repo_root else _find_repo_root()
    results = validate_final_acceptance_schemas(repo_root)
    all_pass = all(r.status == "PASS" for r in results)
    for r in results:
        symbol = "PASS" if r.status == "PASS" else "FAIL"
        print(f"[{symbol}] {r.summary}")
    if args.output:
        write_schema_validation_results(results, repo_root)
        print(f"Results written to {repo_root / '.agentx-init' / 'final_acceptance' / 'final_acceptance_schema_validation_results.json'}")
    return 0 if all_pass else 1


def _handle_validate_schemas(args: argparse.Namespace) -> int:
    return _handle_check(args)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="final-acceptance",
        description="Agent X Final System Acceptance Layer (Layer 22)",
    )
    parser.add_argument(
        "--repo-root",
        help="Repository root path (auto-detected if not provided)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run final acceptance validation")
    run_parser.add_argument(
        "--mode", choices=sorted(ALL_MODES), default=MODE_IMPLEMENTATION_ACCEPTANCE,
        help="Acceptance mode (default: IMPLEMENTATION_ACCEPTANCE)",
    )
    run_parser.add_argument("--commit", help="Reviewed commit SHA")
    run_parser.add_argument("--branch", help="Reviewed branch name")
    run_parser.add_argument(
        "--bootstrap-self", action="store_true",
        help="Enable bootstrap self-validation mode",
    )
    run_parser.add_argument(
        "--skip-validation", action="store_true",
        help="Skip validation commands (compileall, pytest)",
    )
    run_parser.add_argument(
        "--skip-schema-validation", action="store_true",
        help="Skip schema validation checks",
    )
    run_parser.add_argument(
        "--skip-cross-layer", action="store_true",
        help="Skip cross-layer dependency checks",
    )
    run_parser.add_argument(
        "--no-full-pytest", action="store_true",
        help="Skip full pytest run (scoped tests only)",
    )
    run_parser.add_argument(
        "--no-avoid-recursive", action="store_true",
        help="Allow recursive final acceptance test discovery",
    )
    run_parser.add_argument(
        "--no-safe-deferrals", action="store_true",
        help="Reject all safe deferrals, treating them as blockers",
    )
    run_parser.add_argument(
        "--output-json", help="Path to write JSON results output",
    )
    run_parser.set_defaults(func=_handle_run)

    report_parser = subparsers.add_parser("report", help="Show last acceptance report")
    report_parser.set_defaults(func=_handle_report)

    check_parser = subparsers.add_parser("check", help="Validate JSON schemas")
    check_parser.add_argument(
        "--output", action="store_true",
        help="Write validation results to runtime directory",
    )
    check_parser.set_defaults(func=_handle_check)

    validate_schemas_parser = subparsers.add_parser(
        "validate-schemas", help="Validate final acceptance JSON schemas",
    )
    validate_schemas_parser.add_argument(
        "--output", action="store_true",
        help="Write validation results to runtime directory",
    )
    validate_schemas_parser.set_defaults(func=_handle_validate_schemas)

    parsed = parser.parse_args(argv)
    return parsed.func(parsed)


if __name__ == "__main__":
    sys.exit(main())
