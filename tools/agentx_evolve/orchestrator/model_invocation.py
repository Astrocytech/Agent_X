from __future__ import annotations

from typing import Any, Callable

from agentx_evolve.orchestrator.orchestrator_models import (
    ModelInvocationBinding,
    PromptBinding,
    ExecutionStep,
    utc_now_iso,
    new_id,
)


ALLOWED_MODEL_PROFILES = {"default", "fast", "precise"}
REQUIRED_PROMPT_CONTRACT_VERSION = "1.0"


def _check_model_profile_allowed(step: ExecutionStep, model_profile_id: str) -> bool:
    if model_profile_id not in ALLOWED_MODEL_PROFILES:
        return False
    return True


def invoke_model_for_step(
    step: ExecutionStep,
    model_profile_id: str,
    prompt_text: str,
    model_adapter_fn: Callable | None,
    binding_context: dict,
) -> tuple[ModelInvocationBinding, dict]:
    binding = ModelInvocationBinding(
        binding_id=new_id("mb"),
        step_id=step.step_id,
        run_id=step.run_id or "",
        model_profile_id=model_profile_id,
        prompt_contract_version=REQUIRED_PROMPT_CONTRACT_VERSION,
        caller_role=step.assigned_role,
        requested_task_type=step.step_name,
        status="PENDING",
        idempotency_key=f"model-{step.step_id}-{model_profile_id}",
    )

    if not _check_model_profile_allowed(step, model_profile_id):
        binding.status = "BLOCKED"
        binding.errors.append(f"Model profile {model_profile_id} not allowed")
        return binding, {"status": "BLOCKED", "error": binding.errors[-1]}

    if model_adapter_fn is None:
        binding.status = "BLOCKED"
        binding.errors.append("Model adapter unavailable")
        return binding, {"status": "BLOCKED", "error": binding.errors[-1]}

    try:
        result = model_adapter_fn(
            model_profile_id=model_profile_id,
            prompt=prompt_text,
            step_id=step.step_id,
            run_id=step.run_id,
        )
        binding.status = "COMPLETED" if result.get("status") in ("SUCCESS", None) else "FAILED"
        return binding, result
    except Exception as e:
        binding.status = "FAILED"
        binding.errors.append(str(e))
        return binding, {"status": "FAILED", "error": str(e)}


def create_prompt_binding_for_step(
    step: ExecutionStep,
    prompt_contract_id: str,
    input_schema_id: str,
    output_schema_id: str,
) -> PromptBinding:
    return PromptBinding(
        binding_id=new_id("pb"),
        step_id=step.step_id,
        run_id=step.run_id or "",
        prompt_contract_id=prompt_contract_id,
        prompt_contract_version=REQUIRED_PROMPT_CONTRACT_VERSION,
        input_contract_schema_id=input_schema_id,
        output_contract_schema_id=output_schema_id,
    )
