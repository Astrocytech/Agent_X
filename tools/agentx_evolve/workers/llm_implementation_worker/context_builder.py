from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerContextPackage,
    utc_now_iso,
    new_id,
    sha256_dict,
    redact_secret_like,
)


SECRET_PATTERNS = [
    "api_key", "apikey", "api-key", "api.key",
    "token", "secret", "password", "credential",
    "private_key", "private-key", "private.key",
    "-----begin", "-----end",
    "sk-", "pk-",
]


def build_context_package(
    task: LLMWorkerTask,
    context_sources: dict,
    policy_context: dict,
    repo_root: Path,
) -> LLMWorkerContextPackage:
    pkg = LLMWorkerContextPackage(
        context_package_id=new_id("cp"),
        created_at=utc_now_iso(),
        task_id=task.task_id,
    )

    allowed_dirs = policy_context.get("allowed_source_dirs", [])
    blocked_dirs = policy_context.get("blocked_source_dirs", [])

    included: list[str] = []
    excluded: list[str] = []
    chunks: list[dict] = []

    for source_name, source_data in context_sources.items():
        source_path = source_data.get("path", "")
        content = source_data.get("content", "")

        if _is_blocked(source_path, allowed_dirs, blocked_dirs):
            excluded.append(source_path)
            continue

        included.append(source_path)
        chunk = {
            "source": source_name,
            "path": source_path,
            "content": content,
        }
        chunks.append(chunk)

    pkg.included_files = included
    pkg.excluded_files = excluded
    pkg.context_chunks = chunks
    pkg.context_summary = f"{len(included)} context files included, {len(excluded)} excluded"

    pkg = redact_context_secrets(pkg)
    pkg = enforce_context_budget(pkg, task.max_context_chars)
    pkg = detect_prompt_injection(pkg)

    hash_data = {
        "included_files": sorted(pkg.included_files),
        "excluded_files": sorted(pkg.excluded_files),
        "context_chunks": [
            {"source": c.get("source", ""), "path": c.get("path", ""), "content": c.get("content", "")}
            for c in pkg.context_chunks
        ],
        "redaction_report": pkg.redaction_report,
        "truncation_report": pkg.truncation_report,
        "prompt_injection_report": pkg.prompt_injection_report,
    }
    pkg.context_hash = sha256_dict(hash_data)

    return pkg


def _is_blocked(path: str, allowed_dirs: list[str], blocked_dirs: list[str]) -> bool:
    for blocked in blocked_dirs:
        if path.startswith(blocked):
            return True
    if not allowed_dirs:
        return False
    for allowed in allowed_dirs:
        if path.startswith(allowed):
            return False
    return True


def sanitize_context_chunk(chunk: dict) -> dict:
    sanitized = dict(chunk)
    content = sanitized.get("content", "")
    if isinstance(content, str):
        sanitized["content"] = content[:10000] if len(content) > 10000 else content
    return sanitized


def redact_context_secrets(
    context_package: LLMWorkerContextPackage,
) -> LLMWorkerContextPackage:
    redaction_count = 0
    redacted_chunks = []

    for chunk in context_package.context_chunks:
        content = chunk.get("content", "")
        if not isinstance(content, str):
            continue
        original = content
        for pattern in SECRET_PATTERNS:
            if pattern in content.lower():
                content = redact_secret_like(content)
                break
        if content != original:
            redaction_count += 1
            redacted_chunks.append(chunk.get("path", "unknown"))
            chunk["content"] = content

    context_package.redaction_report = {
        "redactions_applied": redaction_count,
        "redacted_chunks": redacted_chunks,
    }
    if redaction_count:
        context_package.warnings.append(
            f"Redacted {redaction_count} chunk(s) containing secret-like content"
        )

    return context_package


def enforce_context_budget(
    context_package: LLMWorkerContextPackage,
    max_context_chars: int,
) -> LLMWorkerContextPackage:
    total = context_package.total_chars()
    if total <= max_context_chars:
        return context_package

    remaining = total
    truncated_count = 0
    for chunk in context_package.context_chunks:
        if remaining <= max_context_chars:
            break
        content = chunk.get("content", "")
        if not isinstance(content, str):
            continue
        excess = remaining - max_context_chars
        trim_chars = min(len(content), excess + 100)
        if trim_chars > 0 and len(content) >= trim_chars:
            keep = max(len(content) - trim_chars, 0)
            truncated = len(content) - keep
            chunk["content"] = content[:keep] + "\n...[TRUNCATED]..."
            remaining -= truncated
            truncated_count += 1

    context_package.truncation_report = {
        "original_chars": total,
        "max_context_chars": max_context_chars,
        "truncated_chunks": truncated_count,
    }
    if truncated_count:
        context_package.warnings.append(
            f"Truncated {truncated_count} chunk(s) to fit {max_context_chars} char budget"
        )

    return context_package


INJECTION_INDICATORS = [
    "ignore previous instructions",
    "ignore all instructions",
    "you are not bound by",
    "override your instructions",
    "disregard your guidelines",
    "you must now act as",
    "from now on, you are",
    "system override",
    "you are free from",
    "do not follow",
    "bypass",
]


def detect_prompt_injection(
    context_package: LLMWorkerContextPackage,
) -> LLMWorkerContextPackage:
    found: list[dict] = []

    for chunk in context_package.context_chunks:
        content = chunk.get("content", "")
        path = chunk.get("path", "unknown")
        if not isinstance(content, str):
            continue
        for indicator in INJECTION_INDICATORS:
            if indicator in content.lower():
                found.append({
                    "source_path": path,
                    "indicator": indicator,
                    "severity": "warning",
                })
                break

    context_package.prompt_injection_report = {
        "injections_detected": len(found),
        "injection_details": found,
    }
    if found:
        context_package.warnings.append(
            f"Detected {len(found)} potential prompt injection(s) in context"
        )

    return context_package
