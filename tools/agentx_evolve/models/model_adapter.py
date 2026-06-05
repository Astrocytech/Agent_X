from __future__ import annotations

from abc import ABC, abstractmethod

from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    ModelProviderProfile,
    ModelPolicyDecision,
    utc_now_iso,
    new_id,
    SOURCE_COMPONENT,
    MODEL_STATUS_BLOCKED,
)
from agentx_evolve.tools.tool_models import COMMAND_NOT_IMPLEMENTED


class BaseModelProviderAdapter(ABC):

    def __init__(self, provider_profile: ModelProviderProfile):
        self.provider_profile = provider_profile

    @abstractmethod
    def is_available(self, context: dict) -> bool:
        ...

    def validate_request(
        self, request: ModelRequest, profile: ModelProviderProfile, context: dict
    ) -> ModelPolicyDecision | None:
        return None

    @abstractmethod
    def run_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        ...

    @abstractmethod
    def run_json_prompt(self, request: ModelRequest, profile: ModelProviderProfile, context: dict) -> ModelResponse:
        ...


def make_blocked_response(request: ModelRequest, reason: str, failure_class: str = COMMAND_NOT_IMPLEMENTED) -> ModelResponse:
    now = utc_now_iso()
    return ModelResponse(
        model_response_id=new_id("res"),
        model_request_id=request.model_request_id,
        timestamp=now,
        source_component=SOURCE_COMPONENT,
        model_id=request.model_id,
        provider_id=request.provider_id,
        status=MODEL_STATUS_BLOCKED,
        message=reason,
        failure_class=failure_class,
    )
