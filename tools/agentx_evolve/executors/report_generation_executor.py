from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionResult:
    status: str = "UNKNOWN"
    action_id: str = ""
    run_id: str = ""
    artifacts: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    evidence_refs: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "action_id": self.action_id,
            "run_id": self.run_id,
            "artifacts": list(self.artifacts),
            "errors": list(self.errors),
            "evidence_refs": list(self.evidence_refs),
        }


class MvpReportGenerationExecutor:
    def __init__(self, artifact_store: Any) -> None:
        self._artifact_store = artifact_store
        self._last_result: ExecutionResult | None = None

    def execute(self, action: Any, envelope: Any, context: dict[str, Any]) -> dict[str, Any]:
        if not envelope or not envelope.is_sealed():
            return ExecutionResult(
                status="FAIL", action_id=getattr(action, "action_id", ""),
                run_id=context.get("run_id", ""), errors=["Security envelope required"]).to_dict()

        if self._artifact_store is None:
            return ExecutionResult(
                status="FAIL", action_id=getattr(action, "action_id", ""),
                run_id=context.get("run_id", ""), errors=["Artifact store not available"]).to_dict()

        run_id = context.get("run_id", "")
        action_id = getattr(action, "action_id", "")
        report_content = context.get("report_content", {})
        report_name = context.get("report_name", "report.json")

        if context.get("suppress_failure"):
            return ExecutionResult(
                status="FAIL", action_id=action_id,
                run_id=run_id, errors=["Execution suppressed"]).to_dict()

        artifact = self._artifact_store.write(
            run_id=run_id, action_id=action_id,
            name=report_name, data=report_content,
            artifact_type="report",
        )

        result = ExecutionResult(
            status="PASS",
            action_id=action_id,
            run_id=run_id,
            artifacts=[artifact],
            evidence_refs=[{"path": artifact.get("path", ""), "hash": artifact.get("hash", "")}],
        )
        self._last_result = result
        return result.to_dict()

    @property
    def last_result(self) -> ExecutionResult | None:
        return self._last_result
