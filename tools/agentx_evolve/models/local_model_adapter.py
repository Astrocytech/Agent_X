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
from agentx_evolve.models.model_adapter import BaseModelProviderAdapter
from agentx_evolve.models.local_provider_adapter import LocalProviderAdapter

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
        self._inner = LocalProviderAdapter(provider_profile)

    def is_available(self, context: dict) -> bool:
        return self._inner.is_available(context)

    def validate_request(
        self, request: ModelRequest, profile: ModelProviderProfile, context: dict
    ) -> ModelPolicyDecision | None:
        return self._inner.validate_request(request, profile, context)

    def run_prompt(
        self, request: ModelRequest, profile: ModelProviderProfile, context: dict
    ) -> ModelResponse:
        return self._inner.run_prompt(request, profile, context)

    def run_json_prompt(
        self, request: ModelRequest, profile: ModelProviderProfile, context: dict
    ) -> ModelResponse:
        return self._inner.run_json_prompt(request, profile, context)
