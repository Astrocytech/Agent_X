from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_SENSITIVE_PATTERNS: list[str] = [
    r"sk-[a-zA-Z0-9]{20,}",
    r"ghp_[a-zA-Z0-9]{36}",
    r"gho_[a-zA-Z0-9]{36}",
    r"AKIA[0-9A-Z]{16}",
    r"api_key['\"]?\s*[:=]\s*['\"][^'\"]+['\"]",
    r"password['\"]?\s*[:=]\s*['\"][^'\"]+['\"]",
    r"secret['\"]?\s*[:=]\s*['\"][^'\"]+['\"]",
    r"token['\"]?\s*[:=]\s*['\"][^'\"]+['\"]",
    r"private_key['\"]?\s*[:=]\s*['\"][^'\"]+['\"]",
]

SENSITIVE_KEYS: set[str] = {
    "api_key", "api-key", "API_KEY", "apikey",
    "password", "passwd", "secret", "token",
    "private_key", "private-key", "access_key",
    "access_token", "auth_token", "session_key",
}


def redact_text(text: str, patterns: list[str] | None = None) -> str:
    if not text:
        return text
    if patterns is None:
        patterns = DEFAULT_SENSITIVE_PATTERNS
    redacted = text
    for pattern in patterns:
        redacted = re.sub(pattern, "***REDACTED***", redacted)
    return redacted


def redact_dict(data: dict, keys_to_redact: set[str] | None = None) -> dict:
    if keys_to_redact is None:
        keys_to_redact = SENSITIVE_KEYS
    result: dict = {}
    for k, v in data.items():
        if k.lower() in keys_to_redact:
            result[k] = "***REDACTED***"
        elif isinstance(v, dict):
            result[k] = redact_dict(v, keys_to_redact)
        elif isinstance(v, list):
            result[k] = [
                redact_dict(item, keys_to_redact) if isinstance(item, dict)
                else redact_text(str(item)) if isinstance(item, str)
                else item
                for item in v
            ]
        elif isinstance(v, str):
            result[k] = redact_text(v)
        else:
            result[k] = v
    return result


def redact_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        return redact_dict(payload)
    if isinstance(payload, str):
        return redact_text(payload)
    return payload
