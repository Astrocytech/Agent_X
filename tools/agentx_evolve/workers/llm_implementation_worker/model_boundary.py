from __future__ import annotations

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerPromptPackage,
    LLMWorkerModelRequest,
    LLMWorkerModelResponse,
    LLMWorkerResult,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    DEP_AVAILABLE,
    DEP_MISSING,
    DEFAULT_TEMPERATURE,
    MODEL_RESPONSE_STATUS_SUCCESS,
    MODEL_RESPONSE_STATUS_BLOCKED,
    MODEL_RESPONSE_STATUS_FAILED,
    MODEL_RESPONSE_STATUS_INVALID,
)
from agentx_evolve.workers.llm_implementation_worker.worker_errors import (
    WORKER_MODEL_CALL_FAILED,
    WORKER_MODEL_POLICY_DENIED,
    WORKER_MODEL_RESPONSE_INVALID,
)


def build_model_request(
    task: LLMWorkerTask,
    prompt_package: LLMWorkerPromptPackage,
    model_profile_id: str,
    policy_context: dict,
) -> LLMWorkerModelRequest:
    request = LLMWorkerModelRequest(
        model_request_id=new_id("mr"),
        created_at=utc_now_iso(),
        task_id=task.task_id,
        model_profile_id=model_profile_id,
        prompt_package_id=prompt_package.prompt_package_id,
        requested_capability="implementation",
        max_output_chars=task.max_model_output_chars,
        temperature=policy_context.get("temperature", DEFAULT_TEMPERATURE),
        deterministic=True,
    )

    request.model_request_hash = sha256_dict({
        "task_id": request.task_id,
        "model_profile_id": request.model_profile_id,
        "prompt_package_id": request.prompt_package_id,
        "requested_capability": request.requested_capability,
        "temperature": request.temperature,
    })

    return request


def call_model_adapter(
    model_request: LLMWorkerModelRequest,
    prompt_package: LLMWorkerPromptPackage,
    model_context: dict,
) -> LLMWorkerModelResponse:
    adapter_status = model_context.get("status", DEP_MISSING)

    if adapter_status == DEP_MISSING:
        return LLMWorkerModelResponse(
            model_response_id=new_id("mres"),
            created_at=utc_now_iso(),
            task_id=model_request.task_id,
            model_request_id=model_request.model_request_id,
            status=MODEL_RESPONSE_STATUS_BLOCKED,
            safe_summary="Model adapter is missing. Model call blocked.",
            failure_class=WORKER_MODEL_CALL_FAILED,
            errors=["Model adapter unavailable"],
        )

    if adapter_status == "FAILED":
        return LLMWorkerModelResponse(
            model_response_id=new_id("mres"),
            created_at=utc_now_iso(),
            task_id=model_request.task_id,
            model_request_id=model_request.model_request_id,
            status=MODEL_RESPONSE_STATUS_FAILED,
            safe_summary="Model adapter returned failure status.",
            failure_class=WORKER_MODEL_CALL_FAILED,
            errors=["Model adapter failed"],
        )

    try:
        adapter_fn = model_context.get("adapter_fn")
        if adapter_fn is None:
            return LLMWorkerModelResponse(
                model_response_id=new_id("mres"),
                created_at=utc_now_iso(),
                task_id=model_request.task_id,
                model_request_id=model_request.model_request_id,
                status=MODEL_RESPONSE_STATUS_INVALID,
                safe_summary="No adapter function provided.",
                failure_class=WORKER_MODEL_RESPONSE_INVALID,
                errors=["No adapter function"],
            )

        raw_response = adapter_fn(
            model_request=model_request,
            prompt_package=prompt_package,
        )

        response = LLMWorkerModelResponse(
            model_response_id=new_id("mres"),
            created_at=utc_now_iso(),
            task_id=model_request.task_id,
            model_request_id=model_request.model_request_id,
            status=MODEL_RESPONSE_STATUS_SUCCESS,
            safe_summary=raw_response.get(
                "safe_summary",
                "Model response received.",
            ),
            raw_response_ref=raw_response.get("raw_response_ref"),
            parsed_output_ref=raw_response.get("parsed_output_ref"),
            usage_summary=raw_response.get("usage_summary", {}),
        )

        response.model_response_hash = sha256_dict(response.to_dict())
        return response

    except Exception as e:
        return LLMWorkerModelResponse(
            model_response_id=new_id("mres"),
            created_at=utc_now_iso(),
            task_id=model_request.task_id,
            model_request_id=model_request.model_request_id,
            status=MODEL_RESPONSE_STATUS_FAILED,
            safe_summary=f"Model adapter call failed: {e}",
            failure_class=WORKER_MODEL_CALL_FAILED,
            errors=[f"Adapter exception: {e}"],
        )
