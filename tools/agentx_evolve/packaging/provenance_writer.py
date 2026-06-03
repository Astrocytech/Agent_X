from __future__ import annotations
import os
import platform
import subprocess
import sys
from pathlib import Path
from agentx_evolve.packaging.packaging_models import (
    PackageManifest,
    PackageProvenance,
    canonical_json,
    new_id,
    redact_sensitive_text,
    sha256_bytes,
    sha256_file,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def get_git_commit(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def get_git_branch(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            timeout=30,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            return branch if branch else None
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def get_git_status(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            timeout=30,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if not output:
                return "CLEAN"
            return "DIRTY"
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return "UNKNOWN"


def get_build_environment() -> dict:
    env: dict = {
        "python_version": sys.version.split()[0],
        "python_full_version": sys.version.strip(),
        "platform": sys.platform,
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
    }
    raw_env = {k: v for k, v in os.environ.items()}
    redacted_env = {k: redact_sensitive_text(v) for k, v in raw_env.items()}
    env["environment_variables"] = redacted_env
    return env


def write_package_provenance(
    repo_root: Path,
    manifest: PackageManifest,
    package_artifact: Path,
    package_sha256: str,
    build_command: str,
    output_path: Path,
) -> PackageProvenance:
    manifest_path = repo_root / manifest.source_root
    if manifest_path.is_file():
        manifest_sha = sha256_file(manifest_path)
    else:
        manifest_sha = sha256_bytes(canonical_json(to_dict(manifest)))

    provenance = PackageProvenance(
        provenance_id=new_id("prov"),
        created_at=utc_now_iso(),
        package_name=manifest.package_name,
        package_version=manifest.package_version,
        source_commit=get_git_commit(repo_root) or "UNKNOWN",
        source_branch=get_git_branch(repo_root) or "UNKNOWN",
        source_tree_status=get_git_status(repo_root),
        manifest_path=str(manifest_path),
        manifest_sha256=manifest_sha,
        build_command=build_command,
        build_environment=get_build_environment(),
        builder_version=f"Python {sys.version.split()[0]}",
        package_artifact=str(package_artifact),
        package_sha256=package_sha256,
        reproducibility_settings={
            "recorded_timestamp": utc_now_iso(),
            "normalized_timestamp": "0",
            "normalized_permissions": {},
            "normalized_owner_group": "0:0",
        },
    )

    write_json_atomic(output_path, to_dict(provenance))
    return provenance
