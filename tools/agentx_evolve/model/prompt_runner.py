from __future__ import annotations
import time
import hashlib
from typing import Any
from agentx_evolve.model.model_models import (
    PromptRequest, ModelResponse, ModelProfile,
    MD_SUCCESS, MD_FAILED, MD_INVALID_OUTPUT,
    MD_INSUFFICIENT_CONTEXT, MD_TIMEOUT,
    new_id, utc_now_iso,
)
from agentx_evolve.model.json_output_validator import JsonOutputValidator
from agentx_evolve.model.model_registry import ModelRegistry


class ModelRetryPolicy:
    def __init__(self, max_retries: int = 2, backoff_seconds: float = 1.0):
        self._max_retries = max_retries
        self._backoff = backoff_seconds

    def should_retry(self, response: ModelResponse, attempt: int) -> bool:
        if attempt >= self._max_retries:
            return False
        if response.status in (MD_TIMEOUT, MD_FAILED):
            return True
        if response.status == MD_INVALID_OUTPUT:
            return True
        return False

    def get_backoff(self, attempt: int) -> float:
        return self._backoff * (2 ** attempt)


class BaseProvider:
    def __init__(self, config: dict | None = None):
        self._config = config or {}

    def call(self, request: PromptRequest) -> ModelResponse:
        raise NotImplementedError

    def _make_response(self, request: PromptRequest, status: str,
                       content: str = "", **kwargs) -> ModelResponse:
        return ModelResponse(
            response_id=new_id("mr"),
            timestamp=utc_now_iso(),
            request_id=request.request_id,
            status=status,
            content=content,
            profile_id=request.profile_id,
            prompt_hash=hashlib.sha256(
                (request.system_prompt + request.user_prompt).encode()
            ).hexdigest()[:16],
            output_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
            **kwargs,
        )


class LocalProvider(BaseProvider):
    def call(self, request: PromptRequest) -> ModelResponse:
        if request.json_mode:
            content = '{"status": "ok", "task": "' + request.task_type + '", "message": "simulated"}'
        else:
            content = f"[local:{request.profile_id}] simulated response for {request.task_type}"
        return self._make_response(
            request, MD_SUCCESS,
            content=content,
            model_used="local-simulated",
            tokens_in=len(request.system_prompt) + len(request.user_prompt),
            tokens_out=50,
            duration_ms=100.0,
        )


class PromptRunner:
    def __init__(self, registry: ModelRegistry | None = None,
                 validator: JsonOutputValidator | None = None,
                 retry_policy: ModelRetryPolicy | None = None):
        self._registry = registry or ModelRegistry()
        self._validator = validator or JsonOutputValidator()
        self._retry_policy = retry_policy or ModelRetryPolicy()
        self._providers: dict[str, BaseProvider] = {
            "local": LocalProvider(),
        }

    def register_provider(self, provider_id: str, provider: BaseProvider) -> None:
        self._providers[provider_id] = provider

    def run(self, request: PromptRequest) -> ModelResponse:
        profile = self._registry.get_profile(request.profile_id)
        if profile is None:
            return ModelResponse(
                response_id=new_id("mr"), timestamp=utc_now_iso(),
                request_id=request.request_id, status=MD_FAILED,
                content="", errors=[f"Unknown profile: {request.profile_id}"],
            )
        provider = self._providers.get(profile.provider)
        if provider is None:
            return ModelResponse(
                response_id=new_id("mr"), timestamp=utc_now_iso(),
                request_id=request.request_id, status=MD_FAILED,
                content="", errors=[f"Unknown provider: {profile.provider}"],
            )
        last_response = None
        for attempt in range(profile.retry_limit + 1):
            start = time.monotonic()
            try:
                response = provider.call(request)
            except Exception as e:
                response = self._make_error(request, f"Provider error: {e}", attempt)
            response.retry_attempts = attempt
            response.duration_ms = (time.monotonic() - start) * 1000

            if response.status == MD_SUCCESS and request.json_mode:
                if request.expected_schema:
                    valid, data, error = self._validator.validate(
                        response.content, request.expected_schema
                    )
                    if valid:
                        response.json_data = data
                        return response
                    response.status = MD_INVALID_OUTPUT
                    response.errors.append(f"Schema validation failed: {error}")
                else:
                    valid, data, error = self._validator.validate(response.content)
                    if valid:
                        response.json_data = data
                        return response
                    response.status = MD_INVALID_OUTPUT
                    response.errors.append(f"JSON parse failed: {error}")
            if response.status == MD_SUCCESS:
                return response
            last_response = response
            if not self._retry_policy.should_retry(response, attempt):
                break
            time.sleep(self._retry_policy.get_backoff(attempt))
        return last_response or self._make_error(request, "No response", 0)

    def _make_error(self, request: PromptRequest, message: str, attempt: int) -> ModelResponse:
        return ModelResponse(
            response_id=new_id("mr"), timestamp=utc_now_iso(),
            request_id=request.request_id, status=MD_FAILED,
            content="", errors=[message], retry_attempts=attempt,
        )
