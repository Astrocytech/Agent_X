from __future__ import annotations

import compileall
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    INSTALL_MODE_ARCHIVE_EXTRACT,
    VALIDATION_STATUS_FAIL,
    VALIDATION_STATUS_PASS,
    CommandRecord,
    InstallValidationReport,
    PackageManifest,
    new_id,
    tmp_dir,
    utc_now_iso,
    write_json_atomic,
)


def _extract_archive(package_artifact: Path, extract_to: Path) -> None:
    suffix = "".join(package_artifact.suffixes)
    if package_artifact.name.endswith(".tar.gz") or suffix in (".tar", ".tgz"):
        with tarfile.open(package_artifact, "r:*") as tf:
            tf.extractall(path=extract_to)
    elif package_artifact.name.endswith(".zip"):
        with zipfile.ZipFile(package_artifact, "r") as zf:
            zf.extractall(path=extract_to)
    else:
        raise ValueError(f"Unsupported archive format: {package_artifact.name}")


def _extracted_contents(extract_to: Path) -> list[str]:
    return sorted(
        str(p.relative_to(extract_to))
        for p in extract_to.rglob("*")
        if p.is_file()
    )


def _compile_python_files(extract_to: Path) -> CommandRecord:
    record = CommandRecord(
        name="compile_python",
        command=f"python -m compileall {extract_to}",
        status="PASS",
        summary="Compileall completed on extracted Python files",
    )
    try:
        res = subprocess.run(
            ["python", "-m", "compileall", str(extract_to)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        record.exit_code = res.returncode
        if res.returncode != 0:
            record.status = "FAIL"
            record.stderr_summary = res.stderr[:500] if res.stderr else ""
            record.errors.append(f"compileall failed with exit code {res.returncode}")
        record.stdout_summary = res.stdout[:500] if res.stdout else ""
    except Exception as exc:
        record.status = "FAIL"
        record.errors.append(f"compileall execution error: {exc}")
    return record


def validate_local_install(
    package_artifact: Path,
    manifest: PackageManifest,
    repo_root: Path,
) -> InstallValidationReport:
    tmp_root = tmp_dir(repo_root)
    temp_validation = tmp_root / f"install_{new_id('val')}"
    temp_validation.mkdir(parents=True, exist_ok=True)

    report = InstallValidationReport(
        report_id=new_id("install"),
        created_at=utc_now_iso(),
        package_artifact=str(package_artifact.resolve()),
        validation_mode=INSTALL_MODE_ARCHIVE_EXTRACT,
        network_allowed=False,
        temp_validation_root=str(temp_validation.resolve()),
        status=VALIDATION_STATUS_PASS,
    )

    commands_run: list[CommandRecord] = []

    try:
        extract_cmd = CommandRecord(
            name="extract_archive",
            command=f"extract {package_artifact.name} to {temp_validation}",
            exit_code=0,
            status="PASS",
            summary=f"Extracted {package_artifact.name}",
        )
        try:
            _extract_archive(package_artifact, temp_validation)
        except Exception as exc:
            extract_cmd.exit_code = 1
            extract_cmd.status = "FAIL"
            extract_cmd.errors.append(f"Extraction failed: {exc}")
            report.status = VALIDATION_STATUS_FAIL
            report.errors.append(str(exc))
        commands_run.append(extract_cmd)

        verify_cmd = CommandRecord(
            name="verify_contents",
            command="check extracted files exist",
            exit_code=0,
            status="PASS",
            summary="Verified extracted contents",
        )
        contents = _extracted_contents(temp_validation)
        if not contents:
            verify_cmd.exit_code = 1
            verify_cmd.status = "FAIL"
            verify_cmd.errors.append("No files found after extraction")
            report.status = VALIDATION_STATUS_FAIL
            report.errors.append("Extraction produced no files")
        commands_run.append(verify_cmd)

        py_files = [p for p in contents if p.endswith(".py")]
        if py_files:
            compile_record = _compile_python_files(temp_validation)
            commands_run.append(compile_record)
            if compile_record.status == "FAIL":
                report.status = VALIDATION_STATUS_FAIL
                report.errors.append("compileall validation failed")

        report.commands_run = commands_run
    except Exception as exc:
        report.status = VALIDATION_STATUS_FAIL
        report.errors.append(f"Install validation failed: {exc}")
    finally:
        if temp_validation.exists():
            shutil.rmtree(temp_validation)

    return report
