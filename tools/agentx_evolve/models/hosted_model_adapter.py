from __future__ import annotations

from agentx_evolve.models.model_adapter import BaseModelProviderAdapter, make_blocked_response
from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    ModelProviderProfile,
    MODEL_HOSTED_NOT_ALLOWED,
)


class HostedModelAdapter(BaseModelProviderAdapter):

    def is_available(self, context: dict) -> bool:
        return context.get("hosted_provider_approved", False)

    def run_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        if not self.is_available(context):
            return make_blocked_response(request, "Hosted providers are disabled by default", MODEL_HOSTED_NOT_ALLOWED)
        return make_blocked_response(request, "Hosted adapter not connected")

    def run_json_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        if not self.is_available(context):
            return make_blocked_response(request, "Hosted providers are disabled by default", MODEL_HOSTED_NOT_ALLOWED)
        return make_blocked_response(request, "Hosted adapter not connected")
