from __future__ import annotations

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    ParsedModelOutput,
    LLMWorkerContextPackage,
    ImplementationPlan,
    LLMWorkerResult,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_INVALID,
    ALLOWED_VALIDATION_COMMANDS,
)
from agentx_evolve.workers.llm_implementation_worker.worker_errors import (
    WORKER_PATCH_PROPOSAL_INVALID,
)


def generate_implementation_plan(
    task: LLMWorkerTask,
    parsed_output: ParsedModelOutput,
    context_package: LLMWorkerContextPackage,
) -> ImplementationPlan:
    steps = parsed_output.implementation_plan.get("steps", [])
    if not steps:
        steps = _build_default_steps(parsed_output)

    plan = ImplementationPlan(
        plan_id=new_id("ip"),
        created_at=utc_now_iso(),
        task_id=task.task_id,
        target_component_id=task.target_component_id,
        steps=steps,
        files_expected_to_change=parsed_output.files_to_change,
        schemas_expected_to_change=parsed_output.schemas_to_change,
        tests_expected_to_change=parsed_output.tests_to_change,
        risk_notes=parsed_output.risk_notes,
        required_authorities=parsed_output.implementation_plan.get(
            "required_authorities", []
        ),
        validation_commands=parsed_output.implementation_plan.get(
            "validation_commands", []
        ),
        acceptance_criteria_mapping=[
            {"acceptance_criteria": ac, "status": "planned", "evidence_ref": ""}
            for ac in task.acceptance_criteria
        ],
    )

    plan.implementation_plan_hash = sha256_dict(plan.to_dict())

    return plan


def _build_default_steps(parsed_output: ParsedModelOutput) -> list[dict]:
    steps = []
    for f in parsed_output.files_to_change:
        steps.append({
            "order": len(steps) + 1,
            "action": "modify",
            "target": f,
            "description": f"Implement changes in {f}",
        })
    for s in parsed_output.schemas_to_change:
        steps.append({
            "order": len(steps) + 1,
            "action": "update_schema",
            "target": s,
            "description": f"Update schema {s}",
        })
    for t in parsed_output.tests_to_change:
        steps.append({
            "order": len(steps) + 1,
            "action": "update_test",
            "target": t,
            "description": f"Update test {t}",
        })
    return steps


def validate_implementation_plan(
    plan: ImplementationPlan,
    task: LLMWorkerTask,
) -> LLMWorkerResult | None:
    errors = []

    if not plan.steps:
        errors.append("Implementation plan has no steps")

    for cmd in plan.validation_commands:
        if cmd not in ALLOWED_VALIDATION_COMMANDS:
            errors.append(
                f"Validation command '{cmd}' is not in the allowlist"
            )

    allowed_dirs = _get_allowed_dirs(task.target_component_id)
    for f in plan.files_expected_to_change:
        if not any(f.startswith(d) for d in allowed_dirs):
            errors.append(
                f"File '{f}' is outside allowed directories for {task.target_component_id}"
            )

    if errors:
        return LLMWorkerResult(
            worker_result_id=new_id("wr"),
            created_at=utc_now_iso(),
            task_id=task.task_id,
            status=WORKER_INVALID,
            message="Implementation plan validation failed",
            worker_mode=task.worker_mode,
            failure_class=WORKER_PATCH_PROPOSAL_INVALID,
            errors=errors,
        )

    return None


def _get_allowed_dirs(component_id: str) -> list[str]:
    return [f"src/{component_id}", f"tools/{component_id}"]
