from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from agentx_evolve.evaluation.evaluation_runner import run_evaluation


def run_evaluation_from_config(config_path: str, repo_root: str, **overrides) -> dict:
    config = {}
    if config_path:
        p = Path(config_path)
        if p.exists():
            config = json.loads(p.read_text())
    config.update(overrides)
    suite_path = Path(config.get("suite_path", ""))
    if not suite_path.is_absolute():
        suite_path = Path(repo_root) / suite_path
    repo_root_path = Path(repo_root)
    run = run_evaluation(
        suite_path=suite_path,
        repo_root=repo_root_path,
        run_config_path=Path(config_path) if config_path else None,
        first_run=config.get("first_run", False),
        execution_mode=config.get("execution_mode", "OFFLINE_FIXTURE"),
        dry_run=config.get("dry_run", False),
        allow_tool_adapter_cases=config.get("allow_tool_adapter_cases", False),
        write_reports=config.get("write_reports", True),
        write_evidence=config.get("write_evidence", True),
        allow_candidate_baseline_write=config.get("allow_candidate_baseline_write", False),
    )
    return {
        "run_id": run.run_id,
        "suite_id": run.suite_id,
        "status": run.score_summary.get("status", "COMPLETED") if isinstance(run.score_summary, dict) else "COMPLETED",
        "total_cases": len(run.case_results),
        "passed": sum(1 for r in run.case_results if r.passed),
        "failed": sum(1 for r in run.case_results if not r.passed and r.status not in ("EVAL_SKIPPED",)),
        "skipped": sum(1 for r in run.case_results if r.status == "EVAL_SKIPPED"),
        "score_summary": run.score_summary,
        "threshold_summary": run.threshold_summary,
        "regression_summary": run.regression_summary,
        "warnings": run.warnings,
        "errors": run.errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent-X Evaluation Harness CLI")
    parser.add_argument("--suite", required=True, help="Path to benchmark suite JSON")
    parser.add_argument("--repo", required=True, help="Repository root path")
    parser.add_argument("--config", help="Run config JSON path")
    parser.add_argument("--first-run", action="store_true", help="First run (no baseline)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    parser.add_argument("--execution-mode", default="OFFLINE_FIXTURE", choices=["OFFLINE_FIXTURE", "CONTROLLED_TOOL_ADAPTER"])
    parser.add_argument("--write-reports", default=True, action=argparse.BooleanOptionalAction)
    parser.add_argument("--write-evidence", default=True, action=argparse.BooleanOptionalAction)
    parser.add_argument("--allow-tool-adapter-cases", action="store_true")
    parser.add_argument("--allow-candidate-baseline-write", action="store_true")
    args = parser.parse_args()
    try:
        result = run_evaluation_from_config(
            config_path=args.config or "",
            repo_root=args.repo,
            suite_path=args.suite,
            first_run=args.first_run,
            execution_mode=args.execution_mode,
            dry_run=args.dry_run,
            write_reports=args.write_reports,
            write_evidence=args.write_evidence,
            allow_tool_adapter_cases=args.allow_tool_adapter_cases,
            allow_candidate_baseline_write=args.allow_candidate_baseline_write,
        )
        print(json.dumps(result, indent=2))
        if result["errors"]:
            sys.exit(1)
    except Exception as e:
        print(f"Evaluation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
