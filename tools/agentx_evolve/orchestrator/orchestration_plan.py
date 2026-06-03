from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.orchestrator.orchestrator_models import (
    ExecutionStep,
    OrchestrationTask,
    TaskPlan,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    GATE_TYPE_APPROVAL,
    GATE_TYPE_GOVERNANCE,
    GATE_TYPE_PROMOTION,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_CRITICAL,
    RUNTIME_ARTIFACT_ROOT,
)


ALLOWED_ROLES = {"orchestrator", "tool_agent", "model_agent", "human_approver", "governance", "promotion_gate"}
ALLOWED_TOOLS = {"source_reader", "file_lister", "diff_viewer", "search_code", "read_file"}
ALLOWED_STEP_TYPES = {"POLICY", "TOOL", "MODEL", "GATE", "PROMOTION", "EVIDENCE", "PLANNING", "LOCKING"}


def decompose_task(task: OrchestrationTask) -> TaskPlan:
    errors: list[str] = []

    if not task.task_id:
        errors.append("task_id is required")
    if not task.title:
        errors.append("title is required")
    if not task.description:
        errors.append("description is required")

    scope = list(task.allowed_tools) if task.allowed_tools else []

    steps: list[dict] = []
    step_index = 0

    step = {
        "step_index": step_index,
        "step_name": "validate_task",
        "step_type": "POLICY",
        "assigned_role": "orchestrator",
        "description": "Validate task schema and policy",
        "idempotency_key": f"validate-{task.task_id}",
    }
    steps.append(step)
    step_index += 1

    if task.allowed_tools:
        step = {
            "step_index": step_index,
            "step_name": "execute_tools",
            "step_type": "TOOL",
            "assigned_role": "tool_agent",
            "description": f"Execute tools: {', '.join(task.allowed_tools)}",
            "idempotency_key": f"tools-{task.task_id}-{step_index}",
        }
        steps.append(step)
        step_index += 1

    if task.allowed_model_profiles:
        step = {
            "step_index": step_index,
            "step_name": "invoke_model",
            "step_type": "MODEL",
            "assigned_role": "model_agent",
            "description": f"Invoke model: {', '.join(task.allowed_model_profiles)}",
            "idempotency_key": f"model-{task.task_id}-{step_index}",
        }
        steps.append(step)
        step_index += 1

    if task.requires_human_approval:
        step = {
            "step_index": step_index,
            "step_name": "human_approval",
            "step_type": "GATE",
            "assigned_role": "human_approver",
            "description": "Required human approval gate",
            "gate_type": GATE_TYPE_APPROVAL,
            "idempotency_key": f"approval-{task.task_id}",
        }
        steps.append(step)
        step_index += 1

    if task.requires_governance:
        step = {
            "step_index": step_index,
            "step_name": "governance_check",
            "step_type": "GATE",
            "assigned_role": "governance",
            "description": "Required governance check",
            "gate_type": GATE_TYPE_GOVERNANCE,
            "idempotency_key": f"governance-{task.task_id}",
        }
        steps.append(step)
        step_index += 1

    if task.requires_promotion_gate:
        step = {
            "step_index": step_index,
            "step_name": "promotion_gate",
            "step_type": "PROMOTION",
            "assigned_role": "promotion_gate",
            "description": "Required promotion gate",
            "gate_type": GATE_TYPE_PROMOTION,
            "idempotency_key": f"promotion-{task.task_id}",
        }
        steps.append(step)
        step_index += 1

    step = {
        "step_index": step_index,
        "step_name": "finalize",
        "step_type": "EVIDENCE",
        "assigned_role": "orchestrator",
        "description": "Finalize run and write evidence",
        "idempotency_key": f"finalize-{task.task_id}",
    }
    steps.append(step)

    plan = TaskPlan(
        plan_id=new_id("plan"),
        created_at=utc_now_iso(),
        task_id=task.task_id,
        plan_status="PENDING",
        steps=steps,
        risk_level=task.risk_level,
        objective=task.description,
        scope=scope,
        errors=errors,
    )
    plan.plan_hash = plan.compute_hash()
    return plan


def high_risk_requires_approval(task: OrchestrationTask) -> bool:
    return task.risk_level in (RISK_LEVEL_HIGH, RISK_LEVEL_CRITICAL)


def source_mutation_requires_governance(task: OrchestrationTask) -> bool:
    return task.task_type in ("SOURCE_MUTATION", "PATCH_APPLY")


def validate_execution_step(step_data: dict) -> list[str]:
    errors = []
    role = step_data.get("assigned_role", "")
    if role and role not in ALLOWED_ROLES:
        errors.append(f"Unknown role: {role}")
    step_type = step_data.get("step_type", "")
    if step_type and step_type not in ALLOWED_STEP_TYPES:
        errors.append(f"Unknown step type: {step_type}")
    tool_name = step_data.get("tool_name", "")
    if tool_name and tool_name not in ALLOWED_TOOLS:
        errors.append(f"Unknown tool: {tool_name}")
    return errors


def build_execution_steps(plan: TaskPlan) -> list[ExecutionStep]:
    steps: list[ExecutionStep] = []
    for sdata in plan.steps:
        step = ExecutionStep(
            step_id=new_id("step"),
            plan_id=plan.plan_id,
            run_id=plan.run_id,
            created_at=utc_now_iso(),
            updated_at=utc_now_iso(),
            step_index=sdata.get("step_index", 0),
            step_name=sdata.get("step_name", ""),
            step_type=sdata.get("step_type", ""),
            assigned_role=sdata.get("assigned_role", ""),
            status="PENDING",
            idempotency_key=sdata.get("idempotency_key", ""),
            description=sdata.get("description", ""),
        )
        steps.append(step)
    return steps


def order_execution_steps(steps: list[ExecutionStep]) -> list[ExecutionStep]:
    return sorted(steps, key=lambda s: s.step_index)


def write_execution_steps(
    steps: list[ExecutionStep],
    run_id: str,
    repo_root: Path,
) -> dict:
    artifact_dir = repo_root / RUNTIME_ARTIFACT_ROOT / "runs" / run_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_dir / "execution_steps.jsonl"
    with open(path, "w") as f:
        for step in steps:
            import json as _json
            f.write(_json.dumps(step.to_dict(), sort_keys=True, default=str) + "\n")
    return {"path": str(path)}
