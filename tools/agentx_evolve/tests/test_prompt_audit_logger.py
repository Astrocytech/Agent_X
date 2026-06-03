import pytest
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import (
    PromptAuditEvent, PromptRegistry, PromptRuntimeBinding,
    PromptDiffRecord, PromptMigrationRecord, PROMPT_DECISION_ALLOW,
    COMPATIBILITY_COMPATIBLE,
)
from agentx_evolve.prompts.prompt_audit_logger import (
    append_prompt_audit_event, append_prompt_registry_event,
    append_prompt_version_event, append_prompt_binding_event,
    append_prompt_diff_event, append_prompt_migration_event,
    append_prompt_safety_event, write_latest_prompt_binding,
    write_prompt_evidence_manifest, write_prompt_completion_record,
)


class TestPromptAuditLogger:
    def test_audit_history_written(self, tmp_path):
        event = PromptAuditEvent(
            audit_id="pa-001", event_type="TEST", status="SUCCESS",
            message="test event",
        )
        result = append_prompt_audit_event(event, tmp_path)
        assert result["audit_id"] == "pa-001"
        log_file = tmp_path / ".agentx-init" / "prompts" / "prompt_registry_history.jsonl"
        assert log_file.exists()
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) >= 1

    def test_registry_event_written(self, tmp_path):
        registry = PromptRegistry(registry_id="pr-001")
        result = append_prompt_registry_event(registry, tmp_path)
        assert result["registry_id"] == "pr-001"

    def test_binding_event_written(self, tmp_path):
        binding = PromptRuntimeBinding(
            binding_id="rb-001", prompt_contract_id="pc-001",
            prompt_version_id="pv-001", bound_by_component="Test",
            caller_role="dev", task_type="TASK",
            input_contract_id="ic-001", output_contract_id="oc-001",
            prompt_body_sha256="abc",
        )
        result = append_prompt_binding_event(binding, tmp_path)
        assert result["binding_id"] == "rb-001"

    def test_diff_event_written(self, tmp_path):
        diff = PromptDiffRecord(
            diff_id="pd-001", from_prompt_version_id="pv-001",
            to_prompt_version_id="pv-002", summary="test",
            compatibility_result=COMPATIBILITY_COMPATIBLE,
        )
        result = append_prompt_diff_event(diff, tmp_path)
        assert result["diff_id"] == "pd-001"

    def test_migration_event_written(self, tmp_path):
        migration = PromptMigrationRecord(
            migration_id="pm-001", from_prompt_version_id="pv-001",
            to_prompt_version_id="pv-002",
            affected_runtime_bindings=["rb-001"],
        )
        result = append_prompt_migration_event(migration, tmp_path)
        assert result["migration_id"] == "pm-001"

    def test_safety_event_written(self, tmp_path):
        event = {"event": "safety_check", "result": "pass"}
        result = append_prompt_safety_event(event, tmp_path)
        assert result["event"] == "safety_check"

    def test_latest_prompt_binding_written_atomically(self, tmp_path):
        binding = PromptRuntimeBinding(
            binding_id="rb-002", prompt_contract_id="pc-001",
            prompt_version_id="pv-001", bound_by_component="Test",
            caller_role="dev", task_type="TASK",
            input_contract_id="ic-001", output_contract_id="oc-001",
            prompt_body_sha256="abc",
        )
        result = write_latest_prompt_binding(binding, tmp_path)
        assert result["binding_id"] == "rb-002"
        latest_file = tmp_path / ".agentx-init" / "prompts" / "latest_prompt_binding.json"
        assert latest_file.exists()
        data = json.loads(latest_file.read_text())
        assert data["binding_id"] == "rb-002"

    def test_evidence_manifest_written(self, tmp_path):
        evidence = {"component_id": "TEST", "final_decision": "DONE"}
        result = write_prompt_evidence_manifest(evidence, tmp_path)
        assert result["final_decision"] == "DONE"
        manifest_file = tmp_path / ".agentx-init" / "prompts" / "prompt_contract_versioning_evidence_manifest.json"
        assert manifest_file.exists()

    def test_completion_record_written(self, tmp_path):
        record = {"component_id": "TEST", "final_decision": "DONE"}
        result = write_prompt_completion_record(record, tmp_path)
        assert result["final_decision"] == "DONE"
        comp_file = tmp_path / ".agentx-init" / "prompts" / "prompt_contract_versioning_completion_record.json"
        assert comp_file.exists()
