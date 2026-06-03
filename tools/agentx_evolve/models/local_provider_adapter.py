from __future__ import annotations

from agentx_evolve.models.model_adapter import BaseModelProviderAdapter, make_blocked_response
from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    ModelProviderProfile,
    PROVIDER_LOCAL,
)


class LocalProviderAdapter(BaseModelProviderAdapter):

    def is_available(self, context: dict) -> bool:
        return context.get("local_provider_available", False)

    def run_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        if not self.is_available(context):
            return make_blocked_response(request, "Local provider not available in this context")
        return make_blocked_response(request, "Local provider adapter not connected to a runtime")

    def run_json_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        if not self.is_available(context):
            return make_blocked_response(request, "Local provider not available in this context")
        return make_blocked_response(request, "Local provider adapter not connected to a runtime")
