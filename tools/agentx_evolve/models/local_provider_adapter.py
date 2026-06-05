from __future__ import annotations

from agentx_evolve.models.model_adapter import BaseModelProviderAdapter, make_blocked_response
from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    ModelProviderProfile,
    MODEL_PROVIDER_UNAVAILABLE,
)


class LocalProviderAdapter(BaseModelProviderAdapter):

    def is_available(self, context: dict) -> bool:
        return context.get("local_runtime_available", False)

    def run_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        if not self.is_available(context):
            return make_blocked_response(request, "Local runtime not available", MODEL_PROVIDER_UNAVAILABLE)
        return make_blocked_response(request, "Local provider run_prompt not implemented", "COMMAND_NOT_IMPLEMENTED")

    def run_json_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        if not self.is_available(context):
            return make_blocked_response(request, "Local runtime not available", MODEL_PROVIDER_UNAVAILABLE)
        return make_blocked_response(request, "Local provider run_json_prompt not implemented", "COMMAND_NOT_IMPLEMENTED")
