import json
import pytest
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

DOCS_SYNC_SCHEMAS = [
"documentation_record.schema.json",
    "documentation_scan.schema.json",
    "documentation_registry.schema.json",
    "documentation_drift_report.schema.json",
    "documentation_change_record.schema.json",
    "documentation_sync_plan.schema.json",
"documentation_sync_operation.schema.json",
    "documentation_sync_result.schema.json",
    "documentation_link_validation.schema.json",
    "documentation_staleness_record.schema.json",
    "documentation_index_record.schema.json",
    "generated_document_section.schema.json",
    "generated_section_registry.schema.json",
    "documentation_manual_protection.schema.json",
    "documentation_sync_policy_decision.schema.json",
    "documentation_sync_deviation.schema.json",
    "documentation_sync_command_result.schema.json",
    "documentation_sync_controller_result.schema.json",
    "documentation_sync_lock.schema.json",
    "documentation_sync_traceability_matrix.schema.json",
    "documentation_evidence_manifest.schema.json",
    "documentation_review_report.schema.json",
    "documentation_completion_record.schema.json",
]


@pytest.fixture
def valid_document_record():
    return {
        "schema_version": "1.0",
        "schema_id": "documentation_record.schema.json",
        "document_id": "test-doc",
        "path": "docs/test.md",
        "title": "Test Doc",
        "document_type": "CONTRACT",
        "authority": "MANUAL_GOVERNED",
        "component_id": "TEST",
        "status": "CURRENT",
        "sha256": "abc",
        "contains_generated_markers": False,
        "protected": True,
        "links_out": [],
        "links_in": [],
        "warnings": [],
        "errors": [],
    }


@pytest.fixture
def valid_scan_report():
    return {
        "schema_version": "1.0",
        "schema_id": "documentation_scan.schema.json",
        "component_id": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
        "scan_id": "scan-1",
        "created_at": "2026-01-01T00:00:00Z",
        "repo_root": "/tmp",
        "scanned_paths": [],
        "documents": [],
        "skipped_paths": [],
        "summary": {},
        "warnings": [],
        "errors": [],
    }


@pytest.fixture
def valid_sync_operation():
    return {
        "schema_version": "1.0",
        "schema_id": "documentation_sync_operation.schema.json",
        "operation_id": "op-1",
        "operation_type": "UPDATE_GENERATED",
        "target_path": "doc.md",
        "target_authority": "GENERATED",
        "requires_policy_approval": False,
        "requires_manual_review": False,
        "allowed_to_apply": True,
        "reason": "test",
        "evidence_refs": [],
        "warnings": [],
        "errors": [],
    }


@pytest.fixture
def valid_drift_record():
    return {
        "schema_version": "1.0",
        "schema_id": "documentation_drift_report.schema.json",
        "drift_id": "drift-1",
        "created_at": "2026-01-01T00:00:00Z",
        "document_id": "doc-1",
        "path": "path/doc",
        "drift_type": "MISSING_SCHEMA",
        "status": "DRIFTED",
        "expected": {},
        "actual": {},
        "severity": "HIGH",
        "recommended_operation": "REVIEW",
        "warnings": [],
        "errors": [],
    }


@pytest.fixture
def valid_command_result():
    return {
        "schema_version": "1.0",
        "schema_id": "documentation_sync_command_result.schema.json",
        "command_id": "cmd-1",
        "name": "test",
        "command": "echo hello",
        "started_at": "start",
        "ended_at": "end",
        "exit_code": 0,
        "status": "PASS",
        "summary": "ok",
        "output_artifact": "out.txt",
        "output_sha256": "abc",
        "warnings": [],
        "errors": [],
    }


@pytest.fixture
def valid_documentation_registry():
    return {
        "schema_version": "1.0",
        "schema_id": "documentation_registry.schema.json",
        "registry_id": "reg-1",
        "created_at": "2026-01-01T00:00:00Z",
        "component_id": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
        "entries": [
            {
                "document_path": "docs/contract.md",
                "document_id": "doc-1",
                "document_type": "CONTRACT",
                "authority": "MANUAL_GOVERNED",
            }
        ],
        "warnings": [],
        "errors": [],
    }


