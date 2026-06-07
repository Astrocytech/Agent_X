from __future__ import annotations

from pathlib import Path

from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    ModelRegistry,
    ModelProfile,
    ModelProviderProfile,
    utc_now_iso,
    new_id,
    SOURCE_COMPONENT,
    MODEL_STATUS_BLOCKED,
    MODEL_STATUS_INVALID,
    MODEL_STATUS_RETRYABLE,
    MODEL_STATUS_FAILED,
    POLICY_ALLOW,
    POLICY_BLOCK,
    SELECTION_ALLOW,
    SELECTION_BLOCK,
    ALL_TASK_TYPES,
)
from agentx_evolve.models.model_registry import get_model_profile, get_provider_profile
from agentx_evolve.models.model_policy import check_model_permission
from agentx_evolve.models.model_selector import select_model_for_task
from agentx_evolve.models.model_request_validator import validate_model_request
from agentx_evolve.models.model_response_validator import validate_model_response
from agentx_evolve.models.json_output_validator import parse_json_output, validate_json_output, make_invalid_json_response
from agentx_evolve.models.model_retry_policy import should_retry_model_response, make_retry_record, DEFAULT_MAX_RETRIES
from agentx_evolve.models.model_call_logger import write_model_call_evidence, append_model_retry
from agentx_evolve.models.invalid_model_request import handle_invalid_model_request
from agentx_evolve.models.ollama_adapter import OllamaAdapter
from agentx_evolve.models.lmstudio_adapter import LMStudioAdapter
from agentx_evolve.models.openai_compatible_adapter import OpenAICompatibleAdapter
from agentx_evolve.models.hosted_model_adapter import HostedModelAdapter
from agentx_evolve.models.dev_provider_adapter import DevProviderAdapter
from agentx_evolve.models.model_adapter import BaseModelProviderAdapter, make_blocked_response
from agentx_evolve.model_runtime.runtime_models import RuntimeProfile


def _get_adapter(provider_profile: ModelProviderProfile) -> BaseModelProviderAdapter | None:
    kind = provider_profile.provider_type
    mapping = {
        "DEV": DevProviderAdapter,
        "OLLAMA": OllamaAdapter,
        "LMSTUDIO": LMStudioAdapter,
        "OPENAI_COMPATIBLE": OpenAICompatibleAdapter,
        "HOSTED": HostedModelAdapter,
    }
    cls = mapping.get(kind)
    if cls is None:
        return None
    return cls(provider_profile)


def run_prompt(
    request: ModelRequest,
    registry: ModelRegistry,
    runtime_profile: RuntimeProfile | None = None,
    policy_context: dict | None = None,
    provider_context: dict | None = None,
    repo_root: Path | None = None,
) -> ModelResponse:
    return _run_prompt_impl(request, registry, runtime_profile, policy_context, provider_context, repo_root, json_only=False)


def run_json_prompt(
    request: ModelRequest,
    registry: ModelRegistry,
    runtime_profile: RuntimeProfile | None = None,
    policy_context: dict | None = None,
    provider_context: dict | None = None,
    expected_schema: dict | None = None,
    repo_root: Path | None = None,
) -> ModelResponse:
    return _run_prompt_impl(request, registry, runtime_profile, policy_context, provider_context, repo_root, json_only=True, expected_schema=expected_schema)


def _run_prompt_impl(
    request: ModelRequest,
    registry: ModelRegistry,
    runtime_profile: RuntimeProfile | None,
    policy_context: dict | None,
    provider_context: dict | None,
    repo_root: Path | None,
    json_only: bool = False,
    expected_schema: dict | None = None,
) -> ModelResponse:
    ctx = policy_context or {}
    prov_ctx = provider_context or {}
    rp = runtime_profile

    # 1. Validate request
    req_errors = validate_model_request(request, registry)
    if req_errors:
        resp = handle_invalid_model_request(None, "; ".join(req_errors))
        if repo_root:
            from agentx_evolve.models.model_call_logger import append_invalid_model
            append_invalid_model(request, resp, repo_root)
        return resp

    # 2. Get model and provider profiles
    model_profile = get_model_profile(registry, request.model_id)
    if model_profile is None:
        resp = handle_invalid_model_request(None, f"Model not found: {request.model_id}")
        if repo_root:
            from agentx_evolve.models.model_call_logger import append_invalid_model
            append_invalid_model(request, resp, repo_root)
        return resp

    provider_profile = get_provider_profile(registry, request.provider_id)
    if provider_profile is None:
        resp = handle_invalid_model_request(None, f"Provider not found: {request.provider_id}")
        return resp

    # 3. Policy check
    policy = check_model_permission(request, model_profile, provider_profile, ctx)
    if policy.decision == POLICY_BLOCK:
        resp = make_blocked_response(request, policy.reason, "MODEL_POLICY_DENIED")
        if repo_root:
            from agentx_evolve.models.model_call_logger import append_blocked_model
            append_blocked_model(request, resp, repo_root)
        return resp

    # 4. Selection check
    selection = select_model_for_task(request, registry, vars(rp) if rp else None, ctx)
    if selection.decision == SELECTION_BLOCK:
        resp = make_blocked_response(request, f"Selection blocked: {selection.reason}", "MODEL_NOT_FOUND")
        if repo_root:
            from agentx_evolve.models.model_call_logger import append_blocked_model
            append_blocked_model(request, resp, repo_root)
        return resp

    # 5. Get provider adapter
    adapter = _get_adapter(provider_profile)
    if adapter is None or not adapter.is_available(prov_ctx):
        resp = make_blocked_response(request, f"Provider {provider_profile.provider_id} not available", "MODEL_PROVIDER_UNAVAILABLE")
        if repo_root:
            from agentx_evolve.models.model_call_logger import append_blocked_model
            append_blocked_model(request, resp, repo_root)
        return resp

    # 6. Run prompt with retry
    max_retries = provider_profile.max_retries
    for attempt in range(max_retries + 1):
        if json_only:
            response = adapter.run_json_prompt(request, provider_profile, prov_ctx)
        else:
            response = adapter.run_prompt(request, provider_profile, prov_ctx)

        # Validate response
        resp_errors = validate_model_response(response)
        if resp_errors:
            response.errors.extend(resp_errors)

        if json_only:
            parsed = parse_json_output(response.raw_output)
            if parsed is not None:
                response.json_output = parsed
                response.json_valid = True
                schema_errors = validate_json_output(parsed, expected_schema)
                if schema_errors:
                    response.errors.extend(schema_errors)
                    response.schema_valid = False
                else:
                    response.schema_valid = True
            else:
                response.json_valid = False
                response.schema_valid = False

        # Check retry
        is_retryable = should_retry_model_response(response, request, attempt, max_retries)
        if is_retryable and attempt < max_retries:
            retry_record = make_retry_record(request, response, attempt + 1)
            if repo_root:
                append_model_retry(retry_record, repo_root)
            request.retry_attempt = attempt + 1
            continue
        elif not is_retryable:
            break

    # 7. Write evidence
    if repo_root:
        write_model_call_evidence(request, response, repo_root)

    return response
