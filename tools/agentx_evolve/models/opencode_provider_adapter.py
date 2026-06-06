from __future__ import annotations

from agentx_evolve.models.model_adapter import BaseModelProviderAdapter, make_blocked_response
from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    ModelProviderProfile,
    MODEL_DIRECT_ACTION_BLOCKED,
)


class OpenCodeProviderAdapter(BaseModelProviderAdapter):

    def is_available(self, context: dict) -> bool:
        return False

    def run_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        if not self.is_available(context):
            return make_blocked_response(request, "OpenCode provider adapter is a stub - blocked by default", MODEL_DIRECT_ACTION_BLOCKED)
        return make_blocked_response(request, "OpenCode provider adapter not connected")

    def run_json_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        if not self.is_available(context):
            return make_blocked_response(request, "OpenCode provider adapter is a stub - blocked by default", MODEL_DIRECT_ACTION_BLOCKED)
        return make_blocked_response(request, "OpenCode provider adapter not connected")
