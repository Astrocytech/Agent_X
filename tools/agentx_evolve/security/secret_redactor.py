from __future__ import annotations
import re
from agentx_evolve.security.security_models import (
    SandboxPolicy, SecretRedactionResult,
    utc_now_iso, new_id,
)

_KNOWN_SECRET_NAMES = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GITHUB_TOKEN",
    "GITLAB_TOKEN",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_ACCESS_KEY_ID",
    "API_KEY",
    "TOKEN",
    "SECRET",
]


_OPTIONAL_QUOTE = "[\"'']?"


def _build_patterns() -> list[tuple[str, re.Pattern]]:
    patterns: list[tuple[str, re.Pattern]] = []

    for name in _KNOWN_SECRET_NAMES:
        raw = (
            rf"(?:{re.escape(name)}\s*[=:]\s*{_OPTIONAL_QUOTE})"
            rf"([A-Za-z0-9_\-\.]{{8,}})"
            rf"{_OPTIONAL_QUOTE}"
        )
        patterns.append(
            (name, re.compile(raw, re.IGNORECASE))
        )

    generic_token = re.compile(
        r"(?<![A-Za-z0-9])(sk-[A-Za-z0-9]{20,}|[A-Za-z0-9_\-\.]{40,})(?![A-Za-z0-9])"
    )
    patterns.append(("GENERIC_LONG_TOKEN", generic_token))

    return patterns


_DEFAULT_PATTERNS = _build_patterns()


def redact_secrets(text: str, policy: SandboxPolicy | None = None) -> SecretRedactionResult:
    if not text:
        return SecretRedactionResult(
            result_id=new_id("srr"),
            timestamp=utc_now_iso(),
            status="SUCCESS",
            redacted_text=text,
            redaction_count=0,
            redaction_types=[],
        )

    redacted = text
    redaction_count = 0
    redaction_types: list[str] = []

    for type_name, pattern in _DEFAULT_PATTERNS:
        new_text, count = pattern.subn(_redact_replacement(type_name), redacted)
        if count > 0:
            redacted = new_text
            redaction_count += count
            redaction_types.append(type_name)

    custom_patterns: list[str] = policy.redact_secret_patterns if policy else []
    for pattern_str in custom_patterns:
        if not pattern_str:
            continue
        try:
            pattern = re.compile(pattern_str)
            new_text, count = pattern.subn("[REDACTED_SECRET]", redacted)
            if count > 0:
                redacted = new_text
                redaction_count += count
                redaction_types.append("CUSTOM_PATTERN")
        except re.error:
            pass

    return SecretRedactionResult(
        result_id=new_id("srr"),
        timestamp=utc_now_iso(),
        status="SUCCESS",
        redacted_text=redacted,
        redaction_count=redaction_count,
        redaction_types=redaction_types,
    )


def _redact_replacement(type_name: str) -> str:
    if "API_KEY" in type_name:
        return f"[REDACTED_API_KEY]"
    if "TOKEN" in type_name:
        return f"[REDACTED_TOKEN]"
    if "SECRET" in type_name:
        return f"[REDACTED_SECRET]"
    return f"[REDACTED_SECRET]"
