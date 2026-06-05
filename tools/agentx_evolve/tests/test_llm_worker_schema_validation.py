import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "llm_worker")

LLM_WORKER_SCHEMAS = [
    "llm_worker_task.schema.json",
    "llm_worker_result.schema.json",
    "llm_worker_dependency_status.schema.json",
    "llm_worker_context_package.schema.json",
    "llm_worker_prompt_package.schema.json",
    "llm_worker_model_request.schema.json",
    "llm_worker_model_response.schema.json",
    "llm_worker_model_output.schema.json",
    "llm_worker_implementation_plan.schema.json",
    "llm_worker_patch_proposal.schema.json",
    "llm_worker_validation_handoff.schema.json",
    "llm_worker_audit.schema.json",
    "llm_worker_evidence_manifest.schema.json",
    "llm_worker_review_report.schema.json",
    "llm_worker_completion_record.schema.json",
    "llm_worker_deviation_register.schema.json",
    "llm_worker_traceability_matrix.schema.json",
    "llm_worker_static_bypass_scan.schema.json",
]


def _get_valid_fixtures():
    if not os.path.isdir(FIXTURES_DIR):
        return []
    return sorted([
        f for f in os.listdir(FIXTURES_DIR)
        if f.endswith(".json") and f.startswith("valid_")
    ])


def _get_invalid_fixtures():
    if not os.path.isdir(FIXTURES_DIR):
        return []
    return sorted([
        f for f in os.listdir(FIXTURES_DIR)
        if f.endswith(".json")
        and (f.startswith("missing_") or f.startswith("invalid_"))
    ])


class TestAllWorkerSchemas:
    def test_all_schemas_exist(self):
        for sname in LLM_WORKER_SCHEMAS:
            path = os.path.join(SCHEMA_DIR, sname)
            assert os.path.exists(path), f"Missing schema: {sname}"

    @pytest.mark.parametrize("fname", _get_valid_fixtures())
    def test_valid_fixture_passes(self, fname):
        import jsonschema
        fpath = os.path.join(FIXTURES_DIR, fname)
        with open(fpath) as f:
            data = json.load(f)
        schema_id = data.get("schema_id", "")
        spath = os.path.join(SCHEMA_DIR, schema_id)
        with open(spath) as f:
            schema = json.load(f)
        jsonschema.validate(data, schema)

    @pytest.mark.parametrize("fname", _get_invalid_fixtures())
    def test_invalid_fixture_fails(self, fname):
        import jsonschema
        fpath = os.path.join(FIXTURES_DIR, fname)
        with open(fpath) as f:
            data = json.load(f)
        schema_id = data.get("schema_id", "")
        spath = os.path.join(SCHEMA_DIR, schema_id)
        with open(spath) as f:
            schema = json.load(f)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)

    def test_each_schema_accepts_valid_instance(self):
        import jsonschema
        for sname in LLM_WORKER_SCHEMAS:
            spath = os.path.join(SCHEMA_DIR, sname)
            with open(spath) as f:
                schema = json.load(f)
            valid_instance = _make_valid_instance(sname)
            jsonschema.validate(valid_instance, schema)

    def test_each_schema_rejects_missing_required(self):
        import jsonschema
        for sname in LLM_WORKER_SCHEMAS:
            spath = os.path.join(SCHEMA_DIR, sname)
            with open(spath) as f:
                schema = json.load(f)
            with pytest.raises(jsonschema.ValidationError):
                jsonschema.validate({}, schema)


