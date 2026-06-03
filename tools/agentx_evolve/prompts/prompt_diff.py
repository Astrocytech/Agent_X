from __future__ import annotations

import difflib
from agentx_evolve.prompts.prompt_models import (
    PromptVersion,
    PromptDiffRecord,
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_BREAKING,
    COMPATIBILITY_UNKNOWN,
    sha256_dict,
    utc_now_iso,
    new_id,
)


def _find_sections(text: str) -> dict[str, str]:
    lines = text.split("\n")
    sections: dict[str, str] = {}
    current_name = "__preamble__"
    current_lines: list[str] = []
    for line in lines:
        if line.startswith("# ") or line.startswith("## ") or line.startswith("### "):
            if current_lines:
                sections[current_name] = "\n".join(current_lines)
            current_name = line.strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections[current_name] = "\n".join(current_lines)
    return sections


def create_prompt_diff(
    old_version: PromptVersion, new_version: PromptVersion
) -> PromptDiffRecord:
    old_sections = _find_sections(old_version.prompt_body)
    new_sections = _find_sections(new_version.prompt_body)
    added: list[str] = []
    removed: list[str] = []
    changed: list[str] = []
    all_keys = set(old_sections.keys()) | set(new_sections.keys())
    for key in sorted(all_keys):
        old_val = old_sections.get(key)
        new_val = new_sections.get(key)
        if old_val is None and new_val is not None:
            added.append(key)
        elif old_val is not None and new_val is None:
            removed.append(key)
        elif old_val is not None and new_val is not None and old_val != new_val:
            changed.append(key)
    breaking = bool(
        old_version.breaking_change != new_version.breaking_change
        or "required output" in str(new_version.change_summary).lower()
    )
    compatibility = COMPATIBILITY_BREAKING if (breaking or changed) else COMPATIBILITY_COMPATIBLE
    summary_parts: list[str] = []
    if added:
        summary_parts.append(f"added sections: {', '.join(added)}")
    if removed:
        summary_parts.append(f"removed sections: {', '.join(removed)}")
    if changed:
        summary_parts.append(f"changed sections: {', '.join(changed)}")
    if not summary_parts:
        summary_parts.append("no changes detected")
    summary = "; ".join(summary_parts)
    diff_id = new_id("pd")
    record = PromptDiffRecord(
        diff_id=diff_id,
        from_prompt_version_id=old_version.prompt_version_id,
        to_prompt_version_id=new_version.prompt_version_id,
        created_at=utc_now_iso(),
        summary=summary,
        added_sections=added,
        removed_sections=removed,
        changed_sections=changed,
        compatibility_result=compatibility,
        breaking_reasons=["section content changed"] if changed else [],
    )
    record.diff_sha256 = hash_prompt_diff(record)
    return record


def summarize_prompt_diff(diff_record: PromptDiffRecord) -> str:
    parts: list[str] = [f"Diff: {diff_record.from_prompt_version_id} -> {diff_record.to_prompt_version_id}"]
    parts.append(f"Compatibility: {diff_record.compatibility_result}")
    if diff_record.summary:
        parts.append(f"Summary: {diff_record.summary}")
    if diff_record.breaking_reasons:
        parts.append(f"Breaking reasons: {'; '.join(diff_record.breaking_reasons)}")
    return " | ".join(parts)


def hash_prompt_diff(diff_record: PromptDiffRecord) -> str:
    data = {
        "from": diff_record.from_prompt_version_id,
        "to": diff_record.to_prompt_version_id,
        "summary": diff_record.summary,
        "added": diff_record.added_sections,
        "removed": diff_record.removed_sections,
        "changed": diff_record.changed_sections,
        "compatibility": diff_record.compatibility_result,
    }
    return sha256_dict(data)
