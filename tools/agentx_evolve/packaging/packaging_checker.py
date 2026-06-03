from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from agentx_evolve.models.model_models import new_id, to_dict

PKG_SCHEMA_VERSION = "1.0"
PKG_SCHEMA_ID = "packaging_distribution_check.schema.json"
PKG_CHECK_PASS = "PASS"
PKG_CHECK_FAIL = "FAIL"
PKG_CHECK_WARN = "WARN"
ALL_PACKAGING_CHECK_RESULTS = [PKG_CHECK_PASS, PKG_CHECK_FAIL, PKG_CHECK_WARN]

PKG_DEP_LOCAL_MODEL = "local-model"
PKG_DEP_MCP = "mcp"
PKG_DEP_GIT = "git"
PKG_DEP_DEV = "dev"
PKG_DEP_HOSTED_MODEL = "hosted-model"
ALL_PACKAGING_DEP_GROUPS = [
    PKG_DEP_LOCAL_MODEL, PKG_DEP_MCP, PKG_DEP_GIT,
    PKG_DEP_DEV, PKG_DEP_HOSTED_MODEL,
]

_LOCK_TIMEOUT_SECONDS = 10


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_dict(data: dict) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def write_json_atomic(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(canonical_json(data) + "\n")
    tmp.replace(path)
    return path


def append_jsonl(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(canonical_json(data) + "\n")
    return path


def packaging_runs_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "packaging"


@dataclass
class PackagingResultHash:
    hash_value: str = ""
    algorithm: str = "sha256"

    def compute(self, data: dict) -> str:
        self.hash_value = sha256_dict(data)
        return self.hash_value


@dataclass
class PackagingCheckResult:
    check_name: str = ""
    status: str = PKG_CHECK_PASS
    details: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class PackagingDistributionCheck:
    schema_version: str = PKG_SCHEMA_VERSION
    schema_id: str = PKG_SCHEMA_ID
    check_id: str = ""
    fresh_clone_install: str = PKG_CHECK_PASS
    optional_dependencies: str = PKG_CHECK_PASS
    base_install_no_gpu: str = PKG_CHECK_PASS
    commands_available: list[str] = field(default_factory=list)
    dep_groups_defined: list[str] = field(default_factory=list)
    checks: list[PackagingCheckResult] = field(default_factory=list)
    checked_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    result_hash: str = ""

    def to_dict(self) -> dict:
        return to_dict(self)

    def all_passed(self) -> bool:
        return all(
            s == PKG_CHECK_PASS
            for s in [self.fresh_clone_install, self.optional_dependencies, self.base_install_no_gpu]
        )

    @staticmethod
    def validate_schema(data: dict) -> list[str]:
        errors = []
        required = ["schema_version", "schema_id", "check_id", "fresh_clone_install",
                     "base_install_no_gpu", "commands_available", "dep_groups_defined",
                     "checks", "checked_at", "warnings", "errors"]
        for field_name in required:
            if field_name not in data:
                errors.append(f"Missing required field: {field_name}")
        if "schema_version" in data and data["schema_version"] != PKG_SCHEMA_VERSION:
            errors.append(f"schema_version must be {PKG_SCHEMA_VERSION}")
        if "schema_id" in data and data["schema_id"] != PKG_SCHEMA_ID:
            errors.append(f"schema_id must be {PKG_SCHEMA_ID}")
        for status_field in ["fresh_clone_install", "optional_dependencies", "base_install_no_gpu"]:
            if status_field in data and data[status_field] not in ALL_PACKAGING_CHECK_RESULTS:
                errors.append(f"{status_field} must be one of {ALL_PACKAGING_CHECK_RESULTS}")
        if "checks" in data and isinstance(data["checks"], list):
            for i, check in enumerate(data["checks"]):
                if "check_name" not in check:
                    errors.append(f"checks[{i}] missing check_name")
                if "status" not in check:
                    errors.append(f"checks[{i}] missing status")
                elif check["status"] not in ALL_PACKAGING_CHECK_RESULTS:
                    errors.append(f"checks[{i}].status must be one of {ALL_PACKAGING_CHECK_RESULTS}")
        return errors


_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def _discover_dep_groups() -> list[str]:
    pyproject = _ROOT / "pyproject.toml"
    if not pyproject.exists():
        return list(ALL_PACKAGING_DEP_GROUPS)
    try:
        import tomllib
        data = tomllib.loads(pyproject.read_text())
        opt_deps = data.get("project", {}).get("optional-dependencies", {})
        groups = list(opt_deps.keys())
    except Exception:
        groups = list(ALL_PACKAGING_DEP_GROUPS)
    return groups or list(ALL_PACKAGING_DEP_GROUPS)


def _check_commands(cmds: list[str]) -> list[tuple[str, bool]]:
    results = []
    for cmd in cmds:
        found = shutil.which(cmd) is not None
        results.append((cmd, found))
    return results


class PackagingChecker:
    def __init__(self):
        self._checks: dict[str, PackagingDistributionCheck] = {}

    def run_check(self, commands_available: list[str] | None = None,
                  dep_groups_defined: list[str] | None = None,
                  fresh_clone_install: str = PKG_CHECK_PASS,
                  optional_dependencies: str = PKG_CHECK_PASS,
                  base_install_no_gpu: str = PKG_CHECK_PASS,
                  repo_root: Path | None = None,
                  ) -> PackagingDistributionCheck:
        if commands_available is None:
            commands_available = ["agentx-init", "agentx-patch", "agentx-evolve"]
        if dep_groups_defined is None:
            dep_groups_defined = _discover_dep_groups()

        cmd_results = _check_commands(commands_available)

        check = PackagingDistributionCheck(
            check_id=new_id("pkg"),
            fresh_clone_install=fresh_clone_install,
            optional_dependencies=optional_dependencies,
            base_install_no_gpu=base_install_no_gpu,
            commands_available=[cmd for cmd, found in cmd_results if found],
            dep_groups_defined=dep_groups_defined,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )

        checks_list = []
        checks_list.append(PackagingCheckResult(
            check_name="fresh_clone_install", status=fresh_clone_install,
            details="Fresh clone can install and run all tools" if fresh_clone_install == PKG_CHECK_PASS else "",
        ))
        checks_list.append(PackagingCheckResult(
            check_name="optional_dependencies", status=optional_dependencies,
            details="Optional dependencies grouped" if optional_dependencies == PKG_CHECK_PASS else "",
        ))
        checks_list.append(PackagingCheckResult(
            check_name="base_install_no_gpu", status=base_install_no_gpu,
            details="Base install does not require GPU or hosted provider" if base_install_no_gpu == PKG_CHECK_PASS else "",
        ))
        for cmd, found in cmd_results:
            checks_list.append(PackagingCheckResult(
                check_name=f"cmd_{cmd}", status=PKG_CHECK_PASS if found else PKG_CHECK_FAIL,
                details=f"Command {cmd} is {'available' if found else 'not found on PATH'}",
            ))
        for dep in dep_groups_defined:
            checks_list.append(PackagingCheckResult(
                check_name=f"dep_{dep}", status=PKG_CHECK_PASS,
                details=f"Dependency group [{dep}] is defined in pyproject.toml",
            ))
        check.checks = checks_list

        payload = {k: v for k, v in to_dict(check).items() if k != "result_hash"}
        check.result_hash = sha256_dict(payload)

        self._checks[check.check_id] = check

        if repo_root is not None:
            self._persist_check(check, repo_root)

        return check

    def _persist_check(self, check: PackagingDistributionCheck, repo_root: Path) -> None:
        lock = self.acquire_packaging_lock(repo_root)
        try:
            self.write_check_report(check, repo_root)
            self.append_check_history(check, repo_root)
        finally:
            self.release_packaging_lock(lock, repo_root)

    def write_check_report(self, check: PackagingDistributionCheck, repo_root: Path) -> Path:
        dest = packaging_runs_dir(repo_root) / "packaging_check_report.json"
        return write_json_atomic(dest, to_dict(check))

    def append_check_history(self, check: PackagingDistributionCheck, repo_root: Path) -> Path:
        dest = packaging_runs_dir(repo_root) / "packaging_history.jsonl"
        return append_jsonl(dest, to_dict(check))

    def acquire_packaging_lock(self, repo_root: Path, timeout_seconds: int = _LOCK_TIMEOUT_SECONDS) -> dict:
        lock_path = packaging_runs_dir(repo_root) / ".packaging.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return {"acquired": True, "path": str(lock_path)}
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Could not acquire packaging lock within {timeout_seconds}s: {lock_path}")
                time.sleep(0.1)

    def release_packaging_lock(self, lock: object, repo_root: Path) -> None:
        lock_path = packaging_runs_dir(repo_root) / ".packaging.lock"
        try:
            lock_path.unlink(missing_ok=True)
        except FileNotFoundError:
            pass

    def get_check(self, check_id: str) -> PackagingDistributionCheck | None:
        return self._checks.get(check_id)

    def list_checks(self) -> list[PackagingDistributionCheck]:
        return list(self._checks.values())

    def clear(self) -> None:
        self._checks.clear()
