from __future__ import annotations
from typing import Any

from agentx_evolve.runtime.config import RuntimeConfig
from agentx_evolve.providers.mock_provider import MockProvider
from agentx_evolve.providers.opencode_provider import OpenCodeProvider, OpenCodeProviderError


class ProviderRouter:
    def __init__(self, config: RuntimeConfig):
        self.config = config

    def get_provider(self) -> MockProvider | OpenCodeProvider:
        provider_name = self.config.provider

        if provider_name == "mock":
            return MockProvider(model=self.config.model)

        if provider_name == "opencode":
            return OpenCodeProvider(
                base_url=self.config.opencode_base_url,
                api_key=self.config.opencode_api_key,
                model=self._payload_model(self.config.model),
                timeout_seconds=self.config.timeout_seconds,
                session_id=self.config.opencode_session_id,
            )

        raise OpenCodeProviderError(
            f"unknown provider: {provider_name}", exit_code=2, status="BLOCKED",
        )

    @staticmethod
    def _payload_model(model_id: str) -> str:
        if model_id.startswith("opencode/"):
            return model_id.split("/", 1)[1]
        return model_id
