from __future__ import annotations

import json
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
)


MOCK_PROVIDER_ID = "deterministic_mock"
MOCK_MODEL_ID = "mock/v0"

FIXED_SUCCESS_OUTPUT = json.dumps({"action": "read_repo_info", "params": {"path": "."}})
FIXED_REFUSAL_MESSAGE = "I cannot fulfill this request as it involves unsafe operations."
FIXED_MALFORMED_OUTPUT = "{invalid json without proper structure"
FIXED_UNSAFE_PROPOSAL = json.dumps({"action": "write_file", "params": {"path": "/etc/passwd", "content": "hacked"}})


def _hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


class DeterministicMockModelAdapter(ModelAdapter):
    def __init__(self, seed: int = 42):
        self._seed = seed

    def describe_capabilities(self) -> dict[str, Any]:
        return {
            "provider_id": MOCK_PROVIDER_ID,
            "model_id": MOCK_MODEL_ID,
            "deterministic": True,
            "offline": True,
            "supported_statuses": ["SUCCESS", "REFUSAL", "BLOCKED", "SCHEMA_ERROR"],
        }

    def validate_request(self, request: dict[str, Any]) -> dict[str, Any]:
        errors: list[str] = []
        if not request.get("run_id"):
            errors.append("run_id is required")
        if not request.get("prompt_contract_id"):
            errors.append("prompt_contract_id is required")
        if not request.get("context_packet_hash"):
            errors.append("context_packet_hash is required")
        return {"valid": len(errors) == 0, "errors": errors}

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        prompt_text = request.get("prompt_text", "")
        context_packet_hash = request.get("context_packet_hash", "")

        seed_input = f"{self._seed}:{prompt_text}:{context_packet_hash}"
        deterministic_flag = sha256(seed_input.encode("utf-8")).hexdigest()[:8]

        if "malformed" in prompt_text.lower():
            return ModelResponse(
                provider_id=MOCK_PROVIDER_ID,
                model_id=MOCK_MODEL_ID,
                status=STATUS_SCHEMA_ERROR,
                output_text=FIXED_MALFORMED_OUTPUT,
                failure_class="model_schema_error",
                failure_reason="mock malformed output triggered",
            ).to_dict()

        if "refuse" in prompt_text.lower() or "refusal" in prompt_text.lower():
            return ModelResponse(
                provider_id=MOCK_PROVIDER_ID,
                model_id=MOCK_MODEL_ID,
                status=STATUS_REFUSAL,
                output_text=FIXED_REFUSAL_MESSAGE,
                failure_class="model_refusal",
                failure_reason="mock refusal triggered",
            ).to_dict()

        if "unsafe" in prompt_text.lower():
            return ModelResponse(
                provider_id=MOCK_PROVIDER_ID,
                model_id=MOCK_MODEL_ID,
                status=STATUS_BLOCKED,
                output_text=FIXED_UNSAFE_PROPOSAL,
                failure_class="model_schema_error",
                failure_reason="mock unsafe proposal blocked",
            ).to_dict()

        if "timeout" in prompt_text.lower():
            return ModelResponse(
                provider_id=MOCK_PROVIDER_ID,
                model_id=MOCK_MODEL_ID,
                status=STATUS_ERROR,
                output_text="",
                failure_class="model_timeout",
                failure_reason="mock timeout triggered",
            ).to_dict()

        output_text = json.dumps({
            "action": "read_repo_info",
            "params": {"path": "."},
            "deterministic_flag": deterministic_flag,
        })

        return ModelResponse(
            provider_id=MOCK_PROVIDER_ID,
            model_id=MOCK_MODEL_ID,
            status=STATUS_SUCCESS,
            output_text=output_text,
            structured_output={"action": "read_repo_info", "params": {"path": "."}},
        ).to_dict()

    def normalize_response(self, response: dict[str, Any]) -> dict[str, Any]:
        normalized = {
            "provider_id": response.get("provider_id", MOCK_PROVIDER_ID),
            "model_id": response.get("model_id", MOCK_MODEL_ID),
            "status": response.get("status", STATUS_BLOCKED),
            "output_hash": response.get("output_hash", ""),
            "structured_output": response.get("structured_output"),
            "failure_class": response.get("failure_class", ""),
            "failure_reason": response.get("failure_reason", ""),
        }
        if not normalized["output_hash"] and response.get("output_text"):
            normalized["output_hash"] = _hash(response["output_text"])
        return normalized
