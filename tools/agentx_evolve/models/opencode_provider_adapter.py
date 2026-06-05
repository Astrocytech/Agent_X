from __future__ import annotations

from agentx_evolve.models.model_adapter import BaseModelProviderAdapter, make_blocked_response
from agentx_evolve.models.model_models import ModelRequest, ModelResponse, ModelProviderProfile


class OpenCodeProviderAdapter(BaseModelProviderAdapter):

    def is_available(self, context: dict) -> bool:
        return False

    def run_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        return make_blocked_response(request, "OpenCode provider adapter is a stub - blocked by default")

    def run_json_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        return make_blocked_response(request, "OpenCode provider adapter is a stub - blocked by default")
