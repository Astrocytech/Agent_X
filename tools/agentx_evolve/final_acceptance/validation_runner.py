import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acceptance_models import FinalAcceptanceValidationResult, STATUS_PASS, STATUS_FAIL, STATUS_NOT_RUN
from .artifact_writer import write_json_artifact, ensure_runtime_root
from .hash_utils import sha256_file


def run_validation_commands(
    repo_root: Path,
    include_full_pytest: bool = True,
    avoid_recursive_final_acceptance: bool = True,
) -> list[FinalAcceptanceValidationResult]:
    results: list[FinalAcceptanceValidationResult] = []

    compileall = run_single_validation_command(
        repo_root,
        "compileall",
        [sys.executable, "-m", "compileall", str(repo_root / "tools")],
        "compileall_output.txt",
        timeout_seconds=120,
    )
    results.append(compileall)

    if include_full_pytest:
        pytest = run_single_validation_command(
            repo_root,
            "pytest",
            [
                sys.executable, "-m", "pytest",
                str(repo_root / "tools/agentx_evolve/tests"),
                "-x", "--tb=short", "-q",
            ],
            "pytest_output.txt",
            timeout_seconds=180,
        )
        results.append(pytest)
    else:
        results.append(FinalAcceptanceValidationResult(
            command_name="pytest",
            command_text="Full pytest (skipped)",
            status=STATUS_NOT_RUN,
            summary="Skipped per configuration",
        ))

    scoped_pytest = run_single_validation_command(
        repo_root,
        "pytest_final_acceptance",
        [
            sys.executable, "-m", "pytest",
            str(repo_root / "tools/agentx_evolve/tests/test_final_acceptance_*.py"),
            "-x", "--tb=short", "-q",
        ],
        "pytest_final_acceptance_output.txt",
        timeout_seconds=180,
    )
    results.append(scoped_pytest)

    return results


def run_single_validation_command(
    repo_root: Path,
    command_name: str,
    command: list[str],
    output_artifact_name: str,
    timeout_seconds: int = 120,
) -> FinalAcceptanceValidationResult:
    root = ensure_runtime_root(repo_root)
    output_path = root / output_artifact_name

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            timeout=timeout_seconds,
            shell=False,
        )
        exit_code = result.returncode
        stdout = (result.stdout or "") + "\n" + (result.stderr or "")
        output_path.write_text(stdout, encoding="utf-8")
        output_sha = sha256_file(output_path) if output_path.exists() else None
        status = STATUS_PASS if exit_code == 0 else STATUS_FAIL
        summary = f"exit_code={exit_code}, {len(stdout)} chars output"
    except subprocess.TimeoutExpired:
        exit_code = -1
        stdout = f"TIMEOUT after {timeout_seconds}s"
        output_path.write_text(stdout, encoding="utf-8")
        output_sha = sha256_file(output_path) if output_path.exists() else None
        status = STATUS_FAIL
        summary = f"TIMEOUT after {timeout_seconds}s"
    except FileNotFoundError:
        exit_code = -1
        stdout = f"Command not found: {command[0]}"
        output_path.write_text(stdout, encoding="utf-8")
        output_sha = sha256_file(output_path) if output_path.exists() else None
        status = STATUS_FAIL
        summary = stdout

    return FinalAcceptanceValidationResult(
        command_name=command_name,
        command_text=" ".join(str(c) for c in command),
        exit_code=exit_code,
        status=status,
        summary=summary,
        output_artifact_path=str(output_path) if output_path.exists() else None,
        output_sha256=output_sha,
    )


def _result_to_dict(r: FinalAcceptanceValidationResult) -> dict:
    return {
        "schema_version": r.schema_version,
        "schema_id": r.schema_id,
        "source_component": r.source_component,
        "command_name": r.command_name,
        "command_text": r.command_text,
        "exit_code": r.exit_code,
        "status": r.status,
        "summary": r.summary,
        "output_artifact_path": r.output_artifact_path,
        "output_sha256": r.output_sha256,
        "expected_failure": r.expected_failure,
        "expected_failure_condition": r.expected_failure_condition,
        "warnings": r.warnings,
        "errors": r.errors,
    }


def write_validation_results(
    results: list[FinalAcceptanceValidationResult], repo_root: Path,
) -> Path:
    data: dict[str, Any] = {
        "schema_version": "1.0",
        "schema_id": "final_acceptance_validation_result.schema.json",
        "source_component": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
        "results": [_result_to_dict(r) for r in results],
        "warnings": [],
        "errors": [],
    }
    return write_json_artifact(repo_root, "final_acceptance_validation_results.json", data)
