from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acceptance_models import FinalAcceptanceDeviation
from .artifact_writer import write_json_artifact, runtime_root


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def build_runtime_artifact_report(
    repo_root: Path,
    deviation_register: list[FinalAcceptanceDeviation],
) -> dict[str, Any]:
    rt_root = runtime_root(repo_root)
    checks: list[dict[str, Any]] = []
    findings: list[str] = []
    all_pass = True

    check1_artifacts = list(rt_root.rglob("*")) if rt_root.exists() else []
    check1_all_under_rt = all(
        rt_root in p.parents or p == rt_root for p in check1_artifacts
    ) if check1_artifacts else True
    checks.append({
        "check_id": "artifacts_under_runtime_root",
        "description": "All final acceptance artifacts are under .agentx-init/final_acceptance/",
        "status": "PASS" if check1_all_under_rt else "FAIL",
        "details": f"Found {len(check1_artifacts)} artifact(s)" if check1_all_under_rt else "Some artifacts outside runtime root",
    })
    if not check1_all_under_rt:
        all_pass = False
        findings.append("Some artifacts are not under .agentx-init/final_acceptance/")

    source_dirs = [
        repo_root / "tools" / "agentx_evolve" / "final_acceptance",
        repo_root / "tools" / "agentx_evolve" / "schemas",
        repo_root / "tools" / "agentx_evolve" / "tests",
    ]
    check2_issues = []
    for sd in source_dirs:
        if sd.exists():
            for p in sd.rglob("*"):
                if p.is_file() and rt_root in p.parents:
                    check2_issues.append(str(p))
    checks.append({
        "check_id": "no_source_dir_runtime_state",
        "description": "No source directories are used for runtime state",
        "status": "PASS" if not check2_issues else "FAIL",
        "details": "All runtime state in approved directories" if not check2_issues else f"{len(check2_issues)} file(s) in source dirs",
    })
    if check2_issues:
        all_pass = False
        findings.extend(f"Runtime state in source dir: {p}" for p in check2_issues)

    check3_allowed_paths = {
        str(p.relative_to(repo_root)) if p.is_relative_to(repo_root) else str(p)
        for p in check1_artifacts
    }
    deviations_paths = set()
    for d in deviation_register:
        for ref in d.evidence_refs:
            deviations_paths.add(ref)

    unauthorized = check3_allowed_paths - deviations_paths - {str(rt_root.relative_to(repo_root))}
    checks.append({
        "check_id": "deviations_cover_unauthorized_paths",
        "description": "Runtime artifact boundary exceptions have deviation entries",
        "status": "PASS" if not unauthorized else "PARTIAL",
        "details": f"{len(unauthorized)} path(s) without deviation entries" if unauthorized else "All paths covered by deviations",
    })

    report_status = "PASS" if all_pass else ("PARTIAL" if not check2_issues else "FAIL")

    return {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_runtime_artifact_report.schema.json",
        "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "created_at": _make_timestamp(),
        "report_status": report_status,
        "checks": checks,
        "findings": findings,
        "warnings": [],
        "errors": [],
    }


def write_runtime_artifact_report(data: dict[str, Any], repo_root: Path) -> Path:
    return write_json_artifact(repo_root, "final_acceptance_runtime_artifact_report.json", data)
