from __future__ import annotations
import warnings
from dataclasses import dataclass, field
from typing import Any

try:
    from agentx_evolve.prompts.prompt_runtime_binding import (
        bind_prompt_for_runtime as _bind_prompt_for_runtime,
        resolve_prompt_body as _resolve_prompt_body,
    )

    warnings.warn(
        "prompt_runtime_binding is deprecated; use prompt_binding.PromptBinding",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    pass

__all__ = [
    "PromptBinding",
    "bind_prompt",
    "resolve_binding",
]


@dataclass
class PromptBinding:
    binding_id: str = ""
    prompt_id: str = ""
    context_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)


def bind_prompt(prompt: dict[str, Any], context: dict[str, Any]) -> PromptBinding:
    from agentx_evolve.prompts.prompt_models import new_id
    return PromptBinding(
        binding_id=new_id("pb"),
        prompt_id=prompt.get("prompt_id", ""),
        context_schema=dict(context),
    )


def resolve_binding(binding: PromptBinding) -> dict[str, Any]:
    return {
        "binding_id": binding.binding_id,
        "prompt_id": binding.prompt_id,
        "resolved": True,
    }
