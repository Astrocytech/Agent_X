from __future__ import annotations

import json

from agentx_evolve.models.model_models import (
    ModelResponse,
    ModelRequest,
    utc_now_iso,
    new_id,
    SOURCE_COMPONENT,
    MODEL_STATUS_INVALID,
    MODEL_STATUS_FAILED,
)


def parse_json_output(raw_text: str) -> dict | None:
    if not raw_text:
        return None

    text = raw_text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from code fences
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start) if "```" in text[start:] else len(text)
        try:
            return json.loads(text[start:end].strip())
        except (json.JSONDecodeError, ValueError):
            pass
    elif "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start) if "```" in text[start:] else len(text)
        try:
            return json.loads(text[start:end].strip())
        except (json.JSONDecodeError, ValueError):
            pass

    return None


def validate_json_output(parsed: dict, schema: dict | None = None) -> list[str]:
    errors: list[str] = []

    if parsed is None:
        errors.append("Parsed JSON is None")
        return errors

    if schema is None:
        return errors

    required = schema.get("required", [])
    for field in required:
        if field not in parsed:
            errors.append(f"Missing required field: {field}")

    return errors


def make_invalid_json_response(request: ModelRequest, reason: str) -> ModelResponse:
    now = utc_now_iso()
    return ModelResponse(
        model_response_id=new_id("res"),
        model_request_id=request.model_request_id,
        timestamp=now,
        source_component=SOURCE_COMPONENT,
        model_id=request.model_id,
        provider_id=request.provider_id,
        status=MODEL_STATUS_INVALID,
        message=reason,
        json_valid=False,
        schema_valid=False,
    )
