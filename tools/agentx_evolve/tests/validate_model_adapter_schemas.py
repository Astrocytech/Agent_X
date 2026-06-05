#!/usr/bin/env python3
"""Standalone schema validator for Model Adapter Layer schemas.

Usage:
    PYTHONPATH=tools python tools/agentx_evolve/tests/validate_model_adapter_schemas.py

Returns exit code 0 if all schemas validate, 1 otherwise.
"""
import json
import sys
from pathlib import Path

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"

MODEL_SCHEMAS = {
    "model_request.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_request.schema.json",
        "model_request_id": "req_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ModelAdapter",
        "caller_role": "ORCHESTRATOR",
        "task_type": "SUMMARIZE_CONTEXT",
        "model_id": "small_fast_local",
        "provider_id": "local_provider",
        "prompt": "Summarize the current context",
        "system_prompt": "",
        "json_only": True,
        "context_budget_tokens": 4096,
        "max_output_tokens": 1024,
        "temperature": 0.0,
        "warnings": [],
        "errors": [],
    },
    "model_response.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_response.schema.json",
        "model_response_id": "res_001",
        "model_request_id": "req_001",
        "timestamp": "2026-06-05T00:00:01Z",
        "source_component": "ModelAdapter",
        "model_id": "small_fast_local",
        "provider_id": "local_provider",
        "status": "SUCCESS",
        "message": "completed",
        "raw_output": "Here is the summary.",
        "json_output": None,
        "json_valid": False,
        "schema_valid": False,
        "failure_class": None,
        "warnings": [],
        "errors": [],
    },
    "model_profile.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_profile.schema.json",
        "model_id": "small_fast_local",
        "display_name": "Small Fast Local",
        "provider_id": "local_provider",
        "capability_class": "SMALL_FAST",
        "context_window": 4096,
        "max_output_tokens": 1024,
        "enabled": True,
        "warnings": [],
        "errors": [],
    },
    "model_provider_profile.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_provider_profile.schema.json",
        "provider_id": "local_provider",
        "provider_type": "LOCAL",
        "display_name": "Local Model Runtime",
        "transport_mode": "LOCAL_IN_PROCESS",
        "local_only": True,
        "network_allowed": False,
        "max_retries": 1,
        "enabled": True,
        "warnings": [],
        "errors": [],
    },
    "model_capability_profile.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_capability_profile.schema.json",
        "capability_id": "small_fast",
        "capability_class": "SMALL_FAST",
        "description": "Small fast model for summarization",
        "supported_tasks": ["SUMMARIZE_CONTEXT", "CLASSIFY_FAILURE"],
        "requires_json_output": True,
        "max_context_window": 4096,
        "writes_source": False,
        "runs_tools": False,
        "runs_commands": False,
        "warnings": [],
        "errors": [],
    },
    "model_registry.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_registry.schema.json",
        "registry_id": "reg_001",
        "created_at": "2026-06-05T00:00:00Z",
        "source_component": "ModelRegistry",
        "models": [],
        "provider_profiles": [],
        "capability_profiles": [],
        "warnings": [],
        "errors": [],
    },
    "model_policy_decision.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_policy_decision.schema.json",
        "decision_id": "pol_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ModelPolicy",
        "model_id": "small_fast_local",
        "caller_role": "ORCHESTRATOR",
        "task_type": "SUMMARIZE_CONTEXT",
        "decision": "ALLOW",
        "reason": "All checks passed",
        "warnings": [],
        "errors": [],
    },
    "model_policy.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_policy.schema.json",
        "policy_id": "mp_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ModelPolicy",
        "default_model_mode": "FAKE_ONLY",
        "model_profiles": [],
        "warnings": [],
        "errors": [],
    },
    "model_selection_decision.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_selection_decision.schema.json",
        "decision_id": "sel_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ModelAdapter",
        "task_type": "SUMMARIZE_CONTEXT",
        "selected_model_id": "small_fast_local",
        "selected_provider_id": "local_provider",
        "decision": "ALLOW",
        "reason": "Selected by capability match",
        "warnings": [],
        "errors": [],
    },
    "model_retry_record.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_retry_record.schema.json",
        "retry_id": "ret_001",
        "original_request_id": "req_001",
        "model_request_id": "req_001",
        "model_response_id": "res_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ModelAdapter",
        "attempt_number": 1,
        "retry_reason": "MODEL_INVALID_JSON",
        "decision": "RETRY",
        "warnings": [],
        "errors": [],
    },
    "model_runtime_profile.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_runtime_profile.schema.json",
        "profile_id": "local_default",
        "profile_name": "Local Default Runtime",
        "local_only": True,
        "network_allowed": False,
        "max_loaded_models": 1,
        "default_context_window": 4096,
        "max_total_context_tokens": 8192,
        "endpoint_allowlisted": False,
        "allowed_endpoints": ["127.0.0.1", "localhost"],
        "warnings": [],
        "errors": [],
    },
    "model_call_evidence.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_call_evidence.schema.json",
        "evidence_id": "ev_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ModelAdapter",
        "model_request_id": "req_001",
        "model_response_id": "res_001",
        "model_id": "small_fast_local",
        "provider_id": "local_provider",
        "prompt_hash": "abc123def456",
        "output_hash": "789ghi012jkl",
        "status": "SUCCESS",
        "warnings": [],
        "errors": [],
    },
    "model_adapter_completion_record.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_adapter_completion_record.schema.json",
        "component_id": "ModelAdapter",
        "component_name": "Model Adapter Layer",
        "status": "PASS",
        "validated_commit": "abc123",
        "validated_at": "2026-06-05T00:00:00Z",
        "review_environment": {"os": "linux", "python_version": "3.12", "pytest_version": "9.0"},
        "commands_run": [],
        "files_created_or_changed": [],
        "schemas_created_or_changed": [],
        "tests_created_or_changed": [],
        "validated_capabilities": [],
        "implementation_score": 1.0,
        "final_decision": "APPROVED",
    },
    "model_adapter_evidence_manifest.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_adapter_evidence_manifest.schema.json",
        "component_id": "ModelAdapter",
        "validated_commit": "abc123",
        "validated_at": "2026-06-05T00:00:00Z",
        "review_environment": {"os": "linux", "python_version": "3.12", "pytest_version": "9.0"},
        "commands": [],
        "source_mutation_status": "CLEAN",
        "provider_status": "FAKE_ONLY",
        "local_model_status": "BLOCKED",
        "hosted_model_status": "DISABLED",
        "final_decision": "PASS",
    },
    "model_audit.schema.json": {
        "schema_version": "1.0",
        "schema_id": "model_audit.schema.json",
        "audit_id": "aud_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ModelAdapter",
        "event_type": "MODEL_CALL",
        "model_request_id": "req_001",
        "model_response_id": "res_001",
        "model_id": "small_fast_local",
        "provider_id": "local_provider",
        "status": "SUCCESS",
        "message": "Model call completed",
        "warnings": [],
        "errors": [],
    },
}


def main() -> int:
    errors = []
    tested = 0

    for schema_name, valid_instance in MODEL_SCHEMAS.items():
        schema_path = SCHEMA_DIR / schema_name
        if not schema_path.exists():
            errors.append(f"MISSING: {schema_name}")
            continue

        schema = json.loads(schema_path.read_text())

        try:
            import jsonschema
            jsonschema.validate(valid_instance, schema)
            tested += 1
        except jsonschema.ValidationError as e:
            errors.append(f"VALIDATION FAIL: {schema_name} — {e.message}")
        except ImportError:
            errors.append("jsonschema not installed — skipping schema validation")

    for schema_path in SCHEMA_DIR.glob("*.schema.json"):
        if schema_path.name.startswith("model_") and schema_path.name not in MODEL_SCHEMAS:
            errors.append(f"UNTESTED: {schema_path.name}")

    total = len(MODEL_SCHEMAS)
    print(f"Model schemas tested: {tested}/{total}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All model schemas validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
