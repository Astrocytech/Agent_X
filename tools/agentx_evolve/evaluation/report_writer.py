from __future__ import annotations
from pathlib import Path
import json

from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun, EvaluationReport,
    utc_now_iso, new_eval_id, to_dict,
)
from agentx_evolve.evaluation.evaluation_errors import EVAL_REPORT_WRITE_FAILED


def write_evaluation_report(run: EvaluationRun, repo_root: Path) -> dict:
    report = EvaluationReport(
        report_id=new_eval_id("report"),
        run_id=run.run_id,
        suite_id=run.suite_id,
        timestamp=utc_now_iso(),
        status=run.score_summary.get("status", "UNKNOWN") if isinstance(run.score_summary, dict) else "UNKNOWN",
        summary=f"Evaluation run {run.run_id} for suite {run.suite_id}",
        score_summary=run.score_summary,
        threshold_summary=run.threshold_summary,
        regression_summary=run.regression_summary,
        case_summaries=[
            {
                "case_id": r.case_id,
                "status": r.status,
                "passed": r.passed,
                "score": r.score,
                "message": r.message[:200] if r.message else "",
                "failure_class": r.failure_class,
            }
            for r in run.case_results
        ],
        artifact_refs=run.artifact_refs,
        evidence_refs=run.evidence_refs,
        warnings=run.warnings,
        errors=run.errors,
    )
    json_path = write_evaluation_report_json(report, repo_root)
    md_path = write_evaluation_report_md(report, repo_root)
    latest_path = write_latest_evaluation_run(report, repo_root)
    return {
        "report": to_dict(report),
        "json_path": str(json_path),
        "md_path": str(md_path),
        "latest_path": str(latest_path),
    }


def write_evaluation_report_json(report: EvaluationReport, repo_root: Path) -> Path:
    report_dir = repo_root / ".agentx-init" / "evaluation" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{report.report_id}_evaluation_report.json"
    path.write_text(json.dumps(to_dict(report), indent=2))
    return path


def write_evaluation_report_md(report: EvaluationReport, repo_root: Path) -> Path:
    report_dir = repo_root / ".agentx-init" / "evaluation" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Evaluation Report: {report.report_id}",
        f"",
        f"**Suite:** {report.suite_id}",
        f"**Run:** {report.run_id}",
        f"**Timestamp:** {report.timestamp}",
        f"**Status:** {report.status}",
        f"",
        f"## Score Summary",
        f"```json",
        f"{json.dumps(report.score_summary, indent=2)}",
        f"```",
        f"",
        f"## Threshold Summary",
        f"```json",
        f"{json.dumps(report.threshold_summary, indent=2)}",
        f"```",
    ]
    if report.regression_summary:
        lines.extend([
            f"",
            f"## Regression Summary",
            f"```json",
            f"{json.dumps(report.regression_summary, indent=2)}",
            f"```",
        ])
    lines.extend([
        f"",
        f"## Case Results ({len(report.case_summaries)} cases)",
    ])
    for cs in report.case_summaries:
        lines.append(f"- **{cs['case_id']}**: {cs['status']} (score={cs['score']})")
    lines.extend([
        f"",
        f"## Final Verdict",
        f"**{report.status}**",
    ])
    path = report_dir / f"{report.report_id}_evaluation_report.md"
    path.write_text("\n".join(lines))
    return path


def write_latest_evaluation_run(run: EvaluationRun, repo_root: Path) -> Path:
    latest_dir = repo_root / ".agentx-init" / "evaluation" / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    path = latest_dir / "latest_evaluation_run.json"
    path.write_text(json.dumps(to_dict(run), indent=2))
    return path


def write_latest_evaluation_report(report: EvaluationReport, repo_root: Path) -> Path:
    latest_dir = repo_root / ".agentx-init" / "evaluation" / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    path = latest_dir / "latest_evaluation_report.json"
    path.write_text(json.dumps(to_dict(report), indent=2))
    return path
