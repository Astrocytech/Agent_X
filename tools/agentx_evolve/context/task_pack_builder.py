from __future__ import annotations
from pathlib import Path
from typing import Any

from agentx_evolve.context.context_models import (
    TaskInput, ContextSource, ContextItem, ContextPack, TaskPack,
    new_id, utc_now_iso, stable_hash,
    INCLUDE,
    NEEDS_COMPRESSION, COMPATIBLE,
    INCOMPATIBLE_OVER_CONTEXT_WINDOW, INCOMPATIBLE_MODEL_POLICY,
)
from agentx_evolve.context.task_input_normalizer import normalize_task_input
from agentx_evolve.context.context_source_loader import load_context_sources
from agentx_evolve.context.prompt_injection_filter import filter_prompt_injection_items
from agentx_evolve.context.sensitive_data_redactor import redact_sensitive_context_items
from agentx_evolve.context.priority_scorer import score_priority_batch
from agentx_evolve.context.recency_scorer import score_recency_batch
from agentx_evolve.context.deduplication_engine import deduplicate_context_items
from agentx_evolve.context.budget_estimator import estimate_context_item_budget, estimate_context_pack_budget
from agentx_evolve.context.compression_planner import plan_context_compression
from agentx_evolve.context.summary_selector import select_summary_items
from agentx_evolve.context.model_context_compatibility import check_model_context_compatibility
from agentx_evolve.context.tool_context_compatibility import check_tool_context_compatibility


VALID_INCLUSIONS = {
    INCLUDE,
    "REDACT_AND_INCLUDE",
    "SUMMARIZE",
}


def build_context_items_from_sources(
    sources: list[ContextSource],
    source_payloads: dict | None = None,
    task_input: TaskInput | None = None,
    builder_context: dict | None = None,
) -> list[ContextItem]:
    return _sources_to_items(sources)


def build_task_pack(
    raw_task: dict,
    source_requests: list[dict],
    builder_context: dict | None = None,
    repo_root: Path | None = None,
) -> TaskPack:
    if builder_context is None:
        builder_context = {}

    policy_context = builder_context.get("policy_context", {})
    model_profile = builder_context.get("model_profile", {})
    runtime_profile = builder_context.get("runtime_profile")
    tool_registry = builder_context.get("tool_registry", {})
    max_context_tokens = builder_context.get("max_context_tokens", model_profile.get("context_window", 4096))
    reserved_output_tokens = builder_context.get("reserved_output_tokens", 1024)

    # 1-2. Normalize task
    task_input = normalize_task_input(raw_task)
    if task_input.errors:
        return _error_task_pack(task_input, "task normalization failed")

    # 3-4. Load context sources
    sources = load_context_sources(source_requests, policy_context, repo_root)

    # 5-6. Convert sources to items
    context_items = _sources_to_items(sources)

    # 7. Filter prompt injection
    injection_result = filter_prompt_injection_items(context_items)
    context_items = injection_result["filtered_items"]

    # 8. Redact sensitive data
    redaction_result = redact_sensitive_context_items(context_items)

    # 9-10. Score priority and recency
    context_items = score_priority_batch(context_items, task_input)
    context_items = score_recency_batch(context_items)

    # 11. Deduplicate
    dedup_result = deduplicate_context_items(context_items)
    context_items = dedup_result["unique_items"]

    # 12-13. Estimate budget
    for it in context_items:
        estimate_context_item_budget(it)
    budget = estimate_context_pack_budget(context_items, max_context_tokens, reserved_output_tokens)

    # 14-15. Plan compression and select summaries
    compression_plan = plan_context_compression(context_items, budget)
    summaries = []
    if compression_plan["needs_compression"]:
        summaries = select_summary_items(context_items, compression_plan)
        context_items = [it for it in context_items if it.context_item_id not in compression_plan.get("summary_item_ids", [])]
        context_items.extend(summaries)

    # 16. Check model compatibility
    included = [it for it in context_items if it.inclusion_decision in VALID_INCLUSIONS or it in summaries]
    excluded = [it for it in context_items if it not in included]

    pack_id = new_id("cp")
    context_pack = ContextPack(
        context_pack_id=pack_id,
        created_at=utc_now_iso(),
        task_input_id=task_input.task_input_id,
        model_profile_id=model_profile.get("model_profile_id"),
        runtime_profile_id=runtime_profile.get("runtime_profile_id") if runtime_profile else None,
        max_context_tokens=max_context_tokens,
        reserved_output_tokens=reserved_output_tokens,
        available_input_tokens=budget["available_input_tokens"],
        total_estimated_tokens=budget["total_estimated_tokens"],
        included_items=included,
        excluded_items=excluded,
        summary_items=summaries,
    )

    model_compat = check_model_context_compatibility(context_pack, model_profile, runtime_profile)
    tool_compat = check_tool_context_compatibility(task_input, context_pack, tool_registry, policy_context)

    if model_compat["decision"] in (INCOMPATIBLE_OVER_CONTEXT_WINDOW, INCOMPATIBLE_MODEL_POLICY):
        context_pack.errors.append(f"model incompatible: {model_compat['reason']}")

    context_pack.warnings.extend(
        f"prompt injection excluded: {e.context_item_id}"
        for e in injection_result.get("excluded_items", [])
    )

    task_pack = TaskPack(
        task_pack_id=new_id("tp"),
        created_at=utc_now_iso(),
        task_input=task_input,
        context_pack=context_pack,
        model_profile_id=model_profile.get("model_profile_id"),
        runtime_profile_id=runtime_profile.get("runtime_profile_id") if runtime_profile else None,
        allowed_tools=tool_compat.get("allowed_tools", []),
        blocked_tools=tool_compat.get("blocked_tools", []),
        required_outputs=task_input.required_outputs,
        forbidden_actions=task_input.forbidden_actions,
        evidence_refs=[f"src:{s.source_id}" for s in sources],
    )

    return task_pack


def _sources_to_items(sources: list[ContextSource]) -> list[ContextItem]:
    items: list[ContextItem] = []
    for src in sources:
        if src.source_trust_level == "SOURCE_TRUST_BLOCKED":
            continue
        item = ContextItem(
            context_item_id=new_id("ci"),
            created_at=utc_now_iso(),
            source_id=src.source_id,
            source_component=src.source_component,
            source_trust_level=src.source_trust_level,
            item_kind="FILE_SNIPPET",
            title=f"Source: {src.source_type}",
            content=src.source_path or src.source_id,
            content_hash=stable_hash(src.source_path or src.source_id),
            evidence_refs=src.evidence_refs,
            dedupe_key=src.source_id,
        )
        items.append(item)
    return items


def _error_task_pack(task_input: TaskInput, reason: str) -> TaskPack:
    return TaskPack(
        task_pack_id=new_id("tp-error"),
        created_at=utc_now_iso(),
        task_input=task_input,
        errors=[reason],
    )


# ---------------------------------------------------------------------------
# Schema injection (absorbed from schema_injector.py)
# ---------------------------------------------------------------------------


def inject_schema(task_type: str, schemas: dict[str, Any] | None = None) -> dict | None:
    if schemas is None:
        return None
    return schemas.get(task_type)


def list_available_schemas(schemas: dict[str, Any]) -> list[str]:
    return list(schemas.keys())
