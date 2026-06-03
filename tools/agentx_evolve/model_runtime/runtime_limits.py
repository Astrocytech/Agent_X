from __future__ import annotations

from agentx_evolve.models.model_models import ModelRequest, ModelProfile
from agentx_evolve.model_runtime.runtime_models import RuntimeProfile


def estimate_token_count(text: str) -> int:
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    return max(words, chars // 4)


def check_context_budget(
    request: ModelRequest,
    profile: ModelProfile,
    runtime_profile: RuntimeProfile,
) -> list[str]:
    errors: list[str] = []

    prompt_tokens = estimate_token_count(request.prompt)
    system_tokens = estimate_token_count(request.system_prompt or "")
    total_tokens = prompt_tokens + system_tokens

    model_window = profile.context_window
    runtime_max = runtime_profile.max_total_context_tokens
    effective_max = min(model_window, runtime_max)

    if total_tokens > effective_max:
        errors.append(
            f"Total context {total_tokens} exceeds effective max {effective_max} "
            f"(model window: {model_window}, runtime max: {runtime_max})"
        )

    if request.max_output_tokens > profile.max_output_tokens:
        errors.append(
            f"Requested output tokens {request.max_output_tokens} exceeds "
            f"model max {profile.max_output_tokens}"
        )

    return errors


def truncate_for_evidence(text: str, max_chars: int = 2000) -> str:
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"... (truncated, {len(text)} total chars)"
