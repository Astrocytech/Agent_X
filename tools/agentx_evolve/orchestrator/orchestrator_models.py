from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

from agentx_evolve.orchestrator.orchestrator_config import (
    SCHEMA_VERSION,
    SOURCE_COMPONENT,
    ORCH_STATUS_CREATED,
    ORCH_ALL_STATUSES,
    SESSION_STATUS_ACTIVE,
    ALL_SESSION_STATUSES,
    STEP_STATUS_PENDING,
    ALL_STEP_STATUSES,
    DECISION_CONTINUE,
    DECISION_NOT_DONE,
    ALL_DECISIONS,
    RUN_MODE_EXECUTE_CONTROLLED,
    ALL_RUN_MODES,
    ALL_DEPENDENCY_MODES,
    RECOVERY_ACTION_NONE,
    ALL_RECOVERY_ACTIONS,
    GATE_STATUS_PENDING,
    ALL_GATE_STATUSES,
    GATE_TYPE_APPROVAL,
    ALL_GATE_TYPES,
    RISK_LEVEL_LOW,
    ALL_RISK_LEVELS,
    DEFAULT_MAX_STEPS,
    DEFAULT_MAX_RETRIES_TOTAL,
    DEFAULT_MAX_RETRIES_PER_STEP,
    DEFAULT_MAX_TOOL_CALLS,
    DEFAULT_MAX_MODEL_CALLS,
    DEFAULT_MAX_RUN_SECONDS,
    DEFAULT_MAX_STEP_SECONDS,
    DEFAULT_MAX_EVIDENCE_BYTES,
    DEFAULT_MAX_REPLANS,
    COMPONENT_NAME,
)
from agentx_evolve.orchestrator.orchestrator_errors import (
    ALL_ORCHESTRATOR_FAILURE_CLASSES,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}-{ts}"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def sha256_dict(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    return dict(obj)


def compute_self_hash(data: dict, self_hash_field: str = "evidence_manifest_sha256") -> str:
    canonical = {k: v for k, v in data.items() if k != self_hash_field}
    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


@dataclass
class OrchestrationSession:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "orchestration_session.schema.json"
    session_id: str = ""
    run_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    source_component: str = SOURCE_COMPONENT
    requested_task_id: str = ""
    requested_task_summary: str = ""
    initiating_role: str = ""
    orchestration_mode: str = RUN_MODE_EXECUTE_CONTROLLED
    state: str = ORCH_STATUS_CREATED
    session_status: str = SESSION_STATUS_ACTIVE
    idempotency_key: str = ""
    policy_context_ref: str | None = None
    model_profile_ref: str | None = None
    prompt_contract_version: str | None = None
    tool_registry_snapshot_ref: str | None = None
    source_snapshot_id: str = ""
    source_snapshot_hash: str = ""
    policy_snapshot_id: str = ""
    policy_snapshot_ref: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def is_terminal(self) -> bool:
        return self.session_status in ("COMPLETED", "FAILED", "CANCELLED")


@dataclass
class OrchestrationState:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "orchestration_state.schema.json"
    state_id: str = ""
    session_id: str = ""
    run_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    source_component: str = SOURCE_COMPONENT
    previous_state: str = ""
    current_state: str = ORCH_STATUS_CREATED
    terminal: bool = False
    reason: str = ""
    state_version: int = 1
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class OrchestrationTask:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "orchestration_task.schema.json"
    task_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    title: str = ""
    description: str = ""
    task_type: str = ""
    risk_level: str = RISK_LEVEL_LOW
    requested_outputs: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    allowed_roles: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)
    allowed_model_profiles: list[str] = field(default_factory=list)
    requires_human_approval: bool = False
    requires_governance: bool = False
    requires_promotion_gate: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class TaskPlan:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "task_plan.schema.json"
    plan_id: str = ""
    session_id: str = ""
    run_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    task_id: str = ""
    plan_status: str = "PENDING"
    steps: list[dict] = field(default_factory=list)
    plan_hash: str = ""
    plan_version: int = 1
    risk_level: str = RISK_LEVEL_LOW
    objective: str = ""
    scope: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def compute_hash(self) -> str:
        return sha256_dict(self.to_dict())


@dataclass
class ExecutionStep:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "execution_step.schema.json"
    step_id: str = ""
    plan_id: str = ""
    session_id: str = ""
    run_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    source_component: str = SOURCE_COMPONENT
    step_index: int = 0
    step_name: str = ""
    step_type: str = ""
    assigned_role: str = ""
    status: str = STEP_STATUS_PENDING
    idempotency_key: str = ""
    description: str = ""
    depends_on_step_ids: list[str] = field(default_factory=list)
    blocks_step_ids: list[str] = field(default_factory=list)
    step_input_hashes: dict = field(default_factory=dict)
    step_output_hashes: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def is_terminal_step(self) -> bool:
        return self.status in ("COMPLETED", "FAILED", "BLOCKED", "SKIPPED")


