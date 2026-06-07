from __future__ import annotations

import logging
from typing import Any

from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    ModelProviderProfile,
    ModelPolicyDecision,
    PROVIDER_LOCAL,
    MODEL_STATUS_SUCCESS,
    MODEL_STATUS_BLOCKED,
    MODEL_STATUS_FAILED,
    MODEL_NOT_FOUND,
    utc_now_iso,
    new_id,
    SOURCE_COMPONENT,
)
from agentx_evolve.models.model_adapter import BaseModelProviderAdapter, make_blocked_response

logger = logging.getLogger(__name__)


class LocalProviderAdapter(BaseModelProviderAdapter):
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
