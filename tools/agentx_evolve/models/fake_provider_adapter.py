from __future__ import annotations

import json

from agentx_evolve.models.model_adapter import BaseModelProviderAdapter
from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    ModelProviderProfile,
    utc_now_iso,
    new_id,
    SOURCE_COMPONENT,
    MODEL_STATUS_SUCCESS,
    MODEL_STATUS_BLOCKED,
)
from agentx_evolve.models.json_output_validator import parse_json_output


class FakeProviderAdapter(BaseModelProviderAdapter):

    def is_available(self, context: dict) -> bool:
        return True

    def run_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        now = utc_now_iso()
        raw = f'Fake response for: {request.prompt[:50]}'
        return ModelResponse(
            model_response_id=new_id("res"),
            model_request_id=request.model_request_id,
            timestamp=now,
            source_component=SOURCE_COMPONENT,
            model_id=request.model_id,
            provider_id=request.provider_id,
            status=MODEL_STATUS_SUCCESS,
            message="Fake provider response",
            raw_output=raw,
            json_output=None,
            json_valid=False,
            schema_valid=True,
            prompt_hash="fake_hash",
            output_hash="fake_hash",
            token_count_input=len(request.prompt.split()),
            token_count_output=len(raw.split()),
        )

    def run_json_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        now = utc_now_iso()
        json_data = {
            "summary": f"Fake summary for: {request.prompt[:50]}",
            "task_type": request.task_type,
            "status": "simulated",
        }
        raw = json.dumps(json_data)
        return ModelResponse(
            model_response_id=new_id("res"),
            model_request_id=request.model_request_id,
            timestamp=now,
            source_component=SOURCE_COMPONENT,
            model_id=request.model_id,
            provider_id=request.provider_id,
            status=MODEL_STATUS_SUCCESS,
            message="Fake provider JSON response",
            raw_output=raw,
            json_output=json_data,
            json_valid=True,
            schema_valid=True,
            prompt_hash="fake_hash",
            output_hash="fake_hash",
            token_count_input=len(request.prompt.split()),
            token_count_output=len(raw.split()),
        )
