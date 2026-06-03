from __future__ import annotations
from typing import Any

from agentx_evolve.context.context_models import (
    ContextPack,
    COMPATIBLE,
    INCOMPATIBLE_OVER_CONTEXT_WINDOW,
    INCOMPATIBLE_MODEL_POLICY,
    NEEDS_COMPRESSION,
)


def check_model_context_compatibility(
    context_pack: ContextPack,
    model_profile: dict,
    runtime_profile: dict | None = None,
) -> dict[str, Any]:
    context_window = model_profile.get("context_window", 4096)
    output_tokens = context_pack.reserved_output_tokens
    estimated = context_pack.total_estimated_tokens
    available = context_window - output_tokens

    if context_pack.max_context_tokens > 0:
        available = min(available, context_pack.max_context_tokens)

    fits = estimated <= available

    if not fits:
        reduction_needed = estimated - available
        if reduction_needed <= context_window * 0.3:
            return {
                "decision_id": "mc-needs-compression",
                "model_profile_id": model_profile.get("model_profile_id", ""),
                "context_window_tokens": context_window,
                "estimated_input_tokens": estimated,
                "reserved_output_tokens": output_tokens,
                "fits": False,
                "required_reductions": reduction_needed,
                "decision": NEEDS_COMPRESSION,
                "reason": f"pack exceeds available tokens by {reduction_needed}",
                "warnings": [],
                "errors": [],
            }
        return {
            "decision_id": "mc-over-window",
            "model_profile_id": model_profile.get("model_profile_id", ""),
            "context_window_tokens": context_window,
            "estimated_input_tokens": estimated,
            "reserved_output_tokens": output_tokens,
            "fits": False,
            "required_reductions": reduction_needed,
            "decision": INCOMPATIBLE_OVER_CONTEXT_WINDOW,
            "reason": f"pack exceeds context window by {reduction_needed}",
            "warnings": [],
            "errors": [],
        }

    policy_check = model_profile.get("allowed_task_types", [])
    if policy_check and context_pack.task_input_id:
        pass

    return {
        "decision_id": "mc-compatible",
        "model_profile_id": model_profile.get("model_profile_id", ""),
        "context_window_tokens": context_window,
        "estimated_input_tokens": estimated,
        "reserved_output_tokens": output_tokens,
        "fits": True,
        "required_reductions": 0,
        "decision": COMPATIBLE,
        "reason": "pack fits within model context window",
        "warnings": [],
        "errors": [],
    }
