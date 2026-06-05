from __future__ import annotations

from agentx_evolve.models.model_adapter import BaseModelProviderAdapter, make_blocked_response
from agentx_evolve.models.model_models import ModelRequest, ModelResponse, ModelProviderProfile


class LMStudioAdapter(BaseModelProviderAdapter):

    def is_available(self, context: dict) -> bool:
        return context.get("lmstudio_running", False)

    def run_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        return make_blocked_response(request, "LM Studio adapter not connected - requires local LM Studio server")

    def run_json_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        return make_blocked_response(request, "LM Studio adapter not connected - requires local LM Studio server")
