from __future__ import annotations

from agentx_evolve.models.model_adapter import BaseModelProviderAdapter, make_blocked_response
from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    ModelProviderProfile,
    MODEL_NETWORK_NOT_ALLOWED,
)


class OpenAICompatibleAdapter(BaseModelProviderAdapter):

    def is_available(self, context: dict) -> bool:
        return context.get("openai_compatible_running", False)

    def run_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        if not self.is_available(context):
            return make_blocked_response(request, "OpenAI-compatible adapter disabled by default", MODEL_NETWORK_NOT_ALLOWED)
        return make_blocked_response(request, "OpenAI-compatible adapter not connected - requires local server")

    def run_json_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        if not self.is_available(context):
            return make_blocked_response(request, "OpenAI-compatible adapter disabled by default", MODEL_NETWORK_NOT_ALLOWED)
        return make_blocked_response(request, "OpenAI-compatible adapter not connected - requires local server")
