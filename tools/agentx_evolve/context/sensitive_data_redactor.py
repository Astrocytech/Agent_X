from __future__ import annotations
import re
from typing import Any

from agentx_evolve.context.context_models import ContextItem, REDACT_AND_INCLUDE


SECRET_PATTERNS: list[tuple[str, str]] = [
    ("API_KEY", r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}['\"]?"),
    ("TOKEN", r"(?i)(token|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{16,}['\"]?"),
    ("PASSWORD", r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?[^\s]{8,}['\"]?"),
    ("PRIVATE_KEY", r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"),
    ("AWS_KEY", r"(?i)(AKIA[0-9A-Z]{16})"),
    ("GITHUB_TOKEN", r"(?i)(ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{36,})"),
    ("ENV_SECRET", r"(?i)(secret|SECRET)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}['\"]?"),
    ("SESSION_TOKEN", r"(?i)(session[_-]?id|session_token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}['\"]?"),
]


def redact_sensitive_context_item(item: ContextItem) -> ContextItem:
    new_content = item.content
    redaction_count = 0

    for redact_type, pattern in SECRET_PATTERNS:
        found = re.search(pattern, new_content)
        if found:
            new_content = re.sub(pattern, f"[REDACTED_{redact_type}]", new_content)
            redaction_count += 1

    if redaction_count > 0:
        item.redacted = True
        item.content = new_content
        item.inclusion_decision = REDACT_AND_INCLUDE

    return item


def redact_sensitive_context_items(items: list[ContextItem]) -> dict[str, Any]:
    redacted_items: list[ContextItem] = []
    redaction_records: list[dict] = []

    for item in items:
        before = item.content
        redact_sensitive_context_item(item)
        if item.redacted:
            redacted_items.append(item)
            redaction_records.append({
                "context_item_id": item.context_item_id,
                "redaction_type": "SENSITIVE_DATA",
                "safe_to_include": True,
            })

    return {
        "redacted_items": redacted_items,
        "redaction_records": redaction_records,
        "total_scanned": len(items),
        "total_redacted": len(redacted_items),
    }
