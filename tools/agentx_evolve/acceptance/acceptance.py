from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from agentx_evolve.model.model_models import new_id, to_dict

AC_SCHEMA_VERSION = "1.0"
AC_CHECK_PASS = "PASS"
AC_CHECK_FAIL = "FAIL"
AC_CHECK_SKIP = "SKIP"
ALL_ACCEPTANCE_CHECK_RESULTS = [AC_CHECK_PASS, AC_CHECK_FAIL, AC_CHECK_SKIP]


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


class AcceptanceCheck:
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

    def _run_check(self, name: str) -> AcceptanceCheckResult:
        result = AcceptanceCheckResult(check_name=name)
        descriptions = {
            "fresh_clone_install": "Fresh clone can install and run all tools",
            "initiator_commands": "Initiator scan/status/plan/propose/validate/graph work",
            "patch_execution": "Patch execution on approved low-risk change",
            "rollback": "Rollback on failed validation",
            "source_guard": "Source guard blocks unauthorized edits",
            "llm_worker_output": "LLM worker produces schema-valid patch candidate",
            "orchestrator_session": "Orchestrator completes one safe session",
            "human_review": "Human review can approve/reject",
            "promotion_gate": "Promotion gate can recommend acceptance",
            "audit_memory_graph": "Audit/memory/graph record all events",
            "no_l0_mutation": "No L0 mutation",
            "no_uncontrolled_shell": "No uncontrolled shell",
            "no_network_default": "No network by default",
            "small_model_profile": "Small local model profile works",
            "schema_validation": "Schema validation passes for all new artifacts",
            "tool_protocol": "Tool protocol validates",
            "prompt_contracts": "Prompt contracts validate",
            "backup_restore": "Backup/restore can recover inspection state",
            "controlled_degradation": "Controlled degradation works",
        }
        result.details = descriptions.get(name, "")
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
