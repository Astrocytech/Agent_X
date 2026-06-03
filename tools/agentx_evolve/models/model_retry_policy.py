from __future__ import annotations

from agentx_evolve.models.model_models import (
    ModelResponse,
    ModelRequest,
    ModelRetryRecord,
    utc_now_iso,
    new_id,
    SOURCE_COMPONENT,
    MODEL_STATUS_INVALID,
    MODEL_STATUS_RETRYABLE,
)


DEFAULT_MAX_RETRIES = 1


def should_retry_model_response(
    response: ModelResponse,
    request: ModelRequest,
    attempt_number: int,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> bool:
    if attempt_number >= max_retries:
        return False

    if response.status == MODEL_STATUS_INVALID:
        return False

    if not response.json_valid:
        return True

    if not response.schema_valid:
        return True

    return False


def make_retry_record(
    request: ModelRequest,
    response: ModelResponse,
    attempt_number: int,
) -> ModelRetryRecord:
    now = utc_now_iso()

    reason = "unknown"
    if not response.json_valid:
        reason = "MODEL_INVALID_JSON"
    elif not response.schema_valid:
        reason = "MODEL_SCHEMA_VALIDATION_FAILED"

    decision = "RETRY"
    if attempt_number >= DEFAULT_MAX_RETRIES:
        decision = "BLOCK"

    return ModelRetryRecord(
        retry_id=new_id("ret"),
        original_request_id=request.original_request_id or request.model_request_id,
        model_request_id=request.model_request_id,
        model_response_id=response.model_response_id,
        timestamp=now,
        source_component=SOURCE_COMPONENT,
        attempt_number=attempt_number,
        retry_reason=reason,
        decision=decision,
    )
