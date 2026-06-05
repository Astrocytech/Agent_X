from __future__ import annotations

from agentx_evolve.prompts.prompt_models import (
    PromptVersion,
    PromptContract,
    PromptDiffRecord,
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_BREAKING,
    COMPATIBILITY_REQUIRES_MIGRATION,
    COMPATIBILITY_UNKNOWN,
)
from agentx_evolve.prompts.prompt_diff import create_prompt_diff


def check_prompt_compatibility(
    old_version: PromptVersion,
    new_version: PromptVersion,
    contract: PromptContract,
) -> PromptDiffRecord:
    diff = create_prompt_diff(old_version, new_version)
    change_type = classify_prompt_change(diff)
    diff.compatibility_result = change_type
    return diff


def classify_prompt_change(diff_record: PromptDiffRecord) -> str:
    if diff_record.breaking_reasons:
        return COMPATIBILITY_BREAKING
    if diff_record.changed_sections:
        return COMPATIBILITY_REQUIRES_MIGRATION
    if diff_record.added_sections or diff_record.removed_sections:
        return COMPATIBILITY_REQUIRES_MIGRATION
    if diff_record.compatibility_result == COMPATIBILITY_UNKNOWN:
        return COMPATIBILITY_UNKNOWN
    return COMPATIBILITY_COMPATIBLE


def requires_migration(diff_record: PromptDiffRecord) -> bool:
    result = diff_record.compatibility_result
    return result in (
        COMPATIBILITY_BREAKING,
        COMPATIBILITY_REQUIRES_MIGRATION,
        COMPATIBILITY_UNKNOWN,
    )