@dataclass
class ToolInvocationBinding:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "tool_invocation_binding.schema.json"
    binding_id: str = ""
    step_id: str = ""
    session_id: str = ""
    run_id: str = ""
    tool_name: str = ""
    caller_role: str = ""
    requested_effect: str = ""
    arguments_summary: str = ""
    dispatch_status: str = "PENDING"
    idempotency_key: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ModelInvocationBinding:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "model_invocation_binding.schema.json"
    binding_id: str = ""
    step_id: str = ""
    session_id: str = ""
    run_id: str = ""
    model_profile_id: str = ""
    prompt_contract_version: str = ""
    prompt_binding_id: str = ""
    caller_role: str = ""
    requested_task_type: str = ""
    status: str = "PENDING"
    idempotency_key: str = ""
    output_quarantined: bool = False
    proposed_actions_ref: str = ""
    quarantine_reason: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class PromptBinding:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "prompt_binding.schema.json"
    binding_id: str = ""
    step_id: str = ""
    session_id: str = ""
    run_id: str = ""
    prompt_contract_id: str = ""
    prompt_contract_version: str = ""
    input_contract_schema_id: str = ""
    output_contract_schema_id: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ApprovalGateRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "approval_gate_record.schema.json"
    approval_record_id: str = ""
    step_id: str = ""
    session_id: str = ""
    run_id: str = ""
    created_at: str = ""
    gate_type: str = GATE_TYPE_APPROVAL
    reason: str = ""
    required_approver_role: str = ""
    approval_status: str = GATE_STATUS_PENDING
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def is_resolved(self) -> bool:
        return self.approval_status in ("APPROVED", "DENIED", "ABSTAIN", "NOT_REQUIRED")


@dataclass
class PromotionGateRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "promotion_gate_record.schema.json"
    promotion_record_id: str = ""
    session_id: str = ""
    run_id: str = ""
    created_at: str = ""
    promotion_target: str = ""
    promotion_status: str = GATE_STATUS_PENDING
    promotion_decision: str = ""
    proposal_id: str = ""
    policy_decision_id: str = ""
    candidate_id: str = ""
    rollback_ref: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def is_resolved(self) -> bool:
        return self.promotion_status in ("APPROVED", "DENIED", "ABSTAIN", "NOT_REQUIRED")


@dataclass
class RecoveryAction:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "recovery_action.schema.json"
    recovery_action_id: str = ""
    session_id: str = ""
    run_id: str = ""
    created_at: str = ""
    failure_class: str = ""
    failure_severity: str = "medium"
    recovery_strategy: str = RECOVERY_ACTION_NONE
    action_status: str = "PENDING"
    retry_count: int = 0
    max_retries: int = DEFAULT_MAX_RETRIES_PER_STEP
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries


@dataclass
class OrchestratorEvidenceEvent:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "orchestrator_evidence_event.schema.json"
    event_id: str = ""
    session_id: str = ""
    run_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    event_type: str = ""
    status: str = ""
    message: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class RunLedger:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "run_ledger.schema.json"
    ledger_id: str = ""
    session_id: str = ""
    run_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    source_component: str = SOURCE_COMPONENT
    final_status: str = ""
    task_id: str = ""
    steps_total: int = 0
    steps_completed: int = 0
    steps_failed: int = 0
    steps_blocked: int = 0
    final_decision: str = DECISION_CONTINUE
    events: list[dict] = field(default_factory=list)
    ledger_hash: str = ""
    previous_ledger_hash: str = ""
    event_count: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def compute_hash(self) -> str:
        return sha256_dict(self.to_dict())


@dataclass
class OrchestratorEvidenceManifest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "orchestrator_evidence_manifest.schema.json"
    manifest_id: str = ""
    session_id: str = ""
    run_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    component_id: str = ""
    validated_commit: str = ""
    evidence_files: list[str] = field(default_factory=list)
    evidence_file_hashes: dict = field(default_factory=dict)
    runtime_artifacts: list[str] = field(default_factory=list)
    source_mutation_status: str = "NOT_MUTATED"
    final_decision: str = DECISION_NOT_DONE
    evidence_manifest_sha256: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def compute_hash(self) -> str:
        return compute_self_hash(self.to_dict(), "evidence_manifest_sha256")


@dataclass
class OrchestratorReviewReport:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "orchestrator_review_report.schema.json"
    review_report_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    component_id: str = ""
    reviewed_commit: str = ""
    reviewed_at: str = ""
    commands_run: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    evidence_manifest_path: str = ""
    evidence_manifest_sha256: str = ""
    completion_record_sha256: str = ""
    final_verdict: str = "NOT_DONE"
    review_report_sha256: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def compute_hash(self) -> str:
        return compute_self_hash(self.to_dict(), "review_report_sha256")


@dataclass
class OrchestratorCompletionRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "orchestrator_completion_record.schema.json"
    completion_record_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    component_id: str = ""
    component_name: str = COMPONENT_NAME
    status: str = ""
    validated_commit: str = ""
    validated_at: str = ""
    canonical_subdirectories: list[str] = field(default_factory=list)
    commands_run: list[str] = field(default_factory=list)
    evidence_manifest_sha256: str = ""
    review_report_sha256: str = ""
    implementation_score: float = 0.0
    final_decision: str = DECISION_NOT_DONE
    completion_record_sha256: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def compute_hash(self) -> str:
        return compute_self_hash(self.to_dict(), "completion_record_sha256")


@dataclass
class RunAdmission:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "run_admission.schema.json"
    admission_id: str = ""
    run_id: str = ""
    created_at: str = ""
    requested_objective: str = ""
    risk_level: str = RISK_LEVEL_LOW
    allowed_mode: str = RUN_MODE_EXECUTE_CONTROLLED
    decision: str = "PENDING"
    evidence_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class OrchestratorContractCompatibility:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "orchestrator_contract_compatibility.schema.json"
    compatibility_id: str = ""
    run_id: str = ""
    created_at: str = ""
    checked_at: str = ""
    layer_contracts: dict = field(default_factory=dict)
    compatibility_status: str = "PENDING"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)
