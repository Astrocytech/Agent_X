from __future__ import annotations

import json as _json
from pathlib import Path
from typing import Any

from agentx_evolve.orchestrator.orchestrator_models import (
    ApprovalGateRecord,
    ExecutionStep,
    ModelInvocationBinding,
    OrchestrationSession,
    OrchestrationState,
    OrchestratorCompletionRecord,
    OrchestratorEvidenceEvent,
    OrchestratorEvidenceManifest,
    OrchestratorReviewReport,
    PromptBinding,
    PromotionGateRecord,
    RecoveryAction,
    RunLedger,
    ToolInvocationBinding,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    COMPONENT_ID,
    COMPONENT_NAME,
    DECISION_NOT_DONE,
    RUNTIME_ARTIFACT_ROOT,
    SOURCE_COMPONENT,
)


def _runs_dir(repo_root: Path, run_id: str) -> Path:
    d = repo_root / RUNTIME_ARTIFACT_ROOT / "runs" / run_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_json(path: Path, data: dict) -> dict:
    path.write_text(_json.dumps(data, indent=2, sort_keys=True, default=str))
    return {"path": str(path), "sha256": sha256_dict(data)}


def _append_jsonl(path: Path, data: dict) -> dict:
    with open(path, "a") as f:
        f.write(_json.dumps(data, sort_keys=True, default=str) + "\n")
    return {"path": str(path), "sha256": sha256_dict(data)}


def append_session_history(session: OrchestrationSession, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, session.run_id)
    return _write_json(d / "orchestration_session.json", session.to_dict())


def write_latest_session(session: OrchestrationSession, repo_root: Path) -> dict:
    latest_dir = repo_root / RUNTIME_ARTIFACT_ROOT
    latest_dir.mkdir(parents=True, exist_ok=True)
    return _write_json(latest_dir / "latest_orchestration_session.json", session.to_dict())


def append_state_history(state: OrchestrationState, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, state.run_id)
    return _write_json(d / "orchestration_state.json", state.to_dict())


def write_latest_state(state: OrchestrationState, repo_root: Path) -> dict:
    latest_dir = repo_root / RUNTIME_ARTIFACT_ROOT
    latest_dir.mkdir(parents=True, exist_ok=True)
    return _write_json(latest_dir / "latest_orchestration_state.json", state.to_dict())


def append_execution_step(step: ExecutionStep, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, step.run_id or "")
    return _append_jsonl(d / "execution_steps.jsonl", step.to_dict())


def append_tool_invocation(binding: ToolInvocationBinding, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, binding.run_id)
    return _append_jsonl(d / "tool_invocations.jsonl", binding.to_dict())


def append_model_invocation(binding: ModelInvocationBinding, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, binding.run_id)
    return _append_jsonl(d / "model_invocations.jsonl", binding.to_dict())


def append_prompt_binding(binding: PromptBinding, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, binding.run_id)
    return _append_jsonl(d / "prompt_bindings.jsonl", binding.to_dict())


def append_approval_gate_record(record: ApprovalGateRecord, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, record.run_id)
    return _append_jsonl(d / "approval_gate_records.jsonl", record.to_dict())


def append_promotion_gate_record(record: PromotionGateRecord, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, record.run_id)
    return _append_jsonl(d / "promotion_gate_records.jsonl", record.to_dict())


def append_recovery_action(action: RecoveryAction, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, action.run_id)
    return _append_jsonl(d / "recovery_actions.jsonl", action.to_dict())


def append_evidence_event(event: OrchestratorEvidenceEvent, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, event.run_id)
    return _append_jsonl(d / "orchestrator_events.jsonl", event.to_dict())


def append_ledger(ledger: RunLedger, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, ledger.run_id)
    return _write_json(d / "run_ledger.json", ledger.to_dict())


def write_latest_ledger(ledger: RunLedger, repo_root: Path) -> dict:
    latest_dir = repo_root / RUNTIME_ARTIFACT_ROOT
    latest_dir.mkdir(parents=True, exist_ok=True)
    return _write_json(latest_dir / "latest_run_ledger.json", ledger.to_dict())


def append_decision_history(decision: dict, run_id: str, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, run_id)
    return _append_jsonl(d / "orchestration_decision_history.jsonl", decision)


def append_recovery_history(action: RecoveryAction, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, action.run_id)
    return _append_jsonl(d / "orchestration_recovery_history.jsonl", action.to_dict())


def append_gate_history(record: dict, run_id: str, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, run_id)
    return _append_jsonl(d / "orchestration_gate_history.jsonl", record)


def append_audit_history(audit_entry: dict, run_id: str, repo_root: Path) -> dict:
    d = _runs_dir(repo_root, run_id)
    return _append_jsonl(d / "orchestration_audit_history.jsonl", audit_entry)


