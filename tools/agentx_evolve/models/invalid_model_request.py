from __future__ import annotations

from agentx_evolve.models.model_models import (
    ModelRequest,
    ModelResponse,
    InvalidModelRequestRecord,
    utc_now_iso,
    new_id,
    SOURCE_COMPONENT,
    MODEL_STATUS_INVALID,
    MODEL_REQUEST_INVALID,
    UNKNOWN_MODEL_FAILURE,
)


def handle_invalid_model_request(raw_request: ModelRequest | None, reason: str) -> ModelResponse:
    now = utc_now_iso()

    model_id = "unknown"
    req_id = None
    if raw_request is not None:
        model_id = raw_request.model_id or "unknown"
        req_id = raw_request.model_request_id

    failure_class = MODEL_REQUEST_INVALID if raw_request is not None else UNKNOWN_MODEL_FAILURE

    return ModelResponse(
        model_response_id=new_id("res"),
        model_request_id=req_id or new_id("unk"),
        timestamp=now,
        source_component=SOURCE_COMPONENT,
        model_id=model_id,
        provider_id="unknown",
        status=MODEL_STATUS_INVALID,
        message=f"Invalid model request: {reason}",
        failure_class=failure_class,
    )
