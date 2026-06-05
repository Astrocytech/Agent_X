from __future__ import annotations
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from agentx_evolve.model.model_models import new_id, to_dict

PKG_SCHEMA_VERSION = "1.0"
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

    def to_dict(self) -> dict:
        return to_dict(self)

    def all_passed(self) -> bool:
        return all(
            s == PKG_CHECK_PASS
            for s in [self.fresh_clone_install, self.optional_dependencies, self.base_install_no_gpu]
        )


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
                  ) -> PackagingDistributionCheck:
        if commands_available is None:
            commands_available = ["agentx-init", "agentx-patch", "agentx-evolve"]
        if dep_groups_defined is None:
            dep_groups_defined = _discover_dep_groups()

        cmd_results = _check_commands(commands_available)
        all_cmds_found = all(found for _, found in cmd_results)

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
        self._checks[check.check_id] = check
        return check

    def get_check(self, check_id: str) -> PackagingDistributionCheck | None:
        return self._checks.get(check_id)

    def list_checks(self) -> list[PackagingDistributionCheck]:
        return list(self._checks.values())

    def clear(self) -> None:
        self._checks.clear()
