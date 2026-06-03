from __future__ import annotations

import json
import logging
from pathlib import Path

from agentx_evolve.prompts.prompt_models import (
    PromptVersion,
    PromptRuntimeBinding,
    PromptAuditEvent,
    to_dict,
    utc_now_iso,
    new_id,
    P_PROMPT_EVENT_TYPE_VERSION_ACTIVATED,
    P_PROMPT_EVENT_TYPE_BINDING_CREATED,
    P_PROMPT_EVENT_TYPE_SAFETY_CHECK,
)

logger = logging.getLogger(__name__)


def _events_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / ".agentx-init" / "prompts" / "prompt_events.jsonl"


def _append_event(record: dict, repo_root: str | Path) -> None:
    path = _events_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def record_prompt_activation(
    version: PromptVersion,
    success: bool,
    repo_root: str | Path,
    reason: str = "",
) -> PromptAuditEvent:
    event_type = (
        P_PROMPT_EVENT_TYPE_VERSION_ACTIVATED
        if success
        else "ACTIVATION_FAILED"
    )
    record = PromptAuditEvent(
        audit_id=new_id("evt"),
        timestamp=utc_now_iso(),
        source_component="PromptEvidence",
        event_type=event_type,
        prompt_contract_id=version.prompt_contract_id,
        prompt_version_id=version.prompt_version_id,
        status="SUCCESS" if success else "FAILED",
        message=reason or f"version {version.version} activated",
    )
    _append_event(to_dict(record), repo_root)
    logger.info(
        "record_prompt_activation: contract=%s version=%s success=%s",
        version.prompt_contract_id, version.prompt_version_id, success,
    )
    return record


def record_prompt_binding(
    binding: PromptRuntimeBinding,
    success: bool,
    repo_root: str | Path,
    reason: str = "",
) -> PromptAuditEvent:
    event_type = (
        P_PROMPT_EVENT_TYPE_BINDING_CREATED
        if success
        else "BINDING_FAILED"
    )
    record = PromptAuditEvent(
        audit_id=new_id("evt"),
        timestamp=utc_now_iso(),
        source_component="PromptEvidence",
        event_type=event_type,
        prompt_contract_id=binding.prompt_contract_id,
        prompt_version_id=binding.prompt_version_id,
        status="SUCCESS" if success else "FAILED",
        message=reason or f"binding {binding.binding_id} created",
    )
    _append_event(to_dict(record), repo_root)
    logger.info(
        "record_prompt_binding: contract=%s binding=%s success=%s",
        binding.prompt_contract_id, binding.binding_id, success,
    )
    return record


def record_prompt_safety_check(
    contract_id: str,
    version_id: str,
    passed: bool,
    repo_root: str | Path,
    findings: list[str] | None = None,
) -> PromptAuditEvent:
    record = PromptAuditEvent(
        audit_id=new_id("evt"),
        timestamp=utc_now_iso(),
        source_component="PromptEvidence",
        event_type=P_PROMPT_EVENT_TYPE_SAFETY_CHECK,
        prompt_contract_id=contract_id,
        prompt_version_id=version_id,
        status="PASS" if passed else "FAIL",
        message="; ".join(findings) if findings else ("safety check passed" if passed else "safety check failed"),
    )
    _append_event(to_dict(record), repo_root)
    logger.info(
        "record_prompt_safety_check: contract=%s version=%s passed=%s",
        contract_id, version_id, passed,
    )
    return record
