from __future__ import annotations
from typing import Any

from agentx_evolve.context.context_models import (
    TaskPack, ContextPack, ContextItem, ContextSource,
    TP_READY, TP_DRAFT, TP_BLOCKED, TP_INVALID,
    COMPATIBLE, INCOMPATIBLE_OVER_CONTEXT_WINDOW, INCOMPATIBLE_MODEL_POLICY,
)


def validate_task_pack(task_pack: TaskPack, validation_context: dict | None = None) -> dict:
    if validation_context is None:
        validation_context = {}

    errors: list[str] = list(task_pack.errors)
    warnings: list[str] = list(task_pack.warnings)

    status = TP_READY

    schema_valid = _check_schema(task_pack)
    if not schema_valid:
        errors.append("schema validation failed")
        status = TP_INVALID

    if task_pack.task_input is None:
        errors.append("missing task_input")
        status = TP_INVALID
    elif task_pack.task_input.errors:
        errors.extend(task_pack.task_input.errors)
        status = TP_INVALID

    budget_valid = True
    if task_pack.context_pack is not None:
        cp = task_pack.context_pack
        if cp.total_estimated_tokens > cp.max_context_tokens > 0:
            if any("incompatible" in e for e in cp.errors):
                budget_valid = False
            else:
                budget_valid = False
            if status == TP_READY:
                status = TP_BLOCKED

    model_compatible = True
    tool_compatible = True
    injection_risk_accepted = True
    redaction_complete = True
    evidence_refs_present = len(task_pack.evidence_refs) > 0

    for err in errors:
        if "model" in err.lower():
            model_compatible = False
        if "tool" in err.lower():
            tool_compatible = False
        if "injection" in err.lower():
            injection_risk_accepted = False
        if "redact" in err.lower():
            redaction_complete = False

    if task_pack.context_pack and task_pack.context_pack.errors:
        for e in task_pack.context_pack.errors:
            if "injection" in e.lower():
                injection_risk_accepted = False
                if status == TP_READY:
                    status = TP_BLOCKED
            if "redact" in e.lower():
                redaction_complete = False
                if status == TP_READY:
                    status = TP_BLOCKED

    if not model_compatible or not tool_compatible:
        if status == TP_READY:
            status = TP_BLOCKED

    result = {
        "status": status,
        "schema_valid": schema_valid,
        "budget_valid": budget_valid,
        "model_compatible": model_compatible,
        "tool_compatible": tool_compatible,
        "prompt_contract_compatible": validation_context.get("prompt_contract_id") is not None,
        "injection_risk_accepted": injection_risk_accepted,
        "redaction_complete": redaction_complete,
        "evidence_refs_present": evidence_refs_present,
        "errors": errors,
        "warnings": warnings,
    }
    return result


def validate_context_pack(context_pack: ContextPack, validation_context: dict | None = None) -> dict:
    if validation_context is None:
        validation_context = {}

    errors: list[str] = list(context_pack.errors)
    warnings: list[str] = list(context_pack.warnings)

    if context_pack.total_estimated_tokens > context_pack.max_context_tokens > 0:
        errors.append("context pack exceeds max_context_tokens")

    if not context_pack.included_items and not errors:
        warnings.append("context pack has no included items")

    return {
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "warnings": warnings,
        "item_count": len(context_pack.included_items),
        "total_tokens": context_pack.total_estimated_tokens,
        "within_budget": context_pack.total_estimated_tokens <= context_pack.max_context_tokens,
    }


def _check_schema(task_pack: TaskPack) -> bool:
    if not task_pack.task_pack_id:
        return False
    if not task_pack.created_at:
        return False
    if task_pack.status not in ("DRAFT", "READY", "BLOCKED", "INVALID"):
        return False
    return True
