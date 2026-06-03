from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

MP_SMALL_FAST = "small_fast"
MP_SMALL_CODER = "small_coder"
MP_MEDIUM_CODER = "medium_coder_optional"
MP_HOSTED_FALLBACK = "hosted_fallback_optional"
ALL_MODEL_PROFILES = [MP_SMALL_FAST, MP_SMALL_CODER, MP_MEDIUM_CODER, MP_HOSTED_FALLBACK]

MD_SUCCESS = "SUCCESS"
MD_FAILED = "FAILED"
MD_INVALID_OUTPUT = "INVALID_OUTPUT"
MD_INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"
MD_TIMEOUT = "TIMEOUT"
MD_RATE_LIMITED = "RATE_LIMITED"
ALL_MODEL_STATUSES = [MD_SUCCESS, MD_FAILED, MD_INVALID_OUTPUT, MD_INSUFFICIENT_CONTEXT, MD_TIMEOUT, MD_RATE_LIMITED]

TASK_IMPLEMENT_PATCH = "IMPLEMENT_PATCH"
TASK_FIX_VALIDATION = "FIX_VALIDATION"
TASK_WRITE_TEST = "WRITE_TEST"
TASK_EXPLAIN_FAILURE = "EXPLAIN_FAILURE"
TASK_REVIEW_CODE = "REVIEW_CODE"
TASK_GENERATE_PLAN = "GENERATE_PLAN"
ALL_TASK_TYPES = [TASK_IMPLEMENT_PATCH, TASK_FIX_VALIDATION, TASK_WRITE_TEST,
                  TASK_EXPLAIN_FAILURE, TASK_REVIEW_CODE, TASK_GENERATE_PLAN]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    if prefix:
        return f"{prefix}-{uuid4().hex}"
    return uuid4().hex


def to_dict(obj: object) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if isinstance(val, list):
                result[f] = [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in val]
            elif isinstance(val, dict):
                result[f] = {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in val.items()}
            else:
                result[f] = val
        return result
    if isinstance(obj, dict):
        return {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in obj]
    return obj


@dataclass
class ModelProfile:
    profile_id: str = MP_SMALL_FAST
    name: str = "Small Fast"
    description: str = "Small fast model for simple tasks"
    provider: str = "local"
    model_name: str = ""
    max_tokens: int = 4096
    temperature: float = 0.2
    timeout_seconds: int = 60
    retry_limit: int = 2
    supports_json_mode: bool = True
    token_budget: int = 8192
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class PromptRequest:
    request_id: str = ""
    timestamp: str = ""
    task_type: str = TASK_IMPLEMENT_PATCH
    system_prompt: str = ""
    user_prompt: str = ""
    profile_id: str = MP_SMALL_FAST
    json_mode: bool = False
    expected_schema: dict | None = None
    token_budget: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ModelResponse:
    response_id: str = ""
    timestamp: str = ""
    request_id: str = ""
    status: str = MD_SUCCESS
    content: str = ""
    json_data: dict | None = None
    model_used: str = ""
    profile_id: str = ""
    prompt_hash: str = ""
    output_hash: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    duration_ms: float = 0.0
    retry_attempts: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ModelProviderConfig:
    provider_id: str = ""
    provider_type: str = ""
    api_base: str = ""
    api_key_env: str = ""
    default_model: str = ""
    timeout_seconds: int = 60
    max_retries: int = 2
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)
