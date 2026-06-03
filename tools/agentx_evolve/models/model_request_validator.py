from __future__ import annotations

from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelRegistry,
    ModelResponse,
    utc_now_iso,
    new_id,
    SOURCE_COMPONENT,
    MODEL_STATUS_INVALID,
    ALL_TASK_TYPES,
    ALL_ROLES,
)


def validate_model_request(request: ModelRequest, registry: ModelRegistry) -> list[str]:
    errors: list[str] = []

    if not request.model_request_id:
        errors.append("Missing model_request_id")

    if not request.timestamp:
        errors.append("Missing timestamp")

    if request.task_type not in ALL_TASK_TYPES:
        errors.append(f"Unknown task_type: {request.task_type}")

    if request.caller_role not in ALL_ROLES:
        errors.append(f"Unknown caller_role: {request.caller_role}")

    if not request.model_id:
        errors.append("Missing model_id")

    if not request.provider_id:
        errors.append("Missing provider_id")

    if not request.prompt:
        errors.append("Missing prompt")

    # Check model exists in registry
    model_found = False
    for m in registry.models:
        if m.model_id == request.model_id:
            model_found = True
            break
    if not model_found:
        errors.append(f"Model '{request.model_id}' not found in registry")

    # Check provider exists in registry
    provider_found = False
    for p in registry.provider_profiles:
        if p.provider_id == request.provider_id:
            provider_found = True
            break
    if not provider_found:
        errors.append(f"Provider '{request.provider_id}' not found in registry")

    return errors
