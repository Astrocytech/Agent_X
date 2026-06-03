from __future__ import annotations

import logging

from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    ModelProviderProfile,
    ModelPolicyDecision,
    PROVIDER_LOCAL,
    MODEL_STATUS_SUCCESS,
    MODEL_STATUS_BLOCKED,
    utc_now_iso,
    new_id,
    SOURCE_COMPONENT,
)
from agentx_evolve.models.model_adapter import BaseModelProviderAdapter, make_blocked_response

logger = logging.getLogger(__name__)


class LocalModelAdapter(BaseModelProviderAdapter):
    def __init__(self, provider_profile: ModelProviderProfile | None = None):
        if provider_profile is None:
            provider_profile = ModelProviderProfile(
                provider_id="local-default",
                provider_kind=PROVIDER_LOCAL,
                model_ids=[],
            )
        super().__init__(provider_profile)

    def is_available(self, context: dict) -> bool:
        return False

    def validate_request(
        self, request: ModelRequest, profile: ModelProviderProfile, context: dict
    ) -> ModelPolicyDecision | None:
        return None

    def run_prompt(
        self, request: ModelRequest, profile: ModelProviderProfile, context: dict
    ) -> ModelResponse:
        return make_blocked_response(request, "Local provider not available in this context")

    def run_json_prompt(
        self, request: ModelRequest, profile: ModelProviderProfile, context: dict
    ) -> ModelResponse:
        return make_blocked_response(request, "Local provider not available in this context")
