import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import (
    PromptDiffRecord, PromptMigrationRecord,
    COMPATIBILITY_BREAKING, COMPATIBILITY_REQUIRES_MIGRATION,
    MIGRATION_STATUS_REQUIRED, MIGRATION_STATUS_IN_PROGRESS,
    MIGRATION_STATUS_COMPLETE, MIGRATION_STATUS_BLOCKED,
)
from agentx_evolve.prompts.prompt_migration import (
    create_prompt_migration_record, validate_prompt_migration_record,
    mark_prompt_migration_complete,
)


class TestCreatePromptMigrationRecord:
    def test_breaking_change_creates_migration(self):
        diff = PromptDiffRecord(
            diff_id="pd-001",
            from_prompt_version_id="pv-001",
            to_prompt_version_id="pv-002",
            summary="breaking change",
            changed_sections=["## Output"],
            compatibility_result=COMPATIBILITY_BREAKING,
        )
        migration = create_prompt_migration_record(
            diff, ["rb-001"], {"governance_required": True}
        )
        assert migration.migration_id.startswith("pm-")
        assert migration.from_prompt_version_id == "pv-001"
        assert migration.governance_required is True
        assert migration.approval_required is True

    def test_compatible_change_still_creates_record(self):
        diff = PromptDiffRecord(
            diff_id="pd-002",
            from_prompt_version_id="pv-001",
            to_prompt_version_id="pv-002",
            summary="compatible change",
            compatibility_result="COMPATIBLE",
        )
        migration = create_prompt_migration_record(
            diff, [], {}
        )
        assert migration.migration_status == MIGRATION_STATUS_REQUIRED


class TestValidatePromptMigrationRecord:
    def test_valid_migration_passes(self):
        m = PromptMigrationRecord(
            migration_id="pm-001",
            from_prompt_version_id="pv-001",
            to_prompt_version_id="pv-002",
            migration_status=MIGRATION_STATUS_REQUIRED,
            affected_runtime_bindings=["rb-001"],
        )
        errors = validate_prompt_migration_record(m)
        assert errors == []

    def test_missing_migration_id_fails(self):
        m = PromptMigrationRecord(
            from_prompt_version_id="pv-001",
            to_prompt_version_id="pv-002",
            migration_status=MIGRATION_STATUS_REQUIRED,
        )
        errors = validate_prompt_migration_record(m)
        assert any("migration_id" in e for e in errors)

    def test_complete_without_evidence_fails(self):
        m = PromptMigrationRecord(
            migration_id="pm-001",
            from_prompt_version_id="pv-001",
            to_prompt_version_id="pv-002",
            migration_status=MIGRATION_STATUS_COMPLETE,
        )
        errors = validate_prompt_migration_record(m)
        assert any("evidence" in e for e in errors)


class TestMarkMigrationComplete:
    def test_requires_evidence_to_complete(self):
        m = PromptMigrationRecord(
            migration_id="pm-001",
            from_prompt_version_id="pv-001",
            to_prompt_version_id="pv-002",
            migration_status=MIGRATION_STATUS_REQUIRED,
            affected_runtime_bindings=["rb-001"],
        )
        m = mark_prompt_migration_complete(m, ["ev-001"])
        assert m.migration_status == MIGRATION_STATUS_COMPLETE
        assert "ev-001" in m.evidence_refs

    def test_no_evidence_returns_error(self):
        m = PromptMigrationRecord(
            migration_id="pm-001",
            from_prompt_version_id="pv-001",
            to_prompt_version_id="pv-002",
            migration_status=MIGRATION_STATUS_REQUIRED,
            affected_runtime_bindings=["rb-001"],
        )
        m = mark_prompt_migration_complete(m, [])
        assert m.migration_status == MIGRATION_STATUS_REQUIRED
        assert len(m.errors) > 0
