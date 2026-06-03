from agentx_evolve.model.prompt_runner import BaseProvider
from agentx_evolve.model.model_models import PromptRequest, ModelResponse, MD_SUCCESS, new_id, utc_now_iso


class OpenCodeProvider(BaseProvider):
    def call(self, request: PromptRequest) -> ModelResponse:
        return self._make_response(
            request, MD_SUCCESS,
            content=f"[opencode:{request.profile_id}] simulated response",
            model_used="opencode-simulated",
            tokens_in=100, tokens_out=50, duration_ms=200.0,
        )


class OllamaProvider(BaseProvider):
    def call(self, request: PromptRequest) -> ModelResponse:
        return self._make_response(
            request, MD_SUCCESS,
            content=f"[ollama:{request.profile_id}] simulated response",
            model_used="ollama-simulated",
            tokens_in=100, tokens_out=50, duration_ms=300.0,
        )


class LMStudioProvider(BaseProvider):
    def call(self, request: PromptRequest) -> ModelResponse:
        return self._make_response(
            request, MD_SUCCESS,
            content=f"[lmstudio:{request.profile_id}] simulated response",
            model_used="lmstudio-simulated",
            tokens_in=100, tokens_out=50, duration_ms=250.0,
        )


class OpenAICompatibleProvider(BaseProvider):
    def call(self, request: PromptRequest) -> ModelResponse:
        return self._make_response(
            request, MD_SUCCESS,
            content=f"[openai-compat:{request.profile_id}] simulated response",
            model_used="openai-compat-simulated",
            tokens_in=100, tokens_out=50, duration_ms=200.0,
        )
