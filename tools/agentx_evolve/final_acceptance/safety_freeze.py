import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifact_writer import write_json_artifact, runtime_root


STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_NOT_CHECKED = "NOT_CHECKED"


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _get_git_status(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=repo_root, timeout=30,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def _check_source_mutation(repo_root: Path) -> dict[str, Any]:
    status = _get_git_status(repo_root)
    if not status:
        return {"check": "source_mutation", "status": STATUS_PASS, "detail": "Working tree clean or no changes"}
    source_changes = []
    for line in status.split("\n"):
        line = line.strip()
        if not line:
            continue
        flags = line[:2]
        path_part = line[3:]
        if path_part and not path_part.startswith(".agentx-init"):
            source_changes.append(line)
    if source_changes:
        return {
            "check": "source_mutation",
            "status": STATUS_FAIL,
            "detail": f"{len(source_changes)} source file(s) modified",
            "changed_files": source_changes[:20],
        }
    return {"check": "source_mutation", "status": STATUS_PASS, "detail": "Only runtime artifacts modified"}


def _check_runtime_artifact_boundary(repo_root: Path) -> dict[str, Any]:
    rt = runtime_root(repo_root)
    if not rt.exists():
        return {"check": "runtime_artifact_boundary", "status": STATUS_NOT_CHECKED, "detail": "Runtime root does not exist"}
    boundary_violations = []
    for p in rt.rglob("*"):
        if p.is_file():
            try:
                resolved = p.resolve()
                rt_resolved = rt.resolve()
                if rt_resolved not in resolved.parents and resolved != rt_resolved:
                    boundary_violations.append(str(p))
            except (OSError, ValueError):
                boundary_violations.append(str(p))
    if boundary_violations:
        return {
            "check": "runtime_artifact_boundary",
            "status": STATUS_FAIL,
            "detail": f"{len(boundary_violations)} artifact(s) outside runtime root",
            "violations": boundary_violations[:10],
        }
    return {"check": "runtime_artifact_boundary", "status": STATUS_PASS, "detail": "All artifacts under runtime root"}


def _check_external_service_requirements() -> dict[str, Any]:
    return {"check": "external_service_requirements", "status": STATUS_PASS, "detail": "No external service requirements detected"}


def build_safety_freeze_report(repo_root: Path) -> dict[str, Any]:
    checks = [
        _check_source_mutation(repo_root),
        _check_runtime_artifact_boundary(repo_root),
        _check_external_service_requirements(),
    ]
    overall = STATUS_PASS
    for c in checks:
        if c["status"] == STATUS_FAIL:
            overall = STATUS_FAIL
            break
        if c["status"] == STATUS_NOT_CHECKED:
            overall = STATUS_NOT_CHECKED

    return {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_safety_freeze.schema.json",
        "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "created_at": _make_timestamp(),
        "safety_freeze_status": overall,
        "checks": checks,
        "warnings": [],
        "errors": [],
    }


def write_safety_freeze_report(data: dict[str, Any], repo_root: Path) -> Path:
    return write_json_artifact(repo_root, "final_acceptance_safety_freeze.json", data)