def write_latest_step(step: ExecutionStep, repo_root: Path) -> dict:
    latest_dir = repo_root / RUNTIME_ARTIFACT_ROOT
    latest_dir.mkdir(parents=True, exist_ok=True)
    return _write_json(latest_dir / "latest_orchestration_step.json", step.to_dict())


def write_latest_result(result: dict, run_id: str, repo_root: Path) -> dict:
    latest_dir = repo_root / RUNTIME_ARTIFACT_ROOT
    latest_dir.mkdir(parents=True, exist_ok=True)
    return _write_json(latest_dir / "latest_orchestration_result.json", result)


def write_latest_run_lock(lock_data: dict, run_id: str, repo_root: Path) -> dict:
    latest_dir = repo_root / RUNTIME_ARTIFACT_ROOT
    latest_dir.mkdir(parents=True, exist_ok=True)
    return _write_json(latest_dir / "latest_orchestration_run_lock.json", lock_data)


def create_evidence_manifest(
    run_id: str,
    session_id: str,
    evidence_files: list[str] | None = None,
    runtime_artifacts: list[str] | None = None,
) -> OrchestratorEvidenceManifest:
    manifest = OrchestratorEvidenceManifest(
        manifest_id=new_id("em"),
        session_id=session_id,
        run_id=run_id,
        created_at=utc_now_iso(),
        component_id=COMPONENT_ID,
        validated_commit="",
        evidence_files=evidence_files or [],
        evidence_file_hashes={},
        runtime_artifacts=runtime_artifacts or [],
        source_mutation_status="NOT_MUTATED",
        final_decision=DECISION_NOT_DONE,
    )
    manifest.evidence_manifest_sha256 = manifest.compute_hash()
    return manifest


def write_evidence_manifest(
    manifest: OrchestratorEvidenceManifest,
    repo_root: Path,
) -> dict:
    d = _runs_dir(repo_root, manifest.run_id)
    path = d / "orchestrator_evidence_manifest.json"
    data = manifest.to_dict()
    path.write_text(__import__("json").dumps(data, indent=2, sort_keys=True, default=str))
    return {"path": str(path), "sha256": manifest.evidence_manifest_sha256}


def create_review_report(
    manifest: OrchestratorEvidenceManifest,
    commands_run: list[str] | None = None,
) -> OrchestratorReviewReport:
    report = OrchestratorReviewReport(
        review_report_id=new_id("rr"),
        created_at=utc_now_iso(),
        component_id=COMPONENT_ID,
        reviewed_commit="",
        reviewed_at=utc_now_iso(),
        commands_run=commands_run or [],
        blockers=[],
        evidence_manifest_path="",
        evidence_manifest_sha256=manifest.evidence_manifest_sha256,
        final_verdict="NOT_DONE",
    )
    report.review_report_sha256 = report.compute_hash()
    return report


def write_review_report(
    report: OrchestratorReviewReport,
    repo_root: Path,
    run_id: str,
) -> dict:
    d = _runs_dir(repo_root, run_id)
    path = d / "orchestrator_review_report.json"
    data = report.to_dict()
    path.write_text(__import__("json").dumps(data, indent=2, sort_keys=True, default=str))
    return {"path": str(path), "sha256": report.review_report_sha256}


def create_completion_record(
    manifest: OrchestratorEvidenceManifest,
    review_report: OrchestratorReviewReport,
    status: str = "DONE",
    implementation_score: float = 0.0,
) -> OrchestratorCompletionRecord:
    record = OrchestratorCompletionRecord(
        completion_record_id=new_id("cr"),
        created_at=utc_now_iso(),
        component_id=COMPONENT_ID,
        component_name=COMPONENT_NAME,
        status=status,
        validated_commit="",
        validated_at=utc_now_iso(),
        canonical_subdirectories=[
            "tools/agentx_evolve/orchestrator/",
            "tools/agentx_evolve/schemas/",
            "tools/agentx_evolve/tests/",
        ],
        commands_run=[],
        evidence_manifest_sha256=manifest.evidence_manifest_sha256,
        review_report_sha256=review_report.review_report_sha256,
        implementation_score=implementation_score,
        final_decision=status,
    )
    record.completion_record_sha256 = record.compute_hash()
    return record


def write_completion_record(
    record: OrchestratorCompletionRecord,
    repo_root: Path,
    run_id: str,
) -> dict:
    d = _runs_dir(repo_root, run_id)
    path = d / "orchestrator_completion_record.json"
    data = record.to_dict()
    path.write_text(__import__("json").dumps(data, indent=2, sort_keys=True, default=str))
    return {"path": str(path), "sha256": record.completion_record_sha256}
