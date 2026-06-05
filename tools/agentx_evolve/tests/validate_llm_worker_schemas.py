#!/usr/bin/env python3
"""Standalone schema validator for all LLM Worker schemas.

Usage:
    python tools/agentx_evolve/tests/validate_llm_worker_schemas.py

Exits with 0 if all schemas pass, 1 otherwise.
"""
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("Required: pip install jsonschema")
    sys.exit(1)

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

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


def valid_instance(schema_name: str) -> dict:
    base = {
        "schema_version": "1.0",
        "schema_id": schema_name,
        "warnings": [],
        "errors": [],
    }
    if schema_name == "llm_worker_task.schema.json":
        base.update({
            "task_id": "t-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "requested_by": "tester", "caller_role": "dev",
            "worker_mode": "PLAN_ONLY", "implementation_goal": "test",
            "target_component_id": "test", "target_files": [],
            "dry_run": True,
        })
    elif schema_name == "llm_worker_result.schema.json":
        base.update({
            "worker_result_id": "wr-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "status": "SUCCESS", "message": "ok",
            "worker_mode": "PLAN_ONLY",
        })
    elif schema_name == "llm_worker_dependency_status.schema.json":
        base.update({
            "dependency_status_id": "ds-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "model_adapter": "AVAILABLE", "tool_adapter": "AVAILABLE",
            "policy_registry": "AVAILABLE", "failure_taxonomy": "AVAILABLE",
            "governed_patch_execution": "AVAILABLE", "restricted_mode": False,
        })
    elif schema_name == "llm_worker_context_package.schema.json":
        base.update({
            "context_package_id": "cp-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "included_files": [],
            "context_summary": "empty", "context_hash": "abc",
        })
    elif schema_name == "llm_worker_prompt_package.schema.json":
        base.update({
            "prompt_package_id": "pp-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "context_package_id": "cp-001",
            "prompt_hash": "abc",
        })
    elif schema_name == "llm_worker_model_request.schema.json":
        base.update({
            "model_request_id": "mr-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "model_profile_id": "default",
            "prompt_package_id": "pp-001",
            "requested_capability": "impl",
            "max_output_chars": 32000, "deterministic": True,
        })
    elif schema_name == "llm_worker_model_response.schema.json":
        base.update({
            "model_response_id": "mres-001", "created_at": "now",
            "source_component": "ModelAdapter", "task_id": "t-001",
            "model_request_id": "mr-001", "status": "SUCCESS",
            "safe_summary": "ok",
        })
    elif schema_name == "llm_worker_model_output.schema.json":
        base.update({
            "parsed_output_id": "po-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "model_response_id": "mres-001",
            "implementation_summary": "summary",
        })
    elif schema_name == "llm_worker_implementation_plan.schema.json":
        base.update({
            "plan_id": "ip-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "target_component_id": "test",
            "steps": [],
        })
    elif schema_name == "llm_worker_patch_proposal.schema.json":
        base.update({
            "patch_proposal_id": "pp-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "plan_id": "ip-001",
            "patch_format": "structured_file_change_list",
            "target_files": [], "proposed_changes": [],
            "requires_governance": True, "requires_human_approval": False,
            "handoff_status": "PENDING",
        })
    elif schema_name == "llm_worker_validation_handoff.schema.json":
        base.update({
            "validation_handoff_id": "vh-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "plan_id": "ip-001",
            "validation_commands": [], "handoff_target": "ToolAdapter",
            "dry_run": True,
        })
    elif schema_name == "llm_worker_audit.schema.json":
        base.update({
            "audit_id": "aud-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "event_type": "TEST", "status": "OK", "message": "test",
        })
    elif schema_name == "llm_worker_evidence_manifest.schema.json":
        base.update({
            "manifest_id": "em-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "worker_result_id": "wr-001",
            "entries": [{"entry_id": "e1", "sha256": "abc"}],
            "evidence_manifest_sha256": "abc",
        })
    elif schema_name == "llm_worker_review_report.schema.json":
        base.update({
            "review_report_id": "rr-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "worker_result_id": "wr-001",
            "verdict": "DONE", "review_notes": [],
            "review_report_sha256": "abc",
        })
    elif schema_name == "llm_worker_completion_record.schema.json":
        base.update({
            "completion_record_id": "cr-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "worker_result_id": "wr-001",
            "status": "DONE", "completion_record_sha256": "abc",
        })
    elif schema_name == "llm_worker_deviation_register.schema.json":
        base.update({
            "deviation_register_id": "dr-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001", "deviations": [],
        })
    elif schema_name == "llm_worker_traceability_matrix.schema.json":
        base.update({
            "traceability_matrix_id": "tm-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "entries": [{"req": "test", "status": "planned"}],
        })
    elif schema_name == "llm_worker_static_bypass_scan.schema.json":
        base.update({
            "scan_id": "scan-001", "created_at": "now",
            "source_component": "LLMImplementationWorker",
            "task_id": "t-001",
            "scan_results": [{"check": "test", "pass": True}],
            "overall_pass": True,
        })
    base.setdefault("source_component", "LLMImplementationWorker")
    return base


def main() -> int:
    errors = []
    tested = 0
    for sname in LLM_WORKER_SCHEMAS:
        spath = SCHEMA_DIR / sname
        if not spath.exists():
            errors.append(f"MISSING: {sname}")
            continue
        schema = json.loads(spath.read_text())
        instance = valid_instance(sname)
        try:
            jsonschema.validate(instance, schema)
            tested += 1
        except jsonschema.ValidationError as e:
            errors.append(f"VALIDATION FAIL: {sname} — {e.message}")

    total = len(LLM_WORKER_SCHEMAS)
    print(f"Schemas tested: {tested}/{total}")
    if errors:
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All LLM Worker schemas validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
