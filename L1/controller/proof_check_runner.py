from __future__ import annotations

import dataclasses
import enum
import pathlib as _pathlib
import typing as _typing

__all__ = [
    "CheckStatus",
    "ProofCheck",
    "ProofCheckResult",
    "ProofCheckRunner",
    "ProofCheckRunnerError",
    "run_proof_checks",
]


class CheckStatus(enum.Enum):
    PENDING = "pending"
    PASS = "pass"
    FAIL = "fail"
    SKIPPED = "skipped"


@dataclasses.dataclass(frozen=True)
class ProofCheck:
    check_id: str
    name: str
    description: str
    status: CheckStatus
    details: str


@dataclasses.dataclass(frozen=True)
class ProofCheckResult:
    checks: tuple[ProofCheck, ...]
    all_passed: bool
    summary: str


class ProofCheckRunnerError(Exception):
    pass

_CheckFn = _typing.Callable[[], str | None]


class ProofCheckRunner:
    def __init__(self, repo_root: str = "."):
        root = _pathlib.Path(repo_root).resolve(strict=False)
        if not root.exists():
            raise ProofCheckRunnerError("repo_root does not exist")
        if not root.is_dir():
            raise ProofCheckRunnerError("repo_root is not a directory")
        self._root = root
        self._checks: list[tuple[str, str, _CheckFn]] = []

    def add_check(self, name: str, description: str, check_fn: _CheckFn) -> None:
        self._checks.append((name, description, check_fn))

    def run_all(self) -> ProofCheckResult:
        results: list[ProofCheck] = []
        passed = 0
        failed = 0

        for i, (name, desc, fn) in enumerate(self._checks):
            try:
                err = fn()
                if err is None:
                    results.append(
                        ProofCheck(
                            check_id=f"CHK-{i + 1:03d}",
                            name=name,
                            description=desc,
                            status=CheckStatus.PASS,
                            details="",
                        )
                    )
                    passed += 1
                else:
                    results.append(
                        ProofCheck(
                            check_id=f"CHK-{i + 1:03d}",
                            name=name,
                            description=desc,
                            status=CheckStatus.FAIL,
                            details=str(err),
                        )
                    )
                    failed += 1
            except Exception as e:
                results.append(
                    ProofCheck(
                        check_id=f"CHK-{i + 1:03d}",
                        name=name,
                        description=desc,
                        status=CheckStatus.FAIL,
                        details=f"exception: {e}",
                    )
                )
                failed += 1

        return ProofCheckResult(
            checks=tuple(results),
            all_passed=failed == 0,
            summary=f"{passed} passed, {failed} failed",
        )


def _file_exists(path: str) -> str | None:
    p = _pathlib.Path(path)
    if not p.exists():
        return f"file not found: {path}"
    if not p.is_file():
        return f"not a file: {path}"
    return None


def _file_contains(path: str, *keywords: str) -> str | None:
    err = _file_exists(path)
    if err:
        return err
    content = _pathlib.Path(path).read_bytes()
    for kw in keywords:
        if kw.encode() not in content:
            return f"missing keyword {kw!r} in {path}"
    return None


def _check_dir(path: str) -> str | None:
    p = _pathlib.Path(path)
    if not p.exists():
        return f"directory not found: {path}"
    if not p.is_dir():
        return f"not a directory: {path}"
    return None


def run_proof_checks(repo_root: str = ".") -> ProofCheckResult:
    runner = ProofCheckRunner(repo_root)

    runner.add_check(
        "validation_report_exists",
        "L1/generated/validation_report.md exists with required sections",
        lambda: _file_contains(
            f"{runner._root}/L1/generated/validation_report.md",
            "Validation Report",
            "WARNING",
        ),
    )

    runner.add_check(
        "lockfile_exists",
        "L1/generated/semantic_lockfile.yaml exists with required fields",
        lambda: _file_contains(
            f"{runner._root}/L1/generated/semantic_lockfile.yaml",
            "lockfile_version",
            "base_commit",
        ),
    )

    runner.add_check(
        "readiness_report_exists",
        "L1/generated/readiness_report.md exists with status",
        lambda: _file_contains(
            f"{runner._root}/L1/generated/readiness_report.md",
            "Readiness Report",
        ),
    )

    runner.add_check(
        "release_manifest_exists",
        "L1/generated/release_package_manifest.yaml exists",
        lambda: _file_contains(
            f"{runner._root}/L1/generated/release_package_manifest.yaml",
            "release_package_manifest_version",
        ),
    )

    runner.add_check(
        "evidence_directory_exists",
        "L1/evidence/ directory exists",
        lambda: _check_dir(f"{runner._root}/L1/evidence"),
    )

    runner.add_check(
        "fic_index_exists",
        "L1/fic/index.fic.yaml exists",
        lambda: _file_exists(f"{runner._root}/L1/fic/index.fic.yaml"),
    )

    return runner.run_all()