@pytest.fixture
def valid_change_record():
    return {
        "schema_version": "1.0",
        "schema_id": "documentation_change_record.schema.json",
        "change_id": "chg-1",
        "run_id": "run-1",
        "created_at": "2026-01-01T00:00:00Z",
        "source_component": "DocumentationSynchronization",
        "target_document": "docs/generated/index.md",
        "action": "UPDATED",
        "decision_id": "dec-1",
        "before_hash": "abc",
        "after_hash": "def",
        "source_input_hashes": [],
        "changed_sections": [],
        "drift_records_resolved": [],
        "drift_records_remaining": [],
        "evidence_refs": [],
        "warnings": [],
        "errors": [],
    }


@pytest.fixture
def valid_generated_section():
    return {
        "schema_version": "1.0",
        "schema_id": "generated_document_section.schema.json",
        "section_id": "sec-1",
        "target_path": "docs/generated/index.md",
        "start_marker": "<!-- AGENTX-DOCSYNC:BEGIN sec-1 -->",
        "end_marker": "<!-- AGENTX-DOCSYNC:END sec-1 -->",
        "generator_component": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
        "status": "CURRENT",
        "warnings": [],
        "errors": [],
    }


@pytest.fixture
def valid_generated_section_registry(valid_generated_section):
    return {
        "schema_version": "1.0",
        "schema_id": "generated_section_registry.schema.json",
        "registry_id": "reg-sections-1",
        "created_at": "2026-01-01T00:00:00Z",
        "component_id": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
        "sections": [valid_generated_section],
        "duplicate_section_ids": [],
        "warnings": [],
        "errors": [],
    }


@pytest.fixture
def valid_policy_decision():
    return {
        "schema_version": "1.0",
        "schema_id": "documentation_sync_policy_decision.schema.json",
        "decision_id": "pd-1",
        "created_at": "2026-01-01T00:00:00Z",
        "source_component": "DocumentationSynchronization",
        "target_document": "docs/generated/index.md",
        "operation_type": "UPDATE_GENERATED",
        "decision": "ALLOW",
        "reason": "approved generated path",
        "requires_human_approval": False,
        "warnings": [],
        "errors": [],
    }


def _load_schema(name):
    path = SCHEMA_DIR / name
    with open(path) as f:
        return json.load(f)


class TestDocsSyncSchemasAcceptValid:
    def test_document_record_accepts_valid(self, valid_document_record):
        schema = _load_schema("documentation_record.schema.json")
        assert "type" in schema
        assert "properties" in schema
        for req in schema.get("required", []):
            assert req in valid_document_record, f"missing required field: {req}"

    def test_scan_report_accepts_valid(self, valid_scan_report):
        schema = _load_schema("documentation_scan.schema.json")
        for req in schema.get("required", []):
            assert req in valid_scan_report, f"missing required field: {req}"

    def test_drift_record_accepts_valid(self, valid_drift_record):
        schema = _load_schema("documentation_drift_report.schema.json")
        for req in schema.get("required", []):
            assert req in valid_drift_record, f"missing required field: {req}"

    def test_sync_operation_accepts_valid(self, valid_sync_operation):
        schema = _load_schema("documentation_sync_operation.schema.json")
        for req in schema.get("required", []):
            assert req in valid_sync_operation, f"missing required field: {req}"

    def test_command_result_accepts_valid(self, valid_command_result):
        schema = _load_schema("documentation_sync_command_result.schema.json")
        for req in schema.get("required", []):
            assert req in valid_command_result, f"missing required field: {req}"

    def test_documentation_registry_accepts_valid(self, valid_documentation_registry):
        schema = _load_schema("documentation_registry.schema.json")
        for req in schema.get("required", []):
            assert req in valid_documentation_registry, f"missing required field: {req}"

    def test_change_record_accepts_valid(self, valid_change_record):
        schema = _load_schema("documentation_change_record.schema.json")
        for req in schema.get("required", []):
            assert req in valid_change_record, f"missing required field: {req}"

    def test_generated_section_accepts_valid(self, valid_generated_section):
        schema = _load_schema("generated_document_section.schema.json")
        for req in schema.get("required", []):
            assert req in valid_generated_section, f"missing required field: {req}"

    def test_generated_section_registry_accepts_valid(self, valid_generated_section_registry):
        schema = _load_schema("generated_section_registry.schema.json")
        for req in schema.get("required", []):
            assert req in valid_generated_section_registry, f"missing required field: {req}"

    def test_policy_decision_accepts_valid(self, valid_policy_decision):
        schema = _load_schema("documentation_sync_policy_decision.schema.json")
        for req in schema.get("required", []):
            assert req in valid_policy_decision, f"missing required field: {req}"

    def test_all_schemas_exist(self):
        for name in DOCS_SYNC_SCHEMAS:
            path = SCHEMA_DIR / name
            assert path.exists(), f"schema not found: {name}"

    def test_all_schemas_are_valid_json(self):
        for name in DOCS_SYNC_SCHEMAS:
            path = SCHEMA_DIR / name
            with open(path) as f:
                data = json.load(f)
            assert isinstance(data, dict)
            assert "$schema" in data
            assert "type" in data