def _make_valid_instance(schema_id: str) -> dict:
    base = {
        "schema_version": "1.0",
        "schema_id": schema_id,
        "warnings": [],
        "errors": [],
    }
    if schema_id == "llm_worker_task.schema.json":
        base.update({
            "task_id": "t-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "requested_by": "tester",
            "caller_role": "dev",
            "worker_mode": "PLAN_ONLY",
            "implementation_goal": "test",
            "target_component_id": "test",
            "target_files": [],
            "dry_run": True,
        })
    elif schema_id == "llm_worker_result.schema.json":
        base.update({
            "worker_result_id": "wr-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "status": "SUCCESS",
            "message": "ok",
            "worker_mode": "PLAN_ONLY",
        })
    elif schema_id == "llm_worker_dependency_status.schema.json":
        base.update({
            "dependency_status_id": "ds-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "model_adapter": "AVAILABLE",
            "tool_adapter": "AVAILABLE",
            "policy_registry": "AVAILABLE",
            "failure_taxonomy": "AVAILABLE",
            "governed_patch_execution": "AVAILABLE",
            "restricted_mode": False,
        })
    elif schema_id == "llm_worker_context_package.schema.json":
        base.update({
            "context_package_id": "cp-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "included_files": [],
            "context_summary": "summary",
            "context_hash": "abc",
        })
    elif schema_id == "llm_worker_prompt_package.schema.json":
        base.update({
            "prompt_package_id": "pp-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "context_package_id": "cp-001",
            "prompt_hash": "abc",
        })
    elif schema_id == "llm_worker_model_request.schema.json":
        base.update({
            "model_request_id": "mr-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "model_profile_id": "default",
            "prompt_package_id": "pp-001",
            "requested_capability": "impl",
            "max_output_chars": 32000,
            "deterministic": True,
        })
    elif schema_id == "llm_worker_model_response.schema.json":
        base.update({
            "model_response_id": "mres-test",
            "created_at": "now",
            "source_component": "ModelAdapter",
            "task_id": "t-001",
            "model_request_id": "mr-001",
            "status": "SUCCESS",
            "safe_summary": "ok",
        })
    elif schema_id == "llm_worker_model_output.schema.json":
        base.update({
            "parsed_output_id": "po-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "model_response_id": "mres-001",
            "implementation_summary": "summary",
        })
    elif schema_id == "llm_worker_implementation_plan.schema.json":
        base.update({
            "plan_id": "ip-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "target_component_id": "test",
            "steps": [],
        })
    elif schema_id == "llm_worker_patch_proposal.schema.json":
        base.update({
            "patch_proposal_id": "pp-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "plan_id": "ip-001",
            "patch_format": "structured_file_change_list",
            "target_files": [],
            "proposed_changes": [],
            "requires_governance": True,
            "requires_human_approval": False,
            "handoff_status": "PENDING",
        })
    elif schema_id == "llm_worker_validation_handoff.schema.json":
        base.update({
            "validation_handoff_id": "vh-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "plan_id": "ip-001",
            "validation_commands": [],
            "handoff_target": "ToolAdapter",
            "dry_run": True,
        })
    elif schema_id == "llm_worker_audit.schema.json":
        base.update({
            "audit_id": "aud-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "event_type": "TEST",
            "status": "SUCCESS",
            "message": "test",
        })
    elif schema_id == "llm_worker_evidence_manifest.schema.json":
        base.update({
            "manifest_id": "em-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "worker_result_id": "wr-001",
            "entries": [{"entry_id": "e1", "sha256": "abc"}],
            "evidence_manifest_sha256": "abc",
        })
    elif schema_id == "llm_worker_review_report.schema.json":
        base.update({
            "review_report_id": "rr-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "worker_result_id": "wr-001",
            "verdict": "DONE",
            "review_notes": [],
            "review_report_sha256": "abc",
        })
    elif schema_id == "llm_worker_completion_record.schema.json":
        base.update({
            "completion_record_id": "cr-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "worker_result_id": "wr-001",
            "status": "DONE",
            "completion_record_sha256": "abc",
        })
    elif schema_id == "llm_worker_deviation_register.schema.json":
        base.update({
            "deviation_register_id": "dr-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "deviations": [],
        })
    elif schema_id == "llm_worker_traceability_matrix.schema.json":
        base.update({
            "traceability_matrix_id": "tm-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "entries": [{"req": "test", "status": "planned"}],
        })
    elif schema_id == "llm_worker_static_bypass_scan.schema.json":
        base.update({
            "scan_id": "scan-test",
            "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "scan_results": [{"check": "test", "pass": True}],
            "overall_pass": True,
        })
    else:
        base["source_component"] = "LLMImplementationWorker"
    return base
