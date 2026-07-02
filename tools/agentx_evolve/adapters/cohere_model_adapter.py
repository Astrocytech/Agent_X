from __future__ import annotations

import json
import os
from hashlib import sha256
from typing import Any

from agentx_evolve.adapters.model_adapter import ModelAdapter
from agentx_evolve.adapters.model_request import ModelRequest
from agentx_evolve.adapters.model_response import (
    ModelResponse,
    STATUS_SUCCESS,
    STATUS_REFUSAL,
    STATUS_BLOCKED,
    STATUS_SCHEMA_ERROR,
    STATUS_ERROR,
    STATUS_TIMEOUT,
)

COHERE_PROVIDER_ID = "cohere"
COHERE_MODEL_ID = "cohere/command-r-plus"

LIVE_FLAG_ENV = "AGENTX_COHERE_LIVE"


class CohereModelAdapter(ModelAdapter):
    def __init__(self, live: bool | None = None):
        self._live = live if live is not None else os.environ.get(LIVE_FLAG_ENV, "").lower() in ("1", "true", "yes")

    def describe_capabilities(self) -> dict[str, Any]:
        return {
            "provider_id": COHERE_PROVIDER_ID,
            "model_id": COHERE_MODEL_ID,
            "live_required": True,
            "offline": not self._live,
            "supported_statuses": ["SUCCESS", "REFUSAL", "BLOCKED", "ERROR", "SCHEMA_ERROR", "TIMEOUT"],
        }

    def validate_request(self, request: dict[str, Any]) -> dict[str, Any]:
        errors: list[str] = []
        if not request.get("run_id"):
            errors.append("run_id is required")
        if not request.get("prompt_contract_id"):
            errors.append("prompt_contract_id is required")
        if not request.get("context_packet_hash"):
            errors.append("context_packet_hash is required")
        if not request.get("provider_id"):
            errors.append("provider_id is required")
        if not request.get("model_id"):
            errors.append("model_id is required")
        return {"valid": len(errors) == 0, "errors": errors}

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        if not self._live:
            return ModelResponse(
                provider_id=COHERE_PROVIDER_ID,
                model_id=COHERE_MODEL_ID,
                status=STATUS_BLOCKED,
                output_text="",
                failure_class="live_provider_disabled",
                failure_reason="Cohere adapter requires live flag (AGENTX_COHERE_LIVE=1)",
            ).to_dict()

        api_key = os.environ.get("COHERE_API_KEY", "")
        if not api_key:
            return ModelResponse(
                provider_id=COHERE_PROVIDER_ID,
                model_id=COHERE_MODEL_ID,
                status=STATUS_ERROR,
                output_text="",
                failure_class="secret_missing",
                failure_reason="COHERE_API_KEY not set",
            ).to_dict()

        prompt_text = request.get("prompt_text", "")
        max_tokens = request.get("max_tokens", 2048)
        temperature = request.get("temperature", 0.0)

        try:
            import httpx
            resp = httpx.post(
                "https://api.cohere.ai/v1/generate",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": request.get("model_id", COHERE_MODEL_ID),
                    "prompt": prompt_text,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            output_text = data.get("text", "")

            if not output_text:
                return ModelResponse(
                    provider_id=COHERE_PROVIDER_ID,
                    model_id=COHERE_MODEL_ID,
                    status=STATUS_ERROR,
                    output_text="",
                    failure_class="model_provider_error",
                    failure_reason="empty response from Cohere API",
                ).to_dict()

            return ModelResponse(
                provider_id=COHERE_PROVIDER_ID,
                model_id=COHERE_MODEL_ID,
                status=STATUS_SUCCESS,
                output_text=output_text,
            ).to_dict()

        except httpx.TimeoutException:
            return ModelResponse(
                provider_id=COHERE_PROVIDER_ID,
                model_id=COHERE_MODEL_ID,
                status=STATUS_TIMEOUT,
                output_text="",
                failure_class="model_timeout",
                failure_reason="Cohere API request timed out",
            ).to_dict()

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code == 401:
                failure_class = "secret_missing"
                reason = "Cohere API returned 401 — invalid API key"
            elif status_code == 429:
                failure_class = "model_provider_error"
                reason = "Cohere API rate limited"
            else:
                failure_class = "model_provider_error"
                reason = f"Cohere API returned {status_code}"
            return ModelResponse(
                provider_id=COHERE_PROVIDER_ID,
                model_id=COHERE_MODEL_ID,
                status=STATUS_ERROR,
                output_text="",
                failure_class=failure_class,
                failure_reason=reason,
            ).to_dict()

        except Exception as e:
            return ModelResponse(
                provider_id=COHERE_PROVIDER_ID,
                model_id=COHERE_MODEL_ID,
                status=STATUS_ERROR,
                output_text="",
                failure_class="model_provider_error",
                failure_reason=f"Cohere API error: {e}",
            ).to_dict()

    def normalize_response(self, response: dict[str, Any]) -> dict[str, Any]:
        normalized = {
            "provider_id": response.get("provider_id", COHERE_PROVIDER_ID),
            "model_id": response.get("model_id", COHERE_MODEL_ID),
            "status": response.get("status", STATUS_BLOCKED),
            "output_hash": response.get("output_hash", ""),
            "structured_output": response.get("structured_output"),
            "failure_class": response.get("failure_class", ""),
            "failure_reason": response.get("failure_reason", ""),
        }
        if not normalized["output_hash"] and response.get("output_text"):
            normalized["output_hash"] = sha256(response["output_text"].encode("utf-8")).hexdigest()
        return normalized