class TestDocsSyncSchemasRejectInvalid:
    def test_document_record_rejects_missing_required(self):
        schema = _load_schema("documentation_record.schema.json")
        required = set(schema.get("required", []))
        minimal = {
            "schema_version": "1.0",
            "schema_id": "documentation_record.schema.json",
            "document_id": "test",
            "path": "test.md",
            "document_type": "OTHER",
            "authority": "UNKNOWN",
        }
        for req in required:
            assert req in minimal, f"required field {req} not in minimal valid object"

    def test_scan_report_rejects_missing_required(self):
        schema = _load_schema("documentation_scan.schema.json")
        required = set(schema.get("required", []))
        minimal = {
            "schema_version": "1.0",
            "schema_id": "documentation_scan.schema.json",
            "component_id": "TEST",
            "scan_id": "s1",
            "created_at": "now",
            "repo_root": "/tmp",
        }
        for req in required:
            assert req in minimal, f"required field {req} not in minimal valid object"

    def test_command_result_rejects_missing_required(self):
        schema = _load_schema("documentation_sync_command_result.schema.json")
        required = set(schema.get("required", []))
        minimal = {
            "schema_version": "1.0",
            "schema_id": "documentation_sync_command_result.schema.json",
            "command_id": "c1",
            "name": "test",
            "command": "echo",
            "started_at": "s",
            "ended_at": "e",
            "exit_code": 0,
            "status": "PASS",
        }
        for req in required:
            assert req in minimal, f"required field {req} not in minimal valid object"

    def test_documentation_registry_rejects_missing_required(self):
        schema = _load_schema("documentation_registry.schema.json")
        required = set(schema.get("required", []))
        minimal = {
            "schema_version": "1.0",
            "schema_id": "documentation_registry.schema.json",
            "registry_id": "r1",
            "created_at": "now",
            "component_id": "TEST",
            "entries": [],
        }
        for req in required:
            assert req in minimal, f"required field {req} not in minimal valid object"

    def test_change_record_rejects_missing_required(self):
        schema = _load_schema("documentation_change_record.schema.json")
        required = set(schema.get("required", []))
        minimal = {
            "schema_version": "1.0",
            "schema_id": "documentation_change_record.schema.json",
            "change_id": "c1",
            "run_id": "r1",
            "created_at": "now",
            "source_component": "TEST",
            "target_document": "doc.md",
            "action": "UPDATED",
            "decision_id": "d1",
        }
        for req in required:
            assert req in minimal, f"required field {req} not in minimal valid object"

    def test_generated_section_rejects_missing_required(self):
        schema = _load_schema("generated_document_section.schema.json")
        required = set(schema.get("required", []))
        minimal = {
            "schema_version": "1.0",
            "schema_id": "generated_document_section.schema.json",
            "section_id": "s1",
            "target_path": "doc.md",
            "start_marker": "<begin>",
            "end_marker": "<end>",
            "generator_component": "TEST",
            "status": "CURRENT",
        }
        for req in required:
            assert req in minimal, f"required field {req} not in minimal valid object"

    def test_generated_section_registry_rejects_missing_required(self):
        schema = _load_schema("generated_section_registry.schema.json")
        required = set(schema.get("required", []))
        minimal = {
            "schema_version": "1.0",
            "schema_id": "generated_section_registry.schema.json",
            "registry_id": "r1",
            "created_at": "now",
            "component_id": "TEST",
            "sections": [],
        }
        for req in required:
            assert req in minimal, f"required field {req} not in minimal valid object"

    def test_policy_decision_rejects_missing_required(self):
        schema = _load_schema("documentation_sync_policy_decision.schema.json")
        required = set(schema.get("required", []))
        minimal = {
            "schema_version": "1.0",
            "schema_id": "documentation_sync_policy_decision.schema.json",
            "decision_id": "d1",
            "created_at": "now",
            "source_component": "TEST",
            "target_document": "doc.md",
            "operation_type": "UPDATE_GENERATED",
            "decision": "ALLOW",
            "requires_human_approval": False,
        }
        for req in required:
            assert req in minimal, f"required field {req} not in minimal valid object"
