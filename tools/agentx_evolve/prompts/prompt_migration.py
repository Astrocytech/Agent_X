from __future__ import annotations

from agentx_evolve.prompts.prompt_models import (
    PromptDiffRecord,
    PromptMigrationRecord,
    MIGRATION_STATUS_REQUIRED,
    MIGRATION_STATUS_IN_PROGRESS,
    MIGRATION_STATUS_COMPLETE,
    MIGRATION_STATUS_BLOCKED,
    utc_now_iso,
    new_id,
)
from agentx_evolve.prompts.prompt_compatibility import requires_migration


def create_prompt_migration_record(
    diff_record: PromptDiffRecord,
    affected_runtime_bindings: list[str],
    approval_context: dict,
) -> PromptMigrationRecord:
    required_actions: list[str] = []
    if diff_record.changed_sections:
        required_actions.append("review changed sections")
    if diff_record.compatibility_result in ("BREAKING", "REQUIRES_MIGRATION"):
        required_actions.append("review compatibility impact")
    governance_required = bool(
        diff_record.compatibility_result == "BREAKING"
        or approval_context.get("governance_required", False)
    )
    approval_required = bool(
        governance_required or approval_context.get("approval_required", False)
    )
    migration = PromptMigrationRecord(
        migration_id=new_id("pm"),
        from_prompt_version_id=diff_record.from_prompt_version_id,
        to_prompt_version_id=diff_record.to_prompt_version_id,
        created_at=utc_now_iso(),
        migration_status=MIGRATION_STATUS_REQUIRED,
        required_actions=required_actions,
        affected_runtime_bindings=affected_runtime_bindings,
        approval_required=approval_required,
        governance_required=governance_required,
    )
    return migration


def validate_prompt_migration_record(
    migration: PromptMigrationRecord,
) -> list[str]:
    errors = []
    if not migration.migration_id:
        errors.append("migration_id is required")
    if not migration.from_prompt_version_id:
        errors.append("from_prompt_version_id is required")
    if not migration.to_prompt_version_id:
        errors.append("to_prompt_version_id is required")
    if migration.migration_status not in (
        MIGRATION_STATUS_REQUIRED,
        MIGRATION_STATUS_IN_PROGRESS,
        MIGRATION_STATUS_COMPLETE,
        MIGRATION_STATUS_BLOCKED,
    ):
        errors.append(f"invalid migration_status: {migration.migration_status}")
    if migration.migration_status == MIGRATION_STATUS_COMPLETE and not migration.evidence_refs:
        errors.append("cannot mark migration complete without evidence_refs")
    return errors


def mark_prompt_migration_complete(
    migration: PromptMigrationRecord,
    evidence_refs: list[str],
) -> PromptMigrationRecord:
    if not evidence_refs:
        migration.errors.append("cannot mark migration complete without evidence refs")
        return migration
    migration.migration_status = MIGRATION_STATUS_COMPLETE
    migration.evidence_refs = list(evidence_refs)
    return migration
