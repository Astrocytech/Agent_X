from __future__ import annotations

import dataclasses
import typing as _typing

__all__ = [
    "BoundaryCheck",
    "BoundaryCheckResult",
    "BoundaryChecker",
    "BoundaryCheckerError",
    "check_boundaries",
]


@dataclasses.dataclass(frozen=True)
class BoundaryCheck:
    check_name: str
    passed: bool
    message: str


@dataclasses.dataclass(frozen=True)
class BoundaryCheckResult:
    checks: tuple[BoundaryCheck, ...]
    all_passed: bool


class BoundaryCheckerError(Exception):
    pass


_L0_PREFIX = "L0/"


class BoundaryChecker:
    def check(self, changed_files: object) -> BoundaryCheckResult:
        if not isinstance(changed_files, tuple):
            raise BoundaryCheckerError("changed_files must be a tuple")
        checks: list[BoundaryCheck] = []
        all_pass = True

        l0_changes: list[str] = []
        for cf in changed_files:
            if isinstance(cf, str) and cf.startswith(_L0_PREFIX):
                l0_changes.append(cf)
        if l0_changes:
            all_pass = False
            checks.append(
                BoundaryCheck(
                    check_name="no_l0_changes",
                    passed=False,
                    message=f"L0 files changed: {', '.join(l0_changes)}",
                )
            )
        else:
            checks.append(
                BoundaryCheck(
                    check_name="no_l0_changes",
                    passed=True,
                    message="no L0 files changed",
                )
            )

        abs_paths: list[str] = []
        for cf in changed_files:
            if isinstance(cf, str) and cf.startswith("/"):
                abs_paths.append(cf)
        if abs_paths:
            all_pass = False
            checks.append(
                BoundaryCheck(
                    check_name="paths_are_relative",
                    passed=False,
                    message=f"absolute paths: {', '.join(abs_paths)}",
                )
            )
        else:
            checks.append(
                BoundaryCheck(
                    check_name="paths_are_relative",
                    passed=True,
                    message="all paths are relative",
                )
            )

        return BoundaryCheckResult(
            checks=tuple(checks),
            all_passed=all_pass,
        )


def check_boundaries(changed_files: tuple[str, ...]) -> BoundaryCheckResult:
    return BoundaryChecker().check(changed_files)
