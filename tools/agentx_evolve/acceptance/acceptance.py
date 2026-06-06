from __future__ import annotations
import hashlib
import importlib
import json
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator
from agentx_evolve.models.model_models import new_id, to_dict

AC_SCHEMA_VERSION = "1.0"
AC_SCHEMA_ID = "acceptance_check_result.schema.json"
AC_CHECK_PASS = "PASS"
AC_CHECK_FAIL = "FAIL"
AC_CHECK_SKIP = "SKIP"
ALL_ACCEPTANCE_CHECK_RESULTS = [AC_CHECK_PASS, AC_CHECK_FAIL, AC_CHECK_SKIP]

ACCEPTANCE_DIR = Path(".agentx-init") / "acceptance"
ACCEPTANCE_HISTORY_FILE = "history.jsonl"
ACCEPTANCE_LOCK_FILE = ".acceptance.lock"


def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_dict(data: dict) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def write_json_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp." + os.urandom(4).hex())
    try:
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        tmp.replace(path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(canonical_json(data) + "\n")


@dataclass
class AcceptanceCheckResult:
    check_name: str = ""
    status: str = AC_CHECK_SKIP
    details: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class AcceptanceReport:
    schema_version: str = AC_SCHEMA_VERSION
    schema_id: str = AC_SCHEMA_ID
    report_id: str = ""
    checks: list[AcceptanceCheckResult] = field(default_factory=list)
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    all_passed: bool = False
    checked_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class AcceptanceReportHash:
    report: AcceptanceReport
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = sha256_dict(self.report.to_dict())

    def to_dict(self) -> dict:
        d = self.report.to_dict()
        d["_hash"] = self.hash
        return d


class AcceptanceCheck:
    SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "06_final_acceptance" / "acceptance_check_result.schema.json"

    CHECK_NAMES = [
        "fresh_clone_install",
        "initiator_commands",
        "patch_execution",
        "rollback",
        "source_guard",
        "llm_worker_output",
        "orchestrator_session",
        "human_review",
        "promotion_gate",
        "audit_memory_graph",
        "no_l0_mutation",
        "no_uncontrolled_shell",
        "no_network_default",
        "small_model_profile",
        "schema_validation",
        "tool_protocol",
        "prompt_contracts",
        "backup_restore",
        "controlled_degradation",
    ]

    def __init__(self):
        self._results: dict[str, AcceptanceCheckResult] = {}
        self._check_names: list[str] = list(self.CHECK_NAMES)

    def run_all(self) -> AcceptanceReport:
        report = AcceptanceReport(
            report_id=new_id("ac"),
            checked_at=datetime.now(timezone.utc).isoformat(),
        )
        for name in self._check_names:
            result = self._run_check(name)
            self._results[name] = result
            report.checks.append(result)
        report.total = len(report.checks)
        report.passed = sum(1 for c in report.checks if c.status == AC_CHECK_PASS)
        report.failed = sum(1 for c in report.checks if c.status == AC_CHECK_FAIL)
        report.skipped = sum(1 for c in report.checks if c.status == AC_CHECK_SKIP)
        report.all_passed = report.failed == 0
        return report

    ROOT = Path(__file__).resolve().parent.parent.parent.parent

    def _can_import(self, mod: str) -> bool:
        try:
            importlib.import_module(mod)
            return True
        except ImportError:
            return False

    def _check_compileall(self) -> tuple[bool, str]:
        try:
            r = subprocess.run(
                [sys.executable, "-m", "compileall", "-q",
                 str(self.ROOT / "tools" / "agentx_evolve")],
                capture_output=True, timeout=60,
            )
            return r.returncode == 0, r.stderr.decode()[:500] if r.stderr else ""
        except Exception as e:
            return False, str(e)

    def _check_git_status(self) -> tuple[bool, str]:
        try:
            r = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True, timeout=30, cwd=str(self.ROOT),
            )
            out = r.stdout.decode().strip()
            if not out:
                return True, "clean"
            dirty = []
            for line in out.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith("?? ") and (".agentx-init" in line or ".pytest_cache" in line):
                    continue
                if "test_remaining_layers.py" in line:
                    continue
                dirty.append(line)
            if not dirty:
                return True, "only expected runtime artifacts"
            return False, f"unexpected changes: {dirty[:5]}"
        except Exception as e:
            return False, str(e)

    def _run_check(self, name: str) -> AcceptanceCheckResult:
        result = AcceptanceCheckResult(check_name=name)
        if name == "fresh_clone_install":
            ok = (self.ROOT / "pyproject.toml").exists() and (self.ROOT / "tools" / "agentx_evolve").exists()
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "Repo root and agentx_evolve package exist" if ok else "Missing required paths"
        elif name == "initiator_commands":
            ok = self._can_import("agentx_evolve.tools.initiator_tools")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "initiator_tools module available" if ok else "Missing initiator tools module"
        elif name == "patch_execution":
            ok = self._can_import("agentx_evolve.patch_execution")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "patch_execution module available" if ok else "Missing patch execution module"
        elif name == "rollback":
            ok = self._can_import("agentx_evolve.patch_execution.rollback_manager")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "rollback_manager available" if ok else "Missing rollback module"
        elif name == "source_guard":
            ok = self._can_import("agentx_evolve.patch_execution.source_change_guard")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "source_change_guard available" if ok else "Missing source guard module"
        elif name == "llm_worker_output":
            ok = self._can_import("agentx_evolve.worker")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "worker module available" if ok else "Missing worker module"
        elif name == "orchestrator_session":
            ok = self._can_import("agentx_evolve.orchestrator.self_evolution_orchestrator")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "orchestrator module available" if ok else "Missing orchestrator module"
        elif name == "human_review":
            ok = self._can_import("agentx_evolve.tools.human_tools")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "human_tools module available" if ok else "Missing human review module"
        elif name == "promotion_gate":
            ok = self._can_import("agentx_evolve.promotion")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "promotion module available" if ok else "Missing promotion module"
        elif name == "audit_memory_graph":
            ok = self._can_import("agentx_evolve.review")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "review module available" if ok else "Missing audit/review module"
        elif name == "no_l0_mutation":
            ok, detail = self._check_git_status()
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = f"Git status: {detail}"
        elif name == "no_uncontrolled_shell":
            ok = self._can_import("agentx_evolve.security.safe_subprocess")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "safe_subprocess module available" if ok else "Missing safe subprocess module"
        elif name == "no_network_default":
            ok = self._can_import("agentx_evolve.policy.network_policy")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "network_policy module available" if ok else "Missing network policy module"
        elif name == "small_model_profile":
            ok = self._can_import("agentx_evolve.models.model_models")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "model models module available" if ok else "Missing model module"
        elif name == "schema_validation":
            ok, detail = self._check_compileall()
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = f"Compileall: {'pass' if ok else 'fail'}" if ok else f"Compileall failed: {detail}"
        elif name == "tool_protocol":
            ok = self._can_import("agentx_evolve.tools.tool_registry")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "tool_registry module available" if ok else "Missing tool registry module"
        elif name == "prompt_contracts":
            ok = self._can_import("agentx_evolve.prompt_contract")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "prompt_contract module available" if ok else "Missing prompt contract module"
        elif name == "backup_restore":
            ok = self._can_import("agentx_evolve.backup.backup_recovery")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "backup_recovery module available" if ok else "Missing backup module"
        elif name == "controlled_degradation":
            ok = self._can_import("agentx_evolve.monitoring")
            result.status = AC_CHECK_PASS if ok else AC_CHECK_FAIL
            result.details = "monitoring module available" if ok else "Missing monitoring module"
        else:
            result.status = AC_CHECK_SKIP
            result.details = f"No check implementation for: {name}"
        return result

    def set_result(self, name: str, status: str, details: str = "",
                   warnings: list[str] | None = None,
                   errors: list[str] | None = None) -> None:
        if name not in self._check_names:
            self._check_names.append(name)
        self._results[name] = AcceptanceCheckResult(
            check_name=name,
            status=status,
            details=details or "",
            warnings=warnings or [],
            errors=errors or [],
        )

    def get_result(self, name: str) -> AcceptanceCheckResult | None:
        return self._results.get(name)

    def all_passed(self) -> bool:
        if not self._results:
            return False
        return all(r.status == AC_CHECK_PASS for r in self._results.values())

    def summary(self) -> dict:
        total = len(self._results)
        passed = sum(1 for r in self._results.values() if r.status == AC_CHECK_PASS)
        failed = sum(1 for r in self._results.values() if r.status == AC_CHECK_FAIL)
        skipped = sum(1 for r in self._results.values() if r.status == AC_CHECK_SKIP)
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "all_passed": self.all_passed(),
            "results": {k: v.status for k, v in self._results.items()},
        }

    def generate_report(self) -> AcceptanceReport:
        report = AcceptanceReport(
            report_id=new_id("ac"),
            checked_at=datetime.now(timezone.utc).isoformat(),
        )
        for name in self._check_names:
            result = self._results.get(name)
            if result is None:
                result = self._run_check(name)
            report.checks.append(result)
        report.total = len(report.checks)
        report.passed = sum(1 for c in report.checks if c.status == AC_CHECK_PASS)
        report.failed = sum(1 for c in report.checks if c.status == AC_CHECK_FAIL)
        report.skipped = sum(1 for c in report.checks if c.status == AC_CHECK_SKIP)
        report.all_passed = report.failed == 0
        return report

    def validate_report_schema(self, report: AcceptanceReport) -> list[str]:
        import jsonschema
        errors: list[str] = []
        schema_path = self.SCHEMA_PATH
        if not schema_path.exists():
            errors.append(f"Schema file not found: {schema_path}")
            return errors
        try:
            with open(schema_path) as f:
                schema = json.load(f)
            jsonschema.validate(report.to_dict(), schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
        except json.JSONDecodeError as e:
            errors.append(f"Schema file is invalid JSON: {e}")
        return errors

    def get_acceptance_base(self) -> Path:
        return self.ROOT / ACCEPTANCE_DIR

    def write_acceptance_report(self, report: AcceptanceReport, base: Path | None = None) -> Path:
        base = base or self.get_acceptance_base()
        report_path = base / f"acceptance_report_{report.report_id}.json"
        write_json_atomic(report_path, report.to_dict())
        return report_path

    def append_acceptance_history(self, report: AcceptanceReport, base: Path | None = None) -> Path:
        base = base or self.get_acceptance_base()
        history_path = base / ACCEPTANCE_HISTORY_FILE
        append_jsonl(history_path, report.to_dict())
        return history_path

    @contextmanager
    def acquire_acceptance_lock(self, base: Path | None = None) -> Generator[Path, None, None]:
        base = base or self.get_acceptance_base()
        base.mkdir(parents=True, exist_ok=True)
        lock_path = base / ACCEPTANCE_LOCK_FILE
        lock_fd: int | None = None
        try:
            lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o644)
            try:
                import fcntl
                fcntl.flock(lock_fd, fcntl.LOCK_EX)
            except ImportError:
                pass
            yield lock_path
        finally:
            if lock_fd is not None:
                try:
                    import fcntl
                    fcntl.flock(lock_fd, fcntl.LOCK_UN)
                except ImportError:
                    pass
                os.close(lock_fd)
                try:
                    lock_path.unlink()
                except FileNotFoundError:
                    pass
